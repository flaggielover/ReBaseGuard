import numpy as np

from rebaseguard_certify.mesh import TensorCandidate


def test_tensor_candidate_interpolates_nodes_and_reflects():
    coordinates = np.linspace(0.0, 5.0, 5)
    values = coordinates[:, None] - coordinates[None, :]
    candidate = TensorCandidate(values, h=5.0)
    assert candidate.evaluate(2.5, 1.25) == 1.25
    assert candidate.evaluate(1.25, 2.5) == -1.25


def test_dyadic_round_trip_is_deterministic():
    values = np.array([[0.0, 0.1], [0.2, 0.3]])
    candidate = TensorCandidate(values, h=5.0)
    encoded = candidate.to_dyadic(scale_bits=40)
    restored = TensorCandidate.from_dyadic(encoded)
    assert restored.to_dyadic(scale_bits=40) == encoded

