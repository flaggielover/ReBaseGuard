"""Frozen P8 configuration.

Every inherited constant is read at run time from the artifact that owns it.
The only hand-written numbers here are P8's own grids and seed namespace, all
declared in ``EXPERIMENT_PROTOCOL.md`` before any production cell was run.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
P3 = ROOT / "level4" / "closure_proofs" / "m_rho_stability_priority3"
P4 = ROOT / "level4" / "closure_proofs" / "location_family"
P7 = ROOT / "level4" / "closure_proofs" / "p7_statistical_consequences"
STAGE_D = ROOT / "level4" / "stage_d"
P8 = ROOT / "level4" / "closure_proofs" / "p8_model_class_robustness"
RESULTS = P8 / "results"
FIGURES = P8 / "figures"   # declared for scope tests; P8 produces no figures

#: P8 entropy namespace.  Distinct from Stage D (20261001), P7 (20260831),
#: P6R2b (0x50365232_42435250).  Never varied by cell, family or detector.
SEED_NAMESPACE = 0x50385F4D_43520001          # "P8_MCR" v1

#: windows.  {1,2,3,5} are exactly the windows P3 supports; {10,20} are used
#: for the window law only and are labelled EXTRAPOLATION_BEYOND_P3.
M_GRID = (1, 2, 3, 5, 10, 20)
M_P3_SUPPORTED = (1, 2, 3, 5)
#: lag depth for the selection profile gamma_r
LAG_DEPTH = 20

DETECTORS = ("cusum", "sr")
#: fixed integer codes.  Python's ``hash`` of a str is salted per process, so it
#: must never appear in a seed address.
DETECTOR_CODE = {"cusum": 11, "sr": 13}
FAMILY_CODE = {"gaussian": 101, "t10": 103, "t5": 107, "t3": 109,
               "contam0.05": 113, "contam0.1": 127}

FAMILIES = ("gaussian", "t10", "t5", "t3", "contam0.05", "contam0.1")

#: families whose Gamma integrand has a divergent third absolute moment, so no
#: Berry-Esseen rate is available and the sample variance itself has infinite
#: variance.  Declared BEFORE any P8 production run; see EXPERIMENT_PROTOCOL.md.
MOMENT_MARGINAL = ("t3",)

SHIFTS = (0.5, 1.0, 2.0)
RAMP_SLOPES = (0.02, 0.05)


def stage_d_cusum_thresholds() -> dict[str, float]:
    """Family-specific frozen CUSUM thresholds, read from Stage D D3."""
    d = json.loads((STAGE_D / "results" / "d3_nongaussian.json").read_text())
    return {r["family"]: float(r["threshold"]) for r in d["rows"]}


def stage_d_target_arl0() -> float:
    d = json.loads((STAGE_D / "results" / "d3_nongaussian.json").read_text())
    return float(d["target_arl0"])


def stage_d_historical_arl() -> dict[str, float]:
    d = json.loads((STAGE_D / "results" / "d3_nongaussian.json").read_text())
    return {r["family"]: float(r["arl0_measured"]) for r in d["rows"]}


def stage_d_gamma_psi() -> dict:
    """Stage-D D3 Gamma_psi (a DIFFERENT estimand; see the dependency audit)."""
    d = json.loads((STAGE_D / "results" / "d3_nongaussian.json").read_text())
    return {r["family"]: {int(p["m"]): (p["gamma_psi"], p["se"])
                          for p in r["per_m"]} for r in d["rows"]}


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
            out[row["family"]] = {k: (float(v) if v not in ("True", "False")
                                      else v == "True")
                                 for k, v in row.items() if k != "family"}
    return out
