from __future__ import annotations

import numpy as np
import pytest

from rebaseguard_mgt1a.model import (
    gamma_components,
    predicted_derivative,
    stage_a_integrand,
    truncated_window,
)


def test_stage_d_short_cycle_uses_tau_denominator():
    lags = np.array([[3.0, 2.0, 1.0, 0.0, 0.0]])
    total, mean = truncated_window(lags, np.array([3]), 5)
    assert total[0] == 6.0
    assert mean[0] == 2.0


def test_stage_d_long_cycle_uses_m_denominator():
    lags = np.array([[4.0, 3.0, 2.0, 1.0, 9.0]])
    total, mean = truncated_window(lags, np.array([5]), 3)
    assert total[0] == 9.0
    assert mean[0] == 3.0


def test_short_cycle_decomposition_and_nonnegative_correction():
    direct, fixed, correction = gamma_components(
        np.array([2]), np.array([3.0]), np.array([3.0]), 5
    )
    assert direct[0] == pytest.approx(4.5)
    assert fixed[0] == pytest.approx(1.8)
    assert correction[0] == pytest.approx(2.7)
    assert direct[0] == pytest.approx(fixed[0] + correction[0])
    assert correction[0] >= 0.0


def test_long_cycle_correction_is_zero():
    direct, fixed, correction = gamma_components(
        np.array([8]), np.array([3.0]), np.array([5.0]), 5
    )
    assert direct[0] == fixed[0]
    assert correction[0] == 0.0


def test_m1_reduces_to_terminal_observation_and_zero_correction():
    lags = np.array([[7.0], [-4.0]])
    tau = np.array([1, 8])
    sums, means = truncated_window(lags, tau, 1)
    assert np.array_equal(sums, lags[:, 0])
    assert np.array_equal(means, lags[:, 0])
    direct, fixed, correction = gamma_components(tau, np.array([2.0, 3.0]), sums, 1)
    assert np.array_equal(direct, fixed)
    assert np.array_equal(correction, np.zeros(2))


def test_stage_a_integrand_always_uses_fixed_m():
    got = stage_a_integrand(np.array([10.0]), np.array([3.0]), 5)
    assert got[0] == 6.0


def test_rho_scaling_formula():
    gamma = np.array([4.0, 2.0])
    assert np.array_equal(predicted_derivative(gamma, 1.0), np.array([-3.0, -1.0]))
    assert np.array_equal(predicted_derivative(gamma, 0.0), np.zeros(2))
    assert np.array_equal(predicted_derivative(gamma, 0.5), np.array([-1.5, -0.5]))

