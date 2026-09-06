#!/usr/bin/env python3
"""P4Z micro-pilots -- FALSIFICATION ONLY, NOT RESULT BEARING.

These runs exist to kill broken estimators cheaply while the CUSUM Aux4
campaign owns the authoritative compute.  They are single threaded, they are
budgeted in seconds, and nothing they produce is a scientific certificate:
every output carries ``result_bearing: false`` and no P4/P4X/P4Y verdict may
cite it.

Usage:  python micropilots/run_micropilots.py [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
NS = HERE.parent
P4_SRC = NS.parent / "p4_theory_generalization" / "src"
sys.path.insert(0, str(P4_SRC))
sys.path.insert(0, str(NS / "src"))

from rebaseguard_p4_general.detectors import Detector           # noqa: E402
from rebaseguard_p4_general.families import REGISTRY            # noqa: E402
from rebaseguard_p4_general.simulate import (                   # noqa: E402
    simulate_group, stream_counter,
)
from rebaseguard_p4z.analytic import FAMILY_KITS                # noqa: E402
from rebaseguard_p4z.rbscore import rb_score_batch              # noqa: E402
from rebaseguard_p4z.rbmap import rb_map_derivative_batch       # noqa: E402

FD_STEPS = (0.05, 0.025)          # frozen P4 convention, unchanged
R_STAR = 0.010823063             # frozen P4X precision target, unchanged

#: (label, family, detector kind, threshold, max_steps, regime)
CELLS = [
    ("easy",           "gaussian", "cusum", 2.0,               60_000,  "control"),
    ("difficult",      "t1p5",     "cusum", 5.0,              200_000,  "heavy"),
    ("difficult",      "t1p5",     "sr",    520.886133602749, 200_000,  "heavy"),
    ("near-threshold", "t1p5",     "sr",    20.0,              60_000,  "heavy"),
    ("near-threshold", "t3",       "cusum", 5.0,              200_000,  "moderate"),
]
M_GRID = (1, 2, 3, 5)


def tail_diagnostics(x: np.ndarray) -> dict[str, float]:
    """Pilot-4's concentration diagnostics, plus a Hill index."""
    x = np.asarray(x, float)
    dev = (x - x.mean()) ** 2
    total = float(dev.sum())
    order = np.sort(dev)[::-1]
    k = max(10, x.size // 200)
    absdev = np.sort(np.abs(x - x.mean()))[::-1][: k + 1]
    hill = (
        float(1.0 / np.mean(np.log(absdev[:k] / absdev[k])))
        if absdev[k] > 0 else float("nan")
    )
    return {
        "top1_share_of_squared_deviation": float(order[0] / total),
        "top5_share_of_squared_deviation": float(order[:5].sum() / total),
        "hill_index_upper_half_percent": hill,
        "per_path_sd": float(x.std(ddof=1)),
    }


def summarise(batch_means: list[float]) -> dict[str, float]:
    v = np.asarray(batch_means, float)
    mean = float(v.mean())
    se = float(v.std(ddof=1) / math.sqrt(v.size))
    return {"mean": mean, "se": se,
            "relative_se": abs(se / mean) if mean != 0 else float("inf"),
            "batches": int(v.size)}


def run_cell(family_name, kind, threshold, max_steps, batches, paths, seed):
    family = REGISTRY[family_name]
    kit = FAMILY_KITS[family_name]
    det = Detector(kind, threshold)
    out = {"rb_score": {}, "rb_map": {}, "historical_route_a": {}}

    # --- Candidate A -------------------------------------------------------
    means = {m: [] for m in M_GRID}
    last = None
    t0 = time.process_time()
    for b in range(batches):
        rng = np.random.Generator(np.random.PCG64([seed, b]))
        vals, unstopped, _ = rb_score_batch(
            family=family, kit=kit, detector_kind=kind, threshold=threshold,
            m_grid=M_GRID, n_paths=paths, rng=rng, max_steps=max_steps,
            new_state=det.new_state, step_fn=det.step,
        )
        for m in M_GRID:
            means[m].append(float(vals[m].mean()))
        last = vals
    cpu_a = time.process_time() - t0
    for m in M_GRID:
        out["rb_score"][str(m)] = summarise(means[m]) | tail_diagnostics(last[m])
    out["rb_score_cpu_seconds"] = cpu_a
    out["rb_score_paths"] = batches * paths

    # --- historical Route A, same paths, for the tail comparison ----------
    t0 = time.process_time()
    (run_,) = simulate_group(
        family=family, detector=det, e_values=(0.0,), n_paths=paths,
        seed=seed, batch=0, m_max=max(M_GRID), mode="compact", max_steps=max_steps,
    )
    cpu_h = time.process_time() - t0
    for m in M_GRID:
        out["historical_route_a"][str(m)] = tail_diagnostics(
            run_.window_mean(m) * run_.score_sum
        )
    out["historical_route_a_cpu_seconds"] = cpu_h
    out["historical_route_a_paths"] = paths

    # --- Candidate B -------------------------------------------------------
    b_means = {m: [] for m in M_GRID}
    b_last = None
    t0 = time.process_time()
    for b in range(max(2, batches // 2)):
        vals = rb_map_derivative_batch(
            fd_steps=FD_STEPS, m_grid=M_GRID, family=family, kit=kit,
            detector_kind=kind, threshold=threshold, n_paths=paths,
            seed=seed + 1, batch=b, max_steps=max_steps,
            new_state=det.new_state, step_fn=det.step,
            stream_counter=stream_counter,
        )
        for m in M_GRID:
            b_means[m].append(float(vals[m].mean()))
        b_last = vals
    cpu_b = time.process_time() - t0
    for m in M_GRID:
        out["rb_map"][str(m)] = summarise(b_means[m]) | tail_diagnostics(b_last[m])
    out["rb_map_cpu_seconds"] = cpu_b
    out["rb_map_paths"] = max(2, batches // 2) * paths
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(NS / "micropilots" / "diagnostics"
                                         / "micropilot.json"))
    ap.add_argument("--batches", type=int, default=8)
    ap.add_argument("--paths", type=int, default=40_000)
    ap.add_argument("--seed", type=int, default=4_090_001)
    args = ap.parse_args()

    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        if os.environ.get(var) != "1":
            print(f"refusing to run: {var} must be 1 (single-thread rule)",
                  file=sys.stderr)
            return 2

    doc = {
        "schema": "rebaseguard.p4z-micropilot-diagnostic.v1",
        "result_bearing": False,
        "purpose": "falsify candidate estimators; NOT a scientific certificate",
        "binding_on_any_verdict": False,
        "frozen_inputs_unchanged": {
            "fd_steps": list(FD_STEPS), "m_grid": list(M_GRID),
            "r_star": R_STAR, "relative_gate": 0.03, "z_gate": 4.0,
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "threads": 1,
        },
        "seed": args.seed,
        "batches": args.batches,
        "paths_per_batch": args.paths,
        "cells": [],
    }
    total_cpu = 0.0
    for label, fam, kind, thr, max_steps, regime in CELLS:
        res = run_cell(fam, kind, thr, max_steps, args.batches, args.paths,
                       args.seed)
        cpu = (res["rb_score_cpu_seconds"] + res["rb_map_cpu_seconds"]
               + res["historical_route_a_cpu_seconds"])
        total_cpu += cpu
        doc["cells"].append({
            "label": label, "family": fam,
            "detector": f"{kind}@{thr:g}", "regime": regime,
            "cell_cpu_seconds": cpu, **res,
        })
        print(f"{label:15s} {fam:9s} {kind}@{thr:g}  {cpu:6.1f} CPU-s")
    doc["total_cpu_seconds"] = total_cpu
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"\ntotal {total_cpu:.1f} CPU-s -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
