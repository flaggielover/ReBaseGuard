"""Batch-level covariance and multivariate correspondence calculations."""

from __future__ import annotations

from math import sqrt

import numpy as np
from scipy.stats import f as f_distribution
from scipy.stats import t as t_distribution


def batch_summary(values: np.ndarray) -> dict[str, np.ndarray]:
    x = np.asarray(values, dtype=float)
    if x.ndim != 2 or x.shape[0] < 2:
        raise ValueError("at least two batch rows required")
    return {
        "mean": x.mean(axis=0),
        "sd": x.std(axis=0, ddof=1),
        "se": x.std(axis=0, ddof=1) / np.sqrt(x.shape[0]),
    }


def paired_covariance(direct: np.ndarray, reconstructed: np.ndarray) -> dict:
    x = np.asarray(direct, dtype=float)
    y = np.asarray(reconstructed, dtype=float)
    if x.shape != y.shape or x.ndim != 2 or x.shape[0] < 3:
        raise ValueError("aligned batch matrices required")
    difference = x - y
    n = x.shape[0]
    var_x = np.var(x, axis=0, ddof=1)
    var_y = np.var(y, axis=0, ddof=1)
    covariance = np.array([
        np.cov(x[:, j], y[:, j], ddof=1)[0, 1] for j in range(x.shape[1])
    ])
    correlation = np.array([
        np.corrcoef(x[:, j], y[:, j])[0, 1] for j in range(x.shape[1])
    ])
    var_formula = var_x + var_y - 2.0 * covariance
    var_direct = np.var(difference, axis=0, ddof=1)
    paired_se = np.sqrt(np.maximum(var_direct, 0.0) / n)
    naive_se = np.sqrt((var_x + var_y) / n)
    return {
        "difference": difference,
        "mean_difference": difference.mean(axis=0),
        "paired_se": paired_se,
        "naive_independence_se": naive_se,
        "variance_x": var_x,
        "variance_y": var_y,
        "covariance": covariance,
        "correlation": correlation,
        "variance_difference_direct": var_direct,
        "variance_difference_formula": var_formula,
    }


def hotelling_crosscheck(differences: np.ndarray, alpha: float = 0.01) -> dict:
    d = np.asarray(differences, dtype=float)
    if d.ndim != 2 or d.shape[0] <= d.shape[1]:
        raise ValueError("more batches than dimensions required")
    batches, dimensions = d.shape
    mean = d.mean(axis=0)
    covariance = np.cov(d, rowvar=False, ddof=1)
    eigenvalues = np.linalg.eigvalsh(covariance)
    condition = float(np.linalg.cond(covariance))
    t2 = float(batches * mean @ np.linalg.solve(covariance, mean))
    f_stat = float((batches - dimensions) / (dimensions * (batches - 1)) * t2)
    p_value = float(f_distribution.sf(f_stat, dimensions, batches - dimensions))
    marginal_se = d.std(axis=0, ddof=1) / sqrt(batches)
    critical = float(t_distribution.ppf(1.0 - 0.05 / (2.0 * dimensions), batches - 1))
    return {
        "mean_difference": mean,
        "covariance": covariance,
        "eigenvalues": eigenvalues,
        "condition_number": condition,
        "hotelling_t2": t2,
        "f_statistic": f_stat,
        "p_value": p_value,
        "alpha": alpha,
        "marginal_se": marginal_se,
        "marginal_z": np.divide(mean, marginal_se, out=np.zeros_like(mean), where=marginal_se > 0),
        "bonferroni_95_critical": critical,
        "bonferroni_95_low": mean - critical * marginal_se,
        "bonferroni_95_high": mean + critical * marginal_se,
    }


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n < 1 or not 0 <= successes <= n:
        raise ValueError("valid binomial count required")
    p = successes / n
    denominator = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denominator
    radius = z / denominator * sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return center - radius, center + radius


def path_sd(n: int, total: np.ndarray, total_sq: np.ndarray) -> np.ndarray:
    if n < 2:
        raise ValueError("at least two paths required")
    variance = np.maximum((total_sq - np.square(total) / n) / (n - 1), 0.0)
    return np.sqrt(variance)

