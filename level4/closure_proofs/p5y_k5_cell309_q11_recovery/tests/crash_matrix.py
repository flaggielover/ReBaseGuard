#!/usr/bin/env python3
"""Crash-injection matrix for the qualification write / restart / resume protocol (synthetic gates only).

  python3 crash_matrix.py --replica SCRATCH_REPLICA --work NEW_SCRATCH_DIR --out RESULTS.json

Two protocols are exercised, each with SIGKILL injected at every protocol point:
  r1  the REAL frozen runner (code/p309_qualify.py main) in a scratch replica of r1 at the launch commit, with EVERY
      gate replaced by a synthetic stub (no gate does any work; nothing reads any input).  One precondition is
      replaced by a test double: the freeze-manifest check, which binds the freeze host's machine identity and
      therefore refuses on any other host (shown separately by case R-HOST, unstubbed).
  new the rehearsal protocol of code/p309_rehearsal.py (atomic record, then ledger row), through its own
      record_start / record_gate / record_summary functions.
Every outcome is judged by the independent validator (code/attempt_validator.py) and by byte hashes of the attempt
and the ledger before and after each restart / resume request -- never by an exit status alone.
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
VALIDATOR = NS / "code" / "attempt_validator.py"
REHEARSAL = NS / "code" / "p309_rehearsal.py"
NS_R1 = "level4/closure_proofs/p5y_k5_cell309_p309_r1"
LAUNCH = "c950054ae0aa8f9e5d7171b520af3f601238a017"
SCRATCH_ROOT = Path("/tmp/claude-0")
GATES = ["QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08", "QC09", "QC10", "QC11", "QC12", "QC13",
         "QC14", "QC15", "QC16", "QC17", "QC_U2", "QC_D5"]
STUBBED = ("qc_research_simple", "qc05", "qc06", "qc07", "qc08", "qc09", "qc10", "qc_formal", "qc13", "qc16",
           "qc17", "qc_u2", "qc_d5", "mirror", "run")


def kill_self() -> None:
    os.kill(os.getpid(), signal.SIGKILL)


# ================================================================================ child: the real r1 runner
def child_r1(replica: Path, crash: str) -> int:
    fns = replica / NS_R1
    sys.path.insert(0, str(fns / "code"))
    import p309_qualify as Q  # noqa: E402
    if Path(Q.__file__).resolve().parent != (fns / "code").resolve() or SCRATCH_ROOT not in Path(Q.__file__).parents:
        raise SystemExit("child: runner not imported from the scratch replica")
    point, _, gate = crash.partition(":")
    real_os, real_sub, real_log, real_xwrite = Q.os, Q.subprocess, Q.E.log, Q.xwrite

    class OsProxy:
        fd_names: dict = {}

        def __getattr__(self, k):
            return getattr(real_os, k)

        def open(self, path, flags, mode=0o777, **kw):
            fd = real_os.open(path, flags, mode, **kw)
            self.fd_names[fd] = Path(path).name
            return fd

        def write(self, fd, data):
            name = self.fd_names.get(fd, "")
            target = "P309_QUALIFICATION.json" if point == "partial_summary" else f"{gate}.json"
            if name == target and point in ("empty_record", "partial_record", "partial_summary"):
                if point != "empty_record":
                    real_os.write(fd, data[: len(data) // 2])
                kill_self()
            return real_os.write(fd, data)

        def mkdir(self, path, *a, **kw):
            if Path(path).name == "attempt_1":
                if point == "before_attempt_dir":
                    kill_self()
                if point == "race":
                    time.sleep(1.5)                      # both racers pass the existence check first
            return real_os.mkdir(path, *a, **kw)

    class SubProxy:
        def __getattr__(self, k):
            return getattr(real_sub, k)

        def run(self, cmd, *a, **kw):
            if any(str(c).endswith("make_freeze_manifest.py") for c in cmd) and "--check" in cmd:
                return real_sub.CompletedProcess(cmd, 0, "MANIFEST IDENTICAL (test double: host binding)\n", "")
            return real_sub.run(cmd, *a, **kw)

    def log(script, purpose, **kw):
        if point == "before_run_start" and str(purpose).startswith(Q.RUN_START):
            kill_self()
        return real_log(script, purpose, **kw)

    def xwrite(path, text):
        real_xwrite(path, text)
        if point == "after_record" and Path(path).name == f"{gate}.json":
            kill_self()

    def stub(name):
        def f(*a, **kw):
            log(f"synthetic:{name}", f"SYNTHETIC GATE {name} start", klass="SYNTHETIC", notes="crash matrix")
            if point == "during_gate" and name == gate:
                kill_self()
            return {"pass": True, "synthetic": True, "runs": [{"rc": 0, "stdout_tail": "synthetic"}]}
        return f

    Q.os, Q.subprocess, Q.E.log, Q.xwrite = OsProxy(), SubProxy(), log, xwrite
    gate_of = {"qc05": "QC05", "qc06": "QC06", "qc07": "QC07", "qc08": "QC08", "qc09": "QC09", "qc10": "QC10",
               "qc13": "QC13", "qc16": "QC16", "qc17": "QC17", "qc_u2": "QC_U2", "qc_d5": "QC_D5"}
    research = iter(["QC01", "QC02", "QC03", "QC04"])
    formal = iter(["QC11", "QC12", "QC15"])
    Q.qc_research_simple = lambda m, rel, opt=False: stub(next(research))()
    Q.qc_formal = lambda rel, *a, **kw: stub(next(formal))()
    for fn, g in gate_of.items():
        setattr(Q, fn, stub(g))
    Q.mirror = lambda freeze: Path("/nonexistent-synthetic-mirror")
    Q.run = lambda cmd, cwd, timeout=0: (log("synthetic:QC14", "SYNTHETIC GATE QC14 start", klass="SYNTHETIC"),
                                         kill_self() if point == "during_gate" and gate == "QC14" else None,
                                         {"rc": 0, "cmd": ["synthetic"]})[2]
    for name in STUBBED:
        if getattr(Q, name).__module__ == "p309_qualify" and name != "run":
            raise SystemExit(f"child: {name} is not stubbed")
    sys.argv = ["p309_qualify.py", "--workers", "1"]
    return Q.main()


# ================================================================================ child: the new protocol
def child_new(out: Path, crash: str, gates: list) -> int:
    sys.path.insert(0, str(NS / "code"))
    import p309_rehearsal as RH  # noqa: E402
    point, _, gate = crash.partition(":")
    real_write, real_link, real_fsync = os.write, os.link, os.fsync
    current = {"name": ""}

    def write(fd, data):
        if current["name"].startswith(f".{gate}.json.tmp") or (point.endswith("summary") and
                                                                 current["name"].startswith(".REHEARSAL_SUMMARY")):
            if point in ("tmp_partial", "tmp_partial_summary"):
                real_write(fd, bytes(data)[: len(data) // 2])
                kill_self()
        if current["name"] == "GATE_LEDGER.jsonl" and point == "torn_ledger_row" and current.get("gate") == gate:
            real_write(fd, bytes(data)[: len(data) // 2])
            kill_self()
        return real_write(fd, data)

    real_open = os.open

    def open_(path, flags, mode=0o777, **kw):
        current["name"] = Path(path).name
        return real_open(path, flags, mode, **kw)

    def link(src, dst, **kw):
        if Path(dst).name == f"{gate}.json" and point == "after_tmp_before_link":
            kill_self()
        if Path(dst).name == "REHEARSAL_SUMMARY.json" and point == "after_tmp_before_link_summary":
            kill_self()
        real_link(src, dst, **kw)
        if Path(dst).name == f"{gate}.json" and point == "after_link_before_unlink":
            kill_self()

    os.write, os.link, os.open = write, link, open_
    real_append = RH.ledger_append

    def ledger_append(ledger, row):
        current["gate"] = row.get("gate")
        if point == "after_record_before_ledger" and row.get("gate") == gate:
            kill_self()
        if point == "after_summary_before_row" and row.get("event") == "SUMMARY_RECORDED":
            kill_self()
        real_append(ledger, row)
        if point == "after_ledger" and row.get("gate") == gate:
            kill_self()
    RH.ledger_append = ledger_append
    if point == "before_provenance":
        os.mkdir(out)
        os.mkdir(out / "attempt")
        kill_self()
    os.mkdir(out)                                         # exclusive: a second run into the same directory fails
    att = out / "attempt"
    os.mkdir(att)
    ledger = out / "GATE_LEDGER.jsonl"
    prov = {"schema": "P309_REHEARSAL_PROVENANCE/1", "kind": "SYNTHETIC crash matrix", "gates": gates,
            "harness": "frozen", "recorded_freeze": "4c754a73767903a5ad5dddff725f1e173a0a6876",
            "new_target_evaluations": 0, "pid": os.getpid()}
    RH.record_start(out, ledger, prov)
    recs = {}
    for k in gates:
        res = {"pass": True, "synthetic": True, "qc": k, "freeze_commit": prov["recorded_freeze"], "utc": RH.utc(),
               "wall_s": 0.0, "harness": "frozen" if k in ("QC11", "QC_D5") else "n/a"}
        RH.record_gate(att, ledger, k, res)
        recs[k] = res
    summary = {"schema": "P309_REHEARSAL_SUMMARY/1", "freeze_commit": prov["recorded_freeze"], "gates_requested": gates,
               "gates": {k: True for k in gates}, "pass": True,
               "files": {k: RH.sha_file(att / f"{k}.json") for k in gates},
               "provenance_sha256": RH.sha_file(out / "PROVENANCE.json"), "replica_protected_refs_after": []}
    RH.record_summary(out, ledger, summary)
    return 0


# ================================================================================ parent
def sha_tree(*paths: Path) -> str:
    h = hashlib.sha256()
    for root in paths:
        if root.is_file():
            h.update(root.name.encode() + b"\0" + root.read_bytes())
            continue
        if not root.exists():
            h.update(b"<absent>" + str(root).encode())
            continue
        for p in sorted(root.rglob("*")):
            if p.is_file():
                h.update(str(p.relative_to(root)).encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def git(repo: Path, *a: str, check=True) -> str:
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=check).stdout


class Matrix:
    def __init__(self, replica: Path, work: Path):
        self.replica, self.work, self.cases = replica, work, []
        self.fns = replica / NS_R1
        self.qdir = self.fns / "qualification"
        self.ledger = self.fns / "ledger" / "ZERO_TARGET_LEDGER.jsonl"

    # ----- r1
    def reset(self) -> None:
        if self.qdir.exists():
            shutil.rmtree(self.qdir)
        git(self.replica, "checkout", "-q", "--", f"{NS_R1}/ledger")
        if git(self.replica, "rev-parse", "HEAD").strip() != LAUNCH:
            git(self.replica, "reset", "-q", "--hard", LAUNCH)
        st = git(self.replica, "status", "--porcelain", "--untracked-files=all")
        if st.strip():
            raise SystemExit(f"replica not clean after reset: {st[:300]}")

    def r1(self, crash: str = "none", timeout=600) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(HERE), "child-r1", "--replica", str(self.replica), "--crash", crash],
                              capture_output=True, text=True, timeout=timeout)

    def validate_r1(self) -> dict:
        r = subprocess.run([sys.executable, str(VALIDATOR), "r1-attempt", str(self.qdir / "attempt_1"),
                            str(self.ledger), "--record-utc", "2026-09-30T17:06:09Z", "--no-gate-evidence"],
                           capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except ValueError:
            return {"verdict": "VALIDATOR_ERROR", "reasons": [r.stdout[-300:], r.stderr[-300:]]}

    def run_starts(self) -> int:
        return sum(1 for l in self.ledger.read_text().splitlines()
                   if '"purpose": "QUALIFICATION RUN START' in l)

    def resume_probe(self) -> dict:
        """a restart request after the interruption, then two concurrent ones: each must be refused and change
        nothing (attempt and ledger bytes identical)"""
        before = sha_tree(self.qdir, self.ledger)
        r = self.r1("none")
        mid = sha_tree(self.qdir, self.ledger)
        ps = [subprocess.Popen([sys.executable, str(HERE), "child-r1", "--replica", str(self.replica), "--crash",
                                "none"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        outs = [p.communicate(timeout=600) for p in ps]
        after = sha_tree(self.qdir, self.ledger)
        refused = ["QUALIFICATION REFUSED" in r.stdout] + ["QUALIFICATION REFUSED" in o[0] for o in outs]
        return {"refused": refused, "unchanged": before == mid == after, "all_refused_unchanged":
                all(refused) and before == mid == after}

    def add(self, cid: str, desc: str, ok: bool, **detail) -> None:
        self.cases.append({"id": cid, "desc": desc, "pass": bool(ok), **detail})

    def r1_cases(self) -> None:
        expect = [  # (id, crash point, expected verdict, reason fragment, description)
            ("R01", "before_attempt_dir", None, None, "interrupted before the first write"),
            ("R02", "before_run_start", "INTERRUPTED", "without a RUN START", "attempt directory created, no RUN START"),
            ("R03", "during_gate:QC01", "INTERRUPTED", "first missing QC01", "interrupted during the first gate"),
            ("R04", "empty_record:QC05", "CORRUPT", "empty file", "interrupted after open, before write (empty record)"),
            ("R05", "partial_record:QC05", "CORRUPT", "unparseable", "interrupted during the record write (torn)"),
            ("R06", "after_record:QC05", "INTERRUPTED", "first missing QC06",
             "interrupted after the record, before the next ledger update"),
            ("R07", "during_gate:QC06", "INTERRUPTED", "first missing QC06",
             "interrupted after the ledger update (gate start), before its record"),
            ("R08", "during_gate:QC_D5", "INTERRUPTED", "first missing QC_D5",
             "r1's actual case: interrupted during QC-D5 after QC_U2's record"),
            ("R09", "partial_summary", "CORRUPT", "unparseable", "all records written, summary torn"),
            ("R10", "none", "PASS", None, "control: an uninterrupted synthetic run"),
        ]
        for cid, crash, verdict, frag, desc in expect:
            self.reset()
            r = self.r1(crash)
            killed = r.returncode == -signal.SIGKILL
            if crash == "before_attempt_dir":
                no_trace = not (self.qdir / "attempt_1").exists() and self.run_starts() == 0
                r2 = self.r1("none")                     # nothing was recorded: a fresh start is a first start
                v = self.validate_r1()
                self.add(cid, desc, killed and no_trace and v["verdict"] == "PASS" and self.run_starts() == 1,
                         killed=killed, no_trace_before_restart=no_trace, restart_verdict=v["verdict"],
                         run_start_lines=self.run_starts(), restart_stdout=r2.stdout[-200:])
                continue
            v = self.validate_r1()
            ok = v["verdict"] == verdict and (frag is None or any(frag in x for x in v["reasons"]))
            ok = ok and (killed if crash != "none" else r.returncode == 0)
            rp = self.resume_probe() if crash != "none" else {"all_refused_unchanged": True, "note": "complete run"}
            if crash == "none":
                rp = self.resume_probe()                 # a complete run is not re-runnable either
            self.add(cid, desc, ok and rp["all_refused_unchanged"] and self.run_starts() <= 1, crash=crash,
                     killed=killed, verdict=v["verdict"], reasons=v["reasons"][:4], resume=rp,
                     run_start_lines=self.run_starts())

        # stale lock: an empty attempt directory left behind (no RUN START)
        self.reset()
        (self.qdir / "attempt_1").mkdir(parents=True)
        rp = self.resume_probe()
        v = self.validate_r1()
        self.add("R11", "stale lock: an empty attempt directory blocks every restart (fail closed)",
                 rp["all_refused_unchanged"] and v["verdict"] == "INTERRUPTED", verdict=v["verdict"], resume=rp)
        # pre-existing partial artifact
        self.reset()
        (self.qdir / "attempt_1").mkdir(parents=True)
        (self.qdir / "attempt_1" / "QC01.json").write_text('{"pass": tr')
        rp = self.resume_probe()
        v = self.validate_r1()
        self.add("R12", "restart over a pre-existing partial artifact is refused; the artifact is classified CORRUPT",
                 rp["all_refused_unchanged"] and v["verdict"] == "CORRUPT", verdict=v["verdict"], resume=rp)
        # pre-existing summary without an attempt
        self.reset()
        self.qdir.mkdir()
        (self.qdir / "P309_QUALIFICATION.json").write_text("{}")
        b = sha_tree(self.qdir, self.ledger)
        r = self.r1("none")
        self.add("R13", "a stray summary blocks a start", "QUALIFICATION REFUSED" in r.stdout and
                 sha_tree(self.qdir, self.ledger) == b, stdout=r.stdout[-200:])
        # duplicated start request: two fresh runs race
        self.reset()
        ps = [subprocess.Popen([sys.executable, str(HERE), "child-r1", "--replica", str(self.replica), "--crash",
                                "race"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        outs = [p.communicate(timeout=600) for p in ps]
        rcs = sorted(p.returncode for p in ps)
        v = self.validate_r1()
        self.add("R14", "duplicated start request (two racing runners): exactly one attempt, one RUN START, a valid "
                 "record set", self.run_starts() == 1 and v["verdict"] == "PASS" and rcs[0] == 0 and rcs[1] != 0,
                 rcs=rcs, verdict=v["verdict"], loser_stderr=[o[1][-200:] for o in outs if "FileExistsError" in o[1]])
        # torn ledger tail before the start (a truncated checkpoint of the ledger)
        self.reset()
        with open(self.ledger, "a") as fh:
            fh.write('{"utc": "2026-')
        r = self.r1("none")
        v = self.validate_r1()
        self.add("R15", "torn ledger tail before the start: the r1 runner does NOT detect it at start (finding); the "
                 "validator classifies the attempt CORRUPT", v["verdict"] == "CORRUPT" and r.returncode == 0,
                 runner_rc=r.returncode, verdict=v["verdict"], reasons=v["reasons"][:3],
                 finding="r1 runner: no ledger integrity check before RUN START (QC13 would fail hours later)")
        # mismatched commit: a frozen directory changed after the freeze
        self.reset()
        (self.fns / "code" / "zz_mismatch.py").write_text("# changed after the freeze\n")
        git(self.replica, "add", "-A")
        subprocess.run(["git", "-C", str(self.replica), "-c", "user.name=t", "-c", "user.email=t@invalid", "commit",
                        "-qm", "mismatch"], check=True)
        r = self.r1("none")
        refused = "QUALIFICATION REFUSED" in r.stdout and not self.qdir.exists()
        self.add("R16", "start / resume from a mismatched commit (frozen directory changed) is refused before any write",
                 refused, stdout=r.stdout[-200:])
        self.reset()
        # mismatched environment: the real (unstubbed) host binding
        r = subprocess.run([sys.executable, str(self.fns / "code" / "make_freeze_manifest.py"), "--check"],
                           capture_output=True, text=True)
        self.add("R17", "mismatched environment: the frozen manifest binds the freeze host (machine-id + hostname); on "
                 "this host the runner's precondition refuses", r.returncode != 0 and "DIFFERS" in r.stdout,
                 stdout=r.stdout.strip())
        self.reset()

    # ----- new protocol
    def new(self, name: str, crash: str, gates=("QC01", "QC02", "QC03")) -> tuple[Path, subprocess.CompletedProcess]:
        out = self.work / name
        r = subprocess.run([sys.executable, str(HERE), "child-new", "--out", str(out), "--crash", crash, "--gates",
                            ",".join(gates)], capture_output=True, text=True, timeout=120)
        return out, r

    def validate_new(self, out: Path) -> dict:
        r = subprocess.run([sys.executable, str(VALIDATOR), "rehearsal", str(out), "--no-gate-evidence"],
                           capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except ValueError:
            return {"verdict": "VALIDATOR_ERROR", "reasons": [r.stdout[-300:], r.stderr[-300:]]}

    def new_cases(self) -> None:
        expect = [
            ("N01", "before_provenance", "INTERRUPTED", "no provenance", "interrupted before the first write"),
            ("N02", "tmp_partial:QC02", "INTERRUPTED", "leftover temporary", "interrupted during the temporary write"),
            ("N03", "after_tmp_before_link:QC02", "INTERRUPTED", "leftover temporary",
             "temporary complete, record not yet linked"),
            ("N04", "after_link_before_unlink:QC02", "INTERRUPTED", "without its ledger row",
             "record linked, temporary not removed, ledger not updated"),
            ("N05", "after_record_before_ledger:QC02", "INTERRUPTED", "without its ledger row",
             "after the artifact write, before the ledger update"),
            ("N06", "after_ledger:QC02", "INTERRUPTED", "missing", "after the ledger update"),
            ("N07", "torn_ledger_row:QC02", "CORRUPT", "torn", "torn ledger row (power-loss model)"),
            ("N08", "tmp_partial_summary", "INTERRUPTED", "no summary", "interrupted during the summary write"),
            ("N09", "after_summary_before_row", "INTERRUPTED", "summary written but its ledger row is missing",
             "summary written, its ledger row not"),
            ("N10", "none", "PASS", None, "control: an uninterrupted synthetic run"),
        ]
        for cid, crash, verdict, frag, desc in expect:
            out, r = self.new(cid, crash)
            v = self.validate_new(out)
            before = sha_tree(out)
            out2, r2 = self.new(cid, "none")            # restart into the same directory: refused, nothing changes
            refused = r2.returncode != 0 and "FileExistsError" in r2.stderr and sha_tree(out) == before
            ok = v["verdict"] == verdict and (frag is None or any(frag in x for x in v["reasons"])) and refused
            ok = ok and (r.returncode == -signal.SIGKILL if crash != "none" else r.returncode == 0)
            self.add(cid, desc, ok, crash=crash, verdict=v["verdict"], reasons=v["reasons"][:3],
                     restart_refused_unchanged=refused)
        # duplicated start into one directory: exactly one run proceeds
        ps = [subprocess.Popen([sys.executable, str(HERE), "child-new", "--out", str(self.work / "N11"), "--crash",
                                "none", "--gates", "QC01,QC02,QC03"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True) for _ in range(2)]
        [p.communicate(timeout=120) for p in ps]
        v = self.validate_new(self.work / "N11")
        self.add("N11", "duplicated start request into one directory: exactly one run, valid records",
                 sorted(p.returncode for p in ps)[0] == 0 and sorted(p.returncode for p in ps)[1] != 0
                 and v["verdict"] == "PASS", rcs=[p.returncode for p in ps], verdict=v["verdict"])
        # negative fixtures (mutants) on a complete run
        base, _ = self.new("N12_base", "none")

        def mutant(cid, desc, fn, verdict, frag):
            m = self.work / cid
            shutil.copytree(base, m)
            fn(m)
            v = self.validate_new(m)
            self.add(cid, desc, v["verdict"] == verdict and any(frag in x for x in v["reasons"]), verdict=v["verdict"],
                     reasons=v["reasons"][:3])
        other, _ = self.new("N12_other", "none")
        mutant("N13", "mixed provenance: a record from another run swapped in",
               lambda m: shutil.copy(other / "attempt" / "QC02.json", m / "attempt" / "QC02.json"), "CORRUPT", "hash")
        mutant("N14", "stale record: foreign freeze commit",
               lambda m: (m / "attempt" / "QC02.json").write_text(
                   (m / "attempt" / "QC02.json").read_text().replace("4c754a73", "00000000")), "CORRUPT", "foreign freeze")
        mutant("N15", "duplicated ledger row (a gate recorded twice)",
               lambda m: open(m / "GATE_LEDGER.jsonl", "a").write(
                   (m / "GATE_LEDGER.jsonl").read_text().splitlines()[2] + "\n"), "CORRUPT", "duplicate")
        mutant("N16", "ledger row without its record (record deleted)",
               lambda m: (m / "attempt" / "QC03.json").unlink(), "CORRUPT", "without its record")
        mutant("N17", "a second RUN_START (a resumed run appended to an old one)",
               lambda m: open(m / "GATE_LEDGER.jsonl", "a").write(
                   (m / "GATE_LEDGER.jsonl").read_text().splitlines()[0] + "\n"), "CORRUPT", "RUN_START")
        mutant("N18", "a record edited after the summary",
               lambda m: (m / "attempt" / "QC01.json").write_text(
                   (m / "attempt" / "QC01.json").read_text().replace('"wall_s": 0.0', '"wall_s": 1.0')), "CORRUPT",
               "hash")
        mutant("N19", "summary claims a gate the records do not hold",
               lambda m: (m / "REHEARSAL_SUMMARY.json").write_text(
                   (m / "REHEARSAL_SUMMARY.json").read_text().replace('"QC03": true', '"QC03": true, "QC04": true')),
               "CORRUPT", "summary")
        mutant("N20", "a target counter set in the ledger",
               lambda m: open(m / "GATE_LEDGER.jsonl", "a").write('{"event": "X", "new_target_evaluations": 1}\n'),
               "CORRUPT", "target counter")


def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="mode", required=True)
    c1 = sp.add_parser("child-r1")
    c1.add_argument("--replica", required=True)
    c1.add_argument("--crash", default="none")
    c2 = sp.add_parser("child-new")
    c2.add_argument("--out", required=True)
    c2.add_argument("--crash", default="none")
    c2.add_argument("--gates", required=True)
    pm = sp.add_parser("run")
    pm.add_argument("--replica", required=True)
    pm.add_argument("--work", required=True)
    pm.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.mode == "child-r1":
        return child_r1(Path(a.replica).resolve(), a.crash)
    if a.mode == "child-new":
        return child_new(Path(a.out), a.crash, a.gates.split(","))
    replica, work = Path(a.replica).resolve(), Path(a.work).resolve()
    if SCRATCH_ROOT not in replica.parents or SCRATCH_ROOT not in work.parents:
        raise SystemExit("replica and work directory must lie under the scratchpad root")
    if git(replica, "rev-parse", "HEAD").strip() != LAUNCH:
        raise SystemExit("the replica is not at the launch commit")
    work.mkdir(parents=True)
    M = Matrix(replica, work)
    t0 = time.time()
    M.r1_cases()
    M.new_cases()
    fails = [c for c in M.cases if not c["pass"]]
    res = {"schema": "P309_CRASH_MATRIX/1", "pass": not fails, "cases": M.cases,
           "counts": {"total": len(M.cases), "failed": len(fails)}, "wall_s": round(time.time() - t0, 1),
           "python": sys.version.split()[0], "replica_head": LAUNCH,
           "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE, VALIDATOR, REHEARSAL)},
           "statement": "synthetic gates only; nothing evaluated; NEW TARGET EVALUATIONS = 0"}
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    for c in M.cases:
        print(f"[{'PASS' if c['pass'] else 'FAIL'}] {c['id']} {c['desc']} -> {c.get('verdict', '')}")
    print(f"P309 CRASH MATRIX: {len(M.cases) - len(fails)}/{len(M.cases)} pass")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
