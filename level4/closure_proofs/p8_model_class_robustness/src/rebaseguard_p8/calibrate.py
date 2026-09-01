"""Threshold calibration to the frozen in-control ARL target.

Used **only** for the SR detector on the five non-Gaussian families, where the
repository supplies no threshold (`P8_DEFINITION_AUDIT.md` section 7,
`PRIORITY_DEPENDENCY_AUDIT.md` `N1`).  The CUSUM thresholds are read from
Stage-D D3 and are never recalibrated.

Procedure: bisection in ``log(threshold)`` against ``ARL_0(threshold)``, the
same shape as ``stage_d/src/calibrate.py``.  Every evaluation uses the P8
addressable primitive field at a declared batch address, so the whole trace is
replayable from the recorded addresses alone.
"""
from __future__ import annotations

import numpy as np

from .detectors import make_step
from .primitives import BLOCK_LEN, ROWS_PER_BLOCK, stopped_block


def arl0(*, experiment: str, family: str, detector: str, threshold: float,
         batch: int, n_row_blocks: int, e: float = 0.0,
         max_steps: int = 4_000_000) -> tuple[float, float, int]:
    """``(mean tau, standard error, n)`` for independent reset cycles."""
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


def calibrate(*, experiment: str, family: str, detector: str, target: float,
              start: float, n_row_blocks: int = 61, max_iter: int = 12,
              rel_tol: float = 2e-3) -> dict:
    """Calibrate a threshold to ``target`` and return it with the full trace.

    For the two-chart SR the in-control ARL is asymptotically **linear** in the
    natural threshold ``A``, so the proportional update ``A <- A * target/ARL(A)``
    is the natural iteration and converges in a few steps.  A log-bisection on a
    wide bracket is not used because an over-large ``A`` costs simulation time
    proportional to its own (enormous) ARL.

    Every evaluation is at a declared batch address, so the trace replays from
    the recorded addresses alone.
    """
    trace = []

    def evaluate(thr, it):
        a, se, n = arl0(experiment=experiment, family=family, detector=detector,
                        threshold=thr, batch=1_000 + it,
                        n_row_blocks=n_row_blocks)
        trace.append({"iter": it, "threshold": float(thr), "arl0": a,
                      "se": se, "n": n, "batch": 1_000 + it,
                      "relative_error": abs(a - target) / target})
        return a

    thr = float(start)
    best = None
    for it in range(max_iter):
        a = evaluate(thr, it)
        rel = abs(a - target) / target
        if best is None or rel < best[1]:
            best = (thr, rel)
        if rel <= rel_tol:
            break
        # damped proportional update; damping keeps Monte Carlo noise from
        # driving the iterate away once the residual is at the noise floor
        factor = (target / a) ** (1.0 if rel > 0.05 else 0.6)
        thr = float(np.clip(thr * factor, thr / 4.0, thr * 4.0))
    return {"family": family, "detector": detector, "target_arl0": target,
            "threshold": best[0], "relative_error_at_selection": best[1],
            "n_iterations": len(trace), "trace": trace,
            "start_threshold": float(start),
            "n_cycles_per_evaluation": int(n_row_blocks * ROWS_PER_BLOCK),
            "procedure": ("damped proportional iteration A <- A*(target/ARL)^p "
                          "on the P8 addressable field; ARL_0 is asymptotically "
                          "linear in the SR natural threshold"),
            "label": "NEW_P8_CALIBRATION"}
