"""Cell-307 RLR campaign (r1) -- append-only zero-target ledger (one JSON line per computation of the campaign).

Classes: START_STATE_READ, HISTORICAL_READ, NONTARGET_DECOY (pinned certifier or consumer on a declared decoy outside
the quarantined band), SYNTHETIC (no kernel), GOVERNANCE (git / file checks), DISCLOSURE (a retroactive record of a
past exposure; no computation), TARGET_EXECUTION (only the one granted
execution; written by nobody before the grant). Every line states new_target_evaluations and
target_equivalent_proxies explicitly.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[1] / "ledger" / "ZERO_TARGET_LEDGER_307.jsonl"
CLASSES = ("START_STATE_READ", "HISTORICAL_READ", "NONTARGET_DECOY", "SYNTHETIC", "GOVERNANCE", "DISCLOSURE")


def log(script: str, klass: str, purpose: str, drifts=None, cells=None, notes: str = "") -> None:
    if klass not in CLASSES:
        raise ValueError(f"ledger class {klass!r} is not a pre-grant class")
    row = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "script": script,
           "class": klass, "purpose": purpose, "drifts": drifts or [], "cells_touched": cells or [],
           "new_target_evaluations": 0, "target_equivalent_proxies": 0, "target_informed_optimisation": 0,
           "notes": notes}
    with LEDGER.open("a") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
