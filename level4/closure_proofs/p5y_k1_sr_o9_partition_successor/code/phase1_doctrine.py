"""Phase 1: partition doctrine audit (read-only, hash-bound, whitespace-normalized fragment checks)."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
FRAG = {
    "p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md": [
        "For the EXACT cell midpoint e0 and actual radius rho, put Delta=cell-e0.",
        "No degree, precision, scope, P1, complexity, CPU-limit or cell-splitting relaxation is permitted after freeze.",
        "The .050 allocation covers BOTH nominal variation and Taylor uncertainty."],
    "p5y_k1_cover_ledger_successor/CHECKPOINT.md": [
        "successor and its prospective semantic decisions; it does not recolor old results.",
        "no gaps, overlaps, adaptive splitting or result-dependent cell changes.",
        "NEW_EXECUTABLE_COVER_COUNT: CUSUM=326, SR=316, total=642.",
        "This prospectively specified replacement is justified by the same proof and common exact rule, not by a target count or observed production outcome.",
        "The 316 does not narrow drift or detector scope.",
        "OLD_12255_WORK_UNIVERSE_STATUS = SUPERSEDED_BY_SUCCESSOR.",
        "The old 323/322/12255 facts remain byte-identical historical facts.",
        "The s rule is a geometry bound, NOT a proof that B_cover will pass."],
    "p5y_k1_cover_ledger_successor/config/checkpoint.json": [
        "\"adaptive_splitting\":false", "\"expansion_point\":\"EXACT_MIDPOINT\"", "\"historical_manifest_reinterpreted_in_place\":false",
        "\"new_governed_campaign\":true", "\"result_dependent_cell_deletion_allowed\":false",
        "\"rho\":\"(right-left)/2 = max(abs(left-e0),abs(right-e0))\"", "\"target\":\"sup_e |R_D,m(e)| < 2; K1 only; both detectors and m=1,2,3,5\"",
        "\"old_universe_status\":\"SUPERSEDED_BY_SUCCESSOR; historical record immutable\"", "\"noncanonical_geometry\""],
    "p5y_k1_cover_ledger_successor/config/cells.json": [],
    "p8r_temporal_integrity_repair/TEMPORAL_ANCHOR.md": [
        "`I1` runs `git ls-tree` on the named commit and fails if any production",
        "`tests/test_temporal_anchor.py` additionally requires"],
    "p8r_temporal_integrity_repair/REPAIR_RATIONALE.md": [
        "No pre-result temporal anchor.", "Result-driven amendment.",
        "They are re-asked under frozen rules and reported as they come out."],
    "p9r_final_synthesis_repair/README.md": [
        "It does not rewrite P9 and it does not convert `P9 = PARTIAL` into `CLOSED` retroactively."],
    "p5y_k1_cusum_aux3_successor/README.md": ["no new top-level work id, no new frozen DAG node"],
    "p5y_k1_cusum_aux4_fullcover/README.md": ["required the complete 326-cell CUSUM cover to be"],
    "p5y_k1_sr_o9_curvature_successor/config/SUCCESSOR_PREDECLARATION.json": [
        "A max-over-subintervals enclosure (parent rho) is doctrinally permitted but is not part of this successor, and would need its own predeclared dyadic ladder."],
    "p5y_k1_sr_o9_aux3_successor/config/AUX3_SR_RECORD.json": ["AUX3_SR_FEASIBILITY_FAIL"],
    "p5y_k1_sr_o9_opnorm_successor/config/OPNORM_SUCCESSOR_RECORD.json": ["OPERATOR_NORM_TIGHTENING_INSUFFICIENT"],
    "p5y_k1_sr_o9_curvature_successor/config/CURVATURE_SUCCESSOR_RECORD.json": [],
    "p5y_k1_sr_o9_executor_t1_successor/code/sr_o9_candidates.py": [
        "The cell must be byte-identical (canonically) to its frozen record",
        "a c_SR component is admissible only for the last"],
}
ANSWERS = {
    "A_vs_B": "A (silently subdividing frozen cell 313 after its failure and counting it for the frozen campaign) is "
              "ILLEGAL: ERROR_ALGEBRA s7 forbids cell-splitting relaxation after freeze, checkpoint sets adaptive_splitting "
              "= false and forbids result-dependent cell changes, and T1 refuses any cell record not byte-identical to "
              "its frozen entry. B is the pattern the frozen record itself used: the cover-ledger successor replaced the "
              "old 323/322 executable cover by a newly declared 326/316 table under a new governed campaign "
              "(new_governed_campaign = true, historical_manifest_reinterpreted_in_place = false, old universe "
              "SUPERSEDED_BY_SUCCESSOR, old facts byte-identical, 'does not recolor old results'). P8R/P9R repaired failed "
              "campaigns in new namespaces behind a pre-result temporal anchor without rewriting history.",
    "1_B_permitted": "YES, as a new additive K1 successor campaign. The s7 prohibition binds the frozen campaign "
                     "('after freeze'); it does not bind a new campaign declared before its own results.",
    "2_temporal_anchor": "A git commit (P8R Checkpoint-A standard) that contains the protocol, the deterministic partition "
                         "generator, the generated cell table and its hash, every threshold, and the executable surface, "
                         "and NO successor scientific result; checked from git (ls-tree of the anchor, anchor ancestor of "
                         "HEAD, every result recorded against a descendant commit).",
    "3_global_partition": "The successor must declare the WHOLE SR partition (all of [0, c_SR]) as one canonical table. "
                          "A globally predeclared nonuniform partition is allowed: the frozen cover is already nonuniform "
                          "(its step depends on C at each left endpoint). Every cell must be defined; none may be left to "
                          "the old table.",
    "4_high_rho_only": "YES, if the refinement is a deterministic function of frozen geometry (parent rho, C_upper, a_up, "
                       "norms) applied uniformly to every parent cell, never of observed pass/fail. The frozen cover's own "
                       "rule is exactly such a geometry rule.",
    "5_inputs_frozen_only": "YES: the generator may read only the frozen cell table and frozen constants plus constants "
                            "fixed in the protocol; it may not read any T2-T5 record, verdict or ratio.",
    "6_new_identities": "YES: T1 refuses any record differing from the frozen cell, and resume identity includes cells_sha256 "
                        "and cell_index; children need new identities (successor schema, parent index, child index, N) "
                        "and a new cells_sha256.",
    "7_old_obligations": "YES: the old 316-cell obligations and every result (cell 313 m2/m3/m5 FAIL included) stay "
                         "immutable historical evidence; the successor does not claim them.",
    "8_theorem_unchanged": "YES: same target sup_e |R_D,m(e)| < 2 over the same SR drift domain [0, c_SR] (negative drift by "
                           "the inherited oddness), same m scope, same B_cover = 1/20 per cell, same D/Z/precision/degree.",
    "9_new_successor": "YES: a new K1 SR cover successor with its own work universe (28 obligations per NEW cell), not a "
                       "repair of the 316-cell campaign.",
    "caveat": "The need for a finer partition is known because cell 313 failed. This is disclosed, not hidden. It is "
              "admissible under the P8R standard (a successor is designed from known failures) provided the rule is "
              "global and geometry-only, frozen before any successor result, and never tuned on successor results.",
}


def main():
    rec, ok = {}, True
    for rel, frags in FRAG.items():
        p = CP / rel
        tn = " ".join(p.read_text().split())
        r = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "fragments": {f: (" ".join(f.split()) in tn) for f in frags}}
        ok &= all(r["fragments"].values())
        rec[rel] = r
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.partition-doctrine.v1", "bound_artifacts": rec, "all_fragments_present": ok,
           "answers": ANSWERS, "ruling": "PARTITION_SUCCESSOR_PERMITTED_AS_NEW_PREDECLARED_ADDITIVE_CAMPAIGN" if ok else "DOCTRINE_TEXT_MISMATCH"}
    (NS / "evidence/phase1_doctrine.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(out["ruling"], [(k, f) for k, v in rec.items() for f, g in v["fragments"].items() if not g])


if __name__ == "__main__":
    main()
