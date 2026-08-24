#!/usr/bin/env python3
"""Protocol and protected-history integrity for external validation V2."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
PROTOCOL_FILES = [
    "PROTOCOL.md",
    "TASK_DEFINITIONS.md",
    "METRIC_DEFINITIONS.md",
    "results/protocol.json",
    "results/dataset_selection.json",
    "data_manifest/datasets.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protocol_record() -> dict:
    digest = hashlib.sha256()
    files = {}
    for relative in PROTOCOL_FILES:
        data = (BASE / relative).read_bytes()
        files[relative] = hashlib.sha256(data).hexdigest()
        digest.update(data)
    return {
        "schema": "rebaseguard.external-validation-v2.protocol-hash.v1",
        "frozen_at": "2026-08-24",
        "files": files,
        "combined_sha256": digest.hexdigest(),
        "combination_rule": "raw file bytes concatenated in recorded insertion order",
        "status": "FROZEN",
    }


def tracked_tree(root_name: str) -> dict:
    files = subprocess.check_output(
        ["git", "ls-files", "--", root_name], cwd=ROOT, text=True
    ).splitlines()
    digest = hashlib.sha256()
    for relative in files:
        rel = relative.encode()
        data = (ROOT / relative).read_bytes()
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return {"files": len(files), "sha256": digest.hexdigest()}


def verify() -> list[str]:
    errors = []
    expected = json.loads((BASE / "results/protocol_hash.json").read_text())
    if protocol_record() != expected:
        errors.append("frozen protocol bundle hash mismatch")
    execution = json.loads((BASE / "results/execution_hash.json").read_text())
    if sha256(BASE / execution["file"]) != execution["sha256"]:
        errors.append("frozen execution configuration hash mismatch")
    history = json.loads((BASE / "results/historical_hashes.json").read_text())
    for name, frozen in history["roots"].items():
        if tracked_tree(name) != frozen:
            errors.append(f"protected root changed: {name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-protocol-hash", action="store_true")
    args = parser.parse_args()
    if args.write_protocol_hash:
        path = BASE / "results/protocol_hash.json"
        path.write_text(json.dumps(protocol_record(), indent=2) + "\n")
        print(path)
        return 0
    errors = verify()
    print("integrity: PASS" if not errors else "integrity: FAIL")
    for error in errors:
        print(f"  {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
