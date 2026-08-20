"""Non-rigorous bilinear-collocation solve of the exact SR Fredholm system."""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.sparse import coo_matrix, eye
from scipy.sparse.linalg import spsolve
from scipy.special import ndtr

from rebaseguard_phase4c.geometry import (
    COORDINATE_MIN,
    PRODUCT_MAX,
    PRODUCT_MIN,
    SUM_CAP,
)
from rebaseguard_phase4c.operator import LIVE_Y_MAX, LOG_A


@dataclass(slots=True)
class ApproximateSolution:
    nodes_per_axis: int
    quadrature_order: int
    grid: np.ndarray
    a: np.ndarray
    b: np.ndarray
    gamma: float
    discrete_residual_a: float
    discrete_residual_b: float
    symmetry_error_a: float
    symmetry_error_b: float
    operator_row_mass_error: float
    runtime_seconds: float

    def summary(self) -> dict[str, float | int | list[float] | str]:
        spacing = self.grid[1] - self.grid[0]
        grad_a = np.gradient(self.a, spacing, edge_order=2)
        grad_b = np.gradient(self.b, spacing, edge_order=2)
        curvature_a = np.gradient(grad_a[0], spacing, axis=0, edge_order=2)
        curvature_a += np.gradient(grad_a[1], spacing, axis=1, edge_order=2)
        curvature_b = np.gradient(grad_b[0], spacing, axis=0, edge_order=2)
        curvature_b += np.gradient(grad_b[1], spacing, axis=1, edge_order=2)
        y_plus, y_minus = np.meshgrid(self.grid, self.grid, indexing="ij")
        product = np.expm1(y_plus) * np.expm1(y_minus)
        reachable = (
            (y_plus >= COORDINATE_MIN)
            & (y_minus >= COORDINATE_MIN)
            & (y_plus + y_minus <= SUM_CAP)
            & (product >= PRODUCT_MIN)
            & (product <= PRODUCT_MAX)
        )
        reachable[0, 0] = True
        b_curvature_index = np.unravel_index(
            int(np.argmax(np.abs(curvature_b))), curvature_b.shape
        )
        reachable_b_curvature = np.where(reachable, np.abs(curvature_b), -1.0)
        reachable_b_curvature_index = np.unravel_index(
            int(np.argmax(reachable_b_curvature)), curvature_b.shape
        )
        return {
            "proof_role": "NON-RIGOROUS APPROXIMATE CONTINUUM SOLVE ONLY",
            "nodes_per_axis": self.nodes_per_axis,
            "states": self.nodes_per_axis**2,
            "quadrature_order": self.quadrature_order,
            "gamma": self.gamma,
            "discrete_residual_a": self.discrete_residual_a,
            "discrete_residual_b": self.discrete_residual_b,
            "symmetry_error_a": self.symmetry_error_a,
            "symmetry_error_b": self.symmetry_error_b,
            "operator_row_mass_error": self.operator_row_mass_error,
            "a_range": [float(np.min(self.a)), float(np.max(self.a))],
            "b_range": [float(np.min(self.b)), float(np.max(self.b))],
            "reachable_grid_fraction": float(np.mean(reachable)),
            "a_range_on_reachable_enclosure": [
                float(np.min(self.a[reachable])),
                float(np.max(self.a[reachable])),
            ],
            "b_range_on_reachable_enclosure": [
                float(np.min(self.b[reachable])),
                float(np.max(self.b[reachable])),
            ],
            "max_gradient_norm_a": float(np.max(np.hypot(*grad_a))),
            "max_gradient_norm_b": float(np.max(np.hypot(*grad_b))),
            "max_abs_laplacian_a": float(np.max(np.abs(curvature_a))),
            "max_abs_laplacian_b": float(np.max(np.abs(curvature_b))),
            "max_gradient_norm_a_on_reachable_enclosure": float(
                np.max(np.hypot(*grad_a)[reachable])
            ),
            "max_gradient_norm_b_on_reachable_enclosure": float(
                np.max(np.hypot(*grad_b)[reachable])
            ),
            "max_abs_laplacian_a_on_reachable_enclosure": float(
                np.max(np.abs(curvature_a[reachable]))
            ),
            "max_abs_laplacian_b_on_reachable_enclosure": float(
                np.max(np.abs(curvature_b[reachable]))
            ),
            "strongest_b_curvature_location": [
                float(self.grid[b_curvature_index[0]]),
                float(self.grid[b_curvature_index[1]]),
            ],
            "strongest_reachable_b_curvature_location": [
                float(self.grid[reachable_b_curvature_index[0]]),
                float(self.grid[reachable_b_curvature_index[1]]),
            ],
            "runtime_seconds": self.runtime_seconds,
        }


def _bilinear_entries(
    q_plus: np.ndarray, q_minus: np.ndarray, *, nodes: int
) -> tuple[np.ndarray, np.ndarray]:
    spacing = LIVE_Y_MAX / (nodes - 1)
    plus_position = np.clip(q_plus / spacing, 0.0, nodes - 1.0)
    minus_position = np.clip(q_minus / spacing, 0.0, nodes - 1.0)
    i0 = np.minimum(np.floor(plus_position).astype(np.int64), nodes - 2)
    j0 = np.minimum(np.floor(minus_position).astype(np.int64), nodes - 2)
    fp = plus_position - i0
    fm = minus_position - j0
    columns = np.stack(
        (
            i0 * nodes + j0,
            (i0 + 1) * nodes + j0,
            i0 * nodes + (j0 + 1),
            (i0 + 1) * nodes + (j0 + 1),
        ),
        axis=1,
    )
    interpolation = np.stack(
        ((1.0 - fp) * (1.0 - fm), fp * (1.0 - fm), (1.0 - fp) * fm, fp * fm),
        axis=1,
    )
    return columns, interpolation


def solve_approximate_sr(
    nodes_per_axis: int, *, quadrature_order: int = 64
) -> ApproximateSolution:
    if nodes_per_axis < 5 or quadrature_order < 8:
        raise ValueError("approximation is too small")
    started = time.perf_counter()
    nodes = nodes_per_axis
    states = nodes * nodes
    grid = np.linspace(0.0, LIVE_Y_MAX, nodes)
    y_plus, y_minus = np.meshgrid(grid, grid, indexing="ij")
    y_plus_flat = y_plus.ravel()
    y_minus_flat = y_minus.ravel()
    ell = y_minus_flat - LOG_A - 0.5
    upper = LOG_A - y_plus_flat + 0.5

    gauss_nodes, gauss_weights = leggauss(quadrature_order)
    midpoint = 0.5 * (ell + upper)
    half_width = 0.5 * (upper - ell)
    z = midpoint[:, None] + half_width[:, None] * gauss_nodes[None, :]
    integration_weight = (
        half_width[:, None]
        * gauss_weights[None, :]
        * np.exp(-0.5 * z * z)
        / np.sqrt(2.0 * np.pi)
    )
    q_plus = np.logaddexp(0.0, y_plus_flat[:, None] + z - 0.5)
    q_minus = np.logaddexp(0.0, y_minus_flat[:, None] - z - 0.5)
    columns, interpolation = _bilinear_entries(
        q_plus.ravel(), q_minus.ravel(), nodes=nodes
    )
    repeated_rows = np.repeat(np.arange(states), quadrature_order * 4)
    columns_flat = columns.ravel()
    base_weight = np.repeat(integration_weight.ravel(), 4)
    values = base_weight * interpolation.ravel()
    values_z = np.repeat((integration_weight * z).ravel(), 4) * interpolation.ravel()
    k_matrix = coo_matrix(
        (values, (repeated_rows, columns_flat)), shape=(states, states)
    ).tocsr()
    kz_matrix = coo_matrix(
        (values_z, (repeated_rows, columns_flat)), shape=(states, states)
    ).tocsr()

    phi_ell = np.exp(-0.5 * ell * ell) / np.sqrt(2.0 * np.pi)
    phi_upper = np.exp(-0.5 * upper * upper) / np.sqrt(2.0 * np.pi)
    r_a = phi_upper - phi_ell
    r_b = ndtr(ell) - ell * phi_ell + ndtr(-upper) + upper * phi_upper
    system = eye(states, format="csr") - k_matrix
    a_flat = spsolve(system, r_a)
    b_flat = spsolve(system, kz_matrix @ a_flat + r_b)
    residual_a = a_flat - (k_matrix @ a_flat + r_a)
    residual_b = b_flat - (k_matrix @ b_flat + kz_matrix @ a_flat + r_b)
    expected_mass = ndtr(upper) - ndtr(ell)
    row_mass_error = np.max(np.abs(np.asarray(k_matrix.sum(axis=1)).ravel() - expected_mass))
    a = a_flat.reshape(nodes, nodes)
    b = b_flat.reshape(nodes, nodes)
    return ApproximateSolution(
        nodes,
        quadrature_order,
        grid,
        a,
        b,
        float(b[0, 0]),
        float(np.max(np.abs(residual_a))),
        float(np.max(np.abs(residual_b))),
        float(np.max(np.abs(a + a.T))),
        float(np.max(np.abs(b - b.T))),
        float(row_mass_error),
        time.perf_counter() - started,
    )
