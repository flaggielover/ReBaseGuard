"""Stream A0 job queue: run a declared job list with at most MAXPROC concurrent processes, each under a hard CPU cap
(RLIMIT_CPU; SIGXCPU/SIGKILL on overrun -> the job is recorded ABORTED_CPU_CAP, never silently dropped).

  python3 -I -B -S a0_queue.py JOBFILE [MAXPROC] [CPU_CAP_SECONDS]

JOBFILE: one job per line, the arguments of a0_run.py (e.g. "c2b 11/10 40").  Status lines go to
logs/queue_<JOBFILE stem>.jsonl (appended incrementally).
"""
from __future__ import annotations

import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _limit(cap):
    def f():
        resource.setrlimit(resource.RLIMIT_CPU, (cap, cap + 30))
        os.nice(5)
    return f


def main():
    jobfile = Path(sys.argv[1])
    maxproc = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
    jobs = [ln.split() for ln in jobfile.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    status = HERE / "logs" / f"queue_{jobfile.stem}.jsonl"
    running = []
    pending = list(jobs)

    def emit(rec):
        with status.open("a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")

    while pending or running:
        while pending and len(running) < maxproc:
            args = pending.pop(0)
            name = "_".join(a.replace("/", "_").replace(".py", "") for a in args)
            if len(name) > 120:          # bug fix: long argument lists overflowed the file-name limit (Errno 63)
                name = name[:80] + "_" + hashlib.sha256(" ".join(args).encode()).hexdigest()[:16]
            log = open(HERE / "logs" / f"job_{name}.log", "w")
            script, rest = (args[0], args[1:]) if args[0].endswith(".py") else ("a0_run.py", args)
            p = subprocess.Popen([sys.executable, "-I", "-B", "-S", str(HERE / script), *rest], stdout=log,
                                 stderr=subprocess.STDOUT, cwd=str(HERE), preexec_fn=_limit(cap))
            running.append((p, args, time.time(), log))
            emit({"event": "start", "job": args, "pid": p.pid, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        time.sleep(2)
        still = []
        for (p, args, t0, log) in running:
            rc = p.poll()
            if rc is None:
                still.append((p, args, t0, log))
                continue
            log.close()
            ru = resource.getrusage(resource.RUSAGE_CHILDREN)
            emit({"event": "end", "job": args, "rc": rc, "wall": round(time.time() - t0, 1),
                  "status": "OK" if rc == 0 else ("ABORTED_CPU_CAP" if rc in (-24, -9) else "FAILED"),
                  "children_cpu_total_so_far": round(ru.ru_utime + ru.ru_stime, 1)})
        running = still
    emit({"event": "queue_done", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})


if __name__ == "__main__":
    main()
