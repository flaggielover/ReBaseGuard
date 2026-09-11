"""Stop-rule analysis after OPERATOR_NORM_TIGHTENING_INSUFFICIENT (NON-CERTIFYING, diagnostic only).

Decomposes the refined cell-uniform H error eps_H_cell of every F_r at cell 313, under the certified norms and under
the oracle norms, into the terms of the frozen sr_refine closure
    nH = C * (deltaH_cell + k2*nF + 2*k1*nD + epsS2_cell),   nD = epsD_mid + rho*supH,   supH = sup|H_hat| + nH,
and reports the M_R2 each m would need to reach B_cover <= 1/20 with its D_interval unchanged.
"""
import json
import re
import sys
from pathlib import Path

import oracle_norms as O

NS = Path(__file__).resolve().parents[1]
BALL = re.compile(r"\[([-0-9.e+]+)")


def num(x):
    x = str(x)
    m = BALL.match(x)
    return float(m.group(1)) if m else float(O.T4.Fr(x))


def decompose(r4):
    out = {}
    for r, tr in sorted(r4["refinement"].items(), key=lambda kv: int(kv[0])):
        i, s = tr["inputs"], tr["summary"]
        C, k1, k2 = num(i["C"]), num(i["k1"]), num(i["k2"])
        nF, nD, nH = num(s["eps_F_cell"]), num(s["eps_D_cell"]), num(s["eps_H_cell"])
        parts = {"C*deltaH_cell (mean-value residual)": C * num(i["delta_H_cell"]),
                 "C*k2*nF (value chain)": C * k2 * nF,
                 "C*2k1*nD (parent-rho derivative feedback)": C * 2 * k1 * nD,
                 "C*epsS2_cell (source chain)": C * num(i["eps_S2_cell"])}
        out[str(r)] = {"eps_H_cell": nH, "parts": parts, "parts_sum": sum(parts.values()),
                       "nD": nD, "nD_rho_supH_share": 1 - num(i["eps_D_mid"]) / nD if nD else None,
                       "sup_H_hat": num(i["sup_H_hat"]), "contraction": num(s["contraction"])}
    return out


def main():
    O.T.check_threads()
    ids = {"K0", "K1", "K2", "K3", "Kz0", "Kz1", "Kz2", "Kz3"}
    base, _, r4b, SV = O.run(set())
    orc, _, r4o, _ = O.run(ids, SV=SV)
    rho = float(O.T4.Fr(r4b["rho_upper"]))
    need = {}
    for m in ("1", "2", "3", "5"):
        D = orc["D_mag"][m]
        need[m] = {"rho": rho, "D_mag_oracle": D, "M_R2_certified": base["M_R2"][m], "M_R2_oracle": orc["M_R2"][m],
                   "M_R2_max_for_ratio_1": (0.05 - rho * D) / (rho * rho / 2),
                   "required_reduction_factor_vs_oracle": orc["M_R2"][m] / ((0.05 - rho * D) / (rho * rho / 2))}
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.opnorm-next-blocker.v1", "cell": 313, "DIAGNOSTIC_ONLY": True,
           "decomposition_certified_norms": decompose(r4b), "decomposition_oracle_norms": decompose(r4o),
           "cover_requirement": need,
           "R2_assembly_coefficients": {m: [list(map(str, c)) for c in O.T4.assembly.coefficients(int(m))] for m in ("2", "3", "5")}}
    (NS / "evidence/phase3_next_blocker_c313.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for lab in ("decomposition_certified_norms", "decomposition_oracle_norms"):
        print(lab)
        for r, d in out[lab].items():
            print(f"  F{r} epsH {d['eps_H_cell']:.4g} (sum {d['parts_sum']:.4g}) supHhat {d['sup_H_hat']:.3g} "
                  + " | ".join(f"{k.split(' ')[0]} {v:.3g}" for k, v in d["parts"].items()))
    for m, d in need.items():
        print(m, {k: round(v, 4) for k, v in d.items()})


if __name__ == "__main__":
    main()
