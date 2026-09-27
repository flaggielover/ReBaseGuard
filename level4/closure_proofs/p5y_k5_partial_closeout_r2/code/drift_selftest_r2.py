"""Drift-algorithm self-test for the K5 PARTIAL closeout R2 (administrative; no science).

Builds a THROWAWAY `git clone --shared --no-checkout` of this repository in a temporary directory OUTSIDE the
repository, copies the R2 namespace into it, takes an R2 ref snapshot there, then injects one drift scenario at a time
into the CLONE's refs (new commits are built with plumbing on a private index), runs `closeout_checks_r2.py --diff`
in the clone, records the verdict, and restores the clone's refs. The real repository's refs are never written; the
clone is deleted at the end. Content written into scenario commits is synthetic status text, not scientific data.

Usage: python3 -I -S -B drift_selftest_r2.py --workdir DIR --out FILE
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
REPO = NS.parents[2]
NS_REL = "level4/closure_proofs/p5y_k5_partial_closeout_r2"
ENV = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": "/var/empty", "LC_ALL": "C",
       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
       "GIT_AUTHOR_NAME": "selftest", "GIT_AUTHOR_EMAIL": "selftest@invalid", "GIT_AUTHOR_DATE": "2026-09-28T00:00:00+0900",
       "GIT_COMMITTER_NAME": "selftest", "GIT_COMMITTER_EMAIL": "selftest@invalid",
       "GIT_COMMITTER_DATE": "2026-09-28T00:00:00+0900"}

K1_PATH = "level4/closure_proofs/p5y_k1_successor_final_adjudication/evidence/FINAL_ADJUDICATION.json"
K4_PATH = "level4/closure_proofs/p5y_k4r1_final_adjudication/K4R1_FINAL_VERDICT.json"
FLAGFILE = "level4/closure_proofs/p5y_k5b_independent_countersignature/README.md"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        print("refused: run with python3 -I -S -B", file=sys.stderr)
        return 2
    work = pathlib.Path(a.workdir).resolve()
    if str(work).startswith(str(REPO)) or str(REPO).startswith(str(work)):
        print("refused: workdir must be outside the repository", file=sys.stderr)
        return 2
    clone = work / "clone"
    if clone.exists():
        shutil.rmtree(clone)
    work.mkdir(parents=True, exist_ok=True)

    def g(*args, cwd=clone, env_extra=None, stdin_text=None, check=True):
        env = dict(ENV, **(env_extra or {}))
        r = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, input=stdin_text,
                           stdin=None if stdin_text is not None else subprocess.DEVNULL, timeout=3600)
        if check and r.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)[:120]}: {r.stderr[:300]}")
        return r.stdout.strip()

    g("clone", "--quiet", "--shared", "--no-checkout", str(REPO), str(clone), cwd=work)
    real_common = pathlib.Path(g("rev-parse", "--git-common-dir", cwd=REPO)).resolve()
    clone_common = (clone / g("rev-parse", "--git-common-dir")).resolve()
    assert clone_common != real_common and str(clone_common).startswith(str(work)), "clone isolation failed"
    shutil.copytree(NS, clone / NS_REL, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    checker = clone / NS_REL / "code" / "closeout_checks_r2.py"

    def run_checker(*args):
        r = subprocess.run([sys.executable, "-I", "-S", "-B", str(checker), *args], cwd=clone,
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=3600)
        return r.returncode, r.stdout[-400:], r.stderr[-400:]

    snap = work / "snapshot.json"
    rc, so, se = run_checker("--snapshot", "--out", str(snap))
    base_snap = json.loads(snap.read_text())

    def ref_of_record(path):
        for kind, v in base_snap["reconstruction"]["versions"].items():
            if v["path"] == path and v["current"]:
                tips = [t for x in v["versions"] if x["blob"] == v["current"] for t in x["live_tips"]]
                refs = [r["ref"] for r in base_snap["refs"] if r["peeled"] in tips]      # branches AND (annotated) tags
                return tips[0], refs
        return None, []

    def commit_with(parent, changes, msg):
        idx = work / "index.tmp"
        if idx.exists():
            idx.unlink()
        e = {"GIT_INDEX_FILE": str(idx)}
        g("read-tree", parent, env_extra=e)
        for path, content in changes.items():
            blob = g("hash-object", "-w", "--stdin", stdin_text=content)
            g("update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env_extra=e)
        tree = g("write-tree", env_extra=e)
        return g("commit-tree", tree, "-p", parent, "-m", msg), tree

    def show(obj, path):
        return g("show", f"{obj}:{path}")

    all_refs = {l.split(" ", 1)[1]: l.split(" ", 1)[0] for l in g("for-each-ref", "--format=%(objectname) %(refname)").splitlines()}

    def restore():
        now = {l.split(" ", 1)[1]: l.split(" ", 1)[0] for l in g("for-each-ref", "--format=%(objectname) %(refname)").splitlines()}
        for r in set(now) - set(all_refs):
            g("update-ref", "-d", r)
        for r, o in all_refs.items():
            if now.get(r) != o:
                g("update-ref", r, o)

    k1_tip, k1_refs = ref_of_record(K1_PATH)
    k4_tip, k4_refs = ref_of_record(K4_PATH)
    results = []

    def scenario(name, expect_verdicts, apply):
        apply()
        out = work / f"diff_{name}.json"
        rc, so, se = run_checker("--diff", str(snap), "--diff-phase", "adjudication", "--out", str(out))
        d = json.loads(out.read_text())
        restore()
        got = d["verdict"]
        classes = sorted({s[0] for s in d["stops"]})
        ok = (got == "CONTINUE") if expect_verdicts == ["CONTINUE"] else \
            (got != "CONTINUE" and bool(set(expect_verdicts) & set(classes)))
        results.append({"scenario": name, "expected": expect_verdicts, "verdict": got, "stop_classes": classes,
                        "ref_changes": [(c["ref"], c["change"]) for c in d.get("ref_changes", [])],
                        "compatible_drift": d.get("compatible_drift"), "pass": ok})

    scenario("S0_no_change", ["CONTINUE"], lambda: None)

    def s1():
        c, _ = commit_with(k4_tip, {"level4/closure_proofs/zz_unknown/STATUS.md": "P5Y state: K1 = CLOSED K5 = OPEN\n"},
                           "synthetic: unknown status carrier")
        g("update-ref", "refs/heads/zz-new-status", c)
    scenario("S1_new_ref_unknown_carrier", ["STOP_AMBIGUOUS_CROSS_REF_STATE"], s1)

    def s2():
        txt = show(k4_tip, K4_PATH).replace('"K4R1_SUCCESSOR_VERDICT": "CLOSED"', '"K4R1_SUCCESSOR_VERDICT": "NOT_CLOSED"')
        c, _ = commit_with(k4_tip, {K4_PATH: txt}, "synthetic: K4 verdict changed")
        for r in k4_refs:
            g("update-ref", r, c)
    scenario("S2_binding_ref_moved_incompatible", ["STOP_CONFLICTING_LIVE_RECORDS", "STOP_INCOMPATIBLE_BINDING_DRIFT"], s2)

    def s3():
        c, _ = commit_with(k4_tip, {"level4/zz_note.txt": "hello\n"}, "synthetic: unrelated file")
        for r in k4_refs:
            g("update-ref", r, c)
    scenario("S3_binding_ref_moved_compatible", ["CONTINUE"], s3)

    def s4():
        for r in k1_refs:
            g("update-ref", "-d", r)
    scenario("S4_binding_ref_deleted", ["STOP_MISSING_BINDING_RECORD"], s4)

    def s5():
        g("update-ref", "refs/heads/zz-renamed-k1", k1_tip)
        for r in k1_refs:
            g("update-ref", "-d", r)
    scenario("S5_binding_ref_renamed", ["CONTINUE"], s5)

    def s6():
        parent = g("rev-parse", f"{k1_tip}^")
        txt = show(k1_tip, K1_PATH).replace('"cpu_cap": 150', '"cpu_cap": 151')
        c, _ = commit_with(parent, {K1_PATH: txt}, "synthetic: divergent K1 record")
        g("update-ref", "refs/heads/zz-divergent-k1", c)
    scenario("S6_conflicting_live_records", ["STOP_CONFLICTING_LIVE_RECORDS"], s6)

    def s7():
        g("update-ref", "refs/tags/zz-old", base_snap["commit_tips"][0])
    scenario("S7_new_unrelated_ref_at_frozen_commit", ["CONTINUE"], s7)

    def s8():
        _, tree = commit_with(k4_tip, {"level4/closure_proofs/zz_tree/STATUS.md": "K5 = OPEN P5Y = NOT_YET_CLOSED\n"},
                              "synthetic tree only")
        g("update-ref", "refs/zz/tree-ref", tree)
    scenario("S8_new_tree_ref_unknown_carrier", ["STOP_AMBIGUOUS_CROSS_REF_STATE"], s8)

    def s9():
        txt = show(k4_tip, FLAGFILE).replace("K5_DECLARED_CLOSED       = NO", "K5_DECLARED_CLOSED       = YES")
        c, _ = commit_with(k4_tip, {FLAGFILE: txt}, "synthetic: positive closure flag")
        g("update-ref", "refs/heads/zz-flag", c)
    scenario("S9_positive_closure_flag", ["STOP_AMBIGUOUS_CROSS_REF_STATE", "STOP_POSITIVE_CLOSURE_FLAG"], s9)

    report = {"schema": "rebaseguard.p5y.k5.partial-closeout-r2.drift-selftest.v1",
              "clone": "git clone --shared --no-checkout (temporary, outside the repository; deleted afterwards)",
              "snapshot_verdict_in_clone": base_snap["verdict"], "snapshot_refs_in_clone": base_snap["refs_enumerated"],
              "k1_record_refs_in_clone": k1_refs, "k4_record_refs_in_clone": k4_refs,
              "scenarios": results, "pass": base_snap["verdict"] == "CONTINUE" and all(r["pass"] for r in results)}
    pathlib.Path(a.out).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    shutil.rmtree(clone)
    print(f"drift self-test pass={report['pass']} -> {a.out}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
