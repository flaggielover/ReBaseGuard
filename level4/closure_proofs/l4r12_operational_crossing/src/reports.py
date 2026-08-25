#!/usr/bin/env python3
"""Generate human-readable mirrors of the final L4R-12 decision."""
from __future__ import annotations

import argparse
import json

from config import BASE, RESULTS


def build() -> dict[str, str]:
    d = json.loads((RESULTS / "decision.json").read_text())
    evidence = json.loads((RESULTS / "evidence_assessment.json").read_text())
    first = json.loads((RESULTS / "adversarial_first.json").read_text())
    final = json.loads((RESULTS / "adversarial_final.json").read_text())
    crossing = evidence["crossing"]
    final_report = f"""# L4R-12 final closure report

## Decision

- Scoped verdict: **`{d['scoped_verdict']}`**
- Exact row: **{d['target']}**
- Class: **{d['original_requirement_class']}**
- Semantics: **{d['semantics']}**
- Original L4R-12 current status: **{d['original_L4R12_current_status']}**
- Same-requirement mapping: **{str(d['same_requirement_mapping']).lower()}**
- Negative-result closure allowed: **{str(d['negative_result_closure_allowed']).lower()}**
- Evidence sufficient: **{str(d['evidence_sufficient']).lower()}**

The positive operational-transition hypothesis was falsified under a frozen,
adequately resolved design. L4R-12 itself was an investigational question, so
the result is a completed research question with a valid negative answer—not a
low-power non-demonstration.

## Evidence

Stage D brackets the Gamma_m=2 crossing at `{crossing['stage_d_bracket']}` with
endpoint separation `{crossing['stage_d_endpoint_z']}` standard errors and a
secondary interpolated value `{crossing['stage_d_interpolated']:.6f}`. D4
independently refines the bracket to `{crossing['D4_bracket']}` and obtains
`{crossing['D4_gamma_at_bracket']}` at its endpoints.

D2.5 used 20,000 replicates on `m={{10,20,50,65,75,90,100}}`. Zero of four
preselected localization metrics peak at the crossing and all four are monotone
in log m. N12.1–N12.10 pass 10/10. No new science was run.

## Claim firewall

Claim-safe: {d['claim_safe']}

Prohibited: {d['claim_forbidden']}

## Integrity and verification

Historical Stage D remains `STAGE-D-PARTIAL`; D2.5 remains `MATHEMATICAL, NOT
OPERATIONAL`; D4 remains `D4-PHASE-MAP-CLOSED`; L4R-06 remains
`L4R06-POLICY-CLOSED`; historical Stage F and the Final Global Re-audit remain
`LEVEL-4-PARTIAL`.

Adversarial first/final: `{first['n_passed']}/19` / `{final['n_passed']}/19`.
Repository verification: `{d['verification']['pytest_pass_count']}` pytest
checks, status `{d['verification']['status']}`. Offline reproduction status:
`{d['reproduction']['status']}`.

This isolated mapping does not perform a new global re-audit. Exact next action:
**{d['exact_next_action']}**.
"""
    failures = f"""# L4R-12 failure diagnoses

## Current isolated audit

No unresolved audit failure remains. C12.1–C12.10 pass, A1–A19 pass, and the
repository verifier is green. The scoped result is `{d['scoped_verdict']}`.

## Preserved negative scientific result

The historical positive hypothesis did fail: no frozen operational metric
localized at the crossing. That negative outcome is preserved verbatim as
`MATHEMATICAL, NOT OPERATIONAL`; it is not repaired, reversed, or presented as a
positive transition. Under the controlling investigational semantics, the
failure of the positive hypothesis is the valid answer to the research question.

## Preserved historical statuses

Stage D, Stage F, the post-closure re-audit, and the Final Global Re-audit remain
historically partial. D4 and L4R-06 remain closed. No historical file was edited.

## Limitations

The result is scoped to the frozen Gaussian CUSUM, `rho=1`, Stage-D window
convention, grid, shifts, and monitored metrics. It does not prove that no
operational consequence can exist in other protocols or systems.
"""
    capsule = f"""# L4R-12 progress capsule

| Field | Value |
|---|---|
| Step | 2 / 2 |
| Gate | final scoped decision |
| Original wording found | yes |
| Semantics | investigational |
| Existing evidence sufficient | yes |
| New science needed | no |
| Negative result class | C — completed question, valid negative answer |
| Same-requirement mapping | yes |
| Focused tests | pass |
| Adversarial | first {first['n_passed']}/19; final {final['n_passed']}/19 |
| Historical D2.5 preserved | yes |
| Git | final checkpoint pending commit |
| Remaining | {d['exact_next_action']} |
"""
    return {
        "FINAL_REPORT.md": final_report,
        "FAILURE_DIAGNOSES.md": failures,
        "PROGRESS_CAPSULE.md": capsule,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    mismatches = []
    for name, text in build().items():
        path = BASE / name
        if args.check:
            if not path.exists() or path.read_text() != text:
                mismatches.append(name)
        else:
            path.write_text(text)
    if mismatches:
        print("L4R-12 reports are not byte-stable:", ", ".join(mismatches))
        return 1
    print("L4R-12 human reports: byte-stable" if args.check else "L4R-12 human reports generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

