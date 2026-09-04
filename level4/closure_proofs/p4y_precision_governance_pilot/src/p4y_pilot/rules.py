"""Candidate precision-allocation rules.

Every rule is a pure function of ROUTE-LOCAL PRECISION and frozen constants.
None of them may read -- and none of them is given -- the discrepancy between
the routes, its sign, the |z| statistic, the pass/fail outcome, the family
correspondence result, or whether a cell was historically difficult.  The
signature of ``run`` is the enforcement: those quantities are not arguments.

Terminal states
---------------
``ATTAINED``          the pooled realised relative SE is <= r*.
``PRECISION_LIMITED`` the NEXT stage the rule requires would cross the frozen
                      cap, so the rule is not allowed to buy it.
``UNRESOLVED``        neither -- the rule ran out of permitted stages while
                      still inside the cap.  This is the P4X G1 defect.  It is
                      representable here ONLY so that the baseline rules can
                      be shown to produce it; RULE C and RULE D cannot.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .stats import chi2_upper_quantile_ratio

ATTAINED = "ATTAINED"
PRECISION_LIMITED = "PRECISION_LIMITED"
UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class Outcome:
    status: str
    blocks: int
    stages: int
    relative_se: float
    r_star: float
    stage_blocks: tuple[int, ...] = ()
    stage_relative_se: tuple[float, ...] = ()
    next_stage_blocks: int | None = None       # what the cap refused, if any

    @property
    def attained(self) -> bool:
        return self.status == ATTAINED


@dataclass(frozen=True, slots=True)
class Rule:
    """A predeclared allocation rule.

    ``safety`` is the multiplicative factor applied to the TARGET, so a rule
    with ``safety = 1.3`` sizes every stage to reach ``r* / 1.3``.  ``adaptive``
    replaces the constant by ``sqrt(q_delta(B))``, the block-count-dependent
    chi-square inflation, which tends to 1 as B grows.
    """

    name: str
    max_stages: int                # counting stage 1; math.inf means cap-only
    safety: float = 1.0
    adaptive: bool = False
    delta: float = 0.95

    def target(self, blocks: int) -> float:
        """The relative SE a stage of size ``blocks`` is sized to reach."""
        if self.adaptive:
            return 1.0 / math.sqrt(chi2_upper_quantile_ratio(blocks, self.delta))
        return 1.0 / self.safety


def _size(blocks: int, achieved: float, r_star: float, kappa: float,
          factor: float) -> int:
    """Frozen scaling law, inverted.  ``relSE ~ N^-kappa`` and ``N ~ blocks``.

        blocks_next = blocks * (achieved / (r* * factor)) ** (1 / kappa)

    ``factor <= 1`` shrinks the target and so enlarges the allocation.
    """
    if achieved <= 0 or not math.isfinite(achieved):
        return blocks + 1
    ratio = achieved / (r_star * factor)
    if ratio <= 1.0:
        return blocks
    return max(blocks + 1, math.ceil(blocks * ratio ** (1.0 / kappa)))


def _size_adaptive(blocks: int, achieved: float, r_star: float, kappa: float,
                   rule: Rule) -> int:
    """Fixed point of ``B' = size(B, achieved, r*, kappa, target(B'))``.

    ``target`` rises towards 1 as ``B'`` grows, so the map is decreasing and
    the iteration settles in a handful of steps; it is capped at 40 and the
    last iterate is returned, which is always a legal (if slightly
    conservative) allocation.
    """
    nxt = _size(blocks, achieved, r_star, kappa, rule.target(max(blocks, 3)))
    for _ in range(40):
        prev = nxt
        nxt = _size(blocks, achieved, r_star, kappa, rule.target(prev))
        if nxt == prev:
            break
    return nxt


def initial_blocks(rule: Rule, reference_blocks: int, reference_relative_se: float,
                   r_star: float, kappa: float, min_blocks: int) -> int:
    """Stage 1, sized from the historical-style reference measurement.

    Identical in shape to the frozen P4X stage-1 rule
    ``N_required = N_ref * (relSE_ref / r*) ** (1 / kappa)``; the rules differ
    only in the target they aim at.
    """
    factor = (rule.target(reference_blocks) if rule.adaptive
              else 1.0 / rule.safety)
    return max(min_blocks,
               _size(reference_blocks, reference_relative_se, r_star, kappa,
                     factor))


@dataclass
class Ledger:
    """What a rule actually spent, for the CPU-multiplier comparison."""

    blocks: int = 0
    stages: int = 0
    stage_blocks: list[int] = field(default_factory=list)
    stage_relative_se: list[float] = field(default_factory=list)


def run(
    rule: Rule,
    *,
    measure,                      # (blocks) -> realised worst-m relative SE
    reference_blocks: int,
    reference_relative_se: float,
    r_star: float,
    kappa: float,
    cap_blocks: int,
    min_blocks: int,
) -> Outcome:
    """Execute one allocation under ``rule`` and return its terminal state.

    ``measure`` is the ONLY channel through which the rule learns anything,
    and it returns route-local precision and nothing else.
    """
    blocks = initial_blocks(rule, reference_blocks, reference_relative_se,
                            r_star, kappa, min_blocks)
    led = Ledger()

    while True:
        if blocks > cap_blocks:
            # Cannot even start this stage: the cap refuses it.
            return Outcome(PRECISION_LIMITED, led.blocks, led.stages,
                           led.stage_relative_se[-1] if led.stage_relative_se
                           else math.inf,
                           r_star, tuple(led.stage_blocks),
                           tuple(led.stage_relative_se), blocks)
        achieved = measure(blocks)
        led.blocks = blocks
        led.stages += 1
        led.stage_blocks.append(blocks)
        led.stage_relative_se.append(achieved)

        if achieved <= r_star:
            return Outcome(ATTAINED, blocks, led.stages, achieved, r_star,
                           tuple(led.stage_blocks),
                           tuple(led.stage_relative_se))

        if rule.adaptive:
            nxt = _size_adaptive(blocks, achieved, r_star, kappa, rule)
        else:
            nxt = _size(blocks, achieved, r_star, kappa, 1.0 / rule.safety)

        if nxt > cap_blocks:
            # THE definition of PRECISION_LIMITED: the next stage the frozen
            # rule requires would cross the frozen cap.  Nothing else.
            return Outcome(PRECISION_LIMITED, blocks, led.stages, achieved,
                           r_star, tuple(led.stage_blocks),
                           tuple(led.stage_relative_se), nxt)

        if led.stages >= rule.max_stages:
            # Only reachable for the bounded-stage baselines.  A rule that can
            # end here is exactly the P4X defect.
            return Outcome(UNRESOLVED, blocks, led.stages, achieved, r_star,
                           tuple(led.stage_blocks),
                           tuple(led.stage_relative_se), nxt)
        blocks = nxt


def can_end_unresolved(rule: Rule) -> bool:
    """True iff the rule admits the third state.  A frozen rule must not."""
    return math.isfinite(rule.max_stages)


# --------------------------------------------------------------- the slate
#: The predeclared candidate slate.  Fixed before any design or validation
#: replicate is drawn, and not added to afterwards.
CANDIDATES: tuple[Rule, ...] = (
    # RULE A -- the P4X rule verbatim: one-shot sizing, at most one top-up.
    Rule("A_oneshot_one_topup", max_stages=2, safety=1.0),
    # RULE B -- the same shape with a predeclared constant safety factor.
    Rule("B_oneshot_safety_1.15", max_stages=2, safety=1.15),
    Rule("B_oneshot_safety_1.30", max_stages=2, safety=1.30),
    Rule("B_oneshot_safety_1.50", max_stages=2, safety=1.50),
    # RULE C -- staged, terminated ONLY by the cap.
    Rule("C_staged_safety_1.00", max_stages=math.inf, safety=1.00),
    Rule("C_staged_safety_1.15", max_stages=math.inf, safety=1.15),
    Rule("C_staged_safety_1.30", max_stages=math.inf, safety=1.30),
    # RULE D -- staged with the block-count-adaptive chi-square inflation.
    Rule("D_staged_quantile_0.95", max_stages=math.inf, adaptive=True,
         delta=0.95),
    Rule("D_staged_quantile_0.99", max_stages=math.inf, adaptive=True,
         delta=0.99),
)
