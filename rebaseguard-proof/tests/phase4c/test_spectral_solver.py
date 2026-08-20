from __future__ import annotations

from rebaseguard_phase4c.spectral_solver import solve_spectral_sr


def test_small_spectral_solve_has_correct_symmetry_and_gamma_scale():
    result = solve_spectral_sr(
        5, quadrature_order=64, validation_grid_nodes=9
    )
    assert 10.0 < result.gamma < 20.0
    assert result.symmetry_error_a < 1e-14
    assert result.symmetry_error_b < 1e-14
    assert result.condition_number < 1e5
