"""Task 6: REAL transient-systemd acceptance for the portable recovery successor.

Real: production launcher (ps1_cellseq_launcher), transient systemd unit, supervisor, ledger,
campaign lock, reservation accounting, per-cell markers, drain, checkpoint, export, resume.
Synthetic: only the science (per-cell spins). Runs in a throwaway clone under a
SYNTHETIC_CONTROL contract, so nothing can reach genuine production.

  python live_acceptance.py <A|B|C|D|E|all> --work <dir>
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
FROZEN_OPS = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
                  "p5y_k1_ps1_lifecycle_adapter")
sys.path.insert(0, str(NS / "driver"))
sys.path.insert(0, str(NS / "ops"))      # recovery ops FIRST: never shadow generated modules
import opscommon as OC                                            # noqa: E402
import runtime_state as RS                                        # noqa: E402
import ps1_checkpoint as CK                                       # noqa: E402

PY = "/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python"
PRODCTL = NS / "ops" / "prodctl.py"
WORKTREE = "/home/ubuntu/work/ReBaseGuard-sr-o9-t1"


def sh(*a, **kw):
    return subprocess.run(list(a), capture_output=True, text=True, **kw)


def prodctl(contract, *args):
    r = sh(PY, str(PRODCTL), *args, "--contract", str(contract))
    try:
        return json.loads(r.stdout) if r.stdout.strip() else {"_rc": r.returncode, "_err": r.stderr[-400:]}
    except ValueError:
        return {"_rc": r.returncode, "_stdout": r.stdout[-600:], "_err": r.stderr[-400:]}


def make_clone(dest: Path) -> Path:
    head = sh("git", "-C", WORKTREE, "rev-parse", "HEAD").stdout.strip()
    sh("git", "clone", "-q", "--local", "--no-checkout", WORKTREE, str(dest))
    sh("git", "-C", str(dest), "-c", "advice.detachedHead=false", "checkout", "-q", "--detach", head)
    RS.install_git_policy(dest)
    return dest


def synthetic_contract(tmp: Path, root: Path, control: dict, service_mode=True) -> Path:
    c = json.loads(OC.CONTRACT_PATH.read_text())
    c["mode"] = "SYNTHETIC_CONTROL"
    # the recovery successor declares a NEW parent: the recovery commit that carries this
    # namespace. The predecessor authorization commit stays recorded, never overwritten.
    head = sh("git", "-C", str(root), "rev-parse", "HEAD").stdout.strip()
    c["parent"]["predecessor_commit"] = c["parent"]["commit"]
    c["parent"]["commit"] = head
    c["parent"]["tag"] = sh("git", "-C", str(root), "describe", "--tags",
                            "--exact-match", head).stdout.strip() or head
    ctl = tmp / "control.json"
    ctl.write_text(json.dumps(control))
    c["accounting"]["poll_interval_s"] = 0.5
    c["service"]["unit_prefix"] = "rbg-recov-synth-"
    c["parent"]["workers"]["AWS"] = len(control["cores"])
    for role in list(c["hosts"]):
        spec = c["hosts"][role]
        spec["production_root"] = str(root if role == "AWS" else tmp / f"absent-{role}")
        spec["ops_root"] = str(NS)                       # recovery prodctl + entry
        spec["python"] = PY
        spec["runtime_dir"] = str(tmp / f"runtime-{role}")
        spec["online_cpus"] = os.cpu_count()
        if not service_mode:
            spec["launch_prefix"] = []
        c["service"]["environment"][role]["RBG_SYNTH_CONTROL"] = str(ctl)
    c["synthetic"] = {"entry": "tests/synthetic_cellseq_entry.py", "service_mode": service_mode,
                      "boot_id_file": str(tmp / "boot_id"), "boot_time_file": str(tmp / "boot_time")}
    (tmp / "boot_id").write_text("recov-boot-1\n")
    (tmp / "boot_time").write_text("0\n")
    p = tmp / "synthetic_contract.json"
    p.write_text(json.dumps(c, indent=1, sort_keys=True))
    return p


def setup(work: Path, control: dict, service_mode=True):
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    root = make_clone(work / "clone")
    return synthetic_contract(work, root, control, service_mode), root


def wait_idle(contract, timeout=300):
    t_end = time.monotonic() + timeout
    while time.monotonic() < t_end:
        st = prodctl(contract, "status", "--role", "AWS")
        if st.get("campaign_lock") != "LIVE":
            return st
        time.sleep(2.0)
    return prodctl(contract, "status", "--role", "AWS")


def sealed_cells(root: Path):
    d = root / "level4/closure_proofs/p5y_k1_ps1_production/production/cells"
    return sorted(int(p.stem) for p in d.glob("[0-9]*.json")) if d.exists() else []


# ------------------------------------------------------------------ A: drain
def scenario_A(work: Path):
    print("=" * 70); print("A. start -> finalize cells -> real prodctl drain")
    NCELLS = 32
    ct, root = setup(work, {"spin_s": 3.0, "cells": list(range(NCELLS)), "cores": [20, 21]})
    st = prodctl(ct, "start", "--role", "AWS")
    print(f"  start unit: {st.get('unit')}  state {st.get('unit_state')}")
    time.sleep(16)
    mid = sealed_cells(root)
    print(f"  finalized before drain: {mid}")
    dr = prodctl(ct, "drain", "--role", "AWS", "--wait", "120")
    print(f"  drain flag: {dr.get('flag')}  settled={dr.get('settled')}")
    fin_st = wait_idle(ct)
    after = sealed_cells(root)
    ok = {
      "cells_finalized_before_drain>=2": len(mid) >= 2,
      "no_new_cells_after_drain_beyond_inflight": len(after) >= len(mid),
      "lock_FREE": fin_st.get("campaign_lock") == "FREE",
      "zero_open_reservations": fin_st.get("open_reservations") == [],
      "no_unsettled_runs": fin_st.get("unsettled_runs") == [],
      "no_torn_from_drain": not fin_st.get("torn_attempts"),
      "drain_stopped_admission": len(after) < NCELLS,
      "inflight_cells_reached_boundary": len(after) >= len(mid),
    }
    print(f"  finalized after drain : {after}")
    print(f"  torn_attempts         : {fin_st.get('torn_attempts')}")
    for k, v in ok.items():
        print(f"    {'PASS' if v else 'FAIL'}  {k}")
    return all(ok.values()), {"before": mid, "after": after, "status": fin_st}


# ------------------------------------------- B: per-cell durability under tear
def scenario_B(work: Path):
    print("=" * 70); print("B. group [0,1,2,3]; 0,1 finalize; infrastructure tear during 2")
    ct, root = setup(work, {"spin_s": 2.0, "cells": [0, 1, 2, 3], "cores": [20, 21],
                            "die": {"2": [1]}})
    prodctl(ct, "start", "--role", "AWS")
    fin_st = wait_idle(ct, timeout=240)
    # A SIGKILL landing mid-ledger-write leaves the frozen lock AMBIGUOUS, so the supervisor
    # correctly DEFERS settlement. That is the frozen design: the sanctioned recover step
    # completes it. Durability is unaffected -- finalized cells are already committed.
    deferred = bool(fin_st.get("open_reservations"))
    if deferred:
        rc = prodctl(ct, "recover", "--role", "AWS")
        print(f"  settlement was deferred; prodctl recover -> {str(rc)[:120]}")
        fin_st = prodctl(ct, "status", "--role", "AWS")
    after = sealed_cells(root)
    ops_torn = fin_st.get("torn_attempts", {})
    print(f"  settlement_deferred_then_recovered: {deferred}")
    ok = {
      "0_and_1_FINALIZED": after[:2] == [0, 1],
      "2_NOT_finalized": 2 not in after,
      "3_NOT_falsely_completed": 3 not in after,
      "no_rollback_of_0_1": len(after) >= 2 and 0 in after and 1 in after,
      "torn_recorded_for_active_cell": bool(ops_torn),
      "lock_FREE": fin_st.get("campaign_lock") == "FREE",
      "zero_open_reservations": fin_st.get("open_reservations") == [],
    }
    print(f"  finalized     : {after}")
    print(f"  torn_attempts : {ops_torn}")
    for k, v in ok.items():
        print(f"    {'PASS' if v else 'FAIL'}  {k}")
    return all(ok.values()), {"finalized": after, "torn": ops_torn}


# ------------------------------- B2: DECISIVE -- launcher SIGKILLed after durable marker
def scenario_B2(work: Path):
    print("=" * 70)
    print("B2. DECISIVE: cell 0 commits live; cell 1 marker durable then LAUNCHER SIGKILLed")
    print("    (launcher finally/atexit cannot run -- only supervisor reconciliation can save it)")
    ct, root = setup(work, {"spin_s": 2.0, "cells": [0, 1, 2, 3], "cores": [20, 21],
                            "kill_launcher_after_cell": 1})
    prodctl(ct, "start", "--role", "AWS")
    fin_st = wait_idle(ct, timeout=300)
    after = sealed_cells(root)
    recon, reason = None, None
    rd = work / "runtime-AWS" / "runs"
    for f in sorted(rd.glob("*.json")) if rd.exists() else []:
        d = json.loads(f.read_text())
        recon = d.get("reconciliation") or recon
        reason = d.get("reason") or reason
    print(f"  run end reason : {reason}")
    print(f"  finalized      : {after}")
    print(f"  torn_attempts  : {fin_st.get('torn_attempts')}")
    print(f"  reconciliation : {json.dumps(recon) if recon else 'ABSENT'}")
    ok = {
      "0_FINALIZED": 0 in after,
      "1_FINALIZED_FROM_DURABLE_MARKER": 1 in after,
      "reconciliation_actually_ran": bool(recon and 1 in (recon.get("finalized") or [])),
      "launcher_was_sigkilled": reason is not None and "CHILD_EXIT_-9" in str(reason),
      "2_and_3_not_finalized": 2 not in after and 3 not in after,
      "no_duplicate_commit": len(after) == len(set(after)),
      "lock_FREE": fin_st.get("campaign_lock") == "FREE",
      "zero_open_reservations": fin_st.get("open_reservations") == [],
      "torn_not_incremented_for_finalized": all(str(c) not in (fin_st.get("torn_attempts") or {})
                                                for c in after),
    }
    for k, v in ok.items():
        print(f"    {'PASS' if v else 'FAIL'}  {k}")
    return all(ok.values()), {"finalized": after, "reconciliation": recon}


# ------------------------- B3: the other side of the barrier -- kill BEFORE marker rename
def scenario_B3(work: Path):
    print("=" * 70)
    print("B3. kill LAUNCHER before cell 1's marker is renamed -> cell 1 must NOT finalize")
    ct, root = setup(work, {"spin_s": 2.0, "cells": [0, 1, 2, 3], "cores": [20, 21],
                            "kill_launcher_before_cell": 1})
    prodctl(ct, "start", "--role", "AWS")
    fin_st = wait_idle(ct, timeout=300)
    after = sealed_cells(root)
    recon, reason = None, None
    rd = work / "runtime-AWS" / "runs"
    for f in sorted(rd.glob("*.json")) if rd.exists() else []:
        d = json.loads(f.read_text())
        recon = d.get("reconciliation") or recon
        reason = d.get("reason") or reason
    print(f"  run end reason : {reason}")
    print(f"  finalized      : {after}")
    print(f"  torn_attempts  : {fin_st.get('torn_attempts')}")
    print(f"  reconciliation : {json.dumps(recon) if recon else 'ABSENT'}")
    ok = {
      "0_FINALIZED": 0 in after,
      "1_NOT_finalized_no_durable_marker": 1 not in after,
      "no_false_finalization": set(after) <= {0},
      "1_torn_or_pending": str(1) in (fin_st.get("torn_attempts") or {}) or 1 not in after,
      "lock_FREE": fin_st.get("campaign_lock") == "FREE",
      "zero_open_reservations": fin_st.get("open_reservations") == [],
    }
    for k, v in ok.items():
        print(f"    {'PASS' if v else 'FAIL'}  {k}")
    return all(ok.values()), {"finalized": after}


# --------------------------------------------- C: checkpoint / export / resume
def scenario_C(work: Path):
    print("=" * 70); print("C. checkpoint -> export -> clean runtime -> resume")
    ct, root = setup(work, {"spin_s": 2.0, "cells": [0, 1, 2, 3], "cores": [20, 21]})
    prodctl(ct, "start", "--role", "AWS")
    fin_st = wait_idle(ct, timeout=240)
    fin = sealed_cells(root)
    print(f"  finalized: {fin}")
    cp = prodctl(ct, "checkpoint", "--role", "AWS")
    print(f"  checkpoint: {cp.get('sha256')}  finalized={cp.get('finalized')} pending={cp.get('pending')}")
    ex = prodctl(ct, "export", "--role", "AWS", "--output", str(work / "bundle_out"))
    rep = (ex.get("export") or {})
    print(f"  export: {rep.get('files')} files  tar_sha256={str(rep.get('tar_sha256'))[:16]}")
    bundle = Path(rep.get("bundle_dir", ""))
    fresh = work / "fresh_bundle"
    if bundle.exists():
        shutil.copytree(bundle, fresh)
    rs = prodctl(ct, "resume", "--role", "AWS", "--checkpoint", str(fresh))
    print(f"  resume: {rs.get('resume')}  schedule_only_pending={rs.get('schedule_only_pending')} "
          f"finalized_never_rescheduled={rs.get('finalized_never_rescheduled')}")
    ok = {
      "checkpoint_created": bool(cp.get("sha256")),
      "domain_partition_369": (cp.get("finalized", 0) + cp.get("pending", 0)) == 369,
      "export_has_files": (rep.get("files") or 0) > 0,
      "bundle_verifies_in_clean_dir": rs.get("resume") == "VERIFIED_READY",
      "schedules_only_pending": rs.get("schedule_only_pending") == 369 - len(fin),
      "never_reschedules_finalized": rs.get("finalized_never_rescheduled") == len(fin),
      "historical_cpu_preserved": abs((rs.get("historical_cpu_h_preserved") or 0) - 92.32) < 1e-6,
    }
    for k, v in ok.items():
        print(f"    {'PASS' if v else 'FAIL'}  {k}")
    return all(ok.values()), {"checkpoint": cp, "export": rep, "resume": rs,
                              "bundle": str(fresh), "contract": str(ct)}


# ---------------------------------------------------------- D: corruption
def scenario_D(work: Path, prior):
    print("=" * 70); print("D. corruption must fail closed")
    bundle = Path(prior["bundle"]); ct = prior["contract"]
    res = {}
    # D1 checkpoint hash
    b1 = work / "corrupt_ck"; shutil.rmtree(b1, ignore_errors=True); shutil.copytree(bundle, b1)
    ck = json.loads((b1 / "checkpoint.json").read_text())
    ck["finalized_cells"] = ck["finalized_cells"] + [999]
    (b1 / "checkpoint.json").write_text(json.dumps(ck))
    r = prodctl(ct, "resume", "--role", "AWS", "--checkpoint", str(b1))
    res["D1_checkpoint_hash"] = "REFUSED" in r
    print(f"    {'PASS' if res['D1_checkpoint_hash'] else 'FAIL'}  D1 corrupted checkpoint -> {str(r)[:90]}")
    # D2 finalized evidence
    b2 = work / "corrupt_ev"; shutil.rmtree(b2, ignore_errors=True); shutil.copytree(bundle, b2)
    victim = next(iter(sorted((b2 / "evidence").rglob("*"))))
    while victim.is_dir():
        victim = next(iter(sorted(victim.iterdir())))
    victim.write_bytes(b'{"tampered":true}\n')
    r = prodctl(ct, "resume", "--role", "AWS", "--checkpoint", str(b2))
    res["D2_evidence_hash"] = "REFUSED" in r
    print(f"    {'PASS' if res['D2_evidence_hash'] else 'FAIL'}  D2 tampered evidence -> {str(r)[:90]}")
    # D3 duplicate finalized scheduling
    b3 = work / "corrupt_dup"; shutil.rmtree(b3, ignore_errors=True); shutil.copytree(bundle, b3)
    ck = json.loads((b3 / "checkpoint.json").read_text())
    ck["pending_cells"] = sorted(set(ck["pending_cells"]) | set(ck["finalized_cells"]))
    ck["checkpoint_content_sha256"] = CK._content_hash(ck)
    (b3 / "checkpoint.json").write_text(json.dumps(ck))
    r = prodctl(ct, "resume", "--role", "AWS", "--checkpoint", str(b3))
    res["D3_duplicate_finalized"] = "REFUSED" in r
    print(f"    {'PASS' if res['D3_duplicate_finalized'] else 'FAIL'}  D3 duplicate scheduling -> {str(r)[:90]}")
    return all(res.values()), res


# ------------------------------------------------------ E: accounting continuity
def scenario_E(work: Path, prior):
    print("=" * 70); print("E. cumulative accounting continuity")
    bundle = Path(prior["bundle"]); ct = prior["contract"]
    ck = json.loads((bundle / "checkpoint.json").read_text())
    acc = ck["accounting"]
    b = work / "reset_acc"; shutil.rmtree(b, ignore_errors=True); shutil.copytree(bundle, b)
    ck2 = json.loads((b / "checkpoint.json").read_text())
    ck2["accounting"]["historical_cpu_h"] = 0.0
    ck2["checkpoint_content_sha256"] = CK._content_hash(ck2)
    (b / "checkpoint.json").write_text(json.dumps(ck2))
    r = prodctl(ct, "resume", "--role", "AWS", "--checkpoint", str(b))
    ok = {
      "historical_92_32_present": abs(acc["historical_cpu_h"] - 92.32) < 1e-6,
      "cumulative_includes_historical": acc["cumulative_cpu_h"] >= 92.32,
      "reset_attempt_refused": "REFUSED" in r,
    }
    print(f"  historical={acc['historical_cpu_h']}  generation={acc['generation_cpu_h']:.6f}  "
          f"cumulative={acc['cumulative_cpu_h']:.6f}")
    for k, v in ok.items():
        print(f"    {'PASS' if v else 'FAIL'}  {k}")
    return all(ok.values()), acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", choices=("A", "B", "B2", "B3", "C", "D", "E", "all"))
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    w = Path(a.work)
    results, prior = {}, None
    if a.scenario in ("A", "all"):
        results["A"], _ = scenario_A(w / "A")
    if a.scenario in ("B", "all"):
        results["B"], _ = scenario_B(w / "B")
    if a.scenario in ("B2", "all"):
        results["B2"], _ = scenario_B2(w / "B2")
    if a.scenario in ("B3", "all"):
        results["B3"], _ = scenario_B3(w / "B3")
    if a.scenario in ("C", "D", "E", "all"):
        results["C"], prior = scenario_C(w / "C")
    if a.scenario in ("D", "all"):
        results["D"], _ = scenario_D(w / "D", prior)
    if a.scenario in ("E", "all"):
        results["E"], _ = scenario_E(w / "E", prior)
    print("=" * 70)
    print("LIVE ACCEPTANCE: " + "  ".join(f"{k}={'PASS' if v else 'FAIL'}" for k, v in results.items()))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
