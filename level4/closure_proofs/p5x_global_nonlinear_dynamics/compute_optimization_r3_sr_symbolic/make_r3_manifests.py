"""Freeze the R3 method documents at the Checkpoint-E anchor."""
from __future__ import annotations
import hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

R3 = Path(__file__).resolve().parent
NS = R3.parent
ROOT = NS.parents[2]
REL = R3.relative_to(ROOT).as_posix()
PROTOCOL = ["EXACT_SR_TARGET.md", "R3_ARCHITECTURE_AUDIT.md", "PROOF.md",
            "R3_FROZEN_SPEC.md", "cusum_measurement_lane/CUSUM_MULTIPLIER_MEASUREMENT.md"]
SOURCE = ["make_r3_manifests.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def block(paths, kind):
    return {"kind": kind, "namespace": REL,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "note": "byte identity to the Checkpoint-E anchor is mandatory",
            "files": {r: {"sha256": sha(R3 / r), "bytes": (R3 / r).stat().st_size}
                      for r in paths}}


def main() -> None:
    (R3 / "R3_PROTOCOL_DIGEST.json").write_text(json.dumps(block(PROTOCOL, "r3_protocol"), indent=1) + "\n")
    (R3 / "R3_SOURCE_MANIFEST.json").write_text(json.dumps(block(SOURCE, "r3_source"), indent=1) + "\n")
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.split()
    rel_ns = NS.relative_to(ROOT).as_posix()
    protected = {r: sha(ROOT / r) for r in tracked
                 if not r.startswith(rel_ns) and (ROOT / r).is_file()}
    prior = {}
    for sub in ("certified_method_repair_ra", "compute_optimization_r1", "compute_optimization_r2"):
        d = NS / sub
        prior.update({p.relative_to(NS).as_posix(): sha(p) for p in sorted(d.iterdir()) if p.is_file()})
    (NS / "results" / "integrity" / "protected_tree_manifest_r3_pre.json").write_text(
        json.dumps({"kind": "protected_tree_pre_r3", "generated_utc": datetime.now(timezone.utc).isoformat(),
                    "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                 capture_output=True, text=True).stdout.strip(),
                    "worktree": str(ROOT), "namespace_excluded": rel_ns,
                    "tracked_file_count": len(protected),
                    "prior_campaign_files_frozen": prior, "files": protected}, indent=1) + "\n")
    print(f"protocol {len(PROTOCOL)} source {len(SOURCE)} protected {len(protected)} prior {len(prior)}")


if __name__ == "__main__":
    main()
