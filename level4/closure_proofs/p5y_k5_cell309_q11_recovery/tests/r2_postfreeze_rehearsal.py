#!/usr/bin/env python3
"""Independent post-freeze rehearsal of r2's repaired QC11 / QC-D5 path (scratch replica; development evidence only).

  python3 r2_postfreeze_rehearsal.py --replica SCRATCH_CLONE_OF_r2 --work NEW_SCRATCH_DIR --out RESULT.json

Why: the r1 rehearsal shows that r2's QC11 harness repair, dropped into r1 alone, passes QC11 but fails QC-D5 --
r1's frozen scanner pins the harness by AST hash.  r2 ships the repair together with re-pinned scanner allowances.
This tool checks that package post-freeze, independently of r2's own drill tool (which it neither imports nor runs):
  1. a scratch clone of r2 at 101ef2cb (local remote only, clean, no protected ref);
  2. in the clone only: r2's UNMODIFIED generators and placeholder check make a synthetic freeze F'; a record-only
     child FR' records it; one checkpoint-style commit follows (the topology r2's plan section 5 prescribes);
  3. topology witness (computed here with git, not by r2 code): exactly one freeze-record commit at HEAD, its parent
     is F', F's own history holds none;
  4. QC11, QC12 and the three QC-D5 parts run exactly as r2's runner defines them (python -I -S -B; scan pins
     --list), with P309_SCRATCH_ROOT and P309_EVIDENCE_DIR under the work directory;
  5. verdicts from content: the QC11 flow table (every flow passes, a post-freeze sandbox holds exactly one record
     commit), the D5 control table, the backstop table, "P309 SCAN PINS: all current";
  6. after: no protected ref in the clone; the session repository unchanged.
Nothing here reads a target input; the driver is only exercised in TEST sandboxes by r2's own tests.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

SCRATCH_ROOT = Path("/tmp/claude-0")
SESSION_REPO = Path(__file__).resolve().parents[4]
R2_HEAD = "101ef2cb17e5eab2892212178278da45b98004ed"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
RECORD_REL = NS2 + "/ledger/FREEZE_RECORD.json"
CHECKPOINT_REL = NS2 + "/ledger/CHECKPOINT_PUSHES.jsonl"
PROTECTED = ("refs/p5y-k5-cell30", "refs/p309-cell309", "refs/rlr-tail/")


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(repo: Path, *a: str) -> str:
    e = {**os.environ, "GIT_AUTHOR_NAME": "p309-rehearsal", "GIT_AUTHOR_EMAIL": "rehearsal@invalid",
         "GIT_COMMITTER_NAME": "p309-rehearsal", "GIT_COMMITTER_EMAIL": "rehearsal@invalid"}
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True, env=e).stdout.strip()


def run(cmd: list, cwd: Path, env: dict, timeout=12 * 3600) -> dict:
    t0 = time.time()
    p = subprocess.run([str(c) for c in cmd], cwd=str(cwd), capture_output=True, text=True, env=env, timeout=timeout)
    return {"cmd": [str(c) for c in cmd], "rc": p.returncode, "wall_s": round(time.time() - t0, 1),
            "stdout_tail": p.stdout[-6000:], "stderr_tail": p.stderr[-3000:]}


def table(path: Path) -> dict:
    try:
        d = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        return {"_unreadable": str(exc)}
    return d


def flows_of(d: dict) -> dict:
    """the pass/fail entries of a control table (nested one level where the tool nests them)"""
    out = {}
    for k, v in d.items():
        if isinstance(v, dict) and isinstance(v.get("pass"), bool):
            out[k] = v["pass"]
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, dict) and isinstance(v2.get("pass"), bool):
                    out[f"{k}/{k2}"] = v2["pass"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replica", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    clone, work = Path(a.replica).resolve(), Path(a.work).resolve()
    for p in (clone, work):
        if SCRATCH_ROOT not in p.parents or SESSION_REPO in p.parents or p == SESSION_REPO:
            raise SystemExit(f"refused: {p} is not a scratch path outside the session repository")
    for url in git(clone, "remote", "-v").split():
        if "://" in url or "@" in url:
            raise SystemExit("refused: the replica has a network remote")
    if git(clone, "rev-parse", "HEAD") != R2_HEAD or git(clone, "status", "--porcelain", "--untracked-files=all"):
        raise SystemExit("refused: the replica is not a clean r2 checkout at 101ef2cb")
    if [r for r in git(clone, "for-each-ref", "--format=%(refname)").split() if r.startswith(PROTECTED)]:
        raise SystemExit("refused: protected ref in the replica")
    session_before = (git(SESSION_REPO, "rev-parse", "HEAD"), git(SESSION_REPO, "status", "--porcelain"))
    work.mkdir(parents=True)
    scratch, evid = work / "scratch", work / "evidence"
    scratch.mkdir()
    evid.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "P309_"))}
    env.update({"P309_SCRATCH_ROOT": str(scratch), "P309_EVIDENCE_DIR": str(evid), "PYTHONUNBUFFERED": "1"})
    fns = clone / NS2
    res = {"schema": "P309_R2_POSTFREEZE_REHEARSAL/1", "kind": "development rehearsal (scratch replica)",
           "utc_start": utc(), "replica_head": R2_HEAD, "python": platform.python_version(),
           "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
           "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}

    # 2. the topology (r2's unmodified generators, in the clone only)
    gens = [run([sys.executable, "-B", fns / "code" / g], clone, env) for g in
            ("make_freeze_manifest.py", "make_freeze_params.py", "p309_placeholder_check.py")]
    res["generators"] = [{"cmd": g["cmd"][-1].rsplit("/", 1)[-1], "rc": g["rc"], "tail": g["stdout_tail"][-300:]}
                         for g in gens]
    if any(g["rc"] for g in gens):
        res["verdict"] = "BLOCKED: the unmodified generators failed in the clone"
        Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
        return 1
    git(clone, "add", NS2)
    git(clone, "commit", "-q", "-m", "rehearsal: synthetic freeze F' (unmodified generators; never pushed)")
    f = git(clone, "rev-parse", "HEAD")
    (clone / RECORD_REL).write_text(json.dumps({"freeze_commit": f, "recorded_utc": utc(),
                                                "rule": "rehearsal: F's record-only child"}, indent=1) + "\n")
    git(clone, "add", RECORD_REL)
    git(clone, "commit", "-q", "-m", "rehearsal: freeze record FR' (record only)")
    fr = git(clone, "rev-parse", "HEAD")
    with open(clone / CHECKPOINT_REL, "a") as fh:
        fh.write(json.dumps({"utc": utc(), "rehearsal": True, "content_head": fr}) + "\n")
    git(clone, "add", CHECKPOINT_REL)
    git(clone, "commit", "-q", "-m", "rehearsal: checkpoint-style record commit")
    # 3. topology witness, computed here
    hist = git(clone, "log", "--format=%H", "HEAD", "--", RECORD_REL).split()
    res["topology"] = {"F": f, "FR": fr, "tip": git(clone, "rev-parse", "HEAD"),
                       "record_commits_at_head": len(hist), "record_parent_is_F": git(clone, "rev-parse", f"{fr}^") == f,
                       "record_commits_in_F_history": len(git(clone, "log", "--format=%H", f, "--", RECORD_REL).split()),
                       "record_commit_touches_only_record": git(clone, "diff", "--name-only", f, fr) == RECORD_REL}
    t = res["topology"]
    topo_ok = (t["record_commits_at_head"] == 1 and hist == [fr] and t["record_parent_is_F"]
               and t["record_commits_in_F_history"] == 0 and t["record_commit_touches_only_record"])

    # 4. the gates as r2's runner defines them
    py = sys.executable
    gates = {
        "QC11": [run([py, "-I", "-S", "-B", fns / "tests" / "test_p309_exactly_once.py"], fns, env)],
        "QC12": [run([py, "-I", "-S", "-B", fns / "code" / "p309_static_check.py"], fns, env)],
        "QC_D5": [run([py, "-I", "-S", "-B", fns / "tests" / "test_p309_d5_exception.py"], fns, env),
                  run([py, "-I", "-S", "-B", fns / "tests" / "test_p309_site_backstop.py"], fns, env),
                  run([py, fns / "code" / "p309_scan_pins.py", "--list"], fns, env)],
    }
    # 5. verdicts from content
    flows = table(next(iter(evid.rglob("EXACTLY_ONCE_FLOWS.json")), evid / "missing"))
    d5 = table(next(iter(evid.rglob("D5_EXCEPTION_CONTROLS.json")), evid / "missing"))
    bs = table(next(iter(evid.rglob("SITE_BACKSTOP_CONTROLS.json")), evid / "missing"))
    pins_tail = gates["QC_D5"][2]["stdout_tail"]
    ff, fd, fb = flows_of(flows), flows_of(d5), flows_of(bs)
    content = {
        "QC11_flows": len(ff), "QC11_flows_failed": sorted(k for k, v in ff.items() if not v),
        "QC11_table_pass": flows.get("pass"),
        "D5_controls": len(fd), "D5_controls_failed": sorted(k for k, v in fd.items() if not v),
        "backstop_controls": len(fb), "backstop_failed": sorted(k for k, v in fb.items() if not v),
        "scan_pins_all_current": "P309 SCAN PINS: all current" in pins_tail,
        "scan_pins_not_current": [l for l in pins_tail.splitlines() if "STALE" in l or "NOT LISTED" in l][:20],
        "QC12_static_check_tail": gates["QC12"][0]["stdout_tail"][-600:],
    }
    rcs = {k: [r["rc"] for r in v] for k, v in gates.items()}
    gate_pass = {
        "QC11": rcs["QC11"] == [0] and ff and not content["QC11_flows_failed"],
        "QC12": rcs["QC12"] == [0],
        "QC_D5": rcs["QC_D5"] == [0, 0, 0] and fd and fb and not content["D5_controls_failed"]
                 and not content["backstop_failed"] and content["scan_pins_all_current"],
    }
    refs_after = [r for r in git(clone, "for-each-ref", "--format=%(refname)").split() if r.startswith(PROTECTED)]
    session_after = (git(SESSION_REPO, "rev-parse", "HEAD"), git(SESSION_REPO, "status", "--porcelain"))
    res.update({"topology_ok": topo_ok, "gates": gate_pass, "rcs": rcs, "content": content,
                "runs": {k: [{kk: r[kk] for kk in ("cmd", "rc", "wall_s", "stdout_tail", "stderr_tail")} for r in v]
                         for k, v in gates.items()},
                "replica_protected_refs_after": refs_after,
                "session_repo_unchanged": session_before[0] == session_after[0],
                "evidence_sha256": {str(p.relative_to(evid)): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in sorted(evid.rglob("*")) if p.is_file()},
                "utc_end": utc(), "new_target_evaluations": 0})
    res["pass"] = topo_ok and all(gate_pass.values()) and not refs_after
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"pass": res["pass"], "topology_ok": topo_ok, "gates": gate_pass,
                      "content": {k: v for k, v in content.items() if k != "QC12_static_check_tail"}}, indent=1))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
