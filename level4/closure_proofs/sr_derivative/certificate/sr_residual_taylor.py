"""Cancellation-preserving Taylor patch bounds for the SR Bellman residual."""

from __future__ import annotations

from dataclasses import dataclass

from flint import arb

from taylor_model import (
    Model,
    evaluate_candidate,
    gaussian_density,
    integrate_last_variable,
    softplus,
    taylor_absolute_bound,
    total_degree_remainder,
)


@dataclass(frozen=True)
class PatchBound:
    residual_a: arb
    polynomial_a: arb
    remainder_a: arb


def _constant(value: arb, variables: int, order: int) -> Model:
    return Model.constant(value, variables, order)


def _integrand_a(
    coefficients_a: list[list[int]],
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    y_plus: Model,
    y_minus: Model,
    t: Model,
) -> Model:
    variables = y_plus.variables
    order = y_plus.order
    half = arb(1) / arb(2)
    midpoint = (y_minus - y_plus).scale(half)
    half_width = _constant(log_a + half, variables, order) - (
        y_plus + y_minus
    ).scale(half)
    z = midpoint + half_width * t
    q_plus = softplus(y_plus + z - _constant(half, variables, order))
    q_minus = softplus(y_minus - z - _constant(half, variables, order))
    candidate = evaluate_candidate(
        coefficients_a, scale_bits, live_max, q_plus, q_minus
    )
    return half_width * candidate * gaussian_density(z)


def _state_candidate_a(
    coefficients_a: list[list[int]],
    scale_bits: int,
    live_max: arb,
    y_plus: Model,
    y_minus: Model,
) -> Model:
    return evaluate_candidate(
        coefficients_a, scale_bits, live_max, y_plus, y_minus
    )


def _reward_a(log_a: arb, y_plus: Model, y_minus: Model) -> Model:
    half = arb(1) / arb(2)
    constant = _constant(log_a + half, y_plus.variables, y_plus.order)
    upper = constant - y_plus
    lower = y_minus - constant
    return gaussian_density(upper) - gaussian_density(lower)


def bound_residual_a_patch(
    coefficients_a: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    plus_lower: arb,
    plus_upper: arb,
    minus_lower: arb,
    minus_upper: arb,
    innovation_partitions: int = 24,
    order: int = 8,
) -> PatchBound:
    """Bound the complete ``a-Ka-r_a`` residual on one state rectangle."""

    center_plus = (plus_lower + plus_upper) / arb(2)
    center_minus = (minus_lower + minus_upper) / arb(2)
    radius_plus = (plus_upper - plus_lower) / arb(2)
    radius_minus = (minus_upper - minus_lower) / arb(2)

    y_plus = Model.variable(center_plus, 0, 2, order)
    y_minus = Model.variable(center_minus, 1, 2, order)
    residual_model = _state_candidate_a(
        coefficients_a, scale_bits, live_max, y_plus, y_minus
    ) - _reward_a(log_a, y_plus, y_minus)

    direct_interval_plus = plus_lower.union(plus_upper)
    direct_interval_minus = minus_lower.union(minus_upper)
    interval_plus = Model.variable(direct_interval_plus, 0, 2, order + 1)
    interval_minus = Model.variable(direct_interval_minus, 1, 2, order + 1)
    direct_remainder = total_degree_remainder(
        _state_candidate_a(
            coefficients_a, scale_bits, live_max, interval_plus, interval_minus
        ),
        (radius_plus, radius_minus),
    )
    reward_remainder = total_degree_remainder(
        _reward_a(log_a, interval_plus, interval_minus),
        (radius_plus, radius_minus),
    )

    t_step = arb(2) / arb(innovation_partitions)
    integration_remainder = arb(0)
    for index in range(innovation_partitions):
        t_left = -arb(1) + arb(index) * t_step
        t_right = t_left + t_step
        t_center = (t_left + t_right) / arb(2)
        t_radius = t_step / arb(2)

        yp = Model.variable(center_plus, 0, 3, order)
        ym = Model.variable(center_minus, 1, 3, order)
        t = Model.variable(t_center, 2, 3, order)
        integrand = _integrand_a(
            coefficients_a, scale_bits, live_max, log_a, yp, ym, t
        )
        integrated = integrate_last_variable(integrand, t_radius)
        residual_model = residual_model - integrated

        yp_interval = Model.variable(direct_interval_plus, 0, 3, order + 1)
        ym_interval = Model.variable(direct_interval_minus, 1, 3, order + 1)
        t_interval = Model.variable(t_left.union(t_right), 2, 3, order + 1)
        interval_integrand = _integrand_a(
            coefficients_a,
            scale_bits,
            live_max,
            log_a,
            yp_interval,
            ym_interval,
            t_interval,
        )
        integration_remainder += arb(2) * t_radius * total_degree_remainder(
            interval_integrand,
            (radius_plus, radius_minus, t_radius),
        )

    polynomial_bound = taylor_absolute_bound(
        residual_model, (radius_plus, radius_minus)
    )
    remainder = direct_remainder + reward_remainder + integration_remainder
    return PatchBound(
        residual_a=polynomial_bound + remainder,
        polynomial_a=polynomial_bound,
        remainder_a=remainder,
    )
