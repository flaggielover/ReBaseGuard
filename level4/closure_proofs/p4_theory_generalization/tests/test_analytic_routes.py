"""Route Q and the closed forms: the parts of the evidence with no sampling
error at all."""

from __future__ import annotations

import math

import pytest

from rebaseguard_p4_general import quadrature as routeq
from rebaseguard_p4_general.families import REGISTRY

SUPPORTED = ("gaussian", "laplace", "logistic", "t3", "t1p5", "skewnormal4")
C = 2.0


@pytest.mark.parametrize("name", SUPPORTED)
@pytest.mark.parametrize("m", (1, 2, 3, 5))
def test_score_identity_holds_to_quadrature_accuracy(name, m):
    family = REGISTRY[name]
    gain, _ = routeq.gain(family, C, m)
    derivative = routeq.map_derivative(family, C, m)
    assert abs(gain + derivative) / abs(gain) < 1e-6


def test_laplace_closed_form_matches_the_quadrature():
    b = 2.0 ** -0.5
    closed = routeq.laplace_closed_form(b, C)
    gain, _ = routeq.gain(REGISTRY["laplace"], C, 1)
    assert closed["gain"] == pytest.approx(gain, rel=1e-10)
    assert closed["gain"] == pytest.approx(1.0 + 2.0 * math.sqrt(2.0), rel=1e-12)
    assert closed["map_derivative"] == pytest.approx(-closed["gain"], rel=1e-15)


def test_uniform_identity_fails_by_the_exact_predicted_amount():
    """F1: with moving support the score side is exactly zero and the true
    slope is not, so the identity is false."""
    a, c = math.sqrt(3.0), 1.0
    family = REGISTRY["uniform"]
    gain, _ = routeq.gain(family, c, 1)
    assert gain == 0.0
    derivative = routeq.map_derivative(family, c, 1, tail=2.5)
    assert derivative == pytest.approx(-a / (a - c), rel=1e-4)
    assert abs(gain + derivative) > 1.0


def test_deterministic_stopping_is_neutral_for_every_family():
    """Corollary G2 in its purest form: with tau = 1 the gain is E[Z psi(Z)],
    which integration by parts makes exactly one for every regular family."""
    from scipy import integrate

    import numpy as np
    for name in SUPPORTED + ("cauchy",):
        family = REGISTRY[name]
        value = integrate.quad(
            lambda z: z * family.psi(np.array([z]))[0]
            * math.exp(family.logpdf(np.array([z]))[0]),
            -np.inf, np.inf, limit=400,
        )[0]
        assert value == pytest.approx(1.0, abs=2e-6), name


def test_the_gaussian_score_sum_is_the_residual_total_and_others_are_not():
    import numpy as np
    grid = np.array([-2.0, -0.5, 0.5, 3.0])
    np.testing.assert_allclose(REGISTRY["gaussian"].psi(grid), grid)
    for name in ("laplace", "logistic", "t3"):
        assert not np.allclose(REGISTRY[name].psi(grid), grid)
