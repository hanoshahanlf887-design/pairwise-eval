import math
import unittest

from pairwise_eval.validation import validate_finite_number, validate_preference, validate_tolerance, validate_weights


class ValidationTests(unittest.TestCase):
    def test_valid_values(self):
        self.assertEqual(validate_preference("TIE"), "TIE")
        self.assertEqual(validate_finite_number(3), 3.0)

    def test_invalid_labels_and_numbers(self):
        with self.assertRaises(ValueError):
            validate_preference("LEFT")
        for value in (True, math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_finite_number(value)

    def test_tolerance_and_weights(self):
        with self.assertRaises(ValueError):
            validate_tolerance(-0.1)
        with self.assertRaises(ValueError):
            validate_weights({"quality": 0})
        with self.assertRaises(ValueError):
            validate_weights({"quality": -1})


if __name__ == "__main__":
    unittest.main()
