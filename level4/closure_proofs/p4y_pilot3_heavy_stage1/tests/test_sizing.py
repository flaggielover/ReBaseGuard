"""Stage-1 sizing: the inherited law, one rounding, and the UCB substitution."""

import math

import pytest

from p4y_pilot3.sizing import coverage, size_stage1
from p4y_pilot3.strata3 import KAPPA_K1, KAPPA_K2

KW = dict(target=0.01, min_blocks=8, abs_ceiling=10 ** 9)


def test_sizing_is_the_inherited_law():
    s = size_stage1(b_ref=32, relse_point=0.05, relse_upper=0.05,
                    kappa=0.5, **KW)
    assert s.b1 == math.ceil(32 * (0.05 / 0.01) ** 2)
    s2 = size_stage1(b_ref=32, relse_point=0.05, relse_upper=0.05,
                     kappa=KAPPA_K2, **KW)
    assert s2.b1 == math.ceil(32 * (0.05 / 0.01) ** (1 / KAPPA_K2))


def test_rounding_happens_exactly_once_at_the_logical_total():
    """No per-shard rounding: one ceil, on the total block count."""
    s = size_stage1(b_ref=7, relse_point=0.0301, relse_upper=0.0301,
                    kappa=0.5, **KW)
    exact = 7 * (0.0301 / 0.01) ** 2
    assert s.b1 == math.ceil(exact)
    assert s.b1 - exact < 1.0


def test_the_upper_bound_never_allocates_less_than_the_point_estimate():
    for u in (0.05, 0.06, 0.08, 0.2):
        s = size_stage1(b_ref=32, relse_point=0.05, relse_upper=u,
                        kappa=0.5, **KW)
        assert s.b1 >= s.b1_point


def test_inflation_is_recorded_for_the_contrast():
    s = size_stage1(b_ref=32, relse_point=0.05, relse_upper=0.065,
                    kappa=0.5, **KW)
    assert s.inflation == pytest.approx(1.3)
    assert s.b1 == math.ceil(32 * 6.5 ** 2)
    assert s.b1_point == math.ceil(32 * 5.0 ** 2)
    assert s.b1 / s.b1_point == pytest.approx(1.3 ** 2, rel=0.01)


def test_kappa_k2_always_buys_at_least_as_much_as_k1():
    for u in (0.011, 0.02, 0.05):
        a = size_stage1(b_ref=32, relse_point=u, relse_upper=u,
                        kappa=KAPPA_K2, **KW).b1
        b = size_stage1(b_ref=32, relse_point=u, relse_upper=u,
                        kappa=KAPPA_K1, **KW).b1
        assert a >= b


def test_the_absolute_ceiling_refuses_rather_than_executes():
    s = size_stage1(b_ref=32, relse_point=0.05, relse_upper=5.0,
                    target=0.01, kappa=0.5, min_blocks=8, abs_ceiling=1000)
    assert s.refused
    assert s.b1 > 1000


def test_coverage_is_the_pilot2_failure_quantity():
    assert coverage(300, 215) is True
    assert coverage(214, 215) is False
    assert coverage(215, 215) is True


def test_a_degenerate_bound_is_refused_not_silently_shrunk():
    s = size_stage1(b_ref=32, relse_point=0.05, relse_upper=math.inf,
                    target=0.01, kappa=0.5, min_blocks=8, abs_ceiling=1000)
    assert s.refused
