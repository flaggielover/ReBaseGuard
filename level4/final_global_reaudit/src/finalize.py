#!/usr/bin/env python3
"""Create the final machine decision and human-readable closure reports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from config import BASE, RESULTS, ROOT, load
from integrity import verify as verify_integrity


def final_decision() -> dict[str, Any]:
    derived = load(RESULTS / "derived_decision.json")
    evidence = load(RESULTS / "evidence_audit.json")
    adversarial = load(RESULTS / "adversarial_final.json")
    reproduction = load(RESULTS / "reproduction.json")
    verification = load(RESULTS / "verification.json")
    integrity = verify_integrity()
    gates = {
        "derived_evidence_audit": derived["evidence_audit_status"] == "PASS" and evidence["all_campaigns_pass"],
        "protected_history": integrity["status"] == "INTACT",
        "adversarial_26_of_26": adversarial["status"] == "PASS" and adversarial["passed"] == 26,
        "offline_byte_stable_reproduction": reproduction["status"] == "PASS" and reproduction["byte_stable"] and reproduction["offline"],
        "level_1_3_verification": verification["level_1_3_status"] == "PASS",
        "level_4_verification": verification["level_4_status"] == "PASS" and verification["current_distinct_checks"] == 1139,
    }
    if not all(gates.values()):
        raise ValueError(f"final audit engineering gate failed: {gates}")
    return {
        "schema": "rebaseguard.level4-final-global-decision.v1",
        "audit_metadata": {
            "audit_name": "FINAL GLOBAL LEVEL-4 RE-AUDIT AND PROJECT CLOSURE",
            "audit_date": "2026-08-24",
            "deterministic_audit_timestamp": "2026-08-24T00:00:00+09:00",
            "audited_commit": derived["audit_metadata"]["audited_commit"],
            "mode": "AUDIT_DERIVATION_ONLY_NO_NEW_SCIENCE",
        },
        "audit_status": "COMPLETE",
        "historical_stage_f_verdict": derived["historical_stage_f_verdict"],
        "previous_post_closure_verdict": derived["previous_post_closure_verdict"],
        "current_verdict": derived["current_verdict"],
        "original_requirement_count": derived["original_requirement_count"],
        "mandatory_requirement_count": derived["mandatory_requirement_count"],
        "current_counts": derived["current_counts"],
        "mandatory_counts": derived["mandatory_counts"],
        "exact_remaining_blockers": derived["mandatory_blockers"],
        "exact_remaining_open_nonblockers": derived["remaining_open_nonblockers"],
        "rows_changed_since_previous_reaudit": derived["rows_changed_since_previous_reaudit"],
        "later_closure_campaigns_used": derived["later_closure_campaigns_used"],
        "protected_history": integrity,
        "verification": verification,
        "adversarial": {"status": adversarial["status"], "passed": adversarial["passed"],
                         "total": adversarial["total"], "first_run": "24/26 FAIL"},
        "reproducer": reproduction,
        "engineering_gates": gates,
        "claim_boundary_summary": {
            "theorem": "Scoped human theorems and conditional Lean spines are distinguished.",
            "certificate": "Gamma_CUSUM is Arb-certified; Gamma_SR is not.",
            "numerical": "Gamma_SR > 2 remains confirmatory numerical.",
            "d4": "Deterministic local stability, not an operational phase-transition proof.",
            "external_validation": "L4R-15 closed under its frozen counting rule; P2 remains regime-dependent.",
            "novelty": "N2 scoped search conclusion, not absolute novelty or priority.",
        },
        "sr_boundary": derived["sr_boundary"],
        "historical_statuses_preserved": derived["historical_statuses_preserved"],
        "remaining_partial_negative_assessment": derived["remaining_partial_negative_assessment"],
        "claims": derived["claims"],
        "requirements": derived["requirements"],
        "decision_rule_trace": derived["decision_rule_trace"],
        "level4_campaign_status": "REMAINS_OPEN_PARTIAL",
        "exact_next_action": "Resolve only the frozen L4R-06 and L4R-12 mandatory non-PASS blockers in a separately authorized future campaign; do not start that work in this audit.",
    }


def table(decision: dict[str, Any]) -> str:
    lines = [
        "| ID | Requirement | Class | Stage F | Previous re-audit | Current | Changed now | Blocks closure |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in decision["requirements"]:
        lines.append(
            f"| {row['id']} | {row['requirement']} | {row['classification']} | "
            f"{row['stage_f']['label']} | {row['previous_reaudit_status']} | "
            f"**{row['current_status']}** | {'YES' if row['changed_since_previous_reaudit'] else 'NO'} | "
            f"{'YES' if row['blocks_closure'] else 'NO'} |"
        )
    return "\n".join(lines)


def final_report(decision: dict[str, Any]) -> str:
    counts, mandatory = decision["current_counts"], decision["mandatory_counts"]
    blockers = "\n".join(
        f"- **{row['id']} — {row['requirement']}**: {row['current_status']}. {row['reason']}"
        for row in decision["exact_remaining_blockers"]
    )
    changes = "\n".join(
        f"- {row['id']} — {row['requirement']}: {row['current_status']} via `{row['campaign']}`."
        for row in decision["rows_changed_since_previous_reaudit"]
    )
    return f"""# Final global Level-4 re-audit

## A. Final global verdict

> **`{decision['current_verdict']}`**

The later D4, external-validation, and novelty campaigns close the previous
FAIL/OPEN blockers, but the original fallback taxonomy requires every mandatory
row to be PASS. L4R-06 and L4R-12 remain mandatory non-PASS rows, so CLOSED is
not available. `LEVEL-4-CLOSED-WITH-LIMITATIONS` remains unauthorized.

## B. Historical Stage-F verdict

`{decision['historical_stage_f_verdict']}` — unchanged historical fact.

## C. Previous post-closure verdict

`{decision['previous_post_closure_verdict']}` — unchanged historical fact.

## D. Current requirement counts

{counts['PASS']} PASS · {counts['PARTIAL']} PARTIAL/NEGATIVE · {counts['FAIL']} FAIL · {counts['OPEN']} OPEN.

## E. Mandatory requirement counts

{mandatory['PASS']} PASS · {mandatory['PARTIAL']} PARTIAL/NEGATIVE · {mandatory['FAIL']} FAIL · {mandatory['OPEN']} OPEN, of {decision['mandatory_requirement_count']}.

## F. Requirement-by-requirement table

{table(decision)}

## G. Rows changed since the previous re-audit

{changes}

## H. Remaining partial/negative rows

{blockers}

- **L4R-13** is a nonmandatory STRONG_EXTENSION partial and does not block
  closure. The exact provenance analysis is in `REQUIREMENT_LEDGER.md`.

## I–J. Remaining OPEN items and SR Arb status

No original ledger row is currently OPEN. The rigorous SR local-instability
Arb certificate remains an explicit OPEN optional rigor upgrade outside L4R-10.
Level 4 closure would not imply `SR-GAMMA-CERTIFIED`.

## K. D4 interpretation

D4 closes L4R-11 with `F'_{{rho,m}}(0)=rho(1-GammaTilde_m)`. This is a
protocol-specific deterministic local-stability map, not proof of an abrupt
stochastic operational transition. Historical D2.5 remains `MATHEMATICAL, NOT
OPERATIONAL`.

## L. External-validation synthesis

L4R-15 is closed by three independent successful tasks against a frozen
requirement of two: V2 Household plus V3 MetroPT-3 and Online Retail II. Stage E
remains 0/3, V2 remains 1/3, V3 Route B remains unfavorable, and P2 remains
regime-dependent.

## M. Novelty positioning

Novelty verification closes L4R-16 at N2: partial overlap found and claims
narrowed. Within the documented search scope, no work was identified that
combines the same alarm-stopped next-reference mechanism with the reported
derivative and stability results. This is not absolute novelty or priority.

## N–Q. Scientific extrema

- **Strongest rigorous result:** {decision['claims']['strongest_rigorous_result']}
- **Strongest general theorem:** {decision['claims']['strongest_general_theorem']}
- **Strongest cross-detector result:** {decision['claims']['strongest_cross_detector_result']}
- **Most important negative result:** {decision['claims']['most_important_negative_result']}

## R. Publication-safe claim

{decision['claims']['publication_safe_summary']}

## S. Resume-safe claim

{decision['claims']['resume_safe_summary']}

## T. Prohibited claims

See `CLAIM_FIREWALL.md`. Absolute novelty, priority, universal safety,
production readiness, detector independence, SR certification, and an
operational phase transition are not supported.

## U–W. Verification, adversarial, and reproduction

- distinct authoritative checks: {decision['verification']['current_distinct_checks']}/{decision['verification']['expected_distinct_checks']}
- focused final-audit tests: {decision['verification']['final_audit_focused_checks']}/36
- adversarial: first 24/26 preserved; final {decision['adversarial']['passed']}/{decision['adversarial']['total']}
- reproduction: {decision['reproducer']['status']}, offline and byte-stable
- command: `bash level4/final_global_reaudit/reproduce.sh`

## X. Protected-history confirmation

`{decision['protected_history']['status']}`: {decision['protected_history']['trees_verified']} trees and {decision['protected_history']['files_verified']} historical files verified.

## Y–Z. Project state and exact next action

The current Level-4 research campaign remains open/partial. {decision['exact_next_action']}
"""


def adversarial_report() -> str:
    first = load(RESULTS / "adversarial_first.json")
    final = load(RESULTS / "adversarial_final.json")
    final_by = {row["id"]: row for row in final["checks"]}
    lines = [
        "# Final global re-audit adversarial audit", "",
        f"First run: **{first['passed']}/{first['total']} {first['status']}**. "
        f"Final run: **{final['passed']}/{final['total']} {final['status']}**.", "",
        "| ID | Attack | First | Final | Final evidence |", "|---|---|---|---|---|",
    ]
    for before in first["checks"]:
        after = final_by[before["id"]]
        lines.append(f"| {before['id']} | {before['name']} | "
                     f"{'PASS' if before['passed'] else 'FAIL'} | "
                     f"{'PASS' if after['passed'] else 'FAIL'} | {after['detail']} |")
    lines += ["", "No scientific gate, classification, threshold, mapping, or historical status was weakened between runs.", ""]
    return "\n".join(lines)


def current_status(decision: dict[str, Any]) -> str:
    counts = decision["current_counts"]
    return f"""# Current Level-4 status

> **`{decision['current_verdict']}`**

- Historical Stage F: `{decision['historical_stage_f_verdict']}`.
- Previous post-closure re-audit: `{decision['previous_post_closure_verdict']}`.
- Current ledger: {counts['PASS']} PASS / {counts['PARTIAL']} PARTIAL / {counts['FAIL']} FAIL / {counts['OPEN']} OPEN.
- Mandatory blockers: L4R-06 and L4R-12, both PARTIAL/non-PASS.
- SR Arb certificate: OPEN optional rigor upgrade; not an original-row blocker.
- Exact next action: {decision['exact_next_action']}
"""


def outputs() -> dict[Path, str]:
    decision = final_decision()
    report = final_report(decision)
    return {
        RESULTS / "final_decision.json": json.dumps(decision, indent=2, sort_keys=True) + "\n",
        BASE / "FINAL_REPORT.md": report,
        BASE / "ADVERSARIAL_AUDIT.md": adversarial_report(),
        ROOT / "level4/reports/LEVEL_4_FINAL_GLOBAL_REAUDIT.md": report,
        ROOT / "level4/reports/LEVEL_4_CURRENT_STATUS.md": current_status(decision),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = outputs()
    stale = []
    for path, content in generated.items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if stale:
        print("stale final decision/report artifacts: " + ", ".join(stale))
        return 1
    verdict = json.loads(generated[RESULTS / "final_decision.json"])["current_verdict"]
    print(f"final global decision: {verdict}" + (" byte-stable" if args.check else " generated"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
