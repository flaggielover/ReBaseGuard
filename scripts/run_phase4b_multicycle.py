"""Run the precommitted modest Phase-4B multi-cycle sanity check."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from rebaseguard_phase4b.multicycle import simulate_multicycle_sr


ROOT = Path(__file__).resolve().parent.parent
DIAGNOSTIC = ROOT / "proofs" / "phase4b" / "diagnostic_runs.json"
DEFAULT_OUTPUT = ROOT / "proofs" / "phase4b" / "multicyle_diagnostic.json"


def _checkpoint(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chains", type=int, default=512)
    parser.add_argument("--cycles", type=int, default=120)
    parser.add_argument("--burn-in", type=int, default=30)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    diagnostic = json.loads(DIAGNOSTIC.read_text())
    if diagnostic["status"] != "complete":
        raise RuntimeError("stopped-score campaign is incomplete")
    combined = diagnostic["sr_campaign"]["combined"]
    gamma = float(combined["gamma"])
    gamma_se = float(combined["gamma_se"])
    gamma_lower = float(combined["gamma_ci95_lower"])
    gamma_upper = float(combined["gamma_ci95_upper"])
    if gamma_lower <= 2.0:
        raise RuntimeError("critical reuse fraction is not established diagnostically")
    rho_c = 1.0 / (gamma - 1.0)
    rho_c_se = gamma_se / (gamma - 1.0) ** 2
    rho_c_interval = [1.0 / (gamma_upper - 1.0), 1.0 / (gamma_lower - 1.0)]
    policies = [
        {"name": "fresh", "rho": 0.0, "seed": 41001},
        {"name": "below_local_threshold", "rho": 0.8 * rho_c, "seed": 41002},
        {"name": "above_local_threshold", "rho": 1.2 * rho_c, "seed": 41003},
        {"name": "full_reuse", "rho": 1.0, "seed": 41004},
    ]
    payload: dict[str, object] = {
        "schema": "rebaseguard.phase4b.multicycle-diagnostic.v1",
        "proof_role": "NON-RIGOROUS MULTI-CYCLE SANITY CHECK ONLY",
        "status": "running",
        "detector": diagnostic["detector"],
        "source_diagnostic": "proofs/phase4b/diagnostic_runs.json",
        "critical_fraction": {
            "identity": "rho_c=1/(Gamma_D-1)",
            "gamma": gamma,
            "rho_c": rho_c,
            "rho_c_delta_method_se": rho_c_se,
            "rho_c_transformed_ci95": rho_c_interval,
        },
        "policy_precommit": (
            "fresh rho=0; 0.8*rho_c below; 1.2*rho_c above; full rho=1"
        ),
        "configuration": {
            "chains": args.chains,
            "retained_cycles_per_chain": args.cycles,
            "burn_in_cycles": args.burn_in,
            "reference_update": (
                "e_next=rho*(e+Z_tau)+(1-rho)*X_fresh, X_fresh iid N(0,1)"
            ),
        },
        "attempted_settings": policies,
        "failed_or_null_settings": [],
        "runs": [],
    }
    _checkpoint(args.output, payload)

    for policy in policies:
        started = time.perf_counter()
        try:
            sample = simulate_multicycle_sr(
                threshold=float(diagnostic["detector"]["threshold_A"]),
                rho=float(policy["rho"]),
                seed=int(policy["seed"]),
                chains=args.chains,
                cycles_per_chain=args.cycles,
                burn_in_cycles=args.burn_in,
            )
        except Exception as exc:
            failed = dict(policy)
            failed["error"] = f"{type(exc).__name__}: {exc}"
            payload["failed_or_null_settings"].append(failed)  # type: ignore[union-attr]
            _checkpoint(args.output, payload)
            raise
        summary = sample.summary()
        summary.update(policy)
        summary["runtime_seconds"] = time.perf_counter() - started
        payload["runs"].append(summary)  # type: ignore[union-attr]
        _checkpoint(args.output, payload)
        print(json.dumps(summary, sort_keys=True), flush=True)

    payload["status"] = "complete"
    _checkpoint(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
