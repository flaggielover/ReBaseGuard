import pytest

from rebaseguard_certify.model import Alarm, State, oracle_step, run_path
from rebaseguard_certify.pathwise import reference_replay


@pytest.mark.parametrize(
    "innovations",
    [
        [0.3, 1.4, 1.8, 2.1, 1.8],
        [-0.3, -1.4, -1.8, -2.1, -1.8],
        [1.0, -2.0, 1.0, -2.0, -2.0, -2.0, -2.0],
        [0.1, -0.1, 0.2, -0.2, 8.0],
    ],
)
def test_reference_replay_matches_oracle_pathwise(innovations):
    reference = reference_replay(innovations)
    state = State(0.0, 0.0)
    total = 0.0
    for row in reference:
        outcome = oracle_step(state, total, row.z)
        assert outcome.state.plus == pytest.approx(row.post_plus)
        assert outcome.state.minus == pytest.approx(row.post_minus)
        assert outcome.t_sum == pytest.approx(row.post_t)
        assert outcome.alarm.value == row.alarm
        assert outcome.terminal_reward == pytest.approx(row.terminal_reward)
        state = outcome.state
        total = outcome.t_sum

    result = run_path(innovations)
    terminal = reference[-1]
    assert result.tau == terminal.time
    assert result.z_tau == terminal.z
    assert result.t_sum == pytest.approx(terminal.post_t)
    assert result.z_tau * result.t_sum == pytest.approx(terminal.terminal_reward)
    assert result.alarm is (Alarm.UP if terminal.alarm == 1 else Alarm.DOWN)
