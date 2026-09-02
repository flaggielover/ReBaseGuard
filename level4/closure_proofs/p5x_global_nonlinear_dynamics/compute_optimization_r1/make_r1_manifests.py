"""Freeze the R1 method documents and implementation at the Checkpoint-C anchor."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

R1 = Path(__file__).resolve().parent
NS = R1.parent
ROOT = NS.parents[2]
REL = R1.relative_to(ROOT).as_posix()

PROTOCOL = ["NEUTRALITY_AUDIT.md", "PROOF.md", "R1_FROZEN_SPEC.md"]
SOURCE = ["drift_minorant.py", "r1_stop_gate.py", "r1_selftest.py",
          "make_r1_manifests.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def block(paths, kind):
    return {"kind": kind, "namespace": REL,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "note": "byte identity to the Checkpoint-C anchor is mandatory",
            "files": {r: {"sha256": sha(R1 / r), "bytes": (R1 / r).stat().st_size}
                      for r in paths}}


def main() -> None:
    (R1 / "R1_PROTOCOL_DIGEST.json").write_text(
        json.dumps(block(PROTOCOL, "r1_protocol"), indent=1) + "\n")
    (R1 / "R1_SOURCE_MANIFEST.json").write_text(
        json.dumps(block(SOURCE, "r1_source"), indent=1) + "\n")
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.split()
    rel_ns = NS.relative_to(ROOT).as_posix()
    protected = {r: sha(ROOT / r) for r in tracked
                 if not r.startswith(rel_ns) and (ROOT / r).is_file()}
    ra = NS / "certified_method_repair_ra"
    ra_frozen = {p.relative_to(NS).as_posix(): sha(p)
                 for p in sorted(ra.iterdir()) if p.is_file()}
    (NS / "results" / "integrity" / "protected_tree_manifest_r1_pre.json").write_text(
        json.dumps({"kind": "protected_tree_pre_r1_optimization",
                    "generated_utc": datetime.now(timezone.utc).isoformat(),
                    "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                 capture_output=True, text=True).stdout.strip(),
                    "worktree": str(ROOT),
                    "namespace_excluded": rel_ns,
                    "tracked_file_count": len(protected),
                    "ra_reference_implementation_frozen": ra_frozen,
                    "files": protected}, indent=1) + "\n")
    print(f"protocol {len(PROTOCOL)}  source {len(SOURCE)}  protected {len(protected)}  ra_frozen {len(ra_frozen)}")


if __name__ == "__main__":
    main()
