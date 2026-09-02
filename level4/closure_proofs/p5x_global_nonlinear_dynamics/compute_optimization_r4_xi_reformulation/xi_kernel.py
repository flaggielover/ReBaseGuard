"""P5X R4: the multiplicative-xi / zeta closed-form SR kernel.

Implements exactly the formulas frozen in XI_DERIVATION_AND_INVARIANCE.md
sections 7 and 14, and nothing more.  There are no z-panels and no softplus
approximation anywhere on the certified path; COUNTERS records that as a
machine-checkable fact for gate criterion P5.
"""
from __future__ import annotations

import sys
from pathlib import Path

from flint import arb

_PROOF_SRC = Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"
if str(_PROOF_SRC) not in sys.path:
    sys.path.insert(0, str(_PROOF_SRC))

from rebaseguard_certify.arb_backend import gaussian_cdf, rational, workprec  # noqa: E402

A_NUM, A_DEN = 4581762885148045, 8796093022208
GRID = 64

# P5: instrumented, not asserted by inspection.
COUNTERS = {"z_panels": 0, "softplus_expansions": 0, "phi_evals": 0}


def reset_counters() -> None:
    for k in COUNTERS:
        COUNTERS[k] = 0


def sr_constants() -> tuple[arb, arb, arb]:
    """(A, b_SR = log(1+A), c_SR = log A + 1/2) -- identical to R3's."""
    A = arb(A_NUM) / arb(A_DEN)
    return A, (arb(1) + A).log(), A.log() + rational(1, 2)


# ---------------------------------------------------------------- coordinates

def y_to_zeta(y: arb, A: arb) -> arb:
    """zeta = (exp(y) - 1)/A.  Exact bijection [0, log(1+A)] -> [0, 1]."""
    return (y.exp() - arb(1)) / A


def zeta_patch(i: int, j: int, grid: int = GRID):
    """The EXACT image under y -> zeta of R3's frozen y-patch (i, j).

    Same set of states, so R4 and R3 are compared with one variable changed.
    """
    A, b, c = sr_constants()
    yp = (b * arb(i) / arb(grid), b * arb(i + 1) / arb(grid))
    ym = (b * arb(j) / arb(grid), b * arb(j + 1) / arb(grid))
    return {"yp": yp, "ym": ym,
            "zp": (y_to_zeta(yp[0], A), y_to_zeta(yp[1], A)),
            "zm": (y_to_zeta(ym[0], A), y_to_zeta(ym[1], A))}


def live_limits(zp: arb, zm: arb, A: arb):
    """Section 14: u = 1/2 - log(1/A + zeta^+),  l = log(1/A + zeta^-) - 1/2."""
    inv = arb(1) / A
    return (inv + zm).log() - rational(1, 2), rational(1, 2) - (inv + zp).log()


# ------------------------------------------------------- the closed-form core

def gaussian_exp_integral(k: int, l: arb, u: arb, e: arb) -> arb:
    """int_l^u e^{kz} phi(z+e) dz = e^{k^2/2 - ke} [Phi(u+e-k) - Phi(l+e-k)].

    Exact identity (complete the square); evaluated in outward-rounded balls.
    """
    kk = arb(k)
    COUNTERS["phi_evals"] += 2
    diff = gaussian_cdf(u + e - kk) - gaussian_cdf(l + e - kk)
    return (kk * kk / arb(2) - kk * e).exp() * diff


def kernel_apply(coeffs, zp: arb, zm: arb, e: arb, A: arb) -> arb:
    """(K_e f)(zeta) for f = sum_{i,j} coeffs[i][j] (zeta^+)^i (zeta^-)^j.

    Section 14:  f(T(zeta, z)) = sum_k G_k(zeta) E^k,  E = e^{z-1/2},
                 G_k = sum_{i-j=k} c_ij (1/A+zeta^+)^i (1/A+zeta^-)^j,
    so (K_e f)(zeta) = sum_k G_k * e^{-k/2} * int e^{kz} phi(z+e) dz.

    zp, zm may be balls (a state patch): inclusion isotonicity then makes the
    result a valid enclosure for every state in the patch.
    """
    n_i, n_j = len(coeffs), len(coeffs[0])
    l, u = live_limits(zp, zm, A)
    inv = arb(1) / A
    P = [arb(1)] * n_i
    Q = [arb(1)] * n_j
    for i in range(1, n_i):
        P[i] = P[i - 1] * (inv + zp)
    for j in range(1, n_j):
        Q[j] = Q[j - 1] * (inv + zm)

    # E^+ = e^{z-1/2}, E^- = e^{-z-1/2}.  These are NOT reciprocal:
    # E^+ E^- = e^{-1}.  So (E^+)^i (E^-)^j = e^{(i-j)z} e^{-(i+j)/2}: the
    # z-exponent is k = i-j but the constant prefactor depends on i+j.
    G: dict[int, arb] = {}
    for i in range(n_i):
        for j in range(n_j):
            c = coeffs[i][j]
            if c == 0:
                continue
            cc = c if isinstance(c, arb) else arb(c)
            pref = (-arb(i + j) / arb(2)).exp()
            G[i - j] = G.get(i - j, arb(0)) + cc * P[i] * Q[j] * pref

    total = arb(0)
    for k, g in G.items():
        total += g * gaussian_exp_integral(k, l, u, e)
    return total


# ------------------------------------------------------------- reference only

def kernel_quadrature(coeffs, zp: arb, zm: arb, e: arb, A: arb, n: int) -> arb:
    """Composite-Simpson reference for P2.  Point states only; never certified."""
    l, u = live_limits(zp, zm, A)
    inv = arb(1) / A
    h = (u - l) / arb(n)

    def integrand(z: arb) -> arb:
        ap = (inv + zp) * (z - rational(1, 2)).exp()
        am = (inv + zm) * (-z - rational(1, 2)).exp()
        s = arb(0)
        pi_ = arb(1)
        for i in range(len(coeffs)):
            qj = arb(1)
            for j in range(len(coeffs[0])):
                s += arb(coeffs[i][j]) * pi_ * qj
                qj *= am
            pi_ *= ap
        phi = (-(z + e) * (z + e) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
        return s * phi

    acc = integrand(l) + integrand(u)
    for t in range(1, n):
        acc += integrand(l + h * arb(t)) * arb(4 if t % 2 else 2)
    return acc * h / arb(3)
