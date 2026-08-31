"""E3/E4: the two response functions every P7 bridge statement is built on.

A(x)      = E[tau | reset state, innovations ~ N(-x,1)]     run-length response
g_m(x)    = E_x[zbar_m]                                     reuse-drift response

Both are measured on one shared innovation stream per grid point, so A and every
g_m at that point are perfectly paired.  A is even and g_m is odd by the
sign-reversal symmetry the P1/P2 theorems use; the negative half of the grid is
simulated at a few points purely as a symmetry check.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p7 import CUSUM, SR, SR_THRESHOLD, CUSUM_THRESHOLD   # noqa: E402
from rebaseguard_p7.config import (                                   # noqa: E402
    DETECTOR_CODE, M_GRID, RESULTS, SEED_FAMILY)
from rebaseguard_p7.cycles import run_cycle_batches                   # noqa: E402

X_GRID = [0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.125, 0.15,
          0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90,
          1.00, 1.20, 1.40, 1.60, 1.80, 2.00, 2.50, 3.00]
SYMMETRY_CHECK = [-0.05, -0.20, -1.00]


def n_for(x: float) -> int:
    ax = abs(x)
    if ax <= 0.15:
        return 400_000
    if ax <= 0.50:
        return 200_000
    return 100_000


def main() -> None:
    out = {"seed_family": SEED_FAMILY, "m_grid": list(M_GRID), "curves": {}}
    for det, thr in ((CUSUM, CUSUM_THRESHOLD), (SR, SR_THRESHOLD)):
        rows = []
        t0 = time.time()
        for x in X_GRID + SYMMETRY_CHECK:
            n = n_for(x)
            ss = np.random.SeedSequence([SEED_FAMILY, 3, DETECTOR_CODE[det],
                                         0 if x >= 0 else 1,
                                         int(round(abs(x) * 1e6))])
            cs = run_cycle_batches(detector=det, e=x, n_paths=n,
                                   m_grid=M_GRID, seed_seq=ss, threshold=thr)
            tau = cs.tau.astype(float)
            row = {
                "x": x, "n": n,
                "arl": float(tau.mean()),
                "arl_se": float(tau.std(ddof=1) / np.sqrt(n)),
                "arl_median": float(np.median(tau)),
                "p_up": float(cs.up.mean()),
                "g": {}, "g_se": {}, "var_zbar": {},
                "symmetry_check": x in SYMMETRY_CHECK,
            }
            for m in M_GRID:
                zb = cs.zbar_for(m)
                row["g"][str(m)] = float(zb.mean())
                row["g_se"][str(m)] = float(zb.std(ddof=1) / np.sqrt(n))
                row["var_zbar"][str(m)] = float(zb.var(ddof=1))
            if x == 0.0:
                row["gamma_tilde"] = {
                    str(m): float((cs.zbar_for(m) * cs.T).mean()) for m in M_GRID}
                row["gamma_tilde_se"] = {
                    str(m): float((cs.zbar_for(m) * cs.T).std(ddof=1) / np.sqrt(n))
                    for m in M_GRID}
            rows.append(row)
            print(f"{det} x={x:+.3f} n={n} ARL={row['arl']:9.3f} "
                  f"g1={row['g']['1']:+.4f} [{time.time()-t0:6.1f}s]", flush=True)
        out["curves"][det] = rows
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "response_curves.json").write_text(json.dumps(out, indent=1))
    print("wrote", RESULTS / "response_curves.json")


if __name__ == "__main__":
    main()
