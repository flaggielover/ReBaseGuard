"""Shared helpers for the CUSUM Aux5 production checkpoint. NON-CERTIFYING.

The certifier (Aux5 `qualify5.py`) never imports anything from this namespace: it always runs as its own
`env -i` interpreter. Every write that carries authority is atomic (a temporary file in the same directory,
fsync, `os.replace`, fsync of the directory), and every refusal is a `Refusal` carrying a stable code.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import re
import signal
import socket
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
CLOSURE = ROOT / "level4/closure_proofs"
AUX5_NS = CLOSURE / "p5y_k1_cusum_aux5_successor"
AUX4_NS = CLOSURE / "p5y_k1_cusum_aux4_fullcover"
SPEC_NS = CLOSURE / "p5y_k1_cover_ledger_successor"
K4_NS = CLOSURE / "p5y_k2k5_postk1_audit"

CHECKPOINT = NS / "config/PRODUCTION_CHECKPOINT.json"
CHECKPOINT_HASH = NS / "config/PRODUCTION_CHECKPOINT_HASH"
FREEZE_RECORD = NS / "config/FREEZE_RECORD.json"

LINUX = sys.platform.startswith("linux")
CLK_TCK = os.sysconf("SC_CLK_TCK")
_LIBC = ctypes.CDLL(None, use_errno=True) if LINUX else None
_PR_SET_PDEATHSIG, _PR_SET_CHILD_SUBREAPER = 1, 36

_RATIONAL = re.compile(r"-?[0-9]+(/[1-9][0-9]*)?")
HEX64 = re.compile(r"[0-9a-f]{64}")


class Refusal(RuntimeError):
    """Fail-closed refusal with a stable code."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code, self.detail = code, detail


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


def is_rational_str(value) -> bool:
    return isinstance(value, str) and _RATIONAL.fullmatch(value) is not None


# ------------------------------------------------------------------ durable writes
def fsync_dir(directory) -> None:
    fd = os.open(str(directory), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write_bytes(path, data: bytes) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".{path.name}.tmp-{os.getpid()}"
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    fsync_dir(path.parent)


def atomic_write_json(path, obj) -> None:
    atomic_write_bytes(path, (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode())


def append_durable(path, line: str) -> None:
    """Append one line; a final line a crash left without its newline is terminated first."""
    path = Path(path)
    prefix = ""
    if path.exists() and path.stat().st_size:
        with open(path, "rb") as fh:
            fh.seek(-1, os.SEEK_END)
            prefix = "" if fh.read(1) == b"\n" else "\n"
    with open(path, "a") as fh:
        fh.write(prefix + line + "\n")
        fh.flush()
        os.fsync(fh.fileno())


# ------------------------------------------------------------------ processes (Linux; inert elsewhere)
def boot_id() -> str:
    p = Path("/proc/sys/kernel/random/boot_id")
    return p.read_text().strip() if p.exists() else "NO_BOOT_ID"


def boot_time() -> float:
    try:
        for line in Path("/proc/stat").read_text().splitlines():
            if line.startswith("btime "):
                return float(line.split()[1])
    except OSError:
        pass
    return 0.0


def proc_stat(pid) -> dict | None:
    try:
        raw = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    fields = raw[raw.rindex(")") + 2:].split()          # proc(5) fields 3, 4, ...
    return {"state": fields[0], "utime": int(fields[11]), "stime": int(fields[12]),
            "starttime": int(fields[19])}


def pid_alive(pid, start_ticks=None) -> bool:
    st = proc_stat(pid) if pid else None
    if st is None or st["state"] in ("Z", "X"):
        return False
    return start_ticks is None or st["starttime"] == start_ticks


def proc_cpu_usec(pid, start_ticks) -> int | None:
    """CPU of a live process, rounded UP by one clock tick (an upper bound)."""
    st = proc_stat(pid)
    if st is None or st["starttime"] != start_ticks:
        return None
    return (st["utime"] + st["stime"] + 1) * 1_000_000 // CLK_TCK


def rusage_usec(ru) -> int:
    return int(round((ru.ru_utime + ru.ru_stime) * 1_000_000))


def _prctl(option: int, arg: int) -> None:
    if _LIBC is not None and _LIBC.prctl(option, arg, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), f"prctl({option}, {arg}) failed")


def pdeathsig_preexec(parent_pid: int):
    """preexec_fn: the child is SIGKILLed when its supervisor dies (preserved across the env/taskset execs)."""
    def pre():
        _prctl(_PR_SET_PDEATHSIG, signal.SIGKILL)
        if os.getppid() != parent_pid:
            os._exit(125)
    return pre


def set_child_subreaper() -> None:
    _prctl(_PR_SET_CHILD_SUBREAPER, 1)


def exit_facts(status: int) -> dict:
    exited = os.WIFEXITED(status)
    return {"exited": exited, "exit_code": os.WEXITSTATUS(status) if exited else None,
            "signal": os.WTERMSIG(status) if os.WIFSIGNALED(status) else None}


def processes_matching(markers) -> list[dict]:
    out, me = [], os.getpid()
    for d in Path("/proc").glob("[0-9]*"):
        if int(d.name) == me:
            continue
        try:
            cmd = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
        except OSError:
            continue
        if cmd and any(m in cmd for m in markers):
            out.append({"pid": int(d.name), "cmdline": cmd[:240]})
    return out


# ------------------------------------------------------------------ host identity
LIBC = Path("/usr/lib/x86_64-linux-gnu/libc.so.6")
BOUND_HOST_FACTS = ("host_name", "machine_id_sha256", "cpu_model", "logical_cpus", "physical_cores",
                    "smt_groups", "kernel_release", "libc_path", "libc_sha256", "glibc_package_version")
# re-checked before every admission: no subprocess, a few milliseconds
GUARD_HOST_FACTS = tuple(k for k in BOUND_HOST_FACTS if k != "glibc_package_version")


def _run(argv) -> str | None:
    try:
        out = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def host_facts(*, with_package: bool = True) -> dict:
    facts = {"host_name": socket.gethostname(), "kernel_release": os.uname().release}
    mid = Path("/etc/machine-id")
    facts["machine_id_sha256"] = sha256_file(mid) if mid.exists() else None
    facts["cpu_model"] = None
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text().splitlines():
            if line.startswith("model name"):
                facts["cpu_model"] = line.split(":", 1)[1].strip()
                break
    groups: dict = {}
    for d in sorted(Path("/sys/devices/system/cpu").glob("cpu[0-9]*"), key=lambda d: int(d.name[3:])):
        core, pkg = d / "topology/core_id", d / "topology/physical_package_id"
        if core.exists() and pkg.exists():
            groups.setdefault((int(pkg.read_text()), int(core.read_text())), []).append(int(d.name[3:]))
    facts["smt_groups"] = [groups[k] for k in sorted(groups)]
    facts["physical_cores"] = len(groups)
    facts["logical_cpus"] = sum(len(v) for v in groups.values())
    facts["libc_path"] = str(LIBC) if LIBC.exists() else None
    facts["libc_sha256"] = sha256_file(LIBC) if LIBC.exists() else None
    if with_package:
        facts["glibc_package_version"] = _run(["dpkg-query", "-W", "-f=${Version}", "libc6"])
    return facts


def host_problems(expected: dict, live: dict, keys) -> list[str]:
    return [f"host {k}: live {live.get(k)!r} != bound {expected.get(k)!r}"
            for k in keys if live.get(k) != expected.get(k)]
