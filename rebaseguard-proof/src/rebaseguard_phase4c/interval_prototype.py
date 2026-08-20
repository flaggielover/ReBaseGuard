"""Lightweight Arb cell prototype for the nonlinear SR operator.

This is a feasibility instrument, not a final certificate.  It validates exact
dyadic candidates against the continuum formulas on selected cells only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction

from flint import arb

from rebaseguard_certify.arb_backend import (
    ball_record,
    gaussian_cdf,
    gaussian_mass,
    gaussian_phi,
    rational,
    workprec,
)
from rebaseguard_phase4c.spectral_solver import solve_spectral_sr


@dataclass(frozen=True, slots=True)
class DyadicCandidate:
    degree: int
    scale_bits: int
    a: tuple[tuple[int, ...], ...]
    b: tuple[tuple[int, ...], ...]
    diagnostic_residual_a: float
    diagnostic_residual_b: float
    source_gamma: float

    def digest(self) -> str:
        payload = json.dumps(
            {"degree": self.degree, "scale_bits": self.scale_bits, "a": self.a, "b": self.b},
            separators=(",", ":"),
        ).encode()
        return hashlib.sha256(payload).hexdigest()


def fit_dyadic_candidate(
    *,
    quadrature_order: int = 256,
    degree: int = 16,
    scale_bits: int = 44,
) -> DyadicCandidate:
    solution = solve_spectral_sr(
        degree,
        quadrature_order=quadrature_order,
        validation_grid_nodes=31,
    )
    coefficients_a = solution.a_coefficients
    coefficients_b = solution.b_coefficients
    scale = 1 << scale_bits
    integer_a = tuple(
        tuple(int(round(value * scale)) for value in row) for row in coefficients_a
    )
    integer_b = tuple(
        tuple(int(round(value * scale)) for value in row) for row in coefficients_b
    )
    return DyadicCandidate(
        degree,
        scale_bits,
        integer_a,
        integer_b,
        solution.validation_residual_a,
        solution.validation_residual_b,
        solution.gamma,
    )


def _decimal_rational(value: float) -> arb:
    fraction = Fraction(str(value))
    return rational(fraction.numerator, fraction.denominator)


def interval_from_center(center: float, width: float) -> arb:
    midpoint = _decimal_rational(center)
    radius = _decimal_rational(width) / arb(2)
    return (midpoint - radius).union(midpoint + radius)


def interval_from_endpoints(lower: float, upper: float) -> arb:
    return _decimal_rational(lower).union(_decimal_rational(upper))


def arb_softplus(value: arb) -> arb:
    return (arb(1) + value.exp()).log()


def arb_transition(y_plus: arb, y_minus: arb, z: arb) -> tuple[arb, arb]:
    return (
        arb_softplus(y_plus + z - rational(1, 2)),
        arb_softplus(y_minus - z - rational(1, 2)),
    )


def arb_continuation_bounds(y_plus: arb, y_minus: arb) -> tuple[arb, arb]:
    log_a = rational(8325, 16).log()
    return y_minus - log_a - rational(1, 2), log_a - y_plus + rational(1, 2)


def _chebyshev_values(value: arb, degree: int) -> list[arb]:
    values = [arb(1)]
    if degree == 0:
        return values
    values.append(value)
    for _ in range(2, degree + 1):
        values.append(arb(2) * value * values[-1] - values[-2])
    return values


def evaluate_candidate(
    coefficients: tuple[tuple[int, ...], ...],
    scale_bits: int,
    y_plus: arb,
    y_minus: arb,
) -> arb:
    live_max = (arb(1) + rational(8325, 16)).log()
    x = arb(2) * y_plus / live_max - arb(1)
    y = arb(2) * y_minus / live_max - arb(1)
    x_values = _chebyshev_values(x, len(coefficients) - 1)
    y_values = _chebyshev_values(y, len(coefficients) - 1)
    result = arb(0)
    denominator = arb(1 << scale_bits)
    for i, row in enumerate(coefficients):
        for j, coefficient in enumerate(row):
            if coefficient:
                result += arb(coefficient) * x_values[i] * y_values[j] / denominator
    return result


def _optional(value: arb) -> arb:
    return value.union(arb(0))


def interval_residual_on_cell(
    candidate: DyadicCandidate,
    y_plus: arb,
    y_minus: arb,
    *,
    z_partitions: int,
) -> tuple[arb, arb, dict[str, arb]]:
    """Enclose both residuals on a state cell by positive-measure z boxes."""

    if z_partitions < 8:
        raise ValueError("z_partitions must be at least eight")
    ell, upper = arb_continuation_bounds(y_plus, y_minus)
    outer_lower = ell.lower()
    outer_upper = upper.upper()
    core_lower = ell.upper()
    core_upper = upper.lower()
    step = (outer_upper - outer_lower) / arb(z_partitions)
    k_a = arb(0)
    kz_a = arb(0)
    k_b = arb(0)
    optional_bins = 0
    for index in range(z_partitions):
        z_lower = outer_lower + arb(index) * step
        z_upper = outer_lower + arb(index + 1) * step
        z_cell = z_lower.union(z_upper)
        q_plus, q_minus = arb_transition(y_plus, y_minus, z_cell)
        a_q = evaluate_candidate(
            candidate.a, candidate.scale_bits, q_plus, q_minus
        )
        b_q = evaluate_candidate(
            candidate.b, candidate.scale_bits, q_plus, q_minus
        )
        mass = gaussian_mass(z_lower, z_upper)
        guaranteed = z_lower >= core_lower and z_upper <= core_upper
        if not guaranteed:
            a_q = _optional(a_q)
            b_q = _optional(b_q)
            za_q = _optional(z_cell * evaluate_candidate(
                candidate.a, candidate.scale_bits, q_plus, q_minus
            ))
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
    a_y = evaluate_candidate(candidate.a, candidate.scale_bits, y_plus, y_minus)
    b_y = evaluate_candidate(candidate.b, candidate.scale_bits, y_plus, y_minus)
    residual_a = a_y - k_a - r_a
    residual_b = b_y - k_b - kz_a - r_b
    return residual_a, residual_b, {
        "q_plus_example": arb_transition(y_plus, y_minus, (outer_lower + outer_upper) / arb(2))[0],
        "q_minus_example": arb_transition(y_plus, y_minus, (outer_lower + outer_upper) / arb(2))[1],
        "ell": ell,
        "upper": upper,
        "r_a": r_a,
        "r_b": r_b,
        "optional_bins": arb(optional_bins),
    }


def ball_width(value: arb) -> float:
    return 2.0 * float(value.rad().upper())


def residual_record(value: arb) -> dict[str, str | float]:
    return {**ball_record(value, digits=50), "width_upper": ball_width(value)}


def run_representative_prototype(*, bits: int = 192) -> dict[str, object]:
    candidate = fit_dyadic_candidate()
    representatives = {
        "reset_neighborhood": (0.0, 0.0, True),
        "near_plus_boundary": (6.15, 0.08, False),
        "near_minus_boundary": (0.08, 6.15, False),
        "symmetry_diagonal": (2.8, 2.8, False),
        "strong_reachable_curvature": (5.58, 0.08, False),
    }
    refinements = [
        (0.125, 64),
        (0.0625, 128),
        (0.03125, 256),
    ]
    records: list[dict[str, object]] = []
    with workprec(bits):
        for width, partitions in refinements:
            for name, (center_plus, center_minus, reset_box) in representatives.items():
                if reset_box:
                    y_plus = interval_from_endpoints(0.0, width)
                    y_minus = interval_from_endpoints(0.0, width)
                else:
                    y_plus = interval_from_center(center_plus, width)
                    y_minus = interval_from_center(center_minus, width)
                residual_a, residual_b, details = interval_residual_on_cell(
                    candidate, y_plus, y_minus, z_partitions=partitions
                )
                curvature_z = interval_from_center(0.5 - center_plus, width)
                q_curvature = arb_transition(y_plus, y_minus, curvature_z)
                records.append(
                    {
                        "cell": name,
                        "state_width": width,
                        "z_partitions": partitions,
                        "residual_a": residual_record(residual_a),
                        "residual_b": residual_record(residual_b),
                        "q_plus_curvature_width": ball_width(q_curvature[0]),
                        "q_minus_curvature_width": ball_width(q_curvature[1]),
                        "continuation_ell": ball_record(details["ell"], digits=40),
                        "continuation_upper": ball_record(details["upper"], digits=40),
                        "r_a_width": ball_width(details["r_a"]),
                        "r_b_width": ball_width(details["r_b"]),
                        "optional_boundary_bins": int(float(details["optional_bins"].mid())),
                    }
                )
    return {
        "schema": "rebaseguard.phase4c.interval-prototype.v1",
        "proof_role": "REPRESENTATIVE-CELL ARB FEASIBILITY PROTOTYPE; NOT A GLOBAL CERTIFICATE",
        "precision_bits": bits,
        "candidate": {
            "degree": candidate.degree,
            "scale_bits": candidate.scale_bits,
            "sha256": candidate.digest(),
            "independent_grid_residual_a_float": candidate.diagnostic_residual_a,
            "independent_grid_residual_b_float": candidate.diagnostic_residual_b,
            "source_gamma_float": candidate.source_gamma,
        },
        "method": (
            "exact-dyadic Chebyshev candidate; Arb softplus and Gaussian moments; "
            "positive-measure interval z partition with optional endpoint strips"
        ),
        "records": records,
    }
