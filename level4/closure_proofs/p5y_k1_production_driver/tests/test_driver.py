"""Focused pre-T2S tests for the K1 production driver. No production run."""
from __future__ import annotations

import json, pathlib, sys, tempfile, unittest

NS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NS))
from k1prod import driver as DR, kernel as K, qualify as Q, schema as S   # noqa: E402

CK = S.load_checkpoint()
UNITS = S.enumerate_units(CK)


class TestWorkConservation(unittest.TestCase):
    def test_total_matches_checkpoint(self):
        self.assertEqual(len(UNITS), CK["work_conservation"]["total_units"])
        self.assertEqual(len(UNITS), 12255)

    def test_exact_conservation_at_every_worker_count(self):
        for w in (1, 8, 16, 32, 64):
            r = S.verify_conservation(len(UNITS), w)
            self.assertTrue(r["exact"], w)
            self.assertTrue(r["no_duplicates"], w)
            self.assertTrue(r["no_missing"], w)
            self.assertTrue(r["first"] and r["last"], w)

    def test_no_duplicate_work_ids(self):
        ids = [S.unit_id(*u) for u in UNITS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_missing_unit_is_detected(self):
        n = len(UNITS)
        bad = [(0, n // 2), (n // 2 + 1, n)]          # deliberately drops one
        covered = [i for lo, hi in bad for i in range(lo, hi)]
        self.assertNotEqual(set(covered), set(range(n)))

    def test_duplicate_unit_is_detected(self):
        n = len(UNITS)
        bad = [(0, n // 2 + 1), (n // 2, n)]          # deliberately overlaps
        covered = [i for lo, hi in bad for i in range(lo, hi)]
        self.assertNotEqual(len(covered), len(set(covered)))

    def test_ceil_per_shard_would_overexecute(self):
        import math
        n = len(UNITS)
        for w in (7, 16, 997):
            self.assertGreater(w * math.ceil(n / w), n)

    def test_cusum_block_precedes_sr(self):
        first_sr = next(i for i, u in enumerate(UNITS) if u[0] == "SR")
        self.assertTrue(all(u[0] == "CUSUM" for u in UNITS[:first_sr]))
        self.assertEqual(first_sr, 323 * 19)


class TestRecordIntegrity(unittest.TestCase):
    def _run(self, d):
        return DR.Run(pathlib.Path(d), 0, 64)

    def test_corrupt_partial_line_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "c.jsonl"
            rec = S.new_record("SR", 0, "F_0", ck_hash="x", be_hash="y")
            S.atomic_append(p, rec)
            p.write_text(p.read_text() + '{"schema": "rebaseguard.p5y.k1.cel\n')
            good, bad = S.read_records(p)
            self.assertEqual(len(good), 1)
            self.assertEqual(bad, 1)

    def test_wrong_schema_line_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "c.jsonl"
            p.write_text(json.dumps({"schema": "other", "work_id": "z"}) + "\n")
            good, bad = S.read_records(p)
            self.assertEqual((len(good), bad), (0, 1))

    def test_checkpoint_hash_mismatch_is_not_resumed(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._run(d)
            rec = S.new_record("SR", 0, "F_0", ck_hash="WRONG", be_hash=r.be_hash)
            rec["status"] = "COMPLETE"
            S.atomic_append(r.records, rec)
            done, info = r.resume()
            self.assertEqual(done, set())
            self.assertEqual(info["hash_mismatched_rejected"], 1)

    def test_backend_hash_mismatch_is_not_resumed(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._run(d)
            rec = S.new_record("SR", 0, "F_0", ck_hash=r.ck_hash, be_hash="WRONG")
            rec["status"] = "COMPLETE"
            S.atomic_append(r.records, rec)
            done, info = r.resume()
            self.assertEqual(done, set())
            self.assertEqual(info["hash_mismatched_rejected"], 1)

    def test_atomic_resume_skips_completed_units(self):
        with tempfile.TemporaryDirectory() as d:
            r = self._run(d)
            wid = S.unit_id("CUSUM", 0, "h_1")
            rec = S.new_record("CUSUM", 0, "h_1", ck_hash=r.ck_hash, be_hash=r.be_hash)
            rec["status"] = "COMPLETE"
            S.atomic_append(r.records, rec)
            done, info = r.resume()
            self.assertIn(wid, done)
            self.assertEqual(info["resumable_complete"], 1)

    def test_record_carries_R_and_Rprime_fields(self):
        rec = S.new_record("SR", 0, "F_0", ck_hash="a", be_hash="b")
        for f in ("R_enclosure", "R_prime_enclosure", "contributing_object_ids",
                  "endpoint_sliver_contribution", "budget_usage_by_component",
                  "P1_E_d", "P1_headroom_rel", "e_interval", "detector",
                  "m_relevance", "certificate_status", "failure_class",
                  "cpu_seconds", "checkpoint_hash", "backend_hash", "work_id"):
            self.assertIn(f, rec, f)


class TestPhasesAndGovernance(unittest.TestCase):
    def test_phase_a_passes_and_gates(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(DR.Run(pathlib.Path(d), 0, 64).phase_a()["PASS"])

    def test_shards_above_worker_ceiling_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a = DR.Run(pathlib.Path(d), 0, 65).phase_a()
            self.assertFalse(a["PASS"])
            self.assertFalse(a["checks"]["shards_within_worker_ceiling"])

    def test_producer_cannot_self_award_K1_CLOSED(self):
        with tempfile.TemporaryDirectory() as d:
            f = DR.Run(pathlib.Path(d), 0, 1).phase_f()
            self.assertFalse(f["producer_may_self_award"])
            self.assertFalse(f["K1_CLOSED_awardable_here"])
            self.assertFalse(f["coverage_complete"])

    def test_phase_d_refuses_incomplete_object_sets(self):
        with tempfile.TemporaryDirectory() as d:
            r = DR.Run(pathlib.Path(d), 0, 1)
            rec = S.new_record("SR", 0, "F_0", ck_hash=r.ck_hash, be_hash=r.be_hash)
            rec["status"] = "COMPLETE"
            S.atomic_append(r.records, rec)
            dd = r.phase_d()
            self.assertEqual(dd["cells_incomplete"], 1)
            self.assertFalse(dd["PASS"])

    def test_cpu_cap_stops_before_violation(self):
        with tempfile.TemporaryDirectory() as d:
            r = DR.Run(pathlib.Path(d), 0, 1)
            out = r.run_units("CUSUM", "B", set(), cpu_budget_s=0.0)
            self.assertEqual(out["stopped"], "CPU_CAP")
            self.assertEqual(sum(out["counts"].values()), 0)

    def test_cap_is_the_frozen_one(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(DR.Run(pathlib.Path(d), 0, 1).cap_cpu_h,
                             CK["cpu_governance"]["SUCCESSOR_K1_HARD_CAP"])
            self.assertEqual(DR.Run(pathlib.Path(d), 0, 1).cap_cpu_h, 1126)

    def test_dry_run_creates_no_certified_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            r = DR.Run(pathlib.Path(d), 0, 64, dry_run=True)
            out = r.go(["A", "B"])
            recs, _ = S.read_records(r.records)
            self.assertTrue(all(x["status"] in ("NOT_RUN", "NOT_IMPLEMENTED")
                                for x in recs))
            self.assertEqual(out["P5Y_K1_SUCCESSOR_VERDICT"], "NOT_RUN")


class TestKernelGapIsExplicit(unittest.TestCase):
    def test_gap_is_reported_not_hidden(self):
        """CUSUM is now fully implemented; SR remains partial (F_0 only)."""
        f = K.implemented_fraction(UNITS)
        self.assertLess(f["fraction"], 1.0)
        cusum = {c for c in f["implemented_classes"] if c.startswith("CUSUM/")}
        sr = {c for c in f["implemented_classes"] if c.startswith("SR/")}
        self.assertEqual(len(cusum), 19)
        self.assertEqual(sr, {"SR/F_0"})

    def test_unimplemented_unit_is_NOT_IMPLEMENTED_not_FAILED(self):
        # probe an object that is genuinely still unimplemented: SR/h_1
        rec = S.new_record("SR", 0, "h_1", ck_hash="a", be_hash="b")
        out = K.run_unit("SR", 0, "h_1", rec, dry_run=True)
        self.assertEqual(out["status"], "NOT_IMPLEMENTED")
        self.assertEqual(out["failure_class"], "KERNEL_NOT_IMPLEMENTED")

    def test_not_implemented_never_counts_as_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            r = DR.Run(pathlib.Path(d), 0, 64)
            # shard 0 of 64 is entirely CUSUM, which is now implemented, so it
            # dry-runs to NOT_RUN; the SR gap is checked on an SR shard.
            r.go(["A", "B", "C", "F"])
            f = r.phase_f()
            self.assertEqual(f["complete"], 0)
            self.assertFalse(f["coverage_complete"])
            r2 = DR.Run(pathlib.Path(d) / "sr", 63, 64)
            r2.go(["A", "C", "F"])
            self.assertGreater(r2.phase_f()["not_implemented"], 0)


class TestQualificationIsNonResultBearing(unittest.TestCase):
    def test_qualification_creates_no_production_evidence(self):
        q = Q.qualify(workers=2)
        self.assertFalse(q["result_bearing"])
        self.assertFalse(q["creates_K1_evidence"])
        self.assertIsNone(q["K1_verdict_produced"])
        self.assertIn("ENVIRONMENT_QUALIFICATION", q)

    def test_qualification_does_not_touch_cover_cells(self):
        import ast
        src = (NS / "k1prod/qualify.py").read_text()
        tree = ast.parse(src)
        called = {n.func.id for n in ast.walk(tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertNotIn("run_unit", called)
        self.assertNotIn("certify", called)


if __name__ == "__main__":
    unittest.main(verbosity=2)
