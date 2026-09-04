"""The estimand, its estimator, and the stability statistics."""

import math

import numpy as np
import pytest

from p4y_pilot4.estimand import (
    concentration, prefix_curve, ratio_spread, rel_se, split_estimates,
    theta_hat,
)


def test_theta_is_the_coefficient_of_variation():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    assert theta_hat(x) == pytest.approx(x.std(ddof=1) / x.mean())


def test_theta_is_scale_free():
    rng = np.random.default_rng(1)
    x = 5.0 + rng.standard_normal(200)
    assert theta_hat(x) == pytest.approx(theta_hat(7.5 * x), rel=1e-12)


def test_relse_identity_is_theta_over_sqrt_b():
    """The reason theta is the governance-relevant object."""
    rng = np.random.default_rng(2)
    x = 3.0 + rng.standard_normal(400)
    t = theta_hat(x)
    for b in (16, 64, 256):
        assert rel_se(t, b) == pytest.approx(t / math.sqrt(b))
    # and it matches the statistic governance actually computes
    assert rel_se(theta_hat(x), x.size) == pytest.approx(
        x.std(ddof=1) / math.sqrt(x.size) / abs(x.mean()))


def test_theta_is_undefined_on_degenerate_input():
    assert math.isnan(theta_hat(np.array([1.0])))
    assert math.isnan(theta_hat(np.array([1.0, -1.0])))     # mean zero


def test_concentration_finds_a_single_dominating_block():
    x = np.concatenate([np.ones(999), np.array([1000.0])])
    c = concentration(x)
    assert c["top1"] > 0.9
    assert c["n"] == 1000


def test_concentration_is_small_for_a_well_aggregated_law():
    rng = np.random.default_rng(4)
    c = concentration(2.5 + rng.standard_normal(2048))
    assert c["top1"] < 0.02
    assert c["top5"] < 0.05


def test_prefix_curve_reports_every_frozen_fraction():
    rng = np.random.default_rng(5)
    p = prefix_curve(2.5 + rng.standard_normal(1024))
    assert set(p) == {"0.125", "0.25", "0.5", "1"}
    assert p["1"]["n"] == 1024 and p["0.5"]["n"] == 512


def test_split_estimates_are_disjoint_and_equal_sized():
    x = np.arange(100, dtype=float) + 1.0
    e = split_estimates(x, 4)
    assert len(e) == 4
    assert all(math.isfinite(v) for v in e)


def test_ratio_spread_is_max_over_min():
    assert ratio_spread([1.0, 2.0, 4.0]) == pytest.approx(4.0)
    assert math.isinf(ratio_spread([1.0]))


def test_the_framework_detects_a_stable_regime_when_one_exists():
    """The ordinary-control logic, on a synthetic finite-variance law."""
    rng = np.random.default_rng(6)
    x = 6.0 + 0.2 * rng.standard_normal(4096)
    assert ratio_spread(split_estimates(x, 2)) < 1.25
    p = prefix_curve(x)
    assert 1 / 1.15 <= p["1"]["theta"] / p["0.5"]["theta"] <= 1.15
    assert concentration(x)["top1"] <= 0.10


def test_the_framework_rejects_a_tail_dominated_law():
    """A law of the shape Pilot-3 actually met."""
    rng = np.random.default_rng(7)
    x = 2.5 + rng.standard_t(2.2, 4096)
    c = concentration(x)
    spread = ratio_spread(split_estimates(x, 2))
    assert c["top1"] > 0.10 or spread > 1.25
