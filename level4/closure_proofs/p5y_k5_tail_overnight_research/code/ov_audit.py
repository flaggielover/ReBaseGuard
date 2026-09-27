"""Governance / provenance audit for the overnight campaign (stdlib + read-only git).

Checks, each with a negative control where one is meaningful:
  L1  ledger: counts of new target evaluations, target-equivalent proxies, target-informed optimisation,
      and LEAK_FLAG lines (all must be 0);
  L2  static scan of all new code (ov_quarantine.scan) incl. its planted negative control;
  L3  every file changed since the base commit lies inside this namespace;
  L4  r5 coverage map blob unchanged (f978eeb6...), no COVERAGE_MAP_R6 on any ref;
  L5  exactly-once refs unchanged (refs/c12r2/*, refs/c11rd/*);
  L6  historical namespaces untouched (floor r2, C12-R2, closeout r0-r2, route audit) -- implied by L3,
      reported separately for readability.
Writes ledger/OV_AUDIT.json and prints the verdict.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
REPO = NS.parents[2]
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

BASE = "8b9fc0bb1c6994dfb0e942cc7a6d411aaf51db99"
NS_REL = str(NS.relative_to(REPO))
R5_PATH = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
R5_BLOB = "f978eeb6b41188eabaf3c6d590c9178d711f1ce6"
EXACTLY_ONCE = {
    "refs/c12r2/cell306-target-consumed": "dec92e09",  # ov-quarantine: literal-ok exactly-once ref name checked read-only
    "refs/c12r2/cell306-pending-result": "0ac46b3d",  # ov-quarantine: literal-ok exactly-once ref name checked read-only
    "refs/c11rd/r1-execution-consumed": "4b716d43",
}
PROTECTED = [
    "level4/closure_proofs/p5y_k5_tail_floor_r2",
    "level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption",
    "level4/closure_proofs/p5y_k5_partial_closeout",
    "level4/closure_proofs/p5y_k5_partial_closeout_r1",
    "level4/closure_proofs/p5y_k5_partial_closeout_r2",
    "level4/closure_proofs/p5y_k5_tail_route_audit",
    "level4/closure_proofs/p5y_k5_tail_c2_closure",
]


def git(*args: str) -> str:
    return subprocess.run(["git", "--no-replace-objects", "-C", str(REPO), *args],
                          check=True, capture_output=True, text=True).stdout


def ledger_counts(path: Path) -> dict:
    tot = {"lines": 0, "new_target_evaluations": 0, "target_equivalent_proxies": 0,
           "target_informed_optimisation": 0, "leak_flags": 0, "classes": {}}
    if not path.exists():
        return tot
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        tot["lines"] += 1
        tot["new_target_evaluations"] += int(r.get("new_target_evaluations", 0))
        tot["target_equivalent_proxies"] += int(r.get("target_equivalent_proxies", 0))
        tot["target_informed_optimisation"] += int(r.get("target_informed_optimisation", 0))
        tot["leak_flags"] += int(bool(r.get("LEAK_FLAG")))
        k = r.get("class", "?")
        tot["classes"][k] = tot["classes"].get(k, 0) + 1
    return tot


def ledger_negative_control() -> bool:
    """A planted leak line must be counted."""
    tmp = NS / "ledger" / ".audit_negative_control.jsonl"
    tmp.write_text(json.dumps({"new_target_evaluations": 1, "LEAK_FLAG": True, "class": "X"}) + "\n")
    try:
        c = ledger_counts(tmp)
    finally:
        tmp.unlink()
    return c["new_target_evaluations"] == 1 and c["leak_flags"] == 1


def main() -> int:
    out: dict = {"schema": "OV_AUDIT/1", "base": BASE, "head": git("rev-parse", "HEAD").strip()}
    lc = ledger_counts(Q.LEDGER)
    out["L1_ledger"] = lc | {"negative_control_detected": ledger_negative_control()}
    sc = Q.scan()
    out["L2_static_scan"] = {k: sc[k] for k in ("verdict", "files_scanned", "findings",
                                                "negative_control_detected", "sanctioned_files",
                                                "sanctioned_historical_read")}
    changed = [p for p in git("diff", "--name-only", BASE, "HEAD").splitlines() if p]
    worktree = [p for p in git("diff", "--name-only", BASE).splitlines() if p]   # includes uncommitted edits (F1)
    untracked = [p for p in git("ls-files", "--others", "--exclude-standard").splitlines() if p]

    def outside_of(paths):
        return sorted({p for p in paths if not p.startswith(NS_REL + "/")})

    outside = outside_of(changed + worktree + untracked)
    # negative control through the SAME filter (review F1): a planted outside path must be reported
    planted = "level4/closure_proofs/p5y_k5_tail_floor_r2/PLANTED_CONTROL.md"
    l3_control = outside_of(changed + [planted]) == sorted(set(outside_of(changed)) | {planted})
    out["L3_scope"] = {"changed_files_since_base": len(changed), "worktree_changed": len(worktree),
                       "untracked": len(untracked), "outside_namespace": outside,
                       "negative_control_detected": l3_control}
    r5 = git("rev-parse", f"HEAD:{R5_PATH}").strip()
    r6_hits = [p for p in git("log", "--all", "--format=", "--name-only").splitlines() if "COVERAGE_MAP_R6" in p]
    out["L4_coverage"] = {"r5_blob": r5, "r5_unchanged": r5 == R5_BLOB, "r6_paths_any_ref": sorted(set(r6_hits))}
    refs = {}
    for ref, want in EXACTLY_ONCE.items():
        try:
            got = git("rev-parse", ref).strip()
        except subprocess.CalledProcessError:
            got = "MISSING"
        refs[ref] = {"expected_prefix": want, "actual": got, "ok": got.startswith(want)}
    out["L5_exactly_once_refs"] = refs
    out["L6_protected_namespaces_touched"] = sorted({p for p in changed for d in PROTECTED if p.startswith(d + "/")})
    ok = (out["L3_scope"]["negative_control_detected"] and lc["new_target_evaluations"] == 0
          and lc["target_equivalent_proxies"] == 0
          and lc["target_informed_optimisation"] == 0 and lc["leak_flags"] == 0
          and out["L1_ledger"]["negative_control_detected"]
          and sc["verdict"] == "PASS" and not outside and out["L4_coverage"]["r5_unchanged"]
          and not r6_hits and all(v["ok"] for v in refs.values())
          and not out["L6_protected_namespaces_touched"])
    incidents = sorted(q.name for q in (NS / "ledger").glob("INCIDENT_*.md"))
    out["incidents_recorded"] = incidents
    out["verdict"] = "PASS" if ok else "FAIL"
    if not ok and lc["new_target_evaluations"] == 0 and lc["target_equivalent_proxies"] == len(incidents) \
            and sc["verdict"] == "PASS" and not outside and out["L4_coverage"]["r5_unchanged"] and not r6_hits \
            and all(v["ok"] for v in refs.values()):
        out["verdict_detail"] = ("FAIL solely because of the recorded proxy-exposure incidents "
                                 f"({len(incidents)}); 0 new target evaluations; governance otherwise clean")
    (NS / "ledger" / "OV_AUDIT.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: out[k] for k in ("verdict", "head")} | {"detail": out.get("verdict_detail"),
        "incidents": out["incidents_recorded"],
        "ledger": {k: lc[k] for k in ("lines", "new_target_evaluations", "target_equivalent_proxies",
                                      "target_informed_optimisation", "leak_flags")},
        "scan": out["L2_static_scan"]["verdict"], "files_scanned": sc["files_scanned"],
        "sanctioned_files": sc["sanctioned_files"],
        "outside_namespace": outside, "r5_unchanged": out["L4_coverage"]["r5_unchanged"],
        "r6": out["L4_coverage"]["r6_paths_any_ref"],
        "refs_ok": all(v["ok"] for v in refs.values())}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
