import math

from scipy.integrate import quad

from rebaseguard_certify.equations import absorbing_rewards_float, apply_k_float
from rebaseguard_certify.model import State


def _phi(z: float) -> float:
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


def test_absorbing_rewards_match_direct_quadrature():
    state = State(1.25, 0.75)
    ra, rb = absorbing_rewards_float(state, 0.5, 5.0)
    ell, upper = -4.75, 4.25
    direct_a = quad(lambda z: z * _phi(z), -math.inf, ell)[0] + quad(
        lambda z: z * _phi(z), upper, math.inf
    )[0]
    direct_b = quad(lambda z: z * z * _phi(z), -math.inf, ell)[0] + quad(
        lambda z: z * z * _phi(z), upper, math.inf
    )[0]
    assert abs(ra - direct_a) < 1e-13
    assert abs(rb - direct_b) < 1e-13


def test_k_on_constant_is_continuation_probability():
    state = State(0.0, 0.0)
    value = apply_k_float(lambda _: 1.0, state, 0.5, 5.0)
    assert 0.9999999 < value < 1.0

