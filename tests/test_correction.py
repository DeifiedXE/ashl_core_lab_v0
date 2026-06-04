import tempfile
import unittest
from pathlib import Path

from ashl_core.correction import CORRECTION_OPTIONS, create_correction_pending, is_correction_request
from ashl_core.integrated_loop import run_turn
from ashl_core.persistence import read_jsonl


class CorrectionTests(unittest.TestCase):
    def test_correction_detection(self):
        self.assertTrue(is_correction_request("不是，我是在說睡眠模式功能。"))
        self.assertFalse(is_correction_request("睡眠模式這個功能怎麼設計？"))

    def test_create_correction_pending_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            pending = create_correction_pending(previous, "不是，我是在說睡眠模式功能。", tmp)
            rows = read_jsonl(Path(tmp) / "correction_log.jsonl")

            self.assertEqual(pending["type"], "correction.pending")
            self.assertTrue(pending["needs_user_label"])
            self.assertEqual(pending["options"], CORRECTION_OPTIONS)
            self.assertEqual(rows, [pending])

    def test_integrated_loop_correction_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
            rows = read_jsonl(Path(tmp) / "correction_log.jsonl")

            self.assertIsNotNone(result["correction_pending"])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["type"], "correction.pending")
            self.assertIn("event_mismatch", rows[0]["options"])
            self.assertIn("Correction pending", result["final_output"])

    def test_no_previous_trace_does_not_crash_or_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp)

            self.assertIsNone(result["correction_pending"])
            self.assertEqual(read_jsonl(Path(tmp) / "correction_log.jsonl"), [])


if __name__ == "__main__":
    unittest.main()
