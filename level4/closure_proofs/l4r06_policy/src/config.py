"""Frozen configuration and paths for the L4R-06 policy campaign."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
RESULTS = BASE / "results"
CELLS = RESULTS / "cells"
FIGURES = BASE / "figures"
PYTHON = ROOT / "level4/.venv/bin/python"

PROTOCOL_SHA256 = "34120561dde61ea1ce5e9de50c37870d53326e726da77088bd2439062d9871fa"
COMBINED_PROTOCOL_SHA256 = "2abda564099eae20079806609af5d9a48144fa78c95c29de7ccf5e31f8a49faa"
SAFETY_FACTOR = 0.8
PRIMARY_EPSILON = 0.10
SECONDARY_EPSILON = 0.05
ABSOLUTE_DELAY_GUARD = 1.25
REGIMES = (1, 20, 70, 100)
ACTIVE_REGIMES = (1, 20, 70)
SHIFTS = (0.25, 0.5, 1.0, 1.5)
POLICY_LABELS = ("P0", "P1", "P2", "P3")
P2_RHO = 0.0297958439
SEED_CONFIRM = 2026082406
SEED_BOOTSTRAP = 2026082407
SEED_ADVERSARIAL = 2026082408
N_REPLICATES = 200
N_EVENTS = 200
BURN_IN = 300
CYCLES_BETWEEN = 15
N_BOOTSTRAP = 10_000


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n"
