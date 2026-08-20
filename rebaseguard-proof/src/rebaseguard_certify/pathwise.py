"""Independent deterministic path replay for convention auditing.

This module deliberately does not call :func:`model.step` or
:func:`model.oracle_step`. It is diagnostic reference code, not proof code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class TraceRow:
    time: int
    z: float
    pre_plus: float
    pre_minus: float
    pre_t: float
    post_plus: float
    post_minus: float
    post_t: float
    alarm: int
    terminal_reward: float | None


def reference_replay(
    innovations: Iterable[float], *, k: float = 0.5, h: float = 5.0
) -> list[TraceRow]:
    """Replay a path from first principles and stop after the first alarm."""

    plus = 0.0
    minus = 0.0
    total = 0.0
    trace: list[TraceRow] = []
    for time, z_value in enumerate(innovations, start=1):
        z = float(z_value)
        pre_plus, pre_minus, pre_t = plus, minus, total
        plus = max(0.0, pre_plus + z - k)
        minus = max(0.0, pre_minus - z - k)
        total = pre_t + z
        alarm = 1 if plus >= h else (-1 if minus >= h else 0)
        reward = z * total if alarm else None
        trace.append(
            TraceRow(
                time,
                z,
                pre_plus,
                pre_minus,
                pre_t,
                plus,
                minus,
                total,
                alarm,
                reward,
            )
        )
        if alarm:
            return trace
    raise ValueError("innovation sequence ended before an alarm")
