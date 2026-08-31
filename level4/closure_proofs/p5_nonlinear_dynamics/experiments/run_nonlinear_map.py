#!/usr/bin/env python3
"""E1: high-resolution estimate of R(e)=E[Rbar|e], S(e)=Var(Rbar|e), A(e)=E[tau|e].

Because M_{D,m,rho}(e) = rho * R_{D,m}(e) exactly (DEFINITION_AUDIT.md §4), one
pass over ``e`` yields the conditional-mean map for EVERY rho.  Statistical unit
is the independent batch; reported errors are batch standard errors.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import RESULTS, SEED_FAMILY                  # noqa: E402
from rebaseguard_p5.kernel import raw_map_point                  # noqa: E402

M_GRID = (1, 2, 3, 5)
DETECTORS = ("cusum", "sr")
MAGS = (0.0, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4,
        0.5, 0.65, 0.8, 1.0, 1.2, 1.5, 1.8, 2.2, 2.6, 3.0, 3.5, 4.0, 5.0)
N_BATCHES = 8


def plan(e: float) -> int:
    a = abs(e)
    if a <= 0.1:
        return 50_000
    if a <= 0.5:
        return 100_000
    if a <= 1.5:
        return 200_000
    return 400_000


def main(seed_family: int = SEED_FAMILY, tag: int = 1,
         out: str = "nonlinear_map.json") -> None:
    grid = sorted({round(s * v, 6) for v in MAGS for s in (1.0, -1.0)})
    rows, t0 = [], time.time()
    for det in DETECTORS:
        for i, e in enumerate(grid):
            r = raw_map_point(detector=det, e=e, m_grid=M_GRID,
                              n_paths=plan(e), n_batches=N_BATCHES,
                              seed_family=seed_family, tag=tag * 1000 + i)
            rows.append(r)
            print(f"{det} e={e:+.3f} A={r['tau_mean']:9.2f} "
                  f"R1={r['per_m'][0]['R']:+.5f} "
                  f"({time.time() - t0:6.1f}s)", flush=True)
    (RESULTS / out).write_text(json.dumps(
        {"seed_family": seed_family, "tag": tag, "m_grid": list(M_GRID),
         "n_batches": N_BATCHES, "e_grid": grid, "rows": rows}, indent=1))
    print("wrote", RESULTS / out)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--seed-family", type=int, default=SEED_FAMILY)
    p.add_argument("--tag", type=int, default=1)
    p.add_argument("--out", default="nonlinear_map.json")
    a = p.parse_args()
    main(a.seed_family, a.tag, a.out)
