"""Vectorized symmetric-SR simulation for non-rigorous diagnostics."""

from __future__ import annotations

import math

import numpy as np
from scipy.special import ndtri

from rebaseguard_phase4b.harness import StoppingSample
from rebaseguard_phase4b.sr_model import FROZEN_DELTA


_MASK = (1 << 64) - 1
_MIX1 = np.uint64(0xBF58476D1CE4E5B9)
_MIX2 = np.uint64(0x94D049BB133111EB)
_TIME_MIX = 0x9E3779B97F4A7C15
_PATH_MIX = np.uint64(0xD2B74407B1CE6E93)


def _counter_normals(seed: int, time: int, indices: np.ndarray) -> np.ndarray:
    """Path/time-addressable deterministic normals for calibration CRN."""

    time_word = np.uint64((int(time) * _TIME_MIX) & _MASK)
    values = np.multiply(indices.astype(np.uint64) + np.uint64(1), _PATH_MIX)
    values ^= np.uint64(seed & _MASK) ^ time_word
    values ^= values >> np.uint64(30)
    values = np.multiply(values, _MIX1)
    values ^= values >> np.uint64(27)
    values = np.multiply(values, _MIX2)
    values ^= values >> np.uint64(31)
    uniforms = ((values >> np.uint64(11)).astype(np.float64) + 0.5) * (2.0**-53)
    return ndtri(uniforms)


def simulate_symmetric_sr(
    n: int,
    *,
    threshold: float,
    seed: int,
    error: float = 0.0,
    delta: float = FROZEN_DELTA,
    counter_based: bool = False,
    max_steps: int = 100_000,
) -> StoppingSample:
    if n <= 0:
        raise ValueError("n must be positive")
    if threshold <= 0.0:
        raise ValueError("threshold must be positive")
    if delta != FROZEN_DELTA:
        raise ValueError("Phase-4B freezes delta=1")
    rng = None if counter_based else np.random.default_rng(seed)
    log_threshold = math.log(threshold)
    y_plus = np.zeros(n)
    y_minus = np.zeros(n)
    total = np.zeros(n)
    active = np.ones(n, dtype=bool)
    tau = np.zeros(n, dtype=np.int64)
    z_tau = np.zeros(n)
    t_tau = np.zeros(n)
    arm = np.zeros(n, dtype=np.int8)

    for time in range(1, max_steps + 1):
        indices = np.flatnonzero(active)
        if indices.size == 0:
            break
        if counter_based:
            z = _counter_normals(seed, time, indices) - error
        else:
            assert rng is not None
            z = rng.standard_normal(indices.size) - error
        log_r_plus = y_plus[indices] + z - 0.5
        log_r_minus = y_minus[indices] - z - 0.5
        total[indices] += z
        y_plus[indices] = np.logaddexp(0.0, log_r_plus)
        y_minus[indices] = np.logaddexp(0.0, log_r_minus)
        plus_crossed = log_r_plus >= log_threshold
        minus_crossed = log_r_minus >= log_threshold
        fired = plus_crossed | minus_crossed
        if np.any(fired):
            done = indices[fired]
            done_plus = plus_crossed[fired]
            done_minus = minus_crossed[fired]
            done_log_plus = log_r_plus[fired]
            done_log_minus = log_r_minus[fired]
            directions = np.where(
                done_plus & done_minus,
                np.where(
                    done_log_plus > done_log_minus,
                    1,
                    np.where(done_log_minus > done_log_plus, -1, 2),
                ),
                np.where(done_plus, 1, -1),
            )
            tau[done] = time
            z_tau[done] = z[fired]
            t_tau[done] = total[done]
            arm[done] = directions
            active[done] = False
    else:
        raise RuntimeError(f"{int(np.sum(active))} SR paths did not alarm")

    return StoppingSample(tau, z_tau, t_tau, arm)

