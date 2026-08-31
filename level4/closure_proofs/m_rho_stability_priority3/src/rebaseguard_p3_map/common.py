"""Small shared helpers for the Priority-3 map campaign."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def write_json(path: Path, payload: Any) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def dig(payload: Any, pointer: str) -> Any:
    """Resolve a dotted pointer such as ``score.gamma_mean``."""
    node = payload
    for part in pointer.split("."):
        node = node[part]
    return node
