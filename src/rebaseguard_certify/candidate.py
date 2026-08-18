"""Ordinary sparse collocation solver for non-proof candidate functions."""

from __future__ import annotations

import math

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.sparse import coo_matrix, eye
from scipy.sparse.linalg import spsolve
from scipy.special import ndtr

from rebaseguard_certify.mesh import TensorCandidate


def _phi(z: np.ndarray | float) -> np.ndarray | float:
    return np.exp(-0.5 * np.asarray(z) ** 2) / math.sqrt(2.0 * math.pi)


def _add_bilinear_row(
    rows: list[int],
    columns: list[int],
    data: list[float],
    row: int,
    p: float,
    m: float,
    weight: float,
    intervals: int,
    h: float,
) -> None:
    spacing = h / intervals
    p_scaled = min(max(p, 0.0), h) / spacing
    m_scaled = min(max(m, 0.0), h) / spacing
    i = min(int(p_scaled), intervals - 1)
    j = min(int(m_scaled), intervals - 1)
    x = p_scaled - i
    y = m_scaled - j
    size = intervals + 1
    for di, dj, coefficient in (
        (0, 0, (1 - x) * (1 - y)),
        (1, 0, x * (1 - y)),
        (0, 1, (1 - x) * y),
        (1, 1, x * y),
    ):
        rows.append(row)
        columns.append((i + di) * size + (j + dj))
        data.append(weight * coefficient)


def solve_candidates(
    *, intervals: int = 32, quadrature_order: int = 48, k: float = 0.5, h: float = 5.0
) -> tuple[TensorCandidate, TensorCandidate, dict[str, object]]:
    if intervals < 2 or quadrature_order < 4:
        raise ValueError("candidate resolution is too small")
    nodes, weights = leggauss(quadrature_order)
    size = intervals + 1
    dimension = size * size
    rows: list[int] = []
    columns: list[int] = []
    matrix_data: list[float] = []
    kz_rows: list[int] = []
    kz_columns: list[int] = []
    kz_data: list[float] = []
    reward_a = np.zeros(dimension)
    reward_b = np.zeros(dimension)

    for i in range(size):
        p = h * i / intervals
        for j in range(size):
            m = h * j / intervals
            row = i * size + j
            ell = m - h - k
            upper = h + k - p
            midpoint = 0.5 * (ell + upper)
            radius = 0.5 * (upper - ell)
            z_values = midpoint + radius * nodes
            quadrature_weights = radius * weights * _phi(z_values)
            for z, weight in zip(z_values, quadrature_weights, strict=True):
                next_p = max(0.0, p + float(z) - k)
                next_m = max(0.0, m - float(z) - k)
                _add_bilinear_row(
                    rows,
                    columns,
                    matrix_data,
                    row,
                    next_p,
                    next_m,
                    float(weight),
                    intervals,
                    h,
                )
                _add_bilinear_row(
                    kz_rows,
                    kz_columns,
                    kz_data,
                    row,
                    next_p,
                    next_m,
                    float(z * weight),
                    intervals,
                    h,
                )
            phi_upper = float(_phi(upper))
            phi_ell = float(_phi(ell))
            reward_a[row] = phi_upper - phi_ell
            reward_b[row] = (
                upper * phi_upper
                + (1.0 - ndtr(upper))
                + ndtr(ell)
                - ell * phi_ell
            )

    kernel = coo_matrix((matrix_data, (rows, columns)), shape=(dimension, dimension)).tocsr()
    kernel_z = coo_matrix(
        (kz_data, (kz_rows, kz_columns)), shape=(dimension, dimension)
    ).tocsr()
    operator = eye(dimension, format="csr") - kernel
    a_values = np.asarray(spsolve(operator, reward_a)).reshape(size, size)
    b_values = np.asarray(spsolve(operator, reward_b + kernel_z @ a_values.ravel())).reshape(
        size, size
    )
    # The equations commute with reflection. Averaging removes ordinary solver noise;
    # proof code later verifies the symmetry independently before using it.
    a_values = 0.5 * (a_values - a_values.T)
    b_values = 0.5 * (b_values + b_values.T)
    metadata = {
        "proof_role": "NON-RIGOROUS CANDIDATE ONLY",
        "intervals": intervals,
        "quadrature_order": quadrature_order,
        "gamma_candidate": float(b_values[0, 0]),
    }
    return TensorCandidate(a_values, h), TensorCandidate(b_values, h), metadata
