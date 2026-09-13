"""The CUSUM Aux5 production supervisor and its keeper. NON-CERTIFYING.

  keeper      sets PR_SET_CHILD_SUBREAPER, starts the supervisor, forwards SIGTERM/SIGINT to it, and reaps the
              supervisor and every orphaned worker with exact rusage into reaper.jsonl; exits with the
              supervisor's code.
  supervisor  holds the campaign flock for its whole life; opens (or creates) the ledger; refuses corrupted
              sealed evidence; reconciles whatever a dead predecessor left open; then admits PENDING cells in
              ascending index order, one worker per bound physical core, while the host guard holds, no halt is
              set, no drain is requested and the cap invariant admits one more reservation.
  worker      the frozen certifier, started by the bound argv (env -i, taskset to one core) with
              PR_SET_PDEATHSIG=SIGKILL, so no worker outlives its supervisor. The supervisor never kills a worker:
              a drain (SIGTERM, SIGINT or a DRAIN marker) stops admissions and lets admitted work finish and seal.

EXIT CODES  0 COMPLETE, 10 DRAINED, 20 HALTED, 30 REFUSED, 40 INCOMPLETE_BUDGET_EXHAUSTED

  python prod_supervisor.py --synthetic-spec CFG.json [--keep]     synthetic acceptance only
  production is started exclusively by `prod_entry.py launch` (keeper + preflight + supervisor)
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prod_ledger as L                                                       # noqa: E402
from prod_common import (Refusal, append_durable, pdeathsig_preexec, proc_cpu_usec, proc_stat,  # noqa: E402
                         rusage_usec, set_child_subreaper)
from prod_sealer import seal_file, verify_record                              # noqa: E402
from prod_spec import CampaignSpec                                            # noqa: E402

EXIT_COMPLETE, EXIT_DRAINED, EXIT_HALTED, EXIT_REFUSED, EXIT_BUDGET = 0, 10, 20, 30, 40
EXIT_FOR = {"COMPLETE": EXIT_COMPLETE, "DRAINED": EXIT_DRAINED, "HALTED": EXIT_HALTED,
            "INCOMPLETE_BUDGET_EXHAUSTED": EXIT_BUDGET}
KEEPER_ENV = "RBG_AUX5_KEEPER_PID"


def log(event: str, **fields) -> None:
    print(json.dumps({"t": round(time.time(), 3), "event": event, **fields}, sort_keys=True, default=str), flush=True)


class Supervisor:
    def __init__(self, spec, *, preflight=None):
        self.spec, self.preflight = spec, preflight
        self.run_id = f"R{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{os.getpid()}"
        self.draining = False
        self.procs: dict = {}        # pid -> (attempt id, Popen), referenced so subprocess never reaps them itself

    def _on_signal(self, signum, _frame) -> None:
        if not self.draining:
            log("DRAIN_REQUESTED", signal=signum)
        self.draining = True

    def run(self) -> int:
        signal.signal(signal.SIGTERM, self._on_signal)
        signal.signal(signal.SIGINT, self._on_signal)
        spec = self.spec
        if spec.require_keeper and os.environ.get(KEEPER_ENV) != str(os.getppid()):
            log("REFUSED", code="NO_KEEPER", detail="a production supervisor runs only under its keeper")
            return EXIT_REFUSED
        lock = L.CampaignLock(spec.root)
        try:
            lock.acquire({"run_id": self.run_id, "pid": os.getpid(), "host": socket.gethostname(),
                          "t_wall": time.time()})
        except Refusal as r:
            log("REFUSED", code=r.code, detail=r.detail)
            return EXIT_REFUSED
        try:
            return self._run_locked(lock)
        except Refusal as r:
            log("REFUSED", code=r.code, detail=r.detail, in_flight=len(self.procs))
            return EXIT_REFUSED
        finally:
            lock.release()

    def _run_locked(self, lock) -> int:
        spec = self.spec
        probe_usec = 0
        if self.preflight is not None:
            ready, report, probe_usec = self.preflight()
            if not ready:
                log("NOT_READY", failures=[c for c in report["checks"] if c["status"] != "PASS"])
                return EXIT_REFUSED
        if L.Paths(spec.root).drain.exists():
            raise Refusal("DRAIN_PRESENT", "a DRAIN marker is present; remove it explicitly before relaunching")
        led = L.Ledger(spec, lock, run_id=self.run_id)
        relation = led.open(allow_genesis=True)
        sealed = L.verify_sealed_evidence(spec, led.state)
        st = led.state
        in_flight = any(a["status"] in L.OPEN for a in st["attempts"].values())
        if st["disposition"] in L.TERMINAL and not in_flight:
            log("TERMINAL", disposition=st["disposition"], halt=st["halt"])
            return EXIT_FOR[st["disposition"]]
        reaped, unreadable = L.read_reaper(led.p)
        overhead = L.unmatched_overhead(reaped, st)
        led.txn("RUN_OPENED", lambda s: L.op_run_open(s, self.run_id, os.getpid(), probe_usec, overhead),
                {"run_id": self.run_id, "relation": relation})
        report = L.reconcile(led, reaped, unreadable)
        log("OPENED", run_id=self.run_id, relation=relation, sealed_verified=sealed, reconciled=report)
        return self._loop(led)

    # -------------------------------------------------------------- main loop
    def _loop(self, led) -> int:
        spec = self.spec
        next_beat = time.monotonic() + spec.heartbeat_s
        while True:
            self._reap(led)
            if not self.draining and led.p.drain.exists():
                self.draining = True
                log("DRAIN_REQUESTED", marker=str(led.p.drain))
            if time.monotonic() >= next_beat:
                self._heartbeat(led)
                next_beat = time.monotonic() + spec.heartbeat_s
            denied = False
            if not self.draining and led.state["halt"] is None:
                denied = self._admit(led)
            if not self.procs:
                st = led.state
                if st["halt"] is not None:
                    return self._finish(led, "HALTED")
                if all(c["status"] == "SEALED" for c in st["cells"].values()):
                    return self._finish(led, "COMPLETE")
                if self.draining:
                    return self._finish(led, "DRAINED")
                if denied:
                    return self._finish(led, "INCOMPLETE_BUDGET_EXHAUSTED", budget={
                        "pending_cells": sorted(int(c) for c, x in st["cells"].items() if x["status"] == "PENDING"),
                        "committed_usec": L.committed_total(st), "cap_usec": spec.cap_usec,
                        "reservation_usec": spec.reservation_usec,
                        "rule": "115 * (committed + R) > 100 * CAP with no attempt in flight; the cap is never raised",
                        "t_wall": time.time()})
                if L.next_pending(st) is None:
                    led.txn("HALT", lambda s: L.op_halt(s, "NO_ADMISSIBLE_CELL"), {})
                    return self._finish(led, "HALTED")
            time.sleep(spec.poll_s)

    def _admit(self, led) -> bool:
        """Admit into every free core. Returns True iff the cap invariant denied an admission."""
        spec = self.spec
        busy = {led.state["attempts"][aid]["core"] for aid, _ in self.procs.values()}
        free = [c for c in spec.cores if c not in busy]
        if not free or L.next_pending(led.state) is None:
            return False
        problems = spec.host_guard()
        if problems:
            led.txn("HALT", lambda s: L.op_halt(s, "HOST_DRIFT", problems=problems[:8]), {"reason": "HOST_DRIFT"})
            log("HALT", reason="HOST_DRIFT", problems=problems)
            return False
        for core in free:
            cell = L.next_pending(led.state)
            if cell is None:
                return False
            try:
                aid = led.txn("RESERVED", lambda s: L.op_reserve(s, spec, cell, core, self.run_id),
                              {"cell": cell, "core": core})
            except Refusal as r:
                if r.code == "CAP_ADMISSION_DENIED":
                    log("ADMISSION_DENIED", detail=r.detail, in_flight=len(self.procs))
                    return True
                raise
            self._spawn(led, aid)
            if led.state["halt"] is not None:
                return False
        return False

    def _spawn(self, led, aid: str) -> None:
        spec, a = self.spec, led.state["attempts"][aid]
        out = Path(spec.root) / a["record"]
        out.parent.mkdir(parents=True, exist_ok=True)
        argv = spec.worker_argv(cell=a["cell"], core=a["core"], out=out)
        t_spawn = time.time()
        with open(out.parent / "worker.log", "ab") as worker_log:
            try:
                proc = subprocess.Popen(argv, cwd=str(spec.worker_cwd), env=spec.worker_env,
                                        stdin=subprocess.DEVNULL, stdout=worker_log, stderr=subprocess.STDOUT,
                                        close_fds=True, preexec_fn=pdeathsig_preexec(os.getpid()))
            except (OSError, subprocess.SubprocessError) as exc:
                def released(s):
                    L.op_close(s, aid, "RELEASED", 0, "NO_PROCESS_STARTED", tear_kind=L.SPAWN_FAILED,
                               detail=repr(exc)[:300])
                    L.op_halt(s, L.SPAWN_FAILED, attempt=aid, detail=repr(exc)[:300])
                led.txn("RELEASED", released, {"attempt": aid})
                log("SPAWN_FAILED", attempt=aid, error=repr(exc))
                return
        stat = proc_stat(proc.pid)
        ticks = stat["starttime"] if stat else None
        self.procs[proc.pid] = (aid, proc)
        led.txn("RUNNING", lambda s: L.op_running(s, aid, proc.pid, ticks, t_spawn), {"attempt": aid, "pid": proc.pid})
        log("SPAWNED", attempt=aid, cell=a["cell"], core=a["core"], pid=proc.pid)

    def _reap(self, led) -> None:
        for pid in list(self.procs):
            try:
                wpid, status, ru = os.wait4(pid, os.WNOHANG)
            except ChildProcessError:
                aid, _proc = self.procs.pop(pid)
                a = led.state["attempts"][aid]
                charge, evidence, _t = L.tail_bound(a, now=time.time(), current_boot=a["boot_id"])
                led.txn("TORN", lambda s: L.op_close(s, aid, "TORN", charge, evidence, tear_kind=L.ORPHAN,
                                                     detail="exit status lost"), {"attempt": aid})
                continue
            if wpid == 0:
                continue
            aid, proc = self.procs.pop(pid)
            proc.returncode = os.waitstatus_to_exitcode(status)
            self._finalize(led, aid, status, ru)

    def _finalize(self, led, aid: str, status: int, ru) -> None:
        spec, a = self.spec, led.state["attempts"][aid]
        t_exit, measured = time.time(), rusage_usec(ru)
        how = {"exited": os.WIFEXITED(status), "exit_code": os.WEXITSTATUS(status) if os.WIFEXITED(status) else None,
               "signal": os.WTERMSIG(status) if os.WIFSIGNALED(status) else None}
        record = Path(spec.root) / a["record"]

        def close(state, kind=None, detail=None, seal=None):
            def m(s):
                L.op_close(s, aid, state, measured, "WAIT4_RUSAGE", tear_kind=kind, detail=detail, seal=seal)
                s["supervisor_runs"][self.run_id]["children_usec"] += measured
            led.txn(state, m, {"attempt": aid, "cell": a["cell"], **how})
            log(state, attempt=aid, cell=a["cell"], cpu_s=round(measured / 1e6, 3), kind=kind, detail=detail, **how)

        if record.exists():
            try:
                facts = verify_record(record, cell=a["cell"], spec=spec, measured_cpu_usec=measured,
                                      wall_bound_s=t_exit - a["t_spawn"], not_before_wall=a["t_reserved"])
            except Refusal as r:
                close("FAILED", L.MALFORMED, f"{r.code}: {r.detail[:300]}")
                return
            seal_file(record)
            close("SEALED", seal={**facts, "exit": how, "recovered": False})
        elif how["exited"] and how["exit_code"] == 0:
            close("FAILED", L.MALFORMED, "exit code 0 without a record")
        elif how["exited"]:
            close("FAILED", L.WORKER_FAILURE, f"exit code {how['exit_code']}")
        else:
            close("TORN", L.INFRA_SIGNAL, f"signal {how['signal']}")

    def _heartbeat(self, led) -> None:
        now, samples = time.time(), {}
        for pid, (aid, _proc) in self.procs.items():
            ticks = led.state["attempts"][aid]["pid_start_ticks"]
            cpu = proc_cpu_usec(pid, ticks) if ticks is not None else None
            if cpu is not None:
                samples[aid] = cpu
        led.txn("HEARTBEAT", lambda s: [L.op_sample(s, aid, cpu, now) for aid, cpu in samples.items()],
                {"samples": len(samples)})

    def _finish(self, led, disposition: str, budget=None) -> int:
        def m(s):
            s["disposition"] = disposition
            if budget is not None:
                s["budget_exhaustion"] = budget
            L.op_run_end(s, self.run_id)
        led.txn(f"DISPOSITION_{disposition}", m, {"run_id": self.run_id})
        st = led.state
        log("FINISHED", disposition=disposition, halt=st["halt"], committed_usec=L.committed_total(st),
            sealed=sum(1 for c in st["cells"].values() if c["status"] == "SEALED"))
        return EXIT_FOR[disposition]


# ------------------------------------------------------------------ keeper
def keep(argv: list, *, root, env=None) -> int:
    set_child_subreaper()
    paths = L.Paths(root)
    env = dict(os.environ if env is None else env)
    env[KEEPER_ENV] = str(os.getpid())
    child = subprocess.Popen(argv, env=env, close_fds=True)

    def forward(_signum, _frame):
        try:
            os.kill(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    signal.signal(signal.SIGTERM, forward)
    signal.signal(signal.SIGINT, forward)
    supervisor_status = None
    while True:
        try:
            pid, status, ru = os.wait4(-1, 0)
        except ChildProcessError:
            break
        is_supervisor = pid == child.pid
        paths.root.mkdir(parents=True, exist_ok=True)
        append_durable(paths.reaper, json.dumps(
            L.reaper_record("CHILD_REAPED", pid, status, ru, is_supervisor=is_supervisor), sort_keys=True))
        if is_supervisor:
            supervisor_status = status
            child.returncode = os.waitstatus_to_exitcode(status)
    paths.root.mkdir(parents=True, exist_ok=True)
    append_durable(paths.reaper, json.dumps(L.reaper_record(
        "KEEPER_EXIT", os.getpid(), None, resource.getrusage(resource.RUSAGE_SELF), is_supervisor=False),
        sort_keys=True))
    if supervisor_status is None:
        return EXIT_REFUSED
    code = os.waitstatus_to_exitcode(supervisor_status)
    return code if code >= 0 else 128 - code


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CUSUM Aux5 supervisor (synthetic acceptance entry)")
    ap.add_argument("--synthetic-spec", required=True)
    ap.add_argument("--keep", action="store_true", help="run the supervisor under a keeper")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.synthetic_spec).read_text())
    spec = CampaignSpec.synthetic(cfg)
    if a.keep:
        return keep([sys.executable, str(Path(__file__).resolve()), "--synthetic-spec", a.synthetic_spec],
                    root=spec.root)
    return Supervisor(spec).run()


if __name__ == "__main__":
    raise SystemExit(main())
