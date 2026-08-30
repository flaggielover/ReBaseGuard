from __future__ import annotations

import hashlib
import json
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frozen_input_hashes() -> None:
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    frozen = manifest["frozen_new_inputs"]
    assert digest(CAMPAIGN / frozen["numerical_protocol"]) == frozen["numerical_protocol_sha256"]
    assert digest(CAMPAIGN / frozen["finite_support_witness"]) == frozen["finite_support_witness_sha256"]


def test_numerical_correspondence_passes_preregistered_grid() -> None:
    result = json.loads((CAMPAIGN / "results/numerical_correspondence.json").read_text())
    assert result["protocol_sha256"] == json.loads((CAMPAIGN / "manifest.json").read_text())["frozen_new_inputs"]["numerical_protocol_sha256"]
    assert result["protocol"]["m_grid"] == [1, 2, 3, 5]
    assert result["protocol"]["rho_grid"] == [0.05, 0.1, 0.25]
    assert len(result["decision"]["cells"]) == 12
    assert result["decision"]["all_cells_pass"]
    assert all(cell["pass"] for cell in result["decision"]["cells"])
    assert "Not an Arb" in result["evidence_boundary"]


def test_interval_certificate_passes_and_is_bounded() -> None:
    result = json.loads((CAMPAIGN / "certificates/certificate.json").read_text())
    assert result["evidence_class"] == "RIGOROUS_INTERVAL_FINITE_SUPPORT_ONLY"
    assert result["all_checks_pass"]
    assert [record["m"] for record in result["records"]] == [2, 3, 5]
    for record in result["records"]:
        assert all(record["checks"].values())
        assert record["exact"]["gamma"] == "15/2"
        assert record["exact"]["attraction_derivative"] == "-13/20"
        assert record["exact"]["repulsion_derivative"] == "-13/8"
    assert "not a frozen Gaussian" in result["evidence_boundary"]


def test_lean_compile_record_and_axiom_boundary() -> None:
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    result = json.loads((CAMPAIGN / "results/lean_compile.json").read_text())
    assert result["compiled"] and not result["imports_track1b"]
    assert not result["concrete_gaussian_cusum_domination_machine_checked"]
    assert digest(CAMPAIGN / result["source"]) == manifest["lean"]["source_sha256"]
    audit = (CAMPAIGN / "results/axiom_audit.txt").read_text()
    assert audit.count("depends on axioms") == 5
    assert "propext" in audit and "Classical.choice" in audit and "Quot.sound" in audit


def test_five_category_closure_decision() -> None:
    decision = json.loads((CAMPAIGN / "results/closure_decision.json").read_text())
    assert decision["verdict"] == "CLOSED"
    assert decision["all_required_gates_pass"]
    assert all(decision["categories"].values())
    assert not decision["frozen_gaussian_m_gt_1_interval_certified"]
    report = (CAMPAIGN / "CLOSURE_REPORT.md").read_text()
    for heading in (
        "Analytical theorem closure", "Lean proof-spine closure",
        "Frozen Gaussian CUSUM numerical correspondence",
        "Finite-support Arb certification",
        "Frozen-history and inheritance integrity",
    ):
        assert heading in report
