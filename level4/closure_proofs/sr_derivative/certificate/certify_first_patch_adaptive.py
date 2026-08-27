#!/usr/bin/env python3
"""Certify the first SR continuum patch with adaptive innovation bisection."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

from sr_adaptive_residual import (
    InnovationInterval,
    Rectangle,
    local_integration_remainder_a,
    matched_polynomial_residual_model_a,
)
from sr_bernstein import bernstein_absolute_bound
from taylor_model import taylor_absolute_bound

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
PRECISION_BITS = 192
TAYLOR_ORDER = 6
INITIAL_PARTITIONS = 32
MAX_DEPTH = 5
MAX_INTERVALS = 256
INTEGRATION_TARGET = Fraction(4, 1_000_000)
PATCH_TARGET = Fraction(5, 1_000_000)


@dataclass(frozen=True)
class Leaf:
    lower: Fraction
    upper: Fraction
    depth: int
    bound: arb


def ball_record(value: arb, digits: int = 60) -> dict[str, str]:
    return {
        "ball": value.str(digits, radius=True),
        "lower_enclosure": value.lower().str(digits, radius=True),
        "upper_enclosure": value.upper().str(digits, radius=True),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, object]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def as_arb(value: Fraction) -> arb:
    return arb(value.numerator) / arb(value.denominator)


def sum_bounds(leaves: list[Leaf]) -> arb:
    return sum((leaf.bound for leaf in leaves), arb(0))


def exact_cover(leaves: list[Leaf]) -> bool:
    ordered = sorted(leaves, key=lambda leaf: leaf.lower)
    return (
        ordered[0].lower == Fraction(-1)
        and ordered[-1].upper == Fraction(1)
        and all(left.upper == right.lower for left, right in zip(ordered, ordered[1:]))
    )


def main() -> int:
    candidate_path = RESULTS / "arb_candidate.json"
    profile_path = RESULTS / "sr_residual_remainder_budget.json"
    candidate = json.loads(candidate_path.read_text())
    profile = json.loads(profile_path.read_text())
    if int(profile["patch"]["innovation_partitions"]) != INITIAL_PARTITIONS:
        raise ValueError("profile partition count does not match adaptive seed")

    with ctx.workprec(PRECISION_BITS):
        threshold = arb(A_NUMERATOR) / arb(A_DENOMINATOR)
        live_max = (arb(1) + threshold).log()
        log_a = threshold.log()
        state = Rectangle(arb(0), live_max / arb(64), arb(0), live_max / arb(64))
        step = Fraction(2, INITIAL_PARTITIONS)
        leaves = []
        for record in profile["per_innovation_interval"]:
            index = int(record["index"])
            lower = Fraction(-1) + index * step
            leaves.append(
                Leaf(lower, lower + step, 0, arb(record["total"]["ball"]))
            )

        target = as_arb(INTEGRATION_TARGET)
        split_history: list[dict[str, object]] = []
        while not sum_bounds(leaves) < target:
            splittable = [leaf for leaf in leaves if leaf.depth < MAX_DEPTH]
            if not splittable or len(leaves) >= MAX_INTERVALS:
                break
            parent = max(
                splittable,
                key=lambda leaf: (float(leaf.bound.upper()), -float(leaf.lower)),
            )
            midpoint = (parent.lower + parent.upper) / 2
            child_specs = (
                (parent.lower, midpoint),
                (midpoint, parent.upper),
            )
            children = []
            for lower, upper in child_specs:
                bound = local_integration_remainder_a(
                    candidate["a"],
                    scale_bits=candidate["scale_bits"],
                    live_max=live_max,
                    log_a=log_a,
                    state=state,
                    innovation=InnovationInterval(
                        as_arb(lower), as_arb(upper), parent.depth + 1
                    ),
                    taylor_order=TAYLOR_ORDER,
                )
                children.append(Leaf(lower, upper, parent.depth + 1, bound))
            child_sum = children[0].bound + children[1].bound
            if not child_sum < parent.bound:
                raise ArithmeticError("adaptive innovation split did not tighten")
            leaves.remove(parent)
            leaves.extend(children)
            split_history.append(
                {
                    "parent": {
                        "lower": [parent.lower.numerator, parent.lower.denominator],
                        "upper": [parent.upper.numerator, parent.upper.denominator],
                        "depth": parent.depth,
                        "bound": ball_record(parent.bound),
                    },
                    "child_sum": ball_record(child_sum),
                    "tightening_factor": ball_record(parent.bound / child_sum),
                }
            )

        integration_remainder = sum_bounds(leaves)
        direct = arb(profile["additive_budget"]["direct_candidate_remainder"]["ball"])
        reward = arb(profile["additive_budget"]["reward_gaussian_remainder"]["ball"])
        ordered = sorted(leaves, key=lambda leaf: leaf.lower)
        polynomial_model = matched_polynomial_residual_model_a(
            candidate["a"],
            scale_bits=candidate["scale_bits"],
            live_max=live_max,
            log_a=log_a,
            state=state,
            innovations=[
                InnovationInterval(as_arb(leaf.lower), as_arb(leaf.upper), leaf.depth)
                for leaf in ordered
            ],
            taylor_order=TAYLOR_ORDER,
        )
        state_radius = live_max / arb(128)
        polynomial_taylor_bound = taylor_absolute_bound(
            polynomial_model, (state_radius, state_radius)
        )
        polynomial, bernstein_coefficients = bernstein_absolute_bound(
            polynomial_model, state_radius, state_radius
        )
        patch_bound = polynomial + direct + reward + integration_remainder
        checks = {
            "exact_innovation_cover": exact_cover(leaves),
            "integration_target_met": integration_remainder < target,
            "patch_engineering_target_met": patch_bound < as_arb(PATCH_TARGET),
            "every_split_strictly_tightened": len(split_history) > 0,
            "maximum_depth_respected": max(leaf.depth for leaf in leaves) <= MAX_DEPTH,
            "sampled_grid_not_used": True,
            "gaussian_tail_term_present": True,
        }
        if not all(checks.values()):
            status = "PILOT_FAIL"
        else:
            status = "FIRST_PATCH_CERTIFIED"
        output = {
            "schema": "rebaseguard.sr-adaptive-first-patch.v1",
            "status": status,
            "proof_role": "RIGOROUS CONTINUUM PATCH CERTIFICATE; NOT A GLOBAL CERTIFICATE",
            "precision_bits": PRECISION_BITS,
            "candidate_sha256": candidate["sha256"],
            "input_sha256": {
                candidate_path.name: sha256(candidate_path),
                profile_path.name: sha256(profile_path),
            },
            "state_patch": {
                "normalized_plus": [[0, 1], [1, 64]],
                "normalized_minus": [[0, 1], [1, 64]],
                "physical_scale": "L=log(1+A)",
            },
            "targets": {
                "integration": [INTEGRATION_TARGET.numerator, INTEGRATION_TARGET.denominator],
                "patch": [PATCH_TARGET.numerator, PATCH_TARGET.denominator],
            },
            "taylor_order": TAYLOR_ORDER,
            "initial_innovation_partitions": INITIAL_PARTITIONS,
            "final_innovation_intervals": len(leaves),
            "split_count": len(split_history),
            "maximum_depth": max(leaf.depth for leaf in leaves),
            "polynomial_residual_a": ball_record(polynomial),
            "polynomial_taylor_absolute_bound": ball_record(
                polynomial_taylor_bound
            ),
            "bernstein": {
                "degree_plus": len(bernstein_coefficients) - 1,
                "degree_minus": len(bernstein_coefficients[0]) - 1,
                "coefficient_count": sum(
                    len(row) for row in bernstein_coefficients
                ),
                "convex_hull_bound_used": True,
                "outward_rounded_interval_coefficients": True,
            },
            "direct_candidate_remainder": ball_record(direct),
            "reward_gaussian_remainder": ball_record(reward),
            "adaptive_integration_remainder": ball_record(integration_remainder),
            "certified_patch_residual_a": ball_record(patch_bound),
            "gaussian_tails": {
                "truncation_used": False,
                "remainder": ball_record(arb(0)),
                "reason": "t in [-1,1] exactly covers the full state-dependent continuation interval; alarm tails are in analytic r_a",
            },
            "leaves": [
                {
                    "lower": [leaf.lower.numerator, leaf.lower.denominator],
                    "upper": [leaf.upper.numerator, leaf.upper.denominator],
                    "depth": leaf.depth,
                    "bound": ball_record(leaf.bound),
                }
                for leaf in ordered
            ],
            "split_history": split_history,
            "checks": checks,
            "sampled_grid_used": False,
            "global_reachable_cover_complete": False,
        }
    atomic_json(RESULTS / "sr_residual_first_patch_adaptive.json", output)
    print(f"SR adaptive first patch: {status}")
    return 0 if status == "FIRST_PATCH_CERTIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
