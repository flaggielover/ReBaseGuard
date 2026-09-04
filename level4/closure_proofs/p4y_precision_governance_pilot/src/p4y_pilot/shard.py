"""Exact shard partition of a frozen block allocation.

The P4X defect, stated precisely
--------------------------------
P4X sharded a stage-2 top-up with

    per_shard = ceil(blocks_total / n_shards)

and then gave *every* shard ``per_shard`` blocks.  The executed total is

    n_shards * ceil(B / K)  =  B + ((-B) mod K)

which is >= B and equals B only when K divides B.  For the campaign's largest
top-up, B = 8801 and K = 5, so 8805 blocks and 8805 * 250000 = 2 201 250 000
paths executed against a frozen allocation of 8801 blocks / 2 200 250 000
paths: four unauthorised blocks, one million unauthorised paths.

The repair is the exact balanced partition below.  It is the only partition
that simultaneously satisfies sum == B and max - min <= 1.
"""

from __future__ import annotations

from dataclasses import dataclass


class ShardInvariantError(AssertionError):
    """Raised when a partition would not execute exactly the frozen total."""


def partition(total_blocks: int, workers: int) -> list[int]:
    """Split ``total_blocks`` across ``workers`` with an exact sum.

        q, r = divmod(B, K)
        shard_i = q + 1 for i < r, else q

    Sums to ``q*K + r == B`` by the division algorithm, and the multiset of
    sizes is ``{q+1}*r + {q}*(K-r)`` so the spread is at most one.  Empty
    shards are *kept*, not dropped: dropping them would silently change K and
    the addressing below is what makes them free.
    """
    if total_blocks < 0:
        raise ValueError("total_blocks must be non-negative")
    if workers < 1:
        raise ValueError("workers must be >= 1")
    q, r = divmod(total_blocks, workers)
    sizes = [q + 1 if i < r else q for i in range(workers)]
    verify(sizes, total_blocks)
    return sizes


def offsets(sizes: list[int]) -> list[int]:
    """Exclusive prefix sums: the first logical block index of each shard."""
    out, run = [], 0
    for s in sizes:
        out.append(run)
        run += s
    return out


def block_ids(total_blocks: int, workers: int, shard: int) -> range:
    """The LOGICAL block indices shard ``shard`` must execute.

    Contiguous half-open ranges of a single global index space.  The union
    over shards is exactly ``range(total_blocks)`` for every ``workers``, so
    the logical block set is invariant under K -- see ``blocks.py``.
    """
    if not 0 <= shard < workers:
        raise ValueError("shard out of range")
    sizes = partition(total_blocks, workers)
    start = offsets(sizes)[shard]
    return range(start, start + sizes[shard])


def verify(sizes: list[int], total_blocks: int) -> None:
    """Mechanical check of the two invariants.  Raises, never warns."""
    got = sum(sizes)
    if got != total_blocks:
        raise ShardInvariantError(
            f"shard sum {got} != frozen total {total_blocks} "
            f"(delta {got - total_blocks:+d} blocks)"
        )
    if sizes and max(sizes) - min(sizes) > 1:
        raise ShardInvariantError(
            f"shard sizes unbalanced: max {max(sizes)} min {min(sizes)}"
        )


def p4x_defective_partition(total_blocks: int, workers: int) -> list[int]:
    """The P4X partition, reproduced verbatim so the defect is testable.

    Present only as the regression target of
    ``tests/test_shard_invariants.py``.  Never called by the pilot.
    """
    import math

    per_shard = math.ceil(total_blocks / workers)
    return [per_shard] * workers


@dataclass(frozen=True, slots=True)
class Allocation:
    """A frozen allocation and the only execution plan allowed to realise it."""

    total_blocks: int
    block_size: int
    workers: int

    @property
    def total_paths(self) -> int:
        return self.total_blocks * self.block_size

    def plan(self) -> list[dict]:
        sizes = partition(self.total_blocks, self.workers)
        starts = offsets(sizes)
        return [
            {
                "shard": i,
                "blocks": sizes[i],
                "block_size": self.block_size,
                "paths": sizes[i] * self.block_size,
                "first_block_id": starts[i],
                "block_ids": range(starts[i], starts[i] + sizes[i]),
            }
            for i in range(self.workers)
        ]

    def audit(self) -> dict:
        """Executed-vs-frozen ledger.  ``delta_blocks`` must be exactly 0.

        The coverage check is structural, not enumerative: the shard ranges
        are contiguous, start at 0 and abut, so they tile ``range(B)`` iff
        each start equals the previous end and the last end is ``B``.  A
        frozen allocation can be billions of blocks; nothing here may
        materialise them.
        """
        plan = self.plan()
        executed = sum(p["blocks"] for p in plan)
        tiles, cursor = True, 0
        for p in plan:
            r = p["block_ids"]
            if r.start != cursor or len(r) != p["blocks"]:
                tiles = False
                break
            cursor = r.stop
        tiles = tiles and cursor == self.total_blocks
        return {
            "frozen_blocks": self.total_blocks,
            "executed_blocks": executed,
            "delta_blocks": executed - self.total_blocks,
            "frozen_paths": self.total_paths,
            "executed_paths": executed * self.block_size,
            "delta_paths": (executed - self.total_blocks) * self.block_size,
            "block_ids_tile_the_global_range": tiles,
            "max_minus_min": (max(p["blocks"] for p in plan)
                              - min(p["blocks"] for p in plan)),
        }
