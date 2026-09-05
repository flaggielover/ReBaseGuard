"""Focused tests for the cover-ledger IMPLEMENTATION namespace.

These test the implementation against the FROZEN specification. Passing them is
not a scientific qualification and never authorises production.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction as F
from math import comb, erf, exp, pi, sqrt
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(SPEC_NS / "code"))

import assembly                                                    # noqa: E402
import depgraph                                                    # noqa: E402
import ledger                                                      # noqa: E402
import opnorms                                                     # noqa: E402
import spec                                                        # noqa: E402
import universe                                                    # noqa: E402
from intervals import (exact, mag_fraction, outward_upper,          # noqa: E402
                       record, upper_fraction, workprec)
from flint import arb                                              # noqa: E402

import algebra as FROZEN                                           # noqa: E402


class FrozenSpecCorrespondence(unittest.TestCase):
    def test_frozen_artifacts_hash_unchanged(self):
        self.assertEqual(spec.verify_frozen_spec(), spec.FROZEN_HASHES)

    def test_budgets_and_caps_not_relaxed(self):
        self.assertEqual(spec.TOP_BUDGETS, FROZEN.TOP_BUDGETS)
        self.assertEqual(sum(spec.TOP_BUDGETS.values()), F(19, 100))
        self.assertEqual(sum(spec.NESTED_CANDIDATE.values()), F(1, 25))
        self.assertEqual(spec.NESTED_CANDIDATE["B_end"], F(1, 250))
        self.assertEqual(spec.TOP_RESERVE, F(1, 100))
        self.assertEqual(spec.LOCAL_GATE_BUDGET, F(1, 10))
        self.assertFalse(spec.RESERVE_DRAWABLE)
        self.assertFalse(spec.REDISTRIBUTION_ALLOWED)

    def test_claimant_ownership_matches_frozen(self):
        self.assertEqual(spec.CLAIMANT_OWNERS, FROZEN.CLAIMANTS)
        for k in ("dF_equation_certificate", "Kprime_F_dependency",
                  "derivative_source_dependency", "finite_derivative_chain",
                  "derivative_arithmetic", "curvature_envelope"):
            self.assertEqual(spec.CLAIMANT_OWNERS[k], "B_cover")

    def test_hard_cap_unchanged(self):
        self.assertEqual(spec.HARD_CAP_CPU_H, 1126)
        self.assertEqual(spec.COST_MODEL["cap_adequacy"], "NOT_ESTABLISHED")

    def test_precision_preserved(self):
        self.assertEqual(spec.PRODUCTION_BITS, 256)
        self.assertFalse(spec.PRECISION_ESCALATION_ALLOWED)
        self.assertFalse(spec.DEGREE_ADAPTATION_ALLOWED)

    def test_historical_verdicts_unchanged(self):
        h = spec.CHECKPOINT["history"]
        self.assertEqual(h["P5"], "PARTIAL")
        self.assertEqual(h["P5X"], "PARTIAL")
        self.assertEqual(h["historical_K1"], "K1_INCOMPLETE_BUDGET")
        self.assertEqual(h["Task1"], "FAIL")
        self.assertEqual(h["Task1R"], "PASS")
        self.assertEqual(spec.CHECKPOINT["LEVEL4_GLOBAL_CLOSURE"], "NO")
        self.assertEqual(spec.CHECKPOINT["scientific_verdict"], "NOT_RUN")
        self.assertFalse(spec.CHECKPOINT["changes_historical_verdicts"])


class WorkUniverse(unittest.TestCase):
    def test_exact_count_and_frozen_identity(self):
        ids = universe.work_ids()
        self.assertEqual(len(ids), 17978)
        self.assertEqual(len(set(ids)), 17978)
        self.assertEqual(ids, FROZEN.work_ids(spec.CELLS))
        self.assertEqual(universe.unit_kind_counts()["object"], 12198)
        self.assertEqual(spec.COUNTS, {"CUSUM": 326, "SR": 316})

    def test_counts_derived_not_hardcoded(self):
        half = spec.CELLS[:10]
        self.assertEqual(len(universe.work_ids(half)), 28 * 10 + 2)

    def test_deterministic_ids_across_processes(self):
        cmd = [sys.executable, "-c",
               f"import sys,json;sys.path.insert(0,{str(NS / 'code')!r});"
               "import universe;print(json.dumps([list(map(str,u)) for u in universe.work_ids()]))"]
        a = subprocess.check_output(cmd)
        b = subprocess.check_output(cmd)
        self.assertEqual(a, b)
        self.assertEqual(json.loads(a)[0], ["CUSUM", "0", "object", "h_1"])

    def test_stable_hashing(self):
        h1 = universe.universe_hash(backend_hash="test")
        h2 = universe.universe_hash(backend_hash="test")
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, universe.universe_hash(backend_hash="other"))

    def test_shard_conservation_all_worker_counts(self):
        units = universe.work_ids()
        for workers in (1, 2, 8, 16, 32, 64):
            r = universe.verify_shard_conservation(workers, units)
            self.assertTrue(r["union_equals_universe"], workers)
            self.assertTrue(r["no_overlap"], workers)
            self.assertTrue(r["no_dropped_work"], workers)
            self.assertEqual(sum(r["shard_sizes"]), 17978)
            self.assertLessEqual(r["max_minus_min"], 1)

    def test_no_ceil_inflation(self):
        # ceil-per-shard would allocate more than N slots overall.
        for workers in (7, 8, 64):
            floor_total = sum(universe.shard_bounds(17978, k, workers)[1]
                              - universe.shard_bounds(17978, k, workers)[0]
                              for k in range(workers))
            self.assertEqual(floor_total, 17978)
            ceil_total = -(-17978 // workers) * workers
            self.assertGreaterEqual(ceil_total, floor_total)

    def test_shards_disjoint_pairwise(self):
        units = universe.work_ids()
        parts = [set(universe.shard(units, k, 16)) for k in range(16)]
        for i in range(16):
            for j in range(i + 1, 16):
                self.assertEqual(parts[i] & parts[j], set())


class ResumeAdmission(unittest.TestCase):
    def _good(self):
        return {"checkpoint_hash": spec.CHECKPOINT_SHA256,
                "cells_sha256": spec.CELLS_SHA256,
                "error_algebra_sha256": spec.ERROR_ALGEBRA_SHA256,
                "backend_hash": "B", "implementation_hash": universe.implementation_hash(),
                "precision_bits": 256, "obligation_universe_total": 17978}

    def test_matching_record_admitted(self):
        self.assertTrue(universe.admit_resume_record(self._good(), backend_hash="B"))

    def test_old_12255_universe_rejected(self):
        r = self._good(); r["obligation_universe_total"] = 12255
        with self.assertRaises(universe.ResumeRejected):
            universe.admit_resume_record(r, backend_hash="B")

    def test_old_successor_checkpoint_hash_rejected(self):
        r = self._good()
        r["checkpoint_hash"] = \
            "a5d09f83078bf02ae5d015bfb08eb35429190f646cc51260f6ca72fce6e325ec"
        with self.assertRaises(universe.ResumeRejected):
            universe.admit_resume_record(r, backend_hash="B")

    def test_mismatched_implementation_hash_rejected(self):
        r = self._good(); r["implementation_hash"] = "0" * 64
        with self.assertRaises(universe.ResumeRejected):
            universe.admit_resume_record(r, backend_hash="B")

    def test_mismatched_backend_cells_or_precision_rejected(self):
        for field, bad in (("backend_hash", "X"), ("cells_sha256", "0" * 64),
                           ("precision_bits", 384)):
            r = self._good(); r[field] = bad
            with self.assertRaises(universe.ResumeRejected):
                universe.admit_resume_record(r, backend_hash="B")


class DerivativeDependency(unittest.TestCase):
    def test_matches_frozen_reference_exactly(self):
        ef, ed = depgraph.reference_resolvent_errors(3, F(1, 100), F(2, 100),
                                                     F(4, 5), F(1, 1000), F(1, 50))
        self.assertEqual((ef, ed), (F(9, 100), F(279, 1000)))
        self.assertEqual((ef, ed), FROZEN.resolvent_errors(
            3, F(1, 100), F(2, 100), F(4, 5), F(1, 1000), F(1, 50)))

    def test_zero_dependency_case(self):
        ef, ed = depgraph.reference_resolvent_errors(2, F(1, 10), 0, F(1, 2), F(1, 5), 0)
        self.assertEqual(ef, F(1, 5))
        self.assertEqual(ed, 2 * (F(1, 5) + F(1, 2) * F(1, 5)))

    def test_single_and_combined_dependency_activation(self):
        base = depgraph.reference_resolvent_errors(1, 0, 0, 1, 0, 0)[1]
        self.assertEqual(base, 0)
        only_kf = depgraph.reference_resolvent_errors(1, F(1, 10), 0, 1, 0, 0)[1]
        only_s1 = depgraph.reference_resolvent_errors(1, 0, 0, 1, 0, F(1, 10))[1]
        both = depgraph.reference_resolvent_errors(1, F(1, 10), 0, 1, 0, F(1, 10))[1]
        self.assertEqual(only_kf, F(1, 10))
        self.assertEqual(only_s1, F(1, 10))
        self.assertEqual(both, only_kf + only_s1)

    def test_no_term_may_be_omitted(self):
        full = depgraph.reference_resolvent_errors(3, F(1, 100), F(2, 100),
                                                   F(4, 5), F(1, 1000), F(1, 50))[1]
        omit_kf = 3 * (F(1, 1000) + F(1, 50))
        omit_s1 = 3 * (F(1, 1000) + F(4, 5) * F(9, 100))
        self.assertGreater(full, omit_kf)
        self.assertGreater(full, omit_s1)

    def test_leibniz_power_step_matches_frozen(self):
        got = depgraph.reference_power_step(1, 2, 3, (5, 7, 11), (13, 17, 19))
        self.assertEqual(got, (18, 34, 73))
        self.assertEqual(got, FROZEN.power_error_step(1, 2, 3, (5, 7, 11), (13, 17, 19)))

    def test_negative_inputs_rejected(self):
        with self.assertRaises(ValueError):
            depgraph.reference_resolvent_errors(3, -1, 0, 1, 1, 0)


class NoDoubleCounting(unittest.TestCase):
    def _dag(self):
        with workprec(256):
            norms = opnorms.table(exact(0))
        return depgraph.ErrorDAG(C=exact(2), norms=norms)

    def test_duplicate_local_certificate_rejected(self):
        d = self._dag()
        with workprec(256):
            d.local("x", arb(1), owner="F_equation_certificate_value", order=0)
            with self.assertRaises(depgraph.DoubleCountingError):
                d.local("x", arb(1), owner="F_equation_certificate_value", order=0)

    def test_duplicate_node_assignment_rejected(self):
        d = self._dag()
        d.set("n", arb(1))
        with self.assertRaises(depgraph.DoubleCountingError):
            d.set("n", arb(2))

    def test_duplicate_tagged_edge_rejected(self):
        d = self._dag()
        with workprec(256):
            d.local("l1", arb(0), owner="finite_kernel_chain_value", order=0)
            d.local("l2", arb(0), owner="finite_kernel_chain_value", order=0)
            d.set("src", arb(1))
            d.operator_sum("a", 0, "l1", [(1, arb(1), "src")],
                           owner="finite_kernel_chain_value")
            d._edge_keys.discard(("src", "a", 0, "1", "finite_kernel_chain_value"))
            d._edge_keys.add(("src", "b", 0, "1", "finite_kernel_chain_value"))
            with self.assertRaises(depgraph.DoubleCountingError):
                d.operator_sum("b", 0, "l2", [(1, arb(1), "src")],
                               owner="finite_kernel_chain_value")

    def test_duplicate_ledger_charge_rejected(self):
        d = self._dag()
        with workprec(256):
            d.charge(primitive="p", path="F->R", destination="R", order=0,
                     owner="F_equation_certificate_value", amount=arb(1))
            with self.assertRaises(depgraph.DoubleCountingError):
                d.charge(primitive="p", path="F->R", destination="R", order=0,
                         owner="F_equation_certificate_value", amount=arb(1))

    def test_same_primitive_may_reach_R_and_Rprime(self):
        """Distinct (destination, order) is a DIFFERENT charge, not a duplicate."""
        d = self._dag()
        with workprec(256):
            d.charge(primitive="p", path="F->R", destination="R", order=0,
                     owner="F_equation_certificate_value", amount=arb(1))
            d.charge(primitive="p", path="F->D", destination="D", order=1,
                     owner="Kprime_F_dependency", amount=arb(1))
        self.assertEqual(len(d.charges), 2)

    def test_value_style_derivative_charge_rejected(self):
        """The old campaign's C*delta_dF against B_candidate is refused."""
        d = self._dag()
        with workprec(256):
            with self.assertRaises(depgraph.ValueStyleDerivativeCharge):
                d.charge(primitive="dF_0", path="dF->R", destination="R", order=1,
                         owner="F_equation_certificate_value", amount=arb(1))
            with self.assertRaises(depgraph.ValueStyleDerivativeCharge):
                d.local("bad", arb(1), owner="source_dependency_value", order=1)

    def test_missing_dependency_is_not_zero(self):
        d = self._dag()
        with workprec(256):
            d.local("l", arb(0), owner="finite_kernel_chain_value", order=0)
            with self.assertRaises(depgraph.MissingDependency):
                d.operator_sum("y", 0, "l", [(1, arb(1), "absent")],
                               owner="finite_kernel_chain_value")

    def test_separate_derivative_charge_refused_in_cover(self):
        with workprec(256):
            with self.assertRaises(ledger.SeparateDerivativeCharge):
                ledger.cover_charge(arb(1), F(1, 10), arb(1),
                                    separate_derivative_charge=F(1, 5))
            with self.assertRaises(ValueError):
                FROZEN.cover(FROZEN.Interval(0, 0), FROZEN.Interval(-1, 1),
                             F(1, 10), 1, separate_derivative_charge=F(1, 5))


class Assembly(unittest.TestCase):
    def test_coefficients_match_frozen_config_and_reference(self):
        self.assertTrue(assembly.check_frozen_coefficient_table())
        for m in spec.M_VALUES:
            self.assertEqual(sorted(assembly.coefficients(m)), sorted(FROZEN.terms(m)))

    def test_coefficients_match_short_stop_decomposition(self):
        for m in spec.M_VALUES:
            self.assertEqual(set(assembly.coefficients(m)),
                             set(assembly.short_stop_decomposition(m)))

    def test_no_leading_e_term(self):
        with workprec(256):
            with self.assertRaises(ValueError):
                assembly.assemble(1, {0: arb(1)}, {}, leading_e=arb(1))

    def test_interval_assembly_contains_exact_reference(self):
        """The Arb assembly must CONTAIN the exact-rational reference result."""
        with workprec(256):
            fv = {r: exact(F(r + 1, 7)) for r in range(5)}
            wv = {(r, j): exact(F(r - j, 11)) for r in range(4) for j in range(4 - r)}
            for m in spec.M_VALUES:
                got = assembly.assemble(m, fv, wv)
                want = sum(F(r + 1, 7) * c for k, r, j, c in
                           assembly.coefficients(m) if k == "F")
                want += sum(F(r - j, 11) * c for k, r, j, c in
                            assembly.coefficients(m) if k == "W")
                self.assertTrue(got.contains(exact(want)), (m, str(got)))

    def test_interval_assembly_matches_frozen_reference_structure(self):
        fv = {r: FROZEN.Interval(r, r + F(1, 10)) for r in range(5)}
        wv = {(r, j): FROZEN.Interval(r - j, r - j + F(1, 20))
              for r in range(4) for j in range(4 - r)}
        with workprec(256):
            for m in spec.M_VALUES:
                ref = FROZEN.assemble(m, fv, wv)
                afv = {r: exact(r) .union(exact(r + F(1, 10))) for r in range(5)}
                awv = {k: exact(v.lo).union(exact(v.hi)) for k, v in wv.items()}
                got = assembly.assemble(m, afv, awv)
                self.assertTrue(got.contains(exact(ref.lo)))
                self.assertTrue(got.contains(exact(ref.hi)))

    def test_all_three_orders_use_the_same_coefficients(self):
        for m in spec.M_VALUES:
            base = assembly.coefficients(m)
            for _order in (0, 1, 2):
                self.assertEqual(assembly.coefficients(m), base)

    def test_curvature_bound_nonnegative_and_is_magnitude(self):
        with workprec(256):
            v = exact(-3).union(exact(1))
            got = mag_fraction(assembly.curvature_bound(v))
            self.assertGreaterEqual(got, F(3))          # outward
            self.assertLess(got, F(3) + F(1, 10 ** 6))
            self.assertTrue(assembly.curvature_bound(v) >= 0)

    def test_scope_rejects_m_outside_frozen_set(self):
        for bad in (0, 4, 6):
            with self.assertRaises(ValueError):
                assembly.coefficients(bad)

    def test_e0_value_identity_m1(self):
        """For m=1 the assembly is exactly F_0, with no finite-power part."""
        self.assertEqual(assembly.coefficients(1), [("F", 0, 0, F(1))])


class OutwardRounding(unittest.TestCase):
    def test_outward_upper_never_below_the_true_upper(self):
        with workprec(256):
            for v in (F(1, 3), F(-1, 3), F(0), F(22, 7), F(1, 10 ** 20)):
                x = exact(v)
                self.assertGreaterEqual(outward_upper(x), upper_fraction(x))
                self.assertGreaterEqual(outward_upper(x), v)

    def test_outward_upper_lands_on_the_dyadic_grid(self):
        with workprec(256):
            got = outward_upper(exact(F(1, 3)), bits=8)
            self.assertEqual((got * 256).denominator, 1)
            self.assertGreaterEqual(got, F(1, 3))
            self.assertLess(got - F(1, 3), F(1, 256))

    def test_record_endpoints_are_exact_rationals_not_floats(self):
        with workprec(256):
            r = record(exact(F(1, 3)))
            self.assertNotIn(".", r["lo"] + r["hi"])
            self.assertLessEqual(F(r["lo"]), F(1, 3))
            self.assertGreaterEqual(F(r["hi"]), F(1, 3))

    def test_exact_rational_injection_encloses(self):
        with workprec(256):
            self.assertTrue(exact(F(1, 3)).contains(arb(1) / arb(3)))


class CoverLedger(unittest.TestCase):
    def test_matches_frozen_reference_cover_amount(self):
        with workprec(256):
            D = exact(1) + arb(0, 4)              # exactly [-3, 5]
            got = ledger.cover_charge(D, F(1, 10), exact(4))
            _, want = FROZEN.cover(FROZEN.Interval(1, 2), FROZEN.Interval(-3, 5),
                                   F(1, 10), 4)
            self.assertEqual(want, F(13, 25))
            self.assertGreaterEqual(got["usage"], want)      # outward, never below
            # Arb radii carry 30-bit granularity; the slack is outward and tiny.
            self.assertLess(got["usage"] - want, want * F(1, 10 ** 6))

    def test_children_sum_to_the_single_charge(self):
        with workprec(256):
            D = exact(1) + arb(0, 4)
            got = ledger.cover_charge(D, F(1, 10), exact(4))
            c = got["children"]
            total = (c["nominal_first_order"] + c["derivative_uncertainty"]
                     + c["curvature"])
            self.assertTrue(total >= got["exact"] - exact(F(1, 10 ** 40)))

    def test_taylor_encloses_a_known_quadratic_on_the_whole_cell(self):
        # R(e) = 2 + 3e + 4e^2 about e0 = 0, cell [-1/4, 1/4], R'' = 8.
        with workprec(256):
            enc = ledger.taylor_enclosure(exact(2), exact(3), F(1, 4), exact(8))
            for e in (F(-1, 4), F(-1, 8), F(0), F(1, 8), F(1, 4)):
                self.assertTrue(enc.contains(exact(2 + 3 * e + 4 * e * e)), e)

    def test_target_gate_requires_strictly_inside_minus2_2(self):
        with workprec(256):
            self.assertEqual(ledger.target_gate(exact(0).union(exact(1)))["status"],
                             "PASS")
            self.assertEqual(ledger.target_gate(exact(0).union(exact(3)))["status"],
                             "FAIL")
            self.assertEqual(ledger.target_gate(exact(-2).union(exact(2)))["status"],
                             "FAIL")

    def test_missing_input_is_not_computed_never_pass(self):
        g = ledger.top_level_gates({"B_candidate": F(1, 100)})
        self.assertEqual(g["B_kernel"]["status"], "NOT_COMPUTED")
        self.assertEqual(g["total"]["status"], "NOT_COMPUTED")
        self.assertIsNone(g["B_kernel"]["usage"])

    def test_over_cap_usage_fails(self):
        g = ledger.top_level_gates({k: F(1) for k in spec.TOP_BUDGETS})
        self.assertEqual(g["total"]["status"], "FAIL")

    def test_reserve_is_never_drawable(self):
        g = ledger.top_level_gates({k: F(0) for k in spec.TOP_BUDGETS})
        self.assertFalse(g["top_reserve"]["drawable"])
        self.assertEqual(g["B_resolvent"]["cap"], "0/1")
        n = ledger.nested_candidate_gates({q: F(0) for q in
                                           ("eq", "trunc", "tail", "end", "int", "round")})
        self.assertFalse(n["B_reserve"]["drawable"])

    def test_b_other_has_no_claimant(self):
        self.assertNotIn("B_other", set(spec.CLAIMANT_OWNERS.values()))


class OperatorNorms(unittest.TestCase):
    """The whole-cell curvature certificate rests on these; check them numerically."""

    @staticmethod
    def _numeric_abs_integral(he, n=400001, lim=12.0):
        # Diagnostic Simpson cross-check ONLY; never a certificate.
        h = 2 * lim / (n - 1)
        total = 0.0
        for i in range(n):
            x = -lim + i * h
            w = 1 if i in (0, n - 1) else (4 if i % 2 else 2)
            total += w * abs(he(x)) * exp(-0.5 * x * x) / sqrt(2 * pi)
        return total * h / 3

    def test_kernel_norms_bound_the_numeric_integrals(self):
        hes = {0: lambda x: 1.0, 1: lambda x: x, 2: lambda x: x * x - 1,
               3: lambda x: x ** 3 - 3 * x}
        with workprec(256):
            for i, he in hes.items():
                numeric = self._numeric_abs_integral(he)
                bound = float(opnorms.kernel_norm(i).abs_upper())
                self.assertGreaterEqual(bound, numeric * (1 - 1e-9), i)
                self.assertLess(bound, numeric * 1.02 + 1e-12, i)

    def test_z_moments_bound_the_numeric_integrals(self):
        hes = {0: lambda x: 1.0, 1: lambda x: x, 2: lambda x: x * x - 1}
        with workprec(256):
            for i, he in hes.items():
                numeric = self._numeric_abs_integral(lambda x, he=he: x * he(x))
                self.assertGreaterEqual(
                    float(opnorms.z_moment(i).abs_upper()), numeric * (1 - 1e-9), i)

    def test_frozen_named_bounds(self):
        with workprec(256):
            self.assertLessEqual(float(opnorms.kernel_norm(0).abs_upper()), 1.0)
            self.assertAlmostEqual(float(opnorms.kernel_norm(1).abs_upper()),
                                   2 * exp(0) / sqrt(2 * pi), places=10)
            self.assertAlmostEqual(float(opnorms.kernel_norm(2).abs_upper()),
                                   4 * exp(-0.5) / sqrt(2 * pi), places=10)
            # M_2 reproduces the independently frozen raw-variable constant.
            self.assertAlmostEqual(float(opnorms.z_moment(2).abs_upper()),
                                   1.13788, places=5)

    def test_cramer_supremum_dominates_the_true_supremum(self):
        with workprec(256):
            for n, he in ((0, lambda x: 1.0), (1, lambda x: x),
                          (2, lambda x: x * x - 1), (3, lambda x: x ** 3 - 3 * x)):
                true_sup = max(abs(he(x / 100)) * exp(-0.5 * (x / 100) ** 2)
                               / sqrt(2 * pi) for x in range(-800, 801))
                self.assertGreaterEqual(
                    float(opnorms.sup_phi_derivative(n).abs_upper()), true_sup, n)

    def test_raw_operator_norm_includes_the_leibniz_terms(self):
        with workprec(256):
            emax = exact(2)
            for i in (1, 2):
                bare = opnorms.z_kernel_norm(i, emax) + emax * opnorms.kernel_norm(i)
                self.assertGreater(opnorms.raw_kernel_norm(i, emax), bare)

    def test_norms_are_not_sampled(self):
        self.assertFalse(
            opnorms.table(exact(0))["provenance"]["sampled_operator_norms_used"])


class ProductionGuard(unittest.TestCase):
    def test_production_disabled(self):
        self.assertFalse(spec.PRODUCTION_ENABLED)
        self.assertFalse(spec.CHECKPOINT["no_production_authorization_from_this_checkpoint"]
                         is not True)
        with self.assertRaisesRegex(RuntimeError, "PRODUCTION_DISABLED"):
            FROZEN.require_production()

    def test_no_production_result_directories(self):
        for folder in ("results", "certificates", "production_logs"):
            self.assertFalse((NS / folder).exists(), folder)
            self.assertFalse((SPEC_NS / folder).exists(), folder)

    def test_sr_cell_is_not_implemented_never_passed(self):
        import qualify
        rec = qualify.run_cell("SR", 0)
        self.assertEqual(rec["status"], "NOT_IMPLEMENTED")
        self.assertNotIn("PASS", json.dumps(rec))

    def test_representative_set_is_small(self):
        import qualify
        self.assertEqual(len(qualify.ANCHORS), 6)
        self.assertLessEqual(len(qualify.anchor_cells("CUSUM")),
                             qualify.MAX_REPRESENTATIVE_CELLS)


class FrozenNamespaceUntouched(unittest.TestCase):
    def test_frozen_successor_tree_byte_identical(self):
        manifest = json.loads((SPEC_NS / "manifests/freeze.json").read_text())
        import hashlib
        actual = {}
        for p in SPEC_NS.rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts \
                    and p != SPEC_NS / "manifests/freeze.json":
                actual[str(p.relative_to(SPEC_NS))] = \
                    hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(actual, manifest["files"])

    def test_implementation_writes_only_inside_its_own_namespace(self):
        changed = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT).decode().splitlines()
        rel = str(NS.relative_to(ROOT))
        stray = [line for line in changed if rel not in line]
        self.assertEqual(stray, [], f"writes outside {rel}: {stray}")


class Layer1Fidelity(unittest.TestCase):
    def test_local_dyadic_candidate_matches_frozen_spectral_candidate(self):
        import numpy as np
        import cusum_layer1 as L1
        try:
            from rebaseguard_certify.spectral_candidate import SpectralCandidate
        except ModuleNotFoundError:                       # scipy absent
            self.skipTest("frozen SpectralCandidate needs scipy")
        rng = np.random.default_rng(20260905)
        vals = rng.normal(size=(13, 13))
        want = SpectralCandidate(vals, L1.H_FROZEN).to_chebyshev_dyadic(
            scale_bits=L1.SCALE_BITS)
        got = L1.dyadic_candidate(vals, 13)
        self.assertEqual(got["numerators"], want["numerators"])
        self.assertEqual(got["degree"], want["degree"])
        self.assertEqual((got["h_num"], got["h_den"]), (want["h_num"], want["h_den"]))

    def test_frozen_geometry_constants_unchanged(self):
        import cusum_layer2  # noqa: F401  (sets the frozen module search path)
        import cusum_layer1 as L1
        import ra_certifier as RA
        self.assertEqual((L1.K_FROZEN, L1.H_FROZEN), (RA.K_FROZEN, RA.H_FROZEN))
        self.assertEqual(L1.DEGREE, RA.DEGREE)
        self.assertEqual(L1.QUADRATURE, RA.QUADRATURE)
        self.assertEqual(L1.SCALE_BITS, RA.SCALE_BITS)

    def test_second_order_operators_present(self):
        import cusum_layer1 as L1
        co = L1.collocation(0.25, degree=4, quad=20)
        for key in ("K", "Kz", "dK", "dKz", "ddK", "ddKz", "S0", "dS0", "ddS0"):
            self.assertIn(key, co)

    def test_w_indices_cover_the_frozen_assembly(self):
        import cusum_layer1 as L1
        needed = {(r, j) for m in spec.M_VALUES
                  for k, r, j, c in assembly.coefficients(m) if k == "W" and j >= 1}
        self.assertTrue(needed <= set(L1.W_INDICES))


if __name__ == "__main__":
    unittest.main(verbosity=2)
