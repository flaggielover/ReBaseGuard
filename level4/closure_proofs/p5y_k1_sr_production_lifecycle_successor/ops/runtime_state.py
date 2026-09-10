"""IMMUTABLE SOURCE vs EXPECTED MUTABLE PRODUCTION STATE vs UNEXPECTED STATE.

The frozen approved-head gate runs `git status --porcelain` and refuses ANY
untracked file. Production itself creates untracked files inside the parent
namespace (ledger, ledger lock/tmp, cell records, cell temp files), so without a
rule every restart after the first ledger write is refused.

The rule is REPOSITORY-GOVERNED: the exact exclude block is the tracked file
config/RUNTIME_STATE_EXCLUDE of this successor, installed verbatim into the
repository's info/exclude (the only exclude source that leaves the approved
HEAD untouched) and VERIFIED before every run:

  * the block is present exactly once and byte-identical;
  * every declared runtime path is ignored BY THAT BLOCK;
  * a fixed set of look-alike unexpected paths is NOT ignored;
  * git never ignores tracked files, so tracked-source mutation still refuses.

Ignored does not mean trusted: every file under production/ is additionally
classified by content. Unexpected files REFUSE (this is the only guard on a
host without git, i.e. Vultr).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from opscommon import (OPS_NS, PARENT_NS_REL, OpsRefusal, fsync_dir, prod_ns, sha256_file,
                       write_json_atomic)

POLICY_FILE = OPS_NS / "config/RUNTIME_STATE_EXCLUDE"
BEGIN = "# BEGIN rebaseguard p5y_k1_sr production runtime state"

DECLARED = (
    ("FROZEN_LEDGER", re.compile(r"^production/PRODUCTION_LEDGER\.json$"), ("AWS", "VULTR")),
    ("FROZEN_LEDGER_LOCK", re.compile(r"^production/PRODUCTION_LEDGER\.json\.lock$"), ("AWS", "VULTR")),
    ("FROZEN_LEDGER_TMP", re.compile(r"^production/PRODUCTION_LEDGER\.tmp$"), ("AWS", "VULTR")),
    ("CELL_RECORD", re.compile(r"^production/cells/[0-9]{4}\.json$"), ("AWS", "VULTR")),
    ("CELL_TMP", re.compile(r"^production/cells/\.tmp-[^/]+$"), ("AWS", "VULTR")),
    ("HANDOFF_CONSUMED", re.compile(r"^evidence/handoff_consumed\.json$"), ("VULTR",)),
)
TRACKED_RUNTIME_NEIGHBOURS = ("production/README.md",)

POSITIVE_PROBES = ("production/PRODUCTION_LEDGER.json", "production/PRODUCTION_LEDGER.json.lock",
                   "production/PRODUCTION_LEDGER.tmp", "production/cells/0000.json",
                   "production/cells/0315.json", "production/cells/.tmp-abc123")
NEGATIVE_PROBES = ("production/foo.json", "production/PRODUCTION_LEDGER.json.bak",
                   "production/PRODUCTION_LEDGER.json.lock2", "production/cells/12345.json",
                   "production/cells/abc.json", "production/cells/0000.json.bak",
                   "production/cells/sub/0000.json", "production/cells/0000.jsonx",
                   "driver/new_module.py", "driver/production_launcher.py.orig",
                   "config/extra.json", "evidence/x.json", "evidence/handoff_consumed.json",
                   "tests/test_extra.py", "README.md.new")


def policy_block() -> str:
    return POLICY_FILE.read_text()


def _git(root, *args, check=True):
    r = subprocess.run(["git", "-C", str(root)] + list(args), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise OpsRefusal(f"git {' '.join(args)} failed: {r.stderr.strip()[:200]}")
    return r


def exclude_path(root) -> Path:
    common = _git(root, "rev-parse", "--git-common-dir").stdout.strip()
    p = Path(common)
    if not p.is_absolute():
        p = Path(root) / p
    return p / "info/exclude"


def install_git_policy(root) -> str:
    block = policy_block()
    ex = exclude_path(root)
    text = ex.read_text() if ex.exists() else ""
    if text.count(block) == 1:
        return "ALREADY_INSTALLED"
    if BEGIN in text:
        raise OpsRefusal(f"{ex} carries a DIFFERENT rebaseguard runtime block; refusing")
    ex.parent.mkdir(parents=True, exist_ok=True)
    new = text + ("" if text.endswith("\n") or not text else "\n") + block
    tmp = ex.with_name(ex.name + ".tmp-ops")
    tmp.write_text(new)
    os.replace(tmp, ex)
    return "INSTALLED"


def verify_git_policy(root) -> dict:
    block = policy_block()
    ex = exclude_path(root)
    text = ex.read_text() if ex.exists() else ""
    if text.count(block) != 1:
        raise OpsRefusal(f"governed runtime exclude block not installed exactly once in {ex}")
    lines = {l for l in block.splitlines() if l and not l.startswith("#")}
    for rel in POSITIVE_PROBES:
        path = f"{PARENT_NS_REL}/{rel}"
        r = _git(root, "check-ignore", "-v", path, check=False)
        if r.returncode != 0:
            raise OpsRefusal(f"declared runtime path is NOT ignored: {rel}")
        src, _, pat = r.stdout.split("\t")[0].split(":", 2)
        srcp = Path(src) if Path(src).is_absolute() else Path(root) / src
        if srcp.resolve() == ex.resolve():
            if pat not in lines:
                raise OpsRefusal(f"{rel} is ignored by a NON-governed info/exclude line {pat!r}")
        elif _git(root, "ls-files", "--error-unmatch", src, check=False).returncode != 0:
            raise OpsRefusal(f"{rel} is ignored by {src}:{pat}, which is neither the governed "
                             "block nor a tracked repository .gitignore")
    established = []
    for rel in NEGATIVE_PROBES:
        r = _git(root, "check-ignore", "-v", f"{PARENT_NS_REL}/{rel}", check=False)
        if r.returncode != 0:
            continue
        src = r.stdout.split("\t")[0].split(":", 2)[0]
        srcp = Path(src) if Path(src).is_absolute() else Path(root) / src
        tracked = _git(root, "ls-files", "--error-unmatch", src, check=False).returncode == 0
        if srcp.resolve() == ex.resolve() or not tracked:
            raise OpsRefusal(f"unexpected path would be SILENTLY IGNORED by a local exclude "
                             f"source: {rel} ({r.stdout.strip()})")
        # ignored by the ESTABLISHED tracked repository policy (e.g. *.bak): git status will
        # not show it, so the content classifier (classify_tree) is the guard and refuses it.
        established.append(f"{rel} <- {r.stdout.split(chr(9))[0]}")
    return {"exclude_file": str(ex), "block_sha256": sha256_file(POLICY_FILE),
            "positive_probes": len(POSITIVE_PROBES), "negative_probes": len(NEGATIVE_PROBES),
            "ignored_by_established_tracked_policy_classifier_guarded": established}


def classify(rel: str, role: str):
    for kind, rx, roles in DECLARED:
        if rx.match(rel):
            return kind if role in roles else None
    return None


def classify_tree(spec, role, state, owners) -> dict:
    """Classify EVERY file under production/ (+ the Vultr handoff record)."""
    ns = prod_ns(spec)
    out = {"expected": [], "orphan_results": [], "stale_tmp": [], "unexpected": [],
           "mismatch": [], "lock": []}
    completed = (state or {}).get("completed_cells", {})
    cands = [p for p in (ns / "production").rglob("*") if p.is_file() or p.is_symlink()]
    hc = ns / "evidence/handoff_consumed.json"
    if hc.exists():
        cands.append(hc)
    for p in sorted(cands):
        rel = p.relative_to(ns).as_posix()
        if rel in TRACKED_RUNTIME_NEIGHBOURS:
            continue
        kind = classify(rel, role)
        if kind is None or p.is_symlink():
            out["unexpected"].append(rel)
        elif kind in ("FROZEN_LEDGER", "HANDOFF_CONSUMED"):
            out["expected"].append(rel)
        elif kind == "FROZEN_LEDGER_LOCK":
            out["lock"].append(rel)
        elif kind in ("FROZEN_LEDGER_TMP", "CELL_TMP"):
            out["stale_tmp"].append(rel)
        elif kind == "CELL_RECORD":
            cell = int(p.stem)
            if owners.get(cell) != role:
                out["unexpected"].append(rel)
                continue
            try:
                rec = json.loads(p.read_bytes())
            except Exception:                                     # noqa: BLE001
                rec = None
            if str(cell) in completed:
                (out["expected"] if rec == completed[str(cell)] else out["mismatch"]).append(rel)
            else:
                out["orphan_results"].append(rel)
    return out


def quarantine(rt, spec, rels, reason) -> list:
    """Move non-admissible runtime files OUT of the source tree. Never deleted,
    never read back as results."""
    ns = prod_ns(spec)
    if not rels:
        return []
    qd = rt.root / "quarantine" / (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
                                   + "-" + os.urandom(3).hex())
    moved = []
    for rel in rels:
        src = ns / rel
        dst = qd / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        digest = sha256_file(src)
        try:
            os.replace(src, dst)
        except OSError:
            shutil.copy2(src, dst)
            os.unlink(src)
        fsync_dir(src.parent)
        moved.append({"path": rel, "sha256": digest, "reason": reason})
    write_json_atomic(qd / "QUARANTINE_MANIFEST.json", {"files": moved})
    return moved
