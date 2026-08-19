"""Forensic ablations of the historical finite Bellman discretization.

The historical implementation is deliberately not imported or modified.
This module reconstructs selected variants so individual sources of finite
bias can be isolated. All outputs remain finite diagnostic cross-checks.
"""

from __future__ import annotations

from fractions import Fraction

from flint import arb, arb_mat

from rebaseguard_certify.arb_backend import (
    ball_record,
    gaussian_cdf,
    gaussian_first_moment,
    gaussian_mass,
    gaussian_phi,
    workprec,
)


def _floor_index(value: Fraction, cells: int, h: Fraction) -> int:
    clipped = min(max(value, Fraction(0)), h)
    scaled = clipped * cells / h
    return min(scaled.numerator // scaled.denominator, cells)


def _reachable_nodes(cells: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (i, j)
        for i in range(cells + 1)
        for j in range(cells + 1)
        if i == 0 or j == 0 or 5 * (i + j) <= 4 * cells
    )


def historical_floor_reachable_ablation(
    *, cells: int = 12, z_bins: int = 96, bits: int = 160
) -> dict[str, object]:
    """Replay the historical floor projection on the reachable node subset."""

    if cells < 2 or z_bins < 4:
        raise ValueError("ablation resolution is too small")
    h_q = Fraction(5)
    k_q = Fraction(1, 2)
    nodes = _reachable_nodes(cells)
    node_index = {node: index for index, node in enumerate(nodes)}
    dimension = len(nodes)
    with workprec(bits):
        kernel = arb_mat(dimension, dimension)
        kernel_z = arb_mat(dimension, dimension)
        reward_a = arb_mat(dimension, 1)
        reward_b = arb_mat(dimension, 1)
        for row, (i, j) in enumerate(nodes):
            p_q = h_q * i / cells
            m_q = h_q * j / cells
            ell_q = m_q - h_q - k_q
            upper_q = h_q + k_q - p_q
            width_q = (upper_q - ell_q) / z_bins
            continuing_mass = arb(0)
            for z_index in range(z_bins):
                lower_q = ell_q + width_q * z_index
                bin_upper_q = lower_q + width_q
                midpoint_q = (lower_q + bin_upper_q) / 2
                next_p_q = max(Fraction(0), p_q + midpoint_q - k_q)
                next_m_q = max(Fraction(0), m_q - midpoint_q - k_q)
                destination_node = (
                    _floor_index(next_p_q, cells, h_q),
                    _floor_index(next_m_q, cells, h_q),
                )
                if destination_node not in node_index:
                    raise ArithmeticError("floor transition escaped reachable complex")
                destination = node_index[destination_node]
                lower = arb(lower_q.numerator) / arb(lower_q.denominator)
                bin_upper = arb(bin_upper_q.numerator) / arb(bin_upper_q.denominator)
                mass = gaussian_mass(lower, bin_upper)
                first = gaussian_first_moment(lower, bin_upper)
                kernel[row, destination] += mass
                kernel_z[row, destination] += first
                continuing_mass += mass
            ell = arb(ell_q.numerator) / arb(ell_q.denominator)
            upper = arb(upper_q.numerator) / arb(upper_q.denominator)
            reward_a[row, 0] = gaussian_phi(upper) - gaussian_phi(ell)
            reward_b[row, 0] = (
                upper * gaussian_phi(upper)
                + arb(1)
                - gaussian_cdf(upper)
                + gaussian_cdf(ell)
                - ell * gaussian_phi(ell)
            )
            absorbing_mass = arb(1) - gaussian_mass(ell, upper)
            if not (continuing_mass + absorbing_mass).contains(1):
                raise ArithmeticError("finite Bellman mass balance failed")

        operator = arb_mat(dimension, dimension)
        for i in range(dimension):
            for j in range(dimension):
                operator[i, j] = (arb(1) if i == j else arb(0)) - kernel[i, j]
        a_values = operator.solve(reward_a)
        b_values = operator.solve(reward_b + kernel_z * a_values)
        ones = arb_mat(dimension, 1)
        for row in range(dimension):
            ones[row, 0] = arb(1)
        arl_values = operator.solve(ones)
        gamma = b_values[node_index[(0, 0)], 0]
        return {
            "schema": "rebaseguard.historical-floor-reachable-ablation.v1",
            "proof_role": "FORENSIC FINITE ARB ABLATION ONLY",
            "continuum_certificate": False,
            "cells": cells,
            "z_bins": z_bins,
            "precision_bits": bits,
            "full_square_nodes": (cells + 1) ** 2,
            "reachable_nodes": dimension,
            "gamma_finite": ball_record(gamma),
            "arl_finite": ball_record(arl_values[node_index[(0, 0)], 0]),
        }
