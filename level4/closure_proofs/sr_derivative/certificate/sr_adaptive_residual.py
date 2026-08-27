"""Rigorous local refinement primitives for adaptive SR residual bounds."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from flint import arb

from sr_residual_taylor import (
    _integrand_a,
    _integrand_b,
    _reward_a,
    _state_candidate_a,
    _state_candidate_b,
)
from taylor_model import Model, integrate_last_variable, taylor_absolute_bound
from taylor_model import total_degree_remainder
from sr_bernstein import bernstein_absolute_bound


@dataclass(frozen=True)
class Rectangle:
    plus_lower: arb
    plus_upper: arb
    minus_lower: arb
    minus_upper: arb

    def bisect(self) -> tuple["Rectangle", "Rectangle", "Rectangle", "Rectangle"]:
        plus_midpoint = (self.plus_lower + self.plus_upper) / arb(2)
        minus_midpoint = (self.minus_lower + self.minus_upper) / arb(2)
        return (
            Rectangle(
                self.plus_lower,
                plus_midpoint,
                self.minus_lower,
                minus_midpoint,
            ),
            Rectangle(
                plus_midpoint,
                self.plus_upper,
                self.minus_lower,
                minus_midpoint,
            ),
            Rectangle(
                self.plus_lower,
                plus_midpoint,
                minus_midpoint,
                self.minus_upper,
            ),
            Rectangle(
                plus_midpoint,
                self.plus_upper,
                minus_midpoint,
                self.minus_upper,
            ),
        )


@dataclass(frozen=True)
class InnovationInterval:
    lower: arb
    upper: arb
    depth: int = 0

    def bisect(self) -> tuple["InnovationInterval", "InnovationInterval"]:
        midpoint = (self.lower + self.upper) / arb(2)
        return (
            InnovationInterval(self.lower, midpoint, self.depth + 1),
            InnovationInterval(midpoint, self.upper, self.depth + 1),
        )


def local_integration_remainder_a(
    candidate_a: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    state: Rectangle,
    innovation: InnovationInterval,
    taylor_order: int,
) -> arb:
    """Bound one transformed-innovation interval's integrated remainder."""

    remainder_order = taylor_order + 1
    plus_interval = state.plus_lower.union(state.plus_upper)
    minus_interval = state.minus_lower.union(state.minus_upper)
    innovation_ball = innovation.lower.union(innovation.upper)
    plus_radius = (state.plus_upper - state.plus_lower) / arb(2)
    minus_radius = (state.minus_upper - state.minus_lower) / arb(2)
    innovation_radius = (innovation.upper - innovation.lower) / arb(2)
    integrand = _integrand_a(
        candidate_a,
        scale_bits,
        live_max,
        log_a,
        Model.variable(plus_interval, 0, 3, remainder_order),
        Model.variable(minus_interval, 1, 3, remainder_order),
        Model.variable(innovation_ball, 2, 3, remainder_order),
    )
    total = arb(0)
    for exponent, coefficient in integrand.coefficients.items():
        if sum(exponent) != remainder_order:
            continue
        total += (
            arb(2)
            * innovation_radius
            * coefficient.abs_upper()
            * plus_radius ** exponent[0]
            * minus_radius ** exponent[1]
            * innovation_radius ** exponent[2]
        )
    return total


def innovation_split_bound(
    candidate_a: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    state: Rectangle,
    innovation: InnovationInterval,
    taylor_order: int,
) -> tuple[arb, tuple[arb, arb]]:
    children = innovation.bisect()
    child_bounds = tuple(
        local_integration_remainder_a(
            candidate_a,
            scale_bits=scale_bits,
            live_max=live_max,
            log_a=log_a,
            state=state,
            innovation=child,
            taylor_order=taylor_order,
        )
        for child in children
    )
    return child_bounds[0] + child_bounds[1], child_bounds


def state_split_bound(
    candidate_a: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    state: Rectangle,
    innovation: InnovationInterval,
    taylor_order: int,
) -> tuple[arb, tuple[arb, arb, arb, arb]]:
    child_bounds = tuple(
        local_integration_remainder_a(
            candidate_a,
            scale_bits=scale_bits,
            live_max=live_max,
            log_a=log_a,
            state=child,
            innovation=innovation,
            taylor_order=taylor_order,
        )
        for child in state.bisect()
    )
    return max(child_bounds), child_bounds


def matched_polynomial_residual_model_a(
    candidate_a: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    state: Rectangle,
    innovations: list[InnovationInterval],
    taylor_order: int,
) -> Model:
    """Build the residual polynomial on the exact adaptive leaves."""

    plus_center = (state.plus_lower + state.plus_upper) / arb(2)
    minus_center = (state.minus_lower + state.minus_upper) / arb(2)
    plus_radius = (state.plus_upper - state.plus_lower) / arb(2)
    minus_radius = (state.minus_upper - state.minus_lower) / arb(2)
    y_plus = Model.variable(plus_center, 0, 2, taylor_order)
    y_minus = Model.variable(minus_center, 1, 2, taylor_order)
    residual = _state_candidate_a(
        candidate_a, scale_bits, live_max, y_plus, y_minus
    ) - _reward_a(log_a, y_plus, y_minus)
    for innovation in innovations:
        t_center = (innovation.lower + innovation.upper) / arb(2)
        t_radius = (innovation.upper - innovation.lower) / arb(2)
        integrand = _integrand_a(
            candidate_a,
            scale_bits,
            live_max,
            log_a,
            Model.variable(plus_center, 0, 3, taylor_order),
            Model.variable(minus_center, 1, 3, taylor_order),
            Model.variable(t_center, 2, 3, taylor_order),
        )
        residual = residual - integrate_last_variable(integrand, t_radius)
    return residual


def matched_polynomial_residual_a(
    candidate_a: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    state: Rectangle,
    innovations: list[InnovationInterval],
    taylor_order: int,
) -> arb:
    model = matched_polynomial_residual_model_a(
        candidate_a,
        scale_bits=scale_bits,
        live_max=live_max,
        log_a=log_a,
        state=state,
        innovations=innovations,
        taylor_order=taylor_order,
    )
    return taylor_absolute_bound(
        model,
        (
            (state.plus_upper - state.plus_lower) / arb(2),
            (state.minus_upper - state.minus_lower) / arb(2),
        ),
    )


def static_state_remainder_a(
    candidate_a: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    state: Rectangle,
    taylor_order: int,
) -> tuple[arb, arb]:
    remainder_order = taylor_order + 1
    plus_interval = state.plus_lower.union(state.plus_upper)
    minus_interval = state.minus_lower.union(state.minus_upper)
    plus_radius = (state.plus_upper - state.plus_lower) / arb(2)
    minus_radius = (state.minus_upper - state.minus_lower) / arb(2)
    yp = Model.variable(plus_interval, 0, 2, remainder_order)
    ym = Model.variable(minus_interval, 1, 2, remainder_order)
    direct = total_degree_remainder(
        _state_candidate_a(candidate_a, scale_bits, live_max, yp, ym),
        (plus_radius, minus_radius),
    )
    reward = total_degree_remainder(
        _reward_a(log_a, yp, ym), (plus_radius, minus_radius)
    )
    return direct, reward


def local_integration_remainder_b(
    candidate_a: list[list[int]],
    candidate_b: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    state: Rectangle,
    innovation: InnovationInterval,
    taylor_order: int,
) -> arb:
    remainder_order = taylor_order + 1
    plus_interval = state.plus_lower.union(state.plus_upper)
    minus_interval = state.minus_lower.union(state.minus_upper)
    innovation_ball = innovation.lower.union(innovation.upper)
    plus_radius = (state.plus_upper - state.plus_lower) / arb(2)
    minus_radius = (state.minus_upper - state.minus_lower) / arb(2)
    innovation_radius = (innovation.upper - innovation.lower) / arb(2)
    integrand = _integrand_b(
        candidate_a,
        candidate_b,
        scale_bits,
        live_max,
        log_a,
        Model.variable(plus_interval, 0, 3, remainder_order),
        Model.variable(minus_interval, 1, 3, remainder_order),
        Model.variable(innovation_ball, 2, 3, remainder_order),
    )
    total = arb(0)
    for exponent, coefficient in integrand.coefficients.items():
        if sum(exponent) != remainder_order:
            continue
        total += (
            arb(2)
            * innovation_radius
            * coefficient.abs_upper()
            * plus_radius ** exponent[0]
            * minus_radius ** exponent[1]
            * innovation_radius ** exponent[2]
        )
    return total


def matched_polynomial_residual_model_b(
    candidate_a: list[list[int]],
    candidate_b: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    state: Rectangle,
    innovations: list[InnovationInterval],
    taylor_order: int,
) -> Model:
    plus_center = (state.plus_lower + state.plus_upper) / arb(2)
    minus_center = (state.minus_lower + state.minus_upper) / arb(2)
    y_plus = Model.variable(plus_center, 0, 2, taylor_order)
    y_minus = Model.variable(minus_center, 1, 2, taylor_order)
    residual = _state_candidate_b(
        candidate_b, scale_bits, live_max, y_plus, y_minus
    ) - Model.constant(arb(1), 2, taylor_order)
    for innovation in innovations:
        t_center = (innovation.lower + innovation.upper) / arb(2)
        t_radius = (innovation.upper - innovation.lower) / arb(2)
        integrand = _integrand_b(
            candidate_a,
            candidate_b,
            scale_bits,
            live_max,
            log_a,
            Model.variable(plus_center, 0, 3, taylor_order),
            Model.variable(minus_center, 1, 3, taylor_order),
            Model.variable(t_center, 2, 3, taylor_order),
        )
        residual = residual - integrate_last_variable(integrand, t_radius)
    return residual


def static_state_remainder_b(
    candidate_b: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    state: Rectangle,
    taylor_order: int,
) -> arb:
    remainder_order = taylor_order + 1
    plus_interval = state.plus_lower.union(state.plus_upper)
    minus_interval = state.minus_lower.union(state.minus_upper)
    plus_radius = (state.plus_upper - state.plus_lower) / arb(2)
    minus_radius = (state.minus_upper - state.minus_lower) / arb(2)
    yp = Model.variable(plus_interval, 0, 2, remainder_order)
    ym = Model.variable(minus_interval, 1, 2, remainder_order)
    return total_degree_remainder(
        _state_candidate_b(candidate_b, scale_bits, live_max, yp, ym),
        (plus_radius, minus_radius),
    )


def fraction_to_arb(value: Fraction) -> arb:
    return arb(value.numerator) / arb(value.denominator)


def certify_adaptive_patch_a(
    candidate_a: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    normalized_plus: tuple[Fraction, Fraction],
    normalized_minus: tuple[Fraction, Fraction],
    taylor_order: int = 6,
    initial_partitions: int = 32,
    integration_target: Fraction = Fraction(4, 1_000_000),
    patch_target: Fraction = Fraction(5, 1_000_000),
    max_depth: int = 5,
    max_intervals: int = 256,
    include_trace: bool = True,
) -> dict[str, object]:
    """Certify one exact normalized state rectangle by adaptive innovation splits."""

    state = Rectangle(
        live_max * fraction_to_arb(normalized_plus[0]),
        live_max * fraction_to_arb(normalized_plus[1]),
        live_max * fraction_to_arb(normalized_minus[0]),
        live_max * fraction_to_arb(normalized_minus[1]),
    )
    step = Fraction(2, initial_partitions)
    leaves: list[tuple[Fraction, Fraction, int, arb]] = []
    for index in range(initial_partitions):
        lower = Fraction(-1) + index * step
        upper = lower + step
        bound = local_integration_remainder_a(
            candidate_a,
            scale_bits=scale_bits,
            live_max=live_max,
            log_a=log_a,
            state=state,
            innovation=InnovationInterval(
                fraction_to_arb(lower), fraction_to_arb(upper), 0
            ),
            taylor_order=taylor_order,
        )
        leaves.append((lower, upper, 0, bound))

    target = fraction_to_arb(integration_target)
    split_history: list[dict[str, object]] = []
    while not sum((leaf[3] for leaf in leaves), arb(0)) < target:
        splittable = [leaf for leaf in leaves if leaf[2] < max_depth]
        if not splittable or len(leaves) >= max_intervals:
            break
        parent = max(
            splittable,
            key=lambda leaf: (float(leaf[3].upper()), -float(leaf[0])),
        )
        lower, upper, depth, parent_bound = parent
        midpoint = (lower + upper) / 2
        children = []
        for child_lower, child_upper in ((lower, midpoint), (midpoint, upper)):
            child_bound = local_integration_remainder_a(
                candidate_a,
                scale_bits=scale_bits,
                live_max=live_max,
                log_a=log_a,
                state=state,
                innovation=InnovationInterval(
                    fraction_to_arb(child_lower),
                    fraction_to_arb(child_upper),
                    depth + 1,
                ),
                taylor_order=taylor_order,
            )
            children.append((child_lower, child_upper, depth + 1, child_bound))
        child_sum = children[0][3] + children[1][3]
        if not child_sum < parent_bound:
            raise ArithmeticError("adaptive innovation split did not tighten")
        leaves.remove(parent)
        leaves.extend(children)
        split_history.append(
            {
                "parent_lower": [lower.numerator, lower.denominator],
                "parent_upper": [upper.numerator, upper.denominator],
                "parent_depth": depth,
                "parent_bound": parent_bound.str(40, radius=True),
                "child_sum": child_sum.str(40, radius=True),
            }
        )

    ordered = sorted(leaves, key=lambda leaf: leaf[0])
    innovations = [
        InnovationInterval(fraction_to_arb(lower), fraction_to_arb(upper), depth)
        for lower, upper, depth, _ in ordered
    ]
    integration = sum((leaf[3] for leaf in ordered), arb(0))
    model = matched_polynomial_residual_model_a(
        candidate_a,
        scale_bits=scale_bits,
        live_max=live_max,
        log_a=log_a,
        state=state,
        innovations=innovations,
        taylor_order=taylor_order,
    )
    plus_radius = (state.plus_upper - state.plus_lower) / arb(2)
    minus_radius = (state.minus_upper - state.minus_lower) / arb(2)
    polynomial, coefficients = bernstein_absolute_bound(
        model, plus_radius, minus_radius
    )
    direct, reward = static_state_remainder_a(
        candidate_a,
        scale_bits=scale_bits,
        live_max=live_max,
        log_a=log_a,
        state=state,
        taylor_order=taylor_order,
    )
    residual = polynomial + direct + reward + integration
    exact_cover = (
        ordered[0][0] == Fraction(-1)
        and ordered[-1][1] == Fraction(1)
        and all(left[1] == right[0] for left, right in zip(ordered, ordered[1:]))
    )
    result = {
        "status": "PATCH_CERTIFIED" if residual < fraction_to_arb(patch_target) else "PATCH_FAIL",
        "normalized_plus": [
            [normalized_plus[0].numerator, normalized_plus[0].denominator],
            [normalized_plus[1].numerator, normalized_plus[1].denominator],
        ],
        "normalized_minus": [
            [normalized_minus[0].numerator, normalized_minus[0].denominator],
            [normalized_minus[1].numerator, normalized_minus[1].denominator],
        ],
        "taylor_order": taylor_order,
        "initial_partitions": initial_partitions,
        "final_intervals": len(ordered),
        "split_count": len(split_history),
        "maximum_depth": max(leaf[2] for leaf in ordered),
        "polynomial_bernstein": polynomial.str(60, radius=True),
        "direct_remainder": direct.str(60, radius=True),
        "reward_remainder": reward.str(60, radius=True),
        "integration_remainder": integration.str(60, radius=True),
        "certified_residual_a": residual.str(60, radius=True),
        "bernstein_degree": [len(coefficients) - 1, len(coefficients[0]) - 1],
        "exact_innovation_cover": exact_cover,
        "sampled_grid_used": False,
        "trace_included": include_trace,
    }
    if include_trace:
        result["leaves"] = [
            {
                "lower": [lower.numerator, lower.denominator],
                "upper": [upper.numerator, upper.denominator],
                "depth": depth,
                "bound": bound.str(50, radius=True),
            }
            for lower, upper, depth, bound in ordered
        ]
        result["split_history"] = split_history
    return result


def certify_adaptive_patch_b(
    candidate_a: list[list[int]],
    candidate_b: list[list[int]],
    *,
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    normalized_plus: tuple[Fraction, Fraction],
    normalized_minus: tuple[Fraction, Fraction],
    taylor_order: int = 6,
    initial_partitions: int = 32,
    integration_target: Fraction = Fraction(4, 1_000),
    patch_target: Fraction = Fraction(5, 1_000),
    max_depth: int = 5,
    max_intervals: int = 256,
    include_trace: bool = True,
) -> dict[str, object]:
    """Certify one exact normalized state rectangle for the coupled b-residual."""

    state = Rectangle(
        live_max * fraction_to_arb(normalized_plus[0]),
        live_max * fraction_to_arb(normalized_plus[1]),
        live_max * fraction_to_arb(normalized_minus[0]),
        live_max * fraction_to_arb(normalized_minus[1]),
    )
    step = Fraction(2, initial_partitions)
    leaves: list[tuple[Fraction, Fraction, int, arb]] = []
    for index in range(initial_partitions):
        lower = Fraction(-1) + index * step
        upper = lower + step
        bound = local_integration_remainder_b(
            candidate_a,
            candidate_b,
            scale_bits=scale_bits,
            live_max=live_max,
            log_a=log_a,
            state=state,
            innovation=InnovationInterval(
                fraction_to_arb(lower), fraction_to_arb(upper), 0
            ),
            taylor_order=taylor_order,
        )
        leaves.append((lower, upper, 0, bound))

    target = fraction_to_arb(integration_target)
    split_history: list[dict[str, object]] = []
    while not sum((leaf[3] for leaf in leaves), arb(0)) < target:
        splittable = [leaf for leaf in leaves if leaf[2] < max_depth]
        if not splittable or len(leaves) >= max_intervals:
            break
        parent = max(
            splittable,
            key=lambda leaf: (float(leaf[3].upper()), -float(leaf[0])),
        )
        lower, upper, depth, parent_bound = parent
        midpoint = (lower + upper) / 2
        children = []
        for child_lower, child_upper in ((lower, midpoint), (midpoint, upper)):
            child_bound = local_integration_remainder_b(
                candidate_a,
                candidate_b,
                scale_bits=scale_bits,
                live_max=live_max,
                log_a=log_a,
                state=state,
                innovation=InnovationInterval(
                    fraction_to_arb(child_lower),
                    fraction_to_arb(child_upper),
                    depth + 1,
                ),
                taylor_order=taylor_order,
            )
            children.append((child_lower, child_upper, depth + 1, child_bound))
        child_sum = children[0][3] + children[1][3]
        if not child_sum < parent_bound:
            raise ArithmeticError("adaptive b innovation split did not tighten")
        leaves.remove(parent)
        leaves.extend(children)
        split_history.append(
            {
                "parent_lower": [lower.numerator, lower.denominator],
                "parent_upper": [upper.numerator, upper.denominator],
                "parent_depth": depth,
                "parent_bound": parent_bound.str(40, radius=True),
                "child_sum": child_sum.str(40, radius=True),
            }
        )

    ordered = sorted(leaves, key=lambda leaf: leaf[0])
    innovations = [
        InnovationInterval(fraction_to_arb(lower), fraction_to_arb(upper), depth)
        for lower, upper, depth, _ in ordered
    ]
    integration = sum((leaf[3] for leaf in ordered), arb(0))
    model = matched_polynomial_residual_model_b(
        candidate_a,
        candidate_b,
        scale_bits=scale_bits,
        live_max=live_max,
        log_a=log_a,
        state=state,
        innovations=innovations,
        taylor_order=taylor_order,
    )
    plus_radius = (state.plus_upper - state.plus_lower) / arb(2)
    minus_radius = (state.minus_upper - state.minus_lower) / arb(2)
    polynomial, coefficients = bernstein_absolute_bound(
        model, plus_radius, minus_radius
    )
    direct = static_state_remainder_b(
        candidate_b,
        scale_bits=scale_bits,
        live_max=live_max,
        state=state,
        taylor_order=taylor_order,
    )
    residual = polynomial + direct + integration
    exact_cover = (
        ordered[0][0] == Fraction(-1)
        and ordered[-1][1] == Fraction(1)
        and all(left[1] == right[0] for left, right in zip(ordered, ordered[1:]))
    )
    result = {
        "status": (
            "PATCH_CERTIFIED"
            if residual < fraction_to_arb(patch_target)
            else "PATCH_FAIL"
        ),
        "normalized_plus": [
            [normalized_plus[0].numerator, normalized_plus[0].denominator],
            [normalized_plus[1].numerator, normalized_plus[1].denominator],
        ],
        "normalized_minus": [
            [normalized_minus[0].numerator, normalized_minus[0].denominator],
            [normalized_minus[1].numerator, normalized_minus[1].denominator],
        ],
        "taylor_order": taylor_order,
        "initial_partitions": initial_partitions,
        "final_intervals": len(ordered),
        "split_count": len(split_history),
        "maximum_depth": max(leaf[2] for leaf in ordered),
        "polynomial_bernstein": polynomial.str(60, radius=True),
        "direct_remainder": direct.str(60, radius=True),
        "reward_remainder": "0",
        "integration_remainder": integration.str(60, radius=True),
        "certified_residual_b": residual.str(60, radius=True),
        "bernstein_degree": [len(coefficients) - 1, len(coefficients[0]) - 1],
        "exact_innovation_cover": exact_cover,
        "sampled_grid_used": False,
        "trace_included": include_trace,
    }
    if include_trace:
        result["leaves"] = [
            {
                "lower": [lower.numerator, lower.denominator],
                "upper": [upper.numerator, upper.denominator],
                "depth": depth,
                "bound": bound.str(50, radius=True),
            }
            for lower, upper, depth, bound in ordered
        ]
        result["split_history"] = split_history
    return result
