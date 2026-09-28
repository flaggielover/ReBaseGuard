"""C1b strip-piecewise machinery (declaration D8). Exact side + untrusted float side. No side effects beyond
registering six extra boundary forms in c1b_kernel.ELL (l3 - b, l2 + b for b = 1, 2, 3) at import.

A candidate is a list ws = [P_1, ..., P_S] of state polynomials, P_s used on strip s = [BW[s-1], BW[s]] of t = p+m
(right-closed; strip 1 closed).  For x in x-region J = [J-1, J] (J = 1..5) of t:
  J = 1 : A pieces u in [l3 - BW[s], l3 - BW[s-1]] with P_s;  C pieces u in [l2 + BW[s-1], l2 + BW[s]] with P_s;
          (whole kernel: atom piece u in [l3, l2] with P_1(0,0))
  J >= 2: sigma = strip containing [J-2, J-1] (the images of piece B have p'+m' = p+m-1 in it);
          A: [l3 - BW[sigma], l2] with P_sigma, then full strips s > sigma;  C: [l3, l2 + BW[sigma]] with P_sigma,
          then full strips s > sigma;  B: [l2, l3] with P_sigma.
The value w(x) for x in region J uses P_{strip containing [J-1, J]}.  BW = [0, 5] reproduces the plain family.
"""
from __future__ import annotations

import math
from fractions import Fraction as F

import c1b_kernel as KX
import c1b_float as FL

for _b in (1, 2, 3):
    KX.ELL[30 + _b] = (-KX.K - _b, 0, 1, 1)     # l3 - b
    KX.ELL[20 + _b] = (KX.K + _b, -1, 0, 1)     # l2 + b

NREG = 5
BW_PW = (0, 1, 2, 3, 5)
BW_PLAIN = (0, 5)


def keyA(b: int) -> int:        # boundary l3 - b
    return {0: 3, 5: 4}.get(b, 30 + b)


def keyC(b: int) -> int:        # boundary l2 + b
    return {0: 2, 5: 1}.get(b, 20 + b)


def strip_of_interval(BW, lo: int, hi: int) -> int:
    for s in range(1, len(BW)):
        if BW[s - 1] <= lo and hi <= BW[s]:
            return s
    raise ValueError("interval not inside one strip")


def strip_of_t(BW, t: float) -> int:
    for s in range(1, len(BW)):
        if t <= BW[s]:
            return s
    return len(BW) - 1


def kernel_gf_pw(ws: list, BW, j: int = 0, whole: bool = False) -> tuple:
    S = len(BW) - 1
    uA = [KX._ucoef(P, "A", j) for P in ws]
    uB = [KX._ucoef(P, "B", j) for P in ws]
    uC = [KX._ucoef(P, "C", j) for P in ws]
    forms = []
    for J in range(1, NREG + 1):
        g: dict = {}
        if J == 1:
            for s in range(1, S + 1):
                KX._integrate(uA[s - 1], keyA(BW[s]), keyA(BW[s - 1]), g)
                KX._integrate(uC[s - 1], keyC(BW[s - 1]), keyC(BW[s]), g)
            if whole:
                w00 = ws[0].get((0, 0, 0), F(0))
                if w00:
                    KX._integrate({j: {(0, 0, 0): w00 * (-1) ** j}}, 3, 2, g)
        else:
            sg = strip_of_interval(BW, J - 2, J - 1)
            KX._integrate(uA[sg - 1], keyA(BW[sg]), 2, g)
            KX._integrate(uC[sg - 1], 3, keyC(BW[sg]), g)
            KX._integrate(uB[sg - 1], 2, 3, g)
            for s in range(sg + 1, S + 1):
                KX._integrate(uA[s - 1], keyA(BW[s]), keyA(BW[s - 1]), g)
                KX._integrate(uC[s - 1], keyC(BW[s - 1]), keyC(BW[s]), g)
        forms.append({k: v for k, v in g.items() if v})
    return tuple(forms)


# ------------------------------------------------------------------------------------------ tuple (per-region) algebra
def tadd(A: tuple, B: tuple, s=1) -> tuple:
    return tuple(KX.gf_add(a, b, s) for a, b in zip(A, B))


def tscale(A: tuple, s) -> tuple:
    return tuple(KX.gf_scale(a, s) for a in A)


def tsubs_e(A: tuple, e0) -> tuple:
    return tuple(KX.gf_subs_e(a, e0) for a in A)


def tconst(g: dict) -> tuple:
    return tuple(g for _ in range(NREG))


def tpoly(ws: list, BW) -> tuple:
    return tuple(KX.gf_poly(ws[strip_of_interval(BW, J - 1, J) - 1]) for J in range(1, NREG + 1))


KA_T = (KX.KA[0],) + tuple({} for _ in range(NREG - 1))
H1_T, H1P_T, H1PP_T = (tconst(KX.H1[0]), tconst(KX.H1P[0]), tconst(KX.H1PP[0]))


def region_of_point(p: F, m: F) -> int:
    t = p + m
    return max(1, min(NREG, math.ceil(t))) if t > 0 else 1


def teval(A: tuple, p, m, e) -> tuple:
    return KX.gf_eval(A[region_of_point(F(p), F(m)) - 1], p, m, e)


def regions_of_box(b) -> list:
    """x-regions a box must be checked in.  D13: points of R with p+m > 4 lie only on the axis segments, which are
    covered by 1-D boxes; so the J = 5 form is checked on 1-D boxes only (2-D boxes have p, m <= 4)."""
    pc, mc, rp, rm = b
    lo, hi = pc - rp + mc - rm, pc + rp + mc + rm
    two_d = rp > 0 and rm > 0
    return [J for J in range(1, NREG + 1) if not (hi < J - 1 or lo > J) and not (two_d and J == NREG)]


def in_R(p, m) -> bool:
    """R = {0 <= p, m <= 5 : p = 0 or m = 0 or p + m <= 4}."""
    return 0 <= p <= 5 and 0 <= m <= 5 and (p == 0 or m == 0 or p + m <= 4)


def enclose_t(A: tuple, e_c: F, e_r: F = F(0), h: F = F(1, 4), extra_levels: int = 4, KT: int = 10,
              tol: F = F(5, 4), abs_tol: F = F(1, 10 ** 12)) -> dict:
    """rigorous (lo, hi) of a per-region G-form tuple over R (x) [e_c - e_r, e_c + e_r] (D2 adaptive rule)."""
    Ai = tuple(KX.to_int_gf(a) for a in A)
    work = [(b, 0) for b in KX.base_cover(h)]
    results = {}
    while True:
        new = []
        for b, lev in work:
            los, his, mids = [], [], []
            own = None
            for J in regions_of_box(b):
                lo, hi, mid = KX.gf_box_int(Ai[J - 1], (b[0], b[1], e_c), (b[2], b[3], e_r), KT)
                los.append(lo)
                his.append(hi)
                mids.append(mid)
                if in_R(b[0], b[1]) and region_of_point(b[0], b[1]) == J:
                    own = mid          # centre value of the owning form at a point of R (a genuine witness)
            results[b] = (min(los), max(his), mids, lev, own)
        cmax = max(max(v[2]) for v in results.values())
        cmin = min(min(v[2]) for v in results.values())
        up_lim = cmax + (tol - 1) * abs(cmax) + abs_tol
        lo_lim = cmin - (tol - 1) * abs(cmin) - abs_tol
        for b, (lo, hi, mids, lev, own) in list(results.items()):
            if (hi > up_lim or lo < lo_lim) and lev < extra_levels:
                del results[b]
                for cb in KX.split_box(b):
                    if KX.box_in_R_nonempty(cb):
                        new.append((cb, lev + 1))
        if not new:
            break
        work = new
    lo = min(v[0] for v in results.values())
    hi = max(v[1] for v in results.values())
    wl = min(results.items(), key=lambda kv: kv[1][0])[0]
    wh = max(results.items(), key=lambda kv: kv[1][1])[0]
    owns = [v[4] for v in results.values() if v[4] is not None]
    return {"lo": lo, "hi": hi, "centre_min": cmin, "centre_max": cmax, "boxes": len(results),
            "centre_min_R": min(owns) if owns else None, "centre_max_R": max(owns) if owns else None,
            "max_level": max(v[3] for v in results.values()),
            "argmin_box": [float(x) for x in wl], "argmax_box": [float(x) for x in wh]}


# ------------------------------------------------------------------------------------------ untrusted float side
def sample_set_pw():
    pts = FL.sample_set()
    seen = set(pts)
    for i in range(21):
        for j in range(21 - i):
            q = (i / 20, j / 20)
            if q not in seen:
                pts.append(q)
                seen.add(q)
    return pts


class DiscPW:
    def __init__(self, e: float, d: int, BW, pts=None):
        self.e, self.d, self.BW = e, d, BW
        self.S = len(BW) - 1
        self.idx = FL.basis_index(d)
        self.nb = len(self.idx)
        self.pts = pts or sample_set_pw()
        self.nod, self.ka = [], []
        for (p, m) in self.pts:
            nl, ka = FL.nodes(p, m, e)
            self.nod.append(nl)
            self.ka.append(ka)

    def feval(self, coefs, p, m):
        s = strip_of_t(self.BW, p + m)
        tp = FL.cheb_all(2 * p / 5 - 1, self.d)
        tm = FL.cheb_all(2 * m / 5 - 1, self.d)
        return sum(c * tp[i] * tm[j] for c, (i, j) in zip(coefs[s - 1], self.idx))

    def apply(self, coefs, j: int = 0):
        return [sum(ww * (S ** j) * self.feval(coefs, pp, mm) for (ww, S, pp, mm) in nl) for nl in self.nod]

    def value(self, coefs):
        return [self.feval(coefs, p, m) for (p, m) in self.pts]

    def matrix(self, whole=False):
        n = self.S * self.nb
        cols = [[0.0] * len(self.pts) for _ in range(n)]
        b00 = FL.basis_vals(0.0, 0.0, self.d, self.idx)
        for i, ((p, m), nl) in enumerate(zip(self.pts, self.nod)):
            acc = [0.0] * n
            s = strip_of_t(self.BW, p + m)
            bx = FL.basis_vals(p, m, self.d, self.idx)
            for k in range(self.nb):
                acc[(s - 1) * self.nb + k] += bx[k]
            for (ww, S, pp, mm) in nl:
                sn = strip_of_t(self.BW, pp + mm)
                bv = FL.basis_vals(pp, mm, self.d, self.idx)
                off = (sn - 1) * self.nb
                for k in range(self.nb):
                    acc[off + k] -= ww * bv[k]
            if whole:
                for k in range(self.nb):
                    acc[k] -= self.ka[i] * b00[k]
            for k in range(n):
                cols[k][i] = acc[k]
        return cols

    def split(self, c):
        return [c[s * self.nb:(s + 1) * self.nb] for s in range(self.S)]


def solve_chain_pw(e: float, d: int, BW) -> dict:
    D = DiscPW(e, d, BW)
    qt = FL.QR(D.matrix(False))
    qw = FL.QR(D.matrix(True))
    pts = D.pts
    sv = lambda rhs: D.split(qt.solve(rhs))
    out = {}
    out["b0"] = b0 = sv([1.0] * len(pts))
    out["b1"] = b1 = sv(D.apply(b0, 1))
    out["b2"] = sv([a + 2 * b for a, b in zip(D.apply(b0, 2), D.apply(b1, 1))])
    out["xT"] = sv(D.value(b0))
    out["d0"] = d0 = sv([FL.h1f(p, m, e) for p, m in pts])
    out["d1"] = d1 = sv([a + FL.h1pf(p, m, e) for a, (p, m) in zip(D.apply(d0, 1), pts)])
    out["d2"] = sv([a - b + 2 * c + FL.h1ppf(p, m, e) for a, b, c, (p, m) in
                    zip(D.apply(d0, 2), D.apply(d0, 0), D.apply(d1, 1), pts)])
    out["W"] = D.split(qw.solve([1.0] * len(pts)))
    out["_idx"] = D.idx
    out["_disc"] = D
    return out


def to_exact_pw(coefs, idx) -> list:
    return [KX.dyadic_round_poly(FL.to_exact_poly(c, idx)) for c in coefs]
