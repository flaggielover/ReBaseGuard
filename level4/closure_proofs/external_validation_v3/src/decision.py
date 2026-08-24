#!/usr/bin/env python3
"""Derive the confirmatory scientific V3 and cross-campaign decisions."""
from __future__ import annotations

import json

from config import BASE, PRIMARY_TASKS, PROTOCOL


def derive() -> dict:
    analyses = {
        task: json.loads((BASE / f"results/task_{task}_analysis.json").read_text())
        for task in PRIMARY_TASKS
    }
    support = {task: row["H3_4"]["supported"] for task, row in analyses.items()}
    contradictions = [task for task, row in analyses.items()
                      if row["H3_3"]["strong_safety_contradiction"]]
    usable = [task for task, row in analyses.items() if row["task_verdict"] != "V3-TASK-UNUSABLE"]
    new_successes = sum(support.values())
    cross_count = 1 + new_successes
    required = PROTOCOL["aggregation"]["minimum_cross_campaign_successes"]
    original = "CLOSED" if cross_count >= required and not contradictions else "PARTIAL"
    if contradictions or not usable:
        campaign = "EXTERNAL-VALIDATION-V3-FAILED"
    elif original == "CLOSED":
        campaign = "EXTERNAL-VALIDATION-V3-CLOSED"
    else:
        campaign = "EXTERNAL-VALIDATION-V3-PARTIAL"
    return {
        "schema": "rebaseguard.external-validation-v3.scientific-decision.v1",
        "scientific_campaign_verdict": campaign,
        "original_external_validation_requirement": original,
        "v3_task_support": support,
        "v3_joint_support_count": new_successes,
        "v3_usable_task_count": len(usable),
        "cross_campaign_success_count": cross_count,
        "cross_campaign_required": required,
        "existing_cross_campaign_success": "V2 Household",
        "strong_safety_contradictions": contradictions,
        "historical_stage_e": "STAGE-E-PARTIAL",
        "historical_v2": "EXTERNAL-VALIDATION-V2-PARTIAL",
        "historical_v2_joint_support": "1/3",
        "global_reaudit_performed": False,
        "historical_global_verdict": "LEVEL-4-PARTIAL",
        "stop_rule": "NO_V4",
    }


def main() -> int:
    decision = derive()
    path = BASE / "results/scientific_decision.json"
    path.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n")
    print(decision["scientific_campaign_verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
