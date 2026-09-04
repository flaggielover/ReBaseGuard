"""Shard-sum invariant, the 8801/5 regression, and shard-invariant identity.

Brief sections 17, 18 and 21.  The partition itself is inherited from Pilot-1
unchanged and imported read-only; these tests re-pin it in the Pilot-2
namespace so that a P4Y checkpoint drafted from Pilot-2 carries its own
evidence rather than a cross-reference.
"""

import pytest

from p4y_pilot.blocks import Cell, block_value, summarise
from p4y_pilot.shard import (
    Allocation, ShardInvariantError, block_ids, p4x_defective_partition,
    partition, verify,
)
from p4y_pilot2.addressing import seed
from p4y_pilot2.strata import CELL_STRATA, CELLS, STRATA, cap_blocks

K_VALUES = [1, 2, 5, 7, 13, 64]
P4X_B, P4X_K, P4X_BLOCK = 8_801, 5, 250_000


# ----------------------------------------------------- section 17 invariants
@pytest.mark.parametrize("k", K_VALUES)
@pytest.mark.parametrize("b", [0, 1, 7, 48, 215, 300, 1784, 8_801, 100_000,
                               2_200_168_765])
def test_sum_is_exact_and_balanced(b, k):
    sizes = partition(b, k)
    assert sum(sizes) == b
    assert max(sizes) - min(sizes) <= 1
    assert len(sizes) == k


@pytest.mark.parametrize("k", K_VALUES)
@pytest.mark.parametrize("b", [0, 1, 7, 48, 215, 300, 1784, 8_801])
def test_executed_equals_requested_blocks_and_paths(b, k):
    a = Allocation(total_blocks=b, block_size=250_000, workers=k).audit()
    assert a["executed_blocks"] == b
    assert a["delta_blocks"] == 0
    assert a["executed_paths"] == b * 250_000
    assert a["delta_paths"] == 0
    assert a["block_ids_tile_the_global_range"]


def test_no_independent_per_shard_rounding_occurs():
    """Section 17: rounding per shard is what produced the P4X over-run."""
    import math

    for b, k in ((8_801, 5), (1784, 5), (215, 7), (300, 13)):
        exact = partition(b, k)
        rounded = [math.ceil(b / k)] * k
        assert sum(exact) == b
        if b % k:
            assert sum(rounded) > b
            assert exact != rounded


# ------------------------------------------------------- section 18 regression
def test_historical_8801_block_regression():
    sizes = partition(P4X_B, P4X_K)
    assert sum(sizes) == 8_801
    assert sum(sizes) != 8_805
    assert sorted(sizes) == [1760, 1760, 1760, 1760, 1761]
    a = Allocation(total_blocks=P4X_B, block_size=P4X_BLOCK,
                   workers=P4X_K).audit()
    assert a["executed_blocks"] == 8_801
    assert a["executed_paths"] == 2_200_250_000
    assert a["delta_blocks"] == 0 and a["delta_paths"] == 0


def test_the_defective_historical_implementation_is_pinned():
    bad = p4x_defective_partition(P4X_B, P4X_K)
    assert bad == [1761] * 5
    assert sum(bad) == 8_805
    assert sum(bad) * P4X_BLOCK == 2_201_250_000
    assert sum(bad) - P4X_B == 4
    assert (sum(bad) - P4X_B) * P4X_BLOCK == 1_000_000


def test_one_extra_or_missing_block_fails():
    with pytest.raises(ShardInvariantError):
        verify([1761] * 5, P4X_B)              # +4
    with pytest.raises(ShardInvariantError):
        verify([1760] * 5 + [0], P4X_B)        # -1
    with pytest.raises(ShardInvariantError):
        verify([1760, 1760, 1760, 1760, 1762], P4X_B)   # +1


# ------------------------------------------- section 21 shard-invariant identity
IDENT = Cell(key="ident2", layer="reduced", kind="cusum", threshold=2.0,
             family="t1p5", route="route_a", max_steps=60_000,
             block_size=2_000, heavy=True)
B = 12


def _run(k, stream):
    out = {}
    for shard in range(k):
        for bid in block_ids(B, k, shard):
            out[bid] = block_value(IDENT, stream, bid)
    return out


def test_the_logical_block_set_does_not_depend_on_k():
    for k in K_VALUES:
        seen = set()
        for shard in range(k):
            ids = set(block_ids(B, k, shard))
            assert not (seen & ids)
            seen |= ids
        assert seen == set(range(B))


def test_block_outputs_are_bit_identical_across_k():
    stream = seed("H", "T1", "validation", 0)
    ref = _run(1, stream)
    for k in K_VALUES:
        got = _run(k, stream)
        assert got.keys() == ref.keys()
        for bid, v in got.items():
            assert v == ref[bid], f"K={k} changed block {bid}"


@pytest.mark.parametrize("k", K_VALUES)
def test_pooled_summary_equals_the_unsharded_formula(k):
    stream = seed("H", "T1", "validation", 1)
    unsharded = [block_value(IDENT, stream, i)[1] for i in range(B)]
    sharded = _run(k, stream)
    pooled = [sharded[i][1] for i in range(B)]
    assert pooled == unsharded
    a, b = summarise(unsharded), summarise(pooled)
    assert (a["mean"], a["se"], a["blocks"]) == (b["mean"], b["se"], b["blocks"])


# ------------------------------------------------- the frozen caps are integers
def test_every_frozen_cap_is_an_integer_block_count():
    from p4y_pilot2.strata import CAP_MULTIPLIERS

    for s in STRATA:
        for m in CAP_MULTIPLIERS:
            cb = cap_blocks(s, m)
            assert isinstance(cb, int) and cb >= s.b1 * m - 1
            assert partition(cb, 5) and sum(partition(cb, 5)) == cb


def test_every_pilot2_cell_stratum_pair_has_a_frozen_cap():
    for name in CELLS:
        for sk in CELL_STRATA[name]:
            s = next(x for x in STRATA if x.key == sk)
            assert cap_blocks(s, 1.5) >= 1
