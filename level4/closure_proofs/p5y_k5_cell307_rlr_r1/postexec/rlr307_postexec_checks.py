"""Cell-307 RLR campaign (r1) -- immediate post-execution checks (brief section 23). Read-only except that it runs the
driver's `execute` once more (which must REFUSE before anything, because the marker exists) and `seal-only` (which
must report "nothing computed"). It never evaluates anything.

    python3.14 -I -S -B rlr307_postexec_checks.py --out FILE
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(NS / "code"))
import rlr307_driver as D  # noqa: E402

ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0"}


def git(*a) -> str:
    return subprocess.run(["/usr/bin/git", "-C", str(REPO), *a], capture_output=True, text=True, env=ENV,
                          stdin=subprocess.DEVNULL).stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seal", required=True, help="the seal commit")
    ap.add_argument("--grant", required=True, help="the grant commit")
    a = ap.parse_args()
    c = {}
    pending = git("rev-parse", "-q", "--verify", D.PENDING_REF)
    marker = git("rev-parse", "-q", "--verify", D.CONSUMED_REF)
    entry = git("ls-tree", a.seal, "--", D.RESULT_REL).split()
    blob = entry[2] if len(entry) >= 3 else None
    raw = subprocess.run(["/usr/bin/git", "-C", str(REPO), "cat-file", "blob", blob or "0" * 40], capture_output=True,
                         env=ENV).stdout
    c["1_result_blob"] = {"blob": blob, "equals_pending_ref": blob == pending, "mode": entry[0] if entry else None,
                          "blob_id_recomputed": hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == blob}
    rec = json.loads(raw)
    body = {k: v for k, v in rec.items() if k != "sha256"}
    c["1_result_self_hash"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() == rec.get("sha256")
    c["2_seal_commit"] = {"seal": a.seal, "changes_only_result": git("diff-tree", "--no-commit-id", "--name-only", "-r",
                                                                     a.seal).split() == [D.RESULT_REL]}
    c["3_seal_parent_is_grant"] = git("rev-parse", f"{a.seal}^") == a.grant
    c["4_consumed_marker"] = {"marker": marker, "names_grant": marker == a.grant}
    all_refs = [r for r in git("for-each-ref", "--format=%(refname)").split() if r.startswith(D.PRIOR_MARKERS)]
    c["5_exactly_one_execution"] = {"refs": all_refs, "target_evaluations": rec.get("target_evaluations"),
                                    "status": rec.get("status"),
                                    "result_commits_in_history": git("log", "--all", "--format=%H", "--",
                                                                     D.RESULT_REL).split()}
    r2 = subprocess.run([sys.executable, "-I", "-S", "-B", str(NS / "code/rlr307_driver.py"), "execute"],
                        capture_output=True, text=True, env=ENV, cwd=str(REPO))
    c["6_second_execution_refused"] = {"exit": r2.returncode, "stdout": r2.stdout.strip()[-200:],
                                       "refused_before_anything": r2.returncode == 2 and "REFUSED" in r2.stdout}
    so = subprocess.run([sys.executable, "-I", "-S", "-B", str(NS / "code/rlr307_driver.py"), "seal-only"],
                        capture_output=True, text=True, env=ENV, cwd=str(REPO))
    c["7_seal_only_read_only"] = {"exit": so.returncode, "stdout": so.stdout.strip()[-200:],
                                  "nothing_computed": so.returncode == 0 and "nothing computed" in so.stdout,
                                  "head_unchanged": git("rev-parse", "HEAD") == a.seal}
    wt = (REPO / D.RESULT_REL)
    c["7b_worktree_copy_equals_sealed_bytes"] = wt.is_file() and not wt.is_symlink() and wt.read_bytes() == raw
    c["8_r5_unchanged_no_r6"] = {"r5_blob": git("rev-parse", f"{a.seal}:{D.PINS['coverage_r5'][0]}"),
                                 "r5_ok": git("rev-parse", f"{a.seal}:{D.PINS['coverage_r5'][0]}").startswith(
                                     D.PINS["coverage_r5"][2]),
                                 "r6_paths_any_ref": [p for p in git("log", "--all", "--format=", "--name-only").split()
                                                      if "COVERAGE_MAP_R6" in p]}
    outside = [p for p in git("diff", "--name-only", "7f45e048", a.seal).split() if not p.startswith(D.NS_REL + "/")]
    c["9_no_other_cell_evaluated"] = {"result_cell": rec.get("cell"), "changes_outside_namespace": outside,
                                      "other_marker_refs": [r for r in git("for-each-ref", "--format=%(refname)").split()
                                                            if "consumed" in r and not r.startswith(
                                                                ("refs/p5y-k5-cell307-rlr-r1/", "refs/c12r2/",
                                                                 "refs/c11rd/"))]}
    ok = (c["1_result_blob"]["equals_pending_ref"] and c["1_result_blob"]["blob_id_recomputed"]
          and c["1_result_self_hash"] and c["2_seal_commit"]["changes_only_result"] and c["3_seal_parent_is_grant"]
          and c["4_consumed_marker"]["names_grant"] and c["5_exactly_one_execution"]["target_evaluations"] == 1
          and len(c["5_exactly_one_execution"]["result_commits_in_history"]) == 1
          and c["6_second_execution_refused"]["refused_before_anything"] and c["7_seal_only_read_only"]["nothing_computed"]
          and c["7_seal_only_read_only"]["head_unchanged"] and c["7b_worktree_copy_equals_sealed_bytes"]
          and c["8_r5_unchanged_no_r6"]["r5_ok"] and not c["8_r5_unchanged_no_r6"]["r6_paths_any_ref"]
          and c["9_no_other_cell_evaluated"]["result_cell"] == 307
          and not c["9_no_other_cell_evaluated"]["changes_outside_namespace"])
    out = {"schema": "rebaseguard.p5y.k5.cell307-rlr-r1.postexec.v1", "checks": c, "pass": bool(ok),
           "note": "status and structure only; this file quotes no target value"}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"POSTEXEC {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
