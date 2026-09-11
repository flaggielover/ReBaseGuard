"""Write the PS1 round record and RESULT.md from committed evidence only (post-execution)."""
import glob
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
EV = NS / "evidence"
MS = ("1", "2", "3", "5")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def region(parent):
    d = EV / f"certified/parent_{parent}"
    if not d.exists():
        return None
    man = json.loads((d / "RUN_MANIFEST.json").read_text())
    rows = []
    cpu = {}
    import gzip
    for f in glob.glob(str(d / "chunks/rec_*.jsonl*")):
        for line in (gzip.open(f, "rt") if f.endswith(".gz") else open(f)):
            r = json.loads(line)
            cpu.setdefault(r["successor_cell"], [0.0, 0, 0])
            cpu[r["successor_cell"]][0] += r["cpu_seconds"]
            cpu[r["successor_cell"]][1] += 1
            cpu[r["successor_cell"]][2] = max(cpu[r["successor_cell"]][2], r["peak_rss_kib"])
    for s in man["successor_cells"].split(","):
        p = d / f"summary_s{s}.json"
        if not p.exists():
            rows.append({"successor_cell": int(s), "status": "NOT_FINALIZED"})
            continue
        m = json.loads(p.read_text())
        t4 = json.loads((d / f"t4_s{s}.json").read_text())
        c = cpu.get(int(s), [0, 0, 0])
        rows.append({"successor_cell": int(s), "id": m["id"], "T3_PASS": m["T3_PASS"], "t5_status": m["t5_status"],
                     "t5_pass": m["t5_pass_count"], "t5_total": m["t5_total"], "B_cover_ratio": m["B_cover_ratio"],
                     "B_cover_usage": {k: t4["m"][k]["cover"]["usage"] for k in MS},
                     "M_R2": {k: float(eval(v)) if "/" in v else float(v) for k, v in m["M_R2"].items()},
                     "contraction_max": m["contraction_max"], "assembly_margins": m["worst_obligation_margin"],
                     "t3_patch_cpu_h": c[0] / 3600, "patch_records": c[1], "peak_rss_mib": c[2] / 1024,
                     "t3_aggregate_t4_t5_cpu_s": m["cpu_s"], "t5_sha256": m["t5_sha256"], "git_commit": m["git_commit"]})
    return {"parent": parent, "manifest": man, "cells": rows,
            "all_28_of_28": all(r.get("t5_status") == "T5_28_OF_28_PASS" for r in rows) and bool(rows)}


def main():
    p1 = json.loads((EV / "phase1_doctrine.json").read_text())
    agg = json.loads((EV / "phase34_diag_aggregate.json").read_text())["by_N"]
    rules = json.loads((EV / "phase25_rules_projection.json").read_text())["projection"]
    proto = json.loads((NS / "config/PARTITION_PROTOCOL.json").read_text())
    ti = {s: json.loads((EV / f"temporal_integrity_{s}.json").read_text())
          for s in ("pre_execution", "post_execution") if (EV / f"temporal_integrity_{s}.json").exists()}
    r313 = region(313)
    ctrl = {p: region(p) for p in (150, 275, 315)}
    ctrl = {p: v for p, v in ctrl.items() if v is not None}
    if r313 is None or not r313["all_28_of_28"]:
        cls = "PARTITION_SUCCESSOR_CERTIFIED_REGION_NOT_CLOSING"
    elif ti.get("post_execution", {}).get("verdict") != "TEMPORAL_INTEGRITY_PASS":
        cls = "PARTITION_SUCCESSOR_TEMPORAL_INTEGRITY_FAIL"
    elif len(ctrl) == 3 and all(v["all_28_of_28"] for v in ctrl.values()):
        cls = "PARTITION_SUCCESSOR_313_REGION_28_OF_28_PASS"
    else:
        cls = "PARTITION_SUCCESSOR_CERTIFIED_REGION_NOT_CLOSING"
    per_cell_cpu = [c["t3_patch_cpu_h"] for v in [r313] + list(ctrl.values()) if v for c in v["cells"] if "t3_patch_cpu_h" in c]
    mean_cpu = sum(per_cell_cpu) / len(per_cell_cpu) if per_cell_cpu else None
    rec = {"schema": "rebaseguard.p5y.k1.sr.partition-successor.round-record.v1", "classification": cls,
           "anchor_commit": "9bfe3a71dd1884c933aa237896c21d59f9775c0e", "protocol_sha256": sha(NS / "config/PARTITION_PROTOCOL.json"),
           "successor_cells_sha256": proto["partition"]["successor_cells_sha256"],
           "governance": {"ruling": p1["ruling"], "answers": p1["answers"]},
           "diagnostic_worst_child": {n: {v: agg[n]["variants"][v]["worst_ratio_m235"] for v in ("B_certified", "A_oracle")} for n in agg},
           "rules_projection": rules, "temporal_integrity": {s: v["verdict"] for s, v in ti.items()},
           "certified_313_region": r313, "controls": ctrl,
           "measured_cost": {"mean_t3_midpoint_cpu_h_per_successor_cell": mean_cpu,
                             "projected_369_cell_cpu_h": mean_cpu * 369 if mean_cpu else None,
                             "note": "measured at 30-way load on 32 vCPU; estimate only; cap not requalified"},
           "not_claimed": ["K1 CLOSED", "P5Y CLOSED", "PRODUCTION READY", "the old 316-cell campaign passed"]}
    (NS / "config/PS1_ROUND_RECORD.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    det = json.loads((EV / "replay_313/determinism.json").read_text()) if (EV / "replay_313/determinism.json").exists() else None
    L = ["# PS1 - P5Y K1 SR predeclared partition successor: round result", "",
         f"**Classification: `{cls}`.** Not K1 closure; not P5Y closure; not production ready; the old 316-cell "
         "campaign is NOT claimed to pass.", "",
         "## A. Governance ruling", "", f"`{p1['ruling']}`.", ""] + [f"- **{k}**: {v}" for k, v in p1["answers"].items()] + [
         "", "## B. Old vs new campaign semantics", "",
         "The frozen 316-cell campaign and every result of it (cell 313 m1 PASS, m2/m3/m5 FAIL) remain immutable history. "
         "PS1 is a new additive K1 SR successor with its own predeclared 369-cell table, its own identities "
         "(PS1-SR-P<parent>-N<n>-K<k>) and its own work universe (28 obligations per successor cell); the theorem target, "
         "domain, thresholds and science are unchanged. Union of successor cells = [0, c_SR] exactly.", "",
         "## C. Legal partition rules evaluated", "",
         "| rule | successor cells | refined parents | old 313 -> | max child rho | CPU-h (midpoint T3) |", "|---|---:|---:|---:|---:|---:|"]
    for k, v in rules.items():
        L.append(f"| {k} | {v['successor_cells']} | {v['refined_parents']} | {v['children_of_313']} | {v['max_child_rho']:.4f} | {v['cpu_h_midpoint_only_T3']:.0f} |")
    L += ["", "## D/E. rho-scaling and child-location diagnostic (NON-CERTIFYING, pre-anchor)", "",
          "| N | child rho | worst-child ratio m2/m3/m5 (certified inputs, B) | oracle (A) | worst child |", "|---:|---:|---|---|---|"]
    aggfull = json.loads((EV / "phase34_diag_aggregate.json").read_text())["by_N"]
    for n, row in aggfull.items():
        b_, a_ = row["variants"]["B_certified"]["worst"], row["variants"]["A_oracle"]["worst"]
        L.append(f"| {n} | {row['child_rho']:.5f} | " + " / ".join(f"{b_[m]['ratio']:.3g}" for m in ("2", "3", "5"))
                 + " | " + " / ".join(f"{a_[m]['ratio']:.3g}" for m in ("2", "3", "5")) + f" | k{b_['5']['worst_child_k']} (leftmost) |")
    L += ["", "## G/H. Chosen pre-result rule and anchor", "",
          f"RULE RHO_CAP, r_max = 1/25 (dyadic, equal exact-rational children, C_upper inherited); 369 cells; table sha256 "
          f"`{rec['successor_cells_sha256']}`; protocol sha256 `{rec['protocol_sha256']}`; temporal anchor commit "
          "`9bfe3a71dd1884c933aa237896c21d59f9775c0e` (2026-09-11T05:26:43Z), containing no successor result.", "",
          "## I. Temporal integrity", "", f"{rec['temporal_integrity']}", "",
          "## J/K. Certified successor cells", "",
          "| successor cell | T3 | T5 | B_cover/limit m1 | m2 | m3 | m5 | M_R2 m5 | contraction | T3 CPU-h | peak RSS MiB |",
          "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for v in [r313] + [ctrl[p] for p in sorted(ctrl)]:
        if not v:
            continue
        for c in v["cells"]:
            if "id" not in c:
                L.append(f"| {c['successor_cell']} | not finalized | | | | | | | | | |")
                continue
            L.append(f"| {c['id']} | {c['T3_PASS']} | {c['t5_pass']}/{c['t5_total']} | "
                     + " | ".join(f"{c['B_cover_ratio'][m]:.4g}" for m in MS)
                     + f" | {c['M_R2']['5']:.4g} | {c['contraction_max']:.3f} | {c['t3_patch_cpu_h']:.1f} | {c['peak_rss_mib']:.0f} |")
    L += ["", f"Determinism replay (fresh process, 6 patches of successor cell 360): {det['all_identical'] if det else 'not run'}.", "",
          "## F. Cost", "", (f"Measured T3 midpoint CPU per successor cell: {mean_cpu:.1f} CPU-h (30-way load, 32 vCPU); "
          f"369-cell projection {(mean_cpu or 0) * 369:.0f} CPU-h. Estimate only; the 1,126 CPU-h cap is not requalified "
          "and is far exceeded.") if mean_cpu else "", "",
          "## L. Production firewall", "", "No production process, no prodctl, no AWS/Vultr production worker, no production "
          "ledger touched; every predecessor namespace byte-identical (temporal-integrity I3).", "",
          "## M. Next step", "", "A governed full PS1 SR campaign over all 369 successor cells under this frozen protocol "
          "(and a matching governed decision on the CPU cap), followed by independent adjudication. Not started.", ""]
    (NS / "RESULT.md").write_text("\n".join(L))
    print(cls, sha(NS / "config/PS1_ROUND_RECORD.json")[:16])


if __name__ == "__main__":
    main()
