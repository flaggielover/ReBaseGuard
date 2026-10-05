#!/usr/bin/env python3
"""Positive and negative unit tests of the runtime hardening (H1-H5), run against a runner in a scratch replica.

  python3 test_r2h_runtime.py --replica R --label hardened|baseline --scratch S --out FILE

Each test works only in temporary directories (the runner's QDIR, ledgers and REPO are pointed there).  Run against
the hardened runner every test must pass; run against r2's runner as shipped, the hardening tests must FAIL -- that
is what shows the tests discriminate (the baseline run is the mutant control).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
HARDENING_TESTS = {"T03_fsync_file_and_dir", "T04_interrupted_write_leaves_no_record", "T05_ledger_problems",
                   "T06_prelaunch_state", "T07_sync_ledgers", "T08_attempt_start_marker"}


def git(repo, *a):
    e = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@invalid", "GIT_COMMITTER_NAME": "t",
         "GIT_COMMITTER_EMAIL": "t@invalid"}
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True, env=e).stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replica", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.environ["P309_SCRATCH_ROOT"] = a.scratch
    sys.path.insert(0, str(Path(a.replica) / NS2 / "code"))
    import p309_qualify as Q  # noqa: E402
    real_os = Q.os
    results = {}

    def case(name, fn):
        try:
            fn()
            results[name] = {"pass": True}
        except Exception as exc:  # noqa: BLE001 - a failed assertion or a missing function is a FAIL
            results[name] = {"pass": False, "error": f"{type(exc).__name__}: {exc}"[:300]}

    class Spy:
        def __init__(self, fail_write_after=None):
            self.ops, self.names, self.fail = [], {}, fail_write_after

        def __getattr__(self, k):
            return getattr(real_os, k)

        def open(self, path, flags, mode=0o777, **kw):
            fd = real_os.open(path, flags, mode, **kw)
            self.names[fd] = Path(path).name
            return fd

        def write(self, fd, data):
            if self.fail is not None:
                real_os.write(fd, bytes(data)[: self.fail])
                raise OSError("injected: interrupted write")
            return real_os.write(fd, data)

        def fsync(self, fd):
            self.ops.append(("fsync", self.names.get(fd, "?")))
            return real_os.fsync(fd)

    tmp = Path(tempfile.mkdtemp(prefix="r2h-unit-", dir=a.scratch))

    def t01():
        d = tmp / "t01"
        d.mkdir()
        Q.xwrite(d / "R.json", '{"a": 1}\n')
        assert (d / "R.json").read_text() == '{"a": 1}\n'
        assert [p.name for p in d.iterdir()] == ["R.json"], "a temporary file was left"

    def t02():
        d = tmp / "t02"
        d.mkdir()
        (d / "R.json").write_text("original\n")
        try:
            Q.xwrite(d / "R.json", "new\n")
        except FileExistsError:
            pass
        else:
            raise AssertionError("an existing record was overwritten")
        assert (d / "R.json").read_text() == "original\n"
        assert [p.name for p in d.iterdir()] == ["R.json"] or all(p.name.startswith(".R.json.tmp") or p.name == "R.json"
                                                                for p in d.iterdir())

    def t03():
        d = tmp / "t03"
        d.mkdir()
        spy = Spy()
        Q.os = spy
        try:
            Q.xwrite(d / "R.json", "x\n")
        finally:
            Q.os = real_os
        names = [n for op, n in spy.ops]
        assert any(n.startswith(".R.json.tmp") for n in names), f"the record bytes were not fsynced: {spy.ops}"
        assert "t03" in names, f"the directory was not fsynced: {spy.ops}"

    def t04():
        d = tmp / "t04"
        d.mkdir()
        Q.os = Spy(fail_write_after=3)
        try:
            try:
                Q.xwrite(d / "R.json", '{"pass": true}\n')
            except OSError:
                pass
        finally:
            Q.os = real_os
        assert not (d / "R.json").exists(), "a torn record exists under its final name"

    def t05():
        d = tmp / "t05"
        d.mkdir()
        ok = d / "ok.jsonl"
        ok.write_text(json.dumps({"new_target_evaluations": 0}) + "\n")
        assert Q._ledger_problems(ok) == []
        torn = d / "torn.jsonl"
        torn.write_text(json.dumps({"a": 0}) + "\n" + '{"utc": "20')
        assert len(Q._ledger_problems(torn)) == 2
        nz = d / "nz.jsonl"
        nz.write_text(json.dumps({"new_target_evaluations": 1}) + "\n")
        assert any("nonzero" in x for x in Q._ledger_problems(nz))

    def t06():
        repo = tmp / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        rec = repo / Q.D.FREEZE_RECORD_REL
        rec.parent.mkdir(parents=True)
        rec.write_text("{}\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "record")
        led = repo / "ledger.jsonl"
        before = json.dumps({"utc": "2000-01-01T00:00:00Z", "purpose": Q.RUN_START + " dev run before the freeze"})
        led.write_text(before + "\n")
        qd = tmp / "qdir"
        qd.mkdir()
        saved = (Q.REPO, Q.QDIR, Q.E.Q.EXEC_LEDGER, Q.E.Q.EXPOSURE_LEDGER)
        Q.REPO, Q.QDIR, Q.E.Q.EXEC_LEDGER, Q.E.Q.EXPOSURE_LEDGER = repo, qd, led, tmp / "none.jsonl"
        try:
            assert Q.prelaunch_state(Q.RUN_START, ()) == [], "a clean state was refused"
            (qd / ".x.tmp-1").write_text("{")
            assert any(".x.tmp-1" in p for p in Q.prelaunch_state(Q.RUN_START, ())), "a temporary file was not refused"
            (qd / ".x.tmp-1").unlink()
            with open(led, "a") as fh:
                fh.write(json.dumps({"utc": "2099-01-01T00:00:00Z", "purpose": Q.RUN_START + " lost attempt"}) + "\n")
            assert any("prior run" in p for p in Q.prelaunch_state(Q.RUN_START, ())), "an orphan RUN START passed"
        finally:
            Q.REPO, Q.QDIR, Q.E.Q.EXEC_LEDGER, Q.E.Q.EXPOSURE_LEDGER = saved

    def t07():
        d = tmp / "t07"
        d.mkdir()
        l1, l2 = d / "a.jsonl", d / "b.jsonl"
        l1.write_text("{}\n")
        l2.write_text("{}\n")
        saved = (Q.E.Q.EXEC_LEDGER, Q.E.Q.EXPOSURE_LEDGER)
        Q.E.Q.EXEC_LEDGER, Q.E.Q.EXPOSURE_LEDGER = l1, l2
        spy = Spy()
        Q.os = spy
        try:
            Q.sync_ledgers()
        finally:
            Q.os = real_os
            Q.E.Q.EXEC_LEDGER, Q.E.Q.EXPOSURE_LEDGER = saved
        names = [n for op, n in spy.ops]
        assert "a.jsonl" in names and "b.jsonl" in names and "t07" in names, spy.ops

    def t08():
        m = Q.attempt_start("f" * 40, {"unit": "u", "mode": "official", "record_bytes": b"r"})
        assert m["boot_id"] and m["runner_sha256"] and "none" in m["retry_rule"] and m["freeze_commit"] == "f" * 40

    for name, fn in [("T01_xwrite_writes_exact_bytes", t01), ("T02_xwrite_never_overwrites", t02),
                     ("T03_fsync_file_and_dir", t03), ("T04_interrupted_write_leaves_no_record", t04),
                     ("T05_ledger_problems", t05), ("T06_prelaunch_state", t06), ("T07_sync_ledgers", t07),
                     ("T08_attempt_start_marker", t08)]:
        case(name, fn)
    if a.label == "hardened":
        ok = all(r["pass"] for r in results.values())
        expectation = "every test passes"
    else:
        ok = all(results[n]["pass"] != (n in HARDENING_TESTS) for n in results)
        expectation = "the hardening tests fail and the common tests pass (the tests discriminate)"
    out = {"schema": "P309_R2H_RUNTIME_TESTS/1", "label": a.label, "expectation": expectation,
           "meets_expectation": ok, "results": results,
           "runner": str(Path(Q.__file__).resolve())}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for n, r in results.items():
        print(f"[{'PASS' if r['pass'] else 'FAIL'}] {n} {r.get('error', '')}")
    print(f"{a.label}: meets expectation ({expectation}): {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
