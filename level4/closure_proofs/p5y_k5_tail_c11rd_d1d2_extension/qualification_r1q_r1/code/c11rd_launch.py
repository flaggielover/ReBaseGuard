"""C11RD-R1Q-R1 -- the repaired, sanitized, sealing LAUNCHER of the ONE cell-306 D1/D2 execution.

A qualification-governance addition OUTSIDE the frozen scientific object (freeze ce5b8595): nothing
under code/ changes and every frozen hash stays valid. It SUPERSEDES qualification_r1/code/c11rd_launch.py
of the rejected qualification 3addf9d3 (review 89330534, QUALIFICATION_REJECTED, blocker B-1: the
automatic seal could fail AFTER the one execution was consumed, on repository states the preflight
never looked at). That file is historical and is NOT a permitted entry. The frozen runner
(code/c11rd_runs.py --mode real) remains the only code that computes and keeps all its own guards
R0-R7; this launcher only decides WHETHER it may start and SEALS what it leaves.

Invariant: complete preflight -> final gate -> consume exactly once -> run once -> immediate seal.
Everything that can be checked before consumption is checked before consumption; after consumption
nothing is ever reported as a refusal.

  L1 SANITIZED STATE. The launcher proceeds only when the process IS in the sanitized state: flags
     -I -S -B, no pycache prefix, and exactly the environment SAFE_ENV (PATH=/usr/bin:/bin,
     HOME=/var/empty, LANG=C, GIT_NO_REPLACE_OBJECTS=1, GIT_CONFIG_NOSYSTEM=1,
     GIT_CONFIG_GLOBAL=/dev/null, GIT_ATTR_NOSYSTEM=1, GIT_OPTIONAL_LOCKS=0) plus the two keys the
     runtime itself adds (LC_CTYPE from PEP 538, __CF_USER_TEXT_ENCODING from macOS). Otherwise it
     re-executes itself ONCE into that state; a process that carries the re-exec marker but is not in
     that state refuses (a preset marker cannot skip the re-exec). Checked before any frozen import.
     Every git call: /usr/bin/git --no-replace-objects -c core.commitGraph=false
     -c core.hooksPath=/dev/null -c core.fsmonitor=false, in its own session.
  L2 PREFLIGHT, fail-closed, creating nothing. Commit ids are validated (40 hex) before any git call.
     The qualified host, interpreter (the executable stub, the Mach-O image actually running and
     libpython), the interpreter runtime files (re-hashed), the worktree, the launcher's own sha256,
     the exact freeze commit and the canonical qualification paths, the frozen runner's hash; the
     frozen grant check; the runner's own guards R0, R1, R4, R5, R6/R7 run in advance; the SEAL
     preconditions: HEAD == the authorization review commit on the qualified branch, the index
     equals HEAD with no unmerged entry, the worktree and the namespace clean, no git lock file in
     the worktree's git dir, the common dir or refs/, no merge/rebase/cherry-pick/revert/bisect in
     progress, files ref backend, an explicit repo-local identity, no sparse checkout, no git
     attribute on the seal paths, writable object store; AC power and an open lid; idle host, disk,
     memory, a readable process table, no other runner, no consumed ref.
  L3 SLEEP PREVENTION. /usr/bin/caffeinate -i -s -w <launcher pid> in its own session, verified in
     `pmset -g assertions` (PreventUserIdleSystemSleep and PreventSystemSleep).
  GATE Signal deferral is installed, then the seal preconditions, the consumed ref and the runs
     paths are checked AGAIN immediately before consumption; a signal received so far refuses.
  L4 CONSUMPTION. The create-only ref refs/c11rd/r1-execution-consumed in the COMMON git dir. From
     here the one execution is consumed whatever happens next.
  L5 ONE RUN. The frozen runner once, sanitized environment, log outside the worktree. SIGINT,
     SIGTERM, SIGHUP, SIGQUIT are forwarded while it runs; a signal between consumption and the
     start means the runner is NOT started (the execution stays consumed).
  L6 IMMEDIATE SEAL, signals deferred (recorded, not acted on) until the report is printed. The
     seal never uses the shared index: on a private index it reads the start HEAD's tree, adds
     evidence/runs/ (artifact, .partial, lock, the runner log, the launch journal -- whatever
     exists), writes the tree, creates the commit (parent = start HEAD), and moves the branch with a
     compare-and-swap update-ref. Transient failures are retried under the bounded policy
     SEAL_RETRY_DELAYS (seal steps only; the runner is never started again); a moved branch is
     permanent. Then the worktree index is refreshed for evidence/runs/ only. The launcher never
     reads a value of the runs artifact.

Exit codes: 0 SEALED (any outcome class); 2 REFUSE (nothing consumed, nothing run); 4 the
distinct terminal state "EXECUTION CONSUMED — RESULT UNSEALED" (never prefixed REFUSE), whose only
permitted continuation is the seal-only recovery (--seal-only), which never starts the runner; 5
"SEAL-ONLY REFUSED" (the recovery's preconditions failed; it changed nothing).

Outcome classes (exit code and file presence only):
  COMPLETED_CERTIFIED          exit 0, artifact and lock present
  COMPLETED_NOT_CERTIFIED      exit 3, artifact and lock present (cap hit or accounting failure)
  CONSUMED_NO_RESULT           lock present, no artifact (crash, kill, interruption)
  REFUSED_BEFORE_LOCK          runner started, no lock (the runner refused at R0-R7); consumed
  CONSUMED_RUNNER_NOT_STARTED  consumed, runner never started (a signal or a start failure)
  ANOMALOUS                    any other combination (sealed as found; the execution review decides)

    python3 -I -S -B c11rd_launch.py --authorization-review-commit SHA [--preflight-only | --seal-only]
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parents[1]
REPO = NS.parents[2]
NS_REL = "level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension"
FREEZE_COMMIT = "ce5b85959a1693525f9e001e7c191516a4ee7d76"
QUAL_SCHEMA = "c11rd.qualification.r1q_r1"
FROZEN_CODE = NS / "code"
RUNNER_REL = "code/c11rd_runs.py"
LAUNCHER_REL = "qualification_r1q_r1/code/c11rd_launch.py"
QUAL_ARTIFACT_REL = "evidence/qualification_r1q_r1/C11RD_R1Q_R1_QUALIFICATION.json"
QUAL_REVIEW_REL = "review/C11RD_R1Q_R1_QUALIFICATION_REVIEW.md"
GRANT_REL = "config/C11RD_GRANT.json"
FREEZE_REL = "protocol/C11RD_FREEZE_R1.json"
RUNS_DIR_REL = "evidence/runs"
LOCK_NAME = "C11RD_EXECUTION.lock"
ARTIFACT_NAME = "C11RD_RUNS.json"
SEALED_LOG_NAME = "C11RD_EXECUTION.log"
SEALED_JOURNAL_NAME = "C11RD_LAUNCH_JOURNAL.jsonl"
CONSUMED_REF = "refs/c11rd/r1-execution-consumed"
LOG_DIR_NAME = "c11rd_r1"                                # under the git COMMON dir, outside every worktree
GIT = "/usr/bin/git"
GIT_PREFIX = (GIT, "--no-replace-objects", "-c", "core.commitGraph=false", "-c", "core.hooksPath=/dev/null",
              "-c", "core.fsmonitor=false")
CAFFEINATE = "/usr/bin/caffeinate"
PMSET = "/usr/bin/pmset"
IOREG = "/usr/sbin/ioreg"
VM_STAT = "/usr/bin/vm_stat"
PS = "/bin/ps"
SAFE_ENV = {"PATH": "/usr/bin:/bin", "HOME": "/var/empty", "LANG": "C", "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_ATTR_NOSYSTEM": "1",
            "GIT_OPTIONAL_LOCKS": "0"}
RUNTIME_ADDED = {"LC_CTYPE": re.compile(r"(C\.)?UTF-8"),                     # PEP 538 locale coercion
                 "__CF_USER_TEXT_ENCODING": re.compile(r"0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+")}  # macOS
MARKER = "C11RD_LAUNCH_SANITIZED"
SEAL_RETRY_DELAYS = (1, 2, 4, 8, 16, 32)       # 7 seal attempts within 63 s; the SEAL only, never the runner
REFRESH_RETRY_DELAYS = (1, 2)                  # the cosmetic worktree-index refresh after a landed seal
IN_PROGRESS = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "REBASE_HEAD", "BISECT_LOG", "AUTO_MERGE",
               "rebase-merge", "rebase-apply", "sequencer")
EXIT_SEALED, EXIT_REFUSED, EXIT_UNSEALED, EXIT_SEAL_ONLY_REFUSED = 0, 2, 4, 5
UNSEALED_BANNER = "EXECUTION CONSUMED — RESULT UNSEALED"
HEX40 = re.compile(r"[0-9a-f]{40}")
FORWARDED = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT)
STATE = {"consumed": False}


class LaunchRefusal(Exception):
    """Before consumption only: nothing was consumed and nothing ran. The message starts with REFUSE."""


class SealFailure(Exception):
    def __init__(self, msg, permanent=False):
        super().__init__(msg)
        self.permanent = permanent


class SealOnlyRefusal(Exception):
    """The seal-only recovery did not start (its preconditions failed); it changed nothing."""


class ConsumedUnsealed(Exception):
    """After consumption: the terminal UNSEALED state (report dict attached)."""
    def __init__(self, report):
        super().__init__(UNSEALED_BANNER)
        self.report = report


# ------------------------------------------------------------------------------------------------
# L1: the sanitized state
# ------------------------------------------------------------------------------------------------
def safe_env() -> dict:
    return dict(SAFE_ENV)


def sanitize_process_env() -> dict:
    """Replace this process's environment by the safe set (frozen functions inherit os.environ)."""
    os.environ.clear()
    os.environ.update(SAFE_ENV)
    return safe_env()


def sanitized_state_problems() -> list:
    """Every way this process differs from the state the sanitizing re-exec produces (empty = in it)."""
    p = []
    fl = sys.flags
    if not (fl.isolated and fl.no_site and fl.dont_write_bytecode) or sys.pycache_prefix is not None:
        p.append("the interpreter is not running as `python3 -I -S -B` without a pycache prefix")
    env = dict(os.environ)
    if env.pop(MARKER, "1") != "1":
        p.append(f"{MARKER} has an unexpected value")
    for k, v in SAFE_ENV.items():
        if env.pop(k, None) != v:
            p.append(f"{k} is not the sanitized value")
    for k, pat in RUNTIME_ADDED.items():
        if k in env and not pat.fullmatch(env.pop(k)):
            p.append(f"{k} has an unexpected value")
    if env:
        p.append(f"unexpected environment variables {sorted(env)}")
    return p


def _run(argv, *, env_extra=None, text=True, timeout=600):
    """A child in its OWN session: a terminal's SIGINT/SIGHUP to the launcher's group never reaches it."""
    return subprocess.run(argv, capture_output=True, text=text, env=dict(SAFE_ENV, **(env_extra or {})),
                          start_new_session=True, timeout=timeout)


def git(repo, *args, env_extra=None, text=True):
    return _run([*GIT_PREFIX, "-C", str(repo), *args], env_extra=env_extra, text=text)


def is_commit_id(x) -> bool:
    return isinstance(x, str) and HEX40.fullmatch(x) is not None


def sha256(path) -> str:
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def _frozen():
    """The frozen runner module (its pre-import barrier runs; the interpreter must be -I -S -B)."""
    if str(FROZEN_CODE) not in sys.path:
        sys.path.insert(0, str(FROZEN_CODE))
    import c11rd_runs as RN
    return RN


# ------------------------------------------------------------------------------------------------
# the interpreter actually running (review QR1.N-11)
# ------------------------------------------------------------------------------------------------
def loaded_images() -> list:
    """Every Mach-O image dyld has loaded into this process; image 0 is the main executable."""
    import ctypes
    lib = ctypes.CDLL(None)
    lib._dyld_image_count.restype = ctypes.c_uint32
    lib._dyld_get_image_name.restype = ctypes.c_char_p
    lib._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    return [lib._dyld_get_image_name(i).decode() for i in range(lib._dyld_image_count())]


def interpreter_identity() -> dict:
    """sys.executable (a framework stub on macOS), the Mach-O image that actually runs (dyld image 0)
    and libpython, each with its sha256; version and flags."""
    imgs = [os.path.realpath(x) for x in loaded_images()]
    exe = os.path.realpath(sys.executable)
    lib = os.path.realpath(os.path.join(sys.base_prefix, "Python"))
    return {"executable_realpath": exe, "executable_sha256": sha256(exe),
            "main_image": imgs[0], "main_image_sha256": sha256(imgs[0]),
            "libpython": lib, "libpython_sha256": sha256(lib) if os.path.isfile(lib) else None,
            "libpython_loaded": lib in imgs, "version": sys.version.split()[0],
            "flags_isolated_nosite_nobytecode": bool(sys.flags.isolated and sys.flags.no_site
                                                     and sys.flags.dont_write_bytecode)}


def runtime_files() -> dict:
    """sha256 of every interpreter file this process has loaded: Mach-O images under the interpreter
    prefix (main image, libpython, extension modules) and the standard-library sources AND the
    cached bytecode actually executed (-B stops writing .pyc, not reading them)."""
    base = os.path.realpath(sys.base_prefix) + "/"
    paths = {os.path.realpath(x) for x in loaded_images()}
    for m in list(sys.modules.values()):
        for attr in ("__file__", "__cached__"):
            f = getattr(m, attr, None)
            if isinstance(f, str):
                paths.add(os.path.realpath(f))
    return {f: sha256(f) for f in sorted(paths) if f.startswith(base) and os.path.isfile(f)}


def runtime_problems(qualified) -> list:
    rec = qualified.get("runtime_files_sha256") or {}
    if not rec:
        return ["the qualification binds no interpreter runtime files"]
    p = []
    changed = [f for f, h in rec.items() if not os.path.isfile(f) or sha256(f) != h]
    if changed:
        p.append(f"interpreter runtime files differ from the qualified ones ({len(changed)}, e.g. {changed[:2]})")
    unbound = [f for f in runtime_files() if f not in rec]
    if unbound:
        p.append(f"this process loaded interpreter files the qualification did not bind ({unbound[:3]})")
    return p


# ------------------------------------------------------------------------------------------------
# host state
# ------------------------------------------------------------------------------------------------
def available_memory_kb() -> int | None:
    """free + inactive + speculative pages of `vm_stat` (None if unreadable)."""
    try:
        out = _run([VM_STAT], timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"page size of (\d+) bytes", out)
    pages = {k: int(v) for k, v in re.findall(r"Pages (free|inactive|speculative):\s+(\d+)\.", out)}
    if not m or set(pages) != {"free", "inactive", "speculative"}:
        return None
    return sum(pages.values()) * int(m.group(1)) // 1024


def other_runner_processes() -> list | None:
    try:
        out = _run([PS, "-A", "-o", "pid=,command="], timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return [ln.strip() for ln in out.stdout.splitlines() if "c11rd_runs.py" in ln and str(os.getpid()) != ln.split()[0]]


def power_state() -> dict:
    """{'ac_power': bool|None, 'lid_open': bool|None} from `pmset -g batt` and the clamshell state."""
    try:
        batt = _run([PMSET, "-g", "batt"], timeout=30).stdout
        clam = _run([IOREG, "-r", "-k", "AppleClamshellState", "-d", "4"], timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return {"ac_power": None, "lid_open": None}
    m = re.search(r"Now drawing from '([^']+)'", batt)
    k = re.search(r'"AppleClamshellState" = (Yes|No)', clam)
    return {"ac_power": None if not m else m.group(1) == "AC Power", "lid_open": None if not k else k.group(1) == "No"}


# ------------------------------------------------------------------------------------------------
# L2: preflight
# ------------------------------------------------------------------------------------------------
def commit_id_problems(g: dict, auth_review_commit) -> list:
    """Review QR1.N-14: every commit id that will reach git is a full 40-hex id (no option injection)."""
    q = g.get("qualification") if isinstance(g.get("qualification"), dict) else {}
    ids = {"grant freeze_commit": g.get("freeze_commit"), "grant qualification.commit": q.get("commit"),
           "grant qualification.review_commit": q.get("review_commit"), "authorization review commit": auth_review_commit}
    bad = sorted(k for k, v in ids.items() if not is_commit_id(v))
    return [f"not a full 40-hex commit id: {bad}"] if bad else []


def load_qualified(repo, ns_rel, grant) -> dict:
    """The qualification artifact AT the grant's qualification commit, from the canonical path."""
    q = grant.get("qualification") if isinstance(grant, dict) and isinstance(grant.get("qualification"), dict) else {}
    qc = q.get("commit")
    if not is_commit_id(qc):
        raise LaunchRefusal("REFUSE L2: the grant's qualification commit is not a full 40-hex commit id")
    r = git(repo, "show", f"{qc}:{ns_rel}/{QUAL_ARTIFACT_REL}", text=False)
    if r.returncode != 0:
        raise LaunchRefusal("REFUSE L2: the qualification artifact is not at its canonical path in the qualification commit")
    try:
        art = json.loads(r.stdout)
    except ValueError:
        raise LaunchRefusal("REFUSE L2: the qualification artifact is not JSON")
    if not isinstance(art, dict) or art.get("schema") != QUAL_SCHEMA:
        raise LaunchRefusal(f"REFUSE L2: the qualification artifact is not a {QUAL_SCHEMA} artifact")
    return art


def git_dirs(repo):
    gd = git(repo, "rev-parse", "--path-format=absolute", "--git-dir")
    cd = git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if gd.returncode != 0 or cd.returncode != 0:
        return None
    return pathlib.Path(os.path.realpath(gd.stdout.strip())), pathlib.Path(os.path.realpath(cd.stdout.strip()))


def lock_files(gd: pathlib.Path, cd: pathlib.Path) -> list:
    found = set()
    for d in (gd, cd):
        found |= {str(f) for f in d.glob("*.lock")}
        if (d / "refs").is_dir():
            found |= {str(f) for f in (d / "refs").rglob("*.lock")}
    return sorted(found)


def seal_paths(ns_rel) -> list:
    return [f"{ns_rel}/{RUNS_DIR_REL}/{n}" for n in (ARTIFACT_NAME, ARTIFACT_NAME + ".partial", LOCK_NAME,
                                                     SEALED_LOG_NAME, SEALED_JOURNAL_NAME)]


def seal_safety_problems(repo, ns_rel, auth_review_commit, qualified) -> list:
    """Review QR1.B-1: every repository state that would make the immediate seal predictably fail
    (or seal on a different base) refuses BEFORE consumption. Reads only."""
    repo = pathlib.Path(repo)
    dirs = git_dirs(repo)
    if not dirs:
        return ["the git directories cannot be established"]
    gd, cd = dirs
    p = []
    head = git(repo, "rev-parse", "--verify", "-q", "HEAD").stdout.strip()
    if head != auth_review_commit:
        p.append("HEAD is not the authorization review commit")
    sym = git(repo, "symbolic-ref", "-q", "HEAD")
    if sym.returncode != 0 or sym.stdout.strip() != qualified.get("launch_branch"):
        p.append("HEAD is not the qualified launch branch (detached, or another branch)")
    if git(repo, "rev-parse", "--show-ref-format").stdout.strip() != "files":
        p.append("the ref storage is not the files backend")
    locks = lock_files(gd, cd)
    if locks:
        p.append(f"git lock files present: {locks}")
    busy = [n for n in IN_PROGRESS if (gd / n).exists()]
    if busy:
        p.append(f"a git operation is in progress: {busy}")
    if git(repo, "diff-index", "--cached", "--quiet", "HEAD", "--").returncode != 0:
        p.append("the index differs from HEAD (staged changes anywhere in the repository)")
    if git(repo, "ls-files", "--unmerged").stdout.strip():
        p.append("the index has unmerged entries")
    st = git(repo, "status", "--porcelain", "--untracked-files=all")
    if st.returncode != 0 or st.stdout.strip():
        p.append("the worktree is not clean (modified or untracked files)")
    ns_st = git(repo, "status", "--porcelain", "--ignored", "--untracked-files=all", "--", ns_rel)
    if ns_st.returncode != 0 or ns_st.stdout.strip():
        p.append("the namespace is not clean")
    for key in ("user.name", "user.email"):
        if not git(repo, "config", "--get", key).stdout.strip():
            p.append(f"no explicit {key}: the seal commit needs a configured identity")
    if any(git(repo, "var", v).returncode != 0 for v in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT")):
        p.append("the commit identity cannot be resolved")
    if git(repo, "config", "--bool", "core.sparseCheckout").stdout.strip() == "true":
        p.append("sparse checkout is on")
    attrs = git(repo, "check-attr", "-a", "--", *seal_paths(ns_rel))
    if attrs.returncode != 0 or attrs.stdout.strip():
        p.append("git attributes apply to the seal paths")
    for d in (cd / "objects", cd / "refs", gd, repo / ns_rel / "evidence"):
        if not (d.is_dir() and os.access(d, os.W_OK)):
            p.append(f"not a writable directory: {d}")
    return p


def runner_guard_problems(repo, ns_rel, RN, fz) -> list:
    """Review QR1.N-9: the frozen runner's own guards that can be decided before consumption, run in
    advance by calling the frozen functions (the runner re-runs all of them authoritatively)."""
    repo = pathlib.Path(repo)
    p = []

    def guard(label, fn):
        try:
            fn()
        except SystemExit as exc:
            p.append(f"{label}: {exc}")
        except Exception as exc:                                  # noqa: BLE001 -- any failure refuses
            p.append(f"{label}: {type(exc).__name__}: {exc}")
    guard("runner R0 (loaded modules)", RN.verify_loaded_modules)
    guard("runner R1 (frozen code, C7)", lambda: RN.verify_code(fz))
    ns = repo / ns_rel
    if any(os.path.lexists(ns / RUNS_DIR_REL / n) for n in (ARTIFACT_NAME, LOCK_NAME)):
        p.append("runner R4: a runs artifact or execution lock exists on disk")

    def r4():
        hist = RN.ever_committed([f"{ns_rel}/{RN.RUNS_REL}", f"{ns_rel}/{RN.LOCK_REL}"], repo=repo)
        if hist:
            raise RN.Refusal(f"REFUSE R4: a runs artifact or lock was committed before ({hist[:3]})")
    guard("runner R4 (history)", r4)
    guard("runner R5 (premise)", RN.MD.c11r_fh_premise)

    def r6():
        lo, hi = RN.MD.cell_block()
        if [str(lo), str(hi)] != fz["target"]["drift_block"] or fz["target"]["cell"] != 306:
            raise RN.Refusal("REFUSE R6: the statement table's block is not the frozen target")
        RN.verify_cover_and_accounting(fz)
    guard("runner R6/R7 (target, cover, accounting)", r6)
    return p


def preflight(repo, ns_rel, auth_review_commit, qualified, *, runner_path, launcher_path=None) -> list:
    """Every reason not to launch (empty = launch). Creates nothing."""
    repo, ns = pathlib.Path(repo), pathlib.Path(repo) / ns_rel
    gp = ns / GRANT_REL
    if not gp.is_file() or gp.is_symlink():
        return [f"no grant at {GRANT_REL} (or it is a symlink)"]
    try:
        g = json.loads(gp.read_text())
    except ValueError:
        return ["the grant is not JSON"]
    if not isinstance(g, dict):
        return ["the grant is not a JSON object"]
    bad = commit_id_problems(g, auth_review_commit)
    if bad:
        return bad
    RN = _frozen()
    fz = json.loads((ns / FREEZE_REL).read_text())
    try:
        host = RN.host_identity()
        wt = RN.worktree_identity(repo=repo)
    except SystemExit as exc:
        return [f"identity: {exc}"]
    p = [f"frozen grant check: {x}" for x in
         RN.grant_problems(fz, g, host=host, worktree=wt, auth_review_commit=auth_review_commit, repo=repo, ns=ns,
                           code_dir=pathlib.Path(runner_path).parent)]
    if host != qualified.get("host", {}).get("grant_host"):
        p.append("host identity is not the qualified host")
    if interpreter_identity() != qualified.get("interpreter"):
        p.append("interpreter (stub, running image, libpython, version, -I -S -B) is not the qualified one")
    p += runtime_problems(qualified)
    if wt != qualified.get("worktree"):
        p.append("worktree identity is not the qualified worktree")
    own = pathlib.Path(launcher_path or __file__).resolve()
    if sha256(own) != qualified.get("qualification_code_sha256", {}).get(LAUNCHER_REL):
        p.append("this launcher is not the qualified launcher (sha256)")
    if g.get("freeze_commit") != qualified.get("freeze_commit"):
        p.append("the grant's freeze commit is not the qualified freeze")
    q = g.get("qualification") or {}
    if q.get("artifact_path") != f"{ns_rel}/{QUAL_ARTIFACT_REL}" or q.get("review_path") != f"{ns_rel}/{QUAL_REVIEW_REL}":
        p.append("the grant's qualification paths are not the canonical ones")
    if sha256(runner_path) != qualified.get("frozen_code_sha256", {}).get(RUNNER_REL):
        p.append("the runner is not the frozen runner")
    p += runner_guard_problems(repo, ns_rel, RN, fz)
    p += seal_safety_problems(repo, ns_rel, auth_review_commit, qualified)
    lim = qualified.get("launch_limits", {})
    pw = power_state()
    if lim.get("require_ac_power", True) and pw["ac_power"] is not True:
        p.append(f"not on AC power ({pw['ac_power']})")
    if lim.get("require_lid_open", True) and pw["lid_open"] is not True:
        p.append(f"the lid is not open ({pw['lid_open']})")
    if os.getloadavg()[0] > lim.get("load1_max", -1):
        p.append(f"host not idle: 1-min load {os.getloadavg()[0]:.2f} > {lim.get('load1_max')}")
    if shutil.disk_usage(repo).free < lim.get("disk_free_min_bytes", float("inf")):
        p.append("free disk below the qualified minimum")
    mem = available_memory_kb()
    if mem is None or mem < lim.get("memory_available_min_kb", float("inf")):
        p.append("available memory unreadable or below the qualified minimum")
    if RN.memory_status(os.getpid(), fz["resource_caps"]["rss_kb"], ps=PS)[0] != "OK":
        p.append("process table unreadable (memory accounting impossible)")
    others = other_runner_processes()
    if others is None or others:
        p.append(f"other runner processes or unreadable process list: {others}")
    if git(repo, "rev-parse", "--verify", "-q", CONSUMED_REF).returncode == 0:
        p.append("the execution was already consumed (consumed ref exists)")
    return p


# ------------------------------------------------------------------------------------------------
# L3 - L6
# ------------------------------------------------------------------------------------------------
def start_sleep_prevention() -> subprocess.Popen:
    c = subprocess.Popen([CAFFEINATE, "-i", "-s", "-w", str(os.getpid())], env=safe_env(), start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        out = _run([PMSET, "-g", "assertions"], timeout=30).stdout
        mine = [ln for ln in out.splitlines() if f"pid {c.pid}(caffeinate)" in ln]
        if any("PreventUserIdleSystemSleep" in ln for ln in mine) and any("PreventSystemSleep" in ln for ln in mine):
            return c
        time.sleep(0.1)
    c.kill()
    raise LaunchRefusal("REFUSE L3: the sleep-prevention assertions could not be verified")


class SignalGuard:
    """From the final gate to the printed report: SIGINT/SIGTERM/SIGHUP/SIGQUIT are recorded and, while
    the runner lives, forwarded to it; they never interrupt the launcher (so never the seal).
    SIGTSTP is recorded and ignored."""
    def __init__(self):
        self.received, self.child, self.phase, self.old = [], None, "gate", {}

    def _handler(self, signum, _frame):
        ev = {"signal": signal.Signals(signum).name, "phase": self.phase, "forwarded": False}
        if self.child is not None and signum != signal.SIGTSTP:
            try:
                self.child.send_signal(signum)
                ev["forwarded"] = True
            except (ProcessLookupError, OSError):
                pass
        self.received.append(ev)

    def install(self):
        self.old = {s: signal.signal(s, self._handler) for s in (*FORWARDED, signal.SIGTSTP)}

    def restore(self):
        for s, h in self.old.items():
            signal.signal(s, h)


class Journal:
    """Append-only JSON-lines record of the launch, outside the worktree (fsync'ed per event). A failing
    write never raises: the journal is evidence, it must not decide whether the seal happens."""
    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.launch_id = f"{os.getpid()}-{time.time():.6f}"
        self.write_failures = 0

    def event(self, kind, **kw):
        rec = {"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "launch": self.launch_id, "event": kind, **kw}
        try:
            with open(self.path, "a") as f:
                f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")
                f.flush()
                os.fsync(f.fileno())
        except OSError:
            self.write_failures += 1


def consume(repo, head) -> None:
    r = git(repo, "update-ref", "-m", "C11RD-R1: the one execution is consumed", CONSUMED_REF, head, "")
    if r.returncode != 0:
        raise LaunchRefusal("REFUSE L4: the consumed ref could not be created (it exists or is locked); "
                            f"this launch consumed nothing and ran nothing: {r.stderr.strip()}")


def run_once(cmd, cwd, log_path, sig: SignalGuard) -> int:
    with open(log_path, "x") as log:
        child = subprocess.Popen(cmd, cwd=str(cwd), env=safe_env(), stdout=log, stderr=subprocess.STDOUT)
        sig.child, sig.phase = child, "running"
        try:
            while True:
                try:
                    return child.wait()
                except Exception:                           # noqa: BLE001 -- never seal while the runner lives
                    if child.poll() is not None:
                        return child.returncode
                    time.sleep(1)
        finally:
            sig.child, sig.phase = None, "sealing"


def outcome_class(rc, runs_dir: pathlib.Path) -> str:
    art, lock = (runs_dir / ARTIFACT_NAME).exists(), (runs_dir / LOCK_NAME).exists()
    if rc is None:
        return "CONSUMED_RUNNER_NOT_STARTED" if not (art or lock) else "ANOMALOUS"
    if rc == 0 and art and lock:
        return "COMPLETED_CERTIFIED"
    if rc == 3 and art and lock:
        return "COMPLETED_NOT_CERTIFIED"
    if lock and not art:
        return "CONSUMED_NO_RESULT"
    if not lock and not art:
        return "REFUSED_BEFORE_LOCK"
    return "ANOMALOUS"


def recovered_class(runs_dir: pathlib.Path) -> str:
    """The class of a result sealed by the seal-only recovery without the launcher's report (launcher
    death): from file presence only; the execution review decides."""
    art, lock = (runs_dir / ARTIFACT_NAME).exists(), (runs_dir / LOCK_NAME).exists()
    return {(True, True): "RECOVERED_ARTIFACT_AND_LOCK", (False, True): "RECOVERED_LOCK_ONLY",
            (False, False): "RECOVERED_NO_LOCK"}.get((art, lock), "ANOMALOUS")


def _seal_attempt(repo, ns_rel, start_head, branch_ref, msg, tmp_index, prior) -> dict:
    """One attempt. SealFailure(permanent=True) if the branch moved; transient otherwise. Never touches
    the shared index; the only shared state it changes is the branch ref, by compare-and-swap."""
    runs = f"{ns_rel}/{RUNS_DIR_REL}"
    sym = git(repo, "symbolic-ref", "-q", "HEAD")
    if sym.returncode != 0 or sym.stdout.strip() != branch_ref:
        raise SealFailure("HEAD is no longer the launch branch", permanent=True)
    cur = git(repo, "rev-parse", "--verify", "-q", branch_ref).stdout.strip()
    if cur in prior:                                          # an earlier attempt of THIS seal landed
        return _verify_landed(repo, start_head, cur)
    if cur != start_head:
        raise SealFailure(f"the launch branch moved during the execution ({start_head[:12]} -> {cur[:12]})", permanent=True)
    env = {"GIT_INDEX_FILE": str(tmp_index)}
    for f in (tmp_index, pathlib.Path(str(tmp_index) + ".lock")):
        f.unlink(missing_ok=True)

    def step(label, r):
        if r.returncode != 0:
            raise SealFailure(f"{label}: {(r.stderr or '').strip()[:300]}")
        return r.stdout.strip()
    step("read-tree", git(repo, "read-tree", start_head, env_extra=env))
    step("add", git(repo, "add", "-f", "--", runs, env_extra=env))
    staged = step("diff-index", git(repo, "diff-index", "--cached", "--name-only", start_head, "--", env_extra=env)).split()
    if not staged or any(not s.startswith(runs + "/") for s in staged):
        raise SealFailure(f"the private index stages unexpected paths {staged}", permanent=True)
    tree = step("write-tree", git(repo, "write-tree", env_extra=env))
    commit = step("commit-tree", git(repo, "commit-tree", "--no-gpg-sign", tree, "-p", start_head, "-m", msg))
    prior.add(commit)
    upd = git(repo, "update-ref", "-m", "C11RD-R1: immediate seal", branch_ref, commit, start_head)
    if upd.returncode != 0:
        now = git(repo, "rev-parse", "--verify", "-q", branch_ref).stdout.strip()
        if now != commit:
            raise SealFailure(f"update-ref: {upd.stderr.strip()[:300]}", permanent=(now != start_head))
    tmp_index.unlink(missing_ok=True)
    return _verify_landed(repo, start_head, commit)


def _verify_landed(repo, start_head, commit) -> dict:
    head = git(repo, "rev-parse", "--verify", "-q", "HEAD").stdout.strip()
    parent = git(repo, "rev-parse", "--verify", "-q", f"{commit}^").stdout.strip()
    parents = git(repo, "rev-list", "--parents", "-n", "1", commit).stdout.split()[1:]
    files = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", start_head, commit).stdout.split()
    if head != commit or parent != start_head or parents != [start_head]:
        raise SealFailure("the seal commit landed but HEAD or its parent is not as expected", permanent=True)
    return {"seal_commit": commit, "sealed_paths": files}


def seal(repo, ns_rel, start_head, branch_ref, rc, copies: dict, journal, *, cls=None, delays=None, label="SEAL") -> dict:
    """The immediate seal with the bounded retry policy (seal steps only; nothing is ever re-run).
    Raises ConsumedUnsealed when the policy is exhausted or the failure is permanent."""
    repo = pathlib.Path(repo)
    delays = SEAL_RETRY_DELAYS if delays is None else tuple(delays)
    runs_dir = repo / ns_rel / RUNS_DIR_REL
    cls = cls or outcome_class(rc, runs_dir)
    msg = (f"p5y: K5 C11RD-R1 — {label} of the one cell-306 D1/D2 execution ({cls}, runner exit {rc})\n\n"
           f"Sealed by the qualified launcher (C11RD-R1Q-R1); no value of the runs artifact was read.\n"
           f"Consumed ref {CONSUMED_REF} -> {start_head}\n")
    tmp_index = pathlib.Path(journal.path).with_name(f"C11RD_SEAL_INDEX_{start_head[:12]}")
    attempts, prior = [], set()
    for i in range(len(delays) + 1):
        try:
            runs_dir.mkdir(parents=True, exist_ok=True)
            journal.event("seal_attempt", attempt=i + 1, outcome=cls, runner_exit=rc)
            for name, src in copies.items():
                if src is not None and pathlib.Path(src).is_file():
                    shutil.copyfile(src, runs_dir / name)
            if journal.path.is_file():
                shutil.copyfile(journal.path, runs_dir / SEALED_JOURNAL_NAME)
            res = _seal_attempt(repo, ns_rel, start_head, branch_ref, msg, tmp_index, prior)
            attempts.append({"attempt": i + 1, "ok": True})
            break
        except (SealFailure, OSError, subprocess.SubprocessError) as exc:
            permanent = getattr(exc, "permanent", False)
            attempts.append({"attempt": i + 1, "ok": False, "permanent": permanent, "error": str(exc)[:400]})
            journal.event("seal_attempt_failed", attempt=i + 1, permanent=permanent, error=str(exc)[:400])
            if permanent or i == len(delays):
                rep = {"start_head": start_head, "consumed_ref": CONSUMED_REF, "runner_exit": rc, "outcome": cls,
                       "seal_attempts": len(attempts), "attempt_log": attempts, "policy_delays_seconds": list(delays),
                       "last_error": str(exc)[:400], "permanent": permanent, "runs_dir": str(runs_dir),
                       "log_dir": str(pathlib.Path(journal.path).parent), "journal": str(journal.path)}
                journal.event("unsealed", **{k: v for k, v in rep.items() if k != "attempt_log"})
                raise ConsumedUnsealed(rep)
            time.sleep(delays[i])
    refreshed = False
    for j in range(len(REFRESH_RETRY_DELAYS) + 1):          # the worktree index learns the sealed paths
        if git(repo, "reset", "-q", "--", f"{ns_rel}/{RUNS_DIR_REL}").returncode == 0:
            refreshed = True
            break
        if j < len(REFRESH_RETRY_DELAYS):
            time.sleep(REFRESH_RETRY_DELAYS[j])
    clean = git(repo, "status", "--porcelain", "--ignored", "--untracked-files=all", "--", ns_rel).stdout.strip() == ""
    out = dict(res, sealed=True, outcome=cls, runner_exit=rc, start_head=start_head, consumed_ref=CONSUMED_REF,
               seal_attempts=len(attempts), attempt_log=attempts, index_refreshed=refreshed,
               namespace_clean_after_seal=clean)
    journal.event("sealed", seal_commit=res["seal_commit"], attempts=len(attempts), index_refreshed=refreshed)
    return out


def final_gate_problems(repo, ns_rel, auth, qualified, log_path, sig) -> list:
    p = seal_safety_problems(repo, ns_rel, auth, qualified)
    if git(repo, "rev-parse", "--verify", "-q", CONSUMED_REF).returncode == 0:
        p.append("the execution was already consumed (consumed ref exists)")
    ns = pathlib.Path(repo) / ns_rel
    if any(os.path.lexists(ns / RUNS_DIR_REL / n) for n in (ARTIFACT_NAME, LOCK_NAME)):
        p.append("a runs artifact or execution lock exists on disk")
    if log_path.exists():
        p.append(f"the execution log already exists: {log_path}")
    if sig.received:
        p.append(f"signal(s) received before consumption: {[s['signal'] for s in sig.received]}")
    return p


def launch(repo, ns_rel, auth_review_commit, *, runner_cmd, runner_path, log_dir, launcher_path=None,
           qualified=None) -> dict:
    """L1-L6 on the given repository (main() passes the real, frozen values)."""
    repo = pathlib.Path(repo)
    sanitize_process_env()
    STATE["consumed"] = False
    if not is_commit_id(auth_review_commit):
        raise LaunchRefusal("REFUSE L2: the authorization review commit is not a full 40-hex commit id")
    if qualified is None:
        gp = repo / ns_rel / GRANT_REL
        if not gp.is_file() or gp.is_symlink():
            raise LaunchRefusal(f"REFUSE L2: no grant at {GRANT_REL} (or it is a symlink)")
        try:
            qualified = load_qualified(repo, ns_rel, json.loads(gp.read_text()))
        except ValueError:
            raise LaunchRefusal("REFUSE L2: the grant is not JSON")
    problems = preflight(repo, ns_rel, auth_review_commit, qualified, runner_path=runner_path, launcher_path=launcher_path)
    if problems:
        raise LaunchRefusal("REFUSE L2: " + "; ".join(problems))
    start_head, branch_ref = auth_review_commit, qualified["launch_branch"]
    log_path = pathlib.Path(log_dir) / f"C11RD_EXECUTION_{start_head[:12]}.log"
    journal = Journal(pathlib.Path(log_dir) / f"C11RD_LAUNCH_JOURNAL_{start_head[:12]}.jsonl")
    journal.event("preflight_pass", start_head=start_head)
    caff = start_sleep_prevention()
    sig = SignalGuard()
    try:
        sig.install()
        gate = final_gate_problems(repo, ns_rel, auth_review_commit, qualified, log_path, sig)
        if gate:
            journal.event("gate_refused", problems=gate)
            raise LaunchRefusal("REFUSE GATE: " + "; ".join(gate))
        consume(repo, start_head)
        STATE["consumed"] = True                            # ---- consumed: never REFUSE from here on
        sig.phase = "consumed"
        journal.event("consumed", ref=CONSUMED_REF, start_head=start_head)
        rc = None
        try:
            if sig.received:
                journal.event("runner_not_started", reason="signal after consumption",
                              signals=[s["signal"] for s in sig.received])
            else:
                journal.event("runner_starting", cmd=[str(x) for x in runner_cmd])
                rc = run_once(runner_cmd, pathlib.Path(runner_path).parent, log_path, sig)
                journal.event("runner_exited", runner_exit=rc)
        except Exception as exc:                            # noqa: BLE001 -- a start failure is still consumed
            journal.event("runner_start_failed", error=f"{type(exc).__name__}: {exc}"[:400])
        sig.phase = "sealing"
        try:
            if not log_path.exists():
                log_path.write_text("runner not started (see the launch journal)\n")
            res = seal(repo, ns_rel, start_head, branch_ref, rc, {SEALED_LOG_NAME: log_path}, journal)
        except ConsumedUnsealed:
            raise
        except BaseException as exc:                        # noqa: BLE001 -- consumed: every failure is UNSEALED
            raise ConsumedUnsealed({"start_head": start_head, "consumed_ref": CONSUMED_REF, "runner_exit": rc,
                                    "outcome": "UNKNOWN", "seal_attempts": None, "permanent": True,
                                    "last_error": f"{type(exc).__name__}: {exc}"[:400], "runs_dir": str(repo / ns_rel / RUNS_DIR_REL),
                                    "log_dir": str(log_dir), "journal": str(journal.path)}) from exc
        sig.phase = "reporting"
        return dict(res, signals_deferred=list(sig.received))
    except ConsumedUnsealed as exc:
        exc.report["signals_deferred"] = list(sig.received)
        _write_unsealed_report(log_dir, exc.report)
        raise
    finally:
        sig.restore()
        caff.terminate()


def _write_unsealed_report(log_dir, rep):
    try:
        p = pathlib.Path(log_dir) / f"C11RD_UNSEALED_{rep['start_head'][:12]}.json"
        p.write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n")
    except OSError:
        pass


def seal_only(repo, ns_rel, auth_review_commit, qualified, *, log_dir) -> dict:
    """The ONLY continuation of the UNSEALED state (and of a launcher death): commit exactly what the
    consumed execution left under evidence/runs/ on top of the start HEAD. It never starts the runner,
    never reads a runs value and cannot un-consume anything."""
    repo = pathlib.Path(repo)
    sanitize_process_env()
    if not is_commit_id(auth_review_commit):
        raise SealOnlyRefusal("SEAL-ONLY REFUSED (nothing changed): the start commit is not a full 40-hex commit id")
    p = []
    if git(repo, "rev-parse", "--verify", "-q", CONSUMED_REF).stdout.strip() != auth_review_commit:
        p.append("the execution was not consumed at this commit (consumed ref absent or elsewhere)")
    if git(repo, "rev-parse", "--verify", "-q", "HEAD").stdout.strip() != auth_review_commit:
        p.append("HEAD is not the start HEAD of the consumed execution")
    sym = git(repo, "symbolic-ref", "-q", "HEAD")
    if sym.returncode != 0 or sym.stdout.strip() != qualified.get("launch_branch"):
        p.append("HEAD is not the qualified launch branch")
    runs = f"{ns_rel}/{RUNS_DIR_REL}"
    if git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", runs).stdout.strip():
        p.append("evidence/runs/ is already in HEAD (already sealed)")
    others = other_runner_processes()
    if others is None or others:
        p.append(f"a runner process may still be running (or the process list is unreadable): {others}")
    log_path = pathlib.Path(log_dir) / f"C11RD_EXECUTION_{auth_review_commit[:12]}.log"
    runs_dir = repo / ns_rel / RUNS_DIR_REL
    if not log_path.is_file() and not (runs_dir.is_dir() and any(runs_dir.iterdir())):
        p.append("nothing to seal (no runs directory content and no launcher log)")
    if p:
        raise SealOnlyRefusal("SEAL-ONLY REFUSED (nothing changed; a consumed, unsealed execution stays so): " + "; ".join(p))
    rep_path = pathlib.Path(log_dir) / f"C11RD_UNSEALED_{auth_review_commit[:12]}.json"
    rc, cls = None, None
    if rep_path.is_file():
        rep = json.loads(rep_path.read_text())
        rc, cls = rep.get("runner_exit"), rep.get("outcome")
    journal = Journal(pathlib.Path(log_dir) / f"C11RD_LAUNCH_JOURNAL_{auth_review_commit[:12]}.jsonl")
    journal.event("seal_only_start")
    sig = SignalGuard()
    sig.phase = "sealing"
    sig.install()
    try:
        res = seal(repo, ns_rel, auth_review_commit, qualified["launch_branch"], rc,
                   {SEALED_LOG_NAME: log_path}, journal, cls=cls or recovered_class(runs_dir),
                   label="SEAL-ONLY RECOVERY")
        return dict(res, signals_deferred=list(sig.received), recovery=True)
    except ConsumedUnsealed as exc:
        exc.report["signals_deferred"] = list(sig.received)
        _write_unsealed_report(log_dir, exc.report)
        raise
    finally:
        sig.restore()


def format_unsealed(rep: dict) -> str:
    return "\n".join([
        UNSEALED_BANNER,
        f"  The one execution IS CONSUMED: {CONSUMED_REF} -> {rep.get('start_head')}",
        f"  runner exit {rep.get('runner_exit')}; outcome class {rep.get('outcome')}",
        f"  seal attempts {rep.get('seal_attempts')} (bounded policy, delays {rep.get('policy_delays_seconds')} s); "
        f"last failure ({'permanent' if rep.get('permanent') else 'transient'}): {rep.get('last_error')}",
        f"  Left exactly as found: {rep.get('runs_dir')}; launcher log and journal under {rep.get('log_dir')}",
        "  DO NOT re-run the launcher or the runner. DO NOT read, move, edit or delete anything under evidence/runs/.",
        "  The ONLY permitted continuation: clear the blocking condition, then run the seal-only recovery",
        f"    python3 -I -S -B {NS_REL}/{LAUNCHER_REL} --authorization-review-commit {rep.get('start_head')} --seal-only",
        "  It commits exactly evidence/runs/ on top of the start HEAD and never starts the runner.",
        "  A seal-only recovery never permits a new D1/D2 execution.",
        "UNSEALED_REPORT " + json.dumps(rep, sort_keys=True, default=str)])


def execute(fn, *args, **kw) -> tuple:
    """(exit code, text) for launch() or seal_only(); after consumption nothing is reported as REFUSE."""
    try:
        return EXIT_SEALED, "SEALED " + json.dumps(fn(*args, **kw), sort_keys=True, default=str)
    except LaunchRefusal as exc:
        return EXIT_REFUSED, str(exc)
    except SealOnlyRefusal as exc:
        return EXIT_SEAL_ONLY_REFUSED, str(exc)
    except ConsumedUnsealed as exc:
        return EXIT_UNSEALED, format_unsealed(exc.report)
    except BaseException as exc:                            # noqa: BLE001
        if STATE["consumed"] or fn is seal_only:
            return EXIT_UNSEALED, format_unsealed({"last_error": f"{type(exc).__name__}: {exc}"[:400],
                                                   "outcome": "UNKNOWN", "permanent": True})
        return EXIT_REFUSED, (f"REFUSE: unexpected error before consumption (nothing consumed, nothing run): "
                              f"{type(exc).__name__}: {exc}")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    probs = sanitized_state_problems()                      # L1, before ANY other import or git call
    if probs:
        if MARKER in os.environ:
            print("REFUSE L1: not in the sanitized state after (or instead of) the sanitizing re-exec: " + "; ".join(probs))
            return EXIT_REFUSED
        os.execve(sys.executable, [sys.executable, "-I", "-S", "-B", str(pathlib.Path(__file__).resolve()), *argv],
                  dict(SAFE_ENV, **{MARKER: "1"}))
    ap = argparse.ArgumentParser()
    ap.add_argument("--authorization-review-commit", required=True)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--preflight-only", action="store_true")
    mode.add_argument("--seal-only", action="store_true")
    a = ap.parse_args(argv)
    if not is_commit_id(a.authorization_review_commit):
        print("REFUSE L2: --authorization-review-commit must be a full 40-hex commit id")
        return EXIT_REFUSED
    gp = NS / GRANT_REL
    if not gp.is_file() or gp.is_symlink():
        print(f"REFUSE L2: no grant at {GRANT_REL} (or it is a symlink)")
        return EXIT_REFUSED
    try:
        grant = json.loads(gp.read_text())
        qualified = load_qualified(REPO, NS_REL, grant)
    except LaunchRefusal as exc:
        print(exc)
        return EXIT_REFUSED
    except (ValueError, OSError, AttributeError) as exc:
        print(f"REFUSE L2: the grant or the qualification artifact is unreadable: {type(exc).__name__}")
        return EXIT_REFUSED
    own = pathlib.Path(__file__).resolve()
    at_head = git(REPO, "show", f"HEAD:{NS_REL}/{LAUNCHER_REL}", text=False)
    if qualified.get("freeze_commit") != FREEZE_COMMIT or at_head.returncode != 0 or at_head.stdout != own.read_bytes() \
            or own != (REPO / NS_REL / LAUNCHER_REL).resolve():
        print("REFUSE L2: not the canonical launcher of the canonical freeze (freeze commit, path, or blob at HEAD)")
        return EXIT_REFUSED
    common = pathlib.Path(git(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    if a.seal_only:
        code, text = execute(seal_only, REPO, NS_REL, a.authorization_review_commit, qualified, log_dir=common / LOG_DIR_NAME)
    elif a.preflight_only:
        sanitize_process_env()
        probs = preflight(REPO, NS_REL, a.authorization_review_commit, qualified, runner_path=NS / RUNNER_REL)
        print("PREFLIGHT " + ("PASS" if not probs else "REFUSED:\n  - " + "\n  - ".join(probs)))
        return EXIT_SEALED if not probs else EXIT_REFUSED
    else:
        cmd = [sys.executable, "-I", "-S", "-B", str(NS / RUNNER_REL), "--mode", "real",
               "--authorization-review-commit", a.authorization_review_commit]
        code, text = execute(launch, REPO, NS_REL, a.authorization_review_commit, runner_cmd=cmd,
                             runner_path=NS / RUNNER_REL, log_dir=common / LOG_DIR_NAME, qualified=qualified)
    print(text, flush=True)
    if code == EXIT_UNSEALED:
        print(text, file=sys.stderr, flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
