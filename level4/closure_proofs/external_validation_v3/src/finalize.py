#!/usr/bin/env python3
"""Derive the generator-owned final V3 decision from all closure gates."""
from __future__ import annotations

import argparse
import json

from config import BASE
from integrity import verify


def derive() -> dict:
    science = json.loads((BASE / "results/scientific_decision.json").read_text())
    adversarial = json.loads((BASE / "results/adversarial_final.json").read_text())
    reproduction = json.loads((BASE / "results/reproduction.json").read_text())
    verification = json.loads((BASE / "results/verification.json").read_text())
    integrity_ok = not verify()
    closure_gates = {
        "scientific": science["scientific_campaign_verdict"] == "EXTERNAL-VALIDATION-V3-CLOSED",
        "adversarial_25_of_25": adversarial["status"] == "PASS" and adversarial["passed"] == 25,
        "byte_stable_reproduction": reproduction["status"] == "PASS" and reproduction["byte_stable"],
        "full_repository_verification": verification["status"] == "PASS" and
                                        verification["current_distinct_checks"] == 1103,
        "historical_integrity": integrity_ok,
    }
    closed = all(closure_gates.values())
    return {
        "schema": "rebaseguard.external-validation-v3.final-decision.v1",
        "final_campaign_verdict": "EXTERNAL-VALIDATION-V3-CLOSED" if closed else
                                  "EXTERNAL-VALIDATION-V3-FAILED",
        "original_external_validation_requirement":
            science["original_external_validation_requirement"] if closed else "PARTIAL",
        "closure_gates": closure_gates,
        "v3_joint_support": f"{science['v3_joint_support_count']}/2",
        "cross_campaign_success_count": science["cross_campaign_success_count"],
        "cross_campaign_required": science["cross_campaign_required"],
        "historical_stage_e": science["historical_stage_e"],
        "historical_v2": science["historical_v2"],
        "historical_v2_joint_support": science["historical_v2_joint_support"],
        "historical_global_verdict": science["historical_global_verdict"],
        "global_reaudit_performed": False,
        "next_action": "FINAL GLOBAL LEVEL-4 RE-AUDIT" if closed else "HUMAN GLOBAL SCIENTIFIC DECISION",
        "stop_rule": "NO_V4",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(derive(), indent=2, sort_keys=True) + "\n"
    path = BASE / "results/decision.json"
    if args.check:
        passed = path.exists() and path.read_text() == content
        print(f"final decision: {'byte-stable' if passed else 'STALE'}")
        return 0 if passed else 1
    path.write_text(content)
    print(json.loads(content)["final_campaign_verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
