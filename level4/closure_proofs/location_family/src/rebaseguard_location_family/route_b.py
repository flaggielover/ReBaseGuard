"""Route B: independent signed-chart conditional-map implementation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class ConditionalBatch:
    errors: np.ndarray
    terminal: np.ndarray
    tau: np.ndarray
    direction: np.ndarray
    ties: int
    simultaneous_crossings: int

    def maps(self) -> np.ndarray:
        return self.errors + self.terminal.mean(axis=0)


def physical_draws(
    family: str, generator: np.random.Generator, count: int
) -> np.ndarray:
    if family == "gaussian":
        return generator.normal(loc=0.0, scale=1.0, size=count)
    if family in {"t10", "t5", "t3"}:
        degrees = {"t10": 10, "t5": 5, "t3": 3}[family]
        variance_scale = (degrees / (degrees - 2.0)) ** 0.5
        return generator.standard_t(df=degrees, size=count) / variance_scale
    if family in {"contam0.05", "contam0.1"}:
        probability = {"contam0.05": 0.05, "contam0.1": 0.10}[family]
        normal = generator.normal(size=count)
        component = generator.uniform(size=count) < probability
        normal[component] *= 3.0
        return normal
    raise ValueError(f"unsupported family: {family}")


def trace_signed(path: np.ndarray, threshold: float) -> tuple[int, float, int]:
    upper = 0.0
    lower = 0.0
    for time, residual_raw in enumerate(np.asarray(path, dtype=float), start=1):
        residual = float(residual_raw)
        upper = max(0.0, upper + residual - 0.5)
        lower = min(0.0, lower + residual + 0.5)
        crossed_upper = upper >= threshold
        crossed_lower = lower <= -threshold
        if crossed_upper or crossed_lower:
            direction = int(crossed_upper) - int(crossed_lower)
            return time, residual, direction
    raise RuntimeError("path did not alarm")


def simulate_conditional_batch(
    *,
    family: str,
    threshold: float,
    errors: np.ndarray,
    n_paths: int,
    generator: np.random.Generator,
    max_steps: int = 4_000_000,
) -> ConditionalBatch:
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
        live_paths = np.flatnonzero(active.any(axis=1))
        if live_paths.size == 0:
            break
        physical = physical_draws(family, generator, live_paths.size)
        residual = physical[:, None] - errors[None, :]
        live = active[live_paths]
        next_upper = np.maximum(0.0, upper[live_paths] + residual - 0.5)
        next_lower = np.minimum(0.0, lower[live_paths] + residual + 0.5)
        upper[live_paths] = np.where(live, next_upper, upper[live_paths])
        lower[live_paths] = np.where(live, next_lower, lower[live_paths])
        crossed_upper = live & (next_upper >= threshold)
        crossed_lower = live & (next_lower <= -threshold)
        crossed = crossed_upper | crossed_lower
        if not crossed.any():
            continue
        both = crossed_upper & crossed_lower
        count_both = int(np.count_nonzero(both))
        ties += count_both
        simultaneous += count_both
        rows, columns = np.nonzero(crossed)
        global_rows = live_paths[rows]
        tau[global_rows, columns] = step
        terminal[global_rows, columns] = residual[rows, columns]
        direction[global_rows, columns] = (
            crossed_upper[rows, columns].astype(np.int8)
            - crossed_lower[rows, columns].astype(np.int8)
        )
        active[global_rows, columns] = False
    else:
        raise RuntimeError(
            f"{int(active.sum())} Route-B condition paths did not alarm"
        )

    return ConditionalBatch(
        errors=errors,
        terminal=terminal,
        tau=tau,
        direction=direction,
        ties=ties,
        simultaneous_crossings=simultaneous,
    )

