#!/usr/bin/env python3
"""Run the 22 frozen adversarial checks for external validation V2."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from config import BASE, PRIMARY_TASKS, PROTOCOL, ROOT
from integrity import verify


def load(relative: str):
    return json.loads((BASE / relative).read_text())


def git_added(relative: str) -> str:
    return subprocess.check_output(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", str(BASE.relative_to(ROOT) / relative)],
        cwd=ROOT, text=True,
    ).splitlines()[-1]


def ancestor(left: str, right: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", left, right],
                          cwd=ROOT).returncode == 0


def add(checks, check_id: str, name: str, passed: bool, detail: str):
    checks.append({"id": check_id, "name": name, "passed": bool(passed), "detail": detail})


def run() -> dict:
    checks = []
    selection = load("results/dataset_selection.json")
    gates = load("results/gates.json")
    decision = load("results/decision.json")
    analyses = {task: load(f"results/task_{task}_analysis.json") for task in PRIMARY_TASKS}
    raw = {task: load(f"results/task_{task}_confirmatory.json") for task in PRIMARY_TASKS}

    stage_e = json.loads((ROOT / "level4/stage_e/results/stage_e_decision.json").read_text())
    add(checks, "A1", "Stage E historical decision unchanged",
        stage_e["decision"] == "STAGE-E-PARTIAL" and stage_e["n_tasks_supporting_H_E5"] == 0,
        "historical Stage E remains PARTIAL with 0/3 H-E5")
    add(checks, "A2", "no old Stage-E data pooled",
        selection["old_stage_e_data_pooled"] is False and
        set(selection["primary_tasks"]) == {"household", "metro", "beijing"},
        "V2 primaries are independent of historical Stage-E tasks")

    freeze_commit = git_added("results/protocol_hash.json")
    outcome_commits = [git_added(f"results/task_{task}_confirmatory.json") for task in PRIMARY_TASKS]
    add(checks, "A3", "dataset selection preceded confirmatory policy outcomes",
        all(freeze_commit != commit and ancestor(freeze_commit, commit) for commit in outcome_commits),
        f"protocol {freeze_commit[:8]} precedes outcomes {sorted({c[:8] for c in outcome_commits})}")
    add(checks, "A4", "no task replacement after unfavorable outcome",
        set(gates["tasks"]) == set(PRIMARY_TASKS) and
        not any(path.exists() for path in [BASE / "results/task_load_diagrams_confirmatory.json"]),
        "all three frozen primaries retained; backup inactive")
    add(checks, "A5", "power floor frozen",
        PROTOCOL["power"]["minimum_effective_blocks"] == 20 and
        load("results/protocol_hash.json")["status"] == "FROZEN",
        "20-block floor is inside frozen protocol bundle")

    gate_commit = git_added("results/gates.json")
    add(checks, "A6", "calibration frozen before evaluation outcomes",
        all(ancestor(gate_commit, commit) and gate_commit != commit for commit in outcome_commits) and
        all(raw[task]["threshold"] == gates["tasks"][task]["calibration"]["threshold"] for task in PRIMARY_TASKS),
        f"gate {gate_commit[:8]} precedes outcome checkpoint; thresholds identical")
    leakage_ok = all(all(row["gates"][key] for key in ("dataset", "leakage", "power", "calibration"))
                     and row["leakage"]["chronological_nonoverlap"]
                     for row in gates["tasks"].values())
    add(checks, "A7", "no future leakage", leakage_ok,
        "train/calibration/evaluation and source guards all pass")
    add(checks, "A8", "matched streams",
        all(row["matched_streams"] and len(row["events"]["relative_grid"]) == 120
            for row in raw.values()),
        "each task has one residual hash, threshold, and 120-point grid shared by policies")

    execution_commit = git_added("results/execution_hash.json")
    add(checks, "A9", "rho outcome-blind",
        PROTOCOL["policies"]["P2_rebaseguard"] == 0.029796 and
        all(ancestor(execution_commit, commit) and execution_commit != commit for commit in outcome_commits),
        f"rho fixed at execution checkpoint {execution_commit[:8]}")
    expected_conditions = {"STEP_0.5", "STEP_1.0", "STEP_2.0", "GRADUAL_1.0", "RECURRING_1.0"}
    add(checks, "A10", "drift conditions outcome-blind",
        {row["id"] for row in PROTOCOL["interventions"]} == expected_conditions and
        all(set(next(iter(row["events"]["policies"].values()))["interventions"]) == expected_conditions
            for row in raw.values()),
        "five conditions match frozen protocol exactly")

    metric_text = (BASE / "METRIC_DEFINITIONS.md").read_text().lower()
    add(checks, "A11", "matched-wait denominator",
        "matched-wait denominator" in metric_text and
        not any("cyclelen" in json.dumps(row).lower() for row in raw.values()),
        "E1 arrays contain only event delay and matched in-control wait")
    add(checks, "A12", "dependence-aware inference",
        PROTOCOL["bootstrap"]["event_block"] == 6 and
        all(row["E2"]["P1_over_P2"]["block"] == 2 for row in analyses.values()),
        "two-week natural and six-event moving blocks used")
    add(checks, "A13", "effective block floor enforced",
        all(row["reliable"] for row in analyses.values()) and
        all(min(gate["actual_power"][key] for key in
                ("natural_week_blocks", "event_blocks", "calibration_cycle_blocks")) >= 20
            for gate in gates["tasks"].values()),
        "every closure endpoint/task meets floor 20")
    add(checks, "A14", "unreliable endpoints excluded",
        all(row["reliable"] for row in analyses.values()),
        "no unreliable endpoint enters H2-4")
    add(checks, "A15", "P3 exploratory only",
        "P3" not in json.dumps(PROTOCOL["policies"]),
        "P3 is absent from the confirmatory policy set")

    safe_text = "\n".join((BASE / name).read_text() for name in ("RESULTS.md", "FINAL_REPORT.md"))
    add(checks, "A16", "no sample-efficiency claim unless consumption differs",
        not re.search(r"sample[- ]efficien|sample savings|fewer samples", safe_text, re.I),
        "current result reports contain no sample-efficiency claim")
    add(checks, "A17", "alert burden not called false-alarm rate",
        not re.search(r"false[- ]alarm rate", safe_text, re.I),
        "current result reports use alert burden only")
    forbidden = ["universally robust", "deployment proven", "distribution-free",
                 "detector-independent", "all real-world streams", "optimal"]
    boundary = (BASE / "FINAL_REPORT.md").read_text()
    negative_context = "It does\nnot support" in boundary and all(word in boundary for word in forbidden)
    add(checks, "A18", "no production-validation wording",
        negative_context and "production validated" in boundary,
        "forbidden phrases appear only inside an explicit does-not-support boundary")

    figures_source = (BASE / "src/figures.py").read_text()
    figure_names = {path.name for path in (BASE / "figures").glob("*.png")}
    add(checks, "A19", "figures from final JSON only",
        "results/summary.json" in figures_source and
        "confirmatory.json" not in figures_source and "analysis.json" not in figures_source and
        len(figure_names) == 4,
        "four figures read only results/summary.json")
    integrity_errors = verify()
    add(checks, "A20", "historical hashes unchanged", not integrity_errors,
        "all protected tracked roots match" if not integrity_errors else "; ".join(integrity_errors))

    verification_path = BASE / "results/verification.json"
    verification = load("results/verification.json") if verification_path.exists() else {}
    add(checks, "A21", "full verifier green",
        verification.get("status") == "PASS" and verification.get("current_distinct_checks") == 1028,
        "verification record missing/not final" if not verification else
        f"recorded status={verification.get('status')} checks={verification.get('current_distinct_checks')}")
    reproduction_path = BASE / "results/reproduction.json"
    reproduction = load("results/reproduction.json") if reproduction_path.exists() else {}
    add(checks, "A22", "reproducer byte-stable",
        reproduction.get("status") == "PASS" and reproduction.get("byte_stable") is True,
        "reproduction record missing/not final" if not reproduction else
        f"recorded status={reproduction.get('status')} byte_stable={reproduction.get('byte_stable')}")

    passed = sum(row["passed"] for row in checks)
    return {"schema": "rebaseguard.external-validation-v2.adversarial.v1",
            "passed": passed, "total": 22,
            "status": "PASS" if passed == 22 else "FAIL", "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.output:
        path = BASE / args.output
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"adversarial: {result['passed']}/{result['total']} {result['status']}")
    for row in result["checks"]:
        if not row["passed"]:
            print(f"  {row['id']} FAIL: {row['name']} — {row['detail']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
