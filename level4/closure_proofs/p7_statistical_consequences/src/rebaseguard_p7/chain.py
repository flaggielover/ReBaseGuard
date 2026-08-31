"""Repeated-cycle re-baselining chain for both frozen detectors.

Stage-D convention, NOT Stage A's:
    frozen stopping rule, no minimum dwell,  tau = inf{t>=1 : alarm}
    truncated reuse window   zbar_m = (1/w) sum_{r<w} z_{tau-r},  w = min(m,tau)
    reference update         e_{j+1} = rho*(e_j + zbar_m) + (1-rho)*fresh
    fresh ~ N(0, 1/m), independent of the stopping event

For ``detector="cusum"``, ``e0=0`` and ``threshold=None`` this consumes the RNG
stream in exactly the same order as ``level4/stage_d/src/chain.py``; the
correspondence test asserts bit-identical ``tau`` and ``e_start``.

Replicates advance in continuous lockstep over time steps, so the cost is
O(n_cycles * ARL) vectorised steps rather than one simulation per cycle.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import CUSUM
from .detectors import make_step


@dataclass(slots=True)
class ChainResult:
    tau: np.ndarray          # (n_rep, n_cycles) int64 cycle lengths
    e_start: np.ndarray      # (n_rep, n_cycles) reference error entering cycle
    direction: np.ndarray    # (n_rep, n_cycles) int8 +1/-1 alarm arm
    detector: str
    m: int
    rho: float
    burn_in: int
    shift: float
    shift_cycle: int

    def post(self, a: np.ndarray) -> np.ndarray:
        return a[:, self.burn_in:]

    @property
    def cycle_arl(self) -> np.ndarray:
        """Per-replicate mean cycle length after burn-in (statistical unit)."""
        return self.post(self.tau).mean(axis=1)

    @property
    def reference_mse(self) -> np.ndarray:
        return (self.post(self.e_start) ** 2).mean(axis=1)


def simulate_chain(*, detector: str, m: int, rho: float, n_rep: int,
                   n_cycles: int, burn_in: int, rng: np.random.Generator,
                   e0: float = 0.0, shift: float = 0.0, shift_cycle: int = -1,
                   threshold: float | None = None,
                   max_steps: int = 40_000_000) -> ChainResult:
    step, _thr, _log = make_step(detector, threshold)
    is_cusum = detector == CUSUM
    L = max(int(m), 1)

    e = np.full(n_rep, float(e0))
    plus = np.zeros(n_rep)
    minus = np.zeros(n_rep)
    buf = np.zeros((n_rep, L))
    pos = np.zeros(n_rep, dtype=np.int64)
    t = np.zeros(n_rep, dtype=np.int64)
    cyc = np.zeros(n_rep, dtype=np.int64)

    tau = np.zeros((n_rep, n_cycles), dtype=np.int64)
    e_start = np.zeros((n_rep, n_cycles))
    direction = np.zeros((n_rep, n_cycles), dtype=np.int8)

    if shift_cycle == 0 and shift != 0.0:
        e -= shift
    e_start[:, 0] = e

    for _ in range(max_steps):
        live = cyc < n_cycles
        if not live.any():
            break
        idx = np.flatnonzero(live)
        z = rng.standard_normal(idx.size) - e[idx]
        np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
        plus[idx] = np_
        minus[idx] = nm_
        buf[idx, pos[idx] % L] = z
        pos[idx] += 1
        t[idx] += 1

        crossed = cu | cd
        if not crossed.any():
            continue
        done = idx[crossed]
        c = cyc[done]
        tau[done, c] = t[done]
        direction[done, c] = np.where(cu[crossed], np.int8(1), np.int8(-1))

        w = np.minimum(L, t[done])
        order = (pos[done][:, None] - 1 - np.arange(L)[None, :]) % L
        lags = np.take_along_axis(buf[done], order, axis=1)
        valid = np.arange(L)[None, :] < w[:, None]
        zbar = np.where(valid, lags, 0.0).sum(axis=1) / w

        fresh = rng.standard_normal(done.size) / np.sqrt(m)
        e[done] = rho * (e[done] + zbar) + (1.0 - rho) * fresh

        plus[done] = 0.0
        minus[done] = 0.0
        buf[done] = 0.0
        pos[done] = 0
        t[done] = 0
        cyc[done] = c + 1

        nxt = cyc[done]
        go = nxt < n_cycles
        if go.any():
            adv = done[go]
            if shift != 0.0:
                hit = adv[cyc[adv] == shift_cycle]
                if hit.size:
                    e[hit] -= shift
            e_start[adv, cyc[adv]] = e[adv]
    else:
        raise RuntimeError(f"{int((cyc < n_cycles).sum())} replicates unfinished")

    del is_cusum
    return ChainResult(tau=tau, e_start=e_start, direction=direction,
                       detector=detector, m=int(m), rho=float(rho),
                       burn_in=int(burn_in), shift=float(shift),
                       shift_cycle=int(shift_cycle))
