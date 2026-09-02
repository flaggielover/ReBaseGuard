#!/usr/bin/env python3
"""R2 — corrected cross-priority reproduction against authoritative P7 cells.

P9 compared its replay against *prose ranges* copied from P7's adjudication.
P9R instead reads the authoritative P7 production artifact

    level4/closure_proofs/p7_statistical_consequences/results/consequences.json

at run time and reproduces each frozen cell under P7's own estimator
convention (``n_rep``, ``n_cycles``, ``burn_in`` are taken from the P7 cell,
never transcribed by hand).  CUSUM and SR are reported separately.

Agreement is judged by the two-sample z statistic with the **combined**
standard error ``z = (a - b) / sqrt(se_a^2 + se_b^2)``; the verdict language is
``MC_CONSISTENT`` / ``MC_TENSION`` / ``MC_DISAGREEMENT`` at |z| <= 3 / <= 4 /
> 4.  Nothing is ever called "exact agreement".

The same cells are additionally replayed with the **defective** P9 SR update on
identical seeds, so the material effect of the ``log 2`` first-step shift is
measured rather than asserted.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

P9R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P9R / "src"))

from rebaseguard_p9r import DETECTORS                          # noqa: E402
from rebaseguard_p9r.chain import simulate_chain               # noqa: E402
from rebaseguard_p9r.provenance import (                       # noqa: E402
    REPO_ROOT, seed_for, write_artifact,
)

P7_CONSEQUENCES = (REPO_ROOT / "level4" / "closure_proofs"
                   / "p7_statistical_consequences" / "results"
                   / "consequences.json")

M_GRID = (1, 2, 3, 5)
RHO_GRID = (0.0, 1.0)


def verdict(z: float) -> str:
    a = abs(z)
    if a <= 3.0:
        return "MC_CONSISTENT"
    if a <= 4.0:
        return "MC_TENSION"
    return "MC_DISAGREEMENT"


def p7_cells() -> dict:
    data = json.loads(P7_CONSEQUENCES.read_text())
    out = {}
    for c in data["cells"]:
        key = (c["detector"], int(c["m"]), round(float(c["rho"]), 10))
        if key[2] in RHO_GRID and key[1] in M_GRID:
            out[key] = c
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="reduced deterministic replay for the focused tests")
    args = ap.parse_args()

    cells = p7_cells()
    if len(cells) != len(DETECTORS) * len(M_GRID) * len(RHO_GRID):
        raise SystemExit(f"expected 16 P7 cells, found {len(cells)}")

    rows, sr_defect_rows = [], []
    for det in DETECTORS:
        for m in M_GRID:
            for rho in RHO_GRID:
                c = cells[(det, m, rho)]
                n_rep = 400 if args.quick else int(c["n_rep"])
                n_cycles = 16 if args.quick else int(c["n_cycles"])
                burn_in = 4 if args.quick else int(c["burn_in"])
                sd = seed_for("repro", det, m, rho, n_rep, n_cycles)
                r = simulate_chain(detector=det, m=m, rho=rho, n_rep=n_rep,
                                   n_cycles=n_cycles, seed=sd)
                arl, se = r.arl(burn_in)
                p7_arl, p7_se = float(c["arl"]), float(c["arl_se"])
                z = (arl - p7_arl) / np.sqrt(se ** 2 + p7_se ** 2)
                cyc1, cyc1_se = r.cycle_mean(0)
                cyc2, cyc2_se = r.cycle_mean(1)
                p7_cyc = c["cycle_arl"]
                row = {
                    "detector": det, "m": m, "rho": rho,
                    "n_rep": n_rep, "n_cycles": n_cycles, "burn_in": burn_in,
                    "seed": sd,
                    "p9r_arl": arl, "p9r_arl_se": se,
                    "p7_arl": p7_arl, "p7_arl_se": p7_se,
                    "combined_se": float(np.sqrt(se ** 2 + p7_se ** 2)),
                    "z": float(z), "verdict": verdict(float(z)),
                    "p9r_cycle1_nominal_A0": cyc1, "p9r_cycle1_se": cyc1_se,
                    "p7_cycle1": float(p7_cyc[0]),
                    "p9r_cycle2": cyc2, "p9r_cycle2_se": cyc2_se,
                    "p7_cycle2": float(p7_cyc[1]),
                }
                rows.append(row)

                if det == "sr":
                    rd = simulate_chain(detector=det, m=m, rho=rho, n_rep=n_rep,
                                        n_cycles=n_cycles, seed=sd,
                                        defective_sr=True)
                    darl, dse = rd.arl(burn_in)
                    dz = (darl - p7_arl) / np.sqrt(dse ** 2 + p7_se ** 2)
                    paired = (r.tau[:, burn_in:].mean(axis=1)
                              - rd.tau[:, burn_in:].mean(axis=1))
                    sr_defect_rows.append({
                        "m": m, "rho": rho, "seed": sd,
                        "corrected_arl": arl, "corrected_se": se,
                        "defective_arl": darl, "defective_se": dse,
                        "defective_z_vs_p7": float(dz),
                        "defective_verdict_vs_p7": verdict(float(dz)),
                        "paired_mean_difference": float(paired.mean()),
                        "paired_se": float(paired.std(ddof=1)
                                           / np.sqrt(paired.size)),
                        "paired_z": float(paired.mean()
                                          / (paired.std(ddof=1)
                                             / np.sqrt(paired.size))),
                    })

    summary = {}
    for det in DETECTORS:
        sub = [r for r in rows if r["detector"] == det]
        summary[det] = {
            "n_cells": len(sub),
            "max_abs_z": max(abs(r["z"]) for r in sub),
            "n_mc_consistent": sum(r["verdict"] == "MC_CONSISTENT" for r in sub),
            "n_mc_tension": sum(r["verdict"] == "MC_TENSION" for r in sub),
            "n_mc_disagreement": sum(r["verdict"] == "MC_DISAGREEMENT"
                                     for r in sub),
            "arl_rho0_range": [min(r["p9r_arl"] for r in sub if r["rho"] == 0.0),
                               max(r["p9r_arl"] for r in sub if r["rho"] == 0.0)],
            "arl_rho1_range": [min(r["p9r_arl"] for r in sub if r["rho"] == 1.0),
                               max(r["p9r_arl"] for r in sub if r["rho"] == 1.0)],
            "cycle2_rho1_range": [
                min(r["p9r_cycle2"] for r in sub if r["rho"] == 1.0),
                max(r["p9r_cycle2"] for r in sub if r["rho"] == 1.0)],
        }

    payload = {"rows": rows, "per_detector_summary": summary,
               "sr_defect_comparison": sr_defect_rows,
               "p7_source": str(P7_CONSEQUENCES.relative_to(REPO_ROOT)),
               "verdict_thresholds": {"MC_CONSISTENT": 3.0, "MC_TENSION": 4.0}}

    name = "reproduction_quick.json" if args.quick else "reproduction.json"
    write_artifact(name,
                   schema="rebaseguard.p9r.reproduction.v1",
                   generator="experiments/run_reproduction.py",
                   config={"m_grid": list(M_GRID), "rho_grid": list(RHO_GRID),
                           "detectors": list(DETECTORS), "quick": args.quick,
                           "estimator": "per-replicate mean cycle length "
                                        "after burn_in, P7 convention",
                           "n_rep_source": "P7 cell", "burn_in_source": "P7 cell"},
                   payload=payload)
    for r in rows:
        print(f"{r['detector']:5s} m={r['m']} rho={r['rho']:.0f}  "
              f"P9R {r['p9r_arl']:8.3f}+-{r['p9r_arl_se']:.3f}   "
              f"P7 {r['p7_arl']:8.3f}+-{r['p7_arl_se']:.3f}   "
              f"z={r['z']:+.2f}  {r['verdict']}")
    for r in sr_defect_rows:
        print(f"SR defect m={r['m']} rho={r['rho']:.0f}: corrected "
              f"{r['corrected_arl']:.3f} vs defective {r['defective_arl']:.3f}"
              f"  paired dz={r['paired_z']:+.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
