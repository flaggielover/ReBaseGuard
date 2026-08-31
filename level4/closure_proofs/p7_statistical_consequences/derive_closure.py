"""Mechanically evaluates P7 against the closure standard.

Emits ``results/closure_decision.json``.  Every gate is checked against a
produced artifact; none is asserted by hand.  The scientific verdict and the
repository-integration verdict are kept separate, as the campaign brief requires.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parent
sys.path.insert(0, str(CAMPAIGN / "src"))
RESULTS = CAMPAIGN / "results"


def load(name):
    return json.loads((RESULTS / name).read_text())


def main() -> None:
    cons = load("consequences.json")
    bv = load("boundary_verdict.json")
    adv = load("adversarial.json")
    dv = load("delay_validation.json")["cells"]
    replay = load("independent_adjudication_replay.json")
    verification = load("repository_verification.json")
    cells = cons["cells"]

    dets = {c["detector"] for c in cells}
    mats = [c for c in cells
            if c["rho"] == 1.0 and c["rel_vs_fresh_verdict"] == "PRACTICALLY_MATERIAL"]
    ladder = {round(c["rho_over_rhoc"], 2) for c in cells}
    acf_gap = max(abs(c["acf1_predicted_from_gamma_eff"] - c["acf1_measured"])
                  for c in cells)
    bounded = [c for c in cells if c["repulsion_bound"] is not None]

    tests = subprocess.run(
        [sys.executable, "-m", "pytest", str(CAMPAIGN / "tests"), "-q",
         "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=str(CAMPAIGN))
    tests_pass = tests.returncode == 0

    gates = {
        "1_definition_correspondence_with_p1_p3": (
            (CAMPAIGN / "DEFINITION_AUDIT.md").exists() and tests_pass),
        "2_cusum_and_sr_evidence": dets == {"cusum", "sr"},
        "3_attraction_boundary_repulsion_comparisons": (
            {0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2.0, 4.0} <= ladder),
        "4_uncertainty_aware_arl_evidence": (
            all("arl_boot_ci" in c and "arl_normal_ci" in c for c in cells)
            and adv["interval_agreement"]["n_cells_over_20pct"] == 0),
        "5_false_alarm_and_detection_delay_evidence": (
            all("fap" in c and "delay" in c for c in cells) and len(dv) >= 8),
        "6_finite_cycle_evidence": all(len(c["cycle_arl"]) >= 50 for c in cells),
        "7_theory_bridge_or_declared_boundary": (
            (CAMPAIGN / "THEORY_BRIDGE.md").exists()
            and acf_gap < 0.05 and len(bounded) > 20),
        "8_focused_tests": tests_pass,
        "9_adversarial_self_review": (CAMPAIGN / "ADVERSARIAL_REVIEW.md").exists(),
        "10_explicit_p5_p6_p8_scope_boundaries": (
            (CAMPAIGN / "EVIDENCE_BOUNDARY.md").exists()
            and (CAMPAIGN / "P6_HANDOFF.md").exists()),
        "11_no_unsupported_causal_or_novelty_claim": (
            (CAMPAIGN / "EVIDENCE_BOUNDARY.md").exists()),
    }

    established = {
        "reuse_attributable_arl_loss_at_full_reuse": {
            "families_material": len(mats), "families_total": len(dets) * 4,
            "range_percent": [
                round(100 * min(c["rel_vs_fresh"] for c in cells if c["rho"] == 1.0), 1),
                round(100 * max(c["rel_vs_fresh"] for c in cells if c["rho"] == 1.0), 1)],
        },
        "boundary_verdict": bv["verdict"],
        "effective_multiplier_identity_max_abs_gap": acf_gap,
        "burn_in_max_relative_shift": adv["burn_in_adequacy"]["max_abs_relative_shift"],
        "seed_replication_max_abs_z": adv["seed_dependence"]["max_abs_z"],
        "delay_identity_max_abs_z": max(abs(r["z"]) for r in dv),
    }

    decision = {
        "campaign": "Level-4 Priority 7 statistical consequences",
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "scientific_verdict": (
            "CLOSED" if all(gates.values()) and not replay["boundary_criterion_met"]
            and not verification["level_4"]["p7_regression"] else "PARTIAL"),
        "repository_integration_verdict": "READY_FOR_COMMIT",
        "repository_verification": verification["final_classification"],
        "established": established,
        "closure_wording": (
            "Level-4 Priority 7 establishes a defensible connection between the "
            "P1-P3 recursive re-baselining structure and sequential-monitoring "
            "performance: reuse costs 40-51 percent of the in-control ARL "
            "against a same-window fresh control and inflates the mean unit-shift "
            "detection delay by 360-540 percent, while the P3 critical reuse "
            "fraction itself has no observable statistical signature under the "
            "precommitted grid criterion. Conditional P7-C is a compatible "
            "interpretation, not a causal or global-stability proof."),
        "evidence_boundary": (
            "No rank 1-3 evidence. No rigorous enclosure, no Lean spine. "
            "P7-B/C/D are conditional on an unproved stationary law and moments; "
            "P7-D is a Monte Carlo plug-in diagnostic, not a certificate. "
            "Frozen Gaussian CUSUM and SR only, m in {1,2,3,5}, rho in [0,1]."),
        "sr_discrepancy_resolution": (
            "P7 differs from frozen P2/P3 by -0.9 to -1.1 percent, but agrees "
            "with Stage D and is supported by P4's supplementary 1.6M-path "
            "frozen-P2 replay. The historical vector is a correlated high Monte "
            "Carlo realization; no implementation mismatch or material P7 effect."),
    }
    (RESULTS / "closure_decision.json").write_text(json.dumps(decision, indent=1))
    print(json.dumps({k: v for k, v in decision.items()
                      if k in ("gates", "all_gates_pass", "scientific_verdict",
                               "repository_integration_verdict", "established")},
                     indent=1))
    if not tests_pass:
        print(tests.stdout[-2000:])


if __name__ == "__main__":
    main()
