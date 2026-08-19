from rebaseguard_certify.refined_bellman import (
    reachable_grid,
    refined_bellman_diagnostic,
)


def test_reachable_grid_excludes_unreachable_square_corners():
    grid = reachable_grid(2)
    assert (10, 0) in grid.index
    assert (0, 10) in grid.index
    assert (4, 4) in grid.index
    assert (6, 6) not in grid.index


def test_refined_bellman_mass_balance_and_symmetry():
    result = refined_bellman_diagnostic(2)
    assert result["continuum_certificate"] is False
    assert result["historical_solver_modified"] is False
    assert result["maximum_mass_error"] < 1e-12
    assert result["a_reflection_error"] < 1e-10
    assert result["b_reflection_error"] < 1e-10
    assert 10.0 < result["gamma_finite"] < 25.0
    assert 300.0 < result["arl_finite"] < 700.0


def test_refinement_moves_gamma_toward_monte_carlo_and_arl_toward_465():
    coarse = refined_bellman_diagnostic(2)
    fine = refined_bellman_diagnostic(8)
    assert coarse["gamma_finite"] < fine["gamma_finite"] < 16.0
    assert abs(fine["arl_finite"] - 465.0) < abs(coarse["arl_finite"] - 465.0)
