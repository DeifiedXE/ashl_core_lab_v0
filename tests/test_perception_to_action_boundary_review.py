import unittest
from pathlib import Path


class PerceptionToActionBoundaryReviewTests(unittest.TestCase):
    def setUp(self):
        self.doc_path = Path("docs/perception_to_action_boundary_review_v0.md")
        self.doc = self.doc_path.read_text(encoding="utf-8")

    def test_boundary_review_document_exists(self):
        self.assertTrue(self.doc_path.exists())
        self.assertIn("Perception-to-Action Boundary Review v0", self.doc)

    def test_forbidden_transition_phrases_are_recorded(self):
        for phrase in [
            "A retina feature is not an action reason.",
            "A visual_frame is not an action context.",
            "A change_record is not an action trigger.",
            "A focus_candidate is not an action intent.",
            "A ranking_trace is not action selection.",
            "A focus_application_gate_record does not authorize action influence.",
            "No package may allow perception or focus records to modify action_context",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_action_mapping_boundaries_are_recorded(self):
        for phrase in [
            "Future action influence, if ever allowed, must be review-gated, traceable, reversible, and dry-run tested before runtime use.",
            "No direct mapping from focus rank to action is allowed.",
            "No direct mapping from total_score to action is allowed.",
            "No direct mapping from change_salience to movement is allowed.",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_mentor_endocrine_memory_and_predictor_boundaries_are_recorded(self):
        for phrase in [
            "external_mentor_interrupt has unconditional priority",
            "No endocrine signal may authorize perception-to-action influence in v0.",
            "No norepinephrine-like signal may directly select action in v0.",
            "No cortisol-like signal may directly suppress or redirect action in v0.",
            "No dopamine-like signal may directly reinforce visual action paths in v0.",
            "No direct memory write is allowed from perception/focus traces.",
            "No predictor mutation is allowed from perception/focus traces.",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_future_gates_and_followups_are_recorded(self):
        for phrase in [
            "perception_trace_validity_gate",
            "focus_trace_validity_gate",
            "semantic_boundary_gate",
            "mentor_review_gate",
            "action_influence_boundary_gate",
            "memory_write_boundary_gate",
            "predictor_mutation_boundary_gate",
            "runtime_permission_gate",
            "rollback_gate",
            "Perception-to-Action Gate Schema Check v0",
            "Perception-to-Action Dry-Run Trace Design v0",
            "Perception-to-Action Dry-Run Trace Check v0",
            "Action Influence Human Review Gate v0",
            "No runtime action influence may be added before dry-run and human review gates exist.",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_explicit_non_goals_are_recorded(self):
        for phrase in [
            "No runtime focus selector.",
            "No active_focus selection.",
            "No attention control.",
            "No perception-to-action bridge.",
            "No focus-to-action bridge.",
            "No vision-driven action selection.",
            "No action selection influence.",
            "No action candidate scoring from vision.",
            "No visual memory write.",
            "No long-term memory write.",
            "No lesson_store write.",
            "No Memory Layer write.",
            "No predictor mutation.",
            "No persistent rule creation.",
            "No endocrine runtime.",
            "No object recognition.",
            "No object tracking.",
            "No semantic matching.",
            "No symbol grounding claim.",
            "No consciousness claim.",
            "No subjective visual experience claim.",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
