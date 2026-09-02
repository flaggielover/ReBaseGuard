"""Frozen SR threshold calibration with a genuinely held-out acceptance sample.

This module is the *behavioural* half of the P8 repair.  It replaces P8's
``calibrate.py`` + ``polish_sr_calibration.py`` pair, whose defect the
authoritative adjudication recorded as part of ``G14 = FAIL``:

    P8 ran a 163,840-cycle search, verified at
    ``("p8_sr_calibration_verify", batch=7)``, **saw that the verification
    missed**, added a 614,400-cycle refinement phase, and then re-verified at
    that same address.  The acceptance sample was therefore inspected before the
    threshold was final, and the protocol text still declared budgets
    (250,000 / 2,048,000) that were never executed.

P8R's repair has three parts.

1.  **One authoritative budget.**  Every count is read from
    ``config``, which is digested at the temporal anchor.  There is no second
    place where a budget is written, so a declared/executed disagreement of the
    P8 kind cannot arise; ``scripts/audit_integrity.py`` gate ``I13`` re-derives the
    executed counts from the stored trace and compares them to ``config``.

2.  **A fixed-length, non-adaptive search.**  Stage S1 runs exactly
    ``CAL_S1_ITERATIONS`` evaluations and stage S2 exactly
    ``CAL_S2_ITERATIONS``.  Neither stage stops early, neither stage selects a
    "best" iterate, and the returned threshold is simply the iterate the last S2
    update produces.  Nothing about the search depends on a quantity the search
    is not allowed to see, and nothing about it depends on an outcome.

3.  **Holdout separation enforced by the address class.**  Every search
    evaluation is minted in ``CAL_SEARCH``; the acceptance sample is
    ``CAL_VERIFY_1``; the one pre-frozen retry's acceptance sample is
    ``CAL_VERIFY_2``.  :func:`~.addressing.require_class` refuses any other
    combination at the call site, so a search cannot read a verification
    address even by mistake.

The frozen retry rule
---------------------
If the ``CAL_VERIFY_1`` acceptance fails for a family, exactly one retry is
permitted (``CALIBRATION_PLAN.md`` §5): rerun stage S2 from the failed threshold
on the pre-reserved ``CAL_RETRY_BATCH0`` region of ``CAL_SEARCH``, then accept or
reject once on ``CAL_VERIFY_2``.  ``CAL_VERIFY_1`` is never revisited.  If
``CAL_VERIFY_2`` also fails, the family's SR threshold is
``CALIBRATION_FAILED``: it is reported as a negative procedural outcome and its
SR cells are excluded from the gates that presuppose a calibrated threshold.
There is no third attempt.
"""
from __future__ import annotations

import numpy as np

from .addressing import (CAL_SEARCH_ARL0, CAL_VERIFY_1_ARL0, CAL_VERIFY_2_ARL0,
                         AddressClass, require_class)
from .config import (CAL_BETA_MAX, CAL_BETA_MIN, CAL_CLIP_FACTOR,
                     CAL_DAMP_EXPONENT, CAL_DAMP_SWITCH,
                     CAL_RETRY_BATCH0, CAL_S1_BATCH0, CAL_S1_ITERATIONS,
                     CAL_S1_ROW_BLOCKS, CAL_S2_BATCH0, CAL_S2_ITERATIONS,
                     CAL_S2_ROW_BLOCKS, CAL_TOLERANCE, CAL_VERIFY_1_BATCH,
                     CAL_VERIFY_2_BATCH, CAL_VERIFY_ROW_BLOCKS, ROWS_PER_BLOCK)
from .detectors import make_step
from .primitives import BLOCK_LEN, stopped_block

_SEARCH_ONLY = frozenset({AddressClass.CAL_SEARCH})
_VERIFY_ONLY = frozenset({AddressClass.CAL_VERIFY_1, AddressClass.CAL_VERIFY_2,
                          AddressClass.PRODUCTION})


def arl0(*, experiment: str, family: str, detector: str, threshold: float,
         batch: int, n_row_blocks: int, e: float = 0.0,
         max_steps: int = 4_000_000) -> tuple[float, float, int]:
    """``(mean tau, standard error, n)`` for independent reset cycles.

    The standard error is the **batch-means** SE over the ``n_row_blocks``
    addressable row blocks, which are independent by construction.
    """
    step, _ = make_step(detector, threshold)
    means, taus_all = [], []
    for rb in range(int(n_row_blocks)):
        n = ROWS_PER_BLOCK
        plus = np.zeros(n)
        minus = np.zeros(n)
        active = np.ones(n, bool)
        tau = np.zeros(n, np.int64)
        for t in range(1, max_steps + 1):
            idx = np.flatnonzero(active)
            if idx.size == 0:
                break
            b, off = divmod(t - 1, BLOCK_LEN)
            z = stopped_block(experiment, family, batch, rb, b,
                              n_rows=n)[idx, off] - float(e)
            np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
            plus[idx] = np_
            minus[idx] = nm_
            crossed = cu | cd
            if crossed.any():
                done = idx[crossed]
                tau[done] = t
                active[done] = False
        else:
            raise RuntimeError("paths did not alarm")
        taus_all.append(tau)
        means.append(float(tau.mean()))
    tau = np.concatenate(taus_all)
    se = float(np.std(means, ddof=1) / np.sqrt(len(means))) if len(means) > 1 \
        else float(tau.std(ddof=1) / np.sqrt(tau.size))
    return float(tau.mean()), se, int(tau.size)


def _update(thr: float, arl: float, target: float, prev=None) -> float:
    """The frozen log-log secant update, clipped.

    ``ARL_0`` of the symmetric two-chart SR is **not** linear in the natural
    threshold ``A`` over the range these families need: measured locally it
    behaves like ``ARL ~ A^beta`` with ``beta`` around 0.47 for the
    contaminated families.  A plain proportional step therefore undershoots
    badly and six iterations would not reach the operating point.  The frozen
    rule estimates ``beta`` from the two most recent evaluations of this
    calibration and inverts it:

        beta      = log(ARL_i / ARL_{i-1}) / log(A_i / A_{i-1})
        A_{i+1}   = A_i * (target / ARL_i) ** (p / beta)

    ``beta`` is clipped to ``[CAL_BETA_MIN, CAL_BETA_MAX]`` so that a
    noise-driven slope estimate cannot produce an enormous step, and the whole
    multiplier is clipped to ``[1/CAL_CLIP_FACTOR, CAL_CLIP_FACTOR]``.  With no
    previous evaluation (the first iteration) ``beta = 1``, i.e. the plain
    proportional step.

    ``p`` is 1 unless the residual has already fallen to the evaluation's own
    noise floor (``CAL_DAMP_SWITCH``), where a full step would chase noise.
    """
    rel = abs(arl - target) / target
    p = 1.0 if rel > CAL_DAMP_SWITCH else CAL_DAMP_EXPONENT
    beta = 1.0
    if prev is not None:
        a0, r0 = prev
        if a0 > 0 and arl > 0 and r0 > 0 and abs(np.log(thr / a0)) > 1e-12:
            b = float(np.log(arl / r0) / np.log(thr / a0))
            if np.isfinite(b):
                beta = float(np.clip(b, CAL_BETA_MIN, CAL_BETA_MAX))
    factor = (target / arl) ** (p / beta)
    return float(np.clip(thr * factor, thr / CAL_CLIP_FACTOR,
                         thr * CAL_CLIP_FACTOR))


def _search_stage(*, family: str, target: float, thr: float, stage: str,
                  n_iter: int, n_row_blocks: int, batch0: int, prev=None
                  ) -> tuple:
    """Run one fixed-length search stage.

    Returns ``(threshold, trace, prev)``, where ``prev`` is the last
    ``(A, ARL)`` pair so that the secant slope carries across stages.

    Every evaluation is on ``CAL_SEARCH``.  No early stop, no best-of
    selection: the stage runs exactly ``n_iter`` evaluations and hands back the
    iterate the final update produces.
    """
    require_class(CAL_SEARCH_ARL0, _SEARCH_ONLY)
    trace = []
    for it in range(int(n_iter)):
        batch = int(batch0) + it
        a, se, n = arl0(experiment=CAL_SEARCH_ARL0, family=family,
                        detector="sr", threshold=thr, batch=batch,
                        n_row_blocks=n_row_blocks)
        nxt = _update(thr, a, target, prev)
        trace.append({"stage": stage, "iter": it, "threshold_in": float(thr),
                      "arl0": a, "se": se, "n": int(n), "batch": batch,
                      "row_blocks": int(n_row_blocks),
                      "cycles": int(n_row_blocks) * ROWS_PER_BLOCK,
                      "relative_error": abs(a - target) / target,
                      "threshold_out": float(nxt),
                      "address_class": AddressClass.CAL_SEARCH.value})
        prev = (float(thr), float(a))
        thr = nxt
    return float(thr), trace, prev


def _verify(*, experiment: str, family: str, threshold: float, batch: int,
            target: float) -> dict:
    """One held-out acceptance evaluation.  Never called during a search."""
    require_class(experiment, _VERIFY_ONLY)
    a, se, n = arl0(experiment=experiment, family=family, detector="sr",
                    threshold=threshold, batch=batch,
                    n_row_blocks=CAL_VERIFY_ROW_BLOCKS)
    rel = abs(a - target) / target
    return {"experiment": experiment,
            "address_class": require_class(experiment, _VERIFY_ONLY).value,
            "batch": int(batch), "threshold": float(threshold),
            "row_blocks": CAL_VERIFY_ROW_BLOCKS,
            "cycles": CAL_VERIFY_ROW_BLOCKS * ROWS_PER_BLOCK,
            "arl0": a, "se": se, "n": int(n), "relative_error": rel,
            "z": (a - target) / se if se > 0 else None,
            "tolerance": CAL_TOLERANCE,
            "accepted": bool(rel <= CAL_TOLERANCE)}


def calibrate_family(*, family: str, target: float, start: float) -> dict:
    """The complete frozen calibration for one family.

    Returns a record containing the full search trace, the acceptance
    evaluation(s), the executed budgets, and one of the three frozen outcomes
    ``ACCEPTED_VERIFY_1``, ``ACCEPTED_VERIFY_2`` or ``CALIBRATION_FAILED``.
    """
    thr, trace, prev = _search_stage(
        family=family, target=target, thr=float(start), stage="S1",
        n_iter=CAL_S1_ITERATIONS, n_row_blocks=CAL_S1_ROW_BLOCKS,
        batch0=CAL_S1_BATCH0)
    thr, t2, prev = _search_stage(
        family=family, target=target, thr=thr, stage="S2",
        n_iter=CAL_S2_ITERATIONS, n_row_blocks=CAL_S2_ROW_BLOCKS,
        batch0=CAL_S2_BATCH0, prev=prev)
    trace += t2

    v1 = _verify(experiment=CAL_VERIFY_1_ARL0, family=family, threshold=thr,
                 batch=CAL_VERIFY_1_BATCH, target=target)
    rec = {"family": family, "detector": "sr", "target_arl0": target,
           "start_threshold": float(start), "search_trace": trace,
           "verify_1": v1, "verify_2": None, "retry_trace": [],
           "label": "NEW_P8R_CALIBRATION"}

    if v1["accepted"]:
        rec.update({"threshold": float(thr), "outcome": "ACCEPTED_VERIFY_1",
                    "accepted_by": CAL_VERIFY_1_ARL0})
    else:
        # The single frozen retry.  Fresh CAL_SEARCH addresses; a second,
        # pre-reserved holdout.  CAL_VERIFY_1 is never revisited.
        thr2, t3, _ = _search_stage(
            family=family, target=target, thr=thr, stage="RETRY_S2",
            n_iter=CAL_S2_ITERATIONS, n_row_blocks=CAL_S2_ROW_BLOCKS,
            batch0=CAL_RETRY_BATCH0, prev=prev)
        rec["retry_trace"] = t3
        v2 = _verify(experiment=CAL_VERIFY_2_ARL0, family=family,
                     threshold=thr2, batch=CAL_VERIFY_2_BATCH, target=target)
        rec["verify_2"] = v2
        if v2["accepted"]:
            rec.update({"threshold": float(thr2),
                        "outcome": "ACCEPTED_VERIFY_2",
                        "accepted_by": CAL_VERIFY_2_ARL0})
        else:
            rec.update({"threshold": None, "outcome": "CALIBRATION_FAILED",
                        "accepted_by": None,
                        "last_threshold_considered": float(thr2)})

    ev = executed_budget(rec)
    rec["executed_budget"] = ev
    rec["declared_budget"] = declared_budget()
    rec["budget_matches_declaration"] = bool(
        ev["s1_cycles_per_evaluation"] == CAL_S1_ROW_BLOCKS * ROWS_PER_BLOCK
        and ev["s2_cycles_per_evaluation"] == CAL_S2_ROW_BLOCKS * ROWS_PER_BLOCK
        and ev["verification_cycles"] == CAL_VERIFY_ROW_BLOCKS * ROWS_PER_BLOCK
        and ev["s1_evaluations"] == CAL_S1_ITERATIONS
        and ev["s2_evaluations"] == CAL_S2_ITERATIONS)
    return rec


def declared_budget() -> dict:
    """The single authoritative budget statement, straight from ``config``."""
    return {"s1_evaluations": CAL_S1_ITERATIONS,
            "s1_row_blocks_per_evaluation": CAL_S1_ROW_BLOCKS,
            "s1_cycles_per_evaluation": CAL_S1_ROW_BLOCKS * ROWS_PER_BLOCK,
            "s2_evaluations": CAL_S2_ITERATIONS,
            "s2_row_blocks_per_evaluation": CAL_S2_ROW_BLOCKS,
            "s2_cycles_per_evaluation": CAL_S2_ROW_BLOCKS * ROWS_PER_BLOCK,
            "retry_evaluations_if_used": CAL_S2_ITERATIONS,
            "verification_row_blocks": CAL_VERIFY_ROW_BLOCKS,
            "verification_cycles": CAL_VERIFY_ROW_BLOCKS * ROWS_PER_BLOCK,
            "tolerance": CAL_TOLERANCE,
            "search_class": AddressClass.CAL_SEARCH.value,
            "verify_1_class": AddressClass.CAL_VERIFY_1.value,
            "verify_2_class": AddressClass.CAL_VERIFY_2.value}


def executed_budget(rec: dict) -> dict:
    """Re-derive what was actually executed, from the stored trace alone."""
    s1 = [r for r in rec["search_trace"] if r["stage"] == "S1"]
    s2 = [r for r in rec["search_trace"] if r["stage"] == "S2"]
    rt = list(rec.get("retry_trace", []))
    out = {"s1_evaluations": len(s1), "s2_evaluations": len(s2),
           "retry_evaluations": len(rt),
           "s1_cycles_per_evaluation": s1[0]["cycles"] if s1 else None,
           "s2_cycles_per_evaluation": s2[0]["cycles"] if s2 else None,
           "retry_cycles_per_evaluation": rt[0]["cycles"] if rt else None,
           "verification_cycles": rec["verify_1"]["cycles"],
           "verification_evaluations": 1 + (rec.get("verify_2") is not None),
           "total_search_cycles": sum(r["cycles"] for r in s1 + s2 + rt),
           "search_batches": sorted(r["batch"] for r in s1 + s2 + rt),
           "verify_batches": [rec["verify_1"]["batch"]]
                             + ([rec["verify_2"]["batch"]]
                                if rec.get("verify_2") else []),
           "search_classes": sorted({r["address_class"] for r in s1 + s2 + rt}),
           "verify_classes": sorted(
               {rec["verify_1"]["address_class"]}
               | ({rec["verify_2"]["address_class"]}
                  if rec.get("verify_2") else set()))}
    return out
