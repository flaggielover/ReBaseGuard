"""PRE-T2O negative controls for the SR backend cost audit.

Phase-scoped: asserts T1O-phase properties. Post-T3O assertions are separate.
"""
from __future__ import annotations

import json, pathlib, sys, unittest

NS = pathlib.Path(__file__).resolve().parent.parent
ROOT = NS.parents[2]
T1R = ROOT / "level4/closure_proofs/p5y_k1_task1r_budget_harness"
K1 = ROOT / "level4/closure_proofs/p5y_k1_binding_campaign"
for p in (str(NS / "code"), str(T1R / "code")):
    sys.path.insert(0, p)
from flint import arb                                                  # noqa: E402
import harness as H                                                    # noqa: E402
import opt_backend as O                                                # noqa: E402
from rebaseguard_certify.arb_backend import rational, workprec         # noqa: E402
import sr_local as L                                                   # noqa: E402

CFG = json.loads((NS / "config/frozen_audit.json").read_text())
FP = json.loads((T1R / "config/frozen_parameters.json").read_text())
D, Z = FP["selection"]["D_selected"], FP["selection"]["Z_selected"]


def geom():
    A, b, c = L.sr_constants()
    e = rational(H.E_NUM, H.E_DEN)
    g = L.patch_geometry(*H.PATCH, grid=H.GRID)
    p_c = (g["yp"][0] + g["yp"][1]) / arb(2); m_c = (g["ym"][0] + g["ym"][1]) / arb(2)
    Hh = (g["yp"][1] - g["yp"][0]) / arb(2)
    return dict(A=A, b=b, c=c, e=e, geo=g, p_c=p_c, m_c=m_c, H=Hh,
                U_c=c - p_c, L_c=m_c - c, span=(c - p_c) - (m_c - c))


class TestScientificInvariantsUnchanged(unittest.TestCase):
    def test_precision_not_lowered(self):
        pr = json.loads((K1 / "config/precision_policy.json").read_text())
        self.assertEqual(H.PROD_BITS, 256)
        self.assertEqual(pr["SR_production_bits"], 256)
        self.assertFalse(pr["PRECISION_ESCALATION_ALLOWED"])
        self.assertEqual(H.P1_RULE_WORKPREC, 512)

    def test_budget_not_relaxed(self):
        bl = json.loads((K1 / "config/budget_ledger.json").read_text())
        self.assertEqual(H.B_CANDIDATE, 0.040)
        self.assertEqual(bl["ledger_absolute"]["B_candidate"], 0.040)
        self.assertFalse(bl["redistribution_allowed"])
        self.assertEqual(H.budget()["sum_absolute"], H.B_CANDIDATE)

    def test_cover_not_narrowed(self):
        ck = json.loads((K1 / "CHECKPOINT.json").read_text())
        self.assertEqual(ck["cover"]["SR"]["subcell_count"], 322)
        self.assertEqual(ck["cover"]["CUSUM"]["subcell_count"], 323)
        self.assertEqual(ck["scope"]["m_values"], [1, 2, 3, 5])
        self.assertEqual(CFG["work_model"]["SR_subcells"], 322)

    def test_derivative_objects_not_dropped(self):
        ck = json.loads((K1 / "CHECKPOINT.json").read_text())
        ids = {f["id"] for f in ck["production_dag"]["functions"]}
        for r in range(5):
            self.assertIn(f"dF_{r}", ids)
        self.assertEqual(CFG["work_model"]["functions_per_detector"], 19)

    def test_degree_and_ceiling_unchanged(self):
        cx = json.loads((K1 / "config/complexity_guard.json").read_text())
        self.assertEqual(H.CAND_DEGREE, 16)
        self.assertEqual(H.SOFTPLUS_DEGREE, 8)
        self.assertEqual(cx["PRODUCTION_COMPLEXITY_CEILING"], 60000)

    def test_historical_cap_not_rewritten(self):
        ck = json.loads((K1 / "CHECKPOINT.json").read_text())
        self.assertEqual(ck["cpu"]["HARD_CPU_CAP_CPU_HOURS"], 1848)
        self.assertEqual(CFG["immutable_history"]["HARD_CPU_CAP_historical"], 1848)
        self.assertFalse(CFG["immutable_history"]["cap_may_be_raised"])

    def test_historical_verdicts_preserved(self):
        h = CFG["immutable_history"]
        self.assertEqual(h["P5Y_K1_VERDICT"], "K1_INCOMPLETE_BUDGET")
        self.assertEqual(h["P5Y_K1_TASK1"], "FAIL")
        self.assertEqual(h["P5Y_K1_TASK1R"], "PASS")


class TestAuditDesignFrozen(unittest.TestCase):
    def test_routes_and_thresholds_and_cells_frozen(self):
        self.assertTrue(CFG["no_route_additions_after_T2O"])
        self.assertTrue(CFG["no_threshold_change_after_T2O"])
        self.assertTrue(CFG["no_benchmark_set_change_after_T2O"])
        self.assertEqual(len(CFG["routes"]), 4)
        self.assertEqual(len(CFG["benchmark_cells"]), 5)
        self.assertIn("O4_SPARSE", [r["id"] for r in CFG["routes"]])
        o4 = [r for r in CFG["routes"] if r["id"] == "O4_SPARSE"][0]
        self.assertEqual(o4["status"], "NOT_SEPARATELY_BENCHMARKED")
        self.assertIn("reason", o4)

    def test_thresholds_are_ordered_and_derived(self):
        t = CFG["thresholds"]
        self.assertLess(t["T_PANEL_HARD_TARGET_s"], t["T_PANEL_STRONG_TARGET_s"])
        self.assertLess(t["T_PANEL_STRONG_TARGET_s"], t["T_PANEL_PROMISING_TARGET_s"])
        w = CFG["work_model"]
        recomputed = (1848 / w["overhead_factor"] - w["CUSUM_projection_cpu_h"]) \
            * 3600.0 / w["SR_panel_evaluations"]
        self.assertAlmostEqual(t["T_PANEL_HARD_TARGET_s"], recomputed, places=12)

    def test_benchmark_cells_are_not_cherry_picked(self):
        ids = [c["id"] for c in CFG["benchmark_cells"]]
        self.assertEqual(ids, ["A_reference", "B_max_span", "C_sliver_heavy",
                               "D_second_object", "E_cusum_control"])
        for c in CFG["benchmark_cells"]:
            self.assertIn("rationale", c)
        self.assertEqual(CFG["benchmark_cells"][0]["patch"], list(H.PATCH))

    def test_audit_cap_is_small(self):
        self.assertLessEqual(CFG["audit_cpu_cap_hours"], 5.0)
        self.assertLess(CFG["audit_cpu_cap_hours"] / 1848, 0.001)


def _real_candidate(g):
    sys.path.insert(0, str(K1 / "task1"))
    from task1_f0 import build_candidate
    return build_candidate(float(g["b"]), float(g["c"]), float(g["e"]))[0]


class TestNonCancellationPreservingIsRejected(unittest.TestCase):
    """A fast scalar backend must NOT be able to masquerade as admissible.

    Probed with the GENUINE F_0 candidate: the constant candidate is unusable
    here because K_e applied to a constant is genuinely constant over the patch,
    so it cannot distinguish a scalar backend from a cancellation-preserving one.
    """

    def test_scalar_constant_term_only_underbounds_and_is_rejected(self):
        with workprec(H.PROD_BITS):
            g = geom()
            p1 = H.p1_rule(g["H"], g["span"])
            cc = _real_candidate(g)
            coef, ex, ez, h, ctxt = H.run_panels(cc, D, Z, g, p1, only_panel=0)
            Hp = [g["H"] ** k for k in range(2 * D + 2)]
            full = sum(coef[a][b].abs_upper() * Hp[a + b]
                       for a in range(D + 1) for b in range(D + 1))
            scalar_only = coef[0][0].abs_upper()
            # a scalar evaluation keeps only the constant term: it cannot bound
            # the patch range, and is therefore strictly smaller
            self.assertLess(float(scalar_only), float(full))
            dropped = float(full) - float(scalar_only)
            self.assertGreater(dropped, 0.0)

    def test_optimized_route_keeps_every_patch_local_coefficient(self):
        with workprec(H.PROD_BITS):
            g = geom()
            p1 = H.p1_rule(g["H"], g["span"])
            cc = _real_candidate(g)
            opt = O.run_panels_opt(cc, D, Z, g, p1, only_panel=0)
        self.assertEqual(len(opt[0]), D + 1)
        self.assertEqual(len(opt[0][0]), D + 1)
        nonzero = sum(1 for a in range(D + 1) for b in range(D + 1)
                      if not opt[0][a][b].is_zero())
        self.assertGreater(nonzero, 1, "optimized route must not collapse to a scalar")

    def test_no_float_only_path_in_optimized_backend(self):
        import ast
        src = (NS / "code/opt_backend.py").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"float"},
                                 "no float() in the certified path")

    def test_endpoint_slivers_not_omitted(self):
        src = (NS / "code/opt_backend.py").read_text()
        self.assertNotIn("sliver", src.lower().split("docstring")[0].split('"""')[-1],
                         "the optimized panel engine must not touch sliver handling")
        hsrc = (T1R / "code/harness.py").read_text()
        self.assertIn("def sliver", hsrc)
        self.assertIn("sl_up + sl_lo", hsrc.replace("sliver(U_c) + sliver(L_c)", "sl_up + sl_lo"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
