"""Log-log slopes of the atom-constant rungs against Lambda on FX_B, at every declared drift (0, 1/4, 1/2).

Reads NS/validation/B307_AUDIT_FIXTURES.json (produced by b307_run_fixtures.py; exact values rendered as floats) and
writes NS/validation/B307_SCALING.json.  Pure post-processing of synthetic results; no new model evaluation.
The planted rung 'true * Lambda^{1/2}' is kept only as a NON-EVIDENCE arithmetic check (class (c): the least-squares
slope is linear, so it is exactly +1/2 for any data; review C-8).
Class-(a) control (review F6): the documented claim "at drift 0 the TRUE atom functionals scale as Lambda^{1+j/2}"
is checked as |slope - (1 + j/2)| <= 0.05, j = 1, 2, 3, on functionals recomputed through b307_lib.Point; the SAME
check is then run on a mutant whose functionals are computed with |K_i| in place of K_i (sign cancellation removed,
through the same code path). The claim must hold for the true functionals and must FAIL for the mutant.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()


def slope(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


CLAIM_TOL = 0.05


def recompute_series(mutant: bool):
    """exact FX_B series at e = 0 through b307_lib.Point; mutant => |K_i| entrywise inside the functionals."""
    sys.path.insert(0, str(HERE))
    import b307_lib as L
    from fractions import Fraction as F
    lam, a = [], {1: [], 2: [], 3: []}
    for N in (4, 6, 8, 12, 16, 24):
        Q.guard_drift(F(0))
        kp, _, _ = L.score_walk(N)
        P = L.Point(kp, F(0), need_d3=False)
        K = [L.absm(k) for k in P.K] if mutant else P.K
        R = P.R
        RK1R = L.mm(R, K[1], R)
        d2 = L.madd(L.X.mat_scale(L.mm(RK1R, K[1], R), F(2)), L.mm(R, K[2], R))
        d3 = L.madd(L.X.mat_scale(L.mm(RK1R, K[1], RK1R), F(6)), L.X.mat_scale(L.mm(R, K[2], RK1R), F(3)),
                    L.X.mat_scale(L.mm(RK1R, K[2], R), F(3)), L.mm(R, K[3], R))
        lam.append(math.log(P.Lam))
        for j, M in ((1, RK1R), (2, d2), (3, d3)):
            a[j].append(math.log(L.row_l1(M)))
    slopes = {j: slope(lam, a[j]) for j in (1, 2, 3)}
    ok = all(abs(slopes[j] - (1 + j / 2)) <= CLAIM_TOL for j in (1, 2, 3))
    return slopes, ok


def main():
    d = json.loads((NS / "validation" / "B307_AUDIT_FIXTURES.json").read_text())
    pts = [p for p in d["P2_ladders"]["points"] if p["spec"]["class"] == "FX_B"]
    out = {}
    for e in ("0", "1/4", "1/2"):
        sel = [p for p in pts if p["spec"]["e"] == e]
        xs = [math.log(p["Lambda"]) for p in sel]
        rec = {"Lambda": [p["Lambda"] for p in sel], "C_T": [p["C_T"] for p in sel], "C": [p["C"] for p in sel]}
        for A in ("A1", "A2", "A3"):
            rec[A] = {lv: slope(xs, [math.log(p[A][lv]) for p in sel]) for lv in sel[0][A]}
        rec["C_T_slope"] = slope(xs, [math.log(p["C_T"]) for p in sel])
        rec["C_slope"] = slope(xs, [math.log(p["C"]) for p in sel])
        planted = slope(xs, [math.log(p["A1"]["true"] * math.sqrt(p["Lambda"])) for p in sel])
        rec["NON_EVIDENCE_class_c_linear_slope_plant"] = abs(planted - rec["A1"]["true"] - 0.5) < 1e-9
        out[e] = rec
    true_sl, true_ok = recompute_series(False)
    mut_sl, mut_ok = recompute_series(True)
    claim = {"claim": "drift 0: |slope(true A_j) - (1 + j/2)| <= 0.05, j = 1, 2, 3",
             "true_recomputed_slopes": true_sl, "claim_holds_for_true": true_ok,
             "class_a_mutant_absK_slopes": mut_sl, "class_a_mutant_fired": not mut_ok,
             "true_matches_json_fit": all(abs(true_sl[j] - out["0"]["A" + str(j)]["true"]) < 1e-9 for j in (1, 2, 3))}
    with open(NS / "validation" / "B307_SCALING.json", "w") as fh:
        json.dump({"schema": "P5Y_K5_TAIL_OVERNIGHT_B307_SCALING/2", "producer": "streams/B_307/code/b307_scaling.py",
                   "class": "SYNTHETIC_VALIDATION", "source": "validation/B307_AUDIT_FIXTURES.json",
                   "slopes_vs_Lambda_by_drift": out, "exponent_claim_check": claim}, fh, indent=1)
    print("claim", json.dumps(claim, default=str))
    Q.log_execution("streams/B_307/code/b307_scaling.py", "B307: FX_B log-log slopes of atom-constant rungs vs Lambda",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    for e, rec in out.items():
        print(e, {A: {k: round(v, 3) for k, v in rec[A].items()} for A in ("A1", "A2", "A3")},
              "C_T", round(rec["C_T_slope"], 3), "C", round(rec["C_slope"], 3),
              "Lambda", [round(x, 1) for x in rec["Lambda"]])


if __name__ == "__main__":
    main()
