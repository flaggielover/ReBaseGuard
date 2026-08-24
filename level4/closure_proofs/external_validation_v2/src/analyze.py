#!/usr/bin/env python3
"""Mechanically derive task hypotheses from frozen confirmatory arrays."""
from __future__ import annotations

import argparse
import json

import numpy as np

from config import BASE, EXECUTION, PRIMARY_TASKS, PROTOCOL, task_time
from inference import mean_summary, paired_ratio


def ratio_of_ratios(a_num, a_den, b_num, b_den, *, block, draws, seed) -> dict:
    arrays = [np.asarray(x, float) for x in (a_num, a_den, b_num, b_den)]
    if len({x.shape for x in arrays}) != 1:
        raise ValueError("ratio-of-ratios inputs are not event-paired")
    from inference import moving_block_indices
    index = moving_block_indices(arrays[0].size, block, draws, np.random.default_rng(seed))
    samples = ((arrays[0][index].mean(axis=1) / arrays[1][index].mean(axis=1)) /
               (arrays[2][index].mean(axis=1) / arrays[3][index].mean(axis=1)))
    point = float((arrays[0].mean() / arrays[1].mean()) /
                  (arrays[2].mean() / arrays[3].mean()))
    return {
        "ratio": point,
        "ci95": [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))],
        "lower_97_5_one_sided": float(np.quantile(samples, 0.025)),
        "upper_97_5_one_sided": float(np.quantile(samples, 0.975)),
        "lower_99_one_sided": float(np.quantile(samples, 0.01)),
        "upper_99_one_sided": float(np.quantile(samples, 0.99)),
        "n": int(arrays[0].size), "block": block,
        "effective_blocks": int(arrays[0].size // block),
        "pairing": "same event index across policy and intervention/control",
    }


def analyze_task(task: str, gates: dict) -> dict:
    raw = json.loads((BASE / f"results/task_{task}_confirmatory.json").read_text())
    natural = raw["natural"]["policies"]
    block_week = EXECUTION["bootstrap"]["natural_moving_block_weeks"]
    draws, seed = PROTOCOL["bootstrap"]["draws"], PROTOCOL["bootstrap"]["seed"]
    event_block = PROTOCOL["bootstrap"]["event_block"]
    e2_12 = paired_ratio(natural["P1_full_reuse"]["E2_weekly"],
                         natural["P2_rebaseguard"]["E2_weekly"],
                         block=block_week, draws=draws, seed=seed)
    e2_10 = paired_ratio(natural["P1_full_reuse"]["E2_weekly"],
                         natural["P0_fresh"]["E2_weekly"],
                         block=block_week, draws=draws, seed=seed + 1)
    effect_floor = PROTOCOL["hypotheses"]["effect_ratio_floor"]
    h21 = (e2_12["ratio"] >= effect_floor and e2_10["ratio"] >= effect_floor
           and e2_12["lower_97_5_one_sided"] > 1
           and e2_10["lower_97_5_one_sided"] > 1)
    burden = paired_ratio(natural["P1_full_reuse"]["E3_weekly"],
                          natural["P2_rebaseguard"]["E3_weekly"],
                          block=block_week, draws=draws, seed=seed + 2)
    events = raw["events"]["policies"]

    def rr(left: str, right: str, condition: str, offset: int) -> dict:
        return ratio_of_ratios(
            events[left]["interventions"][condition]["delay"],
            events[left]["matched_in_control_wait"],
            events[right]["interventions"][condition]["delay"],
            events[right]["matched_in_control_wait"],
            block=event_block, draws=draws, seed=seed + offset,
        )

    medium = rr("P1_full_reuse", "P2_rebaseguard", "STEP_1.0", 3)
    burden_route = burden["ratio"] >= effect_floor and burden["lower_97_5_one_sided"] > 1
    response_route = medium["ratio"] >= effect_floor and medium["lower_97_5_one_sided"] > 1
    h22 = burden_route or response_route
    safety = {}
    conditions = [row["id"] for row in PROTOCOL["interventions"]]
    for offset, condition in enumerate(conditions, 10):
        value = rr("P2_rebaseguard", "P0_fresh", condition, offset)
        value["excess"] = value["ratio"] - 1
        value["upper99_excess"] = value["upper_99_one_sided"] - 1
        value["lower99_excess"] = value["lower_99_one_sided"] - 1
        value["noninferior_eps_0_10"] = value["upper99_excess"] <= 0.10
        value["noninferior_eps_0_05"] = value["upper99_excess"] <= 0.05
        value["strong_contradiction"] = value["lower99_excess"] > 0.10
        safety[condition] = value
    h23 = all(row["noninferior_eps_0_10"] for row in safety.values())
    contradiction = any(row["strong_contradiction"] for row in safety.values())
    floor = PROTOCOL["power"]["minimum_effective_blocks"]
    reliable = min(e2_12["effective_blocks"], e2_10["effective_blocks"],
                   burden["effective_blocks"], medium["effective_blocks"],
                   *(row["effective_blocks"] for row in safety.values())) >= floor
    h24 = gates["tasks"][task]["status"] == "PASS" and reliable and h21 and h22 and h23
    e1 = {}
    e4 = {}
    for condition in conditions:
        e1[condition] = {}
        e4[condition] = {}
        for policy, row in events.items():
            delays = np.asarray(row["interventions"][condition]["delay"], float)
            waits = np.asarray(row["matched_in_control_wait"], float)
            e1[condition][policy] = float(delays.mean() / waits.mean())
            e4[condition][policy] = {
                "observations": mean_summary(delays, block=event_block, draws=draws, seed=seed + 50),
                "hours": float(delays.mean() / task_time(task)["observations_per_hour"]),
                "censored": int(sum(row["interventions"][condition]["censored"])),
            }
    return {
        "schema": "rebaseguard.external-validation-v2.task-analysis.v1",
        "task": task, "gates": gates["tasks"][task]["gates"],
        "reliable": reliable,
        "E1": e1, "E2": {"P1_over_P2": e2_12, "P1_over_P0": e2_10},
        "E3": {"P1_over_P2": burden}, "E4": e4,
        "H2_1": {"supported": h21},
        "H2_2": {"supported": h22, "alert_burden_route": burden_route,
                  "medium_step_response_route": response_route,
                  "medium_step_P1_over_P2": medium},
        "H2_3": {"supported": h23, "primary_epsilon": 0.10,
                  "secondary_epsilon": 0.05, "conditions": safety,
                  "strong_safety_contradiction": contradiction},
        "H2_4": {"supported": h24},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tasks", nargs="*", default=list(PRIMARY_TASKS))
    args = parser.parse_args()
    gates = json.loads((BASE / "results/gates.json").read_text())
    for task in args.tasks:
        result = analyze_task(task, gates)
        path = BASE / f"results/task_{task}_analysis.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"{task}: H2-4={result['H2_4']['supported']} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
