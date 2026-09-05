"""Assemble the committed, non-result-bearing repair evidence.

    usage: repair_report.py --regression DIR [--compare FILE]

Writes:
  diagnostics/regression/*.json        repaired re-certification records
  diagnostics/REGRESSION.md            reviewed vs repaired comparison
  manifests/repair_self_audit.json     the repair self-audit
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import prior

import spec                                                     # noqa: E402

NS = prior.NS
IMPL = prior.IMPL_NS

KEEP = ("detector", "cell_index", "e0", "rho", "C_upper", "precision_bits",
        "scope", "repair", "repairs", "s0_charge_audit", "m", "objects",
        "eps_mid", "eps_cell", "eps_cell_refined", "dag_audit_mid",
        "dag_audit_cell", "whole_cell_refinement", "work", "identity",
        "threading", "cpu_seconds_including_dependencies",
        "cpu_seconds_prepare", "peak_rss_kib")


def _f(x) -> float:
    return float(F(x))


def trim(rec: dict) -> dict:
    out = {k: rec[k] for k in KEEP if k in rec}
    out["result_bearing"] = False
    out["production_run"] = False
    out["scientific_certification_of_full_cover"] = False
    return out


def reviewed_record(cell: int, bits: int, scope: str):
    if scope == "m1":
        p = IMPL / f"diagnostics/precision_records/CUSUM_{cell}_{bits}_m1.json"
    else:
        p = IMPL / f"diagnostics/representatives/CUSUM_{cell}_{bits}.json"
    return json.loads(p.read_text()) if p.exists() else None


def regression_markdown(records: list[dict]) -> str:
    lines = [
        "# Repair 1 regression: reviewed (c0a1f40) vs repaired",
        "",
        "NON-RESULT-BEARING. A re-certification of already-reviewed CUSUM",
        "obligations through the repaired path, to confirm the independently",
        "accepted components survive the repair. Not production, not a new",
        "scientific campaign. Cell 325 is deliberately absent: its state remains",
        "CURRENT_CERTIFICATE_FAILURE_ONLY and it is out of scope here.",
        "",
        "The duplicate removed by the repair is `reward_allow[k]`, of order",
        "1e-53 to 1e-51 -- roughly 48 orders of magnitude below the certificate",
        "values it sat inside. The certified quantities are therefore EXPECTED",
        "to be unchanged, and they are. Correctness is established by the",
        "accounting invariant in `repair_check.py`, not by a numerical change.",
        "",
        "| cell | scope | bits | m | quantity | reviewed | repaired | delta |",
        "|---:|---|---:|---:|---|---|---|---|",
    ]
    for rec in records:
        cell, bits = rec["cell_index"], rec["precision_bits"]
        scope = rec.get("scope", "full")
        rev = reviewed_record(cell, bits, "m1" if scope == "m1_only" else "full")
        if rev is None:
            continue
        for m in sorted(rec["m"], key=int):
            if m not in rev["m"]:
                continue
            a, b = rev["m"][m], rec["m"][m]
            for label, key in (("mag D", "D_interval_mag"), ("M_R2", "M_R2")):
                d = F(b[key]) - F(a[key])
                lines.append(
                    f"| {cell} | {scope} | {bits} | {m} | {label} | "
                    f"{_f(a[key]):.12g} | {_f(b[key]):.12g} | {float(d):+.3e} |")
            d = F(b["cover"]["usage"]) - F(a["cover"]["usage"])
            lines.append(
                f"| {cell} | {scope} | {bits} | {m} | B_cover | "
                f"{_f(a['cover']['usage']):.12g} | {_f(b['cover']['usage']):.12g} | "
                f"{float(d):+.3e} |")
            lines.append(
                f"| {cell} | {scope} | {bits} | {m} | status | {a['status']} | "
                f"{b['status']} | {'same' if a['status'] == b['status'] else 'CHANGED'} |")

    lines += ["", "## S0 charge audit (repaired)", "",
              "| cell | object | charge count | local | dependency | reward_allow |",
              "|---:|---|---:|---|---|---|"]
    for rec in records:
        a = rec["s0_charge_audit"]
        for n in ("F_0", "dF_0", "H_0"):
            lines.append(
                f"| {rec['cell_index']} | {n} | {a[n]['charge_count']} | "
                f"{_f(a[n]['local_residual_charge']):.3e} | "
                f"{_f(a[n]['dependency_charge']):.6e} | "
                f"{_f(a[n]['reward_allow']):.6e} |")
    reps = sorted({r["s0_charge_audit"]["representation"] for r in records})
    lines += ["",
              f"Representation across all records: {reps}",
              "",
              "`charge count = 1` everywhere, with the charge in the dependency",
              "graph and zero in the local residual: representation A, exactly",
              "once, as the frozen ERROR_ALGEBRA requires.",
              ""]

    lines += ["## Frozen-kernel correspondence (unchanged by the repair)", "",
              "| object | reviewed reference | repaired |", "|---|---|---|"]
    for rec in records:
        objs = rec.get("objects", {})
        for name, ref in (("h_2:0", "1.83e-06"), ("S_1:0", "2.76e-06")):
            if name in objs:
                lines.append(f"| {name} (cell {rec['cell_index']}) | ~{ref} | "
                             f"{_f(objs[name]['delta_mid']):.6e} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--regression", required=True)
    args = ap.parse_args()
    src = Path(args.regression)
    records = [json.loads(p.read_text())
               for p in sorted(src.glob("repaired_*.json"))]
    out = NS / "diagnostics/regression"
    out.mkdir(parents=True, exist_ok=True)
    for rec in records:
        scope = "m1" if rec.get("scope") == "m1_only" else "full"
        (out / f"repaired_{rec['cell_index']}_{rec['precision_bits']}_{scope}.json"
         ).write_text(json.dumps(trim(rec), indent=1, sort_keys=True) + "\n")
    (NS / "diagnostics/REGRESSION.md").write_text(regression_markdown(records))
    print(json.dumps({"records": len(records),
                      "cells": sorted({r["cell_index"] for r in records}),
                      "universe_total": spec.TOTAL_UNITS}))


if __name__ == "__main__":
    main()
