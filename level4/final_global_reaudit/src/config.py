#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
RESULTS = BASE / "results"
SOURCE = BASE / "requirements.json"
PROTECTED = BASE / "protected_hashes.json"
PY = ROOT / "level4/.venv/bin/python"


def load(path: Path) -> dict:
    return json.loads(path.read_text())
