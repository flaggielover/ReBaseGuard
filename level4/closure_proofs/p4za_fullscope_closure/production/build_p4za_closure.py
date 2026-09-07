#!/usr/bin/env python3
"""P4ZA Phase 21 -- the successor closure artifact.

Historical P4 remains PARTIAL in its own artifact.  Nothing is rewritten.
"""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
P4 = NS.parent / "p4_theory_generalization"
P4Z = NS.parent / "p4z_location_family_feasibility"


def main() -> int:
    cov = json.loads((NS/"results"/"claim_coverage.json").read_text())
    adj = json.loads((NS/"production"/"adjudication_p4za.json").read_text())
    aud = json.loads((NS/"production"/"independent_closure_audit.json").read_text())
    rep = json.loads((NS/"production"/"replay_p4za.json").read_text())
    plan = json.loads((NS/"production"/"p4za_campaign_plan.json").read_text())
    start = json.loads((NS/"results"/"p4za_starting_audit.json").read_text())
    lean = json.loads((P4Z/"results"/"lean_audit.json").read_text())
    p4 = json.loads((P4/"results"/"closure_decision.json").read_text())

    c = cov["counts"]
    if adj["counts"]["FAIL"] or c["COVERED_FAIL"]:
        verdict = "P4ZA_FAILED_FROZEN_GATE"
    elif adj["cost"]["COST_CAP"] == "FAIL":
        verdict = "P4ZA_COST_CAP_FAIL"
    elif aud["verdict"] != "CLOSURE_AUDIT_PASS":
        verdict = "P4ZA_PROVENANCE_FAIL"
    elif c["UNCOVERED"] or cov["ambiguous"]:
        verdict = "P4ZA_PROVENANCE_FAIL"
    elif c["INCONCLUSIVE"]:
        verdict = "P4ZA_INCONCLUSIVE"
    else:
        verdict = "P4ZA_CLOSED"

    open_cells = [x for x in adj["cells"] if x["gate_result"] == "INCONCLUSIVE"]
    doc = {
        "schema": "rebaseguard.p4za-successor-closure.v1",
        "result_bearing": True,
        "verdict": verdict,
        "historical_status_unchanged": {
            "P4_ORIGINAL_VERDICT": p4["verdict"],
            "P4_artifacts_modified": False,
            "P4X_P4Y_P4Z_modified": False,
            "statement": "Historical P4 remains PARTIAL in its own artifact. "
                         "P4X, P4Y and P4Z are untouched. P4ZA adds successor "
                         "evidence and rewrites nothing.",
        },
        "full_scope": {
            "cells_total": cov["cells_total"],
            "counts": c,
            "authoritative_sources": {
                "P4Z": cov["sources"]["P4Z"]["cells"],
                "P4ZA": cov["sources"]["P4ZA"]["cells"],
                "P4X": cov["sources"]["P4X"]["cells"],
            },
            "historical_evidence_used_as_sole_authority": False,
            "conservation": cov["conservation"],
        },
        "what_p4za_resolved": {
            "cells_addressed": adj["cells_total"],
            "by_cause": adj["by_cause"],
            "K7_all_resolved": adj["by_cause"]["K7"]["INCONCLUSIVE"] == 0,
            "K3_resolved": adj["by_cause"]["K3"]["PASS"],
            "note": "the 52 cells P4Z left INCONCLUSIVE received new P4ZA "
                    "evidence under the unchanged frozen gate; none was "
                    "upgraded by argument",
        },
        "what_remains_open": {
            "cells": len(open_cells),
            "detail": [{"configuration": x["configuration"], "m": x["m"],
                        "reasons": x["reasons"],
                        "relative_drift": x["fd_ladder"]["relative_drift"],
                        "limit": plan["thresholds"]["fd_ladder_relative_max"],
                        "empirical_order_p": x["fd_ladder"]["empirical_order_p"],
                        "rb_score_relative_se": x["rb_score"]["relative_se"],
                        "rb_map_relative_se": x["rb_map"]["relative_se"],
                        "r_star": plan["thresholds"]["r_star"]}
                       for x in open_cells],
            "reading": "these four cells had their K3 problem resolved -- both "
                       "routes reach relative SE 0.0029-0.0050 against r* = "
                       "0.010823, and scale stability is clean -- but they fail "
                       "K7: the finite-difference Richardson drift is 0.0252-"
                       "0.0268 against the unchanged 0.02 limit, with empirical "
                       "order still 1.43-1.49 rather than 2. The frozen limit "
                       "is NOT widened to admit them.",
        },
        "theorem_scope": {
            "source": "level4/closure_proofs/p4_theory_generalization",
            "tree_object": start["parent_evidence"]["p4_theorem_tree"],
            "modified_by_p4za": False,
        },
        "thresholds": adj["thresholds_used"],
        "truncation_rule": adj["truncation_rule"],
        "cost": adj["cost"],
        "provenance": {
            "independent_closure_audit": aud["verdict"],
            "checks": f"{aud['checks_total']-aud['checks_failed']}/{aud['checks_total']}",
            "replay_blocks": rep["blocks_replayed"],
            "replay_hashes_identical": rep["all_scientific_hashes_identical"],
            "replay_field_mismatch": rep["any_scientific_field_mismatch"],
        },
        "formal": {
            "inherited_bounded_survival_lemma": {
                "declarations": lean["declarations"], "errors": lean["compile"]["errors"],
                "sorry": lean["compile"]["sorry_count"], "new_axioms": lean["new_axioms"],
                "axioms": lean["axioms"]},
            "p4za_addition": "none required; the skewnormal4 integrability "
                             "argument reuses the already-formalised lemma",
        },
        "claims_explicitly_not_made": [
            "historical P4 was retroactively changed to PASS",
            "P4 is CLOSED",
            "P5Y is CLOSED",
            "K1 is CLOSED",
            "Level-4 is CLOSED",
            "production readiness",
            "the full 96-cell scope is closed",
        ],
    }
    (NS/"results"/"p4za_successor_closure.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(f"verdict {verdict}")
    print(f"96-cell coverage {c}")
    print(f"P4ZA cells {adj['counts']}  by cause {adj['by_cause']}")
    print(f"open: {len(open_cells)} cells, all {sorted({x['configuration'] for x in open_cells})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
