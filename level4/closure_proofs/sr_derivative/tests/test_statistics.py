from __future__ import annotations

import numpy as np

from rebaseguard_sr_derivative.statistics import (
    independent_z,
    mean_se,
    one_sided_t_lower,
    paired_central_derivative,
)


def test_paired_derivative_se_uses_batch_differences():
    shared = np.arange(1.0, 65.0)
    perturbation = np.tile(np.array([-0.1, 0.1]), 32)
    h = 0.05
    plus = shared + perturbation
    minus = shared - perturbation
    paired = paired_central_derivative(plus, minus, h)
    signwise_independence_se = np.hypot(mean_se(plus).se, mean_se(minus).se) / (2 * h)
    assert paired.se < signwise_independence_se / 100.0
    assert abs(paired.mean) < 1e-14


def test_independent_z_combines_only_independent_route_ses():
    left = mean_se(np.array([1.0, 2.0, 3.0, 4.0]))
    right = mean_se(np.array([1.5, 2.5, 3.5, 4.5]))
    expected = (left.mean - right.mean) / np.hypot(left.se, right.se)
    assert independent_z(left, right) == expected


def test_one_sided_99_percent_lower_bound_uses_batch_degrees_of_freedom():
    summary = mean_se(np.arange(64.0))
    lower = one_sided_t_lower(summary, 0.99)
    assert lower < summary.mean
    assert summary.n == 64
