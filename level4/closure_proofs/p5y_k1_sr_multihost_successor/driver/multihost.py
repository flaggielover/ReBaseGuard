"""Additive multi-host extension of the SR driver-bound successor.

This module adds ONLY host-role resolution, static shard ownership, per-host and
global ledger assembly, and the layered producer-commit binding. It performs no
scientific computation, defines no new obligation, changes no threshold, and
cannot emit a result-bearing SR cell.

Every gate FAILS CLOSED: it raises MultiHostRefusal unless it can positively
verify its property.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]

GLOBAL_CPU_CAP = 4500.0          # ONE global campaign cap, never per host
OVERHEAD_FACTOR = 1.15
CUSUM_CPU_H = 206.086
TOTAL_CELLS = 316
TOTAL_SR_OBLIGATIONS = 8849

ROLES = {
    "AWS": {
        "sys_vendor": "Amazon EC2",
        "runtime_contract_hash": "d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191",
        "workers": 16,
        "core_assignment": list(range(16)),
        "per_cell_reservation_cpu_h": 11.474662,
    },
    "VULTR": {
        "sys_vendor": "Vultr",
        "runtime_contract_hash": "c7f9fc671664a1bcfef6d2d3d93d6cc865a2a241a869f2e93f94e6e00b6489d9",
        "workers": 4,
        "core_assignment": [0, 2, 4, 6],
        "per_cell_reservation_cpu_h": 10.217741105316279,
    },
}

CELL_RECORD_REQUIRED_FIELDS = (
    "cell_id", "role", "producer_commit", "checkpoint_sha256",
    "runtime_contract_hash", "scientific_content_hash", "cpu_seconds",
    "obligations_completed", "complete",
)


class MultiHostRefusal(RuntimeError):
    """A multi-host gate refused to admit the run."""


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True)).encode("ascii")


def sha256_obj(obj) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


# ------------------------------------------------------------------ host role
def detect_role(sys_vendor: str) -> str:
    """Resolve the host role from the DMI vendor string. Unknown vendor refuses."""
    for role, spec in ROLES.items():
        if spec["sys_vendor"] == sys_vendor:
            return role
    raise MultiHostRefusal(f"unknown host: sys_vendor {sys_vendor!r} maps to no role")


def gate_role(declared_role: str, sys_vendor: str) -> str:
    actual = detect_role(sys_vendor)
    if declared_role != actual:
        raise MultiHostRefusal(
            f"host role mismatch: declared {declared_role} but sys_vendor "
            f"{sys_vendor!r} resolves to {actual}")
    return actual


def gate_runtime_hash(role: str, live_runtime_hash: str) -> str:
    want = ROLES[role]["runtime_contract_hash"]
    if live_runtime_hash != want:
        raise MultiHostRefusal(
            f"{role} runtime contract {live_runtime_hash} != required {want}")
    return live_runtime_hash


def gate_workers(role: str, workers: int, core_assignment: list[int],
                 thread_siblings: dict[int, list[int]]) -> dict:
    """One worker per PHYSICAL core. SMT siblings are never admissible."""
    spec = ROLES[role]
    if workers != spec["workers"]:
        raise MultiHostRefusal(
            f"{role} worker count {workers} != qualified {spec['workers']}")
    if core_assignment != spec["core_assignment"]:
        raise MultiHostRefusal(
            f"{role} core assignment {core_assignment} != frozen {spec['core_assignment']}")
    if len(set(core_assignment)) != len(core_assignment):
        raise MultiHostRefusal("duplicate core in assignment")
    seen_physical = set()
    for c in core_assignment:
        sibs = tuple(sorted(thread_siblings[c]))
        if sibs in seen_physical:
            raise MultiHostRefusal(
                f"SMT misuse: cpu {c} shares a physical core with an already "
                f"assigned cpu (siblings {list(sibs)})")
        seen_physical.add(sibs)
    return {"role": role, "workers": workers, "core_assignment": core_assignment,
            "smt_used": False}


# --------------------------------------------------------------- shard manifest
def load_shard_manifest(path, expect_sha256: str) -> dict:
    raw = Path(path).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != expect_sha256:
        raise MultiHostRefusal(
            f"shard manifest sha256 {got} != authorised {expect_sha256}")
    return json.loads(raw)


def gate_shards(manifest: dict) -> dict:
    if manifest.get("cells_total") != TOTAL_CELLS:
        raise MultiHostRefusal(
            f"shard manifest cells_total {manifest.get('cells_total')} != {TOTAL_CELLS}")
    owners: dict[int, str] = {}
    for role in ("AWS", "VULTR"):
        if role not in manifest:
            raise MultiHostRefusal(f"shard manifest missing role {role}")
        cells = manifest[role]["cells"]
        if len(set(cells)) != len(cells):
            raise MultiHostRefusal(f"duplicate cell ids within {role} shard")
        for c in cells:
            if c in owners:
                raise MultiHostRefusal(
                    f"overlapping shards: cell {c} owned by both {owners[c]} and {role}")
            owners[c] = role
    missing = set(range(TOTAL_CELLS)) - set(owners)
    if missing:
        raise MultiHostRefusal(f"missing cells: {sorted(missing)[:8]} ...")
    extra = set(owners) - set(range(TOTAL_CELLS))
    if extra:
        raise MultiHostRefusal(f"cells outside the frozen cover: {sorted(extra)[:8]}")
    return owners


def gate_cell_ownership(role: str, cell_id: int, owners: dict[int, str]) -> None:
    if cell_id not in owners:
        raise MultiHostRefusal(f"cell {cell_id} is not in the frozen cover")
    if owners[cell_id] != role:
        raise MultiHostRefusal(
            f"foreign-host cell: {role} may not execute cell {cell_id}, "
            f"which is owned by {owners[cell_id]}")


# ---------------------------------------------------- producer-commit binding
def gate_producer_commit(launch_manifest: dict, actual_head: str,
                         checkpoint_sha256: str, shard_manifest_sha256: str) -> str:
    """Layered authorisation: checkpoint -> immutable producer commit ->
    result-free launch manifest -> additive tag. Production is refused unless the
    ACTUAL checkout equals the authorised producer commit."""
    if launch_manifest.get("result_bearing") is not False:
        raise MultiHostRefusal("launch manifest must be result-free")
    for k in ("producer_commit", "multihost_tag", "checkpoint_sha256",
              "shard_manifest_sha256", "runtime_contract_hashes"):
        if not launch_manifest.get(k):
            raise MultiHostRefusal(f"launch manifest missing {k}")
    pc = launch_manifest["producer_commit"]
    if not isinstance(pc, str) or len(pc) != 40:
        raise MultiHostRefusal(f"producer_commit {pc!r} is not a full commit id")
    if launch_manifest["checkpoint_sha256"] != checkpoint_sha256:
        raise MultiHostRefusal("launch manifest checkpoint hash does not bind the checkpoint")
    if launch_manifest["shard_manifest_sha256"] != shard_manifest_sha256:
        raise MultiHostRefusal("launch manifest does not bind the authorised shard manifest")
    for role in ("AWS", "VULTR"):
        if launch_manifest["runtime_contract_hashes"].get(role) != \
                ROLES[role]["runtime_contract_hash"]:
            raise MultiHostRefusal(f"launch manifest {role} runtime hash is not the qualified one")
    if actual_head != pc:
        raise MultiHostRefusal(
            f"checkout HEAD {actual_head} != authorised producer_commit {pc}; "
            "production refused")
    return pc


# ------------------------------------------------------------------- ledgers
def validate_record(rec: dict, role: str, owners: dict[int, str],
                    producer_commit: str, checkpoint_sha256: str) -> None:
    for f in CELL_RECORD_REQUIRED_FIELDS:
        if f not in rec:
            raise MultiHostRefusal(f"torn cell record: missing field {f}")
    if rec["complete"] is not True:
        raise MultiHostRefusal(
            f"torn cell {rec['cell_id']}: partial work never counts")
    if rec["role"] != role:
        raise MultiHostRefusal(
            f"record for cell {rec['cell_id']} claims role {rec['role']} in the {role} ledger")
    gate_cell_ownership(role, rec["cell_id"], owners)
    if rec["producer_commit"] != producer_commit:
        raise MultiHostRefusal(
            f"cell {rec['cell_id']} produced by {rec['producer_commit']} != {producer_commit}")
    if rec["checkpoint_sha256"] != checkpoint_sha256:
        raise MultiHostRefusal(f"cell {rec['cell_id']} bound to a foreign checkpoint")
    if rec["runtime_contract_hash"] != ROLES[role]["runtime_contract_hash"]:
        raise MultiHostRefusal(
            f"cell {rec['cell_id']} carries a runtime hash that is not {role}'s qualified one")
    if not isinstance(rec["cpu_seconds"], (int, float)) or rec["cpu_seconds"] < 0:
        raise MultiHostRefusal(f"cell {rec['cell_id']} has a non-physical cpu_seconds")


def per_host_cpu_h(records: list[dict]) -> float:
    return sum(r["cpu_seconds"] for r in records) / 3600.0


def gate_global_cap(cpu_h_by_role: dict[str, float],
                    governed_overhead_cpu_h: float = CUSUM_CPU_H) -> dict:
    """ONE global cap. Never interpreted as 4500 per host."""
    sr = sum(cpu_h_by_role.values())
    charged = OVERHEAD_FACTOR * (sr + governed_overhead_cpu_h)
    if charged > GLOBAL_CPU_CAP:
        raise MultiHostRefusal(
            f"global cap exceeded: charged {charged:.3f} CPU-h > {GLOBAL_CPU_CAP} "
            f"(per-host {cpu_h_by_role})")
    return {"sr_cpu_h": sr, "governed_overhead_cpu_h": governed_overhead_cpu_h,
            "charged_cpu_h": charged, "cap": GLOBAL_CPU_CAP,
            "headroom_cpu_h": GLOBAL_CPU_CAP - charged}


def gate_per_host_reservation(role: str, records: list[dict]) -> float:
    """A host may not consume more than its own shard's reservation."""
    allowed = ROLES[role]["per_cell_reservation_cpu_h"] * len(records)
    used = per_host_cpu_h(records)
    if used > allowed:
        raise MultiHostRefusal(
            f"{role} consumed {used:.3f} CPU-h > its shard reservation {allowed:.3f}")
    return used


def assemble_global_ledger(host_ledgers: dict[str, list[dict]], owners: dict[int, str],
                           producer_commit: str, checkpoint_sha256: str) -> dict:
    seen: dict[int, str] = {}
    cpu_h_by_role: dict[str, float] = {}
    obligations = 0
    for role, records in host_ledgers.items():
        for rec in records:
            validate_record(rec, role, owners, producer_commit, checkpoint_sha256)
            cid = rec["cell_id"]
            if cid in seen:
                raise MultiHostRefusal(
                    f"cross-host recomputation: cell {cid} appears in both "
                    f"{seen[cid]} and {role} ledgers")
            seen[cid] = role
            obligations += rec["obligations_completed"]
        cpu_h_by_role[role] = gate_per_host_reservation(role, records)
    missing = set(range(TOTAL_CELLS)) - set(seen)
    if missing:
        raise MultiHostRefusal(f"aggregate ledger incomplete: {len(missing)} cells missing")
    if obligations != TOTAL_SR_OBLIGATIONS:
        raise MultiHostRefusal(
            f"obligation conservation violated: {obligations} != {TOTAL_SR_OBLIGATIONS}")
    cap = gate_global_cap(cpu_h_by_role)
    body = {"cells": sorted(seen), "owners": {str(k): v for k, v in sorted(seen.items())},
            "producer_commit": producer_commit, "checkpoint_sha256": checkpoint_sha256,
            "obligations_completed": obligations}
    return {"cells_completed": len(seen), "obligations_completed": obligations,
            "cpu_h_by_role": cpu_h_by_role, "cap": cap,
            "aggregate_ledger_sha256": sha256_obj(body)}


def verify_aggregate_ledger(ledger: dict, expect_sha256: str) -> None:
    if ledger.get("aggregate_ledger_sha256") != expect_sha256:
        raise MultiHostRefusal(
            f"corrupted aggregate ledger: {ledger.get('aggregate_ledger_sha256')} "
            f"!= {expect_sha256}")
