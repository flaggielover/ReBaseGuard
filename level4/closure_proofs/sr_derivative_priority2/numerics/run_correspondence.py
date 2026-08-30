#!/usr/bin/env python3
"""Run the frozen, independent Gaussian SR correspondence protocol."""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]
SRC = CAMPAIGN / "src"
sys.path.insert(0, str(SRC))

from rebaseguard_sr_priority2 import AUTHORITATIVE_A  # noqa: E402
from rebaseguard_sr_priority2.direct_sr import simulate_direct_batch  # noqa: E402
from rebaseguard_sr_priority2.score_sr import simulate_score_batch  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean_se(values: np.ndarray, axis: int = 0) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=float)
    return values.mean(axis=axis), values.std(axis=axis, ddof=1) / math.sqrt(values.shape[axis])


def stage(*, label: str, batches: int, paths: int, score_seed: int,
          direct_seed: int, m_grid: np.ndarray, h_grid: np.ndarray,
          max_steps: int) -> dict:
    score_rows, direct_rows = [], []
    tau_means, short_counts = [], []
    score_ties = score_simultaneous = direct_ties = direct_simultaneous = 0
    stage_key = 1 if label == "pilot" else 2
    for batch in range(batches):
        score_rng = np.random.default_rng(np.random.SeedSequence([score_seed, stage_key, batch]))
        score = simulate_score_batch(
            n_paths=paths, threshold=AUTHORITATIVE_A, m_grid=m_grid,
            rng=score_rng, max_steps=max_steps,
        )
        score_rows.append(score.gamma)
        tau_means.append(score.tau_mean)
        short_counts.append(score.short_counts)
        score_ties += score.ties
        score_simultaneous += score.simultaneous

        direct_rng = np.random.default_rng(np.random.SeedSequence([direct_seed, batch]))
        direct = simulate_direct_batch(
            n_paths=paths, threshold=AUTHORITATIVE_A, m_grid=m_grid,
            h_grid=h_grid, rng=direct_rng, max_steps=max_steps,
        )
        direct_rows.append(direct.derivatives)
        direct_ties += direct.ties
        direct_simultaneous += direct.simultaneous

    score_rows = np.asarray(score_rows)
    direct_rows = np.asarray(direct_rows)
    gamma, gamma_se = mean_se(score_rows)
    derivative, derivative_se = mean_se(direct_rows)
    return {
        "label": label,
        "batches": batches,
        "paths_per_batch_per_condition": paths,
        "score_batch_values": score_rows.tolist(),
        "direct_batch_values": direct_rows.tolist(),
        "gamma": gamma.tolist(),
        "gamma_se": gamma_se.tolist(),
        "direct_derivative": derivative.tolist(),
        "direct_derivative_se": derivative_se.tolist(),
        "mean_tau": float(np.mean(tau_means)),
        "short_cycle_counts": np.asarray(short_counts).sum(axis=0).astype(int).tolist(),
        "ties": {"score": score_ties, "direct": direct_ties},
        "simultaneous_crossings": {
            "score": score_simultaneous, "direct": direct_simultaneous,
        },
    }


def main() -> None:
    protocol_path = CAMPAIGN / "numerics" / "PROTOCOL.json"
    protocol = json.loads(protocol_path.read_text())
    m_grid = np.asarray(protocol["m_grid"], dtype=np.int64)
    rho_grid = np.asarray(protocol["rho_grid"], dtype=float)
    h_grid = np.asarray(protocol["step_grid"], dtype=float)
    gates = protocol["gates"]
    seeds = protocol["seeds"]
    max_steps = int(gates["maximum_steps_per_path"])

    pilot = stage(
        label="pilot", batches=protocol["pilot"]["batches"],
        paths=protocol["pilot"]["paths_per_batch_per_condition"],
        score_seed=seeds["score"], direct_seed=seeds["pilot_direct"],
        m_grid=m_grid, h_grid=h_grid, max_steps=max_steps,
    )
    final = stage(
        label="final", batches=protocol["final"]["batches"],
        paths=protocol["final"]["paths_per_batch_per_condition"],
        score_seed=seeds["score"], direct_seed=seeds["final_direct"],
        m_grid=m_grid, h_grid=h_grid, max_steps=max_steps,
    )

    score_batches = np.asarray(final["score_batch_values"])
    direct_batches = np.asarray(final["direct_batch_values"])
    pilot_score = np.asarray(pilot["gamma_se"])
    pilot_direct = np.asarray(pilot["direct_derivative_se"])
    gamma = np.asarray(final["gamma"])
    gamma_se = np.asarray(final["gamma_se"])
    direct = np.asarray(final["direct_derivative"])
    direct_se = np.asarray(final["direct_derivative_se"])
    prediction = 1.0 - gamma
    rich_batches = (4.0 * direct_batches[:, -1, :] - direct_batches[:, -2, :]) / 3.0
    rich, rich_se = mean_se(rich_batches)
    cells = []
    for j, m in enumerate(m_grid):
        for rho in rho_grid:
            pred = float(rho * prediction[j])
            pred_se = float(abs(rho) * gamma_se[j])
            small = float(rho * direct[-1, j])
            small_se = float(abs(rho) * direct_se[-1, j])
            small_diff = abs(small - pred)
            small_limit = max(
                gates["smallest_step_abs_floor_after_rho"],
                gates["smallest_step_combined_se_multiplier"]
                * math.hypot(small_se, pred_se),
            )
            rich_value = float(rho * rich[j])
            rich_cell_se = float(abs(rho) * rich_se[j])
            rich_diff = abs(rich_value - pred)
            rich_limit = max(
                gates["richardson_abs_floor_after_rho"],
                gates["richardson_combined_se_multiplier"]
                * math.hypot(rich_cell_se, pred_se),
            )
            convergence = True
            convergence_rows = []
            discrepancies = np.abs(rho * direct[:, j] - pred)
            for k in range(1, h_grid.size):
                slack = gates["convergence_slack_combined_se_multiplier"] * abs(rho) * math.hypot(
                    direct_se[k, j], direct_se[k - 1, j]
                )
                ok = bool(discrepancies[k] <= discrepancies[k - 1] + slack)
                convergence &= ok
                convergence_rows.append({"from_h": float(h_grid[k - 1]),
                                         "to_h": float(h_grid[k]),
                                         "slack": slack, "pass": ok})
            precision = bool(
                gamma_se[j] <= pilot_score[j]
                and direct_se[-1, j] <= pilot_direct[-1, j]
            )
            finite = all(math.isfinite(x) for x in (
                pred, pred_se, small, small_se, rich_value, rich_cell_se,
            ))
            checks = {
                "smallest_step_agreement": small_diff <= small_limit,
                "richardson_agreement": rich_diff <= rich_limit,
                "step_ladder_convergence": convergence,
                "sample_escalation_precision": precision,
                "finite": finite,
            }
            cells.append({
                "m": int(m), "rho": float(rho),
                "gamma_tilde": float(gamma[j]), "gamma_tilde_se": float(gamma_se[j]),
                "score_prediction": pred, "score_prediction_se": pred_se,
                "smallest_h": float(h_grid[-1]), "direct_derivative": small,
                "direct_derivative_se": small_se, "absolute_difference": small_diff,
                "agreement_limit": small_limit,
                "richardson_derivative": rich_value,
                "richardson_derivative_se": rich_cell_se,
                "richardson_difference": rich_diff,
                "richardson_limit": rich_limit,
                "convergence": convergence_rows,
                "checks": checks, "pass": all(checks.values()),
            })

    tie_pass = sum(final["ties"].values()) == 0 and sum(pilot["ties"].values()) == 0
    all_cells = all(row["pass"] for row in cells)
    decision = {
        "cells": cells,
        "all_cells_pass": all_cells,
        "exact_tie_gate": tie_pass,
        "all_required_numerical_gates_pass": all_cells and tie_pass,
    }
    payload = {
        "campaign": protocol["campaign"],
        "evidence_class": "EMPIRICAL_FROZEN_GAUSSIAN_SR",
        "protocol": protocol,
        "protocol_sha256": digest(protocol_path),
        "source_sha256": {
            str(path.relative_to(CAMPAIGN)): digest(path)
            for path in (CAMPAIGN / "src" / "rebaseguard_sr_priority2").glob("*.py")
        },
        "python": platform.python_version(), "numpy": np.__version__,
        "pilot": pilot, "final": final, "decision": decision,
        "evidence_boundary": "Empirical only. Not an Arb or interval-certified evaluation of frozen infinite-horizon Gaussian SR m>1 values.",
    }
    output = CAMPAIGN / "results" / "numerical_correspondence.json"
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"output": str(output.relative_to(ROOT)), **decision}, indent=2))
    if not decision["all_required_numerical_gates_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
