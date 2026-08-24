"""Mechanically derive the D4 local stability map from Gamma JSON."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from .common import read_json, write_json
from .config import (
    BOUNDARY_TOLERANCE,
    M_GRID,
    PROTOCOL_SHA256,
    RESULTS,
    RHO_GRID,
    RHO_SAFE,
)


def classify(multiplier: float) -> str:
    magnitude = abs(multiplier)
    if abs(magnitude - 1.0) <= BOUNDARY_TOLERANCE:
        return "BOUNDARY"
    if magnitude < 1.0:
        return "LOCALLY-STABLE"
    return "LOCALLY-UNSTABLE"


def boundary(gamma: float, se: float, ci95: list[float]) -> dict[str, Any]:
    distance = abs(1.0 - gamma)
    if distance == 0.0:
        raw = None
        accessible = False
    else:
        raw = 1.0 / distance
        accessible = raw <= 1.0 + BOUNDARY_TOLERANCE
    if gamma > 1.0:
        regime = "GAMMA_GT_2" if gamma > 2.0 else (
            "GAMMA_EQ_2" if gamma == 2.0 else "ONE_LT_GAMMA_LT_2"
        )
        rho_se = se / (gamma - 1.0) ** 2
        if ci95[0] > 1.0:
            rho_ci = [1.0 / (ci95[1] - 1.0), 1.0 / (ci95[0] - 1.0)]
        else:
            rho_ci = [0.0, None]
    elif gamma == 1.0:
        regime = "GAMMA_EQ_1"
        rho_se = None
        rho_ci = [None, None]
    else:
        regime = "GAMMA_LE_1"
        rho_se = se / max(distance**2, 1e-300)
        rho_ci = [None, None]
    return {
        "gamma_regime": regime,
        "rho_c_unconstrained": raw,
        "rho_c_se_delta": rho_se,
        "rho_c_ci95": rho_ci,
        "boundary_accessible_on_unit_interval": accessible,
    }


def crossing(gamma_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found = []
    for left, right in zip(gamma_rows[:-1], gamma_rows[1:]):
        g0 = left["gamma_tilde"]["mean"]
        g1 = right["gamma_tilde"]["mean"]
        if (g0 - 2.0) * (g1 - 2.0) > 0.0:
            continue
        if g0 == g1:
            estimate = None
        else:
            weight = (2.0 - g0) / (g1 - g0)
            estimate = float(math.exp(math.log(left["m"]) + weight * (
                math.log(right["m"]) - math.log(left["m"])
            )))
        found.append({
            "bracket": [left["m"], right["m"]],
            "gamma_at_bracket": [g0, g1],
            "m_crossing_log_linear": estimate,
        })
    return found


def build() -> dict[str, Any]:
    gamma = read_json(RESULTS / "gamma_grid.json")
    direct = read_json(RESULTS / "direct_validation.json")
    if gamma["m_grid"] != M_GRID.tolist() or not gamma["valid"]:
        raise RuntimeError("invalid or changed Gamma input")
    boundary_rows = []
    cells = []
    for row in gamma["rows"]:
        point = row["gamma_tilde"]
        b = boundary(point["mean"], point["se"], point["ci95"])
        boundary_rows.append({"m": row["m"], **b})
        for rho_raw in RHO_GRID:
            rho = float(rho_raw)
            multiplier = rho * (1.0 - point["mean"])
            lo_multiplier = min(
                rho * (1.0 - point["ci95"][0]),
                rho * (1.0 - point["ci95"][1]),
            )
            hi_multiplier = max(
                rho * (1.0 - point["ci95"][0]),
                rho * (1.0 - point["ci95"][1]),
            )
            cells.append({
                "m": row["m"],
                "rho": rho,
                "lambda": multiplier,
                "lambda_ci95": [lo_multiplier, hi_multiplier],
                "class": classify(multiplier),
                "class_ci_sensitive": classify(lo_multiplier) != classify(hi_multiplier),
            })
    crossings = crossing(gamma["rows"])
    checks = {
        "gamma_input_valid": gamma["valid"],
        "direct_correspondence_valid": direct["valid"],
        "complete_grid": len(cells) == len(M_GRID) * len(RHO_GRID),
        "rho_zero_stable": all(
            row["class"] == "LOCALLY-STABLE" for row in cells if row["rho"] == 0.0
        ),
        "formula_recomputed": all(
            abs(row["lambda"] - row["rho"] * (
                1.0 - next(
                    item["gamma_tilde"]["mean"]
                    for item in gamma["rows"] if item["m"] == row["m"]
                )
            )) <= 1e-15
            for row in cells
        ),
        "all_classes_allowed": all(
            row["class"] in {"LOCALLY-STABLE", "BOUNDARY", "LOCALLY-UNSTABLE"}
            for row in cells
        ),
    }
    output = {
        "schema": "rebaseguard.d4-phase-map.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "title": "Local deterministic reference-map stability",
        "derivative_formula": "F'_{rho,m}(0) = rho(1-GammaTilde_m)",
        "gamma_definition": "GammaTilde_m = E_0[A_m T_tau], A_m=(1/min(m,tau))*sum_{r<min(m,tau)} Z_{tau-r}",
        "claim_scope": "protocol-specific local deterministic conditional-mean skeleton",
        "rho_safe_stage_c": RHO_SAFE,
        "m_grid": M_GRID.tolist(),
        "rho_grid": RHO_GRID.tolist(),
        "gamma_rows": gamma["rows"],
        "boundary_rows": boundary_rows,
        "crossings_gamma_equals_2": crossings,
        "cells": cells,
        "direct_validation_status": direct["valid"],
        "checks": checks,
        "valid": all(checks.values()),
    }
    write_json(RESULTS / "phase_map.json", output)
    if not output["valid"]:
        raise RuntimeError("phase-map mechanical checks failed")
    return output
