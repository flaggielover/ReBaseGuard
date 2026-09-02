"""R-A' result checkpoint tests.  The first FAIL must stay intact."""
from __future__ import annotations

import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
RA = NS / "certified_method_repair_ra"
GATE = json.loads((NS / "results" / "ra_stop_gate.json").read_text())
SELF = json.loads((NS / "results" / "ra_selftest.json").read_text())
DIAG = json.loads((NS / "results" / "ra_diagnostics.json").read_text())
OLD = json.loads((NS / "results" / "stop_gate_cell.json").read_text())


def test_first_certified_method_failure_is_untouched():
    assert OLD["stop_gate"]["verdict"] == "FAIL"
    assert OLD["achieved_half_width"] > 1e40
    assert OLD["stop_gate"]["frozen_threshold"] == 0.2
    assert "STOP_GATE            = FAIL" in (NS / "STOP_GATE.md").read_text()


def test_selftest_passed_before_the_gate():
    assert SELF["verdict"] == "PASS"
    for k in ("S1_coefficient_identity", "S2_reward_accuracy", "S3_weight_accuracy",
              "S4_residual_containment", "S5_origin_is_zero"):
        assert SELF["checks"][k] is True, k


def test_gate_used_the_same_cell_and_threshold():
    assert GATE["detector"] == "cusum" and GATE["m"] == 1
    assert GATE["e_cell"] == [0.24, 0.26] == OLD["e_cell"]
    assert GATE["cell_unchanged_from_failed_gate"] is True
    assert GATE["stop_gate"]["frozen_threshold"] == 0.2 == OLD["stop_gate"]["frozen_threshold"]


def test_verdict_is_mechanical():
    half = GATE["stop_gate"]["achieved_half_width"]
    assert GATE["stop_gate"]["verdict"] == ("PASS" if half <= 0.2 else "FAIL")
    assert GATE["achieved_half_width"] == half


def test_no_retry_and_frozen_subcell_rule_held():
    sc = GATE["subcells"]
    assert sc["tiles_cell_exactly"] is True
    assert sc["n_sub"] == 40
    assert GATE["certified_solves"] == 3 * sc["n_sub"]
    assert GATE["resolvent"]["imported_constant"] is False
    assert GATE["resolvent"]["monotonicity_in_e_used"] is False


def test_far_field_truncation_is_drift_independent():
    balls = [r["ra_kernel_truncation"]["ball"] for r in DIAG["far_field_truncation"]]
    assert len(set(balls)) == 1, "Device 1 must be exactly e-free"
    assert {r["e"] for r in DIAG["far_field_truncation"]} == {0, 0.26, 6.5, 12.0}


def test_dependency_is_reported_as_still_present():
    """Recentring did NOT fix mechanism 2; the document must not claim it did."""
    rows = DIAG["radius_scan"]
    zero = next(r for r in rows if r["e_ball_radius"] == 0.0)
    positive = [r for r in rows if r["e_ball_radius"] > 0]
    worst = max(positive, key=lambda r: r["e_ball_radius"])
    assert float(zero["polynomial_residual"]["ball"].strip("[]").split(" +/-")[0]) < 1e-4
    assert float(worst["polynomial_residual"]["ball"].strip("[]").split(" +/-")[0]) > 1e30
    doc = (RA / "RA_STOP_GATE.md").read_text()
    assert "NOT fixed by recentring" in doc


def test_prediction_falsification_is_recorded():
    doc = (RA / "RA_STOP_GATE.md").read_text()
    assert "falsified on the optimistic side" in doc


def test_full_cover_not_launched_or_authorized():
    assert not list((NS / "results").glob("cover_*"))
    proj = (RA / "RA_COVER_PROJECTION.md").read_text()
    assert "FULL_COVER_AUTHORIZED = NO" in proj


def test_no_lean_sources_yet():
    assert not list(NS.rglob("*.lean"))
