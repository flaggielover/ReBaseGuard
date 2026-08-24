#!/usr/bin/env python3
"""Resumable frozen-cell runner for the L4R-06 confirmatory campaign."""
from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from config import (
    BURN_IN,
    CELLS,
    COMBINED_PROTOCOL_SHA256,
    CYCLES_BETWEEN,
    N_EVENTS,
    N_REPLICATES,
    POLICY_LABELS,
    REGIMES,
    RESULTS,
    SEED_CONFIRM,
    SHIFTS,
    canonical_json,
)
from policy import policies
from simulator import ArmConfig, simulate_arm


def cell_key(policy: str, m: int, shift: float) -> dict[str, Any]:
    return {
        "schema": "rebaseguard.l4r06-cell-key.v1",
        "protocol_sha256": COMBINED_PROTOCOL_SHA256,
        "policy": policy,
        "rho": policies(m)[policy],
        "m": m,
        "shift": shift,
        "n_replicates": N_REPLICATES,
        "n_events": N_EVENTS,
        "burn_in": BURN_IN,
        "cycles_between": CYCLES_BETWEEN,
        "master_seed": SEED_CONFIRM,
    }


def key_hash(key: dict[str, Any]) -> str:
    raw = json.dumps(key, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def cell_path(key: dict[str, Any], directory: Path = CELLS) -> Path:
    return directory / f"cell_{key_hash(key)[:20]}.json"


def expected_keys() -> list[dict[str, Any]]:
    return [
        cell_key(policy, m, shift)
        for m in REGIMES
        for policy in POLICY_LABELS
        for shift in (0.0, *SHIFTS)
    ]


def validate_cell(payload: dict[str, Any], key: dict[str, Any]) -> None:
    if payload.get("key") != key or payload.get("key_sha256") != key_hash(key):
        raise ValueError("cell key/hash mismatch")
    if payload.get("protocol_sha256") != COMBINED_PROTOCOL_SHA256:
        raise ValueError("cell protocol mismatch")
    arm = payload.get("arm", {})
    if not arm.get("finite") or arm.get("completed_events") != N_REPLICATES * N_EVENTS:
        raise ValueError("cell is incomplete or non-finite")
    values = arm.get("per_replicate", {})
    if set(values) != {
        "mean_delay", "reference_mse", "reference_mean", "reference_sd",
        "cycle_arl", "reference_acf1", "direction_acf1",
    } or any(len(v) != N_REPLICATES for v in values.values()):
        raise ValueError("per-replicate cell summaries are incomplete")


def compute_cell(key: dict[str, Any]) -> dict[str, Any]:
    arm = simulate_arm(ArmConfig(
        n_replicates=key["n_replicates"],
        n_events=key["n_events"],
        burn_in=key["burn_in"],
        cycles_between=key["cycles_between"],
        rho=key["rho"],
        m=key["m"],
        shift=key["shift"],
        master_seed=key["master_seed"],
    ))
    payload = {
        "schema": "rebaseguard.l4r06-cell.v1",
        "protocol_sha256": COMBINED_PROTOCOL_SHA256,
        "key": key,
        "key_sha256": key_hash(key),
        "arm": arm,
    }
    validate_cell(payload, key)
    return payload


def write_cell(payload: dict[str, Any], directory: Path = CELLS) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = cell_path(payload["key"], directory)
    path.write_text(canonical_json(payload))
    return path


def load_cell(key: dict[str, Any], directory: Path = CELLS) -> dict[str, Any] | None:
    path = cell_path(key, directory)
    if not path.exists():
        return None
    payload = json.loads(path.read_text())
    validate_cell(payload, key)
    return payload


def manifest(directory: Path = CELLS) -> dict[str, Any]:
    rows = []
    for key in expected_keys():
        path = cell_path(key, directory)
        payload = load_cell(key, directory)
        if payload is None:
            raise FileNotFoundError(path)
        rows.append({
            "key": key,
            "key_sha256": key_hash(key),
            "file": path.name,
            "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    return {
        "schema": "rebaseguard.l4r06-campaign-manifest.v1",
        "protocol_sha256": COMBINED_PROTOCOL_SHA256,
        "n_cells": len(rows),
        "cells": rows,
    }


def run(*, workers: int, force: bool = False) -> None:
    keys = expected_keys()
    pending = []
    for key in keys:
        cached = None if force else load_cell(key)
        if cached is None:
            pending.append(key)
        else:
            print(f"[cached] P={key['policy']} m={key['m']} shift={key['shift']:g}", flush=True)
    print(f"L4R-06 cells: {len(keys) - len(pending)} cached, {len(pending)} pending", flush=True)
    if pending:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(compute_cell, key): key for key in pending}
            for future in as_completed(futures):
                key = futures[future]
                payload = future.result()
                path = write_cell(payload)
                print(f"[complete] P={key['policy']} m={key['m']} shift={key['shift']:g} -> {path.name}", flush=True)
    out = manifest()
    (RESULTS / "campaign_manifest.json").write_text(canonical_json(out))
    print(f"campaign complete: {out['n_cells']} frozen cells")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error("workers must be in [1,16]")
    run(workers=args.workers, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
