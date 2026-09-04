"""One-sided UPPER confidence bounds on the reference relative standard error.

Pilot-2's failure mechanism, restated exactly: the Stage-1 rule fed the POINT
estimate ``relSE_ref_hat`` into ``N1 = N_ref * (relSE_ref/r*)**(1/kappa)``.
For a heavy-tailed family the sample standard deviation of block means is
strongly right-skewed, so its MEDIAN sits below the scale it estimates.  A
point estimate is therefore usually too small, the law raises it to a power
>= 2, and the initial allocation is usually far too small.

Replacing the point estimate by a one-sided UPPER bound at a frozen
confidence level attacks that mechanism directly: it is not "buy more", it is
"stop sizing from a statistic whose median is below the truth".

Three constructions are frozen, plus the point estimate as the baseline
control.  All operate on the same input -- the ``B`` reference BLOCK MEANS --
and all return an upper bound on

    relSE = sd(block means) / ( sqrt(B) * |mean(block means)| )
"""

from __future__ import annotations

import math

import numpy as np
from scipy import stats

#: Frozen one-sided confidence level for every UCB construction.
UCB_LEVEL = 0.95
#: Frozen bootstrap resample count.  Fixed so the method is deterministic
#: given the block means and the bootstrap stream.
BOOTSTRAP_RESAMPLES = 2000


def _relse(values: np.ndarray) -> float:
    b = values.size
    if b < 2:
        return math.inf
    mean = float(values.mean())
    if mean == 0.0:
        return math.inf
    return float(values.std(ddof=1) / math.sqrt(b) / abs(mean))


def point(values: np.ndarray, *, rng=None) -> float:
    """BASELINE CONTROL -- the Pilot-2 rule.  No bound at all."""
    return _relse(values)


def chi2_upper(values: np.ndarray, *, rng=None) -> float:
    """Normal-theory upper bound on sigma, hence on relSE.

    If the ``B`` block means were exactly normal then
    ``(B-1) s^2 / sigma^2 ~ chi2_{B-1}``, so

        sigma <= s * sqrt( (B-1) / chi2_{1-level}(B-1) )

    with probability ``level``.  Cheap, closed form, and the natural first
    candidate -- but it assumes normality of the block means, which is exactly
    what a heavy tail puts in doubt.  The pilot MEASURES whether it delivers
    its nominal coverage rather than assuming it.
    """
    b = values.size
    if b < 3:
        return math.inf
    r = _relse(values)
    if not math.isfinite(r):
        return math.inf
    inflate = math.sqrt((b - 1) / stats.chi2.ppf(1.0 - UCB_LEVEL, b - 1))
    return r * inflate


def t_squared_upper(values: np.ndarray, *, rng=None) -> float:
    """Upper bound on sigma^2 through a one-sided t-bound on its own mean.

    ``sigma^2 = E[(X - mu)^2]`` is a MEAN, so it admits a one-sided
    Student-t upper bound built from the sample variance OF THE SQUARED
    DEVIATIONS.  For block means with tail index ``alpha``, squared deviations
    have index ``alpha/2``; Pilot-2 measured the block-mean index at 5.59 on
    this cell, so the squared deviations still have finite variance and the
    bound is on firmer ground than a normality assumption.

        s2_upper = s2 + t_{level, B-1} * sd(d) / sqrt(B),   d_i = (x_i - xbar)^2
        relSE_upper = sqrt(s2_upper) / ( sqrt(B) * |xbar| )
    """
    b = values.size
    if b < 3:
        return math.inf
    mean = float(values.mean())
    if mean == 0.0:
        return math.inf
    d = (values - mean) ** 2
    s2 = float(d.sum() / (b - 1))
    sd_d = float(d.std(ddof=1))
    t = float(stats.t.ppf(UCB_LEVEL, b - 1))
    s2_upper = s2 + t * sd_d / math.sqrt(b)
    if s2_upper <= 0:
        return math.inf
    return math.sqrt(s2_upper) / (math.sqrt(b) * abs(mean))


def bootstrap_upper(values: np.ndarray, *, rng) -> float:
    """Nonparametric block bootstrap percentile upper bound on relSE.

    Resamples the ``B`` block means with replacement, recomputes relSE on each
    resample, and returns the ``level`` quantile.  Assumes nothing about the
    shape of the block-mean law, which is its appeal; but a bootstrap of a
    scale statistic from few heavy-tailed draws inherits the same downward
    pull it is meant to correct, which is why it is a candidate and not the
    presumed answer.
    """
    b = values.size
    if b < 3:
        return math.inf
    idx = rng.integers(0, b, size=(BOOTSTRAP_RESAMPLES, b))
    sample = values[idx]
    means = sample.mean(axis=1)
    sds = sample.std(axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = sds / math.sqrt(b) / np.abs(means)
    rel = rel[np.isfinite(rel)]
    if rel.size == 0:
        return math.inf
    return float(np.quantile(rel, UCB_LEVEL))


#: Frozen candidate set.  "point" is the Pilot-2 baseline control and is
#: reported, never recommended.
UCB_METHODS = {
    "point_baseline": point,
    "chi2": chi2_upper,
    "t_squared": t_squared_upper,
    "bootstrap": bootstrap_upper,
}

UCB_CANDIDATES = ("chi2", "t_squared", "bootstrap")   # selectable
UCB_BASELINE = "point_baseline"                       # control only


def evaluate(method: str, values: np.ndarray, *, rng) -> float:
    return UCB_METHODS[method](np.asarray(values, dtype=float), rng=rng)
