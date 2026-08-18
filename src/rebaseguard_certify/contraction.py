"""Rigorous continuum block contraction for the exact killed kernel."""

from __future__ import annotations

from flint import arb

from rebaseguard_certify.arb_backend import ball_record, rational, workprec


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
