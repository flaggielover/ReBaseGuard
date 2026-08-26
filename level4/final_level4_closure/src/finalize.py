#!/usr/bin/env python3
"""Generate the terminal machine decision and A-AD human closure record."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from audit import outputs as audit_outputs
from config import BASE, RESULTS, ROOT, canonical_json, load
from decision_engine import derive
from integrity import verify as verify_integrity
from reports import outputs as report_outputs


def claims() -> dict[str, Any]:
    return {
        "strongest_rigorous_result": (
            "The Lean-checked stopped-likelihood differentiation spine, outward-rounded "
            "Gamma_CUSUM enclosure above two, and certified deterministic-skeleton period-2 orbit."
        ),
        "strongest_general_theorem": (
            "For regular one-dimensional location families under explicit stopped change-of-measure, "
            "tail, integrability, and domination hypotheses, F'_rho(0)=rho(1-Gamma_f)."
        ),
        "strongest_cross_detector_result": (
            "CUSUM and the authoritative symmetric two-chart SR detector both support the stopped-score "
            "derivative identity; Gamma_SR > 2 remains confirmatory numerical evidence."
        ),
        "publication_safe_abstract": (
            "ReBaseGuard closes its internally frozen Level-4 research program: all 16 mandatory "
            "requirements are satisfied by the current evidence ledger, while one nonmandatory strong "
            "extension remains partial. The scoped evidence combines a rigorous CUSUM core, a Lean-checked "
            "stopped-likelihood derivative spine, an Arb-certified Gamma_CUSUM > 2 bound, a deterministic "
            "period-2 certificate, derivative theorems for m>1, symmetric two-chart SR, and regular location "
            "families, a D4 local-stability map, a frozen stability-aware reuse policy, semi-real external "
            "validation, and an N2 novelty-hygiene audit. The Gamma_m operational-crossing study has a valid "
            "negative result; P2 safety is regime-dependent, and the SR Arb certificate remains open."
        ),
        "resume_safe": {
            "one_line": "Completed ReBaseGuard's internally frozen Level-4 program through a reproducible 18-row evidence audit with all 16 mandatory requirements passing.",
            "two_bullets": [
                "Built and verified a sequential-monitoring research stack spanning Lean, Arb, deterministic stability, scoped cross-detector theory, and semi-real validation.",
                "Closed the frozen stability-aware-policy and operational-crossing questions while preserving negative results, historical failures, and optional rigor gaps.",
            ],
            "three_technical_bullets": [
                "Lean-checked the stopped-likelihood derivative spine and retained the Arb-certified Gamma_CUSUM > 2 enclosure plus deterministic period-2 certificate.",
                "Established scoped m>1, SR, and regular location-family derivative results and a protocol-specific D4 local-stability phase map.",
                "Verified the frozen lower-95%-bound P3 policy and semi-real validation rule; retained the negative crossing result, N2 novelty position, and open SR Arb certificate.",
            ],
        },
    }


def final_decision() -> dict[str, Any]:
    canonical = load(BASE / "requirements.json")
    evidence = load(RESULTS / "evidence_audit.json")
    ledger = load(RESULTS / "ledger_derivation.json")
    first = load(RESULTS / "adversarial_first.json")
    adversarial = load(RESULTS / "adversarial_final.json")
    reproduction = load(RESULTS / "reproduction.json")
    verification = load(RESULTS / "verification.json")
    integrity = verify_integrity()
    core_stable = all(path.exists() and path.read_text() == content
                      for path, content in {**audit_outputs(), **report_outputs()}.items())
    gates = {
        "all_mapped_closure_evidence_pass": evidence["all_campaigns_pass"] is True,
        "protected_history_intact": integrity["status"] == "INTACT",
        "canonical_artifacts_current": core_stable,
        "adversarial_A1_A32": adversarial["status"] == "PASS" and adversarial["passed"] == 32,
        "offline_byte_stable_reproduction": reproduction["status"] == "PASS"
            and reproduction["byte_stable"] is True and reproduction["offline"] is True,
        "level_1_3_verification": verification["level_1_3_status"] == "PASS"
            and verification["required_checks_skipped"] is False,
        "level_4_verification": verification["level_4_status"] == "PASS"
            and verification["evidence_drift"] is False,
    }
    mechanical = derive(canonical["requirements"], integrity_ok=integrity["status"] == "INTACT",
                        engineering_ok=all(gates.values()))
    if mechanical["current_verdict"] != "LEVEL-4-CLOSED":
        raise ValueError(f"terminal closure gates did not yield CLOSED: {gates}, {mechanical}")
    if mechanical["current_counts"] != ledger["counts"] or mechanical["mandatory_counts"] != ledger["mandatory_counts"]:
        raise ValueError("final mechanical counts disagree with canonical ledger derivation")
    changed = [row for row in canonical["requirements"] if row["changed_since_stage_f"]]
    blockers = [row for row in canonical["requirements"] if row["current_blocking"]]
    return {
        "schema": "rebaseguard.final-level4-closure-decision.v1",
        "generator_owned": True,
        "audit_name": "FINAL FINAL GLOBAL LEVEL-4 CLOSURE RE-AUDIT",
        "mode": "AUDIT_DERIVATION_ONLY_NO_NEW_SCIENCE",
        "audit_status": "COMPLETE",
        "audit_start_head": canonical["audit_start_head"],
        "historical_stage_f_verdict": canonical["historical_verdicts"]["historical_stage_f"],
        "protected_post_closure_verdict": canonical["historical_verdicts"]["protected_post_closure"],
        "previous_final_global_reaudit_verdict": canonical["historical_verdicts"]["previous_final_global"],
        "current_verdict": mechanical["current_verdict"],
        "current_counts": mechanical["current_counts"],
        "mandatory_counts": mechanical["mandatory_counts"],
        "original_requirement_count": mechanical["original_requirement_count"],
        "mandatory_requirement_count": mechanical["mandatory_requirement_count"],
        "mandatory_blockers": blockers,
        "nonmandatory_partial_ids": ledger["nonmandatory_partial_ids"],
        "remaining_open_nonblockers": canonical["open_nonblockers"],
        "requirements": canonical["requirements"],
        "status_transitions": changed,
        "closure_campaigns": evidence["campaigns"],
        "historical_negative_and_unfavorable_results": evidence["negative_and_unfavorable_history"],
        "decision_rule_trace": [*ledger["mechanical_trace"], *[
            f"engineering gate {name} -> {'PASS' if passed else 'FAIL'}"
            for name, passed in gates.items()
        ], f"current verdict -> {mechanical['current_verdict']}"],
        "engineering_gates": gates,
        "protected_history": integrity,
        "verification": verification,
        "adversarial": {
            "first": {"status": first["status"], "passed": first["passed"], "total": first["total"]},
            "final": {"status": adversarial["status"], "passed": adversarial["passed"], "total": adversarial["total"]},
        },
        "reproduction": reproduction,
        "claim_boundary": {
            "Gamma_CUSUM": "ARB-CERTIFIED ABOVE TWO",
            "Gamma_SR_gt_2": "CONFIRMATORY NUMERICAL",
            "SR_GAMMA_CERTIFIED": "NOT AWARDED; OPTIONAL ARB CERTIFICATE OPEN",
            "D4": "PROTOCOL-SPECIFIC DETERMINISTIC LOCAL-STABILITY MAP",
            "external_validation": "SEMI-REAL; P2 SAFETY REGIME-DEPENDENT",
            "novelty": "N2 PARTIAL-OVERLAP-FOUND-CLAIMS-NARROWED",
            "operational_crossing": "VALID NEGATIVE RESULT UNDER FROZEN PROTOCOL",
        },
        "claims": claims(),
        "level4_campaign_status": "CLOSED",
        "further_scientific_closure_campaign_required": False,
        "optional_remaining_work": [
            "publication preparation", "independent human review", "repository release/tagging",
            "paper/preprint drafting", "presentation/defense materials", "future Level-4+ research",
        ],
    }


def requirement_table(decision: dict[str, Any]) -> str:
    lines = [
        "| ID | Requirement | Class | Stage F | Previous final | Current | Blocks |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in decision["requirements"]:
        lines.append(
            f"| {row['id']} | {row['requirement']} | {row['classification']} | "
            f"{row['stage_f_status']['label']} | {row['previous_final_audit_status']} | "
            f"**{row['current_status']}** | {'YES' if row['current_blocking'] else 'NO'} |"
        )
    return "\n".join(lines)


def transition_table(decision: dict[str, Any]) -> str:
    lines = ["| ID | Stage F | Current | Campaign |", "|---|---|---|---|"]
    for row in decision["status_transitions"]:
        lines.append(f"| {row['id']} | {row['stage_f_status']['label']} | **{row['current_status']}** | `{row['transition_campaign']}` |")
    return "\n".join(lines)


def final_report(decision: dict[str, Any]) -> str:
    counts = decision["current_counts"]
    mandatory = decision["mandatory_counts"]
    resume = decision["claims"]["resume_safe"]
    optional = "\n".join(f"- {item}" for item in decision["optional_remaining_work"])
    blockers = "None. All 16 mandatory requirements are PASS."
    open_item = decision["remaining_open_nonblockers"][0]
    return f"""# Final Level-4 closure re-audit

## A. CURRENT FINAL GLOBAL VERDICT

> **`{decision['current_verdict']}`**

This verdict is mechanically derived from the canonical rows and engineering gates.

## B. Historical Stage-F verdict

`{decision['historical_stage_f_verdict']}` — preserved unchanged.

## C. Previous Final Global Re-audit verdict

`{decision['previous_final_global_reaudit_verdict']}` — preserved unchanged. The protected earlier post-closure audit is also `{decision['protected_post_closure_verdict']}`.

## D. Current 18-row counts

{counts['PASS']} PASS · {counts['PARTIAL']} PARTIAL · {counts['FAIL']} FAIL · {counts['OPEN']} OPEN.

## E. Mandatory counts

{mandatory['PASS']} PASS · {mandatory['PARTIAL']} PARTIAL · {mandatory['FAIL']} FAIL · {mandatory['OPEN']} OPEN, of {decision['mandatory_requirement_count']}.

## F. Full 18-row requirement table

{requirement_table(decision)}

## G. Final status transitions

{transition_table(decision)}

L4R-12 is deliberately split: its scientific result remains negative, while the completed investigational requirement becomes PASS.

## H. L4R-06 mapping

`L4R06-POLICY-CLOSED` maps to original L4R-06 PASS. The frozen policy is `rho_P3(m)=min(1, 0.8*rho_c,L95(m))`, with reuse levels 0.053642, 0.245418, 0.781994, and 1.000000 for m=1,20,70,100. Historical C6 remains FAILED and Stage C remains `STAGE-C-PARTIAL`. P2's descriptive advantages at m=70 and m=100, P3=P1 at saturated m=100, and the two secondary epsilon=0.05 failures remain visible.

## I. L4R-12 mapping

`L4R12-CLOSED-NEGATIVE-RESULT` maps to original L4R-12 PASS under its frozen investigational semantics. Stage D brackets the crossing at [50,75] with interpolation 72.189259; D4 independently brackets it at [70,72] with interpolation 71.419386. Across 20,000 replicates, 0/4 metrics peak at the crossing and 4/4 are monotone in log m. Historical D2.5 remains `MATHEMATICAL, NOT OPERATIONAL`; no universal no-effect claim follows.

## J. L4R-13 remaining partial extension

L4R-13, Non-Gaussian robustness, remains `PARTIAL`. It is a nonmandatory `STRONG_EXTENSION` and does not block the frozen closure rule.

## K. Remaining mandatory blockers

{blockers}

## L. Remaining optional/open items

`{open_item['id']}` remains `{open_item['status']}`: {open_item['reason']}

## M. SR Arb status

The SR derivative theorem is CLOSED and Gamma_SR > 2 is CONFIRMATORY NUMERICAL. The rigorous SR local-instability Arb certificate remains OPEN. **LEVEL-4-CLOSED does NOT imply SR-GAMMA-CERTIFIED.**

## N. D4 interpretation

D4 is a protocol-specific deterministic local-stability map, not proof of an abrupt stochastic operational phase transition.

## O. External-validation synthesis

V3 closes L4R-15 with three supporting tasks against two required. Stage E remains 0/3, V2 remains 1/3, V3 Route B remains unfavorable on both tasks, and P2 safety remains regime-dependent.

## P. Novelty synthesis

L4R-16 closes at N2: `PARTIAL-OVERLAP-FOUND-CLAIMS-NARROWED`. This is a scoped hygiene conclusion, not absolute novelty or priority.

## Q. Stability-aware policy synthesis

The frozen P3 policy uses 80% of the lower 95% D4 confidence bound, clipped at one. It satisfies the precommitted primary H6 family without tuning the safety factor after outcomes.

## R. Negative operational-crossing synthesis

The mathematical Gamma_m crossing does not produce a detected operational transition under the frozen monitored metrics and protocol. This completed negative answer closes the research requirement without changing the scientific result into a positive transition or a universal no-effect theorem.

## S. Strongest rigorous result

{decision['claims']['strongest_rigorous_result']}

## T. Strongest general theorem

{decision['claims']['strongest_general_theorem']}

## U. Strongest cross-detector result

{decision['claims']['strongest_cross_detector_result']}

## V. Publication-safe final abstract

{decision['claims']['publication_safe_abstract']}

## W. Resume-safe final claims

One line: {resume['one_line']}

Two bullets:

{chr(10).join(f'- {item}' for item in resume['two_bullets'])}

Three technical bullets:

{chr(10).join(f'- {item}' for item in resume['three_technical_bullets'])}

## X. Prohibited claims

Do not claim universal validity or safety, production proof/deployment, distribution-free or detector-independent results, absolute novelty or priority, SR rigorous certification, or a proved operational phase transition. See `CLAIM_FIREWALL.md`.

## Y. Verification totals

Both authoritative commands passed with no required skips, unexpected Lean axioms, sorry/admit, or evidence drift. Current distinct checks: {decision['verification']['current_distinct_checks']}; terminal focused tests: {decision['verification']['terminal_audit_focused_checks']}.

## Z. Adversarial first/final

First run: {decision['adversarial']['first']['passed']}/{decision['adversarial']['first']['total']} {decision['adversarial']['first']['status']}. Final run: {decision['adversarial']['final']['passed']}/{decision['adversarial']['final']['total']} {decision['adversarial']['final']['status']}.

## AA. Reproduction command

`bash level4/final_level4_closure/reproduce.sh`

## AB. Protected-history confirmation

`{decision['protected_history']['status']}`: {decision['protected_history']['trees_verified']} protected trees and {decision['protected_history']['files_verified']} load-bearing files verified against the audit baseline. All three historical global verdicts remain `LEVEL-4-PARTIAL`.

## AC. Git commit/push

The terminal closure artifacts are intended for one final meaningful closure commit followed by a fast-forward push to `origin/main`; the immutable starting state is recorded in `starting_git.json`.

## AD. FINAL CAMPAIGN STATE

CURRENT LEVEL-4 CAMPAIGN: CLOSED

No further Level-4 scientific closure campaign is required.

Remaining work is optional:

{optional}
"""


def adversarial_report() -> str:
    first = load(RESULTS / "adversarial_first.json")
    final = load(RESULTS / "adversarial_final.json")
    final_by = {row["id"]: row for row in final["checks"]}
    lines = [
        "# Terminal adversarial audit", "",
        f"First run: **{first['passed']}/{first['total']} {first['status']}**. "
        f"Final run: **{final['passed']}/{final['total']} {final['status']}**.", "",
        "| ID | Attack | First | Final | Final evidence |", "|---|---|---|---|---|",
    ]
    for before in first["checks"]:
        after = final_by[before["id"]]
        lines.append(f"| {before['id']} | {before['name']} | {'PASS' if before['passed'] else 'FAIL'} | {'PASS' if after['passed'] else 'FAIL'} | {after['detail']} |")
    lines += ["", "Only missing engineering records failed initially; no scientific rule was weakened.", ""]
    return "\n".join(lines)


def progress_capsule(decision: dict[str, Any]) -> str:
    return f"""# Terminal progress capsule

| Field | Value |
|---|---|
| Step | 12 / 12 |
| Gate | terminal closure complete |
| Original ledger | verified, 18 rows |
| L4R-06 mapping | PASS |
| L4R-12 mapping | PASS |
| Mandatory PASS | {decision['mandatory_counts']['PASS']}/16 |
| Nonmandatory partial | {decision['current_counts']['PARTIAL']} |
| Current derived verdict | {decision['current_verdict']} |
| Focused tests | {decision['verification']['terminal_audit_focused_checks']} PASS |
| Adversarial | {decision['adversarial']['first']['passed']}/32 first; {decision['adversarial']['final']['passed']}/32 final |
| Protected history | {decision['protected_history']['status']} |
| Reproducer | {decision['reproduction']['status']}, offline, byte-stable |
| Full verifier | {decision['verification']['status']} |
| Git | final closure commit/push gate follows artifact generation |
| Remaining | optional work only |
"""


def outputs() -> dict[Path, str]:
    decision = final_decision()
    return {
        RESULTS / "final_decision.json": canonical_json(decision),
        BASE / "FINAL_REPORT.md": final_report(decision),
        BASE / "ADVERSARIAL_AUDIT.md": adversarial_report(),
        BASE / "PROGRESS_CAPSULE.md": progress_capsule(decision),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    generated = outputs()
    for path, content in generated.items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if stale:
        print("stale terminal decision/report artifacts: " + ", ".join(stale))
        return 1
    verdict = load(RESULTS / "final_decision.json")["current_verdict"] if args.check else "LEVEL-4-CLOSED"
    print(f"terminal final decision: {verdict}" + (" byte-stable" if args.check else " generated"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
