"""QC01-QC17 and QC-U2 of the P309 formal campaign, run exactly as frozen (package rev. 2b section B, rev. 2c).

  python3 code/p309_qualify.py [--workers 4]                 the one qualification run (all items, no subset)
  python3 code/p309_qualify.py --host-rerun [--workers 4]    rev. 2c A14 / delta D7: QC10 on an owner-named host,
                                                             into qualification/host_rerun/ (a grant-window path)

R4 B8 (no retry-until-pass): the run writes into a fresh qualification/attempt_1/ (created exclusively; every file
O_EXCL, never overwritten) and then qualification/P309_QUALIFICATION.json (O_EXCL).  If ANY attempt directory already
exists the runner refuses: there is no retry and no resumption, and a failed or interrupted attempt is preserved as it
is for the owner and the reviewers.  The summary passes only if this single complete run passes every gate
Q01-Q17, Q-U2 and Q-D5; no gate may be waived.  Every formal tool is pointed at qualification/ through P309_EVIDENCE_DIR, so the
qualification commit touches only qualification/ and the two ledgers (rev. 2c A8).  Research tests that write into
their own namespace run in a read-only `git archive` export of the frozen commit under the scratchpad (the research
namespace itself is never written).

Preconditions (refused otherwise): HEAD's frozen directories equal the freeze commit's; the freeze manifest
regenerates identically; the working tree is clean except qualification/ and the ledgers; no exactly-once ref exists.
Nothing here reads a target input, evaluates a quarantined cell, or computes in the band.

r2 Q-HOST (plan section 7; review P10; addendum 2; delta review C3-C5, C7, C9): the run, and the host re-run, start only
through code/p309_launch.py.  Before the attempt directory and the RUN START (or HOST RERUN START) line exist, it
refuses unless all of these hold:
* the launcher's record (P309_LAUNCH_RECORD) has no blockers, its mode is the one this invocation needs (official or
  drill for the run, host-rerun for the host re-run), and its scratch root holds both the record and this run's
  P309_SCRATCH_ROOT;
* the host configuration file (P309_HOST_CONFIG) has the bytes the record binds (sha256), and gives the configuration
  the launcher used;
* this process runs in the unit the record names (INVOCATION_ID set; /proc/self/cgroup names the unit), and the unit's
  effective properties (`systemctl show`) include Restart=no, KillMode=control-group, KillSignal=SIGKILL,
  NoNewPrivileges, PrivateTmp and ProtectSystem=strict;
* the host is the one the launcher audited (Q-HOST continuity: boot, machine-id, hostname, instance, interpreter,
  glibc, no suspend), and the cloud instance id, if the launch read one, is read again now (C3);
* the record's mode fits the repository (a drill runs in a clone under the launch's scratch root; the official run
  and the host re-run never do).
The attempt keeps the start evidence: a copy of the (redacted) launch record with the gate, isolation and preflight
results, the unit's effective properties, and their sha256 in QHOST_BASELINE.json (C9).
During the run a monitor (p309_host.py qhost-monitor, every <= 60 s) records continuity and cell-308 activity into the
attempt.  On a failure it signals this process, which SIGKILLs its own process tree at once (C5), records Q-HOST FAIL
and the summary (pass false) and exits; systemd's KillMode=control-group with KillSignal=SIGKILL stops anything left
(owner decision OD-R2-5 option (i); option (ii) would need the owner to amend message 3 section 3).  At the end Q-HOST
passes only if every sample passed, the monitor was alive at the stop with no gap over the interval plus the
tolerance (C4), and a final sample still shows the same host (A15).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import random
import signal
import shutil
import subprocess
import sys
import time
from fractions import Fraction as F
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
REPO = FNS.parents[2]
sys.path.insert(0, str(FNS / "code"))
import p309_env as E  # noqa: E402
import p309_driver as D  # noqa: E402
import p309_host as H  # noqa: E402  (r2 Q-HOST)

QDIR = FNS / "qualification"
SCRATCH = E.scratch_dir("qualification")   # r2 P7: under P309_SCRATCH_ROOT (validated; no fallback)
MIRROR_PATHS = ["level4/closure_proofs/p5y_k5_cell309_research_r1",
                "level4/closure_proofs/p5y_k5_tail_overnight_research/streams/C_308/LR/cusum",
                "level4/closure_proofs/p5y_k5_tail_overnight_research/validation",
                "level4/closure_proofs/p5y_k5_tail_overnight_research/code/ov_fixtures.py",       # QC03's imports
                "level4/closure_proofs/p5y_k5_tail_overnight_research/code/ov_quarantine.py",
                "level4/closure_proofs/p5y_k5_tail_overnight_research/streams/D_309/code/d309_core.py",
                "level4/closure_proofs/p5y_k5_tail_overnight_research/streams/D_309/code/d309_rso.py"]
RMIR = "level4/closure_proofs/p5y_k5_cell309_research_r1"
PY = sys.executable


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


ATT = {"dir": None, "label": "qualification"}         # the attempt directory; the ledger label (delta-2 E6)
RUN_START = "QUALIFICATION RUN START"                   # the single run's ledger line (delta-2 E6)
HOST_START = "HOST RERUN START"


def _fsync_dir(d: Path) -> None:
    """hardening H1: make a directory entry (a new file or subdirectory name) durable"""
    fd = os.open(str(d), os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _fsync_path(p: Path) -> None:
    try:
        fd = os.open(str(p), os.O_RDONLY)
    except FileNotFoundError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def xwrite(path: Path, text: str) -> None:
    """write a new file exclusively and durably (never overwrite).
    Hardening H1: the bytes go to a temporary file in the same directory (O_EXCL), are written completely and
    fsynced, then hard-linked to the final name -- os.link fails if the name exists, so a record is never overwritten
    -- the temporary name is removed and the directory is fsynced.  An interruption therefore leaves either no record
    or a complete one (plus at most a temporary file, which the pre-launch check H3 refuses and the status classifier
    reports as INTERRUPTED): never a torn or empty record under its final name."""
    path = Path(path)
    data = text.encode()
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        view = memoryview(data)
        while view:
            view = view[os.write(fd, view):]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.link(tmp, path)                                   # FileExistsError: an existing record is never replaced
    os.unlink(tmp)
    _fsync_dir(path.parent)


def sync_ledgers() -> None:
    """hardening H2: the execution and exposure ledgers are appended by this process and by the gates' subprocesses
    (q309_guard.log_execution, unchanged); after every start line and every gate record their bytes and directory
    entries are fsynced, so a ledger row is durable before the next step depends on it"""
    for p in (E.Q.EXEC_LEDGER, E.Q.EXPOSURE_LEDGER):
        _fsync_path(Path(p))
        if Path(p).parent.exists():
            _fsync_dir(Path(p).parent)


def _oserr(exc: OSError) -> str:
    return f"{type(exc).__name__} (errno {exc.errno}: {exc.strerror or exc})"


def fs_probe(where: Path) -> list:
    """S1 (independent review of the hardening): a fail-fast proof, before Q-HOST, the attempt directory and the start
    line, that the filesystem holding `where` (the qualification directory) supports exactly what xwrite, sync_ledgers
    and the exclusive attempt rely on: an exclusive create (O_EXCL) that refuses an existing name, a complete write and
    a file fsync, a same-directory hard link that is a second name of the same file and refuses an existing name, a
    directory fsync, and sync_ledgers itself (both ledgers and their directories).  It works only inside its own new
    directory where/.p309-fsprobe-<pid>/ and removes it, so no qualification evidence persists.  A probe directory left
    by an interrupted probe is refused by name and never removed here (nothing is repaired).  Returns the problems, each
    naming the step and the error; an empty list means supported.  Nothing is retried."""
    prefix = ".p309-fsprobe-"
    if not where.is_dir():
        return [f"{where.name}/ does not exist (nothing to probe)"]
    left = sorted(p.name for p in where.iterdir() if p.name.startswith(prefix))
    if left:
        return [f"{where.name}/{n} is left by an interrupted filesystem probe (no attempt was started; it holds only "
                "probe files): remove it by hand, then launch again" for n in left]
    d = where / f"{prefix}{os.getpid()}"
    a, b = d / "probe.a", d / "probe.b"
    data = b"P309 filesystem probe\n"
    step = f"create the probe directory {where.name}/{d.name}"
    try:
        os.mkdir(d)
    except OSError as exc:
        return [f"{step}: {_oserr(exc)}"]
    problems = []
    try:
        step = "exclusive create (O_EXCL)"
        fd = os.open(a, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
        try:
            step = "write"
            view = memoryview(data)
            while view:
                view = view[os.write(fd, view):]
            step = "file fsync"
            os.fsync(fd)
        finally:
            os.close(fd)
        step = "exclusive create over an existing name"
        try:
            os.close(os.open(a, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644))
            problems.append(f"{step}: O_EXCL did not refuse an existing name")
        except FileExistsError:
            pass
        step = "same-directory hard link"
        os.link(a, b)
        sa, sb = os.stat(a), os.stat(b)
        if (sa.st_dev, sa.st_ino) != (sb.st_dev, sb.st_ino) or sa.st_nlink < 2:
            problems.append(f"{step}: the new name is not a second name of the same file (inodes {sa.st_ino} and "
                            f"{sb.st_ino}, link count {sa.st_nlink})")
        elif b.read_bytes() != data:
            problems.append(f"{step}: the new name does not read back the bytes written")
        step = "hard link over an existing name"
        try:
            os.link(a, b)
            problems.append(f"{step}: os.link did not refuse an existing name (a record could be replaced)")
        except FileExistsError:
            pass
        step = "directory fsync"
        _fsync_dir(d)
        _fsync_dir(where)
        step = "ledger and ledger-directory fsync (sync_ledgers)"
        sync_ledgers()
    except OSError as exc:
        problems.append(f"{step}: {_oserr(exc)}")
    finally:
        for p in (b, a):
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass
            except OSError as exc:
                problems.append(f"remove the probe file {p.name}: {_oserr(exc)}")
        try:
            os.rmdir(d)
        except OSError as exc:
            problems.append(f"remove the probe directory {where.name}/{d.name}: {_oserr(exc)} (it blocks every launch "
                            "until removed by hand)")
        else:
            try:
                _fsync_dir(where)
            except OSError as exc:
                problems.append(f"directory fsync after removing the probe: {_oserr(exc)}")
    return problems


def _ledger_problems(p: Path) -> list:
    """hardening H3: a ledger is launchable only if every row parses, the file ends with a newline and every target
    counter is zero"""
    if not p.exists():
        return []
    raw = p.read_bytes()
    bad = [] if not raw or raw.endswith(b"\n") else [f"{p.name}: the last row has no newline (torn append)"]
    for i, line in enumerate(raw.decode(errors="replace").splitlines()):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            bad.append(f"{p.name}: row {i + 1} does not parse (torn or corrupt)")
            continue
        if any(row.get(k, 0) != 0 for k in ("new_target_evaluations", "target_equivalent_proxies",
                                              "target_informed_optimisation")):
            bad.append(f"{p.name}: row {i + 1} has a nonzero target counter")
    return bad


def prelaunch_state(start_prefix: str, allowed: tuple) -> list:
    """hardening H3: deterministic refusal on any trace of a prior or partial run, before Q-HOST, the attempt directory
    and the start line exist.  Refused when: the qualification directory holds anything but the `allowed` entries
    (a prior attempt, a stray summary, a temporary file of an interrupted write); a ledger has a torn or unparseable
    row or a nonzero counter; or a `start_prefix` line was logged at or after the freeze record (a prior run whose
    attempt directory is missing).  Nothing is repaired, removed or resumed."""
    problems = []
    if QDIR.exists():
        problems += [f"qualification/{p.name} exists (a prior or partial run)" for p in sorted(QDIR.iterdir())
                     if p.name not in allowed]
    for p in (E.Q.EXEC_LEDGER, E.Q.EXPOSURE_LEDGER):
        problems += _ledger_problems(Path(p))
    rec = git("log", "-1", "--format=%cI", "--", D.FREEZE_RECORD_REL)     # the registered read runner
    try:
        t0 = datetime.datetime.fromisoformat(rec).astimezone(datetime.timezone.utc)
    except ValueError:
        return problems + ["the freeze record's commit time is unreadable"]
    for line in Path(E.Q.EXEC_LEDGER).read_text(errors="replace").splitlines() if Path(E.Q.EXEC_LEDGER).exists() else []:
        try:
            row = json.loads(line)
            when = datetime.datetime.fromisoformat(str(row.get("utc", "")).replace("Z", "+00:00"))
        except ValueError:
            continue
        if str(row.get("purpose", "")).startswith(start_prefix) and when >= t0:
            problems.append(f"a '{start_prefix}' line at {row.get('utc')} after the freeze record: a prior run's "
                            "attempt is missing")
    return problems


def run(cmd: list, cwd: Path, timeout: int = 6 * 3600) -> dict:
    env = dict(os.environ)
    env["P309_EVIDENCE_DIR"] = str(ATT["dir"] / "evidence")
    t0 = time.time()
    r0 = os.times()
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, env=env)
    r1 = os.times()
    return {"cmd": [str(c) for c in cmd], "rc": p.returncode, "wall_s": round(time.time() - t0, 1),
            "cpu_children_s": round((r1.children_user - r0.children_user) + (r1.children_system - r0.children_system), 1),
            "stdout_tail": p.stdout[-3000:], "stderr_tail": p.stderr[-2000:]}


def mirror(freeze_commit: str) -> Path:
    m = SCRATCH / f"mirror_{freeze_commit[:12]}"
    if m.exists():
        shutil.rmtree(m)
    m.mkdir(parents=True)
    arch = subprocess.run(["git", "-C", str(REPO), "archive", "--end-of-options", freeze_commit, *MIRROR_PATHS],
                          capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(m)], input=arch, check=True)
    return m


def research_test(m: Path, rel: str, *args, opt: bool = False) -> dict:
    E.log(f"{RMIR}/{rel} (in the archive mirror)", f"{ATT['label']}: research test {rel} {' '.join(args)}",
          klass="NONTARGET_DECOY", notes="read-only export of the frozen commit; outputs stay in the mirror")
    if opt:
        return run([PY, "-O", str(m / RMIR / rel), *args], m / RMIR)
    return run([PY, str(m / RMIR / rel), *args], m / RMIR)


# ---------------------------------------------------------------------------------------------------- the items
def qc_research_simple(m: Path, rel: str, opt=False) -> dict:
    r = research_test(m, rel)
    out = {"pass": r["rc"] == 0, "runs": [r]}
    if opt:
        r2 = research_test(m, rel, opt=True)
        out["runs"].append(r2)
        out["pass"] = out["pass"] and r2["rc"] == 0
    return out


def qc05(m: Path) -> dict:
    r = research_test(m, "tests/test_srk_adapter.py")
    import p309_rehearse as RH
    import srk_adapter as AD
    import srk_gate as GT
    man = D.load_manifest()
    con = D.load_consumer(man)
    E.log("code/p309_qualify.py QC05", "QC05 pinned tct_rule re-assembly equality on 12 manufactured seeds",
          klass="SYNTHETIC", notes="manufactured TC-T-shaped inputs; no tail input read")
    eq = {}
    for seed in range(1, 13):
        mf = RH.manufactured(seed)
        T, R = con["T"], con["R"]
        lo, hi, obj = T.tail_enclosure(R, mf["meas"], mf["aux"], mf["A"], 5, None)
        empty = GT.GateResult.empty(RH.DECOY_CELL[0], RH.DECOY_CELL[1], dict(D.GEOMETRY), (1, 2, 3, 4))
        H = AD.srk_enclosure(mf["meas"], mf["A"], 5, RH.DECOY_CELL, empty, obj, (lo, hi), R.coefficients,
                             verifier_id="sha256:" + "0" * 64)
        eq[seed] = (H["lo"], H["hi"]) == (lo, hi)
    return {"pass": r["rc"] == 0 and all(eq.values()), "runs": [r], "pinned_equality_by_seed": eq}


def qc06(m: Path) -> dict:
    vdir = m / RMIR / "verify"
    ref = json.loads((vdir / "VERIFY_RESULTS.json").read_text())
    (vdir / "VERIFY_RESULTS.json").rename(vdir / "VERIFY_RESULTS.committed.json")
    E.log(f"{RMIR}/verify/run_verify_all.py (mirror)", "QC06 research verifier v2 battery on the declared decoy suite",
          klass="NONTARGET_DECOY", drifts=[["-1/3", "37/32"]],
          notes="the research verifier, genuine + v2 mutants + self-tests; probes out of band (ERRATA E-17)")
    r = run([PY, str(vdir / "run_verify_all.py"), "--redo", "--jobs", "3", "--unit-tests"], vdir)
    new = json.loads((vdir / "VERIFY_RESULTS.json").read_text())
    diffs = []
    for f, per in ref["files"].items():
        for i, e in per.items():
            n = new["files"].get(f, {}).get(i)
            if not n or (n.get("verdict"), n.get("reason")) != (e.get("verdict"), e.get("reason")):
                diffs.append(f"{f}#{i}")
    s = new["summary"]["by_harness"]["v2"]
    ok = r["rc"] == 0 and not diffs and s["mutant_expectations_met"] == s["mutants_run"] and not s[
        "expectation_not_met"] and new["unit_selftests"].get("ok") is True
    return {"pass": ok, "runs": [r], "verdict_reason_differences": diffs[:20], "summary": new["summary"],
            "unit_selftests": {k: new["unit_selftests"].get(k) for k in ("ok", "ran", "tests")}}


def qc07(m: Path) -> dict:
    return qc_research_simple(m, "tests/srk_mc_control.py")


def decoy_stage1a(tag: str, workers: int) -> dict:
    out = ATT["dir"] / f"{tag}_DECOY_STAGE1A.json"
    r = run([PY, "-B", str(FNS / "code" / "p309_driver.py"), "decoy-stage1a", "--decoy", "a2_h5",
             "--workers", str(workers), "--out", str(out)], FNS, timeout=24 * 3600)
    return {"run": r, "out": out}


def qc08(m: Path, workers: int) -> dict:
    d = decoy_stage1a("QC08", workers)
    res = json.loads(d["out"].read_text()) if d["out"].exists() else {}
    jobs = res.get("jobs", {})
    returned = [j for j in jobs.values() if j.get("kind") == "JOB_RETURNED"]
    verdicts = res.get("verdicts", {})
    # per-rung certificates of the research best rung are byte-identical to the committed research certificates
    ident, compared = [], 0
    for j in range(4):
        rd = json.loads((m / RMIR / f"evidence/srk_decoys_cell/cell_h5_k1_2_C1_2_37_72_S{j}.json").read_text())
        for i, c in rd["certificates"].items():
            if c.get("status") != "CERTIFIED":
                continue
            mine = [x for x in res.get("certificates", []) if x["block"] == c["block"] and x["hermite_index"] == int(i)
                    and x["degree"] == c["degree"]]
            compared += 1
            ident.append(len(mine) == 1 and mine[0]["sha256"] == c["sha256"])
    batteries = [research_test(m, "tests/test_srk_gate.py"), research_test(m, "tests/test_srk_wrec_refusal.py"),
                 research_test(m, "tests/test_srk_cert_mutants.py"), research_test(m, "tests/e2e_cell_family.py")]
    ok = (d["run"]["rc"] == 0 and res.get("gate", {}).get("source") == "GATE" and len(returned) == 12 and
          set(verdicts.values()) <= {"ACCEPT"} and not res.get("run", {}).get("not_started") and compared > 0
          and all(ident) and all(b["rc"] == 0 for b in batteries))
    return {"pass": ok, "runs": [d["run"]] + batteries, "gate": res.get("gate"), "jobs_returned": len(returned),
            "verdicts": sorted(set(verdicts.values())), "research_best_rung_byte_identity": {
                "compared": compared, "identical": sum(ident)}, "cpu_s_total": res.get("run", {}).get("cpu_s_total")}


def qc09(workers: int) -> dict:
    out, runs, cells = {}, [], {}
    for k in D.DECOY_STAGE1B_CELLS:
        f = ATT["dir"] / f"QC09_DECOY_STAGE1B_{k}.json"
        r = run([PY, "-B", str(FNS / "code" / "p309_driver.py"), "decoy-stage1b", "--cell", str(k),
                 "--workers", str(workers), "--out", str(f)], FNS, timeout=24 * 3600)
        runs.append(r)
        res = json.loads(f.read_text()) if f.exists() else {}
        cells[k] = {"status": res.get("cell", {}).get("status"),
                    "independent_checks": res.get("independent_checks"), "cpu_s_total": res.get("run", {}).get(
                        "cpu_s_total")}
    ok = all(r["rc"] == 0 for r in runs) and all(c["independent_checks"] and c["independent_checks"].get("all_equal")
                                                  for c in cells.values())
    return {"pass": ok, "runs": runs, "cells": cells}


def qc10(workers: int) -> dict:
    d = decoy_stage1a("QC10", workers)
    a = json.loads((ATT["dir"] / "QC08_DECOY_STAGE1A.json").read_text())
    b = json.loads(d["out"].read_text()) if d["out"].exists() else {}
    sa = sorted(c["sha256"] for c in a.get("certificates", []))
    sb = sorted(c["sha256"] for c in b.get("certificates", []))
    same = sa == sb and a.get("verdicts") == b.get("verdicts") and a.get("gate") == b.get("gate")
    return {"pass": d["run"]["rc"] == 0 and same and len(sa) > 0, "runs": [d["run"]], "certificates": len(sa),
            "byte_identical": same, "interpreter": platform.python_version(),
            "platform": f"{sys.platform} {platform.machine()}", "host_id_sha256": D.G.host_id(),
            "note": "QC08 and QC10 both run on this host (the proposed execution host, rev. 2c A14)"}


def git(*a) -> str:
    """read-only git in this repository (a registered runner: the scanner checks every caller's verb)"""
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()


def qc_formal(cmd_rel: str, *args, flags: bool = False) -> dict:
    if flags:
        r = run([PY, "-I", "-S", "-B", str(FNS / cmd_rel), *args], FNS, timeout=12 * 3600)
    else:
        r = run([PY, str(FNS / cmd_rel), *args], FNS, timeout=12 * 3600)
    return {"pass": r["rc"] == 0, "runs": [r]}


def ledger_append_only(freeze: str) -> bool:
    """R4 follow-up 2 NF4: every committed version of the execution ledger from the freeze commit to HEAD, and the
    working copy, is a byte prefix of the next -- a deleted attempt directory AND a deleted ledger line would
    otherwise leave no trace"""
    rel = f"{D.NS_REL}/ledger/ZERO_TARGET_LEDGER.jsonl"
    commits = git("rev-list", "--reverse", f"{freeze}..HEAD", "--", rel).split()
    versions = [subprocess.run(["git", "-C", str(REPO), "show", f"{freeze}:{rel}"], capture_output=True).stdout]
    for c in commits:
        versions.append(subprocess.run(["git", "-C", str(REPO), "show", f"{c}:{rel}"], capture_output=True).stdout)
    versions.append((REPO / rel).read_bytes())
    return all(b.startswith(a) for a, b in zip(versions, versions[1:]))


def qc13(freeze: str) -> dict:
    frozen_now = [git("rev-parse", f"HEAD:{D.NS_REL}/{d}") for d in D.FROZEN_DIRS]
    frozen_then = [git("rev-parse", f"{freeze}:{D.NS_REL}/{d}") for d in D.FROZEN_DIRS]
    refs = git("for-each-ref", "--format=%(refname)").splitlines()
    try:
        recorded = D.recorded_freeze()
    except D.Refusal as exc:
        recorded = f"refused: {exc}"
    ok = {"freeze_record_valid_and_names_this_freeze": recorded == freeze,
          "freeze_is_last_frozen_change": D.freeze_commit() == freeze,
          "frozen_dirs_unchanged_since_freeze": frozen_now == frozen_then,
          "r5_blob_unchanged": git("rev-parse", "HEAD:level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/"
                                            "K5_COVERAGE_MAP_R5.json") == "f978eeb6b41188eabaf3c6d590c9178d711f1ce6",
          "no_exactly_once_ref": not [r for r in refs if r.startswith(D.G._FORBIDDEN_NAMESPACES)],
          "research_namespace_unchanged": not git("diff", "--name-only", "eb9a9c22b093f938e1bf13e0b30512608c58c370",
                                                "HEAD", "--", D.RNS_REL),
          # r2 addendum 1, P2: r1's namespace is never mutated (its tree at r1's final head c902fe2f)
          "r1_namespace_unchanged": git("rev-parse", "HEAD:level4/closure_proofs/p5y_k5_cell309_p309_r1")
          == "ecd1c359ef0c3e0c9911b014b884376a10f6ed5b",
          "qualification_after_freeze": subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", freeze,
                                                        "HEAD"]).returncode == 0}
    ok["no_r6"] = not any("COVERAGE_MAP_R6" in p.upper()
                          for p in git("ls-tree", "-r", "--name-only", "HEAD").splitlines())
    ok["single_qualification_run_since_the_freeze_record"] = single_run_since_freeze()
    ok["execution_ledger_append_only_since_the_freeze"] = ledger_append_only(freeze)
    ph = qc_formal("code/p309_placeholder_check.py")
    ok["no_placeholder_or_choice"] = ph["pass"]
    params = subprocess.run([PY, str(FNS / "code" / "make_freeze_params.py"), "--check"], capture_output=True, text=True)
    ok["freeze_params_regenerate_identically"] = params.returncode == 0
    return {"pass": all(ok.values()), "checks": ok, "runs": ph["runs"]}


def single_run_since_freeze() -> bool:
    """delta-2 E6: from the execution ledger, anchored at the freeze record's commit time, exactly one qualification
    run started after the freeze (this one), and no host re-run started before it"""
    try:
        rec_commit = subprocess.run(["git", "-C", str(REPO), "log", "--format=%H %cI", "--", D.FREEZE_RECORD_REL],
                                    capture_output=True, text=True).stdout.split()
        t0 = datetime.datetime.fromisoformat(rec_commit[1]).astimezone(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
    except (IndexError, ValueError):
        return False
    rows = [json.loads(l) for l in (FNS / "ledger" / "ZERO_TARGET_LEDGER.jsonl").read_text().splitlines() if l.strip()]
    after = [r for r in rows if r.get("utc", "") >= t0]
    starts = [r for r in after if str(r.get("purpose", "")).startswith(RUN_START)]
    hosts = [r for r in after if str(r.get("purpose", "")).startswith(HOST_START)]
    return len(starts) == 1 and not hosts


def qc16() -> dict:
    parts = [qc_formal("verify/run_verify_all_scoped.py", "--jobs", "3", "--unit-tests", "--out",
                       str(ATT["dir"] / "evidence" / "VERIFY_RESULTS_SCOPED.json")),
             qc_formal("tests/test_verify_scoped.py"), qc_formal("tests/test_p309_guard.py", flags=True),
             qc_formal("tests/test_p309_scan_allowance.py")]
    return {"pass": all(x["pass"] for x in parts), "parts": parts}


def qc_u2() -> dict:
    parts = [qc_formal("code/u2_structure_check.py"), qc_formal("tests/test_u2_structure_controls.py")]
    return {"pass": all(x["pass"] for x in parts), "parts": parts}


def qc17() -> dict:
    IND = D._ind() or D.load_rlr307(D.load_manifest())["rlr307_independent"]
    E.log("code/p309_qualify.py QC17", "QC17 S construction on manufactured supplies", klass="SYNTHETIC",
          notes="manufactured supplies only")
    rng = random.Random(20260930)
    bad = 0
    for _ in range(2000):
        A = {j: F(rng.randint(1, 10 ** 6), rng.randint(1, 10 ** 4)) for j in D.FIELDS}
        c = {"A1_SUPPLY_max": D.fs(F(rng.randint(1, 10 ** 6), rng.randint(1, 10 ** 4))),
             "A2_SUPPLY_max": D.fs(F(rng.randint(1, 10 ** 6), rng.randint(1, 10 ** 4)))}
        S = D.compose_S(A, {"cell": {"status": "CERTIFIED", **c}})
        ind = IND.consumed(A, {"A1_SUPPLY": c["A1_SUPPLY_max"], "A2_SUPPLY": c["A2_SUPPLY_max"]})
        fb = D.compose_S(A, {"cell": {"status": "CERTIFICATION_FAILED"}})
        if S != ind or fb != A or D.compose_S(A, None) != A or S["A0"] != A["A0"]:
            bad += 1
    return {"pass": bad == 0, "cases": 2000, "mismatches": bad}


def qc_d5() -> dict:
    """owner D5: the exception is limited to the two ratified sites -- the control suite (with R4's M01-M15), the
    runtime backstop controls (R4F F1(a)), and the scanner's AST-pinned lists current (no unlisted, stale, missing or
    unnecessary entry)"""
    parts = [qc_formal("tests/test_p309_d5_exception.py", flags=True),
             qc_formal("tests/test_p309_site_backstop.py", flags=True)]
    pins = run([PY, str(FNS / "code" / "p309_scan_pins.py"), "--list"], FNS)
    bad = [l for l in pins["stdout_tail"].splitlines() if "NOT LISTED" in l or "STALE" in l or "remove the entry" in l
           or l.endswith(": missing")]
    parts.append({"pass": pins["rc"] == 0 and not bad and "P309 SCAN PINS: all current" in pins["stdout_tail"],
                  "runs": [pins], "not_current": bad})
    return {"pass": all(x["pass"] for x in parts), "parts": parts}


def _under(path: Path, root: str) -> bool:
    rp, rr = os.path.realpath(str(path)), os.path.realpath(root)
    return rp == rr or rp.startswith(rr + os.sep)


UNIT_REQUIRED = {"Restart": ("no",), "KillMode": ("control-group",), "KillSignal": ("9", "SIGKILL"),
                 "NoNewPrivileges": ("yes",), "PrivateTmp": ("yes",), "ProtectSystem": ("strict",)}


def qhost_preflight(modes: tuple) -> dict:
    """r2 P10: every Q-HOST refusal, before the attempt directory and the RUN START line exist.  Raises H.HostError."""
    scratch = H.scratch_root(dict(os.environ), str(REPO), {"foreign_roots": []})
    rec_path = os.environ.get("P309_LAUNCH_RECORD")
    if not rec_path or not Path(rec_path).is_file():
        raise H.HostError("no launch record: the run starts only through code/p309_launch.py")
    rec_bytes = Path(rec_path).read_bytes()
    rec = json.loads(rec_bytes)
    root = rec.get("scratch_root") or ""
    if not root or not _under(Path(rec_path), root) or not _under(Path(scratch), root):
        raise H.HostError("the launch record or this run's scratch root lies outside the launch's scratch root")
    if rec.get("blockers") or rec.get("mode") not in modes:
        raise H.HostError(f"the launch record has blockers or a mode other than {modes}: {rec.get('blockers')}")
    if (rec["mode"] == "drill") != _under(REPO, root):
        raise H.HostError("the launch mode does not fit the repository (a drill runs only in a clone under the "
                          "launch's scratch root; the official run and the host re-run never do)")
    if not os.environ.get("INVOCATION_ID") or (rec.get("unit", "") + ".service") not in (
            Path("/proc/self/cgroup").read_text() if Path("/proc/self/cgroup").exists() else ""):
        raise H.HostError("not running inside the launched systemd unit")
    conf_path = os.environ.get("P309_HOST_CONFIG") or ""
    if not conf_path or H.file_sha256(conf_path) != rec.get("host_config_file_sha256"):
        raise H.HostError("the host configuration file is missing or differs from the one the launch record binds")
    cfg = H.load_launch_config(conf_path, str(REPO), rec["mode"] != "drill")[0]
    if H.config_sha256(dict(cfg, p309_repo=rec["host_config"].get("p309_repo"))) != rec.get("host_config_sha256"):
        raise H.HostError("the host configuration differs from the one the launcher used")
    props = H.unit_properties()
    bad = {k: (props or {}).get(k) for k, ok in UNIT_REQUIRED.items() if (props or {}).get(k) not in ok}
    if props is None or bad:
        raise H.HostError(f"the unit's effective properties are not the launcher's: {bad if props else 'unreadable'}")
    now = H.provenance(cfg)
    launch_prov = rec["preflight"]["provenance"]
    if (launch_prov.get("cloud") or {}).get("instance_id_sha256") and not (now.get("cloud") or {}).get(
            "instance_id_sha256"):
        raise H.HostError("the launch read the cloud instance id and this baseline could not (C3)")
    cont = H.continuity(launch_prov, now, cfg)
    if not cont["pass"]:
        raise H.HostError(f"the host changed since the launch: {cont['checks']}")
    return {"record": rec_path, "record_bytes": rec_bytes, "unit": rec["unit"], "mode": rec["mode"], "cfg": cfg,
            "baseline": now, "continuity_since_launch": cont, "unit_properties": props,
            "host_config_file_sha256": rec["host_config_file_sha256"]}


QHOST_INTERVAL = 60.0
QHOST = {"monitor": None, "file": None, "started": None, "qh": None, "interval": QHOST_INTERVAL}


def _qhost_abort(signum, frame) -> None:
    """the monitor's signal: SIGKILL this process's own tree at once (C5: the heavy jobs ignore SIGTERM), record
    Q-HOST FAIL and the failed summary, then exit; KillMode=control-group with KillSignal=SIGKILL stops anything left
    in the unit.  Nothing is retried or resumed (R4 B8)."""
    try:
        killed = H.kill_own_descendants()
        xwrite(ATT["dir"] / "QHOST_FAIL.json", json.dumps({"utc": utc(), "signal": signum, "monitor_file": str(
            QHOST["file"]), "descendants_killed": len(killed)}, indent=1) + "\n")
        reason = "Q-HOST: the host changed or cell-308 heavy work appeared during the run (OD-R2-5 (i))"
        if ATT["label"] == "host_rerun":
            xwrite(ATT["dir"] / "QC10_HOST_RERUN.json", json.dumps({
                "schema": "P309_HOST_RERUN/2", "utc": utc(), "pass": False, "reason": reason}, indent=1) + "\n")
        else:
            xwrite(QDIR / "P309_QUALIFICATION.json", json.dumps({
                "schema": "P309_QUALIFICATION/2", "attempt": ATT["dir"].name, "utc": utc(), "pass": False,
                "reason": reason, "retry_rule": "none (R4 B8; r2 P23)"}, indent=1, sort_keys=True) + "\n")
        E.log("code/p309_qualify.py", f"{ATT['label'].upper()} ABORTED BY Q-HOST (the attempt is preserved; no retry)",
              klass="GOVERNANCE", notes="r2 P10")
        sync_ledgers()                                        # hardening H2
    finally:
        os._exit(3)


def start_qhost_monitor(qh: dict) -> None:
    """keep the start evidence in the attempt (C9), then start the monitor; its configuration goes on its standard
    input, never on its command line"""
    xwrite(ATT["dir"] / "LAUNCH_RECORD.json", qh["record_bytes"].decode())
    props = json.dumps(qh["unit_properties"], indent=1, sort_keys=True) + "\n"
    xwrite(ATT["dir"] / "UNIT_PROPERTIES.json", props)
    xwrite(ATT["dir"] / "QHOST_BASELINE.json", json.dumps(dict({k: qh[k] for k in (
        "record", "unit", "mode", "baseline", "continuity_since_launch", "host_config_file_sha256")},
        launch_record_sha256=hashlib.sha256(qh["record_bytes"]).hexdigest(),
        unit_properties_sha256=hashlib.sha256(props.encode()).hexdigest(), interval_s=QHOST["interval"],
        gap_tolerance_s=qh["cfg"]["monitor_gap_tolerance_s"]), indent=1, sort_keys=True, default=str) + "\n")
    QHOST["file"], QHOST["qh"] = ATT["dir"] / "QHOST_MONITOR.jsonl", qh
    fh = open(os.open(QHOST["file"], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644), "w")
    signal.signal(signal.SIGTERM, _qhost_abort)
    QHOST["started"] = time.monotonic()                   # follow-up SF1: the monitor's clock (system-wide)
    QHOST["monitor"] = subprocess.Popen(
        [PY, "-B", str(FNS / "code" / "p309_host.py"), "qhost-monitor", "--parent", str(os.getpid()), "--interval",
         str(QHOST["interval"])], stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, universal_newlines=True)
    QHOST["monitor"].stdin.write(json.dumps({"cfg": qh["cfg"], "baseline": qh["baseline"]}))
    QHOST["monitor"].stdin.close()


def stop_qhost_monitor() -> dict:
    """stop the monitor and judge Q-HOST: at least one sample completed and every sample passed, the monitor was alive
    at the stop and left no gap over the interval plus the tolerance between any two of its events on the monotonic
    clock (C4; follow-up SF1), the monitor file is not corrupt (a torn last line is set aside; follow-up X1), and a
    final sample still shows the same host (A15).  The stop time is taken after the monitor is reaped (X1)."""
    mon, qh = QHOST["monitor"], QHOST["qh"]
    signal.signal(signal.SIGTERM, signal.SIG_IGN)      # a late monitor signal must not kill the stop: its row still fails
    alive = mon is not None and mon.poll() is None
    if mon is not None:
        mon.terminate()
        try:
            mon.wait(timeout=30)
        except subprocess.TimeoutExpired:
            mon.kill()
            mon.wait()
    stopped = time.monotonic()                          # follow-up X1: after the monitor is reaped, so every row precedes it
    events, torn, corrupt = H.parse_monitor_rows(QHOST["file"].read_text())
    rows = [r for r in events if r.get("kind") == "sample"]             # the completed samples
    live = H.monitor_liveness([r.get("m", 0) for r in events], QHOST["started"], stopped, alive, QHOST["interval"],
                              qh["cfg"]["monitor_gap_tolerance_s"])   # every event: start-of-sample and result rows
    final = H.provenance(qh["cfg"])
    fcont = H.continuity(qh["baseline"], final, qh["cfg"])
    return {"pass": bool(rows) and all(r.get("pass") for r in rows) and live["pass"] and fcont["pass"] and not corrupt,
            "samples": len(rows), "failed": [r for r in rows if not r.get("pass")][:3], "liveness": live,
            "torn_last_line": torn, "corrupt_lines": corrupt, "final_sample": {"provenance": final, "continuity": fcont}}


def items_table(m: Path, freeze: str, workers: int) -> dict:
    """the qualification items, in order (r2: one function, so that the topology drill runs these very lambdas;
    the runner gains no drill mode)"""
    return {
        "QC01": lambda: qc_research_simple(m, "tests/test_srk_port_identity.py"),
        "QC02": lambda: qc_research_simple(m, "tests/test_srk_envelope.py"),
        "QC03": lambda: qc_research_simple(m, "tests/test_srk_fsm_truth.py"),
        "QC04": lambda: qc_research_simple(m, "tests/test_srk_assembly_twosided.py", opt=True),
        "QC05": lambda: qc05(m),
        "QC06": lambda: qc06(m),
        "QC07": lambda: qc07(m),
        "QC08": lambda: qc08(m, workers),
        "QC09": lambda: qc09(workers),
        "QC10": lambda: qc10(workers),
        "QC11": lambda: qc_formal("tests/test_p309_exactly_once.py", flags=True),
        "QC12": lambda: qc_formal("code/p309_static_check.py", flags=True),
        "QC13": lambda: qc13(freeze),
        "QC14": lambda: {**(lambda r: {"pass": r["rc"] == 0, "runs": [r]})(run(
            [PY, "-B", str(FNS / "code" / "p309_driver.py"), "rehearse", "--out", str(ATT["dir"] / "QC14_REHEARSE.json")],
            FNS)), "rehearse": json.loads((ATT["dir"] / "QC14_REHEARSE.json").read_text()) if (
            ATT["dir"] / "QC14_REHEARSE.json").exists() else None},
        "QC15": lambda: qc_formal("code/p309_self_audit.py", "QUALIFICATION"),
        "QC16": qc16,
        "QC17": qc17,
        "QC_U2": qc_u2,
        "QC_D5": qc_d5,
    }


def run_item(k: str, fn, freeze: str) -> dict:
    """run one item and write its record exclusively into the attempt (a crashed item is a recorded FAIL)"""
    t0 = time.time()
    try:
        res = fn()
    except Exception as exc:  # noqa: BLE001 - a crashed QC is a FAIL, recorded
        res = {"pass": False, "error": f"{type(exc).__name__}: {exc}"[:800]}
    res.update({"qc": k, "freeze_commit": freeze, "utc": utc(), "wall_s": round(time.time() - t0, 1)})
    xwrite(ATT["dir"] / f"{k}.json", json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    sync_ledgers()                                            # hardening H2: the gate's ledger rows are durable too
    print(f"[{'PASS' if res['pass'] else 'FAIL'}] {k} ({res['wall_s']} s)", flush=True)
    return res


def attempt_start(freeze: str, qh: dict) -> dict:
    """hardening H4: the durable start marker -- which boot, process and runner bytes began this attempt (lets an
    interrupted attempt be attributed to a reboot by boot id; nothing reads it to resume)"""
    return {"schema": "P309_ATTEMPT_START/1", "utc": utc(), "pid": os.getpid(), "freeze_commit": freeze,
            "boot_id": (Path("/proc/sys/kernel/random/boot_id").read_text().strip()
                        if Path("/proc/sys/kernel/random/boot_id").exists() else None),
            "runner_sha256": sha_file(Path(__file__)), "unit": qh.get("unit"), "mode": qh.get("mode"),
            "launch_record_sha256": hashlib.sha256(qh.get("record_bytes") or b"").hexdigest(),
            "retry_rule": "none (R4 B8; r2 P23): an interrupted attempt is preserved and never resumed"}


def host_rerun(workers: int) -> int:
    """rev. 2c A14 / delta D7: QC10 re-run on the owner-named host, before the grant commit.  Evidence goes to
    qualification/host_rerun/<host id>/ (exclusive), which the grant window admits (rev. 2c A8 as amended).
    r2 (delta review C7): only through the launcher's host-rerun mode, under the exclusion gate and Q-HOST; every
    refusal comes before the attempt directory and the HOST RERUN START line."""
    try:
        freeze = D.recorded_freeze()
    except D.Refusal as exc:
        print(f"HOST RERUN REFUSED: {exc}")
        return 2
    target = QDIR / "host_rerun" / D.G.host_id()[:16]
    if target.exists():
        print("HOST RERUN REFUSED: this host's re-run already exists (no retry; it is preserved)")
        return 2
    problems = fs_probe(QDIR)                                 # S1: this host's filesystem, before H3 and the start
    if problems:
        print("HOST RERUN REFUSED: filesystem probe (S1): " + "; ".join(problems[:5]))
        return 2
    # hardening H3: no temporary file of an interrupted write anywhere under the re-run directory, launchable ledgers,
    # and no earlier start line for this host's re-run after the freeze record
    names = sorted(p.name for p in QDIR.iterdir()) if QDIR.exists() else []
    problems = prelaunch_state(f"{HOST_START} {D.G.host_id()[:16]}", tuple(n for n in names if not n.startswith(".")))
    rr = QDIR / "host_rerun"
    problems += [f"qualification/host_rerun/{p.name} (a temporary file of an interrupted write)"
                 for p in (sorted(rr.iterdir()) if rr.exists() else []) if p.name.startswith(".")]
    if problems:
        print("HOST RERUN REFUSED: pre-launch state (H3): " + "; ".join(problems[:5]))
        return 2
    try:
        qh = qhost_preflight(("host-rerun",))                 # r2 C7: before the attempt directory and the start line
    except (H.HostError, OSError, ValueError, KeyError) as exc:
        print(f"HOST RERUN REFUSED: Q-HOST: {exc}")
        return 2
    ATT["label"] = "host_rerun"
    (QDIR / "host_rerun").mkdir(parents=True, exist_ok=True)
    ATT["dir"] = target
    os.mkdir(ATT["dir"])                                      # exclusive per host id
    E.log("code/p309_qualify.py --host-rerun", f"{HOST_START} {D.G.host_id()[:16]} (rev. 2c A14 / delta D7)",
          klass="NONTARGET_DECOY", drifts=[["1/2", "37/72"]], notes="QC10 host re-run; the declared a2_h5 decoy")
    _fsync_dir(target.parent)                                 # hardening H4 (after the start line; QC12 T14)
    sync_ledgers()                                            # hardening H2
    xwrite(ATT["dir"] / "ATTEMPT_START.json", json.dumps(attempt_start(freeze, qh), indent=1, sort_keys=True) + "\n")
    (ATT["dir"] / "evidence").mkdir()
    _fsync_dir(ATT["dir"])
    start_qhost_monitor(qh)                                   # r2 C7: continuous Q-HOST sampling (<= 60 s)
    a = decoy_stage1a("QC08_HOST", workers)
    d = decoy_stage1a("QC10_HOST", workers)
    x = json.loads(a["out"].read_text()) if a["out"].exists() else {}
    y = json.loads(d["out"].read_text()) if d["out"].exists() else {}
    q08 = json.loads(git_show(f"{QDIR.relative_to(REPO)}/attempt_1/QC08_DECOY_STAGE1A.json") or "{}")
    same = lambda u, v: (sorted(c["sha256"] for c in u.get("certificates", [])) ==  # noqa: E731
                         sorted(c["sha256"] for c in v.get("certificates", [])) and u.get("verdicts") == v.get("verdicts"))
    qhost = stop_qhost_monitor()
    _fsync_path(QHOST["file"])                                # hardening H2
    xwrite(ATT["dir"] / "QHOST_SUMMARY.json", json.dumps(qhost, indent=1, sort_keys=True, default=str) + "\n")
    sync_ledgers()                                            # hardening H2
    res = {"schema": "P309_HOST_RERUN/2", "freeze_commit": freeze, "utc": utc(), "host_id_sha256": D.G.host_id(),
           "runtime": {"python": platform.python_version(), "platform": f"{sys.platform} {platform.machine()}"},
           "runs": [a["run"], d["run"]], "qhost": {"unit": qh["unit"], "mode": qh["mode"], "pass": qhost["pass"]},
           "pass": a["run"]["rc"] == 0 and d["run"]["rc"] == 0 and same(x, y)
           and same(x, q08) and bool(x.get("certificates")) and qhost["pass"]}
    xwrite(ATT["dir"] / "QC10_HOST_RERUN.json", json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    print(f"[{'PASS' if res['pass'] else 'FAIL'}] QC10 host re-run on {D.G.host_id()[:16]}")
    return 0 if res["pass"] else 1


def git_show(rel: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{rel}"], capture_output=True, text=True).stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--host-rerun", action="store_true")
    a = ap.parse_args()
    if a.host_rerun:
        return host_rerun(a.workers)
    try:
        freeze = D.recorded_freeze()
    except D.Refusal as exc:
        print(f"QUALIFICATION REFUSED: {exc}")
        return 2
    chk = subprocess.run([PY, str(FNS / "code" / "make_freeze_manifest.py"), "--check"], capture_output=True, text=True)
    if chk.returncode != 0:
        print("QUALIFICATION REFUSED: the freeze manifest does not regenerate identically")
        return 2
    dirty = [l for l in subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--", D.NS_REL],
                                       capture_output=True, text=True).stdout.splitlines()
             if "/qualification/" not in l and "/ledger/" not in l]
    if dirty:
        print(f"QUALIFICATION REFUSED: dirty frozen tree {dirty[:3]}")
        return 2
    QDIR.mkdir(exist_ok=True)
    if any(p.name.startswith("attempt_") for p in QDIR.iterdir()) or (QDIR / "P309_QUALIFICATION.json").exists():
        print("QUALIFICATION REFUSED: an attempt already exists (R4 B8: no retry, no resumption; it is preserved; "
              "classify it read-only with the status validator)")
        return 2
    problems = fs_probe(QDIR)                                 # S1: before H3, Q-HOST, the attempt and RUN START
    if problems:
        print("QUALIFICATION REFUSED: filesystem probe (S1): " + "; ".join(problems[:5]))
        return 2
    problems = prelaunch_state(RUN_START, ())                 # hardening H3: before Q-HOST, the attempt and RUN START
    if problems:
        print("QUALIFICATION REFUSED: pre-launch state (H3): " + "; ".join(problems[:5]))
        return 2
    try:
        qh = qhost_preflight(("official", "drill"))         # r2 P10: before the attempt directory and RUN START
    except (H.HostError, OSError, ValueError, KeyError) as exc:
        print(f"QUALIFICATION REFUSED: Q-HOST: {exc}")
        return 2
    ATT["dir"] = QDIR / "attempt_1"
    os.mkdir(ATT["dir"])                                      # exclusive
    E.log("code/p309_qualify.py", f"{RUN_START} attempt_1 at the recorded freeze {freeze[:12]} (the single "
          "qualification run; R4 B8, delta-2 E6)", klass="GOVERNANCE", notes="no retry, no resumption")
    # hardening H4 (after the start line, which QC12 T14 requires right after the mkdir): the attempt directory
    # entry and the start line are made durable, then the durable start marker is written
    _fsync_dir(QDIR)
    sync_ledgers()                                            # hardening H2
    xwrite(ATT["dir"] / "ATTEMPT_START.json", json.dumps(attempt_start(freeze, qh), indent=1, sort_keys=True) + "\n")
    (ATT["dir"] / "evidence").mkdir()
    _fsync_dir(ATT["dir"])
    start_qhost_monitor(qh)                                   # r2 P10: continuous Q-HOST sampling (<= 60 s)
    m = mirror(freeze)
    items = items_table(m, freeze, a.workers)
    results = {}
    for k, fn in items.items():
        results[k] = run_item(k, fn, freeze)
    qhost = stop_qhost_monitor()
    _fsync_path(QHOST["file"])                                # hardening H2: the monitor's rows are durable
    xwrite(ATT["dir"] / "QHOST_SUMMARY.json", json.dumps(qhost, indent=1, sort_keys=True, default=str) + "\n")
    sync_ledgers()                                            # hardening H2: every ledger row precedes the marker
    gates = {("Q" + k[2:]): bool(v.get("pass")) and v.get("freeze_commit") == freeze for k, v in results.items()}
    gates["Q-HOST"] = qhost["pass"]                           # r2 P10
    summary = {"schema": "P309_QUALIFICATION/2", "freeze_commit": freeze, "attempt": ATT["dir"].name, "utc": utc(),
               "pass": len(gates) == len(items) + 1 and all(gates.values()), "gates": gates, "retry_rule": "none (R4 B8)",
               "runtime": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                           "platform": f"{sys.platform} {platform.machine()}", "host_id_sha256": D.G.host_id()},
               "files": {k: sha_file(ATT["dir"] / f"{k}.json") for k in results},
               # hardening H5: the completion marker binds every attempt file (records, decoy outputs, Q-HOST files)
               "attempt_files_sha256": {p.name: sha_file(p) for p in sorted(ATT["dir"].iterdir()) if p.is_file()},
               "qhost": {"unit": qh["unit"], "mode": qh["mode"], "baseline": qh["baseline"], "monitor": qhost},
               "statement": "no target input read; no quarantined cell evaluated; no in-band computation; "
                            "NEW Γ309 TARGET EVALUATIONS = 0"}
    xwrite(QDIR / "P309_QUALIFICATION.json", json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"pass": summary["pass"], "gates": gates}, indent=1))
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
