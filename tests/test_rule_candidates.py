import tempfile
import unittest
from pathlib import Path

from ashl_core.correction import create_correction_label, create_correction_pending
from ashl_core.integrated_loop import run_turn
from ashl_core.persistence import read_jsonl
from ashl_core.rule_candidates import (
    append_rule_candidate,
    build_rule_candidate_from_correction,
    list_rule_candidates,
)


class RuleCandidateTests(unittest.TestCase):
    def _pending_for_sleep_mode(self, tmp: str) -> dict:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
        return create_correction_pending(previous, "不是，我是在說睡眠模式功能。", tmp)

    def test_event_mismatch_builds_rule_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            pending = self._pending_for_sleep_mode(tmp)
            correction = create_correction_label(pending, "判斷錯", tmp)
            candidate = build_rule_candidate_from_correction(correction)

            self.assertIsNotNone(candidate)
            self.assertEqual(candidate["type"], "rule_candidate")
            self.assertEqual(candidate["source"], "correction.event_mismatch")
            self.assertEqual(candidate["status"], "candidate")
            self.assertTrue(candidate["audit_required"])

    def test_rule_candidate_writes_and_reads_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            pending = self._pending_for_sleep_mode(tmp)
            correction = create_correction_label(pending, "判斷錯", tmp)
            candidate = build_rule_candidate_from_correction(correction)

            append_rule_candidate(tmp, candidate)

            self.assertEqual(read_jsonl(Path(tmp) / "rule_candidates.jsonl"), [candidate])
            self.assertEqual(list_rule_candidates(tmp), [candidate])

    def test_reaction_strength_mismatch_returns_none(self):
        correction = {"type": "correction.reaction_strength_mismatch"}

        self.assertIsNone(build_rule_candidate_from_correction(correction))

    def test_expression_mismatch_returns_none(self):
        correction = {"type": "correction.expression_mismatch"}

        self.assertIsNone(build_rule_candidate_from_correction(correction))

    def test_unknown_returns_none(self):
        self.assertIsNone(build_rule_candidate_from_correction(None or {}))

    def test_sleep_mode_event_mismatch_builds_concept_counterexample(self):
        with tempfile.TemporaryDirectory() as tmp:
            pending = self._pending_for_sleep_mode(tmp)
            correction = create_correction_label(pending, "判斷錯", tmp)
            candidate = build_rule_candidate_from_correction(correction)

            self.assertEqual(candidate["candidate_kind"], "concept_counterexample")
            self.assertEqual(candidate["target_phrase"], "睡眠模式")
            self.assertEqual(candidate["not_event"], "user.fatigue_signaled")
            self.assertEqual(candidate["prefer_event"], "technical.topic_discussed")
            self.assertEqual(candidate["wrong_event"], "user.fatigue_signaled")
            self.assertEqual(candidate["correct_event"], "technical.topic_discussed")


if __name__ == "__main__":
    unittest.main()
