"""Phase 3: every zero-new-real candidate route, evaluated or costed, with the reason each is kept or rejected.

Nothing here is a gate. The gate is frozen after this file has run and its output is disclosed in the gate as prior
evidence, exactly as Campaign C3 disclosed its own pre-freeze knowledge.

    python3 -B c4_routes.py --bound BOUND.json --thresholds TH.json --out OUT.json
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c4_common import C2, CP, OPEN_CELLS, cell_supply, committed_inputs, frozen_stack, gamma_at, sha  # noqa: E402

C1_NS = CP / "p5y_k5_tail_operator_registry"


def route_R4_reuse_only() -> dict:
    """The only route that needs no computation at all: E_a[tau] = tau_a / D >= 1 / D, with D from D_mid's UPPER end.

    tau_a = (Ghat_e 1)(a) >= 1 because Ghat >= I on non-negative functions (theorem AD, Lemma SM(a) proof).
    """
    per = {}
    for k in OPEN_CELLS:
        best = None
        for tag, p in (("C1", C1_NS / f"evidence/registry_c1/taboo_cell_{k}.json"),
                       ("C2", C2 / f"evidence/registry_c2/taboo_cell_{k}.json")):
            if p.exists():
                d = json.loads(p.read_bytes())
                if "D_mid" in d:
                    hi = F(d["D_mid"][1])
                    if best is None or hi < best[1]:
                        best = (tag, hi, sha(p))
        per[str(k)] = {"source": best[0], "D_at_e0_upper": str(best[1]),
                       "lower_bound_E_a_tau": str(1 / best[1]),
                       "lower_bound_float": float(1 / best[1]), "artifact_sha256": best[2]}
    return per


def diagnostic_truth() -> dict:
    """NOT A BOUND. Two independent committed float diagnostics of the true E_a[tau] at each cell midpoint.

    (a) the taboo proposal is w = alpha * g_float with beta = 0, so g_float(a) = tau / alpha, and the committed
        candidate value d0 at the atom estimates D; E_a[tau] ~ (tau / alpha) / d0;
    (b) the whole-kernel proposal records `float_sup_taboo_grid` = sup_x E_x[tau] on the float grid.
    They are produced by different code paths and are compared here rather than averaged.
    """
    per = {}
    for k in OPEN_CELLS:
        tb = json.loads((C1_NS / f"evidence/registry_c1/taboo_block_{k}.json").read_bytes())
        tc = json.loads((C1_NS / f"evidence/registry_c1/taboo_cell_{k}.json").read_bytes())
        ar = json.loads((C1_NS / f"evidence/registry_c1/arl_cell_{k}.json").read_bytes())
        if F(tb["proposal"]["beta"]) != 0:
            raise SystemExit(f"cell {k}: the taboo proposal is shifted; (a) is not available")
        a_est = (F(tb["tau"]) / F(tb["proposal"]["alpha"])) / F(tc["candidate_at_atom"]["d0"][0])
        b_est = ar["proposal"]["float_sup_taboo_grid"]
        per[str(k)] = {"e0": tc["e0"], "estimate_from_taboo_candidate": float(a_est),
                       "estimate_from_whole_kernel_grid": float(b_est),
                       "agreement_abs": abs(float(a_est) - float(b_est))}
    return per


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bound", required=True)
    ap.add_argument("--thresholds", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    L = json.loads(Path(a.bound).read_bytes())["cells"]
    TH = json.loads(Path(a.thresholds).read_bytes())["cells"]
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)

    R4 = route_R4_reuse_only()
    per = {}
    for k in OPEN_CELLS:
        meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
        row = {"A0_certified_float": float(s["A"]["A0"])}
        for tag, val in (("L_ladder_Wald", F(L[str(k)]["lower_bound_E_a_tau"])),
                         ("R4_reuse_only", F(R4[str(k)]["lower_bound_E_a_tau"]))):
            d = gamma_at(FC, T, R, B, meas, aux, ad5, cov, val, 0, 0)
            row[tag] = {"lower_bound": float(val), "Gamma_at_bound": float(d["Gamma"]),
                        "excludes_cell": bool(not d["pass"])}
        c = TH[str(k)]["critical_A0"]
        row["critical_A0_closes_below"] = c["closes_below"] if c else None
        row["A0_is_the_blocker"] = c is not None
        per[str(k)] = row

    out = {
        "schema": "rebaseguard.p5y.k5.tail-c4.routes.v1",
        "routes": {
            "L_ladder_Wald": {
                "rank": 1, "preference_class": "exact analytic inequality",
                "theorem": "E_a[tau] >= H / E[(|z| - K)^+] (c4_lower_bound.py, theorem L)",
                "assumptions": "frozen CUSUM geometry; K > 0; start at the atom; E[tau] < infinity (Lemma T)",
                "domain": "any single drift e in the closed cell; evaluated at e_lo",
                "existing_inputs": "K, H from the pinned frozen producer; e_lo from the cover ledger",
                "new_scientific_value_required": False, "kernel_evaluations": 0,
                "independent_of_disputed_surfaces": True,
                "note": "uses no Arb certificate, no registry constant and no candidate polynomial, so it is "
                        "independent of every surface C2 and C3 argued about",
                "status": "SELECTED"},
            "R4_reuse_only": {
                "rank": 2, "preference_class": "deterministic recombination of existing artifacts",
                "theorem": "E_a[tau] = tau_a / D >= 1 / D, with tau_a >= 1 and D from D_mid's upper end",
                "new_scientific_value_required": False, "kernel_evaluations": 0,
                "status": "EVALUATED, INSUFFICIENT",
                "note": "the only strictly-reuse route; reported with its numbers rather than dismissed"},
            "R1_taboo_defect_inversion": {
                "rank": 3, "preference_class": "direct transformation of an existing certified bound",
                "theorem": "w = Ghat 1 + Ghat g with g := w - 1 - Khat w >= 0, and (Ghat g)(a) <= tau_a sup g, "
                           "so tau_a >= w(a) / (1 + sup_X g); then E_a[tau] >= that / D_mid_hi",
                "existing_inputs": "the committed taboo candidate payload w and the frozen certifier",
                "new_scientific_value_required": True,
                "why": "the certifier records inf_X of the defect (margin_lower_bound) but discards sup_X, which is "
                       "the quantity this route needs; obtaining it is a re-run of certify_block, i.e. a new "
                       "operator certification, and python-flint is not present on this host",
                "status": "REJECTED: needs a new operator certification, and cannot change the verdict on 308"},
            "R2_whole_kernel_defect_inversion": {
                "rank": 4, "preference_class": "direct transformation of an existing certified bound",
                "theorem": "E_a[tau] >= Abar / (1 + sup_X G), G := W - 1 - K W",
                "new_scientific_value_required": True,
                "status": "REJECTED: the committed whole-kernel proposal is shifted (beta = 2), so sup G is at "
                          "least 2 sup h_1 and the bound is strictly weaker than R1"},
            "R3_truncated_neumann": {
                "rank": 5, "preference_class": "certified finite-state/operator inequality",
                "theorem": "E_a[tau] >= sum_{j<n} (K_e^j 1)(a), every term non-negative",
                "new_scientific_value_required": True,
                "status": "REJECTED: n kernel applications per cell, i.e. a new operator computation, with no "
                          "advantage over R1"},
            "R5_two_sided_tau_certificate": {
                "rank": 6, "preference_class": "certified operator inequality",
                "theorem": "a candidate t with |t - 1 - Khat t| <= eps gives tau_a in [t(a)/(1+eps), t(a)/(1-eps)]",
                "new_scientific_value_required": True,
                "status": "REJECTED HERE, RECOMMENDED TO A SUCCESSOR: sharpest of all, but it is a new Chebyshev "
                          "fit plus a new Arb certification, and it still cannot discharge 308"},
        },
        "route_results": per,
        "R4_detail": R4,
        "DIAGNOSTIC_true_E_a_tau_at_e0": diagnostic_truth(),
        "DIAGNOSTIC_note": ("measured, not asserted. These are float candidate values read out of committed "
                            "artifacts, not certified bounds, and nothing in the gate or the certificate depends "
                            "on them. They are recorded because they decide whether any route could discharge "
                            "cell 308, and the honest answer is that none can."),
        "new_real_scientific_addresses_evaluated": 0,
        "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    for k, v in per.items():
        print(f"cell {k}: A0_blocker={v['A0_is_the_blocker']} "
              f"L={v['L_ladder_Wald']['lower_bound']:.6f}->excl={v['L_ladder_Wald']['excludes_cell']}  "
              f"R4={v['R4_reuse_only']['lower_bound']:.6f}->excl={v['R4_reuse_only']['excludes_cell']}")
    print("diagnostic truth:", json.dumps(out["DIAGNOSTIC_true_E_a_tau_at_e0"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
