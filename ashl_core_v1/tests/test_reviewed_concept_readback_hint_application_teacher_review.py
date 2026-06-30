from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.task.reviewed_concept_readback_hint_application_preview import (
    TaskWorkingMemoryReadbackHintApplicationPreviewSet,
    build_demo_all_held_task_working_memory_readback_hint_application_preview_set,
    build_demo_task_working_memory_readback_hint_application_preview_set,
)
from ashl_core_v1.task.reviewed_concept_readback_hint_application_teacher_review import (
    TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview,
    TaskWorkingMemoryReadbackHintApplicationTeacherReview,
    TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit,
    build_demo_all_held_task_working_memory_readback_hint_application_teacher_review,
    build_demo_blocked_forbidden_authority_application_review,
    build_demo_blocked_invalid_review_source,
    build_demo_conflict_detected_task_working_memory_readback_hint_application_teacher_review,
    build_demo_rejected_task_working_memory_readback_hint_application_teacher_review,
    build_demo_task_working_memory_readback_hint_application_teacher_review,
    build_task_working_memory_readback_hint_application_teacher_review,
    build_task_working_memory_readback_hint_application_teacher_review_bundle,
    build_task_working_memory_readback_hint_application_teacher_review_safety_audit,
    validate_task_working_memory_readback_hint_application_preview_set_teacher_review,
    validate_task_working_memory_readback_hint_application_teacher_review,
    validate_task_working_memory_readback_hint_application_teacher_review_safety_audit,
)


APPROVED = "approved_for_future_working_memory_application_preparation"


class ReviewedConceptReadbackHintApplicationTeacherReviewTests(unittest.TestCase):
    def test_application_teacher_review_builds_from_valid_application_preview(self) -> None:
        review = self._review_for_first_preview(APPROVED)
        validation = validate_task_working_memory_readback_hint_application_teacher_review(
            review
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_application_teacher_review_preserves_reviewed_concept_id(self) -> None:
        review = self._review_for_first_preview(APPROVED)
        self.assertEqual(
            review.source_reviewed_concept_id,
            self._preview_payload()[
                "task_working_memory_readback_hint_application_preview_set"
            ]["source_reviewed_concept_id"],
        )

    def test_application_teacher_review_preserves_application_preview_id(self) -> None:
        preview = self._first_preview()
        review = self._review_for_first_preview(APPROVED)
        self.assertEqual(
            review.source_hint_application_preview_id,
            preview["hint_application_preview_id"],
        )

    def test_application_teacher_review_preserves_hint_record_id(self) -> None:
        preview = self._first_preview()
        review = self._review_for_first_preview(APPROVED)
        self.assertEqual(
            review.source_task_working_memory_readback_hint_id,
            preview["source_task_working_memory_readback_hint_id"],
        )

    def test_application_teacher_review_preserves_hint_label(self) -> None:
        self.assertEqual(
            self._review_for_first_preview(APPROVED).hint_label,
            "observe_before_direct_retry",
        )

    def test_application_teacher_review_preserves_proposed_working_memory_slot(self) -> None:
        self.assertEqual(
            self._review_for_first_preview(APPROVED).proposed_working_memory_slot,
            "readback_hints",
        )

    def test_application_teacher_review_preserves_proposed_application_scope(self) -> None:
        self.assertEqual(
            self._review_for_first_preview(APPROVED).proposed_application_scope,
            "future_task_initialization",
        )

    def test_application_teacher_review_preserves_proposed_visibility(self) -> None:
        self.assertEqual(
            self._review_for_first_preview(APPROVED).proposed_visibility,
            "advisory_only",
        )

    def test_application_teacher_review_preserves_proposed_lifetime(self) -> None:
        self.assertEqual(
            self._review_for_first_preview(APPROVED).proposed_lifetime,
            "single_task",
        )

    def test_approved_review_sets_future_application_preparation_true(self) -> None:
        self.assertTrue(
            self._review_for_first_preview(
                APPROVED
            ).approved_for_future_working_memory_application_preparation
        )

    def test_approved_review_keeps_active_application_false(self) -> None:
        review = self._review_for_first_preview(APPROVED)
        self.assertFalse(review.approved_for_active_hint_application)
        self.assertFalse(review.applied_to_working_memory)

    def test_approved_review_keeps_working_memory_mutation_false(self) -> None:
        review = self._review_for_first_preview(APPROVED)
        self.assertFalse(review.approved_for_working_memory_mutation)
        self.assertFalse(review.working_memory_mutated)

    def test_approved_review_keeps_candidate_ordering_change_false(self) -> None:
        review = self._review_for_first_preview(APPROVED)
        self.assertFalse(review.approved_for_candidate_ordering_change)
        self.assertFalse(review.candidate_ordering_changed)

    def test_approved_review_keeps_task_behavior_change_false(self) -> None:
        review = self._review_for_first_preview(APPROVED)
        self.assertFalse(review.approved_for_task_behavior_change)
        self.assertFalse(review.task_behavior_changed)

    def test_approved_review_keeps_action_authority_false(self) -> None:
        review = self._review_for_first_preview(APPROVED)
        self.assertFalse(review.approved_for_selected_action_change)
        self.assertFalse(review.approved_for_final_action_change)
        self.assertFalse(review.approved_for_direct_command_change)
        self.assertFalse(review.approved_for_execution)
        self.assertFalse(review.selected_action_changed)
        self.assertFalse(review.final_action_changed)
        self.assertFalse(review.direct_command_changed)
        self.assertFalse(review.execution_created)

    def test_held_review_does_not_approve_future_application_preparation(self) -> None:
        self.assertFalse(
            self._review_for_first_preview(
                "held_for_more_evidence"
            ).approved_for_future_working_memory_application_preparation
        )

    def test_rejected_review_does_not_approve_future_application_preparation(self) -> None:
        self.assertFalse(
            self._review_for_first_preview(
                "rejected"
            ).approved_for_future_working_memory_application_preparation
        )

    def test_needs_more_evidence_review_does_not_approve_future_application_preparation(self) -> None:
        self.assertFalse(
            self._review_for_first_preview(
                "needs_more_evidence"
            ).approved_for_future_working_memory_application_preparation
        )

    def test_conflict_detected_review_does_not_approve_future_application_preparation(self) -> None:
        self.assertFalse(
            self._review_for_first_preview(
                "conflict_detected"
            ).approved_for_future_working_memory_application_preparation
        )

    def test_explicit_teacher_review_requires_non_empty_text(self) -> None:
        review = self._review_for_first_preview(
            APPROVED,
            review_source="explicit_teacher_review",
            review_actor="teacher",
            review_actor_role="teacher",
            teacher_review_text="",
        )
        validation = validate_task_working_memory_readback_hint_application_teacher_review(
            review
        )
        self.assertIn("missing_teacher_review_text", validation["error_codes"])

    def test_explicit_teacher_review_requires_teacher_or_project_owner_role(self) -> None:
        review = self._review_for_first_preview(
            APPROVED,
            review_source="explicit_teacher_review",
            review_actor="demo",
            review_actor_role="system_demo",
            teacher_review_text="Explicitly approve for future preparation.",
        )
        validation = validate_task_working_memory_readback_hint_application_teacher_review(
            review
        )
        self.assertIn("invalid_explicit_review_actor_role", validation["error_codes"])

    def test_demo_review_requires_system_demo_actor_role(self) -> None:
        review = self._review_for_first_preview(
            APPROVED,
            review_source="demo_review",
            review_actor="teacher_demo",
            review_actor_role="teacher",
        )
        validation = validate_task_working_memory_readback_hint_application_teacher_review(
            review
        )
        self.assertIn("invalid_demo_review_actor_role", validation["error_codes"])

    def test_preview_set_teacher_review_builds_from_valid_preview_set(self) -> None:
        set_review = self._valid_set_review()
        validation = validate_task_working_memory_readback_hint_application_preview_set_teacher_review(
            set_review
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_preview_set_review_preserves_preview_count(self) -> None:
        set_review = self._valid_set_review()
        preview_set = self._valid_preview_set()
        self.assertEqual(set_review.preview_count, len(preview_set.application_previews))

    def test_preview_set_review_lists_approved_preview_ids(self) -> None:
        self.assertEqual(len(self._valid_set_review().approved_preview_ids), 2)

    def test_preview_set_review_lists_held_preview_ids(self) -> None:
        self.assertEqual(len(self._valid_set_review().held_preview_ids), 1)

    def test_preview_set_review_lists_rejected_preview_ids(self) -> None:
        payload = (
            build_demo_rejected_task_working_memory_readback_hint_application_teacher_review()
        )
        set_review = TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview.from_dict(
            payload["hint_application_preview_set_teacher_review"]
        )
        self.assertEqual(len(set_review.rejected_preview_ids), set_review.preview_count)

    def test_preview_set_review_status_with_approved_application_previews(self) -> None:
        self.assertEqual(
            self._valid_set_review().set_review_status,
            "reviewed_with_approved_application_previews",
        )

    def test_preview_set_review_status_all_held_or_rejected_when_none_approved(self) -> None:
        payload = (
            build_demo_all_held_task_working_memory_readback_hint_application_teacher_review()
        )
        set_review = TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview.from_dict(
            payload["hint_application_preview_set_teacher_review"]
        )
        self.assertEqual(set_review.set_review_status, "reviewed_all_held_or_rejected")

    def test_scope_warnings_preserved(self) -> None:
        self.assertIn(
            "front_blocked may be too broad",
            self._review_for_first_preview(APPROVED).scope_warning or "",
        )

    def test_counterexample_warnings_preserved(self) -> None:
        self.assertIn(
            "front_blocked + step_forward succeeds",
            self._review_for_first_preview(APPROVED).counterexample_warning or "",
        )

    def test_safety_audit_passes_for_valid_demo_review(self) -> None:
        payload = build_demo_task_working_memory_readback_hint_application_teacher_review()
        validation = validate_task_working_memory_readback_hint_application_teacher_review_safety_audit(
            payload["hint_application_teacher_review_safety_audit"]
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_safety_audit_blocks_invalid_application_preview_set(self) -> None:
        held_preview_payload = (
            build_demo_all_held_task_working_memory_readback_hint_application_preview_set()
        )
        payload = build_task_working_memory_readback_hint_application_teacher_review_bundle(
            held_preview_payload
        )
        audit = TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit.from_dict(
            payload["hint_application_teacher_review_safety_audit"]
        )
        self.assertEqual(audit.audit_status, "blocked_invalid_application_preview_set")

    def test_safety_audit_blocks_invalid_review_source(self) -> None:
        payload = build_demo_blocked_invalid_review_source()
        audit = TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit.from_dict(
            payload["hint_application_teacher_review_safety_audit"]
        )
        self.assertEqual(audit.audit_status, "blocked_invalid_teacher_review_source")

    def test_safety_audit_blocks_forbidden_active_hint_application(self) -> None:
        audit = self._audit_with_review_flag("applied_to_working_memory", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_active_hint_application_detected",
        )

    def test_safety_audit_blocks_forbidden_working_memory_mutation(self) -> None:
        audit = self._audit_with_review_flag("working_memory_mutated", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_working_memory_mutation_detected",
        )

    def test_safety_audit_blocks_forbidden_task_behavior_change(self) -> None:
        audit = self._audit_with_review_flag("task_behavior_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_safety_audit_blocks_forbidden_candidate_ordering_change(self) -> None:
        audit = self._audit_with_review_flag("candidate_ordering_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_safety_audit_blocks_forbidden_selected_action_change(self) -> None:
        audit = self._audit_with_review_flag("selected_action_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_final_action_change(self) -> None:
        audit = self._audit_with_review_flag("final_action_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_direct_command_change(self) -> None:
        audit = self._audit_with_review_flag("direct_command_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_execution(self) -> None:
        audit = self._audit_with_review_flag("execution_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_memory_layer_write(self) -> None:
        audit = self._audit_with_review_flag("memory_layer_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_write_detected",
        )

    def test_cli_review_demo_application_works(self) -> None:
        result = self._run_task_cli("review-demo-application")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("reviewed_with_approved_application_previews", result.stdout)

    def test_cli_show_demo_review_works(self) -> None:
        result = self._run_task_cli("show-demo-review")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("approved_preview_ids", result.stdout)

    def test_cli_show_demo_safety_audit_works(self) -> None:
        result = self._run_task_cli("show-demo-safety-audit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"audit_status": "passed"', result.stdout)

    def test_cli_validate_demo_review_works(self) -> None:
        result = self._run_task_cli("validate-demo-review")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_all_held_works(self) -> None:
        result = self._run_task_cli("review-demo-held", "--case", "all-held")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("reviewed_all_held_or_rejected", result.stdout)

    def test_cli_rejected_works(self) -> None:
        result = self._run_task_cli("review-demo-rejected")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rejected_preview_ids", result.stdout)

    def test_cli_conflict_works(self) -> None:
        result = self._run_task_cli("review-demo-conflict")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("conflict_detected", result.stdout)

    def test_cli_blocked_invalid_review_source_works(self) -> None:
        result = self._run_task_cli(
            "review-demo-blocked",
            "--case",
            "invalid-review-source",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_invalid_teacher_review_source", result.stdout)

    def test_cli_blocked_forbidden_authority_works(self) -> None:
        result = self._run_task_cli(
            "review-demo-blocked",
            "--case",
            "forbidden-authority",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_active_hint_application_detected", result.stdout)

    def test_guided_console_application_teacher_review_demo_works(self) -> None:
        for command in (
            "task-review-reviewed-concept-hint-application-demo",
            "task-show-reviewed-concept-hint-application-review",
            "task-validate-reviewed-concept-hint-application-review",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_task_working_memory_readback_hint_application_teacher_review()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _preview_payload(self) -> dict[str, object]:
        return build_demo_task_working_memory_readback_hint_application_preview_set()

    def _first_preview(self) -> dict[str, object]:
        return self._preview_payload()[
            "task_working_memory_readback_hint_application_previews"
        ][0]

    def _valid_preview_set(self) -> TaskWorkingMemoryReadbackHintApplicationPreviewSet:
        return TaskWorkingMemoryReadbackHintApplicationPreviewSet.from_dict(
            self._preview_payload()[
                "task_working_memory_readback_hint_application_preview_set"
            ]
        )

    def _valid_set_review(
        self,
    ) -> TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview:
        payload = build_demo_task_working_memory_readback_hint_application_teacher_review()
        return TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview.from_dict(
            payload["hint_application_preview_set_teacher_review"]
        )

    def _review_for_first_preview(
        self,
        status: str,
        *,
        review_actor: str = "system_demo",
        review_actor_role: str = "system_demo",
        review_source: str = "demo_review",
        teacher_review_text: str = "",
    ) -> TaskWorkingMemoryReadbackHintApplicationTeacherReview:
        payload = self._preview_payload()
        return build_task_working_memory_readback_hint_application_teacher_review(
            application_preview=payload[
                "task_working_memory_readback_hint_application_previews"
            ][0],
            application_preview_set=payload[
                "task_working_memory_readback_hint_application_preview_set"
            ],
            application_preview_safety_audit=payload[
                "task_working_memory_readback_hint_application_preview_safety_audit"
            ],
            teacher_review_status=status,
            review_actor=review_actor,
            review_actor_role=review_actor_role,
            review_source=review_source,
            teacher_review_text=teacher_review_text,
        )

    def _audit_with_review_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> TaskWorkingMemoryReadbackHintApplicationTeacherReviewSafetyAudit:
        preview_payload = self._preview_payload()
        review_payload = build_demo_task_working_memory_readback_hint_application_teacher_review()
        set_review = TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview.from_dict(
            review_payload["hint_application_preview_set_teacher_review"]
        )
        reviews = list(set_review.application_preview_reviews)
        first = dict(reviews[0].to_dict())
        first[flag_name] = flag_value
        reviews[0] = TaskWorkingMemoryReadbackHintApplicationTeacherReview.from_dict(
            first
        )
        set_review = TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview.from_dict(
            {
                **set_review.to_dict(),
                "application_preview_reviews": [
                    review.to_dict() for review in reviews
                ],
            }
        )
        return build_task_working_memory_readback_hint_application_teacher_review_safety_audit(
            application_preview_set=preview_payload[
                "task_working_memory_readback_hint_application_preview_set"
            ],
            application_preview_safety_audit=preview_payload[
                "task_working_memory_readback_hint_application_preview_safety_audit"
            ],
            set_teacher_review=set_review,
        )

    def _run_task_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.task.reviewed_concept_readback_hint_application_teacher_review_cli",
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
