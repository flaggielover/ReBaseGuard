#!/usr/bin/env python3
"""Render PRODUCTION_RESULT.md from the machine-readable production artifacts.

Every figure in the report is read from a results file; nothing is retyped.
"""

from __future__ import annotations

import json
from pathlib import Path

PROD = Path(__file__).resolve().parent
R = PROD / "results"


def load(name):
    return json.loads((R / name).read_text())


def main() -> None:
    v = load("production_results.json")
    led = load("c2_cell_ledger.json")
    costs = load("cost_ledger.json")
    anchors = load("anchors.json")
    p1 = load("p1_zero_compute.json")
    c6 = load("c6_lean_arb.json")
    s1 = load("c2_stage1.json")
    plan2 = load("c2_stage2_plan.json")
    ob = v["obligations"]

    L = []
    a = L.append
    a("# P4X production result\n")
    a("```text")
    a(f"CHECKPOINT              = P4X_CHECKPOINT_A ({v['checkpoint_commit'][:7]}), "
      f"ACTIVE and BINDING")
    a(f"P4_ORIGINAL_VERDICT     = {v['P4_ORIGINAL_VERDICT']}   (immutable)")
    a(f"P4X_SUCCESSOR_VERDICT   = {v['P4X_SUCCESSOR_VERDICT']}")
    a(f"P4_SCIENTIFIC_LINE      = {v['P4_SCIENTIFIC_LINE_STATUS']}")
    a(f"NOVELTY_STATUS          = {v['NOVELTY_STATUS']}")
    a(f"LEVEL4_GLOBAL_CLOSURE   = {v['LEVEL4_GLOBAL_CLOSURE']}")
    a("```\n")

    a("## 1. Obligation ledger\n")
    a("| obligation | statement | status |")
    a("|---|---|---|")
    for k in ("C1", "C2", "C3", "C4", "C5", "C6", "C7"):
        a(f"| `{k}` | {ob[k].get('statement', '')} | **{ob[k]['status']}** |")
    a("")

    a("## 2. Anchor reproduction (phase P0)\n")
    a(f"{anchors['comparisons']} comparisons across "
      f"{len(anchors['anchors_attempted'])} configurations, "
      f"tolerance `{anchors['anchor_rtol']}`, "
      f"**{len(anchors['mismatches'])} mismatches**.\n")
    a("Reproducing the frozen values bitwise validates, together: "
      + "; ".join(anchors["semantics_validated_by_exact_reproduction"]) + ".\n")

    a("## 3. C2 correspondence\n")
    a(f"* cells: **{led['cells_passed']} / {led['cells_total']} PASS**")
    a(f"* failed: **{led['cells_failed']}**")
    a(f"* precision-limited: **{led['cells_precision_limited']}**\n")
    a("Gate, unchanged from the frozen protocol: relative discrepancy "
      "`<= 0.03` **and** `|z| <= 4`.\n")

    if led["failed_cells"]:
        a("### Failed cells — reported in full\n")
        a("| layer | detector | family | m | Route A | Route B | relative | \\|z\\| | precision |")
        a("|---|---|---|---|---|---|---|---|---|")
        for c in led["failed_cells"]:
            ra, rb = c["route_a"], c["route_b"]
            a(f"| {c['layer']} | {c['detector']} | {c['family']} | {c['m']} | "
              f"{ra['estimate']:.4f} ± {ra['se']:.4f} | "
              f"{rb['estimate']:.4f} ± {rb['se']:.4f} | "
              f"{c['relative_discrepancy'] * 100:.3f}% | {c['z']:.2f} | "
              f"{c['precision_status']} |")
        a("")
    else:
        a("No theorem-supported cell failed the frozen gate.\n")

    if led["precision_limited_cells"]:
        a("### Precision-limited cells\n")
        a("| layer | detector | family | m | reason |")
        a("|---|---|---|---|---|")
        for c in led["precision_limited_cells"]:
            a(f"| {c['layer']} | {c['detector']} | {c['family']} | {c['m']} | "
              f"cost cap under the frozen precision policy |")
        a("")

    a("### Worst cells by relative discrepancy\n")
    a("| layer | detector | family | m | relative | \\|z\\| | Route-A relSE | Route-B relSE | result |")
    a("|---|---|---|---|---|---|---|---|---|")
    for c in sorted(led["cells"], key=lambda c: -c["relative_discrepancy"])[:12]:
        a(f"| {c['layer']} | {c['detector']} | {c['family']} | {c['m']} | "
          f"{c['relative_discrepancy'] * 100:.3f}% | {c['z']:.2f} | "
          f"{c['route_a']['relative_se'] * 100:.3f}% | "
          f"{c['route_b']['relative_se'] * 100:.3f}% | {c['gate_result']} |")
    a("")

    a("## 4. Two-stage precision acquisition\n")
    a(f"* already at `r*` after stage 1: **{len(plan2['already_meeting_r_star'])}** "
      f"of {len(plan2['plans'])} (configuration, route) pairs")
    a(f"* top-ups approved: **{len(plan2['topups_approved'])}**")
    a(f"* precision-limited: **{len(plan2['precision_limited'])}**\n")
    a(f"Trigger: *{plan2['trigger']}*.  It excludes "
      + ", ".join(plan2["trigger_excludes"]) + ".\n")
    if plan2["topups_approved"]:
        a("| configuration | route | stage-1 N | stage-1 relSE | target N | added N | reason |")
        a("|---|---|---|---|---|---|---|")
        for p in plan2["topups_approved"]:
            a(f"| {p['config']} | {p['route']} | {p['stage1_N']:,} | "
              f"{p['stage1_SE_worst_relative'] * 100:.3f}% | "
              f"{p['target_N']:,.0f} | {p['additional_N']:,.0f} | "
              f"{p['reason']} |")
        a("")

    a("## 5. C5 Gaussian consistency\n")
    c5 = p1["C5"]
    a(f"Statistic: `{c5['formula']}`, limit **{c5['limit']}**, "
      f"using both campaigns' published uncertainty.\n")
    a("| detector | m | closed | P4X | signed rel | `z_combined` | historical single-error | pass |")
    a("|---|---|---|---|---|---|---|---|")
    for r in c5["rows"]:
        a(f"| {r['detector']} | {r['m']} | "
          f"{r['closed_estimate']:.6f} ± {r['closed_se']:.6f} | "
          f"{r['p4x_estimate']:.6f} ± {r['p4x_se']:.6f} | "
          f"{r['signed_relative_difference'] * 100:+.3f}% | "
          f"**{r['z_combined']:.3f}** | "
          f"{r['z_historical_single_error_reported_only']:.2f} | "
          f"{'yes' if r['pass'] else 'NO'} |")
    a(f"\nWorst `z_combined` = **{c5['worst_z_combined']:.3f}** against a limit of "
      f"{c5['limit']}.  The historical single-error statistic reaches "
      f"{c5['worst_z_historical_single_error']:.2f} and gates nothing.\n")

    a("## 6. C4 failure-mode evidence\n")
    c4 = p1["C4"]
    a(f"**A3 half** — {c4['a3_half']['proved_failure_mode']}.  Discharged by "
      f"{c4['a3_half']['discharge']}.  "
      f"{c4['a3_half']['uniform_confirmed']}/{c4['a3_half']['uniform_cells']} "
      f"uniform cells corroborate at `|z|` "
      f"{c4['a3_half']['uniform_z_range'][0]:.0f}-"
      f"{c4['a3_half']['uniform_z_range'][1]:.0f}.  New compute: "
      f"**{c4['a3_half']['new_compute']}**.\n")
    a(f"**First-moment half** — {c4['first_moment_half']['proved_failure_mode']}.  "
      f"Discharged by {c4['first_moment_half']['discharge']}.  No Monte Carlo "
      f"disagreement signature is demanded, because a two-route discrepancy "
      f"statistic cannot express non-existence; the measured `|z|` across the "
      f"{c4['first_moment_half']['cauchy_cells']} Cauchy cells is "
      f"{c4['first_moment_half']['measured_z_range'][0]:.3f}-"
      f"{c4['first_moment_half']['measured_z_range'][1]:.3f}.  New compute: "
      f"**{c4['first_moment_half']['new_compute']}**.\n")

    a("## 7. C3 Route-Q cross-check\n")
    c3 = ob["C3"]
    a(f"Role: `{c3['role']}`.  {c3['rows']} rows, worst relative discrepancy "
      f"`{c3['worst_relative_discrepancy']:.3e}` against a tolerance of "
      f"`{c3['tolerance']}`.  Cross-check: **{c3['cross_check']}**.\n")
    a(f"Route Q arbitrated no cell (`{c3['arbitrated_any_cell']}`) and rescued no "
      f"gate (`{c3['rescued_any_gate']}`).  {c3['note']}\n")

    a("## 8. C6 Lean and Arb re-verification\n")
    a(f"* Lean: **{c6['lean']['declarations_audited']}** declarations, axioms "
      f"exactly `{', '.join(c6['lean']['axioms_observed'])}`, "
      f"**{c6['new_lean_declarations']}** new declarations")
    a(f"* Arb: objects `{', '.join(c6['arb']['certificate_objects'])}`, "
      f"**{c6['new_arb_objects']}** new objects")
    for bits, run in c6["arb"]["runs"].items():
        a(f"  * at {bits} bits: {run['checks_evaluated']} checks, "
          f"failed `{run['failed_checks']}`, pass `{run['all_checks_pass']}`")
    a(f"* tools: {json.dumps(c6['tool_versions'])}\n")

    a("## 9. Cost\n")
    a("```text")
    a(f"total CPU               {costs['total_cpu_hours']:.4f} h   "
      f"(cap {costs['total_cap_hours']})   {costs['total_cap_status']}")
    a(f"total wall              {costs['total_wall_hours']:.4f} h")
    a(f"worst configuration     {costs['max_configuration_cpu_hours']:.4f} h   "
      f"(cap {costs['per_configuration_cap_hours']})   "
      f"{costs['per_configuration_cap_status']}")
    a(f"                        {costs['max_configuration']}")
    a("```\n")
    hr = costs["high_risk_configuration"]
    a(f"The pre-registered high-risk configuration `{hr['config']}`: Checkpoint-A "
      f"stage-1 projection {hr['checkpoint_projection_cpu_hours']:.3f} h, "
      f"pre-run projection at the production block size "
      f"{hr['pre_run_projection_cpu_hours']:.3f} h, "
      f"**actual {hr['actual_cpu_hours']:.3f} h**, against a checkpoint "
      f"worst-case of {hr['checkpoint_worst_case_cpu_hours']:.2f} h and a "
      f"{costs['per_configuration_cap_hours']} h cap.\n")

    a("## 10. Binding verdict\n")
    a("```text")
    a(f"P4X_SUCCESSOR_VERDICT   = {v['P4X_SUCCESSOR_VERDICT']}")
    a(f"P4_ORIGINAL_VERDICT     = {v['P4_ORIGINAL_VERDICT']}   (unchanged)")
    a(f"P4_SCIENTIFIC_LINE      = {v['P4_SCIENTIFIC_LINE_STATUS']}")
    a(f"load-bearing contradiction = {v['load_bearing_contradiction']}")
    a(f"integrity failure          = {v['integrity_failure']}")
    a("```\n")

    a("## 11. Integrity\n")
    a(f"Protected tree verified at three readings — pre-production, "
      f"post-production and pre-verdict — over "
      f"{len(ob['C7']['manifest'])} tracked paths by git object: "
      f"{ob['C7']['readings']}.  "
      f"`P4_ORIGINAL_MUTATED = {v['P4_ORIGINAL_MUTATED']}`, "
      f"`P5_P5X_MUTATED = {v['P5_P5X_MUTATED']}`.\n")

    (PROD / "PRODUCTION_RESULT.md").write_text("\n".join(L) + "\n")
    print(f"-> {PROD / 'PRODUCTION_RESULT.md'}")


if __name__ == "__main__":
    main()
