from pathlib import Path
import unittest


class Phase0CurrentCapabilitySnapshotTests(unittest.TestCase):
    def test_snapshot_contains_required_boundary_phrases(self):
        doc = Path("docs/phase0_current_capability_snapshot_2026-06-10.md").read_text(encoding="utf-8")
        required_phrases = [
            "Retained memory can reversibly alter controlled runtime action tendency scores inside a bounded safety envelope",
            "No production action selection",
            "No final_action",
            "No action execution",
            "No proof of learning",
            "No object recognition",
            "No semantic vision",
            "No active_focus",
            "No semantic memory search",
            "No five-layer memory runtime",
            "Temporary cross-session space is demo / fixture handoff only",
            "AGE-to-AGE teaching is a future conceptual line only",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, doc)


if __name__ == "__main__":
    unittest.main()
