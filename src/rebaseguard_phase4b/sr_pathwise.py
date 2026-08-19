"""Independent raw-state replay for the symmetric SR convention audit.

This module deliberately does not import or call the log-domain SR oracle.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class RawSRTraceRow:
    time: int
    z: float
    pre_plus: float
    pre_minus: float
    post_plus: float
    post_minus: float
    t_sum: float
    alarm: int
    terminal_reward: float | None


def replay_sr_raw(
    innovations: Iterable[float], *, threshold: float, delta: float = 1.0
) -> tuple[RawSRTraceRow, ...]:
    if threshold <= 0.0:
        raise ValueError("threshold must be positive")
    if delta != 1.0:
        raise ValueError("Phase-4B freezes delta=1")
    plus = 0.0
    minus = 0.0
    total = 0.0
    trace: list[RawSRTraceRow] = []
    for time, z_value in enumerate(innovations, start=1):
        z = float(z_value)
        pre_plus, pre_minus = plus, minus
        plus = (1.0 + pre_plus) * math.exp(delta * z - 0.5 * delta * delta)
        minus = (1.0 + pre_minus) * math.exp(-delta * z - 0.5 * delta * delta)
        total += z
        plus_crossed = plus >= threshold
        minus_crossed = minus >= threshold
        if plus_crossed and minus_crossed:
            alarm = 1 if plus > minus else (-1 if minus > plus else 2)
        elif plus_crossed:
            alarm = 1
        elif minus_crossed:
            alarm = -1
        else:
            alarm = 0
        reward = z * total if alarm else None
        trace.append(
            RawSRTraceRow(
                time,
                z,
                pre_plus,
                pre_minus,
                plus,
                minus,
                total,
                alarm,
                reward,
            )
        )
        if alarm:
            return tuple(trace)
    raise ValueError("innovation sequence ended before an SR alarm")

