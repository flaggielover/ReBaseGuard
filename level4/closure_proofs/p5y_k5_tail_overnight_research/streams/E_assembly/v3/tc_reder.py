"""Independent re-derivation of the theorem-TC whole-cell enclosure and its Taylor profile (stdlib only).

Written from p5y_k5_lower_front_order3/theorem/THEOREM_TC.md sections 2-3. It imports NO historical campaign
module (no tc_rule, no tc_crosscheck, no consumer); the frozen record fields are read as data only.

Algorithmic route (deliberately different from the frozen expanded formulas):

* the three Taylor bounds are the values at s = rho of ONE quartic and its first two derivatives,
      P(s) := f_F + s f_D + s^2 f_H / 2 + s^3 f_G / 6 + s^4 Env4 / 24,
      p0 = P(rho), p1 = P'(rho), p2 = P''(rho)          (THEOREM_TC section 3, Taylor with integral remainder);
  the same polynomials, kept in s, are the Lemma TC-P profile p0(s), p1(s), p2(s) of THEOREM_TPT section 2;
* Env4 (premise P3) is sigma4 + sum_{i=1..4} C(4,i) k_i * T_{4-i}(rho), where T_n(rho) is the Taylor
  majorant of || Ftilde^(n)(t) || for |t| <= rho, obtained by differentiating the candidate majorant
      Mc(s) := s_F + s s_D + s^2 s_H / 2 + s^3 s_G / 6
  n times and evaluating at rho;
* sigma4 (premise P3): r = 0 the frozen closed-form bound sup_S0[4]; r >= 1 the Leibniz expansion of
  S_r'''' = sum_i C(4,i) J_i(e) h_r^(4-i)(e) with the true-object tower of THEOREM_TC P3:
      ||h_1|| <= 1, ||h_1^(n)|| <= sup_S0[n-1] (n >= 1),
      ||h_j|| <= 1, ||h_j^(n)|| <= sum_{i=0..n} C(n,i) k_i ||h_{j-1}^(n-i)|| (n >= 1, j >= 2);
* f_X = delta_X + eps_src[order(X)]  (premise P2, X = F, D, H, G  <->  order 0, 1, 2, 3);
* rad_r = A0 p2 + 2 A1 p1 + A2 p0, half_r = rho |G_r(a)| + rad_r;
* assembly c(m): F_r with 1/m (r < m); W_(r, t-r-1) with 1/t - 1/m (1 <= t < m, r < t), from the frozen
  whole-cell W2 enclosures keyed "r:j".

All arithmetic is exact (fractions.Fraction).
"""
from __future__ import annotations

from fractions import Fraction as Fr
from functools import lru_cache
from math import comb

M_SCOPE = (1, 2, 3, 5)


class RederRefusal(ValueError):
    pass


# ------------------------------------------------------------------ tiny polynomial kit (coefficients low -> high)

def poly_eval(c: list, s: Fr) -> Fr:
    acc = Fr(0)
    for a in reversed(c):
        acc = acc * s + a
    return acc


def poly_deriv(c: list) -> list:
    return [i * c[i] for i in range(1, len(c))] or [Fr(0)]


def poly_deriv_n(c: list, n: int) -> list:
    for _ in range(n):
        c = poly_deriv(c)
    return c


def _nn(name: str, v: Fr) -> Fr:
    if not isinstance(v, Fr):
        raise RederRefusal(f"{name}: not an exact Fraction")
    if v < 0:
        raise RederRefusal(f"{name}: negative upper bound")
    return v


# ------------------------------------------------------------------ premise P3 pieces

def sigma4(r: int, k: list, j: list, sup_S0: list) -> Fr:
    """Upper bound of sup_C ||S_r''''|| (THEOREM_TC premise P3)."""
    if r == 0:
        return sup_S0[4]

    @lru_cache(maxsize=None)
    def h(jj: int, n: int) -> Fr:
        if n == 0:
            return Fr(1)
        if jj == 1:
            return sup_S0[n - 1]
        return sum((comb(n, i) * k[i] * h(jj - 1, n - i) for i in range(n + 1)), Fr(0))

    return sum((comb(4, i) * j[i] * h(r, 4 - i) for i in range(5)), Fr(0))


def env4(sups: list, k: list, sig4: Fr, rho: Fr) -> Fr:
    """Env4 of premise P3 via the derivative majorant Mc(s) of the Taylor candidate."""
    sF, sD, sH, sG = sups
    Mc = [sF, sD, sH / 2, sG / 6]
    tot = sig4
    for i in range(1, 5):
        tot += comb(4, i) * k[i] * poly_eval(poly_deriv_n(Mc, 4 - i), rho)
    return tot


# ------------------------------------------------------------------ per-source term

def source_term(rec: dict, r: int, A: dict) -> dict:
    """All theorem-TC quantities of object r in one frozen cell record, plus its Taylor profile polynomials."""
    o = rec["r"][str(r)]
    rho = _nn("rho", Fr(rec["rho"]))
    k = [_nn(f"k{i}", Fr(x)) for i, x in enumerate(rec["norms"]["k"])]
    j = [_nn(f"j{i}", Fr(x)) for i, x in enumerate(rec["norms"]["j"])]
    s0 = [_nn(f"supS0_{i}", Fr(x)) for i, x in enumerate(rec["sup_S0"])]
    if len(k) != 5 or len(j) != 5 or len(s0) != 5:
        raise RederRefusal("norm / source-sup tables must have 5 entries")
    eps = [_nn(f"eps{i}", Fr(x)) for i, x in enumerate(o["eps_src"])]
    f = [_nn("delta_F", Fr(o["delta_F"])) + eps[0], _nn("delta_D", Fr(o["delta_D"])) + eps[1],
         _nn("delta_H", Fr(o["delta_H"])) + eps[2], _nn("delta_G", Fr(o["delta_G"])) + eps[3]]
    sups = [_nn(f"sup_{x}", Fr(o["sup"][x])) for x in ("F", "D", "H", "G")]
    sig = sigma4(r, k, j, s0)
    E4 = env4(sups, k, sig, rho)
    P = [f[0], f[1], f[2] / 2, f[3] / 6, E4 / 24]           # P(s)
    P1 = poly_deriv(P)                                       # P'(s)  = p1(s)
    P2 = poly_deriv(P1)                                      # P''(s) = p2(s)
    p0, p1, p2 = poly_eval(P, rho), poly_eval(P1, rho), poly_eval(P2, rho)
    A0, A1, A2 = (_nn(x, A[x]) for x in ("A0", "A1", "A2"))
    rad = A0 * p2 + 2 * A1 * p1 + A2 * p0
    absG = _nn("abs_G_at_a", Fr(o["abs_G_at_a"]))
    Hlo, Hhi = (Fr(x) for x in o["H_at_a"])
    if Hlo > Hhi:
        raise RederRefusal("inverted centre interval H_at_a")
    # profile radius polynomial in s (Lemma TC-P), centre-motion |G| s included (sign of G(a) is not recorded)
    pad = lambda c: c + [Fr(0)] * (len(P) - len(c))  # noqa: E731
    radpoly = [A0 * a + 2 * A1 * b + A2 * c for a, b, c in zip(pad(P2), pad(P1), P)]
    radpoly[1] += absG
    return {"r": r, "f": f, "sups": sups, "sigma4": sig, "Env4": E4, "p": (p0, p1, p2), "rad": rad,
            "half": rho * absG + rad, "H_at_a": (Hlo, Hhi), "abs_G_at_a": absG, "radpoly_s": radpoly}


def w_terms(m: int) -> list:
    """(r, j, c) for the W part of the frozen assembly: W_(r, t-r-1) with 1/t - 1/m."""
    return [(r, t - r - 1, Fr(1, t) - Fr(1, m)) for t in range(1, m) for r in range(t)]


def w_sum(rec: dict, m: int) -> tuple:
    lo = hi = Fr(0)
    for r, jj, c in w_terms(m):
        a, b = (Fr(x) for x in rec["W2"][f"{r}:{jj}"])
        if a > b or c < 0:
            raise RederRefusal("inverted W enclosure or negative coefficient")
        lo += c * a
        hi += c * b
    return lo, hi


def whole_cell(rec: dict, A: dict, m: int) -> dict:
    """The theorem-TC whole-cell enclosure H_m of R''_m on the cell (THEOREM_TC section 3)."""
    if m not in M_SCOPE:
        raise RederRefusal(f"m={m} outside the frozen scope")
    terms = [source_term(rec, r, A) for r in range(m)]
    wlo, whi = w_sum(rec, m)
    lo = wlo + sum(((t["H_at_a"][0] - t["half"]) for t in terms), Fr(0)) / m
    hi = whi + sum(((t["H_at_a"][1] + t["half"]) for t in terms), Fr(0)) / m
    return {"H": (lo, hi), "terms": terms, "W": (wlo, whi)}


def profile_polys(wc: dict, m: int) -> tuple:
    """lo(s), hi(s): the Lemma TC-P profile of R''_m(e0 +- s), s in [0, rho] (no cap)."""
    lo = [wc["W"][0]]
    hi = [wc["W"][1]]
    for t in wc["terms"]:
        rp = t["radpoly_s"]
        n = max(len(lo), len(rp))
        lo = [(lo[i] if i < len(lo) else Fr(0)) - (rp[i] if i < len(rp) else Fr(0)) / m for i in range(n)]
        hi = [(hi[i] if i < len(hi) else Fr(0)) + (rp[i] if i < len(rp) else Fr(0)) / m for i in range(n)]
        lo[0] += t["H_at_a"][0] / m
        hi[0] += t["H_at_a"][1] / m
    return lo, hi


def exact_Pstar_nocap(lo: list, hi: list, e0: Fr, rho: Fr) -> dict:
    """Independent exact P* (Corollary TPT-M) with no cap: both one-sided integrals in closed form,
    I_R = int_0^rho (e0+s)(-lo(s)) ds, I_L = int_0^rho (e0-s) hi(s) ds, via antiderivatives."""
    def integ(c: list) -> Fr:          # int_0^rho c(s) ds
        return sum((a * rho ** (i + 1) / (i + 1) for i, a in enumerate(c)), Fr(0))

    negl = [-a for a in lo]
    IR = e0 * integ(negl) + integ([Fr(0)] + negl)
    IL = e0 * integ(hi) - integ([Fr(0)] + hi)
    return {"I_right": IR, "I_left": IL, "P_star": max(Fr(0), IR, IL)}


def lower_sum(lo: list, hi: list, e0: Fr, rho: Fr, N: int, cap: tuple | None = None) -> Fr:
    """Riemann LOWER sum of P* for the monotone profile (independent bracket from below)."""
    def L(s):
        v = poly_eval(lo, s)
        return v if cap is None else max(cap[0], v)

    def U(s):
        v = poly_eval(hi, s)
        return v if cap is None else min(cap[1], v)

    R = Lft = Fr(0)
    for i in range(N):
        a, b = rho * i / N, rho * (i + 1) / N
        f = -L(a)                      # inf of the non-decreasing -L on [a, b]
        R += (b - a) * min((e0 + a) * f, (e0 + b) * f)
        u = U(a)                       # inf of the non-decreasing U(e0 - s) on [a, b]
        Lft += (b - a) * min((e0 - a) * u, (e0 - b) * u)
    return max(Fr(0), R, Lft)
