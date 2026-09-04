"""RNG / logical-block identity -- the addressing half of the P4X G2 repair.

Requirement (pilot brief 12): changing K must not change the logical set of
requested independent blocks.  Floating-point reduction ORDER is not pinned --
the frozen specification does not demand it -- but block membership and N are.
"""

import math

import pytest

from p4y_pilot.blocks import (
    CELL_STRIDE,
    MAX_NAMESPACES,
    MAX_REPLICATES,
    NAMESPACE_INDEX,
    NAMESPACE_STRIDE,
    SEED_BASE,
    Cell,
    block_value,
    derive_seed,
    summarise,
)
from p4y_pilot.blocks import register_cells
from p4y_pilot.shard import block_ids, partition

#: Probe addresses, high in the space so they can never shadow a pilot cell.
register_cells({"rng-identity-probe": 900, "rng-identity-probe-b": 901,
                "cA": 902, "cB": 903,
                **{f"cell{i}": 910 + i for i in range(8)}})

#: Deliberately tiny: this file tests identity, never precision.
TINY = Cell(key="rng-identity-probe", layer="reduced", kind="cusum",
            threshold=2.0, family="gaussian", route="route_a",
            max_steps=60_000, block_size=2_000, heavy=False)
TINY_B = Cell(key="rng-identity-probe-b", layer="reduced", kind="cusum",
              threshold=2.0, family="gaussian", route="route_b",
              max_steps=60_000, block_size=2_000, heavy=False)

K_VALUES = [1, 2, 5, 7, 12, 64]
B = 12


def _execute_sharded(cell: Cell, seed: int, total: int, workers: int):
    """Run the allocation as K shards and return {logical_id: value}."""
    out = {}
    for shard in range(workers):
        for bid in block_ids(total, workers, shard):
            out[bid] = block_value(cell, seed, bid)
    return out


@pytest.mark.parametrize("k", K_VALUES)
def test_logical_block_set_is_invariant_under_k(k):
    seen = set()
    for shard in range(k):
        ids = set(block_ids(B, k, shard))
        assert not (seen & ids), "a block was scheduled on two workers"
        seen |= ids
    assert seen == set(range(B))
    assert sum(partition(B, k)) == B


def test_unregistered_cells_cannot_draw_blocks():
    with pytest.raises(KeyError, match="no frozen address"):
        derive_seed("never-registered", "design", 0)


def test_address_table_is_frozen_against_reindexing():
    with pytest.raises(ValueError, match="frozen"):
        register_cells({"rng-identity-probe": 42})
    with pytest.raises(ValueError, match="already used"):
        register_cells({"some-other-cell": 900})


def test_seed_derivation_takes_no_worker_argument():
    """The worker index cannot enter the stream without editing this call."""
    import inspect

    params = list(inspect.signature(derive_seed).parameters)
    assert params == ["cell_key", "namespace", "replicate"]
    for bad in ("worker", "shard", "k", "workers", "pid"):
        assert bad not in params


def test_block_values_are_bit_identical_across_k():
    seed = derive_seed(TINY.key, "identity", 0)
    reference = _execute_sharded(TINY, seed, B, 1)
    for k in K_VALUES:
        got = _execute_sharded(TINY, seed, B, k)
        assert got.keys() == reference.keys()
        for bid, value in got.items():
            assert value == reference[bid], f"K={k} changed block {bid}"


def test_route_b_block_values_are_bit_identical_across_k():
    seed = derive_seed(TINY_B.key, "identity", 0)
    reference = _execute_sharded(TINY_B, seed, B, 1)
    for k in (2, 5):
        got = _execute_sharded(TINY_B, seed, B, k)
        for bid, value in got.items():
            assert value == reference[bid]


@pytest.mark.parametrize("k", K_VALUES)
def test_pooled_summary_equals_the_unsharded_pooling_formula(k):
    """Pooling shards IS pooling blocks -- exactly, not approximately."""
    seed = derive_seed(TINY.key, "identity", 1)
    unsharded = [block_value(TINY, seed, i)[1] for i in range(B)]
    sharded = _execute_sharded(TINY, seed, B, k)
    pooled = [sharded[i][1] for i in range(B)]
    assert pooled == unsharded
    a, b = summarise(unsharded), summarise(pooled)
    assert a["mean"] == b["mean"]
    assert a["se"] == b["se"]
    assert a["blocks"] == b["blocks"] == B


@pytest.mark.parametrize("k", K_VALUES)
def test_path_total_is_invariant_under_k(k):
    sizes = partition(B, k)
    assert sum(sizes) * TINY.block_size == B * TINY.block_size


def test_p4x_style_per_shard_seeding_would_change_the_block_set():
    """Pin the defect: a worker-derived seed is a different experiment.

    P4X seeded each shard ``f"{route}_s2_shard{k}"`` and then looped
    ``range(blocks)`` inside it.  Reproduced here at K = 2, the union of the
    two shards' streams shares NO block with the unsharded allocation.
    """
    seed = derive_seed(TINY.key, "identity", 2)
    unsharded = {i: block_value(TINY, seed, i)[1] for i in range(4)}
    p4x = {}
    for shard in range(2):
        shard_seed = derive_seed(TINY.key, f"identity_shard{shard}", 2)
        for local in range(2):                    # each shard restarts at 0
            p4x[(shard, local)] = block_value(TINY, shard_seed, local)[1]
    assert set(p4x.values()).isdisjoint(unsharded.values())


def test_seed_derivation_is_injective_over_the_whole_address_space():
    """No two addresses share a seed -- proved, not sampled.

    A shared seed is not a cosmetic clash: two colliding addresses replay the
    SAME blocks, so replicates that the pilot counts as independent are not.
    """
    keys = [f"cell{i}" for i in range(8)]
    seeds = {}
    for key in keys:
        for ns in NAMESPACE_INDEX:
            for rep in range(200):
                addr = (key, ns, rep)
                s = derive_seed(*addr)
                prev = seeds.setdefault(s, addr)
                assert prev == addr, f"seed collision: {prev} vs {addr}"
    assert len(seeds) == len(keys) * len(NAMESPACE_INDEX) * 200


def test_address_space_bounds_make_collisions_impossible():
    assert MAX_REPLICATES == NAMESPACE_STRIDE
    assert max(NAMESPACE_INDEX.values()) < MAX_NAMESPACES
    assert MAX_NAMESPACES * NAMESPACE_STRIDE <= CELL_STRIDE


def test_stream_is_unique_per_address_and_block():
    """(seed, block id) is the stream key; the pilot must not reuse one."""
    used = {}
    for key in ("cA", "cB"):
        for ns in ("design", "validation"):
            for rep in range(64):
                s = derive_seed(key, ns, rep)
                for bid in range(4):
                    addr = (key, ns, rep, bid)
                    prev = used.setdefault((s, bid), addr)
                    assert prev == addr, f"stream reuse: {prev} vs {addr}"


def test_seed_namespace_is_disjoint_from_every_earlier_campaign():
    """P4 frozen 401xxxx, P4X R0 411xxxx, P4X production 421xxxx."""
    assert SEED_BASE == 4_310_000_000
    for base in (4_010_000, 4_110_000, 4_210_000):
        assert base + 1_000_000 < SEED_BASE
    lowest = derive_seed("cell0", "calibration", 0)
    assert lowest == SEED_BASE + 910 * CELL_STRIDE
    assert lowest > 4_210_000 + 1_000_000


def test_summarise_is_the_frozen_block_convention():
    vals = [1.0, 2.0, 3.0, 4.0]
    s = summarise(vals)
    assert s["mean"] == 2.5
    assert math.isclose(s["sd"], math.sqrt(5.0 / 3.0))
    assert math.isclose(s["se"], math.sqrt(5.0 / 3.0) / 2.0)
    assert math.isclose(s["relative_se"], s["se"] / 2.5)
