"""Direct computation of the random-denominator Stage-D gain integrand."""

from __future__ import annotations

import numpy as np

from .primitives import StoppedPrimitives


def direct_gain(paths: StoppedPrimitives, m_grid: np.ndarray) -> np.ndarray:
    """Compute ``A_m T_tau`` directly from each truncated stopped suffix."""
    m_grid = np.asarray(m_grid, dtype=np.int64)
    if np.any(m_grid < 1) or paths.lags_newest.shape[1] < int(m_grid.max()):
        raise ValueError("positive m grid within retained lag width required")
    values = np.empty((paths.tau.size, m_grid.size))
    for j, m_raw in enumerate(m_grid):
        m = int(m_raw)
        realized = np.minimum(paths.tau, m)
        suffix_sum = np.sum(paths.lags_newest[:, :m], axis=1)
        values[:, j] = suffix_sum / realized * paths.t_tau
    return values


def stage_a_gain(paths: StoppedPrimitives, m: int) -> np.ndarray:
    """Compute the fixed full-window Stage-A gain integrand."""
    if m < 1 or paths.lags_newest.shape[1] < m or np.any(paths.tau < m):
        raise ValueError("Stage A requires a full positive m window")
    suffix_sum = np.sum(paths.lags_newest[:, :m], axis=1)
    return suffix_sum / m * paths.t_tau

