"""Stage C analysis: paired comparisons, criteria evaluation, Pareto frontier.

Pairing discipline
------------------
Every rho cell uses the SAME master seed, so replicate `r` is driven by the same
underlying stream in every cell.  Comparisons between rho are therefore PAIRED
at the replicate level, and the bootstrap resamples replicates (not cycles, not
rho).  Naive independent-point standard errors are never used for a
between-rho comparison, because CRN makes those cells correlated.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from campaign import RESULTS, cell_path
from rebaseguard_level4.streams import STREAM_BOOTSTRAP, generator

Z95 = 1.959963984540054


def load_cells(kind: str, keys: Sequence[dict]) -> list[dict]:
    out = []
    for key in keys:
        path = cell_path(kind, key)
        out.append(json.loads(path.read_text()) if path.exists() else None)
    return out


def paired_bootstrap(a: np.ndarray, b: np.ndarray, *, seed: int,
                     index: int, n_boot: int = 10_000,
                     statistic: str = "difference") -> dict[str, Any]:
    """Bootstrap a paired contrast over replicates.

    `a` and `b` must be aligned replicate-wise; resampling draws the SAME
    replicate indices from both, which is what makes the contrast paired.
    """
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    if a.shape != b.shape:
        raise ValueError("paired arrays must have the same shape")
    n = a.size
    rng = generator(seed, STREAM_BOOTSTRAP, index)
    idx = rng.integers(0, n, size=(n_boot, n))
    if statistic == "difference":
        point = float(a.mean() - b.mean())
        draws = a[idx].mean(axis=1) - b[idx].mean(axis=1)
    elif statistic == "ratio":
        point = float(a.mean() / b.mean())
        draws = a[idx].mean(axis=1) / b[idx].mean(axis=1)
    else:
        raise ValueError(f"unknown statistic {statistic!r}")
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return {"statistic": statistic, "point": point,
            "ci_low": float(lo), "ci_high": float(hi),
            "se": float(draws.std(ddof=1)), "n_replicates": n,
            "n_bootstrap": n_boot, "paired": True,
            "seed_key": [seed, STREAM_BOOTSTRAP, index]}


def per_replicate(cell: dict, name: str) -> np.ndarray:
    return np.asarray(cell["per_replicate"][name], dtype=float)


def find_row(rows: Sequence[dict], rho: float, shift: float | None = None):
    for r in rows:
        if abs(r["rho"] - rho) < 1e-9 and (shift is None
                                           or abs(r["shift"] - shift) < 1e-12):
            return r
    return None


def pareto_front(points: Sequence[tuple[float, float]]) -> list[int]:
    """Indices on the lower-left Pareto front (both objectives minimised)."""
    idx = sorted(range(len(points)), key=lambda i: (points[i][0], points[i][1]))
    front, best = [], np.inf
    for i in idx:
        if points[i][1] < best - 1e-12:
            front.append(i)
            best = points[i][1]
    return sorted(front)


def classify_regime(rho: float, rho_c_point: float,
                    rho_c_cert: tuple[float, float]) -> str:
    """Label a rho by its position relative to the stability boundary.

    The certified enclosure of rho_c is wide ([0.037, 0.342]), so a band of rho
    is genuinely UNDETERMINED by the certificate even though the point estimate
    places it on one side.  That distinction is kept rather than smoothed over.
    """
    lo, hi = rho_c_cert
    if rho < lo:
        return "certified-stable"
    if rho > hi:
        return "certified-unstable"
    return ("undetermined-by-certificate/point-stable" if rho < rho_c_point
            else "undetermined-by-certificate/point-unstable")
