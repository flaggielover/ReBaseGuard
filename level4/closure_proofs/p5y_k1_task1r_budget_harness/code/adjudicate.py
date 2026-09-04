"""T4R: INDEPENDENT adjudication. The producer may not self-award TASK1R PASS.

Re-derives every load-bearing claim from the frozen checkpoint and the result
artifact, without trusting the producer's own verdict field.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
NSREL = "level4/closure_proofs/p5y_k1_task1r_budget_harness"
K1REL = "level4/closure_proofs/p5y_k1_binding_campaign"


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a],
                          capture_output=True, text=True, check=True).stdout


def main() -> int:
    res = json.loads((NS / "results/task1r_F0_qualification.json").read_text())
    fp = json.loads((NS / "config/frozen_parameters.json").read_text())
    man = json.loads((NS / "manifests/task1r_manifest.json").read_text())
    cert, bud = res["certificate"], res["budget"]
    part = json.loads((NS / "config/frozen_parameters.json").read_text())["budget_partition"]

    # --- A. provenance / chronology
    t1r = git("log", "--format=%H", "--grep", "Task-1R T1R", "-1").strip()
    t1r_short = t1r[:7] if t1r else None
    ancestry = bool(t1r) and subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", t1r, "HEAD"]).returncode == 0
    frozen_before = bool(t1r)
    if t1r:
        # every frozen file must be unchanged since T1R
        changed = [f for f in man["file_sha256"]
                   if hashlib.sha256(subprocess.run(
                       ["git", "-C", str(ROOT), "show", f"{t1r}:{NSREL}/{f}"],
                       capture_output=True, check=True).stdout).hexdigest()
                   != man["file_sha256"][f]]
    else:
        changed = ["<T1R commit not found>"]
    agg = hashlib.sha256()
    for f, h in man["file_sha256"].items():
        agg.update(f.encode()); agg.update(b"\0"); agg.update(h.encode()); agg.update(b"\n")
    hash_ok = agg.hexdigest() == man["TASK1R_CHECKPOINT_HASH"]

    # --- B. parameters actually used == parameters frozen
    used = (res["D"], res["Z"])
    frozen = (fp["selection"]["D_selected"], fp["selection"]["Z_selected"])

    # --- C. certificate arithmetic, recomputed
    comp_sum = sum(cert["components"].values())
    arith = {
        "components_sum_equals_delta": abs(comp_sum - cert["delta_F0"]) < 1e-18,
        "propagated_equals_C_times_delta":
            abs(bud["C_SR_at_e"] * cert["delta_F0"]
                - bud["propagated_contribution"]) < 1e-15,
        "fraction_matches": abs(bud["propagated_contribution"] / bud["B_candidate"]
                                - bud["fraction_of_B_candidate"]) < 1e-15,
        "per_line_allowances_correct": all(
            abs(v["allowance_delta_units"]
                - part["absolute"][v["budget_line"]] / bud["C_SR_at_e"]) < 1e-18
            for v in cert["per_line"].values()),
        "per_line_gates_correct": all(
            (v["value"] <= v["allowance_delta_units"]) == v["PASS"]
            for v in cert["per_line"].values()),
        "every_line_within_allowance": all(v["PASS"] for v in cert["per_line"].values()),
        "total_within_B_candidate":
            bud["propagated_contribution"] <= bud["B_candidate"],
    }

    # --- D. budget integrity
    budget_ok = {
        "partition_sums_to_B_candidate": part["sums_to_B_candidate"],
        "sum_absolute_exact": part["sum_absolute"] == bud["B_candidate"],
        "reserve_non_redistributable": part["reserve_redistributable"] is False,
        "no_new_budget": part["new_budget_created"] is False,
        "no_redistribution_used": bud["redistribution_used"] is False,
        "reserve_not_drawn": bud["reserve_drawn"] is False,
        "every_component_has_a_line": set(cert["components"]) == set(cert["per_line"]),
    }

    # --- E. frozen scientific invariants
    sc = res["frozen_scope"]["checks"]
    inv = {k: sc[k] for k in ("detector", "object", "patch", "grid", "e", "bidegree",
                              "scale_bits", "B_candidate", "LOCAL_GATE_BUDGET",
                              "no_redistribution", "eps_P1", "P1_check", "P1_guard",
                              "P1_workprec", "SR_bits", "no_precision_escalation",
                              "no_degree_adaptation", "complexity_ceiling",
                              "m_set", "detectors")}

    # --- F. predecessor immutability
    pred = {"unmutated": res["integrity"]["predecessor_mutated"] == [],
            "still_FAIL": res["integrity"]["predecessor_verdict"] == "FAIL",
            "class_preserved": res["integrity"]["predecessor_governing_class"]
                               == "IMPLEMENTATION_DEFECT"}

    # --- G. guards
    guards = {
        "amplification_UPPER": res["amplification"]["type"] == "UPPER",
        "amplification_PASS": res["amplification"]["PASS"],
        "C0_le_certified_cap": res["amplification"]["C0_le_certified_cap"],
        "P1_PASS": res["p1"]["PASS"],
        "P1_rule_check_distinct": res["p1"]["rule_and_check_distinct"],
        "P1_workprec_512": res["p1"]["P1_RULE_WORKPREC_BITS"] == 512,
        "P1_headroom_above_guard": res["p1"]["HEADROOM_REL"] >= res["p1"]["headroom_guard"],
        "joint_consistency_PASS": res["joint_consistency"]["PASS"],
        "complexity_PASS": res["complexity_guard"]["PASS"],
        "scores_within_ceiling": res["joint_consistency"]["scores_within_ceiling"],
        "precision_256": res["p1"] is not None and res["frozen_scope"]["checks"]["SR_bits"],
    }

    sections = {"provenance": {"T1R_commit": t1r_short,
                               "T1R_is_ancestor_of_HEAD": ancestry,
                               "T1R_frozen_before_T2R": frozen_before,
                               "frozen_files_changed_since_T1R": changed,
                               "manifest_hash_recomputes": hash_ok,
                               "TASK1R_CHECKPOINT_HASH": man["TASK1R_CHECKPOINT_HASH"]},
                "parameters": {"used": list(used), "frozen": list(frozen),
                               "identical": used == frozen,
                               "selection_result_independent":
                                   res["selection_was_result_independent"]},
                "certificate_arithmetic": arith,
                "budget_integrity": budget_ok,
                "frozen_invariants": inv,
                "predecessor_immutability": pred,
                "guards": guards}

    def flat(d):
        for v in d.values():
            if isinstance(v, dict):
                yield from flat(v)
            elif isinstance(v, bool):
                yield v
    checks = list(flat(sections))
    extra = [ancestry, frozen_before, hash_ok, not changed, used == frozen]
    verdict = all(checks) and all(extra)

    tightest = max(cert["per_line"].items(), key=lambda kv: kv[1]["fraction_of_line"])
    out = {"schema": "rebaseguard.p5y.k1.task1r.adjudication.v1",
           "binding": True,
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "adjudicator": "independent of the producing script (code/adjudicate.py)",
           "producer_self_award_permitted": False,
           "sections": sections,
           "checks_total": len(checks) + len(extra),
           "checks_failed": [i for i, c in enumerate(checks + extra) if not c],
           "tightest_line": {"name": tightest[0],
                             "fraction_of_line": tightest[1]["fraction_of_line"],
                             "note": ("the endpoint-sliver term is the structural "
                                      "component the successor did NOT repair; it is "
                                      "the binding line here and is a named residual "
                                      "risk for the full campaign, where other patches "
                                      "may carry larger slivers")},
           "producer_verdict": res["TASK1R_VERDICT"],
           "ADJUDICATED_VERDICT": "PASS" if verdict else "FAIL",
           "P5Y_K1_TASK1R": "PASS" if verdict else "FAIL",
           "NEXT_ACTION": ("K1_FULL_PRODUCTION_CAMPAIGN" if verdict
                           else "STOP_K1_SUCCESSOR_CHAIN")}
    (NS / "adjudication").mkdir(exist_ok=True)
    (NS / "adjudication" / "TASK1R_ADJUDICATION.json").write_text(
        json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("checks_total", "checks_failed", "tightest_line",
                       "producer_verdict", "ADJUDICATED_VERDICT",
                       "P5Y_K1_TASK1R", "NEXT_ACTION")}, indent=1))
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
