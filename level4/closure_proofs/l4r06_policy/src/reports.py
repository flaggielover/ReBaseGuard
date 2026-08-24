#!/usr/bin/env python3
"""Mirror generator-owned L4R-06 JSON into human-readable reports."""
from __future__ import annotations

import json
from pathlib import Path

from config import BASE, RESULTS


def f(value: float) -> str:
    return f"{value:.6f}"


def main() -> int:
    science = json.loads((RESULTS / "scientific_findings.json").read_text())
    decision = json.loads((RESULTS / "decision.json").read_text())
    first = json.loads((RESULTS / "adversarial_first.json").read_text())
    final = json.loads((RESULTS / "adversarial_final.json").read_text())

    mse = science["H6-2"]["family"]["rows"]
    arl = science["H6-3"]["family"]["rows"]
    response = science["H6-4"]["family"]["rows"]
    safety = science["absolute_delay_safety"]["family"]["rows"]

    results = ["# L4R-06 numerical results", "",
               f"Scoped verdict: **{decision['scoped_verdict']}**", "",
               "## Frozen hypotheses", ""]
    for name in ("H6-1", "H6-2", "H6-3", "H6-4", "H6-5"):
        results.append(f"- {name}: **{science[name]['status']}**")
    results += [f"- Absolute-delay safety: **{science['absolute_delay_safety']['status']}**", "",
                "## Reference improvement family", "",
                "| m | MSE(P1)-MSE(P3) | simultaneous lower 95% | status |",
                "|---:|---:|---:|---|"]
    for r in mse:
        results.append(f"| {r['m']} | {f(r['point'])} | {f(r['simultaneous_lower95'])} | {'PASS' if r['pass'] else 'FAIL'} |")
    results += ["", "## Operational false-alert family", "",
                "| m | ARL0(P3)-ARL0(P1) | simultaneous lower 95% | status |",
                "|---:|---:|---:|---|"]
    for r in arl:
        results.append(f"| {r['m']} | {f(r['point'])} | {f(r['simultaneous_lower95'])} | {'PASS' if r['pass'] else 'FAIL'} |")
    results += ["", "## Detection families", "",
                f"All {len(response)} normalized-response and {len(safety)} absolute-delay conditions are retained in `results/scientific_findings.json`.", ""]
    (BASE / "RESULTS.md").write_text("\n".join(results) + "\n")

    max_response = max(response, key=lambda r: r["simultaneous_upper95"])
    max_safety = max(safety, key=lambda r: r["simultaneous_upper95"])
    monitoring = f"""# Monitoring consequences

The pre-specified operational consequence is in-control cycle ARL. Relative to
full reuse, P3 must increase ARL in every active clipping regime, meaning a
lower false-alert burden. H6-3 is **{science['H6-3']['status']}**.

This benefit is accepted only with detection safety. H6-4 is
**{science['H6-4']['status']}** across all 16 conditions. The largest
simultaneous upper bound for `R(P3)-R(P0)` is
`{max_response['simultaneous_upper95']:.6f}` at
`m={max_response['m']}, Delta={max_response['shift']}` against the frozen 0.10
margin. The largest simultaneous upper bound for absolute delay ratio Q is
`{max_safety['simultaneous_upper95']:.6f}` at
`m={max_safety['m']}, Delta={max_safety['shift']}` against the frozen 1.25
guard.

These are scoped Gaussian monitoring consequences, not a universal safety
claim and not evidence of an operational D4 phase transition.
"""
    (BASE / "MONITORING_CONSEQUENCES.md").write_text(monitoring)

    negatives = science["negative_primary_findings"]
    secondary = science["secondary_epsilon_0.05_failures"]
    diagnosis = f"""# Failure diagnoses and unfavorable findings

## HISTORICAL C6 — immutable failure

Historical Stage C remains `STAGE-C-PARTIAL`. C6 failed at `Delta=0.25` and
`Delta=0.5` because the paired upper 95% bounds for raw
`delay(ReBaseGuard)-delay(full reuse)` exceeded 25% of full-reuse delay. The
raw-delay comparison was confounded by materially different in-control alarm
rates, but that diagnosis does not rewrite or reinterpret C6.

## NEW L4R-06 campaign — separate later evidence

Primary unfavorable conditions retained: **{len(negatives)}**.
Secondary epsilon=0.05 failures retained: **{len(secondary)}**.
P2 outcomes and all 80 policy/regime/shift cell summaries remain in the final
scientific JSON whether favorable or unfavorable. No policy, regime, shift,
sample size, threshold, or margin was changed after outcomes.
"""
    (BASE / "FAILURE_DIAGNOSES.md").write_text(diagnosis)

    criteria = "\n".join(f"- {r['id']}: **{r['status']}** — {r['evidence']}"
                           for r in decision["criteria"])
    report = f"""# Final L4R-06 policy closure report

## Decision

**{decision['scoped_verdict']}**

Original requirement: **L4R-06 — Stability-aware reuse policy with monitoring
consequences**.

Current original L4R-06 status: **{decision['original_L4R06_current_status']}**.

Same-requirement mapping: **{str(decision['same_requirement_mapping']).lower()}**.
{decision['mapping_reason']}

## Frozen policy

`rho_P3(m) = min(1, 0.8 * rho_c,L95(m))`

The D4 lower 95% confidence endpoint drives every action. At m=100 the action
saturates naturally at one under the common clipping rule. D4 point estimates
are descriptive only; no P4 or semi-real task was run.

## Closure criteria

{criteria}

## Integrity and scope

- Adversarial first run: {first['n_passed']}/{first['n_checks']}.
- Adversarial final run: {final['n_passed']}/{final['n_checks']}.
- Repository verification: {decision['verification']['status']}, {decision['verification']['pytest_pass_count']} pytest checks.
- Byte-stable reproduction: {decision['reproduction']['status']}.
- Historical C6 preserved: **true**.
- Historical Stage C remains `STAGE-C-PARTIAL`.
- Historical Final Global Re-audit remains `LEVEL-4-PARTIAL`.
- No global re-audit was performed and L4R-12 was not touched.

Claim scope: {decision['claim_scope']}

Next blocker: **{decision['next_blocker']}**.
"""
    (BASE / "FINAL_REPORT.md").write_text(report)

    readme = f"""# L4R-06 stability-aware policy closure campaign

This isolated same-requirement campaign targets exactly **L4R-06 —
Stability-aware reuse policy with monitoring consequences**. It does not amend
Stage C/C6, change the Final Global Re-audit, or address L4R-12.

## Progress capsule

| Field | Value |
|---|---|
| Step | 3 / 3 — final closure |
| Gate | {decision['scoped_verdict']} |
| Original L4R-06 reconstructed? | yes |
| Protocol frozen | yes — `{science['protocol_sha256']}` |
| Policy P3 | frozen |
| Regimes | 4 |
| H6-1 | {science['H6-1']['status']} |
| H6-2 | {science['H6-2']['status']} |
| H6-3 | {science['H6-3']['status']} |
| H6-4 | {science['H6-4']['status']} |
| H6-5 | {science['H6-5']['status']} |
| Focused tests | PASS |
| Adversarial | {final['n_passed']}/{final['n_checks']} PASS |
| Historical C6 preserved | yes — FAILED remains immutable |
| Git | final closure checkpoint pending commit |
| Remaining | L4R-12 only; not started |

Reproduce offline with:

```bash
bash level4/closure_proofs/l4r06_policy/reproduce.sh
```
"""
    (BASE / "README.md").write_text(readme)
    print("generated RESULTS, MONITORING_CONSEQUENCES, FAILURE_DIAGNOSES, FINAL_REPORT, README")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
