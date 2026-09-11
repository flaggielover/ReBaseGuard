"""Write the PRE-RESULT protocol package: config/PARTITION_PROTOCOL.json, PROTOCOL.md, config/PROTOCOL_DIGEST.json.
Reads only the successor table, the frozen checkpoint identifiers and the pre-result (non-certifying) feasibility
evidence of this namespace. Must be run before any successor certified result exists."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
EV = NS / "evidence"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    table = json.loads((NS / "config/successor_cells.json").read_text())
    cells = table["cells"]
    kids = lambda p: [c["index"] for c in cells if c["parent_index"] == p]           # noqa: E731
    hist = {}
    for c in cells:
        if c["child"] == 0:
            hist[str(c["children"])] = hist.get(str(c["children"]), 0) + 1
    agg = json.loads((EV / "phase34_diag_aggregate.json").read_text())["by_N"]
    rules = json.loads((EV / "phase25_rules_projection.json").read_text())["projection"]
    proto = {
        "schema": "rebaseguard.p5y.k1.sr.partition-successor.protocol.v1",
        "successor": "PS1 - P5Y K1 SR predeclared partition successor",
        "purpose": "Prove the SAME K1 SR target over the SAME SR drift domain with the SAME frozen science, on a NEW "
                   "predeclared partition whose cells are small enough for the frozen STYLE_1 Taylor/curvature "
                   "architecture. A new additive successor campaign; the 316-cell campaign and all its results "
                   "(including cell 313 m2/m3/m5 FAIL) stay immutable history and are not claimed.",
        "immutable_predecessors": {"aux3_feasibility": "986e617", "opnorm": "d2981a5", "curvature": "804e387",
                                   "t345": "8b8a242", "frozen_cells_sha256": table["frozen_parent_cells_sha256"],
                                   "frozen_checkpoint": "p5y_k1_cover_ledger_successor/config/checkpoint.json (unchanged)"},
        "global_domain": "SR drift e in [0, c_SR], c_SR = log(4581762885148045/8796093022208) + 1/2 (exact, symbolic); "
                         "negative drift by the inherited exact oddness; far-field theorem P5X-T3 and splice obligations "
                         "inherited unchanged. The CUSUM cover is outside this successor (its own governed campaign).",
        "partition": {"generator": "code/partition_generator.py", "rule": table["rule"], "thresholds": {"r_max": "1/25"},
                      "inputs": "frozen SR cell table and the constants in the generator only",
                      "successor_cells_sha256": sha(NS / "config/successor_cells.json"), "n_cells": table["n_cells"],
                      "split_histogram_parents": hist,
                      "identity_schema": "id = PS1-SR-P<parent:03d>-N<children>-K<child>; index = ordinal by left endpoint; "
                                         "record binds parent_record_sha256, successor table hash, frozen table hash",
                      "midpoint_radius": "e0 = (left+right)/2, rho = (right-left)/2, exact rationals; children of a parent "
                                         "have equal width (R-L)/N; shared boundaries exact; no gaps, no overlaps",
                      "C_upper": "inherited from the parent (a proved bound for every e in the parent)",
                      "terminal": "the terminal parent (315, rho ~ 0.0227 <= 1/25) is not split; its exact affine c_SR "
                                  "encoding is kept; only the last successor cell carries c_SR",
                      "m_sharing": "every successor cell carries all m in {1,2,3,5}; the m=5 curvature bundle owns the "
                                   "shared uniform jets exactly as in the frozen unit structure",
                      "old_313_children": kids(313)},
        "theorem_target": "sup_e |R_D,m(e)| < 2; K1 only; m = 1,2,3,5 (unchanged)",
        "unchanged_science": {"B_cover": "1/20 per cell, STYLE_1, all budgets and nested gates unchanged",
                              "D": 11, "Z": 20, "precision_bits": 256, "candidate_degree": 16,
                              "candidates_contracts": "46 candidates / 102 contracts per cell (frozen O9 census)",
                              "T2": "T2-closed per-patch certifier (O9 core, endpoint-strip successor, B_int, P1 softplus "
                                    "Lagrange factor), all 3,994 frozen live patches",
                              "curvature": "governed mean-value successor: delta_cell = delta_mid + rho*Env over the "
                                           "successor cell (interval-e cell mode not run)",
                              "T4_T5": "frozen ErrorDAG, sr_refine, assembly, ledger and T5 gates, generated verbatim "
                                       "(code/make_successor_stages.py)",
                              "obligations": "28 per successor cell, same unit structure as the frozen parent; SR "
                                             f"successor universe = 28 x {table['n_cells']} = {28 * table['n_cells']} (+ far field)"},
        "selection_justification": {
            "doctrine": "geometry-only rule over the whole domain, the same kind as the frozen s-rule; no pass/fail input",
            "a_priori": "the STYLE_1 charge W = rho|D| + rho^2 M_R2/2 is in absolute units and its uniform-cell "
                        "inflation scales with rho; an absolute radius cap is the direct control",
            "diagnostic_margin_worst_old313_child": {n: agg[n]["variants"]["B_certified"]["worst_ratio_m235"] for n in agg},
            "cost_projection_cpu_h_midpoint_only": {k: v["cpu_h_midpoint_only_T3"] for k, v in rules.items()},
            "rejected": {"GLOBAL_x2": "fails the diagnostic at the old-313 region (1.16)",
                         "GLOBAL_x4_x8": "robust but 3.4x-6.8x the cost of RHO_CAP_1/25",
                         "Q_CAP": "the a-priori sr_refine contraction q is ~0.5 across almost the whole table by the frozen "
                                  "step rule, so it cannot single out the failing region (it would split ~311 cells)",
                         "RHO_CAP_1/32, 1/50": "more cells for no diagnostic need"}},
        "disclosure": "The need for a finer partition is known from the historical cell-313 failure. r_max = 1/25 was "
                      "chosen from NON-CERTIFYING diagnostics of the historical geometry (evidence/phase34_*), before "
                      "and independent of any successor result, and is frozen here.",
        "pre_result_evidence": {p.name: sha(p) for p in sorted(EV.glob("*.json"))},
        "micropilot": {"phase8": {"parent": 313, "successor_cells": kids(313), "require": "every child 28/28 PASS"},
                       "phase9_controls": {p: kids(p) for p in (150, 275, 315)}},
        "prohibitions": ["no change of partition, thresholds or scientific settings after any successor result",
                         "no per-cell tuning, no removal or truncation of any region, no redefinition of K1",
                         "implementation-defect fixes only if they change no partition, threshold or scientific setting; "
                         "each fix committed and recorded; results produced before a fix are rerun",
                         "no claim that the old 316-cell campaign passed", "no production"],
        "status": "PRE_RESULT_PROTOCOL; not K1 closure; not production",
    }
    (NS / "config/PARTITION_PROTOCOL.json").write_text(json.dumps(proto, indent=1, sort_keys=True) + "\n")
    L = ["# PS1 - P5Y K1 SR predeclared partition successor: PRE-RESULT PROTOCOL", "",
         "Frozen before any successor certified result. Machine-readable source: `config/PARTITION_PROTOCOL.json`;",
         "frozen file set: `config/PROTOCOL_DIGEST.json`; temporal anchor: `TEMPORAL_ANCHOR.md` (checked against git).", "",
         "## Purpose", "", proto["purpose"], "", "## Domain and theorem", "", proto["global_domain"], "",
         f"Target: {proto['theorem_target']}.", "", "## Partition (RULE RHO_CAP, r_max = 1/25)", "",
         "For every frozen SR parent (in order) N = smallest of 1, 2, 4, 8, ... with rho/N <= 1/25; equal exact-rational",
         "children; C_upper inherited; terminal parent not split. Generator: `code/partition_generator.py` (reads only the",
         f"frozen cell table). Result: {table['n_cells']} cells, parents split {hist}, table sha256",
         f"`{proto['partition']['successor_cells_sha256']}`. Old cell 313 -> successor cells {kids(313)}.", "",
         "## Unchanged science", ""] + [f"- **{k}**: {v}" for k, v in proto["unchanged_science"].items()] + [
         "", "## Why this rule", ""] + [f"- **{k}**: {v}" for k, v in proto["selection_justification"].items()] + [
         "", "## Disclosure", "", proto["disclosure"], "", "## Micropilot and controls", "",
         f"Phase 8: children of old cell 313 {kids(313)}; every child must be 28/28 PASS. Phase 9 controls: "
         f"{proto['micropilot']['phase9_controls']}.", "", "## Prohibitions", ""] + [f"- {p}" for p in proto["prohibitions"]] + [""]
    (NS / "PROTOCOL.md").write_text("\n".join(L))
    frozen = ["PROTOCOL.md", "config/PARTITION_PROTOCOL.json", "config/successor_cells.json", "tests/test_successor.py"]
    frozen += sorted(str(p.relative_to(NS)) for p in (NS / "code").iterdir() if p.suffix in (".py", ".sh"))
    frozen += sorted(str(p.relative_to(NS)) for p in EV.glob("*.json"))
    dig = {"schema": "rebaseguard.p5y.k1.sr.partition-successor.protocol-digest.v1",
           "files": {f: sha(NS / f) for f in frozen}, "excluded": ["TEMPORAL_ANCHOR.md (written twice)", "config/PROTOCOL_DIGEST.json"]}
    (NS / "config/PROTOCOL_DIGEST.json").write_text(json.dumps(dig, indent=1, sort_keys=True) + "\n")
    print("protocol", sha(NS / "config/PARTITION_PROTOCOL.json")[:16], "digest files", len(dig["files"]), "old313", kids(313),
          "controls", proto["micropilot"]["phase9_controls"])


if __name__ == "__main__":
    main()
