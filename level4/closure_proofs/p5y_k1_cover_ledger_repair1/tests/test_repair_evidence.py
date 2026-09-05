"""Tests over the committed repair evidence and the remaining unresolved state.

These assert that the repair did what it claims, changed nothing else, and did
not quietly resolve anything the adjudication left open.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import prior                                                    # noqa: E402

import spec                                                     # noqa: E402
import universe as reviewed_universe                            # noqa: E402

import repair_audit                                             # noqa: E402
import repair_qualify                                           # noqa: E402
import repair_universe as RU                                    # noqa: E402

REG = sorted((NS / "diagnostics/regression").glob("repaired_*.json"))
IMPL = prior.IMPL_NS


def load(paths):
    return [json.loads(p.read_text()) for p in paths]


class RepairEvidence(unittest.TestCase):
    def test_regression_records_exist(self):
        recs = load(REG)
        self.assertGreaterEqual(len(recs), 5)
        self.assertEqual(sorted({r["cell_index"] for r in recs}), [221, 293])

    def test_evidence_is_non_result_bearing(self):
        for r in load(REG):
            self.assertFalse(r["result_bearing"])
            self.assertFalse(r["production_run"])
            self.assertFalse(r["scientific_certification_of_full_cover"])

    def test_s0_charged_exactly_once_in_every_record(self):
        for r in load(REG):
            a = r["s0_charge_audit"]
            self.assertTrue(a["all_charged_exactly_once"], r["cell_index"])
            self.assertEqual(
                a["representation"],
                "A: residual against fixed candidate + separate epsS")
            for n in ("F_0", "dF_0", "H_0"):
                self.assertEqual(a[n]["charge_count"], 1, (r["cell_index"], n))
                self.assertEqual(F(a[n]["local_residual_charge"]), 0)
                self.assertGreater(F(a[n]["dependency_charge"]), 0)

    def test_certified_quantities_match_the_reviewed_run(self):
        """The duplicate is ~1e-53; the certificates must be unchanged."""
        for r in load(REG):
            if r.get("scope") == "m1_only":
                p = (IMPL / "diagnostics/precision_records"
                     / f"CUSUM_{r['cell_index']}_{r['precision_bits']}_m1.json")
            else:
                p = (IMPL / "diagnostics/representatives"
                     / f"CUSUM_{r['cell_index']}_{r['precision_bits']}.json")
            rev = json.loads(p.read_text())
            for m, L in r["m"].items():
                a = rev["m"][m]
                self.assertEqual(F(L["M_R2"]), F(a["M_R2"]))
                self.assertEqual(F(L["D_interval_mag"]), F(a["D_interval_mag"]))
                self.assertEqual(F(L["cover"]["usage"]), F(a["cover"]["usage"]))
                self.assertEqual(L["status"], a["status"])

    def test_no_double_counting_in_recorded_dags(self):
        for r in load(REG):
            for k in ("dag_audit_mid", "dag_audit_cell"):
                self.assertEqual(r[k]["duplicate_edges"], 0)
                self.assertEqual(r[k]["edges"], r[k]["distinct_edge_keys"])
                self.assertTrue(r[k]["derivative_edges_all_cover"])

    def test_frozen_kernel_correspondence_at_cell_221(self):
        """h_2:0 ~ 1.83e-06 and S_1:0 ~ 2.76e-06 at the e ~ 1/4 cell."""
        rec = next(r for r in load(REG)
                   if r["cell_index"] == 221 and r.get("scope") != "m1_only")
        h2 = float(F(rec["objects"]["h_2:0"]["delta_mid"]))
        s1 = float(F(rec["objects"]["S_1:0"]["delta_mid"]))
        self.assertAlmostEqual(h2, 1.83e-06, delta=0.02e-06)
        self.assertAlmostEqual(s1, 2.76e-06, delta=0.02e-06)

    def test_precision_diagnostic_still_passes(self):
        by_bits = {r["precision_bits"]: r for r in load(REG)
                   if r.get("scope") == "m1_only"}
        self.assertEqual(sorted(by_bits), [256, 384, 512])
        base = by_bits[256]["m"]["1"]
        for b in (384, 512):
            h = by_bits[b]["m"]["1"]
            self.assertEqual(F(h["M_R2"]), F(base["M_R2"]))
            self.assertEqual(F(h["cover"]["usage"]), F(base["cover"]["usage"]))
            self.assertGreaterEqual(F(h["R_interval"]["lo"]),
                                    F(base["R_interval"]["lo"]))
            self.assertLessEqual(F(h["R_interval"]["hi"]),
                                 F(base["R_interval"]["hi"]))
            self.assertEqual(base["status"], h["status"])

    def test_recorded_identities_are_admissible_only_as_themselves(self):
        for r in load(REG):
            for key, ident in r["identity"].items():
                unit = tuple(key.split("|"))
                unit = (unit[0], int(unit[1]), unit[2], unit[3])
                ctx = RU.context(backend_hash=ident["backend_hash"],
                                 impl_hash=ident["implementation_hash"],
                                 precision_bits=ident["precision_bits"])
                self.assertTrue(RU.admit_resume_record(ident, unit, **ctx))
                other = (unit[0], unit[1], unit[2],
                         "3" if unit[3] != "3" else "5")
                with self.assertRaises(RU.ResumeRejected):
                    RU.admit_resume_record(ident, other, **ctx)


class LeafObligationIdentity(unittest.TestCase):
    """A leaf has an EMPTY dependency set; that must still be bound exactly."""

    LEAF = ("CUSUM", 0, "object", "h_1")

    def test_leaf_admitted_and_empty_dependency_set_is_correct(self):
        ctx = RU.context(backend_hash="B")
        rec = RU.canonical_identity(self.LEAF, **ctx)
        self.assertEqual(rec["source_certificate_hashes"], {})
        self.assertTrue(RU.admit_resume_record(rec, self.LEAF, **ctx))

    def test_forged_leaf_dependency_is_rejected(self):
        ctx = RU.context(backend_hash="B")
        rec = copy.deepcopy(RU.canonical_identity(self.LEAF, **ctx))
        rec["source_certificate_hashes"] = {"CUSUM|0|object|S_0": "0" * 64}
        with self.assertRaises(RU.ResumeRejected):
            RU.admit_resume_record(rec, self.LEAF, **ctx)

    def test_leaf_is_not_admissible_as_a_unit_with_dependencies(self):
        ctx = RU.context(backend_hash="B")
        rec = RU.canonical_identity(self.LEAF, **ctx)
        with self.assertRaises(RU.ResumeRejected):
            RU.admit_resume_record(rec, ("CUSUM", 0, "object", "dF_2"), **ctx)


class NothingElseResolved(unittest.TestCase):
    """The repair must not quietly close anything the adjudication left open."""

    def test_cell_325_still_unresolved(self):
        rec = json.loads((IMPL / "diagnostics/representatives"
                          / "CUSUM_325_256.json").read_text())
        failing = sorted(m for m, L in rec["m"].items() if L["status"] == "FAIL")
        self.assertEqual(failing, ["2", "3", "5"])
        self.assertIn(325, repair_qualify.FORBIDDEN_CELLS)
        with self.assertRaises(SystemExit):
            repair_qualify.run_cell(325)
        self.assertEqual([p for p in REG if "325" in p.name], [])

    def test_sr_still_unimplemented(self):
        import qualify
        sr = qualify.run_cell("SR", 0)
        self.assertEqual(sr["status"], "NOT_IMPLEMENTED")
        self.assertNotIn("PASS", json.dumps(sr))

    def test_far_field_still_unimplemented(self):
        status = (IMPL / "IMPLEMENTATION_STATUS.md").read_text()
        self.assertIn("far-field certificates", status)
        self.assertIn("NOT_IMPLEMENTED", status)

    def test_cost_cap_still_not_established(self):
        cost = json.loads((IMPL / "benchmarks/cost_model.json").read_text())
        self.assertEqual(cost["projection"]["frozen_hard_cap_cpu_h"], 1126)
        self.assertFalse(cost["projection"]["cap_increased"])
        self.assertIn(cost["projection"]["COST_CAP_STATUS"],
                      ("FAIL_BUDGET", "NOT_ESTABLISHED"))

    def test_audit_reports_the_remaining_unresolved_items(self):
        a = json.loads((NS / "manifests/repair_self_audit.json").read_text())
        for item in ("SR raw DAG absent", "SR M_R2 absent", "SR all-m absent",
                     "far-field not implemented",
                     "cell 325 CURRENT_CERTIFICATE_FAILURE_ONLY",
                     "full cost cap NOT_ESTABLISHED"):
            self.assertIn(item, a["remaining_unresolved"])
        self.assertFalse(a["production_ready"])
        self.assertFalse(a["implementation_complete"])
        self.assertEqual(a["cost_cap_status"], "NOT_ESTABLISHED")
        self.assertFalse(a["scientific_verdict_changed"])


class ProtectedTrees(unittest.TestCase):
    def test_frozen_successor_untouched(self):
        self.assertTrue(repair_audit.frozen_tree_unchanged())

    def test_reviewed_implementation_byte_identical_to_c0a1f40(self):
        r = repair_audit.reviewed_namespace_preserved()
        self.assertEqual(r["paths_changed"], [])
        self.assertEqual(r["reviewed_commit"], prior.REVIEWED_COMMIT)

    def test_repair_writes_only_inside_its_own_namespace(self):
        changed = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=prior.ROOT).decode().splitlines()
        rel = str(NS.relative_to(prior.ROOT))
        stray = [line for line in changed if rel not in line]
        self.assertEqual(stray, [], f"writes outside {rel}: {stray}")

    def test_frozen_invariants_unchanged(self):
        self.assertEqual(spec.HARD_CAP_CPU_H, 1126)
        self.assertEqual(spec.PRODUCTION_BITS, 256)
        self.assertFalse(spec.PRODUCTION_ENABLED)
        self.assertEqual(len(reviewed_universe.work_ids()), 17978)


if __name__ == "__main__":
    unittest.main(verbosity=2)
