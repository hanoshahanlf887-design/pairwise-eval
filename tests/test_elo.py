import unittest

from pairwise_eval.elo import compute_elo
from pairwise_eval.models import PairwiseVote


class EloTests(unittest.TestCase):
    def test_win_and_tie(self):
        entries = compute_elo([
            PairwiseVote("item_1", "model_alpha", "model_beta", "A"),
            PairwiseVote("item_2", "model_alpha", "model_beta", "TIE"),
        ], initial_rating=1000, k_factor=32)
        ratings = {entry.model_id: entry.rating for entry in entries}
        self.assertGreater(ratings["model_alpha"], ratings["model_beta"])
        self.assertAlmostEqual(sum(ratings.values()), 2000)

    def test_invalid_k_factor(self):
        with self.assertRaises(ValueError):
            compute_elo([], k_factor=0)


if __name__ == "__main__":
    unittest.main()
