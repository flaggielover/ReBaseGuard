"""Outward-rounded tensor Bernstein bounds for centered bivariate models."""

from __future__ import annotations

from math import comb

from flint import arb

from taylor_model import Model


def centered_model_to_unit_power(
    model: Model, radius_plus: arb, radius_minus: arb
) -> dict[tuple[int, int], arb]:
    """Map centered variables to ``[-r,r]`` and then ``u,v in [0,1]``."""

    if model.variables != 2:
        raise ValueError("Bernstein conversion requires a bivariate model")
    result: dict[tuple[int, int], arb] = {}
    for (degree_plus, degree_minus), coefficient in model.coefficients.items():
        for i in range(degree_plus + 1):
            plus_factor = (
                arb(comb(degree_plus, i))
                * (-radius_plus) ** (degree_plus - i)
                * (arb(2) * radius_plus) ** i
            )
            for j in range(degree_minus + 1):
                minus_factor = (
                    arb(comb(degree_minus, j))
                    * (-radius_minus) ** (degree_minus - j)
                    * (arb(2) * radius_minus) ** j
                )
                exponent = (i, j)
                result[exponent] = result.get(exponent, arb(0)) + (
                    coefficient * plus_factor * minus_factor
                )
    return result


def power_to_bernstein(
    coefficients: dict[tuple[int, int], arb]
) -> list[list[arb]]:
    degree_plus = max((i for i, _ in coefficients), default=0)
    degree_minus = max((j for _, j in coefficients), default=0)
    result = [
        [arb(0) for _ in range(degree_minus + 1)]
        for _ in range(degree_plus + 1)
    ]
    for k in range(degree_plus + 1):
        for ell in range(degree_minus + 1):
            value = arb(0)
            for i in range(k + 1):
                plus_factor = arb(comb(k, i)) / arb(comb(degree_plus, i))
                for j in range(ell + 1):
                    minus_factor = arb(comb(ell, j)) / arb(
                        comb(degree_minus, j)
                    )
                    value += (
                        coefficients.get((i, j), arb(0))
                        * plus_factor
                        * minus_factor
                    )
            result[k][ell] = value
    return result


def bernstein_absolute_bound(
    model: Model, radius_plus: arb, radius_minus: arb
) -> tuple[arb, list[list[arb]]]:
    power = centered_model_to_unit_power(model, radius_plus, radius_minus)
    bernstein = power_to_bernstein(power)
    bound = arb(0)
    for row in bernstein:
        for coefficient in row:
            bound = bound.max(coefficient.abs_upper())
    return bound, bernstein
