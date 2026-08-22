from __future__ import annotations

import numpy as np
import pytest

from rebaseguard_mgt1a.analysis import Moments, inverse_variance_pool, wilson_interval


def test_moments_match_direct_statistics():
    values = np.array([[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]])
    moments = Moments.zeros((2,))
    moments.add(values[:2])
    moments.add(values[2:])
    assert np.allclose(moments.mean, values.mean(axis=0))
    assert np.allclose(moments.sd, values.std(axis=0, ddof=1))
    assert np.allclose(moments.se, values.std(axis=0, ddof=1) / np.sqrt(3))


def test_inverse_variance_pool_known_case():
    value, se = inverse_variance_pool(np.array([1.0, 3.0]), np.array([1.0, 1.0]))
    assert value == pytest.approx(2.0)
    assert se == pytest.approx(1.0 / np.sqrt(2.0))


def test_inverse_variance_rejects_zero_se():
    with pytest.raises(ValueError):
        inverse_variance_pool(np.array([1.0, 1.0]), np.array([0.0, 1.0]))


def test_wilson_zero_count_is_finite_and_nonnegative():
    low, high = wilson_interval(0, 1_000_000)
    assert low >= 0.0
    assert 0.0 < high < 1e-4

