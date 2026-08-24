"""Calibration-block-only CUSUM threshold selection and power gate."""
from __future__ import annotations

import numpy as np

from config import EXECUTION, PROTOCOL, task_config
from inference import mean_summary
from monitor import run_monitor


def _measure(stream, threshold: float, initial: float) -> np.ndarray:
    lo, hi = stream.calibration.start, stream.calibration.stop
    run = run_monitor(stream.residual, scale=stream.scale, threshold=threshold,
                      rho=0.0, r0=initial, start=lo, stop=hi,
                      k=PROTOCOL["detector"]["k"], m=PROTOCOL["detector"]["m"])
    burn = EXECUTION["monitor"]["burn_cycles_natural"]
    return np.asarray([cycle.length for cycle in run.cycles[burn:]], float)


def calibrate(stream) -> dict:
    task = stream.task
    target = task_config(task)["target_arl"]
    m = PROTOCOL["detector"]["m"]
    lo = stream.calibration.start
    initial = float(stream.residual[lo - m:lo].mean())
    lower, upper = EXECUTION["calibration"]["h_bounds"]
    trace = []
    for iteration in range(EXECUTION["calibration"]["max_iterations"]):
        threshold = float(np.exp((np.log(lower) + np.log(upper)) / 2))
        lengths = _measure(stream, threshold, initial)
        mean = float(lengths.mean()) if lengths.size else float("inf")
        trace.append({"iteration": iteration, "threshold": threshold,
                      "mean_cycle_length": mean if np.isfinite(mean) else None,
                      "n_cycles": int(lengths.size)})
        if mean < target:
            lower = threshold
        else:
            upper = threshold
        if np.log(upper) - np.log(lower) <= EXECUTION["calibration"]["log_tolerance"]:
            break
    candidates = []
    for threshold in sorted({lower, upper, trace[-1]["threshold"]}):
        lengths = _measure(stream, threshold, initial)
        if lengths.size:
            candidates.append((abs(float(lengths.mean()) - target), threshold, lengths))
    if not candidates:
        raise ValueError(f"{task}: no calibration cycles")
    _, threshold, lengths = min(candidates, key=lambda row: row[0])
    summary = mean_summary(
        lengths, block=task_config(task)["calibration_cycle_block"],
        draws=PROTOCOL["bootstrap"]["draws"], seed=PROTOCOL["bootstrap"]["seed"],
    )
    floor = PROTOCOL["power"]["minimum_effective_blocks"]
    point_ok = abs(summary["mean"] / target - 1) <= PROTOCOL["calibration"]["point_relative_tolerance"]
    ci_ok = summary["ci95"][0] <= target <= summary["ci95"][1]
    power_ok = summary["effective_blocks"] >= floor
    return {
        "task": task, "policy": "P0_fresh", "threshold": threshold,
        "target_arl": target, "achieved": summary, "initial_reference": initial,
        "point_relative_error": summary["mean"] / target - 1,
        "point_tolerance_pass": point_ok, "target_inside_ci": ci_ok,
        "effective_block_gate_pass": power_ok,
        "status": "PASS" if point_ok and ci_ok and power_ok else "FAIL",
        "trace": trace,
    }
