#!/usr/bin/env python3
"""Build the canonical final-JSON source for V3 reports and figures."""
from __future__ import annotations

import json

from config import BASE, PRIMARY_TASKS


def main() -> int:
    gates = json.loads((BASE / "results/gates.json").read_text())
    decision = json.loads((BASE / "results/scientific_decision.json").read_text())
    tasks = {}
    for task in PRIMARY_TASKS:
        analysis = json.loads((BASE / f"results/task_{task}_analysis.json").read_text())
        tasks[task] = {
            "calibration": gates["tasks"][task]["calibration"],
            "power": gates["tasks"][task]["actual_power"],
            "residual_diagnostics": gates["tasks"][task]["calibration_residual_diagnostics"],
            "analysis": analysis,
        }
    v2 = json.loads((BASE.parent / "external_validation_v2/results/summary.json").read_text())
    v2_decision = v2["decision"]
    stage_e = json.loads((BASE.parents[1] / "stage_e/results/stage_e_decision.json").read_text())
    output = {
        "schema": "rebaseguard.external-validation-v3.summary.v1",
        "decision": decision,
        "tasks": tasks,
        "historical": {
            "stage_e": {"decision": stage_e["decision"], "support": "0/3"},
            "v2": {"decision": v2_decision["decision"],
                   "support": v2_decision["tasks_supporting_H2_4"],
                   "required": v2_decision["tasks_required"], "tasks": v2["tasks"]},
        },
    }
    path = BASE / "results/summary.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
