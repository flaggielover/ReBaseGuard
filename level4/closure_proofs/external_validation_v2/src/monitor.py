"""Frozen CUSUM monitor with matched post-alarm reference policies."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Cycle:
    start: int
    alarm: int
    length: int
    direction: int
    reference: float


@dataclass(frozen=True)
class MonitorRun:
    cycles: tuple[Cycle, ...]
    reference_path: np.ndarray
    start: int
    stop: int
    truncated: bool

    @property
    def alarms(self) -> np.ndarray:
        return np.asarray([cycle.alarm for cycle in self.cycles], dtype=np.int64)


def run_monitor(stream: np.ndarray, *, scale: float, threshold: float,
                rho: float, r0: float, start: int = 0, stop: int | None = None,
                k: float = 0.5, m: int = 20) -> MonitorRun:
    """Monitor `stream[start:stop]`; every policy consumes the fresh block."""
    stop = stream.size if stop is None else min(stop, stream.size)
    references = np.full(max(0, stop - start), np.nan)
    cycles = []
    reference = float(r0)
    t = int(start)
    truncated = False
    while t < stop:
        cycle_start = t
        positive = negative = 0.0
        while t < stop:
            references[t - start] = reference
            z = (stream[t] - reference) / scale
            positive = max(0.0, positive + z - k)
            negative = max(0.0, negative - z - k)
            if positive >= threshold or negative >= threshold:
                direction = 1 if positive >= threshold else -1
                length = t - cycle_start + 1
                cycles.append(Cycle(cycle_start, t, length, direction, reference))
                reuse_lo = max(cycle_start, t - min(m, length) + 1)
                reuse = float(stream[reuse_lo:t + 1].mean())
                fresh_lo, fresh_hi = t + 1, t + 1 + m
                references[fresh_lo - start:min(fresh_hi, stop) - start] = reference
                if fresh_hi > stop:
                    truncated = True
                    t = stop
                    break
                fresh = float(stream[fresh_lo:fresh_hi].mean())
                reference = rho * reuse + (1.0 - rho) * fresh
                t = fresh_hi
                break
            t += 1
        else:
            truncated = True
    return MonitorRun(tuple(cycles), references, start, stop, truncated)


def first_alarm_delay(run: MonitorRun, onset: int, cap: int) -> tuple[int, bool]:
    hit = next((cycle.alarm for cycle in run.cycles if cycle.alarm >= onset), None)
    if hit is None or hit - onset > cap:
        return cap, True
    return int(hit - onset), False
