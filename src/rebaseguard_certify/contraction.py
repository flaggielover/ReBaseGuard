"""Rigorous continuum block contraction for the exact killed kernel."""

from __future__ import annotations

from flint import arb, arb_mat

from rebaseguard_certify.arb_backend import ball_record, gaussian_cdf, rational, workprec


def certify_block_contraction(*, n: int = 7, bits: int = 192) -> dict[str, object]:
    if n < 1:
        raise ValueError("block length must be positive")
    with workprec(bits):
        h = rational(5)
        k = rational(1, 2)
        threshold = h + arb(n) * k
        standardized_erfc_argument = threshold / (arb(2 * n)).sqrt()
        # Since G_n/sqrt(n) is standard normal, the union of the two disjoint
        # forcing tails has probability erfc((h+n*k)/sqrt(2*n)).
        q_n = standardized_erfc_argument.erfc()
        beta_n = arb(1) - q_n
        resolvent_bound = arb(n) / q_n
        if not q_n > 0:
            raise ArithmeticError("Arb failed to prove q_n > 0")
        if not beta_n < 1:
            raise ArithmeticError("Arb failed to prove beta_n < 1")
        if not resolvent_bound > 0:
            raise ArithmeticError("invalid resolvent bound")
        return {
            "schema": "rebaseguard.block-contraction.v1",
            "scope": "entire reachable continuum",
            "method": "Gaussian block-sum forcing event",
            "precision_bits": bits,
            "model": {"k_num": 1, "k_den": 2, "h_num": 5, "h_den": 1},
            "n": n,
            "q_n": ball_record(q_n),
            "beta_n": ball_record(beta_n),
            "resolvent_bound": ball_record(resolvent_bound),
            "derivation": {
                "sampled_grid_used": False,
                "forcing_threshold": "h+n*k",
                "events": ["G_n >= h+n*k", "G_n <= -(h+n*k)"],
                "operator_statement": "sup_s K^n 1(s) <= 1-q_n",
                "resolvent_statement": "||(I-K)^-1||_inf <= n/(1-beta_n)=n/q_n",
            },
        }


def certify_monotone_block_contraction(
    *,
    n: int = 250,
    cells: int = 100,
    q_safe_num: int = 19,
    q_safe_den: int = 100,
    bits: int = 192,
) -> dict[str, object]:
    """Certify a sharper continuum contraction with a monotone 1D minorant.

    The grid is not treated as a sampled approximation. Values at left cell
    endpoints induce a step-function lower envelope because the one-sided
    hitting probability is increasing in its starting CUSUM state.
    """

    if n < 1 or cells < 2:
        raise ValueError("invalid contraction discretization")
    with workprec(bits):
        h = rational(5)
        k = rational(1, 2)
        spacing = h / arb(cells)
        transition = arb_mat(cells, cells)
        reward = arb_mat(cells, 1)
        one = arb(1)
        for i in range(cells):
            state = h * arb(i) / arb(cells)
            # Cell zero includes both the reset atom and destinations [0,dx).
            transition[i, 0] = gaussian_cdf(spacing + k - state)
            for j in range(1, cells):
                lower = h * arb(j) / arb(cells) + k - state
                upper = h * arb(j + 1) / arb(cells) + k - state
                transition[i, j] = gaussian_cdf(upper) - gaussian_cdf(lower)
            alarm_threshold = h + k - state
            reward[i, 0] = (alarm_threshold / arb(2).sqrt()).erfc() / arb(2)
            row_total = reward[i, 0]
            for j in range(cells):
                row_total += transition[i, j]
            if not row_total.contains(one):
                raise ArithmeticError(f"row {i} failed probability mass balance")

        values = arb_mat(cells, 1)
        for _ in range(n):
            values = reward + transition * values
        computed_lower = values[0, 0]
        q_safe = rational(q_safe_num, q_safe_den)
        if not computed_lower > q_safe:
            raise ArithmeticError("Arb did not prove the declared safe hitting lower bound")
        beta = one - q_safe
        resolvent_bound = arb(n) / q_safe
        if not beta < 1:
            raise ArithmeticError("failed to prove strict block contraction")
        return {
            "schema": "rebaseguard.monotone-block-contraction.v1",
            "scope": "entire reachable continuum",
            "method": "one-sided monotone Bellman lower envelope",
            "precision_bits": bits,
            "model": {"k_num": 1, "k_den": 2, "h_num": 5, "h_den": 1},
            "n": n,
            "cells": cells,
            "q_safe": {
                "numerator": q_safe_num,
                "denominator": q_safe_den,
                **ball_record(q_safe),
            },
            "computed_one_sided_hit_lower_enclosure": ball_record(computed_lower),
            "beta_n": ball_record(beta),
            "resolvent_bound": ball_record(resolvent_bound),
            "mass_balance": "every Arb row enclosure contains 1",
            "continuum_argument": {
                "sampled_grid_used": False,
                "monotonicity_envelope": True,
                "one_sided_state_monotonicity": "H_t(x) is nondecreasing in x by pathwise coupling",
                "cell_rule": "H_t(y) >= lower[j] for y in [edge_j,edge_(j+1))",
                "two_sided_domination": "one-sided upper crossing forces two-sided absorption",
                "operator_statement": "sup_s K^n 1(s) <= 1-q_safe",
                "resolvent_statement": "||(I-K)^-1||_inf <= n/q_safe",
            },
        }
