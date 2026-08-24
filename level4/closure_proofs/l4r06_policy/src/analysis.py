#!/usr/bin/env python3
"""Mechanical joint-bootstrap analysis for frozen L4R-06 cells."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from campaign import expected_keys, load_cell, manifest
from config import (
    ABSOLUTE_DELAY_GUARD,
    ACTIVE_REGIMES,
    CELLS,
    COMBINED_PROTOCOL_SHA256,
    N_BOOTSTRAP,
    N_REPLICATES,
    PRIMARY_EPSILON,
    REGIMES,
    RESULTS,
    SECONDARY_EPSILON,
    SEED_BOOTSTRAP,
    SHIFTS,
    canonical_json,
)
from integrity import verify as verify_integrity
from policy import policy_table


def _arrays(directory: Path = CELLS) -> dict[tuple[str, int, float], dict[str, np.ndarray]]:
    out = {}
    for key in expected_keys():
        payload = load_cell(key, directory)
        if payload is None:
            raise FileNotFoundError(f"missing frozen cell for {key}")
        metrics = {
            name: np.asarray(values, dtype=float)
            for name, values in payload["arm"]["per_replicate"].items()
        }
        if any(x.shape != (N_REPLICATES,) or not np.all(np.isfinite(x))
               for x in metrics.values()):
            raise ValueError(f"invalid per-replicate values for {key}")
        out[(key["policy"], key["m"], key["shift"])] = metrics
    return out


def _mean(x: np.ndarray, indices: np.ndarray | None = None) -> np.ndarray | float:
    return float(x.mean()) if indices is None else x[indices].mean(axis=1)


def _ratio(num: np.ndarray, den: np.ndarray,
           indices: np.ndarray | None = None) -> np.ndarray | float:
    return _mean(num, indices) / _mean(den, indices)


def _family(
    labels: list[dict[str, Any]],
    estimators: list[Callable[[np.ndarray | None], np.ndarray | float]],
    indices: np.ndarray,
    direction: str,
) -> dict[str, Any]:
    point = np.asarray([f(None) for f in estimators], dtype=float)
    boot = np.column_stack([f(indices) for f in estimators])
    se = boot.std(axis=0, ddof=1)
    safe = np.where(se > 0.0, se, 1.0)
    if direction == "lower":
        maxima = np.max((point - boot) / safe, axis=1)
        critical = float(np.quantile(maxima, 0.95))
        bound = point - critical * se
        bound_name = "simultaneous_lower95"
    elif direction == "upper":
        maxima = np.max((boot - point) / safe, axis=1)
        critical = float(np.quantile(maxima, 0.95))
        bound = point + critical * se
        bound_name = "simultaneous_upper95"
    else:
        raise ValueError(direction)
    rows = []
    for label, p, s, b in zip(labels, point, se, bound, strict=True):
        rows.append({**label, "point": float(p), "bootstrap_se": float(s),
                     bound_name: float(b)})
    return {
        "direction": direction,
        "confidence": 0.95,
        "family_size": len(rows),
        "method": "joint replicate-cluster bootstrap; maximum centered standardized deviation",
        "quantile_method": "NumPy linear",
        "critical_value": critical,
        "rows": rows,
    }


def build_findings(directory: Path = CELLS) -> dict[str, Any]:
    integrity = verify_integrity()
    data = _arrays(directory)
    indices = np.random.Generator(np.random.PCG64(
        np.random.SeedSequence([SEED_BOOTSTRAP, 2])
    )).integers(0, N_REPLICATES, size=(N_BOOTSTRAP, N_REPLICATES))

    def get(policy: str, m: int, shift: float, metric: str) -> np.ndarray:
        return data[(policy, m, shift)][metric]

    mse_labels, mse_estimators = [], []
    arl_labels, arl_estimators = [], []
    for m in ACTIVE_REGIMES:
        mse_labels.append({"m": m, "contrast": "MSE(P1)-MSE(P3)"})
        mse_estimators.append(lambda ix, m=m:
            _mean(get("P1", m, 0.0, "reference_mse"), ix)
            - _mean(get("P3", m, 0.0, "reference_mse"), ix))
        arl_labels.append({"m": m, "contrast": "ARL0(P3)-ARL0(P1)"})
        arl_estimators.append(lambda ix, m=m:
            _mean(get("P3", m, 0.0, "cycle_arl"), ix)
            - _mean(get("P1", m, 0.0, "cycle_arl"), ix))
    mse = _family(mse_labels, mse_estimators, indices, "lower")
    arl = _family(arl_labels, arl_estimators, indices, "lower")

    response_labels, response_estimators = [], []
    safety_labels, safety_estimators = [], []
    for m in REGIMES:
        for shift in SHIFTS:
            response_labels.append({
                "m": m, "shift": shift,
                "contrast": "R_delta(P3)-R_delta(P0)",
            })
            response_estimators.append(lambda ix, m=m, shift=shift:
                _ratio(get("P3", m, shift, "mean_delay"),
                       get("P3", m, 0.0, "mean_delay"), ix)
                - _ratio(get("P0", m, shift, "mean_delay"),
                         get("P0", m, 0.0, "mean_delay"), ix))
            safety_labels.append({
                "m": m, "shift": shift,
                "ratio": "delay(P3)/delay(P0)",
            })
            safety_estimators.append(lambda ix, m=m, shift=shift:
                _ratio(get("P3", m, shift, "mean_delay"),
                       get("P0", m, shift, "mean_delay"), ix))
    response = _family(response_labels, response_estimators, indices, "upper")
    safety = _family(safety_labels, safety_estimators, indices, "upper")

    actions = policy_table()
    h61_rows = []
    for row in actions:
        arithmetic = min(1.0, row["safety_factor"] * row["rho_c_lower95"])
        passed = (
            abs(row["rho"] - arithmetic) <= 1e-15
            and row["rho"] <= row["safety_factor"] * row["rho_c_lower95"] + 1e-15
            and row["multiplier_bound"] <= 0.8 + 1e-15
            and (not row["saturated"] or row["uncapped_allowance"] >= 1.0)
        )
        h61_rows.append({**row, "formula_reconstruction_pass": passed})
    h61 = all(row["formula_reconstruction_pass"] for row in h61_rows)
    for row in mse["rows"]:
        row["pass"] = row["simultaneous_lower95"] > 0.0
    for row in arl["rows"]:
        row["pass"] = row["simultaneous_lower95"] > 0.0
    for row in response["rows"]:
        upper = row["simultaneous_upper95"]
        row["primary_epsilon"] = PRIMARY_EPSILON
        row["primary_pass"] = upper < PRIMARY_EPSILON
        row["secondary_epsilon"] = SECONDARY_EPSILON
        row["secondary_pass"] = upper < SECONDARY_EPSILON
    for row in safety["rows"]:
        row["guard"] = ABSOLUTE_DELAY_GUARD
        row["pass"] = row["simultaneous_upper95"] < ABSOLUTE_DELAY_GUARD

    h62 = all(row["pass"] for row in mse["rows"])
    h63 = all(row["pass"] for row in arl["rows"])
    h64 = all(row["primary_pass"] for row in response["rows"])
    safety_pass = all(row["pass"] for row in safety["rows"])
    h65 = h61 and h62 and h63 and h64 and safety_pass

    summaries = []
    for (policy, m, shift), metrics in sorted(data.items()):
        summaries.append({
            "policy": policy, "m": m, "shift": shift,
            **{name: float(values.mean()) for name, values in metrics.items()},
        })
    m100_p1 = data[("P1", 100, 0.0)]
    m100_p3 = data[("P3", 100, 0.0)]
    saturated_identity = all(
        np.array_equal(m100_p1[name], m100_p3[name]) for name in m100_p1
    )

    negative = []
    for family_name, family, key in (
        ("H6-2", mse, "pass"), ("H6-3", arl, "pass"),
        ("H6-4", response, "primary_pass"), ("absolute safety", safety, "pass"),
    ):
        for row in family["rows"]:
            if not row[key]:
                negative.append({"family": family_name, **row})
    secondary_failures = [
        row for row in response["rows"] if not row["secondary_pass"]
    ]

    campaign = manifest(directory)
    return {
        "schema": "rebaseguard.l4r06-scientific-findings.v1",
        "protocol_sha256": COMBINED_PROTOCOL_SHA256,
        "campaign_manifest_sha256": hashlib.sha256(
            canonical_json(campaign).encode()).hexdigest(),
        "historical_firewall": {
            "integrity": integrity,
            "historical_stage_c": "STAGE-C-PARTIAL",
            "historical_C6": "FAILED",
            "final_global_reaudit": "LEVEL-4-PARTIAL",
            "l4r12_touched": False,
            "D4_operational_interpretation": "MATHEMATICAL, NOT OPERATIONAL",
        },
        "policy": {
            "formula": "rho_P3(m) = min(1, 0.8 * rho_c,L95(m))",
            "source": "protected D4 rho_c 95% confidence-interval lower endpoint",
            "actions": h61_rows,
            "point_estimate_policy_run": False,
            "P4_run": False,
        },
        "allocation": {
            "regimes": list(REGIMES), "shifts": list(SHIFTS),
            "n_replicates": N_REPLICATES, "n_events": 200,
            "n_bootstrap": N_BOOTSTRAP, "bootstrap_seed": SEED_BOOTSTRAP,
            "statistical_unit": "replicate cluster",
            "n_cells": campaign["n_cells"],
        },
        "H6-1": {"status": "PASS" if h61 else "FAIL", "rows": h61_rows},
        "H6-2": {"status": "PASS" if h62 else "FAIL", "family": mse},
        "H6-3": {"status": "PASS" if h63 else "FAIL", "family": arl},
        "H6-4": {"status": "PASS" if h64 else "FAIL", "family": response},
        "absolute_delay_safety": {
            "status": "PASS" if safety_pass else "FAIL", "family": safety,
        },
        "H6-5": {"status": "PASS" if h65 else "FAIL"},
        "saturated_m100_identity": saturated_identity,
        "all_cell_summaries": summaries,
        "negative_primary_findings": negative,
        "secondary_epsilon_0.05_failures": secondary_failures,
        "scientific_gate_status": (
            "SUPPORTED" if h65 and integrity["status"] == "PASS"
            else "NOT-SUPPORTED" if integrity["status"] == "PASS"
            else "INVALID"
        ),
        "same_requirement_mapping_candidate": bool(h65 and integrity["status"] == "PASS"),
        "mapping_reason": (
            "The pre-frozen D4-driven policy establishes stability awareness, "
            "reference improvement, an operational false-alert consequence, "
            "and detection safety under the original monitoring requirement."
            if h65 else
            "One or more frozen scientific gates failed; a stability-aware policy "
            "without the full monitoring-consequence evidence cannot close L4R-06."
        ),
    }


def write_findings(output: Path = RESULTS / "scientific_findings.json",
                   directory: Path = CELLS) -> dict[str, Any]:
    findings = build_findings(directory)
    output.write_text(canonical_json(findings))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RESULTS / "scientific_findings.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = canonical_json(build_findings())
    if args.check:
        if not args.output.exists() or args.output.read_text() != generated:
            print("scientific findings are not byte-stable")
            return 1
        print("scientific findings: byte-stable")
        return 0
    args.output.write_text(generated)
    data = json.loads(generated)
    print("L4R-06 scientific gates:", data["scientific_gate_status"])
    for name in ("H6-1", "H6-2", "H6-3", "H6-4", "H6-5"):
        print(f"  {name}: {data[name]['status']}")
    print("  absolute delay safety:", data["absolute_delay_safety"]["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
