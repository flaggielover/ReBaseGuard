"""Estimator non-drift.

The pilot evaluates the frozen estimators one LOGICAL BLOCK at a time so that
a block can be addressed, sharded and re-pooled.  That reorganisation must not
be an estimator change -- STOP rule 1 of the P4X checkpoint, inherited here as
a kill criterion.

These tests assert BIT equality against the frozen ``route_a`` / ``route_b``,
not agreement to a tolerance.
"""

import sys
from pathlib import Path

import pytest

from p4y_pilot.blocks import (
    FD_STEPS,
    M_GRID,
    Cell,
    block_value,
    derive_seed,
    register_cells,
    summarise,
)

register_cells({"nondrift-a": 920, "nondrift-b": 921, "nondrift-sr": 922})

_P4 = Path(__file__).resolve().parents[2] / "p4_theory_generalization"
sys.path.insert(0, str(_P4 / "src"))
from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.estimators import route_a, route_b  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402

BLOCKS, PATHS = 6, 4_000

CELLS = [
    Cell(key="nondrift-a", layer="reduced", kind="cusum", threshold=2.0,
         family="t1p5", route="route_a", max_steps=60_000,
         block_size=PATHS, heavy=True),
    Cell(key="nondrift-b", layer="reduced", kind="cusum", threshold=2.0,
         family="t1p5", route="route_b", max_steps=60_000,
         block_size=PATHS, heavy=True),
    Cell(key="nondrift-sr", layer="reduced", kind="sr", threshold=20.0,
         family="gaussian", route="route_a", max_steps=60_000,
         block_size=PATHS, heavy=False),
]


def _frozen(cell: Cell, seed: int):
    common = dict(family=REGISTRY[cell.family],
                  detector=Detector(cell.kind, cell.threshold),
                  m_grid=M_GRID, batches=BLOCKS, paths=cell.block_size,
                  seed=seed, max_steps=cell.max_steps)
    if cell.route == "route_a":
        return route_a(**common)
    return route_b(**common, fd_steps=FD_STEPS)


@pytest.mark.parametrize("cell", CELLS, ids=lambda c: c.key)
def test_per_block_pooling_reproduces_the_frozen_estimator_exactly(cell):
    seed = derive_seed(cell.key, "identity", 0)
    frozen = _frozen(cell, seed)
    blocks = [block_value(cell, seed, i) for i in range(BLOCKS)]
    for m in M_GRID:
        got = summarise([b[m] for b in blocks])
        ref = frozen["by_m"][str(m)]["gamma"]
        assert got["mean"] == ref["mean"], f"m={m} mean drifted"
        assert got["se"] == ref["se"], f"m={m} se drifted"
        assert got["blocks"] == ref["batches"]


@pytest.mark.parametrize("cell", CELLS, ids=lambda c: c.key)
def test_block_values_are_deterministic_in_the_logical_id(cell):
    seed = derive_seed(cell.key, "identity", 0)
    assert block_value(cell, seed, 3) == block_value(cell, seed, 3)
    assert block_value(cell, seed, 3) != block_value(cell, seed, 4)


def test_a_prefix_of_the_stream_equals_a_shorter_frozen_run():
    """Staged allocation reads prefixes; a prefix must be its own frozen run."""
    cell = CELLS[0]
    seed = derive_seed(cell.key, "identity", 1)
    blocks = [block_value(cell, seed, i) for i in range(BLOCKS)]
    common = dict(family=REGISTRY[cell.family],
                  detector=Detector(cell.kind, cell.threshold),
                  m_grid=M_GRID, paths=cell.block_size, seed=seed,
                  max_steps=cell.max_steps)
    for stop in (2, 4, BLOCKS):
        short = route_a(**common, batches=stop)
        for m in M_GRID:
            got = summarise([b[m] for b in blocks[:stop]])
            assert got["mean"] == short["by_m"][str(m)]["gamma"]["mean"]
            assert got["se"] == short["by_m"][str(m)]["gamma"]["se"]


def test_frozen_estimator_sources_are_untouched_by_the_pilot():
    """The pilot imports the frozen package read-only; nothing is shadowed."""
    import rebaseguard_p4_general.estimators as est
    import rebaseguard_p4_general.simulate as sim

    assert Path(est.__file__).is_relative_to(_P4)
    assert Path(sim.__file__).is_relative_to(_P4)
