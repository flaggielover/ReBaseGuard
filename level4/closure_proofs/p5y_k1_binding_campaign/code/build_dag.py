"""P5Y K1 -- production task DAG, cover manifests, STOP rules, verdict spec.

DESIGN ARTIFACT. Emits frozen configuration only. Non-result-bearing.
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
CFG = NS / "config"
MAN = NS / "manifests"

M_VALUES = [1, 2, 3, 5]
DETECTORS = ["CUSUM", "SR"]

# ---------------------------------------------------------------- solve DAG
# Objects are defined WITHOUT reference to m (P5X-T1 L1.5-L1.7), so the union
# over m in {1,2,3,5} equals the m=5 set. Verified by Gate-1 PILOT-MSHARE.
def functions() -> list[dict]:
    out: list[dict] = []
    out.append({"id": "h_1", "kind": "closed_form", "deps": [],
                "expr": "1 - Phi(u+e) + Phi(l+e)", "needed_by_m": [3, 5]})
    for j in range(2, 5):
        out.append({"id": f"h_{j}", "kind": "kernel_apply", "deps": [f"h_{j-1}"],
                    "expr": f"K_e h_{j-1}", "needed_by_m": [5]})
    out.append({"id": "S_0", "kind": "closed_form", "deps": [],
                "expr": "phi(u+e) - phi(l+e)", "needed_by_m": [2, 3, 5]})
    for r in range(1, 5):
        out.append({"id": f"S_{r}", "kind": "kernel_apply", "deps": [f"h_{r}"],
                    "expr": f"K_z,e h_{r} + e K_e h_{r}",
                    "needed_by_m": [3, 5] if r == 1 else [5]})
    for r in range(5):
        m_need = [m for m in M_VALUES if r <= m - 1]
        out.append({"id": f"F_{r}", "kind": "resolvent_solve", "deps": [f"S_{r}"],
                    "expr": f"(I - K_e)^-1 S_{r}", "needed_by_m": m_need})
        out.append({"id": f"dF_{r}", "kind": "resolvent_solve",
                    "deps": [f"F_{r}", "S_0"],
                    "expr": "derivative equation; d_e h_1 = -S_0 exactly",
                    "needed_by_m": m_need})
    return out


ASSEMBLY = {
    "general":
        "R_m = (1/m) sum_{r<m} F_r(x0) + sum_{t=1}^{m-1} (1/t - 1/m) "
        "sum_{r<t} (K_e^{t-r-1} S_r)(x0)",
    "derivation": "P5X-T1(c) with raw = Z + e; every finite coefficient collapses "
                  "to (1/t - 1/m).",
    "verified_against_probabilistic_decomposition": [2, 3],
    "per_m": {
        "1": {"F": {"F_0": "1"}, "finite": {}},
        "2": {"F": {"F_0": "1/2", "F_1": "1/2"}, "finite": {"S_0": "1/2"}},
        "3": {"F": {"F_0": "1/3", "F_1": "1/3", "F_2": "1/3"},
              "finite": {"S_0": "2/3", "K S_0": "1/6", "S_1": "1/6"}},
        "5": {"F": {f"F_{r}": "1/5" for r in range(5)},
              "finite": {"S_0": "4/5",
                         "K S_0": "3/10", "S_1": "3/10",
                         "K^2 S_0": "2/15", "K S_1": "2/15", "S_2": "2/15",
                         "K^3 S_0": "1/20", "K^2 S_1": "1/20",
                         "K S_2": "1/20", "S_3": "1/20"}},
    },
}

PHASES = [
    {"id": "A", "name": "integrity + Task-1 F_r qualification",
     "detector": "SR", "cpu_hours_est": 0.5,
     "gates": ["checkpoint_hash", "protected_tree", "direction_audit_both",
               "complexity_guard", "task1_F0"],
     "on_fail": "K1_CAMPAIGN_FAIL_ARCHITECTURE"},
    {"id": "B", "name": "CUSUM compact certificate",
     "detector": "CUSUM", "cells": 323, "functions": 19, "cpu_hours_est": 27.19,
     "on_fail": "per-cell failure_class; STOP under S01-S12"},
    {"id": "C", "name": "SR compact certificate",
     "detector": "SR", "cells": 322, "functions": 19, "cpu_hours_est": 863.84,
     "on_fail": "per-cell failure_class; STOP under S01-S12"},
    {"id": "D", "name": "all-m assembly", "detector": "both",
     "m_values": M_VALUES, "cpu_hours_est": 0.0,
     "note": "arithmetic over already-certified enclosures"},
    {"id": "E", "name": "far-field splice", "detector": "both",
     "cpu_hours_est": 0.01,
     "note": "P5X-T3 B_D on [c_D, c_D+1] plus monotonicity; 3 outward-rounded "
             "Gaussian tail evaluations per detector"},
    {"id": "F", "name": "independent K1 adjudication", "detector": "both",
     "cpu_hours_est": 0.0, "producer_may_self_award": False},
]

PHASE_ORDER_JUSTIFICATION = (
    "Task 1 runs first and on SR because every candidate failure in this "
    "campaign's history (Gate-2D, Gate-2E) was an SR candidate failure, and it "
    "costs one cell. CUSUM then precedes SR because it is ~3% of projected cost "
    "yet exercises the identical raw-variable assembly, m-sharing DAG and budget "
    "ledger: a scientific or governance failure surfacing there costs ~27 CPU-h "
    "instead of ~864. No order optimisation after observing production outcomes."
)

STOP_RULES = [
    ("S01", "certified cell enclosure not strictly inside (-2,2)", "MATHEMATICAL_COUNTEREXAMPLE"),
    ("S02", "candidate budget B_candidate cannot be met", "CANDIDATE_RESIDUAL_TOO_LARGE"),
    ("S03", "representation-complexity guard fails", "REPRESENTATION_COMPLEXITY_FAILURE"),
    ("S04", "amplification direction invalid (lower bound used as upper)", "CHECKPOINT_INTEGRITY_FAILURE"),
    ("S05", "protected artifact mutated", "CHECKPOINT_INTEGRITY_FAILURE"),
    ("S06", "checkpoint hash mismatch", "CHECKPOINT_INTEGRITY_FAILURE"),
    ("S07", "cover gap or overlap", "COVER_INTEGRITY_FAILURE"),
    ("S08", "far-field splice mismatch at e_star_D", "FAR_FIELD_SPLICE_FAILURE"),
    ("S09", "P1 headroom below 1e-6", "P1_HEADROOM_FAILURE"),
    ("S10", "unapproved precision or degree substitution", "PRECISION_FAILURE"),
    ("S11", "budget-ledger violation or attempted redistribution", "BUDGET_EXCEEDED"),
    ("S12", "deterministic work-conservation mismatch", "IMPLEMENTATION_DEFECT"),
    ("S13", "CPU cap breach", "BUDGET_EXCEEDED"),
]

FAILURE_TAXONOMY = [
    "NONE", "MATHEMATICAL_COUNTEREXAMPLE", "CANDIDATE_RESIDUAL_TOO_LARGE",
    "KERNEL_ERROR_TOO_LARGE", "INTERVAL_WIDTH_TOO_LARGE",
    "REPRESENTATION_COMPLEXITY_FAILURE", "P1_HEADROOM_FAILURE",
    "COVER_INTEGRITY_FAILURE", "FAR_FIELD_SPLICE_FAILURE", "PRECISION_FAILURE",
    "BUDGET_EXCEEDED", "CHECKPOINT_INTEGRITY_FAILURE", "IMPLEMENTATION_DEFECT",
    "INCOMPLETE_EXTERNAL", "UNKNOWN",
]

VERDICTS = {
    "K1_CLOSED": {
        "requires_all": [
            "checkpoint_integrity_PASS", "task1_F0_PASS",
            "every_compact_cover_cell_in_scope_PASS",
            "all_m_assembled_for_both_detectors",
            "far_field_splice_valid_both_detectors",
            "every_absolute_budget_respected",
            "non_borrowing_rule_intact", "no_load_bearing_STOP_fired",
            "required_artifact_set_complete",
            "independent_adjudication_PASS",
        ],
        "producer_may_self_award": False,
    },
    "K1_FAIL_MATHEMATICAL": {"trigger": "S01 on a genuine enclosure violation"},
    "K1_FAIL_CERTIFICATE": {"trigger": "S02/S03/S10 or interval width; the "
                                       "architecture cannot certify inside budget"},
    "K1_FAIL_GOVERNANCE": {"trigger": "S04/S05/S06/S07/S11/S12"},
    "K1_CAMPAIGN_FAIL_ARCHITECTURE": {"trigger": "Task-1 F_r qualification FAIL"},
    "K1_INCOMPLETE_BUDGET": {"trigger": "S13 hard CPU cap reached"},
    "K1_INCOMPLETE_EXTERNAL": {"trigger": "external interruption, not a budget breach"},
}

DOWNSTREAM = {
    "if_K1_CLOSED": {
        "K1_STATUS": "K1_CLOSED_BY_P5Y_BINDING_CAMPAIGN",
        "P5_SCIENTIFIC_LINE_STATUS": "PARTIALLY_REPAIRED_BY_SUCCESSOR",
        "P5_ORIGINAL_VERDICT": "PARTIAL",
        "P5X_FINAL_VERDICT": "PARTIAL",
        "K2_s_min": "OPEN", "K3_M2": "OPEN", "K4_H2": "OPEN", "K5_H3a": "OPEN",
        "NOVELTY_STATUS": "NOT_ESTABLISHED",
        "LEVEL4_GLOBAL_CLOSURE": "NO",
        "auto_close_P5": False,
    }
}

# ---------------------------------------------------------------- covers
COVER_CUSUM = {
    "detector": "CUSUM",
    "e_star": 5.5, "e_star_exact": "11/2 = c_D = h/2 + k*... frozen c_CUSUM",
    "interval": [0.0, 5.5],
    "subcell_count": 323,
    "source_artifact":
        "level4/closure_proofs/p5x_global_nonlinear_dynamics/"
        "compute_optimization_r1/R1_COST_REPROJECTION.md",
    "source_note": "R1 optimized monotone-minorant cover: 334 over [0,12], "
                   "323 over [0, e_star] = [0, 5.5]",
    "step_rule": "h(e) = 1 / (4 a C(e)),  a = 2 phi(0) = 0.797884560802865...",
    "walk": "greedy from e=0, exact tiling, no adaptive splitting",
    "covers_exactly": True,
    "adaptive_splitting_allowed": False,
}

COVER_SR = {
    "detector": "SR",
    "e_star": 6.75553146432147319284577138577,
    "interval": [0.0, 6.75553146432147319284577138577],
    "subcell_count": 322,
    "subcell_count_lower_bound": 309,
    "outer_cell_count": 9,
    "width_min": 0.0005196432291227758,
    "width_median": 0.0015509296712958864,
    "width_max": 0.31328086324531856,
    "covers_exactly": True,
    "patches_nominal": 4096,
    "patches_live": 3994,
    "patches_excluded": 102,
    "patch_exclusion_rule":
        "exact multiplicative invariant (xi+' - 1)(xi-' - 1) = xi+ xi- / e; "
        "z cancels exactly, so patch geometry is e-independent",
    "total_panels_over_live_patches": 83452,
    "n_z_mean": 18.8943415122684,
    "n_z_is_not_global_28": True,
    "grid": 64, "degree": 8,
    "source_artifact":
        "level4/closure_proofs/p5y_gate2b_sr_cover/results/sr_cover.json",
    "step_rule": "h(e) = 1 / (4 a C_SR(e))",
    "adaptive_splitting_allowed": False,
}


def main() -> int:
    CFG.mkdir(exist_ok=True)
    MAN.mkdir(exist_ok=True)
    fns = functions()
    dag = {
        "schema": "rebaseguard.p5y.k1.dag.v1", "binding": True,
        "detectors": DETECTORS, "m_values": M_VALUES,
        "cartesian_scope_cells": len(DETECTORS) * len(M_VALUES),
        "functions_per_detector": len(fns),
        "resolvent_solves_per_detector":
            sum(1 for f in fns if f["kind"] == "resolvent_solve"),
        "functions": fns,
        "union_over_m_equals_m5_set": True,
        "m_specific_solves": 0,
        "geometry_multiplied_by_m": False,
        "assembly": ASSEMBLY,
        "phases": PHASES,
        "phase_order_justification": PHASE_ORDER_JUSTIFICATION,
        "total_work_units": 323 * len(fns) + 322 * len(fns),
        "work_unit_address": "(detector, e_subcell_index, function_id)",
        "shard_rule": "shard k gets units [floor(k*N/S), floor((k+1)*N/S))",
        "shard_invariants": ["sum of shard sizes == N exactly", "no overlap",
                             "no omission", "deterministic address mapping",
                             "aggregation identity reproduces the hull",
                             "every unit individually recomputable"],
        "RNG_NOT_LOAD_BEARING": True,
    }
    (CFG / "production_dag.json").write_text(json.dumps(dag, indent=1) + "\n")

    stop = {
        "schema": "rebaseguard.p5y.k1.stoprules.v1", "binding": True,
        "rules": [{"id": i, "condition": c, "failure_class": f,
                   "action": "STOP IMMEDIATELY"} for i, c, f in STOP_RULES],
        "continue_to_see_what_happens_allowed": False,
        "non_decisive_diagnostic_work_exists": False,
        "cpu_stop_semantics": {
            "on_cap": ["stop launching new work",
                       "preserve every completed artifact and partial log",
                       "mark uncomputed cells NOT_COMPUTED explicitly",
                       "PASS may not be inferred from partial coverage",
                       "verdict forced to K1_INCOMPLETE_BUDGET",
                       "no cap extension inside this checkpoint"],
            "external_interruption_verdict": "K1_INCOMPLETE_EXTERNAL",
        },
        "failure_taxonomy": FAILURE_TAXONOMY,
    }
    (CFG / "stop_rules.json").write_text(json.dumps(stop, indent=1) + "\n")

    verdict = {
        "schema": "rebaseguard.p5y.k1.verdict.v1", "binding": True,
        "verdicts": VERDICTS,
        "derived_mechanically_from_recorded_fields": True,
        "narrative_override_allowed": False,
        "downstream_effects": DOWNSTREAM,
        "post_freeze_amendment_allowed": False,
        "required_artifacts": [
            "certificates/cusum_compact_certificate.json",
            "certificates/sr_compact_certificate.json",
            "certificates/far_field_splice.json",
            "certificates/assembly_all_m.json",
            "results/cells_cusum.jsonl", "results/cells_sr.jsonl",
            "results/task1_F0_qualification.json", "results/cpu_ledger.json",
            "results/budget_ledger_usage.json",
            "logs/run_log.jsonl", "logs/shard_map.json",
            "logs/work_conservation.json",
            "adjudication/ADJUDICATION_REPORT.md",
            "adjudication/ADJUDICATION_VERDICT.json",
            "FINAL_K1_VERDICT.json",
        ],
        "missing_artifact_is": "CHECKPOINT_INTEGRITY_FAILURE",
        "cell_record_fields": [
            "detector", "m_relevance", "e_interval", "cover_cell_id",
            "candidate_id", "candidate_degree", "candidate_residual",
            "kernel_residual", "resolvent_amplification_bound",
            "rounding_error", "interval_radius",
            "propagated_absolute_half_width", "allowed_absolute_half_width",
            "budget_usage_by_component", "P1_E_d", "P1_headroom_rel",
            "complexity_score", "working_precision_bits",
            "timing_cpu_seconds", "verdict", "failure_class",
        ],
        "summary_only_artifacts_allowed": False,
    }
    (CFG / "final_verdict_spec.json").write_text(json.dumps(verdict, indent=1) + "\n")

    for name, obj in (("cover_cusum.json", COVER_CUSUM), ("cover_sr.json", COVER_SR)):
        obj = {"schema": "rebaseguard.p5y.k1.cover.v1", "binding": True, **obj}
        (MAN / name).write_text(json.dumps(obj, indent=1) + "\n")

    print("functions/detector      =", len(fns))
    print("resolvent solves/det    =", dag["resolvent_solves_per_detector"])
    print("total work units        =", dag["total_work_units"])
    print("cartesian scope cells   =", dag["cartesian_scope_cells"])
    print("stop rules              =", len(STOP_RULES))
    print("wrote config/{production_dag,stop_rules,final_verdict_spec}.json")
    print("wrote manifests/{cover_cusum,cover_sr}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
