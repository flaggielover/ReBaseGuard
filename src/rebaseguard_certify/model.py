"""Exact pathwise model definitions shared by diagnostics and certifiers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class Alarm(Enum):
    CONTINUE = 0
    UP = 1
    DOWN = -1


@dataclass(frozen=True, slots=True)
class State:
    plus: float
    minus: float


@dataclass(frozen=True, slots=True)
class StepResult:
    state: State
    alarm: Alarm


@dataclass(frozen=True, slots=True)
class PathResult:
    tau: int
    z_tau: float
    t_sum: float
    alarm: Alarm
    pre_state: State
    terminal_state: State


def thresholds(state: State, k: float, h: float) -> tuple[float, float]:
    """Return the inclusive down/up alarm increment thresholds."""

    return state.minus - h - k, h + k - state.plus


def step(state: State, z: float, k: float, h: float) -> StepResult:
    plus = max(0.0, state.plus + z - k)
    minus = max(0.0, state.minus - z - k)
    next_state = State(plus, minus)
    if plus >= h:
        return StepResult(next_state, Alarm.UP)
    if minus >= h:
        return StepResult(next_state, Alarm.DOWN)
    return StepResult(next_state, Alarm.CONTINUE)


def run_path(
    innovations: Iterable[float], k: float = 0.5, h: float = 5.0
) -> PathResult:
    state = State(0.0, 0.0)
    t_sum = 0.0
    for tau, z_value in enumerate(innovations, start=1):
        z = float(z_value)
        pre_state = state
        outcome = step(state, z, k, h)
        t_sum += z
        if outcome.alarm is not Alarm.CONTINUE:
            return PathResult(tau, z, t_sum, outcome.alarm, pre_state, outcome.state)
        state = outcome.state
    raise ValueError("innovation sequence ended before an alarm")

