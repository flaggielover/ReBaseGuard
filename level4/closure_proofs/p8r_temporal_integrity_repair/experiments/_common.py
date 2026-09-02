"""Shared provenance envelope for every P8R production artifact.

`REPAIR_RATIONALE.md` §4 requires that no P8R result file be an orphan: every
one carries the generator that made it, the exact argv, the git commit, the
environment, the address class and tags it consumed, and a content digest of its
own payload.  ``scripts/audit_integrity.py`` gate ``I10`` walks
``results/**`` and fails if any file lacks this envelope or names a generator
that does not exist.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))

ROOT = HERE.parents[2]


def git_commit() -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:                                    # pragma: no cover
        return "UNAVAILABLE"


def environment() -> dict:
    import numpy
    import scipy
    return {"python": sys.version.split()[0],
            "numpy": numpy.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "machine": platform.machine()}


def payload_digest(payload) -> str:
    """SHA-256 of the canonical JSON encoding of a result payload."""
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"),
                   default=float).encode()).hexdigest()


def envelope(*, generator: str, schema: str, tags, payload: dict,
             extra: dict | None = None) -> dict:
    """Wrap ``payload`` with the frozen P8R provenance envelope."""
    env = {"schema": schema,
           "campaign": "P8R",
           "generator": generator if "/" in generator
                        else f"experiments/{generator}",
           "argv": list(sys.argv),
           "git_commit": git_commit(),
           "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime()),
           "environment": environment(),
           "address_tags": list(tags),
           "payload_sha256": payload_digest(payload)}
    if extra:
        env.update(extra)
    env["payload"] = payload
    return env


def write(dest: Path, doc: dict) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(doc, indent=1, default=float) + "\n")


def load_payload(p: Path) -> dict:
    return json.loads(Path(p).read_text())["payload"]
