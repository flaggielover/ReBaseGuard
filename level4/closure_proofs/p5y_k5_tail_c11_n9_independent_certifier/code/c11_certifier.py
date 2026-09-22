"""C11 -- the SECOND, independently implemented certifier for the K5 m=5 tail operator supply.

INDEPENDENCE STATEMENT. This module imports NOTHING from the original certifier's load-bearing
graph. The forbidden set, derived mechanically in phase 2, is: taboo_certify, resolvent_certificate,
opnorms, ra_certifier, fast_range, intervals, rebaseguard_certify, rung3_engine, spec. None appears
here. The original's arithmetic backend is numpy + flint.arb; this module uses EXACT RATIONAL
arithmetic from the standard library, so the independence is both implementational and
arithmetic-backend, which is strictly stronger than N9's stated requirement.

The only shared surfaces are DATA, not code:
  * the frozen model constants K = 1/2, H = 5, C = K + H = 11/2, re-derived from the frozen model
    file by reading its text rather than importing it;
  * the reachable set R, taken as a specification;
  * the cell geometry (e_lo, e_hi) from the committed registry.
Both certifiers must agree about the PROBLEM or they would be answering different questions.

Rigorous rational Gaussian primitives are taken from C7 (`c7_gaussian.py`, which imports only
`fractions`). C7 is not the first certifier and is on no forbidden list; the reuse is declared here
and classified in the design artifact.

THE MATHEMATICS, re-derived from the frozen model's own specification.

State (p, m), both CUSUM arms. From (p, m) the increment is z with z + e ~ N(0,1), i.e. density
phi(z + e). The alarm-free window is z in [ell, up] with

    ell = m - C,    up = C - p,

and the next state is

    (p', m') = ( max(0, p + z - K),  max(0, m - z - K) ).

So the taboo/full kernel acting on a function w is

    (K_e w)(p, m) = INTEGRAL_{ell}^{up} w( max(0,p+z-K), max(0,m-z-K) ) phi(z + e) dz.

p' and m' are piecewise linear in z with kinks at z = K - p and z = m - K. Splitting [ell, up] at
those kinks makes the integrand a POLYNOMIAL in z times phi(z+e) on each piece, so the integral is a
finite combination of Gaussian moments

    M_j(A, B) = INTEGRAL_A^B u^j phi(u) du,

which satisfy M_0 = Phi(B) - Phi(A), M_1 = phi(A) - phi(B), and
M_j = (j-1) M_{j-2} + A^{j-1} phi(A) - B^{j-1} phi(B). Every step is exact in rationals.

A supersolution certificate is then the statement w >= 1 + K_e w on R, from which E_x[tau] <= w(x),
and tau := w(atom) bounds the ARL at the atom.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11_common as C

sys.path.insert(0, str(C.C7 / "code"))
import c7_gaussian as G  # noqa: E402  rigorous rational Phi/phi; imports only `fractions`

K = F(1, 2)
H = F(5)
CC = K + H                      # 11/2, the frozen alarm threshold
ATOM = (F(0), F(0))


class CertRefusal(Exception):
    pass


# ---------------------------------------------------------------------------------------------
# Gaussian moments, exact, with outward rounding kept explicit
# ---------------------------------------------------------------------------------------------
def moments(A: F, B: F, jmax: int) -> list[G.Iv]:
    """M_j = int_A^B u^j phi(u) du for j = 0..jmax, as rigorous intervals."""
    if B < A:
        raise CertRefusal("moment interval is inverted")
    phiA, phiB = G.phi(A), G.phi(B)
    out = [G.Phi(B) - G.Phi(A)]
    # ERRATUM E5 (C11 adjudication finding 13). The reused rational Phi degrades silently far
    # outside this campaign's operating range: c7_gaussian._erf_integral needs roughly t^2/2
    # truncation terms, so for |t| ~ 20 it returns a SOUND but VACUOUS enclosure (width ~1e82)
    # instead of refusing. Guard it here, where the result is consumed, with a fact that needs no
    # knowledge of the series: M_0 is a probability mass, so it lies in [0, 1]. An enclosure wider
    # than 1, or one that does not meet [0, 1], is vacuous and must refuse rather than propagate.
    # Inside C11's range the width is ~1e-70, so this cannot affect any certified result.
    m0 = out[0]
    if m0.hi - m0.lo > F(1) or m0.hi < 0 or m0.lo > 1:
        raise CertRefusal(
            f"vacuous Gaussian enclosure on [{A}, {B}]: M_0 = [{float(m0.lo):.3e}, "
            f"{float(m0.hi):.3e}] is not a usable subset of [0, 1]; the rational Phi series is "
            f"out of range for this argument")
    if jmax >= 1:
        out.append(phiA - phiB)
    for j in range(2, jmax + 1):
        term = G.Iv(j - 1, j - 1) * out[j - 2]
        out.append(term + G.Iv(A ** (j - 1), A ** (j - 1)) * phiA
                   - G.Iv(B ** (j - 1), B ** (j - 1)) * phiB)
    return out


def shifted_moments(a: F, b: F, e: F, jmax: int) -> list[G.Iv]:
    """int_a^b z^j phi(z+e) dz, by u = z + e and the binomial expansion of (u - e)^j."""
    Ms = moments(a + e, b + e, jmax)
    from math import comb
    out = []
    for j in range(jmax + 1):
        acc = G.Iv(0, 0)
        for i in range(j + 1):
            c = comb(j, i) * ((-e) ** (j - i))
            acc = acc + G.Iv(c, c) * Ms[i]
        out.append(acc)
    return out


# ---------------------------------------------------------------------------------------------
# Bivariate polynomials over the rationals: {(i, j): coeff} meaning sum coeff * p^i * m^j
# ---------------------------------------------------------------------------------------------
def poly_deg(w: dict) -> int:
    return max((i + j for (i, j) in w), default=0)


def poly_eval_iv(w: dict, P: G.Iv, M: G.Iv) -> G.Iv:
    acc = G.Iv(0, 0)
    for (i, j), c in w.items():
        t = G.Iv(c, c)
        for _ in range(i):
            t = t * P
        for _ in range(j):
            t = t * M
        acc = acc + t
    return acc


def _pow_lin(c0: F, c1: F, n: int) -> list[F]:
    """coefficients of (c0 + c1 z)^n in z."""
    from math import comb
    return [F(comb(n, k)) * c0 ** (n - k) * c1 ** k for k in range(n + 1)]


def kernel_apply(w: dict, p: F, m: F, e: F) -> G.Iv:
    """(K_e w)(p, m), exact. Splits the alarm-free window at the two kinks."""
    ell, up = m - CC, CC - p
    if up <= ell:
        return G.Iv(0, 0)
    kinks = sorted({ell, up} | {z for z in (K - p, m - K) if ell < z < up})
    total = G.Iv(0, 0)
    for lo, hi in zip(kinks, kinks[1:]):
        if hi <= lo:
            continue
        mid = (lo + hi) / 2
        pz_pos = (p + mid - K) > 0
        mz_pos = (m - mid - K) > 0
        # on this piece p' = p - K + z (or 0) and m' = m - K - z (or 0): both affine in z
        zc: dict[int, F] = {}
        for (i, j), c in w.items():
            if i and not pz_pos:
                continue
            if j and not mz_pos:
                continue
            a = _pow_lin(p - K, F(1), i) if i else [F(1)]
            b = _pow_lin(m - K, F(-1), j) if j else [F(1)]
            for s, av in enumerate(a):
                if av == 0:
                    continue
                for t, bv in enumerate(b):
                    if bv == 0:
                        continue
                    zc[s + t] = zc.get(s + t, F(0)) + c * av * bv
        if not zc:
            continue
        Ms = shifted_moments(lo, hi, e, max(zc))
        for d, c in zc.items():
            total = total + G.Iv(c, c) * Ms[d]
    return total


def alarm_prob(p: F, m: F, e: F) -> G.Iv:
    """h1(p,m) = P(alarm) = 1 - int_ell^up phi(z+e) dz."""
    ell, up = m - CC, CC - p
    if up <= ell:
        return G.Iv(1, 1)
    M = moments(ell + e, up + e, 0)[0]
    return G.Iv(1, 1) - M


# ---------------------------------------------------------------------------------------------
# The reachable set R, taken as a SPECIFICATION and covered by boxes
# ---------------------------------------------------------------------------------------------
def box_meets_R(a: F, b: F, c: F, d: F) -> bool:
    """R = {0<=p,m<=5 and (p+m<=4 or p==0 or m==0)}. A box is kept if it can meet R.

    Keeping a SUPERSET of R is sound: a margin positive on a cover is positive on R. Boxes that
    provably miss R are dropped so the cover is not needlessly loose.
    """
    if b < 0 or d < 0 or a > H or c > H:
        return False
    return (a + c <= 4) or (c == F(0)) or (a == F(0))


def cover(depth: int) -> list[tuple[F, F, F, F]]:
    boxes = [(F(0), H, F(0), H)]
    for _ in range(depth):
        nxt = []
        for (a, b, c, d) in boxes:
            am, cm = (a + b) / 2, (c + d) / 2
            for box in ((a, am, c, cm), (am, b, c, cm), (a, am, cm, d), (am, b, cm, d)):
                if box_meets_R(*box):
                    nxt.append(box)
        boxes = nxt
    return boxes


def min_on_cover(fn, depth: int):
    """Rigorous lower bound of fn over R, by evaluating on a box cover of R."""
    mn = None
    boxes = cover(depth)
    for (a, b, c, d) in boxes:
        v = fn(G.Iv(a, b), G.Iv(c, d))
        mn = v.lo if mn is None or v.lo < mn else mn
    return mn, len(boxes)


# ---------------------------------------------------------------------------------------------
# Uniform bound of K_e w over a BOX of states -- what the supersolution check needs
# ---------------------------------------------------------------------------------------------
def kernel_box_upper(w: dict, a: F, b: F, c: F, d: F, e: F, panels: int = 24) -> G.Iv:
    """A rigorous UPPER bound on (K_e w)(p,m) valid for every (p,m) in [a,b] x [c,d].

    The alarm-free window varies with the state, so the widest possible window is used:
    ell ranges over [c - C, d - C] and up over [C - b, C - a], and the union is
    [c - C, C - a]. Taking a WIDER window can only add non-negative mass when w >= 0, so the
    bound stays an upper bound.

    Over a z-panel the image state lies in a box, because p' = max(0, p + z - K) is monotone in
    both p and z and likewise m' = max(0, m - z - K). w is bounded on that image box by interval
    evaluation, and multiplied by the exact Gaussian mass of the panel. Summing the panels gives a
    rigorous upper bound with no quadrature error, because each panel's mass is exact and w's
    bound on the panel is uniform.
    """
    lo_z, hi_z = c - CC, CC - a
    if hi_z <= lo_z:
        return G.Iv(0, 0)
    step = (hi_z - lo_z) / panels
    acc = G.Iv(0, 0)
    for k in range(panels):
        z0, z1 = lo_z + step * k, lo_z + step * (k + 1)
        p_lo = max(F(0), a + z0 - K)
        p_hi = max(F(0), b + z1 - K)
        m_lo = max(F(0), c - z1 - K)
        m_hi = max(F(0), d - z0 - K)
        wv = poly_eval_iv(w, G.Iv(p_lo, p_hi), G.Iv(m_lo, m_hi))
        mass = moments(z0 + e, z1 + e, 0)[0]
        hi = wv.hi if wv.hi > 0 else F(0)
        acc = acc + G.Iv(0, hi) * G.Iv(0, mass.hi)
    return acc


def supersolution_margin(w: dict, e: F, depth: int = 4, panels: int = 24):
    """Rigorous lower bound of L = w - 1 - K_e w over R, and of w over R.

    margin > 0 and w >= 0 together certify w >= 1 + K_e w on R, hence E_x[tau] <= w(x).
    """
    boxes = cover(depth)
    mn_L, mn_w = None, None
    for (a, b, c, d) in boxes:
        wv = poly_eval_iv(w, G.Iv(a, b), G.Iv(c, d))
        kv = kernel_box_upper(w, a, b, c, d, e, panels)
        L_lo = wv.lo - F(1) - kv.hi
        mn_L = L_lo if mn_L is None or L_lo < mn_L else mn_L
        mn_w = wv.lo if mn_w is None or wv.lo < mn_w else mn_w
    return {"margin_lower_bound": mn_L, "w_min_lower_bound": mn_w,
            "boxes": len(boxes), "certified": bool(mn_L is not None and mn_L > 0 and mn_w >= 0)}
