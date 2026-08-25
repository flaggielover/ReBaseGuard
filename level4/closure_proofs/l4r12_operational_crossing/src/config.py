#!/usr/bin/env python3
"""Shared paths and deterministic serialization for the L4R-12 audit."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
RESULTS = BASE / "results"

PROTOCOL_SHA256 = "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e"
PRECOMMIT_SHA256 = "fb6272ef839d7f3b36af3c8a8ace3d3059df7028dda337455b9df6baaf92bba7"
ORIGINAL_WORDING = "Operational consequence of the Gamma_m crossing"
ORIGINAL_CLASS = "MANDATORY"
NEGATIVE_VERDICT = "MATHEMATICAL, NOT OPERATIONAL"
PRIMARY_METRICS = ("cycle_arl", "reference_mse", "e_acf1", "direction_acf1")
ALLOWED_SCOPED_STATUSES = (
    "L4R12-CLOSED-NEGATIVE-RESULT",
    "L4R12-PARTIAL",
    "L4R12-SEMANTICS-AMBIGUOUS",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())

