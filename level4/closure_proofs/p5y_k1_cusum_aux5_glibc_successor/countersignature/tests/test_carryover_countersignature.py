"""Adversarial tests for the CUSUM Aux5 new-glibc carry-over countersignature.

Governance only: every mutation happens on a temporary copy of the successor namespace or through an injected git
reader. No certifier runs, no runtime root is touched, nothing is authorized.

  python -B countersignature/tests/test_carryover_countersignature.py
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import carryover_countersignature as C                                          # noqa: E402

G, R = C.G, C.R
HAVE_CS = (G.NS / C.CS_REL).is_file()
IS_GIT = (G.REPO / ".git").exists()
RUN_LOG = "evidence/requalification_r1/qualification_r1/c318_A/run.log"


def git_ok(_repo):
    return {"trees": dict(C.PROTECTED_TREES), "ancestors": {k: True for k in C.COMMITS}, "dirty": []}


class Copy:
    def __enter__(self):
        self.d = tempfile.TemporaryDirectory()
        self.ns = Path(self.d.name) / "ns"
        shutil.copytree(G.NS, self.ns, ignore=shutil.ignore_patterns("__pycache__"))
        return self.ns

    def __exit__(self, *exc):
        self.d.cleanup()


def load_cs(ns):
    return json.loads((ns / C.CS_REL).read_bytes())


def write_cs(ns, cs):
    """Rewrite the countersignature consistently with its hash file, so only the semantic change is under test."""
    data = G.dump(cs)
    (ns / C.CS_REL).write_bytes(data)
    (ns / C.CS_HASH_REL).write_text(G.sha256_bytes(data) + "\n")


def has(problems, prefix):
    return any(x.startswith(prefix) for x in problems)


@unittest.skipUnless(HAVE_CS, "the countersignature is issued first")
class CountersignatureTests(unittest.TestCase):
    def verify(self, ns, reader=git_ok):
        return C.verify_countersignature(ns, G.REPO, git_reader=reader)

    @unittest.skipUnless(IS_GIT, "needs a git checkout")
    def test_committed_countersignature_verifies_against_git(self):
        self.assertEqual(C.verify_countersignature(), [])

    def test_valid_countersignature_passes_and_grants_carryover_only(self):
        with Copy() as ns:
            self.assertEqual(self.verify(ns), [])
            cs = load_cs(ns)
            self.assertIs(cs["authorizations"]["CARRYOVER_AUTHORIZED"], True)
            self.assertIs(cs["authorizations"]["PRODUCTION_LAUNCH_AUTHORIZED"], False)
            self.assertIs(cs["authorizations"]["SUCCESSOR_CHECKPOINT_CREATED"], False)
            self.assertFalse((ns / "config/GLIBC_SUCCESSOR_CHECKPOINT.json").exists())

    def test_altered_q6_result_fails(self):
        with Copy() as ns:
            p = ns / R.RESULT_REL
            before = p.read_bytes()
            p.write_bytes(before.replace(b'"Q6_FINAL": "PASS"', b'"Q6_FINAL": "FAIL"', 1))
            self.assertNotEqual(p.read_bytes(), before)
            probs = self.verify(ns)
            self.assertTrue(has(probs, "BOUND_HASH: evidence/requalification_r1/Q6_RESULT.json"), probs)
            self.assertTrue(has(probs, "Q6: "), probs)
            self.assertTrue(has(probs, "LAUNCH_READINESS"), probs)

    def test_missing_run_log_fails_q6_rebuild(self):
        with Copy() as ns:
            (ns / RUN_LOG).unlink()
            probs = self.verify(ns)
            self.assertTrue(any("Q6_RESULT_DOES_NOT_REBUILD" in x for x in probs), probs)
            self.assertTrue(has(probs, f"BOUND_HASH: {RUN_LOG} missing"), probs)
            self.assertTrue(has(probs, "COUNTERSIGNATURE_DOES_NOT_REBUILD"), probs)

    def test_changed_predecessor_binding_fails(self):
        with Copy() as ns:
            p = ns / "config/PREDECESSOR_BINDING.json"
            b = json.loads(p.read_bytes())
            b["accounting"]["settled_usec"] -= 70947
            p.write_bytes(G.dump(b))
            probs = self.verify(ns)
            self.assertTrue(has(probs, "BOUND_HASH: config/PREDECESSOR_BINDING.json changed"), probs)
            self.assertTrue(has(probs, "Q6: "), probs)

    def test_changed_proposal_fails(self):
        with Copy() as ns:
            p = ns / "config/GLIBC_SUCCESSOR_PROPOSAL.json"
            m = json.loads(p.read_bytes())
            m["result_set"]["OLD_CARRYOVER"] = [0, 128]
            p.write_bytes(G.dump(m))
            probs = self.verify(ns)
            self.assertTrue(has(probs, "BOUND_HASH: config/GLIBC_SUCCESSOR_PROPOSAL.json changed"), probs)
            self.assertTrue(has(probs, "Q6: "), probs)

    def test_changed_carryover_partition_fails(self):
        with Copy() as ns:
            base = load_cs(ns)
            for old, new in (([0, 128], [128, 325]), ([0, 127], [127, 325]), ([0, 126], [128, 325]), ([0, 127], [128, 326])):
                with self.subTest(old=old, new=new):
                    cs = copy.deepcopy(base)
                    cs["partition"]["OLD_CARRYOVER"], cs["partition"]["NEW_SUCCESSOR"] = old, new
                    write_cs(ns, cs)
                    probs = self.verify(ns)
                    self.assertTrue(has(probs, "PARTITION"), probs)
                    self.assertTrue(has(probs, "COUNTERSIGNATURE_DOES_NOT_REBUILD"), probs)

    def test_changed_cpu_values_fail(self):
        with Copy() as ns:
            base = load_cs(ns)
            for key, value in (("SUCCESSOR_RESIDUAL_CAP_US", 817313389419), ("SUCCESSOR_RESIDUAL_CAP_US", 1080000000000),
                               ("ABSOLUTE_CAP_US", 1083600000000), ("PREDECESSOR_SETTLED_CPU_US", 262686468127),
                               ("ADMISSION_INVARIANT", [100, 100])):
                with self.subTest(key=key, value=value):
                    cs = copy.deepcopy(base)
                    cs["cpu_continuity"][key] = value
                    write_cs(ns, cs)
                    self.assertTrue(has(self.verify(ns), f"CPU: {key}"))

    def test_each_missing_condition_fails(self):
        with Copy() as ns:
            base = load_cs(ns)
            for k in "abcde":
                with self.subTest(condition=k):
                    cs = copy.deepcopy(base)
                    del cs["conditions"][k]
                    write_cs(ns, cs)
                    self.assertTrue(has(self.verify(ns), f"CONDITION_MISSING: ({k})"))

    def test_weakened_conditions_fail(self):
        with Copy() as ns:
            base = load_cs(ns)
            for k, token in (("b", "D_unsettled_supervisor_runs"), ("d", "PRODUCTION_LAUNCH_AUTHORIZED = NO"),
                             ("c", G.EXPECTED["checkpoint_sha256"]), ("e", "reboot"), ("a", "128-325")):
                with self.subTest(condition=k):
                    cs = copy.deepcopy(base)
                    cs["conditions"][k] = cs["conditions"][k].replace(token, "")
                    write_cs(ns, cs)
                    probs = self.verify(ns)
                    self.assertTrue(has(probs, f"CONDITION_WEAKENED: ({k})"), probs)

    def test_missing_or_altered_clause_adjudication_fails(self):
        with Copy() as ns:
            base = load_cs(ns)
            mutations = {
                "CLAUSE_ADJUDICATION_MISSING": lambda cs: cs.pop("opposing_clause_adjudication"),
                "CLAUSE_ADJUDICATION: quote": lambda cs: cs["opposing_clause_adjudication"].update(quote="Old records are evidence."),
                "CLAUSE_ADJUDICATION: finding": lambda cs: cs["opposing_clause_adjudication"].update(finding="PROHIBITIVE"),
                "CLAUSE_ADJUDICATION: reason missing": lambda cs: cs["opposing_clause_adjudication"]["reasons"].pop(
                    "R3_no_resume_or_import_transition"),
            }
            for code, mutate in mutations.items():
                with self.subTest(code=code):
                    cs = copy.deepcopy(base)
                    mutate(cs)
                    write_cs(ns, cs)
                    self.assertTrue(has(self.verify(ns), code))

    def test_launch_authorization_claim_fails(self):
        with Copy() as ns:
            cs = load_cs(ns)
            cs["authorizations"]["PRODUCTION_LAUNCH_AUTHORIZED"] = True
            write_cs(ns, cs)
            self.assertTrue(has(self.verify(ns), "AUTHORIZATIONS: a countersignature can never authorize production launch"))

    def test_protected_tree_change_fails(self):
        rel = next(iter(C.PROTECTED_TREES))
        changed = lambda repo: {**git_ok(repo), "trees": {**C.PROTECTED_TREES, rel: "0" * 40}}   # noqa: E731
        dirty = lambda repo: {**git_ok(repo), "dirty": [f" M {rel}/config/x.json"]}               # noqa: E731
        orphan = lambda repo: {**git_ok(repo), "ancestors": {**git_ok(repo)["ancestors"], "q6_evidence_repair_commit": False}}  # noqa: E731

        def no_git(_repo):
            raise ValueError("not a git checkout")
        for reader, code in ((changed, "PROTECTED_TREE_CHANGED"), (dirty, "PROTECTED_TREE_DIRTY"),
                             (orphan, "COMMIT_NOT_IN_HISTORY"), (no_git, "PROTECTED_TREES_UNVERIFIABLE")):
            with self.subTest(code=code):
                self.assertTrue(has(self.verify(G.NS, reader), code))

    def test_hash_file_mismatch_fails(self):
        with Copy() as ns:
            (ns / C.CS_HASH_REL).write_text("0" * 64 + "\n")
            self.assertTrue(has(self.verify(ns), "COUNTERSIGNATURE_HASH_FILE"))

    def test_tampered_adjudication_record_fails(self):
        with Copy() as ns:
            p = ns / C.RECORD_REL
            p.write_text(p.read_text().replace("NOT_PROHIBITIVE", "PROHIBITIVE"))
            self.assertTrue(has(self.verify(ns), "COUNTERSIGNATURE_DOES_NOT_REBUILD"))

    def test_signing_must_be_independent_and_match_bound_state(self):
        with Copy() as ns:
            base = load_cs(ns)
            mutations = {
                "SIGNING: reviewer not independent": lambda s: s.update(reviewer_independent_of_authoring_session=False),
                "SIGNING: live observation boot_id": lambda s: s["live_host_observation"].update(boot_id="rebooted"),
                "SIGNING: live observation certifier_or_ledger_processes":
                    lambda s: s["live_host_observation"].update(certifier_or_ledger_processes=1),
                "SIGNING: phase A item 09_origin_main_unchanged":
                    lambda s: s["phase_a_reverification"].update({"09_origin_main_unchanged": "FAIL"}),
            }
            for code, mutate in mutations.items():
                with self.subTest(code=code):
                    cs = copy.deepcopy(base)
                    mutate(cs["signing"])
                    write_cs(ns, cs)
                    self.assertTrue(has(self.verify(ns), code))

    def test_countersignature_alone_cannot_make_launch_readiness_pass(self):
        raw = (G.NS / C.CS_REL).read_bytes()
        cs = json.loads(raw)
        rep = C.launch_readiness_with_countersignature_only(G.NS, cs, raw)
        self.assertEqual(rep["state"], "NOT_READY")
        self.assertEqual(rep["problems"], ["SUCCESSOR_CHECKPOINT_ABSENT"])
        self.assertFalse(rep["CARRYOVER_AUTHORIZED"])
        q6_raw = (G.NS / R.RESULT_REL).read_bytes()
        q6 = G.evaluate_q6(json.loads(q6_raw), json.loads((G.NS / "config/Q6_REFERENCE.json").read_bytes()),
                           result_sha256=G.sha256_bytes(q6_raw))
        bogus = {"schema": G.CHECKPOINT_SCHEMA, "proposal_sha256": cs["proposal_sha256"]}
        rep2 = G.launch_readiness(proposal_problems=[], proposal_sha256=cs["proposal_sha256"], q6=q6, countersignature=cs,
                                  countersignature_sha256=G.sha256_bytes(raw), checkpoint=bogus)
        self.assertEqual((rep2["state"], rep2["problems"]), ("NOT_READY", ["SUCCESSOR_CHECKPOINT_INVALID"]))
        with contextlib.redirect_stdout(io.StringIO()):
            rc = G.main(["launch-readiness", "--q6", str(G.NS / R.RESULT_REL), "--countersignature", str(G.NS / C.CS_REL)])
        self.assertEqual(rc, 30)

    def test_build_never_overwrites_an_issued_countersignature(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(C.main(["build", "--signing", str(G.NS / C.CS_REL)]), 30)


if __name__ == "__main__":
    unittest.main()
