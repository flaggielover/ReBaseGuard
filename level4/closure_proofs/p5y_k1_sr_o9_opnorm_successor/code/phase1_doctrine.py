"""Phase 1: operator-norm doctrine audit (read-only; whitespace-normalized fragment checks + hash binding)."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
FRAG = {
    "p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md": [
        "Use certified operator norm bounds j_k over the whole cell; rigorous whole-line absolute Gaussian moments are admissible. Do not use sampled operator norms.",
        "C is a proven UPPER bound on ||(I-K_e)^-1|| for every e in the declared cell",
        "k0 <= 1, k1 <= 2 phi(0), k2 <= 4 phi(1) follow by integrating |phi|, |phi'|, |phi''| over the whole real line",
        "An interval may be tighter only if a proved enclosure of the same expression preserves every dependency",
        "No degree, precision, scope, P1, complexity,"],
    "p5y_k1_final_completion/CHECKPOINT.md": [
        "calls the whole-line moments \"admissible\", not mandatory",
        "A sharper certified bound on the same operator is not a relaxation of anything"],
    "p5y_k1_final_completion/code/sharp_norms.py": ["at the known roots of `He_n`"],
    "p5y_k1_sr_qualification/code/sr_operators.py": [
        "|z (w^2 - 1)| <= (|w| + |e|) |w^2 - 1|",
        "kz2 = _int_abs_w_phi(L, U) * arb(1) + ae * k2 + _int_w2_phi(L, U)",
        "the widest continuation interval -- attained at the reset state y_0 = (0,0) -- is [-c_SR, c_SR]"],
    "p5y_k1_sr_qualification/SR_DERIVATION.md": ["K_e' = -( K_z,e + e K_e )", "K_e'' = K_z2,e + 2 e K_z,e + ( e^2 - 1 ) K_e"],
    "p5y_k1_cover_ledger_implementation/code/depgraph.py": ["epsY <= lY + sum_i |b_i| ||T_i|| epsX_i"],
    "p5y_k1_sr_o9_t345_successor/code/t4_cell.py": ["def norms_at(e) -> dict:"],
    "p5y_k1_sr_o9_curvature_successor/code/curv_mv.py": ["Its kz2 rests on a pointwise-false"],
    "p5y_k1_sr_o9_curvature_successor/config/CURVATURE_SUCCESSOR_RECORD.json": [],
    "p5y_k1_sr_o9_curvature_successor/evidence/kz2_predecessor_check.json": [],
    "p5y_k1_cusum_aux3_successor/README.md": ["auxiliary third-derivative"],
    "p5y_k1_cusum_aux4_fullcover/README.md": [],
    "p5y_k1_cover_ledger_successor/config/checkpoint.json": ["\"B_resolvent\":\"0\""],
}
ANSWERS = {
    "Q1_requirement": "YES: every propagation edge needs a certified UPPER bound ||T_i|| of the same operator (depgraph "
                      "edge rule; ERROR_ALGEBRA 2 'certified operator norm bounds ... over the whole cell'). Sampled norms are forbidden.",
    "Q2_historical_formula_binding": "NO: whole-line moments are 'admissible', not mandatory. The frozen final-completion "
                                     "campaign replaced them by drift-aware closed forms, min(drift-aware, whole-line, "
                                     "Cauchy-Schwarz), recorded as 'not a relaxation of anything'.",
    "Q3_tighter_proved_norm": "YES, provided it bounds the SAME operator (K^(i), K_z^(i) with the frozen e-free continuation "
                              "limits), sup over the SAME reachable state set and every e of the SAME parent cell, on the "
                              "same edges and owners (ERROR_ALGEBRA 1: a tighter proved enclosure of the same expression).",
    "Q4_cell_dependence": "C_upper is frozen per-cell input and not replaceable (B_resolvent = 0, multiplicative only). "
                          "k_j >= sup_cell ||K_j|| may depend on the frozen parent cell's drift interval. Midpoint-DAG "
                          "norms may be evaluated at e0 (R and D intervals are midpoint quantities); cell-DAG, "
                          "mean-value and refinement norms must be uniform over the parent cell. No sub-cell dependence.",
    "Q5_derivative_specific": "YES: each edge carries its own norm (k_i, kz_i per derivative index), so no shared envelope "
                              "is required; each can be certified separately.",
    "Q6_obligation_identity": "NO change: norms are nested certificate inputs; the 28 units per cell are unchanged.",
    "known_defect": "The frozen sr_operators kz2 cites a pointwise-false inequality; its values were proved valid for the "
                    "six cells (curvature successor evidence). It must not be copied: any successor norm needs an "
                    "independent derivation.",
}


def main():
    rec, ok = {}, True
    for rel, frags in FRAG.items():
        p = CP / rel
        tn = " ".join(p.read_text().split())
        r = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "fragments": {f: (" ".join(f.split()) in tn) for f in frags}}
        ok &= all(r["fragments"].values())
        rec[rel] = r
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.opnorm-doctrine.v1", "bound_artifacts": rec, "all_fragments_present": ok,
           "answers": ANSWERS, "ruling": "OPERATOR_NORM_TIGHTENING_PERMITTED" if ok else "DOCTRINE_TEXT_MISMATCH"}
    (NS / "evidence/phase1_doctrine.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"ruling": out["ruling"], "missing": [(k, f) for k, v in rec.items() for f, g in v["fragments"].items() if not g]}, indent=1))
    for k, v in rec.items():
        print(v["sha256"][:16], k)


if __name__ == "__main__":
    main()
