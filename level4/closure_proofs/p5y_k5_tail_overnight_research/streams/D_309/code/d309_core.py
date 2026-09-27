"""Stream D shared machinery: exact-rational theorem-TC pipeline on synthetic finite-state drift families.

Target-free.  Nothing here reads a CUSUM cell, a K1 record, a registry or any committed tail value.  Every entry point
that takes a drift interval calls ``ov_quarantine.guard_drift`` (defence in depth: the FSM drift parameter is synthetic,
but the guard is cheap and makes the module unusable on the quarantined band).

Contents
  * polynomials in one variable (coefficient lists, low -> high), exact Taylor shift, and RIGOROUS range bounds
    (``sup_abs_on`` / ``min_on``) by recursive bisection with the exact Taylor remainder form;
  * cell-uniform operator bounds k_i >= sup_C ||K_i(e)||, C >= sup_C ||R_e|| (Neumann), source sups sigma_n;
  * ``TCFixture``: theorem-TC / TC-T objects for one source with FIXED candidates (F^, D^, H^, G^), computed two ways:
      - the Leibniz path (phi^(j)(e0) from K_i and the candidates), and
      - an independent polynomial path (phi(e) = S(e) - (I - K_e) F~(e) expanded exactly as a polynomial in t = e - e0),
    so the order-3 / order-4 identities are checked, not assumed.
"""
from __future__ import annotations

import random
import sys
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path

HERE = Path(__file__).resolve().parent
STREAM = HERE.parent
NS = STREAM.parents[1]
sys.path.insert(0, str(NS / "code"))
import ov_fixtures as X  # noqa: E402
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()

# ----------------------------------------------------------------------------------------------- polynomials


def p_eval(c: list, x: F) -> F:
    acc = F(0)
    for a in reversed(c):
        acc = acc * x + a
    return acc


def p_deriv(c: list, k: int = 1) -> list:
    for _ in range(k):
        c = [i * c[i] for i in range(1, len(c))] or [F(0)]
    return c


def p_add(a: list, b: list, s: F = F(1)) -> list:
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else F(0)) + s * (b[i] if i < len(b) else F(0)) for i in range(n)]


def p_scale(a: list, s: F) -> list:
    return [s * x for x in a]


def p_mul(a: list, b: list) -> list:
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0:
            continue
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def p_taylor(c: list, x0: F) -> list:
    """coefficients of t -> c(x0 + t)."""
    out = []
    d = list(c)
    for k in range(len(c)):
        out.append(p_eval(d, x0) / factorial(k))
        d = p_deriv(d, 1)
    return out


def _piece_bounds(c: list, a: F, b: F) -> tuple:
    """On [a,b]: (upper bound of max|c|, lower bound of max|c|, lower bound of min c, upper bound of min c)."""
    m = (a + b) / 2
    h = (b - a) / 2
    d = p_taylor(c, m)
    tail = sum((abs(d[k]) * h ** k for k in range(1, len(d))), F(0))
    ub_abs = abs(d[0]) + tail
    vals = (p_eval(c, a), p_eval(c, b), d[0])
    lb_abs = max(abs(v) for v in vals)
    lb_min = d[0] - tail
    ub_min = min(vals)
    return ub_abs, lb_abs, lb_min, ub_min


def sup_abs_on(c: list, lo: F, hi: F, rel_tol: F = F(1, 10 ** 6), max_depth: int = 40) -> tuple:
    """RIGOROUS (upper, lower) bounds on max_{t in [lo,hi]} |c(t)|.  Exact rationals; the upper bound is the Taylor
    remainder form |c(m)| + sum_k |c^(k)(m)/k!| h^k on every accepted piece, which is a true bound on the piece."""
    lo, hi = F(lo), F(hi)
    if hi < lo:
        lo, hi = hi, lo
    if len(c) <= 1 or lo == hi:
        v = abs(p_eval(c, lo))
        return v, v
    best_lo = F(0)
    accepted = F(0)
    stack = [(lo, hi, 0)]
    while stack:
        a, b, dpt = stack.pop()
        ub, lb, _, _ = _piece_bounds(c, a, b)
        best_lo = max(best_lo, lb)
        if ub <= best_lo * (1 + rel_tol) or dpt >= max_depth or ub == 0:
            accepted = max(accepted, ub)
        else:
            mid = (a + b) / 2
            stack.append((a, mid, dpt + 1))
            stack.append((mid, b, dpt + 1))
    # pieces accepted early against a smaller best_lo remain valid upper bounds; the max is a valid upper bound
    return max(accepted, best_lo), best_lo


def min_on(c: list, lo: F, hi: F, abs_tol: F = F(1, 10 ** 12), max_depth: int = 40) -> F:
    """RIGOROUS lower bound on min_{t in [lo,hi]} c(t)."""
    lo, hi = F(lo), F(hi)
    if len(c) <= 1 or lo == hi:
        return p_eval(c, lo)
    best_up = None
    accepted = None
    stack = [(lo, hi, 0)]
    while stack:
        a, b, dpt = stack.pop()
        _, _, lbm, ubm = _piece_bounds(c, a, b)
        best_up = ubm if best_up is None else min(best_up, ubm)
        if lbm >= best_up - abs_tol or dpt >= max_depth or lbm >= 0:
            accepted = lbm if accepted is None else min(accepted, lbm)
        else:
            mid = (a + b) / 2
            stack.append((a, mid, dpt + 1))
            stack.append((mid, b, dpt + 1))
    return accepted


# ----------------------------------------------------------------------------------------------- families


def guard_interval(lo: F, hi: F) -> None:
    Q.guard_drift(F(lo), F(hi))


def make_family(n: int, seed: int, e_hi: F, deg: int = 4, kill: F = F(1, 5)) -> X.DriftFamily:
    """ov_fixtures.random_family with kernel degree ``deg`` in e (K_1..K_deg non-zero)."""
    guard_interval(F(0), e_hi)
    return X.random_family(n, seed=seed, e_range=(F(0), e_hi), deg=deg, kill=kill)


def make_sources(n: int, count: int, seed: int, deg: int = 5) -> list:
    rng = random.Random(7919 * seed + 17)
    return [[[F(rng.randint(-10, 10), 10) for _ in range(deg + 1)] for _ in range(n)] for _ in range(count)]


def k_cell(fam: X.DriftFamily, i: int, lo: F, hi: F) -> F:
    """k_i >= sup_{e in [lo,hi]} ||K_i(e)||  (max row sum of entrywise rigorous sups)."""
    guard_interval(lo, hi)
    best = F(0)
    for row in fam.kp:
        tot = F(0)
        for p in row:
            d = p_deriv(p, i)
            tot += sup_abs_on(d, lo, hi)[0]
        best = max(best, tot)
    return best


def C_cell(fam: X.DriftFamily, e0: F, rho: F) -> F:
    """C >= sup_{|e-e0|<=rho} ||R_e||, by the Neumann perturbation bound ||R_e|| <= ||R0|| / (1 - ||R0|| d)."""
    lo, hi = e0 - rho, e0 + rho
    guard_interval(lo, hi)
    R0 = X.op_norm(fam.R(e0))
    d = F(0)
    for row in fam.kp:
        tot = F(0)
        for p in row:
            diff = p_add(p, [p_eval(p, e0)], F(-1))
            tot += sup_abs_on(diff, lo, hi)[0]
        d = max(d, tot)
    if R0 * d >= 1:
        raise ValueError("Neumann bound fails on this cell")
    return R0 / (1 - R0 * d)


def sigma_cell(sp: list, nder: int, lo: F, hi: F) -> F:
    guard_interval(lo, hi)
    return max(sup_abs_on(p_deriv(p, nder), lo, hi)[0] for p in sp)


# ----------------------------------------------------------------------------------------------- vectors


def vnorm(v: list) -> F:
    return max(abs(x) for x in v)


def vabs(v: list) -> list:
    return [abs(x) for x in v]


def vadd(*terms) -> list:
    """vadd((c1, v1), (c2, v2), ...) = sum c_i v_i."""
    n = len(terms[0][1])
    out = [F(0)] * n
    for c, v in terms:
        for i in range(n):
            out[i] += c * v[i]
    return out


def mv(A: list, v: list) -> list:
    return X.mat_vec(A, v)


def I_minus(A: list) -> list:
    n = len(A)
    return [[F(int(i == j)) - A[i][j] for j in range(n)] for i in range(n)]


# ----------------------------------------------------------------------------------------------- TC fixture


class TCFixture:
    """Theorem-TC objects for one source S (polynomial vector in e) with fixed candidates at e0.

    candidates: dict with keys F, D, H, G (vectors); G defaults to zero (premise P2' of TC-T).
    """

    def __init__(self, fam: X.DriftFamily, sp: list, e0: F, rho: F, cand: dict):
        self.fam, self.sp, self.e0, self.rho = fam, sp, F(e0), F(rho)
        self.lo, self.hi = self.e0 - self.rho, self.e0 + self.rho
        guard_interval(self.lo, self.hi)
        self.n = fam.n
        self.Fh, self.Dh, self.Hh = cand["F"], cand["D"], cand["H"]
        self.Gh = cand.get("G", [F(0)] * self.n)
        self.K = [fam.K(self.e0, i) for i in range(6)]
        self.S = [[p_eval(p_deriv(p, i), self.e0) for p in sp] for i in range(6)]
        self.famr = X.DriftFamily(fam.kp, sp, (fam.e_lo, fam.e_hi))
        self._phi_poly = None

    # -- Leibniz path: phi^(j)(e0), j = 0..5
    def phi_leibniz(self, j: int) -> list:
        K, S, n = self.K, self.S, self.n
        Ftil = [self.Fh, self.Dh, self.Hh, self.Gh, [F(0)] * n, [F(0)] * n]  # F~^(k)(e0)
        # phi^(j) = S^(j) - (I - K) F~^(j) + sum_{i>=1} C(j,i) K_i F~^(j-i)
        out = vadd((F(1), S[j]), (F(-1), mv(I_minus(K[0]), Ftil[j])))
        for i in range(1, j + 1):
            out = vadd((F(1), out), (F(comb(j, i)), mv(K[i], Ftil[j - i])))
        return out

    # -- independent polynomial path: phi_x(t), t = e - e0, exact
    def phi_poly(self) -> list:
        if self._phi_poly is not None:
            return self._phi_poly
        n = self.n
        Ft = [[self.Fh[y], self.Dh[y], self.Hh[y] / 2, self.Gh[y] / 6] for y in range(n)]
        out = []
        for x in range(n):
            acc = p_add(p_taylor(self.sp[x], self.e0), Ft[x], F(-1))
            for y in range(n):
                acc = p_add(acc, p_mul(p_taylor(self.fam.kp[x][y], self.e0), Ft[y]))
            out.append(acc)
        self._phi_poly = out
        return out

    def phi_poly_deriv_at0(self, j: int) -> list:
        return [(c[j] if j < len(c) else F(0)) * factorial(j) for c in self.phi_poly()]

    def phi_poly_deriv_sup(self, j: int) -> tuple:
        """RIGOROUS (upper, lower) of sup_{|t|<=rho} ||phi^(j)(e0+t)|| (whole cell, composite)."""
        ub, lb = F(0), F(0)
        for c in self.phi_poly():
            u, l_ = sup_abs_on(p_deriv(c, j), -self.rho, self.rho)
            ub, lb = max(ub, u), max(lb, l_)
        return ub, lb

    # -- exact truth
    def Fpp_at_atom(self, t_abs: F) -> F:
        cache = self.__dict__.setdefault("_fpp_cache", {})
        if t_abs not in cache:
            guard_interval(t_abs, t_abs)
            cache[t_abs] = self.famr.F_derivs(t_abs, 2)[2][0]
        return cache[t_abs]


def tc_rad_poly(A: tuple, f: dict, variant: str = "TC") -> list:
    """rad(s) as a polynomial in s (low -> high), theorem TC section 3 with s in place of rho (Lemma TC-P).

    variant TC  : f = {F, D, H, G, Env4}
    variant TCp : order-raised TC+ with a MIDPOINT order-4 premise f4 and a whole-cell order-5 envelope Env5:
                  p2(s) = fH + s fG + s^2/2 f4 + s^3/6 Env5, and the lower p's by integration."""
    A0, A1, A2 = A
    p0, p1, p2 = tc_profile_polys(f, variant)
    return p_add(p_add(p_scale(p2, A0), p_scale(p1, 2 * A1)), p_scale(p0, A2))


def tc_profile_polys(f: dict, variant: str = "TC") -> tuple:
    """(p0, p1, p2) as polynomials in s (Lemma TC-P; TC+ for variant 'TCp')."""
    if variant == "TC":
        p2 = [f["H"], f["G"], f["Env4"] / 2]
        p1 = [f["D"], f["H"], f["G"] / 2, f["Env4"] / 6]
        p0 = [f["F"], f["D"], f["H"] / 2, f["G"] / 6, f["Env4"] / 24]
    elif variant == "TCp":
        p2 = [f["H"], f["G"], f["f4"] / 2, f["Env5"] / 6]
        p1 = [f["D"], f["H"], f["G"] / 2, f["f4"] / 6, f["Env5"] / 24]
        p0 = [f["F"], f["D"], f["H"] / 2, f["G"] / 6, f["f4"] / 24, f["Env5"] / 120]
    else:
        raise ValueError(variant)
    return p0, p1, p2


def lemma_g(k: list, C: F) -> tuple:
    return C, k[1] * C * C, k[2] * C * C + 2 * k[1] ** 2 * C ** 3


def perturbed(v: list, pert: F, rng: random.Random) -> list:
    return [x + pert * F(rng.randint(-100, 100), 100) for x in v]
