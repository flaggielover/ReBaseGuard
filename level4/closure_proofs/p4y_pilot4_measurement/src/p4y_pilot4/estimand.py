"""The measurement object, defined precisely -- brief section 9.

THE RANDOM OBJECT.  For a frozen (configuration, route, window ``m``) and a
logical block size ``b`` paths, let ``X^(b)`` be the per-block value the frozen
Priority-4 estimator returns for one block of ``b`` independent paths.  It is a
plain average of ``b`` i.i.d. per-path contributions (see ``blocks4``), so
``X^(b)`` is a well-defined random variable with the same mean for every ``b``.

THE ESTIMAND.

    theta(b) = sd( X^(b) ) / | E X^(b) |

the coefficient of variation of the block-mean law at block size ``b``.

WHY IT IS THE RIGHT OBJECT.  Future P4Y precision governance compares

    relSE(B) = sd_hat / ( sqrt(B) * |mean_hat| )     against  r*

and ``relSE(B) = theta(b) / sqrt(B)`` exactly.  So estimating ``relSE`` to
within a multiplicative factor is the SAME problem as estimating ``theta`` to
within that factor, and ``theta`` is free of ``B``, which makes the accuracy
question about the block law rather than about an allocation.

FINITE VARIANCE IS NOT ASSUMED.  ``theta`` exists only if ``X^(b)`` has finite
variance.  Pilot-3's evidence is that this is exactly what is in doubt for
``t1p5`` at ``m = 1``.  Pilot-4 therefore treats finiteness as an EMPIRICAL
question: the benchmark is admissible only if its disjoint-split,
growing-prefix and extreme-concentration criteria pass at that block size.  A
Hill index above 2 is never taken as a substitute (brief section 19).

SHARD INVARIANCE.  ``X^(b)`` is a function of a set of logical block ids and
their Philox streams, never of worker assignment or scheduling order, so
``theta`` is invariant to sharding.  The inherited regression tests pin this.

ESTIMATOR.  From ``B_ref`` logical blocks ``x_1..x_B`` at block size ``b``:

    theta_hat = s / |xbar|,   s the ddof=1 sample standard deviation

which is precisely the statistic future governance would compute.  No robust
or trimmed variant is substituted: replacing it would change the meaning of
the inherited standard error, which is out of scope.
"""

from __future__ import annotations

import math

import numpy as np


def theta_hat(values: np.ndarray) -> float:
    """The estimator: sample CV of the block-mean law.  ddof = 1."""
    v = np.asarray(values, dtype=float)
    if v.size < 2:
        return math.nan
    mean = float(v.mean())
    if mean == 0.0 or not np.isfinite(mean):
        return math.nan
    return float(v.std(ddof=1) / abs(mean))


def rel_se(theta: float, blocks: int) -> float:
    """``relSE(B) = theta / sqrt(B)`` -- the identity that makes theta the
    governance-relevant object."""
    return theta / math.sqrt(blocks)


def concentration(values: np.ndarray) -> dict:
    """Share of the total squared deviation carried by the largest blocks.

    The direct measure of whether a block law has actually aggregated, or is
    still a handful of rare extremes wearing a standard deviation.
    """
    v = np.asarray(values, dtype=float)
    d = (v - v.mean()) ** 2
    total = float(d.sum())
    if total <= 0:
        return {"top1": math.nan, "top5": math.nan, "top1pct": math.nan,
                "n": int(v.size)}
    s = np.sort(d)
    k1pct = max(1, int(round(0.01 * v.size)))
    return {"top1": float(s[-1] / total),
            "top5": float(s[-5:].sum() / total) if v.size >= 5 else math.nan,
            "top1pct": float(s[-k1pct:].sum() / total),
            "n": int(v.size)}


def prefix_curve(values: np.ndarray, fractions=(0.125, 0.25, 0.5, 1.0)) -> dict:
    """``theta`` over growing prefixes of a pool."""
    v = np.asarray(values, dtype=float)
    out = {}
    for f in fractions:
        n = max(2, int(round(f * v.size)))
        out[f"{f:g}"] = {"n": n, "theta": theta_hat(v[:n])}
    return out


def split_estimates(values: np.ndarray, parts: int) -> list[float]:
    """``theta`` on each of ``parts`` disjoint, equal, contiguous chunks."""
    v = np.asarray(values, dtype=float)
    k = v.size // parts
    return [theta_hat(v[i * k:(i + 1) * k]) for i in range(parts)] if k >= 2 else []


def ratio_spread(estimates: list[float]) -> float:
    good = [e for e in estimates if math.isfinite(e) and e > 0]
    return max(good) / min(good) if len(good) >= 2 else math.inf
