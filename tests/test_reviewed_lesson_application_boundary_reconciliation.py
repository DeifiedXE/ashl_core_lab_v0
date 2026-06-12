from pathlib import Path
import unittest


DOC_PATH = Path("docs/reviewed_lesson_application_boundary_reconciliation_v0.md")


class ReviewedLessonApplicationBoundaryReconciliationTests(unittest.TestCase):
    def test_design_doc_contains_required_boundaries(self):
        doc = DOC_PATH.read_text(encoding="utf-8")

        required_phrases = [
            "ASHL Core can bridge generic lesson review decisions into the existing reviewed lesson evidence pipeline.",
            "ASHL Core cannot apply lessons from that evidence yet.",
            "lesson_effect_evidence_trace is evidence only",
            "reviewed_lesson_preview is preview only",
            "dry_run_correction is dry-run only",
            "before_after_trial_contrast is contrast only",
            "None of these are application approval",
            "explicit human application approval",
            "application scope defined",
            "rollback path defined",
            "audit trace required",
            "mentor override preserved",
            "allowed_for_runtime_application must remain False",
            "allowed_for_memory_write must remain False",
            "allowed_for_retention_write must remain False",
            "allowed_for_predictor_mutation must remain False",
            "allowed_for_runtime_behavior_change must remain False",
            "would claim proof of learning",
        ]

        missing = [phrase for phrase in required_phrases if phrase not in doc]
        self.assertEqual(missing, [])

    def test_readme_and_research_plan_are_updated(self):
        readme = Path("README.md").read_text(encoding="utf-8")
        research_plan = Path("docs/research_plan.md").read_text(encoding="utf-8")

        self.assertIn("Reviewed Lesson Application Boundary Reconciliation Minimal v0", readme)
        self.assertIn("Reviewed Lesson Application Boundary Reconciliation Minimal v0", research_plan)
        self.assertIn("none of those are application approval", readme)
        self.assertIn("explicit human application approval", research_plan)


if __name__ == "__main__":
    unittest.main()
