#!/usr/bin/env python3
"""P4X production C2 -- stage-2 top-up and gate adjudication.

Stage 2 tops up ONLY where a route's own achieved precision misses r*.  The
trigger reads the route's achieved relative standard error and nothing else:
not the discrepancy, not its sign, not whether the cell passes, not whether the
campaign would close.  The top-up size is deterministic from the achieved SE,
the frozen r*, the frozen kappa, the frozen minimum block size and the paths
already used.

Adjudication then applies the frozen X6 gate to the pooled estimates.

Usage:
    run_c2_stage2_adjudicate.py plan      # project top-ups, enforce caps
    run_c2_stage2_adjudicate.py run       # execute the approved top-ups
    run_c2_stage2_adjudicate.py adjudicate
"""

from __future__ import annotations

import json
import math
import multiprocessing as mp
import sys
import time
from pathlib import Path

PROD = Path(__file__).resolve().parent
sys.path.insert(0, str(PROD))

import importlib.util
_spec = importlib.util.spec_from_file_location("c2", PROD / "run_c2_production.py")
C2 = importlib.util.module_from_spec(_spec)
#: register before exec so multiprocessing can resolve `c2.job` by qualified
#: name when pickling the work function for the pool
sys.modules["c2"] = C2
_spec.loader.exec_module(C2)

CHECKPOINT = C2.CHECKPOINT
R_STAR = C2.R_STAR
M_GRID = C2.M_GRID
TOTAL_CAP_H = C2.TOTAL_CAP_H
PER_CONFIG_CAP_H = C2.PER_CONFIG_CAP_H


def load(name: str) -> dict:
    return json.loads((PROD / "results" / name).read_text())


def other_campaign_cpu_hours() -> float:
    """CPU already spent by this campaign outside the C2 stages."""
    total = 0.0
    for name in ("anchors.json", "c6_lean_arb.json"):
        path = PROD / "results" / name
        if path.exists():
            total += json.loads(path.read_text()).get("cpu_seconds", 0.0)
    return total / 3600.0


def achieved(results: list[dict]) -> dict:
    """Worst achieved relative SE per (config, route), over the shared m grid."""
    out = {}
    for r in results:
        rels = {}
        for m in M_GRID:
            g = r["by_m"][str(m)]
            rels[m] = abs(g["se"] / g["mean"]) if g["mean"] else math.inf
        out[(r["config"], r["route"])] = {
            "result": r, "relative_se_by_m": rels,
            "worst_relative_se": max(rels.values()),
            "worst_m": max(rels, key=rels.get),
        }
    return out


def plan_stage2() -> dict:
    s1 = load("c2_stage1.json")
    ach = achieved(s1["results"])
    spec_by = {(s["config"], s["route"]): s for s in s1["specs"]}

    cpu_by_config: dict[str, float] = {}
    for r in s1["results"]:
        cpu_by_config[r["config"]] = cpu_by_config.get(r["config"], 0.0) \
            + r["cpu_seconds"] / 3600.0
    spent = sum(r["cpu_seconds"] for r in s1["results"]) / 3600.0 \
        + other_campaign_cpu_hours()

    plans = []
    for (cfg, route), a in sorted(ach.items()):
        spec = spec_by[(cfg, route)]
        r = a["result"]
        rel, n1 = a["worst_relative_se"], r["paths"]
        needs = rel > R_STAR
        kappa = C2.KAPPA_TOPUP_HEAVY if spec["heavy"] else 0.5
        if needs:
            target_n = n1 * (rel / R_STAR) ** (1.0 / kappa)
            additional = max(0.0, target_n - n1)
        else:
            target_n, additional = float(n1), 0.0
        sec_per_1e6 = (r["cpu_seconds"] / r["paths"] * 1e6) if r["paths"] else 0.0
        proj_h = additional / 1e6 * sec_per_1e6 / 3600.0
        cfg_total_if_run = cpu_by_config[cfg] + proj_h
        over_config = cfg_total_if_run > PER_CONFIG_CAP_H
        over_total = (spent + proj_h) > TOTAL_CAP_H
        plans.append({
            "config": cfg, "route": route, "heavy": spec["heavy"],
            "reason": "PRECISION_ONLY",
            "stage1_N": n1,
            "stage1_SE_worst_relative": rel,
            "stage1_worst_m": a["worst_m"],
            "relative_se_by_m": {str(k): v for k, v in a["relative_se_by_m"].items()},
            "meets_r_star": not needs,
            "r_star": R_STAR, "kappa_topup": kappa,
            "target_N": target_n, "additional_N": additional,
            "measured_seconds_per_1e6": sec_per_1e6,
            "projected_additional_cpu_hours": proj_h,
            "config_cpu_hours_so_far": cpu_by_config[cfg],
            "config_cpu_hours_if_topped_up": cfg_total_if_run,
            "exceeds_per_configuration_cap": over_config,
            "exceeds_total_cap": over_total,
            "decision": ("NO_TOPUP_REQUIRED" if not needs else
                         "PRECISION_LIMITED" if (over_config or over_total)
                         else "TOPUP_APPROVED"),
        })

    payload = {
        "schema": "rebaseguard.p4x-production-c2-stage2-plan.v1",
        "r_star": R_STAR,
        "trigger": "the route's own achieved relative standard error",
        "trigger_excludes": [
            "discrepancy", "discrepancy sign", "whether the cell passes",
            "whether the cell is close to passing",
            "whether the campaign would close"],
        "campaign_cpu_hours_before_stage2": spent,
        "total_cap_hours": TOTAL_CAP_H,
        "per_configuration_cap_hours": PER_CONFIG_CAP_H,
        "plans": plans,
        "topups_approved": [p for p in plans if p["decision"] == "TOPUP_APPROVED"],
        "precision_limited": [p for p in plans if p["decision"] == "PRECISION_LIMITED"],
        "already_meeting_r_star": [p for p in plans
                                   if p["decision"] == "NO_TOPUP_REQUIRED"],
    }
    (PROD / "results" / "c2_stage2_plan.json").write_text(
        json.dumps(payload, indent=2) + "\n")
    return payload


#: A top-up projected to take longer than this is split across workers.  The
#: split is a SCHEDULING choice: each shard runs the identical estimator at the
#: identical block size with its own Philox seed, and the shards are pooled as
#: blocks.  Total N, block size, estimator and gate are unchanged.
SHARD_THRESHOLD_HOURS = 2.0
MAX_SHARDS = 5


def run_stage2(plan: dict) -> dict:
    approved = plan["topups_approved"]
    if not approved:
        payload = {"schema": "rebaseguard.p4x-production-c2-stage2.v1",
                   "specs": [], "results": [],
                   "note": "no top-up was required or approved",
                   "cpu_seconds_sum_of_jobs": 0.0, "wall_seconds": 0.0}
        (PROD / "results" / "c2_stage2.json").write_text(
            json.dumps(payload, indent=2) + "\n")
        return payload

    s1 = load("c2_stage1.json")
    spec_by = {(s["config"], s["route"]): s for s in s1["specs"]}
    specs = []
    for p in approved:
        base = dict(spec_by[(p["config"], p["route"])])
        blocks_total, bs = C2.allocate(p["additional_N"], base["heavy"])
        proj = p["projected_additional_cpu_hours"]
        n_shards = 1
        if proj > SHARD_THRESHOLD_HOURS:
            n_shards = min(MAX_SHARDS, math.ceil(proj / SHARD_THRESHOLD_HOURS))
        per_shard = math.ceil(blocks_total / n_shards)
        for k in range(n_shards):
            spec = dict(base)
            spec.update({
                "stage": 2, "shard": k, "shards": n_shards,
                "blocks": per_shard, "block_size": bs,
                "projected_cpu_hours": proj / n_shards,
                "seed": C2.seed_for(base["layer"], base["kind"], base["family"],
                                    f"{base['route']}_s2_shard{k}"),
            })
            specs.append(spec)
    t0 = time.perf_counter()
    results = C2.run_specs(specs, "STAGE 2 (precision top-up)")
    payload = {
        "schema": "rebaseguard.p4x-production-c2-stage2.v1",
        "shard_threshold_hours": SHARD_THRESHOLD_HOURS,
        "sharding_note": (
            "a top-up projected above the threshold is split across workers; "
            "each shard runs the identical estimator at the identical block "
            "size with its own Philox seed, and shards are pooled as blocks.  "
            "Total N, block size, estimator, precision rule and gate are "
            "unchanged -- this is a scheduling choice only"),
        "specs": specs, "results": results,
        "cpu_seconds_sum_of_jobs": sum(r["cpu_seconds"] for r in results),
        "wall_seconds": time.perf_counter() - t0,
    }
    (PROD / "results" / "c2_stage2.json").write_text(
        json.dumps(payload, indent=2) + "\n")
    return payload


def adjudicate() -> dict:
    s1 = load("c2_stage1.json")
    s2 = load("c2_stage2.json") if (PROD / "results" / "c2_stage2.json").exists() \
        else {"results": []}
    plan = load("c2_stage2_plan.json")
    corr = json.loads(
        (PROD.parent.parent / "p4_theory_generalization" / "results"
         / "correspondence.json").read_text())

    s1_by = {(r["config"], r["route"]): r for r in s1["results"]}
    s2_by: dict[tuple, list] = {}
    for r in s2["results"]:
        s2_by.setdefault((r["config"], r["route"]), []).append(r)
    limited = {(p["config"], p["route"]) for p in plan["precision_limited"]}

    gate = CHECKPOINT["gates"]["X6_theorem_supported_correspondence"]
    rel_limit = CHECKPOINT["precision_rule"]["frozen_accuracy_criterion"]
    z_limit = 4.0

    cells = []
    for hist in corr["monte_carlo"]["cells"]:
        if hist["family_class"] != "THEOREM-SUPPORTED":
            continue
        cfg = C2.config_key(hist["layer"], hist["detector"], hist["family"])
        m = hist["m"]
        row = {"config": cfg, "layer": hist["layer"], "detector": hist["detector"],
               "family": hist["family"], "m": m}
        est = {}
        for route in ("route_a", "route_b"):
            a1 = s1_by[(cfg, route)]
            shards = s2_by.get((cfg, route), [])
            g = C2.pooled([a1["by_m"][str(m)]]
                          + [s["by_m"][str(m)] for s in shards])
            rel_se = abs(g["se"] / g["mean"]) if g["mean"] else math.inf
            est[route] = {
                "estimate": g["mean"], "se": g["se"],
                "relative_se": rel_se,
                "paths": g["paths"], "blocks": g["batches"],
                "block_size": g["paths_per_batch"],
                "stage1_paths": a1["paths"],
                "stage2_paths": sum(s["paths"] for s in shards),
                "stage2_shards": len(shards),
                "meets_r_star": rel_se <= R_STAR,
                "precision_status": ("PRECISION_LIMITED"
                                     if (cfg, route) in limited
                                     else "AT_TARGET" if rel_se <= R_STAR
                                     else "BELOW_TARGET"),
                "cpu_seconds": a1["cpu_seconds"] + sum(
                    s["cpu_seconds"] for s in shards),
                "wall_seconds": a1["wall_seconds"] + sum(
                    s["wall_seconds"] for s in shards),
                "peak_rss_mb": max([a1["peak_rss_mb"]]
                                   + [s["peak_rss_mb"] for s in shards]),
            }
        a, b = est["route_a"], est["route_b"]
        diff = abs(a["estimate"] - b["estimate"])
        scale = max(abs(a["estimate"]), abs(b["estimate"]))
        combined = math.hypot(a["se"], b["se"])
        rel_disc = diff / scale if scale else math.inf
        z = diff / combined if combined else math.inf
        precision_limited = any(
            est[r]["precision_status"] == "PRECISION_LIMITED"
            for r in ("route_a", "route_b"))
        # Checkpoint A X6 precondition: "each route on each cell must
        # FIRST reach r*, or be declared PRECISION_LIMITED from projected
        # cost alone".  A route that received its one frozen top-up and
        # still missed r*, without hitting a cap, satisfies NEITHER
        # branch, so the gate is not adjudicable for that cell.  The
        # criterion value is still recorded, clearly labelled, so nothing
        # is hidden.
        precondition_unmet = (not precision_limited) and any(
            est[r]["precision_status"] == "BELOW_TARGET"
            for r in ("route_a", "route_b"))
        row.update({
            "route_a": a, "route_b": b,
            "h_values": list(C2.FD_STEPS),
            "richardson": "(4 D(h/2) - D(h)) / 3 per block",
            "absolute_difference": diff,
            "relative_discrepancy": rel_disc,
            "combined_se": combined,
            "z": z,
            "gate_relative_limit": rel_limit,
            "gate_z_limit": z_limit,
            "criterion_satisfied_informational": bool(
                rel_disc <= rel_limit and z <= z_limit),
            "precondition_unmet": precondition_unmet,
            "gate_result": ("PRECISION_LIMITED" if precision_limited else
                            "PRECONDITION_NOT_MET" if precondition_unmet
                            else "PASS"
                            if (rel_disc <= rel_limit and z <= z_limit)
                            else "FAIL"),
            "precision_status": ("PRECISION_LIMITED" if precision_limited
                                 else "AT_TARGET"
                                 if a["meets_r_star"] and b["meets_r_star"]
                                 else "BELOW_TARGET"),
        })
        cells.append(row)

    passed = [c for c in cells if c["gate_result"] == "PASS"]
    failed = [c for c in cells if c["gate_result"] == "FAIL"]
    plimited = [c for c in cells if c["gate_result"] == "PRECISION_LIMITED"]
    unmet = [c for c in cells if c["gate_result"] == "PRECONDITION_NOT_MET"]

    c2_status = ("PASS" if len(passed) == len(cells) else
                 "FAIL" if failed else "INCOMPLETE")
    payload = {
        "schema": "rebaseguard.p4x-production-c2-ledger.v1",
        "obligation": "C2",
        "gate": gate["criterion"],
        "cells_total": len(cells),
        "cells_passed": len(passed),
        "cells_failed": len(failed),
        "cells_precision_limited": len(plimited),
        "cells_precondition_not_met": len(unmet),
        "failed_cells": failed,
        "precision_limited_cells": plimited,
        "precondition_not_met_cells": unmet,
        "precondition": 'Checkpoint A X6: each route on each cell must first reach r*, or be declared PRECISION_LIMITED from projected cost alone',
        "precondition_note": 'Cells recorded PRECONDITION_NOT_MET received their one frozen top-up, sized deterministically by the frozen rule, and still missed r* without hitting any cap. Checkpoint A permits at most one top-up, so no further paths may be bought, and the caps were not reached, so PRECISION_LIMITED does not apply either. The gate is therefore not adjudicable for these cells. Their criterion values are recorded in criterion_satisfied_informational and are NOT treated as passes.',
        "cells": cells,
        "C2": c2_status,
    }
    (PROD / "results" / "c2_cell_ledger.json").write_text(
        json.dumps(payload, indent=2) + "\n")
    return payload


if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if mode == "plan":
        p = plan_stage2()
        print(f"campaign CPU before stage 2: {p['campaign_cpu_hours_before_stage2']:.4f} h")
        print(f"already at r*: {len(p['already_meeting_r_star'])}")
        print(f"top-ups approved: {len(p['topups_approved'])}")
        print(f"precision limited: {len(p['precision_limited'])}")
        for q in p["topups_approved"] + p["precision_limited"]:
            print(f"  {q['config']:34s} {q['route']:8s} {q['decision']:18s} "
                  f"relSE={q['stage1_SE_worst_relative']:.5f} "
                  f"add_N={q['additional_N']:.3g} "
                  f"proj={q['projected_additional_cpu_hours']:.3f}h")
    elif mode == "run":
        run_stage2(load("c2_stage2_plan.json"))
    elif mode == "adjudicate":
        led = adjudicate()
        print(f"C2 = {led['C2']}   pass {led['cells_passed']}/{led['cells_total']}"
              f"   fail {led['cells_failed']}"
              f"   precision-limited {led['cells_precision_limited']}"
              f"   precondition-not-met {led['cells_precondition_not_met']}")
    else:
        raise SystemExit(f"unknown mode {mode}")
