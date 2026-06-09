import unittest
from pathlib import Path


class Phase0ActionLessonLoopReturnPlanningTests(unittest.TestCase):
    def setUp(self):
        self.doc_path = Path("docs/phase0_action_lesson_loop_return_planning_v0.md")
        self.doc = self.doc_path.read_text(encoding="utf-8")

    def test_planning_document_exists(self):
        self.assertTrue(self.doc_path.exists())
        self.assertIn("Phase 0 Action / Lesson Loop Return Planning v0", self.doc)

    def test_phase0_core_loop_is_recorded(self):
        for phrase in [
            "action_intent",
            "expected_outcome",
            "actual_outcome",
            "mismatch",
            "structured failure_reason",
            "lesson_candidate",
            "human review",
            "approved lesson",
            "future behavior correction",
            "Qingyin's grounding priority remains action-result contrast, not visual action control.",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_perception_focus_pause_reason_is_recorded(self):
        for phrase in [
            "The perception/focus path has reached a safe trace/checker/review milestone.",
            "Further work toward active_focus, focus_applied, attention_control, or perception-to-action bridge would cross into runtime control territory.",
            "Before vision/focus can influence action, the action/lesson loop itself should remain the primary maturity target.",
            "ASHL Core / Qingyin has deterministic trace/checker/review-only perception/focus paths",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_safe_next_options_and_recommendation_are_recorded(self):
        for phrase in [
            "Option A: Action Outcome Contrast Baseline Review v0",
            "Review the current action -> expected_outcome -> actual_outcome contrast path",
            "Option B: Failure Reason Coverage Audit v0",
            "Audit whether failure_reason categories cover the next Phase 0 sandbox cases.",
            "Option C: Lesson Candidate Review Path Audit v0",
            "Review how lesson_candidate is generated, reviewed, approved",
            "Recommended:",
            "Action Outcome Contrast Baseline Review v0",
            "It re-centers the project on Phase 0 action grounding without opening runtime action selection or persistent learning.",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_do_not_cross_boundaries_are_recorded(self):
        for phrase in [
            "Do not resume perception-to-action bridge yet.",
            "Do not introduce active_focus.",
            "Do not introduce focus_applied.",
            "Do not introduce attention_control.",
            "Do not allow focus rank, total_score, or change_salience to affect action.",
            "Do not add action selection influence from vision.",
            "Do not add memory write from perception/focus traces.",
            "Do not add predictor mutation.",
            "Do not add persistent rule write.",
            "Do not add endocrine-controlled action.",
            "Do not add runtime action selection.",
            "Do not add lesson application runtime.",
            "Do not add persistent learning.",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_snapshot_and_boundary_check_are_recorded(self):
        for phrase in [
            "Boundary Index Version: 2026-06-09-b41",
            "latest completed commit: 32d4749 Add focus perception boundary construction log",
            "py -3 run_all_smoke_tests.py: PASS",
            "py -3 -m unittest discover: PASS, Ran 1559 tests",
            "planning_only: true",
            "runtime_action_selection_added: false",
            "perception_to_action_bridge_added: false",
            "active_focus_selection_added: false",
            "predictor_modified: false",
            "endocrine_runtime_added: false",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
