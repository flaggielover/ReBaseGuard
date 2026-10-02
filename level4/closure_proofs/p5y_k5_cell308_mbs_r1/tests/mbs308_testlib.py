"""MB-S r1 tests: sandboxes, grant chains, the child harness and the runner. Target-free.

Every state-changing test runs in a `git clone --shared` SANDBOX (own refs, index and worktree; objects shared read-only
through alternates), as MB r1's tests/test_mb308_flows.py does: no marker, journal, pending, checkpoint or seal ref and
no commit is ever created in the real repository. The sandbox checks out the real HEAD on branch
p5y-k5-cell308-mbs-r1, copies this namespace in (or a MUTATED copy of its code, for the mutant runner), plants MB r1's
recorded state (its marker -> afa93072 and its branch) in the sandbox, and commits one synthetic freeze. Grant chains
are synthetic sandbox commits. The driver runs in CHILD processes (tests/mbs308_child.py) so that fault points can
os._exit / SIGKILL it for real; its evaluator is the SYNTHETIC one (tests/mbs308_synth.py), never cell 308.
"""
from __future__ import annotations

import atexit
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve()
NSS = HERE.parents[1]
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
NS_REL = CP + "p5y_k5_cell308_mbs_r1"
NSF_REL = CP + "p5y_k5_cell308_mb_r1"
BRANCH = "p5y-k5-cell308-mbs-r1"
PY = "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14"
GENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "HOME": os.environ.get("HOME", "/var/empty")}
SCRATCH = Path(os.environ.get("MBS308_SCRATCH", "/private/tmp/claude-501/-Users-suzhe-ReBaseGuard/"
                              "d1135746-7699-4331-8dd2-9addf63a6def/scratchpad/builderMBS"))
MBR1_MARKER = "refs/p5y-k5-cell308-mb-r1/target-consumed"
MBR1_TARGET = "afa930727d084a5b70e6b85d30ca8f34c0e8ae74"
PREFIX = "refs/p5y-k5-cell308-mbs-r1/"
BASE = "21e99cf05d60b985e33f337aa4c5a7fd1507402a"


def code_dir() -> Path:
    """The code under test: the namespace's own, or a mutated copy (mutant runner)."""
    return Path(os.environ.get("MBS308_TEST_CODE_DIR", str(NSS / "code")))


def g(root: Path, *args, check=True, text=True):
    p = subprocess.run(["/usr/bin/git", "-C", str(root), *args], capture_output=True, text=text, env=GENV,
                       stdin=subprocess.DEVNULL)
    if check and p.returncode:
        raise RuntimeError(f"git {args[:3]} failed: {(p.stderr if text else p.stderr.decode())[:300]}")
    return p.stdout.strip() if text else p.stdout


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


BASE_STORE = Path(os.environ.get("MBS308_BASE_STORE", "/private/tmp/claude-501/-Users-suzhe-ReBaseGuard/"
                                  "d1135746-7699-4331-8dd2-9addf63a6def/scratchpad/builderMBS/base_store.git"))


def base_store() -> Path:
    """ONE bare `git clone --no-local` of the real repository: a SEPARATE object store. Every sandbox is a
    `--shared` clone of THIS store, never of the real one, so no sandbox write (and no git "freshening" of an object
    that already exists) can ever touch the real object store. The calling process is recorded as a BORROWER inside
    the store before it uses it (borrow_begin; protocol section 8.2)."""
    if not (BASE_STORE / "HEAD").exists():
        subprocess.run(["/usr/bin/git", "clone", "-q", "--bare", "--no-local", str(REPO), str(BASE_STORE)], check=True,
                       env=GENV, capture_output=True)
    if (BASE_STORE / "objects/info/alternates").exists():
        raise RuntimeError("the base store must not borrow objects from the real repository")
    borrow_begin()
    if g(BASE_STORE, "cat-file", "-t", BASE, check=False) != "commit":
        raise RuntimeError("the base store lacks the base commit")
    return BASE_STORE


# ------------------------------------------------------------------ the base store's borrower record (protocol 8.2)
_BORROW: dict = {}


def borrow_begin() -> Path:
    """Record THIS process, once, as a borrower INSIDE the base store (state ACTIVE), before it clones from it or reads
    its objects: the scratch-lifecycle gate never deletes a base store with a live or unfinished borrower, in
    whichever scratch root the borrower's sandboxes lie (reviewQ6 F-2). NOT best effort: a store that cannot record
    its borrower is not used (the exception propagates and no sandbox is made). The record is marked FINISHED when the
    process exits normally; a killed process leaves it ACTIVE and the store is then kept until a human deletes it."""
    if _BORROW.get("pid") != os.getpid():
        rec = infra_scratch().begin_borrow(BASE_STORE, f"tests {Path(sys.argv[0]).name}")
        _BORROW.clear()
        _BORROW.update({"pid": os.getpid(), "record": rec})
        atexit.register(borrow_finish)
    return _BORROW["record"]


def borrow_clone(clone) -> None:
    """Name a sandbox clone this process is about to make from the base store, in its borrower record (mandatory, as
    borrow_begin): the store is kept while that path holds a clone that borrows from it."""
    infra_scratch().borrow_clone(borrow_begin(), clone)


def borrow_finish() -> None:
    """Mark this process's borrower record FINISHED (at exit). A forked child never finishes its parent's record."""
    if _BORROW.get("pid") == os.getpid():
        try:
            infra_scratch().finish_borrow(_BORROW["record"])
        except Exception:                                               # noqa: BLE001 (it stays ACTIVE: the safe side)
            pass


# ------------------------------------------------------------------ the S1 owner records of the grant (brief 54, C1)
_OWNER_TEXTS: dict = {}


def s1_owner_records() -> tuple:
    """The S1_OWNER_RECORDS of the driver under test, read from its TEXT (the driver is never imported here):
    ((record, research path, research commit, byte length, sha256), ...) in the grant's fixed order."""
    import ast
    for n in ast.parse((code_dir() / "mbs308_driver.py").read_text()).body:
        if isinstance(n, ast.Assign) and [getattr(t, "id", None) for t in n.targets] == ["S1_OWNER_RECORDS"]:
            return ast.literal_eval(n.value)
    raise RuntimeError("the driver names no S1_OWNER_RECORDS")


def owner_record_text(commit: str, path: str) -> str:
    """The exact committed bytes of one owner record, read from the BASE STORE at its research commit (never from a
    worktree file). A base store cloned before the record was committed must be rebuilt."""
    key = (commit, path)
    if key not in _OWNER_TEXTS:
        p = subprocess.run(["/usr/bin/git", "-C", str(base_store()), "cat-file", "blob", f"{commit}:{path}"],
                           capture_output=True, env=GENV, stdin=subprocess.DEVNULL)
        if p.returncode != 0:
            raise RuntimeError(f"the base store lacks the owner record {commit[:8]}:{path} (rebuild the base store)")
        _OWNER_TEXTS[key] = p.stdout.decode("utf-8")
    return _OWNER_TEXTS[key]


def s1_index_sha256(rows) -> str:
    return sha(json.dumps([list(r) for r in rows], sort_keys=True, separators=(",", ":")).encode())


def s1_ruling() -> dict:
    """The grant field `user_ruling_s1` as the frozen protocol defines it: the index of ALL the complete owner records
    (original, supplement 1, supplement 2), each with its research path, commit, byte length, sha256 and complete verbatim text, plus
    the index's own digest and reaffirms_c4. The texts are the user's committed bytes; only the grant around them is a
    sandbox stand-in."""
    recs, rows = [], []
    for name, path, commit, _nbytes, _digest in s1_owner_records():
        text = owner_record_text(commit, path)
        raw = text.encode()
        recs.append({"record": name, "path": path, "commit": commit, "bytes": len(raw), "sha256": sha(raw),
                     "verbatim": text})
        rows.append((name, path, commit, len(raw), sha(raw)))
    return {"records": recs, "index_sha256": s1_index_sha256(rows), "reaffirms_c4": True}


def s1_reindex(ur: dict) -> dict:
    """A planted ruling made SELF-CONSISTENT again (each entry's bytes / sha256 recomputed from its text, the index
    digest from the entries): what a forger who controls the grant would write."""
    recs = []
    for r in ur["records"]:
        raw = r["verbatim"].encode()
        recs.append(dict(r, bytes=len(raw), sha256=sha(raw)))
    rows = [(r["record"], r["path"], r["commit"], r["bytes"], r["sha256"]) for r in recs]
    return dict(ur, records=recs, index_sha256=s1_index_sha256(rows))


class Sandbox:
    def __init__(self, tmp: Path):
        tmp.mkdir(parents=True, exist_ok=True)
        root = tmp / "sbx"
        if root.exists():
            shutil.rmtree(root)
        store = base_store()
        borrow_clone(root)                   # recorded in the store BEFORE the clone exists (protocol section 8.2)
        subprocess.run(["/usr/bin/git", "clone", "-q", "--shared", "--no-checkout", str(store), str(root)],
                       check=True, env=GENV, capture_output=True)
        self.root = root.resolve()
        self.tmp = tmp
        if g(self.root, "rev-parse", "--path-format=absolute", "--git-common-dir") == \
                g(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir"):
            raise RuntimeError("the sandbox shares the real common dir")
        alt = (self.root / ".git/objects/info/alternates").read_text().split()
        real_objects = str(Path(g(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve() / "objects")
        if any(str(Path(a).resolve()) == real_objects for a in alt) or \
                [str(Path(a).resolve()) for a in alt] != [str((BASE_STORE / "objects").resolve())]:
            raise RuntimeError("the sandbox must borrow objects from the base store only")
        g(self.root, "config", "user.name", "sandbox")
        g(self.root, "config", "user.email", "sandbox@invalid")
        g(self.root, "checkout", "-q", "-B", BRANCH, BASE)
        # MB r1's recorded state, planted IN THE SANDBOX (GC-8 asserts it)
        g(self.root, "update-ref", MBR1_MARKER, MBR1_TARGET)
        g(self.root, "branch", "-f", "p5y-k5-cell308-mb-r1", BASE)
        self.mbr1_git_dir = tmp / "mbr1_gitdir"
        self.mbr1_git_dir.mkdir(exist_ok=True)
        dst = self.root / NS_REL
        for d in ("tests", "protocol"):
            if (NSS / d).is_dir():
                shutil.copytree(NSS / d, dst / d, ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)
        shutil.copytree(code_dir(), dst / "code", ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)
        (dst / "protocol").mkdir(parents=True, exist_ok=True)
        (dst / "protocol/MBS308_FREEZE.json").write_text(json.dumps({"schema": "sandbox-manifest"}) + "\n")
        g(self.root, "add", "-f", NS_REL)
        g(self.root, "commit", "-q", "-m", "sandbox: synthetic freeze of the MB-S namespace (never in the real repo)")
        self.freeze = g(self.root, "rev-parse", "HEAD")
        self.driver = dst / "code/mbs308_driver.py"
        self.driver_sha = sha(self.driver.read_bytes())
        self.chain = None

    def p(self, rel: str) -> Path:
        return self.root / rel

    def write(self, rel: str, text: str) -> None:
        self.p(rel).parent.mkdir(parents=True, exist_ok=True)
        self.p(rel).write_text(text)

    def commit(self, rels: list, msg: str) -> str:
        g(self.root, "add", "-f", *rels)
        g(self.root, "commit", "-q", "-m", msg)
        return g(self.root, "rev-parse", "HEAD")

    def git_dir(self) -> Path:
        return Path(g(self.root, "rev-parse", "--path-format=absolute", "--git-dir"))

    def spool(self) -> Path:
        return self.git_dir() / "mbs308-spool"

    def common_dir(self) -> Path:
        return Path(g(self.root, "rev-parse", "--path-format=absolute", "--git-common-dir"))

    def lock_path(self, rel: str) -> Path:
        return self.common_dir() / rel

    def plant_lock(self, rel: str) -> Path:
        """A stale git lockfile, as a reset inside a ref write leaves it (sandbox only)."""
        p = self.lock_path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"0" * 40 + b"\n")
        return p

    def locks_aside(self) -> list:
        d = self.spool() / "git-locks-aside"
        return sorted(x.name for x in d.iterdir()) if d.is_dir() else []

    def wipe_state(self) -> None:
        cd = self.common_dir()               # planted git lockfiles first (they block ref deletion)
        for lk in list((cd / PREFIX.rstrip("/")).glob("*.lock")) + [cd / ("refs/heads/" + BRANCH + ".lock"),
                                                                    cd / "packed-refs.lock"]:
            if lk.exists():
                lk.unlink()
        for ref in g(self.root, "for-each-ref", "--format=%(refname)").split():
            if ref.startswith(PREFIX) or ref.startswith("refs/mbs308-test"):
                g(self.root, "update-ref", "-d", ref)
        for ref in g(self.root, "for-each-ref", "--format=%(refname)", "refs/p5y-k5-cell308-mb-r1/").split():
            if ref != MBR1_MARKER:
                g(self.root, "update-ref", "-d", ref)
        g(self.root, "update-ref", MBR1_MARKER, MBR1_TARGET)
        if self.spool().exists():
            shutil.rmtree(self.spool())
        for f in self.mbr1_git_dir.iterdir():
            f.unlink()
        ev = self.p(NS_REL + "/evidence")
        if ev.is_symlink():
            ev.unlink()

    def grant_chain(self, *, driver_sha=None, review_line="QUALIFICATION_ACCEPTED", ruling=True) -> dict:
        """reset to the freeze and build freeze -> qualification -> review -> grant (all synthetic sandbox commits)."""
        self.wipe_state()
        g(self.root, "checkout", "-q", "-f", BRANCH)
        g(self.root, "reset", "-q", "--hard", self.freeze)
        g(self.root, "clean", "-qfdx", "--", NS_REL)
        q = {"schema": "sandbox-synthetic", "pass": True, "review_mode": False, "freeze_commit": self.freeze}
        self.write(NS_REL + "/qualification/MBS308_QUALIFICATION.json", json.dumps(q))
        qc = self.commit([NS_REL + "/qualification/MBS308_QUALIFICATION.json"], "sandbox: qualification (synthetic)")
        self.write(NS_REL + "/review/MBS308_QUALIFICATION_REVIEW.md", f"# sandbox review (synthetic)\n{review_line}\n")
        rc = self.commit([NS_REL + "/review/MBS308_QUALIFICATION_REVIEW.md"], "sandbox: review (synthetic)")
        # ruling: True = every complete owner record as the frozen protocol defines the field; a dict = a planted
        # `user_ruling_s1` (the C1 controls); False / None = no ruling. The grant itself is a sandbox stand-in.
        ur = s1_ruling() if ruling is True else (ruling if isinstance(ruling, dict) else None)
        grant = {"schema": "rebaseguard.p5y.k5.cell308-mbs-r1.grant.v1", "exactly_once": True, "cell": 308,
                 "route": "MB-S", "closure_only": True, "driver_sha256": driver_sha or self.driver_sha,
                 "freeze_commit": self.freeze, "qualification_commit": qc, "qualification_review_commit": rc,
                 "input_manifest_sha256": sha(self.p(NS_REL + "/protocol/MBS308_FREEZE.json").read_bytes()),
                 "user_ruling_s1": ur}
        self.write(NS_REL + "/authorization/MBS308_GRANT.json", json.dumps(grant))
        gc = self.commit([NS_REL + "/authorization/MBS308_GRANT.json"], "sandbox: grant (synthetic)")
        self.chain = {"qual": qc, "review": rc, "grant": gc}
        return self.chain

    # ---- observations (names / ids / counts only; never checkpoint content)
    def refs(self) -> dict:
        out = {}
        for ln in g(self.root, "for-each-ref", "--format=%(refname) %(objectname)", PREFIX).splitlines():
            r, o = ln.split()
            out[r] = o
        return out

    def ckpt_names(self) -> list:
        t = g(self.root, "rev-parse", "-q", "--verify", PREFIX + "ckpt", check=False)
        if not t:
            return []
        return sorted(ln.split("\t", 1)[1] for ln in g(self.root, "ls-tree", t).splitlines())

    def sealed_record(self) -> dict | None:
        raw = subprocess.run(["/usr/bin/git", "-C", str(self.root), "show",
                              f"HEAD:{NS_REL}/evidence/execution/MBS308_CELL308_RESULT.json"], capture_output=True,
                             env=GENV).stdout
        return json.loads(raw) if raw else None

    def sealed_raw(self) -> bytes:
        return subprocess.run(["/usr/bin/git", "-C", str(self.root), "show",
                               f"HEAD:{NS_REL}/evidence/execution/MBS308_CELL308_RESULT.json"], capture_output=True,
                              env=GENV).stdout

    def materialized(self) -> Path:
        return self.p(NS_REL + "/evidence/execution/MBS308_CELL308_RESULT.json")


# ------------------------------------------------------------------ the child harness
def child(sb: Sandbox, action: str, spec: dict | None = None, timeout: int = 300) -> dict:
    """Run the sandbox driver's `action` in a child process (tests/mbs308_child.py). Returns {"rc", "signal",
    "out" (the child's JSON line or None), "stdout"}."""
    spec = dict(spec or {})
    spec.setdefault("mbr1_git_dir", str(sb.mbr1_git_dir))
    spec.setdefault("joblog", str(sb.tmp / "joblog.txt"))
    env = dict(GENV)
    env["MBS308_TEST_CHILD"] = "1"
    env["MBS308_TEST_JOBLOG"] = spec["joblog"]
    for k in ("worker_die", "job_sleep", "alloc_mb"):
        if spec.get(k) is not None:
            env[f"MBS308_TEST_{k.upper()}"] = str(spec[k])
    env["MBS308_TEST_DIEFLAG"] = str(sb.tmp / "worker_died.flag")
    # stdout / stderr go to FILES, and only the child's own exit is awaited: a stray grandchild (an orphaned worker, a
    # resource tracker) holding an inherited descriptor can never hang the test
    of, ef = sb.tmp / "child.out", sb.tmp / "child.err"
    with open(of, "wb") as fo, open(ef, "wb") as fe:
        proc = subprocess.Popen([PY, "-I", "-S", "-B", str(sb.p(NS_REL + "/tests/mbs308_child.py")), str(sb.root),
                                 action, json.dumps(spec)], stdout=fo, stderr=fe, env=env, stdin=subprocess.DEVNULL)
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    if proc.returncode < 0 or proc.returncode == 86:
        time.sleep(1.6)            # a killed driver's orphaned workers exit within 1 s (their parent-death watch)
    p = subprocess.CompletedProcess(proc.args, proc.returncode, of.read_text(errors="replace"),
                                    ef.read_text(errors="replace"))
    out = None
    for ln in reversed(p.stdout.splitlines()):
        if ln.startswith("{") and ln.endswith("}"):
            try:
                out = json.loads(ln)
                break
            except ValueError:
                pass
    detail = None
    for ln in reversed(p.stderr.splitlines()):
        if ln.startswith("{") and ln.endswith("}"):
            try:
                detail = json.loads(ln).get("detail")
                break
            except ValueError:
                pass
    rc = p.returncode
    return {"rc": rc, "signal": -rc if rc < 0 else None, "out": out, "stdout": p.stdout[-1500:],
            "stderr": p.stderr[-1500:], "detail": detail}


def joblog_counts(path) -> dict:
    out: dict = {}
    try:
        for ln in Path(path).read_text().splitlines():
            if ln.strip():
                out[ln.strip()] = out.get(ln.strip(), 0) + 1
    except FileNotFoundError:
        pass
    return out


def certified_bytes(rec: dict) -> bytes:
    """The certified part of a sealed record: the target (stage 1 / stage 2 / decision), canonical JSON."""
    return json.dumps(rec.get("target"), sort_keys=True, separators=(",", ":")).encode()


class Helper:
    """A live helper process (`sleep`) whose identity plays a live driver in classifier tests."""

    def __init__(self, seconds: int = 300):
        self.p = subprocess.Popen(["/bin/sleep", str(seconds)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
        time.sleep(0.3)

    def kill(self) -> None:
        if self.p.poll() is None:
            self.p.kill()
            self.p.wait()


# ------------------------------------------------------------------ the scratch lifecycle (brief 50)
def infra_scratch():
    """The namespace's OWN code/mbs308_scratch.py (never a mutated copy), loaded under a private module name: the
    lifecycle records it writes are what the mutant runner's and the verifier's cleanup rely on."""
    import importlib.util
    name = "_mbs308_scratch_infra"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, NSS / "code" / "mbs308_scratch.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def lifecycle_begin(purpose: str):
    """Record this process as a user of SCRATCH (ACTIVE). Best effort: without a record the root stays ACTIVE (never
    cleaned), which is the safe side."""
    try:
        return infra_scratch().begin(SCRATCH, purpose)
    except Exception:                                                   # noqa: BLE001
        return None


def lifecycle_finish(record) -> None:
    if record is not None:
        try:
            infra_scratch().finish(record)
        except Exception:                                               # noqa: BLE001
            pass


# ------------------------------------------------------------------ the runner
def run_tests(module_globals: dict, names: list | None = None, out_path: str | None = None) -> int:
    rec = lifecycle_begin(f"tests {Path(str(module_globals.get('__file__'))).name}")
    try:
        return _run_tests(module_globals, names, out_path)
    finally:
        lifecycle_finish(rec)


def _run_tests(module_globals: dict, names: list | None = None, out_path: str | None = None) -> int:
    tests = {k: v for k, v in module_globals.items() if k.startswith("t_") and callable(v)}
    sel = names or list(tests)
    res = {}
    t_all = time.time()
    for n in sel:
        t0 = time.time()
        try:
            r = tests[n]()
            ok = bool(r.get("ok")) if isinstance(r, dict) else bool(r)
            res[n] = {"ok": ok, "detail": r if isinstance(r, dict) else None, "seconds": round(time.time() - t0, 1)}
        except Exception as exc:                                        # noqa: BLE001
            res[n] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:600],
                      "trace": traceback.format_exc()[-1500:], "seconds": round(time.time() - t0, 1)}
        print(f"{'PASS' if res[n]['ok'] else 'FAIL'} {n} ({res[n]['seconds']} s)", flush=True)
    summary = {"module": module_globals.get("__file__"), "n": len(res), "passed": sum(1 for v in res.values() if v["ok"]),
               "failed": [k for k, v in res.items() if not v["ok"]], "seconds": round(time.time() - t_all, 1),
               "results": res}
    if out_path:
        Path(out_path).write_text(json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"n": summary["n"], "passed": summary["passed"], "failed": summary["failed"]}))
    return 0 if not summary["failed"] else 1


def cli(module_globals: dict) -> None:
    args = sys.argv[1:]
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = args[i + 1]
        del args[i:i + 2]
    sys.exit(run_tests(module_globals, args or None, out))
