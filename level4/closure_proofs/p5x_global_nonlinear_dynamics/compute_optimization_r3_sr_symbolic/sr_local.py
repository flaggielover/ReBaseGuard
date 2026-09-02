"""R3 minimal feasibility path: local SR softplus enclosure + closed-form
centred Gaussian moments on one state patch x one innovation panel.

Implements exactly the machinery the frozen gate needs and nothing more.
Every construction is justified in PROOF.md L-R3.1 .. L-R3.6.
"""
from __future__ import annotations

import sys
from pathlib import Path

from flint import arb, arb_series

_PROOF_SRC = Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"
if str(_PROOF_SRC) not in sys.path:
    sys.path.insert(0, str(_PROOF_SRC))

from rebaseguard_certify.arb_backend import gaussian_cdf, rational, workprec  # noqa: E402

A_NUM, A_DEN = 4581762885148045, 8796093022208
GRID = 64


def sr_constants() -> tuple[arb, arb, arb]:
    """(A, b_SR = log(1+A), c_SR = log A + 1/2) as exact-rational-derived balls."""
    A = arb(A_NUM) / arb(A_DEN)
    return A, (arb(1) + A).log(), A.log() + rational(1, 2)


def softplus(u: arb) -> arb:
    """log(1+exp(u)) with the stable branch split; rigorous on balls."""
    if u.lower() >= 0:
        return u + (arb(1) + (-u).exp()).log()
    return (arb(1) + u.exp()).log()


def softplus_local_enclosure(centre: arb, half_width: arb, degree: int):
    """L-R3.1: (coefficients a_0..a_degree about `centre`, remainder bound E_d).

    The series is expanded at an argument whose constant term is the INTERVAL
    [centre-h, centre+h], so by inclusion isotonicity every returned coefficient
    ball contains sp^{(k)}(xi)/k! for EVERY xi in that interval -- in particular
    the degree-(d+1) ball is a valid Lagrange remainder factor.
    """
    u_iv = centre + arb(0, half_width.upper())
    x = arb_series([u_iv, arb(1)], degree + 2)
    f = (arb_series([arb(1)], degree + 2) + x.exp()).log()
    coeffs = list(f)[: degree + 2]
    # coefficients about the CENTRE (point), for the polynomial part
    xc = arb_series([centre, arb(1)], degree + 2)
    fc = (arb_series([arb(1)], degree + 2) + xc.exp()).log()
    a = list(fc)[: degree + 1]
    a_next = coeffs[degree + 1]                      # contains sp^{(d+1)}(xi)/(d+1)!
    E = a_next.abs_upper() * (half_width ** (degree + 1))
    return a, arb(0, E.upper()), a_next


def centred_gaussian_moments(z_lo: arb, z_hi: arb, z_c: arb, e: arb, kmax: int):
    """L-R3.3: N_k = int_{z_lo}^{z_hi} (z-z_c)^k phi(z+e) dz, exact recursion."""
    mu = z_c + e
    two_pi = arb(2) * arb.pi()

    def phi(t: arb) -> arb:
        return (-(t * t) / arb(2)).exp() / two_pi.sqrt()

    a_lo, a_hi = z_lo + e, z_hi + e
    t_lo, t_hi = z_lo - z_c, z_hi - z_c
    N = [gaussian_cdf(a_hi) - gaussian_cdf(a_lo)]
    if kmax >= 1:
        N.append(phi(a_lo) - phi(a_hi) - mu * N[0])
    for k in range(2, kmax + 1):
        bnd = (t_hi ** (k - 1)) * phi(a_hi) - (t_lo ** (k - 1)) * phi(a_lo)
        N.append(arb(k - 1) * N[k - 2] - mu * N[k - 1] - bnd)
    return N


def patch_geometry(i: int, j: int, grid: int = GRID):
    """L-R3.5/L-R3.6: patch box, live-region limits, core and strips."""
    _, b, c = sr_constants()
    yp_lo, yp_hi = b * arb(i) / arb(grid), b * arb(i + 1) / arb(grid)
    ym_lo, ym_hi = b * arb(j) / arb(grid), b * arb(j + 1) / arb(grid)
    l_min, l_max = ym_lo - c, ym_hi - c
    u_min, u_max = c - yp_hi, c - yp_lo
    return {"yp": (yp_lo, yp_hi), "ym": (ym_lo, ym_hi),
            "l": (l_min, l_max), "u": (u_min, u_max),
            "core": (l_max, u_min), "strip_l": (l_min, l_max), "strip_u": (u_min, u_max)}


def local_kernel_enclosure(geo, z_lo: arb, z_hi: arb, e: arb, degree: int,
                           cand_degree: int = 16):
    """L-R3.1+L-R3.2+L-R3.3 on ONE panel: enclose int_panel ghat(q_SR) phi dz.

    `ghat` is stood in for by the worst-case bound sup|ghat| <= 1 on the unit
    scale together with the exact composed monomial structure: the feasibility
    gate measures the WIDTH the machinery produces, which is candidate-independent
    up to the factor sup|ghat|.  A production certifier substitutes the real
    exact-dyadic candidate here without changing any of the enclosures below.
    """
    z_c = (z_lo + z_hi) / arb(2)
    h = (z_hi - z_lo) / arb(2)
    yp_lo, yp_hi = geo["yp"]
    ym_lo, ym_hi = geo["ym"]
    # u = y + z - 1/2 over the patch x panel
    up_c = (yp_lo + yp_hi) / arb(2) + z_c - rational(1, 2)
    up_h = (yp_hi - yp_lo) / arb(2) + h
    um_c = (ym_lo + ym_hi) / arb(2) - z_c - rational(1, 2)
    um_h = (ym_hi - ym_lo) / arb(2) + h
    ap, Ep, ap_next = softplus_local_enclosure(up_c, up_h, degree)
    am, Em, am_next = softplus_local_enclosure(um_c, um_h, degree)
    # composed integrand degree in (z - z_c): cand_degree * degree
    comp_deg = cand_degree * degree
    N = centred_gaussian_moments(z_lo, z_hi, z_c, e, comp_deg)
    mass = N[0]
    # width contributed by the softplus remainders, propagated through ghat:
    # |d ghat| <= cand_degree * sup|ghat| on the unit scale
    remainder_width = arb(cand_degree) * (Ep.rad() + Em.rad()) * mass.abs_upper()
    return {"z_c": z_c, "h": h, "softplus_plus": (ap, Ep, ap_next),
            "softplus_minus": (am, Em, am_next), "moments": N,
            "panel_mass": mass, "composed_degree": comp_deg,
            "remainder_width": remainder_width,
            "moment_decay_ok": all(N[k].abs_upper() <= (h ** k) * mass.abs_upper() * arb(11) / arb(10)
                                   for k in range(1, min(len(N), 12)))}


# --------------------------------------------------------------------------
# Absolute derivative bound for softplus (PROOF.md L-R3.1 remark)
# --------------------------------------------------------------------------
def sigma_derivative_polynomials(n: int):
    """p_k with sigma^{(k)}(u) = p_k(sigma(u)); exact integer-coefficient polys.

    p_0 = s ;  p_{k+1}(s) = p_k'(s) * s(1-s).
    """
    from fractions import Fraction
    polys = [[Fraction(0), Fraction(1)]]          # p_0 = s
    for _ in range(n):
        p = polys[-1]
        dp = [p[i] * i for i in range(1, len(p))]  # p'
        # multiply by s - s^2
        out = [Fraction(0)] * (len(dp) + 2)
        for i, c in enumerate(dp):
            out[i + 1] += c
            out[i + 2] -= c
        polys.append(out)
    return polys


def softplus_derivative_bound(order: int) -> arb:
    """M with |sp^{(order)}(u)| = |sigma^{(order-1)}(u)| <= M for ALL real u.

    sigma in (0,1), so bounding the exact integer polynomial p_{order-1} on the
    unit interval by the sum of |coefficients| is rigorous and u-independent.
    """
    polys = sigma_derivative_polynomials(order)
    p = polys[order - 1]
    return sum((arb(c.numerator) / arb(c.denominator)).abs_upper() for c in p)


def softplus_taylor(centre: arb, degree: int):
    """Coefficients a_0..a_degree of sp about `centre` (point expansion)."""
    x = arb_series([centre, arb(1)], degree + 1)
    f = (arb_series([arb(1)], degree + 1) + x.exp()).log()
    return list(f)[: degree + 1]


def softplus_enclosure_absolute(centre: arb, half_width: arb, degree: int):
    """L-R3.1 with the ABSOLUTE derivative bound: (coeffs, remainder ball, M)."""
    import math
    a = softplus_taylor(centre, degree)
    M = softplus_derivative_bound(degree + 1)
    E = M * (half_width ** (degree + 1)) / arb(math.factorial(degree + 1))
    return a, arb(0, E.upper()), M


def compose_candidate(cand_coeffs, Pp, Pm, trunc: int):
    """ghat(P^+(t), P^-(t)) as an arb_poly in t, truncated at `trunc`.

    `cand_coeffs[i][j]` are the exact-dyadic candidate coefficients.  Horner in
    two variables using flint arb_poly multiplication; inclusion-isotone
    throughout (PROOF.md L-R3.2).
    """
    from flint import arb_poly
    n = len(cand_coeffs)
    ap = arb_poly(list(Pp))
    am = arb_poly(list(Pm))
    acc = arb_poly([arb(0)])
    for i in range(n - 1, -1, -1):
        inner = arb_poly([arb(0)])
        row = cand_coeffs[i]
        for j in range(len(row) - 1, -1, -1):
            inner = (inner * am)
            inner = arb_poly(list(inner)[:trunc]) + arb_poly([row[j]])
        acc = acc * ap
        acc = arb_poly(list(acc)[:trunc]) + inner
    return acc


def softplus_derivative_bound_tight(order: int) -> arb:
    """Tight, u-independent bound on |sp^{(order)}| = |sigma^{(order-1)}|.

    sigma in (0,1) and p_{order-1} has exact rational coefficients, so convert it
    to the Bernstein basis on [0,1]; the convex-hull property gives
    |p(s)| <= max_k |b_k| for every s in [0,1].  Rigorous and far tighter than a
    coefficient sum (which is lossy by ~1e3 at these orders).
    """
    from fractions import Fraction
    from math import comb
    p = sigma_derivative_polynomials(order)[order - 1]
    N = len(p) - 1
    best = Fraction(0)
    for k in range(N + 1):
        b = sum(p[i] * Fraction(comb(k, i), comb(N, i)) for i in range(k + 1))
        if abs(b) > best:
            best = abs(b)
    return arb(best.numerator) / arb(best.denominator)
