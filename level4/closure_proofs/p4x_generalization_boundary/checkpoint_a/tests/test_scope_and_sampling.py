"""Production scope, sample-size determinism, and the absence of any
pass/fail-dependent sampling rule."""

from __future__ import annotations

import pytest

R_STAR = 0.010823


def test_production_scope_matches_the_frozen_p4_grid_exactly(
        manifest, p4_correspondence, p4_protocol):
    cells = [c for c in p4_correspondence["monte_carlo"]["cells"]
             if c["family_class"] == "THEOREM-SUPPORTED"]
    outside = [c for c in p4_correspondence["monte_carlo"]["cells"]
               if c["family_class"] == "OUTSIDE-ASSUMPTIONS"]
    s = manifest["production_scope"]
    assert s["theorem_supported_cells"] == len(cells) == 96
    assert s["outside_assumption_cells"] == len(outside) == 32
    assert s["configurations"] == 24
    assert s["m_grid"] == p4_protocol["m_grid"] == [1, 2, 3, 5]
    assert s["theorem_supported_families"] == sorted(
        {c["family"] for c in cells})
    assert s["outside_assumption_families"] == sorted(
        {c["family"] for c in outside})
    assert s["detectors"] == sorted({c["detector"] for c in cells})
    assert len(s["detectors"]) == 4


def test_scope_may_not_be_broadened_or_narrowed(manifest, doc):
    s = manifest["production_scope"]
    assert s["broadening_permitted"] is False
    assert s["narrowing_after_results_permitted"] is False
    assert "Not broadened" in doc


def test_route_counts_match_the_frozen_artifact(manifest, p4_correspondence):
    s = manifest["production_scope"]
    assert s["route_q_rows"] == len(p4_correspondence["route_q"]["rows"]) == 24
    assert s["route_n_rows"] == len(p4_correspondence["route_n"]["rows"]) == 72
    assert len(s["routes"]) == 4


def test_production_plan_covers_every_cell_and_route(manifest):
    plan = manifest["production_plan"]
    assert len(plan) == 96
    seen = {(r["layer"], r["detector"], r["family"], r["m"]) for r in plan}
    assert len(seen) == 96
    for row in plan:
        for route in ("route_a", "route_b"):
            assert route in row, row["config"]


def test_sample_size_rule_is_deterministic_and_reproducible(manifest):
    """N = N_ref * (relSE_ref / r*)^(1/kappa), recomputed from stored inputs."""
    for row in manifest["production_plan"]:
        for route in ("route_a", "route_b"):
            r = row[route]
            rel, n_ref = r["reference_relative_se"], r["reference_paths"]
            for stage, kappa_key in (("stage1", "kappa_stage1"),
                                     ("worst_case", "kappa_topup")):
                k = r[kappa_key]
                expected = (rel / R_STAR) ** (1.0 / k) if rel > R_STAR else 1.0
                assert r[f"{stage}_paths"] == pytest.approx(
                    n_ref * expected, rel=1e-9), (row["config"], route, stage)


def test_cpu_projections_follow_from_paths_and_measured_cost(manifest):
    for row in manifest["production_plan"]:
        for route in ("route_a", "route_b"):
            r = row[route]
            sec = r["seconds_per_1e6_paths"]
            for stage in ("stage1", "worst_case"):
                assert r[f"{stage}_cpu_hours"] == pytest.approx(
                    r[f"{stage}_paths"] / 1e6 * sec / 3600.0, rel=1e-9)


def test_no_plan_record_carries_pass_fail_information(manifest):
    """Structural guarantee: the plan cannot encode an outcome."""
    banned = {"verdict", "passed", "failed", "relative_discrepancy", "z",
              "correspondence", "discrepancy", "close_to_passing"}
    for row in manifest["production_plan"]:
        assert not (set(row) & banned), row["config"]
        for route in ("route_a", "route_b"):
            assert not (set(row[route]) & banned), (row["config"], route)


def test_precision_rule_declares_its_forbidden_dependencies(manifest):
    p = manifest["precision_rule"]
    for banned in ("observed pass/fail", "discrepancy sign",
                   "whether a cell is close to passing"):
        assert banned in p["must_not_depend_on"], banned
    t = p["two_stage_design"]
    assert t["trigger_is"] == "the route's own achieved relative standard error"
    joined = " ".join(t["trigger_is_not"])
    assert "discrepancy" in joined
    assert "sign or direction" in joined
    assert "close to passing" in joined
    assert "pass/fail outcome" in joined


def test_two_stage_design_discloses_its_sequential_bias(manifest, doc):
    t = manifest["precision_rule"]["two_stage_design"]
    assert "optional-" in t["disclosed_limitation"]
    assert "O(1/B)" in t["disclosed_limitation"]
    assert "disclosed rather than assumed away" in doc


def test_cost_projections_are_charged_once_per_configuration(manifest):
    per_config = manifest["per_configuration_plan"]
    assert len(per_config) == 24
    for cfg, c in per_config.items():
        assert c["config_stage1_cpu_hours"] == pytest.approx(
            c["route_a_stage1_cpu_hours"] + c["route_b_stage1_cpu_hours"])
        assert c["config_worst_case_cpu_hours"] == pytest.approx(
            c["route_a_worst_case_cpu_hours"]
            + c["route_b_worst_case_cpu_hours"])
        assert c["config_worst_case_cpu_hours"] >= c["config_stage1_cpu_hours"]


def test_totals_are_the_sum_over_configurations(manifest):
    per_config = manifest["per_configuration_plan"].values()
    t = manifest["projected_cpu_hours"]
    assert t["stage1_cpu_hours"] == pytest.approx(
        sum(c["config_stage1_cpu_hours"] for c in per_config))
    assert t["worst_case_cpu_hours"] == pytest.approx(
        sum(c["config_worst_case_cpu_hours"] for c in per_config))


def test_stage1_projection_fits_inside_both_caps(manifest):
    c = manifest["cost_envelope"]
    assert c["projected_stage1_cpu_hours"] <= c["TOTAL_CPU_CAP_HOURS"]
    for cfg in manifest["per_configuration_plan"].values():
        assert cfg["config_stage1_cpu_hours"] <= c[
            "PER_CONFIGURATION_CPU_CAP_HOURS"]


def test_cost_risk_is_preregistered_not_discovered(manifest, doc, doc_flat):
    """The one configuration that can breach its cap must be named in advance."""
    at_risk = manifest["configurations_at_risk_of_per_configuration_cap"]
    assert at_risk == ["frozen/sr@520.886/t1p5"]
    flagged = [cfg for cfg, c in manifest["per_configuration_plan"].items()
               if c["exceeds_per_configuration_cap_in_worst_case"]]
    assert sorted(flagged) == at_risk
    assert "frozen/sr@520.886/t1p5" in doc
    assert "PRECISION_LIMITED" in doc
    assert "pre-registered now and not discovered later" in doc_flat


def test_precision_limited_declaration_precedes_gate_adjudication(doc_flat):
    assert "before its gate is adjudicated" in doc_flat
    assert "may **never** be made after seeing a result" in doc_flat
    assert "P4X cannot be `CLOSED`; the honest outcome is `PARTIAL`" in doc_flat
