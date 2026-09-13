"""Campaign specifications. NON-CERTIFYING.

There are exactly two constructors:
  CampaignSpec.production()   every value comes from the frozen, hash-bound PRODUCTION_CHECKPOINT.json; the
                              worker argv is the checkpoint's template (the frozen certifier); nothing is injectable
  CampaignSpec.synthetic(cfg) synthetic workers and a synthetic producer identity, refused inside the production
                              runtime root; a synthetic record can never pass a production seal, or vice versa
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import prod_cells
from prod_common import (AUX5_NS, CHECKPOINT, CHECKPOINT_HASH, GUARD_HOST_FACTS, LINUX, NS, ROOT, Refusal, canonical,
                         host_facts, host_problems, sha256_bytes, sha256_file)

CHECKPOINT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-checkpoint.v1"
PRODUCTION_RUNTIME_ROOT = Path("/root/work/postk1-runs/cusum-aux5-production")
QUALIFICATION_RECORDS = {f"{c}{r}": AUX5_NS / f"evidence/qualification_r1/c{c}_{r}/aux5_CUSUM_{c}_256.json"
                         for c in (318, 323) for r in ("A", "B")}
USEC_PER_CPU_H = 3_600_000_000


def qualification_record_shas() -> dict:
    return {k: sha256_file(p) for k, p in QUALIFICATION_RECORDS.items()}


def load_frozen_checkpoint() -> tuple[dict, str]:
    """The checkpoint, its sha256, and proof that every bound source still has its frozen bytes."""
    try:
        raw = CHECKPOINT.read_bytes()
    except OSError as exc:
        raise Refusal("CHECKPOINT_MISSING", str(exc)) from exc
    sha = sha256_bytes(raw)
    if not CHECKPOINT_HASH.exists() or CHECKPOINT_HASH.read_text().strip() != sha:
        raise Refusal("CHECKPOINT_HASH", "PRODUCTION_CHECKPOINT_HASH does not equal sha256(PRODUCTION_CHECKPOINT.json)")
    cp = json.loads(raw)
    if cp.get("schema") != CHECKPOINT_SCHEMA or cp.get("status") != "FROZEN_PRE_PRODUCTION":
        raise Refusal("CHECKPOINT_SCHEMA", f"{cp.get('schema')!r} / {cp.get('status')!r}")
    drift = sorted(r for r, h in cp["bound_sources"].items() if not (ROOT / r).exists() or sha256_file(ROOT / r) != h)
    if drift:
        raise Refusal("BOUND_SOURCE_DRIFT", f"bound sources changed since the freeze: {drift[:6]}")
    return cp, sha


def manifest_identity(manifest: dict) -> dict:
    """The three producer identity hashes, derived exactly as Aux5 manifest_v3 derives them."""
    mh = sha256_bytes(canonical(manifest))
    rh = sha256_bytes(canonical(manifest["runtime"]))
    ph = sha256_bytes(canonical({"schema": manifest["schema"], "manifest_version": manifest["manifest_version"],
                                 "manifest_hash": mh, "runtime_contract_hash": rh}))
    return {"producer_manifest_hash": mh, "runtime_contract_hash": rh, "producer_identity_hash": ph}


def synthetic_identity(runtime: dict) -> dict:
    return {"producer_manifest_hash": sha256_bytes(b"SYNTHETIC producer manifest, not a producer"),
            "runtime_contract_hash": sha256_bytes(canonical(runtime)),
            "producer_identity_hash": sha256_bytes(b"SYNTHETIC producer identity, not a producer"),
            "implementation_hash_kind": "SYNTHETIC_NOT_A_PRODUCER",
            "producer_manifest_path": "SYNTHETIC", "producer_manifest_schema": "SYNTHETIC",
            "producer_manifest_version": 0, "campaign": "SYNTHETIC_NOT_SCIENCE"}


class CampaignSpec:
    def __init__(self, **fields):
        self.__dict__.update(fields)

    @classmethod
    def production(cls) -> "CampaignSpec":
        cp, sha = load_frozen_checkpoint()
        cells = prod_cells.cusum_cells()
        if prod_cells.geometry_digest(cells) != cp["geometry"]["geometry_digest"]:
            raise Refusal("FROZEN_GEOMETRY_MUTATED", "geometry digest differs from the checkpoint")
        manifest = ROOT / cp["producer"]["manifest_path"]
        if sha256_file(manifest) != cp["producer"]["manifest_file_sha256"]:
            raise Refusal("PRODUCER_IDENTITY", "producer manifest v3 bytes differ from the checkpoint")
        runtime = json.loads(manifest.read_text())["runtime"]
        cap, workers, lc = cp["cost_cap"], cp["workers"], cp["lifecycle"]
        return cls(mode="PRODUCTION", synthetic=False, root=Path(cp["runtime_root"]), checkpoint_sha256=sha,
                   campaign_id=cp["campaign_id"], cells=cells, cell_indices=list(range(prod_cells.N_CELLS)),
                   cap_usec=int(cap["cap_cpu_h"]) * USEC_PER_CPU_H, reservation_usec=int(cap["reservation_usec"]),
                   cores=list(workers["cores"]), poll_s=float(lc["poll_seconds"]),
                   heartbeat_s=float(lc["heartbeat_seconds"]), identity=dict(cp["producer"]["record_identity"]),
                   runtime=runtime, precision_bits=int(cp["precision"]["precision_bits"]),
                   qualification_record_sha256=frozenset(cp["qualification"]["record_file_sha256"].values()),
                   worker_template=list(workers["argv_template"]), worker_cwd=Path(cp["checkout_path"]),
                   worker_env={}, host_expected=dict(cp["host"]["bound_facts"]),
                   accounting_exclusions=cp["cost_cap"]["excluded_from_accounting"], require_keeper=True)

    @classmethod
    def synthetic(cls, cfg: dict) -> "CampaignSpec":
        root = Path(cfg["root"]).resolve()
        if root == PRODUCTION_RUNTIME_ROOT or PRODUCTION_RUNTIME_ROOT in root.parents:
            raise Refusal("SYNTHETIC_PRODUCTION_MIX", "a synthetic campaign may not use the production runtime root")
        if not str(cfg["checkpoint_sha256"]).startswith("SYNTHETIC-"):
            raise Refusal("SYNTHETIC_PRODUCTION_MIX", "synthetic checkpoint labels start with SYNTHETIC-")
        runtime = {"schema": "SYNTHETIC_RUNTIME_NOT_A_CONTRACT", "precision_bits": 256}
        pinned = ["/usr/bin/taskset", "-c", "{core}"] if LINUX else []
        template = pinned + [cfg.get("worker_python", sys.executable), str(NS / "tests/synthetic_worker.py"),
                             "--cell", "{cell}", "--out", "{out}", "--config", str(cfg["config_path"])]
        return cls(mode="SYNTHETIC", synthetic=True, root=root, checkpoint_sha256=cfg["checkpoint_sha256"],
                   campaign_id="SYNTHETIC", cells=prod_cells.cusum_cells(), cell_indices=[int(c) for c in cfg["cells"]],
                   cap_usec=int(cfg["cap_usec"]), reservation_usec=int(cfg["reservation_usec"]),
                   cores=[int(c) for c in cfg["cores"]], poll_s=float(cfg.get("poll_s", 0.05)),
                   heartbeat_s=float(cfg.get("heartbeat_s", 0.5)), identity=synthetic_identity(runtime),
                   runtime=runtime, precision_bits=256,
                   qualification_record_sha256=frozenset(qualification_record_shas().values()),
                   worker_template=template, worker_cwd=NS,
                   worker_env={"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"},
                   host_expected=cfg.get("host_expected"),
                   accounting_exclusions={"synthetic": "non-production acceptance; never a production ledger"},
                   require_keeper=False)

    def worker_argv(self, *, cell: int, core: int, out) -> list:
        subs = {"{cell}": str(cell), "{core}": str(core), "{out}": str(out), "{root}": str(self.worker_cwd)}
        argv = []
        for token in self.worker_template:
            for key, value in subs.items():
                token = token.replace(key, value)
            argv.append(token)
        return argv

    def host_guard(self) -> list[str]:
        if not self.host_expected:
            return []
        return host_problems(self.host_expected, host_facts(with_package=False), GUARD_HOST_FACTS)
