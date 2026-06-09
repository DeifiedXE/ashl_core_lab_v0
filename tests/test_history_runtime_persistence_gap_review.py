import unittest
from pathlib import Path


class HistoryRuntimePersistenceGapReviewTests(unittest.TestCase):
    def setUp(self):
        self.doc_path = Path("docs/history_runtime_persistence_gap_review_v0.md")
        self.doc = self.doc_path.read_text(encoding="utf-8")

    def test_review_document_exists(self):
        self.assertTrue(self.doc_path.exists())
        self.assertIn("History Runtime Persistence Gap Review v0", self.doc)

    def test_terms_are_clearly_distinguished(self):
        for phrase in [
            "Session Working Memory",
            "Generalized Memory Exact-Key Bucket",
            "cross-session demo experience records",
            "history runtime",
            "persistent history store",
            "Long-term Memory",
            "Memory Layer",
            "Persistent learning",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_gap_conclusion_is_recorded(self):
        for phrase in [
            "not a true persisted history runtime",
            "The current Generalized Memory line demonstrates exact-key aggregation over cross-session demo experience records, not a true persisted history runtime.",
            "cross-session demo experience records are fixtures",
            "cross-session storage and persistent storage were not added",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_repetition_key_gap_is_recorded(self):
        for phrase in [
            "repetition_key = not_evaluated",
            "A bucket can aggregate records if records are already present.",
            "it cannot itself retain session A records into session B",
            "demo cross-session aggregation does not solve real repetition_key evaluation",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_missing_layer_is_recorded(self):
        for phrase in [
            "session experience record",
            "retention / commit policy",
            "persisted history store",
            "exact-key lookup by repetition_key / similar_context_key",
            "bucket aggregation",
            "read-only evidence for review",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_boundaries_and_next_options_are_recorded(self):
        for phrase in [
            "Do not add storage in this package.",
            "Do not write memory in this package.",
            "Do not enable persistent learning.",
            "Do not mutate predictor behavior.",
            "Do not influence action selection.",
            "Option B: Session Experience Record Schema Design v0",
            "Option C: History Retention Boundary Review v0",
            "Option D: Generalized Memory Exact-Key Bucket Source Audit v0",
            "Recommended immediate next package:",
            "Session Experience Record Schema Design v0",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_readme_and_research_plan_are_updated(self):
        readme = Path("README.md").read_text(encoding="utf-8")
        research_plan = Path("docs/research_plan.md").read_text(encoding="utf-8")

        self.assertIn("History Runtime Persistence Gap Review v0", readme)
        self.assertIn("History Runtime Persistence Gap Review v0", research_plan)
        self.assertIn("does not yet prove a persisted history runtime", readme)
        self.assertIn("recommends Session Experience Record Schema Design v0", research_plan)


if __name__ == "__main__":
    unittest.main()
