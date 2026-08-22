from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]


def _decision():
    return json.loads((CAMPAIGN / "results/decision.json").read_text())


def test_final_status_is_partial_and_preserves_failed_gate():
    decision = _decision()
    assert decision["decision"] == "LOCATION-FAMILY-THEOREM-PARTIAL"
    assert decision["general_location_family_theorem_requirement"] == "PARTIAL"
    assert decision["human_theorem"] == "PROVED UNDER EXPLICIT ANALYTIC HYPOTHESES"
    assert decision["numerical_gate"] == "LOCATION-FAMILY-NUMERICAL-FAILED"


def test_exact_theorem_and_score_sign_are_frozen():
    theorem = _decision()["theorem"]
    assert theorem["parameter_score"] == "s(z)=f'(z)/f(z)"
    assert theorem["sign_relation"] == "s=-psi"
    assert theorem["abstract_derivative"] == "d/de E_e[H_tau]|_0=E_0[H_tau S_tau]"
    assert theorem["rebaseguard_derivative"] == "F'_rho(0)=rho(1-Gamma_f)"


def test_lean_and_axiom_audit_were_not_run():
    lean = _decision()["lean"]
    assert lean["authorized"] is False
    assert lean["status"] == "NOT RUN"
    assert lean["declarations"] == []
    assert lean["axiom_audit"] == "NOT RUN"
    assert not (CAMPAIGN / "lean").exists()


def test_final_report_keeps_claim_and_history_boundaries():
    report = " ".join((CAMPAIGN / "FINAL_REPORT.md").read_text().split())
    required = [
        "LOCATION-FAMILY-THEOREM-PARTIAL",
        "Historical Stage-D t3 remains `AMBIGUOUS`",
        "Lean status: NOT AUTHORIZED / NOT RUN",
        "Stage F and overall Level 4 remain `LEVEL-4-PARTIAL`",
        "not distribution-free, universal, detector-independent",
    ]
    assert all(fragment in report for fragment in required)


def test_reproducer_has_every_gate_and_valid_shell():
    script = CAMPAIGN / "reproduce.sh"
    subprocess.run(["bash", "-n", str(script)], check=True)
    text = script.read_text()
    for fragment in (
        "historical closure-track suites",
        "Track-3 retained artifacts and tests",
        "audit_numerical.py",
        "Lean correctly NOT AUTHORIZED / NOT RUN",
        "scripts/verify_level_4.sh",
    ):
        assert fragment in text


def test_final_artifact_manifest_is_exact():
    manifest = json.loads(
        (CAMPAIGN / "results/final_artifact_manifest.json").read_text()
    )
    assert manifest["decision"] == "LOCATION-FAMILY-THEOREM-PARTIAL"
    for relative, expected in manifest["sha256"].items():
        actual = hashlib.sha256((REPO / relative).read_bytes()).hexdigest()
        assert actual == expected, relative

