"""Lock ownership and deterministic stale-lock recovery.

TWO locks exist:

1. CAMPAIGN LOCK (this successor): a kernel `flock` on <runtime>/campaign.lock,
   held by the sanctioned supervisor for the WHOLE run. The kernel releases it
   when the holder dies, so it cannot go stale; a held lock proves a LIVE owner.
   The bound owner identity (host, boot id, pid, process start time, run id,
   unit, invocation id) is written next to it for diagnosis.

2. FROZEN LEDGER LOCK: the frozen `global_budget._Lock` (O_CREAT|O_EXCL file
   holding "<pid>\\n"), held only for one ledger operation. If its owner dies
   inside that window the file stays forever. Recovery NEVER uses age alone:

      written before the current boot          -> DEAD
      written within 1 s of boot               -> AMBIGUOUS
      content is not exactly "<pid>\\n"        -> AMBIGUOUS
      pid not alive (or zombie)                -> DEAD
      pid alive but started AFTER the lock     -> DEAD  (pid reuse)
      pid alive, older than the lock, and a
        sanctioned producer of this campaign   -> LIVE  (never stolen)
      anything else                            -> AMBIGUOUS (fail closed)

   Reclaim is permitted ONLY for DEAD, and only while the caller holds the
   campaign lock (so no sanctioned producer can be mid-operation).
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import socket
import time
from pathlib import Path

from opscommon import (OpsRefusal, boot_id, boot_time, pid_alive, proc_start_wall,
                       write_json_atomic)

LIVE, DEAD, AMBIGUOUS, ABSENT = "LIVE", "DEAD", "AMBIGUOUS", "ABSENT"
PID_REUSE_TOLERANCE_S = 2.0
BOOT_TOLERANCE_S = 1.0


class CampaignLock:
    def __init__(self, rt, contract):
        self.rt, self.contract, self.fd = rt, contract, None

    def acquire(self, *, run_id, unit, timeout_s=0.0) -> dict:
        self.rt.root.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(self.rt.lock), os.O_CREAT | os.O_RDWR, 0o600)
        deadline = time.monotonic() + timeout_s
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    os.close(fd)
                    raise OpsRefusal(f"ANOTHER_PRODUCER_LIVE: campaign lock held by "
                                     f"{self.read_owner()}")
                time.sleep(0.2)
        self.fd = fd
        owner = {"host": socket.gethostname(), "boot_id": boot_id(self.contract),
                 "pid": os.getpid(), "process_start_wall": proc_start_wall(os.getpid()),
                 "run_id": run_id, "unit": unit,
                 "invocation_id": os.environ.get("INVOCATION_ID"),
                 "acquired_wall": time.time()}
        write_json_atomic(self.rt.owner, owner)
        return owner

    def read_owner(self):
        try:
            return json.loads(self.rt.owner.read_text())
        except Exception:                                         # noqa: BLE001
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
        """LIVE if another process holds it right now, else FREE."""
        if self.held:
            return "SELF"
        if not self.rt.lock.exists():
            return "FREE"
        fd = os.open(str(self.rt.lock), os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
            return "FREE"
        except BlockingIOError:
            return LIVE
        finally:
            os.close(fd)


def is_sanctioned_producer(pid, contract) -> bool:
    prefix = contract["service"]["unit_prefix"]
    try:
        cg = Path(f"/proc/{pid}/cgroup").read_text()
        cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return False
    return prefix in cg or "produce_entry.py" in cmd or "synthetic_entry.py" in cmd


def classify_ledger_lock(lock_path, contract, *, sanctioned=None) -> tuple:
    p = Path(lock_path)
    try:
        st = os.stat(p)
    except FileNotFoundError:
        return ABSENT, "no lock file"
    mtime = st.st_mtime
    bt = boot_time(contract)
    if mtime < bt - BOOT_TOLERANCE_S:
        return DEAD, f"lock written {bt - mtime:.1f}s before the current boot"
    if abs(mtime - bt) <= BOOT_TOLERANCE_S:
        return AMBIGUOUS, "lock written within 1 s of boot"
    content = p.read_bytes()[:64]
    m = re.fullmatch(rb"([0-9]{1,10})\n", content)
    if not m:
        return AMBIGUOUS, f"corrupted owner record in the current boot: {content!r}"
    pid = int(m.group(1))
    if pid <= 1:
        return AMBIGUOUS, f"implausible owner pid {pid}"
    if not pid_alive(pid):
        return DEAD, f"owner pid {pid} is not alive"
    sw = proc_start_wall(pid)
    if sw is None:
        return (DEAD, f"owner pid {pid} vanished") if not pid_alive(pid) else \
            (AMBIGUOUS, f"cannot read start time of live pid {pid}")
    if sw > mtime + PID_REUSE_TOLERANCE_S:
        return DEAD, f"pid {pid} reused: process started {sw - mtime:.1f}s after the lock"
    check = sanctioned or (lambda q: is_sanctioned_producer(q, contract))
    if check(pid):
        return LIVE, f"owner pid {pid} is a live sanctioned producer"
    return AMBIGUOUS, f"pid {pid} alive and older than the lock but not a sanctioned producer"


def reclaim_ledger_lock(lock_path, contract, *, campaign_lock, sanctioned=None) -> dict:
    if campaign_lock is None or not campaign_lock.held:
        raise OpsRefusal("stale-lock reclaim requires holding the campaign lock")
    state, why = classify_ledger_lock(lock_path, contract, sanctioned=sanctioned)
    if state == ABSENT:
        return {"state": ABSENT, "detail": why, "reclaimed": False}
    if state == DEAD:
        os.unlink(lock_path)
        return {"state": DEAD, "detail": why, "reclaimed": True}
    raise OpsRefusal(f"frozen ledger lock {state}: {why}; refusing to reclaim")
