"""Statistical helpers with transparent iid standard-error propagation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class Moments:
    n: int
    sum: np.ndarray
    sumsq: np.ndarray

    @classmethod
    def zeros(cls, shape: tuple[int, ...]) -> "Moments":
        return cls(0, np.zeros(shape), np.zeros(shape))

    def add(self, values: np.ndarray) -> None:
        values = np.asarray(values, dtype=float)
        self.n += values.shape[0]
        self.sum += values.sum(axis=0)
        self.sumsq += np.square(values).sum(axis=0)

    @property
    def mean(self) -> np.ndarray:
        return self.sum / self.n

    @property
    def se(self) -> np.ndarray:
        if self.n < 2:
            return np.full_like(self.sum, np.nan)
        var = np.maximum((self.sumsq - self.sum**2 / self.n) / (self.n - 1), 0.0)
        return np.sqrt(var / self.n)


def central_difference(
    f_plus: np.ndarray, se_plus: np.ndarray,
    f_minus: np.ndarray, se_minus: np.ndarray, h: float,
) -> tuple[np.ndarray, np.ndarray]:
    if h <= 0:
        raise ValueError("h must be positive")
    derivative = (np.asarray(f_plus) - np.asarray(f_minus)) / (2.0 * h)
    se = np.hypot(se_plus, se_minus) / (2.0 * h)
    return derivative, se


def inverse_variance_pool(values: np.ndarray, ses: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=float)
    ses = np.asarray(ses, dtype=float)
    if np.any(ses <= 0):
        raise ValueError("strictly positive standard errors required")
    weights = 1.0 / ses**2
    return ((weights * values).sum(axis=0) / weights.sum(axis=0),
            np.sqrt(1.0 / weights.sum(axis=0)))


def richardson(d_half: np.ndarray, se_half: np.ndarray,
               d_full: np.ndarray, se_full: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Secondary `O(h^2)` extrapolation: `(4 D(h/2)-D(h))/3`."""
    value = (4.0 * np.asarray(d_half) - np.asarray(d_full)) / 3.0
    se = np.hypot(4.0 * np.asarray(se_half), np.asarray(se_full)) / 3.0
    return value, se
