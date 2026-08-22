"""Stage C.1 — the baseline-normalised detection response.

    R_Delta(rho) = E[tau_Delta | rho] / E[tau_0 | rho]

Estimator, fixed in STAGE_C1_PROTOCOL.md section 4: **ratio of means**, not mean
of ratios.  Per replicate `r`, `num_r` averages the stopping times of that
replicate's post-change cycles in the `Delta` arm and `den_r` averages the
identically-indexed cycles of the `Delta = 0` arm run with the SAME seed.  The
estimate is `mean_r(num_r) / mean_r(den_r)` and its uncertainty comes from
resampling **replicates**, never cycles.

Why ratio-of-means rather than mean-of-ratios: the protocol defines `R` as a
ratio of two expectations, and with a heavy-tailed `tau` a per-replicate ratio
is badly behaved when the denominator replicate mean is small.  The
mean-of-ratios variant is computed too, but only as a preregistered adversarial
estimator-variant check.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

BOOT_STREAM = 7717          # Stage C.1 bootstrap stream id (unused elsewhere)


def _rng(seed: int, index: int) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(
        np.random.SeedSequence([int(seed), BOOT_STREAM, int(index)])))


@dataclass(frozen=True, slots=True)
class Estimate:
    name: str
    point: float
    ci_low: float
    ci_high: float
    se: float
    n_replicates: int
    n_bootstrap: int
    method: str

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "point": self.point, "ci_low": self.ci_low,
                "ci_high": self.ci_high, "se": self.se,
                "n_replicates": self.n_replicates,
                "n_bootstrap": self.n_bootstrap, "method": self.method,
                "statistical_unit": "replicate"}


def ratio_of_means(num: np.ndarray, den: np.ndarray) -> float:
    return float(np.mean(num) / np.mean(den))


def mean_of_ratios(num: np.ndarray, den: np.ndarray) -> float:
    return float(np.mean(np.asarray(num) / np.asarray(den)))


def bootstrap_indices(n: int, n_boot: int, seed: int, index: int) -> np.ndarray:
    """One shared index matrix, so every contrast on these replicates is paired."""
    return _rng(seed, index).integers(0, n, size=(n_boot, n))


def estimate_R(num: np.ndarray, den: np.ndarray, *, name: str, seed: int,
               index: int, n_boot: int = 10_000,
               estimator: str = "ratio_of_means") -> Estimate:
    num, den = np.asarray(num, float), np.asarray(den, float)
    if num.shape != den.shape:
        raise ValueError("numerator and denominator must be replicate-aligned")
    f = ratio_of_means if estimator == "ratio_of_means" else mean_of_ratios
    idx = bootstrap_indices(num.size, n_boot, seed, index)
    draws = np.array([f(num[row], den[row]) for row in idx])
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return Estimate(name=name, point=f(num, den), ci_low=float(lo),
                    ci_high=float(hi), se=float(draws.std(ddof=1)),
                    n_replicates=int(num.size), n_bootstrap=n_boot,
                    method=f"percentile bootstrap over replicates, {estimator}")


def estimate_difference(a_num, a_den, b_num, b_den, *, name: str, seed: int,
                        index: int, n_boot: int = 10_000,
                        estimator: str = "ratio_of_means") -> Estimate:
    """Paired CI for `R(a) - R(b)`.

    The SAME bootstrap replicate indices are applied to all four arrays, which
    is what makes the contrast paired: policies and arms share seeds, so their
    replicate-level fluctuations are correlated and an unpaired interval would
    be far too wide.
    """
    arrays = [np.asarray(x, float) for x in (a_num, a_den, b_num, b_den)]
    n = arrays[0].size
    if any(x.shape != arrays[0].shape for x in arrays):
        raise ValueError("all four arrays must be replicate-aligned")
    f = ratio_of_means if estimator == "ratio_of_means" else mean_of_ratios
    idx = bootstrap_indices(n, n_boot, seed, index)
    draws = np.array([f(arrays[0][r], arrays[1][r]) - f(arrays[2][r], arrays[3][r])
                      for r in idx])
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return Estimate(name=name, point=f(arrays[0], arrays[1]) - f(arrays[2], arrays[3]),
                    ci_low=float(lo), ci_high=float(hi),
                    se=float(draws.std(ddof=1)), n_replicates=int(n),
                    n_bootstrap=n_boot,
                    method=f"paired percentile bootstrap over replicates, {estimator}")


def estimate_Q(rbg_num: np.ndarray, fresh_num: np.ndarray, *, name: str,
               seed: int, index: int, n_boot: int = 10_000) -> Estimate:
    """Absolute-delay guard `Q = E[tau_Delta|RBG] / E[tau_Delta|fresh]`."""
    a, b = np.asarray(rbg_num, float), np.asarray(fresh_num, float)
    idx = bootstrap_indices(a.size, n_boot, seed, index)
    draws = np.array([a[r].mean() / b[r].mean() for r in idx])
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return Estimate(name=name, point=float(a.mean() / b.mean()),
                    ci_low=float(lo), ci_high=float(hi),
                    se=float(draws.std(ddof=1)), n_replicates=int(a.size),
                    n_bootstrap=n_boot,
                    method="paired percentile bootstrap over replicates")
