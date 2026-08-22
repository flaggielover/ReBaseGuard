from __future__ import annotations

import numpy as np
import pytest

from rebaseguard_mgt1.analysis import (
    Moments, central_difference, inverse_variance_pool, richardson,
)


def test_running_moments_mean_and_iid_se():
    m = Moments.zeros((1,))
    m.add(np.array([[1.0], [2.0], [3.0]]))
    assert m.n == 3
    assert m.mean[0] == 2.0
    assert m.se[0] == pytest.approx(1.0 / np.sqrt(3.0))


def test_running_moments_combines_batches():
    m = Moments.zeros((2,))
    m.add(np.array([[1.0, 2.0]]))
    m.add(np.array([[3.0, 4.0]]))
    assert np.array_equal(m.mean, np.array([2.0, 3.0]))


def test_central_difference_and_independent_se():
    d, s = central_difference(
        np.array([3.0]), np.array([0.2]), np.array([1.0]), np.array([0.1]), 0.5
    )
    assert d[0] == 2.0
    assert s[0] == pytest.approx(np.hypot(0.2, 0.1))


def test_central_difference_rejects_nonpositive_step():
    with pytest.raises(ValueError):
        central_difference(np.ones(1), np.ones(1), np.ones(1), np.ones(1), 0.0)


def test_inverse_variance_pool_equal_precision():
    value, se = inverse_variance_pool(np.array([[1.0], [3.0]]), np.array([[2.0], [2.0]]))
    assert value[0] == 2.0
    assert se[0] == pytest.approx(np.sqrt(2.0))


def test_inverse_variance_pool_rejects_zero_se():
    with pytest.raises(ValueError):
        inverse_variance_pool(np.ones((2, 1)), np.zeros((2, 1)))


def test_richardson_formula_and_propagation():
    value, se = richardson(np.array([4.0]), np.array([0.2]), np.array([1.0]), np.array([0.1]))
    assert value[0] == 5.0
    assert se[0] == pytest.approx(np.hypot(0.8, 0.1) / 3.0)
