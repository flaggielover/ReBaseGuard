from __future__ import annotations

import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]


def load(relative: str):
    return json.loads((BASE / relative).read_text())


def test_novelty_campaign_closed_before_v2():
    decision = json.loads((ROOT / "level4/closure_proofs/novelty_verification/results/decision.json").read_text())
    assert decision["decision"] == "NOVELTY-VERIFICATION-CLOSED"


def test_historical_stage_e_remains_partial_zero_of_three():
    decision = json.loads((ROOT / "level4/stage_e/results/stage_e_decision.json").read_text())
    assert decision["decision"] == "STAGE-E-PARTIAL"
    assert decision["n_tasks_supporting_H_E5"] == 0


def test_protocol_hash_and_protected_history():
    p = subprocess.run(
        [str(ROOT / "level4/.venv/bin/python"), str(BASE / "src/integrity.py")],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert p.returncode == 0, p.stdout + p.stderr


def test_exactly_three_outcome_blind_primaries():
    selection = load("results/dataset_selection.json")
    assert selection["primary_tasks"] == ["household", "metro", "beijing"]
    assert selection["confirmatory_outcomes_inspected"] is False


def test_backup_rule_cannot_replace_unfavourable_result():
    rule = load("results/dataset_selection.json")["backup_activation_rule"].lower()
    assert "unfavorable" in rule and "may not" in rule


def test_all_projected_endpoint_classes_meet_floor():
    audit = load("results/dataset_audit.json")
    floor = load("results/protocol.json")["power"]["minimum_effective_blocks"]
    for task in ("household", "metro", "beijing"):
        row = audit["tasks"][task]
        assert row["projected_calibration_blocks"] >= floor
        assert row["weekly_blocks"] >= floor
        assert row["event_blocks"] >= floor


def test_protocol_uses_only_p0_p1_p2_for_closure():
    policies = load("results/protocol.json")["policies"]
    assert policies == {"P0_fresh": 0.0, "P1_full_reuse": 1.0, "P2_rebaseguard": 0.029796}


def test_matched_wait_is_the_only_e1_denominator():
    text = (BASE / "METRIC_DEFINITIONS.md").read_text().lower()
    assert "matched-wait denominator" in text
    assert "never a full-cycle denominator" in text


def test_alert_burden_not_false_alarm_rate():
    text = " ".join((BASE / "METRIC_DEFINITIONS.md").read_text().lower().split())
    assert "not a false-alarm rate" in text


def test_no_confirmatory_result_existed_at_protocol_freeze_commit():
    freeze_commit = "c80d5d47c825683a9fe899cb3e4cc45490f2c5bc"
    path = "level4/closure_proofs/external_validation_v2/results/decision.json"
    completed = subprocess.run(["git", "cat-file", "-e", f"{freeze_commit}:{path}"],
                               cwd=ROOT, capture_output=True)
    assert completed.returncode != 0


def test_no_old_stage_e_pooling():
    assert load("results/dataset_selection.json")["old_stage_e_data_pooled"] is False


def test_claim_boundary_forbids_production_validation():
    text = (BASE / "PROTOCOL.md").read_text().lower()
    assert "never supports" in text and "production validated" in text
