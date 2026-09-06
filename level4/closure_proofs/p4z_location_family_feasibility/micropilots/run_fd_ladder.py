#!/usr/bin/env python3
"""P4Z FD-ladder diagnostic -- NOT RESULT BEARING.

Localises the RB-A vs RB-B offset seen on the frozen SR operating point: is it
the Richardson truncation residual of the map route, or something else?
Runs the RB map route at a ladder of finite-difference steps on identical CRN
paths and reports the h-dependence of the raw central difference and of the
Richardson combination.
"""
from __future__ import annotations
import json, math, os, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; NS = HERE.parent
sys.path.insert(0, str(NS.parent / "p4_theory_generalization" / "src"))
sys.path.insert(0, str(NS / "src"))
from rebaseguard_p4_general.detectors import Detector
from rebaseguard_p4_general.families import REGISTRY
from rebaseguard_p4_general.simulate import stream_counter
from rebaseguard_p4z.analytic import FAMILY_KITS
from rebaseguard_p4z.rbmap import rb_map_batch
from rebaseguard_p4z.rbscore import rb_score_batch

LADDER = (0.2, 0.1, 0.05, 0.025, 0.0125)
M_GRID = (1, 2)
CELLS = [("t1p5", "sr", 520.886133602749, 200_000),
         ("t1p5", "cusum", 5.0, 200_000)]


def main() -> int:
    if os.environ.get("OMP_NUM_THREADS") != "1":
        print("refusing: OMP_NUM_THREADS must be 1", file=sys.stderr); return 2
    batches, paths, seed = 6, 40_000, 4_090_101
    doc = {"schema": "rebaseguard.p4z-fd-ladder-diagnostic.v1",
           "result_bearing": False, "ladder": list(LADDER), "cells": []}
    t_all = time.process_time()
    for fam, kind, thr, ms in CELLS:
        family, kit, det = REGISTRY[fam], FAMILY_KITS[fam], Detector(kind, thr)
        row = {"family": fam, "detector": f"{kind}@{thr:g}", "central": {},
               "richardson": {}, "rb_score": {}}
        # reference: RB-A on the same cell
        acc = {m: [] for m in M_GRID}
        for b in range(batches):
            rng = np.random.Generator(np.random.PCG64([seed, b]))
            v, _, _ = rb_score_batch(family=family, kit=kit, detector_kind=kind,
                threshold=thr, m_grid=M_GRID, n_paths=paths, rng=rng,
                max_steps=ms, new_state=det.new_state, step_fn=det.step)
            for m in M_GRID: acc[m].append(float(v[m].mean()))
        for m in M_GRID:
            a = np.array(acc[m])
            row["rb_score"][str(m)] = {"mean": float(a.mean()),
                "se": float(a.std(ddof=1)/math.sqrt(a.size))}
        # ladder of central differences on CRN paths
        cd = {h: {m: [] for m in M_GRID} for h in LADDER}
        for b in range(batches):
            for h in LADDER:
                g = rb_map_batch(family=family, kit=kit, detector_kind=kind,
                    threshold=thr, m_grid=M_GRID, e_values=(h, -h),
                    n_paths=paths, seed=seed + 1, batch=b, max_steps=ms,
                    new_state=det.new_state, step_fn=det.step,
                    stream_counter=stream_counter)
                for m in M_GRID:
                    cd[h][m].append(float((-(g[h][m]-g[-h][m])/(2.0*h)).mean()))
        for h in LADDER:
            row["central"][f"{h:g}"] = {}
            for m in M_GRID:
                a = np.array(cd[h][m])
                row["central"][f"{h:g}"][str(m)] = {"mean": float(a.mean()),
                    "se": float(a.std(ddof=1)/math.sqrt(a.size))}
        for coarse, fine in zip(LADDER[:-1], LADDER[1:]):
            key = f"{coarse:g}/{fine:g}"; row["richardson"][key] = {}
            for m in M_GRID:
                r = (4*np.array(cd[fine][m]) - np.array(cd[coarse][m]))/3.0
                row["richardson"][key][str(m)] = {"mean": float(r.mean()),
                    "se": float(r.std(ddof=1)/math.sqrt(r.size))}
        doc["cells"].append(row)
    doc["total_cpu_seconds"] = time.process_time() - t_all
    out = NS/"micropilots"/"diagnostics"/"fd_ladder.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True)+"\n")
    for c in doc["cells"]:
        print(f"\n{c['family']}/{c['detector']}")
        for m in ("1","2"):
            a = c["rb_score"][m]
            print(f"  m={m}  RB-A = {a['mean']:.5f} +/- {a['se']:.5f}")
            for h in LADDER:
                v = c["central"][f"{h:g}"][m]
                print(f"        central h={h:<7g} {v['mean']:.5f} +/- {v['se']:.5f}"
                      f"   offset {v['mean']-a['mean']:+.5f}")
            for k, v in c["richardson"].items():
                print(f"        Richardson {k:<14s} {v[m]['mean']:.5f} +/- {v[m]['se']:.5f}"
                      f"   offset {v[m]['mean']-a['mean']:+.5f}")
    print(f"\ntotal {doc['total_cpu_seconds']:.1f} CPU-s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
