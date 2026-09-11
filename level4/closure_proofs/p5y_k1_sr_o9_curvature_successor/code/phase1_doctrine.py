"""Phase 1: frozen curvature doctrine audit (read-only). Hash-binds every artifact and checks the load-bearing text."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
FRAG = {
    "p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md": [
        "M_R2(D,cell,m) must be a NONNEGATIVE certified upper bound",
        "All quantities on this right-hand side must be uniform cell bounds",
        "A state-only dyadic candidate may be constant in e over the cell",
        "An interval may be tighter only if a proved enclosure of the same expression",
        "Exactly one Taylor representation: STYLE_1",
        "For the EXACT cell midpoint e0 and actual radius rho",
        "CPU-limit or cell-splitting relaxation is permitted after freeze.",
        "replacing\nthis scientific construction requires a new governed disposition"],
    "p5y_k1_cover_ledger_successor/CHECKPOINT.md": ["adaptive splitting"],
    "p5y_k1_cover_ledger_implementation/code/cusum_layer2.py": [
        "WHY delta_cell IS NOT COMPUTED BY SUBSTITUTING AN INTERVAL e",
        "The construction used instead is the mean-value extension",
        "SUBDIVISION_DEPTH = 0"],
    "p5y_k1_cover_ledger_implementation/code/propagate.py": ["which = \"delta_cell\"  whole-cell residuals"],
    "p5y_k1_cover_ledger_implementation/code/ledger.py": ["W_cover_exact = rho * mag(D_interval) + rho^2 * M_R2 / 2"],
    "p5y_k1_cover_ledger_implementation/code/assembly.py": ["k=2 UNIFORMLY ON\nTHE CELL gives R2_interval"],
    "p5y_k1_cover_ledger_implementation/code/refine.py": ["seeded with the crude mean-value"],
    "p5y_k1_sr_qualification/code/sr_refine.py": ["the iteration is seeded with\nthe crude mean-value bound"],
    "p5y_k1_sr_qualification/SR_MIDPOINT_REFINEMENT.md": ["The cover is frozen at order 2 in `e`."],
    "p5y_k1_sr_qualification/SR_REFINEMENT_DESIGN.md": ["order-3 evidence enters **only** as nested auxiliary evidence"],
    "p5y_k1_sr_qualification/SR_DERIVATION.md": ["is required **uniformly on the cell**"],
    "p5y_k1_final_completion/STATUS.md": ["CERTIFICATE_TOO_LOOSE"],
    "p5y_k1_cusum_aux3_successor/README.md": ["auxiliary third-derivative"],
    "p5y_k1_cusum_aux3_successor/RESULTS.md": ["28 of 28"],
    "p5y_k1_sr_o9_t345_successor/code/t3_patch.py": ["cell : e = the whole cell [left, right] as one ball"],
    "p5y_k1_sr_o9_t345_successor/code/t4_cell.py": ["sr_refine.refine_cell"],
    "p5y_k1_sr_o9_t345_successor/config/T345_RECORD.json": [],
}
JSON_KEYS = {"p5y_k1_cover_ledger_successor/config/checkpoint.json": [
    ("geometry", "adaptive_splitting", False), ("geometry", "expansion_point", "EXACT_MIDPOINT"),
    ("enclosure", "no_interpolation", True), ("enclosure", "style", "STYLE_1_COMPLETE_D_INTERVAL"),
    ("enclosure", "curvature", "M_R2 >= sup_cell |R_m_second| from uniform-cell twice-differentiated resolvent and finite-power enclosures"),
    ("enclosure", "B_cover_complete", "outward_upper(rho*mag(D_interval)+rho^2*M_R2/2)"),
    ("scope", "result_dependent_cell_deletion_allowed", False)]}

ANSWERS = {
    "Q1_quantity": "M_R2 >= sup_{e in parent cell} |R''_{D,m}(e)| at x0, assembled with the frozen positive all-m "
                   "coefficients from uniform-cell H_r = F_r'' and W''_(r,j) enclosures (ERROR_ALGEBRA 3; checkpoint enclosure.curvature).",
    "Q2_one_uniform_enclosure_binding": "NO as a representation. What binds is a certified bound UNIFORM over the parent cell. "
        "ERROR_ALGEBRA 1 permits any proved, dependency-preserving enclosure of the same expression, and the frozen CUSUM "
        "implementation itself does NOT substitute an interval e: it uses delta_cell = delta_mid + rho*Env (cusum_layer2).",
    "Q3_uniform_or_cover": "A rigorous bound for every e in the parent cell. The Taylor cover itself is single and parent-level: "
        "R(cell) in R_interval + (cell-e0) D_interval +- rho^2 M_R2/2 with the EXACT midpoint e0 and the parent rho.",
    "Q4_sr_refine_subintervals": "NO. sr_refine (like frozen refine.py) refines whole-cell ERROR bounds around the parent "
        "midpoint with the parent rho; it has no subinterval concept and neither authorises nor uses one.",
    "Q5_union_of_subinterval_certificates": "YES for M_R2 only: max_j over certified sup_{E_j}|R''| on a cover of the cell "
        "bounds sup_cell|R''|, with parent e0, rho, D_interval and STYLE_1 unchanged. NO for local Taylor covers with local "
        "rho_j: that is cell splitting (ERROR_ALGEBRA 7; checkpoint adaptive_splitting=false; exactly one Taylor "
        "representation, no_interpolation).",
    "Q6_subdivision_geometry": "No frozen subdivision rule exists. Any subdivision must be predeclared and deterministic "
        "before results. The successor chosen here uses none (N = 1).",
    "Q7_scientific_vs_representation": "SCIENTIFIC: theorem target sup|R|<2; B_cover<=1/20 with the parent-rho STYLE_1 "
        "cover; M_R2 >= sup_cell|R''|; the twice-differentiated resolvent H equation, C_upper, the candidates, contracts "
        "and obligations. REPRESENTATION: how sup_cell of the residuals (and of R'') is enclosed: interval-e ball, "
        "mean-value extension, or max over subintervals.",
    "Q8_obligation_identity": "Unchanged. The same 28 units per cell; the new enclosure is nested evidence inside the "
        "existing curvature/assembly obligations, as CUSUM Aux3 did (no new work ID).",
    "Q9_cell_315": "Its right endpoint is exactly c_SR (affine [0,1]). The mean-value successor needs only rho (Arb "
        "enclosure) and the operator window [-c_SR+e_lo, c_SR+e_hi], so no decimal endpoint enters. A piecewise "
        "subdivision would need exact affine sub-endpoints; not used.",
    "Q10_cell_313_target_gate": "Does NOT survive independently: with zero curvature error, the m=1..5 enclosures lie "
        "inside (-2,2) (phase2_decomposition.json: target_gate_with_zero_curvature_error = PASS).",
}


def main():
    rec, ok = {}, True
    for rel, frags in FRAG.items():
        p = CP / rel
        t = p.read_text()
        tn = " ".join(t.split())        # whitespace-normalized: frozen text is hard-wrapped
        r = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "fragments": {f: (" ".join(f.split()) in tn) for f in frags}}
        ok &= all(r["fragments"].values())
        rec[rel] = r
    for rel, keys in JSON_KEYS.items():
        p = CP / rel
        j = json.loads(p.read_text())
        r = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "keys": {f"{a}.{b}": j[a][b] == v for a, b, v in keys}}
        ok &= all(r["keys"].values())
        rec[rel] = r
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.curvature-doctrine.v1", "bound_artifacts": rec, "all_fragments_present": ok,
           "answers": ANSWERS,
           "ruling": "CURVATURE_LOCALIZATION_DOCTRINE_PERMITS_SUCCESSOR" if ok else "DOCTRINE_TEXT_MISMATCH",
           "ruling_scope": ("PERMITTED: tighter proved enclosures of the SAME parent-cell quantity, meaning the frozen mean-value "
                            "whole-cell residual extension, or max over a predeclared subinterval cover, with the parent "
                            "e0/rho/STYLE_1 unchanged. FORBIDDEN: local-rho Taylor covers (cell splitting), new "
                            "candidates, any threshold/degree/precision change.")}
    (NS / "evidence/phase1_doctrine.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"ruling": out["ruling"], "all_fragments_present": ok,
                      "missing": [(k, f) for k, v in rec.items() for f, g in {**v.get("fragments", {}), **v.get("keys", {})}.items() if not g]}, indent=1))
    for k, v in rec.items():
        print(v["sha256"][:16], k)


if __name__ == "__main__":
    main()
