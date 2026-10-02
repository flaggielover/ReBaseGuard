"""Cell-308 MB-S successor campaign (r1) -- the qualification verifier (cases in
config/MBS308_QUALIFICATION_CASES.json), modelled on MB r1's mb308_qualify. The framework and the decision-independent
cases are the non-holder builder4's (research brief 46) and builder5's (brief 50); the decision-dependent cases are the
non-holder builder6's (brief 54), built after the user's recorded owner decisions MBS-6 (i), MBS-7 (i), MBS-8 (i) and
section 11.2 option (a) (config `owner_decisions`). NOT frozen: nothing here authorises a freeze, a qualification run
or any target step.

It can NEVER evaluate cell 308 (or 306, 307, 309):
* the suites run in `git clone --shared` sandboxes of a SEPARATE `--no-local` base store under --work, with the
  synthetic evaluator and the synthetic launchd payload;
* QC09-S imports only the guard module and arms it in a throw-away git repository under --work;
* QC11-S reads source text; QC12-S counts pattern / token hits (counts and file names only, never a value); QC13-S
  checks governance records by commit and path (verdict line, pinned sha256 or a named ledger line; nothing printed);
* Q8-S hashes files; R_RULES_CONTROLS runs planted inputs (and committed text) through code/mbs308_rrules.py;
* the science family (MB r1's, carried; MBS-7 (i)): every certifier call is on a declared decoy / validation drift
  outside [6/5, 13/5] (the guard refuses the rest): the official decoys on cover cells 297 and 316 run the real
  driver's `decoy` under the launchd launcher (QC02, QC03; their records also feed QC04, QC08, MBR1_REPRO, Q12_caps
  and R_RULES_OFFICIAL); the consumer runs on cell 305's COMMITTED record only, in reproduction-only mode (QC01
  `rehearse`); QC05 and QC07 run on synthetic sets and manufactured decoy bundles; QC09-SCI checks that every pinned
  code path REFUSES the band in DECOY mode before any work;
* Q12_caps is MB r1's Q12 on the FIXED caps of MBS-8 (i): a pass / fail check that never derives a cap;
  R_RULES_OFFICIAL compares canonical rule outputs exactly (section 11.2 option (a)).
A case listed in PENDING_CASES (none since brief 54) is DECLARED and returns {"pass": false, "status":
"PENDING_USER_DECISION", "depends_on": [...]}.

Modes
  official   HEAD must be the freeze commit; no review / grant / result / marker / campaign ref / spool result; the
             namespace clean (ignored files included); the host ready (protocol section 8 preflight gates without the
             launcher, the platform pins, AC, sleep channels). FIRST the qualification's own prepared-host readings and
             the official decoys, one at a time, with the frozen values; then every other case. Writes
             qualification/MBS308_QUALIFICATION.json and the case records next to it, nothing else in the repository.
  --review   HEAD = freeze or the qualification commit on it; writes only --out (outside the repository); the suites
             and the heavy science records are re-verified from the committed records unless --heavy.
  --dev      development only (never evidence): any HEAD, only the cases named by --only, writes only --out. Its
             report carries dev_mode = true and pass = false by construction of the aggregation. The dev form of the
             decoy cases computes ONLY on decoy 297 block 0 at the development ladder (run directly, 2 workers); the
             rehearsal (cell 305) and the in-process science cases are loader checks in dev (nothing executed).
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
import math
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
import mbs308_derive as DV  # noqa: E402
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
SUITE_CASES = ("QS-STATIC", "QS-STATE", "QS-CRASH", "QS-LAUNCH", "QS-QUALIFY", "QS-DISK", "QS-CASES")
BUILT_CASES = SUITE_CASES + ("QS-MUTANTS", "QC09-S", "QC11-S", "QC12-S", "QC13-S", "Q8-S", "R_RULES_CONTROLS",
                             "QS-RESUME-DECOY",
                             # the decision-dependent cases, built after the user's recorded owner decisions MBS-7 (i),
                             # MBS-8 (i) and section 11.2 option (a) (brief 54; config `owner_decisions`)
                             "QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08", "Q1_theory", "QC09-SCI",
                             "MBR1_REPRO", "Q12_caps", "R_RULES_OFFICIAL")
RESUME_DECOY_RUNNER = "tests/mbs308_resume_decoy.py"        # QS-RESUME-DECOY's case runner (brief 50)
# case -> the decisions it depends on. EMPTY since brief 54: every declared case is built. The mechanism stays: a case
# listed here is DECLARED, never run, and fails closed (`pending`), and the configuration must agree.
PENDING_CASES: dict = {}
REQUIRED_FILES = ("code/mbs308_driver.py", "code/mbs308_guard.py", "code/mbs308_host.py", "code/mbs308_state.py",
                  "code/mbs308_launch.py", "code/mbs308_qualify.py", "code/mbs308_manifest.py",
                  "code/mbs308_rrules.py", "code/mbs308_scratch.py", "code/mbs308_repin.py",
                  "code/mbs308_derive.py", "code/mbs308_measure.py",
                  "config/MBS308_QUALIFICATION_CASES.json", "GUARD_DIFF.md",
                  "DRIVER_DIFF.md",
                  # section 11.2 option (a): the designated pre-freeze measurement evidence and its derivation
                  "evidence_prefreeze/MBS308_RRULES_DESIGNATED.json",
                  "evidence_prefreeze/MBS308_RRULES_DERIVATION.json")


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
    return {"pass": False, "status": PENDING_STATUS, "depends_on": list(PENDING_CASES.get(case_id, ())),
            "case": case_id}


# ------------------------------------------------------------------ aggregation
def config_consistency(cfg: dict) -> dict:
    """The configuration and this verifier agree: every configured case is BUILT here or DECLARED pending here (with
    the same status and dependencies), every case of this verifier is configured, every gate has a case, every case
    names known gates and EVERY case names at least one gate (reviewQ6 F-5: a case without a gate would be ignored by
    the gates, so a failing or a pending one would not fail the qualification)."""
    ids = [c["id"] for c in cfg.get("cases", [])]
    known = set(BUILT_CASES) | set(PENDING_CASES)
    status_bad = sorted(c["id"] for c in cfg.get("cases", []) if c["id"] in known and
                        c.get("status") != ("BUILT" if c["id"] in BUILT_CASES else PENDING_STATUS))
    deps_bad = sorted(c["id"] for c in cfg.get("cases", []) if c["id"] in PENDING_CASES and
                      tuple(c.get("depends_on") or ()) != PENDING_CASES[c["id"]])
    gates = set(cfg.get("gates", {}))
    used = {g for c in cfg.get("cases", []) for g in (c.get("gates") or [])}
    ungated = sorted(c["id"] for c in cfg.get("cases", []) if not c.get("gates"))
    out = {"duplicate_ids": sorted({i for i in ids if ids.count(i) > 1}),
           "unknown_in_config": sorted(set(ids) - known), "missing_from_config": sorted(known - set(ids)),
           "status_mismatch": status_bad, "depends_on_mismatch": deps_bad,
           "gates_without_cases": sorted(gates - used), "unknown_gates": sorted(used - gates),
           "cases_without_gates": ungated}
    out["pass"] = not any(out.values())
    return out


def aggregate(cases: dict, cfg: dict, mode: str) -> dict:
    """Gates from the configuration; every case summary must carry a boolean `pass`. A missing / non-boolean `pass`,
    a configured case that did not run (official / review), an unknown case or a case that belongs to NO gate
    (reviewQ6 F-5) fails LOUDLY (listed and printed)."""
    cons = config_consistency(cfg)
    missing_pass = sorted(k for k, v in cases.items() if not isinstance(v, dict) or not isinstance(v.get("pass"), bool))
    ids = [c["id"] for c in cfg.get("cases", [])]
    not_run = sorted(i for i in ids if i not in cases) if mode != "dev" else []
    unknown = sorted(k for k in cases if k not in ids)
    gated = {c["id"] for c in cfg.get("cases", []) for g in (c.get("gates") or []) if g in cfg.get("gates", {})}
    ungated = sorted(i for i in set(ids) if i not in gated)             # configured cases no gate would ever read
    gates = {}
    for g in sorted(cfg.get("gates", {})):
        members = [c["id"] for c in cfg["cases"] if g in (c.get("gates") or [])]
        gates[g] = {"cases": members, "pass": bool(members) and all(
            isinstance(cases.get(m), dict) and cases[m].get("pass") is True for m in members)}
    pend = sorted(k for k, v in cases.items() if isinstance(v, dict) and v.get("status") == PENDING_STATUS)
    # owner supplement 2 (sections 1 and 3): the distinct fail-closed statuses a case reached are the QUALIFICATION's
    closed = sorted({str(s) for v in cases.values() if isinstance(v, dict)
                     for s in (v.get("fail_closed_statuses") or [])})
    for s in closed:
        print(f"QUALIFY AGGREGATION: FAILED CLOSED {s} (the qualification fails; nothing cures it)", file=sys.stderr)
    for k in missing_pass:
        print(f"QUALIFY AGGREGATION: case {k} carries no boolean `pass` (fails the qualification)", file=sys.stderr)
    for k in not_run + unknown:
        print(f"QUALIFY AGGREGATION: case {k} {'did not run' if k in not_run else 'is not configured'}",
              file=sys.stderr)
    for k in ungated:
        print(f"QUALIFY AGGREGATION: case {k} belongs to no gate (fails the qualification)", file=sys.stderr)
    ok = mode != "dev" and cons["pass"] and not missing_pass and not not_run and not unknown and not closed and \
        not ungated and all(g["pass"] for g in gates.values())
    return {"config_consistency": cons, "gates": gates, "cases_missing_pass": missing_pass, "cases_not_run": not_run,
            "cases_unknown": unknown, "cases_without_gate": ungated, "pending_user_decision": pend,
            "fail_closed_statuses": closed, "pass": ok}


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


HOST_REPORT_STATUSES = DV.HOST_REPORT_STATUSES


def _clamshell(text: str | None = None):
    """The lid: True closed, False open, None unreadable (`ioreg -r -k AppleClamshellState -d 1`, read-only)."""
    import re as _re
    if text is None:
        text = driver().HOST._run(["/usr/sbin/ioreg", "-r", "-k", "AppleClamshellState", "-d", "1"])
    m = _re.search(r'"AppleClamshellState" = (Yes|No)', text or "")
    return None if m is None else m.group(1) == "Yes"


def _pmset_values(text: str | None = None) -> dict:
    """`pmset -g` settings of interest (read-only): autorestart, sleep, displaysleep, disksleep, lowpowermode; each
    None when the output does not state it (`autorestart` is not listed on every Mac). `readable`: the command gave an
    output that states at least one of them (reviewQ6 F-7: an unreadable reading is never RECORDED)."""
    import re as _re
    if text is None:
        text = driver().HOST._run(["/usr/bin/pmset", "-g"])
    out = {}
    for k in ("autorestart", "sleep", "displaysleep", "disksleep", "lowpowermode"):
        m = _re.search(r"^\s*" + k + r"\s+(\d+)", text or "", _re.M)
        out[k] = int(m.group(1)) if m else None
    out["readable"] = any(v is not None for v in out.values())
    return out


def recorded_status(readable: bool) -> str:
    """A recorded (ungated) item of the host report: RECORDED only when its readings were actually read."""
    return "RECORDED" if readable is True else "UNKNOWN"


def exclusive_status(busy) -> str:
    """host_exclusive in the host report: READY needs a positive reading (a `ps` listing with no busy process); no
    reading (None) is UNKNOWN, never READY."""
    if not isinstance(busy, list):
        return "UNKNOWN"
    return "READY" if not busy else "USER_ACTION"


def pidfile_status(state) -> str:
    """no_other_campaign_job in the host report: READY needs a positive reading (no pidfile, or one whose recorded
    process is positively dead); a live one is NOT_READY; anything else (a recorded process that is not positively
    dead, an invalid pidfile, an unknown state) is UNKNOWN, never READY."""
    return {"ABSENT": "READY", "STALE": "READY", "LIVE": "NOT_READY"}.get(state, "UNKNOWN")


def _pmset_sched(text: str | None = None) -> dict:
    """`pmset -g sched` (read-only): the scheduled and repeating power events, by TYPE only (wake, sleep, restart,
    shutdown, poweron, wakeorpoweron); None when unreadable. A restart hazard is a scheduled restart / shutdown /
    sleep."""
    import re as _re
    if text is None:
        text = driver().HOST._run(["/usr/bin/pmset", "-g", "sched"])
    if text is None:
        return {"readable": False, "event_types": None, "restart_shutdown_or_sleep_scheduled": None}
    types = [m.group(1).lower() for m in _re.finditer(
        r"^\s*(?:\[\d+\]\s+)?(wakeorpoweron|wakepoweron|poweron|wake|sleep|restart|shutdown)\b", text, _re.M | _re.I)]
    return {"readable": True, "event_types": sorted(types),
            "restart_shutdown_or_sleep_scheduled": any(t in ("restart", "shutdown", "sleep") for t in types)}


# Owner decisions section 14 ("FINAL HOST PREFLIGHT ... Immediately before target consumption verify all frozen
# requirements, including: ..."), item by item (brief 54, part C2): the existing gate or recorded reading that covers
# it. A gate exists only where an accepted text already makes it one; the two items without one ("required lid/sleep
# state", "restart hazards controlled") are READ-ONLY recorded readings of --host-report plus an operator line.
# (item as the owner record words it, kind, what covers it, driver / host names that must exist, host-report items,
#  operator checklist line or None)
OWNER_SECTION14 = (
    ("AC power", "GATE", "the driver's preflight gate `ac_power` and `require_ac` in pre_marker_common (execute and "
     "every resume refuse before the marker / before the attempt counter moves)", ("ac_power", "require_ac"),
     ("ac_power",), None),
    ("required lid/sleep state", "RECORDED_READING", "no accepted text makes the lid a gate (protocol 8.1: caffeinate "
     "cannot stop lid-close sleep; keeping the lid open is a user action): --host-report reads, read-only, the lid "
     "(ioreg AppleClamshellState) and the sleep / displaysleep / disksleep timers (pmset -g) and whether the sleep "
     "channels K / S / L are available; after the start any sleep is detected by K / S / L and recorded in the sealed "
     "record", ("kern_times", "log_events"), ("sleep_prevention_and_lid",),
     "the lid is open and the host is on AC before the launch and stays so until the seal"),
    ("sleep prevention", "MECHANISM", "the supervised `caffeinate -i -m -s -w <pid>` started by keep_awake in "
     "pre_marker_common (re-spawned whenever it dies; every death and re-spawn recorded durably and in the sealed "
     "record)", ("keep_awake", "CaffeinateSupervisor"), ("sleep_prevention_and_lid",), None),
    ("automatic macOS/critical-update installation disabled as required", "GATE", "the driver's preflight gate "
     "`no_automatic_os_install` (DR2 c: AutomaticallyInstallMacOSUpdates and CriticalUpdateInstall must be 0; a missing "
     "key is enabled); read-only: disabling them is the user's action", ("no_automatic_os_install",),
     ("automatic_os_installation_disabled",), None),
    ("restart hazards controlled", "RECORDED_READING", "update-triggered restarts are excluded by the gate "
     "`no_automatic_os_install`; --host-report reads, read-only, `pmset -g` autorestart and the scheduled power events "
     "(`pmset -g sched`: a scheduled restart / shutdown / sleep is a hazard); any restart is detected by the boot UUID "
     "and classified CONSUMED_INTERRUPTED (resumable within the frozen budget), never a result",
     ("no_automatic_os_install", "boot_session_uuid"), ("automatic_restart",),
     "no restart, shutdown or sleep is scheduled and no update restart is pending from the launch to the seal"),
    ("thermal state", "GATE", "the driver's preflight gate `thermal_pressure_0` (recorded after the marker, never "
     "gating)", ("thermal_pressure_0",), ("thermal_level_0",), None),
    ("memory pressure", "GATE", "the driver's preflight gates `memory_pressure_normal` and `free_memory_ge_min`",
     ("memory_pressure_normal", "free_memory_ge_min"), ("memory_pressure_normal", "free_memory"), None),
    ("free disk >= frozen threshold", "GATE", "the driver's preflight gate `free_disk_ge_2GiB` (MIN_FREE_DISK; a "
     "failed probe fails closed)", ("free_disk_ge_2GiB", "MIN_FREE_DISK"), ("disk_execution",), None),
    ("host identity", "GATE", "check_platform (the pinned interpreter and libpython with their sha256, the OS build, "
     "the architecture: the qualification host) and check_identity (the qualified worktree, git dir, common dir and "
     "branch)", ("check_platform", "check_identity"), ("host_identity_platform_pins",), None),
    ("boot identity", "GATE", "the driver's preflight gate `boot_uuid_recorded`; the journal and every process "
     "identity carry the boot UUID", ("boot_uuid_recorded",), ("boot_identity",), None),
    ("platform pins", "GATE", "check_platform at preflight, execute, every resume and every computing mode (RC2 / "
     "DR2)", ("check_platform", "PLATFORM_PINS"), ("host_identity_platform_pins",), None),
    ("Git configuration safety", "GATE", "check_seal_preconditions (committer / author identity; the object store "
     "writable, a private index and a trial commit object with the current configuration; the branch ref; the git "
     "dir writable), check_clean (the tree clean, ignored files included; no index / HEAD / branch / packed-refs "
     "lock), check_not_evaluated (no campaign lockfile), and the driver's own fixed git environment "
     "(GIT_NO_REPLACE_OBJECTS=1, GIT_OPTIONAL_LOCKS=0; every durable write passes core.fsync / core.fsyncMethod "
     "explicitly); no accepted text names a further git setting", ("check_seal_preconditions", "check_clean",
                                                                   "check_not_evaluated"), (), None),
    ("no stale/conflicting driver", "GATE", "the preflight gate `no_other_campaign_job` (a LIVE pidfile refuses), "
     "check_not_evaluated (a journal that is not a stale pre-marker intent refuses; campaign lockfiles refuse), "
     "check_helpers and check_grant (the driver and helper bytes are the granted, pinned bytes), the O_EXCL lock",
     ("no_other_campaign_job", "check_not_evaluated", "check_helpers", "check_grant"), ("no_other_campaign_job",),
     None),
    ("exact frozen commit", "GATE", "check_grant (HEAD is the grant commit on the chain freeze -> qualification -> "
     "review -> grant as the grant names it; the driver sha256 and the freeze manifest bound), check_clean and "
     "check_bindings (every pinned file equals its blob at HEAD)", ("check_grant", "check_clean", "check_bindings"),
     (), None),
    ("no existing MB-S marker", "GATE", "check_not_evaluated (any ref under refs/p5y-k5-cell308-mbs-r1/ other than a "
     "stale pre-marker intent refuses: CONSUMED) and the marker's compare-and-swap from zero",
     ("check_not_evaluated", "CONSUMED_REF"), (), None),
    ("no pending-result state", "GATE", "check_not_evaluated (the pending-result ref refuses: CONSUMED; a result in "
     "the tree, in history or in the spool refuses: TARGET_ARTIFACT_EXISTS)", ("check_not_evaluated", "PENDING_REF"),
     (), None),
    ("successor target count still zero", "GATE", "check_not_evaluated (no MB-S marker, journal attempt, checkpoint, "
     "pending result or result exists: zero successor target evaluations) and check_mbr1_state (MB r1's recorded "
     "state exactly: cell 308 consumed once, by MB r1)", ("check_not_evaluated", "check_mbr1_state"), (), None),
)


def owner_section14() -> list:
    return [{"item": i, "kind": k, "covered_by": how, "names": list(names), "host_report_items": list(items),
             "operator_checklist": op} for i, k, how, names, items, op in OWNER_SECTION14]


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
    sched = _pmset_sched()
    item("automatic_restart", "recorded (no gate): a restart is a reboot, detected by the boot UUID and resumable; "
         "the scheduled power events are read by `pmset -g sched` (owner decisions section 14: restart hazards)",
         recorded_status(pm["readable"] and sched["readable"] is True),
         {"autorestart": pm["autorestart"], "pmset_readable": pm["readable"], "scheduled_power_events": sched},
         "automatic restarts by an OS update are excluded by the previous item; a scheduled restart / shutdown / sleep "
         "is for the operator to cancel (a user action; the campaign never changes it)")
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
         "R-ALLOW at the freeze)", exclusive_status(busy),
         [b["comm"] for b in busy] if isinstance(busy, list) else None,
         "quit the listed apps (a user action); a process is never allow-listed by hand; no `ps` reading is UNKNOWN "
         "(the gate itself refuses)")
    rec, pst = D.STATE.read_pidfile(D.store())
    if pst == "STALE" and D.HOST.identity_state(rec["identity"]) != "DEAD":
        pst = "UNKNOWN"                              # as the gate reads it: STALE only on positive evidence of death
    item("no_other_campaign_job", "existing gate: preflight no_other_campaign_job", pidfile_status(pst), pst,
         "READY needs a positive reading: no pidfile, or a recorded process that is positively dead")
    return {"schema": DV.HOST_REPORT_SCHEMA, "read_only": True,
            "changes_made": False, "utc": utc(), "items": items,
            "owner_section14": owner_section14(),
            "operator_actions": json.loads(json.dumps(DV.OPERATOR_ACTIONS)),
            "ready": all(i["status"] in ("READY", "RECORDED") for i in items)}


def host_report_record(work: Path | None = None) -> dict:
    """The read-only host report as it is EMBEDDED in a record (the official qualification record, its rule-input
    record, the designated-measurement evidence): a report that could not be taken is recorded as such, and the
    record's structure check (mbs308_derive.host_report_reasons) then fails."""
    try:
        return host_report(work)
    except Exception as exc:                                          # noqa: BLE001 (recorded; the check fails)
        return {"error": f"{type(exc).__name__}: {exc}"[:300], "read_only": True, "changes_made": False}


def official_inputs(rin: dict, runs: list, host_rep) -> dict:
    """The official qualification's rule-input record (qualification/MBS308_RRULES_OFFICIAL_INPUTS.json): its own
    prepared-host readings, the compact inputs of its official decoys, and the embedded read-only host report taken
    before them."""
    return dict(rin, runs=runs, host_report=host_rep, target_evaluations=0)


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
    """(non-exempt matches, matches exempted as timing fields). Every file is scanned as raw text. A JSON file is
    ALSO scanned as the parser reads it (its DECODED keys and string values, wherever the file lies): a figure written
    with a JSON escape has no raw-text match and would otherwise pass unseen. Only machine-written JSON evidence under
    the post-freeze directories may exempt a match located ONLY inside a timing key (TIMING_KEYS, any depth); every
    other file is scanned without exemption; a raw-text-only match is never exempt."""
    n = len(rx.findall(text))
    if not rel.endswith(".json"):
        return n, 0
    try:
        obj = json.loads(text)
    except ValueError:
        return n, 0
    full = len(rx.findall(json.dumps(obj, sort_keys=True)))        # the record as decoded (escapes resolved)
    parts = Path(rel).relative_to(ns_rel).parts if rel.startswith(ns_rel + "/") else ()
    if not parts or parts[0] not in post_dirs:
        return max(n, full), 0                                     # no exemption outside the post-freeze directories
    kept = len(rx.findall(json.dumps(strip_timing(obj), sort_keys=True)))
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
    escaped = ("\\u%04x" % ord(one[0]) + one[1:]) if one else ""     # the same figure, its first character JSON-escaped
    ctl = {"planted_control_fires": len(rx.findall("row " + planted + " end")) >= 3,
           "planted_json_escaped_value_in_evidence_fires": bool(escaped) and not rx.findall(escaped) and
           tail_hits(rec_rel, '{"record": {"value": "' + escaped + '"}}', rx, post_dirs, ns_rel)[0] > 0 and
           tail_hits(ns_rel + "/config/PLANTED.json", '{"value": "' + escaped + '"}', rx, post_dirs, ns_rel)[0] > 0,
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
    try:
        owner = MF.owner_records(repo, D.S1_OWNER_RECORDS)
    except MF.ManifestRefusal:
        owner = {"error": "an owner record does not resolve or differs from its digest"}
    expect = {"driver.sha256": sha((ns / "code" / "mbs308_driver.py").read_bytes()),
              "verifier.sha256": sha((ns / "code" / "mbs308_qualify.py").read_bytes()),
              "verifier.cases_config_sha256": sha((ns / "config" / "MBS308_QUALIFICATION_CASES.json").read_bytes()),
              "helper_sha256": dict(D.HELPER_SHA256), "platform_pins": dict(D.PLATFORM_PINS),
              "science_base_commit": D.SCIENCE_BASE_COMMIT, "constants": MF.constants(D),
              "guard.cell308_cover": [str(x) for x in D.GUARD.CELL308],
              "guard.consumed_ref": D.GUARD.CONSUMED_REF, "exactly_once.marker": D.CONSUMED_REF,
              "exactly_once.result": D.RESULT_REL, "exactly_once.qualified_branch": D.QUALIFIED_BRANCH,
              "mbr1_state.target": D.MBR1_MARKER_TARGET, "governance_records": records,
              "s1_owner_records": owner}
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
SAMPLER_OK = {"interval_s": "0.25", "max_spacing_ns": 300_000_000, "max_growth_bytes_per_s": 10 * RR.MIB}


def r_rules_planted() -> dict:
    """Every branch of the four rule functions on planted inputs; each expectation is computed here independently
    (exact integers), never by the function under test."""
    M = RR.MIB
    rows = {}

    def rmem(runs, host=HOST_8G, sampler=SAMPLER_OK, cells=(297, 316), poll="2", **kw):
        return RR.r_mem(runs, required_cells=cells, workers=5, mem_poll_s=poll, host=host, sampler=sampler, **kw)

    def smp(g, gap=300_000_000, iv="0.25"):
        return {"interval_s": iv, "max_spacing_ns": gap, "max_growth_bytes_per_s": g}
    ok2 = [_run("a", 297, [("RLR", 4, 100 * M)]), _run("b", 316, [("RLR", 4, 100 * M)])]     # MEM_CAP = 1 GiB
    ev = [{"worker_pid": 1, "rss_bytes": 4 * RR.GIB, "cap_bytes": 3 * RR.GIB, "killed": True}]
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
    # "within the step-5 bound" (readings R1, item 5 (a)): the doubled cap in MEM_CAP's place, the VALID runs' P and D
    bd = d.get("rerun_step5_bound") or {}
    rows["rmem_rerun_bound_from_the_valid_runs"] = bd.get("defined") is True and bd.get("P_bytes") == 100 * M and \
        bd.get("D_bytes") == 64 * M and bd.get("lhs_bytes") == 6 * RR.GIB + 4 * 100 * M + 64 * M and \
        bd.get("rhs_bytes") == 8 * RR.GIB - 1000 * 16384 and bd.get("within") is True and "stop" not in bd
    d3 = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=ev), _run("b", 316, [("RLR", 4, 500 * M)])])
    bd3 = d3.get("rerun_step5_bound") or {}
    rows["rmem_rerun_cap_not_within_the_bound_stops"] = d3["status"] == "RERUN_REQUIRED" and \
        bd3.get("within") is False and bd3.get("lhs_bytes") == 6 * RR.GIB + 4 * 500 * M + 64 * M and "stop" in bd3
    d4 = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=ev)])
    bd4 = d4.get("rerun_step5_bound") or {}
    rows["rmem_rerun_bound_undefined_without_a_valid_run_is_the_owners"] = d4["status"] == "RERUN_REQUIRED" and \
        bd4.get("defined") is False and bd4.get("within") is None and bd4.get("open_point") == RR.OPEN_RERUN_BOUND
    # F-6 as ruled (readings R1, item 4; owner supplement 2, section 6): a clean duplicate of the cell cures nothing
    d2 = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=[{"worker_pid": 1}]),
               _run("a1", 297, [("RLR", 4, 100 * M)]), _run("b", 316, [("RLR", 4, 100 * M)])])
    rows["rmem_event_run_is_rerun_even_when_its_cell_is_covered"] = d2["status"] == "RERUN_REQUIRED" and \
        d2["valid"] is False and [x["id"] for x in d2["rerun_required"]] == ["a"] and d2["missing_cells"] == [] and \
        "MEM_CAP_BYTES" not in d2 and d2["uncured_event_runs"] == ["a"]
    d5 = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=ev),
               _run("a2", 297, [("RLR", 4, 120 * M)], rerun_of="a", cap=3 * RR.GIB), _run("b", 316, [("RLR", 4, 100 * M)])])
    rows["rmem_rerun_not_at_the_doubled_cap_cures_nothing"] = d5["status"] == "RERUN_REQUIRED" and \
        d5["uncured_event_runs"] == ["a"] and "MEM_CAP_BYTES" not in d5
    d6 = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=ev),
               _run("a2", 297, [("RLR", 4, 950 * M)], rerun_of="a", events=ev), _run("b", 316, [("RLR", 4, 100 * M)])])
    rows["rmem_second_event_no_further_doubling"] = d6["status"] == "RERUN_REQUIRED" and \
        d6["rerun_required"] == [{"id": "a2", "cell": 297, "rerun_cap_bytes": 6 * RR.GIB}] and \
        d6["uncured_event_runs"] == ["a", "a2"]
    d7 = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=[{"event": RR.BROKEN_POOL_EVENT, "worker_pid": 1}]),
               _run("b", 316, [("RLR", 4, 100 * M)])])
    rows["rmem_broken_pool_release_is_not_a_watchdog_event"] = d7["status"] == "INCOMPLETE_INPUT" and \
        d7["invalid_runs"][0]["reasons"] == ["WORKER_KILLED_AFTER_A_BROKEN_POOL"] and d7["rerun_required"] == []
    # owner supplement 2, sections 1 and 6: the OFFICIAL series (after the freeze) has no re-run and no cure
    o1 = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=ev), _run("b", 316, [("RLR", 4, 100 * M)])], official=True)
    rows["rmem_official_event_fails_closed_no_rerun"] = o1["status"] == RR.STATUS_OFFICIAL_WATCHDOG and \
        o1["valid"] is False and o1["rerun_required"] == [] and "rerun_step5_bound" not in o1 and \
        o1["event_runs"] == ["a"] and "MEM_CAP_BYTES" not in o1
    o2 = rmem([_run("a", 297, [("RLR", 4, 900 * M)], events=ev), _run("a1", 297, [("RLR", 4, 100 * M)]),
               _run("a2", 297, [("RLR", 4, 100 * M)], rerun_of="a"), _run("b", 316, [("RLR", 4, 100 * M)])],
              official=True)
    rows["rmem_official_event_not_cured_by_duplicate_or_doubled_cap"] = o2["status"] == RR.STATUS_OFFICIAL_WATCHDOG \
        and o2["event_runs"] == ["a"] and any(
            x["id"] == "a2" and "RERUN_NOT_PERMITTED_AFTER_THE_FREEZE" in x["reasons"] and
            "MEASUREMENT_CAP_NOT_AS_RULED" in x["reasons"] for x in o2["invalid_runs"])
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
    # step 6 (readings R1, item 6; owner supplement 2, sections 2 and 3): the three cases
    h = rmem(ok2, sampler=smp(100 * M))             # 100 MiB/s x 2 s > 102.4 MiB; 0.1 x 1 GiB / g = 1.024 s > 0.5 s
    rows["rmem_poll_noncanonical_branch_stops_no_value"] = h["status"] == RR.STATUS_POLL_NONCANONICAL and \
        h["valid"] is False and h["poll"]["recheck_ok"] is False and h["poll"]["case"] == "iii" and \
        h["poll"]["canonical"] is False and h["poll"]["MEM_POLL_S"] is None and \
        h["poll"]["unrounded_quotient_not_an_output"] == "128/125" and h["MEM_CAP_BYTES"] == RR.GIB
    h2 = rmem(ok2, sampler=smp(20 * M))
    rows["rmem_poll_recheck_ok_keeps_mem_poll_s"] = h2["status"] == "OK" and h2["poll"]["recheck_ok"] is True and \
        h2["poll"]["MEM_POLL_S"] == "2" and h2["poll"]["case"] == "i" and h2["poll"]["canonical"] is True
    h3 = rmem(ok2, sampler=smp(300 * M))            # 0.1 x 1 GiB / (300 MiB/s) = 0.341 s <= 0.5 s: the clip
    rows["rmem_poll_clips_to_half_a_second"] = h3["status"] == "OK" and h3["poll"]["recheck_ok"] is False and \
        h3["poll"]["MEM_POLL_S"] == "1/2" and h3["poll"]["case"] == "ii" and h3["poll"]["canonical"] is True
    h4 = rmem(ok2, sampler=smp(F(RR.GIB, 20)))      # g x 2 s == 0.1 x MEM_CAP exactly: the inequality holds
    h5 = rmem(ok2, sampler=smp(F(RR.GIB, 5)))       # 0.1 x MEM_CAP / g == 0.5 s exactly: the clip, not the quotient
    rows["rmem_poll_boundaries_exact"] = h4["poll"]["case"] == "i" and h4["poll"]["MEM_POLL_S"] == "2" and \
        h5["poll"]["case"] == "ii" and h5["poll"]["MEM_POLL_S"] == "1/2" and h5["status"] == "OK"
    h6 = rmem(ok2, sampler=smp(100 * M), poll="1/2")    # the official re-check of a frozen 0.5 s: 50 MiB <= 102.4 MiB
    h7 = rmem(ok2, sampler=smp(300 * M), poll="1/2")    # ... failing: max(0.5, 0.341) = 0.5 s again
    rows["rmem_poll_rechecks_the_value_given"] = h6["poll"]["case"] == "i" and h6["poll"]["MEM_POLL_S"] == "1/2" and \
        h7["poll"]["case"] == "ii" and h7["poll"]["MEM_POLL_S"] == "1/2"
    # READING-6 as corrected (readings R1, item 2; owner supplement 2, section 5): the OBSERVED spacing binds
    i = rmem(ok2, sampler=smp(M, iv="1"))
    rows["rmem_sampler_slower_than_half_second_invalid"] = i["status"] == "INVALID_INPUT" and i["valid"] is False \
        and i["reason"] == "SAMPLER_INTERVAL_ABOVE_0.5_S"
    i2 = rmem(ok2, sampler=smp(M, gap=500_000_000))
    i3 = rmem(ok2, sampler=smp(M, gap=500_000_001))
    rows["rmem_sampler_observed_spacing_binds_exactly_half_a_second_is_within"] = i2["status"] == "OK" and \
        i3["status"] == "INVALID_INPUT" and i3["reason"] == "SAMPLER_OBSERVED_SPACING_ABOVE_0.5_S" and \
        "poll" not in i3 and i3["valid"] is False
    i4 = rmem(ok2, sampler={"interval_s": "0.25", "max_growth_bytes_per_s": M})
    i5 = rmem(ok2, sampler=smp(M, gap=None))
    rows["rmem_sampler_observed_spacing_unrecorded_invalid"] = all(
        x["status"] == "INVALID_INPUT" and x["reason"] == "SAMPLER_OBSERVED_SPACING_UNRECORDED" and "poll" not in x
        for x in (i4, i5))
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


# ====================================================================== the decision-dependent cases (brief 54)
# Built by the non-holder builder6 after the user's recorded owner decisions (config `owner_decisions`): MBS-6 (i),
# MBS-7 (i) (the science unchanged: MB r1's frozen qualification cases carried, re-targeted to the successor identity),
# MBS-8 (i) (MB r1's r3 caps, FIXED: Q12 is a prospective pass / fail check and never derives a cap) and section 11.2
# option (a) (R_RULES_OFFICIAL: exact agreement of the canonical rule outputs). MB r1's implementation
# (p5y_k5_cell308_mb_r1/code/mb308_qualify.py at 21e99cf0) is carried function by function; every deviation is
# listed in BUILD_REPORT section 17.
OUTS = {"rehearse": "MBS308_QC01_REHEARSE_305.json", "decoy297": "MBS308_QC02_DECOY_297.json",
        "decoy316": "MBS308_QC03_DECOY_316_B3.json", "serial": "MBS308_QC04_SERIAL_297_B0.json",
        "det_a": "MBS308_QC04_LADDER_DET_A.json", "det_b": "MBS308_QC04_LADDER_DET_B.json",
        "mc": "MBS308_QC08_MC.json", "asm_controls": "MBS308_QC07_E4.json",
        "rinputs": "MBS308_RRULES_OFFICIAL_INPUTS.json"}
SCIENCE_DECOY_CASES = ("QC02", "QC03", "QC04", "QC08", "MBR1_REPRO", "Q12_caps", "R_RULES_OFFICIAL")
SCIENCE_INPROCESS_CASES = ("QC05", "QC06", "QC07", "QC09-SCI")
LADDER_DET_DRIFTS = ("3", "11/10")                      # MB r1's QC04 (b): one dyadic, one non-dyadic declared drift
DEV_STATUS = "DEV_FORM"                                 # a dev-form summary is never evidence: its `pass` is false
# MB r1's qualification test modules: executed from MB r1's COMMITTED bytes at MB r1's paths (sha256 and blob at
# 21e99cf0, checked against HEAD), exactly as the driver executes MB r1's science modules; nothing is copied
MBR1_TEST_PINS = {
    "test_mb308_twosided": (NSF_REL + "/tests/test_mb308_twosided.py",
                            "e71b12fa7c29261ad0b4ad561c24133a54cc60464d0fc0ca68ca56d055afc8d8",
                            "bf34580a1d555cde785303dbb987a6d33e9c7183"),
    "test_mb308_a0": (NSF_REL + "/tests/test_mb308_a0.py",
                      "be7ca5a7f3e73432ee1d7dd7c2a597c6bc41ef09557643234c3a7b4c1c5b98eb",
                      "716575b4933c98ba3f30d15cc635ff55e2428c0a"),
    "test_mb308_tptb": (NSF_REL + "/tests/test_mb308_tptb.py",
                        "44ea60ac0e28222c365a78fd6c8a92b7f8f72ab2ebc0e70619dcde05e07faec9",
                        "6070ca944ef2de0de6ec28d5192cfc6cadd5faba"),
    "test_mb308_guard": (NSF_REL + "/tests/test_mb308_guard.py",
                         "a64ac7865ec2af48eb18531b48aacac19bf0329d7d31e5ea9b0e390a588fd52f",
                         "bc463e3f4b0f0d6b79fd640e6db4d69c88c3034d"),
}
MBR1_TEST_ENTRY = {   # module -> (entry function, its parameters as MB r1's verifier calls it)
    "test_mb308_twosided": ("composition_test", ("SUP", "S1M", "S1", "IND", "IND7", "cp", "con", "guard")),
    "test_mb308_a0": ("run", ("PIN", "A0C", "c1b", "c2b", "guard", "fd_stride", "scan_points", "byte", "S1M", "vf")),
    "test_mb308_tptb": ("run", ("CON", "asm", "guard", "indep", "DG")),
    "test_mb308_guard": ("run", ("read_pinned", "mods")),
}
MC_PIN = (CP + "p5y_k5_cell307_rlr_r1/tests/test_rlr307_mc.py",
          "811c929acabbdde16ce181f22e66cd7ce9f840c7777add71c632140f7eb348fb",
          "b486a5f695882ae9e23f88702234b97fc2daf0c3")
E4_PIN = (RS + "streams/ASSEMBLY/controls.py", "801fb5ab3450407dd478ef26331f964a8cd27abee3c00768c3fc8a0c95946519",
          "4c42c56af95c3d61d0d86551ea45bd5ad8349692")
A0_R_EVAL_PIN = (RS + "reviews/scratch_A0_R1/r_eval.py",
                 "2fdfe516ceb137f23658d5b0156ed88bdc41602f268e015923e77514eb8dd789",
                 "16efeb208f18670cad3b51601e66372d668108e0")
A0_CERTS = ("C2BX_SUPER_e3_N20_detA.json", "C2BX_SUB_e3_N20_detA.json", "C1B_SUPER_e3_d8_detA.json",
            "C2BX_SUPER_e11_10_N20.json", "C2BX_SUB_e11_10_N20.json")
# Q1: MB r1's NSF copy of THEOREM_MB r1 (the theorem MB-S's unchanged science proves; MBS-7 (i)) must be byte-identical
# to the research file as committed at bfa9ad3c
THEORY_REL = NSF_REL + "/theory/THEOREM_MB.md"
THEORY_RESEARCH = (RS + "theory/THEOREM_MB.md", "bfa9ad3c",
                   "f1c767dccc0bb3738fcae350530d4dda13c8b9db482ffb25528376502f4d0d25",
                   "2ee1a41bccd26c32f2bb150b5f2ad6df856ff3a9")
# MBR1_REPRO (RC2): MB r1's COMMITTED official r3 records, the comparison inputs (sha256 and blob at 21e99cf0)
MBR1_RECORD_PINS = {
    "decoy297": (NSF_REL + "/qualification/MB308_QC02_DECOY_297.json",
                 "14e1ac26e483f90e7845eab92d7e6ff629e497a6ca9ba521b4b7aca734e04f02",
                 "1096a8533a2cbe80aa9550be80cddfc532d0a6ea"),
    "decoy316": (NSF_REL + "/qualification/MB308_QC03_DECOY_316_B3.json",
                 "678025c1420f6162047a441d8ee60b384cbcdb85d028a929a3680cc581922998",
                 "581843963b8cd8821e678ed8dba58e4a166dd041"),
    "serial": (NSF_REL + "/qualification/MB308_QC04_SERIAL_297_B0.json",
               "d697870767caab5a2771a6c0772c15d0e7485280e7110821d73ae654b7227671",
               "26e1b0c845703f8fd871aa03c0aaf0548821d697"),
    "det_a": (NSF_REL + "/qualification/MB308_QC04_LADDER_DET_A.json",
              "fc6d02271aa7f6d049b0029e764153e4c09d2f2f030fcecc5e7021979940f540",
              "e8be508c567d94912b814671069cc9caef882238"),
    "det_b": (NSF_REL + "/qualification/MB308_QC04_LADDER_DET_B.json",
              "e3952991a0a3815de660afe5457fe3857bc0d1f6bee85c379c58840cdade8cb5",
              "f51dd0eeee4895451dbb0443dfad0a9103e94700"),
}
EXTERNAL_PINS.update({f"qualify:mbr1_test:{k}": v for k, v in MBR1_TEST_PINS.items()})
EXTERNAL_PINS.update({f"qualify:mbr1_record:{k}": v for k, v in MBR1_RECORD_PINS.items()})
EXTERNAL_PINS.update({"qualify:mc_307": MC_PIN, "qualify:e4_controls": E4_PIN, "qualify:a0_r_eval": A0_R_EVAL_PIN,
                      "qualify:theorem_mb": (THEORY_REL, THEORY_RESEARCH[2], THEORY_RESEARCH[3]),
                      "qualify:theorem_mb_research": (THEORY_RESEARCH[0], THEORY_RESEARCH[2], THEORY_RESEARCH[3])})
EXTERNAL_PINS.update({f"qualify:a0_cert:{n}": (RS + "streams/A0/certs/" + n, None, None) for n in A0_CERTS})
# Q12 (MB r1 protocol 3.2): the cell-308 Stage-1 job set and the projection's scheduling model
Q12_BLOCKS = 11
Q12_KEYS = (("RLR", 4), ("RLR", 6), ("RLR", 8), ("C2B", 20), ("C2B", 40), ("C2B", 80), ("C1B", 8), ("C1B", 10),
            ("C1B", 12))


def pinned_bytes(pin: tuple, repo: Path = None) -> bytes:
    """A pinned external file: its bytes, checked against the sha256 and (when pinned) the blob at HEAD."""
    repo = repo or REPO
    rel, want, bl = pin
    raw = (repo / rel).read_bytes()
    head = git("rev-parse", f"HEAD:{rel}", repo=repo)
    if (want is not None and sha(raw) != want) or blob_id(raw) != head or (bl is not None and not head.startswith(bl)):
        raise ValueError(f"{rel}: bytes differ from the pin or from the blob at HEAD")
    return raw


def host_mod():
    """mbs308_host of the code under test (no science; MB r1's host module carried, plus the successor's additions)."""
    import mbs308_host as HOST
    return HOST


def driver_caps(src: str = None) -> dict:
    """The caps exactly as the driver's TEXT carries them (the driver is not imported)."""
    dc = module_constants(src if src is not None else (CODE / "mbs308_driver.py").read_text())
    return {k: dc.get(k) for k in ("EVAL_CAP_S", "PRE_CAP_S", "WORKERS", "RUNG_CPU_CAP_S", "DECOY_CAP_S")}


# ------------------------------------------------------------------ MBS-8 (i): the user's section-4 values
def section4_values(driver_src: str, state_src: str, want: dict) -> dict:
    """The driver carries EXACTLY the caps of the user's MBS-8 (i) decision (owner decisions section 4; `want` is the
    configuration's transcription of them, checked against the record's text by the tests): EVAL_CAP 8 h = 28 800 s
    per attempt on awake time (CLOCK_UPTIME_RAW), the per-job CPU caps, PRE_CAP and WORKERS. Mechanical: constants
    from the driver's text, the cap's clock and scope from the structure of the code."""
    dc = module_constants(driver_src)
    rung = dc.get("RUNG_CPU_CAP_S") if isinstance(dc.get("RUNG_CPU_CAP_S"), dict) else {}
    wr = want.get("RUNG_CPU_CAP_S") or {}
    ints = lambda d: {int(k): v for k, v in (d or {}).items()}  # noqa: E731
    r = {"eval_cap_s": type(dc.get("EVAL_CAP_S")) is int and dc.get("EVAL_CAP_S") == want.get("EVAL_CAP_S") == 28800,
         "pre_cap_s": type(dc.get("PRE_CAP_S")) is int and dc.get("PRE_CAP_S") == want.get("PRE_CAP_S"),
         "workers": type(dc.get("WORKERS")) is int and dc.get("WORKERS") == want.get("WORKERS"),
         "job_kinds_exactly_rlr_c2b_c1b_ver": set(rung) == {"RLR", "C2B", "C1B", "VER"},
         "rlr_caps": rung.get("RLR") == ints(wr.get("RLR")) and bool(wr.get("RLR")),
         "c2b_caps": rung.get("C2B") == ints(wr.get("C2B")) and bool(wr.get("C2B")),
         "c1b_caps": isinstance(rung.get("C1B"), dict) and {8, 10, 12} <= set(rung["C1B"]) and
         all(v == wr.get("C1B") for v in rung["C1B"].values()) and type(wr.get("C1B")) is int,
         "ver_caps": isinstance(rung.get("VER"), dict) and bool(rung["VER"]) and
         all(v == wr.get("VER") for v in rung["VER"].values()) and type(wr.get("VER")) is int}
    # per attempt, on awake time: after_marker (called once by execute and once by every resume) starts ONE
    # STATE.AwakeCap(EVAL_CAP_S); AwakeCap reads CLOCK_UPTIME_RAW and no other clock
    tree = ast.parse(driver_src)
    fd = _top(tree)
    am = fd.get("after_marker")
    caps = [c for c in _calls(am, "AwakeCap")]
    r["eval_cap_started_once_per_attempt_in_after_marker"] = len(caps) == 1 and len(_calls(tree, "AwakeCap")) == 1 and \
        len(caps[0].args) == 1 and isinstance(caps[0].args[0], ast.Name) and caps[0].args[0].id == "EVAL_CAP_S" and \
        not caps[0].keywords and len(_calls(fd.get("run_execute"), "after_marker")) == 1 and \
        len(_calls(fd.get("run_resume"), "after_marker")) == 1
    cls = [n for n in ast.parse(state_src).body if isinstance(n, ast.ClassDef) and n.name == "AwakeCap"]
    clocks = {n.attr for c in cls for n in ast.walk(c) if isinstance(n, ast.Attribute) and n.attr.startswith("CLOCK_")}
    other = {n.attr for c in cls for n in ast.walk(c) if isinstance(n, ast.Attribute) and
             n.attr in ("time", "monotonic", "perf_counter", "process_time", "time_ns", "monotonic_ns")
             and isinstance(n.value, ast.Name) and n.value.id == "time"}
    r["eval_cap_clock_is_clock_uptime_raw"] = len(cls) == 1 and clocks == {"CLOCK_UPTIME_RAW"} and not other and \
        want.get("eval_cap_clock") == "CLOCK_UPTIME_RAW"
    return {"checks": r, "driver_values": {"EVAL_CAP_S": dc.get("EVAL_CAP_S"), "PRE_CAP_S": dc.get("PRE_CAP_S"),
                                           "WORKERS": dc.get("WORKERS"),
                                           "RUNG_CPU_CAP_S": {k: {str(a): b for a, b in v.items()}
                                                              for k, v in rung.items() if isinstance(v, dict)}},
            "pass": all(v is True for v in r.values())}


# ------------------------------------------------------------------ Q12 (MB r1's, on the FIXED caps; MBS-8 (i))
def _decoy_jobs(dec: dict) -> tuple:
    """(jobs, problems) from an official decoy record: runtime and status ONLY (incident review C7(b))."""
    jobs, bad = [], []
    for b in dec["stage1"]["blocks"]:
        if not b.get("run"):
            continue
        for r in b["rlr_rungs"]:
            jobs.append({"kind": "RLR", "rung": r["rung"], "wall": r["wall_seconds"], "ok": r.get("status") == "CERTIFIED"})
        for r in b["c2b_rungs"]:
            v = r.get("verification") or {}
            jobs.append({"kind": "C2B", "rung": r["rung"], "wall": r["wall_seconds"],
                         "ver_seconds": v.get("seconds") or 0.0,
                         "ok": r.get("status_U") == "CERTIFIED" and r.get("status_L") == "CERTIFIED"
                         and v.get("verdict") == "VERIFIED" and v.get("accepted") is True})
        for r in b["c1b_rungs"]:
            jobs.append({"kind": "C1B", "rung": r["rung"], "wall": r["wall_seconds"], "ok": r.get("status") == "CERTIFIED"})
        pw = b["pointwise"]
        c2b_up = [u for u in pw.get("uppers", []) if u["impl"] == "C2B"]
        if pw.get("status") != "CERTIFIED" or pw.get("alarms") or pw.get("refuted_rungs") or \
                pw.get("alarm_unavailable") or not c2b_up or any("alarm_sensitivity" not in u for u in c2b_up):
            bad.append(b["index"])
    return jobs, bad


def lpt_makespan(durations: list, workers: int) -> float:
    """Longest-first list scheduling on `workers` identical workers (MB r1 protocol 3.2)."""
    loads = [0.0] * workers
    for d in sorted(durations, reverse=True):
        i = loads.index(min(loads))
        loads[i] += d
    return max(loads)


def _host_verdict(dec: dict | None, HOST) -> dict:
    """MB r1 freeze r3: the host provenance of one decoy run, RE-ASSESSED from its stored raw readings by the host
    module's assess (the stored assessment is reported, never trusted); a record without provenance is AMBIGUOUS."""
    h = (dec or {}).get("host")
    if not isinstance(h, dict):
        return {"status": "AMBIGUOUS", "clean": False, "reasons": ["AMBIGUOUS: the record carries no host provenance"]}
    try:
        v = HOST.assess(h.get("start"), h.get("end"), h.get("samples"), h.get("events"))
    except Exception as exc:                                           # noqa: BLE001
        return {"status": "AMBIGUOUS", "clean": False, "reasons": [f"AMBIGUOUS: {type(exc).__name__}"]}
    stored = (h.get("assessment") or {}).get("status")
    if stored != v["status"]:
        v = dict(v, status="AMBIGUOUS", clean=False,
                 reasons=v["reasons"] + [f"AMBIGUOUS: stored assessment {stored} differs from the re-assessment"])
    # review r3 N2: the host interval must cover the run's recorded Stage-1 (+ Stage-2) walls (1 s rounding allowance)
    try:
        span = (h["end"]["clocks"]["monotonic_raw_ns"] - h["start"]["clocks"]["monotonic_raw_ns"]) // 10 ** 9
        need = float(dec.get("stage1_wall_seconds") or 0) + float(dec.get("stage2_wall_seconds") or 0)
        if span + 1 < need:
            v = dict(v, status="AMBIGUOUS", clean=False,
                     reasons=v["reasons"] + [f"AMBIGUOUS: host interval {span} s does not cover the run's walls"])
    except (KeyError, TypeError, ValueError):
        if v["clean"]:
            v = dict(v, status="AMBIGUOUS", clean=False, reasons=v["reasons"] + ["AMBIGUOUS: interval unreadable"])
    return v


def _launcher_verdict(dec: dict | None, workers: int) -> list:
    """RC6 (the successor's addition to MB r1's Q12): the runtimes count only when the run is the official
    configuration: the real driver's decoy as a launchd job of the launcher, the frozen ladder, WORKERS workers."""
    cfg = ((dec or {}).get("lifecycle") or {}).get("rmem_run")
    if not isinstance(cfg, dict):
        return ["RUN_CONFIGURATION_UNRECORDED"]
    r = []
    if cfg.get("launched_by_launchd") is not True:
        r.append("NOT_UNDER_THE_LAUNCHD_LAUNCHER")
    if cfg.get("workers") != workers:
        r.append("WORKERS_NOT_THE_FROZEN_VALUE")
    if cfg.get("ladder") != "frozen" or (dec or {}).get("dev_ladder") is not False:
        r.append("NOT_THE_FROZEN_LADDER")
    return r


def _q12_core(dec297: dict | None, dec316: dict | None, caps: dict, HOST) -> dict:
    """MB r1's Q12 decision (protocol 3.2) on the OFFICIAL QC02 (297, all blocks) and QC03 (316, blocks 0-2) runtimes,
    against the FIXED caps of MBS-8 (i) (`caps`: the driver's own EVAL_CAP_S, RUNG_CPU_CAP_S and WORKERS): projection =
    longest-first makespan of 11 blocks x the 9 frozen jobs at WORKERS workers, each job taking the larger official wall
    time of its kind and rung (C2b: job wall + its recorded in-job verification seconds, MB r1's convention). Requires
    EVAL_CAP_S >= ceil(1.5 x projection), every per-job cap >= 2 x the official max wall of its kind and rung, every job
    CERTIFIED (C2b VERIFIED and admitted) and no alarm. Runtime and status only. It is a pass / fail check: it never
    derives, proposes or records a candidate cap (the threshold ceil(1.5 x projection) is compared, not reported)."""
    if not dec297 or not dec316:
        return {"pass": False, "missing": [k for k, v in (("QC02", dec297), ("QC03", dec316)) if not v]}
    timing = {"297": _host_verdict(dec297, HOST), "316": _host_verdict(dec316, HOST)}
    config = {"297": _launcher_verdict(dec297, caps["WORKERS"]), "316": _launcher_verdict(dec316, caps["WORKERS"])}
    j297, bad297 = _decoy_jobs(dec297)
    j316, bad316 = _decoy_jobs(dec316)
    mx = {}
    for j in j297 + j316:
        w = j["wall"] + (j.get("ver_seconds") or 0.0)
        key = (j["kind"], j["rung"])
        mx[key] = max(mx.get(key, 0.0), w)
    missing = [f"{k}:{r}" for k, r in Q12_KEYS if (k, r) not in mx]
    if missing:
        return {"pass": False, "missing_job_kinds": missing, "timing_provenance": timing, "run_configuration": config}
    rung = caps["RUNG_CPU_CAP_S"]
    durations = [mx[k] for _ in range(Q12_BLOCKS) for k in Q12_KEYS]
    proj = lpt_makespan(durations, caps["WORKERS"])
    per_job = {f"{k}:{r}": {"cap_s": rung[k][r], "official_max_wall_s": round(mx[(k, r)], 1),
                            "cap_ge_2x": rung[k][r] >= 2 * mx[(k, r)]} for k, r in Q12_KEYS}
    out = {"jobs_297": len(j297), "jobs_316": len(j316), "all_jobs_certified": all(j["ok"] for j in j297 + j316),
           "blocks_with_alarm_or_unadmitted_c2b": {"297": bad297, "316": bad316},
           "projection_jobs": len(durations), "projection_job_seconds": round(sum(durations), 1),
           "projection_makespan_s": round(proj, 1), "eval_cap_s": caps["EVAL_CAP_S"],
           "eval_cap_ok": caps["EVAL_CAP_S"] >= math.ceil(1.5 * proj), "per_job_caps": per_job,
           "stage1_wall_s": {"297": dec297.get("stage1_wall_seconds"), "316": dec316.get("stage1_wall_seconds")},
           "note": "runtime and status only (incident review C7(b)); a pass / fail check of the FIXED caps (MBS-8 (i))"}
    out["caps_pass"] = out["all_jobs_certified"] and not bad297 and not bad316 and out["eval_cap_ok"] and \
        all(c["cap_ge_2x"] for c in per_job.values()) and len(j297) > 0 and len(j316) > 0
    out["timing_provenance"] = timing
    out["timing_clean"] = all(v["clean"] is True for v in timing.values())
    out["run_configuration"] = config
    out["configuration_official"] = not any(config.values())
    out["fail_reasons"] = ([] if out["caps_pass"] else ["CAP_RULE_VIOLATED"]) + \
        [f"TIMING_{v['status']}_{k}" for k, v in timing.items() if not v["clean"]] + \
        [f"CONFIGURATION_{k}" for k, v in config.items() if v]
    out["pass"] = out["caps_pass"] and out["timing_clean"] and out["configuration_official"]   # fails CLOSED
    return out


# real-format power-log lines (MB r1's fixture): the parser must count the Sleep, DarkWake and Wake entries and must
# NOT count "Wake Requests" or "Assertions" lines
Q12_LOG_FIXTURE = (
    "2026-09-29 10:31:00 +0900 Assertions          \tPID 340(powerd) Released PreventUserIdleSystemSleep\n"
    "2026-09-29 10:31:29 +0900 Sleep               \tEntering Sleep state due to 'Clamshell Sleep'\n"
    "2026-09-29 10:31:57 +0900 Wake Requests       \t[process=dasd request=SleepService]\n"
    "2026-09-29 10:32:00 +0900 DarkWake            \tDarkWake from Deep Idle [CDNP]\n"
    "2026-09-29 10:58:43 +0900 Wake                \tWake from Deep Idle [CDNVA]\n")


def _sysctl_text(sleep_s: int, wake_s: int) -> str:
    """Planted `sysctl kern.sleeptime kern.waketime` output in the host's real format (parsed by the host module)."""
    return (f"kern.sleeptime: {{ sec = {sleep_s}, usec = 370188 }} Tue Sep 29 13:41:35 2026\n"
            f"kern.waketime: {{ sec = {wake_s}, usec = 975077 }} Tue Sep 29 13:42:02 2026\n")


def _synthetic_host(HOST, *, gap_s: int = 0, kern_change: bool = False, events=None, battery_at: int | None = None,
                    spacing_s: int = 60, n: int = 12, drop_clocks: bool = False, fixture_window: bool = False,
                    stored_status: str | None = None) -> dict:
    """A planted host-provenance record in the stored format of the host module (integers only). `events` None means
    "log read, no entries" unless set to the string "unavailable" or "fixture" (the real-format log lines)."""
    m0, u0, e0 = 10 ** 15, 4 * 10 ** 14, 1790650000
    if fixture_window:                                   # the fixture's window (2026-09-29 01:30-01:43Z)
        e0 = 1790645400
    therm = {"lines": ["Note: No thermal warning level has been recorded"], "no_warning_recorded": True}

    def snap(k, extra_mono=0):
        c = {"monotonic_raw_ns": m0 + k * spacing_s * 10 ** 9 + extra_mono,
             "uptime_raw_ns": u0 + k * spacing_s * 10 ** 9, "epoch_s": e0 + k * spacing_s + extra_mono // 10 ** 9,
             "utc": "planted"}
        return {"clocks": c, "power": HOST.AC, "thermal_level": 0, "thermal": therm, "load_x100": [100, 100, 100]}
    start = dict(snap(0), kern_us=HOST.kern_times(_sysctl_text(1790656895, 1790656922)))
    samples = [snap(k) for k in range(1, n + 1)]
    end = dict(snap(n + 1, gap_s * 10 ** 9),
               kern_us=HOST.kern_times(_sysctl_text(1790656895 + 3600 * int(kern_change), 1790656922)))
    if battery_at is not None:
        samples[battery_at]["power"] = "Battery Power"
    if drop_clocks:
        end.pop("clocks")
    if events == "unavailable":
        ev = None
    elif events == "fixture":
        ev = HOST.log_events(start["clocks"]["epoch_s"], end["clocks"]["epoch_s"], Q12_LOG_FIXTURE)
    else:
        ev = list(events or [])
    rec = {"start": start, "samples": samples, "end": end, "events": ev}
    try:
        rec["assessment"] = HOST.assess(start, end, samples, ev)
    except Exception:                                                  # noqa: BLE001
        rec["assessment"] = {"status": "AMBIGUOUS"}
    if stored_status is not None:                       # a stored assessment that the raw readings contradict
        rec["assessment"] = dict(rec["assessment"], status=stored_status)
    return rec


def _synthetic_decoy(frac: dict, host, caps: dict, run_cfg: dict | None = None) -> dict:
    """One run block carrying every frozen job kind at wall = frac x its cap (default 1/4), all CERTIFIED, the C2b
    rungs VERIFIED and admitted, the pointwise record CERTIFIED with an admitted C2b upper; the run configuration is
    the official one (launchd launcher, frozen ladder, WORKERS) unless planted otherwise."""
    rung = caps["RUNG_CPU_CAP_S"]
    w = {(k, r): rung[k][r] * frac.get((k, r), frac.get("all", 0.25)) for k, r in Q12_KEYS}
    b = {"index": 0, "run": True,
         "rlr_rungs": [{"rung": r, "wall_seconds": w[("RLR", r)], "status": "CERTIFIED"} for r in (4, 6, 8)],
         "c2b_rungs": [{"rung": n, "wall_seconds": w[("C2B", n)], "status_U": "CERTIFIED", "status_L": "CERTIFIED",
                        "verification": {"seconds": 0.0, "verdict": "VERIFIED", "accepted": True}} for n in (20, 40, 80)],
         "c1b_rungs": [{"rung": d, "wall_seconds": w[("C1B", d)], "status": "CERTIFIED"} for d in (8, 10, 12)],
         "pointwise": {"status": "CERTIFIED", "uppers": [{"impl": "C2B", "alarm_sensitivity": "planted"}]}}
    cfg = dict({"launched_by_launchd": True, "workers": caps["WORKERS"], "ladder": "frozen"}, **(run_cfg or {}))
    return {"stage1": {"blocks": [b]}, "stage1_wall_seconds": 0, "host": host, "dev_ladder": False,
            "lifecycle": {"rmem_run": cfg}}


def _failing_job_keys(r: dict) -> set:
    return {k for k, c in (r.get("per_job_caps") or {}).items() if not c["cap_ge_2x"]}


Q12_CARRIED_CONTROLS = 14                 # MB r1 freeze r3's fourteen
Q12_SUCCESSOR_CONTROLS = 3                # + RC6: the launchd launcher, WORKERS and the frozen ladder


def q12_controls(caps: dict, HOST) -> dict:
    """MB r1 r3's fourteen planted controls through _q12_core, the decision function of the real Q12, plus the
    successor's three (RC6). Expected: the clean control PASSES (the gate can pass); every contamination / ambiguity
    FAILS with the timing reason while the caps still pass; a genuine PER-JOB violation on a CLEAN host fails with
    EVAL_CAP passing and exactly {RLR:8} failing; a genuine EVAL_CAP violation on a CLEAN host fails with every per-job
    cap passing; both at once report both; a run that is not the official configuration fails with the caps and the
    timing passing."""
    clean = lambda **k: _synthetic_host(HOST, **k)  # noqa: E731
    ok_frac = {"all": 0.25}
    per_job_frac = {"all": 0.10, ("RLR", 8): 0.55}          # review r3 F1: EVAL_CAP passes, only RLR:8 fails
    cases = {
        "clean_host_within_caps": (clean(), clean(), ok_frac, True, "CLEAN", True),
        "K_host_slept_30s_during_316": (clean(), clean(gap_s=30), ok_frac, False, "CONTAMINATED", True),
        "S_kern_sleep_time_changed_during_297": (clean(kern_change=True), clean(), ok_frac, False, "CONTAMINATED", True),
        "L_real_format_log_lines_in_316": (clean(), clean(events="fixture", fixture_window=True), ok_frac, False,
                                           "CONTAMINATED", True),
        "L_power_log_unavailable": (clean(events="unavailable"), clean(), ok_frac, False, "AMBIGUOUS", True),
        "K_clocks_missing": (clean(), clean(drop_clocks=True), ok_frac, False, "AMBIGUOUS", True),
        "battery_in_one_sample": (clean(battery_at=5), clean(), ok_frac, False, "CONTAMINATED", True),
        "samples_do_not_cover_the_run": (clean(spacing_s=400), clean(), ok_frac, False, "AMBIGUOUS", True),
        "record_without_host_provenance": (None, clean(), ok_frac, False, "AMBIGUOUS", True),
        "genuine_per_job_cap_violation_clean_host": (clean(), clean(), per_job_frac, False, "CLEAN", False),
        "genuine_eval_cap_violation_clean_host": (clean(), clean(), {"all": 0.45}, False, "CLEAN", False),
        "violation_and_contamination": (clean(), clean(gap_s=30), per_job_frac, False, "CONTAMINATED", False),
        "stored_assessment_contradicted_by_raw_readings": (clean(), clean(events="fixture", fixture_window=True,
                                                                          stored_status="CLEAN"), ok_frac, False,
                                                           "AMBIGUOUS", True),
        "host_interval_shorter_than_the_run": (clean(), "short", ok_frac, False, "AMBIGUOUS", True),
    }
    rows = {}
    for name, (h297, h316, frac, want_pass, want_status, want_caps) in cases.items():
        d316 = _synthetic_decoy(frac, clean() if h316 == "short" else h316, caps)
        if h316 == "short":                              # 13 min of provenance vouching for a 10 000 s run
            d316["stage1_wall_seconds"] = 10000.0
        r = _q12_core(_synthetic_decoy(frac, h297, caps), d316, caps, HOST)
        stat = [v["status"] for v in r.get("timing_provenance", {}).values()]
        worst = "CONTAMINATED" if "CONTAMINATED" in stat else ("AMBIGUOUS" if "AMBIGUOUS" in stat else "CLEAN")
        rows[name] = {"pass_observed": r.get("pass"), "caps_pass": r.get("caps_pass"), "timing": worst,
                      "eval_cap_ok": r.get("eval_cap_ok"), "failing_per_job_keys": sorted(_failing_job_keys(r)),
                      "fail_reasons": r.get("fail_reasons"),
                      "ok": r.get("pass") is want_pass and worst == want_status and r.get("caps_pass") is want_caps
                      and r.get("configuration_official") is True}
    per_job = rows["genuine_per_job_cap_violation_clean_host"]
    per_job["ok"] &= per_job["fail_reasons"] == ["CAP_RULE_VIOLATED"] and per_job["eval_cap_ok"] is True and \
        per_job["failing_per_job_keys"] == ["RLR:8"]
    ev = rows["genuine_eval_cap_violation_clean_host"]
    ev["ok"] &= ev["eval_cap_ok"] is False and ev["failing_per_job_keys"] == []
    both = rows["violation_and_contamination"]
    both["ok"] &= set(both["fail_reasons"] or []) == {"CAP_RULE_VIOLATED", "TIMING_CONTAMINATED_316"} and \
        both["failing_per_job_keys"] == ["RLR:8"]
    # the parser on the real-format fixture: exactly Sleep, DarkWake, Wake over all time (Assertions and Wake Requests
    # skipped), exactly Sleep and DarkWake in the fixture control's window (review r3 N3)
    allt = HOST.log_events(0, 2 ** 40, Q12_LOG_FIXTURE) or []
    win = HOST.log_events(1790645400, 1790645400 + 13 * 60, Q12_LOG_FIXTURE) or []
    rows["L_real_format_log_lines_in_316"]["fixture_parse"] = [e["type"] for e in allt]
    rows["L_real_format_log_lines_in_316"]["ok"] &= [e["type"] for e in allt] == ["Sleep", "DarkWake", "Wake"] and \
        [e["type"] for e in win] == ["Sleep", "DarkWake"]
    carried = len(rows)
    # the successor's own (RC6): the same clean runtimes, not in the official configuration
    for name, cfg, want in (
            ("not_under_the_launchd_launcher_316", {"launched_by_launchd": False}, "NOT_UNDER_THE_LAUNCHD_LAUNCHER"),
            ("workers_not_the_frozen_value_316", {"workers": 1}, "WORKERS_NOT_THE_FROZEN_VALUE"),
            ("not_the_frozen_ladder_316", {"ladder": "dev"}, "NOT_THE_FROZEN_LADDER")):
        r = _q12_core(_synthetic_decoy(ok_frac, clean(), caps), _synthetic_decoy(ok_frac, clean(), caps, cfg), caps,
                      HOST)
        rows[name] = {"pass_observed": r.get("pass"), "caps_pass": r.get("caps_pass"), "timing": "CLEAN"
                      if r.get("timing_clean") else "NOT_CLEAN", "fail_reasons": r.get("fail_reasons"),
                      "ok": r.get("pass") is False and r.get("caps_pass") is True and r.get("timing_clean") is True
                      and r.get("fail_reasons") == ["CONFIGURATION_316"] and
                      (r.get("run_configuration") or {}).get("316") == [want]}
    return {"controls": rows, "n": len(rows), "carried_from_mbr1_r3": carried,
            "failed": sorted(k for k, v in rows.items() if not v["ok"]),
            "pass": carried == Q12_CARRIED_CONTROLS and len(rows) == Q12_CARRIED_CONTROLS + Q12_SUCCESSOR_CONTROLS
            and all(v["ok"] for v in rows.values())}


def q12_caps(dec297: dict | None, dec316: dict | None, *, driver_src: str, state_src: str, section4: dict,
             HOST=None) -> dict:
    """Q12 on the official records, the planted controls through the SAME decision function, and the mechanical check
    that the caps under test are exactly the user's section-4 values (MBS-8 (i))."""
    HOST = HOST or host_mod()
    caps = driver_caps(driver_src)
    s4 = section4_values(driver_src, state_src, section4)
    if not s4["checks"].get("job_kinds_exactly_rlr_c2b_c1b_ver") or type(caps.get("WORKERS")) is not int or \
            type(caps.get("EVAL_CAP_S")) is not int:
        return {"pass": False, "reason": "the driver's caps are unreadable", "section4_values": s4}
    out = _q12_core(dec297, dec316, caps, HOST)
    ctl = q12_controls(caps, HOST)
    out["planted_controls"] = ctl
    out["section4_values"] = s4
    out["pass"] = out["pass"] is True and ctl["pass"] is True and s4["pass"] is True
    return out


# ------------------------------------------------------------------ MB r1's qualification test modules (carried)
def load_mbr1_test(name: str):
    """One of MB r1's qualification test modules, EXECUTED FROM MB r1's COMMITTED BYTES (MBR1_TEST_PINS) by MB r1's own
    pinned loader. Re-targeting to the successor identity: the guard test binds MB r1's guard by NAME at import; the
    successor's guard (MB r1's with the marker line only, QC09-S) is bound to that name while the module loads, so the
    carried checks run against the guard the successor's science is bound to."""
    D = driver()
    saved = sys.modules.get("mb308_guard")
    is_guard = name == "test_mb308_guard"
    if is_guard:
        sys.modules["mb308_guard"] = D.GUARD
    try:
        mod = D.PIN.exec_pinned(REPO, "mbs308_carried_" + name, MBR1_TEST_PINS[name], check_git=True)
    finally:
        if is_guard:
            if saved is None:
                sys.modules.pop("mb308_guard", None)
            else:
                sys.modules["mb308_guard"] = saved
    if is_guard and getattr(mod, "G", None) is not D.GUARD:
        raise RuntimeError("the carried guard test is not bound to the successor's guard")
    return mod


def mbr1_test_static(name: str, repo: Path = None) -> dict:
    """Without executing anything: the module's bytes are the pinned bytes and its entry function has the parameters
    this verifier passes (MBR1_TEST_ENTRY)."""
    fn, want = MBR1_TEST_ENTRY[name]
    try:
        raw = pinned_bytes(MBR1_TEST_PINS[name], repo)
    except (OSError, ValueError) as exc:
        return {"module": name, "pinned_bytes": False, "error": str(exc)[:200], "pass": False}
    defs = [n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == fn]
    got = tuple(a.arg for a in defs[0].args.args) if len(defs) == 1 else None
    return {"module": name, "pinned_bytes": True, "entry": fn, "entry_parameters_as_called": got == want,
            "pass": got == want}


def dev_loader_only(case_id: str, names: list, repo: Path = None) -> dict:
    """The --dev form of a case whose science cannot be run on decoy 297 block 0 at the dev ladder (the only science a
    dev run computes): the carried module's pinned bytes and entry signature are checked; nothing is executed."""
    rows = [mbr1_test_static(n, repo) for n in names]
    return {"pass": False, "status": DEV_STATUS, "dev_form": "loader only: nothing executed", "case": case_id,
            "modules": rows, "dev_checks_ok": bool(rows) and all(r["pass"] is True for r in rows)}


def science_inprocess(sel: set, mode: str) -> dict:
    """MB r1's in-process cases through the pinned science code paths, with the successor's driver, guard and science
    modules: QC05 (two-sided composition), QC06 (pointwise-certificate package), QC07's formal part (TPT-B), QC09-SCI
    (the guard through every pinned code path). Official and review runs only."""
    D = driver()
    con = D.load_consumer()
    sci = D.load_science(allow_uncommitted=(mode == "dev"), with_decoy_gen=True)
    vf = D.PIN.load_verifier(REPO, D.GUARD)
    out = {}
    if "QC05" in sel:
        TT = load_mbr1_test("test_mb308_twosided")
        out["QC05"] = TT.composition_test(D.SUP, D.S1M, sci["S1"], sci["indep"], sci["IND7"], sci["cp"], con, D.GUARD)
    if "QC06" in sel:
        TA = load_mbr1_test("test_mb308_a0")
        out["QC06"] = TA.run(D.PIN, D.A0C, sci["c1b"], sci["c2b"], D.GUARD, S1M=D.S1M, vf=vf)
    if "QC07" in sel:
        TP = load_mbr1_test("test_mb308_tptb")
        out["QC07_formal"] = TP.run(D.CON, sci["asm"], D.GUARD, sci["indep"], sci["asm"]["DG"])
    if "QC09-SCI" in sel:
        TG = load_mbr1_test("test_mb308_guard")
        mods = {"c1b": sci["c1b"], "c2b": sci["c2b"], "S1": sci["S1"], "A0C": D.A0C, "vd": vf["vd"],
                "TPT": sci["asm"]["TPT"], "indep": sci["indep"], "set_flags": D.PIN.set_c1b_flags}
        out["QC09-SCI"] = TG.run(D.CON.read_pinned, mods)
    return out


def science_summary(res) -> dict:
    """A carried in-process case's own result, with the boolean `pass` MB r1's test computed (anything else fails)."""
    if not isinstance(res, dict) or not isinstance(res.get("pass"), bool):
        return {"pass": False, "reason": "NO_RESULT"}
    return res


def qc07_summary(e4, formal) -> dict:
    """MB r1's QC07: the stream-ASSEMBLY E4 controls (29, all detected, valid halves OK) and the formal part."""
    e4 = e4 if isinstance(e4, dict) else {"pass": False, "missing": True}
    formal = formal if isinstance(formal, dict) else {"pass": False, "missing": True}
    return {"assembly_E4": e4, "formal": formal, "pass": e4.get("pass") is True and formal.get("pass") is True}


def qc01_summary(record, rc) -> dict:
    """MB r1's QC01: the driver's `rehearse --cell 305` (C-A and C-B on cell 305's COMMITTED record; equality
    booleans only) exits 0 and its record says pass."""
    rh = record if isinstance(record, dict) else {}
    return {"exit": rc, "C_A": (rh.get("C_A") or {}).get("field_matches") if isinstance(rh.get("C_A"), dict) else None,
            "C_B_failed": (rh.get("C_B") or {}).get("failed") if isinstance(rh.get("C_B"), dict) else None,
            "pass": rc == 0 and rh.get("pass") is True}


def run_qc01(out: Path, driver_path: Path = None) -> dict:
    out.unlink(missing_ok=True)
    reh = subprocess.run([PY, *FLAGS, str(driver_path or CODE / "mbs308_driver.py"), "rehearse", "--cell", "305",
                          "--out", str(out)], capture_output=True, text=True, env=ENV, cwd=str(REPO),
                         stdin=subprocess.DEVNULL)
    try:
        rh = json.loads(out.read_text())
    except (OSError, ValueError):
        rh = None
    return qc01_summary(rh, reh.returncode)


def q1_theory(repo: Path = None) -> dict:
    """MB r1's Q1 theory binding, re-targeted: MB-S proves MB r1's theorem with MB r1's unchanged science (MBS-7 (i)),
    so the bound text is MB r1's NSF copy of THEOREM_MB at MB r1's path: byte-identical to the research file as
    committed at bfa9ad3c (sha256 and blob), the research file present at HEAD with the same bytes."""
    repo = repo or REPO
    rel, commit, pin_sha, pin_blob = THEORY_RESEARCH
    raw = (repo / THEORY_REL).read_bytes() if (repo / THEORY_REL).is_file() else b""
    rs = (repo / rel).read_bytes() if (repo / rel).is_file() else b""
    out = {"nsf_copy": THEORY_REL, "research": f"{rel}@{commit}",
           "research_blob_at_commit_ok": git("rev-parse", f"{commit}:{rel}", repo=repo) == pin_blob,
           "nsf_sha256_ok": sha(raw) == pin_sha, "nsf_blob_ok": blob_id(raw) == pin_blob,
           "nsf_blob_at_head_ok": git("rev-parse", f"HEAD:{THEORY_REL}", repo=repo) == pin_blob,
           "research_file_present_and_identical": sha(rs) == pin_sha}
    out["pass"] = all(v is True for k, v in out.items() if k.endswith("_ok") or k.endswith("_identical"))
    return out


# ------------------------------------------------------------------ the heavy records: QC02, QC03, QC04, QC08
def official_config_reasons(dec: dict | None, job: dict | None, first_blocks, workers: int) -> list:
    """Why a decoy record is not an OFFICIAL-configuration run (the successor's requirement on QC02 / QC03: the real
    driver's decoy as a launchd job of the launcher, the frozen ladder, WORKERS, the planned blocks)."""
    r = list(_launcher_verdict(dec, workers))
    cfg = ((dec or {}).get("lifecycle") or {}).get("rmem_run") or {}
    if cfg.get("first_blocks") != first_blocks:
        r.append("BLOCKS_NOT_AS_PLANNED")
    if job is not None and not (job.get("finished") is True and job.get("detached") is True and
                                job.get("booted_out") is True):
        r.append("JOB_NOT_LAUNCHED_DETACHED_AND_FINISHED")
    return r


def decoy_failure(dec) -> dict | None:
    """The driver's record of a decoy that FAILED (`decoy_failed`: no stage 1, the R-MEM step-1 fields of the run
    kept), as a case summary; None for any other record. A memory-watchdog event in it (owner supplement 2, sections 1
    and 6: an official decoy under the actual frozen MEM_CAP) gives the distinct status
    QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP: the case and the qualification fail closed, nothing cures it."""
    if not isinstance(dec, dict) or dec.get("decoy_failed") is None:
        return None
    wd = (((dec.get("lifecycle") or {}).get("stage1_context") or {}).get("memory_watchdog") or {})
    events = RR.cap_events(wd.get("events")) if isinstance(wd.get("events"), list) else None
    out = {"pass": False, "decoy_failed": str(dec.get("decoy_failed")), "cell": dec.get("decoy_cell"),
           "memory_watchdog_events": None if events is None else len(events),
           "memory_watchdog_cap_bytes": wd.get("cap_bytes"), "status": "DECOY_FAILED"}
    if events:
        out.update({"status": RR.STATUS_OFFICIAL_WATCHDOG, "fail_closed_statuses": [RR.STATUS_OFFICIAL_WATCHDOG]})
    return out


def qc02_eval(dec: dict | None, ladder: dict) -> dict:
    """MB r1's QC02 evaluation of the decoy-297 record (`ladder`: the frozen ladder, from the science module)."""
    if not dec:
        return {"pass": False, "missing": "decoy 297 record"}
    if decoy_failure(dec):
        return decoy_failure(dec)
    st = dec["stage1"]
    blocks = st["blocks"]
    s2 = dec.get("stage2_decoys") or []
    ok_s2 = bool(s2) and all("stage2" in r and all(g.get("pass") is True for g in r["stage2"]["gates"].values())
                             and r["supply"]["independent"]["status"] == "EQUAL" for r in s2)
    return {"blocks": len(blocks), "all_run": all(b["run"] for b in blocks),
            "rlr_blocks_certified": sum(1 for b in blocks if b.get("rlr_block")),
            "pointwise_status": [b["pointwise"]["status"] for b in blocks],
            "verifications": st.get("n_verifications"), "stage2_decoys": len(s2), "stage2_all_gates_pass": ok_s2,
            "r0_order3_variant_present": any(r.get("decoy_meta", {}).get("r0_order3_binds") for r in s2),
            "ladder_full": st["ladder"] == ladder,
            "pass": dec.get("blocks_run") == "all" and all(b["run"] for b in blocks) and ok_s2
            and all(b["pointwise"]["status"] in ("CERTIFIED", "ALARM_UNAVAILABLE", "NOT_CERTIFIED") for b in blocks)
            and st["ladder"] == ladder}


def qc03_eval(dec: dict | None) -> dict:
    """MB r1's QC03: Stage 1 ran on the first three blocks of decoy cover cell 316."""
    if decoy_failure(dec):
        return decoy_failure(dec)
    ok = bool(dec) and len(dec["stage1"]["blocks"]) >= 3 and all(b["run"] for b in dec["stage1"]["blocks"][:3])
    return {"blocks_run": (dec or {}).get("blocks_run"), "pass": ok}


def with_official_config(summary: dict, dec, job, first_blocks, workers: int, exit_code) -> dict:
    """QC02 / QC03 in the official form: MB r1's criterion AND the run is the official configuration."""
    why = official_config_reasons(dec, job, first_blocks, workers)
    return dict(summary, exit=exit_code, official_configuration_reasons=why, job=job,
                **{"pass": summary.get("pass") is True and not why})


def _strip_decoy_timing(o):
    """MBR1_REPRO / QC04: exactly the timing keys seconds, wall_seconds, cpu_seconds and the per-job cpu_cap, stripped
    at every depth (MB r1's QC04 set and the job-level cpu_cap; the protocol's MBR1_REPRO text)."""
    if isinstance(o, dict):
        return {k: _strip_decoy_timing(v) for k, v in o.items() if k not in TIMING_KEYS and k != "cpu_cap"}
    if isinstance(o, list):
        return [_strip_decoy_timing(v) for v in o]
    return o


def _leaves(o, path=()) -> list:
    if isinstance(o, dict):
        return [lf for k in sorted(o) for lf in _leaves(o[k], path + (k,))]
    if isinstance(o, list):
        return [lf for i, v in enumerate(o) for lf in _leaves(v, path + (i,))]
    return [path]


def _public(o):
    """The driver's own publication projection `jsonable` on JSON data: keys starting with "_" are dropped at every
    depth (in-memory fields such as _cpu_seconds, _log_sha256, which no published record carries)."""
    if isinstance(o, dict):
        return {str(k): _public(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, list):
        return [_public(v) for v in o]
    return o


def _serial_view(job: dict) -> dict:
    """MB r1's compared scope of a serial / pooled Stage-1 job: the status fields and the record, after the
    publication projection and the recursive timing strip."""
    j = _public(job)
    keep = {x: j[x] for x in ("status", "status_U", "status_L") if x in j}
    keep["record"] = j.get("record", {})
    return strip_timing(keep)


def _ladder_view(job: dict) -> dict:
    """MB r1's compared scope of a ladder-determinism job: the whole job minus cpu_cap at the job level."""
    j = _public(job)
    j.pop("cpu_cap", None)
    return strip_timing(j)


def _decoy_view(dec: dict) -> dict:
    """MBR1_REPRO's compared scope of a whole decoy record: the run's identity (cell, blocks) and every certified
    part -- Stage 1 (every block, job, certificate digest, verification and pointwise record) and every Stage-2 decoy
    bundle -- with the timing keys and the per-job cpu_cap stripped at every depth. Not compared: provenance (host,
    lifecycle, driver sha256, utc, walls, cpu caps record) and `stage1.workers`, an operational parameter (MB r1's
    QC03 ran at 1 worker; the successor's official decoys run at WORKERS)."""
    st = {k: v for k, v in (dec.get("stage1") or {}).items() if k != "workers"}
    view = {"decoy_cell": dec.get("decoy_cell"), "blocks_total": dec.get("blocks_total"),
            "blocks_run": dec.get("blocks_run"), "dev_ladder": dec.get("dev_ladder"), "stage1": st}
    if "stage2_decoys" in dec:
        view["stage2_decoys"] = dec["stage2_decoys"]
    return _strip_decoy_timing(_public(view))


def _compare(a, b, view) -> dict:
    va, vb = view(a), view(b)
    return {"equal": va == vb, "compared_leaves": len(_leaves(va))}


def _planted(a, b, view) -> bool:
    """MB r1's control: mutate ONE non-timing leaf (the middle one of the compared view) in a deep copy of `a`; the
    SAME comparison must report a difference."""
    import copy
    paths = _leaves(view(a))
    if not paths:
        return False
    path = paths[len(paths) // 2]
    m = copy.deepcopy(a)
    node = m
    try:
        for k in path[:-1]:
            node = node[k]
        v = node[path[-1]]
    except (KeyError, IndexError, TypeError):
        return False
    node[path[-1]] = (not v) if isinstance(v, bool) else (v + 1 if isinstance(v, (int, float)) else
                                                           ("planted" if v is None else str(v) + "#planted"))
    return not _compare(m, b, view)["equal"]


def qc04_eval(dec: dict | None, serial: dict | None, det_a: dict | None, det_b: dict | None) -> dict:
    """MB r1's QC04 r2: (a) block 0 of decoy 297, serial vs pooled; (b) the REVIEW_A0 C4 ladder pair. Every compared
    pair: exactly the timing keys are stripped at every depth (and cpu_cap at the job level); the comparison must be
    non-vacuous (> 0 compared leaves per job) and a planted one-leaf mutation must be detected by the same
    comparison."""
    out = {"stripped_keys": sorted(TIMING_KEYS) + ["cpu_cap (job level)"]}
    if dec and serial:
        b0 = dec["stage1"]["blocks"][0]
        pooled = {f"RLR:{r['rung']}": r for r in b0["rlr_rungs"]} | {f"C2B:{r['rung']}": r for r in b0["c2b_rungs"]} | \
            {f"C1B:{r['rung']}": r for r in b0["c1b_rungs"]}
        rows = {}
        for k, r in serial["results"].items():
            if k.startswith("VER"):
                continue
            p = pooled.get(k)
            if p is None:
                rows[k] = {"equal": False, "compared_leaves": 0, "missing_pooled": True, "control_detected": False}
                continue
            rows[k] = _compare(r, p, _serial_view) | {"control_detected": _planted(r, p, _serial_view)}
        out["serial_vs_pooled"] = rows
        out["serial_ok"] = bool(rows) and len(rows) == len(pooled) and all(
            v["equal"] and v["compared_leaves"] > 0 and v["control_detected"] for v in rows.values())
    else:
        out["serial_ok"] = False
    if det_a and det_b:
        ka, kb = det_a.get("results", {}), det_b.get("results", {})
        rows = {}
        for k in sorted(set(ka) | set(kb)):
            if k not in ka or k not in kb:
                rows[k] = {"equal": False, "compared_leaves": 0, "control_detected": False, "missing_one_side": True}
                continue
            rows[k] = _compare(ka[k], kb[k], _ladder_view) | {"control_detected": _planted(kb[k], ka[k], _ladder_view)}
        out["ladder_pair"] = rows
        out["ladder_drifts"] = [det_a.get("drifts"), det_b.get("drifts")]
        out["ladder_pair_identical"] = bool(rows) and all(
            v["equal"] and v["compared_leaves"] > 0 and v["control_detected"] for v in rows.values())
    else:
        out["ladder_pair_identical"] = False
    out["pass"] = out["serial_ok"] and out["ladder_pair_identical"]
    return out


# ------------------------------------------------------------------ MBR1_REPRO (RC2), the full form
def _job_rows(mine: dict | None, theirs: dict | None, view) -> tuple:
    """Per-job exact equality of two `results` maps (the same key set on both sides is required)."""
    ka, kb = (mine or {}).get("results") or {}, (theirs or {}).get("results") or {}
    rows = {}
    for k in sorted(set(ka) | set(kb)):
        if k not in ka or k not in kb:
            rows[k] = {"equal": False, "compared_leaves": 0, "control_detected": False, "missing_one_side": True}
        else:
            rows[k] = _compare(ka[k], kb[k], view) | {"control_detected": _planted(ka[k], kb[k], view)}
    return rows, bool(rows) and all(v["equal"] and v["compared_leaves"] > 0 and v["control_detected"]
                                    for v in rows.values())


def mbr1_repro(mine: dict, mbr1: dict) -> dict:
    """RC2, the FULL form: the successor's official non-target decoy / ladder records against MB r1's COMMITTED
    official r3 records, EXACT equality with the timing keys (seconds, wall_seconds, cpu_seconds, cpu_cap) stripped at
    every depth: decoy 297 (QC02: every block, Stage 1 and every Stage-2 decoy bundle), decoy 316 blocks 0-2 (QC03),
    the serial block 0 of 297 and the two ladder-determinism records (QC04). Each comparison must be non-vacuous and
    must detect a planted one-leaf mutation. `mine` / `mbr1`: {decoy297, decoy316, serial, det_a, det_b} -> record. A
    mismatch is a STOP (the case fails; nothing is printed of any value)."""
    out = {"stripped_keys": sorted(TIMING_KEYS) + ["cpu_cap"], "not_compared": ["host", "lifecycle", "driver_sha256",
                                                                               "utc", "cpu_caps", "stage1.workers",
                                                                               "walls"]}
    ok = True
    for k in ("decoy297", "decoy316"):
        a, b = mine.get(k), mbr1.get(k)
        if not isinstance(a, dict) or not isinstance(b, dict):
            out[k] = {"equal": False, "missing": True}
            ok = False
            continue
        try:
            row = _compare(a, b, _decoy_view) | {"control_detected": _planted(a, b, _decoy_view),
                                                 "blocks_run_mine": sum(1 for x in a["stage1"]["blocks"] if x.get("run")),
                                                 "blocks_run_mbr1": sum(1 for x in b["stage1"]["blocks"] if x.get("run"))}
        except (KeyError, TypeError):
            row = {"equal": False, "malformed": True, "compared_leaves": 0, "control_detected": False}
        out[k] = row
        ok = ok and row["equal"] is True and row["compared_leaves"] > 0 and row["control_detected"] is True
    out["serial"], s_ok = _job_rows(mine.get("serial"), mbr1.get("serial"), _serial_view)
    out["det_a"], a_ok = _job_rows(mine.get("det_a"), mbr1.get("det_a"), _ladder_view)
    out["det_b"], b_ok = _job_rows(mine.get("det_b"), mbr1.get("det_b"), _ladder_view)
    out["form"] = "full"
    out["pass"] = bool(ok and s_ok and a_ok and b_ok)
    return out


def mbr1_repro_tiny(dec: dict | None, mbr1_297: dict | None) -> dict:
    """The --dev (tiny) form: block 0 of a DEV-ladder decoy 297 against block 0 of MB r1's committed QC02 record, for
    the jobs both ladders hold (RLR d4, C2B N20) and the block geometry. Never evidence."""
    try:
        a0, q0 = dec["stage1"]["blocks"][0], mbr1_297["stage1"]["blocks"][0]
        ra = [r for r in a0["rlr_rungs"] if r["rung"] == 4]
        rq = [r for r in q0["rlr_rungs"] if r["rung"] == 4]
        ca = [r for r in a0["c2b_rungs"] if r["rung"] == 20]
        cq = [r for r in q0["c2b_rungs"] if r["rung"] == 20]
        geo = (a0["tile"], a0["hull"], a0["b"]) == (q0["tile"], q0["hull"], q0["b"])
        rl = _compare(ra, rq, _strip_decoy_timing) | {"control_detected": _planted(ra, rq, _strip_decoy_timing)}
        c2 = _compare(ca, cq, _strip_decoy_timing) | {"control_detected": _planted(ca, cq, _strip_decoy_timing)}
    except (KeyError, IndexError, TypeError):
        return {"pass": False, "status": DEV_STATUS, "form": "tiny", "dev_checks_ok": False, "malformed": True}
    ok = geo and len(ra) == len(rq) == 1 and len(ca) == len(cq) == 1 and all(
        r["equal"] and r["compared_leaves"] > 0 and r["control_detected"] for r in (rl, c2))
    return {"pass": False, "status": DEV_STATUS, "form": "tiny", "dev_checks_ok": bool(ok), "rlr_d4": rl,
            "c2b_n20": c2, "geometry_equal": geo}


# ------------------------------------------------------------------ R_RULES_OFFICIAL (section 11.2, option (a))
def r_rules_official(*, evidence, evidence_sha256, derivation, official: dict | None, driver_src: str,
                     measured_driver_src: str | None, cfg: dict, base_names, HOST=None) -> dict:
    """Owner supplement 1, part I: canonical outputs A (the committed designated pre-freeze evidence through the rule
    functions; the committed derivation must be exactly that) against canonical outputs B (the official QC02 / QC03
    records, made with the ACTUAL FROZEN VALUES, and the qualification's own prepared-host readings, through the SAME
    functions) and against the constants the frozen driver carries: B == A == driver, EXACTLY, for each of the five
    outputs (set equality of the canonical lists for EXCL_ALLOW); every built-in check of the rules must hold for A and
    for B; every official run must be a valid input (official configuration under the launchd launcher, CLEAN host
    provenance, no thermal event, a valid sampler record); and the frozen driver must be the measured driver with
    exactly the five constants applied. No tolerance anywhere; no raw observation is compared.

    Two branches FAIL CLOSED with a distinct status (owner supplement 2, research 74f386a5; `status` and
    `fail_closed_statuses`, which the aggregator lifts to the qualification):
    * QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP (sections 1 and 6): ANY memory-watchdog event in an official
      decoy. No doubling, no qualification-only cap, no cure by another clean run; B has no R-MEM value.
    * MEM_POLL_S_NONCANONICAL_BRANCH (section 3): the official measurements reach step 6's unrounded-quotient branch.
      B's MEM_POLL_S is None: no comparison value is manufactured and the frozen MEM_POLL_S is not touched."""
    import mbs308_measure as MEAS
    import mbs308_repin as RP
    HOST = HOST or host_mod()
    out = {"ruling": "owner supplement 1, part I (section 11.2 option (a))", "comparison": "exact; no tolerance"}
    plan, h3 = DV.plan_of(cfg), cfg["r_allow_h3_readings"]["readings"]
    try:
        C = DV.driver_constants(driver_src)
    except DV.DeriveRefusal as exc:
        return dict(out, **{"pass": False, "reason": f"driver constants: {exc}"})
    out["driver_outputs"] = {k: C[k] for k in DV.OUTPUTS}
    # A: recomputed from the committed designated evidence; the committed derivation must be exactly this
    if not isinstance(evidence, dict) or not isinstance(derivation, dict):
        return dict(out, **{"pass": False, "reason": "no designated evidence or no derivation committed under "
                                                     "evidence_prefreeze/"})
    a = DV.derivation(evidence, evidence_sha256=evidence_sha256, base_names=base_names, h3_readings=h3, plan=plan,
                      rules_sha256=sha((CODE / "mbs308_rrules.py").read_bytes()),
                      tool_sha256=sha((CODE / "mbs308_derive.py").read_bytes()))
    out["A"] = {"status": a["status"], "designated": a["designated"], "outputs": a["outputs"], "checks": a["checks"],
                "evidence_reasons": a["evidence_reasons"], "poll": a["poll"]}
    out["derivation_committed_is_the_recomputation"] = derivation.get("outputs") == a["outputs"] and \
        derivation.get("status") == a["status"] == "OK" and derivation.get("checks") == a["checks"] and \
        (derivation.get("evidence") or {}).get("sha256") == evidence_sha256 and derivation.get("designated") is True
    # the frozen driver = the measured driver with exactly the five constants applied (nothing else changed)
    try:
        applied = RP.apply_constants(measured_driver_src, a["outputs"]) if measured_driver_src is not None and \
            a["status"] == "OK" else None
    except RP.Refused:
        applied = None
    out["measured_driver_is_the_evidence_driver"] = measured_driver_src is not None and \
        sha(measured_driver_src.encode()) == evidence.get("driver_sha256")
    out["frozen_driver_is_measured_driver_with_the_five_outputs_applied"] = applied is not None and \
        applied == driver_src
    # B: the official measurements through the same functions, with the frozen values as the runs' configuration
    if not isinstance(official, dict):
        return dict(out, **{"pass": False, "reason": "no official rule inputs"})
    runs = list(official.get("runs") or [])
    poll = F(C["MEM_POLL_S"])
    run_poll = F(repr(float(poll)))            # the value a decoy record carries: the driver's float, as JSON prints it
    out["official_run_reasons"] = {str(r.get("id")): MEAS.run_reasons(r, plan, cap=C["MEM_CAP_BYTES"], poll=run_poll)
                                   for r in runs}
    out["official_reading_reasons"] = MEAS.reading_reasons(official.get("readings"))
    # the embedded read-only host report of the official run (a recorded field: its STRUCTURE is checked, its statuses
    # are not judged); the designated evidence's own is checked by mbs308_derive.evidence_reasons (A above)
    out["official_host_report_reasons"] = DV.host_report_reasons(official.get("host_report"))
    rules_b = DV.apply_rules(runs=runs, readings=official.get("readings"),
                             hw_memsize_bytes=official.get("hw_memsize_bytes"),
                             hosting_app_paths=(official.get("hosting_app") or {}).get("paths"),
                             base_names=base_names, h3_readings=h3, plan=plan, workers=C["WORKERS"], mem_poll_s=poll,
                             measurement_cap_bytes=C["MEM_CAP_BYTES"], measurement_poll_s=run_poll, official=True)
    b_out, b_checks = DV.canonical(rules_b), DV.checks(rules_b)
    out["B"] = {"outputs": b_out, "checks": b_checks, "poll": DV.poll_note(rules_b), "rules": rules_b,
                "form_reasons": DV.form_reasons(b_out) if all(b_out[k] is not None for k in DV.OUTPUTS) else None}
    out["memory_watchdog_event_in_an_official_decoy"] = any(RR.cap_events(r.get("watchdog_events")) for r in runs)
    out["mem_poll_s_noncanonical_branch_in_the_official_series"] = \
        RR.STATUS_POLL_NONCANONICAL in DV.stop_statuses(rules_b)
    closed = [RR.STATUS_OFFICIAL_WATCHDOG] if out["memory_watchdog_event_in_an_official_decoy"] else []
    closed += [RR.STATUS_POLL_NONCANONICAL] if out["mem_poll_s_noncanonical_branch_in_the_official_series"] else []
    out["fail_closed_statuses"] = closed
    cmp_ = DV.compare(a["outputs"], b_out, out["driver_outputs"])
    out["comparison_by_output"] = cmp_["outputs"]
    out["pass"] = bool(
        not closed and
        a["status"] == "OK" and a["designated"] is True and a["checks"]["all_hold"] is True and
        out["derivation_committed_is_the_recomputation"] and out["measured_driver_is_the_evidence_driver"] and
        out["frozen_driver_is_measured_driver_with_the_five_outputs_applied"] and
        len(runs) == len(plan) and not any(out["official_run_reasons"].values()) and
        not out["official_reading_reasons"] and not out["official_host_report_reasons"] and
        out["B"]["form_reasons"] == [] and
        b_checks["all_hold"] is True and cmp_["all_equal"] is True)
    out["status"] = closed[0] if closed else ("EXACT_AGREEMENT" if out["pass"] else "NOT_IN_AGREEMENT")
    return out


# ------------------------------------------------------------------ children (fresh processes; MB r1's, re-targeted)
def _decoy_ctx():
    """The Stage-1 worker context of DECOY mode, in this process (serial children only)."""
    D = driver()
    D._worker_init("decoy", str(REPO), "", [], sha((CODE / "mbs308_driver.py").read_bytes()), "decoy", True)
    return D, D._W


def child_serial(out: Path, dev: bool = False) -> None:
    """QC04(a): block 0 of decoy 297, every job run serially in THIS process (no pool; per-job caps not applied).
    `dev`: the development ladder (the dev form; never evidence)."""
    D, ctx = _decoy_ctx()
    S1M = D.S1M
    lo, hi, _, _ = D.decoy_cover(297)
    b = S1M.plan(ctx["S1"], D.GUARD, lo, hi)[0]
    ladder = S1M.DEV_LADDER if dev else {"RLR": S1M.LADDER_RLR, "C2B": S1M.LADDER_C2B_N, "C1B": S1M.LADDER_C1B_D}
    t0 = time.time()
    res = {}
    for kind, i, r in S1M.jobs([b], ladder):
        res[f"{kind}:{r}"] = S1M.run_job(ctx, kind, b, r)
    for d in ladder["C1B"]:
        c = res.get(f"C1B:{d}", {})
        if c.get("status") == "CERTIFIED" and c.get("cert") and d <= S1M.C1B_VERIFY_MAX_D:
            res[f"VER:{d}"] = S1M.run_job(ctx, "VER", b, d, c["cert"])
    out.write_text(json.dumps({"block": 0, "results": res, "wall_seconds": round(time.time() - t0, 1)},
                              indent=1, sort_keys=True, default=str) + "\n")


def child_ladder(out: Path, drifts: str, dev: bool = False) -> None:
    """QC04(b) (REVIEW_A0 C4): the pointwise ladder of the frozen driver's job code at the declared drifts (one dyadic,
    with the C1b rungs; one non-dyadic, C2b only), serially in this process; every certificate is reduced to its
    canonical sha256. `dev`: the ONE pointwise drift b of block 0 of decoy 297 at the development ladder's rungs (the
    dev form: the only science a dev run computes lies on decoy 297 block 0)."""
    D, ctx = _decoy_ctx()
    S1M, A0C, GUARD = D.S1M, D.A0C, D.GUARD
    if dev:
        lo, hi, _, _ = D.decoy_cover(297)
        drifts = S1M.fs(S1M.plan(ctx["S1"], GUARD, lo, hi)[0]["b"])
    lad_c2b = S1M.DEV_LADDER["C2B"] if dev else S1M.LADDER_C2B_N
    lad_c1b = S1M.DEV_LADDER["C1B"] if dev else S1M.LADDER_C1B_D
    t0 = time.time()
    res = {}
    for ds in drifts.split(","):
        e = F(ds)
        GUARD.guard_drift(e)
        b = {"index": 0, "tile": (e, e), "hull": (e, e), "b": e}
        dyadic = (e.denominator & (e.denominator - 1)) == 0
        for n in lad_c2b:
            res[f"{ds}:C2B:{n}"] = S1M.run_job(ctx, "C2B", b, n)
        for d in (lad_c1b if dyadic else ()):
            r = S1M.run_job(ctx, "C1B", b, d)
            if r.get("cert"):
                r["cert_sha256"] = A0C.sha256_bytes(A0C.canon(r.pop("cert")))
            res[f"{ds}:C1B:{d}"] = r
    out.write_text(json.dumps({"drifts": drifts, "results": res, "wall_seconds": round(time.time() - t0, 1)},
                              indent=1, sort_keys=True, default=str) + "\n")


def child_e4(out: Path) -> None:
    """QC07(a): stream ASSEMBLY's E4 negative controls (29), regenerated through the research path in this fresh
    process; main() is NOT called (it writes into the research namespace), only its control loop."""
    import types
    D = driver()
    raw = D.PIN.verified_bytes(REPO, E4_PIN, check_git=True)
    path = REPO / E4_PIN[0]
    mod = types.ModuleType("mb308_e4_controls")
    mod.__file__ = str(path)
    sys.modules["mb308_e4_controls"] = mod
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    t0 = time.time()
    rows = [mod.run_control(*c) for c in mod.controls(mod.DG.decoy_set())]
    res = {"controls": len(rows), "detected": sum(1 for r in rows if r["DETECTED"]),
           "not_detected": [r["control"] for r in rows if not r["DETECTED"]],
           "valid_halves_ok": all(r["valid_status"] == "OK" for r in rows), "wall_seconds": round(time.time() - t0, 1)}
    res["pass"] = res["controls"] == 29 and not res["not_detected"] and res["valid_halves_ok"]
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")


def child_mc(out: Path, decoy_path: Path) -> None:
    """QC08: independent Monte Carlo (the cell-307 campaign's pinned simulator, test_rlr307_mc.py) at decoy 297's
    drifts: every RLR block record is checked as in the 307 campaign, and at every b_i U_i >= Lambda_MC - 5 se and
    L_i <= Lambda_MC + 5 se; planted wrong bounds must be flagged."""
    D = driver()
    MC = D.PIN.exec_pinned(REPO, "mb308_rlr307_mc", MC_PIN)
    dec = json.loads(decoy_path.read_text())
    blocks = dec["stage1"]["blocks"]
    rows, ctl = [], {}
    for b in blocks:
        if not b.get("run"):
            continue
        e = float(F(b["b"]))
        est = MC.estimate(e, 971 + 10 * b["index"])
        lam, se = est["Lambda"]
        pw = b["pointwise"]
        row = {"block": b["index"], "U_ok": pw.get("U") is None or float(F(pw["U"])) >= lam - MC.Z * se,
               "L_ok": pw.get("L") is None or float(F(pw["L"])) <= lam + MC.Z * se}
        if b.get("rlr_block"):
            row["rlr_block"] = MC.check(est, b["rlr_block"])["all_hold"]
        rows.append(row)
        if not ctl and pw.get("U") is not None:
            ctl = {"U := Lambda_hat/2 flagged": not (lam / 2 >= lam - MC.Z * se),
                   "L := 2 Lambda_hat flagged": not (2 * lam <= lam + MC.Z * se)}
    res = {"rows": rows, "controls": ctl, "n": len(rows),
           "pass": bool(rows) and all(r["U_ok"] and r["L_ok"] and r.get("rlr_block", True) for r in rows)
           and bool(ctl) and all(ctl.values()), "latent_proxy": "decoy estimates only"}
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")


def spawn_child(args: list, log: Path) -> subprocess.Popen:
    return subprocess.Popen([PY, *FLAGS, str(HERE), *args], stdout=log.open("w"), stderr=subprocess.STDOUT, env=ENV,
                            stdin=subprocess.DEVNULL, cwd=str(REPO))


def load_record(path: Path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None


def frozen_ladder() -> dict:
    S1M = driver().S1M
    return {"RLR": list(S1M.LADDER_RLR), "C2B": list(S1M.LADDER_C2B_N), "C1B": list(S1M.LADDER_C1B_D)}


def official_decoy(cell: int, first_blocks, out: Path, work: Path) -> dict:
    """One OFFICIAL decoy: the real driver's `decoy` (the frozen bytes at their own path) as a transient LaunchAgent of
    the launchd launcher, the frozen ladder, WORKERS, the driver's own MEM_CAP_BYTES and MEM_POLL_S; the compact rule
    inputs of the run are returned, the full record is written to `out`."""
    import mbs308_launch as L
    import mbs308_measure as MEAS
    C = DV.driver_constants((CODE / "mbs308_driver.py").read_text())
    return MEAS.run_decoy(L, interpreter=L.PYTHON, driver=CODE / "mbs308_driver.py", cell=cell,
                          first_blocks=first_blocks, workers=C["WORKERS"], out=out, run_id=f"decoy{cell}",
                          label=L.LABEL_PREFIX + f"{MEAS.DECOY_LABEL}{cell}.{L.utc_compact()}",
                          plist_dir=work / "launch", log_dir=L.LOG_DIR, workdir=REPO, record_dir=work / "launch_records")


def official_decoy_gated(event: dict, cell: int, first_blocks, out: Path, work: Path) -> dict:
    """One official decoy -- unless an EARLIER official decoy of this qualification had a memory-watchdog event (owner
    supplement 2, section 1: the qualification has failed closed; nothing more is launched). `event`: {"seen": bool},
    shared by the phases of one qualification run."""
    if event["seen"]:
        return {"id": f"decoy{cell}", "cell": cell, "record_missing": True,
                "not_run": "AFTER_" + RR.STATUS_OFFICIAL_WATCHDOG}
    r = official_decoy(cell, first_blocks, out, work)
    event["seen"] = bool(RR.cap_events(r.get("watchdog_events")))
    return r


def official_readings() -> dict:
    """The official qualification's OWN prepared-host readings (>= 10, >= 30 s apart), the hosting app and hw.memsize:
    the host-state inputs of canonical outputs B."""
    import mbs308_measure as MEAS
    HOST = host_mod()
    src = (CODE / "mbs308_driver.py").read_text()
    hosting = MEAS.hosting_app()
    fmb = MEAS.driver_function(src, "free_memory_bytes", {"HOST": HOST})
    readings = MEAS.take_readings(lambda: MEAS.reading(fmb, hosting["paths"]))
    hw = (HOST._run([HOST.SYSCTL, "-n", "hw.memsize"]) or "").strip()
    return {"readings": readings, "hosting_app": hosting, "hw_memsize_bytes": int(hw) if hw.isdigit() else None,
            "utc": utc()}


def dev_decoy(out: Path, driver_path: Path = None) -> int:
    """The --dev form of the decoy cases: decoy 297, block 0, the development ladder, 2 workers, run directly (never
    under launchd, never evidence). NONTARGET_DRIFT_VALIDATION."""
    return subprocess.run([PY, *FLAGS, str(driver_path or CODE / "mbs308_driver.py"), "decoy", "--cell", "297",
                           "--first-blocks", "1", "--dev-ladder", "--workers", "2", "--out", str(out)],
                          capture_output=True, env=ENV, cwd=str(REPO), stdin=subprocess.DEVNULL).returncode


# ------------------------------------------------------------------ main
def record_name(case_id: str) -> str:
    return "MBS308_" + case_id.replace("-", "_") + ".json"


def dev_form(summary: dict, checks_ok: bool) -> dict:
    """A dev-form summary: never evidence (`pass` false), with `dev_checks_ok` saying whether the dev run behaved."""
    return dict(summary, **{"pass": False, "status": DEV_STATUS, "dev_checks_ok": bool(checks_ok)})


def qualified_worktree() -> bool:
    """This repository is the campaign's qualified worktree on the qualified branch (the driver's own check_identity).
    The verifier EXECUTES real science (the official decoys under launchd, MB r1's children, the rehearsal, the
    in-process cases) only there: never in a sandbox, a copy or another clone, whatever the preconditions say."""
    D = driver()
    try:
        D.check_identity()
        return True
    except D.Refusal:
        return False


NOT_QUALIFIED = "NOT_THE_QUALIFIED_WORKTREE"


def science_phase(sel: list, mode: str, heavy: bool, cfg: dict, work: Path, odir: Path, rdir: Path,
                  host_rep: dict | None = None) -> dict:
    """The decision-dependent cases (brief 54). Official (and review --heavy): the qualification's own prepared-host
    readings FIRST (the host still idle), then the official decoys ONE AT A TIME under the launchd launcher with the
    frozen values (QC02: 297, every block; QC03: 316, blocks 0-2), then MB r1's children (serial, the ladder pair, E4,
    the Monte Carlo), the rehearsal and the in-process cases, then the evaluations. Review without --heavy: the heavy
    records are re-verified from the committed ones. Dev: decoy 297 block 0 at the dev ladder only; QC01 and the
    in-process cases are loader checks."""
    cases: dict = {}
    want = [c for c in sel if c in SCIENCE_DECOY_CASES + SCIENCE_INPROCESS_CASES + ("QC01", "Q1_theory")]
    if not want:
        return {"cases": cases, "disk": {"checks": [], "refusal": None}, "exit_codes": {}, "host_report": host_rep}
    C = DV.driver_constants((CODE / "mbs308_driver.py").read_text())
    plan = DV.plan_of(cfg)
    paths = {k: odir / v for k, v in OUTS.items()}
    recompute = mode == "official" or (mode == "review" and heavy)
    if mode == "review" and not heavy:                      # re-verify the committed heavy records (read only)
        for k in ("decoy297", "decoy316", "serial", "det_a", "det_b", "mc", "rinputs"):
            paths[k] = rdir / OUTS[k]
    need_decoy = [c for c in want if c in SCIENCE_DECOY_CASES]
    rcs, jobs, disk = {}, {}, {"checks": [], "refusal": None}
    runs, event = [], {"seen": False}
    # official / review runs execute science ONLY in the qualified worktree (a sandbox can never launch the real
    # driver); outside it the executing cases fail closed and only the committed records are re-evaluated
    executes = mode == "dev" or qualified_worktree()
    if not executes:
        recompute = False
    if mode == "dev" and need_decoy:
        gate = disk_check(work, "dev decoy")
        disk["checks"].append(gate)
        if gate["pass"]:
            rcs["decoy297"] = dev_decoy(paths["decoy297"])
        else:
            disk["refusal"] = {"phase": "dev decoy"}
    elif recompute and need_decoy:
        # the read-only host report, embedded in the records (protocol 8.1): the official run's own (taken at its
        # start), else taken here, before the readings and before any decoy
        host_rep = host_rep if host_rep is not None else host_report_record(work)
        rin = official_readings()                           # before any decoy: the prepared idle host
        phases = [(f"official decoy {cell}", (cell, plan[cell], "decoy297" if cell == 297 else f"decoy{cell}"))
                  for cell in sorted(plan)]

        def run_phase(_name, payload):
            cell, fb, key = payload
            return official_decoy_gated(event, cell, fb, paths[key], work)
        gated = SCR.run_gated(phases, gate=lambda name: disk_check(work, name), run=run_phase,
                              verified=lambda r: isinstance(r, dict) and not r.get("record_missing"),
                              clean=lambda name, r: {"deleted": 0})
        disk = {"checks": gated["checks"], "refusal": gated["refusal"]}
        for name, r in gated["results"].items():
            runs.append({k: v for k, v in r.items() if k != "raw_path"})
            jobs[f"decoy{r.get('cell')}"] = r.get("job")
            rcs[f"decoy{r.get('cell')}"] = r.get("exit")
        paths["rinputs"].write_text(json.dumps(official_inputs(rin, runs, host_rep), indent=1, sort_keys=True,
                                               default=str) + "\n")
    # MB r1's children, concurrently (as MB r1 ran them), after the official decoys
    procs = {}
    dflag = ["--_dev"] if mode == "dev" else []
    dec297, dec316 = load_record(paths["decoy297"]), load_record(paths["decoy316"])
    failures = {"decoy297": decoy_failure(dec297), "decoy316": decoy_failure(dec316)}
    dec297 = None if failures["decoy297"] else dec297          # a failed decoy's record is never a science input
    dec316 = None if failures["decoy316"] else dec316
    run_children = (recompute or mode == "dev") and not disk["refusal"] and not event["seen"]
    if run_children and "QC04" in want:
        procs["serial"] = spawn_child(["--_child", "serial", "--out", str(paths["serial"]), *dflag], work / "serial.log")
        for tag in ("det_a", "det_b"):
            procs[tag] = spawn_child(["--_child", "ladder", "--_drift", ",".join(LADDER_DET_DRIFTS), "--out",
                                      str(paths[tag]), *dflag], work / f"{tag}.log")
    if mode != "dev" and executes and "QC07" in want:
        procs["e4"] = spawn_child(["--_child", "e4", "--out", str(paths["asm_controls"])], work / "e4.log")
    for k, p in procs.items():
        p.wait()
        rcs[k] = p.returncode
    if run_children and "QC08" in want and paths["decoy297"].exists() and not failures["decoy297"]:
        with open(work / "mc.log", "w") as fh:
            rcs["mc"] = subprocess.run([PY, *FLAGS, str(HERE), "--_child", "mc", "--_decoy", str(paths["decoy297"]),
                                        "--out", str(paths["mc"])], env=ENV, cwd=str(REPO), stdout=fh,
                                       stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL).returncode
    # ---- QC01 and the in-process cases
    inproc = [c for c in want if c in SCIENCE_INPROCESS_CASES]
    if "QC01" in want:
        if mode == "dev":
            cases["QC01"] = {"pass": False, "status": DEV_STATUS, "dev_form": "never run in dev (the rehearsal reads "
                             "cell 305's committed record: official and review runs only)", "dev_checks_ok": None}
        else:
            cases["QC01"] = run_qc01(paths["rehearse"]) if executes else {"pass": False, "status": NOT_QUALIFIED}
    if inproc and not executes:
        for c in inproc:
            cases[c] = {"pass": False, "status": NOT_QUALIFIED}
    elif inproc and mode == "dev":
        names = {"QC05": ["test_mb308_twosided"], "QC06": ["test_mb308_a0"], "QC07": ["test_mb308_tptb"],
                 "QC09-SCI": ["test_mb308_guard"]}
        for c in inproc:
            cases[c] = dev_loader_only(c, names[c])
    elif inproc:
        try:
            res = science_inprocess(set(inproc), mode)
        except Exception as exc:                                       # noqa: BLE001 (a failed case, recorded)
            res = {"error": f"{type(exc).__name__}: {exc}"[:400]}
        for c in inproc:
            if c == "QC07":
                cases[c] = qc07_summary(load_record(paths["asm_controls"]), res.get("QC07_formal"))
            else:
                cases[c] = science_summary(res.get(c))
            if "error" in res:
                cases[c] = dict(cases[c], error=res["error"])
    if "Q1_theory" in want:
        cases["Q1_theory"] = q1_theory()
    # ---- the heavy records' evaluations
    if host_rep is None:                                     # a review of committed records: the report they embed
        host_rep = (load_record(paths["rinputs"]) or {}).get("host_report")
    if disk["refusal"]:
        for c in need_decoy:
            cases[c] = {"pass": False, "status": "DISK_REFUSED", "refused_before": disk["refusal"].get("phase")}
        return {"cases": cases, "disk": disk, "exit_codes": rcs, "host_report": host_rep}
    if not executes and (mode == "official" or heavy):       # the records would have to be MADE here: never
        for c in need_decoy:
            cases[c] = {"pass": False, "status": NOT_QUALIFIED}
        return {"cases": cases, "disk": disk, "exit_codes": rcs, "host_report": host_rep}
    dev = mode == "dev"
    if "QC02" in want:
        ev = failures["decoy297"] or qc02_eval(dec297, frozen_ladder())
        cases["QC02"] = dev_form(dict(ev, exit=rcs.get("decoy297")), bool(dec297) and
                                 dec297["stage1"]["blocks"][0].get("run") is True) if dev else \
            with_official_config(ev, dec297, jobs.get("decoy297"), plan.get(297), C["WORKERS"],
                                 rcs.get("decoy297", "committed"))
    if "QC03" in want:
        if dev:           # the dev form's stand-in is the dev record of decoy 297 block 0 (cell 316 is official only)
            cases["QC03"] = dev_form({"stand_in": "decoy 297 block 0"}, bool(dec297) and
                                     dec297["stage1"]["blocks"][0].get("run") is True)
        else:
            cases["QC03"] = with_official_config(failures["decoy316"] or qc03_eval(dec316), dec316,
                                                 jobs.get("decoy316"), plan.get(316), C["WORKERS"],
                                                 rcs.get("decoy316", "committed"))
    if "QC04" in want:
        ev = qc04_eval(dec297, load_record(paths["serial"]), load_record(paths["det_a"]), load_record(paths["det_b"]))
        cases["QC04"] = dev_form(ev, ev["pass"] is True) if dev else ev
    if "QC08" in want:
        ev = load_record(paths["mc"]) or {"pass": False, "missing": "decoy 297 record"}
        cases["QC08"] = dev_form(ev, ev.get("pass") is True) if dev else science_summary(ev)
    if "MBR1_REPRO" in want:
        try:
            theirs = {k: json.loads(pinned_bytes(pin)) for k, pin in MBR1_RECORD_PINS.items()}
        except (OSError, ValueError) as exc:
            theirs, cases["MBR1_REPRO"] = None, {"pass": False, "reason": f"MB r1's committed records: {exc}"[:300]}
        if theirs is not None and dev:
            cases["MBR1_REPRO"] = mbr1_repro_tiny(dec297, theirs["decoy297"])
        elif theirs is not None:
            cases["MBR1_REPRO"] = mbr1_repro({"decoy297": dec297, "decoy316": dec316,
                                              "serial": load_record(paths["serial"]),
                                              "det_a": load_record(paths["det_a"]),
                                              "det_b": load_record(paths["det_b"])}, theirs)
    src, state_src = (CODE / "mbs308_driver.py").read_text(), (CODE / "mbs308_state.py").read_text()
    if "Q12_caps" in want:
        ev = q12_caps(dec297, dec316, driver_src=src, state_src=state_src,
                      section4=cfg["owner_decisions"]["MBS-8"]["values"])
        cases["Q12_caps"] = dev_form(ev, (ev.get("planted_controls") or {}).get("pass") is True and
                                     (ev.get("section4_values") or {}).get("pass") is True) if dev else ev
    if "R_RULES_OFFICIAL" in want:
        if dev:
            run = DV.compact_run(dec297 or {}, "decoy297", exit_code=rcs.get("decoy297"))
            ok = isinstance(run.get("driver_maxrss_bytes"), int) and bool(run.get("jobs")) and \
                DV.sampler_input([run]) is not None and isinstance(run.get("watchdog_events"), list) and \
                isinstance((run.get("rss_sampler") or {}).get("max_spacing_ns"), int)
            cases["R_RULES_OFFICIAL"] = dev_form({"rule_inputs_present_in_the_dev_record": ok}, ok)
        else:
            evp, dvp = NS / "evidence_prefreeze" / DV.EVIDENCE_NAME, NS / "evidence_prefreeze" / DV.DERIVATION_NAME
            ev_raw = evp.read_bytes() if evp.is_file() else None
            evd = load_record(evp)
            measured = None
            if isinstance(evd, dict) and evd.get("commit"):
                raw = git_show_bytes(str(evd["commit"]), NS_REL + "/code/mbs308_driver.py")
                measured = raw.decode() if raw is not None else None
            try:
                base = DV.base_names_of(cfg, REPO)
                cases["R_RULES_OFFICIAL"] = r_rules_official(
                    evidence=evd, evidence_sha256=sha(ev_raw) if ev_raw is not None else None,
                    derivation=load_record(dvp), official=load_record(paths["rinputs"]), driver_src=src,
                    measured_driver_src=measured, cfg=cfg, base_names=base)
            except DV.DeriveRefusal as exc:
                cases["R_RULES_OFFICIAL"] = {"pass": False, "reason": str(exc)[:300]}
    return {"cases": cases, "disk": disk, "exit_codes": rcs, "host_report": host_rep}


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
    ap.add_argument("--_child", choices=("serial", "ladder", "e4", "mc"))
    ap.add_argument("--_drift")
    ap.add_argument("--_decoy")
    ap.add_argument("--_dev", action="store_true")
    a = ap.parse_args(argv)
    if a._child:                                                 # MB r1's children (fresh processes of this verifier)
        {"serial": lambda: child_serial(Path(a.out), a._dev),
         "ladder": lambda: child_ladder(Path(a.out), a._drift, a._dev), "e4": lambda: child_e4(Path(a.out)),
         "mc": lambda: child_mc(Path(a.out), Path(a._decoy))}[a._child]()
        return 0
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
    host_rep = None
    if mode == "official":                                           # the whole official run keeps the host awake
        D = driver()
        host0 = {"keep_awake": D.HOST.keep_awake(), "start": D.HOST.snapshot(), "sampler": D.HOST.Sampler().start()}
        host_rep = host_report_record(work_base)    # read-only, at the start: embedded in the record (protocol 8.1)
    ids = [c["id"] for c in cfg["cases"]]
    sel = ids if mode != "dev" else [i for i in (a.only or "").split(",") if i in ids]
    work_base.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="mbs308q", dir=work_base)).resolve()
    life = SCR.begin(work, f"mbs308_qualify {mode}")          # the verifier's own scratch record (brief 50)
    odir = QDIR if mode == "official" else work
    odir.mkdir(exist_ok=True)
    env = suite_env(work)
    heavy = mode == "official" or a.heavy
    rdir = Path(a.records).resolve() if a.records else QDIR
    cases: dict = {}
    for cid in sel:
        if cid in PENDING_CASES:
            cases[cid] = pending(cid)
    # the decision-dependent cases FIRST: the official decoys and the prepared-host readings need the idle host
    sci = science_phase([c for c in sel if c not in PENDING_CASES], mode, heavy, cfg, work, odir, rdir, host_rep)
    cases.update(sci["cases"])
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
              "child_exit_codes": sci["exit_codes"],
              "record_sha256": {p.name: sha(p.read_bytes()) for p in sorted(odir.glob("MBS308_*.json"))
                                if p.name != QUAL_NAME},
              "ledger_entries": [
                  {"agent": "mbs308_qualification", "class": "HISTORICAL_RECONSTRUCTION",
                   "what": "QC01 rehearse cell 305 (C-A, C-B reproduction only; committed record; equality booleans)"},
                  {"agent": "mbs308_qualification", "class": "NONTARGET_DRIFT_VALIDATION",
                   "what": "QC02-QC04, QC06, QC08, MBR1_REPRO, QS-RESUME-DECOY: decoy cells 297 / 316 and MB r1's "
                           "validation drifts 3, 27/10, 11/10 (the official decoys under the launchd launcher)"},
                  {"agent": "mbs308_qualification", "class": "SYNTHETIC_VALIDATION",
                   "what": "QC05, QC07 synthetic sets and decoy bundles; QS-* suites and the mutant matrix (sandboxes "
                           "on a separate base store, synthetic evaluator and launchd payload); QC09-S, QC09-SCI "
                           "(refusals only); Q12 and R-rule planted controls"},
                  {"agent": "mbs308_qualification", "class": "INFRASTRUCTURE",
                   "what": "QC11-S static, QC12-S leak scans (counts only), QC13-S governance, Q8-S manifest, "
                           "Q1_theory, R_RULES_OFFICIAL (rule inputs: memory, host readings; no certified value)"}],
              "target_evaluations": 0, "host": host,
              # the read-only host report (protocol 8.1), embedded; it references where the operator's actions are
              # recorded (the research ledger). A recorded field: its statuses gate nothing here.
              "host_report": host_rep if host_rep is not None else sci.get("host_report"),
              "disk": {"threshold_bytes": SCR.QUAL_MIN_FREE_BYTES, "repository_threshold_bytes": SCR.HOST.MIN_FREE_DISK,
                       "start": disk0, "checks": sci["disk"]["checks"] + gated["checks"],
                       "cleanups": gated["cleanups"], "refusal": sci["disk"]["refusal"] or gated["refusal"]}}
    out = Path(a.out) if a.out else odir / QUAL_NAME
    out.write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
    SCR.finish(life)
    tag = lambda v: "PENDING" if v.get("status") == PENDING_STATUS else ("P" if v.get("pass") is True else "F")  # noqa
    print(f"QUALIFICATION {'PASS' if agg['pass'] else ('DEV' if mode == 'dev' else 'FAIL')}: " +
          " ".join(f"{k}={tag(v) if isinstance(v, dict) else '?'}" for k, v in sorted(cases.items())))
    return 0 if agg["pass"] or mode == "dev" else 1


if __name__ == "__main__":
    sys.exit(main())
