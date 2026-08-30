"""Independent raw-state baseline score route for reset two-chart SR."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(slots=True)
class ScoreBatch:
    gamma: np.ndarray
    tau_mean: float
    short_counts: np.ndarray
    ties: int
    simultaneous: int


def raw_step(r_plus, r_minus, z):
    return ((1.0 + r_plus) * np.exp(z - 0.5),
            (1.0 + r_minus) * np.exp(-z - 0.5))


def run_path(innovations: np.ndarray, threshold: float) -> dict:
    rp = rm = total = 0.0
    stopped: list[float] = []
    for t, z in enumerate(np.asarray(innovations, dtype=float), start=1):
        rp, rm = raw_step(rp, rm, float(z))
        total += float(z)
        stopped.append(float(z))
        if rp >= threshold or rm >= threshold:
            return {"tau": t, "increments": stopped, "T": total,
                    "plus": rp, "minus": rm}
    return {"tau": None, "increments": stopped, "T": total,
            "plus": rp, "minus": rm}


def simulate_score_batch(*, n_paths: int, threshold: float, m_grid: np.ndarray,
                         rng: np.random.Generator,
                         max_steps: int = 4_000_000) -> ScoreBatch:
    """Estimate E_0[A_m T_tau] with a raw recurrence and ring buffer."""
    m_grid = np.asarray(m_grid, dtype=np.int64)
    width = int(m_grid.max())
    rp = np.zeros(n_paths)
    rm = np.zeros(n_paths)
    total = np.zeros(n_paths)
    tau = np.zeros(n_paths, dtype=np.int64)
    active = np.ones(n_paths, dtype=bool)
    buf = np.zeros((n_paths, width))
    products = np.zeros((m_grid.size, n_paths))
    ties = simultaneous = 0
    for step in range(1, max_steps + 1):
        live = np.flatnonzero(active)
        if live.size == 0:
            break
        z = rng.standard_normal(live.size)
        newp, newm = raw_step(rp[live], rm[live], z)
        rp[live], rm[live] = newp, newm
        total[live] += z
        buf[live, (step - 1) % width] = z
        cp, cm = newp >= threshold, newm >= threshold
        crossed = cp | cm
        if not crossed.any():
            continue
        done = live[crossed]
        tau[done] = step
        both = cp[crossed] & cm[crossed]
        simultaneous += int(both.sum())
        ties += int((both & (newp[crossed] == newm[crossed])).sum())
        for j, m in enumerate(m_grid):
            w = min(int(m), step)
            suffix = np.zeros(done.size)
            for lag in range(w):
                suffix += buf[done, (step - 1 - lag) % width]
            products[j, done] = (suffix / w) * total[done]
        active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} score paths did not alarm")
    return ScoreBatch(products.mean(axis=1), float(tau.mean()),
                      np.array([(tau < m).sum() for m in m_grid]),
                      ties, simultaneous)
