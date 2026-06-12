from pathlib import Path
import unittest


class FirstMemoryInfluencedBehaviorBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.doc_path = Path("docs/first_memory_influenced_behavior_boundary_v0.md")
        self.doc = self.doc_path.read_text(encoding="utf-8")

    def test_required_boundary_phrases_are_present(self):
        required_phrases = [
            "Memory may advise action tendency only",
            "Memory must not directly choose final_action",
            "Memory is a warning sign, not a ban command",
            "Past failure is a warning, not a prohibition",
            "retained memory matched → final_action",
            "exploration not blocked",
            "mentor override preserved",
            "rollback path defined",
            "runtime_action_selection_allowed must remain False",
            "Retained memory and applied influence are separate",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_runtime_behavior_remains_not_implemented(self):
        forbidden_runtime_claims = [
            "No production/runtime memory-influenced behavior is allowed.",
            "sandbox-only lesson application and observation records",
            "No runtime action selection.",
            "No final_action creation.",
            "No direct action command.",
            "No action behavior change.",
            "No proof-of-learning claim.",
        ]

        for phrase in forbidden_runtime_claims:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
