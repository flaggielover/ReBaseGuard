"""Controlled drift interventions applied at the residual level (protocol S5).

r_t -> r_t + delta_t * s. The real covariate, noise and dependence structure is
preserved exactly; only a known offset is added, with known timing and
magnitude.
"""
from __future__ import annotations

import numpy as np

GRAD_RAMP = 200
RECUR_ON = 300
RECUR_OFF = 300


def delta_profile(n: int, t0: int, condition: str, magnitude: float) -> np.ndarray:
    """Per-observation delta (in units of the frozen scale s)."""
    d = np.zeros(n)
    if condition == "IC":
        return d
    idx = np.arange(n)
    if condition == "STEP":
        d[idx >= t0] = magnitude
    elif condition == "GRAD":
        after = idx >= t0
        ramp = np.clip((idx - t0) / float(GRAD_RAMP), 0.0, 1.0)
        d[after] = magnitude * ramp[after]
    elif condition == "RECUR":
        phase = (idx - t0) % (RECUR_ON + RECUR_OFF)
        d[(idx >= t0) & (phase < RECUR_ON)] = magnitude
    else:
        raise ValueError(f"unknown condition {condition!r}")
    return d


def inject(residual: np.ndarray, *, scale: float, t0: int, condition: str,
           magnitude: float) -> np.ndarray:
    return residual + delta_profile(residual.size, t0, condition, magnitude) * scale


def injection_grid(n_eval: int, offset: int, k_events: int, seed: int,
                   lo_frac: float = 0.10, hi_frac: float = 0.90) -> np.ndarray:
    """Deterministic evenly spaced onsets with seeded jitter (protocol S5).

    Returned in ABSOLUTE stream indices. The grid depends only on the stream
    length and the seed -- never on any outcome -- and is identical for every
    policy, which is what makes the comparison matched.
    """
    lo = offset + int(n_eval * lo_frac)
    hi = offset + int(n_eval * hi_frac)
    base = np.linspace(lo, hi, k_events)
    spacing = (hi - lo) / max(k_events - 1, 1)
    rng = np.random.default_rng(seed)
    jit = rng.uniform(-0.05, 0.05, size=k_events) * spacing
    return np.clip(np.rint(base + jit), lo, hi).astype(np.int64)
