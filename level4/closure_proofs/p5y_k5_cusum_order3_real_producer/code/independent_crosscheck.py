"""Independent whole-cell enclosure of R'''_m for manufactured chain systems. NON-SCIENTIFIC.

Shares NO code with the engine (rung3_engine), the residual (rung3_residual) or the truth series
(manufactured_chain.expand): it reads only the system's raw coefficient data (A, B, a, b, centre). Standard library
only. Method:

    all objects as exact polynomials in t = e - centre:  h_1 = a, h_j = K h_(j-1), S_0 = b, S_r = J h_r, W = K^j S_r
    F_r = adj(I - K) S_r / det(I - K)          (explicit adjugate, n = 1 or 3)
    R_m = N / Q,  Q = det(I - K)               (frozen coefficient table, component 0)
    d/dt (P / Q^k) = (P' Q - k P Q') / Q^(k+1)  applied three times
    range on the cell: split [e0 - rho, e0 + rho] into pieces; on each, the exact Taylor form
        P(t_c + s) = sum_q p_q s^q,   |s| <= w   ->   p_0 +/- sum_(q>=1) |p_q| w^q
    and the quotient of the numerator and Q^4 intervals (refused if the Q interval contains 0).

Output: an exact rational interval containing R'''_m(e) for every e in the closed cell.
"""
from __future__ import annotations

from fractions import Fraction as Fr

# ------------------------------------------------------------------ scalar polynomials (coefficient lists)


def padd(p, q):
    n = max(len(p), len(q))
    return [(p[i] if i < len(p) else Fr(0)) + (q[i] if i < len(q) else Fr(0)) for i in range(n)]


def pscale(c, p):
    return [c * x for x in p]


def pmul(p, q):
    out = [Fr(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        if a:
            for j, b in enumerate(q):
                out[i + j] += a * b
    return out


def pder(p):
    return [i * p[i] for i in range(1, len(p))] or [Fr(0)]


def pshift(p, t0):
    """Coefficients of p(t0 + s) in s (Horner-style synthetic expansion)."""
    out = [Fr(0)]
    for c in reversed(p):
        out = padd(pmul(out, [t0, Fr(1)]), [c])
    return out


# ------------------------------------------------------------------ matrix / vector polynomials
def mat_poly(coeffs, n):
    return [[[coeffs[p][i][j] for p in range(len(coeffs))] for j in range(n)] for i in range(n)]


def vec_poly(coeffs, n):
    return [[coeffs[p][i] for p in range(len(coeffs))] for i in range(n)]


def mv(M, v):
    n = len(v)
    out = []
    for i in range(n):
        acc = [Fr(0)]
        for j in range(n):
            acc = padd(acc, pmul(M[i][j], v[j]))
        out.append(acc)
    return out


def det_adj(M):
    n = len(M)
    if n == 1:
        return M[0][0], [[[Fr(1)]]]
    if n != 3:
        raise ValueError("n must be 1 or 3")

    def minor(i, j):
        rows = [r for r in range(3) if r != i]
        cols = [c for c in range(3) if c != j]
        a, b = M[rows[0]][cols[0]], M[rows[0]][cols[1]]
        c, d = M[rows[1]][cols[0]], M[rows[1]][cols[1]]
        return padd(pmul(a, d), pscale(Fr(-1), pmul(b, c)))

    cof = [[pscale(Fr((-1) ** (i + j)), minor(i, j)) for j in range(3)] for i in range(3)]
    det = [Fr(0)]
    for j in range(3):
        det = padd(det, pmul(M[0][j], cof[0][j]))
    adj = [[cof[j][i] for j in range(3)] for i in range(3)]
    return det, adj


def coefficients(m):
    rows = [("F", r, 0, Fr(1, m)) for r in range(m)]
    rows += [("W", r, t - r - 1, Fr(1, t) - Fr(1, m)) for t in range(1, m) for r in range(t)]
    return rows


def rational_R(sysm, m):
    """(N, Q) with R_m(t) = N(t) / Q(t) exactly, t = e - centre."""
    n = sysm.n
    K = mat_poly(sysm.A, n)
    J = mat_poly(sysm.B, n)
    I_K = [[padd([Fr(1) if i == j else Fr(0)], pscale(Fr(-1), K[i][j])) for j in range(n)] for i in range(n)]
    Q, adj = det_adj(I_K)
    h = {1: vec_poly(sysm.a, n)}
    for j in range(2, 5):
        h[j] = mv(K, h[j - 1])
    S = {0: vec_poly(sysm.b, n)}
    for r in range(1, 5):
        S[r] = mv(J, h[r])
    N = [Fr(0)]
    for kind, r, j, c in coefficients(m):
        if kind == "F":
            N = padd(N, pscale(c, mv(adj, S[r])[0]))
        else:
            w = S[r]
            for _ in range(j):
                w = mv(K, w)
            N = padd(N, pscale(c, pmul(Q, w[0])))
    return N, Q


def third_derivative(N, Q):
    """(P, k) with R''' = P / Q^k."""
    P, k = N, 1
    dQ = pder(Q)
    for _ in range(3):
        P = padd(pmul(pder(P), Q), pscale(Fr(-k), pmul(P, dQ)))
        k += 1
    return P, k


def taylor_form(p, tc, w):
    c = pshift(p, tc)
    rad = sum((abs(c[q]) * w ** q for q in range(1, len(c))), Fr(0))
    return c[0] - rad, c[0] + rad


def ipow(lo, hi, k):
    cands = [lo ** k, hi ** k]
    if lo < 0 < hi and k % 2 == 0:
        return Fr(0), max(cands)
    return min(cands), max(cands)


def enclosure(sysm, e0: Fr, rho: Fr, m: int, *, pieces: int = 32) -> tuple[Fr, Fr]:
    N, Q = rational_R(sysm, m)
    P, k = third_derivative(N, Q)
    lo_t, hi_t = e0 - rho - sysm.c, e0 + rho - sysm.c
    w = (hi_t - lo_t) / (2 * pieces)
    best_lo = best_hi = None
    for i in range(pieces):
        tc = lo_t + (2 * i + 1) * w
        plo, phi = taylor_form(P, tc, w)
        qlo, qhi = taylor_form(Q, tc, w)
        if qlo <= 0 <= qhi:
            raise ArithmeticError("det(I - K) enclosure contains 0 on the cell")
        dlo, dhi = ipow(qlo, qhi, k)
        quots = [plo / dlo, plo / dhi, phi / dlo, phi / dhi]
        lo, hi = min(quots), max(quots)
        best_lo = lo if best_lo is None else min(best_lo, lo)
        best_hi = hi if best_hi is None else max(best_hi, hi)
    return best_lo, best_hi


def point_value(sysm, e: Fr, m: int) -> Fr:
    N, Q = rational_R(sysm, m)
    P, k = third_derivative(N, Q)
    t = e - sysm.c
    return pshift(P, t)[0] / pshift(Q, t)[0] ** k
