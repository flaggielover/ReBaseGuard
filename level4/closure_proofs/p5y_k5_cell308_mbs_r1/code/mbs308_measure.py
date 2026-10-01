"""Cell-308 MB-S successor campaign (r1) -- the DESIGNATED pre-freeze measurement tool of the R-rules (the user's
section-11.2 ruling, option (a): owner supplement 1, part I, section 1; protocol section 11.2), and the measurement
functions the official qualification shares with it. Built by the non-holder builder6 (research brief 54, part B1).
Target-free: decoy cover cells 297 and 316 only (the guard stays DECOY and refuses the band); NOT frozen. It never
imports the driver, never touches a ref, never changes a system setting (queries only: vm_stat, ps, sysctl, pmset -g,
notifyutil -g, sw_vers, uname; the launchd job it bootstraps is the driver's own `decoy` mode).

What `designate` does, on the final reviewed pre-freeze bytes (HEAD, the namespace clean):
  1. the prepared-host readings: >= 10, >= 30 s apart (the rule's numbers), each with the power source, the driver's
     own `free_memory_bytes` (the function's own text, executed here), vm_stat wired-down pages and the page size, and
     every process the rules can use, with its EXECUTABLE PATH and %cpu (decimal text): every process above 25 %cpu
     (the smallest value EXCL_CPU_PCT can take) and every process of the hosting app;
  2. the official-configuration decoys, the SAME code path as QC02 / QC03's official form: the real driver's `decoy`
     for cell 297 (every block) and cell 316 (blocks 0-2), each as a transient LaunchAgent of the launchd launcher
     (code/mbs308_launch.py), the frozen ladder, WORKERS 5, the driver's then-current provisional MEM_CAP_BYTES (3 GiB)
     and MEM_POLL_S (2 s), as R-MEM step 1 states; one run at a time;
  3. compact DESIGNATED evidence `evidence_prefreeze/MBS308_RRULES_DESIGNATED.json`: the commit, the driver sha256,
     the platform readings, the boot UUID, the host provenance of the whole measurement and of each run, and every
     rule input (no certified decoy value is copied; the full decoy outputs stay under --work, their sha256 recorded).
It REFUSES (nothing run, nothing written) outside the campaign's qualified worktree and branch (the real driver is
never launched from a sandbox, a copy or another clone), when the tree is not the committed bytes, a campaign ref
exists, the host is on battery, the thermal-pressure level is not 0 at the start, the platform differs from the pins, a sleep channel is
unavailable or free disk is short. It marks the evidence INVALID (never designated; the invalid record is written under
--work only, never into the repository) when: a reading is not on AC power; a run's host provenance is not CLEAN (a
sleep on channel K, S or L, a battery reading, samples not covering the run); a ThermalEvent entry of the power log
falls in a run (READING-13: "thermal event" is the host module's ThermalEvent power-log entry; the thermal-pressure
level is recorded at every sample and gates only the start); the host is not prepared (a process above the threshold
that R-ALLOW can never admit must be QUIT by the operator: its basename and path class are reported; a threshold is
never raised for it); a run is not in the official configuration; a run's sampler record is not a valid step-6 input
(the largest OBSERVED spacing of its readings is above 0.5 s or not stated: readings R1, item 2; owner supplement 2,
section 5); a decoy failed; or any memory-watchdog event occurred.

A MEMORY-WATCHDOG EVENT in a designated run (R-MEM step 1: "not a valid input"; owner supplement 2, sections 2, 6 and
7): the tool reports STEP1_RERUN_REQUIRED and STOPS. It records what the rule's ONE re-run would be (the provisional
cap doubled: 6 GiB) and whether that cap is within the step-5 bound, computed by the rule function from the VALID
runs' figures (undefined when no valid run exists: the owner's open point, named). It runs nothing more: the driver
has, by design, no cap-override facility; no re-run limit, no further doubling and no other cap is inferred. If the
doubled cap is not within the bound: STOP AND REPORT BEFORE FREEZE.

The DESIGNATION RULE (a PROPOSAL of builder6, flagged for the review and the owner; protocol section 11.2, step 1):
the unit is the whole series of ONE invocation; an invocation that ends invalid designates nothing, its record stays
under --work as INVALID_<utc>_... and is listed (name, sha256, status, reasons) in every later record made with the
same --work; a later invocation measures the WHOLE series again (a single decoy is never re-measured into an existing
series and no run is ever selected among several); once a series is designated (the evidence file exists under
evidence_prefreeze/) the tool refuses to run again (ALREADY_DESIGNATED): there is no best-of-N.

READING-12 (protocol section 11.3; for the ratifier or a reviewer to confirm): "the hosting app that runs the launcher"
is the application bundle (the path up to the first `.app` component) of the nearest ancestor process of this tool
whose executable lies inside a bundle; it is read from the process ancestry, recorded with the ancestor chain, and
never taken from an argument.

    python3.14 -I -S -B mbs308_measure.py designate --work DIR      (the designated measurement; never a builder's)
    python3.14 -I -S -B mbs308_measure.py readings --out FILE       (read-only: one prepared-host series, FILE outside
                                                                      the repository; for the operator's preparation)
    python3.14 -I -S -B mbs308_measure.py designate --dev --work DIR   (decoy 297 block 0, dev ladder, 2 workers: a
                                                                      DEV record under --work only; never evidence)
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
import mbs308_derive as DV  # noqa: E402
import mbs308_host as HOST  # noqa: E402
import mbs308_rrules as RR  # noqa: E402

NS_REL = DV.NS_REL
DRIVER = "mbs308_driver.py"
MBS_REF_PREFIX = "refs/p5y-k5-cell308-mbs-r1/"
READINGS_N = RR.READINGS_MIN               # ">= 10 readings"
READINGS_SPACING_S = RR.READING_SPACING_S  # "30 s apart"
DECOY_LABEL = "decoy"
DEV_PLAN = {297: 1}                        # the dev form: decoy 297, block 0 (dev ladder, 2 workers); never evidence
DEV_WORKERS = 2
GENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1"}
_PCPU = re.compile(r"^\d+(\.\d+)?$")
_WIRED = re.compile(r"^Pages wired down:\s+(\d+)\.", re.M)
_PAGE = re.compile(r"page size of (\d+) bytes")


class MeasureRefusal(Exception):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(repo: Path, *args) -> str:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(repo), *args], capture_output=True,
                       text=True, env=GENV, stdin=subprocess.DEVNULL)
    return p.stdout.strip() if p.returncode == 0 else ""


# ------------------------------------------------------------------ the driver's own functions, from its TEXT
def driver_function(src: str, name: str, namespace: dict):
    """A module-level function of the driver, compiled from ITS OWN source segment (the driver is never imported: that
    would load the science modules). Used for `free_memory_bytes`: R-FREE says the value "is measured as the driver's
    own free_memory_bytes"."""
    found = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(found) != 1:
        raise MeasureRefusal("DRIVER_FUNCTION", f"{name} is defined {len(found)} time(s)")
    ns = dict(namespace)
    exec(compile("from __future__ import annotations\n" + ast.get_source_segment(src, found[0]), f"<driver:{name}>",
                 "exec"), ns)
    return ns[name]


# ------------------------------------------------------------------ one prepared-state reading
def parse_ps(text: str | None, self_pid: int) -> tuple:
    """(`ps -A -o pid=,ppid=,pcpu=,comm=` rows as {pid, ppid, pcpu, comm}, the number of rows read, the number
    excluded as this process tree). %cpu stays its DECIMAL TEXT; a row that does not parse is skipped, as the driver's
    busy_processes does. This process and its children are excluded (the reading's own `ps`, the caffeinate)."""
    if not text:
        return None, 0, 0
    rows, n, mine = [], 0, 0
    for ln in text.splitlines():
        parts = ln.split(None, 3)
        if len(parts) != 4 or not parts[0].isdigit() or not parts[1].isdigit() or not _PCPU.match(parts[2]):
            continue
        n += 1
        pid, ppid = int(parts[0]), int(parts[1])
        if pid == self_pid or ppid == self_pid:
            mine += 1
            continue
        rows.append({"pid": pid, "ppid": ppid, "pcpu": parts[2], "comm": parts[3].strip()})
    return rows, n, mine


def keep_procs(rows: list, hosting_app_paths) -> list:
    """The processes the rules can use: every process above 25 %cpu (R-EXCL-PCT's base, the smallest value EXCL_CPU_PCT
    can take; R-ALLOW (a) reads only processes above EXCL_CPU_PCT) and every process of the hosting app (R-EXCL-PCT
    reads its maximum). Each with its pid, executable path and %cpu text."""
    out = []
    for r in rows:
        host = RR._hosting(r["comm"], hosting_app_paths or [])
        if host or RR.pct(r["pcpu"]) > RR.EXCL_BASE_PCT:
            out.append({"pid": r["pid"], "comm": r["comm"], "pcpu": r["pcpu"], "hosting_app": host})
    return out


def reading(free_memory_bytes, hosting_app_paths, texts: dict | None = None, self_pid: int | None = None) -> dict:
    """One prepared-state reading. `texts` (tests only): planted {"vm_stat", "ps", "batt", "thermal", "pressure"}."""
    t = texts or {}
    vm = t["vm_stat"] if "vm_stat" in t else HOST._run(["/usr/bin/vm_stat"])
    ps = t["ps"] if "ps" in t else HOST._run([HOST.PS, "-A", "-o", "pid=,ppid=,pcpu=,comm="])
    rows, n, mine = parse_ps(ps, os.getpid() if self_pid is None else self_pid)
    w, pg = _WIRED.search(vm or ""), _PAGE.search(vm or "")
    return {"t_s": f"{time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)}/1000000000", "utc": utc(),
            "power": HOST.power_source(t.get("batt")), "free_memory_bytes": free_memory_bytes(vm),
            "wired_pages": int(w.group(1)) if w else None, "page_size_bytes": int(pg.group(1)) if pg else None,
            "thermal_level": HOST.thermal_level(t.get("thermal")),
            "memory_pressure": HOST.memory_pressure_level(t.get("pressure")),
            "processes_read": n if rows is not None else None, "own_process_tree_excluded": mine,
            "procs": keep_procs(rows, hosting_app_paths) if rows is not None else None}


def take_readings(one, n: int = READINGS_N, spacing_s: float = READINGS_SPACING_S, sleep=time.sleep,
                  clock=time.monotonic) -> list:
    """`n` readings, each at least `spacing_s` after the previous one (the rule: >= 10, 30 s apart)."""
    out, last = [], None
    for _ in range(n):
        if last is not None:
            while clock() - last < spacing_s:
                sleep(min(1.0, max(0.01, spacing_s - (clock() - last))))
        last = clock()
        out.append(one())
    return out


def reading_reasons(readings) -> list:
    """Why a series cannot feed the rules (beyond the rule functions' own checks): an unreadable field."""
    r = []
    for i, x in enumerate(readings if isinstance(readings, list) else []):
        for k in ("free_memory_bytes", "wired_pages", "page_size_bytes", "procs", "power"):
            if not isinstance(x, dict) or x.get(k) is None:
                r.append(f"READING_{i}_{k.upper()}_UNREADABLE")
    return r


# ------------------------------------------------------------------ the hosting app (READING-12)
def process_comm(pid: int) -> str | None:
    t = (HOST._run([HOST.PS, "-p", str(int(pid)), "-o", "comm="]) or "").strip()
    return t or None


def bundle_of(comm: str | None) -> str | None:
    """The application bundle an executable lies in: the path up to and including the FIRST `.app` component."""
    if not comm or not comm.startswith("/"):
        return None
    parts = comm.split("/")
    for i, p in enumerate(parts[:-1]):
        if p.endswith(".app"):
            return "/".join(parts[:i + 1])
    return None


def hosting_app(pid: int | None = None, comm_of=process_comm, ppid_of=None, limit: int = 64) -> dict:
    """READING-12: the bundle of the nearest ancestor of `pid` (this process) whose executable lies inside an
    application bundle. {"paths": [bundle + "/"] or [], "chain": [{pid, comm, bundle}]}."""
    ppid_of = ppid_of or HOST.process_ppid
    chain, cur, found = [], os.getppid() if pid is None else pid, None
    while cur and cur > 1 and len(chain) < limit:
        comm = comm_of(cur)
        b = bundle_of(comm)
        chain.append({"pid": cur, "comm": comm, "bundle": b})
        if b and found is None:
            found = b
        cur = ppid_of(cur)
    return {"paths": [found + "/"] if found else [], "chain": chain}


# ------------------------------------------------------------------ one official-configuration decoy under launchd
def decoy_program(interpreter: str, driver: Path, cell: int, first_blocks, workers: int, out: Path,
                  dev_ladder: bool = False) -> list:
    args = [interpreter, "-I", "-S", "-B", str(driver), "decoy", "--cell", str(cell), "--workers", str(workers),
            "--out", str(out)]
    if first_blocks is not None:
        args += ["--first-blocks", str(first_blocks)]
    if dev_ladder:
        args += ["--dev-ladder"]
    return args


def run_under_launchd(L, program: list, label: str, *, plist_dir: Path, log_dir: Path, workdir: Path,
                      record_dir: Path, env_extra: dict | None = None) -> dict:
    """Bootstrap `program` as a transient LaunchAgent through the launcher's own `launch` (the detachment proof
    included), wait until its RECORDED identity is positively dead, boot it out and remove the plist. A job whose
    identity was never recorded is never booted out here (the launcher's rule): the run is then reported as failed."""
    rec = L.launch(program, label, plist_dir, log_dir, workdir, record_dir=record_dir, env_extra=env_extra)
    out = {"label": label, "observed": rec.get("observed"), "pid": rec.get("pid"),
           "detached": (rec.get("detachment") or {}).get("detached"), "boot_uuid": rec.get("boot_uuid"),
           "launched_utc": rec.get("launched_utc")}
    if not rec.get("identity"):
        return dict(out, finished=False, error="JOB_IDENTITY_NOT_RECORDED")
    fin = L.wait_and_cleanup(label, rec["plist"], rec["identity"])
    return dict(out, finished=True, last_exit=fin.get("last_exit"), booted_out=fin.get("booted_out"))


def load_json(path: Path):
    try:
        return json.loads(Path(path).read_bytes())
    except (OSError, ValueError):
        return None


def run_decoy(L, *, interpreter: str, driver: Path, cell: int, first_blocks, workers: int, out: Path, run_id: str,
              label: str, plist_dir: Path, log_dir: Path, workdir: Path, record_dir: Path, dev_ladder: bool = False,
              program: list | None = None, env_extra: dict | None = None) -> dict:
    """One decoy run under the launchd launcher and its COMPACT record (DV.compact_run). `program` (tests only): a
    synthetic payload in place of the driver."""
    out.unlink(missing_ok=True)
    prog = program or decoy_program(interpreter, driver, cell, first_blocks, workers, out, dev_ladder)
    job = run_under_launchd(L, prog, label, plist_dir=plist_dir, log_dir=log_dir, workdir=workdir,
                            record_dir=record_dir, env_extra=env_extra)
    rec = load_json(out)
    exit_code = int(job["last_exit"]) if str(job.get("last_exit") or "").lstrip("-").isdigit() else job.get("last_exit")
    if rec is None:
        return {"id": run_id, "cell": cell, "job": job, "exit": exit_code, "record_missing": True}
    return dict(DV.compact_run(rec, run_id, exit_code=exit_code, raw_sha256=sha(out.read_bytes())), job=job,
                raw_path=str(out))


def run_reasons(run: dict, plan: dict, *, cap: int, poll, official: bool = True) -> list:
    """Why ONE run cannot be an input of the rules or of Q12 (empty = valid): no record, not the official
    configuration (the rule function's own step-1 reasons and the plan), a memory-watchdog event, a failed decoy, a
    sampler record that is not a valid step-6 input (the OBSERVED spacing above 0.5 s, or not stated), host provenance
    not CLEAN (sleep on K / S / L, battery, samples not covering the run), a ThermalEvent power-log entry in the run
    (READING-13), or the job not properly launched / detached / finished. `official`: the run must be in the official
    configuration (False only for the dev form)."""
    if run.get("record_missing"):
        return ["RECORD_MISSING"]
    r = list(RR._run_reasons(DV.run_input(run), cap, poll)) if official else []
    if not official and RR.cap_events(run.get("watchdog_events")):
        r.append("MEMORY_WATCHDOG_EVENT")
    r += DV.plan_reasons(run, plan)
    r += RR.sampler_reasons(run.get("rss_sampler"))
    job = run.get("job") or {}
    if job.get("finished") is not True or job.get("detached") is not True or job.get("booted_out") is not True:
        r.append("JOB_NOT_LAUNCHED_DETACHED_AND_FINISHED")
    h = run.get("host") if isinstance(run.get("host"), dict) else {}
    try:
        st = HOST.assess(h.get("start"), h.get("end"), h.get("samples"), h.get("events"))["status"]
    except Exception:                                                  # noqa: BLE001 (fails closed)
        st = "AMBIGUOUS"
    if st != "CLEAN" or (h.get("assessment") or {}).get("status") != "CLEAN":
        r.append(f"HOST_PROVENANCE_{st if st != 'CLEAN' else 'STORED_ASSESSMENT_DIFFERS'}")
    te = h.get("thermal_events")
    if not isinstance(te, list):
        r.append("THERMAL_EVENTS_UNREADABLE")
    elif te:
        r.append("THERMAL_EVENT_DURING_RUN")
    return sorted(set(r))


def not_prepared(rules: dict) -> list:
    """The processes that make a reading series NOT a prepared-host series: above the threshold and never admissible
    by R-ALLOW. Basename and path class only (the operator quits them; a threshold is never raised)."""
    out = []
    for x in (rules.get("r_allow") or {}).get("rejected") or []:
        row = {"name": RR.basename(str(x.get("path", ""))), "path_class": x.get("reason")}
        if row not in out:
            out.append(row)
    return out


# ------------------------------------------------------------------ the designated measurement
def identity_reasons(repo: Path, driver_src: str) -> list:
    """The real driver is launched ONLY in the campaign's qualified worktree (the driver's own QUALIFIED_WORKTREE,
    QUALIFIED_GIT_DIR, QUALIFIED_COMMON_DIR and QUALIFIED_BRANCH, read from its text): never in a sandbox, a copy or
    another clone. Empty = this repository is the qualified worktree on the qualified branch."""
    want = {}
    for n in ast.parse(driver_src).body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and \
                n.targets[0].id.startswith("QUALIFIED_") and isinstance(n.value, ast.Constant):
            want[n.targets[0].id] = n.value.value
    if set(want) != {"QUALIFIED_WORKTREE", "QUALIFIED_GIT_DIR", "QUALIFIED_COMMON_DIR", "QUALIFIED_BRANCH"}:
        return ["QUALIFIED_IDENTITY_UNREADABLE"]
    gd = git(repo, "rev-parse", "--path-format=absolute", "--git-dir")
    cd = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    r = []
    if str(Path(repo).resolve()) != want["QUALIFIED_WORKTREE"] or not gd or not cd or \
            str(Path(gd).resolve()) != want["QUALIFIED_GIT_DIR"] or \
            str(Path(cd).resolve()) != want["QUALIFIED_COMMON_DIR"]:
        r.append("NOT_THE_QUALIFIED_WORKTREE")
    if git(repo, "symbolic-ref", "-q", "HEAD") != want["QUALIFIED_BRANCH"]:
        r.append("NOT_THE_QUALIFIED_BRANCH")
    return r


def preflight(ns: Path, repo: Path, work: Path) -> dict:
    """Refuses unless the measured bytes are the committed bytes and the host can carry a valid measurement."""
    import mbs308_repin as RP
    import mbs308_scratch as SCR
    out = {"commit": git(repo, "rev-parse", "HEAD"),
           "namespace_clean": git(repo, "status", "--porcelain", "--untracked-files=all", "--", NS_REL) == "" and
           bool(git(repo, "rev-parse", "HEAD")),
           "tracked_clean": git(repo, "status", "--porcelain", "--untracked-files=no") == "",
           "no_campaign_refs": git(repo, "for-each-ref", "--format=%(refname)", MBS_REF_PREFIX) == "",
           "power": HOST.power_source(), "thermal_level": HOST.thermal_level(),
           "memory_pressure": HOST.memory_pressure_level(), "lowpowermode": HOST.lowpowermode(),
           "boot_uuid": HOST.boot_session_uuid(),
           "sleep_channels_available": HOST.kern_times() is not None and HOST.log_events(0, 0) is not None}
    try:
        plat = RP.platform_status(ns / "code")
        out["platform"] = {"differs": plat["differs"], "unreadable": plat["unreadable"],
                           "readings": {k: v["reading"] for k, v in plat["pins"].items()}}
    except Exception as exc:                                           # noqa: BLE001
        out["platform"] = {"differs": ["UNREADABLE"], "unreadable": [type(exc).__name__], "readings": {}}
    disk = SCR.check_free([(work, SCR.QUAL_MIN_FREE_BYTES), (repo, HOST.MIN_FREE_DISK)], "designated measurement")
    out["disk"] = {"pass": disk["pass"], "free_bytes": [r["free_bytes"] for r in disk["readings"]]}
    gates = {"NAMESPACE_NOT_THE_COMMITTED_BYTES": out["namespace_clean"] and out["tracked_clean"],
             "CAMPAIGN_REF_EXISTS": out["no_campaign_refs"], "HOST_NOT_ON_AC": out["power"] == HOST.AC,
             "THERMAL_LEVEL_NOT_0_AT_START": out["thermal_level"] == 0,
             "MEMORY_PRESSURE_NOT_NORMAL": out["memory_pressure"] == HOST.MEMORY_PRESSURE_NORMAL,
             "LOW_POWER_MODE": out["lowpowermode"] == 0, "BOOT_UUID_UNREADABLE": bool(out["boot_uuid"]),
             "SLEEP_CHANNELS_UNAVAILABLE": out["sleep_channels_available"],
             "PLATFORM_DIFFERS_FROM_PINS": not out["platform"]["differs"] and not out["platform"]["unreadable"],
             "DISK": out["disk"]["pass"]}
    out["refusals"] = sorted(k for k, v in gates.items() if v is not True)
    return out


def step1_rerun_report(rules: dict) -> dict:
    """What the designated measurement reports when a run had a memory-watchdog event (owner supplement 2, sections 2
    and 7; readings R1, item 5 (a)): the run(s) to re-run, the rule's ONE re-run cap (the provisional cap doubled) and
    whether it is within the step-5 bound -- all the rule function's own figures, from the VALID runs. Nothing is run."""
    mem = rules.get("r_mem") or {}
    return {"status": RR.STATUS_STEP1_RERUN, "r_mem_status": mem.get("status"),
            "event_runs": mem.get("uncured_event_runs"), "rerun_required": mem.get("rerun_required"),
            "rerun_step5_bound": mem.get("rerun_step5_bound"),
            "facility": "NONE: the driver has no cap-override facility; nothing is re-run by this tool",
            "ruling": "owner supplement 2, sections 2, 6 and 7: only the rule's one re-run at the doubled provisional "
                      "cap, within the step-5 bound; if it does not fit: STOP AND REPORT BEFORE FREEZE; no re-run "
                      "limit, no further doubling, nothing inferred"}


def prior_invalid(work: Path) -> list:
    """The invalid series already recorded under --work (the proposed designation rule: each is kept and listed)."""
    out = []
    for f in sorted(Path(work).glob("INVALID_*" + DV.EVIDENCE_NAME)):
        rec = load_json(f)
        raw = f.read_bytes()
        out.append({"name": f.name, "sha256": sha(raw), "status": (rec or {}).get("status"),
                    "invalid_reasons": (rec or {}).get("invalid_reasons")})
    return out


def measure(*, ns: Path, repo: Path, work: Path, L, plan: dict, workers: int, dev: bool, base_names, h3_readings,
            one_reading=None, program_for=None, env_extra: dict | None = None, label_prefix: str | None = None,
            log_dir: Path | None = None, pre: dict | None = None, n_readings: int = READINGS_N,
            spacing_s: float = READINGS_SPACING_S, hosting: dict | None = None, sleep=time.sleep) -> dict:
    """The measurement itself (after `preflight`): the readings, then the planned decoys one at a time, then the
    evidence record. `one_reading`, `program_for`, `hosting`, `label_prefix`, `log_dir`, `spacing_s`: test plants (a
    planted run is never designated: `dev` must be True with any of them)."""
    planted = any(x is not None for x in (one_reading, program_for, hosting, env_extra)) or \
        (n_readings, spacing_s) != (READINGS_N, READINGS_SPACING_S)
    if planted and not dev:
        raise MeasureRefusal("PLANTED_INPUT", "a planted input is never a designated measurement")
    code = ns / "code"
    src = (code / DRIVER).read_text()
    const = DV.driver_constants(src)
    cap, poll = const["MEM_CAP_BYTES"], F(const["MEM_POLL_S"])
    t0 = utc()
    awake = HOST.keep_awake()
    h0, smp = HOST.snapshot(), HOST.Sampler().start()
    hosting = hosting or hosting_app()
    fmb = driver_function(src, "free_memory_bytes", {"HOST": HOST})
    one = one_reading or (lambda: reading(fmb, hosting["paths"]))
    readings = take_readings(one, n_readings, spacing_s, sleep=sleep)
    hw = (HOST._run([HOST.SYSCTL, "-n", "hw.memsize"]) or "").strip()
    hw = int(hw) if hw.isdigit() else None
    invalid = list(reading_reasons(readings))
    if any(not isinstance(x, dict) or x.get("power") != HOST.AC for x in readings):
        invalid.append("READING_NOT_ON_AC")
    # the host-state rules on the readings alone: is this a prepared host?
    pre_rules = DV.apply_rules(runs=[], readings=readings, hw_memsize_bytes=hw, hosting_app_paths=hosting["paths"],
                               base_names=base_names, h3_readings=h3_readings, plan=plan, workers=workers,
                               mem_poll_s=poll, measurement_cap_bytes=cap, measurement_poll_s=poll)
    for k in ("r_excl_pct", "r_allow"):
        if pre_rules[k].get("valid") is not True:
            invalid.append(f"{k.upper()}_{pre_rules[k].get('status')}")
    unprepared = not_prepared(pre_rules)
    status = "MEASURED"
    if unprepared:
        invalid.append("HOST_NOT_PREPARED")
        status = "HOST_NOT_PREPARED"
    runs, step1 = [], None
    prior = prior_invalid(work)
    plist_dir, rec_dir, raw_dir = work / "launch", work / "launch_records", work / "raw"
    for d in (plist_dir, rec_dir, raw_dir):
        d.mkdir(parents=True, exist_ok=True)
    if not invalid:                                   # the decoys run only on a prepared host with valid readings
        for cell in sorted(plan):
            run_id = f"decoy{cell}"
            out = raw_dir / f"MBS308_DECOY_{cell}.json"
            label = (label_prefix or L.LABEL_PREFIX) + f"{DECOY_LABEL}{cell}.{L.utc_compact()}"
            run = run_decoy(L, interpreter=L.PYTHON, driver=code / DRIVER, cell=cell, first_blocks=plan[cell],
                            workers=workers, out=out, run_id=run_id, label=label, plist_dir=plist_dir,
                            log_dir=log_dir or L.LOG_DIR, workdir=repo, record_dir=rec_dir, dev_ladder=dev,
                            program=None if program_for is None else program_for(cell, out), env_extra=env_extra)
            why = run_reasons(run, plan, cap=cap, poll=poll, official=not dev)
            run["invalid_reasons"] = why
            runs.append(run)
            invalid += [f"{run_id}:{w}" for w in why]
            if RR.cap_events(run.get("watchdog_events")):     # R-MEM step 1: not a valid input; report and STOP
                status = RR.STATUS_STEP1_RERUN
                invalid.append(f"{run_id}:{RR.STATUS_STEP1_RERUN}")
                step1 = step1_rerun_report(DV.apply_rules(
                    runs=runs, readings=readings, hw_memsize_bytes=hw, hosting_app_paths=hosting["paths"],
                    base_names=base_names, h3_readings=h3_readings, plan=plan, workers=workers, mem_poll_s=poll,
                    measurement_cap_bytes=cap, measurement_poll_s=poll))
                break
    h1 = HOST.snapshot()
    host = dict(HOST.provenance(h0, smp.stop(), h1), keep_awake=awake)
    if host["assessment"].get("status") != "CLEAN":
        invalid.append(f"MEASUREMENT_HOST_PROVENANCE_{host['assessment'].get('status')}")
    if h0.get("boot_uuid") != h1.get("boot_uuid") or not h1.get("boot_uuid"):
        invalid.append("BOOT_UUID_CHANGED_OR_UNREADABLE")
    if dev:
        invalid.append("DEV_FORM_NEVER_DESIGNATED")
    invalid = sorted(set(invalid))
    return {"schema": DV.EVIDENCE_SCHEMA, "designated": not invalid and status == "MEASURED" and not dev,
            "label": "DEV (never evidence; delete after use)" if dev else
            "DESIGNATED PRE-FREEZE R-RULE MEASUREMENT (owner supplement 1, part I, section 1)",
            "status": status, "invalid_reasons": invalid, "host_not_prepared": unprepared, "step1_rerun": step1,
            "prior_invalid_series": prior,
            "commit": (pre or {}).get("commit"), "driver_sha256": sha((code / DRIVER).read_bytes()),
            "tool_sha256": sha(HERE.read_bytes()), "rules_sha256": sha((code / "mbs308_rrules.py").read_bytes()),
            "launcher_sha256": sha((code / "mbs308_launch.py").read_bytes()),
            "preflight": pre, "boot_uuid": h1.get("boot_uuid"), "hw_memsize_bytes": hw, "hosting_app": hosting,
            "configuration": {"plan": {str(k): v for k, v in sorted(plan.items())}, "workers": workers,
                              "ladder": "dev" if dev else "frozen", "mem_cap_bytes": cap,
                              "mem_poll_s": RR.fstr(poll), "one_run_at_a_time": True},
            "readings": readings, "runs": [{k: v for k, v in r.items() if k != "raw_path"} for r in runs],
            "raw_outputs_outside_the_repository": {r["id"]: {"sha256": r.get("raw_sha256")} for r in runs},
            "host": host, "started_utc": t0, "finished_utc": utc(), "target_evaluations": 0,
            "ledger_class": "NONTARGET_DRIFT_VALIDATION"}


def designate(work: Path, *, dev: bool = False, ns: Path = NS, repo: Path = REPO, out_dir: Path | None = None) -> tuple:
    """(exit code, summary). Official form: the evidence is written to `evidence_prefreeze/` ONLY when it is
    designated; an invalid or DEV record goes under --work."""
    import mbs308_launch as L
    work = work.resolve()
    if work.is_relative_to(repo.resolve()):
        raise MeasureRefusal("WORK_INSIDE_THE_REPOSITORY")
    ident = identity_reasons(repo, (ns / "code" / DRIVER).read_text())
    if ident:                                 # either form launches the REAL driver: the qualified worktree only
        return 2, {"refused": ident, "nothing_run": True}
    designated = (out_dir or ns / "evidence_prefreeze") / DV.EVIDENCE_NAME
    if not dev and os.path.lexists(designated):       # the proposed designation rule: one designated series, no best-of-N
        return 2, {"refused": ["ALREADY_DESIGNATED"], "nothing_run": True}
    work.mkdir(parents=True, exist_ok=True)
    pre = preflight(ns, repo, work)
    if pre["refusals"] and not dev:
        return 2, {"refused": pre["refusals"], "nothing_run": True}
    if dev and "HOST_NOT_ON_AC" in pre["refusals"]:
        return 2, {"refused": ["HOST_NOT_ON_AC"], "nothing_run": True}
    cfg = json.loads((ns / "config" / "MBS308_QUALIFICATION_CASES.json").read_text())
    const = DV.driver_constants((ns / "code" / DRIVER).read_text())
    plan = dict(DEV_PLAN) if dev else DV.plan_of(cfg)
    ev = measure(ns=ns, repo=repo, work=work, L=L, plan=plan, workers=DEV_WORKERS if dev else const["WORKERS"],
                 dev=dev, base_names=DV.base_names_of(cfg, repo), h3_readings=cfg["r_allow_h3_readings"]["readings"],
                 pre=pre)
    text = json.dumps(ev, indent=1, sort_keys=True) + "\n"
    if ev["designated"]:
        dst = designated
        dst.parent.mkdir(parents=True, exist_ok=True)
    else:                                     # an invalid series is KEPT (never overwritten) and listed by the next one
        dst = work / ("DEV_" + DV.EVIDENCE_NAME if dev else
                      f"INVALID_{len(prior_invalid(work)) + 1:03d}_{L.utc_compact()}_{DV.EVIDENCE_NAME}")
        if not dev and os.path.lexists(dst):
            raise MeasureRefusal("INVALID_RECORD_EXISTS", dst.name)
    dst.write_text(text)
    return (0 if ev["designated"] else (0 if dev else 3)), {
        "designated": ev["designated"], "status": ev["status"], "invalid_reasons": ev["invalid_reasons"],
        "host_not_prepared": ev["host_not_prepared"], "step1_rerun": ev["step1_rerun"],
        "prior_invalid_series": len(ev["prior_invalid_series"]), "written": str(dst), "sha256": sha(text.encode())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("designate", "readings"))
    ap.add_argument("--work", help="designate: directory OUTSIDE the repository (plists, launch records, raw outputs)")
    ap.add_argument("--dev", action="store_true", help="designate: the dev form (297 block 0, dev ladder; never evidence)")
    ap.add_argument("--out", help="readings: output file OUTSIDE the repository")
    a = ap.parse_args(argv)
    try:
        if a.what == "readings":
            if not a.out or Path(a.out).resolve().is_relative_to(REPO.resolve()):
                raise MeasureRefusal("OUT", "readings needs --out FILE outside the repository")
            src = (CODE / DRIVER).read_text()
            hosting = hosting_app()
            fmb = driver_function(src, "free_memory_bytes", {"HOST": HOST})
            rs = take_readings(lambda: reading(fmb, hosting["paths"]))
            Path(a.out).write_text(json.dumps({"label": "prepared-host readings (read-only; never evidence)",
                                               "hosting_app": hosting, "readings": rs, "utc": utc()}, indent=1,
                                              sort_keys=True) + "\n")
            print(json.dumps({"readings": len(rs), "written": a.out}))
            return 0
        if not a.work:
            raise MeasureRefusal("WORK", "designate needs --work DIR outside the repository")
        rc, summary = designate(Path(a.work), dev=a.dev)
    except (MeasureRefusal, DV.DeriveRefusal) as e:
        print(f"MBS308 MEASURE REFUSED {e}")
        return 2
    print(json.dumps(summary, indent=1, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main())
