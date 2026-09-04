"""Frozen Pilot-4 measurement design: grids, criteria, budget.

Nothing here is an allocation rule.  There is no Stage-1 sizing, no staged
top-up, no cap, no kappa.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_P1 = Path(__file__).resolve().parents[3] / "p4y_precision_governance_pilot"
if str(_P1 / "src") not in sys.path:
    sys.path.insert(0, str(_P1 / "src"))

from p4y_pilot.blocks import Cell  # noqa: E402

from .addressing4 import register  # noqa: E402
from .blocks4 import BASE_BLOCK_PATHS, base_blocks_needed  # noqa: E402

# ------------------------------------------------------------- frozen grids
BLOCK_SIZES = (250_000, 1_000_000, 4_000_000)

#: Reference block counts per block size.  Chosen so the reference PATH budget
#: stays production-plausible: a reference costs B_ref * b paths per stratum,
#: and eight heavy strata must fit well inside the inherited 45 CPU-hour
#: acceptance envelope.
BREF_GRID = {
    250_000: (32, 64, 128, 256),
    1_000_000: (32, 64, 128),
    4_000_000: (16, 32, 64),
}

#: Benchmark master-pool size, in LOGICAL blocks, per pool.  Two independent
#: pools per (cell, block size).
MASTER_POOL_BLOCKS = {250_000: 2048, 1_000_000: 1024, 4_000_000: 512}

# ----------------------------------------------------- frozen accuracy target
#: theta_hat must land inside [theta_bench / C, theta_bench * C].
ACCURACY_FACTOR = 1.25
#: ... with at least this probability.
TARGET_PROBABILITY = 0.90
#: One-sided validation confidence.
BETA = 0.05
#: Smallest R with TARGET_PROBABILITY ** R <= BETA  ->  29.
R_REFERENCE_DRAWS = 29

#: Reported alongside, never decisive.
SECONDARY_FACTOR = 1.50

# --------------------------------------------- frozen benchmark admissibility
#: Two independent master pools must agree within this multiplicative factor.
C_SPLIT = 1.25
#: Quarter-level split spread, reported; decisive only through C_SPLIT.
SPLIT_PARTS = 4
#: theta over the full pool vs over its first half.
C_PREFIX = 1.15
PREFIX_FRACTIONS = (0.125, 0.25, 0.5, 1.0)
#: Load-bearing: a single block may not carry more than this share of the
#: total squared deviation of the combined benchmark pool.
MAX_TOP1_SHARE = 0.10
MAX_TOP5_SHARE = 0.30

# ---------------------------------------------------------- frozen budgets
PILOT4_CPU_CAP_HOURS = 5.0
#: A candidate pair is affordable only if expanding the reference to it, for
#: all eight production heavy strata, costs at most this.  One fifth of the
#: inherited 45 CPU-hour acceptance envelope.
MAX_PRODUCTION_REFERENCE_HOURS = 10.0
#: Measured P4X production rate for the heavy configurations, s per 1e6 paths.
#: Cost metadata only.
HEAVY_PRODUCTION_RATE_S_PER_1E6 = 12.0
N_HEAVY_PRODUCTION_STRATA = 8

# ---------------------------------------------------------------- cells
@dataclass(frozen=True, slots=True)
class Stratum:
    key: str
    cell: Cell
    heavy: bool
    block_sizes: tuple[int, ...]
    bref_cap: int
    role: str


CELLS: tuple[Stratum, ...] = (
    Stratum("H", Cell(key="H", layer="reduced", kind="cusum", threshold=2.0,
                      family="t1p5", route="route_a", max_steps=60_000,
                      block_size=BASE_BLOCK_PATHS, heavy=True),
            True, BLOCK_SIZES, 256,
            "primary heavy stratum -- the full block-size sweep"),
    Stratum("HSR", Cell(key="HSR", layer="reduced", kind="sr", threshold=20.0,
                        family="t1p5", route="route_a", max_steps=60_000,
                        block_size=BASE_BLOCK_PATHS, heavy=True),
            True, (250_000,), 256,
            "heavy, SR detector -- is the phenomenon detector-generic?"),
    Stratum("HB", Cell(key="HB", layer="reduced", kind="cusum", threshold=2.0,
                       family="t1p5", route="route_b", max_steps=60_000,
                       block_size=BASE_BLOCK_PATHS, heavy=True),
            True, (250_000,), 64,
            "heavy, Route B -- is the phenomenon route-generic?"),
    Stratum("O", Cell(key="O", layer="reduced", kind="cusum", threshold=2.0,
                      family="gaussian", route="route_a", max_steps=60_000,
                      block_size=BASE_BLOCK_PATHS, heavy=False),
            False, (250_000,), 128,
            "ordinary finite-variance control -- the framework must find a "
            "stable regime where one exists"),
)

register({s.key: i for i, s in enumerate(CELLS)})

HEAVY_KEYS = tuple(s.key for s in CELLS if s.heavy)
CONTROL_KEYS = tuple(s.key for s in CELLS if not s.heavy)


def stratum(key: str) -> Stratum:
    return next(s for s in CELLS if s.key == key)


def brefs_for(s: Stratum, block_paths: int) -> tuple[int, ...]:
    return tuple(b for b in BREF_GRID[block_paths] if b <= s.bref_cap)


def master_pool_blocks(s: Stratum, block_paths: int) -> int:
    """Logical blocks per master pool, for one stratum at one block size.

    Eight times the largest reference this stratum tests at that block size,
    capped by the global pool size.  A benchmark must be substantially larger
    than the references it judges; eight times is the frozen multiple.
    """
    return min(MASTER_POOL_BLOCKS[block_paths], 8 * max(brefs_for(s, block_paths)))


def master_base_blocks(s: Stratum) -> int:
    """Base blocks per master pool: enough for the largest block size used."""
    return max(base_blocks_needed(b, master_pool_blocks(s, b))
               for b in s.block_sizes)


def reference_base_blocks(s: Stratum) -> int:
    """Base blocks per reference draw: enough for the largest (b, B_ref)."""
    return max(base_blocks_needed(b, max(brefs_for(s, b)))
               for b in s.block_sizes if brefs_for(s, b))


def production_reference_hours(block_paths: int, bref: int) -> float:
    paths = block_paths * bref * N_HEAVY_PRODUCTION_STRATA
    return paths * HEAVY_PRODUCTION_RATE_S_PER_1E6 / 1e6 / 3600.0


def reachable_addresses() -> list:
    from .addressing4 import Address

    out = []
    for s in CELLS:
        out.append(Address(s.key, "master0", 0))
        out.append(Address(s.key, "master1", 0))
        for r in range(R_REFERENCE_DRAWS):
            out.append(Address(s.key, "reference", r))
    return out
