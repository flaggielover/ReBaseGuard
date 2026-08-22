from __future__ import annotations

import numpy as np

from rebaseguard_mgt1a.simulate import simulate_stopped_batch


def _run(seed: int, *, m: int, dwell: int | None, n: int = 500):
    return simulate_stopped_batch(
        n_paths=n,
        m_grid=np.array([m]),
        rng=np.random.default_rng(seed),
        minimum_dwell=dwell,
    )


def test_stage_a_minimum_dwell_is_enforced():
    for m in (2, 5, 20, 50):
        batch = _run(10 + m, m=m, dwell=m)
        assert np.all(batch.tau >= m)


def test_stage_d_ordinary_stop_has_truncated_short_cycles():
    batch = _run(50, m=50, dwell=None, n=2_000)
    short = batch.tau < 50
    assert short.any()
    assert np.allclose(batch.window_sum[short, 0], batch.t_tau[short])
    assert np.allclose(batch.window_mean[short, 0], batch.t_tau[short] / batch.tau[short])


def test_m1_stage_a_and_stage_d_are_bitwise_identical_with_shared_stream():
    stage_a = _run(91, m=1, dwell=1)
    stage_d = _run(91, m=1, dwell=None)
    assert np.array_equal(stage_a.tau, stage_d.tau)
    assert np.array_equal(stage_a.t_tau, stage_d.t_tau)
    assert np.array_equal(stage_a.window_sum, stage_d.window_sum)


def test_simulator_is_reproducible():
    first = _run(123, m=10, dwell=None)
    second = _run(123, m=10, dwell=None)
    assert np.array_equal(first.tau, second.tau)
    assert np.array_equal(first.window_sum, second.window_sum)

