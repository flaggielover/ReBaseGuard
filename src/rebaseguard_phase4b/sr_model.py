"""Canonical scalar oracle for the symmetric two-chart SR detector."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Iterable


FROZEN_DELTA = 1.0


class SRAlarm(Enum):
    CONTINUE = 0
    PLUS = 1
    MINUS = -1
    TIE = 2


@dataclass(frozen=True, slots=True)
class SRState:
    """Logarithms of ``1+R^+`` and ``1+R^-``."""

    log1p_plus: float = 0.0
    log1p_minus: float = 0.0


@dataclass(frozen=True, slots=True)
class SRStepResult:
    pre_state: SRState
    state: SRState
    z: float
    t_sum: float
    alarm: SRAlarm
    log_r_plus: float
    log_r_minus: float
    terminal_reward: float | None


@dataclass(frozen=True, slots=True)
class SRPathResult:
    tau: int
    z_tau: float
    t_tau: float
    alarm: SRAlarm
    terminal_reward: float
    trace: tuple[SRStepResult, ...]


def _softplus(value: float) -> float:
    if value > 0.0:
        return value + math.log1p(math.exp(-value))
    return math.log1p(math.exp(value))


def sr_oracle_step(
    state: SRState,
    t_sum: float,
    z: float,
    *,
    threshold: float,
    delta: float = FROZEN_DELTA,
) -> SRStepResult:
    """Update both SR arms from one increment and then check ``>= A``."""

    if threshold <= 0.0:
        raise ValueError("threshold must be positive")
    if delta != FROZEN_DELTA:
        raise ValueError("Phase-4B freezes delta=1")
    z = float(z)
    half_delta_sq = 0.5 * delta * delta
    log_r_plus = state.log1p_plus + delta * z - half_delta_sq
    log_r_minus = state.log1p_minus - delta * z - half_delta_sq
    next_state = SRState(_softplus(log_r_plus), _softplus(log_r_minus))
    log_threshold = math.log(threshold)
    plus_crossed = log_r_plus >= log_threshold
    minus_crossed = log_r_minus >= log_threshold
    if plus_crossed and minus_crossed:
        if log_r_plus > log_r_minus:
            alarm = SRAlarm.PLUS
        elif log_r_minus > log_r_plus:
            alarm = SRAlarm.MINUS
        else:
            alarm = SRAlarm.TIE
    elif plus_crossed:
        alarm = SRAlarm.PLUS
    elif minus_crossed:
        alarm = SRAlarm.MINUS
    else:
        alarm = SRAlarm.CONTINUE
    next_t_sum = t_sum + z
    reward = z * next_t_sum if alarm is not SRAlarm.CONTINUE else None
    return SRStepResult(
        state,
        next_state,
        z,
        next_t_sum,
        alarm,
        log_r_plus,
        log_r_minus,
        reward,
    )


def run_sr_path(
    innovations: Iterable[float], *, threshold: float, delta: float = FROZEN_DELTA
) -> SRPathResult:
    state = SRState()
    t_sum = 0.0
    trace: list[SRStepResult] = []
    for time, z in enumerate(innovations, start=1):
        outcome = sr_oracle_step(
            state, t_sum, z, threshold=threshold, delta=delta
        )
        trace.append(outcome)
        if outcome.alarm is not SRAlarm.CONTINUE:
            assert outcome.terminal_reward is not None
            return SRPathResult(
                time,
                outcome.z,
                outcome.t_sum,
                outcome.alarm,
                outcome.terminal_reward,
                tuple(trace),
            )
        state = outcome.state
        t_sum = outcome.t_sum
    raise ValueError("innovation sequence ended before an SR alarm")

