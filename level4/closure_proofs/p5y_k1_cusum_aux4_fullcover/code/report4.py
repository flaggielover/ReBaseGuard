"""Reporting, determinism comparison and the cost model. Not certifying.

    python code/report4.py --determinism DIR_A DIR_B   # write determinism.json
    python code/report4.py --cost-model DIR            # write cost_model.json
    python code/report4.py --write                     # write RESULTS.md
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import ancestry4

import spec

import aggregate_ledger
import audit4
import hash_v2 as H
import manifest_v2

M_ORDER = ("1", "2", "3", "5")
DIFFICULT = ((319, "5"), (320, "5"), (321, "5"), (322, "5"), (323, "5"))


def _fl(s) -> float:
    return float(F(s))


# ------------------------------------------------------------- determinism
def _scientific_slices(rec: dict) -> dict:
    """The exact scientific quantities two honest repeats must agree on."""
    return {
        "intervals": {m: {k: rec["m"][m][k] for k in
                          ("R_interval", "D_interval", "R2_interval", "M_R2")}
                      for m in sorted(rec["m"], key=int)},
        "error_bounds": {"eps_mid": rec["eps_mid"], "eps_cell": rec["eps_cell"],
                         "eps_cell_refined": rec["eps_cell_refined"]},
        "objects": {n: {k: v for k, v in o.items()
                        if k in ("delta_mid", "delta_cell", "envelope")}
                    for n, o in rec["objects"].items()},
        "auxiliary": {n: {k: v for k, v in o.items()
                          if k in ("delta_mid", "envelope",
                                   "polynomial_residual",
                                   "truncation_allowance")}
                      for n, o in rec["auxiliary_evidence"]["objects"].items()},
        "candidate_suprema": rec["auxiliary_evidence"]["candidate_suprema"],
    }


def compare_repeats(dir_a, dir_b) -> dict:
    out = {"schema": "k1.cusum-aux4.determinism.v2", "result_bearing": False,
           "cells": {}}
    a_files = {int(p.stem.split("_")[2]): p
               for p in Path(dir_a).glob("aux4_CUSUM_*.json")}
    b_files = {int(p.stem.split("_")[2]): p
               for p in Path(dir_b).glob("aux4_CUSUM_*.json")}
    for idx in sorted(set(a_files) & set(b_files)):
        a = json.loads(a_files[idx].read_text())
        b = json.loads(b_files[idx].read_text())
        sa, sb = _scientific_slices(a), _scientific_slices(b)
        out["cells"][idx] = {
            "scientific_hash_identical": (a["scientific_content_hash"]
                                          == b["scientific_content_hash"]),
            "scientific_hash": a["scientific_content_hash"],
            "auxiliary_hash_identical": (a["auxiliary_evidence_hash"]
                                         == b["auxiliary_evidence_hash"]),
            "producer_identical": (a["producer"]["producer_identity_hash"]
                                   == b["producer"]["producer_identity_hash"]),
            "runtime_identical": (a["producer"]["runtime_contract_hash"]
                                  == b["producer"]["runtime_contract_hash"]),
            "intervals_identical": sa["intervals"] == sb["intervals"],
            "error_bounds_identical": sa["error_bounds"] == sb["error_bounds"],
            "objects_identical": sa["objects"] == sb["objects"],
            "auxiliary_objects_identical": sa["auxiliary"] == sb["auxiliary"],
            "candidate_suprema_identical": (sa["candidate_suprema"]
                                            == sb["candidate_suprema"]),
            "runtime_fields_differed": (a["cpu_seconds_including_dependencies"]
                                        != b["cpu_seconds_including_dependencies"]),
            "cpu_seconds": [a["cpu_seconds_including_dependencies"],
                            b["cpu_seconds_including_dependencies"]],
            "recomputes": (H.record_scientific_hash(a) == a["scientific_content_hash"]
                           and H.record_scientific_hash(b) == b["scientific_content_hash"]),
        }
    out["all_identical"] = bool(out["cells"]) and all(
        all(v[k] for k in ("scientific_hash_identical", "auxiliary_hash_identical",
                           "producer_identical", "runtime_identical",
                           "intervals_identical", "error_bounds_identical",
                           "objects_identical", "auxiliary_objects_identical",
                           "candidate_suprema_identical", "recomputes"))
        for v in out["cells"].values())
    return out


# -------------------------------------------------------------------- cost
def cost_model(measure_dir) -> dict:
    """Per-cell cost measured under clean conditions, projected to 326 cells."""
    recs = [json.loads(p.read_text())
            for p in sorted(Path(measure_dir).glob("aux4_CUSUM_*.json"))]
    if not recs:
        return {"measured": False}
    cpu = [r["cpu_seconds_including_dependencies"] for r in recs]
    rss = [r["peak_rss_kib"] / 1024 for r in recs]
    aux = [r["cpu_seconds_auxiliary"] for r in recs]
    mean = sum(cpu) / len(cpu)
    worst = max(cpu)
    # 8 logical CPUs on 4 physical cores: hyperthread pairs share an execution
    # unit, so 8 workers cost about 2x the CPU seconds of 4 for the same wall
    # time. 4 workers is therefore strictly cheaper in CPU-hours.
    physical_cores = 4
    projected_cpu_h = 326 * mean / 3600
    projected_wall_h = 326 * mean / physical_cores / 3600
    return {
        "measured": True,
        "cells_measured": sorted(r["cell_index"] for r in recs),
        "conditions": f"{physical_cores} workers on {physical_cores} physical "
                      f"cores (8 logical), one thread each",
        "cpu_seconds_per_cell_mean": round(mean, 1),
        "cpu_seconds_per_cell_worst": round(worst, 1),
        "auxiliary_cpu_seconds_mean": round(sum(aux) / len(aux), 1),
        "auxiliary_share": round(sum(aux) / sum(cpu), 4),
        "peak_rss_mib_per_worker": round(max(rss), 1),
        "physical_cores": physical_cores,
        "logical_cpus": 8,
        "chosen_workers": physical_cores,
        "worker_choice_rationale":
            "8 logical CPUs are 4 hyperthreaded cores. Measured on the "
            "predecessor, 8 workers inflate per-cell CPU by 2.04x for the same "
            "wall time, so 4 workers deliver the same throughput at half the "
            "CPU-hours. CPU-hours are the governed quantity.",
        "projected_cusum_cpu_hours": round(projected_cpu_h, 1),
        "projected_cusum_wall_hours": round(projected_wall_h, 1),
        "hard_cap_cpu_hours": spec.HARD_CAP_CPU_H,
        "cusum_share_of_cap": round(projected_cpu_h / spec.HARD_CAP_CPU_H, 4),
        "cusum_only_exceeds_hard_cap": projected_cpu_h > spec.HARD_CAP_CPU_H,
        "scope_note": "the cap governs the COMPLETE K1 campaign. SR (316 cells) "
                      "is unimplemented and unmeasured, so this is the CUSUM "
                      "contribution only and implies nothing about campaign cost.",
    }


# ----------------------------------------------------------------- results
def block_table(records: dict) -> str:
    rows = ["| cell | m | status | cover util | M_R2 |",
            "| ---: | ---: | :--- | ---: | ---: |"]
    for idx in sorted(records):
        rec = records[idx]
        for m in M_ORDER:
            if m not in rec["m"]:
                continue
            L = rec["m"][m]
            rows.append(f"| {idx} | {m} | {L['status']} | "
                        f"{L['cover']['utilization'] * 100:.2f}% | "
                        f"{_fl(L['M_R2']):.4f} |")
    return "\n".join(rows)


def results_markdown() -> str:
    rep = audit4.run()
    ledger_path = ancestry4.NS / "diagnostics" / "aggregate_ledger.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else None
    records = {}
    for p in sorted((ancestry4.NS / "diagnostics" / "cells").glob("aux4_CUSUM_*.json")):
        r = json.loads(p.read_text())
        records[r["cell_index"]] = r
    sci, prov, cost = rep["science"], rep["provenance"], rep["cost"]
    difficult = {f"{c},m{m}": records[c]["m"][m]["status"]
                 for c, m in DIFFICULT if c in records}
    hard = {k: v for k, v in sorted(records.items()) if k in range(318, 326)}
    return f"""# Results — CUSUM Aux4 full cover

**Verdict: `{rep['verdict']}`.**
CUSUM full cover: `{sci['cusum_full_cover']}`. Far field: inherited `PASS`.
Not production, not result-bearing.

## Cover state

* cells certified under the Aux4 producer: **{sci['cells_certified']} of 326**
* obligations PASS: **{sci['obligations_pass']} of {sci['obligations_certified']}** certified
* cell 325 control all-`m` PASS: {sci['control_325_all_pass']}
* difficult cells: {json.dumps(difficult)}

No predecessor certificate is composed into this ledger: adjudication required a
full 326-cell rerun under a new producer, and the ledger admits a cell only if it
carries this namespace's producer identity.

## Producer identity

| | |
| --- | --- |
| manifest schema | `{prov['producer_manifest_schema']}` |
| manifest path | `{prov['producer_manifest_path']}` |
| manifest hash | `{prov['producer_manifest_hash']}` |
| runtime contract hash | `{prov['runtime_contract_hash']}` |
| producer identity hash | `{prov['producer_identity_hash']}` |
| files bound | {prov['manifest_file_count']} |
| OpenBLAS runtime kernel | `{prov['runtime_contract']['openblas_runtime_corename']}` |

## Cost

`COST_CAP` remains **NOT_ESTABLISHED**. {cost['scope_note']}

{json.dumps(cost.get('cost_model', {}), indent=2)}

## Cells 318–325 (the previously difficult block)

{block_table(hard)}
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--determinism", nargs=2, metavar=("DIR_A", "DIR_B"))
    ap.add_argument("--cost-model", metavar="DIR")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    diag = ancestry4.NS / "diagnostics"
    diag.mkdir(parents=True, exist_ok=True)
    if args.determinism:
        rep = compare_repeats(*args.determinism)
        (diag / "determinism.json").write_text(
            json.dumps(rep, indent=2, sort_keys=True) + "\n")
        print(json.dumps(rep, indent=2, sort_keys=True))
        return
    if args.cost_model:
        model = cost_model(args.cost_model)
        (diag / "cost_model.json").write_text(
            json.dumps(model, indent=2, sort_keys=True) + "\n")
        print(json.dumps(model, indent=2, sort_keys=True))
        return
    text = results_markdown()
    if args.write:
        (ancestry4.NS / "RESULTS.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
