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
    and an sbx clone that borrows from a NON-bare repository."""
    src = tiny_repo(root.parent / (root.name + "_src"))
    store = bare_store(src, root / "work" / "base.git")
    sandbox_clone(store, root / "work" / "t_x" / "sbx")
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
    return {"host": dict(GOOD_HOST, free=free), "su": SU_OFF, "vm_stat": _vm(8 * GIB), "ps": PS_QUIET}


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
        sorted(u["path"] for u in dry["units"] if u["disposable"]) == lay["units"]
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
        if not (isinstance(fn, _ast.FunctionDef) and fn.name in ("host_report", "_clamshell", "_pmset_values")):
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
    queries_only = sorted(c[:2] for c in cmds) == [["/usr/bin/pmset", "-g"], ["/usr/sbin/ioreg", "-r"]]
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


if __name__ == "__main__":
    T.cli(globals())
