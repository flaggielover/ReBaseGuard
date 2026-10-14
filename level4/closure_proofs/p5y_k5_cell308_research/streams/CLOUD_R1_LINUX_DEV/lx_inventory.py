"""Cell-308 new-host route (Claude Cloud, r1) -- read-only host inventory, r2 (DEV stream; INFRASTRUCTURE class).

Reads /proc, /sys, /etc and interpreter files only, through lx_platform's readers, and compares the result field by
field with the 2026-10-04 inventory (governance/new_host_route_cloud_r1/CLOUD_HOST_INVENTORY.json). Runs no workload,
no benchmark, no decoy, no cell; installs nothing; changes no setting. Not designated evidence.

usage: python3 lx_inventory.py <out.json>
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lx_platform as L  # noqa: E402

NS = HERE.parent.parent
R1 = NS / "governance" / "new_host_route_cloud_r1" / "CLOUD_HOST_INVENTORY.json"


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def interpreters() -> list:
    out = []
    for p in sorted(Path("/usr/bin").glob("python3.[0-9]*")):
        if p.name.endswith("-config") or not os.access(p, os.X_OK):
            continue
        try:
            v = subprocess.run([str(p), "-c", "import sys;print(sys.version.split()[0])"], capture_output=True,
                               text=True, timeout=30).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            v = None
        rp = os.path.realpath(p)
        out.append({"path": str(p), "resolves_to": rp, "version": v,
                    "sha256": hashlib.sha256(Path(rp).read_bytes()).hexdigest()})
    return out


def co_resident() -> list:
    rows = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        st = L.proc_stat(int(d.name), L._read(d / "stat") or "")
        status = L._read(d / "status") or ""
        rss = next((int(x.split()[1]) * 1024 for x in status.splitlines() if x.startswith("VmRSS:")), None)
        if st and rss and rss >= 20 * 1024 ** 2:
            rows.append({"comm": st["comm"], "pid": st["pid"], "rss_bytes": rss})
    return sorted(rows, key=lambda r: -r["rss_bytes"])


def main(out: str) -> int:
    t0 = utc()
    mem = L.memory_readings()
    osr = L.os_release() or {}
    cpu_model = next((ln.split(":", 1)[1].strip() for ln in (L._read("/proc/cpuinfo") or "").splitlines()
                      if ln.startswith("model name")), None)
    pins = L.platform_readings()
    inv = {
        "schema": "rebaseguard.p5y.k5.newhost-cloud-r1.host-inventory.v2",
        "class": "INFRASTRUCTURE", "not_designated_evidence": True,
        "new_target_evaluations": 0, "proxy_evaluations": 0, "cell309_activity": "none",
        "benchmarks_run": False, "decoys_run": False, "packages_installed": False, "system_changed": False,
        "collected_utc": {"first": t0},
        "tool": {"path": "streams/CLOUD_R1_LINUX_DEV/lx_inventory.py",
                 "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 "lx_platform_sha256": hashlib.sha256((HERE / "lx_platform.py").read_bytes()).hexdigest()},
        "platform": {"kernel_release": pins["kernel_release"], "machine": pins["machine"], "glibc": pins["glibc"],
                     "os": osr.get("PRETTY_NAME"), "pid1": (L._read("/proc/1/cmdline", binary=True) or b"")
                     .replace(b"\0", b" ").decode(errors="replace").strip()},
        "python": {"default_python3": os.path.realpath("/usr/bin/python3"), "interpreters": interpreters(),
                   "python3.14_present": Path("/usr/bin/python3.14").exists()},
        "cpu": {"model": cpu_model, "online_vcpus": os.cpu_count(), "affinity": sorted(os.sched_getaffinity(0)),
                "cgroup_v1_cfs_quota_us_root": (L._read("/sys/fs/cgroup/cpu/cpu.cfs_quota_us") or "").strip() or None,
                "host_side_quota_or_overcommit": "UNKNOWN"},
        "memory": mem,
        "psi_memory": L.psi_memory(),
        "storage": {"root_free_bytes_statvfs": L.free_disk_bytes("/"),
                    "block_queue_write_cache": (L._read("/sys/block/vda/queue/write_cache") or "").strip() or None},
        "boot": {"boot_id": L.boot_id(), "uptime_s": float((L._read("/proc/uptime") or "0").split()[0])},
        "supervisor": {"systemd_pid1": L.systemd_is_pid1(), "launched_by_systemd": L.launched_by_systemd()},
        "power_source": L.power_source(), "thermal_zones": L.thermal_zones(),
        "suspend_success_count": L.suspend_success_count(),
        "clocksource": (L._read("/sys/devices/system/clocksource/clocksource0/current_clocksource") or "").strip(),
        "auto_update": L.auto_update_settings(),
        "linux_platform_pins_as_proposed": pins,
        "co_resident_processes_rss_ge_20MiB": co_resident(),
        "dev_preflight_PROPOSED_gate_set": L.preflight("/", other_job_running=None, launched=L.launched_by_systemd(),
                                                       host_attestation=None),
    }
    # ---- field-by-field comparison with the 2026-10-04 inventory (same provider, a different session)
    old = json.loads(R1.read_text())
    old_py = {i["path"]: i for i in old["python"]["interpreters"]}
    new_py = {i["path"]: i for i in inv["python"]["interpreters"]}
    cmp_rows = [
        ("cpu model", old["cpu"]["model"], cpu_model),
        ("online vCPUs", old["cpu"]["online_vcpus"], os.cpu_count()),
        ("kernel", old["platform"]["kernel"], pins["kernel_release"]),
        ("OS", old["platform"]["os"], osr.get("PRETTY_NAME")),
        ("MemTotal bytes", old["memory"]["MemTotal_bytes"], mem["meminfo_MemTotal"]),
        ("leaf cgroup memory limit bytes", old["memory"]["effective_allowance_for_processes_started_from_this_shell"
                                                          "_bytes"], mem["effective_limit"]),
        ("python interpreters", sorted(f"{p}={i['version']}" for p, i in old_py.items()),
         sorted(f"{p}={i['version']}" for p, i in new_py.items())),
        ("boot_id", old["boot_and_lifetime"]["boot_id"], inv["boot"]["boot_id"]),
    ]
    inv["comparison_with_r1_20261004"] = [{"field": f, "r1_20261004": a, "r2_now": b, "same": a == b}
                                          for f, a, b in cmp_rows]
    inv["collected_utc"]["last"] = utc()
    Path(out).write_text(json.dumps(inv, indent=1, sort_keys=False) + "\n")
    print(json.dumps(inv["comparison_with_r1_20261004"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
