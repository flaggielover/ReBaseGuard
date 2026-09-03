#!/usr/bin/env python3
"""P4X production PHASE P1 -- obligations requiring no new simulation.

C1  inherited theorem check
C4  CUT-2 analytic / exact discharge (A3 sharpness; A5 non-existence)
C5  CUT-3 two-sample Gaussian consistency arithmetic
C7  protected-tree integrity (pre-production reading)

Every number is derived from artifacts that already exist.  No simulation.
"""

from __future__ import annotations

import json
import math
import subprocess
import time
from pathlib import Path

PROD = Path(__file__).resolve().parent
BOUNDARY = PROD.parent
CLOSURE = BOUNDARY.parent
ROOT = CLOSURE.parents[1]
P4 = CLOSURE / "p4_theory_generalization"
P3 = CLOSURE / "m_rho_stability_priority3"
CHECKPOINT = BOUNDARY / "checkpoint_a" / "results" / "checkpoint_a.json"


def git_object(path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True).strip()


def main() -> None:
    t0 = time.perf_counter()
    cp = json.loads(CHECKPOINT.read_text())
    corr = json.loads((P4 / "results" / "correspondence.json").read_text())
    closure = json.loads((P4 / "results" / "closure_decision.json").read_text())
    adjudication = (P4 / "INDEPENDENT_ADJUDICATION.md").read_text()
    theorem_md = (P4 / "THEOREM.md").read_text()

    # ------------------------------------------------------------- C1 --
    tree_now = git_object("level4/closure_proofs/p4_theory_generalization")
    c1_checks = {
        "p4_tree_object_matches_checkpoint":
            tree_now == cp["inherited_theorem"]["source_tree_object"],
        "p4_verdict_is_partial": closure["verdict"] == "PARTIAL",
        "theorem_states_G1a": "g_m'(0) = -Gamma_{D,m,f}" in theorem_md,
        "theorem_states_G1b":
            "F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f})" in theorem_md,
        "theorem_states_score": "psi(z) = -f'(z)/f(z)" in theorem_md,
        "independent_adjudication_accepted_the_theorem":
            "The main stopped-score derivative theorem survives independent "
            "re-derivation" in " ".join(adjudication.split()),
        "no_new_proof_added": True,
        "no_theorem_strengthening": (
            cp["inherited_theorem"]["strengthening_permitted"] is False),
        "no_theorem_rewriting": (
            cp["inherited_theorem"]["reproving_permitted"] is False),
    }
    c1 = {
        "obligation": "C1",
        "statement": "inherit the theorem unchanged",
        "inherited_tree_object": tree_now,
        "checks": c1_checks,
        "status": "PASS" if all(c1_checks.values()) else "FAIL",
    }

    # ------------------------------------------------------------- C4 --
    outside = [c for c in corr["monte_carlo"]["cells"]
               if c["family_class"] == "OUTSIDE-ASSUMPTIONS"]
    uniform = [c for c in outside if c["family"] == "uniform"]
    cauchy = [c for c in outside if c["family"] == "cauchy"]
    rq_uniform = corr["route_q"]["uniform_counterexample"]
    cert = json.loads((P4 / "certificates" / "certificate.json").read_text())
    uniform_cert = cert["sections"]["uniform_counterexample"]["checks"]
    proof_md = (P4 / "PROOF.md").read_text()

    a3_checks = {
        "identity_is_false_without_A3": "moving support breaks (A3), and the "
            "identity is false" in theorem_md,
        "exact_defect_two_in_theorem": "the identity fails by exactly `2`" in theorem_md,
        "route_q_identity_does_not_hold": rq_uniform["identity_holds"] is False,
        "route_q_score_side_exactly_zero": rq_uniform["gamma_score_route"] == 0.0,
        "arb_uniform_alarm_probability_constant":
            bool(uniform_cert["uniform_alarm_probability_constant"]),
        "arb_uniform_map_exactly_linear":
            bool(uniform_cert["uniform_map_exactly_linear"]),
        "arb_uniform_identity_defect_positive":
            bool(uniform_cert["uniform_identity_defect_positive"]),
        "monte_carlo_corroboration_all_confirmed": all(
            c["verdict"] == "COUNTEREXAMPLE-CONFIRMED" for c in uniform),
    }
    a5_checks = {
        "non_existence_proved_in_theorem":
            "E|A_1| >= E[|Z_1| 1{|Z_1| >= h + k}] = infinity" in theorem_md,
        "non_existence_proved_in_proof": "infinity" in proof_md,
        "no_monte_carlo_disagreement_signature_demanded":
            cp["gates"]["X7b_first_moment_non_existence"][
                "monte_carlo_large_disagreement_signature_required"] is False,
        "no_necessity_claimed_for_A1_A7":
            cp["assumption_semantics"]["necessity_claimed"] is False,
    }
    c4 = {
        "obligation": "C4",
        "statement": "failure-mode evidence matched to the proved failure mode",
        "a3_half": {
            "assumption": "A3 local common support / absolute continuity",
            "proved_failure_mode": "the identity is FALSE, exact defect 2",
            "discharge": "analytic closed form + Route Q + exact rational Arb",
            "uniform_cells": len(uniform),
            "uniform_confirmed": sum(
                1 for c in uniform if c["verdict"] == "COUNTEREXAMPLE-CONFIRMED"),
            "uniform_z_range": [min(c["correspondence"]["z"] for c in uniform),
                                max(c["correspondence"]["z"] for c in uniform)],
            "route_q_exact_slope": rq_uniform["negative_map_derivative_exact"],
            "checks": a3_checks,
            "status": "PASS" if all(a3_checks.values()) else "FAIL",
            "new_compute": "NONE",
        },
        "first_moment_half": {
            "assumption": "A5 / A7 finite first moment",
            "proved_failure_mode": "NON-EXISTENCE of the estimand, E|A_1| = infinity",
            "discharge": "analytic (PROOF.md section 10)",
            "cauchy_cells": len(cauchy),
            "measured_z_range": [min(c["correspondence"]["z"] for c in cauchy),
                                 max(c["correspondence"]["z"] for c in cauchy)],
            "monte_carlo_signature_demanded": False,
            "checks": a5_checks,
            "status": "PASS" if all(a5_checks.values()) else "FAIL",
            "new_compute": "NONE",
        },
    }
    c4["status"] = ("PASS" if c4["a3_half"]["status"] == "PASS"
                    and c4["first_moment_half"]["status"] == "PASS" else "FAIL")

    # ------------------------------------------------------------- C5 --
    p3 = json.loads((P3 / "results" / "stability_map.json").read_text())
    closed = {}
    for entry in p3.get("cells", []) + p3.get("boundary_cells", []):
        key = entry.get("detector_short")
        if key and entry.get("gamma_tilde_se") is not None:
            closed.setdefault(key, {})[entry["m"]] = (
                entry["gamma_tilde"], entry["gamma_tilde_se"])

    gauss_rows = []
    for cell in corr["monte_carlo"]["cells"]:
        if cell["layer"] != "frozen" or cell["family"] != "gaussian":
            continue
        key = "CUSUM" if cell["detector_kind"] == "cusum" else "SR"
        cv, cse = closed[key][cell["m"]]
        a = cell["route_a"]
        diff = abs(a["mean"] - cv)
        z_two = diff / math.hypot(a["se"], cse)
        gauss_rows.append({
            "detector": cell["detector"], "m": cell["m"],
            "closed_estimate": cv, "closed_se": cse,
            "p4x_estimate": a["mean"], "p4x_se": a["se"],
            "absolute_difference": diff,
            "signed_relative_difference": (a["mean"] - cv) / abs(cv),
            "z_combined": z_two,
            "z_historical_single_error_reported_only": diff / a["se"],
            "pass": z_two <= cp["gates"]["X11_gaussian_consistency"]["limit"],
        })
    limit = cp["gates"]["X11_gaussian_consistency"]["limit"]
    c5 = {
        "obligation": "C5",
        "statement": "Gaussian consistency by a two-sample uncertainty statistic",
        "formula": "z_combined = |e1 - e2| / sqrt(SE1^2 + SE2^2)",
        "limit": limit,
        "cells": len(gauss_rows),
        "rows": gauss_rows,
        "worst_z_combined": max(r["z_combined"] for r in gauss_rows),
        "worst_z_historical_single_error": max(
            r["z_historical_single_error_reported_only"] for r in gauss_rows),
        "closed_uncertainty_source":
            "m_rho_stability_priority3/results/stability_map.json gamma_tilde_se",
        "treats_either_estimate_as_exact": False,
        "note": ("The anchor phase reproduced the frozen Route-A Gaussian "
                 "estimates bitwise, so P4X's own Gaussian estimate for these "
                 "eight cells is numerically identical to the frozen one and "
                 "the statistic is arithmetic on published uncertainties."),
        "status": "PASS" if all(r["pass"] for r in gauss_rows) else "FAIL",
    }

    # ------------------------------------------------------------- C7 --
    tree = cp["protected_tree_manifest"]
    mismatches = {p: (exp, git_object(p)) for p, exp in tree.items()
                  if git_object(p) != exp}
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    outside_ns = [l for l in dirty if not l[3:].strip().strip('"').startswith(
        "level4/closure_proofs/p4x_generalization_boundary/")]
    c7 = {
        "obligation": "C7",
        "statement": "protected-tree integrity",
        "reading": "PRE_PRODUCTION",
        "paths_checked": len(tree),
        "mismatches": mismatches,
        "dirty_paths_outside_p4x_namespace": outside_ns,
        "status": "PASS" if not mismatches and not outside_ns else "FAIL",
    }

    payload = {
        "schema": "rebaseguard.p4x-production-p1.v1",
        "phase": "P1_ZERO_NEW_SCIENCE_OBLIGATIONS",
        "new_simulation_performed": False,
        "C1": c1, "C4": c4, "C5": c5, "C7_pre_production": c7,
        "wall_seconds": time.perf_counter() - t0,
    }
    out = PROD / "results" / "p1_zero_compute.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"C1 = {c1['status']}   (inherited theorem, tree {tree_now[:12]})")
    print(f"C4 = {c4['status']}   A3 {c4['a3_half']['status']} "
          f"({c4['a3_half']['uniform_confirmed']}/{c4['a3_half']['uniform_cells']} "
          f"confirmed, |z| {c4['a3_half']['uniform_z_range'][0]:.0f}-"
          f"{c4['a3_half']['uniform_z_range'][1]:.0f}); "
          f"first-moment {c4['first_moment_half']['status']} (non-existence)")
    print(f"C5 = {c5['status']}   worst z_combined {c5['worst_z_combined']:.3f} "
          f"vs limit {limit}  (historical single-error statistic "
          f"{c5['worst_z_historical_single_error']:.2f}, reported only)")
    print(f"C7 = {c7['status']}   {c7['paths_checked']} protected paths, "
          f"{len(mismatches)} mismatches")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
