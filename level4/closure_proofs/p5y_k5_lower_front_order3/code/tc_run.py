"""Governed execution of the theorem-TC producer over exactly the pre-registered addresses (then the pre-registered
2-cell reproduction). Evidence is written OUTSIDE the checkout (the producer refuses a dirty namespace).

    python -B tc_run.py --protocol-sha256 SHA --evidence DIR          (workers: the protocol's frozen count)

Writes DIR/cells/TC_CELL_<k>.json, DIR/repro/TC_CELL_<k>.json, DIR/RUN_LEDGER.jsonl (START / OUTPUT / REPRO lines
with sha256, CPU seconds, head) and DIR/TC_INDEX.json. It never reads a scientific field of an output (no pass/open
inspection before the seal): it hashes files and compares reproduction bytes.
"""
from __future__ import annotations

import os
import sys as _sys

if "numpy" not in _sys.modules:                         # same thread pin as the producer (children inherit it)
    os.environ.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                       "NUMEXPR_NUM_THREADS": "1"})
    os.environ["K1_THREADS_PINNED"] = "1"

import argparse
import concurrent.futures as cf
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
PY = sys.executable
RECORDS = Path("/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
REPRO = (11, 44)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def one(k: int, proto_sha: str, rec_sha: str, out: Path) -> dict:
    cmd = [PY, "-B", str(NS / "code/tc_producer.py"), "real", "--cell", str(k),
           "--record", str(RECORDS / f"aux5_CUSUM_{k}_256.json"), "--record-sha256", rec_sha,
           "--protocol-sha256", proto_sha, "--out", str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return {"cell": k, "ok": False, "stderr": p.stderr[-2000:]}
    meta = json.loads(p.stdout.strip().splitlines()[-1])
    return {"cell": k, "ok": True, "sha256": sha(out), "cpu_seconds": meta["cpu_seconds"],
            "peak_rss_kib": meta["peak_rss_kib"]}


def preflight(proto: dict, protocol_sha256: str, ev: Path) -> list[str]:
    """Review r3 N-R3-1: everything that would make every producer call refuse, checked BEFORE any write. A preflight
    refusal is not a run (no producer invoked, nothing computed, no ledger written)."""
    import platform
    import socket
    import numpy
    import scipy
    import flint
    bad = []
    try:
        ev.resolve().relative_to(REPO.resolve())
        bad.append(f"evidence directory {ev} is inside the checkout")
    except ValueError:
        pass
    if ev.exists():
        bad.append(f"evidence directory {ev} already exists")
    rt = {"host": socket.gethostname(), "python": platform.python_version(), "numpy": numpy.__version__,
          "scipy": scipy.__version__, "python_flint": flint.__version__, "venv": sys.prefix}
    if rt != proto["runtime"]:
        bad.append(f"runtime differs from the protocol: {rt}")
    for k in proto["addresses"]["cells"]:
        if sha(RECORDS / f"aux5_CUSUM_{k}_256.json") != proto["k1_record_sha256"][str(k)]:
            bad.append(f"K1 record {k} differs from its pre-registered sha")
    probe = ("import sys; sys.path.insert(0, %r); import tc_producer as T\n"
             "[T.require_authorized(k, %r) for k in %r]") % (str(NS / "code"), protocol_sha256,
                                                              proto["addresses"]["cells"])
    p = subprocess.run([PY, "-B", "-c", probe], capture_output=True, text=True)
    if p.returncode != 0:
        bad.append("producer gate refuses: " + ((p.stderr.strip().splitlines() or [""])[-1]))
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol-sha256", required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--preflight-only", action="store_true")
    a = ap.parse_args()
    proto = json.loads((NS / "config/TC_PROTOCOL.json").read_bytes())
    if sha(NS / "config/TC_PROTOCOL.json") != a.protocol_sha256:
        raise SystemExit("protocol sha mismatch")
    cells = proto["addresses"]["cells"]
    a.workers = int(proto["budget"]["workers"])          # frozen worker count (review r2 N-R2-9); no override
    ev = Path(a.evidence)
    bad = preflight(proto, a.protocol_sha256, ev)
    if bad:
        print(json.dumps({"PREFLIGHT": "REFUSED", "reasons": bad}))
        return 2
    if a.preflight_only:
        print(json.dumps({"PREFLIGHT": "PASS"}))
        return 0
    (ev / "cells").mkdir(parents=True, exist_ok=False)
    (ev / "repro").mkdir(parents=True, exist_ok=False)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    ledger = ev / "RUN_LEDGER.jsonl"

    def log(rec):
        with open(ledger, "a") as fh:
            fh.write(json.dumps({"utc": now(), "head": head, **rec}, sort_keys=True) + "\n")
    log({"event": "RUN_START", "protocol_sha256": a.protocol_sha256, "addresses": cells, "workers": a.workers})
    cap = float(proto["budget"]["protocol_cap_new_real_cpu_hours"]) * 3600
    results, queue, running, spent, est = {}, list(cells), {}, 0.0, 0.0
    with cf.ThreadPoolExecutor(max_workers=a.workers) as pool:
        while queue or running:
            while queue and len(running) < a.workers:
                reserve = (len(running) + 1) * est + len(REPRO) * est
                if est and spent + reserve > cap:          # would exceed the protocol cap: launch nothing more
                    log({"event": "CAP_STOP", "spent_cpu_seconds": spent, "estimate_per_cell": est,
                         "not_launched": list(queue)})
                    queue = []
                    break
                k = queue.pop(0)
                log({"event": "START", "cell": k})
                running[pool.submit(one, k, a.protocol_sha256, proto["k1_record_sha256"][str(k)],
                                    ev / "cells" / f"TC_CELL_{k}.json")] = k
            if not running:
                break
            done, _ = cf.wait(list(running), return_when=cf.FIRST_COMPLETED)
            for f in done:
                running.pop(f)
                r = f.result()
                results[r["cell"]] = r
                if r["ok"]:
                    spent += r["cpu_seconds"]
                    est = max(est, r["cpu_seconds"])
                log({"event": "OUTPUT", **r})
    failed = sorted(k for k in cells if k not in results or not results[k]["ok"])
    if failed:
        log({"event": "RUN_VOID", "failed_or_not_run": failed, "spent_cpu_seconds": spent})
        print("VOID: failed or not run", failed)
        return 1
    rep = {}
    with cf.ThreadPoolExecutor(max_workers=len(REPRO)) as pool:
        futs = {pool.submit(one, k, a.protocol_sha256, proto["k1_record_sha256"][str(k)],
                            ev / "repro" / f"TC_CELL_{k}.json"): k for k in REPRO}
        for f in cf.as_completed(futs):
            r = f.result()
            r["identical"] = r["ok"] and r["sha256"] == results[r["cell"]]["sha256"]
            rep[r["cell"]] = r
            log({"event": "REPRO", **r})
    cpu = sum(r["cpu_seconds"] for r in results.values()) + sum(r.get("cpu_seconds", 0) for r in rep.values())
    index = {"schema": "rebaseguard.p5y.k5.lower-front-order3.tc-index.v1", "protocol_sha256": a.protocol_sha256,
             "head": head, "cells": {str(k): results[k]["sha256"] for k in sorted(results)},
             "reproduction": {str(k): rep[k]["identical"] for k in sorted(rep)},
             "cpu_seconds_total": cpu}
    (ev / "TC_INDEX.json").write_text(json.dumps(index, sort_keys=True, indent=1) + "\n")
    ok = all(r["identical"] for r in rep.values())
    log({"event": "RUN_END", "reproduction_identical": ok, "cpu_seconds_total": cpu,
         "index_sha256": sha(ev / "TC_INDEX.json")})
    print({"cells": len(results), "reproduction_identical": ok, "cpu_hours": cpu / 3600})
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
