"""Pure Track 1A definitions for Stage-A and Stage-D stopped gains."""

from __future__ import annotations

import numpy as np

M_GRID = np.array([1, 2, 5, 10, 20, 50], dtype=np.int64)
RHO_GRID = np.array([0.0, 0.25, 0.5, 0.75, 1.0])


def truncated_window(
    lags_newest: np.ndarray, tau: np.ndarray, m: int
) -> tuple[np.ndarray, np.ndarray]:
    """Return the Stage-D sum and mean over the last ``min(m,tau)`` lags."""
    lags = np.asarray(lags_newest, dtype=float)
    tau = np.asarray(tau, dtype=np.int64)
    if m < 1:
        raise ValueError("m must be positive")
    if lags.ndim != 2 or tau.ndim != 1 or lags.shape[0] != tau.size:
        raise ValueError("incompatible lags and tau")
    if np.any(tau < 1) or lags.shape[1] < m:
        raise ValueError("positive tau and at least m lag columns required")
    w = np.minimum(m, tau)
    cumulative = np.cumsum(lags[:, :m], axis=1)
    sums = cumulative[np.arange(tau.size), w - 1]
    return sums, sums / w


def gamma_components(
    tau: np.ndarray, t_tau: np.ndarray, window_sum: np.ndarray, m: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return pathwise Stage-D direct, fixed-denominator, and correction terms."""
    tau = np.asarray(tau, dtype=np.int64)
    t_tau = np.asarray(t_tau, dtype=float)
    window_sum = np.asarray(window_sum, dtype=float)
    if m < 1 or np.any(tau < 1):
        raise ValueError("m and tau must be positive")
    if tau.shape != t_tau.shape or tau.shape != window_sum.shape:
        raise ValueError("component arrays must have equal shape")
    w = np.minimum(m, tau)
    direct = (window_sum / w) * t_tau
    fixed = (window_sum / m) * t_tau
    correction = np.where(
        tau < m,
        (1.0 / tau - 1.0 / m) * np.square(t_tau),
        0.0,
    )
    return direct, fixed, correction


def stage_a_integrand(window_sum: np.ndarray, t_tau_m: np.ndarray, m: int) -> np.ndarray:
    """Pathwise Stage-A full-window gain integrand."""
    if m < 1:
        raise ValueError("m must be positive")
    return np.asarray(window_sum, dtype=float) / m * np.asarray(t_tau_m, dtype=float)


def predicted_derivative(gamma: np.ndarray | float, rho: float = 1.0) -> np.ndarray:
    """Evaluate the theorem algebra ``rho * (1 - Gamma)``."""
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [0,1]")
    return rho * (1.0 - np.asarray(gamma, dtype=float))

