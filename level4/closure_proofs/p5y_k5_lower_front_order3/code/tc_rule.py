"""Theorem TC (theorem/THEOREM_TC.md): the exact-rational rule. Pure functions, no I/O, no model evaluation.

Every input is a Fraction that is a certified UPPER bound (residuals, source errors, suprema, norms, A-constants, rho)
except the enclosure centres, which are exact intervals [lo, hi]. Every output is a valid bound under the theorem.

    env4      = sigma4 + 4 k1 sG + 6 k2 (sH + rho sG) + 4 k3 (sD + rho sH + rho^2 sG / 2)
                + k4 (sF + rho sD + rho^2 sH / 2 + rho^3 sG / 6)
    p0        = fF + rho fD + rho^2 fH / 2 + rho^3 fG / 6 + rho^4 env4 / 24      >= sup_cell ||phi||
    p1        = fD + rho fH + rho^2 fG / 2 + rho^3 env4 / 6                      >= sup_cell ||phi'||
    p2        = fH + rho fG + rho^2 env4 / 2                                     >= sup_cell ||phi''||
    rad       = A0 p2 + 2 A1 p1 + A2 p0            >= sup_cell |F_r''(e)(a) - Hhat(a) - (e - e0) Ghat(a)|
    half_r    = rho |Ghat(a)| + rad
    H_m       = sum_{r<m} (1/m) [Hhat_r(a).lo - half_r, Hhat_r(a).hi + half_r] + sum c(m) W_(r,j)
"""
from __future__ import annotations

from fractions import Fraction as F
from math import comb

M_VALUES = (1, 2, 3, 5)


class TCRefusal(ValueError):
    pass


def _nonneg(name: str, v) -> F:
    if not isinstance(v, F):
        raise TCRefusal(f"{name} must be an exact Fraction")
    if v < 0:
        raise TCRefusal(f"{name} must be a nonnegative upper bound")
    return v


def coefficients(m: int) -> list[tuple[str, int, int, F]]:
    """Frozen assembly table (ERROR_ALGEBRA section 4; assembly.coefficients): F_r 1/m (r < m), W_(r,t-r-1) 1/t - 1/m."""
    if m not in M_VALUES:
        raise TCRefusal(f"m = {m} outside the frozen scope")
    rows = [("F", r, 0, F(1, m)) for r in range(m)]
    rows += [("W", r, t - r - 1, F(1, t) - F(1, m)) for t in range(1, m) for r in range(t)]
    return rows


def sigma4_source(r: int, k: dict, j: dict, sup_S0: dict) -> F:
    """Upper bound of sup_cell ||S_r''''(e)|| (theorem TC, premise P3).

    r = 0: the frozen drift-aware closed-form bound sup_S0[4].
    r >= 1: S_r'''' = sum_i C(4,i) J_i h_r^(4-i) with the true-object tower
        ||h_1|| <= 1, ||h_1^(n)|| <= sup_S0[n-1] (h_1' = -S_0), ||h_j|| <= 1, ||h_j^(n)|| <= sum_i C(n,i) k_i ||h_(j-1)^(n-i)||.
    """
    for i in range(5):
        _nonneg(f"k_{i}", k[i])
        _nonneg(f"j_{i}", j[i])
    for n in range(5):
        _nonneg(f"sup_S0_{n}", sup_S0[n])
    if r == 0:
        return sup_S0[4]
    h = {1: {0: F(1), **{n: sup_S0[n - 1] for n in range(1, 5)}}}
    for jj in range(2, 5):
        h[jj] = {0: F(1)}
        for n in range(1, 5):
            h[jj][n] = sum((comb(n, i) * k[i] * h[jj - 1][n - i] for i in range(n + 1)), F(0))
    return sum((comb(4, i) * j[i] * h[r][4 - i] for i in range(5)), F(0))


def env4(sF: F, sD: F, sH: F, sG: F, k: dict, sigma4: F, rho: F) -> F:
    for name, v in (("sF", sF), ("sD", sD), ("sH", sH), ("sG", sG), ("sigma4", sigma4), ("rho", rho)):
        _nonneg(name, v)
    return (sigma4 + 4 * k[1] * sG + 6 * k[2] * (sH + rho * sG)
            + 4 * k[3] * (sD + rho * sH + rho ** 2 * sG / 2)
            + k[4] * (sF + rho * sD + rho ** 2 * sH / 2 + rho ** 3 * sG / 6))


def taylor_bounds(fF: F, fD: F, fH: F, fG: F, e4: F, rho: F) -> tuple[F, F, F]:
    for name, v in (("fF", fF), ("fD", fD), ("fH", fH), ("fG", fG), ("env4", e4), ("rho", rho)):
        _nonneg(name, v)
    p0 = fF + rho * fD + rho ** 2 * fH / 2 + rho ** 3 * fG / 6 + rho ** 4 * e4 / 24
    p1 = fD + rho * fH + rho ** 2 * fG / 2 + rho ** 3 * e4 / 6
    p2 = fH + rho * fG + rho ** 2 * e4 / 2
    return p0, p1, p2


def radius(A: dict, p: tuple[F, F, F]) -> F:
    for name in ("A0", "A1", "A2"):
        _nonneg(name, A[name])
    p0, p1, p2 = p
    return A["A0"] * p2 + 2 * A["A1"] * p1 + A["A2"] * p0


def object_half_width(rho: F, abs_G_at_a: F, rad: F) -> F:
    return _nonneg("rho", rho) * _nonneg("|G(a)|", abs_G_at_a) + _nonneg("rad", rad)


def per_r(cellrec: dict, r: int, A: dict) -> dict:
    """All TC quantities for object r of one producer cell record (exact Fractions)."""
    o = cellrec["r"][str(r)]
    rho = F(cellrec["rho"])
    k = {i: F(cellrec["norms"]["k"][i]) for i in range(5)}
    j = {i: F(cellrec["norms"]["j"][i]) for i in range(5)}
    sup_S0 = {n: F(cellrec["sup_S0"][n]) for n in range(5)}
    fF = F(o["delta_F"]) + F(o["eps_src"][0])
    fD = F(o["delta_D"]) + F(o["eps_src"][1])
    fH = F(o["delta_H"]) + F(o["eps_src"][2])
    fG = F(o["delta_G"]) + F(o["eps_src"][3])
    s4 = sigma4_source(r, k, j, sup_S0)
    e4 = env4(F(o["sup"]["F"]), F(o["sup"]["D"]), F(o["sup"]["H"]), F(o["sup"]["G"]), k, s4, rho)
    p = taylor_bounds(fF, fD, fH, fG, e4, rho)
    rad = radius(A, p)
    half = object_half_width(rho, F(o["abs_G_at_a"]), rad)
    return {"fF": fF, "fD": fD, "fH": fH, "fG": fG, "sigma4": s4, "env4": e4, "p": p, "rad": rad, "half": half}


def cell_enclosure(cellrec: dict, A: dict, m: int) -> tuple[F, F]:
    """The theorem-TC whole-cell enclosure of R''_m on one cell (exact interval)."""
    lo, hi = F(0), F(0)
    for kind, r, jj, c in coefficients(m):
        if kind == "F":
            q = per_r(cellrec, r, A)
            h_lo, h_hi = (F(x) for x in cellrec["r"][str(r)]["H_at_a"])
            if h_lo > h_hi:
                raise TCRefusal("inverted centre interval")
            lo += c * (h_lo - q["half"])
            hi += c * (h_hi + q["half"])
        else:
            w_lo, w_hi = (F(x) for x in cellrec["W2"][f"{r}:{jj}"])
            if w_lo > w_hi or c < 0:
                raise TCRefusal("inverted W enclosure or negative coefficient")
            lo += c * w_lo
            hi += c * w_hi
    return lo, hi
