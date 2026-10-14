"""Reviewer probes (brief 60) against a COPY of lx_platform.py revision 2 in ./base (sha256 7561c364...).
Synthetic inputs only; no cell, drift, science module, decoy or candidate code. Usage: python3 -B probes60.py"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "base"))
import lx_platform as L  # noqa: E402

REPO = "/home/user/ReBaseGuard"
out = {"module_sha256": hashlib.sha256((HERE / "base" / "lx_platform.py").read_bytes()).hexdigest()}


def mk(root, files):
    for rel, txt in files.items():
        p = Path(root, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        if txt is None:
            p.mkdir(parents=True, exist_ok=True)
        else:
            p.write_text(txt)


# ---- review-59 P1 re-run: unreadable battery type; UPS discharging
with tempfile.TemporaryDirectory() as d:
    mk(d, {"AC/type": "Mains\n", "AC/online": "1\n", "BAT0/type": None, "BAT0/status": "Discharging\n"})
    out["P1_unreadable_battery_type"] = L.power_source(d)
with tempfile.TemporaryDirectory() as d:
    mk(d, {"AC/type": "Mains\n", "AC/online": "1\n", "UPS0/type": "UPS\n", "UPS0/status": "Discharging\n"})
    out["P1b_ups_discharging"] = L.power_source(d)
# ---- NEW: unrecognised Battery status values with Mains online
for status in ("Unknown", "garbage", "discharging", "Discharging \x00", "Not charging", "Full"):
    with tempfile.TemporaryDirectory() as d:
        mk(d, {"AC/type": "Mains\n", "AC/online": "1\n", "BAT0/type": "Battery\n", "BAT0/status": status + "\n"})
        out[f"N_power_battery_status[{status!r}]"] = L.power_source(d)
# ---- NEW: Mains online, a second Mains whose 'online' is 0 (fine) and a Battery 'status' that is a directory
with tempfile.TemporaryDirectory() as d:
    mk(d, {"AC/type": "Mains\n", "AC/online": "1\n", "BAT0/type": "Battery\n", "BAT0/status": None})
    out["N_power_battery_status_dir"] = L.power_source(d)

# ---- review-59 P2/P3 re-run with revision 2's API
BOOT = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0"
base_rd = {"power": L.AC, "free_disk": 10 * 2 ** 30, "boot_id": BOOT}
for name, upd in (("empty_dict", {}), ("shown_None", {"guest_updates_shown_disabled": None}),
                  ("shown_str_true", {"guest_updates_shown_disabled": "true"})):
    r = L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=None,
                    host_attestation={"provider_image_updates": L.NO_IMAGE_CHANGE},
                    readings=dict(base_rd, updates=upd), attestation_check=lambda a: (True, []))
    out[f"P2_no_automatic_os_install[{name}]"] = r["gates"]["no_automatic_os_install"]
for name, att in (("accepted_REJECTED", {"reviewed": True, "accepted": "REJECTED"}),
                  ("accepted_false_string", {"reviewed": "no", "accepted": "false"}),
                  ("truthy_ints", {"reviewed": 1, "accepted": 1})):
    r = L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=None, host_attestation=att,
                    readings=dict(base_rd, updates={}))
    out[f"P3_host_lifetime_attested[{name}]"] = r["gates"]["host_lifetime_attested"]

# ---- NEW: self-asserted attestation pointing at an ARBITRARY committed file (README.md), any acceptance string
readme = subprocess.run(["git", "-C", REPO, "show", "HEAD:README.md"], capture_output=True).stdout
HW = {"machine_id_sha256": "a" * 64, "product_uuid_sha256": "b" * 64, "hardware_bound": True}
forged = {"reviewed": True, "accepted": True, "path": "README.md", "sha256": hashlib.sha256(readme).hexdigest(),
          "acceptance_record": "no such review", "machine": HW, "provider_image_updates": L.NO_IMAGE_CHANGE}
ok, why = L.attestation_valid(forged, repo_root=REPO, machine=HW)
out["N_forged_attestation_valid"] = [ok, why]
r = L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=None, host_attestation=forged,
                readings=dict(base_rd, updates={"guest_updates_shown_disabled": True}),
                attestation_check=lambda a: L.attestation_valid(a, repo_root=REPO, machine=HW))
out["N_forged_gates"] = {k: r["gates"][k] for k in ("host_lifetime_attested", "no_automatic_os_install")}

# ---- NEW: boot_id_recorded accepts any non-None injected value
for bad in ("", "garbage", 0, False):
    r = L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=None, host_attestation=None,
                    readings=dict(base_rd, boot_id=bad, updates={}))
    out[f"N_boot_id_recorded[{bad!r}]"] = r["gates"]["boot_id_recorded"]

# ---- NEW: launch gate in launcher_preflight mode with a non-dict launched record
try:
    r = L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=True, host_attestation=None,
                    readings=dict(base_rd, updates={}))
    out["N_launched_True_launcher_mode"] = r["gates"].get("launched_by_systemd")
except Exception as e:  # noqa: BLE001
    out["N_launched_True_launcher_mode"] = f"raises {type(e).__name__}"

# ---- review-59 P4 re-run: partial chains (v1)
MEMINFO = "MemTotal:       16479424 kB\nMemAvailable:   15000000 kB\n"
with tempfile.TemporaryDirectory() as d:
    mk(d, {"memory/a/b/memory.limit_in_bytes": "9223372036854771712\n", "memory/a/b/memory.usage_in_bytes": "400\n",
           "memory/a/memory.limit_in_bytes": "1000000000\n", "memory/a/memory.usage_in_bytes": "garbage\n",
           "memory/memory.limit_in_bytes": "2000000000\n", "memory/memory.usage_in_bytes": "1900000000\n"})
    r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d, root_attested=True)
    out["P4a_partial_usage_root_attested"] = {k: r[k] for k in ("effective_limit", "cgroup_min_headroom",
                                                                "visible_limit_upper_bound")}
with tempfile.TemporaryDirectory() as d:
    mk(d, {"memory/a/b/memory.limit_in_bytes": "3000000000\n", "memory/a/b/memory.usage_in_bytes": "400\n",
           "memory/a/memory.usage_in_bytes": "500\n",
           "memory/memory.limit_in_bytes": "9223372036854771712\n", "memory/memory.usage_in_bytes": "600\n"})
    r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d, root_attested=True)
    out["P4b_unreadable_ancestor_limit"] = {k: r[k] for k in ("effective_limit", "cgroup_min_headroom",
                                                              "visible_limit_upper_bound")}
# ---- NEW: v1 leaf limit 'max' with UNREADABLE usage at the binding (only) limited ancestor is refused; but a v1 level
# whose limit is unlimited and whose usage is unreadable is silently accepted (by design). And: v1 hierarchy without the
# root's files at all.
with tempfile.TemporaryDirectory() as d:
    mk(d, {"memory/a/memory.limit_in_bytes": "1000000000\n", "memory/a/memory.usage_in_bytes": "10\n"})
    r = L.memory_readings(MEMINFO, "4:memory:/a\n", d, root_attested=True)
    out["N_v1_root_files_absent"] = {k: r[k] for k in ("effective_limit", "cgroup_min_headroom")}
# ---- P4c v2 systemd layout
with tempfile.TemporaryDirectory() as d:
    mk(d, {"system.slice/x.service/memory.max": "max\n", "system.slice/x.service/memory.current": "10\n",
           "system.slice/x.service/memory.high": "1000\n",
           "system.slice/memory.max": "max\n", "system.slice/memory.current": "20\n",
           "cgroup.controllers": "cpu memory pids\n"})
    r = L.memory_readings(MEMINFO, "0::/system.slice/x.service\n", d)
    r2 = L.memory_readings(MEMINFO, "0::/system.slice/x.service\n", d, root_attested=True)
    out["P4c_v2_systemd_host"] = {"unattested": [r["effective_limit"], r["cgroup_min_headroom"],
                                                 r["visible_limit_upper_bound"]],
                                  "attested": [r2["effective_limit"], r2["cgroup_min_headroom"]]}

# ---- review-59 P5 re-run in revision 2 terms: raw config text is no longer read; injected dump text only
out["P5a_commented_line"] = L.auto_update_settings('// APT::Periodic::Enable "0";\n', use_live_apt=False,
                                                   timers_dir="/nonexistent", snapd_paths=(), cloud_dir="/nonexistent",
                                                   livepatch_dir="/nonexistent")["guest_updates_shown_disabled"]
# NEW: nested-syntax / raw text as dump input is not dump format: shown_disabled False (fine). And the live host:
live = L.auto_update_settings()
out["P5_live_host"] = {k: live[k] for k in ("apt_config_readable", "apt_periodic", "apt_daily_upgrade_timer_enabled",
                                            "snapd_present", "cloud_init_present", "livepatch_applied",
                                            "guest_updates_shown_disabled")}
# NEW: an apt-daily-upgrade timer enabled from /usr/lib or /lib (vendor preset) or runtime dir is not looked at
out["N_timer_dirs_checked"] = ["/etc/systemd/system/timers.target.wants (only)"]

# ---- review-59 P7 re-run with (pid, starttime) keys
t0 = {(10, 1): (1, 0, "idle", "/usr/bin/x")}
t1 = {(10, 1): (1, 0, "idle", "/usr/bin/x"), (11, 9): (1, 500, "newhog", "/tmp/hog")}
out["P7_newborn_hog"] = L.busy_processes(t0, t1, 5.0, 25, set(), hz=100)
t0 = {(10, 1): (1, 1000, "old", "/usr/bin/x")}
t1 = {(10, 7): (1, 400, "reused_hog", "/tmp/hog")}
out["P7b_pid_reuse_hog"] = L.busy_processes(t0, t1, 4.0, 25, set(), hz=100)
out["P7c_own_pids_contains_1"] = L.busy_processes({}, {}, 4.0, 25, {1}, hz=100)
# NEW: a hog that runs during the window and EXITS before t1 is invisible
t0 = {(10, 1): (1, 0, "idle", "/usr/bin/x"), (12, 5): (1, 0, "hog_exits", "/tmp/hog")}
t1 = {(10, 1): (1, 0, "idle", "/usr/bin/x")}
out["N_hog_exits_in_window"] = L.busy_processes(t0, t1, 5.0, 25, set(), hz=100)
# NEW: a hog whose stat is unreadable at t1 (cpu_ticks skips it silently) -> the same: invisible
with tempfile.TemporaryDirectory() as d:
    mk(d, {"10/stat": "10 (idle) S 1 1 1 0 -1 0 0 0 0 0 0 0 0 0 20 0 1 0 1 0 0\n", "11/stat": None})
    out["N_cpu_ticks_unreadable_pid_skipped"] = {str(k): v for k, v in (L.cpu_ticks(d) or {}).items()}
# NEW: grandchildren of the campaign are counted, but a non-campaign child of a campaign pid is exempt
t0 = {(30, 1): (99, 0, "not_campaign_child", "/usr/bin/stress")}
t1 = {(30, 1): (99, 500, "not_campaign_child", "/usr/bin/stress")}
out["N_child_of_own_pid_exempt"] = L.busy_processes(t0, t1, 5.0, 25, {99}, hz=100)

# ---- P8 / F15 re-run
r = L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=None, host_attestation=None,
                readings=dict(base_rd, updates={}))
out["P8_launch_gate_in_launcher_mode_with_None"] = r["gates"].get("launched_by_systemd", "<absent>")

# ---- NEW: identity with namespaces NOT recorded (older / failed record) read from another namespace: ESRCH -> DEAD
ident = {"pid": 4242, "starttime_ticks": 777, "boot_id": BOOT, "cmdline_sha256": "c" * 64}
out["N_unrecorded_ns_esrch"] = L.identity_state(ident, current_boot=BOOT, exists=lambda p: False,
                                                current_ns={"pidns": 1, "timens": 2})
st = L.proc_stat(4242, "4242 (x) S 1 1 1 0 -1 0 0 0 0 0 10 5 0 0 20 0 1 0 999 0 0\n")
out["N_unrecorded_ns_starttime_differs"] = L.identity_state(ident, current_boot=BOOT, exists=lambda p: True,
                                                            stat=lambda p: st, cmd=lambda p: "c" * 64,
                                                            current_ns={"pidns": 1, "timens": 2})

# ---- NEW: proc_view_complete on this host, and the pid namespace inode vs the init pid namespace (0xEFFFFFFC)
out["N_proc_view_complete_live"] = L.proc_view_complete()
out["N_pidns_inode_live"] = L.ns_inode("pid")
out["N_init_pidns_inode_constant"] = 0xEFFFFFFC

# ---- NEW: mapped_objects with a '(deleted)' mapping (library replaced on disk while mapped)
out["N_mapped_deleted"] = L.mapped_objects(
    "7f00-7f01 r-xp 0 08:01 1 /usr/lib/x86_64-linux-gnu/libm.so.6 (deleted)\n")
# NEW: mapped_objects without libm/libc at all (e.g. maps text partial) is still a 'valid' pin
out["N_mapped_without_libm"] = L.mapped_objects("7f00-7f01 r-xp 0 08:01 1 " + os.path.realpath(sys.executable) + "\n")
# ---- P10 rev2: libpython mapped?
pr = L.platform_readings()
out["P10_rev2_libpython_mapped"] = pr["libpython_mapped"]
out["P10_rev2_mapped_names"] = sorted(Path(k).name for k in (pr["mapped_objects"] or {}))
out["P10_rev2_dpkg_versions"] = pr["dpkg_versions"]
out["P10_rev2_livepatch"] = pr["livepatch"]

print(json.dumps(out, indent=1, default=str))
