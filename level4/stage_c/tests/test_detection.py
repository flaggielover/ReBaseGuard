"""The Stage C detection simulator must be the frozen chain plus a shift."""

from __future__ import annotations

import numpy as np
import pytest

from detection import DetectionConfig, simulate_detection
from rebaseguard_level4.multicycle import MultiCycleConfig, simulate_multicycle


@pytest.mark.parametrize("rho", [0.0, 0.25, 1.0])
def test_zero_shift_reproduces_stage_a_bit_for_bit(rho):
    """Stage C adds a mean shift and nothing else; with no shift it IS Stage A."""
    cfg = DetectionConfig(n_replicates=6, burn_in=5, n_cycles_after=15,
                          rho=rho, shift=0.0, master_seed=31337)
    got = simulate_detection(cfg)
    want = simulate_multicycle(MultiCycleConfig(
        n_replicates=6, n_cycles=20, burn_in=0, rho=rho, m=1,
        master_seed=31337))
    assert np.array_equal(got.tau, want.tau)
    assert np.array_equal(got.e_prev, want.e_prev)
    assert np.array_equal(got.e_next, want.e_next)
    assert np.array_equal(got.direction, want.direction)


def test_shift_is_exactly_a_reference_error_offset():
    """mu -> Delta is exactly e -> e - Delta, because e = R - mu."""
    delta = 0.75
    base = simulate_detection(DetectionConfig(
        n_replicates=8, burn_in=4, n_cycles_after=3, rho=0.0, shift=0.0,
        master_seed=555))
    shifted = simulate_detection(DetectionConfig(
        n_replicates=8, burn_in=4, n_cycles_after=3, rho=0.0, shift=delta,
        master_seed=555))
    # rho = 0 makes e_next independent of the cycle, so the pre-change cycles
    # are identical and the change cycle's e_prev drops by exactly Delta.
    b = base.by_replicate("e_prev")
    s = shifted.by_replicate("e_prev")
    assert np.allclose(b[:, :4], s[:, :4])
    assert np.allclose(s[:, 4], b[:, 4] - delta)


def test_detection_delay_is_the_first_post_change_cycle():
    res = simulate_detection(DetectionConfig(
        n_replicates=5, burn_in=3, n_cycles_after=4, rho=0.5, shift=1.0,
        master_seed=11))
    tau = res.by_replicate("tau")
    assert np.array_equal(res.detection_delays()[:, 0], tau[:, 3])


def test_change_bookkeeping_marks_only_post_change_cycles():
    res = simulate_detection(DetectionConfig(
        n_replicates=3, burn_in=6, n_cycles_after=4, rho=0.5, shift=1.0,
        master_seed=12))
    ci = res.by_replicate("change_index")[0]
    since = res.by_replicate("cycles_since_change")[0]
    assert np.all(ci[:6] == -1)
    assert np.all(ci[6:] == 0)
    assert np.array_equal(since[6:], np.arange(4))


def test_each_change_contributes_exactly_one_offset_at_rho_zero():
    """At rho = 0 the reference fully re-adapts between changes.

    mu_fresh is an observation of the CURRENT process, so e_next = R - mu has
    mean 0 relative to the NEW mean. Each further change therefore displaces the
    reference by exactly one -Delta, not by a cumulative -k*Delta. That is the
    physically correct behaviour and it is what makes rho = 0 the recovery
    baseline.
    """
    delta = 0.5
    res = simulate_detection(DetectionConfig(
        n_replicates=3000, burn_in=20, n_cycles_after=2, rho=0.0, shift=delta,
        master_seed=77, n_changes=3))
    e = res.by_replicate("e_prev")
    for change in range(3):
        col = 20 + change * 2
        assert e[:, col].mean() == pytest.approx(-delta, abs=0.06), change
        # and the cycle AFTER each change is already back on target
        assert e[:, col + 1].mean() == pytest.approx(0.0, abs=0.06), change


def test_full_reuse_recovers_more_slowly_than_fresh():
    """rho = 1 carries the displaced reference forward; rho = 0 does not."""
    delta = 1.5
    out = {}
    for rho in (0.0, 1.0):
        res = simulate_detection(DetectionConfig(
            n_replicates=3000, burn_in=100, n_cycles_after=4, rho=rho,
            shift=delta, master_seed=2024))
        e = res.by_replicate("e_prev")
        out[rho] = np.abs(e[:, 100 + 1]).mean()      # first cycle after re-alarm
    assert out[1.0] > out[0.0]


def test_larger_shift_detects_faster():
    means = []
    for shift in (0.0, 0.5, 1.5):
        res = simulate_detection(DetectionConfig(
            n_replicates=3000, burn_in=100, n_cycles_after=2, rho=0.0,
            shift=shift, master_seed=909))
        means.append(res.detection_delays()[:, 0].mean())
    assert means[0] > means[1] > means[2]


def test_config_validation():
    for kwargs in ({"k": 0.6}, {"h": 4.0}, {"m": 5}, {"rho": 1.5}):
        base = dict(n_replicates=2, burn_in=1, n_cycles_after=1, rho=0.5,
                    shift=1.0, master_seed=1)
        base.update(kwargs)
        with pytest.raises(ValueError):
            DetectionConfig(**base).validate()


def test_no_two_arm_ties():
    res = simulate_detection(DetectionConfig(
        n_replicates=50, burn_in=20, n_cycles_after=20, rho=1.0, shift=1.0,
        master_seed=4242))
    assert res.n_ties == 0


def test_detection_is_reproducible():
    cfg = DetectionConfig(n_replicates=20, burn_in=10, n_cycles_after=5,
                          rho=0.3, shift=1.0, master_seed=8)
    a, b = simulate_detection(cfg), simulate_detection(cfg)
    assert np.array_equal(a.tau, b.tau)
    assert np.array_equal(a.e_next, b.e_next)
