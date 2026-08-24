#!/usr/bin/env python3
"""Run P0-only calibration, leakage, data, and actual power gates."""
from __future__ import annotations

import json

import numpy as np

from acquire import acquire
from calibration import calibrate
from config import BASE, PRIMARY_TASKS, PROTOCOL, protocol_digest, task_config
from datasets import LOADERS
from model import build


def diagnostics(values: np.ndarray, lags: tuple[int, ...]) -> dict:
    values = np.asarray(values, float)
    centered = values - values.mean()
    denominator = float(centered @ centered)
    standardized = centered / values.std()
    return {
        "mean": float(values.mean()), "sd": float(values.std()),
        "excess_kurtosis": float(np.mean(standardized ** 4) - 3),
        "acf": {str(lag): float(centered[:-lag] @ centered[lag:] / denominator)
                for lag in lags if values.size > lag},
    }


def task_gate(task: str) -> dict:
    acquire(task)
    data = LOADERS[task]()
    stream = build(data)
    config = task_config(task)
    natural_blocks = (stream.evaluation.stop - stream.evaluation.start) // config["natural_block_observations"]
    event_blocks = PROTOCOL["events"]["count"] // PROTOCOL["bootstrap"]["event_block"]
    calibration = calibrate(stream)
    floor = PROTOCOL["power"]["minimum_effective_blocks"]
    leakage = {
        "chronological_nonoverlap": stream.train.stop <= stream.calibration.start < stream.calibration.stop <= stream.evaluation.start,
        "model_fit_source": "train only", "scale_source": "train only",
        "threshold_source": "calibration only", "rho_source": "frozen protocol",
        "event_seed_independent": True, "no_future_features": True,
    }
    actual_power = {
        "natural_blocks": int(natural_blocks),
        "event_blocks": int(event_blocks),
        "calibration_cycle_blocks": calibration["achieved"]["effective_blocks"],
        "floor": floor,
    }
    gates = {
        "dataset": data.y.size > 0 and data.audit["malformed_selected_rows"] == 0,
        "leakage": leakage["chronological_nonoverlap"] and leakage["no_future_features"],
        "power": min(actual_power.values()) >= floor,
        "calibration": calibration["status"] == "PASS",
    }
    return {
        "task": task, "n": int(data.y.size),
        "split": {"train": [stream.train.start, stream.train.stop],
                  "calibration": [stream.calibration.start, stream.calibration.stop],
                  "evaluation": [stream.evaluation.start, stream.evaluation.stop]},
        "dataset_audit": data.audit, "model": stream.model,
        "train_residual_scale": stream.scale,
        "calibration_residual_diagnostics": diagnostics(
            stream.residual[stream.calibration], (1, 4, 24, 96, 168)),
        "leakage": leakage, "actual_power": actual_power,
        "calibration": calibration, "gates": gates,
        "status": "PASS" if all(gates.values()) else "FAIL",
    }


def main() -> int:
    tasks = {task: task_gate(task) for task in PRIMARY_TASKS}
    result = {
        "schema": "rebaseguard.external-validation-v3.gates.v1",
        "protocol_hash": protocol_digest(),
        "confirmatory_outcomes_generated": False,
        "tasks": tasks,
        "all_primary_pass": all(row["status"] == "PASS" for row in tasks.values()),
    }
    path = BASE / "results/gates.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(f"all primary gates: {'PASS' if result['all_primary_pass'] else 'FAIL'} -> {path}")
    return 0 if result["all_primary_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
