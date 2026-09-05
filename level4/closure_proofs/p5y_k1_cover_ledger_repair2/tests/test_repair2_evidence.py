"""Tests over the committed Repair2 evidence.

They assert that the evidence really is bound to the code that produced it,
that the chain replays, and that nothing the adjudication left open was quietly
closed.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import prior2                                                   # noqa: E402

import spec                                                     # noqa: E402
import universe as reviewed                                     # noqa: E402

import certhash                                                 # noqa: E402
import producer                                                 # noqa: E402
import provenance                                               # noqa: E402
import repair2_audit                                            # noqa: E402
import repair2_qualify                                          # noqa: E402
import repair2_universe as RU2                                  # noqa: E402

REG = sorted((NS / "diagnostics/regression").glob("repair2_*.json"))
REPAIR1_REG = (prior2.REPAIR1_NS / "diagnostics/regression")


def load(paths):
    return [json.loads(p.read_text()) for p in paths]


class EvidenceIsBoundToItsProducer(unittest.TestCase):
    def test_records_exist(self):
        self.assertGreaterEqual(len(REG), 2)

    def test_stamped_producer_hash_is_the_current_one(self):
        """Catches evidence that has gone stale against its certifying code."""
        current = producer.producer_hash()
        for r in load(REG):
            self.assertEqual(r["producer"]["implementation_hash"], current,
                             f"cell {r['cell_index']}: evidence was produced by "
                             "a different certifying implementation")

    def test_stamped_hash_is_not_the_reviewed_parent(self):
        for r in load(REG):
            self.assertNotEqual(r["producer"]["implementation_hash"],
                                producer.parent_hash())
            self.assertTrue(r["producer"]["distinct_from_parent"])

    def test_manifest_is_recorded_and_covers_repair1(self):
        m = json.loads((NS / "manifests/producer_manifest.json").read_text())
        self.assertEqual(m["producer_hash"], producer.producer_hash())
        self.assertEqual(m["identity_kind"], RU2.IDENTITY_KIND)
        files = m["manifest"]["files"]
        for name in producer.REPAIR1_MODULES:
            rel = str((prior2.REPAIR1_NS / "code" / name)
                      .relative_to(prior2.ROOT))
            self.assertIn(rel, files, name)
        self.assertEqual(m["manifest"], producer.producer_manifest())

    def test_every_certificate_identity_carries_the_repair2_kind(self):
        for r in load(REG):
            for cert in r.get("certificates", {}).values():
                self.assertEqual(cert["identity"]["implementation_hash_kind"],
                                 RU2.IDENTITY_KIND)


class EvidenceChainReplays(unittest.TestCase):
    def test_full_cell_chain_replays_from_the_committed_record(self):
        for r in load(REG):
            if not r.get("certificates"):
                continue
            ctx = RU2.context(precision_bits=r["precision_bits"])
            v = provenance.verify_cell(r, **ctx)
            self.assertTrue(v["all_verified"])
            self.assertEqual(v["obligations"], 28)
            self.assertTrue(v["leaf_maps_empty"])

    def test_committed_certificate_hashes_match_a_fresh_rebuild(self):
        for r in load(REG):
            if not r.get("certificates"):
                continue
            ctx = RU2.context(precision_bits=r["precision_bits"])
            rebuilt = provenance.build_cell_certificates(r, **ctx)
            for uid, stored in r["certificates"].items():
                self.assertEqual(
                    stored["certificate_hash"],
                    certhash.certificate_hash(rebuilt[uid]), uid)

    def test_leaf_and_non_leaf_shapes(self):
        for r in load(REG):
            if not r.get("certificates"):
                continue
            leaves = set(r["provenance_chain"]["leaf_units"])
            self.assertTrue(leaves)
            for uid, cert in r["certificates"].items():
                m = cert["identity"]["source_certificate_hashes"]
                if uid in leaves:
                    self.assertEqual(m, {}, uid)
                else:
                    self.assertTrue(m, uid)

    def test_m1_scoped_run_issues_no_certificate(self):
        m1 = [r for r in load(REG) if r.get("scope") == "m1_only"]
        self.assertTrue(m1)
        for r in m1:
            self.assertEqual(r["certificates"], {})
            self.assertEqual(r["provenance_chain"]["status"], "NOT_A_CERTIFICATE")
            self.assertFalse(r["provenance_chain"]["all_verified"])

    def test_incomplete_evidence_cannot_be_certified(self):
        r = next(x for x in load(REG) if x.get("scope") == "m1_only")
        ctx = RU2.context(precision_bits=r["precision_bits"])
        with self.assertRaises(certhash.IncompleteEvidence):
            provenance.build_cell_certificates(r, **ctx)


class ScientificRegression(unittest.TestCase):
    """Repair2 changes no certified value."""

    def test_certified_values_match_repair1(self):
        r2 = next(x for x in load(REG) if x.get("certificates"))
        p = REPAIR1_REG / f"repaired_{r2['cell_index']}_{r2['precision_bits']}_full.json"
        r1 = json.loads(p.read_text())
        for m, L in r2["m"].items():
            a = r1["m"][m]
            self.assertEqual(F(L["M_R2"]), F(a["M_R2"]), m)
            self.assertEqual(F(L["D_interval_mag"]), F(a["D_interval_mag"]), m)
            self.assertEqual(F(L["cover"]["usage"]), F(a["cover"]["usage"]), m)
            self.assertEqual(L["R_interval"], a["R_interval"], m)
            self.assertEqual(L["status"], a["status"], m)

    def test_s0_still_charged_exactly_once(self):
        for r in load(REG):
            a = r["s0_charge_audit"]
            self.assertTrue(a["all_charged_exactly_once"])
            self.assertEqual(
                a["representation"],
                "A: residual against fixed candidate + separate epsS")

    def test_frozen_kernel_correspondence_retained(self):
        r = next(x for x in load(REG) if x.get("certificates"))
        self.assertAlmostEqual(float(F(r["objects"]["h_2:0"]["delta_mid"])),
                               1.83e-06, delta=0.02e-06)
        self.assertAlmostEqual(float(F(r["objects"]["S_1:0"]["delta_mid"])),
                               2.76e-06, delta=0.02e-06)

    def test_no_double_counting_in_recorded_dags(self):
        for r in load(REG):
            for k in ("dag_audit_mid", "dag_audit_cell"):
                self.assertEqual(r[k]["duplicate_edges"], 0)
                self.assertTrue(r[k]["derivative_edges_all_cover"])


class NothingElseResolved(unittest.TestCase):
    def test_cell_325_still_unresolved(self):
        c = repair2_audit.cell_325_unresolved()
        self.assertTrue(c["reviewed_failures_preserved"])
        self.assertTrue(c["repair2_refuses_325"])
        with self.assertRaises(SystemExit):
            repair2_qualify.run_cell(325)
        self.assertEqual([p for p in REG if "325" in p.name], [])

    def test_sr_and_far_field_absent(self):
        s = repair2_audit.sr_and_far_field_absent()
        self.assertTrue(s["sr_reports_not_implemented"])
        self.assertTrue(s["sr_never_reports_pass"])
        self.assertTrue(s["far_field_declared_not_implemented"])

    def test_cost_cap_still_not_established(self):
        cost = json.loads((prior2.IMPL_NS / "benchmarks/cost_model.json").read_text())
        self.assertEqual(cost["projection"]["frozen_hard_cap_cpu_h"], 1126)
        self.assertFalse(cost["projection"]["cap_increased"])
        self.assertIn(cost["projection"]["COST_CAP_STATUS"],
                      ("FAIL_BUDGET", "NOT_ESTABLISHED"))

    def test_audit_does_not_claim_work_universe_pass(self):
        a = json.loads((NS / "manifests/repair2_self_audit.json").read_text())
        self.assertEqual(a["work_universe_verdict"],
                         "RESERVED_FOR_INDEPENDENT_ADJUDICATION")
        self.assertFalse(a["production_ready"])
        self.assertFalse(a["implementation_complete"])
        self.assertEqual(a["cost_cap_status"], "NOT_ESTABLISHED")
        self.assertFalse(a["scientific_verdict_changed"])
        for item in ("SR raw DAG absent", "far-field not implemented",
                     "cell 325 CURRENT_CERTIFICATE_FAILURE_ONLY",
                     "full cost cap NOT_ESTABLISHED"):
            self.assertIn(item, a["remaining_unresolved"])


class ProtectedTrees(unittest.TestCase):
    def test_frozen_successor_byte_preserved(self):
        self.assertTrue(repair2_audit.frozen_tree_unchanged())

    def test_reviewed_and_repair1_byte_preserved(self):
        for ns, commit in ((prior2.IMPL_NS, prior2.REVIEWED_COMMIT),
                           (prior2.REPAIR1_NS, prior2.REPAIR1_COMMIT)):
            r = repair2_audit.namespace_preserved(ns, commit)
            self.assertEqual(r["paths_changed"], [], r["namespace"])

    def test_repair2_writes_only_inside_its_own_namespace(self):
        changed = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=prior2.ROOT).decode().splitlines()
        rel = str(NS.relative_to(prior2.ROOT))
        stray = [line for line in changed if rel not in line]
        self.assertEqual(stray, [], f"writes outside {rel}: {stray}")

    def test_frozen_invariants_unchanged(self):
        self.assertEqual(spec.HARD_CAP_CPU_H, 1126)
        self.assertEqual(spec.PRODUCTION_BITS, 256)
        self.assertFalse(spec.PRODUCTION_ENABLED)
        self.assertEqual(len(reviewed.work_ids()), 17978)
        self.assertEqual(spec.verify_frozen_spec(), spec.FROZEN_HASHES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
