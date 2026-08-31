#!/usr/bin/env python3
"""Mechanically derive the Priority-4 verdict from the artifacts on disk.

The verdict is a function of files, not of prose.  Every gate is named, every
gate is read from a produced artifact, and the negative claims are asserted as
explicitly as the positive ones.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parent
RESULTS = CAMPAIGN / "results"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text())


def load_optional(name: str) -> dict | None:
    path = RESULTS / name
    return json.loads(path.read_text()) if path.exists() else None


def main() -> None:
    protocol = json.loads((CAMPAIGN / "configs" / "P4_PROTOCOL.json").read_text())
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    corr = load("correspondence.json")
    mapping = load("stability_map.json")
    certificate = json.loads(
        (CAMPAIGN / "certificates" / "certificate.json").read_text()
    )
    lean = load("lean_compile.json")
    # The repository-wide verification is a separately runnable step.  If it has
    # not completed, its gate is reported PENDING and evaluates to False: a
    # closure verdict is never derived from an unfinished verification.
    verification = load_optional("verification.json")

    cells = corr["monte_carlo"]["cells"]
    supported = [c for c in cells if c["family_class"] == "THEOREM-SUPPORTED"]
    outside = [c for c in cells if c["family_class"] == "OUTSIDE-ASSUMPTIONS"]

    # Consistency with the closed Gaussian gains.
    #
    # Two statistics are computed and both are reported.  The **gate** uses the
    # statistic as originally coded, which divides by Priority 4's own standard
    # error alone and therefore treats the closed Monte Carlo value as exact.
    # That is the wrong test for comparing two Monte Carlo estimates, and it was
    # deliberately left unchanged after the data were seen so that no gate
    # outcome could be improved by editing it.  The correctly specified
    # combined-error statistic is reported beside it, using the closed
    # campaigns' own published standard errors read from the authoritative
    # artifact the protocol already names as the source of the point values.
    reference = protocol["frozen_reference_values"]
    closed_map = json.loads(
        (CAMPAIGN.parent / "m_rho_stability_priority3" / "results"
         / "stability_map.json").read_text()
    )
    reference_se: dict[str, dict[str, float]] = {
        "cusum_gaussian": {}, "sr_gaussian": {}
    }
    for entry in closed_map.get("cells", []) + closed_map.get("boundary_cells", []):
        key = {"CUSUM": "cusum_gaussian", "SR": "sr_gaussian"}.get(
            entry.get("detector_short")
        )
        if key and entry.get("gamma_tilde_se") is not None:
            reference_se[key][str(entry["m"])] = entry["gamma_tilde_se"]

    consistency = []
    consistency_combined = []
    consistency_rows = []
    for cell in cells:
        if cell["layer"] != "frozen" or cell["family"] != "gaussian":
            continue
        key = "cusum_gaussian" if cell["detector_kind"] == "cusum" else "sr_gaussian"
        frozen = reference[key][str(cell["m"])]
        se = cell["route_a"]["se"]
        diff = abs(cell["route_a"]["mean"] - frozen)
        single = diff / se if se > 0 else math.inf
        closed_se = reference_se[key].get(str(cell["m"]))
        combined = diff / math.hypot(se, closed_se) if closed_se else None
        consistency.append(single)
        if combined is not None:
            consistency_combined.append(combined)
        consistency_rows.append({
            "detector": cell["detector"], "m": cell["m"],
            "closed_value": frozen, "closed_se": closed_se,
            "priority4_value": cell["route_a"]["mean"], "priority4_se": se,
            "signed_relative_difference":
                (cell["route_a"]["mean"] - frozen) / abs(frozen),
            "z_single_error_gate_statistic": single,
            "z_combined_error_reported_statistic": combined,
        })

    families = {c["family"] for c in supported}
    detectors = {c["detector"] for c in cells}

    gates = {
        "protocol_hash_matches_manifest":
            sha256(CAMPAIGN / "configs" / "P4_PROTOCOL.json")
            == manifest["frozen_new_inputs"]["protocol_sha256"],
        "witness_hash_matches_manifest":
            sha256(CAMPAIGN / "certificates" / "WITNESS.json")
            == manifest["frozen_new_inputs"]["finite_support_witness_sha256"],
        "route_q_analytic_identity_holds": corr["route_q"]["all_pass"],
        "route_q_uniform_identity_fails_as_predicted":
            not corr["route_q"]["uniform_counterexample"]["identity_holds"],
        "route_n_neutrality_holds": corr["route_n"]["all_pass"],
        "all_theorem_supported_cells_pass":
            bool(supported) and all(c["verdict"] == "PASS" for c in supported),
        "all_outside_assumption_cells_demonstrate_failure":
            bool(outside)
            and all(c["verdict"] == "COUNTEREXAMPLE-CONFIRMED" for c in outside),
        "both_frozen_detectors_covered": {"cusum@5", "sr@520.886"} <= detectors,
        "at_least_five_theorem_supported_families": len(families) >= 5,
        "asymmetric_family_origin_not_a_fixed_point": any(
            row["stability_status"] == "FIXED-POINT-NOT-AT-ORIGIN"
            and row["family"].startswith("skewnormal")
            for row in mapping["rows"]
        ),
        "gaussian_consistency_with_closed_core": bool(consistency) and all(
            z <= reference["consistency_z_limit"] for z in consistency
        ),
        "certificate_all_checks_pass": certificate["all_checks_pass"],
        "lean_compiles_with_clean_axioms":
            lean["compiled"] and not lean["sorryAx"]
            and not lean["project_specific_scientific_axioms"]
            and lean["axiom_audit_declarations"] >= 19,
        "repository_verification_all_gates_pass": bool(
            verification and verification.get("all_gates_pass")
        ),
    }
    verification_status = (
        "COMPLETED" if verification else "NOT_RUN_TO_COMPLETION"
    )

    negative_claims = {
        "frozen_infinite_horizon_gains_interval_certified": False,
        "any_frozen_p1_p2_p3_artifact_modified": False,
        "novelty_verdict_claimed": False,
        "global_or_nonlinear_stability_claimed": False,
        "distribution_free_or_detector_universal_claim": False,
        "asymmetric_family_classified_at_the_origin": any(
            row["stability_status"] == "CLASSIFIED" and not row["origin_is_fixed_point"]
            for row in mapping["rows"]
        ),
    }

    all_pass = all(gates.values()) and not any(negative_claims.values())
    verdict = "CLOSED" if all_pass else "PARTIAL"

    payload = {
        "schema": "rebaseguard.p4-closure.v1",
        "campaign": manifest["campaign"],
        "verdict": verdict,
        "all_required_gates_pass": all_pass,
        "gates": gates,
        "repository_verification_status": verification_status,
        "repository_verification_note": (
            "results/verification.json is absent: the repository-wide "
            "verification run was stopped before completion. The gate is "
            "recorded as not passing, and no closure verdict is derived from "
            "an unfinished verification. Codex must run "
            "run_repository_verification.py independently."
            if verification is None else
            "results/verification.json present; gate evaluated from it."
        ),
        "negative_claims_asserted_false": negative_claims,
        "theorem_supported_families": sorted(families),
        "theorem_supported_cells": len(supported),
        "outside_assumption_cells": len(outside),
        "worst_theorem_supported_relative_discrepancy": max(
            (c["correspondence"]["relative_discrepancy"] for c in supported),
            default=None,
        ),
        "worst_theorem_supported_z": max(
            (c["correspondence"]["z"] for c in supported), default=None
        ),
        # Reported breakdown of any non-passing cells.  This does not gate
        # anything; it separates "the two routes disagree by more than the
        # accuracy limit while remaining statistically consistent" (a precision
        # limitation of Route B) from "the two routes are statistically
        # inconsistent" (a possible systematic effect).
        "non_passing_cell_breakdown": {
            "precision_limited_relative_gate_only": [
                {"layer": c["layer"], "detector": c["detector"],
                 "family": c["family"], "m": c["m"],
                 "relative": c["correspondence"]["relative_discrepancy"],
                 "z": c["correspondence"]["z"],
                 "route_b_relative_se": (
                     c["route_b"]["se"] / abs(c["route_b"]["mean"])
                     if c["route_b"]["mean"] else None)}
                for c in supported
                if c["verdict"] != "PASS"
                and c["correspondence"]["z"] <= protocol["gates"]["correspondence_z_limit"]
            ],
            "statistically_inconsistent": [
                {"layer": c["layer"], "detector": c["detector"],
                 "family": c["family"], "m": c["m"],
                 "relative": c["correspondence"]["relative_discrepancy"],
                 "z": c["correspondence"]["z"]}
                for c in supported
                if c["correspondence"]["z"] > protocol["gates"]["correspondence_z_limit"]
            ],
            "outside_assumption_cells_not_demonstrating_the_gate": [
                {"detector": c["detector"], "family": c["family"], "m": c["m"],
                 "relative": c["correspondence"]["relative_discrepancy"],
                 "z": c["correspondence"]["z"],
                 "route_a": c["route_a"], "route_b": c["route_b"],
                 "reading": (
                     "the preregistered counterexample gate expects a "
                     "deterministic defect; this family instead exhibits "
                     "non-convergence, with standard errors comparable to or "
                     "larger than the estimates, which is the failure mode "
                     "PROOF.md section 10 proves but not the one the gate "
                     "was written to detect")}
                for c in outside
                if c["verdict"] != "COUNTEREXAMPLE-CONFIRMED"
            ],
        },
        "gaussian_consistency_worst_z": max(consistency, default=None),
        "gaussian_consistency_worst_z_combined_error":
            max(consistency_combined, default=None),
        "gaussian_consistency_rows": consistency_rows,
        "repository_verification_status": verification_status,
        "repository_verification_note": (
            "The repository-wide regression, freeze-scoped and controlled-"
            "environment verification was not run to completion in this "
            "session. Its gate is recorded as not passing. Independent "
            "adjudication must run `run_repository_verification.py` before any "
            "closure claim; partial pre-checks of the individual suites are "
            "described in CLOSURE_REPORT.md and are not a substitute."
        ) if verification is None else "completed in this session",
        "gaussian_consistency_note": (
            "The gate statistic divides by Priority 4's standard error alone "
            "and so treats the closed Monte Carlo value as exact; it is not "
            "the right test for two Monte Carlo estimates. It was left "
            "unchanged after the data were seen. The combined-error statistic "
            "is the correct one and is reported beside it. Priority 4 does not "
            "update, replace or reinterpret any closed value."
        ),
        "scope": (
            "A conditional derivative and local-stability theorem for regular "
            "one-dimensional location families under the frozen two-sided CUSUM "
            "and two-chart Shiryaev-Roberts recursions, for every truncated "
            "window length m >= 1. Not distribution free, not detector "
            "universal, not global, not nonlinear, and not valid for moving "
            "support or for innovation laws without a first moment."
        ),
        "evidence_boundary": manifest["evidence_boundary"],
    }
    (RESULTS / "closure_decision.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({
        "verdict": verdict,
        "repository_verification_status": verification_status,
        "failed_gates": sorted(k for k, v in gates.items() if not v),
        "violated_negative_claims": sorted(k for k, v in negative_claims.items() if v),
        "worst_relative": payload["worst_theorem_supported_relative_discrepancy"],
        "worst_z": payload["worst_theorem_supported_z"],
    }, indent=2))


if __name__ == "__main__":
    main()
