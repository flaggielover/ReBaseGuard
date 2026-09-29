"""Cell-308 MB-S successor campaign (r1) -- host contract. MB r1's mb308_host (freeze r3; every function below the
"MB r1" marker is byte-identical except `snapshot` / `sample`, which record three more keys) plus the successor's
additions (architecture sections 5 and 6, at the end of this file): the boot session UUID, free disk on the repository
volume, the memory-pressure level (read-only), low-power mode, a caffeinate SUPERVISOR thread that re-spawns
`caffeinate -i -m -s -w <pid>` whenever it dies and records every death and re-spawn, and the pre-marker PREFLIGHT
gates. Environment only: no science, no cell, no drift; no certified value depends on anything in this module; host
provenance never changes a status, an outcome or exactly-once (MB r1 E3). Preflight gates act only BEFORE the marker
(a failing gate refuses; nothing is consumed).

MB r1 (freeze r3) text follows.

Why (protocol section 14): the r2 official qualification failed Q12 because the host slept (lid closed) while the
decoy runtimes that Q12 reads were being measured; a runtime measured across a sleep is not evidence of cost.

Three INDEPENDENT sleep channels, all required:
  K  kernel clocks: CLOCK_MONOTONIC_RAW keeps counting while the host sleeps, CLOCK_UPTIME_RAW does not (macOS); both
     are unadjusted (no NTP slew); over an interval, increment(MONOTONIC_RAW) - increment(UPTIME_RAW) is the time the
     host slept;
  S  kern.sleeptime / kern.waketime (the kernel's last sleep and wake instants): any change over the interval is a
     sleep;
  L  the power-management log (`pmset -g log`): any Sleep / Wake / DarkWake entry stamped inside the interval.
Power: `pmset -g batt` must report AC power at the start, at every sample and at the end.
Thermal and load (RECORDED, never part of the status: a throttled or loaded host only lengthens runtimes, which can
only make a cap check fail, never pass): the OS thermal-pressure level (`notifyutil -g
com.apple.system.thermalpressurelevel`: 0 nominal, 1 moderate, 2 heavy, ...; None if unreadable) at every snapshot and
sample, the power log's ThermalEvent entries in the interval, the load average, and `pmset -g therm` (kept for the
record only: on this host it reports "no warning" while the thermal-pressure level is 1, so it is NOT a cool-host
check; the official run's cool-host precondition is thermal-pressure level 0 at start, see mb308_qualify).

assess() is fail-closed. CLEAN only if every channel is available and parses, the interval is covered by snapshots
and samples at most MAX_SAMPLE_GAP_S apart, no channel indicates a sleep and every power reading is AC. Otherwise
CONTAMINATED (a channel saw a sleep, or a reading was not AC) or AMBIGUOUS (a channel is missing or unparseable, or
the samples do not cover the interval). Only CLEAN is clean.

Every stored number is an integer (ns, us, ms, load x 100) or an ISO timestamp string without fractional seconds.
Prevention (keep_awake): `caffeinate -i -m -s` for the life of the calling process. macOS still sleeps on lid close
without an external display, whatever the assertions, so prevention is best effort and detection is what binds.
"""
from __future__ import annotations

import datetime
import hashlib
import os
import re
import subprocess
import threading
import time

PMSET, SYSCTL, CAFFEINATE, NOTIFYUTIL = "/usr/bin/pmset", "/usr/sbin/sysctl", "/usr/bin/caffeinate", "/usr/bin/notifyutil"
PS, LAUNCHCTL = "/bin/ps", "/bin/launchctl"
THERMAL_KEY = "com.apple.system.thermalpressurelevel"
CAFFEINATE_FLAGS = ("-i", "-m", "-s")          # idle, disk and (on AC) system sleep
ENV = {"PATH": "/usr/bin:/bin:/usr/sbin", "LC_ALL": "C"}
AC = "AC Power"
SLEEP_GAP_TOL_NS = 2_000_000_000               # channel K: the two clock reads are microseconds apart
SAMPLE_EVERY_S = 60
MAX_SAMPLE_GAP_S = 180
LOG_EVENT_TYPES = ("Sleep", "Wake", "DarkWake")
LOG_THERMAL_TYPES = ("ThermalEvent",)
_KT = re.compile(r"kern\.(sleeptime|waketime): \{ sec = (\d+), usec = (\d+) \}")
_BATT = re.compile(r"Now drawing from '([^']+)'")
# a power-log line: "YYYY-MM-DD HH:MM:SS +ZZZZ <type padded with spaces><TAB><details>"; the type must be EXACTLY one of
# LOG_EVENT_TYPES ("Wake Requests", "DarkWake" vs "Wake", ... are told apart by the padding up to the tab)
_LOG = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d [+-]\d{4}) (" + "|".join(LOG_EVENT_TYPES + LOG_THERMAL_TYPES) +
                  r") *\t")
_THERMAL_LEVEL = re.compile(r"^" + re.escape(THERMAL_KEY) + r" (\d+)\s*$")


class HostRefusal(Exception):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def _utc_s(epoch: float | None = None) -> str:
    t = datetime.datetime.now(datetime.timezone.utc) if epoch is None else \
        datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(args: list, timeout: int = 60) -> str | None:
    try:
        p = subprocess.run(args, capture_output=True, text=True, env=ENV, stdin=subprocess.DEVNULL, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout if p.returncode == 0 else None


# ------------------------------------------------------------------ channels (each accepts planted text for controls)
def clocks() -> dict:
    return {"monotonic_raw_ns": time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW),
            "uptime_raw_ns": time.clock_gettime_ns(time.CLOCK_UPTIME_RAW), "epoch_s": int(time.time()),
            "utc": _utc_s()}


def kern_times(text: str | None = None) -> dict | None:
    text = _run([SYSCTL, "kern.sleeptime", "kern.waketime"]) if text is None else text
    if not text:
        return None
    got = {m.group(1): int(m.group(2)) * 1_000_000 + int(m.group(3)) for m in _KT.finditer(text)}
    return got if set(got) == {"sleeptime", "waketime"} else None


def power_source(text: str | None = None) -> str | None:
    text = _run([PMSET, "-g", "batt"]) if text is None else text
    m = _BATT.search(text or "")
    return m.group(1) if m else None


def thermal(text: str | None = None) -> dict | None:
    text = _run([PMSET, "-g", "therm"]) if text is None else text
    if text is None:
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return {"lines": lines, "no_warning_recorded": bool(lines) and all(ln.startswith("Note: No ") for ln in lines)}


def thermal_level(text: str | None = None) -> int | None:
    text = _run([NOTIFYUTIL, "-g", THERMAL_KEY]) if text is None else text
    m = _THERMAL_LEVEL.match((text or "").strip())
    return int(m.group(1)) if m else None


def load_x100() -> list | None:
    try:
        return [round(x * 100) for x in os.getloadavg()]
    except OSError:
        return None


def power_log() -> str | None:
    return _run([PMSET, "-g", "log"], timeout=180)


def _log_entries(t0_epoch: int, t1_epoch: int, text: str | None, types: tuple) -> list | None:
    text = power_log() if text is None else text
    if text is None:
        return None
    out = []
    for ln in text.splitlines():
        m = _LOG.match(ln)
        if not m or m.group(2) not in types:
            continue
        t = int(datetime.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S %z").timestamp())
        if t0_epoch - 1 <= t <= t1_epoch + 1:
            out.append({"utc": _utc_s(t), "type": m.group(2)})
    return out


def log_events(t0_epoch: int, t1_epoch: int, text: str | None = None) -> list | None:
    """Sleep / Wake / DarkWake entries of the power log stamped in [t0 - 1 s, t1 + 1 s]; None if the log is
    unavailable."""
    return _log_entries(t0_epoch, t1_epoch, text, LOG_EVENT_TYPES)


def thermal_events(t0_epoch: int, t1_epoch: int, text: str | None = None) -> list | None:
    """ThermalEvent entries of the power log in the same window (recorded only)."""
    return _log_entries(t0_epoch, t1_epoch, text, LOG_THERMAL_TYPES)


def snapshot() -> dict:
    return {"clocks": clocks(), "kern_us": kern_times(), "power": power_source(), "thermal_level": thermal_level(),
            "thermal": thermal(), "load_x100": load_x100(),
            # MB-S additions (recorded, never gating after the marker)
            "boot_uuid": boot_session_uuid(), "memory_pressure": memory_pressure_level(), "lowpowermode": lowpowermode()}


def sample() -> dict:
    return {"clocks": clocks(), "power": power_source(), "thermal_level": thermal_level(), "thermal": thermal(),
            "load_x100": load_x100(),
            "boot_uuid": boot_session_uuid(), "memory_pressure": memory_pressure_level()}


class Sampler:
    """Background samples every SAMPLE_EVERY_S seconds while a load-bearing interval runs (daemon thread; it never
    touches signals, files or the computation)."""

    def __init__(self, every: int = SAMPLE_EVERY_S):
        self.every, self.samples = every, []
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._loop, name="mb308-host-sampler", daemon=True)

    def _loop(self) -> None:
        while not self._stop.wait(self.every):
            try:
                self.samples.append(sample())
            except Exception as exc:                                  # noqa: BLE001 (recorded, never raised)
                self.samples.append({"error": type(exc).__name__})

    def start(self) -> "Sampler":
        self._t.start()
        return self

    def stop(self) -> list:
        self._stop.set()
        self._t.join(timeout=60)
        return list(self.samples)


# ------------------------------------------------------------------ prevention and the AC precondition
def keep_awake(pid: int | None = None) -> dict:
    try:
        p = subprocess.Popen([CAFFEINATE, *CAFFEINATE_FLAGS, "-w", str(pid or os.getpid())], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"caffeinate_pid": p.pid, "caffeinate_flags": " ".join(CAFFEINATE_FLAGS)}
    except OSError as exc:
        return {"caffeinate": f"unavailable ({type(exc).__name__})"}


def require_ac(text: str | None = None) -> str:
    src = power_source(text)
    if src != AC:
        raise HostRefusal("HOST_NOT_ON_AC", src or "power source unreadable")
    return src


# ------------------------------------------------------------------ the fail-closed assessment
def assess(start, end, samples, events) -> dict:
    reasons = []
    gap_ms = spacing_s = None
    try:
        s0, s1 = start["clocks"], end["clocks"]
        dm = s1["monotonic_raw_ns"] - s0["monotonic_raw_ns"]
        du = s1["uptime_raw_ns"] - s0["uptime_raw_ns"]
        if not (isinstance(dm, int) and isinstance(du, int)) or dm <= 0 or du <= 0:
            reasons.append("AMBIGUOUS: K clocks absent or not increasing")
        else:
            gap_ms = (dm - du) // 1_000_000
            if dm - du > SLEEP_GAP_TOL_NS:
                reasons.append(f"CONTAMINATED: K the host slept {gap_ms // 1000} s in the interval")
            elif dm - du < -SLEEP_GAP_TOL_NS:
                reasons.append("AMBIGUOUS: K uptime advanced more than monotonic time")
    except (KeyError, TypeError):
        reasons.append("AMBIGUOUS: K clocks absent")
    ks, ke = (start or {}).get("kern_us"), (end or {}).get("kern_us")
    if not isinstance(ks, dict) or not isinstance(ke, dict) or set(ks) != {"sleeptime", "waketime"} or set(ke) != set(ks):
        reasons.append("AMBIGUOUS: S kern.sleeptime / kern.waketime absent")
    elif ks != ke:
        reasons.append("CONTAMINATED: S kern.sleeptime / kern.waketime changed in the interval")
    if not isinstance(events, list):
        reasons.append("AMBIGUOUS: L power log unavailable")
    elif events:
        reasons.append(f"CONTAMINATED: L {len(events)} Sleep / Wake / DarkWake entries in the interval")
    seq = [start, *(samples if isinstance(samples, list) else []), end]
    if not isinstance(samples, list):
        reasons.append("AMBIGUOUS: samples absent")
    power = [x.get("power") if isinstance(x, dict) else None for x in seq]
    if any(p is None for p in power):
        reasons.append("AMBIGUOUS: a power reading is absent or unreadable")
    elif any(p != AC for p in power):
        reasons.append("CONTAMINATED: a power reading is not AC")
    try:
        ts = [x["clocks"]["monotonic_raw_ns"] for x in seq]
        steps = [b - a for a, b in zip(ts, ts[1:])]
        spacing_s = max(steps) // 1_000_000_000 if steps else None
        if any(d < 0 for d in steps):
            reasons.append("AMBIGUOUS: samples out of order")
        elif spacing_s is None or spacing_s > MAX_SAMPLE_GAP_S:
            reasons.append(f"AMBIGUOUS: samples do not cover the interval (largest spacing {spacing_s} s)")
    except (KeyError, TypeError):
        reasons.append("AMBIGUOUS: a sample carries no clocks")
    status = "CONTAMINATED" if any(r.startswith("CONTAMINATED") for r in reasons) else \
        ("AMBIGUOUS" if reasons else "CLEAN")
    therm = [x.get("thermal") for x in seq if isinstance(x, dict)]
    levels = [x.get("thermal_level") for x in seq if isinstance(x, dict)]
    loads = [x.get("load_x100") for x in seq if isinstance(x, dict) and isinstance(x.get("load_x100"), list)]
    return {"status": status, "clean": status == "CLEAN", "reasons": reasons, "sleep_gap_ms": gap_ms,
            "samples": len(seq) - 2, "largest_spacing_s": spacing_s,
            "thermal_level_max": max((v for v in levels if isinstance(v, int)), default=None),
            "thermal_level_unreadable": sum(1 for v in levels if not isinstance(v, int)),
            "pmset_therm_warning_recorded": any(isinstance(t, dict) and not t.get("no_warning_recorded") for t in therm),
            "load_x100_max_1min": max((ld[0] for ld in loads), default=None),
            "log_events": events[:50] if isinstance(events, list) else None}


def provenance(start: dict, samples: list, end: dict) -> dict:
    """Close an interval: read the power log over it (sleep entries, and ThermalEvent entries for the record) and
    assess. Never raises."""
    ev = tev = None
    try:
        text = power_log()
        ev = log_events(start["clocks"]["epoch_s"], end["clocks"]["epoch_s"], text) if text is not None else None
        tev = thermal_events(start["clocks"]["epoch_s"], end["clocks"]["epoch_s"], text) if text is not None else None
    except Exception:                                                  # noqa: BLE001
        ev = None
    rec = {"start": start, "samples": samples, "end": end, "events": ev, "thermal_events": tev}
    try:
        rec["assessment"] = assess(start, end, samples, ev)
    except Exception as exc:                                           # noqa: BLE001
        rec["assessment"] = {"status": "AMBIGUOUS", "clean": False, "reasons": [f"AMBIGUOUS: {type(exc).__name__}"]}
    return rec



# ====================================================================== MB-S additions (architecture sections 5, 6)
_UUID = re.compile(r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$")
_LPM = re.compile(r"^\s*lowpowermode\s+(\d+)\s*$", re.M)
MIN_FREE_DISK = 2 * 1024 ** 3                  # section 6: free disk >= 2 GiB on the repository volume
DEFAULTS = "/usr/bin/defaults"
SOFTWARE_UPDATE_DOMAIN = "/Library/Preferences/com.apple.SoftwareUpdate"
SU_KEYS = ("AutomaticallyInstallMacOSUpdates", "AutomaticDownload", "CriticalUpdateInstall", "ConfigDataInstall")
# route delta review DR2 (c): the keys whose automatic INSTALLATION can change the OS build (macOS updates, Rapid
# Security Responses) gate `execute`; a missing key means enabled (the macOS default). The others are recorded.
SU_GATING_KEYS = ("AutomaticallyInstallMacOSUpdates", "CriticalUpdateInstall")
MEMORY_PRESSURE_NORMAL = 1                     # kern.memorystatus_vm_pressure_level: 1 normal, 2 warn, 4 critical
RESPAWN_BACKOFF_S = 0.5


def boot_session_uuid(text: str | None = None) -> str | None:
    """kern.bootsessionuuid: changes at every boot (a reboot is detected by its change; section 6)."""
    text = _run([SYSCTL, "-n", "kern.bootsessionuuid"]) if text is None else text
    t = (text or "").strip().upper()
    return t if _UUID.match(t) else None


def free_disk_bytes(path) -> int | None:
    try:
        st = os.statvfs(str(path))
    except OSError:
        return None
    return st.f_bavail * st.f_frsize


def memory_pressure_level(text: str | None = None) -> int | None:
    """Read-only: kern.memorystatus_vm_pressure_level (1 normal, 2 warn, 4 critical); None if unreadable."""
    text = _run([SYSCTL, "-n", "kern.memorystatus_vm_pressure_level"]) if text is None else text
    t = (text or "").strip()
    return int(t) if t.isdigit() else None


def lowpowermode(text: str | None = None) -> int | None:
    text = _run([PMSET, "-g"]) if text is None else text
    m = _LPM.search(text or "")
    return int(m.group(1)) if m else None


def software_update_settings(texts: dict | None = None) -> dict:
    """READ-ONLY (`defaults read`; nothing is ever written): the automatic-update keys, 1 / 0, or None when the key is
    missing (= enabled by default). `auto_install_enabled` is true when any gating key is enabled or missing."""
    vals = {}
    for k in SU_KEYS:
        t = (texts or {}).get(k) if texts is not None else _run([DEFAULTS, "read", SOFTWARE_UPDATE_DOMAIN, k])
        t = (t or "").strip()
        vals[k] = int(t) if t in ("0", "1") else None
    enabled = {k: vals[k] != 0 for k in SU_KEYS}
    return {"values": vals, "enabled": enabled, "missing_means_enabled": True,
            "auto_install_enabled": any(enabled[k] for k in SU_GATING_KEYS)}


# ------------------------------------------------------------------ process identity (pid, start time, command sha)
def process_start(pid: int, text: str | None = None) -> str | None:
    """The process start time as `ps -o lstart=` prints it (one-second resolution); None if no such process."""
    text = _run([PS, "-p", str(int(pid)), "-o", "lstart="]) if text is None else text
    t = " ".join((text or "").split())
    return t or None


def process_command_sha256(pid: int, text: str | None = None) -> str | None:
    text = _run([PS, "-ww", "-p", str(int(pid)), "-o", "command="]) if text is None else text
    t = (text or "").strip()
    return hashlib.sha256(t.encode()).hexdigest() if t else None


def process_ppid(pid: int) -> int | None:
    t = (_run([PS, "-p", str(int(pid)), "-o", "ppid="]) or "").strip()
    return int(t) if t.isdigit() else None


def pid_alive(pid) -> bool:
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 1:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def identity(pid: int | None = None) -> dict:
    """(pid, start time, boot UUID, command sha256): the identity recorded in pidfiles, locks and the journal."""
    pid = os.getpid() if pid is None else int(pid)
    return {"pid": pid, "start_time": process_start(pid), "boot_uuid": boot_session_uuid(),
            "command_sha256": process_command_sha256(pid)}


def identity_alive(ident, boot_uuid: str | None = None) -> bool:
    """True only if ALL four fields match a live process under the current (or the given) boot UUID. A stale identity
    (a dead pid, a reused pid with another start time or command, another boot) is never trusted."""
    if not isinstance(ident, dict):
        return False
    cur_boot = boot_session_uuid() if boot_uuid is None else boot_uuid
    if not ident.get("boot_uuid") or ident.get("boot_uuid") != cur_boot:
        return False
    pid = ident.get("pid")
    if not pid_alive(pid):
        return False
    st = process_start(pid)
    if st is None or st != ident.get("start_time"):
        return False
    cs = process_command_sha256(pid)
    return cs is not None and cs == ident.get("command_sha256")


# ------------------------------------------------------------------ the caffeinate supervisor (section 5)
class CaffeinateSupervisor:
    """Runs `caffeinate -i -m -s -w <pid>` and re-spawns it whenever it dies while the watched process lives; records
    every spawn and death (utc, caffeinate pid, return code). Environment only: it never touches the computation, a
    signal handler or a file other than the optional append-only event sink."""

    def __init__(self, pid: int | None = None, poll_s: float = 0.2, sink=None):
        self.pid = os.getpid() if pid is None else int(pid)
        self.poll_s, self.sink = poll_s, sink
        self.events: list = []
        self.proc = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._t = threading.Thread(target=self._loop, name="mbs308-caffeinate-supervisor", daemon=True)

    def _record(self, ev: dict) -> None:
        ev = {"utc": _utc_s(), **ev}
        with self._lock:
            self.events.append(ev)
        if self.sink is not None:
            try:
                self.sink(ev)
            except Exception:                                        # noqa: BLE001 (recorded, never raised)
                pass

    def _spawn(self) -> None:
        try:
            self.proc = subprocess.Popen([CAFFEINATE, *CAFFEINATE_FLAGS, "-w", str(self.pid)], stdin=subprocess.DEVNULL,
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._record({"event": "spawn", "caffeinate_pid": self.proc.pid, "watched_pid": self.pid})
        except OSError as exc:
            self.proc = None
            self._record({"event": "spawn_failed", "error": type(exc).__name__})

    def _loop(self) -> None:
        self._spawn()
        while not self._stop.is_set():
            p = self.proc
            if p is None:
                if self._stop.wait(RESPAWN_BACKOFF_S):
                    break
                self._spawn()
                continue
            rc = p.poll()
            if rc is None:
                self._stop.wait(self.poll_s)
                continue
            if self._stop.is_set():
                break
            self._record({"event": "death", "caffeinate_pid": p.pid, "returncode": rc})
            if not pid_alive(self.pid):
                break
            self._stop.wait(0.05)
            if not self._stop.is_set():
                self._spawn()
                self._record({"event": "respawn", "caffeinate_pid": None if self.proc is None else self.proc.pid})

    def start(self) -> "CaffeinateSupervisor":
        self._t.start()
        return self

    def current_pid(self) -> int | None:
        p = self.proc
        return None if p is None or p.poll() is not None else p.pid

    def stop(self) -> dict:
        self._stop.set()
        self._t.join(timeout=10)
        p = self.proc
        if p is not None and p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        return self.record()

    def record(self) -> dict:
        with self._lock:
            ev = list(self.events)
        return {"caffeinate_flags": " ".join(CAFFEINATE_FLAGS), "watched_pid": self.pid, "events": ev,
                "spawns": sum(1 for e in ev if e["event"] == "spawn"),
                "deaths": sum(1 for e in ev if e["event"] == "death"),
                "respawns": sum(1 for e in ev if e["event"] == "respawn")}


# ------------------------------------------------------------------ the launchd context (section 5)
def launchd_job_pid(label: str, uid: int | None = None) -> int | None:
    """The pid launchd reports for gui/<uid>/<label> (`launchctl print`), None if the job is not running."""
    uid = os.getuid() if uid is None else uid
    text = _run([LAUNCHCTL, "print", f"gui/{uid}/{label}"], timeout=30)
    if not text:
        return None
    m = re.search(r"^\s*pid = (\d+)\s*$", text, re.M)
    st = re.search(r"^\s*state = (\S+)\s*$", text, re.M)
    if not m or not st or st.group(1) != "running":
        return None
    return int(m.group(1))


def launched_by_launchd(label_env: str = "MBS308_LAUNCH_LABEL") -> dict:
    """The execute-side check (section 6, last gate): XPC_SERVICE_NAME must EQUAL the launcher's label (the hosting app
    exports XPC_SERVICE_NAME=0, so presence alone proves nothing), the label must carry the campaign prefix, the parent
    must be launchd (pid 1), and `launchctl print` must name THIS pid as the running job."""
    label = os.environ.get(label_env, "")
    xpc = os.environ.get("XPC_SERVICE_NAME", "")
    ok_label = label.startswith("org.rebaseguard.mbs308.") and xpc == label
    ppid = os.getppid()
    job_pid = launchd_job_pid(label) if ok_label else None
    return {"label": label or None, "xpc_service_name_matches": ok_label, "ppid": ppid,
            "launchctl_pid": job_pid, "pass": bool(ok_label and ppid == 1 and job_pid == os.getpid())}


# ------------------------------------------------------------------ preflight gates (section 6; before the marker)
def preflight_gates(repo_path, *, other_job_running: bool, launched: dict | None, texts: dict | None = None,
                    su_texts: dict | None = None) -> dict:
    """Each gate is a boolean; `pass` needs every gate. `launched` None = the launcher gate is not evaluated (the
    launcher's own preflight, before it bootstraps the job); execute passes launched_by_launchd()."""
    t = texts or {}
    power = power_source(t.get("batt"))
    lpm = lowpowermode(t.get("pmset"))
    tl = thermal_level(t.get("thermal"))
    free = free_disk_bytes(repo_path) if "free" not in t else t["free"]
    mp = memory_pressure_level(t.get("memory"))
    boot = boot_session_uuid(t.get("boot"))
    su = software_update_settings(su_texts)
    gates = {"ac_power": power == AC, "lowpowermode_0": lpm == 0, "thermal_pressure_0": tl == 0,
             "free_disk_ge_2GiB": isinstance(free, int) and free >= MIN_FREE_DISK,
             "memory_pressure_normal": mp == MEMORY_PRESSURE_NORMAL, "boot_uuid_recorded": boot is not None,
             "no_other_campaign_job": not other_job_running,
             "no_automatic_os_install": not su["auto_install_enabled"]}
    if launched is not None:
        gates["launched_by_launchd"] = bool(launched.get("pass"))
    return {"gates": gates, "pass": all(gates.values()),
            "readings": {"power": power, "lowpowermode": lpm, "thermal_level": tl, "free_disk_bytes": free,
                         "memory_pressure": mp, "boot_uuid": boot, "launched": launched, "software_update": su}}
