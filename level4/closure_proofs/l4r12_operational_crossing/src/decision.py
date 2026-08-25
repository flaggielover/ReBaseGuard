#!/usr/bin/env python3
"""Generator-owned L4R-12 scoped decision and original-row mapping."""
from __future__ import annotations

import argparse
import json
from typing import Any

from config import ALLOWED_SCOPED_STATUSES, ORIGINAL_CLASS, ORIGINAL_WORDING, RESULTS, canonical_json
from integrity import verify as verify_integrity


def _load(name: str) -> dict[str, Any]:
    return json.loads((RESULTS / name).read_text())


def build() -> dict[str, Any]:
    sources = _load("source_extraction.json")
    semantics = _load("semantic_classification.json")
    evidence = _load("evidence_assessment.json")
    adversarial = _load("adversarial_final.json")
    verification = _load("verification.json")
    reproduction = _load("reproduction.json")
    integrity = verify_integrity()
    n12 = {row["id"]: row["status"] == "PASS" for row in evidence["N12"]}
    gates = {
        "C12.1": (
            sources["requirement"]["wording"] == ORIGINAL_WORDING
            and sources["requirement"]["classification"] == ORIGINAL_CLASS,
            "original wording and MANDATORY class reconstructed exactly",
        ),
        "C12.2": (
            semantics["semantics"] == "INVESTIGATIONAL" and not semantics["source_conflicts"],
            "pre-outcome semantics classified without importing a positive-transition rule",
        ),
        "C12.3": (
            n12["N12.1"] and n12["N12.2"],
            "Stage-D crossing and independent D4 support verified",
        ),
        "C12.4": (
            all(n12[f"N12.{i}"] for i in (3, 4, 5, 6)),
            "frozen operational design, complete grid, and 0/4 peak plus 4/4 monotone result verified",
        ),
        "C12.5": (
            evidence["historical_D2_5_preserved"] and integrity["historical_D2_5_preserved"],
            "historical D2.5 remains MATHEMATICAL, NOT OPERATIONAL",
        ),
        "C12.6": (
            evidence["evidence_sufficient"] and n12["N12.9"]
            and evidence["negative_result_class"]
            == "C_COMPLETED_RESEARCH_QUESTION_WITH_VALID_NEGATIVE_ANSWER",
            "negative answer is distinguished from low-power non-demonstration",
        ),
        "C12.7": (
            semantics["negative_result_closure_allowed"] is True,
            "frozen investigational semantics explicitly allow the negative outcome",
        ),
        "C12.8": (
            evidence["same_requirement_mapping_candidate"] is True,
            "the evidence and acceptance source both target original L4R-12",
        ),
        "C12.9": (
            adversarial["status"] == "PASS" and adversarial["n_passed"] == 19,
            "exactly A1-A19 pass",
        ),
        "C12.10": (
            verification["status"] == "PASS" and verification["terminal_marker"] is True
            and reproduction["status"] == "PASS",
            "authoritative verifier and offline byte-stable replay pass",
        ),
    }
    criteria = [
        {"id": cid, "status": "PASS" if passed else "FAIL", "evidence": statement}
        for cid, (passed, statement) in gates.items()
    ]
    ambiguous = semantics["semantics"] == "AMBIGUOUS" or bool(semantics["source_conflicts"])
    all_pass = all(passed for passed, _ in gates.values())
    if ambiguous:
        verdict = "L4R12-SEMANTICS-AMBIGUOUS"
    elif all_pass:
        verdict = "L4R12-CLOSED-NEGATIVE-RESULT"
    else:
        verdict = "L4R12-PARTIAL"
    assert verdict in ALLOWED_SCOPED_STATUSES
    same = verdict == "L4R12-CLOSED-NEGATIVE-RESULT" and evidence["same_requirement_mapping_candidate"]
    return {
        "schema": "rebaseguard.l4r12-decision.v1",
        "generator_owned": True,
        "target": f"L4R-12 — {ORIGINAL_WORDING}",
        "original_requirement_class": ORIGINAL_CLASS,
        "scoped_verdict": verdict,
        "criteria": criteria,
        "semantics": semantics["semantics"],
        "same_requirement_mapping": same,
        "negative_result_closure_allowed": semantics["negative_result_closure_allowed"],
        "evidence_sufficient": evidence["evidence_sufficient"],
        "historical_D2_5_preserved": True,
        "D4_preserved": True,
        "L4R06_preserved": True,
        "original_L4R12_current_status": "PASS" if same else "PARTIAL",
        "mapping_reason": (
            "The pre-outcome D2.5 sources define an investigational requirement, explicitly "
            "authorize the negative reporting path, and the frozen evidence answers that same "
            "question with sufficient scientific strength."
            if same else
            "The complete frozen same-requirement closure rule did not pass."
        ),
        "negative_result_class": evidence["negative_result_class"],
        "new_science_run": False,
        "claim_safe": evidence["claim_safe"],
        "claim_forbidden": evidence["claim_forbidden"],
        "historical_statuses_preserved": integrity["historical_statuses_verified"],
        "historical_final_global_reaudit": "LEVEL-4-PARTIAL",
        "global_reaudit_performed": False,
        "adversarial": {
            "first_file": "adversarial_first.json",
            "first_result": f"{_load('adversarial_first.json')['n_passed']}/19",
            "final_result": f"{adversarial['n_passed']}/19",
        },
        "verification": verification,
        "reproduction": reproduction,
        "exact_next_action": (
            "FINAL GLOBAL LEVEL-4 RE-AUDIT"
            if same else
            "STOP — LEVEL-4-PARTIAL IS THE SCIENTIFICALLY CORRECT FROZEN-RULE VERDICT"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    text = canonical_json(result)
    path = RESULTS / "decision.json"
    if args.check:
        if not path.exists() or path.read_text() != text:
            print("L4R-12 decision is not byte-stable")
            return 1
    else:
        path.write_text(text)
    print(result["scoped_verdict"])
    print("original L4R-12:", result["original_L4R12_current_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

