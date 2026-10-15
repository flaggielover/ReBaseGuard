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
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import zlib
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
LXDIR = os.environ.get("LX_PLATFORM_DIR", str(HERE.parent))     # the mutation harness points this at a mutant copy
sys.path.insert(0, LXDIR)
import lx_platform as L  # noqa: E402

REAL_PROC_VIEW = L.proc_view_complete      # TestBusy patches the module reader; test_proc_view needs the real one

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
                    dict(self.ident, pidns=-1), dict(self.ident, cmdline_sha256="zz"),
                    dict(self.ident, starttime_ticks=True), dict(self.ident, pidns=True),
                    dict(self.ident, timens=False)):                                    # Z11: bools are not ints
            self.assertEqual(self.state(ident=bad, exists=False), L.UNKNOWN, bad)

    def test_review63_shape_rejects_uppercase_digest_and_boot_id(self):
        """Review 63 W02 / W03: the reader writes lower-case hex; an upper-case cmdline digest or boot id is a malformed
        record, so it proves nothing (UNKNOWN), never DEAD by a 'differing' digest or boot id."""
        for bad in (dict(self.ident, cmdline_sha256="C" * 64), dict(self.ident, boot_id=BOOT.upper())):
            self.assertEqual(self.state(ident=bad, exists=False), L.UNKNOWN, bad)
            self.assertEqual(self.state(ident=bad, exists=True), L.UNKNOWN, bad)
        self.assertEqual(self.state(exists=False), L.DEAD)                       # control: the well-formed record

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

    def test_absent_host_channels_are_never_clean(self):
        """An absent power/counter fixture is ambiguous on every runner, without a host-dependent skip."""
        a, b, _, _ = self.clean_case()
        r = L.assess(dict(a, power="ABSENT", suspend_success=None), b, [], [])
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
            self.assertEqual(set(rows), {"/x/y", "/x", "/"})                    # Y09: ancestry is the property
            self.assertEqual((rows["/x/y"]["cpu.max"], rows["/x"]["cpu.max"], rows["/x"]["pids.max"]),
                             ("max 100000", "200000 100000", "512"))
            self.assertIsNone(rows["/"]["cpu.max"])                                     # unreadable stays None
# ====================================================================== CPU exclusivity
class TestBusy(unittest.TestCase):
    def setUp(self):
        """G6: busy_processes reads proc_view_complete() itself; the synthetic cases fix it to True."""
        self._p = patched(proc_view_complete=lambda *a, **k: True)
        self._p.__enter__()

    def tearDown(self):
        self._p.__exit__()

    def test_view_is_read_not_assumed(self):
        """G6 (review 62's nested-namespace probe): an incomplete or unknown view gives no reading, with no argument
        that could assert completeness."""
        for view in (False, None):
            with patched(proc_view_complete=lambda *a, v=view, **k: v):
                self.assertIsNone(L.busy_processes({}, {}, 5, 25, set()), view)
        self.assertNotIn("view_complete", L.busy_processes.__code__.co_varnames[:L.busy_processes.__code__
                                                                                .co_argcount])

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
        unobserved = {(42, 60): (99, 0, "unobserved_parent", None)}
        self.assertEqual([o["comm"] for o in L.busy_processes(unobserved, {}, 5.0, 25, own={(99, 50)}, hz=100)],
                         ["unobserved_parent"])
        observed = {(42, 60): (99, 0, "own_child", None), (99, 50): (1, 0, "campaign", None)}
        self.assertEqual(L.busy_processes(observed, {}, 5.0, 25, own={(99, 50)}, hz=100), [])

    def test_no_reading_or_unsafe_inputs_fail_closed(self):
        self.assertIsNone(L.busy_processes(None, {}, 5, 25, set()))
        self.assertIsNone(L.busy_processes({}, {}, 0, 25, set()))
        self.assertIsNone(L.busy_processes({}, {}, 5, 25, {(1, 1)}))             # own may not contain init
        self.assertIsNone(L.busy_processes({}, {}, 5, 25, {99}))                 # bare pids: malformed

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
        self.assertTrue(REAL_PROC_VIEW(st, mi, pidns=L.INIT_PID_NS))
        self.assertFalse(REAL_PROC_VIEW(st, mi, pidns=4026532265))           # nested ns with its own /proc
        self.assertFalse(REAL_PROC_VIEW("NSpid:\t77\t3\n", mi, pidns=L.INIT_PID_NS))
        for opt in ("hidepid=2", "subset=pid"):
            self.assertFalse(REAL_PROC_VIEW(st, f"23 28 0:22 / /proc rw,{opt} - proc proc rw\n",
                                                  pidns=L.INIT_PID_NS), opt)
        self.assertIsNone(REAL_PROC_VIEW(st, "23 28 0:22 / /sys rw - sysfs sysfs rw\n", pidns=L.INIT_PID_NS))
        self.assertIsNone(REAL_PROC_VIEW("Name: x\n", mi, pidns=L.INIT_PID_NS))
        self.assertIsNone(REAL_PROC_VIEW(st, mi, pidns=None))

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
            with patched(proc_view_complete=lambda *x, **k: view):
                self.assertIsNone(L.busy_processes(a, b, 0.2, 25, set()))            # P10: no reading
            return
        me = next(k for k in b if k[0] == os.getpid())
        with patched(proc_view_complete=lambda *x, **k: view):
            self.assertIsInstance(L.busy_processes(a, b, 0.2, 25, {me}), list)


# ====================================================================== updates, launch context
class TestUpdatesLaunch(unittest.TestCase):
    def setUp(self):
        """File-mode fixtures have a known non-systemd supervisor; systemctl cases override it explicitly."""
        self._supervisor = patched(systemd_is_pid1=lambda *a, **k: False)
        self._supervisor.__enter__()

    def tearDown(self):
        self._supervisor.__exit__()

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
        """Z03 / Z07 / G7 / G9: every enabling state is True; an ACTIVE unit is True even if disabled; a failed query
        is None (never 'disabled'); not-found is False only when no unit file exists in any root."""
        states = [("enabled", True), ("enabled-runtime", True), ("static", True), ("indirect", True),
                  ("alias", True), ("linked", True), ("linked-runtime", True), ("masked", False),
                  ("masked-runtime", False), ("disabled", False), ("bad", None), (None, None)]
        for out, want in states:
            with patched(systemd_is_pid1=lambda *a, **k: True, _systemctl_is_enabled=lambda u, out=out: out,
                         _systemctl_is_active=lambda u: "inactive"):
                self.assertIs(L.unit_enabled("x.timer"), want, out)
        for act in ("active", "activating", "reloading"):
            with patched(systemd_is_pid1=lambda *a, **k: True, _systemctl_is_enabled=lambda u: "disabled",
                         _systemctl_is_active=lambda u, a=act: a):
                self.assertIs(L.unit_enabled("x.timer"), True, act)
        with tempfile.TemporaryDirectory() as d:
            with patched(systemd_is_pid1=lambda *a, **k: True, _systemctl_is_enabled=lambda u: "not-found",
                         _systemctl_is_active=lambda u: "inactive"):
                self.assertIs(L.unit_enabled("x.timer", (d,)), False)
                Path(d, "x.timer").write_text("")
                self.assertIsNone(L.unit_enabled("x.timer", (d,)))

    def test_failed_systemctl_query_is_no_reading(self):
        """Z07: the query itself (not a patched wrapper): no stdout, an OSError or a timeout is None, never a state;
        with systemd as PID 1 a failed query leaves the unit unknown."""
        import types

        def fake(result):
            def run(*a, **k):
                if isinstance(result, BaseException):
                    raise result
                return subprocess.CompletedProcess(a[0], 1, stdout=result, stderr="")
            return types.SimpleNamespace(run=run, SubprocessError=subprocess.SubprocessError,
                                         DEVNULL=subprocess.DEVNULL)
        for res in ("", "\n", OSError("no systemctl"), subprocess.TimeoutExpired("systemctl", 30)):
            with patched(subprocess=fake(res)):
                self.assertIsNone(L._systemctl_query("is-enabled", "x.timer"), repr(res))
                with patched(systemd_is_pid1=lambda *a, **k: True):
                    self.assertIsNone(L.unit_enabled("x.timer", ()), repr(res))
        with patched(subprocess=fake("disabled\n")):
            self.assertEqual(L._systemctl_query("is-enabled", "x.timer"), "disabled")

    def test_file_mode_edge_cases(self):
        """Z02 / Z04 / G7: a .requires entry, a dangling .wants link, and a missing first root before the enabling one
        are all seen; the default search path is the full systemd.unit(5) list."""
        with tempfile.TemporaryDirectory() as d:
            missing, b = str(Path(d, "missing")), Path(d, "b")
            b.mkdir()
            Path(b, "basic.target.requires").mkdir()
            Path(b, "basic.target.requires", "x.timer").write_text("")
            self.assertIs(L.unit_enabled("x.timer", (missing, str(b))), True)        # Z02 and Z04
            Path(b, "timers.target.wants").mkdir()
            os.symlink(str(Path(d, "nowhere")), Path(b, "timers.target.wants", "y.timer"))
            self.assertIs(L.unit_enabled("y.timer", (missing, str(b))), True)        # dangling link counts
        for root in ("/usr/local/lib/systemd/system", "/run/systemd/transient", "/run/systemd/generator.late",
                     "/etc/systemd/system.control"):
            self.assertIn(root, L.UNIT_ROOTS)

    def test_review63_not_found_unit_file_search_complete(self):
        """Review 63 W04 / W05 / W07: with systemd as PID 1, an inactive not-found unit is 'not enabled' only if NO
        root holds a unit file or link: a dangling link counts, a root that is not a directory is unreadable (unknown),
        and a file in an earlier root is not forgotten when a later root lacks it."""
        with tempfile.TemporaryDirectory() as d:
            a, b, empty = Path(d, "a"), Path(d, "b"), Path(d, "empty")
            for x in (a, b, empty):
                x.mkdir()
            os.symlink(str(Path(d, "nowhere")), Path(a, "x.timer"))                        # dangling link
            Path(b, "y.timer").write_text("")                                             # a real file
            as_file = Path(d, "as_file")
            as_file.write_text("")                                                        # a root that is a file
            with patched(systemd_is_pid1=lambda *a, **k: True, _systemctl_is_enabled=lambda u: "not-found",
                         _systemctl_is_active=lambda u: "inactive"):
                self.assertIsNone(L.unit_enabled("x.timer", (str(a), str(empty))))         # W04
                self.assertIsNone(L.unit_enabled("z.timer", (str(as_file), str(empty))))   # W05
                self.assertIsNone(L.unit_enabled("y.timer", (str(b), str(empty))))         # W07
                self.assertIs(L.unit_enabled("z.timer", (str(empty), str(a))), False)      # control: none anywhere

    def test_review63_upholds_and_mask_precedence(self):
        """Review 63 H6 (file mode): an *.upholds link enables the unit; a mask counts only as the HIGHEST-precedence
        entry: a real unit file in an earlier root overrides a /dev/null link in a later one."""
        with tempfile.TemporaryDirectory() as d:
            hi, lo = Path(d, "hi"), Path(d, "lo")
            hi.mkdir(), lo.mkdir()
            Path(lo, "multi-user.target.upholds").mkdir()
            Path(lo, "multi-user.target.upholds", "u.service").write_text("")
            self.assertIs(L.unit_enabled("u.service", (str(hi), str(lo))), True)
            Path(hi, "x.timer").write_text("[Timer]\n")                                   # real file, higher
            os.symlink("/dev/null", Path(lo, "x.timer"))                                  # mask, lower
            Path(lo, "timers.target.wants").mkdir()
            Path(lo, "timers.target.wants", "x.timer").write_text("")
            self.assertIs(L.unit_enabled("x.timer", (str(hi), str(lo))), True)
            os.symlink("/dev/null", Path(hi, "m.timer"))                                  # mask, highest
            Path(lo, "timers.target.wants", "m.timer").write_text("")
            self.assertIs(L.unit_enabled("m.timer", (str(hi), str(lo))), False)           # control: a real mask

    def test_review64_dangling_top_entry_shadows_lower_mask(self):
        """Review 64 RW2: the highest-precedence entry decides masking even when it is a dangling link; a /dev/null
        link in a lower root does not make a wanted unit 'not enabled'."""
        with tempfile.TemporaryDirectory() as d:
            hi, lo = Path(d, "hi"), Path(d, "lo")
            hi.mkdir(), lo.mkdir()
            os.symlink(str(Path(d, "nowhere")), Path(hi, "x.timer"))                       # dangling, highest
            os.symlink("/dev/null", Path(lo, "x.timer"))                                  # mask, lower
            Path(lo, "timers.target.wants").mkdir()
            Path(lo, "timers.target.wants", "x.timer").write_text("")
            self.assertIs(L.unit_enabled("x.timer", (str(hi), str(lo))), True)

    def test_review64_unreadable_unit_root_is_unknown_not_a_crash(self):
        """Review 64 K9: an OSError while reading a unit root (e.g. listable but not searchable) makes the update
        settings unknown; it never escapes auto_update_settings."""
        import errno
        for exc in (PermissionError("synthetic: root not searchable"),
                    OSError(errno.EIO, "synthetic: I/O error")):                          # review 65 RX4

            def boom(*a, exc=exc, **k):
                raise exc
            with patched(unit_enabled=boom):
                try:
                    r = self.settings('APT::Periodic::Enable "0";\n')
                except OSError as e:                                                      # pragma: no cover
                    self.fail(f"OSError escaped auto_update_settings: {e!r}")
            self.assertTrue(all(v is None for v in r["update_units"].values()), r)
            self.assertFalse(r["guest_updates_shown_disabled"])

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

    def test_known_nonsystemd_context_not_launched(self):
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

    def test_changed_kernel_never_matches_the_recorded_pin(self):
        """A changed kernel pin fails on every runner, without a host-dependent skip or inventory input."""
        got = L.platform_readings()
        different = got["kernel_release"] + "-synthetic-changed"
        self.assertIn("kernel_release", L.pin_mismatches(dict(got, kernel_release=different), got))

    def test_required_members_and_pin_point(self):
        """N11: a mapped set without libm / libc / the loader is not a pin; pin_point imports a fixed list first."""
        mo = L.mapped_objects()
        libc = next(k for k in mo if k.endswith("libc.so.6"))
        libm = next(k for k in mo if k.endswith("libm.so.6"))
        self.assertIsNone(L.mapped_objects(f"7f00-7f01 r-xp 0 08:01 1 {libc}\n"))
        two = f"7f00-7f01 r-xp 0 08:01 1 {libc}\n7f02-7f03 r-xp 0 08:01 2 {libm}\n"
        self.assertIsNone(L.mapped_objects(two))                               # Y06: no loader
        with self.assertRaises(RuntimeError):
            with patched(PIN_POINT_MODULES=()):
                L.pin_point()                                                  # P11: an empty list is refused
        with self.assertRaises(RuntimeError):
            L.pin_point()                                                      # P11: no fixed list defined yet
        with patched(PIN_POINT_MODULES=("json", "hashlib")):                 # both imported statically above
            got = L.pin_point()
        self.assertIn("libc6", got["dpkg_versions"])
        with self.assertRaises(RuntimeError):
            with patched(PIN_POINT_MODULES=("json", "a_module_that_is_not_imported")):
                L.pin_point()
        self.assertEqual(L.pin_point.__code__.co_argcount, 0)                   # G8: no caller override

    def test_unknown_interpreter_package_never_matches(self):
        """X09: an interpreter whose dpkg owner is unknown keeps a placeholder whose version is None."""
        pk = L._python_packages(owner_query=lambda: None)
        self.assertIn(L.UNKNOWN_PACKAGE, pk)
        vers = L.dpkg_versions(pk, query=lambda name: None if name == L.UNKNOWN_PACKAGE else "1.0")
        got = dict(L.platform_readings(), dpkg_versions=vers)
        self.assertIn("dpkg_versions", L.pin_mismatches(got, got))


# ====================================================================== attestation and preflight
ACC = f"{L.ACCEPTANCE_REVIEW_DIR}/{L.ACCEPTANCE_REVIEW_PREFIX}"
GIT_FIXTURE_CONFIG = {"gc.auto": "0", "maintenance.auto": "false", "core.hooksPath": os.devnull,
                      "core.fsmonitor": "false"}


def fixture_git(d, *args):
    options = [option for key, value in GIT_FIXTURE_CONFIG.items() for option in ("-c", f"{key}={value}")]
    return subprocess.run(["git", "-C", str(d), *options, *args], check=True)


def git_init(d):
    fixture_git(d, "init", "-q")
    # Local settings also apply to the platform's read-only Git calls in this fixture.
    for key, value in GIT_FIXTURE_CONFIG.items():
        fixture_git(d, "config", "--local", key, value)


def git_commit(d, files: dict, msg="c"):
    for rel, data in files.items():
        Path(d, rel).parent.mkdir(parents=True, exist_ok=True)
        Path(d, rel).write_bytes(data)
    fixture_git(d, "add", "-A")
    fixture_git(d, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                "commit", "-q", "-m", msg)


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
            git_init(d)
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
            "accepting verdict line twice (review 64 K2)": {
                f"{ACC}1.md": ok + L.ACCEPTANCE_VERDICT_LINE.encode() + b"\n"},
            "token embedded in a non-rejecting line (Y03)": {
                f"{ACC}1.md": b"draft, not final: " + L.ACCEPTANCE_LINE.encode() + b"<SHA>\n"
                + L.ACCEPTANCE_VERDICT_LINE.encode() + b"\n"},
        }
        for name, revs in cases.items():
            rec, why = self.check(self.attestation(), reviews=revs)
            self.assertIsNone(rec, name)
            self.assertTrue(why, name)
        self.assertIsNone(self.check(self.attestation(), same_commit=True)[0])          # same commit as attestation
        g = {   # G1 / G3 (review 62)
            "subdirectory of the review dir": {
                f"{L.ACCEPTANCE_REVIEW_DIR}/scratch_x/{L.ACCEPTANCE_REVIEW_PREFIX}n.md": ok},
            "wrong suffix": {f"{ACC}1.txt": ok},
            "two verdict lines": {f"{ACC}1.md": ok + b"Verdict: something else\n"},
            "lower-case rejection elsewhere": {f"{ACC}1.md": ok,
                                               f"{L.ACCEPTANCE_REVIEW_DIR}/notes.md": b"<SHA> rejected\n"},
            "not-accepted verdict in a scratch file": {f"{ACC}1.md": ok,
                                                       f"{L.ACCEPTANCE_REVIEW_DIR}/s/x.txt": b"<SHA> NOT_ACCEPTED\n"},
            "withdrawn": {f"{ACC}1.md": ok + b"acceptance WITHDRAWN\n"},
        }
        for name, revs in g.items():
            self.assertIsNone(self.check(self.attestation(), reviews=revs)[0], name)

    def test_accepting_line_must_post_date_the_attested_blob(self):
        """G2 (review 62 probes G2-G4, Z05): commit order binds the attested BLOB and the accepting LINE, repository-
        wide: a placeholder review whose acceptance is written together with the attestation, an attestation path
        created first and filled later together with the acceptance, an acceptance moved into the set by git mv, and an
        acceptance older than the attestation are all refused."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        line = f"{L.ACCEPTANCE_LINE}{sha}\n{L.ACCEPTANCE_VERDICT_LINE}\n".encode()

        def run(steps):
            with tempfile.TemporaryDirectory() as d:
                git_init(d)
                for st in steps:
                    if st == "mv":
                        Path(d, ACC).parent.mkdir(parents=True, exist_ok=True)
                        fixture_git(d, "mv", "tmp/acc.md", f"{ACC}1.md")
                        git_commit(d, {})
                    else:
                        git_commit(d, st)
                with patched(machine_identity=lambda *a, **k: self.HW):
                    return L.attestation_valid({"path": "att/HOST.json", "sha256": sha}, repo_root=d)[0]
        self.assertIsNotNone(run([{"att/HOST.json": att}, {f"{ACC}1.md": line}]))           # the legitimate order
        self.assertIsNone(run([{f"{ACC}1.md": b"placeholder\n"}, {"att/HOST.json": att, f"{ACC}1.md": line}]))
        self.assertIsNone(run([{"att/HOST.json": b"placeholder"}, {"att/HOST.json": att, f"{ACC}1.md": line}]))
        self.assertIsNone(run([{"att/HOST.json": att, "tmp/acc.md": line}, "mv"]))
        self.assertIsNone(run([{f"{ACC}1.md": line}, {"att/HOST.json": att}]))           # acceptance first
        self.assertIsNone(self.check(self.attestation(), reviews={})[0])                 # no review at all

    def _repo_run(self, att, steps):
        """Synthetic history: each step is a dict (commit those files), ("rm", path), ("mv", src, dst),
        ("branch", name), ("checkout", name) or ("merge", name, extra_files_or_None)."""
        sha = hashlib.sha256(att).hexdigest()
        ident = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            for st in steps:
                if isinstance(st, dict):
                    git_commit(d, st)
                elif st[0] == "rm":
                    fixture_git(d, "rm", "-q", st[1])
                    git_commit(d, {})
                elif st[0] == "mv":
                    Path(d, st[2]).parent.mkdir(parents=True, exist_ok=True)
                    fixture_git(d, "mv", st[1], st[2])
                    git_commit(d, {})
                elif st[0] == "branch":
                    fixture_git(d, "branch", st[1])
                elif st[0] == "checkout":
                    fixture_git(d, "checkout", "-q", st[1])
                elif st[0] == "merge":
                    fixture_git(d, *ident, "merge", "-q", "--no-ff", "--no-commit", st[1])
                    for rel, data in (st[2] or {}).items():
                        Path(d, rel).parent.mkdir(parents=True, exist_ok=True)
                        Path(d, rel).write_bytes(data)
                    fixture_git(d, "add", "-A")
                    fixture_git(d, *ident, "commit", "-q", "-m", "merge")
            with patched(machine_identity=lambda *a, **k: self.HW):
                return L.attestation_valid({"path": "att/HOST.json", "sha256": sha}, repo_root=d)

    def test_review63_order_every_commit_merges_and_side_branches(self):
        """Review 63 H1 / W01: EVERY commit that adds the attested blob precedes EVERY commit that adds the accepting
        line, merges included: an evil merge introducing both (then a copy of the blob and a quote of the line), an
        acceptance made before the blob and quoted later, and an acceptance on a branch forked before the blob are
        refused; an acceptance on a branch forked after the blob, merged later, is accepted."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        line = f"{L.ACCEPTANCE_LINE}{sha}\n{L.ACCEPTANCE_VERDICT_LINE}\n".encode()
        quote = f"quoted: {L.ACCEPTANCE_LINE}{sha}\n".encode()
        base = {"README": b"base\n"}
        evil = [base, ("branch", "side"), ("checkout", "side"), {"s.txt": b"s\n"}, ("checkout", "-"),
                {"m.txt": b"m\n"}, ("merge", "side", {"att/HOST.json": att, f"{ACC}1.md": line}),
                {"att/COPY.json": att}, {"notes/q.md": quote}]
        self.assertIsNone(self._repo_run(att, evil)[0])                                   # RV08
        first = [base, {f"{ACC}1.md": line}, {"att/HOST.json": att}, {"notes/q.md": quote}]
        self.assertIsNone(self._repo_run(att, first)[0])                                  # RV01 (W01)
        side = [base, ("branch", "side"), ("checkout", "side"), {f"{ACC}1.md": line}, ("checkout", "-"),
                {"att/HOST.json": att}, {"notes/q.md": quote}, ("merge", "side", None)]
        self.assertIsNone(self._repo_run(att, side)[0])
        good = [base, {"att/HOST.json": att}, ("branch", "side"), ("checkout", "side"), {f"{ACC}1.md": line},
                ("checkout", "-"), {"m.txt": b"m\n"}, ("merge", "side", None)]
        rec, why = self._repo_run(att, good)
        self.assertIsNotNone(rec, why)                                                    # control: legitimate merge

    def test_review63_veto_words_and_references(self):
        """Review 63 H3 / W06: a review naming the attestation by its full sha in any case or by a >= 8-hex prefix
        vetoes it with any negative word (incl. revoke, refused, unaccepted, declined, needs revision, veto) or with a
        verdict other than the accepting one; unrelated or neutral mentions do not."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        ok = self.accept(sha)
        note = f"{L.ACCEPTANCE_REVIEW_DIR}/notes.md"
        vetoes = {"revoked (W06)": f"{sha} revoked\n", "upper-case abbreviated": f"{sha[:10].upper()} REJECTED\n",
                  "refused": f"{sha}\nrefused\n", "unaccepted": f"{sha} is unaccepted\n",
                  "declined": f"{sha[:8]} declined\n", "needs revision": f"{sha}\nNEEDS_REVISION\n",
                  "veto": f"veto {sha}\n", "other verdict": f"{sha}\nVERDICT: FIT_WITH_CONDITIONS\n"}
        for name, text in vetoes.items():
            self.assertIsNone(self.check(att, reviews={f"{ACC}1.md": ok, note: text.encode()})[0], name)
        for name, text in {"neutral mention": f"{sha} noted\n",
                           "other sha rejected": f"{'0' * 12} REJECTED\n"}.items():
            rec, why = self.check(att, reviews={f"{ACC}1.md": ok, note: text.encode()})
            self.assertIsNotNone(rec, (name, why))

    def test_review63_rejection_is_permanent(self):
        """Review 63 H3: a rejection anywhere in HEAD's full history under the review directory survives `git rm`,
        `git mv` out of the directory, and a side branch that adds and removes it; an unreadable (non-UTF-8)
        historical review blob refuses verification; an unrelated removed review does not."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        ok = self.accept(sha)
        veto = f"{L.ACCEPTANCE_REVIEW_DIR}/veto.md"
        bad = f"{sha} REJECTED\n".encode()
        cases = {
            "removed": [{"att/HOST.json": att}, {veto: bad}, ("rm", veto), {f"{ACC}1.md": ok}],
            "moved out": [{"att/HOST.json": att}, {veto: bad}, ("mv", veto, "elsewhere/veto.md"), {f"{ACC}1.md": ok}],
            "side branch": [{"att/HOST.json": att}, ("branch", "side"), ("checkout", "side"), {veto: bad},
                            ("rm", veto), ("checkout", "-"), {f"{ACC}1.md": ok}, ("merge", "side", None)],
            "non-UTF-8 history": [{"att/HOST.json": att}, {veto: b"\xff\xfe" + bad}, ("rm", veto),
                                  {f"{ACC}1.md": ok}],
        }
        for name, steps in cases.items():
            self.assertIsNone(self._repo_run(att, steps)[0], name)
        rec, why = self._repo_run(att, [{"att/HOST.json": att}, {veto: b"draft notes\n"}, ("rm", veto),
                                        {f"{ACC}1.md": ok}])
        self.assertIsNotNone(rec, why)                                                    # control

    def test_review63_verdict_like_lines_refuse_acceptance(self):
        """Review 63 H7: an accepting file holds exactly one verdict-like line: formatted verdicts (**Verdict:**,
        '## Verdict -', '* VERDICT:') and bare KEY: VALUE verdict lines (DEV_CODE: NOT_FAIL_CLOSED) refuse it."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        for extra in ("**Verdict:** fine", "## Verdict - fine", "* VERDICT: ok", "DEV_CODE: NOT_FAIL_CLOSED"):
            body = self.accept(sha) + (extra + "\n").encode()
            self.assertIsNone(self.check(att, reviews={f"{ACC}1.md": body})[0], extra)
        rec, why = self.check(att, reviews={f"{ACC}1.md": self.accept(sha) + b"Reviewed on a synthetic host.\n"})
        self.assertIsNotNone(rec, why)                                                    # control: plain prose

    def _valid_in(self, d, att):
        with patched(machine_identity=lambda *a, **k: self.HW):
            return L.attestation_valid({"path": "att/HOST.json", "sha256": hashlib.sha256(att).hexdigest()},
                                       repo_root=d)

    def test_review64_order_ignores_reading_configuration(self):
        """Review 64 K1: neither `log.showRoot=false` in the repository's own configuration nor a textconv driver
        set through `.git/info/attributes` can hide the commit that introduced an acceptance written before the blob;
        a shallow clone, whose boundary commit introduces everything it holds, refuses (never accepts)."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        line = f"{L.ACCEPTANCE_LINE}{sha}\n{L.ACCEPTANCE_VERDICT_LINE}\n".encode()
        quote = f"quoted: {L.ACCEPTANCE_LINE}{sha}\n".encode()
        with tempfile.TemporaryDirectory() as d:                                          # root commit hidden
            git_init(d)
            git_commit(d, {f"{ACC}1.md": line})
            git_commit(d, {"att/HOST.json": att})
            git_commit(d, {"notes/q.md": quote})
            fixture_git(d, "config", "--local", "log.showRoot", "false")
            self.assertIsNone(self._valid_in(d, att)[0])                                  # RV23
        with tempfile.TemporaryDirectory() as d:                                          # textconv hides a commit
            git_init(d)
            git_commit(d, {"README": b"base\n"})
            git_commit(d, {f"{ACC}1.md": line})
            git_commit(d, {"att/HOST.json": att})
            git_commit(d, {"notes/q.md": quote})
            Path(d, ".git", "info").mkdir(exist_ok=True)
            Path(d, ".git", "info", "attributes").write_text(f"{ACC}1.md diff=hide\n")    # only the acceptance
            fixture_git(d, "config", "--local", "diff.hide.textconv", "true")
            self.assertIsNone(self._valid_in(d, att)[0])                                  # RV24
        with tempfile.TemporaryDirectory() as d:                                          # shallow clone
            src, dst = Path(d, "src"), Path(d, "dst")
            src.mkdir()
            git_init(src)
            git_commit(src, {"att/HOST.json": att})
            git_commit(src, {f"{ACC}1.md": line})
            self.assertIsNotNone(self._valid_in(src, att)[0])                             # control: full history
            fixture_git(d, "clone", "-q", "--depth", "1", src.as_uri(), str(dst))
            self.assertIsNone(self._valid_in(dst, att)[0])

    def test_review64_shallow_history_refuses_deleted_preboundary_rejection(self):
        """Review 64 follow-up: a rejecting review committed and then deleted before a shallow clone's boundary is
        invisible to the history scan although the HEAD tree is identical; history completeness is therefore a
        precondition. Full history: the rejection refuses, and a valid acceptance (positive control) is accepted. A
        depth-2 clone and an unreadable completeness answer refuse as unavailable evidence."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        veto = f"{L.ACCEPTANCE_REVIEW_DIR}/veto.md"
        with tempfile.TemporaryDirectory() as d:
            good, bad, cut = Path(d, "good"), Path(d, "bad"), Path(d, "cut")
            for repo, rejected in ((good, False), (bad, True)):
                repo.mkdir()
                git_init(repo)
                git_commit(repo, {"att/HOST.json": att})
                git_commit(repo, {veto: (f"{sha} REJECTED\n" if rejected else "draft notes\n").encode()})
                fixture_git(repo, "rm", "-q", veto)
                git_commit(repo, {})
                git_commit(repo, {f"{ACC}1.md": self.accept(sha)})
            rec, why = self._valid_in(good, att)
            self.assertIsNotNone(rec, why)                                                # positive control
            rec, why = self._valid_in(bad, att)
            self.assertIsNone(rec)
            self.assertTrue(any("HISTORICAL" in w for w in why), why)                     # full history sees it
            fixture_git(d, "clone", "-q", "--depth", "2", bad.as_uri(), str(cut))
            same_tree = [subprocess.run(["git", "-C", str(x), "rev-parse", "HEAD^{tree}"], capture_output=True,
                                        text=True, check=True).stdout for x in (bad, cut)]
            self.assertEqual(same_tree[0], same_tree[1])
            rec, why = self._valid_in(cut, att)
            self.assertIsNone(rec)                                                        # RV29
            self.assertTrue(any("history completeness" in w for w in why), why)
            original = L._git

            def no_answer(repo_root, *args):
                return None if args[:2] == ("rev-parse", "--is-shallow-repository") else original(repo_root, *args)
            with patched(_git=no_answer):
                rec, why = self._valid_in(good, att)
            self.assertIsNone(rec)                                                        # RV30
            self.assertTrue(any("history completeness" in w for w in why), why)

    def _rejected_then_deleted(self, d, att):
        """att -> rejecting review -> git rm -> valid acceptance; returns the four commit ids."""
        sha = hashlib.sha256(att).hexdigest()
        veto = f"{L.ACCEPTANCE_REVIEW_DIR}/veto.md"
        git_init(d)
        ids = []
        for files, rm in (({"att/HOST.json": att}, None), ({veto: f"{sha} REJECTED\n".encode()}, None),
                          ({}, veto), ({f"{ACC}1.md": self.accept(sha)}, None)):
            if rm:
                fixture_git(d, "rm", "-q", rm)
            git_commit(d, files)
            ids.append(subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"], capture_output=True, text=True,
                                      check=True).stdout.strip())
        return ids

    @staticmethod
    def _forge_commit_graph(d, cut_commit):
        """Review 65 L1 (the reviewer's construction): a git-written v1 commit-graph whose CDAT parent entry for
        ``cut_commit`` is rewritten to 'no parent', with a recomputed checksum. Objects, refs and HEAD unchanged."""
        fixture_git(d, "-c", "commitGraph.generationVersion=1", "commit-graph", "write", "--reachable",
                    "--no-changed-paths")
        gp = Path(d, ".git", "objects", "info", "commit-graph")
        b = bytearray(gp.read_bytes())
        assert b[:4] == b"CGPH" and b[4] == 1 and b[5] == 1
        chunks = {}
        for i in range(b[6] + 1):
            cid, off = struct.unpack(">4sQ", b[8 + 12 * i: 20 + 12 * i])
            chunks[cid] = off
        n = struct.unpack(">I", b[chunks[b"OIDF"] + 255 * 4: chunks[b"OIDF"] + 256 * 4])[0]
        oids = [bytes(b[chunks[b"OIDL"] + 20 * i: chunks[b"OIDL"] + 20 * i + 20]).hex() for i in range(n)]
        struct.pack_into(">II", b, chunks[b"CDAT"] + 36 * oids.index(cut_commit) + 20, 0x70000000, 0x70000000)
        b[-20:] = hashlib.sha1(bytes(b[:-20])).digest()
        gp.chmod(0o644)
        gp.write_bytes(bytes(b))

    def test_review65_forged_graph_and_rewritten_object_refuse(self):
        """Review 65 L1: a forged commit-graph or a rewritten loose blob hides a deleted rejection while the HEAD id
        and tree are unchanged and the repository is not shallow. The graph is never read (review 66 M1), so the
        forged graph changes nothing and the rejection refuses as HISTORICAL (review 67 N5: not through fsck's graph
        verification); a rewritten object fails the fsck precondition. Positive control: an honest commit-graph changes
        nothing."""
        att = self.attestation()
        with tempfile.TemporaryDirectory() as d:
            ids = self._rejected_then_deleted(Path(d), att)
            self.assertIsNone(self._valid_in(d, att)[0])                                  # full history: refused
            self._forge_commit_graph(d, ids[2])
            rec, why = self._valid_in(d, att)
            self.assertIsNone(rec)                                  # graph never read (review 66 M1): HISTORICAL
            self.assertTrue(any("HISTORICAL" in w for w in why), why)                     # RV52
            Path(d, ".git", "objects", "info", "commit-graph").unlink()
            oid = subprocess.run(["git", "-C", d, "rev-parse", f"{ids[1]}:{L.ACCEPTANCE_REVIEW_DIR}/veto.md"],
                                 capture_output=True, text=True, check=True).stdout.strip()
            obj = Path(d, ".git", "objects", oid[:2], oid[2:])
            obj.chmod(0o644)
            obj.write_bytes(zlib.compress(b"blob 6\0draft\n"))
            rec, why = self._valid_in(d, att)
            self.assertIsNone(rec)                                                        # RV31 (object)
            self.assertTrue(any("history completeness" in w for w in why), why)
        with tempfile.TemporaryDirectory() as d:                                          # control
            git_init(d)
            git_commit(d, {"att/HOST.json": att})
            git_commit(d, {f"{ACC}1.md": self.accept(hashlib.sha256(att).hexdigest())})
            fixture_git(d, "commit-graph", "write", "--reachable")
            rec, why = self._valid_in(d, att)
            self.assertIsNotNone(rec, why)

    def test_review65_local_fsck_or_promisor_configuration_refuses(self):
        """Review 65 L1 / L6: repository-local `fsck.*` keys (which could downgrade fsck) and partial-clone /
        promisor keys refuse, including `extensions.partialClone` alone and a remote not named origin (review 67
        N5); a valid repository without them is accepted."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        for key, value in ((None, None), ("fsck.missingEmail", "ignore"), ("fsck.skipList", os.devnull),
                           ("fsck.fullPathname", "ignore"),
                           ("remote.origin.promisor", "true"), ("remote.origin.partialclonefilter", "blob:none"),
                           ("extensions.partialClone", "origin"), ("remote.upstream.promisor", "true")):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as d:
                git_init(d)
                git_commit(d, {"att/HOST.json": att})
                git_commit(d, {f"{ACC}1.md": self.accept(sha)})
                if key:
                    if key.startswith("extensions."):
                        fixture_git(d, "config", "--local", "core.repositoryformatversion", "1")
                    fixture_git(d, "config", "--local", key, value)
                rec, why = self._valid_in(d, att)
                if key is None:
                    self.assertIsNotNone(rec, why)
                else:
                    self.assertIsNone(rec)                                           # RV32 RV53 RV54 RV58
                    self.assertTrue(any("history completeness" in w for w in why), why)

    def _partial_clone(self, d, att):
        """A blob:none partial clone of a repository whose deleted rejection blob is therefore missing locally, with
        a configured upload-pack that writes a marker when it runs. Returns (clone, marker)."""
        src, dst, marker = Path(d, "src"), Path(d, "dst"), Path(d, "fetched.marker")
        src.mkdir()
        self._rejected_then_deleted(src, att)
        fixture_git(src, "config", "uploadpack.allowFilter", "true")
        fixture_git(d, "clone", "-q", "--no-local", "--filter=blob:none", src.as_uri(), str(dst))
        script = Path(d, "upload-pack.sh")
        script.write_text(f"#!/bin/sh\ntouch '{marker}'\nexec git-upload-pack \"$@\"\n")
        script.chmod(0o755)
        fixture_git(dst, "config", "remote.origin.uploadpack", str(script))
        return dst, marker

    def test_review65_partial_clone_runs_no_configured_command(self):
        """Review 65 L6: a blob:none partial clone (its promisor keys are in its own configuration) is refused by the
        completeness precondition, and the repository-configured upload-pack command does not run."""
        att = self.attestation()
        with tempfile.TemporaryDirectory() as d:
            dst, marker = self._partial_clone(d, att)
            rec, why = self._valid_in(dst, att)
            self.assertIsNone(rec)
            self.assertTrue(any("history completeness" in w for w in why), why)            # RV39
            self.assertFalse(marker.exists(), "a configured command ran during the check")

    def test_review66_lazy_fetch_blocked_even_past_the_precondition(self):
        """Review 66 M4 (RY1): independently of the configuration check, no missing object is fetched lazily: with the
        precondition bypassed, a partial clone's missing rejection blob is unavailable evidence and the configured
        upload-pack does not run."""
        att = self.attestation()
        with tempfile.TemporaryDirectory() as d:
            dst, marker = self._partial_clone(d, att)
            with patched(_history_complete=lambda repo_root: True):
                rec, why = self._valid_in(dst, att)
            self.assertIsNone(rec)
            self.assertFalse(marker.exists(), "a missing object was fetched lazily")       # RV45

    def test_review66_forged_bloom_filter_is_never_read(self):
        """Review 66 M1: a commit-graph's changed-path Bloom filters are not verified by fsck or `commit-graph
        verify`; zeroing the rejection commit's filter would hide it from the history-wide scan. The graph is never
        read, so the rejection still refuses; an honest Bloom graph changes nothing (positive control)."""
        att = self.attestation()
        with tempfile.TemporaryDirectory() as d:
            ids = self._rejected_then_deleted(Path(d), att)
            fixture_git(d, "commit-graph", "write", "--reachable", "--changed-paths")
            gp = Path(d, ".git", "objects", "info", "commit-graph")
            b = bytearray(gp.read_bytes())
            chunks = {}
            for i in range(b[6] + 1):
                cid, off = struct.unpack(">4sQ", b[8 + 12 * i: 20 + 12 * i])
                chunks[cid] = off
            n = struct.unpack(">I", b[chunks[b"OIDF"] + 255 * 4: chunks[b"OIDF"] + 256 * 4])[0]
            oids = [bytes(b[chunks[b"OIDL"] + 20 * i: chunks[b"OIDL"] + 20 * i + 20]).hex() for i in range(n)]
            ends = [struct.unpack(">I", b[chunks[b"BIDX"] + 4 * i: chunks[b"BIDX"] + 4 * i + 4])[0]
                    for i in range(n)]
            k = oids.index(ids[1])
            for j in range(chunks[b"BDAT"] + 12 + (ends[k - 1] if k else 0), chunks[b"BDAT"] + 12 + ends[k]):
                b[j] = 0
            b[-20:] = hashlib.sha1(bytes(b[:-20])).digest()
            gp.chmod(0o644)
            gp.write_bytes(bytes(b))
            rec, why = self._valid_in(d, att)
            self.assertIsNone(rec)                                                        # RV43
            self.assertTrue(any("HISTORICAL" in w for w in why), why)
        with tempfile.TemporaryDirectory() as d:                                          # control
            git_init(d)
            git_commit(d, {"att/HOST.json": att})
            git_commit(d, {f"{ACC}1.md": self.accept(hashlib.sha256(att).hexdigest())})
            fixture_git(d, "commit-graph", "write", "--reachable", "--changed-paths")
            rec, why = self._valid_in(d, att)
            self.assertIsNotNone(rec, why)

    def test_review66_fsmonitor_command_never_runs(self):
        """Review 66 M2: a repository-local core.fsmonitor command (fsck reads the index) never runs during the
        check."""
        att = self.attestation()
        with tempfile.TemporaryDirectory() as d:
            repo, marker = Path(d, "r"), Path(d, "fsmonitor.marker")
            repo.mkdir()
            git_init(repo)
            git_commit(repo, {"att/HOST.json": att})
            git_commit(repo, {f"{ACC}1.md": self.accept(hashlib.sha256(att).hexdigest())})
            script = Path(d, "fsmonitor.sh")
            script.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 1\n")
            script.chmod(0o755)
            fixture_git(repo, "config", "--local", "core.fsmonitor", str(script))      # overrides the fixture's false
            rec, why = self._valid_in(repo, att)
            self.assertIsNotNone(rec, why)
            self.assertFalse(marker.exists(), "the repository's fsmonitor command ran")       # RV44

    def test_review66_configuration_in_includes_and_worktree_scope_refuses(self):
        """Review 66 M3: an `fsck.*` or promisor key reached through `include.path` or the worktree configuration
        scope refuses like one written directly."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        for how in ("include", "worktree"):
            with self.subTest(how=how), tempfile.TemporaryDirectory() as d:
                git_init(d)
                git_commit(d, {"att/HOST.json": att})
                git_commit(d, {f"{ACC}1.md": self.accept(sha)})
                self.assertIsNotNone(self._valid_in(d, att)[0])                           # control before
                if how == "include":
                    inc = Path(d, "extra.cfg")
                    inc.write_text("[fsck]\n\tbadTimezone = ignore\n")
                    fixture_git(d, "config", "--local", "include.path", str(inc))
                else:
                    fixture_git(d, "config", "--local", "core.repositoryformatversion", "1")
                    fixture_git(d, "config", "--local", "extensions.worktreeConfig", "true")
                    fixture_git(d, "config", "--worktree", "fsck.badTimezone", "ignore")
                rec, why = self._valid_in(d, att)
                self.assertIsNone(rec)                                                    # RV48
                self.assertTrue(any("history completeness" in w for w in why), why)

    def test_review66_unreadable_configuration_listing_refuses(self):
        """Review 66 M4 (RY5): a configuration listing that cannot be read is not a clean configuration."""
        att = self.attestation()
        original = L._git

        def no_config(repo_root, *args):
            return None if args[:1] == ("config",) else original(repo_root, *args)
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            git_commit(d, {"att/HOST.json": att})
            git_commit(d, {f"{ACC}1.md": self.accept(hashlib.sha256(att).hexdigest())})
            self.assertIsNotNone(self._valid_in(d, att)[0])                               # control
            with patched(_git=no_config):
                rec, why = self._valid_in(d, att)
            self.assertIsNone(rec)                                                        # RV47
            self.assertTrue(any("history completeness" in w for w in why), why)

    def test_review66_symlink_attestation_is_refused(self):
        """Review 66 M4 (RY3): the attested entry must be a regular file; a symlink whose target text is the
        attestation JSON is not an attestation file."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            Path(d, "att").mkdir()
            os.symlink(att.decode(), Path(d, "att", "HOST.json"))
            git_commit(d, {})
            git_commit(d, {f"{ACC}1.md": self.accept(sha)})
            self.assertIsNone(self._valid_in(d, att)[0])                                  # RV46

    @staticmethod
    def _out(d, *args, data=None) -> str:
        return subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *args], input=data,
                              capture_output=True, check=True).stdout.decode().strip()

    def test_review67_warning_class_tree_name_refuses(self):
        """Review 67 N1: a deleted rejection stored under a tree entry whose NAME is `<review dir>/veto.md` (fsck
        `fullPathname`, a warning) is invisible to the pathspec-limited history scan, while the full listing (and a
        checkout) shows the file; strict fsck refuses the history as unavailable evidence."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        veto = f"{L.ACCEPTANCE_REVIEW_DIR}/veto.md"
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            git_commit(d, {"att/HOST.json": att})
            c1 = self._out(d, "rev-parse", "HEAD")
            blob = self._out(d, "hash-object", "-w", "--stdin", data=f"{sha} REJECTED\n".encode())
            entries = sorted([("att/", b"40000 att\0" + bytes.fromhex(self._out(d, "rev-parse", "HEAD:att"))),
                              (veto, f"100644 {veto}\0".encode() + bytes.fromhex(blob))])
            tree = self._out(d, "hash-object", "-t", "tree", "--literally", "-w", "--stdin",
                             data=b"".join(e for _, e in entries))
            c2 = self._out(d, "commit-tree", tree, "-p", c1, "-m", "veto")
            c3 = self._out(d, "commit-tree", f"{c1}^{{tree}}", "-p", c2, "-m", "rm")
            fixture_git(d, "update-ref", "HEAD", c3)
            git_commit(d, {f"{ACC}1.md": self.accept(sha)})
            self.assertIn(veto, self._out(d, "ls-tree", "-r", "--name-only", c2).split("\n"))
            self.assertEqual(self._out(d, "rev-list", "--full-history", "HEAD", "--", L.ACCEPTANCE_REVIEW_DIR),
                             self._out(d, "rev-parse", "HEAD"))                           # the scan misses c2
            rec, why = self._valid_in(d, att)
            self.assertIsNone(rec)                                                        # RV49
            self.assertTrue(any("history completeness" in w for w in why), why)

    def test_review67_signature_program_never_runs(self):
        """Review 67 N2: with the repository's own `log.showSignature=true` and `gpg.program`, a signed commit selected
        by the order rule's `git log` would run that program after fsck (it could rewrite a verified object); no
        signature program runs, and the legitimate repository is accepted (review 67 N3). Both the attestation commit
        (selected by `--find-object`) and the acceptance commit (selected by `-S`) are signed (review 68 P3)."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            repo, marker = Path(d, "r"), Path(d, "gpg.marker")
            repo.mkdir()
            git_init(repo)

            def sign_head():
                raw = subprocess.run(["git", "-C", str(repo), "cat-file", "commit", "HEAD"], capture_output=True,
                                     check=True).stdout
                sig = b"gpgsig -----BEGIN PGP SIGNATURE-----\n \n iQEz\n -----END PGP SIGNATURE-----\n"
                signed = self._out(repo, "hash-object", "-t", "commit", "-w", "--stdin",
                                   data=raw.replace(b"\n\n", b"\n" + sig + b"\n", 1))
                fixture_git(repo, "update-ref", "HEAD", signed)
            git_commit(repo, {"att/HOST.json": att})
            sign_head()
            git_commit(repo, {f"{ACC}1.md": self.accept(sha)})
            sign_head()
            script = Path(d, "gpg.sh")
            script.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 1\n")
            script.chmod(0o755)
            fixture_git(repo, "config", "--local", "log.showSignature", "true")
            fixture_git(repo, "config", "--local", "gpg.program", str(script))
            rec, why = self._valid_in(repo, att)
            self.assertFalse(marker.exists(), "a repository-configured signature program ran")  # RV50 RV55
            self.assertIsNotNone(rec, why)

    def test_review67_global_attributes_file_is_not_read(self):
        """Review 67 N4: the isolation reads no global attributes file (`core.attributesFile` defaults to
        `$HOME/.config/git/attributes`, and HOME is kept for git)."""
        with tempfile.TemporaryDirectory() as d:
            home, repo = Path(d, "home"), Path(d, "r")
            Path(home, ".config", "git").mkdir(parents=True)
            Path(home, ".config", "git", "attributes").write_text("* diff=probe67\n")
            repo.mkdir()
            git_init(repo)
            with mock.patch.dict(os.environ, {"HOME": str(home)}):
                out = L._git(repo, "check-attr", "diff", "--", "x")
            self.assertEqual(out, b"x: diff: unspecified\n")                              # RV51

    def test_review68_non_directory_review_paths_refuse(self):
        """Review 68 P1: a checkout can show a rejection at a review path that git's scan never lists as a regular
        file there: a symlink (at HEAD or in history), a gitlink, the review directory itself, or one of its ancestors
        being a symlink in some commit. Each is unavailable evidence."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        rd = L.ACCEPTANCE_REVIEW_DIR
        veto = f"{sha} REJECTED\n".encode()
        up = "../" * rd.count("/")
        for case in ("head_symlink", "history_symlink", "history_gitlink", "review_dir_symlink", "ancestor_symlink"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as d:
                git_init(d)
                git_commit(d, {"att/HOST.json": att})
                if case in ("head_symlink", "history_symlink"):
                    git_commit(d, {"notes/veto.txt": veto})
                    Path(d, rd).mkdir(parents=True)
                    os.symlink(f"{up}../notes/veto.txt", Path(d, rd, "veto.md"))
                    git_commit(d, {})
                    if case == "history_symlink":
                        fixture_git(d, "rm", "-q", f"{rd}/veto.md")
                        git_commit(d, {})
                elif case == "history_gitlink":
                    head = self._out(d, "rev-parse", "HEAD")
                    fixture_git(d, "update-index", "--add", "--cacheinfo", f"160000,{head},{rd}/sub")
                    self._out(d, "commit", "-q", "-m", "gitlink")                         # no `add -A`
                    fixture_git(d, "rm", "-q", "--cached", f"{rd}/sub")
                    self._out(d, "commit", "-q", "-m", "rm")
                else:
                    top = rd if case == "review_dir_symlink" else rd.split("/")[0]
                    git_commit(d, {f"alt/{rd}/veto.md" if case == "ancestor_symlink" else "alt/veto.md": veto})
                    Path(d, top).parent.mkdir(parents=True, exist_ok=True)
                    os.symlink("../" * top.count("/") + "alt", Path(d, top))
                    git_commit(d, {})
                    fixture_git(d, "rm", "-q", top)
                    fixture_git(d, "rm", "-q", "-r", "alt")
                    git_commit(d, {})
                git_commit(d, {f"{ACC}1.md": self.accept(sha)})
                rec, why = self._valid_in(d, att)
                self.assertIsNone(rec)                                                    # RV59 RV60
                self.assertTrue(any("UNAVAILABLE" in w for w in why), why)

    def test_review68_strict_fsck_and_forced_git_environment(self):
        """Review 68 P4: (a) `--strict` itself is required: a WARN-class message other than fullPathname (a
        zero-padded tree mode) refuses as unavailable evidence; (b) the forced git environment, including
        GIT_ATTR_NOSYSTEM, which a test cannot observe without writing the system attributes file."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            git_commit(d, {"att/HOST.json": att})
            c1 = self._out(d, "rev-parse", "HEAD")
            tree = self._out(d, "hash-object", "-t", "tree", "--literally", "-w", "--stdin",
                             data=b"040000 att\0" + bytes.fromhex(self._out(d, "rev-parse", "HEAD:att")))
            fixture_git(d, "update-ref", "HEAD", self._out(d, "commit-tree", tree, "-p", c1, "-m", "padded"))
            git_commit(d, {f"{ACC}1.md": self.accept(sha)})
            rec, why = self._valid_in(d, att)
            self.assertIsNone(rec)                                                        # RV56
            self.assertTrue(any("history completeness" in w for w in why), why)
        forced = {k: L._git_env().get(k) for k in ("GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_ATTR_NOSYSTEM",
                                                    "GIT_GRAFT_FILE", "GIT_NO_LAZY_FETCH")}
        self.assertEqual(forced, {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                                  "GIT_ATTR_NOSYSTEM": "1", "GIT_GRAFT_FILE": os.devnull,
                                  "GIT_NO_LAZY_FETCH": "1"})                              # RV57

    def test_review65_replace_refs_and_grafts_are_ignored(self):
        """Review 65 L2 (RX1, RX2, RX5): a replace graft or an info/grafts entry that cuts the deletion commit, and a
        replace graft that places a pre-blob acceptance after the blob, change nothing: every read, including the
        ancestry check, ignores them."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            ids = self._rejected_then_deleted(Path(d), att)
            fixture_git(d, "replace", "--graft", ids[2])
            self.assertIsNone(self._valid_in(d, att)[0])                                  # RV33
        with tempfile.TemporaryDirectory() as d:
            ids = self._rejected_then_deleted(Path(d), att)
            Path(d, ".git", "info").mkdir(exist_ok=True)
            Path(d, ".git", "info", "grafts").write_text(ids[2] + "\n")
            self.assertIsNone(self._valid_in(d, att)[0])                                  # RV34
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            git_commit(d, {"README": b"x\n"})
            git_commit(d, {f"{ACC}1.md": self.accept(sha)})
            acc = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True,
                                 check=True).stdout.strip()
            git_commit(d, {"att/HOST.json": att})
            blob = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True,
                                  check=True).stdout.strip()
            git_commit(d, {"notes/q.md": f"quoted {L.ACCEPTANCE_LINE}{sha}\n".encode()})
            fixture_git(d, "replace", "--graft", acc, blob)
            self.assertIsNone(self._valid_in(d, att)[0])                                  # RV35

    def test_review65_caller_git_environment_is_ignored(self):
        """Review 65 L3: an inherited GIT_DIR (as in a hook) or object-directory variable cannot redirect the reads
        to another repository."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            bad, good = Path(d, "bad"), Path(d, "good")
            bad.mkdir(), good.mkdir()
            self._rejected_then_deleted(bad, att)
            git_init(good)
            git_commit(good, {"att/HOST.json": att})
            git_commit(good, {f"{ACC}1.md": self.accept(sha)})
            with mock.patch.dict(os.environ, {"GIT_DIR": str(good / ".git"),
                                              "GIT_OBJECT_DIRECTORY": str(good / ".git" / "objects")}):
                rec, why = self._valid_in(bad, att)
            self.assertIsNone(rec, "the caller's GIT_DIR redirected the check")             # RV40
            self.assertTrue(any("HISTORICAL" in w for w in why), why)

    def test_review65_short_exact_listing_refuses(self):
        """Review 65 L2 (RX6): an exact-path listing that omits a reviewed path is unavailable evidence."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        rd = L.ACCEPTANCE_REVIEW_DIR
        original = L._git

        def short(repo_root, *args):
            out = original(repo_root, *args)
            if args[:3] == ("ls-tree", "-z", "HEAD") and out and len(args) > 5:
                return out.split(b"\0")[0] + b"\0"                                         # first entry only
            return out
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            git_commit(d, {"att/HOST.json": att})
            git_commit(d, {f"{ACC}1.md": self.accept(sha), f"{rd}/zz_notes.md": f"{sha} REJECTED\n".encode()})
            with patched(_git=short):
                rec, why = self._valid_in(d, att)
            self.assertIsNone(rec)                                                        # RV38
            self.assertTrue(any("UNAVAILABLE" in w for w in why), why)

    def test_review65_range_like_attestation_path_and_deep_json(self):
        """Review 65 L7: (a) an attestation at `att/x..HEAD` while `att/x` exists is read by its exact path, not as a
        revision range; (b) a deeply nested committed attestation is refused without an exception."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            git_commit(d, {"att/x": b"other\n", "att/x..HEAD": att})
            git_commit(d, {f"{ACC}1.md": self.accept(sha)})
            with patched(machine_identity=lambda *a, **k: self.HW):
                rec, why = L.attestation_valid({"path": "att/x..HEAD", "sha256": sha}, repo_root=d)
            self.assertIsNotNone(rec, why)                                                # RV41
        deep = b"[" * 100000 + b"]" * 100000
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            git_commit(d, {"att/HOST.json": deep})
            try:
                rec, why = L.attestation_valid({"path": "att/HOST.json", "sha256": hashlib.sha256(deep).hexdigest()},
                                               repo_root=d)
            except RecursionError as e:                                                   # pragma: no cover
                self.fail(f"RecursionError escaped attestation_valid: {e!r}")             # RV42
            self.assertIsNone(rec)

    def test_review64_missing_blob_commits_refuse(self):
        """Review 64 RW1: no commit found for the attested blob refuses; `all()` over nothing is not an order."""
        att = self.attestation()
        original = L._commits

        def no_blob(repo_root, *args):
            return [] if any(str(a).startswith("--find-object=") for a in args) else original(repo_root, *args)
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            git_commit(d, {"att/HOST.json": att})
            git_commit(d, {f"{ACC}1.md": self.accept(hashlib.sha256(att).hexdigest())})
            self.assertIsNotNone(self._valid_in(d, att)[0])                               # control
            with patched(_commits=no_blob):
                self.assertIsNone(self._valid_in(d, att)[0])

    def test_review64_non_utf8_historical_review_path_refuses(self):
        """Review 64 RW3: a review path that is not UTF-8 anywhere in the history makes the review evidence
        unavailable; it is never skipped."""
        att = self.attestation()
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            git_commit(d, {"att/HOST.json": att})
            odd = os.path.join(os.fsencode(d), os.fsencode(L.ACCEPTANCE_REVIEW_DIR), b"\xff.md")
            os.makedirs(os.path.dirname(odd), exist_ok=True)
            with open(odd, "wb") as f:
                f.write(f"{hashlib.sha256(att).hexdigest()} REJECTED\n".encode())
            git_commit(d, {})
            os.unlink(odd)
            git_commit(d, {})
            git_commit(d, {f"{ACC}1.md": self.accept(hashlib.sha256(att).hexdigest())})
            rec, why = self._valid_in(d, att)
            self.assertIsNone(rec)
            self.assertTrue(any("UNAVAILABLE" in w for w in why), why)

    def test_review64_side_branch_acceptance_synced_and_merged_refuses(self):
        """Review 64 RW6: an acceptance written on a side branch before the blob existed there, later synced with the
        main line and merged with --no-ff, is refused: every line commit, off the first-parent chain too, counts."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        line = f"{L.ACCEPTANCE_LINE}{sha}\n{L.ACCEPTANCE_VERDICT_LINE}\n".encode()
        steps = [{"README": b"base\n"}, ("branch", "side"), ("checkout", "side"), {f"{ACC}1.md": line},
                 ("checkout", "-"), {"att/HOST.json": att}, ("checkout", "side"), ("merge", "-", None),
                 ("checkout", "-"), ("merge", "side", None)]
        self.assertIsNone(self._repo_run(att, steps)[0])

    def test_review64_sha_inside_longer_hex_run_still_names_it(self):
        """Review 64 K4: a full sha preceded or followed by other hex digits still names the attestation."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        note = f"{L.ACCEPTANCE_REVIEW_DIR}/notes.md"
        for text in (f"blob:a{sha} REJECTED\n", f"{sha}0 rejected\n", f"blob:A{sha.upper()} REJECTED\n"):  # RX3
            self.assertIsNone(self.check(att, reviews={f"{ACC}1.md": self.accept(sha), note: text.encode()})[0],
                              text)

    def test_review64_symlink_is_not_an_accepting_review(self):
        """Review 64 K7: an accepting entry must be a regular file (mode 100644 / 100755); a symlink whose target
        text holds the two lines is not a review. Review 68 P1: once a symlink was committed under the review
        directory, the history stays unavailable evidence after it is replaced; a regular file in a fresh history is
        accepted (control)."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            git_commit(d, {"att/HOST.json": att})
            Path(d, L.ACCEPTANCE_REVIEW_DIR).mkdir(parents=True)
            os.symlink(f"{L.ACCEPTANCE_LINE}{sha}\n{L.ACCEPTANCE_VERDICT_LINE}\n", Path(d, f"{ACC}1.md"))
            git_commit(d, {})
            self.assertIsNone(self._valid_in(d, att)[0])
            os.unlink(Path(d, f"{ACC}1.md"))
            git_commit(d, {f"{ACC}2.md": self.accept(sha)})
            rec, why = self._valid_in(d, att)
            self.assertIsNone(rec)
            self.assertTrue(any("UNAVAILABLE" in w for w in why), why)
        rec, why = self.check(att)
        self.assertIsNotNone(rec, why)                                                    # control: a regular file

    def test_review64_range_like_review_names_do_not_block(self):
        """Review 64 K9: review files named like a revision range (`x`, `x..HEAD`) are ordinary paths; they do not
        make the evidence unavailable."""
        att = self.attestation()
        sha = hashlib.sha256(att).hexdigest()
        rd = L.ACCEPTANCE_REVIEW_DIR
        rec, why = self.check(att, reviews={f"{ACC}1.md": self.accept(sha), f"{rd}/x": b"note\n",
                                            f"{rd}/x..HEAD": b"note\n"})
        self.assertIsNotNone(rec, why)

    def test_forged_or_unaccepted_attestations_refused(self):
        for att in (b"# README\nnot an attestation\n", self.attestation(schema="other"),
                    self.attestation(accepted="REJECTED"), self.attestation(reviewed="true"),
                    self.attestation(accepted=1), self.attestation(machine=dict(self.HW, machine_id_sha256="c" * 64))):
            self.assertIsNone(self.check(att)[0], att[:40])
        soft = dict(self.HW, hardware_bound=False, product_uuid_sha256=None)
        self.assertIsNone(self.check(self.attestation(machine=soft), machine=soft)[0])
        cloned = dict(self.HW, product_uuid_sha256="d" * 64)             # Y05: same machine-id, other hardware
        self.assertIsNone(self.check(self.attestation(), machine=cloned)[0])
        with tempfile.TemporaryDirectory() as d:
            self.repo = Path(d)
            git_init(self.repo)
            for ref in (None, {}, {"path": "att/HOST.json"}, {"path": 1, "sha256": "x"},
                        {"path": "att/HOST.json", "sha256": "0" * 64, "accepted": True}):
                self.assertIsNone(L.attestation_valid(ref, repo_root=self.repo)[0], ref)

    def test_reference_digest_must_match_the_committed_file(self):
        """M25: an accepted digest does not make a DIFFERENT committed file pass."""
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
            accepted, other = self.attestation(), self.attestation(provider_image_updates="anything")
            x = hashlib.sha256(accepted).hexdigest()
            git_commit(d, {"att/HOST.json": other, "att/ACCEPTED.json": accepted})
            git_commit(d, {f"{ACC}1.md": self.accept(x)})
            with patched(machine_identity=lambda *a, **k: self.HW):
                rec, why = L.attestation_valid({"path": "att/HOST.json", "sha256": x}, repo_root=d)
                self.assertIsNone(rec)
                self.assertIn("sha256 mismatch", " ".join(why))
                self.assertIsNotNone(L.attestation_valid({"path": "att/ACCEPTED.json", "sha256": x}, repo_root=d)[0])

    def test_reference_rejects_extra_fields_even_if_otherwise_valid(self):
        """N04: exact reference schema refuses extra assertions on a genuinely accepted committed blob."""
        att = self.attestation()
        ref = {"path": "att/HOST.json", "sha256": hashlib.sha256(att).hexdigest(), "accepted": True}
        rec, why = self.check(att, ref=ref)
        self.assertIsNone(rec)
        self.assertIn("reference must be exactly", " ".join(why))

    def test_absent_blob_is_refused_before_hash_or_json(self):
        """CDEX17: missing committed bytes never reach hashing; this is separate from M25's valid mismatch."""
        hashed = []
        def spy_sha(data):
            hashed.append(data)
            return "0" * 64
        with patched(_git=lambda *a: None, _sha=spy_sha):
            rec, why = L.attestation_valid({"path": "att/ABSENT.json", "sha256": "a" * 64}, repo_root=".")
        self.assertIsNone(rec)
        self.assertEqual(hashed, [])
        self.assertIn("not committed at HEAD", " ".join(why))

    def test_uncommitted_edit_is_not_the_record(self):
        with tempfile.TemporaryDirectory() as d:
            git_init(d)
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

    def readers(self, **kw):
        """G5: host readings are module readers, patched here (preflight has no readings parameter)."""
        r = self.rd(**kw)
        real_boot_id = L.boot_id

        def fake_boot_id(text=None):
            # preflight reads the boot id (no argument), then validates the value it got with boot_id(value)
            if text is None:
                return r["boot_id"]
            return real_boot_id(text) if isinstance(text, str) else None
        return patched(power_source=lambda *a, **k: r["power"], free_disk_bytes=lambda *a, **k: r["free_disk"],
                       boot_id=fake_boot_id, auto_update_settings=lambda *a, **k: r["updates"])

    def gates(self, *, decided=frozenset(), att=(None, ["none"]), upd=None, mode="execute", launched=None,
              fresh=None, **rd):
        fresh = self.launch() if fresh is None else fresh
        with patched(DECIDED=decided, attestation_valid=lambda ref, **k: att,
                     launched_by_systemd=lambda *a, **k: fresh), \
                self.readers(**({"updates": upd} if upd is not None else {}), **rd):
            return L.preflight("/", mode=mode, other_job_running=False, launched=launched,
                               attestation_ref={"x": 1})["gates"]

    def test_no_trust_parameters_in_production(self):
        """P5 / P6: preflight takes no decided / attestation_check parameter."""
        args = L.preflight.__code__.co_varnames[:L.preflight.__code__.co_argcount + L.preflight.__code__
                                                .co_kwonlyargcount]
        for bad in ("decided", "attestation_check", "machine", "readings"):
            self.assertNotIn(bad, args)

    def test_decided_is_validated(self):
        """P5: DECIDED must be a frozenset of known D-* ids; a string (substring trick) or an unknown id raises."""
        for bad in ("xxD-HOST-LIFETIMExx", {"D-HOST-LIFETIME"}, frozenset({"D-NOT-A-DECISION"})):
            with self.assertRaises(ValueError):
                self.gates(decided=bad)
        g = self.gates(decided=frozenset({"D-PIN-POINT", "D-ALLOW-BASE39"}))         # G11: every section-4 id is known
        self.assertEqual(g["host_exclusive"], L.OPEN_DECISION)
        self.assertEqual(len(L.OPEN_DECISIONS), 21)

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
        with self.readers(power=None, free_disk=None, boot_id=None, updates={}):
            r = L.preflight("/", mode="launcher_preflight", other_job_running=None, launched=None,
                            attestation_ref=None)
        for k in ("ac_power", "free_disk_ge_2GiB", "boot_id_recorded", "no_other_campaign_job",
                  "no_automatic_os_install"):
            self.assertEqual(r["gates"][k], L.UNKNOWN, k)
            self.assertEqual(r["blocked"].get(k), L.UNKNOWN, k)
        self.assertEqual(self.gates(power="ABSENT")["ac_power"], L.OPEN_DECISION)
        self.assertEqual(self.gates(free_disk=True)["free_disk_ge_2GiB"], L.UNKNOWN)
        # Q13 / G11: host_exclusive reports EVERY decision it waits on
        self.assertEqual(r["gates"]["host_exclusive"], L.OPEN_DECISION)
        self.assertTrue({"D-EXCL-WINDOW", "D-ALLOW-PATHS", "D-ALLOW-BASE39"} <= set(r["open_decisions"]))
        self.assertTrue(set(r["open_decisions"]) <= set(L.OPEN_DECISIONS))

    def test_launch_gate_uses_a_fresh_reading(self):
        """P6 / N12 / F15: PASS only if a FRESH launched_by_systemd() verifies and any passed record equals it."""
        gates = self.gates()
        self.assertIn("launched_by_systemd", gates)                             # M29: required execute gate
        self.assertEqual(gates.get("launched_by_systemd"), L.PASS)
        self.assertEqual(self.gates(launched=self.launch()).get("launched_by_systemd"), L.PASS)
        self.assertEqual(self.gates(launched=self.launch(invocation_id="zzz")).get("launched_by_systemd"), L.FAIL)
        not_launched = {"systemd_pid1": False, "unit": None, "invocation_id": None, "systemctl": None, "pass": False}
        self.assertEqual(self.gates(launched=self.launch(), fresh=not_launched).get("launched_by_systemd"), L.FAIL)  # P08
        for bad_fresh in ({"pass": True}, self.launch(systemd_pid1=None),
                          self.launch(unit="rebaseguard-mbs308-x.scope"),
                          self.launch(unit="other.service"), self.launch(invocation_id=""),
                          self.launch(systemctl={"MainPID": 1, "InvocationID": "abc"}),
                          self.launch(systemctl={"MainPID": float(os.getpid()), "InvocationID": "abc"}),
                          self.launch(systemctl={"MainPID": os.getpid(), "InvocationID": "zzz"}),
                          self.launch(**{"pass": 1})):
            self.assertEqual(self.gates(fresh=bad_fresh).get("launched_by_systemd"), L.FAIL, bad_fresh)
        self.assertNotIn("launched_by_systemd", self.gates(mode="launcher_preflight"))
        gates = self.gates(mode="launcher_preflight", launched=True)
        self.assertIn("launched_by_systemd", gates)                             # Z09: supplied record is checked
        self.assertEqual(gates.get("launched_by_systemd"), L.FAIL)
        with self.assertRaises(ValueError):
            L.preflight("/", mode=None, other_job_running=False, launched=None, attestation_ref=None)

    def test_live_preflight_fails_closed_here(self):
        r = L.preflight("/", mode="execute", other_job_running=False, launched=None, attestation_ref=None)
        self.assertFalse(r["pass"])
        if L.launched_by_systemd()["pass"] is not True:
            self.assertEqual(r["gates"].get("launched_by_systemd"), L.FAIL)
        self.assertEqual(r["gates"]["host_lifetime_attested"], L.OPEN_DECISION)


if __name__ == "__main__":
    unittest.main()
