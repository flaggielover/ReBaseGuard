"""Cell-308 MB-S successor campaign (r1) -- the R-rule DERIVATION tool and the adapters it shares with the official
qualification (the user's section-11.2 ruling, option (a): owner supplement 1, part I; protocol section 11.2).
Built by the non-holder builder6 (research brief 54, part B2). Target-free; NOT frozen; pure: it reads no host state
and never imports the driver.

The chain it serves (one freeze; no constant changes after it):

    designated pre-freeze measurements (code/mbs308_measure.py; evidence_prefreeze/MBS308_RRULES_DESIGNATED.json)
      -> THIS tool: the EXISTING rule functions of code/mbs308_rrules.py, applied mechanically -> canonical outputs A
      -> the reviewed apply step (code/mbs308_repin.py apply): A into the driver and the protocol table, nothing else
      -> the freeze -> the official qualification, whose decoys run with the frozen values
      -> its own measurements -> the SAME functions -> canonical outputs B
      -> case R_RULES_OFFICIAL: B == A == the constants the frozen driver carries, exactly, for each of the five.

The five canonical outputs (owner supplement 1, section 1), each in the form the rule text itself fixes (the second
ratifier's item 6: CONSTANTS_RATIFICATION_MBS308_READINGS_R1, research ca66e367; checked by `form_reasons`):
    MEM_CAP_BYTES       int bytes, a multiple of 256 MiB, at least 1 GiB            (R-MEM step 4)
    MEM_POLL_S          "2" (the re-check holds: the re-checked value, unchanged) or "1/2" (the rule clips to 0.5 s)
    FREE_MEM_MIN_BYTES  int bytes, a multiple of 256 MiB, at least 2 GiB            (R-FREE)
    EXCL_CPU_PCT        int: 25, or one of 35, 40, 45, 50                           (R-EXCL-PCT)
    EXCL_ALLOW          a set of exact basename strings, carried as the sorted, de-duplicated list (R-ALLOW)
Nothing here adds a tolerance, a superset / subset reading or a canonicalisation that could hide a difference: scalars
are compared as exact integers / rationals and the list as a set of exact strings.

The fail-closed statuses (owner supplement 2, research 74f386a5; the names are mbs308_rrules.STATUS_*):
    STEP1_RERUN_REQUIRED             a designated run with a memory-watchdog event (no valid re-run): stop and report
    MEM_POLL_S_NONCANONICAL_BRANCH   step 6 reaches the unrounded-quotient branch: STOP BEFORE FREEZE; the raw evidence
                                     and the branch are reported, nothing is rounded, MEM_POLL_S has no output value
In either state no output is produced (every output is None) and the apply step refuses.

Readings of the rule text made here (protocol section 11.3; none changes a rule number):
  READING-11 R-MEM step 5's W_idle ("vm_stat wired down x page size in the prepared idle state") is taken as the LARGEST
             wired-down reading of the prepared-state series: the feasibility then holds for every reading of the series.
  READING-6  as CORRECTED by the second ratifier (item 2): step 6's "<= 0.5 s" binds the OBSERVED spacing of the
             sampler's readings. Over the runs of a series the largest observed spacing of any run is the one checked.

    python3.14 -I -S -B mbs308_derive.py derive --evidence FILE --out FILE [--ns DIR] [--repo DIR]
(writes only --out; the reviewed derivation that is committed lives under evidence_prefreeze/)
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
import mbs308_rrules as RR  # noqa: E402

NS_REL = "level4/closure_proofs/p5y_k5_cell308_mbs_r1"
OUTPUTS = ("MEM_CAP_BYTES", "MEM_POLL_S", "FREE_MEM_MIN_BYTES", "EXCL_CPU_PCT", "EXCL_ALLOW")
EVIDENCE_SCHEMA = "rebaseguard.p5y.k5.cell308-mbs-r1.rrules-designated-measurement.v1"
DERIVATION_SCHEMA = "rebaseguard.p5y.k5.cell308-mbs-r1.rrules-derivation.v1"
EVIDENCE_NAME = "MBS308_RRULES_DESIGNATED.json"
DERIVATION_NAME = "MBS308_RRULES_DERIVATION.json"
GENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1"}


class DeriveRefusal(Exception):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ the constants a driver TEXT carries (exact)
def _exact(node, src: str):
    """An exact value of a constant expression of the driver's text: an int; a float literal as the Fraction of its
    DECIMAL TEXT (never through the binary float); + - * ** of those; p / q as a Fraction. Anything else refuses."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            raise ValueError("bool")
        if isinstance(node.value, int):
            return F(node.value)
        if isinstance(node.value, float):
            return F(ast.get_source_segment(src, node).replace("_", ""))
        raise ValueError(type(node.value).__name__)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
        a, b = _exact(node.left, src), _exact(node.right, src)
        if isinstance(node.op, ast.Add):
            return a + b
        if isinstance(node.op, ast.Sub):
            return a - b
        if isinstance(node.op, ast.Mult):
            return a * b
        if isinstance(node.op, ast.Div):
            return a / b
        if b.denominator != 1 or b < 0:
            raise ValueError("power")
        return a ** int(b)
    raise ValueError(type(node).__name__)


def _binding(src: str, name: str):
    found = [n for n in ast.parse(src).body if isinstance(n, ast.Assign) and
             [getattr(t, "id", None) for t in n.targets] == [name]]
    if len(found) != 1:
        raise DeriveRefusal("DRIVER_CONSTANT", f"{name} is bound {len(found)} time(s) at module level, not once")
    return found[0]


def _int_of(x: F, name: str) -> int:
    if x.denominator != 1:
        raise DeriveRefusal("DRIVER_CONSTANT", f"{name} is not an integer")
    return int(x)


def driver_constants(src: str) -> dict:
    """The five rule constants exactly as a driver's TEXT carries them, in canonical form, plus WORKERS and
    DECOY_CELLS. The driver is never imported; a constant that is not a plain literal expression refuses."""
    out = {}
    try:
        out["MEM_CAP_BYTES"] = _int_of(_exact(_binding(src, "MEM_CAP_BYTES").value, src), "MEM_CAP_BYTES")
        out["MEM_POLL_S"] = RR.fstr(_exact(_binding(src, "MEM_POLL_S").value, src))
        out["FREE_MEM_MIN_BYTES"] = _int_of(_exact(_binding(src, "FREE_MEM_MIN_BYTES").value, src),
                                            "FREE_MEM_MIN_BYTES")
        out["EXCL_CPU_PCT"] = _int_of(_exact(_binding(src, "EXCL_CPU_PCT").value, src), "EXCL_CPU_PCT")
        out["WORKERS"] = _int_of(_exact(_binding(src, "WORKERS").value, src), "WORKERS")
    except (ValueError, ZeroDivisionError) as exc:
        raise DeriveRefusal("DRIVER_CONSTANT", f"not a literal constant expression ({exc})")
    al = _binding(src, "EXCL_ALLOW").value
    if not (isinstance(al, ast.Call) and getattr(al.func, "id", None) == "frozenset" and len(al.args) == 1 and
            not al.keywords and isinstance(al.args[0], (ast.Set, ast.List, ast.Tuple)) and
            all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in al.args[0].elts)):
        raise DeriveRefusal("DRIVER_CONSTANT", "EXCL_ALLOW is not a frozenset of string literals")
    names = [e.value for e in al.args[0].elts]
    if len(set(names)) != len(names):
        raise DeriveRefusal("DRIVER_CONSTANT", "EXCL_ALLOW names a process twice")
    out["EXCL_ALLOW"] = sorted(names)
    dc = _binding(src, "DECOY_CELLS").value
    if not (isinstance(dc, ast.Tuple) and all(isinstance(e, ast.Constant) and type(e.value) is int for e in dc.elts)):
        raise DeriveRefusal("DRIVER_CONSTANT", "DECOY_CELLS is not a tuple of int literals")
    out["DECOY_CELLS"] = [e.value for e in dc.elts]
    return out


def driver_outputs(src: str) -> dict:
    c = driver_constants(src)
    return {k: c[k] for k in OUTPUTS}


# ------------------------------------------------------------------ adapters: decoy record -> rule inputs
def compact_run(rec: dict, run_id: str, *, exit_code=None, raw_sha256: str | None = None) -> dict:
    """The R-rule inputs of ONE driver `decoy` record (the driver's own fields; nothing computed, no certified value
    copied): the run's configuration as R-MEM step 1 names it, every job's ru_maxrss, the watchdog's events and peak,
    the driver's own peak RSS, the <= 0.5 s sampler record, and the run's host provenance."""
    lc = rec.get("lifecycle") if isinstance(rec.get("lifecycle"), dict) else {}
    ctx = lc.get("stage1_context") if isinstance(lc.get("stage1_context"), dict) else {}
    wd = ctx.get("memory_watchdog") if isinstance(ctx.get("memory_watchdog"), dict) else {}
    jobs = []
    for name, rss in sorted((ctx.get("job_maxrss_bytes") or {}).items()):
        parts = str(name).split(".")
        if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
            jobs.append({"name": name, "kind": parts[0], "rung": int(parts[2]), "job_maxrss_bytes": rss})
        else:
            jobs.append({"name": name, "kind": None, "rung": None, "job_maxrss_bytes": rss})
    return {"id": run_id, "cell": rec.get("decoy_cell"), "blocks_total": rec.get("blocks_total"),
            "blocks_run": rec.get("blocks_run"), "dev_ladder": rec.get("dev_ladder"),
            "rmem_run": lc.get("rmem_run"), "jobs": jobs,
            "jobs_computed": ctx.get("jobs_computed"), "jobs_served_from_checkpoints": ctx.get(
                "jobs_served_from_checkpoints"),
            "watchdog_events": wd.get("events"), "watchdog_cap_bytes": wd.get("cap_bytes"),
            "worker_peak_rss_bytes": wd.get("worker_peak_rss_bytes"),
            "driver_maxrss_bytes": lc.get("driver_maxrss_bytes"), "rss_sampler": lc.get("rss_sampler"),
            "host": rec.get("host"), "driver_sha256": rec.get("driver_sha256"), "utc": rec.get("utc"),
            "decoy_failed": rec.get("decoy_failed"), "exit": exit_code, "raw_sha256": raw_sha256}


def run_input(run: dict, rerun_of=None) -> dict:
    """One compact run as mbs308_rrules.r_mem takes it (a missing field stays missing: the rule function names it)."""
    cfg = run.get("rmem_run") if isinstance(run.get("rmem_run"), dict) else {}
    poll = cfg.get("mem_poll_s")
    return {"id": run.get("id"), "cell": run.get("cell"), "launcher": cfg.get("launched_by_launchd"),
            "ladder": cfg.get("ladder"), "workers": cfg.get("workers"), "mem_cap_bytes": cfg.get("mem_cap_bytes"),
            "mem_poll_s": None if poll is None else (repr(poll) if isinstance(poll, float) else str(poll)),
            "rerun_of": rerun_of, "watchdog_events": run.get("watchdog_events"),
            "driver_maxrss_bytes": run.get("driver_maxrss_bytes"),
            "worker_peak_rss_bytes": run.get("worker_peak_rss_bytes"), "jobs": run.get("jobs")}


def plan_reasons(run: dict, plan: dict) -> list:
    """The run is one of the planned official decoys (config `official_decoys`: cell -> first blocks, None = every
    block), it completed (exit 0, when known) and it computed every job itself (no checkpoint was served)."""
    r = []
    cell = run.get("cell")
    if cell not in plan:
        r.append("CELL_NOT_IN_THE_PLAN")
    else:
        want = plan[cell]
        got = (run.get("rmem_run") or {}).get("first_blocks")
        if got != want:
            r.append("BLOCKS_NOT_AS_PLANNED")
        if want is None and run.get("blocks_run") != "all":
            r.append("BLOCKS_NOT_AS_PLANNED")
        if want is not None and run.get("blocks_run") != list(range(want)):
            r.append("BLOCKS_NOT_AS_PLANNED")
    if run.get("exit") not in (None, 0, "0"):
        r.append("RUN_EXIT_NOT_ZERO")
    if run.get("decoy_failed") is not None:          # the driver's record of a decoy that raised (never an input)
        r.append("DECOY_FAILED")
    if run.get("jobs_served_from_checkpoints") not in (0, None) or not run.get("jobs_computed"):
        r.append("JOBS_NOT_ALL_COMPUTED_BY_THIS_RUN")
    if any(j.get("kind") is None for j in run.get("jobs") or []):
        r.append("JOB_NAME_MALFORMED")
    return sorted(set(r))


def sampler_input(runs: list) -> dict | None:
    """R-MEM step 6's g: the highest RSS growth rate seen by the <= 0.5 s sampler over the runs (each run carries its
    own sampler record); `interval_s` is the largest SET interval of those samplers and `max_spacing_ns` the largest
    spacing OBSERVED between two readings in any run (READING-6 as corrected: the bound binds this one; None when a
    run does not state it, which the rule function refuses). A run without a complete sampler record gives None (the
    rule function then reports SAMPLER_MISSING)."""
    gs, ivs, gaps = [], [], []
    for r in runs:
        s = r.get("rss_sampler")
        if not isinstance(s, dict) or isinstance(s.get("max_growth_bytes_per_s"), bool) or \
                not isinstance(s.get("max_growth_bytes_per_s"), int) or not isinstance(s.get("interval_s"), str) or \
                not isinstance(s.get("samples"), int) or s["samples"] < 2:
            return None
        try:
            ivs.append(F(s["interval_s"]))
        except (ValueError, ZeroDivisionError):
            return None
        gs.append(s["max_growth_bytes_per_s"])
        gaps.append(s.get("max_spacing_ns"))
    if not gs:
        return None
    stated = all(isinstance(x, int) and not isinstance(x, bool) for x in gaps)
    return {"interval_s": RR.fstr(max(ivs)), "max_growth_bytes_per_s": max(gs),
            "max_spacing_ns": max(gaps) if stated else None, "max_spacing_ns_by_run": gaps, "runs": len(gs)}


def host_input(readings: list, hw_memsize_bytes) -> dict | None:
    """R-MEM step 5's host readings: hw.memsize and W_idle = the LARGEST wired-down reading of the prepared-state series
    (READING-11), with the page size (which must be one value over the series)."""
    if not isinstance(readings, list) or not readings:
        return None
    wired = [r.get("wired_pages") for r in readings if isinstance(r, dict)]
    pages = {r.get("page_size_bytes") for r in readings if isinstance(r, dict)}
    ok = lambda v: isinstance(v, int) and not isinstance(v, bool)  # noqa: E731
    if len(wired) != len(readings) or not all(ok(w) for w in wired) or len(pages) != 1 or not ok(next(iter(pages))) \
            or not ok(hw_memsize_bytes):
        return None
    return {"hw_memsize_bytes": hw_memsize_bytes, "wired_pages": max(wired), "page_size_bytes": next(iter(pages)),
            "wired_pages_by_reading": wired}


def rule_readings(readings: list) -> list:
    """The prepared-state readings as the rule functions take them (t_s, power, free_memory_bytes, procs)."""
    out = []
    for r in readings if isinstance(readings, list) else []:
        r = r if isinstance(r, dict) else {}
        out.append({"t_s": r.get("t_s"), "power": r.get("power"), "free_memory_bytes": r.get("free_memory_bytes"),
                    "procs": r.get("procs") or []})
    return out


# ------------------------------------------------------------------ the rules, applied mechanically
def apply_rules(*, runs: list, readings: list, hw_memsize_bytes, hosting_app_paths, base_names, h3_readings,
                plan: dict, workers: int, mem_poll_s, measurement_cap_bytes: int, measurement_poll_s,
                official: bool = False) -> dict:
    """The four EXISTING rule functions on one measurement series (`official`: the official qualification's series,
    after the freeze; otherwise the designated pre-freeze series). Nothing is decided here: every status, value and
    reason is the rule function's own, except the plan check of each run (plan_reasons), which only removes a run that
    is not one of the planned official decoys."""
    plan_bad = [{"id": r.get("id"), "cell": r.get("cell"), "reasons": why} for r in runs
                for why in [plan_reasons(r, plan)] if why]
    bad_ids = {b["id"] for b in plan_bad}
    # a run with a memory-watchdog event always reaches the rule function (it is never dropped as "not as planned": the
    # driver's record of a failed decoy has no blocks), so R-MEM step 1 names it and no rule is applied past it
    used = [r for r in runs if r.get("id") not in bad_ids or RR.cap_events(r.get("watchdog_events"))]
    host = host_input(readings, hw_memsize_bytes)
    rr = rule_readings(readings)
    mem = RR.r_mem([run_input(r) for r in used], required_cells=sorted(plan), workers=workers, mem_poll_s=mem_poll_s,
                   host=host, sampler=sampler_input(used), measurement_cap_bytes=measurement_cap_bytes,
                   measurement_poll_s=measurement_poll_s, official=official)
    free = RR.r_free(mem, readings=rr, workers=workers)
    excl = RR.r_excl_pct(rr, hosting_app_paths=list(hosting_app_paths or []))
    if excl.get("valid") is True:
        allow = RR.r_allow(rr, excl_cpu_pct=excl["EXCL_CPU_PCT"], base_names=set(base_names),
                           h3_readings=list(h3_readings or []), hosting_app_paths=list(hosting_app_paths or []))
    else:
        allow = {"rule": "R-ALLOW", "status": "NO_R_EXCL_PCT_VALUE", "valid": False}
    return {"runs_not_as_planned": plan_bad, "host_input": host, "sampler_input": sampler_input(used), "r_mem": mem,
            "r_free": free, "r_excl_pct": excl, "r_allow": allow}


def canonical(rules: dict) -> dict:
    """The five canonical outputs of one application of the rules. An output whose rule did not produce a value is
    None (never a default, never the provisional value). MEM_POLL_S exists only on a canonical branch of step 6 (owner
    supplement 2, sections 2 and 3: on the unrounded-quotient branch no value is made)."""
    mem, free, excl, allow = (rules.get(k) or {} for k in ("r_mem", "r_free", "r_excl_pct", "r_allow"))
    out = dict.fromkeys(OUTPUTS)
    if mem.get("status") == "OK" and isinstance(mem.get("MEM_CAP_BYTES"), int):
        out["MEM_CAP_BYTES"] = mem["MEM_CAP_BYTES"]
        poll = mem.get("poll") or {}
        if poll.get("canonical") is True and isinstance(poll.get("MEM_POLL_S"), str):
            out["MEM_POLL_S"] = RR.fstr(F(poll["MEM_POLL_S"]))
    if free.get("valid") is True and isinstance(free.get("FREE_MEM_MIN_BYTES"), int):
        out["FREE_MEM_MIN_BYTES"] = free["FREE_MEM_MIN_BYTES"]
    if excl.get("valid") is True and isinstance(excl.get("EXCL_CPU_PCT"), int):
        out["EXCL_CPU_PCT"] = excl["EXCL_CPU_PCT"]
    if allow.get("valid") is True and isinstance(allow.get("EXCL_ALLOW"), list):
        out["EXCL_ALLOW"] = sorted(set(allow["EXCL_ALLOW"]))
    return out


EXCL_PCT_VALUES = (RR.EXCL_BASE_PCT,) + tuple(
    v for v in range(RR.EXCL_ROUND_STEP, RR.EXCL_CEILING_PCT + 1, RR.EXCL_ROUND_STEP)
    if v > RR.EXCL_FACTOR * RR.EXCL_BASE_PCT)                      # 25, or roundup_5(1.25 x r) <= 50 for a reading r > 25
POLL_VALUES = (RR.MEASUREMENT_POLL_S, RR.POLL_MIN_S)               # the re-checked value unchanged, or the 0.5 s clip


def form_reasons(outputs) -> list:
    """Why a set of five outputs is NOT in the canonical form the rule text fixes (readings R1, item 6; empty = it is).
    A check of FORM only: it says nothing about whether a value is the right one."""
    o = outputs if isinstance(outputs, dict) else {}
    isint = lambda v: isinstance(v, int) and not isinstance(v, bool)  # noqa: E731
    r = []
    cap, free, pc, poll, al = (o.get(k) for k in ("MEM_CAP_BYTES", "FREE_MEM_MIN_BYTES", "EXCL_CPU_PCT", "MEM_POLL_S",
                                                  "EXCL_ALLOW"))
    if not (isint(cap) and cap >= RR.MEM_FLOOR_BYTES and cap % RR.ROUND_STEP_BYTES == 0):
        r.append("MEM_CAP_BYTES_NOT_CANONICAL")
    try:
        poll_ok = isinstance(poll, str) and F(poll) in POLL_VALUES and RR.fstr(F(poll)) == poll
    except (ValueError, ZeroDivisionError):
        poll_ok = False
    if not poll_ok:
        r.append("MEM_POLL_S_NOT_CANONICAL")
    if not (isint(free) and free >= RR.FREE_FLOOR_BYTES and free % RR.ROUND_STEP_BYTES == 0):
        r.append("FREE_MEM_MIN_BYTES_NOT_CANONICAL")
    if not (isint(pc) and pc in EXCL_PCT_VALUES):
        r.append("EXCL_CPU_PCT_NOT_CANONICAL")
    if not (isinstance(al, list) and al and all(isinstance(n, str) and n and "/" not in n for n in al) and
            al == sorted(set(al))):
        r.append("EXCL_ALLOW_NOT_CANONICAL")
    return r


def stop_statuses(rules: dict) -> list:
    """The fail-closed statuses one application of the rules reached (mbs308_rrules.STATUS_*; empty = none)."""
    mem = (rules or {}).get("r_mem") or {}
    st = []
    if mem.get("status") == "RERUN_REQUIRED":
        st.append(RR.STATUS_STEP1_RERUN)
    if mem.get("status") == RR.STATUS_OFFICIAL_WATCHDOG:
        st.append(RR.STATUS_OFFICIAL_WATCHDOG)
    if (mem.get("poll") or {}).get("case") == "iii":
        st.append(RR.STATUS_POLL_NONCANONICAL)
    return st


def checks(rules: dict) -> dict:
    """Every built-in check of the rules, as written (recorded; `all_hold` is their conjunction)."""
    mem, free, excl, allow = (rules.get(k) or {} for k in ("r_mem", "r_free", "r_excl_pct", "r_allow"))
    adds = [rec for a in allow.get("additions") or [] for rec in a.get("records") or []]
    c = {
        "runs_all_as_planned": not rules.get("runs_not_as_planned"),
        "r_mem_no_invalid_run": mem.get("invalid_runs") == [],
        "r_mem_no_rerun_required": mem.get("rerun_required") == [],
        "r_mem_status_ok": mem.get("status") == "OK",
        "r_mem_step5_feasible": (mem.get("feasibility") or {}).get("ok") is True,
        "r_mem_step6_sampler_valid": RR.sampler_reasons(rules.get("sampler_input")) == [],
        "r_mem_step6_poll_on_a_canonical_branch": (mem.get("poll") or {}).get("canonical") is True and
        isinstance((mem.get("poll") or {}).get("MEM_POLL_S"), str),
        "r_free_attainable": free.get("status") == "ATTAINABLE",
        "r_excl_pct_ok": excl.get("status") == "OK",
        "r_allow_ok": allow.get("status") == "OK",
        "r_allow_b_every_addition_under_a_sip_path": allow.get("status") == "OK" and all(
            any(RR.under(rec.get("path"), p) for p in RR.SIP_PREFIXES) for rec in adds),
        "r_allow_never_added_none_admitted": allow.get("status") == "OK" and all(
            RR.never_added_reason(str(rec.get("path")), excl.get("hosting_app_paths") or []) is None for rec in adds),
        # R-EXCL-PCT: "Any other process above the threshold must be quit (or pass R-ALLOW); it is never a reason to
        # raise the threshold": a reading that holds such a process is not a prepared-state reading
        "host_prepared_no_process_left_above_the_threshold": allow.get("status") == "OK" and
        allow.get("rejected") == [],
    }
    c["all_hold"] = all(v is True for v in c.values())
    return c


def poll_note(rules: dict) -> dict:
    """Step 6 as it was reached: the raw evidence (g, the cap, the re-checked value, the sampler's set interval and
    largest observed spacing) and the branch. On the non-canonical branch `MEM_POLL_S` is None and the rule's exact
    expression is reported as `unrounded_quotient_not_an_output` (owner supplement 2, section 2: nothing rounded)."""
    m = rules.get("r_mem") or {}
    p = m.get("poll") or {}
    return {"recheck_ok": p.get("recheck_ok"), "mem_poll_s_in": p.get("mem_poll_s_in"),
            "MEM_POLL_S": p.get("MEM_POLL_S"), "g_bytes_per_s": p.get("g_bytes_per_s"), "case": p.get("case"),
            "canonical": p.get("canonical"), "branch": p.get("branch"),
            "unrounded_quotient_not_an_output": p.get("unrounded_quotient_not_an_output"),
            "MEM_CAP_BYTES": m.get("MEM_CAP_BYTES"), "sampler_interval_s": p.get("sampler_interval_s"),
            "sampler_max_spacing_ns": p.get("sampler_max_spacing_ns")}


def compare(a: dict, b: dict, c: dict) -> dict:
    """EXACT agreement of each canonical output: A (designated measurements), B (official qualification), C (the
    constants the frozen driver carries). No tolerance; EXCL_ALLOW as set equality of the canonical lists. A missing
    output (None) never agrees."""
    rows = {}
    for k in OUTPUTS:
        va, vb, vc = a.get(k), b.get(k), c.get(k)
        if k == "EXCL_ALLOW":
            ok = all(isinstance(v, list) for v in (va, vb, vc)) and set(va) == set(vb) == set(vc) and \
                len(set(va)) == len(va) and len(set(vb)) == len(vb) and len(set(vc)) == len(vc)
            rows[k] = {"equal": ok, "n": [len(v) if isinstance(v, list) else None for v in (va, vb, vc)],
                       "only_in_A": sorted(set(va or []) - set(vb or [])),
                       "only_in_B": sorted(set(vb or []) - set(va or [])),
                       "driver_minus_A": sorted(set(vc or []) - set(va or [])),
                       "A_minus_driver": sorted(set(va or []) - set(vc or []))}
        elif k == "MEM_POLL_S":
            try:
                ok = all(isinstance(v, str) for v in (va, vb, vc)) and F(va) == F(vb) == F(vc)
            except (ValueError, ZeroDivisionError):
                ok = False
            rows[k] = {"equal": ok, "A": va, "B": vb, "driver": vc}
        else:
            ok = all(isinstance(v, int) and not isinstance(v, bool) for v in (va, vb, vc)) and va == vb == vc
            rows[k] = {"equal": ok, "A": va, "B": vb, "driver": vc}
    return {"outputs": rows, "all_equal": all(r["equal"] is True for r in rows.values()) and len(rows) == len(OUTPUTS)}


# ------------------------------------------------------------------ the designated evidence -> canonical outputs A
def evidence_reasons(ev) -> list:
    """Why a file is not designated evidence (empty = it is): the schema, the DESIGNATED flag the measurement tool sets
    only when its run was valid, no recorded invalidity, and the fields the derivation needs."""
    if not isinstance(ev, dict):
        return ["NOT_AN_OBJECT"]
    r = []
    if ev.get("schema") != EVIDENCE_SCHEMA:
        r.append("SCHEMA")
    if ev.get("designated") is not True:
        r.append("NOT_DESIGNATED")
    if ev.get("invalid_reasons") != []:
        r.append("INVALID_REASONS_RECORDED")
    if ev.get("target_evaluations") != 0:
        r.append("TARGET_EVALUATIONS_NOT_ZERO")
    for k in ("commit", "driver_sha256", "runs", "readings", "hw_memsize_bytes", "hosting_app"):
        if ev.get(k) in (None, "", []):
            r.append(f"MISSING_{k.upper()}")
    return r


def derive_a(ev: dict, *, base_names, h3_readings, plan: dict) -> dict:
    """Canonical outputs A from the designated evidence: R-MEM step 1's own configuration (WORKERS 5, the provisional
    cap 3 GiB, MEM_POLL_S 2 s: the rule's numbers, not a driver's), the prepared-host readings and the hosting app the
    measurement recorded."""
    rules = apply_rules(runs=list(ev.get("runs") or []), readings=ev.get("readings"),
                        hw_memsize_bytes=ev.get("hw_memsize_bytes"),
                        hosting_app_paths=(ev.get("hosting_app") or {}).get("paths"), base_names=base_names,
                        h3_readings=h3_readings, plan=plan, workers=RR.MEASUREMENT_WORKERS,
                        mem_poll_s=RR.MEASUREMENT_POLL_S, measurement_cap_bytes=RR.MEASUREMENT_CAP_BYTES,
                        measurement_poll_s=RR.MEASUREMENT_POLL_S)
    outs = canonical(rules)
    return {"rules": rules, "outputs": outs, "checks": checks(rules), "poll": poll_note(rules),
            "fail_closed_statuses": stop_statuses(rules),
            "form_reasons": form_reasons(outs) if all(outs[k] is not None for k in OUTPUTS) else None}


def derivation(ev: dict, *, evidence_sha256: str, base_names, h3_readings, plan: dict, rules_sha256: str,
               tool_sha256: str) -> dict:
    """The derivation record. `status`: "OK" (five canonical outputs, every check holds); a fail-closed status of
    mbs308_rrules (STEP1_RERUN_REQUIRED, MEM_POLL_S_NONCANONICAL_BRANCH: STOP BEFORE FREEZE, with the raw evidence in
    `poll` / `rules`); or "NOT_DERIVED". Unless the status is OK every output is None."""
    why = evidence_reasons(ev)
    a = derive_a(ev, base_names=base_names, h3_readings=h3_readings, plan=plan)
    stops = a["fail_closed_statuses"]
    ok = not why and not stops and a["checks"]["all_hold"] is True and a["form_reasons"] == [] and \
        all(a["outputs"][k] is not None for k in OUTPUTS)
    return {"schema": DERIVATION_SCHEMA, "designated": ev.get("designated") is True and not why,
            "status": "OK" if ok else (stops[0] if stops else "NOT_DERIVED"), "evidence_reasons": why,
            "fail_closed_statuses": stops, "stop_before_freeze": not ok, "form_reasons": a["form_reasons"],
            "evidence": {"name": EVIDENCE_NAME, "sha256": evidence_sha256, "commit": ev.get("commit"),
                         "driver_sha256": ev.get("driver_sha256")},
            "outputs": a["outputs"] if ok else dict.fromkeys(OUTPUTS), "outputs_as_computed": a["outputs"],
            "checks": a["checks"], "poll": a["poll"], "rules": a["rules"],
            "inputs": {"base_names": sorted(base_names), "h3_readings": list(h3_readings or []),
                       "plan": {str(k): v for k, v in sorted(plan.items())}, "workers": RR.MEASUREMENT_WORKERS,
                       "mem_poll_s_in": RR.fstr(RR.MEASUREMENT_POLL_S),
                       "measurement_cap_bytes": RR.MEASUREMENT_CAP_BYTES},
            "rules_sha256": rules_sha256, "tool_sha256": tool_sha256, "ratification": RR.RATIFICATION_COMMIT,
            "target_evaluations": 0}


# ------------------------------------------------------------------ inputs read from committed text (git, read-only)
def git_show(repo: Path, commit: str, rel: str) -> bytes | None:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(repo), "cat-file", "blob",
                        f"{commit}:{rel}"], capture_output=True, env=GENV, stdin=subprocess.DEVNULL)
    return p.stdout if p.returncode == 0 else None


def plan_of(cfg: dict) -> dict:
    return {int(d["cell"]): d["first_blocks"] for d in cfg["official_decoys"]}


def base_names_of(cfg: dict, repo: Path) -> list:
    """R-ALLOW's "current 39 names": EXCL_ALLOW of the driver at the commit the configuration pins (35cabb50)."""
    pin = next(c for c in cfg["commit_pins"] if c["key"] == "driver_39_names_35cabb50")
    raw = git_show(repo, pin["commit"], pin["path"])
    if raw is None:
        raise DeriveRefusal("BASE_NAMES", "the pinned driver of R-ALLOW's 39 names does not resolve")
    names = driver_constants(raw.decode())["EXCL_ALLOW"]
    if len(names) != 39:
        raise DeriveRefusal("BASE_NAMES", f"{len(names)} names at the pinned commit, not 39")
    return names


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("derive",))
    ap.add_argument("--evidence", required=True, help="the designated measurement evidence (JSON)")
    ap.add_argument("--out", required=True, help="where the derivation is written (nothing else is written)")
    ap.add_argument("--ns", help="namespace directory (default: this namespace)")
    ap.add_argument("--repo", help="repository for the pinned commits (default: this namespace's repository)")
    a = ap.parse_args(argv)
    ns = Path(a.ns).resolve() if a.ns else NS
    repo = Path(a.repo).resolve() if a.repo else REPO
    try:
        raw = Path(a.evidence).read_bytes()
        ev = json.loads(raw)
        cfg = json.loads((ns / "config" / "MBS308_QUALIFICATION_CASES.json").read_text())
        d = derivation(ev, evidence_sha256=sha(raw), base_names=base_names_of(cfg, repo),
                       h3_readings=cfg["r_allow_h3_readings"]["readings"], plan=plan_of(cfg),
                       rules_sha256=sha((ns / "code" / "mbs308_rrules.py").read_bytes()),
                       tool_sha256=sha(HERE.read_bytes()))
    except DeriveRefusal as e:
        print(json.dumps({"refused": e.code, "detail": str(e)}))
        return 2
    except (OSError, ValueError, KeyError) as e:
        print(json.dumps({"refused": "INPUT", "detail": f"{type(e).__name__}: {e}"[:300]}))
        return 2
    Path(a.out).write_text(json.dumps(d, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"status": d["status"], "designated": d["designated"], "outputs": d["outputs"],
                      "stop_before_freeze": d["stop_before_freeze"], "fail_closed_statuses": d["fail_closed_statuses"],
                      "poll": d["poll"] if d["fail_closed_statuses"] else None,
                      "checks_failing": sorted(k for k, v in d["checks"].items() if v is not True),
                      "evidence_reasons": d["evidence_reasons"]}, sort_keys=True))
    return 0 if d["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
