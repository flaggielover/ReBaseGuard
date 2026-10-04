#!/usr/bin/env python3
"""PostToolUse tripwire for the P309 Q11 recovery session.

The PreToolUse guard sees only the command text; a program it allowed could still write somewhere it should not.
After every tool call this hook re-checks the repository itself:
  * every changed or untracked path lies in the declared write-set;
  * no exactly-once / production / test ref exists in the session repository;
  * HEAD is still on the allowed branch.
A violation is logged and reported with exit 2 (the harness shows it to the model; the session must stop and
report it -- a PostToolUse hook cannot undo the call).  It also logs the completed call for the SessionEnd audit.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p309_guard_policy as P  # noqa: E402
from p309_pretooluse_guard import in_write_set  # noqa: E402


def git(*a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(P.repo_root()), *a], capture_output=True, text=True, timeout=60)


def violations() -> list[str]:
    out = []
    st = git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    if st.returncode:
        return [f"git status failed: {st.stderr.strip()[:200]}"]
    entries = st.stdout.split("\0")
    k = 0
    while k < len(entries):
        e = entries[k]
        k += 1
        if not e:
            continue
        code, path = e[:2], e[3:]
        if code[0] in "RC":                              # rename / copy: the source path follows
            src = entries[k]
            k += 1
            if not in_write_set(src):
                out.append(f"{code.strip()} {src} (source)")
        if not in_write_set(path):
            out.append(f"{code.strip()} {path}")
    refs = git("for-each-ref", "--format=%(refname)").stdout.split()
    out += [f"protected ref {r}" for r in refs if P.PROTECTED_REF_RE.search(r)]
    br = git("symbolic-ref", "-q", "--short", "HEAD").stdout.strip()
    if br != P.ALLOWED_BRANCH:
        out.append(f"HEAD is on {br or 'a detached commit'}, not {P.ALLOWED_BRANCH}")
    return out


def main() -> int:
    try:
        ev = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        ev = {}
    ti, tr = ev.get("tool_input") or {}, ev.get("tool_response")
    resp = tr if isinstance(tr, dict) else {"text": str(tr)[:2000]}
    stdout = str(resp.get("stdout", resp.get("text", "")))
    rec = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds"),
           "hook": "PostToolUse", "session_id": ev.get("session_id"), "tool": ev.get("tool_name"),
           "command": str(ti.get("command"))[:4000] if "command" in ti else None,
           "file_path": ti.get("file_path") or ti.get("notebook_path"),
           "interrupted": resp.get("interrupted"), "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
           "stdout_tail": stdout[-1500:], "stderr_tail": str(resp.get("stderr", ""))[-800:]}
    try:
        v = violations()
    except Exception as exc:  # noqa: BLE001
        v = [f"tripwire error: {type(exc).__name__}: {exc}"]
    rec["violations"] = v
    try:
        d = P.audit_dir()
        d.mkdir(parents=True, exist_ok=True)
        with open(d / f"{ev.get('session_id') or 'nosession'}.jsonl", "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    except OSError as exc:
        v.append(f"audit log not writable: {exc}")
    if v:
        print("P309 TRIPWIRE: protected state changed after this call -- STOP and report:\n  " + "\n  ".join(v[:20]),
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
