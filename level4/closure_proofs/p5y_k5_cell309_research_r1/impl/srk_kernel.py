"""SRK exact CUSUM kernel machinery, geometry-parametrized (stdlib only).

PORT NOTICE.  This module is a geometry-parametrized port of the reviewed overnight C1b module
``p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/c1b_kernel.py`` (RLR review R2/R3; pinned in
C1B_R2_CODE_PINS).  The mathematics is unchanged; the frozen constants K = 1/2, H = 5 and the cover/region
literals (1 = 2k, 4 = h - 2k, 5 = h) are replaced by fields of a ``Geom`` object.  With Geom(5, 1/2) every G-form and
every enclosure is required to be identical to C1b's (test ``tests/test_srk_port_identity.py``).  The rigorous
Gaussian primitives are imported unchanged from the pinned ``c1b_gauss``.

Model (from the frozen specification, OPERATOR_AUDIT section 1), for geometry (h, k), c = h + k:
state (p, m) in the reachable closure X = {p = 0 or m = 0 or p + m <= h - 2k} of [0, h]^2; increment z with
z + e ~ N(0,1); T(x, z) = ((p + z - k)^+, (m - z - k)^+); survival window z in [m - c, c - p]; the atom a = (0, 0) is
hit iff z in [m - k, k - p] (non-empty iff p + m <= 2k).  With u = z + e, alpha_p = p - k - e, alpha_m = m - k + e:
  region II (p + m >= 2k): A: u in [l4, l2], state (0, alpha_m - u); B: u in [l2, l3], (alpha_p + u, alpha_m - u);
                           C: u in [l3, l1], (alpha_p + u, 0)
  region I  (p + m <= 2k): A: u in [l4, l3]; C: u in [l2, l1]; atom: u in [l3, l2] (whole kernel only)
  l1 = c - p + e, l2 = k - p + e, l3 = m - k + e, l4 = m - c + e.
int_A^B u^n phi = G_n(A)phi(A) - G_n(B)phi(B) + e_n (Phi(B) - Phi(A)),  G_0 = 0, G_1 = 1, G_n = t^{n-1} + (n-1)G_{n-2},
e_n = (n-1)!! (n even), 0 (n odd).  K^(j) w for polynomial w is a "G-form" {key: poly(p, m, e)} per region, keys "1",
("phi", l), ("Phi", l).  K^(j) uses the weight S^j phi(z+e) with S = -(z+e) (score); j = 0 is the plain kernel.
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path

_C1B = Path(__file__).resolve().parents[2] / "p5y_k5_tail_overnight_research" / "streams" / "C_308" / "LR" / "cusum"
if str(_C1B) not in sys.path:
    sys.path.append(str(_C1B))
import c1b_gauss as G  # noqa: E402  (pinned, geometry-free rigorous phi / Phi)


# ------------------------------------------------------------------------------------------ polynomials (p, m, e)
def padd(a: dict, b: dict, s=1) -> dict:
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + s * v
    return {k: v for k, v in out.items() if v != 0}


def pscale(a: dict, s) -> dict:
    if s == 0:
        return {}
    return {k: s * v for k, v in a.items()}


def pmul(a: dict, b: dict) -> dict:
    out: dict = {}
    for (i, j, k), v in a.items():
        for (x, y, z), w in b.items():
            key = (i + x, j + y, k + z)
            out[key] = out.get(key, 0) + v * w
    return {k: v for k, v in out.items() if v != 0}


def aff(c0, cp, cm, ce) -> dict:
    return {k: F(v) for k, v in (((0, 0, 0), c0), ((1, 0, 0), cp), ((0, 1, 0), cm), ((0, 0, 1), ce)) if v != 0}


def peval(P: dict, p, m, e) -> F:
    s = F(0)
    for (i, j, k), v in P.items():
        s += v * (p ** i) * (m ** j) * (e ** k)
    return s


def psubs_e(P: dict, e0: F) -> dict:
    out: dict = {}
    for (i, j, k), v in P.items():
        key = (i, j, 0)
        out[key] = out.get(key, 0) + v * e0 ** k
    return {k: v for k, v in out.items() if v != 0}


def pdeg(P: dict) -> int:
    return max((i + j + k for (i, j, k) in P), default=0)


# ------------------------------------------------------------------------------------------ geometry
class Geom:
    """CUSUM geometry (h, k); c = h + k.  ELL[l] = (const, p, m, e) coefficients of the window endpoints l1..l4."""

    def __init__(self, h, k):
        self.h, self.k = F(h), F(k)
        self.c = self.h + self.k
        if not (self.k > 0 and self.h > 2 * self.k):
            raise ValueError("need k > 0 and h > 2k")
        self.tri = self.h - 2 * self.k           # interior triangle p + m <= tri
        self.reg = 2 * self.k                     # region I: p + m <= 2k
        self.ELL = {1: (self.c, -1, 0, 1), 2: (self.k, -1, 0, 1), 3: (-self.k, 0, 1, 1), 4: (-self.c, 0, 1, 1)}
        self.ALPHA_P = aff(-self.k, 1, 0, -1)
        self.ALPHA_M = aff(-self.k, 0, 1, 1)
        self._pow: dict = {}

    def key(self) -> str:
        return f"h={self.h},k={self.k}"

    def ppow(self, base_key, base: dict, n: int) -> dict:
        kk = (base_key, n)
        if kk not in self._pow:
            self._pow[kk] = {(0, 0, 0): F(1)} if n == 0 else pmul(self.ppow(base_key, base, n - 1), base)
        return self._pow[kk]

    def ell_pow(self, l: int, t: int) -> dict:
        c0, cp, cm, ce = self.ELL[l]
        return self.ppow(("ell", l), aff(c0, cp, cm, ce), t)

    def in_X(self, p, m) -> bool:
        return 0 <= p <= self.h and 0 <= m <= self.h and (p == 0 or m == 0 or p + m <= self.tri)

    def region_of(self, p, m) -> int:
        return 0 if p + m <= self.reg else 1


REAL = Geom(5, F(1, 2))


# ------------------------------------------------------------------------------------------ G-forms
def gf_add(a: dict, b: dict, s=1) -> dict:
    out = dict(a)
    for k, v in b.items():
        out[k] = padd(out.get(k, {}), v, s)
    return {k: v for k, v in out.items() if v}


def gf_scale(a: dict, s) -> dict:
    return {k: pscale(v, F(s)) for k, v in a.items() if s != 0}


def gf_poly(P: dict) -> dict:
    return {"1": dict(P)} if P else {}


def gf_subs_e(a: dict, e0: F) -> dict:
    return {k: psubs_e(v, F(e0)) for k, v in a.items()}


@lru_cache(maxsize=None)
def _Gn(n: int) -> tuple:
    if n == 0:
        return ()
    if n == 1:
        return (F(1),)
    out = [F(0)] * n
    out[n - 1] += 1
    for i, c in enumerate(_Gn(n - 2)):
        out[i] += (n - 1) * c
    return tuple(out)


def _en(n: int) -> int:
    if n % 2:
        return 0
    r = 1
    for k in range(n - 1, 0, -2):
        r *= k
    return r


def _integrate(g: Geom, ucoef: dict, lo: int, hi: int, out: dict) -> None:
    """out += int_{l_lo}^{l_hi} sum_n ucoef[n] u^n phi(u) du  (ucoef: n -> poly)."""
    for l, sgn in ((lo, 1), (hi, -1)):
        acc: dict = {}
        for n, P in ucoef.items():
            for t, gg in enumerate(_Gn(n)):
                if gg:
                    acc[t] = padd(acc.get(t, {}), P, gg)
        tot: dict = {}
        for t, P in acc.items():
            if P:
                tot = padd(tot, pmul(P, g.ell_pow(l, t)))
        if tot:
            out[("phi", l)] = padd(out.get(("phi", l), {}), tot, sgn)
    phiP: dict = {}
    for n, P in ucoef.items():
        en = _en(n)
        if en:
            phiP = padd(phiP, P, en)
    if phiP:
        out[("Phi", hi)] = padd(out.get(("Phi", hi), {}), phiP, 1)
        out[("Phi", lo)] = padd(out.get(("Phi", lo), {}), phiP, -1)


def _ucoef(g: Geom, w: dict, piece: str, j: int) -> dict:
    scal: dict = {}
    for (a, b, _), c in w.items():
        if piece == "A" and a > 0:
            continue
        if piece == "C" and b > 0:
            continue
        for s in range(a + 1):
            for t in range(b + 1):
                key = (a - s, b - t, s + t)
                scal[key] = scal.get(key, 0) + c * math.comb(a, s) * math.comb(b, t) * (-1) ** t
    out: dict = {}
    for (x, y, n), v in scal.items():
        if v == 0:
            continue
        P = pmul(g.ppow("ap", g.ALPHA_P, x), g.ppow("am", g.ALPHA_M, y))
        nn = n + j
        out[nn] = padd(out.get(nn, {}), P, v * (-1) ** j)
    return {n: P for n, P in out.items() if P}


def kernel_gf(g: Geom, w: dict, j: int = 0, whole: bool = False) -> tuple:
    """(GF_I, GF_II): exact closed form of K^(j) w (taboo) or of the whole kernel (atom piece added)."""
    uA, uB, uC = _ucoef(g, w, "A", j), _ucoef(g, w, "B", j), _ucoef(g, w, "C", j)
    gI: dict = {}
    gII: dict = {}
    _integrate(g, uA, 4, 2, gII)
    _integrate(g, uB, 2, 3, gII)
    _integrate(g, uC, 3, 1, gII)
    _integrate(g, uA, 4, 3, gI)
    _integrate(g, uC, 2, 1, gI)
    if whole:
        w00 = w.get((0, 0, 0), F(0))
        if w00:
            _integrate(g, {j: {(0, 0, 0): w00 * (-1) ** j}}, 3, 2, gI)
    clean = lambda gg: {k: v for k, v in gg.items() if v}  # noqa: E731
    return clean(gI), clean(gII)


def both(gf: dict) -> tuple:
    return (gf, gf)


def pair_add(A: tuple, B: tuple, s=1) -> tuple:
    return (gf_add(A[0], B[0], s), gf_add(A[1], B[1], s))


def pair_scale(A: tuple, s) -> tuple:
    return (gf_scale(A[0], s), gf_scale(A[1], s))


def pair_subs_e(A: tuple, e0) -> tuple:
    return (gf_subs_e(A[0], e0), gf_subs_e(A[1], e0))


def poly_pair(P: dict) -> tuple:
    return both(gf_poly(P))


# ------------------------------------------------------------------------------------------ point evaluation
def _basis_iv(g: Geom, key, p, m, e):
    if key == "1":
        return F(1), F(1)
    kind, l = key
    c0, cp, cm, ce = g.ELL[l]
    t = c0 + cp * p + cm * m + ce * e
    return G.phi(t) if kind == "phi" else G.Phi(t)


def _mul_iv(v: F, iv):
    a, b = v * iv[0], v * iv[1]
    return (a, b) if a <= b else (b, a)


def gf_eval(g: Geom, gf: dict, p, m, e) -> tuple:
    lo = hi = F(0)
    for key, P in gf.items():
        v = peval(P, F(p), F(m), F(e))
        a, b = _mul_iv(v, _basis_iv(g, key, F(p), F(m), F(e)))
        lo += a
        hi += b
    return lo, hi


def pair_eval(g: Geom, A: tuple, p, m, e) -> tuple:
    return gf_eval(g, A[g.region_of(F(p), F(m))], p, m, e)


# ------------------------------------------------------------------------------------------ box cover of X
def base_cover(g: Geom, hstep: F = F(1, 4)) -> list:
    """boxes (pc, mc, rp, rm): squares of side hstep meeting the triangle p, m >= 0, p + m <= tri; axis segments to h.
    Requires tri and h - tri to be multiples of hstep (checked)."""
    hstep = F(hstep)
    if (g.tri / hstep).denominator != 1 or ((g.h - g.tri) / hstep).denominator != 1:
        raise ValueError("cover step must divide tri and h - tri")
    boxes = []
    n = int(g.tri / hstep)
    for i in range(n):
        for j in range(n):
            if (i + j) * hstep < g.tri:
                boxes.append((hstep * i + hstep / 2, hstep * j + hstep / 2, hstep / 2, hstep / 2))
    kk = int((g.h - g.tri) / hstep)
    for t in range(kk):
        cc = g.tri + hstep * t + hstep / 2
        boxes.append((cc, F(0), hstep / 2, F(0)))
        boxes.append((F(0), cc, F(0), hstep / 2))
    return boxes


def regions_of_box(g: Geom, b) -> list:
    pc, mc, rp, rm = b
    lo_sum, hi_sum = pc - rp + mc - rm, pc + rp + mc + rm
    out = []
    if lo_sum <= g.reg:
        out.append(0)
    if hi_sum >= g.reg:
        out.append(1)
    return out


def split_box(b) -> list:
    pc, mc, rp, rm = b
    out = []
    dps = (-rp / 2, rp / 2) if rp > 0 else (F(0),)
    dms = (-rm / 2, rm / 2) if rm > 0 else (F(0),)
    for dp in dps:
        for dm in dms:
            out.append((pc + dp, mc + dm, rp / 2 if rp > 0 else F(0), rm / 2 if rm > 0 else F(0)))
    return out


def box_in_X_nonempty(g: Geom, b) -> bool:
    pc, mc, rp, rm = b
    return (pc - rp) + (mc - rm) <= g.tri or rp == 0 or rm == 0


# ------------------------------------------------------------------------------------------ exact dyadic-integer Taylor model
SC = 480            # G-form coefficients are stored as integers at scale 2^SC (exactness asserted)
GP = G.PREC         # phi / Phi intervals as integers at scale 2^GP
_BIN = [[math.comb(n, k) for k in range(80)] for n in range(80)]


def _dy_exp(x: F) -> int:
    d = x.denominator
    if d & (d - 1):
        raise ValueError(f"non-dyadic value {x}")
    return d.bit_length() - 1


def to_int_gf(gf: dict) -> dict:
    out = {}
    for key, P in gf.items():
        Pi = {}
        for a, v in P.items():
            t = v * (1 << SC)
            if t.denominator != 1:
                raise ValueError("G-form coefficient not on the 2^-SC grid")
            Pi[a] = t.numerator
        out[key] = Pi
    return out


def pair_to_int(A: tuple) -> tuple:
    return (to_int_gf(A[0]), to_int_gf(A[1]))


def _iv_int(iv, scale_bits: int):
    lo, hi = iv
    return (lo.numerator << scale_bits) // lo.denominator, -((-(hi.numerator << scale_bits)) // hi.denominator)


_HE_INT: dict = {}


def _he_num(n: int, Nl: int, kd: int) -> int:
    """He_n(Nl / 2^kd) * 2^(kd n), an integer."""
    key = (n, Nl, kd)
    if key not in _HE_INT:
        h0, h1 = 1, Nl
        if n == 0:
            _HE_INT[key] = 1
        else:
            for kk in range(1, n):
                h0, h1 = h1, Nl * h1 - kk * (1 << (2 * kd)) * h0
            _HE_INT[key] = h1
    return _HE_INT[key]


def _imul_add(acc: dict, A: dict, B: dict) -> dict:
    for (i, j, k), v in A.items():
        for (x, y, z), w in B.items():
            kk = (i + x, j + y, k + z)
            acc[kk] = acc.get(kk, 0) + v * w
    return acc


_LPI: dict = {}


def _lin_pow_int(L: tuple, act: tuple, n: int) -> dict:
    key = (L, act, n)
    if key not in _LPI:
        base = {}
        for idx in range(3):
            if act[idx] and L[idx]:
                base[tuple(1 if t == idx else 0 for t in range(3))] = int(L[idx])
        out = {(0, 0, 0): 1}
        for _ in range(n):
            out = _imul_add({}, out, base)
        _LPI[key] = {k: v for k, v in out.items() if v}
    return _LPI[key]


def gf_box_int(g: Geom, gi: dict, c: tuple, r: tuple, KT: int = 10) -> tuple:
    """rigorous (lo, hi, centre) of an integer G-form over the box c +- r in (p, m, e); all inputs dyadic.
    Port of c1b_kernel.gf_box_int with ELL taken from the geometry (the ELL constants must be dyadic)."""
    act = tuple(ri > 0 for ri in r)
    kd = max(1, max(_dy_exp(F(x)) for x in tuple(c) + tuple(r)))
    for l in (1, 2, 3, 4):
        kd = max(kd, _dy_exp(F(g.ELL[l][0])))
    Nc = [int(F(x) * (1 << kd)) for x in c]
    Nr = [int(F(x) * (1 << kd)) for x in r]
    dmax = max((sum(a) for P in gi.values() for a in P), default=0)
    fKT = math.factorial(KT)
    powc = [[x ** n for n in range(dmax + 1)] for x in Nc]
    Q: dict = {}
    rem = F(0)
    Pb_scale = F(1, (1 << (SC + kd * dmax)))
    for key, Pi in gi.items():
        Ps: dict = {}
        for (i, j, k), v in Pi.items():
            for a in (range(i + 1) if act[0] else (0,)):
                va = v * _BIN[i][a] * powc[0][i - a]
                if va == 0:
                    continue
                for b in (range(j + 1) if act[1] else (0,)):
                    vb = va * _BIN[j][b] * powc[1][j - b]
                    if vb == 0:
                        continue
                    for gg in (range(k + 1) if act[2] else (0,)):
                        vg = vb * _BIN[k][gg] * powc[2][k - gg]
                        if vg:
                            sh = kd * (dmax - (i - a) - (j - b) - (k - gg))
                            kk = (a, b, gg)
                            Ps[kk] = Ps.get(kk, 0) + (vg << sh)
        Ps = {kk: v for kk, v in Ps.items() if v}
        if not Ps:
            continue
        Pb = F(0)
        for (a, b, gg), v in Ps.items():
            Pb += abs(v) * F(r[0]) ** a * F(r[1]) ** b * F(r[2]) ** gg
        Pb *= Pb_scale
        if key == "1":
            T = {(0, 0, 0): fKT << (kd * KT)}
            Q["1"] = _imul_add(Q.get("1", {}), Ps, T)
            continue
        kind, l = key
        c0, cp, cm, ce = g.ELL[l]
        L = (cp, cm, ce)
        Nl = int((c0 + cp * F(c[0]) + cm * F(c[1]) + ce * F(c[2])) * (1 << kd))
        rho = sum(abs(L[t]) * F(r[t]) for t in range(3))
        if kind == "phi":
            T = {}
            for n in range(KT + 1):
                if n > 0 and rho == 0:
                    break
                coef = (-1) ** n * (fKT // math.factorial(n)) * _he_num(n, Nl, kd) << (kd * (KT - n))
                if coef:
                    for kk, lv in _lin_pow_int(L, act, n).items():
                        T[kk] = T.get(kk, 0) + coef * lv
            Q[("phi", l)] = _imul_add(Q.get(("phi", l), {}), Ps, T)
            rem += Pb * G.dphi_sup(KT + 1) * rho ** (KT + 1) / math.factorial(KT + 1)
        else:
            Q[("Phi", l)] = _imul_add(Q.get(("Phi", l), {}), Ps, {(0, 0, 0): fKT << (kd * KT)})
            if rho > 0:
                T = {}
                for n in range(1, KT + 1):
                    coef = (-1) ** (n - 1) * (fKT // math.factorial(n)) * _he_num(n - 1, Nl, kd) << (kd * (KT - n + 1))
                    if coef:
                        for kk, lv in _lin_pow_int(L, act, n).items():
                            T[kk] = T.get(kk, 0) + coef * lv
                Q[("phi", l)] = _imul_add(Q.get(("phi", l), {}), Ps, T)
                rem += Pb * G.dphi_sup(KT) * rho ** (KT + 1) / math.factorial(KT + 1)
    coefs: dict = {}
    for sig, Qs in Q.items():
        if sig == "1":
            slo = shi = 1 << GP
        else:
            kind, l = sig
            c0, cp, cm, ce = g.ELL[l]
            tc = c0 + cp * F(c[0]) + cm * F(c[1]) + ce * F(c[2])
            slo, shi = _iv_int(G.phi(tc) if kind == "phi" else G.Phi(tc), GP)
        for alpha, v in Qs.items():
            a, b = v * slo, v * shi
            if a > b:
                a, b = b, a
            lo0, hi0 = coefs.get(alpha, (0, 0))
            coefs[alpha] = (lo0 + a, hi0 + b)
    Amax = max((sum(a) for a in coefs), default=0)
    var = 0
    clo = chi = 0
    for alpha, (a, b) in coefs.items():
        if alpha == (0, 0, 0):
            clo, chi = a, b
            continue
        if any(alpha[t] and not act[t] for t in range(3)):
            continue
        m_ = max(abs(a), abs(b))
        w = Nr[0] ** alpha[0] * Nr[1] ** alpha[1] * Nr[2] ** alpha[2]
        var += m_ * w << (kd * (Amax - sum(alpha)))
    Zbits = SC + kd * dmax + kd * KT + GP
    Z = fKT * (1 << Zbits)
    lo = F(clo, Z) - F(var, Z << (kd * Amax)) - rem
    hi = F(chi, Z) + F(var, Z << (kd * Amax)) + rem
    return lo, hi, F(clo + chi, 2 * Z)


def enclose_box(g: Geom, Ai: tuple, b, e_c: F, e_r: F, KT: int = 10) -> tuple:
    """(lo, hi) of an integer region-pair G-form over the state box b (x) [e_c - e_r, e_c + e_r]."""
    los, his = [], []
    for reg in regions_of_box(g, b):
        lo, hi, _ = gf_box_int(g, Ai[reg], (b[0], b[1], e_c), (b[2], b[3], e_r), KT)
        los.append(lo)
        his.append(hi)
    return min(los), max(his)


def dyadic_round_poly(P: dict, bits: int = 200) -> dict:
    out = {}
    for k, v in P.items():
        t = F(round(v * (1 << bits)), 1 << bits)
        if t:
            out[k] = t
    return out
