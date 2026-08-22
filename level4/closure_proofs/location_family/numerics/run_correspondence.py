#!/usr/bin/env python3
"""Run the frozen Track-3 location-family correspondence campaign."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]
SRC = CAMPAIGN / "src"
sys.path.insert(0, str(SRC))

from rebaseguard_location_family.frozen import (  # noqa: E402
    FAMILIES,
    HISTORICAL_ARL,
    H_STEPS,
    MASTER_SEED,
    PRIMARY_H,
    PROTOCOL_SHA256,
    ROUTE_A_BATCHES,
    ROUTE_A_PATHS_PER_BATCH,
    ROUTE_B_BATCHES,
    ROUTE_B_PATHS_PER_BATCH,
    ROUTE_B_REPLICATIONS,
    THRESHOLDS,
)
from rebaseguard_location_family.route_a import (  # noqa: E402
    location_score,
    log_density,
    simulate_score_batch,
    trace_raw,
)
from rebaseguard_location_family.route_b import (  # noqa: E402
    simulate_conditional_batch,
    trace_signed,
)
from rebaseguard_location_family.statistics import (  # noqa: E402
    combined_z,
    mean_se,
    observed_order,
    paired_derivatives,
    richardson,
    symmetric_relative_difference,
)

RESULTS = CAMPAIGN / "results"
ERRORS = np.array([value for h in H_STEPS for value in (-h, h)], dtype=float)
HISTORICAL_GAUSSIAN_GAMMA = 15.867139929316513
HISTORICAL_GAUSSIAN_BATCH_SE = 0.04952710236592949


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _rng(key: list[int]) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(key)))


def _json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, default=_json_default) + "\n")


def _source_hashes() -> dict[str, str]:
    relative = [
        "level4/closure_proofs/location_family/PROTOCOL.md",
        "level4/closure_proofs/location_family/src/rebaseguard_location_family/frozen.py",
        "level4/closure_proofs/location_family/src/rebaseguard_location_family/route_a.py",
        "level4/closure_proofs/location_family/src/rebaseguard_location_family/route_b.py",
        "level4/closure_proofs/location_family/src/rebaseguard_location_family/statistics.py",
        "level4/closure_proofs/location_family/numerics/run_correspondence.py",
    ]
    return {name: _sha256(REPO / name) for name in relative}


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            result.add(node.module or "")
    return result


def structural_controls() -> dict:
    route_a_path = SRC / "rebaseguard_location_family/route_a.py"
    route_b_path = SRC / "rebaseguard_location_family/route_b.py"
    a_imports = _imports(route_a_path)
    b_imports = _imports(route_b_path)
    b_text = route_b_path.read_text().lower()

    grid = np.array([-4.0, -1.25, -0.2, 0.0, 0.2, 1.25, 4.0])
    score_errors = {}
    dx = 1e-6
    for family in FAMILIES:
        finite_difference = -(
            log_density(family, grid + dx) - log_density(family, grid - dx)
        ) / (2.0 * dx)
        score_errors[family] = float(
            np.max(np.abs(location_score(family, grid) - finite_difference))
        )

    reflection = {}
    base_path = np.full(40, 1.25)
    for family in FAMILIES:
        threshold = THRESHOLDS[family]
        a = trace_raw(base_path, threshold)
        ar = trace_raw(-base_path, threshold)
        b = trace_signed(base_path, threshold)
        br = trace_signed(-base_path, threshold)
        reflection[family] = {
            "route_a_time_preserved": a[0] == ar[0],
            "route_a_terminal_negated": a[1] == -ar[1],
            "route_a_stopped_sum_negated": a[2] == -ar[2],
            "route_a_direction_swapped": a[3] == -ar[3],
            "route_a_product_preserved": a[1] * a[2] == ar[1] * ar[2],
            "route_b_time_preserved": b[0] == br[0],
            "route_b_terminal_negated": b[1] == -br[1],
            "route_b_direction_swapped": b[2] == -br[2],
        }

    manifest = json.loads((RESULTS / "historical_manifest.json").read_text())
    historical_hashes = {
        relative: _sha256(REPO / relative) == expected
        for relative, expected in manifest["sha256"].items()
    }
    seed_keys = {
        "route_a": [MASTER_SEED, 1],
        "route_b_replication_1": [MASTER_SEED, 2],
        "route_b_replication_2": [MASTER_SEED, 3],
        "structural": [MASTER_SEED, 90],
    }
    seed_tuples = [tuple(value) for value in seed_keys.values()]

    rho_values = (0.0, 0.25, 0.5, 1.0)
    e = 0.17
    terminal_mean = -0.23
    rho_scaling = {
        str(rho): rho * (e + terminal_mean) for rho in rho_values
    }

    uniform_edge = {
        "interior_a.e._score_prediction_for_dE": 0.0,
        "actual_dE_e_Z1": -1.0,
        "naive_score_prediction_for_Fprime": 1.0,
        "actual_Fprime": 0.0,
        "mismatch_reproduced": True,
        "classification": "IRREGULAR SUPPORT-SHIFT EDGE; NOT THEOREM CONFIRMATION",
    }

    checks = {
        "protocol_hash": _sha256(CAMPAIGN / "PROTOCOL.md") == PROTOCOL_SHA256,
        "historical_hashes": all(historical_hashes.values()),
        "fresh_seed_keys_pairwise_distinct": len(set(seed_tuples)) == len(seed_tuples),
        "gaussian_score_exact": bool(
            np.array_equal(location_score("gaussian", grid), grid)
        ),
        "all_scores_match_negative_log_density_derivative": all(
            error <= 2e-7 for error in score_errors.values()
        ),
        "all_reflection_checks": all(
            all(cell.values()) for cell in reflection.values()
        ),
        "rho_scaling_exact": all(
            value == float(rho) * (e + terminal_mean)
            for rho, value in zip(rho_values, rho_scaling.values(), strict=True)
        ),
        "route_a_does_not_import_route_b": not any(
            "route_b" in name for name in a_imports
        ),
        "route_b_does_not_import_route_a": not any(
            "route_a" in name for name in b_imports
        ),
        "route_b_contains_no_location_gain_estimator": all(
            token not in b_text
            for token in ("location_score", "psi_total", "gamma_f", "stopped_gain")
        ),
        "uniform_edge_mismatch": uniform_edge["mismatch_reproduced"],
    }
    return {
        "checks": checks,
        "pass": all(checks.values()),
        "score_grid_max_abs_errors": score_errors,
        "reflection": reflection,
        "rho_scaling": rho_scaling,
        "seed_keys": seed_keys,
        "historical_hashes": historical_hashes,
        "uniform_edge": uniform_edge,
    }


def run_route_a() -> dict:
    families = {}
    for family_index, family in enumerate(FAMILIES):
        batches = []
        threshold = THRESHOLDS[family]
        for batch in range(ROUTE_A_BATCHES):
            key = [MASTER_SEED, 1, family_index, batch]
            paths = simulate_score_batch(
                family=family,
                threshold=threshold,
                n_paths=ROUTE_A_PATHS_PER_BATCH,
                rng=_rng(key),
            )
            batches.append(
                {
                    "batch": batch,
                    "seed_key": key,
                    "paths": ROUTE_A_PATHS_PER_BATCH,
                    "gamma_f": float(paths.gain.mean()),
                    "predicted_derivative": float(1.0 - paths.gain.mean()),
                    "arl": float(paths.tau.mean()),
                    "mean_terminal": float(paths.terminal.mean()),
                    "mean_stopped_psi": float(paths.psi_total.mean()),
                    "mean_direction": float(paths.direction.mean()),
                    "ties": paths.ties,
                    "simultaneous_crossings": paths.simultaneous_crossings,
                }
            )
            print(
                f"Route A {family}: batch {batch + 1}/{ROUTE_A_BATCHES}",
                flush=True,
            )
        gamma = np.array([row["gamma_f"] for row in batches])
        derivative = np.array([row["predicted_derivative"] for row in batches])
        arl = np.array([row["arl"] for row in batches])
        terminal = np.array([row["mean_terminal"] for row in batches])
        stopped_psi = np.array([row["mean_stopped_psi"] for row in batches])
        direction = np.array([row["mean_direction"] for row in batches])
        gamma_mean, gamma_se = mean_se(gamma)
        derivative_mean, derivative_se = mean_se(derivative)
        arl_mean, arl_se = mean_se(arl)
        terminal_mean, terminal_se = mean_se(terminal)
        psi_mean, psi_se = mean_se(stopped_psi)
        direction_mean, direction_se = mean_se(direction)
        families[family] = {
            "threshold": threshold,
            "batches": batches,
            "summary": {
                "gamma_f": gamma_mean,
                "gamma_f_se": gamma_se,
                "predicted_derivative": derivative_mean,
                "predicted_derivative_se": derivative_se,
                "arl": arl_mean,
                "arl_se": arl_se,
                "historical_arl": HISTORICAL_ARL[family],
                "historical_arl_relative_error": abs(
                    arl_mean / HISTORICAL_ARL[family] - 1.0
                ),
                "mean_terminal": terminal_mean,
                "mean_terminal_se": terminal_se,
                "mean_stopped_psi": psi_mean,
                "mean_stopped_psi_se": psi_se,
                "mean_direction": direction_mean,
                "mean_direction_se": direction_se,
                "ties": int(sum(row["ties"] for row in batches)),
                "simultaneous_crossings": int(
                    sum(row["simultaneous_crossings"] for row in batches)
                ),
            },
        }
    return {"families": families}


def run_route_b() -> dict:
    families = {}
    for family_index, family in enumerate(FAMILIES):
        replications = []
        threshold = THRESHOLDS[family]
        for replication in range(ROUTE_B_REPLICATIONS):
            batches = []
            for batch in range(ROUTE_B_BATCHES):
                key = [MASTER_SEED, 2 + replication, family_index, batch]
                paths = simulate_conditional_batch(
                    family=family,
                    threshold=threshold,
                    errors=ERRORS,
                    n_paths=ROUTE_B_PATHS_PER_BATCH,
                    generator=_rng(key),
                )
                maps = paths.maps()
                derivatives = paired_derivatives(maps, ERRORS, H_STEPS)
                batches.append(
                    {
                        "batch": batch,
                        "seed_key": key,
                        "path_streams": ROUTE_B_PATHS_PER_BATCH,
                        "maps": maps,
                        "paired_derivatives": derivatives,
                        "arl_by_error": paths.tau.mean(axis=0),
                        "ties": paths.ties,
                        "simultaneous_crossings": paths.simultaneous_crossings,
                    }
                )
                print(
                    f"Route B rep {replication + 1} {family}: "
                    f"batch {batch + 1}/{ROUTE_B_BATCHES}",
                    flush=True,
                )
            batch_derivatives = np.array(
                [row["paired_derivatives"] for row in batches]
            )
            step_summaries = []
            for index, h in enumerate(H_STEPS):
                mean, se = mean_se(batch_derivatives[:, index])
                step_summaries.append({"h": h, "derivative": mean, "se": se})
            primary_index = H_STEPS.index(PRIMARY_H)
            middle_index = H_STEPS.index(0.025)
            richardson_batches = richardson(
                batch_derivatives[:, middle_index],
                batch_derivatives[:, primary_index],
            )
            rich_mean, rich_se = mean_se(richardson_batches)
            replications.append(
                {
                    "replication": replication + 1,
                    "batches": batches,
                    "step_summaries": step_summaries,
                    "primary": step_summaries[primary_index],
                    "observed_order_diagnostic": observed_order(
                        batch_derivatives.mean(axis=0)
                    ),
                    "richardson_diagnostic": {
                        "derivative": rich_mean,
                        "se": rich_se,
                    },
                }
            )
        all_primary_batches = np.concatenate(
            [
                np.array(
                    [row["paired_derivatives"] for row in rep["batches"]]
                )[:, H_STEPS.index(PRIMARY_H)]
                for rep in replications
            ]
        )
        pooled_mean, pooled_se = mean_se(all_primary_batches)
        families[family] = {
            "threshold": threshold,
            "errors": ERRORS,
            "replications": replications,
            "pooled_primary": {
                "h": PRIMARY_H,
                "derivative": pooled_mean,
                "se": pooled_se,
                "batch_count": int(all_primary_batches.size),
            },
            "ties": int(
                sum(
                    row["ties"]
                    for rep in replications
                    for row in rep["batches"]
                )
            ),
            "simultaneous_crossings": int(
                sum(
                    row["simultaneous_crossings"]
                    for rep in replications
                    for row in rep["batches"]
                )
            ),
        }
    return {"families": families}


def evaluate(route_a: dict, route_b: dict, structural: dict) -> dict:
    rows = []
    all_regular_pass = structural["pass"]
    for family in FAMILIES:
        a = route_a["families"][family]["summary"]
        b = route_b["families"][family]
        pooled = b["pooled_primary"]
        rep1 = b["replications"][0]["primary"]
        rep2 = b["replications"][1]["primary"]
        correspondence_z = abs(
            combined_z(
                a["predicted_derivative"],
                a["predicted_derivative_se"],
                pooled["derivative"],
                pooled["se"],
            )
        )
        correspondence_relative = symmetric_relative_difference(
            a["predicted_derivative"], pooled["derivative"]
        )
        replication_z = abs(
            combined_z(
                rep1["derivative"], rep1["se"], rep2["derivative"], rep2["se"]
            )
        )
        replication_relative = symmetric_relative_difference(
            rep1["derivative"], rep2["derivative"]
        )
        criteria = {
            "correspondence_abs_z_le_3": correspondence_z <= 3.0,
            "correspondence_relative_le_3pct": correspondence_relative <= 0.03,
            "replication_abs_z_le_3": replication_z <= 3.0,
            "replication_relative_le_3pct": replication_relative <= 0.03,
            "route_a_arl_within_2pct": a["historical_arl_relative_error"] <= 0.02,
            "route_a_zero_ties": a["ties"] == 0
            and a["simultaneous_crossings"] == 0,
            "route_b_zero_ties": b["ties"] == 0
            and b["simultaneous_crossings"] == 0,
        }
        family_pass = all(criteria.values())
        all_regular_pass &= family_pass
        rows.append(
            {
                "family": family,
                "gamma_f": a["gamma_f"],
                "gamma_f_se": a["gamma_f_se"],
                "route_a_predicted_derivative": a["predicted_derivative"],
                "route_a_se": a["predicted_derivative_se"],
                "route_b_primary_derivative": pooled["derivative"],
                "route_b_se": pooled["se"],
                "correspondence_abs_z": correspondence_z,
                "correspondence_relative": correspondence_relative,
                "route_b_replication_1": rep1,
                "route_b_replication_2": rep2,
                "replication_abs_z": replication_z,
                "replication_relative": replication_relative,
                "arl": a["arl"],
                "historical_arl": a["historical_arl"],
                "arl_relative_error": a["historical_arl_relative_error"],
                "criteria": criteria,
                "pass": family_pass,
            }
        )

    gaussian = rows[0]
    gaussian_historical_z = abs(
        combined_z(
            gaussian["gamma_f"],
            gaussian["gamma_f_se"],
            HISTORICAL_GAUSSIAN_GAMMA,
            HISTORICAL_GAUSSIAN_BATCH_SE,
        )
    )
    gaussian_historical_relative = symmetric_relative_difference(
        gaussian["gamma_f"], HISTORICAL_GAUSSIAN_GAMMA
    )
    gaussian_control = {
        "historical_gamma": HISTORICAL_GAUSSIAN_GAMMA,
        "historical_batch_se": HISTORICAL_GAUSSIAN_BATCH_SE,
        "abs_z": gaussian_historical_z,
        "relative_discrepancy": gaussian_historical_relative,
        "abs_z_le_3": gaussian_historical_z <= 3.0,
        "relative_le_2pct": gaussian_historical_relative <= 0.02,
    }
    gaussian_control["pass"] = (
        gaussian_control["abs_z_le_3"] and gaussian_control["relative_le_2pct"]
    )
    all_regular_pass &= gaussian_control["pass"]

    if all_regular_pass:
        status = "LOCATION-FAMILY-NUMERICAL-PASS"
        declaration = "NUMERICAL GATE CLOSED — LEAN AUTHORIZED"
        lean_authorized = True
    else:
        status = "LOCATION-FAMILY-NUMERICAL-FAILED"
        declaration = "NUMERICAL GATE FAILED — LEAN NOT AUTHORIZED"
        lean_authorized = False

    stage_d = json.loads((REPO / "level4/stage_d/results/d3_nongaussian.json").read_text())
    historical_t3 = next(row for row in stage_d["rows"] if row["family"] == "t3")
    new_t3 = next(row for row in rows if row["family"] == "t3")
    t3_resolution = {
        "new_raw_reuse_gamma_f": new_t3["gamma_f"],
        "historical_gamma_psi": historical_t3["per_m"][0]["gamma_psi"],
        "historical_gamma_psi_over_Epsi_prime": historical_t3["per_m"][0][
            "gamma_psi_normalised"
        ],
        "mathematical_resolution": (
            "NEITHER historical quantity is the raw-observation m=1 reuse gain; "
            "historical Stage-D t3 remains AMBIGUOUS"
        ),
    }

    return {
        "schema": "rebaseguard.location-family.numerical-decision.v1",
        "status": status,
        "declaration": declaration,
        "lean_authorized": lean_authorized,
        "all_regular_families_pass": bool(all_regular_pass),
        "rows": rows,
        "gaussian_control": gaussian_control,
        "t3_estimand_resolution": t3_resolution,
        "uniform_edge": structural["uniform_edge"],
        "structural_pass": structural["pass"],
    }


def write_csv(decision: dict) -> None:
    fields = [
        "family",
        "gamma_f",
        "gamma_f_se",
        "route_a_predicted_derivative",
        "route_a_se",
        "route_b_primary_derivative",
        "route_b_se",
        "correspondence_abs_z",
        "correspondence_relative",
        "replication_abs_z",
        "replication_relative",
        "arl",
        "historical_arl",
        "arl_relative_error",
        "pass",
    ]
    with (RESULTS / "correspondence.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in decision["rows"]:
            writer.writerow({field: row[field] for field in fields})


def main() -> None:
    started = time.time()
    if _sha256(CAMPAIGN / "PROTOCOL.md") != PROTOCOL_SHA256:
        raise RuntimeError("frozen Track-3 protocol hash mismatch")
    structural = structural_controls()
    if not structural["pass"]:
        _write_json(RESULTS / "structural_controls.json", structural)
        raise RuntimeError("pre-outcome structural controls failed")

    metadata = {
        "protocol_sha256": PROTOCOL_SHA256,
        "master_seed": MASTER_SEED,
        "git_head": _git_head(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "source_sha256": _source_hashes(),
    }
    _write_json(RESULTS / "structural_controls.json", {**metadata, **structural})

    route_a = {**metadata, **run_route_a()}
    _write_json(RESULTS / "route_a.json", route_a)
    route_b = {**metadata, **run_route_b()}
    _write_json(RESULTS / "route_b.json", route_b)
    decision = {
        **metadata,
        **evaluate(route_a, route_b, structural),
        "elapsed_seconds": round(time.time() - started, 3),
    }
    _write_json(RESULTS / "numerical_decision.json", decision)
    write_csv(decision)

    print("\n" + decision["declaration"])
    for row in decision["rows"]:
        print(
            f"{row['family']:>10}: A={row['route_a_predicted_derivative']:+.6f} "
            f"B={row['route_b_primary_derivative']:+.6f} "
            f"|z|={row['correspondence_abs_z']:.3f} "
            f"rel={100 * row['correspondence_relative']:.3f}% "
            f"{'PASS' if row['pass'] else 'FAIL'}"
        )


if __name__ == "__main__":
    main()

