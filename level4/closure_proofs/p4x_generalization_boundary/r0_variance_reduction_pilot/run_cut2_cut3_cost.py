#!/usr/bin/env python3
"""CUT-2 and CUT-3 cost determination for P4X R0.

Neither cut needs new simulation.  This script demonstrates that by deriving
both objects from artifacts that already exist in the repository, and prices
the optional confirmatory diagnostics from measured ARLs.

Reads frozen Priority-3 and Priority-4 artifacts read-only.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

PILOT = Path(__file__).resolve().parent
CLOSURE = PILOT.parents[1]
P4 = CLOSURE / "p4_theory_generalization"
P3 = CLOSURE / "m_rho_stability_priority3"


def main() -> None:
    p3 = json.loads((P3 / "results" / "stability_map.json").read_text())
    p4 = json.loads((P4 / "results" / "correspondence.json").read_text())
    protocol = json.loads((P4 / "configs" / "P4_PROTOCOL.json").read_text())

    # ---- CUT-3: the two-sample statistic, from published artifacts only ----
    closed: dict[str, dict[int, tuple[float, float]]] = {}
    for entry in p3.get("cells", []) + p3.get("boundary_cells", []):
        key = entry.get("detector_short")
        if key and entry.get("gamma_tilde_se") is not None:
            closed.setdefault(key, {})[entry["m"]] = (
                entry["gamma_tilde"], entry["gamma_tilde_se"])

    rows = []
    for cell in p4["monte_carlo"]["cells"]:
        if cell["layer"] != "frozen" or cell["family"] != "gaussian":
            continue
        key = "CUSUM" if cell["detector_kind"] == "cusum" else "SR"
        cv, cse = closed[key][cell["m"]]
        a = cell["route_a"]
        diff = abs(a["mean"] - cv)
        rows.append({
            "detector": cell["detector"], "m": cell["m"],
            "closed_value": cv, "closed_se": cse,
            "p4_value": a["mean"], "p4_se": a["se"],
            "signed_relative_difference": (a["mean"] - cv) / abs(cv),
            "z_single_error_historical_gate": diff / a["se"],
            "z_two_sample_correct": diff / math.hypot(a["se"], cse),
        })
    limit = protocol["frozen_reference_values"]["consistency_z_limit"]
    cut3 = {
        "requires_new_simulation": False,
        "reason": ("both standard errors are already published: the closed "
                   "Gaussian gains carry gamma_tilde_se in the frozen "
                   "Priority-3 stability map, and Priority 4 publishes its own "
                   "route_a standard error for every cell"),
        "rows": rows,
        "limit": limit,
        "worst_z_historical_gate": max(r["z_single_error_historical_gate"] for r in rows),
        "worst_z_two_sample": max(r["z_two_sample_correct"] for r in rows),
        "all_pass_two_sample": all(
            r["z_two_sample_correct"] <= limit for r in rows),
        "marginal_production_cost": (
            "zero: the Gaussian family is already one of the six "
            "theorem-supported families in the production grid, so P4X "
            "re-estimates these eight cells as a by-product and the statistic "
            "is arithmetic on numbers it already has"),
        "classification": "NEGLIGIBLE",
    }

    # ---- CUT-2: failure-mode semantics, and the price of confirming them ----
    outside = [c for c in p4["monte_carlo"]["cells"]
               if c["family_class"] == "OUTSIDE-ASSUMPTIONS"]
    by_family: dict[str, list[dict]] = {}
    for cell in outside:
        by_family.setdefault(cell["family"], []).append(cell)

    uniform = by_family["uniform"]
    cauchy = by_family["cauchy"]
    route_q = p4["route_q"]["uniform_counterexample"]

    # cost of an optional confirmatory Cauchy divergence diagnostic, priced
    # from the measured in-control ARLs: Cauchy alarms almost immediately
    cauchy_arls = {c["detector"]: c["arl"]["mean"] for c in cauchy if c["m"] == 1}
    worst_arl = max(cauchy_arls.values())
    ladder_paths = 4 * 2_000_000          # four rungs of 2M paths
    # measured in results/sizing.json: ~6 s per 1e6 paths at mean tau ~13
    seconds_per_1e6_at_tau13 = 6.0
    projected = (ladder_paths / 1e6) * seconds_per_1e6_at_tau13 * (worst_arl / 13.0)

    cut2 = {
        "requires_new_simulation": False,
        "a3_half": {
            "assumption": "A3 local common support / absolute continuity",
            "proved_failure_mode": "the identity is FALSE; exact defect 2",
            "analytic_evidence": "PROOF.md section 9 (closed form)",
            "certified_evidence": ("Arb: alarm probability constant in e, map "
                                   "exactly linear with slope -2, defect "
                                   "exactly 2, exact rational arithmetic"),
            "route_q_evidence": route_q,
            "monte_carlo_evidence": {
                "cells": len(uniform),
                "confirmed": sum(1 for c in uniform
                                 if c["verdict"] == "COUNTEREXAMPLE-CONFIRMED"),
                "relative": sorted({round(c["correspondence"][
                    "relative_discrepancy"], 6) for c in uniform}),
                "z_range": [min(c["correspondence"]["z"] for c in uniform),
                            max(c["correspondence"]["z"] for c in uniform)],
            },
            "load_bearing": True,
            "already_satisfied": True,
            "new_compute_required": "NONE",
        },
        "first_moment_half": {
            "assumption": "A5 / A7 finite first moment",
            "proved_failure_mode": (
                "NON-EXISTENCE of the estimand: E|A_1| = infinity under the "
                "frozen CUSUM, so g_m(e) is undefined and no identity is "
                "asserted to be true or false"),
            "analytic_evidence": "PROOF.md section 10 (closed form)",
            "historical_gate_demanded": {
                "relative": protocol["gates"]["counterexample_min_relative"],
                "z": protocol["gates"]["counterexample_min_z"],
                "signature": "sharp deterministic two-route defect",
            },
            "signature_reachable": False,
            "why_unreachable": (
                "a two-sample z statistic formed from two divergent Monte "
                "Carlo estimators cannot grow: the standard errors grow with "
                "the estimates.  Measured |z| across all 16 Cauchy cells is "
                "0.027 to 1.62, against a gate demanding >= 10"),
            "measured_z_range": [min(c["correspondence"]["z"] for c in cauchy),
                                 max(c["correspondence"]["z"] for c in cauchy)],
            "load_bearing": False,
            "new_compute_required": "NONE",
            "optional_confirmatory_diagnostic": {
                "design": ("a truncated-moment ladder E[|A_1| 1{|A_1|<=K}] "
                           "growing without bound in K, and a standard-error "
                           "ladder failing to shrink at n^{-1/2}"),
                "cauchy_arls_m1": cauchy_arls,
                "projected_paths": ladder_paths,
                "projected_cpu_seconds": projected,
                "projected_cpu_hours": projected / 3600.0,
                "status": "OPTIONAL, not load-bearing",
            },
        },
        "classification": "NONE",
        "note": ("The theorem's logical form is assumptions => identity.  "
                 "Neither A3 nor the first moment needs an empirical failure "
                 "signature for the theorem to hold; A3's sharpness is a "
                 "separate claim that is already proved AND certified, and the "
                 "first-moment boundary is a non-existence claim that a "
                 "two-route discrepancy test cannot express."),
    }

    payload = {
        "schema": "rebaseguard.p4x-r0-cut23.v1",
        "classification": "PRE_FREEZE_COST_AND_PRECISION_PILOT",
        "binding": False,
        "new_simulation_performed": False,
        "cut2": cut2,
        "cut3": cut3,
    }
    out = PILOT / "results" / "cut2_cut3_cost.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"CUT-3  worst z (historical gate) = "
          f"{cut3['worst_z_historical_gate']:.2f}")
    print(f"CUT-3  worst z (two-sample)      = "
          f"{cut3['worst_z_two_sample']:.2f}  limit {limit}  "
          f"all_pass={cut3['all_pass_two_sample']}")
    print(f"CUT-3  classification            = {cut3['classification']}")
    print(f"CUT-2  A3 half                   = already satisfied, "
          f"proved + Arb-certified")
    print(f"CUT-2  first-moment half         = non-existence claim; measured "
          f"|z| {cut2['first_moment_half']['measured_z_range'][0]:.3f}"
          f"-{cut2['first_moment_half']['measured_z_range'][1]:.3f} vs gate >= 10")
    print(f"CUT-2  classification            = {cut2['classification']}  "
          f"(optional diagnostic "
          f"{cut2['first_moment_half']['optional_confirmatory_diagnostic']['projected_cpu_hours']:.3f} CPU-h)")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
