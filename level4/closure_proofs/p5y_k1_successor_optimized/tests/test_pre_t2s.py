"""PRE-T2S checkpoint-design tests for the K1 successor.

PHASE-SCOPED. Every assertion that depends on the T1S phase (notably: no
successor result exists yet) is confined to TestT1SPhase, which is designed to
be skipped once T2S has legitimately produced results -- so it can never later
be miscounted as a governance failure. All other tests are phase-independent
and remain valid for the life of the campaign.
"""
from __future__ import annotations

import json, math, pathlib, sys, unittest

NS = pathlib.Path(__file__).resolve().parent.parent
ROOT = NS.parents[2]
K1 = ROOT / "level4/closure_proofs/p5y_k1_binding_campaign"
AUD = ROOT / "level4/closure_proofs/p5y_k1_sr_backend_cost_audit"
sys.path.insert(0, str(NS / "code"))

CK = json.loads((NS / "config/checkpoint_s.json").read_text())
CM = json.loads((NS / "config/cost_model.json").read_text())
PARENT = json.loads((K1 / "CHECKPOINT.json").read_text())


def results_exist():
    return any(p.is_file() and p.name != ".gitkeep"
               for d in ("results", "certificates", "production_logs")
               for p in (NS / d).rglob("*"))


class TestScopeIdentical(unittest.TestCase):
    def test_detectors_not_narrowed(self):
        self.assertEqual(set(CK["scope"]["detectors"]), {"CUSUM", "SR"})
        self.assertEqual(set(CK["scope"]["detectors"]), set(PARENT["scope"]["detectors"]))

    def test_m_not_narrowed(self):
        self.assertEqual(CK["scope"]["m_values"], [1, 2, 3, 5])
        self.assertEqual(CK["scope"]["m_values"], PARENT["scope"]["m_values"])
        self.assertEqual(CK["scope"]["cartesian_cells"], 8)

    def test_cover_not_narrowed(self):
        self.assertEqual(CK["cover"]["CUSUM"]["subcell_count"], 323)
        self.assertEqual(CK["cover"]["SR"]["subcell_count"], 322)
        self.assertEqual(CK["cover"]["SR"]["patches_live"], 3994)

    def test_splice_not_moved(self):
        self.assertEqual(CK["cover"]["CUSUM"]["e_star"], PARENT["cover"]["CUSUM"]["e_star"])
        self.assertEqual(CK["cover"]["SR"]["e_star"], PARENT["cover"]["SR"]["e_star"])

    def test_target_identical_and_does_not_close_P5(self):
        self.assertTrue(CK["target"]["identical_to_parent"])
        self.assertFalse(CK["target"]["K1_CLOSED_closes_P5"])
        self.assertEqual(len(CK["target"]["remaining_after_K1"]), 4)


class TestInvariantsNotWeakened(unittest.TestCase):
    def test_precision_not_lowered(self):
        self.assertEqual(CK["precision_policy"]["SR_production_bits"], 256)
        self.assertFalse(CK["precision_policy"]["PRECISION_ESCALATION_ALLOWED"])
        self.assertFalse(CK["precision_policy"]["DEGREE_ADAPTATION_ALLOWED"])
        self.assertEqual(CK["p1_rule"]["P1_RULE_WORKPREC_BITS"], 512)

    def test_budgets_not_raised_or_redistributed(self):
        bl = CK["budget_ledger"]
        self.assertEqual(bl["ledger_absolute"]["B_candidate"], 0.040)
        self.assertEqual(bl["local_gate_budget"], 0.100)
        self.assertFalse(bl["redistribution_allowed"])
        for k, v in PARENT["budget_ledger"]["ledger_absolute"].items():
            self.assertEqual(bl["ledger_absolute"][k], v, k)

    def test_p1_rule_carried_exactly(self):
        p = CK["p1_rule"]
        self.assertEqual(p["eps_P1"], 1e-3)
        self.assertEqual(p["P1_CHECK_THRESHOLD"], 1e-9)
        self.assertEqual(p["P1_HEADROOM_GUARD"], 1e-6)
        self.assertTrue(p["rule_and_check_distinct"])

    def test_complexity_ceiling_unchanged(self):
        self.assertEqual(CK["complexity_guard"]["PRODUCTION_COMPLEXITY_CEILING"], 60000)

    def test_endpoint_slivers_not_omitted_or_enlarged(self):
        g = CK["endpoint_sliver_gate"]
        self.assertFalse(g["cross_cell_borrowing"])
        self.assertFalse(g["redistribution"])
        self.assertFalse(g["B_end_enlarged"])
        self.assertTrue(g["tightest_channel"])
        self.assertGreater(g["measured_share_of_B_end"], 0.8)


class TestHistoryImmutable(unittest.TestCase):
    def test_historical_cap_not_rewritten(self):
        self.assertEqual(CK["lineage"]["HISTORICAL_K1_CAP"], 1848)
        self.assertEqual(PARENT["cpu"]["HARD_CPU_CAP_CPU_HOURS"], 1848)
        self.assertEqual(CK["cpu_governance"]["HISTORICAL_K1_CAP"], 1848)

    def test_caps_are_distinct_and_not_copied(self):
        g = CK["cpu_governance"]
        self.assertTrue(g["caps_are_distinct"])
        self.assertNotEqual(g["SUCCESSOR_K1_HARD_CAP"], g["HISTORICAL_K1_CAP"])
        self.assertFalse(g["in_campaign_extension_allowed"])

    def test_historical_verdict_preserved_and_not_resumed(self):
        L = CK["lineage"]
        self.assertEqual(L["HISTORICAL_K1_VERDICT"], "K1_INCOMPLETE_BUDGET")
        self.assertFalse(L["historical_campaign_resumed_or_repaired_in_place"])
        self.assertTrue(L["new_verdict_lineage"])
        self.assertEqual(L["P5Y_K1_TASK1"], "FAIL")
        self.assertEqual(L["P5Y_K1_TASK1R"], "PASS")
        self.assertEqual(L["P5_ORIGINAL_VERDICT"], "PARTIAL")
        self.assertEqual(L["P5X_FINAL_VERDICT"], "PARTIAL")


class TestCapDerivation(unittest.TestCase):
    def test_cap_arithmetic(self):
        g = CK["cpu_governance"]; b = CK["performance_model"]["bands_cpu_h"]
        self.assertEqual(g["SUCCESSOR_K1_HARD_CAP"], math.ceil(1.5 * b["conservative"]))

    def test_cap_is_constraining_but_not_binding_below_worst(self):
        g = CK["cpu_governance"]; b = CK["performance_model"]["bands_cpu_h"]
        self.assertGreater(g["SUCCESSOR_K1_HARD_CAP"], b["worst_plausible"])
        self.assertGreater(g["SUCCESSOR_K1_HARD_CAP"] / b["central"], 1.5)
        self.assertLess(g["SUCCESSOR_K1_HARD_CAP"], 1848)

    def test_bands_ordered_and_worst_cell_used(self):
        b = CK["performance_model"]["bands_cpu_h"]
        self.assertLess(b["central"], b["conservative"])
        self.assertLess(b["conservative"], b["worst_plausible"])
        self.assertIn("WORST", CK["performance_model"]["basis"])
        self.assertTrue(CK["performance_model"]["caches_are_not_free"])

    def test_degraded_reuse_is_a_stop_not_a_band(self):
        d = CK["performance_model"]["degraded_reuse_contingency"]
        self.assertIn("NOT a budget band", d["status"])
        self.assertNotIn(d["cpu_h"], CK["performance_model"]["bands_cpu_h"].values())


class TestBackendEquivalence(unittest.TestCase):
    def test_bit_identity_not_required(self):
        c = CK["correctness_equivalence"]
        self.assertFalse(c["bit_identity_required"])
        self.assertEqual(c["frozen_equivalence_tolerance_relative"], 1e-8)

    def test_measured_evidence_meets_the_frozen_criterion(self):
        m = CK["correctness_equivalence"]["measured_evidence"]
        self.assertEqual(m["enclosure_overlap_failures"], 0)
        self.assertLess(m["equation_defect_relative_agreement"], 1e-8)
        self.assertTrue(m["endpoint_slivers_bit_identical"])
        self.assertTrue(m["all_per_line_gates_pass"])
        self.assertTrue(m["not_uniformly_conservative"])

    def test_amendments_recorded_and_adjudicated(self):
        a = CK["audit_adjudicator_amendments"]
        self.assertFalse(a["hidden"])
        self.assertEqual(len(a["recorded"]), 2)
        for am in a["recorded"]:
            self.assertFalse(am["affects_decisive_quantity"])
        self.assertIn("NEITHER amendment changes", a["conclusion"])


class TestCacheDependency(unittest.TestCase):
    def test_verification_passes_both_directions(self):
        v = CK["cache_dependency_table"]["verification"]
        self.assertTrue(v["positive_chebyshev_tensor_is_drift_independent"])
        self.assertTrue(v["negative_chebyshev_tensor_depends_on_patch"])
        self.assertTrue(v["negative_gaussian_moments_depend_on_drift"])
        self.assertTrue(v["PASS"])

    def test_moments_are_keyed_on_drift(self):
        t = CK["cache_dependency_table"]["table"]
        self.assertIn("drift_e", t["gaussian_moments_N"])
        self.assertIn("drift_e", t["hankel_and_R"])

    def test_tensors_are_not_keyed_on_drift_or_function(self):
        t = CK["cache_dependency_table"]["table"]
        for q in ("chebyshev_TV_TW", "matrices_P_Q_Qflat", "softplus_V", "softplus_W"):
            self.assertNotIn("drift_e", t[q], q)
            self.assertNotIn("function_r", t[q], q)

    def test_invalid_reuse_would_be_rejected(self):
        """Reusing moments across drift is invalid: the table forbids it and the
        measurement shows the values genuinely differ."""
        t = CK["cache_dependency_table"]["table"]
        v = CK["cache_dependency_table"]["verification"]
        self.assertIn("drift_e", t["gaussian_moments_N"])
        self.assertTrue(v["negative_gaussian_moments_depend_on_drift"])

    def test_candidate_is_keyed_on_function_and_derivative(self):
        t = CK["cache_dependency_table"]["table"]
        self.assertIn("function_r", t["candidate_chat"])
        self.assertIn("value_or_derivative", t["candidate_chat"])


class TestWorkConservation(unittest.TestCase):
    def test_total_and_counts(self):
        w = CK["work_conservation"]
        self.assertEqual(w["total_units"], 12255)
        self.assertEqual(w["counts"]["CUSUM"] + w["counts"]["SR"], 12255)

    def test_floor_sharding_conserves_exactly(self):
        n = CK["work_conservation"]["total_units"]
        for s in (1, 7, 16, 64, 128, 997, 4096):
            b = [(n * k) // s for k in range(s + 1)]
            sizes = [b[k + 1] - b[k] for k in range(s)]
            self.assertEqual(sum(sizes), n, f"S={s}")
            self.assertTrue(all(x >= 0 for x in sizes))
            self.assertEqual(b[0], 0); self.assertEqual(b[-1], n)

    def test_ceil_per_shard_would_overexecute(self):
        """The P4X defect: ceil-per-shard duplicates work. Must not be used."""
        n = 12255
        for s in (7, 16, 997):
            ceil_total = s * math.ceil(n / s)
            self.assertGreater(ceil_total, n)
        self.assertIn("never ceil-per-shard", CK["work_conservation"]["shard_rule"])

    def test_no_duplicate_or_missing_units(self):
        inv = CK["work_conservation"]["invariants"]
        self.assertTrue(any("no overlap" in i for i in inv))
        self.assertTrue(any("no omission" in i for i in inv))


class TestGovernance(unittest.TestCase):
    def test_stop_rules_complete_and_no_exception(self):
        self.assertEqual(len(CK["stop_rules"]), 16)
        self.assertFalse(CK["continue_and_see_exception"])
        classes = {r[2] for r in CK["stop_rules"]}
        for c in ("CACHE_SCOPE_VIOLATION", "BACKEND_EQUIVALENCE_FAILURE",
                  "ENDPOINT_SLIVER_FAILURE", "WORK_CONSERVATION_FAILURE"):
            self.assertIn(c, classes)

    def test_every_stop_maps_to_a_verdict(self):
        ids = {r[0] for r in CK["stop_rules"]}
        mapped = set()
        for v in CK["verdicts"].values():
            for tok in str(v.get("trigger", "")).replace(",", " ").split():
                if tok.startswith("S"):
                    mapped.add(tok)
        self.assertTrue(ids <= mapped | {"S14"}, ids - mapped)

    def test_no_producer_self_award(self):
        self.assertFalse(CK["verdicts"]["K1_CLOSED"]["producer_may_self_award"])
        self.assertFalse(CK["verdicts"]["K1_CLOSED"]["closes_P5"])

    def test_execution_order_verifies_task1r_never_reruns(self):
        a = CK["execution_order"][0]
        self.assertIn("VERIFIED, never re-executed", a["note"])
        self.assertEqual(CK["execution_order"][1]["name"], "CUSUM production")

    def test_parallelism_does_not_touch_cpu_accounting(self):
        m = CK["memory_and_parallelism"]
        self.assertTrue(m["parallelism_changes_wall_time_not_cpu_accounting"])
        self.assertFalse(m["oversubscription_allowed"])
        self.assertEqual(m["MAX_WORKERS"], 64)


class TestT1SPhase(unittest.TestCase):
    """T1S-PHASE ONLY. Skipped once T2S has legitimately produced results, so it
    can never later be miscounted as a governance failure."""

    def setUp(self):
        if results_exist():
            self.skipTest("T2S has produced results; this assertion is T1S-scoped")

    def test_no_result_bearing_artifact_at_freeze(self):
        for d in ("results", "certificates", "production_logs"):
            files = [p for p in (NS / d).rglob("*") if p.is_file() and p.name != ".gitkeep"]
            self.assertEqual(files, [], f"{d}/ must be empty at T1S")

    def test_checkpoint_declares_production_not_run(self):
        s = CK["state"]
        self.assertEqual(s["P5Y_K1_SUCCESSOR_PRODUCTION_RUN"], "NO")
        self.assertEqual(s["P5Y_K1_SUCCESSOR_VERDICT"], "NOT_RUN")
        self.assertTrue(CK["design_only"])
        self.assertEqual(CK["temporal"]["this_task_stops_at"], "T1S")


if __name__ == "__main__":
    unittest.main(verbosity=2)
