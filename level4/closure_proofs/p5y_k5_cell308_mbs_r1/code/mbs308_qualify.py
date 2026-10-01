"""Cell-308 MB-S successor campaign (r1) -- the qualification verifier FRAMEWORK (cases in
config/MBS308_QUALIFICATION_CASES.json), modelled on MB r1's mb308_qualify. Built by the non-holder builder4 (research
brief 46). NOT frozen: nothing here authorises a freeze, a qualification run or any target step.

It can NEVER evaluate cell 308 (or 305-307, 309), and no BUILT case computes with the real science:
* the suites run in `git clone --shared` sandboxes of a SEPARATE `--no-local` base store under --work, with the
  synthetic evaluator and the synthetic launchd payload;
* QC09-S imports only the guard module and arms it in a throw-away git repository under --work;
* QC11-S reads source text; QC12-S counts pattern / token hits (counts and file names only, never a value); QC13-S
  checks governance records by commit and path (verdict line, pinned sha256 or a named ledger line; nothing printed);
* Q8-S hashes files; R_RULES_CONTROLS runs planted inputs (and committed text) through code/mbs308_rrules.py.
Every case that differs between the options of the user's pending decisions MBS-7 / MBS-8, or depends on how the
official decoys are sequenced relative to the freeze (protocol section 11), is DECLARED and returns
{"pass": false, "status": "PENDING_USER_DECISION", "depends_on": [...]}: no qualification can pass before those
cases are built after the decisions.

Modes
  official   HEAD must be the freeze commit; no review / grant / result / marker / campaign ref / spool result; the
             namespace clean (ignored files included); the host ready (protocol section 8 preflight gates without the
             launcher, the platform pins, AC, sleep channels). Writes qualification/MBS308_QUALIFICATION.json and the
             suite records next to it, nothing else in the repository.
  --review   HEAD = freeze or the qualification commit on it; writes only --out (outside the repository); the suites
             are re-summarised from the committed records unless --heavy.
  --dev      development only (never evidence): any HEAD, only the cases named by --only, writes only --out. Its
             report carries dev_mode = true and pass = false by construction of the aggregation.
Every case summary carries a boolean `pass`; the aggregator fails LOUDLY on a missing or non-boolean `pass`, on a case
of the configuration that did not run (official / review) and on a case the configuration does not know.

    python3.14 -I -S -B mbs308_qualify.py --work DIR                                   (official)
    python3.14 -I -S -B mbs308_qualify.py --review --work DIR --out FILE [--heavy]
    python3.14 -I -S -B mbs308_qualify.py --dev --work DIR --only QC09-S,QC11-S --out FILE
"""
from __future__ import annotations

import argparse
import ast
import datetime
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
import mbs308_rrules as RR  # noqa: E402
import mbs308_scratch as SCR  # noqa: E402

CP = "level4/closure_proofs/"
NS_REL = CP + "p5y_k5_cell308_mbs_r1"
NSF_REL = CP + "p5y_k5_cell308_mb_r1"
RS = CP + "p5y_k5_cell308_research/"
CONFIG = NS / "config" / "MBS308_QUALIFICATION_CASES.json"
QDIR = NS / "qualification"
QUAL_NAME = "MBS308_QUALIFICATION.json"
MANIFEST_REL = NS_REL + "/protocol/MBS308_FREEZE.json"
GUARD_REL = NS_REL + "/code/mbs308_guard.py"
GUARD_FIELD = ("guard", "cell308_cover")          # the successor manifest's guard-geometry field (QC12-S exemption)
SCHEMA = "rebaseguard.p5y.k5.cell308-mbs-r1.qualification.v1"
PY = sys.executable
FLAGS = ["-I", "-S", "-B"]
ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1",
       "HOME": os.environ.get("HOME", "/var/empty")}
SCIENCE_BASE_COMMIT = "21e99cf05d60b985e33f337aa4c5a7fd1507402a"
MBR1_MARKER_REF = "refs/p5y-k5-cell308-mb-r1/target-consumed"
MBS_REF_PREFIX = "refs/p5y-k5-cell308-mbs-r1/"
# the sanctioned tail-figure pattern file of the research scanner r2 (MB r1's pin; read at RUN TIME only)
PATTERNS_PIN = (RS + "ledger/TAIL_FIGURE_PATTERNS.json",
                "0dc2addcd6ac667c6866736ab913a2513b6ec848636d2fbb04051d02ab49cbf5", "ab0104c6b534")
EXTERNAL_PINS = {"qualify:tail_patterns": PATTERNS_PIN}          # listed by the manifest writer
TIMING_KEYS = frozenset({"seconds", "wall_seconds", "cpu_seconds"})     # MB r1's QC04 / QC12 set, unchanged
PRE_GRANT_CLASSES = frozenset({"HISTORICAL_READ", "HISTORICAL_RECONSTRUCTION", "PRUNING_FROM_COMMITTED",
                               "INFRASTRUCTURE", "SYNTHETIC_VALIDATION", "NONTARGET_DRIFT_VALIDATION",
                               "NONTARGET_REAL_VALIDATION", "THEORY", "REVIEW"})
PENDING_STATUS = "PENDING_USER_DECISION"
SUITE_CASES = ("QS-STATIC", "QS-STATE", "QS-CRASH", "QS-LAUNCH", "QS-QUALIFY", "QS-DISK")
BUILT_CASES = SUITE_CASES + ("QS-MUTANTS", "QC09-S", "QC11-S", "QC12-S", "QC13-S", "Q8-S", "R_RULES_CONTROLS",
                             "QS-RESUME-DECOY")
RESUME_DECOY_RUNNER = "tests/mbs308_resume_decoy.py"        # QS-RESUME-DECOY's case runner (brief 50)
SEQ = "SEQUENCING (protocol section 11)"
PENDING_CASES = {       # case -> the decisions it depends on (config/MBS308_QUALIFICATION_CASES.json says why)
    "QC01": ("MBS-7",), "QC02": ("MBS-7", "MBS-8"), "QC03": ("MBS-7", "MBS-8"), "QC04": ("MBS-7",),
    "QC05": ("MBS-7",), "QC06": ("MBS-7",), "QC07": ("MBS-7",), "QC08": ("MBS-7", "MBS-8"), "Q1_theory": ("MBS-7",),
    "QC09-SCI": ("MBS-7",), "MBR1_REPRO": ("MBS-7",),
    "Q12_caps": ("MBS-8", SEQ), "R_RULES_OFFICIAL": ("MBS-8", SEQ)}
REQUIRED_FILES = ("code/mbs308_driver.py", "code/mbs308_guard.py", "code/mbs308_host.py", "code/mbs308_state.py",
                  "code/mbs308_launch.py", "code/mbs308_qualify.py", "code/mbs308_manifest.py",
                  "code/mbs308_rrules.py", "code/mbs308_scratch.py", "code/mbs308_repin.py",
                  "config/MBS308_QUALIFICATION_CASES.json", "GUARD_DIFF.md",
                  "DRIVER_DIFF.md")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob_id(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(*args, repo: Path = None) -> str:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(repo or REPO), *args], capture_output=True,
                       text=True, env=ENV, stdin=subprocess.DEVNULL)
    return p.stdout.strip() if p.returncode == 0 else ""


def git_rc(*args, repo: Path = None) -> int:
    return subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(repo or REPO), *args],
                          capture_output=True, env=ENV, stdin=subprocess.DEVNULL).returncode


def git_show_bytes(commit: str, rel: str, repo: Path = None) -> bytes | None:
    b = git("rev-parse", "-q", "--verify", f"{commit}:{rel}", repo=repo)
    if not b:
        return None
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(repo or REPO), "cat-file", "blob", b],
                       capture_output=True, env=ENV, stdin=subprocess.DEVNULL)
    return p.stdout if p.returncode == 0 else None


def load_config(path: Path = None) -> dict:
    return json.loads(Path(path or CONFIG).read_text())


_D: dict = {}


def driver():
    """The successor driver, imported lazily (it loads MB r1's science modules from their pinned bytes; nothing is
    computed). Cases that need only source text never import it."""
    if "D" not in _D:
        import mbs308_driver as D
        _D["D"] = D
    return _D["D"]


def module_constants(src: str) -> dict:
    """Top-level constants of a module's SOURCE: literals, str concatenations of earlier constants, tuples, dicts and
    frozenset / set / tuple calls of those. Anything else is skipped (never executed)."""
    env: dict = {}

    def ev(n):
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            return env[n.id]
        if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Mult, ast.Pow)):
            a, b = ev(n.left), ev(n.right)
            return a + b if isinstance(n.op, ast.Add) else (a * b if isinstance(n.op, ast.Mult) else a ** b)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -ev(n.operand)
        if isinstance(n, ast.Tuple):
            return tuple(ev(e) for e in n.elts)
        if isinstance(n, ast.List):
            return [ev(e) for e in n.elts]
        if isinstance(n, ast.Set):
            return {ev(e) for e in n.elts}
        if isinstance(n, ast.Dict):
            return {ev(k): ev(v) for k, v in zip(n.keys, n.values)}
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("frozenset", "set", "tuple") \
                and len(n.args) == 1 and not n.keywords:
            return {"frozenset": frozenset, "set": set, "tuple": tuple}[n.func.id](ev(n.args[0]))
        raise ValueError(type(n).__name__)
    for node in ast.parse(src).body:
        tgt = node.targets if isinstance(node, ast.Assign) else ([node.target] if isinstance(node, ast.AnnAssign)
                                                                 and node.value is not None else [])
        if len(tgt) == 1 and isinstance(tgt[0], ast.Name):
            try:
                env[tgt[0].id] = ev(node.value)
            except (ValueError, TypeError, KeyError, ArithmeticError):
                pass
    return env


def post_freeze_dirs(code: Path = None) -> tuple:
    return tuple(module_constants(((code or CODE) / "mbs308_driver.py").read_text())["POST_FREEZE_DIRS"])


# ------------------------------------------------------------------ declared (option-dependent) cases
def pending(case_id: str) -> dict:
    """An option-dependent case: DECLARED, not built; it fails closed until it is built after the user's decisions."""
    return {"pass": False, "status": PENDING_STATUS, "depends_on": list(PENDING_CASES[case_id]), "case": case_id}


# ------------------------------------------------------------------ aggregation
def config_consistency(cfg: dict) -> dict:
    """The configuration and this verifier agree: every configured case is BUILT here or DECLARED pending here (with
    the same status and dependencies), every case of this verifier is configured, every gate has a case and every
    case names known gates."""
    ids = [c["id"] for c in cfg.get("cases", [])]
    known = set(BUILT_CASES) | set(PENDING_CASES)
    status_bad = sorted(c["id"] for c in cfg.get("cases", []) if c["id"] in known and
                        c.get("status") != ("BUILT" if c["id"] in BUILT_CASES else PENDING_STATUS))
    deps_bad = sorted(c["id"] for c in cfg.get("cases", []) if c["id"] in PENDING_CASES and
                      tuple(c.get("depends_on") or ()) != PENDING_CASES[c["id"]])
    gates = set(cfg.get("gates", {}))
    used = {g for c in cfg.get("cases", []) for g in c.get("gates", [])}
    out = {"duplicate_ids": sorted({i for i in ids if ids.count(i) > 1}),
           "unknown_in_config": sorted(set(ids) - known), "missing_from_config": sorted(known - set(ids)),
           "status_mismatch": status_bad, "depends_on_mismatch": deps_bad,
           "gates_without_cases": sorted(gates - used), "unknown_gates": sorted(used - gates)}
    out["pass"] = not any(out.values())
    return out


def aggregate(cases: dict, cfg: dict, mode: str) -> dict:
    """Gates from the configuration; every case summary must carry a boolean `pass`. A missing / non-boolean `pass`,
    a configured case that did not run (official / review) or an unknown case fails LOUDLY (listed and printed)."""
    cons = config_consistency(cfg)
    missing_pass = sorted(k for k, v in cases.items() if not isinstance(v, dict) or not isinstance(v.get("pass"), bool))
    ids = [c["id"] for c in cfg.get("cases", [])]
    not_run = sorted(i for i in ids if i not in cases) if mode != "dev" else []
    unknown = sorted(k for k in cases if k not in ids)
    gates = {}
    for g in sorted(cfg.get("gates", {})):
        members = [c["id"] for c in cfg["cases"] if g in c.get("gates", [])]
        gates[g] = {"cases": members, "pass": bool(members) and all(
            isinstance(cases.get(m), dict) and cases[m].get("pass") is True for m in members)}
    pend = sorted(k for k, v in cases.items() if isinstance(v, dict) and v.get("status") == PENDING_STATUS)
    for k in missing_pass:
        print(f"QUALIFY AGGREGATION: case {k} carries no boolean `pass` (fails the qualification)", file=sys.stderr)
    for k in not_run + unknown:
        print(f"QUALIFY AGGREGATION: case {k} {'did not run' if k in not_run else 'is not configured'}",
              file=sys.stderr)
    ok = mode != "dev" and cons["pass"] and not missing_pass and not not_run and not unknown and \
        all(g["pass"] for g in gates.values())
    return {"config_consistency": cons, "gates": gates, "cases_missing_pass": missing_pass, "cases_not_run": not_run,
            "cases_unknown": unknown, "pending_user_decision": pend, "pass": ok}


# ------------------------------------------------------------------ preconditions
def preconditions_core(mode: str, facts: dict) -> dict:
    """The decision on gathered facts (pure). official: HEAD = freeze; review: HEAD = freeze or the qualification
    commit on it (adding qualification/ files only); dev: any HEAD."""
    fz, head = facts.get("freeze_commit"), facts.get("head")
    out = {"freeze_commit": fz, "head": head, "mode": mode}
    if mode == "official":
        ok_head = bool(fz) and head == fz
    elif mode == "review":
        added = facts.get("head_changed") or []
        ok_head = bool(fz) and (head == fz or (facts.get("head_parent") == fz and bool(added) and
                                               all(a.startswith(NS_REL + "/qualification/") for a in added)))
    else:
        ok_head = True
    out["head_ok"] = bool(ok_head)
    out["no_review_grant_result_or_post_freeze_record"] = not facts.get("forbidden_present")
    out["no_campaign_refs"] = not facts.get("campaign_refs")
    out["mbr1_recorded_state_exact"] = facts.get("mbr1_state_ok") is True
    out["no_spool_result"] = not facts.get("spool_result_entries")
    if mode != "dev":
        out["tracked_clean"] = facts.get("tracked_clean") is True
    if mode == "official":
        out["namespace_clean_including_ignored"] = facts.get("namespace_clean_including_ignored") is True
        host = facts.get("host") or {}
        for k in ("host_on_ac", "platform_pins", "section8_preflight_gates", "sleep_channels_available"):
            out[k] = host.get(k) is True
        out["host_readings"] = {k: v for k, v in host.items() if k.endswith("_detail")}
    keys = [k for k, v in out.items() if isinstance(v, bool)]
    out["forbidden_present"] = list(facts.get("forbidden_present") or [])
    out["campaign_refs"] = list(facts.get("campaign_refs") or [])
    out["pass"] = all(out[k] for k in keys)
    return out


def host_readiness() -> dict:
    """Protocol section 8 host readiness for an official run: AC, the platform pins (RC2), the section-8 preflight
    gates as the driver computes them (without the launcher gate; each refuses), and the sleep channels K / S / L."""
    D = driver()
    out = {}
    for key, fn in (("host_on_ac", D.require_ac), ("platform_pins", D.check_platform),
                    ("section8_preflight_gates", lambda: D.host_preflight(None))):
        try:
            fn()
            out[key] = True
        except Exception as exc:                                          # noqa: BLE001 (recorded; fails closed)
            out[key], out[key + "_detail"] = False, str(exc)[:300]
    try:
        out["sleep_channels_available"] = D.HOST.kern_times() is not None and D.HOST.log_events(0, 0) is not None
    except Exception:                                                     # noqa: BLE001
        out["sleep_channels_available"] = False
    return out


HOST_REPORT_STATUSES = ("READY", "NOT_READY", "USER_ACTION", "RECORDED", "UNKNOWN")


def _clamshell(text: str | None = None):
    """The lid: True closed, False open, None unreadable (`ioreg -r -k AppleClamshellState -d 1`, read-only)."""
    import re as _re
    if text is None:
        text = driver().HOST._run(["/usr/sbin/ioreg", "-r", "-k", "AppleClamshellState", "-d", "1"])
    m = _re.search(r'"AppleClamshellState" = (Yes|No)', text or "")
    return None if m is None else m.group(1) == "Yes"


def _pmset_values(text: str | None = None) -> dict:
    """`pmset -g` settings of interest (read-only): autorestart, sleep, displaysleep, disksleep, lowpowermode."""
    import re as _re
    if text is None:
        text = driver().HOST._run(["/usr/bin/pmset", "-g"])
    out = {}
    for k in ("autorestart", "sleep", "displaysleep", "disksleep", "lowpowermode"):
        m = _re.search(r"^\s*" + k + r"\s+(\d+)", text or "", _re.M)
        out[k] = int(m.group(1)) if m else None
    return out


def host_report(work: Path | None = None) -> dict:
    """Protocol section 8.1: the host-readiness checklist, READ-ONLY (every reading is a query: pmset -g, ioreg -r,
    defaults read, sysctl, vm_stat, ps, notifyutil -g, sw_vers, uname, statvfs; NO system setting is ever changed).
    Each item says how it is checked (an existing gate, a new gate, or a recorded user action) and its status."""
    D = driver()
    H = D.HOST
    items = []

    def item(key: str, how: str, status: str, reading, note: str = "") -> None:
        items.append({"item": key, "checked_by": how, "status": status if status in HOST_REPORT_STATUSES else
                      "UNKNOWN", "reading": reading, "note": note})
    su = H.software_update_settings()
    item("automatic_os_installation_disabled", "existing gate: preflight no_automatic_os_install (DR2 c)",
         "READY" if not su["auto_install_enabled"] else "USER_ACTION", su,
         "disabling automatic macOS and critical-update installation is the user's action; the campaign never "
         "changes it")
    pm = _pmset_values()
    item("automatic_restart", "recorded (no gate): a restart is a reboot, detected by the boot UUID and resumable",
         "RECORDED", {"autorestart": pm["autorestart"]}, "automatic restarts by an OS update are excluded by the "
         "previous item")
    power = H.power_source()
    item("ac_power", "existing gates: require_ac and preflight ac_power; AC at every sample (sleep channels)",
         "READY" if power == H.AC else ("NOT_READY" if power else "UNKNOWN"), power)
    lid = _clamshell()
    item("sleep_prevention_and_lid", "existing: supervised caffeinate -i -m -s (execute / resume); the sleep channels "
         "K / S / L detect any sleep (qualification runtimes need a CLEAN assessment); the lid is a user action",
         "READY" if lid is False else ("USER_ACTION" if lid else "UNKNOWN"),
         {"lid_closed": lid, "sleep_min": pm["sleep"], "displaysleep_min": pm["displaysleep"],
          "disksleep_min": pm["disksleep"], "sleep_channels_available": H.kern_times() is not None and
          H.log_events(0, 0) is not None},
         "caffeinate cannot stop lid-close (clamshell) sleep: keep the lid open, on AC, for the whole run")
    tl = H.thermal_level()
    item("thermal_level_0", "existing gate: preflight thermal_pressure_0", "READY" if tl == 0 else
         ("NOT_READY" if tl is not None else "UNKNOWN"), tl)
    lpm = H.lowpowermode()
    item("lowpowermode_0", "existing gate: preflight lowpowermode_0", "READY" if lpm == 0 else
         ("NOT_READY" if lpm is not None else "UNKNOWN"), lpm)
    free_repo = H.free_disk_bytes(REPO)
    item("disk_execution", f"existing gate: preflight free_disk_ge_2GiB (MIN_FREE_DISK {H.MIN_FREE_DISK} bytes, "
         "ratification item 23)", "READY" if isinstance(free_repo, int) and free_repo >= H.MIN_FREE_DISK else
         "NOT_READY", free_repo, "a failed probe is NOT_READY (fail closed)")
    qc = SCR.check_free([(work or REPO, SCR.QUAL_MIN_FREE_BYTES), (REPO, H.MIN_FREE_DISK)], "host report")
    item("disk_qualification", f"new gate (brief 50): QUAL_MIN_FREE_BYTES {SCR.QUAL_MIN_FREE_BYTES} bytes before the "
         "verifier's start and each heavy phase, and before the mutant runner's start and each target run",
         "READY" if qc["pass"] else "NOT_READY", [r["free_bytes"] for r in qc["readings"]])
    mp = H.memory_pressure_level()
    fm = D.free_memory_bytes()
    item("memory_pressure_normal", "existing gate: preflight memory_pressure_normal (item 24)",
         "READY" if mp == H.MEMORY_PRESSURE_NORMAL else ("NOT_READY" if mp is not None else "UNKNOWN"), mp)
    item("free_memory", f"existing gate: free_memory_ge_min (FREE_MEM_MIN_BYTES {D.FREE_MEM_MIN_BYTES}, provisional; "
         "R-FREE and its attainability at the qualification)", "READY" if isinstance(fm, int) and
         fm >= D.FREE_MEM_MIN_BYTES else ("NOT_READY" if fm is not None else "UNKNOWN"), fm)
    boot = H.boot_session_uuid()
    item("boot_identity", "existing gate: preflight boot_uuid_recorded; the journal and every identity carry it (a "
         "reboot is CONSUMED_INTERRUPTED)", "READY" if boot else "UNKNOWN", bool(boot))
    try:
        D.check_platform()
        plat, bad = "READY", []
    except D.Refusal as e:
        plat, bad = "NOT_READY", str(e)
    item("host_identity_platform_pins", "existing check: check_platform at preflight, execute, every resume and every "
         "computing mode (RC2 / DR2); re-pinned at the freeze from the qualification host (code/mbs308_repin.py "
         "platform --write-platform)", plat, bad)
    busy = D.busy_processes()
    item("host_exclusive", f"existing gate: host_exclusive (EXCL_CPU_PCT {D.EXCL_CPU_PCT}, EXCL_ALLOW; R-EXCL-PCT / "
         "R-ALLOW at the freeze)", "READY" if not busy else "USER_ACTION", [b["comm"] for b in busy],
         "quit the listed apps (a user action); a process is never allow-listed by hand")
    _rec, pst = D.STATE.read_pidfile(D.store())
    item("no_other_campaign_job", "existing gate: preflight no_other_campaign_job", "READY" if pst != "LIVE" else
         "NOT_READY", pst)
    return {"schema": "rebaseguard.p5y.k5.cell308-mbs-r1.host-report.v1", "read_only": True,
            "changes_made": False, "utc": utc(), "items": items,
            "ready": all(i["status"] in ("READY", "RECORDED") for i in items)}


def gather_facts(mode: str) -> dict:
    D = driver()
    facts = {"freeze_commit": D.freeze_commit(), "head": git("rev-parse", "HEAD"),
             "head_parent": git("rev-parse", "-q", "--verify", "HEAD^"),
             "head_changed": git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").split()}
    forbidden = [D.QREVIEW_REL, D.GRANT_REL, D.RESULT_REL, D.EXEC_DIR_REL] + \
        [NS_REL + "/" + d for d in ("review", "authorization", "evidence", "adjudication", "postexec")]
    facts["forbidden_present"] = sorted({p for p in forbidden if os.path.lexists(REPO / p) or
                                         git("log", "--all", "--format=%H", "--", p)})
    facts["campaign_refs"] = git("for-each-ref", "--format=%(refname)", MBS_REF_PREFIX).split()
    try:
        D.check_mbr1_state()
        facts["mbr1_state_ok"] = True
    except D.Refusal:
        facts["mbr1_state_ok"] = False
    sp = Path(git("rev-parse", "--path-format=absolute", "--git-dir")) / D.STATE.SPOOL_NAME
    facts["spool_result_entries"] = sorted(n for n in (os.listdir(sp) if sp.is_dir() else [])
                                           if n.startswith(D.STATE.RESULT_FILE))
    facts["tracked_clean"] = git("status", "--porcelain", "--untracked-files=no") == ""
    facts["namespace_clean_including_ignored"] = git("status", "--porcelain", "--ignored", "--untracked-files=all",
                                                     "--", NS_REL) == ""
    if mode == "official":
        facts["host"] = host_readiness()
    return facts


def preconditions(mode: str) -> dict:
    return preconditions_core(mode, gather_facts(mode))


# ------------------------------------------------------------------ QS-* suites and the mutant matrix
def suite_env(work: Path) -> dict:
    """The suites' sandboxes live under --work on a SEPARATE `--no-local` base store (the test library clones it from
    the repository on first use); no MBS308_TEST* variable is passed, so the suites test the namespace's own code."""
    return {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "HOME": os.environ.get("HOME", "/var/empty"),
            "MBS308_SCRATCH": str(work / "qs_scratch"), "MBS308_BASE_STORE": str(work / "qs_base_store.git")}


def suite_summary(report, rc: int | None) -> dict:
    """Counts of one suite report (tests/mbs308_testlib.run_tests format). PASS iff > 0 tests, every test ok, the
    report's own counts agree and (when known) the exit code is 0."""
    if not isinstance(report, dict) or not isinstance(report.get("results"), dict):
        return {"pass": False, "reason": "NO_REPORT", "rc": rc}
    res = report["results"]
    n, passed = len(res), sum(1 for v in res.values() if isinstance(v, dict) and v.get("ok") is True)
    failed = sorted(k for k, v in res.items() if not isinstance(v, dict) or v.get("ok") is not True)
    errors = sorted(k for k, v in res.items() if isinstance(v, dict) and v.get("error"))
    ok = n > 0 and passed == n and not failed and report.get("n") == n and report.get("passed") == passed and \
        (rc is None or rc == 0)
    return {"n": n, "passed": passed, "failed": failed, "errors": errors, "rc": rc, "pass": ok}


def declared_mutants(path: Path) -> list:
    """The mutant ids of tests/test_mbs308_mutants.py (read from the source; the module is not imported)."""
    for n in ast.parse(path.read_text()).body:
        if isinstance(n, ast.Assign) and [getattr(t, "id", None) for t in n.targets] == ["MUTANTS"] and \
                isinstance(n.value, ast.Dict):
            return [k.value for k in n.value.keys if isinstance(k, ast.Constant)]
    return []


def mutant_summary(report, declared: list, rc: int | None) -> dict:
    """PASS iff the unmutated code passes every target test, the matrix holds exactly the declared mutants and every
    one is KILLED BY ASSERTION: its target test ran and returned a failure with no error (an exception, a timeout or an
    invalid mutant is not a kill by assertion)."""
    if not isinstance(report, dict) or not isinstance(report.get("matrix"), dict):
        return {"pass": False, "reason": "NO_REPORT", "rc": rc}
    m = report["matrix"]
    by_assert = sorted(k for k, v in m.items() if isinstance(v, dict) and v.get("killed") is True and
                       v.get("test_passed") is False and not v.get("error"))
    other = sorted(k for k, v in m.items() if isinstance(v, dict) and v.get("killed") is True and k not in by_assert)
    surv = sorted(k for k, v in m.items() if not isinstance(v, dict) or v.get("killed") is not True)
    out = {"declared": len(declared), "total": len(m), "killed_by_assertion": len(by_assert),
           "killed_otherwise": other, "survivors": surv, "missing": sorted(set(declared) - set(m)),
           "undeclared": sorted(set(m) - set(declared)), "unmutated_all_pass": report.get("unmutated_all_pass"),
           "rc": rc}
    out["pass"] = report.get("unmutated_all_pass") is True and bool(declared) and not out["missing"] and \
        not out["undeclared"] and len(by_assert) == len(declared) == len(m) and (rc is None or rc == 0)
    return out


def _run_test_file(path: Path, out: Path, env: dict, log: Path) -> int:
    with open(log, "wb") as fh:
        return subprocess.run([PY, *FLAGS, str(path), "--out", str(out)], stdout=fh, stderr=subprocess.STDOUT,
                              env=env, stdin=subprocess.DEVNULL, cwd=str(REPO)).returncode


def run_suite(rel: str, out: Path, env: dict, work: Path, ns: Path = NS) -> dict:
    rc = _run_test_file(ns / rel, out, env, work / (out.stem + ".log"))
    try:
        rep = json.loads(out.read_text())
    except (OSError, ValueError):
        rep = None
    return suite_summary(rep, rc) | {"suite": rel, "record": out.name,
                                     "record_sha256": sha(out.read_bytes()) if out.exists() else None}


def run_mutants(rel: str, out: Path, env: dict, work: Path, ns: Path = NS) -> dict:
    rc = _run_test_file(ns / rel, out, env, work / (out.stem + ".log"))
    try:
        rep = json.loads(out.read_text())
    except (OSError, ValueError):
        rep = None
    return mutant_summary(rep, declared_mutants(ns / rel), rc) | {
        "suite": rel, "record": out.name, "record_sha256": sha(out.read_bytes()) if out.exists() else None}


def resume_decoy_summary(record, rc: int | None) -> dict:
    """QS-RESUME-DECOY (MBS-9 ii): PASS iff the case runner's value-free record says pass (a SIGKILL after k durable
    checkpoints, k served and n - k >= 1 computed at the resume, no rejected checkpoint, every certified leaf of the
    decoy output byte-identical to the uninterrupted run's) and (when known) its exit code is 0. Official form only
    counts as the official case (a dev-form record never passes an official or review run)."""
    if not isinstance(record, dict) or not isinstance(record.get("pass"), bool):
        return {"pass": False, "reason": "NO_RECORD", "rc": rc}
    keys = ("form", "jobs_uninterrupted", "k", "served", "computed", "checkpoints_after_kill", "certified_leaves",
            "stage1_leaves", "stage2_leaves", "stage1_equal", "stage2_equal", "all_certified_equal",
            "rejected_checkpoints", "reason", "error")
    out = {k: record.get(k) for k in keys if k in record}
    out["pass"] = record["pass"] is True and record.get("form") == "official" and \
        record.get("target_evaluations") == 0 and (rc is None or rc == 0)
    out["rc"] = rc
    return out


def run_resume_decoy(form: str, out: Path, env: dict, work: Path, ns: Path = NS) -> dict:
    with open(work / (out.stem + ".log"), "wb") as fh:
        rc = subprocess.run([PY, *FLAGS, str(ns / RESUME_DECOY_RUNNER), "--form", form, "--out", str(out)],
                            stdout=fh, stderr=subprocess.STDOUT, env=env, stdin=subprocess.DEVNULL,
                            cwd=str(REPO)).returncode
    try:
        rec = json.loads(out.read_text())
    except (OSError, ValueError):
        rec = None
    s = resume_decoy_summary(rec, rc)                        # a dev-form record never passes (never evidence)
    return s | {"runner": RESUME_DECOY_RUNNER, "form_run": form, "record": out.name,
                "record_sha256": sha(out.read_bytes()) if out.exists() else None}


# ------------------------------------------------------------------ the disk gate (brief 50)
def disk_check(work: Path, phase: str) -> dict:
    """Free space before the start and before each heavy phase: QUAL_MIN_FREE_BYTES on the --work volume (sandboxes,
    base store) and the ratified MIN_FREE_DISK on the repository volume (the records); a failed probe fails closed."""
    return SCR.check_free([(work, SCR.QUAL_MIN_FREE_BYTES), (REPO, SCR.HOST.MIN_FREE_DISK)], phase)


def clean_suite_scratch(env: dict) -> dict:
    """After a heavy phase whose report was written and verified: delete the disposable sandboxes of the suites'
    scratch root (lifecycle gate; every deletion recorded)."""
    root = Path(env["MBS308_SCRATCH"])
    if not root.is_dir():
        return {"deleted": 0}
    try:
        r = SCR.cleanup(root, execute=True)
    except SCR.ScratchRefusal as e:
        return {"refused": e.code}
    return {"deleted": len(r["deleted"]), "bytes_deleted": r["bytes_deleted"], "refused": r["refused"]}


# ------------------------------------------------------------------ QC09-S: the guard (one-line diff)
GUARD_DIFF_EXPECTED = ['-CONSUMED_REF = "refs/p5y-k5-cell308-mb-r1/target-consumed"',
                       '+CONSUMED_REF = "refs/p5y-k5-cell308-mbs-r1/target-consumed"']

QC09_CHILD = r'''
import json, subprocess, sys
from fractions import Fraction as F
sys.path.insert(0, sys.argv[1])
import mbs308_guard as G
repo, mbr1 = sys.argv[2], sys.argv[3]
R = {}
def refused(fn, *a):
    try:
        fn(*a)
        return False
    except G.QuarantineRefusal:
        return True
def git(*a):
    return subprocess.run(["/usr/bin/git", "-C", repo, *a], capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "HOME": repo,
                               "GIT_CONFIG_NOSYSTEM": "1"}).stdout.strip()
R["decoy_by_default"] = G.mode() == "DECOY"
band = [(F(6, 5), None), (F(2), None), (F(13, 5), None), (F(1), F(3)), (F(-2), None), (F(-13, 5), F(-6, 5))]
R["band_points_intervals_and_mirror_refused"] = all(refused(G.guard_drift, a, b) for a, b in band)
R["cover_end_points_refused_in_decoy"] = all(refused(G.guard_drift, x) for x in G.CELL308)
outside = [(F(1), None), (F(3), None), (F(11, 10), None), (F(1, 2), F(1)), (F(-1), None)]
R["outside_band_admitted"] = not any(refused(G.guard_drift, a, b) for a, b in outside)
R["labels_305_309_refused"] = all(refused(G.guard_cell, "CUSUM", 5, c) for c in range(305, 310))
R["other_labels_admitted"] = not any(refused(G.guard_cell, d, m, c) for d, m, c in
                                     (("CUSUM", 5, 304), ("CUSUM", 5, 310), ("CUSUM", 4, 308), ("SR", 5, 308)))
R["emergency_result_path_refused"] = refused(G.guard_path, "x/mbs308-cell308-emergency-result.json")
adm = G.target_admitted_set()
lst = sorted(adm)
head, parent = git("rev-parse", "HEAD"), git("rev-parse", "HEAD^")
extra = (F(2), F(2))
cases = {"no_marker": refused(G.arm_target, repo, head, lst)}
git("update-ref", mbr1, head)
cases["mbr1_marker_naming_the_grant_at_head"] = refused(G.arm_target, repo, head, lst)
git("update-ref", "-d", mbr1)
git("update-ref", G.CONSUMED_REF, parent)
cases["marker_names_another_commit"] = refused(G.arm_target, repo, head, lst)
cases["grant_is_not_head"] = refused(G.arm_target, repo, parent, lst)
git("update-ref", G.CONSUMED_REF, head)
cases["dropped_pair"] = refused(G.arm_target, repo, head, lst[1:])
cases["extra_band_pair"] = extra not in adm and refused(G.arm_target, repo, head, lst + [extra])
R["arming_refusals"] = cases
R["still_decoy_after_refusals"] = G.mode() == "DECOY"
try:
    G.arm_target(repo, head, lst)
    armed = G.mode() == "TARGET"
except G.QuarantineRefusal:
    armed = False
R["arms_with_the_successor_marker_and_exactly_the_frozen_set"] = armed
a = lst[len(lst) // 2]
R["after_arming_an_admitted_pair_passes"] = armed and not refused(G.guard_drift, a[0], a[1])
R["after_arming_a_non_admitted_band_point_is_refused"] = armed and refused(G.guard_drift, extra[0], extra[1])
R["after_arming_label_308_admitted"] = armed and not refused(G.guard_cell, "CUSUM", 5, 308)
R["after_arming_label_307_refused"] = armed and refused(G.guard_cell, "CUSUM", 5, 307)
R["admitted_pairs"] = len(adm)
print(json.dumps(R, sort_keys=True))
'''


def guard_diff_lines(old: str, new: str) -> list:
    return [ln for ln in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0)
            if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]


def _arming_repo(work: Path) -> Path:
    """A throw-away git repository (two empty commits) for the arming checks: never the campaign's repository."""
    r = work / "qc09_arming_repo"
    if r.exists():
        import shutil
        shutil.rmtree(r)
    r.mkdir(parents=True)
    env = dict(ENV, HOME=str(r), GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="qc09", GIT_AUTHOR_EMAIL="qc09@invalid",
               GIT_COMMITTER_NAME="qc09", GIT_COMMITTER_EMAIL="qc09@invalid")
    for args in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "qc09 base"],
                 ["commit", "-q", "--allow-empty", "-m", "qc09 stand-in grant"]):
        subprocess.run(["/usr/bin/git", "-C", str(r), *args], check=True, capture_output=True, env=env)
    return r


def qc09_guard(work: Path, repo: Path = None, code: Path = None, mbr1_guard_pin: str = None) -> dict:
    repo, code = repo or REPO, code or CODE
    new = (code / "mbs308_guard.py").read_text()
    old_b = git_show_bytes(SCIENCE_BASE_COMMIT, NSF_REL + "/code/mb308_guard.py", repo=repo)
    pin = mbr1_guard_pin or next((c.get("sha256") for c in load_config(code.parent / "config" /
                                                                      "MBS308_QUALIFICATION_CASES.json")["commit_pins"]
                                  if c["key"] == "mbr1_guard_base"), None)
    out = {"mbr1_guard_bytes_are_the_pinned_bytes": old_b is not None and sha(old_b) == pin}
    out["diff_is_exactly_the_marker_line"] = old_b is not None and \
        guard_diff_lines(old_b.decode(), new) == GUARD_DIFF_EXPECTED
    dsrc = (code / "mbs308_driver.py").read_text()
    dc = module_constants(dsrc)
    binds = [n for n in ast.parse(dsrc).body if isinstance(n, ast.Assign) and
             [getattr(t, "id", None) for t in n.targets] == ["CONSUMED_REF"]]
    out["driver_binds_the_guard_marker"] = len(binds) == 1 and ast.unparse(binds[0].value) == "GUARD.CONSUMED_REF"
    out["driver_pins_the_guard_bytes"] = (dc.get("HELPER_SHA256") or {}).get("mbs308_guard.py") == \
        sha(new.encode())
    out["guard_marker_is_the_successors"] = module_constants(new).get("CONSUMED_REF") == \
        MBS_REF_PREFIX + "target-consumed"
    ar = _arming_repo(work)
    p = subprocess.run([PY, *FLAGS, "-c", QC09_CHILD, str(code), str(ar), MBR1_MARKER_REF], capture_output=True,
                       text=True, env=ENV, stdin=subprocess.DEVNULL, cwd=str(work))
    try:
        child = json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        child = {"error": (p.stderr or "")[-300:]}
    out["child"] = child
    flat = [v for k, v in child.items() if k not in ("arming_refusals", "admitted_pairs")] + \
        list((child.get("arming_refusals") or {}).values())
    out["child_expectations_hold"] = p.returncode == 0 and "error" not in child and \
        len(child.get("arming_refusals") or {}) == 6 and bool(flat) and all(v is True for v in flat)
    out["pass"] = all(v is True for k, v in out.items() if isinstance(v, bool))
    return out


# ------------------------------------------------------------------ QC11-S: static structure (AST)
WRITE_NAMES = frozenset({"open", "write_text", "write_bytes", "write", "mkdir", "rename", "replace", "unlink"})
TARGET_PATH_FUNCS = ("stage1", "evaluate_target", "prepare_target", "_worker_job", "_worker_init", "decide",
                     "controls", "compose_and_consume", "target_geometry", "load_science", "after_marker")
POST_MARKER_PRINTERS = ("after_marker", "persist_and_seal", "_pending_seal_materialize", "run_seal_only",
                        "run_resume", "run_recover", "run_close_indeterminate")
PRINT_ALLOWED = frozenset({"cid", "status", "channel", "s", "action", "type(exc).__name__", "len(moved)"})
HELPERS = frozenset({"mbs308_guard.py", "mbs308_host.py", "mbs308_state.py", "mbs308_launch.py"})
COVERED_BY_QS_STATIC = ("RC1: the carried science glue is text-identical to MB r1's "
                        "(t_rc1_science_glue_text_identical)",
                        "MBS-9 (i): module-level names (t_mbs9_referenced_module_names)",
                        "the guard differs only in the marker line (t_rc1_guard_diff_only_marker; QC09-S re-checks)",
                        "the science modules are MB r1's pinned bytes (t_science_pins_equal_mbr1_bytes)",
                        "the fault hook is test-only (t_fault_hook_test_only)",
                        "execute / resume pass the launcher, platform and host gates (t_execute_and_resume_require_"
                        "launcher_and_pins)", "no MB r1 driver mode is invoked (t_no_mbr1_driver_mode_invoked)",
                        "the launcher plist contract (t_launcher_plist_contract)",
                        "the ratified rules R-MEM / R-FREE / R-EXCL-PCT / R-ALLOW in protocol s8 (t_r3_ratified_"
                        "rules_applied)")


def _top(tree) -> dict:
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _all_funcs(tree) -> dict:
    return {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def _calls(node, name) -> list:
    if node is None:
        return []
    return [c for c in ast.walk(node) if isinstance(c, ast.Call) and
            ((isinstance(c.func, ast.Name) and c.func.id == name) or
             (isinstance(c.func, ast.Attribute) and c.func.attr == name))]


def _inside(node, fn) -> bool:
    return fn is not None and any(x is node for x in ast.walk(fn))


def _names(node) -> set:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} | \
        {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}


def _mode_branches(main) -> dict:
    br = {}
    for node in ast.walk(main):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and \
                isinstance(node.test.left, ast.Attribute) and node.test.left.attr == "mode" and \
                len(node.test.comparators) == 1 and isinstance(node.test.comparators[0], ast.Constant):
            br[node.test.comparators[0].value] = ast.Module(body=node.body, type_ignores=[])
    return br


def qc11_driver_structure(src: str, host_src: str) -> dict:
    """The successor driver's structure (what MB r1's QC11 checked, re-targeted to the successor lifecycle)."""
    tree = ast.parse(src)
    fd = _top(tree)
    r = {}
    main, pmc, rx, rr = fd.get("main"), fd.get("pre_marker_common"), fd.get("run_execute"), fd.get("run_resume")
    one = lambda f: [c for c in _calls(main, f) if isinstance(c.func, ast.Name)]  # noqa: E731
    ok = True
    for f in ("run_execute", "run_resume", "run_recover", "run_close_indeterminate"):
        cs = one(f)
        ok = ok and len(cs) == 1 and len(cs[0].args) == 1 and isinstance(cs[0].args[0], ast.Name) and \
            cs[0].args[0].id == "own_sha" and not cs[0].keywords
    so = one("run_seal_only")
    r["cli_passes_no_injection"] = ok and len(so) == 1 and not so[0].args and not so[0].keywords
    ctl = [c for c in _calls(tree, "control") if any(isinstance(a, ast.Name) and a.id == "TARGET_CELL" for a in c.args)]
    gr = _calls(pmc, "check_grant")
    r["target_control_only_in_pre_marker_common_after_check_grant"] = len(ctl) == 1 and _inside(ctl[0], pmc) and \
        bool(gr) and ctl[0].lineno > min(c.lineno for c in gr)
    pm = _calls(tree, "pre_marker_common")
    r["pre_marker_common_only_in_execute_and_resume"] = len(pm) == 2 and \
        {f for f in ("run_execute", "run_resume") if any(_inside(c, fd.get(f)) for c in pm)} == \
        {"run_execute", "run_resume"}
    st = [c for c in _calls(tree, "stage1") if c.args and isinstance(c.args[0], ast.Constant) and
          c.args[0].value == "target"]
    r["stage1_target_only_in_evaluate_target"] = len(st) == 1 and _inside(st[0], fd.get("evaluate_target"))
    refs = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "evaluate_target"]
    r["evaluate_target_referenced_only_by_execute_and_resume"] = len(refs) == 2 and \
        {f for f in ("run_execute", "run_resume") if any(_inside(x, fd.get(f)) for x in refs)} == \
        {"run_execute", "run_resume"}
    arms = _calls(tree, "arm_target")
    places = {f for f in ("evaluate_target", "_worker_init", "run_resume") if any(_inside(c, fd.get(f)) for c in arms)}
    r["arm_target_only_in_evaluate_target_worker_init_and_resume"] = len(arms) == 3 and \
        places == {"evaluate_target", "_worker_init", "run_resume"}
    arm_rr, vr = [c for c in arms if _inside(c, rr)], _calls(rr, "verified_records")
    r["resume_arms_before_reading_checkpoints"] = len(arm_rr) == 1 and len(vr) == 1 and arm_rr[0].lineno < vr[0].lineno
    cref = [c for c in ast.walk(tree) if isinstance(c, ast.Call) and
            any(isinstance(a, ast.Name) and a.id == "CONSUMED_REF" for a in c.args)]
    cas = [c for c in cref if isinstance(c.func, ast.Attribute) and c.func.attr == "cas_ref" and
           isinstance(c.args[0], ast.Name) and c.args[0].id == "CONSUMED_REF"]
    r["exactly_one_marker_write_a_cas_in_run_execute"] = len(cref) == 1 and len(cas) == 1 and _inside(cas[0], rx)
    arming = [c for c in _calls(rx, "advance") if any(k.arg == "state" and isinstance(k.value, ast.Constant) and
                                                       k.value.value == "ARMING" for k in c.keywords)]
    pmx, amx = _calls(rx, "pre_marker_common"), _calls(rx, "after_marker")
    r["marker_after_pre_marker_checks_and_intent_before_computing"] = bool(cas and arming and pmx and amx) and \
        pmx[0].lineno < arming[0].lineno < cas[0].lineno < amx[0].lineno
    hp = _calls(pmc, "host_preflight")
    r["ac_platform_and_host_gates_with_launcher_in_pre_marker_common"] = len(_calls(pmc, "require_ac")) == 1 and \
        len(_calls(pmc, "check_platform")) == 1 and len(hp) == 1 and len(hp[0].args) == 1 and \
        isinstance(hp[0].args[0], ast.Call) and getattr(hp[0].args[0].func, "id", None) == "check_launched"
    br = _mode_branches(main) if main is not None else {}
    r["ac_required_in_preflight"] = len(_calls(main, "require_ac")) == 1 and len(_calls(br.get("preflight"),
                                                                                        "require_ac")) == 1
    no_write = {fn: fd.get(fn) is not None and not [
        c for c in ast.walk(fd[fn]) if isinstance(c, ast.Call) and
        (getattr(c.func, "id", None) in WRITE_NAMES or getattr(c.func, "attr", None) in WRITE_NAMES)]
        for fn in TARGET_PATH_FUNCS}
    r["no_file_write_in_target_path"] = all(no_write.values())
    bad, n_prints = [], 0
    for fn in POST_MARKER_PRINTERS:
        for c in _calls(fd.get(fn), "print"):
            n_prints += 1
            for a in c.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    continue
                if isinstance(a, ast.JoinedStr) and all(not isinstance(v, ast.FormattedValue) or
                                                        ast.unparse(v.value) in PRINT_ALLOWED for v in a.values):
                    continue
                bad.append(f"{fn}:{c.lineno}")
            if c.keywords:
                bad.append(f"{fn}:{c.lineno}:keywords")
    r["post_marker_prints_value_free"] = not bad and n_prints > 0
    hc = module_constants(host_src)
    ka = fd.get("keep_awake")
    r["supervised_caffeinate_ims"] = hc.get("CAFFEINATE_FLAGS") == ("-i", "-m", "-s") and \
        len(_calls(ka, "CaffeinateSupervisor")) == 1 and len(_calls(pmc, "keep_awake")) == 1
    am = fd.get("after_marker")
    r["eval_cap_per_attempt_on_awake_time"] = any(
        c.args and isinstance(c.args[0], ast.Name) and c.args[0].id == "EVAL_CAP_S" for c in _calls(am, "AwakeCap"))
    r["host_provenance_closed_in_after_marker"] = len(_calls(am, "close_host")) == 1
    dec = br.get("decoy")
    snaps, smps, provs = _calls(dec, "snapshot"), _calls(dec, "Sampler"), _calls(dec, "provenance")
    decs = [c for c in _calls(dec, "decoy") if isinstance(c.func, ast.Name)]
    r["decoy_host_provenance_brackets_decoy"] = len(decs) == 1 and len(provs) == 1 and bool(snaps) and \
        len(smps) == 1 and min(c.lineno for c in snaps) <= smps[0].lineno <= decs[0].lineno <= provs[0].lineno
    hs = module_constants(src).get("HELPER_SHA256")
    r["every_helper_pinned"] = isinstance(hs, dict) and set(hs) == HELPERS and \
        all(isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) for v in hs.values())
    return r


def qc11_science_bytes(repo: Path, driver_src: str, ns: Path) -> dict:
    """MB r1's QC11 checks of MB r1's own science bytes, re-run on the bytes the successor executes (SCIENCE_PINS at MB
    r1's paths; each checked against its pin first)."""
    dc = module_constants(driver_src)
    pins, nsf = dc.get("SCIENCE_PINS") or {}, dc.get("NSF_REL")
    r, texts = {}, {}
    ok = len(pins) == 5 and bool(nsf)
    for name, (s, b) in pins.items():
        try:
            raw = (repo / nsf / "code" / f"{name}.py").read_bytes()
        except OSError:
            raw = b""
        ok = ok and sha(raw) == s and blob_id(raw) == b
        texts[name] = raw.decode(errors="replace")
    r["science_bytes_are_the_pinned_bytes"] = ok
    if not ok:
        return r
    con = ast.parse(texts["mb308_consumer"])
    fc = _all_funcs(con)
    forbidden_route = {"penalty_closed", "penalty_c5t", "penalty_riemann", "penalty_riemann_lower",
                       "evaluate_bundle", "p5_c5t_closed_form", "tpt_endpoint_only", "_mutant"}
    r["control_path_names_no_penalty"] = all(k in fc for k in ("_repro_core", "control_cb", "gr3b_cell")) and not (
        (_names(fc["_repro_core"]) | _names(fc["control_cb"]) | _names(fc["gr3b_cell"])) &
        (forbidden_route | {"penalty_blocked", "tptb"}))
    r["stage2_names_no_other_route"] = "_stage2" in fc and not (_names(fc["_stage2"]) & forbidden_route)
    rbg = [k for c in ast.walk(con) if isinstance(c, ast.Call) for k in c.keywords if k.arg == "research_band_guard"]
    r["F2_band_guard_only_from_formal_guard"] = bool(rbg) and all(
        isinstance(k.value, ast.Name) and k.value.id == "band_guard" for k in rbg) and \
        "_stage2" in fc and "f2_band_guard" in _names(fc["_stage2"])
    sup = ast.parse(texts["mb308_supply"])
    rbs = [k for c in ast.walk(sup) if isinstance(c, ast.Call) for k in c.keywords if k.arg == "research_band_guard"]
    r["supply_band_guard_only_from_formal_guard"] = bool(rbs) and all(
        isinstance(k.value, ast.Name) and k.value.id == "band_guard" for k in rbs)
    for name, t in (("mbs308_driver.py", driver_src), ("mb308_consumer", texts["mb308_consumer"]),
                    ("mb308_supply", texts["mb308_supply"]), ("mb308_stage1", texts["mb308_stage1"]),
                    ("mb308_a0core", texts["mb308_a0core"])):
        nm = _names(ast.parse(t))
        r[f"no_private_F2_hooks_{name}"] = "_mutant" not in nm and "tpt_endpoint_only" not in nm
    r["stage1_and_a0core_print_and_write_nothing"] = not any(
        isinstance(c, ast.Call) and ((isinstance(c.func, ast.Name) and c.func.id in {"print", "open"}) or
                                     (isinstance(c.func, ast.Attribute) and c.func.attr in WRITE_NAMES))
        for t in (texts["mb308_stage1"], texts["mb308_a0core"]) for c in ast.walk(ast.parse(t)))
    pc = module_constants(texts["mb308_pinned"])

    def imports(rel):
        try:
            t = ast.parse((repo / rel).read_text())
        except (OSError, SyntaxError, TypeError):
            return None
        return {a.name.split(".")[0] for n in ast.walk(t) if isinstance(n, ast.Import) for a in n.names} | \
            {(n.module or "").split(".")[0] for n in ast.walk(t) if isinstance(n, ast.ImportFrom)}
    i2, i3 = imports((pc.get("INDEP_PIN") or ("",))[0]), imports((pc.get("TUPLE_PIN") or ("",))[0])
    r["F2_imports_stdlib_only"] = i2 is not None and i2 <= {"__future__", "fractions", "re"}
    r["F3_imports_stdlib_only"] = i3 is not None and i3 <= {"__future__", "fractions", "hashlib", "json", "math",
                                                            "random", "copy", "sys"}
    forbidden = ("history" + "/" + "recon", "KNOCK" + "OUT_RECON")        # built, never written (incident review C2)
    hits, exempt = [], []
    for p in sorted(ns.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        text = p.read_text(errors="replace")
        lines = [i for i, ln in enumerate(text.splitlines(), 1) if any(f in ln for f in forbidden)]
        if not lines:
            continue
        span = None
        if p.name == STATIC_CHECK[0]:
            fn = _top(ast.parse(text)).get(STATIC_CHECK[1])
            span = (fn.lineno, fn.end_lineno) if fn is not None else None
        if span and all(span[0] <= i <= span[1] for i in lines):
            exempt.append({"file": p.name, "function": STATIC_CHECK[1], "lines": len(lines)})
        else:
            hits.append(p.name)
    r["no_successor_code_names_the_research_reconstructions"] = not hits
    r["_named_exception"] = exempt
    return r


# the one named exception of the check above: QS-STATIC's own MBS-12 check names the file in order to assert that no
# other successor file does (every occurrence must lie inside that function; anywhere else it is a hit)
STATIC_CHECK = ("test_mbs308_static.py", "t_mbs12_static_carryovers")


def qc11_static(repo: Path = None, code: Path = None, ns: Path = None) -> dict:
    repo, code = repo or REPO, code or CODE
    ns = ns or code.parent
    src = (code / "mbs308_driver.py").read_text()
    drv = qc11_driver_structure(src, (code / "mbs308_host.py").read_text())
    sci = qc11_science_bytes(repo, src, ns)
    return {"driver_structure": drv, "science_bytes": sci, "covered_by_qs_static": list(COVERED_BY_QS_STATIC),
            "pass": bool(drv) and bool(sci) and all(v is True for v in drv.values()) and
            all(v is True for k, v in sci.items() if not k.startswith("_")) and len(sci) > 2}


# ------------------------------------------------------------------ QC12-S: leak scans
def tail_patterns(repo: Path = None) -> list:
    """The tail-figure patterns, read at RUN TIME from the pinned sanctioned file (sha256 and blob at HEAD checked);
    nothing of them is written into this namespace or printed."""
    repo = repo or REPO
    rel, want, bl = PATTERNS_PIN
    raw = (repo / rel).read_bytes()
    head = git("rev-parse", f"HEAD:{rel}", repo=repo)
    if sha(raw) != want or not head.startswith(bl) or blob_id(raw) != head:
        raise ValueError("the tail-figure pattern file differs from its pin")
    return list(json.loads(raw)["patterns"])


def tail_regex(pats: list):
    """Compiled exactly as the research scanner r2 compiles them (MB r1's QC12)."""
    return re.compile("|".join("(?<![0-9])" + p for p in pats))


def strip_timing(o):
    if isinstance(o, dict):
        return {k: strip_timing(v) for k, v in o.items() if k not in TIMING_KEYS}
    if isinstance(o, list):
        return [strip_timing(v) for v in o]
    return o


def tail_hits(rel: str, text: str, rx, post_dirs: tuple, ns_rel: str = NS_REL) -> tuple:
    """(non-exempt matches, matches exempted as timing fields). Only machine-written JSON evidence under the
    post-freeze directories may exempt a match located ONLY inside a timing key (TIMING_KEYS, any depth); every other
    file is scanned as text without exemption; a raw-text-only match is never exempt."""
    n = len(rx.findall(text))
    parts = Path(rel).relative_to(ns_rel).parts if rel.startswith(ns_rel + "/") else ()
    if not n or not parts or parts[0] not in post_dirs or not rel.endswith(".json"):
        return n, 0
    try:
        obj = json.loads(text)
    except ValueError:
        return n, 0
    kept = len(rx.findall(json.dumps(strip_timing(obj), sort_keys=True)))
    full = len(rx.findall(json.dumps(obj, sort_keys=True)))
    return kept + max(0, n - full), max(0, full - kept)


def token_hits(rel: str, text: str, toks: set, geom: set, manifest_rel: str = MANIFEST_REL,
               guard_rel: str = GUARD_REL) -> tuple:
    """(NON-exempt token occurrences, [exemption records]). Cell 308's cover-geometry tokens are exempt ONLY in the
    guard source and inside the manifest's guard-geometry field (every occurrence of the token in the manifest must lie
    in that field); counts only."""
    counts = {t: text.count(t) for t in toks | geom if t in text}
    if not counts:
        return 0, []
    field_counts = {}
    if rel == manifest_rel:
        try:
            vals = json.loads(text).get(GUARD_FIELD[0], {}).get(GUARD_FIELD[1], [])
        except (ValueError, AttributeError):
            vals = []
        field_counts = {t: sum(str(v).count(t) for v in vals) for t in counts}
    bad = n_ex = 0
    for t, n in counts.items():
        if t in geom and rel == guard_rel:
            n_ex += n
        elif t in geom and rel == manifest_rel and field_counts.get(t, 0) == n:
            n_ex += n
        else:
            bad += n
    ex = [] if not n_ex else [{"file": rel, "field": ".".join(GUARD_FIELD) if rel == manifest_rel else "source",
                               "occurrences": n_ex}]
    return bad, ex


def tokenise(o, acc: set) -> None:
    """MB r1's tokenisation: exact rational strings (>= 8 chars) and their 6-significant-digit renderings."""
    if isinstance(o, dict):
        for v in o.values():
            tokenise(v, acc)
    elif isinstance(o, list):
        for v in o:
            tokenise(v, acc)
    elif isinstance(o, str) and "/" in o:
        try:
            x = F(o)
        except (ValueError, ZeroDivisionError):
            return
        if len(o) >= 8:
            acc.add(o)
        s = f"{abs(float(x)):.12g}"
        if "e" not in s and len(s.replace(".", "").lstrip("0")) >= 6:
            out, n = "", 0
            for ch in s:
                out += ch
                if ch.isdigit() and (n > 0 or ch != "0"):
                    n += 1
                if n == 6:
                    break
            acc.add(out)


def record_tokens(D) -> set:
    """Tokens of the committed cell-308 records (C2 forecast cell and supplies, REGISTRY_C1 / C2 rows,
    TCT_INPUTS_308), through the driver's pinned reads. Never printed."""
    acc: set = set()
    fc = json.loads(D.read_pinned("c2_forecast"))
    tokenise(fc["cells"]["308"], acc)
    tokenise(fc["supplies"]["308"], acc)
    for key in ("registry_c1", "registry_c2"):
        tokenise([b for b in json.loads(D.read_pinned(key))["blocks"] if b["cell"] == 308], acc)
    tokenise(json.loads(D.read_pinned("tct_inputs_308")), acc)
    return acc


def geometry_tokens(D) -> set:
    cells = [c for c in json.loads(D.read_pinned("cells_json")) if c["detector"] == "CUSUM" and c["index"] == 308]
    acc: set = set()
    if len(cells) == 1:
        tokenise({k: cells[0][k][0] for k in ("left", "right", "e0", "rho")}, acc)
    return acc


def qc12_core(files: list, pats: list, *, post_dirs: tuple, toks: set | None = None, geom: set | None = None,
              manifest_text: str | None = None, ns_rel: str = NS_REL, manifest_rel: str = MANIFEST_REL,
              guard_rel: str = GUARD_REL) -> dict:
    """`files`: [(repo-relative path, text)]. Planted controls are built at run time from the patterns (neutral
    wording) and from the tokens; nothing of a pattern, a token or a hit is returned: counts and file names only."""
    rx = tail_regex(pats)
    hits, timing_ex = {}, []
    for rel, text in files:
        n, ex = tail_hits(rel, text, rx, post_dirs, ns_rel)
        if n:
            hits[rel] = n
        if ex:
            timing_ex.append({"file": rel, "field": "timing keys " + "/".join(sorted(TIMING_KEYS)), "occurrences": ex})
    planted = " and ".join(re.sub(r"\\b|\\", "", pat) for pat in pats[:3])
    one = re.sub(r"\\b|\\", "", pats[0]) if pats else ""
    rec_rel = ns_rel + "/" + post_dirs[0] + "/PLANTED.json"
    ctl = {"planted_control_fires": len(rx.findall("row " + planted + " end")) >= 3,
           "planted_value_in_nontiming_field_of_evidence_fires":
               tail_hits(rec_rel, json.dumps({"record": {"value": one, "seconds": 1.0}}), rx, post_dirs, ns_rel)[0] > 0,
           "planted_value_in_timing_field_of_evidence_exempt_and_counted":
               tail_hits(rec_rel, json.dumps({"record": {"value": "x", "seconds": {"S": one}}}), rx, post_dirs,
                         ns_rel) == (0, 1),
           "planted_value_in_timing_field_outside_post_freeze_dirs_fires":
               tail_hits(ns_rel + "/config/PLANTED.json", json.dumps({"seconds": one}), rx, post_dirs, ns_rel)[0] > 0}
    out = {"files_scanned": len(files), "patterns": len(pats), "tail_figure_hits": hits,
           "timing_field_exemptions": timing_ex, **ctl}
    tail_ok = not hits and all(ctl.values()) and len(pats) > 20
    if toks is None:
        out["record_token_scan"] = "not run (official and review runs, or --record-scan in dev mode)"
        out["pass"] = tail_ok
        return out
    if not geom or not toks:
        out.update({"pass": False, "reason": "no record or geometry tokens derived"})
        return out
    th, exempt = {}, []
    for rel, text in files:
        bad, ex = token_hits(rel, text, toks, geom, manifest_rel, guard_rel)
        if bad:
            th[rel] = bad
        exempt += ex
    c = {"planted_non_geometry_token_in_manifest_copy_fires": False,
         "planted_geometry_token_outside_guard_field_fires": False,
         "planted_geometry_token_inside_guard_field_exempt": False}
    non_geo = sorted(toks - geom)
    if manifest_text is not None and non_geo:
        pr = manifest_text.replace("\n", "\n" + json.dumps(non_geo[len(non_geo) // 2]) + "\n", 1)
        c["planted_non_geometry_token_in_manifest_copy_fires"] = token_hits(manifest_rel, pr, toks, geom,
                                                                            manifest_rel, guard_rel)[0] > 0
        g0 = sorted(geom)[0]
        pg = manifest_text.replace("\n", "\n" + json.dumps(g0) + "\n", 1)
        c["planted_geometry_token_outside_guard_field_fires"] = token_hits(manifest_rel, pg, toks, geom,
                                                                          manifest_rel, guard_rel)[0] > 0
        clean = json.dumps({GUARD_FIELD[0]: {GUARD_FIELD[1]: [g0]}})
        c["planted_geometry_token_inside_guard_field_exempt"] = token_hits(manifest_rel, clean, toks, geom,
                                                                          manifest_rel, guard_rel)[0] == 0
    out.update({"record_tokens": len(toks), "geometry_tokens": len(geom), "record_token_hit_files": sorted(th),
                "record_token_hits": sum(th.values()), "geometry_exemptions": exempt, **c})
    out["pass"] = tail_ok and not th and all(c.values()) and len(toks) > 20
    return out


def qc12_leak(record_scan: bool, repo: Path = None, ns: Path = None) -> dict:
    repo, ns = repo or REPO, ns or NS
    try:
        pats = tail_patterns(repo)
    except (OSError, ValueError, KeyError) as exc:
        return {"pass": False, "reason": f"pattern file: {type(exc).__name__}"}
    files = [(str(p.relative_to(repo)), p.read_text(errors="replace")) for p in sorted(ns.rglob("*"))
             if p.is_file() and "__pycache__" not in p.parts]
    pdirs = post_freeze_dirs(ns / "code")
    if not record_scan:
        return qc12_core(files, pats, post_dirs=pdirs)
    D = driver()
    mp = repo / MANIFEST_REL
    return qc12_core(files, pats, post_dirs=pdirs, toks=record_tokens(D), geom=geometry_tokens(D),
                     manifest_text=mp.read_text() if mp.exists() else None)


# ------------------------------------------------------------------ QC13-S: temporal and governance state
def verdict_ok(text: str, expected) -> bool:
    """MB r1's convention: line 2 (line 1 is the title) is exactly the verdict, which occurs once as a whole line."""
    lines = text.splitlines()
    return isinstance(expected, str) and bool(expected) and len(lines) > 1 and lines[1].strip() == expected and \
        sum(1 for ln in lines if ln.strip() == expected) == 1


def check_record(rec: dict, *, show, is_ancestor) -> dict:
    """One governance record by commit and path. `show(commit, path)` -> bytes | None; `is_ancestor(commit, ref)`.
    Nothing of the record's text is returned."""
    out = {"id": rec.get("id"), "kind": rec.get("kind"), "commit": rec.get("commit"), "path": rec.get("path")}
    if not rec.get("commit") or not rec.get("path"):
        out.update({"status": "PENDING_RECORD", "pass": False})
        return out
    raw = show(rec["commit"], rec["path"])
    if raw is None:
        out.update({"status": "MISSING", "pass": False})
        return out
    status = "OK"
    if rec.get("sha256") and sha(raw) != rec["sha256"]:
        status = "SHA_MISMATCH"
    elif rec.get("kind") == "verdict":
        status = "OK" if verdict_ok(raw.decode(errors="replace"), rec.get("verdict")) else "VERDICT_MISMATCH"
    elif rec.get("kind") == "jsonl_line":
        m, found = rec.get("match") or {}, False
        for ln in raw.decode(errors="replace").splitlines():
            try:
                row = json.loads(ln) if ln.strip() else None
            except ValueError:
                row = None
            if isinstance(row, dict) and m.get("agent") and row.get("agent") == m["agent"] and \
                    m.get("purpose_prefix") and str(row.get("purpose", "")).startswith(m["purpose_prefix"]):
                found = True
                break
        status = "OK" if found else "LINE_MISSING"
    elif rec.get("kind") != "presence":
        status = "UNKNOWN_KIND"
    on_ref = bool(rec.get("ref")) and is_ancestor(rec["commit"], rec["ref"])
    if status == "OK" and not on_ref:
        status = "NOT_ON_REF"
    out.update({"status": status, "on_ref": on_ref, "pass": status == "OK"})
    return out


def ledger_check(text: str | None, agents) -> dict:
    """The successor build agents' research-ledger lines: pre-grant classes only, 0 target evaluations / proxies /
    target-informed optimisation, no LEAK_FLAG. Counts only."""
    if text is None:
        return {"pass": False, "reason": "LEDGER_UNREADABLE"}
    rows, bad = {}, []
    for i, ln in enumerate(text.splitlines(), 1):
        if not ln.strip():
            continue
        try:
            r = json.loads(ln)
        except ValueError:
            bad.append(i)
            continue
        if r.get("agent") not in agents:
            continue
        rows[r["agent"]] = rows.get(r["agent"], 0) + 1
        if r.get("class") not in PRE_GRANT_CLASSES or r.get("new_target_evaluations") != 0 or \
                r.get("target_equivalent_proxies") != 0 or r.get("target_informed_optimisation", 0) != 0 or \
                r.get("LEAK_FLAG"):
            bad.append(i)
    return {"lines_by_agent": rows, "lines": sum(rows.values()), "bad_line_numbers": bad,
            "pass": sum(rows.values()) > 0 and not bad}


def qc13(pre: dict, cfg: dict, repo: Path = None) -> dict:
    repo = repo or REPO
    D = driver()
    try:
        gov = {"pass": True, **D.check_governance_state()}
    except D.Refusal as exc:
        gov = {"pass": False, "refusal": exc.code}
    led_cfg = cfg["ledger"]
    raw = git_show_bytes(led_cfg["ref"], led_cfg["path"], repo=repo)
    led = ledger_check(None if raw is None else raw.decode(errors="replace"), set(led_cfg["agents"]))
    show = lambda c, p: git_show_bytes(c, p, repo=repo)  # noqa: E731
    anc = lambda c, ref: git_rc("merge-base", "--is-ancestor", c, ref, repo=repo) == 0  # noqa: E731
    recs = [check_record(r, show=show, is_ancestor=anc) for r in cfg["governance_records"]]
    return qc13_core(pre, gov, led, recs)


def qc13_core(pre: dict, gov: dict, led: dict, recs: list) -> dict:
    """PASS iff the preconditions, the governance state (r5, no r6), the ledger and EVERY record hold; a record not
    yet named (PENDING_RECORD: the implementation review, the user's freeze decision) fails closed."""
    out = {"preconditions": pre.get("pass") is True, "governance_state": gov, "ledger": led, "records": recs,
           "pending_records": [r["id"] for r in recs if r.get("status") == "PENDING_RECORD"],
           "temporal_basis": "each record's commit is named in the frozen configuration (Q8-S binds its sha256), so "
                             "it existed before the freeze"}
    out["pass"] = out["preconditions"] and gov.get("pass") is True and led.get("pass") is True and bool(recs) and \
        all(r.get("pass") is True for r in recs)
    return out


# ------------------------------------------------------------------ Q8-S: the freeze manifest
def _get(d, dotted: str):
    for k in dotted.split("."):
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def q8_core(man, *, repo: Path, on_disk: set, expect_ext: dict, expect_commit: dict, expect_recorded: dict,
            bindings_ok: bool, required: list, schema: str) -> dict:
    """The manifest against the bytes, the blobs at HEAD, the writer's own pin sets and the code's recorded values."""
    if not isinstance(man, dict):
        return {"pass": False, "reason": "no freeze manifest"}
    frozen = man.get("frozen_files") or {}
    bad = sorted(rel for rel, v in frozen.items()
                 if not (repo / rel).is_file() or sha((repo / rel).read_bytes()) != v.get("sha256")
                 or git("rev-parse", f"HEAD:{rel}", repo=repo) != v.get("git_blob"))
    listed = set(frozen)
    ext = man.get("external_files") or {}
    bad_ext = []
    for k, (rel, pin_sha, pin_blob) in sorted(expect_ext.items()):
        e = ext.get(k) or {}
        p = repo / rel
        head = git("rev-parse", f"HEAD:{rel}", repo=repo)
        if e.get("path") != rel or not p.is_file() or sha(p.read_bytes()) != e.get("sha256") or \
                (pin_sha is not None and pin_sha != e.get("sha256")) or head != e.get("git_blob") or \
                (pin_blob is not None and not head.startswith(pin_blob)):
            bad_ext.append(k)
    cpf = man.get("commit_pinned_files") or {}
    bad_commit = []
    for k, (c, rel, pin) in sorted(expect_commit.items()):
        e = cpf.get(k) or {}
        b = git("rev-parse", "-q", "--verify", f"{c}:{rel}", repo=repo)
        if e.get("commit") != c or e.get("path") != rel or not b or e.get("git_blob") != b or \
                (pin is not None and e.get("sha256") != pin):
            bad_commit.append(k)
    norm = lambda x: json.loads(json.dumps(x, sort_keys=True))  # noqa: E731
    rec_bad = sorted(k for k, v in expect_recorded.items() if norm(_get(man, k)) != norm(v))
    req_missing = [r for r in required if r not in listed]
    proto = [r for r in listed if r.startswith(NS_REL + "/protocol/MBS308_PROTOCOL") and r.endswith(".md")]
    out = {"frozen_files": len(listed), "mismatches": bad, "unlisted_files": sorted(on_disk - listed),
           "listed_but_absent": sorted(listed - on_disk), "external_files": len(ext), "external_mismatches": bad_ext,
           "external_unexpected": sorted(set(ext) - set(expect_ext)), "commit_pin_mismatches": bad_commit,
           "commit_pins_unexpected": sorted(set(cpf) - set(expect_commit)), "recorded_mismatches": rec_bad,
           "required_missing": req_missing, "protocol_listed": bool(proto), "bindings_ok": bindings_ok,
           "schema_ok": man.get("schema") == schema}
    out["pass"] = not bad and not out["unlisted_files"] and not out["listed_but_absent"] and not bad_ext and \
        not out["external_unexpected"] and len(ext) == len(expect_ext) and not bad_commit and \
        not out["commit_pins_unexpected"] and not rec_bad and not req_missing and bool(proto) and \
        bindings_ok is True and out["schema_ok"]
    return out


def q8_manifest(repo: Path = None, ns: Path = None) -> dict:
    repo, ns = repo or REPO, ns or NS
    import mbs308_manifest as MF
    D = driver()
    mp = ns / "protocol" / "MBS308_FREEZE.json"
    if not mp.exists():
        return {"pass": False, "reason": "no freeze manifest"}
    try:
        man = json.loads(mp.read_bytes())
    except ValueError:
        return {"pass": False, "reason": "the freeze manifest is not JSON"}
    me = sys.modules[__name__]
    try:
        D.check_bindings()
        bind = True
    except (D.Refusal, D.PIN.PinError):
        bind = False
    cfg = load_config(ns / "config" / "MBS308_QUALIFICATION_CASES.json")
    try:
        records = MF.record_blobs(repo, cfg["governance_records"])
    except MF.ManifestRefusal:
        records = {"error": "a governance record does not resolve"}
    expect = {"driver.sha256": sha((ns / "code" / "mbs308_driver.py").read_bytes()),
              "verifier.sha256": sha((ns / "code" / "mbs308_qualify.py").read_bytes()),
              "verifier.cases_config_sha256": sha((ns / "config" / "MBS308_QUALIFICATION_CASES.json").read_bytes()),
              "helper_sha256": dict(D.HELPER_SHA256), "platform_pins": dict(D.PLATFORM_PINS),
              "science_base_commit": D.SCIENCE_BASE_COMMIT, "constants": MF.constants(D),
              "guard.cell308_cover": [str(x) for x in D.GUARD.CELL308],
              "guard.consumed_ref": D.GUARD.CONSUMED_REF, "exactly_once.marker": D.CONSUMED_REF,
              "exactly_once.result": D.RESULT_REL, "exactly_once.qualified_branch": D.QUALIFIED_BRANCH,
              "mbr1_state.target": D.MBR1_MARKER_TARGET, "governance_records": records}
    out = q8_core(man, repo=repo, on_disk={str(p.relative_to(repo)) for p in
                                           MF.namespace_files(ns, mp, D.POST_FREEZE_DIRS)},
                  expect_ext=MF.external_pins(D, me), expect_commit=MF.commit_pins(me), expect_recorded=expect,
                  bindings_ok=bind, required=[NS_REL + "/" + r for r in REQUIRED_FILES], schema=MF.SCHEMA)
    out["manifest_sha256"] = sha(mp.read_bytes())
    return out


# ------------------------------------------------------------------ R-rules: planted controls and the H3 reproduction
def _prep(n: int = 10, spacing: int = 30, *, free=None, power: str = RR.AC, procs=None) -> list:
    """Planted prepared-state readings (test values only)."""
    free = free if free is not None else [4 * RR.GIB] * n
    return [{"t_s": 1000 + i * spacing, "power": power, "free_memory_bytes": free[i],
             "procs": (procs[i] if procs is not None else [])} for i in range(n)]


def _run(rid, cell, jobs, *, driver_peak=64 * RR.MIB, events=(), rerun_of=None, launcher=True, workers=5,
         ladder="frozen", cap=None, poll="2", worker_peak=None) -> dict:
    return {"id": rid, "cell": cell, "launcher": launcher, "ladder": ladder, "workers": workers,
            "mem_cap_bytes": cap if cap is not None else RR.MEASUREMENT_CAP_BYTES * (2 if rerun_of else 1),
            "mem_poll_s": poll, "rerun_of": rerun_of, "watchdog_events": list(events),
            "driver_maxrss_bytes": driver_peak, "worker_peak_rss_bytes": worker_peak,
            "jobs": [{"name": f"{k}.0.{r}", "kind": k, "rung": r, "job_maxrss_bytes": v} for k, r, v in jobs]}


HOST_8G = {"hw_memsize_bytes": 8 * RR.GIB, "wired_pages": 1000, "page_size_bytes": 16384}
SAMPLER_OK = {"interval_s": "0.5", "max_growth_bytes_per_s": 10 * RR.MIB}


def r_rules_planted() -> dict:
    """Every branch of the four rule functions on planted inputs; each expectation is computed here independently
    (exact integers), never by the function under test."""
    M = RR.MIB
    rows = {}

    def rmem(runs, host=HOST_8G, sampler=SAMPLER_OK, cells=(297, 316)):
        return RR.r_mem(runs, required_cells=cells, workers=5, mem_poll_s="2", host=host, sampler=sampler)
    a = rmem([_run("a", 297, [("RLR", 4, 100 * M), ("C2B", 20, 400 * M)]),
              _run("b", 316, [("RLR", 4, 110 * M), ("C2B", 20, 380 * M)])])
    rows["rmem_valid_inputs"] = a["status"] == "OK" and a["P_bytes"] == 400 * M and a["k"] == "3" and \
        a["MEM_CAP_BYTES"] == 1280 * M and a["D_bytes"] == 64 * M and a["feasibility"]["ok"] is True
    b = rmem([_run("a", 297, [("RLR", 4, 100 * M), ("C2B", 20, 400 * M)]),
              _run("b", 316, [("RLR", 4, 200 * M), ("C2B", 20, 400 * M)])])
    rows["rmem_spread_raises_k_to_2s"] = b["status"] == "OK" and b["s"] == "2" and b["k"] == "4" and \
        b["MEM_CAP_BYTES"] == 1792 * M
    c = rmem([_run("a", 297, [("RLR", 4, 50 * M)]), _run("b", 316, [("C2B", 20, 60 * M)])])
    rows["rmem_no_rung_twice_s_is_1_and_floor_1GiB"] = c["status"] == "OK" and c["s"] == "1" and \
        c["MEM_CAP_BYTES"] == RR.GIB
    d = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=[{"worker_pid": 1}]),
              _run("b", 316, [("RLR", 4, 100 * M)])])
    rows["rmem_watchdog_event_is_not_a_valid_input_rerun_doubled"] = d["status"] == "RERUN_REQUIRED" and \
        d["valid"] is False and d["rerun_required"] == [{"id": "a", "cell": 297, "rerun_cap_bytes": 6 * RR.GIB}] and \
        "MEMORY_WATCHDOG_EVENT" in d["invalid_runs"][0]["reasons"]
    d2 = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=[{"worker_pid": 1}]),
               _run("a1", 297, [("RLR", 4, 100 * M)]), _run("b", 316, [("RLR", 4, 100 * M)])])
    rows["rmem_event_run_is_rerun_even_when_its_cell_is_covered"] = d2["status"] == "RERUN_REQUIRED" and \
        d2["valid"] is False and [x["id"] for x in d2["rerun_required"]] == ["a"]
    e = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=[{"worker_pid": 1}]),
              _run("a2", 297, [("RLR", 4, 120 * M)], rerun_of="a"), _run("b", 316, [("RLR", 4, 100 * M)])])
    rows["rmem_rerun_valid_and_invalid_peak_excluded"] = e["status"] == "OK" and e["P_bytes"] == 120 * M and \
        e["valid_runs"] == ["a2", "b"]
    f = rmem([_run("a", 297, [("RLR", 4, 100 * M)], launcher=False, workers=4, ladder="dev", poll="1",
                   cap=RR.GIB), _run("b", 316, [("RLR", 4, 100 * M)])])
    rows["rmem_non_official_run_is_invalid"] = f["valid"] is False and set(f["invalid_runs"][0]["reasons"]) >= {
        "NOT_UNDER_LAUNCHD_LAUNCHER", "WORKERS_NOT_5", "NOT_THE_FROZEN_LADDER", "MEM_POLL_S_NOT_2",
        "MEASUREMENT_CAP_NOT_AS_RULED"}
    g = rmem([_run("a", 297, [("RLR", 4, 2000 * M)]), _run("b", 316, [("RLR", 4, 2000 * M)])])
    rows["rmem_feasibility_fails_on_memory"] = g["status"] == "FAILS_ON_MEMORY" and g["valid"] is False and \
        g["MEM_CAP_BYTES"] == 6144 * M and g["feasibility"]["ok"] is False
    h = rmem([_run("a", 297, [("RLR", 4, 100 * M)]), _run("b", 316, [("RLR", 4, 100 * M)])],
             sampler={"interval_s": "0.5", "max_growth_bytes_per_s": 100 * M})
    rows["rmem_poll_recheck_sets_mem_poll_s"] = h["status"] == "OK" and h["poll"]["recheck_ok"] is False and \
        h["poll"]["MEM_POLL_S"] == RR.fstr(max(F(1, 2), F(RR.GIB, 10) / (100 * M)))
    h2 = rmem([_run("a", 297, [("RLR", 4, 100 * M)]), _run("b", 316, [("RLR", 4, 100 * M)])],
              sampler={"interval_s": "0.5", "max_growth_bytes_per_s": 20 * M})
    rows["rmem_poll_recheck_ok_keeps_mem_poll_s"] = h2["poll"]["recheck_ok"] is True and h2["poll"]["MEM_POLL_S"] == "2"
    i = rmem([_run("a", 297, [("RLR", 4, 100 * M)]), _run("b", 316, [("RLR", 4, 100 * M)])],
             sampler={"interval_s": "1", "max_growth_bytes_per_s": M})
    rows["rmem_sampler_slower_than_half_second_invalid"] = i["status"] == "INVALID_INPUT" and i["valid"] is False
    j = rmem([_run("a", 297, [("RLR", 4, 100 * M)])])
    rows["rmem_plan_cell_without_valid_run_incomplete"] = j["status"] == "INCOMPLETE_INPUT" and j["valid"] is False \
        and j["missing_cells"] == [316]
    rows["rmem_no_valid_input"] = rmem([])["status"] == "NO_VALID_INPUT"
    # R-FREE
    fr = RR.r_free(c, readings=_prep(), workers=5)
    rows["rfree_floor_2GiB"] = fr["FREE_MEM_MIN_BYTES"] == 2 * RR.GIB and fr["status"] == "ATTAINABLE"
    fb = RR.r_free(a, readings=_prep(), workers=5)
    rows["rfree_sum_rounded_up"] = fb["FREE_MEM_MIN_BYTES"] == 3072 * M and fb["sum_bytes"] == 1280 * M + 4 * 400 * M \
        + 64 * M
    lo, hi = 1 * RR.GIB, 4 * RR.GIB
    fu = RR.r_free(a, readings=_prep(free=[hi, hi, lo, hi, hi, lo, hi, hi, lo, hi]), workers=5)
    rows["rfree_never_3_consecutive_gate_unattainable_value_kept"] = fu["status"] == "GATE_UNATTAINABLE" and \
        fu["attainable"] is False and fu["FREE_MEM_MIN_BYTES"] == 3072 * M and fu["longest_consecutive_reaching"] == 2
    fa = RR.r_free(a, readings=_prep(free=[lo, lo, hi, hi, hi, lo, lo, lo, lo, lo]), workers=5)
    rows["rfree_3_consecutive_attainable"] = fa["status"] == "ATTAINABLE" and fa["attainable"] is True
    rows["rfree_fewer_than_10_readings_invalid"] = RR.r_free(a, readings=_prep(9), workers=5)["status"] == \
        "INVALID_READINGS"
    rows["rfree_readings_under_30s_apart_invalid"] = RR.r_free(a, readings=_prep(spacing=29), workers=5)["status"] \
        == "INVALID_READINGS"
    rows["rfree_not_on_ac_invalid"] = RR.r_free(a, readings=_prep(power="Battery Power"), workers=5)["status"] == \
        "INVALID_READINGS"
    rows["rfree_without_r_mem_value"] = RR.r_free(g, readings=_prep(), workers=5)["status"] == "NO_R_MEM_VALUE"
    # R-EXCL-PCT
    host = ["/Applications/Host.app"]

    def hp(v, other=None):
        ps = [{"pid": 1, "comm": "/Applications/Host.app/Contents/MacOS/Host", "pcpu": v}]
        if other:
            ps.append(other)
        return _prep(procs=[ps] * 10)
    x1 = RR.r_excl_pct(hp("25.0"), hosting_app_paths=host)
    rows["rexcl_hosting_app_not_above_25"] = x1["EXCL_CPU_PCT"] == 25 and x1["exception_applied"] is False
    x2 = RR.r_excl_pct(hp("28.4"), hosting_app_paths=host)
    rows["rexcl_single_exception_roundup5"] = x2["EXCL_CPU_PCT"] == 40 and x2["exception_applied"] is True and \
        x2["ceiling_applied"] is False
    x3 = RR.r_excl_pct(hp("44.0"), hosting_app_paths=host)
    rows["rexcl_ceiling_50"] = x3["EXCL_CPU_PCT"] == 50 and x3["ceiling_applied"] is True
    x4 = RR.r_excl_pct(hp("10.0", {"pid": 2, "comm": "/usr/libexec/busyd", "pcpu": "95.0"}), hosting_app_paths=host)
    rows["rexcl_other_process_never_raises_it"] = x4["EXCL_CPU_PCT"] == 25 and x4["exception_applied"] is False
    rows["rexcl_invalid_readings"] = RR.r_excl_pct(_prep(9), hosting_app_paths=host)["status"] == "INVALID_READINGS"
    rows["rexcl_hosting_app_unidentified"] = RR.r_excl_pct(_prep(), hosting_app_paths=[])["status"] == "INVALID_INPUT"
    # R-ALLOW
    procs = [{"pid": 10 + i, "comm": c, "pcpu": v} for i, (c, v) in enumerate([
        ("/System/Library/PrivateFrameworks/P.framework/sysd", "30.0"), ("/usr/libexec/ld1", "30.0"),
        ("/usr/sbin/sb1", "30.0"), ("/sbin/sb2", "30.0"), ("/Library/Apple/System/ap1", "30.0"),
        ("/Applications/App.app/Contents/MacOS/App", "90.0"), ("/Users/u/bin/tool", "90.0"), ("/opt/o/bin/od", "90.0"),
        ("/usr/local/bin/ul", "90.0"), ("/Library/Frameworks/F.framework/fw", "90.0"), ("/usr/bin/ub", "90.0"),
        ("/bin/bb", "90.0"), ("/usr/libexec/python3", "90.0"),
        ("/System/Library/Frameworks/Python.framework/Versions/3.9/bin/python3.9", "90.0"),
        ("/System/Planted/Host.app/Contents/MacOS/Host", "90.0"), ("/private/var/x/nd", "90.0"), ("(kern)", "90.0"),
        ("/usr/libexec/at25", "25.0"), ("/usr/libexec/at251", "25.1"), ("/usr/libexec/WindowServer2", "40")])]
    al = RR.r_allow(_prep(procs=[procs] + [[]] * 9), excl_cpu_pct=25, base_names={"launchd", "WindowServer"},
                    h3_readings=[], hosting_app_paths=["/System/Planted/Host.app"])
    names = {x["name"] for x in al["additions"]}
    why = {x["path"]: x["reason"] for x in al["rejected"]}
    rows["rallow_adds_sip_paths_only"] = names == {"sysd", "ld1", "sb1", "sb2", "ap1", "at251", "WindowServer2"}
    rows["rallow_never_added_classes"] = all(
        why.get(p, "").startswith("NEVER_ADDED_PATH_CLASS") for p in (
            "/Applications/App.app/Contents/MacOS/App", "/Users/u/bin/tool", "/opt/o/bin/od", "/usr/local/bin/ul",
            "/Library/Frameworks/F.framework/fw", "/usr/bin/ub", "/bin/bb"))
    rows["rallow_python_interpreters_never_added"] = why.get("/usr/libexec/python3") == \
        "NEVER_ADDED_PYTHON_INTERPRETER" and \
        why.get("/System/Library/Frameworks/Python.framework/Versions/3.9/bin/python3.9") == \
        "NEVER_ADDED_PYTHON_INTERPRETER"
    rows["rallow_hosting_app_never_added"] = why.get("/System/Planted/Host.app/Contents/MacOS/Host") == \
        "NEVER_ADDED_HOSTING_APP"
    rows["rallow_other_paths_not_added"] = why.get("/private/var/x/nd") == "NOT_UNDER_A_SIP_PROTECTED_OS_PATH" and \
        why.get("(kern)") == "PATH_UNKNOWN"
    rows["rallow_threshold_is_strict"] = "at25" not in names and "at251" in names and "/usr/libexec/at25" not in why
    rows["rallow_base_kept_additions_recorded"] = {"launchd", "WindowServer"} <= set(al["EXCL_ALLOW"]) and all(
        r["path"] and r["reading"] for x in al["additions"] for r in x["records"])
    ar = RR.r_allow(_prep(procs=[procs] + [[]] * 9), excl_cpu_pct=40, base_names=set(), h3_readings=[],
                    hosting_app_paths=["/System/Planted/Host.app"])
    rows["rallow_uses_the_r_excl_pct_output"] = {x["name"] for x in ar["additions"]} == set()
    rows["rallow_invalid_readings"] = RR.r_allow(_prep(9), excl_cpu_pct=25, base_names=set(), h3_readings=[],
                                                 hosting_app_paths=host)["status"] == "INVALID_READINGS"
    try:
        RR.pct(25.1)
        rows["pct_refuses_floats"] = False
    except TypeError:
        rows["pct_refuses_floats"] = True
    return rows


def h3_reproduction(repo: Path = None, cfg: dict = None) -> dict:
    """The ratification's own evidence through R-ALLOW: the H3 readings (transcribed in the configuration and checked
    against the ratification text at 3c2a7854) over the 39 names of 35cabb50, with no other reading above the
    threshold, give exactly the item-16 list applied at b0dd8e93."""
    repo = repo or REPO
    cfg = cfg or load_config()
    pins = {c["key"]: c for c in cfg["commit_pins"]}
    rat = git_show_bytes(pins["constants_ratification"]["commit"], pins["constants_ratification"]["path"], repo=repo)
    old = git_show_bytes(pins["driver_39_names_35cabb50"]["commit"], pins["driver_39_names_35cabb50"]["path"],
                         repo=repo)
    new = git_show_bytes(pins["driver_item16_b0dd8e93"]["commit"], pins["driver_item16_b0dd8e93"]["path"], repo=repo)
    if rat is None or old is None or new is None:
        return {"pass": False, "reason": "a pinned commit file does not resolve"}
    text = rat.decode()
    sec = text.split("* **H3**", 1)[1].split("* **H4**", 1)[0] if "* **H3**" in text else ""
    sec = " ".join(sec.split())
    h3 = cfg["r_allow_h3_readings"]["readings"]
    transcribed = bool(h3) and all(f"{r['name']} " in sec and r["pcpu"] in sec and f"`{r['path']}`" in sec for r in h3)
    base = set(module_constants(old.decode()).get("EXCL_ALLOW") or ())
    item16 = set(module_constants(new.decode()).get("EXCL_ALLOW") or ())
    out = RR.r_allow(_prep(), excl_cpu_pct=RR.EXCL_BASE_PCT, base_names=base, h3_readings=h3,
                     hosting_app_paths=["/Applications/"])
    got = set(out.get("EXCL_ALLOW") or ())
    res = {"h3_transcription_matches_the_ratification": transcribed, "base_names": len(base),
           "additions": sorted(x["name"] for x in out.get("additions", [])), "rejected": len(out.get("rejected", [])),
           "equals_item16_list_at_b0dd8e93": got == item16 and len(item16) == 43}
    res["pass"] = transcribed and len(base) == 39 and res["equals_item16_list_at_b0dd8e93"] and not res["rejected"]
    return res


def r_rules_controls(repo: Path = None, cfg: dict = None) -> dict:
    rows = r_rules_planted()
    h3 = h3_reproduction(repo, cfg)
    return {"controls": rows, "n": len(rows), "failed": sorted(k for k, v in rows.items() if v is not True),
            "h3_reproduction": h3, "rule_numbers_source": RR.RATIFICATION_COMMIT,
            "pass": bool(rows) and all(v is True for v in rows.values()) and h3.get("pass") is True}


# ------------------------------------------------------------------ main
def record_name(case_id: str) -> str:
    return "MBS308_" + case_id.replace("-", "_") + ".json"


def main(argv=None) -> int:  # noqa: C901
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", action="store_true")
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--heavy", action="store_true", help="review: re-run the suites instead of re-summarising them")
    ap.add_argument("--only")
    ap.add_argument("--out")
    ap.add_argument("--work", help="base directory OUTSIDE the repository for sandboxes, the base store and records")
    ap.add_argument("--records", help="review / dev without --heavy: directory of the committed suite records")
    ap.add_argument("--record-scan", action="store_true", help="dev only: run QC12-S's committed-record token scan")
    ap.add_argument("--host-report", action="store_true",
                    help="READ-ONLY host-readiness checklist (protocol section 8.1); prints it (and writes --out)")
    a = ap.parse_args(argv)
    if a.host_report:                                            # read-only; no other mode, nothing changed
        if a.dev or a.review or a.only or a.heavy or a.records or a.record_scan:
            print("QUALIFY REFUSED: --host-report takes only --work / --out")
            return 2
        if a.out and Path(a.out).resolve().is_relative_to(REPO.resolve()):
            print("QUALIFY REFUSED: --out must lie outside the repository")
            return 2
        r = host_report(Path(a.work).resolve() if a.work else None)
        text = json.dumps(r, indent=1, sort_keys=True, default=str)
        if a.out:
            Path(a.out).write_text(text + "\n")
        print(text)
        return 0
    mode = "dev" if a.dev else ("review" if a.review else "official")
    if a.dev and a.review:
        print("QUALIFY REFUSED: --dev and --review exclude each other")
        return 2
    if mode != "official" and not a.out:
        print("QUALIFY REFUSED: --review / --dev write only --out")
        return 2
    if mode == "official" and (a.records or a.record_scan or a.only or a.out or a.heavy):
        print("QUALIFY REFUSED: --records / --record-scan / --only / --out / --heavy are review / dev options")
        return 2
    if a.record_scan and mode != "dev":
        print("QUALIFY REFUSED: --record-scan is a dev option (review runs always scan)")
        return 2
    if not a.work:
        print("QUALIFY REFUSED: --work DIR is required (sandboxes and the separate base store live there)")
        return 2
    for opt in (a.work, a.out, a.records):
        if opt and Path(opt).resolve().is_relative_to(REPO.resolve()):
            print("QUALIFY REFUSED: --work / --out / --records must lie outside the repository")
            return 2
    work_base = Path(a.work).resolve()
    disk0 = disk_check(work_base, "verifier start")          # brief 50: before any other work, in every mode
    if not disk0["pass"]:
        print(f"QUALIFY REFUSED: DISK {json.dumps(disk0['readings'], default=str)}")
        return 2
    t0, started = time.time(), utc()
    cfg = load_config()
    host0 = None
    pre = preconditions(mode)
    if not pre["pass"]:
        print(f"QUALIFY REFUSED: preconditions {json.dumps(pre, default=str)}")
        return 2
    if mode == "official":                                           # the whole official run keeps the host awake
        D = driver()
        host0 = {"keep_awake": D.HOST.keep_awake(), "start": D.HOST.snapshot(), "sampler": D.HOST.Sampler().start()}
    ids = [c["id"] for c in cfg["cases"]]
    sel = ids if mode != "dev" else [i for i in (a.only or "").split(",") if i in ids]
    work_base.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="mbs308q", dir=work_base)).resolve()
    life = SCR.begin(work, f"mbs308_qualify {mode}")          # the verifier's own scratch record (brief 50)
    odir = QDIR if mode == "official" else work
    odir.mkdir(exist_ok=True)
    env = suite_env(work)
    cases: dict = {}
    for cid in sel:
        if cid in PENDING_CASES:
            cases[cid] = pending(cid)
    if "QC09-S" in sel:
        cases["QC09-S"] = qc09_guard(work)
    if "QC11-S" in sel:
        cases["QC11-S"] = qc11_static()
    if "R_RULES_CONTROLS" in sel:
        cases["R_RULES_CONTROLS"] = r_rules_controls(cfg=cfg)
    if "Q8-S" in sel:
        cases["Q8-S"] = q8_manifest()
    if "QC13-S" in sel:
        cases["QC13-S"] = qc13(pre, cfg)
    heavy = mode == "official" or a.heavy
    rdir = Path(a.records).resolve() if a.records else QDIR
    phases = []
    for cid in SUITE_CASES + ("QS-MUTANTS", "QS-RESUME-DECOY"):
        if cid not in sel:
            continue
        if heavy or (cid == "QS-RESUME-DECOY" and mode == "dev"):
            phases.append((cid, cid))
            continue
        try:                                         # re-summarise the committed record (read only)
            rep = json.loads((rdir / record_name(cid)).read_text())
        except (OSError, ValueError):
            rep = None
        if cid == "QS-RESUME-DECOY":
            cases[cid] = resume_decoy_summary(rep, None) | {"record": record_name(cid), "recomputed": False}
            continue
        rel = cfg["suites"][cid]
        cases[cid] = (mutant_summary(rep, declared_mutants(NS / rel), None) if cid == "QS-MUTANTS"
                      else suite_summary(rep, None)) | {"suite": rel, "record": record_name(cid), "recomputed": False}

    def run_phase(cid, _payload):                    # one heavy phase; the suites' own lifecycle records govern
        mine = SCR.begin(Path(env["MBS308_SCRATCH"]), f"mbs308_qualify phase {cid}")
        try:
            out = odir / record_name(cid)
            if cid == "QS-RESUME-DECOY":
                return run_resume_decoy("dev" if mode == "dev" else "official", out, env, work)
            return (run_mutants if cid == "QS-MUTANTS" else run_suite)(cfg["suites"][cid], out, env, work)
        finally:
            SCR.finish(mine)
    gated = SCR.run_gated(phases, gate=lambda name: disk_check(work, name), run=run_phase,
                          verified=lambda r: isinstance(r, dict) and r.get("record_sha256") is not None,
                          clean=lambda name, r: clean_suite_scratch(env))
    cases.update(gated["results"])
    for cid in gated["not_run"]:                     # the disk gate refused: fails closed, never runs
        cases[cid] = {"pass": False, "status": "DISK_REFUSED", "refused_before": gated["refusal"]["phase"]}
    if "QC12-S" in sel:                              # last: the suite records under qualification/ are scanned too
        cases["QC12-S"] = qc12_leak(mode in ("official", "review") or a.record_scan)
    agg = aggregate(cases, cfg, mode)
    host = None
    if host0 is not None:
        D = driver()
        host = dict(D.HOST.provenance(host0["start"], host0["sampler"].stop(), D.HOST.snapshot()),
                    keep_awake=host0["keep_awake"])
    report = {"schema": SCHEMA, "freeze_commit": pre["freeze_commit"], "head": pre["head"],
              "review_mode": mode != "official", "dev_mode": mode == "dev", "cases_selected": sorted(sel),
              "heavy_recomputed": heavy, "preconditions": pre, "cases": cases, **agg,
              "started_utc": started, "finished_utc": utc(), "wall_seconds": round(time.time() - t0, 1),
              "verifier_sha256": sha(HERE.read_bytes()), "rules_sha256": sha((CODE / "mbs308_rrules.py").read_bytes()),
              "cases_config_sha256": sha(CONFIG.read_bytes()), "python": sys.version.split()[0],
              "record_sha256": {p.name: sha(p.read_bytes()) for p in sorted(odir.glob("MBS308_*.json"))
                                if p.name != QUAL_NAME},
              "ledger_entries": [
                  {"agent": "mbs308_qualification", "class": "SYNTHETIC_VALIDATION",
                   "what": "QS-* suites and the mutant matrix (sandboxes on a separate base store, synthetic evaluator "
                           "and launchd payload), QC09-S, R-rule planted controls"},
                  {"agent": "mbs308_qualification", "class": "INFRASTRUCTURE",
                   "what": "QC11-S static, QC12-S leak scans (counts only), QC13-S governance, Q8-S manifest"}],
              "target_evaluations": 0, "host": host,
              "disk": {"threshold_bytes": SCR.QUAL_MIN_FREE_BYTES, "repository_threshold_bytes": SCR.HOST.MIN_FREE_DISK,
                       "start": disk0, "checks": gated["checks"], "cleanups": gated["cleanups"],
                       "refusal": gated["refusal"]}}
    out = Path(a.out) if a.out else odir / QUAL_NAME
    out.write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
    SCR.finish(life)
    tag = lambda v: "PENDING" if v.get("status") == PENDING_STATUS else ("P" if v.get("pass") is True else "F")  # noqa
    print(f"QUALIFICATION {'PASS' if agg['pass'] else ('DEV' if mode == 'dev' else 'FAIL')}: " +
          " ".join(f"{k}={tag(v) if isinstance(v, dict) else '?'}" for k, v in sorted(cases.items())))
    return 0 if agg["pass"] or mode == "dev" else 1


if __name__ == "__main__":
    sys.exit(main())
