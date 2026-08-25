from __future__ import annotations

import json
from pathlib import Path

import audit
import integrity
from config import NEGATIVE_VERDICT, ORIGINAL_CLASS, ORIGINAL_WORDING, PRIMARY_METRICS

BASE = Path(__file__).resolve().parents[1]
RESULTS = BASE / "results"


def load(name: str):
    return json.loads((RESULTS / name).read_text())


def test_original_wording_extraction_is_exact():
    got = load("source_extraction.json")
    assert got["requirement"]["wording"] == ORIGINAL_WORDING
    assert got == audit.build_sources()


def test_original_requirement_class_is_mandatory():
    assert load("source_extraction.json")["requirement"]["classification"] == ORIGINAL_CLASS


def test_preoutcome_source_precedence_is_explicit():
    got = load("source_extraction.json")
    assert got["source_precedence"][:2] == [
        "pre-outcome Stage-D protocol", "pre-outcome D2.5 precommit"
    ]
    assert got["authoritative_scope"] == "repository-only"


def test_semantics_are_mechanically_investigational():
    got = load("semantic_classification.json")
    assert got == audit.build_semantics(load("source_extraction.json"))
    assert got["semantics"] == "INVESTIGATIONAL"
    assert got["existential_positive_transition_required"] is False


def test_negative_answer_was_explicitly_allowed_before_outcomes():
    sources = load("source_extraction.json")
    semantics = load("semantic_classification.json")
    assert sources["frozen_precommit"]["written_before_data"]
    assert sources["frozen_precommit"]["negative_rule_present"]
    assert semantics["negative_result_closure_allowed"]


def test_later_partial_normalization_is_not_erased():
    got = load("source_extraction.json")["requirement"]
    assert got["stage_f"] == {"status": "PARTIAL", "label": "NEGATIVE RESULT"}
    assert got["previous_reaudit_status"] == "PARTIAL"


def test_d25_evidence_paths_and_hashes_are_frozen():
    got = load("source_extraction.json")
    assert got["frozen_acceptance_condition"]["source"] == "level4/stage_d/STAGE_D_PROTOCOL.md"
    assert got["frozen_precommit"]["source"] == "level4/stage_d/notes/D2_5_PRECOMMIT.md"


def test_crossing_is_consistent_and_independently_supported():
    got = load("evidence_assessment.json")
    assert got["crossing"]["stage_d_bracket"] == [50, 75]
    assert got["crossing"]["D4_bracket"] == [70, 72]
    assert got["crossing"]["D4_gamma_at_bracket"][0] > 2
    assert got["crossing"]["D4_gamma_at_bracket"][1] < 2


def test_operational_design_retains_complete_frozen_grid():
    got = load("evidence_assessment.json")["operational_design"]
    assert got["m_values"] == [10, 20, 50, 65, 75, 90, 100]
    assert got["n_replicates"] == 20000
    assert got["primary_metrics"] == list(PRIMARY_METRICS)


def test_negative_result_is_not_low_power_nondemonstration():
    got = load("evidence_assessment.json")
    assert got["negative_result_class"] == "C_COMPLETED_RESEARCH_QUESTION_WITH_VALID_NEGATIVE_ANSWER"
    assert min(got["operational_result"]["m65_vs_m75_combined_separation"].values()) > 3


def test_historical_negative_result_is_exact():
    got = load("evidence_assessment.json")
    assert got["historical_verdict"] == NEGATIVE_VERDICT
    assert got["operational_result"]["metrics_peaking_at_crossing"] == 0
    assert got["operational_result"]["metrics_monotone_in_log_m"] == 4


def test_all_n12_checks_pass():
    got = load("evidence_assessment.json")
    assert got["n_passed"] == got["n_total"] == 10
    assert all(row["status"] == "PASS" for row in got["N12"])
    assert got["evidence_sufficient"] is True


def test_same_requirement_candidate_requires_semantics_and_evidence():
    got = load("evidence_assessment.json")
    assert got["same_requirement_mapping_candidate"] is True


def test_claim_firewall_is_scoped_and_forbids_universal_claim():
    got = load("evidence_assessment.json")
    assert "under the frozen" in got["claim_safe"]
    assert got["claim_forbidden"] == "The crossing has no operational consequence in general."


def test_historical_integrity_and_statuses_pass():
    got = integrity.verify()
    assert got["status"] == "PASS", got["errors"]
    assert got["historical_D2_5_preserved"] is True
    assert got["D4_preserved"] is True
    assert got["L4R06_preserved"] is True


def test_audit_json_is_byte_stable():
    for name, value in audit.build_all().items():
        assert (RESULTS / name).read_text() == audit.canonical_json(value)

