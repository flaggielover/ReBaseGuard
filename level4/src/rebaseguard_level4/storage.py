"""Raw (Parquet) and summary (JSON/CSV) persistence for Level 4 runs.

Raw cycle-level tables go to Parquet because they are large and columnar;
summaries and manifests go to JSON/CSV because they are small and want to be
diffable and human-readable.  Generated data under ``level4/results/raw`` is
gitignored by default (see ``level4/.gitignore``); manifests, processed
summaries and figures are tracked.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


def write_parquet(columns: Mapping[str, np.ndarray], path: Path, *,
                  metadata: Mapping[str, str] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.table({k: np.asarray(v) for k, v in columns.items()})
    if metadata:
        table = table.replace_schema_metadata(
            {k: str(v) for k, v in metadata.items()}
        )
    pq.write_table(table, path, compression="zstd")
    return path


def read_parquet(path: Path) -> dict[str, np.ndarray]:
    table = pq.read_table(path)
    return {name: table[name].to_numpy(zero_copy_only=False)
            for name in table.column_names}


def write_json(payload: Any, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=_jsonable))
    return path


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def write_csv(rows: list[Mapping[str, Any]], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return path
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _jsonable(row.get(k)) for k in fields})
    return path


def _jsonable(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    return value
