from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
    ConceptCandidateDraftRecord,
    SimpleConceptTeachingTestSeedRecord,
    TaskClosureConceptDraftSourceRecord,
    build_demo_blocked_task_closure_source,
    build_demo_conflict_task_closure_source,
    build_demo_draft,
    build_demo_success_task_closure_source,
    build_demo_teacher_stopped_source,
    build_demo_teaching_test_seed,
    build_demo_unknown_task_closure_source,
    build_demo_unknown_vs_unknown_blocked_source,
    build_simple_concept_teaching_test_seed,
    draft_concept_candidate_from_task_closure_source,
    validate_concept_candidate_draft_record,
    validate_simple_concept_teaching_test_seed,
    validate_task_closure_concept_draft_source,
)


class ConceptCandidateFromTaskClosureDraftTests(unittest.TestCase):
    def test_build_blocked_task_closure_draft_source_succeeds(self) -> None:
        source = build_demo_blocked_task_closure_source()
        validation = validate_task_closure_concept_draft_source(source)
        self.assertTrue(validation["valid"])
        self.assertTrue(source.draftable_as_concept_candidate)

    def test_blocked_task_closure_drafts_front_blocked_affordance(self) -> None:
        draft = build_demo_draft("blocked")
        self.assertEqual(draft.draft_status, "draft_created")
        self.assertIsNotNone(draft.drafted_concept_candidate)
        self.assertEqual(
            draft.drafted_concept_candidate.concept_label,
            "front_blocked_affordance",
        )

    def test_blocked_draft_creates_support_evidence_ref(self) -> None:
        candidate = build_demo_draft("blocked").drafted_concept_candidate
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate.support_evidence_refs[0].state_summary, "front_blocked")
        self.assertTrue(candidate.support_evidence_refs[0].supports_candidate)

    def test_blocked_draft_creates_teaching_test_seed(self) -> None:
        seed = build_demo_teaching_test_seed("blocked")
        validation = validate_simple_concept_teaching_test_seed(seed)
        self.assertTrue(validation["valid"])
        self.assertEqual(seed.test_status, "seed_created")

    def test_success_task_closure_drafts_visible_front_item_reachable(self) -> None:
        source = build_demo_success_task_closure_source()
        draft = draft_concept_candidate_from_task_closure_source(source)
        self.assertEqual(
            draft.drafted_concept_candidate.concept_label,
            "visible_front_item_reachable",
        )

    def test_unknown_task_closure_drafts_unknown_front_state_requires_observe(self) -> None:
        source = build_demo_unknown_task_closure_source()
        draft = draft_concept_candidate_from_task_closure_source(source)
        self.assertEqual(
            draft.drafted_concept_candidate.concept_label,
            "unknown_front_state_requires_observe",
        )
        self.assertTrue(draft.teacher_review_ready)

    def test_conflict_task_closure_drafts_expected_actual_mismatch(self) -> None:
        source = build_demo_conflict_task_closure_source()
        draft = draft_concept_candidate_from_task_closure_source(source)
        self.assertEqual(
            draft.drafted_concept_candidate.concept_label,
            "expected_actual_mismatch_requires_verification",
        )
        self.assertTrue(draft.teacher_review_ready)

    def test_teacher_stopped_drafts_boundary_control_candidate(self) -> None:
        source = build_demo_teacher_stopped_source()
        draft = draft_concept_candidate_from_task_closure_source(source)
        self.assertEqual(
            draft.drafted_concept_candidate.concept_label,
            "teacher_boundary_requires_stop_or_wait",
        )
        self.assertEqual(draft.drafted_concept_candidate.generalization_level, "single_case")

    def test_unknown_vs_unknown_source_blocks_draft(self) -> None:
        source = build_demo_unknown_vs_unknown_blocked_source()
        self.assertFalse(source.draftable_as_concept_candidate)
        self.assertEqual(source.draft_blocked_reason, "unknown_vs_unknown_not_valid")
        draft = draft_concept_candidate_from_task_closure_source(source)
        self.assertEqual(draft.draft_status, "blocked_unknown_vs_unknown")
        self.assertIsNone(draft.drafted_concept_candidate)

    def test_draft_record_validates_concept_candidate_from_package_61(self) -> None:
        validation = validate_concept_candidate_draft_record(build_demo_draft("blocked"))
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_draft_record_teacher_review_required_true(self) -> None:
        draft = build_demo_draft("blocked")
        self.assertTrue(draft.teacher_review_required)

    def test_draft_record_automatic_approval_created_false(self) -> None:
        validation = validate_concept_candidate_draft_record(build_demo_draft("blocked"))
        self.assertFalse(validation["automatic_approval_created"])

    def test_draft_record_memory_write_performed_false(self) -> None:
        validation = validate_concept_candidate_draft_record(build_demo_draft("blocked"))
        self.assertFalse(validation["memory_write_performed"])

    def test_draft_record_task_behavior_changed_false(self) -> None:
        validation = validate_concept_candidate_draft_record(build_demo_draft("blocked"))
        self.assertFalse(validation["task_behavior_changed"])

    def test_draft_record_concept_extraction_runtime_created_false(self) -> None:
        validation = validate_concept_candidate_draft_record(build_demo_draft("blocked"))
        self.assertFalse(validation["concept_extraction_runtime_created"])

    def test_teaching_test_seed_asks_about_support_evidence(self) -> None:
        seed = build_demo_teaching_test_seed("blocked")
        questions = " ".join(seed.teacher_expected_questions).lower()
        self.assertIn("support evidence", questions)

    def test_teaching_test_seed_asks_about_counterexample_evidence(self) -> None:
        seed = build_demo_teaching_test_seed("blocked")
        questions = " ".join(seed.teacher_expected_questions).lower()
        self.assertIn("counterexample", questions)

    def test_teaching_test_seed_asks_about_overbroad_scope(self) -> None:
        seed = build_demo_teaching_test_seed("blocked")
        self.assertIn("too broad", seed.teacher_visible_prompt.lower())
        self.assertIn("overbroad_scope", seed.expected_teacher_focus)

    def test_teaching_test_seed_does_not_create_teacher_decision(self) -> None:
        seed = build_demo_teaching_test_seed("blocked")
        self.assertTrue(seed.does_not_create_review_decision)

    def test_teaching_test_seed_does_not_approve_concept(self) -> None:
        seed = build_demo_teaching_test_seed("blocked")
        self.assertTrue(seed.does_not_approve_concept)

    def test_teaching_test_seed_does_not_write_memory(self) -> None:
        seed = build_demo_teaching_test_seed("blocked")
        self.assertTrue(seed.does_not_write_memory)

    def test_teaching_test_seed_does_not_change_task_behavior(self) -> None:
        seed = build_demo_teaching_test_seed("blocked")
        self.assertTrue(seed.does_not_change_task_behavior)

    def test_invalid_draft_source_blocks_validation(self) -> None:
        source = self._mutated_source(build_demo_blocked_task_closure_source(), source_task_id="")
        validation = validate_task_closure_concept_draft_source(source)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_task_id", validation["error_codes"])

    def test_invalid_draft_record_blocks_memory_write_flag(self) -> None:
        draft = self._mutated_draft(build_demo_draft("blocked"), memory_write_performed=True)
        validation = validate_concept_candidate_draft_record(draft)
        self.assertFalse(validation["valid"])
        self.assertIn("memory_write_performed_true", validation["error_codes"])

    def test_invalid_teaching_seed_blocks_review_decision_creation(self) -> None:
        seed = self._mutated_seed(
            build_demo_teaching_test_seed("blocked"),
            does_not_create_review_decision=False,
        )
        validation = validate_simple_concept_teaching_test_seed(seed)
        self.assertFalse(validation["valid"])
        self.assertIn("does_not_create_review_decision_false", validation["error_codes"])

    def test_cli_draft_demo_blocked_works(self) -> None:
        result = self._run_learning_cli("draft-demo-blocked")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("front_blocked_affordance", result.stdout)

    def test_cli_draft_demo_success_works(self) -> None:
        result = self._run_learning_cli("draft-demo-success")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("visible_front_item_reachable", result.stdout)

    def test_cli_draft_demo_unknown_works(self) -> None:
        result = self._run_learning_cli("draft-demo-unknown")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("unknown_front_state_requires_observe", result.stdout)

    def test_cli_draft_demo_conflict_works(self) -> None:
        result = self._run_learning_cli("draft-demo-conflict")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("expected_actual_mismatch_requires_verification", result.stdout)

    def test_cli_draft_demo_teacher_stopped_works(self) -> None:
        result = self._run_learning_cli("draft-demo-teacher-stopped")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("teacher_boundary_requires_stop_or_wait", result.stdout)

    def test_cli_draft_demo_unknown_vs_unknown_shows_blocked_status(self) -> None:
        result = self._run_learning_cli("draft-demo-unknown-vs-unknown")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_unknown_vs_unknown", result.stdout)

    def test_cli_show_teaching_test_seed_works(self) -> None:
        result = self._run_learning_cli(
            "show-teaching-test-seed",
            "--demo",
            "blocked",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("teaching_test_seed_id", result.stdout)

    def test_cli_validate_demo_works(self) -> None:
        result = self._run_learning_cli("validate-demo", "--demo", "blocked")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_guided_console_learning_draft_demo_concept_works(self) -> None:
        result = self._run_guided_cli(
            "learning-draft-demo-concept",
            "--demo",
            "blocked",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("front_blocked_affordance", result.stdout)

    def test_guided_console_learning_show_teaching_test_seed_works(self) -> None:
        result = self._run_guided_cli(
            "learning-show-teaching-test-seed",
            "--demo",
            "blocked",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("teaching_test_seed", result.stdout)

    def test_guided_console_learning_validate_demo_draft_works(self) -> None:
        result = self._run_guided_cli(
            "learning-validate-demo-draft",
            "--demo",
            "blocked",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_draft("blocked")
        build_demo_teaching_test_seed("blocked")
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _mutated_source(
        self,
        source: TaskClosureConceptDraftSourceRecord,
        **changes: object,
    ) -> TaskClosureConceptDraftSourceRecord:
        data = source.to_dict()
        data.update(changes)
        return TaskClosureConceptDraftSourceRecord.from_dict(data)

    def _mutated_draft(
        self,
        draft: ConceptCandidateDraftRecord,
        **changes: object,
    ) -> ConceptCandidateDraftRecord:
        data = draft.to_dict()
        data.update(changes)
        return ConceptCandidateDraftRecord.from_dict(data)

    def _mutated_seed(
        self,
        seed: SimpleConceptTeachingTestSeedRecord,
        **changes: object,
    ) -> SimpleConceptTeachingTestSeedRecord:
        data = seed.to_dict()
        data.update(changes)
        return SimpleConceptTeachingTestSeedRecord.from_dict(data)

    def _run_learning_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.learning.concept_candidate_from_task_closure_draft_cli",
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _run_guided_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli",
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
