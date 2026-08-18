"""High-accuracy Chebyshev candidate solver (non-rigorous construction only)."""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import ndtr


def _barycentric_weights(degree: int) -> np.ndarray:
    weights = (-1.0) ** np.arange(degree + 1)
    weights[[0, -1]] *= 0.5
    return weights


def _basis(value: float, nodes: np.ndarray, weights: np.ndarray) -> np.ndarray:
    differences = value - nodes
    exact = np.flatnonzero(np.abs(differences) < 2e-14)
    if exact.size:
        result = np.zeros_like(nodes)
        result[exact[0]] = 1.0
        return result
    terms = weights / differences
    return terms / np.sum(terms)


@dataclass(slots=True)
class SpectralCandidate:
    values: np.ndarray
    h: float
    degree: int = field(init=False)
    nodes: np.ndarray = field(init=False)
    weights: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        self.values = np.asarray(self.values, dtype=float)
        self.degree = self.values.shape[0] - 1
        x = np.cos(np.pi * np.arange(self.degree + 1) / self.degree)
        self.nodes = 0.5 * self.h * (1.0 - x)
        self.weights = _barycentric_weights(self.degree)

    def evaluate(self, plus: float, minus: float) -> float:
        wp = _basis(float(plus), self.nodes, self.weights)
        wm = _basis(float(minus), self.nodes, self.weights)
        return float(wp @ self.values @ wm)


def solve_spectral_candidates(
    *, degree: int = 16, quadrature_order: int = 80, k: float = 0.5, h: float = 5.0
) -> tuple[SpectralCandidate, SpectralCandidate, dict[str, object]]:
    if degree < 4:
        raise ValueError("degree too small")
    count = degree + 1
    x = np.cos(np.pi * np.arange(count) / degree)
    state_nodes = 0.5 * h * (1.0 - x)
    bary_weights = _barycentric_weights(degree)
    gauss_nodes, gauss_weights = leggauss(quadrature_order)
    dimension = count * count
    kernel = np.zeros((dimension, dimension))
    kernel_z = np.zeros((dimension, dimension))
    reward_a = np.zeros(dimension)
    reward_b = np.zeros(dimension)
    normalizer = math.sqrt(2.0 * math.pi)

    for i, p in enumerate(state_nodes):
        for j, m in enumerate(state_nodes):
            row = i * count + j
            ell = m - h - k
            upper = h + k - p
            midpoint = 0.5 * (ell + upper)
            radius = 0.5 * (upper - ell)
            for node, weight in zip(gauss_nodes, gauss_weights, strict=True):
                z = midpoint + radius * node
                density_weight = radius * weight * math.exp(-0.5 * z * z) / normalizer
                next_p = max(0.0, p + z - k)
                next_m = max(0.0, m - z - k)
                wp = _basis(next_p, state_nodes, bary_weights)
                wm = _basis(next_m, state_nodes, bary_weights)
                interpolation = np.outer(wp, wm).ravel()
                kernel[row] += density_weight * interpolation
                kernel_z[row] += z * density_weight * interpolation
            phi_upper = math.exp(-0.5 * upper * upper) / normalizer
            phi_ell = math.exp(-0.5 * ell * ell) / normalizer
            reward_a[row] = phi_upper - phi_ell
            reward_b[row] = (
                upper * phi_upper
                + 1.0
                - ndtr(upper)
                + ndtr(ell)
                - ell * phi_ell
            )
    operator = np.eye(dimension) - kernel
    a_values = np.linalg.solve(operator, reward_a).reshape(count, count)
    b_values = np.linalg.solve(
        operator, reward_b + kernel_z @ a_values.ravel()
    ).reshape(count, count)
    a_values = 0.5 * (a_values - a_values.T)
    b_values = 0.5 * (b_values + b_values.T)
    metadata = {
        "proof_role": "NON-RIGOROUS CANDIDATE ONLY",
        "degree": degree,
        "quadrature_order": quadrature_order,
        "gamma_candidate": float(b_values[0, 0]),
    }
    return SpectralCandidate(a_values, h), SpectralCandidate(b_values, h), metadata
