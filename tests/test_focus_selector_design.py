from pathlib import Path
import unittest


DOC_PATH = Path("docs/focus_selector_design_v0.md")


class FocusSelectorDesignTests(unittest.TestCase):
    def test_design_doc_contains_required_boundaries(self):
        doc = DOC_PATH.read_text(encoding="utf-8")

        required_phrases = [
            "focus_candidate",
            "candidate_source",
            "reason_codes",
            "score_fields",
            "semantic_label remains null",
            "not attention",
            "not action intent",
            "not object recognition",
            "not object tracking",
            "not semantic vision",
            "runtime_focus_selector = False",
            "attention_control = False",
            "focus_applied = False",
            "blocked_from_action_selection",
            "blocked_from_memory_write",
            "blocked_from_endocrine_control",
            "Perception-to-Action Boundary Review",
            "No runtime focus selector.",
            "No action selection influence.",
            "No memory write.",
        ]

        missing = [phrase for phrase in required_phrases if phrase not in doc]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
