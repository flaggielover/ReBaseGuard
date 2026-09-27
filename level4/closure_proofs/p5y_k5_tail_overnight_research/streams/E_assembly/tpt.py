"""Theorem TPT (Taylor-profile transport) — exact-rational implementation (stdlib only).

Two independent evaluations of the transport penalty:

* ``penalty_closed``  closed-form polynomial integration of t * (-L(t)) (Corollary TPT-M), with the
                      K1 cap handled by a split at a rational point s' (valid for ANY s');
* ``penalty_riemann`` monotone Riemann UPPER sums on a uniform rational partition (V4 cross-check);
                      it must be >= penalty_closed and converge to it.

Also the historical comparators ``penalty_c5t`` (theorem C5-T) and ``penalty_frozen`` (K5-B
direct clause rho*x_hi*M), both from the whole-cell enclosure = the profile at s = rho.

Every public entry point takes a ``CellProfile`` and runs ``_check``, which calls
``ov_quarantine.guard_cell`` on the (detector, m, cell) label AND ``ov_quarantine.guard_drift`` on the
cell's geometry [x_lo, x_hi], and requires len(terms) == m -- so a target cell cannot be evaluated through
this module even under a false label (review V3 findings T1, T2).

Revision r1 (after the V3 non-target validation report, before any target use):
  T1 guard on every public function; T2 label/terms/geometry binding; T3 the K1-cap split point is taken on
  the NON-binding side of the crossing, so the closed form is exact on [0, s'] and dominated by C5-T;
  T4 the closed-form vs Riemann-upper assertion (not a theorem once a split is used) is replaced by a
  Riemann LOWER-sum bracket, and interval orders are validated.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()

Poly = list  # coefficients in s, low -> high


def padd(a: Poly, b: Poly, sb: F = F(1)) -> Poly:
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else F(0)) + sb * (b[i] if i < len(b) else F(0)) for i in range(n)]


def pscale(a: Poly, c: F) -> Poly:
    return [c * x for x in a]


def pmul(a: Poly, b: Poly) -> Poly:
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def peval(a: Poly, s: F) -> F:
    acc = F(0)
    for c in reversed(a):
        acc = acc * s + c
    return acc


def pint(a: Poly, lo: F, hi: F) -> F:
    """exact integral of polynomial a(s) over [lo, hi]."""
    tot = F(0)
    for k, c in enumerate(a):
        tot += c * (hi ** (k + 1) - lo ** (k + 1)) / (k + 1)
    return tot


@dataclass
class SourceTerm:
    """One r of theorem TC: centre interval of H_r(a), |G_r(a)|, midpoint residuals, sups."""
    H_at_a: tuple            # (lo, hi) enclosure of the candidate value Ĥ_r(a)
    abs_G_at_a: F            # |Ĝ_r(a)| (0 under TC-T premise (P2'))
    fF: F
    fD: F
    fH: F
    fG: F
    Env4: F


@dataclass
class CellProfile:
    detector: str
    m: int
    cell: int
    e0: F
    rho: F
    g_hi: F
    A0: F
    A1: F
    A2: F
    terms: list                         # list[SourceTerm], r = 0..m-1, each weighted 1/m
    W: tuple = (F(0), F(0))             # whole-cell W enclosure sum (lo, hi), already c-weighted
    H_K1: tuple | None = None           # whole-cell K1 enclosure of R''_m, or None
    label: str = ""
    meta: dict = field(default_factory=dict)

    @property
    def x_lo(self) -> F:
        return self.e0 - self.rho

    @property
    def x_hi(self) -> F:
        return self.e0 + self.rho


def rad_poly(cp: CellProfile, t: SourceTerm) -> Poly:
    """rad_r(s) = A0 p2(s) + 2 A1 p1(s) + A2 p0(s), plus the centre-motion term s*|G(a)|."""
    _check(cp)
    p0 = [t.fF, t.fD, t.fH / 2, t.fG / 6, t.Env4 / 24]
    p1 = [t.fD, t.fH, t.fG / 2, t.Env4 / 6]
    p2 = [t.fH, t.fG, t.Env4 / 2]
    r = padd(padd(pscale(p2, cp.A0), pscale(p1, 2 * cp.A1)), pscale(p0, cp.A2))
    return padd(r, [F(0), t.abs_G_at_a])


def lo_hi_polys(cp: CellProfile) -> tuple:
    """TC profile bounds lo(s), hi(s) of R''_m(e0 +- s) (before the K1 cap)."""
    _check(cp)
    m = F(len(cp.terms))
    lo: Poly = [cp.W[0]]
    hi: Poly = [cp.W[1]]
    for t in cp.terms:
        rp = rad_poly(cp, t)
        lo = padd(lo, padd([t.H_at_a[0]], rp, F(-1)), F(1) / m)
        hi = padd(hi, padd([t.H_at_a[1]], rp), F(1) / m)
    return lo, hi


def _iv_ok(iv) -> bool:
    return iv is None or (len(iv) == 2 and iv[0] <= iv[1])


def _check(cp: CellProfile) -> None:
    Q.guard_cell(cp.detector, cp.m, cp.cell)
    Q.guard_drift(cp.x_lo, cp.x_hi)            # geometry binding: refuses the tail band whatever the label
    if len(cp.terms) != cp.m:
        raise ValueError("label m must equal the number of source terms (1/m weights)")
    if not (_iv_ok(cp.W) and _iv_ok(cp.H_K1) and all(_iv_ok(t.H_at_a) for t in cp.terms)):
        raise ValueError("intervals must be ordered (lo <= hi)")
    if not cp.x_lo > 0:
        raise ValueError("TPT needs x_lo > 0 (it integrates t, not |t|)")
    if cp.rho <= 0:
        raise ValueError("rho must be positive")
    for t in cp.terms:
        for v in (t.abs_G_at_a, t.fF, t.fD, t.fH, t.fG, t.Env4):
            if v < 0:
                raise ValueError("profile coefficients must be >= 0 (monotone profile)")
    if min(cp.A0, cp.A1, cp.A2) < 0:
        raise ValueError("atom constants must be >= 0")


def _crossing(poly: Poly, level: F, rho: F, decreasing: bool, bits: int = 60) -> F | None:
    """rational s' in [0, rho] at or BEFORE the crossing of poly(s) with level (monotone poly), i.e. on the
    side where the profile (not the cap) binds; None if the profile binds on all of [0, rho]."""
    f0, f1 = peval(poly, F(0)) - level, peval(poly, rho) - level
    if decreasing:
        if f0 <= 0:
            return F(0)
        if f1 >= 0:
            return None
    else:
        if f0 >= 0:
            return F(0)
        if f1 <= 0:
            return None
    a, b = F(0), rho
    for _ in range(bits):
        mid = (a + b) / 2
        v = peval(poly, mid) - level
        if (v > 0) == decreasing:
            a = mid
        else:
            b = mid
    return a  # non-binding side (T3): exact on [0, a], cap used on [a, rho] is an over-estimate there


def penalty_closed(cp: CellProfile) -> dict:
    """Corollary TPT-M: P* = max(0, I_right, I_left), each an exact polynomial integral (upper bound
    when the K1 cap is split at a rational s')."""
    _check(cp)
    lo, hi = lo_hi_polys(cp)
    e0, rho = cp.e0, cp.rho
    # right side: integrand (e0 + s) * (-L(s)),  L = max(capLo, lo(s))
    tR = [e0, F(1)]
    negLo = pscale(lo, F(-1))
    if cp.H_K1 is not None:
        sR = _crossing(lo, cp.H_K1[0], rho, decreasing=True)
    else:
        sR = None
    if sR is None:
        I_right = pint(pmul(tR, negLo), F(0), rho)
    else:
        I_right = pint(pmul(tR, negLo), F(0), sR) + pint(pscale(tR, -cp.H_K1[0]), sR, rho)
    # left side: t = e0 - s, integrand (e0 - s) * U(e0 - s), U = min(capHi, hi(s)); dt = ds
    tL = [e0, F(-1)]
    if cp.H_K1 is not None:
        sL = _crossing(hi, cp.H_K1[1], rho, decreasing=False)
    else:
        sL = None
    if sL is None:
        I_left = pint(pmul(tL, hi), F(0), rho)
    else:
        I_left = pint(pmul(tL, hi), F(0), sL) + pint(pscale(tL, cp.H_K1[1]), sL, rho)
    P = max(F(0), I_right, I_left)
    return {"P_star": P, "I_right": I_right, "I_left": I_left, "split_right": sR, "split_left": sL}


def penalty_riemann(cp: CellProfile, N: int = 64) -> F:
    """Independent monotone Riemann upper sum for P* (Corollary TPT-M)."""
    _check(cp)
    lo, hi = lo_hi_polys(cp)
    e0, rho = cp.e0, cp.rho

    def L(s):
        v = peval(lo, s)
        return v if cp.H_K1 is None else max(cp.H_K1[0], v)

    def U(s):
        v = peval(hi, s)
        return v if cp.H_K1 is None else min(cp.H_K1[1], v)

    right = F(0)
    left = F(0)
    for i in range(N):
        a, b = rho * i / N, rho * (i + 1) / N
        f = -L(b)  # -L non-decreasing in s: sup on [a,b] at b
        right += (b - a) * max((e0 + a) * f, (e0 + b) * f)
        u = U(b)   # U(e0 - s) non-decreasing in s
        left += (b - a) * max((e0 - a) * u, (e0 - b) * u)
    return max(F(0), right, left)


def penalty_riemann_lower(cp: CellProfile, N: int = 64) -> F:
    """Monotone Riemann LOWER sum of max(0, I_right(rho), I_left(rho)) -- a lower bound of P* (TPT-M)."""
    _check(cp)
    lo, hi = lo_hi_polys(cp)
    e0, rho = cp.e0, cp.rho

    def L(s):
        v = peval(lo, s)
        return v if cp.H_K1 is None else max(cp.H_K1[0], v)

    def U(s):
        v = peval(hi, s)
        return v if cp.H_K1 is None else min(cp.H_K1[1], v)

    right = F(0)
    left = F(0)
    for i in range(N):
        a, b = rho * i / N, rho * (i + 1) / N
        f = -L(a)
        right += (b - a) * min((e0 + a) * f, (e0 + b) * f)
        u = U(a)
        left += (b - a) * min((e0 - a) * u, (e0 - b) * u)
    return max(F(0), right, left)


def whole_cell_enclosure(cp: CellProfile) -> tuple:
    _check(cp)
    lo, hi = lo_hi_polys(cp)
    Hlo, Hhi = peval(lo, cp.rho), peval(hi, cp.rho)
    if cp.H_K1 is not None:
        Hlo, Hhi = max(Hlo, cp.H_K1[0]), min(Hhi, cp.H_K1[1])
    if Hlo > Hhi:
        raise ValueError("empty enclosure")
    return Hlo, Hhi


def penalty_c5t(cp: CellProfile) -> F:
    _check(cp)
    Hlo, Hhi = whole_cell_enclosure(cp)
    wR = cp.rho * (cp.x_hi - cp.rho / 2)
    wL = cp.rho * (cp.x_lo + cp.rho / 2)
    return max(max(-Hlo, F(0)) * wR, max(Hhi, F(0)) * wL)


def penalty_frozen(cp: CellProfile) -> F:
    """rho * x_hi * mag(H); equals the consumed frozen clause rho*x_hi*M_k whenever M_k = mag(H_final)
    (true on all 136 lower-front pairs, V3); a consumer with M_k < mag(H_final) would differ."""
    _check(cp)
    Hlo, Hhi = whole_cell_enclosure(cp)
    return cp.rho * cp.x_hi * max(abs(Hlo), abs(Hhi))


def evaluate(cp: CellProfile) -> dict:
    pc = penalty_closed(cp)
    pr = penalty_riemann(cp)
    pl = penalty_riemann_lower(cp)
    c5 = penalty_c5t(cp)
    fr = penalty_frozen(cp)
    if not (pl <= pc["P_star"] and pl <= pr):
        raise AssertionError("V4: Riemann lower sum above an upper bound of P*")
    if not (pc["P_star"] <= c5 <= fr):
        raise AssertionError("TPT-D dominance violated")
    return {"P_tpt": pc["P_star"], "P_riemann": pr, "P_riemann_lower": pl, "P_c5t": c5, "P_frozen": fr,
            "Gamma_tpt": cp.g_hi + pc["P_star"], "Gamma_c5t": cp.g_hi + c5,
            "Gamma_frozen": cp.g_hi + fr, "detail": pc}


# ----------------------------------------------------------------------------- TPT-B (block-resolved)

@dataclass
class Block:
    """Atom constants valid for every e in [e_lo, e_hi] (e.g. one registry sub-block)."""
    e_lo: F
    e_hi: F
    A0: F
    A1: F
    A2: F


def _lo_hi_with(cp: CellProfile, A: tuple) -> tuple:
    saved = (cp.A0, cp.A1, cp.A2)
    cp.A0, cp.A1, cp.A2 = A
    try:
        return lo_hi_polys(cp)
    finally:
        cp.A0, cp.A1, cp.A2 = saved


def _check_blocks(cp: CellProfile, blocks: list) -> list:
    _check(cp)
    bl = sorted(blocks, key=lambda b: b.e_lo)
    if not bl or bl[0].e_lo > cp.x_lo or bl[-1].e_hi < cp.x_hi:
        raise ValueError("blocks must cover the cell")
    for a, b in zip(bl, bl[1:]):
        if b.e_lo > a.e_hi:
            raise ValueError("blocks must be contiguous (no gap)")
    for b in bl:
        Q.guard_drift(b.e_lo, b.e_hi)
        if min(b.A0, b.A1, b.A2) < 0 or b.e_lo > b.e_hi:
            raise ValueError("bad block")
    return bl


def penalty_blocked(cp: CellProfile, blocks: list) -> dict:
    """Theorem TPT-B: the profile uses, at each t, the constants of a block containing t.

    Within one block the integrand t*(-L(t)) (right) / t*U(t) (left) is monotone in s = |t - e0|, so the running
    integral I(e) is quasi-convex on each piece and its supremum over the cell is attained at a piece endpoint.
    P*_B = max(0, max over right piece ends of I_right, max over left piece ends of I_left), each an exact
    polynomial integral (the K1 cap, if any, is handled per piece by the non-binding-side split, an upper bound).
    """
    bl = _check_blocks(cp, blocks)
    e0, rho = cp.e0, cp.rho

    def piece_integral(A, s_a, s_b, side):
        lo, hi = _lo_hi_with(cp, A)
        if side == "R":
            tpoly = [e0, F(1)]
            prof = pscale(lo, F(-1))
            cap = None if cp.H_K1 is None else -cp.H_K1[0]
            crossing = None if cp.H_K1 is None else _crossing(lo, cp.H_K1[0], rho, decreasing=True)
        else:
            tpoly = [e0, F(-1)]
            prof = hi
            cap = None if cp.H_K1 is None else cp.H_K1[1]
            crossing = None if cp.H_K1 is None else _crossing(hi, cp.H_K1[1], rho, decreasing=False)
        if cap is None or crossing is None or crossing >= s_b:
            return pint(pmul(tpoly, prof), s_a, s_b)
        if crossing <= s_a:
            return pint(pscale(tpoly, cap), s_a, s_b)
        return pint(pmul(tpoly, prof), s_a, crossing) + pint(pscale(tpoly, cap), crossing, s_b)

    best = F(0)
    # right side: pieces of [e0, x_hi]
    cuts = sorted({e0, cp.x_hi} | {b.e_lo for b in bl if e0 < b.e_lo < cp.x_hi}
                  | {b.e_hi for b in bl if e0 < b.e_hi < cp.x_hi})
    run = F(0)
    for a, b in zip(cuts, cuts[1:]):
        mid = (a + b) / 2
        blk = [x for x in bl if x.e_lo <= mid <= x.e_hi]
        A = (max(x.A0 for x in blk), max(x.A1 for x in blk), max(x.A2 for x in blk))
        run += piece_integral(A, a - e0, b - e0, "R")
        best = max(best, run)
    run_r = run
    cuts = sorted({cp.x_lo, e0} | {b.e_lo for b in bl if cp.x_lo < b.e_lo < e0}
                  | {b.e_hi for b in bl if cp.x_lo < b.e_hi < e0}, reverse=True)
    run = F(0)
    for a, b in zip(cuts, cuts[1:]):  # a > b, moving left from e0
        mid = (a + b) / 2
        blk = [x for x in bl if x.e_lo <= mid <= x.e_hi]
        A = (max(x.A0 for x in blk), max(x.A1 for x in blk), max(x.A2 for x in blk))
        run += piece_integral(A, e0 - a, e0 - b, "L")
        best = max(best, run)
    return {"P_star_B": best, "I_right_full": run_r, "I_left_full": run, "pieces": len(cuts)}
