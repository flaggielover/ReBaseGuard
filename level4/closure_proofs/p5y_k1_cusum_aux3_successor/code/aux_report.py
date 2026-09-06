"""Reporting and the repeat-run comparison. Contributes to no certificate.

    python code/aux_report.py --determinism REPEATDIR   # write determinism.json
    python code/aux_report.py --write                   # write RESULTS.md
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import ancestry

import aux_audit as audit
import aux_certhash as CH

PRED_DIR = ancestry.CUSUM_NS / "diagnostics" / "cells"
M_ORDER = ("1", "2", "3", "5")


def _fl(s) -> float:
    return float(F(s))


def required_tightening(level: dict) -> float:
    cap = F(level["cover"]["cap"])
    usage = F(level["cover"]["usage"])
    curvature = F(level["cover"]["children"]["curvature"])
    other = usage - curvature
    if cap <= other:
        return float("inf")
    return float(curvature / (cap - other))


def predecessor_records() -> dict:
    out = {}
    for p in sorted(PRED_DIR.glob("succ_CUSUM_*.json")):
        r = json.loads(p.read_text())
        out[r["cell_index"]] = r
    return out


def block_table(recs: dict) -> str:
    rows = ["| cell | rho | m | status | classification | cover util | M_R2 | "
            "nodes tightened |",
            "| ---: | ---: | ---: | :--- | :--- | ---: | ---: | ---: |"]
    for idx, rec in sorted(recs.items()):
        for m in M_ORDER:
            if m not in rec["m"]:
                continue
            L = rec["m"][m]
            rows.append(f"| {idx} | {_fl(rec['rho'][0]):.5f} | {m} | {L['status']} "
                        f"| {audit.classify(L)} | "
                        f"{L['cover']['utilization'] * 100:.2f}% | "
                        f"{_fl(L['M_R2']):.4f} | "
                        f"{rec['node_refinement']['nodes_tightened']} |")
    return "\n".join(rows)


def comparison_table(recs: dict) -> str:
    prev = predecessor_records()
    rows = ["| cell | m | predecessor (70a2943) | this successor | improvement |",
            "| ---: | ---: | :--- | :--- | ---: |"]
    for idx, rec in sorted(recs.items()):
        if idx not in prev:
            continue
        for m in M_ORDER:
            if m not in rec["m"] or m not in prev[idx]["m"]:
                continue
            a, b = prev[idx]["m"][m], rec["m"][m]
            ua, ub = a["cover"]["utilization"], b["cover"]["utilization"]
            rows.append(f"| {idx} | {m} | {ua * 100:.2f}% {a['status']} | "
                        f"{ub * 100:.2f}% {b['status']} | {ua / ub:.2f}x |")
    return "\n".join(rows)


def auxiliary_table(recs: dict) -> str:
    rows = ["| cell | auxiliary objects | aux CPU s | aux share | "
            "nodes considered | nodes tightened | best factor |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for idx, rec in sorted(recs.items()):
        nr = rec["node_refinement"]
        rows.append(f"| {idx} | {len(rec['auxiliary_evidence']['objects'])} | "
                    f"{rec['cpu_seconds_auxiliary']:.0f} | "
                    f"{rec['cpu_seconds_auxiliary'] / rec['cpu_seconds_including_dependencies'] * 100:.1f}% | "
                    f"{nr['nodes_considered']} | {nr['nodes_tightened']} | "
                    f"{nr['best_factor']:.2f}x |"
                    if nr["best_factor"] else
                    f"{nr['nodes_considered']} | {nr['nodes_tightened']} | -- |")
    return "\n".join(rows)


def determinism_section() -> str:
    path = ancestry.NS / "diagnostics" / "determinism.json"
    if not path.exists():
        return "No repeat runs were recorded for this build."
    rep = json.loads(path.read_text())
    rows = ["| cell | recorded hash | fresh repeat | identical | CPU s "
            "(recorded / repeat) |",
            "| ---: | :--- | :--- | :--- | :--- |"]
    for cell, v in sorted(rep["cells"].items(), key=lambda kv: int(kv[0])):
        rows.append(f"| {cell} | `{v['recorded_scientific_hash'][:16]}` | "
                    f"`{v['repeat_scientific_hash'][:16]}` | "
                    f"{'yes' if v['identical'] else '**NO**'} | "
                    f"{v['recorded_cpu_seconds']:.0f} / "
                    f"{v['repeat_cpu_seconds']:.0f} |")
    return "\n".join(rows)


def compare_repeats(repeat_dir) -> dict:
    """Fresh repeats against the committed records, cell by cell."""
    out = {"schema": "k1.cusum-aux3.determinism.v1", "result_bearing": False,
           "cells": {}}
    for repeat in sorted(Path(repeat_dir).glob("aux3_CUSUM_*.json")):
        original = audit.CELLS_DIR / repeat.name
        if not original.exists():
            continue
        a = json.loads(original.read_text())
        b = json.loads(repeat.read_text())
        ha, hb = CH.record_scientific_hash(a), CH.record_scientific_hash(b)
        out["cells"][a["cell_index"]] = {
            "recorded_scientific_hash": ha,
            "repeat_scientific_hash": hb,
            "identical": ha == hb,
            "producer_identical": (a["producer"]["producer_manifest_hash"]
                                   == b["producer"]["producer_manifest_hash"]),
            "auxiliary_hash_identical": (a["auxiliary_evidence_hash"]
                                         == b["auxiliary_evidence_hash"]),
            "runtime_fields_differed": (a["cpu_seconds_including_dependencies"]
                                        != b["cpu_seconds_including_dependencies"]),
            "recorded_cpu_seconds": a["cpu_seconds_including_dependencies"],
            "repeat_cpu_seconds": b["cpu_seconds_including_dependencies"],
        }
    out["all_identical"] = bool(out["cells"]) and all(
        v["identical"] and v["producer_identical"] and v["auxiliary_hash_identical"]
        for v in out["cells"].values())
    return out


def results_markdown() -> str:
    rep = audit.run()
    recs = audit.records()
    sci, cost, prov = rep["science"], rep["cost"], rep["provenance"]
    resolved = sci["previously_failing_now_pass"]
    still = sci["still_open"]
    return f"""# Results — CUSUM aux3 successor

**Verdict: `{rep['verdict']}`.**
CUSUM compact cover: `{sci['cusum_compact_cover']}`. Far field: inherited `PASS`.
Not production, not result-bearing, no cell claimed closed beyond its own
certificate.

## The five obligations this task targeted

The predecessor left exactly five failures: (319,5), (320,5), (321,5), (322,5),
(323,5). After the auxiliary third-derivative refinement:
**{len(resolved)} of 5 now PASS**{'' if not still else ', still open: ' + ', '.join(f'({c},{m})' for c, m in still)}.

## Counts, stated exactly

* cells 318–324: **{sci['block_318_324_pass']} of {sci['block_318_324_obligations']}** obligations PASS
* cells 318–325: **{sci['with_control_318_325_pass']} of {sci['with_control_318_325_obligations']}** obligations PASS
* cell 325 regression control: {'clean, all m PASS' if sci['control_regression_clean'] else '**REGRESSED**'}

{block_table(recs)}

## Against the predecessor (70a2943)

{comparison_table(recs)}

## Auxiliary evidence

Nested third-derivative certificates (`h'''`, `S'''`, `W'''`) owned by the cell's
existing curvature obligations. No top-level work id, no DAG node: the frozen
universe stays at 17,978.

{auxiliary_table(recs)}

## Provenance

| | |
| --- | --- |
| producer manifest hash | `{prov['producer_manifest_hash']}` |
| manifest schema | `{prov['producer_manifest_schema']}` |
| committed artifact | `{prov['producer_manifest_path']}` |
| files bound | {prov['manifest_files']} |
| manifest verifies from disk | {prov['manifest_verifies']} |
| strict coverage in the certifying process | {prov['strict_coverage_in_certifying_process']} |

## Determinism

{determinism_section()}

## Cost

`COST_CAP` remains **NOT_ESTABLISHED**. {cost['contention_note']}
Auxiliary evidence costs {cost['auxiliary_share'] and f"{cost['auxiliary_share'] * 100:.1f}%"} of the per-cell CPU.
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--determinism")
    args = ap.parse_args()
    if args.determinism:
        rep = compare_repeats(args.determinism)
        path = ancestry.NS / "diagnostics" / "determinism.json"
        path.write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n")
        print(json.dumps(rep, indent=2, sort_keys=True))
        return
    text = results_markdown()
    if args.write:
        (ancestry.NS / "RESULTS.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
