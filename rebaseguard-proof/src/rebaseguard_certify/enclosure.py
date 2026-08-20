"""Propagate certified continuum residuals through the resolvent bound."""

from __future__ import annotations

from flint import arb

from rebaseguard_certify.arb_backend import ball_record, rational, workprec


def _stored_ball(record: dict[str, str]) -> arb:
    return arb(record["ball"])


def propagate_residual_enclosure(
    residual: dict[str, object], contraction: dict[str, object], *, bits: int = 256
) -> dict[str, object]:
    with workprec(bits):
        delta_a = _stored_ball(residual["delta_a"])
        delta_b = _stored_ball(residual["delta_b"])
        b_origin = _stored_ball(residual["b_hat_origin"])
        n = int(contraction["n"])
        q_safe_record = contraction["q_safe"]
        q_safe = rational(
            int(q_safe_record["numerator"]), int(q_safe_record["denominator"])
        )
        c_bound = arb(n) / q_safe
        mu = (arb(2) / arb.pi()).sqrt()
        e_a = c_bound.abs_upper() * delta_a.abs_upper()
        e_b = c_bound.abs_upper() * (
            delta_b.abs_upper() + mu.abs_upper() * e_a.abs_upper()
        )
        gamma = b_origin + arb(0, 1) * e_b.abs_upper()
        proof_pass = gamma > arb(2)
        return {
            "schema": "rebaseguard.residual-propagation.v1",
            "precision_bits": bits,
            "resolvent_bound": ball_record(c_bound),
            "mu": ball_record(mu),
            "E_a": ball_record(e_a),
            "E_b": ball_record(e_b),
            "gamma": ball_record(gamma),
            "gamma_lower_gt_2": proof_pass,
            "formula": {
                "E_a": "C*delta_a",
                "E_b": "C*(delta_b+mu*E_a)",
                "Gamma": "b_hat(0,0)+[-E_b,E_b]",
            },
        }
