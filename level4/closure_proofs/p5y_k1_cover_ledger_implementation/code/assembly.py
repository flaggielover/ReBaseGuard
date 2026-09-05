"""Exact all-m certified interval assembly and the whole-cell curvature M_R2.

Frozen ERROR_ALGEBRA section 4, with c_(m,t) = 1/t - 1/m and W_(r,j) = K^j S_r:

    R_m^(k) = (1/m) sum_(r<m) F_r^(k)(x0)
              + sum_(t=1)^(m-1) c_(m,t) sum_(r<t) W_(r,t-r-1)^(k)(x0)

The SAME exact positive rational coefficients serve k = 0, 1, 2; only the objects
change. k=0 at e0 gives R_interval, k=1 at e0 gives D_interval, k=2 UNIFORMLY ON
THE CELL gives R2_interval, and M_R2 = mag(R2_interval).

This is the raw-variable reformulation: there is NO leading "+e" term. In the
g-variable system R = g + e; here the unknown is F = R itself and the e-linear
content of the reward has already cancelled, so adding e would double count.
`assemble` refuses a leading-term argument for exactly that reason.

Every coefficient enters as an exact rational injected through Arb division, so
the products are outward rounded and the sums remain enclosures. No step
converts an object to a Python float.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import comb

from flint import arb

import spec
from intervals import exact


def coefficients(m: int) -> list[tuple[str, int, int, F]]:
    """Frozen exact all-m coefficient table, rederived from c_(m,t) = 1/t - 1/m."""
    if m not in spec.M_VALUES:
        raise ValueError(f"m={m} outside the frozen scope {spec.M_VALUES}")
    out = [("F", r, 0, F(1, m)) for r in range(m)]
    out += [("W", r, t - r - 1, F(1, t) - F(1, m))
            for t in range(1, m) for r in range(t)]
    return out


def assemble(m: int, F_vals: dict, W_vals: dict, *, leading_e=None) -> arb:
    """Certified interval assembly of R_m^(k) from order-k object enclosures."""
    if leading_e is not None:
        raise ValueError(
            "the raw-variable reformulation has no leading +e term; adding one "
            "would double count the drift already inside F")
    total = arb(0)
    for kind, r, j, c in coefficients(m):
        value = F_vals[r] if kind == "F" else W_vals[(r, j)]
        total = total + value * exact(c)
    return total


def assembly_arithmetic_excess(m: int, F_vals: dict, W_vals: dict,
                               result: arb) -> arb:
    """etaR_interval: widening introduced by the assembly beyond its inputs.

    The exact assembly of enclosures has radius exactly sum |c| * rad(input);
    anything Arb adds on top is outward-rounding widening that ERROR_ALGEBRA
    section 6 routes to B_interval. Never negative.
    """
    ideal = arb(0)
    for kind, r, j, c in coefficients(m):
        value = F_vals[r] if kind == "F" else W_vals[(r, j)]
        ideal = ideal + exact(abs(c)) * arb(0, value.rad())
    excess = arb(result.rad()) - arb(ideal.abs_upper())
    return excess if excess > 0 else arb(0)


def enclose(centre: arb, radius: arb) -> arb:
    """A certified enclosure centre +/- radius as a single Arb ball."""
    if not radius >= 0:
        raise ValueError("negative certified radius")
    return centre + arb(0, radius.abs_upper())


def all_m_report(F_vals: dict, W_vals: dict, order: int) -> dict:
    """Assemble every frozen m at one derivative order."""
    out = {}
    for m in spec.M_VALUES:
        value = assemble(m, F_vals, W_vals)
        out[m] = {"interval": value,
                  "arithmetic_excess": assembly_arithmetic_excess(m, F_vals, W_vals, value),
                  "terms": len(coefficients(m)), "derivative_order": order}
    return out


def curvature_bound(R2_interval: arb) -> arb:
    """M_R2 = mag(R2_interval) >= sup_(e in cell) |R''_(D,m)(e)|.

    Nonnegative by construction. Every rounding inside R2_interval is already
    inside this magnitude and must not be charged again (section 3).
    """
    value = R2_interval.abs_upper()
    if not value >= 0:
        raise ArithmeticError("negative curvature bound")
    return value


def check_frozen_coefficient_table() -> bool:
    """The rederived table must equal the frozen config/checkpoint.json table."""
    for m, rows in spec.ASSEMBLY_TERMS.items():
        if sorted(coefficients(m)) != sorted(rows):
            return False
    return True


def short_stop_decomposition(m: int) -> list[tuple[str, int, int, F]]:
    """Independent regrouping by terminal time t, used as a cross-check.

    -1/m from removing short stopping times plus +1/t from their convention-A
    restoration; the coefficient of W_(r,j) is 1/(r+j+1) - 1/m.
    """
    out = [("F", r, 0, F(1, m)) for r in range(m)]
    for r in range(m - 1):
        for j in range(m - r - 1):
            out.append(("W", r, j, F(1, r + j + 1) - F(1, m)))
    return out
