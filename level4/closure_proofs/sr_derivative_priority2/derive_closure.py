#!/usr/bin/env python3
"""Mechanically derive the seven-category Priority-2 verdict."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parent
ROOT = CAMPAIGN.parents[2]
SR_ROOT = "level4/closure_proofs/sr_derivative"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    assumptions = json.loads((CAMPAIGN / "results" / "assumption_discharge.json").read_text())
    numerical = json.loads((CAMPAIGN / "results" / "numerical_correspondence.json").read_text())
    certificate = json.loads((CAMPAIGN / "certificates" / "certificate.json").read_text())
    lean = json.loads((CAMPAIGN / "results" / "lean_compile.json").read_text())
    verification = json.loads((CAMPAIGN / "results" / "verification.json").read_text())
    frozen = manifest["frozen_new_inputs"]
    history = manifest["immutable_sr_history"]
    inputs_clean = all(
        sha(CAMPAIGN / frozen[key]) == frozen[f"{key}_sha256"]
        for key in ("numerical_protocol", "finite_support_witness", "assumption_targets")
    )
    history_clean = sha(CAMPAIGN / history["manifest"]) == history["manifest_sha256"]
    current_tree = subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{SR_ROOT}"], cwd=ROOT, text=True
    ).strip()
    protected_worktree_clean = subprocess.run(
        ["git", "diff", "--quiet", "--", SR_ROOT], cwd=ROOT
    ).returncode == 0
    documents = ["SR_HISTORY_AUDIT.md", "DEFINITION_AUDIT.md", "THEOREM.md",
                 "PROOF.md", "ASSUMPTION_DISCHARGE.md", "INHERITANCE_LEDGER.md",
                 "CORRESPONDENCE_TABLE.md", "NUMERICAL_CORRESPONDENCE.md",
                 "CERTIFICATE_REPORT.md", "LEAN_CORRESPONDENCE.md"]
    categories = {
        "sr_definition_history_audit": all((CAMPAIGN / p).is_file() for p in documents[:2]),
        "analytical_sr_theorem_closure": assumptions["all_analytical_obligations_discharged"]
            and all(row["status"] in ("PROVED", "INHERITED_GENERIC") for row in assumptions["obligations"]),
        "lean_proof_spine_closure": lean["compiled"] and not lean["sorryAx"]
            and lean["axiom_audit_declarations"] == 7
            and sha(CAMPAIGN / lean["source"]) == manifest["lean"]["source_sha256"],
        "frozen_gaussian_sr_numerical_correspondence":
            numerical["decision"]["all_required_numerical_gates_pass"]
            and numerical["protocol_sha256"] == frozen["numerical_protocol_sha256"],
        "finite_support_arb_certification": certificate["all_checks_pass"]
            and certificate["witness_sha256"] == frozen["finite_support_witness_sha256"],
        "cross_representation_correspondence": all((CAMPAIGN / p).is_file() for p in documents[4:]),
        "frozen_history_inheritance_integrity": inputs_clean and history_clean
            and current_tree == history["additive_sr_certificate"]["git_tree"]
            and protected_worktree_clean and verification["required_regressions_pass"],
    }
    all_pass = all(categories.values())
    verdict = "CLOSED" if all_pass else ("PARTIALLY_CLOSED" if any(categories.values()) else "NOT_CLOSED")
    payload = {
        "campaign": "Level-4 Priority 2 Shiryaev-Roberts derivative closure",
        "verdict": verdict, "categories": categories,
        "all_required_gates_pass": all_pass,
        "frozen_infinite_horizon_gaussian_sr_m_gt_1_interval_certified": False,
        "historical_diagnostics": verification["historical_diagnostics"],
        "closure_wording": "Level-4 Priority 2 -- the Shiryaev-Roberts derivative theorem and its declared validation package are closed." if all_pass else "Priority-2 closure requirements are not all satisfied.",
        "evidence_boundary": "Arb certification is for the exact finite-support SR-compatible witness only.",
    }
    (CAMPAIGN / "results" / "closure_decision.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
