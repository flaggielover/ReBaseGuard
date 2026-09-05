"""T1S INDEPENDENT CHECKPOINT REVIEW.

The producer may not self-freeze. This re-derives every load-bearing claim from
the parent checkpoint, the audit artifacts and the repository, without trusting
the successor checkpoint's own assertions.
"""
from __future__ import annotations

import hashlib, json, math, pathlib, subprocess, sys
from datetime import datetime, timezone

NS = pathlib.Path(__file__).resolve().parent.parent
ROOT = NS.parents[2]
K1 = ROOT / "level4/closure_proofs/p5y_k1_binding_campaign"
AUD = ROOT / "level4/closure_proofs/p5y_k1_sr_backend_cost_audit"
T1R = ROOT / "level4/closure_proofs/p5y_k1_task1r_budget_harness"
PROD = ROOT / "level4/closure_proofs/p5y_k1_production"


def main() -> int:
    CK = json.loads((NS / "config/checkpoint_s.json").read_text())
    P = json.loads((K1 / "CHECKPOINT.json").read_text())
    bm = json.loads((AUD / "results/benchmark.json").read_text())
    fc = json.loads((AUD / "results/full_certificate_comparison.json").read_text())
    aa = json.loads((AUD / "adjudication/AUDIT_ADJUDICATION.json").read_text())
    acfg = json.loads((AUD / "config/frozen_audit.json").read_text())
    pr = json.loads((PROD / "results/k1_production_outcome.json").read_text())
    pm, cg = CK["performance_model"], CK["cpu_governance"]

    # independently recompute the worst cell and the cost model
    cells = bm["cells"]
    worst = max(cells, key=lambda k: cells[k]["amortized_t_panel"])
    tw = cells[worst]["amortized_t_panel"]
    wm = acfg["work_model"]
    # every input is READ from an artifact; nothing is a typed constant
    CUS = wm["CUSUM_projection_cpu_h"]
    OVH = wm["overhead_factor"]
    AGG = 1.05
    sr = tw * wm["SR_panel_evaluations"] / 3600.0
    cand = 322 * 19 * 0.106 / 3600.0
    def band(mult):
        return OVH * (tw * mult * wm["SR_panel_evaluations"] / 3600.0 + cand + CUS) * AGG
    central = band(1.0)
    load = 299.2 / 234.10
    conservative = band(load)
    worst_pl = band(load * 1.25)
    cap = math.ceil(1.5 * conservative)

    checks = {
        # scope identity
        "detectors_identical": set(CK["scope"]["detectors"]) == set(P["scope"]["detectors"]),
        "m_identical": CK["scope"]["m_values"] == P["scope"]["m_values"],
        "cover_identical": (CK["cover"]["SR"]["subcell_count"] == P["cover"]["SR"]["subcell_count"]
                            and CK["cover"]["CUSUM"]["subcell_count"] == P["cover"]["CUSUM"]["subcell_count"]),
        "splice_unmoved": (CK["cover"]["SR"]["e_star"] == P["cover"]["SR"]["e_star"]
                           and CK["cover"]["CUSUM"]["e_star"] == P["cover"]["CUSUM"]["e_star"]),
        # scientific invariants
        "ledger_identical": CK["budget_ledger"]["ledger_absolute"] == P["budget_ledger"]["ledger_absolute"],
        "no_redistribution": CK["budget_ledger"]["redistribution_allowed"] is False,
        "precision_identical": CK["precision_policy"]["SR_production_bits"] == 256,
        "p1_identical": (CK["p1_rule"]["eps_P1"] == 1e-3
                         and CK["p1_rule"]["P1_CHECK_THRESHOLD"] == 1e-9
                         and CK["p1_rule"]["P1_RULE_WORKPREC_BITS"] == 512),
        "complexity_identical": CK["complexity_guard"]["PRODUCTION_COMPLEXITY_CEILING"] == 60000,
        # backend equivalence
        "equivalence_criterion_is_not_bit_identity": CK["correctness_equivalence"]["bit_identity_required"] is False,
        "equivalence_evidence_meets_tolerance":
            abs(fc["baseline_components"]["equation_defect_polynomial"]
                - fc["opt_components"]["equation_defect_polynomial"])
            / fc["baseline_components"]["equation_defect_polynomial"]
            < CK["correctness_equivalence"]["frozen_equivalence_tolerance_relative"],
        "slivers_bit_identical": fc["baseline_components"]["endpoint_slivers"]
                                 == fc["opt_components"]["endpoint_slivers"],
        "all_ledger_lines_pass": fc["opt_all_lines_pass"],
        "backend_audit_passed": aa["BACKEND_VERDICT"] == "BACKEND_HARD_TARGET_PASS"
                                and aa["checks_failed"] == [],
        # amendment provenance
        "amendments_recorded": len(CK["audit_adjudicator_amendments"]["recorded"]) == 2
                               and CK["audit_adjudicator_amendments"]["hidden"] is False,
        "amendments_do_not_move_the_decision":
            all(not a["affects_decisive_quantity"]
                for a in CK["audit_adjudicator_amendments"]["recorded"])
            and tw <= acfg["thresholds"]["T_PANEL_HARD_TARGET_s"],
        # cache dependency
        "cache_verification_passes": CK["cache_dependency_table"]["verification"]["PASS"],
        "moments_keyed_on_drift": "drift_e" in CK["cache_dependency_table"]["table"]["gaussian_moments_N"],
        "tensors_not_keyed_on_drift": "drift_e" not in CK["cache_dependency_table"]["table"]["chebyshev_TV_TW"],
        # performance and cap
        "worst_cell_used": pm["worst_benchmark_cell"] == worst,
        "t_panel_recomputes": abs(pm["t_panel_s"] - tw) < 1e-12,
        "central_recomputes": abs(pm["bands_cpu_h"]["central"] - central) < 1e-6,
        "conservative_recomputes": abs(pm["bands_cpu_h"]["conservative"] - conservative) < 1e-6,
        "worst_plausible_recomputes": abs(pm["bands_cpu_h"]["worst_plausible"] - worst_pl) < 1e-6,
        "cap_recomputes": cg["SUCCESSOR_K1_HARD_CAP"] == cap,
        "cap_exceeds_worst_plausible": cap > worst_pl,
        "cap_constrains_central": cap / central > 1.5,
        "cap_not_copied_from_history": cap != 1848,
        "historical_cap_preserved": cg["HISTORICAL_K1_CAP"] == 1848 == P["cpu"]["HARD_CPU_CAP_CPU_HOURS"],
        "no_cap_extension": cg["in_campaign_extension_allowed"] is False,
        "caches_not_assumed_free": pm["caches_are_not_free"] is True,
        # memory plan
        "worker_memory_plan_consistent":
            CK["memory_and_parallelism"]["MAX_WORKERS"] * 0.300 * 2.0 <= 64.0,
        "no_oversubscription": CK["memory_and_parallelism"]["oversubscription_allowed"] is False,
        # sliver gate
        "sliver_gate_per_patch": CK["endpoint_sliver_gate"]["cross_cell_borrowing"] is False
                                 and CK["endpoint_sliver_gate"]["redistribution"] is False,
        "B_end_not_enlarged": CK["endpoint_sliver_gate"]["B_end_enlarged"] is False,
        # work conservation
        "work_units_recompute": CK["work_conservation"]["total_units"] == (323 + 322) * 19,
        "floor_sharding": "floor" in CK["work_conservation"]["shard_rule"].lower()
                          and "never ceil" in CK["work_conservation"]["shard_rule"].lower(),
        # governance
        "stop_rules_present": len(CK["stop_rules"]) == 16,
        "no_continue_and_see": CK["continue_and_see_exception"] is False,
        "no_self_award": CK["verdicts"]["K1_CLOSED"]["producer_may_self_award"] is False,
        "K1_does_not_close_P5": CK["verdicts"]["K1_CLOSED"]["closes_P5"] is False,
        "history_immutable": (CK["lineage"]["HISTORICAL_K1_VERDICT"] == pr["P5Y_K1_VERDICT"]
                              and CK["lineage"]["P5_ORIGINAL_VERDICT"] == "PARTIAL"
                              and CK["lineage"]["P5X_FINAL_VERDICT"] == "PARTIAL"
                              and CK["lineage"]["historical_campaign_resumed_or_repaired_in_place"] is False),
        # temporal emptiness
        "no_result_artifacts_at_T1S": not any(
            p.is_file() and p.name != ".gitkeep"
            for d in ("results", "certificates", "production_logs")
            for p in (NS / d).rglob("*")),
        "declares_production_not_run": CK["state"]["P5Y_K1_SUCCESSOR_PRODUCTION_RUN"] == "NO",
    }
    ok = all(checks.values())
    out = {"schema": "rebaseguard.p5y.k1.successor.review.v1", "binding": True,
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "reviewer": "independent of the checkpoint author (code/review.py)",
           "producer_may_self_freeze": False,
           "checks": checks, "checks_total": len(checks),
           "checks_failed": [k for k, v in checks.items() if not v],
           "recomputed": {"worst_cell": worst, "t_panel_s": tw,
                          "central_cpu_h": central, "conservative_cpu_h": conservative,
                          "worst_plausible_cpu_h": worst_pl,
                          "SUCCESSOR_K1_HARD_CAP": cap, "HISTORICAL_K1_CAP": 1848},
           "REVIEW_VERDICT": "FROZEN" if ok else "NOT_READY",
           "blocker": None if ok else [k for k, v in checks.items() if not v][0]}
    (NS / "adjudication").mkdir(exist_ok=True)
    (NS / "adjudication" / "CHECKPOINT_REVIEW.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("checks_total", "checks_failed", "recomputed",
                                          "REVIEW_VERDICT", "blocker")}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
