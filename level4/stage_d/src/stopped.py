"""Stage D core: stopped-path statistics for the frozen detectors.

Simulates independent monitoring cycles from a reset state at reference error e
and records everything the Stage D estimands need:

    tau        stopping time
    T_tau      stopped innovation sum, terminal increment included
    z_{tau-i}  the last L innovations of the stopped path
    direction  which arm fired

THE STOPPED-WINDOW CONVENTIONS ARE COMPUTED SEPARATELY AND BOTH RETURNED.
The Stage D blueprint defines the reused statistic with a truncated denominator

    zbar_m = (1/w) sum_{i<w} z_{tau-i},   w = min(m, tau)                 (A)

but *also* asserts the closed form Gamma_m = (1/m) sum_{i<m} gamma_i, which is
the fixed-denominator / zero-padded statistic

    zbar_m = (1/m) sum_{i<min(m,tau)} z_{tau-i}                           (B)

These differ whenever P(tau < m) > 0, and they have different m -> infinity
limits (A tends to E[T_tau^2/tau]; B tends to 0). This module computes both so
the audit can decide on evidence rather than on which reads better.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "level4" / "src"))
from rebaseguard_level4.frozen import (       # noqa: E402  frozen semantics
    H_FROZEN, K_FROZEN, alarm_direction, count_ties, cusum_update,
)

CUSUM = "cusum"
SR = "sr"


@dataclass(slots=True)
class StoppedStats:
    """Accumulated stopped-path statistics; batches combine additively."""
    n: int
    L: int
    sum_tau: float
    sum_tau_sq: float
    sum_T: float
    sum_T_sq: float
    sum_up: int
    # lag weights: sum over cycles of z_{tau-i} * T_tau, and the count with i<tau
    lag_num: np.ndarray            # (L,)
    lag_cnt: np.ndarray            # (L,)
    # convention A and B accumulators, per m in the grid
    m_grid: np.ndarray
    a_num: np.ndarray              # (M,)  sum of (S_w / w) * T
    b_num: np.ndarray              # (M,)  sum of (S_w / m) * T
    a_sq: np.ndarray               # for standard errors
    b_sq: np.ndarray
    # the reuse statistic itself (no T weight), for the INDUCED MAP F(e)
    zbar_num: np.ndarray           # (M,)  sum of S_w / w   (convention A)
    zbar_sq: np.ndarray
    # D3: score-weighted stopped functional, psi in BOTH window and score sum
    psi_num: np.ndarray            # (M,)  sum of (S_w^psi / w) * T_psi
    psi_sq: np.ndarray
    sum_Tsq_over_tau: float        # the m -> inf limit of convention A
    n_ties: int

    def combine(self, other: "StoppedStats") -> "StoppedStats":
        assert self.L == other.L and np.array_equal(self.m_grid, other.m_grid)
        return StoppedStats(
            n=self.n + other.n, L=self.L,
            sum_tau=self.sum_tau + other.sum_tau,
            sum_tau_sq=self.sum_tau_sq + other.sum_tau_sq,
            sum_T=self.sum_T + other.sum_T,
            sum_T_sq=self.sum_T_sq + other.sum_T_sq,
            sum_up=self.sum_up + other.sum_up,
            lag_num=self.lag_num + other.lag_num,
            lag_cnt=self.lag_cnt + other.lag_cnt,
            m_grid=self.m_grid,
            a_num=self.a_num + other.a_num, b_num=self.b_num + other.b_num,
            a_sq=self.a_sq + other.a_sq, b_sq=self.b_sq + other.b_sq,
            zbar_num=self.zbar_num + other.zbar_num,
            zbar_sq=self.zbar_sq + other.zbar_sq,
            psi_num=self.psi_num + other.psi_num,
            psi_sq=self.psi_sq + other.psi_sq,
            sum_Tsq_over_tau=self.sum_Tsq_over_tau + other.sum_Tsq_over_tau,
            n_ties=self.n_ties + other.n_ties)

    # ---- estimands -------------------------------------------------------
    @property
    def arl(self) -> float:
        return self.sum_tau / self.n

    @property
    def E_T_sq(self) -> float:
        return self.sum_T_sq / self.n

    @property
    def gamma_lag(self) -> np.ndarray:
        """gamma_i = E[z_{tau-i} 1{i<tau} T_tau]."""
        return self.lag_num / self.n

    def gamma_m(self, convention: str) -> np.ndarray:
        num = self.a_num if convention == "A" else self.b_num
        return num / self.n

    def gamma_psi(self) -> np.ndarray:
        """Gamma_psi = E[(1/w) sum_{i<w} psi(z_{tau-i}) * sum_{t<=tau} psi(z_t)].

        This is the PROTOCOL-FROZEN D3 estimand. It is NOT normalised by
        E[psi']; see notes/D3_REGULARITY.md, which records that the
        stability-relevant ratio is Gamma_psi / E[psi'] and that the two
        coincide only for the Gaussian, where E[psi'] = 1.
        """
        return self.psi_num / self.n

    def gamma_psi_se(self) -> np.ndarray:
        mean = self.psi_num / self.n
        var = np.maximum(self.psi_sq / self.n - mean ** 2, 0.0)
        return np.sqrt(var / self.n)

    def induced_map(self, e: float) -> np.ndarray:
        """F_{1,m}(e) = e + E_e[zbar_m], the full-reuse induced map.

        X_{tau-i} = R_j + z_{tau-i}, so the reused reference is
        R_{j+1} = R_j + zbar_m and the new error is e_{j+1} = e + zbar_m.
        """
        return e + self.zbar_num / self.n

    def induced_map_se(self) -> np.ndarray:
        mean = self.zbar_num / self.n
        var = np.maximum(self.zbar_sq / self.n - mean ** 2, 0.0)
        return np.sqrt(var / self.n)

    def gamma_m_se(self, convention: str) -> np.ndarray:
        num = self.a_num if convention == "A" else self.b_num
        sq = self.a_sq if convention == "A" else self.b_sq
        mean = num / self.n
        var = np.maximum(sq / self.n - mean ** 2, 0.0)
        return np.sqrt(var / self.n)

    @property
    def gamma_inf_A(self) -> float:
        """E[T_tau^2 / tau], the m -> infinity limit of convention A."""
        return self.sum_Tsq_over_tau / self.n


def _sr_update(rp, rm, z, log_thr):
    """`log_thr` is log(A). Callers pass A in natural units; `simulate_stopped`
    takes the log exactly once, so a threshold can never be mistaken for its
    own logarithm."""
    """Symmetric two-chart Shiryaev-Roberts in the log domain.

    Stored as Y = log(1 + R) with the softplus recursion, exactly as the frozen
    Phase-4B detector definition specifies; algebraically identical to the raw
    recursion and numerically stable.
    """
    log_r_plus = rp + z - 0.5
    log_r_minus = rm - z - 0.5
    return (np.logaddexp(0.0, log_r_plus), np.logaddexp(0.0, log_r_minus),
            log_r_plus >= log_thr, log_r_minus >= log_thr)


def simulate_stopped(
    *, detector: str, threshold: float, e: float, n_paths: int, L: int,
    m_grid: np.ndarray, rng: np.random.Generator,
    innovation: Callable[[np.random.Generator, int], np.ndarray] | None = None,
    k: float = K_FROZEN, max_steps: int = 4_000_000,
    score: Callable[[np.ndarray], np.ndarray] | None = None,
) -> StoppedStats:
    """One batch of independent cycles started from the reset state."""
    m_grid = np.asarray(m_grid, dtype=np.int64)
    M = m_grid.size
    if detector == SR:
        if threshold <= 1.0:
            raise ValueError(
                f"SR threshold A must exceed 1 (got {threshold}); pass A in "
                f"NATURAL units, not log A")
        log_thr = float(np.log(threshold))
    else:
        log_thr = None
    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    total = np.zeros(n_paths)
    buf = np.zeros((n_paths, L))
    # allocated only for D3; when score is None nothing below touches them, so
    # Gaussian results stay bit-identical to runs made before this hook existed
    total_psi = np.zeros(n_paths) if score is not None else None
    buf_psi = np.zeros((n_paths, L)) if score is not None else None
    pos = np.zeros(n_paths, dtype=np.int64)
    active = np.ones(n_paths, dtype=bool)
    tau = np.zeros(n_paths, dtype=np.int64)
    T = np.zeros(n_paths)
    up = np.zeros(n_paths, dtype=bool)
    ties = 0

    for step in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        raw = (rng.standard_normal(idx.size) if innovation is None
               else innovation(rng, idx.size))
        z = raw - e
        if detector == CUSUM:
            np_, nm_, cu, cd = cusum_update(plus[idx], minus[idx], z, k, H_FROZEN)
        elif detector == SR:
            np_, nm_, cu, cd = _sr_update(plus[idx], minus[idx], z, log_thr)
        else:
            raise ValueError(f"unknown detector {detector!r}")
        plus[idx] = np_
        minus[idx] = nm_
        total[idx] += z
        buf[idx, pos[idx] % L] = z
        if score is not None:
            pz = score(z)
            total_psi[idx] += pz
            buf_psi[idx, pos[idx] % L] = pz
        pos[idx] += 1
        if detector == CUSUM and threshold != H_FROZEN:
            cu = np_ >= threshold
            cd = nm_ >= threshold
        crossed = cu | cd
        if not crossed.any():
            continue
        ties += count_ties(cu & crossed, cd & crossed)
        done = idx[crossed]
        tau[done] = step
        T[done] = total[done]
        up[done] = cu[crossed]
        active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} paths did not alarm")

    # ---- lag weights and both window conventions -------------------------
    lag_num = np.zeros(L)
    lag_cnt = np.zeros(L)
    a_num = np.zeros(M); b_num = np.zeros(M)
    a_sq = np.zeros(M); b_sq = np.zeros(M)
    zbar_num = np.zeros(M); zbar_sq = np.zeros(M)
    psi_num = np.zeros(M); psi_sq = np.zeros(M)
    order = (pos[:, None] - 1 - np.arange(L)[None, :]) % L      # newest first
    lags = np.take_along_axis(buf, order, axis=1)               # (n, L)
    valid = np.arange(L)[None, :] < tau[:, None]
    lags = np.where(valid, lags, 0.0)
    lag_num += (lags * T[:, None]).sum(axis=0)
    lag_cnt += valid.sum(axis=0)
    csum = np.cumsum(lags, axis=1)                              # S_j, j=1..L
    if score is not None:
        lags_psi = np.where(valid,
                            np.take_along_axis(buf_psi, order, axis=1), 0.0)
        csum_psi = np.cumsum(lags_psi, axis=1)
        T_psi = total_psi
    for j, m in enumerate(m_grid):
        w = np.minimum(m, tau)
        s = csum[np.arange(tau.size), np.minimum(w, L) - 1]
        va = (s / w) * T
        vb = (s / m) * T
        a_num[j] = va.sum(); b_num[j] = vb.sum()
        a_sq[j] = (va ** 2).sum(); b_sq[j] = (vb ** 2).sum()
        zb = s / w                                  # convention-A window mean
        zbar_num[j] = zb.sum(); zbar_sq[j] = (zb ** 2).sum()
        if score is not None:
            sp = csum_psi[np.arange(tau.size), np.minimum(w, L) - 1]
            vp = (sp / w) * T_psi
            psi_num[j] = vp.sum(); psi_sq[j] = (vp ** 2).sum()

    return StoppedStats(
        n=n_paths, L=L, sum_tau=float(tau.sum()),
        sum_tau_sq=float((tau.astype(float) ** 2).sum()),
        sum_T=float(T.sum()), sum_T_sq=float((T ** 2).sum()),
        sum_up=int(up.sum()), lag_num=lag_num, lag_cnt=lag_cnt,
        m_grid=m_grid, a_num=a_num, b_num=b_num, a_sq=a_sq, b_sq=b_sq,
        zbar_num=zbar_num, zbar_sq=zbar_sq, psi_num=psi_num, psi_sq=psi_sq,
        sum_Tsq_over_tau=float((T ** 2 / tau).sum()), n_ties=ties)


def run_batches(*, detector: str, threshold: float, e: float, n_paths: int,
                batch: int, L: int, m_grid, seed_seq, **kw) -> StoppedStats:
    """Accumulate independent batches; each batch gets its own child seed."""
    total = None
    remaining = n_paths
    for b, child in enumerate(seed_seq.spawn(int(np.ceil(n_paths / batch)))):
        size = min(batch, remaining)
        if size <= 0:
            break
        rng = np.random.Generator(np.random.PCG64(child))
        s = simulate_stopped(detector=detector, threshold=threshold, e=e,
                             n_paths=size, L=L, m_grid=m_grid, rng=rng, **kw)
        total = s if total is None else total.combine(s)
        remaining -= size
    return total
