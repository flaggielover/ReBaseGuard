"""Run provenance: everything needed to re-create a formal run exactly.

A run that cannot produce this record is not a formal run.  ``build_manifest``
is called by every experiment driver before any data is written, and the
manifest is stored beside the raw output.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = Path(__file__).resolve().parent


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    return out.stdout.strip()


def git_state() -> dict[str, Any]:
    commit = _git("rev-parse", "HEAD")
    status = _git("status", "--porcelain")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    return {
        "commit": commit,
        "branch": branch,
        "dirty": None if status is None else bool(status),
        "dirty_paths": None if status is None else status.splitlines(),
    }


def dependency_versions() -> dict[str, str]:
    versions: dict[str, str] = {
        "python": sys.version,
        "python_short": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
    for name in ("numpy", "scipy", "pyarrow", "matplotlib"):
        try:
            module = __import__(name)
        except ImportError:
            versions[name] = "not installed"
        else:
            versions[name] = getattr(module, "__version__", "unknown")
    return versions


def code_hash() -> dict[str, str]:
    """SHA-256 of every source file in this package, plus a combined digest.

    This pins the *code version actually executed*, independently of whether the
    working tree is committed.
    """
    digests: dict[str, str] = {}
    for path in sorted(PACKAGE_ROOT.glob("*.py")):
        digests[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    combined = hashlib.sha256(
        "".join(f"{k}:{v}" for k, v in sorted(digests.items())).encode()
    ).hexdigest()
    digests["__combined__"] = combined
    return digests


def config_digest(config: dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def experiment_id(gate: str, stage: str, config: dict[str, Any]) -> str:
    """Deterministic experiment id: same gate+stage+config -> same id."""
    return f"{gate}-{stage}-{config_digest(config)[:12]}"


def build_manifest(
    *,
    gate: str,
    stage: str,
    config: dict[str, Any],
    streams: list[dict[str, Any]] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "experiment_id": experiment_id(gate, stage, config),
        "gate": gate,
        "stage": stage,
        "utc_timestamp": datetime.now(timezone.utc).isoformat(),
        "proof_role": "NON-RIGOROUS NUMERICAL DIAGNOSTIC — NOT PROOF EVIDENCE",
        "git": git_state(),
        "environment": dependency_versions(),
        "code_sha256": code_hash(),
        "config": config,
        "config_sha256": config_digest(config),
        "streams": streams or [],
    }
    if extra:
        manifest["extra"] = extra
    return manifest


def write_manifest(manifest: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=False, default=str))
    return path
