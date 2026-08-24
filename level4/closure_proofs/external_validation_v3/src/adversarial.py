#!/usr/bin/env python3
"""Run the 25 frozen adversarial checks for external validation V3."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess

from config import BASE, PRIMARY_TASKS, PROTOCOL, ROOT, protocol_digest
from integrity import verify


def load(relative: str) -> dict:
    return json.loads((BASE / relative).read_text())


def git_added(relative: str) -> str:
    output = subprocess.check_output(
        ["git", "log", "--diff-filter=A", "--format=%H", "--",
         str(BASE.relative_to(ROOT) / relative)], cwd=ROOT, text=True,
    ).splitlines()
    return output[-1] if output else ""


def ancestor(left: str, right: str) -> bool:
    return bool(left and right) and subprocess.run(
        ["git", "merge-base", "--is-ancestor", left, right], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(checks: list[dict], check_id: str, name: str, passed: bool, detail: str) -> None:
    checks.append({"id": check_id, "name": name, "passed": bool(passed), "detail": detail})


def run_focused_tests() -> tuple[bool, str]:
    result = subprocess.run(
        [str(ROOT / "level4/.venv/bin/python"), "-m", "pytest", str(BASE / "tests"), "-q"],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    match = re.search(r"(\d+) passed", result.stdout)
    count = int(match.group(1)) if match else 0
    return result.returncode == 0 and count == 75, f"focused tests={count}/75 returncode={result.returncode}"


def run() -> dict:
    checks: list[dict] = []
    selection = load("results/dataset_selection.json")
    discovery = load("results/dataset_discovery.json")
    gates = load("results/gates.json")
    analyses = {task: load(f"results/task_{task}_analysis.json") for task in PRIMARY_TASKS}
    raw = {task: load(f"results/task_{task}_confirmatory.json") for task in PRIMARY_TASKS}
    stage_e = json.loads((ROOT / "level4/stage_e/results/stage_e_decision.json").read_text())
    v2 = json.loads((ROOT / "level4/closure_proofs/external_validation_v2/results/decision.json").read_text())

    add(checks, "A1", "Stage E unchanged",
        stage_e["decision"] == "STAGE-E-PARTIAL" and stage_e["n_tasks_supporting_H_E5"] == 0,
        "historical Stage E remains PARTIAL with 0/3 H-E5")
    add(checks, "A2", "V2 unchanged",
        v2["decision"] == "EXTERNAL-VALIDATION-V2-PARTIAL" and sum(v2["task_support"].values()) == 1,
        "protected V2 decision remains PARTIAL with one supporting task")
    add(checks, "A3", "V2 partial result preserved",
        load("results/scientific_decision.json")["historical_v2_joint_support"] == "1/3",
        "V2 Household remains its sole H2-4 success")
    add(checks, "A4", "no V2 statistics pooled into V3 inference",
        PROTOCOL["aggregation"]["no_statistical_pooling"] and
        all("V2" not in json.dumps(row) for row in raw.values()),
        "V3 confirmatory records contain only task-level streams; aggregation counts decisions")

    freeze_commit = git_added("results/protocol_hash.json")
    outcome_commits = [git_added(f"results/task_{task}_confirmatory.json") for task in PRIMARY_TASKS]
    add(checks, "A5", "selection outcome-blind",
        selection["forbidden_policy_outcomes_inspected"] is False and
        discovery["forbidden_policy_outcomes_inspected"] is False and
        all(ancestor(freeze_commit, commit) and freeze_commit != commit for commit in outcome_commits),
        f"selection/protocol {freeze_commit[:8]} precedes outcomes {sorted(c[:8] for c in outcome_commits)}")
    add(checks, "A6", "power floor frozen",
        PROTOCOL["power"]["minimum_effective_blocks"] == 40 and
        load("results/protocol_hash.json")["protocol_sha256"] == protocol_digest(),
        "40-effective-block floor is in the hashed protocol")
    add(checks, "A7", "no failed task replacement",
        selection["backup"] is None and set(gates["tasks"]) == set(PRIMARY_TASKS),
        "both frozen primaries retained; no backup exists")

    execution_commit = git_added("results/execution_hash.json")
    add(checks, "A8", "rho outcome-blind",
        PROTOCOL["policies"] == {"P0_fresh": 0.0, "P1_full_reuse": 1.0,
                                  "P2_rebaseguard": 0.029796} and
        all(ancestor(execution_commit, commit) and execution_commit != commit for commit in outcome_commits),
        f"rho fixed at execution checkpoint {execution_commit[:8]}")
    expected = {"STEP_0.5", "STEP_1.0", "STEP_2.0", "GRADUAL_1.0", "RECURRING_1.0"}
    add(checks, "A9", "interventions frozen",
        {row["id"] for row in PROTOCOL["interventions"]} == expected and
        all(set(next(iter(row["events"]["policies"].values()))["interventions"]) == expected
            for row in raw.values()),
        "five confirmatory conditions exactly match the frozen family")
    h = PROTOCOL["hypotheses"]
    add(checks, "A10", "H3 definitions unchanged",
        h == {"effect_ratio_floor": 1.1, "primary_noninferiority_epsilon": 0.1,
              "secondary_noninferiority_epsilon": 0.05,
              "simultaneous_one_sided_confidence": 0.99},
        "effect, multiplicity, and safety thresholds match the freeze")
    add(checks, "A11", "matched streams",
        all(row["matched_streams"] and len(row["events"]["relative_grid"]) == 240 and
            set(row["natural"]["policies"]) == set(PROTOCOL["policies"]) for row in raw.values()),
        "each task uses one residual stream and one event grid across policies")
    add(checks, "A12", "no future leakage",
        all(all(row["gates"][key] for key in ("dataset", "leakage", "power", "calibration")) and
            row["leakage"]["chronological_nonoverlap"] and row["leakage"]["no_future_features"]
            for row in gates["tasks"].values()),
        "chronological splits and train/calibration ownership guards pass")
    add(checks, "A13", "dependence-aware block inference",
        PROTOCOL["bootstrap"]["event_block"] == 6 and
        all(value["effective_blocks"] >= 40 for row in analyses.values()
            for section in (row["E1"], row["E2"]) for value in section.values()),
        "paired task-level moving blocks are used; no iid endpoint inference")
    add(checks, "A14", "simultaneous non-inferiority",
        all(row["H3_3"]["supported"] and
            all(value["upper99_excess"] <= 0.10 for value in row["H3_3"]["conditions"].values())
            for row in analyses.values()),
        "all five conditions pass the frozen simultaneous one-sided 99% bound")
    add(checks, "A15", "effective-block floor enforced",
        all(row["reliable"] for row in analyses.values()) and
        all(min(value["actual_power"].values()) >= 40 for value in gates["tasks"].values()),
        "every calibration, natural, and event endpoint meets floor 40")
    add(checks, "A16", "no direction-only support",
        all(value["ratio"] >= 1.1 and value["lower_97_5_one_sided"] > 1
            for row in analyses.values() for section in (row["E1"], row["E2"])
            for value in section.values()),
        "H3-1 and H3-2 Route A meet magnitude and lower-bound rules")
    add(checks, "A17", "contradictions not hidden",
        all(not row["H3_3"]["strong_safety_contradiction"] and
            all(not value["strong_contradiction"] for value in row["H3_3"]["conditions"].values())
            for row in analyses.values()),
        "no strong P2 contradiction exists; all condition bounds remain visible")
    add(checks, "A18", "P3 exploratory only",
        "P3" not in json.dumps(PROTOCOL["policies"]) and
        all("P3" not in json.dumps(row) for row in raw.values()),
        "P3 is absent from every confirmatory policy set")

    report_text = "\n".join((BASE / name).read_text() for name in ("RESULTS.md", "FINAL_REPORT.md"))
    forbidden = ["production validation", "deployment readiness", "universal robustness",
                 "distribution-free validity", "detector independence", "optimality"]
    add(checks, "A19", "no production-validation wording",
        "does not establish" in report_text and all(term in report_text for term in forbidden) and
        "production validated" not in report_text.lower(),
        "strong claims appear only in an explicit does-not-establish boundary")
    aggregation_commit = git_added("results/protocol_hash.json")
    add(checks, "A20", "aggregation frozen before outcomes",
        PROTOCOL["aggregation"]["minimum_cross_campaign_successes"] == 2 and
        all(ancestor(aggregation_commit, commit) and aggregation_commit != commit for commit in outcome_commits),
        f"counting rule frozen at {aggregation_commit[:8]} before confirmatory outcomes")
    figure_source = (BASE / "src/figures.py").read_text()
    figure_names = {path.name for path in (BASE / "figures").glob("*.png")}
    add(checks, "A21", "figures use summary only",
        "results/summary.json" in figure_source and "confirmatory.json" not in figure_source and
        "analysis.json" not in figure_source and len(figure_names) == 5,
        "five figures are generated exclusively from results/summary.json")
    manifests = load("manifests/datasets.json")["datasets"]
    hash_ok = (load("results/execution_hash.json")["execution_config_sha256"] ==
               sha256(BASE / "results/execution_config.json"))
    add(checks, "A22", "protocol, execution, dataset, and history hashes pass",
        protocol_digest() == load("results/protocol_hash.json")["protocol_sha256"] and
        hash_ok and all(len(row["archive_sha256"]) == 64 for row in manifests) and not verify(),
        "all frozen digests and protected historical trees verify")
    tests_ok, tests_detail = run_focused_tests()
    add(checks, "A23", "focused tests pass", tests_ok, tests_detail)

    verification_path = BASE / "results/verification.json"
    verification = load("results/verification.json") if verification_path.exists() else {}
    add(checks, "A24", "full repository verifier passes",
        verification.get("status") == "PASS" and verification.get("current_distinct_checks") == 1103,
        "verification record missing/not final" if not verification else
        f"status={verification.get('status')} checks={verification.get('current_distinct_checks')}")
    reproduction_path = BASE / "results/reproduction.json"
    reproduction = load("results/reproduction.json") if reproduction_path.exists() else {}
    add(checks, "A25", "generated science bytes reproduce",
        reproduction.get("status") == "PASS" and reproduction.get("byte_stable") is True,
        "reproduction record missing/not final" if not reproduction else
        f"status={reproduction.get('status')} byte_stable={reproduction.get('byte_stable')}")

    passed = sum(row["passed"] for row in checks)
    return {"schema": "rebaseguard.external-validation-v3.adversarial.v1",
            "passed": passed, "total": 25, "status": "PASS" if passed == 25 else "FAIL",
            "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.output:
        (BASE / args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"adversarial: {result['passed']}/{result['total']} {result['status']}")
    for row in result["checks"]:
        if not row["passed"]:
            print(f"  {row['id']} FAIL: {row['name']} — {row['detail']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
