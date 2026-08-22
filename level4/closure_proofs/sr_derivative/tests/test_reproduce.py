from __future__ import annotations

import os
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]


def test_reproducer_has_every_required_gate_and_valid_shell():
    script = CAMPAIGN / "reproduce.sh"
    text = script.read_text()
    assert os.access(script, os.X_OK)
    assert "m_gt_1/tests" in text
    assert "m_gt_1_track1a/tests" in text
    assert "m_gt_1_track1b/tests" in text
    assert '"$CAMPAIGN/tests"' in text
    assert "audit_arb_attempt.py" in text
    assert "SRDerivative.lean" in text
    assert "AxiomAudit.lean" in text
    assert "verify_level_4.sh" in text
    subprocess.run(["bash", "-n", str(script)], check=True)


def test_reproducer_verifies_retained_numerics_without_rerunning_or_tuning():
    text = (CAMPAIGN / "reproduce.sh").read_text()
    assert "run_correspondence.py" not in text
    assert "--quick" not in text
    assert "Arb OPEN-attempt audit is not byte-stable" in text
    assert "Gamma_SR > 2: CONFIRMATORY NUMERICAL ONLY" in text
    assert "rigorous SR local-instability certificate: OPEN" in text

