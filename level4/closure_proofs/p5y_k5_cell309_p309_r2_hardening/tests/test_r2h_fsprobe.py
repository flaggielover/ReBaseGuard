#!/usr/bin/env python3
"""Focused positive and negative tests of the S1 filesystem pre-launch probe (fs_probe) of the r2 adoption candidate.

  python3 test_r2h_fsprobe.py run --source REPO --commit C --label s1|pre_s1 --work NEW_DIR --out FILE

A fresh scratch replica of commit C with a synthetic, non-target freeze is built (code/r2h_replica.py of the hardening
namespace).  Nothing evaluates a target: every gate, the mirror, Q-HOST's preflight and its monitor are test doubles
(as in tests/r2h_crash_matrix.py); only the runner's own pre-launch code, attempt creation and record writes are real.

F01-F13  unit tests of fs_probe() in temporary directories, with faults injected through a proxy of the runner's `os`
         (no unsupported filesystem is available in this container, so each missing capability is simulated at the
         system-call boundary the probe uses).
F14-F15  SF1-A unit tests: a ledger that cannot be opened for appending (F14), a missing ledger (F15).
M01-M06  integration: the real main() / host_rerun() in the replica, run in a child process:
         M01 supported filesystem: the run proceeds and completes; no probe directory is left.
         M02 hard links unsupported (os.link -> EPERM): refused before Q-HOST, the attempt directory and RUN START;
             qualification/ empty; ledger bytes unchanged.
         M03 directory fsync unsupported (EINVAL on an O_DIRECTORY fd): the same.
         M04 a probe directory left by an interrupted probe: refused, naming it; it is not removed.
         M05 host_rerun with hard links unsupported: refused before HOST RERUN START.
         M06 (SF1-A) a ledger that cannot be appended to (the fault is injected both in the runner's os.open and
             in the ledger writer's Path.open): refused before Q-HOST, the attempt directory and RUN START.
Labels: s1a (the SF1-A runner): every test must pass.  pre_s1a (S1 runner without SF1-A): F01-F13 and M01-M05 pass,
F14, F15 and M06 fail (they discriminate; M06 records the attempt being consumed).  pre_s1 (before S1): see below.
Label s1 (historical, before SF1-A existed): every S1 test must pass.  Label pre_s1 (the candidate before S1): F01-F13 and M02-M05 must fail and M01 must
pass -- the tests discriminate; for M02/M03/M05 the report records what the pre-S1 runner does instead (it writes
the start line and creates the attempt, then fails at its first durable write: the single attempt is consumed).
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
HNS = HERE.parents[1]
sys.path.insert(0, str(HNS / "code"))
import r2h_replica as RP  # noqa: E402

NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
RUNNER_MOD = "p309_" + "qualify"
HOST_MOD = "p309_" + "host"
PROBE_PREFIX = ".p309-fsprobe-"
UNIT = [f"F{i:02d}" for i in range(1, 14)]
INTEG = ["M01", "M02", "M03", "M04", "M05"]
SF1A = ["F14", "F15", "M06"]                                       # the SF1-A cases


def import_runner(replica: Path):
    sys.path.insert(0, str(replica / NS2 / "code"))
    Q = __import__(RUNNER_MOD)
    if Path(Q.__file__).resolve().parent != (replica / NS2 / "code").resolve():
        raise SystemExit("runner not imported from the replica")
    return Q


class Faulty:
    """a proxy of the runner's os module; `faults` maps a capability to an injected behaviour"""

    def __init__(self, real, faults=()):
        self.real, self.faults, self.ops, self.dirfds, self.names = real, set(faults), [], set(), {}

    def __getattr__(self, k):
        return getattr(self.real, k)

    def open(self, path, flags, mode=0o777, **kw):
        if ("ledger_noappend" in self.faults and str(path).endswith(".jsonl") and flags & self.real.O_APPEND
                and flags & (self.real.O_WRONLY | self.real.O_RDWR)):
            raise PermissionError(errno.EACCES, "Permission denied (injected: ledger not appendable)")
        if "no_excl" in self.faults and Path(path).name == "probe.a" and self.real.path.exists(path):
            flags &= ~self.real.O_EXCL
        fd = self.real.open(path, flags, mode, **kw)
        self.names[fd] = Path(path).name
        if flags & self.real.O_DIRECTORY:
            self.dirfds.add(fd)
        return fd

    def close(self, fd):
        self.dirfds.discard(fd)
        return self.real.close(fd)

    def write(self, fd, data):
        if "enospc" in self.faults and self.names.get(fd) == "probe.a":
            raise OSError(errno.ENOSPC, "No space left on device (injected)")
        return self.real.write(fd, data)

    def fsync(self, fd):
        name = self.names.get(fd, "?")
        self.ops.append(("fsync", name))
        if fd in self.dirfds and "no_dir_fsync" in self.faults:
            raise OSError(errno.EINVAL, "Invalid argument (injected: directory fsync unsupported)")
        if name == "probe.a" and "eio_fsync" in self.faults:
            raise OSError(errno.EIO, "Input/output error (injected)")
        if name.endswith(".jsonl") and "ledger_fsync" in self.faults:
            raise OSError(errno.EIO, "Input/output error (injected: ledger fsync)")
        return self.real.fsync(fd)

    def link(self, src, dst, **kw):
        self.ops.append(("link", Path(dst).name))
        if "no_link" in self.faults:
            raise PermissionError(errno.EPERM, "Operation not permitted (injected: hard links unsupported)")
        if "link_replaces" in self.faults and self.real.path.exists(dst):
            self.real.unlink(dst)
        if "link_copies" in self.faults:
            data = Path(src).read_bytes()
            fd = self.real.open(dst, self.real.O_WRONLY | self.real.O_CREAT | self.real.O_EXCL, 0o644)
            self.real.write(fd, data)
            self.real.close(fd)
            return None
        return self.real.link(src, dst, **kw)

    def rmdir(self, path, **kw):
        if "no_rmdir" in self.faults:
            raise OSError(errno.EBUSY, "Device or resource busy (injected)")
        return self.real.rmdir(path, **kw)


# ===================================================================================== unit tests (in-process)
def unit_tests(replica: Path, scratch: Path) -> dict:
    os.environ["P309_SCRATCH_ROOT"] = str(scratch)
    Q = import_runner(replica)
    real = Q.os
    res = {}
    tmp = Path(tempfile.mkdtemp(prefix="fsprobe-unit-", dir=scratch))
    led_dir = tmp / "ledger"
    led_dir.mkdir()
    l1, l2 = led_dir / "ZERO_TARGET_LEDGER.jsonl", led_dir / "EXPOSURE_LEDGER.jsonl"
    l1.write_text("{}\n")
    l2.write_text("{}\n")
    saved = (Q.E.Q.EXEC_LEDGER, Q.E.Q.EXPOSURE_LEDGER)
    Q.E.Q.EXEC_LEDGER, Q.E.Q.EXPOSURE_LEDGER = l1, l2

    def probe(name, faults=()):
        d = tmp / name
        d.mkdir()
        px = Faulty(real, faults)
        Q.os = px
        try:
            out = Q.fs_probe(d)
        finally:
            Q.os = real
        return d, out, px

    def case(cid, fn):
        try:
            fn()
            res[cid] = {"pass": True}
        except Exception as exc:  # noqa: BLE001 - an assertion or a missing function is a FAIL
            res[cid] = {"pass": False, "error": f"{type(exc).__name__}: {exc}"[:400]}

    def left(d):
        return sorted(p.name for p in d.iterdir())

    def f01():
        d, out, _ = probe("f01")
        assert out == [], out
        assert left(d) == [], f"the probe left {left(d)}"

    def f02():
        d, out, px = probe("f02")
        assert out == [], out
        ops = px.ops
        assert ("fsync", "probe.a") in ops, ops
        assert [o for o in ops if o[0] == "link"] == [("link", "probe.b"), ("link", "probe.b")], ops
        names = [n for k, n in ops if k == "fsync"]
        assert "f02" in names and any(n.startswith(PROBE_PREFIX) for n in names), ops
        assert "ZERO_TARGET_LEDGER.jsonl" in names and "EXPOSURE_LEDGER.jsonl" in names and "ledger" in names, ops

    def expect(cid, faults, step, err=None):
        def f():
            d, out, _ = probe(cid.lower(), faults)
            assert out, "an unsupported capability was accepted"
            assert any(step in p for p in out), out
            if err is not None:
                assert any(f"errno {err}" in p for p in out), out
            assert left(d) == [], f"the probe left {left(d)} after a refusal"
        return f

    def f10():
        d, out, _ = probe("f10", {"no_rmdir"})
        assert any("remove the probe directory" in p and "blocks every launch" in p for p in out), out
        lo = [n for n in left(d) if n.startswith(PROBE_PREFIX)]
        assert len(lo) == 1, left(d)
        again = Q.fs_probe(d)
        assert again and all("left by an interrupted filesystem probe" in p and lo[0] in p for p in again), again
        assert (d / lo[0]).exists(), "the leftover was removed by the probe"

    def f11():
        d = tmp / "f11"
        d.mkdir()
        code = ("import os, signal, sys; sys.path.insert(0, %r); Q = __import__(%r); real = Q.os\n"
                "class P:\n"
                "    def __getattr__(self, k): return getattr(real, k)\n"
                "    def link(self, s, t, **kw): os.kill(os.getpid(), signal.SIGKILL)\n"
                "Q.os = P(); Q.fs_probe(__import__('pathlib').Path(%r))\n") % (
            str(replica / NS2 / "code"), RUNNER_MOD, str(d))
        env = {**os.environ, "P309_SCRATCH_ROOT": str(scratch)}
        r = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True, env=env, timeout=120)
        assert r.returncode == -signal.SIGKILL, (r.returncode, r.stderr[-300:])
        lo = [n for n in left(d) if n.startswith(PROBE_PREFIX)]
        assert len(lo) == 1, left(d)
        before = sorted(str(p.relative_to(d)) for p in d.rglob("*"))
        again = Q.fs_probe(d)
        assert again and lo[0] in again[0] and "interrupted filesystem probe" in again[0], again
        assert sorted(str(p.relative_to(d)) for p in d.rglob("*")) == before, "the probe changed the leftover"

    def f12():
        out = Q.fs_probe(tmp / "f12-missing")
        assert out and "does not exist" in out[0], out
        assert not (tmp / "f12-missing").exists()

    case("F01", f01)
    case("F02", f02)
    case("F03", expect("F03", {"no_link"}, "same-directory hard link", errno.EPERM))
    case("F04", expect("F04", {"link_replaces"}, "did not refuse an existing name (a record could be replaced)"))
    case("F05", expect("F05", {"link_copies"}, "not a second name of the same file"))
    case("F06", expect("F06", {"no_excl"}, "O_EXCL did not refuse an existing name"))
    case("F07", expect("F07", {"eio_fsync"}, "file fsync", errno.EIO))
    case("F08", expect("F08", {"no_dir_fsync"}, "directory fsync", errno.EINVAL))
    case("F09", expect("F09", {"ledger_fsync"}, "sync_ledgers", errno.EIO))
    case("F10", f10)
    case("F11", f11)
    case("F12", f12)
    case("F13", expect("F13", {"enospc"}, "write", errno.ENOSPC))
    case("F14", expect("F14", {"ledger_noappend"}, "ledger appendability", errno.EACCES))

    def f15():
        saved15 = Q.E.Q.EXPOSURE_LEDGER
        Q.E.Q.EXPOSURE_LEDGER = led_dir / "MISSING_LEDGER.jsonl"
        try:
            d, out, _ = probe("f15")
        finally:
            Q.E.Q.EXPOSURE_LEDGER = saved15
        assert any("ledger appendability (MISSING_LEDGER.jsonl" in p and f"errno {errno.ENOENT}" in p for p in out), out
        assert left(d) == [], f"the probe left {left(d)}"
        assert not (led_dir / "MISSING_LEDGER.jsonl").exists(), "the probe created a ledger"

    case("F15", f15)
    Q.E.Q.EXEC_LEDGER, Q.E.Q.EXPOSURE_LEDGER = saved
    return res


# ===================================================================================== integration child
def child(replica: Path, case: str) -> int:
    Q = import_runner(replica)
    H = __import__(HOST_MOD)
    real_os, real_sub = Q.os, Q.subprocess
    faults = {"M02": {"no_link"}, "M03": {"no_dir_fsync"}, "M05": {"no_link"},
              "M06": {"ledger_noappend"}}.get(case, set())
    Q.os = Faulty(real_os, faults)
    if case == "M06":                       # the same fault for the ledger writer (pathlib, outside the runner's os)
        import pathlib
        real_path_open = pathlib.Path.open

        def path_open(self, mode="r", *a, **kw):
            if self.name.endswith(".jsonl") and self.parent.name == "ledger" and any(c in mode for c in "aw+"):
                raise PermissionError(errno.EACCES, "Permission denied (injected: ledger not appendable)")
            return real_path_open(self, mode, *a, **kw)
        pathlib.Path.open = path_open

    class DummyMonitor:
        class _In:
            def write(self, _):
                pass

            def close(self):
                pass
        stdin = _In()

        def poll(self):
            return None

        def terminate(self):
            pass

        def wait(self, timeout=None):
            return 0

        def kill(self):
            pass

    class SubProxy:
        def __getattr__(self, k):
            return getattr(real_sub, k)

        def Popen(self, cmd, *a, **kw):  # noqa: N802
            if any(str(c).endswith(HOST_MOD + ".py") for c in cmd):
                return DummyMonitor()
            return real_sub.Popen(cmd, *a, **kw)

    def stub(name):
        def f(*a, **kw):
            Q.E.log(f"synthetic:{name}", f"SYNTHETIC GATE {name} start", klass="SYNTHETIC", notes="fs probe tests")
            return {"pass": True, "synthetic": True, "runs": [{"rc": 0, "stdout_tail": "synthetic"}]}
        return f

    def preflight(modes):
        print("PREFLIGHT_CALLED", flush=True)
        return {"record": "synthetic", "record_bytes": b'{"synthetic": true}\n', "unit": "p309-r2-synthetic",
                "mode": "official", "cfg": {"monitor_gap_tolerance_s": 45.0}, "baseline": {"synthetic": True},
                "continuity_since_launch": {"pass": True}, "unit_properties": {"Restart": "no"},
                "host_config_file_sha256": "0" * 64}

    Q.subprocess = SubProxy()
    research, formal = iter(["QC01", "QC02", "QC03", "QC04"]), iter(["QC11", "QC12", "QC15"])
    Q.qc_research_simple = lambda m, rel, opt=False: stub(next(research))()
    Q.qc_formal = lambda rel, *a, **kw: stub(next(formal))()
    for fn, g in {"qc05": "QC05", "qc06": "QC06", "qc07": "QC07", "qc08": "QC08", "qc09": "QC09", "qc10": "QC10",
                  "qc13": "QC13", "qc16": "QC16", "qc17": "QC17", "qc_u2": "QC_U2", "qc_d5": "QC_D5"}.items():
        setattr(Q, fn, stub(g))
    Q.mirror = lambda freeze: Path("/nonexistent-synthetic-mirror")
    Q.run = lambda cmd, cwd, timeout=0: {"rc": 0, "cmd": ["synthetic"]}
    Q.qhost_preflight = preflight
    Q.stop_qhost_monitor = lambda: {"pass": True, "samples": 1, "synthetic": True}
    Q.decoy_stage1a = lambda label, workers: {"run": {"rc": 0}, "out": Path("/nonexistent-synthetic-decoy")}
    sys.argv = ["runner", "--workers", "1"] + (["--host-rerun"] if case == "M05" else [])
    return Q.main()


def sha_tree(*paths: Path) -> str:
    h = hashlib.sha256()
    for root in paths:
        if root.is_file():
            h.update(root.name.encode() + b"\0" + root.read_bytes())
        elif root.exists():
            for p in sorted(root.rglob("*")):
                h.update(str(p.relative_to(root)).encode() + b"\0" + (p.read_bytes() if p.is_file() else b"<dir>"))
        else:
            h.update(b"<absent>")
    return h.hexdigest()


def integration(replica: Path, topo: dict, env: dict, label: str) -> dict:
    fns = replica / NS2
    qdir, ledger = fns / "qualification", fns / "ledger" / "ZERO_TARGET_LEDGER.jsonl"

    def reset():
        if qdir.exists():
            shutil.rmtree(qdir)
        RP.git(replica, "checkout", "-q", "--", f"{NS2}/ledger")
        if RP.git(replica, "status", "--porcelain", "--untracked-files=all"):
            raise SystemExit("replica not clean after reset")

    def starts(prefix="QUALIFICATION RUN START"):
        return sum(f'"purpose": "{prefix}' in l for l in ledger.read_text().splitlines())

    def run(case):
        return subprocess.run([sys.executable, "-B", str(HERE), "child", "--replica", str(replica), "--case", case],
                              capture_output=True, text=True, timeout=900, env=env)

    def probe_left():
        return sorted(str(p.relative_to(fns)) for p in fns.rglob(PROBE_PREFIX + "*"))

    res = {}
    # M01: supported -> the run proceeds and completes, no probe leftover
    reset()
    r = run("M01")
    summ = qdir / "P309_QUALIFICATION.json"
    s = json.loads(summ.read_text()) if summ.exists() else {}
    res["M01"] = {"rc": r.returncode, "preflight_called": "PREFLIGHT_CALLED" in r.stdout, "run_start_lines": starts(),
                  "summary_pass": s.get("pass"), "attempt_start": (qdir / "attempt_1" / "ATTEMPT_START.json").exists(),
                  "probe_left": probe_left(), "stdout_tail": r.stdout[-300:], "stderr_tail": r.stderr[-300:]}
    res["M01"]["pass"] = (r.returncode == 0 and res["M01"]["preflight_called"] and starts() == 1 and s.get("pass")
                          is True and res["M01"]["attempt_start"] and not res["M01"]["probe_left"])
    # M02 / M03: an unsupported capability -> refused before Q-HOST, the attempt and RUN START
    for cid, step in (("M02", "same-directory hard link"), ("M03", "directory fsync")):
        reset()
        before = ledger.read_bytes()
        r = run(cid)
        refusal = [l for l in r.stdout.splitlines() if "REFUSED" in l]
        res[cid] = {"rc": r.returncode, "refusal": refusal[:1], "preflight_called": "PREFLIGHT_CALLED" in r.stdout,
                    "attempt_dir": (qdir / "attempt_1").exists(), "run_start_lines": starts(),
                    "qualification_entries": sorted(p.name for p in qdir.iterdir()) if qdir.exists() else None,
                    "ledger_unchanged": ledger.read_bytes() == before, "probe_left": probe_left(),
                    "stderr_tail": r.stderr[-400:]}
        res[cid]["pass"] = (r.returncode == 2 and bool(refusal) and "filesystem probe (S1)" in refusal[0]
                            and step in refusal[0] and not res[cid]["preflight_called"]
                            and not res[cid]["attempt_dir"] and starts() == 0 and res[cid]["ledger_unchanged"]
                            and res[cid]["qualification_entries"] == [] and not res[cid]["probe_left"])
    # M04: a probe directory left by an interrupted probe -> refused by name, never removed
    reset()
    qdir.mkdir()
    lo = qdir / (PROBE_PREFIX + "4242")
    lo.mkdir()
    (lo / "probe.a").write_text("P309 filesystem probe\n")
    before = sha_tree(qdir, ledger)
    r = run("M04")
    refusal = [l for l in r.stdout.splitlines() if "REFUSED" in l]
    res["M04"] = {"rc": r.returncode, "refusal": refusal[:1], "preflight_called": "PREFLIGHT_CALLED" in r.stdout,
                  "unchanged": sha_tree(qdir, ledger) == before, "run_start_lines": starts()}
    res["M04"]["pass"] = (r.returncode == 2 and bool(refusal) and "interrupted filesystem probe" in refusal[0]
                          and lo.name in refusal[0] and res["M04"]["unchanged"] and starts() == 0
                          and not res["M04"]["preflight_called"])
    # M05: host re-run with hard links unsupported -> refused before HOST RERUN START (qualification/ must exist)
    reset()
    qdir.mkdir()
    before = ledger.read_bytes()
    r = run("M05")
    refusal = [l for l in r.stdout.splitlines() if "REFUSED" in l]
    res["M05"] = {"rc": r.returncode, "refusal": refusal[:1], "preflight_called": "PREFLIGHT_CALLED" in r.stdout,
                  "host_start_lines": starts("HOST RERUN START"), "ledger_unchanged": ledger.read_bytes() == before,
                  "host_rerun_dir": (qdir / "host_rerun").exists(), "probe_left": probe_left(),
                  "stderr_tail": r.stderr[-400:]}
    res["M05"]["pass"] = (r.returncode == 2 and bool(refusal) and refusal[0].startswith("HOST RERUN REFUSED: filesystem "
                          "probe (S1)") and not res["M05"]["preflight_called"] and starts("HOST RERUN START") == 0
                          and res["M05"]["ledger_unchanged"] and not res["M05"]["host_rerun_dir"]
                          and not res["M05"]["probe_left"])
    # M06 (SF1-A): a ledger that cannot be appended to -> refused before Q-HOST, the attempt directory and RUN START
    reset()
    before = ledger.read_bytes()
    r = run("M06")
    refusal = [l for l in r.stdout.splitlines() if "REFUSED" in l]
    res["M06"] = {"rc": r.returncode, "refusal": refusal[:1], "preflight_called": "PREFLIGHT_CALLED" in r.stdout,
                  "attempt_dir": (qdir / "attempt_1").exists(), "run_start_lines": starts(),
                  "qualification_entries": sorted(p.name for p in qdir.iterdir()) if qdir.exists() else None,
                  "ledger_unchanged": ledger.read_bytes() == before, "probe_left": probe_left(),
                  "stderr_tail": r.stderr[-400:]}
    res["M06"]["pass"] = (r.returncode == 2 and bool(refusal) and "filesystem probe (S1)" in refusal[0]
                          and "ledger appendability" in refusal[0] and not res["M06"]["preflight_called"]
                          and not res["M06"]["attempt_dir"] and starts() == 0 and res["M06"]["ledger_unchanged"]
                          and res["M06"]["qualification_entries"] == [] and not res["M06"]["probe_left"])
    reset()
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="mode", required=True)
    r = sp.add_parser("run")
    for k in ("--source", "--commit", "--label", "--work", "--out"):
        r.add_argument(k, required=True)
    c = sp.add_parser("child")
    c.add_argument("--replica", required=True)
    c.add_argument("--case", required=True)
    a = ap.parse_args()
    if a.mode == "child":
        return child(Path(a.replica), a.case)
    work = Path(a.work)
    work.mkdir()
    scratch = work / "p309_scratch"
    scratch.mkdir()
    replica = work / "replica"
    info = RP.build(a.source, a.commit, replica)
    topo = RP.synthetic_freeze(replica, scratch)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "P309_"))}
    env.update(P309_SCRATCH_ROOT=str(scratch), P309_EVIDENCE_DIR=str(work / "evidence"), TMPDIR=str(work))
    os.environ.update(P309_EVIDENCE_DIR=str(work / "evidence"), TMPDIR=str(work))
    units = unit_tests(replica, scratch)
    integ = integration(replica, topo, env, a.label)
    results = {**units, **integ}
    s1_ids = UNIT + INTEG
    if a.label == "s1a":
        ok = all(v["pass"] for v in results.values())
        expectation = "every test passes (S1 and SF1-A)"
    elif a.label == "pre_s1a":
        ok = all(results[k]["pass"] for k in s1_ids) and all(not results[k]["pass"] for k in SF1A)
        expectation = ("the S1 tests pass and the SF1-A tests fail on the runner without SF1-A: the SF1-A tests "
                       "discriminate")
    elif a.label == "s1":
        ok = all(results[k]["pass"] for k in s1_ids)
        expectation = "every S1 test passes"
    else:
        ok = (all(not units[k]["pass"] for k in UNIT) and integ["M01"]["pass"]
              and all(not integ[k]["pass"] for k in ("M02", "M03", "M04", "M05")))
        expectation = ("the S1 tests fail on the pre-S1 runner (fs_probe absent; unsupported filesystems not refused "
                       "before the start line) while the supported-filesystem run passes: the tests discriminate")
    out = {"schema": "P309_R2H_FSPROBE_TESTS/1", "label": a.label, "commit": info["commit"], "tree": info["tree"],
           "runner_sha256": hashlib.sha256((replica / NS2 / "code" / (RUNNER_MOD + ".py")).read_bytes()).hexdigest(),
           "tool_sha256": hashlib.sha256(HERE.read_bytes()).hexdigest(), "expectation": expectation,
           "meets_expectation": ok, "results": results,
           "statement": "synthetic gates and Q-HOST doubles; faults injected at the os boundary; nothing evaluated; "
                        "NEW TARGET EVALUATIONS = 0"}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    for k, v in results.items():
        print(f"[{'PASS' if v['pass'] else 'FAIL'}] {k} {v.get('error', '') or v.get('refusal', '')}")
    print(f"{a.label}: meets expectation ({expectation}): {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
