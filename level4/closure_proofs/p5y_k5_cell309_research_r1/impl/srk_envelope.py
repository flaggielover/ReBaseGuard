"""SRK rigorous state-resolved kernel-norm envelopes (stdlib only, exact rationals + pinned c1b_gauss).

I_i(J) := int_J |He_i(v)| phi(v) dv for a rational interval J = [a, b], rigorous upper bound.
On a sub-interval where He_i has constant sign, int He_i phi = [-He_{i-1} phi]  (d/dv(He_{i-1} phi) = -He_i phi).
Irrational roots of He_i are bracketed by rational intervals of width <= 2^-40; on a bracket the integral is bounded
by (width) * sup|He_i| * phi(0) with sup|He_i| <= sum |coef| max(|lo|,|hi|)^j.

Box envelope (THEOREM_SRK section 1, monotonicity):  for a state box B = [p0,p1] x [m0,m1] and drift set
E = [e_lo, e_hi],  sup_{x in B, e in E} k_i(x; e) <= I_i([m0 - c + e_lo, c - p0 + e_hi]).
"""
from __future__ import annotations

from fractions import Fraction as F
from functools import lru_cache

import srk_kernel as KX

G = KX.G

HE = {0: [F(1)], 1: [F(0), F(1)], 2: [F(-1), F(0), F(1)], 3: [F(0), F(-3), F(0), F(1)],
      4: [F(3), F(0), F(-6), F(0), F(1)], 5: [F(0), F(15), F(0), F(-10), F(0), F(1)]}


def he(i: int, v: F) -> F:
    return sum((c * v ** j for j, c in enumerate(HE[i])), F(0))


def _isqrt_bracket(x: F, bits: int = 40) -> tuple:
    """(lo, hi) rationals with lo <= sqrt(x) <= hi, hi - lo <= 2^-bits (x >= 0)."""
    s = 1 << bits
    n = x.numerator * s * s // x.denominator
    r = G._isqrt(n)
    return F(r, s), F(r + 2, s)


@lru_cache(maxsize=None)
def root_brackets(i: int) -> tuple:
    """sorted list of (lo, hi) rational brackets of the real roots of He_i (exact roots have lo == hi)."""
    if i == 0:
        return ()
    if i == 1:
        return ((F(0), F(0)),)
    if i == 2:
        return ((F(-1), F(-1)), (F(1), F(1)))
    if i == 3:
        lo, hi = _isqrt_bracket(F(3))
        return ((-hi, -lo), (F(0), F(0)), (lo, hi))
    if i == 4:
        # roots +-sqrt(3 -+ sqrt 6)
        s6lo, s6hi = _isqrt_bracket(F(6), 60)
        a_lo, _ = _isqrt_bracket(3 - s6hi, 40)
        _, a_hi = _isqrt_bracket(3 - s6lo, 40)
        b_lo, _ = _isqrt_bracket(3 + s6lo, 40)
        _, b_hi = _isqrt_bracket(3 + s6hi, 40)
        return ((-b_hi, -b_lo), (-a_hi, -a_lo), (a_lo, a_hi), (b_lo, b_hi))
    raise ValueError(i)


def _sup_abs_he(i: int, a: F, b: F) -> F:
    t = max(abs(a), abs(b))
    return sum((abs(c) * t ** j for j, c in enumerate(HE[i])), F(0))


def _signed_integral_iv(i: int, a: F, b: F) -> tuple:
    """rigorous (lo, hi) of int_a^b He_i phi = He_{i-1}(a)phi(a) - He_{i-1}(b)phi(b)   (i >= 1)."""
    ha, hb = he(i - 1, a), he(i - 1, b)
    pa, pb = G.phi(a), G.phi(b)
    ta = sorted((ha * pa[0], ha * pa[1]))
    tb = sorted((hb * pb[0], hb * pb[1]))
    return ta[0] - tb[1], ta[1] - tb[0]


def abs_integral_upper(i: int, a, b) -> F:
    """rigorous upper bound of int_a^b |He_i(v)| phi(v) dv, a <= b rational."""
    a, b = F(a), F(b)
    if b <= a:
        return F(0)
    if i == 0:
        return G.Phi(b)[1] - G.Phi(a)[0]
    pts = [a]
    brackets = []
    for lo, hi in root_brackets(i):
        if hi < a or lo > b:
            continue
        lo2, hi2 = max(lo, a), min(hi, b)
        brackets.append((lo2, hi2))
    total = F(0)
    cur = a
    for lo, hi in brackets:
        if lo > cur:
            s_lo, s_hi = _signed_integral_iv(i, cur, lo)
            total += max(abs(s_lo), abs(s_hi))
        if hi > lo:
            total += (hi - lo) * _sup_abs_he(i, lo, hi) * G.phi(F(0))[1]
        cur = max(cur, hi)
    if b > cur:
        s_lo, s_hi = _signed_integral_iv(i, cur, b)
        total += max(abs(s_lo), abs(s_hi))
    return total


def kappa_upper(i: int, span: F = F(40)) -> F:
    """rigorous upper bound of kappa_i = E|He_i(Y)| (integral over [-span, span] plus a crude tail bound)."""
    core = abs_integral_upper(i, -span, span)
    # tail: int_{|v|>s} |He_i| phi <= 2 * sum|c_j| int_s^inf v^j phi <= 2 sum|c_j| (s^j + j!!) phi(s) * 2  (loose)
    tail = F(0)
    for j, c in enumerate(HE[i]):
        if c:
            tail += 4 * abs(c) * (span ** j + 1 + j * span ** max(j - 2, 0)) * G.phi(span)[1]
    return core + tail


def box_envelope(g: KX.Geom, i: int, b, e_lo: F, e_hi: F) -> F:
    """upper bound of sup_{x in box b, e in [e_lo, e_hi]} k_i(x; e)  (b = (pc, mc, rp, rm))."""
    pc, mc, rp, rm = b
    p0, m0 = pc - rp, mc - rm
    a = m0 - g.c + F(e_lo)
    bb = g.c - p0 + F(e_hi)
    return abs_integral_upper(i, a, bb)


def point_k_upper(g: KX.Geom, i: int, p, m, e) -> F:
    """upper bound of k_i(x; e) at a point (used by tests)."""
    return abs_integral_upper(i, F(m) - g.c + F(e), g.c - F(p) + F(e))


def point_k_lower(g: KX.Geom, i: int, p, m, e) -> F:
    """rigorous LOWER bound of k_i(x; e) at a point (used by tests): sign-constant pieces only, brackets dropped."""
    a, b = F(m) - g.c + F(e), g.c - F(p) + F(e)
    if i == 0:
        return max(F(0), G.Phi(b)[0] - G.Phi(a)[1])
    cur, tot = a, F(0)
    for lo, hi in root_brackets(i):
        if hi < a or lo > b:
            continue
        lo2, hi2 = max(lo, a), min(hi, b)
        if lo2 > cur:
            s_lo, s_hi = _signed_integral_iv(i, cur, lo2)
            m_ = min(abs(s_lo), abs(s_hi)) if s_lo * s_hi > 0 else F(0)
            tot += m_
        cur = max(cur, hi2)
    if b > cur:
        s_lo, s_hi = _signed_integral_iv(i, cur, b)
        tot += min(abs(s_lo), abs(s_hi)) if s_lo * s_hi > 0 else F(0)
    return tot
