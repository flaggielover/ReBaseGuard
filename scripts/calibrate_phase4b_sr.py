"""ARL-only calibration for the frozen-delta symmetric SR detector."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import time
from pathlib import Path

import flint

from rebaseguard_phase4b.sr_simulation import simulate_symmetric_sr


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "proofs" / "phase4b" / "arl_calibration.json"
TARGET_ARL = 465.0
CALIBRATION_SEED = 314159


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _base_payload() -> dict[str, object]:
    return {
        "schema": "rebaseguard.phase4b.sr-arl-calibration.v1",
        "proof_role": "NON-RIGOROUS ARL CALIBRATION ONLY",
        "detector": "symmetric two-chart Shiryaev-Roberts",
        "delta": 1.0,
        "delta_frozen_before_gamma": True,
        "selection_uses_gamma": False,
        "target_arl": TARGET_ARL,
        "calibration_seed": CALIBRATION_SEED,
        "common_random_numbers": "path/time-addressable counter normals",
        "attempts": [],
        "environment": {
            "python": platform.python_version(),
            "numpy": importlib.metadata.version("numpy"),
            "scipy": importlib.metadata.version("scipy"),
            "python_flint": importlib.metadata.version("python-flint"),
            "flint": flint.__FLINT_VERSION__,
        },
        "protected_hashes": {
            "proofs/certificate.json": _sha256(ROOT / "proofs" / "certificate.json"),
            "src/rebaseguard_certify/bellman.py": _sha256(
                ROOT / "src" / "rebaseguard_certify" / "bellman.py"
            ),
        },
    }


def _write(payload: dict[str, object]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _attempt(
    payload: dict[str, object], *, threshold: float, n: int, phase: str
) -> dict[str, object]:
    started = time.perf_counter()
    result = simulate_symmetric_sr(
        n,
        threshold=threshold,
        seed=CALIBRATION_SEED,
        counter_based=True,
    ).summary(detector="symmetric_sr")
    record: dict[str, object] = {
        "attempt_index": len(payload["attempts"]) + 1,
        "phase": phase,
        "threshold_A": threshold,
        "sample_size": n,
        "seed": CALIBRATION_SEED,
        "runtime_seconds": time.perf_counter() - started,
        "arl": result["arl"],
        "arl_se": result["arl_se"],
        "decision": "above_target" if result["arl"] > TARGET_ARL else "below_target",
        "gamma_not_inspected": True,
    }
    payload["attempts"].append(record)
    _write(payload)
    print(json.dumps(record, sort_keys=True), flush=True)
    return record


def main() -> None:
    payload = _base_payload()
    _write(payload)
    coarse = [
        _attempt(payload, threshold=threshold, n=60_000, phase="coarse_bracket")
        for threshold in (300.0, 450.0, 600.0, 750.0)
    ]
    below = max((row for row in coarse if row["arl"] < TARGET_ARL), key=lambda row: row["threshold_A"])
    above = min((row for row in coarse if row["arl"] > TARGET_ARL), key=lambda row: row["threshold_A"])
    lower = float(below["threshold_A"])
    upper = float(above["threshold_A"])
    refinement: list[dict[str, object]] = []
    for _ in range(5):
        midpoint = (lower + upper) / 2.0
        row = _attempt(payload, threshold=midpoint, n=120_000, phase="bisection")
        refinement.append(row)
        if float(row["arl"]) < TARGET_ARL:
            lower = midpoint
        else:
            upper = midpoint
    candidates = coarse + refinement
    selected = min(candidates, key=lambda row: abs(float(row["arl"]) - TARGET_ARL))
    selected_threshold = float(selected["threshold_A"])
    sensitivity = [
        _attempt(
            payload,
            threshold=selected_threshold * factor,
            n=180_000,
            phase=f"sensitivity_{factor:.2f}",
        )
        for factor in (0.95, 1.0, 1.05)
    ]
    selected = min(
        [selected, sensitivity[1]],
        key=lambda row: abs(float(row["arl"]) - TARGET_ARL),
    )
    payload["selected_threshold_A"] = float(selected["threshold_A"])
    payload["selected_arl_estimate"] = float(selected["arl"])
    payload["selected_arl_se"] = float(selected["arl_se"])
    payload["selection_rule"] = "closest recorded ARL to 465; Gamma never inspected"
    payload["all_attempts_preserved"] = True
    _write(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

