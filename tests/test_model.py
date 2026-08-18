import numpy as np
import pytest

from rebaseguard_certify.model import Alarm, State, run_path, step, thresholds


def test_alarm_thresholds_at_origin():
    assert thresholds(State(0.0, 0.0), 0.5, 5.0) == (-5.5, 5.5)


def test_step_records_up_alarm_and_terminal_state():
    outcome = step(State(4.9, 0.0), 0.7, 0.5, 5.0)
    assert outcome.alarm is Alarm.UP
    assert outcome.state.plus == pytest.approx(5.1)
    assert outcome.state.minus == 0.0


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
