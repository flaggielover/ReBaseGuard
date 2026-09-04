"""Frozen pilot configuration -- addresses, cells, constants inherited from P4.

Everything here is either (a) inherited unchanged from the frozen Priority-4
protocol and the P4X precision policy, or (b) a pilot-only scheduling constant
that has no scientific meaning.  Nothing in this file is a P4Y freeze.
"""

from __future__ import annotations

from .blocks import Cell, register_cells

# ---------------------------------------------------------------- inherited
#: Forced by the unchanged 3% accuracy criterion: 1.96 * sqrt(2) * r* = 0.03.
R_STAR_PRODUCTION = 0.010823

#: Heavy-tail rate from the frozen P4X policy, kappa = 1 - 1/alpha at the
#: measured tail-index floor alpha = 1.47.  Inherited, not re-fitted.
ALPHA_FLOOR = 1.47
KAPPA_HEAVY = 1.0 - 1.0 / ALPHA_FLOOR          # 0.3197278911564626
KAPPA_LIGHT = 0.5

#: Frozen block-size convention.  Production keeps 250 000 for alpha < 2.
PRODUCTION_BLOCK_HEAVY = 250_000
PRODUCTION_BLOCK_DEFAULT = 20_000

M_GRID = (1, 2, 3, 5)
FD_STEPS = (0.05, 0.025)

# ------------------------------------------------------------- pilot-only
#: Stage-1 block count the pilot target r*_pilot is defined against.  Chosen
#: SMALL on purpose: realised-precision variability is worst at few blocks, so
#: a rule validated here is conservative for the far larger production block
#: counts.  See PILOT_PREREGISTRATION.md sec. 4.
B1_NOMINAL = 24
REFERENCE_BLOCKS = 12
MIN_BLOCKS = 8
CAP_MULTIPLIER = 6                     # cap_blocks = 6 * B1_NOMINAL = 144
CALIBRATION_BLOCKS = 400

#: Replication.  R_VALIDATION = 59 is the smallest R with delta**R <= beta at
#: delta = 0.95, beta = 0.05, so a clean run certifies p_attain >= 0.95.
R_DESIGN = 20
R_VALIDATION = 59
DELTA = 0.95
BETA = 0.05

#: Global replicate numbering keeps the design and validation reference
#: streams disjoint: design uses 0.., validation uses 1000...
DESIGN_BASE = 0
VALIDATION_BASE = 1_000

#: STOP rules.  Hard, checked live, never silently extended.
PILOT_CPU_CAP_HOURS = 2.0
POOL_HARD_LIMIT = REFERENCE_BLOCKS + CAP_MULTIPLIER * B1_NOMINAL

# ------------------------------------------------- AMENDMENT 1: cost tail
#: Added after design, before validation.  Purpose: project a production cap
#: from an UNCENSORED cost distribution.  Never used to select a rule.
COSTTAIL_REPLICATES = 24
COSTTAIL_CAP_MULTIPLIER = 16
COSTTAIL_CAP_BLOCKS = COSTTAIL_CAP_MULTIPLIER * B1_NOMINAL
COSTTAIL_POOL_LIMIT = REFERENCE_BLOCKS + COSTTAIL_CAP_BLOCKS
COSTTAIL_RULES = ("A_oneshot_one_topup", "C_staged_safety_1.00",
                  "D_staged_quantile_0.95")

PILOT_CELLS: tuple[Cell, ...] = (
    Cell(key="C1", layer="reduced", kind="cusum", threshold=2.0,
         family="t1p5", route="route_a", max_steps=60_000,
         block_size=50_000, heavy=True),
    Cell(key="C2", layer="reduced", kind="cusum", threshold=2.0,
         family="t1p5", route="route_b", max_steps=60_000,
         block_size=20_000, heavy=True),
    Cell(key="C3", layer="reduced", kind="sr", threshold=20.0,
         family="t1p5", route="route_a", max_steps=60_000,
         block_size=50_000, heavy=True),
    Cell(key="C4", layer="reduced", kind="sr", threshold=20.0,
         family="t1p5", route="route_b", max_steps=60_000,
         block_size=20_000, heavy=True),
    Cell(key="C5", layer="reduced", kind="cusum", threshold=2.0,
         family="gaussian", route="route_b", max_steps=60_000,
         block_size=20_000, heavy=False),
    # C6 repeats C1 at the PRODUCTION heavy-tail block size, so the pilot can
    # say whether its small-block operating point is conservative or merely
    # different.  Same configuration, same route, different block size only.
    Cell(key="C6", layer="reduced", kind="cusum", threshold=2.0,
         family="t1p5", route="route_a", max_steps=60_000,
         block_size=PRODUCTION_BLOCK_HEAVY, heavy=True),
)

register_cells({c.key: i for i, c in enumerate(PILOT_CELLS)})


def kappa_for(cell: Cell) -> float:
    return KAPPA_HEAVY if cell.heavy else KAPPA_LIGHT
