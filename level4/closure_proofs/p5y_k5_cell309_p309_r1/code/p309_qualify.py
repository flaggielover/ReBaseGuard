"""QC01-QC17 and QC-U2 of the P309 formal campaign, run exactly as frozen (package rev. 2b section B, rev. 2c).

  python3 code/p309_qualify.py [--only QC08,QC10] [--workers 4]

Writes qualification/QCxx.json per item and qualification/P309_QUALIFICATION.json (pass iff every gate Q01-Q17 and
Q-U2 passes; no gate may be waived).  Every formal tool is pointed at qualification/ through P309_EVIDENCE_DIR, so the
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
                "level4/closure_proofs/p5y_k5_tail_overnight_research/validation"]
RMIR = "level4/closure_proofs/p5y_k5_cell309_research_r1"
PY = sys.executable


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cmd: list, cwd: Path, timeout: int = 6 * 3600, env_extra=None) -> dict:
    env = dict(os.environ)
    env["P309_EVIDENCE_DIR"] = str(QDIR / "evidence")
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
    E.log(f"{RMIR}/{rel} (in the archive mirror)", f"qualification: research test {rel} {' '.join(args)}",
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
    out = QDIR / f"{tag}_DECOY_STAGE1A.json"
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
        f = QDIR / f"QC09_DECOY_STAGE1B_{k}.json"
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
    a = json.loads((QDIR / "QC08_DECOY_STAGE1A.json").read_text())
    b = json.loads(d["out"].read_text()) if d["out"].exists() else {}
    sa = sorted(c["sha256"] for c in a.get("certificates", []))
    sb = sorted(c["sha256"] for c in b.get("certificates", []))
    same = sa == sb and a.get("verdicts") == b.get("verdicts") and a.get("gate") == b.get("gate")
    return {"pass": d["run"]["rc"] == 0 and same and len(sa) > 0, "runs": [d["run"]], "certificates": len(sa),
            "byte_identical": same, "interpreter": platform.python_version(),
            "platform": f"{sys.platform} {platform.machine()}", "host_id_sha256": D.G.host_id(),
            "note": "QC08 and QC10 both run on this host (the proposed execution host, rev. 2c A14)"}


def qc_formal(cmd_rel: str, *args) -> dict:
    r = run([PY, str(FNS / cmd_rel), *args], FNS, timeout=12 * 3600)
    return {"pass": r["rc"] == 0, "runs": [r]}


def qc13(freeze: str) -> dict:
    g = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()  # noqa
    frozen_now = [g("rev-parse", f"HEAD:{D.NS_REL}/{d}") for d in D.FROZEN_DIRS]
    frozen_then = [g("rev-parse", f"{freeze}:{D.NS_REL}/{d}") for d in D.FROZEN_DIRS]
    refs = g("for-each-ref", "--format=%(refname)").splitlines()
    ok = {"freeze_is_last_frozen_change": D.freeze_commit() == freeze,
          "frozen_dirs_unchanged_since_freeze": frozen_now == frozen_then,
          "r5_blob_unchanged": g("rev-parse", "HEAD:level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/"
                                            "K5_COVERAGE_MAP_R5.json") == "f978eeb6b41188eabaf3c6d590c9178d711f1ce6",
          "no_exactly_once_ref": not [r for r in refs if r.startswith(D.G._PROD_NAMESPACE)],
          "research_namespace_unchanged": not g("diff", "--name-only", "eb9a9c22b093f938e1bf13e0b30512608c58c370",
                                                "HEAD", "--", D.RNS_REL),
          "qualification_after_freeze": subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", freeze,
                                                        "HEAD"]).returncode == 0}
    ok["no_r6"] = not any("COVERAGE_MAP_R6" in p.upper() for p in g("ls-tree", "-r", "--name-only", "HEAD").splitlines())
    return {"pass": all(ok.values()), "checks": ok}


def qc16() -> dict:
    parts = [qc_formal("verify/run_verify_all_scoped.py", "--jobs", "3", "--unit-tests", "--out",
                       str(QDIR / "evidence" / "VERIFY_RESULTS_SCOPED.json")),
             qc_formal("tests/test_verify_scoped.py"), qc_formal("tests/test_p309_guard.py"),
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    freeze = D.freeze_commit()
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
    (QDIR / "evidence").mkdir(exist_ok=True)
    only = set(a.only.split(",")) if a.only else None
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
        "QC11": lambda: qc_formal("tests/test_p309_exactly_once.py"),
        "QC12": lambda: qc_formal("code/p309_static_check.py"),
        "QC13": lambda: qc13(freeze),
        "QC14": lambda: {**(lambda r: {"pass": r["rc"] == 0, "runs": [r]})(run(
            [PY, "-B", str(FNS / "code" / "p309_driver.py"), "rehearse", "--out", str(QDIR / "QC14_REHEARSE.json")],
            FNS)), "rehearse": json.loads((QDIR / "QC14_REHEARSE.json").read_text()) if (
            QDIR / "QC14_REHEARSE.json").exists() else None},
        "QC15": lambda: qc_formal("code/p309_self_audit.py", "QUALIFICATION"),
        "QC16": qc16,
        "QC17": qc17,
        "QC_U2": qc_u2,
    }
    for k, fn in items.items():
        if only and k not in only:
            continue
        t0 = time.time()
        try:
            res = fn()
        except Exception as exc:  # noqa: BLE001 - a crashed QC is a FAIL, recorded
            res = {"pass": False, "error": f"{type(exc).__name__}: {exc}"[:800]}
        res.update({"qc": k, "freeze_commit": freeze, "utc": utc(), "wall_s": round(time.time() - t0, 1)})
        (QDIR / f"{k}.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
        print(f"[{'PASS' if res['pass'] else 'FAIL'}] {k} ({res['wall_s']} s)", flush=True)
    results = {k: json.loads((QDIR / f"{k}.json").read_text()) for k in items if (QDIR / f"{k}.json").exists()}
    gates = {("Q" + k[2:]): bool(v.get("pass")) and v.get("freeze_commit") == freeze for k, v in results.items()}
    summary = {"schema": "P309_QUALIFICATION/1", "freeze_commit": freeze, "utc": utc(),
               "pass": len(gates) == len(items) and all(gates.values()), "gates": gates,
               "runtime": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                           "platform": f"{sys.platform} {platform.machine()}", "host_id_sha256": D.G.host_id()},
               "files": {k: sha_file(QDIR / f"{k}.json") for k in results},
               "statement": "no target input read; no quarantined cell evaluated; no in-band computation; "
                            "NEW Γ309 TARGET EVALUATIONS = 0"}
    (QDIR / "P309_QUALIFICATION.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"pass": summary["pass"], "gates": gates}, indent=1))
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
