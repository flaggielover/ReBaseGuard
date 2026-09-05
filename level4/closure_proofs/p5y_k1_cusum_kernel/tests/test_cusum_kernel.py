"""Focused tests for the CUSUM raw-variable kernel. No production run."""
from __future__ import annotations
import ast, json, math, pathlib, sys, unittest
NS = pathlib.Path(__file__).resolve().parent.parent
ROOT = NS.parents[2]
for p in (str(ROOT / "rebaseguard-proof/src"), str(NS / "code"),
          str(ROOT / "level4/closure_proofs/p5y_k1_production_driver")):
    sys.path.insert(0, p)
import cusum_raw as CR                                                # noqa: E402
from k1prod import kernel as DK, schema as DS                         # noqa: E402

CERT = json.loads((NS / "results/certification_e_quarter.json").read_text())


class TestRawVariableFidelity(unittest.TestCase):
    def test_raw_reward_has_no_e_term(self):
        """rho_1^raw = phi_u - phi_l. The old g-variable reward carries an extra
        -e(1 - Phi_u + Phi_l); reinserting it would be the deleted +e term."""
        src = (ROOT / "level4/closure_proofs/p5y_micropilot_gate1/raw_certifier.py").read_text()
        fn = src.split("def reward_rho1_raw")[1].split("def ")[0]
        self.assertIn("bi_add(phi_u", fn)
        self.assertNotIn("bracket", fn)

    def test_old_g_variable_certifier_is_not_on_the_production_path(self):
        tree = ast.parse((NS / "code/cusum_raw.py").read_text())
        calls = {n.func.attr for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertNotIn("certify_at_exact_drift", calls)

    def test_geometry_is_the_frozen_cusum_one(self):
        self.assertEqual(float(CR.C), 5.5)
        self.assertEqual(float(CR.K_), 0.5)
        self.assertEqual(float(CR.H_), 5.0)
        self.assertEqual(CR.DEGREE, 12)
        self.assertEqual(CR.BITS, 256)


class TestObjectCoverage(unittest.TestCase):
    def test_all_four_classes_enumerated(self):
        self.assertEqual(CR.H_OBJECTS, ["h_1", "h_2", "h_3", "h_4"])
        self.assertEqual(len(CR.S_OBJECTS), 5)
        self.assertEqual(len(CR.F_OBJECTS), 5)
        self.assertEqual(len(CR.DF_OBJECTS), 5)
        self.assertEqual(len(CR.ALL_OBJECTS), 19)

    def test_every_cusum_work_unit_resolves_to_an_implemented_object(self):
        units = [u for u in DS.enumerate_units(DS.load_checkpoint()) if u[0] == "CUSUM"]
        self.assertEqual(len(units), 323 * 19)
        missing = {fn for d, c, fn in units if not DK.kernel_status(d, fn)[0]}
        self.assertEqual(missing, set())

    def test_no_duplicate_object_mapping(self):
        self.assertEqual(len(CR.ALL_OBJECTS), len(set(CR.ALL_OBJECTS)))


class TestCertifiedBudgets(unittest.TestCase):
    def test_every_object_certified_and_within_its_frozen_budget(self):
        self.assertEqual(len(CERT["rows"]), 19)
        for r in CERT["rows"]:
            self.assertTrue(r["PASS"], f"{r['object']} at {100*r['utilisation']:.2f}%")
        self.assertTrue(CERT["all_pass"])

    def test_budgets_are_the_frozen_ones(self):
        led = DS.load_checkpoint()["budget_ledger"]["ledger_absolute"]
        for r in CERT["rows"]:
            self.assertAlmostEqual(r["allowance"],
                                   led[r["line"]] / CERT["C_CUSUM_quarter"], places=15)

    def test_no_budget_borrowing_between_classes(self):
        lines = {r["class"]: r["line"] for r in CERT["rows"]}
        self.assertEqual(lines["h"], "B_kernel")
        self.assertEqual(lines["S"], "B_kernel")
        self.assertEqual(lines["F"], "B_candidate")
        self.assertEqual(lines["dF"], "B_candidate")


class TestAssembly(unittest.TestCase):
    def test_all_frozen_m_present(self):
        self.assertEqual(sorted(CERT["assembly"]), ["1", "2", "3", "5"])

    def test_R_within_the_K1_target_and_matches_the_measured_probe(self):
        r1 = CERT["assembly"]["1"]["R"]
        self.assertLess(abs(r1), 2.0)
        # FEASIBILITY_AUDIT records a measured probe of 1.576/1.591 at e = 0.25
        self.assertAlmostEqual(abs(r1), 1.576, delta=0.01)

    def test_R_decreases_in_magnitude_with_m(self):
        v = [abs(CERT["assembly"][str(m)]["R"]) for m in (1, 2, 3, 5)]
        self.assertTrue(all(v[i] > v[i + 1] for i in range(3)))

    def test_assembly_uses_the_frozen_general_formula(self):
        from fractions import Fraction
        src = (NS / "code/cusum_raw.py").read_text()
        self.assertIn("Fraction(1, t) - Fraction(1, m)", src)
        self.assertIn("w = min(m, tau)", src)


class TestDerivativeSystem(unittest.TestCase):
    def test_derivatives_are_analytic_not_finite_differenced(self):
        src = (NS / "code/cusum_raw.py").read_text()
        self.assertIn("dK @ F[r]", src)
        self.assertNotIn("(Rp - Rm)", src)

    def test_exact_identity_d_e_h1_equals_minus_S0(self):
        src = (NS / "code/cusum_raw.py").read_text()
        self.assertIn('dh = {1: -co["S0"]}', src)


class TestNoProductionAndNoSRChange(unittest.TestCase):
    def test_certification_artifact_is_one_cell_not_the_cover(self):
        self.assertFalse(CERT["result_bearing"])
        self.assertIn("NOT the frozen cover", CERT["scope"])

    def test_cell_drift_mapping_is_guarded(self):
        self.assertTrue(DK.CELL_DRIFT_IS_PLACEHOLDER)
        rec = DS.new_record("CUSUM", 5, "F_0", ck_hash="a", be_hash="b")
        out = DK.run_unit("CUSUM", 5, "F_0", rec, dry_run=False)
        self.assertEqual(out["status"], "NOT_IMPLEMENTED")
        self.assertEqual(out["failure_class"], "CELL_DRIFT_MAPPING_NOT_IMPLEMENTED")

    def test_sr_kernel_untouched(self):
        self.assertEqual(DK.IMPLEMENTED[("SR", "F_0")],
                         "qualified by Task1R (PASS) and re-timed by the backend audit")
        self.assertNotIn(("SR", "h_1"), DK.IMPLEMENTED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
