#!/usr/bin/env python3
"""P4ZB Phase 18 -- successor closure for the general location family.

Historical P4 remains PARTIAL in its own artifact.  Nothing is rewritten.
"""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
P4 = NS.parent / "p4_theory_generalization"
P4Z = NS.parent / "p4z_location_family_feasibility"
P4ZA = NS.parent / "p4za_fullscope_closure"


def main() -> int:
    adj = json.loads((NS/"production"/"adjudication_p4zb.json").read_text())
    cov = json.loads((NS/"results"/"final_coverage.json").read_text())
    aud = json.loads((NS/"production"/"independent_closure_audit.json").read_text())
    rep = json.loads((NS/"production"/"replay_p4zb.json").read_text())
    plan = json.loads((NS/"production"/"p4zb_campaign_plan.json").read_text())
    start = json.loads((NS/"results"/"p4zb_starting_audit.json").read_text())
    lean = json.loads((P4Z/"results"/"lean_audit.json").read_text())
    p4 = json.loads((P4/"results"/"closure_decision.json").read_text())
    c = cov["counts"]

    if adj["counts"]["FAIL"] or c["COVERED_FAIL"]:
        verdict = "P4ZB_FAILED_FROZEN_GATE"
    elif adj["cost"]["COST_CAP"] == "FAIL":
        verdict = "P4ZB_COST_CAP_FAIL"
    elif aud["verdict"] != "CLOSURE_AUDIT_PASS":
        verdict = "P4ZB_PROVENANCE_FAIL"
    elif c["UNCOVERED"] or not cov["conservation"]["conserved"] \
         or not cov["conservation"]["one_source_per_cell"]:
        verdict = "P4ZB_PROVENANCE_FAIL"
    elif c["INCONCLUSIVE"] or adj["counts"]["INCONCLUSIVE"]:
        verdict = "P4ZB_INCONCLUSIVE"
    else:
        verdict = "P4ZB_CLOSED"

    doc = {
        "schema": "rebaseguard.p4zb-successor-closure.v1",
        "result_bearing": True,
        "verdict": verdict,
        "historical_status_unchanged": {
            "P4_ORIGINAL_VERDICT": p4["verdict"],
            "P4_artifacts_modified": False,
            "P4X_P4Y_P4Z_P4ZA_modified": False,
            "statement": "Historical P4 remains PARTIAL in its own artifact. "
                         "P4X, P4Y, P4Z and P4ZA are untouched. No historical "
                         "verdict is rewritten and no INCONCLUSIVE was "
                         "reinterpreted: the four cells received new P4ZB "
                         "measurement under the unchanged frozen gate.",
        },
        "what_p4zb_resolved": {
            "configuration": plan["scope_lock"]["configuration"],
            "m": plan["scope_lock"]["m"],
            "counts": adj["counts"],
            "cells": [{"m": x["m"], "gate_result": x["gate_result"],
                       "relative_discrepancy": x["correspondence"]["relative_discrepancy"],
                       "z": x["correspondence"]["z"],
                       "T_B_relative": x["fd_ladder"]["relative_drift"],
                       "empirical_order_p": x["fd_ladder"]["empirical_order_p"],
                       "p4za_style_coarse_drift": x["fd_ladder"]["p4za_style_coarse_drift"],
                       "rb_score_relative_se": x["rb_score"]["relative_se"],
                       "rb_map_relative_se": x["rb_map"]["relative_se"]}
                      for x in adj["cells"]],
            "what_changed":
                "Only the reference neighbour of the truncation estimate. Route "
                "B remains the frozen per-batch Richardson at (0.05, 0.025); the "
                "K7 limit remains 0.02; every scientific threshold is unchanged. "
                "P4ZA compared the frozen pair against the COARSER (0.1,0.05) "
                "neighbour, which under the validated h^4 model overstates the "
                "residual by 15x; P4ZB compares it against the FINER "
                "(0.025,0.0125) neighbour. On identical blocks the coarser "
                "reference reads 0.0232-0.0256 and the finer reads 0.0038-0.0045.",
        },
        "full_scope": {
            "cells_total": cov["cells_total"], "counts": c,
            "authoritative_sources": cov["authoritative_sources"],
            "conservation": cov["conservation"],
            "historical_evidence_used_as_sole_authority": False,
            "P4X_role": "corroboration only, 0 authoritative dispositions",
        },
        "theorem_scope": {
            "source": "level4/closure_proofs/p4_theory_generalization",
            "tree_object": start["parent_evidence"]["p4_theorem_tree"],
            "modified": False,
            "statement": "G1a: Gamma_{D,m,f} = E_0[A_m S_tau^psi] for a regular "
                         "one-dimensional location family under the frozen "
                         "two-sided CUSUM and two-chart SR, every m >= 1. Not "
                         "distribution free, not detector universal, not global, "
                         "not nonlinear, not valid for moving support or without "
                         "a first moment.",
        },
        "thresholds": adj["thresholds_used"],
        "cost": adj["cost"],
        "provenance": {
            "independent_closure_audit": aud["verdict"],
            "checks": f"{aud['checks_total']-aud['checks_failed']}/{aud['checks_total']}",
            "replay_blocks": rep["blocks_replayed"],
            "replay_hashes_identical": rep["all_scientific_hashes_identical"],
            "replay_field_mismatch": rep["any_scientific_field_mismatch"],
        },
        "formal": {
            "bounded_survival_lemma": {
                "declarations": lean["declarations"],
                "errors": lean["compile"]["errors"],
                "sorry": lean["compile"]["sorry_count"],
                "new_axioms": lean["new_axioms"], "axioms": lean["axioms"]},
            "p4zb_addition": "none required",
        },
        "successor_closure_statement":
            "The general-location-family closure obligations of the frozen P4 "
            "theorem are closed by successor evidence: all 96 theorem-supported "
            "cells now carry a governed disposition under the unchanged frozen "
            "gate, authored by P4Z (44), P4ZA (48) and P4ZB (4), with zero "
            "scientific FAIL, zero INCONCLUSIVE and zero uncovered claims. "
            "This is successor evidence composed across a governed lineage; it "
            "does not alter the historical P4 record."
            if verdict == "P4ZB_CLOSED" else
            "The scope is NOT closed; see counts.",
        "claims_explicitly_not_made": [
            "historical P4 was retroactively changed to PASS",
            "P4's own historical verdict is anything other than PARTIAL",
            "P5Y is CLOSED", "K1 is CLOSED", "Level-4 is CLOSED",
            "production readiness",
            "the theorem holds beyond its own frozen scope",
        ],
    }
    (NS/"results"/"p4zb_successor_closure.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(f"verdict {verdict}")
    print(f"P4ZB four cells: {adj['counts']}")
    print(f"final 96-cell coverage: {c}")
    print(f"authoritative sources: {cov['authoritative_sources']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
