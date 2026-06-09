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
            "Focus Lock Prevention",
            "Attention Transfer Safety",
            "attention_intensity_cap",
            "attention_duration_limit",
            "norepinephrine_like_interrupt",
            "cortisol_like_forced_diffusion",
            "interruptible",
            "decayable",
            "bounded",
            "Attention Forced Interruption Conditions",
            "attention_duration_exceeded",
            "norepinephrine_like_new_change_interrupt",
            "cortisol_threshold_forced_diffusion",
            "external_mentor_interrupt",
            "N is not defined in v0.",
            "Threshold values are not defined in v0.",
            "blocked_from_action_selection",
            "blocked_from_memory_write",
            "blocked_from_endocrine_control",
            "Perception-to-Action Boundary Review",
            "No runtime focus selector.",
            "no norepinephrine-controlled attention",
            "no cortisol-controlled attention",
            "No action selection influence.",
            "No memory write.",
        ]

        missing = [phrase for phrase in required_phrases if phrase not in doc]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
