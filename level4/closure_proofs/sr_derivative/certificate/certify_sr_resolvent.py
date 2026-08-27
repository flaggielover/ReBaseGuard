#!/usr/bin/env python3
"""Rigorous block-resolvent certificate for the symmetric two-chart SR kernel.

The two-chart stopping time is no later than the hitting time of either one-sided
chart. We therefore lower-bound the probability that the plus chart hits A
within ``n`` steps, uniformly over every live two-chart state. In log-state
coordinates y=log(1+R), the one-sided transition

    y' = softplus(y + Z - 1/2)

is pathwise monotone in y. A finite partition of [0, log(1+A)) therefore gives
an analytic lower envelope, not a sampled approximation: values at each left
cell edge lower-bound the finite-horizon hitting probability throughout that
cell. All transition probabilities are enclosed with Arb.

If q_safe is certified below the n-step one-sided hit probability from y=0,
then for the exact killed two-chart kernel K

    sup_s K^n 1(s) <= 1-q_safe,
    ||(I-K)^-1||_inf <= n/q_safe.
"""

from __future__ import annotations

import json
import os
import platform
import tempfile
from pathlib import Path

import flint
from flint import arb, arb_mat, ctx

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"

A_NUMERATOR = 4581762885148045
A_DENOMINATOR = 8796093022208
N_STEPS = 250
CELLS = 200
Q_SAFE_NUMERATOR = 19
Q_SAFE_DENOMINATOR = 100
PRECISION_BITS = 192


def rational(numerator: int, denominator: int = 1) -> arb:
    return arb(numerator) / arb(denominator)


def gaussian_cdf(value: arb) -> arb:
    return (arb(1) + (value / arb(2).sqrt()).erf()) / arb(2)


def ball_record(value: arb, digits: int = 60) -> dict[str, str]:
    return {
        "ball": value.str(digits, radius=True),
        "lower_enclosure": value.lower().str(digits, radius=True),
        "upper_enclosure": value.upper().str(digits, radius=True),
    }


def atomic_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def certify() -> dict[str, object]:
    with ctx.workprec(PRECISION_BITS):
        one = arb(1)
        threshold = rational(A_NUMERATOR, A_DENOMINATOR)
        log_a = threshold.log()
        live_max = (one + threshold).log()
        spacing = live_max / arb(CELLS)

        transition = arb_mat(CELLS, CELLS)
        reward = arb_mat(CELLS, 1)

        for i in range(CELLS):
            # Left endpoint of source cell. Pathwise monotonicity implies this
            # gives the smallest n-step hit probability throughout the cell.
            y = live_max * arb(i) / arb(CELLS)

            # y' = softplus(y+z-1/2).  Destination y' in [a,b) is equivalent
            # to z in [log(expm1(a))-y+1/2, log(expm1(b))-y+1/2).
            # Cell 0 includes y'=0 only as a limit; its lower z endpoint is
            # -infinity, so its mass is just Phi(z_upper).
            upper_y = spacing
            upper_z = (upper_y.exp() - one).log() - y + rational(1, 2)
            transition[i, 0] = gaussian_cdf(upper_z)

            for j in range(1, CELLS):
                lower_y = live_max * arb(j) / arb(CELLS)
                upper_y = live_max * arb(j + 1) / arb(CELLS)
                lower_z = (lower_y.exp() - one).log() - y + rational(1, 2)
                upper_z = (upper_y.exp() - one).log() - y + rational(1, 2)
                transition[i, j] = gaussian_cdf(upper_z) - gaussian_cdf(lower_z)

            # Hitting R' >= A is y' >= log(1+A), equivalently
            # z >= log(A) - y + 1/2.
            alarm_z = log_a - y + rational(1, 2)
            reward[i, 0] = one - gaussian_cdf(alarm_z)

            row_total = reward[i, 0]
            for j in range(CELLS):
                row_total += transition[i, j]
            if not row_total.contains(one):
                raise ArithmeticError(f"row {i} failed probability mass balance")

        values = arb_mat(CELLS, 1)
        for _ in range(N_STEPS):
            values = reward + transition * values

        computed_lower = values[0, 0]
        q_safe = rational(Q_SAFE_NUMERATOR, Q_SAFE_DENOMINATOR)
        if not computed_lower > q_safe:
            raise ArithmeticError(
                "Arb did not certify the declared n-step hitting lower bound"
            )

        beta_n = one - q_safe
        resolvent_bound = arb(N_STEPS) / q_safe
        if not beta_n < one:
            raise ArithmeticError("strict block contraction was not certified")

        return {
            "schema": "rebaseguard.sr-monotone-block-contraction.v1",
            "status": "CERTIFIED_COMPONENT",
            "scope": "authoritative symmetric two-chart SR killed kernel",
            "precision_bits": PRECISION_BITS,
            "python_flint": flint.__version__,
            "python": platform.python_version(),
            "threshold": {
                "runtime_rational": [A_NUMERATOR, A_DENOMINATOR],
                "A": ball_record(threshold),
                "log_A": ball_record(log_a),
                "live_log_state_max": ball_record(live_max),
            },
            "n": N_STEPS,
            "cells": CELLS,
            "q_safe": {
                "numerator": Q_SAFE_NUMERATOR,
                "denominator": Q_SAFE_DENOMINATOR,
                **ball_record(q_safe),
            },
            "computed_one_sided_hit_lower_enclosure": ball_record(computed_lower),
            "beta_n": ball_record(beta_n),
            "resolvent_bound": ball_record(resolvent_bound),
            "proof": {
                "sampled_grid_used": False,
                "pathwise_monotonicity": (
                    "softplus(y+z-1/2) is increasing in y for every innovation z"
                ),
                "cell_rule": (
                    "finite-horizon hit probability on each source cell is bounded "
                    "below by the value at its exact left endpoint"
                ),
                "two_chart_domination": (
                    "a plus-chart hit forces absorption of the symmetric two-chart detector"
                ),
                "operator_statement": "sup_s K^n 1(s) <= 1-q_safe",
                "resolvent_statement": "||(I-K)^-1||_inf <= n/q_safe",
                "mass_balance": "every Arb row enclosure contains one",
            },
        }


def main() -> int:
    result = certify()
    atomic_json(RESULTS / "sr_monotone_contraction.json", result)
    print("SR monotone block contraction: CERTIFIED_COMPONENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
