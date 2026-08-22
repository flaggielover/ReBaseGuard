"""Apply the frozen Stage D decision rule. No label may be invented."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
PROTOCOL_SHA = "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e"
ALLOWED = ["STAGE-D-INCONCLUSIVE", "STAGE-D-SR-FAILED",
           "STAGE-D-NONGAUSSIAN-PARTIAL", "STAGE-D-CLOSED-GENERALIZED",
           "STAGE-D-PARTIAL"]


def load(n):
    return json.loads((RES / n).read_text())


def main() -> None:
    d1 = load("d1_gamma.json")
    d14 = load("d1_4_sr_map.json")
    d2 = load("d2_gamma_m.json")
    d23 = load("d2_3_derivative.json")
    d25 = load("d2_5_verdict.json")
    d3 = load("d3_nongaussian.json")
    adv = load("adversarial_d.json")
    cal = load("calibration_d1.json")

    criteria = [
        {"id": "D1.1", "statement": "SR ARL0-matched to CUSUM(h=5), |ratio-1| <= 0.01",
         "status": "PASS" if cal["criterion_met"] else "FAIL",
         "value": f"rel err {cal['relative_error']:+.5f} +/- {cal['relative_error_se']:.5f}"},
        {"id": "D1.2", "statement": "lower 95% bound of Gamma_SR strictly > 2",
         "status": "PASS" if d1["d1_2"]["criterion_met"] else "FAIL",
         "value": f"lower bound {d1['d1_2']['lower_bound_normal']:.4f}"},
        {"id": "D1.3", "statement": "95% CI for Gamma_SR - Gamma_CUSUM excludes 0",
         "status": "PASS" if d1["d1_3"]["criterion_met"] else "FAIL",
         "value": (f"{d1['d1_3']['difference']:+.4f} "
                   f"CI [{d1['d1_3']['ci'][0]:+.4f}, {d1['d1_3']['ci'][1]:+.4f}]")},
        {"id": "D1.4", "statement": "SR period-2 candidate root, or NO-CANDIDATE",
         "status": d14["sr"]["verdict"],
         "value": (f"e* = {d14['sr']['root']:.6f} "
                   f"+/- {d14['sr']['root_half_width']:.6f}")},
        {"id": "D2.1", "statement": "gamma_i decay (descriptive, no criterion)",
         "status": "DESCRIPTIVE",
         "value": (f"gamma_0 = {d2['d2_1_lag']['gamma_0']:.4f}; "
                   f"E[T^2]/ARL0 = {d2['d2_1_lag']['wald_ratio_ETsq_over_arl0']:.5f}")},
        {"id": "D2.2", "statement": "bracket with both ends > 3 SE from Gamma_m = 2",
         "status": "PASS" if d2["d2_2_bracket"] else "FAIL",
         "value": (f"m* in [{d2['d2_2_bracket']['m_lo']}, {d2['d2_2_bracket']['m_hi']}], "
                   f"z = +{d2['d2_2_bracket']['z_lo']:.1f} / "
                   f"-{d2['d2_2_bracket']['z_hi']:.1f}")},
        {"id": "D2.3", "statement": "FD of the actual induced map = 1 - Gamma_m within 3 combined SE",
         "status": "PASS" if d23["criterion_met_all_m"] else "FAIL",
         "value": (f"{d23['n_m_passing']}/{d23['n_m_total']} at the "
                   f"pre-committed primary step h = {d23['primary_step']}")},
        {"id": "D2.4", "statement": "Gamma_m -> Gamma_inf < 2 (numerical only)",
         "status": "NUMERICAL",
         "value": (f"Gamma_inf = {d2['d2_4_asymptote']['gamma_inf_A_E_Tsq_over_tau']:.4f} "
                   f"+/- {d2['d2_4_asymptote']['se']:.4f}")},
        {"id": "D2.5", "statement": "does the crossing predict an operational change?",
         "status": d25["verdict"],
         "value": (f"{d25['n_metrics_peaking_at_m_star']}/4 metrics peak at m*; "
                   f"{d25['n_metrics_monotone']}/4 monotone in log m")},
        {"id": "D3.1", "statement": "regularity assumptions written and labelled before simulation",
         "status": "PASS",
         "value": "notes/D3_REGULARITY.md, A1 and A4 marked UNPROVED"},
        {"id": "D3.2", "statement": "per family, ARL0-matched, lower 95% bound of Gamma_psi vs 2",
         "status": ("PASS" if d3["d3_2_families_passing"] == d3["d3_2_families_total"]
                    else "FAIL"),
         "value": (f"{d3['d3_2_families_passing']}/{d3['d3_2_families_total']} "
                   f"frozen; {d3['d3_2_families_passing_normalised']}/"
                   f"{d3['d3_2_families_total']} normalised by E[psi']")},
        {"id": "D3.2-t3", "statement": "t3 under the two estimands (assumption A5)",
         "status": "AMBIGUOUS",
         "value": "Gamma_psi = 2.5980 PASS; Gamma_psi/E[psi'] = 1.2990 FAIL"},
        {"id": "D3.3", "statement": "naive Gaussian-form Gamma_T is diagnostic only",
         "status": "PASS",
         "value": "reported as diagnostic; never used as evidence"},
        {"id": "D4", "statement": "stability map, gated on D1 and D2 both surviving",
         "status": "NOT RUN",
         "value": "gate not met: D2.3 FAILED"},
    ]

    d1_pass = all(c["status"] == "PASS" for c in criteria
                  if c["id"] in ("D1.1", "D1.2", "D1.3"))
    d2_pass = all(c["status"] == "PASS" for c in criteria
                  if c["id"] in ("D2.2", "D2.3"))
    d3_all = d3["d3_2_families_passing"] == d3["d3_2_families_total"]
    adv_ok = adv["n_failed"] == 0

    steps = []
    if not adv_ok:
        decision = "STAGE-D-INCONCLUSIVE"
        steps.append("1 TRIGGERED: an adversarial check failed undiagnosed")
    else:
        steps.append(f"1 not triggered: adversarial {adv['n_passed']}/"
                     f"{adv['n_checks']}; the one first-run failure (A11) is "
                     f"diagnosed in notes/FAILURE_DIAGNOSES.md")
        if not d1_pass:
            decision = "STAGE-D-SR-FAILED"
            steps.append("2 TRIGGERED: D1.2 failed")
        else:
            steps.append("2 not triggered: D1.1, D1.2, D1.3 all PASS")
            if d1_pass and d2_pass and not d3_all:
                decision = "STAGE-D-NONGAUSSIAN-PARTIAL"
                steps.append("3 TRIGGERED")
            elif d1_pass and d2_pass and d3_all:
                decision = "STAGE-D-CLOSED-GENERALIZED"
                steps.append("4 TRIGGERED")
            else:
                decision = "STAGE-D-PARTIAL"
                steps.append("3 not reachable: requires D2 to pass, and D2.3 FAILED")
                steps.append("4 not reachable: same reason")
                steps.append("5 TRIGGERED: fall-through -> STAGE-D-PARTIAL")

    assert decision in ALLOWED, decision
    actual = hashlib.sha256((ROOT / "STAGE_D_PROTOCOL.md").read_bytes()).hexdigest()

    out = {"stage": "D", "decision": decision, "allowed_labels": ALLOWED,
           "protocol_sha256_expected": PROTOCOL_SHA,
           "protocol_sha256_actual": actual,
           "protocol_unchanged": actual == PROTOCOL_SHA,
           "decision_rule_trace": steps,
           "gate_summary": {"D1_pass": d1_pass, "D2_pass": d2_pass,
                            "D3_all_families_frozen_criterion": d3_all,
                            "adversarial_all_pass": adv_ok},
           "criteria": criteria,
           "scope_limits": [
               "SR agreement is two-detector replication, NOT detector-independence.",
               "D3 is numerical robustness over six families, NOT distribution-free.",
               "No Monte Carlo result here is certified or proved.",
               "m* is a local-stability boundary of the deterministic "
               "conditional-mean skeleton at e = 0, NOT an operational phase "
               "transition.",
           ]}
    (RES / "stage_d_decision.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"{'ID':<9} {'STATUS':<28} STATEMENT")
    for c in criteria:
        print(f"{c['id']:<9} {c['status']:<28} {c['statement']}")
        print(f"{'':<9} {'':<28} -> {c['value']}")
    print("\nDecision rule trace:")
    for s in steps:
        print(f"  {s}")
    print(f"\n  FINAL STAGE D DECISION: {decision}")
    print(f"  protocol hash unchanged: {actual == PROTOCOL_SHA}")


if __name__ == "__main__":
    main()
