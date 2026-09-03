"""Governance consistency: nothing historical may move, and nothing may be
frozen or claimed by a pre-campaign audit."""

from __future__ import annotations

import subprocess

import pytest

DOCS = ("README.md", "AUDIT.md", "HISTORICAL_OBLIGATION_TABLE.md",
        "DRAFT_SUCCESSOR_SCOPE.md")

#: Phrases that could never be legitimate in a pre-campaign audit.  Negated
#: forms such as "no Level-4 global closure is claimed" are the point of several
#: of these documents, so the patterns are written as positive assertions only.
FORBIDDEN = (
    "p4 = closed",
    "p4 is closed",
    "p4 is now closed",
    "level-4 global closure is established",
    "level-4 is globally closed",
    "novelty is established",
    "first proof in the literature",
    "is distribution-free",
    "is detector-universal",
)


@pytest.mark.parametrize("name", DOCS)
def test_document_exists_and_is_substantive(audit, name):
    path = audit / name
    assert path.exists(), name
    assert len(path.read_text()) > 700, name


@pytest.mark.parametrize("name", DOCS)
def test_no_forbidden_overclaim(audit, name):
    text = (audit / name).read_text().lower()
    for phrase in FORBIDDEN:
        assert phrase not in text, (name, phrase)


@pytest.mark.parametrize("name", DOCS)
def test_every_document_restates_p4_as_partial(audit, name):
    assert "PARTIAL" in (audit / name).read_text(), name


def test_audit_is_not_binding_and_creates_no_checkpoint(results):
    assert results["binding"] is False
    assert results["checkpoint_created"] is False
    assert results["classification"] == "PRE_SUCCESSOR_FEASIBILITY_AND_SCOPE_AUDIT"


def test_draft_successor_scope_is_marked_draft_and_unexecuted(audit):
    text = (audit / "DRAFT_SUCCESSOR_SCOPE.md").read_text()
    assert "NOT EXECUTED, NOT FROZEN" in text
    assert "STATUS        = DRAFT_ONLY" in text
    assert "CHECKPOINT    = NOT CREATED" in text


def test_draft_scope_contains_every_required_section(audit):
    text = (audit / "DRAFT_SUCCESSOR_SCOPE.md").read_text()
    for heading in ("Exact successor scientific question",
                    "Exact required theorem",
                    "Assumptions",
                    "Correspondence points / cells",
                    "Lean spine",
                    "Interval / certificate requirement",
                    "Pass / fail gates",
                    "Resource stop rule",
                    "Historical preservation rules"):
        assert heading in text, heading


def test_governance_test_answers_are_all_preserving(results):
    test = results["governance"]["successor_governance_test"]
    assert test["requires_changing_historical_p4_verdict"] is False
    assert test["requires_changing_historical_failed_artifacts"] is False
    assert test["requires_changing_frozen_theorem_meaning"] is False
    assert test["requires_changing_a_p4_threshold_after_seeing_results"] is False
    assert test["adds_new_successor_evidence_under_fresh_preregistered_scope"] is True
    assert results["governance"]["p4x_governance_valid"] == "YES"


def test_the_p4x_own_threshold_risk_is_recorded_not_hidden(results):
    risk = results["governance"]["successor_governance_test"]["p4x_own_threshold_risk"]
    assert risk.startswith("REAL")
    assert "post-hoc" in risk


def test_the_destroyed_disposition_artifact_is_recorded_with_its_digest(results):
    gov = results["governance"]
    assert gov["p4_disposition_audit_status"] == "DESTROYED_AND_UNRECOVERABLE"
    assert len(gov["p4_disposition_audit_sha256"]) == 64
    assert gov["prohibition_text_readable"] is False
    assert gov["prohibition_reading"] == "A"
    assert gov["conditionality"]


def test_no_p4r_or_p4_1_prohibition_exists_in_the_historical_record(root):
    """The audit's claim of zero historical references must stay true.

    This audit's own documents discuss the absent `P4R` / `P4.1` prohibition by
    name, so the audit namespace is excluded: the claim is about the historical
    record, not about this audit's discussion of it.
    """
    out = subprocess.run(
        ["git", "grep", "-l", "-E", r"P4R|P4\.1|p4_1",
         "--", "*.md", "*.json", "*.py", "*.lean", "*.sh", "*.txt",
         ":(exclude)level4/closure_proofs/p4x_generalization_boundary/**"],
        cwd=root, capture_output=True, text=True,
    )
    assert out.stdout.strip() == "", out.stdout


def test_level4_global_closure_is_not_claimed(results):
    assert results["verdicts"]["LEVEL4_GLOBAL_CLOSURE"] == "NO"
    assert results["verdicts"]["NOVELTY_STATUS"] == "NOT_ESTABLISHED"
    assert results["verdicts"]["P5_RESIDUAL_STATUS"] == "DOCUMENTED_LIMITATION"


def test_decision_is_one_of_the_four_charter_cases(results):
    assert results["verdicts"]["P4X_DECISION"] in {
        "OPEN_P4X_SUCCESSOR", "OPEN_P4X_NARROW_SUCCESSOR",
        "ONE_MORE_CHEAP_AUDIT_REQUIRED", "DO_NOT_OPEN_P4X",
    }
    assert results["verdicts"]["P4X_FEASIBILITY"] in {
        "STRONG", "MODERATE", "WEAK", "NOT_FEASIBLE"}
    assert results["verdicts"]["P4X_EXPECTED_SCALE"] in {
        "LIGHT", "MEDIUM", "HEAVY", "P5X_LIKE"}


def test_a_p5x_like_scale_would_have_to_be_warned_about(results):
    """The charter forbids opening a P5X-like campaign without an explicit warning."""
    scale = results["verdicts"]["P4X_EXPECTED_SCALE"]
    if scale in {"HEAVY", "P5X_LIKE"}:
        assert "WARNING" in (results["verdicts"].get(
            "P4X_EXPECTED_SCALE_CAVEAT", "").upper())
    else:
        # a non-heavy scale still has to carry its honest cost caveat
        assert results["verdicts"]["P4X_EXPECTED_SCALE_CAVEAT"]


def test_all_four_routes_are_assessed(results):
    routes = results["routes"]
    assert sorted(routes) == ["A", "B", "C", "D"]
    for key, route in routes.items():
        for field in ("math_risk", "implementation", "certification", "cpu",
                      "wall", "new_lean", "new_arb", "p_true_contradiction"):
            assert field in route, (key, field)


def test_only_route_b_is_recommended(results):
    routes = results["routes"]
    assert routes["B"].get("recommended") is True
    assert routes["A"]["closes_line"] is False
    assert routes["C"]["required_for_closure"] is False
    assert routes["D"]["admissible_as_p4_repair"] is False


def test_protected_tree_objects_are_recorded(results):
    objects = results["protected_tree_objects_at_head"]
    for path in ("level4/closure_proofs/p4_theory_generalization",
                 "level4/closure_proofs/p5_nonlinear_dynamics",
                 "level4/closure_proofs/p5x_global_nonlinear_dynamics",
                 "level4/closure_proofs/m_gt_1_priority1",
                 "level4/closure_proofs/sr_derivative_priority2",
                 "level4/closure_proofs/m_rho_stability_priority3",
                 "level4/closure_proofs/p9r_final_synthesis_repair"):
        assert len(objects[path]) == 40, path


def test_protected_tree_objects_still_match_head(root, results):
    for path, expected in results["protected_tree_objects_at_head"].items():
        out = subprocess.run(["git", "rev-parse", f"HEAD:{path}"],
                             cwd=root, capture_output=True, text=True)
        assert out.returncode == 0, path
        assert out.stdout.strip() == expected, path


def test_audit_writes_nothing_outside_its_own_namespace(root, results):
    assert results["writes_outside_audit_namespace"] == 0
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    prefix = "level4/closure_proofs/p4x_generalization_boundary/"
    for line in out.stdout.splitlines():
        path = line[3:].strip().strip('"')
        assert path.startswith(prefix), line
