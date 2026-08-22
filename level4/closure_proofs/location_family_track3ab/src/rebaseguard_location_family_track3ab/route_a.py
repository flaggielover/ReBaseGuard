"""Route A: raw nonnegative-chart CUSUM stopped-score estimator.

This is the validated Track-3 raw-state algorithm restricted to unit-variance
t3 and instrumented for resumable variance-aware batch summaries.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .frozen import DEGREES_OF_FREEDOM, K, UNIT_VARIANCE_SCALE


@dataclass(frozen=True, slots=True)
class ScorePaths:
    tau: np.ndarray
    terminal: np.ndarray
    score_sum: np.ndarray
    direction: np.ndarray
    ties: int
    simultaneous_crossings: int

    @property
    def gain(self) -> np.ndarray:
        return self.terminal * self.score_sum


def draw_t3(generator: np.random.Generator, count: int) -> np.ndarray:
    return generator.standard_t(DEGREES_OF_FREEDOM, size=count) / UNIT_VARIANCE_SCALE


def t3_location_score(z: np.ndarray) -> np.ndarray:
    """Conventional unit-variance t3 location score: 4z/(1+z^2)."""
    data = np.asarray(z, dtype=float)
    return 4.0 * data / (1.0 + data * data)


def simulate_score_batch(
    *,
    threshold: float,
    n_paths: int,
    generator: np.random.Generator,
    max_steps: int = 4_000_000,
) -> ScorePaths:
    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    score_sum = np.zeros(n_paths)
    active = np.ones(n_paths, dtype=bool)
    tau = np.zeros(n_paths, dtype=np.int64)
    terminal = np.zeros(n_paths)
    direction = np.zeros(n_paths, dtype=np.int8)
    ties = 0
    simultaneous = 0

    for step in range(1, max_steps + 1):
        index = np.flatnonzero(active)
        if index.size == 0:
            break
        z = draw_t3(generator, index.size)
        next_plus = np.maximum(0.0, plus[index] + z - K)
        next_minus = np.maximum(0.0, minus[index] - z - K)
        plus[index] = next_plus
        minus[index] = next_minus
        score_sum[index] += t3_location_score(z)
        crossed_plus = next_plus >= threshold
        crossed_minus = next_minus >= threshold
        crossed = crossed_plus | crossed_minus
        if not crossed.any():
            continue
        both = crossed_plus & crossed_minus
        count_both = int(np.count_nonzero(both))
        ties += count_both
        simultaneous += count_both
        done = index[crossed]
        tau[done] = step
        terminal[done] = z[crossed]
        direction[done] = (
            crossed_plus[crossed].astype(np.int8)
            - crossed_minus[crossed].astype(np.int8)
        )
        active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} Route-A paths did not alarm")

    return ScorePaths(
        tau=tau,
        terminal=terminal,
        score_sum=score_sum,
        direction=direction,
        ties=ties,
        simultaneous_crossings=simultaneous,
    )


def summarize_score_paths(paths: ScorePaths) -> dict:
    gain = paths.gain
    centered_sq = (gain - gain.mean()) ** 2
    order = np.argsort(np.abs(gain))[::-1]
    top_one_percent = order[: max(1, int(np.ceil(0.01 * gain.size)))]
    return {
        "paths": int(gain.size),
        "gamma_f": float(gain.mean()),
        "gain_sample_variance": float(gain.var(ddof=1)),
        "gain_min": float(gain.min()),
        "gain_q001": float(np.quantile(gain, 0.001)),
        "gain_q01": float(np.quantile(gain, 0.01)),
        "gain_median": float(np.median(gain)),
        "gain_q99": float(np.quantile(gain, 0.99)),
        "gain_q999": float(np.quantile(gain, 0.999)),
        "gain_max": float(gain.max()),
        "top_one_percent_abs_gain_variance_share": float(
            centered_sq[top_one_percent].sum() / centered_sq.sum()
        ),
        "arl": float(paths.tau.mean()),
        "terminal_mean": float(paths.terminal.mean()),
        "score_sum_mean": float(paths.score_sum.mean()),
        "direction_mean": float(paths.direction.mean()),
        "ties": paths.ties,
        "simultaneous_crossings": paths.simultaneous_crossings,
    }
