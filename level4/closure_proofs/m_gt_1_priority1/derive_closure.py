#!/usr/bin/env python3
"""Mechanically derive the five-category Priority-1 closure decision."""

from __future__ import annotations

import hashlib
import json
import locale
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parent
ROOT = CAMPAIGN.parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def track1b_hash() -> str:
    base = ROOT / "level4/closure_proofs/m_gt_1_track1b"
    locale.setlocale(locale.LC_COLLATE, "")
    files = sorted(
        (p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts),
        key=lambda p: locale.strxfrm(str(p.relative_to(ROOT))),
    )
    listing = "".join(f"{sha(p)}  {p.relative_to(ROOT)}\n" for p in files)
    return hashlib.sha256(listing.encode()).hexdigest()


def main() -> None:
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    numerical = json.loads((CAMPAIGN / "results/numerical_correspondence.json").read_text())
    certificate = json.loads((CAMPAIGN / "certificates/certificate.json").read_text())
    lean = json.loads((CAMPAIGN / "results/lean_compile.json").read_text())
    verification = json.loads((CAMPAIGN / "results/verification.json").read_text())
    old = manifest["immutable_prior_evidence"]
    required_human = ["DEFINITION_AUDIT.md", "THEOREM.md", "PROOF.md"]
    required_cross = ["NUMERICAL_CORRESPONDENCE.md", "LEAN_CORRESPONDENCE.md",
                      "CERTIFICATE_REPORT.md", "CORRESPONDENCE_TABLE.md",
                      "INHERITANCE_LEDGER.md"]

    analytical = all((CAMPAIGN / name).is_file() for name in required_human)
    lean_pass = (
        lean["compiled"]
        and sha(CAMPAIGN / lean["source"]) == manifest["lean"]["source_sha256"]
        and (CAMPAIGN / "results/axiom_audit.txt").read_text().count("depends on axioms") == 5
    )
    numerical_pass = (
        numerical["decision"]["all_cells_pass"]
        and numerical["protocol_sha256"] == manifest["frozen_new_inputs"]["numerical_protocol_sha256"]
    )
    certificate_pass = (
        certificate["all_checks_pass"]
        and certificate["witness_sha256"] == manifest["frozen_new_inputs"]["finite_support_witness_sha256"]
    )
    parent_clean = subprocess.run(
        ["git", "diff", "--quiet", "--", "level4/closure_proofs/m_gt_1"], cwd=ROOT
    ).returncode == 0
    integrity_pass = (
        track1b_hash() == old["track1b_tree_sha256"]
        and sha(ROOT / "level4/stage_d/results/d2_3_derivative.json") == old["historical_d2_3_sha256"]
        and sha(ROOT / "level4/stage_d/results/stage_d_decision.json") == old["historical_stage_d_decision_sha256"]
        and sha(ROOT / "level4/closure_proofs/m_gt_1_track1a/results/decision.json") == old["historical_track1a_decision_sha256"]
        and parent_clean
        and all((CAMPAIGN / name).is_file() for name in required_cross)
        and verification["campaign_focused_tests"]["status"] == "PASS"
        and verification["level_1_3_full_verifier"]["status"] == "PASS"
    )
    categories = {
        "analytical_theorem_closure": analytical,
        "lean_proof_spine_closure": lean_pass,
        "frozen_gaussian_cusum_numerical_correspondence": numerical_pass,
        "finite_support_arb_certification": certificate_pass,
        "frozen_history_inheritance_integrity": integrity_pass,
    }
    verdict = "CLOSED" if all(categories.values()) else (
        "PARTIALLY_CLOSED" if any(categories.values()) else "NOT_CLOSED"
    )
    result = {
        "campaign": "Level-4 Priority 1 general Stage-D m>1 derivative theorem",
        "verdict": verdict,
        "categories": categories,
        "all_required_gates_pass": all(categories.values()),
        "frozen_gaussian_m_gt_1_interval_certified": False,
        "evidence_boundary": "Arb certification is for the exact finite-support witness only.",
        "unrelated_repository_gate_failure": verification["level_4_regression"],
    }
    out = CAMPAIGN / "results/closure_decision.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
