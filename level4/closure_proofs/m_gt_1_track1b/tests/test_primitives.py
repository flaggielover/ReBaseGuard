from __future__ import annotations

import numpy as np

from rebaseguard_mgt1b.primitives import primitive_checks, simulate_stopped_batch


def run(seed: int, *, max_m: int = 50, dwell: int | None = None, n: int = 500):
    return simulate_stopped_batch(
        n_paths=n,
        max_m=max_m,
        rng=np.random.default_rng(seed),
        minimum_dwell=dwell,
    )


def test_raw_primitives_have_valid_shapes_and_padding():
    paths = run(1)
    assert all(primitive_checks(paths).values())


def test_minimum_dwell_is_enforced():
    for m in (1, 2, 5, 20, 50):
        paths = run(10 + m, max_m=m, dwell=m)
        assert np.all(paths.tau >= m)


def test_seed_reproducibility():
    first = run(42)
    second = run(42)
    assert np.array_equal(first.tau, second.tau)
    assert np.array_equal(first.t_tau, second.t_tau)
    assert np.array_equal(first.lags_newest, second.lags_newest)

