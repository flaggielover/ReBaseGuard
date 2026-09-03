#!/usr/bin/env python3
"""P4X R0 variance-reduction and cost-calibration pilot.

PRE_FREEZE_COST_AND_PRECISION_PILOT.  Not Checkpoint A, not a production run,
not a successor result, not closure evidence.

Hard budget: 4 CPU-hours total.  The runner tracks its own CPU consumption and
aborts rather than exceed it.
"""

from __future__ import annotations

import json
import math
import resource
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

PILOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PILOT / "src"))
P4 = PILOT.parents[1] / "p4_theory_generalization"
sys.path.insert(0, str(P4 / "src"))

from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402
from r0_methods import (  # noqa: E402
    batch_summary, g2_control, hill_tail_index, run_block,
)

CPU_BUDGET_SECONDS = 4 * 3600
M_GRID = (1, 2, 3, 5)

#: Fresh seed namespace: the frozen campaign used 401xxxx, this pilot uses
#: 411xxxx, so no pilot block can coincide with a frozen block.
SEED_BASE = 4110000

CONFIGS = {
    "frozen/sr@520.886/t1p5": dict(
        layer="frozen", kind="sr", threshold=520.886133602749,
        family="t1p5", max_steps=200_000, symmetric=True,
        hist_paths=960_000, hist_blocks=48, hist_paths_per_block=20_000,
        hist_rel_se={1: 0.23325520628624588, 2: 0.15356566571557112,
                     3: 0.11839265331118375, 5: 0.08460626359787078},
        pilot_paths_per_block=20_000, pilot_blocks=48, seed=SEED_BASE + 1,
        ladder_multipliers=(1, 4, 16, 64), ladder_blocks=32,
    ),
    "frozen/cusum@5/t1p5": dict(
        layer="frozen", kind="cusum", threshold=5.0,
        family="t1p5", max_steps=200_000, symmetric=True,
        hist_paths=960_000, hist_blocks=48, hist_paths_per_block=20_000,
        hist_rel_se={1: 0.08102337199844538, 2: 0.05763, 3: 0.04563, 5: 0.03324},
        pilot_paths_per_block=20_000, pilot_blocks=48, seed=SEED_BASE + 2,
        ladder_multipliers=(1, 4, 16, 64), ladder_blocks=32,
    ),
    "reduced/sr@20/t1p5": dict(
        layer="reduced", kind="sr", threshold=20.0,
        family="t1p5", max_steps=60_000, symmetric=True,
        hist_paths=3_200_000, hist_blocks=32, hist_paths_per_block=100_000,
        hist_rel_se={1: 0.0371890653796169, 2: 0.026276690986780288,
                     3: 0.020864496710286038, 5: 0.015261881710116268},
        pilot_paths_per_block=100_000, pilot_blocks=32, seed=SEED_BASE + 3,
        ladder_multipliers=(1, 4, 16, 64), ladder_blocks=32,
    ),
    "frozen/sr@520.886/skewnormal4": dict(
        layer="frozen", kind="sr", threshold=520.886133602749,
        family="skewnormal4", max_steps=200_000, symmetric=False,
        hist_paths=960_000, hist_blocks=48, hist_paths_per_block=20_000,
        hist_rel_se={1: 0.00450, 2: 0.00412, 3: 0.00419, 5: 0.00423},
        pilot_paths_per_block=20_000, pilot_blocks=24, seed=SEED_BASE + 4,
        ladder_multipliers=(1, 2, 4, 8), ladder_blocks=16,
    ),
}

#: (name, fd_steps, method).  ``baseline`` is the frozen Route-B configuration.
METHODS = (
    ("baseline_h0.05", (0.05, 0.025), "baseline"),
    ("reflection_h0.05", (0.05, 0.025), "reflection"),
    ("coarse_h0.10", (0.10, 0.05), "baseline"),
    ("coarse_h0.20", (0.20, 0.10), "baseline"),
    ("fine_h0.025", (0.025, 0.0125), "baseline"),
)


def cpu_seconds() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


class Budget:
    def __init__(self, cap: float) -> None:
        self.cap = cap
        self.start_cpu = cpu_seconds()
        self.start_wall = time.perf_counter()

    @property
    def cpu_used(self) -> float:
        return cpu_seconds() - self.start_cpu

    @property
    def wall_used(self) -> float:
        return time.perf_counter() - self.start_wall

    def check(self, label: str) -> None:
        if self.cpu_used > self.cap:
            raise SystemExit(
                f"R0 CPU budget exhausted at {label}: "
                f"{self.cpu_used:.0f}s > {self.cap:.0f}s"
            )


def variance_ratio_ci(sd_a: float, n_a: int, sd_b: float, n_b: int,
                      conf: float = 0.95) -> tuple[float, float, float]:
    """Ratio ``var_a / var_b`` with an F-distribution confidence interval."""
    ratio = (sd_a ** 2) / (sd_b ** 2)
    lo_q, hi_q = (1 - conf) / 2, 1 - (1 - conf) / 2
    f_lo = stats.f.ppf(lo_q, n_a - 1, n_b - 1)
    f_hi = stats.f.ppf(hi_q, n_a - 1, n_b - 1)
    return ratio, ratio / f_hi, ratio / f_lo


def run_method(cfg: dict, method_name: str, fd_steps, method: str,
               budget: Budget, keep_contributions: bool = False) -> dict:
    family = REGISTRY[cfg["family"]]
    detector = Detector(cfg["kind"], cfg["threshold"])
    blocks = cfg["pilot_blocks"]
    paths = cfg["pilot_paths_per_block"]

    per_m: dict[int, list[float]] = {m: [] for m in M_GRID}
    decoupled: list[float] = []
    contributions: list[np.ndarray] = []
    drawn = 0
    t0, c0 = time.perf_counter(), cpu_seconds()

    for block in range(blocks):
        res = run_block(
            family=family, detector=detector, m_grid=M_GRID, paths=paths,
            seed=cfg["seed"], block=block, fd_steps=fd_steps,
            max_steps=cfg["max_steps"], method=method,
            keep_contributions=keep_contributions and block < 4,
        )
        for m in M_GRID:
            per_m[m].append(res.richardson[m])
        decoupled.append(res.decoupled_fraction)
        drawn += res.innovations_drawn
        if res.contributions is not None:
            contributions.append(res.contributions)
        budget.check(f"{cfg['family']}/{method_name}/block{block}")

    wall, cpu = time.perf_counter() - t0, cpu_seconds() - c0
    summary = {m: batch_summary(per_m[m]) for m in M_GRID}
    for m in M_GRID:
        s = summary[m]
        s["relative_se"] = abs(s["se"] / s["mean"]) if s["mean"] else math.inf

    out = {
        "method": method_name,
        "fd_steps": list(fd_steps),
        "estimator": method,
        "blocks": blocks,
        "paths_per_block": paths,
        "total_paths": blocks * paths,
        "innovations_drawn": drawn,
        "wall_seconds": wall,
        "cpu_seconds": cpu,
        "cpu_per_1e6_paths": cpu / (blocks * paths) * 1e6,
        "decoupled_fraction_mean": float(np.mean(decoupled)),
        "by_m": {str(m): summary[m] for m in M_GRID},
        "block_values_m1": per_m[1],
    }
    if contributions:
        pooled = np.concatenate(contributions)
        out["tail_diagnostic_m1"] = hill_tail_index(pooled - 1.0)
        out["contribution_stats_m1"] = {
            "n": int(pooled.size),
            "mean": float(pooled.mean()),
            "exactly_one_fraction": float(np.isclose(pooled, 1.0).mean()),
            "abs_max_minus_one": float(np.abs(pooled - 1.0).max()),
        }
    return out


def scaling_ladder(cfg: dict, budget: Budget) -> dict:
    """Per-block standard deviation as a function of block size.

    Finite summand variance implies ``sd ~ n^{-1/2}``.  A tail index
    ``alpha < 2`` implies the slower rate ``n^{1/alpha - 1}``.  This is the
    measurement that decides whether precision is purchasable at all.
    """
    family = REGISTRY[cfg["family"]]
    detector = Detector(cfg["kind"], cfg["threshold"])
    base = cfg["pilot_paths_per_block"]
    rungs = [base // 4 * r for r in cfg["ladder_multipliers"]]
    blocks = cfg["ladder_blocks"]
    points = []
    for paths in rungs:
        vals: list[float] = []
        t0, c0 = time.perf_counter(), cpu_seconds()
        for block in range(blocks):
            res = run_block(
                family=family, detector=detector, m_grid=(1,), paths=paths,
                seed=cfg["seed"] + 500, block=block, fd_steps=(0.05, 0.025),
                max_steps=cfg["max_steps"], method="baseline",
            )
            vals.append(res.richardson[1])
            budget.check(f"ladder/{cfg['family']}/{paths}/block{block}")
        cpu = cpu_seconds() - c0
        s = batch_summary(vals)
        points.append({
            "paths_per_block": paths, "blocks": blocks,
            "block_sd": s["block_sd"], "mean": s["mean"],
            "se": s["se"], "cpu_seconds": cpu,
            "wall_seconds": time.perf_counter() - t0,
        })
        print(f"    ladder n={paths:>8d}  block_sd={s['block_sd']:.5f}  "
              f"mean={s['mean']:.5f}  cpu={cpu:.1f}s")
    logn = np.log(np.array([p["paths_per_block"] for p in points], float))
    logs = np.log(np.array([p["block_sd"] for p in points], float))
    slope, intercept = np.polyfit(logn, logs, 1)
    resid = logs - (slope * logn + intercept)
    return {
        "points": points,
        "fitted_log_log_slope": float(slope),
        "fit_residual_rms": float(np.sqrt((resid ** 2).mean())),
        "sqrt_n_slope": -0.5,
        "interpretation": (
            "slope ~ -0.5 means the summand has finite variance and precision "
            "is purchasable at the usual n^{-1/2} rate; a slope materially "
            "above -0.5 means it is not"
        ),
    }


def main() -> None:
    budget = Budget(CPU_BUDGET_SECONDS)
    results: dict[str, dict] = {}

    for name, cfg in CONFIGS.items():
        print(f"\n=== {name} ===")
        methods: dict[str, dict] = {}
        for method_name, fd_steps, method in METHODS:
            if method == "reflection" and not cfg["symmetric"]:
                methods[method_name] = {
                    "method": method_name, "skipped": True,
                    "reason": ("reflection-antithetic requires a symmetric "
                               "family; this family is asymmetric"),
                }
                print(f"  {method_name:20s} SKIPPED (asymmetric family)")
                continue
            out = run_method(cfg, method_name, fd_steps, method, budget,
                             keep_contributions=(method_name == "baseline_h0.05"))
            methods[method_name] = out
            m1 = out["by_m"]["1"]
            print(f"  {method_name:20s} m=1 {m1['mean']:8.4f} +- {m1['se']:.4f} "
                  f"(relSE {m1['relative_se']:.4f})  cpu={out['cpu_seconds']:6.1f}s "
                  f"decoupled={out['decoupled_fraction_mean']:.4f}")

        # variance ratios against the baseline, per m, with F-based CIs
        base = methods["baseline_h0.05"]
        for method_name, out in methods.items():
            if out.get("skipped") or method_name == "baseline_h0.05":
                continue
            ratios = {}
            for m in M_GRID:
                b = base["by_m"][str(m)]
                o = out["by_m"][str(m)]
                r, lo, hi = variance_ratio_ci(
                    b["block_sd"], b["blocks"], o["block_sd"], o["blocks"])
                cpu_mult = out["cpu_seconds"] / base["cpu_seconds"]
                ratios[str(m)] = {
                    "variance_reduction_factor": r,
                    "vrf_ci95": [lo, hi],
                    "ess_multiplier": r,
                    "cpu_multiplier": cpu_mult,
                    "vrf_per_cpu": r / cpu_mult if cpu_mult else math.inf,
                    "estimate_shift_in_baseline_se": (
                        (o["mean"] - b["mean"]) / b["se"] if b["se"] else math.nan
                    ),
                }
            out["versus_baseline"] = ratios

        print("  --- scaling ladder ---")
        ladder = scaling_ladder(cfg, budget)
        print(f"    fitted log-log slope = {ladder['fitted_log_log_slope']:.4f} "
              f"(sqrt-n would be -0.5)")

        # G2 control variate probe: is there any usable variance in it?
        gmean, gvar = g2_control(
            family=REGISTRY[cfg["family"]],
            detector=Detector(cfg["kind"], cfg["threshold"]), m=1,
            paths=20_000, seed=cfg["seed"] + 900, block=0, step=0.05,
            horizon=max(2, int(round(cfg.get("horizon_hint", 8)))),
        )
        results[name] = {
            "config": cfg | {"hist_rel_se": {str(k): v for k, v
                                             in cfg["hist_rel_se"].items()}},
            "methods": methods,
            "scaling_ladder": ladder,
            "g2_control_probe": {
                "mean": gmean, "per_path_variance": gvar,
                "known_expectation": 1.0,
                "usable_as_control_variate": bool(gvar > 1e-12),
                "note": ("Corollary G2 makes the deterministic-horizon control "
                         "exactly 1 on every CRN path, so its variance is zero "
                         "and it carries no information about the stopped "
                         "estimator"),
            },
        }
        budget.check(f"after {name}")

    payload = {
        "schema": "rebaseguard.p4x-r0-pilot.v1",
        "classification": "PRE_FREEZE_COST_AND_PRECISION_PILOT",
        "binding": False,
        "checkpoint_created": False,
        "cpu_budget_seconds": CPU_BUDGET_SECONDS,
        "cpu_used_seconds": budget.cpu_used,
        "wall_used_seconds": budget.wall_used,
        "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 20),
        "seed_base": SEED_BASE,
        "m_grid": list(M_GRID),
        "methods": [m[0] for m in METHODS],
        "results": results,
    }
    out = PILOT / "results" / "pilot.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nCPU used {budget.cpu_used:.1f}s of {CPU_BUDGET_SECONDS}s "
          f"({budget.cpu_used / 3600:.3f} h); wall {budget.wall_used:.1f}s")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
