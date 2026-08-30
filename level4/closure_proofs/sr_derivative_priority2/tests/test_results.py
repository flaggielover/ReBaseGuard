from __future__ import annotations

import json
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]


def test_all_analytical_obligations_are_proved_without_numerics() -> None:
    result = json.loads((CAMPAIGN / "results" / "assumption_discharge.json").read_text())
    assert result["all_analytical_obligations_discharged"]
    assert not result["numerical_evidence_used"]
    assert [row["id"] for row in result["obligations"]] == [f"SR-A{i}" for i in range(1, 9)]
    assert all(row["status"] == "PROVED" for row in result["obligations"])


def test_all_preregistered_numerical_cells_pass() -> None:
    result = json.loads((CAMPAIGN / "results" / "numerical_correspondence.json").read_text())
    assert result["protocol"]["m_grid"] == [1, 2, 3, 5]
    assert result["protocol"]["rho_grid"] == [0.05, 0.1, 0.25]
    assert len(result["decision"]["cells"]) == 12
    assert result["decision"]["all_required_numerical_gates_pass"]
    assert all(row["pass"] for row in result["decision"]["cells"])
    assert result["final"]["short_cycle_counts"] == [0, 0, 1, 37]
    assert "Not an Arb" in result["evidence_boundary"]


def test_lean_boundary_and_axiom_audit() -> None:
    result = json.loads((CAMPAIGN / "results" / "lean_compile.json").read_text())
    assert result["compiled"] and result["axiom_audit_declarations"] == 7
    assert not result["sorryAx"]
    assert not result["imports_historical_sr_theorem"]
    assert not result["concrete_gaussian_domination_machine_checked"]
    audit = (CAMPAIGN / "results" / "axiom_audit.txt").read_text()
    assert audit.count("depends on axioms") == 7
    assert "sorryAx" not in audit


def test_required_reports_preserve_evidence_boundary() -> None:
    required = ["README.md", "THEOREM.md", "PROOF.md", "SR_HISTORY_AUDIT.md",
                "DEFINITION_AUDIT.md", "ASSUMPTION_DISCHARGE.md",
                "NUMERICAL_CORRESPONDENCE.md", "CERTIFICATE_REPORT.md",
                "LEAN_CORRESPONDENCE.md", "INHERITANCE_LEDGER.md",
                "CORRESPONDENCE_TABLE.md"]
    assert all((CAMPAIGN / path).is_file() for path in required)
    combined = "\n".join((CAMPAIGN / path).read_text() for path in (
        "README.md", "NUMERICAL_CORRESPONDENCE.md", "CERTIFICATE_REPORT.md"
    ))
    assert "finite-support" in combined
    assert "not an Arb" in combined or "not an interval" in combined


def test_mechanical_seven_category_closure() -> None:
    result = json.loads((CAMPAIGN / "results" / "closure_decision.json").read_text())
    assert result["verdict"] == "CLOSED"
    assert result["all_required_gates_pass"]
    assert len(result["categories"]) == 7 and all(result["categories"].values())
    assert not result["frozen_infinite_horizon_gaussian_sr_m_gt_1_interval_certified"]
    report = (CAMPAIGN / "CLOSURE_REPORT.md").read_text()
    assert "Level-4 Priority 2 -- CLOSED" in report
    assert "HISTORICAL_DIAGNOSTICS" in report
    assert "does not interval-certify frozen Gaussian SR" in report
