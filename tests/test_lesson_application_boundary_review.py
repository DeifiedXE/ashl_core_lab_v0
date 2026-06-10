from pathlib import Path
import unittest


DOC_PATH = Path("docs/lesson_application_boundary_review_v0.md")


class LessonApplicationBoundaryReviewTests(unittest.TestCase):
    def test_design_doc_contains_required_boundaries(self):
        doc = DOC_PATH.read_text(encoding="utf-8")

        required_phrases = [
            "Lesson Application Boundary Review",
            "reviewed_lesson_trace_preview is not lesson application",
            "approved_for_preview is not approval for application",
            "preview_content is not an action command",
            "preview_content must not modify action selection",
            "preview_content must not modify action behavior",
            "dry-run correction",
            "Application is forbidden in v0.",
            "No direct mapping from lesson preview to action selection",
            "No direct mapping from correction_type to action command",
            "No direct mapping from lesson_candidate to behavior change",
            "external mentor instruction has unconditional priority",
            "reviewed_preview_validity_gate",
            "dry_run_correction_gate",
            "before_after_contrast_gate",
            "lesson_effect_evidence_gate",
            "human_application_approval_gate",
            "action_selection_boundary_gate",
            "memory_write_boundary_gate",
            "predictor_mutation_boundary_gate",
            "persistence_boundary_gate",
            "rollback_gate",
            "Reviewed Lesson Dry-Run Correction Combined Package",
            "No dry-run correction runtime.",
            "No lesson application runtime.",
            "No runtime action selection.",
            "No action behavior change.",
            "No memory write.",
            "No predictor mutation.",
            "No proof of learning claim.",
        ]

        missing = [phrase for phrase in required_phrases if phrase not in doc]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
