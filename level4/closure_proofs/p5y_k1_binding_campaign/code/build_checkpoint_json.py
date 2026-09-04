"""P5Y K1 -- machine-readable checkpoint. DESIGN ARTIFACT, non-result-bearing."""
from __future__ import annotations

import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]


def load(rel: str) -> dict:
    return json.loads((NS / rel).read_text())


def main() -> int:
    budget = load("config/budget_ledger.json")
    dag = load("config/production_dag.json")
    stop = load("config/stop_rules.json")
    verdict = load("config/final_verdict_spec.json")
    p1 = load("config/p1_rule.json")
    cx = load("config/complexity_guard.json")
    prec = load("config/precision_policy.json")
    cov_c = load("manifests/cover_cusum.json")
    cov_s = load("manifests/cover_sr.json")

    cpu = subprocess.run(
        ["python3", str(HERE / "cpu_model_k1.py")],
        capture_output=True, text=True, check=True)
    cpu_model = json.loads(cpu.stdout)

    ck = {
        "schema": "rebaseguard.p5y.k1.checkpoint.v1",
        "checkpoint_id": "P5Y-K1-BINDING-CHECKPOINT-1",
        "binding": True,
        "design_only": True,
        "production_run": "NO",
        "result_bearing_artifacts_present": False,

        "inherited_state": {
            "P5_ORIGINAL_VERDICT": "PARTIAL",
            "P5X_FINAL_VERDICT": "PARTIAL",
            "P5X_CAMPAIGN": "ARCHIVALLY_COMPLETE",
            "P5Y_GATE1": "PASS_ROUTE_B_SUPPORTED",
            "P5Y_GATE2A": "SR_PRECISION_PASS_256",
            "P5Y_GATE2B": "SR_COVER_PASS_MEASURED",
            "P5Y_GATE2C": "M2_ASSEMBLY_INCOMPLETE_EXTERNAL",
            "P5Y_GATE2CBIS": "M2_ASSEMBLY_B_PASS",
            "P5Y_GATE2D": "SR_REALCANDIDATE_FAIL_REPRESENTATION",
            "P5Y_GATE2E": "SR_METRIC_FAIL_CANDIDATE",
            "P5Y_GATE2F": "SR_METRIC_B_PASS_256",
            "failed_gates_remain_failed_permanently": True,
            "reinterpretation_of_prior_verdicts": False,
        },

        "target": {
            "claim": "R_max(D,m) = sup_e |R_{D,m}(e)| < 2 for both detectors and "
                     "all frozen m",
            "K1_only": True,
            "out_of_scope": ["K2_s_min", "K3_M2", "K4_H2", "K5_H3a",
                             "novelty", "level4_global_closure"],
        },

        "scope": {
            "detectors": {
                "CUSUM": {"k": 0.5, "h": 5, "two_sided": True,
                          "test": "inclusive post-update", "priority": "plus-arm"},
                "SR": {"A": 520.886133602749, "charts": 2, "stored": "y=log(1+R)",
                       "y0": 0.0, "b_SR_is_log1pA": True,
                       "erratum": "D1 (b_SR = log(1+A))"},
            },
            "m_values": [1, 2, 3, 5],
            "cartesian_cells": 8,
            "observation": "raw_t ~ iid N(0,1), Delta = 0, z_t = raw_t - e",
            "stopping": "tau inclusive, w = min(m,tau), Stage-D convention A",
            "source": "p5x_global_nonlinear_dynamics/FROZEN_SCOPE.md",
            "result_dependent_cell_deletion_allowed": False,
        },

        "architecture": {
            "route": "B",
            "raw_variable_reformulation": True,
            "external_plus_e_cancellation": False,
            "CUSUM_backend": "recentred Hermite phi-expansion order 120, "
                             "exact-dyadic Chebyshev degree 12, Bernstein range "
                             "bound, depth ladder (0,1,2,3), 256-bit Arb",
            "SR_backend": "degree-8 composed contraction, candidate bidegree "
                          "(16,16), 256-bit Arb, patch grid 64, continuous "
                          "minimal-safe panel rule, Gate-2F asymmetric P1",
            "m_sharing": True,
            "far_field": "P5X-T3 analytic splice",
            "substitution_after_results_allowed": False,
        },

        "amplification": {
            "type": "UPPER",
            "object": "||(I - K_e)^{-1}||_inf = sup_x E_{x,e}[tau]",
            "form": "C = min_t t / H_t(0), H_t a LOWER Bellman envelope",
            "per_detector": {
                "CUSUM": {"source": "compute_optimization_r1/drift_minorant.py",
                          "cells": 100, "n_max": 250, "bits": 192,
                          "C_at_0": 1232.84},
                "SR": {"source": "p5y_gate2b_sr_cover/sr_cover.py",
                       "cells": 200, "n_max": 250, "bits": 192,
                       "C_at_0": 1205.9371382854872,
                       "C_at_quarter": 187.7471962405577},
            },
            "certified_cap": 1315.7894736842106,
            "direction_audit_mandatory_before_cells": True,
            "uses_P5X_defect_D3_assumption": False,
        },

        "budget_ledger": budget,
        "p1_rule": p1,
        "complexity_guard": cx,
        "precision_policy": prec,
        "cover": {"CUSUM": cov_c, "SR": cov_s},
        "production_dag": dag,
        "stop_rules": stop,
        "final_verdict_spec": verdict,

        "cpu": {
            "model": cpu_model,
            "soft_expected_band_cpu_hours":
                cpu_model["bands_cpu_hours"]["soft_expected_band"],
            "HARD_CPU_CAP_CPU_HOURS": cpu_model["bands_cpu_hours"]["hard_cpu_cap"],
            "cap_derivation": "ceil(beta * K1_conservative), beta = 1.5 "
                              "governance-inherited from Gate-2C-bis",
            "programme_worst_reference_not_adopted": 4597,
            "cap_extension_allowed": False,
        },

        "task1": {
            "name": "F_r candidate qualification",
            "detector": "SR", "object": "F_0", "e": "1/4 exact",
            "patch": [17, 11], "grid": 64,
            "candidate_bidegree": [16, 16], "dyadic_scale_bits": 50,
            "residual_certified_by": "equation defect ||Fhat - K_e Fhat - S_0^raw||"
                                     " via reachable-set range bound, propagated "
                                     "as C * delta",
            "budget_line": "B_candidate (already frozen; no new budget)",
            "guard_before_kernel_construction": True,
            "on_fail": "K1_CAMPAIGN_FAIL_ARCHITECTURE, STOP, no repair in this "
                       "checkpoint",
            "is_first_result_bearing_task": True,
            "executed": False,
        },

        "governance": {
            "protected_write_paths": ["results/", "certificates/", "logs/"],
            "immutable": ["p5_nonlinear_dynamics/", "p5x_global_nonlinear_dynamics/",
                          "p5y_micropilot_gate1/", "p5y_gate2a_sr_precision/",
                          "p5y_gate2b_sr_cover/", "p5y_gate2c_m2_assembly/",
                          "p5y_gate2cbis_m2_assembly_b/",
                          "p5y_gate2d_sr_realcandidate/", "p5y_gate2e_sr_metric/",
                          "p5y_gate2f_sr_metric_b/"],
            "post_freeze_amendment_allowed": False,
            "independent_adjudication_required": True,
            "producer_may_self_award_K1_CLOSED": False,
            "merge_to_main_authorized": False,
            "temporal_anchors": {
                "T0": "namespace + checkpoint authored",
                "T1": "freeze commit; hashes from git ls-tree at anchor",
                "T2": "design-validation tests pass against the anchor commit",
                "T3": "production execution -- NOT PERFORMED",
                "T4": "adjudication -- NOT PERFORMED",
            },
            "hash_source": "git ls-tree at anchor commit (never the worktree)",
        },

        "residual_risk": {
            "R1": "F_r resolvent-solution candidates have never been built at "
                  "production fidelity; Gate-2D failed on the EASIER closed-form "
                  "h_1. Dominant risk; Task 1 exists for it.",
            "R2": "C_SR(0) = 1205.94 multiplies every local error; the cover is "
                  "densest exactly where amplification is largest.",
            "R3": "the 322-cell SR cover came from a monotone ENVELOPE walk; the "
                  "true production cover may be larger (the x1.25 worst band).",
            "R4": "the far-field splice requires numerics to reach e_star_D "
                  "exactly; a gap is S08 and fatal, not patchable.",
            "R5": "no outcome here bears on K2..K5 or novelty.",
        },

        "state": {
            "P5Y_K1_CHECKPOINT_STATUS": "FROZEN",
            "P5Y_BINDING_CHECKPOINT_CREATED": "YES",
            "P5Y_PRODUCTION_RUN": "NO",
        },
    }
    (NS / "CHECKPOINT.json").write_text(json.dumps(ck, indent=1) + "\n")
    print("wrote CHECKPOINT.json",
          (NS / "CHECKPOINT.json").stat().st_size, "bytes")
    print("HARD_CPU_CAP =", ck["cpu"]["HARD_CPU_CAP_CPU_HOURS"], "CPU-h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
