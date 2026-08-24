#!/usr/bin/env python3
"""Build the single final JSON consumed by reports and figures."""
from __future__ import annotations

import json

import numpy as np

from config import BASE, EXECUTION, PRIMARY_TASKS, PROTOCOL
from inference import mean_summary


def build_summary() -> dict:
    decision = json.loads((BASE / "results/decision.json").read_text())
    gates = json.loads((BASE / "results/gates.json").read_text())
    draws, seed = PROTOCOL["bootstrap"]["draws"], PROTOCOL["bootstrap"]["seed"]
    week_block = EXECUTION["bootstrap"]["natural_moving_block_weeks"]
    tasks = {}
    for task in PRIMARY_TASKS:
        raw = json.loads((BASE / f"results/task_{task}_confirmatory.json").read_text())
        analysis = json.loads((BASE / f"results/task_{task}_analysis.json").read_text())
        natural = raw["natural"]["policies"]
        e2, e3 = {}, {}
        for offset, policy in enumerate(PROTOCOL["policies"]):
            e2[policy] = mean_summary(natural[policy]["E2_weekly"], block=week_block,
                                      draws=draws, seed=seed + 100 + offset)
            e3[policy] = mean_summary(natural[policy]["E3_weekly"], block=week_block,
                                      draws=draws, seed=seed + 110 + offset)
        events = raw["events"]["policies"]
        e1 = {}
        for condition in analysis["E1"]:
            e1[condition] = {}
            for offset, policy in enumerate(PROTOCOL["policies"]):
                delay = np.asarray(events[policy]["interventions"][condition]["delay"], float)
                wait = np.asarray(events[policy]["matched_in_control_wait"], float)
                from analyze import ratio_of_ratios
                # Ratio to an identical all-ones reference yields the policy's
                # normalized response with the same paired event bootstrap.
                ones = np.ones_like(delay)
                value = ratio_of_ratios(delay, wait, ones, ones,
                                        block=PROTOCOL["bootstrap"]["event_block"],
                                        draws=draws, seed=seed + 120 + offset)
                e1[condition][policy] = value
        tasks[task] = {
            "n": gates["tasks"][task]["n"],
            "power": gates["tasks"][task]["actual_power"],
            "calibration": gates["tasks"][task]["calibration"],
            "E1": e1, "E2": e2, "E3": e3, "E4": analysis["E4"],
            "H2_1": analysis["H2_1"], "H2_2": analysis["H2_2"],
            "H2_3": analysis["H2_3"], "H2_4": analysis["H2_4"],
            "reference_ratios": analysis["E2"],
            "alert_burden_ratio": analysis["E3"]["P1_over_P2"],
        }
    return {
        "schema": "rebaseguard.external-validation-v2.final-summary.v1",
        "decision": decision, "tasks": tasks,
        "figure_source_only": True,
    }


def main() -> int:
    result = build_summary()
    path = BASE / "results/summary.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
