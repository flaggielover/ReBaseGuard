"""C11RD -- RIGOROUS residual Taylor models over a box of states x a drift sub-block.

For candidate polynomials D0..D3 (exact dyadic rationals, band-piecewise; see c11rd_float) and a box
B of states in one band times a drift interval E_j = [e_c - de, e_c + de], this module returns Taylor
models (c11rd_tm) of the three residuals, valid for EVERY (x, e) in B x E_j:

    r0 = D0(e) - Khat_e D0(e) - h_1
    r1 = D1(e) - Khat_e D1(e) - Khat'_e D0(e) - h_1'
    r2 = D2(e) - Khat_e D2(e) - 2 Khat'_e D1(e) - Khat''_e D0(e) - h_1''

with the e-Taylor candidates (h = e - e_c)
    D0(e) = D0 + h D1 + h^2/2 D2 + h^3/6 D3,  D1(e) = D1 + h D2 + h^2/2 D3,  D2(e) = D2 + h D3.

Everything is closed form (theory/D1_D2_DERIVATION.md, sections 1-3): on each kernel piece the image
of z is affine in z and lies in ONE band, so the integrand is a polynomial in y = z + e times
phi^(i)(y) = (-1)^i He_i(y) phi(y); the piece integral is sum_r c_r(u) I_r(u) with I_r the centred
moments of c11rd_tm.centred_moments. Endpoints, images and sources are Taylor models in the box
variables u = (u_s, u_t, u_e) in [-1, 1]^3: s = s_c + ds u_s, theta = t_c + dt u_t, e = e_c + de u_e,
p = s (1 + theta)/2, m = s (1 - theta)/2 (bands 0-3), or (p, m) = (s, 0) / (0, s) (band 4 axes).

Nothing here reads a target value, an original certificate, a registry or a comparison.
"""
from __future__ import annotations

import math
from fractions import Fraction as F

import c11rd_tm as T

K, C = F(1, 2), F(11, 2)
NV = 3   # u_s, u_t, u_e


def _dy(x: F, bits: int = 30) -> F:
    """A nearby dyadic with 2^-bits denominator (only used as an expansion point: exactness of the
    final enclosure never depends on it)."""
    return F(math.floor(x * (1 << bits)), 1 << bits)


# ---------------------------------------------------------------------------------------------
# exact polynomial utilities
# ---------------------------------------------------------------------------------------------
def taylor_shift_2(poly: dict, P0: F, M0: F) -> dict:
    """f(P0 + a, M0 + b) = sum h[(r, t)] a^r b^t, exactly."""
    if not poly:
        return {}
    deg = max(i + j for i, j in poly)
    pP = [F(1)]
    pM = [F(1)]
    for _ in range(deg):
        pP.append(pP[-1] * P0)
        pM.append(pM[-1] * M0)
    out = {}
    for (i, j), c in poly.items():
        for r in range(i + 1):
            cr = c * math.comb(i, r) * pP[i - r]
            if cr == 0:
                continue
            for t in range(j + 1):
                v = cr * math.comb(j, t) * pM[j - t]
                if v:
                    out[(r, t)] = out.get((r, t), F(0)) + v
    return out


def taylor_shift_1(poly: dict, t0: F) -> dict:
    if not poly:
        return {}
    deg = max(poly)
    pw = [F(1)]
    for _ in range(deg):
        pw.append(pw[-1] * t0)
    out = {}
    for i, c in poly.items():
        for r in range(i + 1):
            v = c * math.comb(i, r) * pw[i - r]
            if v:
                out[r] = out.get(r, F(0)) + v
    return out


def restrict_axis(poly2: dict, axis: str) -> dict:
    """band polynomial restricted to p = 0 (axis 'm': variable m) or m = 0 (axis 'p': variable p)."""
    if axis == "m":
        return {j: c for (i, j), c in poly2.items() if i == 0}
    return {i: c for (i, j), c in poly2.items() if j == 0}


def he_shift(i: int, yc: F) -> list:
    """coefficients of (-1)^i He_i(yc + v) in v (exact)."""
    h = T.hermite(i)
    out = [F(0)] * (i + 1)
    for d, c in enumerate(h):
        for r in range(d + 1):
            out[r] += (-1) ** i * c * math.comb(d, r) * yc ** (d - r)
    return out


# ---------------------------------------------------------------------------------------------
# the box and its Taylor-model coordinates
# ---------------------------------------------------------------------------------------------
class Box:
    def __init__(self, band: int, s: tuple, e: tuple, theta: tuple | None = None,
                 axis: str | None = None, order: int = 4):
        self.band, self.s, self.e, self.theta, self.axis, self.N = band, s, e, theta, axis, order
        s0, s1 = F(s[0]), F(s[1])
        # a box must lie in ONE closed band (theory section 8): no box may straddle a kink line
        if band in (0, 1, 2, 3):
            if not (band <= s0 < s1 <= band + 1) or theta is None or \
                    not (-1 <= F(theta[0]) < F(theta[1]) <= 1):
                raise ValueError(f"box {s}, {theta} is not inside closed band {band}")
        elif band == 4:
            if not (4 <= s0 < s1 <= 5) or axis not in ("p", "m"):
                raise ValueError(f"box {s} / axis {axis} is not a band-4 axis segment")
        else:
            raise ValueError(f"unknown band {band}")
        if not F(e[0]) <= F(e[1]):
            raise ValueError("inverted drift interval")
        sc, ds = (s0 + s1) / 2, (s1 - s0) / 2
        ec, de = (F(e[0]) + F(e[1])) / 2, (F(e[1]) - F(e[0])) / 2
        self.ec, self.de = ec, de
        N = order
        S = T.TM.var(NV, N, 0, sc, ds)
        self.E = T.TM.var(NV, N, 2, ec, de)
        self.h = T.TM.var(NV, N, 2, 0, de)
        if band == 4:
            zero = T.TM.const(NV, N, 0)
            self.p, self.m = (S, zero) if axis == "p" else (zero, S)
        else:
            tc, dt = (F(theta[0]) + F(theta[1])) / 2, (F(theta[1]) - F(theta[0])) / 2
            TH = T.TM.var(NV, N, 1, tc, dt)
            half = S.scale(F(1, 2))
            self.p = half + half * TH
            self.m = half - half * TH
        self.S = self.p + self.m

    def split(self):
        """Bisect along s and (bands 0-3) theta."""
        s0, s1 = F(self.s[0]), F(self.s[1])
        sm = (s0 + s1) / 2
        if self.band == 4:
            return [Box(4, (s0, sm), self.e, axis=self.axis, order=self.N),
                    Box(4, (sm, s1), self.e, axis=self.axis, order=self.N)]
        t0, t1 = F(self.theta[0]), F(self.theta[1])
        tm = (t0 + t1) / 2
        return [Box(self.band, a, self.e, theta=b, order=self.N)
                for a in ((s0, sm), (sm, s1)) for b in ((t0, tm), (tm, t1))]

    def label(self) -> dict:
        d = {"band": self.band, "s": [str(F(self.s[0])), str(F(self.s[1]))],
             "e": [str(F(self.e[0])), str(F(self.e[1]))]}
        if self.band == 4:
            d["axis"] = self.axis
        else:
            d["theta"] = [str(F(self.theta[0])), str(F(self.theta[1]))]
        return d


# ---------------------------------------------------------------------------------------------
# kernel pieces with Taylor-model endpoints (z-variable), exactly as c11rd_float.pieces
# ---------------------------------------------------------------------------------------------
def pieces_tm(bx: Box) -> list:
    """[(z0, z1, tag)] with TM endpoints. Tags ('L', j) / ('R', j): image on the p = 0 / m = 0 axis
    in band j; ('M', k - 1): image on s' = s - 1 in band k - 1 (theory, Lemma 1)."""
    k, p, m, S = bx.band, bx.p, bx.m, bx.S
    N = bx.N
    cst = lambda x: T.TM.const(NV, N, F(x))
    out = []
    for j in range(max(0, k - 1), 5):
        if k >= 1 and j == k - 1:
            a_img = S - 1                      # image range starts at s - 1 (in [k-1, k])
        else:
            a_img = cst(j)
        b_img = cst(j + 1)
        out.append((m - K - b_img, m - K - a_img, ("L", j)))
        out.append((a_img + K - p, b_img + K - p, ("R", j)))
    if k >= 1:
        a2, a1 = K - p, m - K
        for i in range(k):
            z0 = a2 + (a1 - a2).scale(F(i, k))
            z1 = a2 + (a1 - a2).scale(F(i + 1, k))
            out.append((z0, z1, ("M", k - 1)))
    return out


# ---------------------------------------------------------------------------------------------
# one box: all kernel applications K^(i) D_j, i = 0..2, j = 0..3
# ---------------------------------------------------------------------------------------------
def _candidate_band_poly(cand: dict, j: int):
    return cand[j]


def kernel_box(bx: Box, cands: list, orders=(0, 1, 2), J: int = 34) -> dict:
    """{(i, j): TM of (Khat_e^(i) D_j)(x)} over the box."""
    N = bx.N
    # box-level shifts: P = p - K - e (+ yc), M = m - K + e (- yc); their non-constant parts
    Pbase_tm = bx.p - K - bx.E
    Mbase_tm = bx.m - K + bx.E
    Pb0 = _dy(Pbase_tm.split_const()[0])
    Mb0 = _dy(Mbase_tm.split_const()[0])
    dP = Pbase_tm - Pb0            # small TM (tiny constant + variation)
    dM = Mbase_tm - Mb0
    degmax = max(max((i + jj for (i, jj) in c[kk]), default=0) for c in cands
                 for kk in range(4)) if cands else 0
    degmax = max(degmax, max(max(c[("A", ax)], default=0) for c in cands for ax in ("p", "m")))
    powP, powM = dP.powers(degmax), dM.powers(degmax)
    prodPM = {}

    def pm(a, b):
        key = (a, b)
        if key not in prodPM:
            prodPM[key] = powP[a] * powM[b]
        return prodPM[key]

    result = {(i, jc): T.TM(NV, N, {}, 0) for i in orders for jc in range(len(cands))}
    for z0, z1, tag in pieces_tm(bx):
        y0, y1 = z0 + bx.E, z1 + bx.E
        c0 = (y0.split_const()[0] + y1.split_const()[0]) / 2
        yc = _dy(c0, 10)
        A, Bt = y0 - yc, y1 - yc
        # integrand coefficients (in v = y - yc) per candidate
        coeffs_per_cand = []
        for jc, cand in enumerate(cands):
            kind, jb = tag
            if kind in ("L", "R"):
                if jb == 4:
                    f1 = cand[("A", "m" if kind == "L" else "p")]
                else:
                    f1 = restrict_axis(cand[jb], "m" if kind == "L" else "p")
                if kind == "L":          # m' = (Mb0 - yc) + dM - v
                    t0, dT, sgn = Mb0 - yc, powM, -1
                else:                    # p' = (Pb0 + yc) + dP + v
                    t0, dT, sgn = Pb0 + yc, powP, 1
                sh = taylor_shift_1(f1, t0)
                deg = max(sh, default=0)
                cv = [T.TM(NV, N, {}, 0) for _ in range(deg + 1)]
                for i, a in sh.items():
                    for r in range(i + 1):
                        coef = a * math.comb(i, r) * (sgn ** r)
                        if coef:
                            cv[r] = cv[r] + dT[i - r].scale(coef)
            else:
                f2 = cand[jb]
                sh = taylor_shift_2(f2, Pb0 + yc, Mb0 - yc)   # a = dP + v, b = dM - v
                deg = max((i + jj for (i, jj) in sh), default=0)
                cv = [T.TM(NV, N, {}, 0) for _ in range(deg + 1)]
                for (i, jj), h in sh.items():
                    for r in range(i + 1):
                        cr = h * math.comb(i, r)
                        for t in range(jj + 1):
                            coef = cr * math.comb(jj, t) * (-1) ** t
                            if coef:
                                cv[r + t] = cv[r + t] + pm(i - r, jj - t).scale(coef)
            coeffs_per_cand.append(cv)
        rmax = max(len(cv) for cv in coeffs_per_cand) - 1
        kmax = rmax + max(orders)
        I = T.centred_moments(yc, A, Bt, kmax, J)
        for i in orders:
            hv = he_shift(i, yc)
            # Jr = int v^r (-1)^i He_i(yc + v) phi(yc + v) dv = sum_d hv[d] I[r + d]
            Jr = []
            for r in range(rmax + 1):
                acc = T.TM(NV, N, {}, 0)
                for d, hc in enumerate(hv):
                    if hc:
                        acc = acc + I[r + d].scale(hc)
                Jr.append(acc)
            for jc, cv in enumerate(coeffs_per_cand):
                acc = result[(i, jc)]
                for r, ctm in enumerate(cv):
                    acc = acc + ctm * Jr[r]
                result[(i, jc)] = acc
    return result


def state_values(bx: Box, cands: list) -> list:
    """[TM of D_j(x)] over the box (the candidate of the box's own band)."""
    N = bx.N
    p0, m0 = _dy(bx.p.split_const()[0]), _dy(bx.m.split_const()[0])
    dp, dm = bx.p - p0, bx.m - m0
    out = []
    if bx.band == 4:
        s0 = _dy(bx.S.split_const()[0])
        ds = bx.S - s0
        pw = None
        for cand in cands:
            f = cand[("A", bx.axis)]
            sh = taylor_shift_1(f, s0)
            deg = max(sh, default=0)
            if pw is None or len(pw) <= deg:
                pw = ds.powers(deg)
            acc = T.TM(NV, N, {}, 0)
            for i, a in sh.items():
                acc = acc + pw[i].scale(a)
            out.append(acc)
        return out
    deg = max(max((i + j for (i, j) in c[bx.band]), default=0) for c in cands)
    pp, pmm = dp.powers(deg), dm.powers(deg)
    cache = {}
    for cand in cands:
        sh = taylor_shift_2(cand[bx.band], p0, m0)
        acc = T.TM(NV, N, {}, 0)
        for (i, j), a in sh.items():
            key = (i, j)
            if key not in cache:
                cache[key] = pp[i] * pmm[j]
            acc = acc + cache[key].scale(a)
        out.append(acc)
    return out


def sources(bx: Box) -> list:
    """[h_1, h_1', h_1''] as TMs: h_1 = 1 - Phi(C - p + e) + Phi(m - C + e),
    h_1' = -phi(au) + phi(al), h_1'' = au phi(au) - al phi(al)."""
    au = C - bx.p + bx.E
    al = bx.m - C + bx.E
    Pu, Pl = T.Phi_tm(au), T.Phi_tm(al)
    pu, pl = T.phi_tm(au), T.phi_tm(al)
    h0 = (T.TM.const(NV, bx.N, 1) - Pu) + Pl
    h1 = pl - pu
    h2 = au * pu - al * pl
    return [h0, h1, h2]


def residuals_box(bx: Box, cands: list, J: int = 34) -> dict:
    """TMs of r0, r1, r2 over the box (cands = [D0, D1, D2, D3])."""
    KD = kernel_box(bx, cands, orders=(0, 1, 2), J=J)
    Dx = state_values(bx, cands)
    h = bx.h
    hp = h.powers(3)
    fact = [1, 1, 2, 6]

    def e_taylor(vals, k):
        """sum_{j >= k} h^(j-k)/(j-k)! vals[j]"""
        acc = T.TM(NV, bx.N, {}, 0)
        for j in range(k, 4):
            acc = acc + (hp[j - k] * vals[j]).scale(F(1, fact[j - k]))
        return acc

    def k_taylor(i, k):
        return e_taylor([KD[(i, j)] for j in range(4)], k)
    src = sources(bx)
    r0 = e_taylor(Dx, 0) - k_taylor(0, 0) - src[0]
    r1 = e_taylor(Dx, 1) - k_taylor(0, 1) - k_taylor(1, 0) - src[1]
    r2 = e_taylor(Dx, 2) - k_taylor(0, 2) - k_taylor(1, 1).scale(2) - k_taylor(2, 0) - src[2]
    return {"r0": r0, "r1": r1, "r2": r2, "Dx": Dx}
