"""UCB constructions: monotonicity, level, determinism, and the mechanism.

Pilot-3 exists because a POINT estimate of a heavy-tailed scale is
median-low.  These tests pin what each construction is, and demonstrate on
synthetic laws that the point estimate under-covers while a bound does not --
before any real block is drawn.
"""

import math

import numpy as np
import pytest

from p4y_pilot3.ucb import (
    BOOTSTRAP_RESAMPLES, UCB_BASELINE, UCB_CANDIDATES, UCB_LEVEL, UCB_METHODS,
    evaluate,
)


def rng():
    return np.random.default_rng(12345)


@pytest.mark.parametrize("method", list(UCB_METHODS))
def test_every_bound_is_at_least_the_point_estimate(method):
    r = rng()
    for _ in range(50):
        x = 2.5 + r.standard_normal(32)
        p = evaluate(UCB_BASELINE, x, rng=r)
        u = evaluate(method, x, rng=r)
        assert u >= p - 1e-12, (method, p, u)


@pytest.mark.parametrize("method", list(UCB_METHODS))
def test_bounds_are_deterministic_in_their_inputs(method):
    x = 2.5 + np.random.default_rng(3).standard_normal(64)
    a = evaluate(method, x, rng=np.random.default_rng(9))
    b = evaluate(method, x, rng=np.random.default_rng(9))
    assert a == b, f"{method} is not reproducible from (data, stream)"


@pytest.mark.parametrize("method", list(UCB_METHODS))
def test_bounds_scale_correctly(method):
    """relSE is scale-free in the units of the block means."""
    r = rng()
    x = 2.5 + r.standard_normal(64)
    a = evaluate(method, x, rng=np.random.default_rng(1))
    b = evaluate(method, 10.0 * x, rng=np.random.default_rng(1))
    assert a == pytest.approx(b, rel=1e-9)


def test_the_frozen_level_and_resamples_are_what_the_preregistration_says():
    assert UCB_LEVEL == 0.95
    assert BOOTSTRAP_RESAMPLES == 2000
    assert UCB_BASELINE == "point_baseline"
    assert set(UCB_CANDIDATES) == {"chi2", "t_squared", "bootstrap"}
    assert UCB_BASELINE not in UCB_CANDIDATES, "the baseline is not selectable"


def test_the_point_estimate_under_covers_a_heavy_tailed_scale():
    """The mechanism Pilot-3 exists to remove, demonstrated synthetically."""
    r = np.random.default_rng(2026)
    df, n = 5.6, 1500
    sc = 1.0 / math.sqrt(df / (df - 2))
    for b in (16, 32, 64):
        true = 1.0 / (math.sqrt(b) * 2.5)
        cov = 0
        for _ in range(n):
            x = 2.5 + sc * r.standard_t(df, b)
            if evaluate(UCB_BASELINE, x, rng=r) >= true:
                cov += 1
        assert cov / n < 0.5, f"point estimate covered {cov/n:.3f} at B={b}"


def test_chi2_recovers_most_of_the_nominal_level_under_a_heavy_tail():
    r = np.random.default_rng(2027)
    df, n = 5.6, 1500
    sc = 1.0 / math.sqrt(df / (df - 2))
    for b in (32, 64):
        true = 1.0 / (math.sqrt(b) * 2.5)
        cov = sum(evaluate("chi2", 2.5 + sc * r.standard_t(df, b), rng=r) >= true
                  for _ in range(n)) / n
        assert cov > 0.80, f"chi2 covered only {cov:.3f} at B={b}"


@pytest.mark.parametrize("method", list(UCB_METHODS))
def test_degenerate_inputs_do_not_crash(method):
    """A single block yields no scale at all; the three BOUNDS additionally
    need three blocks, and every degenerate case returns +inf, which the
    sizing rule turns into a refusal rather than a silent tiny allocation."""
    r = rng()
    assert math.isinf(evaluate(method, np.array([1.0]), rng=r))
    two = evaluate(method, np.array([1.0, 2.0]), rng=r)
    if method == UCB_BASELINE:
        assert math.isfinite(two)          # a point estimate exists at B = 2
    else:
        assert math.isinf(two)             # every bound requires B >= 3
    v = evaluate(method, np.zeros(16), rng=r)
    assert math.isinf(v) or v == 0.0
