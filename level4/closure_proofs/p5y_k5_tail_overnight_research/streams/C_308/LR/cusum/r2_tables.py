"""Producer of Appendix V of C1B_ROUTE_SUMMARY.md (LATENT-PROXY values, R2.3): reads NS/validation/C1B_R2_SUMMARY.json
and C1B_R2_MC.json and prints markdown tables.  No kernel evaluation.  Output: logs/appendix_V.md"""
from __future__ import annotations

import json
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[3]


def f(v, nd=4):
    x = v["float"] if isinstance(v, dict) else v
    return f"{x:.{nd}g}"


def main():
    S = json.loads((NS / "validation" / "C1B_R2_SUMMARY.json").read_text())
    order = sorted(S["drifts"], key=lambda k: float(F(k)))
    L = ["Source: `NS/validation/C1B_R2_SUMMARY.json` (producer `c1b_report.py R2_PW`), tables printed by `r2_tables.py`.",
         "Ladder minima (maxima for lower bounds) over the certified pinned rungs d in {4, 6, 8}; exact rationals in the JSON.", "",
         "**V.1 Certified inputs (pointwise).**", "",
         "| e | tau | tau_a,lo | C_T | C_R | A-bar | Lambda_lo | D_lo | D1 | D2 | S2^ | T_N | L1 | L2 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in order:
        c = S["drifts"][e]["certified"]
        L.append("| " + " | ".join([e] + [f(c[k]) for k in ("tau", "tau_a_lo", "C_T", "C_R", "A_bar", "Lambda_lo", "D_lo",
                                                             "D1", "D2", "S2_up", "TN_up", "L1_up", "L2_up")]) + " |")
    L += ["", "**V.2 Supplies (same certified inputs).** SUPPLY = D14 combined supply (only it is guaranteed <= Dv' and <= G).", "",
          "| e | rho1 | kappa1 C_T | rho2 | Dv' rho2-factor | A1 RLR | A1 Dv' | A1 G | A1 SUPPLY | A2 RLR | A2 Dv' | A2 G | A2 SUPPLY | Dv'/RLR A1 | Dv'/RLR A2 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in order:
        c = S["drifts"][e]["certified"]
        L.append("| " + " | ".join([e] + [f(c[k]) for k in ("rho1", "rho1_Dv", "rho2", "rho2_Dv", "A1_RLR", "A1_Dv", "G1",
                                                             "A1_SUPPLY", "A2_RLR", "A2_Dv", "G2", "A2_SUPPLY",
                                                             "ratio_A1_Dv_over_RLR", "ratio_A2_Dv_over_RLR")]) + " |")
    for name, b in S["blocks"].items():
        c = b["certified"]
        L += ["", f"**V.3 Block-uniform ({name}).** " + b["statement"], "",
              "| tau | C_T | A-bar | D_lo | D1 | D2 | L1 | L2 | A1 RLR | A1 Dv' | A1 SUPPLY | A2 RLR | A2 Dv' | A2 SUPPLY |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
              "| " + " | ".join(f(c[k]) for k in ("tau", "C_T", "A_bar", "D_lo", "D1", "D2", "L1_up", "L2_up", "A1_RLR",
                                                  "A1_Dv", "A1_SUPPLY", "A2_RLR", "A2_Dv", "A2_SUPPLY")) + " |"]
    L += ["", "**V.4 NON-CERTIFIED context (MC, N = 200000, seed 12345; float fairness Dv' with float C_T).**", "",
          "| e | MC tau_a | MC D | MC Lambda | MC L1 | MC L2 | Dv'/RLR A1 with float C_T |", "|---|---|---|---|---|---|---|"]
    for e in order:
        v = S["drifts"][e]
        m = v.get("MC_NONCERTIFIED", {})
        fc = v.get("Dv_with_float_C_T_NONCERTIFIED", {})
        L.append(f"| {e} | {f(m['sigma']['mean'])} | {f(m['alarm']['mean'])} | {f(m['Lambda_renewal'])} | "
                 f"{f(m['L1']['mean'])} | {f(m['L2']['mean'])} | {f(fc.get('ratio_A1_Dv_over_RLR', float('nan')))} |")
    (HERE / "logs" / "appendix_V.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:6]))


if __name__ == "__main__":
    main()
