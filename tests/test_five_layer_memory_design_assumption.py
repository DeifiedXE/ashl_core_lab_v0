import unittest
from pathlib import Path


class FiveLayerMemoryDesignAssumptionTests(unittest.TestCase):
    def test_design_doc_contains_required_phrases(self):
        doc = Path("docs/five_layer_memory_design_assumption_v0_1.md").read_text(
            encoding="utf-8"
        )
        required_phrases = [
            "Core Memory",
            "Long-term Memory",
            "Working Memory",
            "Archive Memory",
            "Anchor Layer",
            "Anchor Layer is a navigation index",
            "does not store memory content",
            "mentor-gated JSONL retention",
            "Archive Memory: not implemented",
            "Anchor Layer: not implemented",
            "No endocrine-driven anchor lookup is implemented",
            "五層記憶系統已完整實作",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, doc)

    def test_forbidden_complete_implementation_claim_only_appears_in_not_allowed_claims(self):
        doc = Path("docs/five_layer_memory_design_assumption_v0_1.md").read_text(
            encoding="utf-8"
        )
        phrase = "五層記憶系統已完整實作"
        self.assertEqual(doc.count(phrase), 1)
        not_allowed_section = doc.split("## Not-Allowed Claims", 1)[1]
        self.assertIn(phrase, not_allowed_section)

    def test_archive_memory_minimum_fields_are_preserved(self):
        doc = Path("docs/five_layer_memory_design_assumption_v0_1.md").read_text(
            encoding="utf-8"
        )
        for field in ["文字片段", "來源情境摘要", "信心等級", "使用次數"]:
            with self.subTest(field=field):
                self.assertIn(field, doc)


if __name__ == "__main__":
    unittest.main()
