"""The score of every family must be the analytic score of its own density."""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import integrate

from rebaseguard_p4_general.families import REGISTRY

GRID = np.array([-6.1, -4.3, -2.1, -0.7, -0.11, 0.11, 0.7, 2.1, 4.3, 6.1, 9.0])
SMOOTH = [name for name, f in REGISTRY.items() if f.common_support]


@pytest.mark.parametrize("name", SMOOTH)
def test_score_matches_numeric_derivative_of_log_density(name):
    family = REGISTRY[name]
    step = 1e-5
    numeric = -(family.logpdf(GRID + step) - family.logpdf(GRID - step)) / (2 * step)
    np.testing.assert_allclose(numeric, family.psi(GRID), rtol=2e-4, atol=2e-5)


@pytest.mark.parametrize("name", SMOOTH)
def test_density_integrates_to_one(name):
    family = REGISTRY[name]
    mass = integrate.quad(
        lambda x: math.exp(family.logpdf(np.array([x]))[0]),
        -np.inf, np.inf, limit=400,
    )[0]
    assert abs(mass - 1.0) < 1e-8


@pytest.mark.parametrize(
    "name", [n for n, f in REGISTRY.items()
             if f.common_support and f.finite_abs_moment_order > 1]
)
def test_declared_score_bound_holds(name):
    family = REGISTRY[name]
    if family.score_bound is None:
        pytest.skip("family declares an unbounded score")
    wide = np.linspace(-200.0, 200.0, 40001)
    assert np.max(np.abs(family.psi(wide))) <= family.score_bound * (1 + 1e-9)


def test_gaussian_score_is_the_identity():
    np.testing.assert_allclose(REGISTRY["gaussian"].psi(GRID), GRID)


def test_uniform_interior_score_is_identically_zero():
    inside = np.array([-1.5, -0.5, 0.0, 0.5, 1.5])
    np.testing.assert_array_equal(REGISTRY["uniform"].psi(inside), np.zeros(5))


def test_laplace_log_density_is_not_everywhere_differentiable():
    """The hypothesis that Priority 1 and Priority 2 assume, and that
    Priority 4 replaces, is genuinely violated here."""
    assert REGISTRY["laplace"].everywhere_differentiable_logdensity is False
    assert REGISTRY["gaussian"].everywhere_differentiable_logdensity is True


def test_sample_moments_match_the_declared_normalisation():
    rng = np.random.default_rng(20260831)
    for name in ("gaussian", "laplace", "logistic", "t3", "skewnormal4"):
        draws = REGISTRY[name].sample(rng, (400000,))
        assert abs(float(draws.mean())) < 0.02
        assert abs(float(draws.var()) - 1.0) < 0.06


def test_skewnormal_is_asymmetric_and_declared_so():
    family = REGISTRY["skewnormal4"]
    assert family.symmetric is False
    left = family.logpdf(np.array([-1.0]))[0]
    right = family.logpdf(np.array([1.0]))[0]
    assert abs(left - right) > 0.1


def test_families_declare_the_moment_boundary():
    assert REGISTRY["cauchy"].finite_abs_moment_order == 1.0
    assert REGISTRY["t1p5"].finite_abs_moment_order == 1.5
    assert REGISTRY["t3"].finite_abs_moment_order == 3.0
