#!/usr/bin/env python3
"""Exactly A1-A19 for the isolated L4R-12 closure audit."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from config import (
    NEGATIVE_VERDICT,
    ORIGINAL_CLASS,
    ORIGINAL_WORDING,
    PRIMARY_METRICS,
    RESULTS,
    ROOT,
    canonical_json,
)
from integrity import verify as verify_integrity


def _load(name: str) -> dict[str, Any]:
    path = RESULTS / name
    return json.loads(path.read_text()) if path.exists() else {}


def _focused_tests() -> tuple[bool, str]:
    proc = subprocess.run(
        [str(ROOT / "level4/.venv/bin/python"), "-m", "pytest",
         "level4/closure_proofs/l4r12_operational_crossing/tests", "-q"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    match = re.search(r"(\d+) passed", proc.stdout)
    detail = f"{match.group(1)} focused tests passed" if match else proc.stdout[-500:]
    return proc.returncode == 0, detail


def run() -> dict[str, Any]:
    sources = _load("source_extraction.json")
    semantics = _load("semantic_classification.json")
    evidence = _load("evidence_assessment.json")
    verification = _load("verification.json")
    reproduction = _load("reproduction.json")
    decision = _load("decision.json")
    integrity = verify_integrity()
    focused_ok, focused_detail = _focused_tests()
    n12 = {row["id"]: row for row in evidence.get("N12", [])}
    checks: list[dict[str, Any]] = []

    def add(cid: str, name: str, passed: bool, evidence_text: str) -> None:
        checks.append({
            "id": cid,
            "check": name,
            "passed": bool(passed),
            "evidence": evidence_text,
        })

    statuses = integrity.get("historical_statuses_verified", {})
    add("A1", "Stage D unchanged",
        integrity.get("status") == "PASS" and statuses.get("stage_d") == "STAGE-D-PARTIAL",
        "protected Stage-D tree/files match; STAGE-D-PARTIAL preserved")
    add("A2", "D2.5 preserved",
        integrity.get("historical_D2_5_preserved") is True
        and evidence.get("historical_verdict") == NEGATIVE_VERDICT,
        "historical D2.5 remains MATHEMATICAL, NOT OPERATIONAL")
    add("A3", "D4 unchanged",
        integrity.get("D4_preserved") is True,
        "protected D4 tree/files match; D4-PHASE-MAP-CLOSED preserved")
    add("A4", "L4R-06 closure unchanged",
        integrity.get("L4R06_preserved") is True,
        "protected L4R-06 tree/decision match; L4R06-POLICY-CLOSED preserved")
    design = evidence.get("operational_design", {})
    add("A5", "no new m grid",
        evidence.get("mode") == "AUDIT_REPLAY_ONLY_NO_NEW_SCIENCE"
        and design.get("m_values") == [10, 20, 50, 65, 75, 90, 100],
        f"historical D2.5 m grid retained: {design.get('m_values')}")
    add("A6", "no new metric search",
        design.get("primary_metrics") == list(PRIMARY_METRICS)
        and design.get("R_delta_reported") is True,
        "four frozen localization metrics plus the historically reported R_delta are retained")
    taxonomy = semantics.get("taxonomy_audit", {})
    add("A7", "no post-outcome taxonomy change",
        sources.get("requirement", {}).get("stage_f") == {"status": "PARTIAL", "label": "NEGATIVE RESULT"}
        and taxonomy.get("later_normalized_status") == "PARTIAL",
        "historical NEGATIVE RESULT/PARTIAL remains verbatim; only a later isolated mapping is evaluated")
    separations = evidence.get("operational_result", {}).get("m65_vs_m75_combined_separation", {})
    add("A8", "no absence-of-significance negative proof",
        bool(separations) and min(separations.values()) > 3,
        f"smooth across-crossing changes are resolved: combined-SE separations={separations}")
    add("A9", "low-power alternative explicitly checked",
        n12.get("N12.9", {}).get("status") == "PASS"
        and evidence.get("negative_result_class")
        == "C_COMPLETED_RESEARCH_QUESTION_WITH_VALID_NEGATIVE_ANSWER",
        "N12.9 passes using 20,000 replicates, resolved smooth changes, and the prior scientific-validity audit")
    add("A10", "original wording cited",
        sources.get("requirement", {}).get("wording") == ORIGINAL_WORDING
        and sources.get("requirement", {}).get("classification") == ORIGINAL_CLASS,
        f"{ORIGINAL_WORDING} [{ORIGINAL_CLASS}]")
    mapping_explicit = isinstance(evidence.get("same_requirement_mapping_candidate"), bool)
    if decision:
        mapping_explicit = mapping_explicit and isinstance(decision.get("same_requirement_mapping"), bool)
    add("A11", "same-requirement mapping explicit", mapping_explicit,
        f"audit candidate={evidence.get('same_requirement_mapping_candidate')}; final decision present={bool(decision)}")
    safe_claim = evidence.get("claim_safe", "")
    add("A12", "no universal no-effect claim",
        "under the frozen" in safe_claim and "in general" not in safe_claim,
        "generator claim is limited to the frozen protocol and metrics")
    add("A13", "no operational-transition claim",
        "no corresponding operational transition was found" in safe_claim
        and evidence.get("historical_verdict") == NEGATIVE_VERDICT,
        "the crossing is not relabeled as an operational phase transition")
    add("A14", "no historical negative result erased",
        evidence.get("historical_D2_5_preserved") is True
        and statuses.get("stage_d_D2_5") == NEGATIVE_VERDICT,
        "negative result appears in both historical integrity and derived evidence")
    add("A15", "no Final Global Re-audit rewritten",
        statuses.get("final_global_current") == "LEVEL-4-PARTIAL"
        and statuses.get("final_global_historical_stage_f") == "LEVEL-4-PARTIAL",
        "protected Final Global Re-audit remains LEVEL-4-PARTIAL")
    add("A16", "protected hashes intact",
        integrity.get("status") == "PASS",
        f"{integrity.get('trees_verified')} trees and {integrity.get('files_verified')} files verified")
    add("A17", "focused tests green", focused_ok, focused_detail)
    add("A18", "repository verifier green",
        verification.get("status") == "PASS" and verification.get("terminal_marker") is True,
        f"verification status={verification.get('status', 'MISSING')}")
    add("A19", "reproducer byte-stable",
        reproduction.get("status") == "PASS"
        and reproduction.get("audit_artifacts_byte_stable") is True,
        f"reproduction status={reproduction.get('status', 'MISSING')}")
    assert [row["id"] for row in checks] == [f"A{i}" for i in range(1, 20)]
    passed = sum(row["passed"] for row in checks)
    return {
        "schema": "rebaseguard.l4r12-adversarial.v1",
        "n_checks": 19,
        "n_passed": passed,
        "status": "PASS" if passed == 19 else "FAIL",
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", choices=("first", "final"))
    parser.add_argument("--check-final", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.check_final:
        path = RESULTS / "adversarial_final.json"
        if not path.exists() or json.loads(path.read_text()) != result:
            print("L4R-12 final adversarial record is not reproducible")
            return 1
    elif args.label:
        (RESULTS / f"adversarial_{args.label}.json").write_text(canonical_json(result))
    else:
        parser.error("choose --label or --check-final")
    print(f"L4R-12 adversarial: {result['n_passed']}/{result['n_checks']} {result['status']}")
    for row in result["checks"]:
        if not row["passed"]:
            print(f"  {row['id']} FAIL: {row['check']}")
    return 0 if args.label == "first" or result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

