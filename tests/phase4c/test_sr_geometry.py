from __future__ import annotations

import math

import numpy as np
import pytest

from rebaseguard_phase4c.geometry import (
    COORDINATE_MIN,
    EXP_SUM_CAP,
    MIN_CONTINUATION_WIDTH,
    PRODUCT_MAX,
    PRODUCT_MIN,
    SUM_CAP,
    in_reachable_enclosure,
    transition_product_identity,
)
from rebaseguard_phase4c.operator import (
    LIVE_Y_MAX,
    THRESHOLD_A,
    continuation_bounds,
    transition,
)


def test_sum_cap_is_exact_fixed_point_of_invariant_envelope_map():
    mapped = math.log(
        (1.0 + THRESHOLD_A)
        * (1.0 + math.exp(SUM_CAP - 1.0) / THRESHOLD_A)
    )
    assert mapped == pytest.approx(SUM_CAP)
    assert math.exp(SUM_CAP) == pytest.approx(EXP_SUM_CAP)
    assert math.exp(SUM_CAP - 1.0) == pytest.approx(PRODUCT_MAX)


@pytest.mark.parametrize("y_plus,y_minus,z", [(0.0, 0.0, 0.3), (2.0, 3.0, -1.4)])
def test_transition_product_identity_is_independent_of_innovation(y_plus, y_minus, z):
    actual, expected = transition_product_identity(y_plus, y_minus, z)
    assert actual == pytest.approx(expected)


def test_coordinate_floor_follows_from_product_floor_and_chart_cap():
    assert math.expm1(COORDINATE_MIN) * THRESHOLD_A == pytest.approx(PRODUCT_MIN)


def test_enclosure_is_much_smaller_than_naive_square():
    assert SUM_CAP < 1.08 * LIVE_Y_MAX
    assert SUM_CAP < 0.54 * (2.0 * LIVE_Y_MAX)
    assert PRODUCT_MAX < 0.002 * THRESHOLD_A**2
    assert MIN_CONTINUATION_WIDTH > 6.79


def test_reset_and_random_live_successors_are_in_enclosure():
    assert in_reachable_enclosure(0.0, 0.0)
    rng = np.random.default_rng(404)
    states = [(0.0, 0.0)]
    for _ in range(10_000):
        y_plus, y_minus = states[int(rng.integers(len(states)))]
        ell, upper = continuation_bounds(y_plus, y_minus)
        z = rng.uniform(ell + 1e-10, upper - 1e-10)
        successor = transition(y_plus, y_minus, z)
        assert in_reachable_enclosure(*successor)
        if len(states) < 500:
            states.append(successor)


def test_reflection_preserves_reachable_enclosure():
    points = [
        (COORDINATE_MIN, LIVE_Y_MAX),
        (0.5 * SUM_CAP, 0.5 * SUM_CAP),
        (1.0, 4.0),
    ]
    for y_plus, y_minus in points:
        assert in_reachable_enclosure(y_plus, y_minus) == in_reachable_enclosure(
            y_minus, y_plus
        )
