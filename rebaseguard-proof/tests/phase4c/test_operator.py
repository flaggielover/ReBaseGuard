from __future__ import annotations

import math

import pytest
from scipy.integrate import quad

from rebaseguard_phase4c.operator import (
    LIVE_Y_MAX,
    LOG_A,
    THRESHOLD_A,
    absorbing_moments,
    bellman_rhs,
    continuation_bounds,
    normal_pdf,
    transition,
)


@pytest.mark.parametrize(
    ("r_plus", "r_minus", "z"),
    [(0.0, 0.0, 0.2), (3.0, 7.0, -1.3), (500.0, 0.8, 0.01)],
)
def test_softplus_transition_is_exact_raw_sr_algebra(r_plus, r_minus, z):
    y_plus, y_minus = math.log1p(r_plus), math.log1p(r_minus)
    q_plus, q_minus = transition(y_plus, y_minus, z)
    raw_plus = (1.0 + r_plus) * math.exp(z - 0.5)
    raw_minus = (1.0 + r_minus) * math.exp(-z - 0.5)
    assert math.expm1(q_plus) == pytest.approx(raw_plus)
    assert math.expm1(q_minus) == pytest.approx(raw_minus)


@pytest.mark.parametrize("y_plus,y_minus", [(0.0, 0.0), (1.2, 4.3), (6.0, 0.7)])
def test_continuation_endpoints_are_exact_alarm_boundaries(y_plus, y_minus):
    ell, upper = continuation_bounds(y_plus, y_minus)
    q_at_ell = transition(y_plus, y_minus, ell)
    q_at_upper = transition(y_plus, y_minus, upper)
    assert math.expm1(q_at_ell[1]) == pytest.approx(THRESHOLD_A)
    assert math.expm1(q_at_upper[0]) == pytest.approx(THRESHOLD_A)
    assert ell == pytest.approx(y_minus - LOG_A - 0.5)
    assert upper == pytest.approx(LOG_A - y_plus + 0.5)


def test_continuation_interval_is_nonempty_on_naive_live_square():
    minimum_width = 2.0 * LOG_A + 1.0 - 2.0 * LIVE_Y_MAX
    assert minimum_width > 0.99


@pytest.mark.parametrize("y_plus,y_minus", [(0.0, 0.0), (2.0, 3.0), (6.0, 0.8)])
def test_absorbing_gaussian_moments_match_direct_quadrature(y_plus, y_minus):
    ell, upper = continuation_bounds(y_plus, y_minus)
    r_a, r_b = absorbing_moments(y_plus, y_minus)
    direct_a = quad(lambda z: z * normal_pdf(z), -math.inf, ell)[0]
    direct_a += quad(lambda z: z * normal_pdf(z), upper, math.inf)[0]
    direct_b = quad(lambda z: z * z * normal_pdf(z), -math.inf, ell)[0]
    direct_b += quad(lambda z: z * z * normal_pdf(z), upper, math.inf)[0]
    assert r_a == pytest.approx(direct_a, abs=2e-13)
    assert r_b == pytest.approx(direct_b, abs=2e-13)


def test_affine_bellman_rhs_matches_direct_reward_integral():
    y_plus, y_minus = 1.1, 2.3
    a = lambda p, m: 0.2 + 0.03 * p - 0.05 * m
    b = lambda p, m: 1.0 + 0.1 * p * m
    ell, upper = continuation_bounds(y_plus, y_minus)

    def direct(x: float) -> float:
        lower = quad(lambda z: z * (x + z) * normal_pdf(z), -math.inf, ell)[0]
        middle = quad(
            lambda z: (
                a(*transition(y_plus, y_minus, z)) * (x + z)
                + b(*transition(y_plus, y_minus, z))
            )
            * normal_pdf(z),
            ell,
            upper,
        )[0]
        upper_tail = quad(lambda z: z * (x + z) * normal_pdf(z), upper, math.inf)[0]
        return lower + middle + upper_tail

    for x in (-4.0, 0.0, 3.5):
        assert bellman_rhs(y_plus, y_minus, x, a, b) == pytest.approx(
            direct(x), abs=3e-12
        )


def test_reflection_swaps_transition_and_continuation_bounds():
    y_plus, y_minus, z = 1.4, 3.2, -0.7
    q_plus, q_minus = transition(y_plus, y_minus, z)
    reflected = transition(y_minus, y_plus, -z)
    assert reflected == pytest.approx((q_minus, q_plus))
    ell, upper = continuation_bounds(y_plus, y_minus)
    reflected_ell, reflected_upper = continuation_bounds(y_minus, y_plus)
    assert reflected_ell == pytest.approx(-upper)
    assert reflected_upper == pytest.approx(-ell)
