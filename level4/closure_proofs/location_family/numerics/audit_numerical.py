#!/usr/bin/env python3
"""Independent retained-summary auditor for the frozen Track-3 numerical gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]
RESULTS = CAMPAIGN / "results"
PROTOCOL_SHA256 = "52a27f178f91b88abfc78c28c327084eedafa61e6e91b24354a9faf1b3ed55f6"
PRIMARY_H = 0.0125


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean_se(values) -> tuple[float, float]:
    array = np.asarray(values, dtype=float)
    return float(array.mean()), float(array.std(ddof=1) / np.sqrt(array.size))


def abs_z(x: float, sx: float, y: float, sy: float) -> float:
    return float(abs(x - y) / np.hypot(sx, sy))


def relative(x: float, y: float) -> float:
    return float(abs(x - y) / ((abs(x) + abs(y)) / 2.0))


def close(x: float, y: float, tolerance: float = 1e-12) -> bool:
    return bool(abs(x - y) <= tolerance * max(1.0, abs(x), abs(y)))


def audit() -> dict:
    route_a = json.loads((RESULTS / "route_a.json").read_text())
    route_b = json.loads((RESULTS / "route_b.json").read_text())
    decision = json.loads((RESULTS / "numerical_decision.json").read_text())
    structural = json.loads((RESULTS / "structural_controls.json").read_text())
    manifest = json.loads((RESULTS / "historical_manifest.json").read_text())

    checks = {
        "protocol_hash": sha256(CAMPAIGN / "PROTOCOL.md") == PROTOCOL_SHA256,
        "historical_hashes": all(
            sha256(REPO / relative_path) == expected
            for relative_path, expected in manifest["sha256"].items()
        ),
        "structural_pass": structural["pass"] is True,
        "stored_status_failed": decision["status"]
        == "LOCATION-FAMILY-NUMERICAL-FAILED",
        "stored_lean_not_authorized": decision["lean_authorized"] is False,
    }
    rows = []
    recomputed_all_pass = structural["pass"]
    failed_predicates = []
    stored_by_family = {row["family"]: row for row in decision["rows"]}

    for family, a_family in route_a["families"].items():
        stored = stored_by_family[family]
        a_batches = a_family["batches"]
        gamma, gamma_se = mean_se([row["gamma_f"] for row in a_batches])
        derivative = 1.0 - gamma
        b_family = route_b["families"][family]
        rep_summaries = []
        all_primary = []
        for replication in b_family["replications"]:
            primary = []
            for batch in replication["batches"]:
                index = next(
                    i
                    for i, step in enumerate((0.05, 0.025, 0.0125))
                    if step == PRIMARY_H
                )
                primary.append(batch["paired_derivatives"][index])
            rep_mean, rep_se = mean_se(primary)
            rep_summaries.append((rep_mean, rep_se))
            all_primary.extend(primary)
        pooled, pooled_se = mean_se(all_primary)
        correspondence_z = abs_z(derivative, gamma_se, pooled, pooled_se)
        correspondence_relative = relative(derivative, pooled)
        replication_z = abs_z(*rep_summaries[0], *rep_summaries[1])
        replication_relative = relative(rep_summaries[0][0], rep_summaries[1][0])
        arl = float(np.mean([row["arl"] for row in a_batches]))
        arl_relative = abs(arl / a_family["summary"]["historical_arl"] - 1.0)
        criteria = {
            "correspondence_abs_z_le_3": correspondence_z <= 3.0,
            "correspondence_relative_le_3pct": correspondence_relative <= 0.03,
            "replication_abs_z_le_3": replication_z <= 3.0,
            "replication_relative_le_3pct": replication_relative <= 0.03,
            "route_a_arl_within_2pct": arl_relative <= 0.02,
            "route_a_zero_ties": sum(row["ties"] for row in a_batches) == 0
            and sum(row["simultaneous_crossings"] for row in a_batches) == 0,
            "route_b_zero_ties": b_family["ties"] == 0
            and b_family["simultaneous_crossings"] == 0,
        }
        family_pass = all(criteria.values())
        recomputed_all_pass &= family_pass
        for predicate, passed in criteria.items():
            if not passed:
                failed_predicates.append(f"{family}:{predicate}")
        stored_match = all(
            [
                close(gamma, stored["gamma_f"]),
                close(gamma_se, stored["gamma_f_se"]),
                close(derivative, stored["route_a_predicted_derivative"]),
                close(pooled, stored["route_b_primary_derivative"]),
                close(pooled_se, stored["route_b_se"]),
                close(correspondence_z, stored["correspondence_abs_z"]),
                close(correspondence_relative, stored["correspondence_relative"]),
                close(replication_z, stored["replication_abs_z"]),
                close(replication_relative, stored["replication_relative"]),
                criteria == stored["criteria"],
                family_pass == stored["pass"],
            ]
        )
        checks[f"{family}_stored_summary_exact"] = stored_match
        rows.append(
            {
                "family": family,
                "gamma_f": gamma,
                "route_a_derivative": derivative,
                "route_b_derivative": pooled,
                "correspondence_abs_z": correspondence_z,
                "replication_abs_z": replication_z,
                "replication_relative": replication_relative,
                "criteria": criteria,
                "pass": family_pass,
            }
        )

    checks["recomputed_regular_gate_fails"] = recomputed_all_pass is False
    checks["exactly_one_failed_predicate"] = failed_predicates == [
        "t3:replication_relative_le_3pct"
    ]
    checks["no_lean_artifact_exists"] = not (CAMPAIGN / "lean").exists()
    return {
        "schema": "rebaseguard.location-family.numerical-audit.v1",
        "pass": all(checks.values()),
        "audit_scope": "honest reproduction of the frozen FAILED gate",
        "checks": checks,
        "failed_predicates": failed_predicates,
        "recomputed_status": "LOCATION-FAMILY-NUMERICAL-FAILED",
        "lean_authorized": False,
        "rows": rows,
    }


def main() -> None:
    result = audit()
    (RESULTS / "numerical_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    if not result["pass"]:
        raise SystemExit("Track-3 retained numerical audit: FAIL")
    print("Track-3 retained numerical audit: PASS (frozen numerical gate FAILED)")


if __name__ == "__main__":
    main()

