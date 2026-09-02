"""R5 frozen-document invariants.

D8 STANDING RULE OBSERVED: nothing here inspects transient worktree state.
Anchor-phase properties live in tests/test_checkpoint_h.py against git objects.
"""
from __future__ import annotations
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R5 = NS / "compute_optimization_r5_scaled_tail"
DER = (R5 / "SCALED_TAIL_DERIVATION.md").read_text()
SPEC = (R5 / "R5_FROZEN_SPEC.md").read_text()


def test_r4_p3_threshold_is_not_weakened():
    assert "1e12" in SPEC and "NOT weakened" in SPEC
    assert "2.1356e17" in SPEC


def test_all_nine_lemmas_stated_and_proved():
    for k in range(1, 10):
        assert f"`L-R5.{k}`" in DER, k
    assert DER.count("**PROVED**") >= 9


def test_class_is_a_representation_repair_not_a_scope_change():
    assert "CERTIFIED_NUMERICAL_REPRESENTATION_REPAIR" in DER
    import re
    assert re.search(r"not a\s+scientific method change", DER, re.I)
    assert re.search(r"not a detector revision", DER, re.I)


def test_r4_gate_remains_fail_and_is_not_reinterpreted():
    assert "R4's frozen gate remains **FAIL**" in DER


def test_exponent_identity_is_stated():
    assert "k^2/2 - k e - (x + e - k)^2 / 2  =  k x - (x + e)^2 / 2" in DER


def test_noncancellation_constants_are_exact_and_d1_corrected():
    assert "0.9961640701886751383284382" in DER      # W = 2(c_SR - b_SR)
    assert "3.13312228929" in DER                    # regime B/C ratio floor
    assert "0.19078688886760390794" in DER           # regime D difference floor


def test_correspondence_criterion_is_rigorous_vs_rigorous():
    assert "RIGOROUS  vs  RIGOROUS" in SPEC
    assert "DIAGNOSTIC ONLY" in SPEC
    assert "Explicitly forbidden" in SPEC


def test_no_retry_ladder_was_frozen():
    assert "There is none." in SPEC


def test_prediction_recorded_before_implementation():
    assert "Frozen prediction (recorded before implementation)" in SPEC
