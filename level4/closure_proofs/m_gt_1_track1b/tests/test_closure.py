from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]


def test_lean_build_and_axiom_audit_hooks_are_complete():
    main = (CAMPAIGN / "lean/MGtOneTrack1B.lean").read_text()
    audit = (CAMPAIGN / "lean/AxiomAudit.lean").read_text()
    required = {
        "directTerm_eq_fixed_add_shortCorrection",
        "shortCorrection_nonneg",
        "integral_direct_eq_fixed_add_correction",
        "derivative_spine_of_dominated",
    }
    assert all(f"theorem {name}" in main for name in required)
    assert all(f"#print axioms RebaseguardLean.Track1B.{name}" in audit for name in required)
    assert not re.search(r"\b(sorry|admit|axiom)\b", main)


def test_reproduce_script_has_all_required_gates_and_valid_shell():
    script = CAMPAIGN / "reproduce.sh"
    text = script.read_text()
    assert os.access(script, os.X_OK)
    assert "m_gt_1_track1a/reproduce.sh" in text
    assert "run_replication.py\" --resume" in text
    assert "MGtOneTrack1B.lean" in text and "AxiomAudit.lean" in text
    subprocess.run(["bash", "-n", str(script)], check=True)


def test_claim_guard_preserves_machine_checked_boundary():
    theorem = (CAMPAIGN / "THEOREM.md").read_text()
    correspondence = (CAMPAIGN / "LEAN_CORRESPONDENCE.md").read_text()
    assert "not claim that the entire concrete" in theorem
    assert "not a fully instantiated CUSUM theorem" in correspondence
    assert "measurability" in correspondence
    assert "uniform integrable" in correspondence


def test_lean_axiom_allowlist_is_exactly_documented():
    text = (CAMPAIGN / "LEAN_CORRESPONDENCE.md").read_text()
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    found = set(re.findall(r"(?:propext|Classical\.choice|Quot\.sound)", text))
    assert found == allowed


def test_numerical_decision_and_lean_gate_order_are_consistent():
    decision = json.loads((CAMPAIGN / "results/numerical_decision.json").read_text())
    assert decision["lean_authorized"] is True
    assert decision["declaration"] == "NUMERICAL GATE CLOSED — LEAN AUTHORIZED"
    protocol = (CAMPAIGN / "PROTOCOL.md").read_text()
    progress = (CAMPAIGN / "PROGRESS_CAPSULE.md").read_text()
    assert "Only after numerical authorization" in protocol
    assert "NUMERICAL GATE CLOSED — LEAN AUTHORIZED" in progress
