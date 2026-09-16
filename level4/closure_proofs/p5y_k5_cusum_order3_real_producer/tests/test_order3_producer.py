"""Development unit tests (seeds disjoint from the frozen protocol). Arb-dependent tests skip without python-flint.

    python3 -B tests/test_order3_producer.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from fractions import Fraction as Fr
from math import comb
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
sys.path.insert(0, str(NS / "code"))

import independent_crosscheck as IC  # noqa: E402
import k1_inputs as K1  # noqa: E402
import manufactured_chain as MC  # noqa: E402

HAVE_FLINT = importlib.util.find_spec("flint") is not None
RECORDS = CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records"


class Stdlib(unittest.TestCase):
    def test_independent_path_equals_series_truth(self):
        for n, deg in ((1, 3), (3, 2)):
            s = MC.random_chain(17, n, deg=deg, centre=Fr(1, 5))
            for m in (1, 2, 3, 5):
                e = Fr(1, 5) + Fr(1, 97)
                self.assertEqual(IC.point_value(s, e, m), s.true_R(e, m, 3))

    def test_independent_enclosure_contains_samples(self):
        s = MC.random_chain(23, 1, deg=3, centre=Fr(1, 3))
        lo, hi = IC.enclosure(s, Fr(1, 3), Fr(1, 40), 2, pieces=8)
        for g in range(9):
            e = Fr(1, 3) - Fr(1, 40) + Fr(2 * g, 320)
            self.assertTrue(lo <= s.true_R(e, 2, 3) <= hi)

    def test_target_fixture_hits_target(self):
        base = MC.random_chain(31, 3, centre=Fr(1, 4))
        s = MC.with_target_R3_m1(base, Fr(1, 4), Fr(-7, 3))
        self.assertEqual(s.true_R(Fr(1, 4), 1, 3), Fr(-7, 3))

    def test_k1_validation_accepts_committed_records_and_enforces_target_gate(self):
        for i in (0, 309):
            v = K1.validate((RECORDS / f"aux5_CUSUM_{i}_256.json").read_bytes(), cell_index=i)
            self.assertTrue(all(v["checks"].values()))
            self.assertTrue(all(x["target_gate"]["status"] == "PASS" for x in v["per_m"].values()))
        self.assertTrue(K1.validate((RECORDS / "aux5_CUSUM_309_256.json").read_bytes(), cell_index=309)
                        ["endpoint_region"])

    def test_k1_validation_refuses(self):
        b = (RECORDS / "aux5_CUSUM_0_256.json").read_bytes()
        with self.assertRaises(K1.K1InputRefused):
            K1.validate(b, cell_index=1)
        with self.assertRaises(K1.K1InputRefused):
            K1.validate(b + b" ", cell_index=0)
        with self.assertRaises(K1.K1InputRefused):
            K1._rat("0.5")

    def test_residual_terms_are_order3_leibniz(self):
        import rung3_residual as RR
        self.assertEqual([(c, i) for c, i, _ in RR.TERMS], [(comb(3, i), i) for i in range(4)])
        self.assertEqual([f for _, _, f in RR.TERMS], ["G", "H", "D", "F"])

    def test_registry_pinned_and_empty(self):
        src = (NS / "code/cusum_order3.py").read_text()
        reg = (NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY.json").read_bytes()
        self.assertIn(hashlib.sha256(reg).hexdigest(), src)
        self.assertEqual(json.loads(reg)["authorizations"], [])


@unittest.skipUnless(HAVE_FLINT, "python-flint not installed")
class Arb(unittest.TestCase):
    def test_dev_fixture_sound(self):
        import run_fixture as RF
        import soundness as SD
        s = MC.random_chain(41, 3, centre=Fr(3, 7))
        rig, _g, res, _ = RF.certify_fixture(s, Fr(3, 7), Fr(1, 60), seed=3, noise=Fr(1, 10 ** 5), bits=256)
        self.assertEqual(SD.violations(s, rig, res), [])

    def test_export_is_precision_independent(self):
        import rung3_engine as E
        from flint import arb
        with E.precision(256):
            x = arb(1) / arb(3)
        lo, hi = E.ball_fractions(x)
        self.assertTrue(lo <= Fr(1, 3) <= hi and hi - lo < Fr(1, 2 ** 250))

    def test_refusals(self):
        import rung3_engine as E
        with self.assertRaises(E.ProducerRefusal):
            with E.precision(100):
                pass
        with self.assertRaises(E.ProducerRefusal):
            E.coefficients(4)


if __name__ == "__main__":
    unittest.main(verbosity=1)
