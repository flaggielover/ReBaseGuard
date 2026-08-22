"""Stage D multi-cycle chain: repeated monitoring with stopped-window reuse.

Stage D convention, NOT Stage A's:
  * frozen stopping rule, NO minimum dwell (tau = inf{t >= 1 : alarm});
  * truncated reuse window zbar_m = (1/w) sum_{i<w} z_{tau-i}, w = min(m, tau);
  * e_{j+1} = rho * (e_j + zbar_m) + (1 - rho) * fresh,  fresh ~ N(0, 1/m).

Stage C's simulator implements Stage A's minimum dwell and so defines a
different map for m > 1; it is deliberately not reused here.

All replicates advance in CONTINUOUS lockstep -- each one rebaselines on its own
alarm and immediately begins its next cycle -- so the loop runs over time steps
rather than over cycles. Cost is O(n_cycles * ARL) steps instead of one full
simulation per cycle.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "level4" / "src"))
from rebaseguard_level4.frozen import (       # noqa: E402
    H_FROZEN, K_FROZEN, cusum_update,
)


@dataclass(slots=True)
class ChainResult:
    tau: np.ndarray          # (n_rep, n_cycles)  cycle lengths
    e_start: np.ndarray      # (n_rep, n_cycles)  reference error entering cycle
    direction: np.ndarray    # (n_rep, n_cycles)  +1 / -1 alarm arm
    burn_in: int
    shift_cycle: int         # -1 if no shift was applied
    m: int
    rho: float

    def _post(self, a: np.ndarray) -> np.ndarray:
        return a[:, self.burn_in:]

    @property
    def cycle_arl(self) -> np.ndarray:
        """Per-replicate mean cycle length, post burn-in (in-control cycles)."""
        return self._post(self.tau).mean(axis=1)

    @property
    def reference_mse(self) -> np.ndarray:
        return (self._post(self.e_start) ** 2).mean(axis=1)

    @property
    def e_acf1(self) -> np.ndarray:
        e = self._post(self.e_start)
        a, b = e[:, :-1], e[:, 1:]
        am, bm = a.mean(axis=1, keepdims=True), b.mean(axis=1, keepdims=True)
        num = ((a - am) * (b - bm)).mean(axis=1)
        den = np.sqrt(((a - am) ** 2).mean(axis=1) * ((b - bm) ** 2).mean(axis=1))
        return np.where(den > 0, num / np.maximum(den, 1e-300), 0.0)

    @property
    def direction_acf1(self) -> np.ndarray:
        d = self._post(self.direction).astype(float)
        a, b = d[:, :-1], d[:, 1:]
        am, bm = a.mean(axis=1, keepdims=True), b.mean(axis=1, keepdims=True)
        num = ((a - am) * (b - bm)).mean(axis=1)
        den = np.sqrt(((a - am) ** 2).mean(axis=1) * ((b - bm) ** 2).mean(axis=1))
        return np.where(den > 0, num / np.maximum(den, 1e-300), 0.0)

    @property
    def tau_at_shift(self) -> np.ndarray:
        if self.shift_cycle < 0:
            raise ValueError("no shift was applied in this run")
        return self.tau[:, self.shift_cycle]


def simulate_chain(*, m: int, rho: float, n_rep: int, n_cycles: int,
                   burn_in: int, rng: np.random.Generator,
                   shift: float = 0.0, shift_cycle: int = -1,
                   max_steps: int = 20_000_000) -> ChainResult:
    L = max(int(m), 1)
    e = np.zeros(n_rep)
    plus = np.zeros(n_rep)
    minus = np.zeros(n_rep)
    buf = np.zeros((n_rep, L))
    pos = np.zeros(n_rep, dtype=np.int64)
    t = np.zeros(n_rep, dtype=np.int64)          # steps inside the current cycle
    cyc = np.zeros(n_rep, dtype=np.int64)        # which cycle each replicate is in

    tau = np.zeros((n_rep, n_cycles), dtype=np.int64)
    e_start = np.zeros((n_rep, n_cycles))
    direction = np.zeros((n_rep, n_cycles), dtype=np.int8)

    rows = np.arange(n_rep)
    if shift_cycle == 0 and shift != 0.0:
        e -= shift
    e_start[:, 0] = e

    for _ in range(max_steps):
        live = cyc < n_cycles
        if not live.any():
            break
        idx = np.flatnonzero(live)
        z = rng.standard_normal(idx.size) - e[idx]
        np_, nm_, cu, cd = cusum_update(plus[idx], minus[idx], z, K_FROZEN, H_FROZEN)
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
        direction[done, c] = np.where(np_[crossed] >= H_FROZEN, 1, -1)

        # truncated window mean over the last w = min(m, tau) innovations
        w = np.minimum(L, t[done])
        order = (pos[done][:, None] - 1 - np.arange(L)[None, :]) % L
        lags = np.take_along_axis(buf[done], order, axis=1)
        valid = np.arange(L)[None, :] < w[:, None]
        zbar = np.where(valid, lags, 0.0).sum(axis=1) / w

        fresh = rng.standard_normal(done.size) / np.sqrt(m)
        e[done] = rho * (e[done] + zbar) + (1.0 - rho) * fresh

        # reset detector state and begin the next cycle
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

    del rows
    return ChainResult(tau=tau, e_start=e_start, direction=direction,
                       burn_in=burn_in, shift_cycle=shift_cycle,
                       m=int(m), rho=float(rho))
