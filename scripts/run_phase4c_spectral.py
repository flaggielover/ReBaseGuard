"""Generate the high-quality non-rigorous Phase-4C candidate study."""

from __future__ import annotations

import json
from pathlib import Path

from rebaseguard_phase4c.spectral_solver import solve_spectral_sr


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "proofs" / "phase4c" / "spectral_candidate_study.json"


def main() -> None:
    payload: dict[str, object] = {
        "schema": "rebaseguard.phase4c.spectral-candidate-study.v1",
        "proof_role": "NON-RIGOROUS CANDIDATE-QUALITY FEASIBILITY STUDY",
        "runs": [],
        "failed_or_null_settings": [],
    }
    for degree in (8, 10, 12, 14, 16):
        try:
            result = solve_spectral_sr(degree, quadrature_order=256)
        except Exception as exc:
            payload["failed_or_null_settings"].append(  # type: ignore[union-attr]
                {"degree": degree, "error": f"{type(exc).__name__}: {exc}"}
            )
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            raise
        summary = result.summary()
        payload["runs"].append(summary)  # type: ignore[union-attr]
        print(json.dumps(summary, sort_keys=True), flush=True)
    finest = payload["runs"][-1]  # type: ignore[index]
    payload["comparison"] = {
        "phase4b_monte_carlo_gamma": 17.272084700443617,
        "finest_spectral_gamma": finest["gamma"],
        "difference": float(finest["gamma"]) - 17.272084700443617,
        "monte_carlo_standard_errors": abs(
            float(finest["gamma"]) - 17.272084700443617
        )
        / 0.028026952428261528,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
