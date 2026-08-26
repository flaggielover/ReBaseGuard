#!/usr/bin/env python3
"""Shared constants for the terminal Level-4 closure audit."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
RESULTS = BASE / "results"
SOURCE = ROOT / "level4/final_global_reaudit/requirements.json"
PREVIOUS = ROOT / "level4/final_global_reaudit/results/final_decision.json"
PROTECTED = BASE / "protected_hashes.json"
PY = ROOT / "level4/.venv/bin/python"

STARTING_HEAD = "849bfe491ccc48b633f8c93fbb481b5f53ab754d"
ALLOWED_ROW_STATUSES = ("PASS", "PARTIAL", "FAIL", "OPEN")
ALLOWED_GLOBAL_STATUSES = (
    "LEVEL-4-CLOSED",
    "LEVEL-4-CLOSED-WITH-LIMITATIONS",
    "LEVEL-4-PARTIAL",
    "LEVEL-4-FAILED",
)


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
