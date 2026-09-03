"""Direct-residual oscillation audit invariants.  Pre-freeze; nothing frozen."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R = json.loads((NS / "b2_direct_residual_oscillation_audit" / "audit_results.json").read_text())


def test_no_binding_checkpoint_or_gate():
    assert R["next_binding_checkpoint"] == "NOT_CREATED"
    assert R["binding_gate_run"] is False


def test_exact_object_reused_and_b1_untouched():
    u = R["reuses"]
    assert u["candidate"].startswith("exact R8")
    assert u["r6_kernel"] and u["xi_transform"] and u["b1_untouched"]
    assert u["C_SR_cell"] == 216.963
    assert R["invariants"]["candidate_refit"] is False


def test_gradient_is_exact_by_h_squared_decay():
    s = R["gradient"]["fd_step_sweep"]
    assert s["1e-5"]/s["1e-6"] > 90 and s["1e-6"]/s["1e-7"] > 90 and s["1e-7"]/s["1e-8"] > 90
    assert R["gradient"]["correspondence_error"] <= 1e-10
    assert R["gradient"]["boundary_terms_combined_before_enclosure"] is True


def test_combining_alone_gives_no_gain_in_the_monomial_basis():
    c = R["control_naive_vs_combined"]
    assert abs(c["combining_gain"] - 1.0) < 1e-6
    assert c["combined_radius"] == c["naive_sum_of_radii"]


def test_edge_structural_fact_tightens_the_boundary_hull():
    s = R["structural_fact"]
    assert s["hull_edge_plus"] < s["hull_full"]


def test_candidate_derivative_is_essentially_exact_but_kernel_term_is_not():
    b = R["bernstein_bounded_gradient"]
    assert b["ghat_x_cell_hull_width"] < 1e-6
    assert b["K_Eplus_width"] > 0.5 and b["K_Eminus_width"] > 0.4
    assert b["looseness_plus"] > 50


def test_width_and_cost_never_both_close():
    lad = {r["grid"]: r for r in R["grid_ladder"]}
    assert all(not r["meets_f3"] for g, r in lad.items() if r["cost_class"] != "COST_FAIL")
    assert all(r["cost_class"] == "COST_FAIL" for g, r in lad.items() if r["meets_f3"])


def test_required_delta_matches_the_r8_formula():
    exact = (0.2 - 0.01) / 216.963
    assert abs(R["required_delta_for_F3"] - exact) / exact < 1e-6


def test_not_frozen_and_blocker_classified():
    v = R["verdicts"]
    assert v["S1_width"] == "FAIL" and v["S2_cost"] == "FAIL"
    assert v["ready_to_freeze"] is False and v["blocker"] == "DR-B4"


def test_invariants_preserved():
    i = R["invariants"]
    assert i["z_panels"] == 0 and i["softplus_approximations"] == 0
    assert i["r6_fast_kernel_unchanged"] and i["b1_unchanged"]
