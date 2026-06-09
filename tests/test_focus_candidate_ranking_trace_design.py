from pathlib import Path
import unittest


DOC_PATH = Path("docs/focus_candidate_ranking_trace_design_v0.md")


class FocusCandidateRankingTraceDesignTests(unittest.TestCase):
    def test_design_doc_contains_required_boundaries(self):
        doc = DOC_PATH.read_text(encoding="utf-8")

        required_phrases = [
            "ranking_trace",
            "ranking item",
            "rank_position",
            "score_snapshot",
            "total_score is a ranking reference",
            "not a sole winner condition",
            "cooldown_state",
            "decay_state",
            "interruptible",
            "forced_interrupt_reason",
            "external_mentor_interrupt",
            "unconditional priority",
            "active_focus_id",
            "active_focus_id = None",
            "focus_applied = False",
            "attention_control = False",
            "runtime_ranking = False",
            "runtime_focus_selector = False",
            "No runtime ranking.",
            "No active_focus selection.",
            "No focus application.",
            "No attention control.",
            "No action selection influence.",
            "No memory write.",
            "Perception-to-Action Boundary Review",
        ]

        missing = [phrase for phrase in required_phrases if phrase not in doc]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
