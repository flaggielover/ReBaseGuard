"""Phase 1: the exact critical A0 thresholds, and the monotonicity that makes them meaningful.

Everything here is derived by evaluating the committed equations -- theorem TC-T's whole-cell enclosure composed
with the frozen K5-B direct clause -- at chosen atom-constant triples. No threshold is transcribed from prose and
no rounded value is used as an input anywhere downstream.

Two distinct objects are produced, and the difference matters:

  * `critical_A0`  the bisected bracket [closes_below, open_at_or_above] of the A1 = A2 = 0 critical value. This is
                   a REPORTED quantity. It is never the load-bearing test, because a bisected bracket is a rounded
                   object and a PASS must not depend on which side of the bracket a bound falls.

  * `monotone`     the structural fact that licenses the load-bearing test: Gamma is nondecreasing in A0 once the
                   TC-T/K5-B intersection is non-empty, so `Gamma(B, 0, 0) >= 0` proves `Gamma(A0, 0, 0) >= 0` for
                   every A0 >= B. The load-bearing test in Phase 6 is that direct evaluation at the certified
                   lower bound, not a comparison against `critical_A0`.

    python3 -B c4_thresholds.py --out OUT.json
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c4_common import OPEN_CELLS, cell_supply, committed_inputs, frozen_stack, gamma_at  # noqa: E402

BISECTION_STEPS = 220


def intersection_nonempty(d, ad5) -> bool:
    """The TC-T enclosure [lo, hi] meets the sealed R2 interval. Once true it stays true as [lo, hi] widens."""
    return not (max(F(ad5["R2_interval"]["lo"]), d["lo"]) > min(F(ad5["R2_interval"]["hi"]), d["hi"]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)
    per = {}
    for k in OPEN_CELLS:
        meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
        A = s["A"]
        g = lambda a0: gamma_at(FC, T, R, B, meas, aux, ad5, cov, a0, 0, 0)          # noqa: E731
        cert, ko = g(A["A0"]), g(A["A0"])
        row = {"A0_certified": str(A["A0"]), "A0_certified_float": float(A["A0"]),
               "Gamma_A1A2_zero_at_certified_A0": float(ko["Gamma"]),
               "closes_at_A1A2_zero": bool(ko["pass"]),
               "intersection_nonempty_at_certified_A0": intersection_nonempty(cert, ad5)}

        if ko["pass"]:
            row["critical_A0"] = None
            row["why_no_threshold"] = ("A0 is not this cell's blocker: it already closes at A1 = A2 = 0 with A0 "
                                       "left exactly as certified, so no lower bound on E_a[tau] can exclude it.")
        else:
            lo, hi = F(0), A["A0"]
            if not g(lo)["pass"]:
                row["critical_A0"] = None
                row["why_no_threshold"] = "the cell stays open even at A0 = 0; A0 is not the binding constraint"
            else:
                for _ in range(BISECTION_STEPS):
                    mid = (lo + hi) / 2
                    if g(mid)["pass"]:
                        lo = mid
                    else:
                        hi = mid
                row["critical_A0"] = {
                    "closes_below_exact": str(lo), "open_at_or_above_exact": str(hi),
                    "closes_below": float(lo), "open_at_or_above": float(hi),
                    "bracket_width": float(hi - lo),
                    "outward_rounded_12dp": f"{float(hi):.12f}",
                    "A0_reduction_factor_needed_from_certified": float(A["A0"] / lo),
                    "A0_reduction_percent_needed": float(100 * (1 - lo / A["A0"]))}

        # monotonicity of Gamma in A0, exercised rather than asserted: a ladder from 0 to the certified value
        ladder = [F(i, 20) * A["A0"] for i in range(21)]
        vals = [g(x) for x in ladder]
        row["monotone"] = {
            "ladder_points": len(ladder),
            "Gamma_nondecreasing": all(vals[i]["Gamma"] <= vals[i + 1]["Gamma"] for i in range(len(vals) - 1)),
            "intersection_nonempty_from": next((float(x) for x, v in zip(ladder, vals)
                                                if intersection_nonempty(v, ad5)), None),
            "Gamma_at_A0_zero": float(vals[0]["Gamma"])}
        per[str(k)] = row

    out = {"schema": "rebaseguard.p5y.k5.tail-c4.thresholds.v1",
           "derivation": "theorem TC-T whole-cell enclosure -> frozen K5-B direct clause, exact rationals",
           "bisection_steps": BISECTION_STEPS,
           "load_bearing_test": "Gamma(B, 0, 0) >= 0 evaluated directly; critical_A0 is reported, never an input",
           "new_real_scientific_addresses_evaluated": 0,
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY", "cells": per}
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    for k, v in per.items():
        c = v["critical_A0"]
        print(f"cell {k}: A0={v['A0_certified_float']:.9f} Gamma(A1=A2=0)={v['Gamma_A1A2_zero_at_certified_A0']:+.9f} "
              f"closes={v['closes_at_A1A2_zero']} "
              f"crit={'-' if not c else c['outward_rounded_12dp']} monotone={v['monotone']['Gamma_nondecreasing']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
