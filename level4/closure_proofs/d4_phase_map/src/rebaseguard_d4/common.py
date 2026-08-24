"""Deterministic serialization and batch-summary helpers."""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .config import Z95


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def write_json(path: Path, payload: Any) -> None:
    """Atomically write canonical, byte-stable JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        payload, indent=2, sort_keys=True, default=json_default, allow_nan=False
    ) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(encoded)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def batch_summary(values: Iterable[float]) -> dict[str, Any]:
    array = np.asarray(list(values), dtype=float)
    if array.ndim != 1 or array.size < 2 or not np.all(np.isfinite(array)):
        raise ValueError("at least two finite batch values required")
    mean = float(np.mean(array))
    se = float(np.std(array, ddof=1) / math.sqrt(array.size))
    return {
        "n_batches": int(array.size),
        "mean": mean,
        "se": se,
        "ci95": [mean - Z95 * se, mean + Z95 * se],
    }


def wilson_interval(successes: int, total: int) -> list[float]:
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("invalid binomial counts")
    p = successes / total
    z2 = Z95 * Z95
    den = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / den
    radius = Z95 * math.sqrt(p * (1.0 - p) / total + z2 / (4.0 * total**2)) / den
    return [max(0.0, center - radius), min(1.0, center + radius)]


def inverse_variance_pool(values: Iterable[float], ses: Iterable[float]) -> tuple[float, float]:
    value_array = np.asarray(list(values), dtype=float)
    se_array = np.asarray(list(ses), dtype=float)
    if value_array.size == 0 or value_array.shape != se_array.shape:
        raise ValueError("aligned nonempty values and SEs required")
    if np.any(~np.isfinite(value_array)) or np.any(~np.isfinite(se_array)):
        raise ValueError("finite values and SEs required")
    if np.any(se_array <= 0.0):
        raise ValueError("strictly positive SEs required")
    weight = 1.0 / np.square(se_array)
    return (
        float(np.sum(weight * value_array) / np.sum(weight)),
        float(math.sqrt(1.0 / np.sum(weight))),
    )
