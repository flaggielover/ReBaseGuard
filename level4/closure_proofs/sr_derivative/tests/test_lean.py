from __future__ import annotations

import re
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
MAIN = CAMPAIGN / "lean/SRDerivative.lean"
AUDIT = CAMPAIGN / "lean/AxiomAudit.lean"


def test_lean_source_contains_every_authorized_spine_target():
    source = MAIN.read_text()
    declarations = {
        "srStep_reflection",
        "alarmed_reflection",
        "firstAlarm_reflection",
        "reflected_alarm_preserves_time",
        "reflected_alarm_negates_terminal_and_total",
        "reflected_terminal_product",
        "reuseMean_odd",
        "derivative_spine_of_dominated",
        "gamma_gt_two_full_reuse_instability",
        "authoritativeA_ne_historical",
    }
    assert all(f"theorem {name}" in source for name in declarations)
    assert "import RebaseguardLean.IntegralBridge" in source


def test_lean_source_has_no_bypass_or_scientific_axiom():
    source = MAIN.read_text()
    assert not re.search(r"\b(sorry|admit|axiom)\b", source)


def test_axiom_audit_covers_headlines_and_has_exact_allowlist():
    audit_source = AUDIT.read_text()
    output = (CAMPAIGN / "results/axiom_audit.txt").read_text()
    printed = re.findall(r"#print axioms RebaseguardLean\.SRDerivative\.([A-Za-z0-9_]+)", audit_source)
    assert len(printed) == 9
    assert output.count("depends on axioms") == 9
    assert all(f"SRDerivative.{name}' depends on axioms" in output for name in printed)
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    found = set(re.findall(r"(?:propext|Classical\.choice|Quot\.sound)", output))
    assert found == allowed
    stripped = re.sub(r"(?:propext|Classical\.choice|Quot\.sound)", "", output)
    assert "sorryAx" not in stripped


def test_correspondence_report_states_conditional_boundary_and_open_certificate():
    report = (CAMPAIGN / "LEAN_CORRESPONDENCE.md").read_text()
    assert "conditional formal proof spine" in report
    assert "concrete SR tail, measurability" in report
    assert "not described as an end-to-end Lean formalization" in report
    assert "CONFIRMATORY NUMERICAL ONLY" in report
    assert "local-instability certificate remains `OPEN`" in report
