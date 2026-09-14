"""Synthetic acceptance scenarios, part A: pre-genesis, universe, predecessor evidence, Q6, countersignature, host,
boot, containment, CPU cap. NON-RESULT-BEARING."""
from __future__ import annotations

import copy
import json
import os
import shutil
import socket
import tempfile
from pathlib import Path

from gs_fixtures import (CACHE, GS, GSCampaign, PredFixture, PS, SP, attempts, check, composite, expect_refusal,
                         forge_next_state, real_checkpoint, refused_with, scenario)
import carryover_countersignature as CC
import glibc_successor as G
import gs_authorization as GA
import gs_entry as E
import gs_host as H
import prod_ledger as L
import q6_result as R
from prod_common import atomic_write_bytes, atomic_write_json, host_facts, sha256_bytes, sha256_file

FREEZE_DEPENDENT = {"G01_checkpoint_and_freeze", "G05_run_authorization", "G06_synthetic_acceptance"}


def live_overrides() -> dict:
    """The expensive live facts, collected once (read-only) and reused by the adversarial preflight calls."""
    if "live" not in CACHE:
        import prod_entry as PE
        import prov_integrity as PI
        cp, _sha = real_checkpoint()
        pspec, pauthz = E.predecessor_objects()
        CACHE["live"] = {"live_binding": G.collect(GS.ROOT), "predecessor_audit": PI.audit(pspec, pauthz),
                         "probe": PE.identity_probe(cp)[0], "host_identity": H.full_host_identity(),
                         "containment": H.containment_state(), "countersignature_problems": CC.verify_countersignature(),
                         "protected_trees": CC.check_git(CC.git_state, GS.ROOT), "processes": H.foreign_campaign_processes()}
    return copy.deepcopy(CACHE["live"])


def failing(rep: dict) -> dict:
    return {c["check"]: c.get("code") for c in rep["checks"] if c["status"] != "PASS"}


def preflight_fails_exactly(ov: dict, extra: set) -> dict:
    got = failing(E.preflight(overrides=ov))
    check(set(got) == FREEZE_DEPENDENT | set(extra), f"failing checks {got}, expected freeze-dependent + {sorted(extra)}")
    return got


# ====================================================================== scenarios
@scenario("pre-freeze launch preflight: every live check PASS; only freeze-dependent checks fail")
def a00_prefreeze_live_preflight(scratch):
    rep = E.preflight()
    got = failing(rep)
    check(set(got) == FREEZE_DEPENDENT and not rep["ready"] and rep["PRODUCTION_LAUNCH_AUTHORIZED"] is False,
          f"pre-freeze preflight failing {got}")
    check(got["G01_checkpoint_and_freeze"] == "NOT_FROZEN", f"G01 {got}")
    ov = live_overrides()
    check(not ov["processes"] and not ov["countersignature_problems"] and not ov["protected_trees"], "live facts clean")
    preflight_fails_exactly(ov, set())
    return {"failing_before_freeze": got, "passing": [c["check"] for c in rep["checks"] if c["status"] == "PASS"]}


@scenario("clean pre-genesis -> PASS", "cell 128 reservation -> PASS", "cell 325 reservation -> PASS",
          "refused launch leaves PRE_GENESIS residue only", "envelope binds the successor authorization and dd4c89d7")
def a01_clean_pregenesis_and_boundary_cells(scratch):
    import issuance as ISS
    c = GSCampaign(scratch, "a01", cells=[128, 129, 325], cores=[0, 2])
    host = socket.gethostname()
    check(ISS.classify_runtime_root(c.root, lock_state="FREE", bound_host=host)["state"] == "ABSENT", "fresh root absent")
    cs = Path(c.cfg["countersignature_path"])
    saved = cs.read_bytes()
    cs.unlink()
    code, out = c.run(keep=True)
    check(code == PS.EXIT_REFUSED and refused_with(out, "COUNTERSIGNATURE_MISSING") and not (c.root / "ledger.json").exists(),
          f"no genesis without the countersignature (exit {code})")
    rr = ISS.classify_runtime_root(c.root, lock_state="FREE", bound_host=host)
    check(rr["state"] == "PRE_GENESIS", f"refused launch residue {rr}")
    cs.write_bytes(saved)
    c.run_complete()
    st, entries = c.view()
    authz = c.authz()
    check(set(st["cells"]) == {"128", "129", "325"} and st["cap"]["cap_usec"] == c.spec.cap_usec, "universe and cap")
    check(entries[0]["detail"]["production_authorization"] == authz.block == st["production_authorization"]
          and authz.block["countersignature_sha256"] == sha256_bytes(saved), "authorization-born genesis")
    check(len(st["overhead_charges"]) == 3 and all(r["settled"] for r in st["supervisor_runs"].values()),
          f"refused supervisor + two keeper exits charged exactly once each: {st['overhead_charges']}")
    rep = c.audit()
    check(rep["INTEGRITY_READY_FOR_ADJUDICATION"] and len(rep["pairs"]) == 3, f"audit {rep['issues']}")
    for cell in (128, 325):
        (aid, a), = attempts(st, cell=cell, status="SEALED")
        env = json.loads((c.root / a["provenance"]["envelope"]).read_text())
        check(env["checkpoint"]["predecessor_checkpoint_sha256"] == G.EXPECTED["checkpoint_sha256"]
              and env["checkpoint"]["predecessor_status"] == GS.PREDECESSOR_STATUS
              and env["authorization"]["authorization_sha256"] == c.auth_sha, f"cell {cell} envelope bindings")
    return {"pre_genesis": rr["state"], "pairs": sorted(rep["pairs"]), "overhead_records": len(st["overhead_charges"])}


@scenario("old cell reservation 0-127 -> FAIL", "no recomputation of carry-over cells")
def a02_old_cells_refused(scratch):
    c = GSCampaign(scratch, "a02", cells=[128, 129])
    for cells in ([0], [127, 128], [5, 200]):
        expect_refusal("RECOMPUTATION_OF_CARRYOVER_CELL", SP.synthetic_spec, {**c.cfg, "cells": cells})
    atomic_write_json(c.cfg["config_path"], {**c.cfg, "cells": [127, 128]})
    code, out = c.run(keep=False)
    check(code == PS.EXIT_REFUSED and refused_with(out, "RECOMPUTATION_OF_CARRYOVER_CELL") and not c.root.exists(),
          f"a universe with a carry-over cell never opens a ledger (exit {code})")
    c.save()
    check(c.run(keep=True)[0] == PS.EXIT_COMPLETE, "the 128-325 campaign completes")
    st = copy.deepcopy(c.state())
    st["disposition"] = "OPEN"
    for cell in (0, 64, 127):
        expect_refusal("CELL_NOT_IN_UNIVERSE", L.op_reserve, copy.deepcopy(st), c.spec, cell, 4, "T")
    v = c.variant(scratch, "a02_forged_old_row")
    forge_next_state(v.root, lambda s: s["cells"].__setitem__("7", {"status": "SEALED", "attempt": None, "infra_tears": 0}))
    expect_refusal("LEDGER_CORRUPT", v.view)
    return {"spec": "RECOMPUTATION_OF_CARRYOVER_CELL", "op_reserve": "CELL_NOT_IN_UNIVERSE", "forged_row": "LEDGER_CORRUPT"}


@scenario("cell 326 -> FAIL", "production universe is exactly 128-325")
def a03_cell_326_refused(scratch):
    c = GSCampaign(scratch, "a03", cells=[128])
    expect_refusal("CELL_NOT_IN_UNIVERSE", SP.synthetic_spec, {**c.cfg, "cells": [326]})
    expect_refusal("CELL_NOT_IN_UNIVERSE", SP.check_universe, [128, 326])
    lock = L.CampaignLock(c.root)
    lock.acquire({"tool": "acceptance"})
    try:
        led = L.Ledger(c.spec, lock)
        led.open(allow_genesis=True)
        expect_refusal("CELL_NOT_IN_UNIVERSE", L.op_reserve, copy.deepcopy(led.state), c.spec, 326, 0, "T")
    finally:
        lock.release()
    cp, sha = real_checkpoint()
    spec = SP.spec_from_checkpoint(cp, sha)
    check(spec.cell_indices == list(range(128, 326)) and spec.cap_usec == GS.RESIDUAL_CAP_US, "production spec universe/cap")
    return {"production_universe": [spec.cell_indices[0], spec.cell_indices[-1]]}


@scenario("changed predecessor ledger hash -> FAIL")
def a04_changed_predecessor_ledger(scratch):
    ov = live_overrides()
    b = json.loads(GS.BINDING.read_bytes())
    live = copy.deepcopy(ov["live_binding"])
    live["files"]["ledger.json"] = "0" * 64
    check(G.compare_live(b, live), "compare_live refuses")
    preflight_fails_exactly({**ov, "live_binding": live}, {"G08_predecessor_binding_live"})
    files = {n: sha256_file(GS.PREDECESSOR_RUNTIME_ROOT / n) for n in ("ledger.json", "journal.jsonl", "reaper.jsonl")}
    preflight_fails_exactly({**ov, "predecessor_files": {**files, "ledger.json": "1" * 64}}, {"G09_predecessor_halted_immutable"})
    pred = PredFixture(scratch, "a04_pred", sealed=3, universe=8)
    pred.make_terminal()
    tol = pred.tolerance()
    succ_spec = GSCampaign(scratch, "a04_succ", cells=[128]).spec
    v = pred.variant(scratch, "a04_pred_edited")
    led = json.loads((v.root / "ledger.json").read_text())
    led["committed_usec"]["science"] += 1
    atomic_write_json(v.root / "ledger.json", led)
    expect_refusal("LEDGER_ROLLBACK_OR_MUTATION", composite, v, None, tol, succ_spec=succ_spec)
    return {"G08": "PREDECESSOR_CHANGED_SINCE_BINDING", "G09": "PREDECESSOR_EVIDENCE_CHANGED", "composite": "refused"}


@scenario("changed old pair -> FAIL")
def a05_changed_old_pair(scratch):
    ov = live_overrides()
    preflight_fails_exactly({**ov, "predecessor_digest": "2" * 64}, {"G09_predecessor_halted_immutable"})
    rep = copy.deepcopy(ov["predecessor_audit"])
    rep["pairs"]["17"]["record_sha256"] = "3" * 64
    preflight_fails_exactly({**ov, "predecessor_audit": rep}, {"G10_composite_predecessor_half"})
    pred = PredFixture(scratch, "a05_pred", sealed=3, universe=8)
    pred.make_terminal()
    tol = pred.tolerance()
    succ_spec = GSCampaign(scratch, "a05_succ", cells=[128]).spec
    check(composite(pred, None, tol, succ_spec=succ_spec)["state"] == "INCOMPLETE", "untouched fixture is INCOMPLETE")
    out = {}
    for name, target in (("record", "record"), ("envelope", "envelope")):
        v = pred.variant(scratch, f"a05_{name}")
        st = v.state()
        (aid, a), = attempts(st, cell=1, status="SEALED")
        path = v.root / (a["record"] if target == "record" else a["provenance"]["envelope"])
        os.chmod(path, 0o644)
        path.write_bytes(path.read_bytes().replace(b"{", b"{ ", 1))
        rep2 = composite(v, None, tol, succ_spec=succ_spec)
        check(rep2["state"] == "REFUSED" and any("PREDECESSOR_ISSUE_NOT_TOLERATED" in p for p in rep2["problems"]),
              f"{name}: {rep2['problems']}")
        out[name] = rep2["problems"][:2]
    return out


@scenario("missing Q6 -> FAIL")
def a06_missing_q6(scratch):
    d = Path(tempfile.mkdtemp(dir=scratch, prefix="a06_"))
    ns = d / "ns"
    shutil.copytree(GS.NS, ns, ignore=shutil.ignore_patterns("__pycache__"))
    (ns / R.RESULT_REL).unlink()
    check(R.verify_result(ns, GS.ROOT), "Q6 verifier refuses a missing result")
    check(CC.verify_countersignature(ns, GS.ROOT, git_reader=lambda _r: {"trees": dict(CC.PROTECTED_TREES),
                                                                        "ancestors": {k: True for k in CC.COMMITS},
                                                                        "dirty": []}), "countersignature refuses")
    q6 = G.evaluate_q6(None, json.loads((GS.NS / "config/Q6_REFERENCE.json").read_bytes()))
    cp, _sha = real_checkpoint()
    raw = GS.COUNTERSIGNATURE.read_bytes()
    rep = G.launch_readiness(proposal_problems=[], proposal_sha256=GS.PROPOSAL_SHA256, q6=q6, countersignature=json.loads(raw),
                             countersignature_sha256=sha256_bytes(raw), checkpoint=cp)
    check(rep["state"] == "NOT_READY" and "Q6_ABSENT" in rep["problems"], f"launch readiness {rep['problems']}")
    return {"launch_readiness": rep["problems"]}


@scenario("invalid countersignature -> FAIL")
def a07_invalid_countersignature(scratch):
    ov = live_overrides()
    preflight_fails_exactly({**ov, "countersignature_problems": ["COUNTERSIGNATURE_DOES_NOT_REBUILD"]},
                            {"G03_carryover_countersignature"})
    c = GSCampaign(scratch, "a07", cells=[128])
    cs = Path(c.cfg["countersignature_path"])
    cs.write_bytes(cs.read_bytes().replace(b"SYNTHETIC_ACCEPTANCE_FIXTURE", b"SOMEONE_ELSE", 1))
    code, out = c.run(keep=False)
    check(code == PS.EXIT_REFUSED and refused_with(out, "COUNTERSIGNATURE_INVALID") and not (c.root / "ledger.json").exists(),
          f"tampered fixture refused (exit {code})")
    cp, sha = real_checkpoint()
    spec = SP.spec_from_checkpoint(cp, sha)
    expect_refusal("COUNTERSIGNATURE_INVALID", GA.load_authz, spec, cp, auth_path=GS.AUTHORIZATION,
                   hash_path=GS.AUTHORIZATION_HASH, cs_path=cs, cs_verifier=lambda: [])
    expect_refusal("COUNTERSIGNATURE_INVALID", GA.load_authz, spec, cp, auth_path=GS.AUTHORIZATION,
                   hash_path=GS.AUTHORIZATION_HASH, cs_path=GS.COUNTERSIGNATURE, cs_verifier=lambda: ["FORGED"])
    return {"G03": "COUNTERSIGNATURE_INVALID", "synthetic": "COUNTERSIGNATURE_INVALID"}


@scenario("host drift -> FAIL")
def a08_host_drift(scratch):
    ov = live_overrides()
    preflight_fails_exactly({**ov, "host_identity": {**ov["host_identity"], "libc_sha256": "fa430b8f" + "0" * 56}},
                            {"G12_host_runtime_identity_and_boot"})
    libs = dict(ov["host_identity"]["system_libraries_sha256"])
    libs["/usr/lib/x86_64-linux-gnu/libm.so.6"] = "4" * 64
    preflight_fails_exactly({**ov, "host_identity": {**ov["host_identity"], "system_libraries_sha256": libs}},
                            {"G12_host_runtime_identity_and_boot"})
    out = {}
    for name, cfg in (("kernel", {"host_expected": {**host_facts(with_package=False), "kernel_release": "0.0.0-other"}}),
                      ("library", {"library_expected": libs})):
        c = GSCampaign(scratch, f"a08_{name}", cells=[128, 129], cores=[0], **cfg)
        code, _ = c.run(keep=False)
        st = c.state()
        check(code == PS.EXIT_HALTED and st["halt"]["reason"] == "HOST_DRIFT" and not st["attempts"],
              f"{name}: drift halts before any admission (exit {code})")
        out[name] = "HOST_DRIFT"
    return out


@scenario("boot-id change -> FAIL", "reboot or provider maintenance fails closed")
def a09_boot_change(scratch):
    ov = live_overrides()
    preflight_fails_exactly({**ov, "host_identity": {**ov["host_identity"], "boot_id": "00000000-0000-0000-0000-000000000000"}},
                            {"G12_host_runtime_identity_and_boot"})
    c = GSCampaign(scratch, "a09", cells=[128, 129], cores=[0], boot_expected="00000000-0000-0000-0000-000000000000")
    code, _ = c.run(keep=False)
    st = c.state()
    check(code == PS.EXIT_HALTED and st["halt"]["reason"] == "HOST_DRIFT" and not st["attempts"], f"exit {code}")
    return {"G12": "HOST_DRIFT", "admission_guard": "HOST_DRIFT"}


@scenario("containment removed -> FAIL")
def a10_containment_removed(scratch):
    ov = live_overrides()
    for name, mutate in (("holds", lambda s: s.__setitem__("holds", [])),
                         ("dropin", lambda s: s.__setitem__("freeze_dropin", {**s["freeze_dropin"], "exists": False, "content": None})),
                         ("timer", lambda s: s["units"].__setitem__("apt-daily-upgrade.timer", {"enabled": "enabled", "active": "active"}))):
        st = copy.deepcopy(ov["containment"])
        mutate(st)
        preflight_fails_exactly({**ov, "containment": st}, {"G11_containment"})
    return {"holds": "CONTAINMENT_NOT_APPLIED", "dropin": "CONTAINMENT_NOT_APPLIED", "timer": "CONTAINMENT_NOT_APPLIED"}


def _checkpoint_copy(scratch: Path, name: str, mutate) -> tuple[Path, Path]:
    cp, _sha = real_checkpoint()
    bad = copy.deepcopy(cp)
    mutate(bad["cost_cap"])
    d = scratch / name
    d.mkdir()
    data = (json.dumps(bad, indent=1, sort_keys=True) + "\n").encode()
    atomic_write_bytes(d / "cp.json", data)
    atomic_write_bytes(d / "cp.hash", (sha256_bytes(data) + "\n").encode())
    return d / "cp.json", d / "cp.hash"


@scenario("fresh 300 CPU-h reset -> FAIL", "altered residual cap -> FAIL", "omitting predecessor consumption -> FAIL",
          "raising the absolute cap -> FAIL", "changing the invariant -> FAIL", "double charging -> FAIL",
          "undercharging predecessor settlement -> FAIL")
def a11_cap_continuity(scratch):
    abs_, settled, resid = GS.ABSOLUTE_CAP_US, GS.PREDECESSOR_SETTLED_US, GS.RESIDUAL_CAP_US
    cases = {"reset_300": ({"cap_usec": abs_, "successor_residual_cap_usec": abs_}, "CAP_RESET_FORBIDDEN"),
             "residual": ({"cap_usec": resid - 1}, "CAP_RESIDUAL_CHANGED"),
             "omit_predecessor": ({"predecessor_settled_usec": 0}, "CAP_PREDECESSOR_CONSUMPTION"),
             "raise_absolute": ({"absolute_campaign_cap_usec": abs_ + 3_600_000_000}, "CAP_ABSOLUTE_CHANGED"),
             "invariant": ({"invariant": [100, 100]}, "CAP_INVARIANT_CHANGED"),
             "double_charge": ({"cap_usec": abs_ - 2 * settled, "successor_residual_cap_usec": abs_ - 2 * settled},
                               "CAP_RESIDUAL_CHANGED"),
             "undercharge": ({"predecessor_settled_usec": settled - 71506 - 70947}, "CAP_PREDECESSOR_CONSUMPTION")}
    for name, (delta, want) in cases.items():
        p, h = _checkpoint_copy(scratch, f"a11_{name}", lambda cc, d=delta: cc.update(d))
        expect_refusal(want, SP.load_checkpoint, p, h, root=GS.ROOT)
    cp, sha = real_checkpoint()
    spec = SP.spec_from_checkpoint(cp, sha)
    auth, _asha = GA.load_authorization(GS.AUTHORIZATION, GS.AUTHORIZATION_HASH)
    spec.cap_usec = GS.ABSOLUTE_CAP_US
    expect_refusal("AUTHORIZATION_MISMATCH", GA.verify_authorization, auth, spec, cp)
    c = GSCampaign(scratch, "a11_ledger", cells=[128, 129], cores=[0], cap_usec=resid)
    check(c.run(keep=True)[0] == PS.EXIT_COMPLETE, "ledger born against the residual cap")
    check(c.state()["cap"]["cap_usec"] == resid, "genesis cap == residual")
    seq = c.state()["seq"]
    c.cfg["cap_usec"] = abs_
    c.save()
    code, out = c.run(keep=False)
    check(code == PS.EXIT_REFUSED and (refused_with(out, "AUTHORIZATION_MISMATCH") or refused_with(out, "CAP_CHANGE_FORBIDDEN"))
          and c.state()["seq"] == seq, f"cap reset on a live ledger refused without mutation (exit {code})")
    forged = copy.deepcopy(c.state())
    forged["cap"]["cap_usec"] = abs_
    expect_refusal("CAP_CHANGE_FORBIDDEN", L.validate_state, forged, SP.synthetic_spec({**c.cfg, "cap_usec": resid}))
    return {k: v[1] for k, v in cases.items()} | {"ledger_cap_reset": "refused (authorization recomputation / CAP_CHANGE_FORBIDDEN)"}


@scenario("CPU cap exhaustion -> FAIL (terminal, no further admission)")
def a12_cap_exhaustion(scratch):
    c = GSCampaign(scratch, "a12", cells=list(range(128, 140)), cores=[0], cap_usec=4_000_000, reservation_usec=1_000_000,
                   burn_s=0.3)
    code, out = c.run(keep=True)
    check(code == PS.EXIT_BUDGET, f"exit {code}: {out[-300:]}")
    st = c.state()
    seq = st["seq"]
    check(st["disposition"] == "INCOMPLETE_BUDGET_EXHAUSTED" and st["budget_exhaustion"]["pending_cells"], "budget disposition")
    check(c.run(keep=False)[0] == PS.EXIT_BUDGET and c.state()["seq"] == seq, "never admits again")
    rep = c.audit()
    check(not rep["INTEGRITY_READY_FOR_ADJUDICATION"], "an exhausted successor is never adjudication-ready")
    return {"sealed": sum(1 for x in st["cells"].values() if x["status"] == "SEALED")}
