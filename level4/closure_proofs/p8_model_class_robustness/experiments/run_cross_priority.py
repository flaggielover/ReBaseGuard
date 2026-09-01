"""Cross-priority consistency: P8's independent measurement of three estimands.

Priority 4 and Stage-D D3 report numbers that look like they disagree by up to
a factor of 38 on the same family, threshold and window.  P8 measures **all
three** estimands on its own field, in one pass, and reports which historical
number each one reproduces.

    Gamma_A       = E[ zbar^A_m  * sum psi(z_t) ]   raw window x family score
                    -> the derivative of the FROZEN raw-mean reference map
                       (P8-T1); the m=1 case is P4's ``Gamma_f``
    Gamma_psipsi  = E[ psibar^A_m * sum psi(z_t) ]   score window x score sum
                    -> Stage-D D3's frozen ``Gamma_psi``: the derivative of a
                       hypothetical SCORE-TRANSFORMED reuse rule, which is NOT
                       the frozen ReBaseGuard update
    Gamma_naive   = E[ zbar^A_m  * sum z_t ]        raw window x GAUSSIAN score
                    -> Stage-D's ``gamma_T_naive_DIAGNOSTIC_ONLY``; what a
                       Gaussian-score analysis would report on non-Gaussian data

P8 does not edit, adjudicate or re-open P4 or Stage D.  It reports.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
sys.path.insert(0, str(HERE / "experiments"))
from aggregate_gamma import _bm, load_cell                          # noqa: E402
from rebaseguard_p8.analysis import Z95, combined_z                 # noqa: E402
from rebaseguard_p8.config import (                                 # noqa: E402
    FAMILIES, P7, RESULTS, STAGE_D, p3_boundaries, p4_correspondence,
    stage_d_gamma_psi)


def sr_gain_three_way() -> dict:
    """P3 vs P7 vs P8 on the frozen Gaussian SR gain.

    P7 recorded that its SR estimate sits below P3's at every ``m`` with the same
    sign and magnitude, sharpened it at P3's own sample size
    (``p7/results/sr_gain_check.json``), and explicitly did **not** resolve it,
    since P7 does not own those numbers.  P8 is a third independent
    implementation on a different primitive field; this table says which of the
    two it agrees with.  P8 does not own or resolve them either.
    """
    p7 = json.loads((P7 / "results" / "sr_gain_check.json").read_text())
    p3 = p3_boundaries()
    cell = json.loads((RESULTS / "gamma" / "E1_sr_gaussian.json").read_text())
    nb = cell["n_batches"]
    rows = []
    for r in p7["rows"]:
        if r["detector"] != "sr":
            continue
        m = int(r["m"])
        v = np.array([b["gamma_A"][str(m)] for b in cell["batches"]])
        g8, s8 = float(v.mean()), float(v.std(ddof=1) / np.sqrt(nb))
        rows.append({
            "m": m,
            "p3_gamma": p3[("sr", m)]["gamma_tilde"],
            "p3_se": p3[("sr", m)]["gamma_tilde_se"],
            "p7_gamma": r["p7_gamma"], "p7_se": r["p7_batch_se"],
            "p8_gamma": g8, "p8_se": s8,
            "z_p8_vs_p3": combined_z(g8, s8, p3[("sr", m)]["gamma_tilde"],
                                     p3[("sr", m)]["gamma_tilde_se"]),
            "z_p8_vs_p7": combined_z(g8, s8, r["p7_gamma"], r["p7_batch_se"]),
            "relative_p8_vs_p3": g8 / p3[("sr", m)]["gamma_tilde"] - 1.0,
            "relative_p8_vs_p7": g8 / r["p7_gamma"] - 1.0})
    return {
        "note": ("P8 agrees with P7 and both sit below P3 at every m, with the "
                 "same sign and magnitude P7 reported. P8 neither owns nor "
                 "resolves the P3 numbers; this is a third independent "
                 "measurement recorded for whoever does."),
        "rows": rows}


def main() -> None:
    d3 = json.loads((STAGE_D / "results" / "d3_nongaussian.json").read_text())
    naive_ref = {r["family"]: {int(p["m"]): p["gamma_T_naive_DIAGNOSTIC_ONLY"]
                               for p in r["per_m"]} for r in d3["rows"]}
    psi_ref = stage_d_gamma_psi()
    p4 = p4_correspondence()
    rows = []
    for f in FAMILIES:
        cell = load_cell("cusum", f, "E1")
        if cell is None:
            continue
        nb = cell["n_batches"]

        def est(key, m):
            v = _bm(cell, (key, str(m)))
            return float(v.mean()), float(v.std(ddof=1) / np.sqrt(nb))

        row = {"family": f, "detector": "cusum", "threshold": cell["threshold"],
               "n_cycles": cell["n_cycles"], "per_m": {}}
        for m in (1, 5, 20):
            gA, sA = est("gamma_A", m)
            gP, sP = est("gamma_psipsi", m)
            gN, sN = est("gamma_naive", m)
            rec = {"gamma_A": gA, "gamma_A_se": sA,
                   "gamma_psipsi": gP, "gamma_psipsi_se": sP,
                   "gamma_naive": gN, "gamma_naive_se": sN,
                   "wrong_score_inflation_naive_over_A": gN / gA,
                   "stage_d_gamma_psi": psi_ref[f][m][0],
                   "stage_d_gamma_psi_se": psi_ref[f][m][1],
                   "stage_d_gamma_T_naive": naive_ref[f][m],
                   "z_vs_stage_d_gamma_psi": combined_z(
                       gP, sP, psi_ref[f][m][0], psi_ref[f][m][1]),
                   "relative_vs_stage_d_gamma_psi":
                       gP / psi_ref[f][m][0] - 1.0,
                   "relative_vs_stage_d_gamma_T_naive":
                       gN / naive_ref[f][m] - 1.0}
            if m == 1:
                rec["p4_gamma_f"] = p4[f]["gamma_f"]
                rec["p4_gamma_f_se"] = p4[f]["gamma_f_se"]
                rec["z_vs_p4_gamma_f"] = combined_z(gA, sA, p4[f]["gamma_f"],
                                                    p4[f]["gamma_f_se"])
                rec["relative_vs_p4_gamma_f"] = gA / p4[f]["gamma_f"] - 1.0
                rec["p4_over_stage_d_apparent_disagreement"] = (
                    p4[f]["gamma_f"] / psi_ref[f][1][0])
            row["per_m"][str(m)] = rec
        rows.append(row)
    out = {
        "schema": "rebaseguard.p8.cross-priority-consistency.v1",
        "finding": (
            "P4's Gamma_f and Stage-D D3's Gamma_psi are DIFFERENT ESTIMANDS, not "
            "disagreeing measurements of one. P4 weights the RAW convention-A "
            "window by the family score sum; Stage-D weights the SCORE-TRANSFORMED "
            "window by the same score sum. P8 measures both on its own field and "
            "reproduces each against its own source. The apparent factor-of-3-to-38 "
            "gap between the two published numbers is entirely definitional."),
        "which_estimand_is_the_frozen_reference_map_derivative": (
            "Gamma_A. The frozen update is e_{j+1} = rho (e_j + zbar^A_m) + "
            "(1-rho) mu_fresh with zbar^A_m a RAW mean (level4/src frozen model; "
            "P5 T1; P8-L0), so the reference-map multiplier is rho(1 - Gamma_A). "
            "Gamma_psi is the multiplier of a score-transformed reuse rule that "
            "no ReBaseGuard artifact implements."),
        "p8_does_not_adjudicate": (
            "P8 owns neither artifact and edits neither. Stage D remains "
            "STAGE-D-PARTIAL; P4 remains LOCATION-FAMILY-THEOREM-PARTIAL."),
        "rows": rows,
        "frozen_gaussian_sr_gain_three_way": sr_gain_three_way()}
    (RESULTS / "cross_priority_consistency.json").write_text(
        json.dumps(out, indent=1) + "\n")
    print(f"{'family':12s} {'P8 G_A(1)':>10s} {'P4 G_f':>9s} {'z':>6s} | "
          f"{'P8 G_psipsi':>11s} {'StageD':>9s} {'z':>7s} | {'naive/A':>8s}")
    for r in rows:
        a = r["per_m"]["1"]
        print(f"{r['family']:12s} {a['gamma_A']:10.4f} {a['p4_gamma_f']:9.4f} "
              f"{a['z_vs_p4_gamma_f']:+6.2f} | {a['gamma_psipsi']:11.4f} "
              f"{a['stage_d_gamma_psi']:9.4f} {a['z_vs_stage_d_gamma_psi']:+7.2f} | "
              f"{a['wrong_score_inflation_naive_over_A']:8.2f}x")


if __name__ == "__main__":
    main()
