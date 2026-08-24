from __future__ import annotations

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))

from config import DATASETS, POLICIES, PRIMARY_TASKS, PROTOCOL, protocol_digest
from integrity import verify


def load(name: str) -> dict:
    return json.loads((BASE / name).read_text())


def test_protocol_hash_is_frozen():
    assert protocol_digest() == load("results/protocol_hash.json")["protocol_sha256"]


def test_candidate_pool_has_twelve_pre_outcome_entries():
    audit = load("results/dataset_discovery.json")
    assert len(audit["candidates"]) == 12
    assert audit["forbidden_policy_outcomes_inspected"] is False


def test_two_primaries_are_frozen_without_backup():
    selected = load("results/dataset_selection.json")
    assert selected["primaries"] == ["metropt", "retail"]
    assert selected["backup"] is None
    assert selected["selection_frozen_before_confirmatory_outcomes"] is True


def test_selected_sources_are_new_and_licensed():
    assert PRIMARY_TASKS == ("metropt", "retail")
    assert {row["uci_id"] for row in DATASETS["datasets"]} == {791, 502}
    assert all(row["license"] == "CC BY 4.0" for row in DATASETS["datasets"])
    assert all(len(row["archive_sha256"]) == 64 for row in DATASETS["datasets"])


def test_selected_domains_are_independent_of_v2_household():
    discovery = load("results/dataset_discovery.json")
    domains = {row["domain"] for row in discovery["candidates"]
               if row["decision"].startswith("PRIMARY")}
    assert domains == {"industrial compressor sensors", "retail operations"}
    assert "household energy" not in domains


def test_power_floor_is_forty():
    assert PROTOCOL["power"]["minimum_effective_blocks"] == 40


def test_calibration_allocation_accounts_for_fresh_block():
    assert PROTOCOL["splits"] == {"train": 0.2, "calibration": 0.3, "evaluation": 0.5}
    m = PROTOCOL["detector"]["m"]
    metro_cycles = 4968 // (PROTOCOL["tasks"]["metropt"]["target_arl"] + m) - 3
    retail_cycles = 5265 // (PROTOCOL["tasks"]["retail"]["target_arl"] + m) - 3
    assert metro_cycles // PROTOCOL["tasks"]["metropt"]["calibration_cycle_block"] >= 40
    assert retail_cycles // PROTOCOL["tasks"]["retail"]["calibration_cycle_block"] >= 40


def test_event_floor_yields_forty_blocks():
    assert PROTOCOL["events"]["count"] == 240
    assert PROTOCOL["events"]["count"] // PROTOCOL["bootstrap"]["event_block"] == 40


def test_projected_natural_blocks_meet_floor():
    assert 8281 // PROTOCOL["tasks"]["metropt"]["natural_block_observations"] >= 40
    assert 8775 // PROTOCOL["tasks"]["retail"]["natural_block_observations"] >= 40


def test_policies_are_authoritative_and_outcome_blind():
    assert POLICIES == {"P0_fresh": 0.0, "P1_full_reuse": 1.0,
                        "P2_rebaseguard": 0.029796}


def test_intervention_family_is_frozen():
    assert [row["id"] for row in PROTOCOL["interventions"]] == [
        "STEP_0.5", "STEP_1.0", "STEP_2.0", "GRADUAL_1.0", "RECURRING_1.0"
    ]


def test_hypothesis_thresholds_are_frozen():
    h = PROTOCOL["hypotheses"]
    assert h["effect_ratio_floor"] == 1.1
    assert h["primary_noninferiority_epsilon"] == 0.1
    assert h["simultaneous_one_sided_confidence"] == 0.99


def test_cross_campaign_aggregation_is_frozen():
    a = PROTOCOL["aggregation"]
    assert a["existing_success"] == "V2 Household"
    assert a["minimum_cross_campaign_successes"] == 2
    assert a["no_statistical_pooling"] is True


def test_no_confirmatory_v3_outcome_exists_at_freeze():
    assert not list((BASE / "results").glob("task_*_confirmatory.json"))
    assert load("results/protocol_hash.json")["confirmatory_outcomes_existed_when_frozen"] is False


def test_historical_trees_are_intact():
    assert verify() == []


def test_v2_partial_and_household_only_are_preserved():
    v2 = load("../external_validation_v2/results/decision.json")
    assert v2["decision"] == "EXTERNAL-VALIDATION-V2-PARTIAL"
    assert v2["task_support"] == {"beijing": False, "household": True, "metro": False}
