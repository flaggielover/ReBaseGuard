"""Rigorous prototype block contractions for the frozen SR killed kernel."""

from __future__ import annotations

from flint import arb, arb_mat

from rebaseguard_certify.arb_backend import (
    ball_record,
    gaussian_cdf,
    rational,
    workprec,
)


def certify_block_sum_forcing(*, n: int = 9, bits: int = 192) -> dict[str, object]:
    """Certify absorption from a two-sided extreme Gaussian block sum."""

    if n < 1:
        raise ValueError("n must be positive")
    with workprec(bits):
        log_a = rational(8325, 16).log()
        cutoff = (log_a + arb(n) / arb(2)) / arb(n).sqrt()
        q = (cutoff / arb(2).sqrt()).erfc()
        resolvent = arb(n) / q
        if not q > 0:
            raise ArithmeticError("failed to prove positive forcing probability")
        return {
            "method": "two-sided Gaussian block-sum forcing",
            "n": n,
            "q": ball_record(q),
            "beta": ball_record(arb(1) - q),
            "resolvent_bound": ball_record(resolvent),
            "operator_statement": "sup_y K^n 1(y) <= 1-q",
            "forcing_events": [
                "sum Z_i >= log(A)+n/2",
                "sum Z_i <= -log(A)-n/2",
            ],
        }


def certify_one_sided_monotone_minorant(
    *,
    n: int = 139,
    cells: int = 200,
    q_safe_num: int = 11,
    q_safe_den: int = 100,
    bits: int = 192,
) -> dict[str, object]:
    """Certify a uniform SR hit probability using one chart and monotonicity.

    Grid values are lower step envelopes, not samples: the finite-horizon
    one-sided hitting probability is nondecreasing in its starting SR state.
    """

    if n < 1 or cells < 2:
        raise ValueError("invalid contraction parameters")
    with workprec(bits):
        one = arb(1)
        half = rational(1, 2)
        a = rational(8325, 16)
        log_a = a.log()
        live_max = (one + a).log()
        edges = [live_max * arb(index) / arb(cells) for index in range(cells + 1)]
        transition = arb_mat(cells, cells)
        alarm = arb_mat(cells, 1)
        for i in range(cells):
            state = edges[i]
            first_upper = edges[1].expm1().log() - state + half
            transition[i, 0] = gaussian_cdf(first_upper)
            for j in range(1, cells):
                lower = edges[j].expm1().log() - state + half
                upper = edges[j + 1].expm1().log() - state + half
                transition[i, j] = gaussian_cdf(upper) - gaussian_cdf(lower)
            alarm_threshold = log_a - state + half
            alarm[i, 0] = one - gaussian_cdf(alarm_threshold)
            row_total = alarm[i, 0]
            for j in range(cells):
                row_total += transition[i, j]
            if not row_total.contains(one):
                raise ArithmeticError(f"probability mass check failed in row {i}")

        values = arb_mat(cells, 1)
        for _ in range(n):
            values = alarm + transition * values
        computed = values[0, 0]
        q_safe = rational(q_safe_num, q_safe_den)
        if not computed > q_safe:
            raise ArithmeticError("declared safe hit probability was not certified")
        resolvent = arb(n) / q_safe
        return {
            "method": "one-sided SR monotone Bellman lower envelope",
            "n": n,
            "cells": cells,
            "computed_hit_probability": ball_record(computed),
            "q_safe": {
                "numerator": q_safe_num,
                "denominator": q_safe_den,
                **ball_record(q_safe),
            },
            "beta": ball_record(one - q_safe),
            "resolvent_bound": ball_record(resolvent),
            "mass_balance": "every Arb transition-plus-alarm row contains 1",
            "continuum_argument": {
                "sampled_grid_used": False,
                "pathwise_monotonicity": (
                    "one-sided SR hitting probability is nondecreasing in R+"
                ),
                "cell_rule": (
                    "destination values use the left endpoint of each Y cell"
                ),
                "two_sided_domination": (
                    "a one-sided plus-chart hit forces symmetric two-chart absorption"
                ),
                "uniform_start": "all live plus-chart states dominate R+=0",
                "operator_statement": "sup_y K^n 1(y) <= 1-q_safe",
                "resolvent_statement": "||(I-K)^-1||_inf <= n/q_safe",
            },
        }


def run_contraction_prototypes(*, bits: int = 192) -> dict[str, object]:
    return {
        "schema": "rebaseguard.phase4c.contraction-prototype.v1",
        "proof_role": "RIGOROUS FEASIBILITY BOUNDS; NOT THE FINAL SR CERTIFICATE",
        "precision_bits": bits,
        "block_sum": certify_block_sum_forcing(bits=bits),
        "one_sided_monotone": certify_one_sided_monotone_minorant(bits=bits),
    }
