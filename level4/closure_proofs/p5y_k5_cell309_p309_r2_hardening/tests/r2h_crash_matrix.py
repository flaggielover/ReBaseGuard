#!/usr/bin/env python3
"""Crash-injection failure matrix for the r2 qualification runner (synthetic gates only; scratch replicas only).

  python3 r2h_crash_matrix.py run --source REPO --commit C --label baseline|hardened --work NEW_DIR --out FILE

The REAL runner (code/p309_qualify.py main) of the package at commit C runs in a fresh scratch replica that carries a
synthetic, non-target freeze (code/r2h_replica.py).  Test doubles replace only:
  * every gate function (each logs a SYNTHETIC start line, does no work, reads no input);
  * Q-HOST's preflight (no systemd unit exists here) -- returns a synthetic launch context, or raises HostError for
    the host-identity case;
  * the Q-HOST monitor process (a dummy object) and the monitor verdict (pass).
The freeze-manifest check runs for real (the synthetic freeze was made on this host).  SIGKILL is injected at every
protocol point; os.fsync / os.link calls are logged.  Every outcome is judged by the independent validator
(code/r2h_validator.py) and by byte hashes before and after each restart request -- never by an exit status alone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
sys.path.insert(0, str(NS / "code"))
import r2h_replica as RP  # noqa: E402

VALIDATOR = NS / "code" / "r2h_validator.py"
NS2 = RP.NS2
SCRATCH_ROOT = Path("/tmp/claude-0")
GATES = ["QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08", "QC09", "QC10", "QC11", "QC12", "QC13",
         "QC14", "QC15", "QC16", "QC17", "QC_U2", "QC_D5"]


def kill_self() -> None:
    os.kill(os.getpid(), signal.SIGKILL)


# ===================================================================================== child: the real runner
def child(replica: Path, crash: str) -> int:
    fns = replica / NS2
    sys.path.insert(0, str(fns / "code"))
    import p309_qualify as Q  # noqa: E402
    import p309_host as H  # noqa: E402
    if Path(Q.__file__).resolve().parent != (fns / "code").resolve() or SCRATCH_ROOT not in Path(Q.__file__).parents:
        raise SystemExit("child: runner not imported from the scratch replica")
    point, _, gate = crash.partition(":")
    flog = os.environ.get("R2H_FSYNC_LOG")
    real_os, real_sub, real_log, real_xwrite = Q.os, Q.subprocess, Q.E.log, Q.xwrite

    def note(kind, name):
        if flog:
            with open(flog, "a") as fh:
                fh.write(json.dumps({"op": kind, "name": name}) + "\n")

    def target(name: str) -> bool:
        if point in ("partial_summary", "empty_summary"):
            return name == "P309_QUALIFICATION.json" or name.startswith(".P309_QUALIFICATION.json.tmp")
        return name == f"{gate}.json" or name.startswith(f".{gate}.json.tmp")

    class OsProxy:
        names: dict = {}

        def __getattr__(self, k):
            return getattr(real_os, k)

        def open(self, path, flags, mode=0o777, **kw):
            fd = real_os.open(path, flags, mode, **kw)
            self.names[fd] = Path(path).name
            return fd

        def write(self, fd, data):
            if target(self.names.get(fd, "")) and point in ("empty_record", "partial_record", "partial_summary",
                                                             "empty_summary"):
                if point.startswith("partial"):
                    real_os.write(fd, bytes(data)[: len(data) // 2])
                kill_self()
            return real_os.write(fd, data)

        def fsync(self, fd):
            note("fsync", self.names.get(fd, f"fd{fd}"))
            return real_os.fsync(fd)

        def link(self, src, dst, **kw):
            note("link", Path(dst).name)
            if point == "before_link" and target(Path(dst).name):
                kill_self()
            real_os.link(src, dst, **kw)
            if point == "after_link" and target(Path(dst).name):
                kill_self()

        def mkdir(self, path, *a, **kw):
            if Path(path).name == "attempt_1":
                if point == "before_attempt_dir":
                    kill_self()
                if point == "race":
                    time.sleep(1.5)
            return real_os.mkdir(path, *a, **kw)

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

        def Popen(self, cmd, *a, **kw):  # noqa: N802 - the Q-HOST monitor is a dummy here
            if any(str(c).endswith("p309_host.py") for c in cmd):
                return DummyMonitor()
            return real_sub.Popen(cmd, *a, **kw)

    def log(script, purpose, **kw):
        if point == "before_run_start" and str(purpose).startswith(Q.RUN_START):
            kill_self()
        return real_log(script, purpose, **kw)

    def xwrite(path, text):
        if point == "before_summary" and Path(path).name == "P309_QUALIFICATION.json":
            kill_self()
        if point == "abort_crash" and Path(path).name == "P309_QUALIFICATION.json":
            kill_self()
        real_xwrite(path, text)
        if point == "after_record" and Path(path).name == f"{gate}.json":
            kill_self()

    def stub(name):
        def f(*a, **kw):
            log(f"synthetic:{name}", f"SYNTHETIC GATE {name} start", klass="SYNTHETIC", notes="crash matrix")
            if point == "during_gate" and name == gate:
                kill_self()
            if point in ("abort_signal", "abort_crash") and name == gate:
                os.kill(os.getpid(), signal.SIGTERM)       # the monitor's signal: the runner's real abort path
                time.sleep(5)
            return {"pass": True, "synthetic": True, "runs": [{"rc": 0, "stdout_tail": "synthetic"}]}
        return f

    def preflight(modes):
        if point == "host_differs":
            raise H.HostError("the host changed since the launch: {'same_boot': False} (test double)")
        return {"record": "synthetic", "record_bytes": b'{"synthetic": true}\n', "unit": "p309-r2-qualify-synthetic",
                "mode": "official", "cfg": {"monitor_gap_tolerance_s": 45.0}, "baseline": {"synthetic": True},
                "continuity_since_launch": {"pass": True}, "unit_properties": {"Restart": "no"},
                "host_config_file_sha256": "0" * 64}

    Q.os, Q.subprocess, Q.E.log, Q.xwrite = OsProxy(), SubProxy(), log, xwrite
    research, formal = iter(["QC01", "QC02", "QC03", "QC04"]), iter(["QC11", "QC12", "QC15"])
    Q.qc_research_simple = lambda m, rel, opt=False: stub(next(research))()
    Q.qc_formal = lambda rel, *a, **kw: stub(next(formal))()
    for fn, g in {"qc05": "QC05", "qc06": "QC06", "qc07": "QC07", "qc08": "QC08", "qc09": "QC09", "qc10": "QC10",
                  "qc13": "QC13", "qc16": "QC16", "qc17": "QC17", "qc_u2": "QC_U2", "qc_d5": "QC_D5"}.items():
        setattr(Q, fn, stub(g))
    Q.mirror = lambda freeze: Path("/nonexistent-synthetic-mirror")
    q14 = stub("QC14")
    Q.run = lambda cmd, cwd, timeout=0: (q14(), {"rc": 0, "cmd": ["synthetic"]})[1]
    Q.qhost_preflight = preflight
    Q.stop_qhost_monitor = lambda: {"pass": True, "samples": 1, "synthetic": True}
    sys.argv = ["p309_qualify.py", "--workers", "1"]
    return Q.main()


# ===================================================================================== parent
def sha_tree(*paths: Path) -> str:
    h = hashlib.sha256()
    for root in paths:
        if root.is_file():
            h.update(root.name.encode() + b"\0" + root.read_bytes())
        elif root.exists():
            for p in sorted(root.rglob("*")):
                if p.is_file():
                    h.update(str(p.relative_to(root)).encode() + b"\0" + p.read_bytes())
        else:
            h.update(b"<absent>" + str(root).encode())
    return h.hexdigest()


class Matrix:
    def __init__(self, replica: Path, work: Path, topo: dict, env: dict):
        self.r, self.work, self.topo, self.env, self.cases = replica, work, topo, env, []
        self.fns = replica / NS2
        self.qdir, self.ledger = self.fns / "qualification", self.fns / "ledger" / "ZERO_TARGET_LEDGER.jsonl"

    def reset(self) -> None:
        if self.qdir.exists():
            shutil.rmtree(self.qdir)
        RP.git(self.r, "checkout", "-q", "--", f"{NS2}/ledger")
        if RP.git(self.r, "rev-parse", "HEAD") != self.topo["tip"]:
            RP.git(self.r, "reset", "-q", "--hard", self.topo["tip"])
        st = RP.git(self.r, "status", "--porcelain", "--untracked-files=all")
        if st:
            raise SystemExit(f"replica not clean after reset: {st[:300]}")

    def run(self, crash="none", fsync_log=None) -> subprocess.CompletedProcess:
        env = dict(self.env)
        if fsync_log:
            env["R2H_FSYNC_LOG"] = str(fsync_log)
        return subprocess.run([sys.executable, str(HERE), "child", "--replica", str(self.r), "--crash", crash],
                              capture_output=True, text=True, timeout=600, env=env)

    def status(self) -> dict:
        p = subprocess.run([sys.executable, str(VALIDATOR), "status", str(self.qdir), str(self.ledger), "--record-utc",
                            self.topo["record_utc"], "--freeze", self.topo["F"]], capture_output=True, text=True)
        try:
            return json.loads(p.stdout)
        except ValueError:
            return {"classification": "VALIDATOR_ERROR", "reasons": [p.stdout[-300:], p.stderr[-300:]]}

    def starts(self) -> int:
        return sum('"purpose": "QUALIFICATION RUN START' in l for l in self.ledger.read_text().splitlines())

    def restart_probe(self) -> dict:
        """one restart request, then two concurrent ones: each must be refused and change nothing"""
        before = sha_tree(self.qdir, self.ledger)
        r = self.run()
        mid = sha_tree(self.qdir, self.ledger)
        ps = [subprocess.Popen([sys.executable, str(HERE), "child", "--replica", str(self.r), "--crash", "none"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.env)
              for _ in range(2)]
        outs = [p.communicate(timeout=600) for p in ps]
        after = sha_tree(self.qdir, self.ledger)
        refused = ["QUALIFICATION REFUSED" in r.stdout] + ["QUALIFICATION REFUSED" in o[0] for o in outs]
        return {"refused": refused, "unchanged": before == mid == after,
                "ok": all(refused) and before == mid == after,
                "refusal_texts": sorted({l for o in [r.stdout] + [x[0] for x in outs] for l in o.splitlines()
                                         if "REFUSED" in l})[:3]}

    def add(self, cid, risk, desc, **detail) -> None:
        self.cases.append({"id": cid, "risk": risk, "desc": desc, **detail})

    def crash_cases(self) -> None:
        pts = [
            ("C01", "interruption before first write", "before_attempt_dir"),
            ("C02", "attempt directory without RUN START (stale lock)", "before_run_start"),
            ("C03", "interruption during a gate", "during_gate:QC01"),
            ("C04", "interruption after open, before write (record)", "empty_record:QC05"),
            ("C05", "interruption during the record write", "partial_record:QC05"),
            ("C06", "interruption before the record is linked", "before_link:QC05"),
            ("C07", "interruption after the record is linked", "after_link:QC05"),
            ("C08", "crash between artifact write and ledger update", "after_record:QC05"),
            ("C09", "crash between ledger update and the record", "during_gate:QC06"),
            ("C10", "host restart during QC-D5 (r1's case)", "during_gate:QC_D5"),
            ("C11", "crash between the last ledger update and the completion marker", "before_summary"),
            ("C12", "interruption during the completion marker write", "partial_summary"),
            ("C13", "Q-HOST abort during a gate (real abort path)", "abort_signal:QC07"),
            ("C14", "interruption inside the Q-HOST abort, before its summary", "abort_crash:QC07"),
            ("C15", "control: an uninterrupted synthetic run", "none"),
        ]
        for cid, desc, crash in pts:
            self.reset()
            flog = self.work / f"{cid}.fsync.jsonl"
            r = self.run(crash, flog)
            st = self.status()
            ops = [json.loads(l) for l in flog.read_text().splitlines()] if flog.exists() else []
            probe = self.restart_probe()
            if crash == "before_attempt_dir":
                no_trace = not (self.qdir / "attempt_1").exists() and self.starts() == 0
                self.add(cid, "interruption before first write", desc, crash=crash, rc=r.returncode,
                         status_after_crash=st["classification"], no_trace=no_trace,
                         fresh_start_allowed_after=not probe["refused"][0], restart=probe)
                continue
            self.add(cid, desc, desc, crash=crash, rc=r.returncode, classification=st["classification"],
                     reasons=st["reasons"][:4], restart=probe, run_start_lines=self.starts(),
                     fsync_ops=sum(o["op"] == "fsync" for o in ops), link_ops=sum(o["op"] == "link" for o in ops),
                     fsynced=sorted({o["name"] for o in ops if o["op"] == "fsync"})[:12])

    def state_cases(self) -> None:
        def pre(cid, desc, setup):
            self.reset()
            setup()
            before = sha_tree(self.qdir, self.ledger)
            r = self.run()
            st = self.status()
            refused = "QUALIFICATION REFUSED" in r.stdout
            self.add(cid, desc, desc, runner_refused=refused, unchanged=sha_tree(self.qdir, self.ledger) == before,
                     refusal=[l for l in r.stdout.splitlines() if "REFUSED" in l][:1], classification_after=
                     st["classification"], run_start_lines=self.starts(), stdout_tail=r.stdout[-200:])

        pre("S01", "stale lock: an empty attempt directory", lambda: (self.qdir / "attempt_1").mkdir(parents=True))
        pre("S02", "partial artifact: a torn record in a prior attempt",
            lambda: ((self.qdir / "attempt_1").mkdir(parents=True),
                     (self.qdir / "attempt_1" / "QC01.json").write_text('{"pass": tr')))
        pre("S03", "stray completion marker without an attempt",
            lambda: (self.qdir.mkdir(), (self.qdir / "P309_QUALIFICATION.json").write_text("{}")))
        pre("S04", "leftover temporary file in the qualification directory",
            lambda: (self.qdir.mkdir(), (self.qdir / ".P309_QUALIFICATION.json.tmp-1").write_text('{"pa')))
        pre("S05", "torn ledger tail before launch (truncated checkpoint)",
            lambda: open(self.ledger, "a").write('{"utc": "2026-'))
        pre("S06", "orphan RUN START: a prior run's start line but no attempt directory",
            lambda: open(self.ledger, "a").write(json.dumps({
                "utc": "2099-01-01T00:00:00Z", "script": "code/p309_qualify.py", "class": "GOVERNANCE",
                "purpose": "QUALIFICATION RUN START attempt_1 (prior run, attempt lost)", "drifts": [],
                "cells_touched": [], "new_target_evaluations": 0, "target_equivalent_proxies": 0,
                "target_informed_optimisation": 0, "notes": "fixture"}) + "\n"))
        self.reset()
        before = sha_tree(self.qdir, self.ledger)
        r = self.run("host_differs")
        self.add("S07", "host identity differs at launch", "Q-HOST preflight raises HostError (host changed)",
                 runner_refused="QUALIFICATION REFUSED: Q-HOST" in r.stdout,
                 unchanged=not (self.qdir / "attempt_1").exists() and self.starts() == 0,
                 refusal=[l for l in r.stdout.splitlines() if "REFUSED" in l][:1])
        self.reset()
        (self.fns / "code" / "zz_mismatch.py").write_text("# changed after the freeze\n")
        RP.git(self.r, "add", "-A")
        RP.git(self.r, "commit", "-qm", "mismatch")
        r = self.run()
        self.add("S08", "resume / start from a mismatched commit", "a frozen directory changed after the freeze",
                 runner_refused="QUALIFICATION REFUSED" in r.stdout, unchanged=not self.qdir.exists() or
                 not (self.qdir / "attempt_1").exists(), refusal=[l for l in r.stdout.splitlines() if "REFUSED" in l][:1])
        self.reset()
        ps = [subprocess.Popen([sys.executable, str(HERE), "child", "--replica", str(self.r), "--crash", "race"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.env) for _ in range(2)]
        outs = [p.communicate(timeout=600) for p in ps]
        st = self.status()
        self.add("S09", "double launch (two runners race)", "both pass the existence check, then mkdir decides",
                 rcs=sorted(p.returncode for p in ps), run_start_lines=self.starts(), classification=st["classification"],
                 loser=[o[1].strip().splitlines()[-1][-160:] for o in outs if o[1].strip()][:1])
        self.reset()


def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="mode", required=True)
    c = sp.add_parser("child")
    c.add_argument("--replica", required=True)
    c.add_argument("--crash", default="none")
    r = sp.add_parser("run")
    r.add_argument("--source", required=True)
    r.add_argument("--commit", required=True)
    r.add_argument("--label", required=True)
    r.add_argument("--work", required=True)
    r.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.mode == "child":
        return child(Path(a.replica).resolve(), a.crash)
    work = Path(a.work).resolve()
    if SCRATCH_ROOT not in work.parents:
        raise SystemExit("the work directory must lie under the scratchpad root")
    work.mkdir(parents=True)
    scratch = work / "p309_scratch"
    scratch.mkdir()
    t0 = time.time()
    built = RP.build(a.source, a.commit, work / "replica")
    topo = RP.synthetic_freeze(work / "replica", scratch)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "P309_"))}
    env["P309_SCRATCH_ROOT"] = str(scratch)
    M = Matrix(work / "replica", work, topo, env)
    M.crash_cases()
    M.state_cases()
    res = {"schema": "P309_R2H_CRASH_MATRIX/1", "label": a.label, "package_commit": a.commit, "replica": built,
           "topology": {k: v for k, v in topo.items() if k != "generators"}, "cases": M.cases,
           "wall_s": round(time.time() - t0, 1), "python": sys.version.split()[0],
           "runner_sha256": hashlib.sha256((work / "replica" / NS2 / "code" / "p309_qualify.py").read_bytes()).hexdigest(),
           "tool_sha256": hashlib.sha256(HERE.read_bytes()).hexdigest(),
           "validator_sha256": hashlib.sha256(VALIDATOR.read_bytes()).hexdigest(),
           "statement": "synthetic gates only; nothing evaluated; NEW TARGET EVALUATIONS = 0"}
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    for c in M.cases:
        print(c["id"], c["desc"][:60], "|", {k: c.get(k) for k in ("classification", "status_after_crash",
                                                                     "runner_refused", "fsync_ops", "run_start_lines")
                                              if k in c}, "| restart ok" if c.get("restart", {}).get("ok") else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
