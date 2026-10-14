"""Isolated, target-free tests of the DEV-ONLY Linux platform layer (lx_platform), revision 2.

Synthetic inputs only: planted /proc and /sys text in temporary directories, ``sleep`` / busy-loop child processes,
temporary files and a temporary git repository. No cell, no drift, no science module, no decoy is imported or run;
the historical candidate is only READ (``git show 142d97a9:...``) to pin two constants.
Revision 2 adds tests for every code finding of review 59 (F1, F2, F8-F15, F22, F23) and kills the reviewer's mutants
R01-R10 (tests/run_mutants.py carries them).

usage: python3 -m unittest discover -s tests -v      (from streams/CLOUD_R1_LINUX_DEV)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import signal
import stat as _stat
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

REPO = HERE.parents[5]
CAND_HOST = "level4/closure_proofs/p5y_k5_cell308_mbs_r1/code/mbs308_host.py"
CAND_COMMIT = "142d97a90a1c3fafff394044aa1448674f7a633c"
BOOT = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0"
OTHER_BOOT = "11111111-2222-3333-4444-555555555555"
NS = {"pidns": 4026531836, "timens": 4026531834}


def stat_text(pid=4242, comm="py (x) y", state="S", ppid=1, utime=10, stime=5, start=777):
    rest = [state, ppid, 1, 1, 0, -1, 0, 0, 0, 0, 0, utime, stime, 0, 0, 20, 0, 1, 0, start, 0, 0]
    return f"{pid} ({comm}) " + " ".join(map(str, rest)) + "\n"


def mkfiles(root: Path, files: dict) -> Path:
    for rel, txt in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt)
    return root


def wait_not_alive(ident, timeout=5.0) -> list:
    seen, deadline = [], time.time() + timeout
    while time.time() < deadline:
        s = L.identity_state(ident)
        seen.append(s)
        if s == L.DEAD:
            break
        time.sleep(0.02)
    return seen


# ====================================================================== identity
class TestIdentity(unittest.TestCase):
    ident = {"pid": 4242, "starttime_ticks": 777, "boot_id": BOOT, "cmdline_sha256": "c" * 64, **NS}

    def state(self, ident=None, boot=BOOT, exists=True, stat=None, cmd="c" * 64, ns=NS):
        st = stat if stat is not None else L.proc_stat(4242, stat_text())
        return L.identity_state(ident or self.ident, current_boot=boot, exists=lambda p: exists,
                                stat=lambda p: st, cmd=lambda p: cmd, current_ns=ns)

    def test_parse_comm_with_spaces_and_parens(self):
        st = L.proc_stat(4242, stat_text(comm="a ) b (c"))
        self.assertEqual((st["comm"], st["state"], st["ppid"], st["starttime"], st["utime"]),
                         ("a ) b (c", "S", 1, 777, 10))

    def test_malformed_stat_is_none(self):
        for t in ("", "garbage", "12 (x", "12 (x) S"):
            self.assertIsNone(L.proc_stat(1, t), t)

    def test_empty_cmdline_is_a_failed_read(self):
        self.assertIsNone(L.cmdline_sha256(1, b""))
        self.assertEqual(L.cmdline_sha256(1, b"a\0b\0"), hashlib.sha256(b"a\0b\0").hexdigest())

    def test_alive_only_when_all_fields_match(self):
        self.assertEqual(self.state(), L.ALIVE)

    def test_live_task_states_are_alive(self):
        """R07: stopped (T, t), uninterruptible (D), running (R), idle (I) tasks are live."""
        for s in ("R", "S", "D", "T", "t", "I"):
            self.assertEqual(self.state(stat=L.proc_stat(4242, stat_text(state=s))), L.ALIVE, s)

    def test_positive_death_evidence(self):
        self.assertEqual(self.state(boot=OTHER_BOOT), L.DEAD)                       # reboot
        self.assertEqual(self.state(exists=False), L.DEAD)                           # ESRCH
        self.assertEqual(self.state(stat=L.proc_stat(4242, stat_text(start=778))), L.DEAD)   # pid reuse
        self.assertEqual(self.state(cmd="d" * 64), L.DEAD)                           # another command

    def test_zombie_is_never_proof_of_death(self):
        """F2: a zombie / dead task reads UNKNOWN (macOS O-4 outcome), never DEAD."""
        for s in ("Z", "X"):
            self.assertEqual(self.state(stat=L.proc_stat(4242, stat_text(state=s))), L.UNKNOWN, s)

    def test_failed_readings_are_unknown_never_dead(self):
        self.assertEqual(self.state(boot=""), L.UNKNOWN)
        self.assertEqual(self.state(exists=None), L.UNKNOWN)
        self.assertEqual(L.identity_state(self.ident, current_boot=BOOT, exists=lambda p: True,
                                          stat=lambda p: None, cmd=lambda p: "c" * 64, current_ns=NS), L.UNKNOWN)
        self.assertEqual(self.state(cmd=None), L.UNKNOWN)

    def test_namespace_mismatch_is_unknown(self):
        """F14: a reader in another PID / time namespace cannot prove anything about the recorded pid."""
        self.assertEqual(self.state(ns=dict(NS, pidns=1)), L.UNKNOWN)
        self.assertEqual(self.state(ns=dict(NS, timens=None)), L.UNKNOWN)
        self.assertEqual(self.state(ns=dict(NS, pidns=1), exists=False), L.UNKNOWN)   # ESRCH there proves nothing

    def test_unrecorded_fields(self):
        """N-2: a field never recorded is never compared (cannot prove death) and blocks ALIVE."""
        for k in ("boot_id", "starttime_ticks", "cmdline_sha256", "pidns", "timens"):
            partial = dict(self.ident, **{k: None})
            self.assertEqual(self.state(ident=partial), L.UNKNOWN, k)
        no_cmd = dict(self.ident, cmdline_sha256=None)
        self.assertEqual(self.state(ident=no_cmd, cmd="d" * 64), L.UNKNOWN)
        no_start = dict(self.ident, starttime_ticks=None)
        self.assertEqual(self.state(ident=no_start, stat=L.proc_stat(4242, stat_text(start=1))), L.UNKNOWN)

    def test_real_process_lifecycle(self):
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], start_new_session=True)
        try:
            time.sleep(0.3)
            ident = L.identity(p.pid)
            self.assertEqual(L.identity_state(ident), L.ALIVE)
        finally:
            p.kill()
            p.wait()
        self.assertEqual(L.identity_state(ident), L.DEAD)

    def test_zombie_leader_with_live_thread_is_not_dead(self):
        """Review 59 probe P6 as a test: the main thread exits (pthread_exit) while a worker thread computes; the
        leader shows state Z although the process lives and uses CPU. It must never read DEAD."""
        child = ("import ctypes,threading,time,sys\n"
                 "def w():\n t=time.time()+4\n while time.time()<t: pass\n"
                 "threading.Thread(target=w).start()\n"
                 "sys.stdout.write('ready\\n');sys.stdout.flush()\n"
                 "ctypes.CDLL(None).pthread_exit(None)\n")
        p = subprocess.Popen([sys.executable, "-c", child], stdout=subprocess.PIPE, text=True)
        try:
            ident = L.identity(p.pid)
            self.assertEqual(p.stdout.readline().strip(), "ready")
            time.sleep(0.4)
            states = []
            for _ in range(5):
                st = L.proc_stat(p.pid)
                states.append((st and st["state"], L.identity_state(ident)))
                time.sleep(0.1)
            self.assertTrue(any(s == "Z" for s, _ in states), states)     # the probe really reached a zombie leader
            self.assertTrue(all(v != L.DEAD for _, v in states), states)
        finally:
            p.kill()
            p.wait()
            p.stdout.close()

    def test_detached_child_survives_parent_death(self):
        """A new-session grandchild survives SIGKILL of its parent (ALIVE); after its own kill it is never ALIVE again
        (DEAD once reaped; UNKNOWN while an unreaped zombie). This is NOT what S6 needs (survival of the host)."""
        code = ("import subprocess,sys,time;"
                "c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],start_new_session=True);"
                "print(c.pid,flush=True);time.sleep(60)")
        parent = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True)
        gpid = int(parent.stdout.readline())
        time.sleep(0.3)
        ident = L.identity(gpid)
        parent.kill()
        parent.wait()
        parent.stdout.close()
        time.sleep(0.3)
        try:
            self.assertEqual(L.identity_state(ident), L.ALIVE)
        finally:
            os.kill(gpid, signal.SIGKILL)
        seen = wait_not_alive(ident, 3.0)
        self.assertNotEqual(seen[-1], L.ALIVE, seen)
        self.assertIn(seen[-1], (L.DEAD, L.UNKNOWN))


class TestBootMachine(unittest.TestCase):
    def test_boot_id(self):
        self.assertEqual(L.boot_id(BOOT + "\n"), BOOT)
        for bad in ("", "nope", BOOT.upper(), BOOT[:-1]):
            self.assertIsNone(L.boot_id(bad), bad)
        self.assertIsNotNone(L.boot_id())

    def test_machine_identity_hashes_and_hardware_binding(self):
        with tempfile.TemporaryDirectory() as d:
            mid, dmi = Path(d, "mid"), Path(d, "dmi")
            mid.write_text("abc\n")
            r = L.machine_identity(mid, dmi)
            self.assertEqual(r["machine_id_sha256"], hashlib.sha256(b"abc").hexdigest())
            self.assertFalse(r["hardware_bound"])
            dmi.write_text("UUID\n")
            self.assertTrue(L.machine_identity(mid, dmi)["hardware_bound"])


# ====================================================================== interval assessment
def snap(mono, boot, real, *, susp=0, bid=BOOT, power=L.AC):
    return {"clocks": {"monotonic_ns": mono, "boottime_ns": boot, "realtime_ns": real}, "suspend_success": susp,
            "boot_id": bid, "power": power}


S = 10 ** 9


def git_show(rel: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), "show", f"{CAND_COMMIT}:{rel}"], capture_output=True, text=True,
                          check=True).stdout


class TestAssess(unittest.TestCase):
    def clean_case(self):
        return snap(0, 0, 0), snap(120 * S, 120 * S, 120 * S), [snap(60 * S, 60 * S, 60 * S)], []

    def test_constants_equal_the_candidates(self):
        """R04 / R09: the tolerance and spacing are the accepted mbs308_host values (read from 142d97a9)."""
        src = git_show(CAND_HOST)
        tol = int(re.search(r"^SLEEP_GAP_TOL_NS = ([\d_]+)", src, re.M).group(1).replace("_", ""))
        gap = int(re.search(r"^MAX_SAMPLE_GAP_S = (\d+)", src, re.M).group(1))
        self.assertEqual((L.SLEEP_GAP_TOL_NS, L.MAX_SAMPLE_GAP_S), (tol, gap))

    def test_clean_needs_every_channel(self):
        a, b, s, j = self.clean_case()
        self.assertEqual(L.assess(a, b, s, j)["status"], "CLEAN")

    def test_suspend_detected_just_above_tolerance(self):
        a, b, s, j = self.clean_case()
        b["clocks"]["boottime_ns"] += 3 * S
        self.assertEqual(L.assess(a, b, s, j)["status"], "CONTAMINATED")

    def test_pause_channel_is_ambiguous(self):
        a, b, s, j = self.clean_case()
        b["clocks"]["realtime_ns"] += 3 * S
        r = L.assess(a, b, s, j)
        self.assertEqual(r["status"], "AMBIGUOUS")
        self.assertTrue(any(x.startswith("AMBIGUOUS: P") for x in r["reasons"]))

    def test_missing_channels_never_clean(self):
        a, b, s, j = self.clean_case()
        self.assertEqual(L.assess(a, b, s, None)["status"], "AMBIGUOUS")
        self.assertEqual(L.assess(dict(a, suspend_success=None), b, s, j)["status"], "AMBIGUOUS")
        self.assertEqual(L.assess(a, dict(b, power="ABSENT"), s, j)["status"], "AMBIGUOUS")
        self.assertEqual(L.assess(a, dict(b, power=None), s, j)["status"], "AMBIGUOUS")
        self.assertEqual(L.assess(a, dict(b, boot_id=None), s, j)["status"], "AMBIGUOUS")

    def test_power_checked_at_every_sample(self):
        """R10: a battery reading in the middle of the interval contaminates it."""
        a, b, _, j = self.clean_case()
        mid = snap(60 * S, 60 * S, 60 * S, power="BATTERY")
        self.assertEqual(L.assess(a, b, [mid], j)["status"], "CONTAMINATED")
        self.assertEqual(L.assess(a, b, [dict(mid, power=None)], j)["status"], "AMBIGUOUS")

    def test_reboot_battery_suspendcount_journal(self):
        a, b, s, j = self.clean_case()
        self.assertEqual(L.assess(a, dict(b, boot_id=OTHER_BOOT), s, j)["status"], "CONTAMINATED")
        self.assertEqual(L.assess(a, dict(b, power="BATTERY"), s, j)["status"], "CONTAMINATED")
        self.assertEqual(L.assess(a, dict(b, suspend_success=1), s, j)["status"], "CONTAMINATED")
        self.assertEqual(L.assess(a, b, s, [{"t": 1}])["status"], "CONTAMINATED")

    def test_sample_spacing_boundary(self):
        """R09: 180 s spacing is covered, 181 s is not."""
        a = snap(0, 0, 0)
        self.assertEqual(L.assess(a, snap(180 * S, 180 * S, 180 * S), [], [])["status"], "CLEAN")
        self.assertEqual(L.assess(a, snap(181 * S, 181 * S, 181 * S), [], [])["status"], "AMBIGUOUS")

    def test_live_host_is_never_clean(self):
        self.assertNotEqual(L.assess(L.snapshot(), L.snapshot(), [], None)["status"], "CLEAN")


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

    def test_failed_or_unknown_supplies_are_unknown(self):
        """F9 / R01: an unreadable type, an unreadable battery status, or an unknown supply type is never AC."""
        base = {"AC/type": "Mains\n", "AC/online": "1\n"}
        with tempfile.TemporaryDirectory() as d:
            mkfiles(Path(d), dict(base, **{"BAT0/type": "Battery\n"}))          # status file missing
            self.assertIsNone(L.power_source(d))
        with tempfile.TemporaryDirectory() as d:
            mkfiles(Path(d), base)
            (Path(d) / "BAT1" / "type").mkdir(parents=True)                   # type unreadable (a directory)
            self.assertIsNone(L.power_source(d))
        with tempfile.TemporaryDirectory() as d:
            mkfiles(Path(d), dict(base, **{"ups/type": "UPS\n", "ups/status": "Discharging\n"}))
            self.assertEqual(L.power_source(d), "BATTERY")
        with tempfile.TemporaryDirectory() as d:
            mkfiles(Path(d), dict(base, **{"usb/type": "USB\n", "usb/online": "1\n"}))
            self.assertIsNone(L.power_source(d))

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


# ====================================================================== memory and cgroups
MEMINFO = "MemTotal:       16479424 kB\nMemFree:        12000000 kB\nMemAvailable:   15000000 kB\n" \
          "Inactive(file):  2000000 kB\nSwapTotal:             0 kB\nHugePages_Total:       0\n"
BIG = "9223372036854771712"


class TestMemory(unittest.TestCase):
    def v1(self, d, leaf="1000000000", mid=BIG, leaf_use="400\n", drop=()):
        files = {"memory/a/b/memory.limit_in_bytes": leaf + "\n", "memory/a/b/memory.usage_in_bytes": leaf_use,
                 "memory/a/memory.limit_in_bytes": mid + "\n", "memory/a/memory.usage_in_bytes": "500\n",
                 "memory/memory.limit_in_bytes": BIG + "\n", "memory/memory.usage_in_bytes": "600\n"}
        for k in drop:
            files.pop(k)
        return mkfiles(Path(d), files)

    def test_meminfo_units(self):
        m = L.meminfo(MEMINFO)
        self.assertEqual(m["MemTotal"], 16479424 * 1024)
        self.assertEqual(m["HugePages_Total"], 0)

    def test_v1_needs_root_attestation_for_a_number(self):
        with tempfile.TemporaryDirectory() as d:
            self.v1(d)
            r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)
            self.assertEqual([x["path"] for x in r["cgroup"]["chain"]], ["/a/b", "/a", "/"])
            self.assertIsNone(r["effective_limit"])
            self.assertIsNone(r["cgroup_min_headroom"])
            self.assertEqual(r["visible_limit_upper_bound"], 1000000000)
            ra = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d, root_attested=True)
            self.assertEqual((ra["effective_limit"], ra["cgroup_min_headroom"]), (1000000000, 1000000000 - 400))

    def test_partial_chain_never_numeric(self):
        """F10: an unreadable limit anywhere, or an unreadable usage at a limited level, gives no number."""
        with tempfile.TemporaryDirectory() as d:
            self.v1(d, drop=("memory/a/memory.limit_in_bytes",))
            r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d, root_attested=True)
            self.assertEqual((r["effective_limit"], r["cgroup_min_headroom"], r["visible_limit_upper_bound"]),
                             (None, None, None))
        with tempfile.TemporaryDirectory() as d:
            self.v1(d, leaf_use="?\n", mid="2000000000")      # another limited level exists: a partial min is possible
            r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d, root_attested=True)
            self.assertIsNone(r["cgroup_min_headroom"])

    def test_ancestor_tighter_than_leaf(self):
        with tempfile.TemporaryDirectory() as d:
            self.v1(d, leaf=BIG, mid="500000000")
            r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d, root_attested=True)
            self.assertEqual(r["effective_limit"], 500000000)

    def test_v2_root_and_memory_high(self):
        with tempfile.TemporaryDirectory() as d:
            mkfiles(Path(d), {"x/y/memory.max": "max\n", "x/y/memory.high": "3000\n", "x/y/memory.current": "10\n",
                              "x/memory.max": "8000\n", "x/memory.high": "max\n", "x/memory.current": "20\n"})
            cg = "0::/x/y\n"
            self.assertIsNone(L.memory_readings(MEMINFO, cg, d)["effective_limit"])        # root not attested
            r = L.memory_readings(MEMINFO, cg, d, root_attested=True)
            self.assertEqual(r["cgroup"]["version"], "v2")
            self.assertEqual(r["effective_limit"], 3000)                                  # memory.high binds
            self.assertEqual(r["cgroup_min_headroom"], 2990)
            ch = L.memory_cgroup_chain(cg, d)
            self.assertIsNone(L._chain_values(ch, root_attested=False))                    # helper refuses directly
            self.assertIsNotNone(L._chain_values(ch, root_attested=True))
            Path(d, "x/memory.high").unlink()                                              # unreadable high
            self.assertIsNone(L.memory_readings(MEMINFO, cg, d, root_attested=True)["effective_limit"])

    def test_no_rfree_quantity_is_produced(self):
        r = L.memory_readings(MEMINFO, "4:memory:/\n", "/nonexistent")
        self.assertNotIn("free_memory_bytes", r)
        self.assertIn("D-MEM-FREE", r["note"])

    def test_cgroup_resources_raw(self):
        with tempfile.TemporaryDirectory() as d:
            mkfiles(Path(d), {"x/cgroup.controllers": "cpu pids\n", "x/cpu.max": "200000 100000\n",
                              "x/cpuset.cpus.effective": "0-1\n", "x/pids.max": "max\n"})
            r = L.cgroup_resources("0::/x\n", d)
            self.assertEqual((r["cpu.max"], r["cpuset.cpus.effective"], r["pids.max"]),
                             ("200000 100000", "0-1", "max"))


# ====================================================================== CPU exclusivity
class TestBusy(unittest.TestCase):
    def test_window_not_lifetime_and_reuse_and_birth(self):
        hz = 100
        t0 = {(10, 1): (1, 1000, "old_hog", "/usr/bin/x"), (11, 2): (1, 0, "spiker", "/opt/y"),
              (12, 3): (99, 0, "mine", None), (20, 5): (1, 0, "gone", None)}
        t1 = {(10, 1): (1, 1000, "old_hog", "/usr/bin/x"), (11, 2): (1, 300, "spiker", "/opt/y"),
              (12, 3): (99, 900, "mine", None), (13, 50): (1, 200, "newborn", None),
              (20, 60): (1, 150, "reused_pid", None)}
        busy = {b["comm"]: b for b in L.busy_processes(t0, t1, 5.0, 25, own_pids={99}, hz=hz)}
        self.assertEqual(set(busy), {"spiker", "newborn", "reused_pid"})
        self.assertEqual(busy["spiker"]["pct"], 60.0)
        self.assertTrue(busy["newborn"]["born_in_window"])

    def test_no_reading_or_unsafe_inputs_fail_closed(self):
        self.assertIsNone(L.busy_processes(None, {}, 5, 25, set()))
        self.assertIsNone(L.busy_processes({}, {}, 0, 25, set()))
        self.assertIsNone(L.busy_processes({}, {}, 5, 25, {1}))                 # own_pids may not contain init
        self.assertIsNone(L.busy_processes({}, {}, 5, 25, set(), view_complete=False))
        self.assertIsNone(L.busy_processes({}, {}, 5, 25, set(), view_complete=None))

    def test_no_name_or_path_allowlist(self):
        """R05 / D-ALLOW-PATHS: no process is exempt by name or path, including the Cloud session controller."""
        for comm, exe in (("claude", "/opt/claude-code/bin/claude"), ("process_api", "/process_api"),
                          ("systemd-journald", "/usr/lib/systemd/systemd-journald")):
            t0 = {(5, 1): (2, 0, comm, exe)}
            t1 = {(5, 1): (2, 100, comm, exe)}
            self.assertEqual(len(L.busy_processes(t0, t1, 1.0, 25, set(), hz=100)), 1, comm)

    def test_proc_view(self):
        mi = "23 28 0:22 / /proc rw,relatime - proc proc rw\n"
        self.assertTrue(L.proc_view_complete("NSpid:\t77\n", mi))
        self.assertFalse(L.proc_view_complete("NSpid:\t77\t3\n", mi))
        self.assertFalse(L.proc_view_complete("NSpid:\t77\n", "23 28 0:22 / /proc rw,hidepid=2 - proc proc rw\n"))
        self.assertIsNone(L.proc_view_complete("Name: x\n", mi))

    def test_live_snapshot(self):
        a = L.cpu_ticks()
        time.sleep(0.2)
        b = L.cpu_ticks()
        self.assertIsInstance(L.busy_processes(a, b, 0.2, 25, {os.getpid()}, view_complete=L.proc_view_complete()),
                              list)


# ====================================================================== updates, launch context
class TestUpdatesLaunch(unittest.TestCase):
    def settings(self, dump, **mk):
        d = tempfile.mkdtemp()
        paths = {"timers_dir": Path(d, "timers"), "uu_binary": str(Path(d, "uu")),
                 "snapd_paths": (str(Path(d, "snapd")),), "cloud_dir": str(Path(d, "cloud")),
                 "livepatch_dir": str(Path(d, "livepatch"))}
        Path(paths["timers_dir"]).mkdir()
        if mk.get("timer"):
            Path(paths["timers_dir"], "apt-daily-upgrade.timer").write_text("")
        for k in ("snapd", "cloud"):
            if mk.get(k):
                Path(d, k).mkdir()
        if mk.get("livepatch") is not None:
            Path(d, "livepatch").mkdir()
            for n in mk["livepatch"]:
                Path(d, "livepatch", n).mkdir()
        return L.auto_update_settings(dump, use_live_apt=False, **paths)

    def test_positive_evidence_only(self):
        off = 'APT::Periodic "";\nAPT::Periodic::Enable "0";\n'
        self.assertTrue(self.settings(off)["guest_updates_shown_disabled"])
        self.assertTrue(self.settings('APT::Periodic::Unattended-Upgrade "0";\n')["guest_updates_shown_disabled"])
        for kw in ({"timer": True}, {"snapd": True}, {"cloud": True}, {"livepatch": ["kpatch_1"]}):
            self.assertFalse(self.settings(off, **kw)["guest_updates_shown_disabled"], kw)
        self.assertFalse(self.settings('APT::Periodic::Unattended-Upgrade "1";\n')["guest_updates_shown_disabled"])
        self.assertFalse(self.settings("")["guest_updates_shown_disabled"])                 # nothing positive
        self.assertFalse(L.auto_update_settings(None, use_live_apt=False)["guest_updates_shown_disabled"])

    def test_dump_lines_only(self):
        """apt-config dump never prints comments; a commented-out key in raw text is not a dump line."""
        self.assertFalse(self.settings('// APT::Periodic::Enable "0";\n')["guest_updates_shown_disabled"])

    def test_reboot_vector_recorded_and_provider_unknown(self):
        r = self.settings('APT::Periodic::Enable "0";\nUnattended-Upgrade::Automatic-Reboot "true";\n')
        self.assertEqual(r["unattended_automatic_reboot"], "true")
        self.assertEqual(r["provider_image_updates"], L.UNKNOWN)

    def test_launched_by_systemd_requires_everything(self):
        cg = "1:name=systemd:/system.slice/rebaseguard-mbs308-exec.service\n"
        env = {"INVOCATION_ID": "abc"}
        good = {"MainPID": os.getpid(), "InvocationID": "abc"}
        self.assertTrue(L.launched_by_systemd(env=env, proc_cgroup_text=cg, show=lambda u: good, pid1=True)["pass"])
        for kw in ({"pid1": False}, {"env": {}},
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
            self.assertEqual(L.durable_write(p, b"{}"), hashlib.sha256(b"{}").hexdigest())
            self.assertFalse(Path(d, "result.json.tmp").exists())

    def test_fsyncs_file_then_directory(self):
        """R03 / R08: the data and the directory are both fsync'd, in that order."""
        calls, real = [], os.fsync

        def spy(fd):
            calls.append("dir" if _stat.S_ISDIR(os.fstat(fd).st_mode) else "file")
            return real(fd)
        os.fsync = spy
        try:
            with tempfile.TemporaryDirectory() as d:
                L.durable_write(Path(d, "r"), b"x")
        finally:
            os.fsync = real
        self.assertEqual(calls, ["file", "dir"])

    def test_stale_tmp_is_a_named_state(self):
        """F23: a stale tmp raises StaleTmp and is left in place."""
        with tempfile.TemporaryDirectory() as d:
            Path(d, "r.tmp").write_text("stale")
            with self.assertRaises(L.StaleTmp):
                L.durable_write(Path(d, "r"), b"x")
            self.assertEqual(Path(d, "r.tmp").read_text(), "stale")

    def test_tmp_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            os.symlink(os.path.join(d, "elsewhere"), os.path.join(d, "r.tmp"))
            with self.assertRaises(OSError):
                L.durable_write(Path(d, "r"), b"x")
            self.assertFalse(Path(d, "elsewhere").exists())

    def test_crash_injection_old_or_new_never_partial(self):
        """SIGKILL at each stage: complete OLD or complete NEW bytes, never a mix (SIGKILL is not a power loss)."""
        old = b"OLD" * 100000
        for stage, want in {"written": old, "fsynced": old, "renamed": b"NEW" * 100000}.items():
            with tempfile.TemporaryDirectory() as d:
                p = Path(d, "result.json")
                p.write_bytes(old)
                rc = subprocess.run([sys.executable, "-c", _CHILD, LXDIR, str(p), stage]).returncode
                self.assertEqual(rc, -signal.SIGKILL, stage)
                self.assertEqual(p.read_bytes(), want, stage)
                self.assertEqual(Path(d, "result.json.tmp").exists(), stage != "renamed", stage)


# ====================================================================== pins
class TestPins(unittest.TestCase):
    def test_pin_set_covers_libm_libc_loader(self):
        """F1: the mapped shared objects (incl. libm.so.6, libc.so.6, the loader) and package versions are pinned."""
        self.assertEqual(set(L.PIN_KEYS), {"python_executable", "python_sha256", "python_sys_version",
                                           "mapped_objects", "dpkg_versions", "livepatch", "os_id", "os_version_id",
                                           "os_version", "kernel_release", "machine", "glibc"})
        got = L.platform_readings()
        names = {Path(k).name for k in got["mapped_objects"]}
        for lib in ("libm.so.6", "libc.so.6"):
            self.assertIn(lib, names)
        self.assertTrue(any(n.startswith("ld-linux") for n in names))
        self.assertIn("libc6", got["dpkg_versions"])

    def test_every_pin_key_is_compared(self):
        """R06: changing any one pinned value is a mismatch."""
        got = L.platform_readings()
        self.assertEqual(L.pin_mismatches(got, got), [])
        for k in L.PIN_KEYS:
            v = got[k]
            changed = (dict(v, **{next(iter(v)): "different"}) if isinstance(v, dict) and v else
                       (["x"] if isinstance(v, list) else f"{v}-different"))
            self.assertEqual(L.pin_mismatches(dict(got, **{k: changed}), got), [k], k)

    def test_libm_change_with_same_glibc_string(self):
        """The review-59 case: libc6 8.7 vs 8.9 both report 'glibc 2.39'; the package version and libm digest differ."""
        got = L.platform_readings()
        libm = next(k for k in got["mapped_objects"] if k.endswith("libm.so.6"))
        other = dict(got, mapped_objects=dict(got["mapped_objects"], **{libm: "0" * 64}))
        self.assertEqual(L.pin_mismatches(other, got), ["mapped_objects"])
        other = dict(got, dpkg_versions=dict(got["dpkg_versions"], libc6="2.39-0ubuntu8.7"))
        self.assertEqual(L.pin_mismatches(other, got), ["dpkg_versions"])

    def test_unreadable_pins_never_match(self):
        got = L.platform_readings()
        for bad in ({"python_sha256": None}, {"mapped_objects": None}, {"mapped_objects": {}},
                    {"dpkg_versions": dict(got["dpkg_versions"], libc6=None)}):
            pins = dict(got, **bad)
            self.assertIn(next(iter(bad)), L.pin_mismatches(pins, pins), bad)
        self.assertIsNone(L.mapped_objects("7f00-7f01 r-xp 0 08:01 1 /nonexistent/libx.so.1\n"))

    def test_r1_vs_r2_hosts_would_mismatch(self):
        inv = json.loads((HERE.parents[2] / "governance" / "new_host_route_cloud_r1" /
                          "CLOUD_HOST_INVENTORY.json").read_text())
        r1 = dict(L.platform_readings(), kernel_release=inv["platform"]["kernel"].split()[1])
        self.assertIn("kernel_release", L.pin_mismatches(r1, L.platform_readings()))


# ====================================================================== attestation and preflight
class TestAttestationPreflight(unittest.TestCase):
    HW = {"machine_id_sha256": "a" * 64, "product_uuid_sha256": "b" * 64, "hardware_bound": True}

    def repo_with(self, d, rel, data: bytes):
        subprocess.run(["git", "init", "-q", d], check=True)
        Path(d, rel).parent.mkdir(parents=True, exist_ok=True)
        Path(d, rel).write_bytes(data)
        subprocess.run(["git", "-C", d, "add", rel], check=True)
        subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                        "commit", "-q", "-m", "a"], check=True)

    def test_attestation_strict(self):
        """F8 / F20 / R02: only a reviewed, accepted, committed, sha-bound, hardware-bound record passes."""
        with tempfile.TemporaryDirectory() as d:
            self.repo_with(d, "att/HOST.md", b"attest")
            good = {"reviewed": True, "accepted": True, "path": "att/HOST.md",
                    "sha256": hashlib.sha256(b"attest").hexdigest(), "acceptance_record": "reviews/X.md",
                    "machine": self.HW}
            self.assertEqual(L.attestation_valid(good, repo_root=d, machine=self.HW), (True, []))
            bad = [None, {}, dict(good, accepted="REJECTED"), dict(good, reviewed="false"), dict(good, accepted=1),
                   dict(good, sha256="0" * 64), dict(good, path="att/MISSING.md"), dict(good, acceptance_record=""),
                   dict(good, machine=dict(self.HW, machine_id_sha256="c" * 64))]
            for b in bad:
                self.assertFalse(L.attestation_valid(b, repo_root=d, machine=self.HW)[0], b)
            soft = dict(self.HW, hardware_bound=False, product_uuid_sha256=None)
            self.assertFalse(L.attestation_valid(dict(good, machine=soft), repo_root=d, machine=soft)[0])
            Path(d, "att/HOST.md").write_bytes(b"edited, not committed")
            self.assertTrue(L.attestation_valid(good, repo_root=d, machine=self.HW)[0])   # HEAD blob, not worktree

    def rd(self, **kw):
        base = {"power": L.AC, "free_disk": 10 * 2 ** 30, "boot_id": BOOT,
                "updates": {"guest_updates_shown_disabled": True, "provider_image_updates": L.UNKNOWN}}
        base.update(kw)
        return base

    def test_all_favourable_still_blocked_by_open_decisions(self):
        att = {"provider_image_updates": L.NO_IMAGE_CHANGE}
        r = L.preflight("/", mode="execute", other_job_running=False, launched={"pass": True},
                        host_attestation=att, readings=self.rd(), attestation_check=lambda a: (True, []))
        self.assertFalse(r["pass"])
        self.assertEqual(set(r["blocked"]), {"lowpowermode_0", "thermal_pressure_0", "memory_pressure_normal",
                                             "free_memory_ge_min", "host_exclusive"})

    def test_update_gate(self):
        """F8: PASS only with shown-disabled guest updates AND an accepted attestation carrying the token."""
        tok = {"provider_image_updates": L.NO_IMAGE_CHANGE}

        def gate(upd, att, ok):
            return L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=None,
                               host_attestation=att, readings=self.rd(updates=upd),
                               attestation_check=lambda a: (ok, []))["gates"]["no_automatic_os_install"]
        shown = {"guest_updates_shown_disabled": True}
        self.assertEqual(gate(shown, tok, True), L.PASS)
        self.assertEqual(gate(shown, tok, False), L.UNKNOWN)
        self.assertEqual(gate(shown, {"provider_image_updates": "unknown"}, True), L.UNKNOWN)
        self.assertEqual(gate(shown, None, True), L.UNKNOWN)
        for upd in ({}, None, {"guest_updates_shown_disabled": "true"}, {"guest_updates_shown_disabled": False}):
            self.assertEqual(gate(upd, tok, True), L.UNKNOWN, upd)

    def test_unknowns_never_pass_and_are_reported(self):
        rd = self.rd(power=None, free_disk=None, boot_id=None, updates={})
        r = L.preflight("/", mode="launcher_preflight", other_job_running=None, launched=None,
                        host_attestation=None, readings=rd)
        for k in ("ac_power", "free_disk_ge_2GiB", "boot_id_recorded", "no_other_campaign_job",
                  "no_automatic_os_install", "host_lifetime_attested"):
            self.assertEqual(r["gates"][k], L.UNKNOWN, k)
            self.assertEqual(r["blocked"].get(k), L.UNKNOWN, k)
        self.assertEqual(L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=None,
                                     host_attestation=None, readings=self.rd(power="ABSENT"))["gates"]["ac_power"],
                         L.OPEN_DECISION)

    def test_launch_gate_modes(self):
        """F15: execute / resume without the launch record FAIL; an unknown mode is refused."""
        for mode in ("execute", "resume"):
            r = L.preflight("/", mode=mode, other_job_running=False, launched=None, host_attestation=None,
                            readings=self.rd())
            self.assertEqual(r["gates"]["launched_by_systemd"], L.FAIL, mode)
        r = L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=None,
                        host_attestation=None, readings=self.rd())
        self.assertNotIn("launched_by_systemd", r["gates"])
        with self.assertRaises(ValueError):
            L.preflight("/", mode=None, other_job_running=False, launched=None, host_attestation=None)

    def test_live_preflight_fails_closed_here(self):
        r = L.preflight("/", mode="execute", other_job_running=False, launched=L.launched_by_systemd(),
                        host_attestation=None)
        self.assertFalse(r["pass"])
        self.assertEqual(r["gates"]["launched_by_systemd"], L.FAIL)
        self.assertEqual(r["gates"]["host_lifetime_attested"], L.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
