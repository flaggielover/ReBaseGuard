"""Stage E monitoring engine: frozen-form CUSUM on a real residual stream with
post-alarm reference reuse.

Protocol S8. On an alarm at index tau_j:

    mu_reuse = mean of the last w = min(m, cycle length) residuals up to tau_j
    mu_fresh = mean of the m residuals AFTER tau_j        (settling block)
    R_{j+1}  = rho * mu_reuse + (1 - rho) * mu_fresh

and the next cycle begins at tau_j + 1 + m. EVERY policy consumes exactly the
same observations, including the fresh settling block, in every cycle: the
policies differ only in rho.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

K_FROZEN = 0.5
M_WINDOW = 20
BURN_CYCLES = 3
LOCAL_MEAN_HORIZON = 100


@dataclass(slots=True)
class Cycle:
    start: int
    alarm: int
    length: int
    direction: int
    reference: float          # R_j in force during the cycle
    local_mean: float         # mean of the stream the cycle actually faced


@dataclass(slots=True)
class MonitorRun:
    cycles: list[Cycle] = field(default_factory=list)
    n_obs: int = 0
    truncated: bool = False   # stream ended mid-cycle

    @property
    def alarm_indices(self) -> np.ndarray:
        return np.array([c.alarm for c in self.cycles], dtype=np.int64)

    def post_burn(self, burn: int = BURN_CYCLES) -> list[Cycle]:
        return self.cycles[burn:]


def run_monitor(stream: np.ndarray, *, scale: float, threshold: float,
                rho: float, m: int = M_WINDOW, r0: float,
                start: int = 0, stop: int | None = None,
                k: float = K_FROZEN) -> MonitorRun:
    """Run the reuse chain over `stream[start:stop]`.

    `stream` is the residual sequence ALREADY carrying any drift injection --
    the monitor sees exactly what an operator would see.
    """
    n = stream.size if stop is None else min(stop, stream.size)
    out = MonitorRun(n_obs=max(0, n - start))
    R = float(r0)
    t = int(start)
    while t < n:
        cyc_start = t
        sp = mn = 0.0
        alarm = -1
        direction = 0
        while t < n:
            z = (stream[t] - R) / scale
            sp = max(0.0, sp + z - k)
            mn = max(0.0, mn - z - k)
            if sp >= threshold or mn >= threshold:
                alarm = t
                direction = 1 if sp >= threshold else -1
                break
            t += 1
        if alarm < 0:                       # stream ended before an alarm
            out.truncated = True
            break
        length = alarm - cyc_start + 1
        lo = max(cyc_start, alarm - min(m, length) + 1)
        mu_reuse = float(stream[lo:alarm + 1].mean())

        fresh_lo, fresh_hi = alarm + 1, alarm + 1 + m
        if fresh_hi > n:                    # not enough data for the fresh block
            out.truncated = True
            hz = stream[alarm + 1:min(alarm + 1 + LOCAL_MEAN_HORIZON, n)]
            out.cycles.append(Cycle(cyc_start, alarm, length, direction, R,
                                    float(hz.mean()) if hz.size else float("nan")))
            break
        mu_fresh = float(stream[fresh_lo:fresh_hi].mean())

        hz = stream[cyc_start:min(cyc_start + LOCAL_MEAN_HORIZON, n)]
        out.cycles.append(Cycle(cyc_start, alarm, length, direction, R,
                                float(hz.mean())))
        R = rho * mu_reuse + (1.0 - rho) * mu_fresh
        t = fresh_hi
    return out


def first_alarm_at_or_after(stream: np.ndarray, *, t0: int, scale: float,
                            threshold: float, rho: float, r0: float,
                            start: int, stop: int, m: int = M_WINDOW) -> int | None:
    """Detection delay support: index of the first alarm at or after `t0`."""
    run = run_monitor(stream, scale=scale, threshold=threshold, rho=rho,
                      m=m, r0=r0, start=start, stop=stop)
    for c in run.cycles:
        if c.alarm >= t0:
            return c.alarm
    return None
