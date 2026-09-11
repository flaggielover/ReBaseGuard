"""Phase 1: aux3-style SR third-derivative evidence -- doctrine / governance audit (read-only, hash-bound)."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
FRAG = {
    "p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md": [
        "M_R2(D,cell,m) must be a NONNEGATIVE certified upper bound for sup_{e in cell}|R''_(D,m)(e)|",
        "A fixed sufficient certificate construction is differentiation twice",
        "replacing this scientific construction requires a new governed disposition",
        "No candidate degree increase or precision escalation is licensed",
        "An interval may be tighter only if a proved enclosure of the same expression preserves every dependency",
        "No finite-difference estimate or historical g-variable curvature certificate"],
    "p5y_k1_cover_ledger_successor/config/checkpoint.json": [
        "\"adaptive_splitting\":false", "\"expansion_point\":\"EXACT_MIDPOINT\"", "\"assembly_units_per_cell\":4",
        "\"curvature_bundles_per_cell\":4", "\"objects_per_cell\":19", "\"total_units\":17978"],
    "p5y_k1_cover_ledger_successor/CHECKPOINT.md": [],
    "p5y_k1_cusum_aux3_successor/README.md": [
        "nested internal support", "no new top-level work id, no new frozen DAG node",
        "The cascade and this bound are both", "hashed into the parent certificate's scientific"],
    "p5y_k1_cusum_aux3_successor/RESULTS.md": ["5 of 5 now PASS"],
    "p5y_k1_cusum_aux3_successor/code/aux_refine.py": [
        "The auxiliary evidence is used only at the midpoint", "so no whole-cell order-3 quantity is ever required",
        "refuses any node whose kept value exceeds the cascade"],
    "p5y_k1_cusum_aux3_successor/code/aux_certifier.py": [],
    "p5y_k1_cusum_aux3_successor/code/aux_collocation.py": [],
    "p5y_k1_cusum_aux4_fullcover/README.md": ["AUXILIARY_DERIVATIVE_SOUND = YES", "AUXILIARY_GOVERNANCE",
                                               "anything unrecognised defaults to **SCIENTIFIC**"],
    "p5y_k1_sr_qualification/SR_DERIVATION.md": ["They do not depend on `e`.", "K_e'' = K_z2,e + 2 e K_z,e + ( e^2 - 1 ) K_e"],
    "p5y_k1_sr_o9_executor_t1_successor/README.md": ["46 candidates / 102 contracts"],
    "p5y_k1_sr_o9_executor_t1_successor/code/sr_o9_candidates.py": ["CAND_DEGREE = 16", "ORDERS = (0, 1, 2)"],
    "p5y_k1_sr_o9_t2_per_patch_successor/code/sr_o9_equations.py": ["ORD = (0, 1, 2)"],
    "p5y_k1_sr_o9_pre_t2_governance_successor/ADJUDICATION.md": ["stays immutable historical evidence"],
    "p5y_k1_sr_o9_t345_successor/code/t4_cell.py": [],
    "p5y_k1_sr_o9_curvature_successor/code/curv_mv.py": [],
    "p5y_k1_sr_o9_opnorm_successor/config/OPNORM_SUCCESSOR_RECORD.json": ["OPERATOR_NORM_TIGHTENING_INSUFFICIENT"],
}
ANSWERS = {
    "Q1_additive_aux_candidates_preserve_28": "YES. Precedent CUSUM aux3/aux4: third-derivative candidates entered as an "
        "additive successor with no new top-level work id and no new frozen DAG node; universe 17,978 and the per-cell "
        "19+1+4+4 = 28 SR obligations are untouched. The frozen SR T2 census (46 candidates / 102 contracts) stays "
        "immutable; order-3 objects form a separate auxiliary census.",
    "Q2_evidence_only": "YES. They are nested internal support of the existing curvature (and hence assembly) "
        "obligations, bound into the parent certificate as an auxiliary-evidence hash with every leaf SCIENTIFIC by "
        "default (aux4 repair of the AUXILIARY_GOVERNANCE defect). They are not obligations.",
    "Q3_same_quantity": "YES, as a min-with-cascade refinement: the certified quantity is unchanged "
        "(M_R2 = mag(R2_interval(cell)) >= sup_{e in parent cell}|R''_{D,m}(e)|, same all-m assembly, same H_r and W2 "
        "node intervals). The Taylor bound H_r(x0,e) in H_r(x0,e0) + [-1,1]*(rho*|F_r'''(x0,e0)| + (rho^2/2)*T[F_r,4]) "
        "(or aux3's node form eps_mid + rho*||X'''(e0)|| + (rho^2/2)*T[X,4]) is a proved enclosure of the same node "
        "quantity, and a node keeps the cascade whenever it is smaller. ERROR_ALGEBRA s3 fixes differentiation twice as "
        "the construction and requires a new governed disposition to replace it, so the successor must carry that "
        "disposition explicitly. The cascade is still computed and remains the fallback.",
    "Q4_midpoint": "YES: EXACT_MIDPOINT e0 of the frozen parent cell (checkpoint geometry), the same e0 as T2/T3.",
    "Q5_parent_rho": "YES: the frozen parent rho; no splitting (adaptive_splitting=false) and no local rho.",
    "Q6_fourth_order_global": "YES: T[X,4] must bound sup over every state and every e in the whole parent cell. The "
        "norm tower does this by construction from cell-uniform operator norms and closed-form source suprema. No "
        "whole-cell order-3 candidate quantity is used; order 3 is used at e0 only.",
    "Q7_census_change": "YES, an additive auxiliary census (order-3 candidates and their contracts) is required, and "
        "only through an explicitly governed successor: ERROR_ALGEBRA s3 (new governed disposition), aux4 "
        "AUXILIARY_GOVERNANCE. The historical 46/102 census and every predecessor stay byte-identical.",
}


def main():
    rec, ok = {}, True
    for rel, frags in FRAG.items():
        p = CP / rel
        tn = " ".join(p.read_text().split())
        r = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "fragments": {f: (" ".join(f.split()) in tn) for f in frags}}
        ok &= all(r["fragments"].values())
        rec[rel] = r
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.aux3-doctrine.v1", "bound_artifacts": rec, "all_fragments_present": ok,
           "answers": ANSWERS,
           "ruling": "AUX3_SR_PERMITTED_ONLY_VIA_EXPLICITLY_GOVERNED_ADDITIVE_SUCCESSOR" if ok else "DOCTRINE_TEXT_MISMATCH"}
    (NS / "evidence/phase1_doctrine.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(out["ruling"], [(k, f) for k, v in rec.items() for f, g in v["fragments"].items() if not g])


if __name__ == "__main__":
    main()
