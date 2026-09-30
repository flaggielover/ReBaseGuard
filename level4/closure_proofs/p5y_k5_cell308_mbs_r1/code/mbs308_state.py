"""Cell-308 MB-S successor campaign (r1) -- the durable lifecycle (architecture sections 2-4 and 7). No science.

Everything here is value-free bookkeeping around the ONE evaluation: it never computes, never prints a certified
quantity, and reads checkpoint CONTENT only through `Checkpointer.verified_records` (called by `resume` after the guard
is armed). The pieces:

  * the JOURNAL: a canonical JSON blob (self sha256, schema, strictly increasing `seq`, `prev` = the previous journal
    id) in the object store, written durably (`git -c core.fsync=loose-object,reference hash-object -w`) and then
    pointed to by refs/p5y-k5-cell308-mbs-r1/journal by compare-and-swap against the previous journal id. It records
    the state, the grant, the driver sha256, the boot session UUID, the process identity, the attempt counter, the
    checkpoint tree id and count, per-job checkpoint verification failures and the result's sha256 / blob id / seal
    commit (hashes only). It never carries a target value.
  * the SPOOL (section 3): <git dir>/mbs308-spool/ (outside the worktree, never tracked, never under /private/tmp):
    result.json.tmp by O_CREAT|O_EXCL|O_NOFOLLOW, fsync (+ F_FULLFSYNC), rename, directory fsync (+ F_FULLFSYNC),
    read-back byte equality and self-hash; `result.json.tmp` is never read as a result; a rejected file is renamed
    aside (never read again).
  * the PENDING ref, the SEAL (a private-index commit adding only the result path; branch update by CAS) and
    MATERIALIZATION (O_EXCL|O_NOFOLLOW) -- in the driver, which owns the paths; this module provides the object-store
    and ref primitives they use.
  * CHECKPOINTS (section 4): one blob per completed Stage-1 job (schema ...ckpt.v1: job key, the record's sha256, the
    grant, the driver sha256, the journal seq, the tagged-JSON record), entered into a tree pointed to by
    refs/p5y-k5-cell308-mbs-r1/ckpt (CAS); a checkpoint is never a result (no Stage 2, no decision, no `complete`).
  * the read-only STATE CLASSIFIER (section 2) over refs, spool, journal, process table and boot UUID;
  * the resume budget (3 resumes, 7 days after the marker), the two-consecutive-failures rule, the O_EXCL lockfile,
    the pidfile identity (pid, start time, boot UUID, command sha256), and the awake-time EVAL_CAP watchdog;
  * the TEST-ONLY fault hook `fault(point)`: inert unless a test assigns FAULT in-process; the driver's CLI refuses
    to run any mode when FAULT is set or an MBS308_TEST* variable is in the environment (static check in the tests).
"""
from __future__ import annotations

import datetime
import fcntl
import hashlib
import json
import os
import re
import secrets
import signal
import stat
import subprocess
import threading
import time
from fractions import Fraction as F
from pathlib import Path

import mbs308_host as HOST

# ------------------------------------------------------------------ frozen names and rules
REF_PREFIX = "refs/p5y-k5-cell308-mbs-r1/"
MARKER_REF = REF_PREFIX + "target-consumed"
PENDING_REF = REF_PREFIX + "pending-result"
JOURNAL_REF = REF_PREFIX + "journal"
CKPT_REF = REF_PREFIX + "ckpt"
ZERO = "0" * 40
SPOOL_NAME = "mbs308-spool"
RESULT_FILE = "result.json"
TMP_FILE = "result.json.tmp"
PIDFILE = "driver.pid"
LOCKFILE = "recover.lock"
HOST_LOG = "host-events.jsonl"
RESULT_SCHEMA = "rebaseguard.p5y.k5.cell308-mbs-r1.result.v1"
JOURNAL_SCHEMA = "rebaseguard.p5y.k5.cell308-mbs-r1.journal.v1"
CKPT_SCHEMA = "rebaseguard.p5y.k5.cell308-mbs-r1.ckpt.v1"
MAX_RESUMES = 3                                   # section 4 (b)
DEADLINE_S = 7 * 86400                            # section 4 (c): 7 days after the marker
CKPT_FAIL_LIMIT = 2                               # section 4 (a): two consecutive verification failures of one job
TARGET_EVALUATED = "TARGET_EVALUATED"
POST_MARKER_FAILURES = ("INDEPENDENT_CHECK_FAILED", "INCONSISTENT", "C6_REFUSED", "TARGET_EVALUATION_FAILED",
                        "POST_MARKER_RECORDING_FAILED", "RESUME_CONTROL_FAILED", "INDETERMINATE_CLOSED")
TERMINAL_STATUSES = (TARGET_EVALUATED, *POST_MARKER_FAILURES, "CONTROL_FAILED")
JOURNAL_STATES = ("ARMING", "COMPUTING", "RESULT_DURABLE", "PENDING_RESULT", "SEALED", "CLOSING_INDETERMINATE",
                  "INDETERMINATE_SEALED", "ABORTED_INTENT")
STATES = ("NO_TARGET_CONSUMED", "CONSUMED_COMPUTING", "CONSUMED_INTERRUPTED", "RESULT_DURABLE_UNSEALED",
          "PENDING_RESULT", "SEALED", "CONSUMED_UNRECORDED", "INDETERMINATE")
# the frozen recovery action of every state (section 2); `recover` performs exactly this and nothing else
ACTIONS = {"NO_TARGET_CONSUMED": "none", "CONSUMED_COMPUTING": "wait", "CONSUMED_INTERRUPTED": "resume",
           "RESULT_DURABLE_UNSEALED": "seal-only", "PENDING_RESULT": "seal-only", "SEALED": "materialize",
           "CONSUMED_UNRECORDED": "close-indeterminate", "INDETERMINATE": "materialize"}
GIT_WRITE_CFG = ("-c", "core.fsync=loose-object,reference", "-c", "core.fsyncMethod=fsync")
ENV = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/var/empty"), "GIT_OPTIONAL_LOCKS": "0",
       "GIT_NO_REPLACE_OBJECTS": "1", "LC_ALL": "C"}

# ------------------------------------------------------------------ the TEST-ONLY fault hook (section 7)
FAULT = None                    # production: None, always. Tests assign {point: {"at": k, "how": "exit"|"kill"}}.
_FAULT_COUNTS: dict = {}


def fault(point: str) -> None:
    """Fault point `point` (F1..F12): a real os._exit or SIGKILL of this process at its k-th passage. Inert in
    production (FAULT is None; the driver's CLI refuses to start when FAULT is set)."""
    spec = FAULT
    if spec is None:
        return
    s = spec.get(point)
    if s is None:
        return
    n = _FAULT_COUNTS[point] = _FAULT_COUNTS.get(point, 0) + 1
    if n < int(s.get("at", 1)):
        return
    if s.get("how") == "plant":             # R1 (iv): a lockfile appears here (what a reset inside a git write leaves)
        if n == int(s.get("at", 1)):
            fd = os.open(s["path"], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            os.write(fd, b"0" * 40 + b"\n")
            os.close(fd)
        return
    if s.get("how") == "bump_journal":      # R1 (iv): another writer advances the journal here (a genuine conflict)
        if n == int(s.get("at", 1)):
            st = Store(s["repo"], s["branch"])
            jid, jrec = Journal.read(st)
            Journal(st, jid, jrec).advance(bumped_by_test=True)
        return
    if s.get("how") == "kill":
        os.kill(os.getpid(), signal.SIGKILL)
        time.sleep(30)
    os._exit(int(s.get("code", 86)))


def test_hooks_present() -> list:
    """Why production must refuse (empty list = clean)."""
    why = [k for k in os.environ if k.startswith("MBS308_TEST")]
    if FAULT is not None:
        why.append("FAULT")
    return why


# ------------------------------------------------------------------ small helpers
class StateError(RuntimeError):
    """A lifecycle precondition failed (value-free)."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


class JournalConflict(StateError):
    """The journal CAS failed: another process advanced the journal (it owns the run now)."""


class RefWriteError(OSError):
    """R1 (i): an update-ref failure that is NOT a compare-and-swap conflict (the ref still holds the expected old
    value: a stale lockfile, an I/O error). Recorded and retried; never read as "another process owns the run"."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


REF_WRITE_FAILURES: list = []      # value-free, in memory: {utc, ref, try, rc, lock_present}


class LostOwnership(BaseException):
    """Raised inside a running attempt whose journal was advanced by another process: the attempt must stop at once
    and persist nothing (the new owner holds the evaluation)."""


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_blob_id(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def utc(epoch: float | None = None) -> str:
    t = datetime.datetime.now(datetime.timezone.utc) if epoch is None else \
        datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_utc(s: str) -> float:
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc).timestamp()


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def serialize(obj: dict) -> bytes:
    """The result bytes (MB r1 layout: indent 1, sorted keys, self sha256). MB-S normalizes through one JSON round trip
    FIRST, so the self sha256 is re-verifiable from the bytes (MB r1's hashed the pre-normalization object: an
    int-keyed dict sorts numerically before and lexically after a round trip, so its hash could not be re-verified)."""
    body = json.loads(json.dumps(obj, sort_keys=True))
    body.pop("sha256", None)
    body["sha256"] = sha(json.dumps(body, sort_keys=True).encode())
    return (json.dumps(body, indent=1, sort_keys=True) + "\n").encode()


def verify_serialized(data: bytes) -> dict | None:
    """The record if `data` is exactly serialize(record) (canonical layout and a matching self sha256), else None."""
    try:
        body = json.loads(data)
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(body, dict) or not isinstance(body.get("sha256"), str):
        return None
    rest = dict(body)
    got = rest.pop("sha256")
    if got != sha(json.dumps(rest, sort_keys=True).encode()):
        return None
    if data != (json.dumps(body, indent=1, sort_keys=True) + "\n").encode():
        return None
    return body


def canon_signed(obj: dict) -> bytes:
    body = dict(obj)
    body.pop("self_sha256", None)
    body["self_sha256"] = sha(canon(body))
    return canon(body)


def verify_signed(data: bytes) -> dict | None:
    try:
        body = json.loads(data)
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(body, dict):
        return None
    rest = dict(body)
    got = rest.pop("self_sha256", None)
    if got is None or got != sha(canon(rest)) or canon(body) != data:
        return None
    return body


# ------------------------------------------------------------------ tagged JSON (lossless checkpoint records)
def enc(o):
    """Lossless JSON for a Stage-1 job record: Fraction, float, tuple and dict (as ordered key/value pairs) are
    tagged, so that decoding rebuilds equal objects of equal types with equal dict insertion order."""
    if o is None or isinstance(o, (bool, str)):
        return o
    if isinstance(o, int):
        return o
    if isinstance(o, float):
        return {"$f": o.hex()}
    if isinstance(o, F):
        return {"$F": f"{o.numerator}/{o.denominator}"}
    if isinstance(o, tuple):
        return {"$T": [enc(x) for x in o]}
    if isinstance(o, list):
        return [enc(x) for x in o]
    if isinstance(o, dict):              # ALWAYS ordered pairs: key types AND insertion order survive (canon sorts keys)
        return {"$D": [[enc(k), enc(v)] for k, v in o.items()]}
    raise TypeError(f"checkpoint encoding: unsupported type {type(o).__name__}")


def dec(o):
    if isinstance(o, list):
        return [dec(x) for x in o]
    if isinstance(o, dict):
        if len(o) == 1:
            (k, v), = o.items()
            if k == "$f":
                return float.fromhex(v)
            if k == "$F":
                n, d = v.split("/")
                return F(int(n), int(d))
            if k == "$T":
                return tuple(dec(x) for x in v)
            if k == "$D":
                return {dec(a): dec(b) for a, b in v}
        return {k: dec(v) for k, v in o.items()}
    return o


# ------------------------------------------------------------------ the campaign's git / spool store
class Store:
    """Git plumbing and the spool for ONE repository (the qualified worktree, or a test sandbox)."""

    def __init__(self, repo, branch_ref: str, retry_delays: tuple = ()):
        self.repo = Path(repo)
        self.branch_ref = branch_ref
        self.retry_delays = tuple(retry_delays)   # the driver passes MB r1's SEAL_RETRY_DELAYS (no new number)
        self._gd = None
        self._cd = None

    # ---- git
    def git(self, *args, input_bytes=None, write=False, text=True, env_extra=None):
        env = dict(ENV)
        if env_extra:
            env.update(env_extra)
        cmd = ["/usr/bin/git", "--no-replace-objects", *(GIT_WRITE_CFG if write else ()), "-C", str(self.repo), *args]
        p = subprocess.run(cmd, input=input_bytes, capture_output=True, env=env,
                           stdin=None if input_bytes is not None else subprocess.DEVNULL)
        if text:
            return subprocess.CompletedProcess(p.args, p.returncode, p.stdout.decode(errors="replace"),
                                               p.stderr.decode(errors="replace"))
        return p

    def rev(self, ref: str) -> str:
        p = self.git("rev-parse", "-q", "--verify", ref)
        return p.stdout.strip() if p.returncode == 0 else ""

    def obj_type(self, oid: str) -> str:
        p = self.git("cat-file", "-t", oid)
        return p.stdout.strip() if p.returncode == 0 else ""

    def read_ref(self, ref: str) -> tuple:
        """(readable, value): value "" = the ref does not exist; readable False = the read itself failed."""
        p = self.git("rev-parse", "-q", "--verify", ref)
        if p.returncode == 0:
            return True, p.stdout.strip()
        if p.returncode == 1 and not p.stdout.strip():
            return True, ""
        return False, None

    def cas_ref(self, ref: str, new: str, old: str | None) -> bool:
        """update-ref by compare-and-swap (`old` None or ZERO = the ref must not exist). R1 (i): after a failed
        update-ref the ref is RE-READ. Only "the ref no longer holds the expected old value" is a conflict (False).
        Anything else (a stale lockfile, an I/O error, an unreadable ref) is recorded and retried on
        `retry_delays`; if it persists: RefWriteError (infrastructure)."""
        expect = "" if old in (None, ZERO) else old
        for i, delay in enumerate((0.0, *self.retry_delays)):
            if delay:
                time.sleep(delay)
            p = self.git("update-ref", ref, new, old or ZERO, write=True)
            if p.returncode == 0:
                return True
            readable, cur = self.read_ref(ref)
            if readable and cur != expect:
                return False                                  # a genuine compare-and-swap conflict
            REF_WRITE_FAILURES.append({"utc": utc(), "ref": ref, "try": i + 1, "rc": p.returncode,
                                       "lock_present": os.path.lexists(self.common_dir() / (ref + ".lock"))})
        raise RefWriteError("REF_WRITE_FAILED", ref)

    def put_blob(self, data: bytes) -> str:
        p = self.git("hash-object", "-w", "--stdin", input_bytes=data, write=True)
        oid = p.stdout.strip()
        if p.returncode or oid != git_blob_id(data):
            raise OSError("hash-object did not store the produced bytes")
        return oid

    def get_blob(self, oid: str) -> bytes | None:
        if not oid or not re.fullmatch(r"[0-9a-f]{40}", oid) or self.obj_type(oid) != "blob":
            return None
        p = self.git("cat-file", "blob", oid, text=False)
        if p.returncode or git_blob_id(p.stdout) != oid:
            return None
        return p.stdout

    def ls_tree(self, tree: str) -> dict | None:
        """{name: blob id} of a flat tree; None if it is not a readable tree."""
        if not tree or self.obj_type(tree) != "tree":
            return None
        p = self.git("ls-tree", "-z", tree, text=False)
        if p.returncode:
            return None
        out = {}
        for item in p.stdout.split(b"\0"):
            if not item:
                continue
            meta, name = item.split(b"\t", 1)
            mode, typ, oid = meta.decode().split()
            if typ != "blob" or mode != "100644":
                return None
            out[name.decode()] = oid
        return out

    def mktree(self, entries: dict) -> str:
        body = "".join(f"100644 blob {oid}\t{name}\n" for name, oid in sorted(entries.items())).encode()
        p = self.git("mktree", input_bytes=body, write=True)
        if p.returncode or not p.stdout.strip():
            raise OSError("mktree failed")
        return p.stdout.strip()

    def git_dir(self) -> Path:
        if self._gd is None:
            self._gd = Path(self.git("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip())
        return self._gd

    def common_dir(self) -> Path:
        if self._cd is None:
            self._cd = Path(self.git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
        return self._cd

    # ---- spool (section 3)
    def spool(self, create: bool = False) -> Path:
        d = self.git_dir() / SPOOL_NAME
        if create:
            try:
                os.mkdir(d, 0o700)
            except FileExistsError:
                pass
        if os.path.lexists(d):
            st = os.lstat(d)
            if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid():
                raise StateError("SPOOL_UNSAFE", "the spool is not a plain directory owned by this user")
        return d

    def spool_exists(self, name: str) -> bool:
        return os.path.lexists(self.spool() / name)

    def spool_read(self, name: str) -> bytes | None:
        """Read a spool file with O_NOFOLLOW (a regular file, one link) or None. Never used for result.json.tmp."""
        if name == TMP_FILE:
            raise StateError("TMP_NEVER_READ", "result.json.tmp is never read as a result")
        d = self.spool()
        try:
            fd = os.open(d / name, os.O_RDONLY | os.O_NOFOLLOW)
        except (FileNotFoundError, OSError):
            return None
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                return None
            chunks = []
            while chunk := os.read(fd, 1 << 20):
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(fd)

    def quarantine(self, name: str, reason: str) -> str | None:
        """Rename a spool file aside (never read again); returns the new name."""
        d = self.spool()
        if not os.path.lexists(d / name):
            return None
        new = f"{name}.rejected-{reason}-{datetime.datetime.now(datetime.timezone.utc):%Y%m%dT%H%M%S}-" \
              f"{secrets.token_hex(3)}"
        dfd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.rename(name, new, src_dir_fd=dfd, dst_dir_fd=dfd)
            fsync_dir(dfd)
        finally:
            os.close(dfd)
        return new

    def spool_write_result(self, data: bytes) -> dict:
        """Section 3 steps 3-5: O_EXCL tmp, fsync, rename, dir fsync (+ F_FULLFSYNC), read-back verify. Fault points
        F5 (partial tmp), F6 (after write, before fsync), F7 (after fsync, before rename)."""
        d = self.spool(create=True)
        if self.spool_exists(RESULT_FILE):
            raise StateError("SPOOL_RESULT_EXISTS", "a result.json is already in the spool")
        if self.spool_exists(TMP_FILE):
            self.quarantine(TMP_FILE, "stale-tmp")
        dfd = os.open(d, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        steps = []
        try:
            fd = os.open(TMP_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=dfd)
            steps.append("open_excl")
            try:
                half = len(data) // 2
                _write_all(fd, data[:half])
                fault("F5")
                _write_all(fd, data[half:])
                steps.append("write")
                fault("F6")
                fsync_file(fd)
                steps.append("fsync")
            finally:
                os.close(fd)
            fault("F7")
            os.rename(TMP_FILE, RESULT_FILE, src_dir_fd=dfd, dst_dir_fd=dfd)
            steps.append("rename")
            fsync_dir(dfd)
            steps.append("dir_fsync")
        finally:
            os.close(dfd)
        back = self.spool_read(RESULT_FILE)
        if back != data or verify_serialized(back) is None:
            raise OSError("spool read-back differs from the produced bytes or its self sha256 fails")
        steps.append("read_back_verified")
        return {"sha256": sha(data), "bytes": len(data), "steps": steps}

    def host_log(self, ev: dict) -> None:
        """Append one value-free host event (caffeinate deaths / re-spawns, attempt snapshots) durably."""
        d = self.spool(create=True)
        fd = os.open(d / HOST_LOG, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
        try:
            _write_all(fd, canon(ev) + b"\n")
            fsync_file(fd)
        finally:
            os.close(fd)

    def host_log_read(self) -> list:
        raw = self.spool_read(HOST_LOG) or b""
        out = []
        for ln in raw.splitlines():
            try:
                out.append(json.loads(ln))
            except ValueError:
                out.append({"unparseable_line": True})
        return out


def _write_all(fd: int, b: bytes) -> None:
    view = memoryview(b)
    while view:
        n = os.write(fd, view)
        view = view[n:]


def fsync_file(fd: int) -> None:
    os.fsync(fd)
    try:
        fcntl.fcntl(fd, fcntl.F_FULLFSYNC)
    except (AttributeError, OSError):
        pass


def fsync_dir(dfd: int) -> None:
    os.fsync(dfd)
    try:
        fcntl.fcntl(dfd, fcntl.F_FULLFSYNC)
    except (AttributeError, OSError):
        pass


# ------------------------------------------------------------------ result verification (no value is printed)
def verify_result(data: bytes | None, *, grant: str, driver_sha: str | None) -> tuple:
    """(record, "") if `data` is a complete target result (or value-free record) bound to this grant and driver:
    canonical bytes, self sha256, schema, complete = true, a terminal status, cell 308. Else (None, reason)."""
    if data is None:
        return None, "ABSENT"
    rec = verify_serialized(data)
    if rec is None:
        return None, "SELF_HASH_OR_LAYOUT"
    if rec.get("schema") != RESULT_SCHEMA:
        return None, "SCHEMA"
    if rec.get("complete") is not True or rec.get("status") not in TERMINAL_STATUSES:
        return None, "NOT_COMPLETE"
    if rec.get("cell") != 308:
        return None, "CELL"
    g = rec.get("grant")
    if not isinstance(g, dict) or g.get("grant_commit") != grant:
        return None, "GRANT_BINDING"
    if driver_sha is None or rec.get("driver_sha256") != driver_sha:
        return None, "DRIVER_BINDING"
    return rec, ""


# ------------------------------------------------------------------ the journal
class Journal:
    """The single writer's view: the current (id, record); every advance is a durable blob + a CAS on the ref."""

    def __init__(self, store: Store, jid: str | None, rec: dict | None):
        self.store, self.jid, self.rec = store, jid, rec

    @staticmethod
    def read(store: Store) -> tuple:
        """(id, record) -- record None when absent or invalid (schema, self sha256, seq, state)."""
        jid = store.rev(JOURNAL_REF)
        if not jid:
            return "", None
        rec = verify_signed(store.get_blob(jid) or b"")
        if rec is None or rec.get("schema") != JOURNAL_SCHEMA or not isinstance(rec.get("seq"), int) or \
                rec["seq"] < 1 or rec.get("state") not in JOURNAL_STATES:
            return jid, None
        return jid, rec

    def advance(self, **changes) -> str:
        new = dict(self.rec or {})
        new.update(changes)
        seq = (self.rec or {}).get("seq", 0) + 1
        if new.get("attempt_seq") == "SELF":             # the entry that starts an attempt records its own seq
            new["attempt_seq"] = seq
        new.update({"schema": JOURNAL_SCHEMA, "seq": seq, "prev": self.jid or None, "utc": utc()})
        data = canon_signed(new)
        oid = self.store.put_blob(data)
        if not self.store.cas_ref(JOURNAL_REF, oid, self.jid or None):
            raise JournalConflict("JOURNAL_CAS", "the journal moved (another process owns the run)")
        self.jid, self.rec = oid, verify_signed(data)
        return oid


# ------------------------------------------------------------------ checkpoints (section 4)
def ckpt_name(key) -> str:
    kind, block, rung = key
    if not re.fullmatch(r"[A-Z0-9]{2,8}", str(kind)):
        raise ValueError("checkpoint job kind")
    return f"{kind}.{int(block)}.{int(rung)}"


def ckpt_key(name: str):
    m = re.fullmatch(r"([A-Z0-9]{2,8})\.(\d+)\.(\d+)", name)
    return None if m is None else (m.group(1), int(m.group(2)), int(m.group(3)))


TERMINAL_JOURNAL_STATES = ("SEALED", "INDETERMINATE_SEALED", "CLOSING_INDETERMINATE")


def job_identity_ok(name: str, key, rec: dict, record) -> bool:
    """A checkpoint is served only as the job it was written for: the tree entry name, the checkpoint's own name and
    job fields, and the decoded record's (kind, block, rung) must all name the same job (never job A served as B)."""
    if key is None or rec.get("name") != name or rec.get("job") != [key[0], key[1], key[2]]:
        return False
    if isinstance(record, dict) and {"kind", "block", "rung"} <= set(record):
        return (record["kind"], record["block"], record["rung"]) == key
    return True


def platform_digest(platform: dict | None) -> str | None:
    return None if platform is None else sha(canon(platform))


class Checkpointer:
    """Writes one checkpoint per completed Stage-1 job, bound to (grant, driver sha256, attempt, the journal seq that
    started the attempt, the platform digest); `verified_records` (resume only, guard armed, never after a terminal
    state -- MBS-4) returns the records whose hash, schema and every binding verify, and the names that failed. No
    journal entry is written per checkpoint (MBS-3: durable logs carry state transitions only); the checkpoint tree is
    the only per-job record."""

    def __init__(self, store: Store, journal: Journal | None, grant: str, driver_sha: str, ref: str = CKPT_REF,
                 attempt: int | None = None, attempt_seq: int | None = None, platform: dict | None = None,
                 campaign=None):
        self.store, self.journal, self.grant, self.driver_sha, self.ref = store, journal, grant, driver_sha, ref
        self.attempt, self.attempt_seq, self.platform_sha = attempt, attempt_seq, platform_digest(platform)
        self.campaign = campaign
        self.tree = store.rev(ref) or ""
        self.entries = (store.ls_tree(self.tree) or {}) if self.tree else {}
        self.written, self.write_failures = 0, 0

    def write(self, key, record) -> None:
        name = ckpt_name(key)
        body = enc(record)
        payload = {"schema": CKPT_SCHEMA, "job": [key[0], int(key[1]), int(key[2])], "name": name,
                   "grant_commit": self.grant, "driver_sha256": self.driver_sha, "attempt": self.attempt,
                   "journal_seq": self.attempt_seq, "platform_sha256": self.platform_sha,
                   "record_sha256": sha(canon(body)), "record": body}
        oid = self.store.put_blob(canon_signed(payload))
        entries = dict(self.entries)
        entries[name] = oid
        tree = self.store.mktree(entries)
        if not self.store.cas_ref(self.ref, tree, self.tree or None):
            raise JournalConflict("CKPT_CAS", "the checkpoint tree moved (another process owns the run)")
        self.tree, self.entries = tree, entries
        self.written += 1
        fault("F3")

    def refuse_if_terminal(self) -> None:
        """MBS-4: once the run is terminal (SEALED / INDETERMINATE, or closing), checkpoint content is never read."""
        jrec = Journal.read(self.store)[1] if self.journal is not None or self.campaign is not None else None
        if jrec is not None and jrec.get("state") in TERMINAL_JOURNAL_STATES:
            raise StateError("CKPT_TERMINAL", "the run is terminal: checkpoints are never read again")
        if self.campaign is not None and sealed_entry(self.campaign) is not None:
            raise StateError("CKPT_TERMINAL", "a record is sealed: checkpoints are never read again")

    def verified_records(self, attempts: dict | None = None) -> tuple:
        """({key: record}, [failed names]) -- READS CHECKPOINT CONTENT: only `resume`, after arming the guard, and never
        after a terminal state. `attempts` = {attempt: the journal seq that started it} of the PREVIOUS attempts (from
        the journal); a checkpoint must name one of them exactly (not another attempt, not a future seq)."""
        self.refuse_if_terminal()
        good, bad = {}, []
        for name, oid in sorted(self.entries.items()):
            key = ckpt_key(name)
            rec = verify_signed(self.store.get_blob(oid) or b"")
            ok = key is not None and rec is not None and rec.get("schema") == CKPT_SCHEMA
            ok = ok and rec.get("grant_commit") == self.grant                             # the grant
            ok = ok and rec.get("driver_sha256") == self.driver_sha                       # the driver
            ok = ok and rec.get("platform_sha256") == self.platform_sha                   # the platform pin
            if ok and attempts is not None:                                               # the attempt and its seq
                ok = rec.get("attempt") in attempts and rec.get("journal_seq") == attempts[rec.get("attempt")]
            ok = ok and isinstance(rec.get("record"), (dict, list)) and \
                rec.get("record_sha256") == sha(canon(rec["record"]))
            if ok:
                try:
                    r = dec(rec["record"])
                except (ValueError, TypeError, KeyError):
                    r, ok = None, False
                ok = ok and job_identity_ok(name, key, rec, r)                            # job A never served as B
            if ok:
                good[key] = r
            else:
                bad.append(name)
        return good, bad


# ------------------------------------------------------------------ lock and pidfile (section 5)
class Locked(StateError):
    pass


class Lock:
    """O_EXCL lockfile in the spool holding the owner's identity. A stale lock (its recorded identity is positively
    DEAD, HOST.identity_state; a failed `ps` or boot-UUID reading is UNKNOWN and keeps the lock held; no recorded
    identity: no process) is reported, moved aside after re-reading it, and replaced; the journal CAS is the second line
    of defence."""

    def __init__(self, store: Store, name: str = LOCKFILE):
        self.store, self.name, self.held, self.stale_broken = store, name, False, None

    def acquire(self) -> dict:
        d = self.store.spool(create=True)
        me = HOST.identity()
        data = canon({"identity": me, "utc": utc()})
        for _ in range(4):
            try:
                fd = os.open(d / self.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            except FileExistsError:
                holder_raw = self.store.spool_read(self.name)
                if holder_raw is None:                     # it vanished meanwhile: try again
                    continue
                try:
                    holder = json.loads(holder_raw).get("identity")
                except (ValueError, AttributeError):
                    holder = None
                if _not_dead(holder, None, None):          # liveness delta: alive unless positively DEAD
                    raise Locked("LOCKED", "another recover / resume holds the lock")
                aside = f"{self.name}.rejected-stale-lock-{datetime.datetime.now(datetime.timezone.utc):%Y%m%dT%H%M%S}-" \
                        f"{secrets.token_hex(3)}"
                dfd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.rename(self.name, aside, src_dir_fd=dfd, dst_dir_fd=dfd)
                except FileNotFoundError:                  # another breaker moved it first: try again
                    continue
                finally:
                    os.close(dfd)
                if self.store.spool_read(aside) != holder_raw:
                    try:                                   # we moved ANOTHER breaker's fresh lock: put it back
                        os.link(d / aside, d / self.name)
                    except OSError:
                        pass
                    raise Locked("LOCK_RACE", "the lock changed while it was being broken")
                self.stale_broken = aside
                continue
            try:
                _write_all(fd, data)
                fsync_file(fd)
            finally:
                os.close(fd)
            self.held = True
            return {"identity": me, "stale_lock_broken": self.stale_broken}
        raise Locked("LOCK_RACE", "the lock could not be taken")

    def release(self) -> None:
        if not self.held:
            return
        d = self.store.spool()
        raw = self.store.spool_read(self.name)
        try:
            ident = json.loads(raw or b"{}").get("identity", {})
        except ValueError:
            ident = {}
        if ident.get("pid") == os.getpid():
            os.unlink(d / self.name)
        self.held = False


def write_pidfile(store: Store, extra: dict) -> dict:
    d = store.spool(create=True)
    rec = {"identity": HOST.identity(), **extra, "utc": utc()}
    tmp = f"{PIDFILE}.tmp-{os.getpid()}-{secrets.token_hex(3)}"
    dfd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=dfd)
        try:
            _write_all(fd, canon(rec))
            fsync_file(fd)
        finally:
            os.close(fd)
        os.rename(tmp, PIDFILE, src_dir_fd=dfd, dst_dir_fd=dfd)
        fsync_dir(dfd)
    finally:
        os.close(dfd)
    return rec


def read_pidfile(store: Store, boot_uuid: str | None = None) -> tuple:
    """(record, "ABSENT" | "LIVE" | "STALE" | "INVALID"): LIVE only if all four identity fields match a live process
    under the current boot. A stale pidfile is reported and never trusted."""
    try:
        raw = store.spool_read(PIDFILE)
    except StateError:
        return None, "INVALID"
    if raw is None:
        return None, "ABSENT"
    try:
        rec = json.loads(raw)
    except ValueError:
        return None, "INVALID"
    ident = rec.get("identity") if isinstance(rec, dict) else None
    if not isinstance(ident, dict):
        return rec, "INVALID"
    return rec, "LIVE" if HOST.identity_alive(ident, boot_uuid) else "STALE"


def remove_own_pidfile(store: Store) -> None:
    rec, st = read_pidfile(store)
    if rec and isinstance(rec.get("identity"), dict) and rec["identity"].get("pid") == os.getpid():
        try:
            os.unlink(store.spool() / PIDFILE)
        except OSError:
            pass


# ------------------------------------------------------------------ stale git lockfiles of the campaign (R1 iii)
LOCKS_ASIDE = "git-locks-aside"
RECOVER_ACTIONS = "recover-actions.jsonl"
LSOF = "/usr/sbin/lsof"


def git_lockfiles(st: Store) -> list:
    """The campaign's git lockfiles, relative to the common dir: refs/p5y-k5-cell308-mbs-r1/*.lock and the branch lock
    (what a reset or power loss inside one of the campaign's own ref writes leaves).

    C-1 (REVIEW_IMPLEMENTATION_MBS308_DELTA): packed-refs.lock is NEVER a campaign lockfile. It blocks only ref
    deletion, which the campaign never performs, so the campaign never creates or owns it; whenever it exists it
    belongs to some other git process of the shared repository (gc, pack-refs, a ref deletion in any worktree), and a
    live git holder has no open descriptor, so lsof cannot prove it stale. It is never listed, never moved and never
    deleted here; MB r1's carried check_clean refuses it before the marker (nothing consumed), and after the marker a
    ref write it prevented would fail as a recorded RefWriteError (fail closed; git keeps its own lock)."""
    cd = st.common_dir()
    out = []
    d = cd / REF_PREFIX.rstrip("/")
    if d.is_dir():
        out += sorted(f"{REF_PREFIX}{p.name}" for p in d.iterdir() if p.name.endswith(".lock"))
    rel = st.branch_ref + ".lock"
    if os.path.lexists(cd / rel):
        out.append(rel)
    return out


def lockfile_open(path) -> bool | None:
    """True: some process has the file open; False: none (lsof finds nothing); None: unknown (lsof failed)."""
    try:
        p = subprocess.run([LSOF, "-t", "--", str(path)], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           env={"PATH": "/usr/bin:/bin:/usr/sbin", "LC_ALL": "C"})
    except OSError:
        return None
    if p.returncode == 0 and p.stdout.strip():
        return True
    if p.returncode == 1 and not p.stdout.strip():
        return False
    return None


def _not_dead(ident, boot_uuid: str | None, exclude_pid: int | None) -> bool:
    """N-3: a RECORDED campaign process identity holds the lockfiles unless it is positively DEAD
    (HOST.identity_state); a failed `ps` or boot-UUID reading (UNKNOWN) is never evidence of death. No recorded
    identity: no process."""
    if not isinstance(ident, dict) or ident.get("pid") == exclude_pid:
        return False
    return HOST.identity_state(ident, boot_uuid) != "DEAD"


def git_lock_info(st: Store, boot_uuid: str | None = None, exclude_pid: int | None = None) -> dict:
    """Read-only. The lockfiles are STALE only when every recorded campaign process (the O_EXCL recover lock's
    holder, the pidfile, the journal's recorded process) is positively dead AND no process has any of them open."""
    locks = git_lockfiles(st)
    if not locks:
        return {"git_locks": [], "git_locks_stale": None}
    live = []
    jrec = Journal.read(st)[1]
    if jrec is not None and _not_dead(jrec.get("process"), boot_uuid, exclude_pid):
        live.append("journal_process")
    prec, _pst = read_pidfile(st, boot_uuid)
    if isinstance(prec, dict) and _not_dead(prec.get("identity"), boot_uuid, exclude_pid):
        live.append("pidfile")
    try:
        holder = json.loads(st.spool_read(LOCKFILE) or b"{}").get("identity")
    except (ValueError, AttributeError, StateError):
        holder = None
    if _not_dead(holder, boot_uuid, exclude_pid):
        live.append("recover_lock")
    opened = {rel: lockfile_open(st.common_dir() / rel) for rel in locks}
    return {"git_locks": locks, "git_locks_live_campaign_process": live,
            "git_locks_not_provably_closed": [r for r, v in opened.items() if v is not False],
            "git_locks_stale": not live and all(v is False for v in opened.values())}


def move_stale_git_locks(st: Store, boot_uuid: str | None = None) -> list:
    """`recover`'s frozen action for stale campaign git lockfiles: under the O_EXCL campaign lock, re-verify that they
    are stale, then MOVE each one aside into the spool (never delete; never inside refs/, where a renamed file would
    read as a ref), fsync both directories, and append a value-free record (name, size, birth and change times,
    where it went, by whom) to <spool>/recover-actions.jsonl."""
    lock = Lock(st)
    lock.acquire()
    try:
        info = git_lock_info(st, boot_uuid, exclude_pid=os.getpid())
        if not info["git_locks"]:
            return []
        if not info["git_locks_stale"]:
            raise StateError("GIT_LOCKS_NOT_STALE", "a live campaign process or an open file holds a lockfile")
        sp = st.spool(create=True)
        aside = sp / LOCKS_ASIDE
        try:
            os.mkdir(aside, 0o700)
        except FileExistsError:
            pass
        moved = []
        for rel in info["git_locks"]:
            src = st.common_dir() / rel
            stt = os.lstat(src)
            name = rel.replace("/", "__") + f".{datetime.datetime.now(datetime.timezone.utc):%Y%m%dT%H%M%S}." \
                f"{secrets.token_hex(3)}"
            os.rename(src, aside / name)
            for d in (src.parent, aside):
                dfd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    fsync_dir(dfd)
                finally:
                    os.close(dfd)
            rec = {"utc": utc(), "action": "git_lock_moved_aside", "lock": rel, "bytes": stt.st_size,
                   "birth_utc": utc(stt.st_birthtime), "mtime_utc": utc(stt.st_mtime),
                   "moved_to": f"{LOCKS_ASIDE}/{name}", "by": HOST.identity()}
            fd = os.open(sp / RECOVER_ACTIONS, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
            try:
                _write_all(fd, canon(rec) + b"\n")
                fsync_file(fd)
            finally:
                os.close(fd)
            moved.append(rec)
        return moved
    finally:
        lock.release()


def recover_actions_read(st: Store) -> list:
    try:
        raw = st.spool_read(RECOVER_ACTIONS) or b""
    except StateError:
        return []
    return [json.loads(x) for x in raw.splitlines() if x.strip()]


# ------------------------------------------------------------------ EVAL_CAP per attempt, on awake time (section 8)
class AwakeCap:
    """EVAL_CAP counted on CLOCK_UPTIME_RAW (which stops while the host sleeps, channel K): the cap applies per attempt,
    from the marker or from the resume start, and never across a sleep. On expiry it sends SIGALRM to this process
    (the driver's handler raises TimeoutError in the main thread, exactly as MB r1's alarm did)."""

    def __init__(self, cap_s: float, poll_s: float = 5.0, on_hit=None):
        self.cap_s, self.poll_s = cap_s, poll_s
        self.on_hit = on_hit or (lambda: os.kill(os.getpid(), signal.SIGALRM))
        self._stop = threading.Event()
        self.hit = False
        self.t0 = None
        self._t = threading.Thread(target=self._loop, name="mbs308-awake-cap", daemon=True)

    def elapsed(self) -> float:
        return (time.clock_gettime_ns(time.CLOCK_UPTIME_RAW) - self.t0) / 1e9

    def _loop(self) -> None:
        while not self._stop.wait(min(self.poll_s, max(0.01, self.cap_s / 20))):
            if self.elapsed() >= self.cap_s:
                self.hit = True
                self.on_hit()
                return

    def start(self) -> "AwakeCap":
        self.t0 = time.clock_gettime_ns(time.CLOCK_UPTIME_RAW)
        self._t.start()
        return self

    def stop(self) -> dict:
        self._stop.set()
        return {"cap_s": self.cap_s, "awake_elapsed_s": round(self.elapsed(), 3) if self.t0 else None, "hit": self.hit,
                "clock": "CLOCK_UPTIME_RAW"}


# ------------------------------------------------------------------ the read-only state classifier (section 2)
class Campaign:
    """Where the campaign lives: the store (repo + branch), the result path in the tree and the grant path."""

    def __init__(self, store: Store, result_rel: str, grant_rel: str):
        self.store, self.result_rel, self.grant_rel = store, result_rel, grant_rel


def granted_driver_sha(camp: Campaign, grant_commit: str) -> str | None:
    p = camp.store.git("show", f"{grant_commit}:{camp.grant_rel}")
    if p.returncode:
        return None
    try:
        g = json.loads(p.stdout)
    except ValueError:
        return None
    v = g.get("driver_sha256") if isinstance(g, dict) else None
    return v if isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) else None


def sealed_entry(camp: Campaign) -> str | None:
    head = camp.store.rev(camp.store.branch_ref)
    if not head:
        return None
    p = camp.store.git("ls-tree", head, "--", camp.result_rel)
    parts = p.stdout.split()
    if p.returncode or not parts:
        return None
    return parts[2] if parts[:2] == ["100644", "blob"] else "NOT_A_BLOB"


def classify(camp: Campaign, *, platform: dict, boot_uuid: str | None = None, now: float | None = None) -> dict:
    """The state (section 2) from refs, spool, journal, process table, boot UUID and the current platform readings
    (RC2 / DR2: a resume never runs on another platform) only. Read-only: no ref, file or object is written; checkpoint
    CONTENT is never read (only the tree listing). Returns value-free details."""
    if not isinstance(platform, dict):
        raise StateError("PLATFORM_READINGS", "the classifier needs the current platform readings")
    st = camp.store
    why: list = []
    info = {"marker": st.rev(MARKER_REF) or None, **git_lock_info(st, boot_uuid)}
    marker = info["marker"]
    if not marker:
        return {"state": "NO_TARGET_CONSUMED", "why": ["NO_MARKER"], **info}
    drv = granted_driver_sha(camp, marker)
    info["driver_sha256"] = drv
    # 1. a seal on the branch
    ent = sealed_entry(camp)
    if ent is not None:
        rec, r = verify_result(st.get_blob(ent) if ent != "NOT_A_BLOB" else None, grant=marker, driver_sha=drv)
        info["sealed_blob"] = ent
        if rec is None:
            return {"state": "INDETERMINATE", "why": ["SEALED_RECORD_FAILS_VERIFICATION:" + r], **info}
        if rec["status"] == TARGET_EVALUATED:
            info["pending_names_sealed_blob"] = st.rev(PENDING_REF) == ent
            return {"state": "SEALED", "why": ["SEALED_TARGET_EVALUATED"], **info}
        return {"state": "INDETERMINATE", "why": ["SEALED_STATUS:" + rec["status"]], **info}
    # 2. a pending ref naming verified bytes
    pending = st.rev(PENDING_REF)
    if pending:
        rec, r = verify_result(st.get_blob(pending), grant=marker, driver_sha=drv)
        if rec is not None:
            return {"state": "PENDING_RESULT", "why": ["PENDING_VERIFIES"], "pending": pending, **info}
        why.append("STALE_PENDING_REF:" + r)
        info["stale_pending"] = pending
    # 3. a durable, verified complete result in the spool (result.json only; the .tmp is never read)
    try:
        spool_data = st.spool_read(RESULT_FILE)
    except StateError as exc:
        spool_data = None
        why.append("SPOOL_UNSAFE:" + exc.code)
    if spool_data is not None:
        rec, r = verify_result(spool_data, grant=marker, driver_sha=drv)
        if rec is not None:
            return {"state": "RESULT_DURABLE_UNSEALED", "why": why + ["SPOOL_RESULT_VERIFIES"], **info}
        why.append("SPOOL_RESULT_REJECTED:" + r)
        info["spool_result_rejected"] = True
    # 4. the journal
    jid, jrec = Journal.read(st)
    info["journal"] = jid or None
    if jrec is None:
        return {"state": "CONSUMED_UNRECORDED", "why": why + ["NO_JOURNAL" if not jid else "JOURNAL_INVALID"], **info}
    info["journal_seq"], info["attempt"] = jrec["seq"], jrec.get("attempt")
    if jrec.get("grant_commit") != marker or drv is None or jrec.get("driver_sha256") != drv:
        return {"state": "CONSUMED_UNRECORDED", "why": why + ["JOURNAL_BINDING"], **info}
    if jrec["state"] in ("CLOSING_INDETERMINATE", "INDETERMINATE_SEALED"):
        return {"state": "CONSUMED_UNRECORDED", "why": why + ["CLOSING_INDETERMINATE"], **info}
    if jrec["state"] == "ABORTED_INTENT":        # an intent whose marker CAS failed: it never owned the marker
        return {"state": "CONSUMED_UNRECORDED", "why": why + ["ABORTED_INTENT"], **info}
    cur_boot = HOST.boot_session_uuid() if boot_uuid is None else boot_uuid
    # liveness delta (REVIEW_IMPLEMENTATION_MBS308_DELTA_R3 s3): the recorded process is computing unless it is
    # positively DEAD (HOST.identity_state); a failed `ps` or boot-UUID reading (UNKNOWN) is never evidence of death
    if _not_dead(jrec.get("process"), cur_boot, None):
        return {"state": "CONSUMED_COMPUTING", "why": why + ["PROCESS_NOT_PROVABLY_DEAD"], **info}
    why.append("PROCESS_DEAD" if jrec.get("boot_uuid") == cur_boot else "BOOT_UUID_CHANGED")
    # RC2 / DR2: the platform of the marker attempt, recorded in the journal, must be the platform now; a mismatch is
    # the frozen terminal rule (close-indeterminate), NEVER a mixed-platform resume
    if jrec.get("platform_mismatch") or jrec.get("platform") != platform:
        return {"state": "CONSUMED_UNRECORDED", "why": why + ["PLATFORM_PIN_MISMATCH"], **info}
    # checkpoints permit? (the tree listing only; content is never read here)
    jt = jrec.get("ckpt_tree")
    if jt:
        ref_tree = st.rev(CKPT_REF)
        have = st.ls_tree(ref_tree) if ref_tree else None
        want = st.ls_tree(jt)
        if have is None or want is None or any(have.get(n) != o for n, o in want.items()):
            return {"state": "CONSUMED_UNRECORDED", "why": why + ["CKPT_TREE_INCONSISTENT"], **info}
    fails = jrec.get("ckpt_failures") or {}
    if any(int(v) >= CKPT_FAIL_LIMIT for v in fails.values()):
        return {"state": "CONSUMED_UNRECORDED", "why": why + ["CKPT_CONSECUTIVE_FAILURES"], **info}
    if int(jrec.get("attempt") or 1) >= 1 + MAX_RESUMES:
        return {"state": "CONSUMED_UNRECORDED", "why": why + ["RESUME_BUDGET_EXHAUSTED"], **info}
    try:           # the marker time; an ARMING journal (death right after the marker) carries the intent time
        t_marker = parse_utc(jrec.get("marker_utc") or jrec["intent_utc"])
    except (KeyError, TypeError, ValueError):
        return {"state": "CONSUMED_UNRECORDED", "why": why + ["NO_MARKER_TIME"], **info}
    if (time.time() if now is None else now) - t_marker > DEADLINE_S:
        return {"state": "CONSUMED_UNRECORDED", "why": why + ["DEADLINE_PASSED"], **info}
    return {"state": "CONSUMED_INTERRUPTED", "why": why, **info}


# ------------------------------------------------------------------ the checkpointing pool (section 4) and GC-10
# MB r1's stage1() is kept TEXT-IDENTICAL: it names `ProcessPoolExecutor` and `wait`, which the MB-S driver binds to
# CheckpointingPool and checkpointing_wait. With no context (CK is None) they behave exactly as the originals plus the
# per-job peak-RSS record and the memory watchdog; with a context they serve verified checkpoints as already-completed
# futures (never recomputed) and write a checkpoint for every job that completes.
from concurrent.futures import ALL_COMPLETED, Future  # noqa: E402
from concurrent.futures import ProcessPoolExecutor as _PPE  # noqa: E402
from concurrent.futures import wait as _wait  # noqa: E402


class Ctx:
    """One evaluation attempt's lifecycle context (value-free counters; the records live only in memory and in the
    checkpoint blobs)."""

    def __init__(self, checkpointer: Checkpointer | None = None, verified: dict | None = None,
                 mem_cap_bytes: int | None = None, mem_poll_s: float = 2.0):
        self.checkpointer, self.verified = checkpointer, dict(verified or {})
        self.mem_cap, self.mem_poll_s = mem_cap_bytes, mem_poll_s
        self.served, self.submitted, self.ckpt_write_failures = [], [], []
        self.job_maxrss, self.worker_peak_rss, self.mem_events = {}, {}, []

    def summary(self) -> dict:
        kinds: dict = {}
        for name, rss in self.job_maxrss.items():
            k = name.split(".", 1)[0]
            kinds[k] = max(kinds.get(k, 0), rss)
        return {"jobs_served_from_checkpoints": len(self.served), "jobs_computed": len(self.submitted),
                "served": sorted(ckpt_name(k) for k in self.served),
                "checkpoints_written": 0 if self.checkpointer is None else self.checkpointer.written,
                "checkpoint_write_failures": list(self.ckpt_write_failures),
                "job_maxrss_bytes": dict(sorted(self.job_maxrss.items())), "peak_rss_bytes_by_kind": kinds,
                "memory_watchdog": {"cap_bytes": self.mem_cap, "events": list(self.mem_events),
                                    "worker_peak_rss_bytes": max(self.worker_peak_rss.values(), default=None)}}


CK: Ctx | None = None


def run_measured(fn, *args):
    """Runs in the worker: the unchanged job function, then the worker's peak RSS (bytes on macOS)."""
    import resource
    out = fn(*args)
    return {"__mbs308__": True, "out": out, "maxrss": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def worker_init_wrapper(parent_pid, orig_init, orig_args):
    """Runs in the worker before the unchanged initializer: a parent-death watch (a worker whose driver died exits
    within a second instead of computing for nobody). The parent pid is passed explicitly: a worker that starts after
    its driver was killed (its PPID is already 1) must exit too -- it would otherwise block forever on the call queue,
    whose pipe it holds both ends of."""
    if os.getppid() != parent_pid:
        os._exit(70)

    def watch():
        while True:
            time.sleep(1.0)
            if os.getppid() != parent_pid:
                os._exit(70)
    threading.Thread(target=watch, name="mbs308-parent-watch", daemon=True).start()
    if orig_init is not None:
        orig_init(*orig_args)


class _MemWatch:
    """GC-10: polls every worker's RSS; a worker above the cap is killed (SIGKILL) and the kill is recorded; the pool
    then breaks and the attempt fails (an execution failure, INDETERMINATE after the marker; never a silent drop).

    It also RELEASES A BROKEN POOL: the workers inherit the driver's SIG_IGN for SIGTERM (and MB r1's _worker_init
    ignores it explicitly), so concurrent.futures' own terminate_broken (SIGTERM, then join while holding the
    executor's shutdown lock) would wait forever for a live worker, and the driver would hang until EVAL_CAP. When the
    pool is marked broken, every remaining worker is SIGKILLed here and the kill is recorded."""

    def __init__(self, pool, ctx):
        self.pool, self.ctx = pool, ctx
        self.poll_s = ctx.mem_poll_s if ctx is not None else 2.0
        self.events = ctx.mem_events if ctx is not None else []
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._loop, name="mbs308-memwatch", daemon=True)

    def _release_broken(self) -> None:
        if not getattr(self.pool, "_broken", False):
            return
        try:
            procs = list((getattr(self.pool, "_processes", {}) or {}).items())
        except RuntimeError:
            return
        for pid, proc in procs:
            if proc.exitcode is None:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                    self.events.append({"utc": utc(), "event": "broken_pool_worker_killed", "worker_pid": int(pid)})
                except OSError:
                    pass

    def _loop(self) -> None:
        while not self._stop.wait(self.poll_s):
            self._release_broken()
            if self.ctx is None:
                continue
            try:
                pids = [int(p) for p in list(getattr(self.pool, "_processes", {}) or {})]
            except (RuntimeError, TypeError, ValueError):
                continue
            if not pids:
                continue
            p = subprocess.run(["/bin/ps", "-o", "pid=,rss=", "-p", ",".join(map(str, pids))], capture_output=True,
                               text=True, env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"}, stdin=subprocess.DEVNULL)
            for ln in p.stdout.splitlines():
                parts = ln.split()
                if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                    continue
                pid, rss = int(parts[0]), int(parts[1]) * 1024
                self.ctx.worker_peak_rss[pid] = max(self.ctx.worker_peak_rss.get(pid, 0), rss)
                if self.ctx.mem_cap is not None and rss > self.ctx.mem_cap:
                    try:
                        os.kill(pid, signal.SIGKILL)
                        killed = True
                    except OSError:
                        killed = False
                    self.ctx.mem_events.append({"utc": utc(), "worker_pid": pid, "rss_bytes": rss,
                                                "cap_bytes": self.ctx.mem_cap, "killed": killed})

    def start(self) -> "_MemWatch":
        self._t.start()
        return self

    def stop(self) -> None:
        self._stop.set()


class CheckpointingPool(_PPE):
    def __init__(self, max_workers=None, mp_context=None, initializer=None, initargs=(), *, max_tasks_per_child=None):
        super().__init__(max_workers=max_workers, mp_context=mp_context, initializer=worker_init_wrapper,
                         initargs=(os.getpid(), initializer, tuple(initargs)), max_tasks_per_child=max_tasks_per_child)
        self._mbs308_ctx = CK
        self._mbs308_watch = _MemWatch(self, CK).start()

    def submit(self, fn, /, *args, **kwargs):
        ctx = self._mbs308_ctx
        key = (args[0], args[1]["index"], args[2])
        outer = Future()
        outer._mbs308_key = key
        if ctx is not None and key in ctx.verified:
            outer._mbs308_from_ckpt = True
            ctx.served.append(key)
            outer.set_result(ctx.verified[key])
            return outer
        outer._mbs308_from_ckpt = False
        if ctx is not None:
            ctx.submitted.append(key)
        inner = super().submit(run_measured, fn, *args, **kwargs)

        def relay(f):
            if f.cancelled():
                outer.cancel()
                return
            exc = f.exception()
            if exc is not None:
                outer.set_exception(exc)
                return
            r = f.result()
            if ctx is not None:
                ctx.job_maxrss[ckpt_name(key)] = r["maxrss"]
            outer.set_result(r["out"])
        inner.add_done_callback(relay)
        return outer

    def shutdown(self, wait=True, *, cancel_futures=False):
        try:                    # the watch keeps running during the shutdown: it may have to release a broken pool
            super().shutdown(wait=wait, cancel_futures=cancel_futures)
        finally:
            self._mbs308_watch.stop()
        if not wait:            # stage1's own p.terminate() cannot stop workers that ignore SIGTERM: SIGKILL the rest,
            try:                # so an abandoned pool never keeps computing, and interpreter exit never waits for it
                procs = list((getattr(self, "_processes", {}) or {}).items())
            except RuntimeError:
                procs = []
            for pid, proc in procs:
                if proc.exitcode is None:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                        self._mbs308_watch.events.append({"utc": utc(), "event": "shutdown_worker_killed",
                                                          "worker_pid": int(pid)})
                    except OSError:
                        pass


def checkpointing_wait(fs, timeout=None, return_when=ALL_COMPLETED):
    """concurrent.futures.wait, then (main thread) one durable checkpoint per newly completed computed job."""
    res = _wait(fs, timeout=timeout, return_when=return_when)
    ctx = CK
    if ctx is not None and ctx.checkpointer is not None:
        for f in res.done:
            if getattr(f, "_mbs308_from_ckpt", True) or getattr(f, "_mbs308_ckpt_done", False):
                continue
            f._mbs308_ckpt_done = True
            if f.cancelled() or f.exception() is not None:
                continue
            try:
                ctx.checkpointer.write(f._mbs308_key, f.result())
            except JournalConflict:
                raise LostOwnership()
            except Exception as exc:                                # noqa: BLE001 (lifecycle only; recorded)
                ctx.ckpt_write_failures.append(f"{ckpt_name(f._mbs308_key)}: {type(exc).__name__}")
    return res
