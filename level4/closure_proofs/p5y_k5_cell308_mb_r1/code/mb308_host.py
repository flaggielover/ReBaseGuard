"""Cell-308 MB campaign (r1, freeze r3) -- host-environment provenance: sleep, power, thermal. Environment only: no
science, no cell, no drift; no certified value depends on anything in this module.

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
import os
import re
import subprocess
import threading
import time

PMSET, SYSCTL, CAFFEINATE, NOTIFYUTIL = "/usr/bin/pmset", "/usr/sbin/sysctl", "/usr/bin/caffeinate", "/usr/bin/notifyutil"
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
            "thermal": thermal(), "load_x100": load_x100()}


def sample() -> dict:
    return {"clocks": clocks(), "power": power_source(), "thermal_level": thermal_level(), "thermal": thermal(),
            "load_x100": load_x100()}


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
