"""Pure definitions for the Stage-D truncated-window theorem.

This module contains no simulator and imports no historical conditional-map
implementation. Arrays use one row per stopped path.
"""

from __future__ import annotations

import numpy as np

M_GRID = np.array([1, 2, 5, 10, 20, 50, 75, 100], dtype=np.int64)
RHO_GRID = np.array([0.0, 0.25, 0.5, 1.0])
H_LADDER = np.array([0.1, 0.05, 0.025, 0.0125])
PRIMARY_H = 0.0125


def truncated_window(lags_newest: np.ndarray, tau: np.ndarray, m: int) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(sum, mean)`` over the last ``min(m,tau)`` observations.

    ``lags_newest[:, 0]`` is the terminal observation. Entries beyond ``tau``
    must be zero. This function deliberately divides by the realized ``w``.
    """
    lags = np.asarray(lags_newest, dtype=float)
    tau = np.asarray(tau, dtype=np.int64)
    if m < 1:
        raise ValueError("m must be positive")
    if lags.ndim != 2 or tau.ndim != 1 or lags.shape[0] != tau.size:
        raise ValueError("incompatible lag and tau arrays")
    if np.any(tau < 1) or lags.shape[1] < m:
        raise ValueError("tau must be positive and enough lags must be supplied")
    w = np.minimum(m, tau)
    csum = np.cumsum(lags[:, :m], axis=1)
    window_sum = csum[np.arange(tau.size), w - 1]
    return window_sum, window_sum / w


def gamma_components(
    tau: np.ndarray, t_tau: np.ndarray, window_sum: np.ndarray, m: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pathwise ``(GammaA integrand, GammaB integrand, short correction)``.

    The returned arrays obey ``A = B + C`` up to floating-point roundoff when
    ``window_sum`` is the sum over the actual truncated window.
    """
    tau = np.asarray(tau, dtype=np.int64)
    t_tau = np.asarray(t_tau, dtype=float)
    window_sum = np.asarray(window_sum, dtype=float)
    if m < 1 or np.any(tau < 1):
        raise ValueError("m and tau must be positive")
    w = np.minimum(m, tau)
    a = (window_sum / w) * t_tau
    b = (window_sum / m) * t_tau
    c = np.where(tau < m, (1.0 / tau - 1.0 / m) * t_tau**2, 0.0)
    return a, b, c


def mixed_update(e: np.ndarray, zbar: np.ndarray, fresh: np.ndarray, rho: float) -> np.ndarray:
    """Frozen Stage-D update ``rho*(e+zbar)+(1-rho)*fresh``."""
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [0,1]")
    return rho * (np.asarray(e) + np.asarray(zbar)) + (1.0 - rho) * np.asarray(fresh)


def predicted_derivative(gamma_tilde: np.ndarray, rho: float = 1.0) -> np.ndarray:
    """The theorem prediction ``rho*(1-Gamma_tilde)``."""
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [0,1]")
    return rho * (1.0 - np.asarray(gamma_tilde, dtype=float))
