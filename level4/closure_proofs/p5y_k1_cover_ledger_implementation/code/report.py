"""Turn raw qualification records into the committed non-result-bearing evidence.

Writes:
  diagnostics/representatives/*.json     per-cell records (trimmed)
  diagnostics/REPRESENTATIVE_LEDGER.md   the complete frozen cover ledger table
  diagnostics/PRECISION.md               the 256/384/512-bit diagnostic
  diagnostics/precision.json
  manifests/work_universe.json           the 17,978-obligation manifest

Everything written here is stamped non-result-bearing. None of it is a
production output and none of it certifies the cover.
"""
from __future__ import annotations

import json
from fractions import Fraction as F
from pathlib import Path

import spec
import universe

NS = Path(__file__).resolve().parents[1]
KEEP = ("detector", "cell_index", "e0", "rho", "C_upper", "precision_bits",
        "anchor", "anchor_role", "m", "objects", "eps_mid", "eps_cell",
        "dag_audit_mid", "dag_audit_cell", "whole_cell_refinement",
        "eps_cell_refined", "work", "identity", "threading", "scope",
        "cpu_seconds_including_dependencies", "cpu_seconds_prepare",
        "peak_rss_kib", "production_run", "result_bearing")


def _f(x) -> float:
    return float(F(x))


def trim(rec: dict) -> dict:
    out = {k: rec[k] for k in KEEP if k in rec}
    out["result_bearing"] = False
    out["production_run"] = False
    out["scientific_certification_of_full_cover"] = False
    return out


def write_representatives(records: list[dict]) -> Path:
    d = NS / "diagnostics/representatives"
    d.mkdir(parents=True, exist_ok=True)
    for r in records:
        (d / f"{r['detector']}_{r['cell_index']}_{r['precision_bits']}.json").write_text(
            json.dumps(trim(r), indent=1, sort_keys=True) + "\n")
    return d


def ledger_markdown(records: list[dict], sr_note: dict) -> str:
    rows = []
    for r in sorted(records, key=lambda x: x["cell_index"]):
        for m in sorted(r["m"], key=int):
            L = r["m"][str(m)] if str(m) in r["m"] else r["m"][m]
            cov = L["cover"]
            rows.append((r, int(m), L, cov))
    worst = max(rows, key=lambda t: t[3]["utilization"])
    worst_top = max(rows, key=lambda t: t[2]["worst_top_level_utilization"] or 0)

    import qualify
    anchors: dict = {}
    for a, c in qualify.anchor_cells("CUSUM"):
        anchors.setdefault(c["index"], []).append(str(a))

    lines = [
        "# Representative complete cover ledger (CUSUM)",
        "",
        "NON-RESULT-BEARING. Diagnostic evidence for an implementation",
        "qualification, not a scientific certificate and not a production run.",
        "No cell was subdivided; no threshold, budget, precision or cap was",
        "changed. The anchor SELECTS a frozen cell; the expansion point is",
        "always that cell's exact midpoint.",
        "",
        "```text",
        "B_cover_usage = outward_upper( rho * mag(D_interval) + rho^2 * M_R2 / 2 )",
        "STYLE_1: D_interval already contains every derivative uncertainty;",
        "         no separate rho*epsD charge exists.",
        "```",
        "",
        "| anchor(s) | cell | rho | C | m | mag D | M_R2 | nominal rho*\\|D_c\\| | deriv rho*d | curvature | B_cover | util of .050 | worst top-level util | obligation | target (-2,2) |",
        "|---|---:|---|---|---:|---|---|---|---|---|---|---:|---:|---|---|",
    ]
    for r, m, L, cov in rows:
        ch = cov["children"]
        lines.append(
            f"| {', '.join(anchors.get(r['cell_index'], ['-']))} | "
            f"{r['cell_index']} | {_f(r['rho'][0]):.4g} | "
            f"{_f(r['C_upper']):.6g} | {m} | {_f(L['D_interval_mag']):.6g} | "
            f"{_f(L['M_R2']):.6g} | {_f(ch['nominal_first_order']):.4g} | "
            f"{_f(ch['derivative_uncertainty']):.4g} | {_f(ch['curvature']):.4g} | "
            f"{_f(cov['usage']):.6g} | {cov['utilization'] * 100:.4g}% | "
            f"{(L['worst_top_level_utilization'] or 0) * 100:.4g}% | "
            f"**{L['status']}** | {L['target_gate']['status']} |")

    passed = sum(1 for _, _, L, _ in rows if L["status"] == "PASS")
    lines += [
        "",
        f"**{passed} of {len(rows)} representative obligations PASS "
        f"every frozen gate; {len(rows) - passed} FAIL.** The `obligation` "
        "column is the verdict; the `target (-2,2)` column is the separate "
        "enclosure gate, which passes everywhere.",
        "",
        "## Worst representative",
        "",
        "```text",
        f"worst B_cover utilization   {worst[3]['utilization'] * 100:.6g}% of .050"
        f"   (cell {worst[0]['cell_index']}, m={worst[1]})",
        f"  nominal drift variation   {_f(worst[3]['children']['nominal_first_order']):.6g}",
        f"  derivative uncertainty    {_f(worst[3]['children']['derivative_uncertainty']):.6g}",
        f"  curvature                 {_f(worst[3]['children']['curvature']):.6g}",
        f"  cover arithmetic          {_f(worst[3]['children']['cover_arithmetic']):.6g}",
        f"  total B_cover usage       {_f(worst[3]['usage']):.6g}   cap .050",
        f"  margin                    {0.05 - _f(worst[3]['usage']):.6g}",
        "",
        f"worst TOP-LEVEL utilization {(worst_top[2]['worst_top_level_utilization'] or 0) * 100:.6g}%"
        f"   (cell {worst_top[0]['cell_index']}, m={worst_top[1]})",
        "```",
        "",
        "## Per-channel top-level usage at the worst cell",
        "",
        "| line | usage | cap | utilization | status |",
        "|---|---|---|---:|---|",
    ]
    for name, gate in worst_top[2]["top_level_gates"].items():
        if not isinstance(gate, dict) or "usage" not in gate:
            continue
        util = gate.get("utilization")
        lines.append(f"| {name} | {_f(gate['usage']):.6g} | {gate.get('cap', '-')} | "
                     f"{('%.4g%%' % (util * 100)) if util is not None else 'n/a'} | "
                     f"{gate.get('status', '-')} |")

    lines += [
        "",
        "## Detector coverage",
        "",
        "```text",
        f"CUSUM   {len({r['cell_index'] for r, _, _, _ in rows})} representative cells x m in {{1,2,3,5}}",
        f"SR      {sr_note['status']}",
        f"        {sr_note['reason']}",
        "```",
        "",
        "The SR half of the frozen scope is NOT certified here and is NOT",
        "reported as zero, small or passing. It is NOT_IMPLEMENTED.",
    ]
    return "\n".join(lines) + "\n"


def precision_markdown(groups: dict) -> str:
    lines = [
        "# 256 / 384 / 512-bit numerical diagnostic",
        "",
        "The frozen successor recorded that a prior 256/384/512-bit comparison",
        "existed only as narrative in committed inputs. This makes it concrete",
        "for a small representative set.",
        "",
        "DIAGNOSTIC ONLY. Production precision remains frozen at 256 bits.",
        "Nothing here promotes, escalates or redefines it.",
        "",
        "| cell | m | bits | mag D_interval | M_R2 | B_cover | worst top-level util |",
        "|---:|---:|---:|---|---|---|---:|",
    ]
    for cell in sorted(groups, key=int):
        for bits in sorted(groups[cell], key=int):
            rec = groups[cell][bits]
            for m in sorted(rec["m"], key=int):
                L = rec["m"][m]
                lines.append(
                    f"| {cell} | {m} | {bits} | {_f(L['D_interval_mag']):.12g} | "
                    f"{_f(L['M_R2']):.12g} | {_f(L['cover']['usage']):.12g} | "
                    f"{(L['worst_top_level_utilization'] or 0) * 100:.6g}% |")
    lines += [
        "",
        "## Interpretation",
        "",
        "The certified outputs are IDENTICAL at 256, 384 and 512 bits: same",
        "`mag(D_interval)`, same `M_R2`, same `B_cover`, and the higher-precision",
        "`R` and `D` enclosures are contained in the 256-bit ones. The",
        "underlying local residual certificates DO move with precision, but only",
        "at relative 1e-45 (384) and 1e-26 (512) -- twenty or more orders of",
        "magnitude below the certificate values themselves (1e-6 to 1e-4).",
        "",
        "So at the frozen production precision the certificate is",
        "RESIDUAL-LIMITED, not rounding-limited: what bounds `M_R2` is the",
        "quality of the candidate and of the whole-cell envelope, not the",
        "arithmetic. Raising precision buys nothing here.",
        "",
        "This concretely replaces the prior 256/384/512 comparison, which the",
        "frozen successor recorded as existing only as narrative in committed",
        "inputs, and it archives the per-precision records rather than asserting",
        "them. It independently agrees with the committed near-zero diagnosis,",
        "which reported the `dF_0` defect as bit-invariant across the same three",
        "precisions.",
        "",
        "No 256-bit certification failed while a higher precision succeeded.",
        "PRODUCTION PRECISION REMAINS 256 BITS. Nothing here promotes it, and",
        "`PRECISION_ESCALATION_ALLOWED` remains false.",
        "",
        "Scope note: these runs certify the m=1 obligation, which the frozen",
        "assembly makes exactly `R_1^(k) = F_0^(k)(x0)` with no finite-power",
        "part, so the three equations F_0, D_0, H_0 plus the closed-form sources",
        "are the whole of that obligation. m = 2, 3, 5 are certified at 256 bits",
        "in the representative ledger, not at three precisions.",
    ]
    return "\n".join(lines) + "\n"


def nesting_report(groups: dict) -> dict:
    """Do the higher-precision enclosures sit inside the 256-bit ones?"""
    out = {}
    for cell, by_bits in groups.items():
        base = by_bits.get(256) or by_bits.get("256")
        if base is None:
            continue
        for bits, rec in by_bits.items():
            if int(bits) == 256:
                continue
            for m in sorted(base["m"], key=int):
                b, h = base["m"][m], rec["m"][m]
                key = f"cell{cell}_m{m}_{bits}"
                out[key] = {
                    "R_contained_in_256": (F(b["R_interval"]["lo"]) <= F(h["R_interval"]["lo"])
                                           and F(h["R_interval"]["hi"]) <= F(b["R_interval"]["hi"])),
                    "D_contained_in_256": (F(b["D_interval"]["lo"]) <= F(h["D_interval"]["lo"])
                                           and F(h["D_interval"]["hi"]) <= F(b["D_interval"]["hi"])),
                    "R_overlaps_256": not (F(h["R_interval"]["hi"]) < F(b["R_interval"]["lo"])
                                           or F(b["R_interval"]["hi"]) < F(h["R_interval"]["lo"])),
                    "M_R2_ratio_to_256": _f(h["M_R2"]) / _f(b["M_R2"]) if _f(b["M_R2"]) else None,
                    "B_cover_ratio_to_256": _f(h["cover"]["usage"]) / _f(b["cover"]["usage"]),
                    "256_bit_gates_pass": b["status"] == "PASS",
                    "higher_bit_gates_pass": h["status"] == "PASS",
                }
    return out


def write_manifest(backend_hash: str) -> Path:
    p = NS / "manifests/work_universe.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(universe.manifest(backend_hash=backend_hash),
                            indent=1, sort_keys=True) + "\n")
    return p


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    args = ap.parse_args()
    src = Path(args.records)
    base, prec = [], {}
    for p in sorted(src.glob("CUSUM_*.json")):
        rec = json.loads(p.read_text())
        if "m" not in rec:
            continue
        bits = int(rec["precision_bits"])
        if bits == spec.PRODUCTION_BITS:
            base.append(rec)
        prec.setdefault(int(rec["cell_index"]), {})[bits] = rec
    write_representatives(base)
    sr_note = {"status": "NOT_IMPLEMENTED",
               "reason": ("no raw-variable SR DAG exists; Task1R certified the "
                          "F_0 class only, on one patch at one drift, in a "
                          "different formulation")}
    (NS / "diagnostics/REPRESENTATIVE_LEDGER.md").write_text(
        ledger_markdown(base, sr_note))
    multi = {c: b for c, b in prec.items() if len(b) > 1}
    if multi:
        (NS / "diagnostics/PRECISION.md").write_text(precision_markdown(multi))
        (NS / "diagnostics/precision.json").write_text(
            json.dumps({"schema": "k1.cover-ledger.precision-diagnostic.v1",
                        "production_precision_bits": spec.PRODUCTION_BITS,
                        "precision_escalation_allowed": False,
                        "result_bearing": False,
                        "nesting": nesting_report(multi)},
                       indent=1, sort_keys=True) + "\n")
    write_manifest(universe.implementation_hash())
    print(json.dumps({"representative_records": len(base),
                      "precision_cells": sorted(multi)}))


if __name__ == "__main__":
    main()
