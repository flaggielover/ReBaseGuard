"""Every frozen constant must match its source, and r* must be derivable."""

from __future__ import annotations

import math

import pytest

R_STAR = 0.010823


def test_r_star_is_derived_from_the_unchanged_accuracy_criterion(manifest, p4_protocol):
    p = manifest["precision_rule"]
    frozen = p4_protocol["gates"]["correspondence_relative_limit"]
    assert p["frozen_accuracy_criterion"] == frozen == 0.03
    assert p["attainment_z"] == 1.96
    assert p["r_star"] == R_STAR
    exact = 0.03 / (1.96 * math.sqrt(2.0))
    assert p["r_star_exact"] == pytest.approx(exact, rel=1e-12)
    assert abs(R_STAR - exact) < 1e-6
    assert p["r_star_derivation"] == "1.96 * sqrt(2) * r* = 0.03"


def test_frozen_criteria_are_inherited_not_weakened(manifest, p4_protocol, doc_flat):
    assert p4_protocol["gates"]["correspondence_relative_limit"] == 0.03
    assert p4_protocol["gates"]["correspondence_z_limit"] == 4.0
    assert manifest["gates"]["X6_theorem_supported_correspondence"][
        "weakening_permitted"] is False
    assert "0.03" in manifest["gates"]["X6_theorem_supported_correspondence"][
        "criterion"]
    assert "inherited unchanged" in manifest["precision_rule"][
        "frozen_accuracy_source"]
    assert "not weakened" in doc_flat


def test_x6_is_allowed_to_fail(manifest, doc_flat):
    x6 = manifest["gates"]["X6_theorem_supported_correspondence"]
    assert x6["failure_permitted"] is True
    assert "MUST be allowed to FAIL" in x6["note"]
    assert "must be allowed to FAIL" in doc_flat


def test_heavy_tail_policy_matches_the_r0_measurement(manifest, r0_tail_sweep):
    h = manifest["heavy_tail_policy"]
    assert h["only_family_requiring_alpha_below_2"] == "t1p5"
    lo, hi = h["measured_alpha_range_t1p5"]
    measured = [r[route]["tail"]["alpha"]
                for r in r0_tail_sweep["rows"] if r["family"] == "t1p5"
                for route in ("route_a", "route_b")]
    assert lo == pytest.approx(min(measured))
    assert hi == pytest.approx(max(measured))
    assert hi < 2.0
    others = [r[route]["tail"]["alpha"]
              for r in r0_tail_sweep["rows"] if r["family"] != "t1p5"
              for route in ("route_a", "route_b")]
    assert h["measured_alpha_min_other_families"] == pytest.approx(min(others))
    assert min(others) >= 2.0


def test_frozen_alpha_is_the_conservative_floor(manifest):
    h = manifest["heavy_tail_policy"]
    lo, hi = h["measured_alpha_range_t1p5"]
    assert h["frozen_alpha_t1p5_for_planning"] == 1.47
    assert h["frozen_alpha_t1p5_for_planning"] <= lo
    assert h["kappa_t1p5"] == pytest.approx(1.0 - 1.0 / 1.47, rel=1e-12)
    assert 0 < h["kappa_t1p5"] < 0.5


def test_kappa_rule_is_stated_and_applied(manifest):
    assert manifest["heavy_tail_policy"]["kappa_rule"] == (
        "kappa = 0.5 if alpha >= 2 else 1 - 1/alpha")
    for row in manifest["production_plan"]:
        for route in ("route_a", "route_b"):
            r = row[route]
            assert r["kappa_stage1"] == 0.5
            expected = (1.0 - 1.0 / 1.47) if row["heavy_tailed"] else 0.5
            assert r["kappa_topup"] == pytest.approx(expected, rel=1e-12)


def test_minimum_block_sizes_are_frozen(manifest):
    h = manifest["heavy_tail_policy"]
    assert h["minimum_block_paths_heavy_tail"] == 250_000
    assert h["minimum_block_paths_default"] == 20_000
    for row in manifest["production_plan"]:
        expected = 250_000 if row["heavy_tailed"] else 20_000
        assert row["minimum_block_paths"] == expected
        assert row["heavy_tailed"] == (row["family"] == "t1p5")


def test_gaussian_two_sample_statistic_is_exact(manifest, doc):
    g = manifest["gates"]["X11_gaussian_consistency"]
    assert g["statistic"] == (
        "z_combined = |estimate_1 - estimate_2| / sqrt(SE_1^2 + SE_2^2)")
    assert g["limit"] == 4.0
    assert g["cells"] == 8
    assert g["treats_either_estimate_as_exact"] is False
    assert g["is_a_new_preregistered_object"] is True
    assert g["repairs_a_p4_gate"] is False
    assert "gates nothing" in g["historical_single_error_statistic"]
    assert "sqrt(SE_1^2 + SE_2^2)" in doc


def test_cost_caps_are_frozen(manifest, doc):
    c = manifest["cost_envelope"]
    assert c["TOTAL_CPU_CAP_HOURS"] == 60.0
    assert c["PER_CONFIGURATION_CPU_CAP_HOURS"] == 40.0
    assert c["silent_extension_permitted"] is False
    assert c["breach_action"] == "STOP"
    assert "TOTAL_CPU_CAP             = 60 CPU-hours" in doc
    assert "PER_CONFIGURATION_CPU_CAP = 40 CPU-hours" in doc


def test_estimator_plan_is_frozen_with_no_variance_reduction(manifest, p4_protocol):
    e = manifest["estimator_plan"]
    assert e["status"] == "FROZEN"
    assert e["variance_reduction_adopted"] == "NONE"
    assert e["fd_steps"] == p4_protocol["fd_steps"] == [0.05, 0.025]
    assert set(e["rejected_candidates"]) == {
        "reflection_antithetic", "corollary_g2_control_variate",
        "coarse_finite_difference_step", "fine_finite_difference_step"}
    for reason in e["rejected_candidates"].values():
        assert reason


def test_lean_and_arb_are_re_verification_only(manifest, doc):
    la = manifest["lean_and_arb"]
    assert la["new_lean_declarations_permitted"] is False
    assert la["new_arb_objects_permitted"] is False
    assert la["inherited_lean_declarations"] == 19
    assert sorted(la["inherited_lean_axioms"]) == [
        "Classical.choice", "Quot.sound", "propext"]
    assert la["inherited_arb_objects"] == 3
    assert "NEW LEAN DECLARATIONS  = NOT PERMITTED" in doc
    assert "NEW ARB OBJECTS        = NOT PERMITTED" in doc
