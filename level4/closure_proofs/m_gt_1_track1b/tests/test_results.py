from __future__ import annotations

import json
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]


def data():
    return json.loads((CAMPAIGN / "results/replication.json").read_text())


def test_complete_numerical_gate_passes_without_changing_history():
    d = data()
    assert d["verdict"]["decision"] == "PASS"
    assert all(d["verdict"]["gate_checks"].values())
    assert d["track1a"] == "MGT1-TRACK1A-FAILED"
    assert d["track1a_m20_abs_z"] == 3.1302795226595075
    assert d["historical_d2_3"] == "FAILED"


def test_paired_covariance_aware_route_passes_every_check():
    paired = data()["verdict"]["paired"]
    assert all(paired["checks"].values())
    assert paired["max_pathwise_discrepancy"] <= 1e-10
    assert paired["max_batch_mean_discrepancy"] <= 1e-10
    assert np.all(np.array(paired["covariance"]) > 0)
    assert np.all(np.array(paired["correlation"]) >= 0.999999999)
    assert np.all(
        np.array(paired["paired_se"]) <= np.array(paired["naive_independence_se"])
    )


def test_independent_route_uses_global_frozen_gate():
    independent = data()["verdict"]["independent"]
    assert all(independent["checks"].values())
    assert independent["p_value"] >= independent["alpha"] == 0.01
    assert independent["condition_number"] <= 1e12
    assert max(independent["relative_discrepancy"]) <= 0.02


def test_all_batch_keys_are_unique_and_routes_disjoint():
    d = data()
    paired = {tuple(key) for key in d["route_p"]["seed_keys"]}
    direct = {tuple(key) for key in d["route_i_direct"]["seed_keys"]}
    recon = {tuple(key) for key in d["route_i_reconstruction"]["seed_keys"]}
    assert len(paired) == len(direct) == len(recon) == 64
    assert paired.isdisjoint(direct | recon)
    assert direct.isdisjoint(recon)


def test_short_cycle_and_correction_rows_are_complete_and_nonnegative():
    rows = data()["verdict"]["short_cycle"]
    assert {row["m"] for row in rows} == {1, 2, 5, 10, 20, 50}
    assert rows[0]["probability"] == rows[0]["correction"] == 0.0
    assert rows[1]["count"] == rows[1]["correction"] == 0
    assert all(row["probability"] >= 0 and row["correction"] >= 0 for row in rows)


def test_secondary_distinction_preserves_m2_inconsistency_and_m20_m50_replication():
    rows = {row["m"]: row for row in data()["verdict"]["distinction"]}
    assert rows[2]["gain_difference_D_minus_A"] < 0
    assert rows[2]["ci95"][1] < 0
    for m in (20, 50):
        assert rows[m]["gain_difference_D_minus_A"] > 0
        assert rows[m]["ci95"][0] > 0


def test_m1_control_is_exact():
    m1 = data()["verdict"]["m1_control"]
    assert m1["pass"] is True
    assert m1["tau_equal"] and m1["t_tau_equal"] and m1["lags_equal"]
    assert m1["stage_a_stage_d_gain_equal"]
    assert m1["direct_reconstruction_equal"]
    assert m1["maximum_correction"] == 0.0


def test_numeric_decision_authorizes_lean_exactly():
    decision = json.loads((CAMPAIGN / "results/numerical_decision.json").read_text())
    assert decision["decision"] == "PASS"
    assert decision["declaration"] == "NUMERICAL GATE CLOSED — LEAN AUTHORIZED"
    assert decision["lean_authorized"] is True


def test_replication_report_keeps_claim_guards():
    text = (CAMPAIGN / "REPLICATION_REPORT.md").read_text()
    assert "3.130" in text and "frozen failure" in text
    assert "Per-cell z-values are diagnostics only" in text
    assert "NUMERICAL GATE CLOSED — LEAN AUTHORIZED" in text
    assert "D2.3" not in text or "FAILED" in text

