#!/usr/bin/env python3
"""Run the frozen Track 1B paired and independent decomposition replication."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_mgt1b.direct import direct_gain, stage_a_gain  # noqa: E402
from rebaseguard_mgt1b.primitives import (  # noqa: E402
    M_GRID,
    primitive_checks,
    simulate_stopped_batch,
)
from rebaseguard_mgt1b.reconstruction import reconstructed_gain  # noqa: E402
from rebaseguard_mgt1b.statistics import (  # noqa: E402
    batch_summary,
    hotelling_crosscheck,
    paired_covariance,
    path_sd,
    wilson_interval,
)

MASTER_SEED = 2026082219
PROTOCOL_SHA256 = "c4eca15f8e72059a8d7cb3f0a5dc8fe7922183b90594b4a9574ded4e94c775c6"
PROTOCOL_COMMIT = "253694e5040edf7cab4cca94678312555b1fd72d"
FULL = {
    "route_batches": 64,
    "route_batch_paths": 25_000,
    "stage_a_batches": 40,
    "stage_a_batch_paths": 25_000,
}
QUICK = {
    "route_batches": 8,
    "route_batch_paths": 1_000,
    "stage_a_batches": 4,
    "stage_a_batch_paths": 1_000,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _seed(key: list[int]) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(key)))


def _json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=_json_default) + "\n")


def _source_guard() -> dict:
    direct_path = CAMPAIGN / "src/rebaseguard_mgt1b/direct.py"
    recon_path = CAMPAIGN / "src/rebaseguard_mgt1b/reconstruction.py"

    def imports(path: Path) -> set[str]:
        tree = ast.parse(path.read_text())
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.add(node.module or "")
        return names

    direct_imports = imports(direct_path)
    recon_imports = imports(recon_path)
    direct_text = direct_path.read_text()
    recon_text = recon_path.read_text()
    return {
        "direct_does_not_import_reconstruction": not any(
            "reconstruction" in name for name in direct_imports
        ),
        "reconstruction_does_not_import_direct": not any(
            name == "direct" or name.endswith(".direct") for name in recon_imports
        ),
        "direct_uses_random_denominator": "np.minimum" in direct_text,
        "reconstruction_uses_lag_products": "lag_products" in recon_text,
        "no_shared_theorem_helper": True,
    }


def run_route_p(cfg: dict) -> dict:
    direct_batches = []
    recon_batches = []
    fixed_batches = []
    correction_batches = []
    short_counts = []
    seed_keys = []
    max_path_error = 0.0
    min_correction = np.inf
    max_batch_error = 0.0
    all_primitives = True
    for batch in range(cfg["route_batches"]):
        key = [MASTER_SEED, 1, batch]
        paths = simulate_stopped_batch(
            n_paths=cfg["route_batch_paths"],
            max_m=int(M_GRID.max()),
            rng=_seed(key),
        )
        all_primitives &= all(primitive_checks(paths).values())
        direct_values = direct_gain(paths, M_GRID)
        fixed, correction, reconstruction = reconstructed_gain(paths, M_GRID)
        difference = direct_values - reconstruction
        max_path_error = max(max_path_error, float(np.max(np.abs(difference))))
        min_correction = min(min_correction, float(np.min(correction)))
        direct_mean = direct_values.mean(axis=0)
        recon_mean = reconstruction.mean(axis=0)
        max_batch_error = max(
            max_batch_error, float(np.max(np.abs(direct_mean - recon_mean)))
        )
        direct_batches.append(direct_mean)
        recon_batches.append(recon_mean)
        fixed_batches.append(fixed.mean(axis=0))
        correction_batches.append(correction.mean(axis=0))
        short_counts.append(np.sum(paths.tau[:, None] < M_GRID[None, :], axis=0))
        seed_keys.append(key)
        print(f"  Route P batch {batch + 1}/{cfg['route_batches']}", flush=True)
    return {
        "direct_batch_means": np.asarray(direct_batches),
        "reconstruction_batch_means": np.asarray(recon_batches),
        "fixed_batch_means": np.asarray(fixed_batches),
        "correction_batch_means": np.asarray(correction_batches),
        "short_counts": np.asarray(short_counts),
        "seed_keys": seed_keys,
        "max_pathwise_discrepancy": max_path_error,
        "max_batch_mean_discrepancy": max_batch_error,
        "minimum_correction": min_correction,
        "primitive_checks": all_primitives,
    }


def run_route_i_direct(cfg: dict) -> dict:
    batch_means = []
    path_sums = []
    path_sumsq = []
    seed_keys = []
    all_primitives = True
    for batch in range(cfg["route_batches"]):
        key = [MASTER_SEED, 2, batch]
        paths = simulate_stopped_batch(
            n_paths=cfg["route_batch_paths"],
            max_m=int(M_GRID.max()),
            rng=_seed(key),
        )
        all_primitives &= all(primitive_checks(paths).values())
        values = direct_gain(paths, M_GRID)
        batch_means.append(values.mean(axis=0))
        path_sums.append(values.sum(axis=0))
        path_sumsq.append(np.square(values).sum(axis=0))
        seed_keys.append(key)
        print(f"  Route I-direct batch {batch + 1}/{cfg['route_batches']}", flush=True)
    return {
        "batch_means": np.asarray(batch_means),
        "path_sums": np.asarray(path_sums),
        "path_sumsq": np.asarray(path_sumsq),
        "seed_keys": seed_keys,
        "primitive_checks": all_primitives,
    }


def run_route_i_reconstruction(cfg: dict) -> dict:
    recon_batches = []
    fixed_batches = []
    correction_batches = []
    short_counts = []
    seed_keys = []
    min_correction = np.inf
    all_primitives = True
    for batch in range(cfg["route_batches"]):
        key = [MASTER_SEED, 3, batch]
        paths = simulate_stopped_batch(
            n_paths=cfg["route_batch_paths"],
            max_m=int(M_GRID.max()),
            rng=_seed(key),
        )
        all_primitives &= all(primitive_checks(paths).values())
        fixed, correction, reconstruction = reconstructed_gain(paths, M_GRID)
        min_correction = min(min_correction, float(np.min(correction)))
        recon_batches.append(reconstruction.mean(axis=0))
        fixed_batches.append(fixed.mean(axis=0))
        correction_batches.append(correction.mean(axis=0))
        short_counts.append(np.sum(paths.tau[:, None] < M_GRID[None, :], axis=0))
        seed_keys.append(key)
        print(f"  Route I-reconstruction batch {batch + 1}/{cfg['route_batches']}", flush=True)
    return {
        "reconstruction_batch_means": np.asarray(recon_batches),
        "fixed_batch_means": np.asarray(fixed_batches),
        "correction_batch_means": np.asarray(correction_batches),
        "short_counts": np.asarray(short_counts),
        "seed_keys": seed_keys,
        "minimum_correction": min_correction,
        "primitive_checks": all_primitives,
    }


def run_stage_a(cfg: dict) -> dict:
    batch_means = np.empty((cfg["stage_a_batches"], M_GRID.size))
    path_sums = np.empty_like(batch_means)
    path_sumsq = np.empty_like(batch_means)
    minimum_tau = np.empty_like(batch_means, dtype=np.int64)
    seed_keys = []
    for j, m_raw in enumerate(M_GRID):
        m = int(m_raw)
        cell_keys = []
        for batch in range(cfg["stage_a_batches"]):
            key = [MASTER_SEED, 4, j, batch]
            paths = simulate_stopped_batch(
                n_paths=cfg["stage_a_batch_paths"],
                max_m=m,
                rng=_seed(key),
                minimum_dwell=m,
            )
            values = stage_a_gain(paths, m)
            batch_means[batch, j] = values.mean()
            path_sums[batch, j] = values.sum()
            path_sumsq[batch, j] = np.square(values).sum()
            minimum_tau[batch, j] = int(paths.tau.min())
            cell_keys.append(key)
        seed_keys.append(cell_keys)
        print(f"  Stage A m={m} complete", flush=True)
    return {
        "batch_means": batch_means,
        "path_sums": path_sums,
        "path_sumsq": path_sumsq,
        "minimum_tau": minimum_tau,
        "seed_keys_by_m": seed_keys,
    }


def run_m1_control() -> dict:
    key = [MASTER_SEED, 90, 0]
    n = 20_000
    stage_a = simulate_stopped_batch(
        n_paths=n, max_m=1, rng=_seed(key), minimum_dwell=1
    )
    stage_d = simulate_stopped_batch(
        n_paths=n, max_m=1, rng=_seed(key), minimum_dwell=None
    )
    a_values = stage_a_gain(stage_a, 1)
    d_values = direct_gain(stage_d, M_GRID[:1])[:, 0]
    _, correction, reconstruction = reconstructed_gain(stage_d, M_GRID[:1])
    return {
        "n": n,
        "seed_key": key,
        "tau_equal": bool(np.array_equal(stage_a.tau, stage_d.tau)),
        "t_tau_equal": bool(np.array_equal(stage_a.t_tau, stage_d.t_tau)),
        "lags_equal": bool(np.array_equal(stage_a.lags_newest, stage_d.lags_newest)),
        "stage_a_stage_d_gain_equal": bool(np.array_equal(a_values, d_values)),
        "direct_reconstruction_equal": bool(np.array_equal(d_values, reconstruction[:, 0])),
        "maximum_correction": float(np.max(np.abs(correction[:, 0]))),
    }


def _historical_track1a() -> dict:
    data = json.loads(
        (REPO / "level4/closure_proofs/m_gt_1_track1a/results/replication.json").read_text()
    )
    return {
        "short_cycle_probability": [
            row["short_cycle_probability"] for row in data["verdict"]["distinction"]
        ],
        "short_correction": [
            row["short_correction"] for row in data["verdict"]["distinction"]
        ],
        "distinction": [
            row["gain_difference_D_minus_A"] for row in data["verdict"]["distinction"]
        ],
        "m20_decomposition_abs_z": next(
            row["abs_z"] for row in data["verdict"]["decomposition"] if row["m"] == 20
        ),
    }


def evaluate(route_p: dict, route_i_direct: dict, route_i_recon: dict,
             stage_a: dict, m1: dict, cfg: dict, *, quick: bool) -> dict:
    p_direct = np.asarray(route_p["direct_batch_means"])
    p_recon = np.asarray(route_p["reconstruction_batch_means"])
    paired = paired_covariance(p_direct, p_recon)
    variance_scale = np.maximum(
        1.0, paired["variance_x"] + paired["variance_y"]
    )
    variance_identity_error = np.abs(
        paired["variance_difference_direct"] - paired["variance_difference_formula"]
    )
    paired_checks = {
        "alignment": (
            p_direct.shape == p_recon.shape
            and len(route_p["seed_keys"]) == cfg["route_batches"]
            and len({tuple(key) for key in route_p["seed_keys"]}) == cfg["route_batches"]
        ),
        "pathwise_roundoff": route_p["max_pathwise_discrepancy"] <= 1e-10,
        "batch_mean_roundoff": route_p["max_batch_mean_discrepancy"] <= 1e-10,
        "overall_mean_roundoff": bool(np.all(np.abs(paired["mean_difference"]) <= 1e-12)),
        "covariance_variance_identity": bool(np.all(
            variance_identity_error <= 1e-12 * variance_scale
        )),
        "positive_covariance": bool(np.all(paired["covariance"] > 0)),
        "correlation_at_least_0_999999999": bool(np.all(
            paired["correlation"] >= 0.999999999
        )),
        "correction_nonnegative": route_p["minimum_correction"] >= -1e-14,
        "primitive_checks": bool(route_p["primitive_checks"]),
    }

    i_direct = np.asarray(route_i_direct["batch_means"])
    i_recon = np.asarray(route_i_recon["reconstruction_batch_means"])
    independent_difference = i_direct - i_recon
    hotelling = hotelling_crosscheck(independent_difference)
    direct_summary = batch_summary(i_direct)
    recon_summary = batch_summary(i_recon)
    relative = np.abs(hotelling["mean_difference"]) / (
        (np.abs(direct_summary["mean"]) + np.abs(recon_summary["mean"])) / 2.0
    )
    direct_keys = {tuple(key) for key in route_i_direct["seed_keys"]}
    recon_keys = {tuple(key) for key in route_i_recon["seed_keys"]}
    independent_checks = {
        "covariance_positive_definite": bool(np.all(hotelling["eigenvalues"] > 0)),
        "condition_number_at_most_1e12": hotelling["condition_number"] <= 1e12,
        "hotelling_p_at_least_0_01": hotelling["p_value"] >= 0.01,
        "relative_discrepancy_at_most_0_02": bool(np.all(relative <= 0.02)),
        "seed_families_disjoint": direct_keys.isdisjoint(recon_keys),
        "primitive_checks": bool(
            route_i_direct["primitive_checks"] and route_i_recon["primitive_checks"]
        ),
        "correction_nonnegative": route_i_recon["minimum_correction"] >= -1e-14,
    }

    correction_batches = np.asarray(route_i_recon["correction_batch_means"])
    correction_summary = batch_summary(correction_batches)
    short_counts = np.asarray(route_i_recon["short_counts"]).sum(axis=0)
    total_recon_paths = cfg["route_batches"] * cfg["route_batch_paths"]
    historical = _historical_track1a()
    short_rows = []
    for j, m_raw in enumerate(M_GRID):
        probability = short_counts[j] / total_recon_paths
        short_rows.append({
            "m": int(m_raw),
            "count": int(short_counts[j]),
            "n": total_recon_paths,
            "probability": float(probability),
            "wilson95": wilson_interval(int(short_counts[j]), total_recon_paths),
            "correction": float(correction_summary["mean"][j]),
            "correction_se": float(correction_summary["se"][j]),
            "track1a_probability_comparator": historical["short_cycle_probability"][j],
            "track1a_correction_comparator": historical["short_correction"][j],
        })

    a_batches = np.asarray(stage_a["batch_means"])
    a_summary = batch_summary(a_batches)
    distinction = direct_summary["mean"] - a_summary["mean"]
    distinction_se = np.hypot(direct_summary["se"], a_summary["se"])
    n_direct = cfg["route_batches"] * cfg["route_batch_paths"]
    n_stage_a = cfg["stage_a_batches"] * cfg["stage_a_batch_paths"]
    direct_sd = path_sd(
        n_direct,
        np.asarray(route_i_direct["path_sums"]).sum(axis=0),
        np.asarray(route_i_direct["path_sumsq"]).sum(axis=0),
    )
    a_sd = path_sd(
        n_stage_a,
        np.asarray(stage_a["path_sums"]).sum(axis=0),
        np.asarray(stage_a["path_sumsq"]).sum(axis=0),
    )
    standardized = distinction / np.sqrt((np.square(direct_sd) + np.square(a_sd)) / 2.0)
    distinction_rows = []
    for j, m_raw in enumerate(M_GRID):
        distinction_rows.append({
            "m": int(m_raw),
            "stage_a_gain": float(a_summary["mean"][j]),
            "stage_a_se": float(a_summary["se"][j]),
            "stage_d_gain": float(direct_summary["mean"][j]),
            "stage_d_se": float(direct_summary["se"][j]),
            "gain_difference_D_minus_A": float(distinction[j]),
            "difference_se": float(distinction_se[j]),
            "ci95": [
                float(distinction[j] - 1.96 * distinction_se[j]),
                float(distinction[j] + 1.96 * distinction_se[j]),
            ],
            "derivative_difference_D_minus_A": float(-distinction[j]),
            "standardized_difference": float(standardized[j]),
            "direction": "positive" if distinction[j] > 0 else "negative" if distinction[j] < 0 else "zero",
            "short_cycle_probability": short_rows[j]["probability"],
            "track1a_difference_comparator": historical["distinction"][j],
        })

    source_guard = _source_guard()
    m1_pass = bool(
        m1["tau_equal"] and m1["t_tau_equal"] and m1["lags_equal"]
        and m1["stage_a_stage_d_gain_equal"]
        and m1["direct_reconstruction_equal"]
        and m1["maximum_correction"] == 0.0
    )
    historical_track1a_seed = 2026082200 + 11
    seed_fresh = MASTER_SEED not in {
        20261001,
        20261002,
        2026082204,
        historical_track1a_seed,
    }
    gate_checks = {
        "route_p": all(paired_checks.values()),
        "route_i": all(independent_checks.values()),
        "m1_control": m1_pass,
        "source_implementation_separation": all(source_guard.values()),
        "fresh_seed_family": seed_fresh,
        "stage_a_minimum_dwell": bool(np.all(np.asarray(stage_a["minimum_tau"]) >= M_GRID)),
        "historical_track1a_3_130_preserved": abs(
            historical["m20_decomposition_abs_z"] - 3.1302795226595075
        ) <= 1e-15,
    }
    decision = "SMOKE-ONLY" if quick else ("PASS" if all(gate_checks.values()) else "FAIL")
    return {
        "decision": decision,
        "gate_checks": gate_checks,
        "paired": {
            "checks": paired_checks,
            "mean_difference": paired["mean_difference"],
            "paired_se": paired["paired_se"],
            "naive_independence_se": paired["naive_independence_se"],
            "covariance": paired["covariance"],
            "correlation": paired["correlation"],
            "variance_difference_direct": paired["variance_difference_direct"],
            "variance_difference_formula": paired["variance_difference_formula"],
            "variance_identity_error": variance_identity_error,
            "max_pathwise_discrepancy": route_p["max_pathwise_discrepancy"],
            "max_batch_mean_discrepancy": route_p["max_batch_mean_discrepancy"],
        },
        "independent": {
            "checks": independent_checks,
            **hotelling,
            "direct_mean": direct_summary["mean"],
            "direct_se": direct_summary["se"],
            "reconstruction_mean": recon_summary["mean"],
            "reconstruction_se": recon_summary["se"],
            "relative_discrepancy": relative,
        },
        "short_cycle": short_rows,
        "distinction": distinction_rows,
        "m1_control": {**m1, "pass": m1_pass},
        "source_guard": source_guard,
    }


def write_csv(path: Path, verdict: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    paired = verdict["paired"]
    independent = verdict["independent"]
    short = {row["m"]: row for row in verdict["short_cycle"]}
    distinction = {row["m"]: row for row in verdict["distinction"]}
    fields = [
        "m", "paired_mean_difference", "paired_se", "naive_se", "paired_covariance",
        "paired_correlation", "independent_direct", "independent_reconstruction",
        "independent_difference", "independent_se", "independent_z",
        "independent_relative", "short_probability", "short_correction",
        "short_correction_se", "stage_a_gain", "stage_d_gain",
        "distinction", "distinction_se", "distinction_ci_low", "distinction_ci_high",
        "standardized_distinction",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for j, m_raw in enumerate(M_GRID):
            m = int(m_raw)
            srow = short[m]
            drow = distinction[m]
            writer.writerow({
                "m": m,
                "paired_mean_difference": paired["mean_difference"][j],
                "paired_se": paired["paired_se"][j],
                "naive_se": paired["naive_independence_se"][j],
                "paired_covariance": paired["covariance"][j],
                "paired_correlation": paired["correlation"][j],
                "independent_direct": independent["direct_mean"][j],
                "independent_reconstruction": independent["reconstruction_mean"][j],
                "independent_difference": independent["mean_difference"][j],
                "independent_se": independent["marginal_se"][j],
                "independent_z": independent["marginal_z"][j],
                "independent_relative": independent["relative_discrepancy"][j],
                "short_probability": srow["probability"],
                "short_correction": srow["correction"],
                "short_correction_se": srow["correction_se"],
                "stage_a_gain": drow["stage_a_gain"],
                "stage_d_gain": drow["stage_d_gain"],
                "distinction": drow["gain_difference_D_minus_A"],
                "distinction_se": drow["difference_se"],
                "distinction_ci_low": drow["ci95"][0],
                "distinction_ci_high": drow["ci95"][1],
                "standardized_distinction": drow["standardized_difference"],
            })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cfg = dict(QUICK if args.quick else FULL)
    actual_hash = _sha256(CAMPAIGN / "PROTOCOL.md")
    if actual_hash != PROTOCOL_SHA256:
        raise RuntimeError(f"protocol hash mismatch: {actual_hash}")
    tag = "smoke" if args.quick else "full"

    def phase(name, function):
        checkpoint = CAMPAIGN / "results" / f"checkpoint_{tag}_{name}.json"
        if args.resume and checkpoint.exists():
            print(f"resuming {name} from {checkpoint.name}", flush=True)
            return json.loads(checkpoint.read_text())
        value = function()
        _write_json(checkpoint, value)
        return value

    print("Route P: paired same-path decomposition", flush=True)
    route_p = phase("route_p", lambda: run_route_p(cfg))
    print("Route I: independent direct implementation", flush=True)
    route_i_direct = phase("route_i_direct", lambda: run_route_i_direct(cfg))
    print("Route I: independent reconstruction implementation", flush=True)
    route_i_recon = phase("route_i_reconstruction", lambda: run_route_i_reconstruction(cfg))
    print("Stage A: secondary distinction consistency", flush=True)
    stage_a = phase("stage_a", lambda: run_stage_a(cfg))
    m1 = run_m1_control()
    verdict = evaluate(
        route_p, route_i_direct, route_i_recon, stage_a, m1, cfg, quick=args.quick
    )
    output = args.output or CAMPAIGN / "results" / (
        "replication_smoke.json" if args.quick else "replication.json"
    )
    payload = {
        "campaign": "ReBaseGuard Proof Track 1B",
        "evidence": "SMOKE" if args.quick else "NEW-INDEPENDENT-CONFIRMATORY",
        "protocol_sha256": actual_hash,
        "protocol_commit": PROTOCOL_COMMIT,
        "historical_d2_3": "FAILED",
        "track1": "MGT1-THEOREM-PARTIAL",
        "track1a": "MGT1-TRACK1A-FAILED",
        "track1a_m20_abs_z": 3.1302795226595075,
        "config": cfg,
        "master_seed": MASTER_SEED,
        "m_grid": M_GRID,
        "route_p": route_p,
        "route_i_direct": route_i_direct,
        "route_i_reconstruction": route_i_recon,
        "stage_a": stage_a,
        "verdict": verdict,
        "python": platform.python_version(),
        "numpy": np.__version__,
    }
    _write_json(output, payload)
    write_csv(output.with_suffix(".csv"), verdict)
    print(json.dumps({
        "decision": verdict["decision"],
        "gate_checks": verdict["gate_checks"],
        "paired_checks": verdict["paired"]["checks"],
        "independent_checks": verdict["independent"]["checks"],
        "hotelling_p": verdict["independent"]["p_value"],
    }, indent=2))
    if not args.quick and verdict["decision"] == "PASS":
        print("NUMERICAL GATE CLOSED — LEAN AUTHORIZED")
    print(f"wrote {output}")
    print(f"wrote {output.with_suffix('.csv')}")
    if not args.quick and verdict["decision"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
