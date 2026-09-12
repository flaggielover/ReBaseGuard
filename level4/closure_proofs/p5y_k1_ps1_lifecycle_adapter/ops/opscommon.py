"""Shared OPERATIONAL primitives for the P5Y K1 SR production lifecycle.

This module implements NO science, NO scheduling and NO accounting rule of its
own. It provides: the hash-bound operational contract, fsync'd atomic I/O, host
identity (boot id / boot time / process start time), exact CPU sources and the
runtime directory that lives OUTSIDE every git source tree.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

OPS_NS = Path(__file__).resolve().parents[1]
CONTRACT_PATH = OPS_NS / "config/OPERATIONAL_CONTRACT.json"
CONTRACT_HASH_PATH = OPS_NS / "config/OPERATIONAL_CONTRACT_HASH"
PARENT_NS_REL = "level4/closure_proofs/p5y_k1_ps1_production"
CONTRACT_SCHEMA = "rebaseguard.p5y.k1.sr.production.operational-contract.v1"
JOURNAL_CPU_MESSAGE_ID = "ae8f7b866b0347b9af31fe1c80b127c0"


class OpsRefusal(RuntimeError):
    """An operational gate refused. Always fail closed."""


# ------------------------------------------------------------------ bytes/IO
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p) -> str:
    return sha256_bytes(Path(p).read_bytes())


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def fsync_dir(path) -> None:
    fd = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(path, data: bytes, *, tmp=None) -> None:
    """temp -> write -> fsync -> rename -> fsync(dir). A crash leaves old or new."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tmp) if tmp else path.parent / f".tmp-ops-{path.name}-{os.getpid()}"
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        view = memoryview(data)
        while view:
            n = os.write(fd, view)
            view = view[n:]
        os.fsync(fd)
    except BaseException:
        os.close(fd)
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise
    os.close(fd)
    os.replace(tmp, path)
    fsync_dir(path.parent)


def write_json_atomic(path, obj, *, tmp=None) -> None:
    atomic_write(path, (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode(), tmp=tmp)


def read_json_strict(path):
    """Parse a JSON document. Partial/corrupt content REFUSES; never defaults."""
    raw = Path(path).read_bytes()
    try:
        return json.loads(raw)
    except Exception as exc:                                      # noqa: BLE001
        raise OpsRefusal(f"corrupt/partial JSON at {path}: {type(exc).__name__}: {exc}") from exc


# ------------------------------------------------------------------ contract
def load_contract(path=None) -> dict:
    """The PRODUCTION contract is hash-bound; any other file must declare itself a
    SYNTHETIC_CONTROL contract and may never point at a production path."""
    path = Path(path) if path else CONTRACT_PATH
    raw = path.read_bytes()
    c = json.loads(raw)
    if c.get("schema") != CONTRACT_SCHEMA:
        raise OpsRefusal(f"not an operational contract: {c.get('schema')!r}")
    if path.resolve() == CONTRACT_PATH.resolve():
        want = CONTRACT_HASH_PATH.read_text().strip()
        if sha256_bytes(raw) != want:
            raise OpsRefusal(f"operational contract sha256 {sha256_bytes(raw)} != frozen {want}")
        if c.get("mode") != "PRODUCTION":
            raise OpsRefusal("the frozen contract must be mode PRODUCTION")
    else:
        if c.get("mode") != "SYNTHETIC_CONTROL":
            raise OpsRefusal("a non-frozen contract must be mode SYNTHETIC_CONTROL")
        prod = json.loads(CONTRACT_PATH.read_text())
        forbidden = set()
        for spec in prod["hosts"].values():
            forbidden |= {str(Path(spec["production_root"]).resolve()),
                          str(Path(spec["runtime_dir"]).resolve())}
        for role, spec in c["hosts"].items():
            for k in ("production_root", "runtime_dir"):
                if str(Path(spec[k]).resolve()) in forbidden:
                    raise OpsRefusal(
                        f"SYNTHETIC_CONTROL contract points {role}.{k} at a PRODUCTION path")
    c["_path"] = str(path)
    c["_sha256"] = sha256_bytes(raw)
    return c


def host_spec(contract, role) -> dict:
    if role not in contract["hosts"]:
        raise OpsRefusal(f"role {role!r} not in the operational contract")
    return contract["hosts"][role]


def prod_ns(spec) -> Path:
    return Path(spec["production_root"]) / PARENT_NS_REL


def ledger_path(spec) -> Path:
    return prod_ns(spec) / "production/PRODUCTION_LEDGER.json"


def frozen_accounting(spec):
    """Import ONLY the frozen accounting primitives (no science, no scheduler)."""
    d = str(prod_ns(spec) / "driver")
    if d not in sys.path:
        sys.path.insert(0, d)
    import multihost as M                                         # noqa: E402
    import global_budget as GB                                    # noqa: E402
    return M, GB


def frozen_budget(spec, contract):
    M, GB = frozen_accounting(spec)
    return GB.GlobalBudget(ledger_path(spec), M.validate_governed_cost, M.gate_global_cap,
                           overhead_cpu_h=contract["parent"]["governed_overhead_cpu_h"],
                           cap_cpu_h=M.validate_governed_cap(M.GLOBAL_CPU_CAP))


# ------------------------------------------------------------ host identity
def _synthetic(contract) -> dict:
    return (contract or {}).get("synthetic") or {}


def boot_id(contract=None) -> str:
    f = _synthetic(contract).get("boot_id_file")
    if f and Path(f).exists():
        return Path(f).read_text().strip()
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip()


def boot_time(contract=None) -> float:
    f = _synthetic(contract).get("boot_time_file")
    if f and Path(f).exists():
        return float(Path(f).read_text().strip())
    for line in Path("/proc/stat").read_text().splitlines():
        if line.startswith("btime "):
            return float(line.split()[1])
    raise OpsRefusal("cannot read btime")


def _stat_fields(pid):
    try:
        raw = Path(f"/proc/{pid}/stat").read_text()
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return None
    rest = raw[raw.rindex(")") + 2:].split()
    return rest                      # rest[0] = state (field 3)


def pid_alive(pid: int) -> bool:
    f = _stat_fields(pid)
    return f is not None and f[0] not in ("Z", "X")


def proc_start_wall(pid, contract=None):
    f = _stat_fields(pid)
    if f is None:
        return None
    ticks = int(f[19])                                   # field 22 starttime
    return boot_time(None) + ticks / os.sysconf("SC_CLK_TCK")


def proc_cpu_usec(pid, include_children=True) -> int:
    f = _stat_fields(pid)
    if f is None:
        return 0
    hz = os.sysconf("SC_CLK_TCK")
    t = int(f[11]) + int(f[12]) + ((int(f[13]) + int(f[14])) if include_children else 0)
    return int(t * 1_000_000 // hz)


def children_of(pid, include_zombies=False) -> list:
    out = []
    for d in Path("/proc").iterdir():
        if d.name.isdigit():
            f = _stat_fields(int(d.name))
            if f is not None and int(f[1]) == pid and (include_zombies or f[0] not in ("Z", "X")):
                out.append(int(d.name))        # a zombie is a DEAD (unjoined) process
    return sorted(out)


def descendants_of(pid, include_zombies=False) -> list:
    seen, frontier = [], [pid]
    while frontier:
        nxt = []
        for p in frontier:
            for c in children_of(p, include_zombies):
                if c not in seen:
                    seen.append(c)
                    nxt.append(c)
        frontier = nxt
    return seen


def online_cpus() -> int:
    return os.cpu_count() or 1


def free_gib(path) -> float:
    return shutil.disk_usage(str(path)).free / 2 ** 30


# --------------------------------------------------------------- CPU sources
class CgroupCPU:
    """EXACT CPU of every process in this service's own cgroup (systemd unit)."""
    kind = "CGROUP"

    def __init__(self, unit: str):
        line = Path("/proc/self/cgroup").read_text().strip().splitlines()[-1]
        cg = line.split("::", 1)[1] if "::" in line else line.split(":")[-1]
        if not cg.endswith("/" + unit):
            raise OpsRefusal(f"not running in the dedicated unit cgroup {unit} (cgroup {cg})")
        self.path = Path("/sys/fs/cgroup" + cg)

    def usage_usec(self) -> int:
        for line in (self.path / "cpu.stat").read_text().splitlines():
            if line.startswith("usage_usec "):
                return int(line.split()[1])
        raise OpsRefusal("cpu.stat has no usage_usec")

    def procs(self) -> list:
        return [int(x) for x in (self.path / "cgroup.procs").read_text().split()]


class ProcTreeCPU:
    """SYNTHETIC-HARNESS ONLY (no dedicated cgroup): self + reaped children +
    every live descendant. The supervisor is a child subreaper, so orphaned
    grandchildren are reparented to it and are still counted when reaped."""
    kind = "PROCTREE"

    def usage_usec(self) -> int:
        s = resource.getrusage(resource.RUSAGE_SELF)
        c = resource.getrusage(resource.RUSAGE_CHILDREN)
        total = int((s.ru_utime + s.ru_stime + c.ru_utime + c.ru_stime) * 1_000_000)
        # unreaped zombies still carry their times in /proc/<pid>/stat and are not yet in
        # any parent's cutime, so they are counted here exactly once
        return total + sum(proc_cpu_usec(p) for p in descendants_of(os.getpid(), True))

    def procs(self) -> list:
        return [os.getpid()] + descendants_of(os.getpid(), True)


# ----------------------------------------------------------------- systemd
def unit_state(unit: str) -> tuple:
    r = subprocess.run(["systemctl", "show", "-p", "LoadState", "-p", "ActiveState", unit],
                       capture_output=True, text=True, timeout=30)
    kv = dict(l.split("=", 1) for l in r.stdout.splitlines() if "=" in l)
    return kv.get("LoadState", ""), kv.get("ActiveState", "")


def journal_cpu_usage_usec(unit: str, invocation_id: str):
    """systemd's own persisted exact CPU record for one unit invocation, or None."""
    try:
        r = subprocess.run(["journalctl", "-u", unit, "-o", "json", "--no-pager"],
                           capture_output=True, text=True, timeout=60)
    except Exception:                                             # noqa: BLE001
        return None
    for line in r.stdout.splitlines():
        try:
            d = json.loads(line)
        except Exception:                                         # noqa: BLE001
            continue
        if d.get("MESSAGE_ID") == JOURNAL_CPU_MESSAGE_ID and \
                d.get("INVOCATION_ID") == invocation_id and "CPU_USAGE_NSEC" in d:
            return int(d["CPU_USAGE_NSEC"]) // 1000
    return None


# ------------------------------------------------------------ runtime dir
RUN_ID_RE = re.compile(r"^[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}$")


def new_run_id() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + os.urandom(4).hex()


class RuntimeDir:
    """Mutable operational state, OUTSIDE every git source tree."""

    def __init__(self, spec):
        self.root = Path(spec["runtime_dir"])
        for src in (spec["production_root"], spec.get("ops_root", spec["production_root"])):
            s = str(Path(src).resolve())
            if str(self.root.resolve()).startswith(s + os.sep) or str(self.root.resolve()) == s:
                raise OpsRefusal(f"runtime dir {self.root} lies inside source tree {s}")

    def ensure(self):
        for d in ("runs", "logs", "quarantine", "handoff"):
            (self.root / d).mkdir(parents=True, exist_ok=True)
        return self

    def run_record(self, run_id) -> Path:
        if not RUN_ID_RE.match(run_id):
            raise OpsRefusal(f"malformed run id {run_id!r}")
        return self.root / "runs" / f"{run_id}.json"

    def log(self, run_id) -> Path:
        return self.root / "logs" / f"{run_id}.log"

    @property
    def continuity(self) -> Path:
        return self.root / "continuity.jsonl"

    @property
    def lock(self) -> Path:
        return self.root / "campaign.lock"

    @property
    def owner(self) -> Path:
        return self.root / "campaign.owner.json"
