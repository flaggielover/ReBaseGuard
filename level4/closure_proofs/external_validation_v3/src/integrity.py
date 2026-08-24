#!/usr/bin/env python3
"""Verify frozen protocol and all protected historical repository trees."""
from __future__ import annotations

import json
import subprocess

from config import BASE, ROOT, protocol_digest


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def verify() -> list[str]:
    errors: list[str] = []
    frozen = json.loads((BASE / "results/protocol_hash.json").read_text())
    actual = protocol_digest()
    if actual != frozen["protocol_sha256"]:
        errors.append(f"protocol hash mismatch: {actual}")

    history = json.loads((BASE / "results/historical_hashes.json").read_text())
    baseline = history["baseline_commit"]
    if subprocess.run(["git", "merge-base", "--is-ancestor", baseline, "HEAD"],
                      cwd=ROOT).returncode:
        errors.append("historical baseline is not an ancestor of HEAD")
    for path, expected in history["trees"].items():
        try:
            current = git("rev-parse", f"HEAD:{path}")
        except subprocess.CalledProcessError:
            errors.append(f"missing protected tree: {path}")
            continue
        if current != expected:
            errors.append(f"protected tree changed: {path}")
        changed = subprocess.run(["git", "diff", "--quiet", baseline, "--", path],
                                 cwd=ROOT).returncode
        if changed:
            errors.append(f"protected working content changed: {path}")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        print("integrity: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("integrity: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
