"""Checkpoint push of the cell-309 research branch ONLY, under the user's standing preservation authorization
(2026-09-29): nine checks, all must pass, else no push.  Appends one line per attempt to ledger/CHECKPOINT_PUSHES.jsonl.

  1 fetch origin read-only (branch + main)            6 new commits touch only the research namespace
  2 current branch == BRANCH                           7 no target artifact / grant / marker / r6 / adoption / status
  3 push changes only this single ref (dry run)        8 explicit single-ref refspec, no tags, no force
  4 zero remote-only unique commits would be lost      9 fetch again; remote HEAD == local HEAD
  5 no force required (remote tip is an ancestor of HEAD, or the ref is absent)

Usage: python3 code/checkpoint_push.py [--dry]
"""
from __future__ import annotations

import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

BRANCH = "claude/rebaseguard-k5-cell-309-w0jv8m"
NS_PREFIX = "level4/closure_proofs/p5y_k5_cell309_research_r1/"
REPO = Path(__file__).resolve().parents[4]
LEDGER = Path(__file__).resolve().parents[1] / "ledger" / "CHECKPOINT_PUSHES.jsonl"
FORBIDDEN_PATH = re.compile(r"(^|/)(authorization|postexec|adjudication|protocol)/|GRANT|SEAL|target[-_]consumed|"
                            r"pending[-_]result|COVERAGE_MAP_R6|ADOPTION|_CELL30[5-9]_RESULT|TARGET_EXECUTION",
                            re.I)
ORDINARY_REF = re.compile(r"^refs/(heads|remotes|tags)/|^refs/stash$")   # anything else (e.g. an exactly-once marker) fails check 7


def git(*a, check=True) -> str:
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(a)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def remote_tip() -> str | None:
    out = git("ls-remote", "origin", f"refs/heads/{BRANCH}")
    return out.split()[0] if out else None


def main(dry: bool) -> int:
    rec = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "checks": {}}
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        rec["checks"][name] = {"pass": bool(cond), "detail": detail}
        ok = ok and bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    # 1 read-only fetch
    tip = remote_tip()
    git("fetch", "origin", "+refs/heads/main:refs/remotes/origin/main")
    if tip:
        git("fetch", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")
    chk("1_fetch_readonly", True, f"remote tip={tip or 'ABSENT'}")
    # 2 branch
    cur = git("rev-parse", "--abbrev-ref", "HEAD")
    chk("2_current_branch", cur == BRANCH, cur)
    head = git("rev-parse", "HEAD")
    rec["local_head"] = head
    clean = git("status", "--porcelain") == ""
    chk("2b_working_tree_clean", clean)
    # 4/5 no remote-only commits, no force
    if tip:
        is_anc = subprocess.run(["git", "merge-base", "--is-ancestor", tip, head], cwd=REPO).returncode == 0
        lost = git("rev-list", tip, f"^{head}") if is_anc is False else ""
        chk("4_zero_remote_only_commits", is_anc, f"remote-only: {len(lost.split()) if lost else 0}")
        chk("5_no_force_required", is_anc, "fast-forward" if is_anc else "NON-FAST-FORWARD")
        base = tip
    else:
        chk("4_zero_remote_only_commits", True, "ref absent: nothing to lose")
        chk("5_no_force_required", True, "ref absent: creation")
        base = "b73b9449fb13e7134455d8f5819c1f9d5290bb0b"
    # 6/7 new commits: namespace-only paths, no forbidden artifact
    new = git("rev-list", head, f"^{base}").split()
    paths = set(git("diff", "--name-only", base, head).split()) if new else set()
    outside = sorted(p for p in paths if not p.startswith(NS_PREFIX))
    chk("6_namespace_only", not outside, f"{len(new)} new commits, {len(paths)} paths; outside={outside[:5]}")
    bad = sorted(p for p in paths if FORBIDDEN_PATH.search(p))
    refs = [r for r in git("for-each-ref", "--format=%(refname)").split() if not ORDINARY_REF.match(r)]
    chk("7_no_target_or_governance_artifact", not bad and not refs, f"bad_paths={bad[:5]} marker_refs={refs[:5]}")
    # 3/8 dry run: exactly one ref, explicit refspec, no tags, no force
    spec = f"refs/heads/{BRANCH}:refs/heads/{BRANCH}"
    dr = subprocess.run(["git", "push", "--dry-run", "--porcelain", "origin", spec], cwd=REPO, capture_output=True,
                        text=True)
    lines = [l for l in dr.stdout.splitlines() if "\t" in l]
    single = len(lines) == 1 and lines[0].split("\t")[1].startswith(f"refs/heads/{BRANCH}:refs/heads/{BRANCH}")
    forced = any(l.startswith("+") for l in lines)
    uptodate = any(l.startswith("=") for l in lines)
    chk("3_single_ref_only", single and dr.returncode == 0, repr(lines))
    chk("8_explicit_refspec_no_force", not forced, spec)
    rec["new_commits"] = len(new)
    if not ok or dry or uptodate:
        rec["pushed"] = False
        rec["reason"] = "checks failed" if not ok else ("dry run" if dry else "already up to date")
        if not ok:
            _log(rec)       # failed attempts are recorded (the tree is then dirty on purpose: a failure needs attention)
        print("NO PUSH:", rec["reason"])
        return 0 if (ok and (dry or uptodate)) else 1
    r = subprocess.run(["git", "push", "origin", spec], cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        rec["pushed"] = False
        rec["reason"] = "push failed: " + r.stderr.strip()[-300:]
        _log(rec)
        print(rec["reason"])
        return 1
    # 9 verify
    git("fetch", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")
    after = git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    chk("9_remote_equals_local", after == head, f"remote={after} local={head}")
    rec["remote_head_after"] = after
    rec["pushed"] = True
    rec["mode"] = "plain fast-forward" if tip else "plain (branch creation)"
    rec["remote_only_commits_overwritten"] = 0
    _log(rec)
    # keep the working tree clean: record the push itself in a local commit (pushed at the next checkpoint)
    git("add", str(LEDGER.relative_to(REPO)))
    git("commit", "-q", "-m", f"p5y: K5 cell-309 research r1 — ledger: checkpoint push record ({head[:8]})\n\n"
        "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
        "Claude-Session: https://claude.ai/code/session_01RiV5bfPm5GJ4GcvoBrCC3p")
    return 0 if after == head else 1


def _log(rec):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")


if __name__ == "__main__":
    sys.exit(main("--dry" in sys.argv))
