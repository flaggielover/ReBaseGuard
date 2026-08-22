"""Batch-level statistics fixed by the Track-3 protocol."""

from __future__ import annotations

import numpy as np


def mean_se(values: np.ndarray) -> tuple[float, float]:
    data = np.asarray(values, dtype=float)
    if data.ndim != 1 or data.size < 2:
        raise ValueError("mean_se requires at least two one-dimensional batches")
    return float(data.mean()), float(data.std(ddof=1) / np.sqrt(data.size))


def combined_z(x: float, sx: float, y: float, sy: float) -> float:
    denominator = float(np.hypot(sx, sy))
    if denominator == 0.0:
        return 0.0 if x == y else float("inf")
    return float((x - y) / denominator)


def symmetric_relative_difference(x: float, y: float) -> float:
    denominator = (abs(x) + abs(y)) / 2.0
    if denominator == 0.0:
        return 0.0 if x == y else float("inf")
    return float(abs(x - y) / denominator)


def paired_derivatives(
    maps: np.ndarray, errors: np.ndarray, h_steps: tuple[float, ...]
) -> np.ndarray:
    maps = np.asarray(maps, dtype=float)
    errors = np.asarray(errors, dtype=float)
    output = []
    for h in h_steps:
        plus = int(np.flatnonzero(np.isclose(errors, h, rtol=0.0, atol=1e-15))[0])
        minus = int(np.flatnonzero(np.isclose(errors, -h, rtol=0.0, atol=1e-15))[0])
        output.append((maps[plus] - maps[minus]) / (2.0 * h))
    return np.asarray(output)


def observed_order(estimates: np.ndarray) -> float | None:
    coarse, middle, fine = np.asarray(estimates, dtype=float)
    numerator = coarse - middle
    denominator = middle - fine
    if denominator == 0.0 or numerator / denominator <= 0.0:
        return None
    return float(np.log2(numerator / denominator))


def richardson(middle: np.ndarray, fine: np.ndarray) -> np.ndarray:
    return (4.0 * np.asarray(fine) - np.asarray(middle)) / 3.0

