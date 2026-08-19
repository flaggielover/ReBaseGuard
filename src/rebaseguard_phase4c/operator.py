"""Exact floating-point transcription of the frozen SR continuum operator.

This module is diagnostic scaffolding, not proof evidence.  Its formulas are
the specification that later Arb prototypes independently enclose.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from scipy.integrate import quad
from scipy.special import ndtr


DELTA = 1.0
THRESHOLD_A = 520.3125
LOG_A = math.log(THRESHOLD_A)
LIVE_Y_MAX = math.log1p(THRESHOLD_A)
SQRT_2PI = math.sqrt(2.0 * math.pi)


def softplus(value: float) -> float:
    if value > 0.0:
        return value + math.log1p(math.exp(-value))
    return math.log1p(math.exp(value))


def transition(y_plus: float, y_minus: float, z: float) -> tuple[float, float]:
    """Return ``log(1+R')`` for both charts after observing ``z``."""

    return (
        softplus(y_plus + z - 0.5),
        softplus(y_minus - z - 0.5),
    )


def continuation_bounds(y_plus: float, y_minus: float) -> tuple[float, float]:
    """Return the strict continuation interval ``ell < z < u``."""

    ell = y_minus - LOG_A - 0.5
    upper = LOG_A - y_plus + 0.5
    return ell, upper


def normal_pdf(value: float) -> float:
    return math.exp(-0.5 * value * value) / SQRT_2PI


def absorbing_moments(y_plus: float, y_minus: float) -> tuple[float, float]:
    """Return alarm-tail coefficients ``r_a=E[Z;alarm]`` and ``r_b=E[Z^2;alarm]``."""

    ell, upper = continuation_bounds(y_plus, y_minus)
    phi_ell = normal_pdf(ell)
    phi_upper = normal_pdf(upper)
    r_a = phi_upper - phi_ell
    r_b = (
        ndtr(ell)
        - ell * phi_ell
        + ndtr(-upper)
        + upper * phi_upper
    )
    return r_a, r_b


def apply_continuation_operators(
    y_plus: float,
    y_minus: float,
    a: Callable[[float, float], float],
    b: Callable[[float, float], float],
) -> tuple[float, float, float]:
    """Numerically evaluate ``K a``, ``K_z a``, and ``K b`` at one point."""

    ell, upper = continuation_bounds(y_plus, y_minus)

    def weighted(z: float, function: Callable[[float, float], float]) -> float:
        q_plus, q_minus = transition(y_plus, y_minus, z)
        return function(q_plus, q_minus) * normal_pdf(z)

    k_a = quad(lambda z: weighted(z, a), ell, upper, epsabs=2e-13)[0]
    kz_a = quad(lambda z: z * weighted(z, a), ell, upper, epsabs=2e-13)[0]
    k_b = quad(lambda z: weighted(z, b), ell, upper, epsabs=2e-13)[0]
    return k_a, kz_a, k_b


def bellman_rhs(
    y_plus: float,
    y_minus: float,
    x: float,
    a: Callable[[float, float], float],
    b: Callable[[float, float], float],
) -> float:
    """Evaluate the one-step Bellman right-hand side for an affine continuation."""

    k_a, kz_a, k_b = apply_continuation_operators(y_plus, y_minus, a, b)
    r_a, r_b = absorbing_moments(y_plus, y_minus)
    return (k_a + r_a) * x + kz_a + k_b + r_b

