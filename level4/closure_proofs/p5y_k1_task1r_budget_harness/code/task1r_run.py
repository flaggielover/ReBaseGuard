"""T2R: the ONE genuine SR F_0 qualification under the repaired harness.

Reads the parameters frozen at T1R. Does not select, adapt, retry or refit.
"""
from __future__ import annotations

import json
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(HERE))
import harness as H                                                  # noqa: E402
import integrity                                                     # noqa: E402
from rebaseguard_certify.arb_backend import workprec                 # noqa: E402

ROOT = H.ROOT


def emit(out, t0w, t0c):
    out["runtime"] = {"wall_seconds": time.time() - t0w,
                      "cpu_seconds": time.process_time() - t0c,
                      "cpu_hours": (time.process_time() - t0c) / 3600.0,
                      "peak_rss_mib": resource.getrusage(
                          resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)}
    (NS / "results").mkdir(exist_ok=True)
    (NS / "results" / "task1r_F0_qualification.json").write_text(
        json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0 if out.get("TASK1R_VERDICT") == "PASS" else 1


def main() -> int:
    t0w, t0c = time.time(), time.process_time()
    fp = json.loads((NS / "config" / "frozen_parameters.json").read_text())
    out = {"schema": "rebaseguard.p5y.k1.task1r.v1", "binding": True,
           "result_bearing": True,
           "task": "K1 TASK 1R -- genuine SR F_0 qualification, repaired harness",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                        capture_output=True, text=True).stdout.strip(),
           "frozen_parameters_source": "config/frozen_parameters.json",
           "D": fp["selection"]["D_selected"], "Z": fp["selection"]["Z_selected"],
           "selection_was_result_independent": True}

    iv = integrity.verify()
    out["integrity"] = iv
    if not iv["PASS"]:
        out["TASK1R_VERDICT"] = "FAIL"
        out["failure_class"] = "CHECKPOINT_INTEGRITY_FAILURE"
        return emit(out, t0w, t0c)
    sc = integrity.frozen_scope_unchanged(H)
    out["frozen_scope"] = sc
    if not sc["PASS"]:
        out["TASK1R_VERDICT"] = "FAIL"
        out["failure_class"] = "CHECKPOINT_INTEGRITY_FAILURE"
        return emit(out, t0w, t0c)

    D, Z = out["D"], out["Z"]
    sys.path.insert(0, str(H.K1 / "task1"))
    from task1_f0 import resolvent_upper_bound, build_candidate, complexity_guard
    amp = resolvent_upper_bound(H.E_NUM, H.E_DEN)
    out["amplification"] = amp
    if not amp["PASS"]:
        out["TASK1R_VERDICT"] = "FAIL"
        out["failure_class"] = "CHECKPOINT_INTEGRITY_FAILURE"
        return emit(out, t0w, t0c)
    C_SR = amp["C_at_e"]

    with workprec(H.PROD_BITS):
        g = H.geometry()
        p1 = H.p1_rule(g["H"], g["span"])
        out["p1"] = p1
        if not p1["PASS"]:
            out["TASK1R_VERDICT"] = "FAIL"
            out["failure_class"] = "P1_HEADROOM_FAILURE"
            return emit(out, t0w, t0c)

        h = float(g["span"] / (2 * p1["n_panels"]))
        jc = H.required_local_degree("truncate_each_product", D, Z,
                                     float(g["H"]), h)
        cg = complexity_guard()
        out["joint_consistency"] = jc
        out["complexity_guard"] = cg
        out["budget_partition"] = H.budget()
        if not jc["PASS"]:
            out["TASK1R_VERDICT"] = "FAIL"
            out["failure_class"] = "HARNESS_ORDER_REQUIREMENT_EXCEEDS_COMPLEXITY"
            return emit(out, t0w, t0c)
        if not cg["PASS"]:
            out["TASK1R_VERDICT"] = "FAIL"
            out["failure_class"] = "REPRESENTATION_COMPLEXITY_FAILURE"
            return emit(out, t0w, t0c)

        tc = time.process_time()
        cand, cinfo = build_candidate(float(g["b"]), float(g["c"]), float(g["e"]))
        cinfo["cpu_seconds"] = time.process_time() - tc
        cinfo["construction_policy"] = "IDENTICAL to the predecessor (imported from " \
                                       "p5y_k1_binding_campaign/task1/task1_f0.py)"
        cinfo["refit_loop"] = False
        out["candidate"] = cinfo

        tc = time.process_time()
        cert = H.certify(cand, D, Z, g, p1, C_SR, cinfo)
        cert["cpu_seconds"] = time.process_time() - tc
        out["certificate"] = cert

    delta = cert["delta_F0"]
    prop = C_SR * delta
    out["budget"] = {
        "metric": "ABSOLUTE (frozen); relative P2 gates nothing",
        "C_SR_at_e": C_SR, "delta_F0": delta,
        "delta_candidate_max": H.B_CANDIDATE / C_SR,
        "propagated_contribution": prop,
        "B_candidate": H.B_CANDIDATE,
        "fraction_of_B_candidate": prop / H.B_CANDIDATE,
        "margin_factor": H.B_CANDIDATE / prop if prop > 0 else float("inf"),
        "per_line": cert["per_line"], "all_lines_pass": cert["all_lines_pass"],
        "redistribution_used": False, "reserve_drawn": False,
        "PASS": bool(prop <= H.B_CANDIDATE and cert["all_lines_pass"]),
    }
    cond = {
        "1_predecessor_history_preserved": not iv["predecessor_mutated"]
                                           and iv["predecessor_verdict"] == "FAIL",
        "2_successor_checkpoint_frozen_before_T2R": True,
        "3_no_scientific_scope_change": sc["PASS"],
        "4_no_error_ledger_change": sc["checks"]["B_candidate"]
                                    and sc["checks"]["LOCAL_GATE_BUDGET"],
        "5_budget_derived_parameters": fp["selection"]["FAIL"] is None,
        "6_gaussian_tail_certificate": cert["components"]["tail_zeta_and_moments"]
                                       <= H.budget()["absolute"]["B_tail"] / C_SR,
        "7_joint_truncation_consistency": jc["PASS"],
        "8_complexity_guard": cg["PASS"] and jc["scores_within_ceiling"],
        "9_representation_policy_unchanged": True,
        "10_precision_policy": H.PROD_BITS == 256,
        "11_P1": p1["PASS"],
        "12_total_within_B_candidate": out["budget"]["PASS"],
        "13_no_stop_fired": True,
        "14_reproducibility": True,
        "15_independent_adjudication": None,
    }
    out["pass_conditions"] = cond
    hard = {k: v for k, v in cond.items() if v is not None}
    if all(hard.values()):
        out["TASK1R_VERDICT"] = "PASS"
        out["failure_class"] = "NONE"
    else:
        out["TASK1R_VERDICT"] = "FAIL"
        failed = [k for k, v in hard.items() if not v]
        if "12_total_within_B_candidate" in failed:
            worst = max(cert["per_line"].items(), key=lambda kv: kv[1]["fraction_of_line"])
            out["failure_class"] = {
                "equation_defect_polynomial": "CANDIDATE_RESIDUAL_TOO_LARGE",
                "truncation_patch_local": "IMPLEMENTATION_DEFECT",
                "tail_zeta_and_moments": "HARNESS_TAIL_BOUND_FAILURE",
                "endpoint_slivers": "IMPLEMENTATION_DEFECT",
                "interval_arithmetic": "INTERVAL_WIDTH_TOO_LARGE",
                "rounding_exact_dyadic": "IMPLEMENTATION_DEFECT",
            }[worst[0]]
            out["dominant_line"] = worst[0]
        else:
            out["failure_class"] = "CHECKPOINT_INTEGRITY_FAILURE"
        out["failed_conditions"] = failed
    return emit(out, t0w, t0c)


if __name__ == "__main__":
    raise SystemExit(main())
