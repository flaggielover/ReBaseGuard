"""Independent auditor for the frozen Pilot-2 endpoint (brief section 7).

The endpoint is NOT "the rule said it was done".  It is a property of the
realised run, re-derived here from the recorded trajectory and the frozen cap,
without asking the rule what it thinks.  That is what makes it able to fail:
an implementation that executed past the cap, mislabelled a terminal state, or
stopped without the cap actually refusing the next stage, is caught.

    valid governance disposition
        = ATTAINED              with achieved <= target and blocks <= cap
        or PRECISION_LIMITED    with achieved > target
                                and next_stage_blocks > cap
                                and blocks <= cap
        and, in both branches, no scientific-outcome field reachable from the
        stopping decision.

A validly PRECISION_LIMITED route is a valid GOVERNANCE DISPOSITION.  It is
NOT a scientific success, and this module never calls it one -- the two are
reported separately throughout.
"""

from __future__ import annotations

from dataclasses import dataclass

from .rule import ATTAINED, FORBIDDEN_FIELDS, PRECISION_LIMITED, Outcome, Trajectory


@dataclass(frozen=True, slots=True)
class Audit:
    valid: bool
    status: str
    reasons: tuple[str, ...]

    @property
    def attained(self) -> bool:
        return self.valid and self.status == ATTAINED

    @property
    def precision_limited(self) -> bool:
        return self.valid and self.status == PRECISION_LIMITED


def audit(outcome: Outcome, traj: Trajectory, *, cap_blocks: int,
          measure_inputs_seen: tuple[str, ...] = ()) -> Audit:
    """Re-derive validity from the record.  Never trusts the rule's own label."""
    bad: list[str] = []

    if outcome.status not in (ATTAINED, PRECISION_LIMITED):
        bad.append(f"terminal state {outcome.status!r} is not one of the two "
                   "permitted dispositions")

    if outcome.blocks > cap_blocks:
        bad.append(f"executed {outcome.blocks} blocks beyond the cap {cap_blocks}")

    if outcome.stage_blocks and max(outcome.stage_blocks) > cap_blocks:
        bad.append("a recorded stage exceeded the cap")

    if outcome.status == ATTAINED:
        if not outcome.relative_se <= outcome.target:
            bad.append(f"labelled ATTAINED with relSE {outcome.relative_se!r} "
                       f"> target {outcome.target!r}")
    elif outcome.status == PRECISION_LIMITED:
        if not outcome.relative_se > outcome.target:
            bad.append("labelled PRECISION_LIMITED while already at target")
        if outcome.next_stage_blocks is None:
            bad.append("PRECISION_LIMITED without a refused next stage")
        elif not outcome.next_stage_blocks > cap_blocks:
            bad.append(f"PRECISION_LIMITED but the next stage "
                       f"{outcome.next_stage_blocks} does not exceed the cap "
                       f"{cap_blocks}")

    if outcome.target != traj.target or outcome.kappa != traj.kappa:
        bad.append("outcome does not belong to the trajectory it is audited against")

    leaked = [f for f in measure_inputs_seen if f in FORBIDDEN_FIELDS]
    if leaked:
        bad.append(f"scientific outcome fields reached the allocation: {leaked}")

    return Audit(not bad, outcome.status, tuple(bad))


def summarise(audits: list[Audit]) -> dict:
    n = len(audits)
    valid = sum(a.valid for a in audits)
    att = sum(a.attained for a in audits)
    lim = sum(a.precision_limited for a in audits)
    return {
        "replicates": n,
        "valid_dispositions": valid,
        "attained": att,
        "precision_limited": lim,
        "invalid": n - valid,
        "valid_disposition_rate": valid / n if n else float("nan"),
        "attainment_rate": att / n if n else float("nan"),
        "precision_limited_rate": lim / n if n else float("nan"),
        "invalid_reasons": sorted({r for a in audits for r in a.reasons})[:8],
    }
