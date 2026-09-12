"""PS1 production launcher (NEW, additive). Replaces the historical non-conformant production adapter for PS1.

Interface = what the audited lifecycle ops expect of a production namespace: load_production_authorization,
production_preflight, admit_cell, run_production_cells(pf, poll_timeout=None), assemble_production_campaign.
Accounting = the frozen GlobalBudget (byte-identical copy) over the PS1 ledger with the PS1 cap from multihost.
Release call sites are exactly the three the lifecycle classifies (worker failure / malformed -> HALT; the finally
block -> torn infrastructure escrow, retry-eligible).

Historical defects fixed: workers verify 256-bit precision in a fresh interpreter; results cross processes as JSON
files only (no Queue, no Arb); a cell is sealed only after its evidence files are re-read and re-hashed from disk and
its T5 record re-verified 28/28; no surrogate envelope; COMPLETE only for verified cells.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
PROD_NS = NS
ROOT = NS.parents[2]
PRODUCTION_DIR = NS / "production"
PRODUCTION_LEDGER = PRODUCTION_DIR / "PRODUCTION_LEDGER.json"
AUTH_PATH = NS / "config/LAUNCH_AUTHORIZATION.json"
AUTH_HASH_PATH = NS / "config/LAUNCH_AUTHORIZATION_HASH"
SHARD_MANIFEST = NS / "config/SHARD_MANIFEST.json"
PRODUCTION_LEDGER_SCHEMA = "rebaseguard.p5y.k1.sr.multihost.global-budget.v1"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import multihost as M                     # noqa: E402
import global_budget as GB                # noqa: E402
import production_provenance as PP        # noqa: E402


class ProductionRefusal(RuntimeError):
    pass


class PoolWorkerLost(RuntimeError):
    """Infrastructure: a pool worker process died. Never a scientific verdict."""


def _sha256(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def authorization_hash(path=None) -> str:
    return _sha256(path or AUTH_PATH)


def production_closure_hash(ns=None) -> str:
    ns = Path(ns or NS)
    files = {r: _sha256(ns / r) for r in sorted(("driver/production_launcher.py", "driver/production_provenance.py"))}
    return hashlib.sha256("".join(f"{k}:{v}\n" for k, v in files.items()).encode()).hexdigest()


def load_production_authorization(path=None, hash_path=None) -> dict:
    path, hash_path = Path(path or AUTH_PATH), Path(hash_path or AUTH_HASH_PATH)
    want = hash_path.read_text().strip()
    if _sha256(path) != want:
        raise ProductionRefusal(f"launch authorization sha256 {_sha256(path)} != frozen {want}")
    auth = json.loads(path.read_text())
    if auth.get("schema") != "rebaseguard.p5y.k1.ps1.launch-authorization.v1" or auth.get("result_bearing") is not False:
        raise ProductionRefusal("not a result-free PS1 launch authorization")
    return auth


def executor_source_identity(root=None) -> dict:
    root = Path(root or ROOT)
    auth = load_production_authorization()
    got = {rel: _sha256(root / rel) for rel in sorted(auth["executor_source_manifest"])}
    return {"files": got, "EXECUTOR_HASH": hashlib.sha256(M.canonical(got)).hexdigest()}


def gate_production_result_path(path, *, ns=None) -> Path:
    p = Path(path).resolve()
    base = (Path(ns or NS) / "production").resolve()
    if base not in p.parents and p != base / "PRODUCTION_LEDGER.json":
        raise ProductionRefusal(f"{p} is outside the PS1 production namespace")
    return p


def gate_no_evidence_collision(paths, *, ns=None) -> None:
    for p in paths:
        if Path(p).exists():
            raise ProductionRefusal(f"refusing to overwrite existing production evidence {p}")


def _atomic_write(path: Path, data: bytes) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".tmp-{path.name}-{os.getpid()}"
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    fd = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def worker_env(auth, role) -> dict:
    """Frozen host environment + PYTHONPATH derived from THIS checkout root (relative list bound in the authorization)."""
    env = dict(auth["hosts"][role]["environment"])
    env["PYTHONPATH"] = ":".join(str(ROOT / rel) for rel in auth["pythonpath_rel"])
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _probe(auth, role) -> dict:
    host = auth["hosts"][role]
    r = subprocess.run([host["python"], str(HERE / "ps1_pool_worker.py"), "--probe"], env=worker_env(auth, role),
                       cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise ProductionRefusal(f"precision/runtime probe failed: {r.stderr[-500:]}")
    return json.loads(r.stdout)


def production_preflight(auth=None, *, role=None, budget_path=None, probe=True, **kw) -> dict:
    """Every PS1 production gate. Executes NO science."""
    auth = auth or load_production_authorization()
    trace = []

    def ok(gate, detail=None):
        trace.append({"gate": gate, "status": "PASS", "detail": detail})
    vendor = Path("/sys/class/dmi/id/sys_vendor").read_text().strip() if role is None else M.ROLES[role]["sys_vendor"]
    role = M.gate_role(role or M.detect_role(vendor), vendor)
    ok("host_role", {"role": role, "sys_vendor": vendor})
    if auth["hosts"].get(role, {}).get("workers", 0) <= 0:
        raise ProductionRefusal(f"{role} is not an authorised PS1 host")
    ok("thread_contract", M.gate_thread_contract())
    head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"]).decode().strip()
    pc = auth["producer_commit"]
    if subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", pc, head]).returncode != 0:
        raise ProductionRefusal(f"authorised producer_commit {pc} is not an ancestor of checkout HEAD {head}")
    changed = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", pc, head, "--"] + sorted(auth["executor_source_manifest"]),
                             capture_output=True, text=True, check=True).stdout.split()
    if changed:
        raise ProductionRefusal(f"executor source changed since the producer commit: {changed[:5]}")
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no", "--"]
                           + sorted(auth["executor_source_manifest"]), capture_output=True, text=True, check=True).stdout.split()
    if dirty:
        raise ProductionRefusal(f"executor source has uncommitted changes: {dirty[:5]}")
    ok("producer_commit", {"producer_commit": pc, "head": head, "executor_unchanged_since_producer": True})
    ex = executor_source_identity()
    if ex["EXECUTOR_HASH"] != auth["scientific_adapter_hash"]:
        raise ProductionRefusal("live PS1 executor source is not the authorised executor")
    ok("executor_source_identity", ex["EXECUTOR_HASH"])
    for rel, key in ((auth["successor_cells_path"], "successor_cells_sha256"), (auth["live_patches_path"], "live_patches_sha256"),
                     (auth["protocol_path"], "ps1_protocol_sha256")):
        if _sha256(ROOT / rel) != auth[key]:
            raise ProductionRefusal(f"{rel} identity drift")
    ok("ps1_identities", {k: auth[k] for k in ("successor_cells_sha256", "live_patches_sha256", "ps1_protocol_sha256")})
    owners = M.gate_shards(M.load_shard_manifest(SHARD_MANIFEST, auth["shard_manifest_sha256"]))
    manifest = json.loads(SHARD_MANIFEST.read_text())
    flat = [c for g in manifest["groups"] for c in g]
    if sorted(flat) != list(range(M.TOTAL_CELLS)) or len(set(flat)) != len(flat):
        raise ProductionRefusal("cell groups do not partition the PS1 universe exactly once")
    ok("shard_manifest", {"cells": len(owners), "groups": len(manifest["groups"])})
    if probe:
        pr = _probe(auth, role)
        if pr["precision_inside_scientific_context"] != 256 or not pr["thread_contract_ok"]:
            raise ProductionRefusal(f"worker contract probe failed: {pr}")
        M.gate_runtime_hash(role, pr["runtime"]["sha256"])
        ok("fresh_interpreter_precision_256_and_runtime", {"runtime_sha256": pr["runtime"]["sha256"]})
    budget = GB.GlobalBudget(Path(budget_path or PRODUCTION_LEDGER), M.validate_governed_cost, M.gate_global_cap,
                             overhead_cpu_h=auth["governed_overhead_cpu_h"], cap_cpu_h=M.validate_governed_cap(M.GLOBAL_CPU_CAP))
    st = budget.status()
    ok("global_cap", st["cap"])
    owned = sorted(c for c, r in owners.items() if r == role)
    done = set(st["completed_cells"])
    pending = [c for c in owned if c not in done]
    pf = {"auth": auth, "role": role, "budget": budget, "owners": owners, "owned": owned, "pending": pending,
          "groups": manifest["groups"], "trace": trace, "root": ROOT,
          "active": {"active_host": auth["active_host"], "reason": "PS1 production authorization"},
          "production": {"authorization_hash": authorization_hash(), "production_closure_sha256": production_closure_hash(),
                         "scientific_adapter_hash": auth["scientific_adapter_hash"], "production_dir": str(PRODUCTION_DIR),
                         "production_ledger": str(budget.path), "production_ledger_schema": PRODUCTION_LEDGER_SCHEMA,
                         "genuine_cells_completed": len(done)},
          "READY": True}
    return pf


def admit_cell(pf, cell_id, *, reservation_cpu_h=None) -> str:
    auth, role, budget = pf["auth"], pf["role"], pf["budget"]
    if pf["active"]["active_host"] != role:
        raise ProductionRefusal(f"{role} is not the active host")
    M.gate_cell_ownership(role, cell_id, pf["owners"])
    if cell_id not in pf["pending"]:
        raise ProductionRefusal(f"cell {cell_id} is not pending for {role}")
    res = M.validate_governed_cost(reservation_cpu_h if reservation_cpu_h is not None
                                   else auth["hosts"][role]["per_cell_reservation_cpu_h"], "cell reservation")
    return budget.draw(role, cell_id, res)


class Pool:
    """16 persistent workers, one per physical core, file-protocol only."""

    def __init__(self, auth, role, workdir: Path, run_tag: str, ready_timeout=600.0):
        host = auth["hosts"][role]
        self.slots = []
        self.root = Path(workdir) / run_tag
        self.root.mkdir(parents=True, exist_ok=False)
        for k, core in enumerate(host["core_assignment"]):
            d = self.root / f"slot_{k:02d}"
            d.mkdir()
            log = open(d / "worker.log", "ab")
            p = subprocess.Popen([host["python"], str(HERE / "ps1_pool_worker.py"), "--slot", str(k), "--core", str(core),
                                  "--workdir", str(d)], env=worker_env(auth, role), cwd=str(ROOT), stdout=log,
                                 stderr=subprocess.STDOUT)
            self.slots.append({"k": k, "core": core, "dir": d, "proc": p, "task": None})
        t_end = time.monotonic() + ready_timeout
        while not all((s["dir"] / "ready.json").exists() for s in self.slots):
            self.check_alive()
            if time.monotonic() > t_end:
                raise PoolWorkerLost("pool workers did not become ready")
            time.sleep(0.5)

    def check_alive(self):
        dead = [s["k"] for s in self.slots if s["proc"].poll() is not None]
        if dead:
            raise PoolWorkerLost(f"pool worker(s) {dead} died")

    def idle(self):
        return [s for s in self.slots if s["task"] is None]

    def submit(self, slot, task):
        slot["task"] = task
        _atomic_write(slot["dir"] / "task.json", M.canonical(task))

    def get(self, timeout=None):
        t_end = None if timeout is None else time.monotonic() + timeout
        while True:
            self.check_alive()
            for s in self.slots:
                if s["task"] is not None and (s["dir"] / "result.json").exists():
                    res = json.loads((s["dir"] / "result.json").read_text())
                    os.replace(s["dir"] / "result.json", s["dir"] / f"result_{res.get('task_id')}.json")
                    task, s["task"] = s["task"], None
                    if res.get("task_id") != task["task_id"]:
                        raise ProductionRefusal(f"slot {s['k']} returned task {res.get('task_id')} for {task['task_id']}")
                    return task, res
            if t_end is not None and time.monotonic() > t_end:
                raise PoolWorkerLost("no result within poll timeout")
            time.sleep(2.0)

    def close(self):
        for s in self.slots:
            try:
                (s["dir"] / "STOP").write_text("stop\n")
            except OSError:
                pass
        t_end = time.monotonic() + 30
        while time.monotonic() < t_end and any(s["proc"].poll() is None for s in self.slots):
            time.sleep(0.5)
        for s in self.slots:
            if s["proc"].poll() is None:
                s["proc"].kill()
                s["proc"].wait()


def _verified(r, cell, task) -> bool:
    """Re-read every evidence file from disk and re-verify it; never trust the worker's summary alone."""
    if not isinstance(r, dict) or r.get("cell_id") != cell or r.get("ok") is not True or r.get("precision_bits") != 256:
        return False
    ev = r.get("evidence") or {}
    if set(ev) != {"t3", "t4", "t5", "patches_gz"}:
        return False
    for k, v in ev.items():
        p = Path(v["path"])
        if not str(p).startswith(task["evidence_dir"]) or not p.exists() or _sha256(p) != v["sha256"]:
            return False
    t5 = json.loads(Path(ev["t5"]["path"]).read_text())
    t4 = json.loads(Path(ev["t4"]["path"]).read_text())
    t3 = json.loads(Path(ev["t3"]["path"]).read_text())
    if not (t3["T3_PASS"] and t5["status"] == "T5_28_OF_28_PASS" and t5["pass_count"] == 28 and t5["total"] == 28
            and all(o["status"] == "PASS" for o in t5["obligations"]) and t5["obligation_ids_equal_frozen_universe"]
            and t5["provenance_chain_verified"] and t5["cell"] == cell and t4["cell"] == cell and t3["cell"] == cell):
        return False
    sch = hashlib.sha256(M.canonical({"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
                                      "t5_certificate_hashes": [o["certificate_hash"] for o in t5["obligations"]]}) + b"\n").hexdigest()
    return sch == r.get("scientific_content_hash")


# ------------------------------------------------- the result-bearing loop
def run_production_cells(pf, *, max_cells=None, poll_timeout=None) -> dict:
    """GENUINE PS1 SR production. Never invoked by any test in this namespace."""
    auth, role, budget = pf["auth"], pf["role"], pf["budget"]
    ah = authorization_hash()
    adapter = auth["scientific_adapter_hash"]
    if executor_source_identity(pf["root"])["EXECUTOR_HASH"] != adapter:
        raise ProductionRefusal("live PS1 executor is not the authorised executor")
    run_tag = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + f"-{os.getpid()}"
    host = auth["hosts"][role]
    pool = Pool(auth, role, Path(host["work_dir"]), run_tag)
    pend = set(pf["pending"] if max_cells is None else pf["pending"][:max_cells])
    groups = [g2 for g2 in ([c for c in g if c in pend] for g in pf["groups"]) if g2]
    inflight, done, stopped = {}, [], None
    try:
        while groups or inflight:
            while groups and pool.idle():
                grp = groups[0]
                drawn = []
                for cell in grp:
                    try:
                        key = admit_cell(pf, cell)
                    except (GB.BudgetRefusal, M.MultiHostRefusal) as exc:
                        stopped = f"admission stopped: {exc}"
                        break
                    inflight[cell] = key
                    drawn.append(cell)
                groups.pop(0) if len(drawn) == len(grp) else None
                if stopped:
                    groups = []
                if drawn:
                    tid = f"{run_tag}-g{drawn[0]:04d}"
                    pool.submit(pool.idle()[0], {"task_id": tid, "cells": drawn,
                                                 "evidence_dir": str(Path(host["evidence_dir"]) / run_tag / f"g{drawn[0]:04d}"),
                                                 "live_patches": str(ROOT / auth["live_patches_path"]),
                                                 "live_patches_sha256": auth["live_patches_sha256"],
                                                 "expect_patches": auth["live_patches_count"],
                                                 "successor_cells_sha256": auth["successor_cells_sha256"]})
                if stopped:
                    break
            if not inflight:
                break
            task, rec = pool.get(timeout=poll_timeout)
            for cell in task["cells"]:
                key = inflight.pop(cell)
                if not rec.get("ok"):
                    budget.release(key); continue
                r = rec.get("results", {}).get(str(cell))
                if not _verified(r, cell, task):
                    budget.release(key)
                    raise ProductionRefusal(f"cell {cell}: result failed re-verification from disk")
                M.gate_cell_ownership(role, cell, pf["owners"])
                actual = M.validate_governed_cost(r["cpu_seconds"] / 3600.0, "actual cell CPU-h")
                record = {"cell_id": cell, "role": role, "producer_commit": auth["producer_commit"],
                          "checkpoint_sha256": auth["checkpoint_sha256"],
                          "runtime_contract_hash": auth["runtime_contract_hashes"][role],
                          "scientific_content_hash": r["scientific_content_hash"], "cpu_seconds": actual * 3600.0,
                          "obligations_completed": 28, "complete": True, "successor_id": r["successor_id"],
                          "B_cover_ratio": r["B_cover_ratio"], "evidence": r["evidence"], "task_id": task["task_id"],
                          "precision_bits": 256}
                M.validate_record(record, role, pf["owners"], auth["producer_commit"], auth["checkpoint_sha256"])
                sealed = PP.seal(record, production_authorization_hash=ah, scientific_adapter_hash=adapter,
                                 certificate_digest=r["evidence"]["t5"]["sha256"])
                PP.verify(sealed, production_authorization_hash=ah, scientific_adapter_hash=adapter)
                out = gate_production_result_path(PRODUCTION_DIR / "cells" / f"{cell:04d}.json")
                gate_no_evidence_collision([out])
                _atomic_write(out, (json.dumps(sealed, indent=1, sort_keys=True) + "\n").encode())
                budget.commit(key, actual, sealed)
                done.append(cell)
    finally:
        for k in inflight.values():
            budget.release(k)
        pool.close()
    return {"completed": done, "stopped": stopped, "status": budget.status()}


def assemble_production_campaign(pf, host_ledgers) -> dict:
    """Final assembly over the single AWS ledger: every PS1 cell present exactly once and COMPLETE."""
    owners = pf["owners"]
    recs = host_ledgers.get("AWS", [])
    for rec in recs:
        M.validate_record(rec, "AWS", owners, pf["auth"]["producer_commit"], pf["auth"]["checkpoint_sha256"])
    ids = sorted(r["cell_id"] for r in recs)
    if ids != list(range(M.TOTAL_CELLS)):
        raise ProductionRefusal(f"assembly incomplete: {len(ids)}/{M.TOTAL_CELLS} cells")
    return {"cells": len(ids), "obligations": 28 * len(ids), "cpu_h": M.per_host_cpu_h(recs),
            "far_field": pf["auth"]["far_field_obligation"]}
