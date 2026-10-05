#!/usr/bin/env python3
"""SessionEnd audit for the P309 Q11 recovery session (also run by hand with --snapshot OUT before the final commit).

Records, from the hook logs and the repository itself (never from the model's own account):
  * commands executed (PostToolUse) and every guard decision (PreToolUse), refusals by rule;
  * files written (Write / Edit calls, and the git diff against the branch point);
  * git: branch, HEAD, commits since the branch point, diff, working-tree state;
  * tests and their exact results (the committed TEST_RESULTS.json of the new namespace, by sha256);
  * the target-evaluation count, computed independently (protected refs, grant / result files, every execution
    ledger row's counter, and guard-allowed commands that match a target pattern);
  * unresolved blockers (BLOCKERS.json of the new namespace);
  * tripwire violations.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p309_guard_policy as P  # noqa: E402

LEDGER_GLOBS = ("level4/closure_proofs/p5y_k5_cell309_p309_r1/ledger/ZERO_TARGET_LEDGER.jsonl",
                P.NEW_NS + "ledger/ZERO_TARGET_LEDGER.jsonl")


def git(*a: str) -> str:
    r = subprocess.run(["git", "-C", str(P.repo_root()), *a], capture_output=True, text=True, timeout=120)
    return r.stdout if r.returncode == 0 else ""


def sha(p: Path) -> str | None:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return None


def read_logs() -> list[dict]:
    rows = []
    d = P.audit_dir()
    for f in sorted(d.glob("*.jsonl")) if d.exists() else []:
        for line in f.read_text(errors="replace").splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                rows.append({"hook": "UNPARSEABLE", "file": f.name})
    return rows


def target_count(rows: list[dict]) -> dict:
    refs = git("for-each-ref", "--format=%(refname)").split()
    prot = [r for r in refs if P.PROTECTED_REF_RE.search(r)]
    head_files = git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
    grant_at_head = [f for f in head_files if P.GRANT_RE.search(f)]
    # count what this session added or changed (committed since the branch point, or in the working tree); grant
    # files of other, older campaigns that are byte-identical at the branch point are listed, not counted
    if git("cat-file", "-t", P.BASE_COMMIT).strip() == "commit":
        changed = set(git("diff", "--name-only", P.BASE_COMMIT, "HEAD").splitlines())
    else:
        changed = set(head_files)                     # no branch point (fixtures): every file counts
    changed |= {l[3:] for l in git("status", "--porcelain=v1", "--untracked-files=all").splitlines()}
    grant = [f for f in sorted(changed) if P.GRANT_RE.search(f)]
    preexisting_grant = [f for f in grant_at_head if f not in changed]
    r6 = [f for f in head_files if re.search(r"COVERAGE_MAP_R6", f, re.I)]
    r5_blob = git("rev-parse", "HEAD:level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/"
                               "K5_COVERAGE_MAP_R5.json").strip()
    nonzero, total = 0, 0
    for rel in LEDGER_GLOBS:
        p = P.repo_root() / rel
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            total += 1
            try:
                r = json.loads(line)
            except ValueError:
                nonzero += 1                              # an unreadable row cannot be shown to be zero
                continue
            if any(r.get(k, 0) != 0 for k in ("new_target_evaluations", "target_equivalent_proxies",
                                               "target_informed_optimisation")):
                nonzero += 1
    allowed_target_cmds = [r.get("command") for r in rows if r.get("hook") == "PreToolUse" and
                           r.get("decision") == "allow" and r.get("command") and
                           (P.TARGET_MODE_RE.search(r["command"]))]
    count = len(prot) + len(grant) + nonzero + len(allowed_target_cmds)
    return {"new_target_evaluations": count, "protected_refs_in_session_repo": prot,
            "grant_or_result_files_added_or_changed_by_session": grant,
            "preexisting_grant_files_unchanged_since_branch_point": preexisting_grant, "r6_files_at_HEAD": r6,
            "r5_blob_at_HEAD": r5_blob, "r5_blob_expected": "f978eeb6b41188eabaf3c6d590c9178d711f1ce6",
            "r5_unchanged": r5_blob == "f978eeb6b41188eabaf3c6d590c9178d711f1ce6",
            "ledger_rows_checked": total, "ledger_rows_nonzero_or_unreadable": nonzero,
            "guard_allowed_target_mode_commands": allowed_target_cmds,
            "method": "independent of the model: refs, HEAD tree, every execution-ledger row, the guard's own log"}


def build(session_id: str | None) -> dict:
    rows = read_logs()
    pre = [r for r in rows if r.get("hook") == "PreToolUse"]
    post = [r for r in rows if r.get("hook") == "PostToolUse"]
    denied = [r for r in pre if r.get("decision") == "deny"]
    by_rule: dict = {}
    for r in denied:
        by_rule[r.get("rule")] = by_rule.get(r.get("rule"), 0) + 1
    ns = P.repo_root() / P.NEW_NS
    tests = ns / "evidence" / "TEST_RESULTS.json"
    blockers = ns / "BLOCKERS.json"
    hooks = {f.name: sha(f) for f in sorted(P.HOOK_DIR.glob("*.py"))}
    hooks["settings.json"] = sha(P.repo_root() / ".claude" / "settings.json")
    return {
        "schema": "P309_Q11_RECOVERY_SESSION_AUDIT/1",
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "session_id": session_id,
        "sessions_in_log": sorted({str(r.get("session_id")) for r in rows}),
        "hook_sha256": hooks,
        "git": {"branch": git("symbolic-ref", "-q", "--short", "HEAD").strip(),
                "head": git("rev-parse", "HEAD").strip(), "base": P.BASE_COMMIT,
                "commits_since_base": git("log", "--format=%H %s", f"{P.BASE_COMMIT}..HEAD").splitlines(),
                "diff_name_status_vs_base": git("diff", "--name-status", P.BASE_COMMIT, "HEAD").splitlines(),
                "working_tree_status": git("status", "--porcelain=v1", "--untracked-files=all").splitlines(),
                "remote_tracking_allowed_branch": git("rev-parse", "-q", "--verify",
                                                      f"refs/remotes/origin/{P.ALLOWED_BRANCH}").strip() or None},
        "commands": {"guard_decisions": len(pre), "allowed": len(pre) - len(denied), "denied": len(denied),
                     "denied_by_rule": by_rule,
                     "denied_detail": [{"utc": r.get("utc"), "rule": r.get("rule"), "why": r.get("why"),
                                        "command": (r.get("command") or r.get("file_path") or "")[:300]}
                                       for r in denied],
                     "executed_bash": [{"utc": r.get("utc"), "command": (r.get("command") or "")[:600],
                                        "interrupted": r.get("interrupted"), "stdout_sha256": r.get("stdout_sha256")}
                                       for r in post if r.get("tool") == "Bash"]},
        "files_written": sorted({r.get("file_path") for r in post
                                 if r.get("tool") in ("Write", "Edit", "MultiEdit", "NotebookEdit")
                                 and r.get("file_path")}),
        "tests": {"path": str(tests.relative_to(P.repo_root())), "sha256": sha(tests),
                  "content": json.loads(tests.read_text()) if tests.exists() else None},
        "target_evaluation_count": target_count(rows),
        "tripwire_violations": [{"utc": r.get("utc"), "violations": r.get("violations"),
                                 "command": (r.get("command") or r.get("file_path") or "")[:300]}
                                for r in post if r.get("violations")],
        "unresolved_blockers": json.loads(blockers.read_text()) if blockers.exists() else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", help="write the audit here (repository-relative or absolute)")
    a = ap.parse_args()
    sid = None
    if not a.snapshot:
        try:
            sid = json.loads(sys.stdin.read() or "{}").get("session_id")
        except ValueError:
            sid = None
    audit = build(sid)
    text = json.dumps(audit, indent=1, sort_keys=True, default=str) + "\n"
    if a.snapshot:
        out = Path(a.snapshot)
        out = out if out.is_absolute() else P.repo_root() / out
    else:
        out = P.audit_dir() / f"SESSION_AUDIT_{sid or 'unknown'}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"P309 SESSION AUDIT -> {out} (target evaluations {audit['target_evaluation_count']['new_target_evaluations']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
