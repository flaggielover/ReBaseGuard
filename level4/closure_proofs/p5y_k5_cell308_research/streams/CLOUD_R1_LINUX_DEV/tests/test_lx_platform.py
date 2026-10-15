"""Isolated, target-free tests of the DEV-ONLY Linux platform layer (lx_platform), revision 4.

Synthetic inputs only: planted /proc and /sys text in temporary directories, ``sleep`` / busy-loop child processes,
temporary files and a temporary git repository. No cell, no drift, no science module, no decoy is imported or run;
the historical candidate is only READ (``git show 142d97a9:...``) to pin two constants.
Revision 2 added tests for every code finding of review 59 (F1, F2, F8-F15, F22, F23) and kills its mutants R01-R10.
Revision 3 added tests for review 60's N1-N8, N11-N13 and kills its X01-X09. Revision 4 adds tests for review 61's
P1-P2, P5-P11 and kills its Y01-Y09 (tests/run_mutants.py carries all of them). Trust-relevant inputs are no longer
production parameters: tests change them through `patched()` on module attributes only.

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


class patched:
    """Temporarily replace module attributes of lx_platform (test seams only; production has no such parameters)."""

    def __init__(self, **attrs):
        self.attrs, self.saved = attrs, {}

    def __enter__(self):
        for k, v in self.attrs.items():
            self.saved[k] = getattr(L, k)
            setattr(L, k, v)
        return self

    def __exit__(self, *exc):
        for k, v in self.saved.items():
            setattr(L, k, v)


def attested():
    return patched(root_attestation=lambda ref: (True, []))


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


    def test_unrecorded_namespace_never_proves_death(self):
        """N8: without recorded namespaces, ESRCH or a starttime difference proves nothing (UNKNOWN); a boot-id change
        still proves a reboot."""
        for k in ("pidns", "timens"):
            rec = dict(self.ident, **{k: None})
            self.assertEqual(self.state(ident=rec, exists=False), L.UNKNOWN, k)
            self.assertEqual(self.state(ident=rec, stat=L.proc_stat(4242, stat_text(start=1))), L.UNKNOWN, k)
            self.assertEqual(self.state(ident=rec, boot=OTHER_BOOT), L.DEAD, k)
    def test_malformed_records_prove_nothing(self):
        """P9: a malformed record is UNKNOWN, never DEAD (a bad boot id would otherwise 'prove' a reboot; a negative
        pid would address a process group)."""
        for bad in (dict(self.ident, boot_id="garbage"), dict(self.ident, pid=-4242), dict(self.ident, pid=True),
                    dict(self.ident, pid="4242"), dict(self.ident, starttime_ticks="777"),
                    dict(self.ident, pidns=-1), dict(self.ident, cmdline_sha256="zz")):
            self.assertEqual(self.state(ident=bad, exists=False), L.UNKNOWN, bad)

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
    def setUp(self):
        """The CLEAN logic is tested as it would run once a reviewed journal reader exists (P7)."""
        self._p = patched(JOURNAL_READER_REVIEWED=True)
        self._p.__enter__()

    def tearDown(self):
        self._p.__exit__()

    def test_no_reviewed_journal_reader_never_clean(self):
        """P7: with no reviewed journal reader (the shipped state), a caller-supplied [] cannot make L' silent."""
        a, b, s, j = self.clean_case()
        with patched(JOURNAL_READER_REVIEWED=False):
            r = L.assess(a, b, s, [])
        self.assertEqual(r["status"], "AMBIGUOUS")
        self.assertTrue(any("no reviewed journal reader" in x for x in r["reasons"]))

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

    def test_monotonic_ahead_of_boottime_and_absent_samples(self):
        """X04 / X06: monotonic advancing more than boottime, or samples absent, is AMBIGUOUS, never CLEAN."""
        a, b, s, j = self.clean_case()
        b["clocks"]["monotonic_ns"] += 3 * S
        b["clocks"]["realtime_ns"] += 3 * S                          # keep channel P silent: isolate K'
        self.assertEqual(L.assess(a, b, s, j)["status"], "AMBIGUOUS")
        a, b, s, j = self.clean_case()
        self.assertEqual(L.assess(a, b, None, j)["status"], "AMBIGUOUS")

    def test_live_host_is_never_clean(self):
        """N13: with a well-formed (empty) journal list, this Cloud VM is still never CLEAN (no suspend_stats, no
        power supply), so a regression in those channels is detectable."""
        snap0 = L.snapshot()
        if snap0["power"] not in (None, "ABSENT") and snap0["suspend_success"] is not None:
            self.skipTest("host exposes power and suspend_stats: a CLEAN interval is legitimate here (P10)")
        r = L.assess(snap0, L.snapshot(), [], [])
        self.assertNotEqual(r["status"], "CLEAN")


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

    def test_unrecognised_battery_status_is_unknown(self):
        """N2: only Discharging and the known not-discharging statuses are read; anything else is UNKNOWN."""
        base = {"AC/type": "Mains\n", "AC/online": "1\n", "BAT0/type": "Battery\n"}
        for st in ("Unknown", "garbage", "discharging", "Discharging\0"):
            with tempfile.TemporaryDirectory() as d:
                mkfiles(Path(d), dict(base, **{"BAT0/status": st + "\n"}))
                self.assertIsNone(L.power_source(d), st)
        for st in ("Charging", "Full", "Not charging"):
            with tempfile.TemporaryDirectory() as d:
                mkfiles(Path(d), dict(base, **{"BAT0/status": st + "\n"}))
                self.assertEqual(L.power_source(d), L.AC, st)

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
            with attested():
                ra = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)
            self.assertEqual((ra["effective_limit"], ra["cgroup_min_headroom"]), (1000000000, 1000000000 - 400))

    def test_partial_chain_never_numeric(self):
        """F10: an unreadable limit anywhere, or an unreadable usage at a limited level, gives no number."""
        with tempfile.TemporaryDirectory() as d:
            self.v1(d, drop=("memory/a/memory.limit_in_bytes",))
            with attested():
                r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)
            self.assertEqual((r["effective_limit"], r["cgroup_min_headroom"], r["visible_limit_upper_bound"]),
                             (None, None, None))
        with tempfile.TemporaryDirectory() as d:
            self.v1(d, leaf_use="?\n", mid="2000000000")      # another limited level exists: a partial min is possible
            with attested():
                r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)
            self.assertIsNone(r["cgroup_min_headroom"])

    def test_ancestor_tighter_than_leaf(self):
        with tempfile.TemporaryDirectory() as d:
            self.v1(d, leaf=BIG, mid="500000000")
            with attested():
                r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)
            self.assertEqual(r["effective_limit"], 500000000)

    def test_v2_root_and_memory_high(self):
        with tempfile.TemporaryDirectory() as d:
            mkfiles(Path(d), {"x/y/memory.max": "max\n", "x/y/memory.high": "3000\n", "x/y/memory.current": "10\n",
                              "x/memory.max": "8000\n", "x/memory.high": "max\n", "x/memory.current": "20\n"})
            cg = "0::/x/y\n"
            self.assertIsNone(L.memory_readings(MEMINFO, cg, d)["effective_limit"])        # root not attested
            with attested():
                r = L.memory_readings(MEMINFO, cg, d)
            self.assertEqual(r["cgroup"]["version"], "v2")
            self.assertEqual(r["effective_limit"], 3000)                                  # memory.high binds
            self.assertEqual(r["cgroup_min_headroom"], 2990)
            ch = L.memory_cgroup_chain(cg, d)
            self.assertIsNone(L._chain_values(ch, root_attested=False))                    # helper refuses directly
            self.assertIsNotNone(L._chain_values(ch, root_attested=True))
            Path(d, "x/memory.high").unlink()                                              # unreadable high
            with attested():
                self.assertIsNone(L.memory_readings(MEMINFO, cg, d)["effective_limit"])

    def test_no_rfree_quantity_is_produced(self):
        r = L.memory_readings(MEMINFO, "4:memory:/\n", "/nonexistent")
        self.assertNotIn("free_memory_bytes", r)
        self.assertIn("D-MEM-FREE", r["note"])

    def test_root_attestation_is_derived_never_asserted(self):
        """N3 / P2: there is no caller flag; root_attestation() needs the initial cgroup namespace, D-HOST-LIFETIME
        decided, a valid attestation and its root_cgroup_is_real field. A non-initial or unreadable namespace blocks a
        number whatever the attestation says (live: review 61's unshare probe inflated the limit to MemTotal)."""
        good = ({"root_cgroup_is_real": True}, [])
        dec = frozenset({"D-HOST-LIFETIME"})
        with patched(ns_inode=lambda kind, pid="self": L.INIT_CGROUP_NS, DECIDED=dec, attestation_valid=lambda r: good):
            self.assertEqual(L.root_attestation({"x": 1}), (True, []))
        for ns in (4026532265, None):
            with patched(ns_inode=lambda kind, pid="self", ns=ns: ns, DECIDED=dec, attestation_valid=lambda r: good):
                self.assertFalse(L.root_attestation({"x": 1})[0], ns)
        with patched(ns_inode=lambda kind, pid="self": L.INIT_CGROUP_NS, attestation_valid=lambda r: good):
            self.assertFalse(L.root_attestation({"x": 1})[0])                       # D-HOST-LIFETIME open
        for rec in ({"root_cgroup_is_real": "true"}, {}, None):
            with patched(ns_inode=lambda kind, pid="self": L.INIT_CGROUP_NS, DECIDED=dec,
                         attestation_valid=lambda r, rec=rec: (rec, [])):
                self.assertFalse(L.root_attestation({"x": 1})[0], rec)
        with tempfile.TemporaryDirectory() as d:
            self.v1(d)
            with patched(ns_inode=lambda kind, pid="self": 4026532265, DECIDED=dec, attestation_valid=lambda r: good):
                r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d, attestation_ref={"x": 1})
            self.assertEqual((r["effective_limit"], r["cgroup_min_headroom"], r["cgroup_ns_initial"]),
                             (None, None, False))                                   # Y04
            self.assertTrue(r["root_attestation_reasons"])
            self.assertNotIn("root_attested", L.memory_readings.__code__.co_varnames[:L.memory_readings.__code__
                                                                                    .co_argcount])

    def test_large_v1_limit_is_a_limit(self):
        """X08: a 2 000 000 000-byte v1 limit is a limit, not the 'unlimited' sentinel."""
        with tempfile.TemporaryDirectory() as d:
            self.v1(d, leaf="2000000000")
            with attested():
                r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d)
            self.assertEqual(r["effective_limit"], 2000000000)

    def test_cgroup_resources_whole_chain(self):
        """N3: cpu.max / cpuset / pids.max are read at every level, so an ancestor's limit is visible."""
        with tempfile.TemporaryDirectory() as d:
            mkfiles(Path(d), {"x/y/cgroup.controllers": "cpu pids\n", "x/y/cpu.max": "max 100000\n",
                              "x/y/pids.max": "max\n", "x/cpu.max": "200000 100000\n", "x/pids.max": "512\n"})
            r = L.cgroup_resources("0::/x/y\n", d)
            rows = {row["path"]: row for row in r["v2"]}
            self.assertEqual((rows["/x/y"]["cpu.max"], rows["/x"]["cpu.max"], rows["/x"]["pids.max"]),
                             ("max 100000", "200000 100000", "512"))
            self.assertIsNone(rows["/"]["cpu.max"])                                     # unreadable stays None
# ====================================================================== CPU exclusivity
class TestBusy(unittest.TestCase):
    def test_window_not_lifetime_and_reuse_and_birth(self):
        hz = 100
        t0 = {(10, 1): (1, 1000, "old_hog", "/usr/bin/x"), (11, 2): (1, 0, "spiker", "/opt/y"),
              (12, 3): (99, 0, "mine", None), (99, 2): (1, 0, "campaign", None)}
        t1 = {(10, 1): (1, 1000, "old_hog", "/usr/bin/x"), (11, 2): (1, 300, "spiker", "/opt/y"),
              (12, 3): (99, 900, "mine", None), (99, 2): (1, 900, "campaign", None),
              (13, 50): (1, 200, "newborn", None), (20, 60): (1, 150, "reused_pid", None)}
        busy = {b["comm"]: b for b in L.busy_processes(t0, t1, 5.0, 25, own={(99, 2)}, hz=hz)}
        self.assertEqual(set(busy), {"spiker", "newborn", "reused_pid"})
        self.assertEqual(busy["spiker"]["pct"], 60.0)
        self.assertTrue(busy["newborn"]["born_in_window"])

    def test_exited_in_window_is_reported(self):
        """N7: a process present at t0 and gone at t1 has unknown usage in the window: reported, never dropped."""
        t0 = {(30, 5): (1, 0, "short_hog", None)}
        out = L.busy_processes(t0, {}, 5.0, 25, own=set(), hz=100)
        self.assertEqual(out, [{"pid": 30, "comm": "short_hog", "exe": None, "pct": None, "exited_in_window": True}])

    def test_reused_campaign_pid_does_not_exempt_children(self):
        """N7: own is keyed by (pid, starttime); a child of a reused pid (older than the campaign process) counts."""
        t0 = {(40, 1): (99, 0, "old_child", None)}
        t1 = {(40, 1): (99, 500, "old_child", None)}
        self.assertEqual(len(L.busy_processes(t0, t1, 5.0, 25, own={(99, 50)}, hz=100)), 1)

    def test_exited_child_of_reused_campaign_pid_is_reported(self):
        """Y02: an exited process whose ppid is a campaign pid but which is OLDER than the campaign process is not
        the campaign's child (pid reuse) and is reported."""
        t0 = {(41, 1): (99, 0, "old_exited", None)}
        out = L.busy_processes(t0, {}, 5.0, 25, own={(99, 50)}, hz=100)
        self.assertEqual([o["comm"] for o in out], ["old_exited"])
        self.assertEqual(L.busy_processes({(42, 60): (99, 0, "own_child", None)}, {}, 5.0, 25, own={(99, 50)}, hz=100),
                         [])

    def test_no_reading_or_unsafe_inputs_fail_closed(self):
        self.assertIsNone(L.busy_processes(None, {}, 5, 25, set()))
        self.assertIsNone(L.busy_processes({}, {}, 0, 25, set()))
        self.assertIsNone(L.busy_processes({}, {}, 5, 25, {(1, 1)}))             # own may not contain init
        self.assertIsNone(L.busy_processes({}, {}, 5, 25, {99}))                 # bare pids: malformed
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
        """N4 / X01 / X02: complete only in the initial PID namespace, with one NSpid id and a /proc without
        hidepid / subset; no /proc line or an unreadable namespace is UNKNOWN."""
        mi = "23 28 0:22 / /proc rw,relatime - proc proc rw\n"
        st = "NSpid:\t77\n"
        self.assertTrue(L.proc_view_complete(st, mi, pidns=L.INIT_PID_NS))
        self.assertFalse(L.proc_view_complete(st, mi, pidns=4026532265))           # nested ns with its own /proc
        self.assertFalse(L.proc_view_complete("NSpid:\t77\t3\n", mi, pidns=L.INIT_PID_NS))
        for opt in ("hidepid=2", "subset=pid"):
            self.assertFalse(L.proc_view_complete(st, f"23 28 0:22 / /proc rw,{opt} - proc proc rw\n",
                                                  pidns=L.INIT_PID_NS), opt)
        self.assertIsNone(L.proc_view_complete(st, "23 28 0:22 / /sys rw - sysfs sysfs rw\n", pidns=L.INIT_PID_NS))
        self.assertIsNone(L.proc_view_complete("Name: x\n", mi, pidns=L.INIT_PID_NS))
        self.assertIsNone(L.proc_view_complete(st, mi, pidns=None))

    def test_unreadable_existing_process_fails_the_snapshot(self):
        """N7: a /proc/<pid> that exists but cannot be read makes the whole snapshot None."""
        with tempfile.TemporaryDirectory() as d:
            mkfiles(Path(d), {"7/stat": stat_text(pid=7)})
            self.assertEqual(set(L.cpu_ticks(d)), {(7, 777)})
            Path(d, "8").mkdir()                                                    # exists, no readable stat
            self.assertIsNone(L.cpu_ticks(d))

    def test_live_snapshot(self):
        a = L.cpu_ticks()
        time.sleep(0.2)
        b = L.cpu_ticks()
        view = L.proc_view_complete()
        if a is None or b is None or view is not True:
            self.assertIsNone(L.busy_processes(a, b, 0.2, 25, set(), view_complete=view))   # P10: no reading
            return
        me = next(k for k in b if k[0] == os.getpid())
        self.assertIsInstance(L.busy_processes(a, b, 0.2, 25, {me}, view_complete=view), list)


# ====================================================================== updates, launch context
class TestUpdatesLaunch(unittest.TestCase):
    def settings(self, dump, **mk):
        d = tempfile.mkdtemp()
        root = Path(d, "units")
        paths = {"unit_roots": (str(root),), "uu_binary": str(Path(d, "uu")),
                 "snapd_paths": (str(Path(d, "snapd")),), "cloud_dir": str(Path(d, "cloud")),
                 "livepatch_dir": str(Path(d, "livepatch"))}
        root.mkdir()
        if mk.get("timer"):
            Path(root, "timers.target.wants").mkdir()
            Path(root, "timers.target.wants", "apt-daily-upgrade.timer").write_text("")
        for k in ("snapd", "cloud"):
            if mk.get(k):
                Path(d, k).mkdir()
        if mk.get("livepatch") == "unreadable":
            Path(d, "livepatch").write_text("")                      # exists but cannot be listed
        elif mk.get("livepatch") is not None:
            Path(d, "livepatch").mkdir()
            for n in mk["livepatch"]:
                Path(d, "livepatch", n).mkdir()
        return L.auto_update_settings(dump, use_live_apt=False, **paths)

    def test_positive_evidence_only(self):
        off = 'APT::Periodic "";\nAPT::Periodic::Enable "0";\n'
        self.assertTrue(self.settings(off)["guest_updates_shown_disabled"])
        self.assertTrue(self.settings('APT::Periodic::Unattended-Upgrade "0";\n')["guest_updates_shown_disabled"])
        for kw in ({"timer": True}, {"snapd": True}, {"cloud": True}, {"livepatch": ["kpatch_1"]},
                   {"livepatch": "unreadable"}):                               # X03
            self.assertFalse(self.settings(off, **kw)["guest_updates_shown_disabled"], kw)
        self.assertFalse(self.settings('APT::Periodic::Unattended-Upgrade "1";\n')["guest_updates_shown_disabled"])
        self.assertFalse(self.settings("")["guest_updates_shown_disabled"])                 # nothing positive
        self.assertFalse(L.auto_update_settings(None, use_live_apt=False)["guest_updates_shown_disabled"])

    def test_unit_enabled_from_every_root(self):
        """P8: enabled anywhere -> True; masked -> False; installed without a link -> False; an unreadable root -> None;
        and the state of an update unit that is enabled or unknown is never 'shown disabled'."""
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d, "a"), Path(d, "b")
            a.mkdir()
            b.mkdir()
            roots = (str(a), str(b))
            self.assertIs(L.unit_enabled("x.timer", roots), False)
            Path(b, "x.timer").write_text("")
            self.assertIs(L.unit_enabled("x.timer", roots), False)
            Path(b, "multi-user.target.wants").mkdir()
            Path(b, "multi-user.target.wants", "x.timer").write_text("")
            self.assertIs(L.unit_enabled("x.timer", roots), True)                   # enabled in the SECOND root
            os.symlink("/dev/null", Path(a, "x.timer"))
            self.assertIs(L.unit_enabled("x.timer", roots), False)                  # masked in the first root
            bad = Path(d, "file_not_dir")
            bad.write_text("")
            self.assertIsNone(L.unit_enabled("y.timer", (str(bad),)))
        off = 'APT::Periodic::Enable "0";\n'
        with patched(unit_enabled=lambda u, roots=None: None):
            self.assertFalse(self.settings(off)["guest_updates_shown_disabled"])  # unknown unit state
        with patched(unit_enabled=lambda u, roots=None: u == "unattended-upgrades.service"):
            self.assertFalse(self.settings(off)["guest_updates_shown_disabled"])

    def test_systemctl_path_when_systemd_is_pid1(self):
        for out, want in (("enabled", True), ("static", True), ("masked", False), ("disabled", False),
                          ("bad", None), (None, None)):
            with patched(systemd_is_pid1=lambda *a, **k: True, _systemctl_is_enabled=lambda u, out=out: out):
                self.assertIs(L.unit_enabled("x.timer"), want, out)

    def test_parser_reads_only_whole_dump_lines(self):
        """N13 (renamed): the parser accepts only whole `apt-config dump` lines; apt's own comment handling is apt's,
        and is relied on by reading the dump rather than the configuration files."""
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
                   {"proc_cgroup_text": "0::/system.slice/rebaseguard-mbs308-exec.scope\n"},          # X07
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

    def test_read_back_mismatch_is_detected(self):
        """X05: if the bytes on disk after the rename are not the bytes written, durable_write raises."""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d, "r")

            def corrupt(stage):
                if stage == "renamed":
                    p.write_bytes(b"something else")
            with self.assertRaises(OSError):
                L.durable_write(p, b"x" * 100, fault=corrupt)

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

    def test_r1_recorded_kernel_is_not_this_hosts(self):
        """N13 (renamed and sharpened): the kernel the 2026-10-04 inventory recorded is not this host's, so a pin set
        taken there fails here on that key."""
        inv = json.loads((HERE.parents[2] / "governance" / "new_host_route_cloud_r1" /
                          "CLOUD_HOST_INVENTORY.json").read_text())
        r1_kernel = inv["platform"]["kernel"].split()[1]
        got = L.platform_readings()
        if r1_kernel == got["kernel_release"]:
            self.skipTest("this host runs the r1 kernel (P10: host-dependent)")
        self.assertNotEqual(r1_kernel, got["kernel_release"])
        self.assertIn("kernel_release", L.pin_mismatches(dict(got, kernel_release=r1_kernel), got))

    def test_required_members_and_pin_point(self):
        """N11: a mapped set without libm / libc / the loader is not a pin; pin_point imports a fixed list first."""
        mo = L.mapped_objects()
        libc = next(k for k in mo if k.endswith("libc.so.6"))
        libm = next(k for k in mo if k.endswith("libm.so.6"))
        self.assertIsNone(L.mapped_objects(f"7f00-7f01 r-xp 0 08:01 1 {libc}\n"))
        two = f"7f00-7f01 r-xp 0 08:01 1 {libc}\n7f02-7f03 r-xp 0 08:01 2 {libm}\n"
        self.assertIsNone(L.mapped_objects(two))                               # Y06: no loader
        with self.assertRaises(RuntimeError):
            L.pin_point(())                                                    # P11: an empty list is refused
        with self.assertRaises(RuntimeError):
            L.pin_point()                                                      # P11: no fixed list defined yet
        got = L.pin_point(("json", "hashlib"))                            # both imported statically above
        self.assertIn("libc6", got["dpkg_versions"])
        with self.assertRaises(RuntimeError):
            L.pin_point(("json", "a_module_that_is_not_imported"))

    def test_unknown_interpreter_package_never_matches(self):
        """X09: an interpreter whose dpkg owner is unknown keeps a placeholder whose version is None."""
        pk = L._python_packages(owner_query=lambda: None)
        self.assertIn(L.UNKNOWN_PACKAGE, pk)
        vers = L.dpkg_versions(pk, query=lambda name: None if name == L.UNKNOWN_PACKAGE else "1.0")
        got = dict(L.platform_readings(), dpkg_versions=vers)
        self.assertIn("dpkg_versions", L.pin_mismatches(got, got))


# ====================================================================== attestation and preflight
ACC = f"{L.ACCEPTANCE_REVIEW_DIR}/{L.ACCEPTANCE_REVIEW_PREFIX}"


def git_commit(d, files: dict, msg="c"):
    for rel, data in files.items():
        Path(d, rel).parent.mkdir(parents=True, exist_ok=True)
        Path(d, rel).write_bytes(data)
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                    "commit", "-q", "-m", msg], check=True)


class TestAttestationPreflight(unittest.TestCase):
    HW = {"machine_id_sha256": "a" * 64, "product_uuid_sha256": "b" * 64, "hardware_bound": True}

    def attestation(self, **over) -> bytes:
        rec = {"schema": L.ATTESTATION_SCHEMA, "reviewed": True, "accepted": True, "machine": self.HW,
               "provider_image_updates": L.NO_IMAGE_CHANGE, "root_cgroup_is_real": True}
        rec.update(over)
        return json.dumps(rec).encode()

    def accept(self, sha, verdict=True) -> bytes:
        return (f"review\n{L.ACCEPTANCE_LINE}{sha}\n" + (L.ACCEPTANCE_VERDICT_LINE + "\n" if verdict else "")).encode()

    def check(self, att: bytes, reviews: dict | None = None, same_commit=False, machine=None, ref=None):
        """att committed first; the review files (path -> bytes) in a SECOND commit (or the same one)."""
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "init", "-q", d], check=True)
            sha = hashlib.sha256(att).hexdigest()
            revs = {f"{ACC}1.md": self.accept(sha)} if reviews is None else \
                {k: (v.replace(b"<SHA>", sha.encode()) if isinstance(v, bytes) else v) for k, v in reviews.items()}
            if same_commit:
                git_commit(d, {"att/HOST.json": att, **revs})
            else:
                git_commit(d, {"att/HOST.json": att})
                if revs:
                    git_commit(d, revs)
            with patched(machine_identity=lambda *a, **k: machine or self.HW):
                return L.attestation_valid(ref or {"path": "att/HOST.json", "sha256": sha}, repo_root=d)

    def test_attestation_read_from_committed_files(self):
        rec, why = self.check(self.attestation())
        self.assertEqual(why, [])
        self.assertEqual(rec["provider_image_updates"], L.NO_IMAGE_CHANGE)

    def test_acceptance_is_found_not_named(self):
        """P1 (review 61 probe B1): the attestation cannot designate its acceptance. A file outside the fixed review
        set, a review without the verdict line, a review that REJECTS while quoting the line, a token embedded in a
        longer line (Y03), and an acceptance committed together with the attestation are all refused."""
        ok = b"x\n" + L.ACCEPTANCE_LINE.encode() + b"<SHA>\n" + L.ACCEPTANCE_VERDICT_LINE.encode() + b"\n"
        cases = {
            "outside the set": {"notes/scratch.md": ok},
            "wrong name in the set dir": {f"{L.ACCEPTANCE_REVIEW_DIR}/OTHER.md": ok},
            "no verdict line": {f"{ACC}1.md": b"x\n" + L.ACCEPTANCE_LINE.encode() + b"<SHA>\n"},
            "rejecting review quoting the line": {f"{ACC}1.md": ok + b"VERDICT: REJECTED\n"},
            "token inside a longer line": {f"{ACC}1.md": b"REJECTED -- do NOT read as " + L.ACCEPTANCE_LINE.encode()
                                           + b"<SHA>\n" + L.ACCEPTANCE_VERDICT_LINE.encode() + b"\n"},
            "accepting and a separate rejecting review": {f"{ACC}1.md": ok, f"{ACC}2.md": b"<SHA> REJECTED\n"},
            "token embedded in a non-rejecting line (Y03)": {
                f"{ACC}1.md": b"draft, not final: " + L.ACCEPTANCE_LINE.encode() + b"<SHA>\n"
                + L.ACCEPTANCE_VERDICT_LINE.encode() + b"\n"},
        }
        for name, revs in cases.items():
            rec, why = self.check(self.attestation(), reviews=revs)
            self.assertIsNone(rec, name)
            self.assertTrue(why, name)
        self.assertIsNone(self.check(self.attestation(), same_commit=True)[0])          # same commit as attestation
        self.assertIsNone(self.check(self.attestation(), reviews={})[0])                 # no review at all

    def test_forged_or_unaccepted_attestations_refused(self):
        for att in (b"# README\nnot an attestation\n", self.attestation(schema="other"),
                    self.attestation(accepted="REJECTED"), self.attestation(reviewed="true"),
                    self.attestation(accepted=1), self.attestation(machine=dict(self.HW, machine_id_sha256="c" * 64))):
            self.assertIsNone(self.check(att)[0], att[:40])
        soft = dict(self.HW, hardware_bound=False, product_uuid_sha256=None)
        self.assertIsNone(self.check(self.attestation(machine=soft), machine=soft)[0])
        cloned = dict(self.HW, product_uuid_sha256="d" * 64)             # Y05: same machine-id, other hardware
        self.assertIsNone(self.check(self.attestation(), machine=cloned)[0])
        for ref in (None, {}, {"path": "att/HOST.json"}, {"path": 1, "sha256": "x"},
                    {"path": "att/HOST.json", "sha256": "0" * 64, "accepted": True}):
            self.assertIsNone(L.attestation_valid(ref)[0], ref)

    def test_reference_digest_must_match_the_committed_file(self):
        """M25: an accepted digest does not make a DIFFERENT committed file pass."""
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "init", "-q", d], check=True)
            accepted, other = self.attestation(), self.attestation(provider_image_updates="anything")
            x = hashlib.sha256(accepted).hexdigest()
            git_commit(d, {"att/HOST.json": other, "att/ACCEPTED.json": accepted})
            git_commit(d, {f"{ACC}1.md": self.accept(x)})
            with patched(machine_identity=lambda *a, **k: self.HW):
                rec, why = L.attestation_valid({"path": "att/HOST.json", "sha256": x}, repo_root=d)
                self.assertIsNone(rec)
                self.assertIn("sha256 mismatch", " ".join(why))
                self.assertIsNotNone(L.attestation_valid({"path": "att/ACCEPTED.json", "sha256": x}, repo_root=d)[0])

    def test_uncommitted_edit_is_not_the_record(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "init", "-q", d], check=True)
            att = self.attestation()
            sha = hashlib.sha256(att).hexdigest()
            git_commit(d, {"att/HOST.json": att})
            git_commit(d, {f"{ACC}1.md": self.accept(sha)})
            Path(d, "att/HOST.json").write_bytes(self.attestation(accepted=False))
            with patched(machine_identity=lambda *a, **k: self.HW):
                self.assertIsNotNone(L.attestation_valid({"path": "att/HOST.json", "sha256": sha}, repo_root=d)[0])

    # ---- preflight
    def rd(self, **kw):
        base = {"power": L.AC, "free_disk": 10 * 2 ** 30, "boot_id": BOOT,
                "updates": {"guest_updates_shown_disabled": True, "provider_image_updates": L.UNKNOWN}}
        base.update(kw)
        return base

    def launch(self, **over):
        rec = {"systemd_pid1": True, "unit": "rebaseguard-mbs308-exec.service", "invocation_id": "abc",
               "systemctl": {"MainPID": os.getpid(), "InvocationID": "abc"}, "pass": True}
        rec.update(over)
        return rec

    def gates(self, *, decided=frozenset(), att=(None, ["none"]), upd=None, mode="execute", launched=None,
              fresh=None, **rd):
        fresh = self.launch() if fresh is None else fresh
        with patched(DECIDED=decided, attestation_valid=lambda ref, **k: att,
                     launched_by_systemd=lambda *a, **k: fresh):
            return L.preflight("/", mode=mode, other_job_running=False, launched=launched, attestation_ref={"x": 1},
                               readings=self.rd(**({"updates": upd} if upd is not None else {}), **rd))["gates"]

    def test_no_trust_parameters_in_production(self):
        """P5 / P6: preflight takes no decided / attestation_check parameter."""
        args = L.preflight.__code__.co_varnames[:L.preflight.__code__.co_argcount + L.preflight.__code__
                                                .co_kwonlyargcount]
        for bad in ("decided", "attestation_check", "machine"):
            self.assertNotIn(bad, args)

    def test_decided_is_validated(self):
        """P5: DECIDED must be a frozenset of known D-* ids; a string (substring trick) or an unknown id raises."""
        for bad in ("xxD-HOST-LIFETIMExx", {"D-HOST-LIFETIME"}, frozenset({"D-NOT-A-DECISION"})):
            with self.assertRaises(ValueError):
                self.gates(decided=bad)

    def test_lifetime_gates_open_while_undecided(self):
        good = ({"provider_image_updates": L.NO_IMAGE_CHANGE}, [])
        g = self.gates(att=good)
        self.assertEqual((g["host_lifetime_attested"], g["no_automatic_os_install"]),
                         (L.OPEN_DECISION, L.OPEN_DECISION))
        g = self.gates(att=good, decided=frozenset({"D-MEM-FREE"}))                  # Y01: another decision
        self.assertEqual((g["host_lifetime_attested"], g["no_automatic_os_install"]),
                         (L.OPEN_DECISION, L.OPEN_DECISION))
        dec = frozenset({"D-HOST-LIFETIME"})
        g = self.gates(att=good, decided=dec)
        self.assertEqual((g["host_lifetime_attested"], g["no_automatic_os_install"]), (L.PASS, L.PASS))
        g = self.gates(att=(None, ["x"]), decided=dec)
        self.assertEqual((g["host_lifetime_attested"], g["no_automatic_os_install"]), (L.UNKNOWN, L.UNKNOWN))
        g = self.gates(att=({"provider_image_updates": "unknown"}, []), decided=dec)
        self.assertEqual(g["no_automatic_os_install"], L.UNKNOWN)
        for upd in ({}, {"guest_updates_shown_disabled": "true"}, {"guest_updates_shown_disabled": False}):
            self.assertEqual(self.gates(att=good, decided=dec, upd=upd)["no_automatic_os_install"], L.UNKNOWN, upd)

    def test_all_favourable_still_blocked(self):
        g = self.gates(att=({"provider_image_updates": L.NO_IMAGE_CHANGE}, []))
        blocked = {k for k, v in g.items() if v != L.PASS}
        self.assertEqual(blocked, {"lowpowermode_0", "thermal_pressure_0", "memory_pressure_normal",
                                   "free_memory_ge_min", "host_exclusive", "host_lifetime_attested",
                                   "no_automatic_os_install"})
        self.assertTrue(all(g[k] == L.OPEN_DECISION for k in blocked))

    def test_boot_id_must_be_valid(self):
        for bad in ("", "garbage", 0, False, BOOT.upper()):
            self.assertEqual(self.gates(boot_id=bad)["boot_id_recorded"], L.UNKNOWN, bad)
        self.assertEqual(self.gates()["boot_id_recorded"], L.PASS)

    def test_unknowns_never_pass_and_are_reported(self):
        r = L.preflight("/", mode="launcher_preflight", other_job_running=None, launched=None, attestation_ref=None,
                        readings=self.rd(power=None, free_disk=None, boot_id=None, updates={}))
        for k in ("ac_power", "free_disk_ge_2GiB", "boot_id_recorded", "no_other_campaign_job",
                  "no_automatic_os_install"):
            self.assertEqual(r["gates"][k], L.UNKNOWN, k)
            self.assertEqual(r["blocked"].get(k), L.UNKNOWN, k)
        self.assertEqual(self.gates(power="ABSENT")["ac_power"], L.OPEN_DECISION)
        self.assertEqual(self.gates(free_disk=True)["free_disk_ge_2GiB"], L.UNKNOWN)

    def test_launch_gate_uses_a_fresh_reading(self):
        """P6 / N12 / F15: PASS only if a FRESH launched_by_systemd() verifies and any passed record equals it."""
        self.assertEqual(self.gates()["launched_by_systemd"], L.PASS)
        self.assertEqual(self.gates(launched=self.launch())["launched_by_systemd"], L.PASS)
        self.assertEqual(self.gates(launched=self.launch(invocation_id="zzz"))["launched_by_systemd"], L.FAIL)
        for bad_fresh in ({"pass": True}, self.launch(systemd_pid1=None),
                          self.launch(unit="rebaseguard-mbs308-x.scope"),
                          self.launch(unit="other.service"), self.launch(invocation_id=""),
                          self.launch(systemctl={"MainPID": 1, "InvocationID": "abc"}),
                          self.launch(systemctl={"MainPID": float(os.getpid()), "InvocationID": "abc"}),
                          self.launch(systemctl={"MainPID": os.getpid(), "InvocationID": "zzz"}),
                          self.launch(**{"pass": 1})):
            self.assertEqual(self.gates(fresh=bad_fresh)["launched_by_systemd"], L.FAIL, bad_fresh)
        self.assertNotIn("launched_by_systemd", self.gates(mode="launcher_preflight"))
        self.assertEqual(self.gates(mode="launcher_preflight", launched=True)["launched_by_systemd"], L.FAIL)
        with self.assertRaises(ValueError):
            L.preflight("/", mode=None, other_job_running=False, launched=None, attestation_ref=None)

    def test_live_preflight_fails_closed_here(self):
        r = L.preflight("/", mode="execute", other_job_running=False, launched=None, attestation_ref=None)
        self.assertFalse(r["pass"])
        if L.launched_by_systemd()["pass"] is not True:
            self.assertEqual(r["gates"]["launched_by_systemd"], L.FAIL)
        self.assertEqual(r["gates"]["host_lifetime_attested"], L.OPEN_DECISION)


if __name__ == "__main__":
    unittest.main()
