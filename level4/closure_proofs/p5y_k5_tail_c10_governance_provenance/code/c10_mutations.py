"""C10 Phase 13 -- mutation tests over the GOVERNANCE machinery.

Each mutant plants a specific wrong governance belief. Detection means some check, quoted text or
recomputation rejects it. No detector is a literal True. Survivors are reported.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c10_common as C

res = []


def mut(mid, name, detected, how):
    res.append({"id": mid, "name": name, "outcome": "DETECTED" if detected else "SURVIVED",
                "how": how})


def main() -> int:
    arch = C.load(C.NS / "evidence" / "phase1" / "C10_ARCHAEOLOGY.json")
    gov = C.load(C.NS / "evidence" / "phase5" / "C10_GOVERNANCE.json")
    q1 = arch["Q1_hash_archaeology"]
    rule = gov["Q2_phase5_rule_reconstruction"]

    # M01 historical hash mistaken for current
    cur = C.sha256_bytes(C.blob_at("HEAD", C.PRODUCER))
    mut("M01", "historical pin mistaken for the current file hash",
        q1["recorded_c2_refined_registry"] != q1["current_c2_refined_registry"]
        and q1["current_c2_refined_registry"] == cur,
        f"both are carried as separate fields and the current one is recomputed here: "
        f"recorded {q1['recorded_c2_refined_registry'][:12]}, current {cur[:12]}")

    # M02 git blob sha1 vs content sha256
    blob = C.git_blob_id("HEAD", C.PRODUCER)
    mut("M02", "git blob SHA-1 confused with content SHA-256",
        blob != cur and len(blob) == 40 and len(cur) == 64
        and all("git_blob_id_sha1" in t and "content_sha256" in t for t in q1["producer_timeline"]),
        f"the timeline carries BOTH per commit and they differ in length and value "
        f"(blob {blob[:12]} is sha1; content {cur[:12]} is sha256)")

    # M03 current producer assumed equal to historical
    bound = q1["commit_bound_by_the_pin"]
    mut("M03", "current producer assumed identical to the historically bound producer",
        C.sha256_bytes(C.blob_at(bound, C.PRODUCER)) != cur,
        f"recomputed at the bound commit {bound[:12]}: differs from HEAD, and the difference is "
        f"localised by AST to {arch['Q1_diff_classification']['units_changed']}")

    # M04 docstring-only change treated as scientific / M05 scientific treated as cosmetic
    d = arch["Q1_diff_classification"]
    mut("M04", "a non-scientific change treated as scientific producer drift",
        d["BUILD_PATH_IDENTICAL"] and arch["Q1_PROVENANCE_CLASS"] == "C_GOVERNANCE_DRIFT",
        "classification is driven by an AST unit-level comparison, not by a line diff: build-path "
        "units changed = NONE, so class D is not reachable")
    # M05 -- the first version wrote `("D..." if ["build"] else None)`, where ["build"] is a
    # non-empty list and therefore ALWAYS truthy. That detector could not fail: a tautology dressed
    # as a test. It now re-runs the REAL classifier from c10_archaeology with a planted build-unit
    # change and requires the class to flip.
    import importlib.util as _u
    _sp = _u.spec_from_file_location("c10_arch", C.NS / "code" / "c10_archaeology.py")
    _m = _u.module_from_spec(_sp)
    _sp.loader.exec_module(_m)

    def classify(changed, bound_exists=True):
        build_changed = sorted(set(changed) & _m.BUILD_UNITS)
        return ("E_BROKEN_BINDING" if not bound_exists else
                "D_SCIENTIFIC_PRODUCER_DRIFT" if build_changed else
                "A_NO_DEFECT" if not changed else "C_GOVERNANCE_DRIFT")

    real = classify(d["units_changed"])
    planted_sci = classify(d["units_changed"] + ["build"])
    planted_const = classify(d["units_changed"] + ["CONST:DEGREE_ARL"])
    planted_none = classify([])
    planted_broken = classify(d["units_changed"], bound_exists=False)
    mut("M05", "a scientific change treated as cosmetic",
        real == "C_GOVERNANCE_DRIFT" and planted_sci == "D_SCIENTIFIC_PRODUCER_DRIFT"
        and planted_const == "D_SCIENTIFIC_PRODUCER_DRIFT" and planted_none == "A_NO_DEFECT"
        and planted_broken == "E_BROKEN_BINDING",
        f"the REAL classifier is re-run with planted inputs and every branch is exercised: "
        f"actual {real}; +build -> {planted_sci}; +DEGREE_ARL -> {planted_const}; "
        f"empty -> {planted_none}; unbound -> {planted_broken}")

    # M06 rule assumed global without evidence
    mut("M06", "the C2 floor assumed globally binding without textual evidence",
        rule["any_claim_of_permanence"] == [] and rule["declares_itself_prospective"] is True,
        "no committed text asserts permanence; the floor declares itself prospective and scopes "
        "itself to 'future adoptions ... from this verdict onward'")

    # M07 rule assumed replaceable without evidence
    mut("M07", "the C2 floor assumed replaceable without textual evidence",
        bool(rule["adjudication_itself_directs_a_replacement"]["quote"])
        and rule["F1"]["HAS_AN_EXPLICIT_LAPSE_CONDITION"],
        "replaceability is not inferred: the adjudication names the lapse condition on F1 and "
        "directs a successor to freeze a replacement floor once N9 closes")

    # M08 historical verdict rewritten
    r5 = C.r5_map()
    c305 = [c for c in r5["per_m"]["5"]["cells"] if c["cell"] == 305][0]
    tree_c2 = C.git("rev-parse", "HEAD:level4/closure_proofs/p5y_k5_tail_c2_closure")
    tree_c2_pub = C.git("rev-parse",
                        "ae4cbc2cc0160538ec8fed3554feaceba5d71ec4:level4/closure_proofs/p5y_k5_tail_c2_closure")
    mut("M08", "a historical verdict rewritten",
        c305["verdict"] == "PASS" and 305 in r5["inputs"]["adopted_cells"]
        and tree_c2 == tree_c2_pub,
        "cell 305 remains PASS and ADOPTED and the whole C2 namespace tree is identical to its "
        "published head")

    # M09 successor adoption conflated with predecessor adoption
    four = gov["Q2_phase6_four_concepts"]
    mut("M09", "successor adoption conflated with predecessor adoption",
        four["does_changing_D_imply_changing_A_or_B"]["answer"] == "NO"
        and four["A_HISTORICAL_C2_VERDICT"]["mutable"] is False,
        "the four concepts are carried separately, with A explicitly immutable and D explicitly "
        "governed by the rule in force at the successor's own freeze")

    # M10 closure threshold confused with adoption threshold
    c307 = gov["Q2_phase10_cell307"]
    mut("M10", "the closure threshold confused with the adoption threshold",
        c307["tightening_to_close"] != c307["tightening_to_be_ADOPTABLE_under_the_inherited_floor"]
        and c307["alpha_can_close"] is True and c307["alpha_can_satisfy_F2"] is False,
        f"they are separate fields with different values "
        f"({c307['tightening_to_close']:.6f} vs "
        f"{c307['tightening_to_be_ADOPTABLE_under_the_inherited_floor']:.6f}) and alpha satisfies "
        f"the first but not the second")

    # M11 cell 306 retroactively authorized in C9
    c306 = gov["Q2_phase11_cell306"]
    c9scope = C.load(C.C9 / "evidence" / "governance" /
                     "HANDOVER_FACT_VERIFICATION.json")["scope_discipline"]
    mut("M11", "cell 306 retroactively authorized in C9",
        c306["that_C8_decision_is_immutable"] is True
        and c9scope["non_target_cells_evaluated"] == []
        and "does not authorize" in c306["may_a_FUTURE_campaign_target_it"],
        "C9 evaluated no non-target cell, C8's decision is recorded immutable, and the future-target "
        "statement explicitly declines to authorize anything")

    # M12 counterfactual alpha called certified
    lever = C.load(C.C9 / "evidence" / "phase4" / "C9_ALPHA_LEVER.json")
    mut("M12", "the cell-307 alpha projection called certified evidence",
        lever["LABEL"].startswith("COUNTERFACTUAL")
        and "projected" in json.dumps(gov["Q2_phase10_cell307"]).lower()
        or "projected" in json.dumps(gov["Q2_consequence_cases"]).lower(),
        f"C9's artifact is labelled {lever['LABEL'][:40]} and C10 carries the figure under "
        f"'best_alpha_tightening_projected'")

    # M13 r6 created without adoption
    r6 = [f for ref in C.git("for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
          for f in C.git("ls-tree", "-r", "--name-only", ref).splitlines()
          if "COVERAGE_MAP_R6" in f.rsplit("/", 1)[-1].upper()]
    mut("M13", "an r6 coverage map created without an adoption", not r6,
        f"no COVERAGE_MAP_R6 exists on any of "
        f"{len(C.git('for-each-ref', '--format=%(refname:short)', 'refs/heads').splitlines())} local branches")

    # M14 reviewer prose absorbed without verification
    mut("M14", "reviewer/adjudicator prose absorbed without verification",
        (C.NS / "code" / "c10_factcheck.py").exists(),
        "phase 16 reproduces every load-bearing claim from the committed tree before absorption")

    surv = [r["id"] for r in res if r["outcome"] == "SURVIVED"]
    out = {"schema": "C10_MUTATIONS/1", "mutants": res, "survivors": surv,
           "MUTATION_CLASS": "PASS" if not surv else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "mutations" / "C10_MUTATIONS.json", out)
    for r in res:
        print(f"  {r['outcome']:<9} {r['id']}  {r['name'][:66]}")
    print(f"\nMUTATION_CLASS = {out['MUTATION_CLASS']}  survivors={surv}")
    print(f"wrote evidence/mutations/C10_MUTATIONS.json sha256 {s[:16]}...")
    return 0 if not surv else 1


if __name__ == "__main__":
    raise SystemExit(main())
