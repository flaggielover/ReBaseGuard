"""Specifications of the provenance successor. NON-CERTIFYING.

  production_spec()   every value from the frozen, hash-bound PROVENANCE_CHECKPOINT.json
  synthetic_spec(cfg) the predecessor synthetic spec with this namespace's synthetic worker (which emits the three
                      certifier-constant flags); refused inside either production runtime root
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import prov_schema as S
import prod_cells
from prod_common import LINUX, ROOT, Refusal, sha256_bytes, sha256_file
from prod_spec import PRODUCTION_RUNTIME_ROOT as PREDECESSOR_RUNTIME_ROOT
from prod_spec import USEC_PER_CPU_H, CampaignSpec

CHECKPOINT = S.NS / "config/PROVENANCE_CHECKPOINT.json"
CHECKPOINT_HASH = S.NS / "config/PROVENANCE_CHECKPOINT_HASH"
FREEZE_RECORD = S.NS / "config/FREEZE_RECORD.json"
AUTHORIZATION = S.NS / "config/RUN_AUTHORIZATION.json"
AUTHORIZATION_HASH = S.NS / "config/RUN_AUTHORIZATION_HASH"
COUNTERSIGNATURE = S.NS / "config/COUNTERSIGNATURE.json"
PRODUCTION_RUNTIME_ROOT = Path("/root/work/postk1-runs/cusum-aux5-production-prov-r1")


def load_checkpoint() -> tuple[dict, str]:
    try:
        raw = CHECKPOINT.read_bytes()
    except OSError as exc:
        raise Refusal("CHECKPOINT_MISSING", str(exc)) from exc
    sha = sha256_bytes(raw)
    if not CHECKPOINT_HASH.exists() or CHECKPOINT_HASH.read_text().strip() != sha:
        raise Refusal("CHECKPOINT_HASH", "PROVENANCE_CHECKPOINT_HASH does not equal the checkpoint sha256")
    cp = json.loads(raw)
    if cp.get("schema") != S.CHECKPOINT_SCHEMA or cp.get("status") != "FROZEN_PRE_PRODUCTION":
        raise Refusal("CHECKPOINT_SCHEMA", f"{cp.get('schema')!r} / {cp.get('status')!r}")
    drift = sorted(r for r, h in cp["bound_sources"].items() if not (ROOT / r).exists() or sha256_file(ROOT / r) != h)
    if drift:
        raise Refusal("BOUND_SOURCE_DRIFT", f"bound sources changed since the freeze: {drift[:6]}")
    return cp, sha


def production_spec() -> tuple:
    cp, sha = load_checkpoint()
    cells = prod_cells.cusum_cells()
    if prod_cells.geometry_digest(cells) != cp["geometry"]["geometry_digest"]:
        raise Refusal("FROZEN_GEOMETRY_MUTATED", "geometry digest differs from the checkpoint")
    manifest = ROOT / cp["producer"]["manifest_path"]
    if sha256_file(manifest) != cp["producer"]["manifest_file_sha256"]:
        raise Refusal("PRODUCER_IDENTITY", "producer manifest v3 bytes differ from the checkpoint")
    runtime = json.loads(manifest.read_text())["runtime"]
    cap, workers, lc = cp["cost_cap"], cp["workers"], cp["lifecycle"]
    spec = CampaignSpec(mode="PRODUCTION", synthetic=False, root=Path(cp["runtime_root"]), checkpoint_sha256=sha,
                        campaign_id=cp["campaign_id"], cells=cells, cell_indices=list(range(prod_cells.N_CELLS)),
                        cap_usec=int(cap["cap_cpu_h"]) * USEC_PER_CPU_H, reservation_usec=int(cap["reservation_usec"]),
                        cores=list(workers["cores"]), poll_s=float(lc["poll_seconds"]),
                        heartbeat_s=float(lc["heartbeat_seconds"]), identity=dict(cp["producer"]["record_identity"]),
                        runtime=runtime, precision_bits=int(cp["precision"]["precision_bits"]),
                        qualification_record_sha256=frozenset(cp["qualification"]["record_file_sha256"].values()),
                        worker_template=list(workers["argv_template"]), worker_cwd=Path(cp["checkout_path"]),
                        worker_env={}, host_expected=dict(cp["host"]["bound_facts"]),
                        accounting_exclusions=cp["cost_cap"]["excluded_from_accounting"], require_keeper=True)
    return spec, cp


def synthetic_spec(cfg: dict):
    root = Path(cfg["root"]).resolve()
    for prod in (PRODUCTION_RUNTIME_ROOT, PREDECESSOR_RUNTIME_ROOT):
        if root == prod or prod in root.parents:
            raise Refusal("SYNTHETIC_PRODUCTION_MIX", "a synthetic campaign may not use a production runtime root")
    spec = CampaignSpec.synthetic(cfg)
    pinned = ["/usr/bin/taskset", "-c", "{core}"] if LINUX else []
    spec.worker_template = pinned + [cfg.get("worker_python", sys.executable), str(S.NS / "tests/prov_synthetic_worker.py"),
                                     "--cell", "{cell}", "--out", "{out}", "--config", str(cfg["config_path"])]
    return spec
