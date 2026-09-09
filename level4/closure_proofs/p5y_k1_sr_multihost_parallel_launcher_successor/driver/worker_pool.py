"""Real host-local process-parallel worker pool with FAIL-CLOSED CPU affinity.

The frozen worker counts (AWS 16, Vultr 4) must correspond to processes that
actually execute cells simultaneously, each pinned to exactly one qualified
PHYSICAL core. The predecessor validated the counts and then ran one sequential
loop; this module is the real executor.

Process-based, not threads: the FLINT/python-flint workload is CPU-bound, the
thread environment is frozen at one thread per worker, and one scientific
process per physical core is exactly what the qualified benchmark measured.

Task kinds, so the pool is provable WITHOUT running genuine science:
  SYNTHETIC_SPIN     busy-wait; used to prove real overlap and affinity
  STRUCTURAL_IMPORT  import every authoritative scientific dependency in the
                     child and return their identities; proves the real path is
                     importable in workers without computing a cell
  SCIENCE            the authoritative computation; reachable only when the
                     frozen authorization has production_enabled=true
"""
from __future__ import annotations

import multiprocessing as mp
import os
import time
import traceback

POOL_SCHEMA = "rebaseguard.p5y.k1.sr.multihost.worker-pool.v1"
TASK_KINDS = ("SYNTHETIC_SPIN", "STRUCTURAL_IMPORT", "SCIENCE")


class AffinityRefusal(RuntimeError):
    """A worker refused because it is not pinned to its authorised core."""


def enforce_affinity(core: int) -> dict:
    """Bind this process to exactly one CPU and VERIFY it. Fail closed."""
    try:
        os.sched_setaffinity(0, {core})
    except Exception as exc:                                       # noqa: BLE001
        raise AffinityRefusal(f"cannot bind to cpu {core}: {exc!r}") from exc
    actual = set(os.sched_getaffinity(0))
    if actual != {core}:
        raise AffinityRefusal(
            f"affinity not honoured: asked for cpu {core}, running on {sorted(actual)}")
    return {"core": core, "affinity": sorted(actual), "pid": os.getpid()}


FROZEN_THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                      "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
FROZEN_THREAD_VALUE = "1"


def enforce_thread_env(thread_env: dict) -> dict:
    """The frozen thread contract must hold INSIDE the worker, not only in the
    parent that spawned it.

    The contract itself is validated first: a worker asked to run with anything
    other than the frozen one-thread-per-worker contract refuses, so nested
    numerical thread expansion cannot be introduced by a malformed parent.
    """
    missing = [v for v in FROZEN_THREAD_VARS if v not in thread_env]
    if missing:
        raise AffinityRefusal(f"thread contract incomplete in worker: missing {missing}")
    wrong = {k: v for k, v in thread_env.items() if v != FROZEN_THREAD_VALUE}
    if wrong:
        raise AffinityRefusal(
            f"thread contract is not the frozen one-thread contract: {wrong}")
    for k, v in thread_env.items():
        os.environ[k] = v
    bad = {k: os.environ.get(k) for k, v in thread_env.items() if os.environ.get(k) != v}
    if bad:
        raise AffinityRefusal(f"thread contract not applied in worker: {bad}")
    return dict(thread_env)


def _run_task(task, root, science_enabled):
    kind = task["kind"]
    if kind == "SYNTHETIC_SPIN":
        deadline = time.monotonic() + float(task["seconds"])
        n = 0
        while time.monotonic() < deadline:
            n += 1                                   # occupy the core, no science
        return {"spins": n}
    if kind == "STRUCTURAL_IMPORT":
        import sys
        sys.path.insert(0, task["driver_dir"])
        import executor_adapter as EA
        mods = EA.bind(root)
        return {"bound_modules": sorted(mods),
                "has_cell_certificate": hasattr(mods["sr_propagate"], "cell_certificate"),
                "has_resolvent": hasattr(mods["sr_nstep"], "ResolventCertificate")}
    if kind == "SCIENCE":
        if not science_enabled:
            raise AffinityRefusal(
                "SCIENCE task dispatched while production_enabled=false")
        import sys
        sys.path.insert(0, task["driver_dir"])
        import executor_adapter as EA
        return EA.execute_cell(root, task["cell_id"])
    raise AffinityRefusal(f"unknown task kind {kind!r}")


def _worker_main(core, task_q, result_q, thread_env, root, science_enabled):
    try:
        aff = enforce_affinity(core)
        enforce_thread_env(thread_env)
    except Exception as exc:                                       # noqa: BLE001
        result_q.put({"fatal": True, "core": core, "pid": os.getpid(),
                      "error": f"{type(exc).__name__}: {exc}"})
        return
    result_q.put({"ready": True, **aff})
    while True:
        task = task_q.get()
        if task is None:
            return
        rec = {"cell_id": task.get("cell_id"), "kind": task["kind"],
               "pid": os.getpid(), "core": core,
               "affinity": sorted(os.sched_getaffinity(0))}
        t0w, t0c = time.monotonic(), time.process_time()
        try:
            rec["payload"] = _run_task(task, root, science_enabled)
            rec["ok"] = True
        except Exception as exc:                                   # noqa: BLE001
            rec["ok"] = False
            rec["error"] = f"{type(exc).__name__}: {exc}"
            rec["traceback"] = traceback.format_exc()[-800:]
        rec["t_start"] = t0w
        rec["t_end"] = time.monotonic()
        rec["cpu_seconds"] = time.process_time() - t0c
        result_q.put(rec)


class WorkerPool:
    """One process per qualified physical core. The PARENT keeps all admission,
    accounting, finalisation and resume authority; workers only compute."""

    def __init__(self, cores, thread_env, root, *, science_enabled=False):
        self.cores = list(cores)
        self.thread_env = dict(thread_env)
        self.root = str(root)
        self.science_enabled = bool(science_enabled)
        self.ctx = mp.get_context("fork")
        self.task_q = self.ctx.Queue()
        self.result_q = self.ctx.Queue()
        self.procs = []
        self.ready = []

    def start(self, ready_timeout=60.0):
        for c in self.cores:
            p = self.ctx.Process(target=_worker_main,
                                 args=(c, self.task_q, self.result_q, self.thread_env,
                                       self.root, self.science_enabled),
                                 daemon=True)
            p.start()
            self.procs.append(p)
        deadline = time.monotonic() + ready_timeout
        while len(self.ready) < len(self.cores):
            if time.monotonic() > deadline:
                raise AffinityRefusal(
                    f"only {len(self.ready)}/{len(self.cores)} workers became ready")
            r = self.result_q.get(timeout=ready_timeout)
            if r.get("fatal"):
                raise AffinityRefusal(f"worker on cpu {r['core']} refused: {r['error']}")
            self.ready.append(r)
        return {"schema": POOL_SCHEMA, "workers": len(self.procs),
                "cores": self.cores,
                "pids": sorted(r["pid"] for r in self.ready),
                "affinity": {r["pid"]: r["affinity"] for r in self.ready}}

    def submit(self, task):
        self.task_q.put(task)

    def get(self, timeout=None):
        return self.result_q.get(timeout=timeout)

    def alive(self):
        return sum(1 for p in self.procs if p.is_alive())

    def close(self):
        for _ in self.procs:
            try:
                self.task_q.put(None)
            except Exception:                                      # noqa: BLE001
                pass
        for p in self.procs:
            p.join(timeout=10)
            if p.is_alive():
                p.terminate()


def max_simultaneous(records) -> int:
    """Maximum number of tasks genuinely in flight at the same instant, from the
    recorded [t_start, t_end) intervals. Concurrency is MEASURED, not inferred
    from process count."""
    events = []
    for r in records:
        events.append((r["t_start"], 1))
        events.append((r["t_end"], -1))
    events.sort(key=lambda e: (e[0], -e[1]))
    cur = best = 0
    for _, d in events:
        cur += d
        best = max(best, cur)
    return best
