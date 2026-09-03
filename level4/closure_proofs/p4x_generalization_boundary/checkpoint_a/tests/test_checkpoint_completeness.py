"""The binding checkpoint must be complete, active, and free of results."""

from __future__ import annotations

import pytest

REQUIRED_TOP_LEVEL = (
    "artifact", "active", "binding", "generated_from_commit", "governance",
    "successor_question", "inherited_theorem", "assumption_semantics",
    "core_obligations", "estimator_plan", "heavy_tail_policy",
    "precision_rule", "production_scope", "production_plan",
    "per_configuration_plan", "gates", "route_q_role", "lean_and_arb",
    "cost_envelope", "stop_rules", "verdict_semantics",
    "scientific_line_semantics", "novelty", "level4_context",
    "protected_tree_manifest", "source_artifact_hashes", "successor_verdict",
)

REQUIRED_DOC_SECTIONS = (
    "## 1. Governance",
    "## 2. Successor scientific question",
    "## 3. Inherited theorem",
    "## 4. Assumption semantics",
    "## 5. Core successor obligations",
    "## 6. Estimator plan",
    "## 7. Heavy-tail policy",
    "## 8. Precision rule",
    "## 9. Production scope",
    "## 10. Gates",
    "## 11. Route-Q role",
    "## 12. Lean and Arb",
    "## 13. Cost envelope",
    "## 14. STOP rules",
    "## 15. Verdict semantics",
    "## 16. Scientific-line semantics",
    "## 17. Novelty",
    "## 18. Level-4 context",
    "## 19. Protected-tree manifest",
)


@pytest.mark.parametrize("key", REQUIRED_TOP_LEVEL)
def test_manifest_has_every_required_section(manifest, key):
    assert key in manifest, key
    assert manifest[key] not in (None, "", {}, []), key


@pytest.mark.parametrize("heading", REQUIRED_DOC_SECTIONS)
def test_document_has_every_required_section(doc, heading):
    assert heading in doc, heading


def test_checkpoint_is_active_and_binding(manifest, doc):
    assert manifest["artifact"] == "P4X_CHECKPOINT_A"
    assert manifest["active"] is True
    assert manifest["binding"] is True
    assert "ACTIVE                  = YES" in doc
    assert "BINDING                 = YES" in doc


def test_checkpoint_records_its_source_commit(manifest, doc):
    commit = manifest["generated_from_commit"]
    assert len(commit) == 40
    assert commit == "b3f050bcfb1c8b908e50376b4bf6d6464871da13"
    assert commit in doc


def test_no_production_was_run_and_no_result_exists(manifest, checkpoint_dir):
    assert manifest["successor_verdict"] == "NOT_YET_RUN"
    assert manifest["production_run_performed"] is False
    assert manifest["result_artifacts_generated"] is False
    produced = {p.name for p in (checkpoint_dir / "results").glob("*.json")}
    assert produced == {"checkpoint_a.json"}, produced


def test_p4_original_verdict_is_partial_everywhere(manifest, doc, p4_closure):
    assert p4_closure["verdict"] == "PARTIAL"
    assert manifest["governance"]["P4_ORIGINAL_VERDICT"] == "PARTIAL"
    assert manifest["governance"]["P4_ORIGINAL_VERDICT_IMMUTABLE"] is True
    assert "P4_ORIGINAL_VERDICT     = PARTIAL" in doc


def test_p4x_is_successor_only_and_not_a_stronger_theorem_campaign(manifest):
    assert manifest["governance"]["P4X_IS_SUCCESSOR_ONLY"] is True
    assert manifest["is_stronger_theorem_campaign"] is False
    assert manifest["inherited_theorem"]["strengthening_permitted"] is False
    assert manifest["inherited_theorem"]["reproving_permitted"] is False


def test_destroyed_disposition_audit_is_recorded_without_claiming_its_wording(
        manifest, doc, doc_flat):
    d = manifest["governance"]["destroyed_disposition_audit"]
    assert d["sha256"] == (
        "bda05c9c5ee5df2a7bfbe11ca1fb07432907378299fd36ea0b75cada68ffba34")
    assert d["status"] == "DESTROYED_AND_UNRECOVERABLE"
    assert d["wording_inherited"] is False
    assert d["precedence_rule"]
    assert d["sha256"] in doc
    assert "does not claim to inherit its wording" in doc_flat


def test_governance_is_derived_from_surviving_evidence(manifest):
    derived = manifest["governance"]["derived_independently_from"]
    assert len(derived) >= 4
    joined = " ".join(derived)
    assert "P5_PARTIAL_SHOULD_BE_FINAL" in joined
    assert "P4X and residual" in joined
    assert "zero" in joined and "P4R" in joined
    assert manifest["governance"]["governance_reading"].startswith(
        "no retroactive repair")


def test_inherited_theorem_is_stated_exactly(manifest, doc):
    t = manifest["inherited_theorem"]
    assert t["G1a"] == "g_m'(0) = -Gamma_{D,m,f}"
    assert t["Gamma"] == "Gamma_{D,m,f} = E_0[ A_m sum_{t<=tau} psi(Z_t) ]"
    assert t["score"] == "psi = -f'/f"
    assert t["G1b"] == "F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f})"
    assert t["quantifier"] == "for every fixed m >= 1"
    for fragment in (t["G1a"], t["G1b"], t["score"]):
        assert fragment in doc


def test_inherited_theorem_cites_the_frozen_tree_object(manifest, root):
    import subprocess
    expected = subprocess.check_output(
        ["git", "rev-parse", "HEAD:level4/closure_proofs/p4_theory_generalization"],
        cwd=root, text=True).strip()
    assert manifest["inherited_theorem"]["source_tree_object"] == expected
    assert manifest["governance"]["historical_p4_tree_object"] == expected


def test_assumption_semantics_are_sufficiency_only(manifest, doc_flat):
    a = manifest["assumption_semantics"]
    assert a["A1_A7_are"] == "SUFFICIENT"
    assert a["necessity_claimed"] is False
    assert a["arbitrary_failure_demonstrations_required"] is False
    assert "non-existence" in a["A5_first_moment_boundary"].lower()
    assert "certified" in a["A3_sharpness"].lower()
    assert "**sufficient** assumptions" in doc_flat


def test_all_seven_core_obligations_are_frozen(manifest):
    c = manifest["core_obligations"]
    assert sorted(c) == ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
    assert all(c[k] for k in c)


def test_novelty_and_level4_context_are_frozen(manifest):
    assert manifest["novelty"]["NOVELTY_STATUS"] == "NOT_ESTABLISHED"
    assert manifest["novelty"]["p4x_performs_novelty_work"] is False
    ctx = manifest["level4_context"]
    assert ctx["P5_RESIDUAL_STATUS"] == "DOCUMENTED_LIMITATION"
    assert ctx["LEVEL4_GLOBAL_CLOSURE"] == "NO"
    assert ctx["p4x_is_not_the_only_residual_limitation"] is True
