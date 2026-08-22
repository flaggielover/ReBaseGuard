from __future__ import annotations

import hashlib
import json
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]


def test_final_decision_closes_only_derivative_theorem():
    decision = json.loads((CAMPAIGN / "results/decision.json").read_text())
    assert decision["decision"] == "SR-DERIVATIVE-CLOSED"
    assert all(value.startswith("PASS") for value in decision["closure_conditions"].values())
    boundary = decision["status_boundary"]
    assert boundary["derivative_theorem"] == "CLOSED"
    assert boundary["Gamma_SR_gt_2"] == "CONFIRMATORY NUMERICAL"
    assert boundary["rigorous_SR_local_instability_certificate"] == "OPEN"
    assert boundary["additional_status"] == "SR-GAMMA-CERTIFIED NOT AWARDED"


def test_final_decision_preserves_conditional_lean_boundary():
    decision = json.loads((CAMPAIGN / "results/decision.json").read_text())
    assert decision["lean"]["concrete_infinite_SR_instantiated"] is False
    assert set(decision["lean"]["axioms"]) == {
        "propext",
        "Classical.choice",
        "Quot.sound",
    }
    assert "domination" in decision["lean"]["human_only_concrete_obligations"]


def test_final_report_never_upgrades_open_arb_attempt():
    report = " ".join((CAMPAIGN / "FINAL_REPORT.md").read_text().split())
    required = [
        "derivative theorem: CLOSED",
        "Gamma_SR > 2: CONFIRMATORY NUMERICAL",
        "rigorous SR local-instability certificate: OPEN",
        "`SR-GAMMA-CERTIFIED` is not awarded",
        "No SR instability claim is described as certified or rigorous",
    ]
    assert all(fragment in report for fragment in required)


def test_historical_stage_f_remains_unchanged_and_not_reaudited():
    decision = json.loads((CAMPAIGN / "results/decision.json").read_text())
    stage_f = json.loads((REPO / "level4/stage_f/results/final_decision.json").read_text())
    assert decision["historical_status_preserved"]["stage_f"] == "LEVEL-4-PARTIAL"
    assert decision["historical_status_preserved"]["global_level4_reaudit_performed"] is False
    assert stage_f["decision"] == "LEVEL-4-PARTIAL"


def test_verification_counts_and_protocol_are_frozen():
    decision = json.loads((CAMPAIGN / "results/decision.json").read_text())
    assert decision["verification"]["historical_closure_tests"] == 110
    assert decision["verification"]["track2_tests"] == 58
    assert decision["verification"]["closure_track_tests_total"] == 168
    assert decision["verification"]["authoritative_tests"] == 695
    assert decision["verification"]["combined_checks"] == 863
    assert decision["verification"]["authoritative_result"] == "LEVEL 4 VERIFICATION OK"
    assert decision["protocol"]["sha256"] == (
        "e9b66ff8ffbf0d8138598b1d4dc19dcc1e44d8b4f33f5b462b5b82f341d5f762"
    )


def test_final_artifact_manifest_is_complete_and_exact():
    manifest = json.loads(
        (CAMPAIGN / "results/final_artifact_manifest.json").read_text()
    )
    assert manifest["schema"] == "rebaseguard.sr-derivative.final-artifacts.v1"
    assert manifest["protocol_sha256"] == (
        "e9b66ff8ffbf0d8138598b1d4dc19dcc1e44d8b4f33f5b462b5b82f341d5f762"
    )
    required = {
        "level4/closure_proofs/sr_derivative/FINAL_REPORT.md",
        "level4/closure_proofs/sr_derivative/results/decision.json",
        "level4/reports/SR_DERIVATIVE_THEOREM_REPORT.md",
    }
    assert required <= set(manifest["sha256"])
    for relative, expected in manifest["sha256"].items():
        actual = hashlib.sha256((REPO / relative).read_bytes()).hexdigest()
        assert actual == expected, relative
