"""C2b float point evaluator of Psi_w(s, y) = (K_e w)(p, m) for a P1 nodal vector, at ARBITRARY (s, y).

Used only for VALIDATION of the certificate's ingredients (finite-difference checks of the Hessian bounds,
off-node spot checks).  Independent of the certificate code path: it evaluates w by P1 point location and integrates
each linear piece exactly against phi with float Phi/phi, by the region decomposition T1..T4 of STRATEGY.md s5.
"""
from __future__ import annotations

import math

import c2b_common as CM

KF, HF = 0.5, 5.0


def w_at(W, N, p, m):
    """P1 interpolant on the anti-diagonal triangulation (and the axis segments beyond s = 4)."""
    h = 1.0 / N
    if m <= 1e-15 and p > 4.0:
        i = min(int(p * N), 5 * N - 1)
        f = p * N - i
        return W[i][0] + f * (W[i + 1][0] - W[i][0])
    if p <= 1e-15 and m > 4.0:
        j = min(int(m * N), 5 * N - 1)
        f = m * N - j
        return W[0][j] + f * (W[0][j + 1] - W[0][j])
    i, j = int(p * N), int(m * N)
    fp, fm = p * N - i, m * N - j
    if i + j >= 4 * N:          # on the hypotenuse s = 4 or rounding: step back into the triangle
        if fp + fm < 1e-12:
            if fp < 1e-12 and fm < 1e-12:
                return W[i][j]
        i, j = (i - 1, j) if i > 0 else (i, j - 1)
        fp, fm = p * N - i, m * N - j
    if fp + fm <= 1.0:
        return W[i][j] + fp * (W[i + 1][j] - W[i][j]) + fm * (W[i][j + 1] - W[i][j])
    return (W[i + 1][j + 1] - (1 - fp) * (W[i + 1][j + 1] - W[i][j + 1])
            - (1 - fm) * (W[i + 1][j + 1] - W[i + 1][j]))


def _lin_int(f0, f1, u0, u1, y):
    """int_{u0}^{u1} (linear f with f(u0)=f0, f(u1)=f1) phi(u - y) du, exact in terms of Phi/phi."""
    if u1 <= u0:
        return 0.0
    t0, t1 = u0 - y, u1 - y
    M0 = CM.Phi_float(t1) - CM.Phi_float(t0)
    M1 = CM.phi_float(t0) - CM.phi_float(t1)       # int t phi
    slope = (f1 - f0) / (u1 - u0)
    # f(u) = f0 + slope (u - u0) = f0 + slope (t - t0)
    return (f0 - slope * t0) * M0 + slope * M1


def _axis_int(vals, N, lo, hi, y):
    h = 1.0 / N
    total = 0.0
    k0 = int(lo * N)
    for k in range(max(0, k0), 5 * N):
        u0, u1 = k * h, (k + 1) * h
        a, b = max(u0, lo), min(u1, hi)
        if b <= a:
            continue
        fa = vals[k] + (a - u0) * N * (vals[k + 1] - vals[k])
        fb = vals[k] + (b - u0) * N * (vals[k + 1] - vals[k])
        total += _lin_int(fa, fb, a, b, y)
    return total


def psi(W, N, s, y, full=True):
    """Psi_w(s, y) with the drift absorbed in y = p - K - e; eta = s - y - 1."""
    a = [W[k][0] for k in range(5 * N + 1)]
    b = [W[0][k] for k in range(5 * N + 1)]
    eta = s - y - 1.0
    A = max(0.0, s - 1.0)
    v = _axis_int(a, N, A, HF, y) + _axis_int(b, N, A, HF, eta)
    if s > 1.0:
        sp = s - 1.0
        # breakpoints of u -> w(u, sp - u): vertical u = k h, horizontal u = sp - k h
        pts = {0.0, sp}
        for k in range(0, 5 * N + 1):
            if 0 < k / N < sp:
                pts.add(k / N)
            if 0 < sp - k / N < sp:
                pts.add(sp - k / N)
        pts = sorted(pts)
        for u0, u1 in zip(pts, pts[1:]):
            f0 = w_at(W, N, u0, max(0.0, sp - u0))
            f1 = w_at(W, N, u1, max(0.0, sp - u1))
            v += _lin_int(f0, f1, u0, u1, y)
    elif full:
        v += W[0][0] * (CM.Phi_float(-y) - CM.Phi_float(eta))
    return v


def K_at(W, N, p, m, e, full=True):
    return psi(W, N, p + m, p - KF - e, full)


def direct_quadrature(W, N, p, m, e, full=True, n=4000):
    """Brute-force midpoint quadrature over z of w(next(z)) phi(z+e): an independent sanity check (slow)."""
    lo, hi = m - 5.5, 5.5 - p
    dz = (hi - lo) / n
    tot = 0.0
    for r in range(n):
        z = lo + (r + 0.5) * dz
        pn, mn = max(0.0, p + z - KF), max(0.0, m - z - KF)
        if not full and pn == 0.0 and mn == 0.0:
            continue
        tot += w_at(W, N, pn, mn) * CM.phi_float(z + e) * dz
    return tot
