"""Cell-308 MB-S successor campaign (r1) -- the disk-safety and scratch-lifecycle gate (non-holder builder5, research
brief 50; motivated by the ENOSPC incident of 2026-09-30, research ledger/enospc_2026-09-30/ENOSPC_AUDIT.md). Target-
free test and qualification INFRASTRUCTURE: the driver never imports this module (the execution's own disk gate is
mbs308_host.preflight_gates' free_disk_ge_2GiB, ratification item 23). NOT frozen.

FREE SPACE. free_bytes(path) is os.statvfs's f_bavail x f_frsize of the volume holding `path`, or None when the
probe fails. check_free() passes only when EVERY probe returned an integer at or above its threshold: a failed or
unreadable probe is never "enough space" (fail closed). A test may PLANT a reading through MBS308_TEST_DISK_FREE
("fail", or an integer number of bytes); a planted reading can only LOWER the real one (min) or fail it, never raise
it, so it can only make a run refuse (the driver's CLI, which never uses this module, refuses any MBS308_TEST* variable).

THE SCRATCH LIFECYCLE. A scratch ROOT is a directory in which processes create sandboxes. Every process that uses a
root records itself in <root>/.mbs308-lifecycle/<pid>-<nonce>.json (schema below): its identity (mbs308_host.identity:
pid, start time, boot UUID, command sha256), its purpose, state ACTIVE, and FINISHED once it is done. Three classes:
  ACTIVE      a root without a valid lifecycle record, or with any record that is not FINISHED, or any record whose
              owner is not POSITIVELY dead (mbs308_host.identity_state is not DEAD; UNKNOWN is never dead) -- except
              that a FINISHED record of the calling process itself counts as finished (a runner cleaning up after its
              own finished phase);
  FINISHED    the evidence of completed runs (reports, JSON, logs, probes, verdicts): kept, never removed here;
  DISPOSABLE  reconstructable sandbox state only -- a sandbox clone (a directory named `sbx` whose .git borrows its
              objects, through objects/info/alternates, from a bare base store and from nothing else) or a bare base
              store (a `*.git` directory: HEAD, objects/, refs/, `bare = true`, no alternates) -- inside a root whose
              class is FINISHED (the nearest ancestor root with a lifecycle record governs a unit).
cleanup() removes ONLY disposable units, dry-run by default (`execute=True` deletes). It never removes a file, a unit
of an ACTIVE root, anything that is or lies under a PROTECTED path (every worktree of the repository and its common
dir -- the refs, the target marker, the pending-result ref, the spool, the seals, the journal and checkpoint refs,
every committed file -- the campaign's qualified worktree, git dir and common dir and MB r1's git dir as the driver
names them, and ~/Library/Logs/ReBaseGuard), a root that is or contains a protected path, a symlink, or anything whose
real path leaves the root. Every unit is re-verified just before its deletion; every deletion is recorded, value-free
(relative path, kind, bytes, utc, who), in <root>/.mbs308-deletions.jsonl and in the returned report.

THRESHOLDS (derived, protocol section 8.2; BUILD_REPORT section 16.4; every input is recorded there).
  QUAL_MIN_FREE_BYTES: the free space the qualification verifier and the mutant runner require on the volume of their
  scratch before they start and before each heavy phase (a suite, the mutant matrix and each of its target runs, the
  resume decoy).

    python3.14 -I -S -B mbs308_scratch.py free PATH [PATH ...]
    python3.14 -I -S -B mbs308_scratch.py status ROOT
    python3.14 -I -S -B mbs308_scratch.py cleanup ROOT [--execute]
    python3.14 -I -S -B mbs308_scratch.py measure --tree DIR [--every S] --out FILE -- CMD ...
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import os
import secrets
import shutil
import stat
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve()


def _load_host():
    """mbs308_host from THIS module's own directory, loaded under a private module name: never through sys.path and
    never as sys.modules["mbs308_host"], so that loading this module (e.g. as the test library's lifecycle writer)
    can never substitute another copy of the host module for the one a test or a mutant imports."""
    import importlib.util
    name = "_mbs308_scratch_host_" + hashlib.sha256(str(HERE.parent).encode()).hexdigest()[:12]
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE.parent / "mbs308_host.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


HOST = _load_host()

REPO = HERE.parents[4]
SCHEMA = "rebaseguard.p5y.k5.cell308-mbs-r1.scratch-lifecycle.v1"
RECORD_DIR = ".mbs308-lifecycle"
DELETIONS_LOG = ".mbs308-deletions.jsonl"
ACTIVE, FINISHED = "ACTIVE", "FINISHED"
PLANT_ENV = "MBS308_TEST_DISK_FREE"
GIB = 1024 ** 3
MIB = 1024 ** 2
LOGS_DIR = Path.home() / "Library" / "Logs" / "ReBaseGuard"
GENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0"}

# ---- QUAL_MIN_FREE_BYTES, derived (protocol section 8.2; BUILD_REPORT section 16.4). Inputs measured target-free by
# builder5 on this host on 2026-09-30 (peak allocated bytes of each suite's scratch tree, sampled every 2 s; the
# per-phase / per-mutant cleanup on): P_max = the heaviest heavy phase (QS-DISK: its own sandbox plus a nested verifier
# with its own base store and a full sandbox; 2.119 GiB, rounded up to the MiB), B = the verifier's base store (a
# `git clone --bare --no-local` of the repository, 458.4 MiB; it persists across the phases), the swap step of
# ratification item 23, and a written safety factor 2 (the base store's growth with the repository, run-to-run variation
# of the test artifacts, the records a phase writes, other host activity until the phase ends).
MEASURED_PEAK_PHASE_BYTES = 2171 * MIB     # QS-DISK peak (2.119 GiB), rounded up to the MiB
MEASURED_BASE_STORE_BYTES = 459 * MIB      # the base store (458.4 MiB), rounded up to the MiB
SWAP_STEP_BYTES = 1 * GIB                  # ratification item 23: macOS swap grows in 1 GiB swapfile steps
SAFETY_FACTOR = 2                          # the written margin
QUAL_MIN_FREE_BYTES = -(-(SAFETY_FACTOR * (MEASURED_PEAK_PHASE_BYTES + MEASURED_BASE_STORE_BYTES) + SWAP_STEP_BYTES)
                        // GIB) * GIB      # roundup to the GiB: 7 GiB


class DiskRefusal(Exception):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


class ScratchRefusal(Exception):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------ free space (fail closed)
def planted_reading() -> tuple:
    """(active, value): a test's planted reading. value None = the probe fails; an int = an upper bound."""
    raw = os.environ.get(PLANT_ENV)
    if raw is None:
        return False, None
    raw = raw.strip()
    if raw.isdigit():
        return True, int(raw)
    return True, None                       # "fail" or anything unparseable: the probe fails


def free_bytes(path) -> int | None:
    """Free bytes available to this user on the volume holding `path`; None when the probe fails."""
    try:
        st = os.statvfs(str(path))
        real = st.f_bavail * st.f_frsize
    except (OSError, ValueError, TypeError):
        return None
    if not isinstance(real, int) or isinstance(real, bool) or real < 0:
        return None
    active, planted = planted_reading()
    if active:
        return None if planted is None else min(real, planted)
    return real


def check_free(needs, phase: str) -> dict:
    """`needs`: [(path, threshold_bytes), ...]. PASS only when every probe is an integer >= its threshold. A path that
    does not exist yet is probed at its nearest existing ancestor."""
    rows = []
    for path, need in needs:
        p = Path(path)
        while not p.exists() and p != p.parent:
            p = p.parent
        got = free_bytes(p)
        rows.append({"path": str(path), "probed": str(p), "free_bytes": got, "need_bytes": int(need),
                     "ok": isinstance(got, int) and not isinstance(got, bool) and got >= int(need)})
    return {"phase": phase, "utc": utc(), "readings": rows, "planted": planted_reading()[0],
            "pass": bool(rows) and all(r["ok"] for r in rows)}


def require_free(needs, phase: str) -> dict:
    r = check_free(needs, phase)
    if not r["pass"]:
        bad = [x for x in r["readings"] if not x["ok"]]
        code = "DISK_UNREADABLE" if any(x["free_bytes"] is None for x in bad) else "DISK_INSUFFICIENT"
        raise DiskRefusal(code, f"{phase}: " + ", ".join(f"{x['probed']} free={x['free_bytes']} need={x['need_bytes']}"
                                                         for x in bad))
    return r


# ------------------------------------------------------------------ lifecycle records
def _write_json_atomic(path: Path, obj: dict) -> None:
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}-{secrets.token_hex(3)}")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        os.write(fd, (json.dumps(obj, sort_keys=True) + "\n").encode())
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, path)


def begin(root, purpose: str) -> Path:
    """Record the calling process as a user of the scratch root (state ACTIVE). Returns the record's path."""
    root = Path(root)
    d = root / RECORD_DIR
    d.mkdir(parents=True, exist_ok=True)
    os.chmod(d, 0o700)
    ident = HOST.identity()
    path = d / f"{os.getpid()}-{secrets.token_hex(4)}.json"
    _write_json_atomic(path, {"schema": SCHEMA, "root": str(root.resolve()), "owner": ident, "purpose": purpose,
                              "state": ACTIVE, "began_utc": utc(), "finished_utc": None})
    return path


def finish(record: Path) -> None:
    """Mark the calling process's record FINISHED (it no longer uses the root)."""
    rec = json.loads(Path(record).read_text())
    if not isinstance(rec.get("owner"), dict) or rec["owner"].get("pid") != os.getpid():
        raise ScratchRefusal("NOT_OWNER", "only the recording process finishes its record")
    rec.update({"state": FINISHED, "finished_utc": utc()})
    _write_json_atomic(Path(record), rec)


def _is_self(owner: dict) -> bool:
    me = HOST.identity()
    return isinstance(owner, dict) and all(owner.get(k) == me.get(k) and me.get(k) for k in
                                           ("pid", "start_time", "boot_uuid", "command_sha256"))


def root_class(root) -> dict:
    """ACTIVE / FINISHED of one root, from its lifecycle records (read-only)."""
    root = Path(root)
    d = root / RECORD_DIR
    reasons, n = [], 0
    if not d.is_dir() or d.is_symlink():
        return {"root": str(root), "class": ACTIVE, "records": 0, "reasons": ["NO_LIFECYCLE_RECORD"]}
    for p in sorted(d.iterdir()):
        if not p.name.endswith(".json") or p.name.startswith("."):
            continue
        n += 1
        try:
            if p.is_symlink():
                raise ValueError("symlink")
            rec = json.loads(p.read_text())
            ok = isinstance(rec, dict) and rec.get("schema") == SCHEMA and isinstance(rec.get("owner"), dict) and \
                rec["owner"].get("pid") and rec.get("state") in (ACTIVE, FINISHED)
        except (OSError, ValueError):
            ok, rec = False, None
        if not ok:
            reasons.append(f"INVALID_RECORD {p.name}")
            continue
        if rec["state"] != FINISHED:
            reasons.append(f"NOT_FINISHED {p.name}")
            continue
        if _is_self(rec["owner"]):
            continue
        st = HOST.identity_state(rec["owner"])
        if st != "DEAD":
            reasons.append(f"OWNER_NOT_DEAD {p.name} ({st})")
    if n == 0:
        reasons.append("NO_LIFECYCLE_RECORD")
    return {"root": str(root), "class": FINISHED if not reasons else ACTIVE, "records": n, "reasons": reasons}


# ------------------------------------------------------------------ protected paths
def _driver_paths(code_dir: Path) -> list:
    """The campaign's own locations as the driver names them (read from its text; the driver is never imported)."""
    try:
        tree = ast.parse((code_dir / "mbs308_driver.py").read_text())
    except (OSError, SyntaxError):
        return []
    out = []
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
            for t in n.targets:
                if getattr(t, "id", None) in ("QUALIFIED_WORKTREE", "QUALIFIED_GIT_DIR", "QUALIFIED_COMMON_DIR",
                                              "MBR1_GIT_DIR"):
                    out.append(n.value.value)
    return out


def protected_paths(repo: Path = None, extra=()) -> list:
    """Real paths that no cleanup may touch: every worktree of `repo` and its common dir, the campaign's qualified
    worktree / git dir / common dir and MB r1's git dir (from the driver's text), the durable logs, and `extra`.
    Refuses (ScratchRefusal) when the repository cannot be read: no protected set, no deletion."""
    repo = Path(repo or REPO)
    p = subprocess.run(["/usr/bin/git", "-C", str(repo), "worktree", "list", "--porcelain"], capture_output=True,
                       text=True, env=GENV, stdin=subprocess.DEVNULL)
    c = subprocess.run(["/usr/bin/git", "-C", str(repo), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                       capture_output=True, text=True, env=GENV, stdin=subprocess.DEVNULL)
    if p.returncode or c.returncode or not c.stdout.strip():
        raise ScratchRefusal("PROTECTED_SET_UNREADABLE", f"git worktree list / rev-parse failed in {repo}")
    paths = [ln[len("worktree "):] for ln in p.stdout.splitlines() if ln.startswith("worktree ")]
    paths += [c.stdout.strip(), str(LOGS_DIR)] + _driver_paths(HERE.parent) + [str(x) for x in extra]
    return sorted({os.path.realpath(x) for x in paths if x})


def _under(path: str, base: str) -> bool:
    return path == base or path.startswith(base.rstrip("/") + "/")


# ------------------------------------------------------------------ disposable units
def _bare_store(d: Path) -> bool:
    try:
        cfg = (d / "config").read_text()
    except OSError:
        return False
    return d.name.endswith(".git") and (d / "HEAD").is_file() and (d / "objects").is_dir() and \
        (d / "refs").is_dir() and "bare = true" in cfg and not (d / "objects/info/alternates").exists() and \
        not any(x.is_symlink() for x in (d / "HEAD", d / "objects", d / "refs", d / "config"))


def _sandbox_clone(d: Path, protected: list) -> bool:
    g = d / ".git"
    if d.name != "sbx" or g.is_symlink() or not g.is_dir():
        return False
    try:
        alt = (g / "objects/info/alternates").read_text().split()
    except OSError:
        return False
    if not alt:
        return False
    for a in alt:
        o = Path(os.path.realpath(a))
        if o.name != "objects" or not _bare_store(o.parent) or any(_under(str(o), x) for x in protected):
            return False
    return (g / "config").is_file()


def find_units(root: Path, protected: list) -> list:
    """(path, kind) of every sandbox clone and bare base store under `root` (symlinks are never followed or
    listed; nothing inside a unit is descended into)."""
    out = []
    for dirpath, dirnames, _files in os.walk(root, followlinks=False):
        keep = []
        for dn in sorted(dirnames):
            p = Path(dirpath) / dn
            if p.is_symlink():
                continue
            if _sandbox_clone(p, protected):
                out.append((p, "sandbox_clone"))
            elif _bare_store(p):
                out.append((p, "bare_base_store"))
            else:
                keep.append(dn)
        dirnames[:] = keep
    return out


def _governing_root(unit: Path, root: Path) -> Path | None:
    for a in [unit.parent, *unit.parent.parents]:
        if (a / RECORD_DIR).is_dir():
            return a
        if a == root:
            break
    return None


def tree_bytes(path) -> int:
    """Allocated bytes of a tree (st_blocks x 512, each inode once, symlinks not followed): what `du` counts."""
    seen, total = set(), 0
    for dirpath, dirnames, files in os.walk(path, followlinks=False):
        for n in dirnames + files:
            try:
                st = os.lstat(os.path.join(dirpath, n))
            except OSError:
                continue
            if (st.st_dev, st.st_ino) in seen:
                continue
            seen.add((st.st_dev, st.st_ino))
            total += st.st_blocks * 512
    try:
        total += os.lstat(path).st_blocks * 512
    except OSError:
        pass
    return total


def _verify_unit(unit: Path, kind: str, root: Path, protected: list) -> str | None:
    """None when `unit` may be deleted now, else the refusal reason."""
    real, rroot = os.path.realpath(unit), os.path.realpath(root)
    if unit.is_symlink() or real != str(unit.absolute()):
        return "SYMLINK_OR_ALIAS"
    if not _under(real, rroot) or real == rroot:
        return "LEAVES_ROOT"
    if any(_under(real, x) or _under(x, real) for x in protected):
        return "PROTECTED"
    if kind == "sandbox_clone" and not _sandbox_clone(unit, protected):
        return "NOT_A_SANDBOX_CLONE"
    if kind == "bare_base_store" and not _bare_store(unit):
        return "NOT_A_BARE_STORE"
    gov = _governing_root(unit, Path(rroot))
    if gov is None:
        return "NO_LIFECYCLE_RECORD"
    if root_class(gov)["class"] != FINISHED:
        return "ROOT_ACTIVE"
    return None


def cleanup(root, *, execute: bool = False, repo: Path = None, extra_protected=()) -> dict:
    """Remove the DISPOSABLE units under `root` (dry-run unless execute). Returns a value-free report."""
    root = Path(root)
    rep = {"root": str(root), "dry_run": not execute, "utc": utc(), "units": [], "deleted": [], "refused": [],
           "bytes_deleted": 0}
    if root.is_symlink() or os.path.realpath(root) != str(root.absolute()):
        raise ScratchRefusal("ROOT_SYMLINK", "the scratch root must be given by its real path")
    if not root.is_dir():
        raise ScratchRefusal("ROOT_MISSING", str(root))
    protected = protected_paths(repo, extra_protected)
    rr = os.path.realpath(root)
    hit = [x for x in protected if _under(rr, x) or _under(x, rr)]
    if hit:
        raise ScratchRefusal("ROOT_PROTECTED", "the root is, lies under or contains a protected path")
    if not getattr(shutil.rmtree, "avoids_symlink_attacks", False):
        raise ScratchRefusal("RMTREE_UNSAFE", "shutil.rmtree does not avoid symlink attacks on this platform")
    rep["protected"] = len(protected)
    units = sorted(find_units(root, protected), key=lambda u: (u[1] != "sandbox_clone", str(u[0])))
    borrowed: dict = {}                     # base store (real path) -> the sandbox clones under root borrowing from it
    for unit, kind in units:
        if kind == "sandbox_clone":
            try:                                # a clone whose alternates cannot be read borrows nothing recorded
                alts = (unit / ".git/objects/info/alternates").read_text().split()
            except OSError:
                alts = []
            for a in alts:
                borrowed.setdefault(os.path.realpath(Path(os.path.realpath(a)).parent), []).append(unit)
    gone: set = set()                       # clones deleted (execute) or found disposable (dry-run) in this pass

    def in_use(store: Path) -> bool:
        return any(b.exists() and b not in gone for b in borrowed.get(os.path.realpath(store), []))
    for unit, kind in units:                # sandbox clones first: a base store goes only after its borrowers
        why = _verify_unit(unit, kind, root, protected)
        if why is None and kind == "bare_base_store" and in_use(unit):
            why = "BASE_STORE_IN_USE"
        rel = str(unit.relative_to(root))
        rep["units"].append({"path": rel, "kind": kind, "disposable": why is None, "reason": why})
        if why is not None:
            rep["refused"].append({"path": rel, "kind": kind, "reason": why})
            continue
        if not execute:
            gone.add(unit)
            continue
        why = _verify_unit(unit, kind, root, protected)          # re-verified just before the deletion
        if why is None and kind == "bare_base_store" and in_use(unit):
            why = "BASE_STORE_IN_USE"
        if why is not None:
            rep["refused"].append({"path": rel, "kind": kind, "reason": why})
            continue
        size = tree_bytes(unit)
        shutil.rmtree(unit)
        gone.add(unit)
        ev = {"utc": utc(), "path": rel, "kind": kind, "bytes": size, "by": {"pid": os.getpid()}}
        rep["deleted"].append(ev)
        rep["bytes_deleted"] += size
        fd = os.open(root / DELETIONS_LOG, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
        try:
            os.write(fd, (json.dumps(ev, sort_keys=True) + "\n").encode())
            os.fsync(fd)
        finally:
            os.close(fd)
    return rep


# ------------------------------------------------------------------ gated heavy phases (the verifier, the mutant runner)
def run_gated(phases: list, *, gate, run, verified, clean) -> dict:
    """Run heavy phases under the disk gate. `phases`: [(name, payload), ...]. gate("start") before anything and
    gate(name) before EVERY phase must return a check with `pass` True; a failing (or malformed) check STOPS: that
    phase and every later one do not run (listed in `not_run`) and the refusal is recorded. After a phase, when
    verified(result) holds, clean(name, result) deletes its disposable scratch (its result was written and verified
    first). Returns {results, checks, cleanups, refusal, not_run}."""
    out = {"results": {}, "checks": [], "cleanups": {}, "refusal": None, "not_run": []}
    names = [n for n, _ in phases]

    def passes(name: str) -> bool:
        c = gate(name)
        ok = isinstance(c, dict) and c.get("pass") is True
        out["checks"].append({"phase": name, "pass": ok,
                              "free_bytes": [r.get("free_bytes") for r in (c or {}).get("readings", [])]
                              if isinstance(c, dict) else None})
        if not ok:
            out["refusal"] = {"phase": name, "check": c}
        return ok
    if not passes("start"):
        out["not_run"] = names
        return out
    for i, (name, payload) in enumerate(phases):
        if not passes(name):
            out["not_run"] = names[i:]
            return out
        r = run(name, payload)
        out["results"][name] = r
        if verified(r):
            out["cleanups"][name] = clean(name, r)
    return out


# ------------------------------------------------------------------ measurement (threshold inputs; target-free)
class TreeMeter:
    """Samples the allocated bytes of a tree every `every` seconds (and the volume's free bytes) while a command runs;
    records the peak and the samples' count (value-free: sizes only)."""

    def __init__(self, tree, every: float = 2.0):
        self.tree, self.every = Path(tree), every
        self.peak, self.samples, self.min_free = 0, 0, None
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._loop, name="mbs308-tree-meter", daemon=True)

    def _sample(self) -> None:
        b = tree_bytes(self.tree) if self.tree.exists() else 0
        self.peak = max(self.peak, b)
        self.samples += 1
        f = free_bytes(self.tree if self.tree.exists() else self.tree.parent)
        if isinstance(f, int):
            self.min_free = f if self.min_free is None else min(self.min_free, f)

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._sample()
            self._stop.wait(self.every)

    def start(self) -> "TreeMeter":
        self._t.start()
        return self

    def stop(self) -> dict:
        self._stop.set()
        self._t.join(timeout=60)
        self._sample()
        return {"tree": str(self.tree), "peak_bytes": self.peak, "samples": self.samples, "every_s": self.every,
                "final_bytes": tree_bytes(self.tree) if self.tree.exists() else 0, "min_free_bytes": self.min_free}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = []
    if "--" in argv:
        i = argv.index("--")
        argv, cmd = argv[:i], argv[i + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("free", "status", "cleanup", "measure"))
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--execute", action="store_true", help="cleanup: delete (default: dry-run)")
    ap.add_argument("--tree")
    ap.add_argument("--every", type=float, default=2.0)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        if a.what == "free":
            r = check_free([(p, QUAL_MIN_FREE_BYTES) for p in a.paths], "free")
            r["QUAL_MIN_FREE_BYTES"] = QUAL_MIN_FREE_BYTES
        elif a.what == "status":
            if len(a.paths) != 1:
                raise ScratchRefusal("ARGS", "status ROOT")
            root = Path(a.paths[0])
            prot = protected_paths()
            r = {"root": root_class(root), "units": [
                {"path": str(u.relative_to(root)), "kind": k, "reason": _verify_unit(u, k, root, prot)}
                for u, k in find_units(root, prot)]}
        elif a.what == "cleanup":
            if len(a.paths) != 1:
                raise ScratchRefusal("ARGS", "cleanup ROOT [--execute]")
            r = cleanup(Path(a.paths[0]), execute=a.execute)
        else:
            if not a.tree or not a.out or not cmd:
                raise ScratchRefusal("ARGS", "measure --tree DIR --out FILE -- CMD ...")
            m = TreeMeter(a.tree, a.every).start()
            t0 = time.time()
            rc = subprocess.run(cmd, stdin=subprocess.DEVNULL).returncode
            r = dict(m.stop(), rc=rc, wall_s=round(time.time() - t0, 1), cmd=cmd)
            Path(a.out).write_text(json.dumps(r, indent=1, sort_keys=True) + "\n")
    except (ScratchRefusal, DiskRefusal) as e:
        print(json.dumps({"refused": e.code, "detail": str(e)}))
        return 2
    print(json.dumps(r, indent=1, sort_keys=True, default=str))
    return 0 if r.get("pass", True) is not False else 1


if __name__ == "__main__":
    sys.exit(main())
