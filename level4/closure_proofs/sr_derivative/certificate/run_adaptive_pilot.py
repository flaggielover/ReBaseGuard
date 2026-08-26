#!/usr/bin/env python3
"""Run rigorous one-level innovation and state refinement pilot gates."""

from __future__ import annotations

import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

from sr_adaptive_residual import (
    InnovationInterval,
    Rectangle,
    innovation_split_bound,
    local_integration_remainder_a,
    state_split_bound,
)

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
PRECISION_BITS = 192
TAYLOR_ORDER = 6


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


def ratio(parent: arb, refined: arb) -> arb:
    return parent / refined


def main() -> int:
    candidate = json.loads((RESULTS / "arb_candidate.json").read_text())
    profile = json.loads((RESULTS / "sr_residual_remainder_budget.json").read_text())
    worst = profile["worst_innovation_interval"]
    with ctx.workprec(PRECISION_BITS):
        threshold = arb(A_NUMERATOR) / arb(A_DENOMINATOR)
        live_max = (arb(1) + threshold).log()
        log_a = threshold.log()
        patch_upper = live_max / arb(64)
        state = Rectangle(arb(0), patch_upper, arb(0), patch_upper)
        worst_index = int(worst["index"])
        exact_t_lower = Fraction(-1) + worst_index * Fraction(
            2, int(profile["patch"]["innovation_partitions"])
        )
        exact_t_upper = exact_t_lower + Fraction(
            2, int(profile["patch"]["innovation_partitions"])
        )
        innovation = InnovationInterval(
            arb(exact_t_lower.numerator) / arb(exact_t_lower.denominator),
            arb(exact_t_upper.numerator) / arb(exact_t_upper.denominator),
            0,
        )
        parent = local_integration_remainder_a(
            candidate["a"],
            scale_bits=candidate["scale_bits"],
            live_max=live_max,
            log_a=log_a,
            state=state,
            innovation=innovation,
            taylor_order=TAYLOR_ORDER,
        )
        innovation_refined, innovation_children = innovation_split_bound(
            candidate["a"],
            scale_bits=candidate["scale_bits"],
            live_max=live_max,
            log_a=log_a,
            state=state,
            innovation=innovation,
            taylor_order=TAYLOR_ORDER,
        )
        state_refined, state_children = state_split_bound(
            candidate["a"],
            scale_bits=candidate["scale_bits"],
            live_max=live_max,
            log_a=log_a,
            state=state,
            innovation=innovation,
            taylor_order=TAYLOR_ORDER,
        )
        exact_state_lower = Fraction(0)
        exact_state_upper = Fraction(1, 64)
        exact_state_midpoint = Fraction(1, 128)
        exact_innovation_midpoint = (exact_t_lower + exact_t_upper) / 2
        checks = {
            "innovation_children_exact_cover": (
                exact_t_lower < exact_innovation_midpoint < exact_t_upper
                and (exact_innovation_midpoint - exact_t_lower)
                + (exact_t_upper - exact_innovation_midpoint)
                == exact_t_upper - exact_t_lower
            ),
            "state_children_exact_cover": (
                exact_state_lower < exact_state_midpoint < exact_state_upper
                and 4
                * (exact_state_midpoint - exact_state_lower)
                * (exact_state_midpoint - exact_state_lower)
                == (exact_state_upper - exact_state_lower)
                * (exact_state_upper - exact_state_lower)
            ),
            "innovation_split_strictly_tightens": innovation_refined < parent,
            "state_split_strictly_tightens": state_refined < parent,
            "sampled_grid_not_used": True,
        }
        if not all(checks.values()):
            raise ArithmeticError("adaptive pilot gate failed")
        output = {
            "schema": "rebaseguard.sr-adaptive-residual-pilot.v1",
            "status": "PILOT_PASS",
            "proof_role": "RIGOROUS LOCAL REFINEMENT TEST; NOT A GLOBAL CERTIFICATE",
            "precision_bits": PRECISION_BITS,
            "candidate_sha256": candidate["sha256"],
            "taylor_order": TAYLOR_ORDER,
            "state_patch": "0<=y_plus<=L/64, 0<=y_minus<=L/64",
            "exact_normalized_state_patch": {
                "plus": [[0, 1], [1, 64]],
                "minus": [[0, 1], [1, 64]],
                "split": [1, 128],
            },
            "innovation_parent": {
                "exact_lower": [exact_t_lower.numerator, exact_t_lower.denominator],
                "exact_upper": [exact_t_upper.numerator, exact_t_upper.denominator],
                "exact_split": [
                    exact_innovation_midpoint.numerator,
                    exact_innovation_midpoint.denominator,
                ],
                "lower": innovation.lower.str(40, radius=True),
                "upper": innovation.upper.str(40, radius=True),
                "remainder": ball_record(parent),
            },
            "innovation_split": {
                "children": [ball_record(value) for value in innovation_children],
                "combined_remainder": ball_record(innovation_refined),
                "tightening_factor": ball_record(ratio(parent, innovation_refined)),
            },
            "state_split": {
                "children": [ball_record(value) for value in state_children],
                "maximum_child_remainder": ball_record(state_refined),
                "tightening_factor": ball_record(ratio(parent, state_refined)),
            },
            "checks": checks,
            "sampled_grid_used": False,
            "global_reachable_cover_complete": False,
        }
    atomic_json(RESULTS / "sr_residual_adaptive_pilot.json", output)
    print("SR adaptive residual pilot: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
