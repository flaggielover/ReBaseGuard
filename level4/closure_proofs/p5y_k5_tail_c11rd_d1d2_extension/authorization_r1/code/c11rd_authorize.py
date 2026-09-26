"""C11RD-R1 AUTHORIZATION -- the prospective authorization of the ONE cell-306 D1/D2 execution of freeze ce5b8595,
qualified by e627d4ec (review e27c2ffd, QUALIFICATION_ACCEPTED), through the qualified launcher (sha256 81ccc048...).

Governance only. It computes nothing scientific, never runs the runner or the comparator, never creates a consumed
ref, a runs file or a log, and never reads an original value. The ONLY file it ever creates in the repository is the
live grant (--make-grant), and only after an AUTHORIZATION_ACCEPTED review of the authorization artifact is committed.

The authorization lineage (the frozen runner and the qualified launcher fix its shape):
  A  the authorization commit: this tool, the verification evidence and the artifact authorization_r1/C11RD_AUTHORIZATION.json,
     which freezes PROSPECTIVELY the exact grant (a template plus the fill rule below) and every launch precondition;
  R  the review commit: parent A, adds exactly review/C11RD_AUTHORIZATION_REVIEW.md holding exactly one AUTHORIZATION_ACCEPTED line;
  G  the grant commit: parent R, adds exactly config/C11RD_GRANT.json = fill(template, A, R). G is THE launch commit: the
     launcher is given --authorization-review-commit G and refuses unless HEAD == G; the frozen runner refuses unless the
     accepted review and the byte-identical grant are present at G. Nothing may be committed after G before the launch.

    python3 -I -S -B c11rd_authorize.py --verify OUT
    python3 -I -S -B c11rd_authorize.py --self-test OUT
    python3 -I -S -B c11rd_authorize.py --compose VERIFY_JSON OUT
    python3 -I -S -B c11rd_authorize.py --make-grant --artifact-commit A --review-commit R
    python3 -I -S -B c11rd_authorize.py --check-grant --authorization-commit G [--out FILE]
    python3 -I -S -B c11rd_authorize.py --launch-preconditions --authorization-commit G
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parents[1]
REPO = NS.parents[2]
NS_REL = "level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension"
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(NS / "qualification_r1q_r1" / "code"))
import c11rd_runs as RN            # noqa: E402  (the frozen runner's pre-import barrier runs: -I -S -B required)
import c11rd_model as MD           # noqa: E402
import c11rd_launch as LA          # noqa: E402  (the qualified launcher; its functions only, never launch())

FREEZE_COMMIT = "ce5b85959a1693525f9e001e7c191516a4ee7d76"
R1_REVIEW_COMMIT = "3c1eff11562638727156f09a9c58b8dc704548a5"
R1_REVIEW_SHA256 = "dd4ccbda22a4c2fde0c40831202d30850b08a88e023bef04326bcccc48914867"
REJECTED_QUAL_COMMIT = "3addf9d3c72d9274813fb5e06486b633a50a133c"
REJECTION_REVIEW_COMMIT = "8933053406b33cb4cc852dfd5b2231f507a552b3"
REJECTION_REVIEW_SHA256 = "d95a2cb62497b7a19aefe1cfd90c23e80230651d9d7aeacc54becf75365baf90"
QUAL_COMMIT = "e627d4ecf402f6d7b827d8ab734b55f4ae41e0e6"
QUAL_REVIEW_COMMIT = "e27c2ffdc55f745e372f0e896d6bedc42a57f341"
QUAL_ARTIFACT_BLOB = "1d79ad42643c543957a5def54699ea557eb82b40"
QUAL_ARTIFACT_SHA256 = "36aa5c68f8761d756bc8592b923825e778d4f971d288b78d74c9d01a159afba4"
QUAL_REVIEW_SHA256 = "be30833558b5ee6b71b2cfb6126ed89a07fb7d00a25999ddf89d701dd3ef689c"
LAUNCHER_SHA256 = "81ccc0482994ba0a4febb8aa5d6ee551f84bb3e66957e06e821250180e11fb48"
QUAL_TOOL_SHA256 = "886679d16d22f6734bf7748dbeaa08452250ecb7685f5ef9d0869f0c99ea0a0d"
QUAL_TOOL_REL = "qualification_r1q_r1/code/c11rd_qualify.py"
LOCAL_MAIN_REF = "c123b9bb8f15d17650545b3fce4aca8a6b61093b"
REMOTE_MAIN_REF = "1cb453826313c189f0bdafd5b84120c1edb74da9"
PYTHON = "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14"
AUTH_DIR_REL = "authorization_r1"
AUTH_ARTIFACT_REL = "authorization_r1/C11RD_AUTHORIZATION.json"
AUTH_TOOL_REL = "authorization_r1/code/c11rd_authorize.py"
AUTH_REVIEW_REL = RN.AUTH_REVIEW_REL                       # review/C11RD_AUTHORIZATION_REVIEW.md (fixed by the frozen runner)
GRANT_REL = RN.GRANT_REL                                   # config/C11RD_GRANT.json (fixed by the frozen runner)
AUTH_PATHS = (f"{AUTH_DIR_REL}/", AUTH_REVIEW_REL, GRANT_REL)
AUTH_SCHEMA = "c11rd.authorization.r1"
LINE_ENDING_KEYS = ("core.autocrlf", "core.safecrlf", "core.eol")
TOKENS = ("AUTHORIZATION_ACCEPTED", "AUTHORIZATION_REJECTED")
CTX = {"repo": REPO}                                       # the self-test points the repository-state helpers at scratch repos


def git(*args, text=True):
    return LA.git(CTX["repo"], *args, text=text)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p) -> str:
    return sha256_bytes(pathlib.Path(p).read_bytes())


def show(commit, rel, text=False):
    r = git("show", f"{commit}:{NS_REL}/{rel}", text=text)
    return r.stdout if r.returncode == 0 else None


def blob(commit, rel):
    return git("rev-parse", "--verify", "-q", f"{commit}:{NS_REL}/{rel}").stdout.strip()


def head():
    return git("rev-parse", "--verify", "-q", "HEAD").stdout.strip()


def parents(c):
    return git("rev-list", "--parents", "-n", "1", c).stdout.split()[1:]


def changed(a, b):
    return git("diff", "--name-only", a, b).stdout.split()


def verdict_counts(text: str, tokens) -> tuple:
    lines = [ln.strip() for ln in text.splitlines()]
    return lines.count(tokens[0]), lines.count(tokens[1])


def qualified() -> dict:
    return json.loads(show(QUAL_COMMIT, LA.QUAL_ARTIFACT_REL))


def freeze() -> dict:
    return json.loads((NS / RN.FREEZE_REL).read_text())


def serialize(grant: dict) -> bytes:
    """The grant's only byte form (the frozen runner compares bytes)."""
    return (json.dumps(grant, indent=1, sort_keys=True) + "\n").encode()


def grant_template(q: dict, fz: dict) -> dict:
    """Every field of the live grant that is known BEFORE the authorization review. The 'authorization' block is
    filled by fill() with the commits and blobs of the reviewed artifact (A) and of the accepted review (R)."""
    lo, hi = MD.cell_block()
    return {
        "campaign": "C11RD", "decision": "ALLOW",
        "target": {"cell": 306, "e_lo": str(lo), "e_hi": str(hi), "constants": ["D1", "D2"]},
        "max_executions": 1,
        "freeze_commit": FREEZE_COMMIT, "freeze_sha256": sha256_file(NS / RN.FREEZE_REL),
        "code_sha256": fz["code_sha256"], "input_bindings": fz["input_bindings"],
        "host": q["host"]["grant_host"], "worktree": q["worktree"],
        "qualification": {"commit": QUAL_COMMIT, "artifact_path": f"{NS_REL}/{LA.QUAL_ARTIFACT_REL}",
                          "artifact_blob": QUAL_ARTIFACT_BLOB, "review_commit": QUAL_REVIEW_COMMIT,
                          "review_path": f"{NS_REL}/{LA.QUAL_REVIEW_REL}"},
        "launcher": {"path": f"{NS_REL}/{LA.LAUNCHER_REL}", "sha256": LAUNCHER_SHA256},
        "launch_branch": q["launch_branch"],
        "authorization": {"artifact_commit": None, "artifact_path": f"{NS_REL}/{AUTH_ARTIFACT_REL}", "artifact_blob": None,
                          "review_commit": None, "review_path": f"{NS_REL}/{AUTH_REVIEW_REL}", "review_blob": None},
        "launch_rule": "the launch commit is the commit G that adds exactly this grant on top of the accepted review "
                       "commit; the qualified launcher is run as `python3.14 -I -S -B <launcher> "
                       "--authorization-review-commit G` with HEAD == G, after the launch preconditions of the "
                       "authorization artifact pass; nothing may be committed after G before the launch",
        "scope": "cell 306, D1 and D2 only; no other cell (307-309 excluded), no comparison, no adoption, no r6, r5 unchanged",
    }


def fill(template: dict, A: str, artifact_blob: str, R: str, review_blob: str) -> dict:
    g = json.loads(json.dumps(template))
    g["authorization"].update(artifact_commit=A, artifact_blob=artifact_blob, review_commit=R, review_blob=review_blob)
    return g


def worktree_gitdirs(cd: pathlib.Path) -> list:
    wt = cd / "worktrees"
    return sorted(p for p in wt.iterdir() if p.is_dir()) if wt.is_dir() else []


def all_lock_files(gd, cd) -> list:
    """Lock files of THIS worktree, the common dir, refs/, and every other worktree of the common dir."""
    found = set(LA.lock_files(gd, cd))
    for w in worktree_gitdirs(cd):
        found |= {str(f) for f in w.glob("*.lock")}
    return sorted(found)


def git_processes() -> list:
    """Running git programs anywhere on the host (any worktree, any client, fsmonitor daemons)."""
    out = subprocess.run(["/bin/ps", "-A", "-o", "pid=,command="], capture_output=True, text=True).stdout
    me = str(os.getpid())
    hits = []
    for ln in out.splitlines():
        parts = ln.split(None, 1)
        if len(parts) < 2 or parts[0] == me:
            continue
        exe = os.path.basename(parts[1].split()[0])
        if exe == "git" or exe.startswith("git-"):
            hits.append(ln.strip()[:200])
    return hits


def line_ending_config() -> dict:
    """Every core.autocrlf / core.safecrlf / core.eol the launcher's git sees (global and system config are off)."""
    r = git("config", "--show-origin", "--get-regexp", r"^core\.(autocrlf|safecrlf|eol)$")
    return {"entries": [ln for ln in r.stdout.splitlines() if ln.strip()], "rc": r.returncode}


def log_dir_state(cd: pathlib.Path) -> dict:
    d = cd / LA.LOG_DIR_NAME
    if not os.path.lexists(d):
        return {"path": str(d), "exists": False, "ok": True}
    ok = d.is_dir() and not d.is_symlink() and os.stat(d).st_uid == os.getuid() and os.access(d, os.W_OK | os.X_OK)
    logs = sorted(p.name for p in d.glob("C11RD_EXECUTION_*.log")) if d.is_dir() else []
    return {"path": str(d), "exists": True, "writable_dir_owned_by_user": ok, "execution_logs": logs, "ok": ok and not logs}


def tmux_state() -> dict:
    """Inside tmux = TMUX is set AND an ancestor process is the tmux server."""
    chain, pid = [], os.getpid()
    for _ in range(64):
        r = subprocess.run(["/bin/ps", "-o", "ppid=,comm=", "-p", str(pid)], capture_output=True, text=True).stdout.split(None, 1)
        if len(r) < 2:
            break
        pid = int(r[0])
        chain.append(os.path.basename(r[1].strip()))
        if pid <= 1:
            break
    installed = [p for p in ("/opt/homebrew/bin/tmux", "/usr/local/bin/tmux", "/usr/bin/tmux") if os.path.exists(p)]
    return {"TMUX_set": bool(os.environ.get("TMUX")), "tmux_ancestor": "tmux" in chain or any(c.startswith("tmux") for c in chain),
            "tmux_installed": installed, "ancestry": chain[:12]}


def maintenance_state(home=None) -> dict:
    home = pathlib.Path(home or os.path.expanduser("~"))
    cfg = subprocess.run(["/usr/bin/git", "config", "--file", str(home / ".gitconfig"), "--get-all", "maintenance.repo"],
                         capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"}).stdout.split()
    agents = [ln for ln in subprocess.run(["/bin/launchctl", "list"], capture_output=True, text=True).stdout.splitlines()
              if "git-scm" in ln or "git.maintenance" in ln]
    return {"global_maintenance_repos": cfg, "launchd_git_agents": agents, "ok": not cfg and not agents}


def runtime_rehash(q: dict) -> list:
    rec = q.get("runtime_files_sha256") or {}
    return [f for f, h in rec.items() if not os.path.isfile(f) or sha256_file(f) != h] if rec else ["<no binding>"]


def repo_state(q: dict, launch_commit: str) -> dict:
    """The seal preconditions exactly as the qualified launcher evaluates them (with launch_commit as the
    authorization commit), plus the checks the launcher does not make (other worktrees, git processes, line
    endings, the log directory, maintenance)."""
    gd, cd = LA.git_dirs(CTX["repo"])
    return {"launcher_seal_preconditions": LA.seal_safety_problems(CTX["repo"], NS_REL, launch_commit, q),
            "lock_files_all_worktrees": all_lock_files(gd, cd), "git_processes": git_processes(),
            "line_endings": line_ending_config(), "config_worktree": (gd / "config.worktree").exists(),
            "log_dir": log_dir_state(cd), "maintenance": maintenance_state(),
            "consumed_ref": git("rev-parse", "--verify", "-q", LA.CONSUMED_REF).stdout.strip(),
            "worktrees": len(worktree_gitdirs(cd)) + 1}


# ================================================================================================================
# --self-test: the checks the qualified launcher does NOT make can fail (planted violations, scratch repos only)
# ================================================================================================================
def self_test() -> dict:
    T = {}
    env = dict(LA.SAFE_ENV)
    G = lambda r, *a: subprocess.run(["/usr/bin/git", "-C", str(r), *a], capture_output=True, text=True, env=env)
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(os.path.realpath(td))
        main_ = td / "main"
        main_.mkdir()
        for a in (["init", "-q", "-b", "main"], ["config", "user.email", "a@example.invalid"], ["config", "user.name", "a"]):
            G(main_, *a)
        (main_ / "f").write_text("x\n")
        G(main_, "add", "f")
        G(main_, "commit", "-qm", "base")
        G(main_, "worktree", "add", "-q", "-b", "launch", str(td / "wt"))
        G(main_, "worktree", "add", "-q", "-b", "other", str(td / "wt2"))
        old = CTX["repo"]
        CTX["repo"] = td / "wt"
        try:
            T["line endings: none in a clean repository (control)"] = line_ending_config()["entries"] == []
            for key, val in (("core.autocrlf", "true"), ("core.safecrlf", "true"), ("core.eol", "crlf")):
                G(main_, "config", key, val)
                T[f"line endings: repository-local {key} detected"] = any(key in e for e in line_ending_config()["entries"])
                G(main_, "config", "--unset", key)
            gd, cd = LA.git_dirs(td / "wt")
            T["locks: none (control)"] = all_lock_files(gd, cd) == []
            other = cd / "worktrees" / "wt2" / "index.lock"
            other.write_text("")
            T["locks: ANOTHER worktree's index.lock detected (the launcher checks only its own)"] = str(other) in all_lock_files(gd, cd)
            other.unlink()
            T["log dir: absent is acceptable (control)"] = log_dir_state(cd)["ok"] is True
            d = cd / LA.LOG_DIR_NAME
            d.mkdir()
            d.chmod(0o555)
            T["log dir: present but NOT writable detected (QR2.N-2)"] = log_dir_state(cd)["ok"] is False
            d.chmod(0o755)
            T["log dir: present and writable is acceptable (control)"] = log_dir_state(cd)["ok"] is True
            (d / "C11RD_EXECUTION_0123456789ab.log").write_text("")
            T["log dir: an existing execution log detected"] = log_dir_state(cd)["ok"] is False
            fake = td / "bin" / "git"
            fake.parent.mkdir()
            fake.symlink_to("/bin/sleep")
            before = git_processes()
            proc = subprocess.Popen([str(fake), "30"])
            try:
                time.sleep(0.3)
                T["git processes: a running git program detected"] = any(str(fake) in x for x in git_processes()) and \
                    not any(str(fake) in x for x in before)
            finally:
                proc.kill()
                proc.wait()
            home = td / "home"
            home.mkdir()
            (home / ".gitconfig").write_text("")
            T["maintenance: none scheduled (control)"] = maintenance_state(home)["global_maintenance_repos"] == []
            (home / ".gitconfig").write_text(f"[maintenance]\n\trepo = {main_}\n")
            T["maintenance: a scheduled git maintenance repository detected"] = maintenance_state(home)["ok"] is False
            tm = tmux_state()
            T["tmux: this process is correctly reported NOT inside tmux (no tmux on the host; a positive control is impossible here)"] = \
                not (tm["TMUX_set"] and tm["tmux_ancestor"])
        finally:
            CTX["repo"] = old
    return {"schema": "c11rd.authorization.selftest.r1", "pass": all(T.values()), "checks": T, "tool_sha256": sha256_file(__file__)}


# ================================================================================================================
# --verify: the authorization-time mechanical verification (read-only)
# ================================================================================================================
def verify() -> dict:
    q, fz = qualified(), freeze()
    H = head()
    C, info = {}, {}
    anc = lambda c: git("merge-base", "--is-ancestor", c, "HEAD").returncode == 0
    C["lineage commits exist and are ancestors of HEAD (ce5b8595, 3c1eff11, 3addf9d3, 89330534, e627d4ec, e27c2ffd)"] = all(
        git("cat-file", "-e", f"{c}^{{commit}}").returncode == 0 and anc(c) for c in
        (FREEZE_COMMIT, R1_REVIEW_COMMIT, REJECTED_QUAL_COMMIT, REJECTION_REVIEW_COMMIT, QUAL_COMMIT, QUAL_REVIEW_COMMIT))
    C["e627d4ec: parent 89330534, adds exactly the 8 qualification files"] = parents(QUAL_COMMIT) == [REJECTION_REVIEW_COMMIT] and \
        len(changed(REJECTION_REVIEW_COMMIT, QUAL_COMMIT)) == 8 and \
        all(p.startswith(f"{NS_REL}/qualification_r1q_r1/") or p.startswith(f"{NS_REL}/evidence/qualification_r1q_r1/")
            or p == f"{NS_REL}/docs/C11RD_R1Q_R1_QUALIFICATION.md" for p in changed(REJECTION_REVIEW_COMMIT, QUAL_COMMIT))
    C["e27c2ffd: parent e627d4ec, adds exactly the qualification review"] = parents(QUAL_REVIEW_COMMIT) == [QUAL_COMMIT] and \
        changed(QUAL_COMMIT, QUAL_REVIEW_COMMIT) == [f"{NS_REL}/{LA.QUAL_REVIEW_REL}"]
    rv_c, rv_h = show(QUAL_REVIEW_COMMIT, LA.QUAL_REVIEW_REL), show("HEAD", LA.QUAL_REVIEW_REL)
    C["qualification review byte-identical at e27c2ffd, HEAD and on disk (sha256 be308335...)"] = rv_c == rv_h == \
        (NS / LA.QUAL_REVIEW_REL).read_bytes() and sha256_bytes(rv_c) == QUAL_REVIEW_SHA256
    C["exactly one QUALIFICATION_ACCEPTED line, no QUALIFICATION_REJECTED line (the frozen runner's parse)"] = \
        verdict_counts(rv_c.decode(), ("QUALIFICATION_ACCEPTED", "QUALIFICATION_REJECTED")) == (1, 0)
    art_c, art_h = show(QUAL_COMMIT, LA.QUAL_ARTIFACT_REL), show("HEAD", LA.QUAL_ARTIFACT_REL)
    C["qualification artifact byte-identical at e627d4ec, HEAD and on disk (blob 1d79ad42, sha256 36aa5c68...)"] = \
        art_c == art_h == (NS / LA.QUAL_ARTIFACT_REL).read_bytes() and sha256_bytes(art_c) == QUAL_ARTIFACT_SHA256 and \
        blob(QUAL_COMMIT, LA.QUAL_ARTIFACT_REL) == blob("HEAD", LA.QUAL_ARTIFACT_REL) == QUAL_ARTIFACT_BLOB
    C["qualification artifact: r1q_r1 schema, PASS, freeze ce5b8595, successor of 3addf9d3, nothing requires a new freeze"] = \
        q["schema"] == LA.QUAL_SCHEMA and q["QUALIFICATION_CLASS"] == "PASS" and q["freeze_commit"] == FREEZE_COMMIT and \
        q["successor_of"]["qualification_commit"] == REJECTED_QUAL_COMMIT and q["requires_new_freeze"] == [] and \
        q["CONTAINS_NO_TARGET_MAGNITUDE"] is True
    lb = show(QUAL_COMMIT, LA.LAUNCHER_REL)
    C["launcher byte-identical at e627d4ec, HEAD and on disk, sha256 81ccc048... = the artifact's binding"] = \
        lb == show("HEAD", LA.LAUNCHER_REL) == (NS / LA.LAUNCHER_REL).read_bytes() and sha256_bytes(lb) == LAUNCHER_SHA256 == \
        q["qualification_code_sha256"][LA.LAUNCHER_REL]
    C["qualification tool sha256 886679d1... = the artifact's binding"] = sha256_file(NS / QUAL_TOOL_REL) == QUAL_TOOL_SHA256 == \
        q["qualification_code_sha256"][QUAL_TOOL_REL]
    C["R1 review, rejection review unchanged (dd4ccbda..., d95a2cb6...)"] = \
        sha256_file(NS / "review/C11RD_R1_PRE_EXECUTION_REVIEW.md") == R1_REVIEW_SHA256 and \
        sha256_file(NS / "review/C11RD_R1_QUALIFICATION_REVIEW.md") == REJECTION_REVIEW_SHA256
    since = changed(QUAL_REVIEW_COMMIT, "HEAD")
    pending = [ln[3:] for ln in git("status", "--porcelain", "--untracked-files=all").stdout.splitlines()]
    foreign = [p for p in since + pending if not any(p.startswith(f"{NS_REL}/{a}") for a in AUTH_PATHS)]
    C["since e27c2ffd only authorization paths changed (committed or pending), nothing outside them"] = foreign == []
    info["changes_since_e27c2ffd"] = sorted(set(since + pending))
    # frozen object
    code = {f"code/{f.name}": sha256_file(f) for f in sorted((NS / "code").iterdir())}
    C["frozen code: exactly the 8 files, sha256 = freeze"] = code == fz["code_sha256"] and len(code) == 8
    C["frozen documents: 8 sha256 = freeze"] = all(sha256_file(NS / r) == h for r, h in fz["document_sha256"].items()) and \
        len(fz["document_sha256"]) == 8
    C["frozen inputs: 8 blobs at HEAD = freeze; C7 sha256 = freeze"] = all(
        git("rev-parse", f"HEAD:{b['path']}").stdout.strip() == b["blob"] for b in fz["input_bindings"].values() if "blob" in b) and \
        sha256_file(REPO / fz["input_bindings"]["c7_gaussian"]["path"]) == fz["input_bindings"]["c7_gaussian"]["sha256"]
    C["freeze JSON and MD byte-identical to ce5b8595; code/, protocol/, theory/ unchanged since"] = \
        show(FREEZE_COMMIT, RN.FREEZE_REL) == (NS / RN.FREEZE_REL).read_bytes() and \
        show(FREEZE_COMMIT, "protocol/C11RD_FREEZE_R1.md") == (NS / "protocol/C11RD_FREEZE_R1.md").read_bytes() and \
        git("diff", "--name-only", FREEZE_COMMIT, "HEAD", "--", f"{NS_REL}/code", f"{NS_REL}/protocol", f"{NS_REL}/theory").stdout.strip() == ""
    lo, hi = MD.cell_block()
    C["target = cell 306 on the frozen block, D1/D2 only; statement table agrees"] = fz["target"] == {
        "cell": 306, "drift_block": ["680769/400000", "17885921/10000000"]} and [str(lo), str(hi)] == fz["target"]["drift_block"] and \
        q["target"]["cell"] == 306 and q["target"]["constants"] == ["D1", "D2"] and q["target"]["drift_block"] == fz["target"]["drift_block"]
    C["scientific parameters and caps exactly as qualified = freeze (43200 s, 2 GiB, 5 workers)"] = \
        q["science"]["frozen_parameters"] == fz["frozen_parameters"] and q["resource_caps"] == fz["resource_caps"] == \
        {"workers": 5, "wall_seconds": 43200, "rss_kb": 2097152} and \
        q["science"]["recurrence"] == fz["F_derivative_recurrence"]["chain"] and \
        q["science"]["D1_formula"] == fz["F_derivative_recurrence"]["propagation"]["D1_j"] and \
        q["science"]["D2_formula"] == fz["F_derivative_recurrence"]["propagation"]["D2_j"] and fz["P_execution_count"] == 1
    # lifecycle absence
    gd, cd = LA.git_dirs(REPO)
    lifecycle = [f"{NS_REL}/{p}" for p in ("evidence/runs", "evidence/comparison", "config", AUTH_REVIEW_REL,
                                           "review/C11RD_EXECUTION_REVIEW.md")]
    try:
        hist = MD.history_commits(lifecycle)
    except MD.ModelError as exc:
        hist = [f"UNREADABLE: {exc}"]
    C["no run, lock, seal, log, comparison, grant or authorization review in any history (frozen reader)"] = hist == []
    C["none on disk; no launcher log directory; no refs/c11rd consumed-execution ref"] = \
        not any((REPO / p).exists() for p in lifecycle) and not (cd / LA.LOG_DIR_NAME).exists() and \
        git("for-each-ref", "refs/c11rd").stdout.strip() == ""
    C["no live grant (config/C11RD_GRANT.json absent on disk and in history)"] = not (NS / GRANT_REL).exists() and hist == []
    main_ = subprocess.run(["/usr/bin/git", "-C", "/Users/suzhe/ReBaseGuard", "rev-parse", "main", "origin/main"],
                           capture_output=True, text=True, env=LA.SAFE_ENV).stdout.split()
    C["LOCAL_MAIN_REF c123b9bb and cached REMOTE_MAIN_REF 1cb45382 recorded separately (not synchronized)"] = \
        main_ == [LOCAL_MAIN_REF, REMOTE_MAIN_REF] and LOCAL_MAIN_REF != REMOTE_MAIN_REF
    # repository state for the seal, the carried-forward conditions
    st = repo_state(q, H)
    info["repo_state"] = st
    only_pending = [x for x in st["launcher_seal_preconditions"]
                    if not (pending and x in ("the worktree is not clean (modified or untracked files)", "the namespace is not clean"))]
    C["launcher seal preconditions hold at HEAD (apart from the pending authorization files themselves)"] = only_pending == []
    C["no line-ending configuration (core.autocrlf / core.safecrlf / core.eol) and no config.worktree"] = \
        st["line_endings"]["entries"] == [] and not st["config_worktree"]
    C["launcher log directory absent (or a writable directory owned by the user, without execution logs)"] = st["log_dir"]["ok"]
    C["no git lock file in any worktree of the common dir, the common dir or refs/"] = st["lock_files_all_worktrees"] == []
    C["no scheduled git maintenance (global maintenance.repo, launchd agents)"] = st["maintenance"]["ok"]
    info["git_processes_now"] = st["git_processes"]
    # qualified bindings still hold on this host
    C["host = the qualified grant host"] = RN.host_identity() == q["host"]["grant_host"]
    C["worktree = the qualified canonical worktree and git common dir; branch = the qualified launch branch"] = \
        RN.worktree_identity() == q["worktree"] and git("symbolic-ref", "-q", "HEAD").stdout.strip() == q["launch_branch"]
    C["interpreter = the qualified stub, running image and libpython"] = LA.interpreter_identity() == q["interpreter"]
    C["every bound interpreter runtime file re-hashes equal"] = runtime_rehash(q) == [] and len(q["runtime_files_sha256"]) == 227
    C["runner guards R0, R1, R4, R5, R6/R7 pass in advance (the launcher's own call)"] = LA.runner_guard_problems(REPO, NS_REL, RN, fz) == []
    # prospective grant: the frozen runner's own check against the template (the only expected findings are the
    # two items that exist only after the review and the grant commit)
    tmpl = grant_template(q, fz)
    probe = fill(tmpl, "0" * 40, "0" * 40, "0" * 40, "0" * 40)
    gp = RN.grant_problems(fz, probe, host=RN.host_identity(), worktree=RN.worktree_identity(), auth_review_commit=H)
    expected = [x for x in gp if "C11RD_AUTHORIZATION_REVIEW.md is not present" in x or "grant is not byte-identical" in x]
    C["prospective grant: the frozen grant check finds ONLY the not-yet-existing review and grant"] = len(gp) == 2 and expected == gp
    info["prospective_frozen_grant_check"] = gp
    try:
        lq = LA.load_qualified(REPO, NS_REL, probe)
        C["prospective grant: the launcher loads the qualification from it (canonical path, r1q_r1 schema)"] = lq == q
    except LA.LaunchRefusal as exc:
        C["prospective grant: the launcher loads the qualification from it (canonical path, r1q_r1 schema)"] = False
        info["load_qualified"] = str(exc)
    C["prospective grant: commit ids, canonical paths, exact freeze, runner hash as the launcher requires"] = \
        LA.commit_id_problems(probe, H) == [] and \
        probe["qualification"]["artifact_path"] == f"{NS_REL}/{LA.QUAL_ARTIFACT_REL}" and \
        probe["qualification"]["review_path"] == f"{NS_REL}/{LA.QUAL_REVIEW_REL}" and probe["freeze_commit"] == q["freeze_commit"] and \
        sha256_file(NS / LA.RUNNER_REL) == q["frozen_code_sha256"][LA.RUNNER_REL]
    info["host_now"] = {"power": LA.power_state(), "load": list(os.getloadavg()), "disk_free": shutil.disk_usage(REPO).free,
                        "memory_available_kb": LA.available_memory_kb(), "tmux": tmux_state()}
    return {"schema": "c11rd.authorization.verify.r1", "HEAD": H, "pass": all(C.values()), "checks": C, "information": info,
            "grant_template_sha256": sha256_bytes(serialize(tmpl)), "tool_sha256": sha256_file(__file__)}


# ================================================================================================================
# --compose: the authorization artifact (prospective; no target magnitude)
# ================================================================================================================
PRECONDITIONS = [
    ("P-01", "HEAD == G, the grant commit (the launch commit), on the qualified launch branch; nothing committed after G",
     "qualified launcher (seal preconditions) + frozen runner R2 + --launch-preconditions"),
    ("P-02", "clean index (== HEAD), no unmerged entry, clean worktree and namespace (ignored files included)",
     "qualified launcher + --launch-preconditions"),
    ("P-03", "no git lock file in this worktree's git dir, the common dir, refs/ or ANY other worktree's git dir; no merge, "
             "rebase, cherry-pick, revert, bisect or sequencer in progress", "qualified launcher (own dirs) + --launch-preconditions (all worktrees)"),
    ("P-04", "no repository-local or worktree core.autocrlf, core.safecrlf or core.eol (review QR2.N-1), no config.worktree, "
             "no git attribute on the seal paths", "--launch-preconditions (+ the launcher checks attributes)"),
    ("P-05", "the launcher log directory <git common dir>/c11rd_r1 is absent, or a writable directory owned by the user holding "
             "no execution log (QR2.N-2)", "--launch-preconditions"),
    ("P-06", "no git activity from any worktree of the common dir, any git client, IDE or fsmonitor daemon during the execution "
             "and the seal: no running git process at launch, no scheduled git maintenance (QR2.N-3)",
     "--launch-preconditions (snapshot at launch) + operator: start no git command anywhere until SEALED or UNSEALED is printed"),
    ("P-07", "the host is otherwise idle: 1-min load <= 2.0, no other runner process", "qualified launcher + --launch-preconditions"),
    ("P-08", "AC power connected", "qualified launcher + --launch-preconditions"),
    ("P-09", "lid open", "qualified launcher + --launch-preconditions"),
    ("P-10", "the launch runs inside tmux (the process is a descendant of the tmux server and TMUX is set) (QR2.N-4)",
     "--launch-preconditions"),
    ("P-11", "no Ctrl-Z / job-control suspension and no Ctrl-C of the pane while the launcher runs; the terminal is not closed "
             "(QR2.N-4)", "operator procedure (not mechanically enforceable)"),
    ("P-12", "qualified sleep prevention active: caffeinate -i -s verified (PreventUserIdleSystemSleep and PreventSystemSleep) "
             "before consumption", "qualified launcher L3"),
    ("P-13", "qualified memory (>= 1 GiB available), disk (>= 2 GiB free), readable process table, interpreter and 227 "
             "runtime files re-hashed, host and worktree identity", "qualified launcher + --launch-preconditions"),
    ("P-14", "the exact launch command with the absolute framework interpreter and -I -S -B only (no -O, no -X) (QR2.N-6)",
     "runbook + qualified launcher L1"),
    ("P-15", "no consumed ref, no runs artifact or lock, no execution log", "qualified launcher + --launch-preconditions"),
]

RUNBOOK = [
    "Install tmux if it is absent (it is absent at authorization time); this is outside the authorization.",
    "Open a NEW tmux session on this host; cd /Users/suzhe/ReBaseGuard-k5c11rd; close every IDE or git client attached to "
    "any worktree of /Users/suzhe/ReBaseGuard/.git and stop any other session's git activity.",
    f"In the tmux pane: {PYTHON} -I -S -B {NS_REL}/{AUTH_TOOL_REL} --launch-preconditions --authorization-commit <G>  "
    "-> must print LAUNCH PRECONDITIONS PASS (exit 0); otherwise stop and fix the cause (nothing is consumed).",
    f"Immediately, in the same pane: {PYTHON} -I -S -B {NS_REL}/{LA.LAUNCHER_REL} --authorization-review-commit <G>",
    "Do not press Ctrl-Z or Ctrl-C, do not close the pane, do not run git anywhere, keep AC power and the lid open, until the "
    "launcher prints SEALED ... or EXECUTION CONSUMED — RESULT UNSEALED (it may take up to 12 h).",
    "SEALED with index_refreshed false: after the blocking lock is gone, run only `git reset -q -- "
    f"{NS_REL}/evidence/runs` (QR2.N-5).",
    "EXECUTION CONSUMED — RESULT UNSEALED (exit 4) or a launcher death: do nothing else; clear the blocking condition; wait until "
    "no c11rd_runs.py process remains; then only the seal-only recovery printed by the launcher. If the launch branch moved "
    "(permanent failure), stop and ask for a separately instructed recovery (QR2.N-5).",
    "Any REFUSE (exit 2): nothing ran. Before retrying, check `git rev-parse --verify -q refs/c11rd/r1-execution-consumed`; if it "
    "exists, the execution IS consumed: only the seal-only recovery (QR2.N-11).",
    "After SEALED: read no value; the next step is a separately instructed execution review, then the comparison.",
]


def compose(v: dict) -> dict:
    q, fz = qualified(), freeze()
    tmpl = grant_template(q, fz)
    return {
        "schema": AUTH_SCHEMA, "campaign": "C11RD-R1 authorization of the ONE cell-306 D1/D2 execution",
        "CONTAINS_NO_TARGET_MAGNITUDE": True, "target_D1_computed": False, "target_D2_computed": False,
        "target_runner_started": False, "live_grant_exists": False,
        "lineage": {"freeze": FREEZE_COMMIT, "pre_execution_review": {"commit": R1_REVIEW_COMMIT, "sha256": R1_REVIEW_SHA256,
                                                                      "verdict": "READY_TO_QUALIFY"},
                    "rejected_qualification": {"commit": REJECTED_QUAL_COMMIT, "review_commit": REJECTION_REVIEW_COMMIT,
                                               "review_sha256": REJECTION_REVIEW_SHA256, "verdict": "QUALIFICATION_REJECTED"},
                    "accepted_qualification": {"commit": QUAL_COMMIT, "artifact": f"{NS_REL}/{LA.QUAL_ARTIFACT_REL}",
                                               "artifact_blob": QUAL_ARTIFACT_BLOB, "artifact_sha256": QUAL_ARTIFACT_SHA256,
                                               "review_commit": QUAL_REVIEW_COMMIT, "review": f"{NS_REL}/{LA.QUAL_REVIEW_REL}",
                                               "review_sha256": QUAL_REVIEW_SHA256, "verdict": "QUALIFICATION_ACCEPTED"}},
        "bindings": {"freeze": {"commit": FREEZE_COMMIT, "json_sha256": sha256_file(NS / RN.FREEZE_REL),
                                "md_sha256": sha256_file(NS / "protocol/C11RD_FREEZE_R1.md")},
                     "frozen_code_sha256": fz["code_sha256"], "input_bindings": fz["input_bindings"],
                     "document_sha256": fz["document_sha256"],
                     "launcher": {"path": f"{NS_REL}/{LA.LAUNCHER_REL}", "sha256": LAUNCHER_SHA256,
                                  "blob": blob(QUAL_COMMIT, LA.LAUNCHER_REL)},
                     "qualification_tool": {"path": f"{NS_REL}/{QUAL_TOOL_REL}", "sha256": QUAL_TOOL_SHA256},
                     "host": q["host"]["grant_host"], "worktree": q["worktree"], "launch_branch": q["launch_branch"],
                     "interpreter": q["interpreter"],
                     "runtime_files": {"count": len(q["runtime_files_sha256"]),
                                       "sha256_of_the_binding": sha256_bytes(json.dumps(q["runtime_files_sha256"], sort_keys=True).encode()),
                                       "source": "the accepted qualification artifact (re-hashed by the launcher at launch)"},
                     "launch_limits": q["launch_limits"]},
        "target": {"cell": 306, "constants": ["D1", "D2"], "drift_block": fz["target"]["drift_block"],
                   "sub_blocks": fz["D_sub_block_partition"]["sub_blocks"], "initial_boxes": 168},
        "science": q["science"], "resource_caps": fz["resource_caps"],
        "execution_semantics": {"count": "exactly ONE execution: freeze P = 1; grant max_executions 1; the runner's permanent "
                                         "lock and history guard R4; the launcher's create-only consumed ref "
                                         f"{LA.CONSUMED_REF} after the preflight and the final gate",
                                "retry": q["retry_semantics"], "seal": q["seal_policy"], "attempt_semantics": q["attempt_semantics"],
                                "entry": "ONLY the qualified launcher; the rejected r1 launcher and direct runner invocation are not permitted"},
        "authorization_lineage": {
            "A": f"the commit of this artifact (adds only {AUTH_DIR_REL}/)",
            "R": f"parent A; adds exactly {NS_REL}/{AUTH_REVIEW_REL}, byte-identical to the fresh reviewer's file, holding exactly "
                 "one AUTHORIZATION_ACCEPTED line and no AUTHORIZATION_REJECTED line",
            "G": f"parent R; adds exactly {NS_REL}/{GRANT_REL} whose bytes are serialize(fill(grant_template, A, blob of this "
                 "artifact at A, R, blob of the review at R)); G is THE launch commit (the authorization commit)",
            "launch_rule": "the launcher is run with --authorization-review-commit G and refuses unless HEAD == G; the frozen "
                           "runner refuses unless the review at G holds exactly one AUTHORIZATION_ACCEPTED line and the grant "
                           "at G is byte-identical to the grant on disk; NOTHING may be committed after G before the launch",
            "why_G_and_not_A": "a grant cannot name the commit that contains it; the grant names A and R, and G is fixed by the "
                               "launch command, the launcher's HEAD check and the frozen runner's byte-identity check"},
        "grant_template": tmpl, "grant_template_sha256": sha256_bytes(serialize(tmpl)),
        "grant_rule": {"fill": "authorization.artifact_commit = A, artifact_blob = git blob of the artifact at A, review_commit "
                               "= R, review_blob = git blob of the review at R; every other field exactly as grant_template",
                       "serialize": "json.dumps(grant, indent=1, sort_keys=True) + newline, UTF-8",
                       "writer": f"{AUTH_TOOL_REL} --make-grant (create-only), then --check-grant after G"},
        "launch_preconditions": [{"id": i, "condition": c, "enforced_by": e} for i, c, e in PRECONDITIONS],
        "launch_command": f"{PYTHON} -I -S -B {NS_REL}/{LA.LAUNCHER_REL} --authorization-review-commit <G>",
        "precondition_command": f"{PYTHON} -I -S -B {NS_REL}/{AUTH_TOOL_REL} --launch-preconditions --authorization-commit <G>",
        "runbook": RUNBOOK,
        "carried_review_notes": {"QR2": "qualification review preserved at e27c2ffd (QUALIFICATION_ACCEPTED)",
                                 "QR2.N-1": "P-04", "QR2.N-2": "P-05", "QR2.N-3": "P-06", "QR2.N-4": "P-10, P-11",
                                 "QR2.N-5": "runbook steps 6-7", "QR2.N-6": "P-14", "QR2.N-7": "no action (leak scans re-run here)",
                                 "QR2.N-8": "accepted residual (launcher-set completeness only)", "QR2.N-9": "accepted residual",
                                 "QR2.N-10": "rule kept: nobody recovers, echoes or pipes the original values",
                                 "QR2.N-11": "runbook step 8"},
        "prohibitions": ["no execution in the authorization round", "no D1/D2 computation outside the one launch",
                         "cells 307-309 not executed or authorized", "no comparison before a separately instructed execution review",
                         "no adoption", "no r6", "r5 unchanged and authoritative", "N9 OPEN, K5 PARTIAL until adjudication",
                         "no frozen scientific file, historical qualification or review artifact changed"],
        "known_unmet_launch_precondition": [] if v["information"]["host_now"]["tmux"]["tmux_installed"] else
            ["P-10: tmux is not installed on this host at authorization time; the launch cannot proceed until it is installed "
             "and the launch runs inside it"],
        "verification": {"file": f"{NS_REL}/{AUTH_DIR_REL}/C11RD_AUTHORIZATION_VERIFY.json", "pass": v["pass"],
                         "checks_passed": sum(bool(x) for x in v["checks"].values()), "checks_total": len(v["checks"]),
                         "entry_HEAD": v["HEAD"], "tool_sha256": v["tool_sha256"]},
        "authorization_tool_sha256": sha256_file(__file__),
        "LOCAL_MAIN_REF": LOCAL_MAIN_REF, "REMOTE_MAIN_REF": REMOTE_MAIN_REF,
    }


# ================================================================================================================
# --make-grant (after AUTHORIZATION_ACCEPTED is committed at R) and --check-grant (after G)
# ================================================================================================================
def _artifact_at(A):
    return show(A, AUTH_ARTIFACT_REL)


def lineage_problems(A: str, R: str) -> list:
    p = []
    if not (LA.is_commit_id(A) and LA.is_commit_id(R)):
        return ["A and R must be full 40-hex commit ids"]
    if parents(R) != [A]:
        p.append("R's only parent is not A")
    if changed(A, R) != [f"{NS_REL}/{AUTH_REVIEW_REL}"]:
        p.append("R does not add exactly the authorization review")
    rv = show(R, AUTH_REVIEW_REL, text=True)
    if rv is None or verdict_counts(rv, TOKENS) != (1, 0):
        p.append("the review at R does not hold exactly one AUTHORIZATION_ACCEPTED line (and no AUTHORIZATION_REJECTED line)")
    art = _artifact_at(A)
    if art is None or json.loads(art).get("schema") != AUTH_SCHEMA:
        p.append("no authorization artifact at A")
    if git("merge-base", "--is-ancestor", QUAL_REVIEW_COMMIT, A).returncode != 0:
        p.append("the accepted qualification review is not an ancestor of A")
    base = git("merge-base", QUAL_REVIEW_COMMIT, A).stdout.strip()
    extra = [x for x in changed(QUAL_REVIEW_COMMIT, A) if not x.startswith(f"{NS_REL}/{AUTH_DIR_REL}/")]
    if base != QUAL_REVIEW_COMMIT or extra:
        p.append(f"A changes more than {AUTH_DIR_REL}/ since e27c2ffd: {extra}")
    return p


def expected_grant(A: str, R: str) -> bytes:
    art = json.loads(_artifact_at(A))
    return serialize(fill(art["grant_template"], A, blob(A, AUTH_ARTIFACT_REL), R, blob(R, AUTH_REVIEW_REL)))


def make_grant(A: str, R: str) -> dict:
    p = lineage_problems(A, R)
    if head() != R:
        p.append("HEAD is not R")
    if git("status", "--porcelain", "--ignored", "--untracked-files=all").stdout.strip():
        p.append("the tree is not clean")
    if git("for-each-ref", "refs/c11rd").stdout.strip() or (NS / GRANT_REL).exists() or (NS / "config").exists():
        p.append("a consumed ref, a grant or config/ already exists")
    art = json.loads(_artifact_at(A))
    if _artifact_at(A) != (NS / AUTH_ARTIFACT_REL).read_bytes() or sha256_bytes(serialize(art["grant_template"])) != art["grant_template_sha256"]:
        p.append("the artifact on disk or its grant template differs from A")
    if p:
        raise SystemExit("REFUSE make-grant: " + "; ".join(p))
    data = expected_grant(A, R)
    (NS / "config").mkdir()
    fd = os.open(NS / GRANT_REL, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    os.write(fd, data)
    os.close(fd)
    return {"grant": f"{NS_REL}/{GRANT_REL}", "sha256": sha256_bytes(data), "A": A, "R": R}


def check_grant(G: str) -> dict:
    C = {}
    R = (parents(G) or [""])[0]
    A = (parents(R) or [""])[0] if R else ""
    C["G, R, A are commit ids; G's only parent is R; R's only parent is A"] = all(LA.is_commit_id(x) for x in (G, R, A)) and \
        len(parents(G)) == 1 and len(parents(R)) == 1
    C["lineage A -> R is the reviewed authorization with exactly one AUTHORIZATION_ACCEPTED"] = lineage_problems(A, R) == []
    C["G adds exactly the grant"] = changed(R, G) == [f"{NS_REL}/{GRANT_REL}"]
    at_g = show(G, GRANT_REL)
    C["the grant at G is byte-identical to the grant on disk and to the artifact's rule fill(template, A, R)"] = \
        at_g is not None and at_g == (NS / GRANT_REL).read_bytes() == expected_grant(A, R)
    C["HEAD == G, clean tree, no consumed ref"] = head() == G and \
        not git("status", "--porcelain", "--ignored", "--untracked-files=all").stdout.strip() and \
        not git("for-each-ref", "refs/c11rd").stdout.strip()
    g = json.loads(at_g) if at_g else {}
    gp = RN.grant_problems(freeze(), g, host=RN.host_identity(), worktree=RN.worktree_identity(), auth_review_commit=G)
    C["the frozen runner's grant check (R2) at HEAD == G finds no problem"] = gp == []
    try:
        C["the launcher loads the accepted qualification through the grant"] = LA.load_qualified(REPO, NS_REL, g) == qualified()
    except LA.LaunchRefusal:
        C["the launcher loads the accepted qualification through the grant"] = False
    pf = subprocess.run([PYTHON, "-I", "-S", "-B", str(NS / LA.LAUNCHER_REL), "--authorization-review-commit", G, "--preflight-only"],
                        capture_output=True, text=True, env=dict(LA.SAFE_ENV), timeout=900)
    items = [ln.strip()[2:] for ln in pf.stdout.splitlines() if ln.strip().startswith("- ")]
    volatile = ("host not idle", "not on AC power", "the lid is not open", "available memory", "free disk")
    C["the qualified launcher's --preflight-only passes apart from host-volatile conditions (it creates nothing)"] = \
        pf.stdout.startswith("PREFLIGHT") and all(any(v in x for v in volatile) for x in items)
    return {"G": G, "R": R, "A": A, "pass": all(C.values()), "checks": C, "frozen_grant_problems": gp,
            "launcher_preflight_only": {"rc": pf.returncode, "stdout": pf.stdout.strip()[:3000]},
            "grant_sha256": sha256_bytes(at_g) if at_g else None}


# ================================================================================================================
# --launch-preconditions (at launch, inside tmux; read-only)
# ================================================================================================================
def launch_preconditions(G: str) -> tuple:
    q = qualified()
    P = {}
    if not LA.is_commit_id(G):
        return False, {"P-01": "G is not a full 40-hex commit id"}
    lim = q["launch_limits"]
    st = repo_state(q, G)
    P["P-01 HEAD == G (grant commit), launch branch, G adds exactly the grant, nothing after G"] = head() == G and \
        git("symbolic-ref", "-q", "HEAD").stdout.strip() == q["launch_branch"] and changed((parents(G) or [""])[0], G) == [f"{NS_REL}/{GRANT_REL}"]
    P["P-02/P-03 the launcher's seal preconditions hold"] = st["launcher_seal_preconditions"] == []
    P["P-03 no lock file in any worktree of the common dir"] = st["lock_files_all_worktrees"] == []
    P["P-04 no core.autocrlf / core.safecrlf / core.eol, no config.worktree"] = st["line_endings"]["entries"] == [] and not st["config_worktree"]
    P["P-05 launcher log directory absent or writable, no execution log"] = st["log_dir"]["ok"]
    P["P-06 no running git process anywhere; no scheduled git maintenance"] = st["git_processes"] == [] and st["maintenance"]["ok"]
    pw = LA.power_state()
    P["P-07 idle host (1-min load <= qualified maximum) and no runner process"] = os.getloadavg()[0] <= lim["load1_max"] and \
        LA.other_runner_processes() == []
    P["P-08 AC power"] = pw["ac_power"] is True
    P["P-09 lid open"] = pw["lid_open"] is True
    tm = tmux_state()
    P["P-10 inside tmux"] = tm["TMUX_set"] and tm["tmux_ancestor"]
    mem = LA.available_memory_kb()
    P["P-13 memory, disk, runtime files, host, worktree"] = mem is not None and mem >= lim["memory_available_min_kb"] and \
        shutil.disk_usage(REPO).free >= lim["disk_free_min_bytes"] and runtime_rehash(q) == [] and \
        RN.host_identity() == q["host"]["grant_host"] and RN.worktree_identity() == q["worktree"]
    P["P-15 no consumed ref, no runs artifact or lock"] = st["consumed_ref"] == "" and not (NS / "evidence/runs").exists()
    detail = {"repo_state": st, "power": pw, "tmux": tm, "load": list(os.getloadavg()), "memory_available_kb": mem}
    return all(P.values()), {"checks": P, "detail": detail}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify")
    ap.add_argument("--self-test")
    ap.add_argument("--compose", nargs=2, metavar=("VERIFY_JSON", "OUT"))
    ap.add_argument("--make-grant", action="store_true")
    ap.add_argument("--check-grant", action="store_true")
    ap.add_argument("--launch-preconditions", action="store_true")
    ap.add_argument("--artifact-commit")
    ap.add_argument("--review-commit")
    ap.add_argument("--authorization-commit")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.verify:
        v = verify()
        pathlib.Path(a.verify).write_text(json.dumps(v, indent=1, sort_keys=True, default=str) + "\n")
        print(f"VERIFY {'PASS' if v['pass'] else 'FAIL'} ({sum(bool(x) for x in v['checks'].values())}/{len(v['checks'])})")
        for k, x in v["checks"].items():
            if not x:
                print("  FAIL", k)
        return 0 if v["pass"] else 1
    if a.self_test:
        t = self_test()
        pathlib.Path(a.self_test).write_text(json.dumps(t, indent=1, sort_keys=True) + "\n")
        print(f"SELF-TEST {'PASS' if t['pass'] else 'FAIL'} ({sum(t['checks'].values())}/{len(t['checks'])})")
        for k, x in t["checks"].items():
            print(("  ok   " if x else "  FAIL ") + k)
        return 0 if t["pass"] else 1
    if a.compose:
        v = json.loads(pathlib.Path(a.compose[0]).read_text())
        st = json.loads((pathlib.Path(a.compose[0]).parent / "C11RD_AUTHORIZATION_SELFTEST.json").read_text())
        if not (v["pass"] and st["pass"]) or v["tool_sha256"] != sha256_file(__file__) or st["tool_sha256"] != sha256_file(__file__):
            raise SystemExit("REFUSE compose: the verification or the self-test did not pass, or came from another tool version")
        art = compose(v)
        art["self_test"] = {"file": f"{NS_REL}/{AUTH_DIR_REL}/C11RD_AUTHORIZATION_SELFTEST.json", "pass": st["pass"],
                            "checks_passed": sum(st["checks"].values()), "checks_total": len(st["checks"])}
        if art["grant_template_sha256"] != v["grant_template_sha256"]:
            raise SystemExit("REFUSE compose: the grant template changed since the verification")
        pathlib.Path(a.compose[1]).write_text(json.dumps(art, indent=1, sort_keys=True, default=str) + "\n")
        print("authorization artifact written")
        return 0
    if a.make_grant:
        print(json.dumps(make_grant(a.artifact_commit or "", a.review_commit or "")))
        return 0
    if a.check_grant:
        r = check_grant(a.authorization_commit or "")
        text = json.dumps(r, indent=1, sort_keys=True, default=str) + "\n"
        if a.out:
            pathlib.Path(a.out).write_text(text)
        print(f"CHECK-GRANT {'PASS' if r['pass'] else 'FAIL'}")
        for k, x in r["checks"].items():
            print(("  ok   " if x else "  FAIL ") + k)
        return 0 if r["pass"] else 1
    if a.launch_preconditions:
        ok, rep = launch_preconditions(a.authorization_commit or "")
        for k, x in rep["checks"].items() if isinstance(rep.get("checks"), dict) else rep.items():
            print(("  ok   " if x is True else "  FAIL ") + k)
        print("LAUNCH PRECONDITIONS " + ("PASS" if ok else "NOT MET -- do NOT launch (nothing has been consumed)"))
        if ok:
            print("  Next, in this pane, immediately: " + f"{PYTHON} -I -S -B {NS_REL}/{LA.LAUNCHER_REL} --authorization-review-commit {a.authorization_commit}")
            print("  Then: no Ctrl-Z, no Ctrl-C, keep the pane open, no git anywhere, until SEALED or UNSEALED is printed.")
        return 0 if ok else 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
