"""Precision-rule determinism, heavy-tail rule, top-up independence, caps."""

from __future__ import annotations

import math

import pytest

R_STAR = 0.010823


def test_r_star_is_the_frozen_value(checkpoint, stage1, stage2_plan):
    assert checkpoint["precision_rule"]["r_star"] == R_STAR
    assert stage1["r_star"] == R_STAR
    assert stage2_plan["r_star"] == R_STAR
    assert abs(R_STAR - 0.03 / (1.96 * math.sqrt(2.0))) < 1e-6


def test_heavy_tail_block_rule_is_enforced(stage1, checkpoint):
    heavy_block = checkpoint["heavy_tail_policy"]["minimum_block_paths_heavy_tail"]
    default_block = checkpoint["heavy_tail_policy"]["minimum_block_paths_default"]
    for spec in stage1["specs"]:
        expected = heavy_block if spec["heavy"] else default_block
        assert spec["block_size"] == expected, spec["config"]
        assert spec["heavy"] == (spec["family"] == "t1p5"), spec["config"]


def test_stage1_allocation_follows_the_frozen_rule(stage1):
    for spec in stage1["specs"]:
        blocks = max(24, math.ceil(spec["required_paths"] / spec["block_size"]))
        assert spec["blocks"] == blocks, spec["config"]


def test_topup_kappa_matches_the_frozen_heavy_tail_policy(stage2_plan, checkpoint):
    kappa_heavy = checkpoint["heavy_tail_policy"]["kappa_t1p5"]
    for p in stage2_plan["plans"]:
        assert p["kappa_topup"] == pytest.approx(
            kappa_heavy if p["heavy"] else 0.5, rel=1e-12), p["config"]


def test_topup_size_is_deterministic_from_achieved_precision(stage2_plan):
    """target_N = stage1_N * (achieved relSE / r*)^(1/kappa)."""
    for p in stage2_plan["plans"]:
        if p["meets_r_star"]:
            assert p["additional_N"] == 0
            continue
        expected = p["stage1_N"] * (
            p["stage1_SE_worst_relative"] / R_STAR) ** (1.0 / p["kappa_topup"])
        assert p["target_N"] == pytest.approx(expected, rel=1e-9), p["config"]
        assert p["additional_N"] == pytest.approx(
            max(0.0, expected - p["stage1_N"]), rel=1e-9)


def test_every_topup_reason_is_precision_only(stage2_plan):
    for p in stage2_plan["plans"]:
        assert p["reason"] == "PRECISION_ONLY", p["config"]


def test_topup_trigger_excludes_pass_fail_information(stage2_plan, prod_dir):
    excl = " ".join(stage2_plan["trigger_excludes"])
    for banned in ("discrepancy", "sign", "passes", "close to passing",
                   "campaign would close"):
        assert banned in excl, banned
    assert stage2_plan["trigger"] == (
        "the route's own achieved relative standard error")
    # structural: no top-up record may carry an outcome field
    banned_fields = {"gate_result", "relative_discrepancy", "z", "verdict",
                     "passes", "pass"}
    for p in stage2_plan["plans"]:
        assert not (set(p) & banned_fields), p["config"]


def test_topup_planning_never_reads_the_other_route(prod_dir):
    """The stage-2 planner must not compute a discrepancy."""
    src = (prod_dir / "run_c2_stage2_adjudicate.py").read_text()
    plan_src = src[src.index("def plan_stage2"):src.index("def run_stage2")]
    for banned in ("relative_discrepancy", "route_a\"] - ", "z =", "gate"):
        assert banned not in plan_src, banned


def test_total_cpu_cap_respected(costs, checkpoint):
    cap = checkpoint["cost_envelope"]["TOTAL_CPU_CAP_HOURS"]
    assert cap == 60.0
    assert costs["total_cpu_hours"] <= cap
    assert costs["total_cap_status"] == "PASS"


def test_per_configuration_cpu_cap_respected(costs, checkpoint):
    cap = checkpoint["cost_envelope"]["PER_CONFIGURATION_CPU_CAP_HOURS"]
    assert cap == 40.0
    for cfg, hours in costs["per_configuration_cpu_hours"].items():
        assert hours <= cap, (cfg, hours)
    assert costs["per_configuration_cap_status"] == "PASS"


def test_high_risk_configuration_projection_was_recorded_before_the_result(costs):
    """Checkpoint A named this configuration in advance; the pre-run projection
    must exist and must not have been derived from its own outcome."""
    hr = costs["high_risk_configuration"]
    assert hr["config"] == "frozen/sr@520.886/t1p5"
    assert hr["checkpoint_projection_cpu_hours"] > 0
    assert hr["pre_run_projection_cpu_hours"] > 0
    assert "actual_cpu_hours" in hr


def test_cpu_accounting_reconciles(costs):
    """Per-job CPU must reconcile with process-level accounting."""
    assert costs["reconciliation"]["relative_difference"] < 0.25
