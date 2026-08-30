from __future__ import annotations

import numpy as np

from rebaseguard_mgt1_priority1.cusum import window_terms


def test_random_denominator_decomposition_short_equal_long() -> None:
    paths = [np.array([3.0]), np.array([1.0, 2.0]), np.array([1.0, 2.0, 3.0])]
    terms = window_terms(paths, np.array([2]))
    assert np.array_equal(terms["tau"], [1, 2, 3])
    assert np.allclose(terms["direct"], terms["fixed"] + terms["correction"])
    assert terms["correction"][0, 0] == 4.5
    assert terms["correction"][1, 0] == 0.0
    assert terms["correction"][2, 0] == 0.0
    assert terms["window"][0, 0] == 3.0
    assert terms["window"][1, 0] == 1.5
    assert terms["window"][2, 0] == 2.5


def test_m_one_is_terminal_increment() -> None:
    paths = [np.array([1.0, -2.0, 4.0]), np.array([-3.0])]
    terms = window_terms(paths, np.array([1]))
    assert np.array_equal(terms["window"][:, 0], [4.0, -3.0])
    assert np.array_equal(terms["correction"][:, 0], [0.0, 0.0])


def test_required_m_two_three_five_forced_short_paths() -> None:
    terms = window_terms([np.array([2.0])], np.array([2, 3, 5]))
    assert np.array_equal(terms["window"][0], [2.0, 2.0, 2.0])
    assert np.all(terms["correction"][0] > 0)
    assert np.allclose(terms["direct"], terms["fixed"] + terms["correction"])
