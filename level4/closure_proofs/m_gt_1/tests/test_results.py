from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]


def data():
    return json.loads((CAMPAIGN / "results/correspondence.json").read_text())


def test_recorded_complete_gate_fails_without_erasing_primary_pass():
    d = data()
    assert d["verdict"]["decision"] == "FAIL"
    assert d["verdict"]["checks"]["primary_pooled_all_within_3se"] is True
    assert d["verdict"]["checks"]["primary_each_rep_all_within_4se"] is True


def test_exact_failed_checks_are_preserved():
    checks = data()["verdict"]["checks"]
    failed = {k for k, v in checks.items() if not v}
    assert failed == {
        "short_cycles_observed_for_every_m_gt_1",
        "stage_a_stage_d_distinct_over_5se",
    }


def test_all_raw_step_grid_cells_are_in_csv():
    with (CAMPAIGN / "results/correspondence.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2 * 4 * 8
    assert {float(r["h"]) for r in rows} == {0.1, 0.05, 0.025, 0.0125}
    assert {int(r["m"]) for r in rows} == {1, 2, 5, 10, 20, 50, 75, 100}


def test_route_a_and_route_b_seed_families_are_disjoint():
    d = data()
    a = {tuple(k[:2]) for rep in d["route_a"] for k in rep["seed_keys"]}
    b = {
        tuple(step[which][:2])
        for rep in d["route_b"] for step in rep["steps"].values()
        for which in ("plus_seed_prefix", "minus_seed_prefix")
    }
    assert a == {(2026082204, 1)}
    assert b == {(2026082204, 2)}
    assert a.isdisjoint(b)


def test_rho_scaling_is_exact_in_recorded_control():
    assert data()["rho_scaling"]["max_abs_error"] == 0.0


def test_short_cycle_correction_is_observed_from_m5_onward():
    d = data()
    for rep in d["route_a"]:
        assert np.all(np.array(rep["short_correction"])[2:] > 0)
        assert rep["max_pathwise_decomposition_error"] <= 1e-9


def test_finite_difference_convergence_checks_pass():
    v = data()["verdict"]
    assert v["shrink_counts"] == {"0.1_to_0.05": 8, "0.05_to_0.025": 8}
    assert 1.25 <= v["median_coarse_order"] <= 2.75


def test_stage_a_stage_d_distinction_failure_is_not_hidden():
    rows = data()["stage_a_stage_d_distinction"]
    m20 = [r for r in rows if r["m"] == 20]
    m100 = [r for r in rows if r["m"] == 100]
    assert all(r["difference_D_minus_A"] < 0 for r in rows)
    assert all(r["abs_z"] < 5 for r in m20)
    assert all(r["abs_z"] > 5 for r in m100)


def test_decision_artifact_is_consistent():
    d = json.loads((CAMPAIGN / "results/decision.json").read_text())
    assert d["decision"] == "MGT1-THEOREM-PARTIAL"
    assert d["primary_derivative_correspondence"] == "PASS"
    assert d["complete_numerical_gate"] == "FAIL"
    assert d["historical_d2_3"] == "FAILED"
    assert d["closes_previous_m_gt_1_requirement"] is False


def test_final_report_has_required_claim_guards():
    text = (CAMPAIGN / "FINAL_REPORT.md").read_text()
    assert "MGT1-THEOREM-PARTIAL" in text
    assert "D2.3 remains `FAILED`" in text
    assert "does **not** close" in text
    assert "overall Level-4 closure" in text


def test_lean_and_certificate_stop_states_are_explicit():
    lean = (CAMPAIGN / "lean/README.md").read_text()
    cert = (CAMPAIGN / "certificate/STATUS.md").read_text()
    assert "NOT STARTED" in lean
    assert "NOT STARTED" in cert


def test_richardson_never_drives_the_decision():
    d = data()
    assert d["richardson_status"] == "SECONDARY DIAGNOSTIC ONLY"
    assert "richardson" not in " ".join(d["verdict"]["checks"]).lower()
