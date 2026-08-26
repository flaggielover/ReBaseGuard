#!/usr/bin/env python3
"""Verify the terminal audit's protected historical evidence."""
from __future__ import annotations

import hashlib
import subprocess
from typing import Any

from config import PROTECTED, ROOT, load


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def verify() -> dict[str, Any]:
    manifest = load(PROTECTED)
    baseline = manifest["baseline_commit"]
    errors: list[str] = []
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", baseline, "HEAD"], cwd=ROOT
    ).returncode:
        errors.append("starting audit HEAD is not an ancestor of current HEAD")
    for relative, expected in manifest["trees"].items():
        try:
            actual = _git("rev-parse", f"HEAD:{relative}")
        except subprocess.CalledProcessError:
            actual = "MISSING"
        if actual != expected:
            errors.append(f"tree {relative}: {actual} != {expected}")
        dirty = _git("status", "--porcelain", "--", relative)
        if dirty:
            errors.append(f"working-tree changes under {relative}: {dirty.splitlines()}")
    for relative, expected in manifest["files"].items():
        path = ROOT / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "MISSING"
        if actual != expected:
            errors.append(f"file {relative}: {actual} != {expected}")

    stage_f = load(ROOT / "level4/stage_f/results/final_decision.json")
    post = load(ROOT / "level4/re_audit_post_closure/results/final_decision.json")
    prior_final = load(ROOT / "level4/final_global_reaudit/results/final_decision.json")
    statuses = {
        "historical_stage_f": stage_f.get("decision"),
        "protected_post_closure": post.get("current_status"),
        "previous_final_global": prior_final.get("current_verdict"),
    }
    if any(value != "LEVEL-4-PARTIAL" for value in statuses.values()):
        errors.append(f"historical global verdict drift: {statuses}")
    return {
        "schema": "rebaseguard.final-level4-closure-integrity.v1",
        "status": "INTACT" if not errors else "BROKEN",
        "baseline_commit": baseline,
        "trees_verified": len(manifest["trees"]),
        "files_verified": len(manifest["files"]),
        "historical_global_statuses": statuses,
        "errors": errors,
    }


def main() -> int:
    result = verify()
    print(
        f"terminal protected history: {result['status']} "
        f"({result['trees_verified']} trees, {result['files_verified']} files)"
    )
    for error in result["errors"]:
        print(f"  {error}")
    return 0 if result["status"] == "INTACT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
