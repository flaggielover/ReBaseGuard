"""Stream D: independent rigorous verifier of whole-kernel ARL supersolution certificates.

Claim verified:  W >= 0 and  W(x) >= 1 + (K_e W)(x)  for every x in
    R = {0 <= p, m <= 5 : p = 0 or m = 0 or p + m <= 4},
    (K_e f)(x) = int_{m-C}^{C-p} f(T(x,z)) phi(z+e) dz,  T(x,z) = ((p+z-K)^+, (m-z-K)^+),  K = 1/2, C = 11/2.
Then E_x[tau] <= W(x); in particular Lambda(e) = E_a[tau] <= W(a), a = (0,0).

Derived from the mathematics only (THEOREM_AD Lemma K and section 4; THEOREM_RLR307 section 0).  This module imports
no certifier module (no c1b_*, c2b_*, c7_gaussian, ...): only the stdlib and the campaign quarantine module.

Method (all load-bearing arithmetic is exact-rational with outward rounding):
  * numbers are dyadic rationals n / 2^PREC held as Python ints; every operation rounds its lower end down and its
    upper end up, so every interval is a rigorous enclosure; the final comparisons are exact integer (= rational)
    comparisons, reported as fractions.Fraction.
  * phi(u) = exp(-u^2/2)/sqrt(2 pi):  exp by integer/fraction split, e^{-1} powers, alternating Taylor series with its
    remainder bound; pi by Machin's formula (alternating series bounds); sqrt by integer isqrt with directed rounding.
  * Phi(u) = 1/2 + sign(u) phi(|u|) S(|u|),  S(v) = sum_{n>=0} v^{2n+1}/(2n+1)!!  (positive series; geometric tail bound).
  * K_e W(x) is split, for x in a t-region (t = p+m; regions are cut at the strip boundaries b and at b+1), into
    pieces on which T(x, .) is affine and W is one polynomial: A (p' = 0, on the m-axis), B (both arms positive,
    t' = t-1), C (m' = 0), and for t <= 1 the atom window [m-K, K-p] with mass W(a) (Phi(K-p+e) - Phi(m-K+e)).
    With u = z + e each piece is sum_n q_n int_{u0}^{u1} u^n phi(u) du, moments by the recurrence
    M_0 = Phi(u1)-Phi(u0), M_1 = phi(u0)-phi(u1), M_n = (n-1) M_{n-2} + u0^{n-1}phi(u0) - u1^{n-1}phi(u1).
  * Branch and bound over R: 2-D boxes cover {t <= 4} (inside [0,4]^2), 1-D segments cover the axis parts t in [4,5].
    On a box, for every t-region the box meets, the residual's analytic region formula F_J is bounded below by the
    larger of the mean-value form  F_J(c) - sum_i max|dF_J/dx_i(box)| r_i  and the second-order Taylor form
    F_J(c) - sum_i |dF_J/dx_i(c)| r_i - (1/2) sum_ij max|d2F_J/dx_i dx_j(box)| r_i r_j  (value and gradient at the
    centre c with thin intervals; gradient and Hessian enclosures over the whole box by forward-mode interval automatic
    differentiation of order 2).  A box is certified when the minimum over its regions is >= 0; if the centre lies in
    R and the residual there (its own region) has an upper bound < 0, the centre is a rigorous refutation witness
    (the run stops at the first witness); otherwise the box is bisected.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import time
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]


def _load_quarantine():
    spec = importlib.util.spec_from_file_location("c308_quarantine", NS / "code" / "c308_quarantine.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


Q = _load_quarantine()
Q.install_import_guard()

KQ = F(1, 2)      # reference value K
HQ = F(5)         # decision interval H
CQ = KQ + HQ      # C = 11/2
TMAX2D = F(4)     # 2-D part of R: p + m <= 4
TOP = F(5)

# ============================================================================================ interval arithmetic
PREC = 128
ONE = 1 << PREC
GUARD = 64
QP = PREC + GUARD           # internal precision of the special functions
QONE = 1 << QP


def ifr(x) -> tuple:
    """Fraction -> enclosing dyadic interval (lo, hi) at PREC bits."""
    x = F(x)
    n, d = x.numerator, x.denominator
    return ((n << PREC) // d, -((-n << PREC) // d))


def ifr_pair(lo, hi) -> tuple:
    return (ifr(lo)[0], ifr(hi)[1])


def to_frac_lo(a: tuple) -> F:
    return F(a[0], ONE)


def to_frac_hi(a: tuple) -> F:
    return F(a[1], ONE)


def iadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def isub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def ineg(a):
    return (-a[1], -a[0])


def imul(a, b):
    a0, a1 = a
    b0, b1 = b
    if a0 >= 0 and b0 >= 0:
        lo, hi = a0 * b0, a1 * b1
    elif a1 <= 0 and b1 <= 0:
        lo, hi = a1 * b1, a0 * b0
    else:
        x0, x1, x2, x3 = a0 * b0, a0 * b1, a1 * b0, a1 * b1
        lo = min(x0, x1, x2, x3)
        hi = max(x0, x1, x2, x3)
    return (lo >> PREC, -((-hi) >> PREC))


def imulint(a, k: int):
    return (a[0] * k, a[1] * k) if k >= 0 else (a[1] * k, a[0] * k)


def imaxabs(a) -> int:
    return max(-a[0], a[1], 0)


ZERO_I = (0, 0)
ONE_I = (ONE, ONE)

# ============================================================================================ constants (pi, 1/sqrt(2 pi))


def _atan_inv_bounds(k: int, terms: int) -> tuple:
    """arctan(1/k) enclosure from the alternating series (terms strictly decreasing)."""
    s = F(0)
    for n in range(terms):
        s += F((-1) ** n, (2 * n + 1) * k ** (2 * n + 1))
    nxt = F(1, (2 * terms + 1) * k ** (2 * terms + 1))
    return (s - nxt, s + nxt)


def _pi_bounds() -> tuple:
    a5 = _atan_inv_bounds(5, 70)
    a239 = _atan_inv_bounds(239, 30)
    lo = 16 * a5[0] - 4 * a239[1]
    hi = 16 * a5[1] - 4 * a239[0]
    return lo, hi


PI_LO, PI_HI = _pi_bounds()
assert F(314159265358979, 10 ** 14) < PI_LO < PI_HI < F(314159265358980, 10 ** 14)
assert PI_HI - PI_LO < F(1, 2 ** 300)


def _inv_sqrt_2pi_q() -> tuple:
    """1/sqrt(2 pi) at QP bits: lo = isqrt(floor(2^{2QP}/(2 pi_hi))), hi = isqrt(ceil(2^{2QP}/(2 pi_lo))) + 1."""
    xlo = F(1 << (2 * QP)) / (2 * PI_HI)
    xhi = F(1 << (2 * QP)) / (2 * PI_LO)
    lo = math.isqrt(xlo.numerator // xlo.denominator)
    hi = math.isqrt(-((-xhi.numerator) // xhi.denominator)) + 1
    return lo, hi


ISQ2PI_Q = _inv_sqrt_2pi_q()


def _expneg_frac_q(g: int) -> tuple:
    """exp(-g / 2^QP) for 0 <= g <= 2^QP at QP bits: alternating Taylor series with directed-rounded terms."""
    tlo = thi = QONE
    slo = shi = QONE
    k = 0
    while True:
        k += 1
        den = k << QP
        tlo = (tlo * g) // den
        thi = -((-(thi * g)) // den)
        if k % 2:
            slo -= thi
            shi -= tlo
        else:
            slo += tlo
            shi += thi
        if thi <= 1 and k >= 2:
            break
    # next term bound: T_{k+1} <= T_k (terms decrease since g <= 1, k >= 1) -> tail enclosed by +-thi
    return (slo - thi - 1, shi + thi + 1)


E1_Q = _expneg_frac_q(QONE)            # e^{-1}
assert E1_Q[0] < E1_Q[1] and 0.3678794 < E1_Q[0] / QONE <= E1_Q[1] / QONE < 0.3678795


@lru_cache(maxsize=None)
def _epow_q(n: int) -> tuple:
    """e^{-n} at QP bits (directed products of the e^{-1} enclosure)."""
    if n == 0:
        return (QONE, QONE)
    a = _epow_q(n - 1)
    return ((a[0] * E1_Q[0]) >> QP, -((-(a[1] * E1_Q[1])) >> QP))


@lru_cache(maxsize=1 << 18)
def phi_q(x: int) -> tuple:
    """phi(x / 2^PREC) enclosure at QP bits; x an int (a PREC-bit dyadic)."""
    num = x * x                       # u^2 = num / 2^(2 PREC); y = u^2/2 = num / 2^(2 PREC + 1)
    sh = 2 * PREC + 1
    n = num >> sh
    f_num = num - (n << sh)           # f = f_num / 2^sh in [0, 1)
    if sh >= QP:
        glo = f_num >> (sh - QP)
        ghi = -((-f_num) >> (sh - QP))
    else:
        glo = ghi = f_num << (QP - sh)
    ex_lo = _expneg_frac_q(ghi)[0]    # exp(-f) decreasing in f
    ex_hi = _expneg_frac_q(glo)[1]
    en = _epow_q(n)
    lo = (((ex_lo * en[0]) >> QP) * ISQ2PI_Q[0]) >> QP
    hi = -((-(-((-(ex_hi * en[1])) >> QP) * ISQ2PI_Q[1])) >> QP)
    return (max(lo, 0), hi)


def _S_series_q(v: int) -> tuple:
    """S(v) = sum_{n>=0} v^{2n+1}/(2n+1)!!, v = v_int / 2^QP >= 0, at QP bits (lower/upper)."""
    v2lo = (v * v) >> QP
    v2hi = -((-(v * v)) >> QP)
    tlo = thi = v
    slo = shi = v
    n = 0
    while True:
        n += 1
        den = (2 * n + 1) << QP
        tlo = (tlo * v2lo) // den
        thi = -((-(thi * v2hi)) // den)
        slo += tlo
        shi += thi
        # ratio of the next terms: v^2/(2n+3) <= 1/2  ->  tail <= T_n
        if thi <= 1 and 2 * v2hi <= (2 * n + 3) << QP:
            break
    return (slo, shi + thi + 1)


@lru_cache(maxsize=1 << 18)
def Phi_point(x: int) -> tuple:
    """Phi(x / 2^PREC) enclosure at PREC bits."""
    v = abs(x) << GUARD
    ph = phi_q(abs(x))
    s = _S_series_q(v)
    plo = (ph[0] * s[0]) >> QP
    phi_ = -((-(ph[1] * s[1])) >> QP)
    half = QONE >> 1
    if x >= 0:
        lo, hi = half + plo, half + phi_
    else:
        lo, hi = half - phi_, half - plo
    lo = max(lo, 0)
    hi = min(hi, QONE)
    return (lo >> GUARD, -((-hi) >> GUARD))


@lru_cache(maxsize=1 << 18)
def phi_point(x: int) -> tuple:
    a = phi_q(x)
    return (a[0] >> GUARD, -((-a[1]) >> GUARD))


def phi_iv(u: tuple) -> tuple:
    lo, hi = u
    if lo <= 0 <= hi:
        top = phi_point(0)[1]
        return (min(phi_point(lo)[0], phi_point(hi)[0]), top)
    if lo > 0:
        return (phi_point(hi)[0], phi_point(lo)[1])
    return (phi_point(lo)[0], phi_point(hi)[1])


def Phi_iv(u: tuple) -> tuple:
    return (Phi_point(u[0])[0], Phi_point(u[1])[1])


# ============================================================================================ forward-mode interval AD
class D:
    """value interval v; gradient intervals (gp, gm) w.r.t. (p, m) or None (value mode); Hessian intervals
    (hpp, hpm, hmm) or None (first-order mode).  Every field is a rigorous enclosure over the input set."""
    __slots__ = ("v", "gp", "gm", "hpp", "hpm", "hmm")

    def __init__(self, v, gp=None, gm=None, hpp=None, hpm=None, hmm=None):
        self.v, self.gp, self.gm, self.hpp, self.hpm, self.hmm = v, gp, gm, hpp, hpm, hmm


def dconst(c: tuple) -> D:
    return D(c)


def _cscale(c: tuple, b: D, v) -> D:
    """c * b for an interval constant c (no derivatives)."""
    if b.gp is None:
        return D(v)
    if b.hpp is None:
        return D(v, imul(c, b.gp), imul(c, b.gm))
    return D(v, imul(c, b.gp), imul(c, b.gm), imul(c, b.hpp), imul(c, b.hpm), imul(c, b.hmm))


def dadd(a: D, b: D) -> D:
    v = iadd(a.v, b.v)
    if a.gp is None:
        return D(v) if b.gp is None else D(v, b.gp, b.gm, b.hpp, b.hpm, b.hmm)
    if b.gp is None:
        return D(v, a.gp, a.gm, a.hpp, a.hpm, a.hmm)
    if a.hpp is None or b.hpp is None:
        if a.hpp is not None or b.hpp is not None:
            raise ValueError("mixed first/second order operands")
        return D(v, iadd(a.gp, b.gp), iadd(a.gm, b.gm))
    return D(v, iadd(a.gp, b.gp), iadd(a.gm, b.gm), iadd(a.hpp, b.hpp), iadd(a.hpm, b.hpm), iadd(a.hmm, b.hmm))


def dneg(a: D) -> D:
    if a.gp is None:
        return D(ineg(a.v))
    if a.hpp is None:
        return D(ineg(a.v), ineg(a.gp), ineg(a.gm))
    return D(ineg(a.v), ineg(a.gp), ineg(a.gm), ineg(a.hpp), ineg(a.hpm), ineg(a.hmm))


def dsub(a: D, b: D) -> D:
    return dadd(a, dneg(b))


def daddc(a: D, c: tuple) -> D:
    return D(iadd(a.v, c), a.gp, a.gm, a.hpp, a.hpm, a.hmm)


def dmul(a: D, b: D) -> D:
    v = imul(a.v, b.v)
    if a.gp is None:
        return _cscale(a.v, b, v)
    if b.gp is None:
        return _cscale(b.v, a, v)
    gp = iadd(imul(a.v, b.gp), imul(a.gp, b.v))
    gm = iadd(imul(a.v, b.gm), imul(a.gm, b.v))
    if a.hpp is None or b.hpp is None:
        if a.hpp is not None or b.hpp is not None:
            raise ValueError("mixed first/second order operands")
        return D(v, gp, gm)
    hpp = iadd(iadd(imul(a.v, b.hpp), imul(a.hpp, b.v)), imulint(imul(a.gp, b.gp), 2))
    hpm = iadd(iadd(imul(a.v, b.hpm), imul(a.hpm, b.v)), iadd(imul(a.gp, b.gm), imul(a.gm, b.gp)))
    hmm = iadd(iadd(imul(a.v, b.hmm), imul(a.hmm, b.v)), imulint(imul(a.gm, b.gm), 2))
    return D(v, gp, gm, hpp, hpm, hmm)


def dmulc(a: D, c: tuple) -> D:
    return _cscale(c, a, imul(a.v, c))


def dmulint(a: D, k: int) -> D:
    if a.gp is None:
        return D(imulint(a.v, k))
    if a.hpp is None:
        return D(imulint(a.v, k), imulint(a.gp, k), imulint(a.gm, k))
    return D(imulint(a.v, k), imulint(a.gp, k), imulint(a.gm, k), imulint(a.hpp, k), imulint(a.hpm, k),
             imulint(a.hmm, k))


def _chain(u: D, f: tuple, f1: tuple, f2_fn) -> D:
    """g(u) with enclosures f of g(U), f1 of g'(U) and (lazily) f2 of g''(U) over the range U of u."""
    if u.gp is None:
        return D(f)
    gp, gm = imul(f1, u.gp), imul(f1, u.gm)
    if u.hpp is None:
        return D(f, gp, gm)
    f2 = f2_fn()
    hpp = iadd(imul(f2, imul(u.gp, u.gp)), imul(f1, u.hpp))
    hpm = iadd(imul(f2, imul(u.gp, u.gm)), imul(f1, u.hpm))
    hmm = iadd(imul(f2, imul(u.gm, u.gm)), imul(f1, u.hmm))
    return D(f, gp, gm, hpp, hpm, hmm)


def dphi(u: D) -> D:
    f = phi_iv(u.v)
    if u.gp is None:
        return D(f)
    f1 = ineg(imul(u.v, f))                                            # phi' = -u phi
    return _chain(u, f, f1, lambda: imul(isub(imul(u.v, u.v), ONE_I), f))   # phi'' = (u^2 - 1) phi


def dPhi(u: D) -> D:
    f = Phi_iv(u.v)
    if u.gp is None:
        return D(f)
    g = phi_iv(u.v)                                                    # Phi' = phi
    return _chain(u, f, g, lambda: ineg(imul(u.v, g)))                 # Phi'' = -u phi


# ============================================================================================ certificate object
def _binom(n, k):
    return math.comb(n, k)


class StripPW:
    """W(p, m) = sum c_ij p^i m^j of strip s; strip s = right-closed [BW[s-1], BW[s]] of t = p + m (strip 1 closed)."""

    def __init__(self, BW, polys, meta=None):
        self.BW = tuple(F(b) for b in BW)
        assert self.BW[0] == 0 and self.BW[-1] == TOP and all(x < y for x, y in zip(self.BW, self.BW[1:]))
        self.polys = [{(int(i), int(j)): F(c) for (i, j), c in P.items() if F(c) != 0} for P in polys]
        assert len(self.polys) == len(self.BW) - 1
        self.meta = meta or {}

    def strip_of_t(self, t: F) -> int:
        """0-based strip index of t (right-closed strips, the first closed at 0)."""
        for s in range(1, len(self.BW)):
            if t <= self.BW[s]:
                return s - 1
        raise ValueError("t outside [0, 5]")

    def value(self, p, m) -> F:
        p, m = F(p), F(m)
        P = self.polys[self.strip_of_t(p + m)]
        return sum((c * p ** i * m ** j for (i, j), c in P.items()), F(0))

    def at_atom(self) -> F:
        return self.polys[0].get((0, 0), F(0))

    def scaled(self, s) -> "StripPW":
        s = F(s)
        return StripPW(self.BW, [{k: c * s for k, c in P.items()} for P in self.polys], dict(self.meta))

    def to_json(self) -> dict:
        return {"format": "VD_STRIP_PW/1", "BW": [f"{b.numerator}/{b.denominator}" for b in self.BW],
                "strips": [[[i, j, f"{c.numerator}/{c.denominator}"] for (i, j), c in sorted(P.items())]
                           for P in self.polys]}

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.to_json(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    @staticmethod
    def from_json(obj: dict) -> "StripPW":
        polys = [{(i, j): F(c) for i, j, c in mons} for mons in obj["strips"]]
        return StripPW([F(b) for b in obj["BW"]], polys, {k: obj[k] for k in obj if k not in ("strips",)})


# ============================================================================================ preparation
def _poly_uni_axis(P: dict, which: str) -> list:
    """P(0, y) (which='A') or P(y, 0) (which='C') as a coefficient list in y."""
    deg = max([i + j for (i, j) in P] + [0])
    out = [F(0)] * (deg + 1)
    for (i, j), c in P.items():
        if which == "A" and i == 0:
            out[j] += c
        elif which == "C" and j == 0:
            out[i] += c
    return out


def _poly_on_line(P: dict) -> list:
    """P(y, S - y) = sum_k y^k R_k(S); returns [R_0, ..., R_deg], each a coefficient list in S."""
    deg = max([i + j for (i, j) in P] + [0])
    R = [[F(0)] * (deg + 1) for _ in range(deg + 1)]
    for (i, j), c in P.items():
        for l_ in range(j + 1):
            R[i + l_][j - l_] += c * _binom(j, l_) * (-1) ** l_
    return R


def _poly_2d(P: dict) -> list:
    """P as [coeff list in m for p^0, p^1, ...] (nested Horner)."""
    deg = max([i + j for (i, j) in P] + [0])
    out = [[F(0)] * (deg + 1) for _ in range(deg + 1)]
    for (i, j), c in P.items():
        out[i][j] += c
    return out


class Region:
    __slots__ = ("r0", "r1", "low", "sW", "sB", "A", "Cp")


class Prep:
    def __init__(self, W: StripPW, e: F, omit_atom: bool = False):
        Q.guard_drift(e)
        self.e = F(e)
        self.omit_atom = omit_atom
        self.W = W
        self.BW = W.BW
        iv = lambda lst: [ifr(c) for c in lst]
        self.P2 = [[iv(row) for row in _poly_2d(P)] for P in W.polys]
        self.PA = [iv(_poly_uni_axis(P, "A")) for P in W.polys]
        self.PC = [iv(_poly_uni_axis(P, "C")) for P in W.polys]
        self.PB = [[iv(R) for R in _poly_on_line(P)] for P in W.polys]
        self.Wa = ifr(W.at_atom())
        e_ = self.e
        self.c_ap = ifr(-KQ - e_)       # a_p = p - K - e
        self.c_am = ifr(e_ - KQ)        # a_m = m - K + e
        self.c_uL = ifr(e_ - CQ)        # uL = m - C + e
        self.c_uH = ifr(CQ + e_)        # uH = C - p + e
        self.c_m1 = ifr(F(-1))
        bps = {F(0), TOP, F(1)} | set(self.BW) | {b + 1 for b in self.BW if b + 1 < TOP}
        bps = sorted(b for b in bps if 0 <= b <= TOP)
        self.regions = []
        for r0, r1 in zip(bps, bps[1:]):
            R = Region()
            R.r0, R.r1 = r0, r1
            R.low = r1 <= 1
            R.sW = self._strip_containing(r0, r1)
            R.sB = None if R.low else self._strip_containing(r0 - 1, r1 - 1)
            inner = [b for b in self.BW if 0 < b < TOP and b >= r1 - 1]
            ups = inner + [TOP]
            R.A = [(b, list(self.BW).index(b) - 1) for b in ups]     # (upper image coordinate, 0-based strip)
            R.Cp = list(R.A)
            self.regions.append(R)

    def _strip_containing(self, lo, hi) -> int:
        for s in range(1, len(self.BW)):
            if self.BW[s - 1] <= lo and hi <= self.BW[s]:
                return s - 1
        raise ValueError(f"({lo}, {hi}] not inside one strip")

    def region_of_t(self, t: F) -> Region:
        for R in self.regions:
            if t <= R.r1:
                return R
        raise ValueError("t > 5")

    def regions_meeting(self, tlo: F, thi: F) -> list:
        return [R for R in self.regions if R.r0 <= thi and tlo <= R.r1]


# ============================================================================================ residual formulas
def _horner(coefs: list, x: D) -> D:
    acc = dconst(coefs[-1])
    for c in reversed(coefs[:-1]):
        acc = daddc(dmul(acc, x), c)
    return acc


def _horner_D(coefs: list, x: D) -> D:
    acc = coefs[-1]
    for c in reversed(coefs[:-1]):
        acc = dadd(dmul(acc, x), c)
    return acc


def _taylor_shift(coefs: list, a: D) -> list:
    """coefficients (in w) of P(a + w), P given by constant-interval or D coefficients."""
    c = [x if isinstance(x, D) else dconst(x) for x in coefs]
    d = len(c) - 1
    for i in range(d):
        for k in range(d - 1, i - 1, -1):
            c[k] = dadd(c[k], dmul(a, c[k + 1]))
    return c


def _eval2(rows: list, p: D, m: D) -> D:
    return _horner_D([_horner(row, m) for row in rows], p)


class EP:
    """an integration endpoint u with phi(u), Phi(u) and cached u^k phi(u)."""
    __slots__ = ("u", "ph", "Ph", "E")

    def __init__(self, u: D):
        self.u = u
        self.ph = dphi(u)
        self.Ph = dPhi(u)
        self.E = [self.ph]

    def Ek(self, k: int) -> D:
        while len(self.E) <= k:
            self.E.append(dmul(self.E[-1], self.u))
        return self.E[k]


def _piece(q: list, e0: EP, e1: EP) -> D:
    """sum_n q_n int_{u0}^{u1} u^n phi(u) du (moment recurrence)."""
    n_max = len(q) - 1
    M = [dsub(e1.Ph, e0.Ph)]
    if n_max >= 1:
        M.append(dsub(e0.Ek(0), e1.Ek(0)))
    for n in range(2, n_max + 1):
        M.append(dadd(dmulint(M[n - 2], n - 1), dsub(e0.Ek(n - 1), e1.Ek(n - 1))))
    acc = dmul(q[0], M[0])
    for n in range(1, n_max + 1):
        acc = dadd(acc, dmul(q[n], M[n]))
    return acc


def residual_region(pre: Prep, R: Region, p: D, m: D) -> D:
    """analytic formula of W - 1 - K_e W valid for t = p + m in region R (extended analytically to any (p, m))."""
    a_p = daddc(p, pre.c_ap)
    a_m = daddc(m, pre.c_am)
    uL = EP(daddc(m, pre.c_uL))
    uH = EP(daddc(dneg(p), pre.c_uH))
    uA = EP(dneg(a_p))           # z = K - p   (p-arm clips below)
    uM = EP(a_m)                 # z = m - K   (m-arm clips above)
    Wx = _eval2(pre.P2[R.sW], p, m)
    KW = None
    shiftA, shiftC = {}, {}
    # ---- A: image (0, m'), m' = a_m - u, from m'_low (u = uM if low else uA) up to 5 (u = uL)
    hi_ep = uM if R.low else uA
    for (b, s) in R.A:
        lo_ep = uL if b == TOP else EP(daddc(a_m, ifr(-b)))
        if s not in shiftA:
            sh = _taylor_shift(pre.PA[s], a_m)                   # P(a_m + w); u = -w
            shiftA[s] = [c if k % 2 == 0 else dneg(c) for k, c in enumerate(sh)]
        term = _piece(shiftA[s], lo_ep, hi_ep)
        KW = term if KW is None else dadd(KW, term)
        hi_ep = lo_ep
    # ---- C: image (p', 0), p' = a_p + u, from p'_low (u = uA if low else uM) up to 5 (u = uH)
    lo_ep = uA if R.low else uM
    for (b, s) in R.Cp:
        hi_ep2 = uH if b == TOP else EP(daddc(dneg(a_p), ifr(b)))
        if s not in shiftC:
            shiftC[s] = _taylor_shift(pre.PC[s], a_p)
        KW = dadd(KW, _piece(shiftC[s], lo_ep, hi_ep2))
        lo_ep = hi_ep2
    # ---- atom window (t <= 1) or B piece (t >= 1)
    if R.low:
        if not pre.omit_atom:
            KW = dadd(KW, dmulc(dsub(uA.Ph, uM.Ph), pre.Wa))
    else:
        S = daddc(dadd(p, m), pre.c_m1)                          # t' = t - 1
        coefs = [_horner(Rk, S) for Rk in pre.PB[R.sB]]          # P(y, S - y) = sum y^k R_k(S)
        qB = _taylor_shift(coefs, a_p)                           # y = a_p + u
        KW = dadd(KW, _piece(qB, uA, uM))
    return daddc(dsub(Wx, KW), ineg(ONE_I))


def W_region(pre: Prep, R: Region, p: D, m: D) -> D:
    return _eval2(pre.P2[R.sW], p, m)


# ============================================================================================ point evaluation
def residual_point(pre: Prep, p: F, m: F) -> tuple:
    """rigorous enclosure (Fractions) of W(x) - 1 - (K_e W)(x) at an exact point x in R (its own region)."""
    p, m = F(p), F(m)
    R = pre.region_of_t(p + m)
    r = residual_region(pre, R, D(ifr(p)), D(ifr(m))).v
    return to_frac_lo(r), to_frac_hi(r)


def KW_point(pre: Prep, p: F, m: F) -> tuple:
    lo, hi = residual_point(pre, p, m)
    w = pre.W.value(p, m)
    return (w - 1 - hi, w - 1 - lo)


# ============================================================================================ branch and bound
def in_R(p: F, m: F) -> bool:
    return 0 <= p <= TOP and 0 <= m <= TOP and (p == 0 or m == 0 or p + m <= TMAX2D)


def _box_bound(pre: Prep, box, fn, order: int = 2) -> int:
    """rigorous lower bound (PREC-bit integer) of fn over box cap R, minimum over the t-regions the box meets.
    order 1: mean-value form  f(c) - sum_i max|df/dx_i(box)| r_i.
    order 2: additionally the Taylor form  f(c) - sum_i |df/dx_i(c)| r_i - (1/2) sum_ij max|H_ij(box)| r_i r_j;
             the larger of the two (both valid) is used."""
    p0, p1, m0, m1 = box
    pc, mc = (p0 + p1) / 2, (m0 + m1) / 2
    rp, rm = (p1 - p0) / 2, (m1 - m0) / 2
    tlo = p0 + m0
    thi = p1 + m1
    if p1 > p0 and m1 > m0:
        thi = min(thi, TMAX2D)
    regs = pre.regions_meeting(tlo, thi)
    rpi, rmi = ifr(rp)[1], ifr(rm)[1]
    if order == 1:
        pC, mC = D(ifr(pc)), D(ifr(mc))
        pX = D(ifr_pair(p0, p1), ONE_I, ZERO_I)
        mX = D(ifr_pair(m0, m1), ZERO_I, ONE_I)
    else:
        pC, mC = D(ifr(pc), ONE_I, ZERO_I), D(ifr(mc), ZERO_I, ONE_I)
        pX = D(ifr_pair(p0, p1), ONE_I, ZERO_I, ZERO_I, ZERO_I, ZERO_I)
        mX = D(ifr_pair(m0, m1), ZERO_I, ONE_I, ZERO_I, ZERO_I, ZERO_I)
    lb = None
    for R in regs:
        fc = fn(pre, R, pC, mC)
        fx = fn(pre, R, pX, mX)
        spread1 = -((-(imaxabs(fx.gp) * rpi + imaxabs(fx.gm) * rmi)) >> PREC)
        b = fc.v[0] - spread1
        if order != 1:
            lin = -((-(imaxabs(fc.gp) * rpi + imaxabs(fc.gm) * rmi)) >> PREC)
            q = (imaxabs(fx.hpp) * rpi * rpi + 2 * imaxabs(fx.hpm) * rpi * rmi + imaxabs(fx.hmm) * rmi * rmi)
            quad = -((-q) >> (2 * PREC + 1))                     # ceil(q / (2 * ONE^2))
            b = max(b, fc.v[0] - lin - quad)
        lb = b if lb is None else min(lb, b)
    return lb


def _centre_value(pre: Prep, box, fn):
    p0, p1, m0, m1 = box
    pc, mc = (p0 + p1) / 2, (m0 + m1) / 2
    if not in_R(pc, mc):
        return None
    R = pre.region_of_t(pc + mc)
    return fn(pre, R, D(ifr(pc)), D(ifr(mc))).v, (pc, mc, R)


def _split(box):
    p0, p1, m0, m1 = box
    wp, wm = p1 - p0, m1 - m0
    out = []
    if wp >= wm and wp > 0:
        pm = (p0 + p1) / 2
        halves = [(p0, pm, m0, m1), (pm, p1, m0, m1)]
    else:
        mm = (m0 + m1) / 2
        halves = [(p0, p1, m0, mm), (p0, p1, mm, m1)]
    for b in halves:
        if b[1] > b[0] and b[3] > b[2]:
            if b[0] + b[2] >= TMAX2D:            # 2-D box meeting R (t <= 4) at most in a corner covered elsewhere
                continue
        out.append(b)
    return out


def initial_boxes(h=F(1, 4)) -> list:
    out = []
    n = int(TMAX2D / h)
    for i in range(n):
        for j in range(n):
            p0, m0 = i * h, j * h
            if p0 + m0 < TMAX2D:
                out.append((p0, p0 + h, m0, m0 + h))
    k = int((TOP - TMAX2D) / h)
    for i in range(k):
        a = TMAX2D + i * h
        out.append((a, a + h, F(0), F(0)))
        out.append((F(0), F(0), a, a + h))
    return out


_PREP_CACHE: dict = {}


def _get_prep(key, W_json, e, omit_atom):
    if key not in _PREP_CACHE:
        _PREP_CACHE.clear()
        _PREP_CACHE[key] = Prep(StripPW.from_json(W_json), F(e), omit_atom)
    return _PREP_CACHE[key]


def bb_box(args) -> dict:
    """local branch and bound on one initial box. fn: 'res' (residual) or 'W' (nonnegativity)."""
    key, W_json, e, omit_atom, box, what, opts = args
    pre = _get_prep(key, W_json, e, omit_atom)
    fn = residual_region if what == "res" else W_region
    min_w = F(opts.get("min_width", F(1, 2 ** 40)))
    max_boxes = int(opts.get("max_boxes", 200000))
    tighten = F(opts.get("tighten_below", 0))
    tight_w = F(opts.get("tighten_min_width", F(1, 2 ** 12)))
    order = int(opts.get("order", 2))
    stack = [box]
    n = 0
    leaves_lb = None
    ub = None
    ub_at = None
    undecided = []
    while stack:
        b = stack.pop()
        n += 1
        lb = _box_bound(pre, b, fn, order)
        cv = _centre_value(pre, b, fn)
        if cv is not None:
            val, (pc, mc, R) = cv
            if ub is None or val[1] < ub:
                ub, ub_at = val[1], (pc, mc)
            if val[1] < 0:
                return {"status": "REFUTED", "boxes": n, "witness": {
                    "p": f"{pc.numerator}/{pc.denominator}", "m": f"{mc.numerator}/{mc.denominator}",
                    "region": [str(R.r0), str(R.r1)], "value_hi": F(val[1], ONE), "value_lo": F(val[0], ONE)},
                    "min_lb": None, "min_ub": F(ub, ONE)}
        width = max(b[1] - b[0], b[3] - b[2])
        need = lb < 0 or (lb < tighten * ONE and width > tight_w)
        if not need:
            leaves_lb = lb if leaves_lb is None else min(leaves_lb, lb)
            continue
        if width <= min_w or n >= max_boxes:
            undecided.append(b)
            leaves_lb = lb if leaves_lb is None else min(leaves_lb, lb)
            if n >= max_boxes:
                undecided.extend(stack)
                break
            continue
        stack.extend(_split(b))
    return {"status": "CERTIFIED" if not undecided else "UNDECIDED", "boxes": n,
            "min_lb": None if leaves_lb is None else F(leaves_lb, ONE),
            "min_ub": None if ub is None else F(ub, ONE),
            "min_ub_at": None if ub_at is None else [str(ub_at[0]), str(ub_at[1])],
            "undecided": [[str(x) for x in u] for u in undecided[:5]], "n_undecided": len(undecided)}


def _run_bb(W: StripPW, e: F, omit_atom: bool, what: str, opts: dict, workers: int, h=F(1, 4)) -> dict:
    Wj = W.to_json()
    key = (W.sha256(), str(e), omit_atom)
    jobs = [(key, Wj, str(e), omit_atom, b, what, opts) for b in initial_boxes(h)]
    t0 = time.time()
    res = []
    early = False
    if workers <= 1:
        for j in jobs:
            res.append(bb_box(j))
            if res[-1]["status"] == "REFUTED":
                early = True
                break
    else:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(min(3, workers)) as pool:
            for r in pool.imap_unordered(bb_box, jobs, chunksize=1):
                res.append(r)
                if r["status"] == "REFUTED":          # a rigorous witness decides FAIL: stop the other workers
                    early = True
                    break
    refuted = [r for r in res if r["status"] == "REFUTED"]
    und = [r for r in res if r["status"] == "UNDECIDED"]
    lbs = [r["min_lb"] for r in res if r.get("min_lb") is not None]
    ubs = [r["min_ub"] for r in res if r.get("min_ub") is not None]
    status = "REFUTED" if refuted else ("UNDECIDED" if und else "CERTIFIED")
    out = {"status": status, "boxes": sum(r["boxes"] for r in res), "initial_boxes": len(jobs),
           "initial_boxes_processed": len(res), "early_exit_on_witness": early,
           "min_lb": min(lbs) if lbs and not refuted and not und else (min(lbs) if lbs else None),
           "min_ub": min(ubs) if ubs else None, "seconds": round(time.time() - t0, 1)}
    if refuted:
        w = min(refuted, key=lambda r: r["witness"]["value_hi"])
        out["witness"] = w["witness"]
    if und:
        out["undecided_examples"] = [u for r in und for u in r["undecided"]][:5]
        out["n_undecided"] = sum(r["n_undecided"] for r in und)
    if status == "CERTIFIED":
        mu = [r for r in res if r.get("min_ub") is not None]
        best = min(mu, key=lambda r: r["min_ub"]) if mu else None
        out["min_ub_at"] = best["min_ub_at"] if best else None
    return out


def verify(W: StripPW, e, *, omit_atom: bool = False, workers: int = 3, opts: dict | None = None,
           h=F(1, 4)) -> dict:
    """Rigorously decide W >= 1 + K_e W and W >= 0 on R.  Returns
    {certified, min_margin_lower_bound, W_at_atom, witness_if_refuted, ...}."""
    e = F(e)
    Q.guard_drift(e)
    opts = dict(opts or {})
    t0 = time.time()
    res = _run_bb(W, e, omit_atom, "res", opts, workers, h)
    wopts = {"min_width": F(1, 2 ** 30), "max_boxes": 20000}
    nonneg = _run_bb(W, e, omit_atom, "W", wopts, workers, h)
    certified = res["status"] == "CERTIFIED" and nonneg["status"] == "CERTIFIED" and nonneg["min_lb"] >= 0
    witness = None
    if res["status"] == "REFUTED":
        witness = {"kind": "RESIDUAL_NEGATIVE", **res["witness"]}
    elif nonneg["status"] == "REFUTED" or (nonneg["min_ub"] is not None and nonneg["min_ub"] < 0):
        witness = {"kind": "W_NEGATIVE", **nonneg.get("witness", {})}
    out = {
        "certified": certified,
        "verdict": "PASS" if certified else ("FAIL" if witness else "UNDECIDED"),
        "min_margin_lower_bound": res["min_lb"] if res["status"] == "CERTIFIED" else None,
        "min_residual_upper_bound": res["min_ub"],
        "min_residual_upper_bound_at": res.get("min_ub_at"),
        "W_min_lower_bound": nonneg["min_lb"],
        "W_at_atom": W.at_atom(),
        "witness_if_refuted": witness,
        "drift": e, "omit_atom": omit_atom, "sha256_W": W.sha256(),
        "residual_bb": {k: v for k, v in res.items() if k not in ("witness",)},
        "nonneg_bb": {k: v for k, v in nonneg.items() if k not in ("witness",)},
        "seconds": round(time.time() - t0, 1),
    }
    return out


def jsonable(o):
    if isinstance(o, F):
        return f"{o.numerator}/{o.denominator}"
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    return o


def load_cert(path) -> StripPW:
    Q.guard_path(path)
    obj = json.loads(Path(path).read_text())
    return StripPW.from_json(obj)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("--drift", default=None)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--tighten", default="0")
    a = ap.parse_args()
    W = load_cert(a.cert)
    e = F(a.drift) if a.drift else F(json.loads(Path(a.cert).read_text())["drift"])
    r = verify(W, e, workers=a.workers, opts={"tighten_below": F(a.tighten)})
    print(json.dumps(jsonable(r), indent=1))
