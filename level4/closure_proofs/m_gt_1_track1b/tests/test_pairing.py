from __future__ import annotations

import numpy as np

from rebaseguard_mgt1b.direct import direct_gain, stage_a_gain
from rebaseguard_mgt1b.primitives import M_GRID, simulate_stopped_batch
from rebaseguard_mgt1b.reconstruction import reconstructed_gain


def ordinary(seed: int, n: int = 2_000):
    return simulate_stopped_batch(
        n_paths=n,
        max_m=int(M_GRID.max()),
        rng=np.random.default_rng(seed),
    )


def test_direct_per_path_decomposition_is_roundoff_exact():
    paths = ordinary(7)
    direct = direct_gain(paths, M_GRID)
    fixed, correction, reconstructed = reconstructed_gain(paths, M_GRID)
    assert np.max(np.abs(direct - reconstructed)) <= 1e-10
    assert np.max(np.abs(direct - fixed - correction)) <= 1e-10


def test_short_correction_is_nonnegative_and_m1_zero():
    paths = ordinary(8)
    _, correction, _ = reconstructed_gain(paths, M_GRID)
    assert np.all(correction >= 0.0)
    assert np.array_equal(correction[:, 0], np.zeros(paths.tau.size))


def test_m1_stage_a_stage_d_exact_reduction():
    seed = 11
    stage_a = simulate_stopped_batch(
        n_paths=500, max_m=1, rng=np.random.default_rng(seed), minimum_dwell=1
    )
    stage_d = simulate_stopped_batch(
        n_paths=500, max_m=1, rng=np.random.default_rng(seed)
    )
    assert np.array_equal(stage_a.tau, stage_d.tau)
    assert np.array_equal(stage_a.t_tau, stage_d.t_tau)
    assert np.array_equal(
        stage_a_gain(stage_a, 1), direct_gain(stage_d, np.array([1]))[:, 0]
    )


def test_pairing_alignment_rejects_no_rows_silently():
    paths = ordinary(13, n=123)
    assert direct_gain(paths, M_GRID).shape == (123, 6)
    assert reconstructed_gain(paths, M_GRID)[2].shape == (123, 6)

