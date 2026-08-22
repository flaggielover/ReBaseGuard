#!/usr/bin/env python3
"""Execute the frozen Track-2 SR derivative numerical correspondence protocol."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
import scipy

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_sr_derivative import AUTHORITATIVE_A, MASTER_SEED  # noqa: E402
from rebaseguard_sr_derivative.calibration import (  # noqa: E402
    reproduce_sr_calibration,
    simulate_cusum_arl,
)
from rebaseguard_sr_derivative.log_sr import (  # noqa: E402
    classify_alarm_logs,
    run_log_path,
    simulate_paired_log_batch,
)
from rebaseguard_sr_derivative.raw_sr import (  # noqa: E402
    classify_alarm,
    run_raw_path,
    simulate_raw_arl,
    simulate_raw_paths,
)
from rebaseguard_sr_derivative.statistics import (  # noqa: E402
    MeanSE,
    independent_z,
    mean_se,
    one_sided_t_lower,
)

PROTOCOL_SHA256 = "e9b66ff8ffbf0d8138598b1d4dc19dcc1e44d8b4f33f5b462b5b82f341d5f762"
H_GRID = np.array([0.1, 0.05, 0.025, 0.0125])
PRIMARY_H = 0.0125

CAL_TARGET_PATHS = 800_000
CAL_SEARCH_PATHS = 200_000
CAL_FINAL_PATHS = 800_000
CAL_FIXED_BATCHES = 64
CAL_FIXED_PATHS = 10_000

ROUTE_A_BATCHES = 64
ROUTE_A_PATHS = 25_000
ROUTE_B_REPLICATIONS = 2
ROUTE_B_BATCHES = 64
ROUTE_B_PATHS = 12_500

HISTORICAL_GAMMA = 17.319830589555345
HISTORICAL_GAMMA_SE = 0.02800150922045604


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rng_for(*key: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence(key))


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def summary_json(summary: MeanSE) -> dict[str, float | int]:
    return {
        "mean": summary.mean,
        "se": summary.se,
        "batch_sd": summary.sd,
        "n_batches": summary.n,
    }


def provenance() -> dict[str, Any]:
    return {
        "git_head": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "protocol_sha256": PROTOCOL_SHA256,
        "threshold_decimal": "520.886133602749",
        "threshold_binary64_hex": AUTHORITATIVE_A.hex(),
        "master_seed": MASTER_SEED,
        "source_sha256": {
            path.relative_to(REPO).as_posix(): sha(path)
            for path in [
                CAMPAIGN / "src/rebaseguard_sr_derivative/raw_sr.py",
                CAMPAIGN / "src/rebaseguard_sr_derivative/log_sr.py",
                CAMPAIGN / "src/rebaseguard_sr_derivative/calibration.py",
                CAMPAIGN / "src/rebaseguard_sr_derivative/statistics.py",
                Path(__file__),
            ]
        },
    }


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


def structural_controls() -> dict[str, Any]:
    raw_source = CAMPAIGN / "src/rebaseguard_sr_derivative/raw_sr.py"
    log_source = CAMPAIGN / "src/rebaseguard_sr_derivative/log_sr.py"
    raw_imports = imported_modules(raw_source)
    log_imports = imported_modules(log_source)
    source_separated = not any(
        "log_sr" in module or "stage_d" in module for module in raw_imports
    ) and not any(
        "raw_sr" in module or "stage_d" in module for module in log_imports
    )

    paths = [
        np.array([0.1, -0.2, 0.4, 7.0]),
        np.array([-0.1, 0.3, -0.5, -7.0]),
        np.array([0.3, -0.1, 0.2, -0.4, 0.5]),
    ]
    correspondence = True
    for path in paths:
        raw = run_raw_path(path, threshold=AUTHORITATIVE_A)
        log = run_log_path(path, threshold=AUTHORITATIVE_A)
        correspondence &= raw.tau == log.tau
        correspondence &= raw.direction == log.direction
        correspondence &= raw.terminal_z == log.terminal_z
        correspondence &= raw.stopped_sum == log.stopped_sum
        correspondence &= bool(np.isclose(np.log1p(raw.r_plus), log.y_plus, rtol=2e-15))
        correspondence &= bool(np.isclose(np.log1p(raw.r_minus), log.y_minus, rtol=2e-15))

    reflect_path = np.array([0.2, -0.3, 0.1, 0.8, 8.0])
    raw_forward = run_raw_path(reflect_path, threshold=AUTHORITATIVE_A)
    raw_reflected = run_raw_path(-reflect_path, threshold=AUTHORITATIVE_A)
    log_forward = run_log_path(reflect_path, threshold=AUTHORITATIVE_A)
    log_reflected = run_log_path(-reflect_path, threshold=AUTHORITATIVE_A)
    reflection = all(
        [
            raw_forward.tau == raw_reflected.tau,
            raw_forward.terminal_z == -raw_reflected.terminal_z,
            raw_forward.stopped_sum == -raw_reflected.stopped_sum,
            raw_forward.r_plus == raw_reflected.r_minus,
            raw_forward.r_minus == raw_reflected.r_plus,
            log_forward.tau == log_reflected.tau,
            log_forward.terminal_z == -log_reflected.terminal_z,
            log_forward.stopped_sum == -log_reflected.stopped_sum,
            log_forward.y_plus == log_reflected.y_minus,
            log_forward.y_minus == log_reflected.y_plus,
        ]
    )

    raw_crossed, raw_direction, raw_both, raw_tie = classify_alarm(
        np.array([700.0, 600.0, 700.0]),
        np.array([600.0, 700.0, 700.0]),
        AUTHORITATIVE_A,
    )
    log_a = float(np.log(AUTHORITATIVE_A))
    log_crossed, log_direction, log_both, log_tie = classify_alarm_logs(
        np.array([log_a + 1.0, log_a + 0.2, log_a + 0.5]),
        np.array([log_a + 0.2, log_a + 1.0, log_a + 0.5]),
        log_a,
    )
    tie_rule = all(
        [
            np.array_equal(raw_crossed, [True, True, True]),
            np.array_equal(raw_direction, [1, -1, 0]),
            np.array_equal(raw_both, [True, True, True]),
            np.array_equal(raw_tie, [False, False, True]),
            np.array_equal(log_crossed, [True, True, True]),
            np.array_equal(log_direction, [1, -1, 0]),
            np.array_equal(log_both, [True, True, True]),
            np.array_equal(log_tie, [False, False, True]),
        ]
    )

    reuse = np.array([-2.0, 0.0, 3.0])
    fresh = np.array([0.5, -0.5, 1.0])
    rho = 0.37
    mixed = rho * reuse + (1.0 - rho) * fresh
    rho_rule = all(
        [
            np.array_equal(0.0 * reuse + fresh, fresh),
            np.array_equal(1.0 * reuse + 0.0 * fresh, reuse),
            np.allclose(mixed - (1.0 - rho) * fresh, rho * reuse),
        ]
    )
    seed_families = [
        {(MASTER_SEED, 1, 0)},
        {(MASTER_SEED, 1, 1, i) for i in range(30)},
        {(MASTER_SEED, 1, 2)},
        {(MASTER_SEED, 1, 3, b) for b in range(64)},
        {(MASTER_SEED, 1, 4, b) for b in range(64)},
        {(MASTER_SEED, 2, b) for b in range(64)},
        {(MASTER_SEED, 3, r, b) for r in range(2) for b in range(64)},
    ]
    seeds_disjoint = all(
        seed_families[i].isdisjoint(seed_families[j])
        for i in range(len(seed_families))
        for j in range(i + 1, len(seed_families))
    )
    checks = {
        "source_separation": source_separated,
        "raw_log_deterministic_correspondence": correspondence,
        "reflection": reflection,
        "simultaneous_and_exact_tie_rule": tie_rule,
        "rho_endpoints_and_interior": rho_rule,
        "seed_families_disjoint": seeds_disjoint,
        "threshold_binary64": AUTHORITATIVE_A.hex() == "0x1.04716cd36dd8dp+9",
        "protocol_hash": sha(CAMPAIGN / "PROTOCOL.md") == PROTOCOL_SHA256,
    }
    return {"checks": checks, "passed": all(checks.values())}


def run_calibration(results: Path, base: dict[str, Any]) -> dict[str, Any]:
    print("calibration: estimating fresh CUSUM target and SR bisection", flush=True)

    def show(iteration: int, threshold: float, arl: float, target: float) -> None:
        print(
            f"  bisection {iteration:02d}: A={threshold:.9f} "
            f"SR={arl:.4f} target={target:.4f}",
            flush=True,
        )

    reproduced = reproduce_sr_calibration(
        master_seed=MASTER_SEED,
        target_paths=CAL_TARGET_PATHS,
        search_paths=CAL_SEARCH_PATHS,
        final_paths=CAL_FINAL_PATHS,
        progress=show,
    )
    sr_batches = np.empty(CAL_FIXED_BATCHES)
    cusum_batches = np.empty(CAL_FIXED_BATCHES)
    for batch in range(CAL_FIXED_BATCHES):
        sr_batches[batch] = simulate_raw_arl(
            n_paths=CAL_FIXED_PATHS,
            threshold=AUTHORITATIVE_A,
            rng=rng_for(MASTER_SEED, 1, 3, batch),
        )
        cusum_batches[batch] = simulate_cusum_arl(
            n_paths=CAL_FIXED_PATHS,
            rng=rng_for(MASTER_SEED, 1, 4, batch),
        )
        if (batch + 1) % 8 == 0:
            print(f"  fixed-threshold ARL batches: {batch + 1}/64", flush=True)

    sr_summary = mean_se(sr_batches)
    cusum_summary = mean_se(cusum_batches)
    candidate_relative_error = abs(reproduced.candidate / AUTHORITATIVE_A - 1.0)
    fixed_ratio = sr_summary.mean / cusum_summary.mean
    criteria = {
        "candidate_within_2_percent": candidate_relative_error <= 0.02,
        "fixed_arl_ratio_within_1_percent": abs(fixed_ratio - 1.0) <= 0.01,
    }
    value = {
        **base,
        "design": {
            "target_paths": CAL_TARGET_PATHS,
            "search_paths_per_iteration": CAL_SEARCH_PATHS,
            "final_paths": CAL_FINAL_PATHS,
            "search_bracket": [100.0, 3000.0],
            "log_width_tolerance": 1e-3,
            "max_iterations": 30,
            "fixed_batches": CAL_FIXED_BATCHES,
            "fixed_paths_per_batch": CAL_FIXED_PATHS,
        },
        "bisection": {
            "target_cusum_arl": reproduced.target_cusum_arl,
            "iterations": reproduced.iterations,
            "final_bracket": [reproduced.lower, reproduced.upper],
            "candidate": reproduced.candidate,
            "candidate_relative_error": candidate_relative_error,
            "candidate_arl_fresh": reproduced.candidate_arl_fresh,
            "candidate_arl_ratio_to_target": (
                reproduced.candidate_arl_fresh / reproduced.target_cusum_arl
            ),
        },
        "fixed_operating_point": {
            "sr_batch_means": sr_batches.tolist(),
            "cusum_batch_means": cusum_batches.tolist(),
            "sr": summary_json(sr_summary),
            "cusum": summary_json(cusum_summary),
            "ratio": fixed_ratio,
            "relative_error": fixed_ratio - 1.0,
        },
        "criteria": criteria,
        "passed": all(criteria.values()),
    }
    atomic_json(results / "calibration.json", value)
    return value


def run_route_a(results: Path, base: dict[str, Any]) -> dict[str, Any]:
    print("Route A: raw-state stopped-score batches", flush=True)
    gamma_batches = np.empty(ROUTE_A_BATCHES)
    arl_batches = np.empty(ROUTE_A_BATCHES)
    z_terminal_batches = np.empty(ROUTE_A_BATCHES)
    stopped_sum_batches = np.empty(ROUTE_A_BATCHES)
    direction_batches = np.empty(ROUTE_A_BATCHES)
    simultaneous_counts = np.zeros(ROUTE_A_BATCHES, dtype=np.int64)
    tie_counts = np.zeros(ROUTE_A_BATCHES, dtype=np.int64)
    rows: list[dict[str, Any]] = []
    for batch in range(ROUTE_A_BATCHES):
        stopped = simulate_raw_paths(
            n_paths=ROUTE_A_PATHS,
            threshold=AUTHORITATIVE_A,
            rng=rng_for(MASTER_SEED, 2, batch),
        )
        gamma_batches[batch] = stopped.product.mean()
        arl_batches[batch] = stopped.tau.mean()
        z_terminal_batches[batch] = stopped.terminal_z.mean()
        stopped_sum_batches[batch] = stopped.stopped_sum.mean()
        direction_batches[batch] = stopped.direction.mean()
        simultaneous_counts[batch] = np.count_nonzero(stopped.simultaneous)
        tie_counts[batch] = np.count_nonzero(stopped.exact_tie)
        rows.append(
            {
                "batch": batch,
                "seed_key": [MASTER_SEED, 2, batch],
                "n_paths": ROUTE_A_PATHS,
                "gamma": gamma_batches[batch],
                "arl": arl_batches[batch],
                "mean_terminal_z": z_terminal_batches[batch],
                "mean_stopped_sum": stopped_sum_batches[batch],
                "mean_direction": direction_batches[batch],
                "simultaneous_crossings": int(simultaneous_counts[batch]),
                "exact_ties": int(tie_counts[batch]),
            }
        )
        if (batch + 1) % 8 == 0:
            print(f"  Route A batches: {batch + 1}/64", flush=True)

    gamma = mean_se(gamma_batches)
    derivative = MeanSE(1.0 - gamma.mean, gamma.se, gamma.sd, gamma.n)
    historical = MeanSE(
        HISTORICAL_GAMMA,
        HISTORICAL_GAMMA_SE,
        float("nan"),
        0,
    )
    z_historical = independent_z(gamma, historical)
    lower_99 = one_sided_t_lower(gamma, confidence=0.995)
    criteria = {
        "historical_gamma_within_4_combined_se": abs(z_historical) <= 4.0,
        "batch_99_percent_lower_bound_above_2": lower_99 > 2.0,
        "zero_exact_ties": int(tie_counts.sum()) == 0,
        "batch_and_path_counts": len(rows) == 64
        and all(row["n_paths"] == 25_000 for row in rows),
    }
    value = {
        **base,
        "design": {
            "batches": ROUTE_A_BATCHES,
            "paths_per_batch": ROUTE_A_PATHS,
            "total_paths": ROUTE_A_BATCHES * ROUTE_A_PATHS,
            "seed_family": [MASTER_SEED, 2, "batch"],
            "state": "raw",
        },
        "batches": rows,
        "summary": {
            "gamma": summary_json(gamma),
            "predicted_derivative": summary_json(derivative),
            "arl": summary_json(mean_se(arl_batches)),
            "mean_terminal_z": summary_json(mean_se(z_terminal_batches)),
            "mean_stopped_sum": summary_json(mean_se(stopped_sum_batches)),
            "mean_direction": summary_json(mean_se(direction_batches)),
            "simultaneous_crossings": int(simultaneous_counts.sum()),
            "exact_ties": int(tie_counts.sum()),
            "historical_gamma": HISTORICAL_GAMMA,
            "historical_gamma_se": HISTORICAL_GAMMA_SE,
            "historical_combined_z": z_historical,
            "batch_t_lower_99": lower_99,
            "lower_bound_status": "CONFIRMATORY NUMERICAL ONLY",
        },
        "criteria": criteria,
        "passed": all(criteria.values()),
    }
    atomic_json(results / "route_a.json", value)
    return value


def run_route_b(
    results: Path,
    base: dict[str, Any],
    route_a: dict[str, Any],
) -> dict[str, Any]:
    print("Route B: independent log-state paired finite differences", flush=True)
    derivatives = np.empty((ROUTE_B_REPLICATIONS, ROUTE_B_BATCHES, H_GRID.size))
    map_plus = np.empty_like(derivatives)
    map_minus = np.empty_like(derivatives)
    tie_counts = np.zeros((ROUTE_B_REPLICATIONS, ROUTE_B_BATCHES), dtype=np.int64)
    simultaneous_counts = np.zeros_like(tie_counts)
    rows: list[dict[str, Any]] = []
    for replication in range(ROUTE_B_REPLICATIONS):
        for batch in range(ROUTE_B_BATCHES):
            stopped = simulate_paired_log_batch(
                n_paths=ROUTE_B_PATHS,
                threshold=AUTHORITATIVE_A,
                h_grid=H_GRID,
                rng=rng_for(MASTER_SEED, 3, replication, batch),
            )
            condition_means = stopped.map_output.mean(axis=2)
            derivatives[replication, batch] = stopped.derivatives
            map_plus[replication, batch] = condition_means[:, 0]
            map_minus[replication, batch] = condition_means[:, 1]
            tie_counts[replication, batch] = np.count_nonzero(stopped.exact_tie)
            simultaneous_counts[replication, batch] = np.count_nonzero(
                stopped.simultaneous
            )
            rows.append(
                {
                    "replication": replication,
                    "batch": batch,
                    "seed_key": [MASTER_SEED, 3, replication, batch],
                    "n_paths_per_sign_step": ROUTE_B_PATHS,
                    "map_plus": condition_means[:, 0].tolist(),
                    "map_minus": condition_means[:, 1].tolist(),
                    "paired_derivative": stopped.derivatives.tolist(),
                    "mean_tau_plus": stopped.tau[:, 0, :].mean(axis=1).tolist(),
                    "mean_tau_minus": stopped.tau[:, 1, :].mean(axis=1).tolist(),
                    "simultaneous_crossings": int(
                        simultaneous_counts[replication, batch]
                    ),
                    "exact_ties": int(tie_counts[replication, batch]),
                }
            )
            if (batch + 1) % 8 == 0:
                print(
                    f"  Route B replication {replication + 1}/2: "
                    f"{batch + 1}/64 batches",
                    flush=True,
                )

    h_summaries: list[dict[str, Any]] = []
    replication_summaries: list[list[MeanSE]] = []
    for replication in range(ROUTE_B_REPLICATIONS):
        replication_summaries.append(
            [mean_se(derivatives[replication, :, index]) for index in range(H_GRID.size)]
        )
    pooled_summaries = [
        mean_se(derivatives[:, :, index].reshape(-1)) for index in range(H_GRID.size)
    ]
    for index, h in enumerate(H_GRID):
        h_summaries.append(
            {
                "h": float(h),
                "replications": [
                    summary_json(replication_summaries[replication][index])
                    for replication in range(ROUTE_B_REPLICATIONS)
                ],
                "pooled": summary_json(pooled_summaries[index]),
            }
        )

    primary_index = int(np.flatnonzero(H_GRID == PRIMARY_H)[0])
    primary_replications = [
        replication_summaries[replication][primary_index]
        for replication in range(ROUTE_B_REPLICATIONS)
    ]
    primary_pooled = pooled_summaries[primary_index]
    route_a_derivative = MeanSE(
        **{
            "mean": route_a["summary"]["predicted_derivative"]["mean"],
            "se": route_a["summary"]["predicted_derivative"]["se"],
            "sd": route_a["summary"]["predicted_derivative"]["batch_sd"],
            "n": route_a["summary"]["predicted_derivative"]["n_batches"],
        }
    )
    pooled_z = independent_z(primary_pooled, route_a_derivative)
    replication_z = [
        independent_z(summary, route_a_derivative) for summary in primary_replications
    ]
    replication_agreement_z = independent_z(
        primary_replications[0], primary_replications[1]
    )
    relative_discrepancy = abs(
        primary_pooled.mean - route_a_derivative.mean
    ) / abs(route_a_derivative.mean)
    richardson_batches = (
        4.0 * derivatives[:, :, primary_index]
        - derivatives[:, :, primary_index - 1]
    ) / 3.0
    richardson = mean_se(richardson_batches.reshape(-1))
    order_differences = [
        abs(pooled_summaries[index].mean - pooled_summaries[index + 1].mean)
        for index in range(H_GRID.size - 1)
    ]
    observed_orders = [
        float(np.log2(order_differences[index] / order_differences[index + 1]))
        if order_differences[index + 1] > 0.0
        else None
        for index in range(len(order_differences) - 1)
    ]
    criteria = {
        "pooled_finest_abs_z_at_most_3": abs(pooled_z) <= 3.0,
        "each_replication_abs_z_at_most_4": all(abs(z) <= 4.0 for z in replication_z),
        "replications_agree_within_3_combined_se": (
            abs(replication_agreement_z) <= 3.0
        ),
        "pooled_relative_discrepancy_at_most_2_percent": (
            relative_discrepancy <= 0.02
        ),
        "zero_exact_ties": int(tie_counts.sum()) == 0,
        "batch_path_and_seed_alignment": len(rows) == 128
        and all(row["n_paths_per_sign_step"] == 12_500 for row in rows),
        "source_and_seed_separation": structural_controls()["passed"],
    }
    value = {
        **base,
        "design": {
            "replications": ROUTE_B_REPLICATIONS,
            "batches_per_replication": ROUTE_B_BATCHES,
            "paths_per_sign_step_batch": ROUTE_B_PATHS,
            "h_grid": H_GRID.tolist(),
            "primary_h": PRIMARY_H,
            "seed_family": [MASTER_SEED, 3, "replication", "batch"],
            "state": "log",
            "uncertainty_unit": "paired batch derivative",
            "crn": "full innovation vector per path/time shared across signs and h ladder",
        },
        "batches": rows,
        "summaries": h_summaries,
        "primary": {
            "route_a_prediction": summary_json(route_a_derivative),
            "pooled": summary_json(primary_pooled),
            "replications": [summary_json(item) for item in primary_replications],
            "pooled_z_vs_route_a": pooled_z,
            "replication_z_vs_route_a": replication_z,
            "replication_agreement_z": replication_agreement_z,
            "relative_discrepancy": relative_discrepancy,
        },
        "secondary_diagnostics": {
            "richardson": summary_json(richardson),
            "successive_absolute_differences": order_differences,
            "observed_orders": observed_orders,
            "controls_verdict": "DIAGNOSTIC ONLY; CANNOT FAIL OR RESCUE PRIMARY",
        },
        "simultaneous_crossings": int(simultaneous_counts.sum()),
        "exact_ties": int(tie_counts.sum()),
        "criteria": criteria,
        "passed": all(criteria.values()),
    }
    atomic_json(results / "route_b.json", value)
    return value


def write_correspondence_csv(
    path: Path, route_a: dict[str, Any], route_b: dict[str, Any]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", newline="", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["route", "replication", "h", "estimate", "se", "role"],
        )
        writer.writeheader()
        prediction = route_a["summary"]["predicted_derivative"]
        writer.writerow(
            {
                "route": "A_raw_score",
                "replication": "",
                "h": "",
                "estimate": prediction["mean"],
                "se": prediction["se"],
                "role": "theorem prediction",
            }
        )
        for row in route_b["summaries"]:
            for replication, summary in enumerate(row["replications"]):
                writer.writerow(
                    {
                        "route": "B_log_conditional_map",
                        "replication": replication,
                        "h": row["h"],
                        "estimate": summary["mean"],
                        "se": summary["se"],
                        "role": "primary" if row["h"] == PRIMARY_H else "diagnostic",
                    }
                )
            writer.writerow(
                {
                    "route": "B_log_conditional_map_pooled",
                    "replication": "pooled",
                    "h": row["h"],
                    "estimate": row["pooled"]["mean"],
                    "se": row["pooled"]["se"],
                    "role": "primary" if row["h"] == PRIMARY_H else "diagnostic",
                }
            )
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> int:
    started = time.time()
    if sha(CAMPAIGN / "PROTOCOL.md") != PROTOCOL_SHA256:
        raise SystemExit("frozen protocol hash mismatch")
    results = CAMPAIGN / "results"
    base = provenance()
    controls = structural_controls()
    atomic_json(results / "structural_controls.json", {**base, **controls})
    if not controls["passed"]:
        raise SystemExit("blocking structural control failed before outcomes")
    print("structural controls: PASS", flush=True)

    calibration = run_calibration(results, base)
    route_a = run_route_a(results, base)
    route_b = run_route_b(results, base, route_a)
    write_correspondence_csv(results / "correspondence.csv", route_a, route_b)

    criteria = {
        "structural_controls": controls["passed"],
        "calibration": calibration["passed"],
        "route_a": route_a["passed"],
        "route_b": route_b["passed"],
    }
    passed = all(criteria.values())
    decision = {
        **base,
        "criteria": criteria,
        "passed": passed,
        "decision": (
            "NUMERICAL GATE CLOSED — LEAN AUTHORIZED"
            if passed
            else "NUMERICAL GATE FAILED — LEAN NOT AUTHORIZED"
        ),
        "track_status_if_stopped_here": (
            "SR-DERIVATIVE-PARTIAL" if not passed else "NUMERICAL-PASS-PENDING-LEAN"
        ),
        "gamma_inequality_status": "CONFIRMATORY NUMERICAL ONLY",
        "rigorous_sr_local_instability_certificate": "OPEN",
        "elapsed_seconds": time.time() - started,
    }
    atomic_json(results / "numerical_decision.json", decision)
    print(decision["decision"], flush=True)
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

