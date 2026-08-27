#!/usr/bin/env python3
"""Profile the rigorous SR first-patch Taylor remainder by proof channel."""

from __future__ import annotations

import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path

from flint import arb, ctx

from sr_residual_taylor import (
    _integrand_a,
    _reward_a,
    _state_candidate_a,
)
from taylor_model import Model, evaluate_candidate, gaussian_density, softplus

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
PRECISION_BITS = 192
TAYLOR_ORDER = 6
INNOVATION_PARTITIONS = 32


def ball_record(value: arb, digits: int = 60) -> dict[str, str]:
    return {
        "ball": value.str(digits, radius=True),
        "lower_enclosure": value.lower().str(digits, radius=True),
        "upper_enclosure": value.upper().str(digits, radius=True),
    }


def atomic_json(path: Path, value: dict[str, object]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def classify(exponent: tuple[int, ...]) -> str:
    plus, minus, innovation = exponent
    if innovation and not plus and not minus:
        return "innovation_width_only"
    if plus and not minus and not innovation:
        return "y_plus_width_only"
    if minus and not plus and not innovation:
        return "y_minus_width_only"
    if not innovation:
        return "mixed_state_width"
    return "mixed_state_innovation"


def contribution(
    coefficient: arb,
    exponent: tuple[int, ...],
    radii: tuple[arb, ...],
    integration_width: arb = arb(1),
) -> tuple[arb, arb]:
    monomial = integration_width
    for radius, power in zip(radii, exponent, strict=True):
        monomial *= radius**power
    midpoint = coefficient.mid().abs_upper() * monomial
    dependency = coefficient.rad().upper() * monomial
    return midpoint, dependency


def transition_factors(
    candidate_a: list[list[int]],
    scale_bits: int,
    live_max: arb,
    log_a: arb,
    y_plus: Model,
    y_minus: Model,
    t: Model,
) -> tuple[Model, Model, Model, Model]:
    variables = y_plus.variables
    order = y_plus.order
    half = arb(1) / arb(2)
    midpoint = (y_minus - y_plus).scale(half)
    half_width = Model.constant(log_a + half, variables, order) - (
        y_plus + y_minus
    ).scale(half)
    z = midpoint + half_width * t
    q_plus = softplus(
        y_plus + z - Model.constant(half, variables, order)
    )
    q_minus = softplus(
        y_minus - z - Model.constant(half, variables, order)
    )
    composed = half_width * evaluate_candidate(
        candidate_a, scale_bits, live_max, q_plus, q_minus
    )
    return q_plus, q_minus, composed, gaussian_density(z)


def degree_remainder(
    model: Model, radii: tuple[arb, ...], integration_width: arb = arb(1)
) -> arb:
    total = arb(0)
    for exponent, coefficient in model.coefficients.items():
        if sum(exponent) == model.order:
            midpoint, dependency = contribution(
                coefficient, exponent, radii, integration_width
            )
            total += midpoint + dependency
    return total


def main() -> int:
    candidate = json.loads((RESULTS / "arb_candidate.json").read_text())
    with ctx.workprec(PRECISION_BITS):
        threshold = arb(A_NUMERATOR) / arb(A_DENOMINATOR)
        live_max = (arb(1) + threshold).log()
        log_a = threshold.log()
        patch_upper = live_max / arb(64)
        radius_state = patch_upper / arb(2)
        state_interval = arb(0).union(patch_upper)
        remainder_order = TAYLOR_ORDER + 1

        yp2 = Model.variable(state_interval, 0, 2, remainder_order)
        ym2 = Model.variable(state_interval, 1, 2, remainder_order)
        direct_candidate = _state_candidate_a(
            candidate["a"], candidate["scale_bits"], live_max, yp2, ym2
        )
        reward = _reward_a(log_a, yp2, ym2)
        direct_remainder = degree_remainder(
            direct_candidate, (radius_state, radius_state)
        )
        reward_remainder = degree_remainder(
            reward, (radius_state, radius_state)
        )

        additive_midpoint: dict[str, arb] = defaultdict(lambda: arb(0))
        additive_dependency: dict[str, arb] = defaultdict(lambda: arb(0))
        per_interval: list[dict[str, object]] = []
        factor_totals = {
            "softplus_q_plus": arb(0),
            "softplus_q_minus": arb(0),
            "candidate_composition": arb(0),
            "gaussian_density": arb(0),
        }
        t_step = arb(2) / arb(INNOVATION_PARTITIONS)
        for index in range(INNOVATION_PARTITIONS):
            t_lower = -arb(1) + arb(index) * t_step
            t_upper = t_lower + t_step
            t_radius = t_step / arb(2)
            t_interval = t_lower.union(t_upper)
            yp = Model.variable(state_interval, 0, 3, remainder_order)
            ym = Model.variable(state_interval, 1, 3, remainder_order)
            t = Model.variable(t_interval, 2, 3, remainder_order)
            integrand = _integrand_a(
                candidate["a"],
                candidate["scale_bits"],
                live_max,
                log_a,
                yp,
                ym,
                t,
            )
            interval_total = arb(0)
            interval_channels: dict[str, arb] = defaultdict(lambda: arb(0))
            radii = (radius_state, radius_state, t_radius)
            integration_width = arb(2) * t_radius
            for exponent, coefficient in integrand.coefficients.items():
                if sum(exponent) != remainder_order:
                    continue
                midpoint, dependency = contribution(
                    coefficient, exponent, radii, integration_width
                )
                channel = classify(exponent)
                additive_midpoint[channel] += midpoint
                additive_dependency[channel] += dependency
                interval_channels[channel] += midpoint + dependency
                interval_total += midpoint + dependency

            q_plus, q_minus, composed, density = transition_factors(
                candidate["a"],
                candidate["scale_bits"],
                live_max,
                log_a,
                yp,
                ym,
                t,
            )
            for name, model in (
                ("softplus_q_plus", q_plus),
                ("softplus_q_minus", q_minus),
                ("candidate_composition", composed),
                ("gaussian_density", density),
            ):
                factor_totals[name] += degree_remainder(
                    model, radii, integration_width
                )
            per_interval.append(
                {
                    "index": index,
                    "t_lower": t_lower.str(30, radius=True),
                    "t_upper": t_upper.str(30, radius=True),
                    "total": ball_record(interval_total),
                    "channels": {
                        name: ball_record(value)
                        for name, value in sorted(interval_channels.items())
                    },
                }
            )

        channels = {}
        integration_remainder = arb(0)
        dependency_total = arb(0)
        for name in sorted(set(additive_midpoint) | set(additive_dependency)):
            midpoint = additive_midpoint[name]
            dependency = additive_dependency[name]
            upper = midpoint + dependency
            integration_remainder += upper
            dependency_total += dependency
            channels[name] = {
                "midpoint_magnitude": ball_record(midpoint),
                "interval_dependency_slack": ball_record(dependency),
                "rigorous_upper": ball_record(upper),
            }

        total_remainder = direct_remainder + reward_remainder + integration_remainder
        worst_interval = max(
            per_interval,
            key=lambda item: float(arb(item["total"]["ball"]).upper()),
        )
        output = {
            "schema": "rebaseguard.sr-residual-remainder-budget.v1",
            "status": "PROFILED_OPEN",
            "proof_role": "RIGOROUS ADDITIVE REMAINDER DECOMPOSITION; NOT A GLOBAL CERTIFICATE",
            "precision_bits": PRECISION_BITS,
            "candidate_sha256": candidate["sha256"],
            "patch": {
                "domain": "0<=y_plus<=L/64, 0<=y_minus<=L/64",
                "taylor_order": TAYLOR_ORDER,
                "remainder_order": remainder_order,
                "innovation_partitions": INNOVATION_PARTITIONS,
            },
            "additive_budget": {
                "direct_candidate_remainder": ball_record(direct_remainder),
                "reward_gaussian_remainder": ball_record(reward_remainder),
                "integration_channels": channels,
                "integration_remainder": ball_record(integration_remainder),
                "interval_dependency_slack_total": ball_record(dependency_total),
                "tail_truncation": "none; t in [-1,1] maps the full continuation interval",
                "tail_remainder": ball_record(arb(0)),
                "bernstein_slack": "not yet used",
                "bernstein_remainder": ball_record(arb(0)),
                "total_taylor_remainder": ball_record(total_remainder),
            },
            "factor_diagnostics": {
                "role": "rigorous non-additive sensitivity indicators; not summed into the proof budget",
                **{
                    name: ball_record(value)
                    for name, value in factor_totals.items()
                },
            },
            "per_innovation_interval": per_interval,
            "worst_innovation_interval": worst_interval,
            "reachable_geometry": {
                "first_patch_is_a_safe_rectangular_over_enclosure": True,
                "geometry_slack_not_numerically_separable": True,
                "global_reachable_cover_complete": False,
            },
            "sampled_grid_used": False,
        }
    atomic_json(RESULTS / "sr_residual_remainder_budget.json", output)
    print("SR continuum Taylor remainder: PROFILED_OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
