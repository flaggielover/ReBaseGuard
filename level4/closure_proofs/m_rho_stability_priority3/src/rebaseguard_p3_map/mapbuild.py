"""Assemble the cross-detector m-rho stability map from provenance JSON."""

from __future__ import annotations

import csv
from fractions import Fraction
from typing import Any

from .classifier import (
    CLASS_BOUNDARY,
    UNCERTAINTY_EXACT,
    classify_cell,
    magnitude_interval,
    multiplier,
)
from .common import read_json, write_json
from .config import (
    BOUNDARY_TOLERANCE,
    GATES,
    M_GRID,
    PROTOCOL,
    PROTOCOL_SHA256,
    RESULTS,
    RHO_DOMAIN,
    RHO_GRID,
)

CELL_FIELDS = [
    "layer", "detector_family", "detector_short", "source_priority", "m",
    "rho", "gamma_tilde", "gamma_tilde_exact", "gamma_tilde_se",
    "gamma_ci95_lo", "gamma_ci95_hi", "lambda", "abs_lambda",
    "abs_lambda_lo", "abs_lambda_hi", "class", "local_first_order_dynamics",
    "gamma_regime", "gamma_evidence_class", "evidence_class",
    "uncertainty_status", "classification_reportable_as_robust",
    "rho_in_admissible_domain", "cell_kind",
]


def _row_interval(row: dict[str, Any]) -> tuple[float, float] | None:
    interval = row["gamma_tilde_ci95"]
    return tuple(interval) if interval else None


def _cell(layer: dict[str, Any], row: dict[str, Any], rho: float,
          kind: str) -> dict[str, Any]:
    record = classify_cell(
        rho,
        row["gamma_tilde"],
        cell_evidence_class=row["cell_evidence_class"],
        gamma_evidence_class=row["gamma_evidence_class"],
        gamma_se=row["gamma_tilde_se"],
        gamma_interval=_row_interval(row),
        gamma_exact=row["gamma_tilde_exact"],
    )
    record.update({
        "layer": layer["id"],
        "detector_family": layer["detector_family"],
        "detector_short": layer["detector_short"],
        "source_priority": layer["source_priority"],
        "m": row["m"],
        "cell_kind": kind,
    })
    return record


def uncertainty_band(row: dict[str, Any]) -> dict[str, Any] | None:
    """The rho interval on which the empirical class is not reportable.

    For a gain interval strictly above one the classification flips exactly
    where ``rho|1-Gamma|`` crosses one, so the sensitive band is bounded by the
    two transformed endpoints.  Outside that band the 95% interval gives the
    same class at both endpoints.
    """
    interval = row["gamma_tilde_ci95"]
    if not interval:
        return None
    lo, hi = sorted(interval)
    if lo <= 1.0 <= hi:
        return {
            "rho_lo": None,
            "rho_hi": None,
            "bounded": False,
            "note": "the gain interval contains one, so no finite sensitive band exists",
        }
    d_lo, d_hi = sorted((abs(1.0 - lo), abs(1.0 - hi)))
    return {
        "rho_lo": 1.0 / d_hi,
        "rho_hi": 1.0 / d_lo,
        "bounded": True,
        "intersects_admissible_domain":
            1.0 / d_hi <= RHO_DOMAIN[1] and 1.0 / d_lo >= RHO_DOMAIN[0],
        "note": "classification is not reportable as robust for rho in this band",
    }


def cross_detector_comparison(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare the two empirical Gaussian boundaries window by window.

    The comparison is deliberately confined to the two empirical layers: the
    finite-support witnesses run at different thresholds and are not estimates
    of the Gaussian boundaries, so comparing them across families would be
    meaningless.
    """
    def pick(layer: str, m: int) -> dict[str, Any]:
        return next(r for r in rows if r["layer"] == layer and r["m"] == m)

    windows = []
    for m in M_GRID:
        cusum = pick("GAUSSIAN_CUSUM_FROZEN", m)
        sr = pick("GAUSSIAN_SR_FROZEN", m)
        c_int = cusum["rho_crit_interval"]
        s_int = sr["rho_crit_interval"]
        disjoint = bool(c_int and s_int and (s_int[1] < c_int[0] or c_int[1] < s_int[0]))
        windows.append({
            "m": m,
            "cusum_rho_crit": cusum["rho_crit"],
            "cusum_rho_crit_ci95": c_int,
            "sr_rho_crit": sr["rho_crit"],
            "sr_rho_crit_ci95": s_int,
            "sr_boundary_below_cusum": sr["rho_crit"] < cusum["rho_crit"],
            "intervals_disjoint": disjoint,
        })
    return {
        "layers_compared": ["GAUSSIAN_SR_FROZEN", "GAUSSIAN_CUSUM_FROZEN"],
        "windows": windows,
        "sr_boundary_below_cusum_at_every_window":
            all(row["sr_boundary_below_cusum"] for row in windows),
        "separation_supported_by_disjoint_intervals_at_every_window":
            all(row["intervals_disjoint"] for row in windows),
        "evidence_class": "THEOREM_PLUS_EMPIRICAL_ESTIMATE",
        "scope": (
            "An empirical ordering between two frozen Gaussian specializations. "
            "It is not a detector-universal law and does not extend to the "
            "finite-support witnesses, which run at different thresholds."
        ),
    }


def build() -> dict[str, Any]:
    prov = read_json(RESULTS / "provenance.json")
    if not prov["valid"] or prov["protocol_sha256"] != PROTOCOL_SHA256:
        raise RuntimeError("provenance artifact is invalid or built under another protocol")

    cells: list[dict[str, Any]] = []
    boundary_rows: list[dict[str, Any]] = []
    boundary_cells: list[dict[str, Any]] = []

    for layer in prov["layers"]:
        for row in layer["rows"]:
            for rho in RHO_GRID:
                cells.append(_cell(layer, row, float(rho), "GRID"))

            bnd = row["boundary"]
            rho_c = bnd["rho_crit"]
            exact_rho_c = None
            exact_unit = None
            if row["gamma_tilde_exact"] is not None and rho_c is not None:
                gamma_q = Fraction(row["gamma_tilde_exact"])
                if gamma_q != 1:
                    rho_q = Fraction(1) / abs(Fraction(1) - gamma_q)
                    exact_rho_c = str(rho_q)
                    exact_unit = abs(rho_q * (Fraction(1) - gamma_q)) == 1
            boundary_rows.append({
                "layer": layer["id"],
                "detector_family": layer["detector_family"],
                "detector_short": layer["detector_short"],
                "source_priority": layer["source_priority"],
                "m": row["m"],
                "gamma_tilde": row["gamma_tilde"],
                "gamma_tilde_exact": row["gamma_tilde_exact"],
                "gamma_tilde_se": row["gamma_tilde_se"],
                "gamma_tilde_ci95": row["gamma_tilde_ci95"],
                "gamma_evidence_class": row["gamma_evidence_class"],
                "provenance_kind": row["provenance_kind"],
                "rho_crit_exact": exact_rho_c,
                "rho_crit_exact_gives_unit_magnitude": exact_unit,
                "uncertainty_band": uncertainty_band(row),
                **bnd,
            })
            if rho_c is not None and RHO_DOMAIN[0] <= rho_c <= RHO_DOMAIN[1]:
                boundary_cells.append(_cell(layer, row, rho_c, "EXACT_BOUNDARY"))

    comparison = cross_detector_comparison(boundary_rows)

    checks = {
        "provenance_valid": bool(prov["valid"]),
        "upstream_hashes_match": bool(prov["upstream_hashes"]["all_match"]),
        "complete_grid": len(cells) == len(prov["layers"]) * len(M_GRID) * len(RHO_GRID),
        "rho_zero_attracting": all(
            cell["class"] == "LOCALLY-STABLE"
            for cell in cells if cell["rho"] == 0.0
        ),
        "formula_recomputed": all(
            abs(cell["lambda"] - multiplier(cell["rho"], cell["gamma_tilde"]))
            <= GATES["require_formula_recomputation_tolerance"]
            for cell in cells
        ),
        "exact_boundary_cells_have_unit_magnitude": all(
            cell["class"] == CLASS_BOUNDARY for cell in boundary_cells
        ),
        "exact_rational_boundaries_are_exact": all(
            row["rho_crit_exact_gives_unit_magnitude"] is not False
            for row in boundary_rows
        ),
        "certified_layers_carry_no_interval": all(
            cell["uncertainty_status"] == UNCERTAINTY_EXACT
            for cell in cells
            if cell["gamma_evidence_class"] == "EXACT_SYMBOLIC"
        ),
        "gaussian_layers_never_labelled_certified": all(
            cell["evidence_class"] != "THEOREM_PLUS_CERTIFIED_INPUT"
            for cell in cells
            if cell["gamma_evidence_class"] == "EMPIRICAL_ONLY"
        ),
        "gamma_not_interpolated_across_m": not prov["gamma_interpolated_across_m"],
        "magnitude_interval_is_exact_image": all(
            magnitude_interval(cell["rho"], *cell["gamma_tilde_ci95"])
            == tuple(cell["abs_lambda_interval"])
            for cell in cells if cell["gamma_tilde_ci95"]
        ),
    }

    payload = {
        "schema": "rebaseguard.p3-stability-map.v1",
        "campaign": PROTOCOL["campaign"],
        "protocol_sha256": PROTOCOL_SHA256,
        "derivative_identity": "lambda_{D,m}(rho) = F'_{rho,m}(0) = rho(1 - GammaTilde_{D,m})",
        "classification_rule": PROTOCOL["classification"]["rule"],
        "boundary_tolerance": BOUNDARY_TOLERANCE,
        "admissible_rho_domain": PROTOCOL["admissible_rho_domain"],
        "m_grid": M_GRID,
        "rho_grid": RHO_GRID,
        "layers": [
            {k: layer[k] for k in (
                "id", "detector_family", "detector_short", "source_priority",
                "gamma_evidence_class", "cell_evidence_class", "uncertainty_model",
            )}
            for layer in prov["layers"]
        ],
        "cells": cells,
        "boundary_cells": boundary_cells,
        "boundary_rows": boundary_rows,
        "cross_detector_comparison": comparison,
        "checks": checks,
        "claim_scope": PROTOCOL["claim_scope"],
        "evidence_boundary": PROTOCOL["evidence_boundary"],
        "valid": all(checks.values()),
    }
    write_json(RESULTS / "stability_map.json", payload)
    write_json(RESULTS / "boundary_table.json", {
        "schema": "rebaseguard.p3-boundary-table.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "rows": boundary_rows,
        "valid": payload["valid"],
    })
    _write_csv(payload)
    return payload


def _write_csv(payload: dict[str, Any]) -> None:
    path = RESULTS / "stability_map.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=CELL_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        for cell in payload["cells"] + payload["boundary_cells"]:
            ci = cell["gamma_tilde_ci95"] or [None, None]
            mag = cell["abs_lambda_interval"] or [None, None]
            writer.writerow({
                "layer": cell["layer"],
                "detector_family": cell["detector_family"],
                "detector_short": cell["detector_short"],
                "source_priority": cell["source_priority"],
                "m": cell["m"],
                "rho": cell["rho"],
                "gamma_tilde": cell["gamma_tilde"],
                "gamma_tilde_exact": cell["gamma_tilde_exact"],
                "gamma_tilde_se": cell["gamma_tilde_se"],
                "gamma_ci95_lo": ci[0],
                "gamma_ci95_hi": ci[1],
                "lambda": cell["lambda"],
                "abs_lambda": cell["abs_lambda"],
                "abs_lambda_lo": mag[0],
                "abs_lambda_hi": mag[1],
                "class": cell["class"],
                "local_first_order_dynamics": cell["local_first_order_dynamics"],
                "gamma_regime": cell["gamma_regime"],
                "gamma_evidence_class": cell["gamma_evidence_class"],
                "evidence_class": cell["evidence_class"],
                "uncertainty_status": cell["uncertainty_status"],
                "classification_reportable_as_robust":
                    cell["classification_reportable_as_robust"],
                "rho_in_admissible_domain": cell["rho_in_admissible_domain"],
                "cell_kind": cell["cell_kind"],
            })
