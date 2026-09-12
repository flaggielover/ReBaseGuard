"""PS1 portable checkpoint: schema, build, verify, export, import.

An immutable, location-independent statement of campaign progress. It contains NO mutable
process state -- no pid, no flock, no systemd invocation id, no open reservation, no cache,
no temp writer state -- so it can be moved to any qualified host and resumed there.

Anchored on the Phase A result: a finalized cell's scientific evidence hashes identically
from any directory, so FINALIZED cells are portable facts, not host-local state.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tarfile
import time
from pathlib import Path

SCHEMA = "rebaseguard.p5y.k1.ps1.portable-checkpoint.v1"
BUNDLE_SCHEMA = "rebaseguard.p5y.k1.ps1.portable-bundle.v1"
TOTAL_CELLS = 369

# ---------------------------------------------------------------- retry taxonomy (Phase J)
SCIENTIFIC_FAILURE = "SCIENTIFIC_FAILURE"      # never retried; halts (inherited, unchanged)
INFRASTRUCTURE_TEAR = "INFRASTRUCTURE_TEAR"    # bounded retry in THIS generation
OPERATOR_EMERGENCY_STOP = "OPERATOR_EMERGENCY_STOP"   # counts as a tear for in-flight cells
GRACEFUL_DRAIN = "GRACEFUL_DRAIN"              # NOT a tear; cells reached a safe boundary

# A cell drained at its boundary is finalized; a cell drained before it started is pending.
# Neither increments torn_attempts. Only these two increment it:
TEARING_KINDS = (INFRASTRUCTURE_TEAR, OPERATOR_EMERGENCY_STOP)


def canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def sha256_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _content_hash(ck: dict) -> str:
    body = {k: v for k, v in ck.items() if k != "checkpoint_content_sha256"}
    return hashlib.sha256(canonical(body)).hexdigest()


def build(*, generation, predecessor, identities, finalized, pending, torn_lineage,
          accounting, runs, hosts, evidence_root, ledger_continuity_sha256) -> dict:
    """finalized: {cell_id: {scientific_content_hash, evidence:{name:{sha256,bytes}}, host, run_id, cpu_seconds}}"""
    fin = {str(k): v for k, v in finalized.items()}
    pend = sorted(int(c) for c in pending)
    fset, pset = {int(k) for k in fin}, set(pend)
    if fset & pset:
        raise ValueError(f"FINALIZED and PENDING overlap: {sorted(fset & pset)}")
    if fset | pset != set(range(TOTAL_CELLS)):
        missing = sorted(set(range(TOTAL_CELLS)) - (fset | pset))
        extra = sorted((fset | pset) - set(range(TOTAL_CELLS)))
        raise ValueError(f"FINALIZED u PENDING != PS1 domain; missing={missing[:8]} extra={extra[:8]}")
    ck = {
        "schema": SCHEMA,
        "checkpoint_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "campaign": "p5y_k1_ps1_production",
        "execution_generation": generation,
        "predecessor": predecessor,
        "identities": identities,
        "finalized_cells": sorted(fset),
        "pending_cells": pend,
        "finalized": fin,
        "torn_attempt_lineage": torn_lineage,
        "accounting": accounting,
        "runs": runs,
        "hosts": hosts,
        "evidence_manifest": {
            "evidence_root_note": "paths are advisory; every cell is verified by hash, not location",
            "root_at_build": str(evidence_root),
            "files": sum(len(v.get("evidence", {})) for v in fin.values()),
        },
        "ledger_continuity_sha256": ledger_continuity_sha256,
        "invariants": {
            "finalized_union_pending_equals_domain": True,
            "finalized_intersect_pending_empty": True,
            "total_cells": TOTAL_CELLS,
            "no_mutable_process_state": True,
        },
    }
    ck["checkpoint_content_sha256"] = _content_hash(ck)
    return ck


def verify(ck: dict, *, evidence_root=None, require_identities=None) -> dict:
    """Fail-closed verification. Returns a report; raises on any violation."""
    rep = {}
    if ck.get("schema") != SCHEMA:
        raise ValueError(f"schema mismatch: {ck.get('schema')}")
    got = _content_hash(ck)
    if got != ck.get("checkpoint_content_sha256"):
        raise ValueError(f"checkpoint content hash mismatch: {got} != {ck.get('checkpoint_content_sha256')}")
    rep["checkpoint_content_sha256"] = got

    fin = {int(k) for k in ck["finalized"]}
    pend = set(ck["pending_cells"])
    if fin & pend:
        raise ValueError(f"FINALIZED n PENDING non-empty: {sorted(fin & pend)}")
    if fin | pend != set(range(TOTAL_CELLS)):
        raise ValueError("FINALIZED u PENDING != PS1 369-cell domain")
    if sorted(fin) != ck["finalized_cells"]:
        raise ValueError("finalized_cells index disagrees with finalized map")
    rep["domain_partition"] = f"{len(fin)} finalized + {len(pend)} pending = {TOTAL_CELLS}"

    if require_identities:
        for k, want in require_identities.items():
            got_i = ck["identities"].get(k)
            if got_i != want:
                raise ValueError(f"identity drift {k}: {got_i} != {want}")
        rep["identities_verified"] = sorted(require_identities)

    if evidence_root is not None:
        root = Path(evidence_root)
        bad = []
        for cell, meta in sorted(ck["finalized"].items(), key=lambda kv: int(kv[0])):
            for name, e in meta["evidence"].items():
                p = root / f"cell_{int(cell):04d}" / name
                if not p.exists():
                    bad.append(f"missing {p}")
                elif sha256_file(p) != e["sha256"]:
                    bad.append(f"hash mismatch {p}")
        if bad:
            raise ValueError(f"finalized evidence verification failed: {bad[:5]} ({len(bad)} total)")
        rep["evidence_verified_cells"] = len(ck["finalized"])

    acc = ck["accounting"]
    if acc["historical_cpu_h"] < 92.32 - 1e-9:
        raise ValueError(f"historical CPU accounting regressed: {acc['historical_cpu_h']} < 92.32")
    rep["historical_cpu_h"] = acc["historical_cpu_h"]
    rep["cumulative_cpu_h"] = acc["cumulative_cpu_h"]
    return rep


def export_bundle(ck: dict, *, evidence_root, out_dir, include_archival=False) -> dict:
    """Deterministic portable bundle: checkpoint + finalized evidence + manifests only."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stage = out / "bundle"
    if stage.exists():
        shutil.rmtree(stage)
    (stage / "evidence").mkdir(parents=True)

    (stage / "checkpoint.json").write_bytes(canonical(ck))
    root = Path(evidence_root)
    manifest = []
    for cell, meta in sorted(ck["finalized"].items(), key=lambda kv: int(kv[0])):
        cd = f"cell_{int(cell):04d}"
        (stage / "evidence" / cd).mkdir(parents=True, exist_ok=True)
        for name, e in sorted(meta["evidence"].items()):
            src = root / cd / name
            dst = stage / "evidence" / cd / name
            shutil.copy2(src, dst)
            got = sha256_file(dst)
            if got != e["sha256"]:
                raise ValueError(f"export hash mismatch {src}: {got} != {e['sha256']}")
            manifest.append((f"evidence/{cd}/{name}", got, dst.stat().st_size))
    manifest.append(("checkpoint.json", sha256_file(stage / "checkpoint.json"),
                     (stage / "checkpoint.json").stat().st_size))

    sums = "".join(f"{h}  {p}\n" for p, h, _ in sorted(manifest))
    (stage / "SHA256SUMS").write_text(sums)
    mf = {"schema": BUNDLE_SCHEMA,
          "checkpoint_content_sha256": ck["checkpoint_content_sha256"],
          "execution_generation": ck["execution_generation"],
          "finalized_cells": ck["finalized_cells"],
          "pending_cells_count": len(ck["pending_cells"]),
          "files": [{"path": p, "sha256": h, "bytes": n} for p, h, n in sorted(manifest)],
          "excluded": ["caches", "scratch", "torn/archival patch evidence", "locks",
                       "journals", "process state", "temporary files"],
          "includes_archival": bool(include_archival)}
    (stage / "MANIFEST.json").write_bytes(canonical(mf))

    tar = out / f"ps1-{ck['execution_generation']['generation_id']}.tar"
    with tarfile.open(tar, "w", format=tarfile.GNU_FORMAT) as tf:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                ti = tf.gettarinfo(str(p), arcname=str(p.relative_to(stage)))
                ti.mtime, ti.uid, ti.gid, ti.uname, ti.gname, ti.mode = 0, 0, 0, "", "", 0o644
                with open(p, "rb") as fh:
                    tf.addfile(ti, fh)
    return {"bundle_dir": str(stage), "tar": str(tar), "tar_sha256": sha256_file(tar),
            "bundle_bytes": tar.stat().st_size, "files": len(manifest),
            "manifest_sha256": sha256_file(stage / "MANIFEST.json"),
            "checkpoint_content_sha256": ck["checkpoint_content_sha256"]}


def verify_bundle(bundle_dir) -> dict:
    b = Path(bundle_dir)
    mf = json.loads((b / "MANIFEST.json").read_text())
    if mf.get("schema") != BUNDLE_SCHEMA:
        raise ValueError("bundle schema mismatch")
    bad = []
    for f in mf["files"]:
        p = b / f["path"]
        if not p.exists():
            bad.append(f"missing {f['path']}")
        elif sha256_file(p) != f["sha256"]:
            bad.append(f"hash mismatch {f['path']}")
    if bad:
        raise ValueError(f"bundle verification failed: {bad[:5]}")
    ck = json.loads((b / "checkpoint.json").read_text())
    if ck["checkpoint_content_sha256"] != mf["checkpoint_content_sha256"]:
        raise ValueError("bundle manifest/checkpoint hash disagreement")
    verify(ck, evidence_root=b / "evidence")
    return {"files_verified": len(mf["files"]), "checkpoint": ck["checkpoint_content_sha256"],
            "finalized": len(ck["finalized_cells"]), "pending": len(ck["pending_cells"])}
