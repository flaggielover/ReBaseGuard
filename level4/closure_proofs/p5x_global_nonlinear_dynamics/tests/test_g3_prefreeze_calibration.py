"""G3 pre-freeze calibration invariants.  Nothing frozen; nothing historical changed."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R = json.loads((NS / "g3_prefreeze_calibration" / "audit_results.json").read_text())


def test_nothing_binding_created_or_executed():
    assert R["next_binding_checkpoint"] == "NOT_CREATED"
    assert R["binding_campaign_executed"] is False
    assert R["historical_r8_mutated"] is False
    assert R["successor_spec_drafted"] is False


def test_one_over_G_scaling_confirmed():
    r = R["grid_scaling"]["ratios_512_over_1024"]
    assert all(abs(x - 2.0) < 0.01 for x in r)
    assert "CONFIRMED" in R["grid_scaling"]["exact_1_over_G"]


def test_e_independence_is_refuted():
    ei = R["e_independence"]
    assert ei["verdict"] == "REFUTED"
    assert ei["ratio"] > 1000
    assert ei["measured_max"] > 100 * ei["k_used_by_g3_audit"]


def test_the_g3_audit_single_cell_value_understated_W():
    u = R["e_independence"]["single_cell_understatement_at_e025"]
    assert u["worst_over_cells"] > u["audit"]


def test_far_field_is_genuinely_harder_not_only_a_loose_bound():
    t = {x["e"]: x for x in R["true_gradient_vs_bound"]}
    assert t[8.0]["true_sum"] > 50          # the TRUE gradient really is large
    assert all(x["looseness"] > 30 for x in t.values())   # and the bound is also loose


def test_bisection_does_not_rescue_overflow():
    a = R["adaptive_cover"]
    assert a["bisection_helps"] is False
    assert a["overflow_cells"] > 1000


def test_most_of_the_cover_overflows_the_grid_cap():
    a = R["adaptive_cover"]
    assert a["overflow_measure_fraction"] > 0.8
    assert a["worst_required_G"] > a["G_max"]
    assert a["accepted_cells"] < 50


def test_g3_audit_cost_is_superseded():
    c = R["cost"]
    assert c["optimistic_g3_audit"] == 54.95
    assert "INVALID" in c["optimistic_status"]
    assert c["cost_class"] == "INFEASIBLE"


def test_prefreeze_not_ready_with_the_right_blocker():
    p = R["pre_freeze"]
    assert p["ready"] is False
    assert p["PF_D"] == "FAIL" and p["PF_E"] == "FAIL" and p["PF_F"] == "FAIL"
    assert p["PF_A"] == "PASS" and p["PF_B"] == "PASS" and p["PF_C"] == "PASS"
    assert "PF-E" in p["blocker"]


def test_near_zero_and_far_tail_have_non_certifier_routes_recorded():
    reg = {tuple(x["range"]): x for x in R["regions"]}
    assert "R(0)=0" in reg[(0, 0.072)]["note"]
    assert "P5X-T3" in reg[(10, 12)]["note"]
