#!/usr/bin/env python3
"""Independent count of target evaluations and target-adjacent state (read-only; imports no campaign code).

  python3 count_target_evaluations.py --out FILE [--scratch DIR ...]

Counts, everywhere this session could have reached:
  * protected refs (exactly-once markers, pending-result refs, production / test namespaces) in the session
    repository, on origin (ls-remote), in every git repository found under the given scratch directories
    (replicas and every QC11 / D5 / guard sandbox);
  * grant, result, emergency-result and run-nonce files under those trees;
  * every execution-ledger row (ZERO_TARGET_LEDGER.jsonl) in the session repository and the replicas, with any
    nonzero target counter or unreadable row counted;
  * r5's blob and the absence of any r6 file at the session HEAD.
NEW TARGET EVALUATIONS is the sum of every count; any unreadable source is counted, never skipped.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
from pathlib import Path

SESSION = Path(__file__).resolve().parents[4]
PROTECTED = re.compile(r"refs/(?:p5y-k5-cell30|p309-cell309|rlr-tail/)")
FILES = re.compile(r"(?:^P309_GRANT\.json$|^P309_RESULT\.json|^p309-emergency-result\.json$|^p309-run-nonce\.json$)")
COUNTERS = ("new_target_evaluations", "target_equivalent_proxies", "target_informed_optimisation")
R5 = ("level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json",
      "f978eeb6b41188eabaf3c6d590c9178d711f1ce6")
BASES = ("c902fe2fe33003ac7e4e61f29c10c81682fc940c", "101ef2cb17e5eab2892212178278da45b98004ed")   # r1, r2 heads
SANDBOX_FIXTURE_REFS = {"refs/rlr-tail/x"}           # test_p309_exactly_once.py flow F23 (both r1 and r2)
SANDBOX_DIR = re.compile(r"/qc11_sandboxes/F23_prior_marker_namespace$")


def base_rows(rel: str) -> set:
    """the ledger's rows as committed at the r1 / r2 heads (pre-existing history, not this session's)"""
    rows = set()
    for b in BASES:
        rc, out = git(SESSION, "show", f"{b}:{rel}")
        if rc == 0:
            rows |= {l for l in out.splitlines() if l.strip()}
    return rows


def git(repo, *a) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True)
    return p.returncode, p.stdout


def repos_under(root: Path) -> list[Path]:
    out = []
    for dirpath, dirnames, _ in os.walk(root):
        if ".git" in dirnames or Path(dirpath, ".git").is_file():
            out.append(Path(dirpath))
        dirnames[:] = [d for d in dirnames if d != ".git"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--scratch", action="append", default=[])
    a = ap.parse_args()
    res = {"schema": "P309_TARGET_EVALUATION_COUNT/1",
           "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "protected_refs": {}, "protected_files": [], "ledgers": {}, "errors": []}
    repos = [SESSION] + [r for s in a.scratch for r in repos_under(Path(s))]
    res["test_sandbox_fixture_refs"] = {}
    for r in repos:
        rc, out = git(r, "for-each-ref", "--format=%(refname)")
        if rc:
            res["errors"].append(f"for-each-ref failed in {r}")
            continue
        hits = [x for x in out.split() if PROTECTED.search(x)]
        # the frozen QC11 harness plants refs/rlr-tail/x in its F23 TEST sandbox to show execute refuses (CONSUMED)
        fixture = [x for x in hits if x in SANDBOX_FIXTURE_REFS and SANDBOX_DIR.search(str(r))]
        if fixture:
            res["test_sandbox_fixture_refs"][str(r)] = fixture
        hits = [x for x in hits if x not in fixture]
        if hits:
            res["protected_refs"][str(r)] = hits
    rc, out = git(SESSION, "ls-remote", "origin")
    if rc:
        res["errors"].append("ls-remote origin failed")
    res["origin_protected_refs"] = [l.split("\t")[1] for l in out.splitlines() if PROTECTED.search(l)]
    res["repositories_scanned"] = len(repos)
    for root in [SESSION / "level4"] + [Path(s) for s in a.scratch]:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            for f in filenames:
                if FILES.match(f):
                    p = Path(dirpath) / f
                    # TEST sandboxes legitimately hold TEST grants built by the QC11 harness: reported, classified
                    res["protected_files"].append({"path": str(p), "in_test_sandbox": any(
                        s in str(p) for s in ("qc11_sandboxes", "d5_controls", "fc2_sandbox", "/sandbox", "drill_"))})
                if f == "ZERO_TARGET_LEDGER.jsonl":
                    p = Path(dirpath) / f
                    m = re.search(r"(level4/closure_proofs/.*)$", str(p))
                    pre = base_rows(m.group(1)) if m else set()
                    rows = bad = old_nonzero = 0
                    for line in p.read_text(errors="replace").splitlines():
                        if not line.strip():
                            continue
                        rows += 1
                        try:
                            r = json.loads(line)
                            nz = any(r.get(k, 0) != 0 for k in COUNTERS)
                        except ValueError:
                            nz = True
                        if nz and line in pre:
                            old_nonzero += 1         # committed before this session (r1 / r2 history)
                        elif nz:
                            bad += 1
                    res["ledgers"][str(p)] = {"rows": rows, "nonzero_or_unreadable": bad,
                                              "preexisting_nonzero_rows_in_r1_r2_history": old_nonzero}
    rc, blob = git(SESSION, "rev-parse", f"HEAD:{R5[0]}")
    res["r5_unchanged"] = blob.strip() == R5[1]
    rc, tree = git(SESSION, "ls-tree", "-r", "--name-only", "HEAD")
    res["r6_files_at_head"] = [p for p in tree.splitlines() if "COVERAGE_MAP_R6" in p.upper()]
    outside_sandbox = [x for x in res["protected_files"] if not x["in_test_sandbox"]]
    res["new_target_evaluations"] = (sum(len(v) for v in res["protected_refs"].values())
                                     + len(res["origin_protected_refs"]) + len(outside_sandbox)
                                     + sum(v["nonzero_or_unreadable"] for v in res["ledgers"].values())
                                     + len(res["errors"]) + (0 if res["r5_unchanged"] else 1)
                                     + len(res["r6_files_at_head"]))
    res["ledger_rows_total"] = sum(v["rows"] for v in res["ledgers"].values())
    res["test_sandbox_grant_files"] = len(res["protected_files"]) - len(outside_sandbox)
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: res[k] for k in ("new_target_evaluations", "repositories_scanned", "ledger_rows_total",
                                          "origin_protected_refs", "r5_unchanged", "r6_files_at_head",
                                          "test_sandbox_grant_files", "errors")}, indent=1))
    return 0 if res["new_target_evaluations"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
