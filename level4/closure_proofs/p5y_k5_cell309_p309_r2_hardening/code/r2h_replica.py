#!/usr/bin/env python3
"""Scratch replicas of an r2-line package with a synthetic, non-target freeze (shared by the crash matrix and the
result-free rehearsal).

  build(source, commit, dest, scratch)  -> a fresh clone at `commit` (local remote only, clean, no protected ref)
  synthetic_freeze(clone, scratch)      -> F' (r2's unmodified generators + placeholder check), FR' (record-only
                                           child), one checkpoint-style commit; returns the witnessed topology

Nothing here reads a target input or runs a gate.  Every git write happens inside `dest`, never in `source`.
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
RECORD_REL = NS2 + "/ledger/FREEZE_RECORD.json"
CHECKPOINT_REL = NS2 + "/ledger/CHECKPOINT_PUSHES.jsonl"
PROTECTED = ("refs/p5y-k5-cell30", "refs/p309-cell309", "refs/rlr-tail/")
IDENTITY = {"GIT_AUTHOR_NAME": "p309-rehearsal", "GIT_AUTHOR_EMAIL": "rehearsal@invalid",
            "GIT_COMMITTER_NAME": "p309-rehearsal", "GIT_COMMITTER_EMAIL": "rehearsal@invalid"}


class ReplicaError(RuntimeError):
    pass


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(repo, *a, check=True) -> str:
    p = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, env={**os.environ, **IDENTITY})
    if check and p.returncode:
        raise ReplicaError(f"git {' '.join(a[:3])}: {p.stderr.strip()[:300]}")
    return p.stdout.strip()


def build(source: str, commit: str, dest: Path) -> dict:
    dest = Path(dest)
    if dest.exists():
        raise ReplicaError(f"{dest} exists (a replica is built once, never reused)")
    p = subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", "--origin", "isolated-source", str(source),
                        str(dest)], capture_output=True, text=True)
    if p.returncode:
        raise ReplicaError(f"clone failed: {p.stderr.strip()[:300]}")
    for url in git(dest, "remote", "-v").split():
        if "://" in url or "@" in url:
            raise ReplicaError("the replica has a network remote; only filesystem sources are accepted")
    if git(dest, "cat-file", "-t", commit, check=False) != "commit":
        git(dest, "fetch", "-q", str(source), commit)
    git(dest, "checkout", "-q", "-b", "rehearsal", commit)
    if git(dest, "rev-parse", "HEAD") != git(dest, "rev-parse", commit + "^{commit}"):
        raise ReplicaError("checkout did not land on the requested commit")
    if git(dest, "status", "--porcelain", "--untracked-files=all"):
        raise ReplicaError("the replica is not clean after checkout")
    bad = [r for r in git(dest, "for-each-ref", "--format=%(refname)").split() if r.startswith(PROTECTED)]
    if bad:
        raise ReplicaError(f"protected refs in the source: {bad[:3]}")
    return {"dest": str(dest), "commit": git(dest, "rev-parse", "HEAD"), "tree": git(dest, "rev-parse", "HEAD^{tree}"),
            "parents": git(dest, "rev-list", "--parents", "-n", "1", "HEAD").split()[1:]}


def synthetic_freeze(clone: Path, scratch: Path) -> dict:
    """F' by the package's own, unmodified generators and placeholder check; FR' records it; one checkpoint commit"""
    clone, fns = Path(clone), Path(clone) / NS2
    if git(clone, "log", "--format=%H", "HEAD", "--", RECORD_REL):
        raise ReplicaError("the package already carries a freeze record")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "P309_"))}
    env["P309_SCRATCH_ROOT"] = str(scratch)
    gens = []
    # order as in a real freeze: the parameters first, then the manifest (which pins freeze/P309_FREEZE.json; r1's F
    # manifest does), then the placeholder check.  r2's drill topology (p309_topology_drill.make_topology) runs the
    # manifest first: its F' manifest then lacks that pin and the runner's own `make_freeze_manifest --check`
    # precondition refuses -- finding F-DRILL-ORDER, invisible to the cloud tier, which never calls main().
    for g in ("make_freeze_params.py", "make_freeze_manifest.py", "p309_placeholder_check.py"):
        r = subprocess.run([sys.executable, "-B", str(fns / "code" / g)], cwd=str(clone), capture_output=True,
                           text=True, env=env)
        gens.append({"tool": g, "rc": r.returncode, "tail": (r.stdout + r.stderr)[-300:]})
        if r.returncode:
            raise ReplicaError(f"{g} failed in the replica: {(r.stdout + r.stderr)[-300:]}")
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
    hist = git(clone, "log", "--format=%H", "HEAD", "--", RECORD_REL).split()
    topo = {"F": f, "FR": fr, "tip": git(clone, "rev-parse", "HEAD"), "generators": gens,
            "record_commits_at_head": len(hist), "record_parent_is_F": git(clone, "rev-parse", fr + "^") == f,
            "record_commits_in_F_history": len(git(clone, "log", "--format=%H", f, "--", RECORD_REL).split()),
            "record_commit_touches_only_record": git(clone, "diff", "--name-only", f, fr) == RECORD_REL,
            "record_utc": git(clone, "log", "-1", "--format=%cI", fr)}
    topo["ok"] = (topo["record_commits_at_head"] == 1 and hist == [fr] and topo["record_parent_is_F"]
                  and topo["record_commits_in_F_history"] == 0 and topo["record_commit_touches_only_record"])
    if not topo["ok"]:
        raise ReplicaError(f"synthetic topology witness failed: {topo}")
    return topo
