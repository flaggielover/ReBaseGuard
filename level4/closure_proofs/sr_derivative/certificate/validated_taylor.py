"""Small outward-rounded Taylor engine for SR residual integration.

The coefficient convention is ``f^(k)(x) / k!``.  Point jets retain the
cancellation in the Bellman residual.  Interval-center jets enclose the next
Taylor coefficient throughout a subinterval and therefore give a rigorous
integral remainder.  This module has no NumPy/SciPy dependency and is intended
for proof-critical use with exact-dyadic candidates.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from flint import arb


Jet = list[arb]


def constant(value: arb, order: int) -> Jet:
    return [value] + [arb(0) for _ in range(order)]


def variable(value: arb, order: int) -> Jet:
    result = constant(value, order)
    if order:
        result[1] = arb(1)
    return result


def add(left: Jet, right: Jet) -> Jet:
    return [a + b for a, b in zip(left, right, strict=True)]


def scale(value: Jet, factor: arb) -> Jet:
    return [coefficient * factor for coefficient in value]


def multiply(left: Jet, right: Jet) -> Jet:
    order = len(left) - 1
    return [
        sum((left[k] * right[n - k] for k in range(n + 1)), arb(0))
        for n in range(order + 1)
    ]


def reciprocal(value: Jet) -> Jet:
    order = len(value) - 1
    result = [arb(1) / value[0]] + [arb(0) for _ in range(order)]
    for n in range(1, order + 1):
        result[n] = -sum(
            (value[k] * result[n - k] for k in range(1, n + 1)), arb(0)
        ) / value[0]
    return result


def exponential(value: Jet) -> Jet:
    order = len(value) - 1
    result = [value[0].exp()] + [arb(0) for _ in range(order)]
    for n in range(1, order + 1):
        result[n] = sum(
            (
                arb(k) * value[k] * result[n - k]
                for k in range(1, n + 1)
            ),
            arb(0),
        ) / arb(n)
    return result


def logarithm(value: Jet) -> Jet:
    order = len(value) - 1
    derivative = [arb(k + 1) * value[k + 1] for k in range(order)]
    quotient = multiply(derivative + [arb(0)], reciprocal(value))
    result = [value[0].log()] + [arb(0) for _ in range(order)]
    for n in range(1, order + 1):
        result[n] = quotient[n - 1] / arb(n)
    return result


def softplus(value: Jet) -> Jet:
    return logarithm(add(constant(arb(1), len(value) - 1), exponential(value)))


def chebyshev_values(value: Jet, degree: int) -> list[Jet]:
    order = len(value) - 1
    result = [constant(arb(1), order)]
    if degree == 0:
        return result
    result.append(value)
    for _ in range(2, degree + 1):
        result.append(
            add(scale(multiply(value, result[-1]), arb(2)), scale(result[-2], -arb(1)))
        )
    return result


def chebyshev_derivatives(value: Jet, degree: int) -> list[Jet]:
    """Return derivatives of ``T_0`` through ``T_degree``."""

    order = len(value) - 1
    derivatives = [constant(arb(0), order)]
    if degree == 0:
        return derivatives
    second_kind = [constant(arb(1), order)]
    if degree > 1:
        second_kind.append(scale(value, arb(2)))
        for _ in range(2, degree):
            second_kind.append(
                add(
                    scale(multiply(value, second_kind[-1]), arb(2)),
                    scale(second_kind[-2], -arb(1)),
                )
            )
    derivatives.extend(
        scale(second_kind[n - 1], arb(n)) for n in range(1, degree + 1)
    )
    return derivatives


def evaluate_chebyshev_candidate(
    coefficients: Sequence[Sequence[int]],
    *,
    scale_bits: int,
    live_max: arb,
    y_plus: Jet,
    y_minus: Jet,
) -> Jet:
    order = len(y_plus) - 1
    normalized_plus = add(
        scale(y_plus, arb(2) / live_max), constant(-arb(1), order)
    )
    normalized_minus = add(
        scale(y_minus, arb(2) / live_max), constant(-arb(1), order)
    )
    plus_values = chebyshev_values(normalized_plus, len(coefficients) - 1)
    minus_values = chebyshev_values(normalized_minus, len(coefficients) - 1)
    denominator = arb(1 << scale_bits)
    result = constant(arb(0), order)
    for i, row in enumerate(coefficients):
        for j, numerator in enumerate(row):
            if numerator:
                result = add(
                    result,
                    scale(
                        multiply(plus_values[i], minus_values[j]),
                        arb(int(numerator)) / denominator,
                    ),
                )
    return result


def evaluate_candidate_with_gradient(
    coefficients: Sequence[Sequence[int]],
    *,
    scale_bits: int,
    live_max: arb,
    y_plus: Jet,
    y_minus: Jet,
) -> tuple[Jet, Jet, Jet]:
    """Evaluate a candidate and its two exact coordinate derivatives."""

    order = len(y_plus) - 1
    normalized_plus = add(
        scale(y_plus, arb(2) / live_max), constant(-arb(1), order)
    )
    normalized_minus = add(
        scale(y_minus, arb(2) / live_max), constant(-arb(1), order)
    )
    degree = len(coefficients) - 1
    plus_values = chebyshev_values(normalized_plus, degree)
    minus_values = chebyshev_values(normalized_minus, degree)
    plus_derivatives = chebyshev_derivatives(normalized_plus, degree)
    minus_derivatives = chebyshev_derivatives(normalized_minus, degree)
    denominator = arb(1 << scale_bits)
    coordinate_scale = arb(2) / live_max
    value = constant(arb(0), order)
    derivative_plus = constant(arb(0), order)
    derivative_minus = constant(arb(0), order)
    for i, row in enumerate(coefficients):
        for j, numerator in enumerate(row):
            if not numerator:
                continue
            coefficient = arb(int(numerator)) / denominator
            value = add(
                value,
                scale(multiply(plus_values[i], minus_values[j]), coefficient),
            )
            derivative_plus = add(
                derivative_plus,
                scale(
                    multiply(plus_derivatives[i], minus_values[j]),
                    coefficient * coordinate_scale,
                ),
            )
            derivative_minus = add(
                derivative_minus,
                scale(
                    multiply(plus_values[i], minus_derivatives[j]),
                    coefficient * coordinate_scale,
                ),
            )
    return value, derivative_plus, derivative_minus


def sigmoid(value: Jet) -> Jet:
    exponential_value = exponential(value)
    return multiply(
        exponential_value,
        reciprocal(add(constant(arb(1), len(value) - 1), exponential_value)),
    )


def gaussian_density(value: Jet) -> Jet:
    square = multiply(value, value)
    numerator = exponential(scale(square, -arb(1) / arb(2)))
    return scale(numerator, arb(1) / (arb(2) * arb.pi()).sqrt())


def integrate_with_taylor_remainder(
    function: Callable[[Jet], Jet],
    lower: arb,
    upper: arb,
    *,
    partitions: int,
    order: int,
) -> arb:
    """Enclose an integral using centered Taylor polynomials and remainders."""

    if partitions < 1 or order < 2:
        raise ValueError("invalid validated Taylor integration parameters")
    step = (upper - lower) / arb(partitions)
    total = arb(0)
    for index in range(partitions):
        left = lower + arb(index) * step
        right = lower + arb(index + 1) * step
        center = (left + right) / arb(2)
        radius = step / arb(2)
        point_coefficients = function(variable(center, order - 1))
        polynomial_integral = arb(0)
        for degree in range(0, order, 2):
            polynomial_integral += (
                arb(2)
                * point_coefficients[degree]
                * radius ** (degree + 1)
                / arb(degree + 1)
            )
        cell = left.union(right)
        remainder_coefficient = function(variable(cell, order))[order].abs_upper()
        remainder = (
            arb(2)
            * remainder_coefficient
            * radius ** (order + 1)
            / arb(order + 1)
        )
        total += polynomial_integral + arb(0, 1) * remainder
    return total
