"""Metrics and replicate-level inference for Gate 4.1.

The statistical unit is the **replicate**, never the cycle.
-----------------------------------------------------------
Cycles inside one replicate are a serially dependent Markov chain, and the whole
point of the Level 4 hypothesis is that they are *strongly* dependent (period-2
alternation).  Treating them as independent observations would understate every
standard error by a large and unknown factor, and would do so in exactly the
direction that flatters the hypothesis.  So:

* each metric is first reduced to one number per replicate;
* the point estimate is the mean over replicates;
* uncertainty comes from resampling **replicates** with replacement
  (nonparametric percentile bootstrap), never from resampling cycles.

Replicate-to-replicate standard deviation is reported alongside every interval
so that a reader can see the raw dispersion rather than only the CI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from .multicycle import CycleTable
from .streams import STREAM_BOOTSTRAP, generator

DEFAULT_LAGS = (1, 2, 3, 4, 5, 6, 7, 8)


def _MEAN(v: np.ndarray) -> float:
    return float(np.mean(v))

DEFAULT_QUANTILES = (0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99)


# ------------------------------------------------------------ per-replicate --

def autocorrelation(series: np.ndarray, lags: Sequence[int]) -> np.ndarray:
    """Standard biased ACF estimator, computed within a single replicate.

    Uses the series' own mean and the lag-0 variance as denominator, which is
    the usual convention and keeps the estimate in [-1, 1].
    """
    x = np.asarray(series, dtype=float)
    x = x - x.mean()
    denom = float(np.dot(x, x))
    out = np.empty(len(lags))
    for i, lag in enumerate(lags):
        if lag <= 0 or lag >= x.size or denom == 0.0:
            out[i] = np.nan
        else:
            out[i] = float(np.dot(x[:-lag], x[lag:])) / denom
    return out


def replicate_statistics(
    table: CycleTable,
    *,
    lags: Sequence[int] = DEFAULT_LAGS,
    quantiles: Sequence[float] = DEFAULT_QUANTILES,
) -> dict[str, np.ndarray]:
    """Reduce the retained cycles of each replicate to one number per metric."""
    retained = table.post_burn_in()
    e = retained.by_replicate("e_next")          # (R, n_cycles)
    tau = retained.by_replicate("tau").astype(float)
    direction = retained.by_replicate("direction").astype(float)

    stats: dict[str, np.ndarray] = {
        "mean_reference_error": e.mean(axis=1),
        "var_reference_error": e.var(axis=1, ddof=1),
        "sd_reference_error": e.std(axis=1, ddof=1),
        "rmse_reference_error": np.sqrt((e ** 2).mean(axis=1)),
        "mean_abs_reference_error": np.abs(e).mean(axis=1),
        "cycle_arl": tau.mean(axis=1),
        "median_tau": np.median(tau, axis=1),
        "sd_tau": tau.std(axis=1, ddof=1),
        "alarm_up_proportion": (direction > 0).mean(axis=1),
        "alternation_rate": (direction[:, 1:] != direction[:, :-1]).mean(axis=1),
        "direction_lag1_product": (direction[:, 1:] * direction[:, :-1]).mean(axis=1),
        "fraction_abs_e_gt_1": (np.abs(e) > 1.0).mean(axis=1),
        "fraction_abs_e_gt_2": (np.abs(e) > 2.0).mean(axis=1),
        "fraction_abs_e_gt_3": (np.abs(e) > 3.0).mean(axis=1),
    }
    for i, q in enumerate(quantiles):
        stats[f"e_quantile_{q:g}"] = np.quantile(e, q, axis=1)
    acf_e = np.array([autocorrelation(row, lags) for row in e])
    acf_d = np.array([autocorrelation(row, lags) for row in direction])
    for i, lag in enumerate(lags):
        stats[f"acf_e_lag{lag}"] = acf_e[:, i]
        stats[f"acf_direction_lag{lag}"] = acf_d[:, i]
    return stats


# ------------------------------------------------------------- aggregation --

@dataclass(frozen=True, slots=True)
class Estimate:
    """A replicate-level estimate with its bootstrap uncertainty."""

    metric: str
    n_replicates: int
    point: float
    replicate_sd: float
    standard_error: float
    ci_low: float
    ci_high: float
    ci_method: str
    ci_level: float
    n_bootstrap: int
    bootstrap_seed_key: list[int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "n_replicates": self.n_replicates,
            "point": self.point,
            "replicate_sd": self.replicate_sd,
            "standard_error": self.standard_error,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "ci_method": self.ci_method,
            "ci_level": self.ci_level,
            "n_bootstrap": self.n_bootstrap,
            "bootstrap_seed_key": self.bootstrap_seed_key,
            "statistical_unit": "replicate",
        }


def bootstrap_estimate(
    values: np.ndarray,
    *,
    metric: str,
    master_seed: int,
    metric_index: int,
    n_bootstrap: int = 10_000,
    level: float = 0.95,
    statistic: Callable[[np.ndarray], float] = _MEAN,
) -> Estimate:
    """Nonparametric percentile bootstrap over replicates.

    The bootstrap generator is derived from ``(master_seed, STREAM_BOOTSTRAP,
    metric_index)`` so that every interval in a report is itself reproducible
    from the manifest.
    """
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    n = v.size
    if n == 0:
        raise ValueError(f"no finite replicate values for metric {metric!r}")
    key = [int(master_seed), STREAM_BOOTSTRAP, int(metric_index)]
    rng = generator(master_seed, STREAM_BOOTSTRAP, metric_index)
    if n == 1:
        point = statistic(v)
        return Estimate(metric, n, point, float("nan"), float("nan"),
                        float("nan"), float("nan"), "percentile-bootstrap",
                        level, 0, key)
    idx = rng.integers(0, n, size=(n_bootstrap, n))
    resampled = v[idx]
    if statistic is _MEAN:
        draws = resampled.mean(axis=1)          # vectorised fast path
    else:
        draws = np.array([statistic(row) for row in resampled])
    alpha = (1.0 - level) / 2.0
    lo, hi = np.quantile(draws, [alpha, 1.0 - alpha])
    return Estimate(
        metric=metric,
        n_replicates=n,
        point=statistic(v),
        replicate_sd=float(np.std(v, ddof=1)),
        standard_error=float(np.std(draws, ddof=1)),
        ci_low=float(lo),
        ci_high=float(hi),
        ci_method="percentile-bootstrap-over-replicates",
        ci_level=level,
        n_bootstrap=n_bootstrap,
        bootstrap_seed_key=key,
    )


def summarise(
    table: CycleTable,
    *,
    n_bootstrap: int = 10_000,
    level: float = 0.95,
    lags: Sequence[int] = DEFAULT_LAGS,
    quantiles: Sequence[float] = DEFAULT_QUANTILES,
) -> dict[str, Any]:
    """Full replicate-level summary of one multi-cycle run."""
    stats = replicate_statistics(table, lags=lags, quantiles=quantiles)
    estimates: dict[str, Any] = {}
    for i, (name, values) in enumerate(sorted(stats.items())):
        estimates[name] = bootstrap_estimate(
            values, metric=name, master_seed=table.config.master_seed,
            metric_index=i, n_bootstrap=n_bootstrap, level=level,
        ).as_dict()

    retained = table.post_burn_in()
    pooled = retained.e_next
    return {
        "config": table.config.as_dict(),
        "policy_label": table.config.policy_label,
        "statistical_unit": "replicate",
        "n_replicates": table.config.n_replicates,
        "n_cycles_per_replicate": table.config.n_cycles,
        "burn_in_cycles": table.config.burn_in,
        "n_retained_cycles_total": int(pooled.size),
        "n_detector_steps_simulated": table.n_steps_simulated,
        "n_two_arm_ties": table.n_ties,
        "min_tau_observed": int(retained.tau.min()),
        "estimates": estimates,
        "pooled_empirical_distribution": {
            "note": "post-burn-in pool over all replicates; CIs come from the "
                    "replicate bootstrap above, not from this pool",
            "n": int(pooled.size),
            "mean": float(pooled.mean()),
            "sd": float(pooled.std(ddof=1)),
            "quantiles": {f"{q:g}": float(np.quantile(pooled, q))
                          for q in quantiles},
        },
        "acf_lags": list(lags),
    }


def burn_in_diagnostic(table: CycleTable, n_blocks: int = 10) -> dict[str, Any]:
    """Block-wise means over the *whole* run, burn-in included.

    Used to justify the burn-in length from data rather than by assertion: if
    early blocks differ from late blocks the burn-in was too short.
    """
    total = table.config.burn_in + table.config.n_cycles
    e = table.e_next.reshape(table.config.n_replicates, total)
    tau = table.tau.reshape(table.config.n_replicates, total).astype(float)
    edges = np.linspace(0, total, n_blocks + 1).astype(int)
    blocks = []
    for i in range(n_blocks):
        lo, hi = edges[i], edges[i + 1]
        if hi <= lo:
            continue
        blocks.append({
            "block": i,
            "cycle_range": [int(lo), int(hi)],
            "contains_burn_in": bool(lo < table.config.burn_in),
            "mean_e": float(e[:, lo:hi].mean()),
            "mean_abs_e": float(np.abs(e[:, lo:hi]).mean()),
            "sd_e": float(e[:, lo:hi].std(ddof=1)),
            "mean_tau": float(tau[:, lo:hi].mean()),
        })
    return {"burn_in_cycles": table.config.burn_in, "blocks": blocks}
