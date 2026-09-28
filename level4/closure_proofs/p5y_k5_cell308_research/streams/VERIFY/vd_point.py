"""Stream D: a SECOND, independent pointwise rigorous evaluator of r(x) = W(x) - 1 - (K_e W)(x) at one exact point.

It shares no numerical routine with vd_verify.py (only the StripPW container is re-implemented here by reading the
same JSON layout):
  * exact fractions.Fraction throughout, with outward dyadic rounding at 2^-BITS only inside the special functions;
  * exp(-y): argument halving y/2^k <= 1/8, alternating Taylor series with Fraction terms, then k squarings;
  * Phi(u) = 1/2 + (1/sqrt(2 pi)) sum_n (-1)^n u^{2n+1} / (2^n n! (2n+1))  (alternating series, tail bound once the
    terms decrease), 1/sqrt(2 pi) from pi by the BBP-type
    series pi = sum_k 16^-k (4/(8k+1) - 2/(8k+4) - 1/(8k+5) - 1/(8k+6)) with its geometric tail bound;
  * breakpoints: generic. All z in the window where the image changes branch (clip points, strip crossings on the
    axes) are collected and sorted; on each sub-interval the branch and strip are decided from the image of the
    midpoint (no region bookkeeping); the integrand is expanded exactly as a polynomial in u = z + e;
  * int Q(u) phi(u) du = [c Phi(u) - A(u) phi(u)] with Q = c + u A - A' (exact back substitution), not moments.
"""
from __future__ import annotations

import importlib.util
import json
import math
from fractions import Fraction as F
from pathlib import Path

_NS = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("c308_quarantine", _NS / "code" / "c308_quarantine.py")
Q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(Q)
Q.install_import_guard()

K = F(1, 2)
C = F(11, 2)
BITS = 200
SC = 1 << BITS


def _down(x: F) -> F:
    return F((x.numerator * SC) // x.denominator, SC)


def _up(x: F) -> F:
    return F(-((-x.numerator * SC) // x.denominator), SC)


def _pi_bbp() -> tuple:
    s = F(0)
    N = 60
    for k in range(N):
        s += F(1, 16 ** k) * (F(4, 8 * k + 1) - F(2, 8 * k + 4) - F(1, 8 * k + 5) - F(1, 8 * k + 6))
    # every omitted term is positive and < 16^-k * 4/(8k+1); geometric tail
    tail = F(4, 8 * N + 1) * F(1, 16 ** N) * F(16, 15)
    return _down(s), _up(s + tail)


PI = _pi_bbp()
assert PI[0] < F(3141592653589794, 10 ** 15) and PI[1] > F(3141592653589793, 10 ** 15)


def _isqrt_bounds(x: F) -> tuple:
    """sqrt(x) enclosure at 2^-BITS."""
    n_lo = (x.numerator * SC * SC) // x.denominator
    n_hi = -((-x.numerator * SC * SC) // x.denominator)
    return F(math.isqrt(n_lo), SC), F(math.isqrt(n_hi) + 1, SC)


_S2PI = (_isqrt_bounds(2 * PI[0])[0], _isqrt_bounds(2 * PI[1])[1])
INV_S2PI = (_down(1 / _S2PI[1]), _up(1 / _S2PI[0]))


def exp_neg(y: F) -> tuple:
    """exp(-y), y >= 0 rational: g = y / 2^k <= 1/8, exact alternating Taylor sum, tail <= next term, then k
    outward-rounded squarings."""
    y = F(y)
    assert y >= 0
    k = 0
    while y / (1 << k) > F(1, 8):
        k += 1
    g = y / (1 << k)
    s, term, n = F(0), F(1), 0
    while True:
        s += term if n % 2 == 0 else -term
        n += 1
        term = term * g / n
        if term < F(1, SC * SC):
            break
    lo, hi = _down(s - term), _up(s + term)
    for _ in range(k):
        lo, hi = _down(lo * lo), _up(hi * hi)
    return max(lo, F(0)), hi


def phi(u: F) -> tuple:
    e = exp_neg(F(u) * F(u) / 2)
    return _down(e[0] * INV_S2PI[0]), _up(e[1] * INV_S2PI[1])


def Phi(u: F) -> tuple:
    """Phi(u) = 1/2 + (1/sqrt(2 pi)) sum_n (-1)^n a_n,  a_n = v^{2n+1} / (2^n n! (2n+1)), v = |u|.
    Exact partial sums; once a_{n+1} < a_n for all later n (v^2 < 2n+3 suffices), |tail| <= a_{n+1}."""
    u = F(u)
    v = abs(u)
    s = F(0)
    t = v                                   # v^{2n+1} / (2^n n!)
    n = 0
    while True:
        a_n = t / (2 * n + 1)
        s += a_n if n % 2 == 0 else -a_n
        t = t * v * v / (2 * (n + 1))
        a_next = t / (2 * n + 3)
        if v * v < 2 * n + 3 and a_next < F(1, SC * SC):
            break
        n += 1
    lo_s, hi_s = s - a_next, s + a_next
    if u >= 0:
        lo = F(1, 2) + lo_s * (INV_S2PI[0] if lo_s >= 0 else INV_S2PI[1])
        hi = F(1, 2) + hi_s * (INV_S2PI[1] if hi_s >= 0 else INV_S2PI[0])
    else:
        lo = F(1, 2) - hi_s * (INV_S2PI[1] if hi_s >= 0 else INV_S2PI[0])
        hi = F(1, 2) - lo_s * (INV_S2PI[0] if lo_s >= 0 else INV_S2PI[1])
    return max(_down(lo), F(0)), min(_up(hi), F(1))


# ---------------------------------------------------------------------------------------------- polynomials in u
def pmul(a: list, b: list) -> list:
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def ppow(a: list, n: int) -> list:
    out = [F(1)]
    for _ in range(n):
        out = pmul(out, a)
    return out


def padd(a: list, b: list) -> list:
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]


def antideriv(q: list) -> tuple:
    """q(u) = c + u A(u) - A'(u):  int q phi = c Phi - A phi."""
    n = len(q) - 1
    while n > 0 and q[n] == 0:
        n -= 1
    if n == 0:
        return q[0], []
    a = [F(0)] * (n + 1)                   # a[k] coefficient of u^k in A, deg A = n - 1
    a[n - 1] = q[n]
    for j in range(n - 1, 0, -1):          # u^j: a[j-1] - (j+1) a[j+1] = q[j]
        a[j - 1] = q[j] + (j + 1) * a[j + 1]
    c = q[0] + a[1]
    return c, a[:n]


def peval(a: list, x: F) -> F:
    s = F(0)
    for c in reversed(a):
        s = s * x + c
    return s


# ---------------------------------------------------------------------------------------------- the certificate
class PW:
    def __init__(self, obj: dict):
        self.BW = [F(b) for b in obj["BW"]]
        self.polys = [{(int(i), int(j)): F(c) for i, j, c in mons} for mons in obj["strips"]]

    def strip(self, t: F) -> int:
        for s in range(1, len(self.BW)):
            if t <= self.BW[s]:
                return s - 1
        raise ValueError

    def value(self, p: F, m: F) -> F:
        P = self.polys[self.strip(p + m)]
        return sum((c * p ** i * m ** j for (i, j), c in P.items()), F(0))

    def cut_levels(self) -> list:
        return list(self.BW)

    def poly_at(self, pp: F, mm: F) -> dict:
        return self.polys[self.strip(pp + mm)]


class PL:
    """P1 nodal function (layout VD_PL_NODAL/1): nodes (i/N, j/N); on each mesh cell the linear interpolant.
    Cell search is written here independently (barycentric test over the candidate cells around the point)."""

    def __init__(self, obj: dict):
        self.N = int(obj["N"])
        self.h = F(1, self.N)
        self.w = [[F(x) for x in col] for col in obj["w"]]

    def _node(self, i, j):
        if 0 <= i < len(self.w) and 0 <= j < len(self.w[i]):
            return self.w[i][j]
        return None

    def poly_at(self, pp: F, mm: F) -> dict:
        """linear polynomial {(1,0): b, (0,1): g, (0,0): a} of a cell containing (pp, mm)."""
        h = self.h
        i0, j0 = math.floor(pp / h), math.floor(mm / h)
        for i in (i0, i0 - 1):
            for j in (j0, j0 - 1):
                for tri in (((i, j), (i + 1, j), (i, j + 1)), ((i + 1, j), (i, j + 1), (i + 1, j + 1))):
                    vals = [self._node(a, b) for a, b in tri]
                    if any(v is None for v in vals):
                        continue
                    (x0, y0), (x1, y1), (x2, y2) = [(a * h, b * h) for a, b in tri]
                    det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
                    l1 = ((pp - x0) * (y2 - y0) - (x2 - x0) * (mm - y0)) / det
                    l2 = ((x1 - x0) * (mm - y0) - (pp - x0) * (y1 - y0)) / det
                    l0 = 1 - l1 - l2
                    if min(l0, l1, l2) >= 0:
                        # W = v0 l0 + v1 l1 + v2 l2, each l affine in (p, m)
                        v0, v1, v2 = vals
                        cb = ((v1 - v0) * (y2 - y0) - (v2 - v0) * (y1 - y0)) / det
                        cg = ((v2 - v0) * (x1 - x0) - (v1 - v0) * (x2 - x0)) / det
                        ca = v0 - cb * x0 - cg * y0
                        return {(0, 0): ca, (1, 0): cb, (0, 1): cg}
        # axis segments beyond t = 4
        if mm == 0:
            i = min(math.floor(pp / h), 5 * self.N - 1)
            v0, v1 = self.w[i][0], self.w[i + 1][0]
            cb = (v1 - v0) / h
            return {(0, 0): v0 - cb * i * h, (1, 0): cb}
        if pp == 0:
            j = min(math.floor(mm / h), 5 * self.N - 1)
            v0, v1 = self.w[0][j], self.w[0][j + 1]
            cg = (v1 - v0) / h
            return {(0, 0): v0 - cg * j * h, (0, 1): cg}
        raise ValueError(f"point {(pp, mm)} not in the mesh")

    def value(self, p: F, m: F) -> F:
        P = self.poly_at(F(p), F(m))
        return sum((c * F(p) ** i * F(m) ** j for (i, j), c in P.items()), F(0))

    def cut_levels(self) -> list:
        return [F(k, self.N) for k in range(5 * self.N + 1)]


def kernel_W(W: PW, e: F, p: F, m: F, omit_atom: bool = False) -> tuple:
    """rigorous enclosure of (K_e W)(p, m)."""
    Q.guard_drift(F(e))
    zlo, zhi = m - C, C - p
    cuts = {zlo, zhi, K - p, m - K}
    for b in W.cut_levels():
        cuts.add(m - K - b)          # image crosses m' = b (m-axis or interior line)
        cuts.add(b + K - p)          # image crosses p' = b (p-axis or interior line)
    cuts = sorted(z for z in cuts if zlo <= z <= zhi)
    lo_sum, hi_sum = F(0), F(0)
    for z0, z1 in zip(cuts, cuts[1:]):
        if z1 <= z0:
            continue
        zm = (z0 + z1) / 2
        pp, mm = p + zm - K, m - zm - K
        pos_p, pos_m = pp > 0, mm > 0
        if not pos_p and not pos_m:                           # atom window
            if omit_atom:
                continue
            poly_z = [W.value(F(0), F(0))]
        else:
            ap = [p - K, F(1)] if pos_p else [F(0)]             # p'(z) as polynomial in z
            am = [m - K, F(-1)] if pos_m else [F(0)]
            poly_z = [F(0)]
            for (i, j), c in W.poly_at(pp if pos_p else F(0), mm if pos_m else F(0)).items():
                poly_z = padd(poly_z, [c * x for x in pmul(ppow(ap, i), ppow(am, j))])
        # shift to u = z + e: Q(u) = poly_z(u - e)
        q = [F(0)]
        for k, c in enumerate(poly_z):
            if c:
                q = padd(q, [c * x for x in ppow([-e, F(1)], k)])
        cc, A = antideriv(q)
        u0, u1 = z0 + e, z1 + e
        P0, P1 = Phi(u0), Phi(u1)
        f0, f1 = phi(u0), phi(u1)
        A0, A1 = peval(A, u0) if A else F(0), peval(A, u1) if A else F(0)
        # c (Phi1 - Phi0) - (A1 phi1 - A0 phi0)
        dP = (P1[0] - P0[1], P1[1] - P0[0])
        t1 = sorted([cc * dP[0], cc * dP[1]])
        t2 = sorted([A1 * f1[0], A1 * f1[1]])
        t3 = sorted([A0 * f0[0], A0 * f0[1]])
        lo_sum += t1[0] - t2[1] + t3[0]
        hi_sum += t1[1] - t2[0] + t3[1]
    return lo_sum, hi_sum


def residual(W: PW, e, p, m, omit_atom: bool = False) -> tuple:
    e, p, m = F(e), F(p), F(m)
    Q.guard_drift(e)
    kw = kernel_W(W, e, p, m, omit_atom)
    w = W.value(p, m)
    return w - 1 - kw[1], w - 1 - kw[0]


def load(path) -> PW:
    return PW(json.loads(Path(path).read_text()))


def make(obj: dict):
    return PL(obj) if obj.get("format") == "VD_PL_NODAL/1" else PW(obj)
