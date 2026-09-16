"""R3 Part D: minimal certified He_6 extension for the order-5/6 norms the graded wiring and the R^(5) majorant need.

The frozen table (p5y_k1_final_completion/code/sharp_norms._roots) stops at He_5 and says "extend the table
deliberately". It is NOT edited. This module is a separate, R3-bound source artifact:

    He_6(x) = x^6 - 15 x^4 + 45 x^2 - 15 = x He_5 - 5 He_4          (recurrence, checked exactly)
    roots   = +-sqrt(t_i),  t_1 < t_2 < t_3 the roots of c(t) = t^3 - 15 t^2 + 45 t - 15, all positive
    t_i     isolated by EXACT rational sign changes on a rational grid, bisected to width 2^-(bits+32); the root ball
            is arb.union of the exact bracket endpoints, and sqrt is outward (Arb)

Provided (each is min(drift-aware, reviewed whole-line) exactly as the frozen sharp_norms pattern):
    k5(left, right)            frozen sharp_norms.kernel_norm(5, ...)                              (He_5 roots, frozen)
    k6(left, right)            min(int_W |He_6| phi, reviewed Cauchy-Schwarz sqrt(6!))
    j5(left, right)            min(int_W |He_6| phi, reviewed raw_kernel_norm(5, e_max))
    j6(left, right)            reviewed raw_kernel_norm(6, e_max)                                   (no He_7 needed)
    sup_S0_on(5, left, right)  min(sup_(Y_u)|He_5 phi| + sup_(Y_l)|He_5 phi|, reviewed 2 sup|phi^(5)|)   (He_6 roots)
    sup_S0_on(n>=6, ...)       reviewed 2 sup|phi^(n)| (Cramer)
Fail closed: a root ball that is neither certainly inside nor certainly outside an integration / search window
raises (no silent split).
"""
from __future__ import annotations

import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(CP / "p5y_k1_cusum_aux5_successor/code"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ancestry5  # noqa: E402,F401

from flint import arb, ctx  # noqa: E402

import opnorms as reviewed  # noqa: E402
import order2  # noqa: E402
import sharp_norms  # noqa: E402
from intervals import exact, tight_upper  # noqa: E402

HE6_COEFFS = [F(-15), F(0), F(45), F(0), F(-15), F(0), F(1)]   # ascending powers
CUBIC = [F(-15), F(45), F(-15), F(1)]                            # c(t), ascending
K_FROZEN, C_FROZEN = F(1, 2), F(11, 2)


class HermiteExtensionRefusal(ArithmeticError):
    pass


def _peval(coeffs, x: F) -> F:
    acc = F(0)
    for c in reversed(coeffs):
        acc = acc * x + c
    return acc


def he_coeffs(n: int) -> list[F]:
    """Exact ascending coefficients of He_n by the three-term recurrence."""
    a, b = [F(1)], [F(0), F(1)]
    if n == 0:
        return a
    for k in range(1, n):
        nxt = [F(0)] + b
        for i, c in enumerate(a):
            nxt[i] -= k * c
        a, b = b, nxt
    return b


def isolate_cubic_roots(bits: int) -> list[tuple[F, F]]:
    grid = [F(i, 4) for i in range(0, 81)]                   # [0, 20]; c(20) > 0 and all roots lie below 15
    brackets = []
    for a, b in zip(grid[:-1], grid[1:]):
        fa, fb = _peval(CUBIC, a), _peval(CUBIC, b)
        if fa == 0 or fb == 0:
            raise HermiteExtensionRefusal("grid hits a root exactly")
        if (fa < 0) != (fb < 0):
            brackets.append((a, b))
    if len(brackets) != 3:
        raise HermiteExtensionRefusal(f"expected 3 sign changes, found {len(brackets)}")
    width = F(1, 2 ** (bits + 32))
    out = []
    for a, b in brackets:
        fa = _peval(CUBIC, a)
        while b - a > width:
            mid = (a + b) / 2
            fm = _peval(CUBIC, mid)
            if fm == 0:
                a = b = mid
                break
            if (fm < 0) == (fa < 0):
                a, fa = mid, fm
            else:
                b = mid
        out.append((a, b))
    return out


_ROOT_CACHE: dict = {}


def root_balls(bits: int | None = None) -> list[arb]:
    bits = ctx.prec if bits is None else bits
    if bits in _ROOT_CACHE:
        return list(_ROOT_CACHE[bits])
    ts = isolate_cubic_roots(bits)
    pos = [exact(a).union(exact(b)).sqrt() for a, b in ts]
    balls = [-r for r in reversed(pos)] + pos
    for x, y in zip(balls[:-1], balls[1:]):
        if not x.upper() < y.lower():
            raise HermiteExtensionRefusal("root balls not certainly ordered")
    _ROOT_CACHE[bits] = tuple(balls)
    return balls


def verification(bits: int = 256) -> dict:
    """Exact and certified checks of the extension (used by the qualification)."""
    from flint import arb as A
    rec = he_coeffs(6) == HE6_COEFFS and he_coeffs(5) == [F(0), F(15), F(0), F(-10), F(0), F(1)]
    xs = [F(-7, 3), F(-1, 2), F(0), F(5, 7), F(13, 4)]
    frozen_match = all(bool((sharp_norms.hermite_he(6, exact(x)) - exact(_peval(HE6_COEFFS, x))).contains(0))
                       for x in xs)
    ts = isolate_cubic_roots(bits)
    sign_changes = all((_peval(CUBIC, a) < 0) != (_peval(CUBIC, b) < 0) for a, b in ts)
    positive = all(a > 0 for a, _ in ts)
    balls = root_balls(bits)
    contains_zero = all(bool(sharp_norms.hermite_he(6, r).contains(0)) for r in balls)
    widths = max(float(r.rad()) for r in balls)
    return {"recurrence_exact": rec, "matches_frozen_hermite_he_at_rationals": frozen_match,
            "cubic_sign_changes_exact": sign_changes, "cubic_roots_positive": positive, "root_count": len(balls),
            "ordered_disjoint": True, "He6_ball_contains_zero_at_each_root": contains_zero,
            "max_root_ball_radius": widths, "roots_mid": [float(r.mid()) for r in balls],
            "pass": rec and frozen_match and sign_changes and positive and len(balls) == 6 and contains_zero}


def _interior(roots, lo: arb, hi: arb):
    cuts = []
    for r in roots:
        if r > lo and r < hi:
            cuts.append(r)
        elif r < lo or r > hi:
            continue
        else:
            raise HermiteExtensionRefusal("root ball straddles a window endpoint")
    return cuts


def absolute_hermite_moment6(lo: arb, hi: arb) -> arb:
    cuts = [lo] + _interior(root_balls(), lo, hi) + [hi]
    total = arb(0)
    for a, b in zip(cuts[:-1], cuts[1:]):
        total = total + (sharp_norms._antiderivative(6, b) - sharp_norms._antiderivative(6, a)).abs_upper()
    return tight_upper(total)


def _min(a, b):
    return a if a.upper() <= b.upper() else b


def k5(left, right) -> arb:
    return sharp_norms.kernel_norm(5, left, right)


def k6(left, right) -> arb:
    lo, hi = sharp_norms._window(left, right)
    return tight_upper(_min(absolute_hermite_moment6(lo, hi), reviewed.kernel_norm(6)))


def j5(left, right) -> arb:
    lo, hi = sharp_norms._window(left, right)
    e_max = exact(max(abs(F(left)), abs(F(right))))
    return tight_upper(_min(absolute_hermite_moment6(lo, hi), reviewed.raw_kernel_norm(5, e_max)))


def j6(left, right) -> arb:
    e_max = exact(max(abs(F(left)), abs(F(right))))
    return tight_upper(reviewed.raw_kernel_norm(6, e_max))


def sup_phi5_on(lo: arb, hi: arb) -> arb:
    pts = [lo, hi] + _interior(root_balls(), lo, hi)
    best = arb(0)
    for y in pts:
        val = (sharp_norms.hermite_he(5, y) * sharp_norms.phi(y)).abs_upper()
        best = val if val.upper() > best.upper() else best
    return tight_upper(best)


def sup_S0_on(n: int, left, right) -> arb:
    """sup over e in [left, right] and the reachable arguments of |S_0^(n)|."""
    if n <= 4:
        return order2.sup_source_derivative_on(n, left, right)
    if n == 5:
        e_lo, e_hi = exact(F(left)), exact(F(right))
        sharp = sup_phi5_on(exact(K_FROZEN) + e_lo, exact(C_FROZEN) + e_hi) + \
            sup_phi5_on(-exact(C_FROZEN) + e_lo, -exact(K_FROZEN) + e_hi)
        return tight_upper(_min(tight_upper(sharp), reviewed.sup_source_derivative(5)))
    return tight_upper(reviewed.sup_source_derivative(n))


def norm_table(left, right) -> dict:
    """k_0..k_6, j_0..j_6 for the cell [left, right] (frozen orders 0..4 plus this extension)."""
    t = sharp_norms.table(left, right)
    k = {i: t["k"][i] for i in range(5)}
    j = {i: t["j"][i] for i in range(5)}
    k[5], k[6] = k5(left, right), k6(left, right)
    j[5], j[6] = j5(left, right), j6(left, right)
    return {"k": k, "j": j}
