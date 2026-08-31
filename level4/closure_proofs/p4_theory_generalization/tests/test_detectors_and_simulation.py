"""The detector recursions must be the frozen ones, and the simulator must
compute the window statistic that the theorem talks about."""

from __future__ import annotations

import numpy as np
import pytest

from rebaseguard_level4 import frozen as frozen_level4
from rebaseguard_p4_general.detectors import A_FROZEN, H_FROZEN, K_FROZEN, Detector
from rebaseguard_p4_general.families import REGISTRY
from rebaseguard_p4_general.simulate import (
    STREAM_STRIDE, simulate_group, stream_counter,
)


def test_frozen_constants_match_the_frozen_model():
    assert K_FROZEN == frozen_level4.K_FROZEN == 0.5
    assert H_FROZEN == frozen_level4.H_FROZEN == 5.0
    assert A_FROZEN == 520.886133602749


def test_cusum_step_matches_the_frozen_scalar_implementation():
    rng = np.random.default_rng(7)
    detector = Detector("cusum", H_FROZEN)
    up, down = detector.new_state(1)
    plus = minus = 0.0
    for step in range(1, 400):
        z = float(rng.standard_normal())
        up, down, crossed = detector.step(up, down, np.array([z]), step)
        plus, minus, alarm = frozen_level4.step_scalar(plus, minus, z)
        assert up[0] == pytest.approx(plus, abs=0, rel=0)
        assert down[0] == pytest.approx(minus, abs=0, rel=0)
        assert bool(crossed[0]) == (alarm != frozen_level4.ALARM_NONE)
        if crossed[0]:
            break


def test_sr_reset_state_reproduces_the_first_update_exactly():
    detector = Detector("sr", A_FROZEN)
    up, down = detector.new_state(1)
    z = np.array([0.37])
    up, down, _ = detector.step(up, down, z, 1)
    # R_1 = (1 + 0) exp(Z_1 - 1/2); the charts are carried in logs
    assert np.exp(up[0]) == pytest.approx(np.exp(0.37 - 0.5), rel=1e-12)
    assert np.exp(down[0]) == pytest.approx(np.exp(-0.37 - 0.5), rel=1e-12)


def test_sr_matches_a_direct_linear_domain_recursion():
    rng = np.random.default_rng(11)
    detector = Detector("sr", 50.0)
    up, down = detector.new_state(1)
    r_plus = r_minus = 0.0
    for step in range(1, 60):
        z = float(rng.standard_normal())
        up, down, crossed = detector.step(up, down, np.array([z]), step)
        r_plus = (1.0 + r_plus) * np.exp(z - 0.5)
        r_minus = (1.0 + r_minus) * np.exp(-z - 0.5)
        assert np.exp(up[0]) == pytest.approx(r_plus, rel=1e-10)
        assert np.exp(down[0]) == pytest.approx(r_minus, rel=1e-10)
        if crossed[0]:
            assert max(r_plus, r_minus) >= 50.0
            break


def test_forcing_increments_alarm_in_one_step_from_the_reset_state():
    for detector in (Detector("cusum", 5.0), Detector("sr", 520.886133602749)):
        up, down = detector.new_state(1)
        z = np.array([detector.forcing_increment()])
        _, _, crossed = detector.step(up, down, z, 1)
        assert bool(crossed[0])


def test_window_mean_is_the_truncated_average_including_the_alarm_increment():
    (run,) = simulate_group(
        family=REGISTRY["gaussian"], detector=Detector("cusum", 2.0),
        e_values=(0.0,), n_paths=4000, seed=5, batch=0, m_max=5, mode="compact",
    )
    assert run.unstopped == 0
    assert (run.tau >= 1).all()
    # m = 1 is exactly the terminal increment
    np.testing.assert_array_equal(run.window_mean(1), run.window[:, -1])
    # on tau < m the window is the whole path, so A_m = T_tau / tau
    short = run.tau < 5
    assert short.any()
    np.testing.assert_allclose(
        run.window_mean(5)[short], (run.total / run.tau)[short], rtol=1e-12
    )
    # the fixed-denominator statistic differs exactly by the window ratio
    np.testing.assert_allclose(
        run.fixed_window_mean(5),
        run.window_mean(5) * np.minimum(5, run.tau) / 5, rtol=1e-12,
    )


def test_short_correction_matches_the_pathwise_decomposition():
    (run,) = simulate_group(
        family=REGISTRY["laplace"], detector=Detector("cusum", 2.0),
        e_values=(0.0,), n_paths=4000, seed=6, batch=0, m_max=5, mode="compact",
    )
    for m in (1, 2, 3, 5):
        direct = run.window_mean(m) * run.score_sum
        fixed = run.fixed_window_mean(m) * run.score_sum
        np.testing.assert_allclose(
            direct, fixed + run.short_correction(m), rtol=1e-10, atol=1e-12
        )
    assert np.all(run.short_correction(1) == 0.0)


def test_the_short_correction_can_be_negative_for_a_bounded_score():
    """Theorem G3: the sign is the sign of T_tau S_tau, not automatic."""
    (run,) = simulate_group(
        family=REGISTRY["laplace"], detector=Detector("cusum", 2.0),
        e_values=(0.0,), n_paths=20000, seed=8, batch=0, m_max=5, mode="compact",
    )
    correction = run.short_correction(5)
    assert (correction < 0).any()
    gaussian_analogue = np.where(
        run.tau < 5, (1.0 / np.maximum(run.tau, 1) - 1 / 5) * run.total ** 2, 0.0
    )
    assert (gaussian_analogue >= 0).all()


def test_aligned_streams_do_not_overlap_between_steps():
    """The pilot defect: Philox emits four words per counter increment, so
    consecutive streams must be separated by far more than the batch size."""
    assert STREAM_STRIDE >= 1 << 64
    assert stream_counter(0, 2) - stream_counter(0, 1) == STREAM_STRIDE
    family = REGISTRY["gaussian"]
    draws = [
        family.sample(
            np.random.Generator(np.random.Philox(key=5, counter=stream_counter(0, s))),
            (100000,),
        )
        for s in (1, 2, 3)
    ]
    for a, b in ((draws[0], draws[1]), (draws[1], draws[2]), (draws[0], draws[2])):
        assert abs(float(np.corrcoef(a, b)[0, 1])) < 0.01
        assert not np.isin(a[:2000], b).any()


def test_aligned_mode_couples_the_two_parameter_values():
    plus, minus = simulate_group(
        family=REGISTRY["gaussian"], detector=Detector("cusum", 2.0),
        e_values=(0.025, -0.025), n_paths=4000, seed=9, batch=0, m_max=1,
        mode="aligned",
    )
    coupled = float((plus.tau == minus.tau).mean())
    uncoupled_plus, _ = simulate_group(
        family=REGISTRY["gaussian"], detector=Detector("cusum", 2.0),
        e_values=(0.025, -0.025), n_paths=4000, seed=10, batch=0, m_max=1,
        mode="aligned",
    )
    uncoupled = float((uncoupled_plus.tau == minus.tau).mean())
    # common random numbers: paired paths mostly stop at the same step, and
    # far more often than two independently seeded runs do
    assert coupled > 0.6
    assert coupled > 5.0 * uncoupled


def test_both_modes_are_reproducible_from_seed_and_batch():
    for mode, values in (("compact", (0.0,)), ("aligned", (0.02, -0.02))):
        first = simulate_group(
            family=REGISTRY["t3"], detector=Detector("sr", 20.0), e_values=values,
            n_paths=2000, seed=3, batch=1, m_max=3, mode=mode,
        )
        second = simulate_group(
            family=REGISTRY["t3"], detector=Detector("sr", 20.0), e_values=values,
            n_paths=2000, seed=3, batch=1, m_max=3, mode=mode,
        )
        for a, b in zip(first, second):
            np.testing.assert_array_equal(a.tau, b.tau)
            np.testing.assert_array_equal(a.score_sum, b.score_sum)


def test_compact_mode_rejects_multiple_parameter_values():
    with pytest.raises(ValueError):
        simulate_group(
            family=REGISTRY["gaussian"], detector=Detector("cusum", 2.0),
            e_values=(0.1, -0.1), n_paths=10, seed=1, batch=0, m_max=1,
            mode="compact",
        )
