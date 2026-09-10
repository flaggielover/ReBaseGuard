"""THE mandatory integrated RESULT-FREE lifecycle:

fresh state -> AWS start -> injected worker loss -> child SIGKILL -> total
process-group loss + simulated reboot + stale lock + torn artefacts -> SIGTERM
stop -> AWS 247 complete -> completed restart refused -> authenticated handoff ->
Vultr refused before import -> import (idempotent, conflicting/tampered refused)
-> Vultr child SIGKILL + stale lock -> reset attempt refused -> Vultr 69 complete
-> final 316/8849 assembly (idempotent) -> completed-campaign restart refused.

Real supervisor processes, real frozen preflight/scheduler/WorkerPool (real
pinned processes), real fsync'd ledgers, real signatures (a TEMPORARY key).
Only the science callable is a synthetic stub. No genuine SR cell runs.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

import conftest as C
import opscommon as OC
import ledger_ops as LO
import supervisor as SV

PNS = OC.PARENT_NS_REL
OPS = LO.OPS_FIELD
EVID = {}


def runrec(rt: Path, rid):
    return json.loads((rt / "runs" / f"{rid}.json").read_text())


def aws_owned(root):
    m = json.loads((Path(root) / PNS / "config/SHARD_MANIFEST.json").read_text())
    return sorted(m["AWS"]["cells"]), sorted(m["VULTR"]["cells"])


def accounting_reconciles(L, role):
    recs = list(L["completed_cells"].values())
    science = sum(r["cpu_seconds"] for r in recs) / 3600.0
    charges = sum(s["charge_cpu_h"] for s in L[OPS]["settlements"])
    return abs(L["committed_cpu_h_by_role"][role] - (science + charges)) < 1e-6


def charged(L):
    return 1.15 * (sum(L["committed_cpu_h_by_role"].values()) +
                   sum(r["reserved_cpu_h"] for r in L["open_reservations"].values()) + 206.086)


@pytest.fixture(scope="module")
def campaign(tmp_path_factory, keys):
    tmp = tmp_path_factory.mktemp("lifecycle")
    aws, vul = C.make_clone(tmp / "aws"), C.make_clone(tmp / "vultr")
    cp = C.synthetic_contract(tmp, aws_root=aws, vultr_root=vul, keys=keys)
    rtA, rtV = tmp / "runtime-AWS", tmp / "runtime-VULTR"
    (tmp / "boot_id").write_text("boot-A")
    (tmp / "boot_time").write_text(str(time.time() - 3600))
    log = tmp / "supervisor.log"
    A_CELLS, V_CELLS = aws_owned(aws)
    spec_a = json.loads(cp.read_text())["hosts"]["AWS"]
    E = {"runs": {}}

    # 1. injected worker loss on the first attempt of cell 10
    C.set_control(cp, spin_s=0.25, die={"10": [1]})
    rc, r1 = C.run_supervisor(cp, "AWS", log=log)
    E["runs"]["worker_loss"] = {"rc": rc, "rec": runrec(rtA, r1)}

    # 2. SIGKILL of the child launcher mid-run
    C.set_control(cp, spin_s=0.25)
    n0 = len(C.ledger(aws)["completed_cells"])
    p, r2 = C.start_supervisor(cp, "AWS", log=log)
    C.wait_for(lambda: len(C.ledger(aws)["completed_cells"]) >= n0 + 20)
    os.kill(runrec(rtA, r2)["child_pid"], signal.SIGKILL)
    E["runs"]["child_sigkill"] = {"rc": p.wait(timeout=300), "rec": runrec(rtA, r2)}

    # 3. total loss of the whole process group (host crash), then crash artefacts + reboot
    n0 = len(C.ledger(aws)["completed_cells"])
    p, r3 = C.start_supervisor(cp, "AWS", log=log)
    C.wait_for(lambda: len(C.ledger(aws)["completed_cells"]) >= n0 + 20)
    C.kill_tree(p.pid)
    p.wait(timeout=60)
    C.wait_for(lambda: not SV.live_run_processes(spec_a), timeout=60)
    L3 = C.ledger(aws)
    E["crash_state"] = {"open_reservations": sorted(L3["open_reservations"]),
                        "run3_status": L3[OPS]["runs"][r3]["status"]}
    prod = aws / PNS / "production"
    q = subprocess.Popen(["true"]); q.wait()
    (prod / "PRODUCTION_LEDGER.json.lock").write_text(f"{q.pid}\n")          # dead-owner lock
    (prod / "cells/.tmp-crash").write_text('{"partial": ')                    # torn temp write
    pending = [c for c in A_CELLS if str(c) not in L3["completed_cells"]]
    (prod / f"cells/{pending[0]:04d}.json").write_text('{"orphan": true}')    # result w/o ledger commit
    time.sleep(1.1)
    (tmp / "boot_id").write_text("boot-B")
    (tmp / "boot_time").write_text(str(time.time()))            # the new boot follows the crash
    time.sleep(2.0)                                             # a real boot precedes any new lock

    # 4. recovery in prestart, then an operator SIGTERM stop mid-run
    n0 = len(L3["completed_cells"])
    p, r4 = C.start_supervisor(cp, "AWS", log=log)
    C.wait_for(lambda: len(C.ledger(aws)["completed_cells"]) >= n0 + 10)
    os.kill(p.pid, signal.SIGTERM)
    E["runs"]["sigterm"] = {"rc": p.wait(timeout=300), "rec": runrec(rtA, r4)}
    E["runs"]["crash_recovered"] = C.ledger(aws)[OPS]["runs"][r3]["settlement"]
    E["quarantine"] = [json.loads(m.read_text()) for m in (rtA / "quarantine").rglob("QUARANTINE_MANIFEST.json")]

    # 5. natural completion
    rc, r5 = C.run_supervisor(cp, "AWS", log=log)
    E["runs"]["complete"] = {"rc": rc, "rec": runrec(rtA, r5)}
    LA = C.ledger(aws)
    E["aws_ledger"] = LA
    E["aws_git_status"] = subprocess.check_output(["git", "-C", str(aws), "status", "--porcelain"]).decode()

    # 6. completed restart refused; ledger bytes untouched
    before = (prod / "PRODUCTION_LEDGER.json").read_bytes()
    rc, _ = C.run_supervisor(cp, "AWS", log=log)
    E["aws_restart_after_complete"] = {"rc": rc,
                                       "ledger_unchanged": before == (prod / "PRODUCTION_LEDGER.json").read_bytes()}

    # 7. authenticated handoff
    E["export1"] = C.prodctl(cp, "AWS", "handoff-export")
    E["export2"] = C.prodctl(cp, "AWS", "handoff-export")
    E["vultr_before_import"] = C.run_supervisor(cp, "VULTR", log=log)[0]
    E["import1"] = C.prodctl(cp, "VULTR", "handoff-import", "--from", str(rtA / "handoff"))
    E["import2"] = C.prodctl(cp, "VULTR", "handoff-import", "--from", str(rtA / "handoff"))
    bad = tmp / "tampered"; shutil.copytree(rtA / "handoff", bad)
    t = json.loads((bad / "AWS_PRODUCTION_LEDGER.json").read_text())
    t["committed_cpu_h_by_role"]["AWS"] = 0.0
    (bad / "AWS_PRODUCTION_LEDGER.json").write_text(json.dumps(t))
    E["import_tampered"] = C.prodctl(cp, "VULTR", "handoff-import", "--from", str(bad))
    sig = tmp / "badsig"; shutil.copytree(rtA / "handoff", sig)
    d = json.loads((sig / "AWS_TO_VULTR_HANDOFF.json").read_text())
    d["payload"]["created_at"] += 1                                     # signature no longer covers it
    (sig / "AWS_TO_VULTR_HANDOFF.json").write_text(json.dumps(d))
    E["import_bad_signature"] = C.prodctl(cp, "VULTR", "handoff-import", "--from", str(sig))
    conf = tmp / "conflict"; conf.mkdir()
    shutil.copy(rtA / "handoff" / "AWS_PRODUCTION_LEDGER.json", conf)
    drv = aws / PNS / "driver"
    code = (f"import sys;sys.path.insert(0,'{drv}');import production_launcher as PL, handoff as HO, "
            f"multihost as M, global_budget as GB;a=PL.load_production_authorization();"
            f"o=M.gate_shards(M.load_shard_manifest('{aws / PNS / 'config/SHARD_MANIFEST.json'}',a['shard_manifest_sha256']));"
            f"b=GB.GlobalBudget('{aws / PNS / 'production/PRODUCTION_LEDGER.json'}',M.validate_governed_cost,"
            f"M.gate_global_cap,overhead_cpu_h=a['governed_overhead_cpu_h'],cap_cpu_h=4500.0);"
            f"HO.export_handoff(auth=a,ns=PL.PROD_NS,owners=o,budget=b,approved_head='{C.PARENT_COMMIT}',"
            f"privkey_pem='{keys[0]}',out_path='{conf / 'AWS_TO_VULTR_HANDOFF.json'}',"
            f"validate_governed_cost=M.validate_governed_cost,gate_global_cap=M.gate_global_cap,nonce='c'*32)")
    subprocess.run([C.PY, "-c", code], check=True)                     # a DIFFERENT, validly signed handoff
    E["import_conflicting"] = C.prodctl(cp, "VULTR", "handoff-import", "--from", str(conf))

    # 8. Vultr: child SIGKILL + dead-owner lock, reset attempt, completion
    C.set_control(cp, spin_s=0.25)
    p, v1 = C.start_supervisor(cp, "VULTR", log=log)
    C.wait_for(lambda: len(C.ledger(vul)["completed_cells"]) >= 10)
    os.kill(runrec(rtV, v1)["child_pid"], signal.SIGKILL)
    E["vruns"] = {"child_sigkill": {"rc": p.wait(timeout=300), "rec": runrec(rtV, v1)}}
    vprod = vul / PNS / "production"
    q = subprocess.Popen(["true"]); q.wait()
    (vprod / "PRODUCTION_LEDGER.json.lock").write_text(f"{q.pid}\n")
    vl = vprod / "PRODUCTION_LEDGER.json"
    vl.rename(vprod / "hidden")
    E["vultr_reset_attempt"] = C.run_supervisor(cp, "VULTR", log=log)[0]
    (vprod / "hidden").rename(vl)
    rc, v2 = C.run_supervisor(cp, "VULTR", log=log)
    E["vruns"]["complete"] = {"rc": rc, "rec": runrec(rtV, v2)}
    E["vultr_ledger"] = C.ledger(vul)

    # 9. assembly and completed-campaign behaviour
    E["assemble1"] = C.prodctl(cp, "VULTR", "assemble")
    E["assemble2"] = C.prodctl(cp, "VULTR", "assemble")
    E["status_v"] = C.prodctl(cp, "VULTR", "status")
    E["status_a"] = C.prodctl(cp, "AWS", "status")
    E["vultr_restart_after_complete"] = C.run_supervisor(cp, "VULTR", log=log)[0]
    E["aws_restart_final"] = C.run_supervisor(cp, "AWS", log=log)[0]
    E["export_after"] = C.prodctl(cp, "AWS", "handoff-export")
    E["supervisor_log_tail"] = log.read_text()[-4000:]
    E.update(tmp=tmp, cp=cp, aws=aws, vul=vul, rtA=rtA, rtV=rtV, A=A_CELLS, V=V_CELLS)
    return E


def test_aws_worker_loss_detected_and_settled(campaign):
    w = campaign["runs"]["worker_loss"]
    assert w["rc"] == SV.EXIT_OTHER and w["rec"]["reason"].startswith("WORKER_LOST")
    s = w["rec"]["settlement"]
    assert s["evidence"] == "SUPERVISOR_FINAL" and s["measured_run_cpu_h"] >= s["committed_science_cpu_h"]
    assert 10 in s["orphan_cells"] and s["unattributed_charge_cpu_h"] > 0.0


def test_aws_child_sigkill_settled_exactly(campaign):
    r = campaign["runs"]["child_sigkill"]["rec"]
    assert r["reason"] == "CHILD_EXIT_-9" and r["settlement"]["evidence"] == "SUPERVISOR_FINAL"
    assert r["settlement"]["orphan_cells"], "in-flight cells must become orphans, then retry-eligible"


def test_host_crash_recovered_with_conservative_tail_bound_and_artefacts(campaign):
    assert campaign["crash_state"]["run3_status"] == "OPEN" and campaign["crash_state"]["open_reservations"]
    s = campaign["runs"]["crash_recovered"]
    assert s["evidence"] == "TAIL_BOUND_REBOOT"
    assert s["measured_run_cpu_h"] >= s["committed_science_cpu_h"]
    files = {f["path"] for q in campaign["quarantine"] for f in q["files"]}
    assert "production/cells/.tmp-crash" in files and any(p.startswith("production/cells/0") for p in files)
    assert campaign["runs"]["sigterm"]["rec"]["reason"] == "STOP_SIGNAL_SIGTERM"


def test_aws_completes_exact_247_without_duplicates_and_accounting_preserved(campaign):
    L = campaign["aws_ledger"]
    assert campaign["runs"]["complete"]["rc"] == 0
    assert sorted(int(c) for c in L["completed_cells"]) == campaign["A"]
    assert L["open_reservations"] == {}
    assert all(r["status"] == "SETTLED" for r in L[OPS]["runs"].values()) and len(L[OPS]["runs"]) == 5
    assert max(L[OPS]["torn_attempts"].values()) <= 2 and L[OPS]["halt"] is None
    assert accounting_reconciles(L, "AWS") and charged(L) <= 4500.0
    for c, rec in L["completed_cells"].items():
        f = campaign["aws"] / PNS / f"production/cells/{int(c):04d}.json"
        assert json.loads(f.read_text()) == rec
    assert campaign["aws_git_status"] == ""
    assert campaign["aws_restart_after_complete"] == {"rc": SV.EXIT_REFUSED, "ledger_unchanged": True}


def test_handoff_binds_recovered_accounting_and_is_idempotent(campaign):
    rc, out = campaign["export1"]
    assert rc == 0 and out["status"] == "EXPORTED"
    assert out["aws_finalized_cpu_h"] == campaign["aws_ledger"]["committed_cpu_h_by_role"]["AWS"]
    torn = sum(s["charge_cpu_h"] for s in campaign["aws_ledger"][OPS]["settlements"])
    assert torn > 0 and out["aws_finalized_cpu_h"] > torn          # torn charges travel to Vultr
    assert campaign["export2"][1]["status"] == "IDEMPOTENT_ALREADY_EXPORTED"
    assert campaign["export_after"][1]["status"] == "IDEMPOTENT_ALREADY_EXPORTED"


def test_vultr_cannot_run_before_import_and_import_is_safe(campaign):
    assert campaign["vultr_before_import"] == SV.EXIT_REFUSED
    assert campaign["import1"][1]["status"] == "APPLIED" and campaign["import1"][1]["remote_completed"] == 247
    assert campaign["import2"][1]["status"] == "IDEMPOTENT_ALREADY_APPLIED"
    assert "REFUSED" in campaign["import_tampered"][1]
    assert "REFUSED" in campaign["import_bad_signature"][1]
    assert "REFUSED" in campaign["import_conflicting"][1] and \
        "DIFFERENT" in campaign["import_conflicting"][1]["REFUSED"], campaign["import_conflicting"]
    assert campaign["vultr_ledger"]["committed_cpu_h_by_role"]["AWS"] == \
        campaign["aws_ledger"]["committed_cpu_h_by_role"]["AWS"]             # inherited, never reset


def test_vultr_interruption_recovery_and_completion(campaign):
    k = campaign["vruns"]["child_sigkill"]["rec"]
    assert k["reason"] == "CHILD_EXIT_-9"
    assert campaign["vultr_reset_attempt"] == SV.EXIT_REFUSED
    V = campaign["vultr_ledger"]
    assert campaign["vruns"]["complete"]["rc"] == 0
    assert sorted(int(c) for c in V["completed_cells"]) == campaign["V"]
    assert V["open_reservations"] == {} and accounting_reconciles(V, "VULTR")
    assert charged(V) <= 4500.0


def test_final_assembly_316_8849_deterministic(campaign):
    rc, a = campaign["assemble1"]
    assert rc == 0 and a["status"] == "ASSEMBLED", a
    assert a["cells_completed"] == 316 and a["obligations_completed"] == 8849
    assert a["far_field"] == "SR:-1:far_field:all_m" and a["governed_charged_cpu_h"] <= 4500.0
    rc2, b = campaign["assemble2"]
    assert b["status"] == "IDEMPOTENT" and {k: v for k, v in b.items() if k != "status"} == \
        {k: v for k, v in a.items() if k != "status"}


def test_completed_campaign_restart_is_refused_everywhere(campaign):
    assert campaign["status_v"][1]["phase"] == "COMPLETE_ASSEMBLED"
    assert campaign["status_a"][1]["phase"] == "SHARD_COMPLETE_HANDOFF_EXPORTED"
    assert campaign["vultr_restart_after_complete"] == SV.EXIT_REFUSED
    assert campaign["aws_restart_final"] == SV.EXIT_REFUSED


# ------------------------------------------------------------ assembly negatives
def _frozen(campaign):
    d = str(campaign["vul"] / PNS / "driver")
    if d not in sys.path:
        sys.path.insert(0, d)
    import production_launcher as PL, production_provenance as PP, multihost as M
    auth = PL.load_production_authorization()
    owners = M.gate_shards(M.load_shard_manifest(campaign["vul"] / PNS / "config/SHARD_MANIFEST.json",
                                                 auth["shard_manifest_sha256"]))
    return PL, PP, M, auth, owners


def _assemble(campaign, aws, vul):
    PL, PP, M, auth, owners = _frozen(campaign)
    ah = PL.authorization_hash()
    for r in aws + vul:
        PP.verify(r, production_authorization_hash=ah, scientific_adapter_hash=auth["scientific_adapter_hash"])
    return PL.assemble_production_campaign({"auth": auth, "owners": owners}, {"AWS": aws, "VULTR": vul})


def _recs(campaign):
    return (copy.deepcopy(list(campaign["aws_ledger"]["completed_cells"].values())),
            copy.deepcopy(list(campaign["vultr_ledger"]["completed_cells"].values())))


def test_assembly_positive_control(campaign):
    a, v = _recs(campaign)
    assert _assemble(campaign, a, v)["cells_completed"] == 316


@pytest.mark.parametrize("mut", ["missing", "duplicate", "foreign", "phase8", "torn", "bad_provenance",
                                 "wrong_checkpoint", "corrupted_hash", "field_swap"])
def test_assembly_rejections(campaign, mut):
    a, v = _recs(campaign)
    PL, PP, M, auth, owners = _frozen(campaign)
    if mut == "missing":
        v.pop()
    elif mut == "duplicate":
        v.append(copy.deepcopy(a[0]))
    elif mut == "foreign":
        r = copy.deepcopy(a[0]); r["role"] = "VULTR"; v.append(r)
    elif mut == "phase8":
        r = v.pop(); v.append({k: r[k] for k in r if k != "production_provenance"} |
                              {"scientific_content_hash": "%064x" % r["cell_id"],
                               "checkpoint_sha256": auth["inherited"]["checkpoint_sha256"]})
    elif mut == "torn":
        v[0]["complete"] = False
    elif mut == "bad_provenance":
        v[0]["production_provenance"]["binding"] = "0" * 64
    elif mut == "wrong_checkpoint":
        v[0]["checkpoint_sha256"] = "f" * 64
    elif mut == "corrupted_hash":
        v[0]["scientific_content_hash"] = "zz"
    elif mut == "field_swap":
        v[0]["production_provenance"], v[1]["production_provenance"] = \
            v[1]["production_provenance"], v[0]["production_provenance"]
    with pytest.raises(Exception):
        _assemble(campaign, a, v)


def test_assembly_rejects_wrong_authorization(campaign):
    a, v = _recs(campaign)
    PL, PP, M, auth, owners = _frozen(campaign)
    with pytest.raises(PP.ProvenanceRefusal):
        PP.verify(v[0], production_authorization_hash="e" * 64,
                  scientific_adapter_hash=auth["scientific_adapter_hash"])


def test_assembly_rejects_incomplete_accounting_and_partial_json(campaign):
    import prodctl as PC
    PL, PP, M, auth, owners = _frozen(campaign)
    V = copy.deepcopy(campaign["vultr_ledger"])
    V[OPS]["settlements"].pop()
    with pytest.raises(OC.OpsRefusal, match="reconcile"):
        PC.reconcile(V, "VULTR", list(V["completed_cells"].values()), M)
    V = copy.deepcopy(campaign["vultr_ledger"])
    next(iter(V[OPS]["runs"].values()))["status"] = "OPEN"
    with pytest.raises(OC.OpsRefusal, match="incomplete"):
        PC.reconcile(V, "VULTR", list(V["completed_cells"].values()), M)
    p = campaign["tmp"] / "partial.json"; p.write_text('{"payload": {')
    with pytest.raises(OC.OpsRefusal, match="partial"):
        OC.read_json_strict(p)


def test_mismatched_attempt_cell_file_refuses_assembly(campaign):
    f = campaign["vul"] / PNS / f"production/cells/{campaign['V'][0]:04d}.json"
    orig = f.read_bytes()
    rec = json.loads(orig); rec["cpu_seconds"] += 1.0
    f.write_text(json.dumps(rec))
    fin = campaign["rtV"] / "FINAL_ASSEMBLY.json"
    keep = fin.read_bytes(); fin.unlink()
    try:
        rc, out = C.prodctl(campaign["cp"], "VULTR", "assemble")
        assert rc == 30 and ("differs" in out["REFUSED"] or "mismatch" in out["REFUSED"]), out
    finally:
        f.write_bytes(orig); fin.write_bytes(keep)


# ---------------------------------------------------------------- science halt
def test_worker_reported_failure_halts_and_is_never_retried(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("halt")
    aws = C.make_clone(tmp / "aws")
    cp = C.synthetic_contract(tmp, aws_root=aws)
    (tmp / "boot_id").write_text("boot-A")
    C.set_control(cp, spin_s=0.05, fail={"12": [1]})
    rc, rid = C.run_supervisor(cp, "AWS", log=tmp / "s.log")
    L = C.ledger(aws)
    assert rc == SV.EXIT_HALT
    h = L[OPS]["halt"]
    assert h["reason"] == "SCIENTIFIC_OR_UNCLASSIFIED_FAILURE" and 12 in h["cells"]["WORKER_REPORTED_FAILURE"]
    assert "SYNTHETIC injected worker failure" in h["events"][0]["error"]
    assert "12" not in L["completed_cells"] and L["open_reservations"] == {}
    assert L[OPS]["runs"][rid]["settlement"]["measured_run_cpu_h"] > 0     # its CPU is charged
    rc2, _ = C.run_supervisor(cp, "AWS", log=tmp / "s.log")
    assert rc2 == SV.EXIT_REFUSED                                          # never retried
    assert C.prodctl(cp, "AWS", "status")[1]["phase"] == "HALTED"


def test_real_production_namespaces_untouched():
    assert C.real_production_untouched() == {"AWS": ["README.md"]}
