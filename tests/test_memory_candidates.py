import tempfile
import unittest
from pathlib import Path

from ashl_core.integrated_loop import run_turn
from ashl_core.memory_candidates import create_memory_candidate
from ashl_core.persistence import read_jsonl


class MemoryCandidateTests(unittest.TestCase):
    def test_create_memory_candidate_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = create_memory_candidate("記住，以後 ASHL Core 先走實驗路線", tmp)
            rows = read_jsonl(Path(tmp) / "memory_candidates.jsonl")

            self.assertEqual(candidate["type"], "memory_candidate")
            self.assertEqual(candidate["status"], "candidate")
            self.assertTrue(candidate["audit_required"])
            self.assertEqual(rows, [candidate])
            self.assertIn("ASHL Core", candidate["content"])

    def test_integrated_loop_memory_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_turn("記住，以後 ASHL Core 先走實驗路線", data_dir=tmp)
            rows = read_jsonl(Path(tmp) / "memory_candidates.jsonl")

            self.assertEqual(result["decision"]["intent"], "self_check")
            self.assertIsNotNone(result["memory_candidate"])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "candidate")
            self.assertTrue(rows[0]["audit_required"])
            self.assertIn("不直接", result["final_output"])


if __name__ == "__main__":
    unittest.main()
