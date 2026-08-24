"""Estimate the exact Track-1B random-window gain on the frozen D4 grid."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

from .common import batch_summary, read_json, wilson_interval, write_json
from .config import (
    CAMPAIGN,
    GAMMA_BATCHES,
    GAMMA_BATCH_PATHS,
    M_GRID,
    MASTER_SEED,
    PROTOCOL_SHA256,
    RESULTS,
)

TRACK1B_SRC = CAMPAIGN.parent / "m_gt_1_track1b" / "src"
sys.path.insert(0, str(TRACK1B_SRC))
from rebaseguard_mgt1b.primitives import simulate_stopped_batch  # noqa: E402

CHECKPOINT = RESULTS / "gamma_grid_checkpoint.json"


def _rng(batch: int) -> np.random.Generator:
    seed = np.random.SeedSequence([MASTER_SEED, 1, batch])
    return np.random.Generator(np.random.PCG64(seed))


def _new_checkpoint() -> dict[str, Any]:
    return {
        "schema": "rebaseguard.d4-gamma-checkpoint.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "estimand": "GammaTilde_m = E_0[A_m T_tau], A_m uses w=min(m,tau)",
        "convention": "Stage-D convention A; ordinary tau; no minimum dwell",
        "master_seed": MASTER_SEED,
        "m_grid": M_GRID.tolist(),
        "config": {"n_batches": GAMMA_BATCHES, "paths_per_batch": GAMMA_BATCH_PATHS},
        "batches": [],
        "complete": False,
    }


def _validate_prefix(checkpoint: dict[str, Any]) -> None:
    if checkpoint["protocol_sha256"] != PROTOCOL_SHA256:
        raise RuntimeError("Gamma checkpoint protocol hash mismatch")
    if checkpoint["m_grid"] != M_GRID.tolist():
        raise RuntimeError("Gamma checkpoint m grid changed")
    expected = list(range(len(checkpoint["batches"])))
    observed = [row["batch"] for row in checkpoint["batches"]]
    if observed != expected:
        raise RuntimeError("Gamma checkpoint batches are not a contiguous prefix")


def _simulate_batch(batch: int, n_paths: int) -> dict[str, Any]:
    paths = simulate_stopped_batch(
        n_paths=n_paths,
        max_m=int(M_GRID.max()),
        rng=_rng(batch),
        minimum_dwell=None,
    )
    lag_cumsum = np.cumsum(paths.lags_newest, axis=1)
    direct_means: list[float] = []
    fixed_means: list[float] = []
    correction_means: list[float] = []
    short_counts: list[int] = []
    max_pathwise_error = 0.0
    min_correction = float("inf")
    for m_raw in M_GRID:
        m = int(m_raw)
        suffix = lag_cumsum[:, m - 1]
        realized = np.minimum(paths.tau, m)
        direct = suffix / realized * paths.t_tau
        fixed = suffix / m * paths.t_tau
        short = paths.tau < m
        correction = np.zeros(n_paths)
        correction[short] = (
            (1.0 / paths.tau[short] - 1.0 / m) * np.square(paths.t_tau[short])
        )
        max_pathwise_error = max(
            max_pathwise_error, float(np.max(np.abs(direct - fixed - correction)))
        )
        min_correction = min(min_correction, float(np.min(correction)))
        direct_means.append(float(np.mean(direct)))
        fixed_means.append(float(np.mean(fixed)))
        correction_means.append(float(np.mean(correction)))
        short_counts.append(int(np.count_nonzero(short)))
    return {
        "batch": batch,
        "n_paths": n_paths,
        "seed_key": [MASTER_SEED, 1, batch],
        "gamma_direct": direct_means,
        "gamma_fixed": fixed_means,
        "short_correction": correction_means,
        "short_counts": short_counts,
        "max_pathwise_decomposition_error": max_pathwise_error,
        "minimum_correction_integrand": min_correction,
    }


def summarize(checkpoint: dict[str, Any]) -> dict[str, Any]:
    _validate_prefix(checkpoint)
    batches = checkpoint["batches"]
    if len(batches) != GAMMA_BATCHES:
        raise RuntimeError(f"expected {GAMMA_BATCHES} Gamma batches")
    total_paths = sum(row["n_paths"] for row in batches)
    rows = []
    for j, m_raw in enumerate(M_GRID):
        direct = batch_summary(row["gamma_direct"][j] for row in batches)
        fixed = batch_summary(row["gamma_fixed"][j] for row in batches)
        correction = batch_summary(row["short_correction"][j] for row in batches)
        short_count = sum(row["short_counts"][j] for row in batches)
        reconstruction_batch_error = max(
            abs(
                row["gamma_direct"][j]
                - row["gamma_fixed"][j]
                - row["short_correction"][j]
            )
            for row in batches
        )
        rows.append({
            "m": int(m_raw),
            "gamma_tilde": direct,
            "fixed_lag_component": fixed,
            "short_cycle_correction": correction,
            "short_cycle_probability": {
                "count": short_count,
                "n_paths": total_paths,
                "estimate": short_count / total_paths,
                "ci95_wilson": wilson_interval(short_count, total_paths),
            },
            "maximum_batch_reconstruction_error": reconstruction_batch_error,
        })
    seed_keys = [tuple(row["seed_key"]) for row in batches]
    checks = {
        "all_batches_present": len(batches) == GAMMA_BATCHES,
        "unique_seed_keys": len(seed_keys) == len(set(seed_keys)),
        "all_batch_sizes_frozen": all(row["n_paths"] == GAMMA_BATCH_PATHS for row in batches),
        "pathwise_decomposition_roundoff": max(
            row["max_pathwise_decomposition_error"] for row in batches
        ) <= 1e-10,
        "batch_decomposition_roundoff": max(
            row["maximum_batch_reconstruction_error"] for row in rows
        ) <= 1e-10,
        "correction_nonnegative": min(
            row["minimum_correction_integrand"] for row in batches
        ) >= -1e-14,
        "finite_positive_gamma_se": all(
            np.isfinite(row["gamma_tilde"]["se"])
            and row["gamma_tilde"]["se"] > 0
            for row in rows
        ),
        "m1_exact_control": (
            rows[0]["short_cycle_probability"]["count"] == 0
            and all(value == 0.0 for value in (
                rows[0]["short_cycle_correction"]["mean"],
                rows[0]["short_cycle_correction"]["se"],
            ))
        ),
    }
    return {
        "schema": "rebaseguard.d4-gamma-summary.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "evidence": "NEW-CONFIRMATORY-NUMERICAL",
        "master_seed": MASTER_SEED,
        "m_grid": M_GRID.tolist(),
        "n_batches": GAMMA_BATCHES,
        "paths_per_batch": GAMMA_BATCH_PATHS,
        "n_paths": total_paths,
        "rows": rows,
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
    for batch in range(len(checkpoint["batches"]), GAMMA_BATCHES):
        checkpoint["batches"].append(_simulate_batch(batch, GAMMA_BATCH_PATHS))
        write_json(CHECKPOINT, checkpoint)
        print(f"Gamma batch {batch + 1}/{GAMMA_BATCHES}", flush=True)
    checkpoint["complete"] = True
    summary = summarize(checkpoint)
    checkpoint["summary"] = summary
    write_json(CHECKPOINT, checkpoint)
    write_json(RESULTS / "gamma_grid.json", summary)
    if not summary["valid"]:
        raise RuntimeError("Gamma grid validity gate failed")
    return summary
