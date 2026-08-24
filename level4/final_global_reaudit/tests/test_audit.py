from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
sys.path.insert(0, str(BASE / "src"))

from audit import EXPECTED_MAP, audit_evidence, build, derive, validate_source
from config import SOURCE, load
from integrity import verify


SOURCE_DATA = load(SOURCE)
ORIGINAL = load(ROOT / SOURCE_DATA["original_source"]["path"])
PREVIOUS = load(ROOT / SOURCE_DATA["previous_decision"]["path"])
EVIDENCE = audit_evidence()
INTEGRITY = verify()
DECISION = derive(SOURCE_DATA, EVIDENCE, INTEGRITY)


def test_01_source_schema_is_final_global_v1():
    assert SOURCE_DATA["schema"] == "rebaseguard.level4-final-global-requirements.v1"


def test_02_audit_start_commit_is_v3_closure_head():
    assert SOURCE_DATA["audit_start_head"] == "ba9f49d202b8feb71fb4923929b506f8e9b88a40"


def test_03_original_requirement_fingerprint_matches():
    path = ROOT / SOURCE_DATA["original_source"]["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == SOURCE_DATA["original_source"]["sha256"]


def test_04_previous_decision_fingerprint_matches():
    path = ROOT / SOURCE_DATA["previous_decision"]["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == SOURCE_DATA["previous_decision"]["sha256"]


def test_05_stage_f_fingerprint_and_verdict_match():
    meta = SOURCE_DATA["historical_stage_f"]
    path = ROOT / meta["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == meta["sha256"]
    assert load(path)["decision"] == "LEVEL-4-PARTIAL"


def test_06_requirement_count_is_exactly_eighteen():
    assert len(SOURCE_DATA["requirements"]) == 18


def test_07_requirement_ids_are_stable_and_ordered():
    assert [row["id"] for row in SOURCE_DATA["requirements"]] == [f"L4R-{i:02d}" for i in range(1, 19)]


def test_08_mandatory_count_is_exactly_sixteen():
    assert sum(row["classification"] == "MANDATORY" for row in SOURCE_DATA["requirements"]) == 16


def test_09_descriptions_match_original_source():
    original = {row["id"]: row for row in ORIGINAL["requirements"]}
    assert all(row["requirement"] == original[row["id"]]["requirement"] for row in SOURCE_DATA["requirements"])


def test_10_classifications_match_original_source():
    original = {row["id"]: row for row in ORIGINAL["requirements"]}
    assert all(row["classification"] == original[row["id"]]["classification"] for row in SOURCE_DATA["requirements"])


def test_11_stage_f_statuses_match_original_source():
    original = {row["id"]: row for row in ORIGINAL["requirements"]}
    assert all(row["stage_f"] == original[row["id"]]["stage_f"] for row in SOURCE_DATA["requirements"])


def test_12_previous_reaudit_statuses_match_previous_decision():
    previous = {row["id"]: row for row in PREVIOUS["requirements"]}
    assert all(row["previous_reaudit_status"] == previous[row["id"]]["current_status"]
               for row in SOURCE_DATA["requirements"])


def test_13_allowed_taxonomy_labels_are_preserved():
    assert SOURCE_DATA["taxonomy"]["allowed_labels"] == ORIGINAL["taxonomy"]["allowed_labels"]


def test_14_closed_requires_all_mandatory_rows_pass():
    assert SOURCE_DATA["taxonomy"]["closed_rule"] == "ALL_MANDATORY_ROWS_PASS"
    assert SOURCE_DATA["taxonomy"]["mandatory_satisfying_statuses"] == ["PASS"]
    assert SOURCE_DATA["taxonomy"]["closed_with_limitations_independently_authorized"] is False


def test_15_campaign_requirement_map_is_exact():
    assert SOURCE_DATA["campaign_requirement_map"] == EXPECTED_MAP


def test_16_all_evidence_campaigns_pass_with_existing_paths():
    assert EVIDENCE["all_campaigns_pass"] is True
    assert all(all((ROOT / path).exists() for path in row["evidence_paths"])
               for row in EVIDENCE["campaigns"])


def test_17_track1b_closes_only_l4r09():
    row = next(row for row in EVIDENCE["campaigns"] if row["campaign"] == "MGT1-TRACK1B-CLOSED")
    assert row["target_requirement"] == "L4R-09" and row["status"] == "PASS"


def test_18_sr_closes_derivative_but_not_arb_certificate():
    row = next(row for row in EVIDENCE["campaigns"] if row["campaign"] == "SR-DERIVATIVE-CLOSED")
    assert row["target_requirement"] == "L4R-10" and row["checks"]["arb_open_preserved"]


def test_19_track3ab_preserves_historical_track3_failure():
    row = next(row for row in EVIDENCE["campaigns"] if row["campaign"] == "LOCATION-FAMILY-TRACK3AB-CLOSED")
    assert row["target_requirement"] == "L4R-14" and row["checks"]["historical_track3_preserved"]


def test_20_d4_closes_l4r11_with_local_formula():
    row = next(row for row in EVIDENCE["campaigns"] if row["campaign"] == "D4-PHASE-MAP-CLOSED")
    assert row["target_requirement"] == "L4R-11" and row["checks"]["formula_matches"]


def test_21_novelty_closes_l4r16_at_n2_only():
    row = next(row for row in EVIDENCE["campaigns"] if row["campaign"] == "NOVELTY-VERIFICATION-CLOSED")
    assert row["target_requirement"] == "L4R-16" and row["checks"]["n2_claim_narrowing_preserved"]


def test_22_v3_closes_l4r15_and_preserves_negative_evidence():
    row = next(row for row in EVIDENCE["campaigns"] if row["campaign"] == "EXTERNAL-VALIDATION-V3-CLOSED")
    assert row["target_requirement"] == "L4R-15"
    assert row["checks"]["historical_stage_e_preserved"] and row["checks"]["historical_v2_preserved"]
    assert row["checks"]["unfavorable_route_b_preserved"]


def test_23_protected_history_is_intact():
    assert INTEGRITY["status"] == "INTACT" and not INTEGRITY["errors"]
    assert INTEGRITY["trees_verified"] == 23 and INTEGRITY["files_verified"] == 23


def test_24_current_counts_are_fifteen_three_zero_zero():
    assert DECISION["current_counts"] == {"PASS": 15, "PARTIAL": 3, "FAIL": 0, "OPEN": 0}


def test_25_mandatory_counts_are_fourteen_two_zero_zero():
    assert DECISION["mandatory_counts"] == {"PASS": 14, "PARTIAL": 2, "FAIL": 0, "OPEN": 0}


def test_26_current_verdict_is_level4_partial():
    assert DECISION["current_verdict"] == "LEVEL-4-PARTIAL"


def test_27_exact_blockers_are_l4r06_and_l4r12():
    assert [(row["id"], row["current_status"]) for row in DECISION["mandatory_blockers"]] == [
        ("L4R-06", "PARTIAL"), ("L4R-12", "PARTIAL")]


def test_28_no_mandatory_fail_or_open_remains():
    assert DECISION["mandatory_fail_open"] == []


def test_29_exact_new_changes_are_d4_external_and_novelty():
    assert [(row["id"], row["campaign"]) for row in DECISION["rows_changed_since_previous_reaudit"]] == [
        ("L4R-11", "D4-PHASE-MAP-CLOSED"),
        ("L4R-15", "EXTERNAL-VALIDATION-V3-CLOSED"),
        ("L4R-16", "NOVELTY-VERIFICATION-CLOSED")]


def test_30_l4r13_is_partial_but_nonblocking():
    row = next(row for row in DECISION["requirements"] if row["id"] == "L4R-13")
    assert row["current_status"] == "PARTIAL" and row["blocks_closure"] is False


def test_31_sr_arb_open_is_explicit_nonblocker():
    assert DECISION["sr_boundary"]["rigorous_SR_local_instability_certificate"] == "OPEN"
    assert DECISION["remaining_open_nonblockers"][0]["id"] == "SR-ARB-CERTIFICATE"


def test_32_historical_stage_e_v2_track_failures_are_preserved():
    history = DECISION["historical_statuses_preserved"]
    assert history["stage_e_H_E5"] == "0/3"
    assert history["external_validation_v2_support"] == "1/3"
    assert history["track_1a"] == "MGT1-TRACK1A-FAILED"
    assert history["historical_track_3"] == "LOCATION-FAMILY-THEOREM-PARTIAL"


def test_33_safe_summaries_are_bounded_and_contain_no_priority_claims():
    text = DECISION["claims"]["publication_safe_summary"] + DECISION["claims"]["resume_safe_summary"]
    assert "remains partial" in text
    assert not any(term in text.lower() for term in ("first-ever", "unprecedented", "previously unknown"))


def test_34_core_generated_artifacts_match_generator_bytes():
    assert all(path.exists() and path.read_text() == content for path, content in build().items())


def test_35_synthetic_mandatory_failure_cannot_close():
    synthetic = derive(copy.deepcopy(SOURCE_DATA), EVIDENCE, INTEGRITY, {"L4R-01": "FAIL"})
    assert synthetic["current_verdict"] != "LEVEL-4-CLOSED"
    assert any(row["id"] == "L4R-01" for row in synthetic["mandatory_blockers"])


def test_36_verifier_integration_and_offline_reproducer_are_present():
    verifier = (ROOT / "scripts/verify_level_4.sh").read_text()
    reproducer = (BASE / "reproduce.sh").read_text().lower()
    assert "final global re-audit suite" in verifier and "final_global_reaudit/tests" in verifier
    assert os.access(BASE / "reproduce.sh", os.X_OK)
    assert not any(token in reproducer for token in ("curl ", "wget ", "http://", "https://"))
