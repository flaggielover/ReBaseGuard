#!/usr/bin/env python3
"""Reconstruct the two immutable SR snapshots from annotated Git tags."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]
SR_ROOT = "level4/closure_proofs/sr_derivative"
SNAPSHOTS = (
    ("terminal_level4", "rebaseguard-level4-closed", 52,
     "5e43336264f257c7224b622f8063eb10aad481d6",
     "abd869b91fe8ba3e69af9db0e7356a73c36c724f",
     "4d084982669c128967720d38a21d882fd92e3249835162e02ba452ad607594aa"),
    ("additive_sr_certificate", "rebaseguard-sr-gamma-certified", 92,
     "b04578810126d3fbc4d938a721481b1e6186b8ce",
     "a4fbe9890b0ba59d588766dccfa17e9ef9d45f1b",
     "3212a35f6f7ebc5d2e05bb791f0a099673f5d60d930ebede96d90fa8ea66a063"),
)


def git(*args: str, binary: bool = False):
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True)
    return result.stdout if binary else result.stdout.decode().strip()


def build(label: str, tag: str, count: int, commit: str, tree: str,
          aggregate: str) -> dict:
    assert git("rev-list", "-n", "1", tag) == commit
    assert git("rev-parse", f"{tag}:{SR_ROOT}") == tree
    paths = git("ls-tree", "-r", "--name-only", tag, SR_ROOT).splitlines()
    assert len(paths) == count
    files = []
    for path in paths:
        data = git("show", f"{tag}:{path}", binary=True)
        files.append({"path": path, "sha256": hashlib.sha256(data).hexdigest()})
    listing = "".join(f"{row['sha256']}  {row['path']}\n" for row in files)
    observed = hashlib.sha256(listing.encode()).hexdigest()
    assert observed == aggregate
    return {
        "label": label, "tag": tag, "commit": commit, "git_tree": tree,
        "file_count": count, "aggregate_sha256": aggregate, "files": files,
    }


def main() -> None:
    records = [build(*snapshot) for snapshot in SNAPSHOTS]
    old = {row["path"]: row["sha256"] for row in records[0]["files"]}
    new = {row["path"]: row["sha256"] for row in records[1]["files"]}
    assert all(new.get(path) == digest for path, digest in old.items())
    assert len(set(new) - set(old)) == 40
    payload = {
        "schema": "rebaseguard.priority2.sr-history.v1",
        "hash_rule": "sorted Git paths; each line '<content-sha256>  <path>\\n'; SHA-256 of UTF-8 concatenation",
        "snapshots": records,
        "original_52_byte_identical_in_92": True,
        "additive_path_count": 40,
    }
    (CAMPAIGN / "history" / "snapshots.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"counts": [r["file_count"] for r in records], "pass": True}))


if __name__ == "__main__":
    main()
