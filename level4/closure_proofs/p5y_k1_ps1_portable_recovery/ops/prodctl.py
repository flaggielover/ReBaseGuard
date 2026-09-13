"""Operator CLI: the ONLY sanctioned way to start, stop, inspect and advance the
P5Y K1 SR production campaign. Nothing here runs science.

  render / start / stop / status / recover / verify / install-runtime-policy
  settle-fallback   (systemd ExecStopPost: settles the run if its supervisor died)
  handoff-export    (AWS: frozen export_handoff on the PRODUCTION ledger)
  handoff-import    (VULTR: frozen verify_handoff + apply_handoff, AWS ledger authenticated)
  assemble          (frozen assemble_production_campaign + governed re-gate)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from opscommon import (OpsRefusal, CgroupCPU, RuntimeDir, atomic_write, canonical,   # noqa: E402
                       frozen_accounting, frozen_budget, host_spec, ledger_path,
                       load_contract, new_run_id, prod_ns, read_json_strict, sha256_bytes,
                       sha256_file, unit_state, write_json_atomic)
import ledger_ops as LO                                                               # noqa: E402
import locks as LK                                                                    # noqa: E402
import runtime_state as RS                                                            # noqa: E402
import supervisor as SV                                                               # noqa: E402

HANDOFF_DOC = "AWS_TO_VULTR_HANDOFF.json"
AWS_LEDGER = "AWS_PRODUCTION_LEDGER.json"
FINAL = "FINAL_ASSEMBLY.json"


def frozen_prod(spec):
    d = str(prod_ns(spec) / "driver")
    if d not in sys.path:
        sys.path.insert(0, d)
    import production_launcher as PL                              # noqa: E402
    import production_provenance as PP                            # noqa: E402
    import handoff as HO                                          # noqa: E402
    import multihost as M                                         # noqa: E402
    return PL, PP, HO, M


def _auth(spec):
    PL, *_ = frozen_prod(spec)
    return PL.load_production_authorization()


# ------------------------------------------------------------------ service
def render_start(contract, role, run_id) -> list:
    spec, svc = host_spec(contract, role), contract["service"]
    unit = SV.unit_name(contract, role, run_id)
    ops = Path(spec["ops_root"])
    cpath = contract["_path"]
    argv = list(spec.get("launch_prefix", [])) + [
        "systemd-run", f"--unit={unit}", f"--uid={spec['user']}",
        f"--working-directory={spec['production_root']}",
        "-p", f"Type={svc['type']}", "-p", f"Restart={svc['restart']}",
        "-p", f"KillMode={svc['kill_mode']}", "-p", f"TimeoutStopSec={svc['timeout_stop_sec']}",
        "-p", "CPUAccounting=yes", "-p", f"RuntimeMaxSec={svc['runtime_max_sec']}",
        "-p", (f"ExecStopPost={spec['python']} {ops / 'ops/prodctl.py'} settle-fallback "
               f"--contract {cpath} --role {role} --run-id {run_id}")]
    for k, v in sorted(svc["environment"][role].items()):
        argv.append(f"--setenv={k}={v}")
    argv += ["--", spec["python"], str(ops / "ops/supervisor.py"),
             "--contract", cpath, "--role", role, "--run-id", run_id]
    return argv


def cmd_start(contract, role, wait_s=8.0) -> dict:
    spec = host_spec(contract, role)
    rt = RuntimeDir(spec).ensure()
    if LK.CampaignLock(rt, contract).probe() == LK.LIVE:
        raise OpsRefusal("a run is already live (campaign lock held)")
    run_id = new_run_id()
    argv = render_start(contract, role, run_id)
    r = subprocess.run(argv, capture_output=True, text=True)
    if r.returncode != 0:
        raise OpsRefusal(f"systemd-run failed: {r.stderr.strip()}")
    time.sleep(wait_s)
    unit = SV.unit_name(contract, role, run_id)
    rec = rt.run_record(run_id)
    return {"run_id": run_id, "unit": unit, "unit_state": unit_state(unit),
            "run_record": json.loads(rec.read_text()) if rec.exists() else None}


def cmd_stop(contract, role) -> dict:
    spec = host_spec(contract, role)
    rt = RuntimeDir(spec)
    owner = LK.CampaignLock(rt, contract).read_owner()
    if not owner or LK.CampaignLock(rt, contract).probe() != LK.LIVE:
        return {"stopped": None, "reason": "no live run"}
    argv = list(spec.get("launch_prefix", [])) + ["systemctl", "stop", owner["unit"]]
    r = subprocess.run(argv, capture_output=True, text=True)
    return {"stopped": owner["unit"], "rc": r.returncode, "stderr": r.stderr.strip()}


# ------------------------------------------------------------------- status
def cmd_status(contract, role) -> dict:
    spec = host_spec(contract, role)
    rt = RuntimeDir(spec)
    M, GB = frozen_accounting(spec)
    io = LO.LedgerIO(ledger_path(spec), M, GB, frozen_budget(spec, contract))
    st = io.read()
    owners = SV.owners_of(spec, contract)
    owned = sorted(c for c, r in owners.items() if r == role)
    lockp = LK.CampaignLock(rt, contract).probe()
    owner = LK.CampaignLock(rt, contract).read_owner()
    cap, refusal = io.cap(st) if st else (None, None)
    done = sorted(int(c) for c in (st or {}).get("completed_cells", {}))
    ops = (st or {}).get(LO.OPS_FIELD) or {}
    unsettled = LO.unsettled_runs(st, role) if st else []
    final = rt.root / FINAL
    hb = rt.root / "heartbeat.json"
    if final.exists():
        phase = "COMPLETE_ASSEMBLED"
    elif ops.get("halt"):
        phase = "HALTED"
    elif lockp == LK.LIVE:
        phase = "RUNNING"
    elif unsettled:
        phase = "INTERRUPTED_RECOVERY_PENDING"
    elif len(set(done) & set(owned)) == len(owned):
        phase = ("SHARD_COMPLETE_HANDOFF_EXPORTED" if (rt.root / "handoff" / HANDOFF_DOC).exists()
                 else "SHARD_COMPLETE_HANDOFF_PENDING") if role == "AWS" \
            else "SHARD_COMPLETE_ASSEMBLY_PENDING"
    elif role == "VULTR" and len((st or {}).get("remote_completed_cells", {})) != contract["parent"]["aws_cells"]:
        phase = "AWAITING_AUTHENTICATED_HANDOFF"
    else:
        phase = "READY_TO_RUN" if st else "NOT_STARTED"
    return {"role": role, "phase": phase, "contract_sha256": contract["_sha256"],
            "campaign_lock": lockp, "owner": owner if lockp == LK.LIVE else None,
            "owned": len(owned), "completed": len(set(done) & set(owned)),
            "pending": len(owned) - len(set(done) & set(owned)),
            "remote_completed": len((st or {}).get("remote_completed_cells", {})),
            "open_reservations": sorted((st or {}).get("open_reservations", {})),
            "committed_cpu_h_by_role": (st or {}).get("committed_cpu_h_by_role", {}),
            "charged_cpu_h": cap["charged_cpu_h"] if cap else None,
            "cap_cpu_h": contract["parent"]["global_cpu_cap"], "headroom_cpu_h": cap["headroom_cpu_h"] if cap else None,
            "cap_refusal": refusal, "runs": len(ops.get("runs", {})), "unsettled_runs": unsettled,
            "settlements": len(ops.get("settlements", [])),
            "torn_attempts": ops.get("torn_attempts", {}), "halt": ops.get("halt"),
            "heartbeat_age_s": (time.time() - json.loads(hb.read_text())["t_wall"])
            if hb.exists() else None}


def with_lock(contract, role, fn, timeout_s=0.0):
    spec = host_spec(contract, role)
    rt = RuntimeDir(spec).ensure()
    lock = LK.CampaignLock(rt, contract)
    lock.acquire(run_id="00000000T000000Z-00000000", unit=f"prodctl:{fn.__name__}",
                 timeout_s=timeout_s)
    try:
        return fn(contract, role, rt, lock)
    finally:
        lock.release()


def _recover(contract, role, rt, lock):
    rep = SV.prestart(contract, role, rt, lock, allow_complete=True)
    rep.pop("io", None)
    rep.pop("state", None)
    return rep


def _settle_fallback(contract, role, rt, lock, run_id=None):
    spec = host_spec(contract, role)
    M, GB = frozen_accounting(spec)
    io = LO.LedgerIO(ledger_path(spec), M, GB, frozen_budget(spec, contract))
    st = io.read()
    run = ((st or {}).get(LO.OPS_FIELD) or {}).get("runs", {}).get(run_id)
    if run is None or run["status"] == "SETTLED":
        return {"settled": False, "why": "run never opened or already settled"}
    flag = (contract.get("synthetic") or {}).get("disable_stop_post_settle_file")
    if contract["mode"] == "SYNTHETIC_CONTROL" and flag and Path(flag).exists():
        # HARNESS ONLY: leave the run unsettled so pre-start must use the JOURNAL evidence
        return {"settled": False, "why": "synthetic: stop-post settlement disabled"}
    cpu = CgroupCPU(SV.unit_name(contract, role, run_id))
    deadline = time.time() + 60
    while [p for p in cpu.procs() if p != os.getpid()]:
        if time.time() > deadline:
            raise OpsRefusal("run processes still alive in stop-post; leaving to prestart")
        time.sleep(0.2)
    u = cpu.usage_usec()
    rec_p = rt.run_record(run_id)
    rec = json.loads(rec_p.read_text()) if rec_p.exists() else {"run_id": run_id}
    rec.update({"final_u_usec": int(u), "final_evidence": "EXECSTOPPOST_CGROUP",
                "status": "ENDED_SUPERVISOR_LOST"})
    write_json_atomic(rec_p, rec)
    LK.reclaim_ledger_lock(Path(str(io.path) + ".lock"), contract, campaign_lock=lock)
    return {"settled": True, "settlement": LO.settle_run(io, rt, role, run_id, u,
                                                         "EXECSTOPPOST_CGROUP")}


# ------------------------------------------------------------------ handoff
def verify_aws_ledger(aws_state, payload, spec, auth, owners, HO, PP, M) -> dict:
    comp = sorted(int(c) for c in aws_state.get("completed_cells", {}))
    if comp != sorted(payload["aws_completed_cell_ids"]):
        raise OpsRefusal("AWS ledger completed set != signed handoff")
    if aws_state.get("open_reservations"):
        raise OpsRefusal("AWS ledger has open reservations")
    lh = sha256_bytes(HO.canonical({"completed": comp,
                                    "committed_cpu_h_by_role": aws_state["committed_cpu_h_by_role"]}))
    if lh != payload["aws_ledger_hash"]:
        raise OpsRefusal("AWS ledger hash does not match the SIGNED aws_ledger_hash")
    rh = sha256_bytes(HO.canonical({str(c): aws_state["completed_cells"][str(c)].get(
        "scientific_content_hash") for c in comp}))
    if rh != payload["aws_result_manifest_hash"]:
        raise OpsRefusal("AWS result manifest does not match the SIGNED hash")
    if aws_state["committed_cpu_h_by_role"].get("AWS") != payload["aws_finalized_cpu_h"]:
        raise OpsRefusal("AWS committed CPU-h != signed aws_finalized_cpu_h")
    ah = sha256_file(prod_ns(spec) / "config/LAUNCH_AUTHORIZATION.json")
    recs = []
    for c in comp:
        rec = aws_state["completed_cells"][str(c)]
        M.validate_record(rec, "AWS", owners, auth["producer_commit"], auth["checkpoint_sha256"])
        PP.verify(rec, production_authorization_hash=ah,
                  scientific_adapter_hash=auth["scientific_adapter_hash"])
        recs.append(rec)
    reconcile(aws_state, "AWS", recs, M)
    return {"records": recs, "ledger_hash": lh}


def reconcile(state, role, recs, M, tol=1e-6):
    ops = state.get(LO.OPS_FIELD)
    if not ops or any(r["status"] != "SETTLED" for r in ops["runs"].values()):
        raise OpsRefusal(f"{role} accounting incomplete: unsettled or missing operational runs")
    if ops.get("halt"):
        raise OpsRefusal(f"{role} ledger is HALTED: {ops['halt']}")
    science = M.per_host_cpu_h(recs) if recs else 0.0
    charges = sum(s["charge_cpu_h"] for s in ops["settlements"])
    committed = state["committed_cpu_h_by_role"].get(role, 0.0)
    if abs(committed - (science + charges)) > tol:
        raise OpsRefusal(f"{role} accounting does not reconcile: committed {committed} != "
                         f"records {science} + settlement charges {charges}")
    return {"science_cpu_h": science, "settlement_charges_cpu_h": charges, "committed": committed}


def _handoff_export(contract, role, rt, lock):
    if role != "AWS":
        raise OpsRefusal("handoff-export runs on AWS only")
    spec = host_spec(contract, role)
    SV.prestart(contract, role, rt, lock, allow_complete=True)
    PL, PP, HO, M = frozen_prod(spec)
    auth = PL.load_production_authorization()
    owners = SV.owners_of(spec, contract)
    head = subprocess.check_output(["git", "-C", spec["production_root"], "rev-parse",
                                    "HEAD"]).decode().strip()
    out = rt.root / "handoff" / HANDOFF_DOC
    res = HO.export_handoff(auth=auth, ns=prod_ns(spec), owners=owners,
                            budget=frozen_budget(spec, contract), approved_head=head,
                            privkey_pem=Path(spec["handoff_private_key"]), out_path=out,
                            validate_governed_cost=M.validate_governed_cost,
                            gate_global_cap=M.gate_global_cap)
    raw = ledger_path(spec).read_bytes()
    snap = rt.root / "handoff" / AWS_LEDGER
    if snap.exists() and snap.read_bytes() != raw:
        raise OpsRefusal("a DIFFERENT AWS ledger snapshot was already exported")
    atomic_write(snap, raw)
    doc = res["document"]
    verify_aws_ledger(json.loads(raw), doc["payload"], spec, auth, owners, HO, PP, M)
    LO.append_continuity(rt, "HANDOFF_EXPORTED", json.loads(raw),
                         {"payload_hash": doc["payload"]["handoff_payload_hash"]})
    return {"status": res["status"], "handoff": str(out), "aws_ledger": str(snap),
            "payload_hash": doc["payload"]["handoff_payload_hash"],
            "aws_finalized_cpu_h": doc["payload"]["aws_finalized_cpu_h"]}


def _key_material(contract, spec, auth):
    syn = contract.get("synthetic") or {}
    if contract["mode"] == "SYNTHETIC_CONTROL" and syn.get("handoff_pubkey"):
        return Path(syn["handoff_pubkey"]), syn["handoff_fingerprint"]
    return prod_ns(spec) / "config/handoff_pubkey.pem", auth["handoff"]["public_key_fingerprint"]


def _handoff_import(contract, role, rt, lock, src=None):
    if role != "VULTR":
        raise OpsRefusal("handoff-import runs on VULTR only")
    spec = host_spec(contract, role)
    PL, PP, HO, M = frozen_prod(spec)
    auth = PL.load_production_authorization()
    owners = SV.owners_of(spec, contract)
    M_, GB = frozen_accounting(spec)
    io = LO.LedgerIO(ledger_path(spec), M_, GB, frozen_budget(spec, contract))
    st = io.read()
    LO.check_continuity(rt, st)
    src = Path(src)
    doc_raw, aws_raw = (src / HANDOFF_DOC).read_bytes(), (src / AWS_LEDGER).read_bytes()
    doc = json.loads(doc_raw)
    pub, fp = _key_material(contract, spec, auth)
    v = HO.verify_handoff(doc=doc, auth=auth, ns=prod_ns(spec), owners=owners,
                          approved_head=contract["parent"]["commit"], pubkey_pem=pub,
                          expected_fingerprint=fp, validate_governed_cost=M.validate_governed_cost,
                          gate_global_cap=M.gate_global_cap)
    verify_aws_ledger(read_json_strict(src / AWS_LEDGER), v["payload"], spec, auth, owners,
                      HO, PP, M)
    for name, raw in ((HANDOFF_DOC, doc_raw), (AWS_LEDGER, aws_raw)):
        dst = rt.root / "handoff" / name
        if dst.exists() and dst.read_bytes() != raw:
            raise OpsRefusal(f"a DIFFERENT {name} was already imported; conflicting handoff refused")
        atomic_write(dst, raw)
    if st is None:
        LO.append_continuity(rt, "GENESIS", None, {"role": role})
        with io.locked():
            fresh = io.fresh()
            fresh[LO.OPS_FIELD] = LO.new_ops(role)
            io.write(fresh)
    elif LO.OPS_FIELD not in st:
        raise OpsRefusal("Vultr ledger exists without an operational block")
    applied = HO.apply_handoff(verified=v, budget=frozen_budget(spec, contract), ns=prod_ns(spec))
    st2 = io.read()
    LO.append_continuity(rt, "HANDOFF_IMPORTED", st2,
                         {"payload_hash": v["handoff_payload_hash"], "status": applied["status"]})
    return {"status": applied["status"], "payload_hash": v["handoff_payload_hash"],
            "inherited_aws_cpu_h": v["aws_finalized_cpu_h"],
            "remote_completed": len(st2.get("remote_completed_cells", {}))}


# ----------------------------------------------------------------- assembly
def _assemble(contract, role, rt, lock):
    if role != "VULTR":
        raise OpsRefusal("final assembly runs on the VULTR host (it holds both ledgers)")
    spec = host_spec(contract, role)
    SV.prestart(contract, role, rt, lock, allow_complete=True)
    PL, PP, HO, M = frozen_prod(spec)
    auth = PL.load_production_authorization()
    owners = SV.owners_of(spec, contract)
    doc = read_json_strict(rt.root / "handoff" / HANDOFF_DOC)
    pub, fp = _key_material(contract, spec, auth)
    v = HO.verify_handoff(doc=doc, auth=auth, ns=prod_ns(spec), owners=owners,
                          approved_head=contract["parent"]["commit"], pubkey_pem=pub,
                          expected_fingerprint=fp, validate_governed_cost=M.validate_governed_cost,
                          gate_global_cap=M.gate_global_cap)
    aws_state = read_json_strict(rt.root / "handoff" / AWS_LEDGER)
    aws = verify_aws_ledger(aws_state, v["payload"], spec, auth, owners, HO, PP, M)
    M_, GB = frozen_accounting(spec)
    io = LO.LedgerIO(ledger_path(spec), M_, GB, frozen_budget(spec, contract))
    vst = io.read()
    if vst.get("remote_handoff_payload_hash") != v["handoff_payload_hash"]:
        raise OpsRefusal("Vultr ledger imported a different handoff")
    consumed = read_json_strict(prod_ns(spec) / "evidence/handoff_consumed.json")
    if consumed.get("handoff_payload_hash") != v["handoff_payload_hash"]:
        raise OpsRefusal("consumed-handoff record does not match")
    if vst.get("open_reservations"):
        raise OpsRefusal("Vultr has open reservations")
    if vst["committed_cpu_h_by_role"].get("AWS") != v["aws_finalized_cpu_h"]:
        raise OpsRefusal("Vultr inherited AWS CPU-h != signed finalized AWS CPU-h")
    ah = sha256_file(prod_ns(spec) / "config/LAUNCH_AUTHORIZATION.json")
    vrecs = []
    for c in sorted(int(x) for x in vst["completed_cells"]):
        rec = vst["completed_cells"][str(c)]
        M.validate_record(rec, "VULTR", owners, auth["producer_commit"], auth["checkpoint_sha256"])
        PP.verify(rec, production_authorization_hash=ah,
                  scientific_adapter_hash=auth["scientific_adapter_hash"])
        f = prod_ns(spec) / f"production/cells/{c:04d}.json"
        if f.exists() and json.loads(f.read_bytes()) != rec:
            raise OpsRefusal(f"cell file {c:04d}.json differs from the ledger record")
        vrecs.append(rec)
    vacct = reconcile(vst, "VULTR", vrecs, M)
    out = PL.assemble_production_campaign({"auth": auth, "owners": owners},
                                          {"AWS": aws["records"], "VULTR": vrecs})
    governed, refusal = io.cap(vst)
    if refusal:
        raise OpsRefusal(f"governed campaign total refuses the ONE global cap: {refusal}")
    body = {"schema": "rebaseguard.p5y.k1.sr.production.final-assembly.v1",
            "cells_completed": out["cells_completed"],
            "obligations_completed": out["obligations_completed"],
            "aggregate_ledger_sha256": out["aggregate_ledger_sha256"],
            "production_records_verified": out["production_records_verified"],
            "production_authorization_hash": out["production_authorization_hash"],
            "science_cpu_h_by_role": out["cpu_h_by_role"],
            "governed_committed_cpu_h_by_role": vst["committed_cpu_h_by_role"],
            "governed_charged_cpu_h": governed["charged_cpu_h"], "cap_cpu_h": governed["cap"],
            "aws_accounting": reconcile(aws_state, "AWS", aws["records"], M),
            "vultr_accounting": vacct, "handoff_payload_hash": v["handoff_payload_hash"],
            "aws_ledger_hash": aws["ledger_hash"],
            "far_field": auth["far_field_obligation"]["work_id"],
            "contract_sha256": contract["_sha256"]}
    raw = (json.dumps(body, indent=1, sort_keys=True) + "\n").encode()
    dst = rt.root / FINAL
    if dst.exists():
        if dst.read_bytes() != raw:
            raise OpsRefusal("a DIFFERENT final assembly already exists")
        return dict(body, status="IDEMPOTENT")
    atomic_write(dst, raw)
    LO.append_continuity(rt, "ASSEMBLED", vst, {"final_sha256": sha256_bytes(raw)})
    return dict(body, status="ASSEMBLED")


# ------------------------------------------------------ portable recovery (generation 2)
def _recovery_driver(spec):
    d = str(prod_ns(spec).parent / "p5y_k1_ps1_portable_recovery" / "driver")
    if d not in sys.path:
        sys.path.insert(0, d)
    import ps1_checkpoint as CK                                   # noqa: E402
    import host_guard as HG                                       # noqa: E402
    return CK, HG


def _generation(contract, role, st):
    ops = (st or {}).get(LO.OPS_FIELD) or {}
    return {"generation_id": "G2", "generation_index": 2, "host_role": role,
            "contract_sha256": contract["_sha256"],
            "runs": sorted((ops.get("runs") or {}))}


PREDECESSOR = {
    "production_authorization_commit": "29b3bffb6a739121b66bdfcb23cb6b6544b39baf",
    "halted_run_id": "20260912T041203Z-962132d3",
    "halted_ledger_sha256": "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab",
    "halt_reason": "RETRY_LIMIT",
    "halt_classification": "EXECUTION_LIFECYCLE_EXHAUSTION_NOT_A_SCIENTIFIC_COUNTEREXAMPLE",
    "historical_cpu_h": 92.32,
    "historical_finalized_cells": 0,
    "historical_patch_records": 24610,
    "historical_patch_records_status": "ARCHIVAL_ONLY_NEVER_SCIENTIFICALLY_ADMISSIBLE",
}


def cmd_drain(contract, role, wait_s=0.0) -> dict:
    """Cooperative drain. Deliberately does NOT take the campaign lock: a running campaign
    holds it. Writes the flag the launcher and workers poll at CELL boundaries only."""
    spec = host_spec(contract, role)
    # resolve from the CONTRACT runtime dir, never from the authorization: under a synthetic
    # contract the authorization still names the genuine work_dir, and a drain must never
    # touch genuine production state.
    work = Path(spec["runtime_dir"]) / "work"
    work.mkdir(parents=True, exist_ok=True)
    flag = work / "DRAIN"
    atomic_write(flag, canonical({"requested_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                  "role": role, "by": "prodctl drain"}))
    out = {"draining": True, "flag": str(flag),
           "semantics": ["no new cell admitted", "in-flight cells run to their boundary",
                         "each completed cell is finalized individually",
                         "GRACEFUL_DRAIN is not a tear: torn_attempts is not incremented"]}
    rt = RuntimeDir(spec)
    if wait_s > 0:
        t_end = time.monotonic() + wait_s
        while time.monotonic() < t_end:
            if LK.CampaignLock(rt, contract).probe() != LK.LIVE:
                out["settled"] = True
                break
            time.sleep(2.0)
        out.setdefault("settled", False)
    out["status"] = cmd_status(contract, role)
    return out


def _finalized_from_ledger(spec, contract, role):
    """Finalized cells are the SEALED per-cell records on disk, re-verified by hash."""
    PL, PP, _HO, M = frozen_prod(spec)
    auth = PL.load_production_authorization()
    cells_dir = prod_ns(spec) / "production" / "cells"
    fin = {}
    for p in sorted(cells_dir.glob("[0-9]*.json")):
        rec = read_json_strict(p)
        cell = int(rec["cell_id"])
        ev = {}
        for k, v in rec["evidence"].items():
            ep = Path(v["path"])
            if not ep.exists():
                raise OpsRefusal(f"finalized cell {cell}: evidence missing {ep}")
            got = sha256_file(ep)
            if got != v["sha256"]:
                raise OpsRefusal(f"finalized cell {cell}: evidence hash drift {ep}")
            ev[k] = {"sha256": got, "bytes": ep.stat().st_size, "path": str(ep)}
        fin[cell] = {"scientific_content_hash": rec["scientific_content_hash"],
                     "evidence": ev, "host": rec["role"], "run_id": rec.get("task_id"),
                     "cpu_seconds": rec["cpu_seconds"], "successor_id": rec.get("successor_id")}
    return fin, auth


def _build_checkpoint(contract, role, rt):
    spec = host_spec(contract, role)
    CK, _HG = _recovery_driver(spec)
    M, GB = frozen_accounting(spec)
    io = LO.LedgerIO(ledger_path(spec), M, GB, frozen_budget(spec, contract))
    st = io.read() or {}
    ops = st.get(LO.OPS_FIELD) or {}
    if st.get("open_reservations"):
        raise OpsRefusal(f"checkpoint refused: {len(st['open_reservations'])} open reservations; "
                         "drain or settle first")
    if LO.unsettled_runs(st, role):
        raise OpsRefusal(f"checkpoint refused: unsettled runs {LO.unsettled_runs(st, role)}")
    fin, auth = _finalized_from_ledger(spec, contract, role)
    owners = SV.owners_of(spec, contract)
    owned = sorted(c for c, r in owners.items() if r == role)
    pending = sorted(set(range(CK.TOTAL_CELLS)) - set(fin))
    committed = st.get("committed_cpu_h_by_role", {})
    gen_cpu = float(committed.get(role, 0.0))
    sci = sum(v["cpu_seconds"] for v in fin.values()) / 3600.0
    acc = {"historical_cpu_h": PREDECESSOR["historical_cpu_h"],
           "generation_cpu_h": gen_cpu,
           "cumulative_cpu_h": PREDECESSOR["historical_cpu_h"] + gen_cpu,
           "scientific_cpu_h": sci,
           "unattributed_cpu_h": PREDECESSOR["historical_cpu_h"] + max(0.0, gen_cpu - sci),
           "global_cap_cpu_h": contract["parent"]["global_cpu_cap"]}
    ck = CK.build(generation=_generation(contract, role, st),
                  predecessor=PREDECESSOR,
                  identities={"producer_commit": auth["producer_commit"],
                              "scientific_adapter_hash": auth["scientific_adapter_hash"],
                              "successor_cells_sha256": auth["successor_cells_sha256"],
                              "live_patches_sha256": auth["live_patches_sha256"],
                              "precision_bits": 256},
                  finalized=fin, pending=pending,
                  torn_lineage=ops.get("torn_attempts", {}),
                  accounting=acc,
                  runs=sorted((ops.get("runs") or {})),
                  hosts={role: {"role": role, "owned": len(owned)}},
                  evidence_root=Path(spec["runtime_dir"]) / "evidence",
                  ledger_continuity_sha256=sha256_file(ledger_path(spec)))
    return ck, CK


def _checkpoint(contract, role, rt, lock):
    ck, CK = _build_checkpoint(contract, role, rt)
    out = rt.root / "checkpoints"
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"checkpoint-{ck['checkpoint_content_sha256'][:12]}.json"
    write_json_atomic(p, ck)
    rep = CK.verify(ck, require_identities=ck["identities"])
    return {"checkpoint": str(p), "sha256": ck["checkpoint_content_sha256"],
            "finalized": len(ck["finalized_cells"]), "pending": len(ck["pending_cells"]),
            "verify": rep}


def _export(contract, role, rt, lock, output=None):
    spec = host_spec(contract, role)
    ck, CK = _build_checkpoint(contract, role, rt)
    auth = _auth(spec)
    src_root = Path(spec["runtime_dir"]) / "evidence"
    stage = Path(output) if output else (rt.root / "export")
    # normalise evidence into cell_XXXX/<name> so the bundle is location-independent
    norm = rt.root / "export_src"
    if norm.exists():
        import shutil as _sh
        _sh.rmtree(norm)
    for cell, meta in ck["finalized"].items():
        d = norm / f"cell_{int(cell):04d}"
        d.mkdir(parents=True, exist_ok=True)
        import shutil as _sh
        for name, e in meta["evidence"].items():
            _sh.copy2(e["path"], d / name)
    rep = CK.export_bundle(ck, evidence_root=norm, out_dir=stage)
    return {"export": rep, "source_evidence_root": str(src_root),
            "excluded": ["caches", "scratch", "archival torn patch records", "locks",
                         "journals", "process state", "temporary files"]}


def _resume(contract, role, rt, lock, ckpt=None):
    """Fail-closed governed resume. Verifies EVERYTHING before any expensive execution."""
    if not ckpt:
        raise OpsRefusal("resume requires --checkpoint <path to checkpoint.json or bundle dir>")
    spec = host_spec(contract, role)
    CK, HG = _recovery_driver(spec)
    p = Path(ckpt)
    if p.is_dir():
        rep_b = CK.verify_bundle(p)
        ck = json.loads((p / "checkpoint.json").read_text())
        ev_root = p / "evidence"
    else:
        ck = read_json_strict(p)
        rep_b = None
        ev_root = None
    auth = _auth(spec)
    want = {"producer_commit": auth["producer_commit"],
            "scientific_adapter_hash": auth["scientific_adapter_hash"],
            "successor_cells_sha256": auth["successor_cells_sha256"],
            "live_patches_sha256": auth["live_patches_sha256"],
            "precision_bits": 256}
    gates = {"checkpoint": CK.verify(ck, evidence_root=ev_root, require_identities=want)}
    PL, *_ = frozen_prod(spec)
    gates["executor_source_identity"] = (
        PL.executor_source_identity(Path(auth["hosts"][role]["production_root"])
                                    if "production_root" in auth["hosts"][role]
                                    else prod_ns(spec).parents[2])["EXECUTOR_HASH"]
        == auth["scientific_adapter_hash"])
    if not gates["executor_source_identity"]:
        raise OpsRefusal("resume refused: live executor is not the authorised executor")
    gates["probe"] = PL._probe(auth, role)
    if gates["probe"].get("precision_inside_scientific_context") != 256:
        raise OpsRefusal("resume refused: worker precision is not 256 bits")
    if not gates["probe"].get("thread_contract_ok"):
        raise OpsRefusal("resume refused: six-variable thread contract not in force")
    M, GB = frozen_accounting(spec)
    io = LO.LedgerIO(ledger_path(spec), M, GB, frozen_budget(spec, contract))
    st = io.read() or {}
    already = {int(c) for c in st.get("completed_cells", {})}
    dup = already & set(ck["finalized_cells"]) - already
    if dup:
        raise OpsRefusal(f"resume refused: duplicate finalized scheduling {sorted(dup)}")
    sched = [c for c in ck["pending_cells"] if c not in already]
    if set(sched) & set(ck["finalized_cells"]):
        raise OpsRefusal("resume refused: a finalized cell appears in the schedule")
    gates["host_maintenance"] = HG.gate(window_hours=float(contract.get("production_window_hours", 24)),
                                        contract_path=None, role=role, fail_closed=False)
    return {"resume": "VERIFIED_READY", "gates": gates, "bundle": rep_b,
            "schedule_only_pending": len(sched), "finalized_never_rescheduled": len(ck["finalized_cells"]),
            "historical_cpu_h_preserved": ck["accounting"]["historical_cpu_h"],
            "next": f"prodctl.py start --role {role}   (schedules pending cells only)"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=("render", "start", "stop", "status", "recover", "verify",
                                        "install-runtime-policy", "settle-fallback",
                                        "handoff-export", "handoff-import", "assemble",
                                        "drain", "checkpoint", "export", "resume"))
    ap.add_argument("--contract", default=None)
    ap.add_argument("--role", required=True, choices=("AWS", "VULTR"))
    ap.add_argument("--run-id")
    ap.add_argument("--from", dest="src")
    ap.add_argument("--output")
    ap.add_argument("--checkpoint", dest="ckpt")
    ap.add_argument("--wait", type=float, default=0.0)
    ap.add_argument("--drain-after-completed", dest="drain_after", type=int)
    a = ap.parse_args(argv)
    c = load_contract(a.contract)
    spec = host_spec(c, a.role)
    try:
        if a.command == "render":
            out = {"argv": render_start(c, a.role, a.run_id or "RUNID")}
        elif a.command == "start":
            out = cmd_start(c, a.role)
        elif a.command == "stop":
            out = cmd_stop(c, a.role)
        elif a.command == "status":
            out = cmd_status(c, a.role)
        elif a.command == "recover":
            out = with_lock(c, a.role, _recover)
        elif a.command == "verify":
            out = {"ops": SV.verify_ops_source(c), "parent": SV.verify_parent(c, spec)}
        elif a.command == "install-runtime-policy":
            out = {"install": RS.install_git_policy(spec["production_root"]),
                   "verify": RS.verify_git_policy(spec["production_root"])}
        elif a.command == "settle-fallback":
            out = with_lock(c, a.role, lambda *x: _settle_fallback(*x, run_id=a.run_id),
                            timeout_s=60.0)
        elif a.command == "handoff-export":
            out = with_lock(c, a.role, _handoff_export)
        elif a.command == "handoff-import":
            out = with_lock(c, a.role, lambda *x: _handoff_import(*x, src=a.src))
        elif a.command == "assemble":
            out = with_lock(c, a.role, _assemble)
        elif a.command == "drain":
            out = cmd_drain(c, a.role, wait_s=a.wait)
        elif a.command == "checkpoint":
            out = with_lock(c, a.role, _checkpoint)
        elif a.command == "export":
            out = with_lock(c, a.role, lambda *x: _export(*x, output=a.output))
        elif a.command == "resume":
            out = with_lock(c, a.role, lambda *x: _resume(*x, ckpt=a.ckpt))
    except Exception as exc:                                     # noqa: BLE001
        # every refusal -- ops or FROZEN (HandoffRefusal, MultiHostRefusal,
        # ProvenanceRefusal, ProductionRefusal, BudgetRefusal) -- fails closed identically
        print(json.dumps({"REFUSED": f"{type(exc).__name__}: {exc}"}, indent=1))
        return 30
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
