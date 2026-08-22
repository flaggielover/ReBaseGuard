"""Route B: independently written log-state conditional-map simulator.

No recursion, stopping, score, Gamma, or theorem helper is shared with Route A
or Stage D.  Full innovation vectors at each time make the common random
numbers addressable by `(path,time)` even when conditions stop differently.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

TIE = np.int8(0)
UP = np.int8(1)
DOWN = np.int8(-1)


@dataclass(slots=True)
class LogPathRecord:
    tau: int | None
    terminal_z: float | None
    stopped_sum: float
    map_output: float | None
    direction: int | None
    simultaneous: bool
    exact_tie: bool
    y_plus: float
    y_minus: float


@dataclass(slots=True)
class PairedLogBatch:
    h_grid: np.ndarray
    map_output: np.ndarray
    tau: np.ndarray
    terminal_z: np.ndarray
    stopped_sum: np.ndarray
    direction: np.ndarray
    simultaneous: np.ndarray
    exact_tie: np.ndarray

    @property
    def derivatives(self) -> np.ndarray:
        means = self.map_output.mean(axis=2)
        return (means[:, 0] - means[:, 1]) / (2.0 * self.h_grid)


def log_step(
    y_plus: np.ndarray | float,
    y_minus: np.ndarray | float,
    z: np.ndarray | float,
) -> tuple[
    np.ndarray | float,
    np.ndarray | float,
    np.ndarray | float,
    np.ndarray | float,
]:
    """One log-state SR update, returning stored states and raw-state logs."""
    ell_plus = y_plus + z - 0.5
    ell_minus = y_minus - z - 0.5
    new_y_plus = np.logaddexp(0.0, ell_plus)
    new_y_minus = np.logaddexp(0.0, ell_minus)
    return new_y_plus, new_y_minus, ell_plus, ell_minus


def classify_alarm_logs(
    ell_plus: np.ndarray | float,
    ell_minus: np.ndarray | float,
    log_threshold: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Classify crossings by the post-update raw-state logarithms."""
    plus = np.asarray(ell_plus)
    minus = np.asarray(ell_minus)
    crossed_plus = plus >= log_threshold
    crossed_minus = minus >= log_threshold
    crossed = crossed_plus | crossed_minus
    simultaneous = crossed_plus & crossed_minus
    exact_tie = simultaneous & (plus == minus)
    direction = np.where(
        exact_tie,
        TIE,
        np.where(plus > minus, UP, DOWN),
    ).astype(np.int8)
    return crossed, direction, simultaneous, exact_tie


def run_log_path(
    innovations: np.ndarray,
    *,
    threshold: float,
    e: float = 0.0,
) -> LogPathRecord:
    """Run one deterministic path from reset using only the log recursion."""
    if threshold <= 1.0:
        raise ValueError("SR threshold must be in natural units and exceed one")
    log_threshold = float(np.log(threshold))
    y_plus = 0.0
    y_minus = 0.0
    total = 0.0
    for step, epsilon in enumerate(np.asarray(innovations, dtype=float), start=1):
        z = float(epsilon - e)
        y_plus, y_minus, ell_plus, ell_minus = log_step(y_plus, y_minus, z)
        total += z
        crossed, direction, simultaneous, exact_tie = classify_alarm_logs(
            ell_plus, ell_minus, log_threshold
        )
        if bool(crossed):
            return LogPathRecord(
                tau=step,
                terminal_z=z,
                stopped_sum=total,
                map_output=e + z,
                direction=int(direction),
                simultaneous=bool(simultaneous),
                exact_tie=bool(exact_tie),
                y_plus=float(y_plus),
                y_minus=float(y_minus),
            )
    return LogPathRecord(
        tau=None,
        terminal_z=None,
        stopped_sum=total,
        map_output=None,
        direction=None,
        simultaneous=False,
        exact_tie=False,
        y_plus=float(y_plus),
        y_minus=float(y_minus),
    )


def simulate_paired_log_batch(
    *,
    n_paths: int,
    threshold: float,
    h_grid: np.ndarray,
    rng: np.random.Generator,
    max_steps: int = 4_000_000,
) -> PairedLogBatch:
    """Simulate the entire paired central-difference ladder in one CRN batch."""
    if n_paths < 1:
        raise ValueError("n_paths must be positive")
    if threshold <= 1.0:
        raise ValueError("SR threshold must be in natural units and exceed one")
    h_grid = np.asarray(h_grid, dtype=float)
    if h_grid.ndim != 1 or h_grid.size == 0 or np.any(h_grid <= 0.0):
        raise ValueError("h_grid must be a nonempty vector of positive steps")

    n_steps = h_grid.size
    e_values = np.stack((h_grid, -h_grid), axis=1)
    log_threshold = float(np.log(threshold))
    shape = (n_steps, 2, n_paths)
    y_plus = np.zeros(shape)
    y_minus = np.zeros(shape)
    total = np.zeros(shape)
    active = np.ones(shape, dtype=bool)

    map_output = np.full(shape, np.nan)
    tau = np.zeros(shape, dtype=np.int64)
    terminal_z = np.zeros(shape)
    stopped_sum = np.zeros(shape)
    direction = np.zeros(shape, dtype=np.int8)
    simultaneous = np.zeros(shape, dtype=bool)
    exact_tie = np.zeros(shape, dtype=bool)

    for step in range(1, max_steps + 1):
        if not active.any():
            break
        epsilon = rng.standard_normal(n_paths)
        z = epsilon[None, None, :] - e_values[:, :, None]
        new_y_plus, new_y_minus, ell_plus, ell_minus = log_step(
            y_plus, y_minus, z
        )
        was_active = active
        y_plus = np.where(was_active, new_y_plus, y_plus)
        y_minus = np.where(was_active, new_y_minus, y_minus)
        total += np.where(was_active, z, 0.0)

        crossed_plus = (ell_plus >= log_threshold) & was_active
        crossed_minus = (ell_minus >= log_threshold) & was_active
        crossed = crossed_plus | crossed_minus
        if not crossed.any():
            continue
        both = crossed_plus & crossed_minus
        tied = both & (ell_plus == ell_minus)
        alarm_direction = np.where(
            tied,
            TIE,
            np.where(ell_plus > ell_minus, UP, DOWN),
        ).astype(np.int8)
        tau[crossed] = step
        terminal_z[crossed] = z[crossed]
        stopped_sum[crossed] = total[crossed]
        map_values = e_values[:, :, None] + z
        map_output[crossed] = map_values[crossed]
        direction[crossed] = alarm_direction[crossed]
        simultaneous[crossed] = both[crossed]
        exact_tie[crossed] = tied[crossed]
        active = was_active & ~crossed
    else:
        raise RuntimeError(f"{int(active.sum())} paired log SR conditions did not alarm")

    return PairedLogBatch(
        h_grid=h_grid,
        map_output=map_output,
        tau=tau,
        terminal_z=terminal_z,
        stopped_sum=stopped_sum,
        direction=direction,
        simultaneous=simultaneous,
        exact_tie=exact_tie,
    )

