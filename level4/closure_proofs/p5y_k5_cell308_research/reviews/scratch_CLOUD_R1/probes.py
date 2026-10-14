"""Reviewer probes (brief 59) against a COPY of lx_platform.py in ./base. Synthetic inputs only; no cell, drift,
science module, decoy or candidate code. Usage: python3 -B probes.py"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "base"))
import lx_platform as L  # noqa: E402

out = {}


def mk(root, files):
    for rel, txt in files.items():
        p = Path(root, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        if txt is None:
            p.mkdir(parents=True, exist_ok=True)      # a DIRECTORY where a file is expected: read fails
        else:
            p.write_text(txt)


# P1 power: battery whose 'type' read fails is skipped -> AC although it is discharging
with tempfile.TemporaryDirectory() as d:
    mk(d, {"AC/type": "Mains\n", "AC/online": "1\n", "BAT0/type": None, "BAT0/status": "Discharging\n"})
    out["P1_power_unreadable_battery_type"] = L.power_source(d)
with tempfile.TemporaryDirectory() as d:
    mk(d, {"AC/type": "Mains\n", "AC/online": "1\n", "UPS0/type": "UPS\n", "UPS0/status": "Discharging\n"})
    out["P1b_power_ups_discharging"] = L.power_source(d)

# P2 preflight update gate with absent / non-literal provider reading
base_rd = {"power": L.AC, "free_disk": 10 * 2 ** 30, "boot_id": "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0"}
for name, upd in (("empty_dict", {}), ("provider_None", {"guest_auto_install_enabled": False,
                                                         "provider_image_updates": None}),
                  ("provider_lowercase_unknown", {"guest_auto_install_enabled": False,
                                                  "provider_image_updates": "unknown"}),
                  ("provider_NOT_ATTESTED", {"guest_auto_install_enabled": False,
                                             "provider_image_updates": "NOT_ATTESTED"})):
    r = L.preflight("/", other_job_running=False, launched={"pass": True}, host_attestation=None,
                    readings=dict(base_rd, updates=upd))
    out[f"P2_no_automatic_os_install[{name}]"] = r["gates"]["no_automatic_os_install"]

# P3 host attestation truthiness
for name, att in (("accepted_REJECTED", {"reviewed": True, "accepted": "REJECTED"}),
                  ("accepted_false_string", {"reviewed": "no", "accepted": "false"}),
                  ("no_machine_binding", {"reviewed": 1, "accepted": 1})):
    r = L.preflight("/", other_job_running=False, launched=None, host_attestation=att,
                    readings=dict(base_rd, updates={"guest_auto_install_enabled": True,
                                                    "provider_image_updates": L.UNKNOWN}))
    out[f"P3_host_lifetime_attested[{name}]"] = r["gates"]["host_lifetime_attested"]

# P4 headroom from a partial chain
MEMINFO = "MemTotal:       16479424 kB\nMemAvailable:   15000000 kB\n"
with tempfile.TemporaryDirectory() as d:
    mk(d, {"memory/a/b/memory.limit_in_bytes": "9223372036854771712\n", "memory/a/b/memory.usage_in_bytes": "400\n",
           "memory/a/memory.limit_in_bytes": "1000000000\n",            # the binding limit; usage UNREADABLE
           "memory/a/memory.usage_in_bytes": "garbage\n",
           "memory/memory.limit_in_bytes": "2000000000\n", "memory/memory.usage_in_bytes": "1900000000\n"})
    r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)
    out["P4a_partial_usage"] = {"effective_limit": r["effective_limit"], "cgroup_min_headroom": r["cgroup_min_headroom"]}
with tempfile.TemporaryDirectory() as d:
    mk(d, {"memory/a/b/memory.limit_in_bytes": "3000000000\n", "memory/a/b/memory.usage_in_bytes": "400\n",
           "memory/a/memory.usage_in_bytes": "500\n",                    # ancestor LIMIT unreadable
           "memory/memory.limit_in_bytes": "9223372036854771712\n", "memory/memory.usage_in_bytes": "600\n"})
    r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)
    out["P4b_unreadable_ancestor_limit"] = {"effective_limit": r["effective_limit"],
                                            "cgroup_min_headroom": r["cgroup_min_headroom"]}
# P4c v2: realistic layout (root has neither memory.max nor memory.current) and memory.high below memory.max
with tempfile.TemporaryDirectory() as d:
    mk(d, {"system.slice/x.service/memory.max": "max\n", "system.slice/x.service/memory.current": "10\n",
           "system.slice/x.service/memory.high": "1000\n",
           "system.slice/memory.max": "max\n", "system.slice/memory.current": "20\n",
           "cgroup.controllers": "cpu memory pids\n"})
    r = L.memory_readings(MEMINFO, "0::/system.slice/x.service\n", d)
    out["P4c_v2_systemd_host"] = {"version": r["cgroup"]["version"], "effective_limit": r["effective_limit"],
                                  "cgroup_min_headroom": r["cgroup_min_headroom"],
                                  "chain": r["cgroup"]["chain"]}

# P5 apt configuration parsing
with tempfile.TemporaryDirectory() as d:
    apt, tim = Path(d, "apt"), Path(d, "timers")
    apt.mkdir(); tim.mkdir()
    (apt / "20auto-upgrades").write_text('APT::Periodic::Update-Package-Lists "1";\n'
                                         '// APT::Periodic::Enable "0";   (commented out)\n')
    out["P5a_commented_line_counts"] = L.auto_update_settings(apt, tim, "/nonexistent")["guest_auto_install_enabled"]
    (apt / "20auto-upgrades").write_text('APT::Periodic::Unattended-Upgrade "1";\n')
    (apt / "99local.dpkg-old").write_text('APT::Periodic::Unattended-Upgrade "0";\n')   # apt ignores this file
    out["P5b_ignored_extension_counts"] = L.auto_update_settings(apt, tim, "/nonexistent")["guest_auto_install_enabled"]
    (apt / "99local.dpkg-old").unlink()
    (apt / "20auto-upgrades").write_text('APT { Periodic { Unattended-Upgrade "1"; }; };\n'
                                         'APT::Periodic::Enable "0";\n')
    out["P5c_nested_syntax"] = L.auto_update_settings(apt, tim, "/nonexistent")
    (apt / "20auto-upgrades").write_text('APT::Periodic::Unattended-Upgrade "0";\n')
    out["P5d_UU0_with_binary_present"] = L.auto_update_settings(apt, tim, "/bin/sh")["guest_auto_install_enabled"]

# P7 busy_processes: a CPU hog born inside the window is not reported
t0 = {10: (1, 0, "idle", "/usr/bin/x")}
t1 = {10: (1, 0, "idle", "/usr/bin/x"), 11: (1, 500, "newhog", "/tmp/hog")}
out["P7_newborn_hog"] = L.busy_processes(t0, t1, 5.0, 25, set(), hz=100)
# pid reuse inside the window: old pid 10 had 1000 ticks, a new process with pid 10 has 400 ticks -> negative delta
t0 = {10: (1, 1000, "old", "/usr/bin/x")}
t1 = {10: (1, 400, "reused_hog", "/tmp/hog")}
out["P7b_pid_reuse_hog"] = L.busy_processes(t0, t1, 4.0, 25, set(), hz=100)
# own_pids containing 1 excludes every orphan / daemon
t0 = {50: (1, 0, "daemon", "/usr/sbin/d")}
t1 = {50: (1, 400, "daemon", "/usr/sbin/d")}
out["P7c_own_pids_contains_1"] = L.busy_processes(t0, t1, 4.0, 25, {1}, hz=100)

# P8 preflight with launched=None: the launch gate is absent rather than failing
r = L.preflight("/", other_job_running=False, launched=None, host_attestation=None, readings=dict(base_rd, updates={}))
out["P8_launch_gate_present_when_launched_None"] = "launched_by_systemd" in r["gates"]

# P10 pin coverage: what the interpreter actually maps vs what is pinned
maps = Path("/proc/self/maps").read_text().splitlines()
libs = sorted({ln.split()[-1] for ln in maps if ".so" in ln.split()[-1]})
pr = L.platform_readings()
out["P10_platform_readings"] = {k: pr[k] for k in ("python_executable", "libpython", "glibc", "os_version")}
out["P10_mapped_shared_objects"] = libs
out["P10_libpython_mapped"] = pr["libpython"] in libs if pr["libpython"] else None
import math, sysconfig  # noqa: E402,E401
out["P10_math_is_builtin"] = "math" in sys.builtin_module_names
out["P10_math_file"] = getattr(math, "__file__", None)
out["P10_Py_ENABLE_SHARED"] = sysconfig.get_config_var("Py_ENABLE_SHARED")

print(json.dumps(out, indent=1, default=str))
