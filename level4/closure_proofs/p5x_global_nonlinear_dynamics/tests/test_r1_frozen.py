"""Checkpoint-C (R1) tests.  These must not reveal the benchmark outcome."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R1 = NS / "compute_optimization_r1"
RA = NS / "certified_method_repair_ra"
ROOT = NS.parents[2]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_classification_is_a_bound_refactor_not_a_science_change():
    audit = (R1 / "NEUTRALITY_AUDIT.md").read_text()
    assert "CLASSIFICATION      = CERTIFIED_BOUND_REFACTOR" in audit
    assert "SCIENTIFIC_TARGET_CHANGED = NO" in audit
    assert "SCIENTIFIC_SCOPE_CHANGED  = NO" in audit


def test_neutrality_audit_covers_every_required_element():
    audit = (R1 / "NEUTRALITY_AUDIT.md").read_text()
    for item in ("detector", "window `m`", "Fredholm equation", "kernel `K_e`",
                 "reward `rho_{1,e}`", "state space", "stopping convention",
                 "enclosure meaning", "theorem consumer interface",
                 "stop-gate semantics"):
        assert item in audit, item


def test_proof_discharges_the_seven_obligations_and_refuses_the_open_claims():
    proof = (R1 / "PROOF.md").read_text()
    for lemma in ("L-R1.1", "L-R1.2", "L-R1.3", "L-R1.4", "L-R1.5", "L-R1.6", "L-R1.7"):
        assert lemma in proof, lemma
    flat = proof.replace("\n", " ")
    assert "sup_e E[tau|e] = E[tau|0]" in flat and "open" in flat
    assert "monotonicity in `e` is unproved" in flat
    assert "one-sided" in flat and "coupling" in flat


def test_spec_keeps_the_ra_cell_and_threshold():
    spec = (R1 / "R1_FROZEN_SPEC.md").read_text()
    assert "e-cell   = [0.24, 0.26]" in spec
    assert "SPEEDUP >= 4.0            ->  STRONG_PASS" in spec
    assert "0.014176477298268092" in spec          # baseline cited, not altered
    ra = (RA / "RA_STOP_GATE.md").read_text()
    assert "e ∈ [0.24, 0.26]" in ra or "[0.24, 0.26]" in ra


def test_spec_freezes_the_derived_parameters_before_the_run():
    spec = (R1 / "R1_FROZEN_SPEC.md").read_text()
    for token in ("C_opt   = 220.707518709682314", "n_sub   = 8",
                  "h_sub   = 0.00125", "closure = C (2 a h_sub + b2 h_sub^2)"):
        assert token in spec, token


def test_prediction_is_pre_registered():
    spec = (R1 / "R1_FROZEN_SPEC.md").read_text()
    assert "predicted half-width  = 0.00886" in spec
    assert "predicted SPEEDUP     = 5.0" in spec


def test_no_r1_result_at_the_anchor():
    forbidden = ["r1_benchmark.json", "r1_selftest.json"]
    present = [f for f in forbidden if (NS / "results" / f).exists()]
    assert not present, f"R1 results must not exist at the anchor: {present}"


def test_ra_reference_implementation_is_untouched():
    manifest = json.loads(
        (NS / "results" / "integrity" / "protected_tree_manifest_r1_pre.json").read_text())
    for rel, digest in manifest["ra_reference_implementation_frozen"].items():
        assert _sha(NS / rel) == digest, rel


def test_r1_digests_match_files():
    for name in ("R1_PROTOCOL_DIGEST.json", "R1_SOURCE_MANIFEST.json"):
        doc = json.loads((R1 / name).read_text())
        for rel, rec in doc["files"].items():
            assert _sha(R1 / rel) == rec["sha256"], rel


def test_prior_results_are_intact():
    old = json.loads((NS / "results" / "stop_gate_cell.json").read_text())
    assert old["stop_gate"]["verdict"] == "FAIL"
    ra = json.loads((NS / "results" / "ra_stop_gate.json").read_text())
    assert ra["stop_gate"]["verdict"] == "PASS"
    assert ra["achieved_half_width"] == 0.014176477298268092
    assert ra["stop_gate"]["frozen_threshold"] == 0.2


def test_historical_incident_still_recorded():
    doc = (NS / "INCIDENT_EXTERNAL_TREE_CHANGE.md").read_text()
    assert "P5X_RESPONSIBLE    = NO" in doc


def test_range_is_not_shortened_by_this_campaign():
    spec = (R1 / "R1_FROZEN_SPEC.md").read_text()
    assert "will not shorten `[0, 12]`" in spec


def test_no_lean_sources_yet():
    assert not list(NS.rglob("*.lean"))
