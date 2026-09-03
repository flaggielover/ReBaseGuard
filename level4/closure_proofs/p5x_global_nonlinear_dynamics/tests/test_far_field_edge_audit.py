"""Far-field minus-edge localization audit invariants.  Pre-freeze; nothing frozen."""
from __future__ import annotations
import json, math
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R = json.loads((NS / "far_field_wminus_edge_audit" / "audit_results.json").read_text())


def test_nothing_binding_created_or_run():
    assert R["next_binding_checkpoint"] == "NOT_CREATED"
    assert R["binding_campaign_executed"] is False
    assert R["historical_r8_mutated"] is False and R["production_run"] is False


def test_edge_geometry_is_exact():
    g = R["edge_geometry"]
    assert g["q_minus_at_l"] == 1.0 and g["exact"] is True
    assert "e^{-s}" in g["law"]


def test_weight_peak_is_not_at_the_edge_for_the_hard_drifts():
    w = R["weight"]
    assert w["peak_z"] == "-e-1"
    assert "5.76" in w["peak_interior_when"]


def test_heaviest_cells_have_the_worst_concentration():
    c = {(x["e"], x["zeta_minus"]): x for x in R["weight"]["concentration"]}
    heavy, light = c[(4, 0.01)], c[(4, 0.90)]
    assert heavy["mass"] > 1000 * light["mass"]
    assert heavy["s0_0.5"] < light["s0_0.5"]


def test_split_optimum_is_shallow_and_modest():
    s = {x["s0"]: x for x in R["s0_sweep_e4"]}
    assert max(x["gain"] for x in s.values()) < 2.5
    assert s[0.05]["R_local"] < 0.02 and s[2.0]["R_local"] > 1000   # locality vs mass


def test_split_rule_was_not_retuned_per_drift():
    assert R["split_rule"]["re_tuned_per_drift"] is False
    assert R["early_stop"]["further_drifts_optimised"] is False


def test_route_fails_the_grid_cap():
    w = R["worst"]
    assert w["G_new"] > w["G_max"] and w["over_by"] > 3
    assert R["verdicts"]["route"] == "FAIL"


def test_gain_is_weakest_where_it_is_needed_most():
    r = {x["e"]: x for x in R["results"]}
    assert r[3.0]["G_new"] == max(x["G_new"] for x in r.values())
    assert r[3.0]["gain"] < r[6.9]["gain"]


def test_global_range_grows_with_drift():
    g = R["verdicts"]["R_global_grows_with_drift"]
    assert g["5.0"] > 100 * g["0.25"]


def test_cost_remains_infeasible_and_other_blocker_recorded():
    c = R["cost"]
    assert "INFEASIBLE" in c["after"] and c["conservative_le_500"] is False
    assert "0.072" in c["independent_blocker_remaining"]
