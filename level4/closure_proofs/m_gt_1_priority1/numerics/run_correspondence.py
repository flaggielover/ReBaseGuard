#!/usr/bin/env python3
"""Run the preregistered independent frozen-CUSUM correspondence study."""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_mgt1_priority1.cusum import stopped_batch  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean_se(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return values.mean(axis=0), values.std(axis=0, ddof=1) / math.sqrt(values.shape[0])


def run_map_level(cfg: dict, label: str) -> dict:
    section = cfg[label]
    batches = int(section["batches"])
    paths = int(section["paths_per_batch_per_e"])
    m_grid = np.asarray(cfg["m_grid"], dtype=np.int64)
    steps = np.asarray(cfg["step_grid"], dtype=float)
    seed_key = "pilot_finite_difference" if label == "pilot" else "final_finite_difference"
    root_seed = int(cfg["seeds"][seed_key])
    derivatives = np.zeros((batches, len(steps), len(m_grid)))
    tau_means = np.zeros((batches, len(steps), 2))
    counts = {"short": np.zeros(len(m_grid), dtype=np.int64),
              "equal": np.zeros(len(m_grid), dtype=np.int64),
              "long": np.zeros(len(m_grid), dtype=np.int64)}
    for b in range(batches):
        for hi, h in enumerate(steps):
            pair = []
            for sign_index, sign in enumerate((-1.0, 1.0)):
                ss = np.random.SeedSequence([root_seed, b, hi, sign_index])
                rng = np.random.Generator(np.random.PCG64(ss))
                result = stopped_batch(
                    e=sign * h, n_paths=paths, m_grid=m_grid, rng=rng,
                    max_steps=int(cfg["gates"]["maximum_steps_per_path"]),
                )
                pair.append(result)
                tau_means[b, hi, sign_index] = result.tau_mean
                if label == "final" and hi == len(steps) - 1:
                    counts["short"] += result.short_counts
                    counts["equal"] += result.tau_equal_counts
                    counts["long"] += result.full_counts
            derivatives[b, hi] = (pair[1].map_base - pair[0].map_base) / (2.0 * h)
    means, ses = mean_se(derivatives.reshape(batches, -1))
    means = means.reshape(len(steps), len(m_grid))
    ses = ses.reshape(len(steps), len(m_grid))
    rich_batches = (4.0 * derivatives[:, 2, :] - derivatives[:, 1, :]) / 3.0
    rich_mean, rich_se = mean_se(rich_batches)
    return {
        "batches": batches,
        "paths_per_batch_per_e": paths,
        "total_paths_per_e": batches * paths,
        "derivative_batch_values": derivatives.tolist(),
        "derivative_mean": means.tolist(),
        "derivative_se": ses.tolist(),
        "richardson_batch_values": rich_batches.tolist(),
        "richardson_mean": rich_mean.tolist(),
        "richardson_se": rich_se.tolist(),
        "tau_mean_by_batch_step_sign": tau_means.tolist(),
        "smallest_step_counts": {key: value.tolist() for key, value in counts.items()},
    }


def run_score(cfg: dict) -> dict:
    batches = int(cfg["final"]["batches"])
    paths = int(cfg["final"]["paths_per_batch_per_e"])
    m_grid = np.asarray(cfg["m_grid"], dtype=np.int64)
    values = np.zeros((batches, len(m_grid)))
    tau_means = np.zeros(batches)
    counts = {"short": np.zeros(len(m_grid), dtype=np.int64),
              "equal": np.zeros(len(m_grid), dtype=np.int64),
              "long": np.zeros(len(m_grid), dtype=np.int64)}
    for b in range(batches):
        ss = np.random.SeedSequence([int(cfg["seeds"]["score"]), b])
        rng = np.random.Generator(np.random.PCG64(ss))
        result = stopped_batch(
            e=0.0, n_paths=paths, m_grid=m_grid, rng=rng,
            max_steps=int(cfg["gates"]["maximum_steps_per_path"]),
        )
        values[b] = 1.0 - result.gamma
        tau_means[b] = result.tau_mean
        counts["short"] += result.short_counts
        counts["equal"] += result.tau_equal_counts
        counts["long"] += result.full_counts
    mean, se = mean_se(values)
    return {
        "batches": batches,
        "paths_per_batch": paths,
        "total_paths": batches * paths,
        "slope_batch_values": values.tolist(),
        "slope_mean": mean.tolist(),
        "slope_se": se.tolist(),
        "gamma_mean": (1.0 - mean).tolist(),
        "tau_mean": float(tau_means.mean()),
        "counts": {key: value.tolist() for key, value in counts.items()},
    }


def decisions(cfg: dict, pilot: dict, final: dict, score: dict) -> dict:
    rho_grid = np.asarray(cfg["rho_grid"], dtype=float)
    score_mean = np.asarray(score["slope_mean"])
    score_se = np.asarray(score["slope_se"])
    fd = np.asarray(final["derivative_mean"])
    fd_se = np.asarray(final["derivative_se"])
    rich = np.asarray(final["richardson_mean"])
    rich_se = np.asarray(final["richardson_se"])
    pilot_se = np.asarray(pilot["derivative_se"])
    g = cfg["gates"]
    cells = []
    all_pass = True
    for ri, rho in enumerate(rho_grid):
        for mi, m in enumerate(cfg["m_grid"]):
            pred = rho * score_mean[mi]
            pred_se = rho * score_se[mi]
            small = rho * fd[2, mi]
            small_se = rho * fd_se[2, mi]
            rich_value = rho * rich[mi]
            rich_value_se = rho * rich_se[mi]
            comb_small = math.hypot(pred_se, small_se)
            comb_rich = math.hypot(pred_se, rich_value_se)
            tol_small = max(float(g["smallest_step_abs_floor_after_rho"]),
                            float(g["smallest_step_combined_se_multiplier"]) * comb_small)
            tol_rich = max(float(g["richardson_abs_floor_after_rho"]),
                           float(g["richardson_combined_se_multiplier"]) * comb_rich)
            hbig = rho * fd[0, mi]
            hbig_se = rho * fd_se[0, mi]
            conv_slack = float(g["convergence_slack_combined_se_multiplier"]) * (
                pred_se + rich_value_se + hbig_se)
            checks = {
                "smallest_step_agreement": bool(abs(small - pred) <= tol_small),
                "richardson_agreement": bool(abs(rich_value - pred) <= tol_rich),
                "convergence": bool(abs(rich_value - pred) <= abs(hbig - pred) + conv_slack),
                "precision_escalation": bool(small_se <= rho * pilot_se[2, mi]),
                "finite": bool(np.all(np.isfinite([pred, small, rich_value]))),
            }
            passed = all(checks.values())
            all_pass &= passed
            cells.append({
                "rho": float(rho), "m": int(m), "prediction": pred,
                "prediction_se": pred_se, "smallest_step": small,
                "smallest_step_se": small_se, "smallest_tolerance": tol_small,
                "richardson": rich_value, "richardson_se": rich_value_se,
                "richardson_tolerance": tol_rich, "h_0_1": hbig,
                "checks": checks, "pass": passed,
            })
    return {"cells": cells, "all_cells_pass": bool(all_pass)}


def main() -> None:
    protocol_path = CAMPAIGN / "numerics" / "PROTOCOL.json"
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    expected = manifest["frozen_new_inputs"]["numerical_protocol_sha256"]
    if sha256(protocol_path) != expected:
        raise SystemExit("numerical protocol hash mismatch")
    cfg = json.loads(protocol_path.read_text())
    started = time.time()
    pilot = run_map_level(cfg, "pilot")
    final = run_map_level(cfg, "final")
    score = run_score(cfg)
    decision = decisions(cfg, pilot, final, score)
    payload = {
        "campaign": cfg["campaign"],
        "evidence_class": "EMPIRICAL_FROZEN_GAUSSIAN_CUSUM",
        "protocol_sha256": expected,
        "protocol": cfg,
        "pilot": pilot,
        "final": final,
        "score": score,
        "decision": decision,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "evidence_boundary": "Not an Arb or interval certificate for frozen Gaussian CUSUM m>1 values.",
    }
    out = CAMPAIGN / "results" / "numerical_correspondence.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"output": str(out.relative_to(ROOT)),
                      "all_cells_pass": decision["all_cells_pass"],
                      "elapsed_seconds": time.time() - started}, indent=2))


if __name__ == "__main__":
    main()
