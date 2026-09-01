"""Family definitions: exact identities and agreement with P4's frozen module."""
import sys
from pathlib import Path

import numpy as np
import pytest

from rebaseguard_p8 import families as F
from rebaseguard_p8.config import FAMILIES, P4, STAGE_D

GRID = np.linspace(-12.0, 12.0, 2401)


@pytest.fixture(scope="module")
def p4_route_a():
    sys.path.insert(0, str(P4 / "src"))
    from rebaseguard_location_family import route_a
    return route_a


@pytest.mark.parametrize("name", FAMILIES)
def test_score_matches_p4(name, p4_route_a):
    """P8's independently written psi must equal P4's frozen location_score."""
    assert np.max(np.abs(F.get(name).psi(GRID)
                         - p4_route_a.location_score(name, GRID))) <= 1e-12


@pytest.mark.parametrize("name", FAMILIES)
def test_logpdf_matches_p4(name, p4_route_a):
    assert np.max(np.abs(F.get(name).logpdf(GRID)
                         - p4_route_a.log_density(name, GRID))) <= 1e-12


@pytest.mark.parametrize("name", FAMILIES)
def test_psi_is_minus_dlogf(name):
    """psi = -d/dz log f, checked by central differences."""
    fam = F.get(name)
    z = np.linspace(-6.0, 6.0, 241)
    assert np.max(np.abs(fam.psi(z) - F.score_by_finite_difference(fam, z))) < 1e-7


@pytest.mark.parametrize("name", FAMILIES)
def test_unit_diagonal_lemma(name):
    """P8-L1(a): E[eps psi(eps)] = 1 exactly for every regular location family."""
    assert abs(F.expected_z_psi(F.get(name)) - 1.0) <= 1e-4


@pytest.mark.parametrize("name", FAMILIES)
def test_score_has_zero_mean(name):
    assert abs(F.expected_psi(F.get(name))) <= 1e-8


@pytest.mark.parametrize("name", FAMILIES)
def test_fisher_information_matches_stage_d(name):
    import json
    d = json.loads((STAGE_D / "results" / "d3_nongaussian.json").read_text())
    ref = {r["family"]: float(r["E_psi_prime"]) for r in d["rows"]}[name]
    assert abs(F.fisher_information(F.get(name)) - ref) <= 1e-6


def test_gaussian_score_is_identity():
    assert np.allclose(F.get("gaussian").psi(GRID), GRID, atol=0, rtol=0)


def test_declared_moment_marginal_family_is_exactly_t3():
    """The MOMENT_MARGINAL declaration must follow from the tail index, not taste.

    The Gamma_A integrand is ``zbar * Psi_tau`` with ``psi`` bounded for the
    t families, so it inherits the innovation tail index ``nu``.  The third
    absolute moment diverges iff ``nu <= 3``.
    """
    from rebaseguard_p8.config import MOMENT_MARGINAL
    derived = tuple(n for n in FAMILIES if F.get(n).tail_moment_order <= 3.0)
    assert derived == MOMENT_MARGINAL
