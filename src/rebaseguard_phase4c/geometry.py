"""Analytic reachable enclosure for the frozen SR live state."""

from __future__ import annotations

import math

from rebaseguard_phase4c.operator import LIVE_Y_MAX, THRESHOLD_A, transition


A = THRESHOLD_A
E = math.e
EXP_SUM_CAP = (A + 1.0) / (1.0 - (A + 1.0) / (E * A))
SUM_CAP = math.log(EXP_SUM_CAP)
PRODUCT_MIN = math.exp(-1.0)
PRODUCT_MAX = EXP_SUM_CAP / E
COORDINATE_MIN = math.log1p(PRODUCT_MIN / A)
MIN_CONTINUATION_WIDTH = 2.0 * math.log(A) + 1.0 - SUM_CAP


def r_coordinates(y_plus: float, y_minus: float) -> tuple[float, float]:
    return math.expm1(y_plus), math.expm1(y_minus)


def in_reachable_enclosure(
    y_plus: float, y_minus: float, *, tolerance: float = 2e-12
) -> bool:
    """Test the closed analytic enclosure, with the reset state added separately."""

    if abs(y_plus) <= tolerance and abs(y_minus) <= tolerance:
        return True
    if not (
        COORDINATE_MIN - tolerance <= y_plus <= LIVE_Y_MAX + tolerance
        and COORDINATE_MIN - tolerance <= y_minus <= LIVE_Y_MAX + tolerance
        and y_plus + y_minus <= SUM_CAP + tolerance
    ):
        return False
    r_plus, r_minus = r_coordinates(y_plus, y_minus)
    product = r_plus * r_minus
    return PRODUCT_MIN - tolerance <= product <= PRODUCT_MAX + tolerance


def transition_product_identity(
    y_plus: float, y_minus: float, z: float
) -> tuple[float, float]:
    """Return both sides of ``R'_+ R'_- = exp(y_+ + y_- - 1)``."""

    q_plus, q_minus = transition(y_plus, y_minus, z)
    return math.expm1(q_plus) * math.expm1(q_minus), math.exp(
        y_plus + y_minus - 1.0
    )

