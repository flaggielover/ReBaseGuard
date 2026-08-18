import numpy as np

from rebaseguard_certify.candidate import solve_candidates


def test_coarse_candidates_obey_reflection_symmetry():
    a_hat, b_hat, metadata = solve_candidates(intervals=8, quadrature_order=16)
    assert np.max(np.abs(a_hat.values + a_hat.values.T)) < 1e-11
    assert np.max(np.abs(b_hat.values - b_hat.values.T)) < 1e-11
    assert abs(a_hat.evaluate(0.0, 0.0)) < 1e-11
    assert b_hat.evaluate(0.0, 0.0) > 2.0
    assert metadata["proof_role"] == "NON-RIGOROUS CANDIDATE ONLY"

