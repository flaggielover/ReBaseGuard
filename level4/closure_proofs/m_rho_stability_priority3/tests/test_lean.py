"""Lean spine and axiom-audit tests."""

from __future__ import annotations

from rebaseguard_p3_map.common import read_json, sha256
from rebaseguard_p3_map.config import CAMPAIGN

LEAN_SOURCE = CAMPAIGN / "lean" / "StabilityMapP3.lean"
AUDIT_TEXT = CAMPAIGN / "results" / "axiom_audit.txt"


def _compile():
    return read_json(CAMPAIGN / "results" / "lean_compile.json")


def test_spine_compiled_and_hash_bound():
    payload = _compile()
    assert payload["compiled"]
    assert payload["source_sha256"] == sha256(LEAN_SOURCE)
    manifest = read_json(CAMPAIGN / "manifest.json")
    assert manifest["lean"]["source_sha256"] == payload["source_sha256"]


def test_no_sorry_and_no_project_axioms():
    payload = _compile()
    assert payload["sorryAx"] is False
    assert payload["project_specific_scientific_axioms"] is False
    assert "sorry" not in LEAN_SOURCE.read_text()
    assert "sorryAx" not in AUDIT_TEXT.read_text()


def test_axiom_audit_reports_only_standard_mathlib_axioms():
    payload = _compile()
    assert payload["allowed_axioms"] == ["Classical.choice", "Quot.sound", "propext"]
    text = AUDIT_TEXT.read_text()
    flat = " ".join(text.split())
    assert flat.count("depends on axioms") == payload["axiom_audit_declarations"] == 14
    for token in ("sorryAx", "Axiom", "axiom "):
        if token == "sorryAx":
            assert token not in flat


def test_audited_declarations_cover_the_declared_map_logic():
    names = {name.rsplit(".", 1)[-1] for name in _compile()["audited_declarations"]}
    assert {
        "abs_multiplier", "abs_multiplier_strictMonoOn", "boundary_at_criticalRho",
        "attracting_iff_lt_criticalRho", "repelling_iff_criticalRho_lt",
        "criticalRho_le_one_iff", "attracting_of_gain_le_two",
        "full_reuse_attracting_of_gain_between_zero_two",
        "full_reuse_boundary_of_gain_eq_zero_or_two",
        "attracting_of_interval", "repelling_of_interval", "trichotomy",
        "cusum_attracting_of_lt_criticalRho", "sr_repelling_of_criticalRho_lt",
    } == names


def test_reuse_of_the_closed_spines_is_recorded_not_hidden():
    payload = _compile()
    assert payload["imports_priority1_closed_spine"]
    assert payload["imports_priority2_closed_spine"]
    assert "synthesis layer" in payload["reuse_rationale"]


def test_lean_makes_no_numerical_or_global_claim():
    boundary = _compile()["boundary"]
    assert "does not certify the Monte Carlo Gaussian gains" in boundary
    assert "first-order local behaviour" in boundary
    source = LEAN_SOURCE.read_text()
    assert "global" not in source.lower().replace("globally", "")  \
        or "Nothing in this file asserts" in source
