#!/usr/bin/env python3
"""Derive the P4X precision policy and project production cost.

The policy is a RULE, not a threshold.  It maps a desired statistical precision
to a required sample size and CPU cost, using only:

  * the frozen 3% accuracy criterion (unchanged, inherited from Track 3);
  * the measured tail index of each estimator's per-path summand;
  * measured CPU per path.

It never consults whether a historical cell passed or failed.  Feeding it the
observed discrepancies would change nothing: they are not among its inputs.
"""

from __future__ import annotations

import json
import math
import resource
import sys
import time
from pathlib import Path

PILOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PILOT / "src"))
P4 = PILOT.parents[1] / "p4_theory_generalization"
sys.path.insert(0, str(P4 / "src"))

from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402
from rebaseguard_p4_general.simulate import simulate_group  # noqa: E402

FROZEN_ACCURACY = 0.03      # inherited unchanged from Track 3, never altered
ATTAINMENT_Z = 1.96         # 95% attainment when the two routes truly agree
#: r* solves  ATTAINMENT_Z * sqrt(2) * r* = FROZEN_ACCURACY
TARGET_REL_SE = FROZEN_ACCURACY / (ATTAINMENT_Z * math.sqrt(2.0))

CAL_PATHS = {"frozen": 40_000, "reduced": 100_000}
MAX_STEPS = {"frozen": 200_000, "reduced": 60_000}
CAL_SEED = 4113001


def cpu_seconds() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def calibrate_cost() -> dict:
    """Seconds per 1e6 paths, per route, for all 24 (layer, detector, family)."""
    layers = {
        "frozen": (("sr", 520.886133602749), ("cusum", 5.0)),
        "reduced": (("sr", 20.0), ("cusum", 2.0)),
    }
    out = {}
    for layer, dets in layers.items():
        for kind, threshold in dets:
            detector = Detector(kind, threshold)
            for name in ("gaussian", "laplace", "logistic", "skewnormal4",
                         "t1p5", "t3"):
                family = REGISTRY[name]
                n = CAL_PATHS[layer]
                # Route B costs two aligned runs, one per finite-difference step
                t0 = time.perf_counter()
                for step in (0.05, 0.025):
                    simulate_group(
                        family=family, detector=detector,
                        e_values=(step, -step), n_paths=n, seed=CAL_SEED,
                        batch=0, m_max=5, mode="aligned",
                        max_steps=MAX_STEPS[layer],
                    )
                b_wall = time.perf_counter() - t0
                t0 = time.perf_counter()
                simulate_group(
                    family=family, detector=detector, e_values=(0.0,),
                    n_paths=n, seed=CAL_SEED + 1, batch=0, m_max=5,
                    mode="compact", max_steps=MAX_STEPS[layer],
                )
                a_wall = time.perf_counter() - t0
                out[f"{layer}/{detector.label}/{name}"] = {
                    "calibration_paths": n,
                    "route_b_seconds_per_1e6": b_wall / n * 1e6,
                    "route_a_seconds_per_1e6": a_wall / n * 1e6,
                }
                print(f"  cost {layer:8s} {detector.label:14s} {name:12s} "
                      f"B={b_wall / n * 1e6:8.1f}  A={a_wall / n * 1e6:8.1f} s/1e6")
    return out


def main() -> None:
    c0 = cpu_seconds()
    corr = json.loads((P4 / "results" / "correspondence.json").read_text())
    tails = json.loads((PILOT / "results" / "tail_sweep.json").read_text())
    pilot = json.loads((PILOT / "results" / "pilot.json").read_text())

    alpha = {}
    for row in tails["rows"]:
        key = f"{row['layer']}/{row['detector']}/{row['family']}"
        alpha[key] = {"route_a": row["route_a"]["tail"]["alpha"],
                      "route_b": row["route_b"]["tail"]["alpha"]}

    cache = PILOT / "results" / "cost_calibration.json"
    if cache.exists():
        print("cost calibration: reusing cached measurement")
        cost = json.loads(cache.read_text())["cost"]
    else:
        print("cost calibration:")
        cost = calibrate_cost()
        cache.write_text(json.dumps(
            {"schema": "rebaseguard.p4x-r0-cost.v1",
             "calibration_paths": CAL_PATHS, "seed": CAL_SEED,
             "cost": cost}, indent=2) + "\n")

    def kappa_classical() -> float:
        """The classical rate, supported by the last rung of every pilot ladder."""
        return 0.5

    def kappa_stable(a: float) -> float:
        """The stable-law rate for an infinite-variance summand."""
        return 0.5 if a >= 2.0 else 1.0 - 1.0 / a

    # A fresh, independently seeded pilot measurement of the reference relative
    # SE exists for the four cost-driving configurations.  Where it exists it is
    # the optimistic reference; the frozen campaign's own value is always the
    # pessimistic one.  The gap between them at an IDENTICAL design is itself
    # the measurement of how unreliable a heavy-tailed standard error is.
    pilot_rel_se: dict[tuple[str, int], float] = {}
    pilot_paths: dict[str, int] = {}
    for cfg_name, res in pilot["results"].items():
        base = res["methods"]["baseline_h0.05"]
        pilot_paths[cfg_name] = base["total_paths"]
        for m_str, s in base["by_m"].items():
            pilot_rel_se[(cfg_name, int(m_str))] = abs(s["relative_se"])

    def project(paths_ref: float, rel_ref: float, k: float, sec: float) -> dict:
        factor = (rel_ref / TARGET_REL_SE) ** (1.0 / k) if rel_ref > TARGET_REL_SE else 1.0
        n_req = paths_ref * factor
        return {"kappa": k, "reference_relative_se": rel_ref,
                "reference_paths": paths_ref, "path_multiplier": factor,
                "required_paths": n_req,
                "cpu_seconds": n_req / 1e6 * sec,
                "cpu_hours": n_req / 1e6 * sec / 3600.0}

    cells = []
    for cell in corr["monte_carlo"]["cells"]:
        if cell["family_class"] != "THEOREM-SUPPORTED":
            continue
        key = f"{cell['layer']}/{cell['detector']}/{cell['family']}"
        row = {"layer": cell["layer"], "detector": cell["detector"],
               "family": cell["family"], "m": cell["m"], "config": key,
               "alpha": alpha[key]}
        for route in ("route_a", "route_b"):
            est = cell[route]
            hist_rel = abs(est["se"] / est["mean"]) if est["mean"] else math.inf
            a = alpha[key][route]
            sec = cost[key][f"{route}_seconds_per_1e6"]

            fresh = pilot_rel_se.get((key, cell["m"])) if route == "route_b" else None
            optimistic_rel = fresh if fresh is not None else hist_rel
            optimistic_paths = (pilot_paths[key] if fresh is not None
                                else est["paths"])
            pessimistic_rel = hist_rel

            row[route] = {
                "historical_paths": est["paths"],
                "historical_relative_se": hist_rel,
                "pilot_relative_se": fresh,
                "alpha": a,
                "already_meets_target": hist_rel <= TARGET_REL_SE,
                # tier 1: fresh reference, classical rate
                "median": project(optimistic_paths, optimistic_rel,
                                  kappa_classical(), sec),
                # tier 2: frozen campaign's own reference, classical rate
                "conservative": project(est["paths"], pessimistic_rel,
                                        kappa_classical(), sec),
                # tier 3: frozen campaign's reference, stable-law rate
                "worst_case": project(est["paths"], pessimistic_rel,
                                      kappa_stable(a), sec),
            }
        cells.append(row)

    # A configuration's four windows SHARE their paths, so cost is charged once
    # per (layer, detector, family, route) at the worst window.
    per_config: dict[str, dict] = {}
    for row in cells:
        cfg = per_config.setdefault(row["config"], {"config": row["config"]})
        for route in ("route_a", "route_b"):
            for mode in ("median", "conservative", "worst_case"):
                k = f"{route}_{mode}_cpu_hours"
                cfg[k] = max(cfg.get(k, 0.0), row[route][mode]["cpu_hours"])

    totals = {}
    for mode in ("median", "conservative", "worst_case"):
        totals[mode] = sum(
            c[f"route_a_{mode}_cpu_hours"] + c[f"route_b_{mode}_cpu_hours"]
            for c in per_config.values())

    PER_CONFIG_ALLOWANCE_HOURS = 20.0
    precision_limited = []
    for cfg_key, cfg in per_config.items():
        for route in ("route_a", "route_b"):
            hours = cfg[f"{route}_worst_case_cpu_hours"]
            if hours > PER_CONFIG_ALLOWANCE_HOURS:
                precision_limited.append({
                    "config": cfg_key, "route": route,
                    "worst_case_cpu_hours": hours,
                    "conservative_cpu_hours": cfg[f"{route}_conservative_cpu_hours"],
                    "median_cpu_hours": cfg[f"{route}_median_cpu_hours"],
                })

    cpu = cpu_seconds() - c0
    payload = {
        "schema": "rebaseguard.p4x-r0-policy.v1",
        "classification": "PRE_FREEZE_COST_AND_PRECISION_PILOT",
        "binding": False,
        "policy": {
            "name": "estimator-precision policy",
            "frozen_accuracy_criterion": FROZEN_ACCURACY,
            "frozen_accuracy_source": (
                "inherited unchanged from Track 3 via the frozen Priority-4 "
                "protocol; this policy does not alter it"),
            "attainment_z": ATTAINMENT_Z,
            "target_relative_se_per_route": TARGET_REL_SE,
            "target_derivation": (
                "r* solves 1.96 * sqrt(2) * r* = 0.03, i.e. the frozen 3% "
                "accuracy criterion is attained with 95% probability when the "
                "two routes genuinely agree.  r* is therefore FORCED by the "
                "frozen criterion, not chosen"),
            "rule": (
                "N_required = N_reference * (relSE_reference / r*)^(1/kappa), "
                "kappa = 0.5 when the estimator's per-path tail index alpha "
                ">= 2, else kappa = 1 - 1/alpha"),
            "inputs": ["frozen accuracy criterion", "measured tail index",
                       "measured reference relative SE", "measured CPU per path"],
            "explicitly_not_inputs": [
                "whether a historical cell passed or failed",
                "the observed Route-A minus Route-B discrepancy",
                "the sign or direction of any disagreement",
            ],
            "arbitration_clause": (
                "a (configuration, route) whose projected worst-case cost "
                "exceeds the per-configuration allowance is declared "
                "PRECISION_LIMITED and arbitrated by Route Q, which has no "
                "sampling error.  The declaration is made from projected cost "
                "alone, before the production estimate exists"),
        },
        "measured_alpha": alpha,
        "cost_calibration_seconds_per_1e6_paths": cost,
        "tier_definitions": {
            "median": ("fresh independently seeded pilot reference relative SE "
                       "where one exists, classical n^{-1/2} rate -- the rate "
                       "the last rung of every pilot ladder supports"),
            "conservative": ("the frozen campaign's own reference relative SE, "
                             "classical rate"),
            "worst_case": ("the frozen campaign's own reference relative SE, "
                           "stable-law rate 1 - 1/alpha -- applies only where "
                           "alpha < 2, i.e. only to t1p5"),
        },
        "per_configuration_allowance_hours": PER_CONFIG_ALLOWANCE_HOURS,
        "cells": cells,
        "per_configuration_cpu_hours": per_config,
        "totals_cpu_hours": totals,
        "precision_limited_candidates": precision_limited,
        "policy_cpu_seconds": cpu,
        "pilot_cpu_seconds_reference": pilot["cpu_used_seconds"],
    }
    out = PILOT / "results" / "precision_policy.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"\ntarget relative SE per route r* = {TARGET_REL_SE:.5f} "
          f"(forced by the frozen {FROZEN_ACCURACY} criterion)")
    print(f"projected production CPU (median)       = {totals['median']:10.2f} h")
    print(f"projected production CPU (conservative) = {totals['conservative']:10.2f} h")
    print(f"projected production CPU (worst case)   = {totals['worst_case']:10.2f} h")
    print(f"per-configuration allowance = {PER_CONFIG_ALLOWANCE_HOURS} h")
    print(f"precision-limited candidates: {len(precision_limited)}")
    for r in sorted(precision_limited, key=lambda r: -r["worst_case_cpu_hours"]):
        print(f"   {r['config']:34s} {r['route']:8s} "
              f"median={r['median_cpu_hours']:8.3f}h "
              f"cons={r['conservative_cpu_hours']:9.2f}h "
              f"worst={r['worst_case_cpu_hours']:12.1f}h")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
