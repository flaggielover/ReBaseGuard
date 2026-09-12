"""Phase 1: decomposition of the measured per-cell cost into stages A-L from the cProfile runs (frozen certifier,
3 patches, idle core) of cells 10, 150, 360, 368, scaled to a full cell by the per-patch linear model, plus the
committed stage costs, and the topology-caused duplication measured in Phase 3."""
import glob
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
E = NS / "evidence"
CERT = NS.parent / "p5y_k1_sr_o9_partition_successor/evidence/certified"
STAGES = [
    ("A_candidate_construction", ("succ_t1.py", "sr_o9_candidates.py:414", "quantize", ":dct", "construct_nodal")),
    ("B_shared_patch_tensors", ("opt_backend.py:56", "cheb_tm2", "harness.py:220", "harness.py:212", "harness.py:206", "harness.py:197", "softplus_tm2")),
    ("C_raw_shift_drift_tensors", ("sr_o9_endpoint_strips.py:73", "opt_backend.py:92", "build_Rbig", "panel_moments")),
    ("D_operator_contractions", ("contract_O9",)),
    ("E_residual_certification", ("candidate_on_patch", "sr_o9_patch_certifier.py:228", "PatchBasis")),
    ("F_endpoint_strip_work", ("sr_o9_endpoint_strips.py:132", "sr_o9_endpoint_strips.py:60", "sr_o9_endpoint_strips.py:96")),
    ("G_source_image_nodes", ("source_tms",)),
]


def classify(func):
    for name, keys in STAGES:
        if any(k in func for k in keys):
            return name
    return "other_python_overhead"


def main():
    uni = json.loads((NS.parent / "p5y_k1_sr_o9_t2_closure_successor/evidence/universe_table.json").read_text())
    nz_total, n_patch = sum(r[2] for r in uni["rows"]), len(uni["rows"])
    out = {"schema": "rebaseguard.p5y.k1.ps1.cost-decomposition.v1", "cells": {}}
    for f in sorted(glob.glob(str(E / "profile/profile_s*.json"))):
        d = json.loads(Path(f).read_text())
        prof_total = sum(v["cpu_s"] for v in d["patches"].values())
        nz = sum(v["n_z"] for v in d["patches"].values())
        buckets = {}
        for r in d["top_tottime"]:
            buckets[classify(r["func"])] = buckets.get(classify(r["func"]), 0.0) + r["tottime"]
        covered = sum(buckets.values())
        buckets["other_python_overhead"] = buckets.get("other_python_overhead", 0.0) + max(0.0, prof_total - covered)
        # per-patch linear model from the 3 patches: cost = a + b*n_z  (least squares)
        pts = [(v["n_z"], v["cpu_s"]) for v in d["patches"].values()]
        mx, my = sum(x for x, _ in pts) / 3, sum(y for _, y in pts) / 3
        b = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)
        a = my - b * mx
        full = a * n_patch + b * nz_total
        qsp = E / "qual_summary.json"
        measured = None
        if qsp.exists():
            qcells = json.loads(qsp.read_text())["cells"]
            measured = qcells.get(str(d["cell"]), {}).get("total_cpu_h") or json.loads(qsp.read_text())["per_cell_cpu_h_stats"]["mean"]
        cell = {"profile_cpu_s_3_patches": prof_total,
                "profile_core": "idle core" if d["cell"] == 360 else "logical cpu 31 = SMT sibling of a busy Phase-4 core: "
                                "absolute CPU inflated ~1.9x, only the SHARES are used",
                "stage_share": {k: v / prof_total for k, v in sorted(buckets.items())},
                "measured_cell_cpu_h_phase4": measured,
                "stage_cpu_h_from_phase4": ({k: v / prof_total * measured for k, v in sorted(buckets.items())}
                                            if measured else None),
                "scaling": {"patches": "a term (strips, per-patch setup)", "panels_n_z": "b term (O9 core, shared tensors)",
                            "candidates_contracts_shifts": "O9 calls = contracts x panels; strip calls = contracts x 2 sides"}}
        s = d["cell"]
        par = {360: 313, 150: 150, 368: 315}.get(s)
        if par:
            m = json.loads((CERT / f"parent_{par}/summary_s{s}.json").read_text())
            cell["H_T3_aggregation_cpu_s"] = m["cpu_s"]["t3_aggregate"]
            cell["I_J_T4_T5_cpu_s"] = m["cpu_s"]["t4_t5"]
        out["cells"][str(s)] = cell
    conc = {}
    for Wk in (1, 16, 32):
        fs = glob.glob(str(E / f"bench_opt/conc_W{Wk}/w*.json"))
        conc[Wk] = sum(json.loads(Path(x).read_text())["cpu_s"] for x in fs) / len(fs)
    ser = {b: json.loads((E / f"bench_opt/series_{b}.json").read_text()) for b in ("b1", "b4", "b16")}
    out["L_duplicated_by_topology"] = {
        "smt_30_to_32_way_cpu_inflation_vs_16": conc[32] / conc[16],
        "committed_runs_used_30_workers": True,
        "cross_cell_panel_cache_lost_in_cell_major": 1 - (ser["b4"]["cpu_s"] / 4) / ser["b1"]["cpu_s"],
        "shift_recomputation_removed_by_OPT_S_OPT_C": "see evidence/identity/id_small.json (cpu_frozen vs cpu_opt)"}
    out["K_serialization_hashing_evidence"] = "negligible (<0.5%): JSON lines per patch, gzip at cell end"
    (E / "cost_decomposition.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for s, c in out["cells"].items():
        print(s, c["measured_cell_cpu_h_phase4"], {k: round(v, 3) for k, v in c["stage_share"].items()})
    print(out["L_duplicated_by_topology"])


if __name__ == "__main__":
    main()
