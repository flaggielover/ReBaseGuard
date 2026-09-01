"""Scientific consistency: every headline number in the documents is re-derived
from the machine-readable artifacts here, so a document and its evidence cannot
drift apart silently.

These tests read ``results/*.json``; they run no simulation.
"""
import json
from pathlib import Path

import numpy as np
import pytest

R = Path(__file__).resolve().parents[1] / "results"
PRIMARY = "cusum_m3"
CELLS = ("cusum_m1", "cusum_m2", "cusum_m3", "cusum_m5",
         "sr_m1", "sr_m2", "sr_m3", "sr_m5")


def _load(name):
    p = R / name
    if not p.exists():
        pytest.skip(f"{name} not produced yet")
    return json.loads(p.read_text())


# --- Stage 1 foundation ----------------------------------------------------

def test_x1_bit_identity_and_x3_reproduction():
    d = _load("correspondence.json")
    assert all(r["tau_identical"] for r in d["x1_bit_identity"])
    assert max(r["max_abs_e_diff"] for r in d["x1_bit_identity"]) == 0.0
    assert len(d["x1_bit_identity"]) == 24
    x3 = d["x3_p7_reproduction"]
    assert len(x3) == 40
    assert all(r["p6_ci_overlaps_p7_ci"] for r in x3)
    assert max(abs(r["z_vs_p7"]) for r in x3) < 3.0


def test_convention_a_residual_is_exactly_zero():
    d = _load("correspondence.json")
    assert max(r["max_abs_update_residual"] for r in d["x2_convention_a"]) == 0.0
    assert any(r["fraction_truncated_windows"] > 0 for r in d["x2_convention_a"])


def test_c_beta_matches_the_preregistered_radius():
    d = _load("correspondence.json")["c_beta"]
    assert abs(d["cusum"]["0.25"]["c"] - 0.2816) < 5e-4
    assert abs(d["sr"]["0.25"]["c"] - 0.2656) < 5e-4


# --- calibration -----------------------------------------------------------

def test_calibration_r2_and_selection_inflation():
    cal = _load("calibration.json")
    for cell in CELLS:
        e = cal[cell]
        assert e["final"]["r2"] > 0.94, cell
        m = e["final"]["m"]
        assert e["v_bar"] > 2.0 * (1.0 / m), cell      # selection inflation
        assert 0.15 < e["rho_flat"] < 0.30, cell


def test_jensen_gap_decreases_with_m():
    cal = _load("calibration.json")
    for det in ("cusum", "sr"):
        gaps = [cal[f"{det}_m{m}"]["jensen_gap_rel"] for m in (1, 2, 3, 5)]
        assert gaps == sorted(gaps, reverse=True), (det, gaps)


# --- the T6-C(iii) criterion ----------------------------------------------

def test_plugin_criterion_holds_in_every_cell():
    d = _load("robust_plugin_criterion.json")
    for cell, v in d.items():
        assert v["criterion_satisfied"], cell
        assert v["plugin_error"] < 0.15 * v["jensen_gap"], cell


# --- the headline comparison ----------------------------------------------

def _b2star(a, cell):
    return a["b2_star"][cell]["best"]


@pytest.mark.parametrize("family", ("eval", "replay"))
def test_saw_beats_b2star_in_every_family_at_matched_cost(family):
    a = _load(f"analysis_{family}.json")
    ic = _load(f"confirm_ic_{family}.json")["cells"]
    dl = _load(f"confirm_delay_{family}.json")["cells"]
    for cell in CELLS:
        ctl = _b2star(a, cell)
        b = a["breadth"][cell]["SAW_M"]
        assert b["Fresh_matched"], cell
        assert b["Arl0"]["lo"] > 0, (cell, "Arl0 not resolved")
        assert b["Rms"]["hi"] < 0, (cell, "Rms not resolved")
        rows = dl[f"{cell}_d1.0"]
        p0, p1, n = rows[ctl]["Dtail100"], rows["SAW_M"]["Dtail100"], rows[ctl]["n"]
        se = np.sqrt(p0 * (1 - p0) / n + p1 * (1 - p1) / n)
        assert (p1 - p0) / se < -1.96, (cell, "Dtail100 not resolved")
        assert ic[cell]["SAW_M"]["Fresh"] == ic[cell][ctl]["Fresh"], cell


def test_primary_cell_headline_numbers():
    a = _load("analysis_eval.json")
    c = a["primary_cell"]["comparisons"]["SAW_M"]
    assert a["primary_cell"]["cell"] == PRIMARY
    assert c["Dtail100"]["rel"] < -0.09 and c["Dtail100"]["hi"] < 0
    assert c["Arl0"]["rel"] > 0.04 and c["Arl0"]["lo"] > 0
    assert c["Fresh"]["rel"] == 0.0
    assert c["Wbar"]["rel"] > 0.5                     # reuses MORE
    assert c["FreshProp"]["rel"] < 0.0                # cheaper under the sensitivity
    assert c["vs_B3"]["Dtail100"]["rel"] < -0.25      # gate G-A threshold
    assert c["vs_B3"]["Dtail100"]["hi"] < -0.25


# --- the ablation ladder ---------------------------------------------------

def test_sensor_ablation_is_indistinguishable_from_the_incumbent():
    a = _load("analysis_eval.json")
    flat = a["primary_cell"]["comparisons"]["SAW_A_flat"]["Dtail100"]
    assert flat["lo"] < 0.0 < flat["hi"], "flat should NOT resolve against B2*"


def test_ladder_is_monotone_in_information_on_arl0_and_rms():
    lad = _load("analysis_eval.json")["ablation_ladder"]
    for cell in CELLS:
        d = lad[cell]
        arl = [d[p]["Arl0"] for p in
               ("SAW_A_flat", "SAW_A_naive", "SAW_A_no_tau", "SAW_M")]
        rms = [d[p]["Rms"] for p in
               ("SAW_A_flat", "SAW_A_naive", "SAW_A_no_tau", "SAW_M")]
        assert arl == sorted(arl), (cell, arl)
        assert rms == sorted(rms, reverse=True), (cell, rms)
        assert d["Z1_oracle_saw"]["Arl0"] > d["SAW_M"]["Arl0"], cell


def test_heuristic_nulls_do_not_beat_the_incumbent():
    a = _load("analysis_eval.json")["primary_cell"]["comparisons"]
    for p in ("B6_zbar_two_level", "B11_conf_gate"):
        assert a[p]["Dtail100"]["rel"] > 0.0, p          # worse than B2*


# --- robustness ------------------------------------------------------------

def test_frontier_improves_arl0_and_rms_in_every_cell():
    d = _load("robust_frontier.json")
    assert len(d) == 18
    for cell, v in d.items():
        rows = v["rows"]
        saw = next(p for p in rows if p.startswith("SAW"))
        b2 = {p: rows[p] for p in rows if p.startswith("B2_")}
        best = min(b2, key=lambda p: b2[p]["Dtail100"])
        assert rows[saw]["Arl0"] > rows[best]["Arl0"], cell
        assert rows[saw]["Rms"] < rows[best]["Rms"], cell
        assert rows[saw]["Fresh"] == rows[best]["Fresh"], cell


def test_finite_reference_regime_reproduces_in_every_cell():
    d = _load("robust_finite_reference.json")
    assert len(d) == 18
    for cell, rows in d.items():
        b2 = {p: rows[p] for p in rows if p.startswith("B2_")}
        best = min(b2, key=lambda p: b2[p]["Dtail100"])
        assert rows["SAW_M"]["Arl0"] > rows[best]["Arl0"], cell
        assert rows["SAW_M"]["Rms"] < rows[best]["Rms"], cell
        assert rows["SAW_M"]["Dtail100"] < rows[best]["Dtail100"], cell


def test_tail_events_meet_the_preregistered_floor_where_a_gate_uses_them():
    dl = _load("confirm_delay_eval.json")["cells"]
    for cell in CELLS:
        rows = dl[f"{cell}_d1.0"]
        for p in ("SAW_M", "B3_full_reuse"):
            assert rows[p]["n_events_100"] >= 200, (cell, p)


def test_full_reuse_reproduces_the_p7_finite_cycle_collapse():
    ic = _load("confirm_ic_eval.json")["cells"]
    for cell in CELLS:
        assert ic[cell]["B3_full_reuse"]["Coll"] < 0.025, cell
        assert ic[cell]["SAW_M"]["Coll"] > 0.15, cell


# --- provenance ------------------------------------------------------------

def test_protected_tree_is_untouched():
    d = _load("protected_tree.json")
    assert d["tracked_files_modified_vs_HEAD"] == []
    assert d["n_protected_tracked_files"] > 2000
    assert d["head"] == "bb03c0ea9ea34060c992b6d7f0390de6a3cf8108"


def test_p5_verdict_is_recorded_and_partial():
    d = _load("p5_verdict.json")
    assert "FINAL_P5_VERDICT               = PARTIAL" in d["verdict_block_verbatim"]
    assert d["repository_checkpoint"] == "bb03c0ea9ea34060c992b6d7f0390de6a3cf8108"
    assert len(d["premises_p6_must_not_use"]) == 7


def test_gate_e_records_its_ordering_defect():
    d = _load("gate_e.json")
    assert d["threshold"]["option_selected"].startswith("E3")
    assert "ORDERING DEFECT" in d["threshold"]["recorded_defect"]
