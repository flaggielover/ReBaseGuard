"""reviewA0: independent FLOAT evaluator of (K_e w)(x) for a P1 w on the C2b mesh, written from the model only.

Model (c2b_common docstring): state (p, m) in R = {p+m <= 4} u {p in [0,5], m = 0} u {p = 0, m in [0,5]};
increment z with z + e ~ N(0,1); window z in [m - C, C - p] (C = K + H); next state (max(0, p+z-K), max(0, m-z-K));
K = 1/2, H = 5, atom a = (0,0).  Decomposition in the increment z (my own):
  p-axis piece  z > max(K-p, m-K):  p' = p+z-K in (max(0,s-1), H],  density phi(p' - p + K + e)
  m-axis piece  z < min(K-p, m-K):  m' = m-z-K in (max(0,s-1), H],  density phi(m' - m + K - e)
  interior      s > 1, z in (K-p, m-K): p' in (0, s-1), m' = s-1-p', density phi(p' - p + K + e)
  atom          s <= 1, z in [m-K, K-p]: mass Phi(K-p+e) - Phi(m-K+e), value w(0,0)
Each piece is split at every mesh line crossed by the path, w is linear between breakpoints, and each linear piece
is integrated against phi in closed form (erfc differences).  Float only: NOT rigorous; used as an independent check.
"""
from __future__ import annotations

import math

K, H, C = 0.5, 5.0, 5.5
SQ2 = math.sqrt(2.0)
IS2PI = 1.0 / math.sqrt(2.0 * math.pi)


def dPhi(ta, tb):
    """Phi(tb) - Phi(ta) for ta <= tb, without catastrophic cancellation in the tails."""
    if ta >= 0.0:
        return 0.5 * (math.erfc(ta / SQ2) - math.erfc(tb / SQ2))
    if tb <= 0.0:
        return 0.5 * (math.erfc(-tb / SQ2) - math.erfc(-ta / SQ2))
    return 1.0 - 0.5 * math.erfc(-ta / SQ2) - 0.5 * math.erfc(tb / SQ2)


def phi(t):
    return IS2PI * math.exp(-0.5 * t * t)


def lin_int(a, b, wa, wb, c):
    """integral over u in [a, b] of the linear function through (a, wa), (b, wb) times phi(u + c)."""
    if b <= a:
        return 0.0
    beta = (wb - wa) / (b - a)
    ta, tb = a + c, b + c
    return (wa - beta * ta) * dPhi(ta, tb) + beta * (phi(ta) - phi(tb))


class P1:
    def __init__(self, Wf, N):
        self.W, self.N, self.h = Wf, N, 1.0 / N

    def axis_p(self, p):
        N = self.N
        x = p * N
        i = min(max(int(math.floor(x)), 0), 5 * N - 1)
        f = x - i
        return self.W[i][0] * (1.0 - f) + self.W[i + 1][0] * f

    def axis_m(self, m):
        N = self.N
        y = m * N
        j = min(max(int(math.floor(y)), 0), 5 * N - 1)
        f = y - j
        return self.W[0][j] * (1.0 - f) + self.W[0][j + 1] * f

    def at(self, p, m):
        if m <= 0.0:
            return self.axis_p(max(p, 0.0))
        if p <= 0.0:
            return self.axis_m(m)
        N, W = self.N, self.W
        x, y = p * N, m * N
        i, j = int(math.floor(x)), int(math.floor(y))
        if i + j > 4 * N - 1:          # rounding at the p+m = 4 boundary
            if i > 0 and x - i < y - j:
                j = 4 * N - 1 - i
            else:
                i = 4 * N - 1 - j
        fx, fy = x - i, y - j
        if fx + fy <= 1.0 or i + j + 1 >= 4 * N:
            return W[i][j] * (1.0 - fx - fy) + W[i + 1][j] * fx + W[i][j + 1] * fy
        return W[i + 1][j] * (1.0 - fy) + W[i][j + 1] * (1.0 - fx) + W[i + 1][j + 1] * (fx + fy - 1.0)

    def _axis_integral(self, which, lo, c):
        h, N = self.h, self.N
        f = self.axis_p if which == "p" else self.axis_m
        k0 = int(math.floor(lo * N)) + 1
        pts = [lo] + [k * h for k in range(k0, 5 * N + 1) if k * h > lo]
        if pts[-1] < H:
            pts.append(H)
        tot = 0.0
        vals = [f(u) for u in pts]
        for r in range(len(pts) - 1):
            tot += lin_int(pts[r], pts[r + 1], vals[r], vals[r + 1], c)
        return tot

    def Kw(self, e, p, m):
        s = p + m
        lo = max(0.0, s - 1.0)
        c3 = -p + K + e
        c2 = -m + K - e
        tot = self._axis_integral("p", lo, c3) + self._axis_integral("m", lo, c2)
        if s > 1.0:
            sp = s - 1.0
            h, N = self.h, self.N
            br = {0.0, sp}
            for k in range(1, int(math.floor(sp * N)) + 1):
                u = k * h
                if 0.0 < u < sp:
                    br.add(u)
                v = sp - k * h
                if 0.0 < v < sp:
                    br.add(v)
            pts = sorted(br)
            vals = [self.at(u, max(sp - u, 0.0)) for u in pts]
            for r in range(len(pts) - 1):
                tot += lin_int(pts[r], pts[r + 1], vals[r], vals[r + 1], c3)
        else:
            tot += dPhi(m - K + e, K - p + e) * self.W[0][0]
        return tot


def cells(N):
    """My own enumeration of the tiling of R: (kind, vertices as (i, j))."""
    out = []
    for i in range(4 * N):
        for j in range(4 * N - i):
            out.append(("L", ((i, j), (i + 1, j), (i, j + 1))))
            if i + j + 2 <= 4 * N:
                out.append(("U", ((i + 1, j), (i, j + 1), (i + 1, j + 1))))
    for i in range(4 * N, 5 * N):
        out.append(("AXP", ((i, 0), (i + 1, 0))))
    for j in range(4 * N, 5 * N):
        out.append(("AXM", ((0, j), (0, j + 1))))
    return out


BARY3 = [(1 / 3, 1 / 3, 1 / 3), (1 / 2, 1 / 2, 0.0), (1 / 2, 0.0, 1 / 2), (0.0, 1 / 2, 1 / 2),
         (2 / 3, 1 / 6, 1 / 6), (1 / 6, 2 / 3, 1 / 6), (1 / 6, 1 / 6, 2 / 3),
         (1 / 6, 5 / 12, 5 / 12), (5 / 12, 1 / 6, 5 / 12), (5 / 12, 5 / 12, 1 / 6),
         (0.9, 0.05, 0.05), (0.05, 0.9, 0.05), (0.05, 0.05, 0.9)]
BARY2 = [(0.5, 0.5), (0.25, 0.75), (0.75, 0.25), (0.1, 0.9), (0.9, 0.1)]


def sample_points(N):
    h = 1.0 / N
    for kind, vs in cells(N):
        lam = BARY3 if len(vs) == 3 else BARY2
        for l in lam:
            p = sum(li * v[0] for li, v in zip(l, vs)) * h
            m = sum(li * v[1] for li, v in zip(l, vs)) * h
            yield kind, vs, p, m


def residual_scan(Wint, Qbits, N, e, direction, max_points=None):
    """direction 'super': r = w - 1 - Kw ; 'sub': r = 1 + Kw - w.  Returns summary (min r, count negative)."""
    sc = 2.0 ** -Qbits
    Wf = [[x * sc for x in col] for col in Wint]
    ev = P1(Wf, N)
    ef = float(e)
    worst, nneg, n, worst_at = None, 0, 0, None
    neg_cells = set()
    for kind, vs, p, m in sample_points(N):
        k = ev.Kw(ef, p, m)
        w = ev.at(p, m)
        r = (w - 1.0 - k) if direction == "super" else (1.0 + k - w)
        n += 1
        if r < 0:
            nneg += 1
            neg_cells.add(vs)
        if worst is None or r < worst:
            worst, worst_at = r, (kind, vs[0], p, m)
        if max_points and n >= max_points:
            break
    return {"points": n, "min_residual": worst, "n_negative": nneg, "n_negative_cells": len(neg_cells),
            "worst_at": worst_at}
