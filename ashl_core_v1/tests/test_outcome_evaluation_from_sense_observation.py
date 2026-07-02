from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.task.outcome_evaluation_from_sense_observation import (
    TaskExpectedEffectReferenceRecord,
    TaskExecutionOutcomeEvaluationRecord,
    TaskGoalDeltaEvaluationRecord,
    TaskOutcomeEvaluationSafetyAudit,
    build_demo_blocked_action_authority_outcome_evaluation,
    build_demo_blocked_invalid_sense_handoff_outcome_evaluation,
    build_demo_blocked_learning_feedback_created_outcome_evaluation,
    build_demo_blocked_memory_write_outcome_evaluation,
    build_demo_blocked_outcome_evaluation,
    build_demo_blocked_task_closure_created_outcome_evaluation,
    build_demo_missing_observation_outcome_evaluation,
    build_demo_observe_outcome_evaluation,
    build_demo_outcome_evaluation_case,
    build_demo_push_right_matched_outcome_evaluation,
    build_demo_push_right_not_matched_outcome_evaluation,
    build_demo_step_forward_matched_outcome_evaluation,
    build_demo_step_forward_not_matched_outcome_evaluation,
    build_demo_unknown_expected_effect_outcome_evaluation,
    build_task_goal_delta_evaluation_record,
    expected_effect_for_direct_command,
    validate_task_expected_effect_reference_record,
    validate_task_execution_outcome_evaluation_record,
    validate_task_goal_delta_evaluation_record,
    validate_task_outcome_evaluation_safety_audit,
)


TASK_CLI = "ashl_core_v1.task.outcome_evaluation_from_sense_observation_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class OutcomeEvaluationFromSenseObservationTests(unittest.TestCase):
    def test_expected_effect_reference_builds_from_observe_command(self) -> None:
        reference = self._reference_record()
        validation = validate_task_expected_effect_reference_record(reference)
        self.assertTrue(validation["valid"])
        self.assertEqual(reference.direct_command, "observe")
        self.assertEqual(reference.expected_effect, "observe_environment")
        self.assertEqual(
            reference.expected_effect_source,
            "deterministic_direct_command_mapping",
        )

    def test_expected_effect_mapping_is_deterministic(self) -> None:
        expected = {
            "observe": "observe_environment",
            "step_forward": "actor_moves_forward",
            "turn_left": "actor_turns_left",
            "push_right": "box_moves_right",
            "unsupported": "unknown_expected_effect",
        }
        for command, effect in expected.items():
            with self.subTest(command=command):
                self.assertEqual(expected_effect_for_direct_command(command), effect)

    def test_expected_effect_reference_has_no_downstream_side_effects(self) -> None:
        reference = self._reference_record()
        self.assertFalse(reference.outcome_evaluation_created)
        self.assertFalse(reference.task_closure_created)
        self.assertFalse(reference.learning_feedback_created)
        self.assertFalse(reference.memory_write_performed)
        self.assertFalse(reference.automatic_learning_approval_created)

    def test_outcome_evaluation_builds_from_valid_sense_handoff(self) -> None:
        outcome = self._outcome_record()
        validation = validate_task_execution_outcome_evaluation_record(outcome)
        self.assertTrue(validation["valid"])
        self.assertEqual(outcome.evaluation_status, "outcome_evaluated")

    def test_outcome_evaluation_blocks_invalid_sense_handoff(self) -> None:
        payload = build_demo_blocked_invalid_sense_handoff_outcome_evaluation()
        outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
            payload["task_execution_outcome_evaluation"]
        )
        self.assertEqual(outcome.evaluation_status, "blocked_invalid_sense_handoff")

    def test_observe_outcome_creates_observation_only_match(self) -> None:
        outcome = self._outcome_record()
        self.assertEqual(outcome.expected_effect, "observe_environment")
        self.assertEqual(outcome.outcome_class, "observation_only")
        self.assertTrue(outcome.expected_effect_matched)
        self.assertFalse(outcome.expected_effect_failed)

    def test_step_forward_with_actor_position_changed_matches_expected_effect(self) -> None:
        payload = build_demo_step_forward_matched_outcome_evaluation()
        outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
            payload["task_execution_outcome_evaluation"]
        )
        self.assertEqual(outcome.expected_effect, "actor_moves_forward")
        self.assertEqual(outcome.outcome_class, "expected_effect_matched")
        self.assertTrue(outcome.expected_effect_matched)

    def test_step_forward_with_actor_position_unchanged_does_not_match(self) -> None:
        payload = build_demo_step_forward_not_matched_outcome_evaluation()
        outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
            payload["task_execution_outcome_evaluation"]
        )
        self.assertEqual(outcome.expected_effect, "actor_moves_forward")
        self.assertEqual(outcome.outcome_class, "expected_effect_not_matched")
        self.assertTrue(outcome.expected_effect_failed)

    def test_push_right_with_box_position_changed_matches_expected_effect(self) -> None:
        payload = build_demo_push_right_matched_outcome_evaluation()
        outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
            payload["task_execution_outcome_evaluation"]
        )
        self.assertEqual(outcome.expected_effect, "box_moves_right")
        self.assertEqual(outcome.outcome_class, "expected_effect_matched")
        self.assertTrue(outcome.expected_effect_matched)

    def test_push_right_with_box_position_unchanged_does_not_match(self) -> None:
        payload = build_demo_push_right_not_matched_outcome_evaluation()
        outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
            payload["task_execution_outcome_evaluation"]
        )
        self.assertEqual(outcome.expected_effect, "box_moves_right")
        self.assertEqual(outcome.outcome_class, "expected_effect_not_matched")
        self.assertTrue(outcome.expected_effect_failed)

    def test_unknown_expected_effect_creates_unknown_outcome(self) -> None:
        payload = build_demo_unknown_expected_effect_outcome_evaluation()
        reference = TaskExpectedEffectReferenceRecord.from_dict(
            payload["task_expected_effect_reference"]
        )
        outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
            payload["task_execution_outcome_evaluation"]
        )
        self.assertEqual(reference.expected_effect, "unknown_expected_effect")
        self.assertEqual(outcome.outcome_class, "unknown_expected_effect")
        self.assertIsNone(outcome.expected_effect_matched)

    def test_missing_observation_creates_unknown_observation(self) -> None:
        payload = build_demo_missing_observation_outcome_evaluation()
        outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
            payload["task_execution_outcome_evaluation"]
        )
        self.assertEqual(outcome.outcome_class, "unknown_observation")
        self.assertEqual(
            outcome.evaluation_status,
            "outcome_unknown_missing_observation",
        )

    def test_outcome_evaluation_has_no_downstream_or_action_side_effects(self) -> None:
        outcome = self._outcome_record()
        self.assertFalse(outcome.task_closure_created)
        self.assertFalse(outcome.learning_feedback_created)
        self.assertFalse(outcome.memory_write_performed)
        self.assertFalse(outcome.automatic_learning_approval_created)
        self.assertFalse(outcome.candidate_ordering_changed)
        self.assertFalse(outcome.selected_action_changed)
        self.assertFalse(outcome.final_action_changed)
        self.assertFalse(outcome.direct_command_changed)
        self.assertFalse(outcome.execution_created_by_evaluation)

    def test_goal_delta_evaluation_builds_from_outcome_evaluation(self) -> None:
        goal_delta = self._goal_delta_record()
        validation = validate_task_goal_delta_evaluation_record(goal_delta)
        self.assertTrue(validation["valid"])
        self.assertEqual(
            goal_delta.source_outcome_evaluation_id,
            self._outcome_record().outcome_evaluation_id,
        )

    def test_goal_delta_not_applicable_for_observe_without_goal(self) -> None:
        goal_delta = self._goal_delta_record()
        self.assertEqual(goal_delta.goal_delta_class, "not_applicable")
        self.assertEqual(goal_delta.goal_delta_status, "goal_delta_not_applicable")

    def test_goal_delta_unknown_when_task_goal_missing(self) -> None:
        payload = build_demo_step_forward_matched_outcome_evaluation()
        goal_delta = TaskGoalDeltaEvaluationRecord.from_dict(
            payload["task_goal_delta_evaluation"]
        )
        self.assertEqual(goal_delta.goal_delta_class, "unknown")
        self.assertEqual(goal_delta.goal_delta_status, "goal_delta_unknown_missing_goal")

    def test_goal_delta_closer_to_goal_only_with_explicit_progress(self) -> None:
        payload = build_demo_push_right_matched_outcome_evaluation()
        goal_delta = TaskGoalDeltaEvaluationRecord.from_dict(
            payload["task_goal_delta_evaluation"]
        )
        self.assertEqual(goal_delta.goal_delta_class, "closer_to_goal")
        self.assertTrue(goal_delta.progress_toward_goal_detected)

    def test_goal_delta_no_progress_for_not_matched_expected_effect(self) -> None:
        payload = build_demo_push_right_not_matched_outcome_evaluation()
        goal_delta = TaskGoalDeltaEvaluationRecord.from_dict(
            payload["task_goal_delta_evaluation"]
        )
        self.assertEqual(goal_delta.goal_delta_class, "no_progress")
        self.assertFalse(goal_delta.progress_toward_goal_detected)

    def test_goal_delta_does_not_create_downstream_side_effects(self) -> None:
        goal_delta = self._goal_delta_record()
        self.assertFalse(goal_delta.task_closure_created)
        self.assertFalse(goal_delta.learning_feedback_created)
        self.assertFalse(goal_delta.memory_write_performed)
        self.assertFalse(goal_delta.automatic_learning_approval_created)

    def test_safety_audit_passes_valid_outcome_evaluation(self) -> None:
        audit = self._audit_record()
        validation = validate_task_outcome_evaluation_safety_audit(audit)
        self.assertTrue(validation["valid"])
        self.assertEqual(audit.audit_status, "passed_outcome_evaluation_only")

    def test_safety_audit_passes_unknown_outcome_without_side_effects(self) -> None:
        payload = build_demo_unknown_expected_effect_outcome_evaluation()
        audit = TaskOutcomeEvaluationSafetyAudit.from_dict(
            payload["task_outcome_evaluation_safety_audit"]
        )
        validation = validate_task_outcome_evaluation_safety_audit(audit)
        self.assertTrue(validation["valid"])
        self.assertEqual(audit.audit_status, "passed_outcome_unknown")

    def test_safety_audit_confirms_evaluation_only_boundaries(self) -> None:
        audit = self._audit_record()
        self.assertTrue(audit.evaluation_only_confirmed)
        self.assertTrue(audit.no_task_closure)
        self.assertTrue(audit.no_learning_feedback)
        self.assertTrue(audit.no_memory_write)
        self.assertTrue(audit.no_core_memory_write)
        self.assertTrue(audit.no_long_term_memory_write)
        self.assertTrue(audit.no_archive_memory_write)
        self.assertTrue(audit.no_anchor_write)
        self.assertTrue(audit.no_automatic_learning_approval)
        self.assertTrue(audit.no_candidate_ordering_change)
        self.assertTrue(audit.no_selected_action_change)
        self.assertTrue(audit.no_final_action_change)
        self.assertTrue(audit.no_direct_command_change)
        self.assertTrue(audit.no_execution_created_by_evaluation)

    def test_safety_audit_blocks_forbidden_side_effects(self) -> None:
        expected = {
            build_demo_blocked_task_closure_created_outcome_evaluation: (
                "blocked_task_closure_detected"
            ),
            build_demo_blocked_learning_feedback_created_outcome_evaluation: (
                "blocked_learning_feedback_detected"
            ),
            build_demo_blocked_memory_write_outcome_evaluation: (
                "blocked_memory_write_detected"
            ),
            build_demo_blocked_action_authority_outcome_evaluation: (
                "blocked_action_authority_detected"
            ),
        }
        for builder, status in expected.items():
            with self.subTest(builder=builder.__name__):
                payload = builder()
                audit = TaskOutcomeEvaluationSafetyAudit.from_dict(
                    payload["task_outcome_evaluation_safety_audit"]
                )
                self.assertEqual(audit.audit_status, status)

    def test_safety_audit_blocks_invalid_sense_handoff(self) -> None:
        payload = build_demo_blocked_invalid_sense_handoff_outcome_evaluation()
        audit = TaskOutcomeEvaluationSafetyAudit.from_dict(
            payload["task_outcome_evaluation_safety_audit"]
        )
        self.assertEqual(audit.audit_status, "blocked_invalid_sense_handoff")

    def test_core_goal_delta_builder_can_record_goal_reached(self) -> None:
        payload = build_demo_push_right_matched_outcome_evaluation()
        outcome = TaskExecutionOutcomeEvaluationRecord.from_dict(
            payload["task_execution_outcome_evaluation"]
        )
        handoff = payload["source_sense_handoff"]
        goal_delta = build_task_goal_delta_evaluation_record(
            outcome_evaluation=outcome,
            sense_handoff=handoff,
            task_goal_id="goal:done",
            task_goal_summary="Goal reached.",
            deterministic_goal_reached=True,
        )
        self.assertEqual(goal_delta.goal_delta_class, "goal_reached")
        self.assertTrue(goal_delta.goal_reached)
        self.assertFalse(goal_delta.task_closure_created)

    def test_cli_commands_work(self) -> None:
        commands = (
            "evaluate-demo-outcome",
            "show-demo-expected-effect",
            "show-demo-outcome-evaluation",
            "show-demo-goal-delta",
            "show-demo-safety-audit",
            "validate-demo-outcome",
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
        )
        for case in cases:
            with self.subTest(case=case):
                payload = self._run_task_cli("evaluate-demo-case", "--case", case)
                self.assertIn("task_execution_outcome_evaluation", payload)

    def test_cli_blocked_cases_work(self) -> None:
        cases = (
            "invalid-sense-handoff",
            "task-closure-created",
            "learning-feedback-created",
            "memory-write-detected",
            "action-authority-detected",
        )
        for case in cases:
            with self.subTest(case=case):
                payload = self._run_task_cli("evaluate-demo-blocked", "--case", case)
                self.assertIn("task_outcome_evaluation_safety_audit", payload)

    def test_guided_console_outcome_evaluation_demo_works(self) -> None:
        payload = self._run_guided_cli("task-evaluate-sense-outcome-demo")
        self.assertEqual(
            payload["task_execution_outcome_evaluation"]["outcome_class"],
            "observation_only",
        )
        self.assertFalse(payload["task_closure_created"])
        self.assertFalse(payload["learning_feedback_created"])
        self.assertFalse(payload["memory_write_performed"])

    def test_guided_console_outcome_evaluation_views_work(self) -> None:
        commands = (
            "task-show-expected-effect-reference",
            "task-show-outcome-evaluation",
            "task-show-goal-delta-evaluation",
            "task-show-outcome-evaluation-safety-audit",
            "task-validate-sense-outcome-evaluation",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_guided_cli(command)
                self.assertFalse(payload.get("task_closure_created", False))
                self.assertFalse(payload.get("learning_feedback_created", False))
                self.assertFalse(payload.get("memory_write_performed", False))

    def test_blocked_dispatcher_works(self) -> None:
        payload = build_demo_blocked_outcome_evaluation("memory-write-detected")
        audit = TaskOutcomeEvaluationSafetyAudit.from_dict(
            payload["task_outcome_evaluation_safety_audit"]
        )
        self.assertEqual(audit.audit_status, "blocked_memory_write_detected")

    def test_no_repo_data_dir_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _demo_payload(self) -> dict[str, object]:
        return build_demo_observe_outcome_evaluation()

    def _reference_record(self) -> TaskExpectedEffectReferenceRecord:
        return TaskExpectedEffectReferenceRecord.from_dict(
            self._demo_payload()["task_expected_effect_reference"]
        )

    def _outcome_record(self) -> TaskExecutionOutcomeEvaluationRecord:
        return TaskExecutionOutcomeEvaluationRecord.from_dict(
            self._demo_payload()["task_execution_outcome_evaluation"]
        )

    def _goal_delta_record(self) -> TaskGoalDeltaEvaluationRecord:
        return TaskGoalDeltaEvaluationRecord.from_dict(
            self._demo_payload()["task_goal_delta_evaluation"]
        )

    def _audit_record(self) -> TaskOutcomeEvaluationSafetyAudit:
        return TaskOutcomeEvaluationSafetyAudit.from_dict(
            self._demo_payload()["task_outcome_evaluation_safety_audit"]
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
