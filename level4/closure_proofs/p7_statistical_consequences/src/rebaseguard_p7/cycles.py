"""Independent single monitoring cycles from a reset detector state.

This is the P7 restatement of the Stage-D stopped-path object.  It records only
what P7 needs (run length, convention-A window mean, stopped sum, alarm arm) and
supports both frozen detectors and an out-of-control location shift.

Conventions (identical to Stage D / P1 / P2):
    innovation      z_t = raw_t - e_eff,  raw_t iid N(0,1)
    e_eff           = e - delta        (a shift +delta of the process mean is
                                        exactly a reference-error offset -delta,
                                        which is how Stage D's chain applies it)
    tau             = inf{t>=1 : alarm after the update at t}, inclusive test
    T_tau           = sum_{t=1}^{tau} z_t, terminal increment included
    w               = min(m, tau)
    zbar_m          = (1/w) sum_{r=0}^{w-1} z_{tau-r}      (convention A)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .detectors import make_step


@dataclass(slots=True)
class CycleSample:
    tau: np.ndarray        # (n,) int64 run lengths
    zbar: np.ndarray       # (M, n) convention-A truncated window mean per m
    T: np.ndarray          # (n,) stopped innovation sum
    up: np.ndarray         # (n,) bool, plus-arm alarm
    e: float
    delta: float
    m_grid: tuple[int, ...]
    detector: str

    def zbar_for(self, m: int) -> np.ndarray:
        return self.zbar[self.m_grid.index(int(m))]


def simulate_cycles(*, detector: str, e: float, delta: float = 0.0,
                    n_paths: int, m_grid, rng: np.random.Generator,
                    threshold: float | None = None,
                    max_steps: int = 2_000_000) -> CycleSample:
    """One batch of independent cycles started from the reset state."""
    step, _thr, _log = make_step(detector, threshold)
    m_grid = tuple(int(v) for v in np.atleast_1d(m_grid))
    L = max(m_grid)
    e_eff = float(e) - float(delta)

    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    total = np.zeros(n_paths)
    buf = np.zeros((n_paths, L))
    pos = np.zeros(n_paths, dtype=np.int64)
    active = np.ones(n_paths, dtype=bool)
    tau = np.zeros(n_paths, dtype=np.int64)
    T = np.zeros(n_paths)
    up = np.zeros(n_paths, dtype=bool)

    for t in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        z = rng.standard_normal(idx.size) - e_eff
        np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
        plus[idx] = np_
        minus[idx] = nm_
        total[idx] += z
        buf[idx, pos[idx] % L] = z
        pos[idx] += 1
        crossed = cu | cd
        if not crossed.any():
            continue
        done = idx[crossed]
        tau[done] = t
        T[done] = total[done]
        up[done] = cu[crossed]
        active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} paths did not alarm")

    order = (pos[:, None] - 1 - np.arange(L)[None, :]) % L      # newest first
    lags = np.take_along_axis(buf, order, axis=1)
    valid = np.arange(L)[None, :] < tau[:, None]
    lags = np.where(valid, lags, 0.0)
    csum = np.cumsum(lags, axis=1)
    rows = np.arange(n_paths)
    zbar = np.empty((len(m_grid), n_paths))
    for j, m in enumerate(m_grid):
        w = np.minimum(m, tau)
        zbar[j] = csum[rows, w - 1] / w
    return CycleSample(tau=tau, zbar=zbar, T=T, up=up, e=float(e),
                       delta=float(delta), m_grid=m_grid, detector=detector)


def run_cycle_batches(*, detector: str, e: float, delta: float = 0.0,
                      n_paths: int, m_grid, seed_seq, batch: int = 100_000,
                      threshold: float | None = None) -> CycleSample:
    """Accumulate independent batches, one child seed each (Stage-D pattern)."""
    parts, remaining = [], n_paths
    n_batches = int(np.ceil(n_paths / batch))
    for child in seed_seq.spawn(n_batches):
        size = min(batch, remaining)
        if size <= 0:
            break
        rng = np.random.Generator(np.random.PCG64(child))
        parts.append(simulate_cycles(detector=detector, e=e, delta=delta,
                                     n_paths=size, m_grid=m_grid, rng=rng,
                                     threshold=threshold))
        remaining -= size
    return CycleSample(
        tau=np.concatenate([p.tau for p in parts]),
        zbar=np.concatenate([p.zbar for p in parts], axis=1),
        T=np.concatenate([p.T for p in parts]),
        up=np.concatenate([p.up for p in parts]),
        e=float(e), delta=float(delta), m_grid=parts[0].m_grid,
        detector=detector)
