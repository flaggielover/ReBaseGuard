"""Certified whole-cell operator norm bounds k_i, jz_i, j_i and sup|phi^(n)|.

ERROR_ALGEBRA.md section 1 and 2 authorise exactly this device:

    "Use K_j = d_e^j K, k_j >= sup_cell ||K_j||. k0 <= 1, k1 <= 2 phi(0),
     k2 <= 4 phi(1) follow by integrating |phi|, |phi'|, |phi''| over the whole
     real line, which bounds the killed integral. These are bounds, not
     empirical fits."
    "Use certified operator norm bounds j_k over the whole cell; rigorous
     whole-line absolute Gaussian moments are admissible. Do not use sampled
     operator norms."

DERIVATIONS (all whole-line, all e-uniform, none sampled).

The raw-variable kernel has e-FREE state limits, so differentiation under the
integral sign has no boundary term:

    (K_e f)(x) = int_{l(x)}^{u(x)} f(q(x,z)) phi(z+e) dz
    (d_e^i K_e f)(x) = int_{l(x)}^{u(x)} f(q(x,z)) phi^(i)(z+e) dz

hence with q mapping into the state domain on which ||f||_inf is taken,

    ||d_e^i K_e|| <= int_R |phi^(i)(y)| dy =: A_i          (killed integral)

Writing phi^(i) = (-1)^i He_i phi:

    A_0 = 1
    A_1 = int |y| phi        = 2 phi(0)
    A_2 = int |y^2-1| phi    = 4 phi(1)
    A_3 = int |y^3-3y| phi   = 2 phi(0) + 8 phi(sqrt 3)
    A_i <= sqrt(int He_i^2 phi) = sqrt(i!)                 (Cauchy-Schwarz)

The closed forms follow from int_0^a y phi = phi(0)-phi(a),
int_0^a y^3 phi = 2 phi(0) - (a^2+2) phi(a), and the sign changes of He_i at
0, +-1, {0, +-sqrt 3}. A_i is taken as the minimum of the closed form (when
known) and the Cauchy-Schwarz bound; both are rigorous upper bounds.

For the z-weighted operator (K_{z,e} f)(x) = int f(q) z phi(z+e) dz,

    ||d_e^i K_{z,e}|| <= int_R |z| |phi^(i)(z+e)| dz
                       = int_R |y - e| |phi^(i)(y)| dy
                      <= M_i + |e| A_i,        M_i := int_R |y phi^(i)(y)| dy
    M_0 = 2 phi(0)
    M_1 = int y^2 phi = 1
    M_2 = int |y||y^2-1| phi = 8 phi(1) - 2 phi(0)
    M_i <= sqrt(int y^2 phi) sqrt(int He_i^2 phi) = sqrt(i!)   (Cauchy-Schwarz)

Finally J_e = K_{z,e} + e K_e, so by Leibniz

    J_i = d_e^i J_e = K_{z,e}^(i) + e K_e^(i) + i K_e^(i-1)
    j_i <= jz_i + e_max A_i + i A_{i-1}

with e_max the exact supremum of |e| on the declared cell.

Pointwise Gaussian-derivative suprema reuse the FROZEN Cramer constant already
binding in ra_certifier.taylor_remainder:

    sup_x |phi^(n)(x)| <= CRAMER * sqrt(n!) / sqrt(2 pi),   CRAMER = 1086/1000.

Every quantity below is returned as an Arb ball whose UPPER endpoint is the
certified bound; callers must use `.upper()`/`abs_upper()` semantics.
"""
from __future__ import annotations

from math import factorial

from flint import arb

from intervals import exact, tight_upper, workprec

CRAMER = arb(1086) / arb(1000)          # frozen: ra_certifier.CRAMER


def phi(x: arb) -> arb:
    return (-(x * x) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()


def _cauchy_schwarz(i: int) -> arb:
    return arb(factorial(i)).sqrt()


def kernel_norm(i: int) -> arb:
    """A_i >= sup_e ||d_e^i K_e||. Whole-line absolute Gaussian moment."""
    if i < 0:
        raise ValueError("negative derivative order")
    closed = None
    if i == 0:
        closed = arb(1)
    elif i == 1:
        closed = arb(2) * phi(arb(0))
    elif i == 2:
        closed = arb(4) * phi(arb(1))
    elif i == 3:
        closed = arb(2) * phi(arb(0)) + arb(8) * phi(arb(3).sqrt())
    cs = _cauchy_schwarz(i)
    if closed is None:
        return tight_upper(cs)
    return tight_upper(closed if closed.upper() <= cs.upper() else cs)


def z_moment(i: int) -> arb:
    """M_i >= int_R |y phi^(i)(y)| dy."""
    if i < 0:
        raise ValueError("negative derivative order")
    closed = None
    if i == 0:
        closed = arb(2) * phi(arb(0))
    elif i == 1:
        closed = arb(1)
    elif i == 2:
        closed = arb(8) * phi(arb(1)) - arb(2) * phi(arb(0))
    cs = _cauchy_schwarz(i)
    if closed is None:
        return tight_upper(cs)
    return tight_upper(closed if closed.upper() <= cs.upper() else cs)


def z_kernel_norm(i: int, e_max: arb) -> arb:
    """jz_i >= sup_{|e|<=e_max} ||d_e^i K_{z,e}||."""
    return tight_upper(z_moment(i) + e_max * kernel_norm(i))


def raw_kernel_norm(i: int, e_max: arb) -> arb:
    """j_i >= sup_cell ||J_i||, J_e = K_{z,e} + e K_e."""
    out = z_kernel_norm(i, e_max) + e_max * kernel_norm(i)
    if i >= 1:
        out = out + arb(i) * kernel_norm(i - 1)
    return tight_upper(out)


def sup_phi_derivative(n: int) -> arb:
    """sup_x |phi^(n)(x)| by the frozen Cramer constant."""
    return tight_upper(CRAMER * _cauchy_schwarz(n) / (arb(2) * arb.pi()).sqrt())


def sup_source_derivative(n: int) -> arb:
    """sup_x |d_e^n S_0(x;e)| for the closed-form S_0 = phi(u+e) - phi(l+e).

    d_e^n S_0 = phi^(n)(u+e) - phi^(n)(l+e), so 2 sup|phi^(n)| bounds it, e-free.
    """
    return tight_upper(arb(2) * sup_phi_derivative(n))


def table(e_max: arb, *, orders: int = 4) -> dict:
    """All certified norms used by one cell, with provenance."""
    return {
        "e_max": e_max,
        "k": {i: kernel_norm(i) for i in range(orders + 1)},
        "M": {i: z_moment(i) for i in range(orders + 1)},
        "jz": {i: z_kernel_norm(i, e_max) for i in range(orders + 1)},
        "j": {i: raw_kernel_norm(i, e_max) for i in range(orders + 1)},
        "sup_phi": {i: sup_phi_derivative(i) for i in range(orders + 2)},
        "provenance": {
            "k": "whole-line int |phi^(i)|; closed form min Cauchy-Schwarz sqrt(i!)",
            "M": "whole-line int |y phi^(i)|; closed form min Cauchy-Schwarz sqrt(i!)",
            "jz": "M_i + e_max * k_i via |z| = |y - e|",
            "j": "jz_i + e_max k_i + i k_(i-1) from J = K_z + e K",
            "sup_phi": "frozen Cramer constant 1086/1000, e-free",
            "sampled_operator_norms_used": False,
        },
    }


def self_check() -> dict:
    """Sanity relations that must hold for the certified table (not a proof)."""
    with workprec(256):
        emax = exact(0)
        t = table(emax)
        return {
            "k0_le_1": bool(t["k"][0].upper() <= arb(1).upper()),
            "k1_le_2phi0": bool(t["k"][1].upper() <= (arb(2) * phi(arb(0))).upper()),
            "k2_le_4phi1": bool(t["k"][2].upper() <= (arb(4) * phi(arb(1))).upper()),
            "monotone_cauchy_schwarz": all(
                t["k"][i].upper() <= _cauchy_schwarz(i).upper() for i in range(5)),
            "all_positive": all(t["k"][i] > 0 for i in range(5)),
        }
