"""POST-T3R tests. PHASE-SCOPED: asserts properties that hold only AFTER the
successor result exists. The T1R-phase assertions (notably "no result yet")
live in test_pre_t2r.py and are NOT re-run here -- the split was designed at
T1R so a phase-scoped test is never miscounted as a scientific failure.
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest

NS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NS / "code"))
import harness as H                                                  # noqa: E402

RES = json.loads((NS / "results/task1r_F0_qualification.json").read_text())
ADJ = json.loads((NS / "adjudication/TASK1R_ADJUDICATION.json").read_text())
FP = json.loads((NS / "config/frozen_parameters.json").read_text())


class TestResultSchema(unittest.TestCase):
    def test_required_fields_present(self):
        for k in ("schema", "binding", "result_bearing", "git_commit", "D", "Z",
                  "integrity", "frozen_scope", "amplification", "p1",
                  "joint_consistency", "complexity_guard", "budget_partition",
                  "candidate", "certificate", "budget", "pass_conditions",
                  "TASK1R_VERDICT", "failure_class", "runtime"):
            self.assertIn(k, RES, k)

    def test_decomposition_has_every_required_component(self):
        for k in ("equation_defect_polynomial", "truncation_patch_local",
                  "tail_zeta_and_moments", "endpoint_slivers",
                  "interval_arithmetic", "rounding_exact_dyadic"):
            self.assertIn(k, RES["certificate"]["components"], k)
            self.assertIn(k, RES["certificate"]["per_line"], k)


class TestCertificateArithmetic(unittest.TestCase):
    def test_components_sum_to_delta(self):
        c = RES["certificate"]
        self.assertAlmostEqual(sum(c["components"].values()), c["delta_F0"], delta=1e-20)

    def test_propagation_and_fraction(self):
        b = RES["budget"]
        self.assertAlmostEqual(b["C_SR_at_e"] * RES["certificate"]["delta_F0"],
                               b["propagated_contribution"], delta=1e-15)
        self.assertAlmostEqual(b["propagated_contribution"] / b["B_candidate"],
                               b["fraction_of_B_candidate"], delta=1e-15)

    def test_certified_bound_contains_the_constant_term(self):
        c = RES["certificate"]
        self.assertGreaterEqual(c["delta_F0"], abs(c["defect_constant_term"]))


class TestBudgetAccounting(unittest.TestCase):
    def test_every_line_within_its_frozen_allowance(self):
        part = FP["budget_partition"]["absolute"]
        C = RES["budget"]["C_SR_at_e"]
        for k, v in RES["certificate"]["per_line"].items():
            self.assertAlmostEqual(v["allowance_delta_units"],
                                   part[v["budget_line"]] / C, delta=1e-20, msg=k)
            self.assertLessEqual(v["value"], v["allowance_delta_units"], k)

    def test_partition_unchanged_and_reserve_locked(self):
        p = FP["budget_partition"]
        self.assertEqual(p["sum_absolute"], H.B_CANDIDATE)
        self.assertFalse(p["reserve_redistributable"])
        self.assertFalse(RES["budget"]["redistribution_used"])
        self.assertFalse(RES["budget"]["reserve_drawn"])

    def test_total_within_B_candidate(self):
        self.assertLessEqual(RES["budget"]["propagated_contribution"], H.B_CANDIDATE)


class TestStopRules(unittest.TestCase):
    def test_no_stop_fired_and_class_is_NONE(self):
        self.assertTrue(RES["pass_conditions"]["13_no_stop_fired"])
        self.assertEqual(RES["failure_class"], "NONE")

    def test_guards_all_passed(self):
        self.assertTrue(RES["amplification"]["PASS"])
        self.assertTrue(RES["p1"]["PASS"])
        self.assertTrue(RES["joint_consistency"]["PASS"])
        self.assertTrue(RES["complexity_guard"]["PASS"])

    def test_parameters_used_are_the_frozen_ones(self):
        self.assertEqual(RES["D"], FP["selection"]["D_selected"])
        self.assertEqual(RES["Z"], FP["selection"]["Z_selected"])


class TestAdjudication(unittest.TestCase):
    def test_independent_and_complete(self):
        self.assertEqual(ADJ["checks_failed"], [])
        self.assertGreaterEqual(ADJ["checks_total"], 50)
        self.assertFalse(ADJ["producer_self_award_permitted"])
        self.assertEqual(ADJ["ADJUDICATED_VERDICT"], RES["TASK1R_VERDICT"])

    def test_predecessor_still_failed(self):
        p = ADJ["sections"]["predecessor_immutability"]
        self.assertTrue(p["unmutated"] and p["still_FAIL"] and p["class_preserved"])

    def test_chronology(self):
        pr = ADJ["sections"]["provenance"]
        self.assertTrue(pr["T1R_frozen_before_T2R"])
        self.assertTrue(pr["T1R_is_ancestor_of_HEAD"])
        self.assertEqual(pr["frozen_files_changed_since_T1R"], [])
        self.assertTrue(pr["manifest_hash_recomputes"])


class TestRepairActuallyWorked(unittest.TestCase):
    """The repaired channels must be orders below the predecessor's."""

    def test_patch_local_truncation_collapsed(self):
        pred = 1.087027e-03
        got = RES["certificate"]["components"]["truncation_patch_local"]
        self.assertLess(got, pred / 1e6)

    def test_tail_channel_negligible(self):
        self.assertLess(RES["certificate"]["components"]["tail_zeta_and_moments"], 1e-10)

    def test_equation_defect_is_now_a_real_share_of_the_total(self):
        c = RES["certificate"]
        eq = c["components"]["equation_defect_polynomial"]
        self.assertGreater(eq / c["delta_F0"], 1e-3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
