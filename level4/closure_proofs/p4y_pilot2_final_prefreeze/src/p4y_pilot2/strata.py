"""Frozen Pilot-2 cells, strata and constants.

Every stratum is an ACTUAL P4X stage-1 block count, reconstructed from the
immutable P4X allocation metadata (`checkpoint_a.json` production_plan and
`c2_cell_ledger.json`).  No P4X correspondence outcome, discrepancy, z or
pass/fail was read to build this file -- only allocation and cost metadata,
which brief section 10 permits.

Verified P4X production regime, 48 (configuration, route) strata:

    stage-1 block counts   48 .. 1784   median 160
    final   block counts   48 .. 9021   median 160
    B_ref / B1             median 1.000, minimum 0.0022 on the heavy-tail
                           high-cost configurations, whose reference was only
                           3.8-24 blocks of 250 000 paths
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_P1 = Path(__file__).resolve().parents[3] / "p4y_precision_governance_pilot"
if str(_P1 / "src") not in sys.path:
    sys.path.insert(0, str(_P1 / "src"))

from p4y_pilot.blocks import Cell  # noqa: E402

from .addressing import register  # noqa: E402

# ------------------------------------------------------------- inherited
#: Operative frozen value, exactly as P4X production used it.
R_STAR = 0.010823
#: Provenance only: checkpoint_a.json precision_rule.r_star_exact.
R_STAR_EXACT = 0.010823062977345114
FROZEN_ACCURACY_CRITERION = 0.03

#: The two predeclared block-count scaling exponents.  No third is admissible.
KAPPA_A = 0.3197278911564626      # 1 - 1/alpha at the frozen alpha floor 1.47
KAPPA_B = 0.5                     # the finite-variance block-count rate
KAPPA_CANDIDATES = {"kappa_A_0.3197": KAPPA_A, "kappa_B_0.5": KAPPA_B}

M_GRID = (1, 2, 3, 5)
FD_STEPS = (0.05, 0.025)

# --------------------------------------------------------------- strata
@dataclass(frozen=True, slots=True)
class Stratum:
    key: str
    b1: int
    b_ref: int
    regime: str
    provenance: str


STRATA: tuple[Stratum, ...] = (
    Stratum("T1", 48, 48, "low",
            "the modal P4X stage-1 allocation: 10 of 48 (config, route) strata"),
    Stratum("T2", 160, 160, "middle",
            "the median P4X stage-1 allocation"),
    Stratum("T3", 300, 300, "high",
            "the upper mode of the B_ref/B1 == 1 group: 11 of 48 strata"),
    Stratum("T4", 215, 4, "heavy-tail high-cost",
            "frozen/cusum@5/t1p5 route B: B_ref 3.8 -> 4, B1 215.2 -> 215.  "
            "This single configuration consumed 18.60 of P4X's 24.75 CPU-hours"),
    Stratum("T5", 1784, 4, "extreme",
            "frozen/sr@520.886/t1p5 route B: the MAXIMUM P4X stage-1 "
            "allocation, again on a 3.8 -> 4 block reference"),
)

#: The stage-1 sizing exponent is INHERITED, not a Pilot-2 choice: every one of
#: P4X's 96 production_plan rows carries kappa_stage1 = 0.5.  Pilot-2's kappa
#: question is about the STAGED GROWTH exponent only.
KAPPA_STAGE1 = 0.5
MIN_BLOCKS = 8

# ---------------------------------------------------------------- cells
#: Block sizes come from the PRE-FREEZE feasibility probe, which measured only
#: cost per block and the Hill index of the BLOCK MEANS -- never an allocation
#: outcome.  Each is the smallest probed size whose block means are
#: comfortably finite-variance, which is what makes the block-COUNT regime
#: faithful:  H alpha ~ 5.5 at 5 000,  L alpha ~ 86 at 1 000,
#: RB alpha ~ 6.0 at 10 000.
CELLS: dict[str, Cell] = {
    "H": Cell(key="H", layer="reduced", kind="cusum", threshold=2.0,
              family="t1p5", route="route_a", max_steps=60_000,
              block_size=5_000, heavy=True),
    "L": Cell(key="L", layer="reduced", kind="cusum", threshold=2.0,
              family="gaussian", route="route_a", max_steps=60_000,
              block_size=1_000, heavy=False),
    "RB": Cell(key="RB", layer="reduced", kind="cusum", threshold=2.0,
               family="t1p5", route="route_b", max_steps=60_000,
               block_size=10_000, heavy=True),
}

#: Which strata each cell runs.  H is the primary heavy-tail cell and covers
#: the whole regime; L is the finite-variance control; RB is a Route-B
#: robustness check reported SEPARATELY and excluded from the primary endpoint.
CELL_STRATA = {"H": ("T1", "T2", "T3", "T4", "T5"),
               "L": ("T1", "T2", "T3"),
               "RB": ("T1",)}

PRIMARY_CELLS = ("H", "L")
ROBUSTNESS_CELLS = ("RB",)

register(cells={"H": 0, "L": 1, "RB": 2},
         strata={s.key: i for i, s in enumerate(STRATA)})

# ---------------------------------------------- why there is no deficit axis
#: A precision DEFICIT is not a separate regime.  Stage 1 is sized from the
#: reference by the inherited law, so a route that is a factor D short of
#: target simply receives a stage-1 allocation D**(1/kappa_stage1) times
#: larger -- and is then, by construction, at target in expectation at its own
#: B1.  The deficit is absorbed into B1, and B1 is exactly what the strata
#: span (48 to 1784, the verified P4X range).  Adding a deficit axis would
#: re-measure the same regime at a shifted B1 and buy nothing.
#:
#: What the heavy-tail configurations actually had was not a deficit but a
#: TINY REFERENCE -- 3.8 blocks of 250 000 paths -- whose relative SE estimate
#: carries a ~41 % standard deviation that the stage-1 law squares.  T4 and T5
#: reproduce that directly.

# ------------------------------------------------------------ cap grid
CAP_MULTIPLIERS = (1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0)
MAX_CAP_MULTIPLIER = max(CAP_MULTIPLIERS)

# ------------------------------------------------------- replication
R_DESIGN = 20
R_VALIDATION = 59
R_DESIGN_ROBUSTNESS = 12
R_VALIDATION_ROBUSTNESS = 29

DESIGN_BASE = 0
VALIDATION_BASE = 100_000 // 2      # 50 000: disjoint from design by construction

CALIBRATION_BLOCKS = 2_000
MIN_BLOCK_MEAN_ALPHA = 2.5          # STOP below this: the regime would not be faithful

# ----------------------------------------------------------- statistics
DELTA = 0.95                        # governance-disposition target
BETA = 0.05                         # one-sided confidence 1 - beta
ATTAINMENT_FLOOR_POOLED = 0.95      # cap-acceptability, pooled
ATTAINMENT_FLOOR_STRATUM = 0.90     # cap-acceptability, per stratum
PRECISION_LIMITED_CEILING = 0.05    # pooled, on validation

# --------------------------------------------------------------- budget
PILOT2_CPU_CAP_HOURS = 3.0

# ------------------------------------------------- cost acceptance (frozen)
FUTURE_TOTAL_CAP_HOURS = 60.0
FUTURE_PER_CONFIG_CAP_HOURS = 40.0
REQUIRED_RESERVE = 0.25             # projections must sit 25 % below the caps
ACCEPT_TOTAL_HOURS = FUTURE_TOTAL_CAP_HOURS * (1 - REQUIRED_RESERVE)        # 45.0
ACCEPT_PER_CONFIG_HOURS = FUTURE_PER_CONFIG_CAP_HOURS * (1 - REQUIRED_RESERVE)  # 30.0

#: Immutable P4X cost basis (cost metadata only, never scientific evidence).
P4X_TOTAL_CPU_HOURS = 24.749349116539157
P4X_MAX_CONFIG_CPU_HOURS = 18.59941603055556


def pool_limit(stratum: Stratum) -> int:
    """Hard per-replicate block ceiling.  Exceeding it is a STOP.

    It equals the reference plus the largest cap in the frozen grid, so the
    rule can always run to the point where the largest cap would refuse it,
    and never one block further.
    """
    return stratum.b_ref + cap_blocks(stratum, MAX_CAP_MULTIPLIER)


def cap_blocks(stratum: Stratum, multiplier: float) -> int:
    """The frozen cap, an INTEGER per (stratum, multiplier).

    Expressed against the stratum's frozen NOMINAL B1, not against whatever
    stage 1 happens to realise, because in production a checkpoint freezes the
    cap before the run.  A route whose realised stage-1 requirement already
    exceeds it is PRECISION_LIMITED from projected cost alone, before a single
    block executes -- which is the inherited P4X semantics verbatim.
    """
    import math
    return int(math.ceil(multiplier * stratum.b1))


def reachable_addresses() -> list:
    """Every logical address the frozen Pilot-2 design will actually touch.

    Enumerated exactly -- cells x their own strata x namespaces x their own
    replicate ranges -- so the section-20 collision audit covers the whole
    domain rather than a sample of it.
    """
    from .addressing import Address

    out = []
    for name in CELLS:
        primary = name in PRIMARY_CELLS
        rd = R_DESIGN if primary else R_DESIGN_ROBUSTNESS
        rv = R_VALIDATION if primary else R_VALIDATION_ROBUSTNESS
        for sk in CELL_STRATA[name]:
            out.append(Address(name, sk, "calibration", 0))
            for i in range(rd):
                out.append(Address(name, sk, "reference", DESIGN_BASE + i))
                out.append(Address(name, sk, "design", DESIGN_BASE + i))
            for i in range(rv):
                out.append(Address(name, sk, "reference", VALIDATION_BASE + i))
                out.append(Address(name, sk, "validation", VALIDATION_BASE + i))
    return out
