"""Write RESULT.md from config/CURVATURE_SUCCESSOR_RECORD.json (no shell interpolation)."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
rec = json.loads((NS / "config/CURVATURE_SUCCESSOR_RECORD.json").read_text())
sha = hashlib.sha256((NS / "config/CURVATURE_SUCCESSOR_RECORD.json").read_bytes()).hexdigest()
p23 = rec["phase2_phase3"]
kill = rec["kill_micropilot"]
L = [f"# P5Y K1 SR O9 curvature certification successor: {rec['classification']}", "",
     "**CURVATURE_CERTIFICATION_SUCCESSOR only. This is a negative result, committed as immutable evidence.** It is not K1",
     "closure, not P5Y closure, and not production readiness. The parent is `8b8a242` (tag",
     "`p5y-k1-sr-o9-t5-one-cell-28-of-28`), which is unchanged.", "",
     f"The authoritative record is `config/CURVATURE_SUCCESSOR_RECORD.json` (sha256 `{sha}`).", "",
     "## A. Doctrine ruling: CURVATURE_LOCALIZATION_DOCTRINE_PERMITS_SUCCESSOR", ""]
for k, v in rec["phase1_doctrine"]["answers"].items():
    L.append(f"- **{k}.** {v}")
L += ["", f"Scope: {rec['phase1_doctrine']['scope']}", "",
      "## B/C. Nominal-vs-certified decomposition and the idealized cover (diagnostic only)", "",
      "| cell | m | certified B_cover / (1/20) | idealized (diagnostic) | M_R2 / nominal R'' | target gate now / with zero curvature error |",
      "|---|---|---|---|---|---|"]
for c, d in p23.items():
    for m, v in d.items():
        L.append(f"| {c} | {m} | {v['B_cover_ratio']:.4g} | {v['IDEALIZED_B_cover_ratio_DIAGNOSTIC']:.3g} | {v['inflation_MR2_over_nominal']:.3g}x |"
                 f" {v['target_gate_current']} / {v['target_gate_with_zero_curvature_error_DIAGNOSTIC']} |")
L += ["", f"**Answer: {rec['phase2_answer']}.**", "",
      "## D/E. Successor architecture and subdivision rule", "",
      "The successor applies the frozen CUSUM layer-2 construction to the SR DAG: delta_cell = delta_mid + rho*Env. Env is",
      "the e-uniform bound on the e-derivative of each node residual, built as closed-form cell-uniform operator norms times",
      "candidate sup norms. The per-node minimum with the T3 interval-e delta_cell is taken; both are valid bounds.",
      "", "The frozen ErrorDAG, `sr_refine`, assembly, ledger and T5 obligations then run unchanged. Parent e0, rho, STYLE_1",
      "and every threshold are unchanged.", "",
      f"Subdivision rule, predeclared {rec['predeclaration']['declared_utc']} (sha256 `{rec['predeclaration']['sha256'][:16]}...`):",
      rec['predeclaration']['subdivision_rule'], "",
      "## F/G. Kill micropilot, with cell 150 as control (subdivision level N = 1)", "",
      "| cell | m | B_cover / (1/20): old -> new | M_R2: old -> new | curvature obligation | assembly obligation | target gate |",
      "|---|---|---|---|---|---|---|"]
for r in kill["rows"]:
    L.append(f"| {r['cell']} | {r['m']} | {r['ratio_old']:.4g} -> {r['ratio_new']:.4g} | {r['M_R2_old']:.4g} -> {r['M_R2_new']:.4g} |"
             f" {r['curvature_obligation_new']} | {r['assembly_obligation_new']} | {r['target_old']} -> {r['target_new']} |")
L += ["", f"Critical kill cases (B_cover / (1/20)): {kill['critical']}. Cell 313 still fails m = 2, 3, 5.", "",
      "What still binds cell 313, from the H closure after the successor:"]
for r, d in kill["cell313_remaining_H_closure"].items():
    L.append(f"- H_{r}: eps_H {d['eps_H_cell']:.4g} = C*deltaH {d['C*deltaH_cell']:.3g} + C*k2*eps_F {d['C*k2*eps_F_cell']:.3g}"
             f" + C*2k1*eps_D {d['C*2k1*eps_D_cell']:.3g} + C*eps_S2 {d['C*eps_S2_cell']:.3g}")
L += ["", f"Control cell 150: every m passes and every ratio is tighter or equal ({rec['control_150']}).", "",
      "## H. Six-cell validation", rec["phase7_six_cell_validation"], "",
      "## I. Determinism",
      f"{rec['determinism']['pairs']} fresh-process replay files, all byte-identical: {rec['determinism']['all_bytes_equal']}; "
      f"zero scientific leaves moved: {rec['determinism']['zero_scientific_leaves_moved']}.", "",
      "## Predecessor disclosure", rec["predecessor_kz2_check"]["note"], "",
      "## J. Cost", json.dumps(rec["cost"], indent=1), "",
      "## Next options (not taken; each needs its own predeclaration or governance)"] + [f"- {x}" for x in rec["next_options_not_taken"]] + [
      "", "## L. Production firewall",
      f"PASS: {rec['production_firewall']['PASS']}. The production worktrees are unchanged "
      f"({rec['production_firewall']['worktrees']}), with no active rbg units and no production processes. prodctl was not run;",
      "no production ledger, retry or worker was touched.", ""]
(NS / "RESULT.md").write_text("\n".join(L) + "\n")
print("RESULT.md", len(L), "lines")
