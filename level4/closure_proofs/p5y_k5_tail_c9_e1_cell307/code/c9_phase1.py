"""C9 Phase 1 -- reconstruct cell 307 exactly, independently, and cross-check against C8.

If C8's 1.0960072461461898x closure target cannot be independently reproduced, C9 does not proceed.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c9_common as C
import c9_chain as X

K1 = F(7978846, 10 ** 7)
K2 = F(9678830, 10 ** 7)
CELL = 307


def main() -> int:
    ch = X.Chain()
    blk2 = ch.blocks2[CELL]
    sup2 = ch.supply_from_block(CELL, blk2, K1, K2)
    sup1 = ch.supply_from_block(CELL, ch.blocks1[CELL], K1, K2)
    supplies = {"C1": sup1, "C2": sup2}
    # C3's mechanism: componentwise-BEST OPERATOR tuple first, THEN Lemma Dv'. Applying a
    # componentwise minimum at the A level instead gives a different (weaker) supply -- that was
    # this module's first error and it produced C2's numbers, not the operative ones.
    best_tuple = ch.operator_best({"C1": ch.blocks1[CELL], "C2": ch.blocks2[CELL]})
    mixed = ch.atom_constants(best_tuple["Abar"], best_tuple["tau"], best_tuple["C_T"],
                              best_tuple["D_lo"], best_tuple["D1"], best_tuple["D2"], K1, K2)
    supplies["operator_mixed"] = mixed

    c8 = C.load(C.C8 / "evidence" / "phase9" / "C8_ADOPTION.json")["per_cell"][str(CELL)]
    c3 = C.load(C.CLOSURE / "p5y_k5_tail_c3_closure" / "evidence" / "phase_c1" /
                "C3_BLOCKER.json")["cells"][str(CELL)]["per_supply"]["operator_mixed"]["A"]

    bud = ch.budget_C5T(CELL)
    Mnow = ch.M_of(CELL, mixed)
    gam = ch.gamma(CELL, mixed)

    def scaled_passes(s):
        return ch.M_of(CELL, {j: mixed[j] * s for j in ("A0", "A1", "A2")}) < bud

    lo, hi = F(1, 1000), F(8)
    while scaled_passes(hi):
        hi *= 2
    if scaled_passes(F(1)):
        raise SystemExit("cell 307 already passes -- contradicts C8")
    for _ in range(72):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if scaled_passes(mid) else (lo, mid)
    s_star = lo
    close_x = 1 / s_star
    adopt_x = F(5, 4) / s_star

    dA = {j: abs(float(mixed[j]) - c3[j]) for j in ("A0", "A1", "A2")}
    d_close = abs(float(close_x) - c8["uniform_eff_tightening_to_close"])
    d_adopt = abs(float(adopt_x) - c8["uniform_eff_tightening_to_be_ADOPTABLE"])
    d_gam = abs(float(gam) - c8["Gamma_now"])
    d_M = abs(float(Mnow) - c8["M_now"])
    agree = max(list(dA.values()) + [d_close, d_adopt, d_gam, d_M]) < 1e-9

    out = {
        "schema": "C9_PHASE1/1", "target": {"detector": "CUSUM", "m": 5, "cell": CELL},
        "independent": ("derived from tct_rule, ADOPTED_TAIL_INPUTS, TCT_INPUTS, REGISTRY_C1/C2 and "
                        "C5_FORECAST; imports no C8 module"),
        "geometry": {k: str(v) for k, v in ch.geom[CELL].items()},
        "current_supply": {
            "certified_supplies_available": sorted(supplies),
            "operator_best_tuple": {k: str(v) for k, v in best_tuple.items()},
            "operator_best_rule": "MIN over (Abar,tau,C_T,D1,D2); MAX over D_lo; then Lemma Dv'",
            "per_supply_eff": {n: str(s["eff"]) for n, s in supplies.items()},
            "operative_mixed": {j: str(mixed[j]) for j in ("eff", "A0", "A1", "A2")},
            "operative_mixed_float": {j: float(mixed[j]) for j in ("eff", "A0", "A1", "A2")},
            "lemma": "Dv': eff = min(Abar, tau/D_lo); A1,A2 = eff * fixed multipliers",
            "eff_binds_on": ("tau/D_lo" if F(blk2["tau"]) / F(blk2["D_lo"]) < F(blk2["Abar"])
                             else "Abar"),
            "Abar": blk2["Abar"], "tau": blk2["tau"], "D_lo": blk2["D_lo"],
            "C_T": blk2["C_T"], "D1": blk2["D1"], "D2": blk2["D2"]},
        "sealed_clip": {"M_R2": str(ch.M0[CELL]), "M_R2_float": float(ch.M0[CELL]),
                        "R2_interval": [str(x) for x in ch.H[CELL]],
                        "clip_binds_now": bool(ch.M0[CELL] <= max(abs(x) for x in ch.enclosure(CELL, mixed)))},
        "consumer_C5T": {"M_needed_C5T": str(bud), "M_needed_C5T_float": float(bud),
                         "M_now": str(Mnow), "M_now_float": float(Mnow),
                         "g_hi": str(ch.g_hi[CELL]), "Gamma_now": float(gam),
                         "verdict_now": "OPEN (Gamma >= 0)" if gam >= 0 else "PASSES"},
        "thresholds_independently_derived": {
            "largest_uniform_scaling_that_passes": str(s_star),
            "SCIENTIFIC_CLOSURE_uniform_eff_tightening": float(close_x),
            "GOVERNANCE_ADOPTION_uniform_eff_tightening": float(adopt_x),
            "required_new_eff_for_closure": float(mixed["eff"] / close_x),
            "required_new_eff_for_adoption": float(mixed["eff"] / adopt_x),
            "adoption_floor": "C2_ADJUDICATION section K: F1 supply-independence OR F2 margin >= 1.25",
            "DISTINCTION": ("SCIENTIFIC_CLOSURE is Gamma < 0. GOVERNANCE_ADOPTION additionally "
                            "requires the binding C2 floor. C9 must not substitute one for the other.")},
        "cross_check_vs_C8": {
            "A_abs_err": dA, "closure_abs_err": d_close, "adoption_abs_err": d_adopt,
            "Gamma_abs_err": d_gam, "M_abs_err": d_M, "agree": bool(agree),
            "C8_closure": c8["uniform_eff_tightening_to_close"],
            "C8_adoption": c8["uniform_eff_tightening_to_be_ADOPTABLE"]},
    }
    if not agree:
        out["HARD_STOP"] = "C8's cell-307 thresholds could not be independently reproduced"
    s = C.write_evidence(C.NS / "evidence" / "phase1" / "C9_PHASE1.json", out)
    cs = out["current_supply"]
    print(f"cell 307 geometry: e in [{float(ch.geom[CELL]['e_lo']):.7f}, {float(ch.geom[CELL]['e_hi']):.7f}]")
    print(f"eff binds on      : {cs['eff_binds_on']}")
    print(f"current eff       : {cs['operative_mixed_float']['eff']:.12f}")
    print(f"A0/A1/A2          : {cs['operative_mixed_float']['A0']:.9f} / "
          f"{cs['operative_mixed_float']['A1']:.9f} / {cs['operative_mixed_float']['A2']:.9f}")
    print(f"M_R2 clip         : {float(ch.M0[CELL]):.9f}   M now {float(Mnow):.9f}   "
          f"budget {float(bud):.9f}")
    print(f"Gamma now         : {float(gam):+.12f}  -> {out['consumer_C5T']['verdict_now']}")
    t = out["thresholds_independently_derived"]
    print(f"\nCLOSURE  tightening {t['SCIENTIFIC_CLOSURE_uniform_eff_tightening']:.13f}  "
          f"-> new eff <= {t['required_new_eff_for_closure']:.12f}")
    print(f"ADOPTION tightening {t['GOVERNANCE_ADOPTION_uniform_eff_tightening']:.13f}  "
          f"-> new eff <= {t['required_new_eff_for_adoption']:.12f}")
    x = out["cross_check_vs_C8"]
    print(f"\ncross-check vs C8: agree={x['agree']}  closure err {x['closure_abs_err']:.2e}  "
          f"adoption err {x['adoption_abs_err']:.2e}  Gamma err {x['Gamma_abs_err']:.2e}")
    print(f"wrote evidence/phase1/C9_PHASE1.json sha256 {s[:16]}...")
    return 0 if agree else 1


if __name__ == "__main__":
    raise SystemExit(main())
