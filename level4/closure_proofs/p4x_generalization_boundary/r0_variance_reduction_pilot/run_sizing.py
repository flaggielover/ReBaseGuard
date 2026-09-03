#!/usr/bin/env python3
"""R0 sizing pass: measure per-batch cost before spending any pilot budget.

Reads the frozen Priority-4 simulator read-only.  Writes nothing but its own
results file.  This exists so that the 4 CPU-hour pilot cap is respected by
construction rather than by hope.
"""

from __future__ import annotations

import json
import resource
import sys
import time
from pathlib import Path

import numpy as np

PILOT = Path(__file__).resolve().parent
P4 = PILOT.parents[1] / "p4_theory_generalization"
sys.path.insert(0, str(P4 / "src"))

from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402
from rebaseguard_p4_general.simulate import simulate_group  # noqa: E402

#: The four cost-driving configurations named by the feasibility audit's
#: DRAFT_SUCCESSOR_SCOPE.md section 8 (R0).
CONFIGS = (
    ("frozen", "sr", 520.886133602749, "t1p5", 200_000),
    ("frozen", "cusum", 5.0, "t1p5", 200_000),
    ("reduced", "sr", 20.0, "t1p5", 60_000),
    ("frozen", "sr", 520.886133602749, "skewnormal4", 200_000),
)

SIZING_PATHS = 4_000
SIZING_SEED = 4110001


def cpu_seconds() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def main() -> None:
    rows = []
    for layer, kind, threshold, family_name, max_steps in CONFIGS:
        detector = Detector(kind, threshold)
        family = REGISTRY[family_name]
        label = f"{layer}/{detector.label}/{family_name}"

        t0, c0 = time.perf_counter(), cpu_seconds()
        plus, minus = simulate_group(
            family=family, detector=detector, e_values=(0.05, -0.05),
            n_paths=SIZING_PATHS, seed=SIZING_SEED, batch=0, m_max=5,
            mode="aligned", max_steps=max_steps,
        )
        wall, cpu = time.perf_counter() - t0, cpu_seconds() - c0

        tau = plus.tau
        # Aligned mode redraws the FULL n_paths vector at every step until the
        # last path in the batch stops, so the batch cost is n_paths * max(tau)
        # while the useful work is only sum(tau).  The ratio is the straggler
        # overhead.
        useful = float(tau.sum())
        drawn = float(SIZING_PATHS * plus.max_steps_used)
        rows.append({
            "config": label,
            "layer": layer, "detector": detector.label,
            "family": family_name, "max_steps": max_steps,
            "sizing_paths": SIZING_PATHS,
            "wall_seconds": wall,
            "cpu_seconds": cpu,
            "seconds_per_path": wall / SIZING_PATHS,
            "seconds_per_1e6_paths": wall / SIZING_PATHS * 1e6,
            "mean_tau": float(tau.mean()),
            "median_tau": float(np.median(tau)),
            "p99_tau": float(np.percentile(tau, 99)),
            "max_tau": int(tau.max()),
            "steps_executed": int(plus.max_steps_used),
            "unstopped": int(plus.unstopped),
            "innovations_useful": useful,
            "innovations_drawn": drawn,
            "straggler_overhead_factor": drawn / useful,
        })
        print(f"{label:44s} wall={wall:7.3f}s  mean_tau={tau.mean():8.2f}  "
              f"max_tau={tau.max():7d}  straggler={drawn/useful:8.1f}x  "
              f"s/1e6paths={wall / SIZING_PATHS * 1e6:9.1f}")

    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 20)
    payload = {
        "schema": "rebaseguard.p4x-r0-sizing.v1",
        "purpose": "pre-pilot cost sizing; not a scientific result",
        "sizing_paths": SIZING_PATHS,
        "sizing_seed": SIZING_SEED,
        "peak_rss_mb": peak_mb,
        "rows": rows,
    }
    out = PILOT / "results" / "sizing.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\npeak RSS {peak_mb:.1f} MB -> {out}")


if __name__ == "__main__":
    main()
