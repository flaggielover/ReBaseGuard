#!/usr/bin/env python3
"""Verify all historical sources protected by the isolated L4R-12 audit."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from config import BASE, NEGATIVE_VERDICT, RESULTS, ROOT


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_at_head(relative: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{relative}"], cwd=ROOT, text=True
    ).strip()


def _dirty_paths(relative: str) -> list[str]:
    return subprocess.check_output(
        ["git", "status", "--porcelain", "--", relative], cwd=ROOT, text=True
    ).splitlines()


def verify() -> dict[str, Any]:
    frozen = json.loads((RESULTS / "historical_hashes.json").read_text())
    errors: list[str] = []
    for relative, expected in frozen["trees"].items():
        try:
            actual = _tree_at_head(relative)
        except subprocess.CalledProcessError:
            actual = "MISSING"
        if actual != expected:
            errors.append(f"tree {relative}: {actual} != {expected}")
        dirty = _dirty_paths(relative)
        if dirty:
            errors.append(f"working-tree changes under {relative}: {dirty}")

    for relative, expected in frozen["files"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else "MISSING"
        if actual != expected:
            errors.append(f"file {relative}: {actual} != {expected}")

    stage_d = json.loads((ROOT / "level4/stage_d/results/stage_d_decision.json").read_text())
    d25 = json.loads((ROOT / "level4/stage_d/results/d2_5_verdict.json").read_text())
    stage_f = json.loads((ROOT / "level4/stage_f/results/final_decision.json").read_text())
    post = json.loads((ROOT / "level4/re_audit_post_closure/results/final_decision.json").read_text())
    final_global = json.loads((ROOT / "level4/final_global_reaudit/results/final_decision.json").read_text())
    d4 = json.loads((ROOT / "level4/closure_proofs/d4_phase_map/results/decision.json").read_text())
    l4r06 = json.loads((ROOT / "level4/closure_proofs/l4r06_policy/results/decision.json").read_text())
    expected_statuses = {
        "stage_d": (stage_d.get("decision"), "STAGE-D-PARTIAL"),
        "stage_d_D2_5": (d25.get("verdict"), NEGATIVE_VERDICT),
        "stage_f": (stage_f.get("decision"), "LEVEL-4-PARTIAL"),
        "post_closure_current": (post.get("current_status"), "LEVEL-4-PARTIAL"),
        "post_closure_historical_stage_f": (
            post.get("historical_stage_f_status"), "LEVEL-4-PARTIAL"
        ),
        "final_global_current": (final_global.get("current_verdict"), "LEVEL-4-PARTIAL"),
        "final_global_historical_stage_f": (
            final_global.get("historical_stage_f_verdict"), "LEVEL-4-PARTIAL"
        ),
        "D4": (d4.get("decision"), "D4-PHASE-MAP-CLOSED"),
        "L4R06": (l4r06.get("scoped_verdict"), "L4R06-POLICY-CLOSED"),
    }
    for name, (actual, expected) in expected_statuses.items():
        if actual != expected:
            errors.append(f"status {name}: {actual!r} != {expected!r}")

    return {
        "schema": "rebaseguard.l4r12-integrity.v1",
        "status": "PASS" if not errors else "FAIL",
        "audited_commit": frozen["audited_commit"],
        "trees_verified": len(frozen["trees"]),
        "files_verified": len(frozen["files"]),
        "historical_statuses_verified": {
            name: actual for name, (actual, _) in expected_statuses.items()
        },
        "historical_D2_5_preserved": d25.get("verdict") == NEGATIVE_VERDICT,
        "D4_preserved": d4.get("decision") == "D4-PHASE-MAP-CLOSED",
        "L4R06_preserved": l4r06.get("scoped_verdict") == "L4R06-POLICY-CLOSED",
        "errors": errors,
    }


def main() -> int:
    result = verify()
    print(
        f"L4R-12 historical integrity: {result['status']} "
        f"({result['trees_verified']} trees, {result['files_verified']} files)"
    )
    for error in result["errors"]:
        print(f"  {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

