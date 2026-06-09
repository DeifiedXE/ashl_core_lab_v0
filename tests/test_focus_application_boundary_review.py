from pathlib import Path
import unittest


DOC_PATH = Path("docs/focus_application_boundary_review_v0.md")


class FocusApplicationBoundaryReviewTests(unittest.TestCase):
    def test_design_doc_contains_required_boundaries(self):
        doc = DOC_PATH.read_text(encoding="utf-8")

        required_phrases = [
            "Focus Application Boundary Review",
            "ranking_trace is not an active focus",
            "rank_position 1 is not selected focus",
            "total_score highest is not selected focus",
            "focus_candidate is a proposal only",
            "active_focus",
            "focus_applied",
            "attention_control",
            "focus_application_candidate_gate",
            "focus_lock_prevention_gate",
            "mentor_interrupt_gate",
            "endocrine_boundary_gate",
            "perception_to_action_boundary_gate",
            "runtime_permission_gate",
            "external_mentor_interrupt",
            "unconditional priority",
            "Perception-to-Action Boundary Review",
            "No focus-to-action bridge",
            "No endocrine runtime controls focus",
            "No runtime focus selector.",
            "No runtime ranking.",
            "No active_focus selection.",
            "No focus application.",
            "No attention control.",
            "No action selection influence.",
            "No memory write.",
        ]

        missing = [phrase for phrase in required_phrases if phrase not in doc]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
