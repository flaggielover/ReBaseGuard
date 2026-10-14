"""Cell-308 new-host route (Claude Cloud, r1) -- read-only host inventory (DEV stream; INFRASTRUCTURE class).

Revision 2 (review 59, F19): the comparison with r1 is NORMALISED (model / kernel / OS strings stripped of suffixes,
interpreters compared per minor version through their resolved paths); adds the libc6 package version, the cgroup
cpu / cpuset / pids limits, the root mount, the hashed machine identity and the /proc-view check.

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
import re
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


def root_mount() -> dict | None:
    for ln in (L._read("/proc/self/mountinfo") or "").splitlines():
        f = ln.split()
        if len(f) > 9 and f[4] == "/":
            sep = f.index("-")
            return {"mount_options": f[5], "fstype": f[sep + 1], "source": f[sep + 2], "super_options": f[sep + 3]}
    return None


def main(out: str) -> int:
    t0 = utc()
    mem = L.memory_readings()
    osr = L.os_release() or {}
    cpu_model = next((ln.split(":", 1)[1].strip() for ln in (L._read("/proc/cpuinfo") or "").splitlines()
                      if ln.startswith("model name")), None)
    pins = L.platform_readings()
    inv = {
        "schema": "rebaseguard.p5y.k5.newhost-cloud-r1.host-inventory.v3",
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
        "cgroup_resources": L.cgroup_resources(),
        "dpkg_versions": pins["dpkg_versions"],
        "machine_identity_hashed": L.machine_identity(),
        "proc_view_complete": L.proc_view_complete(),
        "root_mount": root_mount(),
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
        "dev_preflight_PROPOSED_gate_set": L.preflight("/", mode="execute", other_job_running=None,
                                                       launched=L.launched_by_systemd(), attestation_ref=None),
    }
    # ---- field-by-field comparison with the 2026-10-04 inventory (same provider, a different session)
    old = json.loads(R1.read_text())
    def by_minor(rows):        # {"3.11": (version, sha256)} through the resolved path, so python3 -> 3.11 counts once
        out = {}
        for i in rows:
            m = re.search(r"python(3\.\d+)$", i.get("resolves_to") or i["path"])
            if m:
                out[m.group(1)] = (i["version"], i["sha256"])
        return out
    old_py, new_py = by_minor(old["python"]["interpreters"]), by_minor(inv["python"]["interpreters"])
    leaf = (mem["cgroup"].get("chain") or [{}])[0].get("limit")
    cmp_rows = [
        ("cpu model", old["cpu"]["model"].split(" (")[0], (cpu_model or "").split(" (")[0]),
        ("online vCPUs", old["cpu"]["online_vcpus"], os.cpu_count()),
        ("kernel release", old["platform"]["kernel"].split()[1], pins["kernel_release"]),
        ("OS", old["platform"]["os"].split(" (")[0], osr.get("PRETTY_NAME")),
        ("libc6 package", old["platform"]["glibc"], pins["dpkg_versions"].get("libc6")),
        ("MemTotal bytes", old["memory"]["MemTotal_bytes"], mem["meminfo_MemTotal"]),
        ("leaf cgroup memory limit bytes (raw)",
         old["memory"]["effective_allowance_for_processes_started_from_this_shell_bytes"], leaf),
        ("default python3", next((i["resolves_to"] for i in old["python"]["interpreters"]
                                  if i["path"] == "/usr/bin/python3"), None), inv["python"]["default_python3"]),
        *[(f"python {k} version", old_py.get(k, (None,))[0], new_py.get(k, (None,))[0])
          for k in sorted(set(old_py) | set(new_py))],
        *[(f"python {k} executable sha256", old_py[k][1], new_py[k][1]) for k in sorted(set(old_py) & set(new_py))],
        ("boot_id", old["boot_and_lifetime"]["boot_id"], inv["boot"]["boot_id"]),
    ]
    inv["comparison_normalised"] = True
    inv["comparison_with_r1_20261004"] = [{"field": f, "r1_20261004": a, "r2_now": b, "same": a == b}
                                          for f, a, b in cmp_rows]
    inv["collected_utc"]["last"] = utc()
    Path(out).write_text(json.dumps(inv, indent=1, sort_keys=False) + "\n")
    print(json.dumps(inv["comparison_with_r1_20261004"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
