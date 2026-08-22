"""Transparent iid moment and uncertainty calculations for Track 1A."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np


@dataclass(slots=True)
class Moments:
    n: int
    total: np.ndarray
    total_sq: np.ndarray

    @classmethod
    def zeros(cls, shape: tuple[int, ...]) -> "Moments":
        return cls(0, np.zeros(shape), np.zeros(shape))

    def add(self, values: np.ndarray) -> None:
        x = np.asarray(values, dtype=float)
        self.n += x.shape[0]
        self.total += x.sum(axis=0)
        self.total_sq += np.square(x).sum(axis=0)

    @property
    def mean(self) -> np.ndarray:
        return self.total / self.n

    @property
    def variance(self) -> np.ndarray:
        if self.n < 2:
            return np.full_like(self.total, np.nan)
        return np.maximum(
            (self.total_sq - np.square(self.total) / self.n) / (self.n - 1),
            0.0,
        )

    @property
    def sd(self) -> np.ndarray:
        return np.sqrt(self.variance)

    @property
    def se(self) -> np.ndarray:
        return self.sd / np.sqrt(self.n)


def inverse_variance_pool(
    values: np.ndarray, ses: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=float)
    ses = np.asarray(ses, dtype=float)
    if np.any(ses <= 0) or values.shape != ses.shape:
        raise ValueError("equal shapes and strictly positive SEs required")
    weights = 1.0 / np.square(ses)
    return (
        np.sum(weights * values, axis=0) / np.sum(weights, axis=0),
        np.sqrt(1.0 / np.sum(weights, axis=0)),
    )


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n < 1 or not 0 <= successes <= n:
        raise ValueError("valid binomial count required")
    p = successes / n
    denominator = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denominator
    radius = z / denominator * sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return center - radius, center + radius

