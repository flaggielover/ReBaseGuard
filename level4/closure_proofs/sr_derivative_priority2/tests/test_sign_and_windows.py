from __future__ import annotations

import math
import numpy as np
import pytest


def log_density_ratio(z: float, e: float) -> float:
    return -0.5 * (z + e) ** 2 + 0.5 * z ** 2


def window(path: list[float], m: int) -> tuple[float, float, float]:
    tau = len(path)
    total = sum(path)
    w = min(m, tau)
    suffix = sum(path[-w:])
    direct = suffix / w * total
    fixed = suffix / m * total
    correction = (1 / tau - 1 / m) * total**2 if tau < m else 0.0
    return direct, fixed, correction


def test_qe_likelihood_score_is_minus_stopped_sum() -> None:
    path = [0.4, -1.2, 0.7]
    total = sum(path)
    h = 1e-6
    plus = sum(log_density_ratio(z, h) for z in path)
    minus = sum(log_density_ratio(z, -h) for z in path)
    derivative = (plus - minus) / (2 * h)
    assert derivative == pytest.approx(-total, abs=1e-9)
    assert not math.isclose(derivative, total, abs_tol=1e-6)


@pytest.mark.parametrize("m", [1, 2, 3, 5])
def test_random_denominator_decomposition(m: int) -> None:
    for path in ([2.0], [1.0, -0.5], [0.2, 0.3, -0.1], [0.0] * 5 + [2.0]):
        direct, fixed, correction = window(list(path), m)
        assert direct == pytest.approx(fixed + correction)
        assert correction >= 0.0


def test_short_equal_and_long_branches() -> None:
    m = 3
    assert len([2.0]) < m
    assert len([0.0, 0.0, 2.0]) == m
    assert len([0.0, 0.0, 0.0, 2.0]) > m
    assert window([2.0], m)[0] == 4.0
    assert window([0.0, 0.0, 2.0], m)[2] == 0.0
    assert window([0.0, 0.0, 0.0, 2.0], m)[2] == 0.0
