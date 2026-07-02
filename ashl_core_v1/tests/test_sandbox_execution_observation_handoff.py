from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.sense.sandbox_execution_observation_handoff import (
    SenseSandboxExecutionObservationRecord,
    SenseSandboxObservationHandoffRecord,
    SenseSandboxObservationSafetyAudit,
    SenseSandboxStateDeltaObservationRecord,
    build_demo_blocked_action_authority_observation,
    build_demo_blocked_external_execution_observation,
    build_demo_blocked_invalid_sandbox_execution_observation,
    build_demo_blocked_learning_feedback_created_observation,
    build_demo_blocked_memory_write_observation,
    build_demo_blocked_missing_pre_execution_snapshot_observation,
    build_demo_blocked_outcome_evaluation_created_observation,
    build_demo_blocked_sense_sandbox_observation,
    build_demo_blocked_task_closure_created_observation,
    build_demo_sense_sandbox_observation_handoff,
    build_sense_sandbox_state_delta_observation_record,
    validate_sense_sandbox_execution_observation_record,
    validate_sense_sandbox_observation_handoff_record,
    validate_sense_sandbox_observation_safety_audit,
    validate_sense_sandbox_state_delta_observation_record,
)
from ashl_core_v1.task.teacher_gated_direct_command_sandbox_execution import (
    SandboxExecutionRecord,
)


TASK_CLI = "ashl_core_v1.sense.sandbox_execution_observation_handoff_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class SandboxExecutionObservationHandoffTests(unittest.TestCase):
    def test_sense_observation_builds_from_valid_package85_execution(self) -> None:
        observation = self._observation()
        validation = validate_sense_sandbox_execution_observation_record(observation)
        self.assertTrue(validation["valid"])
        self.assertEqual(observation.sense_observation_status, "observation_record_created")
        self.assertEqual(observation.direct_command, "observe")

    def test_sense_observation_requires_bounded_sandbox_execution_completed(self) -> None:
        payload = build_demo_blocked_invalid_sandbox_execution_observation()
        observation = SenseSandboxExecutionObservationRecord.from_dict(
            payload["sense_sandbox_execution_observation"]
        )
        self.assertEqual(
            observation.sense_observation_status,
            "blocked_invalid_sandbox_execution",
        )

    def test_sense_observation_blocks_external_execution_record(self) -> None:
        payload = build_demo_blocked_external_execution_observation()
        observation = SenseSandboxExecutionObservationRecord.from_dict(
            payload["sense_sandbox_execution_observation"]
        )
        self.assertEqual(
            observation.sense_observation_status,
            "blocked_external_execution_record",
        )

    def test_sense_observation_requires_pre_execution_snapshot(self) -> None:
        payload = build_demo_blocked_missing_pre_execution_snapshot_observation()
        observation = SenseSandboxExecutionObservationRecord.from_dict(
            payload["sense_sandbox_execution_observation"]
        )
        self.assertEqual(
            observation.sense_observation_status,
            "blocked_missing_pre_execution_snapshot",
        )

    def test_sense_observation_preserves_execution_ids_and_command(self) -> None:
        observation = self._observation()
        execution = self._source_execution()
        self.assertEqual(
            observation.source_sandbox_execution_id,
            execution.sandbox_execution_id,
        )
        self.assertEqual(
            observation.source_direct_command_application_id,
            execution.source_direct_command_application_id,
        )
        self.assertEqual(observation.direct_command, "observe")

    def test_sense_observation_records_actor_and_box_state(self) -> None:
        observation = self._observation()
        self.assertEqual(observation.observed_actor_position_before, (0, 0))
        self.assertEqual(observation.observed_actor_position_after, (0, 0))
        self.assertFalse(observation.observed_actor_position_changed)
        self.assertEqual(observation.observed_box_positions_before, ())
        self.assertEqual(observation.observed_box_positions_after, ())
        self.assertFalse(observation.observed_box_position_changed)

    def test_sense_observation_creates_visible_delta_labels(self) -> None:
        labels = self._observation().visible_state_delta_labels
        self.assertIn("actor_position_unchanged", labels)
        self.assertIn("box_position_unchanged", labels)
        self.assertIn("no_contact_detected", labels)
        self.assertIn("visible_no_change", labels)

    def test_sense_observation_does_not_create_downstream_authority(self) -> None:
        observation = self._observation()
        self.assertFalse(observation.outcome_evaluation_created)
        self.assertFalse(observation.task_closure_created)
        self.assertFalse(observation.learning_feedback_created)
        self.assertFalse(observation.memory_write_performed)
        self.assertFalse(observation.automatic_learning_approval_created)
        self.assertFalse(observation.candidate_ordering_changed)
        self.assertFalse(observation.selected_action_changed)
        self.assertFalse(observation.final_action_changed)
        self.assertFalse(observation.direct_command_changed)
        self.assertFalse(observation.execution_created_by_sense)

    def test_state_delta_observation_builds_from_sense_observation(self) -> None:
        delta = self._state_delta()
        validation = validate_sense_sandbox_state_delta_observation_record(delta)
        self.assertTrue(validation["valid"])
        self.assertEqual(delta.source_sense_observation_id, self._observation().sense_observation_id)
        self.assertEqual(delta.source_sandbox_execution_id, self._source_execution().sandbox_execution_id)

    def test_state_delta_observation_preserves_raw_states(self) -> None:
        delta = self._state_delta()
        execution = self._source_execution()
        self.assertEqual(delta.raw_state_before, execution.sandbox_state_before_execution)
        self.assertEqual(delta.raw_state_after, execution.sandbox_state_after_execution)
        self.assertIn("observations", delta.observed_delta_keys)
        self.assertIn("last_command", delta.observed_delta_keys)

    def test_state_delta_observation_describes_without_success_or_failure_labels(self) -> None:
        delta = self._state_delta()
        combined = " ".join(
            (
                delta.observed_delta_summary,
                *delta.observed_delta_keys,
                *delta.visibility_delta["labels"],
            )
        )
        for forbidden in ("success", "failure", "goal_reached", "useful_progress", "learnable"):
            self.assertNotIn(forbidden, combined)

    def test_state_delta_observation_blocks_invalid_observation(self) -> None:
        payload = build_demo_blocked_invalid_sandbox_execution_observation()
        delta = SenseSandboxStateDeltaObservationRecord.from_dict(
            payload["sense_sandbox_state_delta_observation"]
        )
        self.assertEqual(delta.state_delta_status, "blocked_invalid_observation")

    def test_handoff_builds_from_observation_and_state_delta(self) -> None:
        handoff = self._handoff()
        validation = validate_sense_sandbox_observation_handoff_record(handoff)
        self.assertTrue(validation["valid"])
        self.assertEqual(
            handoff.handoff_status,
            "handoff_ready_for_task_outcome_evaluation",
        )

    def test_handoff_targets_task_engine(self) -> None:
        handoff = self._handoff()
        self.assertEqual(handoff.source_engine, "sense_interface")
        self.assertEqual(handoff.target_engine, "task_engine")

    def test_handoff_availability_is_for_task_outcome_only(self) -> None:
        handoff = self._handoff()
        self.assertTrue(handoff.observation_available_for_task_outcome_evaluation)
        self.assertFalse(handoff.observation_available_for_learning_feedback)
        self.assertFalse(handoff.outcome_evaluation_created)
        self.assertFalse(handoff.task_closure_created)
        self.assertFalse(handoff.learning_feedback_created)
        self.assertFalse(handoff.memory_write_performed)
        self.assertFalse(handoff.automatic_learning_approval_created)

    def test_safety_audit_passes_valid_observation_handoff(self) -> None:
        audit = self._audit()
        validation = validate_sense_sandbox_observation_safety_audit(audit)
        self.assertTrue(validation["valid"])
        self.assertEqual(audit.audit_status, "passed_sense_observation_handoff")

    def test_safety_audit_confirms_sense_only_boundaries(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.sense_only_observation_confirmed)
        self.assertTrue(audit.no_outcome_evaluation)
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
        self.assertTrue(audit.no_execution_created_by_sense)

    def test_safety_audit_blocks_downstream_authority(self) -> None:
        expected = {
            build_demo_blocked_outcome_evaluation_created_observation: (
                "blocked_outcome_evaluation_detected"
            ),
            build_demo_blocked_task_closure_created_observation: (
                "blocked_task_closure_detected"
            ),
            build_demo_blocked_learning_feedback_created_observation: (
                "blocked_learning_feedback_detected"
            ),
            build_demo_blocked_memory_write_observation: "blocked_memory_write_detected",
            build_demo_blocked_action_authority_observation: (
                "blocked_action_authority_detected"
            ),
        }
        for builder, status in expected.items():
            with self.subTest(builder=builder.__name__):
                payload = builder()
                audit = SenseSandboxObservationSafetyAudit.from_dict(
                    payload["sense_sandbox_observation_safety_audit"]
                )
                self.assertEqual(audit.audit_status, status)

    def test_safety_audit_blocks_invalid_execution_and_missing_snapshot(self) -> None:
        expected = {
            build_demo_blocked_invalid_sandbox_execution_observation: (
                "blocked_invalid_sandbox_execution"
            ),
            build_demo_blocked_missing_pre_execution_snapshot_observation: (
                "blocked_missing_pre_execution_snapshot"
            ),
            build_demo_blocked_external_execution_observation: (
                "blocked_invalid_sandbox_execution"
            ),
        }
        for builder, status in expected.items():
            with self.subTest(builder=builder.__name__):
                payload = builder()
                audit = SenseSandboxObservationSafetyAudit.from_dict(
                    payload["sense_sandbox_observation_safety_audit"]
                )
                self.assertEqual(audit.audit_status, status)

    def test_core_state_delta_builder_blocks_invalid_observation(self) -> None:
        payload = build_demo_blocked_invalid_sandbox_execution_observation()
        observation = SenseSandboxExecutionObservationRecord.from_dict(
            payload["sense_sandbox_execution_observation"]
        )
        execution = SandboxExecutionRecord.from_dict(payload["source_package85_execution"])
        delta = build_sense_sandbox_state_delta_observation_record(
            sense_observation=observation,
            sandbox_execution=execution,
            pre_execution_snapshot=None,
        )
        self.assertEqual(delta.state_delta_status, "blocked_invalid_observation")

    def test_cli_commands_work(self) -> None:
        commands = (
            "observe-demo-execution",
            "show-demo-observation",
            "show-demo-state-delta",
            "show-demo-handoff",
            "show-demo-safety-audit",
            "validate-demo-observation",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_task_cli(command)
                self.assertIsInstance(payload, dict)

    def test_cli_blocked_cases_work(self) -> None:
        cases = (
            "invalid-sandbox-execution",
            "missing-pre-execution-snapshot",
            "external-execution-record",
            "outcome-evaluation-created",
            "task-closure-created",
            "learning-feedback-created",
            "memory-write-detected",
            "action-authority-detected",
        )
        for case in cases:
            with self.subTest(case=case):
                payload = self._run_task_cli("observe-demo-blocked", "--case", case)
                self.assertIn("sense_sandbox_observation_safety_audit", payload)

    def test_guided_console_sense_observation_demo_works(self) -> None:
        payload = self._run_guided_cli("sense-observe-sandbox-execution-demo")
        self.assertEqual(
            payload["sense_sandbox_observation_handoff"]["handoff_status"],
            "handoff_ready_for_task_outcome_evaluation",
        )
        self.assertFalse(payload["outcome_evaluation_created"])
        self.assertFalse(payload["task_closure_created"])
        self.assertFalse(payload["learning_feedback_created"])
        self.assertFalse(payload["memory_write_performed"])

    def test_guided_console_sense_observation_views_work(self) -> None:
        commands = (
            "sense-show-sandbox-observation",
            "sense-show-sandbox-state-delta",
            "sense-show-observation-handoff",
            "sense-show-observation-safety-audit",
            "sense-validate-sandbox-observation",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_guided_cli(command)
                self.assertFalse(payload.get("outcome_evaluation_created", False))
                self.assertFalse(payload.get("task_closure_created", False))
                self.assertFalse(payload.get("learning_feedback_created", False))
                self.assertFalse(payload.get("memory_write_performed", False))

    def test_no_repo_data_dir_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _payload(self) -> dict[str, object]:
        return build_demo_sense_sandbox_observation_handoff()

    def _observation(self) -> SenseSandboxExecutionObservationRecord:
        return SenseSandboxExecutionObservationRecord.from_dict(
            self._payload()["sense_sandbox_execution_observation"]
        )

    def _state_delta(self) -> SenseSandboxStateDeltaObservationRecord:
        return SenseSandboxStateDeltaObservationRecord.from_dict(
            self._payload()["sense_sandbox_state_delta_observation"]
        )

    def _handoff(self) -> SenseSandboxObservationHandoffRecord:
        return SenseSandboxObservationHandoffRecord.from_dict(
            self._payload()["sense_sandbox_observation_handoff"]
        )

    def _audit(self) -> SenseSandboxObservationSafetyAudit:
        return SenseSandboxObservationSafetyAudit.from_dict(
            self._payload()["sense_sandbox_observation_safety_audit"]
        )

    def _source_execution(self) -> SandboxExecutionRecord:
        return SandboxExecutionRecord.from_dict(self._payload()["source_package85_execution"])

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
