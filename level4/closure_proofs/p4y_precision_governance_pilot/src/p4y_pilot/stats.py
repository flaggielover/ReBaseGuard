"""Attainment statistics: one-sided bounds fixed BEFORE validation is seen.

The pilot's target quantity is

    p_attain = P( achieved relative SE <= r* )

under fresh, independent repetitions of the whole allocation procedure.  It is
estimated only from the ``validation`` seed namespace; the ``design``
namespace tunes the candidate rules and is never counted.
"""

from __future__ import annotations

import math

from scipy import stats


def clopper_pearson_lower(successes: int, trials: int, beta: float) -> float:
    """Exact one-sided Clopper-Pearson lower bound at confidence ``1 - beta``.

    Chosen over the naive ``(1 - delta)^R <= beta`` rule because that rule is
    only defined at zero failures, and a pilot that has to discard a candidate
    the moment it sees one failure cannot rank candidates.  At zero failures
    the two coincide exactly: ``lower = beta**(1/R)``.
    """
    if not 0 <= successes <= trials:
        raise ValueError("successes must lie in [0, trials]")
    if trials == 0:
        return 0.0
    if successes == 0:
        return 0.0
    if successes == trials:
        return float(beta ** (1.0 / trials))
    return float(stats.beta.ppf(beta, successes, trials - successes + 1))


def replicates_for_zero_failure_bound(delta: float, beta: float) -> int:
    """Clean validation replicates needed to certify ``p_attain >= delta``.

    Under the null ``p_attain = delta`` the chance of ``R`` clean replicates is
    ``delta**R``; requiring that to be at most ``beta`` gives

        R >= log(beta) / log(delta)

    which for ``delta = 0.95``, ``beta = 0.05`` is ``R = 59``.

    The brief writes the same rule as ``(1 - delta)**R <= beta``; that form
    reads ``delta`` as the tolerated FAILURE rate.  Here ``delta`` is the
    attainment probability throughout, so the base is ``delta`` and not
    ``1 - delta``.  Substituting the brief's form would ask for R = 1, which
    certifies nothing, so the substitution is made deliberately and stated
    rather than left implicit.
    """
    if not 0.0 < delta < 1.0 or not 0.0 < beta < 1.0:
        raise ValueError("delta and beta must lie strictly inside (0, 1)")
    return int(math.ceil(math.log(beta) / math.log(delta)))


def wilson_interval(successes: int, trials: int, beta: float) -> tuple[float, float]:
    """Two-sided Wilson interval, reported alongside but never used to decide."""
    if trials == 0:
        return (0.0, 1.0)
    z = stats.norm.ppf(1.0 - beta / 2.0)
    p = successes / trials
    d = 1.0 + z * z / trials
    centre = (p + z * z / (2 * trials)) / d
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def chi2_upper_quantile_ratio(blocks: int, delta: float) -> float:
    """``q_delta(B) = chi2_delta(B - 1) / (B - 1)``.

    If the ``B`` block means were exactly normal, the realised sample variance
    satisfies ``s^2 / sigma^2 ~ chi2_{B-1} / (B-1)``, so the realised relative
    SE exceeds its true value by more than ``sqrt(q_delta(B))`` with
    probability exactly ``1 - delta``.  This is the analytic inflation RULE D
    uses; the pilot MEASURES whether it survives a heavy tail rather than
    assuming it.

    ``q_delta(B) -> 1`` as ``B -> inf``, so the inflation vanishes at
    production block counts.  That is the whole point of making it
    ``B``-adaptive instead of a flat safety factor.
    """
    if blocks < 3:
        return float("inf")
    return float(stats.chi2.ppf(delta, blocks - 1) / (blocks - 1))


def hill_alpha(values: list[float], k: int | None = None) -> float:
    """Hill tail index of ``|x|``; ``alpha >= 2`` means finite variance.

    Reported as a pilot diagnostic on BLOCK MEANS.  The frozen policy fixes
    the per-path tail index; whether the 250k-path block means it mandates are
    themselves finite-variance is a separate, measurable question.
    """
    import numpy as np

    a = np.abs(np.asarray(values, dtype=float))
    a = np.sort(a[np.isfinite(a) & (a > 0)])
    n = a.size
    if n < 40:
        return float("nan")
    if k is None:
        k = max(10, int(0.1 * n))
    k = min(k, n - 1)
    top = a[-(k + 1):]
    return float(1.0 / np.mean(np.log(top[1:] / top[0])))
