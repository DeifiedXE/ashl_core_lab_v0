import unittest
from pathlib import Path


class ActionOutcomeContrastBaselineReviewTests(unittest.TestCase):
    def setUp(self):
        self.doc_path = Path("docs/action_outcome_contrast_baseline_review_v0.md")
        self.doc = self.doc_path.read_text(encoding="utf-8")

    def test_baseline_review_document_exists(self):
        self.assertTrue(self.doc_path.exists())
        self.assertIn("Action Outcome Contrast Baseline Review v0", self.doc)

    def test_phase0_contrast_path_is_recorded(self):
        for phrase in [
            "action_intent",
            "expected_outcome",
            "actual_outcome",
            "mismatch",
            "structured failure_reason",
            "lesson_candidate",
            "human review",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_existing_components_are_recorded(self):
        for phrase in [
            "ashl_core/failure_events.py",
            "ashl_core/session_working_memory.py",
            "ashl_core/failure_reason_classifier.py",
            "ashl_core/action_outcome_predictor.py",
            "ashl_core/lesson_candidate_drafts.py",
            "ashl_core/candidate_review.py",
            "ashl_core/integrated_loop.py",
            "failure_event schema foundation",
            "lesson_candidate_draft schema trace",
            "session_working_memory",
            "action_outcome_predictor",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_known_gaps_are_recorded(self):
        for phrase in [
            "whether expected_outcome and actual_outcome are consistently recorded together",
            "whether mismatch fields are standardized",
            "whether failure_reason coverage is complete",
            "whether lesson_candidate source_trace is complete",
            "whether action selection remains unaffected by all review-only traces",
            "whether predictor outputs are consistently blocked from action selection",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_baseline_result_and_recommendation_are_recorded(self):
        for phrase in [
            "Phase 0 action/outcome contrast path exists in partial trace/review form.",
            "The next safe step should strengthen auditability before changing behavior.",
            "Expected vs Actual Outcome Pair Schema Check v0",
            "Validate the smallest reusable expected_outcome / actual_outcome / mismatch record shape",
            "checks that expected_outcome and actual_outcome are both present",
            "checks that unknown-vs-unknown is not valid learning evidence",
            "checks that mismatch is explicit and boolean",
            "checks that structured failure_reason remains required before lesson_candidate input",
            "no runtime action selection",
            "no predictor mutation",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_safety_boundaries_are_recorded(self):
        for phrase in [
            "no runtime action selection",
            "no action selection influence",
            "no new action behavior",
            "no lesson application runtime",
            "no automatic lesson application",
            "no persistent learning",
            "no persistent rule write",
            "no long-term memory write",
            "no lesson_store write",
            "no visual memory write",
            "no predictor mutation",
            "no perception-to-action bridge",
            "no focus-to-action bridge",
            "no active_focus",
            "no attention_control",
            "no endocrine runtime",
            "no autonomy",
            "no semantic vision",
            "no subjective claims",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
