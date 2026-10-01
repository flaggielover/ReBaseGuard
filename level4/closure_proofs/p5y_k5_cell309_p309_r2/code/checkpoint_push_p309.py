"""Checkpoint push of the P309 FORMAL-CAMPAIGN branch ONLY (owner authorization 2026-09-30, "GITHUB / HISTORY": checkpoint
the dedicated formal-campaign branch/namespace with the same conservative single-ref procedure), adapted from the
research campaign's checkpoint_push.py (standing authorization 2026-09-29): nine checks, all must pass, else no push.  Appends one line per attempt to ledger/CHECKPOINT_PUSHES.jsonl.

  1 fetch origin read-only (branch + main)            6 new commits touch only the formal namespace
  2 current branch == BRANCH                           7 no target artifact / grant / marker / r6 / adoption / status
  3 push changes only this single ref (dry run)        8 explicit single-ref refspec, no tags, no force
  4 zero remote-only unique commits would be lost      9 fetch again; remote HEAD == local HEAD
  5 no force required (remote tip is an ancestor of HEAD, or the ref is absent)

Usage: python3 code/checkpoint_push_p309.py [--dry]
"""
from __future__ import annotations

import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

BRANCH = "claude/p5y-k5-cell309-p309-r2"  # q309: literal-ok (branch name, not a cell reference)
NS_PREFIX = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
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
    dirty = git("status", "--porcelain")
    # informational only (not one of the nine required checks): uncommitted files are never pushed
    rec["uncommitted_not_pushed"] = dirty.splitlines()
    print(f"[INFO] uncommitted (not pushed): {dirty.splitlines()}")
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
        base = "eb9a9c22b093f938e1bf13e0b30512608c58c370"          # research HEAD the formal branch starts from
    # 6/7 new commits: namespace-only paths, no forbidden artifact
    new = git("rev-list", head, f"^{base}").split()
    paths = set(git("diff", "--name-only", base, head).split()) if new else set()
    outside = sorted(p for p in paths if not p.startswith(NS_PREFIX))
    chk("6_namespace_only", not outside, f"{len(new)} new commits, {len(paths)} paths; outside={outside[:5]}")
    bad = sorted(p for p in paths if FORBIDDEN_PATH.search(p))
    refs = [r for r in git("for-each-ref", "--format=%(refname)").split() if not ORDINARY_REF.match(r)]
    chk("7_no_target_or_governance_artifact", not bad and not refs, f"bad_paths={bad[:5]} marker_refs={refs[:5]}")
    rq = REPO / "level4" / "closure_proofs" / "p5y_k5_cell309_research_r1" / "code" / "q309_guard.py"
    verdicts = []
    # formal namespace: code/p309_scan.py (research scanner + the owner-authorized narrow marker-name allowance +
    # formal rules); research namespace: the research scanner unchanged
    fs = REPO / NS_PREFIX / "code" / "p309_scan.py"
    for root in (REPO / NS_PREFIX, REPO / "level4" / "closure_proofs" / "p5y_k5_cell309_research_r1"):
        if root == REPO / NS_PREFIX:
            sc = subprocess.run([sys.executable, "-c", "import sys, json; sys.path.insert(0, %r); import p309_scan as "
                                 "S; print(json.dumps(S.scan()))" % str(fs.parent)], capture_output=True, text=True)
        else:
            sc = subprocess.run([sys.executable, "-c", "import sys, json; sys.path.insert(0, %r); import q309_guard "
                                 "as Q; from pathlib import Path; Q.NS = Path(%r); print(json.dumps(Q.scan(Path(%r))))"
                                 % (str(rq.parent), str(root), str(root))], capture_output=True, text=True)
        try:
            verdicts.append(json.loads(sc.stdout)["verdict"])
        except Exception:  # noqa: BLE001
            verdicts.append("UNREADABLE")
    verdict = "PASS" if all(v == "PASS" for v in verdicts) else "FAIL:" + ",".join(verdicts)
    # the research branch/namespace must be unchanged on this branch (owner: "preserve the research branch unchanged")
    research_changed = git("diff", "--name-only", "eb9a9c22b093f938e1bf13e0b30512608c58c370", head, "--",
                           "level4/closure_proofs/p5y_k5_cell309_research_r1/")
    chk("7c_research_namespace_unchanged", not research_changed, f"changed={research_changed.split()[:3]}")
    chk("7b_quarantine_static_scan", verdict == "PASS", verdict)
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
    # record-first (2026-09-29, fixes the one-unpushed-commit loop): the record of THIS push (checks 1-8 on the
    # content head) is committed before the push and travels with it; check 9 is verified after the push and is
    # visible as the next record's remote_before.  Only a failure writes an extra (uncommitted, on purpose) line.
    rec["phase"] = "pre-push record (committed with the push)"
    rec["content_head"] = head
    rec["remote_before"] = tip
    rec["mode"] = "plain fast-forward" if tip else "plain (branch creation)"
    rec["remote_only_commits_overwritten"] = 0
    _log(rec)
    ledger_rel = str(LEDGER.relative_to(REPO))
    git("add", ledger_rel)
    git("commit", "-q", "-m", f"p309 formal r1 — ledger: checkpoint push record ({head[:8]}; committed "
        "before the push, travels with it)\n\n"
        "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
        "Claude-Session: https://claude.ai/code/session_01RiV5bfPm5GJ4GcvoBrCC3p")
    head2 = git("rev-parse", "HEAD")
    # re-check the record commit: it touches exactly the ledger file; still one ref, no force
    rc_paths = git("diff", "--name-only", head, head2).split()
    chk("6b_record_commit_ledger_only", rc_paths == [ledger_rel], repr(rc_paths))
    dr2 = subprocess.run(["git", "push", "--dry-run", "--porcelain", "origin", spec], cwd=REPO, capture_output=True,
                         text=True)
    lines2 = [l for l in dr2.stdout.splitlines() if "\t" in l]
    chk("3b_single_ref_only_after_record", len(lines2) == 1 and dr2.returncode == 0
        and not any(l.startswith("+") for l in lines2), repr(lines2))
    if not ok:
        _log({"utc": rec["utc"], "pushed": False, "reason": "record-commit re-check failed", "local_head": head2})
        print("NO PUSH: record-commit re-check failed")
        return 1
    r = subprocess.run(["git", "push", "origin", spec], cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        _log({"utc": rec["utc"], "pushed": False, "reason": "push failed: " + r.stderr.strip()[-300:],
              "local_head": head2})
        print("push failed:", r.stderr.strip()[-300:])
        return 1
    # 9 verify
    git("fetch", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")
    after = git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    chk("9_remote_equals_local", after == head2, f"remote={after} local={head2}")
    if after != head2:
        _log({"utc": rec["utc"], "pushed": "UNVERIFIED", "reason": "remote != local after push",
              "remote_head_after": after, "local_head": head2})
        return 1
    return 0


def _log(rec):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")


if __name__ == "__main__":
    sys.exit(main("--dry" in sys.argv))
