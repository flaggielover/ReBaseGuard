"""Deterministic addressing, environment capture and artifact provenance.

Every P9R result artifact is written through :func:`write_artifact`, which
stamps the generator path, its argv, the frozen configuration actually used,
the git commit, the environment, and a SHA-256 digest of the payload.  The
focused test ``tests/test_generators.py`` refuses any artifact under
``results/`` that lacks a complete record, which is the direct repair of the
P9 defect "A5/A6 result files have no supplied generator".
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

P9R_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = P9R_ROOT.parents[2]
REL_P9R = "level4/closure_proofs/p9r_final_synthesis_repair"

#: P9R address namespace.  Distinct from P7's SEED_FAMILY (20260831), from
#: Stage D's (20261001) and from P9's ad-hoc SHA-256 of unsalted labels.
SEED_NAMESPACE = "rebaseguard/p9r/v1"


def seed_for(*parts) -> int:
    """Deterministic 63-bit seed from the namespace and the address fields.

    No seed is ever chosen by hand and no seed depends on execution order,
    on ``PYTHONHASHSEED`` or on which cells happen to be live.
    """
    label = "|".join([SEED_NAMESPACE] + [str(p) for p in parts])
    digest = hashlib.sha256(label.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") >> 1


def address(*parts) -> str:
    return "|".join([SEED_NAMESPACE] + [str(p) for p in parts])


def git_commit() -> str:
    try:
        return subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:                                    # pragma: no cover
        return "UNKNOWN"


def git_dirty() -> bool:
    try:
        out = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
                             capture_output=True, text=True, check=True).stdout
        return bool(out.strip())
    except Exception:                                    # pragma: no cover
        return True


def environment() -> dict:
    mods = {}
    for name in ("numpy", "scipy"):
        try:
            mods[name] = __import__(name).__version__
        except Exception:                                # pragma: no cover
            mods[name] = "ABSENT"
    return {"python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(), **mods}


def canonical_digest(payload) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      default=float).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def write_artifact(rel_path: str, *, schema: str, generator: str,
                   config: dict, payload: dict,
                   argv: list[str] | None = None) -> Path:
    """Write ``results/<rel_path>`` with a complete provenance record."""
    record = {
        "schema": schema,
        "generator": f"{REL_P9R}/{generator}",
        "argv": list(argv if argv is not None else sys.argv[1:]),
        "seed_namespace": SEED_NAMESPACE,
        "git_commit": git_commit(),
        "git_dirty_at_write": git_dirty(),
        "environment": environment(),
        "config": config,
        "payload_sha256": canonical_digest(payload),
        "payload": payload,
    }
    out = P9R_ROOT / "results" / rel_path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1, default=float) + "\n")
    return out
