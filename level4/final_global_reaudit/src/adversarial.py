#!/usr/bin/env python3
"""Run the 26 terminal-audit adversarial checks."""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
from pathlib import Path

from audit import EXPECTED_MAP, audit_evidence, derive, requirement_ledger, validate_source
from config import BASE, PY, ROOT, SOURCE, load
from integrity import verify as verify_integrity


def add(checks: list[dict], check_id: str, name: str, passed: bool, detail: str) -> None:
    checks.append({"id": check_id, "name": name, "passed": bool(passed), "detail": detail})


def focused_tests() -> tuple[bool, str]:
    result = subprocess.run([str(PY), "-m", "pytest", str(BASE / "tests"), "-q"],
                            cwd=ROOT, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    match = re.search(r"(\d+) passed", result.stdout)
    count = int(match.group(1)) if match else 0
    return result.returncode == 0 and count == 36, f"focused tests={count}/36 returncode={result.returncode}"


def run() -> dict:
    checks: list[dict] = []
    source = load(SOURCE)
    validate_source(source)
    integrity = verify_integrity()
    evidence = audit_evidence()
    decision = derive(source, evidence, integrity)
    stage_f = load(ROOT / "level4/stage_f/results/final_decision.json")
    previous = load(ROOT / "level4/re_audit_post_closure/results/final_decision.json")
    stage_e = load(ROOT / "level4/stage_e/results/stage_e_decision.json")
    v2 = load(ROOT / "level4/closure_proofs/external_validation_v2/results/decision.json")
    sr = load(ROOT / "level4/closure_proofs/sr_derivative/results/decision.json")
    d4 = load(ROOT / "level4/closure_proofs/d4_phase_map/results/decision.json")
    track3 = load(ROOT / "level4/closure_proofs/location_family_track3ab/results/decision.json")
    track1a = load(ROOT / "level4/closure_proofs/m_gt_1_track1a/results/decision.json")
    novelty = load(ROOT / "level4/closure_proofs/novelty_verification/results/decision.json")

    add(checks, "A1", "historical Stage-F cannot be rewritten to CLOSED",
        stage_f["decision"] == decision["historical_stage_f_verdict"] == "LEVEL-4-PARTIAL",
        "Stage F remains immutable LEVEL-4-PARTIAL")
    add(checks, "A2", "previous post-closure audit cannot be rewritten",
        previous["current_status"] == decision["previous_post_closure_verdict"] == "LEVEL-4-PARTIAL",
        "previous re-audit remains immutable LEVEL-4-PARTIAL")
    add(checks, "A3", "Stage E zero-of-three cannot be erased",
        stage_e["decision"] == "STAGE-E-PARTIAL" and stage_e["n_tasks_supporting_H_E5"] == 0,
        "Stage E remains PARTIAL with H-E5 0/3")
    add(checks, "A4", "V2 one-of-three cannot be erased",
        v2["decision"] == "EXTERNAL-VALIDATION-V2-PARTIAL" and sum(v2["task_support"].values()) == 1,
        "V2 remains PARTIAL with H2-4 1/3")
    safe_claims = "\n".join(decision["claims"].values())
    add(checks, "A5", "V3 cannot become universal external validation",
        "universal external validation" not in safe_claims.lower() and
        "scoped" in decision["claims"]["publication_safe_summary"].lower(),
        "publication-safe claim is explicitly scoped")
    add(checks, "A6", "P2 cannot become universally safe",
        "universally safe" not in safe_claims.lower() and
        "regime-dependent" in (BASE / "CLAIM_FIREWALL.md").read_text(),
        "P2 remains regime-dependent")
    add(checks, "A7", "SR numerical evidence cannot become rigorous certificate",
        sr["status_boundary"]["Gamma_SR_gt_2"] == "CONFIRMATORY NUMERICAL" and
        decision["sr_boundary"]["Gamma_SR_gt_2"] == "CONFIRMATORY NUMERICAL",
        "Gamma_SR > 2 remains confirmatory numerical")
    add(checks, "A8", "SR Arb OPEN cannot be hidden",
        sr["arb"]["status"] == "OPEN" and
        decision["sr_boundary"]["rigorous_SR_local_instability_certificate"] == "OPEN" and
        decision["remaining_open_nonblockers"][0]["status"] == "OPEN",
        "SR rigorous local-instability certificate remains visible and OPEN")
    add(checks, "A9", "D4 cannot become operational phase-transition proof",
        d4["decision"] == "D4-PHASE-MAP-CLOSED" and
        decision["historical_statuses_preserved"]["stage_d_D2_5"] == "MATHEMATICAL, NOT OPERATIONAL" and
        "operational phase-transition proof" not in safe_claims.lower(),
        "D4 is a deterministic local-stability map only")
    add(checks, "A10", "historical Track 3 failure cannot be erased",
        track3["historical_track_3"]["decision"] == "LOCATION-FAMILY-THEOREM-PARTIAL" and
        track3["historical_track_3"]["numerical_gate"] == "FAILED",
        "historical Track 3 remains PARTIAL with failed numerical gate")
    add(checks, "A11", "Track 1A failure cannot be erased",
        track1a["decision"] == "MGT1-TRACK1A-FAILED" and
        decision["historical_statuses_preserved"]["track_1a"] == "MGT1-TRACK1A-FAILED",
        "Track 1A remains failed")
    add(checks, "A12", "novelty verification cannot become absolute novelty",
        novelty["novelty_position"] == "N2" and novelty["claim_narrowing_required"] is True and
        "absolute novelty" not in decision["claims"]["publication_safe_summary"].lower(),
        "N2 partial-overlap/claims-narrowed position preserved")
    add(checks, "A13", "priority language cannot enter safe summaries",
        not re.search(r"first-ever|unprecedented|first analysis|previously unknown",
                      decision["claims"]["publication_safe_summary"] + decision["claims"]["resume_safe_summary"], re.I),
        "publication/resume summaries contain no priority language")

    original = load(ROOT / source["original_source"]["path"])
    original_by = {row["id"]: row for row in original["requirements"]}
    add(checks, "A14", "original mandatory classification cannot change",
        all(row["classification"] == original_by[row["id"]]["classification"]
            for row in source["requirements"]),
        "all 18 classifications match the protected original")
    add(checks, "A15", "original requirement count cannot change",
        decision["original_requirement_count"] == len(source["requirements"]) == 18,
        "exactly 18 stable rows")
    add(checks, "A16", "acceptance thresholds and fallback rule cannot change",
        source["taxonomy"]["closed_rule"] == "ALL_MANDATORY_ROWS_PASS" and
        source["taxonomy"]["mandatory_satisfying_statuses"] == ["PASS"] and
        source["taxonomy"]["closed_with_limitations_independently_authorized"] is False,
        "only PASS satisfies a mandatory row; CLOSED-WITH-LIMITATIONS unavailable")
    add(checks, "A17", "report counts cannot desynchronize from JSON",
        (BASE / "REQUIREMENT_LEDGER.md").read_text() == requirement_ledger(decision) and
        "15 PASS · 3 PARTIAL/NEGATIVE · 0 FAIL · 0 OPEN" in (BASE / "REQUIREMENT_LEDGER.md").read_text(),
        "ledger is byte-derived from the canonical decision")
    changed = decision["rows_changed_since_previous_reaudit"]
    add(checks, "A18", "changed rows cannot omit evidence paths",
        len(changed) == 3 and all(row["evidence_paths"] and
                                  all((ROOT / path).exists() for path in row["evidence_paths"])
                                  for row in changed),
        "all three current transitions have complete existing evidence chains")
    add(checks, "A19", "later campaigns cannot close wrong requirements",
        source["campaign_requirement_map"] == EXPECTED_MAP and
        evidence["campaign_requirement_map"] == EXPECTED_MAP,
        "six-campaign mapping exactly matches authorized targets")
    add(checks, "A20", "protected hashes cannot mutate",
        integrity["status"] == "INTACT" and not integrity["errors"],
        f"{integrity['trees_verified']} trees and {integrity['files_verified']} files intact")

    offline_files = [BASE / "reproduce.sh", BASE / "src/audit.py", BASE / "src/integrity.py",
                     BASE / "src/reproduction.py", BASE / "src/finalize.py"]
    offline_text = "\n".join(path.read_text() for path in offline_files if path.exists()).lower()
    forbidden_network = ("curl ", "wget ", "requests.", "urlopen", "http://", "https://")
    add(checks, "A21", "final reproducer cannot depend on network access",
        all(token not in offline_text for token in forbidden_network),
        "audit reproducer uses committed local evidence only")
    reproduction_path = BASE / "results/reproduction.json"
    reproduction = load(reproduction_path) if reproduction_path.exists() else {}
    add(checks, "A22", "generated audit artifacts must be byte-stable",
        reproduction.get("status") == "PASS" and reproduction.get("byte_stable") is True and
        reproduction.get("offline") is True,
        "reproduction record missing/not final" if not reproduction else
        f"status={reproduction.get('status')} byte_stable={reproduction.get('byte_stable')}")
    add(checks, "A23", "audit cannot claim all open research questions solved",
        "all research questions are solved" not in safe_claims.lower() and
        decision["remaining_open_nonblockers"][0]["status"] == "OPEN",
        "open SR Arb upgrade and remaining limitations are explicit")
    synthetic = derive(copy.deepcopy(source), evidence, integrity, {"L4R-01": "FAIL"})
    add(checks, "A24", "synthetic mandatory blocker cannot yield CLOSED",
        synthetic["current_verdict"] != "LEVEL-4-CLOSED" and
        any(row["id"] == "L4R-01" for row in synthetic["mandatory_blockers"]),
        f"synthetic verdict={synthetic['current_verdict']}")
    verification_path = BASE / "results/verification.json"
    verification = load(verification_path) if verification_path.exists() else {}
    add(checks, "A25", "full repository verification must pass",
        verification.get("status") == "PASS" and
        verification.get("current_distinct_checks") == 1139 and
        verification.get("level_1_3_status") == "PASS" and
        verification.get("level_4_status") == "PASS",
        "verification record missing/not final" if not verification else
        f"status={verification.get('status')} checks={verification.get('current_distinct_checks')}")
    tests_ok, tests_detail = focused_tests()
    add(checks, "A26", "focused final-audit tests must pass", tests_ok, tests_detail)

    passed = sum(row["passed"] for row in checks)
    return {
        "schema": "rebaseguard.level4-final-global-adversarial.v1",
        "passed": passed, "total": 26,
        "status": "PASS" if passed == 26 else "FAIL", "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.output:
        path = BASE / args.output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"final-audit adversarial: {result['passed']}/{result['total']} {result['status']}")
    for row in result["checks"]:
        if not row["passed"]:
            print(f"  {row['id']} FAIL: {row['name']} — {row['detail']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
