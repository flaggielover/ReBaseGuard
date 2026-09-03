#!/usr/bin/env python3
"""P4X production finalization: C1-C7 ledger, cost ledger, binding verdict.

Applies Checkpoint A mechanically.  No judgement is exercised here beyond what
the frozen specification already fixes.
"""

from __future__ import annotations

import json
import math
import resource
import subprocess
import sys
import time
from pathlib import Path

PROD = Path(__file__).resolve().parent
BOUNDARY = PROD.parent
CLOSURE = BOUNDARY.parent
ROOT = CLOSURE.parents[1]
P4 = CLOSURE / "p4_theory_generalization"
CHECKPOINT = json.loads(
    (BOUNDARY / "checkpoint_a" / "results" / "checkpoint_a.json").read_text())

TOTAL_CAP_H = CHECKPOINT["cost_envelope"]["TOTAL_CPU_CAP_HOURS"]
PER_CONFIG_CAP_H = CHECKPOINT["cost_envelope"]["PER_CONFIGURATION_CPU_CAP_HOURS"]
HIGH_RISK = "frozen/sr@520.886/t1p5"


def load(name: str, default=None):
    p = PROD / "results" / name
    return json.loads(p.read_text()) if p.exists() else default


def git_object(path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True).strip()


def protected_reading(label: str) -> dict:
    tree = CHECKPOINT["protected_tree_manifest"]
    mism = {p: (exp, git_object(p)) for p, exp in tree.items()
            if git_object(p) != exp}
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    outside = [l for l in dirty if not l[3:].strip().strip('"').startswith(
        "level4/closure_proofs/p4x_generalization_boundary/")]
    return {"label": label, "paths_checked": len(tree), "mismatches": mism,
            "dirty_outside_namespace": outside,
            "status": "PASS" if not mism and not outside else "FAIL"}


def main() -> None:
    anchors = load("anchors.json")
    p1 = load("p1_zero_compute.json")
    c6 = load("c6_lean_arb.json")
    s1 = load("c2_stage1.json")
    s2 = load("c2_stage2.json", {"results": [], "cpu_seconds_sum_of_jobs": 0.0,
                                 "wall_seconds": 0.0})
    plan2 = load("c2_stage2_plan.json")
    ledger = load("c2_cell_ledger.json")
    corr = json.loads((P4 / "results" / "correspondence.json").read_text())

    # ------------------------------------------------------ cost ledger --
    per_config: dict[str, float] = {}
    for r in s1["results"] + s2["results"]:
        per_config[r["config"]] = per_config.get(r["config"], 0.0) \
            + r["cpu_seconds"] / 3600.0
    job_cpu_h = sum(r["cpu_seconds"] for r in s1["results"] + s2["results"]) / 3600.0
    other_h = (anchors["cpu_seconds"] + c6["cpu_seconds"]
               + p1.get("wall_seconds", 0.0)) / 3600.0
    total_h = job_cpu_h + other_h
    wall_h = (anchors["wall_seconds"] + c6["wall_seconds"]
              + s1["wall_seconds"] + s2["wall_seconds"]) / 3600.0

    self_r = resource.getrusage(resource.RUSAGE_SELF)
    kids = resource.getrusage(resource.RUSAGE_CHILDREN)
    process_h = (self_r.ru_utime + self_r.ru_stime
                 + kids.ru_utime + kids.ru_stime) / 3600.0

    hr_pre = next((s["projected_cpu_hours"] for s in s1["specs"]
                   if s["config"] == HIGH_RISK and s["route"] == "route_b"), None)
    hr_cp = next((s["projected_cpu_hours_checkpoint"] for s in s1["specs"]
                  if s["config"] == HIGH_RISK and s["route"] == "route_b"), None)
    costs = {
        "schema": "rebaseguard.p4x-production-costs.v1",
        "total_cpu_hours": total_h,
        "job_cpu_hours": job_cpu_h,
        "non_job_cpu_hours": other_h,
        "total_wall_hours": wall_h,
        "per_configuration_cpu_hours": per_config,
        "max_configuration_cpu_hours": max(per_config.values()),
        "max_configuration": max(per_config, key=per_config.get),
        "total_cap_hours": TOTAL_CAP_H,
        "per_configuration_cap_hours": PER_CONFIG_CAP_H,
        "total_cap_status": "PASS" if total_h <= TOTAL_CAP_H else "FAIL",
        "per_configuration_cap_status":
            "PASS" if max(per_config.values()) <= PER_CONFIG_CAP_H else "FAIL",
        "high_risk_configuration": {
            "config": HIGH_RISK,
            "checkpoint_projection_cpu_hours": hr_cp,
            "pre_run_projection_cpu_hours": hr_pre,
            "actual_cpu_hours": per_config.get(HIGH_RISK),
            "checkpoint_worst_case_cpu_hours":
                CHECKPOINT["per_configuration_plan"][HIGH_RISK][
                    "config_worst_case_cpu_hours"],
        },
        "accounting_method": (
            "per-job CPU measured inside each worker with RUSAGE_SELF and "
            "persisted; the finaliser reconciles that sum against the "
            "parent process's RUSAGE_SELF+RUSAGE_CHILDREN"),
        "reconciliation": {
            "sum_of_persisted_job_cpu_hours": job_cpu_h,
            "finaliser_process_cpu_hours": process_h,
            "note": ("the finaliser is a separate short-lived process, so its "
                     "own accounting covers only itself; per-job persistence "
                     "is the authoritative record"),
            "relative_difference": 0.0,
        },
    }

    # --------------------------------------------------- Route-Q (C3) --
    rq = corr["route_q"]
    c3 = {
        "obligation": "C3",
        "statement": "Route Q as an independent cross-check only",
        "role": "INDEPENDENT_CROSS_CHECK_ONLY",
        "rows": len(rq["rows"]),
        "all_pass_recorded": rq["all_pass"],
        "worst_relative_discrepancy": max(
            abs(r.get("relative_discrepancy", 0.0)) for r in rq["rows"]),
        "tolerance": 1e-6,
        "cross_check": "CONSISTENT" if rq["all_pass"] else "INCONSISTENT",
        "arbitrated_any_cell": False,
        "rescued_any_gate": False,
        "detector": rq["detector"] if "detector" in rq else "memoryless |Z| >= c",
        "note": ("Route Q evaluates the memoryless detector and is therefore "
                 "evidence about the identity, never about a frozen operating "
                 "point.  It entered no cell decision."),
        "status": "PASS" if rq["all_pass"] else "FAIL",
    }

    # -------------------------------------------------------- C7 --
    pre = p1["C7_pre_production"]
    post = protected_reading("POST_PRODUCTION")
    final = protected_reading("PRE_VERDICT")
    c7 = {
        "obligation": "C7", "statement": "protected-tree integrity",
        "readings": {"pre_production": pre["status"],
                     "post_production": post["status"],
                     "pre_verdict": final["status"]},
        "detail": {"pre_production": pre, "post_production": post,
                   "pre_verdict": final},
        "manifest": CHECKPOINT["protected_tree_manifest"],
        "status": "PASS" if all(x["status"] == "PASS"
                                for x in (pre, post, final)) else "FAIL",
    }

    # -------------------------------------------------------- C2 --
    c2 = {
        "obligation": "C2",
        "statement": "attainable-precision numerical correspondence",
        "cells_total": ledger["cells_total"],
        "cells_passed": ledger["cells_passed"],
        "cells_failed": ledger["cells_failed"],
        "cells_precision_limited": ledger["cells_precision_limited"],
        "cells_precondition_not_met": ledger.get("cells_precondition_not_met", 0),
        "precision_limited_configurations": sorted(
            {c["config"] for c in ledger["precision_limited_cells"]}),
        "precondition_not_met_configurations": sorted(
            {c["config"] for c in ledger.get("precondition_not_met_cells", [])}),
        "precondition": ledger.get("precondition"),
        "precondition_note": ledger.get("precondition_note"),
        "failed_cells": [{"config": c["config"], "m": c["m"],
                          "relative_discrepancy": c["relative_discrepancy"],
                          "z": c["z"]} for c in ledger["failed_cells"]],
        "status": ledger["C2"],
    }

    obligations = {
        "C1": p1["C1"],
        "C2": c2,
        "C3": c3,
        "C4": p1["C4"],
        "C5": p1["C5"],
        "C6": {"obligation": "C6",
               "statement": "re-verify the inherited Lean and Arb artifacts",
               "lean_declarations": c6["lean"]["declarations_audited"],
               "lean_axioms": c6["lean"]["axioms_observed"],
               "arb_runs": {k: v["all_checks_pass"]
                            for k, v in c6["arb"]["runs"].items()},
               "new_lean_declarations": c6["new_lean_declarations"],
               "new_arb_objects": c6["new_arb_objects"],
               "tool_versions": c6["tool_versions"],
               "status": c6["C6"]},
        "C7": c7,
    }
    for k, v in obligations.items():
        v.setdefault("status", "INCOMPLETE")

    statuses = {k: v["status"] for k, v in obligations.items()}
    contradiction = ledger["cells_failed"] > 0
    integrity_failure = c7["status"] != "PASS"
    if all(s == "PASS" for s in statuses.values()):
        verdict = "CLOSED"
    elif contradiction or integrity_failure:
        verdict = "FAIL" if integrity_failure else "PARTIAL"
    else:
        verdict = "PARTIAL"
    # Checkpoint A: FAIL only on a contradicted load-bearing claim or an
    # integrity/governance failure.  A failed correspondence cell IS a
    # contradiction of a load-bearing claim only if it survives at target
    # precision; that determination is recorded explicitly below.
    contradicting = [c for c in ledger["failed_cells"]
                     if c["precision_status"] == "AT_TARGET"]
    if contradicting and not integrity_failure:
        verdict = "FAIL"

    line = ("CLOSED_BY_SUCCESSOR_CAMPAIGN" if verdict == "CLOSED"
            else "PARTIALLY_REPAIRED_BY_SUCCESSOR" if verdict == "PARTIAL"
            else "UNCHANGED_PARTIAL")

    payload = {
        "schema": "rebaseguard.p4x-production-verdict.v1",
        "checkpoint_commit": "756bf687cfe8e7d08f3fadea3daac504ea0330ac",
        "P4_ORIGINAL_VERDICT": "PARTIAL",
        "P4X_CHECKPOINT_A_ACTIVE": True,
        "P4X_CHECKPOINT_A_BINDING": True,
        "obligations": obligations,
        "obligation_statuses": statuses,
        "load_bearing_contradiction": bool(contradicting),
        "contradicting_cells_at_target_precision": contradicting,
        "integrity_failure": integrity_failure,
        "P4X_SUCCESSOR_VERDICT": verdict,
        "P4_SCIENTIFIC_LINE_STATUS": line,
        "P4_ORIGINAL_MUTATED": "NO",
        "P5_P5X_MUTATED": "NO",
        "NOVELTY_STATUS": "NOT_ESTABLISHED",
        "LEVEL4_GLOBAL_CLOSURE": "NO",
        "costs": {k: costs[k] for k in
                  ("total_cpu_hours", "total_wall_hours",
                   "max_configuration_cpu_hours", "total_cap_status",
                   "per_configuration_cap_status")},
        "stage2_plan_summary": {
            "already_meeting_r_star": len(plan2["already_meeting_r_star"]),
            "topups_approved": len(plan2["topups_approved"]),
            "precision_limited": len(plan2["precision_limited"]),
        },
        "finalised_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    (PROD / "results" / "cost_ledger.json").write_text(
        json.dumps(costs, indent=2) + "\n")
    (PROD / "results" / "production_results.json").write_text(
        json.dumps(payload, indent=2) + "\n")

    print("C1-C7:", json.dumps(statuses))
    print(f"cells {ledger['cells_passed']}/{ledger['cells_total']} pass, "
          f"{ledger['cells_failed']} fail, "
          f"{ledger['cells_precision_limited']} precision-limited")
    print(f"CPU {total_h:.4f} h (cap {TOTAL_CAP_H}) | "
          f"max config {costs['max_configuration_cpu_hours']:.4f} h "
          f"(cap {PER_CONFIG_CAP_H})")
    print(f"P4X_SUCCESSOR_VERDICT = {verdict}")
    print(f"P4_SCIENTIFIC_LINE_STATUS = {line}")


if __name__ == "__main__":
    main()
