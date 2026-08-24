"""Direct finite-difference map audit, independent of the Gamma accumulator."""

from __future__ import annotations

import ast
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

from .common import batch_summary, inverse_variance_pool, read_json, write_json
from .config import (
    CAMPAIGN,
    DIRECT_BATCHES,
    DIRECT_BATCH_PATHS,
    DIRECT_CELLS,
    DIRECT_REPLICATIONS,
    EPSILON_LADDER,
    MASTER_SEED,
    PROTOCOL_SHA256,
    RESULTS,
)

LEVEL4 = CAMPAIGN.parents[1]
sys.path.insert(0, str(LEVEL4 / "src"))
from rebaseguard_level4.frozen import H_FROZEN, K_FROZEN, cusum_update  # noqa: E402

CHECKPOINT = RESULTS / "direct_validation_checkpoint.json"


def _rng(key: list[int]) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(key)))


def simulate_map_batch(*, e: float, m: int, n_paths: int, rng: np.random.Generator) -> float:
    """Return a direct estimate of `e + E_e[A_m]` from reset stopped cycles."""
    if m < 1 or n_paths < 1:
        raise ValueError("positive m and path count required")
    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    buffer = np.zeros((n_paths, m))
    position = np.zeros(n_paths, dtype=np.int64)
    active = np.ones(n_paths, dtype=bool)
    tau = np.zeros(n_paths, dtype=np.int64)
    for step in range(1, 4_000_001):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        z = rng.standard_normal(idx.size) - e
        next_plus, next_minus, up, down = cusum_update(
            plus[idx], minus[idx], z, K_FROZEN, H_FROZEN
        )
        plus[idx] = next_plus
        minus[idx] = next_minus
        buffer[idx, position[idx] % m] = z
        position[idx] += 1
        crossed = up | down
        if crossed.any():
            done = idx[crossed]
            tau[done] = step
            active[done] = False
    else:
        raise RuntimeError(f"{int(np.count_nonzero(active))} direct paths did not alarm")
    order = (position[:, None] - 1 - np.arange(m)[None, :]) % m
    lags = np.take_along_axis(buffer, order, axis=1)
    realized = np.minimum(m, tau)
    valid = np.arange(m)[None, :] < realized[:, None]
    zbar = np.sum(np.where(valid, lags, 0.0), axis=1) / realized
    return float(np.mean(e + zbar))


def source_separation() -> dict[str, Any]:
    source = Path(__file__)
    imports = set()
    text = source.read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
    forbidden = ("gamma_grid", "phase_map")
    simulator = next(
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "simulate_map_batch"
    )
    simulator_text = ast.get_source_segment(text, simulator) or ""
    return {
        "direct_source": str(source.relative_to(CAMPAIGN)),
        "does_not_import_gamma_accumulator": not any(
            any(token in name for token in forbidden) for name in imports
        ),
        "does_not_import_boundary_finalizer": "phase_map" not in imports,
        "owns_stopped_cycle_loop": "for step in range" in simulator_text,
        "uses_random_denominator": "np.minimum(m, tau)" in simulator_text,
        "no_minimum_dwell_branch": "minimum_dwell" not in simulator_text,
    }


def _new_checkpoint() -> dict[str, Any]:
    return {
        "schema": "rebaseguard.d4-direct-checkpoint.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "master_seed": MASTER_SEED,
        "cells": [
            {"id": cell_id, "m": m, "rho": rho}
            for cell_id, m, rho in DIRECT_CELLS
        ],
        "epsilon_ladder": EPSILON_LADDER.tolist(),
        "config": {
            "replications": DIRECT_REPLICATIONS,
            "batches_per_sign": DIRECT_BATCHES,
            "paths_per_batch_per_sign": DIRECT_BATCH_PATHS,
        },
        "records": [],
        "complete": False,
    }


def _expected_keys() -> list[tuple[int, int, int, int]]:
    return [
        (cell, step, rep, batch)
        for cell in range(len(DIRECT_CELLS))
        for step in range(len(EPSILON_LADDER))
        for rep in range(DIRECT_REPLICATIONS)
        for batch in range(DIRECT_BATCHES)
    ]


def _validate_prefix(checkpoint: dict[str, Any]) -> None:
    if checkpoint["protocol_sha256"] != PROTOCOL_SHA256:
        raise RuntimeError("direct checkpoint protocol hash mismatch")
    expected = _expected_keys()[: len(checkpoint["records"])]
    observed = [tuple(row["index"]) for row in checkpoint["records"]]
    if observed != expected:
        raise RuntimeError("direct checkpoint is not a contiguous frozen prefix")


def _simulate_record(index: tuple[int, int, int, int]) -> dict[str, Any]:
    cell_index, step_index, rep, batch = index
    cell_id, m, rho = DIRECT_CELLS[cell_index]
    epsilon = float(EPSILON_LADDER[step_index])
    plus_key = [MASTER_SEED, 2, cell_index, step_index, rep, 1, batch]
    minus_key = [MASTER_SEED, 2, cell_index, step_index, rep, 0, batch]
    fresh_key = [MASTER_SEED, 3, cell_index, step_index, rep, batch]
    map_plus_full = simulate_map_batch(
        e=epsilon, m=m, n_paths=DIRECT_BATCH_PATHS, rng=_rng(plus_key)
    )
    map_minus_full = simulate_map_batch(
        e=-epsilon, m=m, n_paths=DIRECT_BATCH_PATHS, rng=_rng(minus_key)
    )
    fresh_mean = float(
        np.mean(_rng(fresh_key).standard_normal(DIRECT_BATCH_PATHS) / math.sqrt(m))
    )
    map_plus = rho * map_plus_full + (1.0 - rho) * fresh_mean
    map_minus = rho * map_minus_full + (1.0 - rho) * fresh_mean
    derivative = (map_plus - map_minus) / (2.0 * epsilon)
    return {
        "index": list(index),
        "cell_id": cell_id,
        "m": m,
        "rho": rho,
        "epsilon": epsilon,
        "replication": rep,
        "batch": batch,
        "n_paths_per_sign": DIRECT_BATCH_PATHS,
        "plus_seed_key": plus_key,
        "minus_seed_key": minus_key,
        "fresh_seed_key": fresh_key,
        "map_plus": map_plus,
        "map_minus": map_minus,
        "fresh_mean_paired_across_signs": fresh_mean,
        "central_derivative": derivative,
    }


def _step_summary(records: list[dict[str, Any]], cell_id: str, step: float, rep: int) -> dict[str, Any]:
    selected = [
        row for row in records
        if row["cell_id"] == cell_id
        and row["epsilon"] == step
        and row["replication"] == rep
    ]
    if len(selected) != DIRECT_BATCHES:
        raise RuntimeError("incomplete direct step")
    summary = batch_summary(row["central_derivative"] for row in selected)
    return {"epsilon": step, **summary}


def summarize(checkpoint: dict[str, Any], gamma: dict[str, Any]) -> dict[str, Any]:
    _validate_prefix(checkpoint)
    if len(checkpoint["records"]) != len(_expected_keys()):
        raise RuntimeError("direct checkpoint incomplete")
    gamma_by_m = {row["m"]: row for row in gamma["rows"]}
    rows = []
    all_plus = []
    all_minus = []
    for cell_id, m, rho in DIRECT_CELLS:
        replications = []
        for rep in range(DIRECT_REPLICATIONS):
            ladder = {
                str(float(step)): _step_summary(
                    checkpoint["records"], cell_id, float(step), rep
                )
                for step in EPSILON_LADDER
            }
            big = ladder[str(0.0125)]
            small = ladder[str(0.00625)]
            richardson = (4.0 * small["mean"] - big["mean"]) / 3.0
            richardson_se = math.hypot(4.0 * small["se"], big["se"]) / 3.0
            replications.append({
                "replication": rep,
                "ladder": ladder,
                "richardson": richardson,
                "richardson_se": richardson_se,
            })
        pooled, pooled_se = inverse_variance_pool(
            (row["richardson"] for row in replications),
            (row["richardson_se"] for row in replications),
        )
        agreement_z = abs(replications[0]["richardson"] - replications[1]["richardson"]) / math.hypot(
            replications[0]["richardson_se"], replications[1]["richardson_se"]
        )
        gamma_row = gamma_by_m[m]["gamma_tilde"]
        target = rho * (1.0 - gamma_row["mean"])
        target_se = rho * gamma_row["se"]
        discrepancy = pooled - target
        combined_se = math.hypot(pooled_se, target_se)
        z = abs(discrepancy) / combined_se
        magnitude_rule = (
            abs(discrepancy) <= 0.10
            if abs(target) < 0.5
            else abs(discrepancy) / abs(target) <= 0.10
        )
        passed = z <= 4.0 and magnitude_rule and agreement_z <= 4.0
        rows.append({
            "cell_id": cell_id,
            "m": m,
            "rho": rho,
            "theorem_lambda": target,
            "theorem_lambda_se": target_se,
            "replications": replications,
            "direct_derivative": pooled,
            "direct_derivative_se": pooled_se,
            "discrepancy": discrepancy,
            "combined_se": combined_se,
            "absolute_z": z,
            "relative_discrepancy": abs(discrepancy) / max(abs(target), 1e-300),
            "replication_agreement_z": agreement_z,
            "magnitude_rule_passed": magnitude_rule,
            "passed": passed,
        })
    for record in checkpoint["records"]:
        all_plus.append(tuple(record["plus_seed_key"]))
        all_minus.append(tuple(record["minus_seed_key"]))
    separation = source_separation()
    checks = {
        "all_frozen_records_present": len(checkpoint["records"]) == len(_expected_keys()),
        "plus_seed_keys_unique": len(all_plus) == len(set(all_plus)),
        "minus_seed_keys_unique": len(all_minus) == len(set(all_minus)),
        "plus_minus_seed_keys_disjoint": set(all_plus).isdisjoint(all_minus),
        "source_separation": all(
            value for key, value in separation.items() if key != "direct_source"
        ),
        "all_cells_pass": all(row["passed"] for row in rows),
    }
    return {
        "schema": "rebaseguard.d4-direct-validation.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "evidence": "NEW-CONFIRMATORY-NUMERICAL",
        "epsilon_ladder": EPSILON_LADDER.tolist(),
        "primary_estimator": "Richardson from central differences at 0.0125 and 0.00625",
        "source_separation": separation,
        "rows": rows,
        "checks": checks,
        "valid": all(checks.values()),
    }


def run(*, resume: bool = True) -> dict[str, Any]:
    gamma = read_json(RESULTS / "gamma_grid.json")
    if not gamma["valid"]:
        raise RuntimeError("Gamma grid must be valid before direct validation")
    if resume and CHECKPOINT.exists():
        checkpoint = read_json(CHECKPOINT)
    else:
        checkpoint = _new_checkpoint()
        write_json(CHECKPOINT, checkpoint)
    _validate_prefix(checkpoint)
    keys = _expected_keys()
    for number, index in enumerate(keys[len(checkpoint["records"]):], start=len(checkpoint["records"])+1):
        checkpoint["records"].append(_simulate_record(index))
        write_json(CHECKPOINT, checkpoint)
        if number % DIRECT_BATCHES == 0:
            print(f"Direct validation records {number}/{len(keys)}", flush=True)
    checkpoint["complete"] = True
    summary = summarize(checkpoint, gamma)
    checkpoint["summary"] = summary
    write_json(CHECKPOINT, checkpoint)
    write_json(RESULTS / "direct_validation.json", summary)
    if not summary["valid"]:
        raise RuntimeError("direct-map correspondence gate failed")
    return summary
