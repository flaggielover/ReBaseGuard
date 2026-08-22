#!/usr/bin/env python3
"""Run the protocol-frozen Track 1A gain and decomposition replication."""

from __future__ import annotations

import argparse
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

from rebaseguard_mgt1a.analysis import (  # noqa: E402
    Moments,
    inverse_variance_pool,
    wilson_interval,
)
from rebaseguard_mgt1a.model import (  # noqa: E402
    M_GRID,
    RHO_GRID,
    gamma_components,
    predicted_derivative,
    stage_a_integrand,
)
from rebaseguard_mgt1a.simulate import simulate_stopped_batch  # noqa: E402

MASTER_SEED = 2026082211
PROTOCOL_SHA256 = "76a5d40b4165758afb72a12dd93f302dd03cbf7db78184ef248156962cc9a79f"
PROTOCOL_COMMIT = "13e497564d5440bc5ea0ae528df682653139ec2c"
FULL = {"n_paths": 1_000_000, "batch": 50_000, "replicates": 2}
QUICK = {"n_paths": 4_000, "batch": 1_000, "replicates": 2}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _seed(parts: list[int]) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(parts)))


def _batches(n: int, size: int):
    left = n
    index = 0
    while left:
        take = min(left, size)
        yield index, take
        index += 1
        left -= take


def _json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=_json_default) + "\n")


def _record(moment: Moments) -> dict:
    return {
        "n": moment.n,
        "estimate": moment.mean.tolist(),
        "se": moment.se.tolist(),
        "sd": moment.sd.tolist(),
    }


def run_stage_a(cfg: dict) -> list[dict]:
    records = []
    for rep in range(cfg["replicates"]):
        gain = Moments.zeros((M_GRID.size,))
        tau_mean = np.zeros(M_GRID.size)
        min_tau = np.zeros(M_GRID.size, dtype=np.int64)
        seed_keys = []
        for j, m_raw in enumerate(M_GRID):
            m = int(m_raw)
            cell = Moments.zeros((1,))
            tau_total = 0
            cell_min = np.iinfo(np.int64).max
            cell_keys = []
            for bi, size in _batches(cfg["n_paths"], cfg["batch"]):
                key = [MASTER_SEED, 1, rep, j, bi]
                stopped = simulate_stopped_batch(
                    n_paths=size,
                    m_grid=np.array([m]),
                    rng=_seed(key),
                    minimum_dwell=m,
                )
                values = stage_a_integrand(
                    stopped.window_sum[:, 0], stopped.t_tau, m
                )
                cell.add(values[:, None])
                tau_total += int(stopped.tau.sum())
                cell_min = min(cell_min, int(stopped.tau.min()))
                cell_keys.append(key)
            gain.n = cell.n
            gain.total[j] = cell.total[0]
            gain.total_sq[j] = cell.total_sq[0]
            tau_mean[j] = tau_total / cell.n
            min_tau[j] = cell_min
            seed_keys.append(cell_keys)
            print(f"  Stage A rep={rep} m={m} complete", flush=True)
        records.append({
            "replicate": rep,
            "gain": _record(gain),
            "derivative": (1.0 - gain.mean).tolist(),
            "derivative_se": gain.se.tolist(),
            "mean_tau_m": tau_mean.tolist(),
            "minimum_tau_m": min_tau.tolist(),
            "seed_keys_by_m": seed_keys,
        })
    return records


def run_stage_d(cfg: dict, route: int) -> list[dict]:
    if route not in (2, 3):
        raise ValueError("Stage-D route must be 2 or 3")
    records = []
    m_float = M_GRID.astype(float)
    for rep in range(cfg["replicates"]):
        direct = Moments.zeros((M_GRID.size,))
        fixed = Moments.zeros((M_GRID.size,))
        correction = Moments.zeros((M_GRID.size,))
        reconstruction = Moments.zeros((M_GRID.size,))
        short = np.zeros(M_GRID.size, dtype=np.int64)
        max_identity_error = 0.0
        minimum_correction = np.inf
        tau_total = 0
        seed_keys = []
        for bi, size in _batches(cfg["n_paths"], cfg["batch"]):
            key = [MASTER_SEED, route, rep, bi]
            stopped = simulate_stopped_batch(
                n_paths=size,
                m_grid=M_GRID,
                rng=_seed(key),
                minimum_dwell=None,
            )
            vd = stopped.window_mean * stopped.t_tau[:, None]
            vb = stopped.window_sum / m_float[None, :] * stopped.t_tau[:, None]
            vc = np.where(
                stopped.tau[:, None] < M_GRID[None, :],
                (1.0 / stopped.tau[:, None] - 1.0 / m_float[None, :])
                * np.square(stopped.t_tau[:, None]),
                0.0,
            )
            for j, m_raw in enumerate(M_GRID):
                ca, cb, cc = gamma_components(
                    stopped.tau,
                    stopped.t_tau,
                    stopped.window_sum[:, j],
                    int(m_raw),
                )
                max_identity_error = max(
                    max_identity_error,
                    float(np.max(np.abs(ca - cb - cc))),
                    float(np.max(np.abs(vd[:, j] - vb[:, j] - vc[:, j]))),
                )
            minimum_correction = min(minimum_correction, float(vc.min()))
            direct.add(vd)
            fixed.add(vb)
            correction.add(vc)
            reconstruction.add(vb + vc)
            short += np.sum(stopped.tau[:, None] < M_GRID[None, :], axis=0)
            tau_total += int(stopped.tau.sum())
            seed_keys.append(key)
        intervals = [wilson_interval(int(count), direct.n) for count in short]
        records.append({
            "replicate": rep,
            "route": route,
            "direct_gain": _record(direct),
            "fixed_denominator_gain": _record(fixed),
            "short_correction": _record(correction),
            "reconstruction": _record(reconstruction),
            "short_cycle_count": short.tolist(),
            "short_cycle_probability": (short / direct.n).tolist(),
            "short_cycle_wilson95": intervals,
            "mean_tau": tau_total / direct.n,
            "max_pathwise_decomposition_error": max_identity_error,
            "minimum_pathwise_correction": minimum_correction,
            "seed_keys": seed_keys,
        })
        print(f"  Stage D route={route} rep={rep} complete", flush=True)
    return records


def run_m1_shared_control() -> dict:
    key = [MASTER_SEED, 90, 0]
    n = 20_000
    stage_a = simulate_stopped_batch(
        n_paths=n,
        m_grid=np.array([1]),
        rng=_seed(key),
        minimum_dwell=1,
    )
    stage_d = simulate_stopped_batch(
        n_paths=n,
        m_grid=np.array([1]),
        rng=_seed(key),
        minimum_dwell=None,
    )
    va = stage_a_integrand(stage_a.window_sum[:, 0], stage_a.t_tau, 1)
    vd, _, correction = gamma_components(
        stage_d.tau, stage_d.t_tau, stage_d.window_sum[:, 0], 1
    )
    return {
        "n": n,
        "seed_key": key,
        "tau_equal": bool(np.array_equal(stage_a.tau, stage_d.tau)),
        "window_equal": bool(np.array_equal(stage_a.window_sum, stage_d.window_sum)),
        "gain_integrand_equal": bool(np.array_equal(va, vd)),
        "maximum_gain_error": float(np.max(np.abs(va - vd))),
        "maximum_correction": float(np.max(np.abs(correction))),
    }


def _prior_m1() -> tuple[float, float]:
    previous = json.loads(
        (REPO / "level4/closure_proofs/m_gt_1/results/correspondence.json").read_text()
    )
    values = np.array([row["gamma_tilde"][0] for row in previous["route_a"]])
    ses = np.array([row["gamma_tilde_se"][0] for row in previous["route_a"]])
    estimate, se = inverse_variance_pool(values, ses)
    return float(estimate), float(se)


def _aggregate_serialized_moments(records: list[dict], field: str) -> tuple[np.ndarray, np.ndarray]:
    """Combine retained raw-moment equivalents when an IV SE is exactly zero."""
    counts = np.array([row[field]["n"] for row in records], dtype=np.int64)
    means = np.array([row[field]["estimate"] for row in records], dtype=float)
    sds = np.array([row[field]["sd"] for row in records], dtype=float)
    total_n = int(counts.sum())
    total = np.sum(counts[:, None] * means, axis=0)
    total_sq = np.sum(
        (counts[:, None] - 1) * np.square(sds) + counts[:, None] * np.square(means),
        axis=0,
    )
    mean = total / total_n
    variance = np.maximum((total_sq - np.square(total) / total_n) / (total_n - 1), 0.0)
    return mean, np.sqrt(variance / total_n)


def evaluate(
    stage_a: list[dict],
    stage_d_direct: list[dict],
    stage_d_recon: list[dict],
    m1_shared: dict,
    *,
    quick: bool,
) -> dict:
    ga = np.array([r["gain"]["estimate"] for r in stage_a])
    ga_se = np.array([r["gain"]["se"] for r in stage_a])
    ga_sd = np.array([r["gain"]["sd"] for r in stage_a])
    gd = np.array([r["direct_gain"]["estimate"] for r in stage_d_direct])
    gd_se = np.array([r["direct_gain"]["se"] for r in stage_d_direct])
    gd_sd = np.array([r["direct_gain"]["sd"] for r in stage_d_direct])
    gb = np.array([r["fixed_denominator_gain"]["estimate"] for r in stage_d_direct])
    correction = np.array([r["short_correction"]["estimate"] for r in stage_d_direct])

    delta = gd - ga
    delta_se = np.hypot(gd_se, ga_se)
    pooled_delta, pooled_delta_se = inverse_variance_pool(delta, delta_se)
    pooled_ga, pooled_ga_se = inverse_variance_pool(ga, ga_se)
    pooled_gd, pooled_gd_se = inverse_variance_pool(gd, gd_se)
    pooled_gb, pooled_gb_se = inverse_variance_pool(
        gb, np.array([r["fixed_denominator_gain"]["se"] for r in stage_d_direct])
    )

    correction_se = np.array([r["short_correction"]["se"] for r in stage_d_direct])
    pooled_correction = np.zeros(M_GRID.size)
    pooled_correction_se = np.zeros(M_GRID.size)
    correction_pooling = ["exact structural zero"] * M_GRID.size
    aggregate_correction, aggregate_correction_se = _aggregate_serialized_moments(
        stage_d_direct, "short_correction"
    )
    for j, m_raw in enumerate(M_GRID):
        if int(m_raw) == 1:
            continue
        if np.all(correction_se[:, j] > 0):
            pooled_correction[j], pooled_correction_se[j] = inverse_variance_pool(
                correction[:, j], correction_se[:, j]
            )
            correction_pooling[j] = "inverse variance"
        else:
            pooled_correction[j] = aggregate_correction[j]
            pooled_correction_se[j] = aggregate_correction_se[j]
            correction_pooling[j] = "combined retained moments (zero-SE replicate edge case)"

    pooled_scale = np.sqrt(np.mean((np.square(ga_sd) + np.square(gd_sd)) / 2.0, axis=0))
    standardized = pooled_delta / pooled_scale
    stopping = gb - ga
    direct_reconstruction_error = delta - (stopping + correction)

    distinction_rows = []
    for j, m_raw in enumerate(M_GRID):
        m = int(m_raw)
        short_count = sum(int(r["short_cycle_count"][j]) for r in stage_d_direct)
        short_n = sum(int(r["direct_gain"]["n"]) for r in stage_d_direct)
        short_ci = wilson_interval(short_count, short_n)
        distinction_rows.append({
            "m": m,
            "stage_a_gain": float(pooled_ga[j]),
            "stage_a_gain_se": float(pooled_ga_se[j]),
            "stage_a_derivative": float(1.0 - pooled_ga[j]),
            "stage_d_gain": float(pooled_gd[j]),
            "stage_d_gain_se": float(pooled_gd_se[j]),
            "stage_d_derivative": float(1.0 - pooled_gd[j]),
            "gain_difference_D_minus_A": float(pooled_delta[j]),
            "gain_difference_se": float(pooled_delta_se[j]),
            "gain_difference_ci95": [
                float(pooled_delta[j] - 1.96 * pooled_delta_se[j]),
                float(pooled_delta[j] + 1.96 * pooled_delta_se[j]),
            ],
            "derivative_difference_D_minus_A": float(-pooled_delta[j]),
            "standardized_gain_difference": float(standardized[j]),
            "abs_z_diagnostic": float(abs(pooled_delta[j]) / pooled_delta_se[j]),
            "fixed_denominator_gain": float(pooled_gb[j]),
            "fixed_denominator_gain_se": float(pooled_gb_se[j]),
            "stopping_time_component": float(pooled_gb[j] - pooled_ga[j]),
            "short_correction": float(pooled_correction[j]),
            "short_correction_se": float(pooled_correction_se[j]),
            "short_correction_pooling": correction_pooling[j],
            "component_reconstruction": float(
                pooled_gb[j] - pooled_ga[j] + pooled_correction[j]
            ),
            "short_cycle_count": short_count,
            "short_cycle_n": short_n,
            "short_cycle_probability": short_count / short_n,
            "short_cycle_wilson95": list(short_ci),
            "replicate_gain_differences": delta[:, j].tolist(),
            "replicate_gain_difference_ses": delta_se[:, j].tolist(),
        })

    recon = np.array([r["reconstruction"]["estimate"] for r in stage_d_recon])
    recon_se = np.array([r["reconstruction"]["se"] for r in stage_d_recon])
    epsilon = gd - recon
    epsilon_se = np.hypot(gd_se, recon_se)
    pooled_epsilon, pooled_epsilon_se = inverse_variance_pool(epsilon, epsilon_se)
    decomposition_rows = []
    for j, m_raw in enumerate(M_GRID):
        decomposition_rows.append({
            "m": int(m_raw),
            "direct_gamma_d": float(pooled_gd[j]),
            "independent_fixed_plus_correction": float(
                inverse_variance_pool(recon[:, j], recon_se[:, j])[0]
            ),
            "absolute_discrepancy": float(abs(pooled_epsilon[j])),
            "combined_se": float(pooled_epsilon_se[j]),
            "abs_z": float(abs(pooled_epsilon[j]) / pooled_epsilon_se[j]),
            "relative_discrepancy": float(abs(pooled_epsilon[j]) / abs(pooled_gd[j])),
            "replicate_discrepancies": epsilon[:, j].tolist(),
            "replicate_combined_ses": epsilon_se[:, j].tolist(),
            "replicate_abs_z": (np.abs(epsilon[:, j]) / epsilon_se[:, j]).tolist(),
        })

    prior_value, prior_se = _prior_m1()
    new_m1_values = np.concatenate([ga[:, 0], gd[:, 0]])
    new_m1_ses = np.concatenate([ga_se[:, 0], gd_se[:, 0]])
    new_m1, new_m1_se = inverse_variance_pool(new_m1_values, new_m1_ses)
    m1_hist_z = abs(float(new_m1) - prior_value) / np.hypot(float(new_m1_se), prior_se)
    m1_delta_z = abs(pooled_delta[0]) / pooled_delta_se[0]

    rho_max_error = 0.0
    rho_rows = []
    for rho in RHO_GRID:
        direct_formula = rho * (1.0 - pooled_gd)
        theorem_formula = predicted_derivative(pooled_gd, float(rho))
        error = float(np.max(np.abs(direct_formula - theorem_formula)))
        rho_max_error = max(rho_max_error, error)
        rho_rows.append({"rho": float(rho), "derivative": theorem_formula.tolist(),
                         "max_abs_error": error})

    pooled_decomp_z = np.abs(pooled_epsilon) / pooled_epsilon_se
    rep_decomp_z = np.abs(epsilon) / epsilon_se
    effect_indices = [int(np.flatnonzero(M_GRID == m)[0]) for m in (20, 50)]
    effect_cells_pass = all(
        pooled_delta[j] - 1.96 * pooled_delta_se[j] > 0
        and np.all(delta[:, j] > 0)
        for j in effect_indices
    )
    checks = {
        "stage_a_minimum_dwell_all_cells": bool(all(
            np.all(np.array(row["minimum_tau_m"]) >= M_GRID) for row in stage_a
        )),
        "m1_shared_pathwise_equality": bool(
            m1_shared["tau_equal"] and m1_shared["window_equal"]
            and m1_shared["gain_integrand_equal"]
            and m1_shared["maximum_correction"] == 0.0
        ),
        "m1_independent_gain_agreement_within_4se": bool(m1_delta_z <= 4.0),
        "m1_prior_gain_agreement_within_4se": bool(m1_hist_z <= 4.0),
        "effect_cells_m20_m50_positive_pooled_ci_and_replicates": bool(effect_cells_pass),
        "direct_component_reconstruction_roundoff": bool(
            np.max(np.abs(direct_reconstruction_error)) <= 1e-10
        ),
        "decomposition_pooled_all_within_3se": bool(np.all(pooled_decomp_z <= 3.0)),
        "decomposition_each_rep_all_within_4se": bool(np.all(rep_decomp_z <= 4.0)),
        "decomposition_pathwise_roundoff": bool(max(
            row["max_pathwise_decomposition_error"]
            for row in [*stage_d_direct, *stage_d_recon]
        ) <= 1e-10),
        "correction_pathwise_nonnegative": bool(min(
            row["minimum_pathwise_correction"]
            for row in [*stage_d_direct, *stage_d_recon]
        ) >= -1e-14),
        "rho_scaling_roundoff": bool(rho_max_error <= 1e-14),
    }
    decision = "SMOKE-ONLY" if quick else ("PASS" if all(checks.values()) else "FAIL")
    return {
        "decision": decision,
        "checks": checks,
        "distinction": distinction_rows,
        "decomposition": decomposition_rows,
        "m1_control": {
            "shared_stream": m1_shared,
            "pooled_stage_d_minus_stage_a": float(pooled_delta[0]),
            "pooled_difference_se": float(pooled_delta_se[0]),
            "abs_z": float(m1_delta_z),
            "prior_gain": prior_value,
            "prior_gain_se": prior_se,
            "new_four_route_pooled_gain": float(new_m1),
            "new_four_route_pooled_se": float(new_m1_se),
            "prior_agreement_abs_z": float(m1_hist_z),
        },
        "rho_scaling": {"rows": rho_rows, "max_abs_error": rho_max_error},
        "maximum_direct_component_reconstruction_error": float(
            np.max(np.abs(direct_reconstruction_error))
        ),
    }


def write_csv(path: Path, verdict: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        fields = [
            "m", "stage_a_gain", "stage_a_gain_se", "stage_a_derivative",
            "stage_d_gain", "stage_d_gain_se", "stage_d_derivative",
            "gain_difference_D_minus_A", "gain_difference_se",
            "ci95_low", "ci95_high", "derivative_difference_D_minus_A",
            "standardized_gain_difference", "fixed_denominator_gain",
            "stopping_time_component", "short_correction", "short_correction_se",
            "short_cycle_probability", "decomposition_abs_discrepancy",
            "decomposition_combined_se", "decomposition_abs_z",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        decomposition = {row["m"]: row for row in verdict["decomposition"]}
        for row in verdict["distinction"]:
            drow = decomposition[row["m"]]
            writer.writerow({
                "m": row["m"],
                "stage_a_gain": row["stage_a_gain"],
                "stage_a_gain_se": row["stage_a_gain_se"],
                "stage_a_derivative": row["stage_a_derivative"],
                "stage_d_gain": row["stage_d_gain"],
                "stage_d_gain_se": row["stage_d_gain_se"],
                "stage_d_derivative": row["stage_d_derivative"],
                "gain_difference_D_minus_A": row["gain_difference_D_minus_A"],
                "gain_difference_se": row["gain_difference_se"],
                "ci95_low": row["gain_difference_ci95"][0],
                "ci95_high": row["gain_difference_ci95"][1],
                "derivative_difference_D_minus_A": row["derivative_difference_D_minus_A"],
                "standardized_gain_difference": row["standardized_gain_difference"],
                "fixed_denominator_gain": row["fixed_denominator_gain"],
                "stopping_time_component": row["stopping_time_component"],
                "short_correction": row["short_correction"],
                "short_correction_se": row["short_correction_se"],
                "short_cycle_probability": row["short_cycle_probability"],
                "decomposition_abs_discrepancy": drow["absolute_discrepancy"],
                "decomposition_combined_se": drow["combined_se"],
                "decomposition_abs_z": drow["abs_z"],
            })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="run a small plumbing smoke test")
    parser.add_argument("--resume", action="store_true", help="reuse deterministic phase checkpoints")
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

    print("Stage A: dwell-stop gains", flush=True)
    stage_a = phase("stage_a", lambda: run_stage_a(cfg))
    print("Stage D: direct truncated gains", flush=True)
    stage_d_direct = phase("stage_d_direct", lambda: run_stage_d(cfg, 2))
    print("Stage D: independent fixed-plus-correction reconstruction", flush=True)
    stage_d_recon = phase("stage_d_reconstruction", lambda: run_stage_d(cfg, 3))
    m1_shared = run_m1_shared_control()
    verdict = evaluate(
        stage_a, stage_d_direct, stage_d_recon, m1_shared, quick=args.quick
    )
    output = args.output or CAMPAIGN / "results" / (
        "replication_smoke.json" if args.quick else "replication.json"
    )
    payload = {
        "campaign": "ReBaseGuard Proof Track 1A",
        "evidence": "SMOKE" if args.quick else "NEW-INDEPENDENT-CONFIRMATORY",
        "protocol_sha256": actual_hash,
        "protocol_commit": PROTOCOL_COMMIT,
        "historical_d2_3": "FAILED",
        "previous_track": "MGT1-THEOREM-PARTIAL",
        "config": cfg,
        "master_seed": MASTER_SEED,
        "m_grid": M_GRID.tolist(),
        "common_random_numbers_stage_a_vs_stage_d": False,
        "stage_a": stage_a,
        "stage_d_direct": stage_d_direct,
        "stage_d_reconstruction": stage_d_recon,
        "verdict": verdict,
        "python": platform.python_version(),
        "numpy": np.__version__,
    }
    _write_json(output, payload)
    write_csv(output.with_suffix(".csv"), verdict)
    print(json.dumps({"decision": verdict["decision"], "checks": verdict["checks"]}, indent=2))
    print(f"wrote {output}")
    print(f"wrote {output.with_suffix('.csv')}")
    if not args.quick and verdict["decision"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
