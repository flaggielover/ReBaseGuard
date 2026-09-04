"""Logical block identity, addressing, and lazy per-block evaluation.

The second half of the P4X sharding defect was addressing, not arithmetic.
P4X gave each shard *its own Philox seed* (``..._s2_shard{k}``) and each shard
then looped ``for batch in range(blocks)``.  The scientific random stream was
therefore a function of the worker, so changing K changed the set of logical
blocks the campaign asked for.  Blocks are i.i.d., so this does not bias the
estimator -- but it destroys reproducibility, makes "the frozen allocation"
un-addressable, and is precisely what let an over-count go unnoticed.

Here a block's stream is a function of its LOGICAL ADDRESS only

    address = (cell_key, namespace, replicate)  ->  seed        (worker-free)
    logical block index                         ->  Philox batch

so shard i simply evaluates a contiguous slice of the SAME global index range
under the SAME seed.  K is a scheduling parameter and nothing else.

The per-block estimator functions reproduce the frozen Priority-4 ``route_a``
and ``route_b`` block by block; ``tests/test_estimator_nondrift.py`` asserts
that pooling them over ``range(B)`` reproduces the frozen functions exactly.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

_P4 = Path(__file__).resolve().parents[3] / "p4_theory_generalization"
if str(_P4 / "src") not in sys.path:
    sys.path.insert(0, str(_P4 / "src"))

from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402
from rebaseguard_p4_general.simulate import simulate_group  # noqa: E402

#: Fresh seed namespace for the P4Y pilot.  Disjoint by construction from the
#: frozen Priority-4 campaign (401xxxx), the P4X R0 pilot (411xxxx) and P4X
#: production (421xxxx): those all live below 5e6, this base is above 4.3e9.
#:
#: The seed is derived by an INJECTIVE positional code, not by a hash modulo a
#: small prime.  The inherited pattern ``SEED_BASE + sha256(...) % 9973`` is
#: collision-prone: over the few thousand addresses a replicated pilot needs,
#: a birthday collision is near-certain, and two colliding addresses do not
#: merely share a number -- they replay the SAME blocks, so "independent
#: replicates" silently stop being independent.  ``tests/`` proves injectivity
#: over the whole declared address space rather than sampling it.
SEED_BASE = 4_310_000_000
CELL_STRIDE = 1_000_000
NAMESPACE_STRIDE = 100_000
MAX_REPLICATES = NAMESPACE_STRIDE          # 100 000 replicates per namespace
MAX_NAMESPACES = CELL_STRIDE // NAMESPACE_STRIDE   # 10 namespaces per cell
MAX_CELLS = 1_000

#: Frozen addressing table.  A cell or namespace absent from it has no seed,
#: so no block can be drawn for it by accident.
CELL_INDEX: dict[str, int] = {}
NAMESPACE_INDEX = {
    "calibration": 0,     # fixes r*_pilot BEFORE any rule is evaluated
    "reference": 1,       # the historical-style reference measurement
    "design": 2,          # tunes the candidate rules
    "validation": 3,      # the ONLY namespace p_attain is estimated from
    "identity": 4,        # tests only, never result-bearing
    "identity_shard0": 5,
    "identity_shard1": 6,
}

FD_STEPS = (0.05, 0.025)
M_GRID = (1, 2, 3, 5)


def register_cells(mapping: dict[str, int]) -> None:
    """Freeze the cell half of the address table.

    Indices are declared EXPLICITLY, never assigned by first-touch order: an
    order-dependent address table means the same cell gets a different seed
    depending on which script ran first, and "the frozen allocation" stops
    being reproducible.  Re-registering a key at a different index, or
    reusing an index, is an error rather than an overwrite.
    """
    for key, idx in mapping.items():
        if not 0 <= idx < MAX_CELLS:
            raise ValueError(f"cell index {idx} outside the address space")
        if CELL_INDEX.get(key, idx) != idx:
            raise ValueError(
                f"cell {key!r} already registered at {CELL_INDEX[key]}, "
                f"not {idx}: the address table is frozen")
        clash = [k for k, v in CELL_INDEX.items() if v == idx and k != key]
        if clash:
            raise ValueError(f"cell index {idx} already used by {clash[0]!r}")
        CELL_INDEX[key] = idx


def derive_seed(cell_key: str, namespace: str, replicate: int) -> int:
    """Worker-independent, injective seed for one (cell, namespace, replicate).

    The worker index is deliberately NOT an argument.  It cannot be added
    later without changing this signature, which the tests pin.
    """
    if cell_key not in CELL_INDEX:
        raise KeyError(
            f"cell {cell_key!r} has no frozen address; register_cells() first")
    if namespace not in NAMESPACE_INDEX:
        raise KeyError(f"namespace {namespace!r} is not in the address table")
    if not 0 <= replicate < MAX_REPLICATES:
        raise ValueError(f"replicate {replicate} outside the address space")
    return (SEED_BASE
            + CELL_INDEX[cell_key] * CELL_STRIDE
            + NAMESPACE_INDEX[namespace] * NAMESPACE_STRIDE
            + replicate)


@dataclass(frozen=True, slots=True)
class Cell:
    """One pilot (layer, detector, family, route) stratum."""

    key: str
    layer: str
    kind: str
    threshold: float
    family: str
    route: str
    max_steps: int
    block_size: int
    heavy: bool

    @property
    def detector(self) -> Detector:
        return Detector(self.kind, self.threshold)

    @property
    def config(self) -> str:
        return f"{self.layer}/{self.kind}@{self.threshold:g}/{self.family}"


def block_value(cell: Cell, seed: int, block_id: int) -> dict[int, float]:
    """The frozen per-block estimator value, per ``m``, for one logical block.

    Route A -- ``mean(A_m * sum psi(Z))`` on a compact single-``e`` run.
    Route B -- the per-block Richardson combination of a CRN central
    difference at ``h = 0.05`` and ``h/2``.

    Both are copied structurally from the frozen ``estimators.py``; the
    non-drift test asserts bit equality, it is not assumed here.
    """
    family = REGISTRY[cell.family]
    detector = cell.detector
    m_max = max(M_GRID)
    if cell.route == "route_a":
        (run,) = simulate_group(
            family=family, detector=detector, e_values=(0.0,),
            n_paths=cell.block_size, seed=seed, batch=block_id, m_max=m_max,
            mode="compact", max_steps=cell.max_steps,
        )
        return {
            m: float((run.window_mean(m) * run.score_sum).mean())
            for m in M_GRID
        }
    coarse, fine = FD_STEPS
    per_step: dict[float, dict[int, float]] = {}
    for step in FD_STEPS:
        plus, minus = simulate_group(
            family=family, detector=detector, e_values=(step, -step),
            n_paths=cell.block_size, seed=seed, batch=block_id, m_max=m_max,
            mode="aligned", max_steps=cell.max_steps,
        )
        per_step[step] = {
            m: float(-((plus.window_mean(m) - minus.window_mean(m))
                       / (2.0 * step)).mean())
            for m in M_GRID
        }
    return {
        m: (4.0 * per_step[fine][m] - per_step[coarse][m]) / 3.0
        for m in M_GRID
    }


@dataclass
class BlockPool:
    """Lazily evaluated, permanently cached logical blocks for one stream.

    A rule asks for ``take(n)``; only blocks never evaluated before are
    simulated.  Because every rule in the comparison reads a PREFIX of the
    same stream, four rules cost no more than the greediest one, and each
    rule still sees a genuinely fresh block whenever it extends.
    """

    cell: Cell
    namespace: str
    replicate: int
    values: dict[int, dict[int, float]] = field(default_factory=dict)
    blocks_simulated: int = 0
    paths_simulated: int = 0
    cpu_seconds: float = 0.0

    @property
    def seed(self) -> int:
        return derive_seed(self.cell.key, self.namespace, self.replicate)

    def take(self, n: int) -> list[dict[int, float]]:
        import resource

        for block_id in range(n):
            if block_id in self.values:
                continue
            r0 = resource.getrusage(resource.RUSAGE_SELF)
            c0 = r0.ru_utime + r0.ru_stime
            self.values[block_id] = block_value(self.cell, self.seed, block_id)
            r1 = resource.getrusage(resource.RUSAGE_SELF)
            self.cpu_seconds += (r1.ru_utime + r1.ru_stime) - c0
            self.blocks_simulated += 1
            self.paths_simulated += self.cell.block_size
        return [self.values[i] for i in range(n)]


def summarise(values: list[float]) -> dict[str, float]:
    """Frozen block-mean convention: mean, block sd, se = sd / sqrt(B)."""
    arr = np.asarray(values, dtype=float)
    b = arr.size
    if b < 2:
        return {"mean": float(arr.mean()) if b else math.nan,
                "sd": math.nan, "se": math.nan, "blocks": int(b),
                "relative_se": math.nan}
    mean = float(arr.mean())
    sd = float(arr.std(ddof=1))
    se = sd / math.sqrt(b)
    return {"mean": mean, "sd": sd, "se": se, "blocks": int(b),
            "relative_se": se / abs(mean) if mean != 0 else math.inf}


def worst_relative_se(blocks: list[dict[int, float]]) -> tuple[float, int]:
    """The precision a route is judged on: the WORST ``m`` in the frozen grid.

    The four windows share their paths, so one allocation must satisfy all
    four.  Taking the worst is the only reading that makes "the route attains
    r*" a property of the route rather than of a chosen window.
    """
    worst, arg = -math.inf, M_GRID[0]
    for m in M_GRID:
        r = summarise([b[m] for b in blocks])["relative_se"]
        if r > worst:
            worst, arg = r, m
    return worst, arg
