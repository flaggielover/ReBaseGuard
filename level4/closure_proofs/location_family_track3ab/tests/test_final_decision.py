from __future__ import annotations

import json
from pathlib import Path


CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]


def final() -> dict:
    return json.loads((CAMPAIGN / "results/decision.json").read_text())


def test_exact_track_and_requirement_decisions() -> None:
    data = final()
    assert data["decision"] == "LOCATION-FAMILY-TRACK3AB-CLOSED"
    assert data["general_location_family_theorem_requirement"] == "CLOSED"
    assert data["global_level4_reaudit_performed"] is False


def test_every_closure_criterion_passes() -> None:
    assert all(final()["criteria"].values())


def test_numerical_decision_is_copied_without_reinterpretation() -> None:
    data = final()
    numerical = json.loads((CAMPAIGN / "results/numerical_decision.json").read_text())
    assert data["numerical"]["status"] == numerical["status"] == "T3A-NUMERICAL-PASS"
    assert data["numerical"]["pooled_relative"] == numerical["pooled"]["comparison"]["symmetric_relative_difference"]
    assert data["numerical"]["pooled_abs_z"] == numerical["pooled"]["comparison"]["absolute_z"]


def test_lean_boundary_and_axioms_are_exact() -> None:
    lean = final()["lean"]
    assert lean["status"] == "COMPILED"
    assert lean["concrete_infinite_t3_instantiated_end_to_end"] is False
    assert lean["axioms"] == ["propext", "Classical.choice", "Quot.sound"]
    assert lean["project_specific_axiom"] is False
    assert lean["sorry_or_admit"] is False


def test_historical_track3_is_still_partial_and_failed() -> None:
    data = final()["historical_track_3"]
    old = json.loads(
        (REPO / "level4/closure_proofs/location_family/results/decision.json").read_text()
    )
    assert data["decision"] == old["decision"] == "LOCATION-FAMILY-THEOREM-PARTIAL"
    assert data["numerical_gate"] == "FAILED"
    assert data["failed_relative_discrepancy"] > data["relative_limit"]
    assert data["unchanged"] is True


def test_claim_guard_and_next_action() -> None:
    report = (CAMPAIGN / "FINAL_REPORT.md").read_text()
    assert "Track 3 did not pass" in report
    assert "not presented as a full" in report
    assert "machine construction of the infinite stochastic process" in report
    assert "No overall Level-4 re-audit was" in report
    assert "performed, and overall Level 4 remains historically" in report
    assert "GLOBAL LEVEL-4 RE-AUDIT" in report
    assert "Track 3 actually passed" not in report
    assert final()["arb"] == "NOT STARTED — OUT OF SCOPE"


def test_reproducer_contains_complete_order_and_count() -> None:
    source = (CAMPAIGN / "reproduce.sh").read_text()
    numerical = source.index("retained numerical checkpoint audit")
    lean = source.index("Track-3B Lean compile")
    authoritative = source.index("authoritative repository verifier")
    final_gate = source.index("final scoped decision")
    assert numerical < lean < authoritative < final_gate
    assert 'scripts/verify_level_4.sh' in source
    assert "929 / 929" in source
