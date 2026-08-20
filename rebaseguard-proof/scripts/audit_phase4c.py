"""Independent consistency/protection audit for the Phase-4C feasibility gate."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import platform
import sys
from pathlib import Path

import flint


ROOT = Path(__file__).resolve().parent.parent
PHASE = ROOT / "proofs" / "phase4c"
REPORT = PHASE / "ReBaseGuard_Phase4C_SR_Certification_Feasibility_Report.md"
PROTECTED = (
    ROOT / "src" / "rebaseguard_certify" / "bellman.py",
    ROOT / "proofs" / "certificate.json",
    ROOT / "proofs" / "enclosure.json",
    ROOT / "proofs" / "residual.json",
    ROOT / "proofs" / "contraction_monotone.json",
    ROOT / "proofs" / "phase4b" / "diagnostic_runs.json",
    ROOT / "proofs" / "phase4b" / "audit.json",
)
INPUTS = (
    PHASE / "analytic_structure.json",
    PHASE / "approximate_solve.json",
    PHASE / "spectral_candidate_study.json",
    PHASE / "interval_prototype.json",
    PHASE / "contraction_prototype.json",
    PHASE / "error_budget.json",
    PHASE / "operator_geometry_derivation.md",
    REPORT,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str) -> dict[str, object]:
    return json.loads((PHASE / name).read_text())


def _mid(record: dict[str, str]) -> float:
    return float(record["ball"].split()[0].lstrip("["))


def main() -> None:
    analytic = _load("analytic_structure.json")
    approximate = _load("approximate_solve.json")
    spectral = _load("spectral_candidate_study.json")
    interval = _load("interval_prototype.json")
    contraction = _load("contraction_prototype.json")
    budget = _load("error_budget.json")
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    check(
        "all Arb analytic structure checks pass",
        all(bool(value) for value in analytic["checks"].values()),
        analytic["checks"],
    )
    width = _mid(analytic["constants"]["minimum_continuation_width"])
    product_max = _mid(analytic["constants"]["product_max"])
    check(
        "compact reachable enclosure is quantitatively useful",
        width > 6.79 and product_max < 304.0,
        {"minimum_width": width, "product_max": product_max},
    )

    approximate_runs = approximate["runs"]
    gammas = [float(run["gamma"]) for run in approximate_runs]
    check(
        "bilinear continuum refinement approaches Phase-4B scale",
        all(right > left for left, right in zip(gammas, gammas[1:]))
        and abs(gammas[-1] - 17.272084700443617) < 0.002,
        gammas,
    )
    spectral_runs = spectral["runs"]
    finest = spectral_runs[-1]
    check(
        "independent spectral solve agrees with Monte Carlo",
        abs(float(finest["gamma"]) - 17.272084700443617)
        < 0.028026952428261528,
        {"spectral": finest["gamma"], "monte_carlo": 17.272084700443617},
    )
    check(
        "degree-16 candidate residual scale is adequate",
        float(finest["independent_grid_residual_a"]) < 1e-6
        and float(finest["independent_grid_residual_b"]) < 1e-5
        and float(finest["collocation_condition_number"]) < 2500,
        finest,
    )

    interval_groups: dict[str, list[dict[str, object]]] = {}
    for row in interval["records"]:
        interval_groups.setdefault(str(row["cell"]), []).append(row)
    refining = True
    for rows in interval_groups.values():
        rows.sort(key=lambda row: float(row["state_width"]), reverse=True)
        for key in ("residual_a", "residual_b"):
            values = [float(row[key]["width_upper"]) for row in rows]
            refining &= all(right < left for left, right in zip(values, values[1:]))
        q_values = [float(row["q_plus_curvature_width"]) for row in rows]
        refining &= all(right < left for left, right in zip(q_values, q_values[1:]))
    check("representative Arb widths refine normally", refining, list(interval_groups))
    finest_raw_b = {
        name: float(sorted(rows, key=lambda row: float(row["state_width"]))[0]["residual_b"]["width_upper"])
        for name, rows in interval_groups.items()
    }
    check(
        "raw boxes honestly rejected for cancellation loss",
        max(finest_raw_b.values()) > 2.0,
        finest_raw_b,
    )

    monotone = contraction["one_sided_monotone"]
    computed_q = _mid(monotone["computed_hit_probability"])
    resolvent = _mid(monotone["resolvent_bound"])
    check(
        "continuum one-sided contraction certified",
        computed_q > 0.11
        and monotone["continuum_argument"]["sampled_grid_used"] is False
        and math.isclose(resolvent, 139.0 / 0.11, rel_tol=1e-12),
        {"computed_q": computed_q, "resolvent": resolvent},
    )
    check(
        "analytic block contraction independently positive",
        _mid(contraction["block_sum"]["q"]) > 0.0003,
        contraction["block_sum"]["q"],
    )

    target = budget["pessimistic_target_budget"]
    check(
        "pessimistic coupled error budget remains above two",
        float(target["expected_lower_bound"]) > 8.0
        and float(budget["failure_boundary_with_other_target_fixed"]["maximum_eps_a_for_lower_gt_2"])
        > float(target["target_global_residual_a"])
        and float(budget["failure_boundary_with_other_target_fixed"]["maximum_eps_b_for_lower_gt_2"])
        > float(target["target_global_residual_b"]),
        target,
    )
    check(
        "candidate identity agrees across interval and budget artifacts",
        interval["candidate"]["sha256"] == budget["candidate"]["sha256"],
        interval["candidate"]["sha256"],
    )

    report_text = REPORT.read_text()
    check(
        "report contains all 21 required sections",
        all(f"## {index}." in report_text for index in range(1, 22)),
        "sections 1-21",
    )
    check(
        "report ends with required structured summary",
        report_text.rstrip().endswith(
            "3. A degree-16 candidate and pessimistic coupled error budget leave a projected lower endpoint near 8.5"
        )
        and "BEGIN FULL CERTIFICATION:\nNO" in report_text,
        "structured stop gate present",
    )
    forbidden = [
        PHASE / "certificate.json",
        PHASE / "final_certificate.json",
        PHASE / "enclosure.json",
    ]
    check(
        "no final SR certificate was generated",
        not any(path.exists() for path in forbidden),
        [str(path.relative_to(ROOT)) for path in forbidden],
    )

    expected_protected = {
        "src/rebaseguard_certify/bellman.py": "5731eb539d73d0f0ca578c22ebc48be14220c9cb61e71d2ac816b9c85dc48343",
        "proofs/certificate.json": "85e68c7dde306f2e6ce464203def22089e9b935d1cfca4b4944cef191d80545e",
        "proofs/enclosure.json": "71c3a68c4d82f3663254975b4bbc6c41632e54430a8e86538ee446dc83145907",
        "proofs/residual.json": "dc463417f629ed0b770967459621f0ebd308df3dd06ca13c57129b168b29edce",
        "proofs/contraction_monotone.json": "694f46dbb65f7d43e37d0e0af681e784d4a6599c232df2b5d94e3f15ae3be434",
        "proofs/phase4b/diagnostic_runs.json": "8f1ef75a91995606a24c05da92f6ff9a345bbd32a5b2e6443246c6052bed14d8",
        "proofs/phase4b/audit.json": "489bbabe99041ab45c7e8f40c36bc543ea5a4b538ae7fb589d8b967f076c97c8",
    }
    actual_protected = {
        str(path.relative_to(ROOT)): _sha256(path) for path in PROTECTED
    }
    check("Level-3 and Phase-4B hashes unchanged", actual_protected == expected_protected, actual_protected)

    passed = all(bool(row["pass"]) for row in checks)
    payload = {
        "schema": "rebaseguard.phase4c.feasibility-audit.v1",
        "proof_role": "INDEPENDENT FEASIBILITY AUDIT; NOT A GAMMA CERTIFICATE",
        "status": "PASS" if passed else "FAIL",
        "verdict": "GREEN" if passed else "RED",
        "checks": checks,
        "environment": {
            "python": platform.python_version(),
            "numpy": importlib.metadata.version("numpy"),
            "scipy": importlib.metadata.version("scipy"),
            "python_flint": importlib.metadata.version("python-flint"),
            "flint": flint.__FLINT_VERSION__,
        },
        "protected_hashes": actual_protected,
        "input_hashes": {
            str(path.relative_to(ROOT)): _sha256(path) for path in INPUTS
        },
        "conclusion": (
            "SR certification feasibility GREEN; full certification not begun"
            if passed
            else "Phase-4C feasibility audit failed"
        ),
    }
    destination = PHASE / "audit.json"
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
