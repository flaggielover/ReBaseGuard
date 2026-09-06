"""The (f, F, Mlow) contract and the four alarm-set integrals, against quadrature.

These are the only family-specific analytic inputs either candidate estimator
uses.  If they are right, the estimators evaluate exactly the frozen estimand;
if they are wrong, everything downstream is wrong.  Nothing here is a
measurement.
"""
import math

import numpy as np
import pytest
from scipy.integrate import quad

from rebaseguard_p4_general.families import REGISTRY
from rebaseguard_p4z.analytic import (
    FAMILY_KITS, alarm_integrals, whole_line_integrals,
)

WITH_MOMENT = [n for n, k in FAMILY_KITS.items() if k.partial_mean is not None]
PROBES = np.array([-4.0, -1.5, -0.3, 0.0, 0.7, 2.2, 6.0])
ALARM_SETS = [(-3.0, 2.5), (-5.5, 5.5), (-1.2, 0.9), (-7.0, 3.3), (-0.6, 0.4)]


@pytest.mark.parametrize("name", sorted(FAMILY_KITS))
def test_pdf_matches_the_frozen_logpdf(name):
    kit, fam = FAMILY_KITS[name], REGISTRY[name]
    assert np.allclose(kit.pdf(PROBES), np.exp(fam.logpdf(PROBES)), rtol=1e-12)


@pytest.mark.parametrize("name", sorted(FAMILY_KITS))
def test_cdf_is_the_integral_of_the_pdf(name):
    kit = FAMILY_KITS[name]
    ref = np.array([quad(kit.pdf, -np.inf, z, limit=500)[0] for z in PROBES])
    assert np.allclose(kit.cdf(PROBES), ref, atol=1e-9)


@pytest.mark.parametrize("name", sorted(WITH_MOMENT))
def test_partial_mean_is_the_integral_of_z_times_the_pdf(name):
    kit = FAMILY_KITS[name]
    ref = np.array([quad(lambda t: t * kit.pdf(t), -np.inf, z, limit=500)[0]
                    for z in PROBES])
    assert np.allclose(np.ravel(kit.partial_mean(PROBES)), ref, atol=1e-9)


@pytest.mark.parametrize("name", sorted(WITH_MOMENT))
def test_families_are_centred_as_hypothesis_A7_requires(name):
    """``int z f = 0``; the J1 identity ``int_U^inf z f = -Mlow(U)`` needs it.

    The probe point has to be far out for ``t1p5``: its partial mean decays
    only like ``x^{-1/2}``, which is the finite-mean/infinite-variance boundary
    the theorem sits on, not a defect.
    """
    kit = FAMILY_KITS[name]
    total = float(np.ravel(kit.partial_mean(np.array([1e12])))[0])
    assert abs(total) < 1e-5


@pytest.mark.parametrize("name", sorted(WITH_MOMENT))
def test_four_alarm_integrals_match_quadrature(name):
    kit, psi = FAMILY_KITS[name], REGISTRY[name].psi
    for lower, upper in ALARM_SETS:
        num = lambda g: (quad(g, -np.inf, lower, limit=500)[0]
                         + quad(g, upper, np.inf, limit=500)[0])
        want = (num(kit.pdf),
                num(lambda t: t * kit.pdf(t)),
                num(lambda t: t * float(psi(np.array([t]))[0]) * kit.pdf(t)),
                num(lambda t: float(psi(np.array([t]))[0]) * kit.pdf(t)))
        got = alarm_integrals(kit, np.array([lower]), np.array([upper]))
        for g, w in zip(got, want):
            assert abs(float(np.ravel(g)[0]) - w) < 1e-7, (name, lower, upper)


def test_family_free_identities_hold_by_construction():
    """J0, J2, J3 use only f and F; only J1 is family specific."""
    for name in WITH_MOMENT:
        kit = FAMILY_KITS[name]
        for lower, upper in ALARM_SETS:
            lo, up = np.array([lower]), np.array([upper])
            j0, _, j2, j3 = alarm_integrals(kit, lo, up)
            assert np.allclose(j0, kit.cdf(lo) + 1.0 - kit.cdf(up))
            assert np.allclose(j3, kit.pdf(up) - kit.pdf(lo))
            assert np.allclose(
                j2, kit.cdf(lo) - lo * kit.pdf(lo) + up * kit.pdf(up)
                + 1.0 - kit.cdf(up))


def test_whole_line_alarm_set_reproduces_corollary_G2_constants():
    """With no survival region, J0 -> 1, J1 -> 0, J2 -> 1, J3 -> 0.

    These are exactly ``E[psi] = 0`` and ``E[eps psi] = 1``, the two
    integration-by-parts identities Corollary G2(b) rests on.
    """
    for name in WITH_MOMENT:
        kit = FAMILY_KITS[name]
        assert whole_line_integrals(kit) == (1.0, 0.0, 1.0, 0.0), name

    # and the limit of the general formula agrees, family by family
    far = np.array([1e12])
    for name in WITH_MOMENT:
        kit = FAMILY_KITS[name]
        j0, j1, j2, j3 = (float(np.ravel(v)[0])
                          for v in alarm_integrals(kit, -far, far))
        assert abs(j0) < 1e-7, name          # survival is certain
        assert abs(j1) < 1e-5, name
        assert abs(j2) < 1e-5, name
        assert abs(j3) < 1e-7, name


def test_overlapping_tails_are_refused_not_double_counted():
    kit = FAMILY_KITS["gaussian"]
    with pytest.raises(ValueError, match="empty survival interval"):
        alarm_integrals(kit, np.array([2.0]), np.array([-2.0]))


def test_no_first_moment_is_refused_rather_than_approximated():
    """Cauchy: THEOREM.md Sec. 9 F2 is non-existence, not imprecision."""
    kit = FAMILY_KITS["cauchy"]
    assert kit.partial_mean is None
    with pytest.raises(ValueError, match="no first moment"):
        alarm_integrals(kit, np.array([-2.0]), np.array([2.0]))


def test_moving_support_family_has_no_p4z_route():
    """uniform is deliberately absent: (A3) fails and the identity is false."""
    assert "uniform" not in FAMILY_KITS
