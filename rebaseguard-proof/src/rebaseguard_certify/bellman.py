"""Independent finite cellwise Arb Bellman cross-check.

This pathway intentionally does not import candidate or residual modules. Its
finite-state result is a cross-check only; no continuum claim is attached.
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


def _destination_index(value: Fraction, cells: int, h: Fraction) -> int:
    clipped = min(max(value, Fraction(0)), h)
    index = (clipped * cells / h).numerator // (clipped * cells / h).denominator
    return min(index, cells)


def finite_interval_bellman_crosscheck(
    *, cells: int = 8, z_bins: int = 48, bits: int = 160
) -> dict[str, object]:
    if cells < 2 or z_bins < 4:
        raise ValueError("cross-check resolution is too small")
    h_q = Fraction(5)
    k_q = Fraction(1, 2)
    size = cells + 1
    dimension = size * size
    with workprec(bits):
        kernel = arb_mat(dimension, dimension)
        kernel_z = arb_mat(dimension, dimension)
        reward_a = arb_mat(dimension, 1)
        reward_b = arb_mat(dimension, 1)
        mass_checks = 0
        for i in range(size):
            p_q = h_q * i / cells
            for j in range(size):
                m_q = h_q * j / cells
                row = i * size + j
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
                    destination = _destination_index(next_p_q, cells, h_q) * size + _destination_index(
                        next_m_q, cells, h_q
                    )
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
                mass_checks += 1
        operator = arb_mat(dimension, dimension)
        for i in range(dimension):
            for j in range(dimension):
                operator[i, j] = (arb(1) if i == j else arb(0)) - kernel[i, j]
        a_values = operator.solve(reward_a)
        b_values = operator.solve(reward_b + kernel_z * a_values)
        gamma = b_values[0, 0]
        return {
            "schema": "rebaseguard.finite-bellman-crosscheck.v1",
            "proof_role": "INDEPENDENT FINITE INTERVAL CROSS-CHECK ONLY",
            "continuum_certificate": False,
            "cells": cells,
            "z_bins": z_bins,
            "precision_bits": bits,
            "mass_balance_rows": mass_checks,
            "gamma_finite": ball_record(gamma),
        }
