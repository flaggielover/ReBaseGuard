"""Truncated multivariate Taylor algebra over Arb balls."""

from __future__ import annotations

from dataclasses import dataclass
from math import factorial

from flint import arb


Exponent = tuple[int, ...]


@dataclass(frozen=True)
class Model:
    coefficients: dict[Exponent, arb]
    variables: int
    order: int

    @classmethod
    def constant(cls, value: arb, variables: int, order: int) -> "Model":
        return cls({(0,) * variables: value}, variables, order)

    @classmethod
    def variable(
        cls, value: arb, index: int, variables: int, order: int
    ) -> "Model":
        exponent = [0] * variables
        exponent[index] = 1
        return cls(
            {(0,) * variables: value, tuple(exponent): arb(1)}, variables, order
        )

    @property
    def constant_term(self) -> arb:
        return self.coefficients.get((0,) * self.variables, arb(0))

    def __add__(self, other: "Model") -> "Model":
        result = dict(self.coefficients)
        for exponent, value in other.coefficients.items():
            result[exponent] = result.get(exponent, arb(0)) + value
        return Model(result, self.variables, self.order)

    def __neg__(self) -> "Model":
        return self.scale(-arb(1))

    def __sub__(self, other: "Model") -> "Model":
        return self + (-other)

    def scale(self, factor: arb) -> "Model":
        return Model(
            {exponent: value * factor for exponent, value in self.coefficients.items()},
            self.variables,
            self.order,
        )

    def __mul__(self, other: "Model") -> "Model":
        result: dict[Exponent, arb] = {}
        for left_exponent, left_value in self.coefficients.items():
            for right_exponent, right_value in other.coefficients.items():
                exponent = tuple(
                    a + b for a, b in zip(left_exponent, right_exponent, strict=True)
                )
                if sum(exponent) <= self.order:
                    result[exponent] = result.get(exponent, arb(0)) + left_value * right_value
        return Model(result, self.variables, self.order)

    def power(self, exponent: int) -> "Model":
        result = Model.constant(arb(1), self.variables, self.order)
        factor = self
        power = exponent
        while power:
            if power & 1:
                result = result * factor
            factor = factor * factor
            power >>= 1
        return result

    def reciprocal(self) -> "Model":
        center = self.constant_term
        if not center > 0 and not center < 0:
            raise ZeroDivisionError("Taylor center enclosure contains zero")
        reciprocal_center = (arb(1) / center.upper()).union(
            arb(1) / center.lower()
        )
        nonconstant = dict(self.coefficients)
        nonconstant[(0,) * self.variables] = arb(0)
        remainder = Model(nonconstant, self.variables, self.order).scale(
            reciprocal_center
        )
        result = Model.constant(arb(0), self.variables, self.order)
        term = Model.constant(arb(1), self.variables, self.order)
        for degree in range(self.order + 1):
            result = result + term.scale((-arb(1)) ** degree)
            term = term * remainder
        return result.scale(reciprocal_center)

    def exp(self) -> "Model":
        center = self.constant_term
        exponential_center = center.lower().exp().union(center.upper().exp())
        nonconstant = dict(self.coefficients)
        nonconstant[(0,) * self.variables] = arb(0)
        remainder = Model(nonconstant, self.variables, self.order)
        result = Model.constant(arb(0), self.variables, self.order)
        term = Model.constant(arb(1), self.variables, self.order)
        for degree in range(self.order + 1):
            result = result + term.scale(arb(1) / arb(factorial(degree)))
            term = term * remainder
        return result.scale(exponential_center)

    def log(self) -> "Model":
        center = self.constant_term
        if not center > 0:
            raise ValueError("Taylor logarithm center enclosure is not positive")
        logarithm_center = center.lower().log().union(center.upper().log())
        reciprocal_center = (arb(1) / center.upper()).union(
            arb(1) / center.lower()
        )
        nonconstant = dict(self.coefficients)
        nonconstant[(0,) * self.variables] = arb(0)
        remainder = Model(nonconstant, self.variables, self.order).scale(
            reciprocal_center
        )
        result = Model.constant(logarithm_center, self.variables, self.order)
        term = remainder
        for degree in range(1, self.order + 1):
            result = result + term.scale(((-arb(1)) ** (degree + 1)) / arb(degree))
            term = term * remainder
        return result


def softplus(value: Model) -> Model:
    return (Model.constant(arb(1), value.variables, value.order) + value.exp()).log()


def chebyshev_values(value: Model, degree: int) -> list[Model]:
    one = Model.constant(arb(1), value.variables, value.order)
    result = [one]
    if degree:
        result.append(value)
    for _ in range(2, degree + 1):
        result.append((value * result[-1]).scale(arb(2)) - result[-2])
    return result


def evaluate_candidate(
    coefficients: list[list[int]],
    scale_bits: int,
    live_max: arb,
    y_plus: Model,
    y_minus: Model,
) -> Model:
    one = Model.constant(arb(1), y_plus.variables, y_plus.order)
    x_plus = y_plus.scale(arb(2) / live_max) - one
    x_minus = y_minus.scale(arb(2) / live_max) - one
    plus = chebyshev_values(x_plus, len(coefficients) - 1)
    minus = chebyshev_values(x_minus, len(coefficients) - 1)
    result = Model.constant(arb(0), y_plus.variables, y_plus.order)
    denominator = arb(1 << scale_bits)
    for i, row in enumerate(coefficients):
        for j, numerator in enumerate(row):
            if numerator:
                result = result + (plus[i] * minus[j]).scale(
                    arb(numerator) / denominator
                )
    return result


def gaussian_density(value: Model) -> Model:
    return (value * value).scale(-arb(1) / arb(2)).exp().scale(
        arb(1) / (arb(2) * arb.pi()).sqrt()
    )


def total_degree_remainder(model: Model, radii: tuple[arb, ...]) -> arb:
    target = model.order
    result = arb(0)
    for exponent, coefficient in model.coefficients.items():
        if sum(exponent) == target:
            term = coefficient.abs_upper()
            for radius, power in zip(radii, exponent, strict=True):
                term *= radius ** power
            result += term
    return result


def integrate_last_variable(model: Model, radius: arb) -> Model:
    """Integrate a centered model over the last variable's symmetric interval."""

    result: dict[Exponent, arb] = {}
    for exponent, coefficient in model.coefficients.items():
        last = exponent[-1]
        if last % 2:
            continue
        reduced = exponent[:-1]
        value = coefficient * arb(2) * radius ** (last + 1) / arb(last + 1)
        result[reduced] = result.get(reduced, arb(0)) + value
    return Model(result, model.variables - 1, model.order)


def taylor_absolute_bound(model: Model, radii: tuple[arb, ...]) -> arb:
    result = arb(0)
    for exponent, coefficient in model.coefficients.items():
        term = coefficient.abs_upper()
        for radius, power in zip(radii, exponent, strict=True):
            term *= radius ** power
        result += term
    return result
