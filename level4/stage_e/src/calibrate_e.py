"""Detector calibration on the CALIBRATION block only (protocol S7).

PROTOCOL CLARIFICATION, recorded rather than silently chosen: S7 fixes the
target and the procedure but does not name which reuse policy the calibration
chain runs under. Calibration must not depend on the policy being compared, so
it runs under the FRESH control (rho = 0) -- the policy with no reuse feedback.
The resulting `h` is then shared by every policy, as S7 requires. See
notes/PROTOCOL_DEVIATIONS.md.
"""
from __future__ import annotations

import numpy as np

from metrics_e import block_bootstrap_mean, cycle_lengths
from monitor import M_WINDOW, run_monitor

ARL0_TARGET = 250.0
N_OFFSETS = 10


def measure_arl(residual: np.ndarray, *, lo: int, hi: int, scale: float,
                threshold: float, r0: float, m: int = M_WINDOW) -> np.ndarray:
    """Pooled in-control cycle lengths from staggered starts in [lo, hi).

    Staggering uses the calibration block more efficiently than a single pass.
    The passes overlap, so the pooled cycles are NOT independent; the reported
    uncertainty is a block bootstrap, and this dependence is stated in the
    calibration record.
    """
    span = hi - lo
    starts = lo + (np.arange(N_OFFSETS) * span // N_OFFSETS)
    out = []
    for s in starts:
        run = run_monitor(residual, scale=scale, threshold=threshold, rho=0.0,
                          m=m, r0=r0, start=int(s), stop=hi)
        out.append(cycle_lengths(run.cycles))
    return np.concatenate(out) if out else np.array([])


def calibrate(residual: np.ndarray, *, lo: int, hi: int, scale: float,
              r0: float, target: float = ARL0_TARGET,
              h_lo: float = 0.5, h_hi: float = 60.0,
              tol_log: float = 1e-3, max_iter: int = 40) -> dict:
    """Bisect on log h so the in-control cycle length equals the target."""
    a, b = np.log(h_lo), np.log(h_hi)
    trace = []
    for it in range(max_iter):
        mid = 0.5 * (a + b)
        h = float(np.exp(mid))
        cl = measure_arl(residual, lo=lo, hi=hi, scale=scale, threshold=h, r0=r0)
        arl = float(cl.mean()) if cl.size else float("inf")
        trace.append({"iter": it, "h": h, "arl": arl, "n_cycles": int(cl.size)})
        if arl < target:
            a = mid
        else:
            b = mid
        if b - a < tol_log:
            break
    h = float(np.exp(0.5 * (a + b)))
    cl = measure_arl(residual, lo=lo, hi=hi, scale=scale, threshold=h, r0=r0)
    boot = block_bootstrap_mean(cl, unit="in-control cycle (calibration block)")
    return {"threshold_h": h, "target_arl0": target,
            "achieved_arl0": boot["mean"], "arl0_ci": boot["ci"],
            "arl0_sd": boot.get("sd"), "n_cycles": boot["n"],
            "n_blocks_effective": boot["n_blocks_effective"],
            "reliable": boot["reliable"],
            "relative_error": boot["mean"] / target - 1.0,
            "calibration_block": [int(lo), int(hi)],
            "policy_used": "fresh (rho = 0)", "n_offsets": N_OFFSETS,
            "iterations": len(trace), "trace": trace,
            "note": ("Calibrated on the calibration block ONLY. No evaluation "
                     "or future data was used. Staggered starts overlap, so "
                     "pooled cycles are dependent; the CI is a block bootstrap.")}
