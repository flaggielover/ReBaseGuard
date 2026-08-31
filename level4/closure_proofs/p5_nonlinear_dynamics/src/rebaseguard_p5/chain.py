"""P5 chain in raw-mean form, plus the audited P7 cross-check.

``simulate_chain_raw`` is the frozen Stage-D chain with the ONLY change being
that the reuse buffer holds ``raw_t`` and the update is written

    e_{j+1} = rho * Rbar_w + (1 - rho) * fresh

instead of ``rho*(e_j + zbar_m) + (1-rho)*fresh``.  The RNG is consumed in
exactly the same order as ``rebaseguard_p7.chain.simulate_chain``, so the two
trajectories agree to floating-point rounding; ``tests/test_correspondence.py``
asserts this.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rebaseguard_p7.detectors import make_step


@dataclass(slots=True)
class ChainResult:
    tau: np.ndarray
    e_start: np.ndarray
    direction: np.ndarray
    detector: str
    m: int
    rho: float
    burn_in: int
    e0: np.ndarray

    def post(self, a):
        return a[:, self.burn_in:]


def simulate_chain_raw(*, detector: str, m: int, rho: float, n_rep: int,
                       n_cycles: int, burn_in: int, rng: np.random.Generator,
                       e0=0.0, threshold: float | None = None,
                       max_steps: int = 40_000_000) -> ChainResult:
    step, _thr, _log = make_step(detector, threshold)
    L = max(int(m), 1)
    e = np.full(n_rep, 0.0) + np.asarray(e0, dtype=float)
    e0_arr = e.copy()

    plus = np.zeros(n_rep)
    minus = np.zeros(n_rep)
    buf = np.zeros((n_rep, L))
    pos = np.zeros(n_rep, dtype=np.int64)
    t = np.zeros(n_rep, dtype=np.int64)
    cyc = np.zeros(n_rep, dtype=np.int64)

    tau = np.zeros((n_rep, n_cycles), dtype=np.int64)
    e_start = np.zeros((n_rep, n_cycles))
    direction = np.zeros((n_rep, n_cycles), dtype=np.int8)
    e_start[:, 0] = e

    for _ in range(max_steps):
        live = cyc < n_cycles
        if not live.any():
            break
        idx = np.flatnonzero(live)
        raw = rng.standard_normal(idx.size)
        z = raw - e[idx]
        np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
        plus[idx] = np_
        minus[idx] = nm_
        buf[idx, pos[idx] % L] = raw
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
        rbar = np.where(valid, lags, 0.0).sum(axis=1) / w

        fresh = rng.standard_normal(done.size) / np.sqrt(m)
        e[done] = rho * rbar + (1.0 - rho) * fresh

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
            e_start[adv, cyc[adv]] = e[adv]
    else:
        raise RuntimeError("unfinished replicates")
    return ChainResult(tau=tau, e_start=e_start, direction=direction,
                       detector=detector, m=int(m), rho=float(rho),
                       burn_in=int(burn_in), e0=e0_arr)
