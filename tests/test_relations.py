import math
import unittest

from pairwise_eval.relations import relation


class RelationTests(unittest.TestCase):
    def test_all_relations(self):
        self.assertEqual(relation(2, 1), "A")
        self.assertEqual(relation(1, 2), "B")
        self.assertEqual(relation(2, 2), "TIE")

    def test_rejects_bool_and_non_finite(self):
        for value in (True, math.nan, math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                relation(value, 1)


if __name__ == "__main__":
    unittest.main()
