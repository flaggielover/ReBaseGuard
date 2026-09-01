"""Calibration diagnostics -- the audit the adjudication required.

Reads the FROZEN P6 calibration artifact (``p6_safe_rebaselining/results/
calibration.json``) and reports, per ``(detector, m, k)`` cell and without
softening:

* the convergence flag actually recorded, and the iteration count reached;
* the number of observations behind ``s1`` (the truncated-window variance);
* whether the ``S_FLOOR = 1e-2`` variance floor is active for that cell;
* whether the ``rho_max = 0.95`` cap can bind for that cell;
* whether the final large-pass refit was followed by another fixed-point
  update -- it was **not**, and the recorded ``drift`` measures exactly that
  one-step-off gap.

The P6R campaign does **not** re-derive the constants.  They are the method that
was adjudicated, they were fitted on TUNE at ``Delta = 0``, and re-deriving them
would change the object under test.  They are audited, and cells whose ``s1``
rests on too few observations get the predeclared sensitivity check of
``experiments/precommit_freeze.py``.
"""
from __future__ import annotations

import json
from pathlib import Path

#: cells whose ``s1`` sample is below this get the predeclared sensitivity check
S1_SPARSE_THRESHOLD = 50
#: the structural constants of the method, restated for the audit
S_FLOOR = 1e-2
RHO_MAX = 0.95


def p6_calibration_path() -> Path:
    return (Path(__file__).resolve().parents[3]
            / "p6_safe_rebaselining" / "results" / "calibration.json")


def audit_calibration(path: Path | None = None) -> dict:
    """Per-cell calibration diagnostics.  Reports what is there, not what is wished."""
    cal = json.loads((path or p6_calibration_path()).read_text())
    cells = {}
    for key, v in cal.items():
        f, fp = v["final"], v["fixed_point"]
        n_final = int(v["n_final"])
        frac = float(v["frac_truncated"])
        n_s1 = int(round(frac * n_final))
        floor_active = bool(min(f["s0"], f["s1"]) <= S_FLOOR)
        cells[key] = {
            "detector": f["detector"], "m": int(f["m"]), "k": int(f["k"]),
            "converged": bool(f["converged"]),
            "iterations_reached": int(fp["iterations"]),
            "g0": f["g0"], "g1": f["g1"], "s0": f["s0"], "s1": f["s1"],
            "r2": f["r2"],
            "n_calibration_cycles": n_final,
            "frac_truncated_windows": frac,
            "n_obs_behind_s1": n_s1,
            "s1_is_fallback_equal_to_s0": bool(abs(f["s1"] - f["s0"]) < 1e-12),
            "s1_sparse": bool(n_s1 < S1_SPARSE_THRESHOLD),
            "variance_floor_1e-2_active": floor_active,
            "rho_max_can_bind": bool(
                (1.0 / f["k"]) / (max(min(f["s0"], f["s1"]), S_FLOOR)
                                  + 1.0 / f["k"]) >= RHO_MAX),
            "final_refit_followed_by_another_fixed_point_update": False,
            "drift_fixed_point_to_final": v["drift"],
        }
    n = len(cells)
    conv = sum(c["converged"] for c in cells.values())
    sparse = [k for k, c in cells.items() if c["s1_sparse"]]
    return {
        "source": str((path or p6_calibration_path())),
        "cells": cells,
        "summary": {
            "n_cells": n,
            "n_converged": conv,
            "all_converged": bool(conv == n),
            "non_converged_cells": [k for k, c in cells.items()
                                    if not c["converged"]],
            "s1_sparse_cells": sparse,
            "s1_fallback_cells": [k for k, c in cells.items()
                                  if c["s1_is_fallback_equal_to_s0"]],
            "variance_floor_active_anywhere": any(
                c["variance_floor_1e-2_active"] for c in cells.values()),
            "rho_max_can_bind_anywhere": any(
                c["rho_max_can_bind"] for c in cells.values()),
            "final_refit_is_a_verified_fixed_point": False,
            "note": (
                "The shipped constants are a refit under the policy built from "
                "the fixed-point iterate, NOT a verified fixed point of "
                "themselves; no further update was run after the large final "
                "pass. The recorded drift measures that one-step-off gap."),
        },
    }
