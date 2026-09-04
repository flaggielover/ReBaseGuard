#!/usr/bin/env python3
"""Stage 0 of the pilot: fix r*_pilot for each cell.

Runs ONLY in the ``calibration`` seed namespace, which no rule and no
replicate ever touches again.  Its single output is a frozen per-cell target

    r*_pilot(cell) = relSE_true(cell, B1_NOMINAL blocks)
                   = sigma_block / (sqrt(B1_NOMINAL) * |mu|)   at the worst m

so that the NOMINAL one-shot rule lands exactly on the target and the pilot
measures the realised-attainment question rather than a mis-sized allocation.

This is a scale choice, not a scientific threshold.  r* = 0.010823 is
untouched and is what P4Y production would use; the pilot simply reproduces
the same dimensionless situation at an affordable block count.
"""

from __future__ import annotations

import json
import math
import resource
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from p4y_pilot.blocks import M_GRID, block_value, derive_seed, summarise  # noqa: E402
from p4y_pilot.config import (  # noqa: E402
    B1_NOMINAL, CALIBRATION_BLOCKS, PILOT_CELLS, R_STAR_PRODUCTION, kappa_for,
)
from p4y_pilot.stats import hill_alpha  # noqa: E402


def cpu() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def main() -> int:
    out = {"schema": "rebaseguard.p4y-pilot-calibration.v1",
           "binding": False,
           "r_star_production": R_STAR_PRODUCTION,
           "b1_nominal": B1_NOMINAL,
           "calibration_blocks": CALIBRATION_BLOCKS,
           "namespace": "calibration",
           "cells": []}
    t0, c0 = time.perf_counter(), cpu()
    for cell in PILOT_CELLS:
        seed = derive_seed(cell.key, "calibration", 0)
        cc = cpu()
        values = [block_value(cell, seed, i) for i in range(CALIBRATION_BLOCKS)]
        cell_cpu = cpu() - cc
        per_m = {}
        for m in M_GRID:
            xs = [v[m] for v in values]
            s = summarise(xs)
            # relSE_true at B1 blocks: the block SD is a property of the block
            # size, so the B1-block relative SE is sd / (sqrt(B1) * |mean|).
            per_m[m] = {
                "mean": s["mean"], "block_sd": s["sd"],
                "rel_se_at_b1": s["sd"] / (math.sqrt(B1_NOMINAL) * abs(s["mean"])),
                "rel_se_calibration": s["relative_se"],
                "hill_alpha_block_means": hill_alpha(xs),
            }
        worst_m = max(M_GRID, key=lambda m: per_m[m]["rel_se_at_b1"])
        raw = per_m[worst_m]["rel_se_at_b1"]
        # Frozen to four significant figures so the target is a declared
        # constant rather than a trailing-digit artefact of the calibration.
        r_star_pilot = float(f"{raw:.4g}")
        out["cells"].append({
            "cell": cell.key, "config": cell.config, "route": cell.route,
            "block_size": cell.block_size, "heavy": cell.heavy,
            "kappa": kappa_for(cell),
            "worst_m": worst_m,
            "r_star_pilot": r_star_pilot,
            "r_star_pilot_raw": raw,
            "by_m": {str(m): per_m[m] for m in M_GRID},
            "calibration_cpu_seconds": cell_cpu,
            "calibration_paths": CALIBRATION_BLOCKS * cell.block_size,
        })
        print(f"{cell.key} {cell.config:28s} {cell.route}  "
              f"worst m={worst_m}  r*_pilot={r_star_pilot:.4g}  "
              f"block_sd={per_m[worst_m]['block_sd']:.4g}  "
              f"mean={per_m[worst_m]['mean']:.5f}  "
              f"hill_alpha(block means)={per_m[worst_m]['hill_alpha_block_means']:.2f}  "
              f"[{cell_cpu:.1f} CPU-s]", flush=True)
    out["total_cpu_seconds"] = cpu() - c0
    out["total_wall_seconds"] = time.perf_counter() - t0
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "calibration.json").write_text(json.dumps(out, indent=1))
    print(f"\ncalibration CPU = {out['total_cpu_seconds']:.1f} s "
          f"({out['total_cpu_seconds']/3600:.4f} CPU-hours)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
