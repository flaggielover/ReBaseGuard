"""Independent fixed-lag plus short-cycle reconstruction implementation."""

from __future__ import annotations

import numpy as np

from .primitives import StoppedPrimitives


def reconstructed_gain(
    paths: StoppedPrimitives, m_grid: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return fixed-lag, correction, and their sum without direct-window code."""
    m_grid = np.asarray(m_grid, dtype=np.int64)
    if np.any(m_grid < 1) or paths.lags_newest.shape[1] < int(m_grid.max()):
        raise ValueError("positive m grid within retained lag width required")
    n = paths.tau.size
    fixed = np.empty((n, m_grid.size))
    correction = np.empty_like(fixed)
    lag_products = paths.lags_newest * paths.t_tau[:, None]
    for j, m_raw in enumerate(m_grid):
        m = int(m_raw)
        fixed[:, j] = np.sum(lag_products[:, :m], axis=1) / m
        short = paths.tau < m
        correction[:, j] = 0.0
        correction[short, j] = (
            (1.0 / paths.tau[short] - 1.0 / m)
            * np.square(paths.t_tau[short])
        )
    return fixed, correction, fixed + correction

