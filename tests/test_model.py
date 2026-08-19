import numpy as np
import pytest

from rebaseguard_certify.model import (
    Alarm,
    State,
    oracle_step,
    run_path,
    step,
    thresholds,
)


def test_alarm_thresholds_at_origin():
    assert thresholds(State(0.0, 0.0), 0.5, 5.0) == (-5.5, 5.5)


def test_step_records_up_alarm_and_terminal_state():
    outcome = step(State(4.9, 0.0), 0.7, 0.5, 5.0)
    assert outcome.alarm is Alarm.UP
    assert outcome.state.plus == pytest.approx(5.1)
    assert outcome.state.minus == 0.0


@pytest.mark.parametrize(
    ("state", "total", "z", "expected_state", "alarm", "reward"),
    [
        (State(0.0, 0.0), 0.0, 0.25, State(0.0, 0.0), Alarm.CONTINUE, None),
        (State(1.0, 0.0), 2.0, -1.0, State(0.0, 0.5), Alarm.CONTINUE, None),
        (State(4.9, 0.0), 3.0, 0.6, State(5.0, 0.0), Alarm.UP, 2.16),
        (State(0.0, 4.9), -3.0, -0.6, State(0.0, 5.0), Alarm.DOWN, 2.16),
        (State(4.9, 0.0), 3.0, 0.599999, State(4.999999, 0.0), Alarm.CONTINUE, None),
        (State(4.9, 0.0), -2.0, 20.0, State(24.4, 0.0), Alarm.UP, 360.0),
    ],
)
def test_one_step_oracle_conventions(
    state, total, z, expected_state, alarm, reward
):
    outcome = oracle_step(state, total, z)
    assert outcome.state.plus == pytest.approx(expected_state.plus)
    assert outcome.state.minus == pytest.approx(expected_state.minus)
    assert outcome.t_sum == pytest.approx(total + z)
    assert outcome.alarm is alarm
    if reward is None:
        assert outcome.terminal_reward is None
    else:
        assert outcome.terminal_reward == pytest.approx(reward)


def test_reflected_paths_swap_alarm_arms():
    z = np.array([0.3, 1.4, 1.8, 2.1, 1.8])
    up = run_path(z, 0.5, 5.0)
    down = run_path(-z, 0.5, 5.0)
    assert up.alarm is Alarm.UP
    assert down.alarm is Alarm.DOWN
    assert up.tau == down.tau
    assert up.z_tau == -down.z_tau
    assert up.t_sum == -down.t_sum
    assert up.z_tau * up.t_sum == down.z_tau * down.t_sum
