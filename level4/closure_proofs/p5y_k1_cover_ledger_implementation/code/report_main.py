"""Entry point that assembles the committed non-result-bearing evidence.

    usage: report_main.py --representatives DIR --precision DIR

The representative directory holds the full four-m records at the frozen 256
bits; the precision directory holds the m=1 scoped records at 256 / 384 / 512.
They are kept apart because they are different scopes and must not be mixed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import report
import spec
import universe

NS = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--representatives", required=True)
    ap.add_argument("--precision", required=True)
    args = ap.parse_args()

    base = [json.loads(p.read_text())
            for p in sorted(Path(args.representatives).glob("CUSUM_*_256.json"))]
    base = [r for r in base if "m" in r and r.get("scope") != "m1_only"]
    base.sort(key=lambda r: r["cell_index"])

    prec: dict = {}
    for p in sorted(Path(args.precision).glob("CUSUM_*_m1.json")):
        r = json.loads(p.read_text())
        prec.setdefault(int(r["cell_index"]), {})[int(r["precision_bits"])] = r

    report.write_representatives(base)
    sr_note = {
        "status": "NOT_IMPLEMENTED",
        "reason": ("no raw-variable SR DAG exists in the repository; Task1R "
                   "certified the F_0 class only, on one patch at one drift, in "
                   "a different (softplus Taylor-model) formulation")}
    (NS / "diagnostics/REPRESENTATIVE_LEDGER.md").write_text(
        report.ledger_markdown(base, sr_note))

    if prec:
        (NS / "diagnostics/PRECISION.md").write_text(report.precision_markdown(prec))
        (NS / "diagnostics/precision.json").write_text(json.dumps(
            {"schema": "k1.cover-ledger.precision-diagnostic.v1",
             "scope": "m=1 obligation (assembly.coefficients(1) == [(F,0,0,1)]),"
                      " complete for that obligation",
             "production_precision_bits": spec.PRODUCTION_BITS,
             "precision_escalation_allowed": False,
             "result_bearing": False, "production_run": False,
             "nesting": report.nesting_report(prec),
             "cpu_seconds": {f"cell{c}_{b}": r["cpu_seconds_including_dependencies"]
                             for c, by in prec.items() for b, r in by.items()}},
            indent=1, sort_keys=True) + "\n")
        d = NS / "diagnostics/precision_records"
        d.mkdir(parents=True, exist_ok=True)
        for c, by in prec.items():
            for b, r in by.items():
                (d / f"CUSUM_{c}_{b}_m1.json").write_text(
                    json.dumps(report.trim(r), indent=1, sort_keys=True) + "\n")

    report.write_manifest(universe.implementation_hash())
    print(json.dumps({"representative_records": len(base),
                      "precision_cells": sorted(prec),
                      "universe_total": spec.TOTAL_UNITS}))


if __name__ == "__main__":
    main()
