"""Additive multi-host extension of the SR driver-bound successor.

This module adds ONLY host-role resolution, static shard ownership, per-host and
global ledger assembly, and the layered producer-commit binding. It performs no
scientific computation, defines no new obligation, changes no threshold, and
cannot emit a result-bearing SR cell.

Every gate FAILS CLOSED: it raises MultiHostRefusal unless it can positively
verify its property.

CAP REPAIR (governance only, no scientific change): there is exactly ONE hard
compute limit, the global governed campaign total. The predecessor additionally
rejected a host whose usage exceeded its own projected shard reservation; that
was a prohibited HOST_HARD_LIMIT, because a host may legitimately consume more
than its projected share when the other host consumes less and the global total
still holds. Per-host figures survive as ACCOUNTING_ONLY / DIAGNOSTIC_ONLY and
never reject.

ACCOUNTING INTEGRITY REPAIR (governance only, no scientific change): every
governed cost component is validated against ONE shared domain primitive
BEFORE any arithmetic, and the resulting aggregate is validated too. The
predecessor validated the per-host components but not `governed_overhead_cpu_h`,
so a NaN, -inf or negative overhead could admit an over-cap campaign
(NaN > 4500 is False). Component-wise validation alone is also insufficient:
finite host values can overflow to +inf whose sum with a -inf overhead is NaN,
so the aggregate is validated as well. Nothing is clamped, abs()-ed or ignored.
"""
from __future__ import annotations

import hashlib
import json
import math
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


# --------------------------------------------------------- accounting domain
GOVERNED_COST_DOMAIN = "finite real, >= 0; bool rejected; -0.0 normalised to 0.0"


def validate_governed_cost(value, what: str) -> float:
    """THE single domain rule for every governed cost component.

    A governed CPU-hour value must be a real, finite, non-negative number.
    Invalid input FAILS CLOSED before it can reach any arithmetic: it is never
    clamped to zero, never passed through abs(), and never ignored.

    bool is rejected explicitly. `True` is an instance of int, so without this
    it would silently count as 1 CPU-h, and `False` as 0 CPU-h.

    -0.0 satisfies `>= 0` under ordinary numeric semantics and is admitted, but
    it is normalised to +0.0 so a negative zero can never propagate into a
    reported total. It cannot reduce an aggregate either way (x + -0.0 == x).
    """
    if isinstance(value, bool):
        raise MultiHostRefusal(
            f"governed cost {what} is a bool ({value!r}); bools are not CPU-hours")
    if not isinstance(value, (int, float)):
        raise MultiHostRefusal(
            f"governed cost {what} is not numeric: {value!r} ({type(value).__name__})")
    v = float(value)
    if not math.isfinite(v):
        raise MultiHostRefusal(f"governed cost {what} is not finite: {value!r}")
    if v < 0.0:
        raise MultiHostRefusal(f"governed cost {what} is negative: {value!r}")
    return v + 0.0                      # normalises -0.0 to +0.0


def validate_governed_factor(value, what: str) -> float:
    """Domain for a governed multiplicative factor: finite and >= 1.

    A factor below 1 would make the overhead multiplier SUBTRACTIVE, silently
    reducing the governed total below the work actually performed. There must be
    no unvalidated subtractive path into the global charge.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MultiHostRefusal(f"governed factor {what} is not numeric: {value!r}")
    v = float(value)
    if not math.isfinite(v):
        raise MultiHostRefusal(f"governed factor {what} is not finite: {value!r}")
    if v < 1.0:
        raise MultiHostRefusal(
            f"governed factor {what} is {value!r} < 1; that would be subtractive")
    return v


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
    validate_governed_cost(rec["cpu_seconds"], f"cell {rec['cell_id']} cpu_seconds")
    ob = rec["obligations_completed"]
    if isinstance(ob, bool) or not isinstance(ob, int) or ob < 0:
        raise MultiHostRefusal(f"cell {rec['cell_id']} has a non-physical obligations_completed")


def per_host_cpu_h(records: list[dict]) -> float:
    """Sum of validated per-cell charges. The SUM is validated too: finite
    addends can still overflow to +inf."""
    total = sum(validate_governed_cost(r["cpu_seconds"], f"cell {r['cell_id']} cpu_seconds")
                for r in records)
    return validate_governed_cost(total / 3600.0, "per-host aggregate CPU-h")


def gate_global_cap(cpu_h_by_role: dict[str, float],
                    governed_overhead_cpu_h: float = CUSUM_CPU_H) -> dict:
    """The ONE and ONLY hard compute limit: GLOBAL_HARD_LIMIT.

    Never interpreted as 4500 per host, per shard or per cell. Acceptance keeps
    the frozen convention exactly: charged <= GLOBAL_CPU_CAP is admitted.
    """
    # (1) EVERY governed component is validated BEFORE any arithmetic.
    factor = validate_governed_factor(OVERHEAD_FACTOR, "OVERHEAD_FACTOR")
    overhead = validate_governed_cost(governed_overhead_cpu_h, "governed_overhead_cpu_h")
    for role in sorted(cpu_h_by_role):
        validate_governed_cost(cpu_h_by_role[role], f"governed CPU-h for {role}")
    # (2) aggregate in the frozen order, then validate the AGGREGATE itself:
    #     individually finite addends can still overflow to +inf, and
    #     (+inf) + (-inf) would be NaN, which no comparison would catch.
    sr = validate_governed_cost(sum(cpu_h_by_role.values()), "aggregate SR CPU-h")
    subtotal = validate_governed_cost(sr + overhead, "governed subtotal CPU-h")
    charged = validate_governed_cost(factor * subtotal, "charged CPU-h")
    # (3) the ONE hard compute limit, frozen convention unchanged.
    if charged > GLOBAL_CPU_CAP:
        raise MultiHostRefusal(
            f"global cap exceeded: charged {charged:.3f} CPU-h > {GLOBAL_CPU_CAP} "
            f"(per-host {cpu_h_by_role})")
    return {"sr_cpu_h": sr, "governed_overhead_cpu_h": overhead,
            "charged_cpu_h": charged, "cap": GLOBAL_CPU_CAP,
            "headroom_cpu_h": GLOBAL_CPU_CAP - charged,
            "enforcement": "GLOBAL_HARD_LIMIT"}


# NOTE: the predecessor's gate_per_host_reservation() is REMOVED, not softened.
# Its presence is asserted against by the audit test, so it cannot silently
# return as a hard limit.
REMOVED_HOST_HARD_LIMITS = ("gate_per_host_reservation",)


def host_accounting(role: str, records: list[dict]) -> dict:
    """ACCOUNTING_ONLY / DIAGNOSTIC_ONLY. Never rejects.

    `projected_share_cpu_h` is a planning projection and `over_projected_share`
    is an anomaly WARNING for telemetry. Neither may gate production: a host may
    exceed its projected share whenever the other host uses less and the ONE
    global governed total still holds.
    """
    used = per_host_cpu_h(records)
    projected = ROLES[role]["per_cell_reservation_cpu_h"] * len(records)
    return {"role": role, "cells": len(records), "cpu_h": used,
            "projected_share_cpu_h": projected,
            "variance_cpu_h": used - projected,
            "over_projected_share": used > projected,   # WARNING ONLY, never a refusal
            "enforcement": "ACCOUNTING_ONLY"}


def reconcile_accounting(host_accounts: dict[str, dict],
                         host_ledgers: dict[str, list[dict]]) -> float:
    """FAIL CLOSED if per-host accounting does not reconcile with the ledgers.

    This is an integrity check on the accounting, not a budget: it protects the
    ONE global limit from being evaluated over numbers that do not describe the
    actual ledger.
    """
    if set(host_accounts) != set(host_ledgers):
        raise MultiHostRefusal(
            f"accounting covers {sorted(host_accounts)} but ledgers cover "
            f"{sorted(host_ledgers)}")
    total = 0.0
    for role, recs in host_ledgers.items():
        acct = host_accounts[role]
        truth_cpu_h = per_host_cpu_h(recs)
        if acct.get("cells") != len(recs):
            raise MultiHostRefusal(
                f"corrupted accounting: {role} claims {acct.get('cells')} cells, "
                f"ledger holds {len(recs)}")
        claimed = validate_governed_cost(acct.get("cpu_h"),
                                         f"{role} claimed accounting cpu_h")
        if abs(claimed - truth_cpu_h) > 1e-9:
            raise MultiHostRefusal(
                f"corrupted accounting: {role} claims {claimed} CPU-h but the "
                f"ledger sums to {truth_cpu_h} CPU-h")
        total += truth_cpu_h
    return total


def assemble_global_ledger(host_ledgers: dict[str, list[dict]], owners: dict[int, str],
                           producer_commit: str, checkpoint_sha256: str) -> dict:
    seen: dict[int, str] = {}
    cpu_h_by_role: dict[str, float] = {}
    accounts: dict[str, dict] = {}
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
        accounts[role] = host_accounting(role, records)      # never rejects
        cpu_h_by_role[role] = accounts[role]["cpu_h"]
    missing = set(range(TOTAL_CELLS)) - set(seen)
    if missing:
        raise MultiHostRefusal(f"aggregate ledger incomplete: {len(missing)} cells missing")
    if obligations != TOTAL_SR_OBLIGATIONS:
        raise MultiHostRefusal(
            f"obligation conservation violated: {obligations} != {TOTAL_SR_OBLIGATIONS}")
    reconcile_accounting(accounts, host_ledgers)   # integrity, not a budget
    cap = gate_global_cap(cpu_h_by_role)           # the ONE hard compute limit
    body = {"cells": sorted(seen), "owners": {str(k): v for k, v in sorted(seen.items())},
            "producer_commit": producer_commit, "checkpoint_sha256": checkpoint_sha256,
            "obligations_completed": obligations}
    return {"cells_completed": len(seen), "obligations_completed": obligations,
            "cpu_h_by_role": cpu_h_by_role, "host_accounting": accounts,
            "hosts_over_projected_share": sorted(
                r for r, a in accounts.items() if a["over_projected_share"]),
            "cap": cap, "aggregate_ledger_sha256": sha256_obj(body)}


def verify_aggregate_ledger(ledger: dict, expect_sha256: str) -> None:
    if ledger.get("aggregate_ledger_sha256") != expect_sha256:
        raise MultiHostRefusal(
            f"corrupted aggregate ledger: {ledger.get('aggregate_ledger_sha256')} "
            f"!= {expect_sha256}")
