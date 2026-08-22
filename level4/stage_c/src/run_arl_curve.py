#!/usr/bin/env python
"""Stage C step 1 — estimate and persist the conditional cycle-length curve A(e)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np

from arl_curve import ACurve, default_grid, estimate_A
from campaign import RESULTS, config_hash
from rebaseguard_level4 import provenance


def main(argv: list[str]) -> int:
    n_paths = int(argv[1]) if len(argv) > 1 else 200_000
    fine_step = float(argv[2]) if len(argv) > 2 else 0.02
    master_seed = 20260821
    grid = default_grid(fine_step=fine_step)
    key = {"n_paths": n_paths, "fine_step": fine_step, "seed": master_seed,
           "n_grid": int(grid.size)}
    tag = "" if fine_step == 0.02 else f"_step{fine_step:g}"
    out = RESULTS / f"arl_curve{tag}.json"
    if out.exists():
        cached = json.loads(out.read_text())
        if cached.get("config_hash") == config_hash(key):
            print(f"[cached] {out}")
            return 0

    print(f"A(e): {grid.size} grid points, {n_paths} paths each, "
          f"fine step {fine_step}", flush=True)
    t0 = time.time()
    result = estimate_A(grid, n_paths=n_paths, master_seed=master_seed)
    curve = ACurve.from_records(result["records"])
    result.update({
        "config_hash": config_hash(key), "key": key,
        "seconds": time.time() - t0,
        "symmetry": curve.symmetry_diagnostics(),
        "monotonicity": curve.monotonicity_diagnostics(),
        "manifest": provenance.build_manifest(
            gate="stage-c", stage="arl_curve", config=key),
    })
    RESULTS.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, default=float))

    sym, mono = result["symmetry"], result["monotonicity"]
    print(f"  A(0)   = {curve(np.array([0.0]))[0]:.3f}")
    print(f"  A(1)   = {curve(np.array([1.0]))[0]:.3f}")
    print(f"  symmetry: {sym['n_pairs']} pairs, max |z| = {sym['max_abs_z']:.2f}, "
          f"mean z = {sym['mean_z']:.3f}")
    print(f"  monotone decreasing in |e|: {mono['monotone_decreasing_in_abs_e']} "
          f"({mono['n_increasing']}/{mono['n_intervals']} intervals increase, "
          f"{mono['n_significantly_increasing']} of them by >3 sigma)")
    for row in mono["significant_increases"][:8]:
        print(f"    increase on [{row['e_from']:.2f}, {row['e_to']:.2f}]: "
              f"dA = {row['delta_A']:+.3f} ({row['z']:.1f} sigma)")
    print(f"  wrote {out}  ({result['seconds']:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
