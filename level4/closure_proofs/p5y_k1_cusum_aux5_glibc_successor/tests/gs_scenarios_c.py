"""Synthetic acceptance scenarios, part C: END-OF-CAMPAIGN SETTLEMENT through the sanctioned operator command
`gs_entry.py settle`. NON-RESULT-BEARING.

Every settlement below is the real command in a fresh interpreter (gs_fixtures.sanctioned_settle). No scenario settles,
reconciles or charges a ledger through a helper. The crash scenarios run the same command with one frozen ledger method
patched to exit the process mid-settlement.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

from gs_fixtures import (GS, NS, Fail, GSCampaign, PredFixture, PS, attempts, check, composite, count, expect_refusal,
                         forge_next_state, real_checkpoint, sanctioned_settle, sanctioned_settle_production, scenario,
                         settle_refused, settlement_bypass_scan, tree_digest)
import gs_composite as GC
import gs_host as H
import gs_settle as ST
import prod_ledger as L
from prod_common import atomic_write_json, canonical, sha256_bytes, sha256_file


# ====================================================================== helpers (read-only or adversarial fixtures)
def unsettled(st: dict) -> list:
    return sorted(r for r, x in st["supervisor_runs"].items() if not x["settled"])


def ledger_bytes(c) -> tuple:
    return tuple((c.root / n).read_bytes() if (c.root / n).exists() else None for n in ("ledger.json", "journal.jsonl"))


def finished_unsettled(scratch: Path, name: str, **cfg) -> GSCampaign:
    """A synthetic successor run to COMPLETE by the frozen supervisor under its keeper, and not settled."""
    c = GSCampaign(scratch, name, **{"cells": [128, 129], "cores": [0], **cfg})
    code, out = c.run(keep=True)
    check(code == PS.EXIT_COMPLETE, f"{name}: exit {code}: {out[-300:]}")
    st = c.state()
    check(len(unsettled(st)) == 1, f"{name}: the frozen supervisor leaves exactly its final run unsettled: {unsettled(st)}")
    rep = c.audit()
    check(sorted(rep["issues"]) == ["D_unsettled_supervisor_runs"] and not rep["INTEGRITY_READY_FOR_ADJUDICATION"],
          f"{name}: before settlement {sorted(rep['issues'])}")
    return c


def refused_unchanged(target, code: str, what: str, c=None) -> str:
    c = target if c is None else c
    before = ledger_bytes(c)
    rc, out, _rep = sanctioned_settle(target)
    check(rc == PS.EXIT_REFUSED and settle_refused(out, code), f"{what}: expected {code}, got rc {rc}: {out[-400:]}")
    check(ledger_bytes(c) == before, f"{what}: a refused settlement never writes the ledger or the journal")
    return code


def reaper_records(c) -> list:
    return [json.loads(x) for x in (c.root / "reaper.jsonl").read_text().splitlines() if x.strip()]


def write_reaper(c, recs: list) -> None:
    (c.root / "reaper.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in recs))


def resign(rec: dict) -> dict:
    """An adversary who also recomputes the reaper record id."""
    body = {k: v for k, v in rec.items() if k != "record_id"}
    return {**body, "record_id": sha256_bytes(canonical(body))}


def final_run(c) -> tuple:
    st = c.state()
    rid = unsettled(st)[0]
    return rid, st["supervisor_runs"][rid]


def is_final_reap(r: dict, run: dict) -> bool:
    return r["kind"] == "CHILD_REAPED" and r["is_supervisor"] and r["pid"] == run["pid"]


def mutate_final_reap(c, fn, *, signed: bool = True) -> None:
    _rid, run = final_run(c)
    recs = []
    for r in reaper_records(c):
        if is_final_reap(r, run):
            r = fn(dict(r))
            r = resign(r) if signed else r
        recs.append(r)
    write_reaper(c, recs)


def expected_charge(c) -> int:
    """Computed here, independently of gs_settle: reap - children - self for the final run, plus every uncharged keeper exit."""
    st = c.state()
    _rid, run = final_run(c)
    recs = reaper_records(c)
    (reap,) = [r for r in recs if is_final_reap(r, run)]
    keeper = [r for r in recs if r["kind"] == "KEEPER_EXIT" and r["record_id"] not in st["overhead_charges"]]
    return reap["cpu_usec"] - run["children_usec"] - run["self_cpu_seen_usec"] + sum(r["cpu_usec"] for r in keeper)


def settle_crashing(c, patch: str) -> int:
    script = (f"import os, sys\nsys.path.insert(0, {str(NS / 'code')!r})\nimport gs_entry\nimport prod_ledger as L\n{patch}\n"
              f"raise SystemExit(gs_entry.main(['settle', '--synthetic-spec', {c.cfg['config_path']!r}]))\n")
    env = {k: v for k, v in os.environ.items() if k != PS.KEEPER_ENV}
    return subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True, timeout=300, env=env).returncode


def owner_pid(c) -> int:
    return json.loads((c.root / "campaign.owner.json").read_text())["pid"]


def wait_idle(timeout: float = 20) -> None:
    deadline = time.monotonic() + timeout
    while H.foreign_campaign_processes() and time.monotonic() < deadline:
        time.sleep(0.2)
    check(H.foreign_campaign_processes() == [], "host idle again")


CRASH_BETWEEN_TRANSITIONS = ("orig = L.Ledger.txn\n"
                             "def txn(self, event, mutate, detail=None):\n"
                             "    if event == 'OVERHEAD_CHARGED':\n"
                             "        os._exit(97)\n"
                             "    return orig(self, event, mutate, detail)\n"
                             "L.Ledger.txn = txn")
CRASH_INSIDE_RUN_SETTLED = ("orig = L.Ledger._append_journal\n"
                            "def append(self, prev, st, event, detail):\n"
                            "    if event == 'RUN_SETTLED':\n"
                            "        os._exit(98)\n"
                            "    return orig(self, prev, st, event, detail)\n"
                            "L.Ledger._append_journal = append")


# ====================================================================== scenarios
@scenario("COMPLETE + one unsettled final supervisor run -> sanctioned settle -> settled -> audit ready",
          "settlement charges REAPER_RUSAGE exactly (reap - children - self) plus the keeper exit, once",
          "settlement never alters records, envelopes, cells, attempts, disposition, halt or cap")
def c01_complete_settle_audit_ready(scratch):
    c = finished_unsettled(scratch, "c01", cells=[128, 129, 130], cores=[0, 2])
    st0, n0, digest0 = c.state(), len(c.journal()), tree_digest(c.root)
    rid, _run = final_run(c)
    want = expected_charge(c)
    rc, out, rep = sanctioned_settle(c)
    check(rc == 0 and rep["state"] == "SETTLED" and set(rep["runs_settled"]) == {rid}, f"settle rc {rc}: {out[-400:]}")
    st1 = c.state()
    run = st1["supervisor_runs"][rid]
    check(run["settled"] and run["settlement"]["evidence"] == "REAPER_RUSAGE" and run["end"] == "EXITED", f"run {rid}: {run}")
    check(L.committed_total(st1) - L.committed_total(st0) == want == rep["committed_usec_after"] - rep["committed_usec_before"],
          f"charged {L.committed_total(st1) - L.committed_total(st0)} != independent {want}")
    for k in ST.UNCHANGED_KEYS:
        check(st1[k] == st0[k], f"settlement changed {k}")
    check({b: v for b, v in st1["committed_usec"].items() if b != "supervisor"}
          == {b: v for b, v in st0["committed_usec"].items() if b != "supervisor"}, "only the supervisor bucket moves")
    check(tree_digest(c.root) == digest0, "record, envelope and worker files are byte-identical")
    check([e["event"] for e in c.journal()[n0:]] == list(ST.SETTLEMENT_EVENTS), "exactly the two frozen transitions")
    audit = c.audit()
    check(audit["INTEGRITY_READY_FOR_ADJUDICATION"] and not audit["issues"] and len(audit["pairs"]) == 3, f"audit {audit['issues']}")
    return {"run": rid, "charged_usec": want, "events": list(ST.SETTLEMENT_EVENTS), "audit": "INTEGRITY_READY_FOR_ADJUDICATION"}


@scenario("settle twice -> no double CPU charge", "settlement is idempotent")
def c02_settle_twice_idempotent(scratch):
    c = finished_unsettled(scratch, "c02")
    rc, out, rep = sanctioned_settle(c)
    check(rc == 0 and rep["state"] == "SETTLED", out[-300:])
    frozen = ledger_bytes(c)
    for i in (2, 3):
        rc, out, again = sanctioned_settle(c)
        check(rc == 0 and again["state"] == "ALREADY_SETTLED" and again["committed_usec_after"] == rep["committed_usec_after"]
              and not again["runs_settled"] and again["overhead_records_charged"] == 0, f"settle #{i}: {out[-300:]}")
        check(ledger_bytes(c) == frozen, f"settle #{i} wrote the ledger")
    return {"first": rep["state"], "second_and_third": "ALREADY_SETTLED", "committed_usec": rep["committed_usec_after"]}


@scenario("crash during settlement -> repeatable, idempotent recovery, charged exactly once")
def c03_crash_during_settlement(scratch):
    out = {}
    for name, patch, code, relation in (("between_transitions", CRASH_BETWEEN_TRANSITIONS, 97, "CONTINUOUS"),
                                        ("inside_run_settled", CRASH_INSIDE_RUN_SETTLED, 98, "JOURNAL_BEHIND_ONE")):
        c = finished_unsettled(scratch, f"c03_{name}")
        st0, want = c.state(), expected_charge(c)
        rc = settle_crashing(c, patch)
        check(rc == code, f"{name}: crash harness exit {rc}")
        got = L.Ledger.read_and_relate(L.Paths(c.root))[3]
        check(got == relation, f"{name}: ledger relation after the crash {got}")
        rc, o, rep = sanctioned_settle(c)
        check(rc == 0 and rep["state"] == "SETTLED" and rep["ledger_relation_at_open"] == relation, f"{name}: recovery {o[-300:]}")
        st1 = c.state()
        check(L.committed_total(st1) - L.committed_total(st0) == want,
              f"{name}: charged {L.committed_total(st1) - L.committed_total(st0)} != {want}")
        check(not unsettled(st1) and len(st1["overhead_charges"]) == len(st0["overhead_charges"]) + 1, f"{name}: charged once")
        events = [e["event"] for e in c.journal()]
        check(events.count("RUN_SETTLED") == 1 and events.count("OVERHEAD_CHARGED") == 1, f"{name}: journal {events[-4:]}")
        rc, o, again = sanctioned_settle(c)
        check(rc == 0 and again["state"] == "ALREADY_SETTLED", f"{name}: settle after recovery {o[-200:]}")
        check(c.audit()["INTEGRITY_READY_FOR_ADJUDICATION"], f"{name}: adjudication-ready after recovery")
        out[name] = {"relation_after_crash": relation, "charged_usec": want}
    return out


@scenario("non-terminal ledger (crashed OPEN, DRAINED) -> settlement refused", "live campaign lock -> settlement refused",
          "ABSENT or PRE_GENESIS successor root -> settlement refused")
def c04_refused_unless_terminal_ledger(scratch):
    out = {}
    a = GSCampaign(scratch, "c04_absent", cells=[128])
    out["absent"] = refused_unchanged(a, "NO_LEDGER", "absent root")
    check(not a.root.exists(), "a refused settlement creates no runtime root")
    g = GSCampaign(scratch, "c04_pregenesis", cells=[128])
    cs = Path(g.cfg["countersignature_path"])
    saved = cs.read_bytes()
    cs.unlink()
    code, _ = g.run(keep=True)
    check(code == PS.EXIT_REFUSED and not (g.root / "ledger.json").exists(), f"refused launch exit {code}")
    cs.write_bytes(saved)
    names = sorted(x.name for x in g.root.iterdir())
    out["pre_genesis"] = refused_unchanged(g, "PRE_GENESIS", "pre-genesis residue")
    check(sorted(x.name for x in g.root.iterdir()) == names, "pre-genesis residue untouched")
    k = finished_unsettled(scratch, "c04_locked")
    holder = subprocess.Popen([sys.executable, "-c", "import fcntl, os, sys, time\nfd = os.open(sys.argv[1], os.O_RDWR)\n"
                               "fcntl.flock(fd, fcntl.LOCK_EX)\nprint('held', flush=True)\ntime.sleep(120)\n",
                               str(k.root / "campaign.lock")], stdout=subprocess.PIPE, text=True)
    try:
        check(holder.stdout.readline().strip() == "held", "lock holder started")
        out["lock_held"] = refused_unchanged(k, "ANOTHER_SUPERVISOR_LIVE", "campaign lock held")
    finally:
        holder.kill()
        holder.wait()
    crashed = GSCampaign(scratch, "c04_crashed", cells=[128, 129], cores=[0], plan={"128": ["hang"]})
    p = crashed.start(keep=True)
    crashed.wait_for(lambda s: attempts(s, cell=128, status="RUNNING"), what="cell 128 running")
    os.kill(owner_pid(crashed), signal.SIGKILL)
    crashed.finish(p)
    wait_idle()
    check(crashed.state()["disposition"] == "OPEN", "a crashed supervisor leaves an OPEN ledger")
    out["open_after_crash"] = refused_unchanged(crashed, "NOT_TERMINAL", "crashed OPEN ledger")
    d = GSCampaign(scratch, "c04_drained", cells=list(range(128, 134)), cores=[0], plan={str(i): ["slow"] for i in range(128, 134)},
                   slow_s=1.0)
    p = d.start(keep=True)
    d.wait_for(lambda s: attempts(s, status="RUNNING"), what="drain candidate running")
    os.kill(p.pid, signal.SIGTERM)
    check(d.finish(p)[0] == PS.EXIT_DRAINED, "drained")
    out["drained"] = refused_unchanged(d, "NOT_TERMINAL", "DRAINED ledger")
    return out


@scenario("active supervisor or worker on the host -> settlement refused")
def c05_refused_while_campaign_process_runs(scratch):
    a = finished_unsettled(scratch, "c05_target")
    b = GSCampaign(scratch, "c05_busy", cells=[128, 129], cores=[0], plan={"128": ["slow"]}, slow_s=6.0)
    p = b.start(keep=True)
    try:
        b.wait_for(lambda s: attempts(s, status="RUNNING"), what="busy campaign running")
        check(any(f["kind"] == "SUPERVISOR_OR_WORKER" for f in H.foreign_campaign_processes()), "busy campaign is visible")
        code = refused_unchanged(a, "HOST_NOT_IDLE", "another campaign running")
    finally:
        done = b.finish(p)[0]
    check(done == PS.EXIT_COMPLETE, "busy campaign completes")
    wait_idle()
    rc, out, rep = sanctioned_settle(a)
    check(rc == 0 and rep["state"] == "SETTLED", f"settles once the host is idle: {out[-300:]}")
    return {"while_busy": code, "once_idle": rep["state"]}


def _drop_final_reap(c):
    _rid, run = final_run(c)
    write_reaper(c, [r for r in reaper_records(c) if not is_final_reap(r, run)])


def _drop_keeper_exit(c):
    write_reaper(c, [r for r in reaper_records(c) if r["kind"] != "KEEPER_EXIT"])


def _duplicate_final_reap(c):
    _rid, run = final_run(c)
    recs = reaper_records(c)
    (reap,) = [r for r in recs if is_final_reap(r, run)]
    write_reaper(c, recs + [resign({**reap, "t_wall": reap["t_wall"] + 0.5})])


def _append_unreadable_line(c):
    with open(c.root / "reaper.jsonl", "a") as f:
        f.write("{not a reaper record\n")


@scenario("missing reaper evidence -> fail closed", "malformed reaper evidence -> fail closed",
          "ambiguous reaper evidence -> fail closed")
def c06_reaper_evidence_missing_or_malformed(scratch):
    cases = {"reaper_file_deleted": (lambda c: (c.root / "reaper.jsonl").unlink(), "SETTLEMENT_EVIDENCE_MISSING"),
             "unreadable_line": (_append_unreadable_line, "REAPER_UNREADABLE"),
             "supervisor_reap_removed": (_drop_final_reap, "SETTLEMENT_EVIDENCE_MISSING"),
             "keeper_exit_removed": (_drop_keeper_exit, "SETTLEMENT_EVIDENCE_MISSING"),
             "supervisor_reap_duplicated": (_duplicate_final_reap, "SETTLEMENT_EVIDENCE_AMBIGUOUS")}
    out = {}
    for name, (mutate, code) in cases.items():
        c = finished_unsettled(scratch, f"c06_{name}", cells=[128])
        mutate(c)
        out[name] = refused_unchanged(c, code, name)
        check(unsettled(c.state()) and not c.audit()["INTEGRITY_READY_FOR_ADJUDICATION"], f"{name}: still not adjudication-ready")
    return out


@scenario("altered supervisor run identity -> fail closed", "a foreign authorization -> settlement refused")
def c07_run_identity_altered(scratch):
    def forge_pid(c):
        rid, run = final_run(c)
        forge_next_state(c.root, lambda s: s["supervisor_runs"][rid].__setitem__("pid", run["pid"] + 1))

    def edit_ledger_json(c):
        rid, run = final_run(c)
        st = c.state()
        st["supervisor_runs"][rid]["pid"] = run["pid"] + 1
        atomic_write_json(c.root / "ledger.json", st)
    cases = {"reap_pid_altered": (lambda c: mutate_final_reap(c, lambda r: {**r, "pid": r["pid"] + 1}),
                                  "SETTLEMENT_EVIDENCE_MISSING"),
             "reap_boot_altered": (lambda c: mutate_final_reap(c, lambda r: {**r, "boot_id": "00000000-0000-0000-0000-000000000000"}),
                                   "SETTLEMENT_EVIDENCE_MISSING"),
             "reap_exit_code_altered": (lambda c: mutate_final_reap(c, lambda r: {**r, "exit_code": PS.EXIT_HALTED}),
                                        "SETTLEMENT_EVIDENCE_CONTRADICTORY"),
             "ledger_run_pid_forged_consistently": (forge_pid, "SETTLEMENT_EVIDENCE_MISSING"),
             "ledger_json_edited_under_journal": (edit_ledger_json, "LEDGER_ROLLBACK_OR_MUTATION")}
    out = {}
    for name, (mutate, code) in cases.items():
        c = finished_unsettled(scratch, f"c07_{name}", cells=[128])
        mutate(c)
        out[name] = refused_unchanged(c, code, name)
    c = finished_unsettled(scratch, "c07_foreign_authorization", cells=[128])
    other = GSCampaign(scratch, "c07_other", cells=[128])
    c.cfg.update(authorization_path=other.cfg["authorization_path"], authorization_hash_path=other.cfg["authorization_hash_path"])
    c.save()
    out["foreign_authorization"] = refused_unchanged(c, "AUTHORIZATION_MISMATCH", "foreign authorization")
    return out


@scenario("altered CPU / rusage accounting -> fail closed")
def c08_cpu_accounting_altered(scratch):
    def forge_committed(c):
        forge_next_state(c.root, lambda s: s["committed_usec"].__setitem__("science", s["committed_usec"]["science"] + 1))

    def forge_children(c):
        rid, run = final_run(c)
        (reap,) = [r for r in reaper_records(c) if is_final_reap(r, run)]
        forge_next_state(c.root, lambda s: s["supervisor_runs"][rid].__setitem__("children_usec", reap["cpu_usec"] + 1))
    cases = {"reap_rusage_below_charged": (lambda c: mutate_final_reap(c, lambda r: {**r, "cpu_usec": 0}),
                                           "SETTLEMENT_EVIDENCE_CONTRADICTORY"),
             "reap_rusage_edited_unsigned": (lambda c: mutate_final_reap(c, lambda r: {**r, "cpu_usec": r["cpu_usec"] + 1000},
                                                                         signed=False), "REAPER_UNREADABLE"),
             "ledger_committed_forged": (forge_committed, "ACCOUNTING_CORRUPT"),
             "ledger_run_children_forged": (forge_children, "SETTLEMENT_EVIDENCE_CONTRADICTORY")}
    out = {}
    for name, (mutate, code) in cases.items():
        c = finished_unsettled(scratch, f"c08_{name}", cells=[128])
        mutate(c)
        out[name] = refused_unchanged(c, code, name)
    return out


@scenario("predecessor runtime passed accidentally -> refused", "a predecessor-shaped ledger is never settled by the successor")
def c09_predecessor_runtime_refused(scratch):
    b = json.loads(GS.BINDING.read_bytes())
    before = {n: sha256_file(GS.PREDECESSOR_RUNTIME_ROOT / n) for n in b["files"]}
    c = GSCampaign(scratch, "c09_cfg", cells=[128])
    out = {}
    for label, root in (("predecessor_root", GS.PREDECESSOR_RUNTIME_ROOT), ("blocked_root", GS.BLOCKED_RUNTIME_ROOT),
                        ("successor_production_root", GS.SUCCESSOR_RUNTIME_ROOT)):
        cfgp = scratch / f"c09_{label}.json"
        atomic_write_json(cfgp, {**c.cfg, "root": str(root), "config_path": str(cfgp)})
        rc, o, _rep = sanctioned_settle(cfgp)
        check(rc == PS.EXIT_REFUSED and settle_refused(o, "SYNTHETIC_PRODUCTION_MIX"), f"{label}: {o[-300:]}")
        out[label] = "SYNTHETIC_PRODUCTION_MIX"
    for root in (GS.PREDECESSOR_RUNTIME_ROOT, GS.BLOCKED_RUNTIME_ROOT / "x"):
        expect_refusal("REFUSED_ROOT", ST.precheck_target, SimpleNamespace(root=root, cell_indices=[128]))
    pred = PredFixture(scratch, "c09_pred", sealed=2, universe=6)
    pred.make_terminal()
    out["predecessor_shaped_ledger"] = refused_unchanged(pred, "PREDECESSOR_RUNTIME_REFUSED", "predecessor-shaped ledger")
    check(unsettled(pred.state()), "the predecessor-shaped run stays unsettled")
    cfgp = scratch / "c09_pred_unmarked.json"
    atomic_write_json(cfgp, {**{k: v for k, v in pred.cfg.items() if k != "predecessor_shape"}, "config_path": str(cfgp)})
    out["predecessor_cells_unmarked"] = refused_unchanged(cfgp, "RECOMPUTATION_OF_CARRYOVER_CELL", "unmarked predecessor cells", c=pred)
    check({n: sha256_file(GS.PREDECESSOR_RUNTIME_ROOT / n) for n in b["files"]} == before and not GS.SUCCESSOR_RUNTIME_ROOT.exists(),
          "real predecessor runtime unchanged; successor root absent")
    return out


@scenario("qualification runtime passed accidentally -> refused", "no settlement target inside a repository checkout")
def c10_qualification_runtime_refused(scratch):
    cp, _sha = real_checkpoint()
    fw = cp["qualification_firewall"]["record_file_sha256"]
    c = GSCampaign(scratch, "c10_cfg", cells=[128])
    out = {}
    for label, root, code in (("aux5_qualification_evidence", GS.AUX5_NS / "evidence/qualification_r1", "QUALIFICATION_ROOT"),
                              ("q6_requalification_evidence", GS.NS / "evidence/requalification_r1/qualification_r1",
                               "QUALIFICATION_ROOT"),
                              ("host_qualification_runs", Path("/root/work/postk1-runs/aux5-qualification"), "QUALIFICATION_ROOT"),
                              ("host_q6_runs", Path("/root/work/postk1-runs/glibc-successor-q6"), "QUALIFICATION_ROOT"),
                              ("repository_config", GS.NS / "config", "REPOSITORY_ROOT")):
        cfgp = scratch / f"c10_{label}.json"
        atomic_write_json(cfgp, {**c.cfg, "root": str(root), "config_path": str(cfgp)})
        rc, o, _rep = sanctioned_settle(cfgp)
        check(rc == PS.EXIT_REFUSED and settle_refused(o, code), f"{label}: {o[-300:]}")
        out[label] = code
    live = {k: sha256_file(GS.ROOT / p) for k, p in cp["qualification"]["record_paths"].items()}
    live.update({f"Q6_{k}": sha256_file(GS.NS / f"evidence/requalification_r1/qualification_r1/c{k[:3]}_{k[3]}/aux5_CUSUM_{k[:3]}_256.json")
                 for k in ("318A", "318B", "323A", "323B")})
    check(live == fw, "qualification and Q6 records unchanged")
    return out


@scenario("terminal HALTED successor -> settled for accounting only, never converted to COMPLETE",
          "budget-exhausted successor -> settled, never adjudication-ready")
def c11_halted_and_exhausted_stay_terminal(scratch):
    h = GSCampaign(scratch, "c11_halted", cells=[128, 129, 130], cores=[0], drift_after_records=1)
    code, o = h.run(keep=True)
    st0 = h.state()
    check(code == PS.EXIT_HALTED and st0["disposition"] == "HALTED" and (st0["halt"] or {}).get("reason") == "HOST_DRIFT"
          and count(st0, "SEALED") >= 1, f"halted fixture exit {code}: {o[-300:]}")
    rc, out, rep = sanctioned_settle(h)
    check(rc == 0 and rep["state"] == "SETTLED" and rep["disposition"] == "HALTED", f"settle HALTED: {out[-300:]}")
    st1 = h.state()
    check(st1["disposition"] == "HALTED" and st1["halt"] == st0["halt"] and st1["cells"] == st0["cells"] and not unsettled(st1),
          "disposition, halt and cells unchanged")
    audit = h.audit()
    check(GS.STOP_ISSUE in audit["issues"] and "D_unsettled_supervisor_runs" not in audit["issues"]
          and not audit["INTEGRITY_READY_FOR_ADJUDICATION"], f"halted audit {sorted(audit['issues'])}")
    seq = st1["seq"]
    check(h.run(keep=False)[0] == PS.EXIT_HALTED and h.state()["seq"] == seq, "a settled HALTED ledger never admits again")
    pred = PredFixture(scratch, "c11_pred", sealed=2, universe=6)
    pred.make_terminal()
    comp = composite(pred, h, pred.tolerance())
    check(comp["state"] != "COMPLETE" and not comp["K4_READY"], f"halted successor composite {comp['state']}")
    expect_refusal("ATTESTATION_REFUSED", GC.build_composite_attestation, comp, successor_checkpoint_sha256="x",
                   predecessor_checkpoint_sha256="y")
    x = GSCampaign(scratch, "c11_exhausted", cells=list(range(128, 136)), cores=[0], cap_usec=4_000_000, reservation_usec=1_000_000,
                   burn_s=0.3)
    code, o = x.run(keep=True)
    check(code == PS.EXIT_BUDGET, f"exhausted fixture exit {code}: {o[-300:]}")
    rc, out, rep2 = sanctioned_settle(x)
    check(rc == 0 and rep2["state"] == "SETTLED" and x.state()["disposition"] == "INCOMPLETE_BUDGET_EXHAUSTED"
          and not x.audit()["INTEGRITY_READY_FOR_ADJUDICATION"], f"settle exhausted: {out[-300:]}")
    check(sanctioned_settle(x)[2]["state"] == "ALREADY_SETTLED", "idempotent on an exhausted ledger")
    return {"halted": {"settlement": rep["state"], "disposition": "HALTED", "composite": comp["state"]},
            "exhausted": {"settlement": rep2["state"], "disposition": "INCOMPLETE_BUDGET_EXHAUSTED"}}


@scenario("CPU cap continuous and unchanged through settlement", "a forged cap refuses settlement",
          "a cap change in the campaign specification refuses settlement")
def c12_cap_continuity_through_settlement(scratch):
    cap = {"cap_usec": GS.RESIDUAL_CAP_US, "reservation_usec": GS.RESERVATION_US}
    c = finished_unsettled(scratch, "c12", **cap)
    st0 = c.state()
    check(st0["cap"] == {**cap, "invariant": GS.INVARIANT}, f"genesis cap {st0['cap']}")
    want = expected_charge(c)
    rc, out, rep = sanctioned_settle(c)
    st1 = c.state()
    check(rc == 0 and st1["cap"] == st0["cap"] and rep["cap_usec"] == GS.RESIDUAL_CAP_US
          and L.committed_total(st1) - L.committed_total(st0) == want, f"cap or charge changed: {out[-300:]}")
    f = finished_unsettled(scratch, "c12_forged_cap", **cap)
    forge_next_state(f.root, lambda s: s["cap"].__setitem__("cap_usec", GS.ABSOLUTE_CAP_US))
    forged = refused_unchanged(f, "CAP_CHANGE_FORBIDDEN", "forged 300 CPU-h cap")
    g = finished_unsettled(scratch, "c12_spec_cap", **cap)
    g.cfg["cap_usec"] = GS.ABSOLUTE_CAP_US
    g.save()
    spec_change = refused_unchanged(g, "AUTHORIZATION_MISMATCH", "specification cap raised to 300 CPU-h")
    return {"cap_usec": GS.RESIDUAL_CAP_US, "charged_usec": want, "forged_cap": forged, "spec_cap": spec_change}


@scenario("production `gs_entry.py settle` refuses without a successor ledger and creates nothing",
          "no acceptance scenario settles through a helper", "settlement tooling bound by the checkpoint")
def c13_production_command_and_no_bypass(scratch):
    rc, out = sanctioned_settle_production()
    check(rc == PS.EXIT_REFUSED and settle_refused(out, "NO_LEDGER") and not GS.SUCCESSOR_RUNTIME_ROOT.exists(),
          f"production settle: {out[-400:]}")
    bypass = settlement_bypass_scan()
    check(bypass == [], f"direct settlement calls in the successor tests: {bypass}")
    try:
        GSCampaign(scratch, "c13_helper", cells=[128]).settle()
        raise AssertionError("the frozen harness settlement helper is reachable from the successor acceptance")
    except Fail:
        pass
    cp, _sha = real_checkpoint()
    es = cp["END_OF_CAMPAIGN_SETTLEMENT"]
    live = {r: sha256_file(GS.ROOT / r) for r in es["module_sha256"]}
    check(live == es["module_sha256"] and es["version"] == ST.SETTLE_VERSION and es["command"] == ST.SETTLE_COMMAND,
          "settlement tooling equals the checkpoint binding")
    return {"production_settle": "NO_LEDGER", "bypass_scan": "clean", "settlement_version": es["version"]}
