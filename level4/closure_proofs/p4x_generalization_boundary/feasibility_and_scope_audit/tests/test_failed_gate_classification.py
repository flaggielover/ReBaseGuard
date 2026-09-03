"""Every failed-gate classification must be recomputable from the P4 cells."""

from __future__ import annotations

import collections

import pytest

CLASSES = {
    "SCIENTIFIC_THEOREM_GAP", "NUMERICAL_CORRESPONDENCE_GAP",
    "CERTIFICATION_GAP", "ASSUMPTION_BOUNDARY_GAP",
    "NEGATIVE_TEST_DESIGN_GAP", "GOVERNANCE_ONLY", "OTHER",
}


def _cells(corr):
    return corr["monte_carlo"]["cells"]


def test_every_failed_gate_carries_a_charter_classification(results):
    assert len(results["failed_gates"]) == 3
    for gate in results["failed_gates"]:
        assert gate["classification"] in CLASSES
        assert gate["scientific_theorem_gap"] is False


def test_no_failed_gate_is_a_scientific_theorem_gap(results):
    assert results["gate_classification_counts"]["SCIENTIFIC_THEOREM_GAP"] == 0
    assert results["verdicts"]["P4X_THEOREM_STATUS"].startswith(
        "PROVED_AND_INDEPENDENTLY_ADJUDICATED"
    )


def test_theorem_supported_pass_count_is_recomputable(p4_correspondence):
    supported = [c for c in _cells(p4_correspondence)
                 if c["family_class"] == "THEOREM-SUPPORTED"]
    counts = collections.Counter(c["verdict"] for c in supported)
    assert counts["PASS"] == 86
    assert counts["FAIL"] == 10
    assert len(supported) == 96


def test_failing_supported_cells_are_only_t1p5_and_one_skewnormal(
        p4_correspondence, results):
    failing = [c for c in _cells(p4_correspondence)
               if c["family_class"] == "THEOREM-SUPPORTED" and c["verdict"] != "PASS"]
    by_family = collections.Counter(c["family"] for c in failing)
    assert by_family == {"t1p5": 9, "skewnormal4": 1}
    audit = results["theorem_supported_cell_audit"]["classification"]
    assert audit["GATE_OVER_SPECIFICATION"] == 9
    assert audit["NUMERICAL_ERROR"] == 1
    assert audit["TRUE_THEOREM_CONTRADICTION"] == 0
    assert sum(audit.values()) == 10


def test_every_t1p5_failure_is_statistically_consistent(p4_correspondence, p4_protocol):
    """The nine t1p5 failures fail on accuracy only, never on consistency."""
    limit = p4_protocol["gates"]["correspondence_z_limit"]
    failing = [c for c in _cells(p4_correspondence)
               if c["family_class"] == "THEOREM-SUPPORTED"
               and c["verdict"] != "PASS" and c["family"] == "t1p5"]
    assert len(failing) == 9
    for c in failing:
        assert c["correspondence"]["z"] <= limit, c


def test_t1p5_route_b_precision_cannot_meet_the_accuracy_gate(
        p4_correspondence, p4_protocol):
    """A 3% accuracy gate asked of an estimator whose own SE reaches 23%."""
    accuracy = p4_protocol["gates"]["correspondence_relative_limit"]
    failing = [c for c in _cells(p4_correspondence)
               if c["family_class"] == "THEOREM-SUPPORTED"
               and c["verdict"] != "PASS" and c["family"] == "t1p5"]
    rel_ses = [c["route_b"]["se"] / abs(c["route_b"]["mean"]) for c in failing]
    assert max(rel_ses) > 0.23
    # Every one of the nine has a Route-B standard error at least half the
    # accuracy the gate demands, so the gate is not reachable by that estimator.
    assert min(rel_ses) >= accuracy / 2


def test_the_single_inconsistent_cell_is_the_skewnormal_sr_m2_cell(
        p4_correspondence, p4_protocol):
    limit = p4_protocol["gates"]["correspondence_z_limit"]
    inconsistent = [c for c in _cells(p4_correspondence)
                    if c["family_class"] == "THEOREM-SUPPORTED"
                    and c["correspondence"]["z"] > limit]
    assert len(inconsistent) == 1
    cell = inconsistent[0]
    assert (cell["family"], cell["detector"], cell["m"], cell["layer"]) == (
        "skewnormal4", "sr@520.886", 2, "frozen")


def test_outside_assumption_split_is_uniform_pass_cauchy_fail(p4_correspondence, results):
    outside = [c for c in _cells(p4_correspondence)
               if c["family_class"] == "OUTSIDE-ASSUMPTIONS"]
    counts = collections.Counter((c["family"], c["verdict"]) for c in outside)
    assert counts[("uniform", "COUNTEREXAMPLE-CONFIRMED")] == 16
    assert counts[("cauchy", "COUNTEREXAMPLE-NOT-DEMONSTRATED")] == 16
    assert len(counts) == 2
    audit = results["outside_assumption_audit"]
    assert audit["uniform"]["confirmed"] == 16
    assert audit["cauchy"]["confirmed"] == 0


def test_cauchy_cells_do_not_converge(p4_correspondence):
    """The gate's z >= 10 signature is unreachable when nothing converges."""
    cauchy = [c for c in _cells(p4_correspondence) if c["family"] == "cauchy"]
    assert len(cauchy) == 16
    for c in cauchy:
        a, b = c["route_a"], c["route_b"]
        # at least one route has a standard error comparable to its own estimate
        ratio = max(a["se"] / max(abs(a["mean"]), 1e-12),
                    b["se"] / max(abs(b["mean"]), 1e-12))
        assert ratio > 0.1, c
        assert c["correspondence"]["z"] < 10.0, c


def test_gaussian_consistency_gate_statistic_vs_correct_statistic(p4_closure):
    """The gate fails; the correctly specified two-sample statistic passes."""
    assert p4_closure["gaussian_consistency_worst_z"] > 4.0
    assert p4_closure["gaussian_consistency_worst_z_combined_error"] < 4.0
    for row in p4_closure["gaussian_consistency_rows"]:
        assert row["closed_se"] is not None
        assert row["z_combined_error_reported_statistic"] <= row[
            "z_single_error_gate_statistic"]


def test_gaussian_discrepancy_is_confined_to_sr_and_one_signed(p4_closure):
    rows = p4_closure["gaussian_consistency_rows"]
    sr = [r for r in rows if r["detector"] == "sr@520.886"]
    cusum = [r for r in rows if r["detector"] == "cusum@5"]
    assert len(sr) == 4 and len(cusum) == 4
    assert all(r["signed_relative_difference"] < 0 for r in rows)
    assert max(abs(r["signed_relative_difference"]) for r in cusum) < 0.005
    assert all(0.009 < abs(r["signed_relative_difference"]) < 0.012 for r in sr)


def test_gaussian_mismatch_is_not_mathematical_or_convention_related(results):
    g = results["gaussian_consistency_audit"]
    assert g["mismatch_is_mathematical"] is False
    assert g["mismatch_is_convention_related"] is False
    assert g["mismatch_is_interpolation_related"] is False
    assert g["repairable_without_changing_scientific_meaning"] is True


def test_audit_performed_no_new_heavy_computation(results):
    assert results["gaussian_consistency_audit"]["new_computation_performed"] is False


@pytest.mark.parametrize("gate_name", [
    "all_theorem_supported_cells_pass",
    "all_outside_assumption_cells_demonstrate_failure",
    "gaussian_consistency_with_closed_core",
])
def test_each_named_failed_gate_is_actually_false_in_p4(p4_closure, gate_name):
    assert p4_closure["gates"][gate_name] is False
