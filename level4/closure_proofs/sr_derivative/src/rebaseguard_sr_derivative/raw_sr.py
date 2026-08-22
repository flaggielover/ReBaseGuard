"""Route A: independently written raw-state Shiryaev--Roberts simulator.

This module deliberately contains its own recursion, alarm classification, and
stopped-statistic accumulation.  It does not import the Stage D or Route B
implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

TIE = np.int8(0)
UP = np.int8(1)
DOWN = np.int8(-1)


@dataclass(slots=True)
class RawPathRecord:
    tau: int | None
    terminal_z: float | None
    stopped_sum: float
    direction: int | None
    simultaneous: bool
    exact_tie: bool
    r_plus: float
    r_minus: float


@dataclass(slots=True)
class RawStoppedBatch:
    tau: np.ndarray
    terminal_z: np.ndarray
    stopped_sum: np.ndarray
    product: np.ndarray
    direction: np.ndarray
    simultaneous: np.ndarray
    exact_tie: np.ndarray
    terminal_plus: np.ndarray
    terminal_minus: np.ndarray


def raw_step(
    r_plus: np.ndarray | float,
    r_minus: np.ndarray | float,
    z: np.ndarray | float,
) -> tuple[np.ndarray | float, np.ndarray | float]:
    """One raw two-chart SR update for unit design shift."""
    new_plus = (1.0 + r_plus) * np.exp(z - 0.5)
    new_minus = (1.0 + r_minus) * np.exp(-z - 0.5)
    return new_plus, new_minus


def classify_alarm(
    r_plus: np.ndarray | float,
    r_minus: np.ndarray | float,
    threshold: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return crossed, direction, simultaneous, and exact-tie arrays."""
    plus = np.asarray(r_plus)
    minus = np.asarray(r_minus)
    crossed_plus = plus >= threshold
    crossed_minus = minus >= threshold
    crossed = crossed_plus | crossed_minus
    simultaneous = crossed_plus & crossed_minus
    exact_tie = simultaneous & (plus == minus)
    direction = np.where(
        exact_tie,
        TIE,
        np.where(plus > minus, UP, DOWN),
    ).astype(np.int8)
    return crossed, direction, simultaneous, exact_tie


def run_raw_path(
    innovations: np.ndarray,
    *,
    threshold: float,
    e: float = 0.0,
) -> RawPathRecord:
    """Run one deterministic residual path from the reset state."""
    if threshold <= 1.0:
        raise ValueError("SR threshold must be in natural units and exceed one")
    r_plus = 0.0
    r_minus = 0.0
    total = 0.0
    for step, epsilon in enumerate(np.asarray(innovations, dtype=float), start=1):
        z = float(epsilon - e)
        r_plus, r_minus = raw_step(r_plus, r_minus, z)
        total += z
        crossed, direction, simultaneous, exact_tie = classify_alarm(
            r_plus, r_minus, threshold
        )
        if bool(crossed):
            return RawPathRecord(
                tau=step,
                terminal_z=z,
                stopped_sum=total,
                direction=int(direction),
                simultaneous=bool(simultaneous),
                exact_tie=bool(exact_tie),
                r_plus=float(r_plus),
                r_minus=float(r_minus),
            )
    return RawPathRecord(
        tau=None,
        terminal_z=None,
        stopped_sum=total,
        direction=None,
        simultaneous=False,
        exact_tie=False,
        r_plus=float(r_plus),
        r_minus=float(r_minus),
    )


def simulate_raw_paths(
    *,
    n_paths: int,
    threshold: float,
    rng: np.random.Generator,
    e: float = 0.0,
    max_steps: int = 4_000_000,
) -> RawStoppedBatch:
    """Simulate independent reset cycles and retain stopped primitives."""
    if n_paths < 1:
        raise ValueError("n_paths must be positive")
    if threshold <= 1.0:
        raise ValueError("SR threshold must be in natural units and exceed one")

    r_plus = np.zeros(n_paths)
    r_minus = np.zeros(n_paths)
    total = np.zeros(n_paths)
    active = np.ones(n_paths, dtype=bool)

    tau = np.zeros(n_paths, dtype=np.int64)
    terminal_z = np.zeros(n_paths)
    stopped_sum = np.zeros(n_paths)
    direction = np.zeros(n_paths, dtype=np.int8)
    simultaneous = np.zeros(n_paths, dtype=bool)
    exact_tie = np.zeros(n_paths, dtype=bool)
    terminal_plus = np.zeros(n_paths)
    terminal_minus = np.zeros(n_paths)

    for step in range(1, max_steps + 1):
        live = np.flatnonzero(active)
        if live.size == 0:
            break
        z = rng.standard_normal(live.size) - e
        new_plus, new_minus = raw_step(r_plus[live], r_minus[live], z)
        r_plus[live] = new_plus
        r_minus[live] = new_minus
        total[live] += z

        crossed, alarm_direction, both, tied = classify_alarm(
            new_plus, new_minus, threshold
        )
        if not crossed.any():
            continue
        done = live[crossed]
        tau[done] = step
        terminal_z[done] = z[crossed]
        stopped_sum[done] = total[done]
        direction[done] = alarm_direction[crossed]
        simultaneous[done] = both[crossed]
        exact_tie[done] = tied[crossed]
        terminal_plus[done] = new_plus[crossed]
        terminal_minus[done] = new_minus[crossed]
        active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} raw SR paths did not alarm")

    product = terminal_z * stopped_sum
    return RawStoppedBatch(
        tau=tau,
        terminal_z=terminal_z,
        stopped_sum=stopped_sum,
        product=product,
        direction=direction,
        simultaneous=simultaneous,
        exact_tie=exact_tie,
        terminal_plus=terminal_plus,
        terminal_minus=terminal_minus,
    )


def simulate_raw_arl(
    *,
    n_paths: int,
    threshold: float,
    rng: np.random.Generator,
    max_steps: int = 4_000_000,
) -> float:
    """Memory-light reset-cycle ARL simulation for calibration."""
    if n_paths < 1:
        raise ValueError("n_paths must be positive")
    if threshold <= 1.0:
        raise ValueError("SR threshold must be in natural units and exceed one")
    r_plus = np.zeros(n_paths)
    r_minus = np.zeros(n_paths)
    active = np.ones(n_paths, dtype=bool)
    total_tau = 0

    for step in range(1, max_steps + 1):
        live = np.flatnonzero(active)
        if live.size == 0:
            return total_tau / n_paths
        z = rng.standard_normal(live.size)
        new_plus, new_minus = raw_step(r_plus[live], r_minus[live], z)
        r_plus[live] = new_plus
        r_minus[live] = new_minus
        crossed = (new_plus >= threshold) | (new_minus >= threshold)
        if crossed.any():
            done = live[crossed]
            total_tau += step * done.size
            active[done] = False
    raise RuntimeError(f"{int(active.sum())} raw SR ARL paths did not alarm")

