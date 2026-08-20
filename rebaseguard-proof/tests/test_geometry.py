from rebaseguard_certify.geometry import in_reachable_closure, reflect
from rebaseguard_certify.model import Alarm, State, step


def test_reachable_closure_includes_axes_and_triangle():
    assert in_reachable_closure(State(4.99, 0.0), 0.5, 5.0)
    assert in_reachable_closure(State(2.0, 1.9), 0.5, 5.0)
    assert not in_reachable_closure(State(2.1, 2.0), 0.5, 5.0)


def test_continuation_preserves_reachable_closure_on_grid():
    states = [State(0.0, 0.0), State(4.9, 0.0), State(0.0, 4.9), State(1.2, 2.3)]
    for state in states:
        for z_quarters in range(-22, 23):
            outcome = step(state, z_quarters / 4.0, 0.5, 5.0)
            if outcome.alarm is Alarm.CONTINUE:
                assert in_reachable_closure(outcome.state, 0.5, 5.0)


def test_reflection_is_involution():
    state = State(1.25, 0.75)
    assert reflect(reflect(state)) == state

