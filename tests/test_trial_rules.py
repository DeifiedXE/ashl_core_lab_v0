import copy
import tempfile
import unittest

from ashl_core.candidate_review import append_candidate_review, build_candidate_review
from ashl_core.rule_candidates import append_rule_candidate
from ashl_core.trial_rules import (
    build_trial_rule_view,
    build_trial_suggestions,
    list_approved_trial_candidates,
)


def sample_candidate() -> dict:
    return {
        "id": "rule_cand_sleep",
        "type": "rule_candidate",
        "status": "candidate",
        "candidate_kind": "concept_counterexample",
        "target_phrase": "睡眠模式",
        "wrong_event": "user.fatigue_signaled",
        "correct_event": "technical.topic_discussed",
        "not_event": "user.fatigue_signaled",
        "prefer_event": "technical.topic_discussed",
        "confidence": 0.3,
        "audit_required": True,
        "created_at": "2026-06-04T00:00:00+00:00",
    }


class TrialRulesTests(unittest.TestCase):
    def test_no_approved_candidate_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list_approved_trial_candidates(tmp), [])

    def test_reviewed_candidate_is_not_trial_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = sample_candidate()
            append_rule_candidate(tmp, candidate)
            append_candidate_review(tmp, build_candidate_review(candidate, "reviewed"))

            self.assertEqual(list_approved_trial_candidates(tmp), [])

    def test_rejected_candidate_is_not_trial_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = sample_candidate()
            append_rule_candidate(tmp, candidate)
            append_candidate_review(tmp, build_candidate_review(candidate, "rejected"))

            self.assertEqual(list_approved_trial_candidates(tmp), [])

    def test_approved_candidate_becomes_trial_rule_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = sample_candidate()
            append_rule_candidate(tmp, candidate)
            append_candidate_review(tmp, build_candidate_review(candidate, "approved_for_trial"))

            approved = list_approved_trial_candidates(tmp)
            view = build_trial_rule_view(approved[0])

            self.assertEqual(len(approved), 1)
            self.assertEqual(view["id"], "trial_rule_cand_sleep")
            self.assertEqual(view["type"], "trial_rule_view")
            self.assertFalse(view["active"])
            self.assertEqual(view["status"], "trial_view")
            self.assertTrue(view["audit_required"])

    def test_sleep_mode_fatigue_event_produces_trial_suggestion(self):
        view = build_trial_rule_view(sample_candidate())
        events = [
            {"name": "user.fatigue_signaled", "confidence": 0.7},
            {"name": "technical.topic_discussed", "confidence": 0.9},
        ]

        suggestions = build_trial_suggestions("睡眠模式這個功能怎麼設計？", events, [view])

        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0]["type"], "trial_suggestion")
        self.assertEqual(suggestions[0]["source_trial_rule"], "trial_rule_cand_sleep")
        self.assertEqual(suggestions[0]["block_event"], "user.fatigue_signaled")
        self.assertEqual(suggestions[0]["prefer_event"], "technical.topic_discussed")
        self.assertFalse(suggestions[0]["applied"])

    def test_text_without_target_phrase_produces_no_suggestion(self):
        view = build_trial_rule_view(sample_candidate())
        events = [{"name": "user.fatigue_signaled", "confidence": 0.7}]

        self.assertEqual(build_trial_suggestions("一般輸入", events, [view]), [])

    def test_missing_block_event_produces_no_suggestion(self):
        view = build_trial_rule_view(sample_candidate())
        events = [{"name": "technical.topic_discussed", "confidence": 0.9}]

        self.assertEqual(build_trial_suggestions("睡眠模式這個功能怎麼設計？", events, [view]), [])

    def test_trial_suggestion_does_not_modify_candidate_events(self):
        view = build_trial_rule_view(sample_candidate())
        events = [
            {"name": "user.fatigue_signaled", "confidence": 0.7},
            {"name": "technical.topic_discussed", "confidence": 0.9},
        ]
        before = copy.deepcopy(events)

        build_trial_suggestions("睡眠模式這個功能怎麼設計？", events, [view])

        self.assertEqual(events, before)


if __name__ == "__main__":
    unittest.main()
