"""Adversarial self-reference tests for the countersignature issuance protocol. Governance only: no production
countersignature is written to the repository, no runtime root is touched, nothing is launched.

  python -B tests/test_issuance.py
"""
from __future__ import annotations

import copy
import itertools
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import issuance as I                                                                    # noqa: E402
from prod_common import Refusal, sha256_bytes, sha256_file                              # noqa: E402
from prov_authorization import load_authorization, verify_countersignature              # noqa: E402
from prov_spec import AUTHORIZATION, AUTHORIZATION_HASH, CHECKPOINT, FREEZE_RECORD      # noqa: E402

AUTH, AUTH_SHA = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
CP_SHA, FR_SHA = sha256_file(CHECKPOINT), sha256_file(FREEZE_RECORD)
EVIDENCE_REL = f"{I.NS_REL}/evidence/review_preflight_r1/REVIEW_PREFLIGHT.json"
TIP, EV_COMMIT, CS_COMMIT = "a" * 40, "b" * 40, "c" * 40
OTHER = "0" * 64


def report(**fail) -> dict:
    """A frozen P01-P10 report; fail maps short check prefix (e.g. P07) to a refusal code."""
    checks = []
    for name in I.FROZEN_CHECKS:
        code = fail.get(name[:3])
        checks.append({"check": name, "status": "PASS"} if code is None else {"check": name, "status": "FAIL", "code": code})
    return {"checks": checks, "ready": not fail}


PRISTINE = {"production_root_exists": False, "production_processes": [], "result_bearing_cells": 0,
            "predecessor_ledger_exists": False, "checkout_clean": True}


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
           "freeze_record_sha256": FR_SHA, "facts": dict(PRISTINE), "decision": {"state": I.REVIEW_READY}}
    rec.update(over)
    return (json.dumps(rec, sort_keys=True) + "\n").encode()


def countersignature(ev_bytes: bytes, **over) -> dict:
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
    ev = evidence()
    return I.check_issuance_binding(cs, auth=auth or AUTH, auth_sha=auth_sha, checkpoint_sha=cp, freeze_sha=fr,
                                    git=git or git_with(ev))


class Tmp:
    def __enter__(self):
        self.d = tempfile.TemporaryDirectory()
        return Path(self.d.name)

    def __exit__(self, *exc):
        self.d.cleanup()


def write(path: Path, obj) -> Path:
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    return path


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
        # even with no issuance problem reported, the frozen P07 failure alone refuses launch
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
        # an unbound reference cannot redirect it: the review evidence must name the same checkpoint
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
            hp.write_text(sha256_file(ap) + "\n")                 # an attacker also rewrites the hash file
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
        for key, val in (("production_root_exists", True), ("production_processes", [{"pid": 7}]),
                         ("result_bearing_cells", 1), ("predecessor_ledger_exists", True), ("checkout_clean", False)):
            dec = I.review_decision(rep, {**PRISTINE, key: val}, [])
            self.assertEqual(dec["state"], I.BLOCKED, key)
            self.assertFalse(dec["signing_permitted"], key)
        self.assertEqual(I.review_decision(report(P07="COUNTERSIGNATURE_MISSING", P09="NO_PRE_RESULT_AUTHORIZATION"),
                                           PRISTINE, [])["state"], I.BLOCKED)
        self.assertEqual(I.review_decision(rep, PRISTINE, ["PREDATES: x"])["state"], I.BLOCKED)
        ev = evidence(facts={**PRISTINE, "production_root_exists": True})
        self.assertTrue(any("not pristine" in x for x in binding(countersignature(ev), git_with(ev))))
        ev = evidence()
        cs = countersignature(ev, iss_statements={**I.REQUIRED_STATEMENTS, "production_result_existed_at_signing": True})
        self.assertTrue(any("STATEMENT" in x for x in binding(cs, git_with(ev))))
        self.assertEqual(I.launch_eligibility(report(), [], {**PRISTINE, "production_root_exists": True})["state"], I.NOT_READY)

    # ---- 8 stale reviewer base
    def test_stale_reviewer_base_refused(self):
        ev = evidence()
        pre_freeze = countersignature(ev, iss_reviewed_tip=I.AUTH_COMMIT)
        self.assertTrue(any("STALE_REVIEWER_BASE" in x for x in binding(pre_freeze, git_with(ev))))
        orphan = countersignature(ev, iss_reviewed_tip="d" * 40)
        self.assertTrue(any("STALE_REVIEWER_BASE" in x for x in binding(orphan, git_with(ev))))
        ev_other_head = evidence(head=I.FREEZE_COMMIT)
        self.assertTrue(any("REVIEW_EVIDENCE" in x for x in binding(countersignature(ev_other_head), git_with(ev_other_head))))
        rolled_back = git_with(ev, head=TIP)                    # HEAD behind the evidence commit
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

    def test_synthetic_or_unapproved_countersignature_refused(self):
        ev = evidence()
        for over in ({"synthetic": True}, {"mode": "SYNTHETIC"}, {"verdict": "BLOCKED"},
                     {"iss_cap": {"cap_cpu_h": 301, "cap_usec": 301 * 3600 * 10**6}},
                     {"iss_universe": {**AUTH["universe"], "cells": 325}}, {"iss_host": {**AUTH["host"], "host_name": "x"}},
                     {"iss_producer": {**AUTH["producer"], "producer_identity_hash": OTHER}}, {"issuance": None}):
            self.assertTrue(binding(countersignature(ev, **over), git_with(ev)), over)


if __name__ == "__main__":
    unittest.main(verbosity=2)
