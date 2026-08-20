"""Run the frozen Phase-4B stopped-score campaign and positive control."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import time
from pathlib import Path

import flint
import numpy as np

from rebaseguard_phase4b.cusum_control import simulate_protected_cusum_control
from rebaseguard_phase4b.harness import StoppingSample
from rebaseguard_phase4b.sr_simulation import simulate_symmetric_sr


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "proofs" / "phase4b" / "diagnostic_runs.json"
CALIBRATION = ROOT / "proofs" / "phase4b" / "arl_calibration.json"
SR_SEEDS = (1729, 20260818)
CUSUM_CONTROL_SEED = 1729
PROTECTED_PATHS = (
    ROOT / "src" / "rebaseguard_certify" / "bellman.py",
    ROOT / "proofs" / "certificate.json",
    ROOT / "proofs" / "enclosure.json",
    ROOT / "proofs" / "residual.json",
    ROOT / "proofs" / "contraction_monotone.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _environment() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": importlib.metadata.version("numpy"),
        "scipy": importlib.metadata.version("scipy"),
        "python_flint": importlib.metadata.version("python-flint"),
        "flint": flint.__FLINT_VERSION__,
    }


def _classification(summary: dict[str, object]) -> dict[str, str]:
    gamma = float(summary["gamma"])
    lower = float(summary["gamma_ci95_lower"])
    upper = float(summary["gamma_ci95_upper"])
    if lower > 5.0:
        category = "GREEN-A candidate"
        meaning = "strong second-detector instability witness"
    elif lower > 2.0 and upper <= 5.0:
        category = "GREEN-B candidate"
        meaning = "nontrivial second-detector instability witness"
    elif lower <= 2.0 <= upper:
        category = "NEAR-CRITICAL / UNRESOLVED"
        meaning = "do not certify from this diagnostic"
    elif upper < 2.0:
        category = "NO WITNESS"
        meaning = "no instability witness for this detector/configuration"
    else:
        category = "GREEN-A/B BOUNDARY"
        meaning = "clearly above two, but the interval does not classify strength"
    return {
        "category": category,
        "meaning": meaning,
        "rule": (
            "95% diagnostic interval: lower>5 GREEN-A; lower>2 and upper<=5 "
            "GREEN-B; overlap 2 near-critical; upper<2 no witness"
        ),
        "point_estimate_regime": (
            "Gamma_D>5" if gamma > 5.0 else "2<Gamma_D<=5" if gamma > 2.0 else "Gamma_D<=2"
        ),
    }


def _concatenate(samples: list[StoppingSample]) -> StoppingSample:
    return StoppingSample(
        tau=np.concatenate([sample.tau for sample in samples]),
        z_tau=np.concatenate([sample.z_tau for sample in samples]),
        t_tau=np.concatenate([sample.t_tau for sample in samples]),
        arm=np.concatenate([sample.arm for sample in samples]),
    )


def _base_payload(*, samples: int, threshold: float) -> dict[str, object]:
    return {
        "schema": "rebaseguard.phase4b.stopped-score-diagnostics.v1",
        "proof_role": "NON-RIGOROUS PHASE-4B DIAGNOSTIC ONLY",
        "status": "running",
        "detector": {
            "name": "symmetric two-chart Shiryaev-Roberts",
            "delta": 1.0,
            "threshold_A": threshold,
            "threshold_source": "proofs/phase4b/arl_calibration.json",
            "threshold_selected_without_gamma": True,
            "boundary": "inclusive post-update max(R_plus,R_minus)>=A",
        },
        "precommit": {
            "Gamma_D>5": "strong instability witness / GREEN-A candidate",
            "clearly 2<Gamma_D<=5": "nontrivial witness / GREEN-B candidate",
            "near 2": "near-critical; do not immediately certify",
            "Gamma_D<2": "no instability witness for this configuration",
        },
        "sr_campaign": {
            "samples_per_seed": samples,
            "precommitted_seeds": list(SR_SEEDS),
            "runs": [],
        },
        "protected_cusum_positive_control": {
            "configuration": {"k": 0.5, "h": 5.0, "m": 1},
            "sample_size": samples,
            "seed": CUSUM_CONTROL_SEED,
            "result": None,
        },
        "attempted_settings": [],
        "failed_or_null_settings": [],
        "environment": _environment(),
        "protected_hashes": {
            str(path.relative_to(ROOT)): _sha256(path) for path in PROTECTED_PATHS
        },
    }


def _checkpoint(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.samples <= 1:
        raise ValueError("samples must exceed one")

    calibration = json.loads(CALIBRATION.read_text())
    if calibration["selection_uses_gamma"] is not False:
        raise RuntimeError("threshold calibration was not Gamma-blind")
    threshold = float(calibration["selected_threshold_A"])
    payload = _base_payload(samples=args.samples, threshold=threshold)
    _checkpoint(args.output, payload)

    sr_samples: list[StoppingSample] = []
    for seed in SR_SEEDS:
        setting = {
            "detector": "symmetric two-chart Shiryaev-Roberts",
            "delta": 1.0,
            "threshold_A": threshold,
            "sample_size": args.samples,
            "seed": seed,
        }
        payload["attempted_settings"].append(setting)  # type: ignore[union-attr]
        started = time.perf_counter()
        try:
            sample = simulate_symmetric_sr(
                args.samples, threshold=threshold, seed=seed
            )
        except Exception as exc:
            failed = dict(setting)
            failed["error"] = f"{type(exc).__name__}: {exc}"
            payload["failed_or_null_settings"].append(failed)  # type: ignore[union-attr]
            _checkpoint(args.output, payload)
            raise
        summary = sample.summary(detector="symmetric two-chart Shiryaev-Roberts")
        summary.update({"seed": seed, "runtime_seconds": time.perf_counter() - started})
        payload["sr_campaign"]["runs"].append(summary)  # type: ignore[index,union-attr]
        sr_samples.append(sample)
        _checkpoint(args.output, payload)
        print(json.dumps(summary, sort_keys=True), flush=True)

    combined = _concatenate(sr_samples).summary(
        detector="symmetric two-chart Shiryaev-Roberts"
    )
    payload["sr_campaign"]["combined"] = combined  # type: ignore[index]
    payload["witness_classification"] = _classification(combined)
    _checkpoint(args.output, payload)

    control_setting = {
        "detector": "protected two-sided Gaussian CUSUM",
        "k": 0.5,
        "h": 5.0,
        "m": 1,
        "sample_size": args.samples,
        "seed": CUSUM_CONTROL_SEED,
    }
    payload["attempted_settings"].append(control_setting)  # type: ignore[union-attr]
    started = time.perf_counter()
    try:
        control = simulate_protected_cusum_control(
            args.samples, seed=CUSUM_CONTROL_SEED
        )
    except Exception as exc:
        failed = dict(control_setting)
        failed["error"] = f"{type(exc).__name__}: {exc}"
        payload["failed_or_null_settings"].append(failed)  # type: ignore[union-attr]
        _checkpoint(args.output, payload)
        raise
    control_summary = control.summary(detector="protected two-sided Gaussian CUSUM")
    control_summary.update(
        {"seed": CUSUM_CONTROL_SEED, "runtime_seconds": time.perf_counter() - started}
    )
    payload["protected_cusum_positive_control"]["result"] = control_summary  # type: ignore[index]
    payload["status"] = "complete"
    _checkpoint(args.output, payload)
    print(json.dumps(control_summary, sort_keys=True), flush=True)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
