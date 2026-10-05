#!/usr/bin/env python3
"""Negative and positive tests for the P309 session guard, tripwire and SessionEnd audit.

  python3 .claude/hooks/tests/test_guard.py [--out FILE]      exit 0 iff every case ends as specified

A refusal passes only if the guard exits 2 AND names the expected rule on stderr AND its audit log records the same
refusal (exit codes alone are never taken as evidence).  An allowance passes only if the guard exits 0 AND logs
"allow".  Commit, tripwire and audit cases run against throw-away fixture repositories under a temporary directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOOKS = HERE.parent
REPO = HOOKS.parents[1]
GUARD = HOOKS / "p309_pretooluse_guard.py"
TRIP = HOOKS / "p309_posttooluse_tripwire.py"
AUDIT = HOOKS / "p309_session_audit.py"
sys.path.insert(0, str(HOOKS))
import p309_guard_policy as P  # noqa: E402

SCRATCH = os.environ.get("P309_TEST_SCRATCH", "/tmp/p309-guard-scratch")


def sub(x, repo: str):
    if isinstance(x, str):
        return x.replace("@REPO@", repo).replace("@SCRATCH@", SCRATCH)
    if isinstance(x, dict):
        return {k: sub(v, repo) for k, v in x.items()}
    return x


def event(case: dict, repo: str, sid: str) -> str:
    if "raw" in case:
        return case["raw"]
    tool = case.get("tool", "Bash")
    if "input" in case:
        ti = sub(case["input"], repo)
    elif tool == "Bash":
        ti = {"command": sub(case["cmd"], repo)}
    elif tool == "Write":
        ti = {"file_path": sub(case["file"], repo), "content": case.get("content", "")}
    elif tool == "Edit":
        ti = {"file_path": sub(case["file"], repo), "old_string": case.get("old", ""), "new_string": case.get("new", "")}
    elif tool == "NotebookEdit":
        ti = {"notebook_path": sub(case["file"], repo), "new_source": case.get("new", "")}
    else:
        ti = {}
    if tool in ("Write", "Edit") and not ti["file_path"].startswith(("/", "~")):
        ti["file_path"] = str(Path(repo) / ti["file_path"])
    return json.dumps({"session_id": sid, "tool_name": tool, "tool_input": ti,
                       "cwd": sub(case.get("cwd", "@REPO@"), repo), "hook_event_name": "PreToolUse"})


def run_hook(script: Path, stdin: str, env_extra: dict) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR",)}
    env.update(env_extra)
    return subprocess.run([sys.executable, str(script)], input=stdin, capture_output=True, text=True, env=env,
                          timeout=60)


def last_log(audit_dir: Path, sid: str) -> dict:
    f = audit_dir / f"{sid}.jsonl"
    if not f.exists():
        return {}
    lines = [l for l in f.read_text().splitlines() if l.strip()]
    return json.loads(lines[-1]) if lines else {}


def vector_cases(tmp: Path) -> list[dict]:
    vec = json.loads((HERE / "guard_vectors.json").read_text())
    out = []
    for kind in ("deny", "allow"):
        for case in vec[kind]:
            sid = f"t-{case['id']}"
            ad = tmp / "audit_vectors"
            r = run_hook(GUARD, event(case, str(REPO), sid), {"P309_GUARD_REPO": str(REPO),
                                                              "P309_GUARD_AUDIT_DIR": str(ad)})
            log = last_log(ad, sid)
            if kind == "deny":
                if case["rule"] == "FAIL_CLOSED_INPUT":
                    ok = r.returncode == 2 and "fail closed" in r.stderr
                else:
                    ok = (r.returncode == 2 and f"[{case['rule']}]" in r.stderr and log.get("decision") == "deny"
                          and log.get("rule") == case["rule"])
            else:
                ok = r.returncode == 0 and log.get("decision") == "allow"
            out.append({"id": case["id"], "kind": kind, "expected_rule": case.get("rule"), "rc": r.returncode,
                        "stderr": r.stderr.strip()[:300], "logged": {k: log.get(k) for k in ("decision", "rule")},
                        "pass": ok})
    return out


def g(repo: Path, *a: str) -> str:
    e = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@invalid", "GIT_COMMITTER_NAME": "t",
         "GIT_COMMITTER_EMAIL": "t@invalid"}
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True, env=e).stdout


def fixture(tmp: Path, name: str) -> Path:
    fx = tmp / name
    fx.mkdir()
    g(fx, "init", "-q", "-b", P.ALLOWED_BRANCH)
    led = fx / "level4/closure_proofs/p5y_k5_cell309_p309_r1/ledger/ZERO_TARGET_LEDGER.jsonl"
    led.parent.mkdir(parents=True)
    led.write_text(json.dumps({"new_target_evaluations": 0, "target_equivalent_proxies": 0,
                               "target_informed_optimisation": 0}) + "\n")
    ok = fx / P.NEW_NS / "a.txt"
    ok.parent.mkdir(parents=True)
    ok.write_text("a\n")
    (fx / ".claude").mkdir()
    (fx / ".claude/.gitignore").write_text("audit/\n")
    g(fx, "add", "-A")
    g(fx, "commit", "-q", "-m", "fixture")
    return fx


def fixture_cases(tmp: Path) -> list[dict]:
    out = []

    def guard_commit(fx: Path, cmd: str, sid: str) -> subprocess.CompletedProcess:
        ev = json.dumps({"session_id": sid, "tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": str(fx)})
        return run_hook(GUARD, ev, {"P309_GUARD_REPO": str(fx), "P309_GUARD_AUDIT_DIR": str(tmp / "audit_fx")})

    def rec(cid, desc, r, ok):
        out.append({"id": cid, "kind": "fixture", "desc": desc, "rc": r.returncode, "stderr": r.stderr.strip()[:300],
                    "pass": ok})

    fx = fixture(tmp, "fx_commit")
    led = fx / "level4/closure_proofs/p5y_k5_cell309_p309_r1/ledger/ZERO_TARGET_LEDGER.jsonl"
    led.write_text(led.read_text() + "{}\n")
    g(fx, "add", "-A")
    r = guard_commit(fx, "git commit -m x", "c1")
    rec("CM1", "commit with a staged protected (r1 ledger) path is refused", r,
        r.returncode == 2 and "[R5_PROTECTED_WRITE]" in r.stderr and "ZERO_TARGET_LEDGER" in r.stderr)
    g(fx, "reset", "-q")
    (fx / P.NEW_NS / "a.txt").write_text("b\n")
    g(fx, "add", P.NEW_NS)
    commit_allow = getattr(P, "COMMIT_ALLOW", None)
    if commit_allow is not None:
        r = guard_commit(fx, "git commit -m x", "c2b")
        rec("CM2b", "commit of a write-set path outside the commit-set (COMMIT_ALLOW) is refused", r,
            r.returncode == 2 and "[R5_PROTECTED_WRITE]" in r.stderr and "may contain only" in r.stderr)
        g(fx, "reset", "-q")
        g(fx, "checkout", "-q", "--", P.NEW_NS)
        cf = fx / commit_allow[0]
        cf.parent.mkdir(parents=True, exist_ok=True)
        cf.write_text("c\n")
        g(fx, "add", commit_allow[0])
    r = guard_commit(fx, "git commit -m x", "c2")
    rec("CM2", "commit of write-set (and commit-set) paths only is allowed", r, r.returncode == 0)
    r = guard_commit(fx, "git commit -a -m x", "c3")
    rec("CM3", "commit -a sweeping in an unstaged protected change is refused", r,
        r.returncode == 2 and "[R5_PROTECTED_WRITE]" in r.stderr)
    r = guard_commit(fx, f"git commit -m x -- {led.relative_to(fx)}", "c3b")
    rec("CM3b", "commit with an explicit protected pathspec is refused", r,
        r.returncode == 2 and "[R5_PROTECTED_WRITE]" in r.stderr)
    g(fx, "checkout", "-q", "-b", "main")
    r = guard_commit(fx, "git commit -m x", "c4")
    rec("CM4", "commit on any branch but the allowed one is refused", r,
        r.returncode == 2 and "[R3_PUSH_TARGET]" in r.stderr)

    def trip(fx: Path, sid: str) -> subprocess.CompletedProcess:
        ev = json.dumps({"session_id": sid, "tool_name": "Bash", "tool_input": {"command": "x"},
                         "tool_response": {"stdout": "", "stderr": "", "interrupted": False}})
        return run_hook(TRIP, ev, {"P309_GUARD_REPO": str(fx), "P309_GUARD_AUDIT_DIR": str(tmp / "audit_trip")})

    t = fixture(tmp, "fx_trip")
    r = trip(t, "w1")
    rec("TW1", "tripwire is silent on a clean repository on the allowed branch", r, r.returncode == 0)
    (t / "level4/closure_proofs/p5y_k5_cell309_p309_r1/ledger/NEW.json").write_text("{}")
    r = trip(t, "w2")
    rec("TW2", "tripwire reports an untracked file in a protected namespace", r,
        r.returncode == 2 and "p5y_k5_cell309_p309_r1/ledger/NEW.json" in r.stderr)
    (t / "level4/closure_proofs/p5y_k5_cell309_p309_r1/ledger/NEW.json").unlink()
    g(t, "update-ref", "refs/p5y-k5-cell309-p309-r1/target-consumed", "HEAD")
    r = trip(t, "w3")
    rec("TW3", "tripwire reports a production exactly-once ref", r,
        r.returncode == 2 and "refs/p5y-k5-cell309-p309-r1/target-consumed" in r.stderr)
    g(t, "update-ref", "-d", "refs/p5y-k5-cell309-p309-r1/target-consumed")
    g(t, "checkout", "-q", "-b", "main")
    r = trip(t, "w4")
    rec("TW4", "tripwire reports HEAD leaving the allowed branch", r, r.returncode == 2 and "not " + P.ALLOWED_BRANCH in r.stderr)

    def audit(fx: Path, name: str) -> dict:
        out_f = tmp / f"{name}.json"
        r = run_hook(AUDIT, "", {"P309_GUARD_REPO": str(fx), "P309_GUARD_AUDIT_DIR": str(tmp / f"audit_{name}")})
        subprocess.run([sys.executable, str(AUDIT), "--snapshot", str(out_f)], capture_output=True, text=True,
                       env={**os.environ, "P309_GUARD_REPO": str(fx), "P309_GUARD_AUDIT_DIR": str(tmp / f"audit_{name}")},
                       check=True)
        return json.loads(out_f.read_text())["target_evaluation_count"]

    a = fixture(tmp, "fx_audit")
    c = audit(a, "sa1")
    out.append({"id": "SA1", "kind": "fixture", "desc": "audit counts 0 on a clean fixture",
                "pass": c["new_target_evaluations"] == 0 and c["ledger_rows_checked"] == 1, "count": c})
    g(a, "update-ref", "refs/p5y-k5-cell309-p309-r2/pending-result", "HEAD")
    c = audit(a, "sa2")
    out.append({"id": "SA2", "kind": "fixture", "desc": "audit counts a protected ref as an evaluation",
                "pass": c["new_target_evaluations"] >= 1 and c["protected_refs_in_session_repo"], "count": c})
    g(a, "update-ref", "-d", "refs/p5y-k5-cell309-p309-r2/pending-result")
    led = a / "level4/closure_proofs/p5y_k5_cell309_p309_r1/ledger/ZERO_TARGET_LEDGER.jsonl"
    led.write_text(led.read_text() + json.dumps({"new_target_evaluations": 1}) + "\n" + "{torn\n")
    c = audit(a, "sa3")
    out.append({"id": "SA3", "kind": "fixture", "desc": "audit counts a nonzero row and a torn (unreadable) row",
                "pass": c["ledger_rows_nonzero_or_unreadable"] == 2 and c["new_target_evaluations"] >= 2, "count": c})
    b = fixture(tmp, "fx_audit_grant")
    gp = b / "level4/closure_proofs/p5y_k5_cell309_p309_r2/authorization/P309_GRANT.json"
    gp.parent.mkdir(parents=True)
    gp.write_text("{}")
    c = audit(b, "sa4")
    out.append({"id": "SA4", "kind": "fixture", "desc": "audit counts a grant file the session added (untracked)",
                "pass": c["new_target_evaluations"] >= 1 and c["grant_or_result_files_added_or_changed_by_session"],
                "count": c})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="p309-guard-test-") as td:
        tmp = Path(td)
        cases = vector_cases(tmp) + fixture_cases(tmp)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HOOKS.glob("*.py"))}
    hashes["tests/guard_vectors.json"] = hashlib.sha256((HERE / "guard_vectors.json").read_bytes()).hexdigest()
    hashes["tests/test_guard.py"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    hashes["settings.json"] = hashlib.sha256((REPO / ".claude/settings.json").read_bytes()).hexdigest()
    fails = [c for c in cases if not c["pass"]]
    res = {"schema": "P309_GUARD_TESTS/1", "pass": not fails,
           "counts": {"total": len(cases), "deny": sum(c["kind"] == "deny" for c in cases),
                      "allow": sum(c["kind"] == "allow" for c in cases),
                      "fixture": sum(c["kind"] == "fixture" for c in cases), "failed": len(fails)},
           "hook_sha256": hashes, "python": platform.python_version(), "cases": cases}
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    for c in fails:
        print(f"FAIL {c['id']} ({c['kind']}, want {c.get('expected_rule')}): rc={c.get('rc')} {c.get('stderr', '')}")
    print(f"P309 GUARD TESTS: {res['counts']['total'] - len(fails)}/{res['counts']['total']} pass "
          f"(deny {res['counts']['deny']}, allow {res['counts']['allow']}, fixture {res['counts']['fixture']})")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
