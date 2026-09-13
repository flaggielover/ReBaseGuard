"""The CUSUM Aux5 production ledger: lifecycle, accounting, continuity, crash reconciliation. NON-CERTIFYING.

STATES
  cell     PENDING -> RESERVED -> RUNNING -> SEALED    terminal: one scientific cell, one sealed record
                                           -> PENDING   attempt TORN (infrastructure loss): retry eligible
                                           -> FAILED    attempt FAILED: the campaign halts, never retried
           RESERVED -> PENDING                          attempt RELEASED: no process was started
  attempt  RESERVED -> RUNNING -> SEALED | TORN | FAILED ;  RESERVED -> RELEASED | TORN | FAILED

INVARIANTS (validate_state: every state is checked before it is written and after it is read)
  a cell has at most one SEALED attempt; a SEALED cell has no open attempt; a cell's status agrees with its
  attempts; each committed CPU bucket equals the sum of the charges recorded on closed attempts and
  supervisor runs; the cap is the one bound at genesis; tear counts equal the infrastructure-TORN attempts.

DURABILITY AND CONTINUITY
  txn(): validate -> atomically replace ledger.json -> append one hash-chained line to journal.jsonl naming
  the new state's sha256. On open: state == last journal state -> CONTINUOUS; state exactly one step past
  the journal (a crash between the two writes) -> the line is re-appended; anything else (a rollback, an
  edit, a deleted ledger, a ledger without a journal) is refused.

ACCOUNTING (integer microseconds)
  committed = science + torn + failed + released + supervisor
  admit one more cell iff 115 * (committed + sum over open attempts of max(R, sampled CPU) + R) <= 100 * CAP
  Every closed attempt is charged, by the best evidence available:
    WAIT4_RUSAGE   the supervisor reaped the worker (exact)
    REAPER_RUSAGE  the keeper reaped it after the supervisor died (exact)
    TAIL_BOUND     last CPU sample + elapsed wall time on its single pinned core, up to now (same boot) or
                   to the boot time (after a reboot). May overcharge; never undercharges.
  Only a RELEASED attempt (its process provably never started) is charged zero.
"""
from __future__ import annotations

import copy
import fcntl
import json
import os
import resource
import time
from pathlib import Path

from prod_common import (Refusal, atomic_write_bytes, atomic_write_json, append_durable, boot_id, boot_time,
                         canonical, exit_facts, pid_alive, rusage_usec, sha256_bytes, sha256_file)
from prod_sealer import seal_file, verify_record

LEDGER_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-ledger.v1"
JOURNAL_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-journal.v1"
REAPER_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.reaper-record.v1"
EXPORT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-export.v1"
CELL_STATES = ("PENDING", "RESERVED", "RUNNING", "SEALED", "FAILED")
ATTEMPT_STATES = ("RESERVED", "RUNNING", "SEALED", "RELEASED", "TORN", "FAILED")
OPEN = ("RESERVED", "RUNNING")
BUCKET = {"SEALED": "science", "TORN": "torn", "FAILED": "failed", "RELEASED": "released"}
BUCKETS = ("science", "torn", "failed", "released", "supervisor")
DISPOSITIONS = ("OPEN", "DRAINED", "COMPLETE", "HALTED", "INCOMPLETE_BUDGET_EXHAUSTED")
TERMINAL = ("COMPLETE", "HALTED", "INCOMPLETE_BUDGET_EXHAUSTED")
INVARIANT = [115, 100]
MAX_INFRA_TEARS_PER_CELL = 3

INFRA_SIGNAL = "INFRASTRUCTURE_SIGNAL"
ORPHAN = "ORPHAN_ATTEMPT"
INFRA_KINDS = (INFRA_SIGNAL, ORPHAN)
WORKER_FAILURE = "WORKER_REPORTED_FAILURE"
MALFORMED = "MALFORMED_RESULT"
SPAWN_FAILED = "SPAWN_FAILED"
PRE_GENESIS_FILES = ("campaign.lock", "campaign.owner.json", "reaper.jsonl")


class Paths:
    def __init__(self, root):
        self.root = Path(root)
        self.lock = self.root / "campaign.lock"
        self.owner = self.root / "campaign.owner.json"
        self.ledger = self.root / "ledger.json"
        self.journal = self.root / "journal.jsonl"
        self.reaper = self.root / "reaper.jsonl"
        self.drain = self.root / "DRAIN"
        self.attempts = self.root / "attempts"


# ------------------------------------------------------------------ pure accounting
def admission_allowed(committed_usec: int, open_usec: int, reservation_usec: int, cap_usec: int) -> bool:
    return INVARIANT[0] * (committed_usec + open_usec + reservation_usec) <= INVARIANT[1] * cap_usec


def committed_total(st) -> int:
    return sum(st["committed_usec"][b] for b in BUCKETS)


def open_usec(st, reservation_usec: int) -> int:
    return sum(max(reservation_usec, a["cpu_sample_usec"]) for a in st["attempts"].values() if a["status"] in OPEN)


def state_sha256(st) -> str:
    return sha256_bytes(canonical(st))


def next_pending(st):
    pending = [int(c) for c, x in st["cells"].items() if x["status"] == "PENDING"]
    return min(pending) if pending else None


def _nonneg_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


# ------------------------------------------------------------------ validation
def validate_state(st, spec) -> None:
    try:
        _validate(st, spec)
    except Refusal:
        raise
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        raise Refusal("LEDGER_CORRUPT", f"malformed ledger state: {exc!r}") from exc


def _validate(st, spec) -> None:
    if not isinstance(st, dict) or st.get("schema") != LEDGER_SCHEMA:
        raise Refusal("LEDGER_SCHEMA", f"ledger schema is not {LEDGER_SCHEMA}")
    if st["mode"] != spec.mode or st["checkpoint_sha256"] != spec.checkpoint_sha256:
        raise Refusal("INCOMPATIBLE_RUN_STATE",
                      f"ledger is {st['mode']} under checkpoint {str(st['checkpoint_sha256'])[:24]}")
    frozen_cap = {"cap_usec": spec.cap_usec, "reservation_usec": spec.reservation_usec, "invariant": INVARIANT}
    if st["cap"] != frozen_cap:
        raise Refusal("CAP_CHANGE_FORBIDDEN",
                      f"ledger cap {st['cap']} != frozen {frozen_cap}; the cap is bound at genesis and never changes")
    if not _nonneg_int(st["seq"]) or st["disposition"] not in DISPOSITIONS:
        raise Refusal("LEDGER_CORRUPT", "seq or disposition")
    cells, attempts, runs = st["cells"], st["attempts"], st["supervisor_runs"]
    if set(cells) != {str(i) for i in spec.cell_indices}:
        raise Refusal("LEDGER_CORRUPT", "the cell universe differs from the frozen cells")
    sums = dict.fromkeys(BUCKETS, 0)
    seals, opens, tears = {}, {}, {}
    for aid, a in attempts.items():
        c, s = str(a["cell"]), a["status"]
        if c not in cells or s not in ATTEMPT_STATES:
            raise Refusal("LEDGER_CORRUPT", f"attempt {aid} cell/status")
        if not _nonneg_int(a["cpu_sample_usec"]):
            raise Refusal("ACCOUNTING_CORRUPT", f"attempt {aid} CPU sample {a['cpu_sample_usec']!r}")
        if s in OPEN:
            if a["charge_usec"] is not None:
                raise Refusal("ACCOUNTING_CORRUPT", f"open attempt {aid} carries a charge")
            opens.setdefault(c, []).append(aid)
            continue
        if not _nonneg_int(a["charge_usec"]):
            raise Refusal("ACCOUNTING_CORRUPT", f"attempt {aid} charge {a['charge_usec']!r}")
        sums[BUCKET[s]] += a["charge_usec"]
        if s == "SEALED":
            if not (isinstance(a["seal"], dict) and isinstance(a["seal"].get("record_sha256"), str)):
                raise Refusal("LEDGER_CORRUPT", f"sealed attempt {aid} has no seal")
            seals.setdefault(c, []).append(aid)
        if s == "TORN" and a["tear_kind"] in INFRA_KINDS:
            tears[c] = tears.get(c, 0) + 1
    for c, cs in cells.items():
        s, sealed, opened = cs["status"], seals.get(c, []), opens.get(c, [])
        if s not in CELL_STATES:
            raise Refusal("LEDGER_CORRUPT", f"cell {c} status {s!r}")
        if len(sealed) > 1:
            raise Refusal("DUPLICATE_SEALED_CELL", f"cell {c} has sealed attempts {sealed}")
        ok = ((s == "SEALED" and len(sealed) == 1 and not opened and cs["attempt"] == sealed[0])
              or (s in OPEN and not sealed and len(opened) == 1 and cs["attempt"] == opened[0]
                  and attempts[opened[0]]["status"] == s)
              or (s == "PENDING" and not sealed and not opened and cs["attempt"] is None)
              or (s == "FAILED" and not sealed and not opened
                  and attempts.get(cs["attempt"], {}).get("status") == "FAILED" and st["halt"] is not None))
        if not ok:
            raise Refusal("LEDGER_CORRUPT", f"cell {c} status {s} disagrees with its attempts")
        if cs["infra_tears"] != tears.get(c, 0):
            raise Refusal("LEDGER_CORRUPT", f"cell {c} tear count {cs['infra_tears']} != {tears.get(c, 0)}")
        if cs["infra_tears"] >= MAX_INFRA_TEARS_PER_CELL and s != "SEALED" and st["halt"] is None:
            raise Refusal("LEDGER_CORRUPT", f"cell {c} reached the tear limit without a halt")
    sup = 0
    for rid, r in runs.items():
        for k in ("charged_usec", "children_usec", "self_cpu_seen_usec"):
            if not _nonneg_int(r[k]):
                raise Refusal("ACCOUNTING_CORRUPT", f"supervisor run {rid} {k} {r[k]!r}")
        sup += r["charged_usec"]
    for rid, v in st["overhead_charges"].items():
        if not _nonneg_int(v):
            raise Refusal("ACCOUNTING_CORRUPT", f"overhead charge {rid} {v!r}")
        sup += v
    sums["supervisor"] = sup
    committed = st["committed_usec"]
    if set(committed) != set(BUCKETS):
        raise Refusal("ACCOUNTING_CORRUPT", "committed buckets")
    for b in BUCKETS:
        if committed[b] != sums[b]:
            raise Refusal("ACCOUNTING_CORRUPT", f"committed {b} {committed[b]!r} != recorded charges {sums[b]}")
    if (st["first_admission_wall"] is None) != (not attempts):
        raise Refusal("LEDGER_CORRUPT", "first admission time disagrees with the attempts")
    if st["disposition"] == "COMPLETE" and any(cs["status"] != "SEALED" for cs in cells.values()):
        raise Refusal("LEDGER_CORRUPT", "COMPLETE with unsealed cells")
    if st["disposition"] == "HALTED" and st["halt"] is None:
        raise Refusal("LEDGER_CORRUPT", "HALTED without a halt record")


# ------------------------------------------------------------------ the campaign lock
class CampaignLock:
    """Kernel flock held for a supervisor's whole life. The kernel releases it when the holder dies, so it cannot
    go stale, and a held lock proves a live owner. The descriptor is not inherited by workers."""

    def __init__(self, root):
        self.p, self.fd = Paths(root), None

    def acquire(self, owner: dict) -> None:
        self.p.root.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(self.p.lock), os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(fd)
            raise Refusal("ANOTHER_SUPERVISOR_LIVE", f"campaign lock is held (owner {self.read_owner()})") from None
        self.fd = fd
        atomic_write_json(self.p.owner, owner)

    def read_owner(self):
        try:
            return json.loads(self.p.owner.read_text())
        except (OSError, ValueError):
            return None

    @property
    def held(self) -> bool:
        return self.fd is not None

    def release(self) -> None:
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None

    def probe(self) -> str:
        if self.held:
            return "SELF"
        if not self.p.lock.exists():
            return "FREE"
        fd = os.open(str(self.p.lock), os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
            return "FREE"
        except BlockingIOError:
            return "LIVE"
        finally:
            os.close(fd)


# ------------------------------------------------------------------ the ledger
class Ledger:
    def __init__(self, spec, lock, run_id=None):
        if lock is None or not lock.held:
            raise Refusal("LOCK_NOT_HELD", "the ledger is opened only by the campaign lock holder")
        self.spec, self.p, self.run_id = spec, Paths(spec.root), run_id
        self.state, self._last = None, None

    @staticmethod
    def read_journal(path) -> tuple[list, bool]:
        """(entries, torn_tail). Only the final line may be torn; any other break is refused."""
        if not Path(path).exists():
            return [], False
        lines = Path(path).read_text().split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        entries, prev = [], None
        for i, line in enumerate(lines):
            try:
                e = json.loads(line)
            except ValueError:
                if i == len(lines) - 1:
                    return entries, True
                raise Refusal("JOURNAL_CORRUPT", f"journal line {i} is unparseable") from None
            body = {k: v for k, v in e.items() if k != "entry_sha256"} if isinstance(e, dict) else None
            if (body is None or e.get("schema") != JOURNAL_SCHEMA
                    or e.get("entry_sha256") != sha256_bytes(canonical(body))
                    or e.get("seq") != (prev["seq"] + 1 if prev else 0)
                    or e.get("prev_entry_sha256") != (prev["entry_sha256"] if prev else None)):
                raise Refusal("JOURNAL_CORRUPT", f"journal hash chain broken at line {i}")
            entries.append(e)
            prev = e
        return entries, False

    @staticmethod
    def read_and_relate(p: Paths):
        """Read the ledger and journal and classify how they relate. Never writes."""
        if p.journal.exists() and not p.ledger.exists():
            raise Refusal("LEDGER_MISSING", "the journal exists but ledger.json is gone; a deleted ledger would reset "
                                            "the budget")
        try:
            st = json.loads(p.ledger.read_bytes())
        except ValueError as exc:
            raise Refusal("LEDGER_CORRUPT", f"ledger.json is unparseable: {exc}") from exc
        entries, torn = Ledger.read_journal(p.journal)
        if not isinstance(st, dict):
            raise Refusal("LEDGER_CORRUPT", "ledger.json is not an object")
        if not entries:
            if (st.get("seq") == 0 and st.get("prev_state_sha256") is None
                    and (st.get("last_event") or {}).get("event") == "GENESIS"):
                return st, entries, torn, "GENESIS_JOURNAL_MISSING"
            raise Refusal("UNSANCTIONED_LEDGER", "a ledger exists with no continuity journal")
        if entries[0]["event"] != "GENESIS":
            raise Refusal("JOURNAL_CORRUPT", "the journal does not start at GENESIS")
        last, sha = entries[-1], state_sha256(st)
        if st.get("seq") == last["seq"] and sha == last["state_sha256"] and not torn:
            return st, entries, torn, "CONTINUOUS"
        if st.get("seq") == last["seq"] + 1 and st.get("prev_state_sha256") == last["state_sha256"]:
            return st, entries, torn, "JOURNAL_BEHIND_ONE"
        raise Refusal("LEDGER_ROLLBACK_OR_MUTATION",
                      f"ledger seq {st.get('seq')} ({sha[:12]}) does not continue journal seq {last['seq']} "
                      f"({last['state_sha256'][:12]})")

    @classmethod
    def inspect(cls, spec) -> dict:
        """Read-only view (preflight, status). Never repairs or writes."""
        p = Paths(spec.root)
        if not p.ledger.exists() and not p.journal.exists():
            extra = sorted(x.name for x in p.root.iterdir() if x.name not in PRE_GENESIS_FILES) if p.root.exists() else []
            if extra:
                raise Refusal("STALE_INCOMPATIBLE_RUN_STATE", f"runtime root holds {extra[:6]} but no ledger")
            return {"relation": "FRESH"}
        st, _entries, _torn, relation = cls.read_and_relate(p)
        validate_state(st, spec)
        return {"relation": relation, "seq": st["seq"], "disposition": st["disposition"], "halt": st["halt"],
                "sealed": sum(1 for c in st["cells"].values() if c["status"] == "SEALED"),
                "open_attempts": sorted(a for a, x in st["attempts"].items() if x["status"] in OPEN),
                "committed_usec": committed_total(st), "state_sha256": state_sha256(st)}

    def open(self, *, allow_genesis: bool) -> str:
        p = self.p
        if not p.ledger.exists() and not p.journal.exists():
            if not allow_genesis:
                raise Refusal("NO_LEDGER", str(p.ledger))
            self._genesis()
            return "GENESIS"
        st, entries, torn, relation = self.read_and_relate(p)
        validate_state(st, self.spec)
        if relation == "CONTINUOUS":
            self.state, self._last = st, entries[-1]
            return relation
        if torn:
            atomic_write_bytes(p.journal, "".join(json.dumps(e, sort_keys=True) + "\n" for e in entries).encode())
        prev = entries[-1] if entries else None
        self._last = self._append_journal(prev, st, st["last_event"]["event"],
                                          {"repaired_after_crash": True, **(st["last_event"].get("detail") or {})})
        self.state = st
        return relation

    def _append_journal(self, prev, st, event, detail) -> dict:
        e = {"schema": JOURNAL_SCHEMA, "seq": st["seq"], "event": event, "state_sha256": state_sha256(st),
             "prev_entry_sha256": prev["entry_sha256"] if prev else None, "t_wall": time.time(), "detail": detail}
        e["entry_sha256"] = sha256_bytes(canonical(e))
        append_durable(self.p.journal, json.dumps(e, sort_keys=True))
        return e

    def _genesis(self) -> None:
        spec, p = self.spec, self.p
        extra = sorted(x.name for x in p.root.iterdir() if x.name not in PRE_GENESIS_FILES) if p.root.exists() else []
        if extra:
            raise Refusal("STALE_INCOMPATIBLE_RUN_STATE", f"runtime root holds {extra[:6]} but no ledger")
        st = {"schema": LEDGER_SCHEMA, "mode": spec.mode, "checkpoint_sha256": spec.checkpoint_sha256,
              "campaign_id": spec.campaign_id,
              "cap": {"cap_usec": spec.cap_usec, "reservation_usec": spec.reservation_usec, "invariant": INVARIANT},
              "cells": {str(i): {"status": "PENDING", "attempt": None, "infra_tears": 0} for i in spec.cell_indices},
              "attempts": {}, "supervisor_runs": {}, "overhead_charges": {},
              "committed_usec": dict.fromkeys(BUCKETS, 0),
              "accounting_exclusions": spec.accounting_exclusions,
              "first_admission_wall": None, "halt": None, "disposition": "OPEN", "budget_exhaustion": None,
              "seq": 0, "prev_state_sha256": None,
              "last_event": {"event": "GENESIS", "detail": {}, "t_wall": time.time()}}
        validate_state(st, spec)
        atomic_write_json(p.ledger, st)
        self.state = st
        self._last = self._append_journal(None, st, "GENESIS", {"checkpoint_sha256": spec.checkpoint_sha256})

    def txn(self, event: str, mutate, detail=None):
        """One validated, durable, journalled transition. Returns mutate()'s result."""
        if self.state is None:
            raise Refusal("LEDGER_NOT_OPEN")
        try:
            on_disk = json.loads(self.p.ledger.read_bytes())
        except (OSError, ValueError) as exc:
            raise Refusal("LEDGER_ROLLBACK_OR_MUTATION", f"ledger unreadable underneath the lock holder: {exc}") from exc
        if state_sha256(on_disk) != self._last["state_sha256"]:
            raise Refusal("LEDGER_ROLLBACK_OR_MUTATION", "ledger.json changed underneath the lock holder")
        new = copy.deepcopy(self.state)
        result = mutate(new)
        self._charge_self(new)
        new["seq"] = self.state["seq"] + 1
        new["prev_state_sha256"] = self._last["state_sha256"]
        new["last_event"] = {"event": event, "detail": detail or {}, "t_wall": time.time()}
        validate_state(new, self.spec)
        atomic_write_json(self.p.ledger, new)
        self._last = self._append_journal(self._last, new, event, detail or {})
        self.state = new
        return result

    def _charge_self(self, st) -> None:
        """Supervisor overhead: this process's own CPU since its last charge."""
        run = st["supervisor_runs"].get(self.run_id) if self.run_id else None
        if run is None or run["end"] is not None:
            return
        now = rusage_usec(resource.getrusage(resource.RUSAGE_SELF))
        delta = max(0, now - run["self_cpu_seen_usec"])
        run["self_cpu_seen_usec"] = max(now, run["self_cpu_seen_usec"])
        run["charged_usec"] += delta
        run["last_charge_wall"] = time.time()
        st["committed_usec"]["supervisor"] += delta


# ------------------------------------------------------------------ transitions (applied inside txn)
def op_reserve(st, spec, cell: int, core: int, run_id: str) -> str:
    if st["halt"] is not None:
        raise Refusal("HALTED", f"campaign halted: {st['halt']}")
    if st["disposition"] in TERMINAL:
        raise Refusal("TERMINAL_DISPOSITION", st["disposition"])
    cs = st["cells"].get(str(cell))
    if cs is None:
        raise Refusal("CELL_NOT_IN_UNIVERSE", str(cell))
    if cs["status"] != "PENDING":
        raise Refusal("DUPLICATE_CELL", f"cell {cell} is {cs['status']}; only a PENDING cell is admitted")
    if any(a["status"] in OPEN and a["core"] == core for a in st["attempts"].values()):
        raise Refusal("CORE_BUSY", f"core {core} already runs an attempt")
    committed, inflight = committed_total(st), open_usec(st, spec.reservation_usec)
    if not admission_allowed(committed, inflight, spec.reservation_usec, spec.cap_usec):
        raise Refusal("CAP_ADMISSION_DENIED",
                      f"115*({committed} + {inflight} + {spec.reservation_usec}) > 100*{spec.cap_usec}")
    now = time.time()
    aid = f"A{len(st['attempts']):05d}-C{cell:04d}"
    st["attempts"][aid] = {
        "cell": cell, "status": "RESERVED", "core": core, "run_id": run_id, "boot_id": boot_id(),
        "t_reserved": now, "pid": None, "pid_start_ticks": None, "t_spawn": None,
        "cpu_sample_usec": 0, "t_sample": None, "record": f"attempts/{aid}/aux5_CUSUM_{cell}_256.json",
        "charge_usec": None, "charge_evidence": None, "tear_kind": None, "detail": None, "seal": None,
        "t_closed": None}
    cs["status"], cs["attempt"] = "RESERVED", aid
    if st["first_admission_wall"] is None:
        st["first_admission_wall"] = now
    return aid


def op_running(st, aid: str, pid: int, start_ticks, t_spawn: float) -> None:
    a = st["attempts"][aid]
    if a["status"] != "RESERVED":
        raise Refusal("LIFECYCLE", f"attempt {aid} is {a['status']}, not RESERVED")
    a.update(status="RUNNING", pid=pid, pid_start_ticks=start_ticks, t_spawn=t_spawn)
    st["cells"][str(a["cell"])]["status"] = "RUNNING"


def op_sample(st, aid: str, cpu_usec: int, t_wall: float) -> None:
    a = st["attempts"][aid]
    if a["status"] in OPEN and cpu_usec >= a["cpu_sample_usec"]:
        a["cpu_sample_usec"], a["t_sample"] = int(cpu_usec), t_wall


def op_halt(st, reason: str, **detail) -> None:
    if st["halt"] is None:
        st["halt"] = {"reason": reason, "t_wall": time.time(), **detail}


def op_close(st, aid: str, status: str, charge_usec: int, evidence: str, *, tear_kind=None, detail=None,
             seal=None) -> None:
    a = st["attempts"][aid]
    if a["status"] not in OPEN:
        raise Refusal("LIFECYCLE", f"attempt {aid} is already {a['status']}")
    cs = st["cells"][str(a["cell"])]
    if cs["attempt"] != aid or cs["status"] not in OPEN:
        raise Refusal("DUPLICATE_CELL", f"cell {a['cell']} is {cs['status']} under attempt {cs['attempt']}")
    a.update(status=status, charge_usec=int(charge_usec), charge_evidence=evidence, tear_kind=tear_kind,
             detail=detail, seal=seal, t_closed=time.time())
    st["committed_usec"][BUCKET[status]] += int(charge_usec)
    if status == "SEALED":
        cs["status"] = "SEALED"
    elif status in ("TORN", "RELEASED"):
        cs["status"], cs["attempt"] = "PENDING", None
        if status == "TORN" and tear_kind in INFRA_KINDS:
            cs["infra_tears"] += 1
            if cs["infra_tears"] >= MAX_INFRA_TEARS_PER_CELL:
                op_halt(st, "RETRY_LIMIT", cell=a["cell"], attempt=aid)
    elif status == "FAILED":
        cs["status"] = "FAILED"
        op_halt(st, tear_kind, cell=a["cell"], attempt=aid, detail=detail)


def op_run_open(st, run_id: str, pid: int, probe_usec: int, overhead: list) -> None:
    if run_id in st["supervisor_runs"]:
        raise Refusal("LIFECYCLE", f"supervisor run id {run_id} reused")
    now = time.time()
    st["supervisor_runs"][run_id] = {"pid": pid, "boot_id": boot_id(), "started_wall": now, "ended_wall": None,
                                     "end": None, "settled": False, "self_cpu_seen_usec": 0,
                                     "children_usec": int(probe_usec), "charged_usec": int(probe_usec),
                                     "last_charge_wall": now, "settlement": None}
    st["committed_usec"]["supervisor"] += int(probe_usec)
    op_charge_overhead(st, overhead)
    if st["disposition"] == "DRAINED":
        st["disposition"] = "OPEN"


def op_charge_overhead(st, overhead: list) -> None:
    """Charge keeper exits and refused launches exactly once each (keyed by reaper record id)."""
    for record_id, usec in overhead:
        if record_id not in st["overhead_charges"]:
            st["overhead_charges"][record_id] = int(usec)
            st["committed_usec"]["supervisor"] += int(usec)


def op_run_end(st, run_id: str) -> None:
    run = st["supervisor_runs"][run_id]
    run["end"], run["ended_wall"] = "EXITED", time.time()


def op_settle_run(st, run_id: str, extra_usec: int, evidence: str) -> None:
    run = st["supervisor_runs"][run_id]
    if run["settled"]:
        return
    run["charged_usec"] += int(extra_usec)
    st["committed_usec"]["supervisor"] += int(extra_usec)
    run["settled"] = True
    run["settlement"] = {"extra_usec": int(extra_usec), "evidence": evidence, "t_wall": time.time()}
    if run["end"] is None:
        run["end"], run["ended_wall"] = "CRASHED", time.time()


# ------------------------------------------------------------------ keeper evidence
def reaper_record(kind: str, pid: int, status, ru, *, is_supervisor: bool) -> dict:
    how = exit_facts(status) if status is not None else {"exited": None, "exit_code": None, "signal": None}
    rec = {"schema": REAPER_SCHEMA, "kind": kind, "pid": pid, "boot_id": boot_id(), "t_wall": time.time(),
           "cpu_usec": rusage_usec(ru), "is_supervisor": is_supervisor, **how}
    rec["record_id"] = sha256_bytes(canonical(rec))
    return rec


def read_reaper(p: Paths) -> tuple[list, int]:
    """(records, unreadable lines). An unreadable line is never matched, so its attempt falls back to a tail bound."""
    if not p.reaper.exists():
        return [], 0
    good, bad = [], 0
    for line in p.reaper.read_text().splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
            body = {k: v for k, v in rec.items() if k != "record_id"}
            if rec.get("schema") != REAPER_SCHEMA or rec.get("record_id") != sha256_bytes(canonical(body)):
                raise ValueError("bad reaper record")
        except (ValueError, AttributeError):
            bad += 1
            continue
        good.append(rec)
    return good, bad


def _unique(records, pred):
    hits = [r for r in records if pred(r)]
    return hits[0] if len(hits) == 1 else None


def match_attempt_reap(reaped, a):
    if a["pid"] is None:
        return None
    t0 = (a["t_spawn"] or a["t_reserved"]) - 1
    return _unique(reaped, lambda r: r["kind"] == "CHILD_REAPED" and not r["is_supervisor"] and r["pid"] == a["pid"]
                   and r["boot_id"] == a["boot_id"] and r["t_wall"] >= t0)


def match_run_reap(reaped, run):
    return _unique(reaped, lambda r: r["kind"] == "CHILD_REAPED" and r["is_supervisor"] and r["pid"] == run["pid"]
                   and r["boot_id"] == run["boot_id"] and r["t_wall"] >= run["started_wall"] - 1)


def unmatched_overhead(reaped, st) -> list:
    """Keeper exits, and supervisors that never opened a run (refused launches): charged once as overhead."""
    out = []
    runs = list(st["supervisor_runs"].values())
    for r in reaped:
        if r["record_id"] in st["overhead_charges"]:
            continue
        if r["kind"] == "KEEPER_EXIT":
            out.append((r["record_id"], r["cpu_usec"]))
        elif r["kind"] == "CHILD_REAPED" and r["is_supervisor"] and not any(
                r["pid"] == run["pid"] and r["boot_id"] == run["boot_id"] and r["t_wall"] >= run["started_wall"] - 1
                for run in runs):
            out.append((r["record_id"], r["cpu_usec"]))
    return out


def tail_bound(a, *, now: float, current_boot: str) -> tuple[int, str, float]:
    same = a["boot_id"] == current_boot
    t_upper = now if same else boot_time()
    t0 = a["t_sample"] or a["t_spawn"] or a["t_reserved"]
    return (a["cpu_sample_usec"] + max(0, int((t_upper - t0) * 1_000_000)) + 1,
            "TAIL_BOUND_NOW" if same else "TAIL_BOUND_REBOOT", t_upper)


# ------------------------------------------------------------------ crash reconciliation
def reconcile(led: Ledger, reaped: list, unreadable: int) -> dict:
    """Close every attempt and settle every supervisor run a dead predecessor left open. Runs under the lock,
    so no other supervisor is alive; a worker still alive is refused, never adopted or killed."""
    spec, p = led.spec, led.p
    now, current = time.time(), boot_id()
    report = {"attempts": {}, "runs": {}, "reaper_unreadable_lines": unreadable}
    for aid in sorted(x for x, a in led.state["attempts"].items() if a["status"] in OPEN):
        a = led.state["attempts"][aid]
        if a["boot_id"] == current and a["pid"] is not None and pid_alive(a["pid"], a["pid_start_ticks"]):
            raise Refusal("LIVE_ORPHAN_WORKER", f"attempt {aid} pid {a['pid']} is alive but its supervisor is gone")
        reap = match_attempt_reap(reaped, a)
        if reap is not None:
            charge, evidence, t_end = reap["cpu_usec"], "REAPER_RUSAGE", reap["t_wall"]
        else:
            charge, evidence, t_end = tail_bound(a, now=now, current_boot=current)
        record, start = p.root / a["record"], a["t_spawn"] or a["t_reserved"]
        how = {k: reap[k] for k in ("exited", "exit_code", "signal")} if reap else None
        kind = detail = seal = None
        if record.exists():
            try:
                facts = verify_record(record, cell=a["cell"], spec=spec, measured_cpu_usec=charge,
                                      wall_bound_s=t_end - start, not_before_wall=a["t_reserved"])
            except Refusal as r:
                status, kind, detail = "FAILED", MALFORMED, f"{r.code}: {r.detail[:300]}"
            else:
                seal_file(record)
                status, seal = "SEALED", {**facts, "exit": how, "recovered": True}
        elif reap is not None and reap["exited"]:
            status = "FAILED"
            kind = WORKER_FAILURE if reap["exit_code"] else MALFORMED
            detail = f"exit code {reap['exit_code']} and no record"
        else:
            status, kind = "TORN", ORPHAN
            detail = f"signal {reap['signal']}" if reap else "no exit evidence"
        led.txn(f"RECONCILED_{status}",
                lambda s: op_close(s, aid, status, charge, evidence, tear_kind=kind, detail=detail, seal=seal),
                {"attempt": aid, "cell": a["cell"], "evidence": evidence})
        report["attempts"][aid] = {"cell": a["cell"], "status": status, "evidence": evidence, "charge_usec": charge}
    for rid in sorted(led.state["supervisor_runs"]):
        run = led.state["supervisor_runs"][rid]
        if run["settled"] or rid == led.run_id:
            continue
        reap = match_run_reap(reaped, run)
        if reap is not None:
            extra = max(0, reap["cpu_usec"] - run["children_usec"] - run["self_cpu_seen_usec"])
            evidence = "REAPER_RUSAGE"
        else:
            same = run["boot_id"] == current
            t_upper = now if same else boot_time()
            extra = max(0, int((t_upper - run["last_charge_wall"]) * 1_000_000)) + 1
            evidence = "TAIL_BOUND_NOW" if same else "TAIL_BOUND_REBOOT"
        led.txn("RUN_SETTLED", lambda s: op_settle_run(s, rid, extra, evidence), {"run_id": rid, "evidence": evidence})
        report["runs"][rid] = {"evidence": evidence, "extra_usec": extra}
    return report


def verify_sealed_evidence(spec, st, *, full: bool = False) -> int:
    """Every sealed record must still be byte-identical to its seal. `full` also re-runs the seal verification."""
    n = 0
    for aid, a in sorted(st["attempts"].items()):
        if a["status"] != "SEALED":
            continue
        path = Path(spec.root) / a["record"]
        if not path.exists() or sha256_file(path) != a["seal"]["record_sha256"]:
            raise Refusal("SEALED_EVIDENCE_CORRUPT",
                          f"cell {a['cell']} ({aid}): {a['record']} is missing or its bytes changed since the seal")
        if full:
            facts = verify_record(path, cell=a["cell"], spec=spec)
            if facts["scientific_content_hash"] != a["seal"]["scientific_content_hash"]:
                raise Refusal("SEALED_EVIDENCE_CORRUPT", f"cell {a['cell']}: scientific hash differs from its seal")
        n += 1
    return n


# ------------------------------------------------------------------ export / restore
def export_bundle(led: Ledger, out_dir) -> dict:
    spec, st, out = led.spec, led.state, Path(out_dir)
    if any(a["status"] in OPEN for a in st["attempts"].values()):
        raise Refusal("EXPORT_REFUSED", "attempts are in flight; a supervisor must reconcile them first")
    if out.exists() and any(out.iterdir()):
        raise Refusal("EXPORT_REFUSED", f"{out} is not empty")
    verify_sealed_evidence(spec, st, full=True)
    files = {}

    def put(relpath: str, data: bytes) -> None:
        atomic_write_bytes(out / relpath, data)
        files[relpath] = sha256_bytes(data)

    put("ledger.json", led.p.ledger.read_bytes())
    put("journal.jsonl", led.p.journal.read_bytes())
    if led.p.reaper.exists():
        put("reaper.jsonl", led.p.reaper.read_bytes())
    sealed = {}
    for aid, a in sorted(st["attempts"].items()):
        if a["status"] == "SEALED":
            data = (Path(spec.root) / a["record"]).read_bytes()
            put(a["record"], data)
            put(f"k4_records/aux5_CUSUM_{a['cell']}_256.json", data)
            sealed[str(a["cell"])] = {"attempt": aid, "record_sha256": a["seal"]["record_sha256"],
                                      "scientific_content_hash": a["seal"]["scientific_content_hash"]}
    manifest = {"schema": EXPORT_SCHEMA, "mode": spec.mode, "checkpoint_sha256": spec.checkpoint_sha256,
                "ledger_seq": st["seq"], "ledger_state_sha256": state_sha256(st), "disposition": st["disposition"],
                "files": files, "sealed_cells": sealed, "k4_records_dir": "k4_records", "t_wall": time.time()}
    manifest["export_sha256"] = sha256_bytes(canonical(manifest))
    atomic_write_json(out / "EXPORT_MANIFEST.json", manifest)
    return manifest


def restore_bundle(spec, bundle_dir) -> dict:
    b = Path(bundle_dir)
    try:
        manifest = json.loads((b / "EXPORT_MANIFEST.json").read_text())
    except (OSError, ValueError) as exc:
        raise Refusal("EXPORT_CORRUPT", f"export manifest unreadable: {exc}") from exc
    body = {k: v for k, v in manifest.items() if k != "export_sha256"}
    if manifest.get("schema") != EXPORT_SCHEMA or manifest.get("export_sha256") != sha256_bytes(canonical(body)):
        raise Refusal("EXPORT_CORRUPT", "export manifest hash does not recompute")
    if manifest["mode"] != spec.mode or manifest["checkpoint_sha256"] != spec.checkpoint_sha256:
        raise Refusal("INCOMPATIBLE_RUN_STATE", "export belongs to another campaign")
    for relpath, digest in manifest["files"].items():
        if not (b / relpath).exists() or sha256_file(b / relpath) != digest:
            raise Refusal("EXPORT_CORRUPT", f"{relpath} is missing or its bytes changed")
    root = Path(spec.root)
    if root.exists() and any(x.name not in ("campaign.lock", "campaign.owner.json") for x in root.iterdir()):
        raise Refusal("STALE_INCOMPATIBLE_RUN_STATE", f"restore target {root} is not empty")
    for relpath in manifest["files"]:
        if not relpath.startswith("k4_records/"):
            atomic_write_bytes(root / relpath, (b / relpath).read_bytes())
    st, _entries, _torn, relation = Ledger.read_and_relate(Paths(root))
    if relation != "CONTINUOUS" or state_sha256(st) != manifest["ledger_state_sha256"]:
        raise Refusal("EXPORT_CORRUPT", "the restored ledger does not match the export")
    validate_state(st, spec)
    for a in st["attempts"].values():
        if a["status"] == "SEALED":
            os.chmod(root / a["record"], 0o444)
    n = verify_sealed_evidence(spec, st, full=True)
    return {"restored_seq": st["seq"], "sealed_cells": n, "state_sha256": state_sha256(st)}
