"""DIAGNOSTIC (NOT CERTIFYING): break-even analysis for a third-order expansion.

This module measures whether expanding the whole-cell `D` bound to second order
in `e` -- which needs a bound on the THIRD derivative -- beats the predecessor's
mean-value step. It is not imported by the certification path and contributes to
no certificate. Its answer is what motivated `code/refine2.py`.

THE QUESTION
------------
After the Phase 6 order-2 tightening the binding quantity in cells 318-324 is
the whole-cell curvature error `epsH`, which enters `M_R2` directly. At cell 321,
r = 4:

    epsH_4 = 9.145 = C*deltaH (0.000) + C*k2*epsF (0.160)
                   + C*2k1*epsD (3.731) + C*epsS2 (5.254)

and the predecessor refinement produces `epsD` by a MEAN VALUE step

    epsD_cell <= epsD_mid + rho * supH,     supH = sup_cell|H| <= |Hhat| + epsH

whose midpoint part is negligible (`epsD_mid = 2.05e-04`, `sup|Hhat| = 8.1e-05`):
essentially all of `epsD = 1.341` is `rho * epsH`. That closes a loop
`epsH -> epsD -> epsH` with gain `rho*C*2k1 = 0.408`, an amplification of 1.69x.
`F` is already expanded to second order; `D` is not, only because the predecessor
had no bound on the third derivative.

THE COMPARISON
--------------
Replacing `rho * sup|d_e^2|` by `(rho^2/2) * sup|d_e^3|` pays exactly when

    sup|d_e^3| / sup|d_e^2|  <  2/rho.

`supF3` majorises `sup_cell ||d_e^3 F_r||`; differentiating the frozen equation
`(I - K_e) F = S` three times in `e` and solving gives

    F3 = (I-K)^(-1)[ 3 K_1 H + 3 K_2 D + K_3 F + S3 ]
    supF3 <= C ( 3 k1 supH + 3 k2 supD + k3 supF + supS3 )

the same derivation, one order further, that the frozen ERROR_ALGEBRA uses to
reach `epsH = C(deltaH + k2 epsF + 2 k1 epsD + epsS2)`. `supS3` uses the frozen
source structure `S_r^(k) = sum_i C(k,i) J_i h_r^(k-i)` with a norm-only tower
for the true `h` from `h_j^(k) = sum_i C(k,i) K_i h_(j-1)^(k-i)`, seeded by the
exact closed forms `sup|h_1^(0)| <= 1` and `h_1^(k+1) = -S_0^(k)`.

THE MEASURED ANSWER: YES, AT EVERY (cell, r) IN THE BLOCK
---------------------------------------------------------
    cell 318 (rho 0.10732, break-even 18.64)  ratio 13.1-17.7  ->  improves
    cell 321 (rho 0.14657, break-even 13.65)  ratio  9.2-13.2  ->  improves
    cell 324 (rho 0.15627, break-even 12.80)  ratio  7.3-11.8  ->  improves
    cell 325 (rho 0.09624, break-even 20.78)  ratio  7.3-13.0  ->  improves

(These are re-measured against the already-tightened records, so they show the
margin that survives the expansion, not the margin before it.) The margin is
thinnest at r = 4, where the h tower grows fastest -- about 3x per order at
cell 321: 0.78, 1.97, 5.79, 19.8 -- against j_i growth of about 2x.

A NOTE ON HOW TO READ THIS
--------------------------
Both columns must be computed with the SAME surrogate for the candidate suprema
(this module uses 1, which is not available outside a prepared cell). Comparing
this module's second-order column against a certificate record's first-order
value is NOT like-for-like -- the record uses the true `sup|Hhat| = 8.1e-05`,
which flatters the first-order term -- and inverts the conclusion at r = 4. The
implementation in `code/refine2.py` uses the true suprema on both sides and
guards every object with `min(new, predecessor)`, so a cell where the expansion
would lose simply keeps the predecessor's bound.

WHAT THIS STILL DOES NOT FIX
----------------------------
The dominant term is not the loop but the propagated source error
`C * epsS2_4 = 5.254` of `9.145`. That number is a pure cascade,

    S_0^(1) 0.0586 -> h_1^(2) 0.0586 -> h_2^(2) 0.274
            -> h_3^(2) 0.835 -> h_4^(2) 1.679 -> S_4^(2) 2.458

each step the frozen DAG's cell-value propagation multiplying by
`k_0 + 2k_1 + k_2 = 2.98`, seeded by the irreducible closed-form term
`rho * sup_cell|phi2| = 0.0586`. Tightening it needs certified MIDPOINT objects
one derivative order above what the frozen object set provides (`h^(3)`,
`S^(3)`); adding those changes the frozen obligation universe and is out of
scope here. The norm-only substitute is far weaker (`rho * sup|h_4^(3)| = 2.90`
against the propagated 1.679) and does not help.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import ancestry                                                 # noqa: E402,F401

from flint import arb                                           # noqa: E402

import sharp_norms                                              # noqa: E402
import spec                                                     # noqa: E402
from intervals import exact, mag_fraction, tight_upper, workprec  # noqa: E402

import order2                                                   # noqa: E402

BLOCK = tuple(range(318, 326))


def h_tower(left, right, k_) -> dict:
    """Norm-only sup bounds on the TRUE h_j^(k), j = 1..4, k = 0..3."""
    T = {(1, 0): arb(1)}
    for k in range(3):
        T[1, k + 1] = order2.sup_source_derivative_on(k, left, right)
    for j in range(2, 5):
        for k in range(4):
            acc = arb(0)
            for i in range(k + 1):
                acc = acc + arb(comb(k, i)) * k_[i] * T[j - 1, k - i]
            T[j, k] = tight_upper(acc)
    return T


def sup_source_third_derivative(left, right, j_, T: dict, r: int) -> arb:
    if r == 0:
        return order2.sup_source_derivative_on(3, left, right)
    acc = arb(0)
    for i in range(4):
        acc = acc + arb(comb(3, i)) * j_[i] * T[r, 3 - i]
    return tight_upper(acc)


def analyse(record: dict) -> dict:
    """Compare the first- and second-order whole-cell D bounds for one cell."""
    cell = next(c for c in spec.CELLS if c["detector"] == "CUSUM"
                and c["index"] == record["cell_index"])
    left, right = F(cell["left"][0]), F(cell["right"][0])
    rho, C = exact(cell["rho"][0]), exact(cell["C_upper"])
    tbl = sharp_norms.table(left, right)
    k_, j_ = tbl["k"], tbl["j"]
    T = h_tower(left, right, k_)

    fl = lambda s: float(F(s))
    per_r = {}
    for r in range(5):
        epsF = exact(F(record["eps_cell_refined"][f"F:{r}"]))
        epsD = exact(F(record["eps_cell_refined"][f"D:{r}"]))
        epsH = exact(F(record["eps_cell_refined"][f"H:{r}"]))
        supS3 = sup_source_third_derivative(left, right, j_, T, r)
        # candidate suprema are O(1) and unavailable outside a prepared cell;
        # 1 is used for them here, which UNDERSTATES supF3 and so favours the
        # expansion under test.
        supF3 = tight_upper(C * (arb(3) * k_[1] * (arb(1) + epsH)
                                 + arb(3) * k_[2] * (arb(1) + epsD)
                                 + k_[3] * (arb(1) + epsF)
                                 + supS3))
        first = tight_upper(rho * (arb(1) + epsH))
        second = tight_upper(rho * rho / arb(2) * supF3)
        per_r[r] = {
            "epsD_cell": str(mag_fraction(epsD)),
            "epsH_cell": str(mag_fraction(epsH)),
            "sup_source_third_derivative": float(mag_fraction(supS3)),
            "supF3": float(mag_fraction(supF3)),
            "first_order_term_rho_supH": float(mag_fraction(first)),
            "second_order_term_half_rho2_supF3": float(mag_fraction(second)),
            "second_order_improves": second.upper() < first.upper(),
            "break_even_ratio_2_over_rho": float(2 / F(mag_fraction(rho))),
            "measured_ratio_supF3_over_supH": float(
                mag_fraction(supF3) / mag_fraction(arb(1) + epsH)),
        }
    return {
        "cell_index": record["cell_index"],
        "rho": float(F(cell["rho"][0])),
        "h_tower_sup": {f"h_{j}^({k})": float(mag_fraction(T[j, k]))
                        for j in range(1, 5) for k in range(4)},
        "kernel_norms_k": {i: float(mag_fraction(k_[i])) for i in k_},
        "raw_kernel_norms_j": {i: float(mag_fraction(j_[i])) for i in j_},
        "per_r": per_r,
        "any_r_improves": any(v["second_order_improves"] for v in per_r.values()),
        "m5_M_R2": fl(record["m"]["5"]["M_R2"]),
        "m5_utilization": record["m"]["5"]["cover"]["utilization"],
    }


def main() -> None:
    cells_dir = Path(__file__).resolve().parent / "cells"
    out = {"schema": "k1.cusum-successor.third-order-analysis.v1",
           "result_bearing": False,
           "certifying": False,
           "conclusion": "second-order expansion of the whole-cell D bound "
                         "improves every (cell, r) in the block: the "
                         "measured third/second derivative ratio is below "
                         "the 2/rho break-even everywhere; implemented in "
                         "code/refine2.py",
           "cells": []}
    with workprec(spec.PRODUCTION_BITS):
        for p in sorted(cells_dir.glob("succ_CUSUM_*.json")):
            out["cells"].append(analyse(json.loads(p.read_text())))
    out["any_cell_improves"] = any(c["any_r_improves"] for c in out["cells"])
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    (Path(__file__).resolve().parent / "third_order_analysis.json").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
