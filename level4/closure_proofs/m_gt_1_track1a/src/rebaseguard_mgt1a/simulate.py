"""Independent stopped-cycle engine for Track 1A.

Only the common frozen CUSUM update is imported. Historical Stage-A and
Stage-D estimator modules are deliberately not imported.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

LEVEL4 = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(LEVEL4 / "src"))
from rebaseguard_level4.frozen import H_FROZEN, K_FROZEN, cusum_update  # noqa: E402

from .model import truncated_window


@dataclass(slots=True)
class StoppedBatch:
    tau: np.ndarray
    t_tau: np.ndarray
    lags_newest: np.ndarray
    window_sum: np.ndarray
    window_mean: np.ndarray


def simulate_stopped_batch(
    *,
    n_paths: int,
    m_grid: np.ndarray,
    rng: np.random.Generator,
    minimum_dwell: int | None = None,
    max_steps: int = 4_000_000,
) -> StoppedBatch:
    """Simulate reset cycles under the in-control standard-Gaussian law.

    ``minimum_dwell=None`` is the ordinary Stage-D stop. A positive integer is
    the Stage-A rule that suppresses termination before that time.
    """
    m_grid = np.asarray(m_grid, dtype=np.int64)
    if n_paths < 1 or m_grid.ndim != 1 or m_grid.size == 0 or np.any(m_grid < 1):
        raise ValueError("positive path count and m grid required")
    if minimum_dwell is not None and minimum_dwell < 1:
        raise ValueError("minimum dwell must be positive")

    max_m = int(m_grid.max())
    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    total = np.zeros(n_paths)
    buffer = np.zeros((n_paths, max_m))
    position = np.zeros(n_paths, dtype=np.int64)
    active = np.ones(n_paths, dtype=bool)
    tau = np.zeros(n_paths, dtype=np.int64)
    t_tau = np.zeros(n_paths)

    for step in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        z = rng.standard_normal(idx.size)
        next_plus, next_minus, up, down = cusum_update(
            plus[idx], minus[idx], z, K_FROZEN, H_FROZEN
        )
        plus[idx] = next_plus
        minus[idx] = next_minus
        total[idx] += z
        buffer[idx, position[idx] % max_m] = z
        position[idx] += 1
        crossed = up | down
        if minimum_dwell is not None and step < minimum_dwell:
            crossed[:] = False
        if crossed.any():
            done = idx[crossed]
            tau[done] = step
            t_tau[done] = total[done]
            active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} paths did not alarm")

    order = (position[:, None] - 1 - np.arange(max_m)[None, :]) % max_m
    lags = np.take_along_axis(buffer, order, axis=1)
    lags = np.where(np.arange(max_m)[None, :] < tau[:, None], lags, 0.0)
    sums = np.empty((n_paths, m_grid.size))
    means = np.empty_like(sums)
    for j, m in enumerate(m_grid):
        sums[:, j], means[:, j] = truncated_window(lags, tau, int(m))
    return StoppedBatch(tau, t_tau, lags, sums, means)

