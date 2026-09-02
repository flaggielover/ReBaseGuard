"""Repeated-cycle re-baselining chain and the single-cycle response ``A(e)``.

Convention **A**, reconstructed from the frozen specification:

* ``Z_t = X_t - e_j``, ``X_t`` iid ``N(0,1)``; the entering reference error
  ``e_j`` is constant within cycle ``j``;
* no minimum dwell: ``tau_j = inf{t >= 1 : alarm}``, inclusive boundary,
  alarm tested after the update;
* truncated reuse window ``w = min(m, tau_j)``, denominator ``w``;
* ``zbar_w`` = mean of the last ``w`` innovations ``Z``;
* ``e_{j+1} = rho (e_j + zbar_w) + (1 - rho) F``, ``F ~ N(0, 1/m)`` drawn
  independently of the stopping event;
* the detector state is reset to the no-headstart initial state at every cycle
  boundary.

Replicates advance in lockstep over time steps, so a cell costs
``O(n_cycles * ARL)`` vectorised steps.  Cycle-boundary bookkeeping is
per-replicate, so replicates that alarm at different times stay independent.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .detectors import make_step


@dataclass(slots=True)
class ChainResult:
    tau: np.ndarray          # (n_rep, n_cycles) int64 cycle lengths
    e_start: np.ndarray      # (n_rep, n_cycles) entering reference error
    detector: str
    m: int
    rho: float

    def arl(self, burn_in: int) -> tuple[float, float]:
        """Per-replicate mean cycle length after ``burn_in`` cycles.

        The statistical unit is the replicate, never the cycle: cycles inside
        one replicate are dependent, replicates are independent.
        """
        per_rep = self.tau[:, burn_in:].mean(axis=1)
        n = per_rep.size
        return float(per_rep.mean()), float(per_rep.std(ddof=1) / np.sqrt(n))

    def cycle_mean(self, index: int) -> tuple[float, float]:
        col = self.tau[:, index].astype(float)
        return float(col.mean()), float(col.std(ddof=1) / np.sqrt(col.size))


def simulate_chain(*, detector: str, m: int, rho: float, n_rep: int,
                   n_cycles: int, seed: int, e0: float = 0.0,
                   defective_sr: bool = False,
                   max_steps: int = 20_000_000) -> ChainResult:
    step, init, _thr, _log = make_step(detector, defective_sr=defective_sr)
    rng = np.random.default_rng(seed)
    L = max(int(m), 1)

    e = np.full(n_rep, float(e0))
    plus, minus = init(n_rep)
    buf = np.zeros((n_rep, L))
    pos = np.zeros(n_rep, dtype=np.int64)
    t = np.zeros(n_rep, dtype=np.int64)
    cyc = np.zeros(n_rep, dtype=np.int64)

    tau = np.zeros((n_rep, n_cycles), dtype=np.int64)
    e_start = np.zeros((n_rep, n_cycles))
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

        w = np.minimum(L, t[done])
        order = (pos[done][:, None] - 1 - np.arange(L)[None, :]) % L
        lags = np.take_along_axis(buf[done], order, axis=1)
        valid = np.arange(L)[None, :] < w[:, None]
        zbar = np.where(valid, lags, 0.0).sum(axis=1) / w

        fresh = rng.standard_normal(done.size) / np.sqrt(m)
        e[done] = rho * (e[done] + zbar) + (1.0 - rho) * fresh

        p0, m0 = init(done.size)
        plus[done] = p0
        minus[done] = m0
        buf[done] = 0.0
        pos[done] = 0
        t[done] = 0
        cyc[done] = c + 1

        adv = done[cyc[done] < n_cycles]
        if adv.size:
            e_start[adv, cyc[adv]] = e[adv]
    else:                                                # pragma: no cover
        raise RuntimeError(f"{int((cyc < n_cycles).sum())} replicates unfinished")

    return ChainResult(tau=tau, e_start=e_start, detector=detector,
                       m=int(m), rho=float(rho))


def response_A(*, detector: str, e: float, n_rep: int, seed: int,
               defective_sr: bool = False,
               max_steps: int = 20_000_000) -> tuple[float, float]:
    """Monte Carlo estimate of ``A(e)`` — one cycle from the reset state.

    ``A(e) = E[tau | entering reference error e]``.  ``A`` does not depend on
    ``m`` or on ``rho``: it is a property of the frozen detector alone.
    """
    step, init, _thr, _log = make_step(detector, defective_sr=defective_sr)
    rng = np.random.default_rng(seed)
    plus, minus = init(n_rep)
    tau = np.zeros(n_rep, dtype=np.int64)
    active = np.ones(n_rep, dtype=bool)
    t = 0
    for _ in range(max_steps):
        if not active.any():
            break
        idx = np.flatnonzero(active)
        t += 1
        z = rng.standard_normal(idx.size) - e
        np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
        plus[idx] = np_
        minus[idx] = nm_
        fired = cu | cd
        hit = idx[fired]
        tau[hit] = t
        active[hit] = False
    else:                                                # pragma: no cover
        raise RuntimeError("response_A did not terminate")
    vals = tau.astype(float)
    return float(vals.mean()), float(vals.std(ddof=1) / np.sqrt(n_rep))
