#!/usr/bin/env python3
"""Verify every protected historical tree and report file."""
from __future__ import annotations

import hashlib
import json
import subprocess

from config import PROTECTED, ROOT


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def verify() -> dict:
    manifest = json.loads(PROTECTED.read_text())
    baseline = manifest["baseline_commit"]
    errors: list[str] = []
    if subprocess.run(["git", "merge-base", "--is-ancestor", baseline, "HEAD"],
                      cwd=ROOT).returncode:
        errors.append("audit baseline is not an ancestor of HEAD")
    for path, expected in manifest["trees"].items():
        try:
            actual = git("rev-parse", f"HEAD:{path}")
        except subprocess.CalledProcessError:
            errors.append(f"missing protected tree: {path}")
            continue
        if actual != expected:
            errors.append(f"protected tree changed: {path}")
        if subprocess.run(["git", "diff", "--quiet", baseline, "--", path],
                          cwd=ROOT).returncode:
            errors.append(f"protected working content changed: {path}")
    for path, expected in manifest["files"].items():
        target = ROOT / path
        if not target.exists():
            errors.append(f"missing protected file: {path}")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"protected file changed: {path}")
    return {
        "status": "INTACT" if not errors else "BROKEN",
        "baseline_commit": baseline,
        "trees_verified": len(manifest["trees"]),
        "files_verified": len(manifest["files"]),
        "errors": errors,
    }


def main() -> int:
    result = verify()
    print(f"protected history: {result['status']} "
          f"({result['trees_verified']} trees, {result['files_verified']} files)")
    for error in result["errors"]:
        print(f"- {error}")
    return 0 if result["status"] == "INTACT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
