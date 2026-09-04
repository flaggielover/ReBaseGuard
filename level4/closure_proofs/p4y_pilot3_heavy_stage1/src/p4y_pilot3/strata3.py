"""Frozen Pilot-3 cells, strata, candidate grids, thresholds and budget.

The heavy-tail class is taken from PRE-EXISTING frozen family metadata, never
from an observed Pilot-3 failure.  P4X's `heavy_tail_policy` records
`only_family_requiring_alpha_below_2 = "t1p5"`, measured alpha 1.471-1.528 for
t1p5 and a minimum of 2.695 for every other family.  Mechanically verified
against `checkpoint_a.json`:

    48 (configuration, route) strata
     8 with frozen heavy_tailed = True   -- all eight are t1p5
    40 ordinary
    the heavy set EQUALS the set that needed stage-1 sizing

so the class is decided by family tail index, decided before P4X ran, and the
8/40 split is the real production mixture rather than a pilot artefact.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_P1 = Path(__file__).resolve().parents[3] / "p4y_precision_governance_pilot"
if str(_P1 / "src") not in sys.path:
    sys.path.insert(0, str(_P1 / "src"))

from p4y_pilot.blocks import Cell  # noqa: E402

from .addressing3 import register  # noqa: E402

# ---------------------------------------------------------------- inherited
R_STAR = 0.010823
R_STAR_EXACT = 0.010823062977345114
FROZEN_ACCURACY_CRITERION = 0.03

KAPPA_K1 = 0.5                       # LEADING candidate (Pilot-2 evidence)
KAPPA_K2 = 0.3197278911564626        # CONTROL
KAPPA_CANDIDATES = {"K1_0.5": KAPPA_K1, "K2_0.3197": KAPPA_K2}

PRODUCTION_BLOCK_HEAVY = 250_000
M_GRID = (1, 2, 3, 5)
FD_STEPS = (0.05, 0.025)

# --------------------------------------------------- production mixture
N_STRATA_TOTAL = 48
N_HEAVY_STRATA = 8
N_ORDINARY_STRATA = 40
HEAVY_FAMILY = "t1p5"

# ------------------------------------------------------- candidate grids
#: Minimum heavy-tail reference block count.  4 is the HISTORICAL value and is
#: carried only as a baseline control, never as a selectable production rule.
BMIN_CANDIDATES = (4, 16, 32, 64, 128)
BMIN_BASELINE = 4
BMIN_SELECTABLE = (16, 32, 64, 128)

CAP_MULTIPLIERS = (1.25, 1.5, 2.0, 3.0)
MAX_CAP_MULTIPLIER = max(CAP_MULTIPLIERS)

#: An allocation this far above the stratum's true requirement is refused
#: before stage 1 and recorded INVALID.  It bounds pilot cost and counts
#: AGAINST the candidate, never in its favour.
ABS_CEILING_MULTIPLE = 40

# ------------------------------------------------------------- strata
@dataclass(frozen=True, slots=True)
class Stratum:
    key: str
    b_req: int          # true blocks needed to reach the target
    b_ref: int          # reference blocks (Bmin for heavy; historical for ordinary)
    heavy: bool
    weight: int         # production strata this pilot stratum stands for
    provenance: str


#: Four of P4X's eight actual heavy stage-1 allocations, spanning the range and
#: including both cost-dominant configurations.  Each stands for two of the
#: eight production heavy strata.
STRATA: tuple[Stratum, ...] = (
    Stratum("S59", 59, 0, True, 2,
            "frozen/sr@520.886/t1p5 route A, B1 = 58.7 -- the minimum heavy allocation"),
    Stratum("S151", 151, 0, True, 2,
            "reduced/sr@20/t1p5 route B, B1 = 151.1 -- lower-middle"),
    Stratum("S215", 215, 0, True, 2,
            "frozen/cusum@5/t1p5 route B, B1 = 215.2 -- consumed 18.60 of "
            "P4X's 24.75 CPU-hours, the cost-dominant configuration"),
    Stratum("S1784", 1784, 0, True, 2,
            "frozen/sr@520.886/t1p5 route B, B1 = 1783.6 -- the maximum"),
    Stratum("ORD", 160, 160, False, 40,
            "the median ordinary stage-1 allocation; finite-variance control, "
            "which the heavy-tail rule must NOT penalise"),
)

HEAVY_STRATA = tuple(s.key for s in STRATA if s.heavy)
ORDINARY_STRATA = tuple(s.key for s in STRATA if not s.heavy)

# --------------------------------------------------------------- cells
CELLS: dict[str, Cell] = {
    "H": Cell(key="H", layer="reduced", kind="cusum", threshold=2.0,
              family="t1p5", route="route_a", max_steps=60_000,
              block_size=5_000, heavy=True),
    "O": Cell(key="O", layer="reduced", kind="cusum", threshold=2.0,
              family="gaussian", route="route_a", max_steps=60_000,
              block_size=1_000, heavy=False),
    "HB": Cell(key="HB", layer="reduced", kind="cusum", threshold=2.0,
               family="t1p5", route="route_b", max_steps=60_000,
               block_size=10_000, heavy=True),
}
CELL_STRATA = {"H": HEAVY_STRATA, "O": ORDINARY_STRATA, "HB": ("S59",)}
PRIMARY_CELLS = ("H", "O")
ROBUSTNESS_CELLS = ("HB",)

register(cells={"H": 0, "O": 1, "HB": 2},
         strata={s.key: i for i, s in enumerate(STRATA)})

# ------------------------------------------------------------ replication
R_DESIGN = 20
R_VALIDATION = 59
R_DESIGN_ROBUSTNESS = 12
R_VALIDATION_ROBUSTNESS = 29
DESIGN_BASE = 0
VALIDATION_BASE = 50_000

#: The high-quality independent benchmark for the true reference precision.
#: 8000 blocks gives the block SD a relative standard error of
#: 1/sqrt(2*(8000-1)) = 0.79 %, which is small against the 25-60 % effects
#: this pilot must resolve.  Documented rather than assumed.
BENCHMARK_BLOCKS = 8_000
BENCHMARK_BLOCKS_ROBUSTNESS = 3_000
MIN_BLOCK_MEAN_ALPHA = 2.5

# ----------------------------------------------------------- statistics
DELTA = 0.95                        # valid-disposition target
BETA = 0.05                         # one-sided confidence
ATTAINMENT_FLOOR_MIXTURE = 0.95     # production-mixture weighted
PRECISION_LIMITED_CEILING = 0.05    # production-mixture weighted
HEAVY_STRATUM_ATTAINMENT_FLOOR = 0.90     # EVERY heavy stratum
HEAVY_STRATUM_PL_CEILING = 0.10           # EVERY heavy stratum

# --------------------------------------------------------------- budget
PILOT3_CPU_CAP_HOURS = 3.0

# --------------------------------------------- cost acceptance (frozen)
FUTURE_TOTAL_CAP_HOURS = 60.0
FUTURE_PER_CONFIG_CAP_HOURS = 40.0
REQUIRED_RESERVE = 0.25
ACCEPT_TOTAL_HOURS = FUTURE_TOTAL_CAP_HOURS * (1 - REQUIRED_RESERVE)        # 45.0
ACCEPT_PER_CONFIG_HOURS = FUTURE_PER_CONFIG_CAP_HOURS * (1 - REQUIRED_RESERVE)  # 30.0

# ------------------------------------------------- frozen selection order
#: Applied to DESIGN results, among candidates satisfying every frozen
#: criterion.  Fixed before execution.
TIE_BREAK = ("conservative_total_cpu", "conservative_max_config_cpu",
             "precision_limited_rate", "rule_simplicity", "bmin")


def stratum(key: str) -> Stratum:
    return next(s for s in STRATA if s.key == key)


def reference_blocks(s: Stratum, bmin: int) -> int:
    """Heavy strata take the enforced minimum; ordinary strata are untouched.

    Brief section 18: the heavy-tail reference inflation applies ONLY to the
    frozen tail class.  Globally penalising all 48 strata to fix 8 is exactly
    what this must not do.
    """
    return bmin if s.heavy else s.b_ref


def abs_ceiling(s: Stratum) -> int:
    return ABS_CEILING_MULTIPLE * s.b_req


def reachable_addresses() -> list:
    from .addressing3 import Address

    out = []
    for name in CELLS:
        primary = name in PRIMARY_CELLS
        rd = R_DESIGN if primary else R_DESIGN_ROBUSTNESS
        rv = R_VALIDATION if primary else R_VALIDATION_ROBUSTNESS
        for sk in CELL_STRATA[name]:
            out.append(Address(name, sk, "benchmark", 0))
            for i in range(rd):
                out.append(Address(name, sk, "reference", DESIGN_BASE + i))
                out.append(Address(name, sk, "design", DESIGN_BASE + i))
            for i in range(rv):
                out.append(Address(name, sk, "reference", VALIDATION_BASE + i))
                out.append(Address(name, sk, "validation", VALIDATION_BASE + i))
    return out
