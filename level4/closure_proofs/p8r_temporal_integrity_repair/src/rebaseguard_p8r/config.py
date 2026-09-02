"""Frozen P8R configuration.

Every inherited constant is read at run time from the artifact that owns it.
The only hand-written numbers here are P8R's own grids, budgets and seed
namespace, all declared in ``FROZEN_PROTOCOL.md`` and digested into
``PROTOCOL_DIGEST.json`` at the temporal anchor, before any production cell was
generated.

**Nothing in this file may change after the anchor commit.**  ``I3`` (source
digest) and ``I7`` (no result-driven threshold change) both check it.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
P3 = ROOT / "level4" / "closure_proofs" / "m_rho_stability_priority3"
P4 = ROOT / "level4" / "closure_proofs" / "location_family"
P7 = ROOT / "level4" / "closure_proofs" / "p7_statistical_consequences"
P8 = ROOT / "level4" / "closure_proofs" / "p8_model_class_robustness"
STAGE_D = ROOT / "level4" / "stage_d"
P8R = ROOT / "level4" / "closure_proofs" / "p8r_temporal_integrity_repair"
RESULTS = P8R / "results"

#: P8R entropy namespace.  Distinct from Stage D (20261001), P7 (20260831),
#: P6R2b (0x50365232_42435250) and **P8 itself** (0x50385F4D_43520001), so P8R
#: is an independent seed realisation of the same estimands rather than a
#: replay of P8's field.  Never varied by cell, family, detector or class:
#: class separation is carried by the experiment tag (see ``addressing.py``).
SEED_NAMESPACE = 0x50385F52_4D435201          # "P8R_MCR" v1

# ---------------------------------------------------------------------------
# factors
# ---------------------------------------------------------------------------
M_GRID = (1, 2, 3, 5, 10, 20)
M_P3_SUPPORTED = (1, 2, 3, 5)
M_CHAIN = (1, 5)
LAG_DEPTH = 20

DETECTORS = ("cusum", "sr")
FAMILIES = ("gaussian", "t10", "t5", "t3", "contam0.05", "contam0.1")

#: fixed integer codes.  Python's ``hash`` of a str is salted per process, so it
#: must never appear in a seed address.
DETECTOR_CODE = {"cusum": 11, "sr": 13}
FAMILY_CODE = {"gaussian": 101, "t10": 103, "t5": 107, "t3": 109,
               "contam0.05": 113, "contam0.1": 127}

#: families whose Gamma integrand has a divergent third absolute moment, so no
#: Berry-Esseen rate is available and the sample variance itself has infinite
#: variance.  Declared BEFORE any P8R production run.
MOMENT_MARGINAL = ("t3",)

#: windows outside P3's support; reported, never gated.
EXTRAPOLATION_M = (10, 20)

SHIFTS = (0.5, 1.0, 2.0)
RAMP_SLOPES = (0.02, 0.05)

#: P7's reuse ladder, verbatim, so P7's boundary criterion applies literally.
RHO_MULTIPLIERS = (0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2.0, 4.0)
RHO_ABSOLUTE = (0.0, 0.25, 0.5, 0.75, 1.0)

# ---------------------------------------------------------------------------
# frozen calibration budgets  (CALIBRATION_PLAN.md; the single authoritative
# statement -- the P8 defect was exactly a disagreement between the declared
# and the executed values of these numbers)
# ---------------------------------------------------------------------------
ROWS_PER_BLOCK = 4096                     # mirrors primitives.ROWS_PER_BLOCK

CAL_S1_ROW_BLOCKS = 64                    # 262,144 cycles per S1 evaluation
CAL_S1_ITERATIONS = 6                     # exactly six, no early stop
CAL_S2_ROW_BLOCKS = 200                   # 819,200 cycles per S2 evaluation
CAL_S2_ITERATIONS = 3                     # exactly three, no early stop
CAL_VERIFY_ROW_BLOCKS = 300               # 1,228,800 cycles, held out
CAL_TOLERANCE = 0.005                     # G2 / S5 acceptance, relative
CAL_CLIP_FACTOR = 4.0                     # per-step bound on A's multiplier
CAL_DAMP_SWITCH = 0.002                   # rel error above which p = 1.0;
#: below the switch the residual is at the evaluation's own noise floor
#: (~0.11% at the S2 budget), so a full proportional step would chase
#: noise.  Above it, full correction is both safe and much faster.
CAL_DAMP_EXPONENT = 0.6                   # p below the switch
#: bounds on the log-log secant slope ``beta`` in ``ARL ~ A^beta``.  Measured
#: locally it is about 0.47 for the contaminated families and near 1 for the
#: Gaussian; the bounds only stop a noise-driven slope from producing a wild
#: step, and the step is clipped again by ``CAL_CLIP_FACTOR``.
CAL_BETA_MIN = 0.2
CAL_BETA_MAX = 2.0

#: batch address regions, disjoint within CAL_SEARCH by construction
CAL_S1_BATCH0 = 1_000
CAL_S2_BATCH0 = 2_000
CAL_RETRY_BATCH0 = 3_000
CAL_VERIFY_1_BATCH = 7
CAL_VERIFY_2_BATCH = 11

# ---------------------------------------------------------------------------
# frozen production budgets  (PRODUCTION_PLAN.md)
# ---------------------------------------------------------------------------
E1_BATCHES = 20
E1_BATCH0 = 0
E1_ROW_BLOCKS = 50                        # 4,096,000 cycles per (D,f) cell
E5_BATCHES = 20
E5_BATCH0 = 100                           # independent batch family
E5_ROW_BLOCKS = 50

ARL0_CHECK_ROW_BLOCKS = 150               # 614,400 cycles per (D,f) cell

E3_REPLICATES = 2_000
E3_CYCLES = 70
E3_BURN_IN = 20

E4_REPLICATES = 6_000
E4_CYCLES = 24
E4_SHIFT_CYCLE = 20

E6_REPRO_BATCHES = 8                      # independent-implementation check
E6_REPRO_PATHS = 32_768                   # 262,144 cycles per checked cell

#: minimum tail events below which a delay tail statistic is labelled
#: INSUFFICIENT_TAIL_EVENTS rather than reported as an estimate.
TAIL_EVENT_FLOOR = 200

# ---------------------------------------------------------------------------
# frozen statistical constants  (STATISTICAL_ANALYSIS_PLAN.md)
# ---------------------------------------------------------------------------
Z95 = 1.959963984540054
COMBINED_Z_TOLERANCE = 3.0                # reproduction agreement bound
BH_Q = 0.10                               # descriptive companion only

# ---------------------------------------------------------------------------
# frozen scientific decision thresholds  (FROZEN_GATES.md)
# ---------------------------------------------------------------------------
S6_LOWER_BOUND = 2.0                      # regime survival, lower 95% > 2
S7_SPREAD_MAX = 0.10                      # window-law spread max/min - 1
S7D_RESIDUAL_MAX = 0.03                   # detector invariance of K
S7F_SPREAD_MAX = 0.10                     # family invariance of K per detector
#: The decomposition Gamma_A(m) = (1/m) sum_r gamma_r + R_m is EXACT algebra,
#: not a statistical claim: both sides are the same expectation summed in a
#: different order, so the residual is pure floating-point noise (order 1e-16)
#: and so is its batch standard error.  Gating on |residual| <= k x SE would
#: therefore compare noise to noise and return an essentially arbitrary O(1)
#: ratio.  P8R gates the absolute residual instead, which is the stricter and
#: the meaningful test.
S8_ABS_TOL = 1e-9                         # decomposition identity, absolute
S9_EXACT_TOL = 1e-12                      # convention algebraic identity
S10_FAMILIES_REQUIRED = 5                 # of 6, for P7 boundary transfer
S11_ARL_FRACTION = 0.50                   # operational degradation
S13_CELL_FRACTION = 0.90                  # seed sensitivity, all cells
S13_NON_T3_FRACTION = 0.95                # seed sensitivity, non-t3 cells
S3_ARL0_REL_MAX = 0.01                    # CUSUM ARL0 at frozen thresholds
S4_EZPSI_TOL = 1e-4
S4_EPSI_TOL = 1e-8
S4_FISHER_TOL = 1e-6
S2_SCORE_TOL = 1e-12                      # P4 score agreement on a fixed grid
#: the independent reimplementation checks 18 cells at 3 combined SE.  Under
#: agreement the expected number of exceedances is about 0.05, but allowing
#: exactly one absorbs ordinary multiplicity without absorbing a real defect.
S17_MAX_OUTLIERS = 1


# ---------------------------------------------------------------------------
# inherited artifacts, read at run time (never copied into this file)
# ---------------------------------------------------------------------------
def stage_d_cusum_thresholds() -> dict[str, float]:
    """Family-specific frozen CUSUM thresholds, read from Stage-D D3."""
    d = json.loads((STAGE_D / "results" / "d3_nongaussian.json").read_text())
    return {r["family"]: float(r["threshold"]) for r in d["rows"]}


def stage_d_target_arl0() -> float:
    d = json.loads((STAGE_D / "results" / "d3_nongaussian.json").read_text())
    return float(d["target_arl0"])


def stage_d_psi_prime() -> dict[str, float]:
    d = json.loads((STAGE_D / "results" / "d3_nongaussian.json").read_text())
    return {r["family"]: float(r["E_psi_prime"]) for r in d["rows"]}


def p3_boundaries() -> dict:
    """``{(detector, m): row}`` for the two frozen Gaussian layers."""
    table = json.loads((P3 / "results" / "boundary_table.json").read_text())
    out = {}
    for row in table["rows"]:
        if not row["layer"].startswith("GAUSSIAN"):
            continue
        out[(row["detector_short"].lower(), int(row["m"]))] = row
    return out


def p4_correspondence() -> dict[str, dict]:
    """P4's measured ``Gamma_f`` per family (m=1, CUSUM).  PARTIAL_ONLY."""
    import csv
    out = {}
    with (P4 / "results" / "correspondence.csv").open() as fh:
        for row in csv.DictReader(fh):
            out[row["family"]] = {
                k: (float(v) if v not in ("True", "False") else v == "True")
                for k, v in row.items() if k != "family"}
    return out
