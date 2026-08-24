#!/usr/bin/env python3
"""Mechanically derive the scoped campaign and global-requirement decisions."""
from __future__ import annotations

import json

from config import BASE, PRIMARY_TASKS
from integrity import verify


def derive() -> dict:
    gates = json.loads((BASE / "results/gates.json").read_text())
    tasks = {task: json.loads((BASE / f"results/task_{task}_analysis.json").read_text())
             for task in PRIMARY_TASKS}
    support = sum(row["H2_4"]["supported"] for row in tasks.values())
    contradictions = [task for task, row in tasks.items()
                      if row["H2_3"]["strong_safety_contradiction"]]
    history_ok = not verify()
    all_gates = gates["all_primary_pass"]
    if support >= 2 and not contradictions and all_gates and history_ok:
        verdict, requirement = "EXTERNAL-VALIDATION-V2-CLOSED", "CLOSED"
    elif support == 1 and not contradictions and all_gates and history_ok:
        verdict, requirement = "EXTERNAL-VALIDATION-V2-PARTIAL", "PARTIAL"
    else:
        verdict, requirement = "EXTERNAL-VALIDATION-V2-FAILED", "UNMET"
    return {
        "schema": "rebaseguard.external-validation-v2.decision.v1",
        "decision": verdict, "global_requirement": requirement,
        "tasks_supporting_H2_4": support, "tasks_required": 2,
        "task_support": {task: row["H2_4"]["supported"] for task, row in tasks.items()},
        "strong_safety_contradictions": contradictions,
        "all_primary_gates_pass": all_gates, "historical_hashes_unchanged": history_ok,
        "historical_stage_e": "STAGE-E-PARTIAL",
        "historical_stage_e_support": "0/3 H-E5",
        "historical_stage_f": "LEVEL-4-PARTIAL",
        "post_closure_global_verdict": "LEVEL-4-PARTIAL",
        "global_reaudit_performed": False,
        "novelty_verification": "NOVELTY-VERIFICATION-CLOSED",
    }


def main() -> int:
    result = derive()
    path = BASE / "results/decision.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{result['decision']} ({result['tasks_supporting_H2_4']}/3)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
