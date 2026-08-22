from __future__ import annotations

import numpy as np
import pytest

from rebaseguard_mgt1.model import (
    gamma_components, mixed_update, predicted_derivative, truncated_window,
)


def test_tau_less_than_m_uses_tau_denominator():
    lags = np.array([[3.0, 2.0, 1.0, 0.0, 0.0]])
    total, mean = truncated_window(lags, np.array([3]), 5)
    assert total[0] == 6.0
    assert mean[0] == 2.0


def test_tau_at_least_m_uses_m_denominator():
    lags = np.array([[4.0, 3.0, 2.0, 1.0, 9.0]])
    total, mean = truncated_window(lags, np.array([5]), 3)
    assert total[0] == 9.0
    assert mean[0] == 3.0


def test_m1_is_terminal_observation():
    lags = np.array([[7.0], [-4.0]])
    total, mean = truncated_window(lags, np.array([1, 8]), 1)
    assert np.array_equal(total, np.array([7.0, -4.0]))
    assert np.array_equal(mean, total)


@pytest.mark.parametrize("m", [0, -1])
def test_truncated_window_rejects_nonpositive_m(m):
    with pytest.raises(ValueError):
        truncated_window(np.zeros((1, 1)), np.array([1]), m)


def test_short_cycle_gamma_correction_is_exact():
    a, b, c = gamma_components(np.array([2]), np.array([3.0]), np.array([3.0]), 5)
    assert a[0] == pytest.approx(4.5)
    assert b[0] == pytest.approx(1.8)
    assert c[0] == pytest.approx(2.7)
    assert a[0] == pytest.approx(b[0] + c[0])


def test_long_cycle_gamma_correction_is_zero():
    a, b, c = gamma_components(np.array([8]), np.array([3.0]), np.array([5.0]), 5)
    assert c[0] == 0.0
    assert a[0] == b[0]


def test_short_correction_is_nonnegative():
    tau = np.array([1, 2, 4, 8])
    t = np.array([-6.0, 2.0, -3.0, 1.0])
    sums = np.where(tau < 5, t, 2.0)
    _, _, c = gamma_components(tau, t, sums, 5)
    assert np.all(c >= 0.0)


def test_rho_zero_is_fresh_only():
    got = mixed_update(np.array([2.0]), np.array([3.0]), np.array([-1.0]), 0.0)
    assert got[0] == -1.0


def test_rho_one_is_full_reuse_with_additive_e():
    got = mixed_update(np.array([2.0]), np.array([3.0]), np.array([-1.0]), 1.0)
    assert got[0] == 5.0


def test_rho_midpoint_is_affine_mix():
    got = mixed_update(np.array([2.0]), np.array([3.0]), np.array([-1.0]), 0.25)
    assert got[0] == pytest.approx(0.5)


def test_rho_outside_unit_interval_rejected():
    with pytest.raises(ValueError):
        mixed_update(np.array([0.0]), np.array([0.0]), np.array([0.0]), 1.1)


def test_predicted_derivative_formula_and_endpoints():
    gamma = np.array([4.0, 2.0])
    assert np.array_equal(predicted_derivative(gamma, 1.0), np.array([-3.0, -1.0]))
    assert np.array_equal(predicted_derivative(gamma, 0.0), np.zeros(2))
