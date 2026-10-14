"""Isolated, target-free tests of the DEV-ONLY Linux platform layer (lx_platform), revision 6.

Synthetic inputs only: planted /proc and /sys text in temporary directories, ``sleep`` / busy-loop child processes,
temporary files and a temporary git repository. No cell, no drift, no science module, no decoy is imported or run;
the historical candidate is only READ (``git show 142d97a9:...``) to pin two constants.
Revision 2 added tests for every code finding of review 59 (F1, F2, F8-F15, F22, F23) and kills its mutants R01-R10.
Revision 3 added tests for the delta review 60's findings N1-N8, N11-N13 and kills its surviving mutants X01-X09
(tests/run_mutants.py carries all of them).
Revision 4 adds independent regression cases for review 61's ownership, record-schema, arithmetic, completeness,
host-cap and sample-order findings, and requires independently observed launch evidence at the public preflight.
Revision 5 adds bounded fixtures for intermediate clock/counter evidence and ambiguous supplied proc/snapshot
records (review 62, F1-F5). These helper-input tests do not establish native Linux or operational acceptance;
trusted-wrapper provenance for raw memory flags, decision/checker/reading seams and fixed imports remains required.

Revision 6 adds delimiter/ASCII refusal evidence for R5-C1; the separate wrapper tests verify synthetic provenance
and restricted public composition without completing any operational condition.

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
from unittest import mock

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


    def test_unrecorded_namespace_never_proves_death(self):
        """N8: without recorded namespaces, ESRCH or a starttime difference proves nothing (UNKNOWN); a boot-id change
        still proves a reboot."""
        for k in ("pidns", "timens"):
            rec = dict(self.ident, **{k: None})
            self.assertEqual(self.state(ident=rec, exists=False), L.UNKNOWN, k)
            self.assertEqual(self.state(ident=rec, stat=L.proc_stat(4242, stat_text(start=1))), L.UNKNOWN, k)
            self.assertEqual(self.state(ident=rec, boot=OTHER_BOOT), L.DEAD, k)

    def test_malformed_current_boot_never_proves_death(self):
        """P2: unrecognised current boot evidence is UNKNOWN, not a positive reboot."""
        for bad in ("garbage", BOOT.upper(), 0, False, [], {}, float("nan")):
            with self.subTest(boot=bad):
                self.assertEqual(self.state(boot=bad), L.UNKNOWN)

    def test_malformed_recorded_boot_never_proves_death(self):
        for bad in ("garbage", BOOT.upper(), 1, False, []):
            with self.subTest(boot=bad):
                self.assertEqual(self.state(ident=dict(self.ident, boot_id=bad)), L.UNKNOWN)

    def test_unrecognised_task_state_is_unknown(self):
        for bad in ("?", "garbage", "", None):
            with self.subTest(state=bad):
                st = dict(L.proc_stat(4242, stat_text()), state=bad)
                self.assertEqual(self.state(stat=st), L.UNKNOWN)

    def test_invalid_identity_schema_is_unknown(self):
        bad_records = [None, [], "identity", True, {},
                       dict(self.ident, pid=True), dict(self.ident, pid=-1), dict(self.ident, pid="4242"),
                       dict(self.ident, starttime_ticks=True), dict(self.ident, starttime_ticks=-1),
                       dict(self.ident, starttime_ticks="777"), dict(self.ident, cmdline_sha256="garbage"),
                       dict(self.ident, pidns=False), dict(self.ident, timens="4026531834")]
        for rec in bad_records:
            with self.subTest(record=rec):
                self.assertEqual(L.identity_state(rec, current_boot=BOOT, exists=lambda p: True,
                    stat=lambda p: L.proc_stat(4242, stat_text()), cmd=lambda p: "c" * 64, current_ns=NS), L.UNKNOWN)

    def test_invalid_stat_schema_is_unknown(self):
        valid = L.proc_stat(4242, stat_text())
        for st in ({}, [], "stat", dict(valid, pid=4243), dict(valid, starttime=True),
                   dict(valid, starttime=-1), dict(valid, utime=-1), dict(valid, stime="5")):
            with self.subTest(stat=st):
                self.assertEqual(L.identity_state(self.ident, current_boot=BOOT, exists=lambda p: True,
                    stat=lambda p: st, cmd=lambda p: "c" * 64, current_ns=NS), L.UNKNOWN)

    def test_stat_parser_rejects_unrecognised_or_mismatched_fields(self):
        for text in (stat_text(pid=4243), stat_text(state="?"), stat_text(utime=-1),
                     stat_text(stime=-1), stat_text(start=-1)):
            with self.subTest(text=text):
                self.assertIsNone(L.proc_stat(4242, text))
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

    def test_intermediate_realtime_excursion_never_clean(self):
        """F1: 0 -> (mono 60, real 90) -> 120 supplies divergence that aligned endpoints cannot erase."""
        a, b, s, j = self.clean_case()
        s[0]["clocks"]["realtime_ns"] = 90 * S
        r = L.assess(a, b, s, j)
        self.assertEqual(r["status"], "AMBIGUOUS")
        self.assertIs(r["clean"], False)
        self.assertTrue(any(x.startswith("AMBIGUOUS: P") for x in r["reasons"]), r)

    def test_intermediate_boottime_excursion_never_clean(self):
        """F1: recognised intermediate K' evidence must be checked even when the endpoint difference is zero."""
        a, b, s, j = self.clean_case()
        s[0]["clocks"]["boottime_ns"] = 90 * S
        r = L.assess(a, b, s, j)
        self.assertEqual(r["status"], "CONTAMINATED")
        self.assertIs(r["clean"], False)
        self.assertTrue(any(x.startswith("CONTAMINATED: K'") for x in r["reasons"]), r)

    def test_intermediate_suspend_counter_reset_is_ambiguous(self):
        """F2: supplied 0 -> 1 -> 0 counter evidence is inconsistent, despite matching endpoints."""
        a, b, s, j = self.clean_case()
        s[0]["suspend_success"] = 1
        r = L.assess(a, b, s, j)
        self.assertEqual(r["status"], "AMBIGUOUS")
        self.assertIs(r["clean"], False)
        self.assertTrue(any(x.startswith("AMBIGUOUS: S'") for x in r["reasons"]), r)

    def test_nondecreasing_suspend_counter_increase_is_contaminated(self):
        """F2 control: a recognised 0 -> 1 -> 1 increase is positive suspend evidence, not a reset."""
        a, b, s, j = self.clean_case()
        s[0]["suspend_success"] = b["suspend_success"] = 1
        r = L.assess(a, b, s, j)
        self.assertEqual(r["status"], "CONTAMINATED")
        self.assertIs(r["clean"], False)
        self.assertTrue(any(x.startswith("CONTAMINATED: S'") for x in r["reasons"]), r)

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

    def test_malformed_boot_readings_never_clean(self):
        """P3: matching malformed boot strings do not become positive interval evidence."""
        for bad in ("garbage", "", BOOT.upper(), False, 0):
            with self.subTest(boot=bad):
                a, b, s, j = self.clean_case()
                for record in (a, *s, b):
                    record["boot_id"] = bad
                self.assertEqual(L.assess(a, b, s, j)["status"], "AMBIGUOUS")

    def test_nonfinite_or_boolean_clock_readings_never_clean(self):
        for bad in (float("nan"), float("inf"), -float("inf"), True, False, "120000000000", None):
            for key in ("monotonic_ns", "boottime_ns", "realtime_ns"):
                for where in ("start", "end", "sample"):
                    with self.subTest(value=bad, clock=key, record=where):
                        a, b, s, j = self.clean_case()
                        record = {"start": a, "end": b, "sample": s[0]}[where]
                        record["clocks"][key] = bad
                        self.assertEqual(L.assess(a, b, s, j)["status"], "AMBIGUOUS")

    def test_invalid_suspend_counter_readings_never_clean(self):
        for bad in (False, True, 0.5, float("nan"), float("inf"), "0", -1, None):
            with self.subTest(count=bad):
                a, b, s, j = self.clean_case()
                for record in (a, *s, b):
                    record["suspend_success"] = bad
                self.assertEqual(L.assess(a, b, s, j)["status"], "AMBIGUOUS")

    def test_invalid_sample_suspend_counter_never_clean(self):
        for bad in (False, "0", -1, None):
            with self.subTest(count=bad):
                a, b, s, j = self.clean_case()
                s[0]["suspend_success"] = bad
                self.assertEqual(L.assess(a, b, s, j)["status"], "AMBIGUOUS")

    def test_malformed_interval_records_never_clean(self):
        for bad in (None, [], "snapshot", True, {}, {"clocks": None}):
            for where in ("start", "end", "sample"):
                with self.subTest(record=bad, position=where):
                    a, b, s, j = self.clean_case()
                    if where == "start":
                        a = bad
                    elif where == "end":
                        b = bad
                    else:
                        s = [bad]
                    r = L.assess(a, b, s, j)
                    self.assertEqual(r["status"], "AMBIGUOUS")
                    self.assertIs(r["clean"], False)

    def test_samples_out_of_order_never_clean(self):
        """P6/Y03: each spacing is small, but the sample occurs after the end."""
        a, b, _, j = self.clean_case()
        r = L.assess(a, b, [snap(150 * S, 150 * S, 150 * S)], j)
        self.assertEqual(r["status"], "AMBIGUOUS")
        self.assertTrue(any("out of order" in reason for reason in r["reasons"]))

    def test_live_host_is_never_clean(self):
        """N13: with a well-formed (empty) journal list, this Cloud VM is still never CLEAN (no suspend_stats, no
        power supply), so a regression in those channels is detectable."""
        r = L.assess(L.snapshot(), L.snapshot(), [], [])
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

    def test_host_memtotal_caps_every_cgroup_limit(self):
        """P6/Y01: a fully readable chain cannot grant more than the host's MemTotal."""
        with tempfile.TemporaryDirectory() as d:
            self.v1(d, leaf="3000", mid="8000")
            r = L.memory_readings("MemTotal: 1000\n", "4:memory:/a/b\n", d, root_attested=True)
            self.assertEqual(r["effective_limit"], 1000)
            self.assertEqual(r["visible_limit_upper_bound"], 1000)

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

    def test_root_attestation_must_be_true(self):
        """N3: a rejected or merely truthy attestation never yields a number."""
        with tempfile.TemporaryDirectory() as d:
            self.v1(d)
            for bad in ("no", "false", "REJECTED", 1, {"accepted": False}, [True]):
                r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d, root_attested=bad)
                self.assertEqual((r["effective_limit"], r["cgroup_min_headroom"]), (None, None), bad)
                self.assertIs(r["root_attested"], False)

    def test_large_v1_limit_is_a_limit(self):
        """X08: a 2 000 000 000-byte v1 limit is a limit, not the 'unlimited' sentinel."""
        with tempfile.TemporaryDirectory() as d:
            self.v1(d, leaf="2000000000")
            r = L.memory_readings(MEMINFO, "4:memory:/a/b\n", d, root_attested=True)
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

    def test_newer_verified_parent_does_not_exempt_older_child(self):
        """Parent identity must match AND precede the child; the new identity check does not replace the age check."""
        t0 = {(99, 50): (1, 0, "campaign", None), (40, 1): (99, 0, "older_child", None)}
        t1 = {(99, 50): (1, 0, "campaign", None), (40, 1): (99, 500, "older_child", None)}
        out = L.busy_processes(t0, t1, 5.0, 25, {(99, 50)}, hz=100)
        self.assertTrue(out is None or any(row["pid"] == 40 for row in out), out)

    def test_reused_campaign_pid_new_children_are_external(self):
        """P1: a new unrelated child of a later PID reuse cannot inherit the old campaign's ownership."""
        t0 = {(99, 2): (1, 0, "old_campaign", None)}
        t1 = {(99, 50): (1, 0, "unrelated_parent", None), (40, 51): (99, 500, "unrelated_child", None)}
        out = L.busy_processes(t0, t1, 5.0, 25, own={(99, 2)}, hz=100)
        self.assertTrue(out is None or any(row["comm"] == "unrelated_child" for row in out), out)

    def test_reused_campaign_pid_exited_child_is_external(self):
        """P1: the t0-only child belongs to the reused parent, so its unknown window usage must not vanish."""
        t0 = {(99, 50): (1, 0, "unrelated_parent", None), (40, 51): (99, 0, "unrelated_child", None)}
        t1 = {(99, 50): (1, 0, "unrelated_parent", None)}
        out = L.busy_processes(t0, t1, 5.0, 25, own={(99, 2)}, hz=100)
        self.assertTrue(out is None or any(row["comm"] == "unrelated_child" and row.get("exited_in_window")
                                          for row in out), out)

    def test_verified_parent_identity_exempts_its_child(self):
        t0 = {(99, 2): (1, 0, "campaign", None), (40, 3): (99, 0, "campaign_child", None)}
        t1 = {(99, 2): (1, 0, "campaign", None), (40, 3): (99, 500, "campaign_child", None)}
        self.assertEqual(L.busy_processes(t0, t1, 5.0, 25, own={(99, 2)}, hz=100), [])

    def test_unobserved_parent_identity_does_not_exempt_child(self):
        t0 = {(40, 3): (99, 0, "unproven_child", None)}
        t1 = {(40, 3): (99, 500, "unproven_child", None)}
        out = L.busy_processes(t0, t1, 5.0, 25, own={(99, 2)}, hz=100)
        self.assertTrue(out is None or any(row["comm"] == "unproven_child" for row in out), out)

    def test_duplicate_pid_identities_in_end_snapshot_are_no_reading(self):
        """F5: a supplied snapshot cannot establish parent ownership with both old and reused PID identities."""
        t0 = {(99, 2): (1, 0, "old_campaign", None)}
        t1 = {(99, 2): (1, 0, "old_campaign", None),
              (99, 50): (1, 0, "unrelated_parent", None),
              (40, 51): (99, 500, "external_child", None)}
        self.assertIsNone(L.busy_processes(t0, t1, 5, 25, own={(99, 2)}, hz=100))

    def test_duplicate_pid_identities_in_start_snapshot_are_no_reading(self):
        """F5: ambiguity in either supplied snapshot invalidates the interval; cpu_ticks itself emits unique PIDs."""
        t0 = {(99, 2): (1, 0, "old_campaign", None),
              (99, 50): (1, 0, "unrelated_parent", None),
              (40, 51): (99, 0, "external_child", None)}
        t1 = {(99, 50): (1, 0, "unrelated_parent", None),
              (40, 51): (99, 500, "external_child", None)}
        self.assertIsNone(L.busy_processes(t0, t1, 5, 25, own={(99, 2)}, hz=100))

    def test_invalid_window_duration_is_no_reading(self):
        t0, t1 = {(40, 1): (1, 0, "hog", None)}, {(40, 1): (1, 500, "hog", None)}
        for bad in (float("nan"), float("inf"), -float("inf"), True, False, "5", None):
            with self.subTest(duration=bad):
                self.assertIsNone(L.busy_processes(t0, t1, bad, 25, set(), hz=100))

    def test_invalid_cpu_threshold_is_no_reading(self):
        t0, t1 = {(40, 1): (1, 0, "hog", None)}, {(40, 1): (1, 500, "hog", None)}
        for bad in (float("nan"), float("inf"), -float("inf"), -1, True, False, "25", None):
            with self.subTest(threshold=bad):
                self.assertIsNone(L.busy_processes(t0, t1, 5, bad, set(), hz=100))

    def test_invalid_tick_frequency_is_no_reading(self):
        t0, t1 = {(40, 1): (1, 0, "hog", None)}, {(40, 1): (1, 500, "hog", None)}
        for bad in (0, -1, float("nan"), float("inf"), True, False, "100"):
            with self.subTest(hz=bad):
                self.assertIsNone(L.busy_processes(t0, t1, 5, 25, set(), hz=bad))

    def test_counter_regression_is_no_reading(self):
        t0, t1 = {(40, 1): (1, 500, "hog", None)}, {(40, 1): (1, 100, "hog", None)}
        self.assertIsNone(L.busy_processes(t0, t1, 5, 25, set(), hz=100))

    def test_invalid_tick_values_are_no_reading(self):
        for bad in (False, -1, 0.5, float("nan"), float("inf"), "500"):
            with self.subTest(ticks=bad):
                self.assertIsNone(L.busy_processes({(40, 1): (1, 0, "hog", None)},
                                                   {(40, 1): (1, bad, "hog", None)}, 5, 25, set(), hz=100))

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

    def test_proc_view_rejects_malformed_nspid(self):
        mi = "23 28 0:22 / /proc rw,relatime - proc proc rw\n"
        for value in ("", "garbage", "0", "-1", "1.5"):
            with self.subTest(nspid=value):
                self.assertIsNot(L.proc_view_complete(f"NSpid:\t{value}\n", mi, pidns=L.INIT_PID_NS), True)

    def test_proc_view_rejects_duplicate_nspid_fields(self):
        """F4: conflicting or repeated supplied status fields cannot establish an unambiguous complete view."""
        mi = "23 28 0:22 / /proc rw,relatime - proc proc rw\n"
        single, nested = "NSpid:\t77\n", "NSpid:\t77 88\n"
        for status in (single + nested, nested + single, single + single):
            with self.subTest(status=status):
                self.assertIsNot(L.proc_view_complete(status, mi, pidns=L.INIT_PID_NS), True)

    def test_proc_view_preserves_the_whole_nspid_payload(self):
        """R5-C1/F06: a value adjoining the colon cannot be silently discarded; numeric tokens are ASCII."""
        mi = "23 28 0:22 / /proc rw,relatime - proc proc rw\n"
        for status in ("NSpid:garbage\t77\n", "NSpid:77 88\n", "NSpid:\t²\n", "NSpid:\t７７\n"):
            with self.subTest(status=status):
                self.assertIsNot(L.proc_view_complete(status, mi, pidns=L.INIT_PID_NS), True)
        for status in ("NSpid:\t77\n", "NSpid: 77\n", "NSpid:77\n"):
            with self.subTest(control=status):
                self.assertIs(L.proc_view_complete(status, mi, pidns=L.INIT_PID_NS), True)

    def test_proc_view_rejects_malformed_mount_metadata(self):
        """F3: malformed supplied mount IDs/device fields are not recognised mountinfo evidence."""
        cases = (("garbage", "garbage", "garbage"),
                 ("garbage", "28", "0:22"), ("23", "garbage", "0:22"), ("23", "28", "garbage"),
                 ("0", "28", "0:22"), ("23", "0", "0:22"),
                 ("-1", "28", "0:22"), ("23", "-1", "0:22"),
                 ("²", "28", "0:22"), ("23", "²", "0:22"),
                 ("２３", "28", "0:22"), ("23", "２８", "0:22"),
                 ("23", "28", "0"), ("23", "28", "0:"), ("23", "28", ":22"),
                 ("23", "28", "0:22:1"), ("23", "28", "x:22"), ("23", "28", "0:x"),
                 ("23", "28", "-1:22"), ("23", "28", "0:-1"))
        for mount_id, parent_id, device in cases:
            with self.subTest(mount_id=mount_id, parent_id=parent_id, device=device):
                mi = f"{mount_id} {parent_id} {device} / /proc rw,relatime - proc proc rw\n"
                self.assertIsNot(L.proc_view_complete("NSpid:\t77\n", mi, pidns=L.INIT_PID_NS), True)

    def test_proc_view_rejects_nonproc_filesystem(self):
        mi = "23 28 0:22 / /proc rw,relatime - tmpfs tmpfs rw\n"
        self.assertIsNot(L.proc_view_complete("NSpid:\t77\n", mi, pidns=L.INIT_PID_NS), True)

    def test_proc_view_rejects_duplicate_mounts(self):
        unrestricted = "23 28 0:22 / /proc rw,relatime - proc proc rw\n"
        restricted = "24 23 0:23 / /proc rw,relatime - proc proc rw,hidepid=2\n"
        for mounts in (unrestricted + restricted, restricted + unrestricted, unrestricted + unrestricted):
            with self.subTest(mounts=mounts):
                self.assertIsNot(L.proc_view_complete("NSpid:\t77\n", mounts, pidns=L.INIT_PID_NS), True)

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
        me = next(k for k in b if k[0] == os.getpid())
        self.assertIsInstance(L.busy_processes(a, b, 0.2, 25, {me}, view_complete=L.proc_view_complete()), list)


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
        self.assertNotEqual(r1_kernel, got["kernel_release"])
        self.assertIn("kernel_release", L.pin_mismatches(dict(got, kernel_release=r1_kernel), got))

    def test_required_members_and_pin_point(self):
        """N11: a mapped set needs libm / libc / the loader; pin_point requires the supplied modules already loaded."""
        libc = next(k for k in L.mapped_objects() if k.endswith("libc.so.6"))
        self.assertIsNone(L.mapped_objects(f"7f00-7f01 r-xp 0 08:01 1 {libc}\n"))
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
class TestAttestationPreflight(unittest.TestCase):
    HW = {"machine_id_sha256": "a" * 64, "product_uuid_sha256": "b" * 64, "hardware_bound": True}

    def repo(self, d, files: dict):
        subprocess.run(["git", "init", "-q", d], check=True)
        for rel, data in files.items():
            Path(d, rel).parent.mkdir(parents=True, exist_ok=True)
            Path(d, rel).write_bytes(data)
        subprocess.run(["git", "-C", d, "add", "-A"], check=True)
        subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                        "commit", "-q", "-m", "a"], check=True)

    def attestation(self, **over) -> bytes:
        rec = {"schema": L.ATTESTATION_SCHEMA, "reviewed": True, "accepted": True, "machine": self.HW,
               "acceptance_record": "reviews/ACCEPT.md", "provider_image_updates": L.NO_IMAGE_CHANGE,
               "root_cgroup_is_real": True}
        rec.update(over)
        return json.dumps(rec).encode()

    def check(self, att: bytes, review: bytes | None = None, ref_extra=None, machine=None):
        with tempfile.TemporaryDirectory() as d:
            sha = hashlib.sha256(att).hexdigest()
            files = {"att/HOST.json": att}
            if review is None:
                review = f"verdict\n{L.ACCEPTANCE_LINE}{sha}\n".encode()
            files["reviews/ACCEPT.md"] = review
            self.repo(d, files)
            ref = {"path": "att/HOST.json", "sha256": sha, **(ref_extra or {})}
            return L.attestation_valid(ref, repo_root=d, machine=machine or self.HW)

    def test_attestation_read_from_the_committed_file(self):
        """N1: every fact comes from the committed file and its committed acceptance record."""
        rec, why = self.check(self.attestation())
        self.assertEqual(why, [])
        self.assertEqual(rec["provider_image_updates"], L.NO_IMAGE_CHANGE)

    def test_forged_or_unaccepted_attestations_refused(self):
        """N1 / F8 / R02: an arbitrary committed file, wrong schema, non-True flags, another machine, a missing or
        mismatching acceptance line, or extra caller fields are all refused."""
        bad = [
            (b"# README\nnot an attestation\n", None, None),
            (self.attestation(schema="other"), None, None),
            (self.attestation(accepted="REJECTED"), None, None),
            (self.attestation(reviewed="true"), None, None),
            (self.attestation(accepted=1), None, None),
            (self.attestation(machine=dict(self.HW, machine_id_sha256="c" * 64)), None, None),
            (self.attestation(), b"verdict: accepted\n", None),                     # no acceptance line
            (self.attestation(), f"{L.ACCEPTANCE_LINE}{'0' * 64}\n".encode(), None),   # names another sha
            (self.attestation(), None, {"accepted": True}),                          # caller-asserted field
        ]
        for att, review, extra in bad:
            rec, why = self.check(att, review, extra)
            self.assertIsNone(rec, (att[:40], review, extra))
            self.assertTrue(why)
        soft = dict(self.HW, hardware_bound=False, product_uuid_sha256=None)
        self.assertIsNone(self.check(self.attestation(machine=soft), machine=soft)[0])
        for ref in (None, {}, {"path": "att/HOST.json"}, {"path": 1, "sha256": "x"}):
            self.assertIsNone(L.attestation_valid(ref)[0], ref)

    def test_reference_digest_must_match_the_committed_file(self):
        """M25: a review accepting digest X does not make a DIFFERENT committed file pass when the reference quotes X."""
        with tempfile.TemporaryDirectory() as d:
            accepted = self.attestation()
            other = self.attestation(provider_image_updates="anything")
            x = hashlib.sha256(accepted).hexdigest()
            self.repo(d, {"att/HOST.json": other, "att/ACCEPTED.json": accepted,
                          "reviews/ACCEPT.md": f"{L.ACCEPTANCE_LINE}{x}\n".encode()})
            rec, why = L.attestation_valid({"path": "att/HOST.json", "sha256": x}, repo_root=d, machine=self.HW)
            self.assertIsNone(rec)
            self.assertIn("sha256 mismatch", " ".join(why))
            self.assertIsNotNone(L.attestation_valid({"path": "att/ACCEPTED.json", "sha256": x}, repo_root=d,
                                                     machine=self.HW)[0])

    def test_uncommitted_edit_is_not_the_record(self):
        with tempfile.TemporaryDirectory() as d:
            att = self.attestation()
            sha = hashlib.sha256(att).hexdigest()
            self.repo(d, {"att/HOST.json": att,
                          "reviews/ACCEPT.md": f"{L.ACCEPTANCE_LINE}{sha}\n".encode()})
            Path(d, "att/HOST.json").write_bytes(self.attestation(accepted=False))   # worktree edit only
            self.assertIsNotNone(L.attestation_valid({"path": "att/HOST.json", "sha256": sha}, repo_root=d,
                                                     machine=self.HW)[0])

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

    def gates(self, *, decided=frozenset(), att=(None, ["none"]), upd=None, mode="execute", launched=None, **rd):
        return L.preflight("/", mode=mode, other_job_running=False,
                           launched=self.launch() if launched is None else launched, attestation_ref={"x": 1},
                           readings=self.rd(**({"updates": upd} if upd is not None else {}), **rd),
                           decided=decided, attestation_check=lambda ref: att, launch_observer=self.launch)["gates"]

    def test_lifetime_gates_open_while_undecided(self):
        """N1: with D-HOST-LIFETIME open, even a valid attestation leaves both dependent gates OPEN_DECISION."""
        good = ({"provider_image_updates": L.NO_IMAGE_CHANGE}, [])
        g = self.gates(att=good)
        self.assertEqual((g["host_lifetime_attested"], g["no_automatic_os_install"]),
                         (L.OPEN_DECISION, L.OPEN_DECISION))
        g = self.gates(att=good, decided=frozenset({"D-HOST-LIFETIME"}))
        self.assertEqual((g["host_lifetime_attested"], g["no_automatic_os_install"]), (L.PASS, L.PASS))
        g = self.gates(att=(None, ["x"]), decided=frozenset({"D-HOST-LIFETIME"}))
        self.assertEqual((g["host_lifetime_attested"], g["no_automatic_os_install"]), (L.UNKNOWN, L.UNKNOWN))
        g = self.gates(att=({"provider_image_updates": "unknown"}, []), decided=frozenset({"D-HOST-LIFETIME"}))
        self.assertEqual(g["no_automatic_os_install"], L.UNKNOWN)
        for upd in ({}, None, {"guest_updates_shown_disabled": "true"}, {"guest_updates_shown_disabled": False}):
            g = L.preflight("/", mode="execute", other_job_running=False, launched=self.launch(),
                            attestation_ref=None, readings=self.rd(updates=upd), decided=frozenset({"D-HOST-LIFETIME"}),
                            attestation_check=lambda ref: good)["gates"]
            self.assertEqual(g["no_automatic_os_install"], L.UNKNOWN, upd)

    def test_all_favourable_still_blocked(self):
        r = L.preflight("/", mode="execute", other_job_running=False, launched=self.launch(), attestation_ref=None,
                        readings=self.rd(), attestation_check=lambda ref: ({"provider_image_updates":
                                                                              L.NO_IMAGE_CHANGE}, []),
                        launch_observer=self.launch)
        self.assertFalse(r["pass"])
        self.assertEqual(set(r["blocked"]), {"lowpowermode_0", "thermal_pressure_0", "memory_pressure_normal",
                                             "free_memory_ge_min", "host_exclusive", "host_lifetime_attested",
                                             "no_automatic_os_install"})
        self.assertTrue(all(v == L.OPEN_DECISION for v in r["blocked"].values()))

    def test_boot_id_must_be_valid(self):
        """N6: the boot-id gate validates the value, not just its presence."""
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

    def test_launch_record_fields_are_verified(self):
        """F15 / N12 / A2: execute / resume need valid fields matching independent observation of this process."""
        self.assertEqual(self.gates()["launched_by_systemd"], L.PASS)
        for bad in ({"pass": True}, True, "yes", self.launch(systemd_pid1=None),
                    self.launch(unit="rebaseguard-mbs308-exec.scope"), self.launch(unit="other.service"),
                    self.launch(invocation_id=""), self.launch(systemctl={"MainPID": 1, "InvocationID": "abc"}),
                    self.launch(systemctl={"MainPID": os.getpid(), "InvocationID": "zzz"}), self.launch(**{"pass": 1})):
            self.assertEqual(self.gates(launched=bad)["launched_by_systemd"], L.FAIL, bad)
        for mode in ("execute", "resume"):
            g = L.preflight("/", mode=mode, other_job_running=False, launched=None, attestation_ref=None,
                            readings=self.rd(), launch_observer=self.launch)["gates"]
            self.assertIn("launched_by_systemd", g)
            self.assertEqual(g["launched_by_systemd"], L.FAIL, mode)
        g = L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=None, attestation_ref=None,
                        readings=self.rd())["gates"]
        self.assertNotIn("launched_by_systemd", g)
        g = L.preflight("/", mode="launcher_preflight", other_job_running=False, launched=True, attestation_ref=None,
                        readings=self.rd())["gates"]
        self.assertEqual(g["launched_by_systemd"], L.FAIL)
        with self.assertRaises(ValueError):
            L.preflight("/", mode=None, other_job_running=False, launched=None, attestation_ref=None)

    def test_supplied_launch_requires_independent_matching_observation(self):
        """A2: supplied flags and systemctl fields cannot substitute for separately observed launch context."""
        supplied = self.launch()
        wrong_unit = self.launch(unit="rebaseguard-mbs308-other.service")
        wrong_invocation = self.launch(invocation_id="other",
                                      systemctl={"MainPID": os.getpid(), "InvocationID": "other"})
        for observed in (None, True, {"pass": True}, self.launch(systemd_pid1=False, **{"pass": False}),
                         wrong_unit, wrong_invocation,
                         self.launch(systemctl={"MainPID": 1, "InvocationID": "abc"})):
            with self.subTest(observed=observed):
                r = L.preflight("/", mode="execute", other_job_running=False, launched=supplied,
                    attestation_ref=None, readings=self.rd(), launch_observer=lambda: observed)
                self.assertIn("launched_by_systemd", r["gates"])
                self.assertEqual(r["gates"]["launched_by_systemd"], L.FAIL)
        r = L.preflight("/", mode="execute", other_job_running=False, launched=supplied,
                        attestation_ref=None, readings=self.rd(), launch_observer=self.launch)
        self.assertEqual(r["gates"]["launched_by_systemd"], L.PASS)

    def test_default_preflight_observes_live_launch_context(self):
        supplied = self.launch()
        for observed, expected in ((self.launch(systemd_pid1=False, **{"pass": False}), L.FAIL),
                                   (self.launch(unit="rebaseguard-mbs308-other.service"), L.FAIL),
                                   (self.launch(), L.PASS)):
            with self.subTest(observed=observed):
                with mock.patch.object(L, "launched_by_systemd", return_value=observed) as observe:
                    r = L.preflight("/", mode="execute", other_job_running=False, launched=supplied,
                                    attestation_ref=None, readings=self.rd())
                observe.assert_called_once_with()
                self.assertIn("launched_by_systemd", r["gates"])
                self.assertEqual(r["gates"]["launched_by_systemd"], expected)

    def test_live_preflight_fails_closed_here(self):
        r = L.preflight("/", mode="execute", other_job_running=False, launched=L.launched_by_systemd(),
                        attestation_ref=None)
        self.assertFalse(r["pass"])
        self.assertEqual(r["gates"]["launched_by_systemd"], L.FAIL)
        self.assertEqual(r["gates"]["host_lifetime_attested"], L.OPEN_DECISION)


if __name__ == "__main__":
    unittest.main()
