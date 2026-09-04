"""The staged allocation rule, inherited from Pilot-1 as C_staged_safety_1.00.

    stage 1                allocate B1 (the stratum's frozen stage-1 count)
    loop
        observe route-local precision ONLY
        if achieved <= target            -> ATTAINED
        next = ceil(B * (achieved/target) ** (1/kappa))
        if next > cap_blocks             -> PRECISION_LIMITED
        else execute exactly the next stage and repeat

There is no "at most one top-up".  The cap is the only terminator, so the
terminal state space is exactly {ATTAINED, PRECISION_LIMITED} -- a property of
the control flow, not an empirical finding.

Brief section 14: the allocation may read only route-local precision.  The
enforcement here is structural.  ``step`` receives a ``Precision`` -- two
floats and nothing else -- and the whole trajectory is computed from a
``measure`` callable returning a float.  There is no parameter, attribute or
closure through which a discrepancy, a z, a sign, a Route-Q value, a Gaussian
consistency result or a historical pass/fail could enter.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

ATTAINED = "ATTAINED"
PRECISION_LIMITED = "PRECISION_LIMITED"

#: Every field the allocation is allowed to see.  Frozen, and pinned by a test.
PRECISION_FIELDS = ("blocks", "relative_se")

#: Fields that must never be reachable from an allocation decision.
FORBIDDEN_FIELDS = (
    "discrepancy", "relative_discrepancy", "z", "sign", "gate", "gate_result",
    "passed", "pass_fail", "criterion_satisfied", "route_other", "route_q",
    "gaussian_consistency", "family_result", "history", "historically_failed",
    "verdict", "correspondence",
)


@dataclass(frozen=True, slots=True)
class Precision:
    """Route-local precision.  The ONLY channel into an allocation decision."""

    blocks: int
    relative_se: float


@dataclass(frozen=True, slots=True)
class Stage:
    index: int
    blocks: int
    relative_se: float
    next_blocks: int | None       # what the rule would require next, if not done


@dataclass(frozen=True, slots=True)
class Trajectory:
    """The complete cap-independent record of one allocation.

    The stage SEQUENCE does not depend on the cap -- the cap only decides where
    the sequence is cut off.  Recording the trajectory once therefore yields
    the exact outcome under EVERY cap in the frozen grid, with no extra
    simulation and no approximation.  ``terminate`` performs that cut.
    """

    stages: tuple[Stage, ...]
    target: float
    kappa: float
    reached_target: bool
    pool_exhausted: bool = False
    #: What stage 1 required, computed from the reference BEFORE any stage-1
    #: block exists.  When it already exceeds the frozen cap the route is
    #: PRECISION_LIMITED from projected cost alone and nothing executes --
    #: the inherited P4X semantics verbatim.
    planned_b1: int = 0


@dataclass(frozen=True, slots=True)
class Outcome:
    status: str
    blocks: int
    stages: int
    relative_se: float
    target: float
    kappa: float
    cap_blocks: int
    next_stage_blocks: int | None
    stage_blocks: tuple[int, ...]


def next_allocation(current: Precision, target: float, kappa: float) -> int:
    """The frozen sizing law, inverted.  Pure in (blocks, relative_se)."""
    if current.relative_se <= 0 or not math.isfinite(current.relative_se):
        return current.blocks + 1
    ratio = current.relative_se / target
    if ratio <= 1.0:
        return current.blocks
    return max(current.blocks + 1,
               math.ceil(current.blocks * ratio ** (1.0 / kappa)))


def trace(*, measure, b1: int, target: float, kappa: float,
          pool_limit: int) -> Trajectory:
    """Run the rule out to the pool limit, recording every stage.

    ``measure(blocks) -> float`` is the only input.  It returns the route's own
    achieved relative standard error and nothing else.
    """
    stages: list[Stage] = []
    blocks = b1
    if b1 > pool_limit:
        # Cannot even plan stage 1 inside the pool.  Since the largest frozen
        # cap is pool_limit - B_ref, every cap in the grid refuses this route
        # before it starts, so no block is drawn and none needs to be.
        return Trajectory((), target, kappa, False, False, b1)
    while True:
        if blocks > pool_limit:
            return Trajectory(tuple(stages), target, kappa, False, True, b1)
        achieved = measure(blocks)
        here = Precision(blocks, achieved)
        if achieved <= target:
            stages.append(Stage(len(stages) + 1, blocks, achieved, None))
            return Trajectory(tuple(stages), target, kappa, True, False, b1)
        nxt = next_allocation(here, target, kappa)
        stages.append(Stage(len(stages) + 1, blocks, achieved, nxt))
        blocks = nxt


def terminate(traj: Trajectory, cap_blocks: int) -> Outcome:
    """Cut a recorded trajectory at a cap.  Exact, not an approximation."""
    if not traj.stages:
        # Refused before stage 1, from projected cost alone.
        return Outcome(PRECISION_LIMITED, 0, 0, math.inf, traj.target,
                       traj.kappa, cap_blocks, traj.planned_b1, ())
    if traj.stages[0].blocks > cap_blocks:
        return Outcome(PRECISION_LIMITED, 0, 0, math.inf, traj.target,
                       traj.kappa, cap_blocks, traj.stages[0].blocks, ())
    executed: list[int] = []
    for stage in traj.stages:
        if stage.blocks > cap_blocks:
            break                                  # never executed under this cap
        executed.append(stage.blocks)
        if stage.next_blocks is None:
            return Outcome(ATTAINED, stage.blocks, len(executed),
                           stage.relative_se, traj.target, traj.kappa,
                           cap_blocks, None, tuple(executed))
        if stage.next_blocks > cap_blocks:
            return Outcome(PRECISION_LIMITED, stage.blocks, len(executed),
                           stage.relative_se, traj.target, traj.kappa,
                           cap_blocks, stage.next_blocks, tuple(executed))
    # The trajectory ran out of recorded stages inside the cap.  Only reachable
    # when the pool limit cut the trace short, which is a STOP condition, never
    # a terminal state of the rule.
    last = traj.stages[-1] if traj.stages else None
    return Outcome("POOL_EXHAUSTED",
                   last.blocks if last else 0, len(executed),
                   last.relative_se if last else math.inf,
                   traj.target, traj.kappa, cap_blocks,
                   last.next_blocks if last else None, tuple(executed))


@dataclass
class Ledger:
    stop_events: list[str] = field(default_factory=list)

    def record(self, event: str) -> None:
        self.stop_events.append(event)
