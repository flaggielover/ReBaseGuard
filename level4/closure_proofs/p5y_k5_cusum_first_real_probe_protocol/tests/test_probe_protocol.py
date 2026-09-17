"""Unit tests of the frozen probe rules and the prelaunch verifier on HYPOTHETICAL inputs only (no real result).

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

X1 = F(5083, 10 ** 7)


class Rules(unittest.TestCase):
    def test_transport_exact_and_refuses_floats(self):
        L1, U1 = PR.transport(F(10), F(12), F(4), F(1, 2))
        self.assertEqual((L1, U1), (F(19, 2), F(25, 2)))
        with self.assertRaises(PR.RuleViolation):
            PR.transport(1.0, 2, 3, X1)
        with self.assertRaises(PR.RuleViolation):
            PR.transport(3, 2, 1, X1)

    def test_three_way_verdict_boundaries(self):
        self.assertEqual(PR.scientific_verdict(F(1, 10 ** 9), 5), PR.SUPPORTS)
        self.assertEqual(PR.scientific_verdict(0, 5), PR.INCONCLUSIVE)             # touching zero is inconclusive
        self.assertEqual(PR.scientific_verdict(-5, 0), PR.INCONCLUSIVE)
        self.assertEqual(PR.scientific_verdict(-5, F(-1, 10 ** 9)), PR.CONTRADICTS)

    def test_point_negative_refutes_even_if_transport_inconclusive(self):
        L1, U1 = PR.transport(-10, -1, 10 ** 9, X1)
        self.assertEqual(PR.scientific_verdict(L1, U1), PR.INCONCLUSIVE)
        self.assertEqual(PR.h3a_consequence(PR.INCONCLUSIVE, PR.point_sign(-10, -1)), "H3A_FALSE_FOR_THIS_M")

    def test_aggregate_routes(self):
        sup = {"verdict": PR.SUPPORTS, "point": "POINT_POSITIVE"}
        inc = {"verdict": PR.INCONCLUSIVE, "point": "POINT_UNDETERMINED"}
        neg = {"verdict": PR.CONTRADICTS, "point": "POINT_NEGATIVE"}
        self.assertEqual(PR.aggregate({1: sup, 2: sup, 3: sup, 5: sup})["label"], "FIRST_CELL_SUPPORTED_ALL_M")
        self.assertEqual(PR.aggregate({1: sup, 2: inc, 3: sup, 5: sup})["label"], "FIRST_CELL_SUPPORTED_SOME_M_UNRESOLVED_OTHERS")
        self.assertEqual(PR.aggregate({1: sup, 2: sup, 3: sup, 5: neg})["route"], "SEEK_ALTERNATE_K5_ROUTE")
        with self.assertRaises(PR.RuleViolation):
            PR.aggregate({1: sup, 2: sup, 3: sup})                                   # no m may be dropped

    def test_consumption_map_complete(self):
        for v in (PR.SUPPORTS, PR.INCONCLUSIVE, PR.CONTRADICTS, PR.VOID):
            entry = PR.k5b_consumption(v)
            for field in ("k5b_step", "cells_closed_by_theorem", "cells_remaining_open", "restart",
                          "next_order3_informative", "h3a_viable"):
                self.assertIn(field, entry)

    def test_addresses_unique_per_m(self):
        cell = {"k1_cell_index": 0, "left": "0/1", "right": "5083/10000000", "point_e": "0/1"}
        hashes = {PR.scientific_address(m=m, cell=cell, k1_record_sha256="a", producer_identity_sha256="b",
                                        protocol_sha256="c", precision_bits=256, attempt_id="A1")["address_sha256"]
                  for m in (1, 2, 3, 5)}
        self.assertEqual(len(hashes), 4)
        with self.assertRaises(PR.RuleViolation):
            PR.scientific_address(m=4, cell=cell, k1_record_sha256="a", producer_identity_sha256="b",
                                  protocol_sha256="c", precision_bits=256, attempt_id="A1")
        with self.assertRaises(PR.RuleViolation):
            PR.scientific_address(m=1, cell=cell, k1_record_sha256="a", producer_identity_sha256="b",
                                  protocol_sha256="c", precision_bits=384, attempt_id="A1")

    def test_qualification_is_sign_independent(self):
        ids = [g["id"] for g in PR.load_prereg()["real_producer_qualification"]["gates"]]
        gates = {i: True for i in ids}
        self.assertEqual(PR.producer_qualification(gates), "PASS")
        self.assertNotIn("sign", json.dumps(PR.load_prereg()["real_producer_qualification"]["gates"]).lower().replace("signature", ""))
        gates["Q07_INTERVAL_CONSISTENCY"] = False
        self.assertEqual(PR.producer_qualification(gates), "FAIL")
        self.assertFalse(PR.science_usable(gates))
        gates = {i: True for i in ids}
        gates["Q15_COST_CEILING"] = False
        self.assertTrue(PR.science_usable(gates))

    def test_retry_and_ladder(self):
        self.assertEqual(PR.retry_decision({"sealed_record_exists": True, "failure_class": "DISK_FULL_BEFORE_SEAL",
                                            "attempts_started": 1})["decision"], "NO_RETRY")
        self.assertEqual(PR.retry_decision({"sealed_record_exists": False, "failure_class": "DISK_FULL_BEFORE_SEAL",
                                            "attempts_started": 1})["decision"], "RETRY_PERMITTED")
        self.assertEqual(PR.retry_decision({"sealed_record_exists": False, "failure_class": "ProducerRefusal",
                                            "attempts_started": 1})["decision"], "NO_RETRY")
        self.assertEqual(PR.retry_decision({"sealed_record_exists": False, "failure_class": "DISK_FULL_BEFORE_SEAL",
                                            "attempts_started": 3})["decision"], "NO_RETRY")
        self.assertEqual(PR.next_rung([]), 256)
        self.assertIsNone(PR.next_rung([256]))


class Verifier(unittest.TestCase):
    def test_template_refused_first_for_authorization(self):
        rep = PV.verify(NS / "protocol/AUTHORIZATION_TEMPLATE.json")
        self.assertEqual(rep["verdict"], "REFUSED")
        self.assertTrue(rep["primary_reason"].startswith("P01: EXECUTION_NOT_AUTHORIZED"))
        self.assertFalse(rep["checks"]["P05"]["pass"])

    def test_flipped_flag_alone_is_still_refused(self):
        auth = json.loads((NS / "protocol/AUTHORIZATION_TEMPLATE.json").read_text())
        forged = copy.deepcopy(auth)
        forged["EXECUTION_AUTHORIZED"] = True
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.json"
            p.write_text(json.dumps(forged))
            rep = PV.verify(p)
        self.assertEqual(rep["verdict"], "REFUSED")
        self.assertTrue(rep["checks"]["P01"]["pass"])
        self.assertFalse(rep["checks"]["P02"]["pass"])                               # unfilled activation fields
        self.assertFalse(rep["checks"]["P05"]["pass"])                               # executor not bound

    def test_tampered_protocol_hash_refused(self):
        auth = json.loads((NS / "protocol/AUTHORIZATION_TEMPLATE.json").read_text())
        auth["PROTOCOL_SHA256"] = "0" * 64
        auth["M_SET"] = [1]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.json"
            p.write_text(json.dumps(auth))
            rep = PV.verify(p)
        self.assertIn("protocol sha256 mismatch", rep["checks"]["P02"]["detail"])
        self.assertIn("M_SET", rep["checks"]["P02"]["detail"])


if __name__ == "__main__":
    unittest.main()
