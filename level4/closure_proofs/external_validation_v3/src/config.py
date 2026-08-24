#!/usr/bin/env python3
"""Frozen paths and structured V3 protocol access."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
CACHE = BASE / "data_cache"
RESULTS = BASE / "results"
PROTOCOL = json.loads((RESULTS / "protocol.json").read_text())
DATASETS = json.loads((BASE / "manifests/datasets.json").read_text())
PRIMARY_TASKS = tuple(PROTOCOL["primaries"])
POLICIES = PROTOCOL["policies"]
PROTOCOL_BUNDLE = (
    "METRIC_DEFINITIONS.md",
    "PROTOCOL.md",
    "TASK_DEFINITIONS.md",
    "manifests/datasets.json",
    "results/dataset_selection.json",
    "results/protocol.json",
)


def protocol_digest() -> str:
    digest = hashlib.sha256()
    for name in sorted(PROTOCOL_BUNDLE):
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update((BASE / name).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def dataset_record(task: str) -> dict:
    return next(row for row in DATASETS["datasets"] if row["id"] == task)


def task_config(task: str) -> dict:
    return PROTOCOL["tasks"][task]
