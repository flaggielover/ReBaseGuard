"""Focused guards for the optional SR monotone-resolvent component."""

from __future__ import annotations

import json
from pathlib import Path


CAMPAIGN = Path(__file__).resolve().parents[1]
CERTIFICATE = CAMPAIGN / "certificate"
RESULTS = CAMPAIGN / "results"


def test_resolvent_artifact_uses_exact_authoritative_model():
    result = json.loads((RESULTS / "sr_monotone_contraction.json").read_text())
    assert result["threshold"]["runtime_rational"] == [
        4581762885148045,
        8796093022208,
    ]
    assert result["n"] == 250
    assert result["q_safe"]["numerator"] == 19
    assert result["q_safe"]["denominator"] == 100
    assert result["proof"]["sampled_grid_used"] is False


def test_resolvent_audit_passes_and_remains_component_scoped():
    audit = json.loads(
        (RESULTS / "sr_monotone_contraction_audit.json").read_text()
    )
    assert audit["status"] == "PASS"
    assert all(audit["checks"].values())
    assert audit["overall_sr_gamma_certificate"] == "OPEN"


def test_resolvent_auditor_is_source_independent():
    source = (CERTIFICATE / "audit_sr_resolvent.py").read_text()
    assert "import certify_sr_resolvent" not in source
    assert "from certify_sr_resolvent" not in source
    assert "scalar/list Arb replay" in source


def test_resolvent_proof_records_continuum_arguments():
    result = json.loads((RESULTS / "sr_monotone_contraction.json").read_text())
    proof = result["proof"]
    assert "increasing" in proof["pathwise_monotonicity"]
    assert "left endpoint" in proof["cell_rule"]
    assert "plus-chart hit" in proof["two_chart_domination"]
    assert proof["operator_statement"] == "sup_s K^n 1(s) <= 1-q_safe"
    assert proof["resolvent_statement"] == "||(I-K)^-1||_inf <= n/q_safe"
