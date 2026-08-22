"""Batch-level statistics fixed by the SR derivative protocol."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import t


@dataclass(frozen=True, slots=True)
class MeanSE:
    mean: float
    se: float
    sd: float
    n: int


def mean_se(values: np.ndarray) -> MeanSE:
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("at least two one-dimensional batch values are required")
    sd = float(values.std(ddof=1))
    return MeanSE(
        mean=float(values.mean()),
        se=sd / float(np.sqrt(values.size)),
        sd=sd,
        n=int(values.size),
    )


def independent_z(left: MeanSE, right: MeanSE) -> float:
    denominator = float(np.hypot(left.se, right.se))
    if denominator == 0.0:
        return 0.0 if left.mean == right.mean else float(np.inf)
    return (left.mean - right.mean) / denominator


def one_sided_t_lower(summary: MeanSE, confidence: float = 0.99) -> float:
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie strictly between zero and one")
    critical = float(t.ppf(confidence, summary.n - 1))
    return summary.mean - critical * summary.se


def paired_central_derivative(
    plus_batch_values: np.ndarray,
    minus_batch_values: np.ndarray,
    h: float,
) -> MeanSE:
    """Compute uncertainty from paired batch derivatives, never signwise SEs."""
    plus = np.asarray(plus_batch_values, dtype=float)
    minus = np.asarray(minus_batch_values, dtype=float)
    if plus.shape != minus.shape or plus.ndim != 1:
        raise ValueError("paired plus/minus batch vectors must have equal 1D shape")
    if h <= 0.0:
        raise ValueError("h must be positive")
    return mean_se((plus - minus) / (2.0 * h))

