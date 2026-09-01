"""Evaluate the post-hoc H2 hypotheses on the cells that were held out.

`results/posthoc_preregistration_H2.json` was frozen while 7 of the 12 cells did
not exist.  This script tests it and writes the outcome beside it.  H2a-H2c are
**exploratory**: they are not closure gates and do not enter
`results/closure_decision.json`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8 import families as F                            # noqa: E402
from rebaseguard_p8.config import DETECTORS, FAMILIES, RESULTS      # noqa: E402


def main() -> None:
    pre = json.loads((RESULTS / "posthoc_preregistration_H2.json").read_text())
    mat = json.loads((RESULTS / "gamma_matrix_E1.json").read_text())
    idx = {(c["detector"], c["family"]): c for c in mat["cells"]}

    # --- H2a: detector invariance of the lag profile, r in 1..5 --------------
    rows_a = []
    for f in FAMILIES:
        a, b = idx[("cusum", f)], idx[("sr", f)]
        for r in range(1, 6):
            wa, wb = a["lag_profile_w"][r], b["lag_profile_w"][r]
            rel = wa / wb - 1.0
            rows_a.append({"family": f, "r": r, "w_cusum": wa, "w_sr": wb,
                           "relative_difference": rel,
                           "pass": bool(abs(rel) <= 0.05)})
    h2a = {"rows": rows_a, "n": len(rows_a),
           "n_pass": sum(r["pass"] for r in rows_a),
           "max_abs_relative": max(abs(r["relative_difference"]) for r in rows_a),
           "criterion": "|w_r(cusum,f)/w_r(sr,f) - 1| <= 0.05 for all 6 families, r in 1..5",
           "verdict": "SUPPORTED" if all(r["pass"] for r in rows_a) else "REJECTED"}

    # --- H2b: w_1 monotone decreasing in Fisher information ------------------
    fisher = {f: F.fisher_information(F.get(f)) for f in FAMILIES}
    predicted = pre["hypotheses"][
        "H2b_w1_is_monotone_decreasing_in_fisher_information"][
        "predicted_ordering_by_DECREASING_w1"]
    measured = {}
    for d in DETECTORS:
        w1 = {f: idx[(d, f)]["lag_profile_w"][1] for f in FAMILIES}
        measured[d] = {"w1": w1,
                       "ordering_by_decreasing_w1":
                           sorted(w1, key=lambda k: -w1[k])}
    h2b = {"fisher_information": fisher, "predicted_ordering": predicted,
           "measured": measured,
           "criterion": "measured ordering of w_1 equals the predicted ordering, in BOTH detectors",
           "verdict": ("SUPPORTED" if all(
               measured[d]["ordering_by_decreasing_w1"] == predicted
               for d in DETECTORS) else "REJECTED"),
           "where_it_fails": ("the contaminated families have LOWER Fisher "
                              "information than the Gaussian and were predicted to "
                              "have the LARGEST w_1; they measure among the "
                              "SMALLEST. The competing tail-heaviness reading, "
                              "which predicts the opposite for them, is the one "
                              "that survives.")}

    # --- H2c: K is a function of (m, w_1) alone ------------------------------
    cells = [(d, f) for d in DETECTORS for f in FAMILIES]
    pairs = []
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            a, b = idx[cells[i]], idx[cells[j]]
            w1a, w1b = a["lag_profile_w"][1], b["lag_profile_w"][1]
            if abs(w1a / w1b - 1.0) > 0.01:
                continue
            worst = max(abs(a["per_m"][str(m)]["K"] / b["per_m"][str(m)]["K"] - 1.0)
                        for m in (2, 3, 5))
            pairs.append({"cell_a": list(cells[i]), "cell_b": list(cells[j]),
                          "w1_a": w1a, "w1_b": w1b,
                          "same_family": cells[i][1] == cells[j][1],
                          "max_abs_K_relative_difference": worst,
                          "pass": bool(worst <= 0.01)})
    cross = [p for p in pairs if not p["same_family"]]
    h2c = {"qualifying_pairs": pairs, "n_pairs": len(pairs),
           "n_cross_family_pairs": len(cross),
           "criterion": "cells with w_1 within 1% have K(m) within 1% for m in {2,3,5}",
           "verdict": ("VACUOUS" if not pairs else
                       "SUPPORTED" if all(p["pass"] for p in pairs) else "REJECTED"),
           "weakness": ("same-family cusum/sr pairs qualify almost automatically, so "
                        "this test reduces to H2a unless cross-family pairs exist; "
                        f"{len(cross)} cross-family pair(s) qualified.")}

    out = {"schema": "rebaseguard.p8.posthoc-H2-evaluation.v1",
           "status": "EXPLORATORY -- not a closure gate",
           "preregistration": "results/posthoc_preregistration_H2.json",
           "H2a": h2a, "H2b": h2b, "H2c": h2c}
    (RESULTS / "posthoc_H2_evaluation.json").write_text(
        json.dumps(out, indent=1) + "\n")
    print(f"H2a {h2a['verdict']}  ({h2a['n_pass']}/{h2a['n']} pass, "
          f"max|rel|={h2a['max_abs_relative']*100:.2f}%)")
    print(f"H2b {h2b['verdict']}")
    for d in DETECTORS:
        print(f"   {d} measured: {measured[d]['ordering_by_decreasing_w1']}")
    print(f"   predicted   : {predicted}")
    print(f"H2c {h2c['verdict']}  ({h2c['n_pairs']} qualifying pairs, "
          f"{h2c['n_cross_family_pairs']} cross-family)")


if __name__ == "__main__":
    main()
