import unittest

from pairwise_eval.consistency import strict_consistent, summarize_consistency, tolerance_consistent


class ConsistencyTests(unittest.TestCase):
    def test_strict_and_tolerance(self):
        self.assertTrue(strict_consistent("A", 2, 1))
        self.assertFalse(strict_consistent("TIE", 2, 1.9))
        self.assertTrue(tolerance_consistent("TIE", 2, 1.9, 0.1))
        self.assertFalse(tolerance_consistent("A", 1.9, 2, 10))

    def test_summary_and_empty_rates(self):
        rows = [
            {"preference": "A", "score_a": 2, "score_b": 1},
            {"preference": "TIE", "score_a": 2, "score_b": 1.9},
        ]
        summary = summarize_consistency(rows, total_pair_count=3, tie_tolerance=0.1)
        self.assertEqual(summary.unmatched_pair_count, 1)
        self.assertEqual(summary.strict_consistency_rate, 0.5)
        self.assertEqual(summary.tolerance_consistency_rate, 1.0)
        self.assertIsNone(summary.per_label_consistency["B"]["strict_rate"])


if __name__ == "__main__":
    unittest.main()
