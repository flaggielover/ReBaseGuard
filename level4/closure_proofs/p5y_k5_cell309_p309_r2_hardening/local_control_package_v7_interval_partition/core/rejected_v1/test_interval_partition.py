"""Small supplied-data regressions; no saved trace or host observation."""
import copy
import unittest
from interval_partition import partition_interval


class PartitionTests(unittest.TestCase):
    def partition(self, threads, processes, interval=(0, 20), window=(0, 20), tid=7):
        result = partition_interval(tid, interval, threads, processes, window)
        slices = result["slices"]
        self.assertEqual(sum(s["ticks"] for s in slices), result["clipped_ticks"])
        self.assertEqual(result["known_ticks"]+result["unknown_ticks"], result["clipped_ticks"])
        self.assertEqual(result["clipped_ticks"]+result["outside_window_ticks"], interval[1]-interval[0])
        self.assertEqual([s["end"] for s in slices[:-1]], [s["start"] for s in slices[1:]])
        for piece in slices:
            self.assertGreater(piece["ticks"], 0)
            self.assertEqual(result["boundaries"][piece["start_boundary"]]["qpc"], piece["start"])
            self.assertEqual(result["boundaries"][piece["end_boundary"]]["qpc"], piece["end"])
        self.assertFalse(result["coverage_complete"])
        self.assertEqual(result["admission"], "BLOCKED")
        return result

    def test_cross_end_preserves_known_prefix_without_extending_end(self):
        r = self.partition({7: [(0, 8, 20, False)]}, {20: [(0, 30, 99, True)]})
        self.assertEqual([(s["start"], s["end"], s["state"]) for s in r["slices"]],
                         [(0, 8, "KNOWN"), (8, 20, "UNKNOWN")])
        self.assertEqual(r["known_ticks"], 8)
        self.assertEqual(r["slices"][0]["identity"]["process_key"], 99)

    def test_prefix_requires_process_coverage_too(self):
        r = self.partition({7: [(0, 8, 20, False)]}, {20: [(4, 6, 99, False)]})
        self.assertEqual(r["known_ticks"], 2)
        self.assertEqual([(s["start"], s["end"]) for s in r["slices"]],
                         [(0, 4), (4, 6), (6, 8), (8, 20)])

    def test_tid_reuse_at_same_qpc_keeps_distinct_generations(self):
        r = self.partition({7: [(0, 10, 20, False), (10, 20, 21, False)]},
                           {20: [(0, 10, 90, False)], 21: [(10, 20, 91, False)]})
        self.assertEqual([s["identity"]["pid"] for s in r["slices"]], [20, 21])
        boundary = next(b for b in r["boundaries"] if b["qpc"] == 10)
        self.assertEqual(len(boundary["evidence"]), 4)
        self.assertIn("NO_EVENT_ORDER_INFERRED", r["same_qpc_policy"])

    def test_pid_reuse_has_distinct_process_keys_and_gap(self):
        r = self.partition({7: [(0, 20, 20, True)]},
                           {20: [(0, 8, 90, False), (12, 20, 91, False)]})
        self.assertEqual([s["identity"]["process_key"] if s["identity"] else None
                          for s in r["slices"]], [90, None, 91])
        self.assertEqual(r["unknown_ticks"], 4)

    def test_duplicate_or_overlapping_threads_are_not_collapsed(self):
        for generations in ([(0, 20, 20, False)]*2,
                            [(0, 14, 20, False), (6, 20, 21, False)]):
            with self.subTest(generations=generations):
                r = self.partition({7: generations},
                                   {20: [(0, 20, 90, False)], 21: [(0, 20, 91, False)]})
                ambiguous = [s for s in r["slices"] if len(s["thread_candidates"]) > 1]
                self.assertTrue(ambiguous)
                self.assertTrue(all(s["reason"] == "AMBIGUOUS_THREAD_GENERATION" for s in ambiguous))

    def test_overlapping_process_generations_are_ambiguous_even_same_key(self):
        r = self.partition({7: [(0, 20, 20, False)]},
                           {20: [(0, 14, 90, False), (6, 20, 90, False)]})
        self.assertEqual(r["unknown_ticks"], 8)
        self.assertEqual(r["slices"][1]["reason"], "AMBIGUOUS_PROCESS_GENERATION")

    def test_window_clipping_empty_contact_and_zero_duration(self):
        t, p = {7: [(0, 20, 20, False)]}, {20: [(0, 20, 90, False)]}
        r = self.partition(t, p, window=(3, 17))
        self.assertEqual((r["known_ticks"], r["outside_window_ticks"]), (14, 6))
        for interval, window in (((0, 20), (20, 30)), ((4, 4), (0, 20)), ((0, 20), (9, 9))):
            with self.subTest(interval=interval, window=window):
                self.assertEqual(self.partition(t, p, interval, window)["slices"], [])

    def test_zero_duration_generation_is_boundary_only(self):
        r = self.partition({7: [(0, 20, 20, True), (10, 10, 21, False)]},
                           {20: [(0, 20, 90, True)], 21: [(0, 20, 91, False)]})
        self.assertEqual(r["known_ticks"], 20)
        self.assertEqual(len(r["slices"]), 2)
        self.assertTrue(all(len(s["thread_candidates"]) == 1 for s in r["slices"]))

    def test_zero_ids_are_not_idle_exemptions(self):
        for tid, pid, key, expected in ((0, 20, 90, "ZERO_TID_NOT_PROVEN_IDLE"),
                                       (7, 0, 90, "PID_ZERO_NOT_PROVEN_IDLE"),
                                       (7, 20, 0, "ZERO_PROCESS_KEY_UNPROVEN")):
            with self.subTest(tid=tid, pid=pid, key=key):
                r = self.partition({tid: [(0, 20, pid, True)]},
                                   {pid: [(0, 20, key, True)]}, tid=tid)
                self.assertEqual(r["known_ticks"], 0)
                self.assertEqual(r["slices"][0]["reason"], expected)

    def test_missing_thread_and_large_exact_qpc_no_input_mutation(self):
        offset = 2**60
        t, p = {7: [(offset, offset+7, 20, False)]}, {20: [(offset, offset+20, 90, False)]}
        before = copy.deepcopy((t, p))
        r = self.partition(t, p, (offset, offset+20), (offset, offset+20))
        self.assertEqual((r["known_ticks"], r["unknown_ticks"]), (7, 13))
        self.assertEqual((t, p), before)
        self.assertEqual(self.partition({}, {})["unknown_ticks"], 20)

    def test_malformed_values_are_rejected(self):
        for rows in ({7: [(9, 2, 20, False)]}, {7: [(0, 20, 20, 1)]},
                     {7: [(0.0, 20, 20, False)]}, {7: [(0, 20, True, False)]}):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                partition_interval(7, (0, 20), rows, {}, (0, 20))
        with self.assertRaises(ValueError):
            partition_interval(True, (0, 20), {}, {}, (0, 20))


if __name__ == "__main__":
    unittest.main()
