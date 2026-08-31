#!/usr/bin/env python3
"""E5: runaway stress test and one-step forgetting.

Section 10 of the P5 brief: deliberately look for divergence.  Extreme initial
reference errors, rho at and near 1, both detectors, long chains.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import RESULTS, SEED_FAMILY                   # noqa: E402
from rebaseguard_p5.chain import simulate_chain_raw               # noqa: E402
from rebaseguard_p5.kernel import child_rng, raw_map_point        # noqa: E402

E0 = (0.0, 5.0, 20.0, 100.0, 1000.0, -1000.0, 1e6)
RHOS = (0.9, 0.99, 1.0)

rows = []
for det in ("cusum", "sr"):
    for m in (1, 5):
        for rho in RHOS:
            for i, e0 in enumerate(E0):
                rng = child_rng(SEED_FAMILY, det, 90 + m, i + 17 * int(rho * 100))
                r = simulate_chain_raw(detector=det, m=m, rho=rho, n_rep=200,
                                       n_cycles=400, burn_in=0, rng=rng, e0=e0)
                e = r.e_start
                rows.append({
                    "detector": det, "m": m, "rho": rho, "e0": e0,
                    "n_rep": 200, "n_cycles": 400,
                    "cycle1_abs_mean": float(np.abs(e[:, 1]).mean()),
                    "cycle1_abs_max": float(np.abs(e[:, 1]).max()),
                    "cycle1_rms": float(np.sqrt((e[:, 1] ** 2).mean())),
                    "tail_rms": float(np.sqrt((e[:, 100:] ** 2).mean())),
                    "global_abs_max": float(np.abs(e).max()),
                    "argmax_cycle": int(np.unravel_index(
                        np.abs(e).argmax(), e.shape)[1]),
                    "final_abs_mean": float(np.abs(e[:, -1]).mean()),
                    "tau1_cycle0": float((r.tau[:, 0] == 1).mean()),
                })
                print(f"{det} m={m} rho={rho:.2f} e0={e0:>9.0f} "
                      f"|e_1|={rows[-1]['cycle1_abs_mean']:.4f} "
                      f"max|e_1|={rows[-1]['cycle1_abs_max']:.3f} "
                      f"tailRMS={rows[-1]['tail_rms']:.4f} "
                      f"globalmax={rows[-1]['global_abs_max']:.3f}"
                      f" (@cycle {rows[-1]['argmax_cycle']})", flush=True)

# one-step forgetting: TV-scale comparison of R,S at extreme e against the reset law
forget = []
for det in ("cusum", "sr"):
    for e in (10.0, 100.0, 1000.0):
        r = raw_map_point(detector=det, e=e, m_grid=(1, 5), n_paths=200_000,
                          n_batches=8, seed_family=SEED_FAMILY, tag=9100)
        forget.append({"detector": det, "e": e, "A": r["tau_mean"],
                       "p_tau1": r["p_tau1"],
                       "R_m1": r["per_m"][0]["R"], "S_m1": r["per_m"][0]["S"],
                       "R_m5": r["per_m"][1]["R"], "S_m5": r["per_m"][1]["S"]})
        print(f"forget {det} e={e:7.0f} A={r['tau_mean']:.4f} "
              f"p(tau=1)={r['p_tau1']:.6f} R={r['per_m'][0]['R']:+.5f} "
              f"S={r['per_m'][0]['S']:.5f}", flush=True)

(RESULTS / "stress.json").write_text(json.dumps(
    {"seed_family": SEED_FAMILY, "rows": rows, "forgetting": forget}, indent=1))
print("wrote stress.json")
