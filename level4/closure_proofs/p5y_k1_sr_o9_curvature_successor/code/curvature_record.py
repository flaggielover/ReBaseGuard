"""Consolidate the curvature-certification successor evidence into config/CURVATURE_SUCCESSOR_RECORD.json."""
import glob
import hashlib
import json
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
REPO = CP.parents[1]
EV = NS / "evidence"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()          # noqa: E731
jl = lambda p: json.loads(Path(p).read_text())                             # noqa: E731


def git(*a, repo=REPO):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True)


def main():
    doc, dec, kill = jl(EV / "phase1_doctrine.json"), jl(EV / "phase2_decomposition.json"), jl(EV / "kill_table.json")
    det, kz2 = jl(EV / "determinism_kill.json"), jl(EV / "kz2_predecessor_check.json")
    pre = NS / "config/SUCCESSOR_PREDECLARATION.json"
    crit = kill["critical"]
    kill_pass = all(v <= 1 for v in crit.values()) and all(r["ratio_new"] <= 1 for r in kill["rows"])
    control = [r for r in kill["rows"] if r["cell"] == 150]
    runs = {c: jl(EV / f"kill/run_c{c}.log") for c in (275, 313, 315, 150)}
    preds = sorted(Path(p).name for p in glob.glob(str(CP / "p5y_k1_sr_o9_*")) if Path(p).name != NS.name)
    unchanged = {d: git("diff", "--quiet", "8b8a242", "--", f"level4/closure_proofs/{d}").returncode == 0
                 and not git("status", "--porcelain", "--", f"level4/closure_proofs/{d}").stdout.strip() for d in preds}
    for d in ("p5y_k1_cover_ledger_implementation", "p5y_k1_cover_ledger_successor", "p5y_k1_sr_qualification", "p5y_k1_cusum_aux3_successor"):
        unchanged[d] = git("diff", "--quiet", "8b8a242", "--", f"level4/closure_proofs/{d}").returncode == 0
    wt = {w: {"head": git("rev-parse", "--short", "HEAD", repo=REPO.parent / w).stdout.strip(),
              "dirty": bool(git("status", "--porcelain", repo=REPO.parent / w).stdout.strip())}
          for w in ("ReBaseGuard-sr-parallel", "ReBaseGuard-sr-lifecycle")}
    active = subprocess.run(["systemctl", "list-units", "--state=active", "--no-pager", "--plain"], capture_output=True, text=True).stdout
    entry = {"prodctl.py", "supervisor.py", "integrated_sr_launcher.py", "production_launcher.py"}
    ps = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True).stdout.splitlines()
    procs = [l for l in ps if (lambda a: len(a) > 2 and a[1].split("/")[-1].startswith("python")
                               and any(t.split("/")[-1] in entry for t in a[2:4]))(l.split())]
    fw = {"worktrees": wt, "active_rbg_units": [l for l in active.splitlines() if "rbg-" in l], "production_processes": procs,
          "prodctl_run": False, "production_ledger_touched": False, "aws_or_vultr_production_started": False}
    fw["PASS"] = (wt["ReBaseGuard-sr-parallel"] == {"head": "bd7cf26", "dirty": False}
                  and wt["ReBaseGuard-sr-lifecycle"] == {"head": "bcec064", "dirty": False}
                  and not fw["active_rbg_units"] and not procs)
    cls = ("CURVATURE_LOCALIZATION_FROZEN_BLOCKED" if doc["ruling"] != "CURVATURE_LOCALIZATION_DOCTRINE_PERMITS_SUCCESSOR"
           else "CURVATURE_SUCCESSOR_REPRESENTATIVE_SET_PASS" if kill_pass
           else "CURVATURE_SUCCESSOR_NUMERICALLY_NOT_CLOSING")
    rec = {
        "schema": "rebaseguard.p5y.k1.sr.o9.curvature-successor-record.v1",
        "status_label": "CURVATURE_CERTIFICATION_SUCCESSOR only (not K1 closure, not P5Y closure, not production readiness)",
        "classification": cls, "parent": {"commit": "8b8a242", "tag": "p5y-k1-sr-o9-t5-one-cell-28-of-28"},
        "phase1_doctrine": {"ruling": doc["ruling"], "answers": doc["answers"], "scope": doc["ruling_scope"],
                            "artifacts_bound": len(doc["bound_artifacts"])},
        "predeclaration": {"file": "config/SUCCESSOR_PREDECLARATION.json", "sha256": sha(pre),
                           "declared_utc": jl(pre)["declared_utc"], "subdivision_rule": jl(pre)["subdivision_rule"]},
        "phase2_phase3": {c: {m: {k: v[k] for k in ("B_cover_ratio", "IDEALIZED_B_cover_ratio_DIAGNOSTIC", "inflation_MR2_over_nominal",
                                                    "nominal_Rsecond_e0", "M_R2", "target_gate_current",
                                                    "target_gate_with_zero_curvature_error_DIAGNOSTIC")}
                              for m, v in d["m"].items()} for c, d in dec.items()},
        "phase2_answer": "B: certified curvature grossly inflated relative to nominal (idealized cover passes in every cell; "
                         "cell 313's target-gate failure does not survive a zero-error curvature term)",
        "kill_micropilot": {"rows": kill["rows"], "critical": crit, "all_pass": kill_pass,
                            "cell313_remaining_H_closure": kill["cell313_H_closure_after_successor"]},
        "control_150": {"all_pass": all(r["ledger_new"] == "PASS" for r in control),
                        "tighter_or_equal": all(r["ratio_new"] <= r["ratio_old"] for r in control), "T5": runs[150]["T5"]},
        "phase7_six_cell_validation": "NOT REACHED: the predeclared condition (every kill case passes) failed at 313 m = 2, 3, 5",
        "determinism": {"pairs": len(det["rows"]), "all_bytes_equal": all(r["bytes_equal"] for r in det["rows"]),
                        "zero_scientific_leaves_moved": det["ZERO_SCIENTIFIC_LEAVES_MOVED"]},
        "predecessor_kz2_check": {"all_valid": kz2["all_valid"],
                                  "note": "frozen sr_operators kz2 cites a pointwise-false inequality; the values used by 8b8a242 are "
                                          "nevertheless valid upper bounds on all six cells (slack 1.07-1.58x); committed T4/T5 stand"},
        "cost": {"curvature_layer_cpu_s_per_cell": {str(c): r["cpu_s"] for c, r in runs.items()},
                 "peak_rss_kib": max(r["rss_kib"] for r in runs.values()),
                 "T2_T3_evidence_reuse": "100% (T3 midpoint-mode deltas and x0 values; no patch recomputation)",
                 "projection_note": "the curvature layer is about 1 CPU-s per cell. The mean-value construction removes "
                                    "the need for the T3 interval-e mode; the T3 midpoint mode alone is ~18 CPU-s per patch "
                                    "at 30-way load (T2 closure runs), i.e. ~20 CPU-h per cell, ~6,300 CPU-h for 316 cells. "
                                    "Estimate only; no cap qualification."},
        "predecessors_unchanged_vs_8b8a242": unchanged, "production_firewall": fw,
        "next_options_not_taken": ["drift-aware sharper operator norms (final_completion sharp_norms precedent)",
                                   "predeclared dyadic max-over-subinterval ladder for the residual enclosure (parent rho)",
                                   "Aux3-style nested third-derivative evidence (needs auxiliary candidates: governance required)"],
        "sources_sha256": {p.name: sha(p) for p in sorted((NS / "code").glob("*.py"))},
        "evidence_sha256": {str(Path(f).relative_to(NS)): sha(f) for f in sorted(glob.glob(str(EV / "**/*"), recursive=True)) if Path(f).is_file()},
    }
    (NS / "config/CURVATURE_SUCCESSOR_RECORD.json").write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"classification": cls, "sha256": sha(NS / "config/CURVATURE_SUCCESSOR_RECORD.json"), "kill_all_pass": kill_pass,
                      "control": rec["control_150"], "determinism": rec["determinism"], "firewall": fw["PASS"],
                      "predecessors_unchanged": all(unchanged.values())}, indent=1, default=str))


if __name__ == "__main__":
    main()
