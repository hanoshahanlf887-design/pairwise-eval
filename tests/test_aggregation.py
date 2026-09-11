import unittest

from pairwise_eval.aggregation import mean_dimensions, weighted_dimensions


class AggregationTests(unittest.TestCase):
    def test_arbitrary_dimensions(self):
        self.assertEqual(mean_dimensions({"clarity": 2, "usefulness": 4}), 3)
        self.assertEqual(weighted_dimensions({"clarity": 2, "usefulness": 4}, {"clarity": 1, "usefulness": 3}), 3.5)

    def test_weight_contract(self):
        with self.assertRaisesRegex(ValueError, "must match"):
            weighted_dimensions({"clarity": 2}, {"clarity": 1, "usefulness": 1})
        with self.assertRaises(ValueError):
            weighted_dimensions({"clarity": 2}, {"clarity": 0})


if __name__ == "__main__":
    unittest.main()
