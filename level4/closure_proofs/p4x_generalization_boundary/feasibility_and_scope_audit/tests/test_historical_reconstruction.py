"""The audit's reconstruction of historical P4 must match the frozen artifacts.

Every assertion here reads the P4 tree, never a summary of it.
"""

from __future__ import annotations


def test_p4_verdict_is_partial(p4_closure, results):
    assert p4_closure["verdict"] == "PARTIAL"
    assert results["historical_p4"]["verdict"] == "PARTIAL"
    assert results["verdicts"]["P4_ORIGINAL_VERDICT"] == "PARTIAL"


def test_p4_all_required_gates_do_not_pass(p4_closure):
    assert p4_closure["all_required_gates_pass"] is False


def test_reconstructed_failed_gate_set_is_exact(p4_closure, results):
    actual = sorted(k for k, v in p4_closure["gates"].items() if not v)
    assert actual == sorted(results["verdicts"]["P4_ORIGINAL_FAILED_GATES"])
    assert len(actual) == 3


def test_reconstructed_cell_counts_match(p4_closure, results):
    hist = results["historical_p4"]
    assert p4_closure["theorem_supported_cells"] == hist["theorem_supported_cells"]
    assert p4_closure["outside_assumption_cells"] == hist["outside_assumption_cells"]
    assert sorted(p4_closure["theorem_supported_families"]) == sorted(
        hist["theorem_supported_families"]
    )


def test_reconstructed_worst_statistics_match(p4_closure, results):
    audit = results["theorem_supported_cell_audit"]
    assert audit["worst_relative_discrepancy"] == p4_closure[
        "worst_theorem_supported_relative_discrepancy"]
    assert audit["worst_z"] == p4_closure["worst_theorem_supported_z"]


def test_reconstructed_gaussian_statistics_match(p4_closure, results):
    g = results["gaussian_consistency_audit"]
    assert g["worst_z_gate_statistic"] == p4_closure["gaussian_consistency_worst_z"]
    assert g["worst_z_combined_error"] == p4_closure[
        "gaussian_consistency_worst_z_combined_error"]


def test_reconstructed_gate_thresholds_match_the_frozen_protocol(p4_protocol):
    gates = p4_protocol["gates"]
    assert gates["correspondence_relative_limit"] == 0.03
    assert gates["correspondence_z_limit"] == 4.0
    assert gates["counterexample_min_relative"] == 0.5
    assert gates["counterexample_min_z"] == 10.0
    assert p4_protocol["frozen_reference_values"]["consistency_z_limit"] == 4.0


def test_reconstructed_scope_matches_the_frozen_protocol(p4_protocol, results):
    hist = results["historical_p4"]
    assert p4_protocol["m_grid"] == hist["windows_measured"]
    supported = sorted(
        name for name, spec in p4_protocol["families"].items()
        if spec["class"] == "THEOREM-SUPPORTED"
    )
    outside = sorted(
        name for name, spec in p4_protocol["families"].items()
        if spec["class"] == "OUTSIDE-ASSUMPTIONS"
    )
    assert supported == sorted(hist["theorem_supported_families"])
    assert outside == sorted(hist["outside_assumption_families"])


def test_theorem_document_states_both_identities(p4):
    text = (p4 / "THEOREM.md").read_text()
    assert "g_m'(0) = -Gamma_{D,m,f}" in text
    assert "F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f})" in text
    assert "psi(z) = -f'(z)/f(z)" in text


def test_theorem_scope_disclaimers_survive(p4):
    text = (p4 / "THEOREM.md").read_text()
    for phrase in ("**not** distribution free", "detector universal",
                   "not valid for moving support"):
        assert phrase in text


def test_frozen_gain_is_not_interval_certified(p4_closure, results):
    assert p4_closure["negative_claims_asserted_false"][
        "frozen_infinite_horizon_gains_interval_certified"] is False
    assert results["historical_p4"]["frozen_gain_interval_certified"] is False


def test_elapsed_seconds_anchor_matches_the_artifact(p4_correspondence, results):
    assert results["historical_p4"]["elapsed_seconds_full_grid"] == (
        p4_correspondence["elapsed_seconds"]
    )
