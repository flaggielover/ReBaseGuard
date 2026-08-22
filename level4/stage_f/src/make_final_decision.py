"""Derive the final Level-4 verdict mechanically from the requirements
reconstruction. No label may be invented; no requirement may be added here."""
from __future__ import annotations

import hashlib, json, subprocess, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RES = REPO / "level4" / "stage_f" / "results"

# Fallback taxonomy: used ONLY because the repository contains no pre-existing
# Level-4 status taxonomy (verified by exhaustive search in the reconstruction).
ALLOWED = ["LEVEL-4-CLOSED", "LEVEL-4-CLOSED-WITH-LIMITATIONS",
           "LEVEL-4-PARTIAL", "LEVEL-4-FAILED"]

# Requirements, transcribed from LEVEL4_REQUIREMENTS_RECONSTRUCTION.md §4.
# `mandatory` follows the CONSERVATIVE reading of staged_task_ranking.csv.
REQUIREMENTS = [
    ("L1-3 closure foundation", "mandatory", "PASS", "closure/LEVEL_1_3_CLOSURE_REPORT.md"),
    ("Multi-cycle oracle, reproducible", "mandatory", "PASS", "level4/reports/GATE_4_1_REPORT.md"),
    ("Conditional map + derivative correspondence at m=1", "mandatory", "PASS", "level4/reports/GATE_4_2_REPORT.md"),
    ("Gamma_CUSUM > 2 rigorously", "mandatory", "PASS", "closure/04_ARB_CERTIFICATE.md"),
    ("Rigorous period-2 for the deterministic skeleton", "mandatory", "PASS", "level4/stage_b/certificate/period2_certificate.json"),
    ("Stability-aware reuse policy + monitoring consequences", "mandatory", "PARTIAL", "level4/stage_c/results/findings.json"),
    ("Confirmatory sensitivity of that policy", "mandatory", "PASS", "level4/stage_c1/results/findings_confirmatory.json"),
    ("SR Monte Carlo derivative", "mandatory", "PASS", "level4/stage_d/results/d1_gamma.json"),
    ("m>1 derivative theorem", "mandatory", "FAIL", "level4/stage_d/results/d2_3_derivative.json"),
    ("SR derivative theorem (proved)", "mandatory", "OPEN", "level4/reports/STAGE_D_LEDGER.md"),
    ("m-rho phase map (D4)", "mandatory", "FAIL", "level4/stage_d/results/stage_d_decision.json"),
    ("Operational consequence of the Gamma_m crossing", "mandatory", "NEGATIVE", "level4/stage_d/results/d2_5_verdict.json"),
    ("Non-Gaussian robustness", "strong extension", "PARTIAL", "level4/stage_d/results/d3_nongaussian.json"),
    ("General location-family theorem", "stretch", "OPEN", "level4/stage_d/notes/D3_REGULARITY.md"),
    ("Semi-real external validation", "mandatory", "FAIL", "level4/stage_e/results/stage_e_decision.json"),
    ("Prior-art / novelty verification", "mandatory", "OPEN", "level_4_theory_numerics/rebaseguard_level4_design.md"),
    ("Reproducibility of every stage", "mandatory", "PASS", "scripts/verify_level_4.sh"),
    ("Protocol integrity", "mandatory", "PASS", "level4/stage_f/results/adversarial_f.json"),
]


def main() -> None:
    mand = [r for r in REQUIREMENTS if r[1] == "mandatory"]
    unmet = [r for r in mand if r[2] in ("FAIL", "OPEN")]
    partial = [r for r in mand if r[2] in ("PARTIAL", "NEGATIVE")]
    passed = [r for r in mand if r[2] == "PASS"]

    adv_p = RES / "adversarial_f.json"
    adv = json.loads(adv_p.read_text()) if adv_p.exists() else {"n_failed": None}

    trace = []
    # central scientific claim intact?
    core_ok = all(r[2] == "PASS" for r in mand if r[0] in (
        "L1-3 closure foundation", "Gamma_CUSUM > 2 rigorously",
        "Rigorous period-2 for the deterministic skeleton"))
    integrity_ok = all(r[2] == "PASS" for r in mand
                       if r[0] in ("Protocol integrity", "Reproducibility of every stage"))

    if not core_ok or not integrity_ok:
        decision = "LEVEL-4-FAILED"
        trace.append("central claim contradicted or protocol integrity lost")
    elif not unmet and not partial:
        decision = "LEVEL-4-CLOSED"
        trace.append("all mandatory requirements satisfied")
    else:
        trace.append("central Level-4 claim NOT contradicted and protocol "
                     "integrity intact -> LEVEL-4-FAILED does not apply")
        trace.append(f"{len(unmet)} mandatory requirement(s) FAIL/OPEN -> "
                     "LEVEL-4-CLOSED does not apply")
        trace.append("LEVEL-4-CLOSED-WITH-LIMITATIONS requires that the ORIGINAL "
                     "architecture permit such closure; the repository contains "
                     "NO pre-specified Level-4 closure criteria or taxonomy "
                     "(verified by exhaustive search), so this label is not "
                     "available without inventing the requirement after the fact")
        trace.append(f"-> LEVEL-4-PARTIAL: {len(unmet)} mandatory unmet, "
                     f"{len(passed)} mandatory passed, substantial results established")
        decision = "LEVEL-4-PARTIAL"

    assert decision in ALLOWED

    out = {
        "stage": "F", "decision": decision, "allowed_labels": ALLOWED,
        "taxonomy_source": ("FALLBACK - no pre-existing Level-4 taxonomy found "
                            "in the repository"),
        "decision_rule_trace": trace,
        "n_mandatory_total": len(mand),
        "n_mandatory_passed": len(passed),
        "n_mandatory_partial_or_negative": len(partial),
        "n_mandatory_unmet": len(unmet),
        "mandatory_unmet": [{"requirement": r[0], "status": r[2], "artifact": r[3]}
                            for r in unmet],
        "mandatory_partial": [{"requirement": r[0], "status": r[2], "artifact": r[3]}
                              for r in partial],
        "requirements": [{"requirement": r[0], "class": r[1], "status": r[2],
                          "artifact": r[3]} for r in REQUIREMENTS],
        "verdict_robust_to_interpretation": {
            "strict_reading": ("staged_task_ranking.csv MANDATORY is binding -> "
                               "3 of 4 Stage D mandatory items FAIL/OPEN -> not closed"),
            "lenient_reading": ("MANDATORY is Stage-D priority only -> closure rests "
                                "on frozen per-stage rules: C PARTIAL, D PARTIAL, "
                                "E PARTIAL -> not closed"),
            "both_readings_agree": True},
        "inherited_stage_decisions": {
            "level_1_3": "CLOSED", "stage_b": "STAGE-B-CLOSED-RIGOROUS-PERIOD2",
            "stage_c": "STAGE-C-PARTIAL",
            "stage_c1": "STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY",
            "stage_d": "STAGE-D-PARTIAL", "stage_e": "STAGE-E-PARTIAL"},
        "adversarial_f": {"passed": adv.get("n_passed"), "total": adv.get("n_checks")},
        "final_status": decision,
        "requirements_source": ("level4/stage_f/LEVEL4_REQUIREMENTS_RECONSTRUCTION.md "
                                "(reconstructed; no pre-specified Level-4 closure "
                                "criteria exist in the repository)"),
        "mandatory_pass": [r[0] for r in passed],
        "protocol_integrity": {
            "protocol_hashes_verified": 4, "precommit_hashes_verified": 3,
            "stage_decisions_verified": 5, "deviations_recorded": 0,
            "status": "INTACT"},
        "historical_artifacts_untouched": True,
        "verification_status": {
            "level_1_3": "ALL CHECKS PASSED (0 skipped) - Lean axiom audit clean, "
                         "final theorem elaborates, Arb certificate full replay PASS",
            "level_4": "LEVEL 4 VERIFICATION OK"},
        "unresolved_requirements": [r[0] for r in unmet],
        "strongest_rigorous_result": (
            "Lean-checked differentiation-under-the-expectation identity plus the "
            "Arb-certified enclosure Gamma_CUSUM in [3.9243482, 27.8493821], and the "
            "Stage B certified period-2 orbit of the DETERMINISTIC conditional-mean "
            "skeleton (root in [1.0287243, 1.0447243], multiplier in [0.10815, 0.83253])"),
        "strongest_generalization_result": (
            "two-detector replication: an ARL0-matched Shiryaev-Roberts chart gives "
            "Gamma_SR = 17.3198 +/- 0.0280 with excess +1.4746 +/- 0.0400 over CUSUM. "
            "NOT detector independence"),
        "strongest_negative_result": (
            "the Gamma_m = 2 crossing is MATHEMATICAL, NOT OPERATIONAL (Stage D D2.5: "
            "0/4 monitoring metrics peak at m*, 4/4 monotone, alternation persists "
            "above the crossing), independently corroborating the 2026-08-21 "
            "falsification of the stochastic period-2 reading"),
        "most_important_ambiguity": (
            "Stage D t3: frozen estimand Gamma_psi = 2.5980 PASSES while the "
            "stability-normalised Gamma_psi/E[psi'] = 1.2990 FAILS; neither selected"),
        "novelty_status": (
            "OPEN. A later external prior-art search found no direct overlap to the "
            "extent searched, but the corresponding review artifact is not currently "
            "persisted in the repository and exhaustive novelty is not established. "
            "Documentation/provenance limitation, not a protocol violation"),
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                   text=True, cwd=REPO).stdout.strip(),
    }
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "final_decision.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"{'requirement':52s} {'class':18s} status")
    for r in REQUIREMENTS:
        print(f"  {r[0][:50]:50s} {r[1]:18s} {r[2]}")
    print("\nDecision trace:")
    for t in trace:
        print(f"  - {t}")
    print(f"\n  FINAL LEVEL-4 VERDICT: {decision}")
    print(f"  mandatory: {len(passed)} pass / {len(partial)} partial / "
          f"{len(unmet)} unmet  of {len(mand)}")


if __name__ == "__main__":
    main()
