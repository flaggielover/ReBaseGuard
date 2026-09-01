"""Aggregate the E1 stopped-cycle cells into the P8 Gamma / rho_c matrix.

Batch means are the statistical unit (protocol section 5).  Every derived
quantity carries the batch-means standard error, and `K` -- the window scaling
of the critical reuse fraction -- carries a delta-method SE that uses the
*empirical batch covariance* between `Gamma_A(m)` and `Gamma_A(1)`, since the
two are measured on the same cycles and are strongly positively correlated.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8.analysis import Z95, rho_c_from_gamma           # noqa: E402
from rebaseguard_p8.config import (                                 # noqa: E402
    DETECTORS, FAMILIES, LAG_DEPTH, M_GRID, MOMENT_MARGINAL, RESULTS)


def load_cell(detector: str, family: str, tag: str = "E1") -> dict | None:
    p = RESULTS / "gamma" / f"{tag}_{detector}_{family}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _bm(cell, path):
    """Per-batch values of a nested key path, as an array."""
    out = []
    for b in cell["batches"]:
        v = b
        for k in path:
            v = v[k]
        out.append(float(v))
    return np.array(out)


def cell_summary(cell: dict) -> dict:
    nb = cell["n_batches"]
    g1 = _bm(cell, ("gamma_A", "1"))
    rows = {}
    for m in cell["m_grid"]:
        gA = _bm(cell, ("gamma_A", str(m)))
        gB = _bm(cell, ("gamma_B", str(m)))
        gN = _bm(cell, ("gamma_naive", str(m)))
        gP = _bm(cell, ("gamma_psipsi", str(m)))
        Rm = _bm(cell, ("R_m", str(m)))
        pt = _bm(cell, ("p_tau_lt_m", str(m)))
        mu, se = float(gA.mean()), float(gA.std(ddof=1) / np.sqrt(nb))
        info = rho_c_from_gamma(mu, se)
        # K = (Gamma(1)-1)/(Gamma(m)-1), delta method with batch covariance
        a, b = g1 - 1.0, gA - 1.0
        Kb = a / b
        K = float(a.mean() / b.mean())
        K_se = float(Kb.std(ddof=1) / np.sqrt(nb))
        rows[str(m)] = {
            "m": int(m),
            "gamma_A": mu, "gamma_A_se": se,
            "gamma_A_ci95": [mu - Z95 * se, mu + Z95 * se],
            "gamma_B": float(gB.mean()),
            "gamma_B_se": float(gB.std(ddof=1) / np.sqrt(nb)),
            "gamma_naive_wrong_score": float(gN.mean()),
            "gamma_psipsi_stage_d_estimand": float(gP.mean()),
            "gamma_psipsi_se": float(gP.std(ddof=1) / np.sqrt(nb)),
            "R_m": float(Rm.mean()), "R_m_se": float(Rm.std(ddof=1) / np.sqrt(nb)),
            "p_tau_lt_m": float(pt.mean()),
            "rho_c": info["rho_c"], "rho_c_interval": info["rho_c_interval"],
            "regime": info["regime"],
            "lower_bound_exceeds_2": info["lower_bound_exceeds_2"],
            "accessible_in_admissible_domain":
                info["accessible_in_admissible_domain"],
            "K": K, "K_se": K_se, "K_ci95": [K - Z95 * K_se, K + Z95 * K_se],
            "extrapolation_beyond_p3": bool(int(m) not in (1, 2, 3, 5)),
        }
    lag = np.array([[b["gamma_lag"][r] for r in range(cell["lag_depth"])]
                    for b in cell["batches"]])
    ptg = np.array([[b["p_tau_gt_r"][r] for r in range(cell["lag_depth"])]
                    for b in cell["batches"]])
    arl = _bm(cell, ("arl",))
    g0 = lag[:, 0]
    wprof = (lag - 1.0) / (g0[:, None] - 1.0)
    return {
        "detector": cell["detector"], "family": cell["family"],
        "threshold": cell["threshold"],
        "threshold_provenance": cell["threshold_provenance"],
        "n_cycles": cell["n_cycles"], "n_batches": nb,
        "moment_marginal": cell["family"] in MOMENT_MARGINAL,
        "arl0": float(arl.mean()), "arl0_se": float(arl.std(ddof=1) / np.sqrt(nb)),
        "max_tau": max(b["max_tau"] for b in cell["batches"]),
        "n_ties": sum(b["n_ties"] for b in cell["batches"]),
        "gamma_lag": lag.mean(axis=0).tolist(),
        "gamma_lag_se": (lag.std(axis=0, ddof=1) / np.sqrt(nb)).tolist(),
        "lag_profile_w": wprof.mean(axis=0).tolist(),
        "lag_profile_w_se": (wprof.std(axis=0, ddof=1) / np.sqrt(nb)).tolist(),
        "p_tau_gt_r": ptg.mean(axis=0).tolist(),
        "per_m": rows,
    }


def build(tag: str = "E1") -> dict:
    cells, missing = [], []
    for d in DETECTORS:
        for f in FAMILIES:
            c = load_cell(d, f, tag)
            if c is None:
                missing.append(f"{d}:{f}")
            else:
                cells.append(cell_summary(c))
    return {"schema": "rebaseguard.p8.gamma-matrix.v1", "tag": tag,
            "m_grid": list(M_GRID), "lag_depth": LAG_DEPTH,
            "moment_marginal_families": list(MOMENT_MARGINAL),
            "missing_cells": missing, "cells": cells}


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "E1"
    out = build(tag)
    (RESULTS / f"gamma_matrix_{tag}.json").write_text(
        json.dumps(out, indent=1) + "\n")
    print(f"cells={len(out['cells'])} missing={out['missing_cells']}")
    for c in out["cells"]:
        r = c["per_m"]
        print(f"{c['detector']:6s} {c['family']:11s} ARL={c['arl0']:7.2f} "
              + " ".join(f"G{m}={r[str(m)]['gamma_A']:7.3f}" for m in (1, 2, 5, 20)))
