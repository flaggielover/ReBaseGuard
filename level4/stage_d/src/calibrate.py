"""D1.1 — ARL0 calibration by frozen bisection.

The threshold is fixed here, on its own seed family, and is NEVER revisited
after any Gamma is seen. Calibration uncertainty is propagated and reported.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stopped import CUSUM, SR, run_batches                      # noqa: E402


def measure_arl0(detector: str, threshold: float, *, n_paths: int,
                 seed_seq, batch: int = 20_000, **kw) -> tuple[float, float]:
    s = run_batches(detector=detector, threshold=threshold, e=0.0,
                    n_paths=n_paths, batch=batch, L=2,
                    m_grid=np.array([1]), seed_seq=seed_seq, **kw)
    var = s.sum_tau_sq / s.n - s.arl ** 2
    return s.arl, float(np.sqrt(max(var, 0.0) / s.n))


def bisect_threshold(detector: str, target_arl0: float, *, lo: float, hi: float,
                     n_paths: int, root_seed: int, tol_log: float = 1e-3,
                     max_iter: int = 30, batch: int = 20_000,
                     verbose: bool = True, **kw) -> dict[str, Any]:
    """Bisect on log-threshold until ARL0 brackets the target.

    Each evaluation uses its own child seed, so the search cannot exploit a
    lucky draw; and the final threshold is re-measured on a fresh seed so the
    reported ARL0 is not the one the search selected on.
    """
    log_lo, log_hi = np.log(lo), np.log(hi)
    trace = []
    for it in range(max_iter):
        log_mid = 0.5 * (log_lo + log_hi)
        thr = float(np.exp(log_mid))
        ss = np.random.SeedSequence([root_seed, 11, it])
        arl, se = measure_arl0(detector, thr, n_paths=n_paths, seed_seq=ss,
                               batch=batch, **kw)
        trace.append({"iter": it, "threshold": thr, "arl0": arl, "se": se})
        if verbose:
            print(f"    it {it:2d}  thr={thr:.6f}  ARL0={arl:9.3f} +/- {se:6.3f}",
                  flush=True)
        if arl < target_arl0:
            log_lo = log_mid
        else:
            log_hi = log_mid
        if log_hi - log_lo < tol_log:
            break
    thr = float(np.exp(0.5 * (log_lo + log_hi)))
    ss = np.random.SeedSequence([root_seed, 12, 0])          # fresh, unbiased
    arl, se = measure_arl0(detector, thr, n_paths=4 * n_paths, seed_seq=ss,
                           batch=batch, **kw)
    return {"detector": detector, "target_arl0": target_arl0,
            "threshold": thr, "achieved_arl0": arl, "arl0_se": se,
            "relative_error": arl / target_arl0 - 1.0,
            "iterations": len(trace), "trace": trace,
            "final_measurement_seed": [root_seed, 12, 0],
            "n_paths_final": 4 * n_paths}
