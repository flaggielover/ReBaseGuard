"""Ordinary floating-point evaluation of the exact dynamic equations.

This module is diagnostic only. Proof-critical evaluation lives in the Arb modules.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from scipy.integrate import quad
from scipy.special import ndtr

from rebaseguard_certify.model import State, thresholds


SQRT_2PI = math.sqrt(2.0 * math.pi)


def phi(z: float) -> float:
    return math.exp(-0.5 * z * z) / SQRT_2PI


def transition(state: State, z: float, k: float) -> State:
    return State(
        max(0.0, state.plus + z - k),
        max(0.0, state.minus - z - k),
    )


def absorbing_rewards_float(state: State, k: float, h: float) -> tuple[float, float]:
    ell, upper = thresholds(state, k, h)
    r_a = phi(upper) - phi(ell)
    r_b = (
        upper * phi(upper)
        + (1.0 - ndtr(upper))
        + ndtr(ell)
        - ell * phi(ell)
    )
    return r_a, r_b


def apply_k_float(
    function: Callable[[State], float], state: State, k: float, h: float
) -> float:
    ell, upper = thresholds(state, k, h)
    value, _ = quad(
        lambda z: function(transition(state, z, k)) * phi(z),
        ell,
        upper,
        epsabs=2e-13,
        epsrel=2e-13,
        points=(k - state.plus, state.minus - k),
        limit=200,
    )
    return value


def apply_kz_float(
    function: Callable[[State], float], state: State, k: float, h: float
) -> float:
    ell, upper = thresholds(state, k, h)
    value, _ = quad(
        lambda z: z * function(transition(state, z, k)) * phi(z),
        ell,
        upper,
        epsabs=2e-13,
        epsrel=2e-13,
        points=(k - state.plus, state.minus - k),
        limit=200,
    )
    return value

