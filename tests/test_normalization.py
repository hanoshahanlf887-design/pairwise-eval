import unittest

from pairwise_eval.normalization import mean_shift_normalize


class NormalizationTests(unittest.TestCase):
    def test_mean_shift(self):
        rows = [
            {"annotator_id": "annotator_01", "score": 2.0},
            {"annotator_id": "annotator_01", "score": 4.0},
            {"annotator_id": "annotator_02", "score": 6.0},
        ]
        normalized, stats = mean_shift_normalize(rows)
        self.assertAlmostEqual(stats.global_mean, 4.0)
        self.assertAlmostEqual(normalized[0]["normalized_score"], 3.0)
        self.assertAlmostEqual(normalized[2]["normalized_score"], 4.0)
        self.assertNotIn("normalized_score", rows[0])

    def test_empty_population(self):
        with self.assertRaises(ValueError):
            mean_shift_normalize([])


if __name__ == "__main__":
    unittest.main()
