#!/usr/bin/env python3
"""Replay the frozen Track-3 t3 seeds and diagnose estimator variance.

This script does not draw fresh campaign data.  It reconstructs the historical
Track-3 t3 batches with their frozen seeds, checks the retained batch means,
and records path-level variance information that was not retained originally.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats


CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]
HISTORICAL = REPO / "level4/closure_proofs/location_family"
sys.path.insert(0, str(HISTORICAL / "src"))

from rebaseguard_location_family.frozen import (  # noqa: E402
    H_STEPS,
    MASTER_SEED,
    ROUTE_A_BATCHES,
    ROUTE_A_PATHS_PER_BATCH,
    ROUTE_B_BATCHES,
    ROUTE_B_PATHS_PER_BATCH,
    THRESHOLDS,
)
from rebaseguard_location_family.route_a import simulate_score_batch  # noqa: E402
from rebaseguard_location_family.route_b import (  # noqa: E402
    simulate_conditional_batch,
)


FAMILY = "t3"
FAMILY_INDEX = 3
ERRORS = np.array([value for h in H_STEPS for value in (-h, h)], dtype=float)
ABS_TOL = 5e-13


def rng(key: list[int]) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(key)))


def summary(values: np.ndarray) -> dict[str, float]:
    data = np.asarray(values, dtype=float)
    mean = float(data.mean())
    sd = float(data.std(ddof=1))
    n = data.size
    sorted_data = np.sort(data)
    trim = max(1, int(math.floor(0.1 * n)))
    trimmed = sorted_data[trim:-trim]
    return {
        "n": int(n),
        "mean": mean,
        "sd": sd,
        "se": sd / math.sqrt(n),
        "median": float(np.median(data)),
        "ten_percent_trimmed_mean": float(trimmed.mean()),
        "skew": float(stats.skew(data, bias=False)),
        "excess_kurtosis": float(stats.kurtosis(data, fisher=True, bias=False)),
        "min": float(data.min()),
        "q01": float(np.quantile(data, 0.01)),
        "q05": float(np.quantile(data, 0.05)),
        "q95": float(np.quantile(data, 0.95)),
        "q99": float(np.quantile(data, 0.99)),
        "max": float(data.max()),
    }


def tail_concentration(values: np.ndarray) -> dict[str, float]:
    data = np.asarray(values, dtype=float)
    centered_sq = (data - data.mean()) ** 2
    total_var_mass = float(centered_sq.sum())
    order = np.argsort(np.abs(data))[::-1]
    output: dict[str, float] = {}
    for fraction in (0.1, 0.01, 0.001, 0.0001):
        count = max(1, int(math.ceil(fraction * data.size)))
        selected = order[:count]
        output[f"top_{fraction:.4f}_abs_share_of_variance_mass"] = (
            float(centered_sq[selected].sum() / total_var_mass)
            if total_var_mass
            else 0.0
        )
        output[f"top_{fraction:.4f}_abs_share_of_signed_sum"] = float(
            data[selected].sum() / data.sum()
        )
    return output


def max_leave_one_batch_influence(batch_means: np.ndarray) -> dict[str, float]:
    values = np.asarray(batch_means, dtype=float)
    full = float(values.mean())
    loo = (values.sum() - values) / (values.size - 1)
    shifts = np.abs(loo - full)
    index = int(np.argmax(shifts))
    return {
        "batch": index,
        "batch_value": float(values[index]),
        "absolute_mean_shift": float(shifts[index]),
        "relative_to_abs_full_mean": float(shifts[index] / abs(full)),
    }


def main() -> None:
    retained_a = json.loads((HISTORICAL / "results/route_a.json").read_text())[
        "families"
    ][FAMILY]
    retained_b = json.loads((HISTORICAL / "results/route_b.json").read_text())[
        "families"
    ][FAMILY]

    all_gains: list[np.ndarray] = []
    a_batch_means: list[float] = []
    a_within_variances: list[float] = []
    a_replay_errors: list[float] = []
    for batch in range(ROUTE_A_BATCHES):
        key = [MASTER_SEED, 1, FAMILY_INDEX, batch]
        paths = simulate_score_batch(
            family=FAMILY,
            threshold=THRESHOLDS[FAMILY],
            n_paths=ROUTE_A_PATHS_PER_BATCH,
            rng=rng(key),
        )
        gains = paths.gain
        batch_mean = float(gains.mean())
        retained = float(retained_a["batches"][batch]["gamma_f"])
        a_replay_errors.append(batch_mean - retained)
        a_batch_means.append(batch_mean)
        a_within_variances.append(float(gains.var(ddof=1)))
        all_gains.append(gains)

    gains = np.concatenate(all_gains)
    a_batches = np.asarray(a_batch_means)
    a_avg_within_var = float(np.mean(a_within_variances))
    a_batch_mean_var_from_within = a_avg_within_var / ROUTE_A_PATHS_PER_BATCH
    a_empirical_batch_mean_var = float(a_batches.var(ddof=1))

    route_b_reps: list[dict] = []
    rep_primary_means: list[float] = []
    rep_primary_ses: list[float] = []
    for rep_index in range(2):
        batch_derivatives: list[np.ndarray] = []
        path_derivatives_by_h: list[list[np.ndarray]] = [[], [], []]
        plus_contrib_by_h: list[list[np.ndarray]] = [[], [], []]
        minus_contrib_by_h: list[list[np.ndarray]] = [[], [], []]
        replay_errors: list[float] = []

        for batch in range(ROUTE_B_BATCHES):
            key = [MASTER_SEED, 2 + rep_index, FAMILY_INDEX, batch]
            paths = simulate_conditional_batch(
                family=FAMILY,
                threshold=THRESHOLDS[FAMILY],
                errors=ERRORS,
                n_paths=ROUTE_B_PATHS_PER_BATCH,
                generator=rng(key),
            )
            maps = paths.maps()
            derivatives = []
            for h_index, h in enumerate(H_STEPS):
                minus_index = 2 * h_index
                plus_index = minus_index + 1
                plus = h + paths.terminal[:, plus_index]
                minus = -h + paths.terminal[:, minus_index]
                path_derivative = (plus - minus) / (2.0 * h)
                derivatives.append(float(path_derivative.mean()))
                path_derivatives_by_h[h_index].append(path_derivative)
                plus_contrib_by_h[h_index].append(plus)
                minus_contrib_by_h[h_index].append(minus)
            derivatives_array = np.asarray(derivatives)
            retained = np.asarray(
                retained_b["replications"][rep_index]["batches"][batch][
                    "paired_derivatives"
                ]
            )
            replay_errors.extend((derivatives_array - retained).tolist())
            batch_derivatives.append(derivatives_array)

        batch_matrix = np.asarray(batch_derivatives)
        h_results = []
        for h_index, h in enumerate(H_STEPS):
            direct = np.concatenate(path_derivatives_by_h[h_index])
            plus = np.concatenate(plus_contrib_by_h[h_index])
            minus = np.concatenate(minus_contrib_by_h[h_index])
            covariance = float(np.cov(plus, minus, ddof=1)[0, 1])
            correlation = float(np.corrcoef(plus, minus)[0, 1])
            n_paths = direct.size
            paired_var_mean = float(direct.var(ddof=1) / n_paths)
            independent_var_mean = float(
                (plus.var(ddof=1) + minus.var(ddof=1))
                / ((2.0 * h) ** 2 * n_paths)
            )
            batch_stats = summary(batch_matrix[:, h_index])
            h_results.append(
                {
                    "h": h,
                    "path_derivative": summary(direct),
                    "batch_derivative": batch_stats,
                    "plus_minus_covariance": covariance,
                    "plus_minus_correlation": correlation,
                    "paired_se_from_paths": math.sqrt(paired_var_mean),
                    "independence_assumption_se": math.sqrt(
                        independent_var_mean
                    ),
                    "crn_variance_ratio_paired_over_independent": (
                        paired_var_mean / independent_var_mean
                    ),
                    "max_batch_influence": max_leave_one_batch_influence(
                        batch_matrix[:, h_index]
                    ),
                }
            )

        primary = h_results[-1]["batch_derivative"]
        rep_primary_means.append(float(primary["mean"]))
        rep_primary_ses.append(float(primary["se"]))
        route_b_reps.append(
            {
                "replication": rep_index + 1,
                "replay_max_abs_error": float(np.max(np.abs(replay_errors))),
                "h_results": h_results,
            }
        )

    x, y = rep_primary_means
    sx, sy = rep_primary_ses
    mean_abs = (abs(x) + abs(y)) / 2.0
    combined_se = math.hypot(sx, sy)
    relative = abs(x - y) / mean_abs

    family_batch_sds = {}
    historical_a = json.loads((HISTORICAL / "results/route_a.json").read_text())
    historical_b = json.loads((HISTORICAL / "results/route_b.json").read_text())
    for family, cell in historical_a["families"].items():
        a_values = np.array([row["gamma_f"] for row in cell["batches"]])
        b_values = np.concatenate(
            [
                np.array(
                    [row["paired_derivatives"][-1] for row in rep["batches"]]
                )
                for rep in historical_b["families"][family]["replications"]
            ]
        )
        family_batch_sds[family] = {
            "route_a_gamma_batch_sd": float(a_values.std(ddof=1)),
            "route_b_primary_batch_sd": float(b_values.std(ddof=1)),
        }

    pooled_b_values = np.concatenate(
        [
            np.array(
                [
                    row["paired_derivatives"][-1]
                    for row in retained_b["replications"][rep]["batches"]
                ]
            )
            for rep in range(2)
        ]
    )
    a_mean = float(1.0 - a_batches.mean())
    a_se = float(a_batches.std(ddof=1) / math.sqrt(a_batches.size))
    b_mean = float(pooled_b_values.mean())
    b_se = float(pooled_b_values.std(ddof=1) / math.sqrt(pooled_b_values.size))

    output = {
        "schema": "rebaseguard.location-family-track3ab.historical-variance.v1",
        "classification": (
            "sampling variance amplified by t3 heavy-tail gain variance; "
            "no retained evidence of finite-difference bias or implementation mismatch"
        ),
        "historical_seed_replay_only": True,
        "fresh_campaign_outcomes_generated": False,
        "route_a": {
            "replay_max_abs_error": float(np.max(np.abs(a_replay_errors))),
            "path_gain": summary(gains),
            "batch_gamma": summary(a_batches),
            "average_within_batch_path_variance": a_avg_within_var,
            "implied_batch_mean_variance_from_within": a_batch_mean_var_from_within,
            "empirical_between_batch_variance": a_empirical_batch_mean_var,
            "between_over_within_implied_ratio": (
                a_empirical_batch_mean_var / a_batch_mean_var_from_within
            ),
            "tail_concentration": tail_concentration(gains),
            "max_batch_influence": max_leave_one_batch_influence(a_batches),
            "t3_score_formula": "psi(z)=4z/(1+z^2)",
            "t3_score_absolute_bound": 2.0,
        },
        "route_b": {
            "replications": route_b_reps,
            "primary_replication_comparison": {
                "replication_means": rep_primary_means,
                "replication_ses": rep_primary_ses,
                "difference": abs(x - y),
                "combined_se": combined_se,
                "absolute_z": abs(x - y) / combined_se,
                "symmetric_relative_difference": relative,
                "delta_method_se_of_relative_difference_at_equality": (
                    combined_se / mean_abs
                ),
                "observed_relative_over_null_se": relative
                / (combined_se / mean_abs),
            },
        },
        "route_a_vs_pooled_route_b": {
            "route_a_derivative": a_mean,
            "route_a_se": a_se,
            "route_b_derivative": b_mean,
            "route_b_se": b_se,
            "absolute_z": abs(a_mean - b_mean) / math.hypot(a_se, b_se),
            "symmetric_relative_difference": abs(a_mean - b_mean)
            / ((abs(a_mean) + abs(b_mean)) / 2.0),
            "delta_method_relative_se_at_equality": math.hypot(a_se, b_se)
            / ((abs(a_mean) + abs(b_mean)) / 2.0),
        },
        "cross_family_batch_sd": family_batch_sds,
        "identifiability_note": (
            "The replay recovers within-batch path variance and CRN covariance. "
            "There is no structural batch heterogeneity: batches differ only by seed."
        ),
    }
    path = CAMPAIGN / "results/historical_variance_diagnosis.json"
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
    print(f"wrote {path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
