from __future__ import annotations

import re
from pathlib import Path


CAMPAIGN = Path(__file__).resolve().parents[1]
MAIN = CAMPAIGN / "lean/LocationFamilyTrack3AB.lean"
AUDIT = CAMPAIGN / "lean/AxiomAudit.lean"


def test_lean_source_contains_complete_authorized_spine() -> None:
    source = MAIN.read_text()
    required = {
        "parameterScoreSum_eq_neg_conventional",
        "stoppedScore_derivative_bridge",
        "rho_scaling",
        "locationFamily_derivative_spine",
        "reflectPath_involutive",
        "conventionalScoreSum_reflection",
        "reflected_stopped_gain",
        "reuseMean_odd",
        "gaussian_score_specialization",
        "gaussian_score_sum_specialization",
        "gaussian_gain_specialization",
        "gamma_threshold_derivative_lt_neg_one",
        "gamma_gt_two_full_reuse_derivative_lt_neg_one",
        "raw_gain_ne_terminal_score_gain",
        "gaussian_terminal_gain_eq_raw",
    }
    assert all(f"theorem {name}" in source for name in required)
    assert "import RebaseguardLean.IntegralBridge" in source


def test_lean_has_no_bypass_or_project_axiom() -> None:
    source = MAIN.read_text()
    assert not re.search(r"\b(sorry|admit|axiom)\b", source)


def test_axiom_audit_has_exact_allowlist() -> None:
    audit_source = AUDIT.read_text()
    output = (CAMPAIGN / "results/axiom_audit.txt").read_text()
    declarations = re.findall(
        r"#print axioms RebaseguardLean\.LocationFamilyTrack3AB\.([A-Za-z0-9_]+)",
        audit_source,
    )
    assert len(declarations) == 16
    assert output.count("depends on axioms") == 16
    assert all(
        f"LocationFamilyTrack3AB.{name}' depends on axioms" in output
        for name in declarations
    )
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    found = set(re.findall(r"(?:propext|Classical\.choice|Quot\.sound)", output))
    assert found == allowed
    assert "sorryAx" not in output


def test_correspondence_report_preserves_conditional_boundary() -> None:
    report = (CAMPAIGN / "LEAN_CORRESPONDENCE.md").read_text()
    assert "conditional formal proof spine" in report
    assert "remain human-proved for the concrete t3 process" in report
    assert "not described as an end-to-end formalization" in report
    assert "propext" in report
    assert "Classical.choice" in report
    assert "Quot.sound" in report
