"""Cell-308 MB-S successor campaign (r1) -- the four written rules R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW of
CONSTANTS_RATIFICATION_MBS308 (research 3c2a7854, section "Written rules"; protocol draft section 8), as PURE functions.

Built by the non-holder builder4 (research brief 46). Target-free; NOT frozen. Nothing here reads the host, a file, git
or any record: every input is passed in, and every number of the rules below is the ratification's (none is chosen
here). The functions compute the rule outputs and record every input; they decide nothing about sequencing. Which
records feed them in the official qualification (the official decoy runs under the launchd launcher, the prepared-state
readings) and how the frozen code comes to carry the outputs are the open sequencing question of protocol section 11
(case R_RULES_OFFICIAL is PENDING_USER_DECISION).

Readings of the rule text that the text leaves open are stated where they are made (READING-1 ... READING-5) and listed
in protocol section 11; each is a reading, not a new rule.

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
def _run_reasons(run: dict) -> list:
    """R-MEM step 1: an OFFICIAL decoy run (the real driver's decoy under the launchd launcher, frozen ladder, WORKERS
    5, provisional cap 3 GiB or -- for a re-run -- that cap doubled, MEM_POLL_S 2 s) without any memory-watchdog
    event."""
    r = []
    if run.get("launcher") is not True:
        r.append("NOT_UNDER_LAUNCHD_LAUNCHER")
    if run.get("ladder") != "frozen":
        r.append("NOT_THE_FROZEN_LADDER")
    if run.get("workers") != MEASUREMENT_WORKERS:
        r.append("WORKERS_NOT_5")
    want_cap = MEASUREMENT_CAP_BYTES * (RERUN_CAP_FACTOR if run.get("rerun_of") is not None else 1)
    if run.get("mem_cap_bytes") != want_cap:
        r.append("MEASUREMENT_CAP_NOT_AS_RULED")
    try:
        poll_ok = F(str(run.get("mem_poll_s"))) == MEASUREMENT_POLL_S
    except (TypeError, ValueError, ZeroDivisionError):
        poll_ok = False
    if not poll_ok:
        r.append("MEM_POLL_S_NOT_2")
    ev = run.get("watchdog_events")
    if not isinstance(ev, list):
        r.append("WATCHDOG_EVENTS_UNRECORDED")
    elif ev:
        r.append("MEMORY_WATCHDOG_EVENT")
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


def r_mem(runs: list, *, required_cells, workers: int, mem_poll_s, host: dict, sampler: dict) -> dict:
    """R-MEM. `runs`: [{id, cell, launcher, ladder, workers, mem_cap_bytes, mem_poll_s, rerun_of, watchdog_events,
    driver_maxrss_bytes, worker_peak_rss_bytes, jobs: [{name, kind, rung, job_maxrss_bytes[, worker_peak_rss_bytes]}]}];
    `required_cells`: the decoy cells of the qualification plan; `workers`, `mem_poll_s`: the driver's WORKERS and
    MEM_POLL_S; `host`: {hw_memsize_bytes, wired_pages, page_size_bytes} of the prepared idle state; `sampler`:
    {interval_s, max_growth_bytes_per_s} of the <= 0.5 s qualification sampler."""
    out = {"rule": "R-MEM", "ratification": RATIFICATION_COMMIT, "inputs": {"runs": len(runs or []),
                                                                            "required_cells": sorted(required_cells)}}
    runs = list(runs or [])
    reruns_of = {r.get("rerun_of") for r in runs if r.get("rerun_of") is not None}
    invalid, valid = [], []
    for r in runs:
        why = _run_reasons(r)
        (invalid if why else valid).append((r, why))
    out["invalid_runs"] = [{"id": r.get("id"), "cell": r.get("cell"), "reasons": why} for r, why in invalid]
    out["valid_runs"] = [r.get("id") for r, _ in valid]
    valid_runs = [r for r, _ in valid]
    covered = {r.get("cell") for r in valid_runs}
    missing = sorted(c for c in required_cells if c not in covered)
    # step 1: a decoy with a watchdog event is re-run with the provisional cap doubled (never used as an input)
    rerun = []
    for r, why in invalid:
        if "MEMORY_WATCHDOG_EVENT" in why and r.get("rerun_of") is None and r.get("id") not in reruns_of:
            rerun.append({"id": r.get("id"), "cell": r.get("cell"),
                          "rerun_cap_bytes": MEASUREMENT_CAP_BYTES * RERUN_CAP_FACTOR})
    out["rerun_required"] = rerun
    if host is None or not all(_is_int(host.get(k)) for k in ("hw_memsize_bytes", "wired_pages", "page_size_bytes")):
        out.update({"status": "INVALID_INPUT", "valid": False, "reason": "HOST_READINGS_MISSING"})
        return out
    if not valid_runs:
        out.update({"status": "NO_VALID_INPUT", "valid": False, "missing_cells": missing})
        return out
    if rerun:                              # every decoy with a watchdog event is re-run before the rule is applied
        out.update({"status": "RERUN_REQUIRED", "valid": False, "missing_cells": missing})
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
    try:
        iv, g = F(str(sampler["interval_s"])), F(str(sampler["max_growth_bytes_per_s"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        out.update({"status": "INVALID_INPUT", "valid": False, "reason": "SAMPLER_MISSING"})
        return out
    if iv <= 0 or iv > SAMPLER_MAX_INTERVAL_S or g < 0:
        out.update({"status": "INVALID_INPUT", "valid": False, "reason": "SAMPLER_INTERVAL_ABOVE_0.5_S"
                    if iv > SAMPLER_MAX_INTERVAL_S else "SAMPLER_MALFORMED"})
        return out
    poll = F(str(mem_poll_s))
    poll_ok = g * poll <= POLL_FRACTION * mem_cap
    new_poll = poll if poll_ok else max(POLL_MIN_S, POLL_FRACTION * mem_cap / g)
    out["poll"] = {"g_bytes_per_s": fstr(g), "sampler_interval_s": fstr(iv), "mem_poll_s_in": fstr(poll),
                   "recheck_ok": poll_ok, "MEM_POLL_S": fstr(new_poll)}
    if not feas["ok"]:
        out.update({"status": "FAILS_ON_MEMORY", "valid": False})
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
