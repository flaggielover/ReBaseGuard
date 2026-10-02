"""MB-S r1: the decision-dependent cases, the section-11.2 chain and the grant's owner records (non-holder builder6,
research brief 54). TARGET-FREE: planted records, planted host readings, synthetic launchd payloads, throw-away git
repositories and sandboxes of the separate --no-local base store. NO science computation, no decoy, no cell 305-309
(the dev decoy of the science cases is tests/test_mbs308_decoy.py, run deliberately).

Covers: Q12's decision function with MB r1 r3's fourteen planted controls and the successor's three, and that it never
states a candidate cap; the section-4 values check (MBS-8 (i)) with planted mismatches; the carried science cases'
summaries, comparisons and pins (QC01-QC08, Q1_theory, QC09-SCI, MBR1_REPRO); the derivation tool, the apply step and
R_RULES_OFFICIAL (section 11.2 option (a): exact agreement, no tolerance); the designated-measurement tool on planted
readings and a synthetic payload under launchd; the owner records in the configuration, the protocol, the manifest and
QC13-S; the final-preflight mapping of owner decisions section 14. The code under test is tests/../code or a mutated
copy (MBS308_TEST_CODE_DIR, the mutant runner).

    python3.14 -I -S -B test_mbs308_cases.py [t_name ...] [--out report.json]
"""
from __future__ import annotations

import ast
import copy
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbs308_testlib as T  # noqa: E402

CODE = T.code_dir()
sys.path.insert(0, str(CODE))
import mbs308_derive as DV  # noqa: E402
import mbs308_host as HOST  # noqa: E402
import mbs308_manifest as MF  # noqa: E402
import mbs308_measure as MEAS  # noqa: E402
import mbs308_qualify as Q  # noqa: E402
import mbs308_repin as RP  # noqa: E402
import mbs308_rrules as RR  # noqa: E402

CFG = Q.load_config(T.NSS / "config" / "MBS308_QUALIFICATION_CASES.json")
PROTO = T.NSS / "protocol" / "MBS308_PROTOCOL_DRAFT.md"
TMP = T.SCRATCH / "t_cases"
MIB, GIB = 1024 ** 2, 1024 ** 3
DRV = (CODE / "mbs308_driver.py").read_text()
STATE_SRC = (CODE / "mbs308_state.py").read_text()
S4 = CFG["owner_decisions"]["MBS-8"]["values"]
PLAN = DV.plan_of(CFG)
H3 = CFG["r_allow_h3_readings"]["readings"]
JOB_OK = {"finished": True, "detached": True, "booted_out": True}
_S: dict = {}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fresh(name: str) -> Path:
    d = TMP / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


def t_designation_history_does_not_dirty_namespace_preflight():
    """D-1 regression: the durable history created by the first official designation is allowed runtime state.
    Any other successor-namespace edit still fails the clean-worktree predicate; this control performs no launch or
    measurement and therefore cannot evaluate a target cell."""
    h = MEAS.SERIES_HISTORY_REL
    return {"ok": MEAS.namespace_status_clean(f"?? {h}\n") and
            MEAS.namespace_status_clean(f" M {h}\n") and
            not MEAS.namespace_status_clean(f"?? {h}.tampered\n") and
            not MEAS.namespace_status_clean(f" M {T.NS_REL}/code/mbs308_measure.py\n")}


def base_names() -> list:
    if "base" not in _S:
        _S["base"] = DV.base_names_of(CFG, T.base_store())
    return _S["base"]


def owner_text(i: int) -> str:
    _name, path, commit, _n, _d = T.s1_owner_records()[i]
    return T.owner_record_text(commit, path)


def caps() -> dict:
    return Q.driver_caps(DRV)


def clean_host(**k) -> dict:
    return dict(Q._synthetic_host(HOST, **k), thermal_events=[])


# ------------------------------------------------------------------ planted decoy records and readings
CAP_EVENT = {"utc": "planted", "worker_pid": 1, "rss_bytes": 4 * GIB, "cap_bytes": 3 * GIB, "killed": True}


def decoy_record(cell: int, first_blocks, *, cap=3 * GIB, poll=2.0, workers=5, ladder="frozen", launched=True,
                 rss_mb=100, events=(), growth=10 * MIB, drv=64 * MIB, host=None, served=0,
                 spacing_ns=300_000_000, failed=None) -> dict:
    """A PLANTED record in the driver's decoy-record format (rule inputs only; no science). `failed`: the driver's
    record of a FAILED decoy (`decoy_failed`; no blocks, no finished job)."""
    blocks = list(range(first_blocks)) if first_blocks is not None else [0, 1]
    jobs = {f"{k}.{b}.{r}": rss_mb * MIB + 1000 * b for b in blocks
            for k, r in (("RLR", 4), ("RLR", 6), ("C2B", 20), ("C1B", 8))}
    if failed:
        return {"decoy_cell": cell, "decoy_failed": failed, "dev_ladder": ladder != "frozen", "mode": "decoy",
                "driver_sha256": "0" * 64, "utc": "planted",
                "lifecycle": {"stage1_context": {"jobs_served_from_checkpoints": 0, "jobs_computed": 0,
                                                 "job_maxrss_bytes": {},
                                                 "memory_watchdog": {"cap_bytes": cap, "events": list(events),
                                                                     "worker_peak_rss_bytes": cap + MIB}},
                              "driver_maxrss_bytes": drv,
                              "rss_sampler": {"interval_s": "0.25", "samples": 9, "failed_reads": 0,
                                              "max_spacing_s": spacing_ns / 1e9, "max_spacing_ns": spacing_ns,
                                              "max_growth_bytes_per_s": growth},
                              "rmem_run": {"workers": workers, "ladder": ladder, "mem_cap_bytes": cap,
                                           "mem_poll_s": poll, "first_blocks": first_blocks,
                                           "launched_by_launchd": launched}},
                "host": host if host is not None else clean_host()}
    return {"decoy_cell": cell, "blocks_total": 5, "blocks_run": "all" if first_blocks is None else blocks,
            "dev_ladder": ladder != "frozen", "driver_sha256": "0" * 64, "utc": "planted",
            "lifecycle": {"stage1_context": {"jobs_served_from_checkpoints": served, "jobs_computed": len(jobs),
                                             "job_maxrss_bytes": jobs,
                                             "memory_watchdog": {"cap_bytes": cap, "events": list(events),
                                                                 "worker_peak_rss_bytes": rss_mb * MIB + 2 * MIB}},
                          "driver_maxrss_bytes": drv,
                          "rss_sampler": {"interval_s": "0.25", "samples": 100, "failed_reads": 0,
                                          "max_spacing_s": spacing_ns / 1e9, "max_spacing_ns": spacing_ns,
                                          "max_growth_bytes_per_s": growth},
                          "rmem_run": {"workers": workers, "ladder": ladder, "mem_cap_bytes": cap, "mem_poll_s": poll,
                                       "first_blocks": first_blocks, "launched_by_launchd": launched}},
            "host": host if host is not None else clean_host()}


def run_of(cell: int, **k) -> dict:
    job = k.pop("job", JOB_OK)
    exit_code = k.pop("exit_code", 0)
    r = DV.compact_run(decoy_record(cell, PLAN[cell], **k), f"decoy{cell}", exit_code=exit_code, raw_sha256="p" * 64)
    return dict(r, job=dict(job))


def readings(n: int = 10, spacing: int = 30, *, free=4 * GIB, procs=None, wired=1000, power=RR.AC) -> list:
    return [{"t_s": f"{(1000 + i * spacing) * 10 ** 9}/1000000000", "utc": "planted", "power": power,
             "free_memory_bytes": free[i] if isinstance(free, list) else free, "wired_pages": wired[i] if
             isinstance(wired, list) else wired, "page_size_bytes": 16384, "thermal_level": 0, "memory_pressure": 1,
             "processes_read": 400, "own_process_tree_excluded": 1,
             "procs": copy.deepcopy(procs[i] if procs and isinstance(procs[0], list) else (procs or []))}
            for i in range(n)]


HOSTING = {"paths": ["/Applications/Planted.app/"], "chain": [{"pid": 2, "comm": "/Applications/Planted.app/x",
                                                               "bundle": "/Applications/Planted.app"}]}
SIP_PROC = {"pid": 77, "comm": "/usr/libexec/plantedd", "pcpu": "30.0", "hosting_app": False}


def planted_host_report(**over) -> dict:
    """A PLANTED read-only host report with the structure the verifier's own has (brief 56 follow-up): every checklist
    item with a status, read_only, and the reference to where the operator's actions are recorded."""
    return dict({"schema": DV.HOST_REPORT_SCHEMA, "read_only": True, "changes_made": False, "utc": "planted",
                 "items": [{"item": k, "checked_by": "planted", "status": "NOT_READY", "reading": None, "note": ""}
                           for k in DV.HOST_REPORT_ITEMS],
                 "operator_actions": copy.deepcopy(DV.OPERATOR_ACTIONS), "ready": False}, **over)


def evidence(runs=None, rds=None, *, designated=True, driver_sha=None, commit="c" * 40, hw=16 * GIB,
             hosting=None) -> dict:
    """PLANTED designated-measurement evidence (never written into the worktree)."""
    return {"schema": DV.EVIDENCE_SCHEMA, "designated": designated, "label": "PLANTED BY A TEST (never evidence)",
            "status": "MEASURED", "invalid_reasons": [], "host_not_prepared": [], "commit": commit,
            "driver_sha256": driver_sha or sha(DRV.encode()), "hw_memsize_bytes": hw,
            "hosting_app": hosting or HOSTING, "readings": rds if rds is not None else readings(procs=[SIP_PROC]),
            "runs": runs if runs is not None else [run_of(297), run_of(316)], "target_evaluations": 0,
            "host_report": planted_host_report()}


def derive(ev: dict) -> dict:
    raw = json.dumps(ev, sort_keys=True).encode()
    return DV.derivation(ev, evidence_sha256=sha(raw), base_names=base_names(), h3_readings=H3, plan=PLAN,
                         rules_sha256=sha((CODE / "mbs308_rrules.py").read_bytes()),
                         tool_sha256=sha((CODE / "mbs308_derive.py").read_bytes()))


# expected canonical outputs of the default planted evidence, computed here independently (exact integers)
EXPECT = {"MEM_CAP_BYTES": 1 * GIB,                               # max(3 x 102 MiB, 1 GiB) rounded up to 256 MiB
          "MEM_POLL_S": "2",                                      # 10 MiB/s x 2 s <= 0.1 x 1 GiB
          "FREE_MEM_MIN_BYTES": 2 * GIB,                          # max(2 GiB, roundup(1024 + 4 x 102 + 64 MiB))
          "EXCL_CPU_PCT": 25}


# ------------------------------------------------------------------ Q12 (MBS-8 (i)) and the section-4 values
def _keys(o, acc=None) -> set:
    acc = set() if acc is None else acc
    if isinstance(o, dict):
        for k, v in o.items():
            acc.add(str(k))
            _keys(v, acc)
    elif isinstance(o, list):
        for v in o:
            _keys(v, acc)
    return acc


def t_q12_decision_and_planted_controls():
    """Q12's decision function on planted records: MB r1 r3's FOURTEEN controls and the successor's three (launcher,
    WORKERS, ladder) all behave as declared through _q12_core; missing records fail; the case passes only with the
    records, the controls AND the section-4 values check."""
    c = Q.q12_controls(caps(), HOST)
    good = Q.q12_caps(Q._synthetic_decoy({"all": 0.25}, clean_host(), caps()),
                      Q._synthetic_decoy({"all": 0.25}, clean_host(), caps()), driver_src=DRV, state_src=STATE_SRC,
                      section4=S4, HOST=HOST)
    none = Q.q12_caps(None, None, driver_src=DRV, state_src=STATE_SRC, section4=S4, HOST=HOST)
    slow = Q.q12_caps(Q._synthetic_decoy({"all": 0.10, ("RLR", 8): 0.55}, clean_host(), caps()),
                      Q._synthetic_decoy({"all": 0.10}, clean_host(), caps()), driver_src=DRV, state_src=STATE_SRC,
                      section4=S4, HOST=HOST)
    # MB r1's convention: a C2b job's wall counts with its recorded in-job verification seconds once more
    ver = Q._synthetic_decoy({"all": 0.10, ("C2B", 80): 0.30}, clean_host(), caps())
    ver["stage1"]["blocks"][0]["c2b_rungs"][2]["verification"]["seconds"] = 0.25 * caps()["RUNG_CPU_CAP_S"]["C2B"][80]
    verq = Q._q12_core(ver, Q._synthetic_decoy({"all": 0.10}, clean_host(), caps()), caps(), HOST)
    names = set(c["controls"])
    ok = verq["pass"] is False and verq["per_job_caps"]["C2B:80"]["cap_ge_2x"] is False and \
        Q._failing_job_keys(verq) == {"C2B:80"} and \
        c["pass"] is True and c["n"] == 17 and c["carried_from_mbr1_r3"] == 14 and c["failed"] == [] and \
        {"clean_host_within_caps", "K_host_slept_30s_during_316", "genuine_per_job_cap_violation_clean_host",
         "genuine_eval_cap_violation_clean_host", "host_interval_shorter_than_the_run",
         "not_under_the_launchd_launcher_316", "workers_not_the_frozen_value_316",
         "not_the_frozen_ladder_316"} <= names and \
        c["controls"]["clean_host_within_caps"]["pass_observed"] is True and \
        good["pass"] is True and good["caps_pass"] is True and good["timing_clean"] is True and \
        none["pass"] is False and slow["pass"] is False and slow["fail_reasons"] == ["CAP_RULE_VIOLATED"] and \
        slow["per_job_caps"]["RLR:8"]["cap_ge_2x"] is False and slow["eval_cap_ok"] is True
    return {"ok": ok, "controls": c["n"], "failed": c["failed"]}


def t_q12_never_states_a_candidate_cap():
    """MBS-8 (i): Q12 is a pass / fail check of the FIXED caps. Its output never carries a derived, required or
    proposed cap: no key of the output (passing or failing) names one, the only cap values in it are the driver's own,
    and the threshold ceil(1.5 x projection) appears nowhere, even when EVAL_CAP fails."""
    cp = caps()
    outs = [Q._q12_core(Q._synthetic_decoy(f, clean_host(), cp), Q._synthetic_decoy(f, clean_host(), cp), cp, HOST)
            for f in ({"all": 0.25}, {"all": 0.45}, {"all": 0.10, ("RLR", 8): 0.55})]
    banned = ("required", "candidate", "proposed", "suggest", "recommend", "derived_cap", "new_cap", "min_cap")
    keys = set().union(*(_keys(o) for o in outs))
    no_key = not any(b in k.lower() for k in keys for b in banned)
    import math
    leak = []
    for o in outs:
        need = math.ceil(1.5 * o["projection_makespan_s"])
        text = json.dumps(o)
        if need != cp["EVAL_CAP_S"] and str(need) in text:
            leak.append(need)
    cap_values = {c["cap_s"] for o in outs for c in o["per_job_caps"].values()} | {o["eval_cap_s"] for o in outs}
    own = {v for d in cp["RUNG_CPU_CAP_S"].values() for v in d.values()} | {cp["EVAL_CAP_S"]}
    ok = no_key and not leak and cap_values <= own and outs[1]["eval_cap_ok"] is False and \
        outs[0]["eval_cap_ok"] is True
    return {"ok": ok, "banned_keys": sorted(k for k in keys if any(b in k.lower() for b in banned)), "leak": leak}


def t_section4_values_and_planted_mismatches():
    """The driver carries EXACTLY the user's section-4 values (owner decisions section 4, MBS-8 (i)): EVAL_CAP 28800 s
    per attempt on CLOCK_UPTIME_RAW; RLR 1800 / 4200 / 8700 s; C2b 1800 / 1800 / 2700 s; C1b 1800 s; VER 1800 s;
    PRE_CAP 1800 s; WORKERS 5. The configuration's values are the record's own lines (read from the base store).
    Each planted mismatch (in the driver's text, the state module's text, or the configuration) fails the check, and
    with it the Q12 case."""
    base = Q.section4_values(DRV, STATE_SRC, S4)
    text = owner_text(0)
    sec4 = text.split("4. MBS-8", 1)[1].split("5. S1", 1)[0] if "4. MBS-8" in text else ""
    lines = ("MBS-8 = OPTION (i): MB r1 r3 CAPS", "EVAL_CAP = 8 hours per attempt, awake time",
             "RLR = 1800 / 4200 / 8700 s", "C2b = 1800 / 1800 / 2700 s", "C1b = 1800 s", "VER = 1800 s",
             "PRE_CAP = 1800 s", "WORKERS = 5")
    record_says = all(ln in sec4 for ln in lines)
    cfg_is_record = S4 == {"EVAL_CAP_S": 8 * 3600, "eval_cap_scope": "per attempt", "eval_cap_clock":
                           "CLOCK_UPTIME_RAW", "RUNG_CPU_CAP_S": {"RLR": {"4": 1800, "6": 4200, "8": 8700},
                                                                 "C2B": {"20": 1800, "40": 1800, "80": 2700},
                                                                 "C1B": 1800, "VER": 1800},
                           "PRE_CAP_S": 1800, "WORKERS": 5}
    plants = {
        "eval_cap_s": (DRV.replace("EVAL_CAP_S = 8 * 3600 ", "EVAL_CAP_S = 9 * 3600 "), STATE_SRC, S4),
        "pre_cap_s": (DRV.replace("PRE_CAP_S = 1800 ", "PRE_CAP_S = 2400 "), STATE_SRC, S4),
        "workers": (DRV.replace("WORKERS = 5 ", "WORKERS = 4 "), STATE_SRC, S4),
        "rlr_caps": (DRV.replace('"RLR": {4: 1800, 6: 4200, 8: 8700}', '"RLR": {4: 1800, 6: 4200, 8: 9000}'),
                     STATE_SRC, S4),
        "c2b_caps": (DRV.replace('"C2B": {20: 1800, 40: 1800, 80: 2700}', '"C2B": {20: 1800, 40: 1800, 80: 3600}'),
                     STATE_SRC, S4),
        "c1b_caps": (DRV.replace('"C1B": {4: 1800, 8: 1800, 10: 1800, 12: 1800}',
                                 '"C1B": {4: 1800, 8: 1800, 10: 1800, 12: 2400}'), STATE_SRC, S4),
        "ver_caps": (DRV.replace('"VER": {4: 1800, 6: 1800, 8: 1800, 10: 1800, 12: 1800}',
                                 '"VER": {4: 1800, 6: 1800, 8: 900, 10: 1800, 12: 1800}'), STATE_SRC, S4),
        "eval_cap_started_once_per_attempt_in_after_marker": (
            DRV.replace("    cap = STATE.AwakeCap(EVAL_CAP_S).start()\n", "    cap = STATE.AwakeCap(10 ** 9).start()\n"),
            STATE_SRC, S4),
        "eval_cap_clock_is_clock_uptime_raw": (
            DRV, STATE_SRC.replace("        return (time.clock_gettime_ns(time.CLOCK_UPTIME_RAW) - self.t0) / 1e9",
                                   "        return (time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW) - self.t0) / 1e9"),
            S4),
    }
    rows = {}
    for check, (d, st, want) in plants.items():
        changed = d != DRV or st != STATE_SRC
        r = Q.section4_values(d, st, want)
        rows[check] = changed and r["pass"] is False and r["checks"].get(check) is False
    cfg_plant = Q.section4_values(DRV, STATE_SRC, dict(S4, EVAL_CAP_S=6 * 3600))
    rows["config_value_differs_from_driver"] = cfg_plant["pass"] is False and \
        cfg_plant["checks"]["eval_cap_s"] is False
    good = Q._synthetic_decoy({"all": 0.25}, clean_host(), caps())
    q12 = Q.q12_caps(good, copy.deepcopy(good), driver_src=plants["rlr_caps"][0], state_src=STATE_SRC, section4=S4,
                     HOST=HOST)
    rows["q12_case_fails_on_a_section4_mismatch"] = q12["pass"] is False and q12["section4_values"]["pass"] is False
    ok = base["pass"] is True and len(base["checks"]) == 10 and record_says and cfg_is_record and all(rows.values())
    return {"ok": ok, "base": base["pass"], "record_says": record_says, "config_is_the_record": cfg_is_record,
            "plants": rows}


# ------------------------------------------------------------------ the carried science cases: summaries
def _s2(ok=True):
    return {"decoy_meta": {"r0_order3_binds": True}, "stage2": {"gates": {"G1": {"pass": ok}}},
            "supply": {"independent": {"status": "EQUAL"}}}


def _full_decoy(cell=297, first=None, *, launched=True, workers=5, n_blocks=5, ladder=None, stage2=True) -> dict:
    lad = ladder or {"RLR": [4, 6, 8], "C2B": [20, 40, 80], "C1B": [8, 10, 12]}
    run = range(n_blocks) if first is None else range(first)
    blocks = [{"index": i, "run": i in run, "pointwise": {"status": "CERTIFIED"}, "rlr_block": {"x": 1},
               "rlr_rungs": [], "c2b_rungs": [], "c1b_rungs": []} for i in range(n_blocks)]
    d = {"decoy_cell": cell, "blocks_run": "all" if first is None else list(run), "dev_ladder": False,
         "stage1": {"blocks": blocks, "ladder": lad, "n_verifications": 3},
         "lifecycle": {"rmem_run": {"launched_by_launchd": launched, "workers": workers, "ladder": "frozen",
                                    "first_blocks": first}}}
    if stage2:
        d["stage2_decoys"] = [_s2(), _s2()]
    return d


LADDER = {"RLR": [4, 6, 8], "C2B": [20, 40, 80], "C1B": [8, 10, 12]}


def t_science_case_summaries():
    """The carried cases' summaries on planted records: QC01 (exit 0 and pass), the in-process cases (the carried
    test's own boolean `pass`; anything else fails), QC07 (E4 and formal), QC02 / QC03 (MB r1's criterion AND the
    official configuration: launchd launcher, WORKERS, frozen ladder, planned blocks, launched / detached / finished),
    Q1_theory on the real pinned files and on a planted altered copy, the dev forms (never a pass). The driver's
    record of a FAILED decoy is never evaluated as science: QC02 / QC03 fail, and with a memory-watchdog event in it
    they carry the status QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP (owner supplement 2, section 1); a release
    of an already-broken pool alone is a failed decoy, not that status. After such an event the later official decoys
    of the qualification are not launched (the launching function is a recorder here: nothing can run)."""
    r = {}
    r["qc01"] = Q.qc01_summary({"pass": True, "C_A": {"field_matches": 9}, "C_B": {"failed": []}}, 0)["pass"] is True \
        and Q.qc01_summary({"pass": True}, 3)["pass"] is False and Q.qc01_summary({"pass": False}, 0)["pass"] is False \
        and Q.qc01_summary(None, 0)["pass"] is False and Q.qc01_summary({"pass": "yes"}, 0)["pass"] is False
    r["science_summary"] = Q.science_summary({"pass": True, "x": 1})["pass"] is True and \
        Q.science_summary({"pass": False})["pass"] is False and Q.science_summary({"x": 1})["pass"] is False and \
        Q.science_summary(None)["pass"] is False and Q.science_summary({"pass": 1})["pass"] is False
    r["qc07"] = Q.qc07_summary({"pass": True}, {"pass": True})["pass"] is True and \
        Q.qc07_summary({"pass": False}, {"pass": True})["pass"] is False and \
        Q.qc07_summary({"pass": True}, {"pass": False})["pass"] is False and \
        Q.qc07_summary(None, {"pass": True})["pass"] is False and Q.qc07_summary({"pass": True}, None)["pass"] is False
    d = _full_decoy()
    woc = lambda dec, job=JOB_OK, fb=None, ev=None: Q.with_official_config(  # noqa: E731
        ev or Q.qc02_eval(dec, LADDER), dec, job, fb, 5, 0)
    r["qc02_pass"] = Q.qc02_eval(d, LADDER)["pass"] is True and woc(d)["pass"] is True
    r["qc02_mbr1_criterion"] = Q.qc02_eval(None, LADDER)["pass"] is False and \
        Q.qc02_eval(_full_decoy(first=2), LADDER)["pass"] is False and \
        Q.qc02_eval(_full_decoy(ladder={"RLR": [4], "C2B": [20], "C1B": [4]}), LADDER)["pass"] is False and \
        Q.qc02_eval(_full_decoy(stage2=False), LADDER)["pass"] is False and \
        Q.qc02_eval(dict(d, stage2_decoys=[_s2(), _s2(False)]), LADDER)["pass"] is False
    r["qc02_official_configuration"] = woc(_full_decoy(launched=False))["pass"] is False and \
        woc(_full_decoy(workers=1))["pass"] is False and woc(d, job={"finished": True, "detached": False,
                                                                  "booted_out": True})["pass"] is False and \
        woc(d, fb=3)["pass"] is False and \
        "NOT_UNDER_THE_LAUNCHD_LAUNCHER" in woc(_full_decoy(launched=False))["official_configuration_reasons"]
    d3 = _full_decoy(316, 3, n_blocks=20, stage2=False)
    w3 = lambda dec, job=JOB_OK: Q.with_official_config(Q.qc03_eval(dec), dec, job, 3, 5, 0)  # noqa: E731
    r["qc03"] = Q.qc03_eval(d3)["pass"] is True and w3(d3)["pass"] is True and \
        Q.qc03_eval(_full_decoy(316, 2, n_blocks=20))["pass"] is False and Q.qc03_eval(None)["pass"] is False and \
        w3(_full_decoy(316, 3, n_blocks=20, workers=1))["pass"] is False and \
        w3(_full_decoy(316, 3, n_blocks=20, launched=False))["pass"] is False
    fw = decoy_record(297, None, failed="BrokenProcessPool", events=[CAP_EVENT])
    fb = decoy_record(316, 3, failed="BrokenProcessPool", events=[{"event": RR.BROKEN_POOL_EVENT, "worker_pid": 7}])
    f2, f3 = Q.qc02_eval(fw, LADDER), Q.qc03_eval(fb)
    w2 = Q.with_official_config(Q.decoy_failure(fw), None, JOB_OK, None, 5, 1)
    r["failed_decoy_records"] = f2["pass"] is False and f2["status"] == RR.STATUS_OFFICIAL_WATCHDOG and \
        f2["fail_closed_statuses"] == [RR.STATUS_OFFICIAL_WATCHDOG] and f2["memory_watchdog_events"] == 1 and \
        f3["pass"] is False and f3["status"] == "DECOY_FAILED" and "fail_closed_statuses" not in f3 and \
        f3["memory_watchdog_events"] == 0 and w2["pass"] is False and \
        w2["fail_closed_statuses"] == [RR.STATUS_OFFICIAL_WATCHDOG] and Q.decoy_failure(d) is None and \
        Q.decoy_failure(None) is None and \
        Q.qc03_eval(decoy_record(316, 3, failed="X", events=[CAP_EVENT]))["status"] == RR.STATUS_OFFICIAL_WATCHDOG
    launched, real_od = [], Q.official_decoy
    Q.official_decoy = lambda cell, fblocks, out, work: launched.append(cell) or (
        {"id": f"decoy{cell}", "cell": cell, "watchdog_events": [CAP_EVENT] if cell == 297 else []})
    try:
        ev1, ev2 = {"seen": False}, {"seen": False}
        a1 = Q.official_decoy_gated(ev1, 297, None, Path("x"), Path("y"))
        a2 = Q.official_decoy_gated(ev1, 316, 3, Path("x"), Path("y"))
        b1 = Q.official_decoy_gated(ev2, 316, 3, Path("x"), Path("y"))
        b2 = Q.official_decoy_gated(ev2, 297, None, Path("x"), Path("y"))
    finally:
        Q.official_decoy = real_od
    r["no_official_decoy_after_a_watchdog_event"] = launched == [297, 316, 297] and a1["cell"] == 297 and \
        a2 == {"id": "decoy316", "cell": 316, "record_missing": True,
               "not_run": "AFTER_" + RR.STATUS_OFFICIAL_WATCHDOG} and b1["cell"] == 316 and "not_run" not in b2 and \
        ev1 == {"seen": True} and ev2 == {"seen": True}
    q1 = Q.q1_theory(T.REPO)
    repo = fresh("q1") / "repo"
    (repo / Path(Q.THEORY_REL).parent).mkdir(parents=True)
    (repo / Q.THEORY_REL).write_bytes((T.REPO / Q.THEORY_REL).read_bytes() + b"planted\n")
    r["q1_theory"] = q1["pass"] is True and Q.q1_theory(repo)["pass"] is False
    dl = Q.dev_loader_only("QC05", ["test_mb308_twosided"], T.REPO)
    df = Q.dev_form({"pass": True, "x": 1}, True)
    r["dev_forms_never_pass"] = dl["pass"] is False and dl["status"] == Q.DEV_STATUS and dl["dev_checks_ok"] is True \
        and df["pass"] is False and df["status"] == Q.DEV_STATUS and df["dev_checks_ok"] is True
    return {"ok": all(r.values()), "rows": r}


def t_mbr1_carried_modules_and_pins():
    """MB r1's qualification test modules and committed records are PINNED to MB r1's bytes at 21e99cf0 (sha256 and
    blob, read from the base store) and are present at HEAD with those bytes; each carried module's entry function has
    the parameters the verifier passes (checked from its text; nothing executed); a planted pin mismatch and a planted
    signature mismatch fail; every pin is an external pin of the manifest."""
    bs = T.base_store()
    rows = {}
    for group, pins in (("test", Q.MBR1_TEST_PINS), ("record", Q.MBR1_RECORD_PINS)):
        for k, (rel, want, bl) in pins.items():
            raw = Q.git_show_bytes(T.BASE, rel, repo=bs)
            rows[f"{group}:{k}"] = raw is not None and sha(raw) == want and Q.blob_id(raw) == bl and \
                (T.REPO / rel).read_bytes() == raw
    static = {n: Q.mbr1_test_static(n, T.REPO) for n in Q.MBR1_TEST_PINS}
    saved = dict(Q.MBR1_TEST_PINS), dict(Q.MBR1_TEST_ENTRY)
    try:
        n = "test_mb308_tptb"
        Q.MBR1_TEST_PINS[n] = (saved[0][n][0], "0" * 64, saved[0][n][2])
        bad_pin = Q.mbr1_test_static(n, T.REPO)["pass"] is False
        Q.MBR1_TEST_PINS[n] = saved[0][n]
        Q.MBR1_TEST_ENTRY[n] = ("run", ("CON", "asm", "guard", "indep"))
        bad_sig = Q.mbr1_test_static(n, T.REPO)["pass"] is False
    finally:
        Q.MBR1_TEST_PINS.clear()
        Q.MBR1_TEST_PINS.update(saved[0])
        Q.MBR1_TEST_ENTRY.clear()
        Q.MBR1_TEST_ENTRY.update(saved[1])
    ext = set(Q.EXTERNAL_PINS)
    listed = all(f"qualify:mbr1_test:{k}" in ext for k in Q.MBR1_TEST_PINS) and \
        all(f"qualify:mbr1_record:{k}" in ext for k in Q.MBR1_RECORD_PINS) and \
        {"qualify:mc_307", "qualify:e4_controls", "qualify:a0_r_eval", "qualify:theorem_mb",
         "qualify:theorem_mb_research"} <= ext and len([k for k in ext if k.startswith("qualify:a0_cert:")]) == 5
    try:
        Q.pinned_bytes((Q.MC_PIN[0], "0" * 64, Q.MC_PIN[2]), T.REPO)
        pin_refuses = False
    except ValueError:
        pin_refuses = True
    ok = all(rows.values()) and len(rows) == 9 and all(s["pass"] is True for s in static.values()) and bad_pin and \
        bad_sig and listed and pin_refuses and Q.pinned_bytes(Q.MC_PIN, T.REPO) is not None
    return {"ok": ok, "pins": rows, "static": {k: v["pass"] for k, v in static.items()}, "bad_pin": bad_pin,
            "bad_signature": bad_sig, "listed": listed}


def _job(v, wall=1.0):
    return {"kind": "RLR", "block": 0, "rung": 4, "status": "CERTIFIED", "wall_seconds": wall, "cpu_cap": {"x": wall},
            "record": {"status": "CERTIFIED", "value": v, "seconds": wall, "_log_sha256": str(wall)}}


def t_qc04_determinism_planted():
    """MB r1's QC04 on planted records: equal jobs pass whatever the timing keys, cpu_cap and private fields say; one
    differing certified leaf fails; a job missing on one side fails; an empty comparison fails; the planted one-leaf
    mutation is detected by the same comparison."""
    def dec(v):
        return {"stage1": {"blocks": [{"rlr_rungs": [dict(_job(v, 9.0), rung=4)], "c2b_rungs": [], "c1b_rungs": []}]}}
    serial = {"results": {"RLR:4": _job("a", 2.0)}}
    det = lambda v, w: {"drifts": "3", "results": {"3:C2B:20": dict(_job(v, w), cert_sha256="c")}}  # noqa: E731
    ok_ = Q.qc04_eval(dec("a"), serial, det("x", 1.0), det("x", 5.0))
    diff_serial = Q.qc04_eval(dec("b"), serial, det("x", 1.0), det("x", 5.0))
    diff_ladder = Q.qc04_eval(dec("a"), serial, det("x", 1.0), det("y", 1.0))
    missing = Q.qc04_eval(dec("a"), {"results": {"RLR:4": _job("a"), "RLR:6": _job("a")}}, det("x", 1.0), det("x", 1.0))
    one_side = Q.qc04_eval(dec("a"), serial, det("x", 1.0), {"drifts": "3", "results": {}})
    none = Q.qc04_eval(None, None, None, None)
    ok = ok_["pass"] is True and ok_["serial_vs_pooled"]["RLR:4"]["control_detected"] is True and \
        ok_["serial_vs_pooled"]["RLR:4"]["compared_leaves"] > 0 and diff_serial["pass"] is False and \
        diff_serial["serial_ok"] is False and diff_ladder["pass"] is False and \
        diff_ladder["ladder_pair_identical"] is False and missing["pass"] is False and one_side["pass"] is False and \
        none["pass"] is False
    return {"ok": ok}


def _repro_set(v="a", wall=1.0, workers=5, extra_block_value=None) -> dict:
    def dec(cell, first):
        blocks = [{"index": i, "run": first is None or i < first, "tile": ["0", "1"], "b": "1/2",
                   "rlr_rungs": [dict(_job(v, wall), block=i)], "c2b_rungs": [], "c1b_rungs": [],
                   "pointwise": {"status": "CERTIFIED", "U": "7/2"}, "rlr_block": {"x": v}} for i in range(3)]
        if extra_block_value is not None:
            blocks[2]["pointwise"]["U"] = extra_block_value
        d = {"decoy_cell": cell, "blocks_total": 3, "blocks_run": "all" if first is None else list(range(first)),
             "dev_ladder": False, "driver_sha256": str(wall), "utc": str(wall), "wall_seconds": wall,
             "stage1_wall_seconds": wall, "cpu_caps": {"parent": str(wall)}, "host": {"x": wall},
             "lifecycle": {"y": wall}, "stage1": {"blocks": blocks, "workers": workers, "ladder": LADDER,
                                                  "n_verifications": 2, "U": ["7/2"]}}
        if cell == 297:
            d["stage2_decoys"] = [{"stage2": {"gates": {"g": {"pass": True}}, "seconds": wall}, "supply": {"s": v}}]
            d["stage2_wall_seconds"] = wall
        return d
    return {"decoy297": dec(297, None), "decoy316": dec(316, 2),
            "serial": {"block": 0, "wall_seconds": wall, "results": {"RLR:4": _job(v, wall)}},
            "det_a": {"drifts": "3", "wall_seconds": wall, "results": {"3:C2B:20": dict(_job(v, wall), cert_sha256=v)}},
            "det_b": {"drifts": "3", "wall_seconds": wall, "results": {"3:C2B:20": dict(_job(v, wall), cert_sha256=v)}}}


def t_mbr1_repro_planted():
    """MBR1_REPRO (RC2), full form, on planted records: exact equality passes whatever the timing keys, the per-job
    cpu_cap, the provenance (host, lifecycle, driver sha256, utc, walls, cpu-caps record) and stage1.workers say; ONE
    differing certified leaf in Stage 1, in a Stage-2 bundle, in the serial record or in a ladder record fails, and so
    do a missing record, a missing job and a different block set; every comparison is non-vacuous and detects a planted
    one-leaf mutation. The tiny (dev) form is never a pass."""
    theirs = _repro_set("a", 1.0, workers=1)
    same = Q.mbr1_repro(_repro_set("a", 99.0, workers=5), theirs)
    rows = {"equal_whatever_timing_and_provenance": same["pass"] is True and
            same["decoy297"]["compared_leaves"] > 5 and same["decoy297"]["control_detected"] is True and
            same["serial"]["RLR:4"]["control_detected"] is True}
    s1 = _repro_set("a")
    s1["decoy316"]["stage1"]["blocks"][1]["rlr_rungs"][0]["record"]["value"] = "b"
    rows["stage1_leaf_differs"] = Q.mbr1_repro(s1, theirs)["pass"] is False and \
        Q.mbr1_repro(s1, theirs)["decoy316"]["equal"] is False
    s2 = _repro_set("a")
    s2["decoy297"]["stage2_decoys"][0]["supply"]["s"] = "b"
    rows["stage2_leaf_differs"] = Q.mbr1_repro(s2, theirs)["pass"] is False
    pw = Q.mbr1_repro(_repro_set("a", extra_block_value="9/2"), theirs)
    rows["pointwise_leaf_differs"] = pw["pass"] is False
    s3 = _repro_set("a")
    s3["serial"]["results"]["RLR:4"]["record"]["value"] = "b"
    rows["serial_leaf_differs"] = Q.mbr1_repro(s3, theirs)["pass"] is False
    s4 = _repro_set("a")
    s4["det_b"]["results"]["3:C2B:20"]["cert_sha256"] = "z"
    rows["ladder_leaf_differs"] = Q.mbr1_repro(s4, theirs)["pass"] is False
    s5 = _repro_set("a")
    s5["det_a"]["results"]["3:C2B:40"] = _job("a")
    rows["extra_job_on_one_side"] = Q.mbr1_repro(s5, theirs)["pass"] is False
    s6 = _repro_set("a")
    s6["decoy316"]["blocks_run"] = [0, 1, 2]
    rows["different_block_set"] = Q.mbr1_repro(s6, theirs)["pass"] is False
    s7 = _repro_set("a")
    s7["decoy297"] = None
    rows["missing_record"] = Q.mbr1_repro(s7, theirs)["pass"] is False
    rows["empty_serial_is_vacuous"] = Q.mbr1_repro(dict(_repro_set("a"), serial={"results": {}}),
                                                   dict(theirs, serial={"results": {}}))["pass"] is False
    tiny_src = {"stage1": {"blocks": [{"tile": ["0", "1"], "hull": ["0", "1"], "b": "1/2",
                                       "rlr_rungs": [dict(_job("a", 1.0), rung=4)],
                                       "c2b_rungs": [dict(_job("a", 2.0), rung=20)]}]}}
    tiny_same = Q.mbr1_repro_tiny(copy.deepcopy(tiny_src), tiny_src)
    tb = copy.deepcopy(tiny_src)
    tb["stage1"]["blocks"][0]["c2b_rungs"][0]["record"]["value"] = "b"
    rows["tiny_form_never_passes"] = tiny_same["pass"] is False and tiny_same["dev_checks_ok"] is True and \
        Q.mbr1_repro_tiny(tb, tiny_src)["dev_checks_ok"] is False and \
        Q.mbr1_repro_tiny(None, tiny_src)["dev_checks_ok"] is False
    return {"ok": all(rows.values()), "rows": rows}


# ------------------------------------------------------------------ section 11.2 (a): derivation, comparison, apply
def set_line(src: str, name: str, value: str) -> str:
    """The driver text with the ONE module-level single-line assignment `name = ...` replaced (whatever value the
    driver carries: provisional before the apply step, the rule output after it)."""
    import re
    new, n = re.subn(rf"(?m)^{name} = .*$", f"{name} = {value}", src)
    if n != 1:
        raise RuntimeError(f"{name} is not bound once on one line")
    return new


def t_driver_constants_exact():
    """The derivation module reads the five rule constants from a driver's TEXT exactly: integers, the float literal's
    DECIMAL TEXT as a rational (never the binary float), p / q as a fraction, EXCL_ALLOW as the canonical sorted
    list; a non-literal constant or a name bound twice refuses."""
    c = DV.driver_constants(DRV)
    out = DV.driver_outputs(DRV)
    v = {"MEM_CAP_BYTES": ("1280 * 1024 ** 2", 1280 * MIB), "MEM_POLL_S": ("1 / 3", "1/3"),
         "EXCL_CPU_PCT": ("40.0", 40), "FREE_MEM_MIN_BYTES": ("3 * 1024 ** 3", 3 * GIB)}
    rows = {}
    for key, (new, want) in v.items():
        rows[key] = DV.driver_constants(set_line(DRV, key, new))[key] == want
    rows["poll_decimal_text_is_exact"] = DV.driver_constants(set_line(DRV, "MEM_POLL_S", "0.1"))["MEM_POLL_S"] == \
        "1/10" and DV.driver_constants(set_line(DRV, "MEM_POLL_S", "2.0"))["MEM_POLL_S"] == "2"
    for name, plant in (("non_literal", set_line(DRV, "MEM_CAP_BYTES", "int('3')")),
                        ("bound_twice", DRV + "\nMEM_CAP_BYTES = 1\n"),
                        ("non_integer_pct", set_line(DRV, "EXCL_CPU_PCT", "25.5")),
                        ("allow_not_literal", DRV.replace("EXCL_ALLOW = frozenset({", "EXCL_ALLOW = set({"))):
        try:
            DV.driver_constants(plant)
            rows[name] = False
        except DV.DeriveRefusal:
            rows[name] = True
    ok = isinstance(c["MEM_CAP_BYTES"], int) and c["WORKERS"] == 5 and c["DECOY_CELLS"] == [297, 316] and \
        out["EXCL_ALLOW"] == sorted(set(out["EXCL_ALLOW"])) and set(out) == set(DV.OUTPUTS) and all(rows.values())
    return {"ok": ok, "rows": rows}


def t_derive_adapters_and_planned_runs():
    """The adapters from a driver decoy record to the rule inputs: every R-MEM input is taken from the record's own
    fields (job ru_maxrss, the watchdog events and peak, the driver's peak RSS, the sampler, the run configuration);
    a run that is not one of the planned official decoys (cell, blocks, exit, checkpoint-served jobs) is named; the
    sampler input is the largest growth rate and the largest OBSERVED spacing over the runs (READING-6 as corrected);
    W_idle is the largest wired-down reading (READING-11); a missing field stays missing and the rule function names
    it; the driver's record of a FAILED decoy is named (DECOY_FAILED) and, when it carries a memory-watchdog event,
    still reaches the rule function (it is never dropped as "not as planned")."""
    rec = decoy_record(297, None)
    run = DV.compact_run(rec, "decoy297", exit_code=0, raw_sha256="x")
    ri = DV.run_input(run)
    r = {"fields": ri["launcher"] is True and ri["ladder"] == "frozen" and ri["workers"] == 5 and
         ri["mem_cap_bytes"] == 3 * GIB and ri["mem_poll_s"] == "2.0" and ri["watchdog_events"] == [] and
         ri["driver_maxrss_bytes"] == 64 * MIB and ri["worker_peak_rss_bytes"] == 102 * MIB and
         len(ri["jobs"]) == 8 and {j["kind"] for j in ri["jobs"]} == {"RLR", "C2B", "C1B"} and
         all(isinstance(j["rung"], int) for j in ri["jobs"]) and RR._run_reasons(ri) == []}
    pr = lambda **k: DV.plan_reasons(run_of(k.pop("cell", 297), **k), PLAN)  # noqa: E731
    r["plan"] = pr() == [] and pr(cell=316) == [] and \
        DV.plan_reasons(DV.compact_run(decoy_record(297, 2), "x", exit_code=0), PLAN) == ["BLOCKS_NOT_AS_PLANNED"] and \
        DV.plan_reasons(DV.compact_run(decoy_record(316, None), "x", exit_code=0), PLAN) == ["BLOCKS_NOT_AS_PLANNED"] \
        and DV.plan_reasons(DV.compact_run(decoy_record(305, None), "x"), PLAN) == ["CELL_NOT_IN_THE_PLAN"] and \
        pr(exit_code=1) == ["RUN_EXIT_NOT_ZERO"] and pr(served=2) == ["JOBS_NOT_ALL_COMPUTED_BY_THIS_RUN"]
    si = DV.sampler_input([run_of(297, growth=5 * MIB, spacing_ns=410_000_000), run_of(316, growth=9 * MIB)])
    broken = run_of(297)
    broken["rss_sampler"] = None
    unstated = run_of(316)
    del unstated["rss_sampler"]["max_spacing_ns"]
    r["sampler"] = si["max_growth_bytes_per_s"] == 9 * MIB and si["interval_s"] == "1/4" and \
        si["max_spacing_ns"] == 410_000_000 and RR.sampler_reasons(si) == [] and \
        DV.sampler_input([run_of(297), broken]) is None and DV.sampler_input([]) is None and \
        DV.sampler_input([run_of(297), unstated])["max_spacing_ns"] is None and \
        RR.sampler_reasons(DV.sampler_input([run_of(297), unstated])) == ["SAMPLER_OBSERVED_SPACING_UNRECORDED"] and \
        RR.sampler_reasons(DV.sampler_input([run_of(297, spacing_ns=500_000_000)])) == [] and \
        RR.sampler_reasons(DV.sampler_input([run_of(297), run_of(316, spacing_ns=500_000_001)])) == \
        ["SAMPLER_OBSERVED_SPACING_ABOVE_0.5_S"]
    failed = DV.compact_run(decoy_record(297, None, failed="BrokenProcessPool", events=[CAP_EVENT]), "decoy297",
                            exit_code=1)
    rules = DV.apply_rules(runs=[failed, run_of(316)], readings=readings(procs=[SIP_PROC]), hw_memsize_bytes=16 * GIB,
                           hosting_app_paths=HOSTING["paths"], base_names=base_names(), h3_readings=H3, plan=PLAN,
                           workers=5, mem_poll_s=F(2), measurement_cap_bytes=3 * GIB, measurement_poll_s=F(2))
    r["failed_decoy_named_and_its_event_reaches_the_rule"] = failed["decoy_failed"] == "BrokenProcessPool" and \
        "DECOY_FAILED" in DV.plan_reasons(failed, PLAN) and rules["r_mem"]["status"] == "RERUN_REQUIRED" and \
        rules["r_mem"]["uncured_event_runs"] == ["decoy297"] and DV.stop_statuses(rules) == [RR.STATUS_STEP1_RERUN]
    hi = DV.host_input(readings(wired=[1000, 3000] + [1000] * 8), 16 * GIB)
    r["host_input_reading_11"] = hi["wired_pages"] == 3000 and hi["page_size_bytes"] == 16384 and \
        DV.host_input(readings(), None) is None and DV.host_input([], 16 * GIB) is None
    missing = DV.compact_run({"decoy_cell": 297}, "x")
    r["missing_fields_named_by_the_rule"] = {"JOB_PEAKS_UNRECORDED", "DRIVER_PEAK_UNRECORDED",
                                             "WATCHDOG_EVENTS_UNRECORDED", "NOT_UNDER_LAUNCHD_LAUNCHER"} <= \
        set(RR._run_reasons(DV.run_input(missing)))
    frozen = DV.run_input(run_of(297, cap=GIB, poll=0.5))
    r["frozen_configuration_parameter"] = RR._run_reasons(frozen) != [] and \
        RR._run_reasons(frozen, GIB, F(1, 2)) == [] and \
        "MEM_POLL_S_NOT_AS_RULED" in RR._run_reasons(DV.run_input(run_of(297, cap=GIB, poll=2.0)), GIB, F(1, 2)) and \
        "MEM_POLL_S_NOT_2" in RR._run_reasons(DV.run_input(run_of(297, poll=0.5)))
    return {"ok": all(r.values()), "rows": r}


def t_derivation_outputs_and_checks():
    """The derivation tool on PLANTED designated evidence: the five canonical outputs equal an independent exact
    computation and are in the canonical form the rule text fixes; every built-in rule check is recorded and a failing
    one leaves the derivation NOT_DERIVED with no output: step-5 feasibility, R-FREE attainability, a process left
    above the threshold (host not prepared), a run outside the plan, a missing planned cell, readings not as ruled, a
    sampler record whose OBSERVED spacing is above 0.5 s or not stated; evidence that is not designated is never
    derived. The two fail-closed statuses of owner supplement 2: a memory-watchdog event gives STEP1_RERUN_REQUIRED
    (also from the driver's failed-decoy record, and not cured by a clean duplicate); step 6's unrounded-quotient
    branch gives MEM_POLL_S_NONCANONICAL_BRANCH with the raw evidence and the branch, no value and nothing rounded;
    the clip to 0.5 s is canonical and derives."""
    d = derive(evidence())
    out = d["outputs"]
    names = set(base_names()) | {"spotlightknowledged.updater", "cloudd", "BackgroundShortcutRunner", "modelcatalogd",
                                 "plantedd"}
    r = {"ok": d["status"] == "OK" and d["designated"] is True and d["checks"]["all_hold"] is True and
         all(out[k] == v for k, v in EXPECT.items()) and out["EXCL_ALLOW"] == sorted(names) and
         d["rules"]["r_mem"]["P_bytes"] == 102 * MIB and d["rules"]["r_mem"]["D_bytes"] == 64 * MIB and
         d["target_evaluations"] == 0}
    big = derive(evidence(runs=[run_of(297, rss_mb=700), run_of(316, rss_mb=700)], hw=4 * GIB))
    r["step5_feasibility"] = big["status"] == "NOT_DERIVED" and big["checks"]["r_mem_step5_feasible"] is False and \
        all(v is None for v in big["outputs"].values()) and big["rules"]["r_mem"]["status"] == "FAILS_ON_MEMORY"
    un = derive(evidence(rds=readings(free=GIB, procs=[SIP_PROC])))
    r["r_free_attainability"] = un["status"] == "NOT_DERIVED" and un["checks"]["r_free_attainable"] is False and \
        un["outputs_as_computed"]["FREE_MEM_MIN_BYTES"] == 2 * GIB and un["outputs"]["FREE_MEM_MIN_BYTES"] is None
    busy = {"pid": 9, "comm": "/Applications/Busy.app/Contents/MacOS/Busy", "pcpu": "80.0", "hosting_app": False}
    np_ = derive(evidence(rds=readings(procs=[busy])))
    r["host_not_prepared"] = np_["status"] == "NOT_DERIVED" and \
        np_["checks"]["host_prepared_no_process_left_above_the_threshold"] is False and \
        "Busy" not in (np_["outputs_as_computed"]["EXCL_ALLOW"] or [])
    none = lambda x: all(v is None for v in x["outputs"].values())  # noqa: E731
    wd = derive(evidence(runs=[run_of(297, events=[{"worker_pid": 1}]), run_of(316)]))
    r["watchdog_event"] = wd["status"] == RR.STATUS_STEP1_RERUN == "STEP1_RERUN_REQUIRED" and none(wd) and \
        wd["checks"]["r_mem_no_rerun_required"] is False and wd["stop_before_freeze"] is True and \
        wd["rules"]["r_mem"]["status"] == "RERUN_REQUIRED" and wd["fail_closed_statuses"] == [RR.STATUS_STEP1_RERUN] \
        and wd["rules"]["r_mem"]["rerun_step5_bound"]["rerun_cap_bytes"] == 6 * GIB
    wf = derive(evidence(runs=[DV.compact_run(decoy_record(297, None, failed="BrokenProcessPool", events=[CAP_EVENT]),
                                              "decoy297", exit_code=1), run_of(316)]))
    dup = dict(run_of(297), id="decoy297_again")
    wc = derive(evidence(runs=[run_of(297, events=[CAP_EVENT]), dup, run_of(316)]))
    r["watchdog_event_failed_record_and_clean_duplicate"] = wf["status"] == RR.STATUS_STEP1_RERUN and none(wf) and \
        wc["status"] == RR.STATUS_STEP1_RERUN and none(wc) and wc["rules"]["r_mem"]["missing_cells"] == []
    bad_forms = {"MEM_CAP_BYTES": [GIB + 1, 768 * MIB, 1.5 * GIB, True], "MEM_POLL_S": ["128/125", "4/2", "2.0", 2, "0"],
                 "FREE_MEM_MIN_BYTES": [GIB, 2 * GIB + 1], "EXCL_CPU_PCT": [30, 26, 55, 25.0],
                 "EXCL_ALLOW": [[], ["b", "a"], ["a", "a"], ["/usr/libexec/a"], [""], "a"]}
    r["canonical_forms"] = d["form_reasons"] == [] and DV.form_reasons(out) == [] and all(
        DV.form_reasons(dict(out, **{k: v})) == [f"{k}_NOT_CANONICAL"] for k, vs in bad_forms.items() for v in vs) \
        and DV.EXCL_PCT_VALUES == (25, 35, 40, 45, 50) and DV.POLL_VALUES == (F(2), F(1, 2))
    pl = derive(evidence(runs=[run_of(297), DV.compact_run(decoy_record(316, None), "decoy316", exit_code=0)]))
    r["run_outside_the_plan"] = pl["status"] == "NOT_DERIVED" and pl["checks"]["runs_all_as_planned"] is False
    one = derive(evidence(runs=[run_of(297)]))
    r["planned_cell_missing"] = one["status"] == "NOT_DERIVED" and \
        one["rules"]["r_mem"]["status"] == "INCOMPLETE_INPUT"
    r["readings_not_as_ruled"] = derive(evidence(rds=readings(9, procs=[SIP_PROC])))["status"] == "NOT_DERIVED" and \
        derive(evidence(rds=readings(spacing=29, procs=[SIP_PROC])))["status"] == "NOT_DERIVED" and \
        derive(evidence(rds=readings(power="Battery Power", procs=[SIP_PROC])))["status"] == "NOT_DERIVED"
    nd = derive(evidence(designated=False))
    inv = derive(dict(evidence(), invalid_reasons=["decoy297:THERMAL_EVENT_DURING_RUN"]))
    r["not_designated_never_derived"] = nd["status"] == "NOT_DERIVED" and nd["designated"] is False and \
        nd["evidence_reasons"] == ["NOT_DESIGNATED"] and all(v is None for v in nd["outputs"].values()) and \
        inv["status"] == "NOT_DERIVED" and "INVALID_REASONS_RECORDED" in inv["evidence_reasons"]
    hot = derive(evidence(runs=[run_of(297, growth=100 * MIB), run_of(316)]))
    r["step6_noncanonical_branch_stops_before_freeze"] = hot["status"] == RR.STATUS_POLL_NONCANONICAL == \
        "MEM_POLL_S_NONCANONICAL_BRANCH" and none(hot) and hot["stop_before_freeze"] is True and \
        hot["fail_closed_statuses"] == [RR.STATUS_POLL_NONCANONICAL] and hot["poll"]["recheck_ok"] is False and \
        hot["poll"]["case"] == "iii" and hot["poll"]["canonical"] is False and hot["poll"]["MEM_POLL_S"] is None and \
        hot["outputs_as_computed"]["MEM_POLL_S"] is None and \
        hot["poll"]["unrounded_quotient_not_an_output"] == RR.fstr(F(GIB, 10) / (100 * MIB)) == "128/125" and \
        hot["poll"]["g_bytes_per_s"] == str(100 * MIB) and hot["poll"]["MEM_CAP_BYTES"] == GIB and \
        "otherwise-branch" in hot["poll"]["branch"]
    clip = derive(evidence(runs=[run_of(297, growth=300 * MIB), run_of(316)]))
    r["step6_clip_to_half_a_second_is_canonical"] = clip["status"] == "OK" and clip["outputs"]["MEM_POLL_S"] == "1/2" \
        and clip["poll"]["case"] == "ii" and clip["outputs"]["MEM_CAP_BYTES"] == GIB and clip["form_reasons"] == []
    slow = derive(evidence(runs=[run_of(297, spacing_ns=500_000_001), run_of(316)]))
    edge = derive(evidence(runs=[run_of(297, spacing_ns=500_000_000), run_of(316)]))
    un = run_of(316)
    del un["rss_sampler"]["max_spacing_ns"]
    unst = derive(evidence(runs=[run_of(297), un]))
    r["sampler_observed_spacing_binds"] = slow["status"] == "NOT_DERIVED" and none(slow) and \
        slow["checks"]["r_mem_step6_sampler_valid"] is False and \
        slow["rules"]["r_mem"]["reason"] == "SAMPLER_OBSERVED_SPACING_ABOVE_0.5_S" and edge["status"] == "OK" and \
        unst["status"] == "NOT_DERIVED" and \
        unst["rules"]["r_mem"]["reason"] == "SAMPLER_OBSERVED_SPACING_UNRECORDED"
    host_busy = {"pid": 5, "comm": "/Applications/Planted.app/Contents/MacOS/Planted", "pcpu": "28.4",
                 "hosting_app": True}
    hb = derive(evidence(rds=readings(procs=[host_busy])))
    r["hosting_app_exception_feeds_r_allow"] = hb["status"] == "OK" and hb["outputs"]["EXCL_CPU_PCT"] == 40 and \
        "cloudd" not in hb["outputs"]["EXCL_ALLOW"] and "spotlightknowledged.updater" in hb["outputs"]["EXCL_ALLOW"]
    return {"ok": all(r.values()), "rows": r}


def t_compare_is_exact_no_tolerance():
    """The comparison of canonical outputs is EXACT for each of the five: one byte, one percent step, one rational
    step or one name of difference fails; there is no tolerance, no superset / subset reading and no canonicalisation
    that hides a difference; a missing output never agrees; all three (A, B, the driver's constants) must agree."""
    A = dict(EXPECT, EXCL_ALLOW=["a", "b", "c"])
    eq = DV.compare(A, copy.deepcopy(A), copy.deepcopy(A))
    rows = {"equal": eq["all_equal"] is True and all(v["equal"] for v in eq["outputs"].values())}

    def differs(key, value, where="B"):
        a, b, c = copy.deepcopy(A), copy.deepcopy(A), copy.deepcopy(A)
        {"A": a, "B": b, "C": c}[where][key] = value
        r = DV.compare(a, b, c)
        return r["all_equal"] is False and r["outputs"][key]["equal"] is False and \
            all(v["equal"] for k, v in r["outputs"].items() if k != key)
    rows["mem_cap_one_byte"] = differs("MEM_CAP_BYTES", GIB + 1) and differs("MEM_CAP_BYTES", GIB + 256 * MIB, "C")
    rows["free_min_one_step"] = differs("FREE_MEM_MIN_BYTES", 2 * GIB + 256 * MIB)
    rows["excl_pct_one_step"] = differs("EXCL_CPU_PCT", 30) and differs("EXCL_CPU_PCT", 30, "A")
    rows["poll_tiny_rational_difference"] = differs("MEM_POLL_S", "2000000001/1000000000") and \
        differs("MEM_POLL_S", "1/2", "C")
    rows["poll_same_rational_other_form"] = DV.compare(dict(A, MEM_POLL_S="4/2"), A, A)["all_equal"] is True
    rows["allow_superset_is_not_agreement"] = differs("EXCL_ALLOW", ["a", "b", "c", "d"])
    rows["allow_subset_is_not_agreement"] = differs("EXCL_ALLOW", ["a", "b"])
    rows["allow_driver_differs"] = differs("EXCL_ALLOW", ["a", "b", "x"], "C")
    rows["allow_duplicate_is_not_canonical"] = differs("EXCL_ALLOW", ["a", "b", "c", "c"])
    rows["missing_output_never_agrees"] = differs("MEM_CAP_BYTES", None) and differs("EXCL_ALLOW", None, "A") and \
        DV.compare(dict.fromkeys(DV.OUTPUTS), dict.fromkeys(DV.OUTPUTS), dict.fromkeys(DV.OUTPUTS))["all_equal"] \
        is False
    rows["bool_is_not_an_integer"] = differs("EXCL_CPU_PCT", True)
    names = DV.compare(dict(A, EXCL_ALLOW=["a", "b", "c", "d"]), A, A)["outputs"]["EXCL_ALLOW"]
    rows["difference_is_named"] = names["only_in_A"] == ["d"] and names["only_in_B"] == []
    return {"ok": all(rows.values()), "rows": rows}


def t_apply_literals_and_constants():
    """The apply step's text rewriting on a COPY of the driver's text: exactly the value expressions of the five rule
    constants change; every other top-level statement is byte-identical; the rewritten text carries exactly the
    outputs (read back exactly); MEM_POLL_S is written only as `2.0` or `0.5` (the two canonical outputs); the
    protocol table is rewritten between its markers only. Malformed outputs refuse, and so does every output that is
    not in its canonical form: a quotient for MEM_POLL_S (nothing is rounded, no p / q expression is written), a cap
    that is not a multiple of 256 MiB or below its floor, a percentage outside 25 / 35 / 40 / 45 / 50, a path."""
    cur = DV.driver_outputs(DRV)          # planted outputs that differ from whatever the driver carries, in all five
    outs = {"MEM_CAP_BYTES": cur["MEM_CAP_BYTES"] + 256 * MIB, "MEM_POLL_S": "1/2" if cur["MEM_POLL_S"] != "1/2" else "2",
            "FREE_MEM_MIN_BYTES": cur["FREE_MEM_MIN_BYTES"] + 256 * MIB,
            "EXCL_CPU_PCT": 40 if cur["EXCL_CPU_PCT"] != 40 else 35,
            "EXCL_ALLOW": sorted((set(cur["EXCL_ALLOW"]) | {"zzd"}) - {"launchd"})}
    new = RP.apply_constants(DRV, outs)
    got = DV.driver_outputs(new)
    a = [(getattr(n.targets[0], "id", None) if isinstance(n, ast.Assign) and len(n.targets) == 1 else None,
          ast.get_source_segment(DRV, n)) for n in ast.parse(DRV).body]
    b = [(getattr(n.targets[0], "id", None) if isinstance(n, ast.Assign) and len(n.targets) == 1 else None,
          ast.get_source_segment(new, n)) for n in ast.parse(new).body]
    changed = [x[0] for x, y in zip(a, b) if x != y]
    r = {"outputs_read_back_exactly": got == {**outs, "MEM_POLL_S": RR.fstr(F(outs["MEM_POLL_S"]))},
         "only_the_five_statements_change": len(a) == len(b) and sorted(changed) == sorted(RP.RULE_CONSTANTS),
         "identity_apply_is_stable": DV.driver_outputs(RP.apply_constants(DRV, DV.driver_outputs(DRV))) ==
         DV.driver_outputs(DRV),
         "lines_within_120_columns": max(len(ln) for ln in RP.allow_literal(outs["EXCL_ALLOW"]).splitlines()) <= 120}
    lits = {x: RP.poll_literal(x) for x in ("2", "1/2")}
    r["poll_literals_exact"] = lits == {"2": "2.0", "1/2": "0.5"} and all(
        DV.driver_constants(set_line(DRV, "MEM_POLL_S", v))["MEM_POLL_S"] == k for k, v in lits.items())
    refused = {}
    for x in ("5/4", "1/3", "128/125", "161061273/123456789", "4/2", "2.0", "0.5", "0", "1", "-2", "x", 2, None):
        try:
            refused[str(x)] = RP.poll_literal(x)
        except RP.Refused as e:
            refused[str(x)] = e.code == "OUTPUT_NOT_CANONICAL"
    r["poll_quotient_or_other_form_never_written"] = all(v is True for v in refused.values())
    for name, bad in (("missing_output", {k: v for k, v in outs.items() if k != "MEM_POLL_S"}),
                      ("float_output", dict(outs, MEM_CAP_BYTES=1.5)), ("empty_allow", dict(outs, EXCL_ALLOW=[])),
                      ("duplicate_allow", dict(outs, EXCL_ALLOW=["a", "a"])),
                      ("zero_poll", dict(outs, MEM_POLL_S="0")), ("bool_pct", dict(outs, EXCL_CPU_PCT=True)),
                      ("noncanonical_poll", dict(outs, MEM_POLL_S="128/125")),
                      ("cap_not_a_multiple_of_256_MiB", dict(outs, MEM_CAP_BYTES=GIB + 1)),
                      ("cap_below_1_GiB", dict(outs, MEM_CAP_BYTES=768 * MIB)),
                      ("free_below_2_GiB", dict(outs, FREE_MEM_MIN_BYTES=GIB)),
                      ("pct_30", dict(outs, EXCL_CPU_PCT=30)),
                      ("allow_with_a_path", dict(outs, EXCL_ALLOW=["/usr/libexec/a", "b"]))):
        try:
            RP.apply_constants(DRV, bad)
            r[name] = False
        except RP.Refused:
            r[name] = True
        except Exception:                                    # noqa: BLE001 (anything but the refusal is a failure)
            r[name] = False
    # a PLANTED literal that would add a statement to the driver: the apply step must refuse it
    real_literals = RP.output_literals
    RP.output_literals = lambda o: dict(real_literals(o), MEM_CAP_BYTES=f"{o['MEM_CAP_BYTES']}\nPLANTED_STATEMENT = 1")
    try:
        RP.apply_constants(DRV, outs)
        r["another_statement_would_change_refused"] = False
    except RP.Refused as e:
        r["another_statement_would_change_refused"] = e.code == "APPLY_CHECK"
    finally:
        RP.output_literals = real_literals
    proto = PROTO.read_text()
    newp = RP.apply_protocol(proto, outs, "RULE OUTPUT A (planted)")
    tab = RP.table_outputs(newp)
    i, j = proto.index(RP.TABLE_BEGIN), proto.index(RP.TABLE_END)
    r["protocol_only_the_table_changes"] = newp[:i] == proto[:i] and newp.endswith(proto[j:]) and \
        {k: tab[k] for k in RP.RULE_CONSTANTS} == {**outs, "MEM_POLL_S": outs["MEM_POLL_S"]} and \
        set(tab["_status"].values()) == {"RULE OUTPUT A (planted)"}
    try:
        RP.apply_protocol(proto.replace(RP.TABLE_END, ""), outs, "x")
        r["protocol_without_markers_refused"] = False
    except RP.Refused:
        r["protocol_without_markers_refused"] = True
    return {"ok": all(r.values()), "rows": r}


def t_protocol_table_is_the_drivers_constants():
    """The protocol's rule-output table states exactly the five constants the driver carries (whatever they are:
    provisional before the apply step, the rule outputs after it), and its status column says which."""
    tab = RP.table_outputs(PROTO.read_text())
    cur = DV.driver_outputs(DRV)
    status = set(tab.get("_status", {}).values())
    same = {k: (F(tab[k]) == F(cur[k]) if k == "MEM_POLL_S" else tab.get(k) == cur[k]) for k in RP.RULE_CONSTANTS}
    provisional = status == {RP.PROVISIONAL}
    applied = len(status) == 1 and next(iter(status)).startswith("RULE OUTPUT A (designated derivation sha256 `")
    return {"ok": all(same.values()) and (provisional or applied), "same": same, "status": sorted(status)}


def _official(runs=None, rds=None, hosting=None, hw=16 * GIB) -> dict:
    return {"readings": rds if rds is not None else readings(procs=[SIP_PROC]), "hosting_app": hosting or HOSTING,
            "hw_memsize_bytes": hw, "host_report": planted_host_report(), "runs": runs if runs is not None else
            [run_of(297, cap=EXPECT["MEM_CAP_BYTES"]), run_of(316, cap=EXPECT["MEM_CAP_BYTES"])]}


def _rro(**k) -> dict:
    """R_RULES_OFFICIAL on planted inputs: the measured driver is the code under test's driver text; the frozen driver
    is that text with the outputs A applied by the apply step's own function."""
    ev = k.pop("ev", None) or evidence()
    raw = json.dumps(ev, sort_keys=True).encode()
    d = k.pop("derivation", None) or derive(ev)
    frozen = k.pop("frozen", None)
    if frozen is None:
        frozen = RP.apply_constants(DRV, d["outputs"]) if d["status"] == "OK" else DRV
    return Q.r_rules_official(evidence=ev, evidence_sha256=sha(raw), derivation=d,
                              official=k.pop("official", None) or _official(), driver_src=frozen,
                              measured_driver_src=k.pop("measured", DRV), cfg=CFG, base_names=base_names(), HOST=HOST)


def t_r_rules_official_exact_agreement():
    """R_RULES_OFFICIAL (section 11.2 option (a)) on planted inputs: it passes when B (official measurements, made
    with the FROZEN cap and poll) == A (designated evidence) == the frozen driver's constants for all five; and FAILS,
    naming the output, when B differs in any one of the five (MEM_CAP by a rounding step, MEM_POLL_S 2 against the
    0.5 s clip, FREE_MEM_MIN, EXCL_CPU_PCT, EXCL_ALLOW by one name more or one name fewer); when the frozen driver
    carries a value that is not A; when a built-in rule check fails for B; when an official decoy was not under the
    launchd launcher, ran with a cap other than the frozen one, has a sampler record whose observed spacing is above
    0.5 s, or its host provenance is not CLEAN or shows a thermal event; when the committed derivation is not the
    recomputation; when the frozen driver differs from the measured driver in anything but the five constants; without
    designated evidence. Owner supplement 2: ANY memory-watchdog event in an official decoy fails CLOSED with the
    status QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP (from a full record, from the driver's failed-decoy record,
    and whatever clean duplicate of the cell exists); the unrounded-quotient branch of step 6 in the official series
    fails CLOSED with MEM_POLL_S_NONCANONICAL_BRANCH and B's MEM_POLL_S is None (no comparison value is made); a frozen
    0.5 s re-checked on either canonical branch agrees. The aggregator lifts both statuses to the qualification."""
    good = _rro()
    cap = EXPECT["MEM_CAP_BYTES"]
    r = {"pass": good["pass"] is True and all(v["equal"] for v in good["comparison_by_output"].values()) and
         good["B"]["checks"]["all_hold"] is True and good["A"]["status"] == "OK" and
         good["frozen_driver_is_measured_driver_with_the_five_outputs_applied"] is True and
         good["status"] == "EXACT_AGREEMENT" and good["fail_closed_statuses"] == [] and
         good["B"]["form_reasons"] == []}

    def only(res, key):
        return res["pass"] is False and res["comparison_by_output"][key]["equal"] is False and \
            all(v["equal"] for k, v in res["comparison_by_output"].items() if k != key)
    b_cap = _rro(official=_official([run_of(297, cap=cap, rss_mb=400), run_of(316, cap=cap, rss_mb=400)]))
    r["B_mem_cap_differs"] = b_cap["pass"] is False and b_cap["comparison_by_output"]["MEM_CAP_BYTES"]["equal"] is False
    b_poll = _rro(official=_official([run_of(297, cap=cap, growth=300 * MIB), run_of(316, cap=cap)]))
    r["B_mem_poll_differs"] = only(b_poll, "MEM_POLL_S") and b_poll["B"]["outputs"]["MEM_POLL_S"] == "1/2" and \
        b_poll["A"]["outputs"]["MEM_POLL_S"] == "2" and b_poll["fail_closed_statuses"] == [] and \
        b_poll["status"] == "NOT_IN_AGREEMENT"
    b_nc = _rro(official=_official([run_of(297, cap=cap, growth=100 * MIB), run_of(316, cap=cap)]))
    row = b_nc["comparison_by_output"]["MEM_POLL_S"]
    r["B_noncanonical_poll_branch_fails_closed_no_value"] = b_nc["pass"] is False and \
        b_nc["status"] == RR.STATUS_POLL_NONCANONICAL and \
        b_nc["fail_closed_statuses"] == [RR.STATUS_POLL_NONCANONICAL] and \
        b_nc["B"]["outputs"]["MEM_POLL_S"] is None and row["B"] is None and row["equal"] is False and \
        b_nc["B"]["poll"]["case"] == "iii" and b_nc["B"]["poll"]["unrounded_quotient_not_an_output"] == "128/125" and \
        b_nc["driver_outputs"]["MEM_POLL_S"] == "2"
    ev_half = evidence(runs=[run_of(297, growth=300 * MIB), run_of(316)])      # A: the clip, MEM_POLL_S = 1/2
    half = [_rro(ev=ev_half, official=_official([run_of(297, cap=cap, poll=0.5, growth=g),
                                                 run_of(316, cap=cap, poll=0.5)])) for g in (300 * MIB, 100 * MIB)]
    r["frozen_half_second_agrees_on_either_canonical_branch"] = all(
        h["pass"] is True and h["A"]["outputs"]["MEM_POLL_S"] == h["B"]["outputs"]["MEM_POLL_S"] == "1/2" ==
        h["driver_outputs"]["MEM_POLL_S"] for h in half) and \
        [h["B"]["poll"]["case"] for h in half] == ["ii", "i"]
    b_free = _rro(official=_official([run_of(297, cap=cap, drv=700 * MIB), run_of(316, cap=cap)]))
    r["B_free_mem_min_differs"] = only(b_free, "FREE_MEM_MIN_BYTES")
    host_busy = {"pid": 5, "comm": "/Applications/Planted.app/Contents/MacOS/Planted", "pcpu": "26.0",
                 "hosting_app": True}
    b_pct = _rro(official=_official(rds=readings(procs=[SIP_PROC, host_busy])))
    r["B_excl_cpu_pct_differs"] = b_pct["pass"] is False and \
        b_pct["comparison_by_output"]["EXCL_CPU_PCT"]["equal"] is False and b_pct["B"]["outputs"]["EXCL_CPU_PCT"] == 35
    other = {"pid": 78, "comm": "/usr/libexec/otherd", "pcpu": "31.0", "hosting_app": False}
    b_more = _rro(official=_official(rds=readings(procs=[SIP_PROC, other])))
    r["B_excl_allow_one_name_more"] = only(b_more, "EXCL_ALLOW") and \
        b_more["comparison_by_output"]["EXCL_ALLOW"]["only_in_B"] == ["otherd"]
    b_less = _rro(official=_official(rds=readings(procs=[])))
    r["B_excl_allow_one_name_fewer"] = only(b_less, "EXCL_ALLOW") and \
        b_less["comparison_by_output"]["EXCL_ALLOW"]["only_in_A"] == ["plantedd"]
    d0 = derive(evidence())
    wrong = RP.apply_constants(DRV, dict(d0["outputs"], EXCL_CPU_PCT=40))
    c_diff = _rro(frozen=wrong)
    r["driver_constant_is_not_A"] = c_diff["pass"] is False and \
        c_diff["comparison_by_output"]["EXCL_CPU_PCT"]["equal"] is False
    unatt = _rro(official=_official(rds=readings(free=GIB, procs=[SIP_PROC])))
    r["B_rule_check_fails"] = unatt["pass"] is False and unatt["B"]["checks"]["r_free_attainable"] is False and \
        all(v["equal"] for v in unatt["comparison_by_output"].values())
    ev1 = dict(CAP_EVENT, cap_bytes=cap, rss_bytes=cap + 1)
    failed = dict(DV.compact_run(decoy_record(297, None, cap=cap, failed="BrokenProcessPool", events=[ev1]),
                                 "decoy297", exit_code=1), job=dict(JOB_OK))
    dup = dict(run_of(297, cap=cap), id="decoy297_again")
    wds = {"full_record": _official([run_of(297, cap=cap, events=[{"worker_pid": 1}]), run_of(316, cap=cap)]),
           "failed_decoy_record": _official([failed, run_of(316, cap=cap)]),
           "with_a_clean_duplicate": _official([run_of(297, cap=cap, events=[ev1]), dup, run_of(316, cap=cap)]),
           "event_in_the_second_decoy": _official([run_of(297, cap=cap), run_of(316, cap=cap, events=[ev1])])}
    wd = {k: _rro(official=v) for k, v in wds.items()}
    r["watchdog_event_in_an_official_decoy"] = all(
        x["pass"] is False and x["memory_watchdog_event_in_an_official_decoy"] is True and
        x["status"] == RR.STATUS_OFFICIAL_WATCHDOG == "QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP" and
        x["fail_closed_statuses"] == [RR.STATUS_OFFICIAL_WATCHDOG] and
        x["B"]["rules"]["r_mem"]["status"] == RR.STATUS_OFFICIAL_WATCHDOG and
        x["B"]["rules"]["r_mem"]["rerun_required"] == [] and x["B"]["outputs"]["MEM_CAP_BYTES"] is None
        for x in wd.values())
    cases = {c["id"]: {"pass": True} for c in CFG["cases"]}
    agg = Q.aggregate(dict(cases, R_RULES_OFFICIAL=wd["full_record"]), CFG, "official")
    agg2 = Q.aggregate(dict(cases, R_RULES_OFFICIAL=b_nc), CFG, "official")
    forced = Q.aggregate(dict(cases, R_RULES_OFFICIAL=dict(wd["full_record"], **{"pass": True})), CFG, "official")
    r["the_qualification_fails_closed_with_the_status"] = agg["pass"] is False and \
        agg["fail_closed_statuses"] == [RR.STATUS_OFFICIAL_WATCHDOG] and agg2["pass"] is False and \
        agg2["fail_closed_statuses"] == [RR.STATUS_POLL_NONCANONICAL] and forced["pass"] is False and \
        Q.aggregate(cases, CFG, "official")["fail_closed_statuses"] == [] and \
        Q.aggregate(cases, CFG, "official")["pass"] is True
    slow = _rro(official=_official([run_of(297, cap=cap, spacing_ns=500_000_001), run_of(316, cap=cap)]))
    r["official_sampler_observed_spacing_above_half_a_second"] = slow["pass"] is False and \
        "SAMPLER_OBSERVED_SPACING_ABOVE_0.5_S" in slow["official_run_reasons"]["decoy297"] and \
        slow["B"]["outputs"]["MEM_CAP_BYTES"] is None and slow["fail_closed_statuses"] == []
    nl = _rro(official=_official([run_of(297, cap=cap, launched=False), run_of(316, cap=cap)]))
    r["official_decoy_not_under_launchd"] = nl["pass"] is False and \
        "NOT_UNDER_LAUNCHD_LAUNCHER" in nl["official_run_reasons"]["decoy297"]
    oc = _rro(official=_official([run_of(297), run_of(316, cap=cap)]))
    r["official_decoy_not_with_the_frozen_cap"] = oc["pass"] is False and \
        "MEASUREMENT_CAP_NOT_AS_RULED" in oc["official_run_reasons"]["decoy297"]
    sl = _rro(official=_official([run_of(297, cap=cap, host=clean_host(gap_s=30)), run_of(316, cap=cap)]))
    th = _rro(official=_official([run_of(297, cap=cap), run_of(316, cap=cap, host=dict(
        clean_host(), thermal_events=[{"type": "ThermalEvent"}]))]))
    r["official_decoy_slept_or_thermal_event"] = sl["pass"] is False and \
        any("HOST_PROVENANCE" in x for x in sl["official_run_reasons"]["decoy297"]) and th["pass"] is False and \
        "THERMAL_EVENT_DURING_RUN" in th["official_run_reasons"]["decoy316"]
    edited = copy.deepcopy(d0)
    edited["outputs"]["EXCL_CPU_PCT"] = 40
    he = _rro(derivation=edited, frozen=RP.apply_constants(DRV, d0["outputs"]))
    r["derivation_edited_by_hand"] = he["pass"] is False and he["derivation_committed_is_the_recomputation"] is False
    extra = RP.apply_constants(DRV, d0["outputs"]).replace("WORKERS = 5 ", "WORKERS = 5  ")
    od = _rro(frozen=extra)
    r["frozen_driver_changed_elsewhere"] = od["pass"] is False and \
        od["frozen_driver_is_measured_driver_with_the_five_outputs_applied"] is False and \
        all(v["equal"] for v in od["comparison_by_output"].values())
    om = _rro(measured=DRV + "\n# other bytes\n")
    r["measured_driver_is_not_the_evidence_driver"] = om["pass"] is False and \
        om["measured_driver_is_the_evidence_driver"] is False
    nd = _rro(ev=evidence(designated=False))
    r["evidence_not_designated"] = nd["pass"] is False and nd["A"]["designated"] is False
    none = Q.r_rules_official(evidence=None, evidence_sha256=None, derivation=None, official=_official(),
                              driver_src=DRV, measured_driver_src=None, cfg=CFG, base_names=base_names(), HOST=HOST)
    r["no_evidence_committed"] = none["pass"] is False
    one = _rro(official=_official([run_of(297, cap=cap)]))
    r["an_official_decoy_missing"] = one["pass"] is False
    return {"ok": all(r.values()), "rows": r}


def t_apply_step_in_a_sandbox():
    """The apply step end to end, through its CLI, in a SANDBOX of the base store (never the worktree): PLANTED
    designated evidence and its derivation are committed there; dry-run reports the change and writes nothing;
    --write changes exactly the driver's five constants, the protocol's table and DRIVER_DIFF.md, and `check` is clean
    afterwards. Refused, with nothing written: a derivation that is not designated; one whose rule check does not hold;
    one that stopped on MEM_POLL_S_NONCANONICAL_BRANCH or on STEP1_RERUN_REQUIRED; a hand-edited output (also one put
    in a non-canonical form); evidence other than the committed bytes; a driver that is not the measured bytes."""
    sb = T.Sandbox(fresh("apply"))
    ns = sb.root / T.NS_REL
    shutil.copytree(T.NSS / "config", ns / "config", dirs_exist_ok=True)
    shutil.copy2(T.NSS / "DRIVER_DIFF.md", ns / "DRIVER_DIFF.md")
    sb.commit([T.NS_REL + "/config", T.NS_REL + "/DRIVER_DIFF.md"], "sandbox: config and DRIVER_DIFF.md")
    tool = ns / "code" / "mbs308_repin.py"
    drv, proto, dd = ns / "code" / "mbs308_driver.py", ns / "protocol" / PROTO.name, ns / "DRIVER_DIFF.md"
    src0, proto0, dd0 = drv.read_text(), proto.read_text(), dd.read_bytes()
    evd = ns / "evidence_prefreeze"
    evd.mkdir()
    ev = evidence(runs=[run_of(297, growth=300 * MIB), run_of(316)], driver_sha=sha(src0.encode()),
                  commit=sb.freeze)                  # the canonical clip: MEM_POLL_S = 1/2

    def plant(e, mutate=None):
        raw = (json.dumps(e, indent=1, sort_keys=True) + "\n").encode()
        (evd / DV.EVIDENCE_NAME).write_bytes(raw)
        d = DV.derivation(e, evidence_sha256=sha(raw), base_names=base_names(), h3_readings=H3, plan=PLAN,
                          rules_sha256=sha((ns / "code/mbs308_rrules.py").read_bytes()),
                          tool_sha256=sha((ns / "code/mbs308_derive.py").read_bytes()))
        if mutate:
            mutate(d)
        (evd / DV.DERIVATION_NAME).write_text(json.dumps(d, indent=1, sort_keys=True) + "\n")
        return d

    def run(*extra):
        p = subprocess.run([T.PY, "-I", "-S", "-B", str(tool), "apply", "--derivation", str(evd / DV.DERIVATION_NAME),
                            "--ns", str(ns), "--repo", str(sb.root), *extra], capture_output=True, text=True,
                           env=T.GENV, stdin=subprocess.DEVNULL, timeout=300)
        try:
            return p.returncode, json.loads(p.stdout)
        except ValueError:
            return p.returncode, {"raw": (p.stdout + p.stderr)[-500:]}
    untouched = lambda: (drv.read_text(), proto.read_text(), dd.read_bytes()) == (src0, proto0, dd0)  # noqa: E731
    r = {}
    plant(evidence(designated=False, driver_sha=sha(src0.encode())))
    rc, out = run("--write")
    r["not_designated_refused"] = rc == 2 and "NOT_DESIGNATED" in out.get("detail", "") and untouched()
    plant(evidence(rds=readings(free=GIB, procs=[SIP_PROC]), driver_sha=sha(src0.encode())))
    rc, out = run("--write")
    r["rule_check_fails_refused"] = rc == 2 and "A_RULE_CHECK_DOES_NOT_HOLD" in out.get("detail", "") and untouched()
    plant(evidence(runs=[run_of(297, growth=100 * MIB), run_of(316)], driver_sha=sha(src0.encode()),
                   commit=sb.freeze))
    rc, out = run("--write")
    r["noncanonical_poll_branch_refused"] = rc == 2 and RR.STATUS_POLL_NONCANONICAL in out.get("detail", "") and \
        "STOP_BEFORE_FREEZE" in out.get("detail", "") and untouched()
    plant(evidence(runs=[run_of(297, events=[CAP_EVENT]), run_of(316)], driver_sha=sha(src0.encode()),
                   commit=sb.freeze))
    rc, out = run("--write")
    r["step1_rerun_required_refused"] = rc == 2 and RR.STATUS_STEP1_RERUN in out.get("detail", "") and untouched()
    plant(ev, mutate=lambda d: d["outputs"].__setitem__("EXCL_CPU_PCT", 50))
    rc, out = run("--write")
    r["hand_edited_output_refused"] = rc == 2 and "NOT_REPRODUCED_FROM_THE_EVIDENCE" in out.get("detail", "") and \
        untouched()
    plant(ev, mutate=lambda d: d["outputs"].__setitem__("MEM_POLL_S", "128/125"))
    rc, out = run("--write")
    r["hand_edited_noncanonical_output_refused"] = rc == 2 and "MEM_POLL_S_NOT_CANONICAL" in out.get("detail", "") \
        and untouched()
    plant(ev)
    (evd / DV.EVIDENCE_NAME).write_bytes((evd / DV.EVIDENCE_NAME).read_bytes() + b" ")
    rc, out = run("--write")
    r["other_evidence_bytes_refused"] = rc == 2 and "EVIDENCE_SHA256_DIFFERS" in out.get("detail", "") and untouched()
    plant(evidence(runs=[run_of(297, growth=300 * MIB), run_of(316)], driver_sha="1" * 64, commit=sb.freeze))
    rc, out = run("--write")
    r["not_the_measured_driver_refused"] = rc == 2 and out.get("refused") == "DRIVER_NOT_THE_MEASURED_BYTES" and \
        untouched()
    d = plant(ev)
    rc, out = run()
    r["dry_run_reports_and_writes_nothing"] = rc == 1 and out.get("stale") is True and out.get("written") is False \
        and out.get("driver_changes") is True and out.get("protocol_changes") is True and untouched()
    rc, out = run("--write")
    new = drv.read_text()
    a = {ast.get_source_segment(src0, n) for n in ast.parse(src0).body}
    b = {ast.get_source_segment(new, n) for n in ast.parse(new).body}
    got = DV.driver_outputs(new)
    r["write_applies_exactly_the_outputs"] = rc == 0 and out.get("written") is True and \
        all((F(got[k]) == F(d["outputs"][k])) if k == "MEM_POLL_S" else got[k] == d["outputs"][k]
            for k in DV.OUTPUTS) and len(a - b) == len(b - a) <= 5 and d["outputs"]["MEM_POLL_S"] == "1/2" and \
        got["MEM_CAP_BYTES"] == GIB and "plantedd" in got["EXCL_ALLOW"] and "MEM_POLL_S = 0.5\n" in new
    tab = RP.table_outputs(proto.read_text())
    i, j = proto0.index(RP.TABLE_BEGIN), proto0.index(RP.TABLE_END)
    r["protocol_table_only"] = proto.read_text()[:i] == proto0[:i] and proto.read_text().endswith(proto0[j:]) and \
        all(v.startswith("RULE OUTPUT A (designated derivation sha256 `") for v in tab["_status"].values()) and \
        tab["MEM_CAP_BYTES"] == got["MEM_CAP_BYTES"] and tab["EXCL_ALLOW"] == got["EXCL_ALLOW"]
    p = subprocess.run([T.PY, "-I", "-S", "-B", str(tool), "check", "--ns", str(ns)], capture_output=True, text=True,
                       env=T.GENV, stdin=subprocess.DEVNULL, timeout=300)
    r["repin_check_clean_after"] = p.returncode == 0 and dd.read_bytes() != dd0
    rc, out = run("--write")
    r["second_apply_is_a_no_op"] = rc == 0 and out.get("stale") is False and out.get("written") is False
    changed = set(T.g(sb.root, "status", "--porcelain", "--untracked-files=no").split()[1::2])
    r["only_three_tracked_files_changed"] = changed == {T.NS_REL + "/code/mbs308_driver.py",
                                                        T.NS_REL + "/protocol/" + PROTO.name,
                                                        T.NS_REL + "/DRIVER_DIFF.md"}
    return {"ok": all(r.values()), "rows": r}


# ------------------------------------------------------------------ the designated-measurement tool (B1)
PS_TEXT = ("    1     0   0.4 /sbin/launchd\n  300     1  30.5 /usr/libexec/somed\n"
           "  310     1  12.0 /Applications/Planted.app/Contents/MacOS/Planted\n"
           "  320     1  26.0 /Applications/Other.app/Contents/MacOS/Other\n  330     1   0.0 (kernel)\n"
           "  {SELF}   300  99.0 /usr/bin/python3\n  341 {SELF}  99.0 /bin/ps\n  garbage line\n")
VM_TEXT = ("Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free:      1000.\n"
           "Pages active:    1000.\nPages inactive:      2000.\nPages speculative:      10.\n"
           "Pages throttled:      0.\nPages wired down:      4321.\nPages purgeable:      5.\n")


def t_measure_readings_and_hosting_app():
    """One prepared-state reading from PLANTED vm_stat / ps / battery texts: the driver's own free_memory_bytes (its
    function text, executed), wired-down pages and page size, the power source, and exactly the processes the rules
    can use (above 25 %cpu, and every hosting-app process) with executable path and %cpu TEXT; this process and its
    children are excluded. The series takes n readings at least the ruled spacing apart. The hosting app is the
    bundle of the nearest ancestor inside an application bundle (READING-12); none found gives no path."""
    fmb = MEAS.driver_function(DRV, "free_memory_bytes", {"HOST": HOST})
    me = 4242
    rd = MEAS.reading(fmb, ["/Applications/Planted.app/"], texts={
        "vm_stat": VM_TEXT, "ps": PS_TEXT.replace("{SELF}", str(me)), "batt": "Now drawing from 'AC Power'\n",
        "thermal": "com.apple.system.thermalpressurelevel 0\n", "pressure": "1\n"}, self_pid=me)
    comms = {p["comm"].rsplit("/", 1)[-1]: p for p in rd["procs"]}
    r = {"free_memory_is_the_drivers": rd["free_memory_bytes"] == (1000 + 2000 + 10 + 5) * 16384,
         "wired_and_page": (rd["wired_pages"], rd["page_size_bytes"]) == (4321, 16384),
         "power_thermal_pressure": (rd["power"], rd["thermal_level"], rd["memory_pressure"]) == ("AC Power", 0, 1),
         "kept_processes": set(comms) == {"somed", "Planted", "Other"} and comms["somed"]["pcpu"] == "30.5" and
         comms["Planted"]["hosting_app"] is True and comms["Planted"]["pcpu"] == "12.0" and
         rd["own_process_tree_excluded"] == 2 and rd["processes_read"] == 7,
         "time_is_a_rational_text": F(rd["t_s"]) > 0}
    bad = MEAS.reading(fmb, [], texts={"vm_stat": "garbage", "ps": "", "batt": "", "thermal": "", "pressure": ""},
                       self_pid=me)
    r["unreadable_fields_named"] = MEAS.reading_reasons([bad]) != [] and MEAS.reading_reasons([rd]) == [] and \
        bad["free_memory_bytes"] is None and bad["procs"] is None
    clock = {"t": 0.0}
    seen = []

    def one():
        seen.append(clock["t"])
        return {"n": len(seen)}
    MEAS.take_readings(one, 4, 30, sleep=lambda s: clock.__setitem__("t", clock["t"] + s), clock=lambda: clock["t"])
    r["series_spacing_at_least_as_ruled"] = len(seen) == 4 and all(b - a >= 30 for a, b in zip(seen, seen[1:])) and \
        MEAS.READINGS_N == RR.READINGS_MIN == 10 and MEAS.READINGS_SPACING_S == RR.READING_SPACING_S == 30
    chain = {10: ("/bin/zsh", 9), 9: ("/Applications/Host.app/Contents/Frameworks/Helper.app/Contents/MacOS/Helper", 8),
             8: ("/Applications/Host.app/Contents/MacOS/Host", 1)}
    ha = MEAS.hosting_app(10, comm_of=lambda p: chain[p][0], ppid_of=lambda p: chain[p][1])
    none = MEAS.hosting_app(10, comm_of=lambda p: "/usr/sbin/sshd", ppid_of=lambda p: 1)
    r["hosting_app_reading_12"] = ha["paths"] == ["/Applications/Host.app/"] and len(ha["chain"]) == 3 and \
        none["paths"] == [] and MEAS.bundle_of("/Applications/A.app/Contents/MacOS/A") == "/Applications/A.app" and \
        MEAS.bundle_of("/usr/bin/python3") is None and MEAS.bundle_of("(kernel)") is None
    return {"ok": all(r.values()), "rows": r}


def t_measure_run_validity():
    """Why a run is not a valid input (MEAS.run_reasons, used by the designated measurement and by R_RULES_OFFICIAL):
    battery, a sleep on channel K, an unavailable power log, a ThermalEvent entry in the run (and an unreadable one),
    a memory-watchdog event (also in the dev form, and from the driver's failed-decoy record), a failed decoy, a
    sampler record whose OBSERVED spacing is above 0.5 s or not stated (exactly 0.5 s is valid), not under the launchd
    launcher, WORKERS, the ladder, a cap or poll other than ruled, the blocks not as planned, the job not launched /
    detached / finished, a missing record. A clean official run has no reason. The processes that make a host not
    prepared are reported by basename and path class only."""
    rr = lambda run, **k: MEAS.run_reasons(run, PLAN, cap=k.get("cap", 3 * GIB), poll=k.get("poll", F(2)))  # noqa
    has = lambda run, word, **k: any(word in x for x in rr(run, **k))  # noqa: E731
    r = {"clean": rr(run_of(297)) == [] and rr(run_of(316)) == [],
         "battery": has(run_of(297, host=clean_host(battery_at=3)), "HOST_PROVENANCE_CONTAMINATED"),
         "sleep_K": has(run_of(297, host=clean_host(gap_s=30)), "HOST_PROVENANCE_CONTAMINATED"),
         "power_log_unavailable": has(run_of(297, host=clean_host(events="unavailable")),
                                      "HOST_PROVENANCE_AMBIGUOUS"),
         "thermal_event": rr(run_of(297, host=dict(clean_host(), thermal_events=[{"type": "ThermalEvent"}]))) ==
         ["THERMAL_EVENT_DURING_RUN"],
         "thermal_events_unreadable": rr(run_of(297, host=dict(clean_host(), thermal_events=None))) ==
         ["THERMAL_EVENTS_UNREADABLE"],
         "watchdog_event": has(run_of(297, events=[{"worker_pid": 1}]), "MEMORY_WATCHDOG_EVENT") and
         "MEMORY_WATCHDOG_EVENT" in MEAS.run_reasons(run_of(297, events=[CAP_EVENT]), PLAN, cap=3 * GIB, poll=F(2),
                                                     official=False) and
         {"MEMORY_WATCHDOG_EVENT", "DECOY_FAILED", "RUN_EXIT_NOT_ZERO"} <= set(rr(dict(DV.compact_run(decoy_record(
             297, None, failed="BrokenProcessPool", events=[CAP_EVENT]), "decoy297", exit_code=1), job=JOB_OK))),
         "broken_pool_release_is_not_a_watchdog_event": rr(run_of(297, events=[
             {"event": RR.BROKEN_POOL_EVENT, "worker_pid": 1}])) == ["WORKER_KILLED_AFTER_A_BROKEN_POOL"],
         "sampler_observed_spacing": rr(run_of(297, spacing_ns=500_000_001)) ==
         ["SAMPLER_OBSERVED_SPACING_ABOVE_0.5_S"] and rr(run_of(297, spacing_ns=500_000_000)) == [] and
         MEAS.run_reasons(run_of(297, spacing_ns=600_000_000), PLAN, cap=3 * GIB, poll=F(2), official=False) ==
         ["SAMPLER_OBSERVED_SPACING_ABOVE_0.5_S"],
         "not_under_launchd": has(run_of(297, launched=False), "NOT_UNDER_LAUNCHD_LAUNCHER"),
         "workers": has(run_of(297, workers=4), "WORKERS_NOT_5"),
         "ladder": has(run_of(297, ladder="dev"), "NOT_THE_FROZEN_LADDER"),
         "cap_not_as_ruled": has(run_of(297, cap=GIB), "MEASUREMENT_CAP_NOT_AS_RULED") and
         rr(run_of(297, cap=GIB), cap=GIB) == [],
         "poll_not_as_ruled": has(run_of(297, poll=1.0), "MEM_POLL_S_NOT_2"),
         "blocks": has(dict(DV.compact_run(decoy_record(297, 2), "x", exit_code=0), job=JOB_OK),
                       "BLOCKS_NOT_AS_PLANNED"),
         "job_not_finished": has(run_of(297, job={"finished": True, "detached": True, "booted_out": False}),
                                 "JOB_NOT_LAUNCHED_DETACHED_AND_FINISHED"),
         "record_missing": rr({"id": "x", "record_missing": True}) == ["RECORD_MISSING"],
         "stored_assessment_contradicted": has(run_of(297, host=clean_host(gap_s=30, stored_status="CLEAN")),
                                               "HOST_PROVENANCE")}
    busy = [{"pid": 9, "comm": "/Applications/Busy.app/Contents/MacOS/Busy", "pcpu": "80.0", "hosting_app": False},
            {"pid": 8, "comm": "/private/var/x/oddd", "pcpu": "70.0", "hosting_app": False}, SIP_PROC]
    rules = DV.apply_rules(runs=[], readings=readings(procs=busy), hw_memsize_bytes=16 * GIB,
                           hosting_app_paths=HOSTING["paths"], base_names=base_names(), h3_readings=H3, plan=PLAN,
                           workers=5, mem_poll_s=F(2), measurement_cap_bytes=3 * GIB, measurement_poll_s=F(2))
    np_ = MEAS.not_prepared(rules)
    r["not_prepared_basename_and_path_class"] = np_ == [
        {"name": "Busy", "path_class": "NEVER_ADDED_PATH_CLASS /Applications/"},
        {"name": "oddd", "path_class": "NOT_UNDER_A_SIP_PROTECTED_OS_PATH"}] and \
        rules["r_excl_pct"]["EXCL_CPU_PCT"] == 25 and MEAS.not_prepared(DV.apply_rules(
            runs=[], readings=readings(procs=[SIP_PROC]), hw_memsize_bytes=16 * GIB,
            hosting_app_paths=HOSTING["paths"], base_names=base_names(), h3_readings=H3, plan=PLAN, workers=5,
            mem_poll_s=F(2), measurement_cap_bytes=3 * GIB, measurement_poll_s=F(2))) == []
    return {"ok": all(r.values()), "rows": r}


def _measure(tag: str, *, rds=None, spec=None, dev=True, plan=None, hrep="planted") -> dict:
    """MEAS.measure on PLANTED readings with the SYNTHETIC payload as the launched program (test label prefix; logs
    under the test log directory; every job booted out and its plist removed by the measurement code itself)."""
    import mbs308_launch as L
    work = fresh(tag)
    C = DV.driver_constants(DRV)                 # the cap and poll the driver under test carries (apply-robust)
    spec = dict({"cap": C["MEM_CAP_BYTES"], "poll": float(F(C["MEM_POLL_S"])), "ladder": "frozen", "sleep_s": 2.0},
                **(spec or {}))
    seq = iter(rds if rds is not None else readings(procs=[SIP_PROC]))
    plan = plan or PLAN

    def program_for(cell, out):
        fb = plan[cell]
        return [L.PYTHON, "-I", "-S", "-B", str(T.NSS / "tests" / "mbs308_decoy_payload.py"), str(CODE), str(out),
                str(cell), "all" if fb is None else str(fb), "5", json.dumps(spec)]
    ev = MEAS.measure(ns=T.NSS if CODE == T.NSS / "code" else CODE.parent, repo=T.REPO, work=work, L=L, plan=plan,
                      workers=5, dev=dev, base_names=base_names(), h3_readings=H3, one_reading=lambda: next(seq),
                      program_for=program_for, label_prefix="org.rebaseguard.mbs308.test.",
                      log_dir=Path.home() / "Library/Logs/ReBaseGuard/mbs308-test", pre={"commit": "planted"},
                      n_readings=10, spacing_s=0.0, hosting=HOSTING, sleep=lambda s: None,
                      host_report=planted_host_report() if hrep == "planted" else hrep)
    left = sorted(p.name for p in (work / "launch").glob("*.plist"))
    jobs = subprocess.run(["/bin/launchctl", "list"], capture_output=True, text=True).stdout
    labels = [(r.get("job") or {}).get("label") for r in ev["runs"]]
    return {"ev": ev, "plists_left": left, "jobs_left": [x for x in labels if x and x in jobs], "work": work}


def t_measure_synthetic_payload_under_launchd():
    """The measurement code path end to end with the SYNTHETIC payload (never the driver; no science): planted
    prepared-host readings, then one launchd job per planned decoy through the launcher's own `launch` (detached, the
    payload's own launchd check true), waited for, booted out, the plist removed; the compact evidence carries every
    rule input, the commit, the driver sha256, the boot UUID and the host provenance, and the rules derive from it.
    A planted run is NEVER designated: the record is labelled DEV, and without `dev` a planted input refuses."""
    m = _measure("measure_ok")
    ev = m["ev"]
    runs = {r["id"]: r for r in ev["runs"]}
    # the payload ran with the cap and poll the driver under test carries; as DESIGNATED evidence the runs are step 1's
    # (3 GiB, 2 s): planted here, so that the derivation of the record is checked whatever the driver carries
    as_step1 = [dict(x, rmem_run=dict(x["rmem_run"], mem_cap_bytes=3 * GIB, mem_poll_s=2.0)) for x in ev["runs"]]
    d = derive(dict(ev, designated=True, invalid_reasons=[], driver_sha256=sha(DRV.encode()), runs=as_step1))
    r = {"two_runs_one_at_a_time": list(runs) == ["decoy297", "decoy316"] and
         all(x["job"]["finished"] is True and x["job"]["detached"] is True and x["job"]["booted_out"] is True
             for x in runs.values()),
         "payload_ran_as_the_launchd_job": all(x["rmem_run"]["launched_by_launchd"] is True for x in runs.values()),
         "rule_inputs_recorded": all(isinstance(x["driver_maxrss_bytes"], int) and x["jobs"] and
                                     x["rss_sampler"]["interval_s"] == "0.25" and
                                     x["rss_sampler"]["max_spacing_ns"] == 300_000_000 and
                                     x["watchdog_events"] == [] and x["invalid_reasons"] == [] and
                                     isinstance(x["host"], dict) and x["raw_sha256"] for x in runs.values()),
         "evidence_fields": ev["schema"] == DV.EVIDENCE_SCHEMA and ev["driver_sha256"] == sha(DRV.encode()) and
         bool(ev["boot_uuid"]) and ev["hw_memsize_bytes"] and len(ev["readings"]) == 10 and
         ev["host"]["assessment"]["status"] and ev["target_evaluations"] == 0 and
         ev["configuration"]["one_run_at_a_time"] is True,
         "never_designated": ev["designated"] is False and ev["invalid_reasons"] == ["DEV_FORM_NEVER_DESIGNATED"] and
         ev["label"].startswith("DEV") and ev["step1_rerun"] is None and ev["prior_invalid_series"] == [],
         "nothing_left_behind": m["plists_left"] == [] and m["jobs_left"] == [],
         "rules_derive_from_it": d["status"] == "OK" and d["rules"]["r_mem"]["status"] == "OK" and
         d["outputs"]["MEM_CAP_BYTES"] == GIB and d["outputs"]["MEM_POLL_S"] == "2" and
         d["rules"]["r_mem"]["invalid_runs"] == []}
    try:                 # the same planted call WITHOUT dev (still the synthetic payload, whatever the code does)
        m2 = _measure("measure_refuse", dev=False)
        r["planted_input_without_dev_refused"] = False
        r["a_planted_run_was_marked_designated"] = m2["ev"].get("designated")
    except MEAS.MeasureRefusal as e:
        r["planted_input_without_dev_refused"] = e.code == "PLANTED_INPUT"
    shutil.rmtree(m["work"], ignore_errors=True)
    return {"ok": all(r.values()), "rows": r, "invalid_reasons": ev["invalid_reasons"]}


def t_measure_refuses_and_invalidates():
    """The measurement marks the evidence INVALID and stops as ruled: (a) a host that is not prepared (a process above
    the threshold that R-ALLOW can never admit): HOST_NOT_PREPARED, the process reported by basename and path class,
    NO decoy launched, no threshold raised; (b) a reading on battery: no decoy launched; (c) a memory-watchdog event
    in the first decoy: STEP1_RERUN_REQUIRED, the second decoy is NOT launched, and the report names the rule's one
    re-run cap (the provisional cap doubled) with the step-5 bound UNDEFINED (no valid run: the owner's open point);
    (c2) an event in the second decoy: the bound is computed from the first, valid, run's figures; nothing is re-run in
    either case; (d) a sampler record whose observed spacing is above 0.5 s invalidates the series; (e) the designated
    flag is false in every case. The CLI refuses outside the campaign's qualified worktree (the real driver is never
    launched from a copy or a sandbox), the preflight refuses a tree that is not the committed bytes (nothing run),
    and the proposed designation rule holds: once designated evidence exists the tool refuses (ALREADY_DESIGNATED,
    nothing measured), and an invalid series is kept under --work, never overwritten, and listed."""
    busy = {"pid": 9, "comm": "/Applications/Busy.app/Contents/MacOS/Busy", "pcpu": "80.0", "hosting_app": False}
    a = _measure("measure_np", rds=readings(procs=[busy]))["ev"]
    b = _measure("measure_batt", rds=readings(power="Battery Power", procs=[SIP_PROC]))["ev"]
    c = _measure("measure_wd", spec={"event": True})
    c2 = _measure("measure_wd2", spec={"event": True, "event_cells": [316]})
    e = _measure("measure_slow", spec={"spacing_ns": 600_000_000})["ev"]
    cap0 = DV.driver_constants(DRV)["MEM_CAP_BYTES"]
    s1, s2 = c["ev"]["step1_rerun"] or {}, c2["ev"]["step1_rerun"] or {}
    b1, b2 = s1.get("rerun_step5_bound") or {}, s2.get("rerun_step5_bound") or {}
    r = {"not_prepared": a["status"] == "HOST_NOT_PREPARED" and a["designated"] is False and a["runs"] == [] and
         a["host_not_prepared"] == [{"name": "Busy", "path_class": "NEVER_ADDED_PATH_CLASS /Applications/"}] and
         "HOST_NOT_PREPARED" in a["invalid_reasons"],
         "battery_reading": b["designated"] is False and b["runs"] == [] and "READING_NOT_ON_AC" in
         b["invalid_reasons"],
         "watchdog_event_stops": c["ev"]["status"] == "STEP1_RERUN_REQUIRED" and c["ev"]["designated"] is False and
         [x["id"] for x in c["ev"]["runs"]] == ["decoy297"] and
         "decoy297:STEP1_RERUN_REQUIRED" in c["ev"]["invalid_reasons"] and c["plists_left"] == [] and
         c["jobs_left"] == [],
         "step1_report_bound_undefined_without_a_valid_run": s1.get("status") == RR.STATUS_STEP1_RERUN and
         s1.get("event_runs") == ["decoy297"] and b1.get("rerun_cap_bytes") == 2 * cap0 and
         b1.get("defined") is False and b1.get("open_point") == RR.OPEN_RERUN_BOUND and
         s1.get("rerun_required") == [{"id": "decoy297", "cell": 297, "rerun_cap_bytes": 2 * cap0}] and
         s1.get("facility", "").startswith("NONE"),
         "step1_report_bound_from_the_valid_run": c2["ev"]["status"] == "STEP1_RERUN_REQUIRED" and
         [x["id"] for x in c2["ev"]["runs"]] == ["decoy297", "decoy316"] and s2.get("event_runs") == ["decoy316"] and
         b2.get("defined") is True and b2.get("P_bytes") == 102 * MIB and b2.get("D_bytes") == 60 * MIB and
         b2.get("lhs_bytes") == 2 * cap0 + 4 * 102 * MIB + 60 * MIB and
         b2.get("within") is (b2.get("lhs_bytes") <= b2.get("rhs_bytes")) and c2["plists_left"] == [] and
         c2["jobs_left"] == [],
         "sampler_spacing_invalidates_the_series": e["designated"] is False and e["status"] == "MEASURED" and
         {"decoy297:SAMPLER_OBSERVED_SPACING_ABOVE_0.5_S", "decoy316:SAMPLER_OBSERVED_SPACING_ABOVE_0.5_S"} <=
         set(e["invalid_reasons"]) and e["step1_rerun"] is None}
    repo = fresh("measure_cli") / "repo"
    ns = repo / T.NS_REL
    shutil.copytree(CODE, ns / "code", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(T.NSS / "config", ns / "config")
    g = lambda *args: subprocess.run(["/usr/bin/git", "-C", str(repo), "-c", "user.name=t", "-c",  # noqa: E731
                                      "user.email=t@invalid", "-c", "commit.gpgsign=false", *args], capture_output=True,
                                     text=True, env=dict(T.GENV, HOME=str(repo)))
    g("init", "-q")
    g("add", "-A")
    g("commit", "-q", "-m", "planted")
    clean_pre = MEAS.preflight(ns, repo, repo.parent / "work")
    (ns / "code" / "planted_untracked.py").write_text("X = 1\n")
    pre = MEAS.preflight(ns, repo, repo.parent / "work")
    r["preflight_refuses_a_tree_that_is_not_the_committed_bytes"] = \
        "NAMESPACE_NOT_THE_COMMITTED_BYTES" in pre["refusals"] and \
        "NAMESPACE_NOT_THE_COMMITTED_BYTES" not in clean_pre["refusals"]
    ident = MEAS.identity_reasons(repo, DRV)
    branch = g("symbolic-ref", "-q", "HEAD").stdout.strip()
    gd = g("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip()
    own = DRV
    for name, val in (("QUALIFIED_WORKTREE", str(repo.resolve())), ("QUALIFIED_GIT_DIR", str(Path(gd).resolve())),
                      ("QUALIFIED_COMMON_DIR", str(Path(gd).resolve())), ("QUALIFIED_BRANCH", branch)):
        own = set_line(own, name, json.dumps(val))
    r["identity_is_the_qualified_worktree_and_branch"] = ident == ["NOT_THE_QUALIFIED_WORKTREE",
                                                                   "NOT_THE_QUALIFIED_BRANCH"] and \
        MEAS.identity_reasons(repo, own) == [] and \
        MEAS.identity_reasons(repo, set_line(own, "QUALIFIED_BRANCH", '"refs/heads/other"')) == \
        ["NOT_THE_QUALIFIED_BRANCH"]
    # designate (both forms) in the mini repository, which is not the qualified worktree: refused before anything is
    # measured. The measuring function is replaced by a recorder, so nothing can be launched whatever the code does.
    measured, real_measure = [], MEAS.measure
    MEAS.measure = lambda **k: measured.append(k.get("dev")) or {
        "designated": False, "status": "RECORDER", "invalid_reasons": ["RECORDER"], "host_not_prepared": [],
        "step1_rerun": None, "prior_invalid_series": MEAS.prior_invalid(k["work"])}
    try:
        for form, dev in (("designate", False), ("designate_dev", True)):
            try:
                rc, summary = MEAS.designate(repo.parent / "work", dev=dev, ns=ns, repo=repo)
            except (MEAS.MeasureRefusal, DV.DeriveRefusal) as e:      # any other stop is not the identity refusal
                rc, summary = None, {"other_refusal": getattr(e, "code", str(e))}
            r[f"{form}_refuses_outside_the_qualified_worktree"] = rc == 2 and summary.get("nothing_run") is True and \
                summary.get("refused") == ["NOT_THE_QUALIFIED_WORKTREE", "NOT_THE_QUALIFIED_BRANCH"]
    finally:
        MEAS.measure = real_measure
    r["nothing_measured_outside_the_qualified_worktree"] = measured == [] and \
        not (ns / "evidence_prefreeze").exists() and not (repo.parent / "work").exists()
    # the proposed designation rule, with the identity gate, the preflight and the pinned 39 names stubbed and the
    # measuring function still the recorder (nothing can be launched): an invalid series is kept and listed, never
    # overwritten; once designated evidence exists the tool refuses and measures nothing
    real = (MEAS.identity_reasons, MEAS.preflight, DV.base_names_of)
    MEAS.identity_reasons = lambda *a, **k: []
    MEAS.preflight = lambda *a, **k: {"refusals": [], "commit": "planted"}
    DV.base_names_of = lambda cfg, rp: base_names()
    MEAS.measure = lambda **k: measured.append("recorder") or {
        "designated": False, "status": "RECORDER", "invalid_reasons": ["RECORDER"], "host_not_prepared": [],
        "step1_rerun": None, "prior_invalid_series": MEAS.prior_invalid(k["work"])}
    wk, od = repo.parent / "work_rule", repo.parent / "designated_out"
    try:
        rc1, s_1 = MEAS.designate(wk, ns=ns, repo=repo, out_dir=od)
        rc2, s_2 = MEAS.designate(wk, ns=ns, repo=repo, out_dir=od)
        kept = sorted(f.name for f in wk.glob("INVALID_*"))
        prior = MEAS.prior_invalid(wk)
        od.mkdir()
        (od / DV.EVIDENCE_NAME).write_text("{}\n")
        n_before = len(measured)
        rc3, s_3 = MEAS.designate(wk, ns=ns, repo=repo, out_dir=od)
        r["designation_rule_invalid_series_kept_and_listed"] = (rc1, rc2) == (3, 3) and len(kept) == 2 and \
            kept[0].startswith("INVALID_001_") and kept[1].startswith("INVALID_002_") and \
            (s_1["prior_invalid_series"], s_2["prior_invalid_series"]) == (0, 1) and \
            [x["status"] for x in prior] == ["RECORDER", "RECORDER"] and all(len(x["sha256"]) == 64 for x in prior)
        r["designation_rule_already_designated_refuses"] = rc3 == 2 and s_3 == {
            "refused": ["ALREADY_DESIGNATED"], "nothing_run": True} and len(measured) == n_before and \
            sorted(f.name for f in wk.glob("INVALID_*")) == kept
    except (MEAS.MeasureRefusal, DV.DeriveRefusal, OSError):
        r["designation_rule_invalid_series_kept_and_listed"] = False
        r["designation_rule_already_designated_refuses"] = False
    finally:
        MEAS.identity_reasons, MEAS.preflight, DV.base_names_of = real
        MEAS.measure = real_measure
    p2 = subprocess.run([T.PY, "-I", "-S", "-B", str(ns / "code" / "mbs308_measure.py"), "designate", "--work",
                         str(repo / "x")], capture_output=True, text=True, env=T.GENV, stdin=subprocess.DEVNULL,
                        timeout=120)
    r["cli_refuses_work_inside_the_repository"] = p2.returncode == 2 and "WORK_INSIDE_THE_REPOSITORY" in p2.stdout \
        and not (repo / "x").exists()
    for d in ("measure_np", "measure_batt", "measure_wd", "measure_wd2", "measure_slow"):
        shutil.rmtree(TMP / d, ignore_errors=True)
    return {"ok": all(r.values()), "rows": r}


SCIENCE_GATE_CHILD = r'''
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import mbs308_qualify as Q
calls = []
def stub(name, ret):
    def f(*a, **k):
        calls.append(name)
        return ret
    return f
class Done:
    returncode = 0
    def wait(self):
        return 0
# every function through which the verifier would EXECUTE science is replaced by a recorder: whatever the code under
# test decides, this child launches nothing
Q.official_decoy = stub("official_decoy", {"record_missing": True, "cell": 0})
Q.official_readings = stub("official_readings", {"readings": [], "hosting_app": {"paths": []},
                                                 "hw_memsize_bytes": None})
Q.run_qc01 = stub("run_qc01", {"pass": False})
Q.science_inprocess = stub("science_inprocess", {})
Q.spawn_child = stub("spawn_child", Done())
Q.dev_decoy = stub("dev_decoy", 1)
cfg = Q.load_config()
sel = [c["id"] for c in cfg["cases"]]
work = Path(sys.argv[2])
work.mkdir(parents=True, exist_ok=True)
out = {}
for mode, heavy in (("official", True), ("review", True), ("review", False)):
    r = Q.science_phase(sel, mode, heavy, cfg, work, work, work)
    out[mode + (":heavy" if heavy else "")] = {k: [v.get("status"), v.get("pass")] for k, v in r["cases"].items()}
print(json.dumps({"qualified": Q.qualified_worktree(), "calls": calls, "cases": out}))
'''


def t_official_science_only_in_the_qualified_worktree():
    """The verifier EXECUTES real science (the official decoys under launchd, MB r1's children, the rehearsal on cell
    305's committed record, the in-process cases) only in the campaign's qualified worktree. In a sandbox of the base
    store (not the qualified worktree), an official run, a review --heavy run and a plain review run execute NOTHING:
    every executing function is replaced by a recorder in a child process, and none is called; the executing cases
    fail closed (NOT_THE_QUALIFIED_WORKTREE); a plain review still re-evaluates the committed records (absent here:
    they fail); Q1_theory (hashes) runs."""
    sys.path.insert(0, str(T.NSS / "tests"))
    import test_mbs308_qualify as TQ
    sb = TQ.sparse_sandbox("science_gate")
    p = subprocess.run([T.PY, "-I", "-S", "-B", "-c", SCIENCE_GATE_CHILD, str(sb["dst"] / "code"),
                        str(sb["tmp"] / "work")], capture_output=True, text=True, env=T.GENV, cwd=str(sb["root"]),
                       stdin=subprocess.DEVNULL, timeout=600)
    try:
        rep = json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"ok": False, "tail": (p.stdout + p.stderr)[-800:]}
    nq = ["NOT_THE_QUALIFIED_WORKTREE", False]
    executing = ("QC01", "QC05", "QC06", "QC07", "QC09-SCI")
    decoy = ("QC02", "QC03", "QC04", "QC08", "MBR1_REPRO", "Q12_caps", "R_RULES_OFFICIAL")
    c = rep["cases"]
    r = {"sandbox_is_not_the_qualified_worktree": rep["qualified"] is False,
         "nothing_executed": rep["calls"] == [],
         "official_fails_closed": all(c["official:heavy"].get(k) == nq for k in executing + decoy),
         "review_heavy_fails_closed": all(c["review:heavy"].get(k) == nq for k in executing + decoy),
         "plain_review_executes_nothing_and_re_evaluates_records": all(c["review"].get(k) == nq for k in executing)
         and all(c["review"].get(k, [0, 0])[1] is False and c["review"][k][0] != "NOT_THE_QUALIFIED_WORKTREE"
                 for k in decoy),
         "q1_theory_runs": c["official:heavy"].get("Q1_theory") == [None, True]}
    shutil.rmtree(sb["tmp"], ignore_errors=True)
    return {"ok": all(r.values()), "rows": r, "calls": rep["calls"]}


# ------------------------------------------------------------------ the owner records: config, protocol, manifest
def t_owner_records_named_and_bound():
    """A1 / C1: the three owner records are named by path, commit, byte length and sha256, identically, in the driver
    (S1_OWNER_RECORDS), the configuration (`owner_decisions`, and QC13-S's governance records) and the protocol
    (section 1), and those are the bytes git holds at the research commits (read from the base store); the manifest
    writer binds them and refuses other bytes; the configuration records the user's options as the records state them."""
    rows_drv = [tuple(x) for x in T.s1_owner_records()]
    cfg_rows = [(x["record"], x["path"], x["commit"], x["bytes"], x["sha256"]) for x in
                CFG["owner_decisions"]["records"]]
    gov = {g["id"]: g for g in CFG["governance_records"]}
    gov_rows = [(x["record"], gov[x["id"]]["path"], gov[x["id"]]["commit"], x["bytes"], gov[x["id"]]["sha256"])
                for x in CFG["owner_decisions"]["records"]]
    real = []
    for name, path, commit, _n, _d in rows_drv:
        raw = T.owner_record_text(commit, path).encode()
        real.append((name, path, commit, len(raw), sha(raw)))
    proto = PROTO.read_text()
    s1 = proto.split("\n## 1.", 1)[1].split("\n## 2.", 1)[0]
    in_proto = all(f"| `{n}` | `{p}` | `{c}` | {b} | `{d}` |" in s1 for n, p, c, b, d in rows_drv)
    mf = MF.owner_records(T.base_store(), rows_drv)
    mf_refuses = mf_refuses_len = len(rows_drv) == 3
    for i in range(len(rows_drv)):                       # each record in turn: another digest, another length
        for kind, bad in (("sha", rows_drv[i][:4] + ("0" * 64,)),
                          ("len", rows_drv[i][:3] + (rows_drv[i][3] - 1, rows_drv[i][4]))):
            try:
                MF.owner_records(T.base_store(), rows_drv[:i] + [bad] + rows_drv[i + 1:])
                refused = False
            except MF.ManifestRefusal:
                refused = True
            mf_refuses = mf_refuses and (refused or kind != "sha")
            mf_refuses_len = mf_refuses_len and (refused or kind != "len")
    t0, t1, t2 = owner_text(0), owner_text(1), owner_text(2)
    od = CFG["owner_decisions"]
    options = od["MBS-6"]["option"] == od["MBS-7"]["option"] == od["MBS-8"]["option"] == "(i)" and \
        od["SECTION-11.2"]["option"] == "(a)" and "MBS-6 = OPTION (i): FINAL" in t0 and \
        "MBS-7 = OPTION (i): KEEP MB-S SCIENCE UNCHANGED" in t0 and "MBS-8 = OPTION (i): MB r1 r3 CAPS" in t0 and \
        "§11.2 OPTION (a)" in t1 and "THE COMPLETE ORIGINAL OWNER-DECISION RECORD" in t1 and \
        "QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP" in t2 and "MEM_POLL_S_NONCANONICAL_BRANCH" in t2 and \
        "OWNER SUPPLEMENT 2" in t2
    decided = [c["id"] for c in CFG["cases"] if c.get("decided_by")]
    ok = rows_drv == cfg_rows == gov_rows == real and \
        [r[0] for r in rows_drv] == ["original", "supplement_1", "supplement_2"] and len(mf) == 3 and \
        in_proto and [m["git_blob"] for m in mf] and mf_refuses and mf_refuses_len and options and \
        set(decided) == {"QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08", "Q1_theory", "QC09-SCI",
                         "MBR1_REPRO", "Q12_caps", "R_RULES_OFFICIAL"} and \
        all(c["status"] == "BUILT" for c in CFG["cases"])
    return {"ok": ok, "driver_config_git_agree": rows_drv == cfg_rows == gov_rows == real, "in_protocol": in_proto,
            "manifest_refuses_other_bytes": mf_refuses and mf_refuses_len, "options": options}


def t_qc13s_owner_records_fail_closed():
    """QC13-S names the three owner records and checks them against the REAL research branch (the base store): each is
    OK as named. Planted controls through the same check: an ALTERED record (another sha256) is SHA_MISMATCH; a record
    whose path is missing at its commit is MISSING; a record not named (no commit) is PENDING_RECORD; a record not on
    the research branch is NOT_ON_REF; each keeps QC13-S failing. The implementation review accepting the frozen build
    is still un-named, so QC13-S still fails closed today."""
    bs = T.base_store()
    show = lambda c, p: Q.git_show_bytes(c, p, repo=bs)  # noqa: E731
    anc = lambda c, ref: Q.git_rc("merge-base", "--is-ancestor", c, ref, repo=bs) == 0  # noqa: E731
    gov = {g["id"]: g for g in CFG["governance_records"]}
    ids = ("USER_FREEZE_DECISION", "USER_OWNER_SUPPLEMENT_1", "USER_OWNER_SUPPLEMENT_2")
    real = {i: Q.check_record(gov[i], show=show, is_ancestor=anc) for i in ids}
    plant = lambda i, **k: Q.check_record(dict(gov[i], **k), show=show, is_ancestor=anc)  # noqa: E731
    r = {"all_three_ok_as_named": len(real) == 3 and all(v["status"] == "OK" and v["pass"] is True
                                                           for v in real.values()) and
         all(gov[i].get("sha256") and gov[i].get("commit") for i in ids)}
    for i in ids:
        r[f"{i}:altered"] = plant(i, sha256="0" * 64)["status"] == "SHA_MISMATCH"
        r[f"{i}:missing"] = plant(i, path=gov[i]["path"] + ".absent")["status"] == "MISSING"
        r[f"{i}:not_named"] = plant(i, commit=None)["status"] == "PENDING_RECORD"
        r[f"{i}:not_on_ref"] = plant(i, ref="refs/heads/main")["status"] == "NOT_ON_REF"
    okr = {"id": "A", "status": "OK", "pass": True}
    P = {"pass": True}
    for name, rec in (("altered", plant(ids[0], sha256="0" * 64)), ("missing", plant(ids[1], path="x/absent")),
                      ("not_named", plant(ids[1], commit=None)), ("supplement_2_altered", plant(ids[2], sha256="0" * 64)),
                      ("supplement_2_not_named", plant(ids[2], commit=None))):
        r[f"qc13_fails_closed_on_{name}"] = Q.qc13_core(P, P, P, [okr, rec])["pass"] is False
    r["qc13_passes_only_when_every_record_holds"] = Q.qc13_core(P, P, P, [okr] + [real[i] for i in ids])[
        "pass"] is True
    pend = [g["id"] for g in CFG["governance_records"] if not g.get("commit")]
    r["implementation_review_still_un_named"] = pend == ["IMPLEMENTATION_REVIEW_ACCEPTED"]
    r["ledger_agents"] = {"builder6", "reviewQ6", "ratifier2"} <= set(CFG["ledger"]["agents"])
    return {"ok": all(r.values()), "rows": r}


def t_protocol_owner_decisions_text():
    """The protocol states the user's decisions: MBS-6 (i) finality in section 10 (and the superseded "further
    successor" wording is gone), the MBS-8 (i) values in section 8, section 11.2 as the ruling (option (a), the
    supplement cited by path / commit / sha256, the chain, one freeze, no tolerance; no open question left), the S1
    index of the three owner records in section 1, the readings as ruled (READING-6 corrected, READING-7 the
    ratifier's) and the builder's own (READING-11 to READING-15), the three fail-closed statuses of owner supplement 2
    with its citation, and the designation rule as a flagged PROPOSAL."""
    p = PROTO.read_text()
    norm = lambda s: " ".join(s.split())  # noqa: E731
    s10 = norm(p.split("\n## 10.", 1)[1].split("\n## 11.", 1)[0])
    s8 = norm(p.split("\n## 8.", 1)[1].split("\n## 9.", 1)[0])
    s112 = norm(p.split("\n### 11.2", 1)[1].split("\n### 11.3", 1)[0])
    s113 = norm(p.split("\n### 11.3", 1)[1].split("\n## 12.", 1)[0])
    s1 = norm(p.split("\n## 1.", 1)[1].split("\n## 2.", 1)[0])
    sup, sup2 = T.s1_owner_records()[1], T.s1_owner_records()[2]
    r = {"mbs6_final": "An INDETERMINATE-class outcome of MB-S is final for route MB on cell 308" in s10 and
         "no further route-MB cell-308 evaluation is authorized after such an outcome" in s10 and
         "MBS-6 = option (i)" in s10 and "FINAL for route MB on cell 308" in s10,
         "s7_further_successor_wording_gone": "any further successor needs" not in norm(p),
         "mbs7_reach": "not a permanent prohibition on separately governed future scientific work" in s10,
         "mbs8_values": all(x in s8 for x in ("MBS-8 = option (i)", "8 h = 28 800 s per attempt",
                                              "CLOCK_UPTIME_RAW", "1800 / 4200 / 8700 s", "1800 / 1800 / 2700 s",
                                              "C1b 1800 s", "VER 1800 s", "PRE_CAP = 1800 s", "WORKERS = 5",
                                              "never derives, proposes or records a candidate cap")),
         "section_11_2_is_the_ruling": "option (a)" in s112 and sup[1].rsplit("/", 1)[-1] in s112 and
         sup[2] in s112 and sup[4] in s112 and "There is ONE freeze" in s112 and "no tolerance anywhere" in s112 and
         "B == A == the constant the frozen driver carries" in s112 and "ACTUAL FROZEN VALUES" in s112 and
         "STEP1_RERUN_REQUIRED" in s112 and all(f"{i}. **" in s112 for i in range(1, 8)) and
         "open sequencing question" not in norm(p) and "Options (b)" in s112,
         "readings_listed": all(f"READING-{i}" in s113 for i in (6, 7, 11, 12, 13, 14, 15)) and
         "READING-6 (CORRECTED" in s113 and "READING-7 (CONFIRMED" in s113 and
         "READING-8" not in p and "READING-9" not in p and "READING-10" not in p,
         "supplement_2_rulings": sup2[1].rsplit("/", 1)[-1] in s112 and sup2[2] in s112 and sup2[4] in s112 and
         all(x in s112 for x in (RR.STATUS_OFFICIAL_WATCHDOG, RR.STATUS_POLL_NONCANONICAL, RR.STATUS_STEP1_RERUN,
                                 "OBSERVED spacing", "0.25 s", "ca66e367")) and
         "no cap-override facility" in s112 and "PROPOSAL" in s112 and "ALREADY_DESIGNATED" in s112,
         "s1_index": "all three complete owner records" in s1 and "index_sha256" in s1 and "S1_OWNER_RECORDS" in s1
         and "supplement_2" in s1}
    return {"ok": all(r.values()), "rows": r}


def t_final_preflight_owner_section14():
    """C2: every item of the user's final host preflight (owner decisions section 14, read from the record itself) is
    mapped, in the record's order and wording, to the existing gate or recorded reading that covers it; every gate or
    function the mapping names exists in the driver / host / state source; the two items no accepted text makes a gate
    (the lid / sleep state, restart hazards) are read-only recorded readings with an operator line; the host report
    carries the mapping and reads the scheduled power events by type only; the protocol states the table."""
    text = owner_text(0)
    sec = text.split("14. FINAL HOST PREFLIGHT", 1)[1].split("15. EXECUTION AUTHORIZATION", 1)[0]
    items = [ln[2:].rstrip(";.").strip() for ln in sec.splitlines() if ln.startswith("- ")]
    mapped = [x[0] for x in Q.OWNER_SECTION14]
    src = DRV + (CODE / "mbs308_host.py").read_text() + STATE_SRC
    names_ok = {x[0]: all(n in src for n in x[3]) and bool(x[3]) for x in Q.OWNER_SECTION14}
    kinds = {x[0]: x[1] for x in Q.OWNER_SECTION14}
    ops = {x[0]: x[5] for x in Q.OWNER_SECTION14}
    report_items = {"automatic_os_installation_disabled", "automatic_restart", "ac_power", "sleep_prevention_and_lid",
                    "thermal_level_0", "lowpowermode_0", "disk_execution", "disk_qualification",
                    "memory_pressure_normal", "free_memory", "boot_identity", "host_identity_platform_pins",
                    "host_exclusive", "no_other_campaign_job"}
    items_ok = all(set(x[4]) <= report_items for x in Q.OWNER_SECTION14)
    sched = Q._pmset_sched("Scheduled power events:\n [0]  wake at 10/01/2026 23:28:25 by 'x'\n"
                           " [1]  restart at 10/02/2026 08:58:51 by 'y'\nRepeating power events:\n"
                           "  wakepoweron at 9:00AM every day\n")
    quiet = Q._pmset_sched("Scheduled power events:\n [0]  wake at 10/01/2026 23:28:25 by 'x'\n")
    p = PROTO.read_text()
    s83 = p.split("\n### 8.3", 1)[1].split("\n## 9.", 1)[0] if "\n### 8.3" in p else ""
    ok = len(items) == 17 and mapped == items and all(names_ok.values()) and items_ok and \
        kinds["required lid/sleep state"] == kinds["restart hazards controlled"] == "RECORDED_READING" and \
        bool(ops["required lid/sleep state"]) and bool(ops["restart hazards controlled"]) and \
        all(v in ("GATE", "MECHANISM", "RECORDED_READING") for v in kinds.values()) and \
        sched["event_types"] == ["restart", "wake", "wakepoweron"] and \
        sched["restart_shutdown_or_sleep_scheduled"] is True and quiet["restart_shutdown_or_sleep_scheduled"] is False \
        and [x["item"] for x in Q.owner_section14()] == items and all(f"| {i} |" in s83 for i in items)
    return {"ok": ok, "items": len(items), "order_and_wording": mapped == items,
            "names_missing": [k for k, v in names_ok.items() if not v]}


def t_declared_cases_all_built_and_pending_fails_closed():
    """Every configured case is BUILT (the decision-dependent ones name the owner record that decided them); the
    PENDING mechanism still fails closed: a PLANTED pending case returns pass false / PENDING_USER_DECISION / its
    dependencies, keeps its gate and the qualification failing, and must be declared consistently on both sides."""
    cons = Q.config_consistency(CFG)
    saved = dict(Q.PENDING_CASES)
    try:
        Q.PENDING_CASES["QC99"] = ("MBS-99",)
        cfg2 = json.loads(json.dumps(CFG))
        cfg2["cases"].append({"id": "QC99", "gates": ["Q8"], "status": Q.PENDING_STATUS, "depends_on": ["MBS-99"]})
        pend = Q.pending("QC99")
        cases = {c["id"]: ({"pass": True} if c["id"] != "QC99" else pend) for c in cfg2["cases"]}
        agg = Q.aggregate(cases, cfg2, "official")
        cons2 = Q.config_consistency(cfg2)
        cfg3 = json.loads(json.dumps(cfg2))
        cfg3["cases"][-1]["depends_on"] = ["OTHER"]
        cons3 = Q.config_consistency(cfg3)
    finally:
        Q.PENDING_CASES.clear()
        Q.PENDING_CASES.update(saved)
    all_pass = Q.aggregate({c["id"]: {"pass": True} for c in CFG["cases"]}, CFG, "official")
    ok = cons["pass"] is True and Q.PENDING_CASES == {} and len(CFG["cases"]) == len(Q.BUILT_CASES) == 28 and \
        pend == {"pass": False, "status": "PENDING_USER_DECISION", "depends_on": ["MBS-99"], "case": "QC99"} and \
        agg["pass"] is False and agg["gates"]["Q8"]["pass"] is False and agg["pending_user_decision"] == ["QC99"] and \
        cons2["pass"] is True and cons3["pass"] is False and cons3["depends_on_mismatch"] == ["QC99"] and \
        all_pass["pass"] is True and "QS-CASES" in Q.SUITE_CASES and \
        CFG["suites"]["QS-CASES"] == "tests/test_mbs308_cases.py"
    return {"ok": ok, "cases": len(CFG["cases"])}


# ====================================================================== brief 56 follow-up (builder7): the embedded host report
def t_host_report_structure_check():
    """Follow-up item 1 (reviewQ6 section 5, note (e)): the structure check of the EMBEDDED read-only host report
    (mbs308_derive.host_report_reasons). A report with the verifier's structure passes whatever its statuses say (the
    report is a record, not a gate: every item NOT_READY passes, every item READY passes); no report, a report that
    could not be taken, another schema, one not read-only, a missing, duplicated or unknown item, an item without a
    known status or without how it is checked, no time and no (or another) reference to where the operator's actions
    are recorded each fail with their reason. That reference is the research ledger the configuration names (QC13-S's
    ledger: same ref and path), written with the research logger. The verifier's OWN report -- taken read-only in a
    fresh process in a sparse sandbox, through the measurement tool's host_report_of -- passes the check and carries
    the reference; its code builds exactly the checklist items the check requires; protocol 8.1 names the place."""
    ok = planted_host_report()
    items = ok["items"]
    r = {"planted_report_passes": DV.host_report_reasons(ok) == [],
         "statuses_are_not_judged": DV.host_report_reasons(planted_host_report(
             items=[dict(i, status="READY") for i in items], ready=True)) == [] and
         DV.host_report_reasons(planted_host_report(items=[dict(i, status="UNKNOWN") for i in items])) == []}
    bad = {"none": (None, ["HOST_REPORT_NOT_EMBEDDED"]), "not_an_object": ("report", ["HOST_REPORT_NOT_EMBEDDED"]),
           "other_schema": (planted_host_report(schema="x"), ["HOST_REPORT_SCHEMA"]),
           "not_read_only": (planted_host_report(read_only=False), ["HOST_REPORT_NOT_READ_ONLY"]),
           "changes_made": (planted_host_report(changes_made=True), ["HOST_REPORT_NOT_READ_ONLY"]),
           "item_missing": (planted_host_report(items=items[1:]), ["HOST_REPORT_ITEMS"]),
           "item_twice": (planted_host_report(items=items[1:] + [items[1]]), ["HOST_REPORT_ITEMS"]),
           "item_unknown": (planted_host_report(items=items + [dict(items[0], item="other")]), ["HOST_REPORT_ITEMS"]),
           "items_not_a_list": (planted_host_report(items={"a": 1}), ["HOST_REPORT_ITEMS"]),
           "item_not_an_object": (planted_host_report(items=items[:-1] + ["free_memory"]), ["HOST_REPORT_ITEMS"]),
           "unknown_status": (planted_host_report(items=[dict(items[0], status="FINE")] + items[1:]),
                              ["HOST_REPORT_ITEM_STATUS"]),
           "no_checked_by": (planted_host_report(items=[dict(items[0], checked_by="")] + items[1:]),
                             ["HOST_REPORT_ITEM_STATUS"]),
           "no_time": (planted_host_report(utc=None), ["HOST_REPORT_TIME"]),
           "no_reference": ({k: v for k, v in ok.items() if k != "operator_actions"},
                            ["OPERATOR_ACTIONS_NOT_REFERENCED"]),
           "another_place": (planted_host_report(operator_actions=dict(DV.OPERATOR_ACTIONS, recorded_in="notes.txt")),
                             ["OPERATOR_ACTIONS_NOT_REFERENCED"])}
    for k, (rep, want) in bad.items():
        r[k] = DV.host_report_reasons(rep) == want
    saved = Q.host_report

    def boom(work=None):
        raise RuntimeError("planted: the report cannot be taken")
    Q.host_report = boom
    try:
        failed = Q.host_report_record(None)
    finally:
        Q.host_report = saved
    r["a_report_that_could_not_be_taken_is_recorded_and_fails"] = "RuntimeError" in str(failed.get("error")) and \
        "HOST_REPORT_SCHEMA" in DV.host_report_reasons(failed) and "HOST_REPORT_ITEMS" in DV.host_report_reasons(failed)
    oa = DV.OPERATOR_ACTIONS
    r["the_place_is_the_research_ledger_of_the_configuration"] = oa["recorded_in"] == CFG["ledger"]["path"] and \
        oa["ref"] == CFG["ledger"]["ref"] and oa["written_with"].endswith("code/c308_quarantine.py log_event") and \
        "user's statement and its time" in oa["line"] and len(oa["actions"]) == 4
    fn = [x for x in ast.parse((CODE / "mbs308_qualify.py").read_text()).body
          if isinstance(x, ast.FunctionDef) and x.name == "host_report"]
    built = [c.args[0].value for c in ast.walk(fn[0]) if isinstance(c, ast.Call) and
             getattr(c.func, "id", None) == "item" and c.args and isinstance(c.args[0], ast.Constant)] if fn else []
    r["the_verifier_builds_exactly_these_items"] = sorted(built) == sorted(DV.HOST_REPORT_ITEMS) and \
        len(built) == len(DV.HOST_REPORT_ITEMS) == 14 and Q.HOST_REPORT_STATUSES == DV.HOST_REPORT_STATUSES
    p = PROTO.read_text()
    s81 = p.split("\n### 8.1", 1)[1].split("\n### 8.2", 1)[0] if "\n### 8.1" in p else ""
    r["protocol_8_1_names_the_place"] = "ledger/TARGET_INTEGRITY_LEDGER.jsonl" in s81 and "log_event" in s81 and \
        "operator_actions" in s81 and "host_report" in s81 and "the user's statement and its time" in s81
    sys.path.insert(0, str(T.NSS / "tests"))
    import test_mbs308_qualify as TQ
    sb = TQ.sparse_sandbox("host_report_embedded")
    work = sb["tmp"] / "work"
    work.mkdir()
    real = MEAS.host_report_of(sb["dst"], work, sb["root"])
    r["the_verifiers_own_report_passes"] = isinstance(real, dict) and DV.host_report_reasons(real) == [] and \
        real.get("operator_actions") == DV.OPERATOR_ACTIONS and real.get("read_only") is True and \
        len(list(work.glob("MBS308_HOST_REPORT_*.json"))) == 1
    shutil.rmtree(sb["tmp"], ignore_errors=True)
    return {"ok": all(r.values()), "rows": r, "real_report_reasons": DV.host_report_reasons(real)}


def t_records_without_the_host_report_fail():
    """Follow-up item 1: a record WITHOUT the embedded host report fails its case's structure check. Designated
    evidence without it (or with a malformed one) is not evidence: the derivation is NOT_DERIVED and names the reason,
    and R_RULES_OFFICIAL fails on it; the official rule-input record without it fails R_RULES_OFFICIAL
    (`official_host_report_reasons`); with both reports the case passes (control), whatever the reports' statuses.
    The measurement embeds the report it is given, as given, and a measurement without one is invalid
    (HOST_REPORT_NOT_EMBEDDED among its reasons). The verifier's rule-input record carries the report it is given."""
    def without(d: dict) -> dict:
        return {k: v for k, v in d.items() if k != "host_report"}
    good = _rro()
    ev_none, ev_bad = without(evidence()), dict(evidence(), host_report=planted_host_report(read_only=False))
    d_none, d_bad, d_ok = derive(ev_none), derive(ev_bad), derive(evidence())
    a_none = _rro(ev=ev_none)
    o_none = _rro(official=without(_official()))
    o_bad = _rro(official=dict(_official(), host_report=planted_host_report(items=[])))
    o_err = _rro(official=dict(_official(), host_report={"error": "planted", "read_only": True, "changes_made": False}))
    ready = planted_host_report(items=[dict(i, status="READY") for i in planted_host_report()["items"]], ready=True)
    o_ready = _rro(ev=dict(evidence(), host_report=ready), official=dict(_official(), host_report=ready))
    r = {"control_passes": good["pass"] is True and good["official_host_report_reasons"] == [] and
         good["A"]["evidence_reasons"] == [] and d_ok["status"] == "OK",
         "statuses_do_not_matter": o_ready["pass"] is True,
         "evidence_without_it_is_not_derived": d_none["status"] == "NOT_DERIVED" and d_none["designated"] is False and
         d_none["evidence_reasons"] == ["HOST_REPORT_NOT_EMBEDDED"] and
         all(v is None for v in d_none["outputs"].values()) and d_none["stop_before_freeze"] is True,
         "evidence_with_a_malformed_one_is_not_derived": d_bad["status"] == "NOT_DERIVED" and
         d_bad["evidence_reasons"] == ["HOST_REPORT_NOT_READ_ONLY"],
         "r_rules_official_fails_on_such_evidence": a_none["pass"] is False and
         a_none["A"]["evidence_reasons"] == ["HOST_REPORT_NOT_EMBEDDED"] and a_none["A"]["status"] == "NOT_DERIVED",
         "official_record_without_it_fails": o_none["pass"] is False and
         o_none["official_host_report_reasons"] == ["HOST_REPORT_NOT_EMBEDDED"] and
         o_none["status"] == "NOT_IN_AGREEMENT" and all(v["equal"] for v in o_none["comparison_by_output"].values()),
         "official_record_with_a_malformed_one_fails": o_bad["pass"] is False and
         o_bad["official_host_report_reasons"] == ["HOST_REPORT_ITEMS"] and o_err["pass"] is False and
         "HOST_REPORT_SCHEMA" in o_err["official_host_report_reasons"]}
    hr = planted_host_report(utc="planted for the measurement")
    m_ok = _measure("measure_hr", hrep=hr)
    m_none = _measure("measure_no_hr", hrep=None)
    r["measurement_embeds_the_report_as_given"] = m_ok["ev"]["host_report"] == hr and \
        m_ok["ev"]["invalid_reasons"] == ["DEV_FORM_NEVER_DESIGNATED"]
    r["measurement_without_it_is_invalid"] = m_none["ev"]["host_report"] is None and \
        m_none["ev"]["designated"] is False and \
        m_none["ev"]["invalid_reasons"] == ["DEV_FORM_NEVER_DESIGNATED", "HOST_REPORT_NOT_EMBEDDED"]
    r["nothing_left_behind"] = m_ok["plists_left"] == m_none["plists_left"] == [] and \
        m_ok["jobs_left"] == m_none["jobs_left"] == []
    oi = Q.official_inputs({"readings": [1], "hosting_app": HOSTING, "hw_memsize_bytes": 2, "utc": "planted"},
                           [{"id": "decoy297"}], hr)
    r["rule_input_record_carries_the_report"] = oi["host_report"] == hr and oi["runs"] == [{"id": "decoy297"}] and \
        oi["readings"] == [1] and oi["target_evaluations"] == 0 and DV.host_report_reasons(oi["host_report"]) == []
    for m in (m_ok, m_none):
        shutil.rmtree(m["work"], ignore_errors=True)
    return {"ok": all(r.values()), "rows": r}


SCIENCE_PHASE_CHILD = r'''
import json, os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import mbs308_qualify as Q
import mbs308_measure as MEAS
calls = []
PLANT = Path(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else None
REPORT = {"planted_host_report": True, "utc": "planted"}
class Done:
    returncode = 0
    def wait(self):
        return 0
def refuse(name):
    def f(*a, **k):
        calls.append("REAL:" + name)
        raise RuntimeError("a real science path was reached: " + name)
    return f
def decoy(event, cell, first_blocks, out, work):          # a RECORDER in the place of the official decoy
    calls.append("official_decoy_gated:%d" % cell)
    if PLANT is not None and cell == 297:                 # the free-space reading FALLS while the first decoy runs
        PLANT.write_text("1\n")
    return {"id": "decoy%d" % cell, "cell": cell, "job": {"finished": True}, "exit": 0, "watchdog_events": []}
def readings():
    calls.append("official_readings")
    return {"readings": [], "hosting_app": {"paths": []}, "hw_memsize_bytes": None, "utc": "planted"}
def report(work=None):
    calls.append("host_report")
    return dict(REPORT)
def dev_decoy(out, driver_path=None):
    calls.append("dev_decoy")
    return 1
# this child plants "this IS the qualified worktree"; EVERY function through which the verifier would execute science
# is replaced by a recorder, and the real launch paths below them by functions that refuse: nothing is ever launched
Q.qualified_worktree = lambda: True
Q.official_decoy_gated = decoy
Q.official_decoy = refuse("official_decoy")
MEAS.run_decoy = refuse("run_decoy")
MEAS.run_under_launchd = refuse("run_under_launchd")
Q.official_readings = readings
Q.host_report = report
Q.dev_decoy = dev_decoy
Q.run_qc01 = refuse("run_qc01")
Q.science_inprocess = refuse("science_inprocess")
Q.spawn_child = refuse("spawn_child")
cfg = Q.load_config()
base = Path(sys.argv[2])
out = {}
def run(tag, sel, mode, heavy, host_rep=None):
    d = base / tag
    d.mkdir(parents=True)
    del calls[:]
    start = Q.disk_check(d, "verifier start")
    r = Q.science_phase(sel, mode, heavy, cfg, d, d, d, host_rep)
    rin = d / Q.OUTS["rinputs"]
    out[tag] = {"start_pass": start["pass"], "calls": list(calls),
                "cases": {k: {x: v.get(x) for x in ("pass", "status", "refused_before")} for k, v in r["cases"].items()},
                "checks": [[c["phase"], c["pass"]] for c in r["disk"]["checks"]],
                "refusal": (r["disk"]["refusal"] or {}).get("phase"), "returned_host_report": r.get("host_report"),
                "inputs_record": json.loads(rin.read_text()) if rin.is_file() else None}
'''
EMBED_RUNS = r'''
run("official", ["QC08"], "official", True, {"planted_host_report": "the official run's own"})
run("review_heavy", ["QC08"], "review", True)
(base / "review").mkdir()
(base / "review" / Q.OUTS["rinputs"]).write_text(json.dumps({"host_report": {"planted_host_report": "committed"}}))
d = base / "review"
r = Q.science_phase(["QC08"], "review", False, cfg, d, d, d)
out["review"] = {"returned_host_report": r.get("host_report")}
Q.host_report = refuse("host_report")
run("report_fails", ["QC08"], "review", True)
print(json.dumps(out))
'''


def t_official_run_embeds_the_host_report():
    """Follow-up item 1, the verifier's wiring (a child process in a sparse sandbox in which "this is the qualified
    worktree" is PLANTED and every function that would execute science is a recorder; nothing is launched): an
    official run writes the report it took at its start into its rule-input record and returns it for the
    qualification record; a review --heavy run takes its own, before the readings and before any decoy; a plain
    review returns the report its committed record embeds; a report that cannot be taken is recorded as such (the
    structure check then fails) and the run goes on."""
    sys.path.insert(0, str(T.NSS / "tests"))
    import test_mbs308_qualify as TQ
    sb = TQ.sparse_sandbox("embed_wiring")
    p = subprocess.run([T.PY, "-I", "-S", "-B", "-c", SCIENCE_PHASE_CHILD + EMBED_RUNS, str(sb["dst"] / "code"),
                        str(sb["tmp"] / "runs"), ""], capture_output=True, text=True, env=T.GENV, cwd=str(sb["root"]),
                       stdin=subprocess.DEVNULL, timeout=600)
    try:
        rep = json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"ok": False, "tail": (p.stdout + p.stderr)[-800:]}
    own = {"planted_host_report": "the official run's own"}
    o, h, f = rep["official"], rep["review_heavy"], rep["report_fails"]
    r = {"official_embeds_its_own_report": (o["inputs_record"] or {}).get("host_report") == own and
         o["returned_host_report"] == own and "host_report" not in o["calls"] and
         o["calls"] == ["official_readings", "official_decoy_gated:297", "official_decoy_gated:316"] and
         [x["id"] for x in o["inputs_record"]["runs"]] == ["decoy297", "decoy316"] and
         o["inputs_record"]["target_evaluations"] == 0,
         "review_heavy_takes_it_first": h["calls"][:2] == ["host_report", "official_readings"] and
         (h["inputs_record"] or {}).get("host_report") == {"planted_host_report": True, "utc": "planted"} and
         h["returned_host_report"] == h["inputs_record"]["host_report"],
         "plain_review_returns_the_committed_one": rep["review"]["returned_host_report"] ==
         {"planted_host_report": "committed"},
         "a_report_that_cannot_be_taken_is_recorded": "RuntimeError" in str(
             ((f["inputs_record"] or {}).get("host_report") or {}).get("error")) and
         DV.host_report_reasons(f["inputs_record"]["host_report"]) != [] and
         f["calls"][-2:] == ["official_decoy_gated:297", "official_decoy_gated:316"],
         "no_real_science_path_reached": not any(c.startswith("REAL:") and c != "REAL:host_report"
                                                 for x in (o, h, f) for c in x["calls"])}
    shutil.rmtree(sb["tmp"], ignore_errors=True)
    return {"ok": p.returncode == 0 and all(r.values()), "rows": r,
            "calls": {k: v.get("calls") for k, v in rep.items()}}


if __name__ == "__main__":
    T.cli(globals())
