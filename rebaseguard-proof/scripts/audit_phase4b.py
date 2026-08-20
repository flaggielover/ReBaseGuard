"""Independent consistency and protection audit for Phase-4B artifacts."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PHASE = ROOT / "proofs" / "phase4b"
PROTECTED = (
    ROOT / "src" / "rebaseguard_certify" / "bellman.py",
    ROOT / "proofs" / "certificate.json",
    ROOT / "proofs" / "enclosure.json",
    ROOT / "proofs" / "residual.json",
    ROOT / "proofs" / "contraction_monotone.json",
)
AUDITED_INPUTS = (
    PHASE / "detector_selection.md",
    PHASE / "detector_definition.md",
    PHASE / "score_derivation.md",
    PHASE / "convention_matrix.md",
    PHASE / "pathwise_replay.json",
    PHASE / "arl_calibration.json",
    PHASE / "diagnostic_runs.json",
    PHASE / "multicyle_diagnostic.json",
    PHASE / "phase4b_witness_report.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict[str, object]:
    return json.loads((PHASE / name).read_text())


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    pathwise = _load("pathwise_replay.json")
    calibration = _load("arl_calibration.json")
    diagnostic = _load("diagnostic_runs.json")
    multicycle = _load("multicyle_diagnostic.json")

    check("pathwise replay complete", pathwise["all_checks_pass"] is True, pathwise["all_checks_pass"])
    boundary = pathwise["inclusive_boundary_cases"]
    check(
        "inclusive alarm boundary",
        [row["first_step_alarm"] for row in boundary] == [False, True, True],
        boundary,
    )
    check(
        "reflection reward preserved",
        pathwise["reflection_check"]["reward_preserved"] is True,
        pathwise["reflection_check"],
    )
    check(
        "simultaneous tie replayed independently",
        pathwise["simultaneous_tie_check"]["match"] is True,
        pathwise["simultaneous_tie_check"],
    )

    attempts = calibration["attempts"]
    check("all 12 calibration attempts preserved", len(attempts) == 12, len(attempts))
    check(
        "calibration Gamma-blind",
        calibration["selection_uses_gamma"] is False
        and all(row["gamma_not_inspected"] is True for row in attempts),
        {"selection_uses_gamma": calibration["selection_uses_gamma"]},
    )
    check(
        "delta frozen through calibration",
        calibration["delta"] == 1.0 and calibration["delta_frozen_before_gamma"] is True,
        calibration["delta"],
    )
    closest = min(attempts, key=lambda row: abs(float(row["arl"]) - 465.0))
    check(
        "selected A follows declared ARL-only rule",
        float(calibration["selected_threshold_A"]) == float(closest["threshold_A"])
        and float(calibration["selected_arl_estimate"]) == float(closest["arl"]),
        closest,
    )
    sensitivity = [row for row in attempts if str(row["phase"]).startswith("sensitivity_")]
    selected_a = float(calibration["selected_threshold_A"])
    check(
        "0.95/1.00/1.05 ARL sensitivity preserved",
        [float(row["threshold_A"]) for row in sensitivity]
        == [0.95 * selected_a, selected_a, 1.05 * selected_a],
        [row["threshold_A"] for row in sensitivity],
    )
    expected_versions = {
        "python": "3.14.5",
        "numpy": "2.5.2",
        "scipy": "1.18.0",
        "python_flint": "0.9.0",
        "flint": "3.6.0",
    }
    check(
        "pinned numerical environment recorded",
        all(calibration["environment"].get(key) == value for key, value in expected_versions.items()),
        calibration["environment"],
    )

    sr = diagnostic["sr_campaign"]
    runs = sr["runs"]
    combined = sr["combined"]
    check("diagnostic complete", diagnostic["status"] == "complete", diagnostic["status"])
    check(
        "precommitted independent SR seeds",
        [row["seed"] for row in runs] == [1729, 20260818]
        and all(row["n"] == 1_000_000 for row in runs),
        [(row["seed"], row["n"]) for row in runs],
    )
    total_n = sum(int(row["n"]) for row in runs)
    weighted_gamma = sum(int(row["n"]) * float(row["gamma"]) for row in runs) / total_n
    weighted_arl = sum(int(row["n"]) * float(row["arl"]) for row in runs) / total_n
    check(
        "pooled SR means replay",
        total_n == int(combined["n"])
        and math.isclose(weighted_gamma, float(combined["gamma"]), abs_tol=1e-14)
        and math.isclose(weighted_arl, float(combined["arl"]), abs_tol=1e-14),
        {"n": total_n, "gamma": weighted_gamma, "arl": weighted_arl},
    )
    z95 = 1.959963984540054
    expected_lower = float(combined["gamma"]) - z95 * float(combined["gamma_se"])
    expected_upper = float(combined["gamma"]) + z95 * float(combined["gamma_se"])
    check(
        "Gamma interval and slope replay",
        math.isclose(expected_lower, float(combined["gamma_ci95_lower"]), abs_tol=1e-14)
        and math.isclose(expected_upper, float(combined["gamma_ci95_upper"]), abs_tol=1e-14)
        and math.isclose(1.0 - float(combined["gamma"]), float(combined["fprime"]), abs_tol=1e-14),
        {"lower": expected_lower, "upper": expected_upper, "fprime": 1.0 - float(combined["gamma"])},
    )
    check(
        "precommitted GREEN-A criterion met",
        expected_lower > 5.0 and diagnostic["witness_classification"]["category"] == "GREEN-A candidate",
        {"lower": expected_lower, "category": diagnostic["witness_classification"]["category"]},
    )
    check(
        "SR convention diagnostics centered",
        abs(float(combined["direction_symmetry_gap"])) < 0.002
        and abs(float(combined["mean_z_tau"])) < 0.005
        and abs(float(combined["mean_t_tau"])) < 0.05
        and abs(float(combined["wald_second_gap"])) < 3.0,
        {
            "direction_gap": combined["direction_symmetry_gap"],
            "mean_z_tau": combined["mean_z_tau"],
            "mean_t_tau": combined["mean_t_tau"],
            "wald_gap": combined["wald_second_gap"],
        },
    )
    control = diagnostic["protected_cusum_positive_control"]["result"]
    check(
        "protected CUSUM positive-control scale",
        control["seed"] == 1729
        and control["n"] == 1_000_000
        and 450.0 < float(control["arl"]) < 480.0
        and 15.0 < float(control["gamma"]) < 17.0,
        {"arl": control["arl"], "gamma": control["gamma"]},
    )
    check(
        "diagnostic failed/null ledger preserved and empty",
        diagnostic["failed_or_null_settings"] == [],
        diagnostic["failed_or_null_settings"],
    )

    critical = multicycle["critical_fraction"]
    gamma = float(combined["gamma"])
    rho_c = 1.0 / (gamma - 1.0)
    expected_rho_interval = [
        1.0 / (float(combined["gamma_ci95_upper"]) - 1.0),
        1.0 / (float(combined["gamma_ci95_lower"]) - 1.0),
    ]
    check(
        "mixed-reuse critical fraction replay",
        math.isclose(rho_c, float(critical["rho_c"]), abs_tol=1e-15)
        and all(
            math.isclose(left, right, abs_tol=1e-15)
            for left, right in zip(expected_rho_interval, critical["rho_c_transformed_ci95"])
        ),
        {"rho_c": rho_c, "interval": expected_rho_interval},
    )
    policies = multicycle["attempted_settings"]
    check(
        "precommitted multi-cycle policies replay",
        [row["name"] for row in policies]
        == ["fresh", "below_local_threshold", "above_local_threshold", "full_reuse"]
        and math.isclose(float(policies[1]["rho"]), 0.8 * rho_c)
        and math.isclose(float(policies[2]["rho"]), 1.2 * rho_c)
        and float(policies[0]["rho"]) == 0.0
        and float(policies[3]["rho"]) == 1.0,
        policies,
    )
    full = next(row for row in multicycle["runs"] if row["name"] == "full_reuse")
    fresh = next(row for row in multicycle["runs"] if row["name"] == "fresh")
    check(
        "multi-cycle full-reuse alternation sanity check",
        float(full["lag1_reference_correlation"]) < -0.4
        and float(full["alarm_direction_alternation_fraction"]) > 0.8
        and abs(float(fresh["lag1_reference_correlation"])) < 0.05,
        {
            "full_lag1": full["lag1_reference_correlation"],
            "full_alternation": full["alarm_direction_alternation_fraction"],
            "fresh_lag1": fresh["lag1_reference_correlation"],
        },
    )
    check(
        "multi-cycle failed/null ledger preserved and empty",
        multicycle["failed_or_null_settings"] == [],
        multicycle["failed_or_null_settings"],
    )

    embedded_hashes = diagnostic["protected_hashes"]
    actual_hashes = {str(path.relative_to(ROOT)): _sha256(path) for path in PROTECTED}
    check("protected Level-3 hashes unchanged", embedded_hashes == actual_hashes, actual_hashes)
    check(
        "report states certification stop gate",
        "rigorous certification not started" in (PHASE / "phase4b_witness_report.md").read_text(),
        "explicit stop statement present",
    )

    passed = all(bool(row["pass"]) for row in checks)
    payload = {
        "schema": "rebaseguard.phase4b.audit.v1",
        "proof_role": "INDEPENDENT DIAGNOSTIC ARTIFACT AUDIT; NOT A CONTINUUM CERTIFICATE",
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "audited_input_hashes": {
            str(path.relative_to(ROOT)): _sha256(path) for path in AUDITED_INPUTS
        },
        "protected_hashes": actual_hashes,
        "conclusion": (
            "GREEN-A diagnostic witness independently replayed; certification stop gate intact"
            if passed
            else "Phase-4B diagnostic audit failed"
        ),
    }
    destination = PHASE / "audit.json"
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
