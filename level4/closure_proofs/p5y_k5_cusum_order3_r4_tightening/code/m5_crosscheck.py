"""R4-C independent cross-check of the exact manufactured derivatives used as truth for M5 (second code path).

The manufactured model (R1/R2): K(e) = sum_p A_p (e - c)^p, J(e) = sum_p B_p (e - c)^p, h_1 = sum_p a_p (e - c)^p,
S_0 = sum_p b_p (e - c)^p, h_j = K h_(j-1), S_r = J h_r, W_(r,j) = K W_(r,j-1), W_(r,0) = S_r, F_r = (I - K)^-1 S_r,
R_m(e) = sum_(rows of the coefficient table) c * X(e)[x0].
The exact truth (first_cell.true_derivs) uses the Taylor recurrence of manufactured_chain.expand. Here R_m^(n)(e) is
recomputed WITHOUT that recurrence: complex ball evaluation of the model (python-flint acb, 256 bits, acb_mat solve) on
a circle of radius r and the trapezoidal Cauchy integral
    R^(n)(e) ~ n! / r^n * mean_k R(e + r w_k) w_k^-n,     w_k = exp(2 pi i k / N),
whose aliasing error is below (r / r_sing)^N with r = r_sing / 8 chosen from a Neumann bound
(||(I - K(zeta))^-1|| finite for |zeta - e| <= 8 r). Agreement with the exact values and M5 >= max |R^(5)| are checked.
The coefficient table is re-typed here from the frozen specification (1/m for F_r, r < m; 1/t - 1/m for W_(r, t-r-1)).
"""
from __future__ import annotations

import math
from fractions import Fraction as Fr

from flint import acb, acb_mat, arb, ctx

NODES = 64


def _coefficients(m):
    rows = [("F", r, 0, Fr(1, m)) for r in range(m)]
    rows += [("W", r, t - r - 1, Fr(1, t) - Fr(1, m)) for t in range(1, m) for r in range(t)]
    return rows


def _q(x: Fr) -> acb:
    return acb(arb(x.numerator) / arb(x.denominator))


def _mat_poly(coeffs, t: acb) -> acb_mat:
    n = len(coeffs[0])
    out = acb_mat(n, n)
    tp = acb(1)
    for c in coeffs:
        out = out + acb_mat([[_q(x) for x in row] for row in c]) * tp
        tp = tp * t
    return out


def _vec_poly(coeffs, t: acb) -> acb_mat:
    n = len(coeffs[0])
    out = acb_mat(n, 1)
    tp = acb(1)
    for c in coeffs:
        out = out + acb_mat([[_q(x)] for x in c]) * tp
        tp = tp * t
    return out


def model_R(sysm, zeta: acb, m: int) -> acb:
    t = zeta - _q(sysm.c)
    K, J = _mat_poly(sysm.A, t), _mat_poly(sysm.B, t)
    n = K.nrows()
    h = {1: _vec_poly(sysm.a, t)}
    for j in range(2, 5):
        h[j] = K * h[j - 1]
    S = {0: _vec_poly(sysm.b, t)}
    for r in range(1, 5):
        S[r] = J * h[r]
    W = {}
    for r in range(4):
        W[(r, 0)] = S[r]
        for j in range(1, 4 - r):
            W[(r, j)] = K * W[(r, j - 1)]
    IK = acb_mat([[acb(int(i == j)) for j in range(n)] for i in range(n)]) - K
    total = acb(0)
    for kind, r, j, c in _coefficients(m):
        v = IK.solve(S[r]) if kind == "F" else W[(r, j)]
        total += _q(c) * v[0, 0]
    return total


def safe_radius(sysm, e: Fr) -> Fr:
    """r with 8 r inside the Neumann region: ||(I-K(e))^-1||_inf * sum_(p>=1) ||K^(p)(e)|| (8r)^p / p! < 1/2 is implied
    by 8 r <= min(1, 1 / (4 C_e sum_p ||A-shift_p||)); C_e from the exact inverse at e."""
    import manufactured_chain as MC
    ex = sysm.expand(e, 1)
    Kc = ex["K"]
    n = len(Kc[0])
    I_K = [[(Fr(1) if i == j else Fr(0)) - Kc[0][i][j] for j in range(n)] for i in range(n)]
    cols = [MC.solve(I_K, [Fr(int(i == j)) for i in range(n)]) for j in range(n)]
    Ce = max(sum(abs(cols[j][i]) for j in range(n)) for i in range(n))
    tail = sum((MC.mnorm(Kc[p]) for p in range(1, len(Kc))), Fr(0))
    s = min(Fr(1), 1 / (4 * Ce * max(tail, Fr(1))))
    return Fr(math.floor(s / 8 * 10 ** 12), 10 ** 12)


def cauchy_derivative(sysm, e: Fr, m: int, n: int) -> float:
    r = safe_radius(sysm, e)
    with ctx.workprec(256):
        acc = acb(0)
        for k in range(NODES):
            w = acb.exp_pi_i(acb(arb(2 * k) / arb(NODES)))
            acc += model_R(sysm, _q(e) + _q(r) * w, m) * w ** (-n)
        val = acc / NODES * math.factorial(n) / _q(r) ** n
        return float(val.real.mid())


def crosscheck(spec: dict, M5: dict, exact_R, grid, tol: float = 1e-6) -> dict:
    """exact_R(e, m, n) -> Fraction (the first_cell truth); M5 {m: float}; grid of Fractions."""
    import sigma_systems as SS
    sysm = SS.build(spec)
    worst, rows, ok = 0.0, [], True
    for m in (1, 2, 3, 5):
        cmax = 0.0
        for e in grid:
            for n in (3, 5):
                ex = float(exact_R(e, m, n))
                cz = cauchy_derivative(sysm, e, m, n)
                worst = max(worst, abs(ex - cz) / max(1.0, abs(ex)))
                if n == 5:
                    cmax = max(cmax, abs(cz))
        dominates = M5[m] >= cmax * (1 - tol)
        ok = ok and dominates
        rows.append({"m": m, "cauchy_max_abs_R5": cmax, "M5": M5[m], "M5_dominates": dominates})
    return {"id": spec["id"], "worst_relative_disagreement": worst, "rows": rows, "pass": ok and worst <= tol}
