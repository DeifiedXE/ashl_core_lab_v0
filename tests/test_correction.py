import tempfile
import unittest
from pathlib import Path

from ashl_core.correction import (
    CORRECTION_OPTIONS,
    create_correction_label,
    create_correction_pending,
    is_correction_request,
    parse_correction_label,
)
from ashl_core.integrated_loop import run_turn
from ashl_core.persistence import read_jsonl
from ashl_core.rule_candidates import build_rule_candidate_from_correction


class CorrectionTests(unittest.TestCase):
    def test_correction_detection(self):
        self.assertTrue(is_correction_request("不是，我是在說睡眠模式功能。"))
        self.assertFalse(is_correction_request("睡眠模式這個功能怎麼設計？"))

    def test_parse_event_mismatch(self):
        self.assertEqual(parse_correction_label("判斷錯"), "event_mismatch")

    def test_parse_reaction_strength_mismatch(self):
        self.assertEqual(parse_correction_label("反應太強"), "reaction_strength_mismatch")

    def test_parse_expression_mismatch(self):
        self.assertEqual(parse_correction_label("說法不對"), "expression_mismatch")

    def test_parse_unknown(self):
        self.assertEqual(parse_correction_label("不知道"), "unknown")

    def test_create_correction_pending_writes_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            pending = create_correction_pending(previous, "不是，我是在說睡眠模式功能。", tmp)
            rows = read_jsonl(Path(tmp) / "correction_log.jsonl")

            self.assertEqual(pending["type"], "correction.pending")
            self.assertTrue(pending["needs_user_label"])
            self.assertEqual(pending["options"], CORRECTION_OPTIONS)
            self.assertEqual(rows, [pending])

    def test_pending_to_event_mismatch_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            pending = create_correction_pending(previous, "不是，我是在說睡眠模式功能。", tmp)
            label = create_correction_label(pending, "判斷錯", tmp)
            rows = read_jsonl(Path(tmp) / "correction_log.jsonl")

            self.assertIsNotNone(label)
            self.assertEqual(label["type"], "correction.event_mismatch")
            self.assertEqual(label["label"], "event_mismatch")
            self.assertEqual(label["status"], "labeled")
            self.assertEqual(label["source_pending_id"], pending["id"])
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[-1], label)
            self.assertFalse((Path(tmp) / "rule_candidates.jsonl").exists())

    def test_event_mismatch_label_can_feed_rule_candidate_builder(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            pending = create_correction_pending(previous, "不是，我是在說睡眠模式功能。", tmp)
            label = create_correction_label(pending, "判斷錯", tmp)
            candidate = build_rule_candidate_from_correction(label)

            self.assertIsNotNone(candidate)
            self.assertEqual(candidate["status"], "candidate")
            self.assertNotEqual(candidate["status"], "active")

    def test_unknown_label_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            pending = create_correction_pending(previous, "不是，我是在說睡眠模式功能。", tmp)
            before = read_jsonl(Path(tmp) / "correction_log.jsonl")
            label = create_correction_label(pending, "不知道", tmp)
            after = read_jsonl(Path(tmp) / "correction_log.jsonl")

            self.assertIsNone(label)
            self.assertEqual(after, before)

    def test_integrated_loop_correction_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
            rows = read_jsonl(Path(tmp) / "correction_log.jsonl")

            self.assertIsNotNone(result["correction_pending"])
            self.assertIsNone(result["correction_label"])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["type"], "correction.pending")
            self.assertIn("event_mismatch", rows[0]["options"])
            self.assertIn("判斷錯", result["final_output"])

    def test_no_previous_trace_does_not_crash_or_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp)

            self.assertIsNone(result["correction_pending"])
            self.assertEqual(read_jsonl(Path(tmp) / "correction_log.jsonl"), [])


if __name__ == "__main__":
    unittest.main()
