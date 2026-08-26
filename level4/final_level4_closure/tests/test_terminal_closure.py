from __future__ import annotations

import copy
import hashlib
import os
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
sys.path.insert(0, str(BASE / "src"))

from audit import CAMPAIGNS, audit_evidence, build_canonical, outputs as audit_outputs
from config import PREVIOUS, SOURCE, load
from decision_engine import derive
from integrity import verify
from reports import outputs as report_outputs
from reproduction import digest, generate


CANONICAL = load(BASE / "requirements.json")
SOURCE_DATA = load(SOURCE)
PREVIOUS_DATA = load(PREVIOUS)
EVIDENCE = load(BASE / "results/evidence_audit.json")
LEDGER = load(BASE / "results/ledger_derivation.json")
ROWS = CANONICAL["requirements"]
BY_ID = {row["id"]: row for row in ROWS}
CAMPAIGN_BY_ID = {row["target_requirement"]: row for row in EVIDENCE["campaigns"]}


def test_01_canonical_schema_is_generator_owned():
    assert CANONICAL["schema"] == "rebaseguard.final-level4-canonical-requirements.v1"
    assert CANONICAL["generator_owned"] is True


def test_02_authoritative_source_fingerprint_matches():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == CANONICAL["authoritative_source"]["sha256"]


def test_03_requirement_count_is_exactly_eighteen():
    assert len(ROWS) == len(SOURCE_DATA["requirements"]) == 18


def test_04_requirement_ids_are_exact_and_ordered():
    assert [row["id"] for row in ROWS] == [f"L4R-{number:02d}" for number in range(1, 19)]


def test_05_mandatory_count_is_exactly_sixteen():
    assert sum(row["mandatory"] for row in ROWS) == 16


def test_06_classifications_match_protected_source():
    source_by = {row["id"]: row for row in SOURCE_DATA["requirements"]}
    assert all(row["classification"] == source_by[row["id"]]["classification"] for row in ROWS)
    assert all(row["class"] == row["classification"] for row in ROWS)


def test_07_wording_matches_protected_source():
    source_by = {row["id"]: row for row in SOURCE_DATA["requirements"]}
    assert all(row["requirement"] == source_by[row["id"]]["requirement"] for row in ROWS)


def test_08_stage_f_statuses_match_protected_source():
    source_by = {row["id"]: row for row in SOURCE_DATA["requirements"]}
    assert all(row["stage_f_status"] == source_by[row["id"]]["stage_f"] for row in ROWS)


def test_09_previous_statuses_match_final_global_decision():
    prior_by = {row["id"]: row for row in PREVIOUS_DATA["requirements"]}
    assert all(row["previous_final_audit_status"] == prior_by[row["id"]]["current_status"] for row in ROWS)


def test_10_frozen_closure_rule_is_unchanged():
    taxonomy = CANONICAL["taxonomy"]
    assert taxonomy["closed_rule"] == "ALL_MANDATORY_ROWS_PASS"
    assert taxonomy["mandatory_satisfying_statuses"] == ["PASS"]
    assert taxonomy["closed_with_limitations_independently_authorized"] is False


def test_11_historical_global_verdicts_are_immutable_partials():
    assert set(CANONICAL["historical_verdicts"].values()) == {"LEVEL-4-PARTIAL"}


def test_12_all_eight_mapped_campaigns_pass():
    assert len(EVIDENCE["campaigns"]) == len(CAMPAIGNS) == 8
    assert EVIDENCE["all_campaigns_pass"] is True


def test_13_l4r06_maps_to_pass():
    row = CAMPAIGN_BY_ID["L4R-06"]
    assert row["campaign"] == "L4R06-POLICY-CLOSED" and row["status"] == "PASS"
    assert row["checks"]["same_requirement_mapping"] and BY_ID["L4R-06"]["current_status"] == "PASS"


def test_14_l4r06_preserves_stage_c_and_c6():
    row = CAMPAIGN_BY_ID["L4R-06"]
    assert row["checks"]["historical_C6_preserved"]
    assert EVIDENCE["negative_and_unfavorable_history"]["stage_c_C6"] == "FAILED"


def test_15_l4r06_preserves_unfavorable_results():
    assert CAMPAIGN_BY_ID["L4R-06"]["checks"]["unfavorable_findings_visible"]


def test_16_l4r12_maps_to_pass():
    row = CAMPAIGN_BY_ID["L4R-12"]
    assert row["campaign"] == "L4R12-CLOSED-NEGATIVE-RESULT" and row["status"] == "PASS"
    assert row["checks"]["same_requirement_mapping"] and BY_ID["L4R-12"]["current_status"] == "PASS"


def test_17_l4r12_is_investigational_negative_answer():
    checks = CAMPAIGN_BY_ID["L4R-12"]["checks"]
    assert checks["investigational_semantics"] and checks["valid_negative_answer"]
    assert checks["scoped_negative_claim"] and checks["no_new_science"]


def test_18_l4r12_crossing_values_and_power_are_verified():
    checks = CAMPAIGN_BY_ID["L4R-12"]["checks"]
    assert checks["crossing_values"] and checks["adequate_power"] and checks["frozen_metrics"]


def test_19_l4r13_remains_nonblocking_partial():
    row = BY_ID["L4R-13"]
    assert row["classification"] == "STRONG_EXTENSION"
    assert row["current_status"] == "PARTIAL" and not row["mandatory"] and not row["current_blocking"]


def test_20_current_counts_are_mechanical():
    result = derive(ROWS, integrity_ok=True, engineering_ok=True)
    assert result["current_counts"] == LEDGER["counts"] == {"PASS": 17, "PARTIAL": 1, "FAIL": 0, "OPEN": 0}


def test_21_mandatory_counts_are_mechanical():
    result = derive(ROWS, integrity_ok=True, engineering_ok=True)
    assert result["mandatory_counts"] == LEDGER["mandatory_counts"] == {"PASS": 16, "PARTIAL": 0, "FAIL": 0, "OPEN": 0}


def test_22_closed_candidate_follows_original_rule():
    assert derive(ROWS, True, True)["current_verdict"] == LEDGER["ledger_candidate_verdict"] == "LEVEL-4-CLOSED"


def test_23_engineering_gate_prevents_premature_closure():
    assert derive(ROWS, True, False)["current_verdict"] == "LEVEL-4-PARTIAL"


def test_24_synthetic_mandatory_partial_forces_partial():
    rows = copy.deepcopy(ROWS)
    rows[0]["current_status"] = "PARTIAL"
    assert derive(rows, True, True)["current_verdict"] == "LEVEL-4-PARTIAL"


def test_25_nonmandatory_partial_does_not_block():
    rows = copy.deepcopy(ROWS)
    next(row for row in rows if row["id"] == "L4R-13")["current_status"] = "PARTIAL"
    assert derive(rows, True, True)["current_verdict"] == "LEVEL-4-CLOSED"


def test_26_optional_sr_arb_open_is_outside_ledger_blockers():
    item = CANONICAL["open_nonblockers"][0]
    assert item["id"] == "SR-ARB-CERTIFICATE" and item["status"] == "OPEN"
    assert LEDGER["mandatory_blocker_ids"] == []


def test_27_sr_numerical_certificate_boundary_is_preserved():
    checks = CAMPAIGN_BY_ID["L4R-10"]["checks"]
    assert checks["Gamma_numerical"] and checks["arb_open"] and checks["theorem_closed"]


def test_28_historical_negative_results_survive():
    history = EVIDENCE["negative_and_unfavorable_history"]
    assert history["stage_d_D2_3"] == "FAIL"
    assert history["stage_d_D2_5"] == "MATHEMATICAL, NOT OPERATIONAL"
    assert history["stage_e_support"] == "0/3"
    assert history["external_validation_v2_support"] == "1/3"
    assert history["track_1A"] == "MGT1-TRACK1A-FAILED"


def test_29_every_transition_has_existing_evidence():
    changed = [row for row in ROWS if row["changed_since_stage_f"]]
    assert len(changed) == 8
    assert all(row["evidence_paths"] and all((ROOT / path).exists() for path in row["evidence_paths"])
               for row in changed)


def test_30_claim_firewall_preserves_bounded_claims():
    text = (BASE / "CLAIM_FIREWALL.md").read_text()
    allowed = text.split("## Prohibited", 1)[0]
    assert "Gamma_SR is not" in allowed and "regime-dependent" in allowed
    assert "all research questions solved" not in allowed.lower()
    assert "absolute novelty" not in allowed.lower()


def test_31_core_json_and_reports_equal_generator_bytes():
    assert all(path.exists() and path.read_text() == content for path, content in audit_outputs().items())
    assert all(path.exists() and path.read_text() == content for path, content in report_outputs().items())


def test_32_reports_display_mechanical_counts():
    ledger = (BASE / "REQUIREMENT_LEDGER.md").read_text()
    assert "17 PASS · 1 PARTIAL · 0 FAIL · 0 OPEN" in ledger
    assert ledger.count("| L4R-") == 18


def test_33_reproducer_regeneration_is_byte_stable_and_offline():
    before = digest()
    generate()
    assert digest() == before
    text = (BASE / "reproduce.sh").read_text().lower()
    assert not any(token in text for token in ("curl ", "wget ", "http://", "https://"))
    assert os.access(BASE / "reproduce.sh", os.X_OK)


def test_34_protected_history_is_intact():
    result = verify()
    assert result["status"] == "INTACT" and not result["errors"]
    assert result["trees_verified"] == 17 and result["files_verified"] == 18


def test_35_audit_rebuild_is_pure_and_consistent():
    canonical, evidence, ledger = build_canonical()
    assert canonical == CANONICAL and evidence == EVIDENCE and ledger == LEDGER


def test_36_verifier_integration_is_present():
    verifier = (ROOT / "scripts/verify_level_4.sh").read_text()
    assert "terminal final Level-4 closure suite" in verifier
    assert "level4/final_level4_closure/tests" in verifier
