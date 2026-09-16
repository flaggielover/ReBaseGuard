"""Tests for the independent P5X L5 review namespace (read-only, no scientific compute).

  python -B tests/test_l5_review.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
sys.path.insert(0, str(NS / "code"))

import l5_review_check as K  # noqa: E402

L5 = "level4/closure_proofs/p5x_global_nonlinear_dynamics/PROOF.md"


def load(rel):
    return json.loads((NS / rel).read_text())


class HashBinding(unittest.TestCase):
    def test_inventory_matches_repository_bytes_and_history(self):
        self.assertEqual(K.verify_hashes(REPO), [])

    def test_l5_proof_never_modified(self):
        h = load("config/L5_HASH_INVENTORY.json")["l5_files"][L5]
        self.assertEqual(h["commits_touching"], 1)
        self.assertEqual(h["introduced_in"], h["last_modified_in"])

    def test_countersignature_binds_l5_and_namespace(self):
        cs, inv = load("COUNTERSIGNATURE.json"), load("config/L5_HASH_INVENTORY.json")
        self.assertEqual(cs["l5"]["file_sha256"], inv["l5_files"][L5]["sha256"])
        self.assertEqual(cs["l5"]["section_sha256"], inv["l5_section"]["sha256"])
        self.assertEqual(cs["l5"]["section_sha256"], hashlib.sha256(K.l5_section_bytes(REPO)).hexdigest())
        for rel, h in cs["bound_namespace_files"].items():
            self.assertEqual(hashlib.sha256((NS / rel).read_bytes()).hexdigest(), h, rel)


class Mathematics(unittest.TestCase):
    def test_kernel_modulus_identity(self):
        self.assertLess(K.modulus_identity_residual(), 1e-12)

    def test_strip_widths_positive_and_ratios_below_one(self):
        rec = K.strip_record()
        self.assertEqual(rec, load("evidence/STRIP_ARITHMETIC.json"))
        for d in rec["detectors"].values():
            self.assertGreater(d["L5_route"]["theta0"], 0)
            self.assertTrue(d["L5_route"]["block_ratio_lt_1"])
            self.assertGreater(d["direct_route"]["theta1"], 0)
            self.assertTrue(d["direct_route"]["series_ratio_lt_1"])

    def test_one_step_no_alarm_mass_maximised_at_zero(self):
        # Phi(s+c) - Phi(s-c) <= 1 - 2 Phi(-c): derivative phi(s+c) - phi(s-c) has sign of -s
        c = 5.5
        top = 1 - 2 * K.upper_tail(c)
        for s in (-3.0, -0.5, 0.0, 0.25, 2.0, 9.0):
            mass = (1 - K.upper_tail(s + c)) - (1 - K.upper_tail(s - c))
            self.assertLessEqual(mass, top + 1e-15)

    def test_k5b_needs_at_most_c3(self):
        rec = K.uses_record()
        self.assertEqual(rec["max_required_order"], "C3")
        self.assertFalse(rec["hidden_C4_in_K5B"])
        self.assertEqual(rec, {k: v for k, v in load("evidence/REGULARITY_USES.json").items() if k in rec})


class Verdict(unittest.TestCase):
    def test_verdict_and_non_claims(self):
        cs = load("COUNTERSIGNATURE.json")
        self.assertEqual(cs["P5X_L5_INDEPENDENT_REVIEW"], "PASS_WITH_SCOPE_LIMITATION")
        self.assertEqual(cs["HOLOMORPHY"], "PASS")
        self.assertEqual(cs["REAL_C3_ON_K5_DOMAIN"], "PASS")
        self.assertEqual(cs["K5B_REGULARITY_PREMISE"], "SATISFIED")
        self.assertEqual(cs["HIDDEN_C4_REQUIREMENT_IN_K5B"], "NO")
        self.assertEqual(cs["TEMPORAL_INTEGRITY"], "PASS")
        self.assertTrue(all(v is False for v in cs["non_claims"].values()))

    def test_adversarial_cases_all_resolved(self):
        cases = load("evidence/ADVERSARIAL_REVIEW.json")["cases"]
        self.assertEqual(len(cases), 10)
        self.assertTrue(all(c["verdict"] in {"RULED_OUT", "NOT_APPLICABLE", "GAP_CLOSED", "BYPASSED", "ABSENT"}
                            for c in cases))


if __name__ == "__main__":
    unittest.main(verbosity=2)
