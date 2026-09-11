import unittest

from pairwise_eval.analysis import analyze_consistency, prepare_scores
from pairwise_eval.models import DimensionScore, PairwiseVote


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.scores = [
            DimensionScore("item_1", "model_alpha", "annotator_01", {"quality": 4}),
            DimensionScore("item_1", "model_alpha", "annotator_02", {"quality": 2}),
            DimensionScore("item_1", "model_beta", "annotator_01", {"quality": 1}),
        ]

    def test_aggregation_granularity(self):
        rows, stats = prepare_scores(self.scores)
        index = {(row["item_id"], row["model_id"]): row for row in rows}
        self.assertEqual(index[("item_1", "model_alpha")]["score"], 3)
        self.assertEqual(index[("item_1", "model_alpha")]["record_count"], 2)
        self.assertIsNone(stats)

    def test_matching_and_unmatched(self):
        votes = [
            PairwiseVote("item_1", "model_alpha", "model_beta", "A"),
            PairwiseVote("item_missing", "model_alpha", "model_beta", "TIE"),
        ]
        result = analyze_consistency(votes, self.scores, tie_tolerance=0.25)
        self.assertEqual(result["matched_pair_count"], 1)
        self.assertEqual(result["unmatched_pair_count"], 1)
        self.assertEqual(result["strict_consistency_rate"], 1)

    def test_normalization_precedes_aggregation(self):
        rows, stats = prepare_scores(self.scores, normalize_annotators=True)
        self.assertIsNotNone(stats)
        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
