#!/usr/bin/env python3
"""Mechanically derive the Priority-3 verdict from the produced artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parent
ROOT = CAMPAIGN.parents[2]
sys.path.insert(0, str(CAMPAIGN / "src"))

REQUIRED_DOCUMENTS = [
    "README.md", "THEOREM.md", "PROOF.md", "EVIDENCE_BOUNDARY.md",
    "PROVENANCE.md", "CLOSURE_REPORT.md", "LEAN_CORRESPONDENCE.md",
    "STABILITY_MAP_REPORT.md",
]
REQUIRED_ARTIFACTS = [
    "configs/MAP_PROTOCOL.json",
    "results/provenance.json",
    "results/stability_map.json",
    "results/stability_map.csv",
    "results/boundary_table.json",
    "results/lean_compile.json",
    "results/axiom_audit.txt",
    "results/verification.json",
    "arb/certificate.json",
    "figures/figure_index.json",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative: str) -> dict:
    return json.loads((CAMPAIGN / relative).read_text())


def main() -> None:
    manifest = load("manifest.json")
    provenance = load("results/provenance.json")
    stability = load("results/stability_map.json")
    boundaries = load("results/boundary_table.json")
    certificate = load("arb/certificate.json")
    lean = load("results/lean_compile.json")
    verification = load("results/verification.json")
    figures = load("figures/figure_index.json")
    required_regressions = {
        "priority3_focused", "level_1_3_full", "priority1", "priority2",
        "historical_sr", "track1b", "d4_phase_map",
        "external_validation_v3", "l4r06_policy", "l4r12_operational",
    }

    frozen = manifest["frozen_new_inputs"]
    protocol_clean = (
        sha(CAMPAIGN / frozen["map_protocol"]) == frozen["map_protocol_sha256"]
        and stability["protocol_sha256"] == frozen["map_protocol_sha256"]
        and provenance["protocol_sha256"] == frozen["map_protocol_sha256"]
        and certificate["protocol_sha256"] == frozen["map_protocol_sha256"]
    )
    upstream_clean = all(
        sha(ROOT / relative) == expected
        for relative, expected in manifest["upstream_sources"].items()
    )
    protected_clean = all(
        subprocess.run(["git", "diff", "--quiet", "HEAD", "--", tree],
                       cwd=ROOT).returncode == 0
        for tree in manifest["protected_trees_read_only"]
    )
    upstream_closed = all(
        json.loads((ROOT / package / "results" / "closure_decision.json").read_text())
        ["verdict"] == "CLOSED"
        for package in (
            "level4/closure_proofs/m_gt_1_priority1",
            "level4/closure_proofs/sr_derivative_priority2",
        )
    )
    documents_present = all((CAMPAIGN / name).is_file() for name in REQUIRED_DOCUMENTS)
    artifacts_present = all((CAMPAIGN / name).is_file() for name in REQUIRED_ARTIFACTS)

    empirical_never_certified = all(
        cell["evidence_class"] != "THEOREM_PLUS_CERTIFIED_INPUT"
        for cell in stability["cells"] + stability["boundary_cells"]
        if cell["gamma_evidence_class"] == "EMPIRICAL_ONLY"
    )
    fragile_never_robust = all(
        cell["evidence_class"] == "INCONCLUSIVE"
        for cell in stability["cells"] + stability["boundary_cells"]
        if not cell["classification_reportable_as_robust"]
    )

    categories = {
        "theorem_and_report_consistency": documents_present
            and stability["derivative_identity"].endswith("rho(1 - GammaTilde_{D,m})"),
        "machine_readable_artifact_schema": artifacts_present
            and stability["schema"] == "rebaseguard.p3-stability-map.v1"
            and boundaries["schema"] == "rebaseguard.p3-boundary-table.v1"
            and stability["valid"] and all(stability["checks"].values()),
        "provenance_and_protected_history": protocol_clean and upstream_clean
            and protected_clean and upstream_closed
            and provenance["upstream_hashes"]["all_match"],
        "cross_detector_map_completeness": len(stability["layers"]) == 4
            and len({layer["source_priority"] for layer in stability["layers"]}) == 2
            and len(stability["cells"]) == 4 * len(stability["m_grid"])
                * len(stability["rho_grid"])
            and len(stability["boundary_cells"]) == 4 * len(stability["m_grid"]),
        "evidence_hierarchy_separation": empirical_never_certified
            and fragile_never_robust
            and certificate["gaussian_layers_certified"] is False,
        "rigorous_interval_certification": certificate["all_checks_pass"],
        "lean_spine_and_axiom_audit": lean["compiled"] and not lean["sorryAx"]
            and not lean["project_specific_scientific_axioms"]
            and lean["axiom_audit_declarations"] == 14
            and sha(CAMPAIGN / lean["source"]) == manifest["lean"]["source_sha256"],
        "figure_data_correspondence":
            figures["traceability"]["every_plotted_cell_traceable"]
            and all(sha(CAMPAIGN / name) == digest
                    for name, digest in figures["figures"].items()),
        "independent_adversarial_adjudication":
            manifest["independent_adjudication"]["candidate_intake_aggregate_sha256"]
                == "41f82b34481bc2427d16a9534affb9fdd0c6efa328db4467d96f0f8f193bc319"
            and not manifest["independent_adjudication"]["candidate_closed_verdict_inherited"]
            and not manifest["independent_adjudication"]
                ["temporal_preregistration_of_candidate_protocol_independently_authenticated"],
        "repository_regressions_and_diagnostics":
            verification["schema"] == "rebaseguard.p3-verification.v3"
            and required_regressions <= set(verification["required_suites"])
            and verification["required_regressions_pass"]
            and verification["environment_diagnostics_reproduce_without_priority3"]
            and verification["controlled_environment_matrix"]["all_checks_pass"]
            and verification["historical_diagnostics_unchanged"]
            and verification["all_gates_pass"],
    }

    all_pass = all(categories.values())
    verdict = "CLOSED" if all_pass else (
        "PARTIALLY_CLOSED" if any(categories.values()) else "NOT_CLOSED")

    payload = {
        "campaign": "Level-4 Priority 3 theorem-supported m-rho stability map",
        "verdict": verdict,
        "categories": categories,
        "all_required_gates_pass": all_pass,
        "frozen_infinite_horizon_gaussian_gains_interval_certified": False,
        "candidate_intake_aggregate_sha256": manifest["independent_adjudication"]
            ["candidate_intake_aggregate_sha256"],
        "candidate_original_closed_verdict": "MODIFIED_THEN_INDEPENDENTLY_ADJUDICATED",
        "post_hoc_gate_widening_accepted": False,
        "literal_required_environment_sensitive_suites_pass":
            all(next(row for row in verification["suites"] if row["label"] == label)
                ["exit_code"] == 0 for label in ("priority1", "historical_sr", "track1b")),
        "candidate_protocol_temporal_preregistration_authenticated": False,
        "global_or_nonlinear_stability_claimed": False,
        "detector_universal_stability_claimed": False,
        "non_gaussian_generality_claimed": False,
        "historical_diagnostics": verification["historical_diagnostics"],
        "environment_diagnostics": verification["environment_diagnostics"],
        "closure_wording": (
            "Level-4 Priority 3 -- the theorem-supported m-rho local stability map "
            "has been mechanically derived from the closed detector-specific "
            "derivative theorems, with explicit evidence boundaries separating "
            "rigorous/certified statements from empirical Gaussian correspondence."
            if all_pass else
            "Priority-3 closure requirements are not all satisfied."
        ),
        "evidence_boundary": stability["evidence_boundary"],
        "claim_scope": stability["claim_scope"],
    }
    (CAMPAIGN / "results" / "closure_decision.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
