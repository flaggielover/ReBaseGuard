"""Unit tests (r2) of the frozen probe rules and the prelaunch verifier on HYPOTHETICAL inputs only (no real result).

    python3 -B tests/test_probe_protocol.py
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import prelaunch_verify as PV  # noqa: E402
import probe_rules as PR  # noqa: E402

TEMPLATE = NS / "protocol/AUTHORIZATION_TEMPLATE_R2.json"


def complete_forgery() -> dict:
    """Every field filled and the flag true, but not committed at the fixed path and no executor amendment."""
    a = json.loads(TEMPLATE.read_text())
    a["EXECUTION_AUTHORIZED"] = True
    a["PROTOCOL_FREEZE_COMMIT"] = "0" * 40
    a["PRODUCER_R4_IDENTITY"]["executor_binding_sha256"] = "f" * 64
    a["AUTHORIZED_BY"] = "forger"
    a["AUTHORIZATION_UTC"] = "1970-01-01T00:00:00Z"
    return a


class Rules(unittest.TestCase):
    def test_transport_uses_frozen_x1_and_refuses_floats(self):
        x1 = F(5083, 10 ** 7)
        L1, U1 = PR.transport(F(10), F(12), F(4))
        self.assertEqual((L1, U1), (10 - x1 * x1 * 2, 12 + x1 * x1 * 2))
        with self.assertRaises(PR.RuleViolation):
            PR.transport(1, 2, 3, x1=F(1, 2))                                          # another cell refused
        with self.assertRaises(PR.RuleViolation):
            PR.transport(1.0, 2, 3)
        with self.assertRaises(PR.RuleViolation):
            PR.transport(3, 2, 1)

    def test_three_way_verdict_boundaries(self):
        self.assertEqual(PR.scientific_verdict(F(1, 10 ** 9), 5), PR.SUPPORTS)
        self.assertEqual(PR.scientific_verdict(0, 5), PR.INCONCLUSIVE)
        self.assertEqual(PR.scientific_verdict(-5, 0), PR.INCONCLUSIVE)
        self.assertEqual(PR.scientific_verdict(-5, F(-1, 10 ** 9)), PR.CONTRADICTS)

    def test_point_negative_routes_to_negative_consumption(self):
        L1, U1 = PR.transport(-10, -1, 10 ** 9)
        v, pt = PR.scientific_verdict(L1, U1), PR.point_sign(-10, -1)
        self.assertEqual(v, PR.INCONCLUSIVE)
        self.assertEqual(PR.h3a_consequence(v, pt), "H3A_FALSE_FOR_THIS_M")
        self.assertEqual(PR.consumption_key(v, pt), "NEGATIVE")
        self.assertTrue(PR.k5b_consumption(v, pt)["h3a_viable"].startswith("no"))

    def test_consumption_map_complete(self):
        for v, pt in ((PR.SUPPORTS, "POINT_POSITIVE"), (PR.INCONCLUSIVE, "POINT_UNDETERMINED"),
                      (PR.CONTRADICTS, "POINT_NEGATIVE"), (PR.VOID, "POINT_UNDETERMINED")):
            entry = PR.k5b_consumption(v, pt)
            for field in ("k5b_step", "cells_closed_by_theorem", "cells_remaining_open", "restart",
                          "next_order3_informative", "h3a_viable"):
                self.assertIn(field, entry)

    def test_aggregate_routes(self):
        sup = {"verdict": PR.SUPPORTS, "point": "POINT_POSITIVE"}
        inc = {"verdict": PR.INCONCLUSIVE, "point": "POINT_UNDETERMINED"}
        neg = {"verdict": PR.INCONCLUSIVE, "point": "POINT_NEGATIVE"}
        self.assertEqual(PR.aggregate({1: sup, 2: sup, 3: sup, 5: sup})["label"], "FIRST_CELL_SUPPORTED_ALL_M")
        self.assertEqual(PR.aggregate({1: sup, 2: inc, 3: sup, 5: sup})["label"],
                         "FIRST_CELL_SUPPORTED_SOME_M_UNRESOLVED_OTHERS")
        self.assertEqual(PR.aggregate({1: sup, 2: sup, 3: sup, 5: neg})["label"], "CUSUM_H3A_TARGET_REFUTED_FOR_SOME_M")
        with self.assertRaises(PR.RuleViolation):
            PR.aggregate({1: sup, 2: sup, 3: sup})

    def test_address_has_no_attempt_id_and_is_unique_per_m(self):
        kw = dict(k1_record_sha256="a", producer_identity_sha256="b", executor_binding_sha256="c",
                  protocol_sha256="d", precision_bits=256)
        addrs = [PR.scientific_address(m=m, **kw) for m in (1, 2, 3, 5)]
        self.assertEqual(len({a["address_sha256"] for a in addrs}), 4)
        self.assertNotIn("attempt_id", addrs[0]["address"])
        self.assertEqual(PR.scientific_address(m=1, **kw), addrs[0])                    # stable across attempts
        with self.assertRaises(PR.RuleViolation):
            PR.scientific_address(m=4, **kw)
        with self.assertRaises(PR.RuleViolation):
            PR.scientific_address(m=1, **dict(kw, precision_bits=384))
        self.assertEqual(PR.attempt_dir(1), "attempt-1")
        with self.assertRaises(PR.RuleViolation):
            PR.attempt_dir(4)

    def test_qualification_is_sign_independent(self):
        ids = [g["id"] for g in PR.load_prereg()["real_producer_qualification"]["gates"]]
        gates = {i: True for i in ids}
        self.assertEqual(PR.producer_qualification(gates), "PASS")
        gates["Q07_INTERVAL_CONSISTENCY"] = False
        self.assertEqual(PR.producer_qualification(gates), "FAIL")
        self.assertFalse(PR.science_usable(gates))
        gates = {i: True for i in ids}
        gates["Q15_COST_CEILING"] = False
        self.assertTrue(PR.science_usable(gates))

    def test_retry_attempt_model(self):
        base = {"sealed_record_exists": False, "attempts_started": 1}
        self.assertEqual(PR.retry_decision(dict(base, arithmetic_started=False, failure_class="HOST_DRIFT"))["decision"],
                         "NOT_AN_ATTEMPT_RELAUNCH_AFTER_VERIFIER")
        self.assertEqual(PR.retry_decision(dict(base, arithmetic_started=True, failure_class="DISK_FULL_BEFORE_SEAL"))["decision"],
                         "RETRY_PERMITTED")
        for cls in ("ProducerRefusal", "CPU_RLIMIT_SIGXCPU", "PRELAUNCH_OR_INITIAL_GATE_REFUSAL_BEFORE_ARITHMETIC"):
            self.assertEqual(PR.retry_decision(dict(base, arithmetic_started=True, failure_class=cls))["decision"], "NO_RETRY")
        self.assertEqual(PR.retry_decision(dict(base, arithmetic_started=True, sealed_record_exists=True,
                                                failure_class="DISK_FULL_BEFORE_SEAL"))["decision"], "NO_RETRY")
        self.assertEqual(PR.retry_decision(dict(base, arithmetic_started=True, attempts_started=3,
                                                failure_class="DISK_FULL_BEFORE_SEAL"))["decision"], "NO_RETRY")
        self.assertEqual(PR.next_rung([]), 256)
        self.assertIsNone(PR.next_rung([256]))

    def test_adoption_requires_independent_adjudication(self):
        self.assertEqual(PR.adoption_status(sealed=True, science_usable_=True, independent_replay_pass=None,
                                            independent_review_pass=None), "PENDING_INDEPENDENT_ADJUDICATION")
        self.assertEqual(PR.adoption_status(sealed=True, science_usable_=True, independent_replay_pass=True,
                                            independent_review_pass=True), "ADOPTED")
        self.assertEqual(PR.adoption_status(sealed=True, science_usable_=False, independent_replay_pass=True,
                                            independent_review_pass=True), "NOT_ADOPTABLE")


class Verifier(unittest.TestCase):
    def _verify(self, auth: dict, name="a.json"):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / name
            p.write_text(json.dumps(auth))
            return PV.verify(p)

    def test_template_refused_first_for_authorization(self):
        rep = PV.verify(TEMPLATE)
        self.assertEqual(rep["verdict"], "REFUSED")
        self.assertTrue(rep["primary_reason"].startswith("P01: EXECUTION_NOT_AUTHORIZED"))
        self.assertFalse(rep["checks"]["P06"]["pass"])

    def test_complete_forgery_refused(self):
        rep = self._verify(complete_forgery(), "AUTHORIZATION_ACTIVE.json")
        self.assertEqual(rep["verdict"], "REFUSED")
        self.assertTrue(rep["checks"]["P01"]["pass"])
        self.assertIn("fixed path", rep["checks"]["P02"]["detail"])
        self.assertFalse(rep["checks"]["P04"]["pass"])                                    # not committed at the fixed path
        self.assertFalse(rep["checks"]["P06"]["pass"])                                    # no executor amendment

    def test_self_claimed_commit_and_tampering_refused(self):
        a = complete_forgery()
        a["PROTOCOL_SHA256"] = "0" * 64
        a["M_SET"] = [1]
        a["OUTPUT_NAMESPACE"] = "/tmp/elsewhere"
        rep = self._verify(a)
        for text in ("protocol sha256 mismatch", "M_SET", "OUTPUT_NAMESPACE"):
            self.assertIn(text, rep["checks"]["P02"]["detail"])


if __name__ == "__main__":
    unittest.main()
