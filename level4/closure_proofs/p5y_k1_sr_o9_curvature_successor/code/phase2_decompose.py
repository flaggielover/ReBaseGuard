"""Phase 2 / Phase 3 (READ-ONLY; Phase 3 values are NON-CERTIFYING DIAGNOSTICS).

Exact decomposition of the committed T4 cover (T345 successor 8b8a242) into rho*mag(D_interval) and rho^2*M_R2/2,
of the R2_interval radius into its assembly terms, and of each refined eps_H_cell into the frozen H-closure terms
C*deltaH_cell + C*k2*eps_F_cell + C*2k1*eps_D_cell + C*eps_S2_cell.  Nominal R'(e0), R''(e0) are the frozen candidate
values at x0 (images: midpoint-mode certified x0 values).  The idealized cover uses nominal values with ZERO
propagated error and the same parent rho: it is a diagnostic, never evidence.
"""
import json
import re
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T
import t4_cell as T4

EV = T.CP / "p5y_k1_sr_o9_t345_successor/evidence"
NS = Path(__file__).resolve().parents[1]
CELLS = (150, 250, 275, 313, 315)
B = Fr(1, 20)


def num(s):
    return float(re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)[0])


def f(x):
    return float(Fr(x))


def midrad(r):
    lo, hi = Fr(r["lo"]), Fr(r["hi"])
    return float((lo + hi) / 2), float((hi - lo) / 2)


def main():
    out = {}
    for c in CELLS:
        t3 = json.loads((EV / f"t3/t3_c{c}.json").read_text())
        t4 = json.loads((EV / f"t4/t4_c{c}.json").read_text())
        built = T.build_cell_candidates(c)["scientific"]
        mant = {x["node"]: x["mantissas"] for x in built["candidates"]}
        rho, C = f(t4["rho_upper"]), f(t4["C_upper"])
        with T.scientific_precision():
            def x0(node):
                v = T4.cand_x0(mant[node]) if node in mant else T4.img_x0(t3["x0_images"]["mid"][node])
                return float(v.mid())
            Hdec = {}
            for r in range(5):
                s, i = t4["refinement"][str(r)]["summary"], t4["refinement"][str(r)]["inputs"]
                eH, eF, eD = num(s["eps_H_cell"]), num(s["eps_F_cell"]), num(s["eps_D_cell"])
                Cf, k1, k2 = f(i["C"]), f(i["k1"]), f(i["k2"])
                dHc, S2 = f(i["delta_H_cell"]), f(i["eps_S2_cell"])
                dHm = t3["delta"]["mid"][f"F:{r}:k2"]["delta_float"]
                terms = {"C*deltaH_cell": Cf * dHc, "C*k2*eps_F_cell": Cf * k2 * eF,
                         "C*2k1*eps_D_cell": Cf * 2 * k1 * eD, "C*eps_S2_cell": Cf * S2}
                Hdec[r] = {"eps_H_cell_refined": eH, "eps_H_cell_crude": f(i["eps_H_crude"]), **terms,
                           "terms_sum": sum(terms.values()), "deltaH_mid": dHm, "deltaH_cell": dHc,
                           "cell_over_mid": dHc / dHm if dHm else None,
                           "share_deltaH": Cf * dHc / sum(terms.values()),
                           "iterations": s["iterations"], "contraction": num(s["contraction"]),
                           "sup_H_hat": f(i["sup_H_hat"]), "sup_D_hat": f(i["sup_D_hat"])}
            per_m = {}
            for m in (1, 2, 3, 5):
                L = t4["m"][str(m)]
                coefs = T4.assembly.coefficients(m)
                Rp = sum(float(cf) * x0(f"F:{r}:k1" if kd == "F" else T4.wnode(r, j, 1)) for kd, r, j, cf in coefs)
                Rpp = sum(float(cf) * x0(f"F:{r}:k2" if kd == "F" else T4.wnode(r, j, 2)) for kd, r, j, cf in coefs)
                R0 = sum(float(cf) * x0(f"F:{r}:k0" if kd == "F" else T4.wnode(r, j, 0)) for kd, r, j, cf in coefs)
                rad_terms = {}
                for kd, r, j, cf in coefs:
                    rec = t4["x0_enclosures"]["H"][str(r)] if kd == "F" else t4["x0_enclosures"]["W"]["2"][f"{r},{j}"]
                    rad_terms[(f"H_{r}" if kd == "F" else f"W''_{r},{j}")] = abs(float(cf)) * midrad(rec)[1]
                R2c, R2r = midrad(L["R2_interval"])
                Dc, Dr = midrad(L["D_interval"])
                Rc, Rr = midrad(L["R_interval"])
                M = f(L["M_R2"])
                ch = {k: f(v) for k, v in L["cover"]["children"].items()}
                ideal = rho * abs(Rp) + rho * rho * abs(Rpp) / 2
                tgt_hw = Rr + ideal
                per_m[m] = {
                    "rho": rho, "B_cover_ratio": L["B_cover_ratio"], "gate_margin_abs": float(B) - L["B_cover_ratio"] * float(B),
                    "first_order_rho_magD": rho * max(abs(Dc - Dr), abs(Dc + Dr)), "curvature_rho2_MR2_half": rho * rho * M / 2,
                    "children": ch, "D_interval": [Dc - Dr, Dc + Dr], "M_R2": M, "R2_centre": R2c, "R2_radius": R2r,
                    "R2_radius_terms": rad_terms,
                    "nominal_Rprime_e0": Rp, "nominal_Rsecond_e0": Rpp, "nominal_R_e0": R0,
                    "inflation_MR2_over_nominal": M / abs(Rpp) if Rpp else None,
                    "IDEALIZED_B_cover_ratio_DIAGNOSTIC": ideal / float(B),
                    "IDEALIZED_first_order_share": rho * abs(Rp) / float(B),
                    "IDEALIZED_curvature_share": rho * rho * abs(Rpp) / 2 / float(B),
                    "target_gate_current": L["target_gate"]["status"],
                    "target_gate_with_zero_curvature_error_DIAGNOSTIC": ("PASS" if (abs(Rc) + tgt_hw) < 2 else "FAIL"),
                    "target_ideal_interval": [Rc - tgt_hw, Rc + tgt_hw]}
        out[str(c)] = {"rho": rho, "C_upper": C, "e0": t4["e0"], "H_closure_decomposition": Hdec, "m": per_m}
        print(f"== cell {c}  rho {rho:.4g}  C {C:.4g}")
        for r, h in Hdec.items():
            print(f"   H_{r}: eps_H {h['eps_H_cell_refined']:.4g} (crude {h['eps_H_cell_crude']:.3g}) = C*dH {h['C*deltaH_cell']:.3g} + C*k2*eF {h['C*k2*eps_F_cell']:.3g}"
                  f" + C*2k1*eD {h['C*2k1*eps_D_cell']:.3g} + C*S2 {h['C*eps_S2_cell']:.3g} | dH_mid {h['deltaH_mid']:.3g} dH_cell {h['deltaH_cell']:.3g}"
                  f" (x{h['cell_over_mid']:.3g}) | iters {h['iterations']} kappa' {h['contraction']:.3f}")
        for m, p in per_m.items():
            print(f"   m{m}: Bcov {p['B_cover_ratio']:.4g} = 1st {p['first_order_rho_magD']/0.05:.4g} + curv {p['curvature_rho2_MR2_half']/0.05:.4g} |"
                  f" M_R2 {p['M_R2']:.4g} vs nominal R'' {p['nominal_Rsecond_e0']:.4g} (x{p['inflation_MR2_over_nominal']:.3g}) |"
                  f" IDEAL {p['IDEALIZED_B_cover_ratio_DIAGNOSTIC']:.4f} (1st {p['IDEALIZED_first_order_share']:.4f} curv {p['IDEALIZED_curvature_share']:.2e}) |"
                  f" target now {p['target_gate_current']} ideal {p['target_gate_with_zero_curvature_error_DIAGNOSTIC']}")
            top = sorted(p["R2_radius_terms"].items(), key=lambda kv: -kv[1])[:3]
            print("        R2 radius top terms:", [(k, f"{v:.3g}") for k, v in top])
    (NS / "evidence/phase2_decomposition.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
