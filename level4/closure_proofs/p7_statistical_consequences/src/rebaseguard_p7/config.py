"""Frozen P7 configuration: imported P3 boundaries, grids and seed family.

Every number in ``P3_BOUNDARY`` is read at run time from the CLOSED Priority-3
artifact ``results/boundary_table.json``.  Nothing is transcribed by hand.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
P3 = ROOT / "level4" / "closure_proofs" / "m_rho_stability_priority3"
P7 = ROOT / "level4" / "closure_proofs" / "p7_statistical_consequences"
RESULTS = P7 / "results"
FIGURES = P7 / "figures"

SEED_FAMILY = 20260831          # P7 root seed; distinct from Stage D's 20261001

#: fixed integer codes for seed derivation.  Python's ``hash`` of a str is
#: salted per process (PYTHONHASHSEED), so it must never appear in a seed.
DETECTOR_CODE = {"cusum": 11, "sr": 13}

M_GRID = (1, 2, 3, 5)           # exactly the windows Priority 3 supports
DETECTORS = ("cusum", "sr")

#: reuse fractions expressed as multiples of the P3 critical fraction rho_c
RHO_OVER_RHOC = (0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2.0, 4.0)
#: absolute reuse anchors, independent of rho_c (includes both baselines)
RHO_ABSOLUTE = (0.0, 0.25, 0.5, 0.75, 1.0)

SHIFTS = (0.5, 1.0)
FA_HORIZONS = (50, 100, 200)


def load_p3_boundaries() -> dict:
    """Return ``{(detector, m): row}`` for the two frozen Gaussian layers."""
    table = json.loads((P3 / "results" / "boundary_table.json").read_text())
    out = {}
    for row in table["rows"]:
        if not row["layer"].startswith("GAUSSIAN"):
            continue
        out[(row["detector_short"].lower(), int(row["m"]))] = row
    return out


def rho_grid(detector: str, m: int, boundaries: dict) -> list[float]:
    """Sorted, de-duplicated reuse grid for one cell, clipped to [0, 1]."""
    rc = boundaries[(detector, m)]["rho_crit"]
    vals = {round(float(v), 10) for v in RHO_ABSOLUTE}
    for f in RHO_OVER_RHOC:
        v = f * rc
        if 0.0 <= v <= 1.0:
            vals.add(round(float(v), 10))
    return sorted(vals)
