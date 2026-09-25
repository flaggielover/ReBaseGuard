"""C11RD -- rigorous multivariate Taylor models in exact fixed-point integer arithmetic.

A Taylor model (TM) of order N in n variables u = (u_1..u_n), each ranging over [-1, 1], is a pair
(P, R): a polynomial P(u) of total degree <= N with fixed-point coefficients and a remainder bound
R >= 0, meaning that the represented function f satisfies

    |f(u) - P(u)| <= R    for every u in [-1, 1]^n.

Coefficients are Python ints scaled by 2^-PREC ("ulps"). Every operation is EXACT integer
arithmetic except explicit roundings, and every rounding error is added to R, so the enclosure is
rigorous. Because every |u_i| <= 1, every monomial satisfies |u^a| <= 1, and a polynomial's range is
bounded by |c_0| + sum_{a != 0} |c_a|.

Elementary functions are composed through their Taylor series about the TM's constant term, with
the Lagrange remainder bounded by an interval bound of the (N+1)-st derivative on the range of the
argument. The Gaussian density and distribution function values at a POINT come from C7's rigorous
rational primitives (c7_gaussian: exact Fractions, proved series remainders, 2^-320 outward
rounding), the same primitives C11's independent certifier used; they are the only external code.

This module knows nothing about the CUSUM model, the cell, or any target value.
"""
from __future__ import annotations

import math
import pathlib
import sys
from fractions import Fraction as F
from functools import lru_cache

_C7 = pathlib.Path(__file__).resolve().parents[2] / "p5y_k5_tail_c7_e2_lambda309" / "code"
sys.path.insert(0, str(_C7))
import c7_gaussian as G  # noqa: E402  rigorous rational phi/Phi; imports only `fractions`

PREC = 160
ONE = 1 << PREC


class TMError(Exception):
    pass


# ---------------------------------------------------------------------------------------------
# fixed-point helpers (all rounding directions explicit)
# ---------------------------------------------------------------------------------------------
def fx_floor(x: F) -> int:
    """floor(x * 2^PREC)."""
    return (x.numerator << PREC) // x.denominator


def fx_ceil(x: F) -> int:
    return -((-x.numerator << PREC) // x.denominator)


def fx_round(x: F) -> tuple[int, int]:
    """Nearest-ish fixed point of x and a bound (in ulps) on the rounding error."""
    lo = fx_floor(x)
    return lo, (0 if F(lo, ONE) == x else 1)


def ulps_to_F(v: int) -> F:
    return F(v, ONE)


def shr_ceil_abs(v: int, bits: int) -> int:
    """ceil(|v| / 2^bits)."""
    v = abs(v)
    return -((-v) >> bits)


# ---------------------------------------------------------------------------------------------
# monomial bookkeeping
# ---------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def monomials(nvars: int, order: int) -> tuple:
    out = []

    def rec(prefix, left, k):
        if k == nvars:
            out.append(tuple(prefix))
            return
        for d in range(left + 1):
            rec(prefix + [d], left - d, k + 1)
    rec([], order, 0)
    out.sort(key=lambda a: (sum(a), a))
    return tuple(out)


def _add_exp(a, b):
    return tuple(x + y for x, y in zip(a, b))


class TM:
    __slots__ = ("n", "N", "c", "r")

    def __init__(self, nvars: int, order: int, coeffs: dict | None = None, rem: int = 0):
        self.n, self.N = nvars, order
        self.c = coeffs if coeffs is not None else {}
        self.r = rem
        if rem < 0:
            raise TMError("negative remainder")

    # ---- constructors ------------------------------------------------------------------------
    @classmethod
    def const(cls, nvars: int, order: int, x) -> "TM":
        """x: int, Fraction, or an interval (lo, hi) of Fractions."""
        if isinstance(x, tuple):
            lo, hi = F(x[0]), F(x[1])
            if hi < lo:
                raise TMError("inverted interval")
            mid = (lo + hi) / 2
            v, e = fx_round(mid)
            rad = fx_ceil((hi - lo) / 2)
            return cls(nvars, order, {(0,) * nvars: v} if v else {}, rad + e + 1)
        v, e = fx_round(F(x))
        return cls(nvars, order, {(0,) * nvars: v} if v else {}, e)

    @classmethod
    def var(cls, nvars: int, order: int, i: int, center, halfwidth) -> "TM":
        """center + halfwidth * u_i."""
        c0, e0 = fx_round(F(center))
        c1, e1 = fx_round(F(halfwidth))
        coeffs = {}
        if c0:
            coeffs[(0,) * nvars] = c0
        if c1:
            ex = [0] * nvars
            ex[i] = 1
            coeffs[tuple(ex)] = c1
        return cls(nvars, order, coeffs, e0 + e1)

    def zero_like(self) -> "TM":
        return TM(self.n, self.N, {}, 0)

    def copy(self) -> "TM":
        return TM(self.n, self.N, dict(self.c), self.r)

    # ---- inspection --------------------------------------------------------------------------
    def const_ulps(self) -> int:
        return self.c.get((0,) * self.n, 0)

    def poly_abs_nonconst(self) -> int:
        z = (0,) * self.n
        return sum(abs(v) for k, v in self.c.items() if k != z)

    def bound_ulps(self) -> int:
        """sup |f| <= this many ulps (crude but rigorous)."""
        return abs(self.const_ulps()) + self.poly_abs_nonconst() + self.r

    def interval(self) -> tuple[F, F]:
        c0 = self.const_ulps()
        w = self.poly_abs_nonconst() + self.r
        return F(c0 - w, ONE), F(c0 + w, ONE)

    def abs_upper(self) -> F:
        return F(self.bound_ulps(), ONE)

    # ---- arithmetic --------------------------------------------------------------------------
    def _chk(self, o):
        if not isinstance(o, TM) or o.n != self.n or o.N != self.N:
            raise TMError("TM shape mismatch")

    def __add__(self, o):
        if not isinstance(o, TM):
            return self + TM.const(self.n, self.N, o)
        self._chk(o)
        c = dict(self.c)
        for k, v in o.c.items():
            c[k] = c.get(k, 0) + v
        return TM(self.n, self.N, {k: v for k, v in c.items() if v}, self.r + o.r)

    __radd__ = __add__

    def __neg__(self):
        return TM(self.n, self.N, {k: -v for k, v in self.c.items()}, self.r)

    def __sub__(self, o):
        if not isinstance(o, TM):
            o = TM.const(self.n, self.N, o)
        return self + (-o)

    def __rsub__(self, o):
        return (-self) + o

    def scale(self, x) -> "TM":
        """Multiply by an exact rational x."""
        x = F(x)
        if x == 0:
            return self.zero_like()
        num, den = x.numerator, x.denominator
        c, err = {}, 0
        for k, v in self.c.items():
            t = v * num
            q = t // den
            if q * den != t:
                err += 1
            if q:
                c[k] = q
        rem = -((-self.r * abs(num)) // den) + err
        return TM(self.n, self.N, c, rem)

    def __mul__(self, o):
        if not isinstance(o, TM):
            if isinstance(o, tuple):
                return self * TM.const(self.n, self.N, o)
            return self.scale(o)
        self._chk(o)
        acc: dict = {}
        for ka, va in self.c.items():
            for kb, vb in o.c.items():
                k = _add_exp(ka, kb)
                acc[k] = acc.get(k, 0) + va * vb
        c, rem = {}, 0
        for k, v in acc.items():
            if sum(k) <= self.N:
                q = v >> PREC                     # floor
                if (q << PREC) != v:
                    rem += 1
                if q:
                    c[k] = q
            else:
                rem += shr_ceil_abs(v, PREC)
        # cross terms of the remainders, in ulps: (B(a) r_b + r_a B(b) + r_a r_b) / 2^PREC
        ba = abs(self.const_ulps()) + self.poly_abs_nonconst()
        bb = abs(o.const_ulps()) + o.poly_abs_nonconst()
        cross = ba * o.r + self.r * bb + self.r * o.r
        rem += shr_ceil_abs(cross, PREC)
        return TM(self.n, self.N, c, rem)

    __rmul__ = __mul__

    def pow(self, k: int) -> "TM":
        if k < 0:
            raise TMError("negative power")
        out = TM.const(self.n, self.N, 1)
        for _ in range(k):
            out = out * self
        return out

    def powers(self, kmax: int) -> list:
        out = [TM.const(self.n, self.N, 1)]
        for _ in range(kmax):
            out.append(out[-1] * self)
        return out

    def split_const(self) -> tuple[F, "TM"]:
        """(x0, X - x0) with x0 the exact dyadic constant coefficient."""
        z = (0,) * self.n
        x0 = F(self.c.get(z, 0), ONE)
        d = {k: v for k, v in self.c.items() if k != z}
        return x0, TM(self.n, self.N, d, self.r)


# ---------------------------------------------------------------------------------------------
# Hermite polynomials He_k (probabilists'): phi^(k)(y) = (-1)^k He_k(y) phi(y)
# ---------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def hermite(k: int) -> tuple:
    """Integer coefficients of He_k, lowest degree first."""
    if k == 0:
        return (1,)
    if k == 1:
        return (0, 1)
    a, b = [1], [0, 1]
    for n in range(1, k):
        c = [0] * (n + 2)
        for i, v in enumerate(b):
            c[i + 1] += v
        for i, v in enumerate(a):
            c[i] -= n * v
        a, b = b, c
    return tuple(b)


def poly_eval_F(coeffs, x: F) -> F:
    acc = F(0)
    for c in reversed(coeffs):
        acc = acc * x + c
    return acc


def poly_abs_sup(coeffs, R: F) -> F:
    """sup_{|x| <= R} |p(x)| <= sum |c_k| R^k."""
    return sum(abs(F(c)) * R ** k for k, c in enumerate(coeffs))


# ---------------------------------------------------------------------------------------------
# rigorous point values of phi, Phi (C7), cached on exact dyadic arguments
# ---------------------------------------------------------------------------------------------
@lru_cache(maxsize=200000)
def phi_point(x: F) -> tuple[F, F]:
    v = G.phi(x)
    return v.lo, v.hi


@lru_cache(maxsize=200000)
def Phi_point(x: F) -> tuple[F, F]:
    v = G.Phi(x)
    return v.lo, v.hi


PHI0_UPPER = phi_point(F(0))[1]


def phi_sup_on(lo: F, hi: F) -> F:
    """sup of phi on [lo, hi] (phi is unimodal at 0)."""
    if lo <= 0 <= hi:
        return PHI0_UPPER
    x = lo if lo > 0 else hi
    return phi_point(_dyadic_toward_zero(x))[1]


def _dyadic_toward_zero(x: F, bits: int = 40) -> F:
    """A dyadic number between 0 and x (inclusive of x's side), so phi there bounds phi(x) above."""
    s = 1 if x > 0 else -1
    a = abs(x)
    d = F(math.floor(a * (1 << bits)), 1 << bits)
    return s * d


def _interval_mid_rad(lo: F, hi: F) -> tuple[F, F]:
    return (lo + hi) / 2, (hi - lo) / 2


def compose(X: TM, derivs_over_fact: list, sup_next_deriv: F) -> TM:
    """g(X) for an analytic g, given enclosures of g^(j)(x0)/j! (j = 0..N) as (lo, hi) pairs at the
    exact constant x0 of X, and an upper bound of |g^(N+1)| on the range of X. Lagrange remainder:
    sup|g^(N+1)| r^(N+1) / (N+1)!."""
    n, N = X.n, X.N
    if len(derivs_over_fact) != N + 1:
        raise TMError("need N + 1 derivative enclosures")
    x0, dX = X.split_const()
    r = F(dX.bound_ulps(), ONE)
    out = TM(n, N, {}, 0)
    powk = TM.const(n, N, 1)
    rk = F(1)
    for j in range(N + 1):
        lo, hi = derivs_over_fact[j]
        mid, rad = _interval_mid_rad(F(lo), F(hi))
        term = powk.scale(mid)
        term.r += fx_ceil(rad * rk) + 1
        out = out + term
        if j < N:
            powk = powk * dX
            rk = rk * r
    out.r += fx_ceil(sup_next_deriv * r ** (N + 1) / math.factorial(N + 1)) + 1
    return out


def phi_tm(X: TM) -> TM:
    """phi(X). phi^(j)(x) = (-1)^j He_j(x) phi(x)."""
    N = X.N
    x0, dX = X.split_const()
    r = F(dX.bound_ulps(), ONE)
    plo, phi_hi = phi_point(x0)
    ders = []
    for j in range(N + 1):
        h = poly_eval_F(hermite(j), x0) * (-1) ** j / math.factorial(j)
        a, b = sorted((h * plo, h * phi_hi))
        ders.append((a, b))
    sup_he = poly_abs_sup(hermite(N + 1), abs(x0) + r)
    M = sup_he * phi_sup_on(x0 - r, x0 + r)
    return compose(X, ders, M)


def Phi_tm(X: TM) -> TM:
    """Phi(X). Phi^(j) = phi^(j-1) for j >= 1."""
    N = X.N
    x0, dX = X.split_const()
    r = F(dX.bound_ulps(), ONE)
    plo, phi_hi = phi_point(x0)
    Plo, Phi_hi = Phi_point(x0)
    ders = [(Plo, Phi_hi)]
    for j in range(1, N + 1):
        h = poly_eval_F(hermite(j - 1), x0) * (-1) ** (j - 1) / math.factorial(j)
        a, b = sorted((h * plo, h * phi_hi))
        ders.append((a, b))
    sup_he = poly_abs_sup(hermite(N), abs(x0) + r)
    M = sup_he * phi_sup_on(x0 - r, x0 + r)
    return compose(X, ders, M)


# ---------------------------------------------------------------------------------------------
# the one integral primitive: I_k = int_{A}^{B} v^k phi(yc + v) dv for TM endpoints A, B (already
# centred: A = alpha - yc, B = beta - yc, both small), by the Taylor series of phi about yc
# ---------------------------------------------------------------------------------------------
def centred_moments(yc: F, A: TM, B: TM, kmax: int, J: int) -> list:
    """[I_0..I_kmax], I_k = int_A^B v^k phi(yc + v) dv, with
    phi(yc + v) = sum_{j<=J} phi^(j)(yc)/j! v^j + R_J(v),  |R_J| <= sup|phi^(J+1)| |v|^(J+1)/(J+1)!.
    Hence I_k = sum_j c_j (B^(k+j+1) - A^(k+j+1)) / (k+j+1) + E_k,
    |E_k| <= sup|phi^(J+1)| / (J+1)! * |B - A| * rho^(k+J+1), rho = max|v| on [A, B]."""
    n, N = A.n, A.N
    plo, phi_hi = phi_point(yc)
    cj = []
    for j in range(J + 1):
        h = poly_eval_F(hermite(j), yc) * (-1) ** j / math.factorial(j)
        cj.append(tuple(sorted((h * plo, h * phi_hi))))
    top = kmax + J + 1
    PA, PB = A.powers(top), B.powers(top)
    rho = max(A.abs_upper(), B.abs_upper())
    width = (B - A).abs_upper()
    sup_he = poly_abs_sup(hermite(J + 1), abs(yc) + rho)
    Mj = sup_he * phi_sup_on(yc - rho, yc + rho) / math.factorial(J + 1)
    out = []
    for k in range(kmax + 1):
        acc = TM(n, N, {}, 0)
        for j in range(J + 1):
            q = k + j + 1
            diff = PB[q] - PA[q]
            lo, hi = cj[j]
            mid, rad = _interval_mid_rad(F(lo), F(hi))
            t = diff.scale(mid / q)
            t.r += fx_ceil(rad * diff.abs_upper() / q) + 1
            acc = acc + t
        acc.r += fx_ceil(Mj * width * rho ** (k + J + 1)) + 1
        out.append(acc)
    return out
