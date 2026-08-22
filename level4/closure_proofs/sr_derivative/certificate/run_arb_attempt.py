#!/usr/bin/env python3
"""Authoritative-threshold Arb probe for the optional SR Gamma certificate.

This recomputes geometry, a non-rigorous spectral candidate, exact dyadic
coefficients, and representative Arb residual cells.  It deliberately records
OPEN because representative cells are not a global residual/coverage proof.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import sys
import tempfile
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint
import numpy as np
import scipy
from flint import arb, ctx
from numpy.polynomial.chebyshev import chebvander2d, chebval2d
from numpy.polynomial.legendre import leggauss
from scipy.special import ndtr

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"

A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
A_DECIMAL_LABEL = "520.886133602749"
PRECISION_BITS = 192
DEGREE = 16
SCALE_BITS = 44
QUADRATURE_ORDER = 256
CELL_WIDTH = Fraction(1, 32)
Z_PARTITIONS = 256


def rational(numerator: int, denominator: int = 1) -> arb:
    return arb(numerator) / arb(denominator)


def gaussian_phi(value: arb) -> arb:
    return (-(value * value) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()


def gaussian_cdf(value: arb) -> arb:
    return (arb(1) + (value / arb(2).sqrt()).erf()) / arb(2)


def ball_record(value: arb, digits: int = 60) -> dict[str, str]:
    return {
        "ball": value.str(digits, radius=True),
        "lower_enclosure": value.lower().str(digits, radius=True),
        "upper_enclosure": value.upper().str(digits, radius=True),
    }


def ball_width(value: arb) -> float:
    return 2.0 * float(value.rad().upper())


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def spectral_candidate(threshold: float) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    """Fresh midpoint collocation used only to construct a candidate."""
    log_a = math.log(threshold)
    live_max = math.log1p(threshold)
    degree = DEGREE
    lobatto = np.cos(np.pi * np.arange(degree + 1) / degree)[::-1]

    def operator_basis(x_flat: np.ndarray, y_flat: np.ndarray, order: int):
        y_plus = 0.5 * live_max * (x_flat + 1.0)
        y_minus = 0.5 * live_max * (y_flat + 1.0)
        ell = y_minus - log_a - 0.5
        upper = log_a - y_plus + 0.5
        nodes, weights = leggauss(order)
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
            qx = 2.0 * q_plus / live_max - 1.0
            qy = 2.0 * q_minus / live_max - 1.0
            basis = chebvander2d(qx, qy, [degree, degree]).reshape(
                order, basis_count
            )
            k_basis[row] = integration_weights @ basis
            kz_basis[row] = (integration_weights * z) @ basis
        phi_ell = np.exp(-0.5 * ell * ell) / np.sqrt(2.0 * np.pi)
        phi_upper = np.exp(-0.5 * upper * upper) / np.sqrt(2.0 * np.pi)
        r_a = phi_upper - phi_ell
        r_b = ndtr(ell) - ell * phi_ell + ndtr(-upper) + upper * phi_upper
        return k_basis, kz_basis, r_a, r_b

    x, y = np.meshgrid(lobatto, lobatto, indexing="ij")
    x_flat, y_flat = x.ravel(), y.ravel()
    values = chebvander2d(x_flat, y_flat, [degree, degree]).reshape(x_flat.size, -1)
    k_basis, kz_basis, r_a, r_b = operator_basis(
        x_flat, y_flat, QUADRATURE_ORDER
    )
    system = values - k_basis
    coefficient_a = np.linalg.solve(system, r_a).reshape(degree + 1, degree + 1)
    coefficient_a = 0.5 * (coefficient_a - coefficient_a.T)
    coefficient_b = np.linalg.solve(
        system, kz_basis @ coefficient_a.ravel() + r_b
    ).reshape(degree + 1, degree + 1)
    coefficient_b = 0.5 * (coefficient_b + coefficient_b.T)

    validation = np.linspace(-1.0, 1.0, 31)
    vx, vy = np.meshgrid(validation, validation, indexing="ij")
    vx_flat, vy_flat = vx.ravel(), vy.ravel()
    validation_values = chebvander2d(
        vx_flat, vy_flat, [degree, degree]
    ).reshape(vx_flat.size, -1)
    validation_k, validation_kz, validation_ra, validation_rb = operator_basis(
        vx_flat, vy_flat, QUADRATURE_ORDER + 32
    )
    residual_a = (
        (validation_values - validation_k) @ coefficient_a.ravel() - validation_ra
    )
    residual_b = (
        (validation_values - validation_k) @ coefficient_b.ravel()
        - validation_kz @ coefficient_a.ravel()
        - validation_rb
    )
    gamma = float(chebval2d(-1.0, -1.0, coefficient_b))
    diagnostics = {
        "gamma_float": gamma,
        "validation_residual_a_float": float(np.max(np.abs(residual_a))),
        "validation_residual_b_float": float(np.max(np.abs(residual_b))),
        "condition_number_float": float(np.linalg.cond(system)),
    }
    return coefficient_a, coefficient_b, diagnostics


def dyadic_coefficients(values: np.ndarray) -> list[list[int]]:
    scale = 1 << SCALE_BITS
    return [[int(round(float(value) * scale)) for value in row] for row in values]


def candidate_digest(a: list[list[int]], b: list[list[int]]) -> str:
    payload = json.dumps(
        {
            "degree": DEGREE,
            "scale_bits": SCALE_BITS,
            "a": a,
            "b": b,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def chebyshev_values(value: arb, degree: int) -> list[arb]:
    values = [arb(1)]
    if degree == 0:
        return values
    values.append(value)
    for _ in range(2, degree + 1):
        values.append(arb(2) * value * values[-1] - values[-2])
    return values


def evaluate_candidate(
    coefficients: list[list[int]], live_max: arb, y_plus: arb, y_minus: arb
) -> arb:
    x = arb(2) * y_plus / live_max - arb(1)
    y = arb(2) * y_minus / live_max - arb(1)
    x_values = chebyshev_values(x, DEGREE)
    y_values = chebyshev_values(y, DEGREE)
    denominator = arb(1 << SCALE_BITS)
    result = arb(0)
    for i, row in enumerate(coefficients):
        for j, coefficient in enumerate(row):
            if coefficient:
                result += arb(coefficient) * x_values[i] * y_values[j] / denominator
    return result


def softplus(value: arb) -> arb:
    return (arb(1) + value.exp()).log()


def transition(y_plus: arb, y_minus: arb, z: arb) -> tuple[arb, arb]:
    return softplus(y_plus + z - rational(1, 2)), softplus(
        y_minus - z - rational(1, 2)
    )


def cell_from_center(center: Fraction, width: Fraction) -> arb:
    midpoint = rational(center.numerator, center.denominator)
    radius = rational(width.numerator, width.denominator) / arb(2)
    return (midpoint - radius).union(midpoint + radius)


def cell_from_endpoints(lower: Fraction, upper: Fraction) -> arb:
    return rational(lower.numerator, lower.denominator).union(
        rational(upper.numerator, upper.denominator)
    )


def optional(value: arb) -> arb:
    return value.union(arb(0))


def residual_cell(
    coefficients_a: list[list[int]],
    coefficients_b: list[list[int]],
    threshold: arb,
    live_max: arb,
    y_plus: arb,
    y_minus: arb,
) -> dict[str, Any]:
    log_a = threshold.log()
    ell = y_minus - log_a - rational(1, 2)
    upper = log_a - y_plus + rational(1, 2)
    outer_lower = ell.lower()
    outer_upper = upper.upper()
    core_lower = ell.upper()
    core_upper = upper.lower()
    step = (outer_upper - outer_lower) / arb(Z_PARTITIONS)
    k_a = arb(0)
    kz_a = arb(0)
    k_b = arb(0)
    optional_bins = 0
    for index in range(Z_PARTITIONS):
        z_lower = outer_lower + arb(index) * step
        z_upper = outer_lower + arb(index + 1) * step
        z_cell = z_lower.union(z_upper)
        q_plus, q_minus = transition(y_plus, y_minus, z_cell)
        a_q = evaluate_candidate(coefficients_a, live_max, q_plus, q_minus)
        b_q = evaluate_candidate(coefficients_b, live_max, q_plus, q_minus)
        mass = gaussian_cdf(z_upper) - gaussian_cdf(z_lower)
        if not (z_lower >= core_lower and z_upper <= core_upper):
            a_q = optional(a_q)
            b_q = optional(b_q)
            za_q = optional(
                z_cell
                * evaluate_candidate(coefficients_a, live_max, q_plus, q_minus)
            )
            optional_bins += 1
        else:
            za_q = z_cell * a_q
        k_a += a_q * mass
        kz_a += za_q * mass
        k_b += b_q * mass
    phi_ell = gaussian_phi(ell)
    phi_upper = gaussian_phi(upper)
    r_a = phi_upper - phi_ell
    r_b = (
        gaussian_cdf(ell)
        - ell * phi_ell
        + (arb(1) - gaussian_cdf(upper))
        + upper * phi_upper
    )
    a_y = evaluate_candidate(coefficients_a, live_max, y_plus, y_minus)
    b_y = evaluate_candidate(coefficients_b, live_max, y_plus, y_minus)
    residual_a = a_y - k_a - r_a
    residual_b = b_y - k_b - kz_a - r_b
    return {
        "y_plus": ball_record(y_plus),
        "y_minus": ball_record(y_minus),
        "residual_a": {**ball_record(residual_a), "width_upper": ball_width(residual_a)},
        "residual_b": {**ball_record(residual_b), "width_upper": ball_width(residual_b)},
        "optional_boundary_bins": optional_bins,
    }


def main() -> int:
    started = time.time()
    threshold_float = A_NUMERATOR / A_DENOMINATOR
    coefficient_a, coefficient_b, diagnostics = spectral_candidate(threshold_float)
    dyadic_a = dyadic_coefficients(coefficient_a)
    dyadic_b = dyadic_coefficients(coefficient_b)
    digest = candidate_digest(dyadic_a, dyadic_b)
    candidate = {
        "schema": "rebaseguard.sr-derivative.arb-candidate.v1",
        "proof_role": "NON-RIGOROUS CANDIDATE; EXACT DYADIC SERIALIZATION",
        "threshold": {
            "decimal_label": A_DECIMAL_LABEL,
            "runtime_rational": [A_NUMERATOR, A_DENOMINATOR],
            "binary64_hex": threshold_float.hex(),
        },
        "degree": DEGREE,
        "scale_bits": SCALE_BITS,
        "a": dyadic_a,
        "b": dyadic_b,
        "sha256": digest,
        "diagnostics": diagnostics,
    }
    atomic_json(RESULTS / "arb_candidate.json", candidate)

    with ctx.workprec(PRECISION_BITS):
        one = arb(1)
        threshold = rational(A_NUMERATOR, A_DENOMINATOR)
        log_a = threshold.log()
        live_max = (one + threshold).log()
        denominator = one - (threshold + one) / (arb.const_e() * threshold)
        exp_sum_cap = (threshold + one) / denominator
        sum_cap = exp_sum_cap.log()
        product_min = (-one).exp()
        product_max = exp_sum_cap / arb.const_e()
        coordinate_min = (one + product_min / threshold).log()
        continuation_width = arb(2) * log_a + one - sum_cap
        fixed_point_image = (
            (one + threshold) * (one + (sum_cap - one).exp() / threshold)
        ).log()
        forcing_bound = log_a + rational(1, 2)
        forcing_probability = arb(2) * (one - gaussian_cdf(forcing_bound))
        crude_resolvent = one / forcing_probability
        gamma_candidate = evaluate_candidate(dyadic_b, live_max, arb(0), arb(0))

        checks = {
            "threshold_exact_runtime_rational": threshold.contains(threshold_float),
            "invariant_denominator_positive": denominator > 0,
            "sum_cap_fixed_point": (fixed_point_image - sum_cap).contains(0),
            "sum_cap_less_than_naive_square": sum_cap < arb(2) * live_max,
            "coordinate_floor_positive": coordinate_min > 0,
            "minimum_continuation_width_positive": continuation_width > 0,
            "forcing_probability_positive": forcing_probability > 0,
            "candidate_reset_value_above_two": gamma_candidate > arb(2),
        }
        if not all(checks.values()):
            raise ArithmeticError("authoritative-threshold Arb probe failed")

        representatives = {
            "reset_patch": (
                cell_from_endpoints(Fraction(0), CELL_WIDTH),
                cell_from_endpoints(Fraction(0), CELL_WIDTH),
            ),
            "plus_boundary_patch": (
                cell_from_center(Fraction(123, 20), CELL_WIDTH),
                cell_from_center(Fraction(2, 25), CELL_WIDTH),
            ),
            "symmetry_diagonal_patch": (
                cell_from_center(Fraction(14, 5), CELL_WIDTH),
                cell_from_center(Fraction(14, 5), CELL_WIDTH),
            ),
        }
        residuals = {
            name: residual_cell(
                dyadic_a, dyadic_b, threshold, live_max, y_plus, y_minus
            )
            for name, (y_plus, y_minus) in representatives.items()
        }
        attempt = {
            "schema": "rebaseguard.sr-derivative.arb-attempt.v1",
            "status": "OPEN",
            "claim": "NO RIGOROUS SR GAMMA INEQUALITY CERTIFIED",
            "precision_bits": PRECISION_BITS,
            "python_flint": flint.__version__,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "threshold": candidate["threshold"],
            "candidate_sha256": digest,
            "candidate_reset_value_arb": ball_record(gamma_candidate),
            "geometry": {
                "A": ball_record(threshold),
                "log_A": ball_record(log_a),
                "live_y_max": ball_record(live_max),
                "sum_cap": ball_record(sum_cap),
                "product_min": ball_record(product_min),
                "product_max": ball_record(product_max),
                "coordinate_min": ball_record(coordinate_min),
                "minimum_continuation_width": ball_record(continuation_width),
                "forcing_bound": ball_record(forcing_bound),
                "one_step_forcing_probability": ball_record(forcing_probability),
                "crude_one_step_resolvent_upper": ball_record(crude_resolvent),
            },
            "checks": checks,
            "representative_residual_cells": residuals,
            "certificate_requirements": {
                "outward_rounded_arb": True,
                "exact_threshold_serialization": True,
                "fresh_candidate_at_authoritative_threshold": True,
                "reachable_enclosure_constants_recomputed": True,
                "representative_residual_cells_only": True,
                "exact_global_patch_cover": False,
                "certified_global_residual_suprema": False,
                "certified_sharp_resolvent": False,
                "certified_propagated_gamma_interval": False,
                "independent_full_certificate_auditor": False,
                "strict_gamma_lower_endpoint_above_two": False,
            },
            "blocking_gap": (
                "The Taylor/Bernstein global residual cover and exact-rational "
                "coverage proof, including the isolated reset point, are not "
                "implemented. Representative Arb cells cannot bound the "
                "continuum residual suprema."
            ),
            "elapsed_seconds": time.time() - started,
        }
    atomic_json(RESULTS / "arb_attempt.json", attempt)
    print("Arb attempt complete: OPEN (no global residual certificate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

