"""Reachable-geometry finite Bellman diagnostic.

This implementation is independent of ``bellman.py``. It uses a piecewise
linear representation along the exact one-dimensional transition curves in
the reachable CUSUM state complex. Gaussian moments on every interpolation
segment are integrated analytically in float64. The result is diagnostic only;
it is not part of the continuum certificate or its trusted computing base.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

import numpy as np
from scipy.sparse import csr_matrix, eye
from scipy.sparse.linalg import spsolve
from scipy.special import ndtr


SQRT_2PI = math.sqrt(2.0 * math.pi)


def _phi(x: float) -> float:
    return math.exp(-0.5 * x * x) / SQRT_2PI


@dataclass(frozen=True, slots=True)
class ReachableGrid:
    cells_per_unit: int
    nodes: tuple[tuple[int, int], ...]
    index: dict[tuple[int, int], int]

    @property
    def denominator(self) -> int:
        return self.cells_per_unit


def reachable_grid(cells_per_unit: int) -> ReachableGrid:
    """Return axes through 5 and the interior triangle ``p+m<=4``."""

    if cells_per_unit < 1:
        raise ValueError("cells_per_unit must be positive")
    scale = cells_per_unit
    nodes: list[tuple[int, int]] = [(0, 0)]
    nodes.extend((i, 0) for i in range(1, 5 * scale + 1))
    nodes.extend((0, j) for j in range(1, 5 * scale + 1))
    nodes.extend(
        (i, j)
        for i in range(1, 4 * scale)
        for j in range(1, 4 * scale - i + 1)
    )
    frozen = tuple(nodes)
    return ReachableGrid(scale, frozen, {node: n for n, node in enumerate(frozen)})


def _destination(state: tuple[Fraction, Fraction], z: Fraction) -> tuple[Fraction, Fraction]:
    p, m = state
    k = Fraction(1, 2)
    return max(Fraction(0), p + z - k), max(Fraction(0), m - z - k)


def _local_weights(
    grid: ReachableGrid, destination: tuple[Fraction, Fraction]
) -> dict[int, Fraction]:
    """Interpolate on one axis or one constant-sum reachable diagonal."""

    p, m = destination
    scale = grid.denominator
    p_scaled = p * scale
    m_scaled = m * scale
    if p == 0:
        coordinate = m_scaled
        fixed = "minus"
    elif m == 0:
        coordinate = p_scaled
        fixed = "plus"
    else:
        total_scaled = p_scaled + m_scaled
        if total_scaled.denominator != 1:
            raise ArithmeticError("transition diagonal does not align with grid")
        coordinate = p_scaled
        fixed = "diagonal"

    lower = coordinate.numerator // coordinate.denominator
    if coordinate.denominator == 1:
        upper = lower
    else:
        upper = lower + 1

    def node_at(value: int) -> tuple[int, int]:
        if fixed == "minus":
            return (0, value)
        if fixed == "plus":
            return (value, 0)
        total = int(p_scaled + m_scaled)
        return (value, total - value)

    if lower == upper:
        return {grid.index[node_at(lower)]: Fraction(1)}
    upper_weight = coordinate - lower
    return {
        grid.index[node_at(lower)]: Fraction(1) - upper_weight,
        grid.index[node_at(upper)]: upper_weight,
    }


def _segment_breaks(
    state: tuple[Fraction, Fraction], scale: int
) -> list[Fraction]:
    p, m = state
    k = Fraction(1, 2)
    h = Fraction(5)
    ell = m - h - k
    upper = h + k - p
    points = {ell, upper, k - p, m - k}
    for coordinate in range(0, 5 * scale + 1):
        value = Fraction(coordinate, scale)
        points.add(value - p + k)
        points.add(m - k - value)
    return sorted(point for point in points if ell <= point <= upper)


def _normal_moments(lower: float, upper: float) -> tuple[float, float, float]:
    mass = float(ndtr(upper) - ndtr(lower))
    first = _phi(lower) - _phi(upper)
    second = mass + lower * _phi(lower) - upper * _phi(upper)
    return mass, first, second


def _solve(cells_per_unit: int) -> tuple[dict[str, object], np.ndarray, np.ndarray]:
    grid = reachable_grid(cells_per_unit)
    scale = grid.denominator
    dimension = len(grid.nodes)
    rows: list[int] = []
    columns: list[int] = []
    kernel_data: list[float] = []
    kz_data: list[float] = []
    reward_a = np.zeros(dimension)
    reward_b = np.zeros(dimension)
    maximum_mass_error = 0.0

    for row, (p_i, m_i) in enumerate(grid.nodes):
        state = (Fraction(p_i, scale), Fraction(m_i, scale))
        p, m = (float(state[0]), float(state[1]))
        ell = m - 5.5
        upper = 5.5 - p
        row_kernel: dict[int, float] = {}
        row_kz: dict[int, float] = {}
        breaks = _segment_breaks(state, scale)
        for lower_q, upper_q in zip(breaks[:-1], breaks[1:], strict=True):
            if lower_q == upper_q:
                continue
            midpoint = (lower_q + upper_q) / 2
            midpoint_weights = _local_weights(grid, _destination(state, midpoint))
            lower_weights = _local_weights(grid, _destination(state, lower_q))
            upper_weights = _local_weights(grid, _destination(state, upper_q))
            active_columns = set(midpoint_weights)
            # At a grid breakpoint the adjacent interval may use a different
            # zero-weight endpoint node. Restrict to the midpoint support and
            # evaluate the continuous affine weights on that local segment.
            lower = float(lower_q)
            segment_upper = float(upper_q)
            width = segment_upper - lower
            mass, first, second = _normal_moments(lower, segment_upper)
            for column in active_columns:
                w_lower = float(lower_weights.get(column, Fraction(0)))
                w_upper = float(upper_weights.get(column, Fraction(0)))
                slope = (w_upper - w_lower) / width
                intercept = w_lower - slope * lower
                k_value = intercept * mass + slope * first
                kz_value = intercept * first + slope * second
                row_kernel[column] = row_kernel.get(column, 0.0) + k_value
                row_kz[column] = row_kz.get(column, 0.0) + kz_value

        for column, value in row_kernel.items():
            rows.append(row)
            columns.append(column)
            kernel_data.append(value)
            kz_data.append(row_kz[column])

        continuing_mass = sum(row_kernel.values())
        expected_mass = float(ndtr(upper) - ndtr(ell))
        maximum_mass_error = max(maximum_mass_error, abs(continuing_mass - expected_mass))
        reward_a[row] = _phi(upper) - _phi(ell)
        reward_b[row] = (
            upper * _phi(upper)
            + 1.0
            - float(ndtr(upper))
            + float(ndtr(ell))
            - ell * _phi(ell)
        )

    kernel = csr_matrix((kernel_data, (rows, columns)), shape=(dimension, dimension))
    kernel_z = csr_matrix((kz_data, (rows, columns)), shape=(dimension, dimension))
    operator = eye(dimension, format="csr") - kernel
    a_values = np.asarray(spsolve(operator, reward_a))
    b_values = np.asarray(spsolve(operator, reward_b + kernel_z @ a_values))
    arl_values = np.asarray(spsolve(operator, np.ones(dimension)))

    a_reflection_error = 0.0
    b_reflection_error = 0.0
    for node, index in grid.index.items():
        reflected = grid.index[(node[1], node[0])]
        a_reflection_error = max(
            a_reflection_error, abs(a_values[index] + a_values[reflected])
        )
        b_reflection_error = max(
            b_reflection_error, abs(b_values[index] - b_values[reflected])
        )

    result: dict[str, object] = {
        "schema": "rebaseguard.refined-bellman-diagnostic.v1",
        "proof_role": "NON-RIGOROUS REFINED FINITE DIAGNOSTIC ONLY",
        "continuum_certificate": False,
        "historical_solver_modified": False,
        "cells_per_unit": cells_per_unit,
        "axis_cells": 5 * cells_per_unit,
        "node_count": dimension,
        "interpolation": "piecewise-linear on exact reachable transition curves",
        "quadrature": "analytic Gaussian moments per interpolation segment",
        "linear_solve": "SciPy sparse float64",
        "gamma_finite": float(b_values[grid.index[(0, 0)]]),
        "arl_finite": float(arl_values[grid.index[(0, 0)]]),
        "maximum_mass_error": maximum_mass_error,
        "a_reflection_error": a_reflection_error,
        "b_reflection_error": b_reflection_error,
    }
    return result, a_values, b_values


def refined_bellman_diagnostic(cells_per_unit: int) -> dict[str, object]:
    return _solve(cells_per_unit)[0]
