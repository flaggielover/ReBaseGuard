"""SRK UNTRUSTED float side (stdlib only): geometry-parametrized collocation for (I - K_e) V = rhs.

PORT NOTICE: geometry-parametrized port of the reviewed C1b float module
(``p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/c1b_float.py``; Disc, QR, Chebyshev family D3,
composite 10-node Gauss-Legendre).  Nothing here is load-bearing: every candidate is re-checked exactly by
``srk_certify`` through ``srk_kernel``.
"""
from __future__ import annotations

import math
from fractions import Fraction as F

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


class FGeom:
    def __init__(self, h, k):
        self.h, self.k = float(h), float(k)
        self.c = self.h + self.k
        self.tri = self.h - 2 * self.k
        self.reg = 2 * self.k


def _pieces(fg: FGeom, p, m):
    ell, up = m - fg.c, fg.c - p
    if p + m >= fg.reg:
        return [(ell, fg.k - p), (fg.k - p, m - fg.k), (m - fg.k, up)]
    return [(ell, m - fg.k), (fg.k - p, up)]


def nodes(fg: FGeom, p, m, e):
    """list of (weight*phi(z+e), p', m') over the taboo window and the atom mass (whole kernel)."""
    out = []
    for z0, z1 in _pieces(fg, p, m):
        L = z1 - z0
        if L <= 0:
            continue
        ns = max(1, math.ceil(2 * L))
        hs = L / ns
        for s in range(ns):
            a = z0 + s * hs
            for x, w in zip(GLX, GLW):
                z = a + (x + 1) * hs / 2
                out.append((w * hs / 2 * phif(z + e), max(0.0, p + z - fg.k), max(0.0, m - z - fg.k)))
    ka = 0.0
    if p + m <= fg.reg:
        ka = Phif(fg.k - p + e) - Phif(m - fg.k + e)
    return out, ka


def basis_index(d: int):
    return [(i, j) for i in range(d + 1) for j in range(d + 1 - i)]


def cheb_all(x: float, d: int):
    t = [1.0, x]
    for _ in range(2, d + 1):
        t.append(2 * x * t[-1] - t[-2])
    return t[: d + 1]


def basis_vals(fg: FGeom, p, m, d, idx):
    tp = cheb_all(2 * p / fg.h - 1, d)
    tm = cheb_all(2 * m / fg.h - 1, d)
    return [tp[i] * tm[j] for (i, j) in idx]


def sample_set(fg: FGeom, n_tri: int = 40, n_axis: int = 20):
    pts = []
    for i in range(n_tri + 1):
        for j in range(n_tri + 1 - i):
            pts.append((fg.tri * i / n_tri, fg.tri * j / n_tri))
    for kk in range(1, n_axis + 1):
        t = fg.tri + (fg.h - fg.tri) * kk / n_axis
        pts.append((t, 0.0))
        pts.append((0.0, t))
    return pts


class Disc:
    def __init__(self, fg: FGeom, e: float, d: int):
        self.fg, self.e, self.d = fg, e, d
        self.idx = basis_index(d)
        self.pts = sample_set(fg)
        self.nod, self.ka, self.Bx = [], [], []
        for (p, m) in self.pts:
            nl, ka = nodes(fg, p, m, e)
            self.nod.append(nl)
            self.ka.append(ka)
            self.Bx.append(basis_vals(fg, p, m, d, self.idx))
        self.B00 = basis_vals(fg, 0.0, 0.0, d, self.idx)

    def matrix(self, whole: bool = True):
        n = len(self.idx)
        cols = [[0.0] * len(self.pts) for _ in range(n)]
        for i, (nl, bx) in enumerate(zip(self.nod, self.Bx)):
            acc = [0.0] * n
            for (ww, pp, mm) in nl:
                bv = basis_vals(self.fg, pp, mm, self.d, self.idx)
                for kk in range(n):
                    acc[kk] += ww * bv[kk]
            if whole:
                for kk in range(n):
                    acc[kk] += self.ka[i] * self.B00[kk]
            for kk in range(n):
                cols[kk][i] = bx[kk] - acc[kk]
        return cols


class QR:
    """Householder QR of a column list (m x n), for repeated least-squares solves (port of C1b QR)."""

    def __init__(self, cols):
        A = [c[:] for c in cols]
        self.m, self.n = len(A[0]), len(A)
        self.vs = []
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


def _cheb_poly(n: int, h: F) -> list:
    """coefficients (low -> high) of T_n(2p/h - 1) in powers of p."""
    T = [[F(1)], [F(0), F(1)]]
    for k in range(2, n + 1):
        a = [F(0)] + [2 * c for c in T[k - 1]]
        b = T[k - 2] + [F(0)] * (len(a) - len(T[k - 2]))
        T.append([x - y for x, y in zip(a, b)])
    tx = T[n]
    out = [F(0)] * (n + 1)
    for i, c in enumerate(tx):
        if c == 0:
            continue
        for k in range(i + 1):
            out[k] += c * math.comb(i, k) * (F(2) / h) ** k * (-1) ** (i - k)
    return out


def to_exact_poly(coef, idx, h) -> dict:
    """exact rational polynomial {(i, j, 0): c} in (p, m) of a float Chebyshev candidate (coefs -> exact dyadics)."""
    h = F(h)
    cache: dict = {}
    out: dict = {}
    for c, (i, j) in zip(coef, idx):
        cf = F(c)
        if cf == 0:
            continue
        for n in (i, j):
            if n not in cache:
                cache[n] = _cheb_poly(n, h)
        for a, ca in enumerate(cache[i]):
            if ca == 0:
                continue
            for b, cb in enumerate(cache[j]):
                if cb == 0:
                    continue
                key = (a, b, 0)
                out[key] = out.get(key, 0) + cf * ca * cb
    return {k: v for k, v in out.items() if v != 0}


_HE_ROOTS = {0: [], 1: [0.0], 2: [-1.0, 1.0], 3: [-math.sqrt(3), 0.0, math.sqrt(3)],
             4: [-math.sqrt(3 + math.sqrt(6)), -math.sqrt(3 - math.sqrt(6)), math.sqrt(3 - math.sqrt(6)),
                 math.sqrt(3 + math.sqrt(6))]}


def he_abs_integral_float(i: int, a: float, b: float, n: int = 400) -> float:
    """float int_a^b |He_i(v)| phi(v) dv (composite GL split at the roots of He_i; untrusted, proposals/tests)."""
    if b <= a:
        return 0.0
    cuts = [a] + [r for r in _HE_ROOTS[i] if a < r < b] + [b]
    s = 0.0
    for lo0, hi0 in zip(cuts, cuts[1:]):
        m = max(1, int(n * (hi0 - lo0) / (b - a)) + 1)
        hs = (hi0 - lo0) / m
        for kk in range(m):
            lo = lo0 + kk * hs
            for x, w in zip(GLX, GLW):
                v = lo + (x + 1) * hs / 2
                he = [1.0, v]
                for t in range(2, i + 1):
                    he.append(v * he[-1] - (t - 1) * he[-2])
                s += w * hs / 2 * abs(he[i]) * phif(v)
    return s
