"""R2 candidate C2 - dense scale-then-synthetic-division affine substitution.

Replaces `rebaseguard_certify.residual._affine_to_unit_square`, measured at 98.0s
of the ~102s Bernstein cost of the two main regions (~80% of a certification),
which uses an O(deg^4) dictionary loop: for each of the ~3500 coefficients it
forms bi_mul(r_powers[i], t_powers[j]) with (i+1)(j+1) terms.

Same substitution, standard algorithm, O(deg^3) scalar work:

    P(r,t) = sum_{ij} c_ij r^i t^j ,  r = a + b*rho ,  t = c + d*sigma
      step 1 scale : c_ij <- c_ij * b^i * d^j
      step 2 shift : Horner synthetic division by a down each r-column,
                     then by c along each t-row

In exact arithmetic this is the same polynomial.  In ball arithmetic both are
outward-rounded enclosures of the same coefficients, so the downstream Bernstein
bound still bounds the same object; `r2_selftest.py` S1/S2 assert coefficient
overlap against the reference and a bounded ratio of the resulting bounds.
"""
from __future__ import annotations

import sys
from pathlib import Path

from flint import arb

_PROOF_SRC = Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"
if str(_PROOF_SRC) not in sys.path:
    sys.path.insert(0, str(_PROOF_SRC))

from rebaseguard_certify.polynomial import BiPoly     # noqa: E402


def affine_to_unit_square_fast(poly: BiPoly, r_lower: arb, r_upper: arb,
                               t_lower: arb, t_upper: arb) -> BiPoly:
    """P(r_lower + (r_upper-r_lower) rho, t_lower + (t_upper-t_lower) sigma)."""
    if not poly:
        return {}
    max_i = max(i for i, _ in poly)
    max_j = max(j for _, j in poly)
    a = r_lower
    b = r_upper - r_lower
    c0 = t_lower
    d = t_upper - t_lower

    grid = [[arb(0)] * (max_j + 1) for _ in range(max_i + 1)]
    for (i, j), coeff in poly.items():
        grid[i][j] = coeff

    # SHIFT FIRST, THEN SCALE.  P(a + b rho) = [P(. + a)](b rho), so the Taylor
    # shift by `a` must precede multiplication of coefficient i by b^i; doing it
    # the other way round computes P(b(rho + a)), a different polynomial.
    if not a.is_zero():
        for j in range(max_j + 1):
            col = [grid[i][j] for i in range(max_i + 1)]
            for k in range(max_i):
                for i in range(max_i - 1, k - 1, -1):
                    col[i] = col[i] + a * col[i + 1]
            for i in range(max_i + 1):
                grid[i][j] = col[i]
    if not c0.is_zero():
        for i in range(max_i + 1):
            row = grid[i]
            for k in range(max_j):
                for j in range(max_j - 1, k - 1, -1):
                    row[j] = row[j] + c0 * row[j + 1]

    b_pow = [arb(1)] * (max_i + 1)
    for i in range(1, max_i + 1):
        b_pow[i] = b_pow[i - 1] * b
    d_pow = [arb(1)] * (max_j + 1)
    for j in range(1, max_j + 1):
        d_pow[j] = d_pow[j - 1] * d

    out: BiPoly = {}
    for i in range(max_i + 1):
        bi = b_pow[i]
        row = grid[i]
        for j in range(max_j + 1):
            v = row[j]
            if not v.is_zero():
                out[(i, j)] = v * bi * d_pow[j]
    return out


def max_abs_on_reachable_fast(low_sum: BiPoly, high_sum: BiPoly, *,
                              subdivision_depth: int) -> tuple[arb, dict]:
    """Reference `_max_abs_on_reachable` with the fast affine substitution.

    The reachable-set cover, the triangle parameterisation, the Bernstein
    conversion and the subdivision are the UNMODIFIED reference routines; only
    `_affine_to_unit_square` is replaced (candidate C2), and the depth is
    supplied by the frozen ladder (candidate C1).
    """
    from rebaseguard_certify.residual import (
        _bernstein_max_abs, _parameterize_triangle, _power_to_bernstein,
    )
    low_p = _parameterize_triangle(low_sum)
    high_p = _parameterize_triangle(high_sum)
    low_u = affine_to_unit_square_fast(low_p, arb(0), arb(1), arb(0), arb(1))
    high_u = affine_to_unit_square_fast(high_p, arb(1), arb(4), arb(0), arb(1))
    low_max, low_n = _bernstein_max_abs(_power_to_bernstein(low_u), subdivision_depth)
    high_max, high_n = _bernstein_max_abs(_power_to_bernstein(high_u), subdivision_depth)

    plus_tail = {(i, 0): c for (i, j), c in high_sum.items() if j == 0}
    minus_tail = {(0, j): c for (i, j), c in high_sum.items() if i == 0}
    plus_u = affine_to_unit_square_fast(plus_tail, arb(4), arb(5), arb(0), arb(1))
    minus_u = affine_to_unit_square_fast(minus_tail, arb(0), arb(1), arb(4), arb(5))
    plus_max, plus_n = _bernstein_max_abs(_power_to_bernstein(plus_u), subdivision_depth)
    minus_max, minus_n = _bernstein_max_abs(_power_to_bernstein(minus_u), subdivision_depth)

    maximum = low_max.max(high_max).max(plus_max).max(minus_max)
    return maximum, {"subdivision_depth": subdivision_depth,
                     "bernstein_patches": low_n + high_n + plus_n + minus_n,
                     "parameterization": "p=r*t, m=r*(1-t)",
                     "pieces": ["0<=r<=1", "1<=r<=4", "axis tails 4<=r<=5"],
                     "reachable_continuum_complete": True,
                     "sampled_grid_used": False,
                     "affine_substitution": "dense scale+synthetic-division (R2 C2)"}
