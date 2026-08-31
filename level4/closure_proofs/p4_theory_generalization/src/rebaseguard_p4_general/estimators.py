"""Batch-level estimators for the three Monte Carlo routes.

All standard errors are *batch* standard errors: each batch contributes one
mean, and the reported error is the spread of those batch means.  The stopped
gain of a heavy-tailed family has a finite variance but an infinite fourth
moment, so a per-path sample-variance error bar is not trustworthy; the batch
means are far closer to normal.  This follows the convention already used by
the closed Priority-1 and Priority-2 campaigns.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .detectors import Detector
from .families import Family
from .simulate import simulate_group


@dataclass(frozen=True, slots=True)
class Estimate:
    mean: float
    se: float
    batches: int
    paths_per_batch: int

    @property
    def paths(self) -> int:
        return self.batches * self.paths_per_batch

    def as_dict(self) -> dict[str, float | int]:
        return {
            "mean": self.mean,
            "se": self.se,
            "batches": self.batches,
            "paths_per_batch": self.paths_per_batch,
            "paths": self.paths,
        }


def summarise(batch_means: list[float]) -> Estimate:
    values = np.asarray(batch_means, dtype=float)
    n = values.size
    se = float(values.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    return Estimate(float(values.mean()), se, n, 0)


def _with_paths(estimate: Estimate, paths_per_batch: int) -> Estimate:
    return Estimate(estimate.mean, estimate.se, estimate.batches, paths_per_batch)


def route_a(
    *,
    family: Family,
    detector: Detector,
    m_grid: tuple[int, ...],
    batches: int,
    paths: int,
    seed: int,
    max_steps: int,
) -> dict[str, object]:
    """Score route: ``Gamma_m = E_0[A_m sum_{t<=tau} psi(Z_t)]`` plus the
    structural diagnostics that live on the same paths."""
    keys = ("gamma", "mean_window", "fixed_gain", "short_correction", "gaussian_gain")
    acc: dict[tuple[str, int], list[float]] = {
        (key, m): [] for key in keys for m in m_grid
    }
    tau_means: list[float] = []
    unstopped = 0
    for batch in range(batches):
        (run,) = simulate_group(
            family=family, detector=detector, e_values=(0.0,), n_paths=paths,
            seed=seed, batch=batch, m_max=max(m_grid), mode="compact",
            max_steps=max_steps,
        )
        unstopped += run.unstopped
        tau_means.append(float(run.tau.mean()))
        for m in m_grid:
            a = run.window_mean(m)
            acc[("gamma", m)].append(float((a * run.score_sum).mean()))
            acc[("mean_window", m)].append(float(a.mean()))
            acc[("fixed_gain", m)].append(
                float((run.fixed_window_mean(m) * run.score_sum).mean())
            )
            acc[("short_correction", m)].append(float(run.short_correction(m).mean()))
            acc[("gaussian_gain", m)].append(float((a * run.total).mean()))
    return {
        "arl": _with_paths(summarise(tau_means), paths).as_dict(),
        "unstopped_paths": unstopped,
        "by_m": {
            str(m): {
                key: _with_paths(summarise(acc[(key, m)]), paths).as_dict()
                for key in keys
            }
            for m in m_grid
        },
    }


def route_b(
    *,
    family: Family,
    detector: Detector,
    m_grid: tuple[int, ...],
    batches: int,
    paths: int,
    seed: int,
    fd_steps: tuple[float, ...],
    max_steps: int,
) -> dict[str, object]:
    """Direct route: a common-random-number central difference of the
    conditional-mean map.  It uses no likelihood, no score and no change of
    measure -- only the detector run at shifted parameter values.

    A central difference has error ``O(h^2)``, and at the frozen operating
    point that error is not negligible: the pilot in ``PROVENANCE.md`` shows a
    5.5% deficit at ``h = 0.05`` shrinking by almost exactly a factor of four
    at ``h = 0.025``.  Route B therefore runs the *same batches* at two steps
    ``h`` and ``h/2`` and reports the Richardson combination

    ```text
    R_b = (4 D_b(h/2) - D_b(h)) / 3
    ```

    formed **per batch**, so the batch standard error automatically accounts
    for the near-perfect correlation between the two steps.  The raw per-step
    estimates are reported alongside it and are never discarded.
    """
    if len(fd_steps) != 2 or not math.isclose(fd_steps[0], 2.0 * fd_steps[1]):
        raise ValueError("fd_steps must be (h, h/2) for Richardson extrapolation")
    per_step: dict[float, dict[tuple[str, int], list[float]]] = {
        step: {(key, m): [] for key in ("gamma", "mean_plus", "mean_minus")
               for m in m_grid}
        for step in fd_steps
    }
    richardson: dict[int, list[float]] = {m: [] for m in m_grid}
    for batch in range(batches):
        batch_gamma: dict[tuple[float, int], float] = {}
        for step in fd_steps:
            plus, minus = simulate_group(
                family=family, detector=detector,
                e_values=(step, -step), n_paths=paths, seed=seed, batch=batch,
                m_max=max(m_grid), mode="aligned", max_steps=max_steps,
            )
            for m in m_grid:
                ap, am = plus.window_mean(m), minus.window_mean(m)
                value = float(-((ap - am) / (2.0 * step)).mean())
                batch_gamma[(step, m)] = value
                per_step[step][("gamma", m)].append(value)
                per_step[step][("mean_plus", m)].append(float(ap.mean()))
                per_step[step][("mean_minus", m)].append(float(am.mean()))
        coarse, fine = fd_steps
        for m in m_grid:
            richardson[m].append(
                (4.0 * batch_gamma[(fine, m)] - batch_gamma[(coarse, m)]) / 3.0
            )
    return {
        "fd_steps": list(fd_steps),
        "primary_estimator": "richardson",
        "by_m": {
            str(m): {
                "gamma": _with_paths(summarise(richardson[m]), paths).as_dict(),
                "per_step": {
                    f"{step:g}": {
                        key: _with_paths(
                            summarise(per_step[step][(key, m)]), paths
                        ).as_dict()
                        for key in ("gamma", "mean_plus", "mean_minus")
                    }
                    for step in fd_steps
                },
            }
            for m in m_grid
        },
    }


def correspondence(gamma_a: dict, gamma_b: dict) -> dict[str, float | bool]:
    """Relative discrepancy and combined-error z between the two routes."""
    a, b = gamma_a["mean"], gamma_b["mean"]
    scale = max(abs(a), abs(b))
    combined = math.hypot(gamma_a["se"], gamma_b["se"])
    return {
        "route_a": a,
        "route_b": b,
        "absolute_difference": abs(a - b),
        "relative_discrepancy": abs(a - b) / scale if scale > 0 else math.inf,
        "combined_se": combined,
        "z": abs(a - b) / combined if combined > 0 else math.inf,
    }
