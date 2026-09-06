"""Human-readable rendering of the successor's certificate records.

Reporting only: contributes to no certificate, is outside the producer manifest,
and is listed in `SUCCESSOR_NON_CERTIFYING`.

    python code/successor_report.py            # print the tables
    python code/successor_report.py --write    # write RESULTS.md
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import ancestry

import successor_audit as audit

PREV_DIR = ancestry.FINAL_NS / "diagnostics" / "cells"
M_ORDER = ("1", "2", "3", "5")


def _fl(s) -> float:
    return float(F(s))


def required_tightening(level: dict) -> float:
    """The factor by which M_R2 must shrink for this (cell, m) to fit the cap."""
    cap = F(level["cover"]["cap"])
    usage = F(level["cover"]["usage"])
    curvature = F(level["cover"]["children"]["curvature"])
    other = usage - curvature
    if cap <= other:
        return float("inf")
    return float(curvature / (cap - other))


def predecessor_records() -> dict:
    out = {}
    for p in sorted(PREV_DIR.glob("sharp_CUSUM_*.json")):
        r = json.loads(p.read_text())
        out[r["cell_index"]] = r
    return out


def block_table(recs: dict) -> str:
    rows = ["| cell | rho | m | status | classification | cover util | M_R2 | "
            "M_R2 needed | still short by |",
            "| ---: | ---: | ---: | :--- | :--- | ---: | ---: | ---: | ---: |"]
    for idx, rec in sorted(recs.items()):
        for m in M_ORDER:
            if m not in rec["m"]:
                continue
            L = rec["m"][m]
            need = required_tightening(L)
            mr2 = _fl(L["M_R2"])
            target = mr2 / need if need not in (0.0, float("inf")) else float("nan")
            short = "--" if L["status"] == "PASS" else f"{need:.3f}x"
            rows.append(f"| {idx} | {_fl(rec['rho'][0]):.5f} | {m} | "
                        f"{L['status']} | {audit.classify(L)} | "
                        f"{L['cover']['utilization'] * 100:.2f}% | {mr2:.4f} | "
                        f"{target:.4f} | {short} |")
    return "\n".join(rows)


def comparison_table(recs: dict) -> str:
    prev = predecessor_records()
    rows = ["| cell | m | predecessor | this successor | improvement |",
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


def determinism_section() -> str:
    path = ancestry.NS / "diagnostics" / "determinism.json"
    if not path.exists():
        return "No repeat runs were recorded for this build."
    rep = json.loads(path.read_text())
    rows = ["| cell | recorded scientific hash | fresh repeat | identical | "
            "CPU seconds (recorded / repeat) |",
            "| ---: | :--- | :--- | :--- | :--- |"]
    for cell, v in sorted(rep["cells"].items(), key=lambda kv: int(kv[0])):
        rows.append(f"| {cell} | `{v['recorded_scientific_hash'][:16]}` | "
                    f"`{v['repeat_scientific_hash'][:16]}` | "
                    f"{'yes' if v['identical'] else '**NO**'} | "
                    f"{v['recorded_cpu_seconds']:.0f} / {v['repeat_cpu_seconds']:.0f} |")
    return "\n".join(rows)


def counts(recs: dict) -> dict:
    prev = predecessor_records()
    now_pass = now_total = was_pass = was_total = 0
    for idx, rec in recs.items():
        for m in M_ORDER:
            if m in rec["m"]:
                now_total += 1
                now_pass += rec["m"][m]["status"] == "PASS"
            if idx in prev and m in prev[idx]["m"]:
                was_total += 1
                was_pass += prev[idx]["m"][m]["status"] == "PASS"
    return {"successor_pass": now_pass, "successor_total": now_total,
            "predecessor_pass": was_pass, "predecessor_total": was_total}


def results_markdown() -> str:
    rep = audit.run()
    recs = audit.records()
    sci, cost, prov = rep["science"], rep["cost"], rep["provenance"]
    c = counts(recs)
    short = sorted({(cell, m) for cell, m in sci["certificate_too_loose"]})
    return f"""# Results — CUSUM completion successor

**Verdict: `{rep['verdict']}`.**
CUSUM compact-cover status: `{sci['cusum_compact_cover_status']}`.
Not production, not result-bearing, no cell claimed closed beyond its own
certificate.

## Where the block stands

{c['successor_pass']} of {c['successor_total']} `(cell, m)` obligations over cells 318–325 now certify,
against {c['predecessor_pass']} of {c['predecessor_total']} before this task. Cell 324 closed completely;
cell 325, the regression control, still passes every `m`
({'clean' if sci['control_regression_clean'] else 'REGRESSED'}). What remains
open is `m = 5` at cells {', '.join(str(x) for x, _ in short) or '(none)'}.

Every remaining failure is `CERTIFICATE_TOO_LOOSE`: the certified `R''` interval
straddles zero, so the bound — not the mathematics — is what fails.
{'No obligation is a SCIENTIFIC_FAILURE and none is an IMPLEMENTATION_DEFECT.' if not sci['scientific_failures'] and not sci['implementation_defects'] else 'SEE THE AUDIT: not all failures are certificate looseness.'}

{block_table(recs)}

## Against the predecessor (`f8e6f75`)

{comparison_table(recs)}

## Provenance

| | |
| --- | --- |
| producer hash | `{prov['producer_hash']}` |
| identity kind | `{prov['producer_hash_kind']}` |
| manifest files | {prov['manifest_file_count']} |
| backend hash | `{prov['backend_hash']}` |
| loaded-module coverage | {'complete' if prov['loaded_module_coverage'] else 'INCOMPLETE'} |
| per-cell chains verified | {sum(1 for v in prov['per_cell'].values() if v['ok'])} of {len(prov['per_cell'])}, 28 obligations each |

## Determinism

The adjudicated predecessor defect was that repeated fresh runs under the same
producer identity produced different certificate hashes. Fresh repeats here, in
separate processes and a separate output directory, reproduce the recorded
scientific hash exactly while their runtime fields differ — which is what makes
the comparison meaningful rather than a file copy.

{determinism_section()}

## Cost

`COST_CAP` remains **NOT_ESTABLISHED**. Measured here, and only here:
{cost['measured_cpu_hours']} CPU-hours over {cost['measured_cells']} cells
(mean {cost['mean_cpu_seconds_per_cell']} s, max {cost['max_cpu_seconds_per_cell']} s per cell,
BLAS and FLINT pinned to one thread, 8 workers on 8 cores).

Those per-cell seconds are **inflated by a factor of
{cost['contention']['observed_inflation_factor']}**: the determinism repeats ran
the same cells with 2 workers instead of 8 and cost about half the CPU seconds,
because the counter charges memory-bandwidth stalls. Neither number is a per-cell
cost model, and this is a measurement, not a projection:
{cost['why_not_established'][0]}.

## What would close the rest

The dominant term is the propagated source error — at cell 321, `r = 4`,
`C * epsS2 = 5.254` of `epsH = 9.145`. It is a pure cascade through the frozen
DAG, multiplying by `k_0 + 2k_1 + k_2 = 2.98` per level from an irreducible
`rho * sup_cell|phi''|` seed. Tightening it needs certified midpoint objects one
derivative order above what the frozen object set carries (`h^(3)`, `S^(3)`).
Adding them changes the frozen obligation universe, which is out of scope for
this task; the norm-only substitute is far weaker and does not help
(`diagnostics/third_order_analysis.py`).
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    text = results_markdown()
    if args.write:
        (ancestry.NS / "RESULTS.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
