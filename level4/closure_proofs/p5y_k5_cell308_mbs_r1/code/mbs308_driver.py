"""Cell-308 MB-S successor campaign (r1) -- the cell-308-only exactly-once driver, derived from MB r1's mb308_driver.

THE SCIENCE IS MB r1's, BYTE-IDENTICAL. The science modules (mb308_stage1, mb308_supply, mb308_consumer, mb308_a0core,
mb308_pinned) are NOT copied: they are executed from MB r1's committed bytes at MB r1's paths, each checked against its
sha256 and its git blob at 21e99cf0 (SCIENCE_PINS), and MB r1's research pins come with them unchanged. Every
science-glue function of this file (controls, compose_and_consume, decide, target_geometry, admitted_pairs,
prepare_target, stage1 / public_stage1 with the Stage-1 admission and aggregation rules, load_science, _worker_init,
_worker_job, _set_job_cap, evaluate_target, the decoy / rehearsal helpers, ...) is TEXT-IDENTICAL to MB r1's
(c46434a3 == 21e99cf0); DRIVER_DIFF.md classifies every hunk and a test compares the function sources by ast.

WHAT CHANGES (lifecycle and identity only; architecture SUCCESSOR_ARCHITECTURE_308.md sections 1-8):
  * identity: the successor worktree, branch, namespace and refs (refs/p5y-k5-cell308-mbs-r1/...), the guard
    mbs308_guard (MB r1's with the successor's marker ref only), MB r1's recorded state asserted exactly (GC-8);
  * a durable state machine (mbs308_state): the journal (blob + CAS), the spool persistence of section 3, the
    pending ref, the seal and materialization, governed Stage-1 checkpoints and a mandatory, budgeted `resume`, the
    read-only classifier (`status` prints the state name only) and `recover` as the only dispatcher;
  * checkpoints enter MB r1's unchanged stage1() through the two names it already uses, ProcessPoolExecutor and wait,
    bound here to mbs308_state.CheckpointingPool / checkpointing_wait (plus the per-job peak RSS record and the
    memory watchdog of GC-10);
  * the host contract (mbs308_host): preflight gates before the marker (AC, low-power mode 0, thermal level 0, disk,
    memory pressure and headroom, boot UUID, no other campaign job, host exclusivity, platform pins RC2, launched by
    the launchd launcher mbs308_launch); a supervised caffeinate; EVAL_CAP per attempt on awake time.

modes
    preflight                          read-only: bindings, governance, MB r1 state, platform, host gates (no launcher)
    rehearse --cell 305                read-only: controls C-A and C-B on cell 305's COMMITTED record (equality only)
    decoy --cell 297|316 [--first-blocks K] [--dev-ladder] --out F
                                       MB r1's decoy mode (writes only --out)
    execute                            launchd-launched, granted worktree only: the ONE evaluation of cell 308
    status                             read-only: prints the state name only
    recover                            the only dispatcher: performs exactly the frozen action of the classified state
    resume                             CONSUMED_INTERRUPTED only (launchd-launched): verified checkpoints are reused
    seal-only                          RESULT_DURABLE_UNSEALED / PENDING_RESULT (and materialize when SEALED); never computes
    close-indeterminate                CONSUMED_UNRECORDED only: seals the value-free INDETERMINATE record

exit codes: 0 sealed TARGET_EVALUATED (or: nothing to do); 2 REFUSED (nothing consumed / nothing changed); 3
            CONTROL_FAILED sealed (target not consumed); 4 UNSEALED (evidence durable; run recover); 5 sealed with a
            post-marker failure status or the INDETERMINATE record; 6 nothing durable (run recover: it resumes); 7
            sealed, worktree copy not materialized (run recover); 8 CONSUMED_COMPUTING (wait); 9 lost ownership (another
            attempt owns the run; nothing written)
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import multiprocessing
import os
import resource
import secrets
import signal
import stat
import subprocess
import sys
import tempfile
import time
import types
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
import mbs308_guard as GUARD  # noqa: E402
import mbs308_host as HOST  # noqa: E402
import mbs308_state as STATE  # noqa: E402

CP = "level4/closure_proofs/"
# ------------------------------------------------------------------ the science: MB r1's bytes at MB r1's paths
NSF_REL = CP + "p5y_k5_cell308_mb_r1"
SCIENCE_BASE_COMMIT = "21e99cf05d60b985e33f337aa4c5a7fd1507402a"      # MB r1 postexec (== freeze r3 c46434a3 bytes)
SCIENCE_PINS = {   # name -> (sha256, git blob at SCIENCE_BASE_COMMIT); load order = dependency order
    "mb308_a0core": ("0873604379bb5008f385ed09c7ae2f0694a402a91881b6a9d2e45649af332de6",
                     "379469a2c4e3432a64ca28fe318a7fd803cb8816"),
    "mb308_stage1": ("23296f837eb7520b36c32bba08d238d940c14a8753e8ce8cadb05f0990f2ec98",
                     "518150ba19991894d6cdd2621f8e60ce9784313c"),
    "mb308_supply": ("af1a818b68459ada53773557e10153ae4ae3edc232d52e93fd19814e4da59b58",
                     "8c4463e7191bb267ff7e2f00603b9c1a4f61ff18"),
    "mb308_consumer": ("c233bdb6235cd8a44bcf187be7d6686a4684f8619bed21ade9130432c5c09188",
                       "2ffdfa631551065e5b0440a0edd09d92ff1a64cd"),
    "mb308_pinned": ("5c221a0e70a708c580f13e1cd622556930f047f3c0b302227a8d9b18c52220a2",
                     "e714650d79aa0bb6ad644784403b0ce01accb78f"),
}


class SciencePinError(RuntimeError):
    """A science module's bytes are not MB r1's pinned bytes (nothing runs)."""


def _science_rev(rel: str) -> str:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(REPO), "rev-parse", f"HEAD:{rel}"],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL,
                       env={"PATH": "/usr/bin:/bin", "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"})
    return p.stdout.strip() if p.returncode == 0 else ""


def load_science_module(name: str) -> types.ModuleType:
    """Execute MB r1's module `name` from its committed bytes (sha256 + git blob, also at HEAD), registered under its own
    name so that MB r1's intra-science imports (mb308_stage1 -> mb308_a0core) resolve to the pinned object."""
    want_sha, want_blob = SCIENCE_PINS[name]
    rel = f"{NSF_REL}/code/{name}.py"
    raw = (REPO / rel).read_bytes()
    if hashlib.sha256(raw).hexdigest() != want_sha or STATE.git_blob_id(raw) != want_blob:
        raise SciencePinError(f"{rel}: bytes differ from MB r1's pinned bytes")
    if _science_rev(rel) != want_blob:
        raise SciencePinError(f"{rel}: HEAD does not hold MB r1's blob")
    cur = sys.modules.get(name)
    if cur is not None:
        if getattr(cur, "_mbs308_sha256", None) != want_sha:
            raise SciencePinError(f"{name} is already imported from somewhere else")
        return cur
    mod = types.ModuleType(name)
    mod.__file__ = str(REPO / rel)
    mod._mbs308_sha256 = want_sha
    sys.modules[name] = mod
    exec(compile(raw, str(REPO / rel), "exec"), mod.__dict__)
    return mod


def check_science_modules() -> dict:
    """Re-check every science module's on-disk bytes and HEAD blob (preflight / execute / resume)."""
    out = {}
    for name, (want_sha, want_blob) in SCIENCE_PINS.items():
        rel = f"{NSF_REL}/code/{name}.py"
        raw = (REPO / rel).read_bytes()
        if hashlib.sha256(raw).hexdigest() != want_sha or STATE.git_blob_id(raw) != want_blob or \
                _science_rev(rel) != want_blob or getattr(sys.modules.get(name), "_mbs308_sha256", None) != want_sha:
            raise Refusal("SCIENCE_PIN_MISMATCH", rel)
        out[rel] = {"sha256": want_sha, "blob": want_blob}
    return out


A0C = load_science_module("mb308_a0core")
S1M = load_science_module("mb308_stage1")
SUP = load_science_module("mb308_supply")
CON = load_science_module("mb308_consumer")
PIN = load_science_module("mb308_pinned")

# lifecycle (architecture section 4): MB r1's stage1() is unchanged; checkpoints, the per-job peak RSS and the memory
# watchdog enter through the two names it uses.
ProcessPoolExecutor = STATE.CheckpointingPool  # noqa: F811
wait = STATE.checkpointing_wait  # noqa: F811

# ------------------------------------------------------------------ identity (the successor's)
NS_REL = CP + "p5y_k5_cell308_mbs_r1"
QUALIFIED_WORKTREE = "/Users/suzhe/ReBaseGuard-c308mbs"
QUALIFIED_GIT_DIR = "/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-c308mbs"
QUALIFIED_COMMON_DIR = "/Users/suzhe/ReBaseGuard/.git"
QUALIFIED_BRANCH = "refs/heads/p5y-k5-cell308-mbs-r1"

TARGET_CELL = 308
REHEARSAL_CELLS = (305,)
DECOY_CELLS = (297, 316)
FIELDS = ("A0", "A1", "A2")
FROZEN_DIRS = ("code", "protocol", "theory", "tests", "config", "errata", "evidence_prefreeze")
POST_FREEZE_DIRS = ("qualification", "review", "authorization", "evidence", "adjudication", "postexec")
DECOY_SEED = 20260929
DECOY_BUNDLES = (("taylor", 1, "cut"), ("midpoint", -1, "loose"), ("mixed", 1, "cut_both"))

EXEC_DIR_REL = NS_REL + "/evidence/execution"
RESULT_NAME = "MBS308_CELL308_RESULT.json"
RESULT_REL = EXEC_DIR_REL + "/" + RESULT_NAME
GUARDED_PATHS = (EXEC_DIR_REL, RESULT_REL, EXEC_DIR_REL + "/MBS308_CELL308_RESULT.tmp",
                 EXEC_DIR_REL + "/MBS308_CELL308_RESULT.json.tmp", EXEC_DIR_REL + "/MBS308_CELL308_RESULT.partial")
GRANT_REL = NS_REL + "/authorization/MBS308_GRANT.json"
QUAL_DIR_REL = NS_REL + "/qualification/"
QUAL_REL = QUAL_DIR_REL + "MBS308_QUALIFICATION.json"
QREVIEW_REL = NS_REL + "/review/MBS308_QUALIFICATION_REVIEW.md"
MANIFEST_REL = NS_REL + "/protocol/MBS308_FREEZE.json"
CONSUMED_REF = GUARD.CONSUMED_REF
PENDING_REF = STATE.PENDING_REF
JOURNAL_REF = STATE.JOURNAL_REF
CKPT_REF = STATE.CKPT_REF
PRIOR_MARKERS = (STATE.REF_PREFIX,)
R6_NAME = "K5_COVERAGE_MAP_R6"
GRANT_SCHEMA = "rebaseguard.p5y.k5.cell308-mbs-r1.grant.v1"
# GC-8: MB r1's recorded state, asserted EXACTLY (a named, reviewed exception; never a prefix wildcard)
MBR1_PREFIX = "refs/p5y-k5-cell308-mb-r1/"
MBR1_MARKER = MBR1_PREFIX + "target-consumed"
MBR1_MARKER_TARGET = "afa930727d084a5b70e6b85d30ca8f34c0e8ae74"
MBR1_BRANCH = "refs/heads/p5y-k5-cell308-mb-r1"
MBR1_GIT_DIR = "/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-c308mb"
MBR1_EMERGENCY_NAME = "mb308-cell308-emergency-result.json"
WORKERS = 5                      # design D11
PRE_CAP_S = 1800                 # everything before the marker (controls included)
EVAL_CAP_S = 8 * 3600            # MB r1 protocol 3.2; MB-S: per attempt, on awake time (architecture section 8)
DECOY_CAP_S = 12 * 3600
SEAL_RETRY_DELAYS = (0.5, 1.0, 2.0, 4.0)
ENV = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/var/empty"), "GIT_OPTIONAL_LOCKS": "0",
       "GIT_NO_REPLACE_OBJECTS": "1", "LC_ALL": "C"}
SCHEMA = STATE.RESULT_SCHEMA
OUTCOMES = ("CELL308_CLOSED_UNDER_MB", "CELL308_NOT_CLOSED_UNDER_MB", "CELL308_EXECUTION_INDETERMINATE")
# GC-10 (provisional; set at the freeze by rule R-MEM of CONSTANTS_RATIFICATION_MBS308 (research 3c2a7854; protocol
# section 8) from the OFFICIAL decoy runs, never from any target run). The provisional 3 GiB is ratified for the
# pre-freeze build and as the measurement cap of the official decoys only.
MEM_CAP_BYTES = 3 * 1024 ** 3
MEM_POLL_S = 2.0
# RC2: the platform the qualification measured; preflight / execute / resume refuse on any mismatch (re-pinned at
# freeze from the qualification host)
PLATFORM_PINS = {
    "python_executable": "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14",
    "python_sha256": "bd3498159da515acf12963b736f3e7e7599619204348868e018bbbc9e0fc9343",
    "libpython": "/Library/Frameworks/Python.framework/Versions/3.14/Python",
    "libpython_sha256": "34463f1b2fc9b5507f493af35080960ba3e86b94c0832c83ea771f8f252b5a55",
    "python_version": "3.14.5",
    "python_sys_version": "3.14.5 (v3.14.5:5607950ef23, May 10 2026, 07:38:09) [Clang 21.0.0 (clang-2100.0.123.102)]",
    "os_build": "25F84",
    "arch": "arm64",
}

# helper modules of this campaign, pinned by sha256 (the grant binds this driver's own sha256). Re-pinned at freeze.
HELPER_SHA256 = {
    "mbs308_guard.py": "48903487f648e9d39bb764497ceae87941c33be73cb4b1fa285ac83bbb1e9435",
    "mbs308_host.py": "6650ceebd7297dd4744c6121f9b41617aabbd50211a634df309c53b5945a2a8b",
    "mbs308_state.py": "e2b6b8e1bb35c2957fca41a5d007e355eddd6e213d66d68995b4d8781895e047",
    "mbs308_launch.py": "1510308a96911278ca157f0305ee122e1a2a9632f1330bfed3ab428c7d6ba5c8",
}
PIN.GUARD_SHA256 = HELPER_SHA256["mbs308_guard.py"]
# per-job CPU caps (REVIEW_A0_CERTIFIER_R1 C3): each Stage-1 job runs in a FRESH worker process (max_tasks_per_child
# = 1) whose RLIMIT_CPU is set to exactly the declared cap; a job refuses to start if an outer hard limit would make the
# effective cap smaller than the declared one. A cap hit kills the worker: an execution failure, never a dropped rung.
# Values: protocol 3.2 (max(3 x the larger decoy wall time rounded up to 300 s, 1800 s)); C1B d4 and every VER entry
# serve only the decoy development ladder / are unused by the frozen ladder (C1b d > 6 is never verified).
RUNG_CPU_CAP_S = {"RLR": {4: 1800, 6: 4200, 8: 8700}, "C2B": {20: 1800, 40: 1800, 80: 2700},
                  "C1B": {4: 1800, 8: 1800, 10: 1800, 12: 1800},
                  "VER": {4: 1800, 6: 1800, 8: 1800, 10: 1800, 12: 1800}}
LINEAGE = [("5a94568af69f775eaabdeb895dea19b9bf664935", "D stage"), ("ae4cbc2c", "coverage map r5"),
           ("a15d083b009868e38a5bd5a808f38f19e6ab4b92", "floor r2"),
           ("3fadb422eaba97123d46e98b9e80277a62a042c8", "REPLACEMENT_FLOOR_ACCEPTED"),
           ("9c2cbf21", "CELL306_NOT_ADOPTED"), ("c5324a78", "ADJUDICATION_ACCEPTED"),
           ("d3b60795", "FREEZE_READY"), ("7f45e048c39023f4805b21a461650fd332af951f", "morning handover"),
           ("b73b9449", "CELL307_CLOSED_UNDER_RLR"),
           # the research lineage required by the coordinator (note 6, item 5)
           ("33185113", "charter"), ("bfa9ad3c", "Theorem MB r1"), ("a7014669", "stream INDEP"),
           ("0292d654", "stream INDEP_TUPLE"), ("e042c8d1", "A0 certifier review"),
           ("f42fef40", "incident-independence review"), ("8da57f89", "incident-review conditions"),
           ("58f190dc", "stream VERIFY follow-up"), ("55d3719c", "pre-freeze formal build"),
           ("fc4eeeee", "stream-A0 certificates"), ("cc249872", "protocol draft p0"),
           # MB-S: MB r1's own chain (consumed, interrupted, INDETERMINATE; history only)
           ("c46434a399eca18a709616a4a4d51918d1a30298", "FREEZE r3"),
           ("7eb057bbbcb3c8d18afc852c1d90f0b3fc0fefc8", "official qualification at freeze r3"),
           ("47bb37c724841c6a8d53bc89eba28765609598ea", "QUALIFICATION_ACCEPTED"),
           ("afa930727d084a5b70e6b85d30ca8f34c0e8ae74", "GRANT"),
           ("21e99cf05d60b985e33f337aa4c5a7fd1507402a", "postexec")]


class Refusal(Exception):
    """Fail closed BEFORE the marker: nothing is evaluated, nothing is consumed."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


class IndependentCheckFailed(RuntimeError):
    """A layer disagrees with its independent reconstruction or verifier (after the marker: INDETERMINATE)."""


class Inconsistent(RuntimeError):
    """L_i > U_i at some pointwise drift: a soundness alarm (after the marker: INDETERMINATE)."""


# ------------------------------------------------------------------ plumbing
def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_blob_id(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def git(*args, env_extra=None, input_bytes=None):
    env = dict(ENV)
    if env_extra:
        env.update(env_extra)
    if input_bytes is not None:
        p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(REPO), *args], input=input_bytes,
                           capture_output=True, env=env)
        return subprocess.CompletedProcess(p.args, p.returncode, p.stdout.decode(errors="replace"),
                                           p.stderr.decode(errors="replace"))
    return subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(REPO), *args],
                          capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def fs(x) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def verdict_ok(text: str, expected: str) -> bool:
    lines = text.splitlines()
    return len(lines) > 1 and lines[1].strip() == expected and sum(1 for ln in lines if ln.strip() == expected) == 1


def freeze_commit() -> str:
    return git("log", "-1", "--format=%H", "--", *(f"{NS_REL}/{d}" for d in FROZEN_DIRS)).stdout.strip()


def git_dir() -> Path:
    return Path(git("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip())


def check_helpers() -> dict:
    out = {}
    for name, pin in HELPER_SHA256.items():
        got = sha((CODE / name).read_bytes())
        if got != pin:
            raise Refusal("HELPER_PIN_MISMATCH", name)
        out[name] = got
    return out


def jsonable(o):
    if isinstance(o, F):
        return fs(o)
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    return o


# ------------------------------------------------------------------ identity, flags, prior evaluation, paths
def check_flags() -> None:
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        raise Refusal("INTERPRETER_FLAGS", "execute and seal-only require python3.14 -I -S -B")


def check_identity() -> dict:
    here = str(REPO.resolve())
    gd = git("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip()
    cd = git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    br = git("symbolic-ref", "-q", "HEAD").stdout.strip()
    if here != QUALIFIED_WORKTREE or str(Path(gd).resolve()) != QUALIFIED_GIT_DIR or \
            str(Path(cd).resolve()) != QUALIFIED_COMMON_DIR:
        raise Refusal("REPO_NOT_QUALIFIED", "not the qualified worktree / git dir / common dir")
    if br != QUALIFIED_BRANCH:
        raise Refusal("WRONG_BRANCH", br or "detached HEAD")
    return {"worktree": here, "git_dir": gd, "common_dir": cd, "branch": br}


def store() -> STATE.Store:
    # R1 (i): a ref write that fails WITHOUT a compare-and-swap conflict is retried on MB r1's frozen seal-retry
    # schedule (SEAL_RETRY_DELAYS; no new number), then raised as STATE.RefWriteError (infrastructure)
    return STATE.Store(REPO, QUALIFIED_BRANCH, retry_delays=SEAL_RETRY_DELAYS)


def campaign() -> STATE.Campaign:
    return STATE.Campaign(store(), RESULT_REL, GRANT_REL)


def check_mbr1_state() -> dict:
    """GC-8: MB r1's recorded state, exactly: its marker -> afa93072 is the ONLY ref under its prefix; no pending ref;
    no mb308 emergency file in MB r1's git dir, this git dir or the common dir; no NSF/evidence path in this worktree,
    at HEAD or on MB r1's branch. MB r1's refs are read here and nowhere else, and never written."""
    refs = [ln.split() for ln in git("for-each-ref", "--format=%(refname) %(objectname)", MBR1_PREFIX).stdout.splitlines()]
    if refs != [[MBR1_MARKER, MBR1_MARKER_TARGET]]:
        raise Refusal("MBR1_STATE", "MB r1's refs are not exactly its recorded marker")
    cd = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    for d in (Path(MBR1_GIT_DIR), git_dir(), cd):
        if os.path.lexists(d / MBR1_EMERGENCY_NAME):
            raise Refusal("MBR1_STATE", "an MB r1 emergency file exists")
    ev = NSF_REL + "/evidence"
    if os.path.lexists(REPO / ev):
        raise Refusal("MBR1_STATE", "an NSF/evidence path exists in the worktree")
    for tip in ("HEAD", MBR1_BRANCH):
        if not git("rev-parse", "-q", "--verify", tip).stdout.strip():
            raise Refusal("MBR1_STATE", f"{tip} does not resolve")
        if git("ls-tree", tip, "--", ev).stdout.strip():
            raise Refusal("MBR1_STATE", f"{tip} holds an NSF/evidence path")
    return {"mbr1_marker": MBR1_MARKER_TARGET, "only_ref": True, "no_pending": True, "no_emergency_file": True,
            "no_evidence_path": True}


def check_not_evaluated() -> dict:
    """No prior MB-S evaluation: no marker / pending / checkpoint ref, no result anywhere, no spool result file. A
    journal is allowed only as a STALE pre-marker intent (state ARMING, or ABORTED_INTENT after a marker write that
    failed; its process dead; no marker): execute takes it over. R1 (iii): a campaign git lockfile refuses (GIT_LOCKED;
    `recover` moves stale ones aside)."""
    locks = STATE.git_lockfiles(store())
    if locks:
        raise Refusal("GIT_LOCKED", f"campaign git lockfile(s) {', '.join(locks)}: run `recover`")
    refs = git("for-each-ref", "--format=%(refname)", PRIOR_MARKERS[0]).stdout.split()
    if any(r != JOURNAL_REF for r in refs):
        raise Refusal("CONSUMED", f"a ref exists under {PRIOR_MARKERS[0]}")
    stale = None
    if JOURNAL_REF in refs:
        jid, jrec = STATE.Journal.read(store())
        if jrec is None or jrec["state"] not in ("ARMING", "ABORTED_INTENT") or \
                HOST.identity_alive(jrec.get("process")):
            raise Refusal("CONSUMED", "a journal exists that is not a stale pre-marker intent")
        stale = jid
    names = git("ls-tree", "-r", "--name-only", "HEAD").stdout.split()
    if RESULT_REL in names or os.path.lexists(REPO / RESULT_REL) or \
            git("log", "--all", "--format=%H", "--", RESULT_REL).stdout.strip():
        raise Refusal("TARGET_ARTIFACT_EXISTS", RESULT_REL)
    sp = store().spool()
    if os.path.lexists(sp) and any(n.startswith(STATE.RESULT_FILE) for n in os.listdir(sp)):
        raise Refusal("TARGET_ARTIFACT_EXISTS", "a result file exists in the spool")
    return {"stale_intent_journal": stale}


def check_result_paths() -> None:
    for rel in GUARDED_PATHS:
        try:
            st = os.lstat(REPO / rel)
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise Refusal("RESULT_PATH_OCCUPIED", f"{rel}: unreadable ({exc.__class__.__name__})")
        raise Refusal("RESULT_PATH_OCCUPIED", f"{rel} holds a {stat.filemode(st.st_mode)} object")
    cur = REPO
    for part in (NS_REL + "/evidence").split("/"):
        cur = cur / part
        try:
            st = os.lstat(cur)
        except FileNotFoundError:
            break
        if not stat.S_ISDIR(st.st_mode):
            raise Refusal("RESULT_PATH_OCCUPIED", f"{cur.relative_to(REPO)} is not a plain directory")


def check_clean() -> None:
    if git("status", "--porcelain", "--untracked-files=all").stdout.strip():
        raise Refusal("DIRTY_TREE")
    if git("status", "--porcelain", "--ignored", "--untracked-files=all", "--", NS_REL).stdout.strip():
        raise Refusal("IGNORED_OBJECT", "an ignored or untracked object exists in the campaign namespace")
    gd, cd = git_dir(), Path(git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    locks = [p for p in (gd / "index.lock", gd / "HEAD.lock", cd / (QUALIFIED_BRANCH + ".lock"),
                         cd / "packed-refs.lock") if os.path.lexists(p)]
    if locks:
        raise Refusal("GIT_LOCKED", str(locks[0]))


def check_seal_preconditions() -> dict:
    if git("var", "GIT_COMMITTER_IDENT").returncode or git("var", "GIT_AUTHOR_IDENT").returncode:
        raise Refusal("SEAL_PRECONDITION", "no committer/author identity")
    head = git("rev-parse", "HEAD").stdout.strip()
    # MB-S: distinct, nonce-carrying probe bytes (never MB r1's probe blob; never an object that already exists, so no
    # write through alternates can freshen an existing object's mtime)
    probe = b"mbs308 object-store write probe " + secrets.token_hex(16).encode() + b"\n"
    w = git("hash-object", "-w", "--stdin", input_bytes=probe)
    if w.returncode or w.stdout.strip() != git_blob_id(probe):
        raise Refusal("SEAL_PRECONDITION", "the object store is not writable")
    with tempfile.TemporaryDirectory(prefix="mbs308pre") as td:
        idx = {"GIT_INDEX_FILE": str(Path(td) / "index")}
        tree = git("write-tree", env_extra=idx) if not git("read-tree", head, env_extra=idx).returncode else None
        if tree is None or tree.returncode:
            raise Refusal("SEAL_PRECONDITION", "a private index cannot be built")
        trial = git("commit-tree", tree.stdout.strip(), "-p", head, "-m",
                    f"mbs308 trial commit object (never referenced) {secrets.token_hex(8)}")
        if trial.returncode:
            raise Refusal("SEAL_PRECONDITION", "a commit object cannot be created with the current configuration")
    if git("rev-parse", "-q", "--verify", QUALIFIED_BRANCH).returncode:
        raise Refusal("SEAL_PRECONDITION", "the branch ref does not resolve")
    if not os.access(git_dir(), os.W_OK):
        raise Refusal("SEAL_PRECONDITION", "the git dir is not writable (fallback evidence channel)")
    evd = REPO / NS_REL / "evidence"
    parent = evd if os.path.lexists(evd) else REPO / NS_REL
    if not os.access(parent, os.W_OK | os.X_OK):
        raise Refusal("SEAL_PRECONDITION", "the worktree copy's parent directory is not writable")
    return {"branch_head": head}


# ------------------------------------------------------------------ platform (RC2) and host contract (section 6, GC-10)
def platform_readings() -> dict:
    exe = os.path.realpath(sys.executable)
    lib = PLATFORM_PINS["libpython"]

    def fsha(p):
        try:
            return hashlib.sha256(Path(p).read_bytes()).hexdigest()
        except OSError:
            return None
    build = HOST._run(["/usr/bin/sw_vers", "-buildVersion"])
    arch = HOST._run(["/usr/bin/uname", "-m"])
    return {"python_executable": exe, "python_sha256": fsha(exe), "libpython": lib, "libpython_sha256": fsha(lib),
            "python_version": sys.version.split()[0], "python_sys_version": sys.version,
            "os_build": (build or "").strip() or None,
            "arch": (arch or "").strip() or None}


def check_platform() -> dict:
    got = platform_readings()
    bad = [k for k, v in PLATFORM_PINS.items() if got.get(k) != v]
    if bad:
        raise Refusal("PLATFORM_PIN_MISMATCH", ", ".join(bad))
    return got


def check_launched() -> dict:
    """execute / resume run only as the launchd job the launcher installed (section 5)."""
    rec = HOST.launched_by_launchd()
    if not rec["pass"]:
        raise Refusal("NOT_LAUNCHED_BY_LAUNCHER", "execute / resume must run as the mbs308_launch launchd job")
    return rec


# GC-10 host headroom and exclusivity (recorded; each refuses start). Provisional values; each is frozen at the freeze
# as the output of its rule in CONSTANTS_RATIFICATION_MBS308 (research 3c2a7854; protocol section 8): FREE_MEM_MIN by
# R-FREE, EXCL_CPU_PCT by R-EXCL-PCT, EXCL_ALLOW by R-ALLOW.
FREE_MEM_MIN_BYTES = 2 * 1024 ** 3
EXCL_CPU_PCT = 25.0
# CONSTANTS_RATIFICATION_MBS308 item 16 (provisional; R-ALLOW decides the frozen list at the freeze): the current
# 39 names plus the four Apple OS daemons of its H3 readings (each under a SIP-protected OS path)
EXCL_ALLOW = frozenset({"kernel_task", "WindowServer", "launchd", "logd", "mds", "mds_stores", "mdworker",
                        "mdworker_shared", "coreaudiod", "powerd", "hidd", "bluetoothd", "configd", "syslogd",
                        "opendirectoryd", "distnoted", "cfprefsd", "trustd", "securityd", "loginwindow", "Dock",
                        "SystemUIServer", "ControlCenter", "Finder", "backupd", "spindump", "ReportCrash",
                        "sysmond", "thermalmonitord", "watchdogd", "runningboardd", "symptomsd", "remoted",
                        "bird", "fseventsd", "diskarbitrationd", "coreservicesd", "notifyd", "UserEventAgent",
                        "spotlightknowledged.updater", "cloudd", "BackgroundShortcutRunner", "modelcatalogd"})


def free_memory_bytes(text: str | None = None) -> int | None:
    text = HOST._run(["/usr/bin/vm_stat"]) if text is None else text
    if not text:
        return None
    import re
    m = re.search(r"page size of (\d+) bytes", text)
    if not m:
        return None
    page = int(m.group(1))
    got = {k: int(v) for k, v in re.findall(r"^Pages (free|inactive|speculative|purgeable):\s+(\d+)\.", text, re.M)}
    if set(got) != {"free", "inactive", "speculative", "purgeable"}:
        return None
    return sum(got.values()) * page


def busy_processes(text: str | None = None) -> list:
    """Processes above EXCL_CPU_PCT (ps %cpu) other than this process tree and the documented OS/UI allow-list."""
    text = HOST._run(["/bin/ps", "-A", "-o", "pid=,ppid=,pcpu=,comm="]) if text is None else text
    mine = {os.getpid(), os.getppid()}
    out = []
    for ln in (text or "").splitlines():
        parts = ln.split(None, 3)
        if len(parts) != 4:
            continue
        pid, ppid, pcpu, comm = parts
        try:
            pid, ppid, pcpu = int(pid), int(ppid), float(pcpu)
        except ValueError:
            continue
        if pid in mine or ppid == os.getpid() or pcpu <= EXCL_CPU_PCT:
            continue
        name = comm.rsplit("/", 1)[-1]
        if name in EXCL_ALLOW:
            continue
        out.append({"pid": pid, "comm": name, "pcpu": pcpu})
    return out


def host_preflight(launched: dict | None, texts: dict | None = None) -> dict:
    """Section 6 gates + GC-10 headroom and exclusivity. Every gate refuses start (before the marker). `texts`: planted
    readings for the tests ({"host": ..., "su": ..., "vm_stat": ..., "ps": ...}); production passes none."""
    t = texts or {}
    pid_rec, pid_state = STATE.read_pidfile(store())
    g = HOST.preflight_gates(REPO, other_job_running=pid_state == "LIVE", launched=launched, texts=t.get("host"),
                             su_texts=t.get("su"))
    fm = free_memory_bytes(t.get("vm_stat"))
    busy = busy_processes(t.get("ps"))
    g["gates"]["free_memory_ge_min"] = isinstance(fm, int) and fm >= FREE_MEM_MIN_BYTES
    g["gates"]["host_exclusive"] = not busy
    g["readings"].update({"free_memory_bytes": fm, "busy_processes": busy, "pidfile": pid_state})
    g["pass"] = all(g["gates"].values())
    if not g["pass"]:
        raise Refusal("HOST_PREFLIGHT", ", ".join(k for k, v in g["gates"].items() if not v))
    return g


# ------------------------------------------------------------------ bindings and governance state
def read_pinned(key: str) -> bytes:
    try:
        return CON.read_pinned(REPO, key)
    except CON.ConsumerRefusal as exc:
        raise Refusal(exc.code, str(exc))


def check_bindings(allow_uncommitted: bool = False) -> dict:
    shas = {}
    for key, (rel, pin, blob) in CON.PINS.items():
        shas[key] = sha(read_pinned(key))
        got = git("rev-parse", f"HEAD:{rel}").stdout.strip()
        if not got.startswith(blob):
            raise Refusal("BLOB_MISMATCH", rel)
        if git("hash-object", "--", rel).stdout.strip() != got:
            raise Refusal("WORKTREE_DIFFERS_FROM_COMMIT", rel)
    try:
        for key, pin in PIN.PINS.items():
            PIN.verified_bytes(REPO, pin, check_git=True)
            shas["module:" + key] = pin[1]
        if (REPO / PIN.INDEP_PIN[0]).exists():
            PIN.verified_bytes(REPO, PIN.INDEP_PIN, check_git=True, allow_uncommitted=allow_uncommitted)
            shas["module:mb_independent"] = PIN.INDEP_PIN[1] + ("" if PIN.INDEP_PIN[2] else " (UNCOMMITTED_DEV)")
        elif not allow_uncommitted:
            raise Refusal("F2_MISSING", "the independent reconstruction (stream F2) is required for execution")
        if not (REPO / PIN.TUPLE_PIN[0]).exists():
            raise Refusal("F3_MISSING", "the independent tuple (stream F3) is required")
        PIN.verified_bytes(REPO, PIN.TUPLE_PIN, check_git=True)
        shas["module:tuple_independent"] = PIN.TUPLE_PIN[1]
    except PIN.PinError as exc:
        raise Refusal("PIN_MISMATCH", str(exc))
    for commit, word in LINEAGE:
        if git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
            raise Refusal("LINEAGE", commit)
        if word not in git("log", "-1", "--format=%s", commit).stdout:
            raise Refusal("LINEAGE_ROLE", commit)
    shas["helpers"] = check_helpers()
    return shas


def check_governance_state() -> dict:
    names = git("ls-tree", "-r", "--name-only", "HEAD").stdout.split()
    if any(Path(n).name.startswith(R6_NAME) for n in names):
        raise Refusal("R6_EXISTS")
    if git("log", "--all", "--format=%H", "--", f"*{R6_NAME}*").stdout.strip():
        raise Refusal("R6_IN_HISTORY")
    r5 = json.loads(read_pinned("coverage_r5"))
    if r5.get("K5_COVERAGE_COMPLETE") is not False or r5.get("union_open_ranges") != [[306, 309]]:
        raise Refusal("R5_STATE", "r5 no longer lists exactly [306, 309] open")
    m5 = {c["cell"]: c["verdict"] for c in r5["per_m"]["5"]["cells"]}
    if any(m5.get(k) == "PASS" for k in (306, 307, 308, 309)):
        raise Refusal("R5_STATE", "a cell in 306-309 is PASS")
    return {"r6": "absent", "r5_union_open_ranges": r5["union_open_ranges"]}


# ------------------------------------------------------------------ pinned modules (main process)
def load_science(allow_uncommitted: bool, with_decoy_gen: bool = False) -> dict:
    """Every pinned module the evaluation needs, loaded from verified bytes with the guard bound."""
    c1b = PIN.load_c1b(REPO, GUARD)
    c2b = PIN.load_c2b(REPO, GUARD)
    S1, IND7 = PIN.load_rlr307(REPO)
    asm = PIN.load_assembly(REPO, GUARD, with_decoy_gen=with_decoy_gen)
    indep = PIN.load_indep(REPO, allow_uncommitted=allow_uncommitted)
    if indep is None and not allow_uncommitted:
        raise Refusal("F2_MISSING", "the independent reconstruction (stream F2) is required for execution")
    f3 = PIN.load_tuple_indep(REPO, GUARD)
    if f3 is None:
        raise Refusal("F3_MISSING", "the independent tuple (stream F3, gate G-R3b) is required")
    asm["F3"] = f3
    if tuple(S1.LADDER) != S1M.LADDER_RLR:
        raise Refusal("RULES", "rlr307_stage1.LADDER differs from the frozen RLR ladder")
    cp = c1b["c1b_certpw"]
    kc = IND7.kappa_check(cp.KAPPA1, cp.KAPPA2)
    if not (kc["kappa1_ge_sqrt_2_over_pi"] and kc["kappa2_ge_4phi1"]):
        raise Refusal("KAPPA", "a certifier kappa is not a valid upper bound")
    return {"c1b": c1b, "c2b": c2b, "S1": S1, "IND7": IND7, "asm": asm, "indep": indep, "cp": cp,
            "kappa": (cp.KAPPA1, cp.KAPPA2), "kappa_check": kc,
            "identity": {"c1b": c1b["_identity"], "c2b": c2b["_identity"], "assembly": asm["_identity"],
                         "F3": f3._mb308_identity,
                         "F2": None if indep is None else {"revision": getattr(indep, "MODULE_REVISION", None),
                                                           "committed": PIN.INDEP_PIN[2] is not None}}}


def target_geometry(con: dict, sci: dict) -> list:
    """D1/D2 for cell 308, cross-checked against cells.json, REGISTRY_C2 (interval, sub-block count), the guard's
    CELL308 and the guard's own rule."""
    lo, hi, e0, rho = CON.cover_interval(con, TARGET_CELL)
    reg = [b for b in json.loads(CON.read_pinned(REPO, "registry_c2"))["blocks"] if b["cell"] == TARGET_CELL]
    if len(reg) != 1 or (F(reg[0]["e_lo"]), F(reg[0]["e_hi"])) != (lo, hi):
        raise Refusal("BLOCK_GEOMETRY", "cover interval differs from REGISTRY_C2's")
    if (lo, hi) != GUARD.CELL308 or e0 != (lo + hi) / 2 or rho != (hi - lo) / 2:
        raise Refusal("BLOCK_GEOMETRY", "cover interval differs from the guard's")
    blocks = S1M.plan(sci["S1"], GUARD, lo, hi)
    if len(blocks) != reg[0]["sub_blocks"]:
        raise Refusal("BLOCK_GEOMETRY", "sub-block count differs from REGISTRY_C2's")
    return blocks


def admitted_pairs(blocks: list, x_lo, x_hi, e0) -> list:
    s = {(F(x_lo), F(x_hi)), (F(x_lo), F(x_lo)), (F(x_hi), F(x_hi)), (F(e0), F(e0))}
    for b in blocks:
        s |= {tuple(b["tile"]), tuple(b["hull"]), (b["b"], b["b"])}
    return sorted((fs(a), fs(c)) for a, c in s)


# ------------------------------------------------------------------ Stage 1: worker pool (spawned processes)
_W: dict = {}


def check_cpu_caps() -> dict:
    """The effective RLIMIT_CPU must allow every declared per-job cap (REVIEW_A0 C3); recorded in the result."""
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    need = max(c for caps in RUNG_CPU_CAP_S.values() for c in caps.values())
    inf = resource.RLIM_INFINITY
    if (hard != inf and hard < need) or (soft != inf and soft < need):
        raise Refusal("CPU_CAP", "an outer RLIMIT_CPU is below a declared per-job cap")
    return {"declared_per_job_s": {k: {str(r): c for r, c in v.items()} for k, v in RUNG_CPU_CAP_S.items()},
            "parent_rlimit_cpu": ["unlimited" if soft == inf else soft, "unlimited" if hard == inf else hard]}


def _set_job_cap(kind: str, rung: int) -> dict:
    cap = RUNG_CPU_CAP_S[kind][rung]
    ru = resource.getrusage(resource.RUSAGE_SELF)
    used = int(ru.ru_utime + ru.ru_stime) + 1
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    want = used + cap
    if hard != resource.RLIM_INFINITY and hard < want:
        raise S1M.InfrastructureFailure("CPU_CAP_EFFECTIVE_BELOW_DECLARED")
    resource.setrlimit(resource.RLIMIT_CPU, (want, want + 30 if hard == resource.RLIM_INFINITY else hard))
    got = resource.getrlimit(resource.RLIMIT_CPU)[0] - used
    if got != cap:
        raise S1M.InfrastructureFailure("CPU_CAP_EFFECTIVE_DIFFERS_FROM_DECLARED")
    return {"declared_s": cap, "effective_s": got}


def _worker_init(mode: str, repo: str, grant_commit: str, pairs: list, driver_sha: str, latent: str,
                 allow_uncommitted: bool) -> None:
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, signal.SIG_IGN)
    if sha(HERE.read_bytes()) != driver_sha:
        raise RuntimeError("worker: driver bytes differ from the parent's")
    check_helpers()
    c1b = PIN.load_c1b(Path(repo), GUARD)
    c2b = PIN.load_c2b(Path(repo), GUARD)
    S1, _ = PIN.load_rlr307(Path(repo))
    vf = PIN.load_verifier(Path(repo), GUARD)
    if mode == "target":
        GUARD.arm_target(repo, grant_commit, [(F(a), F(b)) for a, b in pairs])
    elif mode != "decoy":
        raise RuntimeError(f"worker: unknown mode {mode}")
    _W.clear()
    _W.update({"c1b": c1b, "c2b": c2b, "S1": S1, "vf": vf, "guard": GUARD, "latent": latent,
               "set_flags": PIN.set_c1b_flags, "mode": mode})


def _worker_job(kind: str, block: dict, rung: int, payload=None) -> dict:
    b = {"index": block["index"], "tile": tuple(F(x) for x in block["tile"]),
         "hull": tuple(F(x) for x in block["hull"]), "b": F(block["b"])}
    cap = _set_job_cap(kind, rung)
    out = S1M.run_job(_W, kind, b, rung, payload)
    out["cpu_cap"] = cap
    return out


def _ser_block(b: dict) -> dict:
    return {"index": b["index"], "tile": [fs(x) for x in b["tile"]], "hull": [fs(x) for x in b["hull"]], "b": fs(b["b"])}


def stage1(mode: str, blocks: list, grant_commit: str, own_sha: str, sci: dict, ladder: dict, pairs: list,
           workers: int = WORKERS, which=None, allow_uncommitted: bool = False) -> dict:
    """S1a-S1d. Raises on any infrastructure failure, IndependentCheckFailed on a verifier refutation or a ladder
    disagreement, Inconsistent on L > U."""
    latent = S1M.FORMAL_LATENT if mode == "target" else "decoy certificate (never juxtapose with any tail number)"
    ser = {b["index"]: _ser_block(b) for b in blocks}
    todo = S1M.jobs(blocks, ladder, which)
    results = {}
    ex = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"),
                             max_tasks_per_child=1, initializer=_worker_init,
                             initargs=(mode, str(REPO), grant_commit, pairs, own_sha, latent, allow_uncommitted))
    try:
        pending = {ex.submit(_worker_job, k, ser[i], r): (k, i, r) for k, i, r in todo}
        while pending:
            done, _ = wait(list(pending), return_when=FIRST_COMPLETED)
            for fut in done:
                key = pending.pop(fut)
                res = fut.result()                                   # a worker failure propagates
                results[key] = res
                if key[0] == "C1B" and res.get("status") == "CERTIFIED" and res.get("cert") and \
                        key[2] <= S1M.C1B_VERIFY_MAX_D:
                    vkey = ("VER", key[1], key[2])
                    pending[ex.submit(_worker_job, "VER", ser[key[1]], key[2], res["cert"])] = vkey
    finally:
        procs = list(getattr(ex, "_processes", {}).values())
        ex.shutdown(wait=False, cancel_futures=True)
        for p in procs:
            if p.is_alive():
                p.terminate()
    S1, IND7, cp, indep = sci["S1"], sci["IND7"], sci["cp"], sci["indep"]
    out_blocks, U_list, rlr_recs, n_ver = [], [], [], 0
    for b in blocks:
        i = b["index"]
        rl = [results[("RLR", i, d)] for d in ladder["RLR"] if ("RLR", i, d) in results]
        c1 = [results[("C1B", i, d)] for d in ladder["C1B"] if ("C1B", i, d) in results]
        c2 = [results[("C2B", i, n)] for n in ladder["C2B"] if ("C2B", i, n) in results]
        vers = {d: results[("VER", i, d)]["verification"] for d in ladder["C1B"] if ("VER", i, d) in results}
        n_ver += len(vers)
        run = bool(rl or c1 or c2)
        try:
            brec = S1M.rlr_block(S1, IND7, cp, rl, sci["kappa"]) if rl else None
        except ValueError as exc:
            raise IndependentCheckFailed(f"block {i}: {exc}")
        if brec is not None:
            brec = dict(brec, _kind="RLR_BLOCK", _hull=[fs(b["hull"][0]), fs(b["hull"][1])])
        if indep is not None and rl and not SUP.f2_ladder_check(indep, [r["record"] for r in rl], brec):
            raise IndependentCheckFailed(f"block {i}: Lemma Lad differs from stream F2")
        pw = S1M.pointwise(c2, c1, vers) if run else {"status": "NOT_RUN", "U": None, "L": None}
        if pw["status"] == "INCONSISTENT":
            raise Inconsistent(f"pointwise drift of block {i}: a verifier refutation or a cross-implementation alarm")
        U_list.append(None if pw.get("U") is None else F(pw["U"]))
        rlr_recs.append(brec)
        strip = lambda r: {k: v for k, v in r.items() if k != "cert"}  # noqa: E731
        out_blocks.append({"index": i, "tile": ser[i]["tile"], "hull": ser[i]["hull"], "b": ser[i]["b"], "run": run,
                           "rlr_rungs": rl, "rlr_block": None if brec is None else jsonable(brec),
                           "c2b_rungs": c2, "c1b_rungs": [strip(r) for r in c1],
                           "c1b_certificates": {r["rung"]: r.get("cert") for r in c1 if r.get("cert")},
                           "verifications": vers, "pointwise": jsonable(pw)})
    return {"mode": mode, "ladder": {k: list(v) for k, v in ladder.items()}, "workers": workers,
            "blocks": out_blocks, "U_list": U_list, "rlr_recs": rlr_recs, "n_verifications": n_ver,
            "verifiers": {"C2B": "vd_pl.verify_pl (pinned)", "C1B": f"vd_verify.verify for d <= {S1M.C1B_VERIFY_MAX_D} "
                          "only; higher degrees NOT_INDEPENDENTLY_VERIFIED", "budget": jsonable(S1M.VERIFY_BUDGET)}}


def public_stage1(st1: dict) -> dict:
    return {k: v for k, v in st1.items() if k not in ("U_list", "rlr_recs")} | {
        "U": [None if u is None else fs(u) for u in st1["U_list"]]}


# ------------------------------------------------------------------ composition, Stage 2, decision
def compose_and_consume(sci: dict, con: dict | None, blocks: list, st1: dict, S_I1: dict, reg_sets: list,
                        bundle: dict) -> tuple:
    try:
        sup = SUP.compose(blocks, st1["U_list"], st1["rlr_recs"], S_I1, reg_sets, con, sci["IND7"], sci["cp"],
                          sci["indep"], GUARD)
    except SUP.IndependentCheckFailed as exc:
        raise IndependentCheckFailed(str(exc))
    triples = [(b["tile"][0], b["tile"][1], sup["blocks"][k]["_S"]) for k, b in enumerate(blocks)]
    try:
        st2 = CON.stage2(sci["asm"], GUARD, bundle, triples, sci["indep"])
    except CON.IndependentCheckFailed as exc:
        raise IndependentCheckFailed(str(exc))
    return jsonable(sup), st2


def decide(st2: dict) -> dict:
    """The frozen mechanical outcome (design section 5.4); Gamma = 0 does NOT close."""
    if st2["Gamma_dec_lt_0"]:
        return {"mechanical_outcome": "CELL308_CLOSED_UNDER_MB", "reason": "Gamma_dec < 0 (exact)"}
    return {"mechanical_outcome": "CELL308_NOT_CLOSED_UNDER_MB", "reason": "Gamma_dec >= 0 (exact)"}


def evaluate_target(con: dict, prep: dict) -> dict:
    """The ONE scientific evaluation (after the marker)."""
    GUARD.arm_target(str(REPO), prep["grant_commit"], [(F(a), F(b)) for a, b in prep["pairs"]])
    st1 = stage1("target", prep["blocks"], prep["grant_commit"], prep["own_sha"], prep["sci"], prep["ladder"],
                 prep["pairs"])
    sup, st2 = compose_and_consume(prep["sci"], con, prep["blocks"], st1, prep["A_I1"], prep["reg_sets"],
                                   prep["bundle"])
    return {"cell": TARGET_CELL, "stage1": public_stage1(st1), "supply": sup, "stage2": st2, "decision": decide(st2)}


# ------------------------------------------------------------------ the grant (derived chain)
def check_grant(own_sha: str) -> dict:
    head = git("rev-parse", "HEAD").stdout.strip()
    if not os.path.lexists(REPO / GRANT_REL):
        raise Refusal("GRANT_MISSING")
    if os.path.islink(REPO / GRANT_REL):
        raise Refusal("GRANT_INVALID", "the grant is a symlink")
    if git("log", "-1", "--format=%H", "--", GRANT_REL).stdout.strip() != head:
        raise Refusal("GRANT_INVALID", "HEAD is not the grant commit")
    if git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.split() != [GRANT_REL]:
        raise Refusal("GRANT_INVALID", "the grant commit changes more than the grant")
    g = json.loads((REPO / GRANT_REL).read_bytes())
    if g.get("schema") != GRANT_SCHEMA or g.get("exactly_once") is not True \
            or g.get("cell") != TARGET_CELL or g.get("route") != "MB-S" or g.get("closure_only") is not True:
        raise Refusal("GRANT_INVALID", "schema / cell / route / scope")
    # governance S1: the grant carries, verbatim, the user's explicit ruling authorising a second cell-308 target
    # evaluation and re-affirming the C4 terms (U1-U8), bound by its sha256
    ur = g.get("user_ruling_s1")
    if not isinstance(ur, dict) or not isinstance(ur.get("verbatim"), str) or not ur["verbatim"].strip() or \
            ur.get("sha256") != sha(ur["verbatim"].encode()) or ur.get("reaffirms_c4") is not True:
        raise Refusal("GRANT_INVALID", "the grant does not carry the user's S1 ruling verbatim (governance S1)")
    if g.get("driver_sha256") != own_sha:
        raise Refusal("GRANT_INVALID", "driver bytes differ from the granted driver")
    fz = freeze_commit()
    review_c = git("rev-parse", "HEAD^").stdout.strip()
    qual_c = git("rev-parse", "HEAD^^").stdout.strip()
    if (g.get("freeze_commit"), g.get("qualification_commit"), g.get("qualification_review_commit")) != \
            (fz, qual_c, review_c) or git("rev-parse", "HEAD^^^").stdout.strip() != fz:
        raise Refusal("GRANT_INVALID", "the chain must be freeze -> qualification -> review -> grant, as named")
    if git("diff-tree", "--no-commit-id", "--name-only", "-r", review_c).stdout.split() != [QREVIEW_REL]:
        raise Refusal("GRANT_INVALID", "the review commit changes more than the review")
    qfiles = git("diff-tree", "--no-commit-id", "--name-only", "-r", qual_c).stdout.split()
    if not qfiles or any(not f.startswith(QUAL_DIR_REL) for f in qfiles) or QUAL_REL not in qfiles:
        raise Refusal("GRANT_INVALID", "the qualification commit is not qualification evidence only")
    q = json.loads(git("show", f"{qual_c}:{QUAL_REL}").stdout)
    if q.get("pass") is not True or q.get("review_mode") is not False or q.get("freeze_commit") != fz:
        raise Refusal("GRANT_INVALID", "the qualification report is not an official PASS at the freeze commit")
    if not verdict_ok((REPO / QREVIEW_REL).read_text(), "QUALIFICATION_ACCEPTED"):
        raise Refusal("REVIEW_VERDICT", "qualification review is not QUALIFICATION_ACCEPTED")
    if g.get("input_manifest_sha256") != sha((REPO / MANIFEST_REL).read_bytes()):
        raise Refusal("GRANT_INVALID", "the grant does not bind the frozen input manifest")
    return {"grant_commit": head, "grant_sha256": sha((REPO / GRANT_REL).read_bytes()), "freeze_commit": fz,
            "qualification_commit": qual_c, "qualification_review_commit": review_c}


# ------------------------------------------------------------------ persistence, seal and materialization
def serialize(obj: dict) -> bytes:
    """MB r1's layout; the self sha256 is re-verifiable from the bytes (mbs308_state.serialize)."""
    return STATE.serialize(obj)


def persist_pending(data: bytes, stale: str | None = None) -> str:
    """Step 7: durable blob (`-c core.fsync=loose-object,reference`), its id verified, then the pending ref by CAS from
    zero -- or from a STALE value (a pending ref whose blob is missing or fails verification; classified, recorded)."""
    st = store()
    blob = st.put_blob(data)
    cur = st.rev(PENDING_REF)
    if cur == blob:
        return blob
    if cur and cur != stale:
        raise OSError("the pending-result ref names other bytes")
    if not st.cas_ref(PENDING_REF, blob, cur or None):
        raise OSError("the pending-result ref could not be created")
    return blob


def seal_blob(blob: str, message: str) -> str:
    last = None
    for delay in (0.0, *SEAL_RETRY_DELAYS):
        time.sleep(delay)
        head = git("rev-parse", "HEAD").stdout.strip()
        entry = git("ls-tree", head, "--", RESULT_REL).stdout.split()
        if entry:
            if entry[:3] != ["100644", "blob", blob]:
                raise OSError("HEAD already holds a different result entry")
            return head
        with tempfile.TemporaryDirectory(prefix="mbs308seal") as td:
            idx = {"GIT_INDEX_FILE": str(Path(td) / "index")}
            msgf = Path(td) / "msg"
            msgf.write_text(message)
            steps = [git("read-tree", head, env_extra=idx),
                     git("update-index", "--add", "--cacheinfo", f"100644,{blob},{RESULT_REL}", env_extra=idx)]
            tree = git("write-tree", env_extra=idx)
            if any(s.returncode for s in steps) or tree.returncode:
                last = "index"
                continue
            commit = store().git("commit-tree", tree.stdout.strip(), "-p", head, "-F", str(msgf), write=True)
            if commit.returncode:
                last = "commit-tree"
                continue
            cid = commit.stdout.strip()
            STATE.fault("F11")
            if not store().cas_ref(QUALIFIED_BRANCH, cid, head):
                last = "update-ref"
                continue
            entry = git("ls-tree", cid, "--", RESULT_REL).stdout.split()
            if entry[:3] != ["100644", "blob", blob]:
                raise OSError("the sealed entry is not the persisted blob")
            git("update-index", "--add", "--cacheinfo", f"100644,{blob},{RESULT_REL}")
            return cid
    raise OSError(f"seal failed at {last}")


def materialize(blob: str) -> None:
    data = subprocess.run(["/usr/bin/git", "-C", str(REPO), "cat-file", "blob", blob], capture_output=True,
                          env=dict(ENV), stdin=subprocess.DEVNULL).stdout
    if git_blob_id(data) != blob:
        raise OSError("the object store returned other bytes")
    fds = [os.open(str(REPO), os.O_RDONLY | os.O_DIRECTORY)]
    try:
        for part in (NS_REL + "/evidence/execution").split("/"):
            try:
                os.mkdir(part, 0o755, dir_fd=fds[-1])
            except FileExistsError:
                pass
            fds.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fds[-1]))
        fd = os.open(RESULT_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=fds[-1])
        try:
            STATE._write_all(fd, data)
            STATE.fsync_file(fd)
        finally:
            os.close(fd)
        STATE.fsync_dir(fds[-1])
        rfd = os.open(RESULT_NAME, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fds[-1])
        try:
            st = os.fstat(rfd)
            back = b""
            while chunk := os.read(rfd, 1 << 20):
                back += chunk
        finally:
            os.close(rfd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or back != data:
            raise OSError("the materialized copy is not the sealed bytes")
    finally:
        for fd in reversed(fds):
            os.close(fd)


def materialized_ok(blob: str) -> bool | None:
    """True: the worktree copy is the sealed bytes; False: another object is there; None: nothing there."""
    p = REPO / RESULT_REL
    if not os.path.lexists(p):
        return None
    st = os.lstat(p)
    if not stat.S_ISREG(st.st_mode):
        return False
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        back = b""
        while chunk := os.read(fd, 1 << 20):
            back += chunk
    finally:
        os.close(fd)
    return git_blob_id(back) == blob


def seal_message(status: str) -> str:
    return (f"p5y: K5 cell-308 MB-S r1 — SEAL of the one cell-308 MB-S evaluation ({status})\n\n"
            f"Committed by {NS_REL}/code/mbs308_driver.py from durable bytes (spool + object store + pending ref), "
            "not from a worktree file; the result was not inspected before this commit.\n\n"
            "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")


def fallback_bytes(common_min: dict, stage: str, exc: BaseException) -> bytes:
    rec = {"schema": SCHEMA, "status": "POST_MARKER_RECORDING_FAILED", "stage": stage, "complete": True,
           "error": f"{type(exc).__name__}: {exc}"[:500], "target_evaluations": 1,
           "mechanical_outcome": "CELL308_EXECUTION_INDETERMINATE", **common_min}
    try:
        return serialize(rec)
    except BaseException:
        pass
    try:
        return serialize({k: rec[k] for k in ("schema", "status", "stage", "complete", "target_evaluations",
                                              "mechanical_outcome", "cell", "grant", "driver_sha256") if k in rec})
    except BaseException:
        return (json.dumps({"status": "POST_MARKER_RECORDING_FAILED", "stage": stage,
                            "mechanical_outcome": "CELL308_EXECUTION_INDETERMINATE"}) + "\n").encode()


def _eval_cap(*_):
    raise TimeoutError(f"evaluation exceeded {EVAL_CAP_S} s")


def failure_kind(exc: BaseException) -> str:
    if isinstance(exc, (IndependentCheckFailed, SUP.IndependentCheckFailed, CON.IndependentCheckFailed)):
        return "INDEPENDENT_CHECK_FAILED"
    if isinstance(exc, Inconsistent):
        return "INCONSISTENT"
    if isinstance(exc, CON.Stop) and exc.code == "C6_EMPTY_BAND":
        return "C6_REFUSED"
    return "TARGET_EVALUATION_FAILED"


def persist_and_seal(data: bytes, status: str, jr: STATE.Journal | None, stale_pending: str | None = None) -> int:
    """Section 3 steps 3-9 from the in-memory bytes. Never raises (except LostOwnership); every outcome is an exit code.
    Fault points F4 (before the result write) ... F12 (after the seal)."""
    st = store()
    STATE.fault("F4")
    spool_ok = False
    try:
        st.spool_write_result(data)
        spool_ok = True
    except BaseException:                                              # noqa: BLE001 (the object store follows)
        pass
    STATE.fault("F8")
    if spool_ok and jr is not None:
        _journal(jr, durable=True, state="RESULT_DURABLE", result_sha256=STATE.sha(data))
    STATE.fault("F9")
    try:
        blob = persist_pending(data, stale_pending)
    except BaseException:                                              # noqa: BLE001
        if spool_ok:
            print("MBS308 UNSEALED: the result is durable in the spool; run `recover`. NEVER run execute again.")
            return 4
        print("MBS308 NOTHING DURABLE: the marker exists; run `recover` (it resumes). NEVER run execute again.")
        return 6
    if jr is not None:
        _journal(jr, durable=True, state="PENDING_RESULT", result_blob=blob)
    STATE.fault("F10")
    try:
        cid = seal_blob(blob, seal_message(status))
    except BaseException:                                              # noqa: BLE001
        print("MBS308 UNSEALED: evidence persisted (pending ref); run `recover`. NEVER run execute again.")
        return 4
    STATE.fault("F12")
    if jr is not None:
        _journal(jr, durable=True, state="SEALED" if status == STATE.TARGET_EVALUATED else "INDETERMINATE_SEALED",
                 seal_commit=cid)
    try:
        materialize(blob)
    except BaseException:                                              # noqa: BLE001
        print(f"MBS308 SEALED {cid} (status {status}); worktree copy NOT materialized: run `recover`.")
        return 7
    print(f"MBS308 SEALED {cid} (status {status}; result not printed)")
    return 0 if status == STATE.TARGET_EVALUATED else (3 if status == "CONTROL_FAILED" else 5)


JOURNAL_FAILURES: list = []        # value-free, in memory: {utc, state, error, durable}


def _journal(jr: STATE.Journal, durable: bool = False, **changes) -> None:
    """A journal advance after the marker. Before any durable artifact exists, a genuine CAS conflict means another
    attempt owns the run (stop, write nothing). R1 (ii): once the durable artifacts exist (`durable`: the spool result,
    the pending ref, the seal), a failed advance -- a conflict or an infrastructure failure -- never stops the seal:
    the artifacts decide; the failure is recorded. Other failures are always recorded and ignored."""
    try:
        jr.advance(**changes)
    except STATE.JournalConflict as exc:
        JOURNAL_FAILURES.append({"utc": utc(), "state": changes.get("state"), "error": exc.code, "durable": durable})
        if not durable:
            raise STATE.LostOwnership()
    except Exception as exc:                                           # noqa: BLE001
        JOURNAL_FAILURES.append({"utc": utc(), "state": changes.get("state"), "durable": durable,
                                 "error": getattr(exc, "code", type(exc).__name__)})


def after_marker(con, prep, common: dict, evaluator, t0: float, jr: STATE.Journal, ctx: STATE.Ctx) -> int:
    """From here the target is consumed. Nothing escapes except LostOwnership; every outcome is evidence. EVAL_CAP runs
    per attempt on awake time (CLOCK_UPTIME_RAW); the Stage-1 checkpoints of `ctx` are written as jobs complete."""
    signal.signal(signal.SIGALRM, _eval_cap)
    signal.alarm(0)
    common_min = {"cell": TARGET_CELL, "grant": common.get("grant"), "driver_sha256": common.get("driver_sha256"),
                  "consumed_ref": CONSUMED_REF}
    cap = STATE.AwakeCap(EVAL_CAP_S).start()
    try:
        try:
            t_eval = time.time()
            STATE.CK = ctx
            try:
                tgt = evaluator(con, prep)
            finally:
                STATE.CK = None
                cap_rec = cap.stop()
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
            status = "TARGET_EVALUATED"
        except STATE.LostOwnership:
            raise
        except BaseException as exc:
            cap_rec = cap.stop()
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
            kind = failure_kind(exc)
            tgt, status = {"error": f"{type(exc).__name__}: {exc}"[:800], "failure_kind": kind}, kind
        usage = resource.getrusage(resource.RUSAGE_SELF)
        cusage = resource.getrusage(resource.RUSAGE_CHILDREN)
        common.update({"status": status, "complete": True, "target_evaluated": status == "TARGET_EVALUATED",
                       "target_evaluations": 1, "consumed_ref": CONSUMED_REF, "target": tgt,
                       "mechanical_outcome": (tgt.get("decision", {}).get("mechanical_outcome")
                                              if status == "TARGET_EVALUATED" else "CELL308_EXECUTION_INDETERMINATE"),
                       "finished_utc": utc(), "wall_seconds": round(time.time() - t0, 3),
                       "evaluation_wall_seconds": round(time.time() - t_eval, 3),
                       "peak_rss_bytes": usage.ru_maxrss,
                       "cpu_seconds_parent": round(usage.ru_utime + usage.ru_stime, 3),
                       "cpu_seconds_workers": round(cusage.ru_utime + cusage.ru_stime, 3)})
        common.setdefault("lifecycle", {}).update({"attempt": jr.rec.get("attempt"), "stage1_context": ctx.summary(),
                                                   "eval_cap": cap_rec})
        close_host(common)
        data = serialize(common)
    except STATE.LostOwnership:
        raise
    except BaseException as exc:
        status, data = "POST_MARKER_RECORDING_FAILED", fallback_bytes(common_min, "record", exc)
    return persist_and_seal(data, status, jr)


def keep_awake() -> dict:
    """Environmental only: a SUPERVISED `caffeinate -i -m -s -w <pid>` (re-spawned whenever it dies; every death and
    re-spawn is recorded durably in the spool's host log and in the sealed record)."""
    st = store()

    def sink(ev):
        try:
            st.host_log({"source": "caffeinate_supervisor", **ev})
        except Exception:                                              # noqa: BLE001
            pass
    sup = HOST.CaffeinateSupervisor(sink=sink).start()
    _SUP["sup"] = sup
    return {"caffeinate_supervisor": True, "caffeinate_flags": " ".join(HOST.CAFFEINATE_FLAGS)}


_SUP: dict = {}


def require_ac() -> str:
    """Freeze r3 (protocol section 14): execute and preflight refuse, before the marker, unless on AC power."""
    try:
        return HOST.require_ac()
    except HOST.HostRefusal as exc:
        raise Refusal(exc.code, str(exc))


def close_host(common: dict) -> None:
    """Replace the live host record (start snapshot + sampler) by its closed provenance, with the caffeinate supervisor's
    record and the durable host log. Never raises."""
    h = common.pop("_host", None)
    try:
        sup = _SUP.get("sup")
        common.setdefault("lifecycle", {})["caffeinate"] = None if sup is None else sup.record()
        common["lifecycle"]["host_log"] = store().host_log_read()
        common["lifecycle"]["recover_actions"] = STATE.recover_actions_read(store())
        common["lifecycle"]["ref_write_failures"] = list(STATE.REF_WRITE_FAILURES)
        common["lifecycle"]["journal_failures"] = list(JOURNAL_FAILURES)
    except BaseException as exc:                                       # noqa: BLE001
        common.setdefault("lifecycle", {})["caffeinate"] = {"error": type(exc).__name__}
    if h is None:
        return
    try:
        common["host"] = HOST.provenance(h["start"], h["sampler"].stop(), HOST.snapshot())
    except BaseException as exc:                                       # noqa: BLE001
        common["host"] = {"error": type(exc).__name__}


# ------------------------------------------------------------------ controls and preparation (before the marker)
def controls(con: dict, sci: dict, k: int) -> dict:
    """C-A and C-B on cell k (305 rehearsal or 308 target control); equality only."""
    ca = CON.control_ca(con, k, sci["IND7"])
    bundle = CON.bundle_for(ca["_ci"], ca["_A"], ca["_committed"])
    cb = CON.control_cb(sci["asm"], GUARD, bundle, sci["indep"])
    return {"C_A": CON.public(ca), "C_B": cb, "pass": bool(ca["reproduces_C2_exactly"] and cb["reproduces_exactly"]),
            "_ca": ca, "_bundle": bundle}


def prepare_target(con: dict, ctl: dict, own_sha: str, grant: dict, sci: dict) -> dict:
    blocks = target_geometry(con, sci)
    lo, hi, e0, _ = CON.cover_interval(con, TARGET_CELL)
    pairs = admitted_pairs(blocks, lo, hi, e0)
    if frozenset((F(a), F(b)) for a, b in pairs) != GUARD.target_admitted_set():
        raise Refusal("BLOCK_GEOMETRY", "the admitted set differs from the guard's frozen set")
    return {"blocks": blocks, "pairs": pairs, "grant_commit": grant["grant_commit"], "own_sha": own_sha, "sci": sci,
            "ladder": {"RLR": S1M.LADDER_RLR, "C2B": S1M.LADDER_C2B_N, "C1B": S1M.LADDER_C1B_D},
            "A_I1": ctl["_ca"]["_A"], "reg_sets": CON.i1_sets(REPO, TARGET_CELL), "bundle": ctl["_bundle"],
            "kappa_check": sci["kappa_check"]}


def pre_marker_common(own_sha: str, *, resume: bool) -> tuple:
    """The checks every attempt makes before it may compute (execute: before the marker; resume: before the attempt
    counter moves). Returns (grant, common, con, sci, ctl, prep, awake). Refuses (Refusal) on any failure."""
    t_started = utc()
    ident = check_identity()
    mbr1 = check_mbr1_state()
    sci_mods = check_science_modules()
    grant = check_grant(own_sha)
    shas = check_bindings()
    state = check_governance_state()
    pre = check_seal_preconditions()
    pre["cpu_caps"] = check_cpu_caps()
    pre["host_power"] = require_ac()
    pre["platform"] = check_platform()
    pre["host_gates"] = host_preflight(check_launched())
    awake = keep_awake()
    awake["host_at_start"] = HOST.snapshot()
    try:
        con = load_consumer()
        sci = load_science(allow_uncommitted=False)
        ctl = control(con, sci, TARGET_CELL)
    except CON.ConsumerRefusal as exc:
        raise Refusal(exc.code, str(exc))
    except PIN.PinError as exc:
        raise Refusal("PIN_MISMATCH", str(exc))
    common = {"schema": SCHEMA, "cell": TARGET_CELL, "m": 5, "route": "MB-S", "scope": "CLOSURE_ONLY",
              "identity": ident, "grant": grant, "input_sha256": shas, "science_modules": sci_mods,
              "mbr1_state": mbr1, "governance_state_before": state, "seal_preconditions": pre,
              "driver_sha256": own_sha, "started_utc": t_started,
              "controls": {k: v for k, v in ctl.items() if not k.startswith("_")}, "python": sys.version.split()[0],
              "environment": awake}
    return grant, common, con, sci, ctl, awake


def run_execute(own_sha: str, prepare=None, evaluator=None) -> int:
    """The ONE evaluation. Injection points exist for the sandbox tests only; the CLI never passes them."""
    evaluator = evaluator or evaluate_target
    t0 = time.time()
    check_flags()
    check_identity()
    check_mbr1_state()
    intent = check_not_evaluated()
    check_result_paths()
    check_clean()
    st = store()
    lock = STATE.Lock(st)
    try:
        lock.acquire()
    except STATE.Locked as exc:
        raise Refusal(exc.code, str(exc))
    try:
        grant, common, con, sci, ctl, awake = pre_marker_common(own_sha, resume=False)
        if not ctl["pass"]:
            common.update({"status": "CONTROL_FAILED", "complete": True, "target_evaluated": False,
                           "target_evaluations": 0, "finished_utc": utc(), "wall_seconds": round(time.time() - t0, 3)})
            rc = persist_and_seal(serialize(common), "CONTROL_FAILED", None)
            print("MBS308 CONTROL_FAILED: the target was not evaluated")
            return rc if rc != 0 else 3
        try:
            prep = (prepare or prepare_target)(con, ctl, own_sha, grant, sci)
        except CON.ConsumerRefusal as exc:
            raise Refusal(exc.code, str(exc))
        common.update({"kappa_check": prep.get("kappa_check"), "admitted_pairs": prep.get("pairs"),
                       "blocks_planned": [_ser_block(b) for b in prep.get("blocks", [])]})
        check_result_paths()
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
            signal.signal(sig, signal.SIG_IGN)
        signal.alarm(0)
        host = {"start": HOST.snapshot(), "sampler": HOST.Sampler().start()}
        me = HOST.identity()
        jid, jrec = STATE.Journal.read(st) if intent["stale_intent_journal"] else ("", None)
        jr = STATE.Journal(st, jid or None, jrec)
        base = {"grant_commit": grant["grant_commit"], "driver_sha256": own_sha, "boot_uuid": me["boot_uuid"],
                "platform": common["seal_preconditions"]["platform"],
                "process": me, "attempt": 1, "history": [], "ckpt_tree": None, "n_ckpt": 0, "ckpt_failures": {}}
        try:
            jr.advance(state="ARMING", intent_utc=utc(), **base)          # durable intent BEFORE the marker
        except STATE.JournalConflict:
            host["sampler"].stop()
            raise Refusal("CONSUMED", "another process holds the journal")
        except STATE.RefWriteError as exc:                             # R1 (i): infrastructure, nothing consumed
            host["sampler"].stop()
            raise Refusal("JOURNAL_WRITE_FAILED", f"{exc} (nothing consumed; run `recover`)")
        STATE.fault("F1")
        why = ("CONSUMED", "the exactly-once marker could not be created: the target is never evaluated twice")
        try:
            marker_ok = st.cas_ref(CONSUMED_REF, grant["grant_commit"], None)
        except STATE.RefWriteError as exc:     # R1 (i): the marker is provably absent (re-read); nothing is consumed
            marker_ok, why = False, ("MARKER_WRITE_FAILED", f"{exc} (the marker is absent; nothing consumed; run "
                                                            "`recover`)")
        if not marker_ok:
            host["sampler"].stop()
            try:                        # this intent never owned the marker: it must not make the run look resumable
                jr.advance(state="ABORTED_INTENT", aborted_utc=utc())
            except Exception:                                          # noqa: BLE001
                pass
            raise Refusal(*why)
        STATE.fault("F2")
        common["_host"] = host
        _journal(jr, state="COMPUTING", marker_utc=utc(), attempt_started_utc=utc(), attempt_seq="SELF")
        STATE.write_pidfile(st, {"mode": "execute", "attempt": 1, "label": os.environ.get("MBS308_LAUNCH_LABEL")})
        ck = STATE.Checkpointer(st, jr, grant["grant_commit"], own_sha, attempt=1, attempt_seq=jr.rec.get("attempt_seq"),
                                platform=jr.rec.get("platform"), campaign=campaign())
        ctx = STATE.Ctx(checkpointer=ck, verified={}, mem_cap_bytes=MEM_CAP_BYTES, mem_poll_s=MEM_POLL_S)
        common["lifecycle"] = {"attempt": 1, "resumed": False}
        return after_marker(con, prep, common, evaluator, t0, jr, ctx)
    finally:
        lock.release()
        STATE.remove_own_pidfile(st)


def run_resume(own_sha: str, prepare=None, evaluator=None, boot_uuid: str | None = None) -> int:
    """CONSUMED_INTERRUPTED only (mandatory continuation, section 4): verified checkpoints are reused, exactly the jobs
    without one are recomputed, MB r1's stage1 aggregation runs over all records, then Stage 2, the decision and the
    section-3 persistence. One evaluation, not a rerun. The attempt counter moves by CAS (a concurrent resume loses)."""
    evaluator = evaluator or evaluate_target
    t0 = time.time()
    check_flags()
    check_identity()
    check_mbr1_state()
    st = store()
    lock = STATE.Lock(st)
    try:
        lock.acquire()
    except STATE.Locked as exc:
        raise Refusal(exc.code, str(exc))
    try:
        cls = STATE.classify(campaign(), boot_uuid=boot_uuid, platform=platform_readings())
        if cls["state"] != "CONSUMED_INTERRUPTED":
            raise Refusal("RESUME_REFUSED", f"state {cls['state']}")
        if cls.get("git_locks"):
            raise Refusal("GIT_LOCKED", f"campaign git lockfile(s) {', '.join(cls['git_locks'])}: run `recover`")
        grant, common, con, sci, ctl, awake = pre_marker_common(own_sha, resume=True)
        if cls["marker"] != grant["grant_commit"]:
            raise Refusal("RESUME_REFUSED", "the marker does not name the grant commit at HEAD")
        prep = None
        if ctl["pass"]:
            try:
                prep = (prepare or prepare_target)(con, ctl, own_sha, grant, sci)
            except CON.ConsumerRefusal as exc:
                raise Refusal(exc.code, str(exc))
            common.update({"kappa_check": prep.get("kappa_check"), "admitted_pairs": prep.get("pairs"),
                           "blocks_planned": [_ser_block(b) for b in prep.get("blocks", [])]})
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
            signal.signal(sig, signal.SIG_IGN)
        signal.alarm(0)
        jid, jrec = STATE.Journal.read(st)
        if jid != cls["journal"] or jrec is None:
            raise Refusal("RESUME_REFUSED", "the journal moved since classification")
        jr = STATE.Journal(st, jid, jrec)
        me = HOST.identity()
        attempt = int(jrec.get("attempt") or 1) + 1
        hist = list(jrec.get("history") or []) + [{"attempt": jrec.get("attempt"), "attempt_seq": jrec.get("attempt_seq"),
                                                   "process": jrec.get("process"),
                                                   "boot_uuid": jrec.get("boot_uuid"),
                                                   "started_utc": jrec.get("attempt_started_utc"),
                                                   "classified": cls["why"]}]
        try:
            jr.advance(state="COMPUTING", attempt=attempt, process=me, boot_uuid=me["boot_uuid"],
                       attempt_started_utc=utc(), history=hist, attempt_seq="SELF")
        except STATE.JournalConflict:
            raise Refusal("RESUME_REFUSED", "another resume advanced the journal first")
        except STATE.RefWriteError as exc:                             # R1 (i): the attempt counter did not move
            raise Refusal("JOURNAL_WRITE_FAILED", f"{exc} (the attempt was not consumed; run `recover`)")
        STATE.write_pidfile(st, {"mode": "resume", "attempt": attempt, "label": os.environ.get("MBS308_LAUNCH_LABEL")})
        common["_host"] = {"start": HOST.snapshot(), "sampler": HOST.Sampler().start()}
        common["lifecycle"] = {"attempt": attempt, "resumed": True, "classified": cls["why"]}
        if not ctl["pass"]:
            common.update({"status": "RESUME_CONTROL_FAILED", "complete": True, "target_evaluated": False,
                           "target_evaluations": 1, "consumed_ref": CONSUMED_REF,
                           "mechanical_outcome": "CELL308_EXECUTION_INDETERMINATE", "finished_utc": utc()})
            close_host(common)
            return persist_and_seal(serialize(common), "RESUME_CONTROL_FAILED", jr)
        for name in (STATE.RESULT_FILE, STATE.TMP_FILE):     # INTERRUPTED: any spool result file was rejected
            if st.spool_exists(name):
                st.quarantine(name, "resume")
        GUARD.arm_target(str(REPO), grant["grant_commit"], [(F(a), F(b)) for a, b in prep["pairs"]])
        ck = STATE.Checkpointer(st, jr, grant["grant_commit"], own_sha, attempt=attempt, attempt_seq=jr.rec["attempt_seq"],
                                platform=jr.rec.get("platform"), campaign=campaign())
        prev_attempts = {h["attempt"]: h.get("attempt_seq") for h in jr.rec.get("history") or []
                         if isinstance(h, dict) and isinstance(h.get("attempt"), int)}
        good, bad = ck.verified_records(attempts=prev_attempts)
        fails = dict(jr.rec.get("ckpt_failures") or {})
        for name in bad:
            fails[name] = int(fails.get(name, 0)) + 1
        for key in good:
            fails.pop(STATE.ckpt_name(key), None)
        _journal(jr, ckpt_failures=fails, ckpt_verified=len(good), ckpt_rejected=len(bad), ckpt_tree=ck.tree or None,
                 n_ckpt=len(ck.entries))
        common["lifecycle"].update({"checkpoints_verified": len(good), "checkpoints_rejected": sorted(bad)})
        if any(int(v) >= STATE.CKPT_FAIL_LIMIT for v in fails.values()):
            print("MBS308 RESUME STOPPED: a checkpoint failed verification twice in a row; the state is "
                  "CONSUMED_UNRECORDED (run recover: close-indeterminate)")
            return 6
        ctx = STATE.Ctx(checkpointer=ck, verified=good, mem_cap_bytes=MEM_CAP_BYTES, mem_poll_s=MEM_POLL_S)
        return after_marker(con, prep, common, evaluator, t0, jr, ctx)
    finally:
        lock.release()
        STATE.remove_own_pidfile(st)


def load_consumer():
    return CON.load_consumer(REPO)


def control(con, sci, k):
    return controls(con, sci, k)


def _read_verified_spool(cls: dict) -> bytes:
    st = store()
    data = st.spool_read(STATE.RESULT_FILE)
    rec, why = STATE.verify_result(data, grant=cls["marker"], driver_sha=cls.get("driver_sha256"))
    if rec is None:
        raise Refusal("SEAL_ONLY", f"the spool result does not verify ({why})")
    return data


def run_seal_only(boot_uuid: str | None = None) -> int:
    """Seal and/or materialize DURABLE evidence. Never computes, never evaluates, never touches the consumer."""
    check_flags()
    check_identity()
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, signal.SIG_IGN)
    st = store()
    lock = STATE.Lock(st)
    try:
        lock.acquire()
    except STATE.Locked as exc:
        raise Refusal(exc.code, str(exc))
    try:
        cls = STATE.classify(campaign(), boot_uuid=boot_uuid, platform=platform_readings())
        s = cls["state"]
        if cls.get("git_locks"):
            raise Refusal("GIT_LOCKED", f"campaign git lockfile(s) {', '.join(cls['git_locks'])}: run `recover`")
        jid, jrec = STATE.Journal.read(st)
        jr = STATE.Journal(st, jid, jrec) if jrec is not None else None
        if s == "RESULT_DURABLE_UNSEALED":
            data = _read_verified_spool(cls)
            status = json.loads(data)["status"]
            if jr is not None:
                _journal(jr, durable=True, state="RESULT_DURABLE", result_sha256=STATE.sha(data))
            return _pending_seal_materialize(data, status, jr, cls.get("stale_pending"))
        if s == "PENDING_RESULT":
            data = st.get_blob(cls["pending"])
            status = json.loads(data)["status"]
            return _pending_seal_materialize(data, status, jr, None)
        if s in ("SEALED", "INDETERMINATE"):
            blob = cls.get("sealed_blob")
            if not blob or blob == "NOT_A_BLOB":
                print(f"MBS308 {s}: nothing to materialize")
                return 0 if s == "SEALED" else 5
            want = "SEALED" if s == "SEALED" else "INDETERMINATE_SEALED"
            if jr is not None and jrec.get("state") != want:
                _journal(jr, durable=True, state=want, seal_commit=git("rev-parse", "HEAD").stdout.strip())
            m = materialized_ok(blob)
            if m is None:
                try:
                    materialize(blob)
                except (OSError, FileExistsError) as exc:
                    print(f"MBS308 {s}; materialization refused: {type(exc).__name__}")
                    return 7
            elif m is False:
                print(f"MBS308 {s}; the worktree object at the result path is NOT the sealed bytes")
                return 7
            print(f"MBS308 {s} (materialized; nothing computed)")
            return 0 if s == "SEALED" else 5
        if s == "NO_TARGET_CONSUMED":
            return _seal_control_failed()
        raise Refusal("SEAL_ONLY", f"state {s}: nothing durable to seal")
    finally:
        lock.release()


def _pending_seal_materialize(data: bytes, status: str, jr, stale: str | None) -> int:
    try:
        blob = persist_pending(data, stale)
    except OSError as exc:
        raise Refusal("UNSEALED", str(exc))
    if jr is not None:
        _journal(jr, durable=True, state="PENDING_RESULT", result_blob=blob)
    try:
        cid = seal_blob(blob, seal_message(f"{status}, sealed by seal-only"))
    except OSError as exc:
        raise Refusal("UNSEALED", str(exc))
    if jr is not None:
        _journal(jr, durable=True, state="SEALED" if status == STATE.TARGET_EVALUATED else "INDETERMINATE_SEALED",
                 seal_commit=cid)
    try:
        materialize(blob)
    except (OSError, FileExistsError) as exc:
        print(f"MBS308 SEALED {cid} (status {status}); materialization refused: {type(exc).__name__}")
        return 7
    print(f"MBS308 SEALED {cid} (seal-only; status {status}; nothing computed)")
    return 0 if status == STATE.TARGET_EVALUATED else (3 if status == "CONTROL_FAILED" else 5)


def _seal_control_failed() -> int:
    """No marker: only a durable CONTROL_FAILED record (target not consumed) may be sealed."""
    st = store()
    head = git("rev-parse", "HEAD").stdout.strip()
    pending = st.rev(PENDING_REF)
    data = st.get_blob(pending) if pending else st.spool_read(STATE.RESULT_FILE)
    rec, why = STATE.verify_result(data, grant=head, driver_sha=STATE.granted_driver_sha(campaign(), head))
    if rec is None or rec["status"] != "CONTROL_FAILED":
        raise Refusal("SEAL_ONLY", "no marker and no durable CONTROL_FAILED record: nothing to seal")
    if git("status", "--porcelain", "--untracked-files=all").stdout.strip():
        raise Refusal("DIRTY_TREE", "seal-only needs an otherwise clean tree")
    return _pending_seal_materialize(data, "CONTROL_FAILED", None, None)


def run_close_indeterminate(own_sha: str, boot_uuid: str | None = None) -> int:
    """CONSUMED_UNRECORDED only: seal a VALUE-FREE INDETERMINATE record (no checkpoint content, no target value). There
    is no discretionary abandonment: in every other state this refuses."""
    check_flags()
    check_identity()
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
        signal.signal(sig, signal.SIG_IGN)
    st = store()
    lock = STATE.Lock(st)
    try:
        lock.acquire()
    except STATE.Locked as exc:
        raise Refusal(exc.code, str(exc))
    try:
        cls = STATE.classify(campaign(), boot_uuid=boot_uuid, platform=platform_readings())
        if cls["state"] != "CONSUMED_UNRECORDED":
            raise Refusal("NO_DISCRETIONARY_ABANDONMENT", f"close-indeterminate applies only to CONSUMED_UNRECORDED "
                                                          f"(state {cls['state']})")
        if cls.get("git_locks"):
            raise Refusal("GIT_LOCKED", f"campaign git lockfile(s) {', '.join(cls['git_locks'])}: run `recover`")
        marker = cls["marker"]
        drv = cls.get("driver_sha256")
        if drv is None or drv != own_sha or git("rev-parse", "HEAD").stdout.strip() != marker:
            raise Refusal("CLOSE_REFUSED", "the granted driver at the grant commit closes the run")
        jid, jrec = STATE.Journal.read(st)
        jr = STATE.Journal(st, jid or None, jrec if jrec is not None else {"seq": 0})
        try:
            jr.advance(state="CLOSING_INDETERMINATE", grant_commit=marker, driver_sha256=drv,
                       closing_utc=utc(), closing_reason=cls["why"])
        except STATE.JournalConflict:
            raise Refusal("CLOSE_REFUSED", "the journal moved")
        except STATE.RefWriteError as exc:                             # R1 (i)
            raise Refusal("JOURNAL_WRITE_FAILED", f"{exc} (run `recover`)")
        for name in (STATE.RESULT_FILE, STATE.TMP_FILE):
            if st.spool_exists(name):
                st.quarantine(name, "closing")
        rec = {"schema": SCHEMA, "complete": True, "status": "INDETERMINATE_CLOSED", "cell": TARGET_CELL,
               "grant": {"grant_commit": marker}, "driver_sha256": drv, "target_evaluations": 1,
               "consumed_ref": CONSUMED_REF, "mechanical_outcome": "CELL308_EXECUTION_INDETERMINATE",
               "classified": {"state": cls["state"], "why": cls["why"]},
               "journal": None if jrec is None else {"seq": jrec.get("seq"), "attempt": jrec.get("attempt"),
                                                     "n_ckpt": jrec.get("n_ckpt")},
               "closed_utc": utc(), "value_free": True}
        return persist_and_seal(serialize(rec), "INDETERMINATE_CLOSED", jr, cls.get("stale_pending"))
    finally:
        lock.release()


def run_status(boot_uuid: str | None = None) -> str:
    """Read-only; the caller prints the state name only."""
    return STATE.classify(campaign(), boot_uuid=boot_uuid, platform=platform_readings())["state"]


def run_recover(own_sha: str, prepare=None, evaluator=None, boot_uuid: str | None = None) -> int:
    """The only dispatcher: exactly the frozen action of the classified state (mbs308_state.ACTIONS)."""
    check_flags()
    check_identity()
    cls = STATE.classify(campaign(), boot_uuid=boot_uuid, platform=platform_readings())
    s = cls["state"]
    if cls.get("git_locks") and s != "CONSUMED_COMPUTING":
        # R1 (iii): the frozen, recorded, value-free action for stale campaign git lockfiles, BEFORE resume / seal /
        # close: move them aside (never delete). Not stale (a live campaign process, or an open file): nothing.
        if not cls.get("git_locks_stale"):
            print(f"MBS308 RECOVER state {s}: campaign git lockfiles are held (a live campaign process or an open "
                  "file); nothing done")
            return 8
        try:
            moved = STATE.move_stale_git_locks(store(), boot_uuid)
        except STATE.Locked as exc:
            raise Refusal(exc.code, str(exc))
        print(f"MBS308 RECOVER state {s}: {len(moved)} stale campaign git lockfile(s) moved aside (recorded)")
        s = STATE.classify(campaign(), boot_uuid=boot_uuid, platform=platform_readings())["state"]
    action = STATE.ACTIONS[s]
    print(f"MBS308 RECOVER state {s} -> {action}")
    if action == "none":
        return 0
    if action == "wait":
        return 8
    if action == "resume":
        return run_resume(own_sha, prepare=prepare, evaluator=evaluator, boot_uuid=boot_uuid)
    if action == "close-indeterminate":
        return run_close_indeterminate(own_sha, boot_uuid=boot_uuid)
    return run_seal_only(boot_uuid=boot_uuid)


# ------------------------------------------------------------------ rehearsal and decoy (qualification only)
def rehearse(k: int) -> dict:
    """Cell 305 only: C-A (C2's committed record under S_I1) and C-B (tptb_tail reproduction gates at s = rho).
    Equality booleans only; no new-route value on 305."""
    if k not in REHEARSAL_CELLS:
        raise Refusal("CELL_OUT_OF_SCOPE", str(k))
    con = load_consumer()
    sci = load_science(allow_uncommitted=True)
    ctl = controls(con, sci, k)
    ca = ctl["C_A"]
    return {"cell": k, "C_A": {"reproduces_C2_exactly": ca["reproduces_C2_exactly"],
                               "field_matches": ca["field_matches"], "provenance": ca["provenance"]},
            "C_B": ctl["C_B"], "pass": ctl["pass"], "F2_present": sci["indep"] is not None}


def decoy_cover(k: int) -> tuple:
    cells = [c for c in json.loads(CON.read_pinned(REPO, "cells_json")) if c["detector"] == "CUSUM" and c["index"] == k]
    c = cells[0] if len(cells) == 1 else None
    if c is None or any(c[x][1] != "0/1" for x in ("left", "right", "e0", "rho")):
        raise Refusal("DECOY_GEOMETRY", str(k))
    lo, hi, e0, rho = (F(c[x][0]) for x in ("left", "right", "e0", "rho"))
    if e0 - rho != lo or e0 + rho != hi:
        raise Refusal("DECOY_GEOMETRY", f"{k}: cover is not [e0 - rho, e0 + rho]")
    return lo, hi, e0, rho


def r0_order3_variant(bundle: dict) -> dict:
    """The r = 0 adopted order-3 bound made to BIND (stream F3 note: decoy_gen never does): Sclosed:0:3 + Sclosed:3 is
    set below sup_S0[3]; the decoy's own committed record no longer applies and is dropped."""
    import copy
    p = copy.deepcopy(bundle)
    s3 = F(p["meas"]["sup_S0"][3])
    p["aux"]["candidate_suprema"]["Sclosed:0:3"] = fs(s3 / 10)
    p["aux"]["midpoint_eps"]["Sclosed:3"] = fs(s3 / 1000)
    p.pop("committed", None)
    p["decoy_meta"] = dict(p["decoy_meta"], r0_order3_binds=True)
    return p


def supply_scaled_variant(bundle: dict, factor: int = 1000) -> dict:
    """The decoy supply scaled up so that the Stage-1 members (D14M, G) can BIND in the per-block minimum (decoy_gen's
    supplies are small); the decoy's committed record no longer applies and is dropped."""
    import copy
    p = copy.deepcopy(bundle)
    p["supply"] = {j: fs(F(v) * factor) for j, v in p["supply"].items()}
    p.pop("committed", None)
    p["decoy_meta"] = dict(p["decoy_meta"], supply_scaled=factor)
    return p


def decoy_bundles(sci: dict, e0: F, rho: F) -> list:
    """Manufactured TC-T bundles (stream ASSEMBLY decoy_gen, pinned) with the decoy cell's geometry; label DECOY; plus
    the r = 0 order-3-binding variant of the first one and a supply-scaled variant of the second one."""
    DG = sci["asm"]["DG"]
    saved = DG.GEOMS
    DG.GEOMS = [(e0, rho)]
    try:
        out = [DG.make_decoy(i, DECOY_SEED, regime, sign, cap, 0) for i, (regime, sign, cap) in enumerate(DECOY_BUNDLES)]
    finally:
        DG.GEOMS = saved
    return out + [r0_order3_variant(out[0]), supply_scaled_variant(out[1])]


def decoy(k: int, own_sha: str, workers: int, first_blocks, dev_ladder: bool) -> dict:
    if k not in DECOY_CELLS:
        raise Refusal("CELL_OUT_OF_SCOPE", f"{k} is not a declared decoy")
    lo, hi, e0, rho = decoy_cover(k)
    GUARD.guard_drift(lo, hi)                                          # decoy mode: refuses the band
    caps = check_cpu_caps()
    sci = load_science(allow_uncommitted=True, with_decoy_gen=True)
    blocks = S1M.plan(sci["S1"], GUARD, lo, hi)
    for b in blocks:
        GUARD.guard_drift(*b["hull"])
        GUARD.guard_drift(b["b"])
    ladder = S1M.DEV_LADDER if dev_ladder else {"RLR": S1M.LADDER_RLR, "C2B": S1M.LADDER_C2B_N,
                                                "C1B": S1M.LADDER_C1B_D}
    which = None if first_blocks is None else set(range(first_blocks))
    t0 = time.time()
    st1 = stage1("decoy", blocks, "", own_sha, sci, ladder, [], workers, which, allow_uncommitted=True)
    t1 = time.time()
    out = {"decoy_cell": k, "blocks_total": len(blocks), "blocks_run": sorted(which) if which else "all", "cpu_caps": caps,
           "dev_ladder": dev_ladder, "stage1": public_stage1(st1), "stage1_wall_seconds": round(t1 - t0, 1)}
    if k == 297:
        runs = []
        for bundle in decoy_bundles(sci, e0, rho):
            S_dec = {j: F(bundle["supply"][j]) for j in FIELDS}
            try:
                sup, st2 = compose_and_consume(sci, None, blocks, st1, S_dec, [], bundle)
                runs.append({"decoy_meta": bundle["decoy_meta"], "supply": sup, "stage2": st2,
                             "decoy_outcome": "DECOY_CLOSED" if st2["Gamma_dec_lt_0"] else "DECOY_NOT_CLOSED"})
            except (IndependentCheckFailed, CON.Stop, SUP.SupplyRefusal) as exc:
                runs.append({"decoy_meta": bundle["decoy_meta"], "stop": f"{type(exc).__name__}: {exc}"[:400]})
        out["stage2_decoys"] = runs
        out["stage2_wall_seconds"] = round(time.time() - t1, 1)
    out["latent_proxy"] = "decoy values; never juxtapose with any tail-cell number"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("preflight", "rehearse", "decoy", "execute", "status", "recover", "resume",
                                     "seal-only", "close-indeterminate"))
    ap.add_argument("--cell", type=int)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--first-blocks", type=int)
    ap.add_argument("--dev-ladder", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    hooks = STATE.test_hooks_present()
    if hooks:                                   # section 7: the fault-injection hook exists for tests only
        print(f"MBS308 REFUSED TEST_HOOKS_PRESENT: {', '.join(sorted(hooks))}")
        return 2
    own_sha = sha(HERE.read_bytes())

    def wall_cap(*_):
        raise Refusal("WALL_CAP", f"{PRE_CAP_S} s")

    signal.signal(signal.SIGALRM, wall_cap)
    signal.alarm(DECOY_CAP_S if a.mode == "decoy" else PRE_CAP_S)
    try:
        if a.mode not in ("rehearse", "decoy") and a.cell is not None:
            raise Refusal("CELL_OUT_OF_SCOPE", "only rehearse / decoy take --cell; execute is cell 308 only")
        if a.mode != "decoy" and (a.dev_ladder or a.first_blocks is not None):
            raise Refusal("DEV_FLAG_REFUSED", "--dev-ladder / --first-blocks exist in decoy mode only")
        if a.mode == "status":
            print(run_status())
            return 0
        if a.mode == "preflight":
            check_mbr1_state()
            check_not_evaluated()
            out = {"mode": "preflight", "science_modules": check_science_modules(), "input_sha256": check_bindings(),
                   "governance_state": check_governance_state(), "driver_sha256": own_sha,
                   "host_power": require_ac(), "platform": check_platform(), "host_gates": host_preflight(None)}
            load_consumer()
            out["identity"] = load_science(allow_uncommitted=False)["identity"]
            print("MBS308 PREFLIGHT PASS")
        elif a.mode == "rehearse":
            check_platform()                    # DR2 (a): every mode that computes runs on the pinned platform
            check_not_evaluated()
            check_bindings(allow_uncommitted=True)
            check_governance_state()
            t0 = time.time()
            out = {"mode": "rehearse", **rehearse(a.cell), "wall_seconds": round(time.time() - t0, 3),
                   "driver_sha256": own_sha, "utc": utc()}
            print(f"MBS308 REHEARSE cell {a.cell}: C-A and C-B reproduce the committed record exactly = {out['pass']}")
            if not out["pass"]:
                if a.out:
                    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
                return 3
        elif a.mode == "decoy":
            if a.workers > 5 or a.workers < 1:
                raise Refusal("WORKERS", "1..5 workers")
            check_bindings(allow_uncommitted=True)
            check_science_modules()
            check_platform()                    # DR2 (a)
            h0, smp = HOST.snapshot(), HOST.Sampler().start()
            t0 = time.time()
            STATE.CK = ctx = STATE.Ctx(mem_cap_bytes=MEM_CAP_BYTES, mem_poll_s=MEM_POLL_S)
            rss = STATE.RssSampler(os.getpid()).start()     # R-MEM step 6 input (brief 50; recorded fields only)
            try:
                out = decoy(a.cell, own_sha, a.workers, a.first_blocks, a.dev_ladder)
            finally:
                STATE.CK = None
                rss_rec = rss.stop()
            # R-MEM's inputs of this run (protocol section 8; brief 50 task 3): D = the driver's own peak RSS
            # (ru_maxrss of RUSAGE_SELF, bytes on macOS), the <= 0.5 s sampler's growth rate and peaks, and the run's
            # configuration as R-MEM step 1 names it. Recorded only: nothing here changes a computed value.
            out["lifecycle"] = {"stage1_context": ctx.summary(), "rss_sampler": rss_rec,
                                "driver_maxrss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                "rmem_run": {"workers": a.workers, "ladder": "dev" if a.dev_ladder else "frozen",
                                             "mem_cap_bytes": MEM_CAP_BYTES, "mem_poll_s": MEM_POLL_S,
                                             "first_blocks": a.first_blocks,
                                             "launched_by_launchd": HOST.launched_by_launchd()["pass"]}}
            out["host"] = HOST.provenance(h0, smp.stop(), HOST.snapshot())
            cu = resource.getrusage(resource.RUSAGE_CHILDREN)
            out.update({"mode": "decoy", "driver_sha256": own_sha, "utc": utc(), "wall_seconds": round(time.time() - t0, 1),
                        "cpu_seconds_workers": round(cu.ru_utime + cu.ru_stime, 1)})
            print(f"MBS308 DECOY cell {a.cell}: stage 1 in {out['stage1_wall_seconds']} s")
        elif a.mode == "execute":
            return run_execute(own_sha)
        elif a.mode == "resume":
            return run_resume(own_sha)
        elif a.mode == "recover":
            return run_recover(own_sha)
        elif a.mode == "close-indeterminate":
            return run_close_indeterminate(own_sha)
        else:
            return run_seal_only()
        if a.out:
            Path(a.out).write_text(json.dumps(jsonable(out), indent=1, sort_keys=True) + "\n")
        return 0
    except STATE.LostOwnership:
        print("MBS308 LOST OWNERSHIP: another attempt advanced the journal; this attempt wrote nothing more")
        return 9
    except (Refusal, PIN.PinError, GUARD.QuarantineRefusal, CON.ConsumerRefusal, STATE.StateError,
            SciencePinError, STATE.RefWriteError) as e:
        print(f"MBS308 REFUSED {e}")
        return 4 if getattr(e, "code", None) == "UNSEALED" else 2
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    # MB-S: a hard exit once main() has returned. Everything durable has been written and fsync'd by then; the
    # interpreter's own exit would join concurrent.futures' manager thread, which can wait forever for a pool abandoned
    # by an exception (e.g. the EVAL_CAP alarm) -- a lingering launchd job holding caffeinate.
    _rc = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(_rc)
