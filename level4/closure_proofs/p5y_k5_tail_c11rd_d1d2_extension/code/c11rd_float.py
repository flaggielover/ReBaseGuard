"""C11RD -- the FLOAT candidate proposal (untrusted). Pure Python; no numpy, no original code.

It proposes band-piecewise polynomial approximations D0, D1, D2, D3 of

    d = Ghat h_1,  d' = Ghat(Khat' d + h_1'),  d'' = Ghat(Khat'' d + 2 Khat' d' + h_1''),
    d''' = Ghat(Khat''' d + 3 Khat'' d' + 3 Khat' d'' + h_1''')

at ONE drift value e, by least squares on collocation nodes. Nothing here is trusted: the proposal
is rounded to exact dyadic rationals and every property the certificate uses is then re-derived
rigorously by c11rd_residual (a bad proposal can only give a larger certified bound, never a false
one).

REPRESENTATION. Band k = 0..3 (k <= p + m <= k + 1, p, m >= 0): a bivariate polynomial of total degree
<= n in X = (p - c_k)/r_k, Y = (m - c_k)/r_k with c_k = r_k = (k + 1)/2, in the tensor Chebyshev basis
T_a(X) T_b(Y), a + b <= n. Band 4 (4 <= s <= 5; on the axes only): one univariate polynomial per axis
in x = 2 (s - 9/2), Chebyshev T_a(x), a <= n4. This module only FITS each band's polynomial on its
closed strip; it never decides which band owns a point. The certified candidate's ownership is the
UPPER-CLOSED convention of theory section 1 (band 0 = [0, 1], band k = (k, k + 1], band 4 = axis
points with s in (4, 5]), implemented by c11rd_certify.owner_band; a point on a band line is
fitted by both adjacent bands here, which affects only the tightness of the proposal.

THE KERNEL (docs/D1_D2_STATEMENT_AUDIT.md section 2; theory section 1). For x = (p, m) in band k:
  left arm   z in [m - C, z_L], image (0, m - z - K)       (z_L = m - K if s <= 1 else K - p)
  right arm  z in [z_R, C - p], image (p + z - K, 0)       (z_R = K - p if s <= 1 else m - K)
  middle     z in [K - p, m - K] (only if s > 1), image (p + z - K, m - z - K) on s' = s - 1
  (for s <= 1 the middle is the atom window, removed in Khat).
Khat^(i) f(x) = int f(image(z)) phi^(i)(z + e) dz over those pieces, phi^(i)(y) = (-1)^i He_i(y) phi(y).
"""
from __future__ import annotations

import math
from fractions import Fraction as F

KF, CF, HF = 0.5, 5.5, 5.0
SQ2PI = math.sqrt(2.0 * math.pi)


def phi(y: float) -> float:
    return math.exp(-0.5 * y * y) / SQ2PI


def Phi(y: float) -> float:
    return 0.5 * (1.0 + math.erf(y / math.sqrt(2.0)))


def he(i: int, y: float) -> float:
    if i == 0:
        return 1.0
    a, b = 1.0, y
    for n in range(1, i):
        a, b = b, y * b - n * a
    return b


def phi_d(i: int, y: float) -> float:
    """phi^(i)(y) = (-1)^i He_i(y) phi(y)."""
    return (-1) ** i * he(i, y) * phi(y)


# ---------------------------------------------------------------------------------------------
# Gauss-Legendre nodes (Newton on P_q), pure Python
# ---------------------------------------------------------------------------------------------
_GL = {}


def gauss_legendre(q: int):
    if q in _GL:
        return _GL[q]
    xs, ws = [], []
    for i in range(1, q + 1):
        x = math.cos(math.pi * (i - 0.25) / (q + 0.5))
        for _ in range(100):
            p0, p1 = 1.0, x
            for k in range(2, q + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            dp = q * (x * p1 - p0) / (x * x - 1.0)
            dx = p1 / dp
            x -= dx
            if abs(dx) < 1e-16:
                break
        xs.append(x)
        ws.append(2.0 / ((1.0 - x * x) * dp * dp))
    _GL[q] = (xs, ws)
    return xs, ws


def cheb_all(n: int, x: float) -> list:
    t = [1.0, x]
    for k in range(2, n + 1):
        t.append(2.0 * x * t[-1] - t[-2])
    return t[:n + 1]


# ---------------------------------------------------------------------------------------------
# basis bookkeeping
# ---------------------------------------------------------------------------------------------
class Basis:
    def __init__(self, n: int, n4: int):
        self.n, self.n4 = n, n4
        self.biv = [(a, b) for a in range(n + 1) for b in range(n + 1 - a)]
        self.index = {}
        idx = 0
        for k in range(4):
            for ab in self.biv:
                self.index[("B", k, ab)] = idx
                idx += 1
        for ax in ("p", "m"):
            for a in range(n4 + 1):
                self.index[("A", ax, a)] = idx
                idx += 1
        self.size = idx

    def eval_band(self, k: int, p: float, m: float) -> dict:
        if k == 4:
            ax = "p" if m == 0.0 else "m"
            T = cheb_all(self.n4, 2.0 * (p + m - 4.5))
            return {self.index[("A", ax, a)]: T[a] for a in range(self.n4 + 1)}
        c = r = (k + 1) / 2.0
        TX, TY = cheb_all(self.n, (p - c) / r), cheb_all(self.n, (m - c) / r)
        return {self.index[("B", k, ab)]: TX[ab[0]] * TY[ab[1]] for ab in self.biv}


def pieces(p: float, m: float, band: int):
    """[(z0, z1, tag)] for Khat at a state (p, m) of band `band`: the arms split at image band
    boundaries, the middle split into sub-pieces of width <= 1. Tags: ('L', j), ('R', j): image on
    the p = 0 / m = 0 axis in band j; ('M', band - 1): image on s' = s - 1."""
    s = p + m
    k = band
    out = []
    zl, zu = m - CF, CF - p
    if k == 0:
        zL, zR, lo_img = m - KF, KF - p, 0.0
    else:
        zL, zR, lo_img = KF - p, m - KF, s - 1.0
    for j in range(max(0, k - 1), 5):
        a_img, b_img = max(float(j), lo_img), float(j + 1)
        if b_img <= a_img:
            continue
        # left arm: m' = m - K - z in [a_img, b_img]
        z0, z1 = m - KF - b_img, m - KF - a_img
        out.append((max(z0, zl), min(z1, zL), ("L", j)))
        # right arm: p' = p + z - K in [a_img, b_img]
        z0, z1 = a_img + KF - p, b_img + KF - p
        out.append((max(z0, zR), min(z1, zu), ("R", j)))
    if k >= 1:
        a2, a1 = KF - p, m - KF
        nsub = max(1, k)
        for i in range(nsub):
            out.append((a2 + (a1 - a2) * i / nsub, a2 + (a1 - a2) * (i + 1) / nsub, ("M", k - 1)))
    return [(z0, z1, tag) for (z0, z1, tag) in out if z1 > z0]


def image(tag, p, m, z):
    kind = tag[0]
    if kind == "L":
        return 0.0, m - z - KF
    if kind == "R":
        return p + z - KF, 0.0
    return p + z - KF, m - z - KF


def kernel_rows(B: Basis, p: float, m: float, band: int, e: float, orders=(0, 1, 2, 3),
                q: int = 20):
    """{i: dense row} with row[j] = (Khat^(i) basis_j)(p, m)."""
    xs, ws = gauss_legendre(q)
    rows = {i: [0.0] * B.size for i in orders}
    for z0, z1, tag in pieces(p, m, band):
        half, mid = 0.5 * (z1 - z0), 0.5 * (z1 + z0)
        for x, w in zip(xs, ws):
            z = mid + half * x
            y = z + e
            base = w * half * phi(y)
            pp, mm = image(tag, p, m, z)
            vals = B.eval_band(tag[1], pp, mm)
            for i in orders:
                wi = base * (-1) ** i * he(i, y)
                row = rows[i]
                for idx, v in vals.items():
                    row[idx] += wi * v
    return rows


def h1_derivs(p: float, m: float, e: float, jmax: int = 3):
    """h_1^(j) for j = 0..jmax: h_1 = 1 - Phi(C - p + e) + Phi(m - C + e);
    h_1^(j) = -phi^(j-1)(C - p + e) + phi^(j-1)(m - C + e), j >= 1."""
    au, al = CF - p + e, m - CF + e
    out = [1.0 - Phi(au) + Phi(al)]
    for j in range(1, jmax + 1):
        out.append(-phi_d(j - 1, au) + phi_d(j - 1, al))
    return out


# ---------------------------------------------------------------------------------------------
# nodes and the least-squares solve (Householder QR, pure Python)
# ---------------------------------------------------------------------------------------------
def cheb_lobatto(n: int, a: float, b: float) -> list:
    if n == 1:
        return [0.5 * (a + b)]
    return [0.5 * (a + b) - 0.5 * (b - a) * math.cos(math.pi * i / (n - 1)) for i in range(n)]


def nodes(ns: int, nt: int, n4: int) -> list:
    """[(p, m, band)]: tensor Chebyshev-Lobatto nodes in (s, theta) per band, s = p + m,
    theta = (p - m)/s. Each band's grid spans its CLOSED strip, so a node on a band line s = k + 1 is
    fitted by band k (which owns it under the upper-closed convention, theory section 1) AND by band
    k + 1 (whose closed box also contains it). Fitting only; ownership is c11rd_certify.owner_band."""
    pts = []
    for k in range(4):
        for s in cheb_lobatto(ns, float(k), float(k + 1)):
            ths = [0.0] if s == 0.0 else cheb_lobatto(nt, -1.0, 1.0)
            for th in ths:
                p, m = max(0.0, s * (1 + th) / 2), max(0.0, s * (1 - th) / 2)
                pts.append((p, m, k))
    for s in cheb_lobatto(n4, 4.0, 5.0):
        pts.append((s, 0.0, 4))
        pts.append((0.0, s, 4))
    return pts


class HouseholderQR:
    """Factor A (m x n, list of rows) once; solve min ||A x - b|| for any b afterwards."""

    def __init__(self, A: list):
        m, n = len(A), len(A[0])
        self.m, self.n = m, n
        # column-major copy for speed
        cols = [[A[i][j] for i in range(m)] for j in range(n)]
        self.vs = []
        for j in range(n):
            cj = cols[j]
            normx = math.sqrt(sum(cj[i] * cj[i] for i in range(j, m)))
            if normx == 0.0:
                self.vs.append(None)
                continue
            alpha = -normx if cj[j] >= 0 else normx
            v = [0.0] * m
            v[j] = cj[j] - alpha
            for i in range(j + 1, m):
                v[i] = cj[i]
            vn = sum(v[i] * v[i] for i in range(j, m))
            if vn == 0.0:
                self.vs.append(None)
                continue
            self.vs.append((v, vn))
            for c in range(j, n):
                cc = cols[c]
                dot = 0.0
                for i in range(j, m):
                    dot += v[i] * cc[i]
                f = 2.0 * dot / vn
                if f:
                    for i in range(j, m):
                        cc[i] -= f * v[i]
        self.R = [[cols[c][j] for c in range(n)] for j in range(n)]

    def solve(self, b: list) -> list:
        b = b[:]
        m, n = self.m, self.n
        for j, vv in enumerate(self.vs):
            if vv is None:
                continue
            v, vn = vv
            dot = 0.0
            for i in range(j, m):
                dot += v[i] * b[i]
            f = 2.0 * dot / vn
            if f:
                for i in range(j, m):
                    b[i] -= f * v[i]
        x = [0.0] * n
        R = self.R
        for j in range(n - 1, -1, -1):
            acc = b[j]
            Rj = R[j]
            for c in range(j + 1, n):
                acc -= Rj[c] * x[c]
            x[j] = acc / Rj[j] if Rj[j] != 0.0 else 0.0
        return x


def propose(e: float, *, n: int, n4: int, ns: int, nt: int, q: int = 20) -> dict:
    """Float coefficient vectors c0..c3 (D0..D3) at drift e, and the discrete residual norms."""
    Bz = Basis(n, n4)
    pts = nodes(ns, nt, n4 + 3)
    rowsM, Ker, H = [], [], []
    for (p, m, k) in pts:
        kr = kernel_rows(Bz, p, m, k, e, q=q)
        row = [-v for v in kr[0]]
        for idx, v in Bz.eval_band(k, p, m).items():
            row[idx] += v
        rowsM.append(row)
        Ker.append(kr)
        H.append(h1_derivs(p, m, e))
    T = len(pts)

    def apply(i, c):
        return [sum(Ker[t][i][j] * c[j] for j in range(Bz.size)) for t in range(T)]

    qr = HouseholderQR(rowsM)
    b0 = [H[t][0] for t in range(T)]
    c0 = qr.solve(b0)
    k1c0 = apply(1, c0)
    b1 = [k1c0[t] + H[t][1] for t in range(T)]
    c1 = qr.solve(b1)
    k1c1, k2c0 = apply(1, c1), apply(2, c0)
    b2 = [2 * k1c1[t] + k2c0[t] + H[t][2] for t in range(T)]
    c2 = qr.solve(b2)
    k1c2, k2c1, k3c0 = apply(1, c2), apply(2, c1), apply(3, c0)
    b3 = [3 * k1c2[t] + 3 * k2c1[t] + k3c0[t] + H[t][3] for t in range(T)]
    c3 = qr.solve(b3)

    def resid(c, b):
        return max(abs(sum(rowsM[t][j] * c[j] for j in range(Bz.size)) - b[t]) for t in range(T))
    return {"basis": Bz, "coeffs": [c0, c1, c2, c3], "nodes": T, "unknowns": Bz.size,
            "discrete_residual": [resid(c0, b0), resid(c1, b1), resid(c2, b2), resid(c3, b3)]}


# ---------------------------------------------------------------------------------------------
# float -> EXACT candidate polynomials (dyadic rational coefficients)
# ---------------------------------------------------------------------------------------------
def _cheb_int(n: int) -> list:
    """Integer monomial coefficients of T_0..T_n."""
    T = [[1], [0, 1]]
    for k in range(2, n + 1):
        a = [0] + [2 * c for c in T[-1]]
        b = T[-2] + [0] * (len(a) - len(T[-2]))
        T.append([x - y for x, y in zip(a, b)])
    return T[:n + 1]


def dyadic(x: float, bits: int = 52) -> F:
    return F(round(x * (1 << bits)), 1 << bits)


def _affine_power_poly(cheb_coeffs: list, alpha: F, beta: F) -> dict:
    """sum_k c_k (alpha t + beta)^k as {power of t: Fraction}."""
    out = {}
    for k, ck in enumerate(cheb_coeffs):
        if ck == 0:
            continue
        for i in range(k + 1):
            v = ck * math.comb(k, i) * alpha ** i * beta ** (k - i)
            out[i] = out.get(i, F(0)) + v
    return out


def exact_candidate(Bz: Basis, c: list, bits: int = 52) -> dict:
    """{k: {(i, j): Fraction}} for bands 0..3 (monomials p^i m^j) and {('A', ax): {i: Fraction}} for
    the band-4 axis polynomials (monomials s^i). Coefficients are the float proposal rounded to
    2^-bits in the Chebyshev basis, then expanded EXACTLY."""
    Tn = _cheb_int(max(Bz.n, Bz.n4))
    out = {}
    for k in range(4):
        cc = F(k + 1, 2)
        poly = {}
        for (a, b) in Bz.biv:
            coef = dyadic(c[Bz.index[("B", k, (a, b))]], bits)
            if coef == 0:
                continue
            pa = _affine_power_poly(Tn[a], 1 / cc, F(-1))
            pb = _affine_power_poly(Tn[b], 1 / cc, F(-1))
            for i, u in pa.items():
                for j, v in pb.items():
                    poly[(i, j)] = poly.get((i, j), F(0)) + coef * u * v
        out[k] = {kk: v for kk, v in poly.items() if v != 0}
    for ax in ("p", "m"):
        poly = {}
        for a in range(Bz.n4 + 1):
            coef = dyadic(c[Bz.index[("A", ax, a)]], bits)
            if coef == 0:
                continue
            for i, u in _affine_power_poly(Tn[a], F(2), F(-9)).items():
                poly[i] = poly.get(i, F(0)) + coef * u
        out[("A", ax)] = {kk: v for kk, v in poly.items() if v != 0}
    return out
