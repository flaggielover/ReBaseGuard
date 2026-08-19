import math

import pytest

from rebaseguard_phase4b.sr_model import (
    FROZEN_DELTA,
    SRAlarm,
    SRState,
    run_sr_path,
    sr_oracle_step,
)
from rebaseguard_phase4b.sr_pathwise import replay_sr_raw


def test_delta_is_frozen():
    assert FROZEN_DELTA == 1.0
    with pytest.raises(ValueError, match="freezes delta=1"):
        sr_oracle_step(SRState(), 0.0, 0.0, threshold=10.0, delta=0.5)


def test_initial_state_updates_both_arms_from_same_increment():
    outcome = sr_oracle_step(SRState(), 0.0, 0.25, threshold=10.0)
    assert outcome.log_r_plus == pytest.approx(-0.25)
    assert outcome.log_r_minus == pytest.approx(-0.75)
    assert outcome.state.log1p_plus == pytest.approx(math.log1p(math.exp(-0.25)))
    assert outcome.state.log1p_minus == pytest.approx(math.log1p(math.exp(-0.75)))
    assert outcome.alarm is SRAlarm.CONTINUE
    assert outcome.terminal_reward is None


@pytest.mark.parametrize("epsilon", [-1e-9, 0.0, 1e-9])
def test_exact_and_epsilon_boundary_crossing(epsilon):
    threshold = 10.0
    z = math.log(threshold) + 0.5 + epsilon
    outcome = sr_oracle_step(SRState(), 3.0, z, threshold=threshold)
    expected = SRAlarm.CONTINUE if epsilon < 0.0 else SRAlarm.PLUS
    assert outcome.alarm is expected
    if expected is SRAlarm.PLUS:
        assert outcome.terminal_reward == pytest.approx(z * (3.0 + z))


def test_large_negative_overshoot_and_reflection():
    threshold = 10.0
    minus = sr_oracle_step(SRState(), 2.0, -20.0, threshold=threshold)
    plus = sr_oracle_step(SRState(), -2.0, 20.0, threshold=threshold)
    assert minus.alarm is SRAlarm.MINUS
    assert plus.alarm is SRAlarm.PLUS
    assert minus.state.log1p_minus == pytest.approx(plus.state.log1p_plus)
    assert minus.terminal_reward == pytest.approx(plus.terminal_reward)


def test_symmetric_tie_rule_is_explicit():
    outcome = sr_oracle_step(SRState(0.6, 0.6), 0.0, 0.0, threshold=1.0)
    assert outcome.alarm is SRAlarm.TIE
    assert outcome.terminal_reward == 0.0


@pytest.mark.parametrize(
    "innovations",
    [
        [0.1, -0.2, 0.3, 5.0],
        [-0.1, 0.2, -0.3, -5.0],
        [1.0, -1.5, 0.2, -0.4, 6.0],
    ],
)
def test_log_oracle_matches_independent_raw_replay(innovations):
    threshold = 25.0
    oracle = run_sr_path(innovations, threshold=threshold)
    raw = replay_sr_raw(innovations, threshold=threshold)
    assert oracle.tau == raw[-1].time
    assert oracle.z_tau == raw[-1].z
    assert oracle.t_tau == pytest.approx(raw[-1].t_sum)
    assert oracle.terminal_reward == pytest.approx(raw[-1].terminal_reward)
    for log_row, raw_row in zip(oracle.trace, raw, strict=True):
        assert math.expm1(log_row.state.log1p_plus) == pytest.approx(raw_row.post_plus)
        assert math.expm1(log_row.state.log1p_minus) == pytest.approx(raw_row.post_minus)
        assert log_row.t_sum == pytest.approx(raw_row.t_sum)
        assert log_row.alarm.value == raw_row.alarm


def test_reflected_paths_swap_arms_and_preserve_reward():
    innovations = [0.3, -0.1, 0.7, 5.0]
    positive = run_sr_path(innovations, threshold=25.0)
    negative = run_sr_path([-z for z in innovations], threshold=25.0)
    assert positive.tau == negative.tau
    assert positive.alarm is SRAlarm.PLUS
    assert negative.alarm is SRAlarm.MINUS
    assert positive.z_tau == -negative.z_tau
    assert positive.t_tau == pytest.approx(-negative.t_tau)
    assert positive.terminal_reward == pytest.approx(negative.terminal_reward)
