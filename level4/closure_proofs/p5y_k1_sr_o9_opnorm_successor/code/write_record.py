"""Write the immutable record and RESULT.md of the operator-norm round from committed evidence only."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
EV = NS / "evidence"
CLASS = "OPERATOR_NORM_TIGHTENING_INSUFFICIENT"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p1 = json.loads((EV / "phase1_doctrine.json").read_text())
    orc = json.loads((EV / "phase23_oracle_c313.json").read_text())
    nb = json.loads((EV / "phase3_next_blocker_c313.json").read_text())
    det = (EV / "replay/determinism.txt").read_text().split("\n")
    V = orc["variants"]
    M = ("1", "2", "3", "5")
    ms = ("2", "3", "5")
    req = nb["cover_requirement"]
    nominal_R2 = {"1": 0.24950408168875704, "2": 0.12493124565265834, "3": 0.1259874278576394, "5": 0.12598742960242718}
    target = {m: {"M_R2_max": req[m]["M_R2_max_for_ratio_1"],
                  "cell_H_error_budget_after_nominal": req[m]["M_R2_max_for_ratio_1"] - nominal_R2[m],
                  "aux3_style_requirement": "rho*|R'''(e0)| + (rho^2/2)*T[R,4] <= %.4g, i.e. |R'''(e0)| + %.4f*T[R,4] <= %.4g"
                  % (req[m]["M_R2_max_for_ratio_1"] - nominal_R2[m], req[m]["rho"] / 2,
                     (req[m]["M_R2_max_for_ratio_1"] - nominal_R2[m]) / req[m]["rho"])} for m in ms}
    rec = {
        "schema": "rebaseguard.p5y.k1.sr.o9.opnorm-successor-record.v1",
        "parent_commit": "804e387", "parent_tag": "p5y-k1-sr-o9-curvature-successor-not-closing",
        "classification": CLASS,
        "phase1": {"ruling": p1["ruling"], "answers": p1["answers"], "evidence_sha256": sha(EV / "phase1_doctrine.json")},
        "phase2_3": {"evidence_sha256": sha(EV / "phase23_oracle_c313.json"), "DIAGNOSTIC_ONLY": True,
                     "oracle_method": "exact norms sup_y int|kernel| attained at the reset state y0=(0,0): ||K^(i)|| = "
                                      "int_{-c+e}^{c+e}|He_i|phi, ||K_z^(i)|| = int_{-c+e}^{c+e}|w-e||He_i(w)|phi(w)dw; "
                                      "double-precision Gauss-Legendre between sign changes, point value at e0 for the midpoint "
                                      "DAG, max over an 81-point e-grid of the parent cell for cell DAG / mean-value envelope / "
                                      "refinement, +1e-6 relative; every other certified term unchanged",
                     "B_cover_ratio": {k: V[k]["ratio"] for k in V}, "M_R2": {k: V[k]["M_R2"] for k in V},
                     "norm_table": orc["norm_table"],
                     "ALL_NORMS_closes_m2_m3_m5": orc["ALL_NORMS_closes_m2_m3_m5"]},
        "stop_rule": "2: oracle-tight norms cannot bring m=2,3,5 below 1 -> Phase 4 (rigorous drift-aware norms), Phase 5 "
                     "(kill test), Phase 6 (controls) NOT run; no rigorous norm successor built",
        "phases_not_run": {"4": "stop rule 2", "5": "stop rule 2", "6": "313 not closed", "7": "no successor to cost"},
        "next_blocker": {"evidence_sha256": sha(EV / "phase3_next_blocker_c313.json"),
                         "identity": "NORM_ONLY_UNIFORM_CELL_H_CASCADE: the cell-uniform eps_H of F_1..F_4 is carried by the "
                                     "mean-value residual (F_1), the parent-rho derivative feedback C*2k1*(epsD_mid+rho*supH) "
                                     "and the source cascade C*epsS2 (F_2..F_4), while sup|H_hat| of F_2..F_4 is 1e-2..1e-12",
                         "decomposition_oracle_norms": nb["decomposition_oracle_norms"],
                         "decomposition_certified_norms": nb["decomposition_certified_norms"],
                         "cover_requirement": req},
        "escalation": {
            "requires_CUSUM_AUX3_STYLE_THIRD_DERIVATIVE_EVIDENCE": True,
            "reason": "the frozen sr_refine already applies the aux3 Taylor alternative at orders 0 and 1 (nF, nD); order 2 "
                      "(H) has no Taylor alternative because it needs X'''(e0), which no frozen candidate provides. Norms "
                      "(even exact), D/Z/degree/precision, splitting and local rho are all excluded, so the only remaining "
                      "frozen-compatible lever on eps_H_cell is eps_cell(X^(2)) <= eps_mid(X^(2)) + rho*||X^(3)(e0)|| + "
                      "(rho^2/2)*T[X,4], min with the cascade (CUSUM aux3, Part 3).",
            "closure_not_predicted": "whether it closes 313 depends on the uncomputed |X'''(e0)| and T[X,4]; aux3 measured norm-only "
                                     "towers 500x-53000x above certified candidate sups at CUSUM cell 321, which is the same "
                                     "structure seen here (sup|H_hat| of F_3, F_4 ~ 1e-8..1e-12 against eps_H ~ 30..41)",
            "per_m_target": target,
            "estimated_new_candidates": {
                "F:r:k3 (r=0..4)": 5, "W:(r,j):k3 (r+j<=3, j>=1)": 6, "S:r:k3 / Ssrc:r:k3 (r=0..3)": 4,
                "total_order3_auxiliary_candidates_per_cell": 15,
                "note": "one order-3 object per existing k2 object that feeds R''; midpoint (e0) certification only"},
            "estimated_new_contracts": [
                "order-3 SR equations: K_e''' by differentiating SR_DERIVATION K_e'' = K_z2,e + 2e K_z,e + (e^2-1) K_e once more, "
                "and the Leibniz order-3 recursions for F, W, S (as aux3 code/aux_certifier.py)",
                "order-3 collocation operator continuing phi^(i)/phi = (-1)^i He_i at i=3 on the frozen grid/degree/quadrature/basis",
                "per-patch T2 certification of the 15 order-3 objects at e0 (midpoint residual, B_int/endpoint strips as frozen)",
                "order-4 norm-only tower T[X,4]: new certified K^(4), K_z^(4) bounds (A_5 moments) with an independent derivation "
                "(the sr_operators kz2 justification must not be reused)",
                "governed successor contract: auxiliary evidence nested in the existing units, bound as auxiliary_evidence_hash; "
                "28 obligations per cell unchanged; candidates/contracts change requires explicit authorization"]},
        "determinism_replay": [x for x in det if x],
        "not_claimed": ["K1 CLOSED", "P5Y CLOSED", "PRODUCTION READY"],
        "untouched": ["T1/T2", "endpoint treatment", "B_int", "mean-value successor", "theorem target", "B_cover = 1/20",
                      "D, Z, precision, degree", "candidates/contracts", "frozen parent cells", "production", "316-cell campaign"],
    }
    (NS / "config/OPNORM_SUCCESSOR_RECORD.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    L = ["# P5Y K1 SR O9 — cell 313 operator-norm / source-chain successor", "",
         f"**Classification: `{CLASS}`.** Parent `804e387`. Diagnostic only; nothing certified; no production; "
         "K1/P5Y not closed; not production ready.", "",
         "## Phase 1 — doctrine", "", f"Ruling `{p1['ruling']}`; all bound fragments present.", ""]
    L += [f"- **{k}**: {v}" for k, v in p1["answers"].items()]
    L += ["", "## Phase 3 — oracle-tight norms (NON-CERTIFYING)", "",
          "| variant | m1 | m2 | m3 | m5 | M_R2 m5 |", "|---|---:|---:|---:|---:|---:|"]
    for k in ("base", "K_all", "Kz_all", "ALL_NORMS", "CANDSUP_only__beyond_norm_scope", "ALL_NORMS_plus_CANDSUP__beyond_norm_scope"):
        L.append(f"| {k} | " + " | ".join(f"{V[k]['ratio'][m]:.4g}" for m in M) + f" | {V[k]['M_R2']['5']:.4g} |")
    L += ["", "| norm | old cell (env) | oracle cell sup | old/oracle | removable share of M_R2 m5 |", "|---|---:|---:|---:|---:|"]
    for r in orc["norm_table"]:
        L.append(f"| {r['operator']} | {r['env_old_bound_cell']:.4g} | {r['oracle_cell_sup']:.4g} | "
                 f"{r['old_over_oracle_env']:.3f} | {100 * r['removable_share_M_R2']['5']:.1f}% |")
    L += ["", "Even with every operator norm replaced by its exact value, m=2,3,5 stay at "
          + ", ".join(f"{V['ALL_NORMS']['ratio'][m]:.3g}" for m in ms)
          + ". Stop rule 2 holds: no rigorous norm successor is built; Phases 4–7 are not run.", "",
          "## Next blocker", "", rec["next_blocker"]["identity"] + ".", "",
          "| F_r (oracle norms) | eps_H_cell | C·deltaH | C·k2·nF | C·2k1·nD | C·epsS2 | sup|H_hat| |", "|---|---:|---:|---:|---:|---:|---:|"]
    for r, d in nb["decomposition_oracle_norms"].items():
        p = [d["parts"][k] for k in ("C*deltaH_cell (mean-value residual)", "C*k2*nF (value chain)", "C*2k1*nD (parent-rho derivative feedback)", "C*epsS2_cell (source chain)")]
        L.append(f"| F_{r} | {d['eps_H_cell']:.4g} | " + " | ".join(f"{x:.3g}" for x in p) + f" | {d['sup_H_hat']:.3g} |")
    L += ["", "| m | M_R2 certified | M_R2 oracle | M_R2 max for ratio 1 | reduction still needed |", "|---|---:|---:|---:|---:|"]
    for m in M:
        L.append(f"| {m} | {req[m]['M_R2_certified']:.4g} | {req[m]['M_R2_oracle']:.4g} | {req[m]['M_R2_max_for_ratio_1']:.4g} | "
                 f"{req[m]['required_reduction_factor_vs_oracle']:.3g}x |")
    L += ["", "## Escalation", "", "Requires `CUSUM_AUX3_STYLE_THIRD_DERIVATIVE_EVIDENCE`: " + rec["escalation"]["reason"], "",
          rec["escalation"]["closure_not_predicted"] + ".", ""]
    L += [f"- m={m}: {t['aux3_style_requirement']}" for m, t in target.items()]
    L += ["", "Estimated: 15 order-3 auxiliary candidates per cell, midpoint certification only. New contracts:", ""]
    L += [f"- {c}" for c in rec["escalation"]["estimated_new_contracts"]]
    L += ["", "Not implemented in this round.", "", "## Determinism", ""] + [f"- `{x}`" for x in det if x] + [""]
    (NS / "RESULT.md").write_text("\n".join(L))
    print(sha(NS / "config/OPNORM_SUCCESSOR_RECORD.json"), sha(NS / "RESULT.md"))


if __name__ == "__main__":
    main()
