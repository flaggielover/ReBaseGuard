#!/usr/bin/env python3
"""Build the falsifiable cost/power model from the micro-pilot diagnostics.

Pure arithmetic on the pilot JSON.  No simulation, no new compute.  The model
is deliberately conservative and every safety factor is named.
"""
from __future__ import annotations
import json, math
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
PILOT = NS / "micropilots" / "diagnostics" / "micropilot.json"
OUT = NS / "results" / "estimator_feasibility.json"

R_STAR = 0.010823063          # frozen, forced by 1.96*sqrt(2)*r* = 0.03
TARGET_REL_SE = 0.0025        # P4Z design point, 4.3x tighter than r*
SAFETY_VARIANCE = 4.0         # x4 on variance: pilot sd is a small-sample estimate
SAFETY_CPU = 3.0              # x3 on CPU: unoptimised reference implementation
MIN_BLOCKS = 200              # so the batch SE itself is trustworthy
M_GRID = ("1", "2", "3", "5")

#: the 24 production configurations = 2 layers x 2 detectors x 6 families.
#: The pilot covers 5 of them; the rest are extrapolated by regime, which is
#: exactly what makes this model falsifiable.
REGIME_OF = {
    "gaussian": "light", "laplace": "light", "logistic": "light",
    "skewnormal4": "light", "t3": "moderate", "t1p5": "heavy",
}
LAYERS = {
    "reduced": [("cusum", 2.0), ("sr", 20.0)],
    "frozen": [("cusum", 5.0), ("sr", 520.886133602749)],
}


def main() -> int:
    pilot = json.loads(PILOT.read_text())
    paths_a = pilot["cells"][0]["rb_score_paths"]
    paths_b = pilot["cells"][0]["rb_map_paths"]

    measured = {}
    for c in pilot["cells"]:
        key = f"{c['family']}/{c['detector']}"
        # worst m drives the configuration, since the four m share paths
        rel_sd_a = max(c["rb_score"][m]["per_path_sd"]
                       / abs(c["rb_score"][m]["mean"]) for m in M_GRID)
        rel_sd_b = max(c["rb_map"][m]["relative_se"] * math.sqrt(paths_b)
                       for m in M_GRID)
        hist_rel_sd = max(c["historical_route_a"][m]["per_path_sd"]
                          / abs(c["rb_score"][m]["mean"]) for m in M_GRID)
        measured[key] = {
            "family": c["family"], "detector": c["detector"],
            "regime": c["regime"],
            "rb_score_relative_sd_per_path": rel_sd_a,
            "rb_map_relative_sd_per_path": rel_sd_b,
            "historical_route_a_relative_sd_per_path": hist_rel_sd,
            "variance_reduction_factor_route_a": (hist_rel_sd / rel_sd_a) ** 2,
            "rb_score_cpu_seconds_per_million_paths":
                c["rb_score_cpu_seconds"] / (c["rb_score_paths"] / 1e6),
            "rb_map_cpu_seconds_per_million_paths":
                c["rb_map_cpu_seconds"] / (c["rb_map_paths"] / 1e6),
            "worst_top1_share_rb_score": max(
                c["rb_score"][m]["top1_share_of_squared_deviation"]
                for m in M_GRID),
            "worst_top1_share_historical": max(
                c["historical_route_a"][m]["top1_share_of_squared_deviation"]
                for m in M_GRID),
            "worst_hill_rb_score": min(
                c["rb_score"][m]["hill_index_upper_half_percent"]
                for m in M_GRID),
        }

    # regime envelopes: the worst pilot cell in each regime, no interpolation
    envelope = {}
    for regime in ("light", "moderate", "heavy"):
        rows = [v for v in measured.values() if v["regime"] in
                ({"light": {"control"}, "moderate": {"moderate"},
                  "heavy": {"heavy"}}[regime])]
        if not rows:
            continue
        envelope[regime] = {
            "rb_score_relative_sd_per_path":
                max(r["rb_score_relative_sd_per_path"] for r in rows),
            "rb_map_relative_sd_per_path":
                max(r["rb_map_relative_sd_per_path"] for r in rows),
            "rb_score_cpu_seconds_per_million_paths":
                max(r["rb_score_cpu_seconds_per_million_paths"] for r in rows),
            "rb_map_cpu_seconds_per_million_paths":
                max(r["rb_map_cpu_seconds_per_million_paths"] for r in rows),
            "source_cells": [r["family"] + "/" + r["detector"] for r in rows],
        }
    # the pilot has no 'light' row other than the gaussian control, and no
    # skewnormal4 row at all; both are covered by the light envelope and that
    # extrapolation is recorded as a named risk, not hidden.
    envelope["light"] = envelope.get("light") or {}

    plan, total_cpu_a, total_cpu_b = [], 0.0, 0.0
    for layer, dets in LAYERS.items():
        for kind, thr in dets:
            for fam, regime in REGIME_OF.items():
                env = envelope[regime]
                n_a = math.ceil(SAFETY_VARIANCE
                                * (env["rb_score_relative_sd_per_path"]
                                   / TARGET_REL_SE) ** 2)
                n_b = math.ceil(SAFETY_VARIANCE
                                * (env["rb_map_relative_sd_per_path"]
                                   / TARGET_REL_SE) ** 2)
                block = math.ceil(max(n_a, n_b) / MIN_BLOCKS)
                n_a = block * MIN_BLOCKS
                n_b = block * MIN_BLOCKS
                cpu_a = (SAFETY_CPU * n_a / 1e6
                         * env["rb_score_cpu_seconds_per_million_paths"])
                cpu_b = (SAFETY_CPU * n_b / 1e6
                         * env["rb_map_cpu_seconds_per_million_paths"])
                total_cpu_a += cpu_a
                total_cpu_b += cpu_b
                plan.append({
                    "configuration": f"{layer}/{kind}@{thr:g}/{fam}",
                    "regime": regime,
                    "from_pilot": f"{fam}/{kind}@{thr:g}" in measured,
                    "block_paths": block, "blocks": MIN_BLOCKS,
                    "route_a_paths": n_a, "route_b_paths": n_b,
                    "route_a_cpu_seconds": cpu_a,
                    "route_b_cpu_seconds": cpu_b,
                    "projected_relative_se": TARGET_REL_SE,
                })

    doc = {
        "schema": "rebaseguard.p4z-estimator-feasibility.v1",
        "result_bearing": False,
        "purpose": "falsifiable cost/power model for the P4Z successor campaign",
        "frozen_unchanged": {
            "relative_gate": 0.03, "z_gate": 4.0, "r_star": R_STAR,
            "fd_steps": [0.05, 0.025], "m_grid": [1, 2, 3, 5],
            "note": "no scientific threshold is altered by P4Z",
        },
        "design": {
            "target_relative_se_per_route": TARGET_REL_SE,
            "target_is_tighter_than_r_star_by": R_STAR / TARGET_REL_SE,
            "safety_factor_on_variance": SAFETY_VARIANCE,
            "safety_factor_on_cpu": SAFETY_CPU,
            "minimum_blocks_per_route": MIN_BLOCKS,
            "minimum_blocks_rationale":
                "P4X's 8 unadjudicable cells and P4Y Pilot-4's negative result "
                "both trace to a batch standard error estimated from too few "
                "blocks of a badly concentrated law.  200 blocks makes the SE "
                "itself a trustworthy statistic once the summand has finite "
                "variance, which is what the RB construction supplies.",
        },
        "pilot_source": str(PILOT.relative_to(NS.parent.parent.parent)),
        "measured_cells": measured,
        "regime_envelopes": envelope,
        "extrapolation_risk": {
            "configurations_covered_by_pilot":
                sum(1 for p in plan if p["from_pilot"]),
            "configurations_total": len(plan),
            "families_never_piloted": ["laplace", "logistic", "skewnormal4"],
            "note": "laplace, logistic and skewnormal4 are all light-tailed with "
                    "bounded or near-linear score; they are placed on the "
                    "gaussian envelope.  skewnormal4 is additionally asymmetric, "
                    "so its cost is plausible but its analytic partial mean is "
                    "the least exercised part of the contract.  Stage 0 of the "
                    "campaign must pilot it before the budget is committed.",
        },
        "plan": plan,
        "totals": {
            "route_a_cpu_hours": total_cpu_a / 3600.0,
            "route_b_cpu_hours": total_cpu_b / 3600.0,
            "total_cpu_hours": (total_cpu_a + total_cpu_b) / 3600.0,
            "historical_p4x_total_cpu_hours": 24.7493,
            "historical_p4x_worst_configuration_cpu_hours": 18.5994,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"route A {total_cpu_a/3600:8.4f} CPU-h")
    print(f"route B {total_cpu_b/3600:8.4f} CPU-h")
    print(f"TOTAL   {(total_cpu_a+total_cpu_b)/3600:8.4f} CPU-h "
          f"(P4X spent 24.7493)")
    print(f"-> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
