import numpy as np

from rebaseguard_phase4b.sr_simulation import (
    _counter_normals,
    simulate_symmetric_sr,
)


def test_counter_normals_are_path_time_addressable():
    indices = np.array([2, 5, 9])
    full = _counter_normals(314159, 7, np.arange(12))
    subset = _counter_normals(314159, 7, indices)
    assert np.array_equal(subset, full[indices])


def test_seeded_sr_simulation_is_reproducible_and_symmetric():
    left = simulate_symmetric_sr(512, threshold=25.0, seed=1729)
    right = simulate_symmetric_sr(512, threshold=25.0, seed=1729)
    assert np.array_equal(left.tau, right.tau)
    assert np.array_equal(left.z_tau, right.z_tau)
    assert np.array_equal(left.t_tau, right.t_tau)
    summary = left.summary(detector="symmetric_sr")
    assert summary["n"] == 512
    assert summary["gamma_se"] > 0.0
    assert summary["tie_fraction"] == 0.0


def test_higher_threshold_has_no_smaller_pathwise_arl_with_crn():
    low = simulate_symmetric_sr(
        256, threshold=10.0, seed=314159, counter_based=True
    )
    high = simulate_symmetric_sr(
        256, threshold=20.0, seed=314159, counter_based=True
    )
    assert np.all(high.tau >= low.tau)
