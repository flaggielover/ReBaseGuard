"""Uncertainty utilities (STATISTICAL_DESIGN.md).

Paired-by-seed comparison with a bootstrap over replicate pairs, and P7's
verdict labels reused verbatim so the two campaigns' tables read together.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

INCONCLUSIVE = "INCONCLUSIVE"
STATISTICALLY_RESOLVED = "STATISTICALLY_RESOLVED"
PRACTICALLY_MATERIAL = "PRACTICALLY_MATERIAL"
INSUFFICIENT_TAIL_EVENTS = "INSUFFICIENT_TAIL_EVENTS"


@dataclass(frozen=True, slots=True)
class PairedEffect:
    estimate: float
    lo: float
    hi: float
    n_pairs: int
    correlation: float
    verdict: str


def paired_effect(a: np.ndarray, b: np.ndarray, *, materiality: float = 0.0,
                  n_boot: int = 10_000, alpha: float = 0.05,
                  rng: np.random.Generator | None = None) -> PairedEffect:
    """Bootstrap the paired difference ``mean(a - b)`` over replicate pairs.

    ``materiality`` is the preregistered absolute effect size below which an
    effect is resolved but not material.  The measured pair correlation is
    reported because common random numbers in this chain are seed alignment,
    not path coupling, and the realised variance reduction must be shown rather
    than assumed (STATISTICAL_DESIGN.md section 2).
    """
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("paired_effect needs two equal-length 1-D arrays")
    rng = np.random.default_rng(0) if rng is None else rng
    d = a - b
    n = d.size
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = d[idx].mean(axis=1)
    lo, hi = np.quantile(boot, [alpha / 2, 1 - alpha / 2])
    corr = float(np.corrcoef(a, b)[0, 1]) if n > 1 and a.std() > 0 and b.std() > 0 else float("nan")
    if lo <= 0.0 <= hi:
        verdict = INCONCLUSIVE
    elif abs(float(d.mean())) >= materiality > 0.0:
        verdict = PRACTICALLY_MATERIAL
    else:
        verdict = STATISTICALLY_RESOLVED
    return PairedEffect(float(d.mean()), float(lo), float(hi), n, corr, verdict)


def tail_event_check(n_events: float, minimum: int = 200) -> str | None:
    """Return ``INSUFFICIENT_TAIL_EVENTS`` if a tail estimate is under-powered.

    A cell with too few events is reported as under-powered, never as
    ``INCONCLUSIVE``: the two mean different things and conflating them hides a
    design failure (STATISTICAL_DESIGN.md section 5).
    """
    return INSUFFICIENT_TAIL_EVENTS if n_events < minimum else None


def batch_means(x: np.ndarray, n_batches: int = 20) -> tuple[float, float]:
    """Batch-means estimate of a mean and its standard error for a chain."""
    x = np.asarray(x, float).ravel()
    b = x.size // n_batches
    if b < 1:
        raise ValueError("series too short for the requested batch count")
    m = x[: b * n_batches].reshape(n_batches, b).mean(axis=1)
    return float(m.mean()), float(m.std(ddof=1) / np.sqrt(n_batches))
