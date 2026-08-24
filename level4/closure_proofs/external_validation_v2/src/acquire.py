#!/usr/bin/env python3
"""Acquire official public archives and enforce frozen SHA-256 checksums."""
from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

from config import CACHE, PRIMARY_TASKS, dataset_record


def archive_path(task: str) -> Path:
    return CACHE / f"{task}.zip"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def acquire(task: str) -> Path:
    record = dataset_record(task)
    path = archive_path(task)
    CACHE.mkdir(parents=True, exist_ok=True)
    if path.exists() and sha256(path) == record["archive_sha256"]:
        return path
    if path.exists():
        raise RuntimeError(f"checksum mismatch for existing cache file: {path}")
    subprocess.run(
        ["curl", "-fL", "--retry", "3", "--max-time", "900", "--silent",
         "--show-error", record["url"], "-o", str(path)],
        check=True,
    )
    actual = sha256(path)
    if actual != record["archive_sha256"]:
        raise RuntimeError(f"{task}: expected {record['archive_sha256']}, got {actual}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tasks", nargs="*", default=list(PRIMARY_TASKS))
    args = parser.parse_args()
    for task in args.tasks:
        path = acquire(task)
        print(f"{task}: {sha256(path)} {path.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
