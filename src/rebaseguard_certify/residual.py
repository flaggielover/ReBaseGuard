"""Arb continuum residual certificate using symbolic Gaussian envelopes."""

from __future__ import annotations

from math import comb, factorial
from typing import Mapping

from flint import arb

from rebaseguard_certify.arb_backend import ball_record, rational, workprec
from rebaseguard_certify.polynomial import (
    BiPoly,
    TriPoly,
    bi_add,
    bi_eval,
    bi_mul,
    bi_pow,
    bi_scale,
    chebyshev_payload_to_power,
    tri_add,
    tri_mul,
    tri_pow,
)
def construct_candidate_payloads(
    *, degree: int = 12, quadrature_order: int = 400, scale_bits: int = 50
) -> dict[str, object]:
    from rebaseguard_certify.spectral_candidate import solve_spectral_candidates

    a_hat, b_hat, metadata = solve_spectral_candidates(
        degree=degree, quadrature_order=quadrature_order
    )
    return {
        "schema": "rebaseguard.candidate-pair.v1",
        "proof_role": "EXACT DYADIC CANDIDATE; VALID ONLY AFTER RESIDUAL CERTIFICATION",
        "construction_metadata": metadata,
        "a": a_hat.to_chebyshev_dyadic(scale_bits=scale_bits),
        "b": b_hat.to_chebyshev_dyadic(scale_bits=scale_bits),
    }


def _phi_coefficients(order: int) -> list[arb]:
    normalizer = (arb(2) * arb.pi()).sqrt()
    coefficients = [arb(0)] * (2 * order + 1)
    for n in range(order + 1):
        coefficients[2 * n] = ((-arb(1)) ** n) / (
            normalizer * (arb(2) ** n) * arb(factorial(n))
        )
    return coefficients


def _series_at_affine(coefficients: list[arb], affine: BiPoly) -> BiPoly:
    powers = [{(0, 0): arb(1)}]
    for _ in range(1, len(coefficients)):
        powers.append(bi_mul(powers[-1], affine))
    result: BiPoly = {}
    for degree, coefficient in enumerate(coefficients):
        if coefficient != 0:
            result = bi_add(result, bi_scale(powers[degree], coefficient))
    return result


def _cdf_at_affine(phi_coefficients: list[arb], affine: BiPoly) -> BiPoly:
    integrated = [arb(0)] * (len(phi_coefficients) + 1)
    integrated[0] = rational(1, 2)
    for degree, coefficient in enumerate(phi_coefficients):
        integrated[degree + 1] = coefficient / arb(degree + 1)
    return _series_at_affine(integrated, affine)


def _substitute_candidate(candidate: BiPoly, mode: str) -> TriPoly:
    zero: TriPoly = {(0, 0, 0): arb(0)}
    active_plus: TriPoly = {
        (1, 0, 0): arb(1),
        (0, 0, 1): arb(1),
        (0, 0, 0): -rational(1, 2),
    }
    active_minus: TriPoly = {
        (0, 1, 0): arb(1),
        (0, 0, 1): -arb(1),
        (0, 0, 0): -rational(1, 2),
    }
    q_plus = active_plus if mode in {"up", "both"} else zero
    q_minus = active_minus if mode in {"down", "both"} else zero
    max_i = max(i for i, _ in candidate)
    max_j = max(j for _, j in candidate)
    plus_powers = [tri_pow(q_plus, i) for i in range(max_i + 1)]
    minus_powers = [tri_pow(q_minus, j) for j in range(max_j + 1)]
    result: TriPoly = {}
    for (i, j), coefficient in candidate.items():
        if mode in {"down", "origin"} and i > 0:
            continue
        if mode in {"up", "origin"} and j > 0:
            continue
        term = tri_mul(plus_powers[i], minus_powers[j])
        scaled = {key: value * coefficient for key, value in term.items()}
        result = tri_add(result, scaled)
    return result


def _multiply_by_phi(poly: TriPoly, phi_coefficients: list[arb], z_weight: int) -> TriPoly:
    result: TriPoly = {}
    for (i, j, degree), coefficient in poly.items():
        for phi_degree, phi_coefficient in enumerate(phi_coefficients):
            if phi_coefficient == 0:
                continue
            key = (i, j, degree + phi_degree + z_weight)
            result[key] = result.get(key, arb(0)) + coefficient * phi_coefficient
    return result


def _integrate_z(poly: TriPoly, lower: BiPoly, upper: BiPoly) -> BiPoly:
    maximum = max(degree for _, _, degree in poly) + 1
    lower_powers = [{(0, 0): arb(1)}]
    upper_powers = [{(0, 0): arb(1)}]
    for _ in range(maximum):
        lower_powers.append(bi_mul(lower_powers[-1], lower))
        upper_powers.append(bi_mul(upper_powers[-1], upper))
    result: BiPoly = {}
    for (i, j, degree), coefficient in poly.items():
        divisor = arb(degree + 1)
        for (a, b), endpoint_coefficient in upper_powers[degree + 1].items():
            key = (i + a, j + b)
            result[key] = result.get(key, arb(0)) + coefficient * endpoint_coefficient / divisor
        for (a, b), endpoint_coefficient in lower_powers[degree + 1].items():
            key = (i + a, j + b)
            result[key] = result.get(key, arb(0)) - coefficient * endpoint_coefficient / divisor
    return result


def _kernel_piece(
    candidate: BiPoly,
    mode: str,
    lower: BiPoly,
    upper: BiPoly,
    phi_coefficients: list[arb],
    *,
    z_weight: int,
) -> BiPoly:
    substituted = _substitute_candidate(candidate, mode)
    integrand = _multiply_by_phi(substituted, phi_coefficients, z_weight)
    return _integrate_z(integrand, lower, upper)


def _kernel_polynomials(
    candidate: BiPoly, phi_coefficients: list[arb], *, z_weight: int
) -> tuple[BiPoly, BiPoly]:
    p: BiPoly = {(1, 0): arb(1)}
    m: BiPoly = {(0, 1): arb(1)}
    ell = bi_add(m, {(0, 0): -rational(11, 2)})
    beta = bi_add(m, {(0, 0): -rational(1, 2)})
    alpha = bi_add(bi_scale(p, -arb(1)), {(0, 0): rational(1, 2)})
    upper = bi_add(bi_scale(p, -arb(1)), {(0, 0): rational(11, 2)})

    low_sum = _kernel_piece(candidate, "down", ell, beta, phi_coefficients, z_weight=z_weight)
    low_sum = bi_add(
        low_sum,
        _kernel_piece(candidate, "origin", beta, alpha, phi_coefficients, z_weight=z_weight),
    )
    low_sum = bi_add(
        low_sum,
        _kernel_piece(candidate, "up", alpha, upper, phi_coefficients, z_weight=z_weight),
    )

    high_sum = _kernel_piece(candidate, "down", ell, alpha, phi_coefficients, z_weight=z_weight)
    high_sum = bi_add(
        high_sum,
        _kernel_piece(candidate, "both", alpha, beta, phi_coefficients, z_weight=z_weight),
    )
    high_sum = bi_add(
        high_sum,
        _kernel_piece(candidate, "up", beta, upper, phi_coefficients, z_weight=z_weight),
    )
    return low_sum, high_sum


def _reward_polynomials(phi_coefficients: list[arb]) -> tuple[BiPoly, BiPoly]:
    p: BiPoly = {(1, 0): arb(1)}
    m: BiPoly = {(0, 1): arb(1)}
    ell = bi_add(m, {(0, 0): -rational(11, 2)})
    upper = bi_add(bi_scale(p, -arb(1)), {(0, 0): rational(11, 2)})
    phi_upper = _series_at_affine(phi_coefficients, upper)
    phi_ell = _series_at_affine(phi_coefficients, ell)
    cdf_upper = _cdf_at_affine(phi_coefficients, upper)
    cdf_ell = _cdf_at_affine(phi_coefficients, ell)
    reward_a = bi_add(phi_upper, bi_scale(phi_ell, -arb(1)))
    reward_b = bi_add(bi_mul(upper, phi_upper), {(0, 0): arb(1)})
    reward_b = bi_add(reward_b, bi_scale(cdf_upper, -arb(1)))
    reward_b = bi_add(reward_b, cdf_ell)
    reward_b = bi_add(reward_b, bi_scale(bi_mul(ell, phi_ell), -arb(1)))
    return reward_a, reward_b


def _parameterize_triangle(poly: BiPoly) -> BiPoly:
    """Substitute p=r*t, m=r*(1-t)."""

    result: BiPoly = {}
    for (i, j), coefficient in poly.items():
        for s in range(j + 1):
            key = (i + j, i + s)
            signed = coefficient * arb(comb(j, s)) * ((-arb(1)) ** s)
            result[key] = result.get(key, arb(0)) + signed
    return result


def _affine_to_unit_square(
    poly: BiPoly, r_lower: arb, r_upper: arb, t_lower: arb, t_upper: arb
) -> BiPoly:
    r_affine: BiPoly = {(0, 0): r_lower, (1, 0): r_upper - r_lower}
    t_affine: BiPoly = {(0, 0): t_lower, (0, 1): t_upper - t_lower}
    max_i = max(i for i, _ in poly)
    max_j = max(j for _, j in poly)
    r_powers = [bi_pow(r_affine, i) for i in range(max_i + 1)]
    t_powers = [bi_pow(t_affine, j) for j in range(max_j + 1)]
    result: BiPoly = {}
    for (i, j), coefficient in poly.items():
        result = bi_add(result, bi_scale(bi_mul(r_powers[i], t_powers[j]), coefficient))
    return result


def _power_to_bernstein(poly: BiPoly) -> list[list[arb]]:
    degree_r = max(i for i, _ in poly)
    degree_t = max(j for _, j in poly)
    temporary = [[arb(0) for _ in range(degree_t + 1)] for _ in range(degree_r + 1)]
    for k in range(degree_r + 1):
        for j in range(degree_t + 1):
            value = arb(0)
            for i in range(k + 1):
                coefficient = poly.get((i, j), arb(0))
                value += coefficient * arb(comb(k, i)) / arb(comb(degree_r, i))
            temporary[k][j] = value
    result = [[arb(0) for _ in range(degree_t + 1)] for _ in range(degree_r + 1)]
    for k in range(degree_r + 1):
        for ell in range(degree_t + 1):
            value = arb(0)
            for j in range(ell + 1):
                value += temporary[k][j] * arb(comb(ell, j)) / arb(comb(degree_t, j))
            result[k][ell] = value
    return result


def _split_curve(coefficients: list[arb]) -> tuple[list[arb], list[arb]]:
    degree = len(coefficients) - 1
    levels = [list(coefficients)]
    for _ in range(degree):
        previous = levels[-1]
        levels.append([(previous[i] + previous[i + 1]) / arb(2) for i in range(len(previous) - 1)])
    left = [levels[level][0] for level in range(degree + 1)]
    right = [levels[degree - level][level] for level in range(degree + 1)]
    return left, right


def _split_patch(
    coefficients: list[list[arb]], axis: int
) -> tuple[list[list[arb]], list[list[arb]]]:
    rows = len(coefficients)
    columns = len(coefficients[0])
    if axis == 0:
        left = [[arb(0) for _ in range(columns)] for _ in range(rows)]
        right = [[arb(0) for _ in range(columns)] for _ in range(rows)]
        for column in range(columns):
            curve_left, curve_right = _split_curve([coefficients[row][column] for row in range(rows)])
            for row in range(rows):
                left[row][column] = curve_left[row]
                right[row][column] = curve_right[row]
        return left, right
    left = [[arb(0) for _ in range(columns)] for _ in range(rows)]
    right = [[arb(0) for _ in range(columns)] for _ in range(rows)]
    for row in range(rows):
        curve_left, curve_right = _split_curve(coefficients[row])
        left[row] = curve_left
        right[row] = curve_right
    return left, right


def _bernstein_max_abs(coefficients: list[list[arb]], subdivision_depth: int) -> tuple[arb, int]:
    patches = [coefficients]
    for _ in range(subdivision_depth):
        refined: list[list[list[arb]]] = []
        for patch in patches:
            left, right = _split_patch(patch, 0)
            for half in (left, right):
                bottom, top = _split_patch(half, 1)
                refined.extend((bottom, top))
        patches = refined
    maximum = arb(0)
    for patch in patches:
        for row in patch:
            for coefficient in row:
                maximum = maximum.max(coefficient.abs_upper())
    return maximum, len(patches)


def _max_abs_on_reachable(
    low_sum: BiPoly, high_sum: BiPoly, *, subdivision_depth: int
) -> tuple[arb, dict[str, int]]:
    low_parameterized = _parameterize_triangle(low_sum)
    high_parameterized = _parameterize_triangle(high_sum)
    low_unit = _affine_to_unit_square(
        low_parameterized, arb(0), arb(1), arb(0), arb(1)
    )
    high_unit = _affine_to_unit_square(
        high_parameterized, arb(1), arb(4), arb(0), arb(1)
    )
    low_max, low_patches = _bernstein_max_abs(
        _power_to_bernstein(low_unit), subdivision_depth
    )
    high_max, high_patches = _bernstein_max_abs(
        _power_to_bernstein(high_unit), subdivision_depth
    )

    plus_tail: BiPoly = {(i, 0): coefficient for (i, j), coefficient in high_sum.items() if j == 0}
    minus_tail: BiPoly = {(0, j): coefficient for (i, j), coefficient in high_sum.items() if i == 0}
    plus_unit = _affine_to_unit_square(plus_tail, arb(4), arb(5), arb(0), arb(1))
    minus_unit = _affine_to_unit_square(minus_tail, arb(0), arb(1), arb(4), arb(5))
    plus_max, plus_patches = _bernstein_max_abs(
        _power_to_bernstein(plus_unit), subdivision_depth
    )
    minus_max, minus_patches = _bernstein_max_abs(
        _power_to_bernstein(minus_unit), subdivision_depth
    )
    maximum = low_max.max(high_max).max(plus_max).max(minus_max)
    return maximum, {
        "subdivision_depth": subdivision_depth,
        "bernstein_patches": low_patches + high_patches + plus_patches + minus_patches,
    }


def _chebyshev_sup(payload: Mapping[str, object]) -> arb:
    scale = arb(2) ** int(payload["scale_bits"])
    total = arb(0)
    for row in payload["numerators"]:
        for numerator in row:
            total += abs(arb(int(numerator)) / scale)
    return total


def certify_continuum_residuals(
    candidate_payloads: Mapping[str, object],
    *,
    phi_order: int = 50,
    subdivision_depth: int = 3,
    bits: int = 256,
) -> dict[str, object]:
    with workprec(bits):
        a_payload = candidate_payloads["a"]
        b_payload = candidate_payloads["b"]
        a_hat = chebyshev_payload_to_power(a_payload)
        b_hat = chebyshev_payload_to_power(b_payload)
        phi_coefficients = _phi_coefficients(phi_order)
        k_a_low, k_a_high = _kernel_polynomials(a_hat, phi_coefficients, z_weight=0)
        k_b_low, k_b_high = _kernel_polynomials(b_hat, phi_coefficients, z_weight=0)
        kz_a_low, kz_a_high = _kernel_polynomials(a_hat, phi_coefficients, z_weight=1)
        reward_a, reward_b = _reward_polynomials(phi_coefficients)

        residual_a_low = bi_add(bi_add(a_hat, bi_scale(k_a_low, -arb(1))), bi_scale(reward_a, -arb(1)))
        residual_a_high = bi_add(bi_add(a_hat, bi_scale(k_a_high, -arb(1))), bi_scale(reward_a, -arb(1)))
        residual_b_low = bi_add(bi_add(b_hat, bi_scale(k_b_low, -arb(1))), bi_scale(kz_a_low, -arb(1)))
        residual_b_low = bi_add(residual_b_low, bi_scale(reward_b, -arb(1)))
        residual_b_high = bi_add(bi_add(b_hat, bi_scale(k_b_high, -arb(1))), bi_scale(kz_a_high, -arb(1)))
        residual_b_high = bi_add(residual_b_high, bi_scale(reward_b, -arb(1)))

        polynomial_a, coverage = _max_abs_on_reachable(
            residual_a_low,
            residual_a_high,
            subdivision_depth=subdivision_depth,
        )
        polynomial_b, _ = _max_abs_on_reachable(
            residual_b_low,
            residual_b_high,
            subdivision_depth=subdivision_depth,
        )

        max_y = rational(121, 8)  # (5.5^2)/2
        phi_error = (max_y ** (phi_order + 1)) / (
            arb(factorial(phi_order + 1)) * (arb(2) * arb.pi()).sqrt()
        )
        sup_a = _chebyshev_sup(a_payload)
        sup_b = _chebyshev_sup(b_payload)
        delta_a = polynomial_a + (arb(11) * sup_a + arb(2)) * phi_error
        delta_b = polynomial_b + (
            arb(11) * sup_b + rational(121, 2) * sup_a + arb(22)
        ) * phi_error
        if not delta_a > 0 or not delta_b > 0:
            raise ArithmeticError("invalid residual bounds")
        b_at_origin = bi_eval(b_hat, arb(0), arb(0))
        return {
            "schema": "rebaseguard.continuum-residual.v1",
            "precision_bits": bits,
            "phi_taylor_order": phi_order,
            "phi_uniform_error": ball_record(phi_error),
            "candidate_sup_a": ball_record(sup_a),
            "candidate_sup_b": ball_record(sup_b),
            "polynomial_residual_a": ball_record(polynomial_a),
            "polynomial_residual_b": ball_record(polynomial_b),
            "delta_a": ball_record(delta_a),
            "delta_b": ball_record(delta_b),
            "b_hat_origin": ball_record(b_at_origin),
            "coverage": {
                **coverage,
                "parameterization": "p=r*t, m=r*(1-t)",
                "pieces": ["0<=r<=1", "1<=r<=4", "axis tails 4<=r<=5"],
                "reachable_continuum_complete": True,
                "gaussian_tail_truncation": "none",
            },
        }
