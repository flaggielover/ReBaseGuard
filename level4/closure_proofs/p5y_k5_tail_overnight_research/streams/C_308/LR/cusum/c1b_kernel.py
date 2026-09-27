"""C1b exact CUSUM kernel machinery: polynomial candidates -> closed-form "G-forms" -> rigorous enclosures on R.

Model (re-derived from the frozen specification, as in C11): K = 1/2, H = 5, C = K + H = 11/2, state (p, m),
increment z with z + e ~ N(0,1); next state T(x,z) = ((p+z-K)^+, (m-z-K)^+); alarm-free window z in [m-C, C-p];
atom a = (0,0) is hit iff z in [m-K, K-p] (non-empty iff p+m <= 1).  Taboo kernel K^_e: window minus atom window.
Score S = -(z+e) (d/de log phi(z+e)); moment kernels K^(j) f(x) = int_{A^(x)} f(T(x,z)) S^j phi(z+e) dz.

With u = z + e, alpha_p = p-K-e, alpha_m = m-K+e the pieces are
  region II (p+m >= 1): A: u in [l4, l2], state (0, alpha_m - u);  B: u in [l2, l3], (alpha_p+u, alpha_m-u);
                        C: u in [l3, l1], (alpha_p+u, 0)
  region I  (p+m <= 1): A: u in [l4, l3];  C: u in [l2, l1];  atom: u in [l3, l2] (whole kernel only)
  l1 = C-p+e, l2 = K-p+e, l3 = m-K+e, l4 = m-C+e.
int_A^B u^n phi = G_n(A)phi(A) - G_n(B)phi(B) + e_n (Phi(B)-Phi(A)),  G_0=0, G_1=1, G_n = t^{n-1} + (n-1)G_{n-2},
e_n = (n-1)!! (n even), 0 (n odd).  Hence K^(j) w = sum_l [P_l phi(l) + Q_l Phi(l)] (+ P_0): a "G-form"
{key: poly(p,m,e)} per region, exact rationals.  G-forms are closed under +, scalar, and the enclosure below.

Enclosure of a G-form on a box (Taylor model of order KT at the centre): exact shifted polynomials, exact Hermite
Taylor coefficients (phi^(n)(t) = (-1)^n He_n(t) phi(t)), Lagrange remainder with sup|phi^(n)| <= E|Y|^n/sqrt(2pi),
range of a polynomial bounded by |c_0| + sum_{alpha != 0} |c_alpha| r^alpha.  Sound on B for each region form
used; a box meeting both regions is enclosed with both forms (the union contains the true range on B).
No side effects at import.
"""
from __future__ import annotations

import math
from fractions import Fraction as F
from functools import lru_cache

import c1b_gauss as G

K = F(1, 2)
H = F(5)
C = K + H
ELL = {1: (C, -1, 0, 1), 2: (K, -1, 0, 1), 3: (-K, 0, 1, 1), 4: (-C, 0, 1, 1)}   # const, p, m, e coefficients


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


_POWC: dict = {}


def ppow(base_key, base: dict, n: int) -> dict:
    key = (base_key, n)
    if key not in _POWC:
        _POWC[key] = {(0, 0, 0): F(1)} if n == 0 else pmul(ppow(base_key, base, n - 1), base)
    return _POWC[key]


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
    """coefficients (low->high) of G_n(t)."""
    if n == 0:
        return ()
    if n == 1:
        return (F(1),)
    g2 = list(_Gn(n - 2)) + [F(0)] * n
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


def _ell_pow(l: int, t: int) -> dict:
    c0, cp, cm, ce = ELL[l]
    return ppow(("ell", l), aff(c0, cp, cm, ce), t)


def _integrate(ucoef: dict, lo: int, hi: int, out: dict) -> None:
    """out += int_{l_lo}^{l_hi} sum_n ucoef[n] u^n phi(u) du  (ucoef: n -> poly)."""
    for l, sgn in ((lo, 1), (hi, -1)):
        # sum_n c_n G_n(l)  -> coefficients in powers of l
        acc: dict = {}
        for n, P in ucoef.items():
            for t, g in enumerate(_Gn(n)):
                if g:
                    acc[t] = padd(acc.get(t, {}), P, g)
        tot: dict = {}
        for t, P in acc.items():
            if P:
                tot = padd(tot, pmul(P, _ell_pow(l, t)))
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


ALPHA_P = aff(-K, 1, 0, -1)
ALPHA_M = aff(-K, 0, 1, 1)


def _ucoef(w: dict, piece: str, j: int) -> dict:
    """integrand polynomial in u (n -> poly(p,m,e)) for state polynomial w(p', m') (keys (a, b, 0))."""
    scal: dict = {}          # (x, y, n) -> scalar  meaning scalar * alpha_p^x alpha_m^y u^n
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
        P = pmul(ppow("ap", ALPHA_P, x), ppow("am", ALPHA_M, y))
        nn = n + j
        out[nn] = padd(out.get(nn, {}), P, v * (-1) ** j)
    return {n: P for n, P in out.items() if P}


def kernel_gf(w: dict, j: int = 0, whole: bool = False) -> tuple:
    """(GF_I, GF_II): exact closed form of K^(j) w (taboo) or K^(j) w (whole kernel, atom piece added)."""
    uA, uB, uC = _ucoef(w, "A", j), _ucoef(w, "B", j), _ucoef(w, "C", j)
    gI: dict = {}
    gII: dict = {}
    _integrate(uA, 4, 2, gII)
    _integrate(uB, 2, 3, gII)
    _integrate(uC, 3, 1, gII)
    _integrate(uA, 4, 3, gI)
    _integrate(uC, 2, 1, gI)
    if whole:
        w00 = w.get((0, 0, 0), F(0))
        if w00:
            _integrate({j: {(0, 0, 0): w00 * (-1) ** j}}, 3, 2, gI)
    clean = lambda g: {k: v for k, v in g.items() if v}
    return clean(gI), clean(gII)


def both(g: dict) -> tuple:
    return (g, g)


def pair_add(A: tuple, B: tuple, s=1) -> tuple:
    return (gf_add(A[0], B[0], s), gf_add(A[1], B[1], s))


def pair_scale(A: tuple, s) -> tuple:
    return (gf_scale(A[0], s), gf_scale(A[1], s))


def pair_subs_e(A: tuple, e0) -> tuple:
    return (gf_subs_e(A[0], e0), gf_subs_e(A[1], e0))


# operator-level special functions (identical in both regions unless stated)
H1 = both({"1": {(0, 0, 0): F(1)}, ("Phi", 1): {(0, 0, 0): F(-1)}, ("Phi", 4): {(0, 0, 0): F(1)}})
H1P = both({("phi", 1): {(0, 0, 0): F(-1)}, ("phi", 4): {(0, 0, 0): F(1)}})
H1PP = both({("phi", 1): aff(C, -1, 0, 1), ("phi", 4): pscale(aff(-C, 0, 1, 1), -1)})
KA = ({("Phi", 2): {(0, 0, 0): F(1)}, ("Phi", 3): {(0, 0, 0): F(-1)}}, {})


def poly_pair(P: dict) -> tuple:
    return both(gf_poly(P))


# ------------------------------------------------------------------------------------------ evaluation
def _basis_iv(key, p, m, e):
    if key == "1":
        return F(1), F(1)
    kind, l = key
    c0, cp, cm, ce = ELL[l]
    t = c0 + cp * p + cm * m + ce * e
    return G.phi(t) if kind == "phi" else G.Phi(t)


def _mul_iv(v: F, iv):
    a, b = v * iv[0], v * iv[1]
    return (a, b) if a <= b else (b, a)


def gf_eval(g: dict, p, m, e) -> tuple:
    lo = hi = F(0)
    for key, P in g.items():
        v = peval(P, F(p), F(m), F(e))
        a, b = _mul_iv(v, _basis_iv(key, F(p), F(m), F(e)))
        lo += a
        hi += b
    return lo, hi


def region_of(p, m) -> int:
    return 0 if p + m <= 1 else 1


def pair_eval(A: tuple, p, m, e) -> tuple:
    """point value using the correct region form (both forms agree on p+m = 1)."""
    return gf_eval(A[region_of(F(p), F(m))], p, m, e)


# ------------------------------------------------------------------------------------------ box enclosure
_BIN = [[math.comb(n, k) for k in range(64)] for n in range(64)]


def pshift(P: dict, c: tuple, act: tuple) -> dict:
    """P(c + delta) in delta-monomials; variables with act[i] False are fixed at c[i] (delta_i = 0)."""
    pc, mc, ec = c
    out: dict = {}
    for (i, j, k), v in P.items():
        ai = range(i + 1) if act[0] else (0,)
        aj = range(j + 1) if act[1] else (0,)
        ak = range(k + 1) if act[2] else (0,)
        for a in ai:
            va = v * _BIN[i][a] * pc ** (i - a)
            if va == 0:
                continue
            for b in aj:
                vb = va * _BIN[j][b] * mc ** (j - b)
                if vb == 0:
                    continue
                for g in ak:
                    vg = vb * _BIN[k][g] * ec ** (k - g)
                    if vg:
                        key = (a, b, g)
                        out[key] = out.get(key, 0) + vg
    return out


def _lin_pow(L: tuple, act: tuple, n: int) -> dict:
    """(L . delta)^n as delta-polynomial, L entries in {0, +-1}."""
    base = {}
    for idx in range(3):
        if act[idx] and L[idx]:
            key = tuple(1 if t == idx else 0 for t in range(3))
            base[key] = F(L[idx])
    out = {(0, 0, 0): F(1)}
    for _ in range(n):
        out = pmul(out, base)
    return out


def _abs_bound(P: dict, r: tuple) -> F:
    s = F(0)
    for (i, j, k), v in P.items():
        s += abs(v) * r[0] ** i * r[1] ** j * r[2] ** k
    return s


def gf_box(g: dict, c: tuple, r: tuple, KT: int = 10) -> tuple:
    """rigorous (lo, hi) of the G-form over the box c +- r (r_i may be 0)."""
    act = tuple(ri > 0 for ri in r)
    Q: dict = {}          # sigma -> delta-poly
    rem = F(0)
    fact = math.factorial(KT + 1)
    for key, P in g.items():
        Ps = pshift(P, c, act)
        if key == "1":
            Q["1"] = padd(Q.get("1", {}), Ps)
            continue
        kind, l = key
        c0, cp, cm, ce = ELL[l]
        L = (cp, cm, ce)
        tc = c0 + cp * c[0] + cm * c[1] + ce * c[2]
        rho = sum(abs(L[i]) * r[i] for i in range(3))
        Pb = _abs_bound(Ps, r)
        he = [G.hermite_he(n, tc) for n in range(KT + 1)]
        if kind == "phi":
            T = {}
            for n in range(KT + 1):
                coef = (-1) ** n * he[n] / math.factorial(n)
                if coef:
                    T = padd(T, _lin_pow(L, act, n), coef) if rho > 0 or n == 0 else T
            Q[("phi", l)] = padd(Q.get(("phi", l), {}), pmul(Ps, T))
            rem += Pb * G.dphi_sup(KT + 1) * rho ** (KT + 1) / fact
        else:
            Q[("Phi", l)] = padd(Q.get(("Phi", l), {}), Ps)
            if rho > 0:
                T = {}
                for n in range(1, KT + 1):
                    coef = (-1) ** (n - 1) * he[n - 1] / math.factorial(n)
                    if coef:
                        T = padd(T, _lin_pow(L, act, n), coef)
                Q[("phi", l)] = padd(Q.get(("phi", l), {}), pmul(Ps, T))
                rem += Pb * G.dphi_sup(KT) * rho ** (KT + 1) / fact
    # combine
    c_lo = c_hi = F(0)
    var = F(0)
    coefs: dict = {}
    for sig, P in Q.items():
        if sig == "1":
            iv = (F(1), F(1))
        else:
            kind, l = sig
            c0, cp, cm, ce = ELL[l]
            tc = c0 + cp * c[0] + cm * c[1] + ce * c[2]
            iv = G.phi(tc) if kind == "phi" else G.Phi(tc)
        for alpha, v in P.items():
            a, b = _mul_iv(v, iv)
            lo0, hi0 = coefs.get(alpha, (F(0), F(0)))
            coefs[alpha] = (lo0 + a, hi0 + b)
    for alpha, (a, b) in coefs.items():
        if alpha == (0, 0, 0):
            c_lo, c_hi = a, b
        else:
            w = r[0] ** alpha[0] * r[1] ** alpha[1] * r[2] ** alpha[2]
            if w:
                var += max(abs(a), abs(b)) * w
    return c_lo - var - rem, c_hi + var + rem, (c_lo + c_hi) / 2


# ------------------------------------------------------------------------------------------ cover of R
def base_cover(h: F = F(1, 4)) -> list:
    """boxes (pc, mc, rp, rm): squares of side h meeting the triangle p,m>=0, p+m<=4; axis segments to 5."""
    boxes = []
    n = int(4 / h)
    for i in range(n):
        for j in range(n):
            if (i + j) * h < 4:
                boxes.append((h * i + h / 2, h * j + h / 2, h / 2, h / 2))
    k = int(1 / h)
    for t in range(k):
        c = 4 + h * t + h / 2
        boxes.append((c, F(0), h / 2, F(0)))
        boxes.append((F(0), c, F(0), h / 2))
    return boxes


def regions_of_box(b) -> list:
    pc, mc, rp, rm = b
    lo_sum, hi_sum = pc - rp + mc - rm, pc + rp + mc + rm
    out = []
    if lo_sum <= 1:
        out.append(0)
    if hi_sum >= 1:
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


def box_in_R_nonempty(b) -> bool:
    pc, mc, rp, rm = b
    return (pc - rp) + (mc - rm) <= 4 or rp == 0 or rm == 0


def enclose_pair(A: tuple, e_c: F, e_r: F = F(0), h: F = F(1, 4), extra_levels: int = 4, KT: int = 10,
                 tol: F = F(5, 4), abs_tol: F = F(1, 10 ** 12), boxes=None) -> dict:
    """rigorous (lo, hi) of the region-pair G-form over R (x) [e_c - e_r, e_c + e_r], adaptive per the D2 rule."""
    work = [(b, 0) for b in (boxes if boxes is not None else base_cover(h))]
    Ai = pair_to_int(A)
    results = {}
    while True:
        new = []
        for b, lev in work:
            los, his, mids = [], [], []
            for reg in regions_of_box(b):
                lo, hi, mid = gf_box_int(Ai[reg], (b[0], b[1], e_c), (b[2], b[3], e_r), KT)
                los.append(lo)
                his.append(hi)
                mids.append(mid)
            results[b] = (min(los), max(his), mids, lev)
        # decision: tolerance relative to centre extremes
        cmax = max(max(v[2]) for v in results.values())
        cmin = min(min(v[2]) for v in results.values())
        up_lim = cmax + (tol - 1) * abs(cmax) + abs_tol
        lo_lim = cmin - (tol - 1) * abs(cmin) - abs_tol
        for b, (lo, hi, mids, lev) in list(results.items()):
            if (hi > up_lim or lo < lo_lim) and lev < extra_levels:
                del results[b]
                for cb in split_box(b):
                    if box_in_R_nonempty(cb):
                        new.append((cb, lev + 1))
        if not new:
            break
        work = new
    lo = min(v[0] for v in results.values())
    hi = max(v[1] for v in results.values())
    worst_lo = min(results.items(), key=lambda kv: kv[1][0])
    worst_hi = max(results.items(), key=lambda kv: kv[1][1])
    return {"lo": lo, "hi": hi, "centre_min": cmin, "centre_max": cmax, "boxes": len(results),
            "max_level": max(v[3] for v in results.values()),
            "argmin_box": [str(x) for x in worst_lo[0]], "argmax_box": [str(x) for x in worst_hi[0]]}


# ------------------------------------------------------------------------------------------ polynomial range on R
def poly_range_R(P: dict, h: F = F(1, 4), extra_levels: int = 3) -> tuple:
    """rigorous (min, max) of a state polynomial over R (as a G-form with only the '1' key)."""
    res = enclose_pair(poly_pair(P), F(0), F(0), h=h, extra_levels=extra_levels)
    return res["lo"], res["hi"], res


def selftest() -> dict:
    out = {}
    e = F(1, 2)
    # mass balance K^1 + k_a + h1 = 1 at points of both regions
    one = {(0, 0, 0): F(1)}
    g = pair_subs_e(kernel_gf(one, 0), e)
    ka = pair_subs_e(KA, e)
    h1 = pair_subs_e(H1, e)
    tot = pair_add(pair_add(g, ka), h1)
    worst = F(0)
    for (p, m) in [(F(0), F(0)), (F(1, 4), F(1, 2)), (F(3, 2), F(1, 3)), (F(5), F(0)), (F(0), F(9, 2)), (F(2), F(2))]:
        lo, hi = pair_eval(tot, p, m, e)
        worst = max(worst, abs(lo - 1), abs(hi - 1))
    out["mass_balance_maxdev"] = float(worst)
    out["mass_balance_ok"] = worst < F(1, 10 ** 25)
    # standard moments: whole-kernel K^(j) 1 over a full window approximates E S^j (window covers +-5.5)
    return out


if __name__ == "__main__":
    print(selftest())


# ------------------------------------------------------------------------------------------ exact dyadic-integer Taylor model
SC = 480            # G-form coefficients are stored as integers at scale 2^SC (exactness asserted)
GP = G.PREC         # phi / Phi intervals as integers at scale 2^GP


def _dy_exp(x: F) -> int:
    d = x.denominator
    if d & (d - 1):
        raise ValueError(f"non-dyadic value {x}")
    return d.bit_length() - 1


def to_int_gf(g: dict) -> dict:
    out = {}
    for key, P in g.items():
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
        # He_n(x) 2^(kd n) via recurrence on scaled values: H_n = x H_{n-1} - (n-1) H_{n-2}
        h0, h1 = 1, Nl                       # scaled: He_0 * 1, He_1 * 2^kd
        if n == 0:
            _HE_INT[key] = 1
        else:
            for k in range(1, n):
                h0, h1 = h1, Nl * h1 - k * (1 << (2 * kd)) * h0
            _HE_INT[key] = h1
    return _HE_INT[key]


def gf_box_int(gi: dict, c: tuple, r: tuple, KT: int = 10) -> tuple:
    """same statement as gf_box (rigorous (lo, hi) over c +- r), exact scaled-integer arithmetic.
    Requires c, r, and all G-form coefficients dyadic."""
    act = tuple(ri > 0 for ri in r)
    kd = max(1, max(_dy_exp(F(x)) for x in tuple(c) + tuple(r)))
    Nc = [int(F(x) * (1 << kd)) for x in c]
    Nr = [int(F(x) * (1 << kd)) for x in r]
    dmax = max((sum(a) for P in gi.values() for a in P), default=0)
    fKT = math.factorial(KT)
    powc = [[x ** n for n in range(dmax + 1)] for x in Nc]
    Q: dict = {}
    rem = F(0)
    Pb_scale = F(1, (1 << (SC + kd * dmax)))
    for key, Pi in gi.items():
        # shifted polynomial, integer coefficients at scale 2^(SC + kd*dmax)
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
                    for g in (range(k + 1) if act[2] else (0,)):
                        vg = vb * _BIN[k][g] * powc[2][k - g]
                        if vg:
                            sh = kd * (dmax - (i - a) - (j - b) - (k - g))
                            kk = (a, b, g)
                            Ps[kk] = Ps.get(kk, 0) + (vg << sh)
        Ps = {kk: v for kk, v in Ps.items() if v}
        if not Ps:
            continue
        # |Ps| bound on the box (as a Fraction)
        Pb = F(0)
        for (a, b, g), v in Ps.items():
            Pb += abs(v) * F(r[0]) ** a * F(r[1]) ** b * F(r[2]) ** g
        Pb *= Pb_scale
        if key == "1":
            T = {(0, 0, 0): fKT << (kd * KT)}
            Q["1"] = _imul_add(Q.get("1", {}), Ps, T)
            continue
        kind, l = key
        c0, cp, cm, ce = ELL[l]
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
    # combine with sigma intervals (integers at scale 2^GP)
    coefs: dict = {}
    for sig, Qs in Q.items():
        if sig == "1":
            slo = shi = 1 << GP
        else:
            kind, l = sig
            c0, cp, cm, ce = ELL[l]
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


def dyadic_round_poly(P: dict, bits: int = 200) -> dict:
    """round every coefficient to the nearest multiple of 2^-bits (declaration D7(d))."""
    out = {}
    for k, v in P.items():
        t = F(round(v * (1 << bits)), 1 << bits)
        if t:
            out[k] = t
    return out
