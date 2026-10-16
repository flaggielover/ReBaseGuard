import unittest
from audit_root_coverage import lifetimes


class LifetimeTests(unittest.TestCase):
    def test_rundown_has_unknown_birth_but_bounded_identity(self):
        self.assertEqual(lifetimes([(3, 12, 8), (4, 90, 8)], 10, 100), [(10, 100, 8, True)])

    def test_tid_reuse_is_separate_generation(self):
        self.assertEqual(lifetimes([(1, 11, 8), (2, 12, 8), (1, 20, 9), (2, 30, 9)], 10, 100), [(11, 12, 8, False), (20, 30, 9, False)])

    def test_overlap_is_not_adopted(self):
        with self.assertRaises(ValueError):
            lifetimes([(3, 11, 8), (1, 20, 8), (4, 90, 8)], 10, 100)

    def test_missing_or_mismatched_end(self):
        for rows in [[(1, 11, 8)], [(2, 20, 8)], [(1, 11, 8), (2, 20, 9)]]:
            with self.assertRaises(ValueError):
                lifetimes(rows, 10, 100)


if __name__ == '__main__':
    unittest.main()
