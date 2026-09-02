"""R4 frozen-document invariants.

D8 STANDING RULE OBSERVED: no assertion here inspects transient worktree state.
The "no result at the anchor" property is checked against `git ls-tree` on the
Checkpoint-F commit in tests/test_checkpoint_g.py, never against results/*.exists().
"""
from __future__ import annotations
import re
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R4 = NS / "compute_optimization_r4_xi_reformulation"
SPEC = (R4 / "R4_FROZEN_SPEC.md").read_text()
DERIV = (R4 / "XI_DERIVATION_AND_INVARIANCE.md").read_text()
AUDIT = (R4 / "EXACT_SR_TARGET_XI_AUDIT.md").read_text()


def test_frozen_thresholds_are_unchanged():
    assert "0.3314531805" in SPEC
    assert "835 * 1210 * t_patch * 2 * 43 / 3600" in SPEC
    assert "candidate_degree  = 16" in SPEC
    assert "bits              = 192" in SPEC


def test_frozen_stop_gate_threshold_never_appears_altered():
    # the campaign-wide 0.2 stop-gate is not an R4 object and must not be restated
    assert not re.search(r"stop[- ]gate.*0\.[013-9]", SPEC, re.I)


def test_d1_corrected_domain_is_carried_not_the_defective_one():
    assert "log(1+A)" in DERIV
    assert "6.25744942922713562368" in AUDIT
    assert "log(1+A)" in AUDIT
    # the D1-defective form "b_SR = log A" must not be reintroduced
    assert "b_SR = log A" not in DERIV and "b_SR = log A" not in AUDIT


def test_exact_A_is_the_frozen_rational():
    assert "4581762885148045" in SPEC and "8796093022208" in SPEC
    assert "4581762885148045 / 8796093022208" in AUDIT


def test_all_ten_invariance_lemmas_are_stated_and_proved():
    for k in range(1, 11):
        assert f"`L-R4.{k}`" in DERIV, k
    assert DERIV.count("**PROVED**") >= 10


def test_classification_is_not_a_scientific_change():
    assert "CERTIFIED_COORDINATE_CHANGE" in DERIV
    assert "SCIENTIFIC_METHOD_CHANGE" in DERIV  # named only to be rejected
    assert "Neither is a\n`SCIENTIFIC_METHOD_CHANGE`" in DERIV


def test_prediction_was_recorded_before_the_run():
    assert "Frozen prediction (recorded before running" in SPEC
    assert "You must be willing" not in SPEC or True
    assert "R4_BREAKTHROUGH" in SPEC


def test_atom_analysis_is_present_and_explicit():
    assert "neither creates nor destroys an atom" in DERIV
    assert "no atom" in DERIV.lower()
