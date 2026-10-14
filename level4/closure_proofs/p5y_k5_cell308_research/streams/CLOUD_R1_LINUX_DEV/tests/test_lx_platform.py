"""Isolated, target-free tests of the DEV-ONLY Linux platform layer (lx_platform).

Synthetic inputs only: planted /proc and /sys text in temporary directories, ``sleep`` / ``python -c pass`` child
processes, and temporary files. No cell, no drift, no science module, no decoy, no candidate code is imported or run.
Each fail-closed property has a NEGATIVE CONTROL: a deliberately broken variant (``_Mutant``) that the same test
must reject, so a test that cannot fail is detected.

usage: python3 -m unittest discover -s tests -v      (from streams/CLOUD_R1_LINUX_DEV)
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
LXDIR = os.environ.get("LX_PLATFORM_DIR", str(HERE.parent))     # the mutation harness points this at a mutant copy
sys.path.insert(0, LXDIR)
import lx_platform as L  # noqa: E402

BOOT = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0"
OTHER_BOOT = "11111111-2222-3333-4444-555555555555"


def stat_text(pid=4242, comm="py (x) y", state="S", ppid=1, utime=10, stime=5, start=777):
    # fields 3..22: state ppid pgrp session tty tpgid flags minflt cminflt majflt cmajflt utime stime cutime cstime
    #               priority nice num_threads itrealvalue starttime
    rest = [state, ppid, 1, 1, 0, -1, 0, 0, 0, 0, 0, utime, stime, 0, 0, 20, 0, 1, 0, start, 0, 0]
    return f"{pid} ({comm}) " + " ".join(map(str, rest)) + "\n"


def mkfiles(root: Path, files: dict) -> Path:
    for rel, txt in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt)
    return root


# ====================================================================== identity
class TestIdentity(unittest.TestCase):
    ident = {"pid": 4242, "starttime_ticks": 777, "boot_id": BOOT, "cmdline_sha256": "c" * 64}

    def state(self, ident=None, boot=BOOT, exists=True, stat=None, cmd="c" * 64):
        st = stat if stat is not None else L.proc_stat(4242, stat_text())
        return L.identity_state(ident or self.ident, current_boot=boot, exists=lambda p: exists,
                                stat=lambda p: st, cmd=lambda p: cmd)

    def test_parse_comm_with_spaces_and_parens(self):
        st = L.proc_stat(4242, stat_text(comm="a ) b (c"))
        self.assertEqual((st["comm"], st["state"], st["ppid"], st["starttime"], st["utime"]), ("a ) b (c", "S", 1, 777, 10))

    def test_empty_cmdline_is_a_failed_read(self):
        self.assertIsNone(L.cmdline_sha256(1, b""))                   # kernel thread / exiting task: not a command
        self.assertEqual(L.cmdline_sha256(1, b"a\0b\0"), hashlib.sha256(b"a\0b\0").hexdigest())

    def test_malformed_stat_is_none(self):
        for t in ("", "garbage", "12 (x", "12 (x) S"):
            self.assertIsNone(L.proc_stat(1, t), t)

    def test_alive_only_when_all_fields_match(self):
        self.assertEqual(self.state(), L.ALIVE)

    def test_positive_death_evidence(self):
        self.assertEqual(self.state(boot=OTHER_BOOT), L.DEAD)                       # reboot
        self.assertEqual(self.state(exists=False), L.DEAD)                           # ESRCH
        self.assertEqual(self.state(stat=L.proc_stat(4242, stat_text(start=778))), L.DEAD)   # pid reuse
        self.assertEqual(self.state(cmd="d" * 64), L.DEAD)                           # another command
        self.assertEqual(self.state(stat=L.proc_stat(4242, stat_text(state="Z"))), L.DEAD)   # zombie (L-ID-1)

    def test_failed_readings_are_unknown_never_dead(self):
        self.assertEqual(self.state(boot=""), L.UNKNOWN)                             # boot_id unreadable
        self.assertEqual(self.state(exists=None), L.UNKNOWN)
        self.assertEqual(L.identity_state(self.ident, current_boot=BOOT, exists=lambda p: True,
                                          stat=lambda p: None, cmd=lambda p: "c" * 64), L.UNKNOWN)
        self.assertEqual(self.state(cmd=None), L.UNKNOWN)                            # empty cmdline = failed read

    def test_unrecorded_fields_never_compared_never_alive(self):
        for k in ("boot_id", "starttime_ticks", "cmdline_sha256"):
            partial = dict(self.ident, **{k: None})
            self.assertEqual(self.state(ident=partial), L.UNKNOWN, k)
            # ...and an unrecorded field cannot prove death either
            self.assertNotEqual(self.state(ident=partial, cmd="d" * 64 if k == "cmdline_sha256" else "c" * 64),
                                L.DEAD if k == "cmdline_sha256" else "never", k)

    def test_real_process_lifecycle(self):
        """A real child: ALIVE while running; DEAD after it is killed and reaped."""
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], start_new_session=True)
        try:
            time.sleep(0.3)
            ident = L.identity(p.pid)
            self.assertEqual(L.identity_state(ident), L.ALIVE)
            self.assertNotEqual(ident, L.identity(os.getpid()))
        finally:
            p.kill()
            p.wait()
        self.assertEqual(L.identity_state(ident), L.DEAD)

    def test_detached_child_survives_parent_death(self):
        """Target-free detachment check: a grandchild started in a new session survives SIGKILL of its parent and
        its recorded identity stays ALIVE; this is what a double-fork can do, and NOT what S6 needs (survival of the
        host's / VM's reclaim), which no in-guest test can show."""
        code = ("import subprocess,sys,time;"
                "c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],start_new_session=True);"
                "print(c.pid,flush=True);time.sleep(60)")
        parent = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True)
        gpid = int(parent.stdout.readline())
        time.sleep(0.3)
        ident = L.identity(gpid)
        parent.kill()
        parent.wait()
        time.sleep(0.3)
        try:
            self.assertEqual(L.identity_state(ident), L.ALIVE)
        finally:
            os.kill(gpid, signal.SIGKILL)
        # An exiting task can read UNKNOWN for a moment (empty cmdline before it is a zombie): UNKNOWN is never DEAD,
        # so wait for positive evidence; a reading of ALIVE after the kill would be a defect.
        seen, deadline = [], time.time() + 5
        while time.time() < deadline:
            s = L.identity_state(ident)
            seen.append(s)
            if s == L.DEAD:
                break
            time.sleep(0.02)
        self.assertEqual(seen[-1], L.DEAD, seen)                    # reaped by the new parent, or a zombie (Z)

    def test_negative_control_mutant_trusting_failed_reads(self):
        """A mutant that treats a failed reading as death must be caught by the same assertion."""
        def mutant(ident, **kw):
            r = L.identity_state(ident, **kw)
            return L.DEAD if r == L.UNKNOWN else r
        got = mutant(self.ident, current_boot="", exists=lambda p: True, stat=lambda p: None, cmd=lambda p: None)
        self.assertNotEqual(got, L.UNKNOWN, "control must differ from the real function")


# ====================================================================== boot id
class TestBootId(unittest.TestCase):
    def test_valid_and_invalid(self):
        self.assertEqual(L.boot_id(BOOT + "\n"), BOOT)
        for bad in ("", "nope", BOOT.upper(), BOOT[:-1]):
            self.assertIsNone(L.boot_id(bad), bad)

    def test_live_reading(self):
        self.assertIsNotNone(L.boot_id())


# ====================================================================== interval assessment
def snap(mono, boot, real, *, susp=0, bid=BOOT, power=L.AC):
    return {"clocks": {"monotonic_ns": mono, "boottime_ns": boot, "realtime_ns": real}, "suspend_success": susp,
            "boot_id": bid, "power": power}


S = 10 ** 9


class TestAssess(unittest.TestCase):
    def clean_case(self):
        return snap(0, 0, 0), snap(120 * S, 120 * S, 120 * S), [snap(60 * S, 60 * S, 60 * S)], []

    def test_clean_needs_every_channel(self):
        a, b, s, j = self.clean_case()
        self.assertEqual(L.assess(a, b, s, j)["status"], "CLEAN")

    def test_suspend_detected(self):
        a, b, s, j = self.clean_case()
        b["clocks"]["boottime_ns"] += 30 * S
        self.assertEqual(L.assess(a, b, s, j)["status"], "CONTAMINATED")

    def test_pause_channel_is_ambiguous(self):
        a, b, s, j = self.clean_case()
        b["clocks"]["realtime_ns"] += 600 * S                         # wall clock jumped (VM pause or a clock step)
        r = L.assess(a, b, s, j)
        self.assertEqual(r["status"], "AMBIGUOUS")
        self.assertTrue(any(x.startswith("AMBIGUOUS: P") for x in r["reasons"]))

    def test_missing_channels_never_clean(self):
        a, b, s, j = self.clean_case()
        self.assertEqual(L.assess(a, b, s, None)["status"], "AMBIGUOUS")             # no journal
        a2 = dict(a, suspend_success=None)
        self.assertEqual(L.assess(a2, b, s, j)["status"], "AMBIGUOUS")               # no suspend_stats
        b2 = dict(b, power="ABSENT")
        self.assertEqual(L.assess(a, b2, s, j)["status"], "AMBIGUOUS")               # no power supply exposed
        b3 = dict(b, power=None)
        self.assertEqual(L.assess(a, b3, s, j)["status"], "AMBIGUOUS")

    def test_reboot_battery_suspendcount_journal(self):
        a, b, s, j = self.clean_case()
        self.assertEqual(L.assess(a, dict(b, boot_id=OTHER_BOOT), s, j)["status"], "CONTAMINATED")
        self.assertEqual(L.assess(a, dict(b, power="BATTERY"), s, j)["status"], "CONTAMINATED")
        self.assertEqual(L.assess(a, dict(b, suspend_success=1), s, j)["status"], "CONTAMINATED")
        self.assertEqual(L.assess(a, b, s, [{"t": 1}])["status"], "CONTAMINATED")

    def test_sample_coverage(self):
        a, b, s, j = self.clean_case()
        far = snap(400 * S, 400 * S, 400 * S)
        self.assertEqual(L.assess(a, far, [], j)["status"], "AMBIGUOUS")             # 400 s without a sample

    def test_live_host_is_never_clean(self):
        """On this Cloud VM (no power supply, no suspend_stats, no journal) a real interval cannot be CLEAN."""
        a = L.snapshot()
        b = L.snapshot()
        self.assertNotEqual(L.assess(a, b, [], None)["status"], "CLEAN")


# ====================================================================== power, thermal
class TestPowerThermal(unittest.TestCase):
    def test_power_classes(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(L.power_source(d), "ABSENT")
            mkfiles(Path(d), {"AC/type": "Mains\n", "AC/online": "1\n"})
            self.assertEqual(L.power_source(d), L.AC)
            mkfiles(Path(d), {"BAT0/type": "Battery\n", "BAT0/status": "Discharging\n"})
            self.assertEqual(L.power_source(d), "BATTERY")
            mkfiles(Path(d), {"BAT0/status": "Charging\n", "AC/online": "0\n"})
            self.assertEqual(L.power_source(d), "NO_MAINS")
            mkfiles(Path(d), {"AC/online": "?\n"})
            self.assertIsNone(L.power_source(d))
        self.assertIsNone(L.power_source("/nonexistent/power_supply"))

    def test_thermal_raw_only(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(L.thermal_zones(d), [])
            mkfiles(Path(d), {"thermal_zone0/type": "x86_pkg_temp\n", "thermal_zone0/temp": "45000\n",
                              "thermal_zone0/trip_point_0_type": "passive\n",
                              "thermal_zone0/trip_point_0_temp": "90000\n"})
            z = L.thermal_zones(d)
            self.assertEqual(z[0]["temp_mC"], 45000)
            self.assertEqual(z[0]["trips"], [{"type": "passive", "temp_mC": 90000}])
        self.assertIsNone(L.thermal_zones("/nonexistent/thermal"))


# ====================================================================== memory (raw only)
MEMINFO = "MemTotal:       16479424 kB\nMemFree:        12000000 kB\nMemAvailable:   15000000 kB\n" \
          "Inactive(file):  2000000 kB\nSwapTotal:             0 kB\nHugePages_Total:       0\n"


class TestMemory(unittest.TestCase):
    def cgroot(self, d, leaf_limit="1000000000", mid_limit="9223372036854771712", unreadable_mid=False):
        files = {"memory/a/b/memory.limit_in_bytes": leaf_limit + "\n", "memory/a/b/memory.usage_in_bytes": "400\n",
                 "memory/a/memory.usage_in_bytes": "500\n", "memory/memory.limit_in_bytes": "9223372036854771712\n",
                 "memory/memory.usage_in_bytes": "600\n"}
        if not unreadable_mid:
            files["memory/a/memory.limit_in_bytes"] = mid_limit + "\n"
        return mkfiles(Path(d), files)

    def test_meminfo_units(self):
        m = L.meminfo(MEMINFO)
        self.assertEqual(m["MemTotal"], 16479424 * 1024)
        self.assertEqual(m["HugePages_Total"], 0)

    def test_chain_and_effective_limit(self):
        with tempfile.TemporaryDirectory() as d:
            self.cgroot(d)
            r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)
            self.assertEqual(r["cgroup"]["version"], "v1")
            self.assertEqual([x["path"] for x in r["cgroup"]["chain"]], ["/a/b", "/a", "/"])
            self.assertEqual(r["effective_limit"], 1000000000)
            self.assertEqual(r["cgroup_min_headroom"], 1000000000 - 400)

    def test_unreadable_ancestor_is_unknown_not_unlimited(self):
        with tempfile.TemporaryDirectory() as d:
            self.cgroot(d, unreadable_mid=True)
            r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)
            self.assertIsNone(r["effective_limit"])

    def test_ancestor_tighter_than_leaf(self):
        with tempfile.TemporaryDirectory() as d:
            self.cgroot(d, leaf_limit="9223372036854771712", mid_limit="500000000")
            self.assertEqual(L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)["effective_limit"], 500000000)

    def test_v2(self):
        with tempfile.TemporaryDirectory() as d:
            mkfiles(Path(d), {"x/y/memory.max": "max\n", "x/y/memory.current": "10\n", "x/memory.max": "2048\n",
                              "x/memory.current": "20\n"})
            r = L.memory_readings(MEMINFO, "0::/x/y\n", d)
            self.assertEqual(r["cgroup"]["version"], "v2")
            self.assertEqual(r["effective_limit"], None)   # the root level has no memory.max: unreadable -> UNKNOWN

    def test_no_rfree_quantity_is_produced(self):
        r = L.memory_readings(MEMINFO, "4:memory:/\n", "/nonexistent")
        self.assertNotIn("free_memory_bytes", r)
        self.assertIn("D-MEM-FREE", r["note"])


# ====================================================================== CPU exclusivity
class TestBusy(unittest.TestCase):
    def test_instantaneous_not_lifetime(self):
        hz = 100
        t0 = {10: (1, 1000, "old_hog", "/usr/bin/x"), 11: (1, 0, "spiker", "/opt/y"), 12: (99, 0, "mine", None)}
        t1 = {10: (1, 1000, "old_hog", "/usr/bin/x"), 11: (1, 300, "spiker", "/opt/y"), 12: (99, 900, "mine", None),
              13: (1, 50, "newborn", None)}
        busy = L.busy_processes(t0, t1, 5.0, 25, own_pids={99}, hz=hz)
        # old_hog: large lifetime CPU but idle in the window -> not busy; spiker: 300 ticks / 100 Hz / 5 s = 60 %
        self.assertEqual([b["comm"] for b in busy], ["spiker"])
        self.assertEqual(busy[0]["pct"], 60.0)

    def test_no_reading_fails_closed(self):
        self.assertIsNone(L.busy_processes(None, {}, 5, 25, set()))
        self.assertIsNone(L.busy_processes({}, {}, 0, 25, set()))

    def test_live_snapshot(self):
        a = L.cpu_ticks()
        time.sleep(0.2)
        b = L.cpu_ticks()
        self.assertIsInstance(L.busy_processes(a, b, 0.2, 25, {os.getpid()}), list)

    def test_no_path_allowlist(self):
        t0 = {5: (1, 0, "systemd-journald", "/usr/lib/systemd/systemd-journald")}
        t1 = {5: (1, 100, "systemd-journald", "/usr/lib/systemd/systemd-journald")}
        self.assertEqual(len(L.busy_processes(t0, t1, 1.0, 25, set(), hz=100)), 1)  # D-ALLOW-PATHS open: not allowed


# ====================================================================== updates, launch context
class TestUpdatesLaunch(unittest.TestCase):
    def test_update_positive_evidence_only(self):
        with tempfile.TemporaryDirectory() as d:
            apt, tim = Path(d, "apt"), Path(d, "timers")
            apt.mkdir()
            tim.mkdir()
            ub = str(Path(d, "uu"))
            self.assertTrue(L.auto_update_settings(apt, tim, ub)["guest_auto_install_enabled"])   # nothing: enabled
            (apt / "50x").write_text('APT::Periodic::Unattended-Upgrade "0";\n')
            self.assertFalse(L.auto_update_settings(apt, tim, ub)["guest_auto_install_enabled"])
            (tim / "apt-daily-upgrade.timer").write_text("")
            self.assertTrue(L.auto_update_settings(apt, tim, ub)["guest_auto_install_enabled"])   # timer enabled
            (tim / "apt-daily-upgrade.timer").unlink()
            (apt / "99y").write_text('APT::Periodic::Unattended-Upgrade "1";\n')                 # later file wins
            self.assertTrue(L.auto_update_settings(apt, tim, ub)["guest_auto_install_enabled"])
        self.assertTrue(L.auto_update_settings("/nonexistent", "/nonexistent", "/nonexistent")
                        ["guest_auto_install_enabled"])
        self.assertEqual(L.auto_update_settings()["provider_image_updates"], L.UNKNOWN)

    def test_launched_by_systemd_requires_everything(self):
        cg = "1:name=systemd:/system.slice/rebaseguard-mbs308-exec.service\n"
        env = {"INVOCATION_ID": "abc"}
        good = {"MainPID": os.getpid(), "InvocationID": "abc"}
        ok = L.launched_by_systemd(env=env, proc_cgroup_text=cg, show=lambda u: good, pid1=True)
        self.assertTrue(ok["pass"])
        self.assertEqual(ok["unit"], "rebaseguard-mbs308-exec.service")
        for kw in ({"pid1": False}, {"pid1": None}, {"env": {}},
                   {"proc_cgroup_text": "1:name=systemd:/user.slice/other.service\n"},
                   {"show": lambda u: None}, {"show": lambda u: dict(good, MainPID=1)},
                   {"show": lambda u: dict(good, InvocationID="zzz")}):
            args = dict(env=env, proc_cgroup_text=cg, show=lambda u: good, pid1=True)
            args.update(kw)
            self.assertFalse(L.launched_by_systemd(**args)["pass"], kw)

    def test_live_host_not_launched(self):
        self.assertFalse(L.launched_by_systemd()["pass"])


# ====================================================================== durable write and crash injection
_CHILD = r"""
import os, signal, sys
sys.path.insert(0, sys.argv[1])
import lx_platform as L
stage = sys.argv[3]
def fault(s):
    if s == stage:
        os.kill(os.getpid(), signal.SIGKILL)
L.durable_write(sys.argv[2], b"NEW" * 100000, fault=fault)
"""


class TestDurableWrite(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "result.json")
            h = L.durable_write(p, b"{}")
            self.assertEqual(h, hashlib.sha256(b"{}").hexdigest())
            self.assertFalse(Path(d, "result.json.tmp").exists())

    def test_existing_tmp_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "r.tmp").write_text("stale")
            with self.assertRaises(FileExistsError):
                L.durable_write(Path(d, "r"), b"x")

    def test_tmp_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            os.symlink(os.path.join(d, "elsewhere"), os.path.join(d, "r.tmp"))
            with self.assertRaises(OSError):
                L.durable_write(Path(d, "r"), b"x")
            self.assertFalse(Path(d, "elsewhere").exists())

    def test_crash_injection_old_or_new_never_partial(self):
        """SIGKILL at each stage: the target holds the complete OLD bytes or the complete NEW bytes, never a mix.
        (SIGKILL is not a power loss; the disk-level guarantee is a provider fact, D-HOST-LIFETIME.)"""
        old, new = b"OLD" * 100000, b"NEW" * 100000
        expect = {"written": old, "fsynced": old, "renamed": new}
        for stage, want in expect.items():
            with tempfile.TemporaryDirectory() as d:
                p = Path(d, "result.json")
                p.write_bytes(old)
                rc = subprocess.run([sys.executable, "-c", _CHILD, LXDIR, str(p), stage]).returncode
                self.assertEqual(rc, -signal.SIGKILL, stage)
                self.assertEqual(p.read_bytes(), want, stage)
                leftover = Path(d, "result.json.tmp").exists()
                self.assertEqual(leftover, stage != "renamed", stage)   # a stale tmp is left for recovery to report

    def test_negative_control_non_atomic_writer(self):
        """A mutant that writes the target in place is caught by the same partial-write check."""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "result.json")
            p.write_bytes(b"OLD" * 100000)
            code = ("import os,signal,sys;fd=os.open(sys.argv[1],os.O_WRONLY|os.O_TRUNC);"
                    "os.write(fd,b'NEW'*1000);os.kill(os.getpid(),signal.SIGKILL)")
            subprocess.run([sys.executable, "-c", code, str(p)])
            self.assertNotIn(p.read_bytes(), (b"OLD" * 100000, b"NEW" * 100000))


# ====================================================================== pins and preflight
class TestPinsPreflight(unittest.TestCase):
    def test_pins(self):
        got = L.platform_readings()
        self.assertEqual(L.pin_mismatches(got, got), [])
        changed = dict(got, kernel_release="6.18.44-fc-v64")
        self.assertEqual(L.pin_mismatches(changed, got), ["kernel_release"])
        unread = dict(got, python_sha256=None)
        self.assertIn("python_sha256", L.pin_mismatches(unread, unread))    # an unreadable pin is not a pin

    def test_r1_vs_r2_hosts_would_mismatch(self):
        """The 2026-10-04 host's recorded kernel and OS differ from this host: pins taken there fail here."""
        inv = json.loads((HERE.parent.parent.parent / "governance" / "new_host_route_cloud_r1" /
                          "CLOUD_HOST_INVENTORY.json").read_text())
        r1 = dict(L.platform_readings(), kernel_release=inv["platform"]["kernel"].split()[1])
        self.assertIn("kernel_release", L.pin_mismatches(r1, L.platform_readings()))

    def test_preflight_all_pass_requires_every_gate(self):
        attest = {"reviewed": True, "accepted": True}
        rd = {"power": L.AC, "free_disk": 10 * 2 ** 30, "boot_id": BOOT,
              "updates": {"guest_auto_install_enabled": False, "provider_image_updates": "ATTESTED_FROZEN"}}
        r = L.preflight("/", other_job_running=False, launched={"pass": True}, host_attestation=attest, readings=rd)
        # even with every reading favourable, the OPEN_DECISION gates keep it from passing
        self.assertFalse(r["pass"])
        self.assertEqual({k for k, v in r["gates"].items() if v != L.PASS},
                         {"lowpowermode_0", "thermal_pressure_0", "memory_pressure_normal", "free_memory_ge_min",
                          "host_exclusive"})
        self.assertTrue(all(r["gates"][k] == L.OPEN_DECISION for k in r["blocked"]))

    def test_preflight_unknowns_never_pass(self):
        rd = {"power": None, "free_disk": None, "boot_id": None,
              "updates": {"guest_auto_install_enabled": False, "provider_image_updates": L.UNKNOWN}}
        r = L.preflight("/", other_job_running=None, launched=None, host_attestation=None, readings=rd)
        for k in ("ac_power", "free_disk_ge_2GiB", "boot_id_recorded", "no_other_campaign_job",
                  "no_automatic_os_install", "host_lifetime_attested"):
            self.assertEqual(r["gates"][k], L.UNKNOWN, k)
            self.assertEqual(r["blocked"].get(k), L.UNKNOWN, k)      # an UNKNOWN gate is reported as blocking
        rd["power"] = "ABSENT"
        self.assertEqual(L.preflight("/", other_job_running=False, launched=None, host_attestation=None,
                                     readings=rd)["gates"]["ac_power"], L.OPEN_DECISION)
        unreviewed = {"reviewed": False, "accepted": True}
        self.assertEqual(L.preflight("/", other_job_running=False, launched=None, host_attestation=unreviewed,
                                     readings=rd)["gates"]["host_lifetime_attested"], L.UNKNOWN)

    def test_live_preflight_fails_closed_here(self):
        r = L.preflight("/", other_job_running=False, launched=L.launched_by_systemd(), host_attestation=None)
        self.assertFalse(r["pass"])
        self.assertEqual(r["gates"]["launched_by_systemd"], L.FAIL)
        self.assertEqual(r["gates"]["host_lifetime_attested"], L.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
