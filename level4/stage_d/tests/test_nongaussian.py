"""D3 score correctness. A wrong psi would silently invalidate every D3 result."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import integrate

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nongaussian import (                                    # noqa: E402
    FAMILIES, expected_psi_prime, fisher_information,
)

NAMES = list(FAMILIES)


def _int(f, lim=40.0):
    return integrate.quad(f, -lim, lim, limit=400)[0]


@pytest.mark.parametrize("name", NAMES)
def test_psi_has_zero_mean(name):
    """E[psi] = 0 is required for the score to be a score."""
    fam = FAMILIES[name]
    v = _int(lambda x: fam.psi(np.array([x]))[0]
             * np.exp(fam.logpdf(np.array([x]))[0]))
    assert abs(v) < 1e-8, v


@pytest.mark.parametrize("name", NAMES)
def test_fisher_identity(name):
    """E[psi^2] = E[psi'] -- the regularity identity. This is the check that
    actually catches an incorrectly derived score."""
    fam = FAMILIES[name]
    assert fisher_information(fam) == pytest.approx(expected_psi_prime(fam),
                                                    rel=1e-4)


@pytest.mark.parametrize("name", NAMES)
def test_psi_equals_minus_dlogp_dx(name):
    """psi = -p'/p, checked against a finite difference of the log density."""
    fam = FAMILIES[name]
    xs = np.array([-2.3, -0.7, 0.4, 1.9])
    h = 1e-5
    fd = -(fam.logpdf(xs + h) - fam.logpdf(xs - h)) / (2 * h)
    assert np.allclose(fam.psi(xs), fd, rtol=1e-4, atol=1e-6)


@pytest.mark.parametrize("name", NAMES)
def test_declared_variance_matches_draws(name):
    fam = FAMILIES[name]
    x = fam.draw(np.random.default_rng(5), 500_000)
    assert x.var() == pytest.approx(fam.variance, rel=0.05)


def test_t_families_are_unit_variance_and_gaussian_is_identity():
    for n in ("t10", "t5", "t3"):
        assert FAMILIES[n].unit_variance_rescaled
        assert FAMILIES[n].variance == 1.0
    xs = np.array([-1.5, 0.0, 2.0])
    assert np.allclose(FAMILIES["gaussian"].psi(xs), xs)


def test_unscaled_t_score_would_differ():
    """Guards the rescaling: the bare (nu+1)x/(nu+x^2) is NOT the unit-variance
    score, and using it would mis-weight every D3 estimate."""
    nu, x = 5, np.array([1.3])
    bare = (nu + 1) * x / (nu + x * x)
    assert not np.allclose(FAMILIES["t5"].psi(x), bare)


def test_contaminated_variance_exceeds_one():
    """Recorded, not corrected: only the t families are unit-variance rescaled."""
    assert FAMILIES["contam0.05"].variance == pytest.approx(1.4)
    assert FAMILIES["contam0.1"].variance == pytest.approx(1.8)
