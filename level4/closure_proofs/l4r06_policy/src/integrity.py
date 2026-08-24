#!/usr/bin/env python3
"""Verify the frozen protocol and protected historical artifacts."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from config import BASE, COMBINED_PROTOCOL_SHA256, ROOT, read_json


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_tree(path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True
    ).strip()


def verify() -> dict[str, Any]:
    frozen = read_json(BASE / "results/historical_hashes.json")
    protocol = read_json(BASE / "results/protocol_hash.json")
    errors: list[str] = []

    for relative, expected in frozen["trees"].items():
        try:
            actual = git_tree(relative)
        except subprocess.CalledProcessError:
            actual = "MISSING"
        if actual != expected:
            errors.append(f"tree {relative}: {actual} != {expected}")

    for relative, expected in frozen["files"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else "MISSING"
        if actual != expected:
            errors.append(f"file {relative}: {actual} != {expected}")

    chunks = []
    for name in protocol["combined_sha256_order"]:
        path = BASE / name
        expected = protocol["files"][name]
        actual = sha256(path) if path.exists() else "MISSING"
        if actual != expected:
            errors.append(f"protocol file {name}: {actual} != {expected}")
        if path.exists():
            chunks.append(path.read_bytes())
    combined = hashlib.sha256(b"".join(chunks)).hexdigest()
    if combined != protocol["combined_sha256"] or combined != COMBINED_PROTOCOL_SHA256:
        errors.append(f"combined protocol: {combined}")
    if protocol["confirmatory_outcomes_existed_when_frozen"] is not False:
        errors.append("protocol does not certify a pre-outcome freeze")

    return {
        "schema": "rebaseguard.l4r06-integrity.v1",
        "status": "PASS" if not errors else "FAIL",
        "trees_verified": len(frozen["trees"]),
        "files_verified": len(frozen["files"]),
        "protocol_files_verified": len(protocol["files"]),
        "combined_protocol_sha256": combined,
        "historical_C6_preserved": not errors,
        "errors": errors,
    }


def main() -> int:
    result = verify()
    print(
        f"L4R-06 integrity: {result['status']} "
        f"({result['trees_verified']} trees, {result['files_verified']} files)"
    )
    for error in result["errors"]:
        print(f"  {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
