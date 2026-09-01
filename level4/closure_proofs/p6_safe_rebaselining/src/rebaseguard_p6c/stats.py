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


# -- campaign additions -----------------------------------------------------

def bca_interval(x: np.ndarray, stat=np.mean, *, n_boot: int = 10_000,
                 alpha: float = 0.05,
                 rng: np.random.Generator | None = None) -> tuple[float, float, float]:
    """BCa bootstrap interval for ``stat`` over replicates.

    Returns ``(estimate, lo, hi)``.  Bias-corrected and accelerated, as
    STATISTICAL_DESIGN.md section 3 requires alongside the normal interval.
    """
    from scipy.stats import norm
    x = np.asarray(x, float).ravel()
    n = x.size
    rng = np.random.default_rng(0) if rng is None else rng
    est = float(stat(x))
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = np.array([stat(x[i]) for i in idx]) if stat is not np.mean \
        else x[idx].mean(axis=1)
    z0 = norm.ppf(np.clip((boot < est).mean(), 1e-9, 1 - 1e-9))
    # jackknife acceleration
    tot = x.sum()
    jack = (tot - x) / (n - 1) if stat is np.mean else \
        np.array([stat(np.delete(x, i)) for i in range(n)])
    jbar = jack.mean()
    num = ((jbar - jack) ** 3).sum()
    den = 6.0 * (((jbar - jack) ** 2).sum() ** 1.5)
    a = float(num / den) if den > 0 else 0.0
    zl, zu = norm.ppf(alpha / 2), norm.ppf(1 - alpha / 2)
    def _adj(z):
        return norm.cdf(z0 + (z0 + z) / (1 - a * (z0 + z)))
    lo = float(np.quantile(boot, np.clip(_adj(zl), 0, 1)))
    hi = float(np.quantile(boot, np.clip(_adj(zu), 0, 1)))
    return est, lo, hi


def ratio_bootstrap(num: np.ndarray, den: np.ndarray, *, n_boot: int = 10_000,
                    alpha: float = 0.05,
                    rng: np.random.Generator | None = None) -> tuple[float, float, float]:
    """Bootstrap a ratio of means directly, never a ratio of bootstrapped means."""
    num = np.asarray(num, float).ravel()
    den = np.asarray(den, float).ravel()
    rng = np.random.default_rng(0) if rng is None else rng
    n = num.size
    idx = rng.integers(0, n, size=(n_boot, n))
    b = num[idx].mean(axis=1) / den[idx].mean(axis=1)
    lo, hi = np.quantile(b, [alpha / 2, 1 - alpha / 2])
    return float(num.mean() / den.mean()), float(lo), float(hi)


def relative_effect(a: np.ndarray, b: np.ndarray, *, n_boot: int = 10_000,
                    alpha: float = 0.05,
                    rng: np.random.Generator | None = None) -> dict:
    """Paired relative effect ``mean(a)/mean(b) - 1`` with a paired bootstrap.

    ``a`` is the method, ``b`` the control; both indexed by the same replicate.
    """
    a = np.asarray(a, float).ravel()
    b = np.asarray(b, float).ravel()
    rng = np.random.default_rng(0) if rng is None else rng
    n = a.size
    idx = rng.integers(0, n, size=(n_boot, n))
    rel = a[idx].mean(axis=1) / np.maximum(b[idx].mean(axis=1), 1e-300) - 1.0
    lo, hi = np.quantile(rel, [alpha / 2, 1 - alpha / 2])
    corr = float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else float("nan")
    est = float(a.mean() / b.mean() - 1.0)
    return {"rel": est, "lo": float(lo), "hi": float(hi), "n": int(n),
            "pair_corr": corr,
            "resolved": bool(lo > 0.0 or hi < 0.0)}


def benjamini_hochberg(pvals, q: float = 0.10):
    """BH step-up; returns the boolean reject vector at FDR ``q``."""
    p = np.asarray(pvals, float)
    o = np.argsort(p)
    n = p.size
    thresh = q * (np.arange(1, n + 1) / n)
    passed = p[o] <= thresh
    k = np.flatnonzero(passed)
    out = np.zeros(n, bool)
    if k.size:
        out[o[: k[-1] + 1]] = True
    return out
