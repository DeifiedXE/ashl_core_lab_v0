from __future__ import annotations

import unittest
from pathlib import Path


DOC_PATH = Path("ashl_core_v1/docs/learning_engine_architecture_v0.md")


class LearningEngineArchitectureV0DocTests(unittest.TestCase):
    def test_learning_engine_architecture_doc_exists(self) -> None:
        self.assertTrue(DOC_PATH.is_file())

    def test_document_defines_learning_engine_as_independent(self) -> None:
        text = self._doc()
        self.assertIn("Learning Engine is independent", text)
        self.assertIn("Learning Engine is not:", text)
        self.assertIn("Task Engine", text)
        self.assertIn("Memory Engine", text)
        self.assertIn("Thought Engine", text)

    def test_document_contains_updated_runtime_engine_map_with_learning_engine(self) -> None:
        text = self._doc()
        self.assertIn("Runtime", text)
        self.assertIn("├── Learning Engine", text)
        self.assertIn("├── State Engine", text)
        self.assertIn("├── Memory Engine", text)

    def test_document_contains_english_concept_definition(self) -> None:
        self.assertIn(
            "Concept = a teacher-reviewed experience difference",
            self._doc(),
        )

    def test_document_contains_chinese_concept_definition(self) -> None:
        self.assertIn(
            "概念 = 會改變下一次任務處理的、被審查過、且經過反例檢查的經驗差異",
            self._doc(),
        )

    def test_document_says_counterexamples_are_not_automatic_deletion(self) -> None:
        self.assertIn("Counterexamples are not automatic deletion.", self._doc())

    def test_document_lists_invalidate_narrow_split_outcomes(self) -> None:
        text = self._doc()
        self.assertIn("1. invalidate concept", text)
        self.assertIn("2. narrow concept scope", text)
        self.assertIn("3. split concept into more specific candidates", text)

    def test_document_includes_front_blocked_example(self) -> None:
        text = self._doc()
        self.assertIn("front_blocked + step_forward -> blocked", text)
        self.assertIn("front_blocked + step_forward -> success", text)
        self.assertIn("front_wall_blocked", text)

    def test_document_includes_minimum_concept_candidate_shape(self) -> None:
        text = self._doc()
        self.assertIn("ConceptCandidate", text)
        self.assertIn("support_evidence_refs", text)
        self.assertIn("counterexample_evidence_refs", text)
        self.assertIn("scope_statement", text)
        self.assertIn("teacher_review_required", text)

    def test_document_says_no_runtime_behavior_added(self) -> None:
        self.assertIn("Learning Engine v0 does not add runtime behavior.", self._doc())

    def test_document_says_no_memory_write_added(self) -> None:
        text = self._doc()
        self.assertIn("does not directly write Core, Long-term, Archive, or Anchor memory", text)

    def test_document_recommends_package_61(self) -> None:
        self.assertIn(
            "Package 61 / ASHL Core v1 Learning Engine Concept Candidate Architecture And Schema Minimal v0",
            self._doc(),
        )

    def _doc(self) -> str:
        return DOC_PATH.read_text(encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
