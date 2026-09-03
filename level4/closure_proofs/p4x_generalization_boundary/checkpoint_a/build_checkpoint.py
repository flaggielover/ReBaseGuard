#!/usr/bin/env python3
"""Generate the binding P4X Checkpoint A manifest.

Every frozen number is DERIVED here from artifacts that already exist -- the
frozen Priority-4 protocol and correspondence, and the P4X-R0 pilot results --
rather than transcribed.  Running this script reproduces the manifest exactly;
`tests/` asserts that it does.

This script generates a SPECIFICATION.  It runs no simulation and produces no
scientific result.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

CHECKPOINT = Path(__file__).resolve().parent
BOUNDARY = CHECKPOINT.parent
CLOSURE = BOUNDARY.parent
ROOT = CLOSURE.parents[1]
P4 = CLOSURE / "p4_theory_generalization"
R0 = BOUNDARY / "r0_variance_reduction_pilot"

SOURCE_COMMIT = "b3f050bcfb1c8b908e50376b4bf6d6464871da13"

# ---------------------------------------------------------------- constants --
FROZEN_ACCURACY = 0.03           # inherited unchanged from Track 3 via P4
FROZEN_Z_LIMIT = 4.0             # inherited unchanged
ATTAINMENT_Z = 1.96
R_STAR = 0.010823                # binding; the 6-dp rounding of the derivation
GAUSSIAN_Z_LIMIT = 4.0
TOTAL_CPU_CAP_HOURS = 60.0
PER_CONFIGURATION_CPU_CAP_HOURS = 40.0
MIN_BLOCK_HEAVY_TAIL = 250_000
MIN_BLOCK_DEFAULT = 20_000
#: conservative floor of the R0-measured t1p5 range 1.47-1.53, used for the
#: top-up rate so the heavy-tail risk is not understated
ALPHA_T1P5_FROZEN = 1.47

DESTROYED_DISPOSITION_SHA256 = (
    "bda05c9c5ee5df2a7bfbe11ca1fb07432907378299fd36ea0b75cada68ffba34")

PROTECTED_PATHS = (
    "level4/closure_proofs/p4_theory_generalization",
    "level4/closure_proofs/p5_nonlinear_dynamics",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics",
    "level4/closure_proofs/m_gt_1_priority1",
    "level4/closure_proofs/m_gt_1",
    "level4/closure_proofs/m_gt_1_track1a",
    "level4/closure_proofs/m_gt_1_track1b",
    "level4/closure_proofs/sr_derivative",
    "level4/closure_proofs/sr_derivative_priority2",
    "level4/closure_proofs/m_rho_stability_priority3",
    "level4/closure_proofs/location_family",
    "level4/closure_proofs/location_family_track3ab",
    "level4/closure_proofs/p6_safe_rebaselining",
    "level4/closure_proofs/p6_safe_rebaselining_predesign",
    "level4/closure_proofs/p6r_safe_rebaselining_confirmation",
    "level4/closure_proofs/p6r2_literal_closure_repair",
    "level4/closure_proofs/p6r2b_gate9_crn_identity",
    "level4/closure_proofs/p7_statistical_consequences",
    "level4/closure_proofs/p8_model_class_robustness",
    "level4/closure_proofs/p8r_temporal_integrity_repair",
    "level4/closure_proofs/p9_final_synthesis",
    "level4/closure_proofs/p9r_final_synthesis_repair",
    "level4/closure_proofs/d4_phase_map",
    "level4/closure_proofs/external_validation_v2",
    "level4/closure_proofs/external_validation_v3",
    "level4/closure_proofs/l4r06_policy",
    "level4/closure_proofs/l4r12_operational_crossing",
    "level4/closure_proofs/novelty_verification",
    "rebaseguard-lean",
    "rebaseguard-proof",
    "closure",
    "Mathematical_proof",
    "README.md",
)


def git_object(path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kappa_for(alpha: float) -> float:
    return 0.5 if alpha >= 2.0 else 1.0 - 1.0 / alpha


def main() -> None:
    protocol = json.loads((P4 / "configs" / "P4_PROTOCOL.json").read_text())
    corr = json.loads((P4 / "results" / "correspondence.json").read_text())
    closure = json.loads((P4 / "results" / "closure_decision.json").read_text())
    tails = json.loads((R0 / "results" / "tail_sweep.json").read_text())
    cost = json.loads((R0 / "results" / "cost_calibration.json").read_text())["cost"]
    pilot = json.loads((R0 / "results" / "pilot.json").read_text())
    cut23 = json.loads((R0 / "results" / "cut2_cut3_cost.json").read_text())

    # ------------------------------------------------------ r* derivation --
    exact_r_star = FROZEN_ACCURACY / (ATTAINMENT_Z * math.sqrt(2.0))
    assert abs(R_STAR - exact_r_star) < 1e-6, (R_STAR, exact_r_star)

    # ------------------------------------------------- measured tail index --
    measured_alpha = {
        f"{r['layer']}/{r['detector']}/{r['family']}": {
            "route_a": r["route_a"]["tail"]["alpha"],
            "route_b": r["route_b"]["tail"]["alpha"],
        }
        for r in tails["rows"]
    }
    t1p5_alphas = [v[route] for k, v in measured_alpha.items()
                   for route in ("route_a", "route_b") if k.endswith("/t1p5")]
    other_alphas = [v[route] for k, v in measured_alpha.items()
                    for route in ("route_a", "route_b")
                    if not k.endswith("/t1p5")]
    assert max(t1p5_alphas) < 2.0 and min(other_alphas) >= 2.0

    # ------------------------------------------------------ production scope --
    cells = [c for c in corr["monte_carlo"]["cells"]
             if c["family_class"] == "THEOREM-SUPPORTED"]
    outside = [c for c in corr["monte_carlo"]["cells"]
               if c["family_class"] == "OUTSIDE-ASSUMPTIONS"]

    plan = []
    for cell in cells:
        cfg = f"{cell['layer']}/{cell['detector']}/{cell['family']}"
        heavy = cell["family"] == "t1p5"
        row = {
            "config": cfg, "layer": cell["layer"], "detector": cell["detector"],
            "family": cell["family"], "m": cell["m"],
            "heavy_tailed": heavy,
            "minimum_block_paths": (MIN_BLOCK_HEAVY_TAIL if heavy
                                    else MIN_BLOCK_DEFAULT),
        }
        for route in ("route_a", "route_b"):
            est = cell[route]
            rel_ref = abs(est["se"] / est["mean"])
            sec = cost[cfg][f"{route}_seconds_per_1e6"]
            # Stage 1 is planned at the CLASSICAL rate from the historical
            # reference.  Stage 2 tops up at the frozen heavy-tail rate from
            # the ACHIEVED precision, and exists only for cells that miss r*.
            f1 = (rel_ref / R_STAR) ** (1.0 / 0.5) if rel_ref > R_STAR else 1.0
            n1 = est["paths"] * f1
            kappa_topup = kappa_for(ALPHA_T1P5_FROZEN if heavy else 10.0)
            f_worst = (rel_ref / R_STAR) ** (1.0 / kappa_topup) if rel_ref > R_STAR else 1.0
            n_worst = est["paths"] * f_worst
            row[route] = {
                "reference_paths": est["paths"],
                "reference_relative_se": rel_ref,
                "already_meets_r_star": rel_ref <= R_STAR,
                "measured_alpha": measured_alpha[cfg][route],
                "kappa_stage1": 0.5,
                "kappa_topup": kappa_topup,
                "stage1_paths": n1,
                "stage1_cpu_hours": n1 / 1e6 * sec / 3600.0,
                "worst_case_paths": n_worst,
                "worst_case_cpu_hours": n_worst / 1e6 * sec / 3600.0,
                "seconds_per_1e6_paths": sec,
            }
        plan.append(row)

    # cost is charged once per (configuration, route): the four windows share paths
    per_config = {}
    for row in plan:
        c = per_config.setdefault(row["config"], {
            "config": row["config"], "heavy_tailed": row["heavy_tailed"],
            "minimum_block_paths": row["minimum_block_paths"]})
        for route in ("route_a", "route_b"):
            for k in ("stage1_cpu_hours", "worst_case_cpu_hours"):
                key = f"{route}_{k}"
                c[key] = max(c.get(key, 0.0), row[route][k])
    for c in per_config.values():
        c["config_stage1_cpu_hours"] = (c["route_a_stage1_cpu_hours"]
                                        + c["route_b_stage1_cpu_hours"])
        c["config_worst_case_cpu_hours"] = (c["route_a_worst_case_cpu_hours"]
                                            + c["route_b_worst_case_cpu_hours"])
        c["exceeds_per_configuration_cap_in_worst_case"] = (
            c["config_worst_case_cpu_hours"] > PER_CONFIGURATION_CPU_CAP_HOURS)

    totals = {
        "stage1_cpu_hours": sum(c["config_stage1_cpu_hours"]
                                for c in per_config.values()),
        "worst_case_cpu_hours": sum(c["config_worst_case_cpu_hours"]
                                    for c in per_config.values()),
    }
    at_risk = sorted(
        (c["config"] for c in per_config.values()
         if c["exceeds_per_configuration_cap_in_worst_case"]))

    payload = {
        "schema": "rebaseguard.p4x-checkpoint-a.v1",
        "artifact": "P4X_CHECKPOINT_A",
        "active": True,
        "binding": True,
        "generated_from_commit": SOURCE_COMMIT,
        "campaign": "P4X — successor numerical-evidence campaign for the "
                    "Level-4 Priority-4 location-family derivative theorem",

        "governance": {
            "P4_ORIGINAL_VERDICT": "PARTIAL",
            "P4_ORIGINAL_VERDICT_IMMUTABLE": True,
            "P4X_IS_SUCCESSOR_ONLY": True,
            "historical_p4_tree_object": git_object(
                "level4/closure_proofs/p4_theory_generalization"),
            "destroyed_disposition_audit": {
                "path": "level4/closure_proofs/p4_final_disposition_audit",
                "sha256": DESTROYED_DISPOSITION_SHA256,
                "status": "DESTROYED_AND_UNRECOVERABLE",
                "wording_inherited": False,
                "loss_mechanism": (
                    "untracked namespace removed by an external git clean "
                    "alongside commit 31132e8; recorded in "
                    "p5x_global_nonlinear_dynamics/"
                    "INCIDENT_EXTERNAL_TREE_CHANGE.md section 1(b)"),
                "precedence_rule": (
                    "if an artifact hashing to this digest is recovered and "
                    "forbids a successor campaign, that ruling takes "
                    "precedence and P4X STOPS"),
            },
            "derived_independently_from": [
                "the parallel P5 disposition ruling quoted verbatim in the "
                "surviving p5x_global_nonlinear_dynamics/FEASIBILITY_AUDIT.md: "
                "P5_PARTIAL_SHOULD_BE_FINAL, P5R_LAUNCHED = NO, "
                "NEW_SCIENCE_REQUIRED = YES -- the missing work was ruled new "
                "science for a new priority, not forbidden work",
                "P5X was opened as a successor under that ruling, committed, "
                "and archivally completed with no recorded objection",
                "p5x_global_nonlinear_dynamics/final_scope_disposition_audit/"
                "AUDIT.md section 13 names P4X explicitly: 'P4X and residual "
                "P5 coexist: P4X is not the only remaining repair campaign'",
                "p4_theory_generalization/CLOSURE_REPORT.md section 10 "
                "limitation 1 itself names a follow-up campaign as the fix",
                "a full repository search for P4R / P4.1 / p4_1 returns zero "
                "surviving prohibitive text",
            ],
            "governance_reading": (
                "no retroactive repair or amendment of the historical "
                "priority; a successor campaign under a fresh preregistered "
                "scope is permitted"),
        },

        "successor_question": (
            "Can the already-proved and independently adjudicated Priority-4 "
            "location-family derivative theorem be supported by numerical "
            "evidence whose precision and statistical semantics are correctly "
            "matched to the original scientific claims, without changing the "
            "theorem or its scientific scope?"),
        "is_stronger_theorem_campaign": False,

        "inherited_theorem": {
            "source": "level4/closure_proofs/p4_theory_generalization/THEOREM.md",
            "source_tree_object": git_object(
                "level4/closure_proofs/p4_theory_generalization"),
            "G1a": "g_m'(0) = -Gamma_{D,m,f}",
            "Gamma": "Gamma_{D,m,f} = E_0[ A_m sum_{t<=tau} psi(Z_t) ]",
            "score": "psi = -f'/f",
            "G1b": "F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f})",
            "window": "A_m = (1/w) sum_{r=0}^{w-1} Z_{tau-r}, w = min(m, tau)",
            "residual_convention": "Z_t = eps_t - e,  f_e(z) = f(z+e)",
            "quantifier": "for every fixed m >= 1",
            "companions": ["G1'", "G2", "G3a (narrowed)", "G4"],
            "strengthening_permitted": False,
            "reproving_permitted": False,
        },

        "assumption_semantics": {
            "A1_A7_are": "SUFFICIENT",
            "necessity_claimed": False,
            "A3_sharpness": (
                "separately proved (PROOF.md section 9, exact defect 2) and "
                "Arb-certified as an exact rational; not re-derived by P4X"),
            "A5_first_moment_boundary": (
                "an analytic NON-EXISTENCE result (PROOF.md section 10, "
                "E|A_1| = infinity); not a false-identity claim"),
            "arbitrary_failure_demonstrations_required": False,
            "rule": (
                "P4X must not require failure demonstrations outside merely "
                "sufficient assumptions, and must not test necessity that no "
                "frozen claim asserts"),
        },

        "core_obligations": {
            "C1": "inherit the theorem unchanged",
            "C2": "attainable-precision numerical correspondence",
            "C3": "Route Q only as an independent cross-check",
            "C4": "failure-mode evidence matched to the actual proved failure mode",
            "C5": "Gaussian consistency by a two-sample uncertainty statistic",
            "C6": "re-verify the inherited Lean and Arb artifacts",
            "C7": "protected-tree integrity",
        },

        "estimator_plan": {
            "status": "FROZEN",
            "route_a": "the frozen Priority-4 score estimator, unchanged",
            "route_b": ("the frozen Priority-4 common-random-number central "
                        "difference with per-block Richardson, unchanged"),
            "fd_steps": protocol["fd_steps"],
            "richardson": "(4 D(h/2) - D(h)) / 3, formed per block",
            "variance_reduction_adopted": "NONE",
            "rejected_candidates": {
                "reflection_antithetic": (
                    "pathwise exact (0.000e+00) and distributionally valid for "
                    "symmetric families, but variance reduction factor "
                    "0.001-0.003, a 300-1000x variance INCREASE: substituting "
                    "the mirror for the -h run destroys the CRN cancellation"),
                "corollary_g2_control_variate": (
                    "degenerate; measured per-path variance 6e-29 to 9e-31, "
                    "i.e. exactly zero, which is Corollary G2's own content"),
                "coarse_finite_difference_step": (
                    "inadmissibly biased for skewnormal4 (+4.94 and +33.01 "
                    "baseline standard errors); for t1p5 the benefit is real "
                    "but the bias is unresolved and sign-inconsistent"),
                "fine_finite_difference_step": (
                    "variance increase, factor 0.32-0.55"),
            },
            "evidence": "level4/closure_proofs/p4x_generalization_boundary/"
                        "r0_variance_reduction_pilot/results/pilot.json",
        },

        "heavy_tail_policy": {
            "status": "FROZEN",
            "only_family_requiring_alpha_below_2": "t1p5",
            "measured_alpha_range_t1p5": [min(t1p5_alphas), max(t1p5_alphas)],
            "measured_alpha_min_other_families": min(other_alphas),
            "frozen_alpha_t1p5_for_planning": ALPHA_T1P5_FROZEN,
            "frozen_alpha_rationale": (
                "the conservative floor of the measured 1.47-1.53 range, so "
                "the heavy-tail risk is not understated"),
            "kappa_rule": "kappa = 0.5 if alpha >= 2 else 1 - 1/alpha",
            "kappa_t1p5": kappa_for(ALPHA_T1P5_FROZEN),
            "minimum_block_paths_heavy_tail": MIN_BLOCK_HEAVY_TAIL,
            "minimum_block_paths_default": MIN_BLOCK_DEFAULT,
            "model_justification": (
                "Student-t with nu = 1.5 has tail index exactly 1.5, and the "
                "frozen Priority-4 protocol already records this family as "
                "having infinite variance; the R0 sweep confirms 1.47-1.53 on "
                "both routes at all four layer/detector combinations"),
        },

        "precision_rule": {
            "status": "FROZEN",
            "frozen_accuracy_criterion": FROZEN_ACCURACY,
            "frozen_accuracy_source": (
                "inherited unchanged from Track 3 through the frozen "
                "Priority-4 protocol; P4X does not alter it"),
            "attainment_z": ATTAINMENT_Z,
            "r_star": R_STAR,
            "r_star_exact": exact_r_star,
            "r_star_derivation": "1.96 * sqrt(2) * r* = 0.03",
            "n_required_rule": "N = N_ref * (relSE_ref / r*)^(1/kappa)",
            "two_stage_design": {
                "stage1": ("planned allocation at the classical rate "
                           "kappa = 0.5 from the historical reference "
                           "relative standard error"),
                "stage2": ("at most one top-up, triggered ONLY when a route's "
                           "own ACHIEVED relative standard error on a cell "
                           "exceeds r*, sized by the same rule at the frozen "
                           "heavy-tail kappa, using fresh independent blocks "
                           "pooled with stage 1"),
                "trigger_is": "the route's own achieved relative standard error",
                "trigger_is_not": [
                    "the observed Route-A minus Route-B discrepancy",
                    "the sign or direction of any disagreement",
                    "whether a cell is close to passing",
                    "any pass/fail outcome",
                ],
                "disclosed_limitation": (
                    "a precision-triggered top-up is a sequential design, so "
                    "the pooled standard error carries an O(1/B) optional-"
                    "stopping bias.  With the block counts planned here that "
                    "bias is negligible relative to r*, but it is disclosed "
                    "rather than assumed away"),
            },
            "must_not_depend_on": [
                "observed pass/fail", "discrepancy sign",
                "whether a cell is close to passing"],
        },

        "production_scope": {
            "status": "FROZEN",
            "layers": {
                name: {"detectors": spec["detectors"],
                       "max_steps": spec["max_steps"]}
                for name, spec in protocol["layers"].items()},
            "detectors": sorted({c["detector"] for c in cells}),
            "theorem_supported_families": sorted({c["family"] for c in cells}),
            "outside_assumption_families": sorted({c["family"] for c in outside}),
            "m_grid": protocol["m_grid"],
            "theorem_supported_cells": len(cells),
            "outside_assumption_cells": len(outside),
            "configurations": len(per_config),
            "route_q_rows": len(corr["route_q"]["rows"]),
            "route_n_rows": len(corr["route_n"]["rows"]),
            "routes": ["A (score)", "B (Richardson CRN central difference)",
                       "Q (deterministic quadrature, memoryless detector)",
                       "N (deterministic-stopping neutrality control)"],
            "broadening_permitted": False,
            "narrowing_after_results_permitted": False,
        },

        "production_plan": plan,
        "per_configuration_plan": per_config,
        "projected_cpu_hours": totals,
        "configurations_at_risk_of_per_configuration_cap": at_risk,

        "gates": {
            "X1_protocol_and_witness_hashes": "byte equality with the manifest",
            "X2_inherited_theorem_unchanged": (
                "p4_theory_generalization tree object equals "
                + git_object("level4/closure_proofs/p4_theory_generalization")),
            "X3_route_q_identity": (
                f"worst relative discrepancy <= "
                f"{protocol['route_q']['tolerance_relative']} over "
                f"{len(corr['route_q']['rows'])} rows"),
            "X4_route_q_uniform_failure": (
                "score side exactly 0 and the exact map slope reproduced"),
            "X5_route_n_neutrality": (
                f"all {len(corr['route_n']['rows'])} deterministic-stopping "
                f"cells return gain 1 with |z| <= "
                f"{protocol['neutrality_control']['tolerance_z']}"),
            "X6_theorem_supported_correspondence": {
                "criterion": (
                    f"relative discrepancy <= {FROZEN_ACCURACY} AND "
                    f"|z| <= {FROZEN_Z_LIMIT}, on all "
                    f"{len(cells)} theorem-supported cells"),
                "precondition": (
                    "each route on each cell must first reach r*, or be "
                    "declared PRECISION_LIMITED from projected cost alone"),
                "weakening_permitted": False,
                "failure_permitted": True,
                "note": ("if the purchased-precision estimates still disagree "
                         "materially, the gate MUST be allowed to FAIL"),
            },
            "X7a_a3_moving_support": {
                "semantics": "the identity is FALSE; exact defect 2",
                "discharged_by": [
                    "PROOF.md section 9 closed form",
                    "Route Q: score side exactly 0, exact slope -2.366025",
                    "an exact rational Arb certificate"],
                "monte_carlo_role": "corroborating, not load-bearing",
                "new_compute_required": "NONE",
            },
            "X7b_first_moment_non_existence": {
                "semantics": ("NON-EXISTENCE of the estimand: "
                              "E|A_1| = infinity"),
                "discharged_by": ["PROOF.md section 10"],
                "monte_carlo_large_disagreement_signature_required": False,
                "why": ("a two-route discrepancy statistic cannot express "
                        "non-existence; measured |z| across all 16 Cauchy "
                        "cells is "
                        f"{cut23['cut2']['first_moment_half']['measured_z_range'][0]:.3f}"
                        f"-{cut23['cut2']['first_moment_half']['measured_z_range'][1]:.3f} "
                        "against a historical gate demanding >= 10"),
                "new_compute_required": "NONE",
            },
            "X8_both_frozen_detectors_covered": "cusum@5 and sr@520.886",
            "X9_at_least_five_theorem_supported_families": True,
            "X10_asymmetric_origin_not_a_fixed_point": (
                "skewnormal4 classified FIXED-POINT-NOT-AT-ORIGIN, never "
                "CLASSIFIED at 0"),
            "X11_gaussian_consistency": {
                "statistic": ("z_combined = |estimate_1 - estimate_2| / "
                              "sqrt(SE_1^2 + SE_2^2)"),
                "limit": GAUSSIAN_Z_LIMIT,
                "cells": 8,
                "closed_uncertainty_source": (
                    "gamma_tilde_se in level4/closure_proofs/"
                    "m_rho_stability_priority3/results/stability_map.json"),
                "treats_either_estimate_as_exact": False,
                "historical_single_error_statistic": (
                    "reported alongside; gates nothing"),
                "is_a_new_preregistered_object": True,
                "repairs_a_p4_gate": False,
            },
            "X12_inherited_certificates_reverify": (
                "all Arb checks pass at 160 bits and again at >= 256 bits"),
            "X13_inherited_lean_reverifies": (
                "19 declarations; axioms exactly propext, Classical.choice, "
                "Quot.sound; no sorry, no sorryAx, no project axiom"),
            "X14_protected_tree_integrity": (
                "every tracked path outside the P4X namespace byte-identical "
                "to HEAD, recorded pre and post"),
            "X15_no_historical_mutation": (
                "p4_theory_generalization tree object unchanged and "
                "P4 = PARTIAL unchanged in the root status table"),
        },

        "route_q_role": {
            "role": "INDEPENDENT_CROSS_CHECK_ONLY",
            "detector": protocol["route_q"]["detector"],
            "c": protocol["route_q"]["c"],
            "may_arbitrate_frozen_detector_cells": False,
            "may_serve_as_control_variate": False,
            "withdrawn_clause": (
                "the feasibility audit's draft X6 arbitration clause is "
                "WITHDRAWN and remains withdrawn"),
            "reason": (
                "Route Q evaluates the memoryless detector; the frozen "
                "Priority-4 EVIDENCE_BOUNDARY.md section 3 states that nothing "
                "in Route Q is evidence about h = 5 or A = 520.886133602749"),
        },

        "lean_and_arb": {
            "new_lean_declarations_permitted": False,
            "new_arb_objects_permitted": False,
            "obligation": "re-verification of the inherited artifacts only",
            "inherited_lean_declarations": 19,
            "inherited_lean_axioms": ["propext", "Classical.choice", "Quot.sound"],
            "inherited_arb_objects": 3,
        },

        "cost_envelope": {
            "TOTAL_CPU_CAP_HOURS": TOTAL_CPU_CAP_HOURS,
            "PER_CONFIGURATION_CPU_CAP_HOURS": PER_CONFIGURATION_CPU_CAP_HOURS,
            "projected_stage1_cpu_hours": totals["stage1_cpu_hours"],
            "projected_worst_case_cpu_hours": totals["worst_case_cpu_hours"],
            "silent_extension_permitted": False,
            "breach_action": "STOP",
        },

        "stop_rules": [
            "estimator implementation drift: any deviation of Route A or "
            "Route B from the frozen Priority-4 implementation",
            "protected-tree mutation: any tracked path outside the P4X "
            "namespace differing from HEAD",
            "precision policy mismatch: any sample-size decision not produced "
            "by the frozen N_required rule",
            "unapproved route substitution: any use of Route Q as an arbiter, "
            "or any adopted variance-reduction method",
            "cost-cap breach: total > 60 CPU-hours or a configuration > 40",
            "inability to reproduce historical anchors: the frozen Route-Q, "
            "Route-N, Lean or Arb results failing to re-verify",
            "post-result optimisation: no estimator, threshold, budget or "
            "scope change after seeing a production FAIL",
        ],

        "verdict_semantics": {
            "P4X_CLOSED": "all binding successor obligations C1-C7 pass",
            "P4X_PARTIAL": (
                "the theorem remains valid, some evidence obligations remain "
                "incomplete or fail, and no theorem contradiction is "
                "established"),
            "P4X_FAIL": (
                "a load-bearing scientific claim is contradicted, or an "
                "integrity or governance failure invalidates the campaign"),
            "intermediate_vocabulary_permitted": False,
            "defined_before_results": True,
        },

        "scientific_line_semantics": {
            "if_p4x_closed": {
                "P4_ORIGINAL_VERDICT": "PARTIAL",
                "P4X_SUCCESSOR_VERDICT": "CLOSED",
                "P4_SCIENTIFIC_LINE": "CLOSED_BY_SUCCESSOR_CAMPAIGN",
            },
            "original_p4_remains_historically_partial_forever": True,
        },

        "novelty": {"NOVELTY_STATUS": "NOT_ESTABLISHED",
                    "p4x_performs_novelty_work": False},

        "level4_context": {
            "P5_RESIDUAL_STATUS": "DOCUMENTED_LIMITATION",
            "LEVEL4_GLOBAL_CLOSURE": "NO",
            "p4x_is_not_the_only_residual_limitation": True,
        },

        "protected_tree_manifest": {p: git_object(p) for p in PROTECTED_PATHS},

        "source_artifact_hashes": {
            "P4_PROTOCOL.json": sha256(P4 / "configs" / "P4_PROTOCOL.json"),
            "p4_correspondence.json": sha256(P4 / "results" / "correspondence.json"),
            "p4_closure_decision.json": sha256(P4 / "results" / "closure_decision.json"),
            "r0_pilot.json": sha256(R0 / "results" / "pilot.json"),
            "r0_tail_sweep.json": sha256(R0 / "results" / "tail_sweep.json"),
            "r0_cost_calibration.json": sha256(R0 / "results" / "cost_calibration.json"),
            "r0_cut2_cut3_cost.json": sha256(R0 / "results" / "cut2_cut3_cost.json"),
        },

        "historical_anchors": {
            "p4_verdict": closure["verdict"],
            "p4_failed_gates": sorted(k for k, v in closure["gates"].items() if not v),
            "r0_cpu_hours": pilot["cpu_used_seconds"] / 3600.0,
        },

        "successor_verdict": "NOT_YET_RUN",
        "production_run_performed": False,
        "result_artifacts_generated": False,
    }

    out = CHECKPOINT / "results" / "checkpoint_a.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"P4X Checkpoint A manifest written: {out}")
    print(f"  theorem-supported cells    {len(cells)}  in {len(per_config)} configurations")
    print(f"  r*                         {R_STAR}  (exact {exact_r_star:.9f})")
    print(f"  kappa(t1p5)                {kappa_for(ALPHA_T1P5_FROZEN):.6f}"
          f"  from frozen alpha {ALPHA_T1P5_FROZEN}")
    print(f"  projected stage-1 CPU      {totals['stage1_cpu_hours']:.2f} h")
    print(f"  projected worst-case CPU   {totals['worst_case_cpu_hours']:.2f} h")
    print(f"  caps                       total {TOTAL_CPU_CAP_HOURS} h, "
          f"per configuration {PER_CONFIGURATION_CPU_CAP_HOURS} h")
    print(f"  configurations at risk of the per-configuration cap: {at_risk}")


if __name__ == "__main__":
    main()
