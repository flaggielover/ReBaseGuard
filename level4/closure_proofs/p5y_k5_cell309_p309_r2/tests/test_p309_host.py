"""r2 regression controls for the host package and the launcher (R2-I4, R2-I6; review P7, P9, P10, P11; addendum 2).

  python3 tests/test_p309_host.py      -> evidence/host/HOST_PACKAGE_TESTS.json; exit 0 iff every case passes

Pure decisions only (the Q-HOST monitor loop runs on a virtual clock through its MonitorIO; follow-up SF1): gate_checks, classify, monitor_verdict, monitor_liveness, continuity, the redaction, scratch_root and
the launcher's unit_name, unit-user check and argv redaction are given synthetic observations (delta review C2-C4, C9,
A8, A16 cases added).  The real-/proc, process and signal controls are in tests/test_p309_host_controls.py.  Nothing is sampled from /proc, no process is started or signalled, no file outside the
evidence directory is written, and no host setting is read beyond what scratch_root checks on its own directories.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
import tempfile
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
import p309_env as E  # noqa: E402
import p309_host as H  # noqa: E402
import p309_launch as L  # noqa: E402

CFG = dict(H.load_config([]), foreign_uids=[4242])
OWN = 999999                                   # a synthetic uid for this process in the pure gate decisions
R = {}


def t(name, ok, got=None):
    R[name] = {"pass": bool(ok), "got": got}


def row(tag, frac, heavy=False, pid=1):
    return {"pid": pid, "uid": 1000, "tag": tag, "cpu_fraction": frac, "cmd_sha256": "0" * 64, "heavy_pattern": heavy}


def prov(boot="b", mid="m", host="h", inst="i", sus=0.0):
    return {"boot_id": boot, "machine_id_sha256": mid, "hostname_sha256": host, "python": {"version": "3.11.15"},
            "glibc": "glibc 2.39", "suspended_s": sus, "cloud": {"instance_id_sha256": inst} if inst else {}}


ACC = {"readable": True, "hidepid": False, "foreign_visible": 3}
GOOD = dict(acc=ACC, rows=[], loads=(0.1, 0.1), mem_gb=15.0, disk={"/x": 100.0}, cfg=CFG)


def gate(**kw):
    a = dict(GOOD, **kw)
    return H.gate_checks(a["acc"], a["rows"], a["loads"], a["mem_gb"], a["disk"], a["cfg"], a.get("own", OWN))


# ---- the exclusion gate (start; strict)
t("G01_clean_host_passes", all(gate().values()))
t("G02_unreadable_proc_refused", not gate(acc={"readable": False, "hidepid": None, "foreign_visible": 0})["proc_readable"])
t("G03_hidepid_refused", not gate(acc=dict(ACC, hidepid=True))["proc_not_hidepid"])
t("G04_no_foreign_visible_refused", not gate(acc=dict(ACC, foreign_visible=0))["foreign_processes_visible"])
t("G05_foreign_light_cpu_blocks_start", not gate(rows=[row("foreign", 0.06)])["no_foreign_campaign_process_active"])
t("G06_foreign_new_process_blocks_start", not gate(rows=[row("foreign", None)])["no_foreign_campaign_process_active"])
t("G07_foreign_heavy_pattern_blocks_start", not gate(rows=[row("foreign", 0.0, heavy=True)])[
    "no_foreign_campaign_process_active"])
t("G08_foreign_idle_allows_start", gate(rows=[row("foreign", 0.0)])["no_foreign_campaign_process_active"])
t("G09_other_rebaseguard_heavy_blocks", not gate(rows=[row("other-rebaseguard", 0.9)])[
    "no_other_rebaseguard_heavy_process"])
t("G10_stale_p309_worker_blocks", not gate(rows=[row("p309", 0.0, heavy=True)])["no_stale_p309_worker"])
t("G11_load_above_baseline_blocks", not gate(loads=(3.0, 0.1))["load_at_baseline"])
t("G12_low_ram_blocks", not gate(mem_gb=1.0)["ram_available"])
t("G13_low_disk_blocks", not gate(disk={"/x": 10.0})["disk_available"])
t("G14_no_roots_blocks", not gate(disk={})["disk_available"])
t("G15_no_foreign_uids_blocks", not gate(cfg=dict(CFG, foreign_uids=[]))["foreign_uids_configured"])
t("G16_own_uid_listed_as_foreign_blocks", not gate(own=4242)["foreign_uids_configured"])
t("G17_unattributable_new_process_blocks_start", not gate(rows=[row("unattributable", None)])[
    "no_foreign_campaign_process_active"])
t("G18_unattributable_light_cpu_blocks_start", not gate(rows=[row("unattributable", 0.06)])[
    "no_foreign_campaign_process_active"])

# ---- classification (C2): a configured uid, an unreadable cwd of another non-root user, kernel threads


def rec(uid, cmd="python3 job.py", cwd="", ok=True):
    return {"uid": uid, "cmd": cmd, "cwd": cwd, "cwd_ok": ok}


t("K01_configured_foreign_uid_is_foreign", H.classify(rec(4242), CFG, OWN) == "foreign")
t("K02_other_user_unreadable_cwd_is_unattributable", H.classify(rec(5000, ok=False), CFG, OWN) == "unattributable")
t("K03_root_unreadable_cwd_untagged", H.classify(rec(0, ok=False), CFG, OWN) is None)
t("K04_own_uid_unreadable_cwd_untagged", H.classify(rec(OWN, ok=False), CFG, OWN) is None)
t("K05_kernel_thread_untagged_even_if_uid_listed", H.classify(rec(4242, cmd=""), CFG, OWN) is None)
t("K06_pattern_is_foreign", H.classify(rec(5000, cmd="python3 /x/TEST-foreign-job/run.py"), dict(
    CFG, foreign_patterns=["TEST-foreign-job"]), OWN) == "foreign")

# ---- Q-HOST continuity
base = prov()
t("C01_same_host_passes", H.continuity(base, prov(), CFG)["pass"])
t("C02_reboot_fails", not H.continuity(base, prov(boot="b2"), CFG)["pass"])
t("C03_other_machine_fails", not H.continuity(base, prov(mid="m2"), CFG)["pass"])
t("C04_other_instance_fails", not H.continuity(base, prov(inst="i2"), CFG)["pass"])
c5 = H.continuity(base, prov(inst=None), CFG)
t("C05_imds_timeout_same_boot_passes_unverified", c5["pass"] and c5["instance_unverified"], c5)
t("C06_imds_timeout_after_reboot_fails", not H.continuity(base, prov(boot="b2", inst=None), CFG)["pass"])
t("C07_suspend_over_tolerance_fails", not H.continuity(base, prov(sus=CFG["suspend_tolerance_s"] + 1), CFG)["pass"])
t("C08_runtime_change_fails", not H.continuity(base, dict(prov(), glibc="glibc 2.40"), CFG)["pass"])
c9 = H.continuity(prov(inst=None), prov(), CFG)
t("C09_base_without_id_sample_with_id_passes_unverified", c9["pass"] and c9["instance_unverified"], c9)
t("C10_base_without_id_after_reboot_fails", not H.continuity(prov(inst=None), prov(boot="b2"), CFG)["pass"])
t("C11_both_ids_present_is_verified", not H.continuity(base, prov(), CFG)["instance_unverified"])

# ---- Q-HOST monitor sample (in-run; heavy work only, OD-R2-5 option (i))
ok_c = {"pass": True}
t("M01_quiet_passes", H.monitor_verdict(ok_c, [row("foreign", 0.1)], CFG)[0])
t("M02_foreign_heavy_cpu_fails", not H.monitor_verdict(ok_c, [row("foreign", 0.9)], CFG)[0])
t("M03_foreign_heavy_pattern_fails", not H.monitor_verdict(ok_c, [row("foreign", 0.0, heavy=True)], CFG)[0])
t("M04_foreign_new_process_waits_a_sample", H.monitor_verdict(ok_c, [row("foreign", None)], CFG)[0])
t("M05_other_rebaseguard_heavy_fails", not H.monitor_verdict(ok_c, [row("other-rebaseguard", 0.9)], CFG)[0])
t("M06_continuity_failure_fails", not H.monitor_verdict({"pass": False}, [], CFG)[0])
t("M07_thresholds_distinct", CFG["monitor_heavy_cpu_fraction"] > CFG["heavy_cpu_fraction"],
  [CFG["heavy_cpu_fraction"], CFG["monitor_heavy_cpu_fraction"]])
t("M08_unattributable_heavy_fails", not H.monitor_verdict(ok_c, [row("unattributable", 0.9)], CFG)[0])
t("M09_aggregate_foreign_fails", not H.monitor_verdict(ok_c, [row("foreign", 0.4, pid=i) for i in (1, 2, 3)], CFG)[0])
t("M10_aggregate_below_limit_passes", H.monitor_verdict(ok_c, [row("foreign", 0.4, pid=i) for i in (1, 2)], CFG)[0])

# ---- Q-HOST monitor liveness (C4): interval 60 s, tolerance 30 s
lv = lambda times, stop=200.0, alive=True: H.monitor_liveness(times, 0.0, stop, alive, 60.0, 30.0)["pass"]  # noqa: E731
t("V01_regular_samples_pass", lv([30.0, 90.0, 150.0]))
t("V02_monitor_dead_at_stop_fails", not lv([30.0, 90.0, 150.0], alive=False))
t("V03_no_sample_fails", not lv([], stop=60.0))
t("V04_gap_between_samples_fails", not lv([30.0, 200.0], stop=210.0))
t("V05_gap_before_stop_fails", not lv([30.0, 90.0], stop=200.0))
t("V06_samples_out_of_order_fail", not lv([90.0, 30.0], stop=100.0))


# ---- follow-up SF1: the committed qhost_monitor loop on a virtual clock, judged by monitor_liveness at every stop time
class VirtualIO(H.MonitorIO):
    """a virtual clock: a sample takes the next duration in `durations`; the parent lives until `horizon`"""

    def __init__(self, durations, horizon, fail_at=None):
        self.t, self.durations, self.horizon, self.fail_at = 0.0, list(durations), horizon, fail_at
        self.events, self.signals, self.n = [], [], 0

    def mono(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds

    def sample(self, cfg, interval):
        self.t += self.durations[self.n % len(self.durations)]
        self.n += 1
        now = prov(boot="b2") if self.fail_at is not None and self.n == self.fail_at else prov()
        return now, []

    def parent_alive(self, parent):
        return self.t < self.horizon

    def signal_parent(self, parent):
        self.signals.append(parent)

    def write(self, line):
        self.events.append(json.loads(line))


def worst_gap(durations, scheme="sf1", tol=None):
    """run the committed loop to 1200 s; then, for every stop time from 100 s to 1100 s (step 0.5 s), apply the
    runner's rule to the events written before the stop.  Returns (all stops pass, the largest gap seen)."""
    vio = VirtualIO(durations, 1200.0)
    H.qhost_monitor(CFG, prov(), 1, 60, io=vio)
    tol = CFG["monitor_gap_tolerance_s"] if tol is None else tol
    ok, worst = True, 0.0
    for k in range(200, 2201):
        stop = k * 0.5
        if scheme == "sf1":                             # every event: start-of-sample and result rows (follow-up SF1)
            times = [e["m"] for e in vio.events if e["m"] <= stop]
        else:                                           # round 2: one time per sample, taken at its start
            starts = [e["m"] for e in vio.events if e["kind"] == "sample_start"]
            ends = [e["m"] for e in vio.events if e["kind"] == "sample"]
            times = [st for st, en in zip(starts, ends) if en <= stop]
        lv = H.monitor_liveness(times, 0.0, stop, True, 60.0, tol)
        ok, worst = ok and lv["pass"], max(worst, lv["max_gap_s"])
    return ok, worst


ok47, gap47 = worst_gap([47.0])
t("MV01_worst_case_47s_samples_pass_at_every_stop", ok47 and gap47 <= 60.0, {"max_gap_s": gap47})
okr, gapr = worst_gap([20.0, 47.0, 31.5, 22.0, 46.0, 25.0])
t("MV02_mixed_sample_durations_pass_at_every_stop", okr and gapr <= 60.0, {"max_gap_s": gapr})
okold, gapold = worst_gap([47.0], scheme="round2")
t("MV03_round2_scheme_fails_the_same_run", not okold and gapold > 105.0, {"max_gap_s": gapold})
okstuck, gapstuck = worst_gap([47.0, 47.0, 120.0])
t("MV04_a_stuck_120s_sample_fails", not okstuck and gapstuck >= 120.0, {"max_gap_s": gapstuck})
# follow-up X1: the monitor file's parser (a torn last line is set aside; a corrupt line elsewhere is counted) and the
# order rule at the stop (a row at the stop time itself passes; one after it fails)
ev, torn, bad = H.parse_monitor_rows('{"kind": "sample_start", "m": 1.5}\n{"kind": "sample", "m": 2.5, "pass": true}\n{"kind": "sam')
t("MV06_torn_last_line_set_aside", len(ev) == 2 and torn and bad == 0, [len(ev), torn, bad])
ev, torn, bad = H.parse_monitor_rows('{"kind": "sample_start", "m": 1.5}\nnot json\n{"kind": "sample", "m": 2.5}\n')
t("MV07_corrupt_middle_line_counted", len(ev) == 2 and not torn and bad == 1, [len(ev), torn, bad])
t("MV08_row_at_the_stop_time_passes", H.monitor_liveness([10.0, 30.0, 70.0], 0.0, 70.0, True, 60.0, 45.0)["pass"])
t("MV09_row_after_the_stop_fails", not H.monitor_liveness([10.0, 30.0, 70.001], 0.0, 70.0, True, 60.0, 45.0)["pass"])
vfail = VirtualIO([25.0], 1200.0, fail_at=3)
rcf = H.qhost_monitor(CFG, prov(), 7, 60, io=vfail)
t("MV05_failed_sample_signals_the_parent_once_and_stops", rcf == 1 and vfail.signals == [7] and
  [e["kind"] for e in vfail.events] == ["sample_start", "sample"] * 3 and vfail.events[-1]["pass"] is False,
  {"rc": rcf, "signals": vfail.signals, "events": len(vfail.events)})

# ---- redaction (C9)
FR = "/srv/foreign-TEST-root"
rc = H.redacted_config(dict(CFG, foreign_roots=[FR], foreign_heavy_patterns=["TEST-heavy-job"]))
t("R01_redacted_config_holds_no_foreign_text", FR not in json.dumps(rc) and "TEST-heavy-job" not in json.dumps(rc)
  and "cell" not in json.dumps(rc["foreign_patterns"]), rc["foreign_roots"])
t("R02_config_sha256_binds_foreign_roots", H.config_sha256(dict(CFG, foreign_roots=[FR])) != H.config_sha256(
    dict(CFG, foreign_roots=[FR + "2"])))

# ---- P309_SCRATCH_ROOT (P7)
with tempfile.TemporaryDirectory() as td:
    td = os.path.realpath(td)
    other = os.path.join(td, "other")
    os.mkdir(other)

    def refused(env, cfg=None):
        try:
            H.scratch_root(env, str(E.REPO), cfg or {"foreign_roots": []})
            return False
        except H.HostError:
            return True
    t("S01_valid_accepted", not refused({"P309_SCRATCH_ROOT": td}))
    t("S02_unset_refused", refused({}))
    t("S03_relative_refused", refused({"P309_SCRATCH_ROOT": "rel/x"}))
    t("S04_inside_repo_refused", refused({"P309_SCRATCH_ROOT": str(E.REPO)}))
    t("S05_missing_dir_refused", refused({"P309_SCRATCH_ROOT": os.path.join(td, "nope")}))
    t("S06_empty_foreign_list_refused", refused({"P309_SCRATCH_ROOT": td, "P309_FOREIGN_ROOTS": ""}))
    t("S07_overlapping_foreign_root_refused", refused({"P309_SCRATCH_ROOT": other, "P309_FOREIGN_ROOTS": td}))
    t("S08_nonempty_refused_when_required", refused({"P309_SCRATCH_ROOT": td}, {"foreign_roots": [],
                                                                                "require_empty_scratch": True}))

# ---- the launcher's unit names (F5)
t("L01_drill_name", L.unit_name("drill", "20261001T000000Z") == "p309-r2-drill-20261001T000000Z")
t("L02_official_name", L.unit_name("official", "20261001T000000Z") == "p309-r2-qualify-20261001T000000Z")
try:
    L.unit_name("drill", "x; rm")
    t("L03_bad_stamp_refused", False)
except H.HostError:
    t("L03_bad_stamp_refused", True)
t("L05_host_rerun_name", L.unit_name("host-rerun", "20261001T000000Z") == "p309-r2-hostrerun-20261001T000000Z")
ra = L.redact_argv(["--property=InaccessiblePaths=-" + FR, "--setenv=P309_FOREIGN_ROOTS=" + FR], {"foreign_roots": [FR]})
t("L06_unit_argv_redacted", not any(FR in a for a in ra), ra)
try:
    L.unit_user_check({"unit_user": "root"}, {"foreign_roots": [], "foreign_uids": []})
    t("L07_root_unit_user_refused", False)
except H.HostError:
    t("L07_root_unit_user_refused", True)
try:
    H.load_config(["--config-json", json.dumps({"no_such_key": 1})])
    R["L04_unknown_config_key_refused"] = {"pass": False, "got": None}
except H.HostError:
    R["L04_unknown_config_key_refused"] = {"pass": True, "got": None}

if __name__ == "__main__":
    E.log("tests/test_p309_host.py", "r2 host package and launcher decision tests (synthetic observations)",
          klass="GOVERNANCE", notes="pure functions only; no process started or signalled")
    ok = all(v["pass"] for v in R.values())
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "all_pass": ok,
           "cases": len(R), "results": R}
    (E.evidence_dir("host") / "HOST_PACKAGE_TESTS.json").write_text(json.dumps(out, indent=1, sort_keys=True,
                                                                               default=str) + "\n")
    for k, v in R.items():
        print(f"[{'PASS' if v['pass'] else 'FAIL'}] {k}")
    sys.exit(0 if ok else 1)
