"""Tests over the committed qualification evidence and the refinement.

These check that the evidence is internally consistent and honestly labelled.
They are not a scientific qualification and they never authorise production.
"""
from __future__ import annotations

import json
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"
sys.path.insert(0, str(NS / "code"))

import assembly                                                  # noqa: E402
import bench                                                     # noqa: E402
import ledger                                                    # noqa: E402
import spec                                                      # noqa: E402
from flint import arb                                            # noqa: E402
from intervals import exact, workprec                            # noqa: E402

REPS = sorted((NS / "diagnostics/representatives").glob("*.json"))
PREC = sorted((NS / "diagnostics/precision_records").glob("*.json"))
COST = NS / "benchmarks/cost_model.json"


def load(paths):
    return [json.loads(p.read_text()) for p in paths]


class EvidencePresence(unittest.TestCase):
    def test_representative_records_exist_for_every_frozen_m(self):
        recs = load(REPS)
        self.assertGreaterEqual(len(recs), 5)
        for r in recs:
            self.assertEqual({int(m) for m in r["m"]}, set(spec.M_VALUES))

    def test_evidence_is_marked_non_result_bearing(self):
        for r in load(REPS) + load(PREC):
            self.assertFalse(r["result_bearing"])
            self.assertFalse(r["production_run"])
            self.assertFalse(r["scientific_certification_of_full_cover"])

    def test_no_production_directories_created(self):
        for folder in ("results", "certificates", "production_logs"):
            self.assertFalse((NS / folder).exists(), folder)


class LedgerEvidence(unittest.TestCase):
    def test_every_obligation_has_a_decided_status(self):
        for r in load(REPS):
            for m, L in r["m"].items():
                self.assertIn(L["status"], ("PASS", "FAIL"), (r["cell_index"], m))

    def test_no_uncomputed_budget_line_reads_pass(self):
        for r in load(REPS):
            for L in r["m"].values():
                for name, gate in L["top_level_gates"].items():
                    if name == "total" or not isinstance(gate, dict):
                        continue
                    if "cap" in gate and gate.get("usage") is None:
                        self.assertNotEqual(gate.get("status"), "PASS", name)

    def test_failures_are_reported_not_suppressed(self):
        recs = load(REPS)
        statuses = [L["status"] for r in recs for L in r["m"].values()]
        self.assertIn("FAIL", statuses,
                      "the committed evidence must retain its failures")
        failing = [(r["cell_index"], m) for r in recs
                   for m, L in r["m"].items() if L["status"] == "FAIL"]
        # Every failure is at the largest-radius cell, and it is a cover failure.
        for cell, m in failing:
            L = next(r for r in recs if r["cell_index"] == cell)["m"][m]
            self.assertEqual(L["top_level_gates"]["B_cover"]["status"], "FAIL")
            self.assertGreater(L["cover"]["utilization"], 1.0)

    def test_cover_children_reconstruct_the_single_charge(self):
        for r in load(REPS):
            for L in r["m"].values():
                ch = L["cover"]["children"]
                total = (F(ch["nominal_first_order"]) + F(ch["derivative_uncertainty"])
                         + F(ch["curvature"]) + F(ch["cover_arithmetic"]))
                self.assertGreaterEqual(total, F(L["cover"]["usage"]) * F(9999, 10000))

    def test_style_1_recorded_and_b_other_unused(self):
        for r in load(REPS):
            for L in r["m"].values():
                self.assertEqual(L["cover"]["style"], "STYLE_1_COMPLETE_D_INTERVAL")
                self.assertEqual(F(L["top_level_gates"]["B_other"]["usage"]), 0)
                self.assertEqual(L["top_level_gates"]["B_resolvent"]["cap"], "0/1")

    def test_target_gate_enclosures_lie_strictly_inside_minus2_2(self):
        for r in load(REPS):
            for L in r["m"].values():
                self.assertTrue(L["target_gate"]["strictly_inside_minus2_2"])

    def test_no_double_counting_in_any_recorded_dag(self):
        for r in load(REPS):
            for key in ("dag_audit_mid", "dag_audit_cell"):
                self.assertEqual(r[key]["duplicate_edges"], 0)
                self.assertTrue(r[key]["derivative_edges_all_cover"])
                self.assertEqual(r[key]["edges"], r[key]["distinct_edge_keys"])

    def test_whole_cell_bounds_dominate_midpoint_bounds(self):
        for r in load(REPS):
            for name, o in r["objects"].items():
                self.assertGreaterEqual(F(o["delta_cell"]), F(o["delta_mid"]), name)
                if F(o["envelope"]) > 0:
                    self.assertGreater(F(o["delta_cell"]), F(o["delta_mid"]), name)

    def test_refinement_never_loosens_a_bound(self):
        for r in load(REPS):
            for rr, a in r["whole_cell_refinement"].items():
                for k in ("epsF_cell", "epsD_cell", "epsH_cell"):
                    self.assertLessEqual(F(a["refined"][k]), F(a["crude"][k]),
                                         (r["cell_index"], rr, k))

    def test_refinement_contraction_reported_not_assumed(self):
        for r in load(REPS):
            for a in r["whole_cell_refinement"].values():
                # It is evidence, not a hypothesis: the field exists and the
                # refined bound is valid regardless of its value.
                self.assertIn("observed_contraction_factor_rho_C_2k1", a)
                self.assertGreater(F(a["observed_contraction_factor_rho_C_2k1"]), 0)


class PrecisionEvidence(unittest.TestCase):
    def test_three_precisions_present(self):
        if not PREC:
            self.skipTest("no precision records")
        bits = {r["precision_bits"] for r in load(PREC)}
        self.assertEqual(bits, {256, 384, 512})

    def test_production_precision_not_promoted(self):
        data = json.loads((NS / "diagnostics/precision.json").read_text())
        self.assertEqual(data["production_precision_bits"], 256)
        self.assertFalse(data["precision_escalation_allowed"])

    def test_higher_precision_is_contained_and_no_256_bit_failure(self):
        data = json.loads((NS / "diagnostics/precision.json").read_text())
        for key, n in data["nesting"].items():
            self.assertTrue(n["R_contained_in_256"], key)
            self.assertTrue(n["D_contained_in_256"], key)
            self.assertTrue(n["R_overlaps_256"], key)
            # A 256-bit failure rescued only by more bits must be reported.
            if n["higher_bit_gates_pass"]:
                self.assertTrue(n["256_bit_gates_pass"], key)


class CostEvidence(unittest.TestCase):
    def setUp(self):
        self.cost = json.loads(COST.read_text())
        self.proj = self.cost["projection"]

    def test_cap_unchanged_and_not_increased(self):
        self.assertEqual(self.proj["frozen_hard_cap_cpu_h"], 1126)
        self.assertEqual(self.proj["frozen_hard_cap_cpu_h"], spec.HARD_CAP_CPU_H)
        self.assertFalse(self.proj["cap_increased"])

    def test_universe_is_the_new_one(self):
        self.assertEqual(self.proj["governed_work_units"], 17978)

    def test_sr_is_not_claimed_as_measured(self):
        sr = self.proj["SR"]
        self.assertFalse(sr["measured"])
        self.assertEqual(sr["status"], "NOT_MEASURABLE")
        self.assertIn("indicative_extrapolation", sr)
        self.assertIn("NOT a measurement",
                      sr["indicative_extrapolation"]["method"])

    def test_cost_status_is_honest(self):
        status = self.proj["COST_CAP_STATUS"]
        self.assertIn(status, ("PASS_CANDIDATE", "FAIL_BUDGET", "NOT_ESTABLISHED"))
        if status == "FAIL_BUDGET":
            self.assertGreater(self.proj["campaign_indicative"]["central_cpu_h"],
                               1126)

    def test_memory_within_frozen_envelope(self):
        mem = self.proj["memory"]
        self.assertLessEqual(mem["measured_peak_rss_mib_per_worker"],
                             spec.PER_WORKER_BUDGET_MIB)
        self.assertFalse(mem["oversubscription_allowed"])
        self.assertEqual(mem["worker_ceiling"], 64)

    def test_every_residual_is_classified(self):
        for r in load(REPS):
            for name in r["objects"]:
                self.assertIn(bench.classify(name),
                              ("object", "dependency_bundle", "curvature"), name)

    def test_class_costs_sum_to_the_measured_total(self):
        agg = self.cost["aggregate_cpu_seconds"]
        parts = sum(agg[k]["mean_s"] for k in
                    ("object", "dependency_bundle", "curvature",
                     "assembly", "cell_setup"))
        self.assertAlmostEqual(parts, agg["total"]["mean_s"], places=6)


class ReplayIdentity(unittest.TestCase):
    def test_stored_identity_matches_current_certifying_implementation(self):
        import universe
        current = universe.implementation_hash()
        for r in load(REPS) + load(PREC):
            self.assertEqual(r["identity"]["implementation_hash"], current,
                             f"cell {r['cell_index']}: the committed evidence was "
                             "produced by a different certifying implementation")

    def test_identity_carries_the_full_frozen_resume_key(self):
        for r in load(REPS):
            ident = r["identity"]
            self.assertEqual(ident["checkpoint_hash"], spec.CHECKPOINT_SHA256)
            self.assertEqual(ident["cells_sha256"], spec.CELLS_SHA256)
            self.assertEqual(ident["obligation_universe_total"], 17978)
            self.assertEqual(ident["precision_bits"], 256)
            self.assertEqual(ident["e0"], r["e0"])
            self.assertEqual(ident["rho"], r["rho"])
            self.assertTrue(ident["unit_hash"])

    def test_stored_identity_is_admissible_for_resume(self):
        import universe
        for r in load(REPS):
            record = dict(r["identity"])
            self.assertTrue(universe.admit_resume_record(
                record, backend_hash=record["backend_hash"]))

    def test_certifying_modules_exclude_reporting_tooling(self):
        import universe
        for name in ("report.py", "bench.py", "audit_impl.py", "report_main.py"):
            self.assertNotIn(name, universe.CERTIFYING_MODULES)
        for name in ("cusum_layer2.py", "refine.py", "propagate.py", "ledger.py"):
            self.assertIn(name, universe.CERTIFYING_MODULES)


class FrozenGuardConflict(unittest.TestCase):
    """The frozen successor's freeze-time guard trips on any later commit."""

    def setUp(self):
        self.audit = json.loads((NS / "manifests/self_audit.json").read_text())
        self.conflict = self.audit["frozen_successor_guard_conflict"]

    def test_conflict_is_recorded_not_hidden(self):
        self.assertIn("frozen_successor_guard_conflict", self.audit)
        self.assertEqual(self.conflict["frozen_tests_failing"],
                         ["GovernanceTests::test_protected_tree",
                          "GovernanceTests::test_read_only_adjudication"])

    def test_frozen_namespace_really_is_untouched(self):
        self.assertTrue(self.conflict["frozen_tree_byte_identical_to_freeze_manifest"])
        self.assertTrue(self.conflict["start_head_git_object_manifest_unchanged"])
        self.assertFalse(self.conflict["is_a_frozen_namespace_mutation"])

    def test_only_this_namespace_is_objected_to(self):
        self.assertTrue(self.conflict["all_objected_paths_are_this_namespace"])

    def test_frozen_audit_source_was_not_edited(self):
        """The guard must not be relaxed to make itself pass."""
        import hashlib
        manifest = json.loads((SPEC_NS / "manifests/freeze.json").read_text())
        for rel in ("code/audit.py", "tests/test_successor.py"):
            got = hashlib.sha256((SPEC_NS / rel).read_bytes()).hexdigest()
            self.assertEqual(got, manifest["files"][rel], rel)


class ManifestEvidence(unittest.TestCase):
    def test_work_universe_manifest(self):
        m = json.loads((NS / "manifests/work_universe.json").read_text())
        self.assertEqual(m["total_units"], 17978)
        self.assertEqual(m["base_object_units"], 12198)
        self.assertEqual(m["detector_cell_counts"], {"CUSUM": 326, "SR": 316})
        self.assertFalse(m["production_enabled"])
        for w, s in m["shard_conservation"].items():
            self.assertTrue(s["union_equals_universe"], w)
            self.assertTrue(s["no_overlap"], w)
        self.assertIn(12255, m["old_universes_rejected"])

    def test_self_audit_verdict_is_not_production_ready(self):
        a = json.loads((NS / "manifests/self_audit.json").read_text())
        self.assertFalse(a["production_ready"])
        self.assertFalse(a["scientific_verdict_changed"])
        self.assertNotIn("READY_FOR_PRODUCTION", a["verdict"])
        self.assertEqual(a["checks_failed"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
