"""Gates on the produced artifacts.  These fail loudly if the campaign is
re-run and its conclusion changes."""

from __future__ import annotations

import pytest


def test_route_q_identity_holds_for_every_supported_family(correspondence):
    q = correspondence["route_q"]
    assert q["all_pass"]
    assert len(q["rows"]) >= 24
    for row in q["rows"]:
        assert row["relative_discrepancy"] < 1e-6, row


def test_route_q_uniform_counterexample_is_recorded_as_a_failure(correspondence):
    uc = correspondence["route_q"]["uniform_counterexample"]
    assert uc["identity_holds"] is False
    assert uc["gamma_score_route"] == 0.0
    assert uc["negative_map_derivative_exact"] > 1.0


def test_neutrality_control_passes_for_every_family(correspondence):
    rows = correspondence["route_n"]["rows"]
    assert correspondence["route_n"]["all_pass"]
    assert len(rows) >= 40
    for row in rows:
        assert abs(row["gamma"] - 1.0) < 0.05, row


def test_the_recorded_correspondence_outcome_is_exactly_as_reported(
        correspondence, protocol):
    """The campaign did NOT pass its own correspondence gate.  This test pins
    the exact shape of that outcome so it cannot drift silently.

    Ten of ninety-six theorem-supported cells did not pass.  Nine are the single
    infinite-variance family `t1p5`, all statistically consistent; one is
    `sr@520.886 / skewnormal4 / m=2`.  See `CLOSURE_REPORT.md` section 1.
    """
    limits = protocol["gates"]
    cells = [c for c in correspondence["monte_carlo"]["cells"]
             if c["family_class"] == "THEOREM-SUPPORTED"]
    assert len(cells) == 96
    failing = [c for c in cells if c["verdict"] != "PASS"]
    assert len(failing) == 10

    for cell in cells:
        if cell["verdict"] != "PASS":
            continue
        assert cell["correspondence"]["relative_discrepancy"] <= \
            limits["correspondence_relative_limit"]
        assert cell["correspondence"]["z"] <= limits["correspondence_z_limit"]

    inconsistent = [c for c in cells
                    if c["correspondence"]["z"] > limits["correspondence_z_limit"]]
    assert len(inconsistent) == 1
    only = inconsistent[0]
    assert (only["layer"], only["detector"], only["family"], only["m"]) == \
        ("frozen", "sr@520.886", "skewnormal4", 2)

    precision_limited = [c for c in failing if c is not only]
    assert len(precision_limited) == 9
    assert {c["family"] for c in precision_limited} == {"t1p5"}
    for cell in precision_limited:
        assert cell["correspondence"]["z"] <= limits["correspondence_z_limit"]
        assert cell["route_b"]["se"] / abs(cell["route_b"]["mean"]) > 0.01


def test_every_finite_variance_family_passes_at_both_frozen_operating_points(
        correspondence, protocol):
    """The positive statement the campaign is entitled to make: at the frozen
    operating points, every finite-variance family passes the frozen gate at
    every window length, and under the frozen CUSUM they agree to under 1%."""
    limits = protocol["gates"]
    checked = cusum_checked = 0
    for cell in correspondence["monte_carlo"]["cells"]:
        if cell["layer"] != "frozen" or cell["family_class"] != "THEOREM-SUPPORTED":
            continue
        if cell["family"] in {"t1p5", "skewnormal4"}:
            continue  # infinite variance / the one flagged column
        assert cell["verdict"] == "PASS", cell["correspondence"]
        assert cell["correspondence"]["relative_discrepancy"] <= \
            limits["correspondence_relative_limit"]
        assert cell["correspondence"]["z"] <= limits["correspondence_z_limit"]
        checked += 1
        if cell["detector_kind"] == "cusum":
            assert cell["correspondence"]["relative_discrepancy"] <= 0.01
            cusum_checked += 1
    assert checked == 32
    assert cusum_checked == 16


def test_the_two_outside_assumption_families_fail_in_different_ways(
        correspondence, protocol):
    """Uniform produces a deterministic defect and meets the preregistered
    counterexample gate at every cell.  Cauchy produces a non-convergence, which
    is the pathology PROOF.md section 10 proves but not the one the gate was
    written to detect, so its cells are recorded as not meeting it."""
    limits = protocol["gates"]
    uniform = [c for c in correspondence["monte_carlo"]["cells"]
               if c["family"] == "uniform"]
    cauchy = [c for c in correspondence["monte_carlo"]["cells"]
              if c["family"] == "cauchy"]
    assert len(uniform) == 16 and len(cauchy) == 16

    for cell in uniform:
        assert cell["verdict"] == "COUNTEREXAMPLE-CONFIRMED"
        assert cell["correspondence"]["relative_discrepancy"] >= \
            limits["counterexample_min_relative"]
        assert cell["correspondence"]["z"] >= limits["counterexample_min_z"]

    for cell in cauchy:
        assert cell["verdict"] == "COUNTEREXAMPLE-NOT-DEMONSTRATED"
        window = cell["mean_window_at_zero"]
        assert window["se"] > 0.2 * abs(window["mean"])


def test_uniform_score_side_is_exactly_zero_under_both_frozen_detectors(
        correspondence):
    cells = [c for c in correspondence["monte_carlo"]["cells"]
             if c["family"] == "uniform"]
    assert cells
    for cell in cells:
        assert cell["route_a"]["mean"] == 0.0
        assert abs(cell["route_b"]["mean"]) > 1.0


def test_no_path_failed_to_stop(correspondence):
    for cell in correspondence["monte_carlo"]["cells"]:
        assert cell["unstopped_paths"] == 0, cell["family"]


def test_both_frozen_operating_points_are_covered(correspondence):
    detectors = {c["detector"] for c in correspondence["monte_carlo"]["cells"]
                 if c["layer"] == "frozen"}
    assert detectors == {"cusum@5", "sr@520.886"}


def test_gaussian_consistency_with_the_closed_core_is_recorded_both_ways(
        correspondence, protocol, closure):
    """The coded gate divides by Priority 4's error alone and so fails on the
    four SR cells.  The correctly specified combined-error statistic does not.
    Both are pinned here; the gate was not edited after the data were seen."""
    reference = protocol["frozen_reference_values"]
    single = []
    for cell in correspondence["monte_carlo"]["cells"]:
        if cell["layer"] != "frozen" or cell["family"] != "gaussian":
            continue
        key = "cusum_gaussian" if cell["detector_kind"] == "cusum" else "sr_gaussian"
        frozen = reference[key][str(cell["m"])]
        single.append(abs(cell["route_a"]["mean"] - frozen) / cell["route_a"]["se"])
    assert len(single) == 8
    assert sum(1 for z in single if z > reference["consistency_z_limit"]) == 4

    rows = closure["gaussian_consistency_rows"]
    assert len(rows) == 8
    assert all(r["closed_se"] is not None for r in rows)
    assert max(r["z_combined_error_reported_statistic"] for r in rows) < 3.0

    sr = [r for r in rows if r["detector"].startswith("sr")]
    assert len(sr) == 4
    assert all(-0.015 < r["signed_relative_difference"] < -0.005 for r in sr)


def test_finite_difference_ladder_shows_the_expected_second_order_law(
        correspondence):
    for row in correspondence["fd_ladder"]["rows"]:
        steps = list(row["per_step"].values())
        coarse, fine = steps[0]["gamma"]["mean"], steps[1]["gamma"]["mean"]
        rich = row["richardson"]["mean"]
        # the fine step must lie between the coarse step and the extrapolation
        assert min(coarse, rich) - 1e-9 <= fine <= max(coarse, rich) + 1e-9


def test_stability_map_never_classifies_an_unsupported_cell(stability_map):
    for row in stability_map["rows"]:
        if row["family_class"] != "THEOREM-SUPPORTED":
            assert row["stability_status"] == "NOT-CLASSIFIED-OUTSIDE-ASSUMPTIONS"
            assert row["cells"] == []


def test_asymmetric_family_is_refused_a_classification_at_the_origin(
        stability_map):
    rows = [r for r in stability_map["rows"] if r["family"].startswith("skewnormal")]
    assert rows
    assert all(r["stability_status"] == "FIXED-POINT-NOT-AT-ORIGIN" for r in rows)
    assert all(not r["origin_is_fixed_point"] for r in rows)
    assert all(r["cells"] == [] for r in rows)


def test_symmetric_families_do_place_the_fixed_point_at_the_origin(stability_map):
    """Theorem G4 proves E_0[A_m] = 0 for these; the numeric check only has to
    fail to falsify it."""
    rows = [r for r in stability_map["rows"]
            if r["family"] in {"gaussian", "laplace", "logistic", "t3", "t1p5"}]
    assert rows
    assert all(r["origin_is_fixed_point"] for r in rows)
    assert all(r["stability_status"] == "CLASSIFIED" for r in rows)


def test_the_two_fixed_point_populations_are_separated_by_orders_of_magnitude(
        stability_map):
    """The falsification threshold is only meaningful if the symmetric and
    asymmetric cells are nowhere near each other."""
    symmetric = [r["mean_window_at_zero_z"] for r in stability_map["rows"]
                 if r["family"] in {"gaussian", "laplace", "logistic", "t3"}]
    skew = [r["mean_window_at_zero_z"] for r in stability_map["rows"]
            if r["family"].startswith("skewnormal")]
    assert symmetric and skew
    assert max(symmetric) < 6.0
    assert min(skew) > 50.0 * max(max(symmetric), 1.0)


def test_every_classified_gain_is_labelled_empirical(stability_map):
    for row in stability_map["rows"]:
        assert row["gamma_evidence_class"] == "EMPIRICAL_ONLY"


def test_certificate_covers_every_required_object(certificate):
    assert certificate["all_checks_pass"]
    assert certificate["missing_certificates"] == []
    assert certificate["failed_checks"] == []
    sections = certificate["sections"]
    assert sections["general_score_witness"]["not_a_location_family"] is True
    exact = sections["general_score_witness"]["exact"]
    assert exact["gain"] == "5/2"
    assert exact["expected_short_correction"] == "-1/10"
    assert exact["gaussian_form_gain"] == "7/2"
    assert sections["uniform_counterexample"]["identity_defect"] == "2/1"


def test_closure_decision_is_internally_consistent(closure):
    assert closure["verdict"] in {"CLOSED", "PARTIAL"}
    if closure["verdict"] == "CLOSED":
        assert all(closure["gates"].values())
        assert not any(closure["negative_claims_asserted_false"].values())
    assert closure["negative_claims_asserted_false"][
        "frozen_infinite_horizon_gains_interval_certified"] is False
    assert closure["negative_claims_asserted_false"]["novelty_verdict_claimed"] is False


def test_at_least_six_theorem_supported_families_were_tested(closure):
    assert len(closure["theorem_supported_families"]) >= 6
    assert {"gaussian", "laplace", "logistic", "t3", "t1p5"} <= set(
        closure["theorem_supported_families"]
    )


def test_independent_adjudication_preserves_the_partial_verdict(campaign,
                                                                 closure):
    import json

    audit = json.loads(
        (campaign / "results" / "independent_adjudication.json").read_text()
    )
    assert audit["verdict"] == closure["verdict"] == "PARTIAL"
    assert audit["skewnormal_sr_frozen"]["resolution"].startswith(
        "Finite-step bias"
    )
    assert audit["priority2_sr_mismatch"]["resolution"].startswith(
        "The fresh frozen-P2 implementation replay agrees"
    )
    assert audit["protected_tree_integrity"]["all_byte_identical_to_head"]
    assert audit["novelty"] == "NOVELTY-NOT-ADJUDICATED"
