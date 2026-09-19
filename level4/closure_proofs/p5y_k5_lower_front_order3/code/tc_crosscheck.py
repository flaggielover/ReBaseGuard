"""Independent second calculation path for theorem TC (does NOT import tc_rule).

Written from THEOREM_TC.md in generic form instead of the expanded formulas of tc_rule:
    Taylor:      p_j = sum_{i=j..3} f_i rho^(i-j)/(i-j)!  +  rho^(4-j)/(4-j)! Env4          (f_0..f_3 = fF, fD, fH, fG)
    envelope:    Env4 = sigma4 + sum_{i=1..4} C(4,i) k_i sup_{|t|<=rho} ||Ftilde^(4-i)(t)||,
                 sup ||Ftilde^(n)|| <= sum_{l=n..3} s_l rho^(l-n)/(l-n)!                       (s_0..s_3 = sF, sD, sH, sG)
    sigma4:      r = 0 closed form; r >= 1 by the generic Leibniz tower of h_r^(n) and J_i
    resolvent:   rad = sum_{i=0..2} C(2,i) A_i p_(2-i)          (E'' = sum C(2,i) (d^i R) phi^(2-i))
    assembly:    frozen table c(m) re-derived from 1/t - 1/m; interval sum with nonnegative coefficients.
Returns exact Fractions; qualification requires equality with tc_rule on every fixture and on every real cell.
"""
from __future__ import annotations

from fractions import Fraction as Q
from math import comb, factorial


def _taylor_sup(vals: list, n: int, rho: Q) -> Q:
    return sum((vals[l] * rho ** (l - n) / factorial(l - n) for l in range(n, 4)), Q(0))


def _sigma4(r: int, k: list, j: list, s0: list) -> Q:
    if r == 0:
        return s0[4]
    tower = {}
    for n in range(5):
        tower[(1, n)] = Q(1) if n == 0 else s0[n - 1]
    for jj in range(2, 5):
        for n in range(5):
            tower[(jj, n)] = Q(1) if n == 0 else sum((comb(n, i) * k[i] * tower[(jj - 1, n - i)]
                                                      for i in range(n + 1)), Q(0))
    return sum((comb(4, i) * j[i] * tower[(r, 4 - i)] for i in range(5)), Q(0))


def object_bound(o: dict, rho: Q, k: list, j: list, s0: list, A: list, r: int) -> tuple[Q, Q]:
    f = [Q(o["delta_F"]) + Q(o["eps_src"][0]), Q(o["delta_D"]) + Q(o["eps_src"][1]),
         Q(o["delta_H"]) + Q(o["eps_src"][2]), Q(o["delta_G"]) + Q(o["eps_src"][3])]
    s = [Q(o["sup"][x]) for x in ("F", "D", "H", "G")]
    env = _sigma4(r, k, j, s0) + sum((comb(4, i) * k[i] * _taylor_sup(s, 4 - i, rho) for i in range(1, 5)), Q(0))
    p = [sum((f[i] * rho ** (i - jj) / factorial(i - jj) for i in range(jj, 4)), Q(0))
         + rho ** (4 - jj) / factorial(4 - jj) * env for jj in range(3)]
    rad = sum((comb(2, i) * A[i] * p[2 - i] for i in range(3)), Q(0))
    return rad, rho * Q(o["abs_G_at_a"]) + rad


def enclosure(rec: dict, A: dict, m: int) -> tuple[Q, Q]:
    rho = Q(rec["rho"])
    k = [Q(x) for x in rec["norms"]["k"]]
    j = [Q(x) for x in rec["norms"]["j"]]
    s0 = [Q(x) for x in rec["sup_S0"]]
    Av = [Q(A["A0"]), Q(A["A1"]), Q(A["A2"])]
    lo = hi = Q(0)
    for r in range(m):
        _, half = object_bound(rec["r"][str(r)], rho, k, j, s0, Av, r)
        a, b = (Q(x) for x in rec["r"][str(r)]["H_at_a"])
        lo += (a - half) / m
        hi += (b + half) / m
    for t in range(1, m):
        for r in range(t):
            c = Q(1, t) - Q(1, m)
            a, b = (Q(x) for x in rec["W2"][f"{r}:{t - r - 1}"])
            lo += c * a
            hi += c * b
    return lo, hi
