"""The exact one-step reference-error kernel, in raw-mean form.

DEFINITION_AUDIT.md derives the identity that this module measures.  Writing
``raw_t`` for the iid N(0,1) draw at step ``t`` of a cycle and ``z_t = raw_t - e``
for the innovation the detector sees when the entering reference error is ``e``,
the frozen Stage-D update

    e_{j+1} = rho * (e_j + zbar_m) + (1 - rho) * fresh,
    zbar_m  = (1/w) sum_{r<w} z_{tau-r},   w = min(m, tau),  fresh ~ N(0, 1/m)

collapses, because ``e_j + zbar_m = (1/w) sum_{r<w} raw_{tau-r}``, to

    e_{j+1} = rho * Rbar_w + (1 - rho) * fresh,
    Rbar_w  = (1/w) sum_{r<w} raw_{tau-r}.

Hence the whole ``rho`` dependence of the conditional-mean map is a scalar:

    M_{D,m,rho}(e) = rho * R_{D,m}(e),      R_{D,m}(e) := E[Rbar_w | e]
    V_{D,m,rho}(e) = rho^2 * S_{D,m}(e) + (1-rho)^2 / m,
                     S_{D,m}(e) := Var(Rbar_w | e).

This module estimates ``R`` and ``S`` directly.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rebaseguard_p7.detectors import make_step


@dataclass(slots=True)
class RawSample:
    """One batch of independent cycles started from the reset state at ``e``."""
    e: float
    detector: str
    m_grid: tuple[int, ...]
    tau: np.ndarray        # (n,) int64
    rbar: np.ndarray       # (M, n) raw-window mean per m
    up: np.ndarray         # (n,) bool


def simulate_raw_cycles(*, detector: str, e: float, n_paths: int, m_grid,
                        rng: np.random.Generator,
                        threshold: float | None = None,
                        max_steps: int = 2_000_000) -> RawSample:
    """Frozen cycle simulation recording the terminal RAW window mean.

    Identical stopping/window semantics to ``rebaseguard_p7.cycles``: the only
    change is that the buffered quantity is ``raw_t`` instead of ``z_t``.
    """
    step, _thr, _log = make_step(detector, threshold)
    m_grid = tuple(int(v) for v in np.atleast_1d(m_grid))
    L = max(m_grid)
    e = float(e)

    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    buf = np.zeros((n_paths, L))
    pos = np.zeros(n_paths, dtype=np.int64)
    active = np.ones(n_paths, dtype=bool)
    tau = np.zeros(n_paths, dtype=np.int64)
    up = np.zeros(n_paths, dtype=bool)

    for t in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        raw = rng.standard_normal(idx.size)
        z = raw - e
        np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
        plus[idx] = np_
        minus[idx] = nm_
        buf[idx, pos[idx] % L] = raw
        pos[idx] += 1
        crossed = cu | cd
        if not crossed.any():
            continue
        done = idx[crossed]
        tau[done] = t
        up[done] = cu[crossed]
        active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} paths did not alarm at e={e}")

    order = (pos[:, None] - 1 - np.arange(L)[None, :]) % L      # newest first
    lags = np.take_along_axis(buf, order, axis=1)
    valid = np.arange(L)[None, :] < tau[:, None]
    csum = np.cumsum(np.where(valid, lags, 0.0), axis=1)
    rows = np.arange(n_paths)
    rbar = np.empty((len(m_grid), n_paths))
    for j, m in enumerate(m_grid):
        w = np.minimum(m, tau)
        rbar[j] = csum[rows, w - 1] / w
    return RawSample(e=e, detector=detector, m_grid=m_grid, tau=tau,
                     rbar=rbar, up=up)


def child_rng(seed_family: int, detector: str, tag: int, index: int):
    """Deterministic, reproducible, hash-free child generator."""
    from . import DETECTOR_CODE
    ss = np.random.SeedSequence([int(seed_family), DETECTOR_CODE[detector],
                                 int(tag), int(index)])
    return np.random.Generator(np.random.PCG64(ss))


def raw_map_point(*, detector: str, e: float, m_grid, n_paths: int,
                  n_batches: int, seed_family: int, tag: int,
                  threshold: float | None = None):
    """Batch-mean estimate of R(e)=E[Rbar], S(e)=Var(Rbar) and E[tau].

    Statistical unit = independent batch, so the reported standard errors are
    batch standard errors over ``n_batches`` independent replicates.
    """
    m_grid = tuple(int(v) for v in np.atleast_1d(m_grid))
    means = np.empty((n_batches, len(m_grid)))
    varis = np.empty((n_batches, len(m_grid)))
    m4 = np.empty((n_batches, len(m_grid)))
    taus = np.empty(n_batches)
    tau1 = np.empty(n_batches)
    for b in range(n_batches):
        rng = child_rng(seed_family, detector, tag, b)
        s = simulate_raw_cycles(detector=detector, e=e, n_paths=n_paths,
                                m_grid=m_grid, rng=rng, threshold=threshold)
        means[b] = s.rbar.mean(axis=1)
        varis[b] = s.rbar.var(axis=1, ddof=1)
        m4[b] = (s.rbar ** 4).mean(axis=1)
        taus[b] = s.tau.mean()
        tau1[b] = (s.tau == 1).mean()
    z = 1.959963984540054
    out = {"e": float(e), "detector": detector, "m_grid": list(m_grid),
           "n_paths": int(n_paths), "n_batches": int(n_batches),
           "tau_mean": float(taus.mean()),
           "tau_se": float(taus.std(ddof=1) / np.sqrt(n_batches)),
           "p_tau1": float(tau1.mean()), "z95": z, "per_m": []}
    for j, m in enumerate(m_grid):
        R = float(means[:, j].mean())
        Rse = float(means[:, j].std(ddof=1) / np.sqrt(n_batches))
        S = float(varis[:, j].mean())
        Sse = float(varis[:, j].std(ddof=1) / np.sqrt(n_batches))
        out["per_m"].append({
            "m": int(m), "R": R, "R_se": Rse, "R_lo": R - z * Rse,
            "R_hi": R + z * Rse, "S": S, "S_se": Sse,
            "m4": float(m4[:, j].mean()),
            "m4_se": float(m4[:, j].std(ddof=1) / np.sqrt(n_batches)),
        })
    return out
