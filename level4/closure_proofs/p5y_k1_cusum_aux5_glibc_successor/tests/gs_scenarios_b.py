"""Synthetic acceptance scenarios, part B: crash recovery, duplicates, qualification firewall, composite audit and K4
attestation, launch gating, isolation, process scan. NON-RESULT-BEARING."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

from gs_fixtures import (GS, NS, GSCampaign, PredFixture, PS, SP, attempts, check, composite, count, expect_any,
                         expect_refusal, full_composite, real_checkpoint, refused_with, scenario)
import glibc_successor as G
import gs_authorization as GA
import gs_composite as GC
import gs_entry as E
import gs_host as H
import prod_ledger as L
import prov_ledger as PL
from prod_common import Refusal, atomic_write_json, canonical, sha256_bytes, sha256_file
from prod_sealer import verify_record
from prov_envelope import envelope_rel, verify_pair


def owner_pid(c) -> int:
    return json.loads((c.root / "campaign.owner.json").read_text())["pid"]


@scenario("crash before seal -> recover safely", "keeper evidence charges the lost attempt")
def b01_crash_before_seal(scratch):
    c = GSCampaign(scratch, "b01", cells=[128, 129], cores=[0], plan={"128": ["hang", "ok"]})
    p = c.start(keep=True)
    c.wait_for(lambda s: attempts(s, cell=128, status="RUNNING"), what="cell 128 running")
    os.kill(owner_pid(c), signal.SIGKILL)
    c.finish(p)
    c.run_complete()
    st = c.state()
    (_t, torn), (_s, sealed) = attempts(st, cell=128)
    check(torn["status"] == "TORN" and torn["charge_evidence"] == "REAPER_RUSAGE" and sealed["status"] == "SEALED",
          f"orphan reconciled and retried: {torn['status']} {torn['charge_evidence']}")
    rep = c.audit()
    check(rep["INTEGRITY_READY_FOR_ADJUDICATION"], f"audit {rep['issues']}")
    return {"torn_charge_usec": torn["charge_usec"]}


@scenario("crash after scientific record but before provenance envelope -> reconcile safely")
def b02_crash_after_record_before_envelope(scratch):
    c = GSCampaign(scratch, "b02", cells=[128, 129], cores=[0])
    script = (f"import json, os, sys\nsys.path.insert(0, {str(NS / 'code')!r})\nimport gs_schema\nimport prod_supervisor as PS\n"
              "import gs_supervisor as GSV\nfrom gs_spec import synthetic_spec\n"
              f"cfg = json.load(open({c.cfg['config_path']!r}))\nspec = synthetic_spec(cfg)\n"
              "class Crash(GSV.SuccessorSupervisor):\n"
              "    def _finalize(self, led, aid, status, ru):\n"
              "        PS.Supervisor._finalize(self, led, aid, status, ru)\n"
              "        if led.state['attempts'][aid]['status'] == 'SEALED':\n            os._exit(99)\n"
              "raise SystemExit(Crash(spec, authz_loader=lambda: GSV.synthetic_successor_authz(spec, cfg)).run())\n")
    r = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True, timeout=300)
    check(r.returncode == 99, f"crash harness exit {r.returncode}: {r.stderr[-300:]}")
    unbound = PL.unbound_sealed(c.state())
    check(len(unbound) == 1, f"one sealed-but-unbound attempt: {unbound}")
    check(not c.audit()["INTEGRITY_READY_FOR_ADJUDICATION"], "an unbound seal is not a production result")
    c.run_complete()
    check(c.audit()["INTEGRITY_READY_FOR_ADJUDICATION"], "recovered binding verifies")
    w = GSCampaign(scratch, "b02_write_then_die", cells=[128, 129], cores=[0], plan={"128": ["write_then_hang"]})
    p = w.start(keep=True)
    st = w.wait_for(lambda s: attempts(s, cell=128, status="RUNNING"), what="cell 128 running")
    record = w.root / attempts(st, cell=128)[0][1]["record"]
    deadline = time.monotonic() + 60
    while not record.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    os.kill(owner_pid(w), signal.SIGKILL)
    w.finish(p)
    check(w.run(keep=True)[0] == PS.EXIT_COMPLETE, "resume after supervisor death")
    st2, entries = w.view()
    (aid, a), = attempts(st2, cell=128, status="SEALED")
    env = json.loads((w.root / a["provenance"]["envelope"]).read_text())
    check(a["seal"]["recovered"] is True and env["ledger"]["seal"]["event"] == "RECONCILED_SEALED"
          and env["cpu_accounting"]["charge_evidence"] == "REAPER_RUSAGE", "recovered seal carries a valid envelope")
    verify_pair(spec=w.spec, authz=w.authz(), st=st2, entries=entries, record_path=w.root / a["record"],
                envelope_path=w.root / a["provenance"]["envelope"])
    return {"unbound_after_crash": unbound, "recovered_seal": aid}


@scenario("duplicate seal -> FAIL", "duplicate launch cannot duplicate results")
def b03_duplicate_seal(scratch):
    c = GSCampaign(scratch, "b03", cells=list(range(128, 134)), cores=[0, 2], plan={str(i): ["slow"] for i in range(128, 134)},
                   slow_s=1.0)
    p = c.start(keep=True)
    c.wait_for(lambda s: attempts(s, status="RUNNING"), what="first supervisor running")
    code_b, out_b = c.run(keep=False)
    check(code_b == PS.EXIT_REFUSED and refused_with(out_b, "ANOTHER_SUPERVISOR_LIVE"), f"second launch exit {code_b}")
    check(c.finish(p)[0] == PS.EXIT_COMPLETE, "first supervisor completes")
    st = c.state()
    check(len(st["attempts"]) == 6 and count(st, "SEALED") == 6, "one attempt per cell")
    forged = copy.deepcopy(st)
    aid, a = attempts(forged, cell=128)[0]
    forged["attempts"]["A99999-C0128"] = copy.deepcopy(a)
    forged["committed_usec"]["science"] += a["charge_usec"]
    expect_refusal("DUPLICATE_SEALED_CELL", L.validate_state, forged, c.spec)
    expect_refusal("DUPLICATE_ENVELOPE", PL.op_bind_provenance, copy.deepcopy(st), aid, envelope_rel(aid, 128), "5" * 64)
    reopen = copy.deepcopy(st)
    reopen["disposition"] = "OPEN"
    expect_refusal("DUPLICATE_CELL", L.op_reserve, reopen, c.spec, 128, 4, "T")
    return {"second_launch": "ANOTHER_SUPERVISOR_LIVE", "forged": "DUPLICATE_SEALED_CELL"}


@scenario("duplicate old/new cell -> FAIL", "old/new disjointness", "union exactly 0-325")
def b04_duplicate_old_new_cell(scratch):
    pred = PredFixture(scratch, "b04_pred", sealed=3, universe=8)
    pred.make_terminal()
    tol = pred.tolerance()
    rogue = PredFixture(scratch, "b04_rogue", sealed=10 ** 6, universe=0, cells=[2, 128], cores=[0])
    check(rogue.run(keep=True)[0] == PS.EXIT_COMPLETE, "rogue predecessor-style ledger over an old and a new cell")
    rep = GC.composite_audit(pred_spec=pred.spec, pred_authz=pred.authz(), succ_spec=rogue.spec, succ_authz=rogue.authz(),
                             tolerance=tol, qualification_shas=rogue.spec.qualification_record_sha256,
                             successor_ledger_exists=True)
    check(rep["state"] == "REFUSED" and any(p.startswith("PARTITION_OVERLAP") for p in rep["problems"])
          and "SUCCESSOR_UNIVERSE_CONTAINS_A_CARRYOVER_CELL" in rep["problems"] and not rep["K4_READY"], f"{rep['problems']}")
    check(G.check_partition(range(128), range(127, 326)) and G.check_partition(range(128), range(129, 326)), "partition rule")
    expect_refusal("ATTESTATION_REFUSED", GC.build_composite_attestation, rep, successor_checkpoint_sha256="x",
                   predecessor_checkpoint_sha256="y")
    return {"problems": rep["problems"]}


@scenario("qualification record reuse -> FAIL", "Q6 records are never production")
def b05_qualification_reuse(scratch):
    cp, sha = real_checkpoint()
    spec = SP.spec_from_checkpoint(cp, sha)
    d = scratch / "b05"
    d.mkdir()
    out = {}
    for label, src in (("qualification_318A", GS.AUX5_NS / "evidence/qualification_r1/c318_A/aux5_CUSUM_318_256.json"),
                       ("q6_318A", GS.NS / "evidence/requalification_r1/qualification_r1/c318_A/aux5_CUSUM_318_256.json")):
        dst = d / label / "aux5_CUSUM_318_256.json"
        dst.parent.mkdir()
        shutil.copyfile(src, dst)
        expect_refusal("QUALIFICATION_RECORD_REUSE", verify_record, dst, cell=318, spec=spec)
        out[label] = "QUALIFICATION_RECORD_REUSE"
    pred = PredFixture(scratch, "b05_pred", sealed=2, universe=6)
    pred.make_terminal()
    tol = pred.tolerance()
    succ = GSCampaign(scratch, "b05_succ", cells=[128, 129], cores=[0])
    succ.run_complete()
    sealed_sha = attempts(succ.state(), cell=128, status="SEALED")[0][1]["seal"]["record_sha256"]
    rep = composite(pred, succ, tol, quals=set(succ.spec.qualification_record_sha256) | {sealed_sha})
    check(rep["state"] == "REFUSED" and any(p.startswith("QUALIFICATION_RECORD_REUSE") for p in rep["problems"]), rep["problems"])
    check(cp["qualification_firewall"]["record_file_sha256"].keys() >= {"318A", "Q6_318A"}, "firewall binds both sets")
    return out | {"composite": "QUALIFICATION_RECORD_REUSE"}


@scenario("incomplete composite -> not K4-ready")
def b06_incomplete_composite(scratch):
    pred = PredFixture(scratch, "b06_pred", sealed=3, universe=8)
    pred.make_terminal()
    tol = pred.tolerance()
    succ = GSCampaign(scratch, "b06_succ", cells=[128, 129], cores=[0])
    none_yet = composite(pred, succ, tol)
    check(none_yet["state"] == "INCOMPLETE" and not none_yet["successor_ledger_exists"], f"no successor ledger: {none_yet['state']}")
    succ.run_complete()
    rep = composite(pred, succ, tol)
    check(rep["state"] == "INCOMPLETE" and not rep["K4_READY"] and not rep["union_complete"] and not rep["problems"], f"{rep}")
    expect_refusal("ATTESTATION_REFUSED", GC.build_composite_attestation, rep, successor_checkpoint_sha256="x",
                   predecessor_checkpoint_sha256="y")
    expect_refusal("EXPORT_REFUSED", GC.export_composite, rep, pred_root=pred.root, succ_root=succ.root, out_dir=scratch / "b06_x")
    return {"state": rep["state"], "old": rep["old_cells_verified"], "new": rep["new_cells_verified"]}


@scenario("exact complete synthetic composite -> PASS", "K4 composite attestation", "both provenance halves disclosed",
          "frozen K4 integrity gate accepts the composite attestation (assembly not run)")
def b07_complete_composite_and_k4_gate(scratch):
    pred, tol, succ, before = full_composite(scratch)
    check(before["issues"] == ["D_unsettled_supervisor_runs"] and before["composite"] == "INCOMPLETE"
          and not before["problems"], f"a COMPLETE successor before `gs_entry.py settle` is never K4-ready: {before}")
    check(before["settle"]["state"] == "SETTLED" and before["settle"]["disposition"] == "COMPLETE"
          and not before["settle"]["unsettled_after"], f"sanctioned settlement {before['settle']}")
    audit = succ.audit()
    check(audit["INTEGRITY_READY_FOR_ADJUDICATION"] and not audit["issues"] and len(audit["pairs"]) == 198,
          f"frozen successor integrity audit after settlement: {sorted(audit['issues'])}")
    rep = composite(pred, succ, tol)
    check(rep["state"] == "COMPLETE" and rep["K4_READY"] and rep["old_cells_verified"] == 128
          and rep["new_cells_verified"] == 198 and not rep["problems"], f"{rep['state']} {rep['problems']}")
    kw = {"successor_checkpoint_sha256": succ.spec.checkpoint_sha256, "predecessor_checkpoint_sha256": pred.spec.checkpoint_sha256}
    att = GC.build_composite_attestation(rep, **kw)
    GC.verify_composite_attestation(att, rep, **kw)
    pp = att["production_provenance"]
    check(att["cells_verified"] == 326 and att["all_scientific_hashes_verified"] is True
          and att["producer_checkpoint_sha256"] == succ.spec.checkpoint_sha256
          and pp["successor_checkpoint_binds_predecessor_checkpoint"] == pred.spec.checkpoint_sha256
          and pp["halves"]["predecessor"]["cells"] == [0, 127] and pp["halves"]["successor"]["cells"] == [128, 325],
          "attestation fields and disclosure")
    tampered = copy.deepcopy(att)
    tampered["production_provenance"]["halves"]["predecessor"]["pairs"].pop("0")
    expect_refusal("ATTESTATION_REFUSED", GC.verify_composite_attestation, tampered, rep, **kw)
    manifest = GC.export_composite(rep, pred_root=pred.root, succ_root=succ.root, out_dir=scratch / "b07_export")
    records = [json.loads(p.read_text()) for p in sorted((scratch / "b07_export/k4_records").glob("*.json"))]
    check(manifest["cells"] == 326 and len(records) == 326, "exported exactly one record per verified pair")
    cp, _sha = real_checkpoint()
    path = GS.CLOSURE / "p5y_k2k5_postk1_audit/code/k4_assembly.py"
    check(sha256_file(path) == cp["k4"]["k4_assembly_sha256"], "frozen k4_assembly.py")
    ms = importlib.util.spec_from_file_location("k4_assembly_frozen", path)
    k4 = importlib.util.module_from_spec(ms)
    ms.loader.exec_module(k4)
    att_path = scratch / "b07_attestation.json"
    atomic_write_json(att_path, att)
    k4.check_cusum_attestation(att_path, records)                   # integrity gate only; assemble() is never called
    short = scratch / "b07_short.json"
    atomic_write_json(short, {**att, "cells_verified": 325})
    try:
        k4.check_cusum_attestation(short, records)
        raise AssertionError("K4 accepted an incomplete attestation")
    except k4.AssemblyRefusal:
        pass
    drained = GSCampaign(scratch, "b07_partial", cells=list(range(128, 326)), cores=[0], plan={str(i): ["slow"] for i in range(128, 326)},
                         slow_s=0.5)
    p = drained.start(keep=True)
    drained.wait_for(lambda s: count(s, "SEALED") >= 2, what="two sealed")
    os.kill(p.pid, signal.SIGTERM)
    check(drained.finish(p)[0] == PS.EXIT_DRAINED, "drained successor")
    part = composite(pred, drained, tol)
    check(part["state"] == "INCOMPLETE" and not part["K4_READY"], f"drained composite {part['state']} {part['problems']}")
    return {"cells_verified": 326, "k4_gate": "accepted", "drained_state": part["state"], "k4_assembly_run": False}


@scenario("countersignature alone without checkpoint -> launch FAIL")
def b08_countersignature_alone(scratch):
    raw = GS.COUNTERSIGNATURE.read_bytes()
    q6_raw = (GS.NS / "evidence/requalification_r1/Q6_RESULT.json").read_bytes()
    q6 = G.evaluate_q6(json.loads(q6_raw), json.loads((GS.NS / "config/Q6_REFERENCE.json").read_bytes()),
                       result_sha256=sha256_bytes(q6_raw))
    rep = G.launch_readiness(proposal_problems=[], proposal_sha256=GS.PROPOSAL_SHA256, q6=q6, countersignature=json.loads(raw),
                             countersignature_sha256=sha256_bytes(raw), checkpoint=None)
    check((rep["state"], rep["problems"]) == ("NOT_READY", ["SUCCESSOR_CHECKPOINT_ABSENT"]), f"{rep}")
    expect_refusal("CHECKPOINT_MISSING", SP.load_checkpoint, scratch / "absent.json", scratch / "absent.hash")
    check(E.main(["launch", "--confirm-checkpoint-sha256", "0" * 64, "--confirm-authorization-sha256", "0" * 64]) == 30
          and not GS.SUCCESSOR_RUNTIME_ROOT.exists(), "launch with unconfirmed objects refused; no runtime root")
    return {"launch_readiness": rep["problems"]}


@scenario("checkpoint without run authorization -> launch FAIL", "launch never passes before the freeze")
def b09_checkpoint_without_authorization(scratch):
    c = GSCampaign(scratch, "b09", cells=[128], authorize=False)
    code, out = c.run(keep=False)
    check(code == PS.EXIT_REFUSED and refused_with(out, "AUTHORIZATION_MISSING") and not (c.root / "ledger.json").exists(),
          f"no genesis without a run authorization (exit {code})")
    expect_refusal("AUTHORIZATION_MISSING", GA.load_authorization, scratch / "none.json", scratch / "none.hash")
    cp, sha = real_checkpoint()
    _auth, asha = GA.load_authorization(GS.AUTHORIZATION, GS.AUTHORIZATION_HASH)
    check(E.main(["launch", "--confirm-checkpoint-sha256", sha, "--confirm-authorization-sha256", "0" * 64]) == 30,
          "wrong authorization confirmation refused")
    check(E.main(["launch", "--confirm-checkpoint-sha256", sha, "--confirm-authorization-sha256", asha]) == 30
          and not GS.SUCCESSOR_RUNTIME_ROOT.exists(), "correct confirmations but pre-freeze preflight NOT_READY: refused")
    return {"supervisor": "AUTHORIZATION_MISSING", "launch_before_freeze": "REFUSED"}


@scenario("production isolation", "predecessor runtime read only", "foreign authorization refused")
def b10_isolation_and_foreign_authorization(scratch):
    c = GSCampaign(scratch, "b10", cells=[128, 129], cores=[0])
    for root in (GS.SUCCESSOR_RUNTIME_ROOT / "x", GS.PREDECESSOR_RUNTIME_ROOT / "x", GS.BLOCKED_RUNTIME_ROOT / "x"):
        expect_refusal("SYNTHETIC_PRODUCTION_MIX", SP.synthetic_spec, {**c.cfg, "root": str(root)})
    check(c.run(keep=True)[0] == PS.EXIT_COMPLETE, "synthetic run")
    other = GSCampaign(scratch, "b10_other", cells=[128, 129], cores=[0])
    st, entries = c.view()
    (aid, a), = attempts(st, cell=128, status="SEALED")
    expect_any({"NO_PRE_RESULT_AUTHORIZATION", "AUTHORIZATION_MISMATCH"}, verify_pair, spec=c.spec, authz=other.authz(), st=st,
               entries=entries, record_path=c.root / a["record"], envelope_path=c.root / a["provenance"]["envelope"])
    b = json.loads(GS.BINDING.read_bytes())
    files = {n: sha256_file(GS.PREDECESSOR_RUNTIME_ROOT / n) for n in b["files"]}
    check(files == b["files"] and not GS.SUCCESSOR_RUNTIME_ROOT.exists(), "predecessor unchanged; successor root absent")
    return {"refused_roots": 3, "foreign_authorization": "refused"}


@scenario("host idle check has no self-matching", "a live synthetic supervisor is detected")
def b11_process_scan(scratch):
    check(H.foreign_campaign_processes() == [], "this acceptance process does not match itself")
    decoy = subprocess.Popen(["bash", "-c", "sleep 4; : gs_entry.py _supervise qualify5.py prov_supervisor.py"])
    try:
        time.sleep(0.5)
        check(H.foreign_campaign_processes() == [], "a diagnostic shell mentioning script names is not a campaign process")
    finally:
        decoy.kill()
        decoy.wait()
    c = GSCampaign(scratch, "b11", cells=[128, 129], cores=[0], plan={"128": ["slow"]}, slow_s=3.0)
    p = c.start(keep=True)
    c.wait_for(lambda s: attempts(s, status="RUNNING"), what="running")
    found = H.foreign_campaign_processes()
    check(any(f["kind"] == "SUPERVISOR_OR_WORKER" for f in found), f"live supervisor/worker detected: {found}")
    check(c.finish(p)[0] == PS.EXIT_COMPLETE, "finish")
    deadline = time.monotonic() + 10
    while H.foreign_campaign_processes() and time.monotonic() < deadline:
        time.sleep(0.2)
    check(H.foreign_campaign_processes() == [], "idle again")
    return {"detected_kinds": sorted({f["kind"] for f in found})}
