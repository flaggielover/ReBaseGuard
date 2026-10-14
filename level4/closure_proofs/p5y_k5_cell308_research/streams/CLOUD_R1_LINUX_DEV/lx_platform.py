"""Cell-308 new-host route (Claude Cloud, r1) -- DEVELOPMENT-ONLY Linux platform layer.

STATUS: DEV_ONLY · UNREVIEWED · NOT FROZEN · NOT A CAMPAIGN NAMESPACE · NOT USABLE FOR ANY DESIGNATED SERIES,
QUALIFICATION, FREEZE, GRANT OR TARGET STEP. Nothing in the historical candidate (142d97a9) imports or is changed by
this file. It is a target-free development artefact written under the owner's 2026-10-14 authorization
(governance/new_host_route_cloud_r1/USER_AUTHORIZATION_20261014.md) to make the PROPOSED route amendment
(PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1.md) concrete and testable. It contains no science, no cell, no drift and no
threshold of any R-rule.

Design rules (all fail-closed):

* Every reader returns ``None`` when its source is absent or unreadable. ``None`` is UNKNOWN. UNKNOWN never passes a
  gate and never proves death.
* Where the accepted rule text names a macOS quantity that has no Linux identity (R-FREE's ``free_memory_bytes``,
  R-MEM step 5's ``hw.memsize - W_idle``, the thermal-pressure level, low-power mode, the memory-pressure level,
  R-ALLOW (b)'s SIP path classes), this module exposes the RAW Linux readings only and the gate evaluates to
  ``OPEN_DECISION``. ``OPEN_DECISION`` never passes. No Linux metric is substituted for a macOS one here; choosing a
  mapping is a rule-semantics decision for an independent route reviewer and the owner.
* Process identity keeps the accepted R2 / N-2 semantics of ``mbs308_host.identity_state``: DEAD only on POSITIVE
  evidence; a failed reading is UNKNOWN; a field never recorded is never compared.
* Gates are tri-state-plus: PASS, FAIL, UNKNOWN, OPEN_DECISION. ``preflight`` passes only if every gate is PASS.

Every function that reads the host accepts injected text / paths for the tests (``tests/test_lx_platform.py``).
Stdlib only; Python >= 3.11.
"""
from __future__ import annotations

import hashlib
import os
import platform as _platform
import re
import subprocess
import sys
import time
from pathlib import Path

PASS, FAIL, UNKNOWN, OPEN_DECISION = "PASS", "FAIL", "UNKNOWN", "OPEN_DECISION"
ALIVE, DEAD = "ALIVE", "DEAD"
AC = "AC"                                       # Linux spelling; never compared with mbs308_host.AC ("AC Power")
UNLIMITED_CGROUP_V1 = 2 ** 62                   # memory.limit_in_bytes at or above this is "no limit" (v1 sentinel)
SLEEP_GAP_TOL_NS = 2_000_000_000                # same tolerance as mbs308_host channel K
MAX_SAMPLE_GAP_S = 180                          # same as mbs308_host
MIN_FREE_DISK = 2 * 1024 ** 3                   # same as mbs308_host (section 6)
CAMPAIGN_UNIT_PREFIX = "rebaseguard-mbs308-"    # PROPOSED systemd unit-name prefix (amendment item L-LAUNCH)

# The open rule-semantics decisions this module refuses to make (amendment section 4). Each gate that depends on one
# evaluates to OPEN_DECISION with the decision's id.
OPEN_DECISIONS = {
    "D-MEM-FREE": "R-FREE quantity on Linux (macOS vm_stat free+inactive+speculative+purgeable has no Linux identity)",
    "D-MEM-WIRED": "R-MEM step 5 'hw.memsize - W_idle' on Linux under a cgroup limit",
    "D-MEM-PRESSURE": "memory_pressure_normal (macOS kern.memorystatus_vm_pressure_level == 1) on Linux",
    "D-THERMAL": "thermal_pressure_0 (macOS thermal-pressure level 0) on Linux / on hosts with no thermal zones",
    "D-LPM": "lowpowermode_0 (macOS pmset lowpowermode) on Linux",
    "D-POWER-ABSENT": "AC-power gate on hosts that expose no power supply (VMs, servers)",
    "D-ALLOW-PATHS": "R-ALLOW (b) SIP path classes on Linux",
    "D-EXCL-WINDOW": "R-EXCL-PCT reading on Linux (ps %cpu is a lifetime average on Linux, a decaying average on macOS)",
    "D-PAUSE": "VM pause / snapshot detection channel for hosts whose guest clocks may not show a pause",
    "D-HOST-LIFETIME": "provider lifetime / reclaim / exclusivity guarantees (an attestation, not a reading)",
}


def _read(path, binary: bool = False):
    try:
        return Path(path).read_bytes() if binary else Path(path).read_text()
    except (OSError, UnicodeDecodeError):
        return None


# ====================================================================== boot identity
_BOOT_ID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def boot_id(text: str | None = None) -> str | None:
    """/proc/sys/kernel/random/boot_id (changes on every kernel boot). Malformed or unreadable: None.
    NOTE (amendment L-BOOT): a VM pause / snapshot-restore need not change it; it detects reboots only."""
    text = _read("/proc/sys/kernel/random/boot_id") if text is None else text
    t = (text or "").strip()
    return t if _BOOT_ID.match(t) else None


# ====================================================================== process identity (R2 / N-2 semantics)
def proc_stat(pid: int, text: str | None = None) -> dict | None:
    """Parse /proc/<pid>/stat. ``comm`` may contain spaces and parentheses, so the fields after it are split from the
    LAST ')'. Returns state, ppid, utime, stime (clock ticks) and starttime (clock ticks since boot); None if absent,
    unreadable or malformed."""
    text = _read(f"/proc/{int(pid)}/stat") if text is None else text
    if not text:
        return None
    lp, rp = text.find("("), text.rfind(")")
    if lp < 0 or rp < lp:
        return None
    try:
        head_pid = int(text[:lp].strip())
        rest = text[rp + 1:].split()
        # rest[0] = field 3 (state); field n is rest[n - 3]
        return {"pid": head_pid, "comm": text[lp + 1:rp], "state": rest[0], "ppid": int(rest[1]),
                "utime": int(rest[11]), "stime": int(rest[12]), "starttime": int(rest[19])}
    except (ValueError, IndexError):
        return None


def cmdline_sha256(pid: int, data: bytes | None = None) -> str | None:
    """sha256 of the raw /proc/<pid>/cmdline bytes. Empty (kernel thread, zombie, exiting process) or unreadable:
    None -- a FAILED reading, never a command (the Linux analogue of mbs308_host O-4)."""
    data = _read(f"/proc/{int(pid)}/cmdline", binary=True) if data is None else data
    return hashlib.sha256(data).hexdigest() if data else None


def identity(pid: int | None = None) -> dict:
    """(pid, starttime ticks, boot_id, cmdline sha256): the Linux identity for pidfiles, locks and the journal."""
    pid = os.getpid() if pid is None else int(pid)
    st = proc_stat(pid)
    return {"pid": pid, "starttime_ticks": None if st is None else st["starttime"], "boot_id": boot_id(),
            "cmdline_sha256": cmdline_sha256(pid)}


def _pid_exists(pid: int) -> bool | None:
    """True / False / None (unknown). ESRCH is positive evidence of absence; EPERM means it exists."""
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except (TypeError, ValueError, OSError):
        return None
    return True


def identity_state(ident, *, current_boot: str | None = None, exists=None, stat=None, cmd=None) -> str:
    """ALIVE / DEAD / UNKNOWN with mbs308_host.identity_state's accepted semantics (R2, N-2):

    DEAD only on POSITIVE evidence: the boot id changed; the pid does not exist (ESRCH); the pid's starttime or
    cmdline differs from a RECORDED value; or the process is a zombie / dead task (state Z or X -- PROPOSED reading
    L-ID-1: an exited, unreaped task is gone for identity purposes). UNKNOWN on any failed reading. A field that was
    never recorded is never compared; ALIVE needs every field recorded and matching.
    Injection (tests): ``current_boot`` (string; ``""`` = the reading failed), ``exists(pid)``, ``stat(pid)``,
    ``cmd(pid)``."""
    if not isinstance(ident, dict) or not ident.get("pid"):
        return UNKNOWN
    cur = boot_id() if current_boot is None else (current_boot or None)
    if cur is None:
        return UNKNOWN
    if ident.get("boot_id") and ident["boot_id"] != cur:
        return DEAD
    pid = ident["pid"]
    ex = (exists or _pid_exists)(pid)
    if ex is None:
        return UNKNOWN
    if ex is False:
        return DEAD
    st = (stat or proc_stat)(pid)
    if st is None:
        return UNKNOWN
    if st.get("state") in ("Z", "X"):
        return DEAD
    if ident.get("starttime_ticks") is not None and st["starttime"] != ident["starttime_ticks"]:
        return DEAD
    cs = (cmd or cmdline_sha256)(pid)
    if cs is None:
        return UNKNOWN
    if ident.get("cmdline_sha256") and cs != ident["cmdline_sha256"]:
        return DEAD
    complete = ident.get("boot_id") and ident.get("starttime_ticks") is not None and ident.get("cmdline_sha256")
    return ALIVE if complete else UNKNOWN


# ====================================================================== clocks, suspend and pause channels
def clocks() -> dict:
    """CLOCK_MONOTONIC stops during system suspend on Linux; CLOCK_BOOTTIME does not. CLOCK_REALTIME is wall time.
    (macOS: UPTIME_RAW / MONOTONIC_RAW play these roles in mbs308_host channel K.)"""
    return {"monotonic_ns": time.clock_gettime_ns(time.CLOCK_MONOTONIC),
            "boottime_ns": time.clock_gettime_ns(time.CLOCK_BOOTTIME),
            "realtime_ns": time.clock_gettime_ns(time.CLOCK_REALTIME), "epoch_s": int(time.time())}


def suspend_success_count(text: str | None = None) -> int | None:
    """/sys/power/suspend_stats/success (channel S'): absent on many VMs -> None."""
    text = _read("/sys/power/suspend_stats/success") if text is None else text
    t = (text or "").strip()
    return int(t) if t.isdigit() else None


def snapshot(*, power_root="/sys/class/power_supply", suspend_text: str | None = None) -> dict:
    return {"clocks": clocks(), "boot_id": boot_id(), "suspend_success": suspend_success_count(suspend_text),
            "power": power_source(power_root)}


def assess(start: dict, end: dict, samples, journal_suspend_events) -> dict:
    """Fail-closed interval assessment (the Linux counterpart of mbs308_host.assess; PROPOSED, amendment L-SLEEP).

    K'  Δboottime − Δmonotonic > tol: the system suspended (CONTAMINATED); < −tol: AMBIGUOUS.
    S'  /sys/power/suspend_stats/success changed (CONTAMINATED); absent at either end (AMBIGUOUS).
    L'  journal suspend entries in the interval (CONTAMINATED); ``None`` = journal unavailable (AMBIGUOUS).
    P   |Δrealtime − Δmonotonic| > tol: wall time diverged from monotonic time -- a possible VM pause or a clock step
        (AMBIGUOUS, never CLEAN; it cannot be CONTAMINATED because an NTP step looks the same). PROPOSED new channel,
        strictly additional: it can only remove CLEAN, never create it.
    boot  a boot_id change inside the interval: CONTAMINATED (a reboot).
    power every reading must be AC; any None is AMBIGUOUS.
    spacing samples at most MAX_SAMPLE_GAP_S apart.
    CLEAN only if every channel is available and none fires."""
    reasons = []
    seq = [start, *(samples if isinstance(samples, list) else []), end]
    try:
        c0, c1 = start["clocks"], end["clocks"]
        dm = c1["monotonic_ns"] - c0["monotonic_ns"]
        db = c1["boottime_ns"] - c0["boottime_ns"]
        dr = c1["realtime_ns"] - c0["realtime_ns"]
        if dm <= 0 or db <= 0:
            reasons.append("AMBIGUOUS: K' clocks not increasing")
        else:
            if db - dm > SLEEP_GAP_TOL_NS:
                reasons.append(f"CONTAMINATED: K' suspended {(db - dm) // 10 ** 9} s")
            elif db - dm < -SLEEP_GAP_TOL_NS:
                reasons.append("AMBIGUOUS: K' monotonic advanced more than boottime")
            if abs(dr - dm) > SLEEP_GAP_TOL_NS:
                reasons.append(f"AMBIGUOUS: P wall time diverged from monotonic by {(dr - dm) // 10 ** 6} ms")
    except (KeyError, TypeError):
        reasons.append("AMBIGUOUS: K'/P clocks absent")
    s0, s1 = (start or {}).get("suspend_success"), (end or {}).get("suspend_success")
    if not isinstance(s0, int) or not isinstance(s1, int):
        reasons.append("AMBIGUOUS: S' suspend_stats absent")
    elif s0 != s1:
        reasons.append("CONTAMINATED: S' suspend count changed")
    if not isinstance(journal_suspend_events, list):
        reasons.append("AMBIGUOUS: L' journal unavailable")
    elif journal_suspend_events:
        reasons.append(f"CONTAMINATED: L' {len(journal_suspend_events)} suspend entries")
    boots = [x.get("boot_id") if isinstance(x, dict) else None for x in seq]
    if any(b is None for b in boots):
        reasons.append("AMBIGUOUS: a boot_id reading is absent")
    elif len(set(boots)) > 1:
        reasons.append("CONTAMINATED: boot_id changed (reboot)")
    power = [x.get("power") if isinstance(x, dict) else None for x in seq]
    if any(p is None or p == "ABSENT" for p in power):
        reasons.append("AMBIGUOUS: a power reading is absent or unreadable (no supply exposed counts as absent)")
    elif any(p != AC for p in power):
        reasons.append("CONTAMINATED: a power reading is not AC")
    if not isinstance(samples, list):
        reasons.append("AMBIGUOUS: samples absent")
    try:
        ts = [x["clocks"]["monotonic_ns"] for x in seq]
        steps = [b - a for a, b in zip(ts, ts[1:])]
        if any(d < 0 for d in steps):
            reasons.append("AMBIGUOUS: samples out of order")
        elif not steps or max(steps) // 10 ** 9 > MAX_SAMPLE_GAP_S:
            reasons.append("AMBIGUOUS: samples do not cover the interval")
    except (KeyError, TypeError):
        reasons.append("AMBIGUOUS: a sample carries no clocks")
    status = "CONTAMINATED" if any(r.startswith("CONTAMINATED") for r in reasons) else \
        ("AMBIGUOUS" if reasons else "CLEAN")
    return {"status": status, "clean": status == "CLEAN", "reasons": reasons}


# ====================================================================== power, thermal
def power_source(root="/sys/class/power_supply") -> str | None:
    """"AC" iff at least one supply of type Mains reports online = 1 and no Battery reports status Discharging;
    "BATTERY" if a battery discharges; "NO_MAINS" if supplies exist but none is an online Mains; "ABSENT" if the
    class exposes no Mains / Battery supply at all (amendment D-POWER-ABSENT: on a VM or server the unchanged AC rule
    has no source, and this is never read as AC); None if a reading fails (UNKNOWN)."""
    try:
        entries = sorted(Path(root).iterdir())
    except OSError:
        return None
    mains_online, discharging, seen = False, False, 0
    for e in entries:
        typ = (_read(e / "type") or "").strip()
        if typ == "Mains":
            seen += 1
            on = (_read(e / "online") or "").strip()
            if on not in ("0", "1"):
                return None
            mains_online |= on == "1"
        elif typ == "Battery":
            seen += 1
            st = (_read(e / "status") or "").strip()
            if not st:
                return None
            discharging |= st == "Discharging"
    if not seen:
        return "ABSENT"
    if discharging:
        return "BATTERY"
    return AC if mains_online else "NO_MAINS"


def thermal_zones(root="/sys/class/thermal") -> list | None:
    """Raw zones: [{zone, type, temp_mC, trips: [{type, temp_mC}]}]. None if the class directory is unreadable;
    [] if it exists but exposes no zone. RAW ONLY: no 'thermal-pressure level' is derived (D-THERMAL)."""
    try:
        zs = sorted(p for p in Path(root).iterdir() if p.name.startswith("thermal_zone"))
    except OSError:
        return None
    out = []
    for z in zs:
        t = (_read(z / "temp") or "").strip()
        trips = []
        for tp in sorted(z.glob("trip_point_*_type")):
            k = tp.name[:-len("_type")]
            tv = (_read(z / f"{k}_temp") or "").strip()
            trips.append({"type": (_read(tp) or "").strip(), "temp_mC": int(tv) if tv.lstrip("-").isdigit() else None})
        out.append({"zone": z.name, "type": (_read(z / "type") or "").strip() or None,
                    "temp_mC": int(t) if t.lstrip("-").isdigit() else None, "trips": trips})
    return out


# ====================================================================== memory: RAW Linux quantities only
def meminfo(text: str | None = None) -> dict | None:
    """/proc/meminfo in BYTES (kB lines x 1024; unit-less lines kept as counts)."""
    text = _read("/proc/meminfo") if text is None else text
    if not text:
        return None
    out = {}
    for ln in text.splitlines():
        m = re.match(r"^([\w()]+):\s+(\d+)(?:\s+kB)?\s*$", ln)
        if m:
            out[m.group(1)] = int(m.group(2)) * (1024 if ln.rstrip().endswith("kB") else 1)
    return out or None


def _cg_int(path) -> int | str | None:
    t = (_read(path) or "").strip()
    if t == "max":
        return "max"
    return int(t) if t.isdigit() else None


def memory_cgroup_chain(proc_cgroup_text: str | None = None, root="/sys/fs/cgroup") -> dict:
    """The memory-cgroup chain of this process, leaf to root, with limit and usage at every level (cgroup v1
    ``memory`` controller, or v2 unified ``0::``). Unreadable values are None, never 'unlimited'."""
    text = _read("/proc/self/cgroup") if proc_cgroup_text is None else proc_cgroup_text
    if not text:
        return {"version": None, "chain": None, "reason": "/proc/self/cgroup unreadable"}
    v1 = v2 = None
    for ln in text.splitlines():
        parts = ln.split(":", 2)
        if len(parts) != 3:
            continue
        if "memory" in parts[1].split(","):
            v1 = parts[2]
        elif parts[0] == "0" and parts[1] == "":
            v2 = parts[2]
    rootp = Path(root)
    chain = []
    if v1 is not None:
        base, rel, version = rootp / "memory", v1, "v1"
        lim_name, use_name = "memory.limit_in_bytes", "memory.usage_in_bytes"
    elif v2 is not None and (rootp / v2.lstrip("/") / "memory.current").exists():
        base, rel, version = rootp, v2, "v2"
        lim_name, use_name = "memory.max", "memory.current"
    else:
        return {"version": None, "chain": None, "reason": "no memory controller found"}
    parts = [p for p in rel.split("/") if p]
    for i in range(len(parts), -1, -1):
        d = base.joinpath(*parts[:i])
        lim, use = _cg_int(d / lim_name), _cg_int(d / use_name)
        chain.append({"path": "/" + "/".join(parts[:i]), "limit": lim, "usage": use})
    return {"version": version, "chain": chain}


def effective_memory_limit(chain_rec: dict, mem: dict | None) -> int | None:
    """min(MemTotal, every NUMERIC limit on the chain). Any unreadable limit on the chain -> None (UNKNOWN): an
    unreadable ancestor is never treated as unlimited."""
    if not mem or "MemTotal" not in mem or not chain_rec.get("chain"):
        return None
    out = mem["MemTotal"]
    for lvl in chain_rec["chain"]:
        lim = lvl["limit"]
        if lim is None:
            return None
        if lim == "max" or (isinstance(lim, int) and lim >= UNLIMITED_CGROUP_V1):
            continue
        out = min(out, lim)
    return out


def memory_readings(mem_text: str | None = None, proc_cgroup_text: str | None = None, root="/sys/fs/cgroup") -> dict:
    """Every Linux candidate quantity side by side, each labelled NOT the R-FREE quantity. Deciding which one (if
    any) stands for R-FREE's free_memory_bytes is D-MEM-FREE; this function decides nothing."""
    mem = meminfo(mem_text)
    ch = memory_cgroup_chain(proc_cgroup_text, root)
    eff = effective_memory_limit(ch, mem)
    headroom = None
    if ch.get("chain"):
        hs = [lvl["limit"] - lvl["usage"] for lvl in ch["chain"]
              if isinstance(lvl["limit"], int) and lvl["limit"] < UNLIMITED_CGROUP_V1 and isinstance(lvl["usage"], int)]
        headroom = min(hs) if hs else None
    return {"meminfo_MemTotal": (mem or {}).get("MemTotal"), "meminfo_MemAvailable": (mem or {}).get("MemAvailable"),
            "meminfo_MemFree": (mem or {}).get("MemFree"), "meminfo_Inactive_file": (mem or {}).get("Inactive(file)"),
            "meminfo_SwapTotal": (mem or {}).get("SwapTotal"), "cgroup": ch, "effective_limit": eff,
            "cgroup_min_headroom": headroom,
            "note": "RAW Linux readings; none is the macOS vm_stat free+inactive+speculative+purgeable quantity of "
                    "R-FREE, and none is substituted for it (D-MEM-FREE, D-MEM-WIRED)"}


def psi_memory(text: str | None = None) -> dict | None:
    """/proc/pressure/memory (PSI) raw: {'some': {...}, 'full': {...}}. RAW ONLY (D-MEM-PRESSURE)."""
    text = _read("/proc/pressure/memory") if text is None else text
    if not text:
        return None
    out = {}
    for ln in text.splitlines():
        k, *kv = ln.split()
        out[k] = {a: b for a, b in (x.split("=", 1) for x in kv)}
    return out or None


# ====================================================================== CPU exclusivity (instantaneous, from /proc)
def cpu_ticks(proc_root="/proc") -> dict | None:
    """{pid: (ppid, utime + stime ticks, comm, exe-or-None)} for every readable process. None if /proc is
    unreadable. A process that vanishes between listing and reading is skipped (it cannot be busy any more)."""
    try:
        pids = [int(p.name) for p in Path(proc_root).iterdir() if p.name.isdigit()]
    except OSError:
        return None
    out = {}
    for pid in pids:
        st = proc_stat(pid, _read(f"{proc_root}/{pid}/stat") or "")
        if st is None:
            continue
        try:
            exe = os.readlink(f"{proc_root}/{pid}/exe")
        except OSError:
            exe = None                                  # unreadable path: never auto-allowed (D-ALLOW-PATHS)
        out[pid] = (st["ppid"], st["utime"] + st["stime"], st["comm"], exe)
    return out


def busy_processes(t0: dict | None, t1: dict | None, dt_s: float, threshold_pct: float, own_pids: set,
                   hz: int | None = None) -> list | None:
    """Processes whose CPU use over [t0, t1] exceeds ``threshold_pct`` (100 = one CPU, the macOS ps convention).
    PROPOSED reading for D-EXCL-WINDOW: Linux ``ps %cpu`` is cputime / elapsed over the process LIFETIME and is not
    used. ``own_pids`` (the campaign tree) is excluded; NOTHING ELSE is allowed by path or name here (D-ALLOW-PATHS is
    open, so the strictest reading applies). None if either snapshot is missing (no reading: the gate fails closed)."""
    if t0 is None or t1 is None or dt_s <= 0:
        return None
    hz = hz or os.sysconf("SC_CLK_TCK")
    out = []
    for pid, (ppid, ticks1, comm, exe) in t1.items():
        if pid in own_pids or ppid in own_pids:
            continue
        prev = t0.get(pid)
        if prev is None:
            continue                                     # born inside the window: measured next window
        pct = 100.0 * (ticks1 - prev[1]) / hz / dt_s
        if pct > threshold_pct:
            out.append({"pid": pid, "comm": comm, "exe": exe, "pct": round(pct, 1)})
    return out


# ====================================================================== OS update controls
def auto_update_settings(apt_conf_dir="/etc/apt/apt.conf.d", timers_dir="/etc/systemd/system/timers.target.wants",
                         uu_binary="/usr/bin/unattended-upgrade") -> dict:
    """Guest-visible automatic-update controls. ``guest_auto_install_enabled`` is False only on POSITIVE evidence:
    APT::Periodic::Enable "0", or APT::Periodic::Unattended-Upgrade "0" and no unattended-upgrade binary, and no
    enabled apt-daily-upgrade timer. A missing / unreadable setting counts as enabled (as for the macOS keys).
    ``provider_image_updates`` is always UNKNOWN from inside a guest (the platform can change between sessions
    without any guest setting; see the r2 inventory)."""
    vals = {}
    try:
        files = sorted(Path(apt_conf_dir).iterdir())
    except OSError:
        files = None
    for f in files or []:
        for m in re.finditer(r'APT::Periodic::([\w-]+)\s+"([^"]*)"\s*;', _read(f) or ""):
            vals[m.group(1)] = m.group(2)               # later files override earlier ones, as apt does
    timer = Path(timers_dir, "apt-daily-upgrade.timer").exists()
    uu = Path(uu_binary).exists()
    # disabled only on POSITIVE evidence; an unreadable directory or a missing key counts as enabled
    enabled = not (files is not None and not timer
                   and (vals.get("Enable") == "0" or vals.get("Unattended-Upgrade") == "0"))
    return {"apt_periodic": vals, "apt_daily_upgrade_timer_enabled": timer, "unattended_upgrade_present": uu,
            "guest_auto_install_enabled": enabled, "provider_image_updates": UNKNOWN}


# ====================================================================== supervisor / launch context
def systemd_is_pid1(comm_text: str | None = None, run_dir="/run/systemd/system") -> bool | None:
    comm = _read("/proc/1/comm") if comm_text is None else comm_text
    if comm is None:
        return None
    return comm.strip() == "systemd" and Path(run_dir).is_dir()


def launched_by_systemd(*, env=None, proc_cgroup_text: str | None = None, show=None, pid1=None,
                        prefix: str = CAMPAIGN_UNIT_PREFIX) -> dict:
    """PROPOSED replacement of mbs308_host.launched_by_launchd (amendment L-LAUNCH). PASS requires ALL of:
    systemd is PID 1; this process's cgroup is a ``<prefix>*.service`` unit; INVOCATION_ID is set; ``systemctl show``
    for that unit reports MainPID == this pid and the same InvocationID. Any failed reading: not pass.
    ``show(unit)`` (tests) returns {"MainPID": int, "InvocationID": str} or None."""
    env = os.environ if env is None else env
    is1 = systemd_is_pid1() if pid1 is None else pid1
    text = _read("/proc/self/cgroup") if proc_cgroup_text is None else proc_cgroup_text
    unit = None
    for ln in (text or "").splitlines():
        p = ln.split(":", 2)
        if len(p) == 3 and (p[1] == "name=systemd" or (p[0] == "0" and p[1] == "")):
            last = p[2].rstrip("/").rsplit("/", 1)[-1]
            if last.startswith(prefix) and last.endswith(".service"):
                unit = last
    inv = env.get("INVOCATION_ID")
    rec = None
    if is1 and unit and inv:
        rec = (show or _systemctl_show)(unit)
    ok = bool(is1 and unit and inv and isinstance(rec, dict) and rec.get("MainPID") == os.getpid()
              and rec.get("InvocationID") == inv)
    return {"systemd_pid1": is1, "unit": unit, "invocation_id": inv, "systemctl": rec, "pass": ok}


def _systemctl_show(unit: str) -> dict | None:
    try:
        p = subprocess.run(["systemctl", "show", "-p", "MainPID", "-p", "InvocationID", unit], capture_output=True,
                           text=True, timeout=30, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    kv = dict(ln.split("=", 1) for ln in p.stdout.splitlines() if "=" in ln)
    try:
        return {"MainPID": int(kv["MainPID"]), "InvocationID": kv["InvocationID"]}
    except (KeyError, ValueError):
        return None


# ====================================================================== durable atomic write (Linux)
def durable_write(path, data: bytes, *, fault=None) -> str:
    """O_CREAT|O_EXCL|O_NOFOLLOW tmp in the same directory, write all, fsync, rename over ``path``, fsync the
    directory, read back and verify the sha256. Returns the sha256. ``fault(stage)`` (tests only) is called at each
    stage name: "written", "fsynced", "renamed" -- a crash-injection hook. Linux has no F_FULLFSYNC; fsync is the
    strongest request a process can make, and whether the virtual disk honours it across a VM reclaim is a provider
    fact (D-HOST-LIFETIME), not something this function can establish."""
    p = Path(path)
    tmp = p.with_name(p.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        view = memoryview(data)
        while view:
            n = os.write(fd, view)
            view = view[n:]
        if fault:
            fault("written")
        os.fsync(fd)
        if fault:
            fault("fsynced")
    finally:
        os.close(fd)
    os.replace(tmp, p)
    if fault:
        fault("renamed")
    dfd = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)
    want = hashlib.sha256(data).hexdigest()
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    if got != want:
        raise OSError(f"read-back mismatch: {got} != {want}")
    return want


# ====================================================================== platform pins (Linux)
def os_release(text: str | None = None) -> dict | None:
    text = _read("/etc/os-release") if text is None else text
    if not text:
        return None
    out = {}
    for ln in text.splitlines():
        if "=" in ln and not ln.startswith("#"):
            k, v = ln.split("=", 1)
            out[k] = v.strip().strip('"')
    return out


def _fsha(p) -> str | None:
    b = _read(p, binary=True)
    return hashlib.sha256(b).hexdigest() if b is not None else None


def platform_readings() -> dict:
    """PROPOSED Linux pin set (amendment L-PIN): interpreter path + sha256, libpython path + sha256 (if the build is
    shared), sys.version, os-release ID / VERSION_ID / VERSION, kernel release, machine, glibc. ``cpu_model`` and
    ``vcpus`` are RECORDED (they bear on timing caps, never on the science) and pinned only if the reviewer so decides."""
    import sysconfig
    exe = os.path.realpath(sys.executable)
    lib = None
    ld = sysconfig.get_config_var("LDLIBRARY")
    libdir = sysconfig.get_config_var("LIBDIR")
    if sysconfig.get_config_var("Py_ENABLE_SHARED") and ld and libdir:
        lib = os.path.realpath(os.path.join(libdir, ld))
    osr = os_release() or {}
    cpu = None
    for ln in (_read("/proc/cpuinfo") or "").splitlines():
        if ln.startswith("model name"):
            cpu = ln.split(":", 1)[1].strip()
            break
    return {"python_executable": exe, "python_sha256": _fsha(exe), "libpython": lib,
            "libpython_sha256": _fsha(lib) if lib else None, "python_sys_version": sys.version,
            "os_id": osr.get("ID"), "os_version_id": osr.get("VERSION_ID"), "os_version": osr.get("VERSION"),
            "kernel_release": _platform.release(), "machine": _platform.machine(),
            "glibc": os.confstr("CS_GNU_LIBC_VERSION") if hasattr(os, "confstr") else None,
            "recorded_cpu_model": cpu, "recorded_vcpus": os.cpu_count()}


PIN_KEYS = ("python_executable", "python_sha256", "libpython", "libpython_sha256", "python_sys_version", "os_id",
            "os_version_id", "os_version", "kernel_release", "machine", "glibc")


def pin_mismatches(pins: dict, got: dict) -> list:
    """Keys whose value differs. A pin recorded as None never matches (an unreadable pin is not a pin)."""
    return [k for k in PIN_KEYS if pins.get(k) is None or got.get(k) != pins.get(k)]


# ====================================================================== disk
def free_disk_bytes(path) -> int | None:
    try:
        s = os.statvfs(path)
    except OSError:
        return None
    return s.f_bavail * s.f_frsize


# ====================================================================== preflight (PROPOSED Linux gate set)
def _g(v: bool | None) -> str:
    return UNKNOWN if v is None else (PASS if v else FAIL)


def preflight(repo_path, *, other_job_running: bool | None, launched: dict | None, host_attestation: dict | None,
              readings: dict | None = None) -> dict:
    """The Linux gate set of amendment section 3. Every mbs308_host gate has a counterpart; the ones whose rule
    quantity is undefined on Linux are OPEN_DECISION. ``host_attestation`` is a COMMITTED, REVIEWED record of provider
    lifetime / reclaim / exclusivity facts (D-HOST-LIFETIME); in development it is None, so that gate is UNKNOWN.
    ``readings`` (tests) overrides live readings by key. pass == every gate PASS."""
    r = dict(readings or {})
    power = r["power"] if "power" in r else power_source()
    free = r["free_disk"] if "free_disk" in r else free_disk_bytes(repo_path)
    boot = r["boot_id"] if "boot_id" in r else boot_id()
    upd = r["updates"] if "updates" in r else auto_update_settings()
    gates = {
        "ac_power": OPEN_DECISION if power == "ABSENT" else _g(None if power is None else power == AC),
        "lowpowermode_0": OPEN_DECISION,
        "thermal_pressure_0": OPEN_DECISION,
        "free_disk_ge_2GiB": _g(None if free is None else free >= MIN_FREE_DISK),
        "memory_pressure_normal": OPEN_DECISION,
        "free_memory_ge_min": OPEN_DECISION,
        "boot_id_recorded": _g(boot is not None),
        "no_other_campaign_job": _g(None if other_job_running is None else not other_job_running),
        "no_automatic_os_install": (FAIL if upd.get("guest_auto_install_enabled") else
                                    (UNKNOWN if upd.get("provider_image_updates") == UNKNOWN else PASS)),
        "host_exclusive": OPEN_DECISION,
        "host_lifetime_attested": PASS if (isinstance(host_attestation, dict) and host_attestation.get("reviewed")
                                           and host_attestation.get("accepted")) else UNKNOWN,
    }
    if launched is not None:
        gates["launched_by_systemd"] = PASS if launched.get("pass") else FAIL
    blocked = {k: v for k, v in gates.items() if v != PASS}
    return {"gates": gates, "pass": not blocked, "blocked": blocked,
            "readings": {"power": power, "free_disk_bytes": free, "boot_id": boot, "updates": upd,
                         "launched": launched},
            "open_decisions": sorted({_GATE_DECISION[k] for k, v in gates.items() if v == OPEN_DECISION})}


_GATE_DECISION = {"ac_power": "D-POWER-ABSENT", "lowpowermode_0": "D-LPM", "thermal_pressure_0": "D-THERMAL",
                  "memory_pressure_normal": "D-MEM-PRESSURE", "free_memory_ge_min": "D-MEM-FREE",
                  "host_exclusive": "D-EXCL-WINDOW", "host_lifetime_attested": "D-HOST-LIFETIME"}
