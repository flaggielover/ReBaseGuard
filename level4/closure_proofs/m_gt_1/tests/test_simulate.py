from __future__ import annotations

import numpy as np

from rebaseguard_mgt1.simulate import simulate_stopped_batch


def _run(seed=1, **kw):
    return simulate_stopped_batch(
        e=kw.pop("e", 0.0), n_paths=kw.pop("n_paths", 200),
        m_grid=np.array(kw.pop("m_grid", [1, 5])),
        rng=np.random.default_rng(seed), **kw,
    )


def test_ordinary_stop_outputs_valid_shapes():
    b = _run()
    assert b.tau.shape == (200,)
    assert b.zbar.shape == (200, 2)
    assert np.all(b.tau >= 1)


def test_m1_window_is_terminal_lag_exactly():
    b = _run()
    assert np.array_equal(b.window_sum[:, 0], b.lags_newest[:, 0])
    assert np.array_equal(b.zbar[:, 0], b.lags_newest[:, 0])


def test_tau_less_than_m_window_is_entire_stopped_sum():
    b = _run(n_paths=2000, m_grid=[100])
    short = b.tau < 100
    assert short.any()
    assert np.allclose(b.window_sum[short, 0], b.t_tau[short], atol=1e-12, rtol=1e-12)
    assert np.allclose(b.zbar[short, 0], b.t_tau[short] / b.tau[short])


def test_minimum_dwell_is_stage_a_control_only_and_enforced():
    b = _run(n_paths=500, m_grid=[20], minimum_dwell=20)
    assert np.all(b.tau >= 20)


def test_simulation_is_seed_reproducible():
    a = _run(seed=42)
    b = _run(seed=42)
    assert np.array_equal(a.tau, b.tau)
    assert np.array_equal(a.zbar, b.zbar)


def test_location_parameter_changes_residual_stopped_law():
    a = _run(seed=43, e=0.0)
    b = _run(seed=43, e=0.2)
    assert not np.array_equal(a.t_tau, b.t_tau)
