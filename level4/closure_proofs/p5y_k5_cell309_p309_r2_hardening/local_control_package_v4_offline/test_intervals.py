import unittest
from account_saved_qpc import union, overlap, clipped, unique_lifetime


class IntervalTests(unittest.TestCase):
    def test_nested_irq_is_not_double_subtracted(self):
        self.assertEqual(overlap([(0, 10)], [(1, 8), (3, 5), (7, 9)]), 8)

    def test_disjoint_cpu_time(self):
        self.assertEqual(overlap([(1, 3), (6, 10)], [(2, 7)]), 2)

    def test_touching_half_open_boundaries(self):
        self.assertEqual(overlap([(1, 3)], [(3, 4)]), 0)

    def test_unsorted_union(self):
        self.assertEqual(union([(7, 9), (0, 2), (2, 8)]), [(0, 9)])

    def test_zero_length(self):
        self.assertEqual(union([(4, 4)]), [])

    def test_bad_interval(self):
        for interval in [(-1, 3), (4, 3)]:
            with self.assertRaises(ValueError):
                union([interval])

    def test_clipping(self):
        self.assertEqual(clipped(1, 9, 3, 7), (3, 7))
        self.assertIsNone(clipped(1, 3, 3, 7))

    def test_clipping_rejects_backwards(self):
        with self.assertRaises(ValueError):
            clipped(4, 1, 0, 10)

    def test_unique_generation(self):
        self.assertEqual(unique_lifetime([(1, 4, 9), (2, 8, 9)], 2), (4, 8))

    def test_generation_reuse_or_missing(self):
        for rows in [[(1, 4, 9)], [(1, 4, 9), (2, 8, 10)], [(1, 4, 9), (1, 5, 9), (2, 8, 9)], [(1, 8, 9), (2, 4, 9)]]:
            with self.assertRaises(ValueError):
                unique_lifetime(rows, 2)


if __name__ == '__main__':
    unittest.main()
