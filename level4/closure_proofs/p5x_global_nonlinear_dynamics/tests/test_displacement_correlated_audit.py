"""Displacement-correlated derivative audit invariants.  Pre-freeze."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R = json.loads((NS / "displacement_correlated_derivative_audit" / "audit_results.json").read_text())


def test_nothing_binding_was_created_or_run():
    assert R["next_binding_checkpoint"] == "NOT_CREATED"
    assert R["binding_gate_run"] is False and R["sr_prototype_rerun"] is False


def test_scientific_object_and_b1_untouched():
    u = R["reuses"]
    assert u["refit"] is False and u["r6_kernel"] and u["xi_transform"]
    assert u["b1_untouched"] and u["C_SR_cell"] == 216.963


def test_mass_identity_exact_and_defect_not_small():
    m = R["mass"]
    assert m["quadrature_rel_gap"] < 1e-18
    assert m["defect_is_small"] is False and m["defect_1_minus_M"] > 0.4


def test_correlated_identity_is_exact():
    c = R["correlated_identity"]
    assert c["pass"] is True and c["rel_gap"] < 1e-15


def test_displacement_is_order_one_and_path_equals_global():
    d = R["displacement"]
    assert d["sup_abs_delta_plus"] > 0.5
    assert d["path_local_equals_global"] is True
    assert d["q_plus_range"][1] == 1.0     # exact endpoint identity


def test_signed_moments_are_closed_form_with_no_panels():
    m = R["moments"]
    assert m["signed_closed_form_rel_gap"] < 1e-15 and m["z_panels_used"] == 0
    assert abs(m["signed_plus"]) < m["abs_plus"]   # sign change costs 5x


def test_derivative_ladder_diverges():
    h = R["hessian"]
    assert h["sup_ghat_xx"] / h["sup_ghat_x"] > 5
    assert h["sup_ghat_xxx"] / h["sup_ghat_xx"] > 5
    assert h["converged_by_degree"] <= 32     # 12.75 is the true sup, not a hull artifact


def test_correlated_route_is_worse_than_the_baseline():
    w = R["widths"]
    assert w["tightening_plus"] < 1.0 and w["tightening_minus"] < 1.0
    assert w["tightening_second_order_plus"] < w["tightening_plus"]
    assert R["verdicts"]["worse_than_baseline_at_every_grid"] is True


def test_intermediate_magnitude_did_improve_even_though_width_did_not():
    assert R["term_ledger"]["intermediate_reduction"] > 2.0
    assert R["verdicts"]["correlation_class"] == "FAIL"


def test_s1_never_passes_and_is_not_frozen():
    assert all(not g["s1"] for g in R["grid_ladder"])
    v = R["verdicts"]
    assert v["S1_width"] == "FAIL" and v["ready_to_freeze"] is False
    assert v["failure_class"] == "DC-B"


def test_invariants_preserved():
    i = R["invariants"]
    assert i["z_panels"] == 0 and i["softplus_approximations"] == 0
    assert i["r6_fast_kernel_unchanged"] and i["b1_unchanged"]
