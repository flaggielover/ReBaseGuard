#!/usr/bin/env python3
"""Run and audit the frozen resumable Track-3A t3 campaign."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]
SRC = CAMPAIGN / "src"
RESULTS = CAMPAIGN / "results"
CHECKPOINTS = RESULTS / "checkpoints"
sys.path.insert(0, str(SRC))

from rebaseguard_location_family_track3ab.frozen import (  # noqa: E402
    ABS_Z_LIMIT,
    ARL_RELATIVE_LIMIT,
    BATCHES,
    HISTORICAL_ARL,
    H_STEPS,
    K,
    MASTER_SEED,
    PRIMARY_H,
    RELATIVE_LIMIT,
    REPLICATIONS,
    ROUTE_A_PATHS_PER_BATCH,
    ROUTE_B_PATHS_PER_BATCH,
    THRESHOLD,
)
from rebaseguard_location_family_track3ab.route_a import (  # noqa: E402
    simulate_score_batch,
    summarize_score_paths,
    t3_location_score,
)
from rebaseguard_location_family_track3ab.route_b import (  # noqa: E402
    simulate_conditional_batch,
    summarize_conditional_paths,
)
from rebaseguard_location_family_track3ab.statistics import (  # noqa: E402
    batch_diagnostics,
    combined_z,
    symmetric_relative_difference,
)


ERRORS = np.array([value for h in H_STEPS for value in (-h, h)], dtype=float)
PRIMARY_INDEX = H_STEPS.index(PRIMARY_H)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(payload, indent=2) + "\n")
    temporary.replace(path)


def rng(key: list[int]) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(key)))


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def verify_frozen_artifacts() -> tuple[str, str]:
    protocol = json.loads((RESULTS / "protocol_hash.json").read_text())
    protocol_hash = sha256(CAMPAIGN / "PROTOCOL.md")
    if protocol_hash != protocol["sha256"]:
        raise RuntimeError("PROTOCOL.md no longer matches its frozen hash")

    source_manifest = json.loads((RESULTS / "source_manifest.json").read_text())
    for relative, expected in source_manifest["sha256"].items():
        if sha256(REPO / relative) != expected:
            raise RuntimeError(f"frozen source changed: {relative}")

    historical = json.loads((RESULTS / "historical_manifest.json").read_text())
    for relative, expected in historical["sha256"].items():
        if sha256(REPO / relative) != expected:
            raise RuntimeError(f"historical artifact changed: {relative}")
    return protocol_hash, sha256(RESULTS / "source_manifest.json")


def checkpoint_path(route: str, replication: int, batch: int) -> Path:
    return (
        CHECKPOINTS
        / f"route_{route}_replication_{replication}"
        / f"batch_{batch:03d}.json"
    )


def expected_seed(route: str, replication: int, batch: int) -> list[int]:
    route_code = {"a": 10, "b": 20}[route]
    return [MASTER_SEED, route_code, replication, batch]


def validate_checkpoint(
    payload: dict, route: str, replication: int, batch: int, protocol_hash: str
) -> None:
    expected_paths = (
        ROUTE_A_PATHS_PER_BATCH if route == "a" else ROUTE_B_PATHS_PER_BATCH
    )
    if payload["route"] != route.upper():
        raise RuntimeError("checkpoint route mismatch")
    if payload["replication"] != replication or payload["batch"] != batch:
        raise RuntimeError("checkpoint coordinate mismatch")
    if payload["seed_key"] != expected_seed(route, replication, batch):
        raise RuntimeError("checkpoint seed mismatch")
    if payload["paths"] != expected_paths:
        raise RuntimeError("checkpoint path count mismatch")
    if payload["protocol_sha256"] != protocol_hash:
        raise RuntimeError("checkpoint protocol mismatch")


def run_route_a_batch(replication: int, batch: int, protocol_hash: str) -> dict:
    key = expected_seed("a", replication, batch)
    started = time.perf_counter()
    paths = simulate_score_batch(
        threshold=THRESHOLD,
        n_paths=ROUTE_A_PATHS_PER_BATCH,
        generator=rng(key),
    )
    summary = summarize_score_paths(paths)
    return {
        "schema": "rebaseguard.location-family-track3ab.route-a-batch.v1",
        "route": "A",
        "replication": replication,
        "batch": batch,
        "seed_key": key,
        "paths": ROUTE_A_PATHS_PER_BATCH,
        "protocol_sha256": protocol_hash,
        "elapsed_seconds": time.perf_counter() - started,
        **summary,
    }


def run_route_b_batch(replication: int, batch: int, protocol_hash: str) -> dict:
    key = expected_seed("b", replication, batch)
    started = time.perf_counter()
    paths = simulate_conditional_batch(
        threshold=THRESHOLD,
        errors=ERRORS,
        n_paths=ROUTE_B_PATHS_PER_BATCH,
        generator=rng(key),
    )
    summary = summarize_conditional_paths(paths, H_STEPS)
    return {
        "schema": "rebaseguard.location-family-track3ab.route-b-batch.v1",
        "route": "B",
        "replication": replication,
        "batch": batch,
        "seed_key": key,
        "paths": ROUTE_B_PATHS_PER_BATCH,
        "protocol_sha256": protocol_hash,
        "elapsed_seconds": time.perf_counter() - started,
        **summary,
    }


def run_batches(route: str, replication: int, protocol_hash: str) -> None:
    for batch in range(BATCHES):
        path = checkpoint_path(route, replication, batch)
        if path.exists():
            payload = json.loads(path.read_text())
            validate_checkpoint(payload, route, replication, batch, protocol_hash)
            continue
        if route == "a":
            payload = run_route_a_batch(replication, batch, protocol_hash)
        else:
            payload = run_route_b_batch(replication, batch, protocol_hash)
        write_json_atomic(path, payload)
        if (batch + 1) % 8 == 0 or batch == 0 or batch + 1 == BATCHES:
            print(
                f"Route {route.upper()} replication {replication}: "
                f"{batch + 1}/{BATCHES} checkpointed",
                flush=True,
            )


def load_route(route: str, replication: int, protocol_hash: str) -> list[dict]:
    rows = []
    for batch in range(BATCHES):
        path = checkpoint_path(route, replication, batch)
        if not path.exists():
            raise RuntimeError(f"missing checkpoint: {path.relative_to(REPO)}")
        payload = json.loads(path.read_text())
        validate_checkpoint(payload, route, replication, batch, protocol_hash)
        rows.append(payload)
    return rows


def summarize_route_a(rows: list[dict], replication: int) -> dict:
    gamma = np.array([row["gamma_f"] for row in rows])
    derivative = 1.0 - gamma
    arl = np.array([row["arl"] for row in rows])
    gamma_diag = batch_diagnostics(gamma)
    derivative_diag = batch_diagnostics(derivative)
    arl_diag = batch_diagnostics(arl)
    return {
        "replication": replication,
        "batches": BATCHES,
        "paths_per_batch": ROUTE_A_PATHS_PER_BATCH,
        "total_paths": BATCHES * ROUTE_A_PATHS_PER_BATCH,
        "gamma_f": gamma_diag,
        "predicted_derivative": derivative_diag,
        "arl": arl_diag,
        "historical_arl": HISTORICAL_ARL,
        "historical_arl_relative_error": abs(arl_diag["mean"] - HISTORICAL_ARL)
        / HISTORICAL_ARL,
        "gain_path_variance_mean": float(
            np.mean([row["gain_sample_variance"] for row in rows])
        ),
        "gain_min": float(min(row["gain_min"] for row in rows)),
        "gain_max": float(max(row["gain_max"] for row in rows)),
        "top_one_percent_abs_gain_variance_share_mean": float(
            np.mean([row["top_one_percent_abs_gain_variance_share"] for row in rows])
        ),
        "ties": int(sum(row["ties"] for row in rows)),
        "simultaneous_crossings": int(
            sum(row["simultaneous_crossings"] for row in rows)
        ),
    }


def summarize_route_b(rows: list[dict], replication: int) -> dict:
    derivatives = np.array([row["paired_derivatives"] for row in rows])
    maps = np.array([row["maps"] for row in rows])
    steps = []
    for index, h in enumerate(H_STEPS):
        diag = batch_diagnostics(derivatives[:, index])
        diag["h"] = h
        diag["mean_path_variance"] = float(
            np.mean([row["paired_derivative_path_variances"][index] for row in rows])
        )
        diag["mean_plus_minus_covariance"] = float(
            np.mean([row["plus_minus_covariances"][index] for row in rows])
        )
        diag["mean_plus_minus_correlation"] = float(
            np.mean([row["plus_minus_correlations"][index] for row in rows])
        )
        steps.append(diag)
    return {
        "replication": replication,
        "batches": BATCHES,
        "paths_per_batch": ROUTE_B_PATHS_PER_BATCH,
        "total_path_streams": BATCHES * ROUTE_B_PATHS_PER_BATCH,
        "steps": steps,
        "primary": steps[PRIMARY_INDEX],
        "maps_batch_mean": maps.mean(axis=0).tolist(),
        "ties": int(sum(row["ties"] for row in rows)),
        "simultaneous_crossings": int(
            sum(row["simultaneous_crossings"] for row in rows)
        ),
    }


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            result.add(node.module or "")
    return result


def structural_checks(protocol_hash: str) -> dict:
    route_a_path = SRC / "rebaseguard_location_family_track3ab/route_a.py"
    route_b_path = SRC / "rebaseguard_location_family_track3ab/route_b.py"
    a_imports = imports(route_a_path)
    b_imports = imports(route_b_path)
    b_text = route_b_path.read_text().lower()

    grid = np.array([-9.0, -2.0, -0.2, 0.0, 0.2, 2.0, 9.0])
    score_expected = 4.0 * grid / (1.0 + grid * grid)
    gaussian_grid = np.array([-3.0, -0.5, 0.0, 0.5, 3.0])
    gaussian_log_density_derivative = -gaussian_grid

    seed_keys = [
        tuple(expected_seed(route, replication, batch))
        for route in ("a", "b")
        for replication in range(1, REPLICATIONS + 1)
        for batch in range(BATCHES)
    ]
    checks = {
        "protocol_hash": sha256(CAMPAIGN / "PROTOCOL.md") == protocol_hash,
        "t3_score_formula": bool(np.array_equal(t3_location_score(grid), score_expected)),
        "t3_score_bound": bool(
            np.max(np.abs(t3_location_score(np.linspace(-100, 100, 200001))))
            <= 2.0 + 1e-14
        ),
        "gaussian_specialization_algebra": bool(
            np.array_equal(-gaussian_log_density_derivative, gaussian_grid)
        ),
        "route_a_does_not_import_route_b": not any("route_b" in name for name in a_imports),
        "route_b_does_not_import_route_a": not any("route_a" in name for name in b_imports),
        "route_b_has_no_score_gain_estimator": all(
            token not in b_text
            for token in ("location_score", "score_sum", "gamma_f", "stopped_gain")
        ),
        "seed_keys_pairwise_distinct": len(seed_keys) == len(set(seed_keys)),
        "fresh_master_seed_disjoint_from_track3": MASTER_SEED != 2026082307,
        "h_ladder_exact": H_STEPS == (0.05, 0.025, 0.0125),
        "primary_h_exact": PRIMARY_H == 0.0125,
        "inclusive_threshold_convention": K == 0.5 and THRESHOLD == 6.337011391962933,
    }
    return {"checks": checks, "pass": all(checks.values())}


def batch_identity_checks(a_rows: list[list[dict]], b_rows: list[list[dict]]) -> dict:
    map_errors = []
    score_errors = []
    for rows in a_rows:
        for row in rows:
            score_errors.append((1.0 - row["gamma_f"]) - (1.0 - row["gamma_f"]))
    for rows in b_rows:
        for row in rows:
            maps = np.asarray(row["maps"])
            for index, h in enumerate(H_STEPS):
                recomputed = (maps[2 * index + 1] - maps[2 * index]) / (2.0 * h)
                map_errors.append(recomputed - row["paired_derivatives"][index])
    return {
        "max_abs_route_a_derivative_identity_error": float(np.max(np.abs(score_errors))),
        "max_abs_route_b_map_identity_error": float(np.max(np.abs(map_errors))),
        "pass": bool(
            np.max(np.abs(score_errors)) <= 1e-15
            and np.max(np.abs(map_errors)) <= 2e-12
        ),
    }


def comparison(x: dict, y: dict) -> dict:
    relative = symmetric_relative_difference(x["mean"], y["mean"])
    z = abs(combined_z(x["mean"], x["se"], y["mean"], y["se"]))
    return {
        "x": x["mean"],
        "x_se": x["se"],
        "y": y["mean"],
        "y_se": y["se"],
        "symmetric_relative_difference": relative,
        "absolute_z": z,
        "relative_le_3pct": relative <= RELATIVE_LIMIT,
        "absolute_z_le_3": z <= ABS_Z_LIMIT,
        "pass": relative <= RELATIVE_LIMIT and z <= ABS_Z_LIMIT,
    }


def finalize(protocol_hash: str, source_manifest_hash: str) -> dict:
    a_rows = [load_route("a", rep, protocol_hash) for rep in range(1, 3)]
    b_rows = [load_route("b", rep, protocol_hash) for rep in range(1, 3)]
    a = [summarize_route_a(rows, rep) for rep, rows in enumerate(a_rows, 1)]
    b = [summarize_route_b(rows, rep) for rep, rows in enumerate(b_rows, 1)]

    for rep in range(2):
        write_json_atomic(RESULTS / f"route_a_replication_{rep + 1}.json", a[rep])
        write_json_atomic(RESULTS / f"route_b_replication_{rep + 1}.json", b[rep])

    per_replication = [
        comparison(a[rep]["predicted_derivative"], b[rep]["primary"])
        for rep in range(2)
    ]
    route_a_replication = comparison(
        a[0]["predicted_derivative"], a[1]["predicted_derivative"]
    )
    route_b_replication = comparison(b[0]["primary"], b[1]["primary"])

    pooled_a_values = np.concatenate(
        [np.array([1.0 - row["gamma_f"] for row in rows]) for rows in a_rows]
    )
    pooled_b_values = np.concatenate(
        [
            np.array([row["paired_derivatives"][PRIMARY_INDEX] for row in rows])
            for rows in b_rows
        ]
    )
    pooled_a = batch_diagnostics(pooled_a_values)
    pooled_b = batch_diagnostics(pooled_b_values)
    pooled = comparison(pooled_a, pooled_b)

    structural = structural_checks(protocol_hash)
    identities = batch_identity_checks(a_rows, b_rows)
    all_zero_ties = all(
        cell["ties"] == 0 and cell["simultaneous_crossings"] == 0
        for cell in a + b
    )
    arl_pass = all(
        cell["historical_arl_relative_error"] <= ARL_RELATIVE_LIMIT for cell in a
    )
    statistical = {
        "replication_1_route_a_vs_b": per_replication[0]["pass"],
        "replication_2_route_a_vs_b": per_replication[1]["pass"],
        "route_a_replication_agreement": route_a_replication["pass"],
        "route_b_replication_agreement": route_b_replication["pass"],
        "pooled_route_a_vs_b": pooled["pass"],
    }
    integrity = {
        "structural_checks": structural["pass"],
        "batch_identities": identities["pass"],
        "zero_ties_and_simultaneous_crossings": all_zero_ties,
        "route_a_arl_reproduction": arl_pass,
    }

    if all(integrity.values()) and all(statistical.values()):
        status = "T3A-NUMERICAL-PASS"
        lean_authorized = True
        gate_text = "NUMERICAL GATE CLOSED — LEAN AUTHORIZED"
    elif all(integrity.values()):
        status = "T3A-NUMERICAL-PARTIAL"
        lean_authorized = False
        gate_text = "NUMERICAL GATE NOT CLOSED — LEAN NOT AUTHORIZED"
    else:
        status = "T3A-NUMERICAL-FAILED"
        lean_authorized = False
        gate_text = "NUMERICAL INTEGRITY GATE FAILED — LEAN NOT AUTHORIZED"

    decision = {
        "schema": "rebaseguard.location-family-track3ab.numerical-decision.v1",
        "status": status,
        "gate": gate_text,
        "lean_authorized": lean_authorized,
        "protocol_sha256": protocol_hash,
        "source_manifest_sha256": source_manifest_hash,
        "git_head_at_completion": git_head(),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "sample_design": {
            "replications": REPLICATIONS,
            "batches_per_route_per_replication": BATCHES,
            "route_a_paths_per_batch": ROUTE_A_PATHS_PER_BATCH,
            "route_b_path_streams_per_batch": ROUTE_B_PATHS_PER_BATCH,
            "h_ladder": H_STEPS,
            "primary_h": PRIMARY_H,
        },
        "route_a": a,
        "route_b": b,
        "per_replication_correspondence": per_replication,
        "route_a_replication_agreement": route_a_replication,
        "route_b_replication_agreement": route_b_replication,
        "pooled": {
            "route_a": pooled_a,
            "route_b": pooled_b,
            "comparison": pooled,
        },
        "structural": structural,
        "batch_identities": identities,
        "statistical_gates": statistical,
        "integrity_gates": integrity,
        "relative_limit": RELATIVE_LIMIT,
        "absolute_z_limit": ABS_Z_LIMIT,
    }
    write_json_atomic(RESULTS / "numerical_decision.json", decision)
    print(status)
    print(gate_text)
    return decision


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", choices=("a", "b", "all"), default="all")
    parser.add_argument("--replication", choices=("1", "2", "all"), default="all")
    parser.add_argument(
        "--finalize-only",
        action="store_true",
        help="do not simulate; require every checkpoint and write the decision",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    protocol_hash, source_manifest_hash = verify_frozen_artifacts()
    if not args.finalize_only:
        routes = ("a", "b") if args.route == "all" else (args.route,)
        replications = (1, 2) if args.replication == "all" else (int(args.replication),)
        for replication in replications:
            for route in routes:
                run_batches(route, replication, protocol_hash)

    complete = all(
        checkpoint_path(route, replication, batch).exists()
        for route in ("a", "b")
        for replication in (1, 2)
        for batch in range(BATCHES)
    )
    if complete:
        finalize(protocol_hash, source_manifest_hash)
    else:
        print("campaign checkpointed but incomplete; rerun the same command to resume")


if __name__ == "__main__":
    main()
