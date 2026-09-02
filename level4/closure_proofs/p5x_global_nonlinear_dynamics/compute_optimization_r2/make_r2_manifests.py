"""Freeze the R2 method documents and implementation at the Checkpoint-D anchor."""
from __future__ import annotations
import hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

R2 = Path(__file__).resolve().parent
NS = R2.parent
ROOT = NS.parents[2]
REL = R2.relative_to(ROOT).as_posix()
PROTOCOL = ["R2_PROFILE_AND_AUDIT.md", "R2_FROZEN_SPEC.md"]
SOURCE = ["profile_r1.py", "sensitivity.py", "make_r2_manifests.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def block(paths, kind):
    return {"kind": kind, "namespace": REL,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "note": "byte identity to the Checkpoint-D anchor is mandatory",
            "files": {r: {"sha256": sha(R2 / r), "bytes": (R2 / r).stat().st_size}
                      for r in paths}}


def main() -> None:
    (R2 / "R2_PROTOCOL_DIGEST.json").write_text(json.dumps(block(PROTOCOL, "r2_protocol"), indent=1) + "\n")
    (R2 / "R2_SOURCE_MANIFEST.json").write_text(json.dumps(block(SOURCE, "r2_source"), indent=1) + "\n")
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.split()
    rel_ns = NS.relative_to(ROOT).as_posix()
    protected = {r: sha(ROOT / r) for r in tracked
                 if not r.startswith(rel_ns) and (ROOT / r).is_file()}
    frozen_prior = {}
    for sub in ("certified_method_repair_ra", "compute_optimization_r1"):
        d = NS / sub
        frozen_prior.update({p.relative_to(NS).as_posix(): sha(p)
                             for p in sorted(d.iterdir()) if p.is_file()})
    (NS / "results" / "integrity" / "protected_tree_manifest_r2_pre.json").write_text(
        json.dumps({"kind": "protected_tree_pre_r2_optimization",
                    "generated_utc": datetime.now(timezone.utc).isoformat(),
                    "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                 capture_output=True, text=True).stdout.strip(),
                    "worktree": str(ROOT), "namespace_excluded": rel_ns,
                    "tracked_file_count": len(protected),
                    "prior_campaign_files_frozen": frozen_prior,
                    "files": protected}, indent=1) + "\n")
    print(f"protocol {len(PROTOCOL)} source {len(SOURCE)} protected {len(protected)} prior_frozen {len(frozen_prior)}")


if __name__ == "__main__":
    main()
