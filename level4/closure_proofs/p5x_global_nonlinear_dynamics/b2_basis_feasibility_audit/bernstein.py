"""Exact monomial <-> Bernstein conversion and certified cell restriction.

Used ONLY for rigorous range certification.  The scientific candidate, the R6
kernel and the xi transform are untouched.
"""
from __future__ import annotations
import sys
from math import comb
from pathlib import Path
from flint import arb

_NS = Path(__file__).resolve().parents[1]
for _p in (_NS / "sr_full_cell_prototype", _NS / "compute_optimization_r6_minimal_evaluator",
           _NS / "compute_optimization_r4_xi_reformulation",
           Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def mono_to_bern_matrix(n: int):
    """M[k][i] = C(k,i)/C(n,i) for i<=k, else 0.   x^i = sum_k M[k][i] B_k^n(x)."""
    return [[arb(comb(k, i)) / arb(comb(n, i)) if i <= k else arb(0)
             for i in range(n + 1)] for k in range(n + 1)]


def mono_to_bern_2d(c):
    """beta = M c M^T  (exact tensor conversion on [0,1]^2)."""
    n = len(c) - 1
    M = mono_to_bern_matrix(n)
    tmp = [[sum((M[k][i] * c[i][j] for i in range(n + 1)), arb(0)) for j in range(n + 1)]
           for k in range(n + 1)]
    return [[sum((tmp[k][j] * M[l][j] for j in range(n + 1)), arb(0)) for l in range(n + 1)]
            for k in range(n + 1)]


def bern_eval(beta, x: arb, y: arb) -> arb:
    """Evaluate the tensor Bernstein form directly (for equality checking)."""
    n = len(beta) - 1
    bx = [arb(comb(n, i)) * x ** i * (arb(1) - x) ** (n - i) for i in range(n + 1)]
    by = [arb(comb(n, j)) * y ** j * (arb(1) - y) ** (n - j) for j in range(n + 1)]
    return sum((beta[i][j] * bx[i] * by[j] for i in range(n + 1) for j in range(n + 1)), arb(0))


def _sub_1d(b, t0: arb, t1: arb):
    """de Casteljau restriction of univariate Bernstein coefficients to [t0,t1]."""
    n = len(b) - 1

    def right(bb, t):                      # keep [t,1], reparameterised to [0,1]
        cur = list(bb)
        out = []
        for _ in range(n + 1):
            out.append(cur[-1])
            cur = [cur[i] * (arb(1) - t) + cur[i + 1] * t for i in range(len(cur) - 1)]
        return out[::-1]

    def left(bb, t):                       # keep [0,t]
        cur = list(bb)
        out = []
        for _ in range(n + 1):
            out.append(cur[0])
            cur = [cur[i] * (arb(1) - t) + cur[i + 1] * t for i in range(len(cur) - 1)]
        return out

    b = right(b, t0)
    s = (t1 - t0) / (arb(1) - t0)
    return left(b, s)


def restrict_cell(beta, x0: arb, x1: arb, y0: arb, y1: arb):
    """Exact Bernstein coefficients of the same polynomial on the sub-box."""
    n = len(beta) - 1
    rows = [_sub_1d([beta[i][j] for i in range(n + 1)], x0, x1) for j in range(n + 1)]
    cols = [_sub_1d([rows[j][i] for j in range(n + 1)], y0, y1) for i in range(n + 1)]
    return [[cols[i][j] for j in range(n + 1)] for i in range(n + 1)]


def hull_range(beta):
    """Convex-hull range bound: min beta <= p <= max beta on the (sub)box."""
    lo = min((float(b.lower()) for r in beta for b in r))
    hi = max((float(b.upper()) for r in beta for b in r))
    return lo, hi
