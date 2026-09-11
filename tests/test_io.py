import json
import tempfile
import unittest
from pathlib import Path

from pairwise_eval.io import InputError, read_dimension_scores, read_pairwise_votes


class InputTests(unittest.TestCase):
    def write(self, text):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".jsonl")
        with handle:
            handle.write(text)
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return handle.name

    def test_reads_records(self):
        votes = read_pairwise_votes(self.write('{"item_id":"item_x","model_a":"model_alpha","model_b":"model_beta","preference":"A"}\n'))
        self.assertEqual(len(votes), 1)
        scores = read_dimension_scores(self.write('{"item_id":"item_x","model_id":"model_alpha","annotator_id":"annotator_01","dimensions":{"quality":4}}\n'))
        self.assertEqual(scores[0].dimensions["quality"], 4)

    def test_error_has_file_line_and_missing_field(self):
        path = self.write('{"item_id":"item_x"}\n')
        with self.assertRaises(InputError) as caught:
            read_pairwise_votes(path)
        message = str(caught.exception)
        self.assertIn(path, message)
        self.assertIn("line 1", message)
        self.assertIn("missing required field", message)

    def test_invalid_json_and_invalid_score(self):
        with self.assertRaisesRegex(InputError, "line 1: invalid JSON"):
            read_pairwise_votes(self.write("not-json\n"))
        bad = {"item_id": "item_x", "model_id": "model_alpha", "annotator_id": "annotator_01", "dimensions": {"quality": True}}
        with self.assertRaisesRegex(InputError, "bool is not allowed"):
            read_dimension_scores(self.write(json.dumps(bad) + "\n"))


if __name__ == "__main__":
    unittest.main()
