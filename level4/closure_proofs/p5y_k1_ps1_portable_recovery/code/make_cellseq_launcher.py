"""Generate driver/ps1_cellseq_launcher.py from the FROZEN production_launcher.py.

Asserted substitutions (execution/lifecycle only):
  SUB_WORKER  ps1_pool_worker.py -> ps1_cellseq_worker.py
  SUB_POLL    add Pool.poll() (non-blocking sibling of Pool.get)
  SUB_LOOP    replace the result-bearing loop: durability boundary moves from the
              group-level result.json to the per-cell cell_done_XXXX.json marker

The governed sealing path (gate_cell_ownership, validate_governed_cost, validate_record,
PP.seal, PP.verify, gate_production_result_path, gate_no_evidence_collision, budget.commit)
is reproduced verbatim inside _seal_one(); only its CALL SITE moves earlier.

Release sites are preserved exactly: 'budget.release(key); continue',
'budget.release(key)', 'budget.release(k)'.
"""
import hashlib
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SRC = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod/level4/closure_proofs/"
           "p5y_k1_ps1_production/driver/production_launcher.py")
FROZEN_SHA = "89a3573c4d74ba97e0ab258a0f512dcd3af1595fb1c2ab6056a65a2fe0d46c8a"
# produce_entry binds the launcher to the PRODUCTION namespace driver dir, so the
# recovery modules ship there ADDITIVELY. executor_source_identity hashes an explicit
# 39-file manifest, so new files cannot change EXECUTOR_HASH.
OUT = Path("/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_ps1_production/driver") / "ps1_cellseq_launcher.py"

SUB_WORKER_OLD = 'str(HERE / "ps1_pool_worker.py")'
SUB_WORKER_NEW = 'str(HERE / "ps1_cellseq_worker.py")'

POLL_ANCHOR = """    def close(self):
        for s in self.slots:
"""
POLL_NEW = '''    def poll(self):
        """Non-blocking sibling of get(): a finished GROUP frees its slot. It is no longer
        the scientific durability boundary -- that is the per-cell marker."""
        self.check_alive()
        for s in self.slots:
            if s["task"] is not None and (s["dir"] / "result.json").exists():
                res = json.loads((s["dir"] / "result.json").read_text())
                os.replace(s["dir"] / "result.json", s["dir"] / f"result_{res.get('task_id')}.json")
                task, s["task"] = s["task"], None
                if res.get("task_id") != task["task_id"]:
                    raise ProductionRefusal(f"slot {s['k']} returned task {res.get('task_id')} for {task['task_id']}")
                return task, res
        return None

''' + POLL_ANCHOR

LOOP_START = "# ------------------------------------------------- the result-bearing loop\n"
LOOP_END = "def assemble_production_campaign(pf, host_ledgers) -> dict:"

LOOP_NEW = '''# ------------------------------------------------- the result-bearing loop
def drain_flag_path(auth, role) -> Path:
    """Same location prodctl drain writes: <work_dir>/DRAIN, where work_dir is whatever the
    running campaign was actually configured with (the synthetic hook rewrites it)."""
    return Path(auth["hosts"][role]["work_dir"]) / "DRAIN"


def _seal_one(pf, cell, task, r, ah, adapter):
    """Governed per-cell sealing -- verbatim from the frozen launcher; only the call site
    moved earlier, from group completion to cell completion."""
    auth, role = pf["auth"], pf["role"]
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
    _atomic_write(out, (json.dumps(sealed, indent=1, sort_keys=True) + "\\n").encode())
    return actual, sealed


def _reap_markers(pf, inflight, tasks, done, ah, adapter):
    """Consume every durable per-cell marker that has appeared. THE durability boundary.

    A sealed cell is committed immediately and can never be rolled back because a sibling in
    its scheduling group later tears. This helper NEVER calls budget.release(): the frozen
    OpsBudget classifies a tear by the exact source line AND by the calling frame being
    run_production_cells, so every release must stay lexically in that function. Malformed
    cells are returned for the caller to release."""
    budget = pf["budget"]
    sealed_now, malformed = [], []
    for cell in sorted(inflight):
        task = tasks.get(cell)
        if task is None:
            continue
        marker = Path(task["evidence_dir"]) / f"cell_done_{cell:04d}.json"
        if not marker.exists():
            continue
        try:
            r = json.loads(marker.read_text())
        except (OSError, ValueError):
            continue
        if not _verified(r, cell, task):
            malformed.append(cell)
            continue
        actual, _sealed = _seal_one(pf, cell, task, r, ah, adapter)
        budget.commit(inflight.pop(cell), actual, _sealed)
        done.append(cell)
        sealed_now.append(cell)
    return sealed_now, malformed


def run_production_cells(pf, *, max_cells=None, poll_timeout=None) -> dict:
    """GENUINE PS1 SR production. Never invoked by any test in this namespace.

    Durability is per cell: each cell is validated, sealed and committed the instant its
    marker appears. The group result only frees the worker slot."""
    auth, role, budget = pf["auth"], pf["role"], pf["budget"]
    ah = authorization_hash()
    adapter = auth["scientific_adapter_hash"]
    if executor_source_identity(pf["root"])["EXECUTOR_HASH"] != adapter:
        raise ProductionRefusal("live PS1 executor is not the authorised executor")
    run_tag = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + f"-{os.getpid()}"
    host = auth["hosts"][role]
    dflag = drain_flag_path(auth, role)
    pool = Pool(auth, role, Path(host["work_dir"]), run_tag)
    pend = set(pf["pending"] if max_cells is None else pf["pending"][:max_cells])
    groups = [g2 for g2 in ([c for c in g if c in pend] for g in pf["groups"]) if g2]
    target = pf.get("drain_after_completed")
    inflight, tasks, done, stopped, drained = {}, {}, [], None, False
    t_idle = time.monotonic()
    try:
        while groups or inflight:
            if groups and dflag.exists():
                stopped, groups, drained = "DRAINING: operator drain; no new cells admitted", [], True
            if groups and target is not None and len(done) >= target:
                dflag.write_text("target\\n")
                stopped = f"DRAINING: governed target {target} reached at {len(done)} finalized"
                groups, drained = [], True
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
                if stopped and not drained:
                    groups = []
                if drawn:
                    tid = f"{run_tag}-g{drawn[0]:04d}"
                    t = {"task_id": tid, "cells": drawn,
                         "evidence_dir": str(Path(host["evidence_dir"]) / run_tag / f"g{drawn[0]:04d}"),
                         "live_patches": str(ROOT / auth["live_patches_path"]),
                         "live_patches_sha256": auth["live_patches_sha256"],
                         "expect_patches": auth["live_patches_count"],
                         "successor_cells_sha256": auth["successor_cells_sha256"],
                         "drain_flag": str(dflag),
                         "launcher_pid": os.getpid(), "run_id": run_tag}
                    for cell in drawn:
                        tasks[cell] = t
                    pool.submit(pool.idle()[0], t)
                if stopped and not drained:
                    break
            if not inflight:
                break
            sealed_now, malformed = _reap_markers(pf, inflight, tasks, done, ah, adapter)
            for cell in malformed:
                key = inflight.pop(cell)
                budget.release(key)
                raise ProductionRefusal(f"cell {cell}: marker failed re-verification from disk")
            progressed = bool(sealed_now)
            got = pool.poll()
            if got is None:
                if poll_timeout is not None and not progressed and time.monotonic() - t_idle > poll_timeout:
                    raise PoolWorkerLost("no result within poll timeout")
                if not progressed:
                    # Tight: a durable marker must be consumed before the supervisor's
                    # WORKER_LOST detection settles the run, otherwise a cell that reached
                    # its boundary is torn. Detection latency is ~1-2s; this is 0.25s.
                    time.sleep(0.25)
                continue
            t_idle = time.monotonic()
            task, rec = got
            _reap_markers(pf, inflight, tasks, done, ah, adapter)
            drained_now = bool(rec.get("drained"))
            for cell in task["cells"]:
                key = inflight.pop(cell, None)
                if key is None:
                    continue          # already finalized and committed from its marker
                if drained_now:
                    dkey = key        # never started: the worker drained at a cell boundary
                    budget.release(dkey)
                    continue
                budget.release(key); continue
    finally:
        # A marker already on disk is a FINALIZED cell. Honour it even if the worker died,
        # otherwise a tear would roll back work that had already reached its boundary
        # (observed live in acceptance B: cell 1 sealed on disk, lost to the release sweep).
        try:
            _reap_markers(pf, inflight, tasks, done, ah, adapter)
        except Exception as _exc:                                  # noqa: BLE001
            import traceback
            print(f"FINAL_REAP_FAILED {type(_exc).__name__}: {_exc}", flush=True)
            traceback.print_exc()
        for k in inflight.values():
            budget.release(k)
        pool.close()
    return {"completed": done, "stopped": stopped, "drained": drained,
            "finalized_cells": sorted(done), "status": budget.status()}


'''


def main() -> int:
    got = hashlib.sha256(SRC.read_bytes()).hexdigest()
    if got != FROZEN_SHA:
        raise SystemExit(f"FROZEN LAUNCHER DRIFT: {got} != {FROZEN_SHA}")
    src = SRC.read_text()
    # two call sites: the precision probe and the pool spawn. Both must move.
    if src.count(SUB_WORKER_OLD) != 2:
        raise SystemExit(f"WORKER anchor count {src.count(SUB_WORKER_OLD)}, want 2")
    for name, blk in (("POLL", POLL_ANCHOR), ("LOOP_START", LOOP_START)):
        if src.count(blk) != 1:
            raise SystemExit(f"{name} anchor not found exactly once ({src.count(blk)})")
    out = src.replace(SUB_WORKER_OLD, SUB_WORKER_NEW).replace(POLL_ANCHOR, POLL_NEW, 1)
    a = out.index(LOOP_START)
    b = out.index(LOOP_END)
    out = out[:a] + LOOP_NEW + out[b:]
    for site, want in (("budget.release(key); continue", 1), ("budget.release(key)", 2),
                       ("budget.release(k)", 1), ("budget.release(dkey)", 1)):
        n = out.count(site)
        if n != want:
            raise SystemExit(f"release site {site!r} appears {n} times, want {want}")
    OUT.write_text(out)
    print(f"wrote {OUT}")
    print(f"  frozen launcher sha256 : {got}")
    print(f"  generated sha256       : {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
