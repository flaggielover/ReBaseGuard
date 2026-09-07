#!/usr/bin/env python3
"""P4ZA Phase 5 -- FD ladder micro-calibration.  NOT RESULT BEARING.

Extends the ladder BELOW the frozen finite-difference steps to determine
empirically whether the central difference reaches its predicted O(h^2) regime,
and where.  Its only purpose is to falsify a bad ladder before one is frozen.
"""
from __future__ import annotations
import json, math, os, sys, time
from pathlib import Path
import numpy as np

NS = Path(__file__).resolve().parent.parent
P4Z = NS.parent / "p4z_location_family_feasibility"
sys.path.insert(0, str(P4Z / "src"))
sys.path.insert(0, str(NS.parent / "p4_theory_generalization" / "src"))

from rebaseguard_p4_general.detectors import Detector          # noqa: E402
from rebaseguard_p4_general.families import REGISTRY           # noqa: E402
from rebaseguard_p4_general.simulate import stream_counter     # noqa: E402
from rebaseguard_p4z.analytic import FAMILY_KITS               # noqa: E402
from rebaseguard_p4z.rbmap import rb_map_batch                 # noqa: E402

LADDER = (0.2, 0.1, 0.05, 0.025, 0.0125, 0.00625)
M_GRID = (1, 5)
BLOCKS = 60
SEED = 4_190_001
CELLS = [
    ("frozen/cusum@5/gaussian",    "gaussian", "cusum", 5.0,               200_000,  3942, "K7-affected, worst drift"),
    ("frozen/sr@520.886/gaussian", "gaussian", "sr",    520.886133602749,  200_000,  3942, "K7-affected"),
    ("frozen/sr@520.886/laplace",  "laplace",  "sr",    520.886133602749,  200_000,  3942, "K7-affected, other light family"),
    ("frozen/cusum@5/t1p5",        "t1p5",     "cusum", 5.0,               200_000, 28450, "residue control, already PASS"),
]


def main() -> int:
    for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS","NUMEXPR_NUM_THREADS"):
        if os.environ.get(v) != "1":
            print(f"refusing: {v} must be 1", file=sys.stderr); return 2
    doc = {"schema": "rebaseguard.p4za-ladder-calibration.v1",
           "result_bearing": False,
           "purpose": "falsify a bad FD ladder before freezing one",
           "ladder": list(LADDER), "blocks": BLOCKS, "seed": SEED,
           "m_grid": list(M_GRID), "cells": []}
    t_all = time.process_time()
    for cid, fam, kind, thr, msteps, paths, note in CELLS:
        family, kit, det = REGISTRY[fam], FAMILY_KITS[fam], Detector(kind, thr)
        per = {h: {m: [] for m in M_GRID} for h in LADDER}
        t0 = time.process_time()
        for b in range(BLOCKS):
            for h in LADDER:
                g = rb_map_batch(family=family, kit=kit, detector_kind=kind,
                    threshold=thr, m_grid=M_GRID, e_values=(h, -h),
                    n_paths=paths, seed=SEED, batch=b, max_steps=msteps,
                    new_state=det.new_state, step_fn=det.step,
                    stream_counter=stream_counter)
                for m in M_GRID:
                    per[h][m].append(float((-(g[h][m]-g[-h][m])/(2.0*h)).mean()))
        cpu = time.process_time() - t0
        row = {"configuration": cid, "note": note, "cpu_seconds": cpu, "by_m": {}}
        for m in M_GRID:
            D = {h: np.array(per[h][m]) for h in LADDER}
            means = {f"{h:g}": float(D[h].mean()) for h in LADDER}
            ses   = {f"{h:g}": float(D[h].std(ddof=1)/math.sqrt(BLOCKS)) for h in LADDER}
            # CRN-paired successive differences and their own standard errors
            diffs, orders = {}, {}
            for hc, hf in zip(LADDER[:-1], LADDER[1:]):
                d = D[hc] - D[hf]
                diffs[f"{hc:g}-{hf:g}"] = {"mean": float(d.mean()),
                                           "se": float(d.std(ddof=1)/math.sqrt(BLOCKS))}
            keys = list(diffs)
            for a, b2 in zip(keys[:-1], keys[1:]):
                ra, rb = diffs[a]["mean"], diffs[b2]["mean"]
                orders[f"{a} / {b2}"] = {
                    "ratio": ra/rb if rb else float("nan"),
                    "implied_order_p": math.log2(ra/rb) if (rb and ra/rb > 0) else float("nan")}
            rich = {}
            for hc, hf in zip(LADDER[:-1], LADDER[1:]):
                R = (4*D[hf] - D[hc])/3.0
                rich[f"{hc:g}/{hf:g}"] = {"mean": float(R.mean()),
                                          "se": float(R.std(ddof=1)/math.sqrt(BLOCKS))}
            rk = list(rich)
            adj = {}
            for a, b2 in zip(rk[:-1], rk[1:]):
                d = rich[a]["mean"] - rich[b2]["mean"]
                adj[f"{a} vs {b2}"] = {"difference": d, "residual_estimate_over_15": d/15.0}
            row["by_m"][str(m)] = {"central_difference": means, "central_difference_se": ses,
                                   "paired_differences": diffs, "implied_orders": orders,
                                   "richardson": rich, "adjacent_richardson": adj}
        doc["cells"].append(row)
        print(f"{cid:30s} {cpu:7.1f} CPU-s")
        for m in M_GRID:
            o = row["by_m"][str(m)]["implied_orders"]
            ps = "  ".join(f"{k.split('/')[0].strip()}:{v['implied_order_p']:.2f}" for k,v in o.items())
            print(f"    m={m} implied order p by rung pair -> {ps}")
    doc["total_cpu_seconds"] = time.process_time() - t_all
    out = NS/"results"/"ladder_calibration.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True)+"\n")
    print(f"\ntotal {doc['total_cpu_seconds']:.1f} CPU-s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
