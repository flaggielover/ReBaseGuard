"""Cell-308 new-host route (Claude Cloud, r1) -- DEVELOPMENT-ONLY Linux platform layer (revision 5).

STATUS: DEV_ONLY · NOT ACCEPTED BY ANY GOVERNANCE REVIEW · NOT FROZEN · NOT A CAMPAIGN NAMESPACE · NOT USABLE FOR ANY
DESIGNATED SERIES, QUALIFICATION, FREEZE, GRANT OR TARGET STEP. Nothing in the historical candidate (142d97a9) imports
or is changed by this file. Target-free development artefact under the owner's 2026-10-14 authorization
(governance/new_host_route_cloud_r1/USER_AUTHORIZATION_20261014.md) for the PROPOSED route amendment.

Revision 2 repairs the findings of the fresh review 59 (reviews/REVIEW_CLOUD_R1_FEASIBILITY_AMENDMENT_DEV.md):
F1 pins cover every mapped shared object (libm, libc, loader) plus package versions and livepatch; F2 a zombie is
never proof of death (UNKNOWN, as macOS O-4); F8 gates need a verified, machine-bound, accepted attestation; F9 an
unreadable or unknown power supply is UNKNOWN; F10 cgroup readings are UNKNOWN on any unreadable level and numeric only
with an attested root, memory.high honoured, cpu/cpuset/pids read; F11 apt settings via `apt-config dump` and other
update vectors; F13 exclusivity keyed by (pid, starttime), births counted, namespaces / hidepid refused; F14 identity
records the PID and time namespaces; F15 `launched=None` only for the launcher's own preflight; F23 a stale tmp is a
named state.

Revision 3 repairs the findings of the fresh delta review 60 (reviews/REVIEW_CLOUD_R1_DELTA_R2.md): N1 attestations
are parsed from the committed file and accepted only by a committed review naming their sha256, and the gates that
depend on D-HOST-LIFETIME stay OPEN_DECISION while it is open; N2 only known battery statuses count; N3 root
attestation must be ``is True`` and comes from a verified attestation; N4 the /proc view must be the initial PID
namespace's; N6 the boot id is validated; N7 exited / unreadable processes are not silently dropped and the campaign
tree is keyed by (pid, starttime); N8 pid-based death evidence needs recorded, matching namespaces; N11 the pin set
requires libm, libc and the loader; N12 execute / resume verify the launch record's fields.

Revision 4 repairs the fresh delta review 61 (reviews/REVIEW_CLOUD_R1_DELTA_R3.md), whose remaining paths were all
CALLER-ASSERTED inputs: P1 the acceptance of an attestation is found by a fixed review-path pattern with an explicit
verdict (never named by the attestation); P2 root attestation is derived inside memory_readings from a verified
attestation, and a non-initial or unreadable cgroup namespace always blocks a number; P5 the decided D-* set is a
validated module constant, not a parameter; P6 execute / resume compare the launch record with a fresh reading; P7 L'
is AMBIGUOUS until a reviewed journal reader exists; P8 update units are checked via systemctl or every unit path;
P9 identity records are shape-validated; P11 the pin point refuses an undefined module list. Revision 5 (review 62):
the acceptance set is the direct ``REVIEW_HOST_ATTESTATION_*.md`` children only, with a single verdict line, a
case-insensitive negative scan and blob-level commit order (G1-G3); preflight and busy_processes take every reading
themselves (G5, G6); unit detection follows the full systemd search path, is-active, dangling links and not-found
(G7, G9); the pin point has no list override (G8); DECIDED accepts every amendment id (G11). Trust-relevant test
seams are module attributes. Some readers still take injected texts or roots for the tests (proc_view_complete,
memory_readings, power_source, auto_update_settings, unit_enabled); a reviewed caller never passes them, and
preflight passes none. preflight's caller inputs are mode, other_job_running, launched (compared with a fresh
reading) and attestation_ref (a pointer to committed files); busy_processes takes caller snapshots from cpu_ticks().

Design rules (all fail-closed):

* A reader returns ``None`` when its source is absent, unreadable or of a kind it does not recognise. ``None`` is
  UNKNOWN. UNKNOWN never passes a gate and never proves death.
* Where the accepted rule text names a macOS quantity with no Linux identity, the gate evaluates to
  ``OPEN_DECISION``, which never passes. No Linux metric is substituted for a macOS one here.
* Process identity keeps the accepted R2 / N-2 semantics of ``mbs308_host.identity_state`` (DEAD only on positive
  evidence; failed reading UNKNOWN; unrecorded field never compared) and macOS O-4's outcome for a zombie (UNKNOWN).
* Gates: PASS, FAIL, UNKNOWN, OPEN_DECISION. ``preflight`` passes only if every gate is PASS.

Every reader accepts injected text / paths for the tests. Stdlib only; Python >= 3.11.
"""
from __future__ import annotations

import hashlib
import json
import math
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
SLEEP_GAP_TOL_NS = 2_000_000_000                # == mbs308_host.SLEEP_GAP_TOL_NS (pinned by a test against 142d97a9)
MAX_SAMPLE_GAP_S = 180                          # == mbs308_host.MAX_SAMPLE_GAP_S (pinned by a test against 142d97a9)
MIN_FREE_DISK = 2 * 1024 ** 3                   # == mbs308_host.MIN_FREE_DISK
CAMPAIGN_UNIT_PREFIX = "rebaseguard-mbs308-"    # PROPOSED systemd unit-name prefix (amendment row L-LAUNCH)
NO_IMAGE_CHANGE = "ATTESTED_NO_IMAGE_OR_OS_CHANGE"   # the only provider-image token that can pass (F8)
KNOWN_NOT_DISCHARGING = ("Charging", "Full", "Not charging")   # N2: the only battery statuses read as not discharging
INIT_PID_NS, INIT_CGROUP_NS = 0xEFFFFFFC, 0xEFFFFFFB          # proc_ns_init_ino / cgroup init ns inode (kernel consts)
ATTESTATION_SCHEMA = "rebaseguard.p5y.k5.newhost-cloud-r1.host-attestation.v1"
ACCEPTANCE_LINE = "HOST_ATTESTATION_ACCEPTED sha256="          # a committed review accepts an attestation by this line
DECIDED: frozenset = frozenset()   # the D-* decisions taken by an accepted review and the owner: NONE in development
JOURNAL_READER_REVIEWED = False    # P7: L' counts only once a reviewed journal reader exists (none does)
PIN_POINT_MODULES: tuple | None = None   # P11: the science's import list, fixed by the accepted amendment (not yet)
ACCEPTANCE_REVIEW_DIR = "level4/closure_proofs/p5y_k5_cell308_research/reviews"   # P1: where acceptances may live
ACCEPTANCE_REVIEW_PREFIX = "REVIEW_HOST_ATTESTATION_"                            # P1: and how they are named
ACCEPTANCE_VERDICT_LINE = "VERDICT: HOST_ATTESTATION_ACCEPTED"

OPEN_DECISIONS = {
    "D-MEM-FREE": "R-FREE quantity on Linux (macOS vm_stat free+inactive+speculative+purgeable has no Linux identity)",
    "D-MEM-WIRED": "R-MEM step 5 'hw.memsize - W_idle' on Linux under a cgroup limit",
    "D-MEM-PRESSURE": "memory_pressure_normal (macOS kern.memorystatus_vm_pressure_level == 1) on Linux",
    "D-THERMAL": "thermal_pressure_0 (macOS thermal-pressure level 0) on Linux / on hosts with no thermal zones",
    "D-LPM": "lowpowermode_0 (macOS pmset lowpowermode) on Linux",
    "D-POWER-ABSENT": "AC-power gate on hosts that expose no power supply (VMs, servers) or only USB / UPS supplies",
    "D-ALLOW-PATHS": "R-ALLOW (b) SIP path classes on Linux (the 39-name base set is D-ALLOW-BASE39)",
    "D-EXCL-WINDOW": "R-EXCL-PCT reading on Linux (ps %cpu: lifetime average on Linux, decaying average on macOS)",
    "D-PAUSE": "VM pause / snapshot detection channel for hosts whose guest clocks may not show a pause",
    "D-HOST-LIFETIME": "provider lifetime / reclaim / exclusivity / root-cgroup guarantees (an attestation)",
    # G11: the remaining ids of amendment section 4 (not gate-bound here, but valid members of DECIDED)
    "D-RC2-SCOPE": "which accepted text governs determinism off the old platform",
    "D-ALLOW-BASE39": "R-ALLOW's base set of 39 macOS names on Linux",
    "D-WORKERS-CORES": "WORKERS 5 on fewer than 6 cores",
    "D-CAPS-CPU": "caps measured on macOS arm64 decoys, on a different CPU",
    "D-INTERPRETER": "the Linux interpreter build",
    "D-TEXT-LAUNCHD": "textual amendments of texts naming launchd",
    "D-LID": "the clamshell readiness check",
    "D-S15-NEWHOST": "asserting S15 from another host",
    "D-LDET-REPEAT": "a repeat rule for L-DET",
    "D-PIN-POINT": "the pin point's fixed module list",
    "D-ID-ZOMBIE": "any further Linux evidence of death",
}


class StaleTmp(FileExistsError):
    """durable_write found ``<name>.tmp`` left by an interrupted write. A NAMED state (F23): never deleted here; the
    state machine's recovery must record it and name the operator action, as for MB-S's lockfiles."""


def _read(path, binary: bool = False):
    try:
        return Path(path).read_bytes() if binary else Path(path).read_text()
    except (OSError, UnicodeDecodeError):
        return None


def _sha(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


# ====================================================================== boot, namespaces, machine
_BOOT_ID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def boot_id(text: str | None = None) -> str | None:
    """/proc/sys/kernel/random/boot_id. Detects reboots only; a VM pause need not change it (D-PAUSE)."""
    text = _read("/proc/sys/kernel/random/boot_id") if text is None else text
    t = (text or "").strip()
    return t if _BOOT_ID.match(t) else None


def ns_inode(kind: str, pid: str = "self") -> int | None:
    try:
        return os.stat(f"/proc/{pid}/ns/{kind}").st_ino
    except OSError:
        return None


def machine_identity(machine_id_path="/etc/machine-id", dmi_path="/sys/class/dmi/id/product_uuid") -> dict:
    """sha256 of /etc/machine-id and of the DMI product UUID (values never stored). machine-id alone is not a hardware
    identity on image-cloned VMs (F20); ``hardware_bound`` is True only if the DMI UUID was readable."""
    mid, dmi = _read(machine_id_path), _read(dmi_path)
    return {"machine_id_sha256": _sha(mid.strip().encode()) if mid and mid.strip() else None,
            "product_uuid_sha256": _sha(dmi.strip().encode()) if dmi and dmi.strip() else None,
            "hardware_bound": bool(dmi and dmi.strip())}


# ====================================================================== process identity (R2 / N-2 / O-4 semantics)
def proc_stat(pid: int, text: str | None = None) -> dict | None:
    """Parse /proc/<pid>/stat (``comm`` may contain spaces and parentheses: split at the LAST ')')."""
    if type(pid) is not int or pid <= 0:
        return None
    text = _read(f"/proc/{pid}/stat") if text is None else text
    if not isinstance(text, str) or not text:
        return None
    lp, rp = text.find("("), text.rfind(")")
    if lp < 0 or rp < lp:
        return None
    try:
        head_pid = int(text[:lp].strip())
        rest = text[rp + 1:].split()
        record = {"pid": head_pid, "comm": text[lp + 1:rp], "state": rest[0], "ppid": int(rest[1]),
                  "utime": int(rest[11]), "stime": int(rest[12]), "starttime": int(rest[19])}
        if head_pid != pid or record["state"] not in ("R", "S", "D", "T", "t", "I", "Z", "X") \
                or any(record[k] < 0 for k in ("ppid", "utime", "stime", "starttime")):
            return None
        return record
    except (ValueError, IndexError):
        return None


def cmdline_sha256(pid: int, data: bytes | None = None) -> str | None:
    """sha256 of /proc/<pid>/cmdline. Empty (kernel thread, zombie, exiting task) or unreadable: None (failed read)."""
    data = _read(f"/proc/{int(pid)}/cmdline", binary=True) if data is None else data
    return hashlib.sha256(data).hexdigest() if data else None


def identity(pid: int | None = None) -> dict:
    """(pid, starttime ticks, boot_id, cmdline sha256) plus the RECORDER's PID / time namespace inodes (F14)."""
    pid = os.getpid() if pid is None else int(pid)
    st = proc_stat(pid)
    return {"pid": pid, "starttime_ticks": None if st is None else st["starttime"], "boot_id": boot_id(),
            "cmdline_sha256": cmdline_sha256(pid), "pidns": ns_inode("pid"), "timens": ns_inode("time")}


def _pid_exists(pid: int) -> bool | None:
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except (TypeError, ValueError, OSError):
        return None
    return True


def _ident_shape_ok(ident) -> bool:
    """P9: pid a positive non-bool int; every RECORDED field of the right shape (boot id by the reader's regex,
    starttime and namespace inodes non-negative non-bool ints, cmdline sha256 64 hex)."""
    if not isinstance(ident, dict):
        return False
    pid = ident.get("pid")
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    b = ident.get("boot_id")
    if b is not None and (not isinstance(b, str) or not _BOOT_ID.fullmatch(b)):
        return False
    for k in ("starttime_ticks", "pidns", "timens"):
        v = ident.get(k)
        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 0):
            return False
    c = ident.get("cmdline_sha256")
    return c is None or (isinstance(c, str) and re.fullmatch(r"[0-9a-f]{64}", c) is not None)


def identity_state(ident, *, current_boot: str | None = None, exists=None, stat=None, cmd=None,
                   current_ns: dict | None = None) -> str:
    """ALIVE / DEAD / UNKNOWN.

    DEAD only on POSITIVE evidence: the boot id changed; ESRCH; or the RECORDED starttime / cmdline differs.
    UNKNOWN on any failed reading; on an unrecorded namespace or a namespace mismatch between recorder and reader
    (pid numbers and starttimes are namespace-relative, F14 / N8); and for a zombie / dead task (state Z or X): a
    zombie leader can carry live threads (review 59 probe P6), and macOS O-4 reads a zombie as UNKNOWN, so it is
    never proof of death (F2). Other states (R, S, D, T, t, ...) are a live task. A field never recorded is never
    compared; ALIVE needs every field recorded and matching. Injection (tests): ``current_boot`` (``""`` = read
    failed), ``exists``, ``stat``, ``cmd``,
    ``current_ns`` ({"pidns": int|None, "timens": int|None})."""
    if not _ident_shape_ok(ident):
        return UNKNOWN
    cur = boot_id() if current_boot is None else (boot_id(current_boot) if isinstance(current_boot, str) else None)
    if cur is None:
        return UNKNOWN
    recorded_boot = ident.get("boot_id")
    if recorded_boot is not None and (not isinstance(recorded_boot, str) or boot_id(recorded_boot) is None):
        return UNKNOWN
    if recorded_boot is not None and boot_id(recorded_boot) != cur:
        return DEAD
    ns = current_ns if current_ns is not None else {"pidns": ns_inode("pid"), "timens": ns_inode("time")}
    for k in ("pidns", "timens"):
        # N8: pid numbers, ESRCH and starttimes mean something only in the recorder's namespaces; an unrecorded or
        # different namespace makes every pid-based reading UNKNOWN (a boot-id change, above, stays positive evidence)
        if type(ident.get(k)) is not int or ident[k] <= 0 or not isinstance(ns, dict) \
                or type(ns.get(k)) is not int or ns.get(k) != ident[k]:
            return UNKNOWN
    pid = ident["pid"]
    ex = (exists or _pid_exists)(pid)
    if type(ex) is not bool:
        return UNKNOWN
    if ex is False:
        return DEAD
    st = (stat or proc_stat)(pid)
    if st is None:
        return UNKNOWN
    if not isinstance(st, dict) or type(st.get("pid")) is not int or st["pid"] != pid:
        return UNKNOWN
    if st.get("state") in ("Z", "X"):
        return UNKNOWN
    if st.get("state") not in ("R", "S", "D", "T", "t", "I"):
        return UNKNOWN
    if any(type(st.get(k)) is not int or st[k] < 0 for k in ("ppid", "utime", "stime")):
        return UNKNOWN
    if type(st.get("starttime")) is not int or st["starttime"] < 0:
        return UNKNOWN
    if ident.get("starttime_ticks") is not None and (
            type(ident["starttime_ticks"]) is not int or ident["starttime_ticks"] < 0):
        return UNKNOWN
    if ident.get("starttime_ticks") is not None and st["starttime"] != ident["starttime_ticks"]:
        return DEAD
    cs = (cmd or cmdline_sha256)(pid)
    if not isinstance(cs, str) or not re.fullmatch(r"[0-9a-f]{64}", cs):
        return UNKNOWN
    recorded_cmd = ident.get("cmdline_sha256")
    if recorded_cmd is not None and (not isinstance(recorded_cmd, str)
                                     or not re.fullmatch(r"[0-9a-f]{64}", recorded_cmd)):
        return UNKNOWN
    if ident.get("cmdline_sha256") and cs != ident["cmdline_sha256"]:
        return DEAD
    complete = (ident.get("boot_id") and ident.get("starttime_ticks") is not None and ident.get("cmdline_sha256")
                and ident.get("pidns") is not None and ident.get("timens") is not None)
    return ALIVE if complete else UNKNOWN


# ====================================================================== clocks, suspend and pause channels
def clocks() -> dict:
    """CLOCK_MONOTONIC stops during system suspend on Linux; CLOCK_BOOTTIME does not; CLOCK_REALTIME is wall time."""
    return {"monotonic_ns": time.clock_gettime_ns(time.CLOCK_MONOTONIC),
            "boottime_ns": time.clock_gettime_ns(time.CLOCK_BOOTTIME),
            "realtime_ns": time.clock_gettime_ns(time.CLOCK_REALTIME), "epoch_s": int(time.time())}


def _nint(text, *, signed: bool = False) -> int | None:
    """A bounded ASCII decimal text reading; malformed / unavailable evidence stays unknown."""
    if not isinstance(text, str):
        return None
    t = text.strip()
    if len(t.lstrip("-")) > 4300 or re.fullmatch(r"-?[0-9]+" if signed else r"[0-9]+", t) is None:
        return None
    try:
        return int(t)
    except ValueError:                           # includes the interpreter's configured integer-digit limit
        return None


def suspend_success_count(text: str | None = None) -> int | None:
    text = _read("/sys/power/suspend_stats/success") if text is None else text
    return _nint(text)


def snapshot(*, power_root="/sys/class/power_supply", suspend_text: str | None = None) -> dict:
    return {"clocks": clocks(), "boot_id": boot_id(), "suspend_success": suspend_success_count(suspend_text),
            "power": power_source(power_root)}


def assess(start: dict, end: dict, samples, journal_suspend_events) -> dict:
    """Fail-closed interval assessment (PROPOSED Linux counterpart of mbs308_host.assess; amendment row L-SLEEP).
    K' suspend (boottime − monotonic); S' suspend_stats count; L' journal entries (``None`` = no reader / unavailable;
    no journal reader exists in this module, so L' is always AMBIGUOUS here); P wall-vs-monotonic divergence
    (AMBIGUOUS only; NOT a pause detector: a hypervisor pause invisible to both guest clocks is silent, D-PAUSE);
    boot-id change; power at EVERY reading; sample spacing. CLEAN only if every channel exists and none fires."""
    reasons = []
    if not isinstance(start, dict) or not isinstance(end, dict):
        return {"status": "AMBIGUOUS", "clean": False, "reasons": ["AMBIGUOUS: endpoint record malformed"]}
    seq = [start, *(samples if isinstance(samples, list) else []), end]
    valid_clocks = all(isinstance(x, dict) and isinstance(x.get("clocks"), dict)
                       and all(type(x["clocks"].get(k)) is int and x["clocks"][k] >= 0
                               for k in ("monotonic_ns", "boottime_ns", "realtime_ns")) for x in seq)
    if not valid_clocks:
        reasons.append("AMBIGUOUS: clock records must contain nonnegative integer nanoseconds")
    try:
        if not valid_clocks:
            raise TypeError("invalid clock record")
        pairs = list(zip(seq, seq[1:]))
        if len(seq) > 2:
            pairs.append((start, end))
        for before, after in pairs:
            c0, c1 = before["clocks"], after["clocks"]
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
    counts = [x.get("suspend_success") if isinstance(x, dict) else None for x in seq]
    if any(type(count) is not int or count < 0 for count in counts):
        reasons.append("AMBIGUOUS: S' suspend_stats absent")
    elif any(before > after for before, after in zip(counts, counts[1:])):
        reasons.append("AMBIGUOUS: S' suspend count decreased or reset")
    elif any(before != after for before, after in zip(counts, counts[1:])):
        reasons.append("CONTAMINATED: S' suspend count changed")
    if any(not isinstance(x, dict) or type(x.get("suspend_success")) is not int
           or x["suspend_success"] < 0 for x in seq):
        reasons.append("AMBIGUOUS: a suspend counter reading is malformed")
    if not JOURNAL_READER_REVIEWED:
        reasons.append("AMBIGUOUS: L' no reviewed journal reader exists (whatever the caller passes, P7)")
    elif not isinstance(journal_suspend_events, list):
        reasons.append("AMBIGUOUS: L' journal unavailable")
    elif journal_suspend_events:
        reasons.append(f"CONTAMINATED: L' {len(journal_suspend_events)} suspend entries")
    boots = [x.get("boot_id") if isinstance(x, dict) else None for x in seq]
    if any(not isinstance(b, str) or boot_id(b) is None for b in boots):
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
        if not valid_clocks:
            raise TypeError("invalid sample clock record")
        ts = [x["clocks"]["monotonic_ns"] for x in seq]
        steps = [b - a for a, b in zip(ts, ts[1:])]
        if any(d < 0 for d in steps):
            reasons.append("AMBIGUOUS: samples out of order")
        elif not steps or max(steps) > MAX_SAMPLE_GAP_S * 10 ** 9:
            reasons.append("AMBIGUOUS: samples do not cover the interval")
    except (KeyError, TypeError):
        reasons.append("AMBIGUOUS: a sample carries no clocks")
    status = "CONTAMINATED" if any(r.startswith("CONTAMINATED") for r in reasons) else \
        ("AMBIGUOUS" if reasons else "CLEAN")
    return {"status": status, "clean": status == "CLEAN", "reasons": reasons}


# ====================================================================== power, thermal
def power_source(root="/sys/class/power_supply") -> str | None:
    """"AC": at least one Mains online, no Battery / UPS discharging, every supply readable and of a known type.
    "BATTERY": a Battery or UPS discharges. "NO_MAINS": readable supplies, no online Mains. "ABSENT": no supply at
    all (D-POWER-ABSENT). None (UNKNOWN): any unreadable type / online / status, or a type other than Mains, Battery,
    UPS (e.g. USB-C or wireless chargers: whether they count as AC is D-POWER-ABSENT) (F9); a Battery / UPS status
    other than Discharging or one of KNOWN_NOT_DISCHARGING (e.g. the kernel's "Unknown") is UNKNOWN (N2)."""
    try:
        entries = sorted(Path(root).iterdir())
    except OSError:
        return None
    if not entries:
        return "ABSENT"
    mains_online = discharging = False
    for e in entries:
        typ = (_read(e / "type") or "").strip()
        if typ == "Mains":
            on = (_read(e / "online") or "").strip()
            if on not in ("0", "1"):
                return None
            mains_online |= on == "1"
        elif typ in ("Battery", "UPS"):
            st = (_read(e / "status") or "").strip()
            if st == "Discharging":
                discharging = True
            elif st not in KNOWN_NOT_DISCHARGING:
                return None                                         # N2: "Unknown", garbage, unreadable: UNKNOWN
        else:
            return None
    if discharging:
        return "BATTERY"
    return AC if mains_online else "NO_MAINS"


def thermal_zones(root="/sys/class/thermal") -> list | None:
    """Raw zones only; no 'thermal-pressure level' is derived (D-THERMAL)."""
    try:
        zs = sorted(p for p in Path(root).iterdir() if p.name.startswith("thermal_zone"))
    except OSError:
        return None
    out = []
    for z in zs:
        t = _read(z / "temp")
        trips = []
        for tp in sorted(z.glob("trip_point_*_type")):
            k = tp.name[:-len("_type")]
            tv = _read(z / f"{k}_temp")
            trips.append({"type": (_read(tp) or "").strip(), "temp_mC": _nint(tv, signed=True)})
        out.append({"zone": z.name, "type": (_read(z / "type") or "").strip() or None,
                    "temp_mC": _nint(t, signed=True), "trips": trips})
    return out


# ====================================================================== memory and cgroups: RAW readings only
def meminfo(text: str | None = None) -> dict | None:
    text = _read("/proc/meminfo") if text is None else text
    if not text:
        return None
    out = {}
    for ln in text.splitlines():
        m = re.match(r"^([\w()]+):\s+(\d+)(?:\s+kB)?\s*$", ln)
        if m:
            out[m.group(1)] = int(m.group(2)) * (1024 if ln.rstrip().endswith("kB") else 1)
    return out or None


def _cg_val(path):
    text = _read(path)
    if isinstance(text, str) and text.strip() == "max":
        return "max"
    return _nint(text)


def _proc_cgroup_paths(text: str) -> tuple:
    v1 = v2 = None
    for ln in text.splitlines():
        parts = ln.split(":", 2)
        if len(parts) != 3:
            continue
        if "memory" in parts[1].split(","):
            v1 = parts[2]
        elif parts[0] == "0" and parts[1] == "":
            v2 = parts[2]
    return v1, v2


def memory_cgroup_chain(proc_cgroup_text: str | None = None, root="/sys/fs/cgroup") -> dict:
    """Leaf-to-root memory chain. v1: memory.limit_in_bytes / usage_in_bytes. v2: min(memory.max, memory.high) /
    memory.current; the v2 ROOT has no such files by design and is marked ``root=True`` with limit None. Unreadable
    values are None, never 'unlimited'."""
    text = _read("/proc/self/cgroup") if proc_cgroup_text is None else proc_cgroup_text
    if not text:
        return {"version": None, "chain": None, "reason": "/proc/self/cgroup unreadable"}
    v1, v2 = _proc_cgroup_paths(text)
    rootp = Path(root)
    if v1 is not None:
        version, base, rel = "v1", rootp / "memory", v1
    elif v2 is not None and (rootp / v2.lstrip("/") / "memory.current").exists():
        version, base, rel = "v2", rootp, v2
    else:
        return {"version": None, "chain": None, "reason": "no memory controller found"}
    parts = [p for p in rel.split("/") if p]
    chain = []
    for i in range(len(parts), -1, -1):
        d = base.joinpath(*parts[:i])
        if version == "v1":
            lim, use = _cg_val(d / "memory.limit_in_bytes"), _cg_val(d / "memory.usage_in_bytes")
            if isinstance(lim, int) and lim >= UNLIMITED_CGROUP_V1:
                lim = "max"
        elif i == 0:
            lim = use = None
        else:
            mx, hi = _cg_val(d / "memory.max"), _cg_val(d / "memory.high")
            use = _cg_val(d / "memory.current")
            if mx is None or hi is None:
                lim = None
            else:
                nums = [v for v in (mx, hi) if isinstance(v, int)]
                lim = min(nums) if nums else "max"
        chain.append({"path": "/" + "/".join(parts[:i]), "limit": lim, "usage": use, "root": i == 0})
    return {"version": version, "chain": chain}


def _chain_values(chain_rec: dict, *, root_attested: bool):
    """(limits, usages) over the chain, or None if any needed value is unreadable. The root level's v2 'no file' is
    accepted as 'no limit' only when root_attested (the visible root is the real root, H6 / D-HOST-LIFETIME)."""
    lims, uses = [], []
    for lvl in chain_rec.get("chain") or []:
        if lvl["root"] and chain_rec.get("version") == "v2":
            if root_attested is not True:
                return None
            continue
        if lvl["limit"] is None:
            return None
        lims.append(lvl["limit"])
        uses.append(lvl["usage"])
    return lims, uses


def _effective_memory_limit(chain_rec: dict, mem: dict | None, *, root_attested: bool = False) -> int | None:
    """min(MemTotal, every limit on the chain), NUMERIC ONLY if every level is readable AND the root is attested:
    ancestors hidden by a cgroup namespace cannot be seen by any reader (F10). Otherwise None (UNKNOWN)."""
    if root_attested is not True or not mem or "MemTotal" not in mem or not chain_rec.get("chain"):
        return None
    vals = _chain_values(chain_rec, root_attested=True)
    if vals is None:
        return None
    return min([mem["MemTotal"], *[v for v in vals[0] if isinstance(v, int)]])


def visible_limit_upper_bound(chain_rec: dict, mem: dict | None) -> int | None:
    """The same minimum over the VISIBLE chain, as a raw reading. Hidden ancestors can only lower the true allowance,
    so this is an upper bound and is never usable as an allowance."""
    if not mem or "MemTotal" not in mem or not chain_rec.get("chain"):
        return None
    vals = _chain_values(chain_rec, root_attested=True)
    if vals is None:
        return None
    return min([mem["MemTotal"], *[v for v in vals[0] if isinstance(v, int)]])


def _cgroup_min_headroom(chain_rec: dict, *, root_attested: bool = False) -> int | None:
    """min over limited levels of (limit − usage). None if the root is not attested or ANY level's limit, or any
    limited level's usage, is unreadable (F10: a partial chain never yields a number)."""
    if root_attested is not True:
        return None
    vals = _chain_values(chain_rec, root_attested=True)
    if vals is None:
        return None
    hs = []
    for lim, use in zip(*vals):
        if isinstance(lim, int):
            if not isinstance(use, int):
                return None
            hs.append(lim - use)
    return min(hs) if hs else None


def cgroup_resources(proc_cgroup_text: str | None = None, root="/sys/fs/cgroup") -> dict:
    """RAW cpu / cpuset / pids limits along the WHOLE chain of this process's cgroups, leaf to root (ROUTE_PREPARATION
    Phase 1 list; F10 / N3). v2: cpu.max, cpuset.cpus.effective, pids.max per level; v1: cpu.cfs_quota_us /
    cpu.cfs_period_us, cpuset.effective_cpus, pids.max per level. Unreadable values are None, never 'unlimited'."""
    text = _read("/proc/self/cgroup") if proc_cgroup_text is None else proc_cgroup_text
    out = {"v2": None, "v1": {}}
    if not text:
        return out
    ctl = {}
    for ln in text.splitlines():
        q = ln.split(":", 2)
        if len(q) == 3:
            for c in (q[1].split(",") if q[1] else ["unified"]):
                ctl[c] = q[2]
    rp = Path(root)

    def chain(base: Path, rel: str, names: tuple) -> list:
        parts = [x for x in rel.split("/") if x]
        rows = []
        for i in range(len(parts), -1, -1):
            d = base.joinpath(*parts[:i])
            rows.append({"path": "/" + "/".join(parts[:i]),
                         **{n: (_read(d / n) or "").strip() or None for n in names}})
        return rows
    if "unified" in ctl and (rp / ctl["unified"].lstrip("/") / "cgroup.controllers").exists():
        out["v2"] = chain(rp, ctl["unified"], ("cpu.max", "cpuset.cpus.effective", "pids.max"))
    for c, names in (("cpu", ("cpu.cfs_quota_us", "cpu.cfs_period_us")), ("cpuset", ("cpuset.effective_cpus",)),
                     ("pids", ("pids.max",))):
        if c in ctl and (rp / c).is_dir():
            out["v1"][c] = chain(rp / c, ctl[c], names)
    return out


def root_attestation(attestation_ref) -> tuple:
    """(True, []) only if ALL hold (P2): the reader's cgroup namespace is the INITIAL one (a non-initial or unreadable
    namespace hides ancestors, whatever any record says); D-HOST-LIFETIME is decided (DECIDED); attestation_valid()
    accepts the reference; and the committed attestation says ``root_cgroup_is_real: true``. Never a caller flag."""
    why = []
    if ns_inode("cgroup") != INIT_CGROUP_NS:
        why.append("cgroup namespace not the initial one, or unreadable")
    if "D-HOST-LIFETIME" not in _decided():
        why.append("D-HOST-LIFETIME open")
    rec, r = attestation_valid(attestation_ref) if not why else (None, [])
    why += r
    if not why and (not isinstance(rec, dict) or rec.get("root_cgroup_is_real") is not True):
        why.append("attestation does not state root_cgroup_is_real")
    return (not why), why


def memory_readings(mem_text: str | None = None, proc_cgroup_text: str | None = None, root="/sys/fs/cgroup",
                    *, attestation_ref=None) -> dict:
    """Every Linux candidate quantity side by side, none labelled as the R-FREE quantity (D-MEM-FREE, D-MEM-WIRED).
    effective_limit and headroom are numeric only if root_attestation(attestation_ref) holds (P2)."""
    mem = meminfo(mem_text)
    ch = memory_cgroup_chain(proc_cgroup_text, root)
    root_attested, why = root_attestation(attestation_ref)
    return {"meminfo_MemTotal": (mem or {}).get("MemTotal"), "meminfo_MemAvailable": (mem or {}).get("MemAvailable"),
            "meminfo_MemFree": (mem or {}).get("MemFree"), "meminfo_Inactive_file": (mem or {}).get("Inactive(file)"),
            "meminfo_SwapTotal": (mem or {}).get("SwapTotal"), "cgroup": ch,
            "root_attested": root_attested, "root_attestation_reasons": why,
            "cgroup_ns_initial": ns_inode("cgroup") == INIT_CGROUP_NS,
            "effective_limit": _effective_memory_limit(ch, mem, root_attested=root_attested),
            "visible_limit_upper_bound": visible_limit_upper_bound(ch, mem),
            "cgroup_min_headroom": _cgroup_min_headroom(ch, root_attested=root_attested),
            "note": "RAW Linux readings; none is the macOS vm_stat free+inactive+speculative+purgeable quantity of "
                    "R-FREE, and none is substituted for it (D-MEM-FREE, D-MEM-WIRED). effective_limit and headroom "
                    "are numeric only with a verified root attestation in the initial cgroup namespace (H6)."}


def psi_memory(text: str | None = None) -> dict | None:
    text = _read("/proc/pressure/memory") if text is None else text
    if not text:
        return None
    out = {}
    for ln in text.splitlines():
        k, *kv = ln.split()
        out[k] = {a: b for a, b in (x.split("=", 1) for x in kv)}
    return out or None


# ====================================================================== CPU exclusivity (windowed, from /proc)
def proc_view_complete(status_text: str | None = None, mountinfo_text: str | None = None,
                       pidns: int | None = -1) -> bool | None:
    """True only if this reader's PID namespace is the INITIAL one (inode INIT_PID_NS; N4: inside a nested namespace
    with its own /proc, NSpid shows one id and the view is partial), NSpid has one id, and /proc is mounted without
    hidepid / subset. False if any of these is positively violated; None if a reading fails or no /proc mount line is
    found (F13, N4). ``pidns`` (tests): the namespace inode; -1 = read it."""
    st = _read("/proc/self/status") if status_text is None else status_text
    mi = _read("/proc/self/mountinfo") if mountinfo_text is None else mountinfo_text
    ino = ns_inode("pid") if pidns == -1 else pidns
    if not isinstance(st, str) or not st or not isinstance(mi, str) or not mi or ino is None:
        return None
    if type(ino) is not int or ino <= 0:
        return None
    if ino != INIT_PID_NS:
        return False
    nspid_fields = [ln.partition(":")[2].split() for ln in st.splitlines() if ln.startswith("NSpid:")]
    if len(nspid_fields) != 1:
        return None
    nspid = nspid_fields[0]
    if len(nspid) > 1:
        return False
    if len(nspid) != 1 or not re.fullmatch(r"0*[1-9][0-9]*", nspid[0]):
        return None
    candidates = [ln.split() for ln in mi.splitlines() if len(ln.split()) > 4 and ln.split()[4] == "/proc"]
    if not candidates:
        return None
    if len(candidates) != 1:
        return False
    f = candidates[0]
    if not re.fullmatch(r"0*[1-9][0-9]*", f[0]) or not re.fullmatch(r"0*[1-9][0-9]*", f[1]) \
            or not re.fullmatch(r"[0-9]+:[0-9]+", f[2]):
        return None
    if "-" not in f:
        return None
    separator = f.index("-")
    if separator < 6 or len(f) < separator + 4 or f[3] != "/" or f[separator + 1] != "proc":
        return False
    opts = " ".join(f[5:])
    return not ("hidepid=" in opts or "subset=" in opts)


def cpu_ticks(proc_root="/proc") -> dict | None:
    """{(pid, starttime): (ppid, utime + stime ticks, comm, exe-or-None)}. Keyed by (pid, starttime) so pid reuse is a
    different process (F13). None if /proc is unreadable, or if a process that still exists cannot be read (N7: an
    unreadable process is never silently dropped). A process that vanished between listing and reading is skipped."""
    try:
        pids = [int(q.name) for q in Path(proc_root).iterdir() if q.name.isdigit()]
    except OSError:
        return None
    out = {}
    for pid in pids:
        st = proc_stat(pid, _read(f"{proc_root}/{pid}/stat") or "")
        if st is None:
            if Path(f"{proc_root}/{pid}").exists():
                return None
            continue
        try:
            exe = os.readlink(f"{proc_root}/{pid}/exe")
        except OSError:
            exe = None
        out[(pid, st["starttime"])] = (st["ppid"], st["utime"] + st["stime"], st["comm"], exe)
    return out


def busy_processes(t0: dict | None, t1: dict | None, dt_s: float, threshold_pct: float, own: set,
                   hz: int | None = None) -> list | None:
    """Processes whose CPU use within the window exceeds ``threshold_pct`` (100 = one CPU), plus every process present
    at t0 that EXITED before t1 (its usage in the window is unknown, so it is reported with pct None, N7). A process
    absent from t0 (born in the window, or a reused pid) is charged ALL its ticks to the window. ``own`` (the campaign
    tree) is a set of (pid, starttime) keys (N7); a child is exempt only if its parent key is in ``own`` and it started
    no earlier than that parent. Pid 0 / 1 may not be in ``own``. Nothing is allowed by name or path (D-ALLOW-PATHS).
    None (no reading) if a snapshot is missing, dt <= 0, ``own`` is malformed or unsafe, or a FRESH
    proc_view_complete() reading is not True (G6: the view is read here, never assumed by a default)."""
    if not isinstance(t0, dict) or not isinstance(t1, dict) or not isinstance(dt_s, (int, float)) \
            or isinstance(dt_s, bool) or abs(dt_s) > sys.float_info.max or not math.isfinite(dt_s) \
            or dt_s <= 0 or proc_view_complete() is not True:
        return None
    if not isinstance(threshold_pct, (int, float)) or isinstance(threshold_pct, bool) \
            or abs(threshold_pct) > sys.float_info.max or not math.isfinite(threshold_pct) or threshold_pct < 0:
        return None
    if not isinstance(own, (set, frozenset)) or not all(isinstance(k, tuple) and len(k) == 2 for k in own) \
            or any(k[0] in (0, 1) for k in own):
        return None
    hz = os.sysconf("SC_CLK_TCK") if hz is None else hz
    if type(hz) is not int or hz <= 0:
        return None
    def valid_key(key):
        return isinstance(key, tuple) and len(key) == 2 and type(key[0]) is int and key[0] > 0 \
            and type(key[1]) is int and key[1] >= 0
    if not all(valid_key(key) for key in own) or len({key[0] for key in own}) != len(own):
        return None
    for snapshot in (t0, t1):
        for key, record in snapshot.items():
            if not valid_key(key) or not isinstance(record, (list, tuple)) or len(record) != 4:
                return None
            if type(record[0]) is not int or record[0] < 0 or type(record[1]) is not int or record[1] < 0:
                return None
        if len({key[0] for key in snapshot}) != len(snapshot):
            return None
    if any(t1[key][1] < t0[key][1] for key in t0.keys() & t1.keys()):
        return None
    own_start = {pid: start for pid, start in own}
    def owned(key, ppid, snapshot):
        return key in own or (ppid in own_start and (ppid, own_start[ppid]) in snapshot
                              and key[1] >= own_start[ppid])
    out = []
    for (pid, start), (ppid, ticks1, comm, exe) in t1.items():
        if owned((pid, start), ppid, t1):
            continue
        prev = t0.get((pid, start))
        used = ticks1 - prev[1] if prev is not None else ticks1
        if used < 0:
            return None
        try:
            pct = 100.0 * used / hz / dt_s
        except OverflowError:
            return None
        if not math.isfinite(pct):
            return None
        if pct > threshold_pct:
            out.append({"pid": pid, "comm": comm, "exe": exe, "pct": round(pct, 1), "born_in_window": prev is None})
    for (pid, start), (ppid, _t, comm, exe) in t0.items():
        if (pid, start) not in t1 and not owned((pid, start), ppid, t0):
            out.append({"pid": pid, "comm": comm, "exe": exe, "pct": None, "exited_in_window": True})
    return out


# ====================================================================== OS update controls
def apt_config_dump() -> str | None:
    """Read-only `apt-config dump` (honours apt's own parsing: comments, nesting, ignored files, /etc/apt/apt.conf)."""
    try:
        p = subprocess.run(["apt-config", "dump"], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout if p.returncode == 0 else None


# G7: the system unit search path of systemd.unit(5), in precedence order
UNIT_ROOTS = ("/etc/systemd/system.control", "/run/systemd/system.control", "/run/systemd/transient",
              "/run/systemd/generator.early", "/etc/systemd/system", "/etc/systemd/system.attached",
              "/run/systemd/system", "/run/systemd/system.attached", "/run/systemd/generator",
              "/usr/local/lib/systemd/system", "/usr/lib/systemd/system", "/lib/systemd/system",
              "/run/systemd/generator.late")
UPDATE_UNITS = ("apt-daily-upgrade.timer", "unattended-upgrades.service")   # units that can INSTALL packages


def _systemctl_is_enabled(unit: str) -> str | None:
    return _systemctl_query("is-enabled", unit)


def _systemctl_is_active(unit: str) -> str | None:
    return _systemctl_query("is-active", unit)


def _systemctl_query(verb: str, unit: str) -> str | None:
    try:
        r = subprocess.run(["systemctl", verb, unit], capture_output=True, text=True, timeout=30,
                           stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() or None


def _unit_files(unit: str, unit_roots) -> bool | None:
    """True if a unit file (or link) for ``unit`` exists in any root; None if a root is unreadable."""
    found = False
    for root in unit_roots:
        r = Path(root)
        if not r.exists():
            continue
        if not r.is_dir():
            return None
        f = r / unit
        found |= f.is_symlink() or f.exists()
    return found


def unit_enabled(unit: str, unit_roots=UNIT_ROOTS) -> bool | None:
    """True / False / None (P8, G7, G9).

    With systemd as PID 1: True if ``systemctl is-active`` reports active / activating / reloading (a disabled unit
    can still be running, pulled in by another unit), or ``is-enabled`` reports enabled, enabled-runtime, static,
    indirect, alias, linked or linked-runtime; False only with recognized inactive / failed activity plus disabled /
    masked / masked-runtime, or not-found with no unit file in any root; None otherwise (a failed query is never
    'disabled').
    Without systemd: from every root of the unit search path: masked (the HIGHEST-precedence entry for the unit is a
    link to /dev/null; a lower-precedence mask is overridden, review 63 H6) False; otherwise an entry for the unit in
    any ``*.wants`` / ``*.requires`` / ``*.upholds`` directory, even a dangling link (systemd adds the dependency by
    link name), True; otherwise False; an unreadable root None."""
    supervisor = systemd_is_pid1()
    if supervisor is True:
        act = _systemctl_is_active(unit)
        if act in ("active", "activating", "reloading"):
            return True
        st = _systemctl_is_enabled(unit)
        if st in ("enabled", "enabled-runtime", "static", "indirect", "alias", "linked", "linked-runtime"):
            return True
        if st in ("disabled", "masked", "masked-runtime"):
            return False if act in ("inactive", "failed") else None
        if st == "not-found":
            if act not in ("inactive", "failed"):
                return None
            return False if _unit_files(unit, unit_roots) is False else None
        return None
    if supervisor is not False:
        return None
    first, wanted = None, False
    for root in unit_roots:
        r = Path(root)
        if not r.exists():
            continue
        try:
            subs = list(r.iterdir())
        except OSError:
            return None
        f = r / unit
        if first is None and (f.is_symlink() or f.exists()):
            first = f                                           # review 63 H6: the highest-precedence entry decides
        for d in subs:
            e = d / unit
            if d.name.endswith((".wants", ".requires", ".upholds")) and (e.is_symlink() or e.exists()):
                wanted = True
    if first is not None and first.is_symlink() and os.path.realpath(first) == "/dev/null":
        return False                                            # masked: no dependency can start it
    return wanted                                               # present without a link, or absent everywhere


def auto_update_settings(apt_dump: str | None = None, *, unit_roots=UNIT_ROOTS,
                         uu_binary="/usr/bin/unattended-upgrade", snapd_paths=("/usr/lib/snapd/snapd", "/snap"),
                         cloud_dir="/etc/cloud", livepatch_dir="/sys/kernel/livepatch", use_live_apt=True) -> dict:
    """Guest-visible update and reboot vectors (F11). ``guest_updates_shown_disabled`` is True only on POSITIVE
    evidence: apt-config readable and APT::Periodic::Enable "0" or APT::Periodic::Unattended-Upgrade "0" (apt then
    runs no unattended upgrade even if the binary is installed); no update unit enabled or of unknown state
    (UPDATE_UNITS, via unit_enabled, P8); no snapd; no
    cloud-init directory (it may upgrade packages at boot); no applied livepatch. Anything else: not shown disabled.
    ``provider_image_updates`` is UNKNOWN from inside a guest."""
    dump = (apt_config_dump() if use_live_apt else None) if apt_dump is None else apt_dump
    vals = {}
    for m in re.finditer(r'^APT::Periodic::([\w-]+)\s+"([^"]*)";\s*$', dump or "", re.M):
        vals[m.group(1)] = m.group(2)
    uu_cfg = {m.group(1): m.group(2) for m in
              re.finditer(r'^Unattended-Upgrade::([\w-]+)\s+"([^"]*)";\s*$', dump or "", re.M)}
    units = {}
    for u in UPDATE_UNITS:
        try:
            units[u] = unit_enabled(u, unit_roots)
        except OSError:                                         # review 64 K9: e.g. a root listable, not searchable
            units[u] = None
    timer = any(v is not False for v in units.values())         # enabled OR unknown: not shown disabled
    snapd = any(Path(p).exists() for p in snapd_paths)
    cloud = Path(cloud_dir).exists()
    try:
        livepatch = sorted(p.name for p in Path(livepatch_dir).iterdir())
    except OSError:
        livepatch = None if Path(livepatch_dir).exists() else []
    apt_off = dump is not None and (vals.get("Enable") == "0" or vals.get("Unattended-Upgrade") == "0")
    shown_disabled = bool(apt_off and not timer and not snapd and not cloud and livepatch == [])
    return {"apt_config_readable": dump is not None, "apt_periodic": vals,
            "unattended_automatic_reboot": uu_cfg.get("Automatic-Reboot"),
            "update_units": units, "update_unit_enabled_or_unknown": timer,
            "unattended_upgrade_present": Path(uu_binary).exists(),
            "snapd_present": snapd, "cloud_init_present": cloud, "livepatch_applied": livepatch,
            "guest_updates_shown_disabled": shown_disabled, "provider_image_updates": UNKNOWN}


# ====================================================================== supervisor / launch context
def systemd_is_pid1(comm_text: str | None = None, run_dir="/run/systemd/system") -> bool | None:
    comm = _read("/proc/1/comm") if comm_text is None else comm_text
    if comm is None:
        return None
    return comm.strip() == "systemd" and Path(run_dir).is_dir()


def launched_by_systemd(*, env=None, proc_cgroup_text: str | None = None, show=None, pid1=None,
                        prefix: str = CAMPAIGN_UNIT_PREFIX) -> dict:
    """PROPOSED replacement of mbs308_host.launched_by_launchd (row L-LAUNCH). PASS requires ALL of: systemd PID 1;
    own cgroup is a ``<prefix>*.service`` unit; INVOCATION_ID set; ``systemctl show`` MainPID == pid and the same
    InvocationID. Any failed reading: not pass."""
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
    if is1 is True and unit and inv:
        rec = (show or _systemctl_show)(unit)
    ok = bool(is1 is True and unit and inv and isinstance(rec, dict) and rec.get("MainPID") == os.getpid()
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
    """O_CREAT|O_EXCL|O_NOFOLLOW tmp in the same directory, write all, fsync the file, rename, fsync the directory,
    read back and verify. ``fault(stage)`` (tests) is a crash-injection hook at "written", "fsynced", "renamed".
    A pre-existing tmp raises StaleTmp (named state; never deleted here). Whether the device honours fsync across a
    power loss or VM reclaim is a host fact (H5), not something this function establishes."""
    p = Path(path)
    tmp = p.with_name(p.name + ".tmp")
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    except FileExistsError as exc:
        raise StaleTmp(f"STALE_TMP {tmp}: an earlier write was interrupted; record it, never delete it") from exc
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


# ====================================================================== platform pins (Linux, F1)
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


def mapped_objects(maps_text: str | None = None) -> dict | None:
    """{path: sha256} of every file-backed shared object mapped into THIS process (/proc/self/maps): the loader,
    libc, libm, libpython if loaded, and every extension module imported so far. The pin must therefore be taken
    AFTER the science's modules are imported (the pin point). None if maps is unreadable or a mapped file cannot be
    hashed."""
    text = _read("/proc/self/maps") if maps_text is None else maps_text
    if not text:
        return None
    paths = set()
    for ln in text.splitlines():
        f = ln.split(None, 5)
        if len(f) == 6 and f[5].startswith("/") and re.search(r"\.so(\.|$)", f[5]):
            paths.add(f[5].strip())
    out = {}
    for p in sorted(paths):
        h = _sha(_read(p, binary=True))
        if h is None:
            return None
        out[p] = h
    names = {Path(k).name for k in out}
    if not all(any(n == r or n.startswith(r) for n in names) for r in REQUIRED_MAPPED):
        return None                          # N11: a pin without libm, libc and the loader is not a pin
    return out


REQUIRED_MAPPED = ("libm.so.6", "libc.so.6", "ld-linux")   # N11: members every Linux pin must contain


def dpkg_versions(packages=("libc6",), query=None) -> dict:
    """{package: version or None} via read-only dpkg-query (None if dpkg is absent or the package is unknown)."""
    out = {}
    for pkg in packages:
        if query is not None:
            out[pkg] = query(pkg)
            continue
        try:
            p = subprocess.run(["dpkg-query", "-W", "-f=${Version}", pkg], capture_output=True, text=True, timeout=30,
                               stdin=subprocess.DEVNULL)
            out[pkg] = (p.stdout.strip() or None) if p.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            out[pkg] = None
    return out


def _python_packages(owner_query=None) -> tuple:
    """dpkg packages of the running interpreter: the package owning the executable (`dpkg -S`, read-only) and
    ``libpython<v>-stdlib``. An unknown owner is kept as a placeholder whose version reads None, so the pin never
    matches (fail closed; X09). ``owner_query()`` (tests) replaces the dpkg lookup."""
    v = f"{sys.version_info.major}.{sys.version_info.minor}"
    owner = None
    if owner_query is not None:
        return (owner_query() or UNKNOWN_PACKAGE, f"libpython{v}-stdlib")
    try:
        p = subprocess.run(["dpkg", "-S", os.path.realpath(sys.executable)], capture_output=True, text=True,
                           timeout=30, stdin=subprocess.DEVNULL)
        if p.returncode == 0 and ":" in p.stdout:
            owner = p.stdout.split(":", 1)[0].strip() or None
    except (OSError, subprocess.SubprocessError):
        owner = None
    return (owner or UNKNOWN_PACKAGE, f"libpython{v}-stdlib")


UNKNOWN_PACKAGE = "<unknown-interpreter-package>"


def pin_point() -> dict:
    """N11: read the pins at a fixed PIN POINT: every module of a fixed list (the science's imports, fixed in the
    accepted amendment) must already be imported by the caller with static ``import`` statements, so the mapped set
    does not depend on chance. This function imports nothing itself (the research quarantine scanner refuses dynamic
    imports it cannot resolve); a module of the list that is not loaded raises."""
    mods = PIN_POINT_MODULES                                 # G8: the fixed list only; no caller override
    if not mods:
        raise RuntimeError("PIN_POINT_UNDEFINED: no fixed module list (D-PIN-POINT is open)")    # P11
    missing = [m for m in mods if m not in sys.modules]
    if missing:
        raise RuntimeError(f"PIN_POINT_NOT_REACHED: not imported: {', '.join(missing)}")
    return platform_readings()


def platform_readings(maps_text: str | None = None) -> dict:
    """PROPOSED Linux pin set (row L-PIN): interpreter path + sha256; sys.version; every mapped shared object with its
    sha256 (covers libm.so.6 / libc.so.6 / the loader, the libraries RC2's determinism rests on); dpkg versions of
    libc6 and the interpreter's packages; livepatch state; os-release; kernel release; machine. CPU model and vCPU
    count are RECORDED (pinning them is a reviewer item)."""
    exe = os.path.realpath(sys.executable)
    osr = os_release() or {}
    cpu = None
    for ln in (_read("/proc/cpuinfo") or "").splitlines():
        if ln.startswith("model name"):
            cpu = ln.split(":", 1)[1].strip()
            break
    mo = mapped_objects(maps_text)
    try:
        lp = sorted(p.name for p in Path("/sys/kernel/livepatch").iterdir())
    except OSError:
        lp = None if Path("/sys/kernel/livepatch").exists() else []
    pkgs = dpkg_versions(("libc6", *_python_packages()))
    return {"python_executable": exe, "python_sha256": _sha(_read(exe, binary=True)),
            "python_sys_version": sys.version, "mapped_objects": mo,
            "libpython_mapped": None if mo is None else any("libpython" in k for k in mo),
            "dpkg_versions": pkgs, "livepatch": lp,
            "os_id": osr.get("ID"), "os_version_id": osr.get("VERSION_ID"), "os_version": osr.get("VERSION"),
            "kernel_release": _platform.release(), "machine": _platform.machine(),
            "glibc": os.confstr("CS_GNU_LIBC_VERSION") if hasattr(os, "confstr") else None,
            "recorded_cpu_model": cpu, "recorded_vcpus": os.cpu_count()}


PIN_KEYS = ("python_executable", "python_sha256", "python_sys_version", "mapped_objects", "dpkg_versions",
            "livepatch", "os_id", "os_version_id", "os_version", "kernel_release", "machine", "glibc")


def pin_mismatches(pins: dict, got: dict) -> list:
    """Keys whose value differs. A pin recorded as None (or containing None, e.g. an unknown package) never matches."""
    def unreadable(v):
        return v is None or (isinstance(v, dict) and (not v or any(x is None for x in v.values())))
    return [k for k in PIN_KEYS if unreadable(pins.get(k)) or got.get(k) != pins.get(k)]


# ====================================================================== disk
def free_disk_bytes(path) -> int | None:
    try:
        s = os.statvfs(path)
    except OSError:
        return None
    return s.f_bavail * s.f_frsize


# ====================================================================== host attestation (F8, F20, N1, P1)
# Review 64 K1: git reads are isolated from global / system configuration, replace refs and grafts, and the root
# (or shallow-boundary) commit is always shown; pickaxe searches also pass --no-textconv / --no-ext-diff (_commits).
# Repository-local configuration is still read. History completeness is a precondition (_history_complete): a shallow
# clone hides commits before its boundary, e.g. a rejecting review that was later deleted (review 64 follow-up).
_GIT_ISOLATION = ("--no-replace-objects", "-c", "log.showRoot=true")


def _git_env() -> dict:
    return dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM="1",
                GIT_GRAFT_FILE=os.devnull)


def _git(repo_root, *args) -> bytes | None:
    try:
        r = subprocess.run(["git", "-C", str(repo_root), *_GIT_ISOLATION, *args], capture_output=True, timeout=60,
                           stdin=subprocess.DEVNULL, env=_git_env())
    except (OSError, subprocess.SubprocessError, ValueError, UnicodeError):
        return None
    return r.stdout if r.returncode == 0 else None


def _history_complete(repo_root) -> bool:
    """True only on positive evidence that HEAD's history is complete in this repository: git reports it is not a
    shallow clone. A shallow clone, or no readable answer, is not evidence (the history-wide veto and the order rule
    both read the whole history; a cut history can hide a deleted rejection while the HEAD tree is identical)."""
    return _git(repo_root, "rev-parse", "--is-shallow-repository") == b"false\n"


def _strictly_after(repo_root, earlier: str | None, later: str | None) -> bool:
    """``later`` is a strict descendant of ``earlier`` on HEAD's history."""
    if not earlier or not later or earlier == later:
        return False
    try:
        r = subprocess.run(["git", "-C", str(repo_root), *_GIT_ISOLATION, "merge-base", "--is-ancestor", earlier,
                            later], capture_output=True, timeout=60, stdin=subprocess.DEVNULL, env=_git_env())
    except (OSError, subprocess.SubprocessError, ValueError, UnicodeError):
        return False
    return r.returncode == 0


_VERDICT = re.compile(r"(?i:.*\bverdict\b)|\s*[A-Z][A-Z0-9_]*\s*:\s*[A-Z][A-Z0-9_]*\s*$")   # review 63 H7
_NEGATIVE = re.compile(r"reject|withdraw|not[ _-]?accepted|revoke", re.I)
_NEGATIVE_MORE = re.compile(r"refus|unaccept|declin|needs[ _-]?revision|veto", re.I)          # review 63 H3
_HEX_TOKEN = re.compile(r"[0-9A-Fa-f]{8,64}")


def _names_sha(line: str, sha: str) -> bool:
    """Review 63 H3: a line refers to the attestation by its full sha256 anywhere (review 64 K4: also inside a longer
    hex run) or by any hex run of at least 8 digits that is a prefix of it, in either case."""
    return sha in line.lower() or any(sha.startswith(t.lower()) for t in _HEX_TOKEN.findall(line))


def _vetoing(lines: list, sha: str) -> bool:
    """A file that names the sha (H3: any case, >= 8-hex prefix) and anywhere carries a negative word (reject,
    withdraw, not accepted, revoke, refus*, unaccept*, declin*, needs revision, veto; case-insensitive) or a
    verdict-like line other than ACCEPTANCE_VERDICT_LINE vetoes the attestation."""
    if not any(_names_sha(ln, sha) for ln in lines):
        return False
    return any(_NEGATIVE.search(ln) or _NEGATIVE_MORE.search(ln)
               or (_VERDICT.match(ln) and ln != ACCEPTANCE_VERDICT_LINE) for ln in lines)


def _historical_review_blobs(repo_root, current: set) -> list | None:
    """Review 63 H3: every (blob, path) that existed under ACCEPTANCE_REVIEW_DIR in ANY commit of HEAD's full
    history (side branches included) and is not one of the ``current`` HEAD paths' blobs, with its UTF-8 lines. A
    rejection therefore survives `git rm`, `git mv` out of the directory and later edits. None if any listing or blob
    is unavailable or not UTF-8."""
    commits = _git(repo_root, "rev-list", "--full-history", "HEAD", "--", ACCEPTANCE_REVIEW_DIR)
    if commits is None:
        return None
    seen = {}
    for c in commits.decode("ascii", errors="replace").split():
        listing = _git(repo_root, "ls-tree", "-r", "-z", c, "--", ACCEPTANCE_REVIEW_DIR)
        if listing is None or (listing and not listing.endswith(b"\0")):
            return None
        for entry in filter(None, listing.split(b"\0")):
            meta, sep, name = entry.partition(b"\t")
            parts = meta.split()
            if not sep or len(parts) != 3:
                return None
            if parts[1] != b"blob":
                continue
            try:
                seen.setdefault(parts[2].decode("ascii"), name.decode("utf-8", errors="strict"))
            except UnicodeDecodeError:
                return None
    out = []
    for oid, path in seen.items():
        if oid in current:
            continue
        data = _git(repo_root, "cat-file", "blob", oid)
        if data is None:
            return None
        try:
            out.append((oid, path, [ln.rstrip("\r") for ln in data.decode("utf-8", errors="strict").split("\n")]))
        except UnicodeDecodeError:
            return None
    return out


def _tree_entries(repo_root, paths: list) -> dict | None:
    """{path: (mode, type, object id)} for exactly ``paths`` at HEAD, from `ls-tree -z HEAD -- <paths>` (review 64
    K9: names such as `x..HEAD` are path specs here, never revision ranges); None if unreadable or malformed."""
    if not paths:
        return {}
    data = _git(repo_root, "ls-tree", "-z", "HEAD", "--", *paths)
    if data is None or (data and not data.endswith(b"\0")):
        return None
    out = {}
    for entry in filter(None, data.split(b"\0")):
        meta, sep, name = entry.partition(b"\t")
        parts = meta.split()
        if not sep or len(parts) != 3:
            return None
        try:
            out[name.decode("utf-8", errors="strict")] = tuple(x.decode("ascii") for x in parts)
        except UnicodeDecodeError:
            return None
    return out


def _review_paths(data: bytes | None) -> list | None:
    """Git -z names are whole paths, never quoted or split on tab/newline; bad evidence refuses verification."""
    if not isinstance(data, bytes) or (data and not data.endswith(b"\0")):
        return None
    if not data:
        return []
    try:
        paths = [path.decode("utf-8", errors="strict") for path in data[:-1].split(b"\0")]
    except UnicodeDecodeError:
        return None
    return paths if all(paths) else None


def _acceptances(repo_root, sha: str) -> tuple:
    """G1-G3. The fixed set: DIRECT children of ACCEPTANCE_REVIEW_DIR, committed at HEAD, named
    ``REVIEW_HOST_ATTESTATION_*.md`` (no subdirectory, so no reviewer scratch). A file accepts only if it holds the
    exact line ``HOST_ATTESTATION_ACCEPTED sha256=<sha>`` and exactly ONE verdict-like line (any line containing the
    word "verdict" in any case, or a bare ``KEY: VALUE`` line of capitals; review 63 H7), which is
    ACCEPTANCE_VERDICT_LINE. Any file anywhere under the review directory (recursively) that names the sha and vetoes
    it (_vetoing) rejects it, whether committed at HEAD or present in ANY commit of HEAD's full history (review 63 H3:
    a rejection is permanent; removing or moving the file, or editing it, does not lift it).
    A shallow clone, or a repository whose completeness cannot be read, refuses as unavailable evidence.
    Returns (accepting paths, rejecting paths). Unavailable or unrecognized review evidence returns no acceptances
    and an explicit unavailable-evidence sentinel in the rejecting list; it can never establish verification.
    """
    if not _history_complete(repo_root):
        return [], ["UNAVAILABLE: history completeness not established (shallow clone or unreadable)"]
    tree = _review_paths(_git(repo_root, "ls-tree", "-z", "--name-only", "HEAD", f"{ACCEPTANCE_REVIEW_DIR}/"))
    every = _review_paths(_git(repo_root, "ls-tree", "-r", "-z", "--name-only", "HEAD", "--", ACCEPTANCE_REVIEW_DIR))
    if tree is None or every is None:
        return [], ["UNAVAILABLE: acceptance review listing unreadable or malformed"]
    acc, rej, records = [], [], {}
    for path in every:
        data = _git(repo_root, "cat-file", "blob", f"HEAD:{path}")    # review 64 K9: never a revision range
        if data is None:
            return [], [f"UNAVAILABLE: review blob unreadable: {path}"]
        try:
            lines = [ln.rstrip("\r") for ln in data.decode("utf-8", errors="strict").split("\n")]
        except UnicodeDecodeError:
            return [], [f"UNAVAILABLE: review blob is not UTF-8: {path}"]
        records[path] = lines
        if _vetoing(lines, sha):
            rej.append(path)
    entries = _tree_entries(repo_root, every)
    if entries is None or set(entries) != set(every):
        return [], ["UNAVAILABLE: current review blob ids unreadable"]
    current = {oid for mode, kind, oid in entries.values()}
    history = _historical_review_blobs(repo_root, current)
    if history is None:
        return [], ["UNAVAILABLE: review history unreadable or not UTF-8"]
    rej += [f"HISTORICAL: {path} (blob {oid[:12]})" for oid, path, lines in history if _vetoing(lines, sha)]
    for path in tree:
        name = Path(path).name
        if not (name.startswith(ACCEPTANCE_REVIEW_PREFIX) and name.endswith(".md")) or path in rej:
            continue
        if path not in records:
            return [], [f"UNAVAILABLE: accepting review absent from recursive listing: {path}"]
        lines = records[path]
        if entries[path][:2] not in (("100644", "blob"), ("100755", "blob")):
            continue                                            # review 64 K7: a symlink is not a review file
        verdicts = [ln for ln in lines if _VERDICT.match(ln)]
        if f"{ACCEPTANCE_LINE}{sha}" in lines and verdicts == [ACCEPTANCE_VERDICT_LINE]:
            acc.append(path)
    return acc, rej


def _commits(repo_root, *args) -> list | None:
    """Every commit of the selected history matched by ``args``, merge commits included (their diff against EACH
    parent, `--diff-merges=separate`; git's default shows no merge diff, so a blob or line introduced by a merge would
    be invisible: review 63 H1); de-duplicated; None if git fails or prints anything but commit ids."""
    out = _git(repo_root, "log", "--format=%H", "--no-patch", "--no-textconv", "--no-ext-diff",
               "--diff-merges=separate", *args)
    if out is None:
        return None
    try:
        ids = out.decode("ascii").split()
    except UnicodeDecodeError:
        return None
    if not all(re.fullmatch(r"[0-9a-f]{40,64}", c) for c in ids):
        return None
    return list(dict.fromkeys(ids))


def _ordered(repo_root, att_path: str, acc_path: str, sha: str) -> bool:
    """G2 / review 63 H1: EVERY commit of HEAD's history that adds or removes the attested BLOB (by object id, not by
    path name) is a strict ancestor of EVERY commit that adds or removes the ACCEPTING LINE anywhere in the
    repository; merge commits count on both sides, and no commit is chosen by date. The search is repository-wide on
    purpose: a line written next to the attestation and later moved (git mv) into ``acc_path`` keeps its true commits,
    and a line can enter ``acc_path`` only by an addition (a repository-wide change, so covered) or by a move of an
    earlier one; a path-limited search would see the move instead. Side effects (fail-closed): a quote of the line
    made before or beside the blob, or a later re-introduction of the blob, refuses permanently; any git failure
    refuses. Commit order is not independence: every
    commit may come from one author (a reviewer / ledger binding is a carried condition of D-HOST-LIFETIME)."""
    blob = (_git(repo_root, "rev-parse", f"HEAD:{att_path}") or b"").decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40,64}", blob):
        return False
    pick = f"-S{ACCEPTANCE_LINE}{sha}"
    blob_commits = _commits(repo_root, f"--find-object={blob}", "HEAD")
    line_commits = _commits(repo_root, pick, "HEAD")
    if not blob_commits or not line_commits:
        return False
    return all(_strictly_after(repo_root, b, c) for b in blob_commits for c in line_commits)


def _repository_root() -> Path:
    """Canonical repository containing this development platform; a private reader seam for synthetic tests."""
    return Path(__file__).resolve().parents[5]


def attestation_valid(ref, *, repo_root=None) -> tuple:
    """(record or None, reasons). ``ref`` = exactly {"path", "sha256"}; every fact is read from committed files, none
    from the caller. Valid only if: the file is committed at HEAD with that sha256; it is JSON with schema
    ATTESTATION_SCHEMA, ``reviewed is True``, ``accepted is True`` and a ``machine`` equal to the current hardware-bound
    machine_identity() (BOTH hashes, F20); at least one acceptance review exists in the fixed review set (P1 / G1 / G3:
    _acceptances; never a path the attestation names) whose accepting line was introduced strictly after the attested
    blob (G2: _ordered), and no review under the review directory rejects it.
    ``repo_root`` is a TEST SEAM (default: this repository). It selects which repository's committed files are read,
    so a caller-chosen repository can supply its own attestation and reviews (review 63 H5): a reviewed caller never
    passes it, and the restricted observer binds the canonical repository internally."""
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
        return None, ["reference must be exactly {path, sha256}"]
    path, want = ref["path"], ref["sha256"]
    if not isinstance(path, str) or not isinstance(want, str) or not re.fullmatch(r"[0-9a-f]{64}", want):
        return None, ["malformed reference"]
    base = Path(repo_root) if repo_root else _repository_root()
    data = _git(base, "cat-file", "blob", f"HEAD:{path}")            # review 64 K9: never a revision range
    if data is None:
        return None, ["attestation not committed at HEAD"]
    if _sha(data) != want:
        return None, ["attestation not committed at HEAD, or sha256 mismatch"]
    try:
        rec = json.loads(data)
    except (ValueError, UnicodeDecodeError):
        return None, ["attestation is not JSON"]
    if not isinstance(rec, dict) or rec.get("schema") != ATTESTATION_SCHEMA:
        return None, ["wrong or missing schema"]
    reasons = []
    if rec.get("reviewed") is not True or rec.get("accepted") is not True:
        reasons.append("not reviewed and accepted (strict True, read from the file)")
    cur = machine_identity()
    if not cur.get("hardware_bound") or rec.get("machine") != cur:
        reasons.append("not bound to this hardware identity (both hashes)")
    acc, rej = _acceptances(base, want)
    if rej:
        reasons.append(f"rejected by {', '.join(rej)}")
    acc = [a for a in acc if _ordered(base, path, a, want)]
    if not acc:
        reasons.append("no acceptance review in the fixed set whose accepting line post-dates the attested blob")
    return (rec if not reasons else None), reasons


# ====================================================================== preflight (PROPOSED Linux gate set)
def _g(v: bool | None) -> str:
    return UNKNOWN if v is None else (PASS if v else FAIL)


_GATE_DECISION = {"ac_power": "D-POWER-ABSENT", "lowpowermode_0": "D-LPM", "thermal_pressure_0": "D-THERMAL",
                  "memory_pressure_normal": "D-MEM-PRESSURE", "free_memory_ge_min": "D-MEM-FREE",
                  "host_exclusive": ("D-EXCL-WINDOW", "D-ALLOW-PATHS", "D-ALLOW-BASE39"),
                  "host_lifetime_attested": "D-HOST-LIFETIME",
                  "no_automatic_os_install": "D-HOST-LIFETIME"}
MODES = ("launcher_preflight", "execute", "resume")


def _decided() -> frozenset:
    """P5: the module constant DECIDED, validated: a frozenset of known D-* ids (OPEN_DECISIONS), else an error."""
    if not isinstance(DECIDED, frozenset) or not DECIDED <= frozenset(OPEN_DECISIONS):
        raise ValueError("DECIDED must be a frozenset of known D-* ids")
    return DECIDED


def launch_record_ok(rec) -> bool:
    """N12: every field shows a systemd launch of THIS process; MainPID an int (not bool / float)."""
    if not isinstance(rec, dict):
        return False
    sc = rec.get("systemctl")
    unit = rec.get("unit")
    mp = sc.get("MainPID") if isinstance(sc, dict) else None
    return bool(rec.get("systemd_pid1") is True and isinstance(unit, str) and unit.startswith(CAMPAIGN_UNIT_PREFIX)
                and unit.endswith(".service") and isinstance(rec.get("invocation_id"), str) and rec["invocation_id"]
                and isinstance(mp, int) and not isinstance(mp, bool) and mp == os.getpid()
                and sc.get("InvocationID") == rec["invocation_id"] and rec.get("pass") is True)


def preflight(repo_path, *, mode: str, other_job_running: bool | None, launched: dict | None,
              attestation_ref: dict | None) -> dict:
    """The Linux gate set (amendment §3). Gates that depend on an open D-* decision are OPEN_DECISION while it is not
    in the validated module constant DECIDED (empty in development); that applies to host_lifetime_attested and the
    provider-image half of no_automatic_os_install (N1, P5). The launch gate is evaluated for execute / resume, and
    whenever a record is passed: PASS only if a FRESH launched_by_systemd() reading verifies (launch_record_ok) and any
    passed record equals it (P6). Every host reading is taken inside (G5); the caller inputs are ``mode``,
    ``other_job_running`` (from the reviewed launcher's pidfile check, as in the candidate), the ``launched`` record
    (only compared with a fresh reading) and ``attestation_ref`` (only a pointer to committed files). pass == every
    gate PASS."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    decided = _decided()
    power = power_source()                                  # G5: every reading is taken here, none is supplied
    free = free_disk_bytes(repo_path)
    boot = boot_id()
    upd = auto_update_settings()
    att, att_reasons = attestation_valid(attestation_ref)
    lifetime_open = "D-HOST-LIFETIME" not in decided
    if not isinstance(upd, dict) or upd.get("guest_updates_shown_disabled") is not True:
        upd_gate = UNKNOWN                                      # guest vectors not shown disabled (or no reading)
    elif lifetime_open:
        upd_gate = OPEN_DECISION                                # provider image half: D-HOST-LIFETIME open (N1)
    else:
        upd_gate = PASS if isinstance(att, dict) and att.get("provider_image_updates") == NO_IMAGE_CHANGE else UNKNOWN
    gates = {
        "ac_power": OPEN_DECISION if power == "ABSENT" else _g(None if power is None else power == AC),
        "lowpowermode_0": OPEN_DECISION,
        "thermal_pressure_0": OPEN_DECISION,
        "free_disk_ge_2GiB": _g(None if not isinstance(free, int) or isinstance(free, bool)
                                else free >= MIN_FREE_DISK),
        "memory_pressure_normal": OPEN_DECISION,
        "free_memory_ge_min": OPEN_DECISION,
        "boot_id_recorded": _g(None if not isinstance(boot, str) or boot_id(boot) is None else True),
        "no_other_campaign_job": _g(None if other_job_running is None else other_job_running is False),
        "no_automatic_os_install": upd_gate,
        "host_exclusive": OPEN_DECISION,
        "host_lifetime_attested": OPEN_DECISION if lifetime_open else (PASS if isinstance(att, dict) else UNKNOWN),
    }
    fresh = None
    if mode in ("execute", "resume") or launched is not None:
        fresh = launched_by_systemd()
        ok = launch_record_ok(fresh) and (launched is None or launched == fresh)
        gates["launched_by_systemd"] = PASS if ok else FAIL
    blocked = {k: v for k, v in gates.items() if v != PASS}
    return {"mode": mode, "gates": gates, "pass": not blocked, "blocked": blocked,
            "readings": {"power": power, "free_disk_bytes": free, "boot_id": boot, "updates": upd,
                         "launched": launched, "launched_fresh": fresh, "attestation_reasons": att_reasons},
            "open_decisions": sorted({d for k, v in gates.items() if v == OPEN_DECISION
                                      for d in ((_GATE_DECISION[k],) if isinstance(_GATE_DECISION[k], str)
                                                else _GATE_DECISION[k])})}
