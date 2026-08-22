"""Route B: independent signed-lower-chart paired conditional-map estimator.

This module deliberately does not import Route A or implement a location score
or stopped gain.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class ConditionalPaths:
    errors: np.ndarray
    terminal: np.ndarray
    tau: np.ndarray
    direction: np.ndarray
    ties: int
    simultaneous_crossings: int


def physical_t3(generator: np.random.Generator, count: int) -> np.ndarray:
    return generator.standard_t(df=3, size=count) / np.sqrt(3.0)


def simulate_conditional_batch(
    *,
    threshold: float,
    errors: np.ndarray,
    n_paths: int,
    generator: np.random.Generator,
    max_steps: int = 4_000_000,
) -> ConditionalPaths:
    errors = np.asarray(errors, dtype=float)
    conditions = errors.size
    upper = np.zeros((n_paths, conditions))
    lower = np.zeros((n_paths, conditions))
    active = np.ones((n_paths, conditions), dtype=bool)
    terminal = np.zeros((n_paths, conditions))
    tau = np.zeros((n_paths, conditions), dtype=np.int64)
    direction = np.zeros((n_paths, conditions), dtype=np.int8)
    ties = 0
    simultaneous = 0

    for step in range(1, max_steps + 1):
        live_rows = np.flatnonzero(active.any(axis=1))
        if live_rows.size == 0:
            break
        physical = physical_t3(generator, live_rows.size)
        residual = physical[:, None] - errors[None, :]
        live = active[live_rows]
        next_upper = np.maximum(0.0, upper[live_rows] + residual - 0.5)
        next_lower = np.minimum(0.0, lower[live_rows] + residual + 0.5)
        upper[live_rows] = np.where(live, next_upper, upper[live_rows])
        lower[live_rows] = np.where(live, next_lower, lower[live_rows])
        crossed_upper = live & (next_upper >= threshold)
        crossed_lower = live & (next_lower <= -threshold)
        crossed = crossed_upper | crossed_lower
        if not crossed.any():
            continue
        both = crossed_upper & crossed_lower
        count_both = int(np.count_nonzero(both))
        ties += count_both
        simultaneous += count_both
        row, column = np.nonzero(crossed)
        global_row = live_rows[row]
        tau[global_row, column] = step
        terminal[global_row, column] = residual[row, column]
        direction[global_row, column] = (
            crossed_upper[row, column].astype(np.int8)
            - crossed_lower[row, column].astype(np.int8)
        )
        active[global_row, column] = False
    else:
        raise RuntimeError(f"{int(active.sum())} Route-B paths did not alarm")

    return ConditionalPaths(
        errors=errors,
        terminal=terminal,
        tau=tau,
        direction=direction,
        ties=ties,
        simultaneous_crossings=simultaneous,
    )


def summarize_conditional_paths(
    paths: ConditionalPaths, h_steps: tuple[float, ...]
) -> dict:
    maps = paths.errors + paths.terminal.mean(axis=0)
    derivatives = []
    path_variances = []
    plus_minus_covariances = []
    plus_minus_correlations = []
    for h_index, h in enumerate(h_steps):
        minus_index = 2 * h_index
        plus_index = minus_index + 1
        plus = h + paths.terminal[:, plus_index]
        minus = -h + paths.terminal[:, minus_index]
        path_derivative = (plus - minus) / (2.0 * h)
        derivatives.append(float(path_derivative.mean()))
        path_variances.append(float(path_derivative.var(ddof=1)))
        plus_minus_covariances.append(float(np.cov(plus, minus, ddof=1)[0, 1]))
        plus_minus_correlations.append(float(np.corrcoef(plus, minus)[0, 1]))
    return {
        "path_streams": int(paths.terminal.shape[0]),
        "maps": maps.tolist(),
        "paired_derivatives": derivatives,
        "paired_derivative_path_variances": path_variances,
        "plus_minus_covariances": plus_minus_covariances,
        "plus_minus_correlations": plus_minus_correlations,
        "arl_by_error": paths.tau.mean(axis=0).tolist(),
        "direction_mean_by_error": paths.direction.mean(axis=0).tolist(),
        "ties": paths.ties,
        "simultaneous_crossings": paths.simultaneous_crossings,
    }
