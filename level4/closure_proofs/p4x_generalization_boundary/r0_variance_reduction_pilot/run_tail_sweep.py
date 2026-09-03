#!/usr/bin/env python3
"""Tail-index sweep over every theorem-supported family and both frozen detectors.

The precision policy needs a convergence exponent per cell.  That exponent is a
property of the estimator's per-path summand, not of whether a cell passed, so
it is measured here once and frozen into the policy.

For a summand with tail index ``alpha``:
    alpha >= 2  ->  finite variance, sample means converge at n^{-1/2}
    alpha <  2  ->  infinite variance, sample means converge at n^{1/alpha - 1}

Both routes are measured, because both must reach the target precision.
"""

from __future__ import annotations

import json
import resource
import sys
import time
from pathlib import Path

import numpy as np

PILOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PILOT / "src"))
P4 = PILOT.parents[1] / "p4_theory_generalization"
sys.path.insert(0, str(P4 / "src"))

from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402
from rebaseguard_p4_general.simulate import simulate_group  # noqa: E402
from r0_methods import hill_tail_index  # noqa: E402

FAMILIES = ("gaussian", "laplace", "logistic", "skewnormal4", "t1p5", "t3")
LAYERS = {
    "frozen": (("sr", 520.886133602749), ("cusum", 5.0)),
    "reduced": (("sr", 20.0), ("cusum", 2.0)),
}
MAX_STEPS = {"frozen": 200_000, "reduced": 60_000}
PATHS = {"frozen": 60_000, "reduced": 150_000}
SEED = 4112001
H = 0.05


def cpu_seconds() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def main() -> None:
    c0 = cpu_seconds()
    rows = []
    for layer, detectors in LAYERS.items():
        for kind, threshold in detectors:
            detector = Detector(kind, threshold)
            for name in FAMILIES:
                family = REGISTRY[name]
                paths = PATHS[layer]
                t0 = time.perf_counter()

                # Route B: per-path central-difference contribution at m = 1
                plus, minus = simulate_group(
                    family=family, detector=detector, e_values=(H, -H),
                    n_paths=paths, seed=SEED, batch=0, m_max=1,
                    mode="aligned", max_steps=MAX_STEPS[layer],
                )
                contrib_b = -((plus.window_mean(1) - minus.window_mean(1))
                              / (2.0 * H))

                # Route A: per-path score contribution at m = 1
                (run,) = simulate_group(
                    family=family, detector=detector, e_values=(0.0,),
                    n_paths=paths, seed=SEED + 1, batch=0, m_max=1,
                    mode="compact", max_steps=MAX_STEPS[layer],
                )
                contrib_a = run.window_mean(1) * run.score_sum

                wall = time.perf_counter() - t0
                tail_b = hill_tail_index(contrib_b - 1.0)
                tail_a = hill_tail_index(contrib_a - float(contrib_a.mean()))
                rows.append({
                    "layer": layer, "detector": detector.label, "family": name,
                    "paths": paths, "wall_seconds": wall,
                    "mean_tau": float(run.tau.mean()),
                    "route_b": {
                        "tail": tail_b,
                        "coupled_fraction": float(np.isclose(contrib_b, 1.0).mean()),
                        "mean": float(contrib_b.mean()),
                    },
                    "route_a": {
                        "tail": tail_a,
                        "mean": float(contrib_a.mean()),
                    },
                })
                print(f"{layer:8s} {detector.label:14s} {name:12s} "
                      f"alphaB={tail_b['alpha']:7.3f} alphaA={tail_a['alpha']:7.3f} "
                      f"coupled={rows[-1]['route_b']['coupled_fraction']:.4f} "
                      f"tau={rows[-1]['mean_tau']:7.1f} wall={wall:6.1f}s")

    cpu = cpu_seconds() - c0
    payload = {
        "schema": "rebaseguard.p4x-r0-tailsweep.v1",
        "classification": "PRE_FREEZE_COST_AND_PRECISION_PILOT",
        "binding": False,
        "fd_step": H, "seed": SEED,
        "cpu_seconds": cpu,
        "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 20),
        "rule": ("convergence exponent kappa = 0.5 when alpha >= 2, "
                 "else kappa = 1 - 1/alpha"),
        "rows": rows,
    }
    out = PILOT / "results" / "tail_sweep.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nCPU {cpu:.1f}s -> {out}")


if __name__ == "__main__":
    main()
