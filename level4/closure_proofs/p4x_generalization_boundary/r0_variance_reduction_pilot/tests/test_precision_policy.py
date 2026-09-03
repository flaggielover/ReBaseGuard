"""The precision policy must be deterministic, estimator-based, and blind to
whether any historical cell passed or failed."""

from __future__ import annotations

import math

import pytest

TARGET = 0.03 / (1.96 * math.sqrt(2.0))


def test_target_is_forced_by_the_frozen_accuracy_criterion(policy, p4_protocol):
    p = policy["policy"]
    frozen = p4_protocol["gates"]["correspondence_relative_limit"]
    assert p["frozen_accuracy_criterion"] == frozen == 0.03
    assert p["target_relative_se_per_route"] == pytest.approx(TARGET, rel=1e-12)


def test_frozen_criteria_are_inherited_unchanged(p4_protocol, pilot_dir):
    """The policy derives r* from the 3% criterion; it never replaces it."""
    assert p4_protocol["gates"]["correspondence_relative_limit"] == 0.03
    assert p4_protocol["gates"]["correspondence_z_limit"] == 4.0
    for name in ("PRECISION_POLICY.md", "DRAFT_CHECKPOINT_A.md"):
        text = (pilot_dir / name).read_text()
        assert "inherited unchanged" in text, name


def test_policy_inputs_exclude_pass_fail_information(policy):
    p = policy["policy"]
    for banned in ("whether a historical cell passed or failed",
                   "the observed Route-A minus Route-B discrepancy",
                   "the sign or direction of any disagreement"):
        assert banned in p["explicitly_not_inputs"], banned
    for needed in ("frozen accuracy criterion", "measured tail index",
                   "measured reference relative SE", "measured CPU per path"):
        assert needed in p["inputs"], needed


def test_no_cell_record_carries_a_pass_fail_field(policy):
    """Structural guarantee: the policy's own data cannot encode an outcome."""
    banned = {"verdict", "passed", "failed", "relative_discrepancy", "z",
              "correspondence"}
    for cell in policy["cells"]:
        assert not (set(cell) & banned), cell["config"]
        for route in ("route_a", "route_b"):
            assert not (set(cell[route]) & banned), (cell["config"], route)


def test_required_sample_size_rule_is_reproducible(policy):
    """N = N_ref * (relSE_ref / r*)^(1/kappa), recomputed from stored inputs."""
    target = policy["policy"]["target_relative_se_per_route"]
    for cell in policy["cells"]:
        for route in ("route_a", "route_b"):
            for tier in ("median", "conservative", "worst_case"):
                t = cell[route][tier]
                rel, k = t["reference_relative_se"], t["kappa"]
                expected = (rel / target) ** (1.0 / k) if rel > target else 1.0
                assert t["path_multiplier"] == pytest.approx(expected, rel=1e-9)
                assert t["required_paths"] == pytest.approx(
                    t["reference_paths"] * expected, rel=1e-9)


def test_kappa_follows_the_measured_tail_index(policy):
    for cell in policy["cells"]:
        for route in ("route_a", "route_b"):
            alpha = cell[route]["alpha"]
            assert cell[route]["median"]["kappa"] == 0.5
            assert cell[route]["conservative"]["kappa"] == 0.5
            worst = cell[route]["worst_case"]["kappa"]
            expected = 0.5 if alpha >= 2.0 else 1.0 - 1.0 / alpha
            assert worst == pytest.approx(expected, rel=1e-12)


def test_t1p5_is_the_only_infinite_variance_family(policy):
    below, at_or_above = set(), set()
    for cfg, a in policy["measured_alpha"].items():
        family = cfg.split("/")[-1]
        for route in ("route_a", "route_b"):
            (below if a[route] < 2.0 else at_or_above).add(family)
    assert below == {"t1p5"}
    assert "t1p5" not in at_or_above


def test_measured_alpha_matches_the_model_for_t1p5(policy):
    """Student-t with nu = 1.5 has tail index exactly 1.5."""
    for cfg, a in policy["measured_alpha"].items():
        if cfg.endswith("/t1p5"):
            for route in ("route_a", "route_b"):
                assert 1.35 < a[route] < 1.75, (cfg, route, a[route])


def test_cost_tiers_are_ordered(policy):
    t = policy["totals_cpu_hours"]
    assert t["median"] <= t["conservative"] <= t["worst_case"]
    assert t["median"] > 0


def test_tier_definitions_are_recorded(policy):
    for tier in ("median", "conservative", "worst_case"):
        assert policy["tier_definitions"][tier]


def test_precision_limited_declaration_uses_projected_cost_only(policy):
    p = policy["policy"]
    assert "projected cost alone" in p["arbitration_clause"]
    assert "before the production estimate exists" in p["arbitration_clause"]
    for row in policy["precision_limited_candidates"]:
        assert row["worst_case_cpu_hours"] > policy[
            "per_configuration_allowance_hours"]


def test_only_the_known_configuration_is_cost_significant(policy):
    """Exactly one (configuration, route) drives the worst-case cost."""
    heavy = [r for r in policy["precision_limited_candidates"]]
    assert len(heavy) == 1
    assert heavy[0]["config"] == "frozen/sr@520.886/t1p5"
    assert heavy[0]["route"] == "route_b"


def test_route_q_arbitration_clause_is_withdrawn(pilot_dir):
    """Route Q is a different detector and cannot arbitrate a frozen cell."""
    report = (pilot_dir / "PILOT_REPORT.md").read_text()
    assert "ROUTE_Q_ADMISSIBLE_ROLE = C" in report
    assert "NOT A:" in report and "NOT B:" in report
    draft = (pilot_dir / "DRAFT_CHECKPOINT_A.md").read_text()
    assert "ROUTE_Q_ADMISSIBLE_ROLE = C" in draft
    assert "withdrawn" in draft


def test_minimum_block_size_is_specified_for_heavy_tailed_cells(pilot_dir):
    text = (pilot_dir / "PRECISION_POLICY.md").read_text()
    assert "MINIMUM_BLOCK_SIZE" in text
    assert "250 000" in text


def test_cut2_needs_no_new_compute_and_cut3_is_negligible(cut23):
    assert cut23["new_simulation_performed"] is False
    assert cut23["cut2"]["classification"] == "NONE"
    assert cut23["cut2"]["requires_new_simulation"] is False
    assert cut23["cut2"]["a3_half"]["already_satisfied"] is True
    assert cut23["cut2"]["first_moment_half"]["signature_reachable"] is False
    assert cut23["cut3"]["classification"] == "NEGLIGIBLE"
    assert cut23["cut3"]["requires_new_simulation"] is False
    assert cut23["cut3"]["all_pass_two_sample"] is True
    assert cut23["cut3"]["worst_z_two_sample"] < cut23["cut3"]["limit"]
    assert cut23["cut3"]["worst_z_historical_gate"] > cut23["cut3"]["limit"]
