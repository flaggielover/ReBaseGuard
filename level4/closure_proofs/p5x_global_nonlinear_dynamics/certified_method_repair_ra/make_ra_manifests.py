"""Freeze the R-A' method documents and implementation at the pre-result anchor."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

RA = Path(__file__).resolve().parent
NS = RA.parent
ROOT = NS.parents[2]
REL = RA.relative_to(ROOT).as_posix()

PROTOCOL = ["RA_FEASIBILITY_AUDIT.md", "RA_FROZEN_SPEC.md"]
SOURCE = ["ra_certifier.py", "ra_selftest.py", "ra_diagnostics.py",
          "ra_stop_gate.py", "make_ra_manifests.py"]
ERRATA = ["../errata/D1_SR_DOMAIN_ERRATUM.md", "../errata/D1_MACHINE_SUMMARY.json"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def block(paths, kind):
    return {"kind": kind, "namespace": REL,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "note": "byte identity of these paths to the R-A pre-result anchor is mandatory",
            "files": {rel: {"sha256": sha(RA / rel), "bytes": (RA / rel).stat().st_size}
                      for rel in paths}}


def main() -> None:
    (RA / "RA_PROTOCOL_DIGEST.json").write_text(
        json.dumps(block(PROTOCOL + ERRATA, "ra_protocol"), indent=1) + "\n")
    (RA / "RA_SOURCE_MANIFEST.json").write_text(
        json.dumps(block(SOURCE, "ra_source"), indent=1) + "\n")
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.split()
    rel_ns = NS.relative_to(ROOT).as_posix()
    protected = {r: sha(ROOT / r) for r in tracked
                 if not r.startswith(rel_ns) and (ROOT / r).is_file()}
    (NS / "results" / "integrity" / "protected_tree_manifest_ra_pre.json").write_text(
        json.dumps({"kind": "protected_tree_pre_ra_repair",
                    "generated_utc": datetime.now(timezone.utc).isoformat(),
                    "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                 capture_output=True, text=True).stdout.strip(),
                    "namespace_excluded": rel_ns,
                    "tracked_file_count": len(protected),
                    "files": protected}, indent=1) + "\n")
    print(f"protocol {len(PROTOCOL)+len(ERRATA)}  source {len(SOURCE)}  protected {len(protected)}")


if __name__ == "__main__":
    main()
