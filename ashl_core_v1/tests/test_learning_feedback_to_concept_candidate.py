from __future__ import annotations

import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.learning.learning_feedback_to_concept_candidate import (
    LearningFeedbackTeacherReviewRecord,
    LearningFeedbackToConceptCandidateDraftRecord,
    LearningFeedbackToConceptCandidateRollbackRecord,
    LearningFeedbackToConceptCandidateSafetyAudit,
    apply_learning_feedback_to_concept_candidate_rollback,
    build_demo_blocked_learning_feedback_to_concept_candidate,
    build_demo_failed_expected_effect_to_concept_candidate,
    build_demo_goal_reached_to_concept_candidate,
    build_demo_learning_feedback_to_concept_candidate_case,
    build_demo_no_progress_to_concept_candidate,
    build_demo_observation_only_to_concept_candidate,
    build_demo_successful_expected_effect_to_concept_candidate,
    build_demo_system_fault_blocked_feedback_review,
    build_demo_unknown_outcome_held_feedback_review,
    build_learning_feedback_teacher_review_record,
    build_learning_feedback_teacher_review_set,
    build_learning_feedback_to_concept_candidate_draft_record,
    build_learning_feedback_to_concept_candidate_rollback_record,
    build_learning_feedback_to_concept_candidate_safety_audit,
    map_learning_feedback_to_concept_candidate_kind,
    validate_learning_feedback_teacher_review_record,
    validate_learning_feedback_teacher_review_set,
    validate_learning_feedback_to_concept_candidate_draft_record,
    validate_learning_feedback_to_concept_candidate_rollback_record,
    validate_learning_feedback_to_concept_candidate_safety_audit,
)
from ashl_core_v1.learning.task_closure_learning_feedback_candidate import (
    LearningFeedbackCandidateEvidencePacket,
    LearningFeedbackCandidateRecord,
    LearningFeedbackCandidateSafetyAudit,
)


TASK_CLI = "ashl_core_v1.learning.learning_feedback_to_concept_candidate_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class LearningFeedbackToConceptCandidateTests(unittest.TestCase):
    def test_teacher_review_builds_from_valid_learning_feedback_candidate(self) -> None:
        review = self._review()
        validation = validate_learning_feedback_teacher_review_record(review)
        self.assertTrue(validation["valid"])
        self.assertEqual(
            review.teacher_review_status,
            "approved_for_concept_candidate_draft",
        )

    def test_teacher_review_requires_learning_feedback_safety_audit_pass(self) -> None:
        payload = build_demo_blocked_learning_feedback_to_concept_candidate(
            "invalid-feedback-safety-audit"
        )
        review = LearningFeedbackTeacherReviewRecord.from_dict(
            payload["learning_feedback_teacher_review"]
        )
        self.assertEqual(
            review.teacher_review_status,
            "blocked_invalid_learning_feedback_candidate",
        )

    def test_explicit_teacher_review_requires_non_empty_text(self) -> None:
        review = build_learning_feedback_teacher_review_record(
            candidate=self._candidate(),
            evidence_packet=self._packet(),
            candidate_safety_audit=self._feedback_safety_audit(),
            review_source="explicit_teacher_review",
            review_actor_role="teacher",
            review_actor="teacher",
            teacher_review_text="",
        )
        validation = validate_learning_feedback_teacher_review_record(review)
        self.assertFalse(validation["valid"])
        self.assertIn(
            "explicit_review_requires_teacher_review_text",
            validation["error_codes"],
        )

    def test_explicit_teacher_review_requires_teacher_or_project_owner_role(self) -> None:
        review = build_learning_feedback_teacher_review_record(
            candidate=self._candidate(),
            evidence_packet=self._packet(),
            candidate_safety_audit=self._feedback_safety_audit(),
            review_source="explicit_teacher_review",
            review_actor_role="system_demo",
            review_actor="demo",
            teacher_review_text="approve draft only",
        )
        validation = validate_learning_feedback_teacher_review_record(review)
        self.assertFalse(validation["valid"])
        self.assertIn(
            "explicit_review_requires_teacher_or_project_owner",
            validation["error_codes"],
        )

    def test_demo_review_requires_system_demo_role(self) -> None:
        review = build_learning_feedback_teacher_review_record(
            candidate=self._candidate(),
            evidence_packet=self._packet(),
            candidate_safety_audit=self._feedback_safety_audit(),
            review_source="demo_review",
            review_actor_role="teacher",
            review_actor="teacher",
        )
        validation = validate_learning_feedback_teacher_review_record(review)
        self.assertFalse(validation["valid"])
        self.assertIn("demo_review_requires_system_demo_role", validation["error_codes"])

    def test_teacher_review_approves_concept_candidate_draft_only(self) -> None:
        review = self._review()
        self.assertTrue(review.approved_for_concept_candidate_draft)
        self.assertFalse(review.approved_for_reviewed_concept)
        self.assertFalse(review.approved_for_memory_write)
        self.assertFalse(review.approved_for_behavior_change)
        self.assertFalse(review.approved_for_action_authority)
        self.assertFalse(review.approved_for_automatic_learning_approval)
        self.assertFalse(review.learning_feedback_approved)

    def test_teacher_review_set_lists_approved_candidates(self) -> None:
        review_set = build_learning_feedback_teacher_review_set(reviews=(self._review(),))
        validation = validate_learning_feedback_teacher_review_set(review_set)
        self.assertTrue(validation["valid"])
        self.assertEqual(review_set.approved_count, 1)
        self.assertEqual(
            review_set.set_review_status,
            "review_set_created_with_approved_feedback",
        )

    def test_mapping_rules(self) -> None:
        cases = {
            "goal-reached": "goal_completion_concept_candidate",
            "successful-expected-effect": "positive_affordance_concept_candidate",
            "failed-expected-effect": "negative_affordance_concept_candidate",
            "no-progress": "no_progress_concept_candidate",
            "observation-only": "observation_context_concept_candidate",
        }
        for case, expected_kind in cases.items():
            with self.subTest(case=case):
                draft = self._draft_from_payload(
                    build_demo_learning_feedback_to_concept_candidate_case(case)
                )
                self.assertEqual(draft.concept_candidate_kind, expected_kind)
                self.assertEqual(
                    draft.concept_candidate_status,
                    "concept_candidate_draft_created",
                )

    def test_unknown_outcome_held_for_more_evidence(self) -> None:
        draft = self._draft_from_payload(build_demo_unknown_outcome_held_feedback_review())
        self.assertEqual(draft.concept_candidate_kind, "unknown_outcome_concept_candidate")
        self.assertEqual(draft.concept_candidate_status, "held_for_more_evidence")

    def test_system_fault_blocked_or_held_diagnostic(self) -> None:
        draft = self._draft_from_payload(build_demo_system_fault_blocked_feedback_review())
        self.assertEqual(draft.concept_candidate_kind, "system_fault_diagnostic_candidate")
        self.assertIn(
            draft.concept_candidate_status,
            {"held_for_more_evidence", "blocked_conflict_detected"},
        )

    def test_concept_candidate_draft_builds_after_approved_teacher_review(self) -> None:
        draft = self._draft()
        validation = validate_learning_feedback_to_concept_candidate_draft_record(draft)
        self.assertTrue(validation["valid"])
        self.assertEqual(draft.concept_candidate_status, "concept_candidate_draft_created")

    def test_concept_candidate_draft_preserves_learning_feedback_and_evidence_ids(self) -> None:
        draft = self._draft()
        self.assertEqual(
            draft.source_learning_feedback_candidate_id,
            self._candidate().learning_feedback_candidate_id,
        )
        self.assertEqual(
            draft.source_learning_feedback_evidence_packet_id,
            self._packet().learning_feedback_evidence_packet_id,
        )
        self.assertEqual(
            draft.source_learning_feedback_teacher_review_id,
            self._review().learning_feedback_teacher_review_id,
        )

    def test_concept_candidate_draft_preserves_task_trace_refs(self) -> None:
        draft = self._draft()
        candidate = self._candidate()
        self.assertEqual(draft.source_task_closure_id, candidate.source_task_closure_id)
        self.assertEqual(
            draft.source_outcome_evaluation_id,
            candidate.source_outcome_evaluation_id,
        )
        self.assertEqual(draft.source_sense_handoff_id, candidate.source_sense_handoff_id)
        self.assertEqual(
            draft.source_sandbox_execution_id,
            candidate.source_sandbox_execution_id,
        )
        self.assertEqual(draft.direct_command, candidate.direct_command)
        self.assertEqual(draft.expected_effect, candidate.expected_effect)
        self.assertEqual(draft.outcome_class, candidate.outcome_class)
        self.assertEqual(draft.goal_delta_class, candidate.goal_delta_class)

    def test_concept_candidate_draft_requires_later_gates(self) -> None:
        draft = self._draft()
        self.assertTrue(draft.requires_teacher_review_before_concept_acceptance)
        self.assertTrue(draft.requires_counterexample_check_later)
        self.assertTrue(draft.requires_refinement_later)
        self.assertTrue(draft.requires_reviewed_concept_gate_later)
        self.assertTrue(draft.requires_memory_write_gate_later)

    def test_concept_candidate_draft_does_not_create_reviewed_concept_memory_or_behavior(self) -> None:
        draft = self._draft()
        self.assertFalse(draft.actual_existing_concept_candidate_created)
        self.assertFalse(draft.reviewed_concept_created)
        self.assertFalse(draft.memory_write_performed)
        self.assertFalse(draft.automatic_learning_approval_created)
        self.assertFalse(draft.candidate_ordering_changed)
        self.assertFalse(draft.selected_action_changed)
        self.assertFalse(draft.final_action_changed)
        self.assertFalse(draft.direct_command_created)
        self.assertFalse(draft.execution_created)
        self.assertFalse(draft.task_behavior_changed)

    def test_concept_candidate_draft_blocks_invalid_inputs(self) -> None:
        expected = {
            "invalid-learning-feedback-candidate": "blocked_invalid_learning_feedback",
            "invalid-feedback-safety-audit": "blocked_invalid_learning_feedback",
            "missing-teacher-review": "blocked_invalid_teacher_review",
            "teacher-rejected": "rejected_by_teacher",
            "conflict-detected": "blocked_conflict_detected",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                draft = self._draft_from_payload(
                    build_demo_blocked_learning_feedback_to_concept_candidate(case)
                )
                self.assertEqual(draft.concept_candidate_status, status)

    def test_concept_candidate_draft_blocks_forbidden_authority_paths(self) -> None:
        expected = {
            "reviewed-concept-created": "blocked_reviewed_concept_creation_detected",
            "memory-write-detected": "blocked_memory_write_detected",
            "automatic-learning-approval": "blocked_automatic_learning_approval_detected",
            "action-authority-detected": "blocked_action_authority_detected",
            "behavior-change-detected": "blocked_behavior_change_detected",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                audit = self._audit_from_payload(
                    build_demo_blocked_learning_feedback_to_concept_candidate(case)
                )
                self.assertEqual(audit.audit_status, status)

    def test_rollback_record_created_for_successful_draft(self) -> None:
        rollback = self._rollback()
        validation = validate_learning_feedback_to_concept_candidate_rollback_record(
            rollback
        )
        self.assertTrue(validation["valid"])
        self.assertTrue(rollback.rollback_available)
        self.assertEqual(rollback.rollback_status, "rollback_record_created")

    def test_rollback_withdraws_draft_availability_without_memory_or_behavior(self) -> None:
        applied = apply_learning_feedback_to_concept_candidate_rollback(self._rollback())
        self.assertTrue(applied.rollback_applied)
        self.assertFalse(applied.concept_candidate_draft_available_after_rollback)
        self.assertFalse(applied.reviewed_concept_created)
        self.assertFalse(applied.memory_write_performed)
        self.assertFalse(applied.task_behavior_changed)

    def test_safety_audit_passes_concept_candidate_draft_only(self) -> None:
        audit = self._audit()
        validation = validate_learning_feedback_to_concept_candidate_safety_audit(audit)
        self.assertTrue(validation["valid"])
        self.assertEqual(audit.audit_status, "passed_concept_candidate_draft_only")
        self.assertTrue(audit.concept_candidate_draft_only_confirmed)

    def test_safety_audit_passes_no_concept_candidate_created(self) -> None:
        audit = self._audit_from_payload(build_demo_unknown_outcome_held_feedback_review())
        validation = validate_learning_feedback_to_concept_candidate_safety_audit(audit)
        self.assertTrue(validation["valid"])
        self.assertEqual(audit.audit_status, "passed_no_concept_candidate_created")

    def test_safety_audit_blocks_invalid_learning_feedback_teacher_review_and_missing_rollback(self) -> None:
        expected = {
            "invalid-learning-feedback-candidate": "blocked_invalid_learning_feedback_candidate",
            "invalid-feedback-safety-audit": "blocked_invalid_learning_feedback_candidate",
            "missing-teacher-review": "blocked_invalid_teacher_review",
            "missing-rollback": "blocked_missing_rollback",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                audit = self._audit_from_payload(
                    build_demo_blocked_learning_feedback_to_concept_candidate(case)
                )
                self.assertEqual(audit.audit_status, status)

    def test_map_helper_returns_expected_tuple(self) -> None:
        kind, confidence, label = map_learning_feedback_to_concept_candidate_kind(
            "failed_expected_effect_candidate",
            "negative_affordance_signal",
        )
        self.assertEqual(kind, "negative_affordance_concept_candidate")
        self.assertEqual(confidence, "normal")
        self.assertEqual(label, "failed_affordance_from_expected_effect")

    def test_manual_build_functions_round_trip(self) -> None:
        review = build_learning_feedback_teacher_review_record(
            candidate=self._candidate(),
            evidence_packet=self._packet(),
            candidate_safety_audit=self._feedback_safety_audit(),
        )
        review_set = build_learning_feedback_teacher_review_set(reviews=(review,))
        draft = build_learning_feedback_to_concept_candidate_draft_record(
            candidate=self._candidate(),
            evidence_packet=self._packet(),
            teacher_review=review,
            teacher_review_set=review_set,
        )
        rollback = build_learning_feedback_to_concept_candidate_rollback_record(
            draft=draft
        )
        audit = build_learning_feedback_to_concept_candidate_safety_audit(
            teacher_review_set=review_set,
            drafts=(draft,),
            rollbacks=(rollback,),
        )
        self.assertTrue(
            validate_learning_feedback_to_concept_candidate_safety_audit(audit)[
                "valid"
            ]
        )

    def test_cli_commands_work(self) -> None:
        for args in (
            ["build-demo-concept-candidate"],
            ["show-demo-teacher-review"],
            ["show-demo-concept-candidate-draft"],
            ["show-demo-rollback"],
            ["show-demo-safety-audit"],
            ["validate-demo-concept-candidate"],
        ):
            with self.subTest(args=args):
                payload = self._run_cli(TASK_CLI, args)
                self.assertIsInstance(payload, dict)

    def test_cli_cases_work(self) -> None:
        for case in (
            "goal-reached",
            "successful-expected-effect",
            "failed-expected-effect",
            "no-progress",
            "observation-only",
            "unknown-outcome",
            "system-fault",
        ):
            with self.subTest(case=case):
                payload = self._run_cli(TASK_CLI, ["build-demo-case", "--case", case])
                self.assertIn("learning_feedback_to_concept_candidate_draft", payload)

    def test_cli_blocked_cases_work(self) -> None:
        for case in (
            "invalid-learning-feedback-candidate",
            "invalid-feedback-safety-audit",
            "missing-teacher-review",
            "teacher-rejected",
            "conflict-detected",
            "reviewed-concept-created",
            "memory-write-detected",
            "automatic-learning-approval",
            "action-authority-detected",
            "behavior-change-detected",
            "missing-rollback",
        ):
            with self.subTest(case=case):
                payload = self._run_cli(TASK_CLI, ["build-demo-blocked", "--case", case])
                self.assertIn("learning_feedback_to_concept_candidate_safety_audit", payload)

    def test_guided_console_feedback_to_concept_candidate_demo_works(self) -> None:
        for command in (
            "learning-build-concept-candidate-from-feedback-demo",
            "learning-show-feedback-teacher-review",
            "learning-show-feedback-concept-candidate-draft",
            "learning-show-feedback-concept-candidate-rollback",
            "learning-show-feedback-concept-candidate-safety-audit",
            "learning-validate-feedback-concept-candidate",
        ):
            with self.subTest(command=command):
                payload = self._run_cli(GUIDED_CLI, [command])
                self.assertIsInstance(payload, dict)
                self.assertFalse(payload.get("memory_write_performed", False))

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _payload(self) -> dict[str, object]:
        return build_demo_successful_expected_effect_to_concept_candidate()

    def _candidate(self) -> LearningFeedbackCandidateRecord:
        return LearningFeedbackCandidateRecord.from_dict(
            self._payload()["learning_feedback_candidate"]
        )

    def _packet(self) -> LearningFeedbackCandidateEvidencePacket:
        return LearningFeedbackCandidateEvidencePacket.from_dict(
            self._payload()["learning_feedback_evidence_packet"]
        )

    def _feedback_safety_audit(self) -> LearningFeedbackCandidateSafetyAudit:
        return LearningFeedbackCandidateSafetyAudit.from_dict(
            self._payload()["learning_feedback_candidate_safety_audit"]
        )

    def _review(self) -> LearningFeedbackTeacherReviewRecord:
        return LearningFeedbackTeacherReviewRecord.from_dict(
            self._payload()["learning_feedback_teacher_review"]
        )

    def _draft(self) -> LearningFeedbackToConceptCandidateDraftRecord:
        return self._draft_from_payload(self._payload())

    def _rollback(self) -> LearningFeedbackToConceptCandidateRollbackRecord:
        return LearningFeedbackToConceptCandidateRollbackRecord.from_dict(
            self._payload()["learning_feedback_to_concept_candidate_rollback"]
        )

    def _audit(self) -> LearningFeedbackToConceptCandidateSafetyAudit:
        return self._audit_from_payload(self._payload())

    def _draft_from_payload(
        self,
        payload: dict[str, object],
    ) -> LearningFeedbackToConceptCandidateDraftRecord:
        return LearningFeedbackToConceptCandidateDraftRecord.from_dict(
            payload["learning_feedback_to_concept_candidate_draft"]
        )

    def _audit_from_payload(
        self,
        payload: dict[str, object],
    ) -> LearningFeedbackToConceptCandidateSafetyAudit:
        return LearningFeedbackToConceptCandidateSafetyAudit.from_dict(
            payload["learning_feedback_to_concept_candidate_safety_audit"]
        )

    def _run_cli(self, module: str, args: list[str]) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, "-m", module, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)


if __name__ == "__main__":
    unittest.main()
