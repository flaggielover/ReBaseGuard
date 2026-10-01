"""Cell-308 MB-S successor campaign (r1) -- the four written rules R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW of
CONSTANTS_RATIFICATION_MBS308 (research 3c2a7854, section "Written rules"; protocol draft section 8), as PURE functions.

Built by the non-holder builder4 (research brief 46). Target-free; NOT frozen. Nothing here reads the host, a file, git
or any record: every input is passed in, and every number of the rules below is the ratification's (none is chosen
here). The functions compute the rule outputs and record every input; they decide nothing about sequencing. Which
records feed them is the user's section-11.2 ruling, option (a) (owner supplement 1, part I; protocol section 11.2):
the designated pre-freeze measurements give the outputs the frozen code carries (code/mbs308_derive.py), and the
official qualification re-measures and re-applies these same functions (case R_RULES_OFFICIAL). The one parameter that
ruling adds is the cap / poll the measured runs must have been made with (r_mem's `measurement_cap_bytes`,
`measurement_poll_s`; non-holder builder6, research brief 54); no rule text and no number changed.

Readings of the rule text that the text leaves open are stated where they are made (READING-1 ... READING-5) and listed
in protocol section 11; each is a reading, not a new rule. The second ratifier's rulings on them
(CONSTANTS_RATIFICATION_MBS308_READINGS_R1, research ca66e367) and the owner's supplement 2 (research 74f386a5:
`ledger/USER_RULING_MBS308_OWNER_SUPPLEMENT_2.txt`) are implemented in r_mem and named in its docstring; the three
fail-closed statuses they give are the STATUS_* names below.

Arithmetic is exact (fractions.Fraction); a ps %cpu reading is converted from its decimal text, never through a float.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction as F

RATIFICATION_COMMIT = "3c2a78544899c5772ea95b7b228b1059f056e3fd"
RATIFICATION_REL = "level4/closure_proofs/p5y_k5_cell308_research/governance/CONSTANTS_RATIFICATION_MBS308.md"

MIB, GIB = 1024 ** 2, 1024 ** 3
# ---- every number below is the ratification's (section "Written rules"; the step it comes from is named)
ROUND_STEP_BYTES = 256 * MIB          # "roundup_256MiB" (R-MEM step 4, R-FREE)
MEM_FLOOR_BYTES = 1 * GIB             # R-MEM step 4: max(k x P, 1 GiB)
K_MIN = 3                             # R-MEM step 4: k = max(3, 2s)
K_SPREAD_FACTOR = 2                   # R-MEM step 4: 2s
MEASUREMENT_CAP_BYTES = 3 * GIB       # R-MEM step 1: each official decoy runs with the provisional cap (3 GiB)
MEASUREMENT_POLL_S = F(2)             # R-MEM step 1: ... and MEM_POLL_S 2 s
MEASUREMENT_WORKERS = 5               # R-MEM step 1: WORKERS 5
RERUN_CAP_FACTOR = 2                  # R-MEM step 1: re-run "with the provisional cap doubled"
POLL_FRACTION = F(1, 10)              # R-MEM step 6: g x MEM_POLL_S <= 0.1 x MEM_CAP
POLL_MIN_S = F(1, 2)                  # R-MEM step 6: MEM_POLL_S = max(0.5 s, 0.1 x MEM_CAP / g)
SAMPLER_MAX_INTERVAL_S = F(1, 2)      # R-MEM step 6: "a <= 0.5 s qualification sampler"
FREE_FLOOR_BYTES = 2 * GIB            # R-FREE: max(2 GiB, ...)
READINGS_MIN = 10                     # R-FREE attainability and R-ALLOW (a): >= 10 readings
READING_SPACING_S = 30                # ... 30 s apart
CONSECUTIVE_MIN = 3                   # R-FREE: at least 3 consecutive readings must reach FREE_MEM_MIN
EXCL_BASE_PCT = 25                    # R-EXCL-PCT: EXCL_CPU_PCT = 25
EXCL_CEILING_PCT = 50                 # R-EXCL-PCT: min(50, ...)
EXCL_FACTOR = F(5, 4)                 # R-EXCL-PCT: 1.25 x its maximum reading
EXCL_ROUND_STEP = 5                   # R-EXCL-PCT: roundup_5
SIP_PREFIXES = ("/System/", "/usr/libexec/", "/usr/sbin/", "/sbin/", "/Library/Apple/")        # R-ALLOW (b)
NEVER_PREFIXES = ("/Applications/", "/Users/", "/opt/", "/usr/local/", "/Library/Frameworks/", "/usr/bin/",
                  "/bin/")                                                                    # R-ALLOW "Never added"
AC = "AC Power"                       # prepared state: AC power (R-FREE attainability), as mbs308_host reads it
RULE_NUMBERS = {k: v for k, v in dict(globals()).items() if k.isupper() and not k.startswith("RATIFICATION")}
NS_PER_S = 10 ** 9                    # a unit conversion (the sampler records its observed spacing in nanoseconds)
READINGS_R1_COMMIT = "ca66e367"
SUPPLEMENT_2_COMMIT = "74f386a54088a210a51bb81587225dae64def637"
# ---- the three fail-closed statuses (mechanically detectable; none resolves anything, each stops)
# owner supplement 2, sections 2 and 7 / readings R1, item 5 (a): a DESIGNATED pre-freeze run with a memory-watchdog
# event is not a valid input; the rule's one re-run (the provisional cap doubled, within the step-5 bound) is the only
# cure; no further doubling, no re-run limit, nothing inferred. No cap-override facility exists: stop and report.
STATUS_STEP1_RERUN = "STEP1_RERUN_REQUIRED"
# owner supplement 2, sections 2 and 3 / readings R1, item 6, case (iii): step 6's otherwise-branch above the 0.5 s
# floor gives an unrounded quotient for which the accepted text defines no canonical form. Designated series: STOP
# BEFORE FREEZE. Official series: the qualification FAILS CLOSED. Nothing is rounded; no comparison value is made.
STATUS_POLL_NONCANONICAL = "MEM_POLL_S_NONCANONICAL_BRANCH"
# owner supplement 2, sections 1 and 6: ANY memory-watchdog event in an official-qualification decoy under the actual
# frozen MEM_CAP fails the qualification closed: no doubling, no qualification-only cap, no cure by another clean run.
STATUS_OFFICIAL_WATCHDOG = "QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP"
# the one point the accepted texts still leave to the OWNER (readings R1, item 5 (a) (i)); reported, never resolved
OPEN_RERUN_BOUND = ("OWNER_OPEN_POINT: which P and D stand in the step-5 bound for a re-run when no other valid run "
                    "exists (readings R1, item 5 (a))")
BROKEN_POOL_EVENT = "broken_pool_worker_killed"     # mbs308_state._MemWatch's release of an already-broken pool

_PY = re.compile(r"^[Pp]ython[0-9.]*$")


# ------------------------------------------------------------------ helpers
def roundup(x, step: int) -> int:
    """The smallest multiple of `step` that is >= x (exact)."""
    x = F(x)
    return math.ceil(x / step) * step


def roundup_256mib(x) -> int:
    return roundup(x, ROUND_STEP_BYTES)


def pct(x) -> F:
    """A ps %cpu reading, exactly: from its decimal text (str), an int or a Fraction; never through a float."""
    if isinstance(x, bool) or isinstance(x, float):
        raise TypeError("a %cpu reading must be its decimal text, an int or a Fraction (floats are refused)")
    return F(x) if not isinstance(x, str) else F(x.strip())


def fstr(x) -> str:
    x = F(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def under(path, prefix: str) -> bool:
    """`path` (an executable path, or a directory as the ratification states some H3 locations) lies under the
    directory `prefix` (which ends with '/')."""
    return isinstance(path, str) and (path.rstrip("/") + "/").startswith(prefix)


def basename(comm: str) -> str:
    """The name `busy_processes` compares: comm.rsplit('/')[-1] (R-ALLOW)."""
    return comm.rsplit("/", 1)[-1]


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def cap_events(events) -> list:
    """The MEMORY-WATCHDOG EVENTS of a run's watchdog record (READING-15, builder6): every entry except the watchdog's
    release of an already-broken pool (`event == "broken_pool_worker_killed"`: a kill made because the pool broke, not
    because a worker passed the cap). Anything else in the list -- a kill at the cap, or an entry this function does
    not know -- counts as an event (fail closed)."""
    return [e for e in events or [] if not (isinstance(e, dict) and e.get("event") == BROKEN_POOL_EVENT)]


def sampler_reasons(s) -> list:
    """Why ONE sampler record {interval_s, max_spacing_ns, max_growth_bytes_per_s} is not a valid step-6 input
    (readings R1, item 2; owner supplement 2, section 5): the bound "<= 0.5 s" binds the OBSERVED spacing of the
    readings (exactly 0.5 s is within it); a set interval <= 0.5 s is necessary and not sufficient; a record that does
    not state its largest observed spacing is invalid."""
    if not isinstance(s, dict):
        return ["SAMPLER_MISSING"]
    try:
        iv, g = F(str(s["interval_s"])), F(str(s["max_growth_bytes_per_s"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return ["SAMPLER_MISSING"]
    if iv <= 0 or g < 0:
        return ["SAMPLER_MALFORMED"]
    if iv > SAMPLER_MAX_INTERVAL_S:
        return ["SAMPLER_INTERVAL_ABOVE_0.5_S"]
    gap = s.get("max_spacing_ns")
    if not _is_int(gap) or gap <= 0:
        return ["SAMPLER_OBSERVED_SPACING_UNRECORDED"]
    if F(gap, NS_PER_S) > SAMPLER_MAX_INTERVAL_S:
        return ["SAMPLER_OBSERVED_SPACING_ABOVE_0.5_S"]
    return []


# ------------------------------------------------------------------ prepared-state readings (R-FREE, R-EXCL-PCT,
# R-ALLOW)
def readings_valid(readings) -> dict:
    """The prepared-state series: >= 10 readings, 30 s apart (every consecutive gap >= 30 s on the recorded monotonic
    time `t_s`), every reading on AC power (READING-1: a reading not on AC is not a prepared-state reading)."""
    reasons = []
    if not isinstance(readings, list) or len(readings) < READINGS_MIN:
        reasons.append(f"FEWER_THAN_{READINGS_MIN}_READINGS")
        readings = readings if isinstance(readings, list) else []
    ts = [r.get("t_s") for r in readings if isinstance(r, dict)]
    if len(ts) != len(readings) or any(isinstance(t, bool) or not isinstance(t, (int, float, str)) for t in ts):
        reasons.append("READING_WITHOUT_TIME")
    else:
        tf = [F(str(t)) if isinstance(t, float) else F(t) for t in ts]
        if any(b - a < READING_SPACING_S for a, b in zip(tf, tf[1:])):
            reasons.append(f"READINGS_LESS_THAN_{READING_SPACING_S}_S_APART")
    if any(not isinstance(r, dict) or r.get("power") != AC for r in readings):
        reasons.append("READING_NOT_ON_AC")
    return {"valid": not reasons, "reasons": reasons, "n": len(readings)}


# ------------------------------------------------------------------ R-MEM
def _run_reasons(run: dict, cap: int = MEASUREMENT_CAP_BYTES, poll=MEASUREMENT_POLL_S, official: bool = False) -> list:
    """R-MEM step 1: an OFFICIAL decoy run (the real driver's decoy under the launchd launcher, frozen ladder, WORKERS
    5, provisional cap 3 GiB or -- for a re-run -- that cap doubled, MEM_POLL_S 2 s) without any memory-watchdog
    event. `cap` / `poll`: the memory cap and poll the runs must have been made with. The defaults are step 1's own
    (the designated pre-freeze measurement runs). The user's section-11.2 ruling (owner supplement 1, section 3: "Official
    qualification decoys use the ACTUAL FROZEN VALUES. Do NOT introduce a separate 3-GiB / 2-second measurement
    configuration") makes them, for the official qualification's re-measurement, the constants the frozen driver
    carries: the caller passes those. No number of the rule changes. `official`: the run belongs to the official
    series, where no re-run exists (owner supplement 2, section 1: no doubling, no qualification-only cap)."""
    r = []
    if run.get("launcher") is not True:
        r.append("NOT_UNDER_LAUNCHD_LAUNCHER")
    if run.get("ladder") != "frozen":
        r.append("NOT_THE_FROZEN_LADDER")
    if run.get("workers") != MEASUREMENT_WORKERS:
        r.append("WORKERS_NOT_5")
    if official and run.get("rerun_of") is not None:
        r.append("RERUN_NOT_PERMITTED_AFTER_THE_FREEZE")
    want_cap = cap * (RERUN_CAP_FACTOR if run.get("rerun_of") is not None and not official else 1)
    if run.get("mem_cap_bytes") != want_cap:
        r.append("MEASUREMENT_CAP_NOT_AS_RULED")
    try:
        poll_ok = F(str(run.get("mem_poll_s"))) == F(poll)
    except (TypeError, ValueError, ZeroDivisionError):
        poll_ok = False
    if not poll_ok:
        r.append("MEM_POLL_S_NOT_2" if F(poll) == MEASUREMENT_POLL_S else "MEM_POLL_S_NOT_AS_RULED")
    ev = run.get("watchdog_events")
    if not isinstance(ev, list):
        r.append("WATCHDOG_EVENTS_UNRECORDED")
    elif cap_events(ev):
        r.append("MEMORY_WATCHDOG_EVENT")
    elif ev:                               # the pool broke for another reason: the run failed, it is not an event run
        r.append("WORKER_KILLED_AFTER_A_BROKEN_POOL")
    jobs = run.get("jobs")
    if not isinstance(jobs, list) or not jobs or any(
            not isinstance(j, dict) or not _is_int(j.get("job_maxrss_bytes")) or j.get("kind") is None or
            j.get("rung") is None for j in jobs):
        r.append("JOB_PEAKS_UNRECORDED")
    if not _is_int(run.get("driver_maxrss_bytes")):
        r.append("DRIVER_PEAK_UNRECORDED")
    wp = run.get("worker_peak_rss_bytes")
    if wp is not None and not _is_int(wp):
        r.append("WORKER_PEAK_MALFORMED")
    return r


def _job_peak(j: dict) -> int:
    """Step 2, per job: max(job_maxrss_bytes [ru_maxrss of the job's fresh worker], worker_peak_rss_bytes [watchdog ps])
    where the watchdog's reading is attributed to the job (READING-2: the driver's record carries the watchdog's peak
    per RUN, not per job; a per-job ps peak is used when a record carries one)."""
    w = j.get("worker_peak_rss_bytes")
    return max(j["job_maxrss_bytes"], w if _is_int(w) else 0)


def r_mem(runs: list, *, required_cells, workers: int, mem_poll_s, host: dict, sampler: dict,
          measurement_cap_bytes: int = MEASUREMENT_CAP_BYTES, measurement_poll_s=MEASUREMENT_POLL_S,
          official: bool = False) -> dict:
    """R-MEM. `runs`: [{id, cell, launcher, ladder, workers, mem_cap_bytes, mem_poll_s, rerun_of, watchdog_events,
    driver_maxrss_bytes, worker_peak_rss_bytes, jobs: [{name, kind, rung, job_maxrss_bytes[, worker_peak_rss_bytes]}]}];
    `required_cells`: the decoy cells of the qualification plan; `workers`, `mem_poll_s`: the driver's WORKERS and
    MEM_POLL_S; `host`: {hw_memsize_bytes, wired_pages, page_size_bytes} of the prepared idle state; `sampler`:
    {interval_s, max_spacing_ns, max_growth_bytes_per_s} of the <= 0.5 s qualification sampler (its SET interval, the
    largest spacing OBSERVED between two of its readings, in integer nanoseconds, and the highest growth rate);
    `measurement_cap_bytes`, `measurement_poll_s`: the cap and poll the runs must have been made with (see
    _run_reasons; default: step 1's 3 GiB and 2 s); `official`: the series is the official qualification's (after
    the freeze), not the designated pre-freeze series.

    Readings ruled by the second ratifier (CONSTANTS_RATIFICATION_MBS308_READINGS_R1, research ca66e367; no rule text
    and no number changed):
    * item 2 (READING-6, corrected): step 6's "<= 0.5 s" binds the OBSERVED spacing of the sampler's readings; a set
      interval <= 0.5 s is necessary and not sufficient; exactly 0.5 s is within the bound; a record whose largest
      observed spacing exceeds it (or does not state it) is an invalid input: no g, no MEM_POLL_S, R-MEM not OK.
    * item 4 (F-6, corrected): a run with a memory-watchdog event -- an original decoy or a re-run -- is cured ONLY by
      a VALID re-run of it at the doubled provisional cap (every re-run has that one cap); coverage of its cell by
      another clean run cures nothing. While any event run has no valid re-run no rule is applied and the status is
      RERUN_REQUIRED: never OK, never INCOMPLETE_INPUT, never NO_VALID_INPUT.
    * item 5 (a): "within the step-5 bound" is a condition on the doubled cap, with the valid runs' P and D; which P
      and D stand in it when no other valid run exists is the OWNER's open point (reported, never resolved here).
    * item 6: MEM_POLL_S has a canonical form only when the re-check holds (case i: the re-checked value, unchanged)
      or the otherwise-branch clips to 0.5 s (case ii).

    The owner's supplement 2 (research 74f386a5), on top of those:
    * section 2 / 3: in case iii (the otherwise-branch above the floor) the function STOPS with status
      MEM_POLL_S_NONCANONICAL_BRANCH: `poll["MEM_POLL_S"]` is None (no value is produced, nothing is rounded) and the
      raw evidence and the branch are reported (`poll["unrounded_quotient_not_an_output"]`: the exact value of the
      rule's own expression, in lowest terms).
    * sections 1 and 6 (`official=True`): a memory-watchdog event in an official decoy gives the status
      QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP; there is no re-run (a run that claims to be one is invalid), no
      doubled cap and no cure.
    * section 7: for the designated series nothing but the rule's one re-run exists: no limit, no further doubling."""
    out = {"rule": "R-MEM", "ratification": RATIFICATION_COMMIT,
           "inputs": {"runs": len(runs or []), "required_cells": sorted(required_cells),
                      "measurement_cap_bytes": measurement_cap_bytes, "measurement_poll_s": fstr(measurement_poll_s)}}
    runs = list(runs or [])
    by_id = {r.get("id"): r for r in runs}
    invalid, valid = [], []
    for r in runs:
        why = _run_reasons(r, measurement_cap_bytes, measurement_poll_s, official)
        (invalid if why else valid).append((r, why))
    out["invalid_runs"] = [{"id": r.get("id"), "cell": r.get("cell"), "reasons": why} for r, why in invalid]
    out["valid_runs"] = [r.get("id") for r, _ in valid]
    valid_runs = [r for r, _ in valid]
    covered = {r.get("cell") for r in valid_runs}
    missing = sorted(c for c in required_cells if c not in covered)
    # step 1 (F-6 as ruled): an event run is never used as an input and is cured only by a VALID re-run of it at the
    # doubled provisional cap, directly or through a chain of re-runs (a re-run with an event is itself an event run)
    cured = set()
    for v in valid_runs:
        x, seen = v.get("rerun_of"), set()
        while x is not None and x not in seen:
            cured.add(x)
            seen.add(x)
            x = (by_id.get(x) or {}).get("rerun_of")
    event_ids = {r.get("id") for r, why in invalid if "MEMORY_WATCHDOG_EVENT" in why}
    uncured = [r for r, why in invalid if "MEMORY_WATCHDOG_EVENT" in why and r.get("id") not in cured]
    rerun_cap = measurement_cap_bytes * RERUN_CAP_FACTOR
    # the run to re-run next: an uncured event run whose own re-run (if any) is not itself an event run
    rerun = [{"id": r.get("id"), "cell": r.get("cell"), "rerun_cap_bytes": rerun_cap} for r in uncured
             if not any(x.get("rerun_of") == r.get("id") and x.get("id") in event_ids for x in runs)]
    out["rerun_required"] = [] if official else rerun
    host_ok = host is not None and all(_is_int(host.get(k)) for k in ("hw_memsize_bytes", "wired_pages",
                                                                       "page_size_bytes"))
    if uncured and official:               # owner supplement 2, sections 1 and 6: fail closed; nothing cures it
        out.update({"status": STATUS_OFFICIAL_WATCHDOG, "valid": False, "missing_cells": missing,
                    "event_runs": [r.get("id") for r in uncured]})
        return out
    if uncured:                            # no rule is applied until every event run has a valid re-run
        bound = {"rerun_cap_bytes": rerun_cap}
        if valid_runs and host_ok:         # "within the step-5 bound": the doubled cap in MEM_CAP's place
            p_v = max(max(_job_peak(j) for j in r["jobs"]) for r in valid_runs)
            p_v = max([p_v] + [r["worker_peak_rss_bytes"] for r in valid_runs
                               if _is_int(r.get("worker_peak_rss_bytes"))])
            d_v = max(r["driver_maxrss_bytes"] for r in valid_runs)
            lhs_v = rerun_cap + (workers - 1) * p_v + d_v
            rhs_v = host["hw_memsize_bytes"] - host["wired_pages"] * host["page_size_bytes"]
            bound.update({"defined": True, "P_bytes": p_v, "D_bytes": d_v, "lhs_bytes": lhs_v, "rhs_bytes": rhs_v,
                          "within": lhs_v <= rhs_v})
            if lhs_v > rhs_v:
                bound["stop"] = ("the doubled cap is not within the step-5 bound: the text provides no re-run; "
                                 "STOP AND REPORT BEFORE FREEZE (owner supplement 2, section 7)")
        else:
            bound.update({"defined": False, "within": None, "open_point": OPEN_RERUN_BOUND})
        out.update({"status": "RERUN_REQUIRED", "valid": False, "missing_cells": missing,
                    "uncured_event_runs": [r.get("id") for r in uncured], "rerun_step5_bound": bound})
        return out
    if not host_ok:
        out.update({"status": "INVALID_INPUT", "valid": False, "reason": "HOST_READINGS_MISSING"})
        return out
    if not valid_runs:
        out.update({"status": "NO_VALID_INPUT", "valid": False, "missing_cells": missing})
        return out
    if missing:
        out.update({"status": "INCOMPLETE_INPUT", "valid": False, "missing_cells": missing})
        return out
    # step 2
    P = max(max(_job_peak(j) for j in r["jobs"]) for r in valid_runs)
    P = max([P] + [r["worker_peak_rss_bytes"] for r in valid_runs if _is_int(r.get("worker_peak_rss_bytes"))])
    D = max(r["driver_maxrss_bytes"] for r in valid_runs)
    # step 3 (READING-3: a (kind, rung)'s peak in one run is the largest step-2 job peak of that kind and rung in that
    # run; s compares those per-run peaks across the valid runs in which the (kind, rung) appears)
    per: dict = {}
    for r in valid_runs:
        rp: dict = {}
        for j in r["jobs"]:
            key = (str(j["kind"]), int(j["rung"]))
            rp[key] = max(rp.get(key, 0), _job_peak(j))
        for key, v in rp.items():
            per.setdefault(key, []).append(v)
    spread = {f"{k}:{n}": fstr(F(max(v), min(v))) for (k, n), v in sorted(per.items()) if len(v) >= 2 and min(v) > 0}
    s = max([F(max(v), min(v)) for v in per.values() if len(v) >= 2 and min(v) > 0], default=F(1))
    # step 4
    k = max(F(K_MIN), K_SPREAD_FACTOR * s)
    mem_cap = roundup_256mib(max(k * P, MEM_FLOOR_BYTES))
    # step 5
    w_idle = host["wired_pages"] * host["page_size_bytes"]
    lhs = mem_cap + (workers - 1) * P + D
    rhs = host["hw_memsize_bytes"] - w_idle
    feas = {"lhs_bytes": lhs, "rhs_bytes": rhs, "W_idle_bytes": w_idle, "workers": workers, "ok": lhs <= rhs}
    out.update({"P_bytes": P, "D_bytes": D, "s": fstr(s), "spread_by_kind_rung": spread, "k": fstr(k),
                "MEM_CAP_BYTES": mem_cap, "feasibility": feas})
    # step 6
    bad = sampler_reasons(sampler)         # READING-6 as ruled: the OBSERVED spacing binds (exactly 0.5 s is within)
    if bad:
        out.update({"status": "INVALID_INPUT", "valid": False, "reason": bad[0],
                    "sampler_max_spacing_ns": sampler.get("max_spacing_ns") if isinstance(sampler, dict) else None})
        return out
    iv, g = F(str(sampler["interval_s"])), F(str(sampler["max_growth_bytes_per_s"]))
    gap = sampler.get("max_spacing_ns")
    poll = F(str(mem_poll_s))
    poll_ok = g * poll <= POLL_FRACTION * mem_cap
    new_poll = poll if poll_ok else max(POLL_MIN_S, POLL_FRACTION * mem_cap / g)
    case = "i" if poll_ok else ("ii" if new_poll == POLL_MIN_S else "iii")
    out["poll"] = {"g_bytes_per_s": fstr(g), "sampler_interval_s": fstr(iv), "sampler_max_spacing_ns": gap,
                   "mem_poll_s_in": fstr(poll), "recheck_ok": poll_ok, "case": case, "canonical": case != "iii",
                   "MEM_POLL_S": fstr(new_poll) if case != "iii" else None}
    if case == "iii":                      # owner supplement 2, section 2: nothing rounded, no value produced
        out["poll"].update({"branch": "step 6, otherwise-branch, 0.1 x MEM_CAP / g above the 0.5 s floor",
                            "unrounded_quotient_not_an_output": fstr(new_poll)})
    if not feas["ok"]:
        out.update({"status": "FAILS_ON_MEMORY", "valid": False})
        return out
    if case == "iii":
        out.update({"status": STATUS_POLL_NONCANONICAL, "valid": False})
        return out
    out.update({"status": "OK", "valid": True})
    return out


# ------------------------------------------------------------------ R-FREE
def r_free(mem: dict, *, readings: list, workers: int) -> dict:
    """R-FREE: FREE_MEM_MIN = max(2 GiB, roundup_256MiB(MEM_CAP + (WORKERS - 1) x P + D)) with the R-MEM values, and
    its attainability on the prepared host (>= 10 readings 30 s apart; >= 3 CONSECUTIVE readings reach FREE_MEM_MIN,
    else GATE_UNATTAINABLE; the value is never reduced)."""
    out = {"rule": "R-FREE", "ratification": RATIFICATION_COMMIT}
    if not isinstance(mem, dict) or mem.get("valid") is not True:
        out.update({"status": "NO_R_MEM_VALUE", "valid": False})
        return out
    need = mem["MEM_CAP_BYTES"] + (workers - 1) * mem["P_bytes"] + mem["D_bytes"]
    free_min = max(FREE_FLOOR_BYTES, roundup_256mib(need))
    out.update({"FREE_MEM_MIN_BYTES": free_min, "sum_bytes": need})
    rv = readings_valid(readings)
    out["readings"] = rv
    if not rv["valid"]:
        out.update({"status": "INVALID_READINGS", "valid": False, "attainable": None})
        return out
    vals = [r.get("free_memory_bytes") for r in readings]
    if any(not _is_int(v) for v in vals):
        out.update({"status": "INVALID_READINGS", "valid": False, "attainable": None,
                    "reason": "FREE_MEMORY_UNREADABLE"})
        return out
    best = run = 0
    for v in vals:
        run = run + 1 if v >= free_min else 0
        best = max(best, run)
    out["longest_consecutive_reaching"] = best
    out["attainable"] = best >= CONSECUTIVE_MIN
    out.update({"status": "ATTAINABLE" if out["attainable"] else "GATE_UNATTAINABLE", "valid": True})
    return out


# ------------------------------------------------------------------ R-EXCL-PCT
def _hosting(comm: str, hosting_app_paths) -> bool:
    return any(under(comm, p if p.endswith("/") else p + "/") or comm == p.rstrip("/") for p in hosting_app_paths)


def r_excl_pct(readings: list, *, hosting_app_paths) -> dict:
    """R-EXCL-PCT: 25, with exactly one exception: if the hosting app that runs the launcher exceeds 25 in any
    prepared-state reading, min(50, roundup_5(1.25 x its maximum reading)). READING-4: the hosting app is every process
    whose executable path lies under one of `hosting_app_paths` (its bundle); its reading in one snapshot is the
    largest %cpu of those processes (the gate compares processes one by one)."""
    out = {"rule": "R-EXCL-PCT", "ratification": RATIFICATION_COMMIT,
           "hosting_app_paths": sorted(hosting_app_paths or [])}
    if not hosting_app_paths:
        out.update({"status": "INVALID_INPUT", "valid": False, "reason": "HOSTING_APP_NOT_IDENTIFIED"})
        return out
    rv = readings_valid(readings)
    out["readings"] = rv
    if not rv["valid"]:
        out.update({"status": "INVALID_READINGS", "valid": False})
        return out
    host_max = None
    for r in readings:
        for p in r.get("procs") or []:
            if _hosting(str(p.get("comm", "")), hosting_app_paths):
                v = pct(p["pcpu"])
                host_max = v if host_max is None or v > host_max else host_max
    out["hosting_app_max_reading"] = None if host_max is None else fstr(host_max)
    if host_max is not None and host_max > EXCL_BASE_PCT:
        raw = roundup(EXCL_FACTOR * host_max, EXCL_ROUND_STEP)
        val = min(EXCL_CEILING_PCT, raw)
        out.update({"EXCL_CPU_PCT": val, "exception_applied": True, "ceiling_applied": raw > EXCL_CEILING_PCT})
    else:
        out.update({"EXCL_CPU_PCT": EXCL_BASE_PCT, "exception_applied": False, "ceiling_applied": False})
    out.update({"status": "OK", "valid": True})
    return out


# ------------------------------------------------------------------ R-ALLOW
def never_added_reason(comm: str, hosting_app_paths) -> str | None:
    """The exclusions of R-ALLOW, checked before condition (b): anything under /Applications, /Users, /opt,
    /usr/local, /Library/Frameworks, /usr/bin or /bin; any Python interpreter (READING-5: a basename python, pythonN or
    pythonN.M, or any path inside a Python.framework); the hosting app."""
    for p in NEVER_PREFIXES:
        if under(comm, p):
            return "NEVER_ADDED_PATH_CLASS " + p
    if _PY.match(basename(comm)) or "/Python.framework/" in comm + "/":
        return "NEVER_ADDED_PYTHON_INTERPRETER"
    if _hosting(comm, hosting_app_paths or []):
        return "NEVER_ADDED_HOSTING_APP"
    return None


def r_allow(readings: list, *, excl_cpu_pct, base_names, h3_readings: list, hosting_app_paths) -> dict:
    """R-ALLOW: the frozen list = the current 39 names (`base_names`) U the basename of every process that (a) exceeds
    EXCL_CPU_PCT in any prepared-state qualification reading (>= 10, 30 s apart) or in the ratification's H3 readings
    (`h3_readings`: [{name, path, pcpu}]), and (b) whose executable path lies under /System/, /usr/libexec/,
    /usr/sbin/, /sbin/ or /Library/Apple/; never an excluded class. Each addition is recorded with its path and reading;
    each process above the threshold that is not added is recorded with its reason."""
    out = {"rule": "R-ALLOW", "ratification": RATIFICATION_COMMIT, "excl_cpu_pct": fstr(pct(excl_cpu_pct)),
           "base_count": len(set(base_names or ()))}
    rv = readings_valid(readings)
    out["readings"] = rv
    if not rv["valid"]:
        out.update({"status": "INVALID_READINGS", "valid": False})
        return out
    thr = pct(excl_cpu_pct)
    cands = []
    for i, r in enumerate(readings):
        for p in r.get("procs") or []:
            cands.append({"comm": str(p.get("comm", "")), "pcpu": p.get("pcpu"), "source": f"qualification[{i}]"})
    for h in h3_readings or []:
        cands.append({"comm": str(h.get("path", "")), "name": h.get("name"), "pcpu": h.get("pcpu"),
                      "source": "ratification H3"})
    added, rejected = {}, []
    for c in cands:
        v = pct(c["pcpu"])
        if not v > thr:
            continue
        comm = c["comm"]
        name = c.get("name") or basename(comm)
        rec = {"name": name, "path": comm, "reading": fstr(v), "source": c["source"]}
        why = never_added_reason(comm, hosting_app_paths)
        if why is None and not comm.startswith("/"):
            why = "PATH_UNKNOWN"
        if why is None and not any(under(comm, p) for p in SIP_PREFIXES):
            why = "NOT_UNDER_A_SIP_PROTECTED_OS_PATH"
        if why is not None:
            rejected.append(rec | {"reason": why})
        else:
            added.setdefault(name, []).append(rec)
    base = set(base_names or ())
    out["additions"] = [{"name": n, "records": recs, "already_listed": n in base} for n, recs in sorted(added.items())]
    out["rejected"] = rejected
    out["EXCL_ALLOW"] = sorted(base | set(added))
    out.update({"status": "OK", "valid": True})
    return out
