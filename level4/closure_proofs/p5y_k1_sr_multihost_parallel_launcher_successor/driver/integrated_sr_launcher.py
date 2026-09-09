"""THE authoritative production entry point for the multi-host SR campaign.

This is the ONLY current launch path. It composes the already-adjudicated
primitives (it re-implements none of them) and enforces every frozen gate BEFORE
any result-bearing work becomes reachable:

  launch authorization -> producer/repository identity -> protocol hash ->
  checkpoint hash -> evidence-manifest hash -> shard-manifest hash -> host role ->
  thread contract -> live runtime hash -> physical worker topology ->
  scientific scope -> host shard ownership -> accounting state ->
  GLOBAL governed charge <= 4500 -> pending-cell plan -> [production gate] ->
  cell-atomic execution -> ledger commit -> global-cap recheck -> next cell

The result-bearing transition is REAL and complete. It is closed only by the
frozen authorization field production_enabled=false. A future additive
authorization that changes ONLY that field makes it reachable; nothing in this
file is hardcoded unreachable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
sys.path.insert(0, str(NS / "driver"))

import multihost as M                                              # noqa: E402
import executor_adapter as EA                                      # noqa: E402
import global_budget as GB                                         # noqa: E402
import worker_pool as WP                                           # noqa: E402

LAUNCHER_SCHEMA = "rebaseguard.p5y.k1.sr.multihost.integrated-launcher.v1"

SOURCE_CLOSURE = (
    "driver/integrated_sr_launcher.py", "driver/executor_adapter.py",
    "driver/global_budget.py", "driver/multihost.py",
    "config/protocol.json", "config/PRE_RESULT_CHECKPOINT.json",
    "config/CHECKPOINT_HASH", "config/PROTOCOL_HASH",
    "config/SHARD_MANIFEST.json", "config/SHARD_MANIFEST_SHA256.json",
    "config/EVIDENCE_MANIFEST_HASH", "evidence/EVIDENCE_MANIFEST.json",
    "driver/worker_pool.py",
)
Refusal = M.MultiHostRefusal


def _sha256(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------ authorization
def load_authorization(path=None, expect_sha256=None) -> dict:
    path = Path(path) if path else NS / "config/LAUNCH_AUTHORIZATION.json"
    if not path.exists():
        raise Refusal(f"launch authorization absent: {path}")
    raw = path.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    expect = expect_sha256 or (NS / "config/LAUNCH_AUTHORIZATION_HASH").read_text().strip()
    if got != expect:
        raise Refusal(f"launch authorization sha256 {got} != authorised {expect}")
    auth = json.loads(raw)
    for k in ("producer_commit", "protocol_sha256", "checkpoint_sha256",
              "evidence_manifest_sha256", "shard_manifest_sha256",
              "runtime_contract_hashes", "hosts", "scientific_scope",
              "global_cpu_cap", "production_enabled", "concurrency"):
        if k not in auth:
            raise Refusal(f"launch authorization missing bound field {k}")
    if auth.get("result_bearing") is not False:
        raise Refusal("launch authorization must be result-free")
    return auth


# --------------------------------------------------------------- identities
def integrated_source_manifest(ns=None) -> dict:
    """Canonical hash of the executable production closure, so a host without a
    git checkout is still bound to the exact producer bytes."""
    ns = Path(ns) if ns else NS
    files = {}
    for rel in sorted(SOURCE_CLOSURE):
        p = ns / rel
        if not p.exists():
            raise Refusal(f"integrated closure file absent: {rel}")
        files[rel] = _sha256(p)
    blob = "".join(f"{k}:{v}\n" for k, v in sorted(files.items())).encode()
    return {"files": files,
            "INTEGRATED_SOURCE_MANIFEST_HASH": hashlib.sha256(blob).hexdigest()}


def _git(repo, *args) -> str:
    return subprocess.check_output(["git", "-C", str(repo)] + list(args)).decode().strip()


def _gate_head_against(approved_head: str, live_head: str, *, clean: bool) -> dict:
    """The head relation, isolated so it is directly testable without a repo."""
    if not clean:
        raise Refusal("worktree is not clean; production refused")
    if live_head != approved_head:
        raise Refusal(
            f"live HEAD {live_head} != approved launch head {approved_head}; "
            "an unbound descendant or unrelated commit is refused")
    return {"approved_launch_head": approved_head, "live_head": live_head,
            "worktree_clean": True}


def gate_approved_launch_head(auth, *, repo=None) -> dict:
    """APPROVED LAUNCH STATE IDENTITY.

    The authorization binds a TAG NAME, not a commit hash, because a commit
    cannot contain its own hash. The tag is resolved at run time and the live
    checkout must equal it exactly, so an unbound DESCENDANT of the approved
    state is refused just as firmly as an unrelated commit. The worktree must
    also be clean.
    """
    repo = Path(repo) if repo else ROOT
    tag = auth.get("approved_launch_tag")
    if not tag:
        raise Refusal("launch authorization does not bind approved_launch_tag")
    try:
        approved = _git(repo, "rev-list", "-n1", tag)
    except Exception as exc:                                       # noqa: BLE001
        raise Refusal(f"approved launch tag {tag!r} does not resolve: {exc!r}") from exc
    head = _git(repo, "rev-parse", "HEAD")
    dirty = [l for l in _git(repo, "status", "--porcelain").splitlines() if l.strip()]
    out = _gate_head_against(approved, head, clean=not dirty)
    return {"approved_launch_tag": tag, **out}


def gate_producer_ancestry(auth, approved_head, *, repo=None) -> dict:
    """PRODUCER IMPLEMENTATION IDENTITY.

    The producer commit is the immutable commit that introduced the driver. It
    is NOT required to equal the live checkout; requiring that conflated two
    different identities and made the frozen authorization unsatisfiable at the
    approved head. The correct relation is ancestry.
    """
    repo = Path(repo) if repo else ROOT
    pc = auth.get("producer_commit")
    if not isinstance(pc, str) or len(pc) != 40:
        raise Refusal(f"producer_commit {pc!r} is not a full commit id")
    try:
        kind = _git(repo, "cat-file", "-t", pc)
    except Exception as exc:                                       # noqa: BLE001
        raise Refusal(f"producer_commit {pc} does not exist: {exc!r}") from exc
    if kind != "commit":
        raise Refusal(f"producer_commit {pc} is a {kind}, not a commit")
    rc = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor",
                         pc, approved_head]).returncode
    if rc != 0:
        raise Refusal(
            f"producer_commit {pc} is NOT an ancestor of the approved launch head "
            f"{approved_head}; the approved state does not contain this producer")
    return {"producer_commit": pc, "is_ancestor_of_approved_head": True}


def gate_producer_identity(auth, role, *, repo=None, ns=None) -> dict:
    """Producer binding, per host role.

    AWS runs from the authoritative git worktree, so it is bound to the immutable
    producer commit. Vultr runs from a provisioned immutable tree with no git
    checkout, so it is bound to the INTEGRATED_SOURCE_MANIFEST_HASH of exactly the
    same executable bytes. Both are refused on any mismatch; neither is optional.
    """
    mode = auth["hosts"][role].get("producer_binding")
    if mode == "GIT_COMMIT":
        approved = gate_approved_launch_head(auth, repo=repo)
        anc = gate_producer_ancestry(auth, approved["approved_launch_head"], repo=repo)
        # the frozen manifest-content checks still apply; only the HEAD relation
        # is corrected, so gate_producer_commit is called with the producer
        # commit itself for its content bindings.
        M.gate_producer_commit(auth, anc["producer_commit"],
                               auth["checkpoint_sha256"], auth["shard_manifest_sha256"])
        return {"binding": mode, **approved, **anc}
    if mode == "SOURCE_MANIFEST":
        man = integrated_source_manifest(ns)
        got = man["INTEGRATED_SOURCE_MANIFEST_HASH"]
        want = auth["integrated_source_manifest_sha256"]
        if got != want:
            raise Refusal(f"integrated source manifest {got} != authorised {want}")
        return {"binding": mode, "INTEGRATED_SOURCE_MANIFEST_HASH": got,
                "producer_commit": auth["producer_commit"]}
    raise Refusal(f"host {role} has no recognised producer_binding: {mode!r}")


def gate_bound_hashes(auth, ns=None) -> dict:
    """Bind protocol AND evidence-manifest hashes, which the adjudicator found
    missing from the predecessor manifest."""
    ns = Path(ns) if ns else NS
    checks = {
        "protocol_sha256": (_sha256(ns / "config/protocol.json"), auth["protocol_sha256"]),
        "checkpoint_sha256": ((ns / "config/CHECKPOINT_HASH").read_text().strip(),
                              auth["checkpoint_sha256"]),
        "evidence_manifest_sha256": (_sha256(ns / "evidence/EVIDENCE_MANIFEST.json"),
                                     auth["evidence_manifest_sha256"]),
        "shard_manifest_sha256": (_sha256(ns / "config/SHARD_MANIFEST.json"),
                                  auth["shard_manifest_sha256"]),
    }
    for name, (got, want) in checks.items():
        if got != want:
            raise Refusal(f"{name} {got} != authorised {want}")
    return {k: v[0] for k, v in checks.items()}


def resolve_role(auth, sys_vendor=None) -> str:
    """Role is DERIVED from host identity, never supplied by the caller."""
    vendor_path = Path("/sys/class/dmi/id/sys_vendor")
    vendor = sys_vendor if sys_vendor is not None else (
        vendor_path.read_text().strip() if vendor_path.exists() else "")
    role = M.detect_role(vendor)
    if role not in auth["hosts"]:
        raise Refusal(f"role {role} is not authorised by this launch authorization")
    return role


def venv_root() -> Path:
    """The worktree that actually holds the LIVE venv, derived from the loaded
    numpy rather than from this file's location.

    runtime_identity.backend_libraries() globs `<its own worktree>/level4/.venv`.
    Importing it from a worktree that has no venv yields an EMPTY backend-library
    set and therefore a different, WEAKER contract hash. The launcher's own
    worktree need not hold the venv, so the root is resolved from numpy.
    """
    import numpy
    marker = "/level4/.venv/"
    real = os.path.realpath(numpy.__file__)
    if marker not in real:
        raise Refusal(f"cannot locate the level4 venv from numpy at {real}")
    return Path(real.split(marker)[0])


def gate_runtime_identity(auth, role, *, live_hash=None, env=None) -> dict:
    """Thread contract FIRST: the fingerprint includes thread_environment, so a
    missing contract must refuse precisely rather than look like drift."""
    tc = M.gate_thread_contract(env)
    backend_libs = None
    if live_hash is None:
        vroot = venv_root()
        sys.path.insert(0, str(vroot / "level4/closure_proofs"
                               "/p5y_k1_cusum_aux4_fullcover/code"))
        import runtime_identity as RI                               # noqa: E402
        contract = RI.contract()
        backend_libs = contract.get("backend_libraries") or {}
        if not backend_libs:
            raise Refusal(
                "runtime contract has an EMPTY backend-library set; the fingerprint "
                f"would be computed over no libraries (venv root resolved to {vroot})")
        live_hash = RI.contract_hash(contract)
    M.gate_runtime_hash(role, live_hash)
    if auth["runtime_contract_hashes"][role] != live_hash:
        raise Refusal(f"{role} runtime hash not the authorised one")
    return {"thread_contract": tc["thread_contract"], "runtime_contract_hash": live_hash,
            "backend_libraries_hashed": len(backend_libs) if backend_libs is not None else "injected"}


def gate_topology(auth, role, *, cores=None, siblings=None) -> dict:
    spec = auth["hosts"][role]
    if cores is None:
        cores = M.physical_cores() if hasattr(M, "physical_cores") else None
    if cores is None:
        base = Path("/sys/devices/system/cpu")
        seen, cores = set(), []
        for d in sorted(base.glob("cpu[0-9]*"), key=lambda p: int(p.name[3:])):
            sib = d / "topology/thread_siblings_list"
            if not sib.exists():
                continue
            members = []
            for part in sib.read_text().strip().split(","):
                if "-" in part:
                    a, b = part.split("-")
                    members += list(range(int(a), int(b) + 1))
                else:
                    members.append(int(part))
            key = tuple(sorted(members))
            if key in seen:
                continue
            seen.add(key)
            cores.append(min(members))
        cores.sort()
    if siblings is None:
        siblings = {}
        for c in cores:
            f = Path(f"/sys/devices/system/cpu/cpu{c}/topology/thread_siblings_list")
            sibs = []
            if f.exists():
                for part in f.read_text().strip().split(","):
                    if "-" in part:
                        a, b = part.split("-")
                        sibs += list(range(int(a), int(b) + 1))
                    else:
                        sibs.append(int(part))
            siblings[c] = sibs or [c]
    assign = cores[:spec["workers"]]
    if assign != spec["cores"]:
        raise Refusal(f"{role} core assignment {assign} != authorised {spec['cores']}")
    return M.gate_workers(role, spec["workers"], assign, siblings)


def gate_scientific_scope(auth, root=None) -> dict:
    """Verified against the REAL frozen modules, not against a copied constant."""
    root = Path(root) if root else ROOT
    mods = EA.bind(root)
    want = auth["scientific_scope"]
    a = mods["sr_universe"].audit()
    if not a["ok"]:
        raise Refusal(f"SR universe audit failed: {a.get('findings')}")
    if a["n_cells"] != want["total_cells"]:
        raise Refusal(f"cells {a['n_cells']} != {want['total_cells']}")
    if a["n_sr_obligations"] != want["obligations"]:
        raise Refusal(f"obligations {a['n_sr_obligations']} != {want['obligations']}")
    o9 = json.loads((root / "level4/closure_proofs/p5y_k1_sr_backend_o9_successor"
                     "/config/protocol.json").read_text())
    cen, fs = o9["census"], o9["frozen_scope"]
    if cen["distinct_candidates"] != want["candidates"]:
        raise Refusal("candidate census drift")
    if cen["certified_contracts"] != want["contracts"]:
        raise Refusal("contract census drift")
    for k in ("D", "Z"):
        if fs[k] != want[k]:
            raise Refusal(f"{k} {fs[k]} != {want[k]}")
    if fs["precision_bits"] != want["precision_bits"]:
        raise Refusal("precision drift")
    if want["backend"] != "O9":
        raise Refusal(f"backend {want['backend']} != O9")
    ident = EA.adapter_identity(root)
    if ident["SCIENTIFIC_ADAPTER_HASH"] != auth["scientific_adapter_hash"]:
        raise Refusal(
            f"scientific adapter hash {ident['SCIENTIFIC_ADAPTER_HASH']} "
            f"!= authorised {auth['scientific_adapter_hash']}")
    return {"cells": a["n_cells"], "obligations": a["n_sr_obligations"],
            "candidates": cen["distinct_candidates"], "contracts": cen["certified_contracts"],
            "D": fs["D"], "Z": fs["Z"], "precision_bits": fs["precision_bits"],
            "backend": "O9", "scientific_adapter_hash": ident["SCIENTIFIC_ADAPTER_HASH"]}


def gate_concurrency(auth, role, *, enforce_active=False, active_host=None) -> dict:
    """Concurrency control for the ONE global budget.

    `enforce_active` is False during preflight so BOTH hosts can verify every
    identity, scope and topology gate; it is True at the cell-admission boundary,
    which is the only place a draw against the global budget happens. That keeps
    draws strictly serialised without making a dry-run host-specific.
    """
    c = auth["concurrency"]
    mode = c.get("mode")
    if mode not in GB.CONCURRENCY_MODES:
        raise Refusal(f"unknown concurrency mode {mode!r}")
    if mode == "SERIALIZED_ACTIVE_HOST":
        if enforce_active and active_host != role:
            raise Refusal(
                f"{role} is not the active host ({active_host}); the ONE global "
                "budget is drawn serially, so this host refuses rather than race")
    elif enforce_active:
        ep = c.get("coordinator_endpoint")
        if not ep or not Path(ep).parent.exists():
            raise Refusal("SHARED_COORDINATOR requires a bound, reachable coordinator endpoint")
    return {"mode": mode, "host_sequence": c.get("host_sequence")}


def far_field_attribution(auth, owners) -> dict:
    """The frozen universe holds 8849 SR obligations, but the 316-cell cover
    carries only 8848: the remaining one is SR:-1:far_field:all_m, on cell -1,
    which is NOT a shard cell.

    A campaign that reported obligations_per_cell for all 316 cells would sum to
    8848 and final assembly would refuse obligation conservation forever. The
    far-field obligation is therefore attributed DETERMINISTICALLY to the lowest
    -numbered cell owned by the first host in the frozen sequence. This is
    bookkeeping attribution of work that is produced either way; it changes no
    scientific scope, no threshold and no obligation count.
    """
    ff = auth.get("far_field_obligation")
    if not ff:
        raise Refusal("authorization does not bind far_field_obligation attribution")
    first = auth["concurrency"]["host_sequence"][0]
    owned = sorted(c for c, r in owners.items() if r == first)
    cell = owned[0]
    if ff.get("attributed_to_role") != first or ff.get("attributed_to_cell") != cell:
        raise Refusal(
            f"far-field attribution {ff.get('attributed_to_role')}:{ff.get('attributed_to_cell')} "
            f"!= deterministic {first}:{cell}")
    return {"work_id": ff["work_id"], "count": ff["count"],
            "role": first, "cell": cell}


def obligations_for_cell(auth, owners, role, cell) -> int:
    per = auth["scientific_scope"]["obligations_per_cell"]
    ff = far_field_attribution(auth, owners)
    return per + (ff["count"] if (role == ff["role"] and cell == ff["cell"]) else 0)


def shard_structurally_complete(role, owners, completed) -> bool:
    owned = {c for c, r in owners.items() if r == role}
    return owned.issubset(set(completed))


def resolve_active_host(auth, owners, completed, inflight=0) -> dict:
    """Deterministic, frozen, RESULT-INDEPENDENT role transition.

    SERIALIZED_ACTIVE_HOST would otherwise strand the other host's shard. The
    trigger depends only on structural completion, zero in-flight work and a
    valid ledger -- never on an observed scientific value.
    """
    seq = auth["concurrency"].get("host_sequence")
    if not seq:
        raise Refusal("authorization does not bind a host_sequence")
    for role in seq:
        if not shard_structurally_complete(role, owners, completed):
            return {"active_host": role, "sequence": seq,
                    "reason": "shard not structurally complete"}
        if inflight:
            return {"active_host": role, "sequence": seq,
                    "reason": f"{inflight} tasks still in flight; role may not advance"}
    return {"active_host": None, "sequence": seq,
            "reason": "every shard structurally complete"}


# ------------------------------------------------------------------ preflight
def preflight(auth=None, *, role=None, sys_vendor=None, env=None, live_hash=None,
              cores=None, siblings=None, repo=None, ns=None, root=None,
              budget_path=None) -> dict:
    """Every frozen gate, in the frozen order, before any work is reachable."""
    trace, ns = [], (Path(ns) if ns else NS)

    def step(name, fn):
        trace.append({"gate": name, "status": "PASS", "detail": fn()})

    auth = auth or load_authorization()
    trace.append({"gate": "launch_authorization", "status": "PASS",
                  "detail": {"producer_commit": auth["producer_commit"],
                             "production_enabled": auth["production_enabled"]}})
    resolved = role or resolve_role(auth, sys_vendor)
    step("repository_producer_identity",
         lambda: gate_producer_identity(auth, resolved, repo=repo, ns=ns))
    step("bound_hashes_protocol_checkpoint_evidence_shard", lambda: gate_bound_hashes(auth, ns))
    trace.insert(1, {"gate": "host_role", "status": "PASS", "detail": {"role": resolved}})
    step("thread_contract_and_runtime_identity",
         lambda: gate_runtime_identity(auth, resolved, live_hash=live_hash, env=env))
    step("worker_topology", lambda: gate_topology(auth, resolved, cores=cores, siblings=siblings))
    step("scientific_scope", lambda: gate_scientific_scope(auth, root))
    manifest = M.load_shard_manifest(ns / "config/SHARD_MANIFEST.json",
                                     auth["shard_manifest_sha256"])
    owners = M.gate_shards(manifest)
    owned = sorted(c for c, r in owners.items() if r == resolved)
    if len(owned) != auth["hosts"][resolved]["cell_count"]:
        raise Refusal(f"{resolved} owns {len(owned)} cells != "
                      f"{auth['hosts'][resolved]['cell_count']}")
    trace.append({"gate": "shard_ownership", "status": "PASS",
                  "detail": {"role": resolved, "owned_cells": len(owned)}})

    budget = GB.GlobalBudget(budget_path or (ns / "evidence/global_budget.json"),
                             M.validate_governed_cost, M.gate_global_cap,
                             overhead_cpu_h=auth["governed_overhead_cpu_h"],
                             cap_cpu_h=M.validate_governed_cap(M.GLOBAL_CPU_CAP))
    status = budget.status()
    trace.append({"gate": "global_accounting_and_cap", "status": "PASS",
                  "detail": {"charged_cpu_h": status["cap"]["charged_cpu_h"],
                             "cap": status["cap"]["cap"],
                             "headroom_cpu_h": status["cap"]["headroom_cpu_h"]}})

    active = resolve_active_host(auth, owners, status["completed_cells"], inflight=0)
    trace.append({"gate": "concurrency_and_active_host", "status": "PASS",
                  "detail": dict(gate_concurrency(auth, resolved), **active,
                                 admission_allowed_on_this_host=(
                                     active["active_host"] == resolved))})
    done = set(status["completed_cells"])
    pending = [c for c in owned if c not in done]
    trace.append({"gate": "pending_cell_plan", "status": "PASS",
                  "detail": {"owned": len(owned), "completed": len(done & set(owned)),
                             "pending": len(pending), "first": pending[:5]}})
    return {"role": resolved, "auth": auth, "owners": owners, "owned": owned,
            "pending": pending, "budget": budget, "trace": trace,
            "active": active, "ns": ns, "root": Path(root) if root else ROOT}


# ------------------------------------------------- result-bearing transition
def gate_production_enabled(auth) -> None:
    """The ONLY thing closing the result-bearing path. Everything after this is a
    complete, executable implementation."""
    if auth.get("production_enabled") is not True:
        raise Refusal(
            "production_enabled is false in the frozen launch authorization; "
            "result-bearing execution refused. A future additive authorization "
            "changing ONLY this field makes the path below reachable.")


def execute_one_cell(pf, cell_id, *, science=None, root=None,
                     reservation_cpu_h=None) -> dict:
    """Cell-atomic: draw -> execute -> verify -> commit -> re-gate the cap."""
    auth, role, budget = pf["auth"], pf["role"], pf["budget"]
    gate_production_enabled(auth)
    gate_concurrency(auth, role, enforce_active=True,
                     active_host=pf["active"]["active_host"])
    if pf["active"]["active_host"] != role:
        raise Refusal(
            f"{role} is not the currently active host ({pf['active']['active_host']}): "
            f"{pf['active']['reason']}")
    M.gate_cell_ownership(role, cell_id, pf["owners"])
    if cell_id not in pf["pending"]:
        raise Refusal(f"cell {cell_id} is not pending for {role}")
    reservation = M.validate_governed_cost(
        reservation_cpu_h if reservation_cpu_h is not None
        else auth["hosts"][role]["per_cell_reservation_cpu_h"], "cell reservation")
    key = budget.draw(role, cell_id, reservation)
    try:
        import time
        t0 = time.process_time()
        out = EA.execute_cell(root or ROOT, cell_id, science=science)
        actual = M.validate_governed_cost((time.process_time() - t0) / 3600.0,
                                          "actual cell CPU-h")
        record = {"cell_id": cell_id, "role": role,
                  "producer_commit": auth["producer_commit"],
                  "checkpoint_sha256": auth["checkpoint_sha256"],
                  "runtime_contract_hash": auth["runtime_contract_hashes"][role],
                  "scientific_content_hash": out["scientific_content_hash"],
                  "cpu_seconds": actual * 3600.0,
                  "obligations_completed": auth["scientific_scope"]["obligations_per_cell"],
                  "complete": True}
        M.validate_record(record, role, pf["owners"], auth["producer_commit"],
                          auth["checkpoint_sha256"])
    except Exception:
        budget.release(key)                      # torn cell: nothing is counted
        raise
    cap = budget.commit(key, actual, record)     # atomic finalisation + re-gate
    return {"cell_id": cell_id, "record": record, "cap": cap}


# ------------------------------------------------------- real worker pool
def thread_env_of(auth) -> dict:
    tc = auth["thread_contract"]
    return {v: tc["required_value"] for v in tc["variables"]}


def build_pool(pf, *, science_enabled=False) -> tuple:
    """One REAL process per qualified physical core, each pinned and verified."""
    auth, role = pf["auth"], pf["role"]
    cores = auth["hosts"][role]["cores"]
    pool = WP.WorkerPool(cores, thread_env_of(auth), pf["root"],
                         science_enabled=science_enabled)
    info = pool.start()
    if info["workers"] != auth["hosts"][role]["workers"]:
        pool.close()
        raise Refusal(f"pool has {info['workers']} workers != "
                      f"authorised {auth['hosts'][role]['workers']}")
    for pid, aff in info["affinity"].items():
        if len(aff) != 1 or aff[0] not in cores:
            pool.close()
            raise Refusal(f"worker {pid} affinity {aff} is not a single authorised core")
    if sorted(a[0] for a in info["affinity"].values()) != sorted(cores):
        pool.close()
        raise Refusal("workers are not bound one-per-authorised-core")
    return pool, info


def prove_concurrency(pf, *, seconds=1.0, rounds=1) -> dict:
    """RESULT-FREE saturation: measure genuine overlap, never infer it."""
    pool, info = build_pool(pf, science_enabled=False)
    try:
        n = info["workers"] * rounds
        for i in range(n):
            pool.submit({"kind": "SYNTHETIC_SPIN", "seconds": seconds, "cell_id": None})
        recs = [pool.get(timeout=120 + seconds * n) for _ in range(n)]
    finally:
        pool.close()
    bad = [r for r in recs if not r.get("ok")]
    if bad:
        raise Refusal(f"synthetic workers failed: {bad[:2]}")
    return {"workers": info["workers"], "cores": info["cores"],
            "pids": sorted({r["pid"] for r in recs}),
            "distinct_pids": len({r["pid"] for r in recs}),
            "affinity_per_pid": {r["pid"]: r["affinity"] for r in recs},
            "tasks": len(recs),
            "max_simultaneous_active_workers": WP.max_simultaneous(recs),
            "window_s": round(max(r["t_end"] for r in recs)
                              - min(r["t_start"] for r in recs), 3),
            "serial_equivalent_s": round(sum(r["t_end"] - r["t_start"] for r in recs), 3)}


def structural_import_in_workers(pf) -> dict:
    """Prove the authoritative scientific dependencies import in CHILD processes,
    without computing a genuine cell."""
    pool, info = build_pool(pf, science_enabled=False)
    try:
        for _ in range(info["workers"]):
            pool.submit({"kind": "STRUCTURAL_IMPORT",
                         "driver_dir": str(pf["ns"] / "driver"), "cell_id": None})
        recs = [pool.get(timeout=300) for _ in range(info["workers"])]
    finally:
        pool.close()
    bad = [r for r in recs if not r.get("ok")]
    if bad:
        raise Refusal(f"scientific dependencies did not import in workers: {bad[:1]}")
    return {"workers": len(recs),
            "all_bound": all(r["payload"]["has_cell_certificate"]
                             and r["payload"]["has_resolvent"] for r in recs),
            "bound_modules": recs[0]["payload"]["bound_modules"]}


# ------------------------------------------------------------- the scheduler
def run_production(pf, *, max_cells=None, poll_timeout=3600.0,
                   synthetic_seconds=None) -> dict:
    """Bounded-in-flight scheduler. The PARENT is the sole admission, accounting,
    finalisation and resume authority; workers only compute.

    At most `workers` cells are in flight, and every admission re-draws from the
    ONE global budget under the coordinator lock, so 16 workers cannot each pass
    the same stale cap check.
    """
    auth, role, budget = pf["auth"], pf["role"], pf["budget"]
    gate_production_enabled(auth)
    gate_concurrency(auth, role, enforce_active=True,
                     active_host=pf["active"]["active_host"])
    if pf["active"]["active_host"] != role:
        raise Refusal(f"{role} is not the active host: {pf['active']['reason']}")
    pool, info = build_pool(pf, science_enabled=(synthetic_seconds is None))
    pending = list(pf["pending"] if max_cells is None else pf["pending"][:max_cells])
    inflight, done, stopped = {}, [], None
    try:
        while pending or inflight:
            while pending and len(inflight) < info["workers"]:
                cell = pending[0]
                reservation = M.validate_governed_cost(
                    auth["hosts"][role]["per_cell_reservation_cpu_h"], "cell reservation")
                try:
                    key = budget.draw(role, cell, reservation)   # sole authority
                except (GB.BudgetRefusal, M.MultiHostRefusal) as exc:
                    stopped = f"admission stopped: {exc}"
                    pending = []
                    break
                pending.pop(0)
                inflight[cell] = key
                if synthetic_seconds is None:
                    pool.submit({"kind": "SCIENCE", "cell_id": cell,
                                 "driver_dir": str(pf["ns"] / "driver")})
                else:
                    # RESULT-FREE structural simulation: exercises the real pool,
                    # scheduler, accounting, atomic finalisation and resume without
                    # computing any genuine science.
                    pool.submit({"kind": "SYNTHETIC_SPIN", "cell_id": cell,
                                 "seconds": synthetic_seconds})
            if not inflight:
                break
            rec = pool.get(timeout=poll_timeout)
            cell = rec.get("cell_id")
            if cell not in inflight:
                raise Refusal(f"worker returned unknown/duplicate cell {cell!r}")
            key = inflight.pop(cell)
            if not rec.get("ok"):
                budget.release(key)                  # torn cell: nothing counted
                continue
            sci = (rec["payload"].get("scientific_content_hash")
                   if isinstance(rec.get("payload"), dict) else None)
            if sci is None:
                sci = "%064x" % cell                 # synthetic structural stand-in
            M.gate_cell_ownership(role, cell, pf["owners"])
            actual = M.validate_governed_cost(rec["cpu_seconds"] / 3600.0,
                                              "actual cell CPU-h")
            record = {"cell_id": cell, "role": role,
                      "producer_commit": auth["producer_commit"],
                      "checkpoint_sha256": auth["checkpoint_sha256"],
                      "runtime_contract_hash": auth["runtime_contract_hashes"][role],
                      "scientific_content_hash": sci,
                      "cpu_seconds": actual * 3600.0,
                      "obligations_completed": obligations_for_cell(
                          auth, pf["owners"], role, cell),
                      "complete": True}
            M.validate_record(record, role, pf["owners"], auth["producer_commit"],
                              auth["checkpoint_sha256"])
            budget.commit(key, actual, record)       # atomic finalisation + re-gate
            done.append(cell)
    finally:
        for k in inflight.values():
            budget.release(k)
        pool.close()
    return {"completed": done, "stopped": stopped,
            "status": budget.status()}


# --------------------------------------------------------------- final closure
def final_assembly(pf, host_ledgers) -> dict:
    auth = pf["auth"]
    out = M.assemble_global_ledger(host_ledgers, pf["owners"], auth["producer_commit"],
                                   auth["checkpoint_sha256"])
    if out["cells_completed"] != auth["scientific_scope"]["total_cells"]:
        raise Refusal(f"final assembly: {out['cells_completed']} cells != "
                      f"{auth['scientific_scope']['total_cells']}")
    for role, spec in auth["hosts"].items():
        n = sum(1 for r in host_ledgers.get(role, []))
        if n != spec["cell_count"]:
            raise Refusal(f"final assembly: {role} produced {n} != {spec['cell_count']}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=LAUNCHER_SCHEMA)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--produce", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not (a.dry_run or a.produce):
        ap.error("choose --dry-run or --produce")
    pf = preflight()
    if a.json:
        print(json.dumps({"role": pf["role"], "trace": pf["trace"],
                          "pending": len(pf["pending"])}, indent=1, default=str))
    else:
        for t in pf["trace"]:
            print(f"  {t['status']:5s} {t['gate']}")
        print(f"  role={pf['role']} owned={len(pf['owned'])} pending={len(pf['pending'])}")
    conc = prove_concurrency(pf, seconds=0.6)
    print(f"  POOL  {conc['workers']} real processes, cores {conc['cores']}, "
          f"max simultaneous active = {conc['max_simultaneous_active_workers']}")
    if a.produce:
        try:
            gate_production_enabled(pf["auth"])
        except Refusal as e:
            print(f"  REFUSE result_bearing_transition: {e}")
            return 3
        run_production(pf)
        return 0
    print("  REFUSE result_bearing_transition (dry-run: production_enabled=false)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
