"""Independent ordinary-stop CUSUM and truncated-window calculations.

This module deliberately imports neither Stage D nor either historical m>1
proof track. Constants and recurrences are restated from the frozen prose and
are regression-checked against the read-only primitive separately.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

K = 0.5
H = 5.0


@dataclass(frozen=True, slots=True)
class StoppedBatch:
    e: float
    n: int
    tau_mean: float
    map_base: np.ndarray
    gamma: np.ndarray
    short_counts: np.ndarray
    tau_equal_counts: np.ndarray
    full_counts: np.ndarray


def window_terms(paths: list[np.ndarray], m_grid: np.ndarray) -> dict[str, np.ndarray]:
    """Exact direct and decomposed terms for already-stopped deterministic paths."""
    m_grid = np.asarray(m_grid, dtype=np.int64)
    direct = np.zeros((len(paths), len(m_grid)))
    fixed = np.zeros_like(direct)
    correction = np.zeros_like(direct)
    windows = np.zeros_like(direct)
    taus = np.asarray([len(path) for path in paths], dtype=np.int64)
    totals = np.asarray([float(np.sum(path)) for path in paths])
    if np.any(taus < 1) or np.any(m_grid < 1):
        raise ValueError("paths and window sizes must be nonempty and positive")
    for i, path in enumerate(paths):
        for j, m in enumerate(m_grid):
            w = min(int(m), len(path))
            suffix = float(np.sum(path[-w:]))
            windows[i, j] = suffix / w
            direct[i, j] = windows[i, j] * totals[i]
            fixed[i, j] = suffix / int(m) * totals[i]
            if len(path) < int(m):
                correction[i, j] = (1.0 / len(path) - 1.0 / int(m)) * totals[i] ** 2
    return {
        "tau": taus,
        "total": totals,
        "window": windows,
        "direct": direct,
        "fixed": fixed,
        "correction": correction,
    }


def stopped_batch(
    *, e: float, n_paths: int, m_grid: np.ndarray, rng: np.random.Generator,
    max_steps: int = 4_000_000,
) -> StoppedBatch:
    """Simulate one independent batch from the ordinary Stage-D stopping rule."""
    m_grid = np.asarray(m_grid, dtype=np.int64)
    if n_paths < 1 or m_grid.size < 1 or np.any(m_grid < 1):
        raise ValueError("positive paths and window sizes required")
    width = int(m_grid.max())
    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    total = np.zeros(n_paths)
    tau = np.zeros(n_paths, dtype=np.int64)
    buffer = np.zeros((n_paths, width))
    count = np.zeros(n_paths, dtype=np.int64)
    active = np.ones(n_paths, dtype=bool)

    for step in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        z = rng.standard_normal(idx.size) - e
        p = np.maximum(0.0, plus[idx] + z - K)
        q = np.maximum(0.0, minus[idx] - z - K)
        plus[idx] = p
        minus[idx] = q
        total[idx] += z
        buffer[idx, count[idx] % width] = z
        count[idx] += 1
        crossed = (p >= H) | (q >= H)
        if np.any(crossed):
            done = idx[crossed]
            tau[done] = step
            active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} paths exceeded max_steps")

    order = (count[:, None] - 1 - np.arange(width)[None, :]) % width
    newest = np.take_along_axis(buffer, order, axis=1)
    newest = np.where(np.arange(width)[None, :] < tau[:, None], newest, 0.0)
    cumulative = np.cumsum(newest, axis=1)

    maps = np.zeros(m_grid.size)
    gammas = np.zeros(m_grid.size)
    short = np.zeros(m_grid.size, dtype=np.int64)
    equal = np.zeros(m_grid.size, dtype=np.int64)
    full = np.zeros(m_grid.size, dtype=np.int64)
    rows = np.arange(n_paths)
    for j, m in enumerate(m_grid):
        w = np.minimum(int(m), tau)
        suffix = cumulative[rows, w - 1]
        a = suffix / w
        maps[j] = e + float(np.mean(a))
        gammas[j] = float(np.mean(a * total))
        short[j] = int(np.count_nonzero(tau < m))
        equal[j] = int(np.count_nonzero(tau == m))
        full[j] = int(np.count_nonzero(tau > m))
    return StoppedBatch(
        e=float(e), n=n_paths, tau_mean=float(np.mean(tau)), map_base=maps,
        gamma=gammas, short_counts=short, tau_equal_counts=equal,
        full_counts=full,
    )
