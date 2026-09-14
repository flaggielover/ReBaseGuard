"""Read-only host facts for the new-glibc successor: identity, system libraries, packages, boot, containment, idle.

NON-CERTIFYING. Nothing here writes to the host. The containment collector reproduces, field for field, the
collector that recorded evidence/containment/{PRE,POST,POST_RUN}_STATE.json (label and utc are not compared).
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import gs_schema as GS
from prod_common import boot_id, host_facts

UNITS = ["apt-daily.timer", "apt-daily-upgrade.timer", "apt-daily.service", "apt-daily-upgrade.service",
         "unattended-upgrades.service", "apt-listchanges.timer", "apt-listchanges.service"]
DROPIN = Path("/etc/apt/apt.conf.d/99-rebaseguard-cusum-freeze")


def _run(*argv) -> str:
    try:
        return subprocess.run(list(argv), capture_output=True, text=True, timeout=60).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _sha(p):
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def library_hashes() -> dict:
    return {p: _sha(p) for p in GS.SYSTEM_LIBRARIES}


def package_versions() -> dict:
    return {k: (_run("dpkg-query", "-W", "-f=${Version}", k) or None) for k in GS.PACKAGES}


def full_host_identity() -> dict:
    facts = host_facts(with_package=True)
    facts["system_libraries_sha256"] = library_hashes()
    facts["packages"] = package_versions()
    facts["boot_id"] = boot_id()
    return facts


def containment_state() -> dict:
    return {
        "host_name": os.uname().nodename,
        "units": {u: {"enabled": _run("systemctl", "is-enabled", u), "active": _run("systemctl", "is-active", u)}
                  for u in UNITS},
        "apt_config": [l for l in _run("apt-config", "dump").splitlines()
                       if l.startswith(("APT::Periodic", "Unattended-Upgrade::"))],
        "apt_conf_d_sha256": {p.name: _sha(p) for p in sorted(Path("/etc/apt/apt.conf.d").iterdir())}
        if Path("/etc/apt/apt.conf.d").is_dir() else {},
        "freeze_dropin": {"path": str(DROPIN), "exists": DROPIN.is_file(),
                          "content": DROPIN.read_text() if DROPIN.is_file() else None},
        "holds": sorted(_run("apt-mark", "showhold").split()),
        "other_managers": {"packagekit": bool(_run("dpkg-query", "-W", "-f=${Version}", "packagekit")),
                           "snapd": bool(_run("dpkg-query", "-W", "-f=${Version}", "snapd"))},
        "kernel_release": os.uname().release,
        "system_libraries_sha256": library_hashes(),
    }


def containment_problems(bound_post: dict, live: dict) -> list[str]:
    return [f"CONTAINMENT: {k} differs from the bound POST_STATE" for k in GS.CONTAINMENT_KEYS
            if live.get(k) != bound_post.get(k)]


def identity_problems(bound: dict, live: dict) -> list[str]:
    p = [f"HOST: {k} live {live.get(k)!r} != bound {v!r}" for k, v in bound["bound_facts"].items() if live.get(k) != v]
    for path, h in bound["system_libraries_sha256"].items():
        if (live.get("system_libraries_sha256") or {}).get(path) != h:
            p.append(f"HOST: system library {path} differs")
    if live.get("packages") != bound["packages"]:
        p.append("HOST: package versions differ")
    if live.get("boot_id") != bound["boot_id"]:
        p.append(f"HOST: boot id {live.get('boot_id')!r} != bound {bound['boot_id']!r} (reboot or provider maintenance)")
    return p


# ------------------------------------------------------------------ processes (no self-matching)
def _ppid(pid: int):
    try:
        raw = Path(f"/proc/{pid}/stat").read_text()
        return int(raw[raw.rindex(")") + 2:].split()[1])
    except (OSError, ValueError, IndexError):
        return None


def self_lineage() -> set:
    out, pid = set(), os.getpid()
    while pid and pid not in out:
        out.add(pid)
        pid = _ppid(pid)
    return out


def classify_argv(argv: list) -> str | None:
    """A campaign process iff an argv ELEMENT's basename is a certifier/supervisor/worker script, or an entry script
    followed by a live command. A diagnostic shell whose single `-c` string merely mentions a script never matches."""
    names = [os.path.basename(a) for a in argv]

    def interpreted(i: int) -> bool:        # the script is executed: an interpreter element precedes it, or it is argv[0]
        return i == 0 or any(n.startswith("python") or n in ("bash", "sh", "dash") for n in names[:i])
    for i, n in enumerate(names):
        if not interpreted(i):
            continue
        if n in GS.CERTIFIER_BASENAMES:
            return "CERTIFIER"
        if n in GS.SUPERVISOR_BASENAMES:
            return "SUPERVISOR_OR_WORKER"
        if n in GS.ENTRY_BASENAMES and i + 1 < len(argv) and argv[i + 1] in GS.ENTRY_LIVE_COMMANDS:
            return "ENTRY_LIVE"
    return None


def foreign_campaign_processes(skip=()) -> list[dict]:
    skip = self_lineage() | set(skip)
    out = []
    for d in Path("/proc").glob("[0-9]*"):
        pid = int(d.name)
        if pid in skip:
            continue
        try:
            argv = [x.decode(errors="replace") for x in (d / "cmdline").read_bytes().split(b"\0") if x]
        except OSError:
            continue
        kind = classify_argv(argv)
        if kind:
            out.append({"pid": pid, "kind": kind, "argv": [a[:120] for a in argv[:6]]})
    return out
