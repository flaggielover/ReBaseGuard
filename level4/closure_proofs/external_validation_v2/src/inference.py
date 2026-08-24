"""Dependence-aware moving-block summaries frozen for V2."""
from __future__ import annotations

import numpy as np


def moving_block_indices(n: int, block: int, draws: int, rng) -> np.ndarray:
    if n < 1:
        raise ValueError("cannot bootstrap an empty sequence")
    block = min(block, n)
    starts = rng.integers(0, n - block + 1,
                          size=(draws, int(np.ceil(n / block))))
    index = (starts[:, :, None] + np.arange(block)).reshape(draws, -1)
    return index[:, :n]


def mean_summary(values, *, block: int, draws: int, seed: int) -> dict:
    values = np.asarray(values, float)
    index = moving_block_indices(values.size, block, draws, np.random.default_rng(seed))
    samples = values[index].mean(axis=1)
    return {
        "mean": float(values.mean()),
        "ci95": [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))],
        "n": int(values.size), "block": int(block),
        "effective_blocks": int(values.size // block),
    }


def paired_ratio(numerator, denominator, *, block: int, draws: int,
                 seed: int) -> dict:
    numerator, denominator = np.asarray(numerator, float), np.asarray(denominator, float)
    if numerator.shape != denominator.shape:
        raise ValueError("paired sequences have different shapes")
    index = moving_block_indices(numerator.size, block, draws, np.random.default_rng(seed))
    ratios = numerator[index].mean(axis=1) / denominator[index].mean(axis=1)
    point = float(numerator.mean() / denominator.mean())
    return {
        "ratio": point,
        "ci95": [float(np.quantile(ratios, 0.025)), float(np.quantile(ratios, 0.975))],
        "lower_97_5_one_sided": float(np.quantile(ratios, 0.025)),
        "upper_97_5_one_sided": float(np.quantile(ratios, 0.975)),
        "lower_99_one_sided": float(np.quantile(ratios, 0.01)),
        "upper_99_one_sided": float(np.quantile(ratios, 0.99)),
        "n": int(numerator.size), "block": int(block),
        "effective_blocks": int(numerator.size // block),
        "pairing": "same chronological block/event index",
    }


def paired_difference(left, right, *, block: int, draws: int, seed: int) -> dict:
    left, right = np.asarray(left, float), np.asarray(right, float)
    if left.shape != right.shape:
        raise ValueError("paired sequences have different shapes")
    index = moving_block_indices(left.size, block, draws, np.random.default_rng(seed))
    samples = left[index].mean(axis=1) - right[index].mean(axis=1)
    return {
        "difference": float(left.mean() - right.mean()),
        "ci95": [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))],
        "n": int(left.size), "block": int(block),
        "effective_blocks": int(left.size // block),
    }
