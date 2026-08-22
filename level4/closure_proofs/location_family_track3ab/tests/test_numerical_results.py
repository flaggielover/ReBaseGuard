from __future__ import annotations

import json
from pathlib import Path


CAMPAIGN = Path(__file__).resolve().parents[1]


def decision() -> dict:
    return json.loads((CAMPAIGN / "results/numerical_decision.json").read_text())


def test_exact_numerical_decision_and_lean_gate() -> None:
    data = decision()
    assert data["status"] == "T3A-NUMERICAL-PASS"
    assert data["gate"] == "NUMERICAL GATE CLOSED — LEAN AUTHORIZED"
    assert data["lean_authorized"] is True


def test_both_replications_pass_individually() -> None:
    data = decision()
    assert len(data["per_replication_correspondence"]) == 2
    assert all(cell["pass"] for cell in data["per_replication_correspondence"])
    assert all(
        cell["symmetric_relative_difference"] <= 0.03
        and cell["absolute_z"] <= 3.0
        for cell in data["per_replication_correspondence"]
    )


def test_replication_and_pooled_gates_pass() -> None:
    data = decision()
    assert data["route_a_replication_agreement"]["pass"] is True
    assert data["route_b_replication_agreement"]["pass"] is True
    assert data["pooled"]["comparison"]["pass"] is True
    assert data["pooled"]["comparison"]["symmetric_relative_difference"] < 0.03


def test_integrity_gates_and_ties() -> None:
    data = decision()
    assert all(data["integrity_gates"].values())
    assert data["structural"]["pass"] is True
    assert data["batch_identities"]["pass"] is True
    assert all(cell["ties"] == 0 for cell in data["route_a"] + data["route_b"])


def test_checkpoint_count_and_independent_audit() -> None:
    checkpoints = list((CAMPAIGN / "results/checkpoints").rglob("batch_*.json"))
    assert len(checkpoints) == 768
    audit = json.loads((CAMPAIGN / "results/numerical_audit.json").read_text())
    assert audit["checkpoint_count"] == 768
    assert audit["status"] == "T3A-NUMERICAL-PASS"
    assert audit["all_primary_pass"] is True


def test_historical_track3_failure_remains_visible() -> None:
    diagnosis = (CAMPAIGN / "VARIANCE_DIAGNOSIS.md").read_text()
    report = (CAMPAIGN / "REPLICATION_REPORT.md").read_text()
    assert "4.605351% > 3%" in diagnosis
    assert "4.605351% > 3%" in report
    assert "does not change the old failed decision" in report
