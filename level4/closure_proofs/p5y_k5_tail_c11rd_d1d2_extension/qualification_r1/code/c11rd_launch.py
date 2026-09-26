"""C11RD-R1 -- the sanitized, sealing LAUNCHER of the ONE cell-306 D1/D2 execution.

A qualification-phase GOVERNANCE ADDITION, outside the frozen scientific object: nothing under
code/ is changed and every frozen hash stays valid. The frozen runner (code/c11rd_runs.py --mode
real) remains the only code that computes and keeps all its own guards R0-R7. This launcher wraps
it with the controls the C11RD-R1 pre-execution review (3c1eff11) asked for:

  L1 SANITIZED ENVIRONMENT. main() re-executes itself with ONLY PATH=/usr/bin:/bin, HOME, LANG=C
     and GIT_NO_REPLACE_OBJECTS=1; launch() also replaces os.environ by that set before calling
     any frozen function, so no inherited GIT_*, PYTHON* or PATH entry reaches git or the runner
     (review N-5). Every git call here is /usr/bin/git --no-replace-objects -c
     core.commitGraph=false.
  L2 PREFLIGHT, fail-closed, creating nothing: the QUALIFIED host (hostname, hardware UUID,
     platform, Python version, interpreter realpath and sha256) and worktree (canonical path, git
     common dir); the frozen runner's own grant check (c11rd_runs.grant_problems) is empty; the
     grant's freeze_commit is EXACTLY the qualified freeze and its qualification artifact/review
     paths are EXACTLY the qualified canonical paths (review N-8); the namespace is clean; the
     host is idle (1-min load <= qualified maximum), has the qualified free disk and memory, and a
     readable process table (N-11); no other runner process; no consumed ref.
  L3 SLEEP PREVENTION. /usr/bin/caffeinate -i -w <launcher pid>, verified present in
     `pmset -g assertions` as a PreventUserIdleSystemSleep assertion before anything is consumed.
  L4 CONSUMPTION. The create-only ref refs/c11rd/r1-execution-consumed is created in the COMMON git
     directory (it survives removing and re-adding the worktree; review N-6). From this moment the
     one execution is consumed WHATEVER happens next (fail closed; no retry without a new, reviewed
     authorization).
  L5 ONE RUN. The frozen runner is started once, with the sanitized environment, its output going
     to a log OUTSIDE the worktree (the runner's R3 needs a clean namespace); SIGINT, SIGTERM and
     SIGHUP are forwarded to it and waited for.
  L6 IMMEDIATE SEAL. The launcher's next repository action commits evidence/runs/ (artifact,
     .partial, lock -- whatever exists) plus the log, with the runner's exit code and the outcome
     class in the message; the seal commit's parent is the HEAD the runner started from and it
     touches nothing else. The launcher never reads a value of the runs artifact.

Outcome classes (from exit code and file presence only):
  COMPLETED_CERTIFIED       exit 0, artifact present
  COMPLETED_NOT_CERTIFIED   exit 3, artifact present (cap hit or accounting failure)
  CONSUMED_NO_RESULT        lock present, no artifact (crash, kill, interruption)
  REFUSED_BEFORE_LOCK       no lock (the runner refused at R0-R7); still consumed by L4
  ANOMALOUS                 any other combination (sealed as found; the execution review decides)

    python3 -I -S -B c11rd_launch.py --authorization-review-commit SHA [--preflight-only]
--preflight-only runs L1-L2 and reports; it never starts caffeinate, creates the ref or runs anything.
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
FROZEN_CODE = NS / "code"
RUNNER_REL = "code/c11rd_runs.py"
QUAL_ARTIFACT_REL = "evidence/qualification_r1/C11RD_R1_QUALIFICATION.json"
QUAL_REVIEW_REL = "review/C11RD_R1_QUALIFICATION_REVIEW.md"
GRANT_REL = "config/C11RD_GRANT.json"
FREEZE_REL = "protocol/C11RD_FREEZE_R1.json"
RUNS_DIR_REL = "evidence/runs"
LOCK_NAME = "C11RD_EXECUTION.lock"
ARTIFACT_NAME = "C11RD_RUNS.json"
SEALED_LOG_NAME = "C11RD_EXECUTION.log"
CONSUMED_REF = "refs/c11rd/r1-execution-consumed"
GIT = "/usr/bin/git"
CAFFEINATE = "/usr/bin/caffeinate"
PMSET = "/usr/bin/pmset"
VM_STAT = "/usr/bin/vm_stat"
PS = "/bin/ps"
SAFE_ENV_KEYS = ("PATH", "HOME", "LANG", "GIT_NO_REPLACE_OBJECTS")
RUNTIME_ADDED_KEYS = ("LC_CTYPE", "__CF_USER_TEXT_ENCODING")    # PEP 538 locale coercion; macOS CoreFoundation
MARKER = "C11RD_LAUNCH_SANITIZED"


class LaunchRefusal(SystemExit):
    pass


def safe_env() -> dict:
    return {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/var/empty"), "LANG": "C",
            "GIT_NO_REPLACE_OBJECTS": "1"}


def sanitize_process_env() -> dict:
    """Replace this process's environment by the safe set (frozen functions inherit os.environ)."""
    env = safe_env()
    os.environ.clear()
    os.environ.update(env)
    return env


def git(repo, *args, check=False, text=True):
    r = subprocess.run([GIT, "--no-replace-objects", "-c", "core.commitGraph=false", "-C", str(repo), *args],
                       capture_output=True, text=text, env=safe_env())
    if check and r.returncode != 0:
        raise LaunchRefusal(f"REFUSE: git {' '.join(args[:2])} failed: {(r.stderr or '').strip()}")
    return r


def sha256(path) -> str:
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def _frozen():
    """The frozen runner module (its pre-import barrier runs; interpreter must be -I -S -B)."""
    sys.path.insert(0, str(FROZEN_CODE))
    import c11rd_runs as RN
    return RN


def available_memory_kb() -> int | None:
    """free + inactive + speculative pages of `vm_stat` (None if unreadable)."""
    try:
        out = subprocess.run([VM_STAT], capture_output=True, text=True, timeout=30, env=safe_env()).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"page size of (\d+) bytes", out)
    pages = {k: int(v) for k, v in re.findall(r"Pages (free|inactive|speculative):\s+(\d+)\.", out)}
    if not m or set(pages) != {"free", "inactive", "speculative"}:
        return None
    return sum(pages.values()) * int(m.group(1)) // 1024


def other_runner_processes() -> list | None:
    try:
        out = subprocess.run([PS, "-A", "-o", "pid=,command="], capture_output=True, text=True, timeout=30,
                             env=safe_env())
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return [ln.strip() for ln in out.stdout.splitlines() if "c11rd_runs.py" in ln and str(os.getpid()) != ln.split()[0]]


def interpreter_identity() -> dict:
    exe = os.path.realpath(sys.executable)
    return {"executable_realpath": exe, "executable_sha256": sha256(exe), "version": sys.version.split()[0],
            "flags_isolated_nosite_nobytecode": bool(sys.flags.isolated and sys.flags.no_site
                                                     and sys.flags.dont_write_bytecode)}


def load_qualified(repo, ns_rel, grant) -> dict:
    """The qualification artifact AT the grant's qualification commit, from the canonical path."""
    q = grant.get("qualification") or {}
    qc = q.get("commit", "")
    r = git(repo, "show", f"{qc}:{ns_rel}/{QUAL_ARTIFACT_REL}", text=False)
    if r.returncode != 0:
        raise LaunchRefusal("REFUSE L2: the qualification artifact is not at its canonical path in the qualification commit")
    return json.loads(r.stdout)


def preflight(repo, ns_rel, auth_review_commit, qualified, *, runner_path) -> list:
    """Every reason not to launch (empty = launch). Creates nothing."""
    repo, ns = pathlib.Path(repo), pathlib.Path(repo) / ns_rel
    RN = _frozen()
    p = []
    gp = ns / GRANT_REL
    if not gp.is_file() or gp.is_symlink():
        return [f"no grant at {GRANT_REL}"]
    g = json.loads(gp.read_text())
    fz = json.loads((ns / FREEZE_REL).read_text())
    try:
        host = RN.host_identity()
        wt = RN.worktree_identity(repo=repo)
    except SystemExit as exc:
        return [f"identity: {exc}"]
    gprobs = RN.grant_problems(fz, g, host=host, worktree=wt, auth_review_commit=auth_review_commit,
                               repo=repo, ns=ns, code_dir=pathlib.Path(runner_path).parent)
    p += [f"frozen grant check: {x}" for x in gprobs]
    if host != qualified.get("host", {}).get("grant_host"):
        p.append("host identity is not the qualified host")
    if interpreter_identity() != qualified.get("interpreter"):
        p.append("interpreter (realpath, sha256, version, -I -S -B) is not the qualified one")
    if wt != qualified.get("worktree"):
        p.append("worktree identity is not the qualified worktree")
    if g.get("freeze_commit") != qualified.get("freeze_commit"):
        p.append("the grant's freeze commit is not the qualified freeze")
    q = g.get("qualification") or {}
    if q.get("artifact_path") != f"{ns_rel}/{QUAL_ARTIFACT_REL}" or q.get("review_path") != f"{ns_rel}/{QUAL_REVIEW_REL}":
        p.append("the grant's qualification paths are not the canonical ones")
    if sha256(runner_path) != qualified.get("frozen_code_sha256", {}).get(RUNNER_REL):
        p.append("the runner is not the frozen runner")
    lim = qualified.get("launch_limits", {})
    if os.getloadavg()[0] > lim.get("load1_max", -1):
        p.append(f"host not idle: 1-min load {os.getloadavg()[0]:.2f} > {lim.get('load1_max')}")
    if shutil.disk_usage(repo).free < lim.get("disk_free_min_bytes", float("inf")):
        p.append("free disk below the qualified minimum")
    mem = available_memory_kb()
    if mem is None or mem < lim.get("memory_available_min_kb", float("inf")):
        p.append("available memory unreadable or below the qualified minimum")
    if RN.memory_status(os.getpid(), fz["resource_caps"]["rss_kb"])[0] != "OK":
        p.append("process table unreadable (memory accounting impossible)")
    others = other_runner_processes()
    if others is None or others:
        p.append(f"other runner processes or unreadable process list: {others}")
    if git(repo, "rev-parse", "--verify", "-q", CONSUMED_REF).returncode == 0:
        p.append("the execution was already consumed (consumed ref exists)")
    if git(repo, "status", "--porcelain", "--ignored", "--untracked-files=all", "--", ns_rel).stdout.strip():
        p.append("the namespace is not clean")
    return p


def start_sleep_prevention() -> subprocess.Popen:
    c = subprocess.Popen([CAFFEINATE, "-i", "-w", str(os.getpid())], env=safe_env(),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        out = subprocess.run([PMSET, "-g", "assertions"], capture_output=True, text=True, env=safe_env()).stdout
        if re.search(rf"pid {c.pid}\(caffeinate\).*PreventUserIdleSystemSleep", out):
            return c
        time.sleep(0.1)
    c.kill()
    raise LaunchRefusal("REFUSE L3: the sleep-prevention assertion could not be verified")


def consume(repo) -> str:
    head = git(repo, "rev-parse", "HEAD", check=True).stdout.strip()
    r = git(repo, "update-ref", "-m", "C11RD-R1: the one execution is consumed", CONSUMED_REF, head, "")
    if r.returncode != 0:
        raise LaunchRefusal("REFUSE L4: could not create the consumed ref (it may already exist)")
    return head


def run_once(cmd, cwd, log_path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "x") as log:
        child = subprocess.Popen(cmd, cwd=str(cwd), env=safe_env(), stdout=log, stderr=subprocess.STDOUT)

        def forward(signum, _frame):
            try:
                child.send_signal(signum)
            except ProcessLookupError:
                pass
        old = {s: signal.signal(s, forward) for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
        try:
            while True:
                try:
                    return child.wait()
                except InterruptedError:
                    continue
        finally:
            for s, h in old.items():
                signal.signal(s, h)


def outcome_class(rc: int, runs_dir: pathlib.Path) -> str:
    art, lock = (runs_dir / ARTIFACT_NAME).exists(), (runs_dir / LOCK_NAME).exists()
    if rc == 0 and art and lock:
        return "COMPLETED_CERTIFIED"
    if rc == 3 and art and lock:
        return "COMPLETED_NOT_CERTIFIED"
    if lock and not art:
        return "CONSUMED_NO_RESULT"
    if not lock and not art:
        return "REFUSED_BEFORE_LOCK"
    return "ANOMALOUS"


def seal(repo, ns_rel, start_head, rc, log_path) -> dict:
    """The immediate seal: ONLY evidence/runs/ is committed, on top of the runner's start HEAD."""
    repo = pathlib.Path(repo)
    runs_dir = repo / ns_rel / RUNS_DIR_REL
    runs_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(log_path, runs_dir / SEALED_LOG_NAME)
    cls = outcome_class(rc, runs_dir)
    if git(repo, "rev-parse", "HEAD").stdout.strip() != start_head:
        raise LaunchRefusal("SEAL REFUSED: HEAD moved during the execution -- seal by hand, do nothing else")
    git(repo, "add", "-f", "--", f"{ns_rel}/{RUNS_DIR_REL}", check=True)
    staged = git(repo, "diff", "--cached", "--name-only").stdout.split()
    if not staged or any(not s.startswith(f"{ns_rel}/{RUNS_DIR_REL}/") for s in staged):
        raise LaunchRefusal(f"SEAL REFUSED: unexpected staged paths {staged}")
    msg = (f"p5y: K5 C11RD-R1 — SEAL of the one cell-306 D1/D2 execution ({cls}, runner exit {rc})\n\n"
           f"Sealed immediately by the qualified launcher; no value of the runs artifact was read.\n")
    git(repo, "commit", "-q", "-m", msg, check=True)
    new = git(repo, "rev-parse", "HEAD", check=True).stdout.strip()
    parent = git(repo, "rev-parse", f"{new}^", check=True).stdout.strip()
    if parent != start_head:
        raise LaunchRefusal("SEAL ANOMALY: the seal commit's parent is not the start HEAD")
    return {"seal_commit": new, "outcome": cls, "runner_exit": rc, "sealed_paths": staged}


def launch(repo, ns_rel, auth_review_commit, qualified, *, runner_cmd, runner_path, log_dir) -> dict:
    """L1-L6 on the given repository (main() passes the real, frozen values)."""
    sanitize_process_env()
    problems = preflight(repo, ns_rel, auth_review_commit, qualified, runner_path=runner_path)
    if problems:
        raise LaunchRefusal("REFUSE L2: " + "; ".join(problems))
    caff = start_sleep_prevention()
    try:
        start_head = consume(repo)
        log_path = pathlib.Path(log_dir) / f"C11RD_EXECUTION_{start_head[:12]}.log"
        rc = run_once(runner_cmd, pathlib.Path(runner_path).parent, log_path)
        return seal(repo, ns_rel, start_head, rc, log_path)
    finally:
        caff.terminate()


def main(argv=None) -> int:
    if os.environ.get(MARKER) != "1":                       # L1: exactly one re-exec, sanitized
        env = dict(safe_env(), **{MARKER: "1"})
        os.execve(sys.executable, [sys.executable, "-I", "-S", "-B", str(pathlib.Path(__file__).resolve()),
                                   *(argv if argv is not None else sys.argv[1:])], env)
    extra = set(os.environ) - set(SAFE_ENV_KEYS) - set(RUNTIME_ADDED_KEYS) - {MARKER}
    if extra:
        print(f"REFUSE L1: unexpected environment after the sanitizing re-exec: {sorted(extra)}")
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--authorization-review-commit", required=True)
    ap.add_argument("--preflight-only", action="store_true")
    a = ap.parse_args(argv)
    gp = NS / GRANT_REL
    if not gp.is_file():
        print(f"REFUSE L2: no grant at {GRANT_REL}")
        return 2
    grant = json.loads(gp.read_text())
    qualified = load_qualified(REPO, NS_REL, grant)
    runner_path = NS / RUNNER_REL
    if a.preflight_only:
        sanitize_process_env()
        probs = preflight(REPO, NS_REL, a.authorization_review_commit, qualified, runner_path=runner_path)
        print("PREFLIGHT " + ("PASS" if not probs else "REFUSED:\n  - " + "\n  - ".join(probs)))
        return 0 if not probs else 2
    common = pathlib.Path(git(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir", check=True).stdout.strip())
    cmd = [sys.executable, "-I", "-S", "-B", str(runner_path), "--mode", "real",
           "--authorization-review-commit", a.authorization_review_commit]
    out = launch(REPO, NS_REL, a.authorization_review_commit, qualified, runner_cmd=cmd, runner_path=runner_path,
                 log_dir=common / "c11rd_r1")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
