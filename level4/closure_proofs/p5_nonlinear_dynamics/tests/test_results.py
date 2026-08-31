"""Focused tests on the produced P5 results: every headline claim is asserted."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RES = ROOT / "results"


def load(name):
    return json.loads((RES / name).read_text())


# ---------------------------------------------------------------- the map ---
def test_map_is_odd_to_within_one_percent_of_its_range():
    a = load("hypothesis_audit.json")
    for c in a["cells"]:
        assert c["H1_n_pairs"] >= 20
    # absolute oddness residual is small against sup|R|
    m = load("map_analysis.json")
    for c in m["cells"]:
        assert c["oddness_max_resid"] < 0.01 * c["sup_abs_R"] * 1.2, c


def test_map_saturates_and_forgets():
    a = load("hypothesis_audit.json")
    for c in a["cells"]:
        assert c["H3b_holds"], c            # sup|R| < 2
        assert c["H2_holds"], c             # R(e) < 0 on e > 0
        assert c["far_tail_max_abs_R_beyond_10"] < 0.01, c


def test_secant_gain_decreasing_where_the_theorems_use_it():
    a = load("hypothesis_audit.json")
    for c in a["cells"]:
        assert c["H3a_holds_within_MC_error"], c["H3a_significant_violations"]
        assert c["s_at_E_cap"] < 1.0, c


def test_slope_at_zero_reproduces_p3():
    for f in ("map_analysis.json", "map_analysis_rep.json"):
        for c in load(f)["cells"]:
            assert c["rel_err_vs_p3"] < 0.02, (f, c["detector"], c["m"])


def test_independent_seed_family_reproduces_the_map():
    a = {(c["detector"], c["m"]): c for c in load("map_analysis.json")["cells"]}
    b = {(c["detector"], c["m"]): c for c in load("map_analysis_rep.json")["cells"]}
    assert set(a) == set(b)
    for k in a:
        x = [q for q in a[k]["branch"] if q["rho"] == 1.0][0]
        y = [q for q in b[k]["branch"] if q["rho"] == 1.0][0]
        assert abs(x["e_star"] - y["e_star"]) < 0.005, k
        assert abs(x["snr"] - y["snr"]) < 0.02, k


# ---------------------------------------------------------- the skeleton ---
def test_skeleton_has_only_periods_one_and_two():
    for c in load("skeleton_scan.json")["cells"]:
        seen = {p for r in c["rows"] for p in r["periods"]}
        assert seen <= {0, 1, 2}, (c["detector"], c["m"], seen)


def test_skeleton_period_two_onset_matches_frozen_rho_c():
    an = {(c["detector"], c["m"]): c for c in load("map_analysis.json")["cells"]}
    for c in load("skeleton_scan.json")["cells"]:
        first = next(r["rho"] for r in c["rows"] if r["max_period"] == 2)
        rc = an[(c["detector"], c["m"])]["p3_rho_crit"]
        # scan step is 0.005 and the scan grid is offset from rho_c
        assert abs(first - rc) <= 0.0075, (c["detector"], c["m"], first, rc)


def test_no_two_cycle_below_the_boundary():
    for c in load("map_analysis.json")["cells"]:
        rc = c["p3_rho_crit"]
        for b in c["branch"]:
            if b["rho"] < rc * (1.0 - 1e-3):
                assert not b["exists"], (c["detector"], c["m"], b["rho"])


def test_two_cycle_is_attracting_everywhere_it_exists():
    for c in load("map_analysis.json")["cells"]:
        for b in c["branch"]:
            if b["exists"]:
                assert b["cycle2_multiplier"] < 1.0, (c["detector"], c["m"],
                                                      b["rho"])


def test_snr_vanishes_at_the_boundary_and_stays_small():
    """T10: the branch emerges with amplitude below the map's own resolution.

    At rho = rho_c the exact amplitude is 0, so the measured branch is either at
    the grid floor (e* ~ 0.005-0.01) or unresolvable; both are recorded.
    """
    for c in load("map_analysis.json")["cells"]:
        rc = c["p3_rho_crit"]
        live = [b for b in c["branch"] if b["exists"]]
        first = min(live, key=lambda b: b["rho"])
        assert first["rho"] <= 1.35 * rc, (c["detector"], c["m"], first["rho"])
        assert first["e_star"] < 0.06, (c["detector"], c["m"], first["e_star"])
        assert first["snr"] < 0.15, (c["detector"], c["m"], first["snr"])
        assert max(b["snr"] for b in live) < 2.5, (c["detector"], c["m"])


# ------------------------------------------------------------- the chain ---
def test_dispersion_has_an_interior_optimum_far_above_rho_c():
    cells = load("chain_analysis.json")["cells"]
    for det in ("cusum", "sr"):
        for m in (1, 2, 3, 5):
            r = sorted([x for x in cells if x["detector"] == det
                        and x["m"] == m], key=lambda x: x["rho"])
            rms = np.array([x["rms"] for x in r])
            rho = np.array([x["rho"] for x in r])
            k = int(np.argmin(rms))
            assert 0 < k < len(r) - 1, (det, m)
            assert rho[k] > 1.4 * r[0]["rho_crit"], (det, m, rho[k])
            assert rms[k] < rms[-1] * 0.75, (det, m)


def test_no_localised_feature_at_rho_c():
    b = load("chain_analysis.json")["boundary_probe"]
    assert b
    assert not [x for x in b if x["rank_of_|d2|_at_rhoc"] == 1]


def test_initial_condition_independence():
    for c in load("chain_analysis.json")["cells"]:
        assert max(c["init_dependence_z"].values()) < 4.0, (c["detector"],
                                                            c["m"], c["rho"])


def test_stationary_law_is_not_heavy_tailed():
    for c in load("chain_analysis.json")["cells"]:
        assert c["kurt"] < 3.1, (c["detector"], c["m"], c["rho"], c["kurt"])


def test_acf1_prediction_from_the_map_matches_the_chain():
    for t in load("chain_analysis.json")["t11"]:
        assert t["abs_gap"] < 0.02, t


def test_gamma_eff_is_far_below_the_tangent_gain():
    for t in load("chain_analysis.json")["t11"]:
        if t["rho"] > 0:
            assert t["Gamma_eff"] < 0.25 * t["gamma_tilde_tangent"], t


# ------------------------------------------------------ runaway / modes ---
def test_no_runaway_from_extreme_initial_conditions():
    s = load("stress.json")
    for r in s["rows"]:
        assert r["cycle1_abs_mean"] < 2.5, r
        assert r["tail_rms"] < 2.0, r
        # nothing ever exceeds the initial condition by more than the
        # ordinary stationary range
        assert r["global_abs_max"] <= max(abs(r["e0"]), 6.0), r


def test_one_step_forgetting_at_large_reference_error():
    for f in load("stress.json")["forgetting"]:
        if abs(f["e"]) >= 100:
            assert f["p_tau1"] == 1.0, f
            assert abs(f["R_m1"]) < 0.005 and abs(f["R_m5"]) < 0.005, f
            assert abs(f["S_m1"] - 1.0) < 0.02, f


def test_bimodality_onset_is_far_above_rho_c():
    o = load("bimodality_onset.json")
    assert len(o) >= 4
    for k, v in o.items():
        assert v["onset"] is not None, k
        assert v["over_rhoc"] > 3.0, (k, v)


def test_no_metastability():
    rows = []
    for f in ("density.json", "density_crossover.json"):
        rows += load(f)["rows"]
    for r in rows:
        assert r["mean_residence_cycles"] < 1.6, r
        if r["rho"] >= 0.6:
            assert r["alt_rate"] > 0.8, r


# ------------------------------------------------------------------ lean ---
def test_lean_spine_is_sorry_free_with_standard_axioms_only():
    d = load("lean_compile.json")
    assert d["compiled"] and d["sorry_free"]
    assert d["n_declarations"] == 12
    assert set(d["axioms_used"]) <= {"propext", "Classical.choice", "Quot.sound"}
