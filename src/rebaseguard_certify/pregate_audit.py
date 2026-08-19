"""Independent consistency audit for the Phase-4 pre-gate artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from flint import arb


EXPECTED_HASHES = {
    "src/rebaseguard_certify/bellman.py": (
        "5731eb539d73d0f0ca578c22ebc48be14220c9cb61e71d2ac816b9c85dc48343"
    ),
    "proofs/certificate.json": (
        "85e68c7dde306f2e6ce464203def22089e9b935d1cfca4b4944cef191d80545e"
    ),
    "proofs/enclosure.json": (
        "71c3a68c4d82f3663254975b4bbc6c41632e54430a8e86538ee446dc83145907"
    ),
    "proofs/residual.json": (
        "dc463417f629ed0b770967459621f0ebd308df3dd06ca13c57129b168b29edce"
    ),
    "proofs/contraction_monotone.json": (
        "694f46dbb65f7d43e37d0e0af681e784d4a6599c232df2b5d94e3f15ae3be434"
    ),
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ArithmeticError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_pregate(repository: Path) -> dict[str, object]:
    payload = json.loads((repository / "diagnostics" / "phase4_pregate.json").read_text())
    report_text = (
        repository / "proofs" / "ReBaseGuard_Phase4_Feasibility_PreGate_Report.md"
    ).read_text()

    for relative, expected in EXPECTED_HASHES.items():
        _require(_sha256(repository / relative) == expected, f"protected hash changed: {relative}")
        _require(
            payload["protected_hashes"][relative] == expected,
            f"stored protected hash mismatch: {relative}",
        )

    historical = arb(payload["historical_reproduction"]["gamma_finite"]["ball"])
    reachable = arb(payload["reachable_subset_ablation"]["gamma_finite"]["ball"])
    _require((historical - reachable).contains(0), "reachable ablation changed historical Gamma")
    _require(
        int(payload["reachable_subset_ablation"]["reachable_nodes"])
        < int(payload["reachable_subset_ablation"]["full_square_nodes"]),
        "reachable-state ablation removed no states",
    )
    historical_arl = arb(payload["reachable_subset_ablation"]["arl_finite"]["ball"])
    _require(historical_arl > 2_000, "historical finite persistence was not reproduced")

    runs = payload["monte_carlo"]["runs"]
    _require(len(runs) >= 2, "fewer than two Monte Carlo seeds")
    _require(len({int(run["seed"]) for run in runs}) == len(runs), "Monte Carlo seeds repeat")
    for run in runs:
        _require(int(run["n"]) >= 1_000_000, "Monte Carlo run is too small")
        separation = abs(float(historical.mid()) - float(run["gamma"])) / float(run["gamma_se"])
        _require(separation > 50.0, "Monte Carlo does not decisively separate the values")

    refined = payload["refined_reachable_bellman"]
    gammas = [float(row["gamma_finite"]) for row in refined]
    arl_errors = [abs(float(row["arl_finite"]) - 465.0) for row in refined]
    _require(all(left < right for left, right in zip(gammas, gammas[1:])), "Gamma refinement is not monotone")
    _require(
        all(left > right for left, right in zip(arl_errors, arl_errors[1:])),
        "ARL refinement does not approach the validated scale",
    )
    _require(
        max(float(row["maximum_mass_error"]) for row in refined) < 1e-12,
        "refined Bellman mass balance failed",
    )
    point = float(payload["corrected_point_estimate"]["gamma"])
    _require(15.88 < point < 15.90, "corrected point estimate is outside the audit window")
    _require(
        payload["classification"]["category"] == "D. FINITE DISCRETIZATION BIAS",
        "unexpected discrepancy classification",
    )

    required_report_text = (
        "Γ DISCREPANCY:\nRESOLVED",
        "LEVEL-3 THEOREM STATUS:\nUNCHANGED",
        "CUSUM USED IN SCORE IDENTITY:\nNOT ESSENTIAL",
        "GAUSSIAN ARBITRARY-STOPPING-TIME IDENTITY:\nPROVED",
        "EXPONENTIAL-FAMILY GENERALIZATION:\nPROVED",
        "LEVEL-4 ROUTE:\nGREEN",
        "SECOND DETECTOR GATE:\nGO",
    )
    for item in required_report_text:
        _require(item in report_text, f"missing final report statement: {item}")

    return {
        "schema": "rebaseguard.phase4-pregate-audit.v1",
        "status": "PASS",
        "protected_hashes_verified": True,
        "historical_value_reproduced": True,
        "reachable_ablation_verified": True,
        "monte_carlo_separation_verified": True,
        "refinement_verified": True,
        "report_statuses_verified": True,
        "classification": "D. FINITE DISCRETIZATION BIAS",
        "corrected_point_estimate": point,
        "level4_route": "GREEN",
    }


def main() -> None:
    repository = Path(__file__).resolve().parents[2]
    print(json.dumps(audit_pregate(repository), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
