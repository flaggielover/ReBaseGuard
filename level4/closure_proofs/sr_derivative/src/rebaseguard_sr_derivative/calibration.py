"""Frozen calibration-reproduction and fixed-operating-point checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .raw_sr import simulate_raw_arl


@dataclass(slots=True)
class BisectionResult:
    target_cusum_arl: float
    iterations: list[dict[str, float | int]]
    lower: float
    upper: float
    candidate: float
    candidate_arl_fresh: float


def simulate_cusum_arl(
    *,
    n_paths: int,
    rng: np.random.Generator,
    k: float = 0.5,
    h: float = 5.0,
    max_steps: int = 4_000_000,
) -> float:
    """Reset-cycle ARL for the frozen inclusive two-sided CUSUM."""
    if n_paths < 1:
        raise ValueError("n_paths must be positive")
    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    active = np.ones(n_paths, dtype=bool)
    total_tau = 0
    for step in range(1, max_steps + 1):
        live = np.flatnonzero(active)
        if live.size == 0:
            return total_tau / n_paths
        z = rng.standard_normal(live.size)
        new_plus = np.maximum(0.0, plus[live] + z - k)
        new_minus = np.maximum(0.0, minus[live] - z - k)
        plus[live] = new_plus
        minus[live] = new_minus
        crossed = (new_plus >= h) | (new_minus >= h)
        if crossed.any():
            done = live[crossed]
            total_tau += step * done.size
            active[done] = False
    raise RuntimeError(f"{int(active.sum())} CUSUM ARL paths did not alarm")


def reproduce_sr_calibration(
    *,
    master_seed: int,
    target_paths: int = 800_000,
    search_paths: int = 200_000,
    final_paths: int = 800_000,
    lower: float = 100.0,
    upper: float = 3000.0,
    log_width_tolerance: float = 1e-3,
    max_iterations: int = 30,
    progress: Callable[[int, float, float, float], None] | None = None,
) -> BisectionResult:
    """Execute the precommitted fresh SR threshold bisection."""
    target_rng = np.random.default_rng(np.random.SeedSequence([master_seed, 1, 0]))
    target = simulate_cusum_arl(n_paths=target_paths, rng=target_rng)
    lo = float(lower)
    hi = float(upper)
    rows: list[dict[str, float | int]] = []
    for iteration in range(max_iterations):
        if np.log(hi) - np.log(lo) <= log_width_tolerance:
            break
        candidate = float(np.sqrt(lo * hi))
        rng = np.random.default_rng(
            np.random.SeedSequence([master_seed, 1, 1, iteration])
        )
        arl = simulate_raw_arl(
            n_paths=search_paths, threshold=candidate, rng=rng
        )
        rows.append(
            {
                "iteration": iteration,
                "lower_before": lo,
                "upper_before": hi,
                "candidate": candidate,
                "sr_arl": arl,
            }
        )
        if progress is not None:
            progress(iteration, candidate, arl, target)
        if arl < target:
            lo = candidate
        else:
            hi = candidate
    candidate = float(np.sqrt(lo * hi))
    final_rng = np.random.default_rng(np.random.SeedSequence([master_seed, 1, 2]))
    final_arl = simulate_raw_arl(
        n_paths=final_paths, threshold=candidate, rng=final_rng
    )
    return BisectionResult(
        target_cusum_arl=target,
        iterations=rows,
        lower=lo,
        upper=hi,
        candidate=candidate,
        candidate_arl_fresh=final_arl,
    )
