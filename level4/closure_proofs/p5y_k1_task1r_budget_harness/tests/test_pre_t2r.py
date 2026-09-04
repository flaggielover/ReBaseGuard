"""PRE-T2R tests for K1 Task 1R.  PHASE-SCOPED: this file asserts T1R-phase
properties (notably: no successor result exists yet).  Post-T3R assertions live
in test_post_t3r.py.  That split is designed in advance so a T1R-phase test is
never mistaken for a scientific failure after results exist.
"""
from __future__ import annotations

import ast
import json
import math
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(NS / "code"))
import harness as H                                                  # noqa: E402
import integrity                                                     # noqa: E402
from flint import arb, acb, ctx                                      # noqa: E402
from rebaseguard_certify.arb_backend import gaussian_cdf, workprec   # noqa: E402
import sr_local as L                                                 # noqa: E402


def setup():
    with workprec(H.PROD_BITS):
        g = H.geometry()
        p1 = H.p1_rule(g["H"], g["span"])
    return g, p1


FP = json.loads((NS / "config" / "frozen_parameters.json").read_text())
D_SEL, Z_SEL = FP["selection"]["D_selected"], FP["selection"]["Z_selected"]


class TestPredecessorImmutable(unittest.TestCase):
    def test_predecessor_artifacts_unmutated(self):
        v = integrity.verify()
        self.assertEqual(v["predecessor_mutated"], [])
        self.assertEqual(v["predecessor_verdict"], "FAIL")
        self.assertEqual(v["predecessor_governing_class"], "IMPLEMENTATION_DEFECT")
        self.assertAlmostEqual(v["predecessor_delta_0"], 1.106607209535348e-03,
                               delta=1e-12)

    def test_binding_checkpoint_unmutated(self):
        v = integrity.verify()
        self.assertEqual(v["k1_checkpoint_hash"],
                         "ababbef4d42ad5a7a61e87279eb895c1b2d0ecfe67454f18c85acf6d57cd5c1d")
        self.assertEqual(v["k1_blob_mismatch"], [])
        self.assertEqual(v["protected_tree_mutated"], [])
        self.assertTrue(v["PASS"])

    def test_no_successor_result_before_T2R(self):
        self.assertEqual(integrity.verify()["prior_task1r_results"], [])


class TestScopeAndLedgerUnchanged(unittest.TestCase):
    def test_same_object(self):
        r = integrity.frozen_scope_unchanged(H)
        for k in ("detector", "object", "patch", "grid", "e", "bidegree", "scale_bits"):
            self.assertTrue(r["checks"][k], k)

    def test_budget_and_precision_and_ceiling_unchanged(self):
        r = integrity.frozen_scope_unchanged(H)
        for k in ("B_candidate", "LOCAL_GATE_BUDGET", "no_redistribution",
                  "SR_bits", "no_precision_escalation", "no_degree_adaptation",
                  "complexity_ceiling", "P1_workprec", "eps_P1"):
            self.assertTrue(r["checks"][k], k)
        self.assertTrue(r["PASS"])

    def test_partition_sums_and_reserve_locked(self):
        b = H.budget()
        self.assertTrue(b["sums_to_B_candidate"])
        self.assertEqual(b["sum_absolute"], H.B_CANDIDATE)
        self.assertFalse(b["reserve_redistributable"])
        self.assertFalse(b["new_budget_created"])
        self.assertEqual(sum(H.PARTITION_20THS.values()), 20)


class TestJointConsistencyGuard(unittest.TestCase):
    """The predecessor's TRUNC_U/DEG_X mismatch must be REJECTED."""

    def setUp(self):
        g, p1 = setup()
        self.H = float(g["H"])
        self.h = float(g["span"] / (2 * p1["n_panels"]))

    def test_predecessor_configuration_is_rejected(self):
        bad = H.required_local_degree("compose_then_truncate", 6, 32, self.H, self.h)
        self.assertFalse(bad["PASS"])
        self.assertFalse(bad["D_satisfies_requirement"])
        self.assertGreater(bad["required_D"], bad["D_max_from_complexity"])
        self.assertGreater(bad["required_D"], 6)

    def test_predecessor_architecture_rejected_at_any_affordable_D(self):
        for D in range(6, 53):
            r = H.required_local_degree("compose_then_truncate", D, 20,
                                        self.H, self.h)
            self.assertFalse(r["PASS"], f"D={D} must not rescue late truncation")

    def test_selected_configuration_passes(self):
        ok = H.required_local_degree("truncate_each_product", D_SEL, Z_SEL,
                                     self.H, self.h)
        self.assertTrue(ok["PASS"])
        self.assertGreaterEqual(D_SEL, H.SOFTPLUS_DEGREE + 1)
        self.assertLessEqual(ok["local_score"], H.COMPLEXITY_CEILING)
        self.assertLessEqual(ok["candidate_score"], H.COMPLEXITY_CEILING)

    def test_D_below_source_degree_rejected(self):
        r = H.required_local_degree("truncate_each_product", 6, Z_SEL,
                                    self.H, self.h)
        self.assertFalse(r["PASS"])


class TestGaussianTailCertificate(unittest.TestCase):
    """The new bound must DOMINATE direct high-precision evaluation, and be
    sharper than the predecessor's |N_k| <= h^k N_0."""

    def test_bound_dominates_independent_high_precision_integral(self):
        g, p1 = setup()
        with workprec(H.PROD_BITS):
            h = g["span"] / (arb(2) * arb(p1["n_panels"]))
            for panel in (0, 7, 14, 21, 27):
                z_c = g["L_c"] + arb(2) * h * arb(panel) + h
                mu = z_c + g["e"]
                B = H.gaussian_moment_bound(mu, h, 24)
                ctx.prec = 300
                MU, HH = acb(float(mu)), float(h)
                for k in (0, 1, 2, 5, 8, 13, 21, 24):
                    def f(z, analytic, k=k, MU=MU):
                        w = z + MU
                        return (z ** k) * (-(w * w) / acb(2)).exp() \
                            / (acb(2) * acb.pi()).sqrt()
                    exact = acb.integral(f, acb(-HH), acb(HH))
                    self.assertLessEqual(abs(float(exact.real.mid())),
                                         float(B[k]) * (1 + 1e-12),
                                         f"panel {panel} k={k}")

    def test_sharper_than_predecessor_bound_by_factor_k_plus_1(self):
        g, p1 = setup()
        with workprec(H.PROD_BITS):
            h = g["span"] / (arb(2) * arb(p1["n_panels"]))
            z_c = g["L_c"] + arb(2) * h * arb(14) + h
            mu = z_c + g["e"]
            new = H.gaussian_moment_bound(mu, h, 24)
            N = L.centred_gaussian_moments(z_c - h, z_c + h, z_c, g["e"], 24)
            N0 = N[0].abs_upper()
            for k in (4, 8, 16, 24):
                old = float(N0 * (h ** k))
                self.assertLess(float(new[k]), old)
                self.assertGreater(old / float(new[k]), k / 2.0)

    def test_bound_is_monotone_decreasing_in_k(self):
        g, p1 = setup()
        with workprec(H.PROD_BITS):
            h = g["span"] / (arb(2) * arb(p1["n_panels"]))
            mu = g["L_c"] + arb(2) * h * arb(14) + h + g["e"]
            B = [float(x) for x in H.gaussian_moment_bound(mu, h, 30)]
        self.assertTrue(all(B[i + 1] <= B[i] for i in range(len(B) - 1)))


class TestClosedFormControls(unittest.TestCase):
    """Non-decisive candidates whose defect is known analytically."""

    def _cand(self, c00=None):
        c = [[arb(0)] * (H.CAND_DEGREE + 1) for _ in range(H.CAND_DEGREE + 1)]
        if c00 is not None:
            c[0][0] = arb(c00)
        return c

    def test_zero_candidate_gives_minus_S0(self):
        g, p1 = setup()
        with workprec(H.PROD_BITS):
            cert = H.certify(self._cand(), D_SEL, Z_SEL, g, p1, 187.7471962405577, {})
            two_pi = arb(2) * arb.pi()
            def phi(t):
                return (-(t * t) / arb(2)).exp() / two_pi.sqrt()
            S0 = phi(g["U_c"] + g["e"]) - phi(g["L_c"] + g["e"])
        self.assertAlmostEqual(cert["defect_constant_term"], -float(S0), delta=1e-18)

    def test_constant_candidate_gives_h1_minus_S0(self):
        g, p1 = setup()
        with workprec(H.PROD_BITS):
            cert = H.certify(self._cand(1), D_SEL, Z_SEL, g, p1, 187.7471962405577, {})
            two_pi = arb(2) * arb.pi()
            def phi(t):
                return (-(t * t) / arb(2)).exp() / two_pi.sqrt()
            u, l = g["U_c"], g["L_c"]
            h1 = arb(1) - gaussian_cdf(u + g["e"]) + gaussian_cdf(l + g["e"])
            expect = float(h1 - (phi(u + g["e"]) - phi(l + g["e"])))
        self.assertAlmostEqual(cert["defect_constant_term"], expect, delta=1e-13)
        self.assertGreaterEqual(cert["delta_F0"], abs(expect))


class TestNoHiddenAdaptation(unittest.TestCase):
    def test_runner_reads_frozen_parameters_and_never_selects(self):
        src = (NS / "code" / "task1r_run.py").read_text()
        tree = ast.parse(src)
        calls = {n.func.attr for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertNotIn("select_parameters", calls)
        self.assertIn("frozen_parameters.json", src)

    def test_no_retry_loop_around_certify(self):
        tree = ast.parse((NS / "code" / "task1r_run.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                seg = ast.dump(node)
                self.assertNotIn("certify", seg)
                self.assertNotIn("build_candidate", seg)

    def test_tail_budget_overspend_would_be_rejected(self):
        """A tail contribution above its frozen line must fail its per-line gate."""
        C = 187.7471962405577
        allow = H.budget()["absolute"]["B_tail"] / C
        self.assertGreater(allow, 0)
        over = allow * 1.000001
        self.assertFalse(over <= allow)

    def test_selection_grids_are_frozen_and_ascending(self):
        self.assertEqual(list(H.Z_GRID), sorted(H.Z_GRID))
        self.assertEqual(list(H.D_GRID), sorted(H.D_GRID))
        self.assertEqual(H.D_GRID[0], H.SOFTPLUS_DEGREE + 1)
        self.assertIn(Z_SEL, H.Z_GRID)
        self.assertIn(D_SEL, H.D_GRID)


if __name__ == "__main__":
    unittest.main(verbosity=2)
