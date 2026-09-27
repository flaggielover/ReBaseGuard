"""C1b UNTRUSTED float side: quadrature kernel, least-squares collocation, candidate generation (stdlib only).

Nothing here is load-bearing: every candidate it returns is re-checked by the exact machinery (c1b_kernel).
Quadrature: composite 10-node Gauss-Legendre on unit-length sub-intervals of each window piece.
Family (declaration D3): Chebyshev basis T_i(2p/5-1) T_j(2m/5-1), i+j <= d.  LS by Householder QR.
No side effects at import.
"""
from __future__ import annotations

import math
from fractions import Fraction as F

KF, CF = 0.5, 5.5
SQ2PI = math.sqrt(2 * math.pi)


def phif(t):
    return math.exp(-t * t / 2) / SQ2PI


def Phif(t):
    return 0.5 * math.erfc(-t / math.sqrt(2))


def _gl(n: int):
    xs, ws = [], []
    for i in range(1, n + 1):
        x = math.cos(math.pi * (i - 0.25) / (n + 0.5))
        for _ in range(100):
            p0, p1 = 1.0, x
            for k in range(2, n + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            dp = n * (x * p1 - p0) / (x * x - 1)
            dx = p1 / dp
            x -= dx
            if abs(dx) < 1e-16:
                break
        xs.append(x)
        ws.append(2 / ((1 - x * x) * dp * dp))
    return xs, ws


GLX, GLW = _gl(10)


def _pieces(p, m, taboo=True):
    """survival z-pieces of the window (taboo: atom window removed)."""
    ell, up = m - CF, CF - p
    if p + m >= 1:
        return [(ell, KF - p), (KF - p, m - KF), (m - KF, up)]
    return [(ell, m - KF), (KF - p, up)]


def nodes(p, m, e, taboo=True):
    """list of (weight*phi(z+e), S=-(z+e), p', m') and the atom mass (whole kernel)."""
    out = []
    extra = [m - KF - b for b in (1, 2, 3)] + [KF - p + b for b in (1, 2, 3)]   # strip-line crossings (D8)
    pcs = []
    for z0, z1 in _pieces(p, m):
        cuts = sorted([z0, z1] + [x for x in extra if z0 < x < z1])
        pcs.extend(zip(cuts, cuts[1:]))
    for z0, z1 in pcs:
        L = z1 - z0
        if L <= 0:
            continue
        ns = max(1, math.ceil(L))
        hs = L / ns
        for s in range(ns):
            a = z0 + s * hs
            for x, w in zip(GLX, GLW):
                z = a + (x + 1) * hs / 2
                ww = w * hs / 2 * phif(z + e)
                out.append((ww, -(z + e), max(0.0, p + z - KF), max(0.0, m - z - KF)))
    ka = 0.0
    if p + m <= 1:
        ka = Phif(KF - p + e) - Phif(m - KF + e)
    return out, ka


def basis_index(d: int):
    return [(i, j) for i in range(d + 1) for j in range(d + 1 - i)]


def cheb_all(x: float, d: int):
    t = [1.0, x]
    for _ in range(2, d + 1):
        t.append(2 * x * t[-1] - t[-2])
    return t[: d + 1]


def basis_vals(p, m, d, idx):
    tp = cheb_all(2 * p / 5 - 1, d)
    tm = cheb_all(2 * m / 5 - 1, d)
    return [tp[i] * tm[j] for (i, j) in idx]


def sample_set():
    pts = [(i / 10, j / 10) for i in range(41) for j in range(41 - i)]
    for k in range(1, 21):
        pts.append((4 + k / 20, 0.0))
        pts.append((0.0, 4 + k / 20))
    return pts


class Disc:
    """per (drift, degree): sample points, node lists, basis values at samples and at node states."""

    def __init__(self, e: float, d: int, pts=None):
        self.e, self.d = e, d
        self.idx = basis_index(d)
        self.pts = pts or sample_set()
        self.nod = []
        self.ka = []
        self.Bx = []
        for (p, m) in self.pts:
            nl, ka = nodes(p, m, e)
            self.nod.append(nl)
            self.ka.append(ka)
            self.Bx.append(basis_vals(p, m, d, self.idx))
        self.B00 = basis_vals(0.0, 0.0, d, self.idx)

    def feval(self, coef, p, m):
        tp = cheb_all(2 * p / 5 - 1, self.d)
        tm = cheb_all(2 * m / 5 - 1, self.d)
        return sum(c * tp[i] * tm[j] for c, (i, j) in zip(coef, self.idx))

    def apply(self, coef, j: int = 0):
        """K^(j) f at the samples for f = sum coef_k B_k (taboo)."""
        out = []
        for nl in self.nod:
            s = 0.0
            for (ww, S, pp, mm) in nl:
                s += ww * (S ** j) * self.feval(coef, pp, mm)
            out.append(s)
        return out

    def value(self, coef):
        return [sum(c * b for c, b in zip(coef, bx)) for bx in self.Bx]

    def matrix(self, whole: bool = False):
        n = len(self.idx)
        cols = [[0.0] * len(self.pts) for _ in range(n)]
        for i, (nl, bx) in enumerate(zip(self.nod, self.Bx)):
            acc = [0.0] * n
            for (ww, S, pp, mm) in nl:
                bv = basis_vals(pp, mm, self.d, self.idx)
                for k in range(n):
                    acc[k] += ww * bv[k]
            if whole:
                for k in range(n):
                    acc[k] += self.ka[i] * self.B00[k]
            for k in range(n):
                cols[k][i] = bx[k] - acc[k]
        return cols


class QR:
    """Householder QR of a column list (m x n), for repeated least-squares solves."""

    def __init__(self, cols):
        A = [c[:] for c in cols]
        self.m, self.n = len(A[0]), len(A)
        self.vs, self.R = [], []
        for k in range(self.n):
            x = A[k][k:]
            nx = math.sqrt(sum(t * t for t in x))
            alpha = -nx if x[0] >= 0 else nx
            v = x[:]
            v[0] -= alpha
            nv = math.sqrt(sum(t * t for t in v))
            v = [t / nv for t in v] if nv > 0 else v
            self.vs.append(v)
            for j in range(k, self.n):
                col = A[j]
                dt = sum(vi * col[k + i] for i, vi in enumerate(v))
                for i, vi in enumerate(v):
                    col[k + i] -= 2 * dt * vi
        self.R = [[A[j][i] for j in range(self.n)] for i in range(self.n)]

    def solve(self, b):
        y = b[:]
        for k, v in enumerate(self.vs):
            dt = sum(vi * y[k + i] for i, vi in enumerate(v))
            for i, vi in enumerate(v):
                y[k + i] -= 2 * dt * vi
        c = [0.0] * self.n
        for i in range(self.n - 1, -1, -1):
            s = y[i] - sum(self.R[i][j] * c[j] for j in range(i + 1, self.n))
            c[i] = s / self.R[i][i]
        return c


def h1f(p, m, e):
    return 1 - Phif(CF - p + e) + Phif(m - CF + e)


def h1pf(p, m, e):
    return -phif(CF - p + e) + phif(m - CF + e)


def h1ppf(p, m, e):
    return (CF - p + e) * phif(CF - p + e) - (m - CF + e) * phif(m - CF + e)


def solve_chain(e: float, d: int, log=print) -> dict:
    """float candidates (Chebyshev coefficient lists) for the declared triangular systems at drift e."""
    D = Disc(e, d)
    qr_t = QR(D.matrix(False))
    qr_w = QR(D.matrix(True))
    pts = D.pts
    ones = [1.0] * len(pts)
    out = {}
    out["b0"] = b0 = qr_t.solve(ones)
    k1b0 = D.apply(b0, 1)
    out["b1"] = b1 = qr_t.solve(k1b0)
    k2b0 = D.apply(b0, 2)
    k1b1 = D.apply(b1, 1)
    out["b2"] = qr_t.solve([a + 2 * b for a, b in zip(k2b0, k1b1)])
    out["xT"] = qr_t.solve(D.value(b0))
    out["d0"] = d0 = qr_t.solve([h1f(p, m, e) for p, m in pts])
    k1d0 = D.apply(d0, 1)
    out["d1"] = d1 = qr_t.solve([a + h1pf(p, m, e) for a, (p, m) in zip(k1d0, pts)])
    k2d0 = D.apply(d0, 2)
    k0d0 = D.apply(d0, 0)
    k1d1 = D.apply(d1, 1)
    out["d2"] = qr_t.solve([a - b + 2 * c + h1ppf(p, m, e) for a, b, c, (p, m) in zip(k2d0, k0d0, k1d1, pts)])
    out["W"] = qr_w.solve(ones)
    out["_idx"] = D.idx
    out["_B00"] = D.B00
    return out


def eval_at_atom(coef, B00):
    return sum(c * b for c, b in zip(coef, B00))


# ------------------------------------------------------------------------------------------ exact conversion
def _cheb_poly_in_p(n: int) -> list:
    """coefficients (low->high, Fractions) of T_n(2p/5 - 1) in powers of p."""
    # T_n in x
    T = [[F(1)], [F(0), F(1)]]
    for k in range(2, n + 1):
        a = [F(0)] + [2 * c for c in T[k - 1]]
        b = T[k - 2] + [F(0)] * (len(a) - len(T[k - 2]))
        T.append([x - y for x, y in zip(a, b)])
    tx = T[n]
    # substitute x = 2p/5 - 1
    out = [F(0)] * (n + 1)
    for i, c in enumerate(tx):
        if c == 0:
            continue
        # (2p/5 - 1)^i
        for k in range(i + 1):
            out[k] += c * math.comb(i, k) * F(2, 5) ** k * (-1) ** (i - k)
    return out


_CHEB_CACHE: dict = {}


def to_exact_poly(coef, idx) -> dict:
    """exact rational polynomial {(i, j, 0): c} in (p, m) of the float Chebyshev candidate (coefs -> exact dyadics)."""
    out: dict = {}
    for c, (i, j) in zip(coef, idx):
        cf = F(c)
        if cf == 0:
            continue
        if i not in _CHEB_CACHE:
            _CHEB_CACHE[i] = _cheb_poly_in_p(i)
        if j not in _CHEB_CACHE:
            _CHEB_CACHE[j] = _cheb_poly_in_p(j)
        for a, ca in enumerate(_CHEB_CACHE[i]):
            if ca == 0:
                continue
            for b, cb in enumerate(_CHEB_CACHE[j]):
                if cb == 0:
                    continue
                key = (a, b, 0)
                out[key] = out.get(key, 0) + cf * ca * cb
    return {k: v for k, v in out.items() if v != 0}
