import tempfile
import unittest
from pathlib import Path

from ashl_core.persistence import read_jsonl
from ashl_core.trial_feedback import (
    append_trial_feedback,
    build_trial_feedback,
    get_trial_rule_feedback_summary,
    list_trial_feedback,
    summarize_trial_feedback,
)


def sample_suggestion() -> dict:
    return {
        "type": "trial_suggestion",
        "source_trial_rule": "trial_rule_cand_sleep",
        "source_candidate_id": "rule_cand_sleep",
        "target_phrase": "睡眠模式",
        "suggested_action": "block_event_and_prefer_event",
        "block_event": "user.fatigue_signaled",
        "prefer_event": "technical.topic_discussed",
        "confidence": 0.3,
        "applied": False,
        "reason": "approved_for_trial candidate suggests this event mapping",
    }


class TrialFeedbackTests(unittest.TestCase):
    def test_build_helpful_feedback(self):
        feedback = build_trial_feedback(sample_suggestion(), "helpful", note="good")

        self.assertIsNotNone(feedback)
        self.assertEqual(feedback["type"], "trial_feedback")
        self.assertEqual(feedback["verdict"], "helpful")
        self.assertEqual(feedback["trial_rule_id"], "trial_rule_cand_sleep")
        self.assertEqual(feedback["source_candidate_id"], "rule_cand_sleep")

    def test_build_wrong_feedback(self):
        self.assertEqual(build_trial_feedback(sample_suggestion(), "wrong")["verdict"], "wrong")

    def test_build_unclear_feedback(self):
        self.assertEqual(build_trial_feedback(sample_suggestion(), "unclear")["verdict"], "unclear")

    def test_build_ignored_feedback(self):
        self.assertEqual(build_trial_feedback(sample_suggestion(), "ignored")["verdict"], "ignored")

    def test_unknown_verdict_returns_none(self):
        self.assertIsNone(build_trial_feedback(sample_suggestion(), "promote"))

    def test_append_and_list_trial_feedback(self):
        with tempfile.TemporaryDirectory() as tmp:
            feedback = build_trial_feedback(sample_suggestion(), "helpful")

            append_trial_feedback(tmp, feedback)

            self.assertEqual(list_trial_feedback(tmp), [feedback])
            self.assertEqual(read_jsonl(Path(tmp) / "trial_feedback.jsonl"), [feedback])

    def test_summarize_trial_feedback(self):
        with tempfile.TemporaryDirectory() as tmp:
            for verdict in ["helpful", "wrong", "unclear", "ignored", "helpful"]:
                append_trial_feedback(tmp, build_trial_feedback(sample_suggestion(), verdict))

            summary = summarize_trial_feedback(tmp)

            self.assertEqual(summary["total"], 5)
            self.assertEqual(summary["helpful"], 2)
            self.assertEqual(summary["wrong"], 1)
            self.assertEqual(summary["unclear"], 1)
            self.assertEqual(summary["ignored"], 1)

    def test_trial_rule_feedback_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            append_trial_feedback(tmp, build_trial_feedback(sample_suggestion(), "helpful"))
            append_trial_feedback(tmp, build_trial_feedback(sample_suggestion(), "wrong"))
            other = dict(sample_suggestion(), source_trial_rule="trial_other", source_candidate_id="other")
            append_trial_feedback(tmp, build_trial_feedback(other, "helpful"))

            summary = get_trial_rule_feedback_summary(tmp, "trial_rule_cand_sleep")

            self.assertEqual(summary["trial_rule_id"], "trial_rule_cand_sleep")
            self.assertEqual(summary["total"], 2)
            self.assertEqual(summary["helpful"], 1)
            self.assertEqual(summary["wrong"], 1)
            self.assertEqual(summary["helpful_ratio"], 0.5)
            self.assertEqual(summary["wrong_ratio"], 0.5)

    def test_missing_feedback_file_summaries_do_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                summarize_trial_feedback(tmp),
                {"total": 0, "helpful": 0, "wrong": 0, "unclear": 0, "ignored": 0},
            )
            summary = get_trial_rule_feedback_summary(tmp, "trial_rule_cand_sleep")
            self.assertEqual(summary["total"], 0)
            self.assertEqual(summary["helpful_ratio"], 0.0)
            self.assertEqual(summary["wrong_ratio"], 0.0)

    def test_feedback_does_not_create_active_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            append_trial_feedback(tmp, build_trial_feedback(sample_suggestion(), "helpful"))

            self.assertFalse((Path(tmp) / "active_rules.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
