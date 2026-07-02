from __future__ import annotations

import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
    TaskExpectedEffectReferenceRecord,
    TaskExecutionOutcomeEvaluationRecord,
    TaskGoalDeltaEvaluationRecord,
    TaskOutcomeEvaluationSafetyAudit,
)
from ashl_core_v1.task.task_closure_from_outcome_evaluation import (
    TaskClosureFromOutcomeEvaluationRecord,
    TaskClosureRollbackRecord,
    TaskClosureSafetyAudit,
    TaskClosureSummaryRecord,
    apply_task_closure_rollback,
    build_demo_blocked_invalid_goal_delta_task_closure,
    build_demo_blocked_invalid_outcome_audit_task_closure,
    build_demo_blocked_invalid_outcome_evaluation_task_closure,
    build_demo_blocked_task_closure,
    build_demo_observe_task_closure,
    build_demo_push_right_matched_task_closure,
    build_demo_push_right_not_matched_task_closure,
    build_demo_step_forward_matched_task_closure,
    build_demo_step_forward_not_matched_task_closure,
    build_demo_unknown_outcome_task_closure,
    build_task_closure_from_outcome_evaluation_record,
    build_task_closure_rollback_record,
    build_task_closure_safety_audit,
    build_task_closure_summary_record,
    validate_task_closure_from_outcome_evaluation_record,
    validate_task_closure_rollback_record,
    validate_task_closure_safety_audit,
    validate_task_closure_summary_record,
)


TASK_CLI = "ashl_core_v1.task.task_closure_from_outcome_evaluation_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class TaskClosureFromOutcomeEvaluationTests(unittest.TestCase):
    def test_task_closure_builds_from_valid_outcome_evaluation(self) -> None:
        closure = self._closure_record()
        validation = validate_task_closure_from_outcome_evaluation_record(closure)
        self.assertTrue(validation["valid"])
        self.assertTrue(closure.task_closed)
        self.assertEqual(closure.closure_status, "task_closed_observation_only")

    def test_task_closure_requires_outcome_evaluation_safety_audit_pass(self) -> None:
        payload = build_demo_blocked_invalid_outcome_audit_task_closure()
        closure = TaskClosureFromOutcomeEvaluationRecord.from_dict(
            payload["task_closure_from_outcome_evaluation"]
        )
        self.assertEqual(closure.closure_status, "blocked_invalid_outcome_evaluation")

    def test_task_closure_preserves_source_ids(self) -> None:
        closure = self._closure_record()
        outcome = self._source_outcome_record()
        goal_delta = self._source_goal_delta_record()
        self.assertEqual(closure.source_outcome_evaluation_id, outcome.outcome_evaluation_id)
        self.assertEqual(
            closure.source_goal_delta_evaluation_id,
            goal_delta.goal_delta_evaluation_id,
        )
        self.assertEqual(closure.source_sense_handoff_id, outcome.source_sense_handoff_id)
        self.assertEqual(
            closure.source_sandbox_execution_id,
            outcome.source_sandbox_execution_id,
        )

    def test_task_closure_preserves_direct_command_and_effect_classes(self) -> None:
        closure = self._closure_record()
        self.assertEqual(closure.direct_command, "observe")
        self.assertEqual(closure.expected_effect, "observe_environment")
        self.assertEqual(closure.outcome_class, "observation_only")
        self.assertEqual(closure.goal_delta_class, "not_applicable")

    def test_observe_outcome_creates_observation_only_closure(self) -> None:
        closure = self._closure_record()
        self.assertEqual(closure.closure_class, "observation_only_closure")
        self.assertEqual(closure.closure_status, "task_closed_observation_only")

    def test_step_forward_matched_creates_progress_closure(self) -> None:
        payload = build_demo_step_forward_matched_task_closure()
        closure = TaskClosureFromOutcomeEvaluationRecord.from_dict(
            payload["task_closure_from_outcome_evaluation"]
        )
        self.assertEqual(closure.closure_status, "task_closed_with_progress")

    def test_step_forward_not_matched_creates_expected_effect_failed_closure(self) -> None:
        payload = build_demo_step_forward_not_matched_task_closure()
        closure = TaskClosureFromOutcomeEvaluationRecord.from_dict(
            payload["task_closure_from_outcome_evaluation"]
        )
        self.assertEqual(closure.closure_status, "task_closed_expected_effect_failed")

    def test_push_right_matched_creates_progress_closure(self) -> None:
        payload = build_demo_push_right_matched_task_closure()
        closure = TaskClosureFromOutcomeEvaluationRecord.from_dict(
            payload["task_closure_from_outcome_evaluation"]
        )
        self.assertEqual(closure.closure_status, "task_closed_with_progress")

    def test_push_right_not_matched_creates_expected_effect_failed_closure(self) -> None:
        payload = build_demo_push_right_not_matched_task_closure()
        closure = TaskClosureFromOutcomeEvaluationRecord.from_dict(
            payload["task_closure_from_outcome_evaluation"]
        )
        self.assertEqual(closure.closure_status, "task_closed_expected_effect_failed")

    def test_goal_reached_creates_goal_reached_closure(self) -> None:
        reference, outcome, goal_delta, audit = self._valid_source_records()
        goal_reached = replace(
            goal_delta,
            goal_delta_status="goal_delta_evaluated",
            goal_delta_class="goal_reached",
            goal_reached=True,
            progress_toward_goal_detected=True,
            regression_from_goal_detected=False,
        )
        closure = build_task_closure_from_outcome_evaluation_record(
            expected_effect_reference=reference,
            outcome_evaluation=outcome,
            goal_delta_evaluation=goal_reached,
            outcome_evaluation_safety_audit=audit,
        )
        self.assertEqual(closure.closure_status, "task_closed_goal_reached")

    def test_unknown_outcome_creates_unknown_closure(self) -> None:
        payload = build_demo_unknown_outcome_task_closure()
        closure = TaskClosureFromOutcomeEvaluationRecord.from_dict(
            payload["task_closure_from_outcome_evaluation"]
        )
        self.assertEqual(closure.closure_status, "task_closed_unknown")

    def test_system_fault_creates_system_fault_closure(self) -> None:
        reference, outcome, goal_delta, audit = self._valid_source_records()
        system_fault_outcome = replace(
            outcome,
            outcome_class="system_fault",
            outcome_summary="System fault outcome fixture.",
            evaluation_status="outcome_evaluated",
        )
        system_fault_goal = replace(
            goal_delta,
            goal_delta_status="goal_delta_evaluated",
            goal_delta_class="system_fault",
        )
        closure = build_task_closure_from_outcome_evaluation_record(
            expected_effect_reference=reference,
            outcome_evaluation=system_fault_outcome,
            goal_delta_evaluation=system_fault_goal,
            outcome_evaluation_safety_audit=audit,
        )
        self.assertEqual(closure.closure_status, "task_closed_system_fault")

    def test_learning_feedback_availability_matches_closure_type(self) -> None:
        progress = TaskClosureFromOutcomeEvaluationRecord.from_dict(
            build_demo_step_forward_matched_task_closure()[
                "task_closure_from_outcome_evaluation"
            ]
        )
        failed = TaskClosureFromOutcomeEvaluationRecord.from_dict(
            build_demo_step_forward_not_matched_task_closure()[
                "task_closure_from_outcome_evaluation"
            ]
        )
        unknown = TaskClosureFromOutcomeEvaluationRecord.from_dict(
            build_demo_unknown_outcome_task_closure()["task_closure_from_outcome_evaluation"]
        )
        self.assertTrue(progress.available_for_learning_feedback_candidate_later)
        self.assertTrue(failed.available_for_learning_feedback_candidate_later)
        self.assertFalse(unknown.available_for_learning_feedback_candidate_later)

    def test_closure_does_not_create_learning_memory_action_or_behavior_authority(self) -> None:
        closure = self._closure_record()
        self.assertFalse(closure.learning_feedback_created)
        self.assertFalse(closure.memory_write_performed)
        self.assertFalse(closure.automatic_learning_approval_created)
        self.assertFalse(closure.candidate_ordering_changed)
        self.assertFalse(closure.selected_action_changed)
        self.assertFalse(closure.final_action_changed)
        self.assertFalse(closure.direct_command_changed)
        self.assertFalse(closure.execution_created_by_closure)
        self.assertFalse(closure.task_behavior_changed)

    def test_summary_record_builds_from_closure(self) -> None:
        summary = self._summary_record()
        validation = validate_task_closure_summary_record(summary)
        self.assertTrue(validation["valid"])
        self.assertEqual(summary.source_task_closure_id, self._closure_record().task_closure_id)

    def test_summary_record_uses_deterministic_text_only(self) -> None:
        summary = self._summary_record()
        self.assertIn("direct_command observe expected observe_environment", summary.evidence_summary)
        self.assertIn("Closure: observation_only_closure", summary.evidence_summary)

    def test_summary_record_does_not_create_learning_or_memory(self) -> None:
        summary = self._summary_record()
        self.assertFalse(summary.learning_feedback_created)
        self.assertFalse(summary.memory_write_performed)
        self.assertFalse(summary.automatic_learning_approval_created)

    def test_rollback_record_created_for_successful_closure(self) -> None:
        rollback = self._rollback_record()
        validation = validate_task_closure_rollback_record(rollback)
        self.assertTrue(validation["valid"])
        self.assertEqual(rollback.rollback_status, "rollback_record_created")
        self.assertTrue(rollback.rollback_available)

    def test_rollback_reopens_closure_record_only(self) -> None:
        rollback = apply_task_closure_rollback(task_closure=self._closure_record())
        self.assertEqual(
            rollback.rollback_status,
            "rollback_applied_to_reopen_task_closure_record",
        )
        self.assertTrue(rollback.task_closed_before_rollback)
        self.assertFalse(rollback.task_closed_after_rollback)
        self.assertIsNone(rollback.closure_status_after_rollback)

    def test_rollback_does_not_replay_execution_or_change_authority(self) -> None:
        rollback = apply_task_closure_rollback(task_closure=self._closure_record())
        self.assertFalse(rollback.selected_action_changed)
        self.assertFalse(rollback.final_action_changed)
        self.assertFalse(rollback.direct_command_changed)
        self.assertFalse(rollback.execution_created_by_rollback)
        self.assertFalse(rollback.memory_write_performed)

    def test_safety_audit_passes_valid_task_closure(self) -> None:
        audit = self._audit_record()
        validation = validate_task_closure_safety_audit(audit)
        self.assertTrue(validation["valid"])
        self.assertEqual(audit.audit_status, "passed_task_closure_only")

    def test_safety_audit_blocks_invalid_outcome_evaluation(self) -> None:
        audit = self._audit_from_payload(
            build_demo_blocked_invalid_outcome_evaluation_task_closure()
        )
        self.assertEqual(audit.audit_status, "blocked_invalid_outcome_evaluation")

    def test_safety_audit_blocks_invalid_goal_delta(self) -> None:
        audit = self._audit_from_payload(build_demo_blocked_invalid_goal_delta_task_closure())
        self.assertEqual(audit.audit_status, "blocked_invalid_goal_delta_evaluation")

    def test_safety_audit_blocks_invalid_outcome_audit(self) -> None:
        audit = self._audit_from_payload(build_demo_blocked_invalid_outcome_audit_task_closure())
        self.assertEqual(audit.audit_status, "blocked_invalid_outcome_evaluation")

    def test_safety_audit_blocks_missing_rollback(self) -> None:
        audit = self._audit_from_payload(build_demo_blocked_task_closure("missing-rollback"))
        self.assertEqual(audit.audit_status, "blocked_missing_rollback")

    def test_safety_audit_blocks_learning_feedback_memory_action_and_behavior(self) -> None:
        expected = {
            "learning-feedback-created": "blocked_learning_feedback_detected",
            "memory-write-detected": "blocked_memory_write_detected",
            "action-authority-detected": "blocked_action_authority_detected",
            "behavior-change-detected": "blocked_behavior_change_detected",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                audit = self._audit_from_payload(build_demo_blocked_task_closure(case))
                self.assertEqual(audit.audit_status, status)

    def test_core_builder_can_create_rollback_and_audit_directly(self) -> None:
        closure = self._closure_record()
        summary = build_task_closure_summary_record(task_closure=closure)
        rollback = build_task_closure_rollback_record(task_closure=closure)
        audit = build_task_closure_safety_audit(
            outcome_evaluation=self._source_outcome_record(),
            goal_delta_evaluation=self._source_goal_delta_record(),
            task_closure=closure,
            task_closure_summary=summary,
            task_closure_rollback=rollback,
            outcome_evaluation_safety_audit=self._source_outcome_audit_record(),
        )
        self.assertEqual(audit.audit_status, "passed_task_closure_only")

    def test_cli_commands_work(self) -> None:
        commands = (
            "close-demo-task",
            "show-demo-closure",
            "show-demo-summary",
            "show-demo-rollback",
            "show-demo-safety-audit",
            "validate-demo-closure",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_task_cli(command)
                self.assertIsInstance(payload, dict)

    def test_cli_demo_cases_work(self) -> None:
        cases = (
            "observe",
            "step-forward-matched",
            "step-forward-not-matched",
            "push-right-matched",
            "push-right-not-matched",
            "unknown-outcome",
        )
        for case in cases:
            with self.subTest(case=case):
                payload = self._run_task_cli("close-demo-case", "--case", case)
                self.assertIn("task_closure_from_outcome_evaluation", payload)

    def test_cli_blocked_cases_work(self) -> None:
        cases = (
            "invalid-outcome-evaluation",
            "invalid-goal-delta",
            "invalid-outcome-audit",
            "learning-feedback-created",
            "memory-write-detected",
            "action-authority-detected",
            "behavior-change-detected",
            "missing-rollback",
        )
        for case in cases:
            with self.subTest(case=case):
                payload = self._run_task_cli("close-demo-blocked", "--case", case)
                self.assertIn("task_closure_safety_audit", payload)

    def test_guided_console_task_closure_demo_works(self) -> None:
        payload = self._run_guided_cli("task-close-from-outcome-demo")
        self.assertEqual(payload["guided_console_action"], "task_close_from_outcome_demo")
        self.assertFalse(payload["learning_feedback_created"])
        self.assertFalse(payload["memory_write_performed"])

    def test_guided_console_task_closure_views_work(self) -> None:
        commands = (
            "task-show-outcome-task-closure",
            "task-show-outcome-task-closure-summary",
            "task-show-outcome-task-closure-rollback",
            "task-show-outcome-task-closure-safety-audit",
            "task-validate-outcome-task-closure",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_guided_cli(command)
                self.assertIsInstance(payload, dict)

    def test_no_repo_data_pollution(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _payload(self) -> dict[str, object]:
        return build_demo_observe_task_closure()

    def _closure_record(self) -> TaskClosureFromOutcomeEvaluationRecord:
        return TaskClosureFromOutcomeEvaluationRecord.from_dict(
            self._payload()["task_closure_from_outcome_evaluation"]
        )

    def _summary_record(self) -> TaskClosureSummaryRecord:
        return TaskClosureSummaryRecord.from_dict(self._payload()["task_closure_summary"])

    def _rollback_record(self) -> TaskClosureRollbackRecord:
        return TaskClosureRollbackRecord.from_dict(self._payload()["task_closure_rollback"])

    def _audit_record(self) -> TaskClosureSafetyAudit:
        return TaskClosureSafetyAudit.from_dict(self._payload()["task_closure_safety_audit"])

    def _audit_from_payload(self, payload: dict[str, object]) -> TaskClosureSafetyAudit:
        return TaskClosureSafetyAudit.from_dict(payload["task_closure_safety_audit"])

    def _valid_source_records(
        self,
    ) -> tuple[
        TaskExpectedEffectReferenceRecord,
        TaskExecutionOutcomeEvaluationRecord,
        TaskGoalDeltaEvaluationRecord,
        TaskOutcomeEvaluationSafetyAudit,
    ]:
        payload = self._payload()
        return (
            TaskExpectedEffectReferenceRecord.from_dict(
                payload["source_package87_expected_effect_reference"]
            ),
            self._source_outcome_record(),
            self._source_goal_delta_record(),
            self._source_outcome_audit_record(),
        )

    def _source_outcome_record(self) -> TaskExecutionOutcomeEvaluationRecord:
        return TaskExecutionOutcomeEvaluationRecord.from_dict(
            self._payload()["source_package87_outcome_evaluation"]
        )

    def _source_goal_delta_record(self) -> TaskGoalDeltaEvaluationRecord:
        return TaskGoalDeltaEvaluationRecord.from_dict(
            self._payload()["source_package87_goal_delta_evaluation"]
        )

    def _source_outcome_audit_record(self) -> TaskOutcomeEvaluationSafetyAudit:
        return TaskOutcomeEvaluationSafetyAudit.from_dict(
            self._payload()["source_package87_outcome_evaluation_safety_audit"]
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
