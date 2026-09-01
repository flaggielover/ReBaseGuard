"""Tuning, evaluation and replay streams must be disjoint (I5 / F9)."""
import numpy as np
import pytest

from rebaseguard_p6 import SEED_FAMILIES
from rebaseguard_p6.seeds import assert_disjoint, generator, seed_sequence

CELL = dict(detector="cusum", m=3, policy_id="const(rho=0.2,m=3)", cell_tag="pilot")


def test_families_are_disjoint():
    assert_disjoint(**CELL)


def test_same_key_is_reproducible():
    a = generator(family="eval", **CELL).standard_normal(16)
    b = generator(family="eval", **CELL).standard_normal(16)
    assert np.array_equal(a, b)


def test_distinct_policies_get_distinct_streams():
    a = generator(family="eval", **CELL).standard_normal(8)
    b = generator(family="eval", **{**CELL, "policy_id": "other"}).standard_normal(8)
    assert not np.array_equal(a, b)


def test_unknown_family_is_refused():
    with pytest.raises(ValueError):
        seed_sequence(family="production", **CELL)


def test_all_families_are_covered():
    assert set(SEED_FAMILIES) == {"tune", "eval", "replay"}
