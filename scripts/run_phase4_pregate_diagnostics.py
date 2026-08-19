"""Generate reproducible Phase-4 pre-gate diagnostic artifacts."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
from dataclasses import asdict
from pathlib import Path

import flint

from rebaseguard_certify.bellman import finite_interval_bellman_crosscheck
from rebaseguard_certify.bellman_ablation import historical_floor_reachable_ablation
from rebaseguard_certify.diagnostics import simulate
from rebaseguard_certify.pathwise import reference_replay
from rebaseguard_certify.refined_bellman import refined_bellman_diagnostic


ROOT = Path(__file__).resolve().parent.parent


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _combined_monte_carlo(runs: list[dict[str, object]]) -> dict[str, float | int]:
    counts = [int(run["n"]) for run in runs]
    means = [float(run["gamma"]) for run in runs]
    variances = [float(run["gamma_se"]) ** 2 * count for run, count in zip(runs, counts)]
    total = sum(counts)
    mean = sum(count * value for count, value in zip(counts, means)) / total
    numerator = sum(
        (count - 1) * variance + count * (value - mean) ** 2
        for count, variance, value in zip(counts, variances, means)
    )
    pooled_variance = numerator / (total - 1)
    return {
        "n": total,
        "gamma": mean,
        "gamma_se": (pooled_variance / total) ** 0.5,
    }


def _second_order_extrapolation(coarse: dict[str, object], fine: dict[str, object]) -> float:
    n0 = int(coarse["cells_per_unit"])
    n1 = int(fine["cells_per_unit"])
    y0 = float(coarse["gamma_finite"])
    y1 = float(fine["gamma_finite"])
    return (n1 * n1 * y1 - n0 * n0 * y0) / (n1 * n1 - n0 * n0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=1_000_000)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "diagnostics" / "phase4_pregate.json"
    )
    args = parser.parse_args()

    path_sequences = [
        [0.3, 1.4, 1.8, 2.1, 1.8],
        [-0.3, -1.4, -1.8, -2.1, -1.8],
        [1.0, -2.0, 1.0, -2.0, -2.0, -2.0, -2.0],
        [0.1, -0.1, 0.2, -0.2, 8.0],
    ]
    pathwise = [
        {
            "innovations": sequence,
            "trace": [asdict(row) for row in reference_replay(sequence)],
        }
        for sequence in path_sequences
    ]

    seeds = [1729, 20260818]
    monte_carlo_runs = [simulate(args.samples, seed=seed).summary() for seed in seeds]
    for seed, run in zip(seeds, monte_carlo_runs):
        run["seed"] = seed

    historical = finite_interval_bellman_crosscheck(cells=12, z_bins=96, bits=192)
    reachable_ablation = historical_floor_reachable_ablation(
        cells=12, z_bins=96, bits=192
    )
    historical_state_refinement = [
        historical_floor_reachable_ablation(
            cells=cells, z_bins=8 * cells, bits=128
        )
        for cells in (4, 8, 12, 16, 20, 24, 32)
    ]
    historical_increment_refinement = [
        finite_interval_bellman_crosscheck(cells=12, z_bins=z_bins, bits=128)
        for z_bins in (24, 48, 96, 192, 384)
    ]
    refined = [
        refined_bellman_diagnostic(cells_per_unit)
        for cells_per_unit in (1, 2, 4, 8, 12, 16)
    ]

    protected_paths = [
        ROOT / "src" / "rebaseguard_certify" / "bellman.py",
        ROOT / "proofs" / "certificate.json",
        ROOT / "proofs" / "enclosure.json",
        ROOT / "proofs" / "residual.json",
        ROOT / "proofs" / "contraction_monotone.json",
    ]
    payload = {
        "schema": "rebaseguard.phase4-pregate-diagnostics.v1",
        "proof_role": "NON-RIGOROUS DIAGNOSTIC AND FORENSIC ABLATION ONLY",
        "model": {"k": 0.5, "h": 5.0, "m": 1, "initial_state": [0.0, 0.0]},
        "pathwise_replay": pathwise,
        "monte_carlo": {
            "runs": monte_carlo_runs,
            "combined": _combined_monte_carlo(monte_carlo_runs),
        },
        "historical_reproduction": historical,
        "reachable_subset_ablation": reachable_ablation,
        "historical_state_refinement": historical_state_refinement,
        "historical_increment_refinement": historical_increment_refinement,
        "refined_reachable_bellman": refined,
        "corrected_point_estimate": {
            "method": "second-order extrapolation from cells_per_unit 12 and 16",
            "gamma": _second_order_extrapolation(refined[-2], refined[-1]),
            "proof_role": "NON-RIGOROUS POINT ESTIMATE ONLY",
        },
        "classification": {
            "category": "D. FINITE DISCRETIZATION BIAS",
            "mechanism": "one-sided floor projection of every off-grid next state",
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": importlib.metadata.version("numpy"),
            "scipy": importlib.metadata.version("scipy"),
            "python_flint": importlib.metadata.version("python-flint"),
            "flint": flint.__FLINT_VERSION__,
        },
        "protected_hashes": {
            str(path.relative_to(ROOT)): _sha256(path) for path in protected_paths
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
