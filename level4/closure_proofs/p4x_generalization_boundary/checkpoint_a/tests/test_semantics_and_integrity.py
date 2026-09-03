"""Route-Q role, CUT-2 split semantics, verdict semantics, STOP rules,
protected-tree integrity, and byte-exact reproducibility of the manifest."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest


# ------------------------------------------------------------- Route-Q role --

def test_route_q_role_is_cross_check_only(manifest, doc):
    r = manifest["route_q_role"]
    assert r["role"] == "INDEPENDENT_CROSS_CHECK_ONLY"
    assert r["may_arbitrate_frozen_detector_cells"] is False
    assert r["may_serve_as_control_variate"] is False
    assert "ROUTE_Q_ROLE = INDEPENDENT_CROSS_CHECK_ONLY" in doc


def test_route_q_arbitration_clause_remains_withdrawn(manifest, doc_flat):
    r = manifest["route_q_role"]
    assert "WITHDRAWN" in r["withdrawn_clause"]
    assert "remains withdrawn" in r["withdrawn_clause"]
    assert "memoryless" in r["reason"]
    assert "520.886133602749" in r["reason"]
    assert "remains withdrawn" in doc_flat


def test_route_q_detector_is_not_a_frozen_detector(manifest, p4_protocol):
    r = manifest["route_q_role"]
    assert r["detector"] == p4_protocol["route_q"]["detector"]
    assert r["c"] == p4_protocol["route_q"]["c"] == 2.0
    assert r["detector"] not in manifest["production_scope"]["detectors"]


# --------------------------------------------------- CUT-2 split semantics --

def test_cut2_a3_half_needs_no_new_compute(manifest):
    x = manifest["gates"]["X7a_a3_moving_support"]
    assert x["new_compute_required"] == "NONE"
    assert "FALSE" in x["semantics"]
    assert "defect 2" in x["semantics"]
    assert len(x["discharged_by"]) == 3
    assert "corroborating" in x["monte_carlo_role"]


def test_cut2_first_moment_half_is_non_existence_not_disagreement(manifest):
    x = manifest["gates"]["X7b_first_moment_non_existence"]
    assert "NON-EXISTENCE" in x["semantics"]
    assert "infinity" in x["semantics"]
    assert x["monte_carlo_large_disagreement_signature_required"] is False
    assert x["new_compute_required"] == "NONE"
    assert "cannot express non-existence" in x["why"]


def test_cut2_does_not_demand_necessity_outside_sufficient_assumptions(manifest):
    a = manifest["assumption_semantics"]
    assert a["necessity_claimed"] is False
    assert a["arbitrary_failure_demonstrations_required"] is False
    assert "must not require failure demonstrations" in a["rule"].lower()


# -------------------------------------------------------- verdict semantics --

def test_verdict_semantics_are_defined_before_results(manifest, doc):
    v = manifest["verdict_semantics"]
    assert set(v) >= {"P4X_CLOSED", "P4X_PARTIAL", "P4X_FAIL"}
    assert v["defined_before_results"] is True
    assert v["intermediate_vocabulary_permitted"] is False
    assert "C1-C7" in v["P4X_CLOSED"]
    assert "no theorem contradiction" in v["P4X_PARTIAL"]
    assert "contradicted" in v["P4X_FAIL"]
    assert "P4X = CLOSED" in doc and "P4X = PARTIAL" in doc and "P4X = FAIL" in doc


def test_closed_requires_every_core_obligation(manifest):
    v = manifest["verdict_semantics"]["P4X_CLOSED"]
    assert "all binding successor obligations" in v
    assert sorted(manifest["core_obligations"]) == [
        "C1", "C2", "C3", "C4", "C5", "C6", "C7"]


def test_scientific_line_semantics_preserve_historical_partial(manifest, doc):
    s = manifest["scientific_line_semantics"]
    closed = s["if_p4x_closed"]
    assert closed["P4_ORIGINAL_VERDICT"] == "PARTIAL"
    assert closed["P4X_SUCCESSOR_VERDICT"] == "CLOSED"
    assert closed["P4_SCIENTIFIC_LINE"] == "CLOSED_BY_SUCCESSOR_CAMPAIGN"
    assert s["original_p4_remains_historically_partial_forever"] is True
    assert "remains historically `PARTIAL` forever" in doc


# -------------------------------------------------------------- STOP rules --

def test_all_seven_stop_rules_are_present(manifest, doc):
    rules = manifest["stop_rules"]
    assert len(rules) == 7
    joined = " ".join(rules).lower()
    for trigger in ("estimator implementation drift", "protected-tree mutation",
                    "precision policy mismatch", "unapproved route substitution",
                    "cost-cap breach", "reproduce historical anchors",
                    "post-result optimisation"):
        assert trigger in joined, trigger
    assert "## 14. STOP rules" in doc


def test_post_result_optimisation_is_forbidden(manifest):
    joined = " ".join(manifest["stop_rules"])
    assert "after seeing a production FAIL" in joined


# ------------------------------------------------------------ protected tree --

def test_protected_tree_manifest_is_complete_and_current(manifest, root):
    tree = manifest["protected_tree_manifest"]
    assert len(tree) >= 30
    for path, expected in tree.items():
        out = subprocess.run(["git", "rev-parse", f"HEAD:{path}"],
                             cwd=root, capture_output=True, text=True)
        assert out.returncode == 0, path
        assert out.stdout.strip() == expected, path


def test_protected_tree_covers_every_priority_and_the_root_readme(manifest):
    tree = manifest["protected_tree_manifest"]
    for required in (
            "level4/closure_proofs/p4_theory_generalization",
            "level4/closure_proofs/p5_nonlinear_dynamics",
            "level4/closure_proofs/p5x_global_nonlinear_dynamics",
            "level4/closure_proofs/m_gt_1_priority1",
            "level4/closure_proofs/sr_derivative_priority2",
            "level4/closure_proofs/m_rho_stability_priority3",
            "level4/closure_proofs/p6_safe_rebaselining",
            "level4/closure_proofs/p7_statistical_consequences",
            "level4/closure_proofs/p8_model_class_robustness",
            "level4/closure_proofs/p8r_temporal_integrity_repair",
            "level4/closure_proofs/p9_final_synthesis",
            "level4/closure_proofs/p9r_final_synthesis_repair",
            "rebaseguard-lean", "rebaseguard-proof", "README.md"):
        assert required in tree, required


def test_no_protected_path_is_inside_the_p4x_namespace(manifest):
    for path in manifest["protected_tree_manifest"]:
        assert "p4x_generalization_boundary" not in path, path


def test_source_artifact_hashes_are_current(manifest, checkpoint_dir):
    import hashlib
    closure = checkpoint_dir.parents[1]
    p4 = closure / "p4_theory_generalization"
    r0 = checkpoint_dir.parent / "r0_variance_reduction_pilot"
    paths = {
        "P4_PROTOCOL.json": p4 / "configs" / "P4_PROTOCOL.json",
        "p4_correspondence.json": p4 / "results" / "correspondence.json",
        "p4_closure_decision.json": p4 / "results" / "closure_decision.json",
        "r0_pilot.json": r0 / "results" / "pilot.json",
        "r0_tail_sweep.json": r0 / "results" / "tail_sweep.json",
        "r0_cost_calibration.json": r0 / "results" / "cost_calibration.json",
        "r0_cut2_cut3_cost.json": r0 / "results" / "cut2_cut3_cost.json",
    }
    for name, path in paths.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert manifest["source_artifact_hashes"][name] == digest, name


def test_historical_anchors_match_the_frozen_artifact(manifest, p4_closure):
    a = manifest["historical_anchors"]
    assert a["p4_verdict"] == p4_closure["verdict"] == "PARTIAL"
    assert a["p4_failed_gates"] == sorted(
        k for k, v in p4_closure["gates"].items() if not v)
    assert len(a["p4_failed_gates"]) == 3


def test_checkpoint_writes_only_inside_the_p4x_namespace(root):
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root, capture_output=True, text=True, check=True)
    prefix = "level4/closure_proofs/p4x_generalization_boundary/"
    for line in out.stdout.splitlines():
        path = line[3:].strip().strip('"')
        assert path.startswith(prefix), line


def test_frozen_p4_tree_is_untouched(root):
    out = subprocess.run(
        ["git", "status", "--porcelain",
         "level4/closure_proofs/p4_theory_generalization"],
        cwd=root, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""


# ------------------------------------------------------------ reproducibility --

def test_manifest_is_reproducible_byte_for_byte(checkpoint_dir, tmp_path):
    """Re-running the generator must reproduce the manifest exactly."""
    target = checkpoint_dir / "results" / "checkpoint_a.json"
    before = target.read_bytes()
    backup = tmp_path / "checkpoint_a.json"
    backup.write_bytes(before)
    try:
        proc = subprocess.run(
            [sys.executable, str(checkpoint_dir / "build_checkpoint.py")],
            cwd=checkpoint_dir, capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        assert target.read_bytes() == before
    finally:
        target.write_bytes(backup.read_bytes())


def test_manifest_is_valid_json_and_self_describing(checkpoint_dir):
    payload = json.loads(
        (checkpoint_dir / "results" / "checkpoint_a.json").read_text())
    assert payload["schema"] == "rebaseguard.p4x-checkpoint-a.v1"
