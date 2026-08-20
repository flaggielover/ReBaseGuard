from __future__ import annotations

import numpy as np
import pytest

from rebaseguard_phase4b.multicycle import simulate_multicycle_sr


def test_multicycle_is_seed_reproducible() -> None:
    kwargs = dict(
        threshold=8.0,
        rho=0.25,
        seed=99,
        chains=8,
        cycles_per_chain=5,
        burn_in_cycles=2,
    )
    left = simulate_multicycle_sr(**kwargs)
    right = simulate_multicycle_sr(**kwargs)
    np.testing.assert_array_equal(left.reference_error, right.reference_error)
    np.testing.assert_array_equal(left.cycle_length, right.cycle_length)
    np.testing.assert_array_equal(left.arm, right.arm)


def test_fresh_policy_produces_finite_complete_summary() -> None:
    sample = simulate_multicycle_sr(
        threshold=8.0,
        rho=0.0,
        seed=101,
        chains=8,
        cycles_per_chain=5,
        burn_in_cycles=2,
    )
    summary = sample.summary()
    assert summary["n_cycles"] == 40
    assert np.all(np.isfinite(sample.reference_error))
    assert np.all(sample.cycle_length >= 1)
    assert set(np.unique(sample.arm)).issubset({-1, 1})


@pytest.mark.parametrize("rho", [-0.01, 1.01])
def test_invalid_reuse_fraction_is_rejected(rho: float) -> None:
    with pytest.raises(ValueError, match="rho"):
        simulate_multicycle_sr(
            threshold=8.0,
            rho=rho,
            seed=1,
            chains=4,
            cycles_per_chain=3,
        )
