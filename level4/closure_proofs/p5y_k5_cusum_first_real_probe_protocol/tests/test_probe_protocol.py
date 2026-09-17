"""Unit tests (r4) of the frozen probe rules and the prelaunch verifier on HYPOTHETICAL inputs only (no real result).

    python3 -B tests/test_probe_protocol.py

Verifier tests build throwaway git repositories (with a local bare 'origin') holding only the packet and the two frozen
adapter sources. Test-only substitutions, stated: the literal FREEZE_PARENT of the loaded copy is set to the throwaway
base commit, the origin allow-list is the throwaway bare repository, and the output namespace is a temp directory.
  F1   r2 forgery (collapsed unpublished commits, review FAIL)                     -> refused
  F2   genuine strictly ordered published activation with launch notice           -> governance checks pass
  V05  review with duplicate verdict lines                                        -> refused (P06)
  V12  template edited after the freeze                                           -> refused (P03)
  V21  unpublished authorization                                                  -> refused (P04, P11)
  V22  local update-ref of the remote-tracking ref                                -> refused (publication check)
  V23  authorization supplied through a symlink                                   -> refused (P02, P04)
  S1   host RUN_FAILED contradicting the committed ledger OUTCOME                  -> refused (P11)
  S2   ledger OUTCOME carrying a sealed record sha256, host seal deleted           -> refused (P09)
"""
from __future__ import annotations

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

TEMPLATE = NS / "protocol/AUTHORIZATION_TEMPLATE_R4.json"
PACKET = ["code/probe_rules.py", "code/prelaunch_verify.py", "tests/test_probe_protocol.py",
          "protocol/SCIENCE_PREREGISTRATION_R4.json", "protocol/AUTHORIZATION_TEMPLATE_R4.json",
          "protocol/EXECUTION_BINDING_R4.json"]
ADAPTER_PINS = ["level4/closure_proofs/p5y_k5_order3_readiness_audit/code/k5_minimality.py",
                "level4/closure_proofs/p5y_k5b_independent_countersignature/code/k5b_check.py"]
GOV = ("P02", "P03", "P04", "P06", "P09", "P11", "P12")


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

    def test_address_and_slots(self):
        kw = dict(k1_record_sha256="a", producer_identity_sha256="b", executor_binding_sha256="c",
                  protocol_sha256="d", precision_bits=256)
        addrs = [PR.scientific_address(m=m, **kw) for m in (1, 2, 3, 5)]
        self.assertEqual(len({a["address_sha256"] for a in addrs}), 4)
        self.assertNotIn("attempt_id", addrs[0]["address"])
        for bad in (dict(kw, m=4), dict(kw, m=1, precision_bits=384)):
            with self.assertRaises(PR.RuleViolation):
                PR.scientific_address(**bad)
        with self.assertRaises(PR.RuleViolation):
            PR.slot_dir(PR.load_prereg()["retry_policy"]["max_slots"] + 1)

    def test_failure_class_is_mechanical(self):
        soft = PR.load_prereg()["cpu_ceiling"]["per_attempt_cpu_seconds_soft"]
        self.assertEqual(PR.failure_class({"signal": 24}), "CPU_RLIMIT")
        self.assertEqual(PR.failure_class({"signal": 9, "child_cpu_seconds": soft + 5}), "CPU_RLIMIT")   # hard-limit kill
        self.assertEqual(PR.failure_class({"signal": 9, "kernel_oom_record": True, "child_cpu_seconds": 10}), "PROCESS_KILLED_OOM")
        self.assertEqual(PR.failure_class({"signal": 9, "child_cpu_seconds": 10}), "PROCESS_KILLED_BY_EXTERNAL_SIGNAL")
        self.assertEqual(PR.failure_class({"boot_id_changed": True, "signal": 9}), "HOST_REBOOT_OR_BOOT_ID_CHANGE")
        self.assertEqual(PR.failure_class({"wall_seconds": 10 ** 6, "signal": 9}), "WALL_TIMEOUT")
        self.assertEqual(PR.failure_class({"integrity_refusal": "Q07", "exit_code": 2}), "INTEGRITY_REFUSAL")
        self.assertEqual(PR.failure_class({"exit_code": 1}), "UNKNOWN_FAILURE")
        transient = set(PR.load_prereg()["retry_policy"]["transient_failure_classes_after_arithmetic"])
        self.assertFalse({"CPU_RLIMIT", "WALL_TIMEOUT", "INTEGRITY_REFUSAL", "UNKNOWN_FAILURE"} & transient)

    def test_qualification_and_retry_and_adoption(self):
        ids = [g["id"] for g in PR.load_prereg()["real_producer_qualification"]["gates"]]
        gates = {i: True for i in ids}
        self.assertEqual(PR.producer_qualification(gates), "PASS")
        gates["Q15_COST_CEILING"] = False
        self.assertEqual(PR.producer_qualification(gates), "FAIL")
        base = {"sealed_record_exists": False, "attempts_started": 1, "arithmetic_started": True}
        self.assertEqual(PR.retry_decision(dict(base, failure_class="DISK_FULL_BEFORE_SEAL"))["decision"], "RETRY_PERMITTED")
        self.assertEqual(PR.retry_decision(dict(base, failure_class="CPU_RLIMIT"))["decision"], "NO_RETRY")
        self.assertEqual(PR.next_rung([256]), None)
        self.assertEqual(PR.adoption_status(sealed=True, science_usable_=True, independent_replay_pass=None,
                                            independent_review_pass=None), "PENDING_INDEPENDENT_ADJUDICATION")

    def test_real_freeze_parent_literal(self):
        intro = subprocess.run(["git", "-C", str(REPO), "log", "--diff-filter=A", "--format=%H", "--",
                                f"{NSR}/protocol/SCIENCE_PREREGISTRATION_R4.json"], capture_output=True, text=True).stdout.split()
        if not intro:
            self.skipTest("r4 science file not committed yet")
        parent = subprocess.run(["git", "-C", str(REPO), "show", "-s", "--format=%P", intro[-1]],
                                capture_output=True, text=True).stdout.split()[0]
        self.assertEqual(parent, PV.FREEZE_PARENT)


def _git(root, *args, when=None, check=True):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    if when is not None:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"@{int(when)} +0000"
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env)
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r.stdout.strip()


class Harness:
    def __init__(self, tmp: Path):
        self.tmp, self.root, self.origin = tmp, tmp / "repo", tmp / "origin.git"
        self.ns = self.root / NSR
        self.outns = tmp / "outns"
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True)
        _git(tmp, "init", "-q", str(self.root))
        _git(self.root, "remote", "add", "origin", str(self.origin))
        self.t = time.time() - 9000
        self.write("BASE", "base\n")
        self.base = self.commit("base")
        for relp in PACKET:
            (self.ns / relp).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(NS / relp, self.ns / relp)
        for relp in ADAPTER_PINS:
            (self.root / relp).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relp, self.root / relp)
        spec = importlib.util.spec_from_file_location(f"pv_{id(self)}", self.ns / "code/prelaunch_verify.py")
        self.pv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.pv)
        self.pv.FREEZE_PARENT = self.base                     # test-only substitution (stated in the module docstring)

    def commit(self, msg):
        self.t += 100
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", msg, when=self.t)
        return _git(self.root, "rev-parse", "HEAD")

    def publish(self):
        _git(self.root, "push", "-q", "-f", "origin", "HEAD:refs/heads/p5y-postk1-frontier")
        _git(self.root, "fetch", "-q", "origin")

    def write(self, relp, content):
        path = self.root / relp
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content if isinstance(content, str) else json.dumps(content, indent=1, sort_keys=True) + "\n")
        return path

    def checks(self, auth_path, ids=GOV):
        prereg = json.loads((self.ns / "protocol/SCIENCE_PREREGISTRATION_R4.json").read_text())
        prereg["output_namespace"] = str(self.outns)          # test-only substitution
        auth = json.loads(Path(auth_path).read_text())
        ctx = {"auth_path": auth_path, "live": None, "allowed_origin_urls": (str(self.origin),)}
        out = {}
        for cid in ("P03",) + tuple(c for c in ids if c != "P03"):
            try:
                ok, detail = getattr(self.pv, f"check_{cid}")(auth, prereg, ctx)
            except Exception as exc:
                ok, detail = False, f"raised {type(exc).__name__}: {exc}"
            out[cid] = (ok is True, detail)
        return out


def build(h, *, forged=False, dup_verdict=False, template_drift=False, unpublished_auth=False, symlink_auth=False,
          ledger_extra=None, slot_dir=None):
    freeze = h.commit("freeze r4")
    h.publish()
    science_sha = PR.sha256((h.ns / "protocol/SCIENCE_PREREGISTRATION_R4.json").read_bytes())
    h.write(f"{NSR}/protocol/FREEZE_RECORD_R4.json", {"freeze_commit": freeze, "science_sha256": science_sha})
    h.commit("freeze record")
    h.publish()
    if template_drift:
        tpl = json.loads((h.ns / "protocol/AUTHORIZATION_TEMPLATE_R4.json").read_text())
        tpl["CELL_SET"] = [221]
        h.write(f"{NSR}/protocol/AUTHORIZATION_TEMPLATE_R4.json", tpl)
        h.commit("template drift")
        h.publish()
    srcs = {}
    for relp, text in (("exec/first_real_probe_executor.py", "# executor\n"), ("exec/k5b_adapter.py", "# adapter\n")):
        h.write(relp, text)
        srcs[relp] = PR.sha256(text.encode())
    for relp in ADAPTER_PINS:
        srcs[relp] = PR.sha256((h.root / relp).read_bytes())
    h.write("exec/evidence.json", {"qualification": "synthetic"})
    verdict = "FAIL" if forged else "PASS"
    extra = "REVIEW_VERDICT: FAIL\n" if dup_verdict else ""
    h.write("exec/REVIEW.md", f"# review\nREVIEW_VERDICT: {verdict}\n{extra}"
                              f"REVIEWED_AMENDMENT_SOURCES_SHA256: {PR.sha256(PR.canonical(srcs))}\n")
    if not forged:
        h.commit("executor, evidence, review")
        h.publish()
    amendment = {"schema": "x", "status": "BOUND_QUALIFIED", "science_preregistration_sha256": science_sha,
                 "executor_entry": "exec/first_real_probe_executor.py", "consumption_adapter_entry": "exec/k5b_adapter.py",
                 "executor_sources_sha256": srcs,
                 "qualification_evidence_sha256": {"exec/evidence.json": PR.sha256((h.root / "exec/evidence.json").read_bytes())},
                 "independent_review": "exec/REVIEW.md", "independent_review_sha256": PR.sha256((h.root / "exec/REVIEW.md").read_bytes()),
                 "independent_review_verdict": "PASS", "amendment_rule_ack": True}
    am_path = h.write(f"{NSR}/protocol/EXECUTION_BINDING_AMENDMENT.json", amendment)
    if not forged:
        h.commit("amendment")
        h.publish()
    auth = json.loads((h.ns / "protocol/AUTHORIZATION_TEMPLATE_R4.json").read_text())
    auth.update({"EXECUTION_AUTHORIZED": True, "PROTOCOL_FREEZE_COMMIT": freeze, "AUTHORIZED_BY": "test",
                 "AUTHORIZATION_UTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(h.t + 100 - 60))})
    auth["PRODUCER_R4_IDENTITY"] = dict(auth["PRODUCER_R4_IDENTITY"], executor_binding_sha256=PR.sha256(am_path.read_bytes()))
    if symlink_auth:
        real = h.write(f"{NSR}/protocol/AUTH_REAL.json", auth)
        link = h.ns / "protocol/AUTHORIZATION_ACTIVE.json"
        os.symlink("AUTH_REAL.json", link)
        auth_path = link
    else:
        auth_path = h.write(f"{NSR}/protocol/AUTHORIZATION_ACTIVE.json", auth)
    h.commit("authorization" if not forged else "amendment + authorization in one commit")
    if not forged and not unpublished_auth:
        h.publish()
    if not forged:
        lines = [{"event": "LAUNCH_NOTICE", "slot": "slot-1", "authorization_sha256": PR.sha256(Path(auth_path).read_bytes())}]
        if slot_dir is not None:
            lines = slot_dir(h, auth_path)
        lines += ledger_extra or []
        h.write(f"{NSR}/ledger/ATTEMPT_LEDGER.jsonl", "".join(json.dumps(x) + "\n" for x in lines))
        h.commit("ledger")
        if not unpublished_auth:
            h.publish()
    return auth_path


class Verifier(unittest.TestCase):
    def run_case(self, **kw):
        with tempfile.TemporaryDirectory() as d:
            h = Harness(Path(d))
            return h.checks(build(h, **kw))

    def assert_refused(self, res, *cids):
        for cid in cids:
            self.assertFalse(res[cid][0], f"{cid} should refuse: {res[cid]}")

    def test_template_refused_first_for_authorization(self):
        rep = PV.verify(TEMPLATE)
        self.assertEqual(rep["verdict"], "REFUSED")
        self.assertTrue(rep["primary_reason"].startswith("P01: EXECUTION_NOT_AUTHORIZED"))

    def test_F2_genuine_activation_passes_governance_checks(self):
        res = self.run_case()
        for cid, (ok, detail) in res.items():
            self.assertTrue(ok, f"{cid}: {detail}")

    def test_F1_r2_forgery_refused(self):
        self.assert_refused(self.run_case(forged=True), "P04", "P06", "P11")

    def test_V05_duplicate_verdict_lines_refused(self):
        res = self.run_case(dup_verdict=True)
        self.assert_refused(res, "P06")
        self.assertIn("exactly one accepted REVIEW_VERDICT", res["P06"][1])

    def test_V12_template_drift_refused(self):
        self.assert_refused(self.run_case(template_drift=True), "P03")

    def test_V21_unpublished_authorization_refused(self):
        self.assert_refused(self.run_case(unpublished_auth=True), "P04", "P11")

    def test_V22_local_update_ref_refused(self):
        with tempfile.TemporaryDirectory() as d:
            h = Harness(Path(d))
            auth_path = build(h, unpublished_auth=True)
            _git(h.root, "update-ref", "refs/remotes/origin/p5y-postk1-frontier", "HEAD")
            res = h.checks(auth_path)
        self.assert_refused(res, "P04", "P11")
        self.assertIn("not published", res["P04"][1])

    def test_V23_symlinked_authorization_refused(self):
        self.assert_refused(self.run_case(symlink_auth=True), "P02", "P04")

    def test_S1_host_record_contradicting_ledger_refused(self):
        def slot(h, auth_path):
            d = h.outns / "slot-1"
            d.mkdir(parents=True)
            info = {"arithmetic_started": False, "supervisor_evidence": {"exit_code": 1}}
            (d / "RUN_FAILED.json").write_text(json.dumps(info))
            return [{"event": "LAUNCH_NOTICE", "slot": "slot-1", "authorization_sha256": "x"},
                    {"event": "OUTCOME", "slot": "slot-1", "arithmetic_started": True, "failure_class": "UNKNOWN_FAILURE",
                     "run_failed_sha256": PR.sha256((d / "RUN_FAILED.json").read_bytes()), "sealed_record_sha256": None},
                    {"event": "LAUNCH_NOTICE", "slot": "slot-2", "authorization_sha256": PR.sha256(Path(auth_path).read_bytes())}]
        res = self.run_case(slot_dir=slot)
        self.assert_refused(res, "P11")

    def test_S2_ledger_sealed_outcome_blocks(self):
        def slot(h, auth_path):
            d = h.outns / "slot-1"
            d.mkdir(parents=True)
            info = {"arithmetic_started": True, "supervisor_evidence": {"signal": 9, "child_cpu_seconds": 10}}
            (d / "RUN_FAILED.json").write_text(json.dumps(info))
            return [{"event": "LAUNCH_NOTICE", "slot": "slot-1", "authorization_sha256": "x"},
                    {"event": "OUTCOME", "slot": "slot-1", "arithmetic_started": True,
                     "failure_class": "PROCESS_KILLED_BY_EXTERNAL_SIGNAL",
                     "run_failed_sha256": PR.sha256((d / "RUN_FAILED.json").read_bytes()), "sealed_record_sha256": "ab" * 32},
                    {"event": "LAUNCH_NOTICE", "slot": "slot-2", "authorization_sha256": PR.sha256(Path(auth_path).read_bytes())}]
        res = self.run_case(slot_dir=slot)
        self.assert_refused(res, "P09")


if __name__ == "__main__":
    unittest.main()
