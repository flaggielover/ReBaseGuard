from __future__ import annotations

import json
from pathlib import Path

import decision
import reports
import reproduction_check
from config import ALLOWED_SCOPED_STATUSES

BASE = Path(__file__).resolve().parents[1]
RESULTS = BASE / "results"


def load_if(name: str):
    path = RESULTS / name
    return json.loads(path.read_text()) if path.exists() else None


def test_first_adversarial_run_is_preserved_if_present():
    got = load_if("adversarial_first.json")
    if got is None:
        return
    assert got["n_checks"] == 19
    assert [row["id"] for row in got["checks"]] == [f"A{i}" for i in range(1, 20)]


def test_final_adversarial_is_exactly_19_of_19_if_present():
    got = load_if("adversarial_final.json")
    if got is None:
        return
    assert got["n_passed"] == got["n_checks"] == 19
    assert got["status"] == "PASS"
    assert [row["id"] for row in got["checks"]] == [f"A{i}" for i in range(1, 20)]
    assert all(row["passed"] for row in got["checks"])


def test_verification_record_is_green_if_present():
    got = load_if("verification.json")
    if got is None:
        return
    assert got["status"] == "PASS"
    assert got["terminal_marker"] is True
    assert got["pytest_pass_count"] > 0


def test_reproduction_record_is_byte_stable_if_present():
    got = load_if("reproduction.json")
    if got is None:
        return
    assert got == reproduction_check.build()
    assert got["status"] == "PASS"
    assert got["offline"] is True
    assert got["new_science_run"] is False
    assert got["audit_artifacts_byte_stable"] is True


def test_decision_is_generator_owned_and_mechanical_if_present():
    got = load_if("decision.json")
    if got is None:
        return
    assert got == decision.build()
    assert got["generator_owned"] is True
    assert got["scoped_verdict"] in ALLOWED_SCOPED_STATUSES
    all_pass = all(row["status"] == "PASS" for row in got["criteria"])
    assert (got["scoped_verdict"] == "L4R12-CLOSED-NEGATIVE-RESULT") == all_pass


def test_pass_mapping_occurs_only_when_allowed_and_sufficient_if_present():
    got = load_if("decision.json")
    if got is None:
        return
    assert got["same_requirement_mapping"] == (
        got["negative_result_closure_allowed"]
        and got["evidence_sufficient"]
        and got["scoped_verdict"] == "L4R12-CLOSED-NEGATIVE-RESULT"
    )
    assert (got["original_L4R12_current_status"] == "PASS") == got["same_requirement_mapping"]


def test_decision_preserves_history_if_present():
    got = load_if("decision.json")
    if got is None:
        return
    assert got["historical_D2_5_preserved"] is True
    assert got["D4_preserved"] is True
    assert got["L4R06_preserved"] is True
    assert got["historical_final_global_reaudit"] == "LEVEL-4-PARTIAL"
    assert got["global_reaudit_performed"] is False


def test_claim_firewall_survives_finalization_if_present():
    got = load_if("decision.json")
    if got is None:
        return
    assert "under the frozen" in got["claim_safe"]
    assert "in general" not in got["claim_safe"]
    assert got["claim_forbidden"].endswith("in general.")


def test_human_reports_mirror_decision_if_present():
    got = load_if("decision.json")
    if got is None:
        return
    for name, text in reports.build().items():
        assert (BASE / name).read_text() == text
    final = (BASE / "FINAL_REPORT.md").read_text()
    assert got["scoped_verdict"] in final
    assert got["original_L4R12_current_status"] in final
    assert got["exact_next_action"] in final


def test_reproducer_is_offline_audit_only():
    text = (BASE / "reproduce.sh").read_text()
    assert "curl " not in text and "wget " not in text
    assert "--recompute" not in text
    assert "scripts/verify_level_4.sh" in text
    assert "adversarial.py\" --check-final" in text
