from pathlib import Path
import unittest


DOC_PATH = Path("docs/visual_frame_change_design_v0.md")


class VisualFrameChangeDesignTests(unittest.TestCase):
    def test_design_doc_contains_required_boundaries(self):
        doc = DOC_PATH.read_text(encoding="utf-8")

        required_phrases = [
            "previous_frame",
            "current_frame",
            "change_record",
            "feature_appeared",
            "feature_disappeared",
            "feature_modified",
            "position_changed",
            "no_change",
            "semantic_label remains null",
            "not object tracking",
            "not focus selection",
            "blocked_from_action_selection",
            "blocked_from_memory_write",
            "blocked_from_focus_selection",
            "blocked_from_endocrine_control",
            "No runtime frame storage.",
            "No change detection runtime.",
            "No action selection influence.",
            "No memory write.",
        ]

        missing = [phrase for phrase in required_phrases if phrase not in doc]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
