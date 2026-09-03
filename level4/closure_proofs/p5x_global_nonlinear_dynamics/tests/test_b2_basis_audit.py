"""B2 stable-basis feasibility audit invariants.  Pre-freeze; no gate verdict."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R = json.loads((NS / "b2_basis_feasibility_audit" / "audit_results.json").read_text())


def test_no_checkpoint_j_and_no_binding_gate():
    assert R["checkpoint_j"] == "NOT_CREATED"
    assert R["binding_gate_run"] is False


def test_candidate_reused_exactly_never_refit():
    c = R["candidate"]
    assert c["reused_exactly"] is True and c["refit"] is False and c["degree"] == 16
    assert R["invariants"]["candidate_refit"] is False


def test_bernstein_solves_the_coefficient_scale_problem():
    s = R["coefficient_scale"]
    assert s["max_abs_monomial"] == 2.012154e10
    assert s["max_abs_bernstein"] < 2.0
    assert s["improvement"] > 1e9
    assert s["equality_verified"] is True


def test_ghat_hull_is_sharp_on_the_worst_cell():
    g = R["ghat_range_worst_cell"]
    assert abs(g["overshoot"] - 1.0) < 1e-6
    assert g["bernstein_width"] < g["monomial_width"]


def test_basis_image_route_was_tested_and_rejected():
    """CASE 2 is real; the naive Bernstein reading does not work."""
    b = R["ke_routes"]["B-B1_basis_images"]
    assert b["verdict"] == "REJECTED" and b["case"] == 2
    assert b["recombined_radius"] > R["reference_values"]["old_direct_enclosure"]


def test_selected_route_beats_both_prior_attempts():
    assert R["ke_routes"]["B-B3_centred_bernstein"]["verdict"] == "SELECTED"
    assert R["improvements"]["vs_old_direct_at_64"] > 1e6
    assert R["improvements"]["vs_failed_centred_at_64"] > 1e7


def test_degree_elevation_helps_and_then_saturates():
    d = R["ke_routes"]["B-B3_centred_bernstein"]["degree_elevation"]
    assert d["16"]["Mx"] > 10 and d["32"]["Mx"] < 1.3
    assert abs(d["64"]["residual"] - d["256"]["residual"]) < 1e-3


def test_target_met_by_basis_change_not_by_refinement():
    sweep = {r["grid"]: r for r in R["resolution_sweep"]}
    assert sweep[64]["residual"] < 1e-1          # basis alone: 1.97e6x gain
    assert sweep[256]["residual"] <= 1e-2        # <=1e-2 target met
    assert sweep[256]["residual"] / sweep[64]["residual"] > 0.2   # refinement is a small factor


def test_architecture_invariants_preserved():
    i = R["invariants"]
    assert i["z_panels"] == 0 and i["softplus_approximations"] == 0
    assert i["r6_fast_kernel_unchanged"] and i["xi_transform_unchanged"]
    assert i["recurrence_unchanged"]


def test_all_audit_lemmas_pass_and_case_is_one():
    assert set(R["lemmas"].values()) == {"PASS"}
    assert R["architecture_case"] == 1
    assert R["b1_compatibility"] == "UNAFFECTED"
