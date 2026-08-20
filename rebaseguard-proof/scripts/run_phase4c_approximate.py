"""Generate the Phase-4C non-rigorous continuum refinement study."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from rebaseguard_phase4c.approximate_solver import solve_approximate_sr


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "proofs" / "phase4c" / "approximate_solve.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes", type=int, nargs="+", default=[41, 61, 81, 101, 121])
    parser.add_argument("--quadrature", type=int, default=192)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload: dict[str, object] = {
        "schema": "rebaseguard.phase4c.approximate-continuum.v1",
        "proof_role": "NON-RIGOROUS FEASIBILITY DIAGNOSTIC ONLY",
        "detector": {"delta": 1.0, "threshold_A": 520.3125, "m": 1},
        "quadrature_order": args.quadrature,
        "runs": [],
        "failed_or_null_settings": [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for nodes in args.nodes:
        try:
            result = solve_approximate_sr(nodes, quadrature_order=args.quadrature)
        except Exception as exc:
            payload["failed_or_null_settings"].append(  # type: ignore[union-attr]
                {"nodes_per_axis": nodes, "error": f"{type(exc).__name__}: {exc}"}
            )
            args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            raise
        summary = result.summary()
        payload["runs"].append(summary)  # type: ignore[union-attr]
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(json.dumps(summary, sort_keys=True), flush=True)
    gammas = [float(run["gamma"]) for run in payload["runs"]]  # type: ignore[index]
    inverse_spacing_sq = np.array(
        [1.0 / (nodes - 1) ** 2 for nodes in args.nodes], dtype=float
    )
    fit_count = min(4, len(gammas))
    extrapolated = float(
        np.polyfit(inverse_spacing_sq[-fit_count:], gammas[-fit_count:], 1)[1]
    )
    payload["comparison"] = {
        "phase4b_monte_carlo_gamma": 17.272084700443617,
        "finest_gamma": gammas[-1],
        "absolute_difference": abs(gammas[-1] - 17.272084700443617),
        "second_order_extrapolated_gamma": extrapolated,
        "extrapolated_difference_from_monte_carlo": abs(
            extrapolated - 17.272084700443617
        ),
        "monte_carlo_standard_errors_from_extrapolation": abs(
            extrapolated - 17.272084700443617
        )
        / 0.028026952428261528,
        "successive_differences": [
            gammas[index] - gammas[index - 1] for index in range(1, len(gammas))
        ],
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
