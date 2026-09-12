"""Phase 4 analysis: measured PS1 production-unit cost per cell and the full-campaign projection; end-to-end identity
of the qualification cells that were certified before (150, 360-363, 368) against their certified T4/T5 science."""
import glob
import json
import math
import statistics
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
O = NS / "evidence/qual"
CERT = NS.parent / "p5y_k1_sr_o9_partition_successor/evidence/certified"
PARENT = {150: 150, 360: 313, 361: 313, 362: 313, 363: 313, 368: 315}
GROUPS = [[0, 1, 2, 3], [148, 149, 150, 151], [360, 361, 362, 363], [368]]
N_CELLS, GROUP = 369, 4


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, max(0, math.ceil(q * len(v)) - 1))]


def main():
    patch_cpu, inputs_cpu = {}, {}
    for f in glob.glob(str(O / "chunks/rec_*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            patch_cpu[r["successor_cell"]] = patch_cpu.get(r["successor_cell"], 0.0) + r["cpu_seconds"]
    for f in glob.glob(str(O / "chunks/inputs_g*.json")):
        d = json.loads(Path(f).read_text())
        for s in d["group"]:
            inputs_cpu[s] = inputs_cpu.get(s, 0.0) + d["cell_inputs_cpu_s"] / len(d["group"])
    stage = {}
    for s in patch_cpu:
        p = O / f"stages/summary_s{s}.json"
        if p.exists():
            m = json.loads(p.read_text())
            stage[s] = m["cpu_s"]["t3_aggregate"] + m["cpu_s"]["t4_t5"]
    cells = {}
    for s in sorted(patch_cpu):
        tot = patch_cpu[s] + inputs_cpu.get(s, 0.0) + stage.get(s, 0.0)
        cells[str(s)] = {"patch_cpu_h": patch_cpu[s] / 3600, "inputs_cpu_h": inputs_cpu.get(s, 0.0) / 3600,
                         "t3agg_t4_t5_cpu_h": stage.get(s, 0.0) / 3600, "total_cpu_h": tot / 3600}
    groups = []
    for g in GROUPS:
        if all(str(s) in cells for s in g):
            groups.append({"group": g, "cpu_h": sum(cells[str(s)]["total_cpu_h"] for s in g),
                           "per_cell_cpu_h": sum(cells[str(s)]["total_cpu_h"] for s in g) / len(g)})
    g4 = [x["per_cell_cpu_h"] for x in groups if len(x["group"]) == GROUP]
    single = [x["per_cell_cpu_h"] for x in groups if len(x["group"]) == 1]
    per_cell_all = [c["total_cpu_h"] for c in cells.values()]
    mean_g4 = statistics.mean(g4) if g4 else None
    worst_g4 = max(g4) if g4 else None
    proj_mean = (N_CELLS - 1) * mean_g4 + (single[0] if single else mean_g4)
    proj_worst = (N_CELLS - 1) * worst_g4 + (single[0] if single else worst_g4)
    ident = {}
    for s, par in PARENT.items():
        p = O / f"stages/t4_s{s}.json"
        if not p.exists():
            continue
        q4, c4 = json.loads(p.read_text()), json.loads((CERT / f"parent_{par}/t4_s{s}.json").read_text())
        q5, c5 = json.loads((O / f"stages/t5_s{s}.json").read_text()), json.loads((CERT / f"parent_{par}/t5_s{s}.json").read_text())
        q3, c3 = json.loads((O / f"stages/t3_s{s}.json").read_text()), json.loads((CERT / f"parent_{par}/t3_s{s}.json").read_text())
        ident[str(s)] = {
            "t3_delta_and_x0_identical": q3["delta"] == c3["delta"] and q3["x0_images"] == c3["x0_images"],
            "t3_consumed_records_identical": q3["consumed_records_sha256"] == c3["consumed_records_sha256"],
            "t4_ledgers_identical": all(q4["m"][m] == c4["m"][m] for m in c4["m"]) and q4["B_cover_ratio"] == c4["B_cover_ratio"],
            "t5_statuses_identical": [o["status"] for o in q5["obligations"]] == [o["status"] for o in c5["obligations"]],
            "t5_pass": q5["pass_count"]}
    t5s = {}
    for s in patch_cpu:
        p = O / f"stages/t5_s{s}.json"
        if p.exists():
            t5 = json.loads(p.read_text())
            t5s[str(s)] = {"status": t5["status"], "pass": t5["pass_count"],
                           "B_cover_ratio": json.loads((O / f"stages/t4_s{s}.json").read_text())["B_cover_ratio"]}
    out = {"schema": "rebaseguard.p5y.k1.ps1.cost-qualification.v1", "workers": 16, "pinning": "physical cores 0-15",
           "unit": "deterministic group of 4 consecutive cells, patch-outer, shared per-patch panel cache",
           "cells": cells, "groups": groups, "per_cell_cpu_h_stats": {
               "n": len(per_cell_all), "mean": statistics.mean(per_cell_all), "p50": pct(per_cell_all, 0.5),
               "p90": pct(per_cell_all, 0.9), "max": max(per_cell_all), "min": min(per_cell_all)},
           "group4_per_cell_cpu_h": {"mean": mean_g4, "max": worst_g4, "values": g4}, "terminal_single_cpu_h": single,
           "projection_cpu_h": {"mean_based": proj_mean, "worst_group_based": proj_worst,
                                "mean_plus_10pct": proj_mean * 1.10, "mean_plus_15pct": proj_mean * 1.15,
                                "worst_plus_10pct": proj_worst * 1.10},
           "identity_vs_certified": ident, "t5": t5s,
           "all_qualification_cells_28_of_28": all(v["status"] == "T5_28_OF_28_PASS" for v in t5s.values()) and len(t5s) == len(patch_cpu)}
    (NS / "evidence/qual_summary.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("per_cell_cpu_h_stats", "group4_per_cell_cpu_h", "terminal_single_cpu_h",
                                         "projection_cpu_h", "all_qualification_cells_28_of_28")}, indent=1))
    print(json.dumps(ident, indent=1))


if __name__ == "__main__":
    main()
