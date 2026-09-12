"""Generate driver/ps1_cellseq_worker.py from the FROZEN ps1_pool_worker.py.

EXECUTION-ONLY transform, as ONE whole-block asserted substitution plus a helper insert.
If the frozen source drifts by a single byte, the sha256 gate or the verbatim block
assertion fails and nothing is written.

Every scientific call is reproduced byte-for-byte: S3.cell_inputs, OC.core with identical
arguments, the identical record dict and canonical serialisation, AG.aggregate, S4.t4,
S5.obligations, the identical ok-gate and scientific_content_hash.

Why this cannot change science (RESULT Phase A): succ_t3_aggregate.aggregate() strips
cpu_seconds, peak_rss_kib, cache_hits and cache_misses from every record before
consumed_records_sha256 / t3_record_sha256 are computed. Those four fields are the ONLY
values loop order or cache warmth can touch.

Cost: the cross-cell per-patch cache is lost, so each cell pays the cache-builder cost
(14.98 CPU-h) instead of the grouped 11.96-12.58. Predeclared, not discovered.
"""
import hashlib
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SRC = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod/level4/closure_proofs/"
           "p5y_k1_ps1_production/driver/ps1_pool_worker.py")
FROZEN_SHA = "c5e9e1c35961f18dd17f686a2576ce1f51b698cacffce5e4708a9d4b8cfcd6bb"
# produce_entry binds the launcher to the PRODUCTION namespace driver dir, so the
# recovery modules ship there ADDITIVELY. executor_source_identity hashes an explicit
# 39-file manifest, so new files cannot change EXECUTOR_HASH.
OUT = Path("/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1_ps1_production/driver") / "ps1_cellseq_worker.py"

ANCHOR = "def run_group(task: dict) -> dict:\n"
HELPERS = '''def drain_pending(task: dict) -> bool:
    """DRAIN is cooperative and checked ONLY at a cell boundary, never mid-cell. A cell
    that reaches its boundary under drain is FINALIZED, not torn."""
    f = task.get("drain_flag")
    return bool(f) and Path(f).exists()


MARKER_SCHEMA = "rebaseguard.p5y.k1.ps1.cell-done-marker.v1"


def _seal_cell(ev: Path, s: int, result: dict, task: dict) -> None:
    """THE durability point. A write-ahead completion fact.

    All scientific evidence for cell s is already flushed+fsynced above. atomic_write then
    writes the marker to a .tmp- name, fsyncs its contents, atomically renames it to the
    final cell_done_XXXX.json and fsyncs the containing directory -- so only a complete,
    durable marker can ever carry the final name. A truncated or .tmp- file never qualifies.

    The marker BINDS identity so it can never be replayed across runs: schema, cell, task,
    launcher pid (the supervisor matches this against its own child pid), evidence hashes
    and the scientific content hash."""
    m = dict(result)
    m.update({"marker_schema": MARKER_SCHEMA, "cell_id": s,
              "task_id": task.get("task_id"), "launcher_pid": task.get("launcher_pid"),
              "run_id": task.get("run_id"), "evidence_dir": str(ev),
              "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    atomic_write(ev / f"cell_done_{s:04d}.json", canonical(m))


''' + ANCHOR

OLD = '''        inp = {}
        for s in cells:
            t0 = time.process_time()
            inp[s] = S3.cell_inputs(s)
            cpu[s] += time.process_time() - t0
        files = {s: ev / f"patches_{s:04d}.jsonl" for s in cells}
        fhs = {s: open(files[s], "w") for s in cells}
        for (i, j) in live:
            cache = {}
            for s in cells:
                cands, hashes, C, e0, clsha = inp[s]
                t0 = time.process_time()
                rec = {"schema": S3.SCHEMA, "successor_cell": s, "successor_cells_sha256": SC.table_sha256(), "patch": [i, j],
                       "candidate_identity_list_sha256": clsha, "modes": {}}
                with BP.p1_lagrange_factor():
                    nodes, geo, st = OC.core(i, j, e0, cands, cand_hashes=hashes, C_gate=C, shared_cache=cache, mode="mid")
                rec["modes"]["mid"] = {"nodes": nodes, "geo": geo, "cache_hits": st["hits"], "cache_misses": st["misses"]}
                dt = time.process_time() - t0
                rec["cpu_seconds"] = dt
                rec["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                fhs[s].write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\\n")
                cpu[s] += dt
        for fh in fhs.values():
            fh.flush()
            os.fsync(fh.fileno())
            fh.close()
        for s in cells:
            t0 = time.process_time()
            rec_cell = SC.cell(s)
            t3 = AG.aggregate(s, [str(files[s])])
            atomic_write(ev / f"t3_{s:04d}.json", AG.canonical(t3))
            t4 = S4.t4(t3, rec_cell)
            atomic_write(ev / f"t4_{s:04d}.json", S4.canonical(t4))
            evd = {"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
                   "t3_file_sha256": sha256_file(ev / f"t3_{s:04d}.json"), "t4_file_sha256": sha256_file(ev / f"t4_{s:04d}.json"),
                   "successor_cells_sha256": SC.table_sha256(), "task_id": task["task_id"]}
            t5 = S5.obligations(t3, t4, evd, rec_cell)
            atomic_write(ev / f"t5_{s:04d}.json", S5.canonical(t5))
            gz = ev / f"patches_{s:04d}.jsonl.gz"
            with open(files[s], "rb") as src, open(gz, "wb") as raw:
                with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as z:
                    z.write(src.read())
                raw.flush()
                os.fsync(raw.fileno())
            os.unlink(files[s])
            cpu[s] += time.process_time() - t0
            ok = bool(t3["T3_PASS"] and t5["status"] == "T5_28_OF_28_PASS" and t5["pass_count"] == 28 and t5["total"] == 28
                      and t5["obligation_ids_equal_frozen_universe"] and t5["provenance_chain_verified"])
            sch = hashlib.sha256(canonical({"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
                                            "t5_certificate_hashes": [o["certificate_hash"] for o in t5["obligations"]]})).hexdigest()
            results[str(s)] = {"cell_id": s, "successor_id": rec_cell["id"], "ok": ok, "T3_PASS": t3["T3_PASS"],
                               "t5_status": t5["status"], "pass_count": t5["pass_count"], "total": t5["total"],
                               "B_cover_ratio": t4["B_cover_ratio"], "scientific_content_hash": sch,
                               "evidence": {k: {"path": str(ev / n), "sha256": sha256_file(ev / n)} for k, n in
                                            (("t3", f"t3_{s:04d}.json"), ("t4", f"t4_{s:04d}.json"), ("t5", f"t5_{s:04d}.json"),
                                             ("patches_gz", f"patches_{s:04d}.jsonl.gz"))},
                               "cpu_seconds": cpu[s], "precision_bits": FROZEN_BITS}
'''

NEW = '''        for s in cells:
            if drain_pending(task):
                results["drained_before_cell"] = s
                break
            t0 = time.process_time()
            cands, hashes, C, e0, clsha = S3.cell_inputs(s)
            cpu[s] += time.process_time() - t0
            f_s = ev / f"patches_{s:04d}.jsonl"
            fh = open(f_s, "w")
            for (i, j) in live:
                cache = {}
                t0 = time.process_time()
                rec = {"schema": S3.SCHEMA, "successor_cell": s, "successor_cells_sha256": SC.table_sha256(), "patch": [i, j],
                       "candidate_identity_list_sha256": clsha, "modes": {}}
                with BP.p1_lagrange_factor():
                    nodes, geo, st = OC.core(i, j, e0, cands, cand_hashes=hashes, C_gate=C, shared_cache=cache, mode="mid")
                rec["modes"]["mid"] = {"nodes": nodes, "geo": geo, "cache_hits": st["hits"], "cache_misses": st["misses"]}
                dt = time.process_time() - t0
                rec["cpu_seconds"] = dt
                rec["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\\n")
                cpu[s] += dt
            fh.flush()
            os.fsync(fh.fileno())
            fh.close()
            t0 = time.process_time()
            rec_cell = SC.cell(s)
            t3 = AG.aggregate(s, [str(f_s)])
            atomic_write(ev / f"t3_{s:04d}.json", AG.canonical(t3))
            t4 = S4.t4(t3, rec_cell)
            atomic_write(ev / f"t4_{s:04d}.json", S4.canonical(t4))
            evd = {"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
                   "t3_file_sha256": sha256_file(ev / f"t3_{s:04d}.json"), "t4_file_sha256": sha256_file(ev / f"t4_{s:04d}.json"),
                   "successor_cells_sha256": SC.table_sha256(), "task_id": task["task_id"]}
            t5 = S5.obligations(t3, t4, evd, rec_cell)
            atomic_write(ev / f"t5_{s:04d}.json", S5.canonical(t5))
            gz = ev / f"patches_{s:04d}.jsonl.gz"
            with open(f_s, "rb") as src, open(gz, "wb") as raw:
                with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as z:
                    z.write(src.read())
                raw.flush()
                os.fsync(raw.fileno())
            os.unlink(f_s)
            cpu[s] += time.process_time() - t0
            ok = bool(t3["T3_PASS"] and t5["status"] == "T5_28_OF_28_PASS" and t5["pass_count"] == 28 and t5["total"] == 28
                      and t5["obligation_ids_equal_frozen_universe"] and t5["provenance_chain_verified"])
            sch = hashlib.sha256(canonical({"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
                                            "t5_certificate_hashes": [o["certificate_hash"] for o in t5["obligations"]]})).hexdigest()
            results[str(s)] = {"cell_id": s, "successor_id": rec_cell["id"], "ok": ok, "T3_PASS": t3["T3_PASS"],
                               "t5_status": t5["status"], "pass_count": t5["pass_count"], "total": t5["total"],
                               "B_cover_ratio": t4["B_cover_ratio"], "scientific_content_hash": sch,
                               "evidence": {k: {"path": str(ev / n), "sha256": sha256_file(ev / n)} for k, n in
                                            (("t3", f"t3_{s:04d}.json"), ("t4", f"t4_{s:04d}.json"), ("t5", f"t5_{s:04d}.json"),
                                             ("patches_gz", f"patches_{s:04d}.jsonl.gz"))},
                               "cpu_seconds": cpu[s], "precision_bits": FROZEN_BITS}
            _seal_cell(ev, s, results[str(s)], task)
'''

SYNTH_OLD = '            res = synthetic_spin(task) if task.get("kind") == "SYNTHETIC_SPIN" else run_group(task)\n'
SYNTH_NEW = '''            kind = task.get("kind")
            if kind == "SYNTHETIC_CELLSEQ":
                res = synthetic_cellseq(task)
            elif kind == "SYNTHETIC_SPIN":
                res = synthetic_spin(task)
            else:
                res = run_group(task)
'''

SYNTH_FN_ANCHOR = "def main(argv=None) -> int:\n"
SYNTH_FN = '''def synthetic_cellseq(task: dict) -> dict:
    """ACCEPTANCE-TEST ONLY. Mirrors run_group's cells-outer shape -- spin one cell, seal that
    cell's durable marker, check drain at the boundary, repeat -- while producing NO scientific
    evidence. Every record is stamped synthetic=True, which the PRODUCTION _verified() rejects
    outright; only the SYNTHETIC_CONTROL entry's patched _verified accepts it."""
    ev = Path(task["evidence_dir"])
    ev.mkdir(parents=True, exist_ok=True)
    cells = [int(c) for c in task["cells"]]
    spin = float(task.get("seconds", 0.2))
    die_on = task.get("die_on_cell")
    results = {}
    for s in cells:
        if drain_pending(task):
            results["drained_before_cell"] = s
            break
        if die_on is not None and s == int(die_on):
            os._exit(9)                       # controlled infrastructure tear, mid-cell
        t_end = time.process_time() + spin
        x = 0
        while time.process_time() < t_end:
            x += 1
        r = {"cell_id": s, "ok": True, "synthetic": True, "successor_id": f"SYNTHETIC-{s}",
             "scientific_content_hash": hashlib.sha256(f"SYNTHETIC-CELLSEQ:{s}".encode()).hexdigest(),
             "B_cover_ratio": {}, "cpu_seconds": spin, "precision_bits": FROZEN_BITS,
             "evidence": {"t5": {"path": "SYNTHETIC_CONTROL_NOT_SCIENCE",
                                 "sha256": hashlib.sha256(f"SYN-EV:{s}".encode()).hexdigest()}}}
        # ACCEPTANCE BARRIER (before): kill the LAUNCHER before this cell's marker is
        # renamed into place. The cell must NOT be finalized by anything.
        if task.get("kill_launcher_before_cell") is not None and s == int(task["kill_launcher_before_cell"]):
            import signal as _sig
            os.kill(int(task["launcher_pid"]), _sig.SIGKILL)
            time.sleep(600)
        results[str(s)] = r
        _seal_cell(ev, s, r, task)
        # ACCEPTANCE BARRIER: the marker is now durable (fsynced + atomically renamed).
        # SIGKILL the LAUNCHER so its finally/atexit can never run. Only supervisor-side
        # reconciliation can finalize this cell.
        if task.get("kill_launcher_after_cell") is not None and s == int(task["kill_launcher_after_cell"]):
            import signal as _sig
            os.kill(int(task["launcher_pid"]), _sig.SIGKILL)
            time.sleep(600)
    sealed = {k: v for k, v in results.items() if k.isdigit()}
    return {"ok": all(v["ok"] for v in sealed.values()), "results": sealed, "synthetic": True,
            "finalized_cells": sorted(int(k) for k in sealed),
            "drained": "drained_before_cell" in results, "cpu_seconds_group": spin * len(sealed)}


''' + SYNTH_FN_ANCHOR

OK_OLD = '''    return {"ok": all(r["ok"] for r in results.values()) and len(results) == len(cells), "results": results,
'''
OK_NEW = '''    sealed = {k: v for k, v in results.items() if k.isdigit()}
    return {"ok": all(r["ok"] for r in sealed.values()) and len(sealed) == len(cells), "results": sealed,
            "finalized_cells": sorted(int(k) for k in sealed), "drained": "drained_before_cell" in results,
'''


def main() -> int:
    got = hashlib.sha256(SRC.read_bytes()).hexdigest()
    if got != FROZEN_SHA:
        raise SystemExit(f"FROZEN EXECUTOR DRIFT: {got} != {FROZEN_SHA}")
    src = SRC.read_text()
    for name, blk in (("ANCHOR", ANCHOR), ("OLD", OLD), ("OK_OLD", OK_OLD)):
        if src.count(blk) != 1:
            raise SystemExit(f"{name} block not found exactly once ({src.count(blk)})")
    for nm, blk in (("SYNTH_OLD", SYNTH_OLD), ("SYNTH_FN_ANCHOR", SYNTH_FN_ANCHOR)):
        if src.count(blk) != 1:
            raise SystemExit(f"{nm} not found exactly once ({src.count(blk)})")
    out = (src.replace(ANCHOR, HELPERS, 1).replace(OLD, NEW, 1).replace(OK_OLD, OK_NEW, 1)
              .replace(SYNTH_OLD, SYNTH_NEW, 1).replace(SYNTH_FN_ANCHOR, SYNTH_FN, 1))
    out = out.replace("patch-outer / cells-inner with one",
                      "CELLS-OUTER / PATCH-INNER with a per-cell")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out)
    print(f"wrote {OUT}")
    print(f"  frozen source sha256 : {got}")
    print(f"  generated sha256     : {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
