"""SYNTHETIC acceptance of the CUSUM Aux5 production checkpoint. NON-RESULT-BEARING.

Only synthetic workers (tests/synthetic_worker.py) run, in scratch runtime roots outside the repository. Calls against
the production checkpoint are read-only or refusing: the frozen certifier is never started, the production runtime
root is never created, and production is never launched.

  python -B tests/acceptance.py --scratch DIR --out RESULT.json [--only NAME ...]
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import traceback
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
NS = Path(__file__).resolve().parents[1]
CODE = NS / "code"
sys.path.insert(0, str(CODE))

import k4_input_attestation as K4A                                                        # noqa: E402
import prod_entry as PE                                                                   # noqa: E402
import prod_ledger as L                                                                   # noqa: E402
import prod_supervisor as PS                                                              # noqa: E402
from prod_common import (K4_NS, ROOT, Refusal, append_durable, atomic_write_bytes,        # noqa: E402
                         atomic_write_json, canonical, host_facts, pid_alive, proc_stat, sha256_bytes, sha256_file)
from prod_sealer import verify_record                                                     # noqa: E402
from prod_spec import (PRODUCTION_RUNTIME_ROOT, QUALIFICATION_RECORDS, CampaignSpec,      # noqa: E402
                       load_frozen_checkpoint)

SUPERVISOR = CODE / "prod_supervisor.py"
SCENARIOS: list = []


class Fail(AssertionError):
    pass


def check(cond, msg: str) -> None:
    if not cond:
        raise Fail(msg)


def scenario(*covers):
    def deco(fn):
        SCENARIOS.append((fn.__name__, covers, fn))
        return fn
    return deco


def expect_refusal(code: str, fn, *args, **kw) -> Refusal:
    try:
        fn(*args, **kw)
    except Refusal as r:
        check(r.code == code, f"expected refusal {code}, got {r.code}: {r.detail}")
        return r
    raise Fail(f"expected refusal {code}; nothing was refused")


def refused_with(out: str, code: str) -> bool:
    return f'"code": "{code}"' in out


class Campaign:
    def __init__(self, scratch: Path, name: str, **cfg):
        self.dir = scratch / name
        self.dir.mkdir(parents=True, exist_ok=False)
        self.cfg = {"root": str(self.dir / "root"), "config_path": str(self.dir / "cfg.json"),
                    "checkpoint_sha256": f"SYNTHETIC-{name}", "cells": list(range(6)), "cores": [0, 2],
                    "cap_usec": 10 ** 13, "reservation_usec": 2_000_000, "poll_s": 0.05, "heartbeat_s": 0.25,
                    "burn_s": 0.1, "slow_s": 2.0, "plan": {}, "worker_python": sys.executable}
        self.cfg.update(cfg)
        self.save()
        self.runs = 0

    def save(self) -> None:
        atomic_write_json(self.cfg["config_path"], self.cfg)

    @property
    def root(self) -> Path:
        return Path(self.cfg["root"])

    @property
    def spec(self):
        return CampaignSpec.synthetic(self.cfg)

    def start(self, keep: bool = True):
        self.runs += 1
        log_path = self.dir / f"run{self.runs}.log"
        env = {k: v for k, v in os.environ.items() if k != PS.KEEPER_ENV}
        argv = [sys.executable, "-B", str(SUPERVISOR), "--synthetic-spec", self.cfg["config_path"]]
        with open(log_path, "wb") as log:
            p = subprocess.Popen(argv + (["--keep"] if keep else []), stdout=log, stderr=subprocess.STDOUT, env=env,
                                 start_new_session=True)
        p.log_path = log_path
        return p

    @staticmethod
    def finish(p, timeout: float = 240) -> tuple[int, str]:
        try:
            code = p.wait(timeout)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
            raise Fail(f"supervisor did not finish in {timeout}s") from None
        return code, p.log_path.read_text()

    def run(self, keep: bool = True, timeout: float = 240) -> tuple[int, str]:
        return self.finish(self.start(keep), timeout)

    def state(self) -> dict:
        return json.loads((self.root / "ledger.json").read_text())

    def journal(self) -> list:
        return L.Ledger.read_journal(self.root / "journal.jsonl")[0]

    def reaper(self) -> list:
        return L.read_reaper(L.Paths(self.root))[0]

    def validate(self) -> dict:
        st, _entries, _torn, relation = L.Ledger.read_and_relate(L.Paths(self.root))
        check(relation == "CONTINUOUS", f"ledger relation {relation}")
        L.validate_state(st, self.spec)
        return st

    def wait_for(self, pred, timeout: float = 60, what: str = "condition") -> dict:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                st = self.state()
                if pred(st):
                    return st
            except (OSError, ValueError, KeyError):
                pass
            time.sleep(0.05)
        raise Fail(f"timed out waiting for {what}")

    def open_ledger(self):
        lock = L.CampaignLock(self.root)
        lock.acquire({"tool": "acceptance", "pid": os.getpid()})
        led = L.Ledger(self.spec, lock)
        led.open(allow_genesis=False)
        return lock, led

    def settle(self) -> dict:
        lock, led = self.open_ledger()
        try:
            reaped, unreadable = L.read_reaper(led.p)
            L.reconcile(led, reaped, unreadable)
            overhead = L.unmatched_overhead(reaped, led.state)
            if overhead:
                led.txn("OVERHEAD_CHARGED", lambda s: L.op_charge_overhead(s, overhead), {})
            return led.state
        finally:
            lock.release()


def attempts(st, *, cell=None, status=None) -> list:
    return [(aid, a) for aid, a in sorted(st["attempts"].items())
            if (cell is None or a["cell"] == cell) and (status is None or a["status"] == status)]


def count(st, status) -> int:
    return sum(1 for c in st["cells"].values() if c["status"] == status)


def sealed_hashes(st) -> dict:
    return {a["cell"]: a["seal"]["scientific_content_hash"] for _, a in attempts(st, status="SEALED")}


def wait_pid_dead(pid: int, timeout: float = 10) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not pid_alive(pid):
            return True
        time.sleep(0.05)
    return False


def forge_next_state(root: Path, mutate) -> None:
    """An adversary who rewrites ledger.json AND extends the journal hash chain consistently."""
    p = L.Paths(root)
    st = json.loads(p.ledger.read_text())
    entries, _torn = L.Ledger.read_journal(p.journal)
    new = copy.deepcopy(st)
    mutate(new)
    new["seq"], new["prev_state_sha256"] = st["seq"] + 1, L.state_sha256(st)
    new["last_event"] = {"event": "FORGED", "detail": {}, "t_wall": time.time()}
    atomic_write_json(p.ledger, new)
    e = {"schema": L.JOURNAL_SCHEMA, "seq": new["seq"], "event": "FORGED", "state_sha256": L.state_sha256(new),
         "prev_entry_sha256": entries[-1]["entry_sha256"], "t_wall": time.time(), "detail": {}}
    e["entry_sha256"] = sha256_bytes(canonical(e))
    append_durable(p.journal, json.dumps(e, sort_keys=True))


# ====================================================================== scenarios
@scenario("clean start", "reservation", "synthetic worker success", "atomic sealing", "no duplicate records")
def s01_clean_start_reservation_success(scratch):
    c = Campaign(scratch, "s01", cells=list(range(6)))
    check(not c.root.exists(), "fresh root")
    code, out = c.run(keep=True)
    check(code == PS.EXIT_COMPLETE, f"exit {code}: {out[-600:]}")
    st = c.validate()
    check(st["disposition"] == "COMPLETE" and count(st, "SEALED") == 6, "all six cells sealed")
    check(len(st["attempts"]) == 6, "exactly one attempt per cell")
    for aid, a in attempts(st):
        check(a["status"] == "SEALED" and a["charge_evidence"] == "WAIT4_RUSAGE" and a["charge_usec"] > 0, aid)
        check(a["pid"] and a["pid_start_ticks"] is not None and a["t_spawn"] >= a["t_reserved"], f"{aid} lifecycle fields")
        path = c.root / a["record"]
        check(path.stat().st_mode & 0o222 == 0, f"{aid} sealed record is read-only")
        facts = verify_record(path, cell=a["cell"], spec=c.spec)
        check(facts["record_sha256"] == a["seal"]["record_sha256"], f"{aid} seal binds the record bytes")
    first = attempts(st, cell=0)[0][0]
    order = [e["event"] for e in c.journal()
             if e["detail"].get("attempt") == first or (e["event"] == "RESERVED" and e["detail"].get("cell") == 0)]
    check(order == ["RESERVED", "RUNNING", "SEALED"], f"cell 0 lifecycle order {order}")
    check(st["committed_usec"]["science"] == sum(a["charge_usec"] for _, a in attempts(st)), "science accounting")
    kinds = sorted(r["kind"] for r in c.reaper())
    check(kinds.count("KEEPER_EXIT") == 1 and any(r["is_supervisor"] for r in c.reaper()), f"keeper evidence {kinds}")
    return {"cells_sealed": 6, "committed_usec": L.committed_total(st), "journal_entries": len(c.journal())}


@scenario("synthetic worker failure", "halt on failure")
def s02_worker_failure_halts(scratch):
    c = Campaign(scratch, "s02", cells=list(range(6)), cores=[0], plan={"2": ["fail"]})
    code, out = c.run(keep=True)
    check(code == PS.EXIT_HALTED, f"exit {code}")
    st = c.validate()
    check(st["halt"]["reason"] == L.WORKER_FAILURE and st["cells"]["2"]["status"] == "FAILED", f"halt {st['halt']}")
    check(all(st["cells"][str(i)]["status"] == "SEALED" for i in (0, 1)), "cells before the failure sealed")
    check(all(st["cells"][str(i)]["status"] == "PENDING" and not attempts(st, cell=i) for i in (3, 4, 5)),
          "no admission after the halt")
    seq = st["seq"]
    code2, _ = c.run(keep=False)
    check(code2 == PS.EXIT_HALTED and c.state()["seq"] == seq, "a halted ledger is never resumed or mutated")
    return {"halt": st["halt"]["reason"]}


@scenario("synthetic worker failure", "corrupted evidence refusal", "wrong producer identity refusal",
          "wrong runtime contract refusal")
def s03_bad_records_refused_at_seal(scratch):
    expected = {"malformed": "SCIENTIFIC_HASH", "overclaim": "CPU_EVIDENCE_INCONSISTENT",
                "noout": "exit code 0 without a record", "wrong_identity": "PRODUCER_IDENTITY",
                "wrong_runtime": "RUNTIME_CONTRACT", "selfkill": None}
    details = {}
    for behaviour, marker in expected.items():
        c = Campaign(scratch, f"s03_{behaviour}", cells=[0, 1], cores=[0], plan={"0": [behaviour, "ok"]})
        code, out = c.run(keep=True)
        st = c.validate()
        (aid, a), = attempts(st, cell=0)[:1]
        if behaviour == "selfkill":
            check(code == PS.EXIT_COMPLETE and a["status"] == "TORN" and a["tear_kind"] == L.INFRA_SIGNAL,
                  "a worker killed before writing is TORN and retried")
            check(attempts(st, cell=0)[1][1]["status"] == "SEALED", "retry sealed")
        else:
            check(code == PS.EXIT_HALTED and a["status"] == "FAILED" and marker in (a["detail"] or ""),
                  f"{behaviour}: exit {code} status {a['status']} detail {a['detail']}")
            check(st["cells"]["1"]["status"] == "PENDING", f"{behaviour}: nothing admitted after the halt")
        details[behaviour] = {"status": a["status"], "detail": (a["detail"] or "")[:80]}
    return details


@scenario("SIGTERM", "graceful drain", "skip/resume")
def s04_sigterm_graceful_drain(scratch):
    c = Campaign(scratch, "s04", cells=list(range(8)), cores=[0, 2], plan={str(i): ["slow"] for i in range(8)},
                 slow_s=3.0)
    p = c.start(keep=True)
    c.wait_for(lambda s: len(attempts(s, status="RUNNING")) == 2, what="two attempts RUNNING")
    os.kill(p.pid, signal.SIGTERM)
    code, out = c.finish(p)
    check(code == PS.EXIT_DRAINED, f"exit {code}: {out[-400:]}")
    st = c.validate()
    check(st["disposition"] == "DRAINED" and len(st["attempts"]) == 2, f"attempts {len(st['attempts'])}")
    check(all(a["status"] == "SEALED" for _, a in attempts(st)), "admitted work finished and sealed; nothing torn")
    check(count(st, "PENDING") == 6, "pending cells untouched")
    code2, _ = c.run(keep=True)
    st2 = c.validate()
    check(code2 == PS.EXIT_COMPLETE and len(st2["attempts"]) == 8, "resume completes without re-admitting sealed cells")
    return {"sealed_at_drain": 2, "attempts_total": 8}


@scenario("graceful drain", "stale incompatible run state")
def s05_drain_marker(scratch):
    c = Campaign(scratch, "s05", cells=list(range(5)), cores=[0], plan={str(i): ["slow"] for i in range(5)},
                 slow_s=1.5)
    p = c.start(keep=True)
    c.wait_for(lambda s: attempts(s, status="RUNNING"), what="an attempt RUNNING")
    atomic_write_bytes(c.root / "DRAIN", b"DRAIN\n")
    code, _ = c.finish(p)
    check(code == PS.EXIT_DRAINED, f"exit {code}")
    st = c.validate()
    check(len(st["attempts"]) == 1 and attempts(st)[0][1]["status"] == "SEALED", "only the admitted cell ran")
    code2, out2 = c.run(keep=False)
    check(code2 == PS.EXIT_REFUSED and refused_with(out2, "DRAIN_PRESENT") and c.state()["seq"] == st["seq"],
          "relaunch with DRAIN present is refused without mutation")
    os.unlink(c.root / "DRAIN")
    code3, _ = c.run(keep=True)
    check(code3 == PS.EXIT_COMPLETE, f"exit {code3}")
    return {"drained_after": 1}


@scenario("SIGKILL", "torn attempt rule", "retry accounting")
def s06_worker_sigkill_torn_and_retried(scratch):
    return _worker_signal(scratch, "s06", signal.SIGKILL)


@scenario("SIGTERM", "torn attempt rule")
def s07_worker_sigterm_torn_and_retried(scratch):
    return _worker_signal(scratch, "s07", signal.SIGTERM)


def _worker_signal(scratch, name, sig):
    c = Campaign(scratch, name, cells=[0, 1], cores=[0], plan={"0": ["hang", "ok"]})
    p = c.start(keep=True)
    st = c.wait_for(lambda s: attempts(s, cell=0, status="RUNNING"), what="cell 0 RUNNING")
    pid = attempts(st, cell=0, status="RUNNING")[0][1]["pid"]
    os.kill(pid, sig)
    code, out = c.finish(p)
    check(code == PS.EXIT_COMPLETE, f"exit {code}: {out[-400:]}")
    st = c.validate()
    (a1, t1), (a2, t2) = attempts(st, cell=0)
    check(t1["status"] == "TORN" and t1["tear_kind"] == L.INFRA_SIGNAL and t1["detail"] == f"signal {int(sig)}",
          f"first attempt {t1['status']} {t1['detail']}")
    check(t1["charge_evidence"] == "WAIT4_RUSAGE" and t1["charge_usec"] > 0, "torn attempt charged exactly")
    check(t2["status"] == "SEALED" and st["cells"]["0"]["infra_tears"] == 1, "retried and sealed; one tear")
    check(st["committed_usec"]["torn"] == t1["charge_usec"], "torn bucket")
    return {"torn_charge_usec": t1["charge_usec"]}


@scenario("SIGKILL", "crash recovery", "crash-safe reconciliation", "restart-safe reservation handling")
def s08_supervisor_sigkill_recovered_by_keeper_evidence(scratch):
    c = Campaign(scratch, "s08", cells=list(range(4)), cores=[0, 2], plan={"0": ["hang", "ok"], "1": ["hang", "ok"]})
    p = c.start(keep=True)
    st = c.wait_for(lambda s: len(attempts(s, status="RUNNING")) == 2, what="two RUNNING")
    workers = [a["pid"] for _, a in attempts(st, status="RUNNING")]
    supervisor = json.loads((c.root / "campaign.owner.json").read_text())["pid"]
    os.kill(supervisor, signal.SIGKILL)
    code, _ = c.finish(p)
    check(code == 128 + signal.SIGKILL, f"keeper exit {code}")
    check(all(wait_pid_dead(w) for w in workers), "no worker outlived its supervisor (PDEATHSIG)")
    reaped = {r["pid"]: r for r in c.reaper()}
    check(all(w in reaped and reaped[w]["signal"] == signal.SIGKILL for w in workers), "keeper reaped both workers")
    check(len(attempts(c.state(), status="RUNNING")) == 2, "ledger still shows the in-flight attempts")
    code2, out2 = c.run(keep=True)
    check(code2 == PS.EXIT_COMPLETE, f"exit {code2}: {out2[-400:]}")
    st2 = c.validate()
    for cell in (0, 1):
        (_, t), (_, s) = attempts(st2, cell=cell)
        check(t["status"] == "TORN" and t["tear_kind"] == L.ORPHAN and t["charge_evidence"] == "REAPER_RUSAGE",
              f"cell {cell} orphan reconciled with keeper rusage ({t['charge_evidence']})")
        check(s["status"] == "SEALED", f"cell {cell} retried")
    crashed = [r for r in st2["supervisor_runs"].values() if r["end"] == "CRASHED"]
    check(len(crashed) == 1 and crashed[0]["settlement"]["evidence"] == "REAPER_RUSAGE", "crashed run settled exactly")
    return {"orphans_reconciled": 2}


@scenario("worker death after durable seal is recoverable", "crash recovery", "atomic sealing")
def s09_durable_output_then_death(scratch):
    c = Campaign(scratch, "s09a", cells=[0, 1], cores=[0], plan={"0": ["write_then_hang"]})
    p = c.start(keep=True)
    st = c.wait_for(lambda s: attempts(s, cell=0, status="RUNNING"), what="cell 0 RUNNING")
    record = c.root / attempts(st, cell=0)[0][1]["record"]
    deadline = time.monotonic() + 30
    while not record.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    check(record.exists(), "worker wrote its record")
    os.kill(json.loads((c.root / "campaign.owner.json").read_text())["pid"], signal.SIGKILL)
    c.finish(p)
    code, _ = c.run(keep=True)
    st = c.validate()
    (_, a), = attempts(st, cell=0)
    check(code == PS.EXIT_COMPLETE and a["status"] == "SEALED" and a["seal"]["recovered"] is True
          and a["charge_evidence"] == "REAPER_RUSAGE", f"recovered seal {a['status']} {a['charge_evidence']}")
    c2 = Campaign(scratch, "s09b", cells=[0, 1], cores=[0], plan={"0": ["write_then_selfkill"]})
    code2, _ = c2.run(keep=True)
    st2 = c2.validate()
    (_, b), = attempts(st2, cell=0)
    check(code2 == PS.EXIT_COMPLETE and b["status"] == "SEALED" and b["seal"]["exit"]["signal"] == signal.SIGKILL,
          "a verifying record from a worker that then died is sealed, once")
    return {"recovered_after_supervisor_death": True, "sealed_after_worker_signal": True}


@scenario("stale reservation", "crash recovery", "restart-safe reservation handling")
def s10_stale_reservation_and_unreaped_orphan(scratch):
    c = Campaign(scratch, "s10a", cells=[0, 1], cores=[0])
    crash = (f"import json, os, sys\nsys.path.insert(0, {str(CODE)!r})\nimport prod_supervisor as PS\n"
             f"from prod_spec import CampaignSpec\n"
             f"spec = CampaignSpec.synthetic(json.load(open({c.cfg['config_path']!r})))\n"
             "class Crash(PS.Supervisor):\n    def _spawn(self, led, aid):\n        os._exit(99)\n"
             "raise SystemExit(Crash(spec).run())\n")
    r = subprocess.run([sys.executable, "-B", "-c", crash], capture_output=True, text=True, timeout=120)
    check(r.returncode == 99, f"crash harness exit {r.returncode}: {r.stderr[-300:]}")
    st = c.state()
    (aid, a), = attempts(st)
    check(a["status"] == "RESERVED" and a["pid"] is None, "a stale reservation with no process was left behind")
    code, out = c.run(keep=False)
    check(code == PS.EXIT_COMPLETE, f"exit {code}: {out[-400:]}")
    st = c.validate()
    t = st["attempts"][aid]
    check(t["status"] == "TORN" and t["tear_kind"] == L.ORPHAN and t["charge_evidence"] == "TAIL_BOUND_NOW"
          and t["charge_usec"] > 0, f"stale reservation reconciled: {t['status']} {t['charge_evidence']}")
    check(st["cells"]["0"]["status"] == "SEALED" and st["cells"]["0"]["infra_tears"] == 1, "cell retried")
    check(any(r_["settlement"] and r_["settlement"]["evidence"] == "TAIL_BOUND_NOW"
              for r_ in st["supervisor_runs"].values()), "crashed run settled by tail bound")

    c2 = Campaign(scratch, "s10b", cells=[0, 1], cores=[0], plan={"0": ["hang", "ok"]})
    p = c2.start(keep=False)
    st = c2.wait_for(lambda s: attempts(s, cell=0, status="RUNNING"), what="cell 0 RUNNING")
    worker = attempts(st, cell=0)[0][1]["pid"]
    os.kill(p.pid, signal.SIGKILL)
    c2.finish(p)
    check(wait_pid_dead(worker), "orphaned worker died with its supervisor")
    code2, _ = c2.run(keep=False)
    st2 = c2.validate()
    t2 = attempts(st2, cell=0)[0][1]
    check(code2 == PS.EXIT_COMPLETE and t2["status"] == "TORN" and t2["charge_evidence"] == "TAIL_BOUND_NOW",
          "orphan without keeper evidence charged by the tail bound")
    return {"stale_reservation_charge_usec": t["charge_usec"], "unreaped_orphan_charge_usec": t2["charge_usec"]}


@scenario("crash recovery", "stale incompatible run state")
def s11_live_orphan_refused(scratch):
    c = Campaign(scratch, "s11", cells=[0, 1], cores=[0])
    sleeper = subprocess.Popen(["/bin/sleep", "600"])
    try:
        lock = L.CampaignLock(c.root)
        lock.acquire({"tool": "acceptance"})
        try:
            led = L.Ledger(c.spec, lock)
            led.open(allow_genesis=True)
            ticks = (proc_stat(sleeper.pid) or {}).get("starttime")
            aid = led.txn("RESERVED", lambda s: L.op_reserve(s, c.spec, 0, 0, "MANUAL"))
            led.txn("RUNNING", lambda s: L.op_running(s, aid, sleeper.pid, ticks, time.time()))
        finally:
            lock.release()
        code, out = c.run(keep=False)
        check(code == PS.EXIT_REFUSED and refused_with(out, "LIVE_ORPHAN_WORKER"), f"exit {code}")
        check(sleeper.poll() is None, "the live worker was neither adopted nor killed")
        check(len(c.state()["attempts"]) == 1, "no admission beside a live orphan")
    finally:
        sleeper.kill()
        sleeper.wait()
    code2, _ = c.run(keep=False)
    check(code2 == PS.EXIT_COMPLETE, f"exit {code2}")
    return {"refused_while_alive": True}


@scenario("duplicate launch cannot create duplicate results", "duplicate-cell rule")
def s12_duplicate_launch_prevented(scratch):
    c = Campaign(scratch, "s12a", cells=list(range(6)), cores=[0, 2], plan={str(i): ["slow"] for i in range(6)},
                 slow_s=1.0)
    p = c.start(keep=True)
    c.wait_for(lambda s: attempts(s, status="RUNNING"), what="first supervisor running")
    code_b, out_b = c.run(keep=False)
    check(code_b == PS.EXIT_REFUSED and refused_with(out_b, "ANOTHER_SUPERVISOR_LIVE"), f"second launch exit {code_b}")
    code_a, _ = c.finish(p)
    st = c.validate()
    check(code_a == PS.EXIT_COMPLETE and len(st["attempts"]) == 6, "one attempt per cell")
    c2 = Campaign(scratch, "s12b", cells=list(range(6)), cores=[0, 2])
    procs = [c2.start(keep=False) for _ in range(3)]
    codes = sorted(c2.finish(q)[0] for q in procs)
    st2 = c2.validate()
    check(PS.EXIT_COMPLETE in codes and set(codes) <= {PS.EXIT_COMPLETE, PS.EXIT_REFUSED}, f"race exits {codes}")
    check(len(st2["attempts"]) == 6 and count(st2, "SEALED") == 6, "the race produced one sealed record per cell")
    s = copy.deepcopy(st2)
    s["disposition"] = "OPEN"                                    # test the cell rule, not the terminal rule
    expect_refusal("DUPLICATE_CELL", L.op_reserve, s, c2.spec, 0, 4, "T")
    forged = copy.deepcopy(st2)
    aid, a = attempts(forged, cell=0)[0]
    forged["attempts"]["A99999-C0000"] = copy.deepcopy(a)
    forged["committed_usec"]["science"] += a["charge_usec"]
    expect_refusal("DUPLICATE_SEALED_CELL", L.validate_state, forged, c2.spec)
    return {"race_exit_codes": codes}


@scenario("already-sealed cells are skipped", "skip/resume", "deterministic resume")
def s13_sealed_skip_deterministic_resume(scratch):
    c = Campaign(scratch, "s13", cells=list(range(10)), cores=[0], plan={str(i): ["slow"] for i in range(10)},
                 slow_s=0.6)
    p = c.start(keep=True)
    c.wait_for(lambda s: count(s, "SEALED") >= 3, what="three sealed")
    atomic_write_bytes(c.root / "DRAIN", b"DRAIN\n")
    code, _ = c.finish(p)
    check(code == PS.EXIT_DRAINED, f"exit {code}")
    st = c.validate()
    early = {a["cell"]: sha256_file(c.root / a["record"]) for _, a in attempts(st, status="SEALED")}
    os.unlink(c.root / "DRAIN")
    code2, _ = c.run(keep=True)
    st2 = c.validate()
    check(code2 == PS.EXIT_COMPLETE and len(st2["attempts"]) == 10, "no sealed cell re-admitted")
    check(all(sha256_file(c.root / attempts(st2, cell=k)[0][1]["record"]) == v for k, v in early.items()),
          "sealed records untouched by the resume")
    order = [a["cell"] for _, a in attempts(st2)]
    check(order == sorted(order), f"admission order {order}")
    return {"sealed_before_resume": sorted(early), "admission_order": order}


@scenario("corrupted evidence refusal", "sealed-cell rule")
def s14_corrupted_sealed_evidence_refused(scratch):
    c = Campaign(scratch, "s14", cells=list(range(5)), cores=[0], plan={str(i): ["slow"] for i in range(5)},
                 slow_s=0.6)
    p = c.start(keep=True)
    c.wait_for(lambda s: count(s, "SEALED") >= 2, what="two sealed")
    atomic_write_bytes(c.root / "DRAIN", b"DRAIN\n")
    c.finish(p)
    os.unlink(c.root / "DRAIN")
    st = c.validate()
    record = c.root / attempts(st, status="SEALED")[0][1]["record"]
    original = record.read_bytes()
    os.chmod(record, 0o644)
    record.write_bytes(original.replace(b"{", b"{ ", 1))
    code, out = c.run(keep=False)
    check(code == PS.EXIT_REFUSED and refused_with(out, "SEALED_EVIDENCE_CORRUPT"), f"exit {code}")
    check(c.state()["seq"] == st["seq"], "refusal did not mutate the ledger")
    lock, led = c.open_ledger()
    try:
        expect_refusal("SEALED_EVIDENCE_CORRUPT", L.export_bundle, led, c.dir / "export")
    finally:
        lock.release()
    record.write_bytes(original)
    os.chmod(record, 0o444)
    code2, _ = c.run(keep=True)
    check(code2 == PS.EXIT_COMPLETE, f"exit {code2}")
    return {"refused": "SEALED_EVIDENCE_CORRUPT"}


@scenario("no silent reuse of qualification records", "corrupted evidence refusal",
          "production seal accepts the frozen producer's record format")
def s15_qualification_records_never_production(scratch):
    prod = CampaignSpec.production()
    d = scratch / "s15"
    d.mkdir()
    q = QUALIFICATION_RECORDS["318A"]
    copy_path = d / "aux5_CUSUM_318_256.json"
    shutil.copyfile(q, copy_path)
    expect_refusal("QUALIFICATION_RECORD_REUSE", verify_record, copy_path, cell=318, spec=prod)
    rec = json.loads(q.read_text())
    rec["wall_seconds"] += 0.5                                   # INCIDENTAL: the scientific hash is unchanged
    edited = d / "edited" / "aux5_CUSUM_318_256.json"
    edited.parent.mkdir()
    edited.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    facts = verify_record(edited, cell=318, spec=prod)          # structure/identity/hash: the real format passes
    check(facts["scientific_content_hash"] == rec["scientific_content_hash"], "hash semantics")
    expect_refusal("CPU_EVIDENCE_INCONSISTENT", verify_record, edited, cell=318, spec=prod,
                   measured_cpu_usec=5_000_000, wall_bound_s=5.0)
    expect_refusal("RECORD_PREDATES_ATTEMPT", verify_record, edited, cell=318, spec=prod,
                   not_before_wall=time.time() + 60)
    expect_refusal("CELL_IDENTITY", verify_record, edited, cell=323, spec=prod)
    synth = Campaign(scratch, "s15_synth", cells=[318], cores=[0])
    expect_refusal("QUALIFICATION_RECORD_REUSE", verify_record, copy_path, cell=318, spec=synth.spec)
    return {"real_record_format_accepted_by_production_seal": True,
            "note": "verify_record calls on scratch copies only; no ledger, nothing sealed"}


@scenario("checkpoint/export/resume", "checkpoint/resume preserves scientific identity")
def s16_export_restore_resume(scratch):
    ref = Campaign(scratch, "s16_ref", cells=list(range(8)), cores=[0, 2])
    check(ref.run(keep=True)[0] == PS.EXIT_COMPLETE, "reference run")
    reference = sealed_hashes(ref.validate())
    c = Campaign(scratch, "s16", checkpoint_sha256="SYNTHETIC-s16-shared", cells=list(range(8)), cores=[0],
                 plan={str(i): ["slow"] for i in range(8)}, slow_s=0.5)
    p = c.start(keep=True)
    c.wait_for(lambda s: count(s, "SEALED") >= 3, what="three sealed")
    atomic_write_bytes(c.root / "DRAIN", b"DRAIN\n")
    c.finish(p)
    os.unlink(c.root / "DRAIN")
    lock, led = c.open_ledger()
    try:
        manifest = L.export_bundle(led, c.dir / "bundle")
        before = sealed_hashes(led.state)
    finally:
        lock.release()
    check(len(list((c.dir / "bundle/k4_records").glob("*.json"))) == len(before), "K4 export layout")
    bad = c.dir / "bundle_bad"
    shutil.copytree(c.dir / "bundle", bad)
    victim = bad / next(iter(manifest["files"].keys() - {"ledger.json", "journal.jsonl", "reaper.jsonl"}))
    os.chmod(victim, 0o644)
    victim.write_bytes(victim.read_bytes().replace(b"{", b"{ ", 1))
    moved = Campaign(scratch, "s16_restored", checkpoint_sha256="SYNTHETIC-s16-shared", cells=list(range(8)),
                     cores=[0, 2])
    expect_refusal("EXPORT_CORRUPT", L.restore_bundle, moved.spec, bad)
    other = Campaign(scratch, "s16_other", cells=list(range(8)), cores=[0, 2])
    expect_refusal("INCOMPATIBLE_RUN_STATE", L.restore_bundle, other.spec, c.dir / "bundle")
    restored = L.restore_bundle(moved.spec, c.dir / "bundle")
    expect_refusal("STALE_INCOMPATIBLE_RUN_STATE", L.restore_bundle, moved.spec, c.dir / "bundle")
    code, _ = moved.run(keep=True)
    final = sealed_hashes(moved.validate())
    check(code == PS.EXIT_COMPLETE, f"resume exit {code}")
    check(all(final[k] == v for k, v in before.items()), "sealed hashes preserved across export/restore")
    check(final == reference, "resumed campaign is scientifically identical to an uninterrupted run")
    return {"exported_sealed": len(before), "restored_seq": restored["restored_seq"]}


@scenario("cap: normal progress", "cap: near-cap admission", "cap arithmetic")
def s17_cap_admission_boundary(scratch):
    check(L.admission_allowed(769, 0, 100, 1000) and not L.admission_allowed(770, 0, 100, 1000), "integer boundary")
    check(L.admission_allowed(0, 769, 100, 1000) and not L.admission_allowed(0, 770, 100, 1000), "open == committed")
    c = Campaign(scratch, "s17", cells=[0, 1, 2], cores=[0, 2, 4], cap_usec=1000, reservation_usec=100)
    lock = L.CampaignLock(c.root)
    lock.acquire({"tool": "acceptance"})
    try:
        led = L.Ledger(c.spec, lock)
        led.open(allow_genesis=True)
        st = copy.deepcopy(led.state)
        L.op_charge_overhead(st, [("fixture-669", 669)])
        L.op_reserve(st, c.spec, 0, 0, "T")                          # 115*(669+0+100)   <= 100*1000
        L.op_reserve(st, c.spec, 1, 2, "T")                          # 115*(669+100+100) =  99935
        expect_refusal("CAP_ADMISSION_DENIED", L.op_reserve, st, c.spec, 2, 4, "T")
        st2 = copy.deepcopy(led.state)
        L.op_charge_overhead(st2, [("fixture-670", 670)])
        L.op_reserve(st2, c.spec, 0, 0, "T")
        expect_refusal("CAP_ADMISSION_DENIED", L.op_reserve, st2, c.spec, 1, 2, "T")   # 115*870 = 100050
        st3 = copy.deepcopy(led.state)
        L.op_charge_overhead(st3, [("fixture-500", 500)])
        aid = L.op_reserve(st3, c.spec, 0, 0, "T")
        L.op_sample(st3, aid, 300, time.time())                     # measured CPU above R counts in flight
        expect_refusal("CAP_ADMISSION_DENIED", L.op_reserve, st3, c.spec, 1, 2, "T")   # 115*(500+300+100) > 100000
    finally:
        lock.release()
    cp, _sha = load_frozen_checkpoint()
    cap, r = cp["cost_cap"]["cap_usec"], cp["cost_cap"]["reservation_usec"]
    cmax = int(float(cp["cost_cap"]["c_max_cpu_seconds"]) * 1_000_000)
    check(cp["cost_cap"]["cap_cpu_h"] == 300 and r == 3_600_000_000, "frozen cap and reservation")
    check(L.admission_allowed(325 * cmax, 3 * r, r, cap), "326 cells at c_max fit the invariant at the last admission")
    headroom_h = (100 * cap / 115 - (325 * cmax + 4 * r)) / 3.6e9
    return {"production_last_admission_headroom_cpu_h": round(headroom_h, 2)}


@scenario("cap exhaustion prevents new admissions", "cap cannot be raised after production starts",
          "cap exhaustion produces an incomplete/budget disposition")
def s18_cap_exhaustion_and_no_raise(scratch):
    c = Campaign(scratch, "s18", cells=list(range(12)), cores=[0], cap_usec=4_000_000, reservation_usec=1_000_000,
                 burn_s=0.3)
    code, out = c.run(keep=True)
    check(code == PS.EXIT_BUDGET, f"exit {code}: {out[-400:]}")
    st = c.validate()
    b = st["budget_exhaustion"]
    check(st["disposition"] == "INCOMPLETE_BUDGET_EXHAUSTED" and b and b["pending_cells"], "budget disposition")
    check(not attempts(st, status="RESERVED") and not attempts(st, status="RUNNING"), "nothing in flight")
    check(115 * (L.committed_total(st) + c.spec.reservation_usec) > 100 * c.spec.cap_usec, "denial is exact")
    check(count(st, "SEALED") >= 1, "progress was made before exhaustion")
    seq = st["seq"]
    code2, _ = c.run(keep=False)
    check(code2 == PS.EXIT_BUDGET and c.state()["seq"] == seq, "an exhausted campaign never admits again")
    c.cfg["cap_usec"] = 10 ** 12
    c.save()
    code3, out3 = c.run(keep=False)
    check(code3 == PS.EXIT_REFUSED and refused_with(out3, "CAP_CHANGE_FORBIDDEN") and c.state()["seq"] == seq,
          "raising the cap after admissions is refused")
    return {"sealed_before_exhaustion": count(st, "SEALED"), "pending": len(b["pending_cells"]),
            "committed_usec": L.committed_total(st)}


@scenario("restart with preserved accounting", "cumulative CPU accounting", "retry/recovery accounting explicit")
def s19_restart_preserves_accounting(scratch):
    c = Campaign(scratch, "s19", cells=list(range(6)), cores=[0], plan={str(i): ["slow"] for i in range(6)},
                 slow_s=0.6)
    snapshots = []
    p = c.start(keep=True)
    c.wait_for(lambda s: count(s, "SEALED") >= 2, what="two sealed")
    os.kill(p.pid, signal.SIGTERM)
    check(c.finish(p)[0] == PS.EXIT_DRAINED, "drain")
    snapshots.append(c.validate()["committed_usec"])
    p = c.start(keep=True)
    c.wait_for(lambda s: count(s, "SEALED") >= 3 and attempts(s, status="RUNNING"), what="third sealed, one running")
    os.kill(json.loads((c.root / "campaign.owner.json").read_text())["pid"], signal.SIGKILL)
    c.finish(p)
    snapshots.append(c.validate()["committed_usec"])
    check(c.run(keep=True)[0] == PS.EXIT_COMPLETE, "resume")
    snapshots.append(c.validate()["committed_usec"])
    st = c.settle()
    snapshots.append(st["committed_usec"])
    L.validate_state(st, c.spec)
    for a, b in zip(snapshots, snapshots[1:]):
        check(all(b[k] >= a[k] for k in L.BUCKETS), f"accounting never decreases: {a} -> {b}")
    keeper_exits = [r["record_id"] for r in c.reaper() if r["kind"] == "KEEPER_EXIT"]
    check(len(keeper_exits) == 3 and set(keeper_exits) <= set(st["overhead_charges"]), "each keeper exit charged once")
    check(all(r["settled"] for r in st["supervisor_runs"].values()) and len(st["supervisor_runs"]) == 3, "runs settled")
    ends = sorted(r["end"] for r in st["supervisor_runs"].values())
    check(ends == ["CRASHED", "EXITED", "EXITED"], f"run ends {ends}")
    check(st["committed_usec"]["torn"] > 0, "the attempt lost with the crashed supervisor is charged")
    return {"snapshots": snapshots}


@scenario("corrupted accounting state refusal", "crash-safe reconciliation")
def s20_corrupted_accounting_state_refused(scratch):
    base = Campaign(scratch, "s20_base", checkpoint_sha256="SYNTHETIC-s20", cells=list(range(4)), cores=[0],
                    plan={str(i): ["slow"] for i in range(4)}, slow_s=0.4)
    p = base.start(keep=True)
    base.wait_for(lambda s: count(s, "SEALED") >= 1, what="one sealed")
    old_ledger = (base.root / "ledger.json").read_bytes()
    base.wait_for(lambda s: count(s, "SEALED") >= 2, what="two sealed")
    atomic_write_bytes(base.root / "DRAIN", b"DRAIN\n")
    base.finish(p)
    os.unlink(base.root / "DRAIN")

    def variant(name, mutate):
        v = Campaign(scratch, f"s20_{name}", checkpoint_sha256="SYNTHETIC-s20", cells=list(range(4)), cores=[0])
        shutil.copytree(base.root, v.root)
        mutate(v.root)
        return v

    def edit(root, fn):
        st = json.loads((root / "ledger.json").read_text())
        fn(st)
        atomic_write_json(root / "ledger.json", st)

    cases = {
        "naive_edit": ("LEDGER_ROLLBACK_OR_MUTATION",
                       lambda r: edit(r, lambda s: s["committed_usec"].__setitem__("science", s["committed_usec"]["science"] - 1))),
        "forged_accounting": ("ACCOUNTING_CORRUPT",
                              lambda r: forge_next_state(r, lambda s: s["committed_usec"].__setitem__("science", s["committed_usec"]["science"] - 1))),
        "forged_cap_raise": ("CAP_CHANGE_FORBIDDEN",
                             lambda r: forge_next_state(r, lambda s: s["cap"].__setitem__("cap_usec", s["cap"]["cap_usec"] * 2))),
        "forged_negative_charge": ("ACCOUNTING_CORRUPT",
                                   lambda r: forge_next_state(r, lambda s: next(a for a in s["attempts"].values()).__setitem__("charge_usec", -5))),
        "truncated_ledger": ("LEDGER_CORRUPT",
                             lambda r: (r / "ledger.json").write_bytes((r / "ledger.json").read_bytes()[:200])),
        "deleted_ledger": ("LEDGER_MISSING", lambda r: os.unlink(r / "ledger.json")),
        "deleted_journal": ("UNSANCTIONED_LEDGER", lambda r: os.unlink(r / "journal.jsonl")),
        "rolled_back_ledger": ("LEDGER_ROLLBACK_OR_MUTATION", lambda r: (r / "ledger.json").write_bytes(old_ledger)),
        "broken_chain": ("JOURNAL_CORRUPT",
                         lambda r: (r / "journal.jsonl").write_text((r / "journal.jsonl").read_text().replace('"seq": 1,', '"seq": 7,', 1))),
    }
    results = {}
    for name, (code_expected, mutate) in cases.items():
        v = variant(name, mutate)
        before = (v.root / "ledger.json").read_bytes() if (v.root / "ledger.json").exists() else None
        code, out = v.run(keep=False)
        after = (v.root / "ledger.json").read_bytes() if (v.root / "ledger.json").exists() else None
        check(code == PS.EXIT_REFUSED and refused_with(out, code_expected), f"{name}: exit {code}, wanted {code_expected}")
        check(before == after, f"{name}: the refusal wrote nothing")
        results[name] = code_expected
    for name, cut in (("journal_behind_one", False), ("journal_torn_tail", True)):
        def behind(r, torn=cut):
            lines = (r / "journal.jsonl").read_text().splitlines()
            forge_next_state(r, lambda s: None)
            text = "\n".join(lines) + "\n"
            if torn:
                forged_line = (r / "journal.jsonl").read_text().splitlines()[-1]
                text += forged_line[: len(forged_line) // 2]
            (r / "journal.jsonl").write_text(text)
        v = variant(name, behind)
        code, out = v.run(keep=True)
        check(code == PS.EXIT_COMPLETE, f"{name}: exit {code}: {out[-300:]}")
        v.validate()
        results[name] = "REPAIRED_AND_RESUMED"
    return results


@scenario("wrong runtime contract refusal")
def s21_wrong_runtime_contract_refused(scratch):
    rep = PE.preflight(overrides={"probe_env_extra": {"OPENBLAS_CORETYPE": "Sandybridge"}})
    c06 = next(c for c in rep["checks"] if c["check"] == "C06_runtime_contract")
    check(not rep["ready"] and c06["status"] == "FAIL" and c06["code"] == "RUNTIME_CONTRACT"
          and "openblas_runtime_corename" in c06["detail"], f"C06 {c06}")
    return {"C06": {k: c06[k] for k in ("status", "code")}, "detail": c06["detail"][:160]}


@scenario("wrong producer identity refusal")
def s22_wrong_producer_identity_refused(scratch):
    cp, _sha = load_frozen_checkpoint()
    ident = cp["producer"]["record_identity"]
    fake = {"ok": True, "problems": [], "files": cp["producer"]["tcb_files"],
            "producer_manifest_hash": ident["producer_manifest_hash"],
            "runtime_contract_hash": ident["runtime_contract_hash"], "producer_identity_hash": "0" * 64}
    rep = PE.preflight(overrides={"probe": fake})
    c06 = next(c for c in rep["checks"] if c["check"] == "C06_runtime_contract")
    check(not rep["ready"] and c06["status"] == "FAIL" and c06["code"] == "PRODUCER_IDENTITY", f"C06 {c06}")
    wt = scratch / "s22_tampered_worktree"
    subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(wt), "HEAD"], check=True,
                   capture_output=True)
    try:
        victim = wt / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/intervals.py"
        victim.write_text(victim.read_text() + "\n")
        rep2 = PE.preflight(overrides={"probe_root": str(wt)})
        c06b = next(c for c in rep2["checks"] if c["check"] == "C06_runtime_contract")
        check(c06b["status"] == "FAIL" and "content changed" in c06b["detail"], f"tampered TCB: {c06b}")
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)], capture_output=True)
    return {"fake_identity": c06["code"], "tampered_tcb": c06b["detail"][:160]}


@scenario("wrong host refusal")
def s23_wrong_host_refused(scratch):
    live = host_facts()
    rep = PE.preflight(overrides={"host_facts": {**live, "host_name": "rebaseguard-vultr-01"}})
    c04 = next(c for c in rep["checks"] if c["check"] == "C04_host_identity")
    check(not rep["ready"] and c04["status"] == "FAIL" and c04["code"] == "WRONG_HOST", f"C04 {c04}")
    guard = host_facts(with_package=False)
    c = Campaign(scratch, "s23", cells=[0, 1], cores=[0], host_expected={**guard, "kernel_release": "0.0.0-other"})
    code, _ = c.run(keep=False)
    st = c.validate()
    check(code == PS.EXIT_HALTED and st["halt"]["reason"] == "HOST_DRIFT" and not st["attempts"],
          "a host drift halts before any admission")
    return {"C04": c04["code"], "admission_guard": "HOST_DRIFT"}


@scenario("production isolation", "no permissive fallback")
def s24_production_isolation(scratch):
    check(not PRODUCTION_RUNTIME_ROOT.exists(), "the production runtime root does not exist")
    c = Campaign(scratch, "s24", cells=[0], cores=[0])
    expect_refusal("SYNTHETIC_PRODUCTION_MIX", CampaignSpec.synthetic, {**c.cfg, "root": str(PRODUCTION_RUNTIME_ROOT / "x")})
    expect_refusal("SYNTHETIC_PRODUCTION_MIX", CampaignSpec.synthetic, {**c.cfg, "checkpoint_sha256": "not-synthetic"})
    check(c.run(keep=False)[0] == PS.EXIT_COMPLETE, "synthetic run")
    record = c.root / attempts(c.state())[0][1]["record"]
    expect_refusal("SYNTHETIC_PRODUCTION_MIX", verify_record, record, cell=0, spec=CampaignSpec.production())
    c2 = Campaign(scratch, "s24_keeper", cells=[0], cores=[0])
    spec = c2.spec
    spec.require_keeper = True
    code = subprocess.run([sys.executable, "-B", "-c",
                           f"import json, sys\nsys.path.insert(0, {str(CODE)!r})\nimport prod_supervisor as PS\n"
                           f"from prod_spec import CampaignSpec\n"
                           f"s = CampaignSpec.synthetic(json.load(open({c2.cfg['config_path']!r})))\n"
                           "s.require_keeper = True\nraise SystemExit(PS.Supervisor(s).run())\n"],
                          capture_output=True, text=True, timeout=60).returncode
    check(code == PS.EXIT_REFUSED and not c2.root.exists(), "a keeper-bound supervisor refuses to run without its keeper")
    check(PE.main(["launch", "--confirm-checkpoint-sha256", "0" * 64]) == PS.EXIT_REFUSED, "launch needs the exact sha")
    check(not PRODUCTION_RUNTIME_ROOT.exists(), "the production runtime root is still absent")
    return {"production_root_absent": True}


@scenario("entrypoint fails closed before the freeze", "entrypoint checks")
def s25_preflight_before_freeze(scratch):
    rep = PE.preflight()
    status = {c["check"]: c["status"] for c in rep["checks"]}
    expected_fail = {"C01_checkpoint_and_freeze", "C12_synthetic_acceptance"}
    check(not rep["ready"], "not READY before the freeze record and acceptance exist")
    check({k for k, v in status.items() if v == "FAIL"} == expected_fail,
          f"only the freeze-dependent checks may fail: {[c for c in rep['checks'] if c['status'] == 'FAIL']}")
    return {"status": status}


@scenario("full 326-cell synthetic ledger", "K4 structural attestation gate", "integrity attestation")
def s26_full_synthetic_campaign_and_k4_gate(scratch):
    c = Campaign(scratch, "s26", cells=list(range(326)), cores=[0, 2, 4, 6], burn_s=0.02, heartbeat_s=1.0,
                 reservation_usec=2_000_000)
    code, out = c.run(keep=True, timeout=1800)
    check(code == PS.EXIT_COMPLETE, f"exit {code}: {out[-400:]}")
    st = c.settle()
    check(count(st, "SEALED") == 326 and len(st["attempts"]) == 326, "326 sealed, one attempt each")
    att = K4A.build_integrity_attestation(c.spec, st, checkpoint_sha256=c.spec.checkpoint_sha256)
    att_path = c.dir / "attestation.json"
    atomic_write_json(att_path, att)
    lock, led = c.open_ledger()
    try:
        L.export_bundle(led, c.dir / "bundle")
    finally:
        lock.release()
    k4_dir = c.dir / "bundle/k4_records"
    records = [json.loads(p.read_text()) for p in sorted(k4_dir.glob("*.json"))]
    check(len(records) == 326, "K4 records directory holds exactly the sealed cells")
    cp, _sha = load_frozen_checkpoint()
    path = K4_NS / "code/k4_assembly.py"
    check(sha256_file(path) == cp["k4"]["k4_assembly_sha256"], "frozen k4_assembly.py")
    mod_spec = importlib.util.spec_from_file_location("k4_assembly_frozen", path)
    k4 = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(k4)
    k4.check_cusum_attestation(att_path, records)                  # integrity gate only; assemble() is never called
    short = {**att, "cells_verified": 325}
    atomic_write_json(c.dir / "short.json", short)
    try:
        k4.check_cusum_attestation(c.dir / "short.json", records)
        raise Fail("K4 accepted an incomplete attestation")
    except k4.AssemblyRefusal:
        pass
    foreign = copy.deepcopy(records)
    foreign[0]["producer_identity_hash"] = "0" * 64
    try:
        k4.check_cusum_attestation(att_path, foreign)
        raise Fail("K4 accepted a record from another producer")
    except k4.AssemblyRefusal:
        pass
    return {"cells": 326, "committed_cpu_s": round(L.committed_total(st) / 1e6, 2), "k4_gate": "accepted",
            "k4_assembly_run": False}


# ====================================================================== driver
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    scratch = Path(a.scratch).resolve()
    scratch.mkdir(parents=True, exist_ok=False)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        _cp, sha = load_frozen_checkpoint()
        bound_ok = True
    except Refusal as r:
        sha, bound_ok = f"UNAVAILABLE: {r}", False
    root_absent_before = not PRODUCTION_RUNTIME_ROOT.exists()
    results, coverage = {}, {}
    for name, covers, fn in SCENARIOS:
        if a.only and name not in a.only:
            continue
        t0 = time.monotonic()
        try:
            details = fn(scratch)
            results[name] = {"status": "PASS", "seconds": round(time.monotonic() - t0, 1), "details": details}
        except Exception as exc:                                      # noqa: BLE001
            results[name] = {"status": "FAIL", "seconds": round(time.monotonic() - t0, 1),
                             "error": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc()[-1500:]}
        for cv in covers:
            coverage.setdefault(cv, []).append(name)
        print(f"{results[name]['status']:4s} {results[name]['seconds']:7.1f}s  {name}"
              + ("" if results[name]["status"] == "PASS" else f"  -- {results[name]['error'][:300]}"), flush=True)
    try:
        _cp2, sha_after = load_frozen_checkpoint()
    except Refusal as r:
        sha_after = f"UNAVAILABLE: {r}"
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    ok = (bound_ok and sha == sha_after and root_absent_before and not PRODUCTION_RUNTIME_ROOT.exists()
          and not a.only and all(r["status"] == "PASS" for r in results.values()))
    doc = {"schema": PE.ACCEPTANCE_SCHEMA, "CUSUM_SYNTHETIC_ACCEPTANCE": "PASS" if ok else "FAIL",
           "checkpoint_sha256": sha, "checkpoint_unchanged_during_run": sha == sha_after,
           "bound_sources_verified": bound_ok, "host_name": socket.gethostname(), "git_head": head,
           "python": sys.version.split()[0], "started_utc": started,
           "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "non_result_bearing": True, "frozen_certifier_started": False, "production_launched": False,
           "production_runtime_root_absent_before_and_after": root_absent_before and not PRODUCTION_RUNTIME_ROOT.exists(),
           "scratch": str(scratch), "scenarios": results, "coverage": coverage}
    atomic_write_json(a.out, doc)
    print(json.dumps({"CUSUM_SYNTHETIC_ACCEPTANCE": doc["CUSUM_SYNTHETIC_ACCEPTANCE"],
                      "passed": sum(r["status"] == "PASS" for r in results.values()), "total": len(results)}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
