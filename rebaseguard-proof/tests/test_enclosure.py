from flint import arb

from rebaseguard_certify.arb_backend import ball_record
from rebaseguard_certify.enclosure import propagate_residual_enclosure


def test_residual_propagation_uses_declared_resolvent_formula():
    residual = {
        "delta_a": ball_record(arb("0.000001")),
        "delta_b": ball_record(arb("0.0001")),
        "b_hat_origin": ball_record(arb("15")),
    }
    contraction = {"n": 100, "q_safe": {"numerator": 1, "denominator": 2}}
    result = propagate_residual_enclosure(residual, contraction, bits=160)
    assert result["formula"]["E_a"] == "C*delta_a"
    assert result["formula"]["E_b"] == "C*(delta_b+mu*E_a)"
    assert arb(result["gamma"]["ball"]) > 2

