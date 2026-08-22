"""Slow, deliberately naive scalar reference implementations.

These exist only to be *disagreed with*.  They are written from the frozen
specification in plain Python loops with no vectorisation tricks, and the tests
assert that the fast simulators reproduce them exactly.  Never optimise this
module; if it becomes slow, run it on less data.
"""

from __future__ import annotations

from typing import Iterator, Sequence

import numpy as np

from .frozen import H_FROZEN, K_FROZEN, step_scalar
from .streams import STREAM_FRESH, STREAM_OBS, generator


def run_one_cycle_scalar(
    e: float,
    x_draws: Iterator[float],
    *,
    m: int,
    k: float = K_FROZEN,
    h: float = H_FROZEN,
) -> dict[str, float]:
    """Monitor one cycle from reference offset ``e``; return the alarm record."""
    plus = minus = 0.0
    t_sum = 0.0
    window: list[float] = []
    tau = 0
    while True:
        tau += 1
        x = float(next(x_draws))
        z = x - e
        t_sum += z
        window.append(z)
        plus, minus, alarm = step_scalar(plus, minus, z, k, h)
        if alarm != 0 and tau >= m:
            return {
                "tau": tau,
                "direction": alarm,
                "z_tau": z,
                "t_tau": t_sum,
                "window_sum": float(sum(window[-m:])),
                "mu_reuse": e + float(sum(window[-m:])) / m,
                "s_plus_terminal": plus,
                "s_minus_terminal": minus,
            }


def replay_replicate_scalar(
    *,
    master_seed: int,
    replicate: int,
    n_cycles_total: int,
    m: int,
    rho: float,
    e0: float = 0.0,
    k: float = K_FROZEN,
    h: float = H_FROZEN,
    draw_budget: int = 4_000_000,
) -> list[dict[str, float]]:
    """Independently replay one replicate of ``simulate_multicycle``.

    Reconstructs the replicate's own observation and fresh streams directly from
    the seed rule and walks the chain scalar-wise.  This is the strongest
    available reproducibility check: it never touches the vectorised code path.
    """
    obs = generator(master_seed, STREAM_OBS, replicate).standard_normal(draw_budget)
    fresh = generator(master_seed, STREAM_FRESH, replicate)
    it = iter(obs.tolist())
    fresh_scale = 1.0 / np.sqrt(m)
    e = float(e0)
    rows: list[dict[str, float]] = []
    for _ in range(n_cycles_total):
        record = run_one_cycle_scalar(e, it, m=m, k=k, h=h)
        mu_fresh = float(fresh.standard_normal()) * fresh_scale
        e_next = rho * record["mu_reuse"] + (1.0 - rho) * mu_fresh
        record["e_prev"] = e
        record["mu_fresh"] = mu_fresh
        record["e_next"] = e_next
        rows.append(record)
        e = e_next
    return rows


def gamma_reference_scalar(
    innovations: Sequence[Sequence[float]],
    *,
    k: float = K_FROZEN,
    h: float = H_FROZEN,
) -> list[tuple[int, float, float]]:
    """``(tau, Z_tau, T_tau)`` per path at e = 0, straight from the frozen spec."""
    out: list[tuple[int, float, float]] = []
    for path in innovations:
        plus = minus = 0.0
        t_sum = 0.0
        for tau, z in enumerate(path, start=1):
            z = float(z)
            t_sum += z
            plus, minus, alarm = step_scalar(plus, minus, z, k, h)
            if alarm != 0:
                out.append((tau, z, t_sum))
                break
        else:
            raise ValueError("path ended before an alarm")
    return out
