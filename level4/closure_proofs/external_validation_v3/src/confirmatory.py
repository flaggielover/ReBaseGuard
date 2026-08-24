#!/usr/bin/env python3
"""Generate matched V3 outcomes only after the committed P0 gates pass."""
from __future__ import annotations

import argparse
import hashlib
import json

import numpy as np

from config import BASE, EXECUTION, POLICIES, PRIMARY_TASKS, PROTOCOL, protocol_digest, task_config
from datasets import LOADERS
from model import build
from monitor import first_alarm_delay, run_monitor


def centered_mean(values: np.ndarray, window: int) -> np.ndarray:
    output = np.full(values.size, np.nan)
    left, right = window // 2, window - window // 2
    cumulative = np.concatenate([[0.0], np.cumsum(values)])
    index = np.arange(left, values.size - right + 1)
    output[index] = (cumulative[index + right] - cumulative[index - left]) / window
    return output


def event_grid(task: str, evaluation_size: int) -> np.ndarray:
    count = PROTOCOL["events"]["count"]
    target = task_config(task)["target_arl"]
    warmup = PROTOCOL["events"]["warmup_target_arl"] * target
    cap = PROTOCOL["events"]["administrative_cap_target_arl"] * target
    low = max(int(np.ceil(PROTOCOL["events"]["region"][0] * evaluation_size)),
              warmup + PROTOCOL["detector"]["m"])
    high = min(int(np.floor(PROTOCOL["events"]["region"][1] * evaluation_size)),
               evaluation_size - cap - 1)
    if high - low + 1 < count:
        raise ValueError(f"{task}: evaluation cannot hold {count} unique events")
    base = np.linspace(low, high, count)
    spacing = float((high - low) / (count - 1))
    rng = np.random.default_rng(EXECUTION["events"]["task_seeds"][task])
    jitter = rng.uniform(-1, 1, count) * EXECUTION["events"]["grid_jitter_fraction_of_spacing"] * spacing
    jitter[[0, -1]] = 0
    grid = np.rint(base + jitter).astype(int)
    grid[0], grid[-1] = low, high
    for index in range(1, grid.size):
        grid[index] = max(grid[index], grid[index - 1] + 1)
    if grid[-1] > high:
        raise ValueError(f"{task}: jittered event grid lost uniqueness")
    return grid


def inject(segment: np.ndarray, onset: int, condition: str, scale: float,
           observations_per_hour: int) -> np.ndarray:
    output = segment.copy()
    length = output.size - onset
    if condition.startswith("STEP_"):
        output[onset:] += float(condition.split("_", 1)[1]) * scale
    elif condition == "GRADUAL_1.0":
        duration = 24 * observations_per_hour
        output[onset:] += np.minimum(np.arange(length) / max(1, duration), 1) * scale
    elif condition == "RECURRING_1.0":
        on = 48 * observations_per_hour
        period = 96 * observations_per_hour
        output[onset:] += ((np.arange(length) % period) < on).astype(float) * scale
    else:
        raise ValueError(condition)
    return output


def _acf1(values) -> float:
    values = np.asarray(values, float)
    if values.size < 3:
        return float("nan")
    values -= values.mean()
    denominator = float(values @ values)
    return float(values[:-1] @ values[1:] / denominator) if denominator else 0.0


def natural_blocks(stream, threshold: float) -> dict:
    lo, hi = stream.evaluation.start, stream.evaluation.stop
    m = PROTOCOL["detector"]["m"]
    initial = float(stream.residual[lo - m:lo].mean())
    runs = {
        policy: run_monitor(stream.residual, scale=stream.scale, threshold=threshold,
                            rho=rho, r0=initial, start=lo, stop=hi,
                            k=PROTOCOL["detector"]["k"], m=m)
        for policy, rho in POLICIES.items()
    }
    burn = EXECUTION["monitor"]["burn_cycles_natural"]
    cuts = []
    for run in runs.values():
        if len(run.cycles) < burn:
            raise ValueError(f"{stream.task}: fewer than {burn} natural cycles")
        cuts.append(run.cycles[burn - 1].alarm + 1 + m)
    common = max(cuts)
    block_size = task_config(stream.task)["natural_block_observations"]
    n_blocks = (hi - common) // block_size
    stop = common + n_blocks * block_size
    hours = task_config(stream.task)["observations_per_hour"]
    oracle = centered_mean(stream.residual[lo:hi], 24 * hours)
    output = {}
    for policy, run in runs.items():
        reference = run.reference_path[common - lo:stop - lo]
        truth = oracle[common - lo:stop - lo]
        distortion = np.abs(reference - truth) / stream.scale
        alarms = run.alarms
        e1, e2 = [], []
        for block in range(n_blocks):
            begin = common + block * block_size
            end = begin + block_size
            local = distortion[block * block_size:(block + 1) * block_size]
            e1.append(float(np.nanmean(local)))
            e2.append(float(1000 * np.sum((alarms >= begin) & (alarms < end)) / block_size))
        output[policy] = {
            "E1_blocks": e1,
            "E2_blocks": e2,
            "n_cycles": len(run.cycles),
            "reference_acf1": _acf1([cycle.reference for cycle in run.cycles[burn:]]),
            "alarm_direction_acf1": _acf1([cycle.direction for cycle in run.cycles[burn:]]),
        }
    return {"common_scoring_start": common, "complete_blocks": n_blocks,
            "block_observations": block_size, "policies": output}


def event_outcomes(stream, threshold: float) -> dict:
    lo, hi = stream.evaluation.start, stream.evaluation.stop
    residual = stream.residual
    relative = event_grid(stream.task, hi - lo)
    absolute = relative + lo
    config = task_config(stream.task)
    target = config["target_arl"]
    observations_per_hour = config["observations_per_hour"]
    warmup = PROTOCOL["events"]["warmup_target_arl"] * target
    cap = PROTOCOL["events"]["administrative_cap_target_arl"] * target
    m = PROTOCOL["detector"]["m"]
    conditions = [row["id"] for row in PROTOCOL["interventions"]]
    output = {}
    for policy, rho in POLICIES.items():
        matched, matched_censored = [], []
        interventions = {condition: {"delay": [], "censored": []} for condition in conditions}
        for onset in absolute:
            start, stop = int(onset - warmup), int(onset + cap + 1)
            initial = float(residual[start - m:start].mean())
            base = residual[start:stop]
            local_onset = int(onset - start)
            natural = run_monitor(base, scale=stream.scale, threshold=threshold,
                                  rho=rho, r0=initial, k=PROTOCOL["detector"]["k"], m=m)
            delay, censored = first_alarm_delay(natural, local_onset, cap)
            matched.append(delay)
            matched_censored.append(censored)
            for condition in conditions:
                changed = inject(base, local_onset, condition, stream.scale, observations_per_hour)
                run = run_monitor(changed, scale=stream.scale, threshold=threshold,
                                  rho=rho, r0=initial, k=PROTOCOL["detector"]["k"], m=m)
                delay, censored = first_alarm_delay(run, local_onset, cap)
                interventions[condition]["delay"].append(delay)
                interventions[condition]["censored"].append(censored)
        output[policy] = {"matched_in_control_wait": matched,
                          "matched_in_control_censored": matched_censored,
                          "interventions": interventions}
    return {"relative_grid": relative.tolist(), "absolute_grid": absolute.tolist(),
            "warmup": warmup, "cap": cap, "policies": output}


def run_task(task: str, gates: dict) -> dict:
    if not gates["all_primary_pass"]:
        raise RuntimeError("confirmatory generation prohibited: a frozen gate failed")
    if gates["tasks"][task]["status"] != "PASS":
        raise RuntimeError(f"{task}: confirmatory generation prohibited by task gate")
    if gates["protocol_hash"] != protocol_digest():
        raise RuntimeError("confirmatory generation prohibited: protocol hash mismatch")
    stream = build(LOADERS[task]())
    threshold = gates["tasks"][task]["calibration"]["threshold"]
    residual_hash = hashlib.sha256(stream.residual.astype("<f8").tobytes()).hexdigest()
    return {
        "schema": "rebaseguard.external-validation-v3.task-confirmatory.v1",
        "task": task, "evidence_status": "CONFIRMATORY",
        "protocol_hash": protocol_digest(), "threshold": threshold,
        "residual_sha256_float64_le": residual_hash,
        "split": gates["tasks"][task]["split"], "scale": stream.scale,
        "matched_streams": True, "natural": natural_blocks(stream, threshold),
        "events": event_outcomes(stream, threshold),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tasks", nargs="*", default=list(PRIMARY_TASKS))
    args = parser.parse_args()
    gates = json.loads((BASE / "results/gates.json").read_text())
    for task in args.tasks:
        result = run_task(task, gates)
        path = BASE / f"results/task_{task}_confirmatory.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
        print(f"{task}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
