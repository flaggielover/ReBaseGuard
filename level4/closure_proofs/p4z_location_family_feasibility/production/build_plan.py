#!/usr/bin/env python3
"""Derive the authoritative campaign plan from repository state, and freeze it.

The plan is NOT taken from any prompt.  Scope, families, detectors, layers, the
m grid and every threshold come from the frozen P4 protocol; block counts and
path counts come from the frozen P4Z checkpoint and feasibility model; the
unresolved residue comes from the P4X cell ledger recorded in Phase 0.
"""
from __future__ import annotations

import json
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
P4 = NS.parent / "p4_theory_generalization"

PROTOCOL = json.loads((P4 / "configs" / "P4_PROTOCOL.json").read_text())
CHECKPOINT = json.loads((NS / "configs" / "checkpoint_p4z.json").read_text())
FEASIBILITY = json.loads((NS / "results" / "estimator_feasibility.json").read_text())

SEED_SCORE = CHECKPOINT["seed_policy"]["rb_score"]
SEED_MAP = CHECKPOINT["seed_policy"]["rb_map"]
SEED_LADDER = CHECKPOINT["seed_policy"]["fd_ladder"]
SEED_STRIDE = 100
BLOCKS = CHECKPOINT["budget"]["blocks_per_route"]
STAGE0_BLOCKS = 20
LADDER_BLOCKS = 20
LADDER_STEPS = [0.2, 0.1, 0.05, 0.025]

#: The 8 historically unadjudicated cells, from PHASE0_HISTORICAL_AUDIT.md
#: section 6, which reconstructed them from P4X's own c2_cell_ledger.json.
UNRESOLVED_CELLS = [
    ("reduced", "sr@20", "t1p5", 1), ("reduced", "sr@20", "t1p5", 2),
    ("frozen", "cusum@5", "t3", 1),
    ("frozen", "cusum@5", "t1p5", 1), ("frozen", "cusum@5", "t1p5", 2),
    ("frozen", "sr@520.886", "t1p5", 1), ("frozen", "sr@520.886", "t1p5", 2),
    ("frozen", "sr@520.886", "t1p5", 5),
]


def main() -> int:
    theorem_supported = sorted(
        name for name, spec in PROTOCOL["families"].items()
        if spec["class"] == "THEOREM-SUPPORTED")
    m_grid = list(PROTOCOL["m_grid"])
    block_paths = {row["regime"]: row["block_paths"] for row in FEASIBILITY["plan"]}
    regime_of = {"gaussian": "light", "laplace": "light", "logistic": "light",
                 "skewnormal4": "light", "t3": "moderate", "t1p5": "heavy"}

    configs = []
    for layer in ("reduced", "frozen"):
        for kind, threshold in PROTOCOL["layers"][layer]["detectors"]:
            for family in theorem_supported:
                configs.append({
                    "layer": layer, "detector_kind": kind,
                    "threshold": float(threshold),
                    "detector": f"{kind}@{threshold:g}",
                    "family": family,
                    "max_steps": int(PROTOCOL["layers"][layer]["max_steps"]),
                    "regime": regime_of[family],
                })
    configs.sort(key=lambda c: (c["layer"], c["detector"], c["family"]))

    unresolved_configs = {f"{l}/{d}/{f}" for l, d, f, _ in UNRESOLVED_CELLS}
    for index, cfg in enumerate(configs):
        cfg["index"] = index
        cfg["id"] = f"{cfg['layer']}/{cfg['detector']}/{cfg['family']}"
        cfg["block_paths"] = block_paths[cfg["regime"]]
        cfg["blocks_full"] = BLOCKS
        cfg["blocks_stage0"] = STAGE0_BLOCKS
        cfg["paths_full"] = BLOCKS * cfg["block_paths"]
        cfg["seed_rb_score"] = SEED_SCORE + SEED_STRIDE * index
        cfg["seed_rb_map"] = SEED_MAP + SEED_STRIDE * index
        cfg["seed_fd_ladder"] = SEED_LADDER + SEED_STRIDE * index
        cfg["blocks_fd_ladder"] = LADDER_BLOCKS
        cfg["carries_unresolved_cells"] = cfg["id"] in unresolved_configs
        cfg["unresolved_m"] = sorted(
            m for l, d, f, m in UNRESOLVED_CELLS
            if f"{l}/{d}/{f}" == cfg["id"])

    seeds = ([c["seed_rb_score"] for c in configs]
             + [c["seed_rb_map"] for c in configs]
             + [c["seed_fd_ladder"] for c in configs])
    assert len(set(seeds)) == len(seeds), "seed collision"
    historical = set(PROTOCOL["master_seeds"].values())
    assert not (set(seeds) & historical), "collision with a historical P4 seed"

    plan = {
        "schema": "rebaseguard.p4z-campaign-plan.v1",
        "derived_from": {
            "protocol": "p4_theory_generalization/configs/P4_PROTOCOL.json",
            "checkpoint": "p4z_location_family_feasibility/configs/checkpoint_p4z.json",
            "feasibility": "p4z_location_family_feasibility/results/estimator_feasibility.json",
            "unresolved_cells": "PHASE0_HISTORICAL_AUDIT.md section 6, from P4X c2_cell_ledger.json",
            "note": "no value in this plan is taken from a prompt",
        },
        "scope": {
            "layers": ["reduced", "frozen"],
            "families_theorem_supported": theorem_supported,
            "m_grid": m_grid,
            "configurations": len(configs),
            "cells": len(configs) * len(m_grid),
            "outside_assumption_families": sorted(
                n for n, s in PROTOCOL["families"].items()
                if s["class"] != "THEOREM-SUPPORTED"),
            "outside_assumption_new_compute": "NONE",
            "narrowing_after_results": "NOT PERMITTED",
        },
        "unresolved_residue": {
            "cells": [{"layer": l, "detector": d, "family": f, "m": m}
                      for l, d, f, m in UNRESOLVED_CELLS],
            "count": len(UNRESOLVED_CELLS),
            "configurations": sorted(unresolved_configs),
        },
        "fixed_policy": {
            "blocks_per_route_full": BLOCKS,
            "blocks_per_route_stage0": STAGE0_BLOCKS,
            "adaptive": False,
            "top_ups_permitted": 0,
            "path_count_may_increase_during_run": False,
            "seed_rule": f"seed = base + {SEED_STRIDE} * configuration_index, "
                         f"base rb_score {SEED_SCORE}, rb_map {SEED_MAP}, "
                         f"fd_ladder {SEED_LADDER}",
        },
        "fd_steps": PROTOCOL["fd_steps"],
        "fd_ladder_steps": LADDER_STEPS,
        "fd_ladder_blocks": LADDER_BLOCKS,
        "thresholds": {
            "relative": PROTOCOL["gates"]["correspondence_relative_limit"],
            "z": PROTOCOL["gates"]["correspondence_z_limit"],
            "r_star": CHECKPOINT["gate_thresholds_unchanged"]["r_star"],
            "top1_share_max": CHECKPOINT["uncertainty_rule"]["scale_stability"]["top1_share_max"],
            "top5_share_max": CHECKPOINT["uncertainty_rule"]["scale_stability"]["top5_share_max"],
            "fd_ladder_relative_max": 0.02,
        },
        "budget": {
            "total_cpu_cap_hours": CHECKPOINT["budget"]["total_cpu_cap_hours"],
            "per_configuration_cpu_cap_hours":
                CHECKPOINT["budget"]["per_configuration_cpu_cap_hours"],
        },
        "execution": {"workers": 1, "blas_threads": 1},
        "configurations": configs,
    }
    out = NS / "production" / "campaign_plan.json"
    out.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    print(f"configurations {len(configs)}  cells {len(configs)*len(m_grid)}  "
          f"unresolved cells {len(UNRESOLVED_CELLS)} in "
          f"{len(unresolved_configs)} configurations")
    for c in configs:
        if c["carries_unresolved_cells"]:
            print(f"  * {c['id']:32s} m={c['unresolved_m']}  "
                  f"block_paths={c['block_paths']:,}  seed={c['seed_rb_score']}")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
