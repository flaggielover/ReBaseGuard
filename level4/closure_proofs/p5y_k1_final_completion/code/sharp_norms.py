"""Drift-aware certified operator norms.

WHY
---
The reviewed implementation bounds every kernel operator by a WHOLE-LINE
absolute Gaussian moment:

    ||d_e^i K_e|| <= int_R |phi^(i)|                      (k_i)
    ||d_e^i K_(z,e)|| <= M_i + |e| k_i                    (jz_i)
    ||J_i|| <= jz_i + e_max k_i + i k_(i-1)               (j_i)

ERROR_ALGEBRA section 2 calls whole-line moments "admissible", not mandatory.
At large drift they are very pessimistic, and the `e_max` factors in `jz_i`/`j_i`
make them grow LINEARLY in the drift: at cell 325 (`e_max = 11/2`) they give
`j_0 = 11.8`, `j_1 = 10.8`, `j_2 = 13.4`, which is what dominates that cell's
order-2 envelopes and drives its certificate failure.

THE SHARPER BOUND
-----------------
The raw-variable kernel has e-FREE state limits, so for `x = (p, m)` in the
reachable square `[0, h]^2` the z-window is

    z in [l(x), u(x)] = [m - 11/2, 11/2 - p]  subset  [-11/2, 11/2]

with the widest window exactly at `x = (0,0)`. Substituting `y = z + e`, every
operator's kernel weight is a Hermite function of `y`:

    d_e^i K_e        weight  phi^(i)(y)      = (-1)^i He_i(y) phi(y)
    J_0 = K_z + e K  weight  y phi(y)        =        He_1(y) phi(y)
    J_1 = d_e J_0    weight  (1-y^2) phi(y)  =      - He_2(y) phi(y)
    J_2 = d_e^2 J_0  weight  (y^3-3y) phi(y) =        He_3(y) phi(y)

so BOTH families collapse to one quantity over the shifted window
`W = [left - 11/2, right + 11/2]`, which contains every `(x, e)` in the cell:

    ||d_e^i K_e|| <= A_i(W)          ||J_i|| <= A_(i+1)(W)
    A_n(W) = int_W |He_n(y)| phi(y) dy

`A_n` is evaluated EXACTLY, not quadratured: `int He_n phi = -He_(n-1) phi`, so
splitting `W` at the known roots of `He_n` and summing the absolute increments
of `-He_(n-1) phi` is closed form. Roots used:

    He_0 = 1                 none
    He_1 = y                 0
    He_2 = y^2 - 1           +-1
    He_3 = y^3 - 3y          0, +-sqrt(3)
    He_4 = y^4 - 6y^2 + 3    +-sqrt(3 +- sqrt 6)

Every returned bound is `min(drift-aware, whole-line closed form,
Cauchy-Schwarz sqrt(n!))`, so it can never be worse than the reviewed bound and
is never used unless it is provably smaller. Nothing here changes the frozen
cover geometry, the Taylor semantics, a budget, a threshold or the precision:
it is a strictly sharper certified bound on the same operator.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import factorial

import base                                                     # noqa: F401

from flint import arb                                           # noqa: E402

import opnorms as reviewed_norms                                # noqa: E402
from intervals import exact, tight_upper, workprec              # noqa: E402

Z_HALF = F(11, 2)                    # the raw-variable state half-window


def phi(x: arb) -> arb:
    return (-(x * x) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()


def hermite_he(n: int, y: arb) -> arb:
    """Probabilists' Hermite He_n by the stable three-term recurrence."""
    a, b = arb(1), y
    if n == 0:
        return a
    for k in range(1, n):
        a, b = b, y * b - arb(k) * a
    return b


def _antiderivative(n: int, y: arb) -> arb:
    """int He_n phi = -He_(n-1) phi  (with He_(-1) understood via Phi for n=0)."""
    if n == 0:
        return (arb(1) + (y / arb(2).sqrt()).erf()) / arb(2)      # Phi(y)
    return -hermite_he(n - 1, y) * phi(y)


def _roots(n: int) -> list[F | str]:
    """Exact roots of He_n for the orders this campaign needs (n <= 4)."""
    if n == 0:
        return []
    if n == 1:
        return [F(0)]
    if n == 2:
        return [F(-1), F(1)]
    if n == 3:
        return ["-sqrt3", F(0), "sqrt3"]
    if n == 4:
        return ["-sqrt(3+sqrt6)", "-sqrt(3-sqrt6)",
                "sqrt(3-sqrt6)", "sqrt(3+sqrt6)"]
    if n == 5:
        return ["-sqrt(5+sqrt10)", "-sqrt(5-sqrt10)", F(0),
                "sqrt(5-sqrt10)", "sqrt(5+sqrt10)"]
    raise ValueError(f"He_{n} roots not tabulated; extend the table deliberately")


def _root_value(r) -> arb:
    if isinstance(r, F):
        return exact(r)
    three, six = arb(3), arb(6)
    if r == "sqrt3":
        return three.sqrt()
    if r == "-sqrt3":
        return -three.sqrt()
    if r == "sqrt(3+sqrt6)":
        return (three + six.sqrt()).sqrt()
    if r == "-sqrt(3+sqrt6)":
        return -(three + six.sqrt()).sqrt()
    if r == "sqrt(3-sqrt6)":
        return (three - six.sqrt()).sqrt()
    if r == "-sqrt(3-sqrt6)":
        return -(three - six.sqrt()).sqrt()
    five, ten = arb(5), arb(10)
    if r == "sqrt(5+sqrt10)":
        return (five + ten.sqrt()).sqrt()
    if r == "-sqrt(5+sqrt10)":
        return -(five + ten.sqrt()).sqrt()
    if r == "sqrt(5-sqrt10)":
        return (five - ten.sqrt()).sqrt()
    if r == "-sqrt(5-sqrt10)":
        return -(five - ten.sqrt()).sqrt()
    raise ValueError(r)


def absolute_hermite_moment(n: int, lo: arb, hi: arb) -> arb:
    """A_n = int_lo^hi |He_n(y)| phi(y) dy, exactly, by sign-split antiderivatives."""
    cuts = [lo]
    for r in _roots(n):
        v = _root_value(r)
        # Only interior roots split the interval; Arb comparisons are certified.
        if v > lo and v < hi:
            cuts.append(v)
    cuts.append(hi)
    total = arb(0)
    for a, b in zip(cuts[:-1], cuts[1:]):
        total = total + (_antiderivative(n, b) - _antiderivative(n, a)).abs_upper()
    return tight_upper(total)


def _window(left, right) -> tuple[arb, arb]:
    """W = [left - 11/2, right + 11/2] contains every (x, e) of the cell."""
    return exact(F(left) - Z_HALF), exact(F(right) + Z_HALF)


def _cauchy_schwarz(n: int) -> arb:
    return arb(factorial(n)).sqrt()


def kernel_norm(i: int, left, right) -> arb:
    """k_i: sup over the cell of ||d_e^i K_e||, never worse than the reviewed bound."""
    lo, hi = _window(left, right)
    candidates = [absolute_hermite_moment(i, lo, hi),
                  reviewed_norms.kernel_norm(i),
                  tight_upper(_cauchy_schwarz(i))]
    best = candidates[0]
    for c in candidates[1:]:
        if c.upper() < best.upper():
            best = c
    return tight_upper(best)


def raw_kernel_norm(i: int, left, right) -> arb:
    """j_i: sup over the cell of ||J_i||, where J_i's weight is He_(i+1) phi."""
    lo, hi = _window(left, right)
    e_max = exact(max(abs(F(left)), abs(F(right))))
    sharp = absolute_hermite_moment(i + 1, lo, hi)
    reviewed = reviewed_norms.raw_kernel_norm(i, e_max)
    return tight_upper(sharp if sharp.upper() < reviewed.upper() else reviewed)


def table(left, right, *, orders: int = 4) -> dict:
    """The certified norm table for one frozen cell."""
    lo, hi = _window(left, right)
    e_max = exact(max(abs(F(left)), abs(F(right))))
    return {
        "e_max": e_max,
        "window": (lo, hi),
        "k": {i: kernel_norm(i, left, right) for i in range(orders + 1)},
        "j": {i: raw_kernel_norm(i, left, right) for i in range(orders + 1)},
        "sup_phi": {i: reviewed_norms.sup_phi_derivative(i)
                    for i in range(orders + 2)},
        "provenance": {
            "k": "min(int_W |He_i| phi, whole-line closed form, sqrt(i!))",
            "j": "min(int_W |He_(i+1)| phi, reviewed jz_i + e_max k_i + i k_(i-1))",
            "window": "W = [left - 11/2, right + 11/2]; the raw-variable state "
                      "limits are e-free and widest at x = (0,0)",
            "evaluation": "exact: int He_n phi = -He_(n-1) phi, split at the "
                          "known roots of He_n; no quadrature",
            "sampled_operator_norms_used": False,
            "never_worse_than_reviewed": True,
        },
    }


def improvement_report(left, right) -> dict:
    """How much sharper the drift-aware bounds are for one cell."""
    e_max = exact(max(abs(F(left)), abs(F(right))))
    out = {}
    for i in range(4):
        rk, sk = reviewed_norms.kernel_norm(i), kernel_norm(i, left, right)
        rj, sj = reviewed_norms.raw_kernel_norm(i, e_max), raw_kernel_norm(i, left, right)
        out[f"k_{i}"] = {"reviewed": float(rk.abs_upper()),
                         "sharp": float(sk.abs_upper()),
                         "factor": float(rk.abs_upper()) / float(sk.abs_upper())}
        out[f"j_{i}"] = {"reviewed": float(rj.abs_upper()),
                         "sharp": float(sj.abs_upper()),
                         "factor": float(rj.abs_upper()) / float(sj.abs_upper())}
    return out
