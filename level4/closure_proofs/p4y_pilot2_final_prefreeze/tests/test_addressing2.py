"""Collision-free logical addressing -- brief sections 19-21.

Pilot-1 found that the inherited ``SEED_BASE + sha256(...) % 9973`` scheme
collides at pilot replication counts, and that two colliding addresses replay
the SAME blocks.  Pilot-2 must not carry any modulo compression forward, and
must prove injectivity over the whole frozen domain rather than sample it.
"""

import inspect

import pytest

from p4y_pilot2 import addressing as A
from p4y_pilot2.strata import (
    CELL_STRATA, CELLS, R_DESIGN, R_VALIDATION, STRATA, VALIDATION_BASE,
    reachable_addresses,
)


def test_the_whole_frozen_domain_is_enumerated_and_collision_free():
    """Section 20: #addresses == #unique addresses, over the real domain."""
    domain = reachable_addresses()
    result = A.audit_reachable_domain(domain)
    assert result["addresses"] == len(domain)
    assert result["addresses"] == result["unique_seeds"], result["collisions"]
    assert result["collision_free"]
    assert result["addresses"] > 1_000, "the audit must not be trivially small"


def test_injectivity_holds_far_beyond_the_frozen_domain():
    """A margin check: 200 replicates per (cell, stratum, namespace)."""
    result = A.audit_injectivity(200)
    assert result["collision_free"]
    assert result["addresses"] == result["unique_seeds"]


def test_bounds_make_collisions_impossible_by_construction():
    assert A.bounds_are_injective_by_construction()
    assert A.MAX_REPLICATES <= A.NAMESPACE_STRIDE
    assert A.MAX_NAMESPACES * A.NAMESPACE_STRIDE <= A.STRATUM_STRIDE
    assert A.MAX_STRATA * A.STRATUM_STRIDE <= A.CELL_STRIDE


def test_no_modulo_compression_anywhere_in_the_seed_path():
    src = inspect.getsource(A.seed)
    assert "%" not in src, "modulo compression is not permitted (section 19)"
    assert "hash" not in src.lower()


def test_seed_is_keyed_by_logical_identity_not_by_execution():
    params = list(inspect.signature(A.seed).parameters)
    assert params == ["cell", "stratum", "namespace", "replicate"]
    for banned in ("worker", "worker_id", "pid", "process", "shard",
                   "schedule", "order", "k", "workers"):
        assert banned not in params


def test_design_and_validation_replicate_ranges_are_disjoint():
    assert VALIDATION_BASE >= R_DESIGN
    design = set(range(0, R_DESIGN))
    validation = set(range(VALIDATION_BASE, VALIDATION_BASE + R_VALIDATION))
    assert not (design & validation)


def test_pilot2_seeds_cannot_collide_with_any_earlier_campaign():
    """P4 frozen 401xxxx, P4X R0 411xxxx, P4X production 421xxxx, Pilot-1 4.31e9."""
    lo = min(a.seed for a in reachable_addresses())
    hi = max(a.seed for a in reachable_addresses())
    assert lo == A.CAMPAIGN_BASE == 6_310_000_000
    # above Pilot-1's THEORETICAL ceiling, not merely its observed maximum
    assert lo >= A.PILOT1_CEILING + 1_000_000_000
    assert hi < A.CAMPAIGN_BASE + A.MAX_CELLS * A.CELL_STRIDE
    for base in (4_010_000, 4_110_000, 4_210_000):
        assert base + 1_000_000 < lo


def test_unregistered_addresses_cannot_draw_blocks():
    with pytest.raises(A.AddressError):
        A.seed("not-a-cell", "T1", "design", 0)
    with pytest.raises(A.AddressError):
        A.seed("H", "not-a-stratum", "design", 0)
    with pytest.raises(A.AddressError):
        A.seed("H", "T1", "not-a-namespace", 0)
    with pytest.raises(A.AddressError):
        A.seed("H", "T1", "design", -1)


def test_the_address_table_is_frozen_against_reindexing():
    with pytest.raises(A.AddressError):
        A.register({"H": 17}, {})
    with pytest.raises(A.AddressError):
        A.register({"brand-new": 0}, {})


def test_every_frozen_cell_and_stratum_has_an_address():
    for name in CELLS:
        for sk in CELL_STRATA[name]:
            assert isinstance(A.seed(name, sk, "validation", 0), int)
    assert set(A.STRATUM_INDEX) == {s.key for s in STRATA}
