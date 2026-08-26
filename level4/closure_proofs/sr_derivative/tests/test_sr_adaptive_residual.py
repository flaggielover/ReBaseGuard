"""Focused guards for adaptive SR residual refinement and Bernstein bounds."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from flint import arb, ctx


CAMPAIGN = Path(__file__).resolve().parents[1]
CERTIFICATE = CAMPAIGN / "certificate"
RESULTS = CAMPAIGN / "results"
sys.path.insert(0, str(CERTIFICATE))

from sr_adaptive_residual import InnovationInterval, Rectangle  # noqa: E402
from certify_global_residual_a import (  # noqa: E402
    EXPECTED_FUNDAMENTAL_CELLS,
    cell_key,
    cells,
    geometry_and_algebra_checks,
)
from sr_bernstein import bernstein_absolute_bound  # noqa: E402
from taylor_model import Model  # noqa: E402


def test_exact_dyadic_innovation_bisection_has_no_gap():
    with ctx.workprec(128):
        parent = InnovationInterval(-arb(1) / arb(8), -arb(1) / arb(16))
        left, right = parent.bisect()
        assert left.lower == parent.lower
        assert left.upper == right.lower
        assert right.upper == parent.upper


def test_state_quadtree_children_cover_parent_area_exactly():
    with ctx.workprec(128):
        parent = Rectangle(arb(0), arb(1), arb(0), arb(1))
        children = parent.bisect()
        assert len(children) == 4
        assert sum(
            (
                (child.plus_upper - child.plus_lower)
                * (child.minus_upper - child.minus_lower)
                for child in children
            ),
            arb(0),
        ).contains(1)


def test_bernstein_convex_hull_bounds_centered_square():
    with ctx.workprec(128):
        # p(dx,dy)=dx^2 on dx in [-1,1]. Bernstein coefficients are 1,-1,1.
        model = Model({(2, 0): arb(1)}, 2, 2)
        bound, coefficients = bernstein_absolute_bound(model, arb(1), arb(1))
        assert bound.contains(1)
        assert coefficients[0][0].contains(1)
        assert coefficients[1][0].contains(-1)
        assert coefficients[2][0].contains(1)


def test_interval_bernstein_coefficients_round_outward():
    with ctx.workprec(128):
        uncertain = arb(1).union(arb(2))
        model = Model({(1, 0): uncertain}, 2, 1)
        bound, coefficients = bernstein_absolute_bound(model, arb(1), arb(1))
        assert bound >= 2
        assert coefficients[0][0].contains(-1)
        assert coefficients[0][0].contains(-2)
        assert coefficients[1][0].contains(1)
    assert coefficients[1][0].contains(2)


def test_degree_pruned_model_multiplication_preserves_truncated_convolution():
    with ctx.workprec(128):
        left_2d = Model({(0, 0): arb(2), (1, 0): arb(3), (0, 2): arb(5)}, 2, 2)
        right_2d = Model({(0, 0): arb(7), (0, 1): arb(11), (2, 0): arb(13)}, 2, 2)
        product_2d = left_2d * right_2d
        assert product_2d.coefficients == {
            (0, 0): arb(14),
            (0, 1): arb(22),
            (2, 0): arb(26),
            (1, 0): arb(21),
            (1, 1): arb(33),
            (0, 2): arb(35),
        }

        left_3d = Model({(0, 0, 0): arb(2), (1, 0, 0): arb(3)}, 3, 2)
        right_3d = Model(
            {(0, 0, 0): arb(5), (0, 1, 0): arb(7), (0, 0, 2): arb(11)},
            3,
            2,
        )
        product_3d = left_3d * right_3d
        assert product_3d.coefficients == {
            (0, 0, 0): arb(10),
            (0, 1, 0): arb(14),
            (0, 0, 2): arb(22),
            (1, 0, 0): arb(15),
            (1, 1, 0): arb(21),
        }


def test_adaptive_pilot_proves_both_split_directions_tighten():
    pilot = json.loads((RESULTS / "sr_residual_adaptive_pilot.json").read_text())
    assert pilot["status"] == "PILOT_PASS"
    assert all(pilot["checks"].values())
    assert arb(pilot["innovation_split"]["tightening_factor"]["ball"]) > 200
    assert arb(pilot["state_split"]["tightening_factor"]["ball"]) > 4


def test_first_patch_certificate_is_continuum_scoped_not_global():
    result = json.loads(
        (RESULTS / "sr_residual_first_patch_adaptive.json").read_text()
    )
    assert result["status"] == "FIRST_PATCH_CERTIFIED"
    assert result["sampled_grid_used"] is False
    assert result["global_reachable_cover_complete"] is False
    assert result["checks"]["exact_innovation_cover"] is True
    assert result["checks"]["patch_engineering_target_met"] is True
    assert result["bernstein"]["convex_hull_bound_used"] is True
    assert arb(result["certified_patch_residual_a"]["ball"]) < arb(5) / arb(1_000_000)


def test_representative_patch_pilots_pass_without_claiming_global_cover():
    result = json.loads(
        (RESULTS / "sr_residual_adaptive_patch_pilots.json").read_text()
    )
    assert result["status"] == "PILOT_GATES_PASS"
    assert result["global_reachable_cover_complete"] is False
    assert all(result["checks"].values())
    assert set(result["patches"]) == {
        "easy_interior",
        "difficult_plus_boundary",
    }
    target = arb(5) / arb(1_000_000)
    for patch in result["patches"].values():
        assert patch["status"] == "PATCH_CERTIFIED"
        assert patch["exact_innovation_cover"] is True
        assert patch["sampled_grid_used"] is False
        assert arb(patch["certified_residual_a"]) < target
        component_sum = (
            arb(patch["polynomial_bernstein"])
            + arb(patch["direct_remainder"])
            + arb(patch["reward_remainder"])
            + arb(patch["integration_remainder"])
        )
        assert component_sum.overlaps(arb(patch["certified_residual_a"]))


def test_parent_patch_pilot_records_state_width_blocker():
    result = json.loads(
        (RESULTS / "sr_residual_parent_patch_pilot.json").read_text()
    )
    assert result["status"] == "PARENT_PATCH_BLOCKED"
    assert result["global_reachable_cover_complete"] is False
    assert all(result["checks"].values())
    target = arb(5) / arb(1_000_000)
    for patch in result["patches"].values():
        assert patch["status"] == "PATCH_FAIL"
        assert patch["exact_innovation_cover"] is True
        assert patch["sampled_grid_used"] is False
        assert arb(patch["certified_residual_a"]) > target
        assert arb(patch["integration_remainder"]) > target
        assert patch["final_intervals"] == 256


def test_global_fundamental_cover_enumeration_is_exact_and_unique():
    cover = cells()
    assert len(cover) == EXPECTED_FUNDAMENTAL_CELLS == 1210
    assert len({cell_key(cell) for cell in cover}) == len(cover)
    assert all(0 <= minus <= plus < 64 for plus, minus in cover)
    assert all(plus + minus <= 68 for plus, minus in cover)
    assert (63, 5) in cover
    assert (63, 6) not in cover


def test_global_cover_geometry_and_candidate_symmetry_checks_pass():
    candidate = json.loads((RESULTS / "arb_candidate.json").read_text())
    assert all(geometry_and_algebra_checks(candidate).values())
