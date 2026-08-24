#!/usr/bin/env python3
"""Mechanically derive H3-1--H3-4 from frozen V3 outcome arrays."""
from __future__ import annotations

import argparse
import json

import numpy as np

from config import BASE, PRIMARY_TASKS, PROTOCOL, task_config
from inference import mean_summary, moving_block_indices, paired_ratio


def ratio_of_ratios(a_num, a_den, b_num, b_den, *, block: int, draws: int, seed: int) -> dict:
    arrays = [np.asarray(value, float) for value in (a_num, a_den, b_num, b_den)]
    if len({value.shape for value in arrays}) != 1:
        raise ValueError("ratio-of-ratios inputs are not event-paired")
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
    draws, seed = PROTOCOL["bootstrap"]["draws"], PROTOCOL["bootstrap"]["seed"]
    natural_block = 1
    event_block = PROTOCOL["bootstrap"]["event_block"]
    effect_floor = PROTOCOL["hypotheses"]["effect_ratio_floor"]

    e1_12 = paired_ratio(natural["P1_full_reuse"]["E1_blocks"],
                         natural["P2_rebaseguard"]["E1_blocks"],
                         block=natural_block, draws=draws, seed=seed)
    e1_10 = paired_ratio(natural["P1_full_reuse"]["E1_blocks"],
                         natural["P0_fresh"]["E1_blocks"],
                         block=natural_block, draws=draws, seed=seed + 1)
    h31 = (e1_12["ratio"] >= effect_floor and e1_10["ratio"] >= effect_floor
           and e1_12["lower_97_5_one_sided"] > 1
           and e1_10["lower_97_5_one_sided"] > 1)

    e2_12 = paired_ratio(natural["P1_full_reuse"]["E2_blocks"],
                         natural["P2_rebaseguard"]["E2_blocks"],
                         block=natural_block, draws=draws, seed=seed + 2)
    e2_10 = paired_ratio(natural["P1_full_reuse"]["E2_blocks"],
                         natural["P0_fresh"]["E2_blocks"],
                         block=natural_block, draws=draws, seed=seed + 3)
    route_a = (e2_12["ratio"] >= effect_floor and e2_10["ratio"] >= effect_floor
               and e2_12["lower_97_5_one_sided"] > 1
               and e2_10["lower_97_5_one_sided"] > 1)

    events = raw["events"]["policies"]
    def response(left: str, right: str, condition: str, offset: int) -> dict:
        return ratio_of_ratios(
            events[left]["interventions"][condition]["delay"],
            events[left]["matched_in_control_wait"],
            events[right]["interventions"][condition]["delay"],
            events[right]["matched_in_control_wait"],
            block=event_block, draws=draws, seed=seed + offset,
        )

    medium_12 = response("P1_full_reuse", "P2_rebaseguard", "STEP_1.0", 4)
    medium_10 = response("P1_full_reuse", "P0_fresh", "STEP_1.0", 5)
    route_b = (medium_12["ratio"] >= effect_floor and medium_10["ratio"] >= effect_floor
               and medium_12["lower_97_5_one_sided"] > 1
               and medium_10["lower_97_5_one_sided"] > 1)
    h32 = route_a or route_b

    safety = {}
    conditions = [row["id"] for row in PROTOCOL["interventions"]]
    for offset, condition in enumerate(conditions, 10):
        value = response("P2_rebaseguard", "P0_fresh", condition, offset)
        value["excess"] = value["ratio"] - 1
        value["upper99_excess"] = value["upper_99_one_sided"] - 1
        value["lower99_excess"] = value["lower_99_one_sided"] - 1
        value["noninferior_eps_0_10"] = value["upper99_excess"] <= 0.10
        value["noninferior_eps_0_05"] = value["upper99_excess"] <= 0.05
        value["strong_contradiction"] = value["lower99_excess"] > 0.10
        safety[condition] = value
    h33 = all(value["noninferior_eps_0_10"] for value in safety.values())
    contradiction = any(value["strong_contradiction"] for value in safety.values())
    floor = PROTOCOL["power"]["minimum_effective_blocks"]
    reliable = min(e1_12["effective_blocks"], e1_10["effective_blocks"],
                   e2_12["effective_blocks"], e2_10["effective_blocks"],
                   medium_12["effective_blocks"], medium_10["effective_blocks"],
                   *(value["effective_blocks"] for value in safety.values())) >= floor
    h34 = gates["tasks"][task]["status"] == "PASS" and reliable and h31 and h32 and h33
    verdict = "V3-TASK-SUPPORTED" if h34 else "V3-TASK-NOT-SUPPORTED"
    e3, e4 = {}, {}
    for condition in conditions:
        e3[condition], e4[condition] = {}, {}
        for policy, row in events.items():
            delays = np.asarray(row["interventions"][condition]["delay"], float)
            waits = np.asarray(row["matched_in_control_wait"], float)
            e3[condition][policy] = float(delays.mean() / waits.mean())
            e4[condition][policy] = {
                "observations": mean_summary(delays, block=event_block, draws=draws, seed=seed + 50),
                "hours": float(delays.mean() / task_config(task)["observations_per_hour"]),
                "censored": int(sum(row["interventions"][condition]["censored"])),
            }
    return {
        "schema": "rebaseguard.external-validation-v3.task-analysis.v1",
        "task": task, "reliable": reliable, "task_verdict": verdict,
        "E1": {"P1_over_P2": e1_12, "P1_over_P0": e1_10},
        "E2": {"P1_over_P2": e2_12, "P1_over_P0": e2_10},
        "E3": e3, "E4": e4,
        "H3_1": {"supported": h31},
        "H3_2": {"supported": h32, "route_A_alert_burden": route_a,
                  "route_B_medium_response": route_b,
                  "medium_P1_over_P2": medium_12, "medium_P1_over_P0": medium_10},
        "H3_3": {"supported": h33, "primary_epsilon": 0.10,
                  "secondary_epsilon": 0.05, "conditions": safety,
                  "strong_safety_contradiction": contradiction},
        "H3_4": {"supported": h34},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tasks", nargs="*", default=list(PRIMARY_TASKS))
    args = parser.parse_args()
    gates = json.loads((BASE / "results/gates.json").read_text())
    for task in args.tasks:
        result = analyze_task(task, gates)
        path = BASE / f"results/task_{task}_analysis.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
        print(f"{task}: {result['task_verdict']} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
