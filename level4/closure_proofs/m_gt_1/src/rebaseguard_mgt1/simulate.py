"""Independent stopped-cycle engine for the new closure-proof campaign.

Only the common frozen detector update is imported. In particular, this file
does not import Stage A's ``conditional`` or ``multicycle`` modules and does
not import any Stage-D estimator.
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
    zbar: np.ndarray


def simulate_stopped_batch(
    *,
    e: float,
    n_paths: int,
    m_grid: np.ndarray,
    rng: np.random.Generator,
    minimum_dwell: int | None = None,
    max_steps: int = 4_000_000,
) -> StoppedBatch:
    """Simulate iid cycles from reset detector state.

    ``minimum_dwell=None`` is the Stage-D ordinary stop. A positive dwell is
    used only by the explicit Stage-A distinction control.
    """
    m_grid = np.asarray(m_grid, dtype=np.int64)
    if n_paths < 1 or m_grid.ndim != 1 or m_grid.size == 0 or np.any(m_grid < 1):
        raise ValueError("positive path count and m grid required")
    if minimum_dwell is not None and minimum_dwell < 1:
        raise ValueError("minimum dwell must be positive")
    L = int(m_grid.max())
    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    total = np.zeros(n_paths)
    buf = np.zeros((n_paths, L))
    pos = np.zeros(n_paths, dtype=np.int64)
    active = np.ones(n_paths, dtype=bool)
    tau = np.zeros(n_paths, dtype=np.int64)
    t_tau = np.zeros(n_paths)

    for step in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        z = rng.standard_normal(idx.size) - e
        p, n, up, down = cusum_update(plus[idx], minus[idx], z, K_FROZEN, H_FROZEN)
        plus[idx] = p
        minus[idx] = n
        total[idx] += z
        buf[idx, pos[idx] % L] = z
        pos[idx] += 1
        crossed = up | down
        if minimum_dwell is not None and step < minimum_dwell:
            crossed &= False
        if crossed.any():
            done = idx[crossed]
            tau[done] = step
            t_tau[done] = total[done]
            active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} paths did not alarm")

    order = (pos[:, None] - 1 - np.arange(L)[None, :]) % L
    lags = np.take_along_axis(buf, order, axis=1)
    lags = np.where(np.arange(L)[None, :] < tau[:, None], lags, 0.0)
    sums = np.empty((n_paths, m_grid.size))
    means = np.empty_like(sums)
    for j, m in enumerate(m_grid):
        sums[:, j], means[:, j] = truncated_window(lags, tau, int(m))
    return StoppedBatch(tau=tau, t_tau=t_tau, lags_newest=lags,
                        window_sum=sums, zbar=means)
