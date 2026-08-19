from __future__ import annotations

from rebaseguard_phase4c.approximate_solver import solve_approximate_sr


def test_small_approximate_system_preserves_operator_invariants():
    result = solve_approximate_sr(9, quadrature_order=32)
    assert 10.0 < result.gamma < 25.0
    assert result.discrete_residual_a < 1e-11
    assert result.discrete_residual_b < 1e-10
    assert result.symmetry_error_a < 1e-10
    assert result.symmetry_error_b < 1e-10
    assert result.operator_row_mass_error < 1e-12
