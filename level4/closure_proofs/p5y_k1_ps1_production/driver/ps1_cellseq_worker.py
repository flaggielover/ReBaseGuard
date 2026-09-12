"""PS1 persistent pool worker (NEW; fixes every historical production-adapter defect).

One long-lived process per PHYSICAL core, alive for the whole run (the lifecycle supervisor treats fewer live
children than `workers` while a reservation is open as WORKER_LOST). Communication is by ATOMIC JSON FILES only:
no multiprocessing Queue (no silent feeder loss) and no python-flint Arb object ever crosses a process boundary.

Per task (one deterministic cell GROUP): every one of the 3,994 frozen live patches, CELLS-OUTER / PATCH-INNER with a per-cell
shared per-patch panel cache, through the production per-patch function (generated opt_core.core: the frozen
certifier with the bit-identical OPT-S/OPT-C memoisation), all at the frozen 256-bit precision; then, per cell, the
committed successor T3 aggregation (midpoint + governed mean-value cell mode), T4 and T5. A cell is reported ok ONLY if
T3_PASS, T5 status T5_28_OF_28_PASS with 28/28, the obligation unit structure equals the frozen parent's and the
provenance chain verifies. Any exception is reported as a worker failure (the protocol never retries science).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import platform
import resource
import sys
import time
from pathlib import Path

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
               "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
FROZEN_BITS = 256


def canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def sha256_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path = Path(path)
    tmp = path.with_name(f".tmp-{path.name}-{os.getpid()}")
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


def runtime_fingerprint() -> dict:
    import flint
    import numpy
    cfg = numpy.show_config(mode="dicts") if "mode" in numpy.show_config.__code__.co_varnames else {}
    blas = (cfg.get("Build Dependencies", {}) or {}).get("blas", {}) if isinstance(cfg, dict) else {}
    fp = {"python": platform.python_version(), "implementation": platform.python_implementation(),
          "machine": platform.machine(), "python_flint": flint.__version__, "numpy": numpy.__version__,
          "blas": {k: blas.get(k) for k in ("name", "version")},
          "thread_environment": {v: os.environ.get(v) for v in THREAD_VARS}}
    return {"fingerprint": fp, "sha256": hashlib.sha256(canonical(fp)).hexdigest()}


def probe() -> dict:
    """Fresh-interpreter contract probe: thread contract, precision inside the scientific context, runtime identity."""
    import sr_o9_candidates as T
    from flint import ctx
    outside = ctx.prec
    with T.scientific_precision():
        inside = ctx.prec
        T.require_precision()
    return {"precision_inside_scientific_context": inside, "precision_outside": outside,
            "thread_contract_ok": all(os.environ.get(v) == "1" for v in THREAD_VARS),
            "runtime": runtime_fingerprint(), "pid": os.getpid()}


def drain_pending(task: dict) -> bool:
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


def run_group(task: dict) -> dict:
    import sr_o9_candidates as T
    import sr_o9_bint_p1 as BP
    import opt_core as OC
    import succ_t3 as S3
    import succ_cells as SC
    import succ_t3_aggregate as AG
    import succ_t4 as S4
    import succ_t5 as S5
    from flint import ctx
    cells = [int(c) for c in task["cells"]]
    live = [tuple(map(int, l.split())) for l in Path(task["live_patches"]).read_text().splitlines() if l.strip()]
    if len(live) != task["expect_patches"] or hashlib.sha256(Path(task["live_patches"]).read_bytes()).hexdigest() != task["live_patches_sha256"]:
        raise RuntimeError("live patch table identity mismatch")
    if SC.table_sha256() != task["successor_cells_sha256"]:
        raise RuntimeError("successor cell table identity mismatch")
    ev = Path(task["evidence_dir"])
    ev.mkdir(parents=True, exist_ok=False)
    u0 = resource.getrusage(resource.RUSAGE_SELF)
    cpu = {s: 0.0 for s in cells}
    results = {}
    with T.scientific_precision():
        if ctx.prec != FROZEN_BITS:
            raise RuntimeError(f"worker precision {ctx.prec} != {FROZEN_BITS}")
        for s in cells:
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
                fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
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
    u1 = resource.getrusage(resource.RUSAGE_SELF)
    total = (u1.ru_utime + u1.ru_stime) - (u0.ru_utime + u0.ru_stime)
    sealed = {k: v for k, v in results.items() if k.isdigit()}
    return {"ok": all(r["ok"] for r in sealed.values()) and len(sealed) == len(cells), "results": sealed,
            "finalized_cells": sorted(int(k) for k in sealed), "drained": "drained_before_cell" in results,
            "cpu_seconds_group": total, "precision_bits": FROZEN_BITS}


def synthetic_spin(task: dict) -> dict:
    """ACCEPTANCE-TEST ONLY: burn CPU for task['seconds'] and report task['verdict']. It produces no scientific
    evidence, so the production launcher's from-disk verification can never accept it as a cell."""
    t_end = time.process_time() + float(task["seconds"])
    x = 0
    while time.process_time() < t_end:
        x += 1
    return {"ok": task.get("verdict", True) is True, "results": {}, "synthetic": True, "cpu_seconds_group": float(task["seconds"])}


def synthetic_cellseq(task: dict) -> dict:
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--slot", type=int)
    ap.add_argument("--core", type=int)
    ap.add_argument("--workdir")
    a = ap.parse_args(argv)
    if a.probe:
        sys.stdout.write(canonical(probe()).decode())
        return 0
    if not all(os.environ.get(v) == "1" for v in THREAD_VARS):
        return 3
    os.sched_setaffinity(0, {a.core})
    work = Path(a.workdir)
    work.mkdir(parents=True, exist_ok=True)
    pr = probe()
    if pr["precision_inside_scientific_context"] != FROZEN_BITS or not pr["thread_contract_ok"]:
        return 4
    atomic_write(work / "ready.json", canonical({"slot": a.slot, "core": a.core, "affinity": sorted(os.sched_getaffinity(0)), **pr}))
    while True:
        if (work / "STOP").exists():
            return 0
        t = work / "task.json"
        if not t.exists():
            time.sleep(1.0)
            continue
        task = json.loads(t.read_text())
        try:
            kind = task.get("kind")
            if kind == "SYNTHETIC_CELLSEQ":
                res = synthetic_cellseq(task)
            elif kind == "SYNTHETIC_SPIN":
                res = synthetic_spin(task)
            else:
                res = run_group(task)
        except Exception as exc:                          # noqa: BLE001  (reported, never retried: science halts)
            res = {"ok": False, "results": {}, "error": f"{type(exc).__name__}: {exc}"[:2000]}
        res["task_id"] = task["task_id"]
        res["slot"] = a.slot
        atomic_write(work / "result.json", canonical(res))
        os.replace(t, work / f"done_{task['task_id']}.json")


if __name__ == "__main__":
    raise SystemExit(main())
