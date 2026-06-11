import unittest
from pathlib import Path


class FiveLayerMemoryFrameworkBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.doc_path = Path("docs/five_layer_memory_framework_boundary_v0.md")
        self.doc = self.doc_path.read_text(encoding="utf-8")

    def test_required_boundary_phrases_exist(self):
        required_phrases = [
            "Core Memory",
            "Long-term Memory",
            "Working Memory",
            "Archive Memory",
            "Anchor Layer",
            "Five-layer memory runtime: not implemented",
            "Retained Experience Exact-Key Lookup Minimal v0",
            "exact_key only",
            "Retained Experience Into Dry-Run",
            "first memory-influenced behavior",
            "separate high-risk boundary review",
            "Archive Memory is not implemented",
            "Anchor Layer stores navigation/index paths, not memory content",
            "Specialty anchors are not allowed until Qingyin has a stable self-model",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_forbidden_runtime_claims_remain_blocked(self):
        blocked_phrases = [
            "No Archive Memory runtime.",
            "No Anchor Layer runtime.",
            "No five-layer memory runtime.",
            "No semantic/fuzzy/vector retrieval.",
            "No memory-influenced behavior in this package.",
            "No runtime action selection or action behavior change.",
            "No predictor mutation.",
            "No endocrine-driven anchor lookup.",
            "No proof-of-learning claim.",
        ]
        for phrase in blocked_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_archive_memory_minimum_fields_are_preserved(self):
        for phrase in ("文字片段", "來源情境摘要", "信心等級", "使用次數"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
