"""Non-rigorous Chebyshev collocation for high-quality SR candidates."""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
from numpy.polynomial.chebyshev import chebvander2d, chebval2d
from numpy.polynomial.legendre import leggauss
from scipy.special import ndtr

from rebaseguard_phase4c.operator import LIVE_Y_MAX, LOG_A


@dataclass(slots=True)
class SpectralSolution:
    degree: int
    quadrature_order: int
    a_coefficients: np.ndarray
    b_coefficients: np.ndarray
    gamma: float
    validation_residual_a: float
    validation_residual_b: float
    validation_grid_nodes: int
    condition_number: float
    symmetry_error_a: float
    symmetry_error_b: float
    runtime_seconds: float

    def summary(self) -> dict[str, float | int | str | list[float]]:
        return {
            "proof_role": "NON-RIGOROUS SPECTRAL CANDIDATE ONLY",
            "degree_each_axis": self.degree,
            "coefficients_each_function": (self.degree + 1) ** 2,
            "quadrature_order": self.quadrature_order,
            "gamma": self.gamma,
            "independent_grid_residual_a": self.validation_residual_a,
            "independent_grid_residual_b": self.validation_residual_b,
            "independent_grid_nodes_per_axis": self.validation_grid_nodes,
            "collocation_condition_number": self.condition_number,
            "symmetry_error_a_coefficients": self.symmetry_error_a,
            "symmetry_error_b_coefficients": self.symmetry_error_b,
            "a_coefficient_abs_max": float(np.max(np.abs(self.a_coefficients))),
            "b_coefficient_abs_max": float(np.max(np.abs(self.b_coefficients))),
            "runtime_seconds": self.runtime_seconds,
        }


def _operator_basis(
    normalized_plus: np.ndarray,
    normalized_minus: np.ndarray,
    *,
    degree: int,
    quadrature_order: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    y_plus = 0.5 * LIVE_Y_MAX * (normalized_plus + 1.0)
    y_minus = 0.5 * LIVE_Y_MAX * (normalized_minus + 1.0)
    ell = y_minus - LOG_A - 0.5
    upper = LOG_A - y_plus + 0.5
    nodes, weights = leggauss(quadrature_order)
    basis_count = (degree + 1) ** 2
    k_basis = np.empty((y_plus.size, basis_count))
    kz_basis = np.empty_like(k_basis)
    for row in range(y_plus.size):
        z = 0.5 * (ell[row] + upper[row]) + 0.5 * (
            upper[row] - ell[row]
        ) * nodes
        integration_weights = (
            0.5
            * (upper[row] - ell[row])
            * weights
            * np.exp(-0.5 * z * z)
            / np.sqrt(2.0 * np.pi)
        )
        q_plus = np.logaddexp(0.0, y_plus[row] + z - 0.5)
        q_minus = np.logaddexp(0.0, y_minus[row] - z - 0.5)
        qx = 2.0 * q_plus / LIVE_Y_MAX - 1.0
        qy = 2.0 * q_minus / LIVE_Y_MAX - 1.0
        basis = chebvander2d(qx, qy, [degree, degree]).reshape(
            quadrature_order, basis_count
        )
        k_basis[row] = integration_weights @ basis
        kz_basis[row] = (integration_weights * z) @ basis
    phi_ell = np.exp(-0.5 * ell * ell) / np.sqrt(2.0 * np.pi)
    phi_upper = np.exp(-0.5 * upper * upper) / np.sqrt(2.0 * np.pi)
    r_a = phi_upper - phi_ell
    r_b = ndtr(ell) - ell * phi_ell + ndtr(-upper) + upper * phi_upper
    return k_basis, kz_basis, r_a, r_b


def solve_spectral_sr(
    degree: int,
    *,
    quadrature_order: int = 256,
    validation_grid_nodes: int = 31,
) -> SpectralSolution:
    if degree < 4 or validation_grid_nodes < 5:
        raise ValueError("spectral approximation is too small")
    started = time.perf_counter()
    lobatto = np.cos(np.pi * np.arange(degree + 1) / degree)[::-1]
    x, y = np.meshgrid(lobatto, lobatto, indexing="ij")
    x_flat, y_flat = x.ravel(), y.ravel()
    value_basis = chebvander2d(x_flat, y_flat, [degree, degree]).reshape(
        x_flat.size, -1
    )
    k_basis, kz_basis, r_a, r_b = _operator_basis(
        x_flat,
        y_flat,
        degree=degree,
        quadrature_order=quadrature_order,
    )
    system = value_basis - k_basis
    coefficients_a = np.linalg.solve(system, r_a).reshape(degree + 1, degree + 1)
    coefficients_a = 0.5 * (coefficients_a - coefficients_a.T)
    coefficients_b = np.linalg.solve(
        system, kz_basis @ coefficients_a.ravel() + r_b
    ).reshape(degree + 1, degree + 1)
    coefficients_b = 0.5 * (coefficients_b + coefficients_b.T)

    validation = np.linspace(-1.0, 1.0, validation_grid_nodes)
    vx, vy = np.meshgrid(validation, validation, indexing="ij")
    vx_flat, vy_flat = vx.ravel(), vy.ravel()
    validation_basis = chebvander2d(
        vx_flat, vy_flat, [degree, degree]
    ).reshape(vx_flat.size, -1)
    validation_k, validation_kz, validation_ra, validation_rb = _operator_basis(
        vx_flat,
        vy_flat,
        degree=degree,
        quadrature_order=quadrature_order + 32,
    )
    a_flat = coefficients_a.ravel()
    b_flat = coefficients_b.ravel()
    residual_a = (validation_basis - validation_k) @ a_flat - validation_ra
    residual_b = (
        (validation_basis - validation_k) @ b_flat
        - validation_kz @ a_flat
        - validation_rb
    )
    gamma = float(chebval2d(-1.0, -1.0, coefficients_b))
    return SpectralSolution(
        degree,
        quadrature_order,
        coefficients_a,
        coefficients_b,
        gamma,
        float(np.max(np.abs(residual_a))),
        float(np.max(np.abs(residual_b))),
        validation_grid_nodes,
        float(np.linalg.cond(system)),
        float(np.max(np.abs(coefficients_a + coefficients_a.T))),
        float(np.max(np.abs(coefficients_b - coefficients_b.T))),
        time.perf_counter() - started,
    )
