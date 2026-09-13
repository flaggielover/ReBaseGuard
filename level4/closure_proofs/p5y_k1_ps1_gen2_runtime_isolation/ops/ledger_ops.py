"""Crash-consistent accounting on top of the FROZEN global ledger.

No frozen line is modified. The frozen ledger schema is extended only ADDITIVELY
(an `operational_lifecycle` top-level block, which the frozen code preserves on
every rewrite) and through ordinary `open_reservations` entries that the frozen
`_governed_total` already counts (every entry carries `role` and
`reserved_cpu_h`).

THE INVARIANT (at every frozen admission, through crash and restart):

  1.15 * ( committed_cpu_h_all_roles              # finalised, incl. settled runs
         + sum(open cell reservations)              # frozen in-flight arithmetic
         + TORN escrows                             # released attempts, never dropped
         + SHADOW(run)                              # measured-but-uncommitted run CPU
         + requested reservation
         + governed overhead ) <= 4500

  SHADOW(run) = max(0, U_run - C_run - R_run) + E_stale
     U_run  exact CPU of the run's whole process tree (cgroup), sampled every
            poll interval and fsync'd into the ledger;
     C_run  science CPU committed by the frozen commit() during this run;
     R_run  run-owned open reservations (cells + torn escrows);
     E_stale = 2 * poll_interval_s * online_cpus / 3600  (covers the sampling lag).

  Hence ledger-visible charge >= CPU actually consumed, at every instant.

TORN ATTEMPT STATE MACHINE

  RESERVED/RUNNING --(frozen release(): worker failure / abort)--> TORN_ESCROW
  RESERVED/RUNNING --(abrupt loss: kill, crash, reboot)---------> ORPHAN
  TORN_ESCROW | ORPHAN --(settlement with EXACT run CPU)--------> RECOVERED_TORN
  RECOVERED_TORN --(infrastructure kind, torn count <= 2)-------> RETRY_ELIGIBLE
  RECOVERED_TORN --(worker-reported/malformed/unclassified)-----> HALTED (never retried)
  RECOVERED_TORN --(3rd infrastructure tear of the same cell)---> HALTED (retry limit)

SETTLEMENT (idempotent; one fsync'd atomic write):
  charge = max(0, U_final - C_run); every run-owned reservation is closed;
  committed[role] += charge. So the run is charged EXACTLY its measured CPU
  (science actuals + torn attempts + launcher overhead). Nothing is ever charged
  zero, nothing is reset, per-host caps do not exist.

CPU EVIDENCE HIERARCHY for U_final:
  1 SUPERVISOR_FINAL      cgroup usage read after every run process is dead
  2 EXECSTOPPOST_CGROUP   same, read by the systemd ExecStopPost fallback
  3 JOURNAL               systemd's persisted CPU_USAGE_NSEC for that invocation
  4 TAIL_BOUND            last fsync'd sample u + (t_death_upper - t_sample) * online_cpus,
                          t_death_upper = current boot time after a reboot, else now
                          (valid only once every run process is verified dead)
"""
from __future__ import annotations

import json
import linecache
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

from opscommon import (OpsRefusal, atomic_write, boot_id, boot_time, canonical,
                       journal_cpu_usage_usec, online_cpus, sha256_bytes, write_json_atomic)

OPS_FIELD = "operational_lifecycle"
OPS_SCHEMA = "rebaseguard.p5y.k1.sr.production.operational-lifecycle.v1"
SHADOW = "OPS:SHADOW:"
TORN = "OPS:TORN:"
MAX_INFRA_TEARS_PER_CELL = 3          # protocol: infrastructure failures retry at most twice

ABORT = "INFRASTRUCTURE_ABORT"
WORKER_FAILURE = "WORKER_REPORTED_FAILURE"
MALFORMED = "MALFORMED_RESULT"
UNCLASSIFIED = "UNCLASSIFIED_RELEASE"
DRAIN = "GRACEFUL_DRAIN"          # recovery successor: a boundary drain is NOT a tear
ORPHAN = "ORPHAN_RESERVATION"
HALTING = (WORKER_FAILURE, MALFORMED, UNCLASSIFIED)

# the exact frozen call sites of GlobalBudget.release() in run_production_cells
RELEASE_SITES = {"budget.release(key); continue": WORKER_FAILURE,
                 "budget.release(key)": MALFORMED,
                 "budget.release(k)": ABORT,
                 "budget.release(dkey)": DRAIN}


class ScientificHalt(RuntimeError):
    """A failure the protocol forbids retrying. The campaign stops."""


def usec(u, what="measured CPU") -> int:
    """Measured CPU is a non-negative integer of microseconds. Anything else refuses."""
    if isinstance(u, bool) or not isinstance(u, int) or u < 0:
        raise OpsRefusal(f"{what} is not a non-negative integer of microseconds: {u!r}")
    return u


def e_stale_cpu_h(poll_s: float, cpus: int) -> float:
    return 2.0 * poll_s * cpus / 3600.0


# ------------------------------------------------------------------ ledger io
class LedgerIO:
    def __init__(self, path, M, GB, budget):
        self.path, self.M, self.GB, self.budget = Path(path), M, GB, budget

    @contextmanager
    def locked(self):
        with self.GB._Lock(self.path):
            yield

    def read(self):
        if not self.path.exists():
            return None
        raw = self.path.read_bytes()
        try:
            st = json.loads(raw)
        except Exception as exc:                                  # noqa: BLE001
            raise OpsRefusal(f"production ledger is corrupt/partial: {exc}") from exc
        if st.get("schema") != self.GB.GlobalBudget.SCHEMA:
            raise OpsRefusal(f"production ledger schema {st.get('schema')!r}")
        return st

    def fresh(self):
        return {"schema": self.GB.GlobalBudget.SCHEMA, "committed_cpu_h_by_role": {},
                "open_reservations": {}, "completed_cells": {}, "remote_completed_cells": {}}

    def write(self, st):
        atomic_write(self.path, (json.dumps(st, indent=1, sort_keys=True) + "\n").encode(),
                     tmp=self.path.with_suffix(".tmp"))

    def v(self, x, what):
        return self.M.validate_governed_cost(x, what)

    def cap(self, st):
        """The frozen governed total. Returns (status, refusal-or-None)."""
        try:
            return self.budget._governed_total(st), None
        except Exception as exc:                                  # noqa: BLE001
            return None, str(exc)


def new_ops(role):
    return {"schema": OPS_SCHEMA, "role": role, "runs": {}, "settlements": [],
            "releases": [], "torn_attempts": {}, "halt": None}


def ops_of(st, role):
    ops = st.get(OPS_FIELD)
    if ops is None:
        raise OpsRefusal("ledger carries no operational lifecycle block (unsanctioned ledger)")
    if ops.get("schema") != OPS_SCHEMA or ops.get("role") != role:
        raise OpsRefusal(f"operational block role/schema mismatch: {ops.get('role')!r}")
    return ops


# ---------------------------------------------------------------- continuity
def ledger_view(st):
    if st is None:
        return None
    ops = st.get(OPS_FIELD) or {}
    return {"committed": {k: float(v) for k, v in st.get("committed_cpu_h_by_role", {}).items()},
            "completed": sorted(int(c) for c in st.get("completed_cells", {})),
            "remote_count": len(st.get("remote_completed_cells", {})),
            "remote_hash": st.get("remote_handoff_payload_hash"),
            "settlements": len(ops.get("settlements", [])),
            "open_runs": sorted(r for r, x in ops.get("runs", {}).items() if x["status"] == "OPEN")}


def append_continuity(rt, event, st, extra=None):
    prev = last_continuity(rt)
    rec = {"seq": (prev["seq"] + 1) if prev else 0, "event": event, "t_wall": time.time(),
           "view": ledger_view(st), "extra": extra or {}}
    rec["prev_sha256"] = prev["sha256"] if prev else None
    rec["sha256"] = sha256_bytes(canonical({k: v for k, v in rec.items() if k != "sha256"}))
    rt.root.mkdir(parents=True, exist_ok=True)
    with open(rt.continuity, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return rec


def last_continuity(rt):
    if not rt.continuity.exists():
        return None
    lines = [l for l in rt.continuity.read_text().splitlines() if l.strip()]
    prev = None
    for l in lines:                       # verify the whole hash chain
        rec = json.loads(l)
        body = {k: v for k, v in rec.items() if k != "sha256"}
        if rec["sha256"] != sha256_bytes(canonical(body)) or \
                rec["prev_sha256"] != (prev["sha256"] if prev else None):
            raise OpsRefusal(f"continuity chain broken at seq {rec.get('seq')}")
        prev = rec
    return prev


def check_continuity(rt, st) -> dict:
    """Refuse a reset, rollback or unexplained mutation of the ledger."""
    last = last_continuity(rt)
    if last is None:
        if st is not None:
            raise OpsRefusal("UNSANCTIONED_LEDGER: a production ledger exists with no "
                             "continuity record (created outside the sanctioned lifecycle)")
        return {"state": "GENESIS"}
    lv = last["view"]
    if lv is None:                                   # only a GENESIS record so far
        if st is None:
            return {"state": "GENESIS", "seq": last["seq"]}
        now = ledger_view(st)
        if now["open_runs"]:
            return {"state": "CONTINUOUS_FROM_GENESIS"}
        if now["remote_hash"] and not now["completed"] and not now["settlements"]:
            append_continuity(rt, "RECONCILED", st, {"explained_by": {"handoff_import": now["remote_hash"]}})
            return {"state": "RECONCILED"}
        raise OpsRefusal(f"UNEXPLAINED_LEDGER_MUTATION after GENESIS: {now}")
    if st is None:
        raise OpsRefusal("LEDGER_MISSING: the production ledger vanished after "
                         f"{last['event']}; a deleted ledger would silently reset the budget")
    now = ledger_view(st)
    for role, v in lv["committed"].items():
        if now["committed"].get(role, 0.0) < v:
            raise OpsRefusal(f"LEDGER_ROLLBACK: committed[{role}] {now['committed'].get(role)} "
                             f"< recorded {v}")
    if not set(lv["completed"]).issubset(now["completed"]):
        raise OpsRefusal("LEDGER_ROLLBACK: completed cells disappeared")
    if lv["remote_hash"] and now["remote_hash"] != lv["remote_hash"]:
        raise OpsRefusal("LEDGER_ROLLBACK: imported handoff changed")
    if now["settlements"] < lv["settlements"]:
        raise OpsRefusal("LEDGER_ROLLBACK: settlements disappeared")
    if not now["open_runs"] and now != lv:
        why = explained_transition(last, lv, now, st)
        if why is None:
            raise OpsRefusal(f"UNEXPLAINED_LEDGER_MUTATION since {last['event']} with no "
                             f"sanctioned run open: recorded {lv} now {now}")
        append_continuity(rt, "RECONCILED", st, {"explained_by": why})
        return {"state": "RECONCILED", "explained_by": why}
    return {"state": "CONTINUOUS", "last_event": last["event"], "seq": last["seq"]}


def explained_transition(last, lv, now, st):
    """The ONLY two ledger changes allowed to precede their continuity record: a
    crash between the ledger write and the chain append of (a) a settlement of a
    run that was open at the last record, or (b) an authenticated handoff import."""
    ops = st.get(OPS_FIELD) or {}
    runs = ops.get("runs", {})
    if lv["open_runs"] and all(runs.get(r, {}).get("status") == "SETTLED" for r in lv["open_runs"]) \
            and now["settlements"] == lv["settlements"] + len(lv["open_runs"]):
        return {"settled_runs": lv["open_runs"]}
    if lv["remote_hash"] is None and now["remote_hash"] and now["completed"] == lv["completed"] \
            and now["settlements"] == lv["settlements"]:
        return {"handoff_import": now["remote_hash"]}
    return None


# ----------------------------------------------------------------- run open
def open_run(io, rt, role, run_id, *, unit, invocation_id, cpu_kind, e_stale, boot):
    if io.read() is None and last_continuity(rt) is None:
        append_continuity(rt, "GENESIS", None, {"role": role})
    with io.locked():
        st = io.read() or io.fresh()
        ops = st.setdefault(OPS_FIELD, new_ops(role))
        ops_of(st, role)
        if ops["halt"]:
            raise OpsRefusal(f"campaign HALTED: {ops['halt']}")
        if any(r["status"] == "OPEN" for r in ops["runs"].values()):
            raise OpsRefusal("an earlier run is not settled")
        if st.get("open_reservations"):
            raise OpsRefusal(f"open reservations exist before run start: {sorted(st['open_reservations'])}")
        committed_start = io.v(st.get("committed_cpu_h_by_role", {}).get(role, 0.0), "committed start")
        now = time.time()
        ops["runs"][run_id] = {"status": "OPEN", "role": role, "unit": unit,
                               "invocation_id": invocation_id, "cpu_source": cpu_kind,
                               "boot_id": boot, "started_wall": now,
                               "committed_start": committed_start,
                               "completed_start": sorted(int(c) for c in st.get("completed_cells", {})),
                               "e_stale_cpu_h": e_stale,
                               "last_sample": {"u_usec": 0, "t_wall": now, "boot_id": boot}}
        st.setdefault("open_reservations", {})[SHADOW + run_id] = {
            "role": role, "cell_id": None, "reserved_cpu_h": io.v(e_stale, "stale escrow"),
            "ops": {"kind": "SHADOW", "run_id": run_id}}
        cap, refusal = io.cap(st)
        if refusal:
            raise OpsRefusal(f"CAP: cannot open a run: {refusal}")
        io.write(st)
    append_continuity(rt, "RUN_OPENED", st, {"run_id": run_id})
    return cap


def update_shadow(io, role, run_id, u_usec, boot):
    u_usec = usec(u_usec, "shadow sample")
    with io.locked():
        st = io.read()
        ops = ops_of(st, role)
        run = ops["runs"][run_id]
        if run["status"] != "OPEN":
            return None
        c_run = io.v(st["committed_cpu_h_by_role"].get(role, 0.0) - run["committed_start"], "C_run")
        r_run = sum(io.v(r["reserved_cpu_h"], k) for k, r in st["open_reservations"].items()
                    if k != SHADOW + run_id)
        s = max(0.0, u_usec / 3.6e9 - c_run - r_run) + run["e_stale_cpu_h"]
        now = time.time()
        st["open_reservations"][SHADOW + run_id] = {
            "role": role, "cell_id": None, "reserved_cpu_h": io.v(s, "shadow"),
            "ops": {"kind": "SHADOW", "run_id": run_id, "u_usec": int(u_usec), "t_wall": now}}
        run["last_sample"] = {"u_usec": int(u_usec), "t_wall": now, "boot_id": boot}
        io.write(st)                       # the truth is recorded even if over the cap
        cap, refusal = io.cap(st)
    return {"shadow_cpu_h": s, "c_run": c_run, "r_run": r_run, "cap": cap, "refusal": refusal}


# --------------------------------------------------------------- settlement
def settle_run(io, rt, role, run_id, u_usec_final, evidence):
    u_usec_final = usec(u_usec_final, "final run CPU")
    with io.locked():
        st = io.read()
        ops = ops_of(st, role)
        run = ops["runs"].get(run_id)
        if run is None:
            raise OpsRefusal(f"unknown run {run_id}")
        if run["status"] == "SETTLED":
            return dict(run["settlement"], idempotent=True)
        committed_now = io.v(st["committed_cpu_h_by_role"].get(role, 0.0), "committed now")
        c_run = committed_now - run["committed_start"]
        if c_run < 0:
            raise OpsRefusal(f"committed CPU fell below the run start ({c_run}); corruption")
        c_run = io.v(c_run, "C_run")
        u_h = io.v(int(u_usec_final) / 3.6e9, "U_final")
        charge = io.v(max(0.0, u_h - c_run), "unattributed run charge")
        closed, orphans, torn = {}, [], {}
        for k in sorted(st["open_reservations"]):
            r = st["open_reservations"][k]
            if k == SHADOW + run_id:
                pass
            elif k.startswith(f"{TORN}{run_id}:"):
                torn.setdefault(r["ops"]["kind"], []).append(r["cell_id"])
            elif k.startswith(f"{role}:") and r.get("role") == role:
                orphans.append(r["cell_id"])
            else:
                raise OpsRefusal(f"foreign open reservation {k!r} while settling {run_id}")
            closed[k] = r["reserved_cpu_h"]
        for k in closed:
            del st["open_reservations"][k]
        st["committed_cpu_h_by_role"][role] = io.v(committed_now + charge, "committed after")
        # GRACEFUL_DRAIN is excluded by construction: a cell that never started
        # because the worker drained at a boundary is pending, not torn.
        infra = sorted(set(orphans) | set(torn.get(ABORT, [])))
        for c in infra:
            ops["torn_attempts"][str(c)] = ops["torn_attempts"].get(str(c), 0) + 1
        halting = {k: v for k, v in torn.items() if k in HALTING}
        if halting and not ops["halt"]:
            errs = [e for e in ops["releases"] if e["run_id"] == run_id and e["kind"] in HALTING]
            ops["halt"] = {"reason": "SCIENTIFIC_OR_UNCLASSIFIED_FAILURE", "run_id": run_id,
                           "cells": halting, "events": errs}
        over = sorted(int(c) for c, n in ops["torn_attempts"].items()
                      if n >= MAX_INFRA_TEARS_PER_CELL and str(c) not in st["completed_cells"])
        if over and not ops["halt"]:
            ops["halt"] = {"reason": "RETRY_LIMIT", "run_id": run_id, "cells": over}
        done_now = sorted(int(c) for c in st["completed_cells"])
        cap, refusal = io.cap(st)
        settlement = {"run_id": run_id, "evidence": evidence, "u_usec_final": int(u_usec_final),
                      "measured_run_cpu_h": u_h, "committed_science_cpu_h": c_run,
                      "unattributed_charge_cpu_h": charge, "closed_reservations": closed,
                      "orphan_cells": sorted(orphans), "torn_by_kind": torn,
                      "completed_in_run": sorted(set(done_now) - set(run["completed_start"])),
                      "committed_after_cpu_h": st["committed_cpu_h_by_role"][role],
                      "charged_after_cpu_h": cap["charged_cpu_h"] if cap else None,
                      "cap_refusal": refusal, "settled_wall": time.time()}
        if refusal:
            ops["cap_exhausted"] = {"run_id": run_id, "refusal": refusal}
        run["status"] = "SETTLED"
        run["settlement"] = settlement
        ops["settlements"].append({"run_id": run_id, "evidence": evidence,
                                   "charge_cpu_h": charge, "measured_run_cpu_h": u_h})
        io.write(st)
    append_continuity(rt, "RUN_SETTLED", st, {"run_id": run_id, "evidence": evidence})
    return settlement


def resolve_cpu_evidence(contract, rt, run_id, run, *, service_mode) -> tuple:
    rec_path = rt.run_record(run_id)
    rec = json.loads(rec_path.read_text()) if rec_path.exists() else {}
    if isinstance(rec.get("final_u_usec"), int):
        return rec["final_u_usec"], rec.get("final_evidence", "SUPERVISOR_FINAL")
    if service_mode and run.get("unit") and run.get("invocation_id"):
        u = journal_cpu_usage_usec(run["unit"], run["invocation_id"])
        if u is not None:
            return max(u, run["last_sample"]["u_usec"]), "JOURNAL"
    ls = run["last_sample"]
    cpus = contract["hosts"][run["role"]]["online_cpus"]
    if boot_id(contract) != ls["boot_id"]:
        t_upper, kind = boot_time(contract), "TAIL_BOUND_REBOOT"
    else:
        t_upper, kind = time.time(), "TAIL_BOUND_NOW"
    tail = max(0.0, t_upper - ls["t_wall"]) * cpus * 1_000_000
    return int(ls["u_usec"] + tail), kind


# ------------------------------------------------- torn-release conversion
def make_ops_budget(GB, frozen_budget, run_id, launcher_file):
    """The frozen GlobalBudget with ONE override: release() never drops a
    reservation. It moves it to a TORN escrow (same amount, still counted by the
    frozen cap) and classifies the tear by the exact frozen call site."""
    src = Path(launcher_file).read_text().splitlines()
    stripped = [l.strip() for l in src]
    for line in RELEASE_SITES:
        if stripped.count(line) != 1:
            raise OpsRefusal(f"frozen release call site {line!r} not found exactly once")

    class OpsBudget(GB.GlobalBudget):
        def release(self, key):
            f = sys._getframe(1)
            kind, detail = UNCLASSIFIED, {}
            if f.f_code.co_name == "run_production_cells" and \
                    Path(f.f_code.co_filename).resolve() == Path(launcher_file).resolve():
                kind = RELEASE_SITES.get(linecache.getline(f.f_code.co_filename,
                                                           f.f_lineno).strip(), UNCLASSIFIED)
                rec = f.f_locals.get("rec")
                if kind in (WORKER_FAILURE, MALFORMED) and isinstance(rec, dict):
                    detail = {"error": str(rec.get("error"))[:500],
                              "worker_cpu_seconds": rec.get("cpu_seconds")}
            with GB._Lock(self.path):
                st = self._read()
                res = st.get("open_reservations", {}).pop(key, None)
                if res is None:
                    return
                ops = st.get(OPS_FIELD)
                if ops is None:
                    raise OpsRefusal("OpsBudget on a ledger without an operational block")
                seq = len(ops["releases"])
                tkey = f"{TORN}{run_id}:{res['cell_id']}:{seq}"
                st["open_reservations"][tkey] = {
                    "role": res["role"], "cell_id": res["cell_id"],
                    "reserved_cpu_h": res["reserved_cpu_h"],
                    "ops": {"kind": kind, "run_id": run_id, "from_key": key,
                            "t_wall": time.time(), **detail}}
                ops["releases"].append({"seq": seq, "run_id": run_id, "key": key,
                                        "cell_id": res["cell_id"], "kind": kind, **detail})
                atomic_write(self.path, (json.dumps(st, indent=1, sort_keys=True) + "\n").encode(),
                             tmp=self.path.with_suffix(".tmp"))
            if kind in HALTING:
                raise ScientificHalt(f"cell {res['cell_id']}: {kind} {detail}; the protocol "
                                     "never retries a scientific failure -- campaign stops")

    b = OpsBudget(frozen_budget.path, frozen_budget._validate, frozen_budget._gate,
                  overhead_cpu_h=frozen_budget.overhead_cpu_h, cap_cpu_h=frozen_budget.cap_cpu_h)
    return b


# ------------------------------------------------------------ gate helpers
def halt_state(st, role):
    if st is None or OPS_FIELD not in st:
        return None
    return st[OPS_FIELD].get("halt")


def unsettled_runs(st, role):
    if st is None or OPS_FIELD not in st:
        return []
    return sorted(r for r, x in st[OPS_FIELD]["runs"].items() if x["status"] == "OPEN")
