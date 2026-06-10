from pathlib import Path
import unittest


DOC_PATH = Path("docs/minimal_lesson_effect_retention_boundary_review_v0.md")


class MinimalLessonEffectRetentionBoundaryReviewTests(unittest.TestCase):
    def test_design_doc_contains_required_boundaries(self):
        doc = DOC_PATH.read_text(encoding="utf-8")

        required_phrases = [
            "Minimal Lesson Effect Retention Boundary Review v0",
            "lesson_effect_evidence_trace is not retained learning",
            "visible_trace_difference is not proof of learning",
            "trace-level evidence is not behavior change",
            "retention requires separate memory / persistence boundary",
            "human approval for retention",
            "rollback / delete path",
            "memory write boundary review",
            "persistence boundary review",
            "This package does not retain anything.",
        ]

        missing = [phrase for phrase in required_phrases if phrase not in doc]
        self.assertEqual(missing, [])

    def test_readme_and_research_plan_are_updated(self):
        readme = Path("README.md").read_text(encoding="utf-8")
        research_plan = Path("docs/research_plan.md").read_text(encoding="utf-8")

        self.assertIn("Minimal Lesson Effect Retention Boundary Review v0", readme)
        self.assertIn("Minimal Lesson Effect Retention Boundary Review v0", research_plan)
        self.assertIn("cannot become retained learning", readme)
        self.assertIn("separate memory/persistence boundary", research_plan)


if __name__ == "__main__":
    unittest.main()
