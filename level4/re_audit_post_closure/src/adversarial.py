#!/usr/bin/env python3
"""Deterministic R1--R18 adversarial checks for the post-closure re-audit."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from generate_audit import AUDIT, REPO, SOURCE, VERIFICATION, derive_decision, load_json, verify_historical_hashes


RESULT = AUDIT / "results" / "adversarial.json"
GENERATED_DOCS = (
    AUDIT / "README.md",
    AUDIT / "REQUIREMENT_UPDATE.md",
    AUDIT / "INTEGRITY_AUDIT.md",
    AUDIT / "CURRENT_SCIENTIFIC_SYNTHESIS.md",
    AUDIT / "FINAL_DECISION.md",
    AUDIT / "FAILURE_DIAGNOSES.md",
    REPO / "level4/reports/LEVEL_4_POST_CLOSURE_REAUDIT.md",
    REPO / "level4/reports/LEVEL_4_CURRENT_LEDGER.md",
)


def _stage_d_criterion(decision: dict[str, Any], criterion_id: str) -> dict[str, Any]:
    return next(row for row in decision["criteria"] if row["id"] == criterion_id)


def _all_generated_text() -> str:
    return "\n".join(path.read_text().lower() for path in GENERATED_DOCS if path.exists())


def evaluate_checks() -> list[dict[str, Any]]:
    source = load_json(SOURCE)
    current = derive_decision()
    stage_f = load_json(REPO / "level4/stage_f/results/final_decision.json")
    stage_d = load_json(REPO / "level4/stage_d/results/stage_d_decision.json")
    stage_e = load_json(REPO / "level4/stage_e/results/stage_e_decision.json")
    track1a = load_json(REPO / "level4/closure_proofs/m_gt_1_track1a/results/decision.json")
    track1b = load_json(REPO / "level4/closure_proofs/m_gt_1_track1b/results/decision.json")
    track2 = load_json(REPO / "level4/closure_proofs/sr_derivative/results/decision.json")
    track3 = load_json(REPO / "level4/closure_proofs/location_family/results/decision.json")
    track3ab = load_json(REPO / "level4/closure_proofs/location_family_track3ab/results/decision.json")
    d25 = load_json(REPO / "level4/stage_d/results/d2_5_verdict.json")
    verification = load_json(VERIFICATION)
    historical = verify_historical_hashes()
    docs = _all_generated_text()
    rows = {row["id"]: row for row in current["requirements"]}

    checks: list[dict[str, Any]] = []

    def add(check_id: str, description: str, passed: bool, evidence: Any) -> None:
        checks.append({
            "id": check_id,
            "description": description,
            "passed": bool(passed),
            "evidence": evidence,
        })

    add("R1", "Stage-F historical verdict remains preserved",
        stage_f["decision"] == "LEVEL-4-PARTIAL"
        and current["historical_stage_f_status"] == "LEVEL-4-PARTIAL",
        {"stage_f": stage_f["decision"], "current_historical_field": current["historical_stage_f_status"]})
    add("R2", "Stage-D D2.3 historical FAIL remains preserved",
        _stage_d_criterion(stage_d, "D2.3")["status"] == "FAIL",
        _stage_d_criterion(stage_d, "D2.3"))
    add("R3", "Track 1A historical FAIL remains preserved",
        track1a["decision"] == "MGT1-TRACK1A-FAILED",
        track1a["decision"])
    add("R4", "Historical Track 3 PARTIAL and 4.605351% failure remain preserved",
        track3["decision"] == "LOCATION-FAMILY-THEOREM-PARTIAL"
        and track3["numerical"]["t3_replication_relative"] > track3["numerical"]["t3_replication_relative_limit"],
        {"decision": track3["decision"], "relative": track3["numerical"]["t3_replication_relative"],
         "limit": track3["numerical"]["t3_replication_relative_limit"]})
    add("R5", "Track 1B closure maps only to the m>1 theorem row",
        track1b["decision"] == "MGT1-TRACK1B-CLOSED"
        and track1b["m_gt_1_derivative_theorem_requirement"] == "CLOSED"
        and rows["L4R-09"]["current_status"] == "PASS",
        {"campaign": track1b["decision"], "row": rows["L4R-09"]["current_status"]})
    add("R6", "Track 2 closure maps only to the SR derivative-theorem row",
        track2["decision"] == "SR-DERIVATIVE-CLOSED"
        and track2["status_boundary"]["derivative_theorem"] == "CLOSED"
        and rows["L4R-10"]["current_status"] == "PASS",
        {"campaign": track2["decision"], "row": rows["L4R-10"]["current_status"]})
    add("R7", "Track 3A/3B closure maps to the location-family theorem row",
        track3ab["decision"] == "LOCATION-FAMILY-TRACK3AB-CLOSED"
        and track3ab["general_location_family_theorem_requirement"] == "CLOSED"
        and rows["L4R-14"]["current_status"] == "PASS",
        {"campaign": track3ab["decision"], "row": rows["L4R-14"]["current_status"]})
    add("R8", "No rigorous SR Gamma certificate is claimed",
        track2["status_boundary"]["rigorous_SR_local_instability_certificate"] == "OPEN"
        and track2["arb"]["certified_gamma_interval"] is False
        and current["sr_status_boundary"]["rigorous_SR_local_instability_certificate"] == "OPEN",
        current["sr_status_boundary"])
    add("R9", "Stage E 0/3 H-E5 result remains preserved",
        stage_e["n_tasks_supporting_H_E5"] == 0
        and stage_e["closure_mathematically_unreachable"] is True
        and rows["L4R-15"]["current_status"] == "FAIL",
        {"support": stage_e["n_tasks_supporting_H_E5"], "row": rows["L4R-15"]["current_status"]})
    add("R10", "D2.5 mathematical-not-operational result remains preserved",
        d25["verdict"] == "MATHEMATICAL, NOT OPERATIONAL"
        and rows["L4R-12"]["current_status"] == "PARTIAL",
        {"verdict": d25["verdict"], "normalized_row": rows["L4R-12"]["current_status"]})
    add("R11", "No affirmative detector-independence wording appears",
        "detector-independent" not in docs,
        {"forbidden_occurrences": docs.count("detector-independent")})
    add("R12", "No affirmative distribution-independence wording appears",
        "distribution-free" not in docs,
        {"forbidden_occurrences": docs.count("distribution-free")})
    production_phrases = ("production validated", "production-validation", "production-proven")
    production_hits = [phrase for phrase in production_phrases if phrase in docs]
    add("R13", "No production-validation wording appears",
        not production_hits, {"forbidden_occurrences": production_hits})
    add("R14", "No protected historical hash changed",
        historical["status"] == "INTACT",
        {"files_verified": historical["files_verified"], "missing": historical["missing"],
         "mismatches": historical["mismatches"]})
    stored = load_json(AUDIT / "results/final_decision.json") if (AUDIT / "results/final_decision.json").exists() else {}
    add("R15", "Current verdict mechanically follows from the 18-row table",
        len(source["requirements"]) == 18
        and stored == current
        and (current["pass_count"], current["partial_count"], current["fail_count"], current["open_count"])
            == (12, 3, 2, 1)
        and current["current_status"] == "LEVEL-4-PARTIAL"
        and [row["id"] for row in current["mandatory_unmet"]] == ["L4R-11", "L4R-15", "L4R-16"],
        {"counts": [current["pass_count"], current["partial_count"], current["fail_count"], current["open_count"]],
         "mandatory_unmet": [row["id"] for row in current["mandatory_unmet"]],
         "verdict": current["current_status"]})
    reproduce_text = (AUDIT / "reproduce.sh").read_text() if (AUDIT / "reproduce.sh").exists() else ""
    prohibited = ("run_confirmatory.py", "run_task.py", "run_d4", "make_figures.py", "run_gate41.py", "run_gate42.py")
    prohibited_hits = [item for item in prohibited if item in reproduce_text]
    add("R16", "No new science is performed by the re-audit",
        source["decision_inputs"]["no_new_science_performed"] is True and not prohibited_hits,
        {"source_declaration": source["decision_inputs"]["no_new_science_performed"],
         "prohibited_commands": prohibited_hits})
    verifier_text = (REPO / "scripts/verify_level_4.sh").read_text()
    add("R17", "Full repository verification passes with re-audit integration",
        verification["authoritative_repository"]["status"] == "PASS"
        and verification["authoritative_repository"]["tests"] == 713
        and "level4/re_audit_post_closure/tests" in verifier_text,
        verification["authoritative_repository"])
    add("R18", "The byte-stable post-closure reproduction script passes",
        verification["post_closure_reproducer"]["status"] == "PASS"
        and verification["post_closure_reproducer"]["byte_stable"] is True
        and (AUDIT / "reproduce.sh").exists()
        and os.access(AUDIT / "reproduce.sh", os.X_OK)
        and "generate_audit.py\" --check" in reproduce_text
        and "scripts/verify_level_4.sh" in reproduce_text,
        verification["post_closure_reproducer"])
    return checks


def result_payload() -> dict[str, Any]:
    checks = evaluate_checks()
    passed = sum(item["passed"] for item in checks)
    return {
        "schema": "rebaseguard.level4-post-closure-adversarial.v1",
        "suite": "Post-closure global Level-4 re-audit",
        "n_checks": len(checks),
        "n_passed": passed,
        "n_failed": len(checks) - passed,
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = result_payload()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not RESULT.exists() or RESULT.read_text() != rendered:
            raise SystemExit("stale adversarial result")
    else:
        RESULT.parent.mkdir(parents=True, exist_ok=True)
        RESULT.write_text(rendered)
    print(f"{payload['n_passed']}/{payload['n_checks']} post-closure adversarial checks passed")
    if payload["n_failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
