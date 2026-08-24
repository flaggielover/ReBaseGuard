"""Load the frozen V2 protocol and execution configuration."""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
CACHE = BASE / "data/_cache"


def load_json(relative: str):
    return json.loads((BASE / relative).read_text())


PROTOCOL = load_json("results/protocol.json")
EXECUTION = load_json("results/execution_config.json")
DATASETS = load_json("data_manifest/datasets.json")
POLICIES = PROTOCOL["policies"]
PRIMARY_TASKS = tuple(PROTOCOL["campaign"]["primary_tasks"])


def dataset_record(task: str) -> dict:
    return next(row for row in DATASETS["datasets"] if row["id"] == task)


def task_time(task: str) -> dict:
    return PROTOCOL["task_time"][task]
