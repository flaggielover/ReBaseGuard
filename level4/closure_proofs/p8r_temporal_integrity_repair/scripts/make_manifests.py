"""Build the three P8R integrity manifests.

``SOURCE_MANIFEST.json``
    SHA-256 of every file under ``src/``, ``experiments/``, ``scripts/`` and
    ``tests/`` -- the executable surface of the campaign.

``PROTOCOL_DIGEST.json``
    SHA-256 of every frozen prose artifact (protocol, gates, plans, rationale,
    definition audit, temporal anchor).  P8's provenance record hashed *neither*
    its protocol nor its gates, which is precisely why its ``G14`` claim could
    not be checked; P8R hashes both.

``results/integrity/protected_tree_manifest.json``
    SHA-256 of every tracked file outside the P8R namespace, plus a per-tree
    aggregate digest for each protected tree.  Recomputed at the anchor and at
    the end; ``I11`` requires them to be identical apart from explicitly
    authorised root status files.

Usage:  make_manifests.py [--stage anchor|final]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

P8R = Path(__file__).resolve().parents[1]
ROOT = P8R.parents[2]
REL_P8R = "level4/closure_proofs/p8r_temporal_integrity_repair"

SOURCE_DIRS = ("src", "experiments", "scripts", "tests")

#: prose artifacts frozen at the temporal anchor.  Every one of these must exist
#: in the anchor commit and must be byte-identical in the final commit.
FROZEN_PROSE = (
    "README.md",
    "DEFINITION_AUDIT.md",
    "REPAIR_RATIONALE.md",
    "FROZEN_PROTOCOL.md",
    "FROZEN_GATES.md",
    "CALIBRATION_PLAN.md",
    "RNG_ADDRESS_PLAN.md",
    "PRODUCTION_PLAN.md",
    "STATISTICAL_ANALYSIS_PLAN.md",
    "COMMAND_MANIFEST.json",
)

#: the trees whose bytes P8R must not touch.  ``I11`` hashes each one whole.
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
    "level4/closure_proofs/p9_final_synthesis",
    "level4/stage_d",
    "level4/src",
    "level4/tests",
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
                          capture_output=True, text=True,
                          check=True).stdout.strip()


def aggregate(entries: dict[str, str]) -> str:
    h = hashlib.sha256()
    for k in sorted(entries):
        h.update(f"{k}\0{entries[k]}\0".encode())
    return h.hexdigest()


def source_manifest() -> dict:
    files = {}
    for d in SOURCE_DIRS:
        for p in sorted((P8R / d).rglob("*")):
            if not p.is_file() or "__pycache__" in p.parts:
                continue
            files[str(p.relative_to(P8R))] = sha256_file(p)
    return {"schema": "rebaseguard.p8r.source-manifest.v1",
            "root": REL_P8R, "n_files": len(files),
            "files": files, "aggregate_sha256": aggregate(files)}


def protocol_digest() -> dict:
    files, missing = {}, []
    for name in FROZEN_PROSE:
        p = P8R / name
        if p.exists():
            files[name] = sha256_file(p)
        else:
            missing.append(name)
    return {"schema": "rebaseguard.p8r.protocol-digest.v1",
            "root": REL_P8R, "frozen_prose": list(FROZEN_PROSE),
            "missing": missing, "files": files,
            "aggregate_sha256": aggregate(files)}


def protected_manifest() -> dict:
    files, trees = {}, {}
    for rel in tracked_files():
        if rel.startswith(REL_P8R):
            continue
        p = ROOT / rel
        if not p.exists():
            continue
        files[rel] = sha256_file(p)
    for t in PROTECTED_TREES:
        sub = {k: v for k, v in files.items() if k.startswith(t + "/")}
        trees[t] = {"n_files": len(sub), "aggregate_sha256": aggregate(sub)}
    root_status = {k: v for k, v in files.items() if "/" not in k}
    return {"schema": "rebaseguard.p8r.protected-tree-manifest.v1",
            "excluded_prefix": REL_P8R,
            "n_tracked_outside_p8r": len(files),
            "trees": trees, "root_status_files": root_status,
            "files": files, "aggregate_sha256": aggregate(files)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="anchor",
                    choices=("anchor", "final"))
    a = ap.parse_args()
    stamp = {"stage": a.stage, "git_commit": git_commit(),
             "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                            time.gmtime())}
    if a.stage == "anchor":
        for name, doc in (("SOURCE_MANIFEST.json", source_manifest()),
                          ("PROTOCOL_DIGEST.json", protocol_digest())):
            doc.update(stamp)
            (P8R / name).write_text(json.dumps(doc, indent=1) + "\n")
            print(f"{name:24s} aggregate={doc['aggregate_sha256']} "
                  f"n={doc.get('n_files', len(doc.get('files', {})))}")
        d = P8R / "results" / "integrity"
        d.mkdir(parents=True, exist_ok=True)
        doc = protected_manifest()
        doc.update(stamp)
        (d / "protected_tree_manifest_pre.json").write_text(
            json.dumps(doc, indent=1) + "\n")
        print(f"protected_tree(pre)      aggregate={doc['aggregate_sha256']} "
              f"n={doc['n_tracked_outside_p8r']}")
    else:
        d = P8R / "results" / "integrity"
        doc = protected_manifest()
        doc.update(stamp)
        (d / "protected_tree_manifest_post.json").write_text(
            json.dumps(doc, indent=1) + "\n")
        print(f"protected_tree(post)     aggregate={doc['aggregate_sha256']} "
              f"n={doc['n_tracked_outside_p8r']}")


if __name__ == "__main__":
    main()
