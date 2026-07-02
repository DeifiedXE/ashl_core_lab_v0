from __future__ import annotations

import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.learning.task_closure_learning_feedback_candidate import (
    LearningFeedbackCandidateEvidencePacket,
    LearningFeedbackCandidateRecord,
    LearningFeedbackCandidateSafetyAudit,
    LearningFeedbackCandidateSet,
    build_demo_blocked_learning_feedback_candidate,
    build_demo_expected_effect_failed_learning_feedback_candidate,
    build_demo_goal_reached_learning_feedback_candidate,
    build_demo_learning_feedback_candidate_case,
    build_demo_learning_feedback_candidate_set,
    build_demo_no_progress_learning_feedback_candidate,
    build_demo_observation_only_learning_feedback_candidate,
    build_demo_progress_learning_feedback_candidate,
    build_demo_system_fault_learning_feedback_candidate,
    build_demo_unknown_outcome_learning_feedback_candidate,
    build_learning_feedback_candidate_evidence_packet,
    build_learning_feedback_candidate_safety_audit,
    build_learning_feedback_candidate_set,
    validate_learning_feedback_candidate_evidence_packet,
    validate_learning_feedback_candidate_record,
    validate_learning_feedback_candidate_safety_audit,
    validate_learning_feedback_candidate_set,
)
from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
    TaskExpectedEffectReferenceRecord,
    TaskExecutionOutcomeEvaluationRecord,
    TaskGoalDeltaEvaluationRecord,
)
from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
    TaskClosureFromOutcomeEvaluationRecord,
    TaskClosureSafetyAudit,
)


TASK_CLI = "ashl_core_v1.learning.task_closure_learning_feedback_candidate_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class TaskClosureLearningFeedbackCandidateTests(unittest.TestCase):
    def test_candidate_builds_from_valid_task_closure(self) -> None:
        candidate = self._candidate_record()
        validation = validate_learning_feedback_candidate_record(candidate)
        self.assertTrue(validation["valid"])
        self.assertEqual(
            candidate.feedback_candidate_kind,
            "successful_expected_effect_candidate",
        )

    def test_candidate_requires_task_closure_safety_audit_pass(self) -> None:
        payload = build_demo_blocked_learning_feedback_candidate("invalid-closure-audit")
        audit = LearningFeedbackCandidateSafetyAudit.from_dict(
            payload["learning_feedback_candidate_safety_audit"]
        )
        self.assertEqual(audit.audit_status, "blocked_invalid_task_closure")

    def test_candidate_preserves_source_refs(self) -> None:
        candidate = self._candidate_record()
        closure = self._closure_record()
        outcome = self._outcome_record()
        goal_delta = self._goal_delta_record()
        reference = self._reference_record()
        self.assertEqual(candidate.source_task_closure_id, closure.task_closure_id)
        self.assertEqual(candidate.source_outcome_evaluation_id, outcome.outcome_evaluation_id)
        self.assertEqual(
            candidate.source_goal_delta_evaluation_id,
            goal_delta.goal_delta_evaluation_id,
        )
        self.assertEqual(
            candidate.source_expected_effect_reference_id,
            reference.expected_effect_reference_id,
        )
        self.assertEqual(candidate.source_sense_handoff_id, closure.source_sense_handoff_id)
        self.assertEqual(
            candidate.source_sandbox_execution_id,
            closure.source_sandbox_execution_id,
        )
        self.assertEqual(candidate.direct_command, closure.direct_command)

    def test_goal_reached_maps_to_goal_reached_candidate(self) -> None:
        candidate = self._candidate_from_payload(
            build_demo_goal_reached_learning_feedback_candidate()
        )
        self.assertEqual(candidate.feedback_candidate_kind, "goal_reached_candidate")
        self.assertEqual(candidate.learning_signal_class, "goal_completion_signal")
        self.assertEqual(candidate.review_priority, "high")

    def test_progress_maps_to_successful_expected_effect_candidate(self) -> None:
        candidate = self._candidate_record()
        self.assertEqual(
            candidate.feedback_candidate_kind,
            "successful_expected_effect_candidate",
        )
        self.assertEqual(candidate.learning_signal_class, "positive_affordance_signal")

    def test_expected_effect_failed_maps_to_failed_candidate(self) -> None:
        candidate = self._candidate_from_payload(
            build_demo_expected_effect_failed_learning_feedback_candidate()
        )
        self.assertEqual(candidate.feedback_candidate_kind, "failed_expected_effect_candidate")
        self.assertEqual(candidate.learning_signal_class, "negative_affordance_signal")
        self.assertTrue(candidate.available_for_teacher_review)

    def test_no_progress_maps_to_no_progress_candidate(self) -> None:
        candidate = self._candidate_from_payload(
            build_demo_no_progress_learning_feedback_candidate()
        )
        self.assertEqual(candidate.feedback_candidate_kind, "no_progress_candidate")
        self.assertEqual(candidate.learning_signal_class, "no_progress_signal")

    def test_observation_only_maps_to_observation_context_candidate(self) -> None:
        candidate = self._candidate_from_payload(
            build_demo_observation_only_learning_feedback_candidate()
        )
        self.assertEqual(candidate.feedback_candidate_kind, "observation_only_candidate")
        self.assertEqual(candidate.learning_signal_class, "observation_context_signal")

    def test_unknown_and_system_fault_are_not_review_ready(self) -> None:
        unknown = self._candidate_from_payload(
            build_demo_unknown_outcome_learning_feedback_candidate()
        )
        fault = self._candidate_from_payload(
            build_demo_system_fault_learning_feedback_candidate()
        )
        self.assertEqual(unknown.feedback_candidate_kind, "unknown_outcome_candidate")
        self.assertFalse(unknown.available_for_teacher_review)
        self.assertEqual(fault.feedback_candidate_kind, "system_fault_candidate")
        self.assertEqual(fault.review_priority, "blocked")
        self.assertFalse(fault.available_for_teacher_review)

    def test_candidate_review_readiness_rules(self) -> None:
        progress = self._candidate_record()
        failed = self._candidate_from_payload(
            build_demo_expected_effect_failed_learning_feedback_candidate()
        )
        unknown = self._candidate_from_payload(
            build_demo_unknown_outcome_learning_feedback_candidate()
        )
        self.assertTrue(progress.available_for_teacher_review)
        self.assertTrue(failed.available_for_teacher_review)
        self.assertFalse(unknown.available_for_teacher_review)

    def test_candidate_does_not_create_learning_concepts_memory_or_behavior(self) -> None:
        candidate = self._candidate_record()
        self.assertFalse(candidate.learning_feedback_approved)
        self.assertFalse(candidate.learning_feedback_applied)
        self.assertFalse(candidate.concept_candidate_created)
        self.assertFalse(candidate.reviewed_concept_created)
        self.assertFalse(candidate.memory_write_performed)
        self.assertFalse(candidate.automatic_learning_approval_created)
        self.assertFalse(candidate.candidate_ordering_changed)
        self.assertFalse(candidate.selected_action_changed)
        self.assertFalse(candidate.final_action_changed)
        self.assertFalse(candidate.direct_command_created)
        self.assertFalse(candidate.execution_created)
        self.assertFalse(candidate.task_behavior_changed)

    def test_evidence_packet_builds_from_candidate(self) -> None:
        packet = self._packet_record()
        validation = validate_learning_feedback_candidate_evidence_packet(packet)
        self.assertTrue(validation["valid"])
        self.assertEqual(packet.source_learning_feedback_candidate_id, self._candidate_record().learning_feedback_candidate_id)

    def test_evidence_packet_marks_complete_when_required_refs_exist(self) -> None:
        packet = self._packet_record()
        self.assertTrue(packet.evidence_chain_complete)
        self.assertEqual(packet.evidence_packet_status, "evidence_packet_complete")
        self.assertEqual(packet.missing_evidence_refs, ())

    def test_evidence_packet_marks_partial_when_allowed_refs_missing(self) -> None:
        payload = build_demo_unknown_outcome_learning_feedback_candidate()
        candidate = self._candidate_from_payload(payload)
        closure = self._closure_from_payload(payload)
        outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
            payload["source_package87_outcome_evaluation"]
        )
        outcome = replace(outcome, source_sense_observation_id="")
        packet = build_learning_feedback_candidate_evidence_packet(
            candidate=candidate,
            task_closure=closure,
            outcome_evaluation=outcome,
            goal_delta_evaluation=TaskGoalDeltaEvaluationRecord.from_dict(
                payload["source_package87_goal_delta_evaluation"]
            ),
            expected_effect_reference=TaskExpectedEffectReferenceRecord.from_dict(
                payload["source_package87_expected_effect_reference"]
            ),
        )
        self.assertEqual(packet.evidence_packet_status, "evidence_packet_partial")
        self.assertIn("sense_observation", packet.missing_evidence_refs)

    def test_evidence_packet_blocks_missing_required_outcome_evaluation(self) -> None:
        payload = build_demo_blocked_learning_feedback_candidate("missing-required-evidence")
        packet = LearningFeedbackCandidateEvidencePacket.from_dict(
            payload["learning_feedback_evidence_packet"]
        )
        self.assertEqual(
            packet.evidence_packet_status,
            "blocked_missing_required_outcome_evaluation",
        )

    def test_evidence_packet_does_not_approve_learning_create_concept_or_write_memory(self) -> None:
        packet = self._packet_record()
        self.assertFalse(packet.learning_feedback_approved)
        self.assertFalse(packet.concept_candidate_created)
        self.assertFalse(packet.memory_write_performed)
        self.assertFalse(packet.automatic_learning_approval_created)

    def test_candidate_set_builds_from_multiple_closures(self) -> None:
        payload = build_demo_learning_feedback_candidate_set()
        candidate_set = LearningFeedbackCandidateSet.from_dict(
            payload["learning_feedback_candidate_set"]
        )
        validation = validate_learning_feedback_candidate_set(candidate_set)
        self.assertTrue(validation["valid"])
        self.assertEqual(candidate_set.candidate_count, 3)
        self.assertGreaterEqual(candidate_set.available_for_teacher_review_count, 2)

    def test_candidate_set_blocks_invalid_closure_set(self) -> None:
        payload = build_demo_blocked_learning_feedback_candidate("missing-required-evidence")
        candidate_set = LearningFeedbackCandidateSet.from_dict(
            payload["learning_feedback_candidate_set"]
        )
        self.assertEqual(candidate_set.set_status, "blocked_invalid_task_closure_set")

    def test_candidate_set_does_not_approve_learning_or_write_memory(self) -> None:
        candidate_set = LearningFeedbackCandidateSet.from_dict(
            build_demo_learning_feedback_candidate_set()["learning_feedback_candidate_set"]
        )
        self.assertFalse(candidate_set.learning_feedback_approved)
        self.assertFalse(candidate_set.concept_candidate_created)
        self.assertFalse(candidate_set.memory_write_performed)

    def test_safety_audit_passes_candidate_only_path(self) -> None:
        audit = self._audit_record()
        validation = validate_learning_feedback_candidate_safety_audit(audit)
        self.assertTrue(validation["valid"])
        self.assertEqual(audit.audit_status, "passed_learning_feedback_candidate_only")

    def test_safety_audit_passes_partial_evidence_path_when_allowed(self) -> None:
        payload = build_demo_unknown_outcome_learning_feedback_candidate()
        candidate = self._candidate_from_payload(payload)
        closure = self._closure_from_payload(payload)
        closure_audit = TaskClosureSafetyAudit.from_dict(
            payload["source_task_closure_safety_audit"]
        )
        outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
            payload["source_package87_outcome_evaluation"]
        )
        outcome = replace(outcome, source_sense_observation_id="")
        packet = build_learning_feedback_candidate_evidence_packet(
            candidate=candidate,
            task_closure=closure,
            outcome_evaluation=outcome,
            goal_delta_evaluation=TaskGoalDeltaEvaluationRecord.from_dict(
                payload["source_package87_goal_delta_evaluation"]
            ),
            expected_effect_reference=TaskExpectedEffectReferenceRecord.from_dict(
                payload["source_package87_expected_effect_reference"]
            ),
        )
        candidate_set = build_learning_feedback_candidate_set(
            candidates=(candidate,),
            evidence_packets=(packet,),
        )
        audit = build_learning_feedback_candidate_safety_audit(
            candidate_set=candidate_set,
            task_closures=(closure,),
            task_closure_safety_audits=(closure_audit,),
        )
        self.assertEqual(audit.audit_status, "passed_candidate_created_with_partial_evidence")

    def test_safety_audit_blocks_forbidden_authority_paths(self) -> None:
        expected = {
            "learning-feedback-approved": "blocked_learning_feedback_approval_detected",
            "concept-candidate-created": "blocked_concept_candidate_creation_detected",
            "memory-write-detected": "blocked_memory_write_detected",
            "action-authority-detected": "blocked_action_authority_detected",
            "behavior-change-detected": "blocked_behavior_change_detected",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                audit = self._audit_from_payload(
                    build_demo_blocked_learning_feedback_candidate(case)
                )
                self.assertEqual(audit.audit_status, status)

    def test_cli_commands_work(self) -> None:
        commands = (
            "build-demo-candidate",
            "show-demo-candidate",
            "show-demo-evidence-packet",
            "show-demo-candidate-set",
            "show-demo-safety-audit",
            "validate-demo-candidate",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_task_cli(command)
                self.assertIsInstance(payload, dict)

    def test_cli_demo_cases_work(self) -> None:
        cases = (
            "goal-reached",
            "progress",
            "expected-effect-failed",
            "no-progress",
            "observation-only",
            "unknown-outcome",
            "system-fault",
        )
        for case in cases:
            with self.subTest(case=case):
                payload = self._run_task_cli("build-demo-case", "--case", case)
                self.assertIn("learning_feedback_candidate", payload)

    def test_cli_blocked_cases_work(self) -> None:
        cases = (
            "invalid-task-closure",
            "invalid-closure-audit",
            "learning-feedback-approved",
            "concept-candidate-created",
            "memory-write-detected",
            "action-authority-detected",
            "behavior-change-detected",
            "missing-required-evidence",
        )
        for case in cases:
            with self.subTest(case=case):
                payload = self._run_task_cli("build-demo-blocked", "--case", case)
                self.assertIn("learning_feedback_candidate_safety_audit", payload)

    def test_guided_console_learning_feedback_candidate_demo_works(self) -> None:
        payload = self._run_guided_cli(
            "learning-build-feedback-candidate-from-task-closure-demo"
        )
        self.assertEqual(
            payload["guided_console_action"],
            "learning_build_feedback_candidate_from_task_closure_demo",
        )
        self.assertFalse(payload["learning_feedback_approved"])
        self.assertFalse(payload["memory_write_performed"])

    def test_guided_console_learning_feedback_candidate_views_work(self) -> None:
        commands = (
            "learning-show-feedback-candidate",
            "learning-show-feedback-candidate-evidence",
            "learning-show-feedback-candidate-set",
            "learning-show-feedback-candidate-safety-audit",
            "learning-validate-feedback-candidate",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_guided_cli(command)
                self.assertIsInstance(payload, dict)

    def test_no_repo_data_pollution(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _payload(self) -> dict[str, object]:
        return build_demo_progress_learning_feedback_candidate()

    def _candidate_record(self) -> LearningFeedbackCandidateRecord:
        return self._candidate_from_payload(self._payload())

    def _packet_record(self) -> LearningFeedbackCandidateEvidencePacket:
        return LearningFeedbackCandidateEvidencePacket.from_dict(
            self._payload()["learning_feedback_evidence_packet"]
        )

    def _audit_record(self) -> LearningFeedbackCandidateSafetyAudit:
        return self._audit_from_payload(self._payload())

    def _candidate_from_payload(
        self,
        payload: dict[str, object],
    ) -> LearningFeedbackCandidateRecord:
        return LearningFeedbackCandidateRecord.from_dict(payload["learning_feedback_candidate"])

    def _closure_record(self) -> TaskClosureFromOutcomeEvaluationRecord:
        return self._closure_from_payload(self._payload())

    def _closure_from_payload(
        self,
        payload: dict[str, object],
    ) -> TaskClosureFromOutcomeEvaluationRecord:
        return TaskClosureFromOutcomeEvaluationRecord.from_dict(payload["source_task_closure"])

    def _outcome_record(self) -> TaskExecutionOutcomeEvaluationRecord:
        return TaskExecutionOutcomeEvaluationRecord.from_dict(
            self._payload()["source_package87_outcome_evaluation"]
        )

    def _goal_delta_record(self) -> TaskGoalDeltaEvaluationRecord:
        return TaskGoalDeltaEvaluationRecord.from_dict(
            self._payload()["source_package87_goal_delta_evaluation"]
        )

    def _reference_record(self) -> TaskExpectedEffectReferenceRecord:
        return TaskExpectedEffectReferenceRecord.from_dict(
            self._payload()["source_package87_expected_effect_reference"]
        )

    def _audit_from_payload(
        self,
        payload: dict[str, object],
    ) -> LearningFeedbackCandidateSafetyAudit:
        return LearningFeedbackCandidateSafetyAudit.from_dict(
            payload["learning_feedback_candidate_safety_audit"]
        )

    def _run_task_cli(self, *args: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, "-m", TASK_CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def _run_guided_cli(self, *args: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, "-m", GUIDED_CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)


if __name__ == "__main__":
    unittest.main()
