"""Re-check the protected tree against the pre-campaign manifest (gate G11)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
REL_NS = NS.relative_to(ROOT).as_posix()
MANIFEST = NS / "results" / "integrity" / "protected_tree_manifest_pre.json"
P5_PATH = "level4/closure_proofs/p5_nonlinear_dynamics"
P5_COMMIT = "bb03c0ea9ea34060c992b6d7f0390de6a3cf8108"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hash(commit: str, path: str) -> str:
    out = subprocess.run(["git", "rev-parse", f"{commit}:{path}"], cwd=ROOT,
                         capture_output=True, text=True)
    return out.stdout.strip()


def check() -> dict:
    manifest = json.loads(MANIFEST.read_text())
    recorded = manifest["files"]
    changed, missing, added = [], [], []
    seen = set()
    out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    for rel in out.splitlines():
        if not rel or rel.startswith(REL_NS):
            continue
        p = ROOT / rel
        if not p.is_file():
            continue
        seen.add(rel)
        if rel not in recorded:
            added.append(rel)
        elif sha256(p) != recorded[rel]:
            changed.append(rel)
    for rel in recorded:
        if rel not in seen:
            missing.append(rel)
    p5_now = tree_hash("HEAD", P5_PATH)
    p5_then = tree_hash(P5_COMMIT, P5_PATH)
    return {
        "changed_outside_p5x": sorted(changed),
        "missing_outside_p5x": sorted(missing),
        "added_outside_p5x": sorted(added),
        "p5_tree_hash_head": p5_now,
        "p5_tree_hash_bb03c0e": p5_then,
        "p5_immutable": bool(p5_now) and p5_now == p5_then,
        "pass": not changed and not missing and not added and p5_now == p5_then,
    }


if __name__ == "__main__":
    result = check()
    print(json.dumps(result, indent=1))
    sys.exit(0 if result["pass"] else 1)
