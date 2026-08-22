"""Frozen batch-level statistics for Track 3A."""

from __future__ import annotations

import math

import numpy as np


def mean_se(values: np.ndarray) -> tuple[float, float]:
    data = np.asarray(values, dtype=float)
    if data.ndim != 1 or data.size < 2:
        raise ValueError("mean_se requires at least two one-dimensional batches")
    return float(data.mean()), float(data.std(ddof=1) / math.sqrt(data.size))


def normal_ci95(mean: float, se: float) -> tuple[float, float]:
    return float(mean - 1.96 * se), float(mean + 1.96 * se)


def combined_z(x: float, sx: float, y: float, sy: float) -> float:
    denominator = math.hypot(sx, sy)
    if denominator == 0.0:
        return 0.0 if x == y else float("inf")
    return float((x - y) / denominator)


def symmetric_relative_difference(x: float, y: float) -> float:
    denominator = (abs(x) + abs(y)) / 2.0
    if denominator == 0.0:
        return 0.0 if x == y else float("inf")
    return float(abs(x - y) / denominator)


def ten_percent_trimmed_mean(values: np.ndarray) -> float:
    data = np.sort(np.asarray(values, dtype=float))
    trim = int(math.floor(0.1 * data.size))
    if trim == 0:
        return float(data.mean())
    return float(data[trim:-trim].mean())


def batch_diagnostics(values: np.ndarray) -> dict[str, float]:
    data = np.asarray(values, dtype=float)
    mean, se = mean_se(data)
    centered = data - mean
    sd = float(data.std(ddof=1))
    skew = 0.0 if sd == 0.0 else float(
        data.size / ((data.size - 1) * (data.size - 2))
        * np.sum((centered / sd) ** 3)
    )
    leave_one_out = (data.sum() - data) / (data.size - 1)
    max_influence = float(np.max(np.abs(leave_one_out - mean)))
    return {
        "mean": mean,
        "se": se,
        "ci95_low": normal_ci95(mean, se)[0],
        "ci95_high": normal_ci95(mean, se)[1],
        "sd": sd,
        "median": float(np.median(data)),
        "ten_percent_trimmed_mean": ten_percent_trimmed_mean(data),
        "skew": skew,
        "min": float(data.min()),
        "max": float(data.max()),
        "max_leave_one_batch_mean_influence": max_influence,
        "max_leave_one_batch_relative_influence": (
            max_influence / abs(mean) if mean else float("inf")
        ),
    }
