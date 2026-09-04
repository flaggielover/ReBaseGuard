"""P5Y K1 -- freeze manifests from `git ls-tree` at a NAMED ANCHOR COMMIT.

Never hashes the worktree: a dirty tree cannot forge integrity. Every digest
below is the SHA-256 of blob content read out of the object database at the
anchor commit.

DESIGN ARTIFACT. Non-result-bearing.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
NS_REL = str(NS.relative_to(ROOT))

CHECKPOINT_FILES = [
    "CHECKPOINT.md",
    "CHECKPOINT.json",
    "config/budget_ledger.json",
    "config/p1_rule.json",
    "config/complexity_guard.json",
    "config/precision_policy.json",
    "config/production_dag.json",
    "config/stop_rules.json",
    "config/final_verdict_spec.json",
    "manifests/cover_cusum.json",
    "manifests/cover_sr.json",
    "adjudication/ADJUDICATION_CONTRACT.md",
    "code/cpu_model_k1.py",
    "code/build_config.py",
    "code/build_dag.py",
    "code/build_checkpoint_json.py",
    "code/freeze_manifest.py",
    "tests/test_k1_checkpoint_design.py",
]

PROTECTED_DIRS = [
    "level4/closure_proofs/p5_nonlinear_dynamics",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics",
    "level4/closure_proofs/p5y_micropilot_gate1",
    "level4/closure_proofs/p5y_gate2a_sr_precision",
    "level4/closure_proofs/p5y_gate2b_sr_cover",
    "level4/closure_proofs/p5y_gate2c_m2_assembly",
    "level4/closure_proofs/p5y_gate2cbis_m2_assembly_b",
    "level4/closure_proofs/p5y_gate2d_sr_realcandidate",
    "level4/closure_proofs/p5y_gate2e_sr_metric",
    "level4/closure_proofs/p5y_gate2f_sr_metric_b",
]

PROTECTED_FILES = [
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/FROZEN_SCOPE.md",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/FROZEN_THEOREM.md",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/PROOF.md",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/FROZEN_GATES.md",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/STOP_GATE.md",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/DEFECT_REGISTER.md",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/"
    "certified_method_repair_ra/ra_certifier.py",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/"
    "compute_optimization_r1/drift_minorant.py",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/"
    "compute_optimization_r1/R1_COST_REPROJECTION.md",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/"
    "compute_optimization_r3_sr_symbolic/sr_local.py",
    "level4/closure_proofs/p5_nonlinear_dynamics/THEOREM.md",
    "level4/closure_proofs/p5_nonlinear_dynamics/LIMITATIONS.md",
    "level4/closure_proofs/sr_derivative/results/sr_monotone_contraction.json",
    "level4/closure_proofs/p5y_gate2b_sr_cover/results/sr_cover.json",
    "level4/closure_proofs/p5y_gate2f_sr_metric_b/results/gate2f_adjudication.json",
]


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=True).stdout


def blob_sha256(anchor: str, path: str) -> str | None:
    try:
        raw = subprocess.run(["git", "-C", str(ROOT), "show", f"{anchor}:{path}"],
                             capture_output=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None
    return hashlib.sha256(raw).hexdigest()


def tree_sha(anchor: str, path: str) -> str | None:
    out = git("ls-tree", anchor, path + "/")
    if not out.strip():
        return None
    return out.split()[2]


def main() -> int:
    anchor = sys.argv[1] if len(sys.argv) > 1 else git("rev-parse", "HEAD").strip()
    anchor = git("rev-parse", anchor).strip()

    src = {}
    missing = []
    for rel in CHECKPOINT_FILES:
        d = blob_sha256(anchor, f"{NS_REL}/{rel}")
        if d is None:
            missing.append(rel)
        else:
            src[rel] = d
    if missing:
        print("MISSING at anchor:", missing, file=sys.stderr)
        return 2

    agg = hashlib.sha256()
    for rel in CHECKPOINT_FILES:
        agg.update(rel.encode())
        agg.update(b"\0")
        agg.update(src[rel].encode())
        agg.update(b"\n")
    checkpoint_hash = agg.hexdigest()

    prot = {
        "schema": "rebaseguard.p5y.k1.protected.v1",
        "binding": True,
        "anchor_commit": anchor,
        "hash_source": "git ls-tree / git show at the anchor commit; the worktree "
                       "is never read",
        "immutable_for_campaign_duration": True,
        "writable_paths": [f"{NS_REL}/results", f"{NS_REL}/certificates",
                           f"{NS_REL}/logs"],
        "directory_tree_sha1": {p: tree_sha(anchor, p) for p in PROTECTED_DIRS},
        "file_sha256": {p: blob_sha256(anchor, p) for p in PROTECTED_FILES},
    }
    absent = [k for k, v in prot["file_sha256"].items() if v is None]
    prot["absent_at_anchor"] = absent

    manifest = {
        "schema": "rebaseguard.p5y.k1.sourcemanifest.v1",
        "binding": True,
        "anchor_commit": anchor,
        "namespace": NS_REL,
        "hash_source": "git ls-tree at the anchor commit (never the worktree)",
        "file_sha256": src,
        "aggregate_rule": "sha256 over sorted-by-declaration 'path\\0digest\\n'",
        "CHECKPOINT_HASH": checkpoint_hash,
    }

    (NS / "manifests" / "source_manifest.json").write_text(
        json.dumps(manifest, indent=1) + "\n")
    (NS / "manifests" / "protected_inputs.json").write_text(
        json.dumps(prot, indent=1) + "\n")
    (NS / "manifests" / "CHECKPOINT_HASH.json").write_text(json.dumps({
        "schema": "rebaseguard.p5y.k1.hash.v1",
        "anchor_commit": anchor,
        "CHECKPOINT_HASH": checkpoint_hash,
        "n_files": len(CHECKPOINT_FILES),
        "P5Y_K1_CHECKPOINT_STATUS": "FROZEN",
        "P5Y_PRODUCTION_RUN": "NO",
    }, indent=1) + "\n")

    print("anchor commit    =", anchor)
    print("files hashed     =", len(src))
    print("absent protected =", absent or "none")
    print("CHECKPOINT_HASH  =", checkpoint_hash)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
