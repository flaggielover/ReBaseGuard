"""Build the P5X frozen digests and the pre-campaign protected-tree manifest.

Run once, immediately before the Checkpoint A commit.  Re-running it after a
production result exists is a gate failure, not a convenience: the digests are
the definition of "frozen".
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
REL_NS = NS.relative_to(ROOT).as_posix()

# Documents whose bytes define the frozen protocol.  TEMPORAL_ANCHOR.md is
# deliberately excluded: it is the one file written twice (a commit cannot
# contain its own hash) and nothing is allowed to depend on its prose.
PROTOCOL = [
    "README.md",
    "FEASIBILITY_AUDIT.md",
    "THEOREM_CANDIDATES.md",
    "FAILURE_ANALYSIS.md",
    "FROZEN_THEOREM.md",
    "FROZEN_SCOPE.md",
    "PROOF_OBLIGATIONS.md",
    "CERTIFICATE_PLAN.md",
    "LEAN_PLAN.md",
    "EMPIRICAL_PLAN.md",
    "FROZEN_GATES.md",
    "LIMITATIONS.md",
    "CODEX_HANDOFF.md",
]

# Everything executable that existed before any production result.
SOURCE = [
    "scripts/make_manifests.py",
    "scripts/protected_tree.py",
    "feasibility/fredholm_probe.py",
    "feasibility/run_probe.py",
    "feasibility/results/reduction_probe.json",
    "tests/test_anchor_and_protection.py",
    "tests/test_frozen_documents.py",
    "tests/test_feasibility_probe.py",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return [line for line in out.splitlines() if line]


def untracked_dirs() -> dict[str, str]:
    """Content digest of each untracked directory outside the P5X namespace."""
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    files: dict[str, list[str]] = {}
    for line in out.splitlines():
        if not line.startswith("?? "):
            continue
        rel = line[3:].strip().strip('"')
        if rel.startswith(REL_NS):
            continue
        top = rel.split("/")[0] if "/" not in rel else "/".join(rel.split("/")[:3])
        files.setdefault(top, []).append(rel)
    digests = {}
    for top, members in sorted(files.items()):
        h = hashlib.sha256()
        for rel in sorted(members):
            p = ROOT / rel
            if p.is_file():
                h.update(rel.encode())
                h.update(sha256(p).encode())
        digests[top] = h.hexdigest()
    return digests


def digest_doc(paths: list[str], kind: str) -> dict:
    entries = {}
    for rel in paths:
        p = NS / rel
        if not p.exists():
            raise SystemExit(f"missing {kind} path: {rel}")
        entries[rel] = {"sha256": sha256(p), "bytes": p.stat().st_size}
    return {
        "kind": kind,
        "namespace": REL_NS,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "note": "byte-identity of these paths to the Checkpoint A commit is gate G1",
        "files": entries,
    }


def main() -> None:
    (NS / "PROTOCOL_DIGEST.json").write_text(
        json.dumps(digest_doc(PROTOCOL, "protocol"), indent=1) + "\n")
    (NS / "SOURCE_MANIFEST.json").write_text(
        json.dumps(digest_doc(SOURCE, "source"), indent=1) + "\n")

    protected = {}
    for rel in tracked_files():
        if rel.startswith(REL_NS):
            continue
        p = ROOT / rel
        if p.is_file():
            protected[rel] = sha256(p)
    manifest = {
        "kind": "protected_tree_pre_campaign",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip(),
        "namespace_excluded": REL_NS,
        "tracked_file_count": len(protected),
        "untracked_namespaces_outside_p5x": untracked_dirs(),
        "files": protected,
    }
    out = NS / "results" / "integrity" / "protected_tree_manifest_pre.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"protocol paths : {len(PROTOCOL)}")
    print(f"source paths   : {len(SOURCE)}")
    print(f"protected files: {len(protected)}")
    print(f"untracked outside P5X: {list(manifest['untracked_namespaces_outside_p5x'])}")


if __name__ == "__main__":
    main()
