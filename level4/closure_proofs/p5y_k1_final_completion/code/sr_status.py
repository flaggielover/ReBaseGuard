"""Evidence-based assessment of the SR raw-variable DAG.

This module does not implement SR. It records, with checkable evidence, exactly
what exists and exactly what is missing, so the gap is a measured fact rather
than an assertion.

WHAT EXISTS
-----------
`p5y_k1_task1r_budget_harness` certifies ONE object class, on ONE patch, at ONE
drift, with a PASS verdict:

    DETECTOR, OBJECT = "SR", "F_0"
    PATCH, GRID      = (17, 11), 64
    E_NUM, E_DEN     = 1, 4            i.e. e = 1/4 only
    D, Z             = 11, 20
    runtime          = 12.72 CPU-s, 48.6 MiB peak

`p5y_k1_sr_backend_cost_audit` provides the optimized cancellation-preserving
backend and its timing primitives, verified coefficient-overlap-equivalent to
the reference harness.

WHAT IS MISSING
---------------
The frozen universe needs, for SR, 28 obligations on each of 316 cells plus the
far-field unit: 8,850 of the 17,978 total. Against that, Task1R supplies one
object class at one drift on one of 3,994 live patches.

Concretely absent:
  * h_1..h_4 and S_1..S_4 for SR (the source recursion) at any drift
  * F_1..F_4 (needs S_r, which does not exist)
  * dF_0..dF_4 (the derivative resolvent system)
  * the order-2 chain h'', S'', H_r and the finite powers W_(r,j) at any order
  * whole-cell (uniform-in-e) envelopes, without which no M_R2 exists
  * the exact all-m interval assembly for m in {1,2,3,5}
  * generalisation from patch (17,11) to all 3,994 live patches
  * generalisation from e = 1/4 to all 316 frozen cells

ARCHITECTURAL NOTE (why this is not a small port of the CUSUM code)
-------------------------------------------------------------------
The validated CUSUM path is built on `_kernel_polynomials`, whose geometry is
hard-wired to the CUSUM state square (the 11/2 and 1/2 constants) and to a
recentred Hermite expansion of `phi(z+e)`. SR is a different formulation
entirely: state `y = log(1+R)`, threshold `b = log(1+A)`, two charts, and a
softplus composition certified through bivariate Taylor models in
`(alpha, zeta)` with panel-wise Gaussian moments. The two share the Arb backend
and the frozen error algebra, and essentially nothing else. The frozen
CHECKPOINT lists `complete_SR_raw_DAG` first among its implementation
dependencies for this reason.

CLASSIFICATION
--------------
    SR_IMPLEMENTATION = ABSENT       failure class: IMPLEMENTATION_INCOMPLETE
Not a scientific failure, not a certificate looseness, not a resource limit.
"""
from __future__ import annotations

import json

import base                                                     # noqa: F401

import spec                                                     # noqa: E402

TASK1R = base.TASK1R
AUDIT = base.ROOT / "level4/closure_proofs/p5y_k1_sr_backend_cost_audit"

REQUIRED_OBJECTS = ([f"h_{j}" for j in range(1, 5)]
                    + [f"S_{r}" for r in range(5)]
                    + [f"F_{r}" for r in range(5)]
                    + [f"dF_{r}" for r in range(5)])
IMPLEMENTED_OBJECTS = ["F_0"]


def task1r_evidence() -> dict:
    r = json.loads((TASK1R / "results/task1r_F0_qualification.json").read_text())
    import re
    src = (TASK1R / "code/harness.py").read_text()
    def const(name):
        m = re.search(rf"^{name}\s*=\s*(.+)$", src, re.M)
        return m.group(1).split("#")[0].strip() if m else None
    return {
        "verdict": r["TASK1R_VERDICT"],
        "detector_object": const("DETECTOR, OBJECT"),
        "patch_grid": const("PATCH, GRID"),
        "drift": const("E_NUM, E_DEN"),
        "D": r["D"], "Z": r["Z"],
        "n_panels_on_that_patch": r["p1"]["n_panels"],
        "cpu_seconds": r["runtime"]["cpu_seconds"],
        "peak_rss_mib": r["runtime"]["peak_rss_mib"],
        "objects_certified": IMPLEMENTED_OBJECTS,
    }


def coverage() -> dict:
    n_sr = spec.COUNTS["SR"]
    per_cell = (spec.OBJECTS_PER_CELL + spec.DEPENDENCY_BUNDLES_PER_CELL
                + spec.CURVATURE_BUNDLES_PER_CELL + spec.ASSEMBLY_UNITS_PER_CELL)
    sr_obligations = per_cell * n_sr + 1        # + the SR far-field unit
    return {
        "sr_cells": n_sr,
        "obligations_per_cell": per_cell,
        "sr_obligations_total": sr_obligations,
        "total_universe": spec.TOTAL_UNITS,
        "sr_share_of_universe": sr_obligations / spec.TOTAL_UNITS,
        "live_patches": 3994,
        "objects_required_per_cell": len(REQUIRED_OBJECTS),
        "object_classes_implemented": len(IMPLEMENTED_OBJECTS),
        "drifts_implemented": 1,
        "patches_implemented": 1,
    }


def report() -> dict:
    cov = coverage()
    return {
        "schema": "k1.final.sr-status.v1",
        "SR_IMPLEMENTATION": "ABSENT",
        "SR_M_R2": "ABSENT",
        "SR_ALL_M": "ABSENT",
        "failure_class": "IMPLEMENTATION_INCOMPLETE",
        "not_a_scientific_failure": True,
        "task1r_evidence": task1r_evidence(),
        "coverage": cov,
        "missing": [
            "h_1..h_4 and S_1..S_4 for SR at any drift",
            "F_1..F_4 (require S_r, absent)",
            "dF_0..dF_4 (derivative resolvent system)",
            "order-2 chain h'', S'', H_r and finite powers W_(r,j)",
            "whole-cell uniform-in-e envelopes (no M_R2 without them)",
            "exact all-m interval assembly for m in {1,2,3,5}",
            "generalisation from patch (17,11) to all 3994 live patches",
            "generalisation from e = 1/4 to all 316 frozen cells",
        ],
        "architectural_note": (
            "the validated CUSUM path is hard-wired to the CUSUM state square "
            "and a recentred Hermite expansion; SR is a softplus/Taylor-model "
            "formulation on two charts with panel Gaussian moments. They share "
            "the Arb backend and the frozen error algebra and little else."),
        "consequence": (
            "SR representative certification, SR M_R2, SR all-m assembly and "
            "any SR cost measurement are all blocked; the SR half of the frozen "
            f"scope ({cov['sr_obligations_total']} of {spec.TOTAL_UNITS} "
            "obligations) is undischarged."),
    }
