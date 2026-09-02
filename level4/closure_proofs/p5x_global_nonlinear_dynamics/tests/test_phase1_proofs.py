"""Phase-1 tests: the human proofs are present, the defects are registered, and
the documents that Phase 1 produced say what the protocol requires."""
from __future__ import annotations

import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]


def test_all_mandated_lemmas_are_proved():
    text = (NS / "PROOF.md").read_text()
    for lemma in ("L1", "L2", "L3", "L5", "L6"):
        assert f"## {lemma} " in text, f"missing proof section for {lemma}"
    # the mandate excluded L4/L7/L8; they must not be silently claimed
    assert "`L4`, `L7` and `L8` are not\ndischarged here" in text


def test_every_lemma_section_answers_the_seven_questions():
    text = (NS / "PROOF.md").read_text()
    assert text.count("Dependencies, detector-specificity, certified input, non-claims") == 5
    assert text.count("does NOT prove") >= 5


def test_defects_are_registered_not_silently_repaired():
    reg = (NS / "DEFECT_REGISTER.md").read_text()
    for did in ("D1", "D2", "D3", "D4"):
        assert f"## `{did}`" in reg
    frozen = (NS / "FROZEN_THEOREM.md").read_text()
    # the frozen file must still carry the defective text: no silent edit
    assert "b_SR = log A" in frozen


def test_sr_domain_defect_has_a_witness():
    doc = json.loads((NS / "feasibility" / "results" / "sr_domain_check.json").read_text())
    assert doc["status"] == "FEASIBILITY_PROBE_NON_AUTHORITATIVE"
    assert doc["frozen_b_SR_falsified"] is True
    assert doc["within_corrected_b_SR"] is True
    assert doc["max_live_stored_state"] > doc["log_A_frozen_b_SR"]


def test_mechanism_premise_closure_has_no_monte_carlo():
    audit = (NS / "DEPENDENCY_AUDIT.md").read_text()
    assert "No node in that closure is `EMPIRICAL_ONLY`" in audit


def test_stop_gate_cell_was_declared_before_the_run():
    spec = (NS / "STOP_GATE_SPEC.md").read_text()
    assert "[0.24, 0.26]" in spec
    assert "least** favourable cell" in spec
    assert "achieved half-width <= 0.2" in spec


def test_lean_stage_discipline_respected():
    compat = (NS / "LEAN_COMPATIBILITY.md").read_text()
    assert "no Lean is written" in compat
    lean_files = list(NS.rglob("*.lean"))
    assert not lean_files, f"Lean sources are premature at this stage: {lean_files}"
