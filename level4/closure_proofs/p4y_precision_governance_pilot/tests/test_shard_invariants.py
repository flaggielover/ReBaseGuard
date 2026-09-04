"""Exact shard-sum invariant -- the P4X G2 repair.

Every test here is about ONE number: the count of blocks actually executed
against the count of blocks frozen.  It must be equal, never merely close,
and never larger "because the shards had to be even".
"""

import math

import pytest

from p4y_pilot.shard import (
    Allocation,
    ShardInvariantError,
    block_ids,
    offsets,
    p4x_defective_partition,
    partition,
    verify,
)

#: The historical failure, verbatim.
P4X_B, P4X_K, P4X_BLOCK = 8_801, 5, 250_000


#: Cases small enough that the block-id set may be materialised.
SMALL_CASES = [
    (100, 5),        # B divisible by K
    (8_801, 5),      # B not divisible by K -- the historical case
    (3, 5),          # B < K
    (1, 1),
    (1, 5),          # B = 1 with idle workers
    (0, 4),          # degenerate empty allocation
]

#: Frozen totals of production size.  Nothing may enumerate these.
LARGE_CASES = [
    (2_200_168_765, 64),
    (10**12 + 1, 7),
    (8_801 * 250_000, 5),
]

CASES = SMALL_CASES + LARGE_CASES


@pytest.mark.parametrize("b,k", CASES)
def test_sum_is_exact(b, k):
    assert sum(partition(b, k)) == b


@pytest.mark.parametrize("b,k", CASES)
def test_spread_at_most_one(b, k):
    sizes = partition(b, k)
    assert max(sizes) - min(sizes) <= 1


@pytest.mark.parametrize("b,k", CASES)
def test_worker_count_is_preserved(b, k):
    assert len(partition(b, k)) == k


@pytest.mark.parametrize("b,k", SMALL_CASES)
def test_block_ids_partition_the_global_range(b, k):
    seen = []
    for i in range(k):
        seen.extend(block_ids(b, k, i))
    assert sorted(seen) == list(range(b))
    assert len(seen) == len(set(seen))       # no block executed twice


@pytest.mark.parametrize("b,k", CASES)
def test_offsets_are_contiguous(b, k):
    sizes = partition(b, k)
    starts = offsets(sizes)
    assert starts[0] == 0
    for i in range(1, k):
        assert starts[i] == starts[i - 1] + sizes[i - 1]


def test_historical_case_produces_8801_not_8805():
    sizes = partition(P4X_B, P4X_K)
    assert sum(sizes) == 8_801
    assert sum(sizes) != 8_805
    assert sorted(sizes) == [1760, 1760, 1760, 1760, 1761]


def test_historical_case_path_total_is_exact():
    alloc = Allocation(total_blocks=P4X_B, block_size=P4X_BLOCK, workers=P4X_K)
    audit = alloc.audit()
    assert audit["executed_blocks"] == 8_801
    assert audit["delta_blocks"] == 0
    assert audit["executed_paths"] == 2_200_250_000
    assert audit["delta_paths"] == 0
    assert audit["block_ids_tile_the_global_range"]


def test_p4x_partition_is_reproduced_and_is_wrong():
    """Pin the defect, so a regression to it cannot pass silently."""
    bad = p4x_defective_partition(P4X_B, P4X_K)
    assert bad == [1761] * 5
    assert sum(bad) == 8_805
    assert sum(bad) - P4X_B == 4                       # four extra blocks
    assert (sum(bad) - P4X_B) * P4X_BLOCK == 1_000_000  # one million paths


@pytest.mark.parametrize("b,k", CASES)
def test_p4x_partition_overshoots_exactly_when_k_does_not_divide_b(b, k):
    if b == 0:
        pytest.skip("ceil(0/K) = 0; the defect needs at least one block")
    over = sum(p4x_defective_partition(b, k)) - b
    assert over == (-b) % k
    assert (over == 0) == (b % k == 0)


@pytest.mark.parametrize("k", [1, 2, 3, 5, 7, 8, 13, 64])
def test_no_over_or_under_execution_for_any_k(k):
    """The single test §11 asks for: fail on a delta of even one block."""
    for b in (0, 1, 2, 7, 8_801, 100_000, 2_200_168_765):
        alloc = Allocation(total_blocks=b, block_size=250_000, workers=k)
        audit = alloc.audit()
        assert audit["delta_blocks"] == 0, (b, k, audit)
        assert audit["delta_paths"] == 0, (b, k, audit)
        assert audit["executed_blocks"] == b


def test_verify_rejects_an_over_execution():
    with pytest.raises(ShardInvariantError, match=r"\+4 blocks"):
        verify([1761] * 5, 8_801)


def test_verify_rejects_an_under_execution():
    with pytest.raises(ShardInvariantError, match=r"-1 blocks"):
        verify([1760] * 5, 8_801)


def test_verify_rejects_an_unbalanced_partition():
    with pytest.raises(ShardInvariantError, match="unbalanced"):
        verify([8_799, 1, 1], 8_801)


def test_partition_rejects_bad_arguments():
    with pytest.raises(ValueError):
        partition(-1, 5)
    with pytest.raises(ValueError):
        partition(10, 0)


@pytest.mark.parametrize("b,k", SMALL_CASES)
def test_partition_is_the_unique_balanced_exact_partition(b, k):
    """sum == B and spread <= 1 together determine the multiset of sizes."""
    q, r = divmod(b, k)
    assert sorted(partition(b, k)) == sorted([q] * (k - r) + [q + 1] * r)
    assert math.isclose(sum(partition(b, k)) / k, b / k)


@pytest.mark.parametrize("b,k", LARGE_CASES)
def test_large_allocations_tile_without_enumeration(b, k):
    """A production-sized frozen total is audited structurally."""
    audit = Allocation(total_blocks=b, block_size=250_000, workers=k).audit()
    assert audit["delta_blocks"] == 0
    assert audit["delta_paths"] == 0
    assert audit["block_ids_tile_the_global_range"]
    assert audit["max_minus_min"] <= 1
