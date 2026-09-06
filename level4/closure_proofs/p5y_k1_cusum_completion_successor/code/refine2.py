"""PHASE 7b: second-order Taylor-in-e for the WHOLE-CELL D and F bounds.

THE MEASURED PROBLEM (cell 321, r = 4, after the Phase 6 order-2 tightening)
----------------------------------------------------------------------------
The binding quantity is the whole-cell curvature error `epsH`, which enters
`M_R2` directly:

    epsH_4 = 9.145 = C*deltaH (0.000) + C*k2*epsF (0.160)
                   + C*2k1*epsD (3.731) + C*epsS'' (5.254)

and the predecessor refinement produces `epsD` by a MEAN VALUE step

    epsD_cell <= epsD_mid + rho * supH,     supH = sup_cell|H| <= |Hhat| + epsH

whose midpoint part is negligible (`epsD_mid = 2.05e-04`, `sup|Hhat| = 8.1e-05`):
essentially all of `epsD = 1.341` is `rho * epsH`. That closes a loop
`epsH -> epsD -> epsH` with gain `rho*C*2k1 = 0.408`, an amplification of 1.69x.
`F` is already expanded to second order in `e`; `D` is not -- only because the
predecessor had no bound on the third derivative.

THE EXPANSION
-------------
Every candidate is a state-only polynomial, constant in `e` (Representation A),
so for the error functions `E_F = Fhat - F`, `E_D = Dhat - D`, `E_H = Hhat - H`:

    d_e E_F = -D,    d_e E_D = -H,    d_e E_H = -F'''

Taylor at `e0` with the integral remainder, pointwise in `x`, then sup over `x`:

    epsF_cell <= epsF_mid + rho*||D(e0)|| + (rho^2/2)*||H(e0)|| + (rho^3/6)*supF3
    epsD_cell <= epsD_mid + rho*||H(e0)|| + (rho^2/2)*supF3
    epsH_cell <= epsH_mid + rho*supF3

where `||D(e0)|| <= sup|Dhat| + epsD_mid` and `||H(e0)|| <= sup|Hhat| + epsH_mid`
are MIDPOINT quantities -- four orders of magnitude below their whole-cell
counterparts -- so only the last term of each line still needs a whole-cell
supremum. The predecessor's first line is kept as well and the two are combined
with `min`, so this can only tighten.

THE THIRD-DERIVATIVE BOUND
--------------------------
`supF3` majorises `sup_cell ||d_e^3 F_r||` for the TRUE solution. Differentiate
the frozen equation `(I - K_e) F = S` three times in `e` and solve:

    F''' = (I-K)^(-1) [ 3 K_1 F'' + 3 K_2 F' + K_3 F + S''' ]
    supF3 <= C ( 3 k1 supH + 3 k2 supD + k3 supF + supS3 )

This is the SAME derivation, one order further, that the frozen ERROR_ALGEBRA
performs to reach `epsH = C(deltaH + k2 epsF + 2 k1 epsD + epsS'')`: the binomial
coefficients here (3, 3, 1) continue the frozen second-order line's (1, 2). It
introduces NO new certified error level, NO new object and NO new charge -- it is
a norm-only majorant used inside the refinement, exactly as `supH = sup|Hhat| +
epsH` already is. The frozen error algebra, ledger, budgets, charges, cover
geometry, precision and Taylor degree are untouched.

`supS3` uses the frozen source structure:

    r = 0:  S_0 is the exact closed form, so `sup_cell|S_0'''|` is the
            drift-aware pointwise supremum the Phase 6 closed-form leaves use.
    r >= 1: `S_r^(k) = sum_i C(k,i) J_i h_r^(k-i)`, so
            `supS3_r <= sum_(i=0..3) C(3,i) j_i ||h_r^(3-i)||`
            with a norm-only tower for the true h, from the frozen recursion
            `h_j^(k) = sum_i C(k,i) K_i h_(j-1)^(k-i)`, seeded by the exact
            closed forms `||h_1^(0)|| <= 1` and `h_1^(k+1) = -S_0^(k)`.

WHY EVERY ITERATE IS STILL RIGOROUS
-----------------------------------
All the maps are monotone NON-DECREASING in `(epsF, epsD, epsH)`: larger inputs
give a larger `supF3` and hence larger outputs. So if the input triple is a valid
upper bound, so is the output triple. The iteration is seeded with the
predecessor's refinement -- itself valid unconditionally -- and every step takes
`min` with the previous value, so it is a DECREASING sequence of VALID bounds. No
fixed point is asserted to exist and no contraction is assumed; if the iteration
does not improve, the predecessor's bound simply stands. A final guard refuses
any `r` whose result is not <= the predecessor's.

WHEN IT PAYS
------------
Replacing `rho*sup|d^2|` by `(rho^2/2)*sup|d^3|` helps only when

    sup|d^3| / sup|d^2|  <  2/rho.

Measured across cells 318-325 the ratio is 12.8-14.5 against a break-even of
12.8-20.8, so the gain is real but modest at the widest cells and largest at the
narrow ones. `min` makes the losing case free.
"""
from __future__ import annotations

from math import comb

import ancestry                                                 # noqa: F401

from flint import arb                                           # noqa: E402

import propagate                                                # noqa: E402
import refine as predecessor                                    # noqa: E402
from intervals import exact, mag_fraction, tight_upper          # noqa: E402

import order2                                                   # noqa: E402

MAX_ITERATIONS = predecessor.MAX_ITERATIONS
TIGHTENING = "second_order_taylor_in_e_whole_cell_D_and_F"


class RefinementRegression(RuntimeError):
    """A refinement produced a bound that is not <= the predecessor's."""


def _min(a: arb, b: arb) -> arb:
    return a if a.upper() <= b.upper() else b


def h_tower(cert) -> dict:
    """Norm-only sup bounds on the TRUE h_j^(k), j = 1..4, k = 0..3."""
    k_ = cert.norms["k"]
    T = {(1, 0): arb(1)}
    for k in range(3):
        T[1, k + 1] = order2.sup_source_derivative_on(k, cert.left, cert.right)
    for j in range(2, 5):
        for k in range(4):
            acc = arb(0)
            for i in range(k + 1):
                acc = acc + arb(comb(k, i)) * k_[i] * T[j - 1, k - i]
            T[j, k] = tight_upper(acc)
    return T


def sup_source_third_derivative(cert, r: int, T: dict) -> arb:
    """sup_cell ||d_e^3 S_r||, the frozen source structure one order further."""
    if r == 0:
        return order2.sup_source_derivative_on(3, cert.left, cert.right)
    j_ = cert.norms["j"]
    acc = arb(0)
    for i in range(4):
        acc = acc + arb(comb(3, i)) * j_[i] * T[r, 3 - i]
    return tight_upper(acc)


def refine(cert, mid, crude, *, rs=range(5), iterations: int = MAX_ITERATIONS) -> dict:
    """The predecessor refinement, then the second-order whole-cell expansion."""
    base = predecessor.refine(cert, mid, crude, rs=rs, iterations=iterations)

    rho = exact(cert.rho)
    half_rho2 = rho * rho / arb(2)
    sixth_rho3 = rho * rho * rho / arb(6)
    C = exact(cert.C)
    k1, k2, k3 = cert.norms["k"][1], cert.norms["k"][2], cert.norms["k"][3]
    T = h_tower(cert)

    out, audit = dict(base["eps"]), {}
    for r in rs:
        epsF_mid, epsD_mid = mid.get(f"F:{r}"), mid.get(f"D:{r}")
        epsH_mid = mid.get(f"H:{r}")
        deltaH_cell = cert.residuals[f"H_{r}"]["delta_cell"]
        epsS2 = crude.get(propagate._source_node(r, 2))
        supF_hat = cert.sup["F", r, 0]
        supD_hat = cert.sup["D", r, 0]
        supH_hat = cert.sup["H", r, 0]
        supS3 = sup_source_third_derivative(cert, r, T)

        # midpoint anchors: fixed, they do not move with the iteration
        D_at_e0 = tight_upper(supD_hat + epsD_mid)
        H_at_e0 = tight_upper(supH_hat + epsH_mid)

        epsF, epsD, epsH = (base["eps"][f"F:{r}"], base["eps"][f"D:{r}"],
                            base["eps"][f"H:{r}"])
        trail = []
        for step in range(iterations):
            supF3 = tight_upper(C * (arb(3) * k1 * (supH_hat + epsH)
                                     + arb(3) * k2 * (supD_hat + epsD)
                                     + k3 * (supF_hat + epsF)
                                     + supS3))
            nD = _min(epsD, tight_upper(epsD_mid + rho * H_at_e0
                                        + half_rho2 * supF3))
            nF = _min(epsF, tight_upper(epsF_mid + rho * D_at_e0
                                        + half_rho2 * H_at_e0
                                        + sixth_rho3 * supF3))
            nH = _min(epsH, tight_upper(
                C * (deltaH_cell + k2 * nF + arb(2) * k1 * nD + epsS2)))
            nH = _min(nH, tight_upper(epsH_mid + rho * supF3))
            trail.append({"step": step,
                          "supF3": str(mag_fraction(supF3)),
                          "epsF_cell": str(mag_fraction(nF)),
                          "epsD_cell": str(mag_fraction(nD)),
                          "epsH_cell": str(mag_fraction(nH))})
            improved = nH.upper() < (epsH * exact(999999) / arb(1000000)).upper()
            epsF, epsD, epsH = nF, nD, nH
            if not improved:
                break

        for key, new in ((f"F:{r}", epsF), (f"D:{r}", epsD), (f"H:{r}", epsH)):
            if new.upper() > base["eps"][key].upper():
                raise RefinementRegression(
                    f"{key}: second-order refinement is not <= the predecessor")
            out[key] = new

        base_H = base["eps"][f"H:{r}"]
        audit[r] = {**base["audit"][r],
                    "second_order": {
                        "tightening": TIGHTENING,
                        "iterations": len(trail),
                        "sup_source_third_derivative": str(mag_fraction(supS3)),
                        "supF3_final": trail[-1]["supF3"] if trail else None,
                        "H_at_e0": str(mag_fraction(H_at_e0)),
                        "D_at_e0": str(mag_fraction(D_at_e0)),
                        "predecessor": {
                            "epsF_cell": str(mag_fraction(base["eps"][f"F:{r}"])),
                            "epsD_cell": str(mag_fraction(base["eps"][f"D:{r}"])),
                            "epsH_cell": str(mag_fraction(base_H))},
                        "refined": {"epsF_cell": str(mag_fraction(epsF)),
                                    "epsD_cell": str(mag_fraction(epsD)),
                                    "epsH_cell": str(mag_fraction(epsH))},
                        "factor_H": (float(mag_fraction(base_H) / mag_fraction(epsH))
                                     if mag_fraction(epsH) > 0 else None),
                        "trail": (trail[:3] + ["..."] + trail[-3:]
                                  if len(trail) > 6 else trail)}}
    return {"eps": out, "audit": audit}


def install() -> str:
    """Route `propagate`'s whole-cell refinement through this module.

    `propagate` is a REVIEWED, committed module and is not edited; the successor
    substitutes its refinement dependency explicitly. The substitution is
    recorded in every certificate record, covered by the producer manifest, and
    asserted by the test suite.
    """
    import sys
    propagate.refine = sys.modules[__name__]
    return TIGHTENING
