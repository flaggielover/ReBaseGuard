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
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import random
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

QDIR = FNS / "qualification"
SCRATCH = Path("/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/qualification")
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


def xwrite(path: Path, text: str) -> None:
    """write a new file exclusively (never overwrite)"""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        os.write(fd, text.encode())
    finally:
        os.close(fd)


def run(cmd: list, cwd: Path, timeout: int = 6 * 3600, env_extra=None) -> dict:
    env = dict(os.environ)
    env["P309_EVIDENCE_DIR"] = str(ATT["dir"] / "evidence")
    env.update(env_extra or {})
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
    arch = subprocess.run(["git", "-C", str(REPO), "archive", freeze_commit, *MIRROR_PATHS], capture_output=True,
                          check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(m)], input=arch, check=True)
    return m


def research_test(m: Path, rel: str, *args, opt: bool = False) -> dict:
    cmd = [PY] + (["-O"] if opt else []) + [str(m / RMIR / rel), *args]
    E.log(f"{RMIR}/{rel} (in the archive mirror)", f"{ATT['label']}: research test {rel} {' '.join(args)}",
          klass="NONTARGET_DECOY", notes="read-only export of the frozen commit; outputs stay in the mirror")
    return run(cmd, m / RMIR)


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
    batteries = [research_test(m, t) for t in ("tests/test_srk_gate.py", "tests/test_srk_wrec_refusal.py",
                                               "tests/test_srk_cert_mutants.py", "tests/e2e_cell_family.py")]
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


def qc_formal(cmd_rel: str, *args, flags: bool = False) -> dict:
    r = run([PY, *(["-I", "-S", "-B"] if flags else []), str(FNS / cmd_rel), *args], FNS, timeout=12 * 3600)
    return {"pass": r["rc"] == 0, "runs": [r]}


def qc13(freeze: str) -> dict:
    g = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()  # noqa
    frozen_now = [g("rev-parse", f"HEAD:{D.NS_REL}/{d}") for d in D.FROZEN_DIRS]
    frozen_then = [g("rev-parse", f"{freeze}:{D.NS_REL}/{d}") for d in D.FROZEN_DIRS]
    refs = g("for-each-ref", "--format=%(refname)").splitlines()
    try:
        recorded = D.recorded_freeze()
    except D.Refusal as exc:
        recorded = f"refused: {exc}"
    ok = {"freeze_record_valid_and_names_this_freeze": recorded == freeze,
          "freeze_is_last_frozen_change": D.freeze_commit() == freeze,
          "frozen_dirs_unchanged_since_freeze": frozen_now == frozen_then,
          "r5_blob_unchanged": g("rev-parse", "HEAD:level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/"
                                            "K5_COVERAGE_MAP_R5.json") == "f978eeb6b41188eabaf3c6d590c9178d711f1ce6",
          "no_exactly_once_ref": not [r for r in refs if r.startswith(D.G._PROD_NAMESPACE)],
          "research_namespace_unchanged": not g("diff", "--name-only", "eb9a9c22b093f938e1bf13e0b30512608c58c370",
                                                "HEAD", "--", D.RNS_REL),
          "qualification_after_freeze": subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", freeze,
                                                        "HEAD"]).returncode == 0}
    ok["no_r6"] = not any("COVERAGE_MAP_R6" in p.upper() for p in g("ls-tree", "-r", "--name-only", "HEAD").splitlines())
    ok["single_qualification_run_since_the_freeze_record"] = single_run_since_freeze()
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
    """owner D5: the exception is limited to the two ratified sites -- the control suite, and the scanner's
    ref-mutation whitelist current (no unlisted, no stale entry)"""
    parts = [qc_formal("tests/test_p309_d5_exception.py", flags=True)]
    pins = run([PY, str(FNS / "code" / "p309_scan_pins.py"), "--list"], FNS)
    bad = [l for l in pins["stdout_tail"].splitlines() if "NOT LISTED" in l or "STALE" in l or "remove the entry" in l]
    parts.append({"pass": pins["rc"] == 0 and not bad, "runs": [pins], "not_current": bad})
    return {"pass": all(x["pass"] for x in parts), "parts": parts}


def host_rerun(workers: int) -> int:
    """rev. 2c A14 / delta D7: QC10 re-run on the owner-named host, before the grant commit.  Evidence goes to
    qualification/host_rerun/<host id>/ (exclusive), which the grant window admits (rev. 2c A8 as amended)."""
    freeze = D.recorded_freeze()
    base = QDIR / "host_rerun"
    base.mkdir(parents=True, exist_ok=True)
    ATT["dir"] = base / D.G.host_id()[:16]
    os.mkdir(ATT["dir"])                                      # exclusive per host id
    E.log("code/p309_qualify.py --host-rerun", f"{HOST_START} {D.G.host_id()[:16]} (rev. 2c A14 / delta D7)",
          klass="NONTARGET_DECOY", drifts=[["1/2", "37/72"]], notes="QC10 host re-run; the declared a2_h5 decoy")
    (ATT["dir"] / "evidence").mkdir()
    a = decoy_stage1a("QC08_HOST", workers)
    d = decoy_stage1a("QC10_HOST", workers)
    x = json.loads(a["out"].read_text()) if a["out"].exists() else {}
    y = json.loads(d["out"].read_text()) if d["out"].exists() else {}
    q08 = json.loads(git_show(f"{QDIR.relative_to(REPO)}/attempt_1/QC08_DECOY_STAGE1A.json") or "{}")
    same = lambda u, v: (sorted(c["sha256"] for c in u.get("certificates", [])) ==  # noqa: E731
                         sorted(c["sha256"] for c in v.get("certificates", [])) and u.get("verdicts") == v.get("verdicts"))
    res = {"schema": "P309_HOST_RERUN/1", "freeze_commit": freeze, "utc": utc(), "host_id_sha256": D.G.host_id(),
           "runtime": {"python": platform.python_version(), "platform": f"{sys.platform} {platform.machine()}"},
           "runs": [a["run"], d["run"]], "pass": a["run"]["rc"] == 0 and d["run"]["rc"] == 0 and same(x, y)
           and same(x, q08) and bool(x.get("certificates"))}
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
        print("QUALIFICATION REFUSED: an attempt already exists (R4 B8: no retry, no resumption; it is preserved)")
        return 2
    ATT["dir"] = QDIR / "attempt_1"
    os.mkdir(ATT["dir"])                                      # exclusive
    E.log("code/p309_qualify.py", f"{RUN_START} attempt_1 at the recorded freeze {freeze[:12]} (the single "
          "qualification run; R4 B8, delta-2 E6)", klass="GOVERNANCE", notes="no retry, no resumption")
    (ATT["dir"] / "evidence").mkdir()
    m = mirror(freeze)
    items = {
        "QC01": lambda: qc_research_simple(m, "tests/test_srk_port_identity.py"),
        "QC02": lambda: qc_research_simple(m, "tests/test_srk_envelope.py"),
        "QC03": lambda: qc_research_simple(m, "tests/test_srk_fsm_truth.py"),
        "QC04": lambda: qc_research_simple(m, "tests/test_srk_assembly_twosided.py", opt=True),
        "QC05": lambda: qc05(m),
        "QC06": lambda: qc06(m),
        "QC07": lambda: qc07(m),
        "QC08": lambda: qc08(m, a.workers),
        "QC09": lambda: qc09(a.workers),
        "QC10": lambda: qc10(a.workers),
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
    results = {}
    for k, fn in items.items():
        t0 = time.time()
        try:
            res = fn()
        except Exception as exc:  # noqa: BLE001 - a crashed QC is a FAIL, recorded
            res = {"pass": False, "error": f"{type(exc).__name__}: {exc}"[:800]}
        res.update({"qc": k, "freeze_commit": freeze, "utc": utc(), "wall_s": round(time.time() - t0, 1)})
        xwrite(ATT["dir"] / f"{k}.json", json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
        results[k] = res
        print(f"[{'PASS' if res['pass'] else 'FAIL'}] {k} ({res['wall_s']} s)", flush=True)
    gates = {("Q" + k[2:]): bool(v.get("pass")) and v.get("freeze_commit") == freeze for k, v in results.items()}
    summary = {"schema": "P309_QUALIFICATION/2", "freeze_commit": freeze, "attempt": ATT["dir"].name, "utc": utc(),
               "pass": len(gates) == len(items) and all(gates.values()), "gates": gates, "retry_rule": "none (R4 B8)",
               "runtime": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                           "platform": f"{sys.platform} {platform.machine()}", "host_id_sha256": D.G.host_id()},
               "files": {k: sha_file(ATT["dir"] / f"{k}.json") for k in results},
               "statement": "no target input read; no quarantined cell evaluated; no in-band computation; "
                            "NEW Γ309 TARGET EVALUATIONS = 0"}
    xwrite(QDIR / "P309_QUALIFICATION.json", json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"pass": summary["pass"], "gates": gates}, indent=1))
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
