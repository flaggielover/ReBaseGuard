"""Unit tests (r3) of the frozen probe rules and the prelaunch verifier on HYPOTHETICAL inputs only (no real result).

    python3 -B tests/test_probe_protocol.py

The verifier tests build throwaway git repositories (with a local bare 'origin') that copy only the packet and the two
frozen adapter sources, to exercise the commit / publication / review / ledger anchors end to end:
  F1  the r2 forgery (amendment and authorization in one unpublished commit, review file says FAIL) -> refused
  F2  a genuine activation (strictly ordered published commits, review PASS naming the sources, launch notice) -> the
      governance checks P02, P03, P04, P06, P11 pass (so a real activation is not impossible)
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
NSR = str(NS.relative_to(REPO))
sys.path.insert(0, str(NS / "code"))

import prelaunch_verify as PV  # noqa: E402
import probe_rules as PR  # noqa: E402

TEMPLATE = NS / "protocol/AUTHORIZATION_TEMPLATE_R3.json"
PACKET = ["code/probe_rules.py", "code/prelaunch_verify.py", "tests/test_probe_protocol.py",
          "protocol/SCIENCE_PREREGISTRATION_R3.json", "protocol/AUTHORIZATION_TEMPLATE_R3.json",
          "protocol/EXECUTION_BINDING_R3.json"]
ADAPTER_PINS = ["level4/closure_proofs/p5y_k5_order3_readiness_audit/code/k5_minimality.py",
                "level4/closure_proofs/p5y_k5b_independent_countersignature/code/k5b_check.py"]


class Rules(unittest.TestCase):
    def test_transport_uses_frozen_x1_and_refuses_floats(self):
        x1 = F(5083, 10 ** 7)
        self.assertEqual(PR.transport(F(10), F(12), F(4)), (10 - x1 * x1 * 2, 12 + x1 * x1 * 2))
        for bad in ((1, 2, 3, F(1, 2)), (1.0, 2, 3, None), (3, 2, 1, None)):
            with self.assertRaises(PR.RuleViolation):
                PR.transport(*bad[:3], x1=bad[3])

    def test_three_way_verdict_boundaries(self):
        self.assertEqual(PR.scientific_verdict(F(1, 10 ** 9), 5), PR.SUPPORTS)
        self.assertEqual(PR.scientific_verdict(0, 5), PR.INCONCLUSIVE)
        self.assertEqual(PR.scientific_verdict(-5, 0), PR.INCONCLUSIVE)
        self.assertEqual(PR.scientific_verdict(-5, F(-1, 10 ** 9)), PR.CONTRADICTS)

    def test_point_negative_routes_to_negative_consumption(self):
        L1, U1 = PR.transport(-10, -1, 10 ** 9)
        v, pt = PR.scientific_verdict(L1, U1), PR.point_sign(-10, -1)
        self.assertEqual((v, PR.consumption_key(v, pt)), (PR.INCONCLUSIVE, "NEGATIVE"))
        self.assertTrue(PR.k5b_consumption(v, pt)["h3a_viable"].startswith("no"))

    def test_consumption_map_complete(self):
        for v, pt in ((PR.SUPPORTS, "POINT_POSITIVE"), (PR.INCONCLUSIVE, "POINT_UNDETERMINED"),
                      (PR.CONTRADICTS, "POINT_NEGATIVE"), (PR.VOID, "POINT_UNDETERMINED")):
            for field in ("k5b_step", "cells_closed_by_theorem", "cells_remaining_open", "restart",
                          "next_order3_informative", "h3a_viable"):
                self.assertIn(field, PR.k5b_consumption(v, pt))

    def test_aggregate_routes_and_whole_record_void(self):
        sup = {"verdict": PR.SUPPORTS, "point": "POINT_POSITIVE"}
        inc = {"verdict": PR.INCONCLUSIVE, "point": "POINT_UNDETERMINED"}
        neg = {"verdict": PR.INCONCLUSIVE, "point": "POINT_NEGATIVE"}
        void = {"verdict": PR.VOID, "point": "POINT_UNDETERMINED"}
        self.assertEqual(PR.aggregate({1: sup, 2: sup, 3: sup, 5: sup})["label"], "FIRST_CELL_SUPPORTED_ALL_M")
        self.assertEqual(PR.aggregate({1: sup, 2: inc, 3: sup, 5: sup})["label"],
                         "FIRST_CELL_SUPPORTED_SOME_M_UNRESOLVED_OTHERS")
        self.assertEqual(PR.aggregate({1: sup, 2: sup, 3: sup, 5: neg})["label"], "CUSUM_H3A_TARGET_REFUTED_FOR_SOME_M")
        self.assertEqual(PR.aggregate({1: void, 2: void, 3: void, 5: void})["label"], "VOID")
        for bad in ({1: sup, 2: sup, 3: sup}, {1: void, 2: neg, 3: sup, 5: sup}):
            with self.assertRaises(PR.RuleViolation):
                PR.aggregate(bad)

    def test_address_has_no_attempt_id_and_is_unique_per_m(self):
        kw = dict(k1_record_sha256="a", producer_identity_sha256="b", executor_binding_sha256="c",
                  protocol_sha256="d", precision_bits=256)
        addrs = [PR.scientific_address(m=m, **kw) for m in (1, 2, 3, 5)]
        self.assertEqual(len({a["address_sha256"] for a in addrs}), 4)
        self.assertNotIn("attempt_id", addrs[0]["address"])
        for bad in (dict(kw, m=4), dict(kw, m=1, precision_bits=384)):
            with self.assertRaises(PR.RuleViolation):
                PR.scientific_address(**bad)
        self.assertEqual(PR.slot_dir(1), "slot-1")
        with self.assertRaises(PR.RuleViolation):
            PR.slot_dir(PR.load_prereg()["retry_policy"]["max_slots"] + 1)

    def test_failure_class_is_mechanical(self):
        self.assertEqual(PR.failure_class({"signal": 24}), "CPU_RLIMIT")
        self.assertEqual(PR.failure_class({"signal": 9, "kernel_oom_record": True}), "PROCESS_KILLED_OOM")
        self.assertEqual(PR.failure_class({"signal": 9}), "PROCESS_KILLED_BY_EXTERNAL_SIGNAL")
        self.assertEqual(PR.failure_class({"signal": 9, "cpu_soft_limit_reached": True}), "CPU_RLIMIT")
        self.assertEqual(PR.failure_class({"boot_id_changed": True, "signal": 9}), "HOST_REBOOT_OR_BOOT_ID_CHANGE")
        self.assertEqual(PR.failure_class({"integrity_refusal": "Q07", "exit_code": 2}), "INTEGRITY_REFUSAL")
        self.assertEqual(PR.failure_class({"exit_code": 1}), "UNKNOWN_FAILURE")
        transient = set(PR.load_prereg()["retry_policy"]["transient_failure_classes_after_arithmetic"])
        self.assertFalse({"CPU_RLIMIT", "WALL_TIMEOUT", "INTEGRITY_REFUSAL", "UNKNOWN_FAILURE"} & transient)

    def test_qualification_sign_independent_and_q15(self):
        ids = [g["id"] for g in PR.load_prereg()["real_producer_qualification"]["gates"]]
        gates = {i: True for i in ids}
        self.assertEqual(PR.producer_qualification(gates), "PASS")
        gates["Q07_INTERVAL_CONSISTENCY"] = False
        self.assertEqual((PR.producer_qualification(gates), PR.science_usable(gates)), ("FAIL", False))
        gates = {i: True for i in ids}
        gates["Q15_COST_CEILING"] = False
        self.assertEqual(PR.producer_qualification(gates), "FAIL")

    def test_retry_attempt_model(self):
        base = {"sealed_record_exists": False, "attempts_started": 1}
        self.assertEqual(PR.retry_decision(dict(base, arithmetic_started=False, failure_class="INTEGRITY_REFUSAL"))["decision"],
                         "NOT_AN_ATTEMPT_RELAUNCH_AFTER_VERIFIER")
        self.assertEqual(PR.retry_decision(dict(base, arithmetic_started=True, failure_class="DISK_FULL_BEFORE_SEAL"))["decision"],
                         "RETRY_PERMITTED")
        for cls in ("INTEGRITY_REFUSAL", "CPU_RLIMIT", "WALL_TIMEOUT", "UNKNOWN_FAILURE"):
            self.assertEqual(PR.retry_decision(dict(base, arithmetic_started=True, failure_class=cls))["decision"], "NO_RETRY")
        self.assertEqual(PR.retry_decision(dict(base, arithmetic_started=True, sealed_record_exists=True,
                                                failure_class="DISK_FULL_BEFORE_SEAL"))["decision"], "NO_RETRY")
        self.assertEqual(PR.next_rung([]), 256)
        self.assertIsNone(PR.next_rung([256]))

    def test_adoption_requires_independent_adjudication(self):
        self.assertEqual(PR.adoption_status(sealed=True, science_usable_=True, independent_replay_pass=None,
                                            independent_review_pass=None), "PENDING_INDEPENDENT_ADJUDICATION")
        self.assertEqual(PR.adoption_status(sealed=True, science_usable_=True, independent_replay_pass=True,
                                            independent_review_pass=True), "ADOPTED")


def _git(root, *args, when=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    if when is not None:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"@{int(when)} +0000"
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r.stdout.strip()


class Harness:
    """A throwaway repository with the packet at its real relative path and a local bare origin."""

    def __init__(self, tmp: Path):
        self.root, self.origin = tmp / "repo", tmp / "origin.git"
        self.ns = self.root / NSR
        for relp in PACKET:
            (self.ns / relp).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(NS / relp, self.ns / relp)
        for relp in ADAPTER_PINS:
            (self.root / relp).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relp, self.root / relp)
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True)
        _git(self.root.parent, "init", "-q", str(self.root))
        _git(self.root, "remote", "add", "origin", str(self.origin))
        self.t = time.time() - 5000
        spec = importlib.util.spec_from_file_location(f"pv_{id(self)}", self.ns / "code/prelaunch_verify.py")
        self.pv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.pv)

    def commit(self, msg: str) -> str:
        self.t += 100
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", msg, when=self.t)
        return _git(self.root, "rev-parse", "HEAD")

    def publish(self):
        _git(self.root, "push", "-q", "origin", "HEAD:refs/heads/p5y-postk1-frontier")
        _git(self.root, "fetch", "-q", "origin")

    def write(self, relp: str, content) -> Path:
        path = self.root / relp
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content if isinstance(content, str) else json.dumps(content, indent=1, sort_keys=True) + "\n")
        return path

    def checks(self, auth_path: Path, ids=("P02", "P03", "P04", "P06", "P11")) -> dict:
        prereg = json.loads((self.ns / "protocol/SCIENCE_PREREGISTRATION_R3.json").read_text())
        auth = json.loads(auth_path.read_text())
        ctx = {"auth_path": auth_path, "remote_ref": "origin/p5y-postk1-frontier", "live": None}
        out = {}
        for cid in ("P03",) + tuple(c for c in ids if c != "P03"):
            try:
                ok, detail = getattr(self.pv, f"check_{cid}")(auth, prereg, ctx)
            except Exception as exc:
                ok, detail = False, f"raised {type(exc).__name__}: {exc}"
            out[cid] = (ok is True, detail)
        return out


def _build(h: Harness, *, forged: bool) -> Path:
    freeze = h.commit("freeze r3")
    h.publish()
    science_sha = PR.sha256((h.ns / "protocol/SCIENCE_PREREGISTRATION_R3.json").read_bytes())
    h.write(f"{NSR}/protocol/FREEZE_RECORD_R3.json", {"freeze_commit": freeze, "science_sha256": science_sha})
    h.commit("freeze record")
    h.publish()
    srcs = {}
    for relp, text in (("exec/first_real_probe_executor.py", "# executor\n"), ("exec/k5b_adapter.py", "# adapter\n")):
        h.write(relp, text)
        srcs[relp] = PR.sha256(text.encode())
    for relp in ADAPTER_PINS:
        srcs[relp] = PR.sha256((h.root / relp).read_bytes())
    h.write("exec/evidence.json", {"qualification": "synthetic"})
    verdict = "FAIL" if forged else "PASS"
    h.write("exec/REVIEW.md", f"# review\nREVIEW_VERDICT: {verdict}\nREVIEWED_AMENDMENT_SOURCES_SHA256: {PR.sha256(PR.canonical(srcs))}\n")
    if not forged:
        h.commit("executor, evidence, review")
        h.publish()
    amendment = {"schema": "x", "status": "BOUND_QUALIFIED", "science_preregistration_sha256": science_sha,
                 "executor_entry": "exec/first_real_probe_executor.py", "consumption_adapter_entry": "exec/k5b_adapter.py",
                 "executor_sources_sha256": srcs,
                 "qualification_evidence_sha256": {"exec/evidence.json": PR.sha256((h.root / "exec/evidence.json").read_bytes())},
                 "independent_review": "exec/REVIEW.md",
                 "independent_review_sha256": PR.sha256((h.root / "exec/REVIEW.md").read_bytes()),
                 "independent_review_verdict": "PASS", "amendment_rule_ack": True}
    am_path = h.write(f"{NSR}/protocol/EXECUTION_BINDING_AMENDMENT.json", amendment)
    if not forged:
        h.commit("amendment")
        h.publish()
    auth = json.loads((h.ns / "protocol/AUTHORIZATION_TEMPLATE_R3.json").read_text())
    auth.update({"EXECUTION_AUTHORIZED": True, "PROTOCOL_FREEZE_COMMIT": freeze, "AUTHORIZED_BY": "test",
                 "AUTHORIZATION_UTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(h.t + 100 - 60))})
    auth["PRODUCER_R4_IDENTITY"] = dict(auth["PRODUCER_R4_IDENTITY"], executor_binding_sha256=PR.sha256(am_path.read_bytes()))
    auth_path = h.write(f"{NSR}/protocol/AUTHORIZATION_ACTIVE.json", auth)
    h.commit("authorization" if not forged else "amendment + authorization in one commit")
    if not forged:
        h.publish()
        h.write(f"{NSR}/ledger/ATTEMPT_LEDGER.jsonl", json.dumps({"event": "LAUNCH_NOTICE", "slot": "slot-1",
                "authorization_sha256": PR.sha256(auth_path.read_bytes())}) + "\n")
        h.commit("launch notice")
        h.publish()
    return auth_path


class Verifier(unittest.TestCase):
    def test_template_refused_first_for_authorization(self):
        rep = PV.verify(TEMPLATE)
        self.assertEqual(rep["verdict"], "REFUSED")
        self.assertTrue(rep["primary_reason"].startswith("P01: EXECUTION_NOT_AUTHORIZED"))
        self.assertFalse(rep["checks"]["P06"]["pass"])

    def test_extra_keys_and_template_drift_refused(self):
        a = json.loads(TEMPLATE.read_text())
        a.update({"EXECUTION_AUTHORIZED": True, "M_SET": [1], "OUTPUT_NAMESPACE": "/tmp/x", "EXTRA": 1,
                  "PROTOCOL_SHA256": "0" * 64})
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "AUTHORIZATION_ACTIVE.json"
            p.write_text(json.dumps(a))
            detail = PV.verify(p)["checks"]["P02"]["detail"]
        for text in ("fixed path", "M_SET", "OUTPUT_NAMESPACE", "EXTRA", "PROTOCOL_SHA256", "activation field"):
            self.assertIn(text, detail)

    def test_F1_r2_forgery_refused(self):
        with tempfile.TemporaryDirectory() as d:
            h = Harness(Path(d))
            res = h.checks(_build(h, forged=True))
        self.assertFalse(res["P04"][0], res["P04"])
        self.assertIn("strictly ordered", res["P04"][1])
        self.assertFalse(res["P06"][0], res["P06"])
        self.assertIn("review file verdict is FAIL", res["P06"][1])
        self.assertFalse(res["P11"][0], res["P11"])

    def test_F2_genuine_activation_passes_governance_checks(self):
        with tempfile.TemporaryDirectory() as d:
            h = Harness(Path(d))
            res = h.checks(_build(h, forged=False))
        for cid, (ok, detail) in res.items():
            self.assertTrue(ok, f"{cid}: {detail}")


if __name__ == "__main__":
    unittest.main()
