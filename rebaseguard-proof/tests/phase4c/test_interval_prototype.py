from __future__ import annotations

from flint import arb

from rebaseguard_certify.arb_backend import workprec
from rebaseguard_phase4c.interval_prototype import (
    arb_continuation_bounds,
    arb_transition,
    ball_width,
    interval_from_center,
)


def test_arb_transition_width_contracts_under_cell_refinement():
    with workprec(128):
        coarse_y = interval_from_center(2.8, 0.125)
        fine_y = interval_from_center(2.8, 0.03125)
        coarse_z = interval_from_center(-2.3, 0.125)
        fine_z = interval_from_center(-2.3, 0.03125)
        coarse = arb_transition(coarse_y, coarse_y, coarse_z)
        fine = arb_transition(fine_y, fine_y, fine_z)
        assert ball_width(fine[0]) < 0.3 * ball_width(coarse[0])
        assert ball_width(fine[1]) < 0.3 * ball_width(coarse[1])


def test_arb_continuation_bounds_have_expected_signs():
    with workprec(128):
        y_plus = arb(1)
        y_minus = arb(2)
        ell, upper = arb_continuation_bounds(y_plus, y_minus)
        assert ell < 0
        assert upper > 0
        assert ell < upper
