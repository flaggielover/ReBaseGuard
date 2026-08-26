#!/usr/bin/env python3
"""Pure Level-4 count and taxonomy derivation."""
from __future__ import annotations

from collections import Counter
from typing import Any

from config import ALLOWED_GLOBAL_STATUSES, ALLOWED_ROW_STATUSES


def derive(rows: list[dict[str, Any]], integrity_ok: bool, engineering_ok: bool) -> dict[str, Any]:
    counts = Counter(row["current_status"] for row in rows)
    mandatory = [row for row in rows if row["mandatory"]]
    mandatory_counts = Counter(row["current_status"] for row in mandatory)
    blockers = [row for row in mandatory if row["current_status"] != "PASS"]
    invalid = [row["id"] for row in rows if row["current_status"] not in ALLOWED_ROW_STATUSES]
    if invalid:
        verdict = "LEVEL-4-FAILED"
    elif blockers or not integrity_ok or not engineering_ok:
        verdict = "LEVEL-4-PARTIAL"
    else:
        verdict = "LEVEL-4-CLOSED"
    assert verdict in ALLOWED_GLOBAL_STATUSES
    return {
        "current_counts": {status: counts[status] for status in ALLOWED_ROW_STATUSES},
        "mandatory_counts": {status: mandatory_counts[status] for status in ALLOWED_ROW_STATUSES},
        "original_requirement_count": len(rows),
        "mandatory_requirement_count": len(mandatory),
        "mandatory_blocker_ids": [row["id"] for row in blockers],
        "invalid_status_ids": invalid,
        "integrity_ok": bool(integrity_ok),
        "engineering_ok": bool(engineering_ok),
        "current_verdict": verdict,
        "rule": "ALL_MANDATORY_ROWS_PASS_AND_ENGINEERING_GATES_PASS",
    }
