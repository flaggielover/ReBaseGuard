#!/usr/bin/env python3
"""Run matched confirmatory outcomes only after every frozen gate passes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from config import BASE, EXECUTION, POLICIES, PRIMARY_TASKS, PROTOCOL, task_time
from datasets import LOADERS
from model import build
from monitor import first_alarm_delay, run_monitor


def centered_mean(values: np.ndarray, window: int) -> np.ndarray:
    result = np.full(values.size, np.nan)
    left = window // 2
    right = window - left
    cumulative = np.concatenate([[0.0], np.cumsum(values)])
    index = np.arange(left, values.size - right + 1)
    result[index] = (cumulative[index + right] - cumulative[index - left]) / window
    return result


def event_grid(task: str, evaluation_size: int) -> np.ndarray:
    count = PROTOCOL["events"]["count"]
    target = task_time(task)["target_arl"]
    warmup = EXECUTION["events"]["warmup_target_arl"] * target
    cap = EXECUTION["events"]["administrative_cap_target_arl"] * target
    low = max(int(np.ceil(PROTOCOL["events"]["region"][0] * evaluation_size)), warmup + PROTOCOL["detector"]["m"])
    high = min(int(np.floor(PROTOCOL["events"]["region"][1] * evaluation_size)), evaluation_size - cap - 1)
    if high - low + 1 < count:
        raise ValueError(f"{task}: evaluation cannot hold {count} event locations")
    base = np.linspace(low, high, count)
    spacing = float((high - low) / (count - 1))
    rng = np.random.default_rng(EXECUTION["events"]["task_seeds"][task])
    jitter = rng.uniform(-1, 1, count) * EXECUTION["events"]["grid_jitter_fraction_of_spacing"] * spacing
    jitter[[0, -1]] = 0.0
    grid = np.rint(base + jitter).astype(int)
    grid[0], grid[-1] = low, high
    for index in range(1, grid.size):
        grid[index] = max(grid[index], grid[index - 1] + 1)
    if grid[-1] > high:
        raise ValueError(f"{task}: jittered grid lost uniqueness")
    return grid


def inject(segment: np.ndarray, onset: int, condition: str, scale: float,
           observations_per_hour: int) -> np.ndarray:
    output = segment.copy()
    n = output.size - onset
    if condition.startswith("STEP_"):
        magnitude = float(condition.split("_", 1)[1])
        output[onset:] += magnitude * scale
    elif condition == "GRADUAL_1.0":
        duration = 24 * observations_per_hour
        delta = np.minimum(np.arange(n) / max(1, duration), 1.0)
        output[onset:] += delta * scale
    elif condition == "RECURRING_1.0":
        period = 48 * observations_per_hour
        delta = ((np.arange(n) // period) % 2 == 0).astype(float)
        output[onset:] += delta * scale
    else:
        raise ValueError(condition)
    return output


def natural_blocks(stream, threshold: float) -> dict:
    lo, hi = stream.evaluation.start, stream.evaluation.stop
    residual = stream.residual
    m = PROTOCOL["detector"]["m"]
    initial = float(residual[lo - m:lo].mean())
    runs = {
        name: run_monitor(residual, scale=stream.scale, threshold=threshold,
                          rho=rho, r0=initial, start=lo, stop=hi,
                          k=PROTOCOL["detector"]["k"], m=m)
        for name, rho in POLICIES.items()
    }
    burn = EXECUTION["monitor"]["burn_cycles_natural"]
    cuts = []
    for run in runs.values():
        if len(run.cycles) < burn:
            raise ValueError(f"{stream.task}: fewer than {burn} natural cycles")
        cuts.append(run.cycles[burn - 1].alarm + 1 + m)
    common = max(cuts)
    week = task_time(stream.task)["week"]
    n_weeks = (hi - common) // week
    stop = common + n_weeks * week
    obs_per_hour = task_time(stream.task)["observations_per_hour"]
    oracle = centered_mean(residual[lo:hi], 24 * obs_per_hour)
    output = {}
    for name, run in runs.items():
        refs = run.reference_path[common - lo:stop - lo]
        truth = oracle[common - lo:stop - lo]
        distortion = np.abs(refs - truth) / stream.scale
        alarms = run.alarms
        e2, e3 = [], []
        for block in range(n_weeks):
            begin = common + block * week
            end = begin + week
            local = distortion[block * week:(block + 1) * week]
            e2.append(float(np.nanmean(local)))
            e3.append(float(1000 * np.sum((alarms >= begin) & (alarms < end)) / week))
        output[name] = {
            "E2_weekly": e2, "E3_weekly": e3,
            "n_cycles": len(run.cycles),
            "reference_acf1": _acf1([cycle.reference for cycle in run.cycles[burn:]]),
            "alarm_direction_acf1": _acf1([cycle.direction for cycle in run.cycles[burn:]]),
        }
    return {"common_scoring_start": common, "full_week_blocks": n_weeks,
            "week_observations": week, "policies": output}


def _acf1(values) -> float:
    values = np.asarray(values, float)
    if values.size < 3:
        return float("nan")
    values -= values.mean()
    denominator = float(values @ values)
    return float(values[:-1] @ values[1:] / denominator) if denominator else float("nan")


def event_outcomes(stream, threshold: float) -> dict:
    lo, hi = stream.evaluation.start, stream.evaluation.stop
    residual = stream.residual
    relative_grid = event_grid(stream.task, hi - lo)
    grid = relative_grid + lo
    time = task_time(stream.task)
    target, obs_per_hour = time["target_arl"], time["observations_per_hour"]
    warmup = EXECUTION["events"]["warmup_target_arl"] * target
    cap = EXECUTION["events"]["administrative_cap_target_arl"] * target
    m = PROTOCOL["detector"]["m"]
    conditions = [row["id"] for row in PROTOCOL["interventions"]]
    policies = {}
    for name, rho in POLICIES.items():
        matched, matched_censored = [], []
        drift = {condition: {"delay": [], "censored": []} for condition in conditions}
        for onset in grid:
            start, stop = int(onset - warmup), int(onset + cap + 1)
            initial = float(residual[start - m:start].mean())
            base = residual[start:stop]
            local_onset = int(onset - start)
            natural = run_monitor(base, scale=stream.scale, threshold=threshold,
                                  rho=rho, r0=initial, k=PROTOCOL["detector"]["k"], m=m)
            delay, censored = first_alarm_delay(natural, local_onset, cap)
            matched.append(delay); matched_censored.append(censored)
            for condition in conditions:
                changed = inject(base, local_onset, condition, stream.scale, obs_per_hour)
                run = run_monitor(changed, scale=stream.scale, threshold=threshold,
                                  rho=rho, r0=initial, k=PROTOCOL["detector"]["k"], m=m)
                delay, censored = first_alarm_delay(run, local_onset, cap)
                drift[condition]["delay"].append(delay)
                drift[condition]["censored"].append(censored)
        policies[name] = {
            "matched_in_control_wait": matched,
            "matched_in_control_censored": matched_censored,
            "interventions": drift,
        }
    return {"relative_grid": relative_grid.tolist(), "absolute_grid": grid.tolist(),
            "warmup": warmup, "cap": cap, "policies": policies}


def run_task(task: str, gates: dict) -> dict:
    if not gates["all_primary_pass"]:
        raise RuntimeError("confirmatory run prohibited: not all primary gates pass")
    gate = gates["tasks"][task]
    if gate["status"] != "PASS":
        raise RuntimeError(f"confirmatory run prohibited: {task} gate failed")
    stream = build(LOADERS[task]())
    threshold = gate["calibration"]["threshold"]
    residual_hash = hashlib.sha256(stream.residual.astype("<f8").tobytes()).hexdigest()
    return {
        "schema": "rebaseguard.external-validation-v2.task-confirmatory.v1",
        "task": task, "evidence_status": "CONFIRMATORY",
        "protocol_hash": gates["protocol_hash"], "threshold": threshold,
        "residual_sha256_float64_le": residual_hash,
        "split": gate["split"], "scale": stream.scale,
        "matched_streams": True, "natural": natural_blocks(stream, threshold),
        "events": event_outcomes(stream, threshold),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tasks", nargs="*", default=list(PRIMARY_TASKS))
    args = parser.parse_args()
    gates_path = BASE / "results/gates.json"
    if not gates_path.exists():
        raise SystemExit("missing pre-outcome results/gates.json")
    gates = json.loads(gates_path.read_text())
    for task in args.tasks:
        result = run_task(task, gates)
        path = BASE / f"results/task_{task}_confirmatory.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"{task}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
