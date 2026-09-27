"""Stream A mechanism study -- float CUSUM kernel machinery (NON-CERTIFIED; stdlib only).

Model (c11_certifier.py:21-43, re-derived here, not imported): state (p, m), K = 1/2, H = 5,
C = K + H = 11/2; increment z with z + e ~ N(0, 1); alarm-free window z in [m - C, C - p];
(p', m') = (max(0, p + z - K), max(0, m - z - K)); atom a = (0, 0); the atom window (both arms
clamp to zero) is z in [m - K, K - p], non-empty iff p + m < 1.  K_e = Khat_e + k_a (x) delta_a.

Two float evaluators:

* ``Nystrom(N, e)``: piecewise-linear Nystrom discretisation of K_e on the reachable set
  R = axes U {p + m <= 4} (grid h = 1/N; the m-axis, the p-axis, and interior level lines
  p + m = k h).  From (p, m) the image of the window is: the m-axis (p' = 0), the level line
  p' + m' = p + m - 1 (both positive), the p-axis (m' = 0) and, if p + m < 1, the atom.  All
  integration limits fall on grid nodes, and each linear segment times phi is integrated in closed
  form (Phi, phi), so the only error is the O(h^2) interpolation of the unknown function.  The atom
  piece is stored separately, so Khat_e = P - atom column exactly as in Lemma K.
* ``kernel_poly(w, p, m, e, atom_removed)``: (K_e w)(p, m) for a bivariate polynomial w, exactly
  in float (Gaussian moments on each smooth piece) -- the continuous kernel, used for the pointwise
  linear-family screen and the box/panel emulation.

Every entry point that takes a drift calls ov_quarantine.guard_drift (amendment 1: no operator
quantity inside [6/5, 13/5] or its mirror).  Labels: all numbers produced here are FLOAT,
NON-CERTIFIED.
"""
from __future__ import annotations

import math
import sys
from array import array
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()

KK = 0.5
HH = 5.0
CC = 5.5
SQ2 = math.sqrt(2.0)
ISQ2PI = 1.0 / math.sqrt(2.0 * math.pi)


def guard(e_lo, e_hi=None) -> None:
    Q.guard_drift(Fr(e_lo), None if e_hi is None else Fr(e_hi))


def phi(u: float) -> float:
    return ISQ2PI * math.exp(-0.5 * u * u)


def pmass(ua: float, ub: float) -> float:
    """int_ua^ub phi, ua <= ub, computed without catastrophic cancellation in either tail."""
    if ua >= 0.0:
        return 0.5 * (math.erfc(ua / SQ2) - math.erfc(ub / SQ2))
    if ub <= 0.0:
        return 0.5 * (math.erfc(-ub / SQ2) - math.erfc(-ua / SQ2))
    return 0.5 * (math.erf(ub / SQ2) - math.erf(ua / SQ2))


# ----------------------------------------------------------------------------------- Nystrom
class Nystrom:
    """Piecewise-linear Nystrom discretisation of K_e on R, grid h = 1/N (N even)."""

    def __init__(self, N: int, e: float):
        guard(e)
        if N % 2:
            raise ValueError("N must be even so that K = 1/2 is a grid point")
        self.N, self.e, self.h = N, float(e), 1.0 / N
        self._cache: dict = {}
        self.K2 = N // 2          # K in grid units
        self.C2 = 11 * N // 2     # C in grid units
        self.H2 = 5 * N
        self.L2 = 4 * N           # interior levels p + m <= 4
        # node table
        self.coords: list = [(0, 0)]
        self.index: dict = {(0, 0): 0}
        for j in range(1, self.H2 + 1):
            self._add((0, j))
        for i in range(1, self.H2 + 1):
            self._add((i, 0))
        for k in range(2, self.L2 + 1):
            for i in range(1, k):
                self._add((i, k - i))
        self.n = len(self.coords)
        self._build()

    def _add(self, c):
        self.index[c] = len(self.coords)
        self.coords.append(c)

    def _pm(self, t: int) -> tuple:
        """(Phi-ish handle, phi) at u = t h + e, cached."""
        r = self._cache.get(t)
        if r is None:
            u = t * self.h + self.e
            r = (u, phi(u))
            self._cache[t] = r
        return r

    def _seg(self, ta: int, tb: int):
        """Weights (W_at_ta, W_at_tb) of int over u in [ta h + e, tb h + e] of the linear
        interpolant with node values at the two ends (ta, tb adjacent lattice points, any order)."""
        u0, ph0 = self._pm(ta)
        u1, ph1 = self._pm(tb)
        lo, hi = (u0, u1) if u0 < u1 else (u1, u0)
        I0 = pmass(lo, hi)
        I1 = (ph0 - ph1) if u0 < u1 else (ph1 - ph0)
        W1 = (I1 - u0 * I0) / (u1 - u0)
        return I0 - W1, W1

    def line_node(self, level: int, q: int) -> int:
        """Node on the level line p + m = level at p = q (grid units)."""
        if q == 0:
            return self.index[(0, level)]
        if q == level:
            return self.index[(level, 0)]
        return self.index[(q, level - q)]

    def _build(self):
        N, K2, C2, H2 = self.N, self.K2, self.C2, self.H2
        self.rows_c: list = []
        self.rows_w: list = []
        self.atom = array("d", [0.0] * self.n)
        self.h1 = array("d", [0.0] * self.n)
        self.rowsum = array("d", [0.0] * self.n)
        for r, (pi, mi) in enumerate(self.coords):
            acc: dict = {}

            def put(node, w):
                acc[node] = acc.get(node, 0.0) + w
            s = pi + mi
            az, bz = K2 - pi, mi - K2          # z-kinks (grid units): p' > 0 iff z > az; m' > 0 iff z < bz
            zlo, zhi = mi - C2, C2 - pi        # alarm-free window
            # the window mass (for h1) as one exact interval
            win = pmass(zlo * self.h + self.e, zhi * self.h + self.e)
            self.h1[r] = 1.0 - win
            if s >= N:
                # m-axis: y = m' in [s - N, H2] ; u = (m - K - y) + e  -> t = mi - K2 - y
                for y in range(s - N, H2):
                    w0, w1 = self._seg(mi - K2 - y, mi - K2 - (y + 1))
                    put(self._axis_m(y), w0)
                    put(self._axis_m(y + 1), w1)
                # interior level s - N: q = p' in [0, s - N]; u = (q - p + K) + e
                lev = s - N
                for q in range(0, lev):
                    w0, w1 = self._seg(q - pi + K2, q + 1 - pi + K2)
                    put(self.line_node(lev, q), w0)
                    put(self.line_node(lev, q + 1), w1)
                # p-axis: y = p' in [s - N, H2]; u = (y - p + K) + e
                for y in range(s - N, H2):
                    w0, w1 = self._seg(y - pi + K2, y + 1 - pi + K2)
                    put(self._axis_p(y), w0)
                    put(self._axis_p(y + 1), w1)
            else:
                for y in range(0, H2):
                    w0, w1 = self._seg(mi - K2 - y, mi - K2 - (y + 1))
                    put(self._axis_m(y), w0)
                    put(self._axis_m(y + 1), w1)
                self.atom[r] = pmass(bz * self.h + self.e, az * self.h + self.e)
                for y in range(0, H2):
                    w0, w1 = self._seg(y - pi + K2, y + 1 - pi + K2)
                    put(self._axis_p(y), w0)
                    put(self._axis_p(y + 1), w1)
            cols = sorted(acc)
            self.rows_c.append(array("i", cols))
            self.rows_w.append(array("d", [acc[c] for c in cols]))
            self.rowsum[r] = sum(acc.values()) + self.atom[r]

    def _axis_m(self, y: int) -> int:
        return self.index[(0, y)]

    def _axis_p(self, y: int) -> int:
        return self.index[(y, 0)]

    # ----------------------------------------------------------------- operators
    def apply(self, x, atom_removed: bool) -> array:
        """(P x) with P = Khat (atom_removed) or K (whole kernel)."""
        out = array("d", [0.0] * self.n)
        x0 = x[0]
        for r in range(self.n):
            s = 0.0
            for c, w in zip(self.rows_c[r], self.rows_w[r]):
                s += w * x[c]
            if not atom_removed:
                s += self.atom[r] * x0
            out[r] = s
        return out

    def solve(self, rhs, atom_removed: bool, tol: float = 1e-13, maxit: int = 2000):
        """x = (I - P)^{-1} rhs by BiCGSTAB (float); returns (x, iterations, final relative residual)."""
        n = self.n

        def A(v):
            pv = self.apply(v, atom_removed)
            return array("d", [v[i] - pv[i] for i in range(n)])
        x = array("d", rhs)                     # initial guess x = rhs
        Ax = A(x)
        r = array("d", [rhs[i] - Ax[i] for i in range(n)])
        rh = array("d", r)
        rho = alpha = om = 1.0
        v = array("d", [0.0] * n)
        p = array("d", [0.0] * n)
        bn = math.sqrt(sum(b * b for b in rhs)) or 1.0
        it = 0
        res = math.sqrt(sum(a * a for a in r)) / bn
        while res > tol and it < maxit:
            it += 1
            rho_new = sum(a * b for a, b in zip(rh, r))
            beta = (rho_new / rho) * (alpha / om)
            rho = rho_new
            p = array("d", [r[i] + beta * (p[i] - om * v[i]) for i in range(n)])
            v = A(p)
            alpha = rho / sum(a * b for a, b in zip(rh, v))
            s = array("d", [r[i] - alpha * v[i] for i in range(n)])
            t = A(s)
            tt = sum(a * a for a in t)
            om = sum(a * b for a, b in zip(t, s)) / tt if tt > 0 else 0.0
            x = array("d", [x[i] + alpha * p[i] + om * s[i] for i in range(n)])
            r = array("d", [s[i] - om * t[i] for i in range(n)])
            res = math.sqrt(sum(a * a for a in r)) / bn
        # true residual
        Ax = A(x)
        tr = math.sqrt(sum((rhs[i] - Ax[i]) ** 2 for i in range(n))) / bn
        return x, it, tr

    def truth(self) -> dict:
        """v = (I-K)^-1 1, t = (I-Khat)^-1 1, d = (I-Khat)^-1 h1, hv = (I-Khat)^-1 k_a (all at nodes)."""
        ones = array("d", [1.0] * self.n)
        v, iv, rv = self.solve(ones, False)
        t, it, rt = self.solve(ones, True)
        d, idd, rd = self.solve(self.h1, True)
        hv, ih, rh = self.solve(self.atom, True)
        return {"v": v, "t": t, "d": d, "hv": hv,
                "iters": {"v": iv, "t": it, "d": idd, "hv": ih},
                "residuals": {"v": rv, "t": rt, "d": rd, "hv": rh}}

    def xy(self, r: int) -> tuple:
        pi, mi = self.coords[r]
        return pi * self.h, mi * self.h


# ----------------------------------------------------------------------------------- continuous kernel
def _moments(A: float, B: float, jmax: int) -> list:
    """M_j = int_A^B u^j phi(u) du, j <= jmax (float, recurrence of c11_certifier.py:42-43)."""
    pa, pb = phi(A), phi(B)
    M = [pmass(A, B)]
    if jmax >= 1:
        M.append(pa - pb)
    for j in range(2, jmax + 1):
        M.append((j - 1) * M[j - 2] + A ** (j - 1) * pa - B ** (j - 1) * pb)
    return M


def _shifted(a: float, b: float, e: float, jmax: int) -> list:
    """int_a^b z^j phi(z+e) dz via u = z + e."""
    Ms = _moments(a + e, b + e, jmax)
    out = []
    for j in range(jmax + 1):
        acc = 0.0
        for i in range(j + 1):
            acc += math.comb(j, i) * ((-e) ** (j - i)) * Ms[i]
        out.append(acc)
    return out


def _pow_lin(c0: float, c1: float, n: int) -> list:
    return [math.comb(n, k) * c0 ** (n - k) * c1 ** k for k in range(n + 1)]


def kernel_poly(w: dict, p: float, m: float, e: float, atom_removed: bool = False) -> float:
    """(K_e w)(p, m) or (Khat_e w)(p, m), w = {(i, j): coeff} meaning sum c p^i m^j (float)."""
    guard(e)
    ell, up = m - CC, CC - p
    if up <= ell:
        return 0.0
    al, be = KK - p, m - KK
    cuts = sorted({ell, up} | {z for z in (al, be) if ell < z < up})
    tot = 0.0
    for lo, hi in zip(cuts, cuts[1:]):
        if hi <= lo:
            continue
        mid = 0.5 * (lo + hi)
        ppos, mpos = (p + mid - KK) > 0, (m - mid - KK) > 0
        if atom_removed and not ppos and not mpos:
            continue                       # the atom piece
        zc: dict = {}
        for (i, j), c in w.items():
            if (i and not ppos) or (j and not mpos):
                continue
            a = _pow_lin(p - KK, 1.0, i) if i else [1.0]
            b = _pow_lin(m - KK, -1.0, j) if j else [1.0]
            for s_, av in enumerate(a):
                for t_, bv in enumerate(b):
                    zc[s_ + t_] = zc.get(s_ + t_, 0.0) + c * av * bv
        if not zc:
            continue
        Ms = _shifted(lo, hi, e, max(zc))
        tot += sum(c * Ms[d] for d, c in zc.items())
    return tot


def h1_cont(p: float, m: float, e: float) -> float:
    guard(e)
    return 1.0 - pmass(m - CC + e, CC - p + e)


def reachable_grid(n: int) -> list:
    """States of R on an n x n grid of [0,5]^2 (the pointwise-screen grid of c11r_boxdata.py:284-286)."""
    ax = [5.0 * i / (n - 1) for i in range(n)]
    return [(p, m) for p in ax for m in ax if (p + m <= 4.0) or p == 0.0 or m == 0.0]
