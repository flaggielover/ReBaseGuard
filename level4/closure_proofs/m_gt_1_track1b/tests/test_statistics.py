from __future__ import annotations

import numpy as np

from rebaseguard_mgt1b.statistics import hotelling_crosscheck, paired_covariance


def test_covariance_formula_uses_negative_two_covariance():
    rng = np.random.default_rng(1)
    x = rng.normal(size=(64, 6))
    y = x + rng.normal(scale=1e-4, size=(64, 6))
    result = paired_covariance(x, y)
    expected = result["variance_x"] + result["variance_y"] - 2 * result["covariance"]
    assert np.allclose(result["variance_difference_formula"], expected)
    assert np.allclose(
        result["variance_difference_formula"],
        result["variance_difference_direct"],
        atol=1e-14,
    )
    assert np.all(result["paired_se"] < result["naive_independence_se"])


def test_independence_formula_when_covariance_is_zero_in_population():
    rng = np.random.default_rng(2)
    x = rng.normal(size=(100_000, 1))
    y = rng.normal(size=(100_000, 1))
    result = paired_covariance(x, y)
    assert abs(result["covariance"][0]) < 0.01


def test_hotelling_uses_full_batch_covariance():
    rng = np.random.default_rng(3)
    base = rng.normal(size=(64, 1))
    differences = np.hstack([base + rng.normal(scale=0.2, size=(64, 1)) for _ in range(6)])
    result = hotelling_crosscheck(differences)
    assert result["covariance"].shape == (6, 6)
    assert np.all(result["eigenvalues"] > 0)
    assert 0.0 <= result["p_value"] <= 1.0


def test_batch_rows_not_paths_are_hotelling_units():
    differences = np.eye(7, 6)
    result = hotelling_crosscheck(differences)
    assert result["marginal_se"].shape == (6,)

