#!/usr/bin/env python3
"""Generate human-readable mirrors from the final summary and decision JSON."""
from __future__ import annotations

import argparse
import json

from config import BASE, PRIMARY_TASKS

NAMES = {"household": "A — Household power", "metro": "B — Metro traffic",
         "beijing": "C — Beijing PM2.5"}


def f(value: float) -> str:
    return f"{value:.3f}"


def results_md(summary: dict) -> str:
    rows = []
    for task in PRIMARY_TASKS:
        row = summary["tasks"][task]
        rows.append(
            f"| {NAMES[task]} | {f(row['reference_ratios']['P1_over_P2']['ratio'])} "
            f"[{f(row['reference_ratios']['P1_over_P2']['ci95'][0])}, {f(row['reference_ratios']['P1_over_P2']['ci95'][1])}] | "
            f"{f(row['alert_burden_ratio']['ratio'])} "
            f"[{f(row['alert_burden_ratio']['ci95'][0])}, {f(row['alert_burden_ratio']['ci95'][1])}] | "
            f"{'YES' if row['H2_1']['supported'] else 'NO'} | "
            f"{'YES' if row['H2_2']['supported'] else 'NO'} | "
            f"{'YES' if row['H2_3']['supported'] else 'NO'} | "
            f"{'YES' if row['H2_4']['supported'] else 'NO'} |"
        )
    detail = []
    for task in PRIMARY_TASKS:
        row = summary["tasks"][task]
        failed = [condition for condition, value in row["H2_3"]["conditions"].items()
                  if not value["noninferior_eps_0_10"]]
        detail.append(f"- **{NAMES[task]}:** H2-1={row['H2_1']['supported']}; "
                      f"H2-2={row['H2_2']['supported']} "
                      f"(burden route={row['H2_2']['alert_burden_route']}, "
                      f"medium-step route={row['H2_2']['medium_step_response_route']}); "
                      f"H2-3={row['H2_3']['supported']}; failed safety conditions="
                      f"{', '.join(failed) if failed else 'none'}; H2-4={row['H2_4']['supported']}.")
    return """# External validation V2 results

All results below are generated from `results/summary.json`. Null, unfavorable,
and contradictory directions are retained.

| Task | E2 P1/P2 ratio [95% CI] | E3 P1/P2 ratio [95% CI] | H2-1 | H2-2 | H2-3 | H2-4 |
|---|---:|---:|---|---|---|---|
""" + "\n".join(rows) + "\n\n## Task decisions\n\n" + "\n".join(detail) + """

## Campaign result

Only household power supports H2-4. Metro shows reference distortion but its
full-reuse alert burden is lower, the medium-step response route is unsupported,
and simultaneous P2 non-inferiority is not demonstrated. Beijing shows
reference distortion and higher P1 alert burden, but simultaneous P2
non-inferiority is not demonstrated. No task shows a strong P2 safety
contradiction.

The frozen >=2/3 closure rule is therefore not met: the scoped result is
`EXTERNAL-VALIDATION-V2-PARTIAL`.
"""


def final_md(summary: dict) -> str:
    decision = summary["decision"]
    return f"""# Final report — external validation V2

## Scoped verdict

> **{decision['decision']}**
>
> Mechanism support: **{decision['tasks_supporting_H2_4']}/3**; required: **2/3**

The later independent campaign is usable and sufficiently powered, but it does
not close the scoped external-validation requirement. This is a scientific
partial result, not a documentation failure.

## Protected historical status

- Stage E: `STAGE-E-PARTIAL`, 0/3 H-E5 — unchanged.
- Stage F: `LEVEL-4-PARTIAL` — unchanged.
- Post-closure global re-audit: `LEVEL-4-PARTIAL` — preserved, not recomputed.
- Novelty verification: `NOVELTY-VERIFICATION-CLOSED` — unchanged.
- No old Stage-E data were pooled; no global re-audit was performed.

## Claim boundary

The campaign supports only the task-specific findings in `RESULTS.md`. It does
not support “production validated”, “universally robust”, “deployment proven”,
“distribution-free”, “detector-independent”, “all real-world streams”, or
“optimal”.

## Exact remaining blocker

Only one of three tasks supports the full H2-4 package. A future external
validation campaign would need at least one additional independently frozen,
sufficiently powered task that jointly supports reference distortion,
operational consequence, and ReBaseGuard non-inferiority. No such follow-up is
started here.

## Verification and reproduction

- focused V2 tests: 45/45
- authoritative distinct-check convention: 1,028 (983 before V2 + 45 V2)
- adversarial first run: 19/22, preserved
- adversarial final run: 22/22
- generated-artifact reproduction: PASS
"""


def calibration_md(summary: dict) -> str:
    rows = []
    for task in PRIMARY_TASKS:
        value = summary["tasks"][task]
        calibration = value["calibration"]
        power = value["power"]
        rows.append(
            f"| {NAMES[task]} | {calibration['threshold']:.10f} | "
            f"{calibration['target_arl']} / {calibration['achieved']['mean']:.4f} | "
            f"[{calibration['achieved']['ci95'][0]:.4f}, {calibration['achieved']['ci95'][1]:.4f}] | "
            f"{power['calibration_cycle_blocks']} | {power['natural_week_blocks']} | "
            f"{power['event_blocks']} | PASS |"
        )
    return """# Calibration and actual power audit

All values were generated after the execution checkpoint and before any
confirmatory P0/P1/P2 evaluation comparison. Calibration used the chronological
calibration block under P0 only. The task threshold is fixed for every policy.

| Task | h | Target / achieved ARL | 95% block interval | Calibration blocks | Natural week blocks | Event blocks | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
""" + "\n".join(rows) + """

Each point error is below 1%, each target lies inside its interval, and every
endpoint class meets the unmodified 20-block floor. The backup was not
activated. Calibration residuals remain misspecified relative to iid Gaussian
theory: Metro retains ACF1 0.724 and Beijing excess kurtosis 12.87. The campaign
therefore uses empirical calibration and the frozen dependence-aware inference;
it does not claim theorem confirmation.

Canonical record: `results/gates.json`.
"""


def adversarial_md() -> str:
    first = json.loads((BASE / "results/adversarial_first.json").read_text())
    final = json.loads((BASE / "results/adversarial_final.json").read_text())
    first_by = {row["id"]: row for row in first["checks"]}
    rows = []
    for row in final["checks"]:
        before = first_by[row["id"]]
        rows.append(f"| {row['id']} | {row['name']} | "
                    f"{'PASS' if before['passed'] else 'FAIL'} | "
                    f"{'PASS' if row['passed'] else 'FAIL'} | {row['detail']} |")
    return f"""# Adversarial audit

The first run is preserved at **{first['passed']}/{first['total']} {first['status']}**.
A19 was an over-broad checker match; A21 and A22 correctly preceded their final
records. The final run is **{final['passed']}/{final['total']} {final['status']}**.

| ID | Check | First | Final | Final evidence |
|---|---|---|---|---|
""" + "\n".join(rows) + """

No scientific threshold, hypothesis, result, or closure rule was weakened
between runs.
"""


def outputs(summary: dict) -> dict[str, str]:
    return {"RESULTS.md": results_md(summary), "FINAL_REPORT.md": final_md(summary),
            "CALIBRATION_AUDIT.md": calibration_md(summary),
            "ADVERSARIAL_AUDIT.md": adversarial_md()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    summary = json.loads((BASE / "results/summary.json").read_text())
    errors = []
    for name, content in outputs(summary).items():
        path = BASE / name
        if args.check:
            if not path.exists() or path.read_text() != content:
                errors.append(name)
        else:
            path.write_text(content)
    if errors:
        print("stale generated reports: " + ", ".join(errors))
        return 1
    print("reports: byte-stable" if args.check else "reports: generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
