"""Phase-3 tests: the stop-gate artifact is the declared cell, the verdict was
computed from the frozen threshold, and nothing was quietly re-run."""
from __future__ import annotations

import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
GATE = json.loads((NS / "results" / "stop_gate_cell.json").read_text())


def test_gate_ran_the_declared_cell():
    assert GATE["detector"] == "cusum"
    assert GATE["m"] == 1
    assert GATE["e_cell"] == [0.24, 0.26]
    assert GATE["is_certified_cell_enclosure"] is True
    assert GATE["diagnostic_radius"] is None


def test_gate_used_the_declared_parameters():
    assert GATE["precision_bits"] == 256
    assert GATE["phi_taylor_order"] == 50
    assert GATE["candidate"]["degree"] == 12
    assert GATE["model"] == {"k_num": 1, "k_den": 2, "h_num": 5, "h_den": 1}
    assert GATE["coverage"]["sampled_grid_used"] is False
    assert GATE["coverage"]["reachable_continuum_complete"] is True


def test_threshold_was_not_reinterpreted():
    assert GATE["stop_gate"]["frozen_threshold"] == 0.2
    half = GATE["stop_gate"]["achieved_half_width"]
    expected = "PASS" if half <= 0.2 else "FAIL"
    assert GATE["stop_gate"]["verdict"] == expected


def test_gate_failed_and_no_cover_was_launched():
    assert GATE["stop_gate"]["verdict"] == "FAIL"
    # a full cover would have produced many cell artifacts
    cells = list((NS / "results").glob("cover_*"))
    assert not cells, f"a full cover must not have been launched: {cells}"


def test_resolvent_was_proved_not_imported():
    res = GATE["resolvent"]
    assert res["imported_constant"] is False
    assert res["monotonicity_in_e_used"] is False


def test_failure_is_documented_with_a_measured_cause():
    doc = (NS / "STOP_GATE.md").read_text()
    assert "STOP_GATE            = FAIL" in doc
    assert "interval dependency blow-up" in doc
    assert "4.9608e+41" in doc          # the measured amplification
    assert "R-A" in doc and "R-B" in doc  # both repairs recorded
    handoff = (NS / "FAILURE_HANDOFF.md").read_text()
    assert "Do not reuse" in handoff or "Do not reuse\n" in handoff


def test_selftest_anchors_the_implementation():
    doc = json.loads((NS / "results" / "selftest_e0.json").read_text())
    assert doc["reward_equals_certified_r_a_at_e0"] is True
    assert doc["residuals_agree"] is True
    assert doc["ghat_origin_is_zero_to_1e-12"] is True


def test_diagnosis_isolates_both_failure_mechanisms():
    """The point-e run separates the two mechanisms of STOP_GATE.md section 4."""
    doc = json.loads((NS / "results" / "stop_gate_diagnosis.json").read_text())
    assert "DIAGNOSTIC ONLY" in doc["role"]
    point = next(r for r in doc["rows"] if r["e_ball_radius"] == 0.0)
    cell_half = GATE["stop_gate"]["achieved_half_width"]
    # mechanism 4.2 (interval dependency): collapsing the ball buys ~42 orders
    assert point["half_width"] < cell_half / 1e40
    # mechanism 4.1 (phi truncation with drift): a point e still misses 0.2
    assert point["half_width"] > 0.2
    doc_text = (NS / "STOP_GATE.md").read_text()
    assert "two independent mechanisms" in doc_text


def test_phi_truncation_mechanism_is_recorded():
    doc = (NS / "STOP_GATE.md").read_text()
    for value in ("3.75603e-7", "4.17665e-5", "7.04071e+44"):
        assert value in doc, value
