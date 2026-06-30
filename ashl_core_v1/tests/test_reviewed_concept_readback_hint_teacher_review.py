from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.memory.reviewed_concept_readback_hint_candidate import (
    ReviewedConceptReadbackHintCandidateSet,
    build_demo_held_for_more_evidence_hint_candidate_set,
    build_demo_reviewed_concept_readback_hint_candidate_set,
)
from ashl_core_v1.memory.reviewed_concept_readback_hint_teacher_review import (
    ReviewedConceptReadbackHintCandidateSetTeacherReview,
    ReviewedConceptReadbackHintCandidateTeacherReview,
    ReviewedConceptReadbackHintTeacherReviewSafetyAudit,
    build_demo_all_held_readback_hint_teacher_review,
    build_demo_blocked_forbidden_authority_review,
    build_demo_blocked_invalid_review_source,
    build_demo_conflict_detected_readback_hint_teacher_review,
    build_demo_rejected_readback_hint_teacher_review,
    build_demo_reviewed_concept_readback_hint_teacher_review,
    build_reviewed_concept_readback_hint_candidate_set_teacher_review,
    build_reviewed_concept_readback_hint_candidate_teacher_review,
    build_reviewed_concept_readback_hint_teacher_review_bundle,
    build_reviewed_concept_readback_hint_teacher_review_safety_audit,
    validate_reviewed_concept_readback_hint_candidate_set_teacher_review,
    validate_reviewed_concept_readback_hint_candidate_teacher_review,
    validate_reviewed_concept_readback_hint_teacher_review_safety_audit,
)


class ReviewedConceptReadbackHintTeacherReviewTests(unittest.TestCase):
    def test_teacher_review_builds_from_valid_candidate(self) -> None:
        review = self._review_for_first_candidate("approved_for_future_hint_preparation")
        validation = validate_reviewed_concept_readback_hint_candidate_teacher_review(
            review
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_teacher_review_preserves_reviewed_concept_id(self) -> None:
        review = self._review_for_first_candidate("approved_for_future_hint_preparation")
        self.assertEqual(
            review.source_reviewed_concept_id,
            self._candidate_payload()["hint_candidate_set"]["source_reviewed_concept_id"],
        )

    def test_teacher_review_preserves_hint_candidate_id(self) -> None:
        candidate = self._first_candidate()
        review = self._review_for_first_candidate("approved_for_future_hint_preparation")
        self.assertEqual(review.source_hint_candidate_id, candidate["readback_hint_candidate_id"])

    def test_approved_status_sets_future_preparation_true(self) -> None:
        review = self._review_for_first_candidate("approved_for_future_hint_preparation")
        self.assertTrue(review.approved_for_future_hint_preparation)

    def test_approved_status_keeps_actual_hint_creation_false(self) -> None:
        review = self._review_for_first_candidate("approved_for_future_hint_preparation")
        self.assertFalse(review.approved_for_actual_hint_creation)
        self.assertFalse(review.actual_task_working_memory_hint_created)

    def test_approved_status_keeps_working_memory_application_false(self) -> None:
        review = self._review_for_first_candidate("approved_for_future_hint_preparation")
        self.assertFalse(review.approved_for_working_memory_application)
        self.assertFalse(review.applied_to_working_memory)
        self.assertFalse(review.working_memory_mutated)

    def test_approved_status_keeps_task_behavior_changed_false(self) -> None:
        review = self._review_for_first_candidate("approved_for_future_hint_preparation")
        self.assertFalse(review.approved_for_task_behavior_change)
        self.assertFalse(review.task_behavior_changed)

    def test_held_status_does_not_approve_future_preparation(self) -> None:
        review = self._review_for_first_candidate("held_for_more_evidence")
        self.assertFalse(review.approved_for_future_hint_preparation)

    def test_rejected_status_does_not_approve_future_preparation(self) -> None:
        review = self._review_for_first_candidate("rejected")
        self.assertFalse(review.approved_for_future_hint_preparation)

    def test_needs_more_evidence_status_does_not_approve_future_preparation(self) -> None:
        review = self._review_for_first_candidate("needs_more_evidence")
        self.assertFalse(review.approved_for_future_hint_preparation)

    def test_conflict_detected_status_does_not_approve_future_preparation(self) -> None:
        review = self._review_for_first_candidate("conflict_detected")
        self.assertFalse(review.approved_for_future_hint_preparation)

    def test_explicit_teacher_review_requires_non_empty_text(self) -> None:
        review = self._review_for_first_candidate(
            "approved_for_future_hint_preparation",
            review_source="explicit_teacher_review",
            review_actor="teacher",
            review_actor_role="teacher",
            teacher_review_text="",
        )
        validation = validate_reviewed_concept_readback_hint_candidate_teacher_review(
            review
        )
        self.assertIn("missing_teacher_review_text", validation["error_codes"])

    def test_explicit_teacher_review_requires_teacher_or_project_owner_role(self) -> None:
        review = self._review_for_first_candidate(
            "approved_for_future_hint_preparation",
            review_source="explicit_teacher_review",
            review_actor="demo",
            review_actor_role="system_demo",
            teacher_review_text="Explicitly approve for future preparation.",
        )
        validation = validate_reviewed_concept_readback_hint_candidate_teacher_review(
            review
        )
        self.assertIn("invalid_explicit_review_actor_role", validation["error_codes"])

    def test_demo_review_requires_system_demo_actor_role(self) -> None:
        review = self._review_for_first_candidate(
            "approved_for_future_hint_preparation",
            review_source="demo_review",
            review_actor="teacher_demo",
            review_actor_role="teacher",
        )
        validation = validate_reviewed_concept_readback_hint_candidate_teacher_review(
            review
        )
        self.assertIn("invalid_demo_review_actor_role", validation["error_codes"])

    def test_candidate_set_teacher_review_builds_from_valid_candidate_set(self) -> None:
        set_review = self._valid_set_review()
        validation = validate_reviewed_concept_readback_hint_candidate_set_teacher_review(
            set_review
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_candidate_set_review_preserves_candidate_count(self) -> None:
        set_review = self._valid_set_review()
        candidate_set = self._valid_candidate_set()
        self.assertEqual(set_review.candidate_count, candidate_set.candidate_count)

    def test_candidate_set_review_lists_approved_candidate_ids(self) -> None:
        set_review = self._valid_set_review()
        self.assertEqual(len(set_review.approved_candidate_ids), 2)

    def test_candidate_set_review_lists_held_candidate_ids(self) -> None:
        set_review = self._valid_set_review()
        self.assertEqual(len(set_review.held_candidate_ids), 1)

    def test_candidate_set_review_lists_rejected_candidate_ids(self) -> None:
        payload = build_demo_rejected_readback_hint_teacher_review()
        set_review = ReviewedConceptReadbackHintCandidateSetTeacherReview.from_dict(
            payload["hint_candidate_set_teacher_review"]
        )
        self.assertEqual(len(set_review.rejected_candidate_ids), set_review.candidate_count)

    def test_set_review_status_with_approved_candidates(self) -> None:
        self.assertEqual(
            self._valid_set_review().set_review_status,
            "reviewed_with_approved_candidates",
        )

    def test_set_review_status_all_held_or_rejected_when_none_approved(self) -> None:
        payload = build_demo_all_held_readback_hint_teacher_review()
        set_review = ReviewedConceptReadbackHintCandidateSetTeacherReview.from_dict(
            payload["hint_candidate_set_teacher_review"]
        )
        self.assertEqual(set_review.set_review_status, "reviewed_all_held_or_rejected")

    def test_scope_warnings_preserved(self) -> None:
        review = self._review_for_first_candidate("approved_for_future_hint_preparation")
        self.assertIn("front_blocked may be too broad", review.scope_warning or "")

    def test_counterexample_warnings_preserved(self) -> None:
        review = self._review_for_first_candidate("approved_for_future_hint_preparation")
        self.assertIn(
            "front_blocked + step_forward succeeds",
            review.counterexample_warning or "",
        )

    def test_safety_audit_passes_for_valid_demo_review(self) -> None:
        payload = build_demo_reviewed_concept_readback_hint_teacher_review()
        validation = validate_reviewed_concept_readback_hint_teacher_review_safety_audit(
            payload["hint_teacher_review_safety_audit"]
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_safety_audit_blocks_invalid_candidate_set(self) -> None:
        held_payload = build_demo_held_for_more_evidence_hint_candidate_set()
        payload = build_reviewed_concept_readback_hint_teacher_review_bundle(held_payload)
        audit = ReviewedConceptReadbackHintTeacherReviewSafetyAudit.from_dict(
            payload["hint_teacher_review_safety_audit"]
        )
        self.assertEqual(audit.audit_status, "blocked_invalid_hint_candidate_set")

    def test_safety_audit_blocks_invalid_review_source(self) -> None:
        payload = build_demo_blocked_invalid_review_source()
        audit = ReviewedConceptReadbackHintTeacherReviewSafetyAudit.from_dict(
            payload["hint_teacher_review_safety_audit"]
        )
        self.assertEqual(audit.audit_status, "blocked_invalid_teacher_review_source")

    def test_safety_audit_blocks_forbidden_actual_hint_creation(self) -> None:
        audit = self._audit_with_review_flag(
            "actual_task_working_memory_hint_created",
            True,
        )
        self.assertEqual(audit.audit_status, "blocked_forbidden_hint_creation_detected")

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

    def test_safety_audit_blocks_forbidden_action_selection(self) -> None:
        audit = self._audit_with_review_flag("action_selection_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_action_execution(self) -> None:
        audit = self._audit_with_review_flag("action_execution_created", True)
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

    def test_blocked_forbidden_authority_demo_blocks(self) -> None:
        payload = build_demo_blocked_forbidden_authority_review()
        self.assertEqual(
            payload["hint_teacher_review_safety_audit"]["audit_status"],
            "blocked_forbidden_hint_creation_detected",
        )

    def test_conflict_demo_status_conflict_detected(self) -> None:
        payload = build_demo_conflict_detected_readback_hint_teacher_review()
        set_review = ReviewedConceptReadbackHintCandidateSetTeacherReview.from_dict(
            payload["hint_candidate_set_teacher_review"]
        )
        self.assertEqual(set_review.set_review_status, "conflict_detected")
        self.assertFalse(set_review.has_approved_candidates_for_future_preparation)

    def test_cli_review_demo_candidates_works(self) -> None:
        result = self._run_memory_cli("review-demo-candidates")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("reviewed_with_approved_candidates", result.stdout)

    def test_cli_show_demo_review_works(self) -> None:
        result = self._run_memory_cli("show-demo-review")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("approved_candidate_ids", result.stdout)

    def test_cli_show_demo_safety_audit_works(self) -> None:
        result = self._run_memory_cli("show-demo-safety-audit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"audit_status": "passed"', result.stdout)

    def test_cli_validate_demo_review_works(self) -> None:
        result = self._run_memory_cli("validate-demo-review")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_all_held_works(self) -> None:
        result = self._run_memory_cli("review-demo-held", "--case", "all-held")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("reviewed_all_held_or_rejected", result.stdout)

    def test_cli_rejected_works(self) -> None:
        result = self._run_memory_cli("review-demo-rejected")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rejected_candidate_ids", result.stdout)

    def test_cli_conflict_works(self) -> None:
        result = self._run_memory_cli("review-demo-conflict")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("conflict_detected", result.stdout)

    def test_cli_blocked_invalid_review_source_works(self) -> None:
        result = self._run_memory_cli(
            "review-demo-blocked",
            "--case",
            "invalid-review-source",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_invalid_teacher_review_source", result.stdout)

    def test_cli_blocked_forbidden_authority_works(self) -> None:
        result = self._run_memory_cli(
            "review-demo-blocked",
            "--case",
            "forbidden-authority",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_hint_creation_detected", result.stdout)

    def test_guided_console_teacher_review_demo_works(self) -> None:
        for command in (
            "memory-review-reviewed-concept-hint-candidates-demo",
            "memory-show-reviewed-concept-hint-candidate-review",
            "memory-validate-reviewed-concept-hint-candidate-review",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_reviewed_concept_readback_hint_teacher_review()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _candidate_payload(self) -> dict[str, object]:
        return build_demo_reviewed_concept_readback_hint_candidate_set()

    def _first_candidate(self) -> dict[str, object]:
        return self._candidate_payload()["hint_candidates"][0]

    def _valid_candidate_set(self) -> ReviewedConceptReadbackHintCandidateSet:
        return ReviewedConceptReadbackHintCandidateSet.from_dict(
            self._candidate_payload()["hint_candidate_set"]
        )

    def _valid_set_review(self) -> ReviewedConceptReadbackHintCandidateSetTeacherReview:
        payload = build_demo_reviewed_concept_readback_hint_teacher_review()
        return ReviewedConceptReadbackHintCandidateSetTeacherReview.from_dict(
            payload["hint_candidate_set_teacher_review"]
        )

    def _review_for_first_candidate(
        self,
        status: str,
        *,
        review_actor: str = "system_demo",
        review_actor_role: str = "system_demo",
        review_source: str = "demo_review",
        teacher_review_text: str = "",
    ) -> ReviewedConceptReadbackHintCandidateTeacherReview:
        payload = self._candidate_payload()
        return build_reviewed_concept_readback_hint_candidate_teacher_review(
            hint_candidate=payload["hint_candidates"][0],
            hint_candidate_set=payload["hint_candidate_set"],
            hint_candidate_safety_audit=payload["hint_candidate_safety_audit"],
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
    ) -> ReviewedConceptReadbackHintTeacherReviewSafetyAudit:
        candidate_payload = self._candidate_payload()
        review_payload = build_demo_reviewed_concept_readback_hint_teacher_review()
        set_review = ReviewedConceptReadbackHintCandidateSetTeacherReview.from_dict(
            review_payload["hint_candidate_set_teacher_review"]
        )
        reviews = list(set_review.candidate_reviews)
        first = dict(reviews[0].to_dict())
        first[flag_name] = flag_value
        reviews[0] = ReviewedConceptReadbackHintCandidateTeacherReview.from_dict(first)
        set_review = ReviewedConceptReadbackHintCandidateSetTeacherReview.from_dict(
            {
                **set_review.to_dict(),
                "candidate_reviews": [review.to_dict() for review in reviews],
            }
        )
        return build_reviewed_concept_readback_hint_teacher_review_safety_audit(
            hint_candidate_set=candidate_payload["hint_candidate_set"],
            hint_candidate_safety_audit=candidate_payload["hint_candidate_safety_audit"],
            set_teacher_review=set_review,
        )

    def _run_memory_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.memory.reviewed_concept_readback_hint_teacher_review_cli",
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
