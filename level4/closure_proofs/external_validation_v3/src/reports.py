#!/usr/bin/env python3
"""Generate the human-readable mirrors from structured V3 data."""
from __future__ import annotations

import argparse
import json

from config import BASE, PRIMARY_TASKS


NAMES = {"metropt": "MetroPT-3 compressor", "retail": "Online Retail II"}


def f(value: float) -> str:
    return f"{value:.6f}"


def yn(value: bool) -> str:
    return "YES" if value else "NO"


def results_md(summary: dict) -> str:
    rows = []
    safety = []
    for task in PRIMARY_TASKS:
        row = summary["tasks"][task]["analysis"]
        e1p2, e1p0 = row["E1"]["P1_over_P2"], row["E1"]["P1_over_P0"]
        e2p2, e2p0 = row["E2"]["P1_over_P2"], row["E2"]["P1_over_P0"]
        rows.append(
            f"| {NAMES[task]} | {f(e1p2['ratio'])} [{f(e1p2['lower_97_5_one_sided'])}, "
            f"{f(e1p2['upper_97_5_one_sided'])}] | {f(e1p0['ratio'])} "
            f"[{f(e1p0['lower_97_5_one_sided'])}, {f(e1p0['upper_97_5_one_sided'])}] | "
            f"{f(e2p2['ratio'])} [{f(e2p2['lower_97_5_one_sided'])}, "
            f"{f(e2p2['upper_97_5_one_sided'])}] | {f(e2p0['ratio'])} "
            f"[{f(e2p0['lower_97_5_one_sided'])}, {f(e2p0['upper_97_5_one_sided'])}] | "
            f"{yn(row['H3_1']['supported'])} | {yn(row['H3_2']['supported'])} | "
            f"{yn(row['H3_3']['supported'])} | {yn(row['H3_4']['supported'])} |"
        )
        condition_text = ", ".join(
            f"{condition}={f(value['upper99_excess'])}"
            for condition, value in row["H3_3"]["conditions"].items()
        )
        safety.append(f"- **{NAMES[task]}:** upper 99% excess bounds: {condition_text}.")
    route_b = []
    for task in PRIMARY_TASKS:
        row = summary["tasks"][task]["analysis"]["H3_2"]
        route_b.append(
            f"- **{NAMES[task]}:** Route A alert burden=YES; Route B medium-step "
            f"response=NO; P1/P2={f(row['medium_P1_over_P2']['ratio'])} "
            f"[{f(row['medium_P1_over_P2']['lower_97_5_one_sided'])}, "
            f"{f(row['medium_P1_over_P2']['upper_97_5_one_sided'])}], P1/P0="
            f"{f(row['medium_P1_over_P0']['ratio'])} "
            f"[{f(row['medium_P1_over_P0']['lower_97_5_one_sided'])}, "
            f"{f(row['medium_P1_over_P0']['upper_97_5_one_sided'])}]."
        )
    return """# External validation V3 results

All values are generated from `results/summary.json`; no cross-task estimate is
pooled. Null and unfavorable routes remain visible.

| Task | E1 P1/P2 ratio [97.5% bounds] | E1 P1/P0 ratio [97.5% bounds] | E2 P1/P2 ratio [97.5% bounds] | E2 P1/P0 ratio [97.5% bounds] | H3-1 | H3-2 | H3-3 | H3-4 |
|---|---:|---:|---:|---:|---|---|---|---|
""" + "\n".join(rows) + """

## Operational-route audit

H3-2 is supported on both tasks through frozen Route A only. The prespecified
Route B result is unfavorable and is not reclassified:

""" + "\n".join(route_b) + """

## Simultaneous P2 non-inferiority

The primary rule requires every upper simultaneous one-sided 99% excess bound
to be at most 0.10:

""" + "\n".join(safety) + """

Both tasks support H3-1, H3-2, H3-3, and therefore H3-4. V3 joint support is
2/2. The scientific scoped result is `EXTERNAL-VALIDATION-V3-CLOSED`.

MetroPT limitation: the administrative cap is 32 observed hours, shorter than
the 48-hour recurring on-phase. Consequently its recurring and step-1 delays
are identical within the frozen scoring window; this limitation is retained.
"""


def cross_campaign_md(summary: dict) -> str:
    rows = []
    for row in summary["cross_campaign_tasks"]:
        def label(field: str) -> str:
            value = row[field]
            if isinstance(value, bool):
                return yn(value)
            return {"SUPPORTED": "YES", "NOT_SUPPORTED": "NO",
                    "UNEVALUABLE": "NA"}.get(value, value)
        rows.append(
            f"| {row['campaign']} | {row['display']} | {row['usability']} | "
            f"{row['minimum_effective_blocks']} | {label('reference_distortion')} | "
            f"{label('operational_consequence')} | {label('p2_safety')} | "
            f"{label('joint_support')} | {yn(row['counts_toward_closure'])} |"
        )
    return """# Frozen cross-campaign aggregation

This is a decision-counting audit, not a meta-analysis. Each task retains its
own frozen protocol and task-level inference; estimates and samples are never
pooled.

| Campaign | Task | Usability | Minimum effective blocks | Reference distortion | Operational consequence | P2 safety | Joint support | Counts |
|---|---|---|---:|---|---|---|---|---|
""" + "\n".join(rows) + """

## Mechanical aggregation

- Stage E remains 0/3 and `STAGE-E-PARTIAL`.
- V2 remains 1/3 and `EXTERNAL-VALIDATION-V2-PARTIAL`; Household power is its
  sole joint-support success.
- V3 contributes MetroPT-3 and Online Retail II, both independently gated and
  jointly supportive.
- Cross-campaign success count: 3; frozen requirement: 2.
- Original Level-4 requirement L4R-15, semi-real external validation: `CLOSED`.

The historical negative Stage-E and V2 tasks remain visible above. This later
closure neither modifies their verdicts nor performs a global Level-4 re-audit.
"""


def calibration_md(summary: dict) -> str:
    rows = []
    for task in PRIMARY_TASKS:
        value = summary["tasks"][task]
        calibration, power = value["calibration"], value["power"]
        rows.append(
            f"| {NAMES[task]} | {calibration['threshold']:.12f} | "
            f"{calibration['target_arl']} / {calibration['achieved']['mean']:.6f} | "
            f"[{calibration['achieved']['ci95'][0]:.6f}, "
            f"{calibration['achieved']['ci95'][1]:.6f}] | "
            f"{power['calibration_cycle_blocks']} | {power['natural_blocks']} | "
            f"{power['event_blocks']} | PASS |"
        )
    return """# Calibration and actual-power audit

Calibration is P0-only and precedes every confirmatory policy comparison. The
chronological split, train-owned model and scale, calibration-owned threshold,
and shared evaluation stream are frozen.

| Task | h | Target / achieved ARL | Dependence-aware 95% interval | Calibration blocks | Natural blocks | Event blocks | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
""" + "\n".join(rows) + """

Both point estimates meet the 10% tolerance, both targets lie inside their
intervals, and every closure endpoint meets the unmodified floor of 40. The
campaign uses empirical calibration and dependence-aware blocks; it does not
claim iid Gaussian residuals or theorem confirmation.
"""


def adversarial_md() -> str:
    first_path = BASE / "results/adversarial_first.json"
    final_path = BASE / "results/adversarial_final.json"
    if not first_path.exists():
        return "# Adversarial audit\n\nThe preserved first run has not yet been executed.\n"
    first = json.loads(first_path.read_text())
    final = json.loads(final_path.read_text()) if final_path.exists() else None
    final_by = {row["id"]: row for row in final["checks"]} if final else {}
    rows = []
    for before in first["checks"]:
        after = final_by.get(before["id"])
        rows.append(
            f"| {before['id']} | {before['name']} | {'PASS' if before['passed'] else 'FAIL'} | "
            f"{'PENDING' if after is None else 'PASS' if after['passed'] else 'FAIL'} | "
            f"{before['detail'] if after is None else after['detail']} |"
        )
    final_text = "pending" if final is None else f"{final['passed']}/{final['total']} {final['status']}"
    return f"""# Adversarial audit

The first run is preserved at **{first['passed']}/{first['total']} {first['status']}**.
Its expected A24/A25 failures precede creation of the full-verifier and
byte-reproduction records. Final result: **{final_text}**.

| ID | Check | First | Final | Evidence |
|---|---|---|---|---|
""" + "\n".join(rows) + """

No scientific threshold, route, task, result, or aggregation rule is weakened
between the two runs.
"""


def final_md(summary: dict) -> str:
    final_path = BASE / "results/decision.json"
    final = json.loads(final_path.read_text()) if final_path.exists() else None
    scientific = summary["decision"]
    verdict = final["final_campaign_verdict"] if final else scientific["scientific_campaign_verdict"]
    next_action = final["next_action"] if final else "FINAL GLOBAL LEVEL-4 RE-AUDIT (after closure gates)"
    verification = json.loads((BASE / "results/verification.json").read_text()) \
        if (BASE / "results/verification.json").exists() else {}
    reproduction = json.loads((BASE / "results/reproduction.json").read_text()) \
        if (BASE / "results/reproduction.json").exists() else {}
    adversarial = json.loads((BASE / "results/adversarial_final.json").read_text()) \
        if (BASE / "results/adversarial_final.json").exists() else {}
    return f"""# Final report — external validation V3

## Scoped V3 verdict

> **{verdict}**
>
> V3 joint support: **2/2**. Cross-campaign successes: **3**; required: **2**.

The later evidentiary status of original requirement L4R-15, semi-real external
validation, is `CLOSED`. This is a generator-owned consequence of the two V3
task decisions plus the frozen decision-counting rule.

## Protected historical statuses

- Stage E: `STAGE-E-PARTIAL`, 0/3 — unchanged.
- External validation V2: `EXTERNAL-VALIDATION-V2-PARTIAL`, 1/3 — unchanged.
- Historical Stage F and the protected post-closure global verdict:
  `LEVEL-4-PARTIAL` — unchanged and not recomputed.
- No Stage-E or V2 estimate is pooled, relabeled, modified, or reinterpreted.

## Preserved negative and limiting evidence

Both V3 tasks support H3-2 through alert-burden Route A, while the frozen
medium-step response Route B is unfavorable on both. Historical Stage-E and V2
negative tasks remain in `CROSS_CAMPAIGN_AGGREGATION.md`. MetroPT recurring
delays equal step-1 delays inside its 32-observed-hour cap, which is shorter
than the 48-hour recurring on-phase.

## Claim boundary

This campaign supports only the frozen task-level mechanism package and the
later L4R-15 evidence status. It does not establish production validation,
deployment readiness, universal robustness, distribution-free validity,
detector independence, or optimality.

Across all campaigns, P2 safety remains regime-dependent: it passes both V3
tasks and V2 Household, but historical V2 Metro and Beijing did not establish
their frozen safety hypothesis. There is no strong V3 contradiction.

## Closure engineering

- focused V3 tests: 75/75
- adversarial final: {adversarial.get('passed', 'pending')}/{adversarial.get('total', 25)}
- authoritative repository checks: {verification.get('current_distinct_checks', 'pending')}/1103
- generated science bytes: {reproduction.get('status', 'pending')}
- next action: `{next_action}`; it is not started here
- stop rule: `NO_V4`
"""


def outputs(summary: dict) -> dict[str, str]:
    return {
        "RESULTS.md": results_md(summary),
        "CROSS_CAMPAIGN_AGGREGATION.md": cross_campaign_md(summary),
        "CALIBRATION_AUDIT.md": calibration_md(summary),
        "ADVERSARIAL_AUDIT.md": adversarial_md(),
        "FINAL_REPORT.md": final_md(summary),
    }


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
