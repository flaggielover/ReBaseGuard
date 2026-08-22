"""Raw stopped-path primitives shared by independent Track 1B implementations."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

LEVEL4 = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(LEVEL4 / "src"))
from rebaseguard_level4.frozen import H_FROZEN, K_FROZEN, cusum_update  # noqa: E402

M_GRID = np.array([1, 2, 5, 10, 20, 50], dtype=np.int64)


@dataclass(slots=True)
class StoppedPrimitives:
    """Only quantities read directly from a simulated stopped trajectory."""

    tau: np.ndarray
    t_tau: np.ndarray
    lags_newest: np.ndarray


def simulate_stopped_batch(
    *,
    n_paths: int,
    max_m: int,
    rng: np.random.Generator,
    minimum_dwell: int | None = None,
    max_steps: int = 4_000_000,
) -> StoppedPrimitives:
    """Simulate reset CUSUM cycles and return no theorem-derived quantities."""
    if n_paths < 1 or max_m < 1:
        raise ValueError("n_paths and max_m must be positive")
    if minimum_dwell is not None and minimum_dwell < 1:
        raise ValueError("minimum dwell must be positive")

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
    return StoppedPrimitives(tau=tau, t_tau=t_tau, lags_newest=lags)


def primitive_checks(paths: StoppedPrimitives) -> dict[str, bool]:
    """Checks that do not encode the decomposition theorem."""
    width = paths.lags_newest.shape[1]
    beyond = np.arange(width)[None, :] >= paths.tau[:, None]
    return {
        "positive_tau": bool(np.all(paths.tau >= 1)),
        "shape_alignment": bool(
            paths.tau.ndim == 1
            and paths.t_tau.shape == paths.tau.shape
            and paths.lags_newest.shape[0] == paths.tau.size
        ),
        "lags_beyond_tau_zero": bool(np.all(paths.lags_newest[beyond] == 0.0)),
    }

