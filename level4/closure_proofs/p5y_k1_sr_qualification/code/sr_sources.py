"""Closed-form SR source terms rho_{1,e}, rho_{2,e} and their e-derivatives.

Exact, per EXACT_SR_TARGET.md section 3 and SR_DERIVATION.md section 4. These are
the only SR objects with a closed form; everything else goes through the panel
operators. Because they are closed form they are also the sharpest available
independent test of the derivative chain: `tests/test_derivative_identities.py`
checks each stated derivative against a rigorous interval difference quotient.

All arithmetic is Arb at the frozen production precision; every returned value is
an enclosure, never a float.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
_PROOF = ROOT / "rebaseguard-proof/src"
if str(_PROOF) not in sys.path:
    sys.path.insert(0, str(_PROOF))

from flint import arb                                              # noqa: E402
from rebaseguard_certify.arb_backend import gaussian_cdf, rational  # noqa: E402


def phi(w: arb) -> arb:
    """Standard normal density, as an Arb enclosure."""
    return (-(w * w) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()


def Phi(w: arb) -> arb:
    return gaussian_cdf(w)


# ----------------------------------------------------------------- rho_1
def rho1(l: arb, u: arb, e: arb) -> arb:
    """rho_{1,e}(y) = phi(u+e) - phi(l+e) - e ( 1 - Phi(u+e) + Phi(l+e) )."""
    U, L = u + e, l + e
    return phi(U) - phi(L) - e * (arb(1) - Phi(U) + Phi(L))


def rho1_d1(l: arb, u: arb, e: arb) -> arb:
    """d/de rho_1.  phi'(w) = -w phi(w), Phi'(w) = phi(w); l and u are e-free.

        rho_1' = -U phi(U) + L phi(L) - (1 - Phi(U) + Phi(L)) - e ( -phi(U) + phi(L) )
    """
    U, L = u + e, l + e
    return (-U * phi(U) + L * phi(L)
            - (arb(1) - Phi(U) + Phi(L))
            - e * (-phi(U) + phi(L)))


def rho1_d2(l: arb, u: arb, e: arb) -> arb:
    """d^2/de^2 rho_1.

    Differentiating rho_1' term by term with phi'' (w) = (w^2 - 1) phi(w):
        d/de[-U phi(U) + L phi(L)] = (U^2 - 1) phi(U) - (L^2 - 1) phi(L)
        d/de[-(1 - Phi(U) + Phi(L))] = phi(U) - phi(L)
        d/de[-e(-phi(U) + phi(L))]  = -(-phi(U) + phi(L)) - e ( U phi(U) - L phi(L) )
    """
    U, L = u + e, l + e
    return ((U * U - arb(1)) * phi(U) - (L * L - arb(1)) * phi(L)
            + arb(2) * (phi(U) - phi(L))
            - e * (U * phi(U) - L * phi(L)))


# ----------------------------------------------------------------- rho_2
def rho2(l: arb, u: arb, e: arb) -> arb:
    """rho_{2,e}(y), frozen form (EXACT_SR_TARGET.md section 3)."""
    U, L = u + e, l + e
    upper = (U * phi(U) + arb(1) - Phi(U)) - arb(2) * e * phi(U) + e * e * (arb(1) - Phi(U))
    lower = (-L * phi(L) + Phi(L)) + arb(2) * e * phi(L) + e * e * Phi(L)
    return upper + lower


def rho2_d1(l: arb, u: arb, e: arb) -> arb:
    """d/de rho_2, term by term (each term differentiated in closed form)."""
    U, L = u + e, l + e
    pU, pL = phi(U), phi(L)
    dpU, dpL = -U * pU, -L * pL                       # d/de phi(U), phi(L)
    # upper branch
    d_upper = ((pU + U * dpU) - pU) - arb(2) * (pU + e * dpU) \
        + arb(2) * e * (arb(1) - Phi(U)) + e * e * (-pU)
    # lower branch
    d_lower = ((-pL - L * dpL) + pL) + arb(2) * (pL + e * dpL) \
        + arb(2) * e * Phi(L) + e * e * pL
    return d_upper + d_lower


# ------------------------------------------------- S_0 = rho_1 (frozen naming)
def S0(l: arb, u: arb, e: arb, order: int) -> arb:
    """S_0^{(order)} = rho_{1,e}^{(order)}, order in {0,1,2}."""
    return {0: rho1, 1: rho1_d1, 2: rho1_d2}[order](l, u, e)
