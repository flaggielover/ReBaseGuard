"""Sanctioned END-OF-CAMPAIGN SETTLEMENT of the new-glibc successor ledger. NON-CERTIFYING, RESULT-AGNOSTIC.

Why it exists. The frozen supervisor ends a campaign with DISPOSITION_<X> and marks its own run EXITED, but never settles
it: frozen reconcile skips the current run, and a terminal ledger is never reopened by a supervisor (the frozen supervisor
returns TERMINAL before reconciling, and preflight G17 refuses a terminal ledger). The frozen prov_integrity.audit
therefore reports D_unsettled_supervisor_runs on EVERY COMPLETE ledger, so the composite audit could never become
COMPLETE. The predecessor lineages settle through `prod_entry.py settle` / `prov_entry.py settle`; this module is the
successor's one sanctioned equivalent, reached only as `gs_entry.py settle`.

Model. Exactly the frozen prov_entry.py settle: the campaign flock, the authorization-bound ledger open, frozen
prod_ledger.reconcile (RUN_SETTLED) and frozen unmatched_overhead / op_charge_overhead (OVERHEAD_CHARGED). Nothing else
writes. What is added is a set of fail-closed preconditions, all checked read-only before the first ledger write:

  target     a successor universe (128-325 only); never a refused, predecessor, blocked, qualification or in-repository root
  ledger     exists (ABSENT and PRE_GENESIS are refused), born under this authorization, validates, terminal disposition
             (COMPLETE, HALTED or INCOMPLETE_BUDGET_EXHAUSTED), no open attempt, no sealed-but-unbound attempt, sealed
             record and bound envelope bytes unchanged
  host       no campaign process of any generation (argv-element scan) and the campaign flock is free
  evidence   every reaper line verifies; the one unsettled run is the latest run, EXITED, with exactly one keeper reap
             record whose exit code equals the disposition's exit code, taken after the run ended, whose rusage is not
             smaller than the CPU the ledger already charged to the run; a keeper exit record follows it

It never writes a record, an envelope, a cell, an attempt, the disposition, the halt, the cap or a predecessor file, and
it never admits. Settling a HALTED or budget-exhausted ledger closes its accounting only; it stays not adjudication-ready.

Idempotent. A settled ledger with no uncharged keeper exit is returned unchanged (ALREADY_SETTLED, no write). A crash
between the two transitions, or inside one, is repaired by the frozen ledger open and completed by the next call; the
frozen transitions charge each run and each reaper record at most once.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import gs_schema as GS
import gs_host as H
import prod_ledger as L
import prod_supervisor as PS
import prov_ledger as PL
from gs_spec import check_universe
from prod_common import Refusal
from prov_envelope import check_genesis

SETTLE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.settlement.v1"
SETTLE_VERSION = "gs-settle-r1"
SETTLE_COMMAND = "python -B level4/closure_proofs/p5y_k1_cusum_aux5_glibc_successor/code/gs_entry.py settle"
SETTLEMENT_EVENTS = ("RUN_SETTLED", "OVERHEAD_CHARGED")
QUALIFICATION_ROOTS = (GS.AUX5_NS / "evidence", GS.NS / "evidence", Path("/root/work/postk1-runs/aux5-qualification"),
                       Path("/root/work/postk1-runs/glibc-successor-q6"))
REPOSITORY_ROOTS = (GS.ROOT, GS.CHECKOUT_PATH, GS.PREDECESSOR_CHECKOUT_PATH)
UNCHANGED_KEYS = ("schema", "mode", "checkpoint_sha256", "campaign_id", "cap", "cells", "attempts", "accounting_exclusions",
                  "first_admission_wall", "halt", "disposition", "budget_exhaustion", "production_authorization")


def _under(root: Path, base: Path) -> bool:
    base = Path(os.path.abspath(base))
    return root == base or base in root.parents


def precheck_target(spec) -> None:
    """Refuses a wrong target before anything is opened, locked or loaded."""
    root = Path(os.path.abspath(spec.root))
    for r in GS.REFUSED_ROOTS:
        if _under(root, r):
            raise Refusal("REFUSED_ROOT", f"{root} is a predecessor or blocked runtime root; it is never settled")
    for r in QUALIFICATION_ROOTS:
        if _under(root, r):
            raise Refusal("QUALIFICATION_ROOT", f"{root} is qualification or requalification evidence, never a ledger to settle")
    for r in REPOSITORY_ROOTS:
        if _under(root, r):
            raise Refusal("REPOSITORY_ROOT", f"{root} lies inside a repository checkout")
    check_universe(spec.cell_indices)


def plan_settlement(st: dict, reaped: list, unreadable: int) -> dict:
    """Pure: what the frozen transitions will charge, or a refusal when the evidence is missing or contradictory."""
    if unreadable:
        raise Refusal("REAPER_UNREADABLE", f"{unreadable} reaper line(s) do not verify; settlement evidence is not trusted")
    runs = st["supervisor_runs"]
    unsettled = sorted(r for r, x in runs.items() if not x["settled"])
    plan = {"runs": {}, "overhead": []}
    if len(unsettled) > 1:
        raise Refusal("SETTLEMENT_EVIDENCE_CONTRADICTORY", f"a terminal ledger with {len(unsettled)} unsettled runs: {unsettled}")
    if unsettled:
        rid = unsettled[0]
        run = runs[rid]
        latest = max(runs, key=lambda r: runs[r]["started_wall"])
        if rid != latest or run["end"] != "EXITED" or run["ended_wall"] is None:
            raise Refusal("SETTLEMENT_EVIDENCE_CONTRADICTORY",
                          f"unsettled run {rid} is not the latest run that ended the campaign (end {run['end']!r})")
        cands = [r for r in reaped if r["kind"] == "CHILD_REAPED" and r["is_supervisor"] and r["pid"] == run["pid"]
                 and r["boot_id"] == run["boot_id"] and r["t_wall"] >= run["started_wall"] - 1]
        if not cands:
            raise Refusal("SETTLEMENT_EVIDENCE_MISSING", f"no keeper reap record for supervisor run {rid} (pid {run['pid']})")
        if len(cands) > 1:
            raise Refusal("SETTLEMENT_EVIDENCE_AMBIGUOUS", f"{len(cands)} keeper reap records match supervisor run {rid}")
        reap = cands[0]
        if L.match_run_reap(reaped, run) is not reap:
            raise Refusal("SETTLEMENT_EVIDENCE_CONTRADICTORY", "the frozen reap matcher disagrees")
        want_exit = PS.EXIT_FOR.get(st["disposition"])
        if reap["exited"] is not True or reap["exit_code"] != want_exit:
            raise Refusal("SETTLEMENT_EVIDENCE_CONTRADICTORY",
                          f"run {rid} reap exit {reap['exit_code']!r} does not match disposition {st['disposition']} ({want_exit})")
        if reap["t_wall"] < run["ended_wall"] - 1:
            raise Refusal("SETTLEMENT_EVIDENCE_CONTRADICTORY", f"run {rid} was reaped before it ended")
        seen = run["children_usec"] + run["self_cpu_seen_usec"]
        if reap["cpu_usec"] < seen:
            raise Refusal("SETTLEMENT_EVIDENCE_CONTRADICTORY",
                          f"run {rid} reap rusage {reap['cpu_usec']} < CPU already charged to it {seen}")
        keeper = [r for r in reaped if r["kind"] == "KEEPER_EXIT" and r["boot_id"] == run["boot_id"]
                  and r["t_wall"] >= reap["t_wall"] - 1 and r["record_id"] not in st["overhead_charges"]]
        if not keeper:
            raise Refusal("SETTLEMENT_EVIDENCE_MISSING", f"no uncharged keeper exit record follows supervisor run {rid}")
        plan["runs"][rid] = {"evidence": "REAPER_RUSAGE", "extra_usec": reap["cpu_usec"] - seen,
                             "reap_record_id": reap["record_id"], "reap_cpu_usec": reap["cpu_usec"]}
    plan["overhead"] = [list(x) for x in L.unmatched_overhead(reaped, st)]
    return plan


def _unchanged(st: dict) -> dict:
    return {**{k: st.get(k) for k in UNCHANGED_KEYS},
            "committed_non_supervisor": {b: v for b, v in st["committed_usec"].items() if b != "supervisor"}}


def settle_campaign(spec, authz, *, process_scan=None) -> dict:
    precheck_target(spec)
    root = Path(spec.root)
    p = L.Paths(root)
    if not p.ledger.exists() and not p.journal.exists():
        if not root.exists():
            raise Refusal("NO_LEDGER", f"{root} does not exist; there is nothing to settle")
        raise Refusal("PRE_GENESIS", f"{root} holds no ledger (PRE_GENESIS or refused-launch residue); nothing to settle")
    procs = (process_scan or H.foreign_campaign_processes)()
    if procs:
        raise Refusal("HOST_NOT_IDLE", f"a campaign process is running: {procs[:3]}")
    lock = L.CampaignLock(root)
    lock.acquire({"tool": "gs_entry settle", "version": SETTLE_VERSION, "pid": os.getpid(), "t_wall": time.time()})
    try:
        st0, entries0, _torn, relation = L.Ledger.read_and_relate(p)          # read-only: every refusal precedes a write
        L.validate_state(st0, spec)
        check_genesis(st0, entries0, authz)
        if st0["disposition"] not in L.TERMINAL:
            raise Refusal("NOT_TERMINAL", f"disposition {st0['disposition']}: a non-terminal ledger is settled by its next "
                                          "supervisor start, never by this command")
        if any(a["status"] in L.OPEN for a in st0["attempts"].values()):
            raise Refusal("TERMINAL_LEDGER_WITH_OPEN_ATTEMPT", "contradictory terminal ledger")
        if PL.unbound_sealed(st0):
            raise Refusal("TERMINAL_LEDGER_WITH_UNBOUND_SEAL", "contradictory terminal ledger; envelopes are never written here")
        sealed = L.verify_sealed_evidence(spec, st0)
        envelopes = PL.verify_bound_envelopes(spec, st0)
        reaped, unreadable = L.read_reaper(p)
        plan = plan_settlement(st0, reaped, unreadable)
        before, committed0 = _unchanged(st0), L.committed_total(st0)
        if not plan["runs"] and not plan["overhead"] and relation == "CONTINUOUS":
            return _report("ALREADY_SETTLED", spec, authz, st0, st0, plan, relation, sealed, envelopes)
        led = PL.ProvenanceLedger(spec, lock, authz=authz)
        led.open(allow_genesis=False)                                         # frozen crash repair (JOURNAL_BEHIND_ONE)
        rep = L.reconcile(led, reaped, unreadable)
        got = {r: {"evidence": v["evidence"], "extra_usec": v["extra_usec"]} for r, v in rep["runs"].items()}
        if rep["attempts"] or got != {r: {"evidence": v["evidence"], "extra_usec": v["extra_usec"]} for r, v in plan["runs"].items()}:
            raise Refusal("SETTLEMENT_DIVERGED", f"frozen reconcile {rep} differs from the verified plan {plan['runs']}")
        overhead = L.unmatched_overhead(reaped, led.state)
        if [list(x) for x in overhead] != plan["overhead"]:
            raise Refusal("SETTLEMENT_DIVERGED", "keeper overhead differs from the verified plan")
        if overhead:
            led.txn("OVERHEAD_CHARGED", lambda s: L.op_charge_overhead(s, overhead),
                    {"records": len(overhead), "tool": SETTLE_VERSION})
        st1 = led.state
        charged = sum(v["extra_usec"] for v in plan["runs"].values()) + sum(u for _r, u in plan["overhead"])
        if (_unchanged(st1) != before or L.committed_total(st1) - committed0 != charged
                or any(not x["settled"] for x in st1["supervisor_runs"].values())):
            raise Refusal("SETTLEMENT_INVARIANT_VIOLATED", "settlement changed more than run settlement and keeper overhead")
        return _report("SETTLED", spec, authz, st0, st1, plan, relation, sealed, envelopes)
    finally:
        lock.release()


def _report(state, spec, authz, st0, st1, plan, relation, sealed, envelopes) -> dict:
    return {"schema": SETTLE_SCHEMA, "version": SETTLE_VERSION, "state": state, "mode": spec.mode,
            "runtime_root": str(spec.root), "checkpoint_sha256": spec.checkpoint_sha256,
            "authorization_sha256": authz.block["authorization_sha256"], "disposition": st1["disposition"],
            "ledger_relation_at_open": relation, "runs_settled": plan["runs"],
            "overhead_records_charged": len(plan["overhead"]), "overhead_usec": sum(u for _r, u in plan["overhead"]),
            "committed_usec_before": L.committed_total(st0), "committed_usec_after": L.committed_total(st1),
            "cap_usec": st1["cap"]["cap_usec"], "seq_before": st0["seq"], "seq_after": st1["seq"],
            "state_sha256_after": L.state_sha256(st1), "sealed_records_verified": sealed, "bound_envelopes_verified": envelopes,
            "unsettled_after": sorted(r for r, x in st1["supervisor_runs"].items() if not x["settled"]),
            "records_envelopes_cells_disposition_cap_written": False}
