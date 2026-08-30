"""Independent log-state perturbed-law direct conditional-map route."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(slots=True)
class DirectBatch:
    derivatives: np.ndarray
    ties: int
    simultaneous: int


def log_step(y_plus, y_minus, z):
    ell_plus = y_plus + z - 0.5
    ell_minus = y_minus - z - 0.5
    return (np.logaddexp(0.0, ell_plus), np.logaddexp(0.0, ell_minus),
            ell_plus, ell_minus)


def run_path(innovations: np.ndarray, threshold: float, e: float = 0.0) -> dict:
    yp = ym = total = 0.0
    stopped: list[float] = []
    log_a = float(np.log(threshold))
    for t, epsilon in enumerate(np.asarray(innovations, dtype=float), start=1):
        z = float(epsilon - e)
        yp, ym, ep, em = log_step(yp, ym, z)
        total += z
        stopped.append(z)
        if ep >= log_a or em >= log_a:
            return {"tau": t, "increments": stopped, "T": total,
                    "y_plus": yp, "y_minus": ym}
    return {"tau": None, "increments": stopped, "T": total,
            "y_plus": yp, "y_minus": ym}


def simulate_direct_batch(*, n_paths: int, threshold: float,
                          m_grid: np.ndarray, h_grid: np.ndarray,
                          rng: np.random.Generator,
                          max_steps: int = 4_000_000) -> DirectBatch:
    """Central differences for e+E_e[A_m], with CRN only inside this route."""
    m_grid = np.asarray(m_grid, dtype=np.int64)
    h_grid = np.asarray(h_grid, dtype=float)
    e_values = np.column_stack((h_grid, -h_grid)).reshape(-1)
    conditions = e_values.size
    width = int(m_grid.max())
    shape = (conditions, n_paths)
    yp = np.zeros(shape)
    ym = np.zeros(shape)
    active = np.ones(shape, dtype=bool)
    buf = np.zeros((conditions, n_paths, width))
    means = np.zeros((conditions, m_grid.size, n_paths))
    log_a = float(np.log(threshold))
    ties = simultaneous = 0
    for step in range(1, max_steps + 1):
        if not active.any():
            break
        epsilon = rng.standard_normal(n_paths)
        z = epsilon[None, :] - e_values[:, None]
        nyp, nym, ep, em = log_step(yp, ym, z)
        yp = np.where(active, nyp, yp)
        ym = np.where(active, nym, ym)
        slot = (step - 1) % width
        buf[:, :, slot] = np.where(active, z, buf[:, :, slot])
        cp, cm = (ep >= log_a) & active, (em >= log_a) & active
        crossed = cp | cm
        if not crossed.any():
            continue
        both = cp & cm
        simultaneous += int(both.sum())
        ties += int((both & (ep == em)).sum())
        for condition in range(conditions):
            done = np.flatnonzero(crossed[condition])
            if done.size == 0:
                continue
            for j, m in enumerate(m_grid):
                w = min(int(m), step)
                suffix = np.zeros(done.size)
                for lag in range(w):
                    suffix += buf[condition, done, (step - 1 - lag) % width]
                means[condition, j, done] = suffix / w
        active &= ~crossed
    else:
        raise RuntimeError(f"{int(active.sum())} direct conditions did not alarm")
    condition_means = means.mean(axis=2).reshape(h_grid.size, 2, m_grid.size)
    plus = h_grid[:, None] + condition_means[:, 0, :]
    minus = -h_grid[:, None] + condition_means[:, 1, :]
    derivatives = (plus - minus) / (2.0 * h_grid[:, None])
    return DirectBatch(derivatives, ties, simultaneous)
