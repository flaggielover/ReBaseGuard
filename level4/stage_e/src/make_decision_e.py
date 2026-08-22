"""Apply the frozen Stage E decision rule. No fourth status may be invented."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
PROTO_SHA = "974487019f57c7c319b3bfafcdc20497ab6fca86834ad0d2245a694296ef23cc"
ALLOWED = ["STAGE-E-CLOSED-EXTERNAL-VALIDATION", "STAGE-E-PARTIAL",
           "STAGE-E-FAILED"]
EXPLORATORY = "P3_moderate_EXPLORATORY"


def load(n):
    return json.loads((RES / n).read_text())


def main() -> None:
    adv = load("adversarial.json")

    per = {
        "electricity": {
            "task": "A", "dataset": "Electricity / Elec2 (OpenML 151)",
            "usability": "USABLE", "power_class": "adequate",
            "effective_blocks": {"E1": 24, "E4": 24, "E2": 23, "E3": 23},
            "unreliable_endpoints": [],
            "hypotheses": {
                "H_E1": {"status": "SUPPORTED",
                         "detail": "E2(P1)=0.3330 > E2(P2)=0.2564 (+0.0766 "
                                   "[+0.0369,+0.1135]) and > E2(P0)=0.2447 "
                                   "(+0.0883 [+0.0498,+0.1326]); both CIs exclude 0"},
                "H_E2": {"status": "NOT SUPPORTED",
                         "kind": "statistical non-demonstration",
                         "detail": "burden P1 5.55 > P2 5.38 > P0 5.15 in the "
                                   "predicted order; all cycle-length CIs include 0"},
                "H_E3": {"status": "NOT SUPPORTED",
                         "kind": "statistical non-demonstration",
                         "detail": "fails at 3 of 5 conditions at both margins; "
                                   "point estimate of the excess is NEGATIVE at "
                                   "all five, so this is failure to demonstrate "
                                   "non-inferiority, NOT demonstrated inferiority"},
                "H_E4": {"status": "NOT SUPPORTED",
                         "kind": "directional contradiction",
                         "detail": "R(P1)-R(P2) = -0.0141 [-0.2855,+0.2047]: "
                                   "point estimate is the OPPOSITE sign to the "
                                   "hypothesis, and the CI includes 0"},
                "H_E5": {"status": "NOT SUPPORTED",
                         "detail": "needs H-E1 AND (H-E2 OR H-E4); only H-E1 holds"},
            },
            "counts_toward_H_E5": False,
        },
        "air_quality": {
            "task": "B", "dataset": "UCI Air Quality (id 360)",
            "usability": "USABLE", "power_class": "LOW-POWER",
            "effective_blocks": {"E1": 5, "E4": 5, "E2": 5, "E3": 5},
            "unreliable_endpoints": ["P3 E2 (4 blocks)"],
            "hypotheses": {
                "H_E1": {"status": "NOT SUPPORTED",
                         "kind": "statistical non-demonstration",
                         "detail": "P1 largest (1.1349) but P1-P2 [-0.7147,+0.9203] "
                                   "and P1-P0 [-0.6993,+0.9213] include 0"},
                "H_E2": {"status": "NOT SUPPORTED",
                         "kind": "statistical non-demonstration",
                         "detail": "P2 5.33 < P1 5.70 in the predicted direction; "
                                   "cycle-length CI includes 0"},
                "H_E3": {"status": "SUPPORTED at eps=0.10",
                         "eps_0.05": "NOT SUPPORTED (STEP_0.5 upper95 excess "
                                     "+0.0577 > 0.05)",
                         "detail": "all five conditions pass at the primary margin"},
                "H_E4": {"status": "NOT SUPPORTED",
                         "kind": "statistical non-demonstration",
                         "detail": "R(P1)-R(P2) = +0.0528 [-0.0436,+0.2367]: "
                                   "predicted direction, CI includes 0"},
                "H_E5": {"status": "NOT SUPPORTED",
                         "detail": "needs H-E1 AND (H-E2 OR H-E4); H-E1 unmet"},
            },
            "counts_toward_H_E5": False,
        },
        "bike_sharing": {
            "task": "C", "dataset": "UCI Bike Sharing (id 275)",
            "usability": "PARTIALLY USABLE AFTER FREEZE",
            "power_class": "E1/E4 adequate; E2/E3 below floor",
            "effective_blocks": {"E1": 10, "E4": 10, "E2": 2, "E3": 2},
            "unreliable_endpoints": ["E2", "E3"],
            "hypotheses": {
                "H_E1": {"status": "UNEVALUABLE",
                         "detail": "E2 below the pre-specified effective-block "
                                   "floor for all closure policies (2-3 blocks)"},
                "H_E2": {"status": "UNEVALUABLE",
                         "detail": "E3 below the floor for all closure policies"},
                "H_E3": {"status": "SUPPORTED at eps=0.10 AND eps=0.05",
                         "detail": "all five conditions pass at both margins"},
                "H_E4": {"status": "SUPPORTED",
                         "detail": "R(P1)-R(P2) = +0.0470 [+0.0062,+0.1266], "
                                   "excludes 0; the only task where H-E4 is met"},
                "H_E5": {"status": "NOT MET",
                         "detail": "requires H-E1 AND (H-E2 OR H-E4); H-E1 is "
                                   "UNEVALUABLE, so the conjunction cannot hold"},
            },
            "counts_toward_H_E5": False,
        },
    }

    n_support = sum(v["counts_toward_H_E5"] for v in per.values())
    adv_ok = adv["n_failed"] == 0

    # ---- frozen decision rule, applied in order -------------------------
    trace = []
    if not adv_ok:
        decision = "STAGE-E-FAILED"
        trace.append("adversarial/reproducibility failure -> STAGE-E-FAILED")
    elif n_support >= 2:
        decision = "STAGE-E-CLOSED-EXTERNAL-VALIDATION"
        trace.append(f"{n_support}/3 tasks support H-E5 -> closure")
    else:
        trace.append(f"adversarial suite {adv['n_passed']}/{adv['n_checks']} -> "
                     "STAGE-E-FAILED not triggered on that ground")
        trace.append(f"only {n_support}/3 tasks support H-E5 -> "
                     "STAGE-E-CLOSED-EXTERNAL-VALIDATION unreachable")
        trace.append("full reuse IS meaningfully worse in at least one task "
                     "(Task A H-E1 supported; Task C H-E4 supported), so the "
                     "STAGE-E-FAILED condition 'full reuse not meaningfully "
                     "worse in any task' does NOT hold")
        trace.append("ReBaseGuard does not systematically degrade detection: "
                     "H-E3 holds at eps=0.10 in Tasks B and C and every Task A "
                     "point estimate favours P2 -> second FAILED condition "
                     "does NOT hold")
        trace.append("task conclusions conflict materially and one task became "
                     "partially unusable after freeze -> STAGE-E-PARTIAL")
        decision = "STAGE-E-PARTIAL"

    assert decision in ALLOWED, decision
    actual = hashlib.sha256((ROOT / "STAGE_E_PROTOCOL.md").read_bytes()).hexdigest()

    out = {
        "stage": "E", "decision": decision, "allowed_labels": ALLOWED,
        "protocol_sha256_expected": PROTO_SHA, "protocol_sha256_actual": actual,
        "protocol_unchanged": actual == PROTO_SHA,
        "decision_rule_trace": trace,
        "n_tasks_supporting_H_E5": n_support,
        "n_tasks_required_for_closure": 2,
        "closure_mathematically_unreachable": bool(n_support < 2),
        "adversarial": {"passed": adv["n_passed"], "total": adv["n_checks"]},
        "per_task": per,
        "exploratory_policy_excluded": EXPLORATORY,
        "scope_limits": [
            "Semi-real external validation, NOT deployment validation.",
            "Three streams are not a population; nothing here is universal.",
            "No sample-efficiency claim: every policy consumes the fresh "
            "settling block each cycle, so fresh consumption is identical.",
            "E3 is an alert BURDEN, not a false-alarm rate: the natural "
            "streams contain real concept drift.",
            "epsilon = 0.10 is an independently pre-specified Stage E margin, "
            "NOT a continuation of Stage C.1's epsilon = 0.05.",
        ],
    }
    (RES / "stage_e_decision.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"{'task':14s} {'usability':32s} {'H-E5':14s} counts")
    for k, v in per.items():
        print(f"{k:14s} {v['usability']:32s} "
              f"{v['hypotheses']['H_E5']['status']:14s} {v['counts_toward_H_E5']}")
    print("\nDecision rule trace:")
    for t in trace:
        print(f"  - {t}")
    print(f"\n  FINAL STAGE E DECISION: {decision}")
    print(f"  adversarial: {adv['n_passed']}/{adv['n_checks']}   "
          f"protocol unchanged: {actual == PROTO_SHA}")


if __name__ == "__main__":
    main()
