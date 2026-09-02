#!/usr/bin/env python3
"""R3 (A5 repair) — burn-in sensitivity of the full-reuse operational estimate.

This is the generator that P9's ``results/burnin_sensitivity.json`` never had.

P9's finding (its ``P9-N1``) was that the approach to the stationary regime
under full reuse is slow and oscillatory, so a finite-horizon operational ARL
depends materially on the burn-in convention.  P9R keeps the finding, supplies
the generator, and additionally reports the *authoritative* P7 burn-in (12) as
one of the tabulated conventions so that the comparison in ``REPRODUCTION.md``
is convention-matched rather than convention-explained after the fact.

The SR cells use the corrected frozen recurrence.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

P9R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P9R / "src"))

from rebaseguard_p9r import DETECTORS                          # noqa: E402
from rebaseguard_p9r.chain import simulate_chain               # noqa: E402
from rebaseguard_p9r.provenance import seed_for, write_artifact  # noqa: E402

M_GRID = (1, 5)
RHO = 1.0
DISCARDS = (0, 1, 3, 6, 10, 12, 20)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    n_rep = 400 if args.quick else 5000
    n_cycles = 24 if args.quick else 50

    rows = []
    for det in DETECTORS:
        for m in M_GRID:
            sd = seed_for("burnin", det, m, RHO, n_rep, n_cycles)
            r = simulate_chain(detector=det, m=m, rho=RHO, n_rep=n_rep,
                               n_cycles=n_cycles, seed=sd)
            by_cycle = r.tau.mean(axis=0)
            by_cycle_se = r.tau.std(axis=0, ddof=1) / np.sqrt(n_rep)
            conventions = {}
            for d in DISCARDS:
                if d >= n_cycles:
                    continue
                arl, se = r.arl(d)
                conventions[str(d)] = {"discard": d, "arl": arl, "arl_se": se}
            rows.append({
                "detector": det, "m": m, "rho": RHO, "seed": sd,
                "n_rep": n_rep, "n_cycles": n_cycles,
                "cycle_mean": [float(x) for x in by_cycle],
                "cycle_mean_se": [float(x) for x in by_cycle_se],
                "conventions": conventions,
                "pooled_over_discard12":
                    conventions["0"]["arl"] / conventions["12"]["arl"],
                "monotone_approach": bool(
                    np.all(np.diff(by_cycle[1:]) >= 0.0)),
            })

    payload = {"rows": rows, "discards": list(DISCARDS),
               "authoritative_p7_burn_in": 12,
               "note": "the statistical unit is the replicate; cycles within a "
                       "replicate are dependent and are never pooled as "
                       "independent observations"}

    name = "burnin_sensitivity_quick.json" if args.quick else "burnin_sensitivity.json"
    write_artifact(name,
                   schema="rebaseguard.p9r.burnin-sensitivity.v1",
                   generator="experiments/run_burnin_sensitivity.py",
                   config={"m_grid": list(M_GRID), "rho": RHO,
                           "discards": list(DISCARDS), "n_rep": n_rep,
                           "n_cycles": n_cycles, "quick": args.quick},
                   payload=payload)
    for r in rows:
        cs = r["conventions"]
        print(f"{r['detector']:5s} m={r['m']}: "
              + "  ".join(f"d{d}={cs[d]['arl']:.2f}" for d in cs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
