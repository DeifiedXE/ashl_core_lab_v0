from __future__ import annotations

import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.learning.learning_feedback_to_concept_candidate import (
    LearningFeedbackToConceptCandidateDraftRecord,
)
from ashl_core_v1.learning import feedback_concept_candidate_review_refinement as refinement
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    refine_feedback_concept_candidate_demo_from_guided_cradle_growth_console,
    validate_feedback_concept_candidate_refinement_from_guided_cradle_growth_console,
)


class FeedbackConceptCandidateReviewRefinementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = refinement.build_demo_successful_expected_effect_refinement()
        self.draft = LearningFeedbackToConceptCandidateDraftRecord.from_dict(
            self.payload["learning_feedback_to_concept_candidate_draft"]
        )
        self.review = refinement.FeedbackConceptCandidateReviewRecord.from_dict(
            self.payload["feedback_concept_candidate_review"]
        )
        self.scope = refinement.FeedbackConceptCandidateScopeCheckRecord.from_dict(
            self.payload["feedback_concept_candidate_scope_check"]
        )
        self.counterexample = (
            refinement.FeedbackConceptCandidateCounterexampleCheckRecord.from_dict(
                self.payload["feedback_concept_candidate_counterexample_check"]
            )
        )
        self.refined = refinement.FeedbackConceptCandidateRefinementRecord.from_dict(
            self.payload["feedback_concept_candidate_refinement"]
        )

    def test_review_record_builds_from_package_90_draft(self) -> None:
        self.assertEqual(
            self.review.source_concept_candidate_draft_id,
            self.draft.concept_candidate_draft_id,
        )
        self.assertEqual(
            self.review.source_learning_feedback_candidate_id,
            self.draft.source_learning_feedback_candidate_id,
        )
        self.assertEqual(self.review.proposed_concept_label, self.draft.proposed_concept_label)
        self.assertEqual(self.review.concept_candidate_kind, self.draft.concept_candidate_kind)
        self.assertEqual(self.review.teacher_review_status, "approved_for_refinement")
        self.assertTrue(self.review.approved_for_refinement)
        self.assertTrue(
            refinement.validate_feedback_concept_candidate_review_record(self.review)["valid"]
        )

    def test_review_record_grants_refinement_only(self) -> None:
        self.assertFalse(self.review.approved_for_reviewed_concept)
        self.assertFalse(self.review.approved_for_memory_write)
        self.assertFalse(self.review.approved_for_behavior_change)
        self.assertFalse(self.review.approved_for_action_authority)
        self.assertFalse(self.review.approved_for_automatic_learning_approval)
        self.assertFalse(self.review.reviewed_concept_created)
        self.assertFalse(self.review.memory_write_performed)
        self.assertFalse(self.review.automatic_learning_approval_created)
        self.assertFalse(self.review.task_behavior_changed)

    def test_review_source_validation_rules(self) -> None:
        explicit_blank = refinement.build_feedback_concept_candidate_review_record(
            draft=self.draft,
            teacher_review_status="approved_for_refinement",
            review_source="explicit_teacher_review",
            review_actor_role="teacher",
            teacher_review_text="",
        )
        self.assertIn(
            "explicit_review_requires_teacher_review_text",
            refinement.validate_feedback_concept_candidate_review_record(explicit_blank)[
                "error_codes"
            ],
        )
        explicit_bad_role = refinement.build_feedback_concept_candidate_review_record(
            draft=self.draft,
            teacher_review_status="approved_for_refinement",
            review_source="explicit_teacher_review",
            review_actor_role="system_demo",
            teacher_review_text="teacher approved refinement only",
        )
        self.assertIn(
            "explicit_review_requires_teacher_or_project_owner",
            refinement.validate_feedback_concept_candidate_review_record(explicit_bad_role)[
                "error_codes"
            ],
        )
        demo_bad_role = refinement.build_feedback_concept_candidate_review_record(
            draft=self.draft,
            teacher_review_status="approved_for_refinement",
            review_source="demo_review",
            review_actor_role="teacher",
        )
        self.assertIn(
            "demo_review_requires_system_demo_role",
            refinement.validate_feedback_concept_candidate_review_record(demo_bad_role)[
                "error_codes"
            ],
        )

    def test_scope_check_preserves_and_bounds_scope(self) -> None:
        self.assertEqual(
            self.scope.source_concept_candidate_draft_id,
            self.draft.concept_candidate_draft_id,
        )
        self.assertEqual(self.scope.scope_check_status, "scope_valid_for_refinement")
        self.assertTrue(self.scope.scope_is_context_bound)
        self.assertTrue(self.scope.scope_requires_sandbox_context)
        self.assertFalse(self.scope.reviewed_concept_created)
        self.assertFalse(self.scope.memory_write_performed)
        self.assertTrue(
            refinement.validate_feedback_concept_candidate_scope_check_record(self.scope)[
                "valid"
            ]
        )

    def test_scope_check_detects_too_broad_scope(self) -> None:
        payload = refinement.build_demo_blocked_scope_too_broad_refinement()
        scope = payload["feedback_concept_candidate_scope_check"]
        audit = payload["feedback_concept_candidate_refinement_safety_audit"]
        self.assertEqual(scope["scope_check_status"], "scope_too_broad")
        self.assertIn("scope_too_broad", scope["scope_warning_labels"])
        self.assertEqual(audit["audit_status"], "blocked_invalid_scope_check")

    def test_counterexample_check_passes_no_counterexamples(self) -> None:
        self.assertEqual(
            self.counterexample.counterexample_check_status,
            "counterexample_check_passed_no_counterexamples",
        )
        self.assertTrue(self.counterexample.has_support_evidence)
        self.assertFalse(self.counterexample.has_counterexamples)
        self.assertTrue(
            refinement.validate_feedback_concept_candidate_counterexample_check_record(
                self.counterexample
            )["valid"]
        )

    def test_counterexample_check_requires_scope_narrowing_when_handled(self) -> None:
        check = refinement.build_feedback_concept_candidate_counterexample_check_record(
            draft=self.draft,
            review=self.review,
            scope_check=self.scope,
            counterexample_refs=("counterexample:changed_context",),
            counterexample_notes=("requires narrower direct-command context",),
        )
        record = refinement.build_feedback_concept_candidate_refinement_record(
            draft=self.draft,
            review=self.review,
            scope_check=self.scope,
            counterexample_check=check,
        )
        self.assertEqual(
            check.counterexample_check_status,
            "counterexample_check_requires_scope_narrowing",
        )
        self.assertEqual(record.refinement_status, "held_for_more_evidence")

    def test_counterexample_check_recommends_split(self) -> None:
        check = refinement.build_feedback_concept_candidate_counterexample_check_record(
            draft=self.draft,
            review=self.review,
            scope_check=self.scope,
            counterexample_refs=("counterexample:split",),
            counterexample_notes=("same command needs distinct context",),
            requires_split=True,
        )
        record = refinement.build_feedback_concept_candidate_refinement_record(
            draft=self.draft,
            review=self.review,
            scope_check=self.scope,
            counterexample_check=check,
        )
        self.assertEqual(record.refinement_status, "split_recommended")
        self.assertTrue(record.split_recommended)
        self.assertTrue(record.split_candidate_labels)

    def test_counterexample_check_blocks_unhandled_counterexamples(self) -> None:
        payload = refinement.build_demo_blocked_unhandled_counterexample_refinement()
        counterexample = payload["feedback_concept_candidate_counterexample_check"]
        record = payload["feedback_concept_candidate_refinement"]
        audit = payload["feedback_concept_candidate_refinement_safety_audit"]
        self.assertEqual(
            counterexample["counterexample_check_status"],
            "counterexample_check_blocked_unhandled_counterexamples",
        )
        self.assertEqual(record["refinement_status"], "blocked_unhandled_counterexamples")
        self.assertEqual(audit["audit_status"], "blocked_invalid_counterexample_check")

    def test_refinement_record_preserves_source_fields(self) -> None:
        self.assertEqual(
            self.refined.source_concept_candidate_draft_id,
            self.draft.concept_candidate_draft_id,
        )
        self.assertEqual(self.refined.original_concept_label, self.draft.proposed_concept_label)
        self.assertEqual(self.refined.original_concept_scope, self.draft.proposed_concept_scope)
        self.assertEqual(
            self.refined.original_concept_candidate_kind,
            self.draft.concept_candidate_kind,
        )
        self.assertEqual(self.refined.support_evidence_refs, self.counterexample.support_evidence_refs)
        self.assertTrue(
            refinement.validate_feedback_concept_candidate_refinement_record(self.refined)[
                "valid"
            ]
        )

    def test_refinement_record_creates_refined_candidate_only(self) -> None:
        self.assertEqual(self.refined.refinement_status, "refined_concept_candidate_created")
        self.assertTrue(self.refined.available_for_reviewed_concept_preparation_later)
        self.assertTrue(self.refined.rollback_available)
        self.assertFalse(self.refined.reviewed_concept_created)
        self.assertFalse(self.refined.memory_write_performed)
        self.assertFalse(self.refined.automatic_learning_approval_created)
        self.assertFalse(self.refined.task_behavior_changed)
        self.assertFalse(self.refined.candidate_ordering_changed)
        self.assertFalse(self.refined.selected_action_changed)
        self.assertFalse(self.refined.final_action_changed)
        self.assertFalse(self.refined.direct_command_created)
        self.assertFalse(self.refined.execution_created)

    def test_refinement_maps_demo_outcome_classes(self) -> None:
        cases = {
            "successful-expected-effect": "sandbox_positive_affordance_",
            "failed-expected-effect": "sandbox_negative_affordance_",
            "goal-reached": "sandbox_goal_completion_by_",
            "no-progress": "sandbox_no_progress_",
            "observation-only": "sandbox_observation_context_",
        }
        for case, label_prefix in cases.items():
            with self.subTest(case=case):
                payload = refinement.build_demo_feedback_concept_candidate_refinement_case(case)
                record = payload["feedback_concept_candidate_refinement"]
                self.assertEqual(
                    record["refinement_status"],
                    "refined_concept_candidate_created",
                )
                self.assertTrue(record["refined_concept_label"].startswith(label_prefix))

    def test_held_and_conflict_cases_do_not_create_refined_candidate(self) -> None:
        unknown = refinement.build_demo_unknown_outcome_held_refinement()
        system_fault = refinement.build_demo_system_fault_blocked_refinement()
        self.assertEqual(
            unknown["feedback_concept_candidate_refinement"]["refinement_status"],
            "held_for_more_evidence",
        )
        self.assertEqual(
            system_fault["feedback_concept_candidate_refinement"]["refinement_status"],
            "conflict_detected",
        )
        self.assertFalse(
            unknown["feedback_concept_candidate_refinement"][
                "available_for_reviewed_concept_preparation_later"
            ]
        )
        self.assertFalse(
            system_fault["feedback_concept_candidate_refinement"][
                "available_for_reviewed_concept_preparation_later"
            ]
        )

    def test_invalid_draft_and_missing_review_block_refinement(self) -> None:
        invalid = refinement.build_demo_blocked_invalid_concept_candidate_draft_refinement()
        missing = refinement.build_demo_blocked_missing_teacher_review_refinement()
        self.assertEqual(
            invalid["feedback_concept_candidate_refinement"]["refinement_status"],
            "blocked_invalid_review",
        )
        self.assertEqual(
            invalid["feedback_concept_candidate_refinement_safety_audit"]["audit_status"],
            "blocked_invalid_feedback_concept_candidate_draft",
        )
        self.assertEqual(
            missing["feedback_concept_candidate_refinement"]["refinement_status"],
            "blocked_invalid_review",
        )
        self.assertEqual(
            missing["feedback_concept_candidate_refinement_safety_audit"]["audit_status"],
            "blocked_invalid_review",
        )

    def test_teacher_rejected_review_does_not_refine(self) -> None:
        payload = refinement.build_demo_blocked_teacher_rejected_refinement()
        self.assertEqual(
            payload["feedback_concept_candidate_review"]["teacher_review_status"],
            "rejected",
        )
        self.assertEqual(
            payload["feedback_concept_candidate_refinement"]["refinement_status"],
            "rejected_by_review",
        )
        self.assertEqual(
            payload["feedback_concept_candidate_refinement_safety_audit"]["audit_status"],
            "passed_all_held_or_blocked",
        )

    def test_review_set_counts_refined_held_and_blocked_records(self) -> None:
        success = refinement.build_demo_successful_expected_effect_refinement()
        held = refinement.build_demo_unknown_outcome_held_refinement()
        blocked = refinement.build_demo_blocked_unhandled_counterexample_refinement()
        review_set = refinement.build_feedback_concept_candidate_review_set(
            reviews=tuple(
                item["feedback_concept_candidate_review"]
                for item in (success, held, blocked)
                if item["feedback_concept_candidate_review"] is not None
            ),
            scope_checks=tuple(
                item["feedback_concept_candidate_scope_check"]
                for item in (success, held, blocked)
            ),
            counterexample_checks=tuple(
                item["feedback_concept_candidate_counterexample_check"]
                for item in (success, held, blocked)
            ),
            refinements=tuple(
                item["feedback_concept_candidate_refinement"]
                for item in (success, held, blocked)
            ),
        )
        self.assertEqual(review_set.refined_count, 1)
        self.assertEqual(review_set.held_count, 1)
        self.assertEqual(review_set.blocked_count, 1)
        self.assertEqual(
            review_set.review_set_status,
            "review_set_created_with_refined_candidates",
        )
        self.assertTrue(
            refinement.validate_feedback_concept_candidate_review_set(review_set)["valid"]
        )

    def test_safety_audit_passes_for_valid_demo(self) -> None:
        audit = self.payload["feedback_concept_candidate_refinement_safety_audit"]
        validation = refinement.validate_feedback_concept_candidate_refinement_safety_audit(
            audit
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(
            audit["audit_status"],
            "passed_feedback_concept_candidate_refinement_only",
        )
        self.assertTrue(audit["refinement_only_confirmed"])
        self.assertTrue(audit["no_reviewed_concept_creation"])
        self.assertTrue(audit["no_memory_write"])
        self.assertTrue(audit["no_automatic_learning_approval"])
        self.assertTrue(audit["no_task_behavior_change"])

    def test_safety_audit_blocks_forbidden_authority_cases(self) -> None:
        cases = {
            "reviewed-concept-created": "blocked_reviewed_concept_creation_detected",
            "memory-write-detected": "blocked_memory_write_detected",
            "automatic-learning-approval": "blocked_automatic_learning_approval_detected",
            "action-authority-detected": "blocked_action_authority_detected",
            "behavior-change-detected": "blocked_behavior_change_detected",
        }
        for case, expected_status in cases.items():
            with self.subTest(case=case):
                payload = refinement.build_demo_blocked_feedback_concept_candidate_refinement(
                    case
                )
                audit = payload["feedback_concept_candidate_refinement_safety_audit"]
                self.assertEqual(audit["audit_status"], expected_status)

    def test_refinement_validation_detects_forbidden_authority(self) -> None:
        record = replace(self.refined, selected_action_changed=True)
        validation = refinement.validate_feedback_concept_candidate_refinement_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("forbidden_authority_detected", validation["error_codes"])

    def test_cli_commands_work(self) -> None:
        commands = (
            ("refine-demo-candidate",),
            ("show-demo-review",),
            ("show-demo-scope-check",),
            ("show-demo-counterexample-check",),
            ("show-demo-refinement",),
            ("show-demo-safety-audit",),
            ("validate-demo-refinement",),
            ("refine-demo-case", "--case", "successful-expected-effect"),
            ("refine-demo-case", "--case", "failed-expected-effect"),
            ("refine-demo-case", "--case", "goal-reached"),
            ("refine-demo-case", "--case", "no-progress"),
            ("refine-demo-case", "--case", "observation-only"),
            ("refine-demo-case", "--case", "unknown-outcome"),
            ("refine-demo-case", "--case", "system-fault"),
            ("refine-demo-blocked", "--case", "invalid-concept-candidate-draft"),
            ("refine-demo-blocked", "--case", "missing-teacher-review"),
            ("refine-demo-blocked", "--case", "teacher-rejected"),
            ("refine-demo-blocked", "--case", "scope-too-broad"),
            ("refine-demo-blocked", "--case", "unhandled-counterexample"),
            ("refine-demo-blocked", "--case", "reviewed-concept-created"),
            ("refine-demo-blocked", "--case", "memory-write-detected"),
            ("refine-demo-blocked", "--case", "automatic-learning-approval"),
            ("refine-demo-blocked", "--case", "action-authority-detected"),
            ("refine-demo-blocked", "--case", "behavior-change-detected"),
        )
        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "ashl_core_v1.learning.feedback_concept_candidate_review_refinement_cli",
                        *command,
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(json.loads(result.stdout))

    def test_guided_console_demo_and_validation_work(self) -> None:
        payload = refine_feedback_concept_candidate_demo_from_guided_cradle_growth_console()
        validation = validate_feedback_concept_candidate_refinement_from_guided_cradle_growth_console()
        self.assertEqual(
            payload["guided_console_action"],
            "learning_refine_feedback_concept_candidate_demo",
        )
        self.assertFalse(payload["reviewed_concept_created"])
        self.assertFalse(payload["memory_write_performed"])
        self.assertFalse(payload["automatic_learning_approval_created"])
        self.assertFalse(payload["task_behavior_changed"])
        self.assertTrue(validation["validation"]["valid"])

    def test_guided_console_cli_command_works(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli",
                "learning-validate-feedback-concept-candidate-refinement",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertTrue(payload["validation"]["valid"])
        self.assertFalse(payload["reviewed_concept_created"])
        self.assertFalse(payload["memory_write_performed"])

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())


if __name__ == "__main__":
    unittest.main()
