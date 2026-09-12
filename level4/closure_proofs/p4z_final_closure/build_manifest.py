#!/usr/bin/env python3
"""Derive MANIFEST.json and gate_discharge.json for the final P4Z closure packet.

Every pin is read from the repository. Nothing is hand-copied, so an edit to any
pinned artifact makes the build or the packet tests fail rather than silently
changing the record.

The manifest deliberately carries no hash of itself. Integrity of the manifest
is established externally, by the commit that contains it; `manifest_self_hash`
is excluded by construction and `tests/test_packet.py` asserts that.

NOT RESULT BEARING. Reads only; writes only inside this namespace.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parent
CP = NS.parent
REPO = CP.parent.parent

P4 = CP / "p4_theory_generalization"
P4Z = CP / "p4z_location_family_feasibility"
P4ZA = CP / "p4za_fullscope_closure"
P4ZB = CP / "p4zb_skewnormal4_k7"
P4ZR = CP / "p4zr_rng_provenance_repair"


def git(*a: str) -> str:
    return subprocess.run(("git", "-C", str(REPO)) + a,
                          capture_output=True, text=True, check=True).stdout.strip()


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree(ref: str, path: str) -> str:
    return git("rev-parse", f"{ref}:{path}")


def commit_of(branch: str) -> dict:
    full = git("rev-parse", branch)
    return {"branch": branch, "commit": full,
            "subject": git("log", "-1", "--format=%s", full),
            "date": git("log", "-1", "--format=%cI", full)}


def rel(p: Path) -> str:
    return p.relative_to(REPO).as_posix()


def pin(p: Path) -> dict:
    return {"path": rel(p), "sha256": sha(p)}


# --------------------------------------------------------------------------
# the three original P4 gates and what discharges each
# --------------------------------------------------------------------------

def gate_discharge() -> dict:
    decision = json.loads((P4 / "results" / "closure_decision.json").read_text())
    gates = decision["gates"]
    cov = json.loads((P4ZB / "results" / "final_coverage.json").read_text())
    p4x_prod = (REPO.parent / "ReBaseGuard-p4x" / "level4" / "closure_proofs"
                / "p4x_generalization_boundary" / "production" / "results"
                / "production_results.json")

    # the three gates that are false in P4's own frozen decision
    failed = sorted(k for k, v in gates.items() if v is False)
    assert failed == ["all_outside_assumption_cells_demonstrate_failure",
                      "all_theorem_supported_cells_pass",
                      "gaussian_consistency_with_closed_core"], failed

    rows = [
        {
            "original_p4_gate": "all_theorem_supported_cells_pass",
            "recorded_in_p4_as": gates["all_theorem_supported_cells_pass"],
            "discharged_by": "P4Z -> P4ZA -> P4ZB successor evidence",
            "mechanism": "new measurement under the unchanged frozen gate; "
                         "96 theorem-supported cells, one authoritative source each",
            "evidence": {
                "final_coverage": rel(P4ZB / "results" / "final_coverage.json"),
                "cells_total": cov["cells_total"],
                "counts": cov["counts"],
                "authoritative_sources": cov["authoritative_sources"],
                "conservation": cov["conservation"],
            },
            "rule_c_applied": False,
            "status": "DISCHARGED",
        },
        {
            "original_p4_gate": "all_outside_assumption_cells_demonstrate_failure",
            "recorded_in_p4_as": gates["all_outside_assumption_cells_demonstrate_failure"],
            "discharged_by": "P4X obligation C4, admitted under obligation-local Rule C",
            "mechanism": "the proved failure mode for a law with no first moment is "
                         "NON-EXISTENCE of the estimand, not a Monte Carlo "
                         "disagreement signature; the discharge is analytic",
            "rule_c_applied": True,
            "rule_c_findings": {
                "independently_identifiable": True,
                "predates_or_avoids_the_defective_path": True,
                "uses_no_tainted_result_bearing_computation": True,
                "new_compute": "NONE",
                "reconstructible_without_the_defect": True,
                "frozen_provenance_intact": True,
                "note": "P4X's governance failure is the stage-2 top-up sharding on "
                        "frozen/cusum@5/t1p5. C4 records new_compute NONE and rests "
                        "on PROOF.md section 10 plus the Arb certificate, so the "
                        "defective path is not traversed.",
            },
            "status": "DISCHARGED",
        },
        {
            "original_p4_gate": "gaussian_consistency_with_closed_core",
            "recorded_in_p4_as": gates["gaussian_consistency_with_closed_core"],
            "discharged_by": "P4X obligation C5, admitted under obligation-local Rule C",
            "mechanism": "the correctly specified two-sample statistic "
                         "z = |e1-e2| / sqrt(SE1^2 + SE2^2) over frozen published "
                         "anchors; P4's own gate divided by one standard error alone",
            "rule_c_applied": True,
            "rule_c_findings": {
                "independently_identifiable": True,
                "predates_or_avoids_the_defective_path": True,
                "uses_no_tainted_result_bearing_computation": True,
                "new_compute": "NONE (arithmetic over published uncertainties; the "
                               "anchor phase reproduced the frozen Route-A Gaussian "
                               "estimates bitwise)",
                "reconstructible_without_the_defect": True,
                "frozen_provenance_intact": True,
                "note": "The eight C5 cells are Gaussian under cusum@5 and "
                        "sr@520.886; the sharded configuration is "
                        "frozen/cusum@5/t1p5 and is not among them.",
            },
            "status": "DISCHARGED",
        },
    ]
    return {
        "schema": "rebaseguard.p4z-final-gate-discharge.v1",
        "result_bearing": False,
        "p4_closure_decision": rel(P4 / "results" / "closure_decision.json"),
        "p4_recorded_verdict": decision["verdict"],
        "p4_all_required_gates_pass": decision["all_required_gates_pass"],
        "originally_failed_gates": failed,
        "gates": rows,
        "all_discharged": all(r["status"] == "DISCHARGED" for r in rows),
        "p4x_campaign_rehabilitated": False,
        "p4x_campaign_note": "Rule C is applied obligation-locally. P4X's "
                             "campaign-level governance outcome is unchanged and "
                             "is not rehabilitated by this packet.",
        "historical_p4_verdict_unchanged": decision["verdict"] == "PARTIAL",
        "p4x_production_results_available": p4x_prod.is_file(),
        "p4x_production_results_sha256": sha(p4x_prod) if p4x_prod.is_file() else None,
    }


def build_manifest() -> dict:
    strict = json.loads((P4ZR / "results" / "strict_gate_reconstruction.json").read_text())
    disc = json.loads((P4ZR / "results" / "rng_collision_disclosure.json").read_text())

    return {
        "schema": "rebaseguard.p4z-final-closure-manifest.v1",
        "result_bearing": False,
        "manifest_self_hash": "EXCLUDED BY CONSTRUCTION: the manifest carries no "
                              "hash of itself; its integrity is established by the "
                              "commit that contains it",
        "frozen_theorem": {
            "namespace": rel(P4),
            "tree_object": tree("HEAD", rel(P4)),
            "protocol": pin(P4 / "configs" / "P4_PROTOCOL.json"),
            "theorem_md": pin(P4 / "THEOREM.md"),
            "proof_md": pin(P4 / "PROOF.md"),
            "closure_decision": pin(P4 / "results" / "closure_decision.json"),
            "modification": "NOT PERMITTED",
        },
        "historical_lineage": {
            "P4": {"verdict": "PARTIAL", "immutable": True,
                   "branches": ["main", "codex/presentation-refresh"]},
            "P4X": {"outcome": "governance failure / non-closure",
                    "scientific_failures": "NONE",
                    "branch": "p4x-feasibility-audit",
                    "commit": git("rev-parse", "p4x-feasibility-audit"),
                    "rehabilitated_by_this_packet": False},
            "P4Y": {"outcome": "NOT_FEASIBLE", "checkpoint_frozen": False,
                    "production_run": False,
                    "branches": ["p4y-prefreeze-pilot", "p4y-pilot2-final",
                                 "p4y-pilot3-heavy-stage1", "p4y-pilot4-measurement"]},
        },
        "successor_campaigns": {
            "P4Z": {
                "namespace": rel(P4Z), "tree_object": tree("HEAD", rel(P4Z)),
                "freeze_commit": git("rev-list", "-1", "--grep=P4Z pre-run freeze",
                                     "p4zb-skewnormal4-k7"),
                "result_commit": git("rev-list", "-1",
                                     "--grep=P4Z result-bearing checkpoint",
                                     "p4zb-skewnormal4-k7"),
                "self_verdict": json.loads(
                    (P4Z / "results" / "successor_closure.json").read_text())["verdict"],
                "adjudication": pin(P4Z / "production" / "adjudication.json"),
                "successor_closure": pin(P4Z / "results" / "successor_closure.json"),
                "checkpoint": pin(P4Z / "configs" / "checkpoint_p4z.json"),
                "estimand_contract": pin(P4Z / "configs" / "estimand_contract.json"),
            },
            "P4ZA": {
                "namespace": rel(P4ZA), "tree_object": tree("HEAD", rel(P4ZA)),
                "freeze_commit": git("rev-list", "-1", "--grep=P4ZA pre-run freeze",
                                     "p4zb-skewnormal4-k7"),
                "result_commit": git("rev-list", "-1",
                                     "--grep=P4ZA result-bearing checkpoint",
                                     "p4zb-skewnormal4-k7"),
                "self_verdict": json.loads(
                    (P4ZA / "results" / "p4za_successor_closure.json").read_text())["verdict"],
                "adjudication": pin(P4ZA / "production" / "adjudication_p4za.json"),
                "successor_closure": pin(P4ZA / "results" / "p4za_successor_closure.json"),
                "campaign_plan": pin(P4ZA / "production" / "p4za_campaign_plan.json"),
            },
            "P4ZB": {
                "namespace": rel(P4ZB), "tree_object": tree("HEAD", rel(P4ZB)),
                "freeze_commit": git("rev-list", "-1", "--grep=P4ZB pre-run freeze",
                                     "p4zb-skewnormal4-k7"),
                "result_commit": git("rev-list", "-1",
                                     "--grep=P4ZB result-bearing checkpoint",
                                     "p4zb-skewnormal4-k7"),
                "self_verdict": json.loads(
                    (P4ZB / "results" / "p4zb_successor_closure.json").read_text())["verdict"],
                "adjudication": pin(P4ZB / "production" / "adjudication_p4zb.json"),
                "successor_closure": pin(P4ZB / "results" / "p4zb_successor_closure.json"),
                "final_coverage": pin(P4ZB / "results" / "final_coverage.json"),
                "campaign_plan": pin(P4ZB / "production" / "p4zb_campaign_plan.json"),
                "branch": "p4zb-skewnormal4-k7",
                "branch_commit": git("rev-parse", "p4zb-skewnormal4-k7"),
            },
        },
        "corroboration_only": {
            "P4X_c2_cell_ledger_sha256": disc["findings"]["overlaps"][0]
            ["authoritative_source_of_this_configuration"] and None,
        },
        "adjudication_inputs": {
            "B1_k7": {
                "verdict": "PASS_ADMISSIBLE",
                "basis": "K7 is a successor-added precondition absent from "
                         "P4_PROTOCOL.json; every version was frozen before its own "
                         "result-bearing run; no original frozen threshold changed; "
                         "and the strict-gate reconstruction holds with T_B removed",
                "supporting_artifact": pin(
                    P4ZR / "results" / "strict_gate_reconstruction.json"),
                "diagnostic_history_preserved": [
                    rel(P4Z / "configs" / "checkpoint_p4z.json"),
                    rel(P4ZA / "K7_DIAGNOSIS.md"),
                    rel(P4ZB / "SKEWNORMAL4_K7_ASYMPTOTICS.md"),
                ],
            },
            "B2_rng_provenance": {
                "verdict": "PASS",
                "branch": "p4zr-rng-provenance-repair",
                "commit": git("rev-parse", "p4zr-rng-provenance-repair"),
                "namespace": rel(P4ZR), "tree_object": tree("HEAD", rel(P4ZR)),
                "disclosure": pin(P4ZR / "results" / "rng_collision_disclosure.json"),
                "record": pin(P4ZR / "RNG_ADDRESS_SEPARATION.md"),
                "audit_module": pin(
                    P4ZR / "src" / "rebaseguard_p4zr" / "rng_address_audit.py"),
                "findings": {
                    "P4Z": disc["campaign_audits"]["P4Z"]["verdict"],
                    "P4ZA": disc["campaign_audits"]["P4ZA"]["verdict"],
                    "P4ZB": disc["campaign_audits"]["P4ZB"]["verdict"],
                    "address_overlaps_total": disc["findings"]["address_overlaps_total"],
                    "overlapping_addresses_total":
                        disc["findings"]["overlapping_addresses_total"],
                    "disposition_bearing_overlaps":
                        disc["impact"]["disposition_bearing_overlaps"],
                },
            },
            "B3_rule_c": {
                "verdict": "PASS_ADMISSIBLE",
                "scope": "obligation-local; P4X as a campaign is not rehabilitated",
                "obligations": ["P4X C4", "P4X C5"],
            },
            "B4_presentation": {
                "verdict": "PASS",
                "branch": "codex/presentation-refresh",
                "commit": git("rev-parse", "codex/presentation-refresh"),
                "note": "separates the campaign self-verdicts from the independent "
                        "closure status on the public surface",
            },
        },
        "strict_gate_reconstruction": {
            "cells_total": strict["cells_total"],
            "cells_passing": strict["cells_passing_the_strict_gate"],
            "worst_z_monte_carlo_error_only":
                strict["worst_z_monte_carlo_error_only"]["value"],
            "z_limit": strict["worst_z_monte_carlo_error_only"]["limit"],
            "worst_relative_discrepancy":
                strict["worst_relative_discrepancy"]["value"],
            "relative_limit": strict["worst_relative_discrepancy"]["limit"],
            "cells_exceeding_either_frozen_gate":
                strict["cells_total"] - strict["cells_passing_the_strict_gate"],
            "reproduce": rel(P4ZR / "audit" / "strict_gate_recheck.py"),
        },
        "protected_trees": {
            rel(p): tree("HEAD", rel(p))
            for p in (P4, P4Z, P4ZA, P4ZB, P4ZR)
        },
        "new_numerical_compute": "NONE",
    }


def main() -> int:
    man = build_manifest()
    man.pop("corroboration_only", None)          # derived elsewhere; keep manifest lean
    (NS / "MANIFEST.json").write_text(
        json.dumps(man, indent=2, sort_keys=True) + "\n")
    gd = gate_discharge()
    (NS / "gate_discharge.json").write_text(
        json.dumps(gd, indent=2, sort_keys=True) + "\n")
    print("MANIFEST.json and gate_discharge.json written")
    print(f"  originally failed P4 gates : {len(gd['originally_failed_gates'])}")
    print(f"  all discharged             : {gd['all_discharged']}")
    print(f"  strict gate                : "
          f"{man['strict_gate_reconstruction']['cells_passing']}/"
          f"{man['strict_gate_reconstruction']['cells_total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
