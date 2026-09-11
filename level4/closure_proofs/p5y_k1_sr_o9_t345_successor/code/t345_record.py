"""Consolidate T3/T4/T5 evidence into config/T345_RECORD.json and classify the round (evidence only)."""
import glob
import gzip
import hashlib
import json
import subprocess
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
REPO = CP.parents[1]
EV = NS / "evidence"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()          # noqa: E731
jl = lambda p: json.loads(Path(p).read_text())                             # noqa: E731


def git(*a, repo=REPO):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True).stdout.strip()


def cost(cell):
    cpu, rss, n = 0.0, 0, 0
    for f in sorted(glob.glob(str(EV / f"patch_records/*/*.jsonl.gz"))):
        for line in gzip.open(f, "rt"):
            r = json.loads(line)
            if r["cell"] == cell:
                cpu += r["cpu_seconds"]; rss = max(rss, r["peak_rss_kib"]); n += 1
    return {"patch_records": n, "cpu_seconds": cpu, "cpu_hours": cpu / 3600, "mean_cpu_s_per_patch_both_modes": cpu / max(n, 1),
            "peak_rss_kib_per_worker": rss}


def main():
    t3 = {int(Path(f).stem.split("_c")[1]): jl(f) for f in sorted(glob.glob(str(EV / "t3/t3_c*.json")))}
    t4 = {int(Path(f).stem.split("_c")[1]): jl(f) for f in sorted(glob.glob(str(EV / "t4/t4_c*.json")))}
    t5 = {int(Path(f).stem.split("_c")[1]): jl(f) for f in sorted(glob.glob(str(EV / "t5/t5_c*.json")))}
    rep = {Path(f).name: jl(f) for f in sorted(glob.glob(str(EV / "replay/*.json")))}
    cells = {}
    for c in sorted(set(t3) | set(t4)):
        row = {"T3_PASS": t3[c]["T3_PASS"] if c in t3 else None, "T3_checks": t3[c]["checks"] if c in t3 else None}
        if c in t4:
            L = t4[c]["m"]
            row.update({"all_m_status": t4[c]["all_m_status"], "B_cover_ratio": t4[c]["B_cover_ratio"],
                        "M_R2": {m: float(Fr(v["M_R2"])) for m, v in L.items()},
                        "D_interval_mag": {m: float(Fr(v["D_interval_mag"])) for m, v in L.items()},
                        "R_interval": {m: [float(Fr(v["R_interval"]["lo"])), float(Fr(v["R_interval"]["hi"]))] for m, v in L.items()},
                        "unrefined_W_cover": {m: float(Fr(v["W_cover_unrefined_upper"])) for m, v in L.items()},
                        "failing_gates": {m: sorted(k for k, g in v["top_level_gates"].items() if g.get("status") == "FAIL") for m, v in L.items()},
                        "rho_upper": float(Fr(t4[c]["rho_upper"])), "C_upper": float(Fr(t4[c]["C_upper"])),
                        "refinement_iterations": {r: v["summary"]["iterations"] for r, v in t4[c]["refinement"].items()}})
        if c in t5:
            row.update({"T5_status": t5[c]["status"], "T5_pass_count": t5[c]["pass_count"]})
        row["cost"] = cost(c)
        cells[str(c)] = row
    target = 150
    ok3 = target in t3 and t3[target]["T3_PASS"]
    ok4 = target in t4 and all(v == "PASS" for v in t4[target]["all_m_status"].values())
    ok5 = target in t5 and t5[target]["status"] == "T5_28_OF_28_PASS"
    det = all(r["ZERO_SCIENTIFIC_LEAVES_MOVED"] for r in rep.values()) and bool(rep)
    if not ok3:
        cls = "T3_WHOLE_CELL_AGGREGATION_FAIL"
    elif not ok4:
        cls = "T4_BCOVER_NUMERICALLY_NOT_CLOSING"
    elif not ok5 or not det:
        cls = "T5_OBLIGATION_NOT_CLOSING"
    else:
        cls = "T5_ONE_REAL_SR_CELL_28_OF_28_PASS"
    prod = {w: {"head": git("rev-parse", "--short", "HEAD", repo=REPO.parent / w),
                "dirty": bool(git("status", "--porcelain", repo=REPO.parent / w))}
            for w in ("ReBaseGuard-sr-parallel", "ReBaseGuard-sr-lifecycle")}
    active = subprocess.run(["systemctl", "list-units", "--state=active", "--no-pager", "--plain"], capture_output=True, text=True).stdout
    # Real production processes only: a python process whose script argument is one of the production entry points.
    # (A substring search also matched this tool's own shells, whose command text merely mentions those words.)
    entry = {"prodctl.py", "supervisor.py", "integrated_sr_launcher.py", "production_launcher.py"}
    ps = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True).stdout.splitlines()
    procs = "\n".join(l for l in ps if (lambda a: len(a) > 2 and a[1].split("/")[-1].startswith("python")
                                         and any(t.split("/")[-1] in entry for t in a[2:4]))(l.split()))
    unit = subprocess.run(["systemctl", "show", "rbg-p5y-k1-sr-prod-aws-20260910T105333Z-640db8f2.service", "-p", "ActiveState",
                           "-p", "StateChangeTimestamp"], capture_output=True, text=True).stdout.split()
    firewall = {"worktrees": prod, "active_rbg_units": [l for l in active.splitlines() if "rbg-" in l],
                "production_processes": [l for l in procs.splitlines() if l.strip()], "historical_unit": unit,
                "prodctl_started": False, "production_ledger_touched": False, "retries_consumed": 0,
                "aws_or_vultr_workers_started": False}
    firewall["PASS"] = (prod["ReBaseGuard-sr-parallel"] == {"head": "bd7cf26", "dirty": False}
                        and prod["ReBaseGuard-sr-lifecycle"] == {"head": "bcec064", "dirty": False}
                        and not firewall["active_rbg_units"] and not firewall["production_processes"])
    pred = {d: git("diff", "--quiet", "1bd7a3f", "--", f"level4/closure_proofs/{d}") == "" and
            subprocess.run(["git", "-C", str(REPO), "diff", "--quiet", "1bd7a3f", "--", f"level4/closure_proofs/{d}"]).returncode == 0
            for d in sorted(Path(p).name for p in glob.glob(str(CP / "p5y_k1_sr_o9_*")) if Path(p).name != NS.name)}
    rec = {"schema": "rebaseguard.p5y.k1.sr.o9.t345-record.v1", "parent": {"commit": "1bd7a3f", "tag": "p5y-k1-sr-o9-t2-per-patch-closed"},
           "classification": cls,
           "status": ("T5_ONE_REAL_SR_CELL_28_OF_28_PASS" if cls == "T5_ONE_REAL_SR_CELL_28_OF_28_PASS" else cls),
           "target_cell": target, "cells": cells, "determinism": {k: {x: v[x] for x in ("mode", "total_moved_scientific",
                                                                                     "total_moved_incidental", "ZERO_SCIENTIFIC_LEAVES_MOVED")}
                                                                  for k, v in rep.items()},
           "production_firewall": firewall, "predecessor_namespaces_unchanged_vs_1bd7a3f": pred,
           "not_claimed": ["K1 closure", "production authorization or readiness", "the 316-cell campaign",
                           "any cell other than those listed", "far-field (inherited, not recomputed)"],
           "sources_sha256": {p.name: sha(p) for p in sorted((NS / "code").glob("*.py"))},
           "evidence_sha256": {str(Path(f).relative_to(NS)): sha(f) for f in sorted(glob.glob(str(EV / "**/*.json"), recursive=True))
                               + sorted(glob.glob(str(EV / "patch_records/*/*.gz")))}}
    out = NS / "config/T345_RECORD.json"
    out.write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"classification": cls, "sha256": sha(out), "firewall": firewall["PASS"], "predecessors_unchanged": all(pred.values()),
                      "cells": {c: {k: v for k, v in r.items() if k in ("T3_PASS", "all_m_status", "B_cover_ratio", "T5_status", "T5_pass_count")}
                                for c, r in cells.items()}}, indent=1, default=str))


if __name__ == "__main__":
    main()
