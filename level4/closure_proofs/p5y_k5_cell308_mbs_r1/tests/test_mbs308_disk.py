"""MB-S r1: the disk-safety and scratch-lifecycle gate (non-holder builder5, research brief 50), and the re-pin
tooling. TARGET-FREE: planted free-space readings (MBS308_TEST_DISK_FREE, or a planted os.statvfs), planted scratch
roots and a PLANTED repository (with worktree, campaign refs, spool and a sealed file) under the scratch directory, one
full sandbox cloned from the separate --no-local base store (never the real object store) for the driver-level tests
(synthetic evaluator), and the real repository only READ, as the protected set (nothing is deleted there: every call
naming it refuses before it walks anything). No science computation; no cell.

Properties (brief 50, task 1 f): insufficient or unreadable disk fails closed before irreversible work (the verifier's
start, the mutant runner's start, the driver's execute and resume preflight); cleanup cannot target active scratch, nor
evidence (JSON, reports, ledgers, manifests, verdicts), nor refs, nor the target marker, the pending ref, the spool or a
seal; a probe failure never reads as sufficient space. Each has a mutant killed by the test's own assertion.

    python3.14 -I -S -B test_mbs308_disk.py [t_name ...] [--out report.json]
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbs308_testlib as T  # noqa: E402

TMP = T.SCRATCH / "t_disk"
_S: dict = {}
GIB = 1024 ** 3
GOOD_HOST = {"batt": "Now drawing from 'AC Power'\n", "pmset": " lowpowermode         0\n",
             "thermal": "com.apple.system.thermalpressurelevel 0\n", "free": 10 * GIB, "memory": "1\n",
             "boot": "A7417159-025C-461F-8BF8-3F9C7F3C58CB\n"}
SU_OFF = {"AutomaticallyInstallMacOSUpdates": "0", "AutomaticDownload": "1", "CriticalUpdateInstall": "0",
          "ConfigDataInstall": "1"}
PS_QUIET = "    1     0   0.4 /sbin/launchd\n  300     1   1.2 /usr/libexec/somed\n"


def _big_memory() -> int:
    """Free memory far above the driver's FREE_MEM_MIN_BYTES, whatever value the driver under test carries (the
    provisional one before the apply step of protocol section 11.2, R-FREE's output after it)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_mbs308_derive_disk", T.code_dir() / "mbs308_derive.py")
    dv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dv)                     # the exact reader of the driver's TEXT (never imports the driver)
    return max(8 * GIB, 2 * dv.driver_constants((T.code_dir() / "mbs308_driver.py").read_text())["FREE_MEM_MIN_BYTES"])


def _vm(free_bytes: int) -> str:
    pages = free_bytes // 16384
    return ("Mach Virtual Memory Statistics: (page size of 16384 bytes)\n"
            f"Pages free:                               {pages}.\nPages active:                  1000.\n"
            "Pages inactive:                                0.\nPages speculative:                0.\n"
            "Pages throttled:                                0.\nPages wired down:            1000.\n"
            "Pages purgeable:                                0.\n")


def _load(name: str):
    """A module of the code under test (T.code_dir(): the namespace's own or a mutated copy), by path, under a private
    name (the infra copy the test library uses is never substituted)."""
    key = f"_t_disk_{name}_{hashlib.sha256(str(T.code_dir()).encode()).hexdigest()[:10]}"
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, T.code_dir() / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


def SCR():
    return _load("mbs308_scratch")


def HOST():
    return SCR().HOST              # the host module of the code under test (loaded privately by the scratch module)


def sb() -> T.Sandbox:
    if "sb" not in _S:
        _S["sb"] = T.Sandbox(TMP / "full")
    return _S["sb"]


def fresh_dir(name: str) -> Path:
    d = TMP / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return Path(os.path.realpath(d))


def git(root, *args, check=True) -> str:
    p = subprocess.run(["/usr/bin/git", "-C", str(root), "-c", "commit.gpgsign=false", *args], capture_output=True,
                       text=True, stdin=subprocess.DEVNULL,
                       env=dict(T.GENV, GIT_AUTHOR_NAME="planted", GIT_AUTHOR_EMAIL="planted@invalid",
                                GIT_COMMITTER_NAME="planted", GIT_COMMITTER_EMAIL="planted@invalid",
                                GIT_CONFIG_NOSYSTEM="1"))
    if check and p.returncode:
        raise RuntimeError(f"git {args[:3]}: {p.stderr[:300]}")
    return p.stdout.strip()


def dead_identity() -> dict:
    h = T.Helper(60)
    ident = HOST().identity(h.p.pid)
    h.kill()
    return ident


def plant_borrower(store: Path, owner: dict, state: str, clones=(), **extra) -> Path:
    """A planted record in a base store's borrower register (protocol section 8.2), as the library writes it."""
    d = Path(store) / SCR().BORROW_DIR
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{owner.get('pid')}-{secrets.token_hex(3)}.json"
    p.write_text(json.dumps({"schema": SCR().BORROW_SCHEMA, "store": str(store), "owner": owner, "purpose": "planted",
                             "state": state, "clones": [os.path.realpath(c) for c in clones],
                             "began_utc": "planted", "finished_utc": None, **extra}))
    return p


def head_readable(clone: Path) -> bool:
    """A sandbox clone can still read its HEAD commit (its borrowed objects are there)."""
    return subprocess.run(["/usr/bin/git", "-C", str(clone), "cat-file", "-e", "HEAD^{commit}"], capture_output=True,
                          env=T.GENV, stdin=subprocess.DEVNULL).returncode == 0


def plant_record(root: Path, owner: dict, state: str, **extra) -> Path:
    d = root / SCR().RECORD_DIR
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{owner.get('pid')}-{secrets.token_hex(3)}.json"
    p.write_text(json.dumps({"schema": SCR().SCHEMA, "root": str(root), "owner": owner, "purpose": "planted",
                             "state": state, "began_utc": "planted", "finished_utc": None, **extra}))
    return p


def tree_hashes(root: Path, skip=()) -> dict:
    out = {}
    for dp, dns, fns in os.walk(root, followlinks=False):
        dns[:] = [d for d in dns if not any(str(Path(dp) / d).startswith(str(s)) for s in skip)]
        for f in fns:
            p = Path(dp) / f
            out[str(p.relative_to(root))] = "LINK:" + os.readlink(p) if p.is_symlink() else \
                hashlib.sha256(p.read_bytes()).hexdigest()
        for d in dns:
            p = Path(dp) / d
            if p.is_symlink():
                out[str(p.relative_to(root))] = "LINK:" + os.readlink(p)
    return out


def tiny_repo(d: Path) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    git(d, "init", "-q", "-b", "main")
    (d / "f.txt").write_text("planted\n")
    git(d, "add", "f.txt")
    git(d, "commit", "-q", "-m", "planted")
    return d


def bare_store(src: Path, dst: Path) -> Path:
    subprocess.run(["/usr/bin/git", "clone", "-q", "--bare", "--no-local", str(src), str(dst)], check=True,
                   capture_output=True, env=T.GENV)
    return dst


def sandbox_clone(store: Path, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["/usr/bin/git", "clone", "-q", "--shared", str(store), str(dst)], check=True, capture_output=True,
                   env=T.GENV)
    return dst


def layout(root: Path) -> dict:
    """A scratch root as the suites leave it: a bare base store and a sandbox clone of it (the only DISPOSABLE units),
    next to evidence of completed runs (a JSON report, a log, a ledger, a manifest, a verdict, a probe, a result) and to
    look-alikes that are NOT units: a plain directory named sbx holding a report, a *.git directory that is not bare,
    and an sbx clone that borrows from a NON-bare repository. The store carries its borrower register as the test
    library leaves it after a finished run (one FINISHED record of a dead process, naming the clone); the non-bare
    look-alike carries the same register, so only its shape keeps it from being a unit."""
    src = tiny_repo(root.parent / (root.name + "_src"))
    store = bare_store(src, root / "work" / "base.git")
    clone = sandbox_clone(store, root / "work" / "t_x" / "sbx")
    if "dead" not in _S:
        _S["dead"] = dead_identity()
    plant_borrower(store, _S["dead"], "FINISHED", clones=[clone])
    files = {"work/t_x/report.json": '{"n": 1, "passed": 1}\n', "work/t_x/child.out": "log line\n",
             "work/ledger.jsonl": '{"agent": "planted"}\n', "work/MBS308_FREEZE.json": '{"schema": "planted"}\n',
             "work/REVIEW_VERDICT.md": "# planted\nQUALIFICATION_ACCEPTED\n", "work/probe.json": "{}\n",
             "results/result.json": '{"planted": true}\n', "work/t_y/sbx/report.json": '{"not": "a sandbox"}\n'}
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    fake = root / "work" / "fake.git"
    for sub in ("objects", "refs"):
        (fake / sub).mkdir(parents=True, exist_ok=True)
    (fake / "HEAD").write_text("ref: refs/heads/main\n")
    (fake / "config").write_text("[core]\n\tbare = false\n")
    plant_borrower(fake, _S["dead"], "FINISHED")
    sandbox_clone(src, root / "work" / "t_z" / "sbx")          # borrows from a NON-bare repository: not a unit
    return {"units": sorted(["work/base.git", "work/t_x/sbx"]), "kept_dirs": ["work/t_y/sbx", "work/fake.git",
                                                                              "work/t_z/sbx"], "files": sorted(files)}


# ====================================================================== free space
def t_free_probe_fails_closed():
    """A probe failure never reads as sufficient space: a planted failure ("fail"), a statvfs that raises and an
    unparseable planted value each give None, and check_free / require_free refuse (DISK_UNREADABLE); a reading below
    the threshold refuses (DISK_INSUFFICIENT); a planted value can only LOWER the real reading (min), never raise it; an
    empty list of probes never passes; a reading exactly at the threshold passes."""
    S = SCR()
    d = fresh_dir("free")
    real_statvfs, saved = os.statvfs, os.environ.get(S.PLANT_ENV)

    class Fake:
        f_bavail, f_frsize = 1000, 4096

    out = {}
    try:
        os.environ.pop(S.PLANT_ENV, None)
        out["real_is_int"] = isinstance(S.free_bytes(d), int)
        os.statvfs = lambda p: Fake()
        out["fake"] = S.free_bytes(d) == 4096000
        out["at_threshold"] = S.check_free([(d, 4096000)], "t")["pass"] is True
        out["above_threshold"] = S.check_free([(d, 4096001)], "t")["pass"] is False
        os.environ[S.PLANT_ENV] = str(10 ** 15)
        out["plant_cannot_raise"] = S.free_bytes(d) == 4096000 and S.check_free([(d, 4096001)], "t")["pass"] is False
        os.environ[S.PLANT_ENV] = "4000"
        out["plant_lowers"] = S.free_bytes(d) == 4000
        for v in ("fail", "garbage", ""):
            os.environ[S.PLANT_ENV] = v
            out[f"plant_{v or 'empty'}_is_none"] = S.free_bytes(d) is None
        os.environ[S.PLANT_ENV] = "fail"
        c = S.check_free([(d, 1)], "t")
        out["failed_probe_refuses"] = c["pass"] is False and c["readings"][0]["free_bytes"] is None
        try:
            S.require_free([(d, 1)], "t")
            out["require_unreadable"] = False
        except S.DiskRefusal as e:
            out["require_unreadable"] = e.code == "DISK_UNREADABLE"
        os.environ[S.PLANT_ENV] = "10"
        try:
            S.require_free([(d, 11)], "t")
            out["require_insufficient"] = False
        except S.DiskRefusal as e:
            out["require_insufficient"] = e.code == "DISK_INSUFFICIENT"
        os.environ.pop(S.PLANT_ENV, None)

        def boom(p):
            raise OSError("planted statvfs failure")
        os.statvfs = boom
        out["statvfs_error_is_none"] = S.free_bytes(d) is None and S.check_free([(d, 1)], "t")["pass"] is False
        os.statvfs = real_statvfs
        out["no_probe_never_passes"] = S.check_free([], "t")["pass"] is False
        out["missing_path_probes_ancestor"] = isinstance(
            S.check_free([(d / "not" / "yet", 1)], "t")["readings"][0]["free_bytes"], int)
    finally:
        os.statvfs = real_statvfs
        if saved is None:
            os.environ.pop(S.PLANT_ENV, None)
        else:
            os.environ[S.PLANT_ENV] = saved
    return {"ok": all(out.values()), "cases": out}


def t_driver_disk_gate_fails_closed():
    """The DRIVER's own start gate (mbs308_host.preflight_gates, free_disk_ge_2GiB, ratified MIN_FREE_DISK 2 GiB, item
    23): a failed probe (free_disk_bytes on an unreadable path, or a planted None) fails the gate, so does a reading
    one byte below the threshold; exactly the threshold passes; the reading itself is an int for a real path."""
    H = HOST()
    base = {k: v for k, v in GOOD_HOST.items() if k != "free"}
    gate = lambda texts, repo="/": H.preflight_gates(repo, other_job_running=False, launched={"pass": True},  # noqa
                                                     texts=texts, su_texts=SU_OFF)
    g_missing = gate(base, "/nonexistent/mbs308/volume")
    out = {"probe_on_missing_path_is_none": H.free_disk_bytes("/nonexistent/mbs308/volume") is None,
           "probe_real_is_int": isinstance(H.free_disk_bytes(str(TMP.parent)), int),
           "unreadable_fails_gate": g_missing["gates"]["free_disk_ge_2GiB"] is False and
           g_missing["readings"]["free_disk_bytes"] is None and g_missing["pass"] is False,
           "planted_none_fails_gate": gate(dict(base, free=None))["gates"]["free_disk_ge_2GiB"] is False,
           "below_fails_gate": gate(dict(base, free=H.MIN_FREE_DISK - 1))["gates"]["free_disk_ge_2GiB"] is False,
           "at_threshold_passes": gate(dict(base, free=H.MIN_FREE_DISK))["gates"]["free_disk_ge_2GiB"] is True,
           "threshold_is_ratified": H.MIN_FREE_DISK == 2 * GIB}
    return {"ok": all(out.values()), "cases": out}


def _planted(free) -> dict:
    return {"host": dict(GOOD_HOST, free=free), "su": SU_OFF, "vm_stat": _vm(_big_memory()), "ps": PS_QUIET}


def _journal(sbx) -> dict | None:
    raw = subprocess.run(["/usr/bin/git", "-C", str(sbx.root), "cat-file", "blob", T.PREFIX + "journal"],
                         capture_output=True, env=T.GENV).stdout
    return json.loads(raw) if raw else None


def t_execute_resume_refuse_on_disk():
    """The driver's execute and resume refuse on insufficient or unreadable disk BEFORE irreversible work (synthetic
    evaluator in a sandbox; the REAL start gates on planted readings, every other reading good): execute refuses
    HOST_PREFLIGHT naming only free_disk_ge_2GiB, with no campaign ref (no intent, no marker), no spool result and
    nothing sealed; resume after a crash refuses the same way before the attempt counter moves (the journal's attempt
    stays 1, the state stays CONSUMED_INTERRUPTED). Controls: with a sufficient reading execute seals, and resume
    resumes and seals."""
    s = sb()
    H = HOST()
    out = {}
    s.grant_chain()
    for case, free in (("below", H.MIN_FREE_DISK - 1), ("probe_failed", None)):
        r = T.child(s, "execute", {"host_texts": _planted(free)})
        out[f"execute_{case}"] = r["out"] == {"rc": 2, "refused": "HOST_PREFLIGHT"} and \
            r["detail"] == "HOST_PREFLIGHT: free_disk_ge_2GiB" and s.refs() == {} and \
            not (s.spool() / "result.json").exists() and s.sealed_record() is None
    r = T.child(s, "execute", {"host_texts": _planted(10 * GIB)})
    out["execute_control_seals"] = r["out"] == {"rc": 0} and (s.sealed_record() or {}).get("status") == \
        "TARGET_EVALUATED"
    s.grant_chain()
    T.child(s, "execute", {"host_texts": _planted(10 * GIB), "fault": {"F3": {"at": 2, "how": "kill"}}})
    j0 = _journal(s)
    st0 = T.child(s, "status")["stdout"].strip().splitlines()[-1]
    for case, free in (("below", H.MIN_FREE_DISK - 1), ("probe_failed", None)):
        r = T.child(s, "resume", {"host_texts": _planted(free)})
        j = _journal(s)
        out[f"resume_{case}"] = r["out"] == {"rc": 2, "refused": "HOST_PREFLIGHT"} and \
            r["detail"] == "HOST_PREFLIGHT: free_disk_ge_2GiB" and j == j0 and j0 is not None and \
            j0.get("attempt") == 1 and T.child(s, "status")["stdout"].strip().splitlines()[-1] == st0
    out["crash_state"] = st0 == "CONSUMED_INTERRUPTED"
    r = T.child(s, "resume", {"host_texts": _planted(10 * GIB)})
    out["resume_control_seals"] = r["out"] == {"rc": 0} and (s.sealed_record() or {}).get("status") == \
        "TARGET_EVALUATED"
    return {"ok": all(out.values()), "cases": out}


def t_thresholds_derived():
    """The thresholds are the protocol's derivation, bound in code and text alike (section 8.2): QUAL_MIN_FREE_BYTES =
    roundup_GiB(SAFETY_FACTOR x (P_max + B) + swap step) with the recorded inputs (P_max 2171 MiB, B 459 MiB, factor 2,
    the 1 GiB swap step of item 23) is 7 GiB, and the protocol states that result and those inputs; the execution
    threshold stays the ratified 2 GiB (no amendment)."""
    S = SCR()
    mib, gib = 1024 ** 2, 1024 ** 3
    want = -(-(2 * (2171 * mib + 459 * mib) + gib) // gib) * gib
    proto = (T.NSS / "protocol/MBS308_PROTOCOL_DRAFT.md").read_text()
    s82 = proto.split("### 8.2 ", 1)[1].split("\n## 9.", 1)[0] if "### 8.2 " in proto else ""
    out = {"inputs": (S.MEASURED_PEAK_PHASE_BYTES, S.MEASURED_BASE_STORE_BYTES, S.SWAP_STEP_BYTES, S.SAFETY_FACTOR) ==
           (2171 * mib, 459 * mib, gib, 2),
           "formula": S.QUAL_MIN_FREE_BYTES == want == 7 * gib,
           "protocol_states_it": "QUAL_MIN_FREE_BYTES = roundup_GiB(2 × (P_max + B) + 1 GiB) = 7 GiB" in s82 and
           "P_max = 2.119 GiB" in s82 and "B = 0.448 GiB" in s82,
           "execution_threshold_ratified": HOST().MIN_FREE_DISK == 2 * gib and "no amendment proposed" in s82}
    return {"ok": all(out.values()), "cases": out, "QUAL_MIN_FREE_BYTES": S.QUAL_MIN_FREE_BYTES}


# ====================================================================== the lifecycle classes
def t_lifecycle_classes():
    """ACTIVE unless every record is FINISHED and its owner POSITIVELY dead (UNKNOWN is never dead): no record / an
    empty record directory / an invalid record / an ACTIVE record (even of a dead process) / a FINISHED record of a live
    process / of a live process whose `ps` fails / of a dead process while the boot-UUID read fails -> ACTIVE; a
    FINISHED record of a dead process, of a process whose pid now belongs to another start time (reused), or of the
    calling process itself -> FINISHED."""
    S = SCR()
    H = S.HOST
    base = fresh_dir("classes")
    res = {}

    def cls(name: str, setup) -> str:
        root = base / name
        root.mkdir()
        setup(root)
        return S.root_class(root)["class"]
    dead = dead_identity()
    h = T.Helper(120)
    try:
        live = H.identity(h.p.pid)
        res["no_record"] = cls("a", lambda r: None) == "ACTIVE"
        res["empty_record_dir"] = cls("k", lambda r: (r / S.RECORD_DIR).mkdir()) == "ACTIVE"
        res["self_active"] = cls("b", lambda r: S.begin(r, "t")) == "ACTIVE"
        res["self_finished"] = cls("c", lambda r: S.finish(S.begin(r, "t"))) == "FINISHED"
        res["dead_finished"] = cls("d", lambda r: plant_record(r, dead, "FINISHED")) == "FINISHED"
        res["reused_pid_finished"] = cls("l", lambda r: plant_record(
            r, dict(live, start_time="Thu Jan  1 00:00:00 1970"), "FINISHED")) == "FINISHED"
        res["live_finished"] = cls("e", lambda r: plant_record(r, live, "FINISHED")) == "ACTIVE"
        real_start = H.process_start
        H.process_start = lambda pid, text=None: None if int(pid) == h.p.pid else real_start(pid, text)
        try:
            res["live_ps_failing"] = cls("f", lambda r: plant_record(r, live, "FINISHED")) == "ACTIVE"
        finally:
            H.process_start = real_start
        real_boot = H.boot_session_uuid
        H.boot_session_uuid = lambda text=None: None
        try:
            res["dead_boot_read_failing"] = cls("m", lambda r: plant_record(r, dead, "FINISHED")) == "ACTIVE"
        finally:
            H.boot_session_uuid = real_boot
        res["dead_active"] = cls("g", lambda r: plant_record(r, dead, "ACTIVE")) == "ACTIVE"

        def invalid(r):
            (r / S.RECORD_DIR).mkdir()
            (r / S.RECORD_DIR / "1-x.json").write_text("{not json")
        res["invalid_record"] = cls("h", invalid) == "ACTIVE"
        res["no_owner_pid"] = cls("i", lambda r: plant_record(r, dict(dead, pid=None), "FINISHED")) == "ACTIVE"
        res["one_active_of_two"] = cls("j", lambda r: (plant_record(r, dead, "FINISHED"),
                                                       plant_record(r, live, "ACTIVE"))) == "ACTIVE"
    finally:
        h.kill()
    return {"ok": all(res.values()), "cases": res}


# ====================================================================== cleanup
def t_cleanup_only_disposable():
    """Cleanup removes ONLY disposable units (a sandbox clone of a bare base store, and the bare base store, in that
    order) of a FINISHED root whose owner is dead; dry-run (the default) deletes nothing; every other file (a JSON
    report, a log, a ledger, a manifest, a verdict, a probe, a result) and every look-alike (a plain directory named
    sbx, a non-bare *.git directory, an sbx clone of a non-bare repository) stays byte for byte; each deletion is
    recorded value-free in the deletions log."""
    S = SCR()
    root = fresh_dir("only") / "root"
    root.mkdir()
    lay = layout(root)
    plant_record(root, dead_identity(), "FINISHED")
    before = tree_hashes(root, skip=[root / u for u in lay["units"]])
    dry = S.cleanup(root, repo=T.REPO)
    after_dry = all((root / u).is_dir() for u in lay["units"]) and dry["deleted"] == [] and \
        sorted(u["path"] for u in dry["units"] if u["disposable"]) == lay["units"] and \
        sorted(u["path"] for u in dry["units"]) == lay["units"]       # no look-alike is even listed as a unit
    ex = S.cleanup(root, execute=True, repo=T.REPO)
    log = [json.loads(x) for x in (root / S.DELETIONS_LOG).read_text().splitlines()]
    kept = tree_hashes(root)
    kept.pop(S.DELETIONS_LOG, None)
    out = {"dry_run_deletes_nothing": after_dry and dry["dry_run"] is True,
           "deleted_exactly_the_units": [d["path"] for d in ex["deleted"]] == ["work/t_x/sbx", "work/base.git"],
           "units_gone": not any((root / u).exists() for u in lay["units"]),
           "every_other_file_byte_identical": kept == before,
           "look_alikes_kept": all((root / d).is_dir() for d in lay["kept_dirs"]),
           "deletions_logged_value_free": len(log) == 2 and all(set(e) == {"utc", "path", "kind", "bytes", "by"}
                                                                for e in log)}
    return {"ok": all(out.values()), "cases": out, "units": dry["units"]}


def t_cleanup_refuses_active_scratch():
    """Cleanup never targets ACTIVE scratch: a root recorded ACTIVE by the calling process, a root FINISHED by a live
    process, a FINISHED root whose live owner's `ps` fails (UNKNOWN), a root without any lifecycle record: nothing is
    deleted (each unit refused ROOT_ACTIVE / NO_LIFECYCLE_RECORD) and every byte stays. A nested ACTIVE root inside a
    FINISHED one keeps its own sandbox (the nearest recorded root governs) while the outer FINISHED root's sandbox
    goes."""
    S = SCR()
    H = S.HOST
    base = fresh_dir("active")
    out = {}
    h = T.Helper(180)
    try:
        live = H.identity(h.p.pid)
        real_start = H.process_start
        for case, setup in (("self_active", lambda r: S.begin(r, "t")),
                            ("live_finished", lambda r: plant_record(r, live, "FINISHED")),
                            ("live_ps_failing", lambda r: plant_record(r, live, "FINISHED")),
                            ("no_record", lambda r: None)):
            root = base / case
            root.mkdir()
            lay = layout(root)
            setup(root)
            snap = tree_hashes(root)
            if case == "live_ps_failing":
                H.process_start = lambda pid, text=None: None if int(pid) == h.p.pid else real_start(pid, text)
            try:
                r = S.cleanup(root, execute=True, repo=T.REPO)
            finally:
                H.process_start = real_start
            want = "NO_LIFECYCLE_RECORD" if case == "no_record" else "ROOT_ACTIVE"
            out[case] = r["deleted"] == [] and tree_hashes(root) == snap and \
                sorted(x["path"] for x in r["refused"] if x["reason"] == want) == lay["units"]
        root = base / "nested"
        root.mkdir()
        outer = layout(root)
        plant_record(root, dead_identity(), "FINISHED")
        inner = root / "inner"
        inner.mkdir()
        inner_units = layout(inner)["units"]
        S.begin(inner, "t")                                        # the inner root is ACTIVE (this process)
        r = S.cleanup(root, execute=True, repo=T.REPO)
        out["nested"] = sorted(d["path"] for d in r["deleted"]) == sorted(outer["units"]) and \
            all((inner / u).is_dir() for u in inner_units) and \
            sorted(x["path"] for x in r["refused"] if x["reason"] == "ROOT_ACTIVE") == \
            sorted("inner/" + u for u in inner_units)
    finally:
        h.kill()
    return {"ok": all(out.values()), "cases": out}


def t_cleanup_symlinks_and_escape():
    """Symlinks are never followed and never deleted, and nothing whose real path leaves the root is a unit: a symlink
    named sbx to a real sandbox outside, a symlinked directory holding a sandbox, and a symlinked *.git to a bare store
    outside are neither listed nor touched; the outside tree stays byte for byte; a root given through a symlink is
    refused (ROOT_SYMLINK); a unit reached through a symlinked parent is refused SYMLINK_OR_ALIAS, and one outside the
    root LEAVES_ROOT."""
    S = SCR()
    base = fresh_dir("links")
    outside = base / "outside"
    outside.mkdir()
    src = tiny_repo(base / "src")
    store = bare_store(src, outside / "base.git")
    sandbox_clone(store, outside / "sbx")
    root = base / "root"
    root.mkdir()
    plant_record(root, dead_identity(), "FINISHED")
    (root / "sbx").symlink_to(outside / "sbx")
    (root / "linkdir").symlink_to(outside)
    (root / "store.git").symlink_to(outside / "base.git")
    snap = tree_hashes(outside)
    r = S.cleanup(root, execute=True, repo=T.REPO)
    prot = S.protected_paths(T.REPO)
    alias = base / "alias"
    alias.symlink_to(root)
    try:
        S.cleanup(alias, execute=True, repo=T.REPO)
        alias_refused = False
    except S.ScratchRefusal as e:
        alias_refused = e.code == "ROOT_SYMLINK"
    out = {"nothing_listed_or_deleted": r["units"] == [] and r["deleted"] == [],
           "outside_byte_identical": tree_hashes(outside) == snap and (root / "sbx").is_symlink(),
           "root_alias_refused": alias_refused,
           "via_symlinked_parent": S._verify_unit(root / "linkdir" / "sbx", "sandbox_clone", root, prot) ==
           "SYMLINK_OR_ALIAS",
           "outside_root": S._verify_unit(outside / "sbx", "sandbox_clone", root, prot) == "LEAVES_ROOT"}
    return {"ok": all(out.values()), "cases": out}


def t_cleanup_never_touches_repository():
    """Refs, the target marker, the pending-result ref, the spool, seals, committed evidence and worktrees are never
    touched. A PLANTED repository (a worktree, campaign refs -- marker, pending, journal, ckpt --, a spool with a result
    in its git dir and in its worktree's git dir, a committed evidence file, a seal commit) is the protected set: every
    root that is, lies under or contains its worktrees or its common dir (spool included) is refused ROOT_PROTECTED; a
    FINISHED scratch root holding symlinks into it and a --shared clone of it deletes nothing; afterwards every ref and
    every file of the planted repository is unchanged. The real repository's worktrees, common dir, the campaign's
    qualified paths and MB r1's git dir are in the default protected set, and a root naming the real worktree or common
    dir refuses before anything is walked (dry-run). A bare store under a protected path is refused PROTECTED."""
    S = SCR()
    base = fresh_dir("repo")
    P = tiny_repo(base / "P")
    (P / "level4" / "evidence").mkdir(parents=True)
    (P / "level4" / "evidence" / "E.json").write_text('{"sealed": "planted"}\n')
    git(P, "add", "-f", "level4")
    git(P, "commit", "-q", "-m", "planted seal")
    head = git(P, "rev-parse", "HEAD")
    for ref in ("target-consumed", "pending-result", "journal", "ckpt"):
        git(P, "update-ref", T.PREFIX + ref, head)
    git(P, "worktree", "add", "-q", str(base / "P_wt"), "-b", "other")
    common = Path(git(P, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    wt_gd = Path(git(base / "P_wt", "rev-parse", "--path-format=absolute", "--git-dir"))
    for gd in (common, wt_gd):
        (gd / "mbs308-spool").mkdir()
        (gd / "mbs308-spool" / "result.json").write_text('{"planted": "result"}\n')
    refs0 = git(P, "for-each-ref", "--format=%(refname) %(objectname)")
    snap = {"P": tree_hashes(P), "wt": tree_hashes(base / "P_wt")}
    out = {}
    for name, root in (("worktree", P), ("common_dir", common), ("worktree_git_dir", wt_gd),
                       ("second_worktree", base / "P_wt"), ("spool", common / "mbs308-spool"),
                       ("committed_evidence_dir", P / "level4" / "evidence"), ("contains_repository", base)):
        try:
            S.cleanup(Path(os.path.realpath(root)), execute=True, repo=P)
            out[name] = False
        except S.ScratchRefusal as e:
            out[name] = e.code == "ROOT_PROTECTED"
    scratch = base.parent / (base.name + "_scratch")
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir()
    plant_record(scratch, dead_identity(), "FINISHED")
    (scratch / "link_common").symlink_to(common)
    (scratch / "refs.git").symlink_to(common)
    (scratch / "link_wt").symlink_to(base / "P_wt")
    sandbox_clone(P, scratch / "t" / "sbx")                        # a clone borrowing from the protected repository
    r = S.cleanup(scratch, execute=True, repo=P)
    out["scratch_with_links_deletes_nothing"] = r["deleted"] == [] and (scratch / "t" / "sbx").is_dir()
    out["planted_repository_unchanged"] = git(P, "for-each-ref", "--format=%(refname) %(objectname)") == refs0 and \
        tree_hashes(P) == snap["P"] and tree_hashes(base / "P_wt") == snap["wt"]
    prot = S.protected_paths(T.REPO)
    real_common = os.path.realpath(git(T.REPO, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    out["real_set"] = all(os.path.realpath(x) in prot for x in (T.REPO, real_common, str(S.LOGS_DIR))) and \
        all(os.path.realpath(x) in prot for x in S._driver_paths(T.code_dir()))
    for name, root in (("real_worktree", T.REPO), ("real_common_dir", Path(real_common))):
        try:
            S.cleanup(Path(os.path.realpath(root)), execute=False, repo=T.REPO)
            out[name] = False
        except S.ScratchRefusal as e:
            out[name] = e.code == "ROOT_PROTECTED"
    R = base.parent / (base.name + "_prot")
    if R.exists():
        shutil.rmtree(R)
    R.mkdir()
    plant_record(R, dead_identity(), "FINISHED")
    q = bare_store(P, R / "Q.git")
    out["unit_under_protected"] = S._verify_unit(q, "bare_base_store", R, [os.path.realpath(q)]) == "PROTECTED"
    return {"ok": all(out.values()), "cases": out}


# ====================================================================== the gated heavy phases
def t_run_gated_phases():
    """The heavy-phase runner the verifier and the mutant runner share (mbs308_scratch.run_gated): a failing start
    check runs NOTHING; a check failing before the second phase stops there (the first ran, the rest are listed as not
    run, the refusal recorded); a malformed check fails closed; a phase is cleaned only after its result is verified."""
    S = SCR()
    ph = [("a", 1), ("b", 2), ("c", 3)]

    def go(fail_at=None, malformed=None, verified=lambda r: True):
        ran, cleaned = [], []

        def gate(n):
            if n == malformed:
                return {"pass": "yes"}
            return {"pass": n != fail_at, "readings": [{"free_bytes": 1}]}
        g = S.run_gated(ph, gate=gate, run=lambda n, p: ran.append(n) or {"n": n}, verified=verified,
                        clean=lambda n, r: cleaned.append(n) or {"deleted": 1})
        return g, ran, cleaned
    g1, r1, c1 = go(fail_at="start")
    g2, r2, c2 = go(fail_at="b")
    g3, r3, c3 = go(verified=lambda r: r["n"] != "b")
    g4, r4, _ = go(malformed="start")
    g5, r5, _ = go(malformed="c")
    out = {"start_refusal_runs_nothing": r1 == [] and g1["not_run"] == ["a", "b", "c"] and
           g1["refusal"]["phase"] == "start",
           "stops_before_b": r2 == ["a"] and g2["not_run"] == ["b", "c"] and g2["refusal"]["phase"] == "b",
           "all_ran": r3 == ["a", "b", "c"] and g3["refusal"] is None and g3["not_run"] == [],
           "cleaned_only_verified": c3 == ["a", "c"] and sorted(g3["cleanups"]) == ["a", "c"],
           "malformed_start_fails_closed": r4 == [] and g4["refusal"]["phase"] == "start",
           "malformed_phase_fails_closed": r5 == ["a", "b"] and g5["not_run"] == ["c"]}
    return {"ok": all(out.values()), "cases": out}


def t_mutant_runner_disk_gate_and_cleanup():
    """The REAL mutant runner (tests/test_mbs308_mutants.py, --only M11): with a planted insufficient reading it
    refuses at the start (nothing runs, no mutated code is made, no sandbox created, the report fails); unplanted, it
    kills M11 by assertion, the unmutated target passes, and each phase's sandbox is DELETED once its result file is
    verified (no sbx directory remains; the deletions are recorded; the result files stay)."""
    root = fresh_dir("runner")
    env = dict(T.GENV, MBS308_SCRATCH=str(root), MBS308_BASE_STORE=str(T.BASE_STORE))
    runner = T.NSS / "tests" / "test_mbs308_mutants.py"
    out_low = root / "low.json"
    p = subprocess.run([T.PY, "-I", "-S", "-B", str(runner), "--only", "M11", "--out", str(out_low)],
                       capture_output=True, text=True, env=dict(env, MBS308_TEST_DISK_FREE="1"),
                       stdin=subprocess.DEVNULL, timeout=600)
    low = json.loads(out_low.read_text())
    tm = root / "t_mutants"
    refused = p.returncode == 1 and (low.get("disk_refusal") or {}).get("phase") == "start" and \
        low["matrix"] == {} and low["unmutated"] == {} and len(low["not_run"]) == 2 and \
        not (tm / "UNMUTATED" / "code").exists() and not list(tm.rglob("sbx"))
    out_ok = root / "ok.json"
    p2 = subprocess.run([T.PY, "-I", "-S", "-B", str(runner), "--only", "M11", "--out", str(out_ok)],
                        capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL, timeout=1800)
    rep = json.loads(out_ok.read_text())
    cl = rep.get("cleanups", {})
    cleaned = p2.returncode == 0 and rep["matrix"]["M11"]["killed"] is True and \
        rep["matrix"]["M11"]["test_passed"] is False and not rep["matrix"]["M11"].get("error") and \
        rep["unmutated_all_pass"] is True and set(cl) == {"UNMUTATED state::t_computing_then_interrupted", "M11"} and \
        all(v.get("deleted", 0) >= 1 for v in cl.values()) and not list(tm.rglob("sbx")) and \
        (tm / "M11" / "result.json").is_file() and (tm / "UNMUTATED" / "result.json").is_file() and \
        all((tm / t / "scratch" / T.infra_scratch().DELETIONS_LOG).is_file() for t in ("M11", "UNMUTATED"))
    return {"ok": refused and cleaned, "refused_at_start": refused, "cleaned_after_verified": cleaned,
            "peak_scratch_bytes": rep.get("scratch_meter", {}).get("peak_bytes"),
            "bytes_deleted": {k: v.get("bytes_deleted") for k, v in cl.items()}}


def _verifier_copy(tag: str) -> Path:
    """A copy of the namespace's code / config / tests at the namespace's relative path under a scratch directory
    (NOT a repository): the verifier's start gate must refuse before anything else is read."""
    d = fresh_dir(tag)
    ns = d / T.NS_REL
    for sub in ("config", "tests", "protocol"):
        shutil.copytree(T.NSS / sub, ns / sub, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(T.code_dir(), ns / "code", ignore=shutil.ignore_patterns("__pycache__"))
    return ns


def t_verifier_disk_gate():
    """The qualification verifier refuses on insufficient or unreadable disk at its START, before anything else (no
    precondition, no work directory, no record under qualification/, no --out): official mode with a planted
    insufficient reading, dev mode with a planted failed probe. Control: without the plant the official run gets past
    the disk gate (it then stops on its preconditions, which a copy outside a repository cannot meet)."""
    ns = _verifier_copy("verifier")
    q = ns / "code" / "mbs308_qualify.py"
    w = ns.parents[4].parent / (ns.parents[4].name + "_work")      # outside the copy (the verifier's REPO)
    if w.exists():
        shutil.rmtree(w)
    runs = {}
    for name, args, plant in (("official_low", [str(q), "--work", str(w)], "1"),
                              ("dev_failed_probe", [str(q), "--dev", "--work", str(w), "--only", "QC11-S", "--out",
                                                    str(w.parent / "verifier_o.json")], "fail"),
                              ("official_control", [str(q), "--work", str(w)], None)):
        env = dict(T.GENV) if plant is None else dict(T.GENV, MBS308_TEST_DISK_FREE=plant)
        p = subprocess.run([T.PY, "-I", "-S", "-B", *args], capture_output=True, text=True, env=env,
                           cwd=str(ns.parents[4]), stdin=subprocess.DEVNULL, timeout=300)
        runs[name] = (p.returncode, "QUALIFY REFUSED: DISK" in p.stdout)
    nothing = not w.exists() and not (ns / "qualification").exists() and not (w.parent / "verifier_o.json").exists()
    ok = runs["official_low"] == (2, True) and runs["dev_failed_probe"] == (2, True) and \
        runs["official_control"][1] is False and nothing
    return {"ok": ok, "runs": {k: list(v) for k, v in runs.items()}, "nothing_written": nothing}


def t_verifier_heavy_phase_gated_and_cleaned():
    """The verifier's heavy phases go through the gate and the cleanup (a dev --heavy run of QS-STATIC in a sparse
    sandbox of the base store): the report records the start check and the check before QS-STATIC (both passing, with
    the thresholds), the suite ran and passed, and its sandboxes were deleted after its record was verified (the
    suites' scratch root keeps no sbx)."""
    sys.path.insert(0, str(T.NSS / "tests"))
    import test_mbs308_qualify as TQ
    s = TQ.sparse_sandbox("disk_heavy")
    out = s["tmp"] / "dev_heavy.json"
    p = subprocess.run([T.PY, "-I", "-S", "-B", str(s["dst"] / "code/mbs308_qualify.py"), "--dev", "--heavy",
                        "--work", str(s["tmp"] / "work"), "--only", "QS-STATIC", "--out", str(out)],
                       capture_output=True, text=True, env=T.GENV, cwd=str(s["root"]), stdin=subprocess.DEVNULL,
                       timeout=1800)
    try:
        rep = json.loads(out.read_text())
    except (OSError, ValueError):
        return {"ok": False, "tail": (p.stdout + p.stderr)[-800:]}
    d = rep.get("disk", {})
    left = [x for x in (s["tmp"] / "work").rglob("sbx")]
    ok = p.returncode == 0 and (rep["cases"]["QS-STATIC"].get("n") or 0) > 0 and \
        [c["phase"] for c in d.get("checks", [])] == ["start", "QS-STATIC"] and \
        all(c["pass"] for c in d["checks"]) and d["start"]["pass"] is True and \
        d["threshold_bytes"] == SCR().QUAL_MIN_FREE_BYTES and \
        d["cleanups"].get("QS-STATIC", {}).get("deleted", 0) >= 1 and left == []
    shutil.rmtree(s["tmp"], ignore_errors=True)
    return {"ok": ok, "checks": d.get("checks"), "cleanup": d.get("cleanups"), "sbx_left": len(left),
            "static_suite": {k: rep["cases"]["QS-STATIC"].get(k) for k in ("n", "passed", "failed", "pass")}}


HOST_ITEMS = {"automatic_os_installation_disabled", "automatic_restart", "ac_power", "sleep_prevention_and_lid",
              "thermal_level_0", "lowpowermode_0", "disk_execution", "disk_qualification", "memory_pressure_normal",
              "free_memory", "boot_identity", "host_identity_platform_pins", "host_exclusive", "no_other_campaign_job"}


def _settings() -> dict:
    """The host settings the report reads, read here independently (read-only): pmset -g values and the
    SoftwareUpdate keys."""
    pm = subprocess.run(["/usr/bin/pmset", "-g"], capture_output=True, text=True, env=T.GENV).stdout
    vals = {}
    for ln in pm.splitlines():
        parts = ln.split()
        if len(parts) >= 2 and parts[0] in ("autorestart", "sleep", "displaysleep", "disksleep", "lowpowermode"):
            vals[parts[0]] = parts[1]
    for k in ("AutomaticallyInstallMacOSUpdates", "AutomaticDownload", "CriticalUpdateInstall", "ConfigDataInstall"):
        vals[k] = subprocess.run(["/usr/bin/defaults", "read", "/Library/Preferences/com.apple.SoftwareUpdate", k],
                                 capture_output=True, text=True, env=T.GENV).stdout.strip()
    return vals


def t_verifier_host_report_read_only():
    """--host-report (protocol section 8.1; task 5): the READ-ONLY host-readiness checklist from the verifier's own code
    (a sparse sandbox of the base store): exit 0, every checklist item present with how it is checked and a status of
    the allowed set, `read_only` true and `changes_made` false, `ready` exactly when every item is READY or RECORDED;
    the host settings it reads are the same after it ran; the report's code path names no command that writes a
    setting; combined with another mode it refuses."""
    import ast as _ast
    sys.path.insert(0, str(T.NSS / "tests"))
    import test_mbs308_qualify as TQ
    s = TQ.sparse_sandbox("host_report")
    q = s["dst"] / "code/mbs308_qualify.py"
    before = _settings()
    out = s["tmp"] / "host_report.json"
    p = subprocess.run([T.PY, "-I", "-S", "-B", str(q), "--host-report", "--out", str(out)], capture_output=True,
                       text=True, env=T.GENV, cwd=str(s["root"]), stdin=subprocess.DEVNULL, timeout=600)
    after = _settings()
    try:
        rep = json.loads(out.read_text())
    except (OSError, ValueError):
        return {"ok": False, "tail": (p.stdout + p.stderr)[-800:]}
    items = {i["item"]: i for i in rep["items"]}
    src = (T.code_dir() / "mbs308_qualify.py").read_text()
    cmds, writers = [], []
    for fn in _ast.parse(src).body:                 # the report's own code: its command vectors and any write call
        if not (isinstance(fn, _ast.FunctionDef) and fn.name in ("host_report", "_clamshell", "_pmset_values",
                                                                 "_pmset_sched")):
            continue
        for node in _ast.walk(fn):
            if isinstance(node, _ast.List) and node.elts and isinstance(node.elts[0], _ast.Constant) and \
                    str(node.elts[0].value).startswith("/"):
                cmds.append([getattr(e, "value", "?") for e in node.elts])
            if isinstance(node, _ast.Call):
                name = node.func.attr if isinstance(node.func, _ast.Attribute) else getattr(node.func, "id", "")
                if name in ("write", "write_text", "write_bytes", "open", "unlink", "rename", "replace", "mkdir",
                            "chmod", "system", "Popen", "run"):
                    writers.append(name)
    queries_only = sorted(cmds) == [["/usr/bin/pmset", "-g"], ["/usr/bin/pmset", "-g", "sched"],
                                    ["/usr/sbin/ioreg", "-r", "-k", "AppleClamshellState", "-d", "1"]]
    r2 = subprocess.run([T.PY, "-I", "-S", "-B", str(q), "--host-report", "--dev", "--out", str(s["tmp"] / "x.json")],
                        capture_output=True, text=True, env=T.GENV, cwd=str(s["root"]), stdin=subprocess.DEVNULL,
                        timeout=120)
    ok = p.returncode == 0 and set(items) == HOST_ITEMS and all(
        i["status"] in ("READY", "NOT_READY", "USER_ACTION", "RECORDED", "UNKNOWN") and i["checked_by"]
        for i in items.values()) and rep["read_only"] is True and rep["changes_made"] is False and \
        rep["ready"] == all(i["status"] in ("READY", "RECORDED") for i in items.values()) and before == after and \
        writers == [] and queries_only and r2.returncode == 2 and "REFUSED" in r2.stdout and \
        not (s["tmp"] / "x.json").exists()
    shutil.rmtree(s["tmp"], ignore_errors=True)
    return {"ok": ok, "statuses": {k: v["status"] for k, v in items.items()}, "write_calls": writers,
            "commands": cmds, "settings_unchanged": before == after}


# ====================================================================== the re-pin tooling (task 2)
def _run_tool(args, cwd=None) -> tuple:
    p = subprocess.run([T.PY, "-I", "-S", "-B", *args], capture_output=True, text=True, env=T.GENV,
                       stdin=subprocess.DEVNULL, cwd=cwd, timeout=300)
    try:
        return p.returncode, json.loads(p.stdout)
    except ValueError:
        return p.returncode, {"raw": (p.stdout + p.stderr)[-600:]}


def t_repin_helpers_and_platform():
    """code/mbs308_repin.py on a COPY of the code: helpers -- dry-run reports a planted stale helper and writes
    nothing; --write rewrites exactly that pin (one line of the driver changes) and the table is clean afterwards.
    platform -- the tool's readings are the driver's own platform_readings() on this host (read in a sandbox child);
    a planted pin mismatch is reported and nothing written in dry-run; --write alone is refused; --write-platform
    rewrites exactly that pin (one line)."""
    d = fresh_dir("repin")
    code = d / "code"
    shutil.copytree(T.code_dir(), code, ignore=shutil.ignore_patterns("__pycache__"))
    tool, drv = code / "mbs308_repin.py", code / "mbs308_driver.py"
    out = {}
    rc0, r0 = _run_tool([str(tool), "helpers", "--code", str(code)])
    out["clean_copy"] = rc0 == 0 and r0.get("stale") == []
    (code / "mbs308_host.py").write_text((code / "mbs308_host.py").read_text() + "# planted\n")
    b0 = drv.read_bytes()
    rc1, r1 = _run_tool([str(tool), "helpers", "--code", str(code)])
    out["dry_run_reports_writes_nothing"] = rc1 == 1 and r1.get("stale") == ["mbs308_host.py"] and \
        drv.read_bytes() == b0
    rc2, r2 = _run_tool([str(tool), "helpers", "--code", str(code), "--write"])
    changed = [(a, b) for a, b in zip(b0.decode().splitlines(), drv.read_text().splitlines()) if a != b]
    out["write_one_pin"] = rc2 == 0 and r2.get("written") is True and r2.get("after") == [] and \
        len(changed) == 1 and '"mbs308_host.py"' in changed[0][1] and \
        hashlib.sha256((code / "mbs308_host.py").read_bytes()).hexdigest() in changed[0][1]
    rc3, r3 = _run_tool([str(tool), "platform", "--code", str(code)])
    drv_readings = T.child(sb(), "platform")["out"]["platform"]
    out["readings_equal_driver"] = rc3 == 0 and r3.get("differs") == [] and \
        {k: v["reading"] for k, v in r3["pins"].items()} == drv_readings
    b1 = drv.read_text()
    drv.write_text(b1.replace('"os_build": "', '"os_build": "PLANTED', 1))
    b2 = drv.read_bytes()
    rc4, r4 = _run_tool([str(tool), "platform", "--code", str(code)])
    out["mismatch_reported_not_written"] = rc4 == 1 and r4.get("differs") == ["os_build"] and drv.read_bytes() == b2
    rc5, r5 = _run_tool([str(tool), "platform", "--code", str(code), "--write"])
    out["plain_write_refused"] = rc5 == 2 and r5.get("refused") == "FLAG" and drv.read_bytes() == b2
    rc6, r6 = _run_tool([str(tool), "platform", "--code", str(code), "--write-platform"])
    ch = [(a, b) for a, b in zip(b2.decode().splitlines(), drv.read_text().splitlines()) if a != b]
    out["write_platform_one_pin"] = rc6 == 0 and r6.get("written") is True and r6.get("after") == [] and \
        len(ch) == 1 and '"os_build"' in ch[0][1] and drv.read_text() == b1
    return {"ok": all(out.values()), "cases": out}


def t_repin_driver_diff():
    """The DRIVER_DIFF.md generator: against the real repository (read only; the working files are copies) it first
    reproduces the COMMITTED DRIVER_DIFF.md from the committed driver byte for byte, and the working DRIVER_DIFF.md is
    exactly its output for the working driver (no hunk touches a carried definition). In a sandbox: a committed DRIVER_DIFF.md that the
    generator does not reproduce is refused (GENERATOR_NOT_VALIDATED); a stale working file is reported and left
    untouched in dry-run, and --write makes it current."""
    tool = T.code_dir() / "mbs308_repin.py"
    copy = fresh_dir("repin_dd") / "ns"                            # the working files, COPIED: never written in place
    (copy / "code").mkdir(parents=True)
    shutil.copy2(T.NSS / "code" / "mbs308_driver.py", copy / "code" / "mbs308_driver.py")
    shutil.copy2(T.NSS / "DRIVER_DIFF.md", copy / "DRIVER_DIFF.md")
    rc, r = _run_tool([str(tool), "driver-diff", "--ns", str(copy), "--repo", str(T.REPO)])
    out = {"real_validated_and_current": rc == 0 and r.get("validated_against_head") is True and
           r.get("stale") is False and r.get("science_glue_hunks") == [] and r.get("written") is False}
    s = sb()
    s.grant_chain()
    ns = s.root / T.NS_REL
    md = ns / "DRIVER_DIFF.md"
    shutil.copy2(T.NSS / "DRIVER_DIFF.md", md)                     # the sandbox copies code / tests / protocol only
    s.commit([T.NS_REL + "/DRIVER_DIFF.md"], "sandbox: DRIVER_DIFF.md of the namespace")
    rc1, r1 = _run_tool([str(tool), "driver-diff", "--ns", str(ns), "--repo", str(s.root)])
    out["sandbox_validated"] = rc1 == 0 and r1.get("validated_against_head") is True
    good = md.read_bytes()
    md.write_bytes(good + b"planted line\n")
    rc2, r2 = _run_tool([str(tool), "driver-diff", "--ns", str(ns), "--repo", str(s.root)])
    out["stale_reported_untouched"] = rc2 == 1 and r2.get("stale") is True and md.read_bytes() == good + \
        b"planted line\n"
    rc3, r3 = _run_tool([str(tool), "driver-diff", "--ns", str(ns), "--repo", str(s.root), "--write"])
    out["write_makes_current"] = rc3 == 0 and r3.get("written") is True and md.read_bytes() == good
    md.write_bytes(good + b"planted committed change\n")
    s.commit([T.NS_REL + "/DRIVER_DIFF.md"], "sandbox: planted DRIVER_DIFF.md change")
    rc4, r4 = _run_tool([str(tool), "driver-diff", "--ns", str(ns), "--repo", str(s.root)])
    out["unreproduced_commit_refused"] = rc4 == 2 and r4.get("refused") == "GENERATOR_NOT_VALIDATED"
    s.grant_chain()                                                # back to the synthetic freeze
    return {"ok": all(out.values()), "cases": out}


def t_tree_meter():
    """The measurement helper counts allocated bytes (each inode once, symlinks not followed) and keeps the peak."""
    S = SCR()
    d = fresh_dir("meter")
    (d / "a").write_bytes(b"x" * 300000)
    os.link(d / "a", d / "b")
    (d / "c").symlink_to("/usr/bin")
    one = S.tree_bytes(d)
    m = S.TreeMeter(d, 0.2).start()
    (d / "big").write_bytes(b"y" * 2000000)
    time.sleep(0.6)
    (d / "big").unlink()
    r = m.stop()
    return {"ok": 300000 <= one < 300000 + 64 * 1024 and r["peak_bytes"] >= 2000000 + 300000 and r["samples"] >= 2
            and r["final_bytes"] < r["peak_bytes"], "tree_bytes": one, "meter": r}


# ====================================================================== reviewQ6's repairs (builder7, research brief 56)
def _store_root(base: Path, name: str) -> tuple:
    """A FINISHED root R1 (dead owner) holding a bare base store and one sandbox clone of it."""
    root = base / name
    root.mkdir(parents=True)
    src = tiny_repo(base / (name + "_src"))
    store = bare_store(src, root / "work" / "base.git")
    clone = sandbox_clone(store, root / "work" / "t_x" / "sbx")
    if "dead" not in _S:
        _S["dead"] = dead_identity()
    plant_record(root, _S["dead"], "FINISHED")
    return root, store, clone


def t_base_store_borrowed_in_root_kept():
    """R2, the in-root rule (reviewQ6 G-3; protocol 8.2 "a store still borrowed is kept"): a base store goes only
    after every clone under the cleaned root that borrows from it. A FINISHED root holds a store and a clone of it; a
    NESTED root holds a second clone of the SAME store, which the store's register does not name (so only the in-root
    rule can protect it). While the nested root is ACTIVE its clone is kept, and so is the store (BASE_STORE_IN_USE,
    in the dry run and in the execution): the nested clone still reads its HEAD. Control: with the nested root
    FINISHED both clones go, and the store after them."""
    S = SCR()
    base = fresh_dir("inroot")
    out = {}
    for case in ("nested_active", "nested_finished"):
        root, store, c1 = _store_root(base, case)
        inner = root / "inner"
        inner.mkdir()
        c2 = sandbox_clone(store, inner / "t" / "sbx")
        plant_borrower(store, _S["dead"], "FINISHED", clones=[c1])
        if case == "nested_active":
            S.begin(inner, "t")                                    # this process uses the nested root
        else:
            plant_record(inner, _S["dead"], "FINISHED")
        dry = S.cleanup(root, repo=T.REPO)
        ex = S.cleanup(root, execute=True, repo=T.REPO)
        why = {u["path"]: u["reason"] for u in dry["units"]}
        refused = {x["path"]: x["reason"] for x in ex["refused"]}
        deleted = [d["path"] for d in ex["deleted"]]
        if case == "nested_active":
            out[case] = why == {"inner/t/sbx": "ROOT_ACTIVE", "work/t_x/sbx": None,
                                "work/base.git": "BASE_STORE_IN_USE"} and deleted == ["work/t_x/sbx"] and \
                refused == {"inner/t/sbx": "ROOT_ACTIVE", "work/base.git": "BASE_STORE_IN_USE"} and \
                store.is_dir() and c2.is_dir() and head_readable(c2) and not c1.exists()
        else:
            out[case] = all(v is None for v in why.values()) and \
                deleted == ["inner/t/sbx", "work/t_x/sbx", "work/base.git"] and not store.exists()
    return {"ok": all(out.values()), "cases": out}


def t_base_store_borrowed_cross_root_kept():
    """R2, the cross-root rule (reviewQ6 F-2): a base store in a FINISHED root R1 is never deleted while a borrower
    elsewhere may live. A sandbox in ANOTHER root R2 borrows the store's objects (R2 is not under R1, so no scan of R1
    can see it). Cleaning R1 KEEPS the store, and R2's sandbox still reads its HEAD, when: the store has no borrower
    register, or an empty one (it cannot be shown to be unborrowed: BASE_STORE_BORROWERS_UNRECORDED); its register
    holds an ACTIVE record of a live process, a FINISHED record of a live process, a FINISHED record of a live process
    whose `ps` fails (UNKNOWN is never dead), an ACTIVE record of a dead process (it never finished), an invalid
    record or a symlinked record (BASE_STORE_IN_USE); or every record is FINISHED and dead but one names R2's clone,
    which still exists and still borrows (BASE_STORE_IN_USE). R1's own clone goes in every case. Control: every
    record FINISHED and dead and no named clone left: the store is deleted, after R1's clone, and the deletion is
    recorded."""
    S = SCR()
    H = S.HOST
    base = fresh_dir("crossroot")
    out, reasons = {}, {}
    h = T.Helper(300)
    real_start = H.process_start
    try:
        live = H.identity(h.p.pid)
        dead = dead_identity()
        other = base / "valid_record_elsewhere.json"
        cases = {
            "unrecorded": (lambda st, c2: None, "BASE_STORE_BORROWERS_UNRECORDED"),
            "empty_register": (lambda st, c2: (st / S.BORROW_DIR).mkdir(), "BASE_STORE_BORROWERS_UNRECORDED"),
            "live_active": (lambda st, c2: plant_borrower(st, live, "ACTIVE"), "BASE_STORE_IN_USE"),
            "live_finished": (lambda st, c2: plant_borrower(st, live, "FINISHED"), "BASE_STORE_IN_USE"),
            "live_ps_failing": (lambda st, c2: plant_borrower(st, live, "FINISHED"), "BASE_STORE_IN_USE"),
            "dead_active": (lambda st, c2: plant_borrower(st, dead, "ACTIVE"), "BASE_STORE_IN_USE"),
            "invalid_record": (lambda st, c2: ((st / S.BORROW_DIR).mkdir(),
                                               (st / S.BORROW_DIR / "1-x.json").write_text("{not json")),
                               "BASE_STORE_IN_USE"),
            "symlinked_record": (lambda st, c2: ((st / S.BORROW_DIR).mkdir(),
                                                 (st / S.BORROW_DIR / "1-x.json").symlink_to(other)),
                                 "BASE_STORE_IN_USE"),
            "dead_finished_clone_remains": (lambda st, c2: plant_borrower(st, dead, "FINISHED", clones=[c2]),
                                            "BASE_STORE_IN_USE"),
        }
        for case, (plant, want) in cases.items():
            root, store, c1 = _store_root(base, case)
            c2 = sandbox_clone(store, base / (case + "_R2") / "t" / "sbx")
            plant_record(base / (case + "_R2"), live, "ACTIVE")
            if case == "symlinked_record":
                other.write_text(json.dumps({"schema": S.BORROW_SCHEMA, "store": str(store), "owner": dead,
                                             "purpose": "planted", "state": "FINISHED", "clones": []}))
            plant(store, c2)
            if case == "live_ps_failing":
                H.process_start = lambda pid, text=None: None if int(pid) == h.p.pid else real_start(pid, text)
            try:
                dry = S.cleanup(root, repo=T.REPO)
                ex = S.cleanup(root, execute=True, repo=T.REPO)
            finally:
                H.process_start = real_start
            got = {x["path"]: x["reason"] for x in ex["refused"]}
            reasons[case] = got.get("work/base.git")
            out[case] = got == {"work/base.git": want} and [d["path"] for d in ex["deleted"]] == ["work/t_x/sbx"] and \
                {u["path"]: u["reason"] for u in dry["units"]} == {"work/t_x/sbx": None, "work/base.git": want} and \
                store.is_dir() and head_readable(c2)
        # control: nothing borrows any more
        root, store, c1 = _store_root(base, "free")
        gone = base / "free_R2" / "t" / "sbx"                          # a recorded clone that no longer exists
        plant_borrower(store, dead, "FINISHED", clones=[c1, gone])
        ex = S.cleanup(root, execute=True, repo=T.REPO)
        log = [json.loads(x)["path"] for x in (root / S.DELETIONS_LOG).read_text().splitlines()]
        out["control_unborrowed_store_goes"] = [d["path"] for d in ex["deleted"]] == ["work/t_x/sbx", "work/base.git"] \
            and ex["refused"] == [] and not store.exists() and log == ["work/t_x/sbx", "work/base.git"]
    finally:
        H.process_start = real_start
        h.kill()
    return {"ok": all(out.values()), "cases": out, "reasons": reasons}


def t_borrower_records_and_library():
    """R2, the records themselves: begin_borrow writes the calling process's ACTIVE record INSIDE the store,
    borrow_clone names a clone before it is made, finish_borrow marks it FINISHED; only the owner changes its record
    and a finished record names no new clone; a register that is a symlink is refused. Through cleanup: while this
    process's record is ACTIVE the store is kept; once FINISHED it is still kept while the clone it named exists in
    another root; once that clone is gone the store goes. And the TEST LIBRARY does it for every suite process: this
    process has an ACTIVE record inside the suite's own base store, and the full sandbox the library made is named in
    it (so that store reads in use)."""
    S = SCR()
    base = fresh_dir("borrow")
    out = {}
    root, store, c1 = _store_root(base, "R1")
    shutil.rmtree(c1)
    rec = S.begin_borrow(store, "planted borrower")
    j0 = json.loads(rec.read_text())
    out["record_inside_the_store_active"] = rec.parent == Path(os.path.realpath(store)) / S.BORROW_DIR and \
        j0["state"] == "ACTIVE" and j0["owner"]["pid"] == os.getpid() and j0["schema"] == S.BORROW_SCHEMA and \
        j0["clones"] == []
    c2 = base / "R2" / "t" / "sbx"
    S.borrow_clone(rec, c2)
    out["clone_named_before_it_exists"] = not c2.exists() and \
        json.loads(rec.read_text())["clones"] == [os.path.realpath(c2)]
    sandbox_clone(store, c2)
    b = S.store_borrowers(store)
    out["active_record_reads_in_use"] = b["recorded"] is True and len(b["reasons"]) == 1 and \
        b["reasons"][0].startswith("BORROWER_NOT_FINISHED") and b["clones"] == [os.path.realpath(c2)]
    r1 = S.cleanup(root, execute=True, repo=T.REPO)
    out["kept_while_active"] = r1["deleted"] == [] and store.is_dir() and \
        [x["reason"] for x in r1["refused"]] == ["BASE_STORE_IN_USE"]
    S.finish_borrow(rec)
    out["finished"] = json.loads(rec.read_text())["state"] == "FINISHED" and S.store_borrowers(store)["reasons"] == []
    r2 = S.cleanup(root, execute=True, repo=T.REPO)
    out["kept_while_the_named_clone_borrows"] = r2["deleted"] == [] and store.is_dir() and head_readable(c2) and \
        [x["reason"] for x in r2["refused"]] == ["BASE_STORE_IN_USE"]
    for call, code in ((lambda: S.borrow_clone(rec, base / "R3" / "sbx"), "BORROW_NOT_ACTIVE"),
                       (lambda: S.finish_borrow(plant_borrower(store, dead_identity(), "ACTIVE")), "NOT_OWNER")):
        try:
            call()
            out[code] = False
        except S.ScratchRefusal as e:
            out[code] = e.code == code
    for f in (store / S.BORROW_DIR).iterdir():                      # back to the one finished record of this process
        if f != rec:
            f.unlink()
    shutil.rmtree(c2)
    r3 = S.cleanup(root, execute=True, repo=T.REPO)
    out["goes_once_nothing_borrows"] = [d["path"] for d in r3["deleted"]] == ["work/base.git"] and not store.exists()
    linked = bare_store(base / "R1_src", base / "linked.git")
    (base / "elsewhere").mkdir()
    (linked / S.BORROW_DIR).symlink_to(base / "elsewhere")
    try:
        S.begin_borrow(linked, "t")
        out["register_symlink_refused"] = False
    except S.ScratchRefusal as e:
        out["register_symlink_refused"] = e.code == "BORROW_REGISTER" and list((base / "elsewhere").iterdir()) == []
    # the test library, BY ITSELF (this test never calls its borrow functions): making a sandbox through it records
    # this suite process as a borrower inside the suite's own base store and names the sandbox
    I = T.infra_scratch()
    full = sb()
    held = dict(T._BORROW)
    mine = Path(held["record"]) if held.get("pid") == os.getpid() and held.get("record") else None
    jm = json.loads(mine.read_text()) if mine is not None and mine.is_file() else {}
    out["library_records_this_process"] = mine is not None and \
        mine.parent == Path(os.path.realpath(T.BASE_STORE)) / I.BORROW_DIR and \
        (jm.get("owner") or {}).get("pid") == os.getpid() and jm.get("state") == "ACTIVE" and \
        jm.get("schema") == I.BORROW_SCHEMA
    out["library_names_its_sandboxes"] = os.path.realpath(full.root) in (jm.get("clones") or [])
    lib = S.store_borrowers(T.BASE_STORE)
    out["library_store_reads_in_use"] = mine is not None and lib["recorded"] is True and \
        any(r.startswith("BORROWER_NOT_FINISHED " + mine.name) for r in lib["reasons"])
    # ... and it is not best effort: a store in which the record cannot be written is not used (no sandbox is made)
    saved_store = T.BASE_STORE
    T.BASE_STORE = linked                                           # its register is a symlink
    T._BORROW.clear()
    made, code = None, None
    try:
        try:
            T.Sandbox(base / "refused")
            made = True
        except Exception as e:                                      # noqa: BLE001 (the refusal is what is tested)
            made, code = False, getattr(e, "code", type(e).__name__)
    finally:
        T.BASE_STORE = saved_store
        T._BORROW.clear()
        T._BORROW.update(held)
    out["library_refuses_a_store_it_cannot_record_in"] = made is False and code == "BORROW_REGISTER" and \
        not (base / "refused" / "sbx").exists() and list((base / "elsewhere").iterdir()) == []
    return {"ok": all(out.values()), "cases": out}


def t_cleanup_records_before_deleting():
    """R3 (reviewQ6 F-3): no deletion is ever unrecorded. (a) A deletions log that cannot be opened -- a symlink (the
    reviewer's probe), a directory -- stops the pass before anything is deleted: DELETIONS_LOG_UNWRITABLE, every unit
    still there, every byte of the root unchanged, nothing written through the symlink, and the report (nothing
    deleted) comes with the refusal. (b) Each record is on disk BEFORE its unit goes: at the moment each deletion
    starts, the log's last line names that unit and the unit still exists. (c) A log that fails at the SECOND record:
    the first unit is deleted and recorded, the second is neither deleted nor recorded."""
    S = SCR()
    base = fresh_dir("logfirst")
    out = {}
    for case in ("symlink", "directory"):
        root = base / case
        root.mkdir()
        lay = layout(root)
        plant_record(root, _S["dead"], "FINISHED")
        target = base / (case + "_elsewhere.jsonl")
        if case == "symlink":
            target.write_text("")
            (root / S.DELETIONS_LOG).symlink_to(target)
        else:
            (root / S.DELETIONS_LOG).mkdir()
        snap = tree_hashes(root)
        code, rep = None, None
        try:
            S.cleanup(root, execute=True, repo=T.REPO)
        except S.ScratchRefusal as e:
            code, rep = e.code, getattr(e, "report", None)
        out[case] = code == "DELETIONS_LOG_UNWRITABLE" and all((root / u).is_dir() for u in lay["units"]) and \
            tree_hashes(root) == snap and (case != "symlink" or target.read_text() == "") and \
            isinstance(rep, dict) and rep["deleted"] == [] and rep["bytes_deleted"] == 0
    real_rmtree = shutil.rmtree

    def watched(root: Path, seen: list, after=None):
        def rm(path, *a, **k):
            log = root / S.DELETIONS_LOG
            lines = [json.loads(x) for x in log.read_text().splitlines()] if log.is_file() else []
            rel = str(Path(path).relative_to(root))
            seen.append({"unit": rel, "recorded_first": bool(lines) and lines[-1]["path"] == rel,
                         "still_there": Path(path).is_dir()})
            r = real_rmtree(path, *a, **k)
            if after is not None:
                after(rel)
            return r
        rm.avoids_symlink_attacks = real_rmtree.avoids_symlink_attacks
        return rm
    root = base / "order"
    root.mkdir()
    lay = layout(root)
    plant_record(root, _S["dead"], "FINISHED")
    seen: list = []
    shutil.rmtree = watched(root, seen)
    try:
        ex = S.cleanup(root, execute=True, repo=T.REPO)
    finally:
        shutil.rmtree = real_rmtree
    out["record_precedes_each_deletion"] = [x["unit"] for x in seen] == ["work/t_x/sbx", "work/base.git"] and \
        all(x["recorded_first"] and x["still_there"] for x in seen) and \
        [d["path"] for d in ex["deleted"]] == ["work/t_x/sbx", "work/base.git"]
    root = base / "second"
    root.mkdir()
    lay = layout(root)
    plant_record(root, _S["dead"], "FINISHED")
    seen2: list = []

    def break_log(rel):                                             # after the first deletion the log becomes a symlink
        log = root / S.DELETIONS_LOG
        if log.is_file() and not log.is_symlink():
            log.rename(root / "first_records.jsonl")
            log.symlink_to(base / "second_elsewhere.jsonl")
    shutil.rmtree = watched(root, seen2, break_log)
    code, rep = None, None
    try:
        S.cleanup(root, execute=True, repo=T.REPO)
    except S.ScratchRefusal as e:
        code, rep = e.code, getattr(e, "report", None)
    finally:
        shutil.rmtree = real_rmtree
    kept = [json.loads(x)["path"] for x in (root / "first_records.jsonl").read_text().splitlines()] \
        if (root / "first_records.jsonl").is_file() else None
    out["second_record_fails_second_unit_stays"] = code == "DELETIONS_LOG_UNWRITABLE" and \
        [x["unit"] for x in seen2] == ["work/t_x/sbx"] and kept == ["work/t_x/sbx"] and \
        (root / "work/base.git").is_dir() and not (root / "work/t_x/sbx").exists() and \
        not (base / "second_elsewhere.jsonl").exists() and isinstance(rep, dict) and \
        [d["path"] for d in rep["deleted"]] == ["work/t_x/sbx"]
    return {"ok": all(out.values()), "cases": out}


def t_cleanup_reverifies_before_deleting():
    """G-5 (reviewQ6): every unit is verified AGAIN just before its deletion. The state changes right after the first
    verification of a unit found disposable (planted through the module's own _verify_unit: the first call returns,
    then the change happens): (a) a process starts using the root (an ACTIVE record appears): the sandbox clone is
    refused ROOT_ACTIVE and stays; (b) a borrower records itself in the base store: the store is refused
    BASE_STORE_IN_USE and stays. In both, the unit was verified exactly twice and nothing was deleted after the
    change."""
    S = SCR()
    base = fresh_dir("reverify")
    out = {}
    real = S._verify_unit
    for case, kind in (("root_becomes_active", "sandbox_clone"), ("store_gets_a_borrower", "bare_base_store")):
        root, store, clone = _store_root(base, case)
        plant_borrower(store, _S["dead"], "FINISHED", clones=[clone])
        target = clone if kind == "sandbox_clone" else store
        calls: dict = {}

        def planted(unit, k, r, prot, _target=target, _case=case, _root=root, _store=store, _calls=calls):
            why = real(unit, k, r, prot)
            _calls[str(unit)] = _calls.get(str(unit), 0) + 1
            if unit == _target and _calls[str(unit)] == 1 and why is None:
                if _case == "root_becomes_active":
                    S.begin(_root, "a process that starts using the root after the listing")
                else:
                    S.begin_borrow(_store, "a borrower that appears after the listing")
            return why
        S._verify_unit = planted
        try:
            ex = S.cleanup(root, execute=True, repo=T.REPO)
        finally:
            S._verify_unit = real
        refused = {x["path"]: x["reason"] for x in ex["refused"]}
        rel = str(target.relative_to(root))
        want = "ROOT_ACTIVE" if case == "root_becomes_active" else "BASE_STORE_IN_USE"
        after = [d["path"] for d in ex["deleted"]]
        out[case] = target.is_dir() and refused.get(rel) == want and calls.get(str(target)) == 2 and \
            rel not in after and (after == [] if case == "root_becomes_active" else after == ["work/t_x/sbx"])
    return {"ok": all(out.values()), "cases": out}


def t_planted_reading_from_a_file():
    """The test facility of R4: MBS308_TEST_DISK_FREE=file:<path> takes the planted reading from that file at EVERY
    probe, so a test can make the reading fall while a run is under way. Like the plain form it can only LOWER the
    real reading or fail it: a value above the real one leaves the real one; an unparseable or empty file, a missing
    file and an unreadable path are FAILED probes (never "no plant")."""
    S = SCR()
    d = fresh_dir("plantfile")
    f = d / "reading"
    real_statvfs, saved = os.statvfs, os.environ.get(S.PLANT_ENV)

    class Fake:
        f_bavail, f_frsize = 1000, 4096

    out = {}
    try:
        os.statvfs = lambda p: Fake()
        os.environ[S.PLANT_ENV] = "file:" + str(f)
        f.write_text(str(10 ** 15) + "\n")
        out["cannot_raise"] = S.free_bytes(d) == 4096000 and S.check_free([(d, 4096000)], "t")["pass"] is True
        f.write_text("5000\n")
        out["lowers"] = S.free_bytes(d) == 5000
        f.write_text("7")
        out["read_at_every_probe"] = S.free_bytes(d) == 7 and S.check_free([(d, 4096000)], "t")["pass"] is False
        for tag, text in (("garbage", "garbage"), ("empty", ""), ("negative", "-5")):
            f.write_text(text)
            c = S.check_free([(d, 1)], "t")
            out[f"{tag}_is_a_failed_probe"] = S.free_bytes(d) is None and c["pass"] is False and c["planted"] is True
        f.unlink()
        out["missing_file_is_a_failed_probe"] = S.planted_reading() == (True, None) and S.free_bytes(d) is None
        os.environ[S.PLANT_ENV] = "file:" + str(d)                  # a directory: unreadable
        out["unreadable_is_a_failed_probe"] = S.planted_reading() == (True, None) and \
            S.check_free([(d, 1)], "t")["pass"] is False
        os.environ.pop(S.PLANT_ENV)
        out["no_plant"] = S.planted_reading() == (False, None) and S.free_bytes(d) == 4096000
    finally:
        os.statvfs = real_statvfs
        if saved is None:
            os.environ.pop(S.PLANT_ENV, None)
        else:
            os.environ[S.PLANT_ENV] = saved
    return {"ok": all(out.values()), "cases": out}


def _fall_when(proc, plant: Path, started, timeout: int) -> bool:
    """Lower the planted reading (to 1 byte) as soon as `started()` holds, while `proc` runs; True if it fell while
    the process was still running."""
    t0, fell = time.time(), False
    while proc.poll() is None:
        if not fell and started():
            plant.write_text("1\n")
            fell = True
        if time.time() - t0 > timeout:
            proc.kill()
            break
        time.sleep(0.05)
    proc.wait()
    return fell


def t_verifier_phase_gate_reading_falls():
    """R4 (reviewQ6 G-4), the verifier's OWN per-phase gate: the free-space reading FALLS after the start. A dev
    --heavy run of QS-STATIC and QS-LAUNCH in a sparse sandbox, its reading planted through a file that drops to one
    byte once QS-STATIC has begun (its log exists): the start check and the check before QS-STATIC pass and QS-STATIC
    runs and passes; the check before QS-LAUNCH fails, so QS-LAUNCH never runs (no log, no record) and its case FAILS
    CLOSED (`pass` false, DISK_REFUSED, refused before QS-LAUNCH); the report names the refusal."""
    sys.path.insert(0, str(T.NSS / "tests"))
    import test_mbs308_qualify as TQ
    s = TQ.sparse_sandbox("disk_falls")
    work, out = s["tmp"] / "work", s["tmp"] / "dev_heavy.json"
    plant = s["tmp"] / "planted_free"
    plant.write_text(str(1 << 60) + "\n")                           # above any real reading: the real one governs
    with open(s["tmp"] / "verifier.log", "wb") as fh:
        proc = subprocess.Popen([T.PY, "-I", "-S", "-B", str(s["dst"] / "code/mbs308_qualify.py"), "--dev", "--heavy",
                                 "--work", str(work), "--only", "QS-STATIC,QS-LAUNCH", "--out", str(out)],
                                stdout=fh, stderr=subprocess.STDOUT, cwd=str(s["root"]), stdin=subprocess.DEVNULL,
                                env=dict(T.GENV, MBS308_TEST_DISK_FREE="file:" + str(plant)))
        fell = _fall_when(proc, plant, lambda: bool(list(work.glob("mbs308q*/MBS308_QS_STATIC.log"))), 1800)
    try:
        rep = json.loads(out.read_text())
    except (OSError, ValueError):
        return {"ok": False, "fell": fell, "tail": (s["tmp"] / "verifier.log").read_text(errors="replace")[-800:]}
    d, cases = rep.get("disk", {}), rep.get("cases", {})
    checks = [(c.get("phase"), c.get("pass")) for c in d.get("checks", [])]
    launch_ran = bool(list(work.glob("mbs308q*/MBS308_QS_LAUNCH*")))
    ok = fell and proc.returncode == 0 and (d.get("start") or {}).get("pass") is True and \
        checks == [("start", True), ("QS-STATIC", True), ("QS-LAUNCH", False)] and \
        (cases.get("QS-STATIC") or {}).get("pass") is True and (cases["QS-STATIC"].get("n") or 0) > 0 and \
        cases.get("QS-LAUNCH") == {"pass": False, "status": "DISK_REFUSED", "refused_before": "QS-LAUNCH"} and \
        (d.get("refusal") or {}).get("phase") == "QS-LAUNCH" and not launch_ran and rep.get("pass") is False
    shutil.rmtree(s["tmp"], ignore_errors=True)
    return {"ok": ok, "fell_while_running": fell, "checks": checks, "launch_case": cases.get("QS-LAUNCH"),
            "launch_ran": launch_ran}


def t_mutant_runner_reading_falls():
    """R4 (reviewQ6 G-4), the mutant runner's per-phase check: the reading FALLS after the start. The REAL runner
    (--only M11: the unmutated target, then M11), its reading planted through a file that drops to one byte once the
    first phase has begun (its code copy exists): the start check and the first check pass and the unmutated target
    runs, passes and is cleaned; the check before M11 fails: M11 never runs (no mutated code, no result), it is
    listed as not run, the refusal is recorded and the runner FAILS (exit 1)."""
    root = fresh_dir("runner_falls")
    plant = root / "planted_free"
    plant.write_text(str(1 << 60) + "\n")
    out, tm = root / "falls.json", root / "t_mutants"
    env = dict(T.GENV, MBS308_SCRATCH=str(root), MBS308_BASE_STORE=str(T.BASE_STORE),
               MBS308_TEST_DISK_FREE="file:" + str(plant))
    with open(root / "runner.log", "wb") as fh:
        proc = subprocess.Popen([T.PY, "-I", "-S", "-B", str(T.NSS / "tests" / "test_mbs308_mutants.py"), "--only",
                                 "M11", "--out", str(out)], stdout=fh, stderr=subprocess.STDOUT, env=env,
                                stdin=subprocess.DEVNULL)
        fell = _fall_when(proc, plant, lambda: (tm / "UNMUTATED" / "code").is_dir(), 1800)
    try:
        rep = json.loads(out.read_text())
    except (OSError, ValueError):
        return {"ok": False, "fell": fell, "tail": (root / "runner.log").read_text(errors="replace")[-800:]}
    checks = [(c.get("phase"), c.get("pass")) for c in rep.get("disk_checks", [])]
    un = rep.get("unmutated", {})
    ok = fell and proc.returncode == 1 and len(checks) == 3 and [c[1] for c in checks] == [True, True, False] and \
        checks[0][0] == "start" and checks[2][0] == "M11" and rep.get("not_run") == ["M11"] and \
        (rep.get("disk_refusal") or {}).get("phase") == "M11" and rep.get("matrix") == {} and len(un) == 1 and \
        all(v.get("test_passed") is True and not v.get("error") for v in un.values()) and \
        not (tm / "M11").exists() and (tm / "UNMUTATED" / "result.json").is_file() and \
        len(rep.get("cleanups", {})) == 1 and not list(tm.rglob("sbx"))
    return {"ok": ok, "fell_while_running": fell, "checks": checks, "not_run": rep.get("not_run"),
            "exit_code": proc.returncode}


def t_verifier_checks_repository_volume():
    """G-6 (reviewQ6): the verifier's disk check reads BOTH volumes: QUAL_MIN_FREE_BYTES on the --work volume and the
    ratified MIN_FREE_DISK on the REPOSITORY volume. On this host both are one volume, so the readings are planted
    per path (os.statvfs): plenty on --work with the repository one byte short, or the repository unreadable, fails
    the check, and the failing reading is the repository's; plenty on both passes; short on --work fails."""
    sys.path.insert(0, str(T.NSS / "tests"))
    import test_mbs308_qualify as TQ
    Q = TQ.Q
    S = Q.SCR
    work = fresh_dir("repovol")
    repo = str(Q.REPO)
    real_statvfs, saved = os.statvfs, os.environ.pop(S.PLANT_ENV, None)
    need_repo, need_work = S.HOST.MIN_FREE_DISK, S.QUAL_MIN_FREE_BYTES

    def planted(repo_free, work_free):
        class R:
            f_frsize = 1

        def statvfs(p):
            v = repo_free if str(p) == repo else work_free
            if v is None:
                raise OSError("planted statvfs failure")
            r = R()
            r.f_bavail = v
            return r
        os.statvfs = statvfs
        try:
            return Q.disk_check(work, "planted")
        finally:
            os.statvfs = real_statvfs
    try:
        both = planted(need_repo, need_work)
        repo_short = planted(need_repo - 1, 100 * need_work)
        repo_unreadable = planted(None, 100 * need_work)
        work_short = planted(100 * need_repo, need_work - 1)
    finally:
        os.statvfs = real_statvfs
        if saved is not None:
            os.environ[S.PLANT_ENV] = saved

    def bad(c):
        return [r["path"] for r in c["readings"] if not r["ok"]]
    out = {"two_readings_work_then_repository": [r["path"] for r in both["readings"]] == [str(work), repo] and
           [r["need_bytes"] for r in both["readings"]] == [need_work, need_repo],
           "both_at_threshold_pass": both["pass"] is True,
           "repository_one_byte_short_fails": repo_short["pass"] is False and bad(repo_short) == [repo],
           "repository_unreadable_fails": repo_unreadable["pass"] is False and bad(repo_unreadable) == [repo] and
           repo_unreadable["readings"][1]["free_bytes"] is None,
           "work_one_byte_short_fails": work_short["pass"] is False and bad(work_short) == [str(work)],
           "thresholds": need_repo == 2 * GIB and need_work == SCR().QUAL_MIN_FREE_BYTES}
    return {"ok": all(out.values()), "cases": out}


HOST_REPORT_CHILD = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
import mbs308_qualify as Q
D = Q.driver()
H = D.HOST
real_run, real_pid, real_state = H._run, D.STATE.read_pidfile, H.identity_state
out = {}
for name, spec in json.loads(sys.argv[2]).items():
    runs = spec.get("run", {})
    H._run = lambda args, timeout=60, _r=runs: _r[" ".join(args)] if " ".join(args) in _r else real_run(args, timeout)
    if "pidfile" in spec:
        D.STATE.read_pidfile = lambda store, boot_uuid=None, _p=spec["pidfile"]: (_p[0], _p[1])
    if "identity_state" in spec:
        H.identity_state = lambda ident, boot_uuid=None, _s=spec["identity_state"]: _s
    try:
        r = Q.host_report()
    finally:
        H._run, D.STATE.read_pidfile, H.identity_state = real_run, real_pid, real_state
    items = {i["item"]: i for i in r["items"]}
    out[name] = {k: [items[k]["status"], items[k]["reading"]] for k in
                 ("automatic_restart", "host_exclusive", "no_other_campaign_job")}
    out[name]["ready"] = r["ready"]
    out[name]["ready_is_all_ready_or_recorded"] = r["ready"] == all(i["status"] in ("READY", "RECORDED")
                                                                    for i in r["items"])
print(json.dumps(out))
'''
PMSET_G = "/usr/bin/pmset -g"
PMSET_SCHED = "/usr/bin/pmset -g sched"
PS_ALL = "/bin/ps -A -o pid=,ppid=,pcpu=,comm="
PMSET_TEXT = "System-wide power settings:\nCurrently in use:\n sleep                0\n displaysleep         10\n" \
    " disksleep            10\n lowpowermode         0\n"


def t_host_report_unreadable_never_ready():
    """R7 (reviewQ6 F-7): in the READ-ONLY host report an unreadable reading is never RECORDED and READY needs a
    positive reading. The verifier's own host_report() in a sparse sandbox, on planted readings (the host module's
    command reader and the pidfile reader are planted; nothing is written): with `pmset -g`, `pmset -g sched` and
    `ps` read and no pidfile, automatic_restart is RECORDED (also where `pmset -g` lists no autorestart, as on this
    host), host_exclusive and no_other_campaign_job are READY; a failed `pmset -g`, or a failed `pmset -g sched`,
    makes automatic_restart UNKNOWN; a failed `ps`, or one without a process row, makes host_exclusive UNKNOWN (a busy
    process: USER_ACTION); a pidfile whose recorded process is not positively dead (its `ps` fails) or an invalid
    pidfile makes no_other_campaign_job UNKNOWN, a live one NOT_READY, a positively dead one READY. `ready` stays
    "every item READY or RECORDED"."""
    sys.path.insert(0, str(T.NSS / "tests"))
    import test_mbs308_qualify as TQ
    s = TQ.sparse_sandbox("host_report_planted")
    good = {PMSET_G: PMSET_TEXT, PMSET_SCHED: "", PS_ALL: PS_QUIET}
    ident = {"pid": 4242, "start_time": "planted", "boot_uuid": "planted", "command_sha256": "0" * 64}
    absent = [None, "ABSENT"]
    spec = {
        "good": {"run": good, "pidfile": absent},
        "pmset_fails": {"run": dict(good, **{PMSET_G: None}), "pidfile": absent},
        "sched_fails": {"run": dict(good, **{PMSET_SCHED: None}), "pidfile": absent},
        "ps_fails": {"run": dict(good, **{PS_ALL: None}), "pidfile": absent},
        "ps_no_row": {"run": dict(good, **{PS_ALL: "\n"}), "pidfile": absent},
        "ps_busy": {"run": dict(good, **{PS_ALL: PS_QUIET + " 4242     1  90.0 /Applications/Busy.app/Busy\n"}),
                    "pidfile": absent},
        "pidfile_not_positively_dead": {"run": good, "pidfile": [{"identity": ident}, "STALE"],
                                        "identity_state": "UNKNOWN"},
        "pidfile_positively_dead": {"run": good, "pidfile": [{"identity": ident}, "STALE"], "identity_state": "DEAD"},
        "pidfile_live": {"run": good, "pidfile": [{"identity": ident}, "LIVE"]},
        "pidfile_invalid": {"run": good, "pidfile": [None, "INVALID"]},
    }
    p = subprocess.run([T.PY, "-I", "-S", "-B", "-c", HOST_REPORT_CHILD, str(s["dst"] / "code"), json.dumps(spec)],
                       capture_output=True, text=True, env=T.GENV, cwd=str(s["root"]), stdin=subprocess.DEVNULL,
                       timeout=900)
    try:
        r = json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"ok": False, "tail": (p.stdout + p.stderr)[-800:]}
    st = {k: {i: v[i][0] for i in ("automatic_restart", "host_exclusive", "no_other_campaign_job")}
          for k, v in r.items()}
    want = {"good": ("RECORDED", "READY", "READY"), "pmset_fails": ("UNKNOWN", "READY", "READY"),
            "sched_fails": ("UNKNOWN", "READY", "READY"), "ps_fails": ("RECORDED", "UNKNOWN", "READY"),
            "ps_no_row": ("RECORDED", "UNKNOWN", "READY"), "ps_busy": ("RECORDED", "USER_ACTION", "READY"),
            "pidfile_not_positively_dead": ("RECORDED", "READY", "UNKNOWN"),
            "pidfile_positively_dead": ("RECORDED", "READY", "READY"),
            "pidfile_live": ("RECORDED", "READY", "NOT_READY"), "pidfile_invalid": ("RECORDED", "READY", "UNKNOWN")}
    out = {k: tuple(st.get(k, {}).get(i) for i in ("automatic_restart", "host_exclusive", "no_other_campaign_job"))
           == w for k, w in want.items()}
    out["no_reading_is_recorded_as_none"] = r.get("ps_fails", {}).get("host_exclusive", [None, 0])[1] is None and \
        r.get("good", {}).get("host_exclusive", [None, None])[1] == [] and \
        r.get("ps_busy", {}).get("host_exclusive", [None, None])[1] == ["Busy"]
    out["never_ready_with_an_unknown_item"] = all(v.get("ready_is_all_ready_or_recorded") is True for v in r.values()) \
        and all(r[k]["ready"] is False for k in want if "UNKNOWN" in want[k] or "NOT_READY" in want[k]
                or "USER_ACTION" in want[k])
    shutil.rmtree(s["tmp"], ignore_errors=True)
    return {"ok": p.returncode == 0 and all(out.values()), "cases": out, "statuses": st}


def t_repin_platform_failed_reading_refused():
    """G-11 (reviewQ6, YRP1): PLATFORM_PINS are never rewritten from a FAILED reading. On a copy of the code whose
    pinned libpython path does not exist (so its sha256 cannot be read) and whose OS-build pin differs: the dry run
    names the unreadable reading and writes nothing; `--write-platform` is refused PLATFORM_READING_FAILED and the
    driver's bytes are unchanged (the differing, readable pin is not written either)."""
    d = fresh_dir("repin_failed")
    code = d / "code"
    shutil.copytree(T.code_dir(), code, ignore=shutil.ignore_patterns("__pycache__"))
    tool, drv = code / "mbs308_repin.py", code / "mbs308_driver.py"
    rc0, r0 = _run_tool([str(tool), "platform", "--code", str(code)])
    lib = (r0.get("pins") or {}).get("libpython", {}).get("pinned")
    src = drv.read_text()
    planted = src.replace(f'"libpython": "{lib}"', '"libpython": "/nonexistent/mbs308/libpython"', 1) \
        .replace('"os_build": "', '"os_build": "PLANTED', 1) if lib else src
    drv.write_text(planted)
    b0 = drv.read_bytes()
    rc1, r1 = _run_tool([str(tool), "platform", "--code", str(code)])
    rc2, r2 = _run_tool([str(tool), "platform", "--code", str(code), "--write-platform"])
    out = {"clean_copy": rc0 == 0 and r0.get("differs") == [] and r0.get("unreadable") == [] and bool(lib),
           "planted": planted != src,
           "dry_run_names_the_failed_reading": rc1 == 1 and r1.get("unreadable") == ["libpython_sha256"] and
           r1.get("differs") == ["libpython_sha256", "os_build"] and drv.read_bytes() == b0,
           "write_refused_nothing_written": rc2 == 2 and r2.get("refused") == "PLATFORM_READING_FAILED" and
           drv.read_bytes() == b0}
    return {"ok": all(out.values()), "cases": out}


def _carried_listed(md: str) -> list:
    import re
    line = [ln for ln in md.splitlines() if ln.startswith("* The carried (text-identical) functions: ")]
    return re.findall(r"`([^`]+)`", line[0]) if len(line) == 1 else []


def _comment_into(src: str, name: str) -> str:
    """`src` with one comment line planted INSIDE the body of the top-level function `name` (valid Python; the
    function's own source text changes, nothing else)."""
    import ast as _ast
    fn = [n for n in _ast.parse(src).body if isinstance(n, _ast.FunctionDef) and n.name == name]
    if len(fn) != 1:
        return src
    lines = src.splitlines(keepends=True)
    at = fn[0].body[0].lineno - 1
    pad = lines[at][:len(lines[at]) - len(lines[at].lstrip())]
    return "".join(lines[:at] + [pad + "# planted by the test: a change inside the body\n"] + lines[at:])


def t_repin_science_glue_refused():
    """F-4 and G-11 (reviewQ6, YRP3): the generator's SCIENCE-GLUE refusal fires for a change INSIDE a carried
    function's body. In a sandbox whose HEAD holds the driver and its DRIVER_DIFF.md: a comment planted in the body of
    a carried function (one the committed header lists, text-identical to MB r1's) is refused SCIENCE_GLUE_HUNK; it
    stays refused when `--classes` names every hunk LIFECYCLE (it cannot be reclassified), and `--write` writes
    nothing. Control: the same change in a function that is NOT carried (host_preflight) is not science glue: the
    file is reported stale, no science-glue hunk, exit 1."""
    tool = T.code_dir() / "mbs308_repin.py"
    s = sb()
    s.grant_chain()
    ns = s.root / T.NS_REL
    md, drv = ns / "DRIVER_DIFF.md", ns / "code" / "mbs308_driver.py"
    shutil.copy2(T.NSS / "DRIVER_DIFF.md", md)
    s.commit([T.NS_REL + "/DRIVER_DIFF.md"], "sandbox: DRIVER_DIFF.md of the namespace")
    good_md, good_drv = md.read_bytes(), drv.read_text()
    carried = _carried_listed(md.read_text())
    args = [str(tool), "driver-diff", "--ns", str(ns), "--repo", str(s.root)]
    rc0, r0 = _run_tool(args)
    out = {"sandbox_clean": rc0 == 0 and r0.get("stale") is False and r0.get("science_glue_hunks") == [],
           "carried_listed": len(carried) > 30 and "stage1" in carried and "host_preflight" not in carried}
    every = json.dumps({str(i): "LIFECYCLE" for i in range(1, 80)})
    for name in ("stage1", "fs"):
        changed = _comment_into(good_drv, name)
        drv.write_text(changed)
        rc1, r1 = _run_tool(args)
        rc2, r2 = _run_tool(args + ["--classes", every])
        rc3, r3 = _run_tool(args + ["--classes", every, "--write"])
        out[f"body_change_in_{name}_refused"] = changed != good_drv and name in carried and \
            (rc1, r1.get("refused")) == (2, "SCIENCE_GLUE_HUNK") and \
            (rc2, r2.get("refused")) == (2, "SCIENCE_GLUE_HUNK") and \
            (rc3, r3.get("refused")) == (2, "SCIENCE_GLUE_HUNK") and md.read_bytes() == good_md
    drv.write_text(_comment_into(good_drv, "host_preflight"))
    rc4, r4 = _run_tool(args)
    out["control_not_carried_is_not_glue"] = rc4 == 1 and r4.get("stale") is True and \
        r4.get("science_glue_hunks") == [] and md.read_bytes() == good_md
    drv.write_text(good_drv)
    s.grant_chain()                                                # back to the synthetic freeze
    return {"ok": all(out.values()), "cases": out, "carried": len(carried)}


# ====================================================================== brief 56 follow-up (builder7): the science-phase gate
SCIENCE_GATE_RUNS = r'''
os.environ["MBS308_TEST_DISK_FREE"] = "file:" + str(PLANT)
PLANT.write_text(str(1 << 60) + "\n")
run("official_falls", ["QC03", "QC08"], "official", True, {"planted_host_report": "own"})
PLANT.write_text(str(1 << 60) + "\n")
PLANT_SAVED, PLANT = PLANT, None
run("official_control", ["QC03", "QC08"], "official", True, {"planted_host_report": "own"})
PLANT = PLANT_SAVED
d = base / "dev_falls"
d.mkdir(parents=True)
del calls[:]
start = Q.disk_check(d, "verifier start")
PLANT.write_text("1\n")                                   # the reading falls after the verifier's start
r = Q.science_phase(["QC08"], "dev", False, cfg, d, d, d)
out["dev_falls"] = {"start_pass": start["pass"], "calls": list(calls),
                    "cases": {k: {x: v.get(x) for x in ("pass", "status", "refused_before")} for k, v in r["cases"].items()},
                    "checks": [[c["phase"], c["pass"]] for c in r["disk"]["checks"]],
                    "refusal": (r["disk"]["refusal"] or {}).get("phase")}
print(json.dumps(out))
'''


def t_verifier_science_gate_reading_falls():
    """Follow-up item 2 (the gap noted under R4): the verifier's SCIENCE-phase disk gate with a reading that falls
    after the start (the same `file:` facility). In a child process in a sparse sandbox, "this is the qualified
    worktree" is PLANTED and every function that would execute science is a RECORDER (nothing is launched, no decoy
    runs). Official: the reading drops to one byte while the FIRST official decoy "runs": the start check and the
    check before decoy 297 pass, the check before decoy 316 fails, decoy 316 is never launched, and every decoy case
    FAILS CLOSED (DISK_REFUSED, refused before `official decoy 316`). Control: with the reading unchanged both
    decoys are launched and nothing is refused. Dev: the reading drops after the verifier's start check: the check
    before the dev decoy fails, the dev decoy is never run, the case fails closed."""
    sys.path.insert(0, str(T.NSS / "tests"))
    import test_mbs308_cases as TC
    import test_mbs308_qualify as TQ
    s = TQ.sparse_sandbox("science_gate_falls")
    plant = s["tmp"] / "planted_free"
    p = subprocess.run([T.PY, "-I", "-S", "-B", "-c", TC.SCIENCE_PHASE_CHILD + SCIENCE_GATE_RUNS,
                        str(s["dst"] / "code"), str(s["tmp"] / "runs"), str(plant)], capture_output=True, text=True,
                       env=T.GENV, cwd=str(s["root"]), stdin=subprocess.DEVNULL, timeout=600)
    try:
        rep = json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"ok": False, "tail": (p.stdout + p.stderr)[-800:]}
    f, c, d = rep["official_falls"], rep["official_control"], rep["dev_falls"]
    refused = {"pass": False, "status": "DISK_REFUSED", "refused_before": "official decoy 316"}
    out = {"official_start_and_first_check_pass_second_fails": f["start_pass"] is True and f["checks"] ==
           [["start", True], ["official decoy 297", True], ["official decoy 316", False]] and
           f["refusal"] == "official decoy 316",
           "second_decoy_never_launched": f["calls"] == ["official_readings", "official_decoy_gated:297"],
           "decoy_cases_fail_closed": f["cases"] == {"QC03": refused, "QC08": refused},
           "control_both_launched_nothing_refused": c["calls"] ==
           ["official_readings", "official_decoy_gated:297", "official_decoy_gated:316"] and c["refusal"] is None and
           all(x[1] for x in c["checks"]) and len(c["checks"]) == 3 and
           all(v["status"] != "DISK_REFUSED" for v in c["cases"].values()),
           "dev_reading_falls_after_the_start": d["start_pass"] is True and d["checks"] == [["dev decoy", False]] and
           d["refusal"] == "dev decoy" and d["calls"] == [] and
           d["cases"] == {"QC08": {"pass": False, "status": "DISK_REFUSED", "refused_before": "dev decoy"}},
           "no_real_science_path_reached": not any(x.startswith("REAL:") for y in (f, c, d) for x in y["calls"])}
    shutil.rmtree(s["tmp"], ignore_errors=True)
    return {"ok": p.returncode == 0 and all(out.values()), "cases": out,
            "calls": {k: v["calls"] for k, v in rep.items()}}


if __name__ == "__main__":
    T.cli(globals())
