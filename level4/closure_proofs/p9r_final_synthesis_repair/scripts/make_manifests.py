#!/usr/bin/env python3
"""Build the three P9R integrity manifests.

``SOURCE_MANIFEST.json``     SHA-256 of every file under ``src/``,
                            ``experiments/``, ``scripts/`` and ``tests/`` —
                            the executable surface of the campaign.
``PROTOCOL_DIGEST.json``     SHA-256 of every frozen prose artifact.
``results/integrity/protected_tree_manifest_{pre,final}.json``
                            SHA-256 of every tracked file outside the P9R
                            namespace, with a per-tree aggregate.

Usage: make_manifests.py [--stage anchor|final]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

P9R = Path(__file__).resolve().parents[1]
ROOT = P9R.parents[2]
REL_P9R = "level4/closure_proofs/p9r_final_synthesis_repair"

SOURCE_DIRS = ("src", "experiments", "scripts", "tests")

FROZEN_PROSE = (
    "README.md",
    "DEFINITION_AUDIT.md",
    "REPAIR_RATIONALE.md",
    "FROZEN_PROTOCOL.md",
    "FROZEN_GATES.md",
    "CLAIM_LANGUAGE_FIREWALL.md",
    "DISCREPANCY_REGISTER.md",
    "THEORY.md",
    "COMMAND_MANIFEST.json",
)

#: trees whose bytes P9R must not touch.  The original P9 namespace and the
#: closed P8R repair namespace are both in here.
PROTECTED_TREES = (
    "level4/closure_proofs/m_rho_stability_priority3",
    "level4/closure_proofs/location_family",
    "level4/closure_proofs/location_family_track3ab",
    "level4/closure_proofs/m_gt_1",
    "level4/closure_proofs/m_gt_1_priority1",
    "level4/closure_proofs/m_gt_1_track1a",
    "level4/closure_proofs/m_gt_1_track1b",
    "level4/closure_proofs/sr_derivative",
    "level4/closure_proofs/sr_derivative_priority2",
    "level4/closure_proofs/p4_theory_generalization",
    "level4/closure_proofs/p5_nonlinear_dynamics",
    "level4/closure_proofs/p6_safe_rebaselining",
    "level4/closure_proofs/p6_safe_rebaselining_predesign",
    "level4/closure_proofs/p6r_safe_rebaselining_confirmation",
    "level4/closure_proofs/p6r2_literal_closure_repair",
    "level4/closure_proofs/p6r2b_gate9_crn_identity",
    "level4/closure_proofs/p7_statistical_consequences",
    "level4/closure_proofs/p8_model_class_robustness",
    "level4/closure_proofs/p8r_temporal_integrity_repair",
    "level4/closure_proofs/p9_final_synthesis",
    "level4/closure_proofs/novelty_verification",
    "level4/closure_proofs/external_validation_v2",
    "level4/closure_proofs/external_validation_v3",
    "level4/final_level4_closure",
    "level4/final_global_reaudit",
    "level4/re_audit_post_closure",
    "level4/stage_d",
    "level4/src",
    "level4/tests",
    "rebaseguard-lean",
    "rebaseguard-proof",
    "closure",
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files"],
                         capture_output=True, text=True, check=True).stdout
    return [l for l in out.splitlines() if l]


def git_commit() -> str:
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def aggregate(entries: dict[str, str]) -> str:
    h = hashlib.sha256()
    for k in sorted(entries):
        h.update(f"{k}\0{entries[k]}\0".encode())
    return h.hexdigest()


def source_manifest() -> dict:
    files = {}
    for d in SOURCE_DIRS:
        for p in sorted((P9R / d).rglob("*")):
            if not p.is_file() or "__pycache__" in p.parts:
                continue
            files[str(p.relative_to(P9R))] = sha256_file(p)
    return {"schema": "rebaseguard.p9r.source-manifest.v1", "root": REL_P9R,
            "n_files": len(files), "files": files,
            "aggregate_sha256": aggregate(files)}


def protocol_digest() -> dict:
    files, missing = {}, []
    for name in FROZEN_PROSE:
        p = P9R / name
        (files.__setitem__(name, sha256_file(p)) if p.exists()
         else missing.append(name))
    return {"schema": "rebaseguard.p9r.protocol-digest.v1", "root": REL_P9R,
            "frozen_prose": list(FROZEN_PROSE), "missing": missing,
            "files": files, "aggregate_sha256": aggregate(files),
            "note": "TEMPORAL_ANCHOR.md is deliberately excluded: it is the one "
                    "document written twice, because a commit cannot contain "
                    "its own hash."}


def protected_manifest(stage: str) -> dict:
    files, trees = {}, {}
    for rel in tracked_files():
        if rel.startswith(REL_P9R):
            continue
        p = ROOT / rel
        if not p.exists():
            continue
        files[rel] = sha256_file(p)
    for t in PROTECTED_TREES:
        sub = {k: v for k, v in files.items() if k.startswith(t + "/")}
        trees[t] = {"n_files": len(sub), "aggregate_sha256": aggregate(sub)}
    root_status = {k: v for k, v in files.items() if "/" not in k}
    return {"schema": "rebaseguard.p9r.protected-tree-manifest.v1",
            "stage": stage, "excluded_prefix": REL_P9R,
            "git_commit": git_commit(),
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "n_tracked_outside_p9r": len(files), "trees": trees,
            "root_status_files": root_status, "files": files,
            "aggregate_sha256": aggregate(files)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("anchor", "final"), default="anchor")
    args = ap.parse_args()

    sm = source_manifest()
    (P9R / "SOURCE_MANIFEST.json").write_text(json.dumps(sm, indent=1) + "\n")
    pd = protocol_digest()
    (P9R / "PROTOCOL_DIGEST.json").write_text(json.dumps(pd, indent=1) + "\n")
    pm = protected_manifest(args.stage)
    name = ("protected_tree_manifest_pre.json" if args.stage == "anchor"
            else "protected_tree_manifest_final.json")
    out = P9R / "results" / "integrity" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pm, indent=1) + "\n")

    print(f"SOURCE_DIGEST      = {sm['aggregate_sha256']}  ({sm['n_files']} files)")
    print(f"PROTOCOL_DIGEST    = {pd['aggregate_sha256']}  ({len(pd['files'])} files)")
    if pd["missing"]:
        print(f"  MISSING PROSE: {pd['missing']}")
    print(f"PROTECTED_TREE_{args.stage.upper():5s} = {pm['aggregate_sha256']}  "
          f"({pm['n_tracked_outside_p9r']} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
