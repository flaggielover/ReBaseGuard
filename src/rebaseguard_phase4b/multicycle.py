"""Non-rigorous multi-cycle simulation for the frozen symmetric SR detector."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class MultiCycleSample:
    reference_error: np.ndarray
    prior_error: np.ndarray
    cycle_length: np.ndarray
    arm: np.ndarray
    terminal_residual: np.ndarray
    chains: int
    cycles_per_chain: int
    burn_in_cycles: int

    def summary(self) -> dict[str, float | int | list[float]]:
        errors = self.reference_error.reshape(self.chains, self.cycles_per_chain)
        arms = self.arm.reshape(self.chains, self.cycles_per_chain)
        x0 = errors[:, :-1].ravel()
        x1 = errors[:, 1:].ravel()
        d0 = arms[:, :-1].ravel().astype(float)
        d1 = arms[:, 1:].ravel().astype(float)
        quantiles = np.quantile(self.reference_error, [0.01, 0.05, 0.5, 0.95, 0.99])
        return {
            "n_cycles": int(self.reference_error.size),
            "chains": self.chains,
            "cycles_per_chain": self.cycles_per_chain,
            "burn_in_cycles": self.burn_in_cycles,
            "mean_reference_error": float(np.mean(self.reference_error)),
            "sd_reference_error": float(np.std(self.reference_error, ddof=1)),
            "reference_error_quantiles_01_05_50_95_99": quantiles.tolist(),
            "fraction_abs_error_gt_1": float(np.mean(np.abs(self.reference_error) > 1.0)),
            "fraction_abs_error_gt_2": float(np.mean(np.abs(self.reference_error) > 2.0)),
            "fraction_abs_error_gt_3": float(np.mean(np.abs(self.reference_error) > 3.0)),
            "lag1_reference_correlation": float(np.corrcoef(x0, x1)[0, 1]),
            "mean_prior_times_new_error": float(
                np.mean(self.prior_error * self.reference_error)
            ),
            "mean_cycle_length": float(np.mean(self.cycle_length)),
            "sd_cycle_length": float(np.std(self.cycle_length, ddof=1)),
            "plus_fraction": float(np.mean(self.arm == 1)),
            "minus_fraction": float(np.mean(self.arm == -1)),
            "alarm_direction_lag_product": float(np.mean(d0 * d1)),
            "alarm_direction_alternation_fraction": float(np.mean(d0 != d1)),
            "prior_error_alarm_direction_correlation": float(
                np.corrcoef(self.prior_error, self.arm.astype(float))[0, 1]
            ),
            "mean_terminal_residual": float(np.mean(self.terminal_residual)),
        }


def simulate_multicycle_sr(
    *,
    threshold: float,
    rho: float,
    seed: int,
    chains: int = 512,
    cycles_per_chain: int = 120,
    burn_in_cycles: int = 30,
    max_observation_rounds: int = 2_000_000,
) -> MultiCycleSample:
    """Simulate independent chains, resetting the SR state at every alarm.

    The next reference error is

        rho * (e + Z_tau) + (1-rho) * X_fresh,

    where ``X_fresh`` is an independent N(0,1) physical observation.
    """

    if threshold <= 0.0:
        raise ValueError("threshold must be positive")
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [0,1]")
    if chains <= 1 or cycles_per_chain <= 1 or burn_in_cycles < 0:
        raise ValueError("invalid chain/cycle configuration")

    rng = np.random.default_rng(seed)
    log_threshold = math.log(threshold)
    total_cycles = burn_in_cycles + cycles_per_chain
    error = np.zeros(chains)
    y_plus = np.zeros(chains)
    y_minus = np.zeros(chains)
    length = np.zeros(chains, dtype=np.int64)
    completed = np.zeros(chains, dtype=np.int64)
    shape = (chains, cycles_per_chain)
    errors = np.empty(shape)
    priors = np.empty(shape)
    lengths = np.empty(shape, dtype=np.int64)
    arms = np.empty(shape, dtype=np.int8)
    terminal = np.empty(shape)

    for _round in range(max_observation_rounds):
        indices = np.flatnonzero(completed < total_cycles)
        if indices.size == 0:
            break
        prior = error[indices]
        z = rng.standard_normal(indices.size) - prior
        log_r_plus = y_plus[indices] + z - 0.5
        log_r_minus = y_minus[indices] - z - 0.5
        y_plus[indices] = np.logaddexp(0.0, log_r_plus)
        y_minus[indices] = np.logaddexp(0.0, log_r_minus)
        length[indices] += 1
        plus_crossed = log_r_plus >= log_threshold
        minus_crossed = log_r_minus >= log_threshold
        fired = plus_crossed | minus_crossed
        if not np.any(fired):
            continue

        done = indices[fired]
        done_z = z[fired]
        old_error = error[done].copy()
        done_log_plus = log_r_plus[fired]
        done_log_minus = log_r_minus[fired]
        direction = np.where(done_log_plus >= done_log_minus, 1, -1).astype(np.int8)
        selected_physical = old_error + done_z
        fresh = rng.standard_normal(done.size)
        new_error = rho * selected_physical + (1.0 - rho) * fresh
        cycle_number = completed[done]
        retained = cycle_number >= burn_in_cycles
        if np.any(retained):
            rows = done[retained]
            cols = cycle_number[retained] - burn_in_cycles
            errors[rows, cols] = new_error[retained]
            priors[rows, cols] = old_error[retained]
            lengths[rows, cols] = length[done][retained]
            arms[rows, cols] = direction[retained]
            terminal[rows, cols] = done_z[retained]
        error[done] = new_error
        y_plus[done] = 0.0
        y_minus[done] = 0.0
        length[done] = 0
        completed[done] += 1
    else:
        unfinished = int(np.sum(completed < total_cycles))
        raise RuntimeError(f"{unfinished} multi-cycle chains did not finish")

    return MultiCycleSample(
        reference_error=errors.ravel(),
        prior_error=priors.ravel(),
        cycle_length=lengths.ravel(),
        arm=arms.ravel(),
        terminal_residual=terminal.ravel(),
        chains=chains,
        cycles_per_chain=cycles_per_chain,
        burn_in_cycles=burn_in_cycles,
    )
