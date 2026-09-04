"""PRE-T2 tests for K1 Production Task 1.

Run BEFORE the first result-bearing execution.  Two classes:

  * CORRECTNESS -- the Taylor-model pipeline is validated end to end against
    CLOSED FORMS using non-decisive candidates (zero, and the constant 1).
    Neither touches the genuine F_0 candidate, so passing them cannot bias the
    Task-1 result.
  * NEGATIVE -- each frozen rule is shown to actually reject a violation.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
T1DIR = HERE.parent
NS = T1DIR.parent
ROOT = NS.parents[2]
for p in (str(T1DIR), str(ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics"
                          "/compute_optimization_r3_sr_symbolic"),
          str(ROOT / "rebaseguard-proof" / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from flint import arb                                              # noqa: E402
from rebaseguard_certify.arb_backend import gaussian_cdf, rational, workprec  # noqa: E402
import sr_local as L                                               # noqa: E402
import task1_f0 as T                                               # noqa: E402


def _setup():
    A, b, c = L.sr_constants()
    e = rational(T.E_NUM, T.E_DEN)
    geo = L.patch_geometry(*T.PATCH, grid=T.GRID)
    half = (geo["yp"][1] - geo["yp"][0]) / arb(2)
    span = (c - (geo["yp"][0] + geo["yp"][1]) / arb(2)) \
        - ((geo["ym"][0] + geo["ym"][1]) / arb(2) - c)
    return b, c, e, geo, half, span


class TestPipelineAgainstClosedForms(unittest.TestCase):
    """Non-decisive candidates whose defect is known analytically."""

    def test_zero_candidate_defect_equals_minus_S0(self):
        with workprec(T.PROD_BITS):
            b, c, e, geo, half, span = _setup()
            p1 = T.p1_rule(half, span)
            zero = [[arb(0)] * (T.CAND_DEGREE + 1) for _ in range(T.CAND_DEGREE + 1)]
            cert = T.certify_defect(zero, geo, e, b, c, p1)
            p_c = (geo["yp"][0] + geo["yp"][1]) / arb(2)
            m_c = (geo["ym"][0] + geo["ym"][1]) / arb(2)
            two_pi = arb(2) * arb.pi()

            def phi(t):
                return (-(t * t) / arb(2)).exp() / two_pi.sqrt()
            S0 = phi(c - p_c + e) - phi(m_c - c + e)
            # Fhat = K_e Fhat = 0, so the defect is exactly -S_0
            self.assertAlmostEqual(cert["defect_constant_term"], -float(S0),
                                   delta=1e-18)
            self.assertLess(cert["delta_0"], 1e-6)

    def test_constant_candidate_defect_equals_h1_minus_S0(self):
        """Fhat = 1  =>  K_e Fhat = Phi(u+e) - Phi(l+e) = 1 - h_1,
        so the defect is exactly h_1 - S_0.  This exercises the FULL kernel
        pipeline -- panels, moments, softplus, Chebyshev composition -- against
        a closed form, with real cancellation (both sides are ~1e-7)."""
        with workprec(T.PROD_BITS):
            b, c, e, geo, half, span = _setup()
            p1 = T.p1_rule(half, span)
            one = [[arb(0)] * (T.CAND_DEGREE + 1) for _ in range(T.CAND_DEGREE + 1)]
            one[0][0] = arb(1)
            cert = T.certify_defect(one, geo, e, b, c, p1)
            p_c = (geo["yp"][0] + geo["yp"][1]) / arb(2)
            m_c = (geo["ym"][0] + geo["ym"][1]) / arb(2)
            u, l = c - p_c, m_c - c
            two_pi = arb(2) * arb.pi()

            def phi(t):
                return (-(t * t) / arb(2)).exp() / two_pi.sqrt()
            h1 = arb(1) - gaussian_cdf(u + e) + gaussian_cdf(l + e)
            S0 = phi(u + e) - phi(l + e)
            expected = float(h1 - S0)
            got = cert["defect_constant_term"]
            self.assertAlmostEqual(got, expected, delta=1e-13)
            # and the certified bound must actually contain the truth
            self.assertGreaterEqual(cert["delta_0"], abs(expected))


class TestNegativeControls(unittest.TestCase):
    def test_wrong_detector_rejected(self):
        real = T.DETECTOR
        try:
            T.DETECTOR = "CUSUM"
            self.assertFalse(T.verify_frozen_parameters()["PASS"])
        finally:
            T.DETECTOR = real

    def test_wrong_patch_rejected(self):
        real = T.PATCH
        try:
            T.PATCH = (18, 11)
            self.assertFalse(T.verify_frozen_parameters()["PASS"])
        finally:
            T.PATCH = real

    def test_higher_degree_rejected(self):
        real = T.CAND_DEGREE
        try:
            T.CAND_DEGREE = 20
            self.assertFalse(T.verify_frozen_parameters()["PASS"])
            self.assertFalse(T.complexity_guard()["PASS"])
        finally:
            T.CAND_DEGREE = real

    def test_higher_precision_rejected(self):
        real = T.PROD_BITS
        try:
            T.PROD_BITS = 384
            self.assertFalse(T.verify_frozen_parameters()["PASS"])
        finally:
            T.PROD_BITS = real

    def test_p1_threshold_collapse_rejected(self):
        real = T.EPS_P1
        try:
            T.EPS_P1 = 0.0          # rule target == check threshold: knife edge
            self.assertFalse(T.verify_frozen_parameters()["PASS"])
        finally:
            T.EPS_P1 = real

    def test_budget_overspend_rejected(self):
        real = T.B_CANDIDATE
        try:
            T.B_CANDIDATE = 0.08     # silently doubling the ledger line
            self.assertFalse(T.verify_frozen_parameters()["PASS"])
        finally:
            T.B_CANDIDATE = real

    def test_checkpoint_hash_corruption_rejected(self):
        real = T.CHECKPOINT_HASH
        try:
            T.CHECKPOINT_HASH = "0" * 64
            self.assertFalse(T.verify_checkpoint()["PASS"])
        finally:
            T.CHECKPOINT_HASH = real

    def test_production_output_present_before_T2_rejected(self):
        marker = NS / "results" / "_negctl_probe.json"
        marker.write_text("{}")
        try:
            v = T.verify_checkpoint()
            self.assertFalse(v["PASS"])
            self.assertIn("results/_negctl_probe.json", v["prior_task1_results"])
        finally:
            marker.unlink()
        self.assertTrue(T.verify_checkpoint()["PASS"])

    def test_complexity_ceiling_is_the_frozen_one(self):
        cx = json.loads((NS / "config/complexity_guard.json").read_text())
        self.assertEqual(T.COMPLEXITY_CEILING, cx["PRODUCTION_COMPLEXITY_CEILING"])
        self.assertNotEqual(T.COMPLEXITY_CEILING, 100_000)


class TestIntegrityAndGuards(unittest.TestCase):
    def test_checkpoint_integrity_passes(self):
        v = T.verify_checkpoint()
        self.assertTrue(v["PASS"], v)
        self.assertEqual(v["recomputed_checkpoint_hash"], T.CHECKPOINT_HASH)
        self.assertEqual(v["blob_mismatch"], [])
        self.assertEqual(v["protected_tree_mutated"], [])
        self.assertEqual(v["protected_blob_mutated"], [])
        self.assertEqual(v["prior_task1_results"], [])

    def test_frozen_parameters_match(self):
        r = T.verify_frozen_parameters()
        self.assertTrue(r["PASS"], [k for k, v in r["checks"].items() if not v])

    def test_complexity_guard_passes_and_is_ordered(self):
        g = T.complexity_guard()
        self.assertTrue(g["PASS"])
        self.assertEqual(g["score"], 37281)
        self.assertTrue(g["evaluated_before_kernel_construction"])

    def test_amplification_direction(self):
        a = T.resolvent_upper_bound(T.E_NUM, T.E_DEN)
        self.assertEqual(a["type"], "UPPER")
        self.assertTrue(a["PASS"])
        self.assertTrue(a["C0_le_certified_cap"])
        self.assertTrue(a["monotone_nonincreasing_in_e"])

    def test_p1_rule_distinct_and_within_headroom(self):
        with workprec(T.PROD_BITS):
            _, _, _, _, half, span = _setup()
            p1 = T.p1_rule(half, span)
        self.assertTrue(p1["rule_and_check_distinct"])
        self.assertTrue(p1["rule_target_evaluated_inside_workprec"])
        self.assertEqual(p1["P1_RULE_WORKPREC_BITS"], 512)
        self.assertTrue(p1["PASS"])
        self.assertGreaterEqual(p1["HEADROOM_REL"], T.P1_HEADROOM_GUARD)


if __name__ == "__main__":
    unittest.main(verbosity=2)
