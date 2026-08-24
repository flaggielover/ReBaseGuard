from __future__ import annotations

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))

from config import PRIMARY_TASKS, PROTOCOL, protocol_digest


def load(name: str) -> dict:
    return json.loads((BASE / name).read_text())


def analyses() -> dict[str, dict]:
    return {task: load(f"results/task_{task}_analysis.json") for task in PRIMARY_TASKS}


def confirmatory() -> dict[str, dict]:
    return {task: load(f"results/task_{task}_confirmatory.json") for task in PRIMARY_TASKS}


def test_confirmatory_outputs_use_the_frozen_protocol():
    for row in confirmatory().values():
        assert row["evidence_status"] == "CONFIRMATORY"
        assert row["protocol_hash"] == protocol_digest()


def test_all_policies_consume_one_matched_residual_stream():
    for row in confirmatory().values():
        assert row["matched_streams"] is True
        assert len(row["residual_sha256_float64_le"]) == 64
        assert set(row["natural"]["policies"]) == set(PROTOCOL["policies"])


def test_event_grids_are_unique_and_frozen_length():
    for row in confirmatory().values():
        grid = row["events"]["relative_grid"]
        assert len(grid) == PROTOCOL["events"]["count"] == 240
        assert len(set(grid)) == len(grid)
        assert grid == sorted(grid)


def test_natural_and_event_effective_blocks_meet_forty():
    for row in analyses().values():
        values = [row["E1"]["P1_over_P2"], row["E1"]["P1_over_P0"],
                  row["E2"]["P1_over_P2"], row["E2"]["P1_over_P0"],
                  row["H3_2"]["medium_P1_over_P2"], row["H3_2"]["medium_P1_over_P0"]]
        values.extend(row["H3_3"]["conditions"].values())
        assert min(value["effective_blocks"] for value in values) >= 40
        assert row["reliable"] is True


def test_h3_1_is_supported_on_both_tasks():
    assert all(row["H3_1"]["supported"] for row in analyses().values())


def test_h3_1_requires_effect_size_and_bounds_not_direction_only():
    for row in analyses().values():
        for value in row["E1"].values():
            assert value["ratio"] >= 1.1
            assert value["lower_97_5_one_sided"] > 1


def test_h3_2_is_supported_through_route_a_on_both_tasks():
    for row in analyses().values():
        assert row["H3_2"]["supported"] is True
        assert row["H3_2"]["route_A_alert_burden"] is True


def test_h3_2_alert_burden_requires_both_comparators():
    for row in analyses().values():
        for value in row["E2"].values():
            assert value["ratio"] >= 1.1
            assert value["lower_97_5_one_sided"] > 1


def test_unfavorable_medium_response_route_is_preserved():
    for row in analyses().values():
        assert row["H3_2"]["route_B_medium_response"] is False
        assert row["H3_2"]["medium_P1_over_P2"]["ratio"] < 1
        assert row["H3_2"]["medium_P1_over_P0"]["ratio"] < 1


def test_h3_3_is_simultaneously_supported_on_both_tasks():
    for row in analyses().values():
        assert row["H3_3"]["supported"] is True
        assert all(value["upper99_excess"] <= 0.10
                   for value in row["H3_3"]["conditions"].values())


def test_no_strong_safety_contradiction_is_hidden():
    for row in analyses().values():
        assert row["H3_3"]["strong_safety_contradiction"] is False
        assert not any(value["strong_contradiction"]
                       for value in row["H3_3"]["conditions"].values())


def test_metro_recurring_cap_limitation_is_preserved():
    metro = confirmatory()["metropt"]["events"]["policies"]
    for policy in PROTOCOL["policies"]:
        assert metro[policy]["interventions"]["RECURRING_1.0"]["delay"] == \
               metro[policy]["interventions"]["STEP_1.0"]["delay"]


def test_h3_4_and_task_verdicts_are_mechanical():
    for row in analyses().values():
        assert row["H3_4"]["supported"] is True
        assert row["task_verdict"] == "V3-TASK-SUPPORTED"


def test_scientific_campaign_verdict_is_closed():
    decision = load("results/scientific_decision.json")
    assert decision["scientific_campaign_verdict"] == "EXTERNAL-VALIDATION-V3-CLOSED"
    assert decision["v3_joint_support_count"] == 2


def test_cross_campaign_rule_closes_original_requirement():
    decision = load("results/scientific_decision.json")
    assert decision["existing_cross_campaign_success"] == "V2 Household"
    assert decision["cross_campaign_success_count"] == 3
    assert decision["cross_campaign_required"] == 2
    assert decision["original_external_validation_requirement"] == "CLOSED"


def test_historical_v2_remains_partial_one_of_three():
    decision = load("results/scientific_decision.json")
    assert decision["historical_v2"] == "EXTERNAL-VALIDATION-V2-PARTIAL"
    assert decision["historical_v2_joint_support"] == "1/3"
    v2 = load("../external_validation_v2/results/decision.json")
    assert v2["decision"] == "EXTERNAL-VALIDATION-V2-PARTIAL"
    assert sum(v2["task_support"].values()) == 1


def test_stage_e_and_global_verdict_are_not_recomputed():
    decision = load("results/scientific_decision.json")
    assert decision["historical_stage_e"] == "STAGE-E-PARTIAL"
    assert decision["historical_global_verdict"] == "LEVEL-4-PARTIAL"
    assert decision["global_reaudit_performed"] is False


def test_stop_rule_forbids_v4():
    assert load("results/scientific_decision.json")["stop_rule"] == "NO_V4"


def test_summary_is_the_only_future_figure_source():
    summary = load("results/summary.json")
    assert summary["schema"] == "rebaseguard.external-validation-v3.summary.v1"
    assert set(summary["tasks"]) == {"metropt", "retail"}
    assert summary["decision"]["scientific_campaign_verdict"] == "EXTERNAL-VALIDATION-V3-CLOSED"
