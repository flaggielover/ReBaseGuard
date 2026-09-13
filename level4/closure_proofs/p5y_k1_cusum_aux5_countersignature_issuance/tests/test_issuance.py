"""Adversarial tests for the countersignature issuance protocol. Governance only: no production countersignature is
written to the repository, no production runtime root is touched, nothing is launched, no scientific worker runs.

  python -B tests/test_issuance.py
"""
from __future__ import annotations

import copy
import itertools
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import issuance as I                                                                    # noqa: E402
import prod_ledger as L                                                                 # noqa: E402
from prod_common import Refusal, canonical, sha256_bytes, sha256_file                   # noqa: E402
from prov_authorization import load_authorization, verify_countersignature              # noqa: E402
from prov_spec import AUTHORIZATION, AUTHORIZATION_HASH, CHECKPOINT, FREEZE_RECORD      # noqa: E402

AUTH, AUTH_SHA = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
CP_SHA, FR_SHA = sha256_file(CHECKPOINT), sha256_file(FREEZE_RECORD)
HOST = AUTH["host"]["host_name"]
EVIDENCE_REL = f"{I.NS_REL}/evidence/review_preflight_r2/REVIEW_PREFLIGHT.json"
TIP, EV_COMMIT, CS_COMMIT = "a" * 40, "b" * 40, "c" * 40
OTHER = "0" * 64
LINUX = sys.platform.startswith("linux")


def report(**fail) -> dict:
    """A frozen P01-P10 report; fail maps short check prefix (e.g. P07) to a refusal code."""
    checks = []
    for name in I.FROZEN_CHECKS:
        code = fail.get(name[:3])
        checks.append({"check": name, "status": "PASS"} if code is None else {"check": name, "status": "FAIL", "code": code})
    return {"checks": checks, "ready": not fail}


ABSENT_ROOT = {"state": I.ROOT_ABSENT, "problems": [], "entries": [], "lock_state": "FREE", "reaper_sha256": None,
               "reaper_size": 0, "reaper_record_ids": [], "overhead_usec": 0}
PRISTINE = {"production_root_exists": False, "runtime_root": ABSENT_ROOT, "production_processes": [],
            "result_bearing_cells": 0, "predecessor_ledger_exists": False, "checkout_clean": True}


def facts_for(rr: dict, **over) -> dict:
    return {**PRISTINE, "runtime_root": rr, "production_root_exists": rr["state"] != I.ROOT_ABSENT, **over}


class FakeGit:
    """Linear history AUTH -> FREEZE -> TIP -> EV -> CS; files[commit] maps path -> bytes."""

    def __init__(self, files=None, head=CS_COMMIT, order=None):
        self.order = order or [I.AUTH_COMMIT, I.FREEZE_COMMIT, TIP, EV_COMMIT, CS_COMMIT]
        self.files, self._head = files or {}, head

    def head(self):
        return self._head

    def is_ancestor(self, a, b):
        return a in self.order and b in self.order and self.order.index(a) <= self.order.index(b)

    def changed_paths(self, a, b, paths):
        fa, fb = self.files.get(a, {}), self.files.get(b, {})
        return sorted(k for k in set(fa) | set(fb) if fa.get(k) != fb.get(k) and any(k.startswith(x) for x in paths))

    def show(self, commit, path):
        for c in reversed(self.order[: self.order.index(commit) + 1]) if commit in self.order else []:
            if path in self.files.get(c, {}):
                return self.files[c][path]
        return None


def evidence(**over) -> bytes:
    rec = {"schema": I.REVIEW_SCHEMA, "head": TIP, "authorization_sha256": AUTH_SHA, "provenance_checkpoint_sha256": CP_SHA,
           "freeze_record_sha256": FR_SHA, "facts": copy.deepcopy(PRISTINE), "decision": {"state": I.REVIEW_READY}}
    rec.update(over)
    return (json.dumps(rec, sort_keys=True) + "\n").encode()


def countersignature(ev_bytes: bytes, **over) -> dict:
    rr = json.loads(ev_bytes).get("facts", {}).get("runtime_root")
    cs = {"schema": I.S.COUNTERSIGN_SCHEMA, "verdict": I.S.APPROVED, "synthetic": False, "mode": "PRODUCTION",
          "authorization_sha256": AUTH_SHA, "production_checkpoint_sha256": CP_SHA,
          "production_run_id": AUTH["production_run_id"], "freeze_record_sha256": FR_SHA,
          "reviewer": "TEST_REVIEWER", "reviewer_independent_of_authoring_session": True,
          "issuance": {"schema": I.ISSUANCE_SCHEMA, "authorization_commit": I.AUTH_COMMIT, "freeze_commit": I.FREEZE_COMMIT,
                       "authorization_id": AUTH["authorization_id"], "ledger_id": AUTH["ledger"]["ledger_id"],
                       "runtime_root": AUTH["ledger"]["runtime_root"], "producer": AUTH["producer"], "host": AUTH["host"],
                       "runtime_contract_hash": AUTH["runtime"]["runtime_contract_hash"], "universe": AUTH["universe"],
                       "cap": {"cap_cpu_h": 300, "cap_usec": 300 * 3600 * 10**6}, "review_verdict": "PASS",
                       "review_state": I.REVIEW_READY, "statements": dict(I.REQUIRED_STATEMENTS), "reviewed_tip": TIP,
                       "pre_genesis_residue": I.residue_summary(rr),
                       "review_evidence": {"path": EVIDENCE_REL, "sha256": sha256_bytes(ev_bytes), "commit": EV_COMMIT}}}
    for k, v in over.items():
        if k.startswith("iss_"):
            cs["issuance"][k[4:]] = v
        else:
            cs[k] = v
    return cs


def git_with(ev_bytes: bytes, **kw) -> FakeGit:
    watched = f"{I.SUCC_REL}/config/PROVENANCE_CHECKPOINT.json"
    files = {TIP: {watched: b"frozen"}, EV_COMMIT: {EVIDENCE_REL: ev_bytes, watched: b"frozen"},
             CS_COMMIT: {EVIDENCE_REL: ev_bytes, watched: b"frozen", I.COUNTERSIGNATURE_REL: b"cs"}}
    return FakeGit(files=files, **kw)


def binding(cs, git=None, auth=None, auth_sha=AUTH_SHA, cp=CP_SHA, fr=FR_SHA):
    return I.check_issuance_binding(cs, auth=auth or AUTH, auth_sha=auth_sha, checkpoint_sha=cp, freeze_sha=fr,
                                    git=git or git_with(evidence()))


class Tmp:
    def __enter__(self):
        self.d = tempfile.TemporaryDirectory()
        return Path(self.d.name)

    def __exit__(self, *exc):
        self.d.cleanup()


def write(path: Path, obj) -> Path:
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    return path


# ---------------------------------------------------------------- runtime-root fixtures (frozen reaper format)
def reaper_rec(kind, pid, cpu, *, sup, exit_code, exited=True, signal=None, boot="test-boot", t=1789298296.9):
    body = {"schema": L.REAPER_SCHEMA, "kind": kind, "pid": pid, "boot_id": boot, "t_wall": t, "cpu_usec": cpu,
            "is_supervisor": sup, "exited": None if kind == "KEEPER_EXIT" else exited,
            "exit_code": exit_code, "signal": signal}
    return {**body, "record_id": sha256_bytes(canonical(body))}


REFUSED_SUP = reaper_rec("CHILD_REAPED", 102197, 4366444, sup=True, exit_code=30)
KEEPER = reaper_rec("KEEPER_EXIT", 102196, 75363, sup=False, exit_code=None)
REFUSED_LAUNCH_USEC = 4366444 + 75363


def reaper_bytes(recs) -> bytes:
    return "".join(json.dumps(r, sort_keys=True) + "\n" for r in recs).encode()


def make_root(base: Path, recs=(REFUSED_SUP, KEEPER), *, owner=None) -> Path:
    root = base / "root"
    root.mkdir()
    (root / "campaign.lock").write_bytes(b"")
    write(root / "campaign.owner.json", owner or {"host": HOST, "pid": 102197, "run_id": "R-refused", "t_wall": 1.0})
    (root / "reaper.jsonl").write_bytes(reaper_bytes(recs))
    return root


def classify(root, lock="FREE"):
    return I.classify_runtime_root(root, lock_state=lock, bound_host=HOST)


class IssuanceTests(unittest.TestCase):
    def assertRefused(self, code, fn, *a, **kw):
        with self.assertRaises(Refusal) as ctx:
            fn(*a, **kw)
        self.assertEqual(ctx.exception.code, code, ctx.exception.detail)

    # ---- 1 missing countersignature
    def test_missing_countersignature_review_ready_production_not_ready(self):
        with Tmp() as d:
            self.assertRefused("COUNTERSIGNATURE_MISSING", verify_countersignature, d / "COUNTERSIGNATURE.json",
                               auth=AUTH, auth_sha=AUTH_SHA, freeze_record_sha256=FR_SHA)
        rep = report(P07="COUNTERSIGNATURE_MISSING")
        dec = I.review_decision(rep, PRISTINE, [])
        self.assertEqual(dec["state"], I.REVIEW_READY)
        self.assertTrue(dec["signing_permitted"])
        self.assertFalse(dec["launch_authorized"])
        self.assertEqual(I.launch_eligibility(rep, ["COUNTERSIGNATURE_MISSING"], PRISTINE)["state"], I.NOT_READY)
        self.assertEqual(I.launch_eligibility(rep, [], PRISTINE)["state"], I.NOT_READY)

    # ---- 2 valid countersignature
    def test_valid_countersignature_review_pass_production_ready(self):
        ev = evidence()
        cs = countersignature(ev)
        with Tmp() as d:
            verify_countersignature(write(d / "COUNTERSIGNATURE.json", cs), auth=AUTH, auth_sha=AUTH_SHA,
                                    freeze_record_sha256=FR_SHA)
        self.assertEqual(binding(cs, git_with(ev)), [])
        rep = report()
        dec = I.review_decision(rep, PRISTINE, [])
        self.assertEqual(dec["state"], I.REVIEW_PASS_SIGNED)
        self.assertFalse(dec["signing_permitted"], "a second countersignature is never issued")
        self.assertEqual(I.launch_eligibility(rep, [], PRISTINE)["state"], I.LAUNCH_READY)

    # ---- 3 wrong countersignature hash
    def test_wrong_countersignature_hash_refused(self):
        ev = evidence()
        cs = countersignature(ev, authorization_sha256=OTHER)
        with Tmp() as d:
            self.assertRefused("COUNTERSIGNATURE_INVALID", verify_countersignature, write(d / "cs.json", cs),
                               auth=AUTH, auth_sha=AUTH_SHA, freeze_record_sha256=FR_SHA)
        self.assertTrue(any("authorization_sha256" in x for x in binding(cs, git_with(ev))))
        rep = report(P07="COUNTERSIGNATURE_INVALID")
        self.assertEqual(I.launch_eligibility(rep, [], PRISTINE)["state"], I.NOT_READY)
        self.assertEqual(I.review_eligibility(rep)["state"], I.BLOCKED, "an invalid signature is not an absent one")
        bad_ev = countersignature(ev, iss_review_evidence={"path": EVIDENCE_REL, "sha256": OTHER, "commit": EV_COMMIT})
        self.assertTrue(any("sha256 differs" in x for x in binding(bad_ev, git_with(ev))))

    # ---- 4 countersignature for another checkpoint
    def test_countersignature_for_another_checkpoint_refused(self):
        ev = evidence()
        cs = countersignature(ev, production_checkpoint_sha256=OTHER)
        with Tmp() as d:
            self.assertRefused("COUNTERSIGNATURE_INVALID", verify_countersignature, write(d / "cs.json", cs),
                               auth=AUTH, auth_sha=AUTH_SHA, freeze_record_sha256=FR_SHA)
        self.assertTrue(binding(cs, git_with(ev)))
        ev2 = evidence(provenance_checkpoint_sha256=OTHER)
        cs2 = countersignature(ev2)
        self.assertTrue(any("REVIEW_EVIDENCE" in x for x in binding(cs2, git_with(ev2))))

    # ---- 5 checkpoint mutation after signing
    def test_checkpoint_mutation_after_signing_refused(self):
        ev = evidence()
        cs = countersignature(ev)
        with Tmp() as d:
            self.assertRefused("COUNTERSIGNATURE_INVALID", verify_countersignature, write(d / "cs.json", cs),
                               auth=AUTH, auth_sha=AUTH_SHA, freeze_record_sha256=OTHER)
        self.assertTrue(binding(cs, git_with(ev), cp=OTHER, fr=OTHER))
        g = git_with(ev)
        g.files[CS_COMMIT][f"{I.SUCC_REL}/config/PROVENANCE_CHECKPOINT.json"] = b"mutated"
        self.assertTrue(any("MUTATED_SINCE_REVIEW" in x for x in binding(cs, g)))
        self.assertEqual(I.launch_eligibility(report(P01="FREEZE_RECORD", P02="BOUND_SOURCE_DRIFT"), [], PRISTINE)["state"],
                         I.NOT_READY)

    # ---- 6 authorization mutation after signing
    def test_authorization_mutation_after_signing_refused(self):
        ev = evidence()
        cs = countersignature(ev)
        mutated = copy.deepcopy(AUTH)
        mutated["cap"]["cap_usec"] += 1
        with Tmp() as d:
            ap, hp = write(d / "RUN_AUTHORIZATION.json", mutated), d / "RUN_AUTHORIZATION_HASH"
            hp.write_text(AUTH_SHA + "\n")
            self.assertRefused("AUTHORIZATION_INVALID", load_authorization, ap, hp)
            hp.write_text(sha256_file(ap) + "\n")
            m_auth, m_sha = load_authorization(ap, hp)
            self.assertRefused("COUNTERSIGNATURE_INVALID", verify_countersignature, write(d / "cs.json", cs),
                               auth=m_auth, auth_sha=m_sha, freeze_record_sha256=FR_SHA)
            self.assertTrue(binding(cs, git_with(ev), auth=m_auth, auth_sha=m_sha))
        g = git_with(ev)
        g.files[CS_COMMIT][f"{I.SUCC_REL}/config/RUN_AUTHORIZATION.json"] = b"mutated"
        self.assertTrue(any("MUTATED_SINCE_REVIEW" in x for x in binding(cs, g)))

    # ---- 7 production already started before signing
    def test_production_started_before_signing_refused(self):
        rep = report(P07="COUNTERSIGNATURE_MISSING")
        started = {**ABSENT_ROOT, "state": I.ROOT_STARTED, "problems": ["PRODUCTION_STARTED"], "entries": ["ledger.json"]}
        for f in (facts_for(started), {**PRISTINE, "production_root_exists": True}, {**PRISTINE, "runtime_root": None},
                  {**PRISTINE, "production_processes": [{"pid": 7}]}, {**PRISTINE, "result_bearing_cells": 1},
                  {**PRISTINE, "predecessor_ledger_exists": True}, {**PRISTINE, "checkout_clean": False}):
            dec = I.review_decision(rep, f, [])
            self.assertEqual(dec["state"], I.BLOCKED, f)
            self.assertFalse(dec["signing_permitted"], f)
        self.assertEqual(I.review_decision(report(P07="COUNTERSIGNATURE_MISSING", P09="NO_PRE_RESULT_AUTHORIZATION"),
                                           PRISTINE, [])["state"], I.BLOCKED)
        self.assertEqual(I.review_decision(rep, PRISTINE, ["PREDATES: x"])["state"], I.BLOCKED)
        ev = evidence(facts=facts_for(started))
        self.assertTrue(any("not pre-genesis" in x for x in binding(countersignature(ev), git_with(ev))))
        ev = evidence()
        cs = countersignature(ev, iss_statements={**I.REQUIRED_STATEMENTS, "production_result_existed_at_signing": True})
        self.assertTrue(any("STATEMENT" in x for x in binding(cs, git_with(ev))))
        self.assertEqual(I.launch_eligibility(report(), [], facts_for(started))["state"], I.NOT_READY)

    # ---- 8 stale reviewer base
    def test_stale_reviewer_base_refused(self):
        ev = evidence()
        pre_freeze = countersignature(ev, iss_reviewed_tip=I.AUTH_COMMIT)
        self.assertTrue(any("STALE_REVIEWER_BASE" in x for x in binding(pre_freeze, git_with(ev))))
        orphan = countersignature(ev, iss_reviewed_tip="d" * 40)
        self.assertTrue(any("STALE_REVIEWER_BASE" in x for x in binding(orphan, git_with(ev))))
        ev_other_head = evidence(head=I.FREEZE_COMMIT)
        self.assertTrue(any("REVIEW_EVIDENCE" in x for x in binding(countersignature(ev_other_head), git_with(ev_other_head))))
        rolled_back = git_with(ev, head=TIP)
        self.assertTrue(any("REVIEW_EVIDENCE" in x for x in binding(countersignature(ev), rolled_back)))

    # ---- structural: no route from Phase A to launch
    def test_no_route_from_review_to_launch(self):
        codes = ("COUNTERSIGNATURE_MISSING", "COUNTERSIGNATURE_INVALID", "UNEXPECTED")
        for mask in itertools.product((None,) + codes, *([(None, "X")] * 9)):
            fail = {}
            p07, others = mask[0], mask[1:]
            if p07:
                fail["P07"] = p07
            for name, code in zip([n for n in I.FROZEN_CHECKS if n != I.SIGNATURE_GATE], others):
                if code:
                    fail[name[:3]] = code
            rep = report(**fail)
            dec = I.review_decision(rep, PRISTINE, [])
            self.assertIn(dec["state"], I.REVIEW_STATES)
            self.assertNotIn(dec["state"], I.LAUNCH_STATES)
            self.assertFalse(dec["launch_authorized"])
            self.assertEqual(dec["signing_permitted"], fail == {"P07": "COUNTERSIGNATURE_MISSING"})
            self.assertEqual(I.launch_eligibility(rep, [], PRISTINE)["state"] == I.LAUNCH_READY, not fail)

    def test_each_substantive_gate_blocks_review(self):
        for name in I.FROZEN_CHECKS:
            if name == I.SIGNATURE_GATE:
                continue
            dec = I.review_decision(report(P07="COUNTERSIGNATURE_MISSING", **{name[:3]: "X"}), PRISTINE, [])
            self.assertEqual(dec["state"], I.BLOCKED, name)

    def test_malformed_report_blocks_both_phases(self):
        rep = report(P07="COUNTERSIGNATURE_MISSING")
        rep["checks"] = [c for c in rep["checks"] if c["check"] != "P10_host_idle"]
        self.assertEqual(I.review_eligibility(rep)["state"], I.BLOCKED)
        full = report()
        full["checks"] = full["checks"][:-1]
        self.assertEqual(I.launch_eligibility(full, [], PRISTINE)["state"], I.NOT_READY)
        lying = report(P07="COUNTERSIGNATURE_MISSING")
        lying["ready"] = True
        self.assertEqual(I.launch_eligibility(lying, [], PRISTINE)["state"], I.NOT_READY)

    def test_synthetic_or_unapproved_or_stale_schema_countersignature_refused(self):
        ev = evidence()
        for over in ({"synthetic": True}, {"mode": "SYNTHETIC"}, {"verdict": "BLOCKED"},
                     {"iss_cap": {"cap_cpu_h": 301, "cap_usec": 301 * 3600 * 10**6}},
                     {"iss_universe": {**AUTH["universe"], "cells": 325}}, {"iss_host": {**AUTH["host"], "host_name": "x"}},
                     {"iss_producer": {**AUTH["producer"], "producer_identity_hash": OTHER}}, {"issuance": None},
                     {"iss_schema": "rebaseguard.p5y.k1.cusum-aux5.countersignature-issuance.v1"},
                     {"iss_pre_genesis_residue": {**I.residue_summary(ABSENT_ROOT), "state": I.ROOT_PRE_GENESIS}}):
            self.assertTrue(binding(countersignature(ev, **over), git_with(ev)), over)


class RuntimeRootTests(unittest.TestCase):
    """Pre-genesis residue versus production start, on real directories with frozen-format reaper records."""

    def eligible(self, rr, **over):
        return I.launch_eligibility(report(), [], facts_for(rr, **over))["state"] == I.LAUNCH_READY

    def test_frozen_constants_have_not_drifted(self):
        self.assertEqual(tuple(L.PRE_GENESIS_FILES), I.FROZEN_PRE_GENESIS_FILES)
        p = L.Paths("/x")
        self.assertEqual((p.ledger.name, p.journal.name), I.GENESIS_FILES)
        self.assertEqual((p.lock.name, p.owner.name, p.reaper.name), I.FROZEN_PRE_GENESIS_FILES)
        cp = json.loads(CHECKPOINT.read_text())
        self.assertEqual(cp["lifecycle"]["exit_codes"]["REFUSED"], I.FROZEN_REFUSED_EXIT)

    def test_A_root_absent_eligible(self):
        with Tmp() as d:
            rr = classify(d / "root")
        self.assertEqual(rr["state"], I.ROOT_ABSENT)
        self.assertTrue(self.eligible(rr))

    def test_B_exact_pre_genesis_files_eligible(self):
        with Tmp() as d:
            root = make_root(d)
            rr = classify(root)
            self.assertEqual(rr["state"], I.ROOT_PRE_GENESIS, rr["problems"])
            self.assertEqual(rr["entries"], sorted(I.FROZEN_PRE_GENESIS_FILES))
            self.assertEqual(rr["overhead_usec"], REFUSED_LAUNCH_USEC)
            self.assertEqual(rr["reaper_record_ids"], [REFUSED_SUP["record_id"], KEEPER["record_id"]])
            self.assertTrue(self.eligible(rr))
            self.assertEqual(I.review_decision(report(P07="COUNTERSIGNATURE_MISSING"), facts_for(rr), [])["state"],
                             I.REVIEW_READY)
            # the frozen lifecycle agrees: its read-only view of such a root is FRESH
            self.assertEqual(L.Ledger.inspect(type("Spec", (), {"root": root})())["relation"], "FRESH")
            # a subset of the frozen files (e.g. a root created by the lock alone) is also pre-genesis
            (root / "reaper.jsonl").unlink()
            self.assertEqual(classify(root)["state"], I.ROOT_PRE_GENESIS)

    def _refused(self, root, *, expect=None, lock="FREE"):
        rr = classify(root, lock)
        self.assertNotIn(rr["state"], I.ACCEPTABLE_ROOT_STATES, rr)
        if expect:
            self.assertEqual(rr["state"], expect, rr)
        self.assertFalse(self.eligible(rr))
        self.assertEqual(I.review_decision(report(P07="COUNTERSIGNATURE_MISSING"), facts_for(rr), [])["state"], I.BLOCKED)
        return rr

    def test_C_pre_genesis_plus_ledger_refused(self):
        for name in I.GENESIS_FILES:
            with Tmp() as d:
                root = make_root(d)
                (root / name).write_text("{}\n")
                self._refused(root, expect=I.ROOT_STARTED)

    def test_D_pre_genesis_plus_reservation_state_refused(self):
        with Tmp() as d:
            root = make_root(d)
            (root / "attempts" / "A00000-C0000").mkdir(parents=True)
            self._refused(root, expect=I.ROOT_CORRUPTED)
        with Tmp() as d:
            root = make_root(d)
            write(root / "ledger.json", {"cells": {"0": {"status": "RESERVED", "attempt": "A00000-C0000"}}})
            self._refused(root, expect=I.ROOT_STARTED)

    def test_E_pre_genesis_plus_scientific_output_refused(self):
        for rel in ("attempts/A00000-C0000/aux5_CUSUM_0_256.json", "aux5_CUSUM_0_256.json",
                    "provenance/A00000-C0000/CUSUM_0000.envelope.json"):
            with Tmp() as d:
                root = make_root(d)
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text('{"scientific_content_hash": "x"}\n')
                self._refused(root, expect=I.ROOT_CORRUPTED)

    def test_F_unknown_or_irregular_entry_refused(self):
        for mutate in (lambda r: (r / "notes.txt").write_text("x"), lambda r: (r / "DRAIN").write_text("x"),
                       lambda r: (r / ".hidden").write_text("x")):
            with Tmp() as d:
                root = make_root(d)
                mutate(root)
                self._refused(root, expect=I.ROOT_CORRUPTED)
        with Tmp() as d:
            root = make_root(d)
            (root / "campaign.lock").unlink()
            (root / "campaign.lock").mkdir()
            self._refused(root)
        with Tmp() as d:
            root = make_root(d)
            (d / "elsewhere.jsonl").write_bytes((root / "reaper.jsonl").read_bytes())
            (root / "reaper.jsonl").unlink()
            (root / "reaper.jsonl").symlink_to(d / "elsewhere.jsonl")
            self._refused(root)
        with Tmp() as d:
            root = make_root(d, owner={"host": "another-host", "pid": 1})
            self._refused(root)
        with Tmp() as d:
            root = make_root(d)
            (root / "campaign.lock").write_text("x")
            self._refused(root)
        with Tmp() as d:
            (d / "file").write_text("x")
            self._refused(d / "file")

    def test_G_running_production_process_or_live_lock_refused(self):
        with Tmp() as d:
            rr = classify(make_root(d))
        self.assertFalse(self.eligible(rr, production_processes=[{"pid": 4242, "cmdline": "python prov_entry.py launch"}]))
        self.assertFalse(self.eligible(rr, result_bearing_cells=1))
        with Tmp() as d:
            self._refused(make_root(d), lock="LIVE")
        with Tmp() as d:
            self._refused(make_root(d), lock="UNPROBEABLE_OSError")

    def test_H_corrupted_reaper_refused(self):
        edited = {**REFUSED_SUP, "cpu_usec": 1}                                   # record_id no longer recomputes
        worker = reaper_rec("CHILD_REAPED", 555, 10, sup=False, exit_code=0)      # a worker ran
        sup_ok = reaper_rec("CHILD_REAPED", 556, 10, sup=True, exit_code=0)       # a supervisor finished normally
        sup_sig = reaper_rec("CHILD_REAPED", 557, 10, sup=True, exit_code=None, exited=False, signal=9)
        negative = reaper_rec("KEEPER_EXIT", 558, -5, sup=False, exit_code=None)
        cases = [reaper_bytes([REFUSED_SUP]) + b"not json\n", reaper_bytes([edited, KEEPER]),
                 reaper_bytes([REFUSED_SUP, KEEPER])[:-1], reaper_bytes([REFUSED_SUP, worker]),
                 reaper_bytes([sup_ok]), reaper_bytes([sup_sig]), reaper_bytes([negative]),
                 reaper_bytes([REFUSED_SUP, REFUSED_SUP]), reaper_bytes([{**KEEPER, "schema": "other"}])]
        for data in cases:
            with Tmp() as d:
                root = make_root(d)
                (root / "reaper.jsonl").write_bytes(data)
                rr = self._refused(root, expect=I.ROOT_CORRUPTED)
                self.assertTrue(any(x.startswith("REAPER") for x in rr["problems"]), rr["problems"])

    def test_I_prior_sealed_cell_refused(self):
        with Tmp() as d:
            root = make_root(d)
            write(root / "ledger.json", {"cells": {"0": {"status": "SEALED", "attempt": "A00000-C0000"}}})
            (root / "journal.jsonl").write_text("{}\n")
            self._refused(root, expect=I.ROOT_STARTED)
        with Tmp() as d:
            root = make_root(d)
            (root / "attempts/A00000-C0000").mkdir(parents=True)
            (root / "attempts/A00000-C0000/aux5_CUSUM_0_256.json").write_text("{}")
            os.chmod(root / "attempts/A00000-C0000/aux5_CUSUM_0_256.json", 0o444)
            self._refused(root, expect=I.ROOT_CORRUPTED)

    def test_residue_bound_at_signing_cannot_be_lost_or_rewritten(self):
        with Tmp() as d:
            root = make_root(d)
            signed = I.residue_summary(classify(root))
            live = classify(root)
            self.assertEqual(I.residue_preserved(signed, live, (root / "reaper.jsonl").read_bytes()), [])
            extra = reaper_rec("KEEPER_EXIT", 900, 11, sup=False, exit_code=None)
            with open(root / "reaper.jsonl", "ab") as fh:                        # a later refused launch appends
                fh.write(reaper_bytes([extra]))
            live = classify(root)
            self.assertEqual(live["state"], I.ROOT_PRE_GENESIS)
            self.assertEqual(I.residue_preserved(signed, live, (root / "reaper.jsonl").read_bytes()), [])
            (root / "reaper.jsonl").write_bytes(reaper_bytes([KEEPER, REFUSED_SUP]))   # reordered rewrite
            self.assertTrue(I.residue_preserved(signed, classify(root), (root / "reaper.jsonl").read_bytes()))
            (root / "reaper.jsonl").write_bytes(reaper_bytes([REFUSED_SUP]))           # truncated
            self.assertTrue(I.residue_preserved(signed, classify(root), (root / "reaper.jsonl").read_bytes()))
            (root / "reaper.jsonl").unlink()                                          # deleted
            self.assertTrue(I.residue_preserved(signed, classify(root), b""))
        self.assertTrue(I.residue_preserved(signed, ABSENT_ROOT, b""), "a signed residue cannot vanish with the root")
        self.assertEqual(I.residue_preserved(I.residue_summary(ABSENT_ROOT), ABSENT_ROOT, b""), [])
        self.assertTrue(I.residue_preserved(None, ABSENT_ROOT, b""))

    @unittest.skipUnless(LINUX, "the frozen ledger accounting reads the Linux boot id")
    def test_J_pre_genesis_overhead_survives_genesis_and_is_charged_once(self):
        from prod_common import boot_id
        from prod_spec import CampaignSpec
        with Tmp() as d:
            root = d / "root"
            spec = CampaignSpec.synthetic({"root": str(root), "checkpoint_sha256": "SYNTHETIC-issuance-J",
                                           "config_path": str(d / "unused.json"), "cells": [0, 1],
                                           "cap_usec": 300 * 3600 * 10**6, "reservation_usec": 3600 * 10**6, "cores": [0]})
            lk = L.CampaignLock(root)
            lk.acquire({"host": HOST, "pid": 102197, "run_id": "R-refused", "t_wall": time.time()})
            lk.release()
            t_ref = time.time() - 120
            recs = [reaper_rec("CHILD_REAPED", 102197, 4366444, sup=True, exit_code=30, boot=boot_id(), t=t_ref),
                    reaper_rec("KEEPER_EXIT", 102196, 75363, sup=False, exit_code=None, boot=boot_id(), t=t_ref)]
            (root / "reaper.jsonl").write_bytes(reaper_bytes(recs))
            self.assertEqual(classify(root)["state"], I.ROOT_PRE_GENESIS)
            expected = {r["record_id"]: r["cpu_usec"] for r in recs}

            def supervisor(run_id, *, open_run=True):
                lock = L.CampaignLock(root)
                lock.acquire({"host": HOST, "pid": os.getpid(), "run_id": run_id, "t_wall": time.time()})
                try:
                    led = L.Ledger(spec, lock, run_id=run_id)
                    relation = led.open(allow_genesis=True)
                    reaped, bad = L.read_reaper(led.p)
                    self.assertEqual(bad, 0)
                    ov = L.unmatched_overhead(reaped, led.state)
                    if open_run:
                        led.txn("RUN_OPENED", lambda s: L.op_run_open(s, run_id, os.getpid(), 0, ov), {"run_id": run_id})
                    return relation, ov, copy.deepcopy(led.state)
                finally:
                    lock.release()

            # crash between GENESIS and RUN_OPENED: nothing charged yet, and nothing lost
            rel0, _ov0, st0 = supervisor("R-J-0", open_run=False)
            self.assertEqual(rel0, "GENESIS")
            self.assertEqual(st0["overhead_charges"], {})
            self.assertEqual(classify(root)["state"], I.ROOT_STARTED)
            # the next supervisor charges the refused launch exactly once
            rel1, ov1, st1 = supervisor("R-J-1")
            self.assertEqual(rel1, "CONTINUOUS")
            self.assertEqual(dict(ov1), expected)
            self.assertEqual(st1["overhead_charges"], expected)
            self.assertEqual(sum(st1["overhead_charges"].values()), REFUSED_LAUNCH_USEC)
            self.assertGreaterEqual(st1["committed_usec"]["supervisor"], REFUSED_LAUNCH_USEC)
            # relaunch: deterministic, no second charge, even if the old overhead list is replayed
            rel2, ov2, st2 = supervisor("R-J-2")
            self.assertEqual((rel2, ov2), ("CONTINUOUS", []))
            self.assertEqual(st2["overhead_charges"], expected)
            replay = copy.deepcopy(st2)
            L.op_charge_overhead(replay, ov1)
            self.assertEqual(replay["committed_usec"], st2["committed_usec"])
            self.assertEqual(st2["cap"], {"cap_usec": 300 * 3600 * 10**6, "reservation_usec": 3600 * 10**6,
                                          "invariant": L.INVARIANT})
            L.validate_state(st2, spec)


if __name__ == "__main__":
    unittest.main(verbosity=2)
