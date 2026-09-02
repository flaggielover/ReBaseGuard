"""Checkpoint-E (R3) tests.

D8/D9 process rule (fourth repetition already recorded): these tests assert
DOCUMENT CONTENT and GIT/MANIFEST HASHES only.  No test here inspects transient
worktree state such as `results/*.exists()`.  Anchor-phase properties are checked
against git objects in test_checkpoint_f.py.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R3 = NS / "compute_optimization_r3_sr_symbolic"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_exact_sr_target_frozen_with_corrected_domain():
    doc = (R3 / "EXACT_SR_TARGET.md").read_text()
    assert "log(1+A) = 6.25744942922713551796607132378" in doc
    assert "c_SR = log A + 1/2" in doc
    assert "pre-update" in doc and "not on the stored state" in doc
    assert "may **not** change" in doc


def test_architecture_audit_uses_measured_incumbent_numbers():
    doc = (R3 / "R3_ARCHITECTURE_AUDIT.md").read_text()
    for tok in ("1210", "96,295", "50,947", "79.6", "grid = 64"):
        assert tok in doc, tok
    assert "not the heuristic" in doc or "measured, not heuristic" in doc.replace("\n", " ")


def test_all_eight_lemmas_present_and_proved():
    proof = (R3 / "PROOF.md").read_text()
    for i in range(1, 9):
        assert f"`L-R3.{i}`" in proof, i
    assert proof.count("**PROVED**") >= 8
    assert "No load-bearing lemma failed" in proof


def test_no_empirical_monotonicity_and_no_scope_change():
    proof = (R3 / "PROOF.md").read_text()
    assert "sup_e E[tau|e] = E[tau|0]" in proof and "is used anywhere" in proof
    spec = (R3 / "R3_FROZEN_SPEC.md").read_text()
    assert "None is a method or scope change" in spec


def test_feasibility_cell_is_the_worst_patch_not_a_convenient_one():
    spec = (R3 / "R3_FROZEN_SPEC.md").read_text()
    assert "p17_m11" in spec
    assert "worst" in spec and "not a convenient one" in spec.replace("\n", " ")


def test_pass_criteria_and_bands_frozen():
    spec = (R3 / "R3_FROZEN_SPEC.md").read_text()
    for tok in ("n_z * t_panel <= 0.3314531805", "R3_BREAKTHROUGH", "PRACTICALLY_VIABLE",
                "predicted n_z", "Retry ladder", "**None.**"):
        assert tok in spec, tok


def test_multiplier_correction_recorded():
    doc = (R3 / "cusum_measurement_lane" / "CUSUM_MULTIPLIER_MEASUREMENT.md").read_text()
    assert "43x" in doc and "previously ASSUMED 11x" in doc
    assert "understated by `19%`" in doc
    spec = (R3 / "R3_FROZEN_SPEC.md").read_text()
    assert "* 43 / 3600" in spec


def test_r3_digests_match_files():
    for name in ("R3_PROTOCOL_DIGEST.json", "R3_SOURCE_MANIFEST.json"):
        doc = json.loads((R3 / name).read_text())
        for rel, rec in doc["files"].items():
            assert _sha(R3 / rel) == rec["sha256"], rel


def test_prior_campaign_files_frozen_by_manifest():
    m = json.loads((NS / "results" / "integrity" / "protected_tree_manifest_r3_pre.json").read_text())
    for rel, digest in m["prior_campaign_files_frozen"].items():
        assert _sha(NS / rel) == digest, rel


def test_prior_results_intact():
    r2 = json.loads((NS / "results" / "r2_benchmark.json").read_text())
    assert r2["speed"]["measured_speedup"] == 14.448401737437928
    r1 = json.loads((NS / "results" / "r1_benchmark.json").read_text())
    assert r1["achieved_half_width"] == 0.008045668639929672
    ra = json.loads((NS / "results" / "ra_stop_gate.json").read_text())
    assert ra["achieved_half_width"] == 0.014176477298268092
    old = json.loads((NS / "results" / "stop_gate_cell.json").read_text())
    assert old["stop_gate"]["verdict"] == "FAIL"
