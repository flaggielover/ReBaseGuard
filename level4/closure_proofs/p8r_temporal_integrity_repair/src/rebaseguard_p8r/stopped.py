"""Independent single monitoring cycles from a reset detector state.

One cycle: start both detector arms at zero, feed residuals
``z_t = eps_t - e_eff`` with ``e_eff = e - delta``, stop at the first inclusive
post-update alarm ``tau``, and record everything the P8 estimands need.

Recorded per path
-----------------
``tau``       run length (terminal increment included)
``T``         ``sum_{t<=tau} z_t``                       (Gaussian score sum)
``Psi``       ``sum_{t<=tau} psi(z_t)``                  (family score sum)
``lag_z``     ``z_{tau-r}`` for ``r < L``, zero where ``r >= tau``
``lag_psi``   ``psi(z_{tau-r})`` likewise
``valid``     ``1{r < tau}``
``up``        plus-arm alarm indicator
``tie``       exact simultaneous crossing (recorded, never silently assigned)

Every estimand is a mean of a per-path functional of these, so batch-means
standard errors and replicate-level bootstraps are both available.

P8R provenance: byte-for-byte the P8 module `.../rebaseguard_p8/stopped.py` apart from this note.  The P8 adjudication verified this window extraction as `WINDOW_EXTRACTION = EXACT` against an independent naive reference (max discrepancy 8.9e-16).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import families as _families
from .detectors import make_step
from .primitives import ROWS_PER_BLOCK, stopped_block, BLOCK_LEN


@dataclass(slots=True)
class StoppedSample:
    tau: np.ndarray        # (n,) int64
    T: np.ndarray          # (n,)
    Psi: np.ndarray        # (n,)
    lag_z: np.ndarray      # (n, L)
    lag_psi: np.ndarray    # (n, L)
    valid: np.ndarray      # (n, L) bool
    up: np.ndarray         # (n,) bool
    n_ties: int
    family: str
    detector: str
    threshold: float
    e: float
    delta: float
    L: int

    def concat(self, other: "StoppedSample") -> "StoppedSample":
        assert self.L == other.L and self.family == other.family
        return StoppedSample(
            tau=np.concatenate([self.tau, other.tau]),
            T=np.concatenate([self.T, other.T]),
            Psi=np.concatenate([self.Psi, other.Psi]),
            lag_z=np.concatenate([self.lag_z, other.lag_z]),
            lag_psi=np.concatenate([self.lag_psi, other.lag_psi]),
            valid=np.concatenate([self.valid, other.valid]),
            up=np.concatenate([self.up, other.up]),
            n_ties=self.n_ties + other.n_ties,
            family=self.family, detector=self.detector,
            threshold=self.threshold, e=self.e, delta=self.delta, L=self.L)

    # ---- window statistics ------------------------------------------------
    def zbar(self, m: int, convention: str = "A") -> np.ndarray:
        """Convention-A (``denominator w = min(m,tau)``) or B (``m``) window."""
        m = int(m)
        if m > self.L:
            raise ValueError(f"m={m} exceeds recorded lag depth L={self.L}")
        s = np.where(self.valid[:, :m], self.lag_z[:, :m], 0.0).sum(axis=1)
        if convention == "A":
            return s / np.minimum(m, self.tau)
        if convention == "B":
            return s / m
        raise ValueError("convention must be 'A' or 'B'")

    def psibar(self, m: int, convention: str = "A") -> np.ndarray:
        """Score-transformed window (the Stage-D D3 estimand's first factor)."""
        m = int(m)
        s = np.where(self.valid[:, :m], self.lag_psi[:, :m], 0.0).sum(axis=1)
        if convention == "A":
            return s / np.minimum(m, self.tau)
        return s / m


def simulate_row_block(*, experiment: str, family: str, detector: str,
                       threshold: float, batch: int, row_block: int,
                       n_paths: int = ROWS_PER_BLOCK, L: int = 20,
                       e: float = 0.0, delta: float = 0.0,
                       max_steps: int = 4_000_000) -> StoppedSample:
    """One addressable row block of independent cycles."""
    step, thr = make_step(detector, threshold)
    psi = _families.get(family).psi
    e_eff = float(e) - float(delta)
    n = int(n_paths)

    plus = np.zeros(n)
    minus = np.zeros(n)
    total = np.zeros(n)
    total_psi = np.zeros(n)
    buf_z = np.zeros((n, L))
    buf_p = np.zeros((n, L))
    pos = np.zeros(n, dtype=np.int64)
    active = np.ones(n, dtype=bool)
    tau = np.zeros(n, dtype=np.int64)
    T = np.zeros(n)
    Psi = np.zeros(n)
    up = np.zeros(n, dtype=bool)
    n_ties = 0

    for t in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        b, off = divmod(t - 1, BLOCK_LEN)
        col = stopped_block(experiment, family, batch, row_block, b,
                            n_rows=n)[:, off]          # address -> value
        z = col[idx] - e_eff                           # live selection AFTER
        pz = psi(z)
        np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
        plus[idx] = np_
        minus[idx] = nm_
        total[idx] += z
        total_psi[idx] += pz
        slot = pos[idx] % L
        buf_z[idx, slot] = z
        buf_p[idx, slot] = pz
        pos[idx] += 1
        crossed = cu | cd
        if not crossed.any():
            continue
        n_ties += int((cu & cd).sum())
        done = idx[crossed]
        tau[done] = t
        T[done] = total[done]
        Psi[done] = total_psi[done]
        up[done] = cu[crossed]
        active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} paths did not alarm")

    order = (pos[:, None] - 1 - np.arange(L)[None, :]) % L      # newest first
    lag_z = np.take_along_axis(buf_z, order, axis=1)
    lag_psi = np.take_along_axis(buf_p, order, axis=1)
    valid = np.arange(L)[None, :] < tau[:, None]
    return StoppedSample(tau=tau, T=T, Psi=Psi,
                         lag_z=np.where(valid, lag_z, 0.0),
                         lag_psi=np.where(valid, lag_psi, 0.0),
                         valid=valid, up=up, n_ties=n_ties, family=family,
                         detector=detector, threshold=float(thr), e=float(e),
                         delta=float(delta), L=L)


def simulate_batch(*, experiment: str, family: str, detector: str,
                   threshold: float, batch: int, n_row_blocks: int,
                   L: int = 20, e: float = 0.0, delta: float = 0.0
                   ) -> StoppedSample:
    """``n_row_blocks * ROWS_PER_BLOCK`` cycles at one batch address."""
    out = None
    for rb in range(int(n_row_blocks)):
        s = simulate_row_block(experiment=experiment, family=family,
                               detector=detector, threshold=threshold,
                               batch=batch, row_block=rb, L=L, e=e, delta=delta)
        out = s if out is None else out.concat(s)
    return out
