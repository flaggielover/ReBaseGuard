#!/usr/bin/env python3
"""Assemble the P4Z successor closure artifact from the adjudicated evidence.

Historical P4 is not rewritten and not relabelled.  This produces a NEW
successor artifact that states exactly which historically unadjudicated cells
the governed P4Z campaign discharged, under which estimator, runtime, hashes
and cost, and says plainly what it does not establish.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
P4 = NS.parent / "p4_theory_generalization"


def load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def main() -> int:
    adj = load(NS / "production" / "adjudication.json")
    ind = load(NS / "production" / "independent_adjudication.json")
    replay = load(NS / "production" / "replay.json")
    lean = load(NS / "results" / "lean_audit.json")
    plan = load(NS / "production" / "campaign_plan.json")
    checkpoint = load(NS / "configs" / "checkpoint_p4z.json")
    contract = load(NS / "production" / "mac_runtime_contract.json")
    manifest_head = load(NS / "production" / "run_state.json")
    p4 = load(P4 / "results" / "closure_decision.json")
    if adj is None or ind is None:
        raise SystemExit("adjudication artifacts are missing; nothing to close")

    residue = adj["unresolved_residue"]
    discharged = residue["by_result"]["PASS"]
    failed = residue["by_result"]["FAIL"]
    inconclusive = residue["by_result"]["INCONCLUSIVE"]

    if failed:
        verdict = "P4Z_FAILED_FROZEN_GATE"
    elif adj["cost"]["COST_CAP"] == "FAIL":
        verdict = "P4Z_COST_CAP_FAIL"
    elif ind["verdict"] != "ADJUDICATION_PASS":
        verdict = "P4Z_PROVENANCE_FAIL"
    elif inconclusive:
        verdict = "P4Z_INCONCLUSIVE"
    elif adj["counts"]["INCONCLUSIVE"]:
        # the residue is discharged but the full 96-cell grid is not
        verdict = "P4Z_NUMERICAL_PASS_AWAITING_FORMAL_OR_GOVERNANCE"
    elif adj["counts"]["FAIL"]:
        verdict = "P4Z_FAILED_FROZEN_GATE"
    else:
        verdict = "P4Z_CLOSED"

    doc = {
        "schema": "rebaseguard.p4z-successor-closure.v1",
        "result_bearing": True,
        "verdict": verdict,
        "historical_status_unchanged": {
            "P4_ORIGINAL_VERDICT": p4["verdict"],
            "P4_artifacts_modified": False,
            "P4_relabelled": False,
            "P4X_and_P4Y_modified": False,
            "statement": "Historical P4 remained PARTIAL throughout and is "
                         "untouched. P4Z supplies successor evidence; it does "
                         "not repair, rewrite or relabel any historical artifact.",
        },
        "successor_evidence": {
            "historically_unresolved_cells": residue["total"],
            "discharged_PASS": discharged,
            "FAIL": failed,
            "INCONCLUSIVE": inconclusive,
            "which_historical_gate": "P4X obligation C2 / Checkpoint A gate X6, "
                                     "the 8 cells recorded PRECONDITION_NOT_MET",
            "cells": [
                {k: c[k] for k in ("layer", "detector", "family", "m",
                                   "gate_result", "reasons")}
                for c in adj["cells"] if c["is_historically_unresolved"]
            ],
        },
        "full_grid": {
            "cells_total": adj["cells_total"],
            "counts": adj["counts"],
            "note": "the frozen scope is 96 cells; a campaign that discharges "
                    "the 8-cell residue has NOT re-adjudicated all 96",
            "killed_configurations": adj["killed_configurations"],
            "excluded_configurations": adj["excluded_configurations"],
        },
        "theorem_scope": {
            "source": "level4/closure_proofs/p4_theory_generalization",
            "tree_object": checkpoint["theorem"]["tree_object"],
            "statement": "G1a: Gamma_{D,m,f} = E_0[A_m S_tau^psi], for a regular "
                         "one-dimensional location family and a fixed "
                         "residual-path stopping rule; the frozen two-sided "
                         "CUSUM and two-chart SR only. Not distribution free, "
                         "not detector universal, not global, not nonlinear, "
                         "not valid for moving support or for an innovation law "
                         "without a first moment.",
            "modified_by_p4z": False,
        },
        "estimators": {
            "primary": checkpoint["estimators"]["primary"],
            "companion": checkpoint["estimators"]["fallback"],
            "analytic_contract": checkpoint["estimators"]["analytic_contract"],
        },
        "runtime": {
            "host": contract["declaration"],
            "runtime_hash": contract["runtime_hash"],
            "cpu": contract["machine"]["cpu_brand"],
            "os": f"{contract['operating_system']['product']} "
                  f"{contract['operating_system']['version']} "
                  f"({contract['operating_system']['build']})",
            "python": contract["python"]["version"],
            "numpy": contract["package_lock"]["numpy"],
            "scipy": contract["package_lock"]["scipy"],
            "blas": contract["numerical_backend"]["blas_name"],
            "workers": plan["execution"]["workers"],
        },
        "thresholds": adj["thresholds_used"],
        "cost": adj["cost"],
        "provenance": {
            "independent_adjudication": ind["verdict"],
            "checks_total": ind["checks_total"],
            "checks_failed": ind["checks_failed"],
            "replay": None if replay is None else {
                "blocks_replayed": replay["blocks_replayed"],
                "all_scientific_hashes_identical":
                    replay["all_scientific_hashes_identical"],
                "any_scientific_field_mismatch":
                    replay["any_scientific_field_mismatch"],
            },
        },
        "formal": None if lean is None else {
            "target": "bounded-survival lemma only",
            "declarations": lean["declarations"],
            "axioms": lean["axioms"],
            "errors": lean["compile"]["errors"],
            "new_axioms": lean["new_axioms"],
        },
        "claims_explicitly_not_made": [
            "historical P4 was retroactively repaired",
            "P4 is CLOSED",
            "P5Y is CLOSED",
            "K1 is CLOSED",
            "Level-4 is CLOSED",
            "production readiness unrelated to this theorem",
            "all 96 frozen cells were re-adjudicated",
        ],
    }
    out = NS / "results" / "successor_closure.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"verdict {verdict}")
    print(f"residue: PASS {discharged}  FAIL {failed}  INCONCLUSIVE {inconclusive}")
    print(f"full grid: {adj['counts']}")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
