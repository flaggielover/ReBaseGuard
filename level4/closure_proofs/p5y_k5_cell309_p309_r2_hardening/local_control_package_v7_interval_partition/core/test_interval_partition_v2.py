"""Generation-binding regressions; supplied data only, no host or trace IO."""
import copy
import unittest
from interval_partition import partition_interval


def exact_evidence(mapping):
    # Only these synthetic test rows use exact Start and real End.
    return {key: {i: dict(start_kind="START", start_anchor=row[0],
                         end_kind="END", end_anchor=row[1])
                  for i, row in enumerate(rows)} for key, rows in mapping.items()}


class BindingTests(unittest.TestCase):
    def part(self, threads, processes, interval=(0, 20), window=(0, 20), tid=7,
             thread_evidence=None, process_evidence=None):
        r = partition_interval(tid, interval, threads, processes, window,
                               thread_evidence=exact_evidence(threads) if thread_evidence is None else thread_evidence,
                               process_evidence=exact_evidence(processes) if process_evidence is None else process_evidence)
        self.assertEqual(r["known_ticks"]+r["unknown_ticks"], r["clipped_ticks"])
        self.assertEqual(r["clipped_ticks"]+r["outside_window_ticks"], interval[1]-interval[0])
        self.assertEqual(sum(s["ticks"] for s in r["slices"]), r["clipped_ticks"])
        self.assertEqual([s["end"] for s in r["slices"][:-1]], [s["start"] for s in r["slices"]][1:])
        for s in r["slices"]:
            self.assertGreater(s["ticks"], 0)
            self.assertEqual(r["boundaries"][s["start_boundary"]]["qpc"], s["start"])
            self.assertEqual(r["boundaries"][s["end_boundary"]]["qpc"], s["end"])
            if s["state"] == "KNOWN":
                self.assertEqual(s["identity"]["thread_ordinal"], r["bound_thread"]["ordinal"])
                self.assertEqual(s["identity"]["process_key"], r["bound_process"]["identity"])
        self.assertFalse(r["coverage_complete"])
        self.assertEqual(r["admission"], "BLOCKED")
        return r

    def test_cross_end_recovers_prefix_only(self):
        r = self.part({7: [(0, 8, 20, False)]}, {20: [(0, 30, 99, False)]})
        self.assertEqual((r["known_ticks"], r["unknown_ticks"]), (8, 12))

    def test_original_cswitch_cannot_migrate_to_new_tid_generation(self):
        t = {7: [(0, 10, 20, False), (10, 20, 21, False)]}
        p = {20: [(0, 10, 90, False)], 21: [(10, 20, 91, False)]}
        r = self.part(t, p)
        self.assertEqual([(s["state"], s["identity"]["pid"] if s["identity"] else None)
                          for s in r["slices"]], [("KNOWN", 20), ("UNKNOWN", None)])
        self.assertEqual(self.part(t, p, window=(12, 18))["known_ticks"], 0)

    def test_pid_reuse_cannot_reparent_existing_thread(self):
        t = {7: [(0, 20, 20, False)]}
        p = {20: [(0, 8, 90, False), (12, 20, 91, False)]}
        for window in ((0, 20), (12, 18)):
            r = self.part(t, p, window=window)
            self.assertEqual(r["known_ticks"], 0)
            self.assertEqual(r["binding_error"], "FULL_THREAD_NOT_WITHIN_BOUND_PROCESS")

    def test_process_birth_after_thread_birth_is_not_repaired_by_clipping(self):
        r = self.part({7: [(0, 8, 20, False)]}, {20: [(4, 30, 99, False)]}, window=(5, 7))
        self.assertEqual(r["known_ticks"], 0)
        self.assertEqual(r["binding_error"], "THREAD_ANCHOR_PROCESS_MISSING_OR_AMBIGUOUS")

    def test_later_thread_start_cannot_claim_original_span(self):
        r = self.part({7: [(5, 20, 20, False)]}, {20: [(0, 30, 90, False)]}, window=(6, 18))
        self.assertEqual(r["known_ticks"], 0)

    def test_same_qpc_original_thread_boundary_is_ambiguous(self):
        r = self.part({7: [(0, 10, 20, False), (10, 20, 21, False)]},
                      {20: [(0, 10, 90, False)], 21: [(10, 30, 91, False)]},
                      interval=(10, 20))
        self.assertEqual(r["known_ticks"], 0)
        self.assertEqual(len(r["original_thread_candidates"]), 2)

    def test_same_qpc_process_boundary_is_ambiguous(self):
        r = self.part({7: [(10, 20, 20, False)]},
                      {20: [(0, 10, 90, False), (10, 30, 91, False)]}, interval=(12, 18))
        self.assertEqual(r["known_ticks"], 0)
        self.assertEqual(r["binding_error"], "THREAD_ANCHOR_PROCESS_MISSING_OR_AMBIGUOUS")

    def test_real_later_cswitch_can_bind_new_generations(self):
        r = self.part({7: [(0, 8, 20, False), (12, 20, 20, False)]},
                      {20: [(0, 8, 90, False), (12, 30, 91, False)]}, interval=(13, 19))
        self.assertEqual(r["known_ticks"], 6)
        self.assertEqual(r["bound_process"]["identity"], 91)

    def test_missing_rundown_anchor_and_synthetic_end_are_unknown(self):
        t, p = {7: [(0, 20, 20, True)]}, {20: [(0, 30, 90, False)]}
        self.assertEqual(self.part(t, p, thread_evidence={})["known_ticks"], 0)
        evidence = {7: {0: dict(start_kind="RUNDOWN", start_anchor=5,
                               end_kind="SYNTHETIC_HIGH", end_anchor=20)}}
        self.assertEqual(self.part(t, p, thread_evidence=evidence)["binding_error"],
                         "SYNTHETIC_END_NOT_OWNERSHIP_EVIDENCE")
        r = partition_interval(7, (0, 20), t, p, (0, 20))
        self.assertEqual(r["known_ticks"], 0)

    def test_actual_rundown_proves_only_after_its_existence_anchor(self):
        t, p = {7: [(0, 20, 20, True)]}, {20: [(0, 30, 90, True)]}
        te = {7: {0: dict(start_kind="RUNDOWN", start_anchor=5, end_kind="END", end_anchor=20)}}
        # v4 row end=traceHigh=30; actual DCEnd=25 only proves existence to 25.
        pe = {20: {0: dict(start_kind="RUNDOWN", start_anchor=2, end_kind="RUNDOWN", end_anchor=25)}}
        self.assertEqual(self.part(t, p, interval=(6, 18), thread_evidence=te, process_evidence=pe)["known_ticks"], 12)
        self.assertEqual(self.part(t, p, interval=(3, 18), window=(10, 18),
                                   thread_evidence=te, process_evidence=pe)["known_ticks"], 0)
        pe[20][0]["end_anchor"] = 15
        self.assertEqual(self.part(t, p, interval=(6, 18), thread_evidence=te,
                                   process_evidence=pe)["known_ticks"], 0)

    def test_overlaps_remain_unknown_without_migrating(self):
        r = self.part({7: [(0, 14, 20, False), (6, 20, 21, False)]},
                      {20: [(0, 30, 90, False)], 21: [(0, 30, 91, False)]})
        self.assertEqual((r["known_ticks"], r["unknown_ticks"]), (6, 14))
        r = self.part({7: [(0, 20, 20, False)]}, {20: [(0, 30, 90, False), (6, 14, 90, False)]})
        self.assertEqual(r["unknown_ticks"], 8)
        r = self.part({7: [(0, 20, 20, False)]*2}, {20: [(0, 30, 90, False)]})
        self.assertEqual(r["known_ticks"], 0)

    def test_clipping_zero_duration_large_qpc_and_no_mutation(self):
        offset = 2**60
        t = {7: [(offset, offset+20, 20, False), (offset+10, offset+10, 21, False)]}
        p = {20: [(offset, offset+30, 90, False)], 21: [(offset, offset+30, 91, False)]}
        old = copy.deepcopy((t, p))
        r = self.part(t, p, (offset, offset+20), (offset+3, offset+17))
        self.assertEqual((r["known_ticks"], r["outside_window_ticks"]), (14, 6))
        self.assertEqual((t, p), old)
        self.assertEqual(self.part({}, {}, (4, 4))["slices"], [])
        self.assertEqual(self.part({}, {}, window=(20, 30))["slices"], [])

    def test_pid_zero_and_tid_zero_never_exempted(self):
        for tid, pid in ((0, 20), (7, 0)):
            r = self.part({tid: [(0, 20, pid, False)]}, {pid: [(0, 30, 90, False)]}, tid=tid)
            self.assertEqual(r["known_ticks"], 0)

    def test_malformed_geometry_is_rejected(self):
        for row in ((9, 2, 20, False), (0, 20, 20, 1), (0.0, 20, 20, False), (0, 20, True, False)):
            with self.subTest(row=row), self.assertRaises(ValueError):
                partition_interval(7, (0, 20), {7: [row]}, {}, (0, 20))


if __name__ == "__main__":
    unittest.main()
