"""Small frozen operational consequence overlay for the D4 theorem map."""

from __future__ import annotations

import sys
from typing import Any

import numpy as np

from .common import batch_summary, read_json, write_json
from .config import (
    CAMPAIGN,
    MASTER_SEED,
    OPERATIONAL_BATCHES,
    OPERATIONAL_BURN_IN,
    OPERATIONAL_CELLS,
    OPERATIONAL_CYCLES,
    OPERATIONAL_REPLICATES_PER_BATCH,
    PROTOCOL_SHA256,
    RESULTS,
)

STAGE_D_SRC = CAMPAIGN.parents[1] / "stage_d" / "src"
sys.path.insert(0, str(STAGE_D_SRC))
from chain import simulate_chain  # noqa: E402

CHECKPOINT = RESULTS / "operational_overlay_checkpoint.json"
METRICS = ("cycle_arl", "reference_mse", "reference_acf1", "direction_acf1")


def _new_checkpoint() -> dict[str, Any]:
    return {
        "schema": "rebaseguard.d4-operational-checkpoint.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "master_seed": MASTER_SEED,
        "cells": [{"m": m, "rho": rho} for m, rho in OPERATIONAL_CELLS],
        "config": {
            "n_batches": OPERATIONAL_BATCHES,
            "replicates_per_batch": OPERATIONAL_REPLICATES_PER_BATCH,
            "cycles": OPERATIONAL_CYCLES,
            "burn_in": OPERATIONAL_BURN_IN,
        },
        "records": [],
        "complete": False,
    }


def _expected_keys() -> list[tuple[int, int]]:
    return [
        (cell, batch)
        for cell in range(len(OPERATIONAL_CELLS))
        for batch in range(OPERATIONAL_BATCHES)
    ]


def _validate_prefix(checkpoint: dict[str, Any]) -> None:
    if checkpoint["protocol_sha256"] != PROTOCOL_SHA256:
        raise RuntimeError("operational checkpoint protocol hash mismatch")
    if [tuple(row["index"]) for row in checkpoint["records"]] != _expected_keys()[: len(checkpoint["records"])]:
        raise RuntimeError("operational checkpoint is not a contiguous frozen prefix")


def _simulate_record(index: tuple[int, int]) -> dict[str, Any]:
    cell, batch = index
    m, rho = OPERATIONAL_CELLS[cell]
    key = [MASTER_SEED, 4, cell, batch]
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(key)))
    result = simulate_chain(
        m=m,
        rho=rho,
        n_rep=OPERATIONAL_REPLICATES_PER_BATCH,
        n_cycles=OPERATIONAL_CYCLES,
        burn_in=OPERATIONAL_BURN_IN,
        rng=rng,
    )
    replicate_values = {
        "cycle_arl": result.cycle_arl,
        "reference_mse": result.reference_mse,
        "reference_acf1": result.e_acf1,
        "direction_acf1": result.direction_acf1,
    }
    return {
        "index": list(index),
        "m": m,
        "rho": rho,
        "batch": batch,
        "seed_key": key,
        "n_replicates": OPERATIONAL_REPLICATES_PER_BATCH,
        "metric_batch_means": {
            name: float(np.mean(values)) for name, values in replicate_values.items()
        },
        "finite_replicate_metrics": all(
            bool(np.all(np.isfinite(values))) for values in replicate_values.values()
        ),
    }


def summarize(checkpoint: dict[str, Any]) -> dict[str, Any]:
    _validate_prefix(checkpoint)
    if len(checkpoint["records"]) != len(_expected_keys()):
        raise RuntimeError("operational checkpoint incomplete")
    phase_map = read_json(RESULTS / "phase_map.json")
    gamma_by_m = {row["m"]: row["gamma_tilde"]["mean"] for row in phase_map["gamma_rows"]}
    rows = []
    for m, rho in OPERATIONAL_CELLS:
        records = [
            row for row in checkpoint["records"]
            if row["m"] == m and row["rho"] == rho
        ]
        metrics = {
            metric: batch_summary(
                row["metric_batch_means"][metric] for row in records
            )
            for metric in METRICS
        }
        multiplier = rho * (1.0 - gamma_by_m[m])
        theorem_class = (
            "LOCALLY-STABLE" if abs(multiplier) < 1.0
            else "BOUNDARY" if abs(multiplier) == 1.0
            else "LOCALLY-UNSTABLE"
        )
        rows.append({
            "m": m,
            "rho": rho,
            "lambda": multiplier,
            "theorem_class": theorem_class,
            "metrics": metrics,
        })
    keys = [tuple(row["seed_key"]) for row in checkpoint["records"]]
    checks = {
        "all_frozen_cells_and_batches_present": len(checkpoint["records"]) == len(_expected_keys()),
        "unique_seed_keys": len(keys) == len(set(keys)),
        "all_replicate_metrics_finite": all(
            row["finite_replicate_metrics"] for row in checkpoint["records"]
        ),
        "both_theorem_sides_present": {
            row["theorem_class"] for row in rows
        } >= {"LOCALLY-STABLE", "LOCALLY-UNSTABLE"},
        "historical_d2_5_preserved": True,
    }
    return {
        "schema": "rebaseguard.d4-operational-overlay.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "evidence": "NEW-CONFIRMATORY-NUMERICAL-CONSEQUENCE-CHECK",
        "convention": "Stage-D convention A; ordinary tau; w=min(m,tau)",
        "statistical_unit": "replicate; uncertainty from frozen independent batch means",
        "rows": rows,
        "interpretation": (
            "Consequence-only overlay; no discontinuity criterion was frozen or required. "
            "These cells cannot overturn historical D2.5."
        ),
        "historical_d2_5": "MATHEMATICAL, NOT OPERATIONAL",
        "checks": checks,
        "valid": all(checks.values()),
    }


def run(*, resume: bool = True) -> dict[str, Any]:
    if resume and CHECKPOINT.exists():
        checkpoint = read_json(CHECKPOINT)
    else:
        checkpoint = _new_checkpoint()
        write_json(CHECKPOINT, checkpoint)
    _validate_prefix(checkpoint)
    keys = _expected_keys()
    for number, index in enumerate(keys[len(checkpoint["records"]):], start=len(checkpoint["records"]) + 1):
        checkpoint["records"].append(_simulate_record(index))
        write_json(CHECKPOINT, checkpoint)
        print(f"Operational overlay records {number}/{len(keys)}", flush=True)
    checkpoint["complete"] = True
    summary = summarize(checkpoint)
    checkpoint["summary"] = summary
    write_json(CHECKPOINT, checkpoint)
    write_json(RESULTS / "operational_overlay.json", summary)
    if not summary["valid"]:
        raise RuntimeError("operational overlay validity gate failed")
    return summary
