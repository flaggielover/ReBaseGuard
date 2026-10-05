#!/usr/bin/env python3
"""Recompute every sha256/bytes in r2_candidate_followup/EVIDENCE_INDEX.json against the committed (git show 4b3baebd)
copies exported under ev/, and list committed files the index does not cover.  Also does the same for
r2_candidate/R2_CANDIDATE_EVIDENCE_MANIFEST.json when its shape allows."""
import hashlib
import json
from pathlib import Path

EV = Path("/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t5/review/ev")


def check(base: Path, files: dict, label: str) -> None:
    ok = bad = 0
    for rel, meta in sorted(files.items()):
        p = base / rel
        if not p.exists():
            print(f"[{label}] MISSING {rel}")
            bad += 1
            continue
        b = p.read_bytes()
        h = hashlib.sha256(b).hexdigest()
        exp_h = meta.get("sha256") if isinstance(meta, dict) else meta
        exp_n = meta.get("bytes") if isinstance(meta, dict) else None
        if h != exp_h or (exp_n is not None and exp_n != len(b)):
            print(f"[{label}] MISMATCH {rel}: index {exp_h} / {exp_n}, recomputed {h} / {len(b)}")
            bad += 1
        else:
            ok += 1
    have = {str(p.relative_to(base)) for p in base.rglob("*") if p.is_file()}
    uncovered = sorted(have - set(files))
    print(f"[{label}] entries={len(files)} match={ok} mismatch_or_missing={bad} committed_not_indexed={uncovered}")


idx = json.loads((EV / "r2_candidate_followup" / "EVIDENCE_INDEX.json").read_text())
check(EV / "r2_candidate_followup", idx["files"], "followup")
for k in ("schema", "candidate_commit", "previous_candidate_commit", "base_r2_commit", "verdict", "statement",
          "test_tool"):
    print(k, "=", json.dumps(idx.get(k))[:400])

man = json.loads((EV / "r2_candidate" / "R2_CANDIDATE_EVIDENCE_MANIFEST.json").read_text())
print("manifest keys:", list(man)[:20])
files = man.get("files") or {}
if isinstance(files, list):
    files = {f.get("path"): f for f in files}
if files:
    check(EV / "r2_candidate", files, "task3")
