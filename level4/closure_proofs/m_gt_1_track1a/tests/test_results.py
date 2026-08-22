from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]


def data():
    return json.loads((CAMPAIGN / "results/replication.json").read_text())


def test_recorded_failure_is_only_the_frozen_pooled_decomposition_check():
    verdict = data()["verdict"]
    assert verdict["decision"] == "FAIL"
    failed = {name for name, passed in verdict["checks"].items() if not passed}
    assert failed == {"decomposition_pooled_all_within_3se"}


def test_distinction_passes_preselected_effect_cells():
    rows = {row["m"]: row for row in data()["verdict"]["distinction"]}
    for m in (20, 50):
        row = rows[m]
        assert row["gain_difference_ci95"][0] > 0
        assert all(value > 0 for value in row["replicate_gain_differences"])
        assert row["gain_difference_D_minus_A"] > 0


def test_every_requested_m_is_reported_with_effect_and_short_cycle_fields():
    rows = data()["verdict"]["distinction"]
    assert {row["m"] for row in rows} == {1, 2, 5, 10, 20, 50}
    for row in rows:
        assert "standardized_gain_difference" in row
        assert "short_cycle_probability" in row
        assert "short_correction" in row
        assert "component_reconstruction" in row


def test_m2_rare_observed_correction_is_not_serialized_as_zero():
    row = next(row for row in data()["verdict"]["distinction"] if row["m"] == 2)
    assert row["short_cycle_count"] == 1
    assert row["short_correction"] > 0
    assert "zero-SE replicate edge case" in row["short_correction_pooling"]


def test_pathwise_decomposition_and_correction_sign_pass():
    d = data()
    for route in ("stage_d_direct", "stage_d_reconstruction"):
        for rep in d[route]:
            assert rep["max_pathwise_decomposition_error"] <= 1e-10
            assert rep["minimum_pathwise_correction"] >= -1e-14
            direct = np.array(rep["direct_gain"]["estimate"])
            fixed = np.array(rep["fixed_denominator_gain"]["estimate"])
            correction = np.array(rep["short_correction"]["estimate"])
            assert np.allclose(direct, fixed + correction, atol=1e-12, rtol=0)


def test_exact_independent_decomposition_failure_cell_is_preserved():
    rows = {row["m"]: row for row in data()["verdict"]["decomposition"]}
    assert rows[20]["abs_z"] > 3.0
    assert rows[20]["abs_z"] < 4.0
    assert all(row["abs_z"] <= 3.0 for m, row in rows.items() if m != 20)
    assert max(max(row["replicate_abs_z"]) for row in rows.values()) < 4.0


def test_m1_and_rho_controls_pass():
    verdict = data()["verdict"]
    shared = verdict["m1_control"]["shared_stream"]
    assert shared["tau_equal"] and shared["gain_integrand_equal"]
    assert shared["maximum_correction"] == 0.0
    assert verdict["m1_control"]["abs_z"] <= 4.0
    assert verdict["m1_control"]["prior_agreement_abs_z"] <= 4.0
    assert verdict["rho_scaling"]["max_abs_error"] == 0.0


def test_csv_has_one_complete_row_per_m():
    with (CAMPAIGN / "results/replication.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 6
    assert {int(row["m"]) for row in rows} == {1, 2, 5, 10, 20, 50}


def test_decision_artifact_preserves_scoped_failure():
    decision = json.loads((CAMPAIGN / "results/decision.json").read_text())
    assert decision["decision"] == "MGT1-TRACK1A-FAILED"
    assert decision["stage_a_stage_d_distinction"] == "PASS"
    assert decision["decomposition_independent"] == "FAIL"
    assert decision["lean"].startswith("NOT STARTED")
    assert decision["historical_d2_3"] == "FAILED"
    assert decision["overall_level4_decision_made"] is False


def test_claim_guards_and_lean_stop_are_explicit():
    report = (CAMPAIGN / "REPLICATION_REPORT.md").read_text()
    lean = (CAMPAIGN / "LEAN_CORRESPONDENCE.md").read_text()
    theorem = (CAMPAIGN / "THEOREM.md").read_text()
    assert "MGT1-TRACK1A-FAILED" not in theorem or "machine-checked" in theorem
    assert "Historical Stage-D D2.3" not in report or "FAILED" in report
    assert "NOT STARTED" in lean
    assert "no track 1a machine-checked theorem is claimed" in theorem.lower()
