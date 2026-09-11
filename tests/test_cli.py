import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run(
            [sys.executable, "-m", "pairwise_eval", *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_three_commands(self):
        votes = str(ROOT / "examples" / "pairwise_votes.jsonl")
        scores = str(ROOT / "examples" / "dimension_scores.jsonl")
        for command in (
            ("rank", votes, "--json"),
            ("aggregate", scores, "--json"),
            ("consistency", votes, scores, "--tie-tolerance", "0.25", "--json"),
        ):
            with self.subTest(command=command):
                result = self.run_cli(*command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIsInstance(json.loads(result.stdout), dict)

    def test_validation_error_exit_code(self):
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".jsonl")
        with handle:
            handle.write('{"item_id":"item_x"}\n')
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        result = self.run_cli("rank", handle.name)
        self.assertEqual(result.returncode, 2)
        self.assertIn("line 1", result.stderr)


if __name__ == "__main__":
    unittest.main()
