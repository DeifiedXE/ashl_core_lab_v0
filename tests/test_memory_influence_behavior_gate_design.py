from pathlib import Path
import unittest


class MemoryInfluenceBehaviorGateDesignTests(unittest.TestCase):
    def setUp(self):
        self.doc_path = Path("docs/memory_influence_behavior_gate_design_v0.md")
        self.doc = self.doc_path.read_text(encoding="utf-8")

    def test_required_gate_boundary_phrases_are_present(self):
        required_phrases = [
            "The behavior gate is not an action selector",
            "The behavior gate only decides whether a memory influence preview is eligible for future pre-action consideration",
            "allowed_for_runtime_action_selection must remain False",
            "allowed_for_final_action must remain False",
            "Past failure is a warning, not a prohibition",
            "Curiosity must not be overwritten by retained memory alone",
            "Mentor override must remain available",
            "Rollback must disable the admitted influence without deleting retained memory",
            "semantic_or_fuzzy_memory_match",
            "proof_of_learning_claim",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_runtime_behavior_remains_not_implemented(self):
        forbidden_runtime_phrases = [
            "No production/runtime memory-influenced behavior is allowed.",
            "sandbox-only lesson application and observation records",
            "No runtime action selection.",
            "No final_action creation.",
            "No direct action command.",
            "No action behavior change.",
            "No proof-of-learning claim.",
        ]

        for phrase in forbidden_runtime_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
