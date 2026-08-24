#!/usr/bin/env python3
"""Build the canonical final-JSON source for V3 reports and figures."""
from __future__ import annotations

import json

from config import BASE, PRIMARY_TASKS, protocol_digest


def status(value: bool | None) -> str:
    return "SUPPORTED" if value is True else "NOT_SUPPORTED" if value is False else "UNEVALUABLE"


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
    v2_protocol = json.loads((BASE.parent / "external_validation_v2/results/protocol_hash.json").read_text())
    stage_e = json.loads((BASE.parents[1] / "stage_e/results/stage_e_decision.json").read_text())
    cross_tasks = []
    for key, row in stage_e["per_task"].items():
        hypotheses = row["hypotheses"]
        reference = hypotheses["H_E1"]["status"]
        operational = (hypotheses["H_E2"]["status"].startswith("SUPPORTED") or
                       hypotheses["H_E4"]["status"].startswith("SUPPORTED"))
        safety = hypotheses["H_E3"]["status"].startswith("SUPPORTED")
        cross_tasks.append({
            "id": f"stage_e_{key}", "display": row["dataset"], "campaign": "Stage E",
            "protocol": stage_e["protocol_sha256_actual"], "usability": row["usability"],
            "minimum_effective_blocks": min(row["effective_blocks"].values()),
            "reference_distortion": reference.replace(" ", "_"),
            "operational_consequence": status(operational), "p2_safety": status(safety),
            "joint_support": False, "counts_toward_closure": False,
        })
    v2_names = {"household": "Household power", "metro": "Metro traffic",
                "beijing": "Beijing PM2.5"}
    for key, row in v2["tasks"].items():
        cross_tasks.append({
            "id": f"v2_{key}", "display": v2_names[key], "campaign": "V2",
            "protocol": v2_protocol["combined_sha256"], "usability": "USABLE",
            "minimum_effective_blocks": min(row["power"][value]
                                              for value in ("calibration_cycle_blocks", "event_blocks", "natural_week_blocks")),
            "reference_distortion": status(row["H2_1"]["supported"]),
            "operational_consequence": status(row["H2_2"]["supported"]),
            "p2_safety": status(row["H2_3"]["supported"]),
            "joint_support": row["H2_4"]["supported"],
            "counts_toward_closure": row["H2_4"]["supported"],
        })
    v3_names = {"metropt": "MetroPT-3 compressor", "retail": "Online Retail II"}
    for key, value in tasks.items():
        row = value["analysis"]
        power = value["power"]
        cross_tasks.append({
            "id": f"v3_{key}", "display": v3_names[key], "campaign": "V3",
            "protocol": protocol_digest(), "usability": "USABLE",
            "minimum_effective_blocks": min(power["calibration_cycle_blocks"],
                                              power["event_blocks"], power["natural_blocks"]),
            "reference_distortion": status(row["H3_1"]["supported"]),
            "operational_consequence": status(row["H3_2"]["supported"]),
            "p2_safety": status(row["H3_3"]["supported"]),
            "joint_support": row["H3_4"]["supported"],
            "counts_toward_closure": row["H3_4"]["supported"],
        })
    output = {
        "schema": "rebaseguard.external-validation-v3.summary.v1",
        "decision": decision,
        "tasks": tasks,
        "historical": {
            "stage_e": {"decision": stage_e["decision"], "support": "0/3",
                        "per_task": stage_e["per_task"]},
            "v2": {"decision": v2_decision["decision"],
                   "support": v2_decision["tasks_supporting_H2_4"],
                   "required": v2_decision["tasks_required"], "tasks": v2["tasks"]},
        },
        "cross_campaign_tasks": cross_tasks,
        "figure_source_only": True,
    }
    path = BASE / "results/summary.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
