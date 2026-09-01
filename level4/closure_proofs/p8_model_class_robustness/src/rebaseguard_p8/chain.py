"""Repeated-cycle re-baselining chain on the addressable primitive field.

Cycle-synchronous, exactly the structure of the repaired Priority-6 simulator
(``p6r2b/simulate.py``): all replicates run cycle ``j`` together, every
observation is fetched **by address** ``(family, detector, m, cycle, index)``
for the whole replicate column and selected by a boolean mask, then the frozen
convention-A update is applied.

The address contains no ``rho``, no shift, no drift pattern and no live-set
position, so every comparison along those axes is a common-random-number
comparison on identical primitive fields.

Frozen semantics
----------------
``tau_j = inf{t >= 1 : alarm}``, both arms updated before an inclusive test,
full reset of arms / buffer / clock at every alarm;
``w = min(m, tau_j)``, ``zbar = (1/w) sum_{r<w} z_{tau-r}``;
``e_{j+1} = rho (e_j + zbar) + (1-rho) mu_fresh``,
``mu_fresh = (1/m) sum_{r<m} Y_r``, ``Y_r`` iid from the family.

Drift
-----
``shift(j)`` is subtracted from the reference error at the *start* of cycle
``j``, which is exactly how a process-mean shift of ``+Delta`` enters in
residual coordinates (Stage D / P7 convention).  ``step`` applies a constant
from ``shift_cycle`` onwards; ``ramp`` applies ``slope * (j - shift_cycle)``.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .detectors import make_step
from . import primitives as PR


@dataclass(slots=True)
class ChainResult:
    tau: np.ndarray          # (n_rep, n_cycles) int64
    e_start: np.ndarray      # (n_rep, n_cycles) reference error entering cycle
    zbar: np.ndarray         # (n_rep, n_cycles)
    shift_at: np.ndarray     # (n_cycles,) applied shift per cycle
    family: str
    detector: str
    m: int
    rho: float
    burn_in: int
    max_block_index: int
    n_monitor_draws: int
    n_overflow_draws: int

    def post(self, a: np.ndarray) -> np.ndarray:
        return a[:, self.burn_in:]

    @property
    def per_replicate_arl(self) -> np.ndarray:
        return self.post(self.tau).mean(axis=1)

    @property
    def per_replicate_ref_mse(self) -> np.ndarray:
        return (self.post(self.e_start) ** 2).mean(axis=1)

    def per_replicate_fap(self, horizon: int) -> np.ndarray:
        return (self.post(self.tau) <= int(horizon)).mean(axis=1)

    @property
    def per_replicate_acf1(self) -> np.ndarray:
        x = self.post(self.e_start)
        x = x - x.mean(axis=1, keepdims=True)
        num = (x[:, :-1] * x[:, 1:]).mean(axis=1)
        den = (x ** 2).mean(axis=1)
        return np.where(den > 0, num / np.maximum(den, 1e-300), 0.0)


def shift_schedule(n_cycles: int, pattern: str = "none", size: float = 0.0,
                   shift_cycle: int = -1, slope: float = 0.0) -> np.ndarray:
    s = np.zeros(int(n_cycles))
    if pattern == "none":
        return s
    j = np.arange(int(n_cycles))
    on = j >= int(shift_cycle)
    if pattern == "step":
        s[on] = float(size)
    elif pattern == "ramp":
        s[on] = float(slope) * (j[on] - int(shift_cycle) + 1)
    else:
        raise ValueError(f"unknown drift pattern {pattern!r}")
    return s


def simulate_chain(*, experiment: str, family: str, detector: str,
                   threshold: float, m: int, rho: float, n_rep: int,
                   n_cycles: int, burn_in: int, e0: float = 0.0,
                   shift: np.ndarray | None = None,
                   max_steps: int = 200_000) -> ChainResult:
    step, _thr = make_step(detector, threshold)
    m = int(m)
    n_rep = int(n_rep)
    n_cycles = int(n_cycles)
    sched = np.zeros(n_cycles) if shift is None else np.asarray(shift, float)
    if sched.shape != (n_cycles,):
        raise ValueError("shift schedule must have one entry per cycle")

    e = np.full(n_rep, float(e0))
    tau = np.zeros((n_rep, n_cycles), np.int64)
    e_start = np.zeros((n_rep, n_cycles))
    zbar_rec = np.zeros((n_rep, n_cycles))
    max_block = 0
    n_mon = 0
    n_ovf = 0

    for j in range(n_cycles):
        e_eff = e - sched[j]                    # residual-coordinate offset
        e_start[:, j] = e_eff
        plus = np.zeros(n_rep)
        minus = np.zeros(n_rep)
        buf = np.zeros((n_rep, m))
        t_cnt = np.zeros(n_rep, np.int64)
        live = np.ones(n_rep, bool)
        t = 0
        while live.any():
            if t >= max_steps:
                raise RuntimeError(f"cycle {j} exceeded {max_steps} steps")
            col = PR.chain_monitor_column(experiment, family, detector, m, j, t,
                                          n_rep, need=live)
            max_block = max(max_block, t // PR.BLOCK_LEN)
            idx = np.flatnonzero(live)
            z = col[idx] - e_eff[idx]
            n_mon += idx.size
            if t >= PR.BLOCK_LEN:
                n_ovf += idx.size
            np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
            plus[idx] = np_
            minus[idx] = nm_
            buf[idx, t % m] = z
            t_cnt[idx] += 1
            crossed = cu | cd
            if crossed.any():
                done = idx[crossed]
                tau[done, j] = t_cnt[done]
                live[done] = False
            t += 1
        w = np.minimum(m, tau[:, j])
        cols = np.arange(m)[None, :]
        order = (tau[:, j][:, None] - 1 - cols) % m
        window = np.take_along_axis(buf, order, axis=1)
        zb = np.where(cols < w[:, None], window, 0.0).sum(axis=1) / w
        zbar_rec[:, j] = zb
        fresh = PR.chain_fresh(experiment, family, detector, m, j, n_rep)
        e = float(rho) * (e_eff + zb) + (1.0 - float(rho)) * fresh
        e = e + sched[j]        # undo the residual offset; drift re-applied next
    return ChainResult(tau=tau, e_start=e_start, zbar=zbar_rec, shift_at=sched,
                       family=family, detector=detector, m=m, rho=float(rho),
                       burn_in=int(burn_in), max_block_index=int(max_block),
                       n_monitor_draws=int(n_mon), n_overflow_draws=int(n_ovf))
